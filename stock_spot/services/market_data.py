"""Cached Alpha Vantage market data and a transparent momentum backtest."""

from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Iterable

from django.db import transaction

from stock_spot.models import AlphaVantageFetch, DailyPrice, MomentumBacktestRun, Stock
from stock_spot.services.alpha_vantage import AlphaVantageError, AlphaVantageService


class DailyPriceValidationError(ValueError):
    """Raised when a provider row cannot safely enter the price cache."""


class DailyPriceCacheService:
    """Fetch and validate daily Alpha Vantage price rows before caching them."""

    SOURCE = 'alpha_vantage'
    MONTHLY_ADJUSTED_SOURCE = 'alpha_vantage_monthly_adjusted'

    def __init__(self, client=None):
        self.client = client or AlphaVantageService()

    @staticmethod
    def _decimal(value, field):
        try:
            result = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise DailyPriceValidationError(f'{field} is not a decimal') from exc
        if not result.is_finite():
            raise DailyPriceValidationError(f'{field} is not finite')
        return result

    @classmethod
    def parse_row(cls, trading_date: str, row: dict, adjusted: bool, monthly: bool = False) -> dict:
        try:
            parsed_date = date.fromisoformat(trading_date)
        except (TypeError, ValueError) as exc:
            raise DailyPriceValidationError('invalid trading date') from exc

        open_price = cls._decimal(row.get('1. open'), 'open')
        high = cls._decimal(row.get('2. high'), 'high')
        low = cls._decimal(row.get('3. low'), 'low')
        close = cls._decimal(row.get('4. close'), 'close')
        volume_key = '6. volume' if monthly and adjusted else '5. volume'
        volume_decimal = cls._decimal(row.get(volume_key), 'volume')
        if min(open_price, high, low, close) <= 0:
            raise DailyPriceValidationError('OHLC prices must be positive')
        if high < max(open_price, low, close) or low > min(open_price, high, close):
            raise DailyPriceValidationError('OHLC range is inconsistent')
        if volume_decimal < 0 or volume_decimal != volume_decimal.to_integral_value():
            raise DailyPriceValidationError('volume must be a non-negative integer')

        adjusted_close = None
        dividend_amount = Decimal('0')
        split_coefficient = Decimal('1')
        if adjusted:
            adjusted_close = cls._decimal(row.get('5. adjusted close'), 'adjusted close')
            dividend_key = '7. dividend amount' if monthly else '7. dividend amount'
            split_key = '8. split coefficient'
            dividend_amount = cls._decimal(row.get(dividend_key, 0), 'dividend amount')
            split_coefficient = cls._decimal(row.get(split_key, 1), 'split coefficient')
            if adjusted_close <= 0 or split_coefficient <= 0:
                raise DailyPriceValidationError('adjusted close and split coefficient must be positive')

        return {
            'trading_date': parsed_date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'adjusted_close': adjusted_close,
            'volume': int(volume_decimal),
            'dividend_amount': dividend_amount,
            'split_coefficient': split_coefficient,
        }

    @staticmethod
    def _hash(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
        return sha256(canonical.encode('utf-8')).hexdigest()

    def refresh(self, symbol: str, adjusted: bool = False, monthly: bool = False) -> dict:
        """Cache a complete API response, rejecting invalid individual rows."""
        stock, _ = Stock.objects.get_or_create(symbol=symbol.upper(), defaults={'isBought': False})
        if monthly and not adjusted:
            endpoint = 'TIME_SERIES_MONTHLY'
        elif monthly:
            endpoint = 'TIME_SERIES_MONTHLY_ADJUSTED'
        else:
            endpoint = 'TIME_SERIES_DAILY_ADJUSTED' if adjusted else 'TIME_SERIES_DAILY'
        source = self.MONTHLY_ADJUSTED_SOURCE if monthly and adjusted else self.SOURCE
        try:
            payload = self.client._make_api_request({
                'function': endpoint,
                'symbol': stock.symbol,
                **({} if monthly else {'outputsize': 'full'}),
            })
            series_key = (
                'Monthly Adjusted Time Series' if monthly and adjusted else
                'Monthly Time Series' if monthly else
                'Time Series (Daily)'
            )
            series = payload.get(series_key)
            if not isinstance(series, dict) or not series:
                raise AlphaVantageError(f'{endpoint} returned no {"monthly" if monthly else "daily"} time series')

            accepted, rejected = [], []
            for trading_date, row in series.items():
                try:
                    accepted.append(self.parse_row(trading_date, row, adjusted, monthly=monthly))
                except DailyPriceValidationError as exc:
                    rejected.append(f'{trading_date}: {exc}')

            if not accepted:
                raise AlphaVantageError('all returned daily rows failed validation')

            with transaction.atomic():
                for row in accepted:
                    defaults = {
                        'open': row['open'], 'high': row['high'], 'low': row['low'],
                        'close': row['close'], 'volume': row['volume'],
                    }
                    # The non-adjusted endpoint must not erase an adjusted series
                    # fetched earlier. Its data is still useful for raw execution prices.
                    if adjusted:
                        defaults.update({
                            'adjusted_close': row['adjusted_close'],
                            'dividend_amount': row['dividend_amount'],
                            'split_coefficient': row['split_coefficient'],
                        })
                    DailyPrice.objects.update_or_create(
                        stock=stock,
                        trading_date=row['trading_date'],
                        source=source,
                        defaults=defaults,
                    )
                newest = max(accepted, key=lambda item: item['trading_date'])
                stock.currentPrice = newest['close']
                stock.startingPrice = stock.startingPrice or newest['close']
                stock.save(update_fields=['currentPrice', 'startingPrice'])
                AlphaVantageFetch.objects.create(
                    stock=stock,
                    endpoint=endpoint,
                    succeeded=True,
                    row_count=len(accepted),
                    content_hash=self._hash(payload),
                    message='; '.join(rejected[:20]),
                )
            return {'symbol': stock.symbol, 'cached': len(accepted), 'rejected': rejected, 'endpoint': endpoint}
        except Exception as exc:
            AlphaVantageFetch.objects.create(
                stock=stock,
                endpoint=endpoint,
                succeeded=False,
                message=str(exc),
            )
            raise


def _shift_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 + months
    year, month_zero_based = divmod(month_index, 12)
    month = month_zero_based + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


class MonthlyMomentumBacktester:
    """Long-only 12-1 monthly momentum, using only rows already in the local cache.

    This is deliberately a price-return baseline. If adjusted close is unavailable,
    it uses raw closes and records that fact in each rebalance result.
    """

    def __init__(self, stocks: Iterable[Stock] | None = None):
        self.stocks = list(stocks) if stocks is not None else list(Stock.objects.all())

    @staticmethod
    def _price_value(price: DailyPrice, require_adjusted: bool):
        if price.adjusted_close is not None:
            return price.adjusted_close, 'adjusted_close'
        if require_adjusted:
            return None, None
        return price.close, 'close'

    @staticmethod
    def _last_on_or_before(prices: list[DailyPrice], target: date):
        matches = [price for price in prices if price.trading_date <= target]
        return matches[-1] if matches else None

    @staticmethod
    def _first_after(prices: list[DailyPrice], target: date):
        return next((price for price in prices if price.trading_date > target), None)

    def run(self, top_n: int = 20, lookback_months: int = 12, skip_months: int = 1,
            require_adjusted: bool = False, cost_bps: Decimal = Decimal('0'),
            value_weight: Decimal = Decimal('0')) -> MomentumBacktestRun:
        if top_n < 1 or lookback_months <= skip_months:
            raise ValueError('top_n must be positive and lookback_months must exceed skip_months')
        if cost_bps < 0 or value_weight < 0 or value_weight > 1:
            raise ValueError('cost_bps cannot be negative and value_weight must be between 0 and 1')
        value_service = None
        if value_weight:
            from stock_spot.services.value import FreeCashFlowYieldService, ValueSignalUnavailable
            value_service = FreeCashFlowYieldService()

        prices_by_stock = {}
        series_source = {}
        for stock in self.stocks:
            daily = list(stock.daily_prices.filter(source=DailyPriceCacheService.SOURCE).order_by('trading_date'))
            monthly = list(stock.daily_prices.filter(
                source=DailyPriceCacheService.MONTHLY_ADJUSTED_SOURCE,
            ).order_by('trading_date'))
            # Prefer a true daily cache once it has enough history. The monthly
            # adjusted endpoint is a no-premium-key POC fallback for this strategy.
            if daily and (daily[-1].trading_date - daily[0].trading_date).days >= 395:
                prices_by_stock[stock.id], series_source[stock.id] = daily, DailyPriceCacheService.SOURCE
            elif monthly:
                prices_by_stock[stock.id], series_source[stock.id] = monthly, DailyPriceCacheService.MONTHLY_ADJUSTED_SOURCE
            else:
                prices_by_stock[stock.id], series_source[stock.id] = daily, DailyPriceCacheService.SOURCE
        usable = {stock_id: rows for stock_id, rows in prices_by_stock.items() if rows}
        if not usable:
            raise ValueError('no cached daily prices; refresh prices before running a backtest')

        start = max(rows[0].trading_date for rows in usable.values())
        end = min(rows[-1].trading_date for rows in usable.values())
        # At month M, form momentum through M-1 from M-12, then enter on
        # the first available bar after M. Twelve months of prior observations
        # are therefore sufficient for the first monthly rebalance.
        first_signal_month = _shift_months(date(start.year, start.month, 1), lookback_months)
        cursor = date(first_signal_month.year, first_signal_month.month, 1)
        months = []
        while cursor <= end:
            signal_target = date(cursor.year, cursor.month, monthrange(cursor.year, cursor.month)[1])
            if signal_target > end:
                break
            months.append(signal_target)
            cursor = _shift_months(cursor, 1)

        portfolio_value = Decimal('1')
        high_watermark = portfolio_value
        max_drawdown = Decimal('0')
        previous_symbols: set[str] = set()
        results = []
        stock_by_id = {stock.id: stock for stock in self.stocks}

        for position, signal_target in enumerate(months[:-1]):
            holding_end = months[position + 1]
            candidates = []
            for stock_id, rows in usable.items():
                signal_price = self._last_on_or_before(rows, _shift_months(signal_target, -skip_months))
                lookback_price = self._last_on_or_before(rows, _shift_months(signal_target, -lookback_months))
                entry = self._first_after(rows, signal_target)
                exit_price = self._first_after(rows, holding_end)
                if not all([signal_price, lookback_price, entry, exit_price]):
                    continue
                signal_value, signal_basis = self._price_value(signal_price, require_adjusted)
                lookback_value, lookback_basis = self._price_value(lookback_price, require_adjusted)
                entry_value, entry_basis = self._price_value(entry, require_adjusted)
                exit_value, exit_basis = self._price_value(exit_price, require_adjusted)
                if not all([signal_value, lookback_value, entry_value, exit_value]):
                    continue
                momentum = signal_value / lookback_value - Decimal('1')
                holding_return = exit_value / entry_value - Decimal('1')
                candidate = {
                    'symbol': stock_by_id[stock_id].symbol,
                    'momentum': momentum,
                    'holding_return': holding_return,
                    'signal_date': signal_price.trading_date.isoformat(),
                    'entry_date': entry.trading_date.isoformat(),
                    'exit_date': exit_price.trading_date.isoformat(),
                    'price_basis': sorted({signal_basis, lookback_basis, entry_basis, exit_basis}),
                    'source': series_source[stock_id],
                }
                if value_service:
                    try:
                        value_signal = value_service.build(stock_by_id[stock_id], signal_target)
                    except ValueSignalUnavailable:
                        continue
                    candidate['free_cash_flow_yield'] = value_signal.free_cash_flow_yield
                    candidate['value_signal_id'] = value_signal.id
                candidates.append(candidate)
            if candidates:
                momentum_ranks = {
                    item['symbol']: rank for rank, item in enumerate(
                        sorted(candidates, key=lambda item: item['momentum'], reverse=True),
                    )
                }
                value_ranks = {
                    item['symbol']: rank for rank, item in enumerate(
                        sorted(candidates, key=lambda item: item.get('free_cash_flow_yield', Decimal('0')), reverse=True),
                    )
                }
                denominator = max(len(candidates) - 1, 1)
                for item in candidates:
                    item['momentum_percentile'] = Decimal('1') - Decimal(momentum_ranks[item['symbol']]) / denominator
                    item['value_percentile'] = Decimal('1') - Decimal(value_ranks[item['symbol']]) / denominator
                    item['combined_score'] = (
                        (Decimal('1') - value_weight) * item['momentum_percentile'] +
                        value_weight * item['value_percentile']
                    )
            selected = sorted(candidates, key=lambda item: item['combined_score'], reverse=True)[:top_n]
            if not selected:
                continue
            symbols = {item['symbol'] for item in selected}
            turnover = Decimal(len(symbols - previous_symbols)) / Decimal(max(len(symbols), 1))
            gross_return = sum((item['holding_return'] for item in selected), Decimal('0')) / Decimal(len(selected))
            net_return = gross_return - turnover * cost_bps / Decimal('10000')
            portfolio_value *= Decimal('1') + net_return
            high_watermark = max(high_watermark, portfolio_value)
            max_drawdown = min(max_drawdown, portfolio_value / high_watermark - Decimal('1'))
            results.append({
                'signal_month_end': signal_target.isoformat(),
                'holding_end': holding_end.isoformat(),
                'holdings': [
                    {
                        key: str(value) if isinstance(value, Decimal) else value
                        for key, value in item.items()
                    }
                    for item in selected
                ],
                'candidate_count': len(candidates),
                'turnover': str(turnover),
                'gross_return': str(gross_return),
                'net_return': str(net_return),
                'portfolio_value': str(portfolio_value),
            })
            previous_symbols = symbols

        if not results:
            raise ValueError('insufficient overlapping price history for a monthly momentum backtest')
        elapsed_years = Decimal(str((date.fromisoformat(results[-1]['holding_end']) - date.fromisoformat(results[0]['signal_month_end'])).days / 365.25))
        annualized = portfolio_value ** (Decimal('1') / elapsed_years) - Decimal('1') if elapsed_years > 0 else Decimal('0')
        summary = {
            'total_return': str(portfolio_value - Decimal('1')),
            'annualized_return': str(annualized),
            'max_drawdown': str(max_drawdown),
            'rebalance_count': len(results),
            'final_value_per_dollar': str(portfolio_value),
            'return_basis': 'adjusted close where present; raw close otherwise' if not require_adjusted else 'adjusted close only',
            'not_included': 'dividends and splits are not separately booked; use adjusted-close-only runs for total-return research.',
        }
        parameters = {
            'top_n': top_n,
            'lookback_months': lookback_months,
            'skip_months': skip_months,
            'require_adjusted': require_adjusted,
            'cost_bps': str(cost_bps),
            'value_weight': str(value_weight),
            'symbols': [stock.symbol for stock in self.stocks],
        }
        return MomentumBacktestRun.objects.create(parameters=parameters, summary=summary, rebalances=results)
