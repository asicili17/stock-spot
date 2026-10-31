from datetime import date
from decimal import Decimal

from django.test import TestCase

from stock_spot.models import (
    AnnualBalanceSheet, AnnualEarning, AnnualIncomeStatement, DailyPrice,
    FundamentalSnapshot, MomentumBacktestRun, QuarterlyEarning, Stock,
)
from stock_spot.services.fundamentals_audit import AlphaVantageFundamentalsAuditor
from stock_spot.services.market_data import DailyPriceCacheService, DailyPriceValidationError, MonthlyMomentumBacktester
from stock_spot.services.value import FreeCashFlowYieldService
from stock_spot.services.fundamentals import ConservativeValuationCalculator, EarningsGrowthMetricCalculator


class FakeAlphaVantageClient:
    def __init__(self, payloads):
        self.payloads = payloads

    def _make_api_request(self, params):
        return self.payloads[params['function']]


class DailyPriceCacheTests(TestCase):
    def test_refresh_caches_valid_rows_and_keeps_adjusted_values(self):
        adjusted_payload = {
            'Time Series (Daily)': {
                '2025-01-03': {
                    '1. open': '10.0', '2. high': '12.0', '3. low': '9.0', '4. close': '11.0',
                    '5. adjusted close': '10.5', '5. volume': '1000',
                    '7. dividend amount': '0.25', '8. split coefficient': '1.0',
                },
                'bad-date': {'1. open': '1', '2. high': '1', '3. low': '1', '4. close': '1', '5. volume': '1'},
            },
        }
        plain_payload = {
            'Time Series (Daily)': {
                '2025-01-03': {'1. open': '10.0', '2. high': '12.0', '3. low': '9.0', '4. close': '11.5', '5. volume': '1001'},
            },
        }
        client = FakeAlphaVantageClient({
            'TIME_SERIES_DAILY_ADJUSTED': adjusted_payload,
            'TIME_SERIES_DAILY': plain_payload,
        })
        service = DailyPriceCacheService(client)

        result = service.refresh('acme', adjusted=True)
        self.assertEqual(result['cached'], 1)
        self.assertEqual(len(result['rejected']), 1)
        service.refresh('acme', adjusted=False)

        price = DailyPrice.objects.get(stock__symbol='ACME', trading_date=date(2025, 1, 3))
        self.assertEqual(price.close, Decimal('11.500000'))
        self.assertEqual(price.adjusted_close, Decimal('10.500000'))

    def test_invalid_price_rows_are_rejected(self):
        with self.assertRaises(DailyPriceValidationError):
            DailyPriceCacheService.parse_row(
                '2025-01-03',
                {'1. open': '10', '2. high': '9', '3. low': '8', '4. close': '10', '5. volume': '100'},
                adjusted=False,
            )

    def test_monthly_adjusted_row_uses_its_documented_volume_column(self):
        row = DailyPriceCacheService.parse_row(
            '2025-01-31',
            {
                '1. open': '10', '2. high': '12', '3. low': '9', '4. close': '11',
                '5. adjusted close': '10.5', '6. volume': '1234', '7. dividend amount': '0.2',
            },
            adjusted=True,
            monthly=True,
        )
        self.assertEqual(row['volume'], 1234)
        self.assertEqual(row['adjusted_close'], Decimal('10.5'))


class MomentumBacktestTests(TestCase):
    def _add_monthly_prices(self, stock, multiplier):
        for year in (2024, 2025):
            last_month = 12 if year == 2024 else 8
            for month in range(1, last_month + 1):
                value = Decimal('100') * (Decimal(str(multiplier)) ** Decimal((year - 2024) * 12 + month - 1))
                DailyPrice.objects.create(
                    stock=stock,
                    trading_date=date(year, month, 28),
                    open=value, high=value, low=value, close=value,
                    adjusted_close=value, volume=1_000_000,
                )

    def test_monthly_momentum_persists_an_explainable_run(self):
        winner = Stock.objects.create(symbol='WIN', isBought=False)
        loser = Stock.objects.create(symbol='LOSE', isBought=False)
        self._add_monthly_prices(winner, '1.02')
        self._add_monthly_prices(loser, '1.005')

        run = MonthlyMomentumBacktester([winner, loser]).run(top_n=1, require_adjusted=True)

        self.assertIsInstance(run, MomentumBacktestRun)
        self.assertGreater(len(run.rebalances), 1)
        self.assertEqual(run.rebalances[0]['holdings'][0]['symbol'], 'WIN')
        self.assertEqual(run.summary['return_basis'], 'adjusted close only')


