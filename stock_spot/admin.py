from django.contrib import admin
from .models import (
    Stock, AnnualEarning, QuarterlyEarning,
    QuarterlyIncomeStatement, AnnualIncomeStatement,
    QuarterlyBalanceSheet, AnnualBalanceSheet,
    QuarterlyCashFlow, AnnualCashFlow
)

admin.site.register(Stock)
# admin.site.register(AnnualEarning)
# admin.site.register(QuarterlyEarning)
admin.site.register(QuarterlyIncomeStatement)
admin.site.register(AnnualIncomeStatement)
admin.site.register(QuarterlyBalanceSheet)
admin.site.register(AnnualBalanceSheet)
admin.site.register(QuarterlyCashFlow)
admin.site.register(AnnualCashFlow)
