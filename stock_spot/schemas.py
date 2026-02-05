from dataclasses import dataclass
from typing import Optional


@dataclass
class AnnualEarningsData:
    fiscalDateEnding: str
    reportedEPS: Optional[float]


@dataclass
class QuarterlyEarningsData:
    fiscalDateEnding: str
    reportedDate: str
    reportedEPS: Optional[float]
    estimatedEPS: Optional[float]
    surprise: Optional[float]
    surprisePercentage: Optional[float]
    reportTime: str


@dataclass
class EarningsData:
    symbol: str
    annualEarnings: list[AnnualEarningsData]
    quarterlyEarnings: list[QuarterlyEarningsData]


@dataclass
class QuarterlyIncomeStatementData:
    fiscalDateEnding: str
    reportedCurrency: str
    # Revenue & Cost
    grossProfit: Optional[int]
    totalRevenue: Optional[int]
    costOfRevenue: Optional[int]
    costofGoodsAndServicesSold: Optional[int]
    # Operating
    operatingIncome: Optional[int]
    sellingGeneralAndAdministrative: Optional[int]
    researchAndDevelopment: Optional[int]
    operatingExpenses: Optional[int]
    # Interest & Investment
    investmentIncomeNet: Optional[int]
    netInterestIncome: Optional[int]
    interestIncome: Optional[int]
    interestExpense: Optional[int]
    nonInterestIncome: Optional[int]
    otherNonOperatingIncome: Optional[int]
    interestAndDebtExpense: Optional[int]
    # Depreciation
    depreciation: Optional[int]
    depreciationAndAmortization: Optional[int]
    # Income & Tax
    incomeBeforeTax: Optional[int]
    incomeTaxExpense: Optional[int]
    netIncomeFromContinuingOperations: Optional[int]
    comprehensiveIncomeNetOfTax: Optional[int]
    # EBIT/EBITDA
    ebit: Optional[int]
    ebitda: Optional[int]
    # Net Income
    netIncome: Optional[int]


@dataclass
class AnnualIncomeStatementData:
    fiscalDateEnding: str
    reportedCurrency: str
    # Revenue & Cost
    grossProfit: Optional[int]
    totalRevenue: Optional[int]
    costOfRevenue: Optional[int]
    costofGoodsAndServicesSold: Optional[int]
    # Operating
    operatingIncome: Optional[int]
    sellingGeneralAndAdministrative: Optional[int]
    researchAndDevelopment: Optional[int]
    operatingExpenses: Optional[int]
    # Interest & Investment
    investmentIncomeNet: Optional[int]
    netInterestIncome: Optional[int]
    interestIncome: Optional[int]
    interestExpense: Optional[int]
    nonInterestIncome: Optional[int]
    otherNonOperatingIncome: Optional[int]
    interestAndDebtExpense: Optional[int]
    # Depreciation
    depreciation: Optional[int]
    depreciationAndAmortization: Optional[int]
    # Income & Tax
    incomeBeforeTax: Optional[int]
    incomeTaxExpense: Optional[int]
    netIncomeFromContinuingOperations: Optional[int]
    comprehensiveIncomeNetOfTax: Optional[int]
    # EBIT/EBITDA
    ebit: Optional[int]
    ebitda: Optional[int]
    # Net Income
    netIncome: Optional[int]


@dataclass
class IncomeStatementData:
    symbol: str
    annualReports: list[AnnualIncomeStatementData]
    quarterlyReports: list[QuarterlyIncomeStatementData]


@dataclass
class QuarterlyBalanceSheetData:
    fiscalDateEnding: str
    reportedCurrency: str
    # Assets
    totalAssets: Optional[int]
    totalCurrentAssets: Optional[int]
    cashAndCashEquivalentsAtCarryingValue: Optional[int]
    cashAndShortTermInvestments: Optional[int]
    inventory: Optional[int]
    currentNetReceivables: Optional[int]
    totalNonCurrentAssets: Optional[int]
    propertyPlantEquipment: Optional[int]
    accumulatedDepreciationAmortizationPPE: Optional[int]
    intangibleAssets: Optional[int]
    intangibleAssetsExcludingGoodwill: Optional[int]
    goodwill: Optional[int]
    investments: Optional[int]
    longTermInvestments: Optional[int]
    shortTermInvestments: Optional[int]
    otherCurrentAssets: Optional[int]
    otherNonCurrentAssets: Optional[int]
    # Liabilities
    totalLiabilities: Optional[int]
    totalCurrentLiabilities: Optional[int]
    currentAccountsPayable: Optional[int]
    deferredRevenue: Optional[int]
    currentDebt: Optional[int]
    shortTermDebt: Optional[int]
    totalNonCurrentLiabilities: Optional[int]
    capitalLeaseObligations: Optional[int]
    longTermDebt: Optional[int]
    currentLongTermDebt: Optional[int]
    longTermDebtNoncurrent: Optional[int]
    shortLongTermDebtTotal: Optional[int]
    otherCurrentLiabilities: Optional[int]
    otherNonCurrentLiabilities: Optional[int]
    # Equity
    totalShareholderEquity: Optional[int]
    treasuryStock: Optional[int]
    retainedEarnings: Optional[int]
    commonStock: Optional[int]
    commonStockSharesOutstanding: Optional[int]


