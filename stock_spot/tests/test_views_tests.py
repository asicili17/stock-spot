from unittest.mock import patch
from django.test import Client,TestCase
from stock_spot.views import _parse_symbols
class ViewsTests(TestCase):
    def setUp(self): self.client=Client()
    def test_symbol_parser_normalizes_and_deduplicates(self):
        self.assertEqual(_parse_symbols(' msft, AAPL,msft '),['MSFT','AAPL']); self.assertEqual(_parse_symbols(None),[])
    @patch('stock_spot.views.EmailService')
    def test_preview_report_requires_symbols_and_returns_html(self,email_service_class):
        self.assertEqual(self.client.post('/api/stocks/api/report/preview/',data={},content_type='application/json').status_code,400)
        service=email_service_class.return_value; service.prepare_stock_report.return_value={'stocks':[],'report_date':'10-30-2026'}; service.render_stock_report.return_value='<p>report</p>'
        response=self.client.post('/api/stocks/api/report/preview/',data='{"symbols":"aapl, msft"}',content_type='application/json')
        self.assertEqual(response.status_code,200); self.assertEqual(response.json()['symbols'],['AAPL','MSFT'])
