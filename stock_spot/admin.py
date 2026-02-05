from django.contrib import admin
from .models import (
    Stock, AnnualEarning, QuarterlyEarning,
    # Alpha Vantage financial statements
    QuarterlyIncomeStatement, AnnualIncomeStatement,
    QuarterlyBalanceSheet, AnnualBalanceSheet,
    QuarterlyCashFlow, AnnualCashFlow,
    # YFinance financial statements
    YFQuarterlyIncomeStatement, YFAnnualIncomeStatement,
    YFQuarterlyBalanceSheet, YFAnnualBalanceSheet,
    YFQuarterlyCashFlow, YFAnnualCashFlow
)

admin.site.register(Stock)
admin.site.register(AnnualEarning)
admin.site.register(QuarterlyEarning)
# Alpha Vantage
admin.site.register(QuarterlyIncomeStatement)
admin.site.register(AnnualIncomeStatement)
admin.site.register(QuarterlyBalanceSheet)
admin.site.register(AnnualBalanceSheet)
admin.site.register(QuarterlyCashFlow)
admin.site.register(AnnualCashFlow)
# YFinance
admin.site.register(YFQuarterlyIncomeStatement)
admin.site.register(YFAnnualIncomeStatement)
admin.site.register(YFQuarterlyBalanceSheet)
admin.site.register(YFAnnualBalanceSheet)
admin.site.register(YFQuarterlyCashFlow)
admin.site.register(YFAnnualCashFlow)
