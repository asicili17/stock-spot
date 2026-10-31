from datetime import date

from django.core.management.base import BaseCommand, CommandError

from stock_spot.models import Stock
from stock_spot.services.value import FreeCashFlowYieldService, ValueSignalUnavailable


class Command(BaseCommand):
    help = 'Build auditable trailing-free-cash-flow-yield signals from Alpha Vantage snapshots.'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='+', help='Ticker symbols with audited cash flow, earnings, and share counts.')
        parser.add_argument('--as-of', required=True, help='Signal date in YYYY-MM-DD format.')

    def handle(self, *args, **options):
        try:
            signal_date = date.fromisoformat(options['as_of'])
        except ValueError as exc:
            raise CommandError('--as-of must be YYYY-MM-DD') from exc
        service = FreeCashFlowYieldService()
        for symbol in options['symbols']:
            try:
                signal = service.build(Stock.objects.get(symbol=symbol.upper()), signal_date)
            except (Stock.DoesNotExist, ValueSignalUnavailable) as exc:
                raise CommandError(f'{symbol.upper()}: {exc}') from exc
            self.stdout.write(self.style.SUCCESS(
                f'{signal.stock.symbol} {signal.signal_date}: FCF yield {signal.free_cash_flow_yield:.4%}, '
                f'FCF {signal.trailing_free_cash_flow}, market cap {signal.market_cap_used}'
            ))
