from types import SimpleNamespace
from unittest.mock import patch
from django.test import TestCase
from stock_spot.models import Stock
from stock_spot.services.email import EmailService
class EmailServiceTests(TestCase):
    @patch('stock_spot.services.email.requests.post')
    def test_renders_and_posts_mailgun_payload(self,post):
        post.return_value=SimpleNamespace(status_code=200); stock=Stock.objects.create(symbol='MAIL',name='Mail Company'); response=EmailService().send_stock_report([stock],'reader@example.com',report_date='10-30-2026')
        self.assertEqual(response.status_code,200); self.assertIn('MAIL',post.call_args.kwargs['data']['html']); self.assertEqual(post.call_args.kwargs['data']['to'],'reader@example.com')