class FundamentalsAuditTests(TestCase):
    def test_audit_creates_one_immutable_snapshot_per_changed_response(self):
        payload = {
            'annualEarnings': [{'fiscalDateEnding': '2024-12-31', 'reportedEPS': '2.00'}],
            'quarterlyEarnings': [{'fiscalDateEnding': '2025-03-31', 'reportedDate': '2025-05-01'}],
        }
        auditor = AlphaVantageFundamentalsAuditor(FakeAlphaVantageClient({'EARNINGS': payload}))

        first = auditor.audit_symbol('audit', endpoints=('EARNINGS',))
        second = auditor.audit_symbol('audit', endpoints=('EARNINGS',))

        self.assertTrue(first[0]['created_snapshot'])
        self.assertFalse(second[0]['created_snapshot'])
        self.assertEqual(FundamentalSnapshot.objects.count(), 1)
        self.assertTrue(first[0]['has_reported_date'])


class FreeCashFlowYieldTests(TestCase):
    def test_builds_fcf_yield_from_available_cash_flow_and_share_count(self):
        stock = Stock.objects.create(symbol='VALUE', isBought=False)
        earnings = {
            'quarterlyEarnings': [
                {'fiscalDateEnding': f'2024-{month:02d}-{day}', 'reportedDate': f'2024-{report_month:02d}-15'}
                for month, day, report_month in [(3, 31, 4), (6, 30, 7), (9, 30, 10), (12, 31, 2)]
            ],
        }
        # The December fiscal period becomes available in the next calendar year.
        earnings['quarterlyEarnings'][-1]['reportedDate'] = '2025-02-15'
        cash_flow = {
            'quarterlyReports': [
                {'fiscalDateEnding': item['fiscalDateEnding'], 'operatingCashflow': '100', 'capitalExpenditures': '30'}
                for item in earnings['quarterlyEarnings']
            ],
        }
        shares = {'data': [
            {'date': item['fiscalDateEnding'], 'shares_outstanding_basic': '100', 'shares_outstanding_diluted': '105'}
            for item in earnings['quarterlyEarnings']
        ]}
        for endpoint, payload, content_hash in [
            ('EARNINGS', earnings, 'earnings'), ('CASH_FLOW', cash_flow, 'cash'), ('SHARES_OUTSTANDING', shares, 'shares'),
        ]:
            FundamentalSnapshot.objects.create(stock=stock, endpoint=endpoint, content_hash=content_hash, payload=payload)
        DailyPrice.objects.create(
            stock=stock, trading_date=date(2025, 2, 28),
            open=Decimal('10'), high=Decimal('10'), low=Decimal('10'), close=Decimal('10'),
            adjusted_close=Decimal('10'), volume=100,
        )

        signal = FreeCashFlowYieldService().build(stock, date(2025, 2, 28))

        self.assertEqual(signal.trailing_free_cash_flow, Decimal('280.0000'))
        self.assertEqual(signal.market_cap_used, Decimal('1000.0000'))
        self.assertEqual(signal.free_cash_flow_yield, Decimal('0.2800000000'))


class LatestFundamentalMetricCalculatorTests(TestCase):
    def test_earnings_growth_metrics_use_matching_periods_and_elapsed_years(self):
        stock = Stock.objects.create(symbol='METR', isBought=False)
        QuarterlyEarning.objects.create(
            stock=stock, fiscalDateEnding=date(2024, 3, 31), reportedDate=date(2024, 4, 20),
            reportedEPS=Decimal('2'), reportTime='bmo',
        )
        QuarterlyEarning.objects.create(
            stock=stock, fiscalDateEnding=date(2025, 3, 31), reportedDate=date(2025, 4, 20),
            reportedEPS=Decimal('3'), reportTime='bmo',
        )
        AnnualEarning.objects.create(stock=stock, fiscalDateEnding=date(2021, 12, 31), reportedEPS=Decimal('1'))
        AnnualEarning.objects.create(stock=stock, fiscalDateEnding=date(2025, 12, 31), reportedEPS=Decimal('2'))

        calculator = EarningsGrowthMetricCalculator()
        yoy_growth = calculator.calculate_quarterly_yoy_eps_growth(stock)
        cagr = calculator.calculate_annual_eps_cagr(stock)

        self.assertEqual(yoy_growth, Decimal('50'))
        self.assertAlmostEqual(float(cagr), 18.92, places=2)

    def test_conservative_valuation_exposes_the_heuristic_components(self):
        stock = Stock.objects.create(symbol='VAL2', isBought=False)
        AnnualBalanceSheet.objects.create(
            stock=stock, fiscalDateEnding=date(2025, 12, 31), totalAssets=1_000,
            goodwill=100, intangibleAssets=50, totalLiabilities=500,
        )
        AnnualIncomeStatement.objects.create(
            stock=stock, fiscalDateEnding=date(2025, 12, 31),
            netIncomeFromContinuingOperations=100, depreciationAndAmortization=20,
        )

        components = ConservativeValuationCalculator().calculate(stock)

        self.assertEqual(components.tangible_net_assets, 350)
        self.assertEqual(components.normalized_earnings, 120)
        self.assertEqual(components.estimated_value, 1_550)
        stock.refresh_from_db()
        self.assertEqual(stock.conservativeCompanyValuation, 1_550)
