from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from stock_spot.models import Stock
from stock_spot.services.market_data import MonthlyMomentumBacktester


class Command(BaseCommand):
    help = 'Run and persist the monthly 12-1 price-momentum proof-of-concept backtest.'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='*', help='Optional cached ticker symbols; default is every cached stock.')
        parser.add_argument('--top-n', type=int, default=20)
        parser.add_argument('--cost-bps', type=Decimal, default=Decimal('0'))
        parser.add_argument('--require-adjusted', action='store_true')
        parser.add_argument(
            '--value-weight', type=Decimal, default=Decimal('0'),
            help='Weight for FCF-yield rank from 0 (momentum only) to 1 (value only).',
        )

    def handle(self, *args, **options):
        stocks = Stock.objects.filter(symbol__in=[symbol.upper() for symbol in options['symbols']]) if options['symbols'] else None
        try:
            run = MonthlyMomentumBacktester(stocks).run(
                top_n=options['top_n'],
                cost_bps=options['cost_bps'],
                require_adjusted=options['require_adjusted'],
                value_weight=options['value_weight'],
            )
        except (ValueError, ArithmeticError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(
            f"Run {run.id}: total return {run.summary['total_return']}, annualized "
            f"{run.summary['annualized_return']}, max drawdown {run.summary['max_drawdown']}, "
            f"{run.summary['rebalance_count']} monthly rebalances."
        ))
