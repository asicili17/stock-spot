from unittest.mock import patch
from django.core.management import call_command
from django.test import TestCase
class ManagementCommandTests(TestCase):
    @patch('stock_spot.management.commands.refresh_av_prices.DailyPriceCacheService')
    def test_refresh_command_passes_monthly_adjusted_options(self,service_class):
        service_class.return_value.refresh.return_value={'symbol':'AAPL','cached':10,'rejected':[],'endpoint':'TIME_SERIES_MONTHLY_ADJUSTED'}
        call_command('refresh_av_prices','--monthly-adjusted','AAPL')
        service_class.return_value.refresh.assert_called_once_with('AAPL',adjusted=True,monthly=True)
