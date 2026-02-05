from django.db import models

from .stock import Stock


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


class AnnualBalanceSheet(models.Model):
    """Alpha Vantage Annual Balance Sheet"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='av_annual_balance_sheets')
    fiscalDateEnding = models.DateField()
    reportedCurrency = models.CharField(max_length=10, default='USD')

    # Assets
    totalAssets = models.BigIntegerField(null=True, blank=True)
    totalCurrentAssets = models.BigIntegerField(null=True, blank=True)
    cashAndCashEquivalentsAtCarryingValue = models.BigIntegerField(null=True, blank=True)
    cashAndShortTermInvestments = models.BigIntegerField(null=True, blank=True)
    inventory = models.BigIntegerField(null=True, blank=True)
    currentNetReceivables = models.BigIntegerField(null=True, blank=True)
    totalNonCurrentAssets = models.BigIntegerField(null=True, blank=True)
    propertyPlantEquipment = models.BigIntegerField(null=True, blank=True)
    accumulatedDepreciationAmortizationPPE = models.BigIntegerField(null=True, blank=True)
    intangibleAssets = models.BigIntegerField(null=True, blank=True)
    intangibleAssetsExcludingGoodwill = models.BigIntegerField(null=True, blank=True)
    goodwill = models.BigIntegerField(null=True, blank=True)
    investments = models.BigIntegerField(null=True, blank=True)
    longTermInvestments = models.BigIntegerField(null=True, blank=True)
    shortTermInvestments = models.BigIntegerField(null=True, blank=True)
    otherCurrentAssets = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentAssets = models.BigIntegerField(null=True, blank=True)

    # Liabilities
    totalLiabilities = models.BigIntegerField(null=True, blank=True)
    totalCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    currentAccountsPayable = models.BigIntegerField(null=True, blank=True)
    deferredRevenue = models.BigIntegerField(null=True, blank=True)
    currentDebt = models.BigIntegerField(null=True, blank=True)
    shortTermDebt = models.BigIntegerField(null=True, blank=True)
    totalNonCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    capitalLeaseObligations = models.BigIntegerField(null=True, blank=True)
    longTermDebt = models.BigIntegerField(null=True, blank=True)
    currentLongTermDebt = models.BigIntegerField(null=True, blank=True)
    longTermDebtNoncurrent = models.BigIntegerField(null=True, blank=True)
    shortLongTermDebtTotal = models.BigIntegerField(null=True, blank=True)
    otherCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentLiabilities = models.BigIntegerField(null=True, blank=True)

    # Equity
    totalShareholderEquity = models.BigIntegerField(null=True, blank=True)
    treasuryStock = models.BigIntegerField(null=True, blank=True)
    retainedEarnings = models.BigIntegerField(null=True, blank=True)
    commonStock = models.BigIntegerField(null=True, blank=True)
    commonStockSharesOutstanding = models.BigIntegerField(null=True, blank=True)

    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Annual BS {self.fiscalDateEnding}"


class QuarterlyBalanceSheet(models.Model):
    """Alpha Vantage Quarterly Balance Sheet"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='av_quarterly_balance_sheets')
    fiscalDateEnding = models.DateField()
    reportedCurrency = models.CharField(max_length=10, default='USD')

    # Assets
    totalAssets = models.BigIntegerField(null=True, blank=True)
    totalCurrentAssets = models.BigIntegerField(null=True, blank=True)
    cashAndCashEquivalentsAtCarryingValue = models.BigIntegerField(null=True, blank=True)
    cashAndShortTermInvestments = models.BigIntegerField(null=True, blank=True)
    inventory = models.BigIntegerField(null=True, blank=True)
    currentNetReceivables = models.BigIntegerField(null=True, blank=True)
    totalNonCurrentAssets = models.BigIntegerField(null=True, blank=True)
    propertyPlantEquipment = models.BigIntegerField(null=True, blank=True)
    accumulatedDepreciationAmortizationPPE = models.BigIntegerField(null=True, blank=True)
    intangibleAssets = models.BigIntegerField(null=True, blank=True)
    intangibleAssetsExcludingGoodwill = models.BigIntegerField(null=True, blank=True)
    goodwill = models.BigIntegerField(null=True, blank=True)
    investments = models.BigIntegerField(null=True, blank=True)
    longTermInvestments = models.BigIntegerField(null=True, blank=True)
    shortTermInvestments = models.BigIntegerField(null=True, blank=True)
    otherCurrentAssets = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentAssets = models.BigIntegerField(null=True, blank=True)

    # Liabilities
    totalLiabilities = models.BigIntegerField(null=True, blank=True)
    totalCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    currentAccountsPayable = models.BigIntegerField(null=True, blank=True)
    deferredRevenue = models.BigIntegerField(null=True, blank=True)
    currentDebt = models.BigIntegerField(null=True, blank=True)
    shortTermDebt = models.BigIntegerField(null=True, blank=True)
    totalNonCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    capitalLeaseObligations = models.BigIntegerField(null=True, blank=True)
    longTermDebt = models.BigIntegerField(null=True, blank=True)
    currentLongTermDebt = models.BigIntegerField(null=True, blank=True)
    longTermDebtNoncurrent = models.BigIntegerField(null=True, blank=True)
    shortLongTermDebtTotal = models.BigIntegerField(null=True, blank=True)
    otherCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentLiabilities = models.BigIntegerField(null=True, blank=True)

    # Equity
    totalShareholderEquity = models.BigIntegerField(null=True, blank=True)
    treasuryStock = models.BigIntegerField(null=True, blank=True)
    retainedEarnings = models.BigIntegerField(null=True, blank=True)
    commonStock = models.BigIntegerField(null=True, blank=True)
    commonStockSharesOutstanding = models.BigIntegerField(null=True, blank=True)

    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Q BS {self.fiscalDateEnding}"


