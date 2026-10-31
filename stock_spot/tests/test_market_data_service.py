from datetime import date
from decimal import Decimal
from django.test import TestCase
from stock_spot.models import DailyPrice, MomentumBacktestRun, Stock
from stock_spot.services.market_data import DailyPriceCacheService, DailyPriceValidationError, MonthlyMomentumBacktester
from stock_spot.tests.helpers import FakeAlphaVantageClient

class DailyPriceCacheServiceTests(TestCase):
    def test_refresh_caches_valid_rows_and_keeps_adjusted_values(self):
        client = FakeAlphaVantageClient({'TIME_SERIES_DAILY_ADJUSTED': {'Time Series (Daily)': {'2025-01-03': {'1. open':'10','2. high':'12','3. low':'9','4. close':'11','5. adjusted close':'10.5','5. volume':'1000','7. dividend amount':'0.25','8. split coefficient':'1'}, 'bad-date': {'1. open':'1','2. high':'1','3. low':'1','4. close':'1','5. volume':'1'}}}, 'TIME_SERIES_DAILY': {'Time Series (Daily)': {'2025-01-03': {'1. open':'10','2. high':'12','3. low':'9','4. close':'11.5','5. volume':'1001'}}}})
        service = DailyPriceCacheService(client)
        result = service.refresh('acme', adjusted=True); service.refresh('acme', adjusted=False)
        price = DailyPrice.objects.get(stock__symbol='ACME', trading_date=date(2025, 1, 3))
        self.assertEqual(result['cached'], 1); self.assertEqual(len(result['rejected']), 1)
        self.assertEqual(price.close, Decimal('11.500000')); self.assertEqual(price.adjusted_close, Decimal('10.500000'))
    def test_rejects_inconsistent_price_range(self):
        with self.assertRaises(DailyPriceValidationError): DailyPriceCacheService.parse_row('2025-01-03', {'1. open':'10','2. high':'9','3. low':'8','4. close':'10','5. volume':'100'}, adjusted=False)
    def test_parses_monthly_adjusted_volume(self):
        row = DailyPriceCacheService.parse_row('2025-01-31', {'1. open':'10','2. high':'12','3. low':'9','4. close':'11','5. adjusted close':'10.5','6. volume':'1234','7. dividend amount':'0.2'}, adjusted=True, monthly=True)
        self.assertEqual(row['volume'], 1234)

class MonthlyMomentumBacktesterTests(TestCase):
    def _add_prices(self, stock, multiplier):
        for year in (2024, 2025):
            for month in range(1, 13 if year == 2024 else 9):
                value = Decimal('100') * (Decimal(str(multiplier)) ** Decimal((year-2024)*12+month-1))
                DailyPrice.objects.create(stock=stock, trading_date=date(year,month,28), open=value,high=value,low=value,close=value,adjusted_close=value,volume=1_000_000)
    def test_persists_explainable_monthly_momentum_run(self):
        winner, loser = Stock.objects.create(symbol='WIN',isBought=False), Stock.objects.create(symbol='LOSE',isBought=False)
        self._add_prices(winner,'1.02'); self._add_prices(loser,'1.005')
        run=MonthlyMomentumBacktester([winner,loser]).run(top_n=1,require_adjusted=True)
        self.assertIsInstance(run,MomentumBacktestRun); self.assertEqual(run.rebalances[0]['holdings'][0]['symbol'],'WIN')
