from django.db import models


class Stock(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    symbol = models.CharField(max_length=5, unique=True)
    companySummary = models.TextField(null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    startingPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currentPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conservativeCompanyValuation = models.BigIntegerField(null=True, blank=True)
    marketCap = models.BigIntegerField(null=True, blank=True)
    sharesOutstanding = models.BigIntegerField(null=True, blank=True)
    priceWhenBought = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    isBought = models.BooleanField(null=True, blank=True)
    sharesOwned = models.IntegerField(null=True, blank=True)
    relativeStrengthIndex = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    yoyEPSPercentGrowth = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    compoundedAnnualGrowthRate = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    @property
    def margin_of_safety(self):
        """Calculate margin of safety: conservative valuation minus market cap
        Positive value indicates potential undervaluation"""
        if self.conservativeCompanyValuation is not None and self.marketCap is not None:
            return self.conservativeCompanyValuation - self.marketCap
        return None
    
    @property
    def margin_of_safety_percentage(self):
        """Calculate margin of safety percentage"""
        if self.conservativeCompanyValuation and self.marketCap:
            try:
                return ((self.conservativeCompanyValuation - self.marketCap) / self.conservativeCompanyValuation) * 100
            except ZeroDivisionError:
                return None
        return None

    def __str__(self):
        return f"{self.symbol}"
