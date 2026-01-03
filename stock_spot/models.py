from django.db import models

class Stock(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    symbol = models.CharField(max_length=5, unique=True)
    companySummary = models.TextField(null=True, blank=True)
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


class QuarterlyIncomeStatement(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='quarterly_income_statements')
    fiscalDateEnding = models.DateField()
    
    # Revenue
    totalRevenue = models.BigIntegerField(null=True, blank=True)
    operatingRevenue = models.BigIntegerField(null=True, blank=True)
    costOfRevenue = models.BigIntegerField(null=True, blank=True)
    grossProfit = models.BigIntegerField(null=True, blank=True)
    
    # Operating Expenses
    operatingExpense = models.BigIntegerField(null=True, blank=True)
    researchAndDevelopment = models.BigIntegerField(null=True, blank=True)
    sellingGeneralAndAdministration = models.BigIntegerField(null=True, blank=True)
    totalExpenses = models.BigIntegerField(null=True, blank=True)
    
    # Operating Income
    operatingIncome = models.BigIntegerField(null=True, blank=True)
    totalOperatingIncomeAsReported = models.BigIntegerField(null=True, blank=True)
    
    # Interest
    interestIncome = models.BigIntegerField(null=True, blank=True)
    interestExpense = models.BigIntegerField(null=True, blank=True)
    netInterestIncome = models.BigIntegerField(null=True, blank=True)
    interestIncomeNonOperating = models.BigIntegerField(null=True, blank=True)
    interestExpenseNonOperating = models.BigIntegerField(null=True, blank=True)
    netNonOperatingInterestIncomeExpense = models.BigIntegerField(null=True, blank=True)
    
    # Other Income/Expenses
    otherIncomeExpense = models.BigIntegerField(null=True, blank=True)
    otherNonOperatingIncomeExpenses = models.BigIntegerField(null=True, blank=True)
    specialIncomeCharges = models.BigIntegerField(null=True, blank=True)
    restructuringAndMergerAcquisition = models.BigIntegerField(null=True, blank=True)
    
    # Pre-tax and Tax
    pretaxIncome = models.BigIntegerField(null=True, blank=True)
    taxProvision = models.BigIntegerField(null=True, blank=True)
    taxRateForCalcs = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    taxEffectOfUnusualItems = models.BigIntegerField(null=True, blank=True)
    
    # Net Income
    netIncome = models.BigIntegerField(null=True, blank=True)
    netIncomeContinuousOperations = models.BigIntegerField(null=True, blank=True)
    netIncomeIncludingNoncontrollingInterests = models.BigIntegerField(null=True, blank=True)
    netIncomeCommonStockholders = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingOperationNetMinorityInterest = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingAndDiscontinuedOperation = models.BigIntegerField(null=True, blank=True)
    minorityInterests = models.BigIntegerField(null=True, blank=True)
    dilutedNIAvailableToComStockholders = models.BigIntegerField(null=True, blank=True)
    
    # EPS
    basicEPS = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    dilutedEPS = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    basicAverageShares = models.BigIntegerField(null=True, blank=True)
    dilutedAverageShares = models.BigIntegerField(null=True, blank=True)
    
    # EBITDA
    ebitda = models.BigIntegerField(null=True, blank=True)
    ebit = models.BigIntegerField(null=True, blank=True)
    normalizedEBITDA = models.BigIntegerField(null=True, blank=True)
    reconciledDepreciation = models.BigIntegerField(null=True, blank=True)
    reconciledCostOfRevenue = models.BigIntegerField(null=True, blank=True)
    
    # Normalized/Unusual Items
    normalizedIncome = models.BigIntegerField(null=True, blank=True)
    totalUnusualItems = models.BigIntegerField(null=True, blank=True)
    totalUnusualItemsExcludingGoodwill = models.BigIntegerField(null=True, blank=True)
    
    # Other
    rentExpenseSupplemental = models.BigIntegerField(null=True, blank=True)
    otherUnderPreferredStockDividend = models.BigIntegerField(null=True, blank=True)
    
    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Q {self.fiscalDateEnding}"


class AnnualIncomeStatement(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='annual_income_statements')
    fiscalDateEnding = models.DateField()
    
    # Revenue
    totalRevenue = models.BigIntegerField(null=True, blank=True)
    operatingRevenue = models.BigIntegerField(null=True, blank=True)
    costOfRevenue = models.BigIntegerField(null=True, blank=True)
    grossProfit = models.BigIntegerField(null=True, blank=True)
    
    # Operating Expenses
    operatingExpense = models.BigIntegerField(null=True, blank=True)
    researchAndDevelopment = models.BigIntegerField(null=True, blank=True)
    sellingGeneralAndAdministration = models.BigIntegerField(null=True, blank=True)
    totalExpenses = models.BigIntegerField(null=True, blank=True)
    
    # Operating Income
    operatingIncome = models.BigIntegerField(null=True, blank=True)
    totalOperatingIncomeAsReported = models.BigIntegerField(null=True, blank=True)
    
    # Interest
    interestIncome = models.BigIntegerField(null=True, blank=True)
    interestExpense = models.BigIntegerField(null=True, blank=True)
    netInterestIncome = models.BigIntegerField(null=True, blank=True)
    interestIncomeNonOperating = models.BigIntegerField(null=True, blank=True)
    interestExpenseNonOperating = models.BigIntegerField(null=True, blank=True)
    netNonOperatingInterestIncomeExpense = models.BigIntegerField(null=True, blank=True)
    
    # Other Income/Expenses
    otherIncomeExpense = models.BigIntegerField(null=True, blank=True)
    otherNonOperatingIncomeExpenses = models.BigIntegerField(null=True, blank=True)
    specialIncomeCharges = models.BigIntegerField(null=True, blank=True)
    restructuringAndMergerAcquisition = models.BigIntegerField(null=True, blank=True)
    
    # Pre-tax and Tax
    pretaxIncome = models.BigIntegerField(null=True, blank=True)
    taxProvision = models.BigIntegerField(null=True, blank=True)
    taxRateForCalcs = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    taxEffectOfUnusualItems = models.BigIntegerField(null=True, blank=True)
    
    # Net Income
    netIncome = models.BigIntegerField(null=True, blank=True)
    netIncomeContinuousOperations = models.BigIntegerField(null=True, blank=True)
    netIncomeIncludingNoncontrollingInterests = models.BigIntegerField(null=True, blank=True)
    netIncomeCommonStockholders = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingOperationNetMinorityInterest = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingAndDiscontinuedOperation = models.BigIntegerField(null=True, blank=True)
    minorityInterests = models.BigIntegerField(null=True, blank=True)
    dilutedNIAvailableToComStockholders = models.BigIntegerField(null=True, blank=True)
    
    # EPS
    basicEPS = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    dilutedEPS = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    basicAverageShares = models.BigIntegerField(null=True, blank=True)
    dilutedAverageShares = models.BigIntegerField(null=True, blank=True)
    averageDilutionEarnings = models.BigIntegerField(null=True, blank=True)
    
    # EBITDA
    ebitda = models.BigIntegerField(null=True, blank=True)
    ebit = models.BigIntegerField(null=True, blank=True)
    normalizedEBITDA = models.BigIntegerField(null=True, blank=True)
    reconciledDepreciation = models.BigIntegerField(null=True, blank=True)
    reconciledCostOfRevenue = models.BigIntegerField(null=True, blank=True)
    
    # Normalized/Unusual Items
    normalizedIncome = models.BigIntegerField(null=True, blank=True)
    totalUnusualItems = models.BigIntegerField(null=True, blank=True)
    totalUnusualItemsExcludingGoodwill = models.BigIntegerField(null=True, blank=True)
    
    # Other
    rentExpenseSupplemental = models.BigIntegerField(null=True, blank=True)
    otherUnderPreferredStockDividend = models.BigIntegerField(null=True, blank=True)
    
    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Annual {self.fiscalDateEnding}"


class AnnualBalanceSheet(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='annual_balance_sheets')
    fiscalDateEnding = models.DateField()
    
    # Shares
    treasurySharesNumber = models.BigIntegerField(null=True, blank=True)
    ordinarySharesNumber = models.BigIntegerField(null=True, blank=True)
    shareIssued = models.BigIntegerField(null=True, blank=True)
    
    # Debt & Capital
    totalDebt = models.BigIntegerField(null=True, blank=True)
    tangibleBookValue = models.BigIntegerField(null=True, blank=True)
    investedCapital = models.BigIntegerField(null=True, blank=True)
    workingCapital = models.BigIntegerField(null=True, blank=True)
    netTangibleAssets = models.BigIntegerField(null=True, blank=True)
    capitalLeaseObligations = models.BigIntegerField(null=True, blank=True)
    
    # Equity
    commonStockEquity = models.BigIntegerField(null=True, blank=True)
    totalCapitalization = models.BigIntegerField(null=True, blank=True)
    totalEquityGrossMinorityInterest = models.BigIntegerField(null=True, blank=True)
    minorityInterest = models.BigIntegerField(null=True, blank=True)
    stockholdersEquity = models.BigIntegerField(null=True, blank=True)
    gainsLossesNotAffectingRetainedEarnings = models.BigIntegerField(null=True, blank=True)
    otherEquityAdjustments = models.BigIntegerField(null=True, blank=True)
    retainedEarnings = models.BigIntegerField(null=True, blank=True)
    additionalPaidInCapital = models.BigIntegerField(null=True, blank=True)
    capitalStock = models.BigIntegerField(null=True, blank=True)
    commonStock = models.BigIntegerField(null=True, blank=True)
    preferredStock = models.BigIntegerField(null=True, blank=True)
    
    # Non-Current Liabilities
    totalLiabilitiesNetMinorityInterest = models.BigIntegerField(null=True, blank=True)
    totalNonCurrentLiabilitiesNetMinorityInterest = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    preferredSecuritiesOutsideStockEquity = models.BigIntegerField(null=True, blank=True)
    nonCurrentAccruedExpenses = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredLiabilities = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredRevenue = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredTaxesLiabilities = models.BigIntegerField(null=True, blank=True)
    longTermDebtAndCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    longTermCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    longTermDebt = models.BigIntegerField(null=True, blank=True)
    longTermProvisions = models.BigIntegerField(null=True, blank=True)
    
    # Current Liabilities
    currentLiabilities = models.BigIntegerField(null=True, blank=True)
    otherCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    currentDeferredLiabilities = models.BigIntegerField(null=True, blank=True)
    currentDeferredRevenue = models.BigIntegerField(null=True, blank=True)
    currentDebtAndCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    currentCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    currentDebt = models.BigIntegerField(null=True, blank=True)
    otherCurrentBorrowings = models.BigIntegerField(null=True, blank=True)
    lineOfCredit = models.BigIntegerField(null=True, blank=True)
    currentProvisions = models.BigIntegerField(null=True, blank=True)
    
    # Payables
    payablesAndAccruedExpenses = models.BigIntegerField(null=True, blank=True)
    currentAccruedExpenses = models.BigIntegerField(null=True, blank=True)
    interestPayable = models.BigIntegerField(null=True, blank=True)
    payables = models.BigIntegerField(null=True, blank=True)
    totalTaxPayable = models.BigIntegerField(null=True, blank=True)
    accountsPayable = models.BigIntegerField(null=True, blank=True)
    
    # Total Assets
    totalAssets = models.BigIntegerField(null=True, blank=True)
    
    # Non-Current Assets
    totalNonCurrentAssets = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentAssets = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredAssets = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredTaxesAssets = models.BigIntegerField(null=True, blank=True)
    
    # Intangibles
    goodwillAndOtherIntangibleAssets = models.BigIntegerField(null=True, blank=True)
    otherIntangibleAssets = models.BigIntegerField(null=True, blank=True)
    goodwill = models.BigIntegerField(null=True, blank=True)
    
    # Property, Plant & Equipment
    netPPE = models.BigIntegerField(null=True, blank=True)
    accumulatedDepreciation = models.BigIntegerField(null=True, blank=True)
    grossPPE = models.BigIntegerField(null=True, blank=True)
    leases = models.BigIntegerField(null=True, blank=True)
    constructionInProgress = models.BigIntegerField(null=True, blank=True)
    otherProperties = models.BigIntegerField(null=True, blank=True)
    machineryFurnitureEquipment = models.BigIntegerField(null=True, blank=True)
    landAndImprovements = models.BigIntegerField(null=True, blank=True)
    properties = models.BigIntegerField(null=True, blank=True)
    
    # Current Assets
    currentAssets = models.BigIntegerField(null=True, blank=True)
    otherCurrentAssets = models.BigIntegerField(null=True, blank=True)
    prepaidAssets = models.BigIntegerField(null=True, blank=True)
    
    # Inventory
    inventory = models.BigIntegerField(null=True, blank=True)
    otherInventories = models.BigIntegerField(null=True, blank=True)
    finishedGoods = models.BigIntegerField(null=True, blank=True)
    workInProcess = models.BigIntegerField(null=True, blank=True)
    rawMaterials = models.BigIntegerField(null=True, blank=True)
    
    # Receivables
    receivables = models.BigIntegerField(null=True, blank=True)
    accountsReceivable = models.BigIntegerField(null=True, blank=True)
    
    # Cash & Investments
    cashCashEquivalentsAndShortTermInvestments = models.BigIntegerField(null=True, blank=True)
    otherShortTermInvestments = models.BigIntegerField(null=True, blank=True)
    cashAndCashEquivalents = models.BigIntegerField(null=True, blank=True)
    cashEquivalents = models.BigIntegerField(null=True, blank=True)
    cashFinancial = models.BigIntegerField(null=True, blank=True)
    
    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Annual BS {self.fiscalDateEnding}"


class QuarterlyBalanceSheet(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='quarterly_balance_sheets')
    fiscalDateEnding = models.DateField()
    
    # Shares
    treasurySharesNumber = models.BigIntegerField(null=True, blank=True)
    ordinarySharesNumber = models.BigIntegerField(null=True, blank=True)
    shareIssued = models.BigIntegerField(null=True, blank=True)
    
    # Debt & Capital
    totalDebt = models.BigIntegerField(null=True, blank=True)
    tangibleBookValue = models.BigIntegerField(null=True, blank=True)
    investedCapital = models.BigIntegerField(null=True, blank=True)
    workingCapital = models.BigIntegerField(null=True, blank=True)
    netTangibleAssets = models.BigIntegerField(null=True, blank=True)
    capitalLeaseObligations = models.BigIntegerField(null=True, blank=True)
    
    # Equity
    commonStockEquity = models.BigIntegerField(null=True, blank=True)
    totalCapitalization = models.BigIntegerField(null=True, blank=True)
    totalEquityGrossMinorityInterest = models.BigIntegerField(null=True, blank=True)
    minorityInterest = models.BigIntegerField(null=True, blank=True)
    stockholdersEquity = models.BigIntegerField(null=True, blank=True)
    gainsLossesNotAffectingRetainedEarnings = models.BigIntegerField(null=True, blank=True)
    otherEquityAdjustments = models.BigIntegerField(null=True, blank=True)
    retainedEarnings = models.BigIntegerField(null=True, blank=True)
    additionalPaidInCapital = models.BigIntegerField(null=True, blank=True)
    capitalStock = models.BigIntegerField(null=True, blank=True)
    commonStock = models.BigIntegerField(null=True, blank=True)
    preferredStock = models.BigIntegerField(null=True, blank=True)
    
    # Non-Current Liabilities
    totalLiabilitiesNetMinorityInterest = models.BigIntegerField(null=True, blank=True)
    totalNonCurrentLiabilitiesNetMinorityInterest = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredLiabilities = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredRevenue = models.BigIntegerField(null=True, blank=True)
    longTermDebtAndCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    longTermCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    longTermDebt = models.BigIntegerField(null=True, blank=True)
    longTermProvisions = models.BigIntegerField(null=True, blank=True)
    
    # Current Liabilities
    currentLiabilities = models.BigIntegerField(null=True, blank=True)
    otherCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    currentDeferredLiabilities = models.BigIntegerField(null=True, blank=True)
    currentDeferredRevenue = models.BigIntegerField(null=True, blank=True)
    currentDebtAndCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    currentCapitalLeaseObligation = models.BigIntegerField(null=True, blank=True)
    currentDebt = models.BigIntegerField(null=True, blank=True)
    otherCurrentBorrowings = models.BigIntegerField(null=True, blank=True)
    lineOfCredit = models.BigIntegerField(null=True, blank=True)
    currentProvisions = models.BigIntegerField(null=True, blank=True)
    
    # Payables
    payablesAndAccruedExpenses = models.BigIntegerField(null=True, blank=True)
    currentAccruedExpenses = models.BigIntegerField(null=True, blank=True)
    payables = models.BigIntegerField(null=True, blank=True)
    totalTaxPayable = models.BigIntegerField(null=True, blank=True)
    accountsPayable = models.BigIntegerField(null=True, blank=True)
    
    # Total Assets
    totalAssets = models.BigIntegerField(null=True, blank=True)
    
    # Non-Current Assets
    totalNonCurrentAssets = models.BigIntegerField(null=True, blank=True)
    otherNonCurrentAssets = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredAssets = models.BigIntegerField(null=True, blank=True)
    nonCurrentDeferredTaxesAssets = models.BigIntegerField(null=True, blank=True)
    
    # Investments
    investmentsAndAdvances = models.BigIntegerField(null=True, blank=True)
    otherInvestments = models.BigIntegerField(null=True, blank=True)
    
    # Intangibles
    goodwillAndOtherIntangibleAssets = models.BigIntegerField(null=True, blank=True)
    otherIntangibleAssets = models.BigIntegerField(null=True, blank=True)
    goodwill = models.BigIntegerField(null=True, blank=True)
    
    # Property, Plant & Equipment
    netPPE = models.BigIntegerField(null=True, blank=True)
    accumulatedDepreciation = models.BigIntegerField(null=True, blank=True)
    grossPPE = models.BigIntegerField(null=True, blank=True)
    leases = models.BigIntegerField(null=True, blank=True)
    constructionInProgress = models.BigIntegerField(null=True, blank=True)
    otherProperties = models.BigIntegerField(null=True, blank=True)
    machineryFurnitureEquipment = models.BigIntegerField(null=True, blank=True)
    landAndImprovements = models.BigIntegerField(null=True, blank=True)
    properties = models.BigIntegerField(null=True, blank=True)
    
    # Current Assets
    currentAssets = models.BigIntegerField(null=True, blank=True)
    otherCurrentAssets = models.BigIntegerField(null=True, blank=True)
    
    # Inventory
    inventory = models.BigIntegerField(null=True, blank=True)
    otherInventories = models.BigIntegerField(null=True, blank=True)
    finishedGoods = models.BigIntegerField(null=True, blank=True)
    workInProcess = models.BigIntegerField(null=True, blank=True)
    rawMaterials = models.BigIntegerField(null=True, blank=True)
    
    # Receivables
    receivables = models.BigIntegerField(null=True, blank=True)
    accountsReceivable = models.BigIntegerField(null=True, blank=True)
    
    # Cash & Investments
    cashCashEquivalentsAndShortTermInvestments = models.BigIntegerField(null=True, blank=True)
    otherShortTermInvestments = models.BigIntegerField(null=True, blank=True)
    cashAndCashEquivalents = models.BigIntegerField(null=True, blank=True)
    cashEquivalents = models.BigIntegerField(null=True, blank=True)
    cashFinancial = models.BigIntegerField(null=True, blank=True)
    
    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Q BS {self.fiscalDateEnding}"


class QuarterlyCashFlow(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='quarterly_cash_flows')
    fiscalDateEnding = models.DateField()
    
    # Summary
    freeCashFlow = models.BigIntegerField(null=True, blank=True)
    capitalExpenditure = models.BigIntegerField(null=True, blank=True)
    
    # Cash Position
    endCashPosition = models.BigIntegerField(null=True, blank=True)
    beginningCashPosition = models.BigIntegerField(null=True, blank=True)
    effectOfExchangeRateChanges = models.BigIntegerField(null=True, blank=True)
    changesInCash = models.BigIntegerField(null=True, blank=True)
    
    # Financing Activities
    financingCashFlow = models.BigIntegerField(null=True, blank=True)
    cashFlowFromContinuingFinancingActivities = models.BigIntegerField(null=True, blank=True)
    netOtherFinancingCharges = models.BigIntegerField(null=True, blank=True)
    proceedsFromStockOptionExercised = models.BigIntegerField(null=True, blank=True)
    netIssuancePaymentsOfDebt = models.BigIntegerField(null=True, blank=True)
    netLongTermDebtIssuance = models.BigIntegerField(null=True, blank=True)
    longTermDebtPayments = models.BigIntegerField(null=True, blank=True)
    longTermDebtIssuance = models.BigIntegerField(null=True, blank=True)
    repaymentOfDebt = models.BigIntegerField(null=True, blank=True)
    issuanceOfDebt = models.BigIntegerField(null=True, blank=True)
    
    # Investing Activities
    investingCashFlow = models.BigIntegerField(null=True, blank=True)
    cashFlowFromContinuingInvestingActivities = models.BigIntegerField(null=True, blank=True)
    netInvestmentPurchaseAndSale = models.BigIntegerField(null=True, blank=True)
    saleOfInvestment = models.BigIntegerField(null=True, blank=True)
    purchaseOfInvestment = models.BigIntegerField(null=True, blank=True)
    netBusinessPurchaseAndSale = models.BigIntegerField(null=True, blank=True)
    netPPEPurchaseAndSale = models.BigIntegerField(null=True, blank=True)
    purchaseOfPPE = models.BigIntegerField(null=True, blank=True)
    
    # Operating Activities
    operatingCashFlow = models.BigIntegerField(null=True, blank=True)
    cashFlowFromContinuingOperatingActivities = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingOperations = models.BigIntegerField(null=True, blank=True)
    
    # Working Capital Changes
    changeInWorkingCapital = models.BigIntegerField(null=True, blank=True)
    changeInOtherWorkingCapital = models.BigIntegerField(null=True, blank=True)
    changeInOtherCurrentAssets = models.BigIntegerField(null=True, blank=True)
    changeInPayablesAndAccruedExpense = models.BigIntegerField(null=True, blank=True)
    changeInPrepaidAssets = models.BigIntegerField(null=True, blank=True)
    changeInInventory = models.BigIntegerField(null=True, blank=True)
    changeInReceivables = models.BigIntegerField(null=True, blank=True)
    changesInAccountReceivables = models.BigIntegerField(null=True, blank=True)
    
    # Non-Cash Items
    otherNonCashItems = models.BigIntegerField(null=True, blank=True)
    stockBasedCompensation = models.BigIntegerField(null=True, blank=True)
    assetImpairmentCharge = models.BigIntegerField(null=True, blank=True)
    deferredTax = models.BigIntegerField(null=True, blank=True)
    deferredIncomeTax = models.BigIntegerField(null=True, blank=True)
    
    # Depreciation & Amortization
    depreciationAmortizationDepletion = models.BigIntegerField(null=True, blank=True)
    depreciationAndAmortization = models.BigIntegerField(null=True, blank=True)
    depreciation = models.BigIntegerField(null=True, blank=True)
    
    # Gains & Losses
    operatingGainsLosses = models.BigIntegerField(null=True, blank=True)
    netForeignCurrencyExchangeGainLoss = models.BigIntegerField(null=True, blank=True)
    gainLossOnSaleOfPPE = models.BigIntegerField(null=True, blank=True)
    
    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Q CF {self.fiscalDateEnding}"


class AnnualCashFlow(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='annual_cash_flows')
    fiscalDateEnding = models.DateField()
    
    # Summary
    freeCashFlow = models.BigIntegerField(null=True, blank=True)
    capitalExpenditure = models.BigIntegerField(null=True, blank=True)
    
    # Supplemental Data
    interestPaidSupplementalData = models.BigIntegerField(null=True, blank=True)
    incomeTaxPaidSupplementalData = models.BigIntegerField(null=True, blank=True)
    
    # Cash Position
    endCashPosition = models.BigIntegerField(null=True, blank=True)
    beginningCashPosition = models.BigIntegerField(null=True, blank=True)
    effectOfExchangeRateChanges = models.BigIntegerField(null=True, blank=True)
    changesInCash = models.BigIntegerField(null=True, blank=True)
    
    # Financing Activities
    financingCashFlow = models.BigIntegerField(null=True, blank=True)
    cashFlowFromContinuingFinancingActivities = models.BigIntegerField(null=True, blank=True)
    netOtherFinancingCharges = models.BigIntegerField(null=True, blank=True)
    proceedsFromStockOptionExercised = models.BigIntegerField(null=True, blank=True)
    netCommonStockIssuance = models.BigIntegerField(null=True, blank=True)
    commonStockIssuance = models.BigIntegerField(null=True, blank=True)
    issuanceOfCapitalStock = models.BigIntegerField(null=True, blank=True)
    netIssuancePaymentsOfDebt = models.BigIntegerField(null=True, blank=True)
    netLongTermDebtIssuance = models.BigIntegerField(null=True, blank=True)
    longTermDebtPayments = models.BigIntegerField(null=True, blank=True)
    longTermDebtIssuance = models.BigIntegerField(null=True, blank=True)
    repaymentOfDebt = models.BigIntegerField(null=True, blank=True)
    issuanceOfDebt = models.BigIntegerField(null=True, blank=True)
    
    # Investing Activities
    investingCashFlow = models.BigIntegerField(null=True, blank=True)
    cashFlowFromContinuingInvestingActivities = models.BigIntegerField(null=True, blank=True)
    netOtherInvestingChanges = models.BigIntegerField(null=True, blank=True)
    netInvestmentPurchaseAndSale = models.BigIntegerField(null=True, blank=True)
    saleOfInvestment = models.BigIntegerField(null=True, blank=True)
    purchaseOfInvestment = models.BigIntegerField(null=True, blank=True)
    netBusinessPurchaseAndSale = models.BigIntegerField(null=True, blank=True)
    saleOfBusiness = models.BigIntegerField(null=True, blank=True)
    purchaseOfBusiness = models.BigIntegerField(null=True, blank=True)
    netIntangiblesPurchaseAndSale = models.BigIntegerField(null=True, blank=True)
    saleOfIntangibles = models.BigIntegerField(null=True, blank=True)
    purchaseOfIntangibles = models.BigIntegerField(null=True, blank=True)
    netPPEPurchaseAndSale = models.BigIntegerField(null=True, blank=True)
    purchaseOfPPE = models.BigIntegerField(null=True, blank=True)
    
    # Operating Activities
    operatingCashFlow = models.BigIntegerField(null=True, blank=True)
    cashFlowFromContinuingOperatingActivities = models.BigIntegerField(null=True, blank=True)
    netIncomeFromContinuingOperations = models.BigIntegerField(null=True, blank=True)
    
    # Working Capital Changes
    changeInWorkingCapital = models.BigIntegerField(null=True, blank=True)
    changeInOtherWorkingCapital = models.BigIntegerField(null=True, blank=True)
    changeInOtherCurrentLiabilities = models.BigIntegerField(null=True, blank=True)
    changeInOtherCurrentAssets = models.BigIntegerField(null=True, blank=True)
    changeInPayablesAndAccruedExpense = models.BigIntegerField(null=True, blank=True)
    changeInPayable = models.BigIntegerField(null=True, blank=True)
    changeInAccountPayable = models.BigIntegerField(null=True, blank=True)
    changeInPrepaidAssets = models.BigIntegerField(null=True, blank=True)
    changeInInventory = models.BigIntegerField(null=True, blank=True)
    changeInReceivables = models.BigIntegerField(null=True, blank=True)
    changesInAccountReceivables = models.BigIntegerField(null=True, blank=True)
    
    # Non-Cash Items
    otherNonCashItems = models.BigIntegerField(null=True, blank=True)
    stockBasedCompensation = models.BigIntegerField(null=True, blank=True)
    assetImpairmentCharge = models.BigIntegerField(null=True, blank=True)
    deferredTax = models.BigIntegerField(null=True, blank=True)
    deferredIncomeTax = models.BigIntegerField(null=True, blank=True)
    
    # Depreciation & Amortization
    depreciationAmortizationDepletion = models.BigIntegerField(null=True, blank=True)
    depreciationAndAmortization = models.BigIntegerField(null=True, blank=True)
    depreciation = models.BigIntegerField(null=True, blank=True)
    
    # Gains & Losses
    operatingGainsLosses = models.BigIntegerField(null=True, blank=True)
    netForeignCurrencyExchangeGainLoss = models.BigIntegerField(null=True, blank=True)
    gainLossOnSaleOfPPE = models.BigIntegerField(null=True, blank=True)
    
    lastUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['stock', 'fiscalDateEnding']

    def __str__(self):
        return f"{self.stock.symbol} - Annual CF {self.fiscalDateEnding}"