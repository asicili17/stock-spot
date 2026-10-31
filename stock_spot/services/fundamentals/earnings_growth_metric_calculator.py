"""Calculations for the latest reported quarterly and annual EPS growth metrics."""

from datetime import date
from decimal import Decimal
import logging

from stock_spot.models import AnnualEarning, QuarterlyEarning, Stock


logger = logging.getLogger(__name__)


class EarningsGrowthMetricCalculator:
    """Update the display-only latest EPS-growth fields on a stock profile.

    These are intentionally separate from the point-in-time research factors.
    A historical backtest must use dated observations and availability dates.
    """

    @staticmethod
    def _one_year_earlier(value: date) -> date:
        try:
            return value.replace(year=value.year - 1)
        except ValueError:  # February 29
            return value.replace(year=value.year - 1, day=28)

    def calculate_quarterly_yoy_eps_growth(self, stock: Stock):
        latest = QuarterlyEarning.objects.filter(stock=stock).order_by('-fiscalDateEnding').first()
        if latest is None or latest.reportedEPS is None:
            return None

        target_date = self._one_year_earlier(latest.fiscalDateEnding)
        prior_candidates = QuarterlyEarning.objects.filter(stock=stock, fiscalDateEnding__year=target_date.year)
        prior = min(
            prior_candidates,
            key=lambda item: abs((item.fiscalDateEnding - target_date).days),
            default=None,
        )
        if prior is None or prior.reportedEPS in (None, Decimal('0')):
            return None

        growth_percent = (latest.reportedEPS / prior.reportedEPS - Decimal('1')) * Decimal('100')
        stock.yoyEPSPercentGrowth = growth_percent
        stock.save(update_fields=['yoyEPSPercentGrowth'])
        return growth_percent

    def calculate_annual_eps_cagr(self, stock: Stock, maximum_years: int = 4):
        """Calculate EPS CAGR over up to ``maximum_years`` elapsed calendar years."""
        observations = list(AnnualEarning.objects.filter(stock=stock).order_by('fiscalDateEnding'))
        if len(observations) < 2:
            return None

        latest = observations[-1]
        eligible = [
            item for item in observations[:-1]
            if (latest.fiscalDateEnding - item.fiscalDateEnding).days <= maximum_years * 366
        ]
        if not eligible:
            return None
        earliest = eligible[0]
        if earliest.reportedEPS is None or latest.reportedEPS is None:
            return None
        if earliest.reportedEPS <= 0 or latest.reportedEPS <= 0:
            return None

        elapsed_years = Decimal(str((latest.fiscalDateEnding - earliest.fiscalDateEnding).days / 365.25))
        if elapsed_years <= 0:
            return None
        cagr_percent = ((latest.reportedEPS / earliest.reportedEPS) ** (Decimal('1') / elapsed_years) - Decimal('1')) * Decimal('100')
        stock.compoundedAnnualGrowthRate = cagr_percent
        stock.save(update_fields=['compoundedAnnualGrowthRate'])
        return cagr_percent
