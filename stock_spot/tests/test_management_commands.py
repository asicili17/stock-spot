from unittest.mock import patch
from django.core.management import call_command
from django.test import TestCase
from stock_spot.models import Stock
class ManagementCommandTests(TestCase):
    @patch('stock_spot.management.commands.refresh_av_prices.DailyPriceCacheService')
    def test_refresh_command_passes_monthly_adjusted_options(self,service_class):
        service_class.return_value.refresh.return_value={'symbol':'AAPL','cached':10,'rejected':[],'endpoint':'TIME_SERIES_MONTHLY_ADJUSTED'}
        call_command('refresh_av_prices','--monthly-adjusted','AAPL')
        service_class.return_value.refresh.assert_called_once_with('AAPL',adjusted=True,monthly=True)
    @patch('stock_spot.management.commands.audit_av_fundamentals.AlphaVantageFundamentalsAuditor')
    def test_audit_command_uses_requested_endpoints(self,auditor_class):
        auditor_class.return_value.audit_symbol.return_value=[{'symbol':'AAPL','endpoint':'EARNINGS','record_count':1,'earliest_date':'2024-01-01','latest_date':'2024-01-01','has_reported_date':True,'snapshot_id':1}]
        call_command('audit_av_fundamentals','AAPL','--endpoints','EARNINGS','--seconds-between','0')
        auditor_class.return_value.audit_symbol.assert_called_once()
    @patch('stock_spot.management.commands.backtest_momentum.MonthlyMomentumBacktester')
    def test_backtest_command_forwards_factor_options(self,backtester_class):
        backtester_class.return_value.run.return_value=type('Run',(),{'id':1,'summary':{'total_return':'0','annualized_return':'0','max_drawdown':'0','rebalance_count':1}})()
        call_command('backtest_momentum','--top-n','5','--value-weight','0.5')
        backtester_class.return_value.run.assert_called_once()
