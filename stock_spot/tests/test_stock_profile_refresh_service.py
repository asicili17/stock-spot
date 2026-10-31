from unittest.mock import MagicMock
from django.test import TestCase
from stock_spot.services.stock_profile_refresh_service import StockProfileRefreshService
class StockProfileRefreshServiceTests(TestCase):
    def test_refresh_calls_provider_and_metric_calculators(self):
        service=StockProfileRefreshService(); service.alpha_vantage=MagicMock(); service.earnings_growth=MagicMock(); service.conservative_valuation=MagicMock()
        stock=service.refresh('prof')
        self.assertEqual(stock.symbol,'PROF'); service.alpha_vantage.get_price_today.assert_called_once_with('PROF'); service.alpha_vantage.get_cash_flow_data.assert_called_once_with('PROF'); service.earnings_growth.calculate_quarterly_yoy_eps_growth.assert_called_once(); service.conservative_valuation.calculate.assert_called_once()
