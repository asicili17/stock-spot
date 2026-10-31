from django.core.management.base import BaseCommand, CommandError

from stock_spot.services.market_data import DailyPriceCacheService


class Command(BaseCommand):
    help = 'Fetch, validate, and cache Alpha Vantage daily prices for one or more symbols.'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='+', help='Ticker symbols, e.g. AAPL MSFT')
        parser.add_argument(
            '--adjusted', action='store_true',
            help='Use TIME_SERIES_DAILY_ADJUSTED. This requires the appropriate Alpha Vantage entitlement.',
        )
        parser.add_argument(
            '--monthly-adjusted', action='store_true',
            help='Cache monthly adjusted bars. This is useful for the no-premium-key momentum POC.',
        )

    def handle(self, *args, **options):
        if options['adjusted'] and options['monthly_adjusted']:
            raise CommandError('--adjusted and --monthly-adjusted cannot be used together')
        service = DailyPriceCacheService()
        for symbol in options['symbols']:
            try:
                result = service.refresh(
                    symbol,
                    adjusted=options['adjusted'] or options['monthly_adjusted'],
                    monthly=options['monthly_adjusted'],
                )
            except Exception as exc:
                raise CommandError(f'{symbol.upper()}: {exc}') from exc
            self.stdout.write(self.style.SUCCESS(
                f"{result['symbol']}: cached {result['cached']} rows from {result['endpoint']}; "
                f"rejected {len(result['rejected'])} rows"
            ))
