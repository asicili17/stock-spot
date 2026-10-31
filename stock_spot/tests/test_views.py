from types import SimpleNamespace
from unittest.mock import patch
from django.http import HttpResponse
from django.test import Client,RequestFactory,TestCase
from rest_framework.test import APIRequestFactory
from stock_spot.models import Stock
from stock_spot.views import StockViewSet, _parse_symbols
class ViewsTests(TestCase):
    def setUp(self): self.client=Client()
    def test_symbol_parser_normalizes_and_deduplicates(self):
        self.assertEqual(_parse_symbols(' msft, AAPL,msft '),['MSFT','AAPL']); self.assertEqual(_parse_symbols(None),[])
    @patch('django.shortcuts.render', return_value=HttpResponse())
    def test_home_page_renders(self, render):
        from stock_spot.views import home_page
        self.assertEqual(home_page(RequestFactory().get('/')).status_code, 200)
        render.assert_called_once()
    def test_create_stock_returns_created_profile_or_provider_error(self):
        factory=APIRequestFactory(); view=StockViewSet(); stock=Stock.objects.create(symbol='NEW',isBought=False)
        view.stock_service.refresh=lambda symbol: stock
        success=view.create_stock(type('Request', (), {'data': {'symbol': 'NEW'}})())
        self.assertEqual(success.status_code,201); self.assertEqual(success.data['symbol'],'NEW')
        view.stock_service.refresh=lambda symbol: (_ for _ in ()).throw(ValueError('provider unavailable'))
        failure=view.create_stock(type('Request', (), {'data': {'symbol': 'BAD'}})())
        self.assertEqual(failure.status_code,400)
    @patch('stock_spot.views.EmailService')
    def test_preview_report_requires_symbols_and_returns_html(self,email_service_class):
        self.assertEqual(self.client.post('/api/stocks/api/report/preview/',data={},content_type='application/json').status_code,400)
        service=email_service_class.return_value; service.prepare_stock_report.return_value={'stocks':[],'report_date':'10-30-2026'}; service.render_stock_report.return_value='<p>report</p>'
        response=self.client.post('/api/stocks/api/report/preview/',data='{"symbols":"aapl, msft"}',content_type='application/json')
        self.assertEqual(response.status_code,200); self.assertEqual(response.json()['symbols'],['AAPL','MSFT'])
    @patch('stock_spot.views.EmailService')
    def test_send_report_validates_and_sends_previously_previewed_stocks(self,email_service_class):
        self.assertEqual(self.client.post('/api/stocks/api/report/send/',data='{"symbols":"AAPL","email":"bad"}',content_type='application/json').status_code,400)
        stock=Stock.objects.create(symbol='AAPL',isBought=False)
        email_service_class.return_value.send_stock_report.return_value=SimpleNamespace(status_code=200)
        response=self.client.post('/api/stocks/api/report/send/',data='{"symbols":"AAPL","email":"reader@example.com"}',content_type='application/json')
        self.assertEqual(response.status_code,200); email_service_class.return_value.send_stock_report.assert_called_once_with([stock],'reader@example.com')
