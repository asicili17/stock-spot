from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import Client, TestCase

from stock_spot.models import (
    AnnualBalanceSheet, AnnualEarning, AnnualIncomeStatement, DailyPrice,
    FundamentalSnapshot, MomentumBacktestRun, QuarterlyEarning, Stock,
)
from stock_spot.services.fundamentals_audit import AlphaVantageFundamentalsAuditor
from stock_spot.services.market_data import DailyPriceCacheService, DailyPriceValidationError, MonthlyMomentumBacktester
from stock_spot.services.value import FreeCashFlowYieldService
from stock_spot.services.fundamentals import ConservativeValuationCalculator, EarningsGrowthMetricCalculator
from stock_spot.services.alpha_vantage import AlphaVantageError, AlphaVantageService, StockNotFoundError
from stock_spot.services.email import EmailService
from stock_spot.services.stock_profile_refresh_service import StockProfileRefreshService
from stock_spot.views import _parse_symbols


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


class StockModelTests(TestCase):
    def test_margin_of_safety_properties_handle_available_and_missing_values(self):
        stock = Stock.objects.create(
            symbol='SAFE', conservativeCompanyValuation=1_250, marketCap=1_000,
        )
        self.assertEqual(stock.margin_of_safety, 250)
        self.assertEqual(stock.margin_of_safety_percentage, Decimal('20'))

        stock.marketCap = None
        self.assertIsNone(stock.margin_of_safety)
        self.assertIsNone(stock.margin_of_safety_percentage)


class AlphaVantageServiceTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(symbol='AV', isBought=False)
        self.service = AlphaVantageService()

    @patch('stock_spot.services.alpha_vantage.requests.get')
    def test_api_request_returns_payload_and_translates_provider_errors(self, get):
        get.return_value = SimpleNamespace(
            raise_for_status=MagicMock(),
            json=lambda: {'Global Quote': {'05. price': '10'}},
        )
        self.assertEqual(self.service._make_api_request({'function': 'GLOBAL_QUOTE'}), {'Global Quote': {'05. price': '10'}})

        get.return_value = SimpleNamespace(raise_for_status=MagicMock(), json=lambda: {'Note': 'slow down'})
        with self.assertRaises(AlphaVantageError):
            self.service._make_api_request({'function': 'GLOBAL_QUOTE'})

    def test_saves_earnings_and_company_overview(self):
        self.service._save_earnings_to_db('AV', {
            'annualEarnings': [{'fiscalDateEnding': '2024-12-31', 'reportedEPS': '2.5'}],
            'quarterlyEarnings': [{
                'fiscalDateEnding': '2025-03-31', 'reportedDate': '2025-04-20',
                'reportedEPS': '0.75', 'estimatedEPS': '0.70', 'surprise': '0.05',
                'surprisePercentage': '7.14', 'reportTime': 'bmo',
            }],
        })
        self.service._save_company_overview('AV', {
            'Description': 'Test company', 'Sector': 'Technology', 'MarketCapitalization': '12345',
        })

        self.stock.refresh_from_db()
        self.assertEqual(self.stock.marketCap, 12345)
        self.assertEqual(self.stock.sector, 'Technology')
        self.assertEqual(AnnualEarning.objects.get(stock=self.stock).reportedEPS, Decimal('2.5'))
        self.assertEqual(QuarterlyEarning.objects.get(stock=self.stock).surprise, Decimal('0.05'))

    def test_unknown_stock_raises_domain_error(self):
        with self.assertRaises(StockNotFoundError):
            self.service._get_stock('MISSING')


class ProfileRefreshAndEmailServiceTests(TestCase):
    def test_profile_refresh_calls_provider_and_named_metric_calculators(self):
        service = StockProfileRefreshService()
        service.alpha_vantage = MagicMock()
        service.earnings_growth = MagicMock()
        service.conservative_valuation = MagicMock()

        stock = service.refresh('prof')

        self.assertEqual(stock.symbol, 'PROF')
        service.alpha_vantage.get_price_today.assert_called_once_with('PROF')
        service.alpha_vantage.get_cash_flow_data.assert_called_once_with('PROF')
        service.earnings_growth.calculate_quarterly_yoy_eps_growth.assert_called_once()
        service.conservative_valuation.calculate.assert_called_once()

    @patch('stock_spot.services.email.requests.post')
    def test_email_service_renders_and_posts_expected_mailgun_payload(self, post):
        post.return_value = SimpleNamespace(status_code=200)
        stock = Stock.objects.create(symbol='MAIL', name='Mail Company')
        service = EmailService()
        response = service.send_stock_report([stock], 'reader@example.com', report_date='10-30-2026')

        self.assertEqual(response.status_code, 200)
        self.assertIn('MAIL', post.call_args.kwargs['data']['html'])
        self.assertEqual(post.call_args.kwargs['data']['to'], 'reader@example.com')


class ViewAndCommandTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_symbol_parser_normalizes_deduplicates_and_rejects_other_inputs(self):
        self.assertEqual(_parse_symbols(' msft, AAPL,msft '), ['MSFT', 'AAPL'])
        self.assertEqual(_parse_symbols(['goog', 'GOOG', 7]), ['GOOG', '7'])
        self.assertEqual(_parse_symbols(None), [])

    @patch('stock_spot.views.EmailService')
    def test_preview_report_requires_symbols_and_returns_rendered_html(self, email_service_class):
        missing = self.client.post('/api/stocks/api/report/preview/', data={}, content_type='application/json')
        self.assertEqual(missing.status_code, 400)

        service = email_service_class.return_value
        service.prepare_stock_report.return_value = {'stocks': [], 'report_date': '10-30-2026'}
        service.render_stock_report.return_value = '<p>report</p>'
        response = self.client.post(
            '/api/stocks/api/report/preview/', data='{"symbols": "aapl, msft"}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['symbols'], ['AAPL', 'MSFT'])

    @patch('stock_spot.management.commands.refresh_av_prices.DailyPriceCacheService')
    def test_refresh_command_passes_monthly_adjusted_options(self, service_class):
        service_class.return_value.refresh.return_value = {
            'symbol': 'AAPL', 'cached': 10, 'rejected': [], 'endpoint': 'TIME_SERIES_MONTHLY_ADJUSTED',
        }
        call_command('refresh_av_prices', '--monthly-adjusted', 'AAPL')
        service_class.return_value.refresh.assert_called_once_with('AAPL', adjusted=True, monthly=True)
