from django.core.management.base import BaseCommand, CommandError

from stock_spot.services.fundamentals_audit import AUDIT_ENDPOINTS, AlphaVantageFundamentalsAuditor


class Command(BaseCommand):
    help = 'Save Alpha Vantage fundamental/share-count responses and report their date coverage.'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='+', help='Ticker symbols, e.g. AAPL MSFT')
        parser.add_argument(
            '--endpoints', nargs='+', choices=AUDIT_ENDPOINTS,
            help='Limit the audit to named Alpha Vantage endpoints.',
        )
        parser.add_argument(
            '--seconds-between', type=float, default=1.1,
            help='Pause between requests to avoid Alpha Vantage burst throttling.',
        )

    def handle(self, *args, **options):
        auditor = AlphaVantageFundamentalsAuditor()
        for symbol in options['symbols']:
            try:
                results = auditor.audit_symbol(
                    symbol,
                    endpoints=options['endpoints'] or AUDIT_ENDPOINTS,
                    seconds_between=options['seconds_between'],
                )
            except Exception as exc:
                raise CommandError(f'{symbol.upper()}: {exc}') from exc
            for result in results:
                self.stdout.write(
                    f"{result['symbol']} {result['endpoint']}: {result['record_count']} records, "
                    f"dates {result['earliest_date']} to {result['latest_date']}, "
                    f"reportedDate={result['has_reported_date']}, snapshot={result['snapshot_id']}"
                )