class AnnualIncomeStatement(models.Model):
    """Alpha Vantage Annual Income Statement"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='av_annual_income_statements')
    fiscalDateEnding = models.DateField()
    reportedCurrency = models.CharField(max_length=10, default='USD')

    # Revenue & Cost
    grossProfit = models.BigIntegerField(null=True, blank=True)
    totalRevenue = models.BigIntegerField(null=True, blank=True)
    costOfRevenue = models.BigIntegerField(null=True, blank=True)
    costofGoodsAndServicesSold = models.BigIntegerField(null=True, blank=True)

    # Operating
    operatingIncome = models.BigIntegerField(null=True, blank=True)
    sellingGeneralAndAdministrative = models.BigIntegerField(null=True, blank=True)
    researchAndDevelopment = models.BigIntegerField(null=True, blank=True)
    operatingExpenses = models.BigIntegerField(null=True, blank=True)

    # Interest & Investment
    investmentIncomeNet = models.BigIntegerField(null=True, blank=True)
    netInterestIncome = models.BigIntegerField(null=True, blank=True)
    interestIncome = models.BigIntegerField(null=True, blank=True)
    interestExpense = models.BigIntegerField(null=True, blank=True)
    nonInterestIncome = models.BigIntegerField(null=True, blank=True)
    otherNonOperatingIncome = models.BigIntegerField(null=True, blank=True)
    interestAndDebtExpense = models.BigIntegerField(null=True, blank=True)

    # Depreciation
    depreciation = models.BigIntegerField(null=True, blank=True)
    depreciationAndAmortization = models.BigIntegerField(null=True, blank=True)

    # Income & Tax
    incomeBeforeTax = models.BigIntegerField(null=True, blank=True)
    incomeTaxExpense = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingOperations = models.BigIntegerField(null=True, blank=True)
    comprehensiveIncomeNetOfTax = models.BigIntegerField(null=True, blank=True)

    # EBIT/EBITDA
    ebit = models.BigIntegerField(null=True, blank=True)
    ebitda = models.BigIntegerField(null=True, blank=True)

    # Net Income
    netIncome = models.BigIntegerField(null=True, blank=True)

    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Annual IS {self.fiscalDateEnding}"


class QuarterlyIncomeStatement(models.Model):
    """Alpha Vantage Quarterly Income Statement"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='av_quarterly_income_statements')
    fiscalDateEnding = models.DateField()
    reportedCurrency = models.CharField(max_length=10, default='USD')

    # Revenue & Cost
    grossProfit = models.BigIntegerField(null=True, blank=True)
    totalRevenue = models.BigIntegerField(null=True, blank=True)
    costOfRevenue = models.BigIntegerField(null=True, blank=True)
    costofGoodsAndServicesSold = models.BigIntegerField(null=True, blank=True)

    # Operating
    operatingIncome = models.BigIntegerField(null=True, blank=True)
    sellingGeneralAndAdministrative = models.BigIntegerField(null=True, blank=True)
    researchAndDevelopment = models.BigIntegerField(null=True, blank=True)
    operatingExpenses = models.BigIntegerField(null=True, blank=True)

    # Interest & Investment
    investmentIncomeNet = models.BigIntegerField(null=True, blank=True)
    netInterestIncome = models.BigIntegerField(null=True, blank=True)
    interestIncome = models.BigIntegerField(null=True, blank=True)
    interestExpense = models.BigIntegerField(null=True, blank=True)
    nonInterestIncome = models.BigIntegerField(null=True, blank=True)
    otherNonOperatingIncome = models.BigIntegerField(null=True, blank=True)
    interestAndDebtExpense = models.BigIntegerField(null=True, blank=True)

    # Depreciation
    depreciation = models.BigIntegerField(null=True, blank=True)
    depreciationAndAmortization = models.BigIntegerField(null=True, blank=True)

    # Income & Tax
    incomeBeforeTax = models.BigIntegerField(null=True, blank=True)
    incomeTaxExpense = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingOperations = models.BigIntegerField(null=True, blank=True)
    comprehensiveIncomeNetOfTax = models.BigIntegerField(null=True, blank=True)

    # EBIT/EBITDA
    ebit = models.BigIntegerField(null=True, blank=True)
    ebitda = models.BigIntegerField(null=True, blank=True)

    # Net Income
    netIncome = models.BigIntegerField(null=True, blank=True)

    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Q IS {self.fiscalDateEnding}"


