from django.db import models

from .stock import Stock


class DailyPrice(models.Model):
    """A validated end-of-day price observation returned by Alpha Vantage."""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='daily_prices')
    trading_date = models.DateField()
    source = models.CharField(max_length=32, default='alpha_vantage')
    open = models.DecimalField(max_digits=18, decimal_places=6)
    high = models.DecimalField(max_digits=18, decimal_places=6)
    low = models.DecimalField(max_digits=18, decimal_places=6)
    close = models.DecimalField(max_digits=18, decimal_places=6)
    adjusted_close = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    volume = models.BigIntegerField()
    dividend_amount = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    split_coefficient = models.DecimalField(max_digits=18, decimal_places=8, default=1)
    retrieved_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['stock', 'trading_date', 'source'],
                name='unique_daily_price_per_source',
            ),
        ]
        indexes = [
            models.Index(fields=['stock', 'trading_date'], name='daily_price_stock_date_idx'),
        ]
        ordering = ['trading_date']

    def __str__(self):
        return f'{self.stock.symbol} {self.trading_date}'


class AlphaVantageFetch(models.Model):
    """Audit trail for cached API responses, without storing API credentials."""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alpha_vantage_fetches')
    endpoint = models.CharField(max_length=64)
    fetched_at = models.DateTimeField(auto_now_add=True)
    succeeded = models.BooleanField(default=False)
    row_count = models.PositiveIntegerField(default=0)
    content_hash = models.CharField(max_length=64, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=['stock', 'endpoint', 'fetched_at'])]
        ordering = ['-fetched_at']


class FundamentalSnapshot(models.Model):
    """Immutable raw response used to audit dates and observed revisions."""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='fundamental_snapshots')
    endpoint = models.CharField(max_length=64)
    retrieved_at = models.DateTimeField(auto_now_add=True)
    content_hash = models.CharField(max_length=64)
    payload = models.JSONField()
    audit_summary = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['stock', 'endpoint', 'content_hash'],
                name='unique_fundamental_snapshot',
            ),
        ]
        ordering = ['-retrieved_at']


class ShareCountObservation(models.Model):
    """Normalized share counts, with the raw Alpha Vantage snapshot retained as provenance."""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='share_count_observations')
    observation_date = models.DateField()
    availability_date = models.DateField(null=True, blank=True)
    basic_shares = models.BigIntegerField(null=True, blank=True)
    diluted_shares = models.BigIntegerField(null=True, blank=True)
    source_snapshot = models.ForeignKey(FundamentalSnapshot, on_delete=models.CASCADE, related_name='share_counts')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['source_snapshot', 'observation_date'],
                name='unique_snapshot_share_count',
            ),
        ]
        ordering = ['observation_date']


class FreeCashFlowYieldSignal(models.Model):
    """A materialized value signal with its availability proxy and source facts."""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='fcf_yield_signals')
    signal_date = models.DateField()
    availability_date = models.DateField()
    trailing_free_cash_flow = models.DecimalField(max_digits=30, decimal_places=4)
    shares_used = models.BigIntegerField()
    raw_close_used = models.DecimalField(max_digits=18, decimal_places=6)
    market_cap_used = models.DecimalField(max_digits=30, decimal_places=4)
    free_cash_flow_yield = models.DecimalField(max_digits=18, decimal_places=10)
    availability_basis = models.CharField(max_length=96)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['stock', 'signal_date'],
                name='unique_fcf_yield_signal_date',
            ),
        ]
        ordering = ['signal_date']


class MomentumBacktestRun(models.Model):
    """An immutable result from the monthly price-momentum proof of concept."""

    created_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField()
    summary = models.JSONField()
    rebalances = models.JSONField()

    class Meta:
        ordering = ['-created_at']