@dataclass
class AnnualBalanceSheetData:
    fiscalDateEnding: str
    reportedCurrency: str
    # Assets
    totalAssets: Optional[int]
    totalCurrentAssets: Optional[int]
    cashAndCashEquivalentsAtCarryingValue: Optional[int]
    cashAndShortTermInvestments: Optional[int]
    inventory: Optional[int]
    currentNetReceivables: Optional[int]
    totalNonCurrentAssets: Optional[int]
    propertyPlantEquipment: Optional[int]
    accumulatedDepreciationAmortizationPPE: Optional[int]
    intangibleAssets: Optional[int]
    intangibleAssetsExcludingGoodwill: Optional[int]
    goodwill: Optional[int]
    investments: Optional[int]
    longTermInvestments: Optional[int]
    shortTermInvestments: Optional[int]
    otherCurrentAssets: Optional[int]
    otherNonCurrentAssets: Optional[int]
    # Liabilities
    totalLiabilities: Optional[int]
    totalCurrentLiabilities: Optional[int]
    currentAccountsPayable: Optional[int]
    deferredRevenue: Optional[int]
    currentDebt: Optional[int]
    shortTermDebt: Optional[int]
    totalNonCurrentLiabilities: Optional[int]
    capitalLeaseObligations: Optional[int]
    longTermDebt: Optional[int]
    currentLongTermDebt: Optional[int]
    longTermDebtNoncurrent: Optional[int]
    shortLongTermDebtTotal: Optional[int]
    otherCurrentLiabilities: Optional[int]
    otherNonCurrentLiabilities: Optional[int]
    # Equity
    totalShareholderEquity: Optional[int]
    treasuryStock: Optional[int]
    retainedEarnings: Optional[int]
    commonStock: Optional[int]
    commonStockSharesOutstanding: Optional[int]


@dataclass
class BalanceSheetData:
    symbol: str
    annualReports: list[AnnualBalanceSheetData]
    quarterlyReports: list[QuarterlyBalanceSheetData]


@dataclass
class QuarterlyCashFlowData:
    fiscalDateEnding: str
    reportedCurrency: str
    # Operating Activities
    operatingCashflow: Optional[int]
    paymentsForOperatingActivities: Optional[int]
    proceedsFromOperatingActivities: Optional[int]
    changeInOperatingLiabilities: Optional[int]
    changeInOperatingAssets: Optional[int]
    depreciationDepletionAndAmortization: Optional[int]
    changeInReceivables: Optional[int]
    changeInInventory: Optional[int]
    profitLoss: Optional[int]
    # Investing Activities
    capitalExpenditures: Optional[int]
    cashflowFromInvestment: Optional[int]
    # Financing Activities
    cashflowFromFinancing: Optional[int]
    proceedsFromRepaymentsOfShortTermDebt: Optional[int]
    paymentsForRepurchaseOfCommonStock: Optional[int]
    paymentsForRepurchaseOfEquity: Optional[int]
    paymentsForRepurchaseOfPreferredStock: Optional[int]
    dividendPayout: Optional[int]
    dividendPayoutCommonStock: Optional[int]
    dividendPayoutPreferredStock: Optional[int]
    proceedsFromIssuanceOfCommonStock: Optional[int]
    proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet: Optional[int]
    proceedsFromIssuanceOfPreferredStock: Optional[int]
    proceedsFromRepurchaseOfEquity: Optional[int]
    proceedsFromSaleOfTreasuryStock: Optional[int]
    # Cash Changes
    changeInCashAndCashEquivalents: Optional[int]
    changeInExchangeRate: Optional[int]
    # Net Income
    netIncome: Optional[int]


@dataclass
class AnnualCashFlowData:
    fiscalDateEnding: str
    reportedCurrency: str
    # Operating Activities
    operatingCashflow: Optional[int]
    paymentsForOperatingActivities: Optional[int]
    proceedsFromOperatingActivities: Optional[int]
    changeInOperatingLiabilities: Optional[int]
    changeInOperatingAssets: Optional[int]
    depreciationDepletionAndAmortization: Optional[int]
    changeInReceivables: Optional[int]
    changeInInventory: Optional[int]
    profitLoss: Optional[int]
    # Investing Activities
    capitalExpenditures: Optional[int]
    cashflowFromInvestment: Optional[int]
    # Financing Activities
    cashflowFromFinancing: Optional[int]
    proceedsFromRepaymentsOfShortTermDebt: Optional[int]
    paymentsForRepurchaseOfCommonStock: Optional[int]
    paymentsForRepurchaseOfEquity: Optional[int]
    paymentsForRepurchaseOfPreferredStock: Optional[int]
    dividendPayout: Optional[int]
    dividendPayoutCommonStock: Optional[int]
    dividendPayoutPreferredStock: Optional[int]
    proceedsFromIssuanceOfCommonStock: Optional[int]
    proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet: Optional[int]
    proceedsFromIssuanceOfPreferredStock: Optional[int]
    proceedsFromRepurchaseOfEquity: Optional[int]
    proceedsFromSaleOfTreasuryStock: Optional[int]
    # Cash Changes
    changeInCashAndCashEquivalents: Optional[int]
    changeInExchangeRate: Optional[int]
    # Net Income
    netIncome: Optional[int]


@dataclass
class CashFlowData:
    symbol: str
    annualReports: list[AnnualCashFlowData]
    quarterlyReports: list[QuarterlyCashFlowData]
