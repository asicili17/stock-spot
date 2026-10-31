from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
from django.test import TestCase
from stock_spot.models import AnnualCashFlow,AnnualEarning,QuarterlyCashFlow,QuarterlyEarning,Stock
from stock_spot.services.alpha_vantage import AlphaVantageError,AlphaVantageService,StockNotFoundError
class AlphaVantageServiceTests(TestCase):
    def setUp(self): self.stock=Stock.objects.create(symbol='AV',isBought=False); self.service=AlphaVantageService()
    @patch('stock_spot.services.alpha_vantage.requests.get')
    def test_translates_provider_errors(self,get):
        get.return_value=SimpleNamespace(raise_for_status=MagicMock(),json=lambda:{'Global Quote':{'05. price':'10'}}); self.assertIn('Global Quote',self.service._make_api_request({'function':'GLOBAL_QUOTE'}))
        get.return_value=SimpleNamespace(raise_for_status=MagicMock(),json=lambda:{'Note':'slow down'})
        with self.assertRaises(AlphaVantageError): self.service._make_api_request({'function':'GLOBAL_QUOTE'})
    def test_saves_earnings_and_company_overview(self):
        self.service._save_earnings_to_db('AV',{'annualEarnings':[{'fiscalDateEnding':'2024-12-31','reportedEPS':'2.5'}],'quarterlyEarnings':[{'fiscalDateEnding':'2025-03-31','reportedDate':'2025-04-20','reportedEPS':'0.75','estimatedEPS':'0.70','surprise':'0.05','surprisePercentage':'7.14','reportTime':'bmo'}]}); self.service._save_company_overview('AV',{'Description':'Test','Sector':'Technology','MarketCapitalization':'12345'})
        self.stock.refresh_from_db(); self.assertEqual(self.stock.marketCap,12345); self.assertEqual(AnnualEarning.objects.get(stock=self.stock).reportedEPS,Decimal('2.5')); self.assertEqual(QuarterlyEarning.objects.get(stock=self.stock).surprise,Decimal('0.05'))
    def test_unknown_stock_raises_domain_error(self):
        with self.assertRaises(StockNotFoundError): self.service._get_stock('MISSING')
    def test_saves_price_and_financial_statement_reports(self):
        self.service._save_price_today('AV','12.34')
        self.service._save_financial_data('AV',{'annualReports':[{'fiscalDateEnding':'2024-12-31','operatingCashflow':'100','capitalExpenditures':'20'}],'quarterlyReports':[{'fiscalDateEnding':'2025-03-31','operatingCashflow':'25','capitalExpenditures':'5'}]},AnnualCashFlow,QuarterlyCashFlow,self.service.CASH_FLOW_FIELDS)
        self.stock.refresh_from_db(); self.assertEqual(self.stock.currentPrice,Decimal('12.34')); self.assertEqual(AnnualCashFlow.objects.get(stock=self.stock).operatingCashflow,100); self.assertEqual(QuarterlyCashFlow.objects.get(stock=self.stock).capitalExpenditures,5)
