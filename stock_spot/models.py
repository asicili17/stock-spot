from django.db import models

class Stock(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    symbol = models.CharField(max_length=5, unique=True)
    startingPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currentPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    priceWhenBought = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    isBought = models.BooleanField(null=True, blank=True)
    sharesOwned = models.IntegerField(null=True, blank=True)
    relativeStrengthIndex = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    yoyEPSPercentGrowth = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    compoundedAnnualGrowthRate = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.symbol}"


class AnnualEarning(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='annual_earnings')
    fiscalDateEnding = models.DateField()
    reportedEPS = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    lastUpdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.symbol} - {self.fiscalDateEnding}"


class QuarterlyEarning(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='quarterly_earnings')
    fiscalDateEnding = models.DateField()
    reportedDate = models.DateField()
    reportedEPS = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    estimatedEPS = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    surprise = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    surprisePercentage = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    reportTime = models.CharField(max_length=10)
    lastUpdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.symbol} - {self.fiscalDateEnding}"