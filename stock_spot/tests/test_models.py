from decimal import Decimal
from django.test import TestCase
from stock_spot.models import Stock
class StockModelTests(TestCase):
    def test_margin_of_safety_properties_handle_available_and_missing_values(self):
        stock=Stock.objects.create(symbol='SAFE',conservativeCompanyValuation=1250,marketCap=1000); self.assertEqual(stock.margin_of_safety,250); self.assertEqual(stock.margin_of_safety_percentage,Decimal('20'))
        stock.marketCap=None; self.assertIsNone(stock.margin_of_safety); self.assertIsNone(stock.margin_of_safety_percentage)
