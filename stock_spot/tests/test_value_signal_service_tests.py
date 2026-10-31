from datetime import date
from decimal import Decimal
from django.test import TestCase
from stock_spot.models import DailyPrice, FundamentalSnapshot, Stock
from stock_spot.services.value import FreeCashFlowYieldService
class FreeCashFlowYieldServiceTests(TestCase):
    def test_builds_signal_from_available_cash_flow_and_share_count(self):
        stock=Stock.objects.create(symbol='VALUE',isBought=False)
        earnings={'quarterlyEarnings':[{'fiscalDateEnding':'2024-03-31','reportedDate':'2024-04-15'},{'fiscalDateEnding':'2024-06-30','reportedDate':'2024-07-15'},{'fiscalDateEnding':'2024-09-30','reportedDate':'2024-10-15'},{'fiscalDateEnding':'2024-12-31','reportedDate':'2025-02-15'}]}
        cash={'quarterlyReports':[{'fiscalDateEnding':item['fiscalDateEnding'],'operatingCashflow':'100','capitalExpenditures':'30'} for item in earnings['quarterlyEarnings']]}; shares={'data':[{'date':item['fiscalDateEnding'],'shares_outstanding_basic':'100'} for item in earnings['quarterlyEarnings']]}
        for endpoint,payload in [('EARNINGS',earnings),('CASH_FLOW',cash),('SHARES_OUTSTANDING',shares)]: FundamentalSnapshot.objects.create(stock=stock,endpoint=endpoint,content_hash=endpoint,payload=payload)
        DailyPrice.objects.create(stock=stock,trading_date=date(2025,2,28),open=10,high=10,low=10,close=10,adjusted_close=10,volume=100)
        signal=FreeCashFlowYieldService().build(stock,date(2025,2,28))
        self.assertEqual(signal.trailing_free_cash_flow,Decimal('280.0000')); self.assertEqual(signal.free_cash_flow_yield,Decimal('0.2800000000'))
