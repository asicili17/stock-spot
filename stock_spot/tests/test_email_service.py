from types import SimpleNamespace
from unittest.mock import MagicMock,patch
from django.test import TestCase
from stock_spot.models import Stock
from stock_spot.services.email import EmailService
class EmailServiceTests(TestCase):
    @patch('stock_spot.services.email.requests.post')
    def test_renders_and_posts_mailgun_payload(self,post):
        post.return_value=SimpleNamespace(status_code=200); stock=Stock.objects.create(symbol='MAIL',name='Mail Company'); response=EmailService().send_stock_report([stock],'reader@example.com',report_date='10-30-2026')
        self.assertEqual(response.status_code,200); self.assertIn('MAIL',post.call_args.kwargs['data']['html']); self.assertEqual(post.call_args.kwargs['data']['to'],'reader@example.com')
    @patch('stock_spot.services.email.StockProfileRefreshService')
    def test_prepare_report_refreshes_requested_symbols_in_order(self,refresh_service):
        Stock.objects.create(symbol='AAPL',isBought=False); Stock.objects.create(symbol='MSFT',isBought=False)
        report=EmailService().prepare_stock_report(['MSFT','AAPL'])
        self.assertEqual([stock.symbol for stock in report['stocks']],['MSFT','AAPL'])
        self.assertEqual(refresh_service.return_value.refresh.call_count,2)