class AnnualCashFlow(models.Model):
    """Alpha Vantage Annual Cash Flow"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='av_annual_cash_flows')
    fiscalDateEnding = models.DateField()
    reportedCurrency = models.CharField(max_length=10, default='USD')

    # Operating Activities
    operatingCashflow = models.BigIntegerField(null=True, blank=True)
    paymentsForOperatingActivities = models.BigIntegerField(null=True, blank=True)
    proceedsFromOperatingActivities = models.BigIntegerField(null=True, blank=True)
    changeInOperatingLiabilities = models.BigIntegerField(null=True, blank=True)
    changeInOperatingAssets = models.BigIntegerField(null=True, blank=True)
    depreciationDepletionAndAmortization = models.BigIntegerField(null=True, blank=True)
    changeInReceivables = models.BigIntegerField(null=True, blank=True)
    changeInInventory = models.BigIntegerField(null=True, blank=True)
    profitLoss = models.BigIntegerField(null=True, blank=True)

    # Investing Activities
    capitalExpenditures = models.BigIntegerField(null=True, blank=True)
    cashflowFromInvestment = models.BigIntegerField(null=True, blank=True)

    # Financing Activities
    cashflowFromFinancing = models.BigIntegerField(null=True, blank=True)
    proceedsFromRepaymentsOfShortTermDebt = models.BigIntegerField(null=True, blank=True)
    paymentsForRepurchaseOfCommonStock = models.BigIntegerField(null=True, blank=True)
    paymentsForRepurchaseOfEquity = models.BigIntegerField(null=True, blank=True)
    paymentsForRepurchaseOfPreferredStock = models.BigIntegerField(null=True, blank=True)
    dividendPayout = models.BigIntegerField(null=True, blank=True)
    dividendPayoutCommonStock = models.BigIntegerField(null=True, blank=True)
    dividendPayoutPreferredStock = models.BigIntegerField(null=True, blank=True)
    proceedsFromIssuanceOfCommonStock = models.BigIntegerField(null=True, blank=True)
    proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet = models.BigIntegerField(null=True, blank=True)
    proceedsFromIssuanceOfPreferredStock = models.BigIntegerField(null=True, blank=True)
    proceedsFromRepurchaseOfEquity = models.BigIntegerField(null=True, blank=True)
    proceedsFromSaleOfTreasuryStock = models.BigIntegerField(null=True, blank=True)

    # Cash Changes
    changeInCashAndCashEquivalents = models.BigIntegerField(null=True, blank=True)
    changeInExchangeRate = models.BigIntegerField(null=True, blank=True)

    # Net Income
    netIncome = models.BigIntegerField(null=True, blank=True)

    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Annual CF {self.fiscalDateEnding}"


class QuarterlyCashFlow(models.Model):
    """Alpha Vantage Quarterly Cash Flow"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='av_quarterly_cash_flows')
    fiscalDateEnding = models.DateField()
    reportedCurrency = models.CharField(max_length=10, default='USD')

    # Operating Activities
    operatingCashflow = models.BigIntegerField(null=True, blank=True)
    paymentsForOperatingActivities = models.BigIntegerField(null=True, blank=True)
    proceedsFromOperatingActivities = models.BigIntegerField(null=True, blank=True)
    changeInOperatingLiabilities = models.BigIntegerField(null=True, blank=True)
    changeInOperatingAssets = models.BigIntegerField(null=True, blank=True)
    depreciationDepletionAndAmortization = models.BigIntegerField(null=True, blank=True)
    changeInReceivables = models.BigIntegerField(null=True, blank=True)
    changeInInventory = models.BigIntegerField(null=True, blank=True)
    profitLoss = models.BigIntegerField(null=True, blank=True)

    # Investing Activities
    capitalExpenditures = models.BigIntegerField(null=True, blank=True)
    cashflowFromInvestment = models.BigIntegerField(null=True, blank=True)

    # Financing Activities
    cashflowFromFinancing = models.BigIntegerField(null=True, blank=True)
    proceedsFromRepaymentsOfShortTermDebt = models.BigIntegerField(null=True, blank=True)
    paymentsForRepurchaseOfCommonStock = models.BigIntegerField(null=True, blank=True)
    paymentsForRepurchaseOfEquity = models.BigIntegerField(null=True, blank=True)
    paymentsForRepurchaseOfPreferredStock = models.BigIntegerField(null=True, blank=True)
    dividendPayout = models.BigIntegerField(null=True, blank=True)
    dividendPayoutCommonStock = models.BigIntegerField(null=True, blank=True)
    dividendPayoutPreferredStock = models.BigIntegerField(null=True, blank=True)
    proceedsFromIssuanceOfCommonStock = models.BigIntegerField(null=True, blank=True)
    proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet = models.BigIntegerField(null=True, blank=True)
    proceedsFromIssuanceOfPreferredStock = models.BigIntegerField(null=True, blank=True)
    proceedsFromRepurchaseOfEquity = models.BigIntegerField(null=True, blank=True)
    proceedsFromSaleOfTreasuryStock = models.BigIntegerField(null=True, blank=True)

    # Cash Changes
    changeInCashAndCashEquivalents = models.BigIntegerField(null=True, blank=True)
    changeInExchangeRate = models.BigIntegerField(null=True, blank=True)

    # Net Income
    netIncome = models.BigIntegerField(null=True, blank=True)

    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Q CF {self.fiscalDateEnding}"
