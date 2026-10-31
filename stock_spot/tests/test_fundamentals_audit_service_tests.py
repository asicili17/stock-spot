from django.test import TestCase
from stock_spot.models import FundamentalSnapshot
from stock_spot.services.fundamentals_audit import AlphaVantageFundamentalsAuditor
from stock_spot.tests.helpers import FakeAlphaVantageClient
class AlphaVantageFundamentalsAuditorTests(TestCase):
    def test_creates_one_snapshot_for_unchanged_payload(self):
        payload={'annualEarnings':[{'fiscalDateEnding':'2024-12-31'}],'quarterlyEarnings':[{'fiscalDateEnding':'2025-03-31','reportedDate':'2025-05-01'}]}
        auditor=AlphaVantageFundamentalsAuditor(FakeAlphaVantageClient({'EARNINGS':payload}))
        self.assertTrue(auditor.audit_symbol('audit',endpoints=('EARNINGS',),seconds_between=0)[0]['created_snapshot'])
        self.assertFalse(auditor.audit_symbol('audit',endpoints=('EARNINGS',),seconds_between=0)[0]['created_snapshot'])
        self.assertEqual(FundamentalSnapshot.objects.count(),1)
