from django.db import models

class Stock(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=4)
    startingPrice = models.DecimalField(max_digits=10, decimal_places=2)
    priceWhenBought = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    isBought = models.BooleanField()
    sharesOwned = models.IntegerField()

    def __str__(self):
        return f"{self.symbol} - {self.name}"


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