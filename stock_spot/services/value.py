"""Free-cash-flow-yield signal construction from auditable Alpha Vantage snapshots."""

from datetime import date
from decimal import Decimal, InvalidOperation

from stock_spot.models import (
    DailyPrice,
    FreeCashFlowYieldSignal,
    FundamentalSnapshot,
    ShareCountObservation,
    Stock,
)


class ValueSignalUnavailable(ValueError):
    pass


def _as_decimal(value, label):
    if value in (None, '', 'None'):
        raise ValueSignalUnavailable(f'missing {label}')
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueSignalUnavailable(f'invalid {label}') from exc


class FreeCashFlowYieldService:
    """Build a conservative, explicitly labelled FCF-yield value signal.

    Statement endpoints lack a report date. The signal maps each cash-flow and
    share-count period to the matching Alpha Vantage earnings ``reportedDate``.
    This is an availability proxy, not proof of point-in-time statement history.
    """

    AVAILABILITY_BASIS = 'matching_earnings_reported_date_proxy'

    @staticmethod
    def _latest_snapshot(stock, endpoint):
        snapshot = FundamentalSnapshot.objects.filter(stock=stock, endpoint=endpoint).first()
        if snapshot is None:
            raise ValueSignalUnavailable(f'no {endpoint} audit snapshot for {stock.symbol}')
        return snapshot

    @staticmethod
    def _earnings_dates(stock):
        snapshot = FreeCashFlowYieldService._latest_snapshot(stock, 'EARNINGS')
        return {
            row['fiscalDateEnding']: date.fromisoformat(row['reportedDate'])
            for row in snapshot.payload.get('quarterlyEarnings', [])
            if row.get('fiscalDateEnding') and row.get('reportedDate')
        }

    def normalize_share_counts(self, stock: Stock):
        snapshot = self._latest_snapshot(stock, 'SHARES_OUTSTANDING')
        earnings_dates = self._earnings_dates(stock)
        saved = 0
        for row in snapshot.payload.get('data', []):
            try:
                observation_date = date.fromisoformat(row['date'])
            except (KeyError, TypeError, ValueError):
                continue
            basic = row.get('shares_outstanding_basic')
            diluted = row.get('shares_outstanding_diluted')
            if basic in (None, '') and diluted in (None, ''):
                continue
            ShareCountObservation.objects.update_or_create(
                source_snapshot=snapshot,
                observation_date=observation_date,
                defaults={
                    'stock': stock,
                    'availability_date': earnings_dates.get(observation_date.isoformat()),
                    'basic_shares': int(basic) if basic not in (None, '') else None,
                    'diluted_shares': int(diluted) if diluted not in (None, '') else None,
                },
            )
            saved += 1
        return saved

    def build(self, stock: Stock, signal_date: date):
        """Create or update the trailing-FCF-yield signal available by ``signal_date``."""
        share_snapshot = self._latest_snapshot(stock, 'SHARES_OUTSTANDING')
        if not ShareCountObservation.objects.filter(source_snapshot=share_snapshot).exists():
            self.normalize_share_counts(stock)
        earnings_dates = self._earnings_dates(stock)
        cash_flow = self._latest_snapshot(stock, 'CASH_FLOW')
        reports = []
        for row in cash_flow.payload.get('quarterlyReports', []):
            fiscal_end = row.get('fiscalDateEnding')
            reported_date = earnings_dates.get(fiscal_end)
            if not reported_date or reported_date > signal_date:
                continue
            try:
                operating_cash_flow = _as_decimal(row.get('operatingCashflow'), 'operating cash flow')
                capital_expenditures = abs(_as_decimal(row.get('capitalExpenditures'), 'capital expenditures'))
                period_end = date.fromisoformat(fiscal_end)
            except (ValueSignalUnavailable, ValueError):
                continue
            reports.append((period_end, reported_date, operating_cash_flow - capital_expenditures))
        reports.sort(reverse=True)
        if len(reports) < 4:
            raise ValueSignalUnavailable(f'fewer than four available quarterly cash-flow reports for {stock.symbol}')
        trailing_reports = reports[:4]
        trailing_fcf = sum((item[2] for item in trailing_reports), Decimal('0'))

        shares = stock.share_count_observations.filter(
            availability_date__isnull=False,
            availability_date__lte=signal_date,
        ).order_by('-observation_date').first()
        if shares is None:
            raise ValueSignalUnavailable(f'no share count with an availability proxy for {stock.symbol}')
        shares_used = shares.basic_shares or shares.diluted_shares
        if not shares_used or shares_used <= 0:
            raise ValueSignalUnavailable(f'invalid share count for {stock.symbol}')

        # Raw close and unadjusted shares form a consistent historical market cap.
        price = DailyPrice.objects.filter(stock=stock, trading_date__lte=signal_date).order_by('-trading_date').first()
        if price is None:
            raise ValueSignalUnavailable(f'no stored price available for {stock.symbol}')
        market_cap = price.close * shares_used
        if market_cap <= 0:
            raise ValueSignalUnavailable(f'invalid market cap for {stock.symbol}')
        availability_date = max(item[1] for item in trailing_reports + [(shares.observation_date, shares.availability_date, Decimal('0'))])
        if availability_date > signal_date:
            raise ValueSignalUnavailable(f'value inputs are not available by {signal_date}')
        signal, _ = FreeCashFlowYieldSignal.objects.update_or_create(
            stock=stock,
            signal_date=signal_date,
            defaults={
                'availability_date': availability_date,
                'trailing_free_cash_flow': trailing_fcf,
                'shares_used': shares_used,
                'raw_close_used': price.close,
                'market_cap_used': market_cap,
                'free_cash_flow_yield': trailing_fcf / market_cap,
                'availability_basis': self.AVAILABILITY_BASIS,
                'metadata': {
                    'cash_flow_snapshot_id': cash_flow.id,
                    'share_snapshot_id': shares.source_snapshot_id,
                    'cash_flow_fiscal_periods': [item[0].isoformat() for item in trailing_reports],
                    'price_date': price.trading_date.isoformat(),
                    'share_observation_date': shares.observation_date.isoformat(),
                },
            },
        )
        return signal
