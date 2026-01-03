import yfinance as yf
import math
from stock_spot.models import (
    Stock,
    QuarterlyIncomeStatement, AnnualIncomeStatement,
    QuarterlyBalanceSheet, AnnualBalanceSheet,
    QuarterlyCashFlow, AnnualCashFlow
)


class YFinanceService:
    """Service for fetching stock data from Yahoo Finance using yfinance library"""

    def _safe_value(self, value):
        """Convert value to int, handling NaN and None"""
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_decimal(self, value):
        """Convert value to float for decimal fields, handling NaN and None"""
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_annual_income_statement_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.get_income_stmt(True, True, 'yearly')
            self.save_annual_income_statement(symbol, data)
            return data
        except Exception as e:
            print(f"YFinance Error fetching annual income statement info for {symbol}: {e}")
            return None

    def get_quarterly_income_statement_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.get_income_stmt(True, True, 'quarterly')
            self.save_quarterly_income_statement(symbol, data)
            return data
        except Exception as e:
            print(f"YFinance Error fetching quarterly income statement info for {symbol}: {e}")
            return None

    def get_annual_balance_sheet_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.get_balance_sheet(True, True, 'yearly')
            self.save_annual_balance_sheet(symbol, data)
            return data
        except Exception as e:
            print(f"YFinance Error fetching annual balance sheet info for {symbol}: {e}")
            return None

    def get_quarterly_balance_sheet_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.get_balance_sheet(True, True, 'quarterly')
            self.save_quarterly_balance_sheet(symbol, data)
            return data
        except Exception as e:
            print(f"YFinance Error fetching quarterly balance sheet info for {symbol}: {e}")
            return None

    def get_annual_cashflow_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.get_cashflow(True, True, 'yearly')
            self.save_annual_cashflow(symbol, data)
            return data
        except Exception as e:
            print(f"YFinance Error fetching annual cash flow info for {symbol}: {e}")
            return None

    def get_quarterly_cashflow_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.get_cashflow(True, True, 'quarterly')
            self.save_quarterly_cashflow(symbol, data)
            return data
        except Exception as e:
            print(f"YFinance Error fetching quarterly cash flow info for {symbol}: {e}")
            return None

    def get_stock_info(self, symbol):
        """Fetch stock info and save current price and summary to existing Stock model"""
        try:
            stock = Stock.objects.filter(symbol=symbol).first()
            if not stock:
                print(f"Stock {symbol} not found in database")
                return None
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            stock.name = info.get('shortName') or info.get('longName') or stock.name
            stock.companySummary = info.get('longBusinessSummary') or stock.companySummary
            price = self._safe_decimal(
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or 
                info.get('previousClose')
            ) or stock.currentPrice or stock.startingPrice
            stock.startingPrice = price
            stock.currentPrice = price
            stock.save()
            
            return stock
        except Exception as e:
            print(f"YFinance Error fetching stock info for {symbol}: {e}")
            return None


    """Methods to save fetched data to database models"""
    def save_quarterly_income_statement(self, symbol, data):
        """Fetch and save quarterly income statement data to database"""
        try:
            if data is None:
                return None
            stock = Stock.objects.get(symbol=symbol)
            saved_records = []
            for timestamp, values in data.items():
                fiscal_date = timestamp.date()
                record, created = QuarterlyIncomeStatement.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'totalRevenue': self._safe_value(values.get('Total Revenue')),
                        'operatingRevenue': self._safe_value(values.get('Operating Revenue')),
                        'costOfRevenue': self._safe_value(values.get('Cost Of Revenue')),
                        'grossProfit': self._safe_value(values.get('Gross Profit')),
                        'operatingExpense': self._safe_value(values.get('Operating Expense')),
                        'researchAndDevelopment': self._safe_value(values.get('Research And Development')),
                        'sellingGeneralAndAdministration': self._safe_value(values.get('Selling General And Administration')),
                        'totalExpenses': self._safe_value(values.get('Total Expenses')),
                        'operatingIncome': self._safe_value(values.get('Operating Income')),
                        'totalOperatingIncomeAsReported': self._safe_value(values.get('Total Operating Income As Reported')),
                        'interestIncome': self._safe_value(values.get('Interest Income')),
                        'interestExpense': self._safe_value(values.get('Interest Expense')),
                        'netInterestIncome': self._safe_value(values.get('Net Interest Income')),
                        'interestIncomeNonOperating': self._safe_value(values.get('Interest Income Non Operating')),
                        'interestExpenseNonOperating': self._safe_value(values.get('Interest Expense Non Operating')),
                        'netNonOperatingInterestIncomeExpense': self._safe_value(values.get('Net Non Operating Interest Income Expense')),
                        'otherIncomeExpense': self._safe_value(values.get('Other Income Expense')),
                        'otherNonOperatingIncomeExpenses': self._safe_value(values.get('Other Non Operating Income Expenses')),
                        'specialIncomeCharges': self._safe_value(values.get('Special Income Charges')),
                        'restructuringAndMergerAcquisition': self._safe_value(values.get('Restructuring And Mergern Acquisition')),
                        'pretaxIncome': self._safe_value(values.get('Pretax Income')),
                        'taxProvision': self._safe_value(values.get('Tax Provision')),
                        'taxRateForCalcs': self._safe_decimal(values.get('Tax Rate For Calcs')),
                        'taxEffectOfUnusualItems': self._safe_value(values.get('Tax Effect Of Unusual Items')),
                        'netIncome': self._safe_value(values.get('Net Income')),
                        'netIncomeContinuousOperations': self._safe_value(values.get('Net Income Continuous Operations')),
                        'netIncomeIncludingNoncontrollingInterests': self._safe_value(values.get('Net Income Including Noncontrolling Interests')),
                        'netIncomeCommonStockholders': self._safe_value(values.get('Net Income Common Stockholders')),
                        'netIncomeFromContinuingOperationNetMinorityInterest': self._safe_value(values.get('Net Income From Continuing Operation Net Minority Interest')),
                        'netIncomeFromContinuingAndDiscontinuedOperation': self._safe_value(values.get('Net Income From Continuing And Discontinued Operation')),
                        'minorityInterests': self._safe_value(values.get('Minority Interests')),
                        'dilutedNIAvailableToComStockholders': self._safe_value(values.get('Diluted NI Availto Com Stockholders')),
                        'basicEPS': self._safe_decimal(values.get('Basic EPS')),
                        'dilutedEPS': self._safe_decimal(values.get('Diluted EPS')),
                        'basicAverageShares': self._safe_value(values.get('Basic Average Shares')),
                        'dilutedAverageShares': self._safe_value(values.get('Diluted Average Shares')),
                        'ebitda': self._safe_value(values.get('EBITDA')),
                        'ebit': self._safe_value(values.get('EBIT')),
                        'normalizedEBITDA': self._safe_value(values.get('Normalized EBITDA')),
                        'reconciledDepreciation': self._safe_value(values.get('Reconciled Depreciation')),
                        'reconciledCostOfRevenue': self._safe_value(values.get('Reconciled Cost Of Revenue')),
                        'normalizedIncome': self._safe_value(values.get('Normalized Income')),
                        'totalUnusualItems': self._safe_value(values.get('Total Unusual Items')),
                        'totalUnusualItemsExcludingGoodwill': self._safe_value(values.get('Total Unusual Items Excluding Goodwill')),
                        'rentExpenseSupplemental': self._safe_value(values.get('Rent Expense Supplemental')),
                        'otherUnderPreferredStockDividend': self._safe_value(values.get('Otherunder Preferred Stock Dividend')),
                    }
                )
                saved_records.append(record)
            return saved_records
        except Exception as e:
            print(f"Error saving quarterly income statement for {symbol}: {e}")
            return None

    def save_annual_income_statement(self, symbol, data):
        """Fetch and save annual income statement data to database"""
        try:
            if data is None:
                return None
            stock = Stock.objects.get(symbol=symbol)
            saved_records = []
            for timestamp, values in data.items():
                fiscal_date = timestamp.date()
                record, created = AnnualIncomeStatement.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'totalRevenue': self._safe_value(values.get('Total Revenue')),
                        'operatingRevenue': self._safe_value(values.get('Operating Revenue')),
                        'costOfRevenue': self._safe_value(values.get('Cost Of Revenue')),
                        'grossProfit': self._safe_value(values.get('Gross Profit')),
                        'operatingExpense': self._safe_value(values.get('Operating Expense')),
                        'researchAndDevelopment': self._safe_value(values.get('Research And Development')),
                        'sellingGeneralAndAdministration': self._safe_value(values.get('Selling General And Administration')),
                        'totalExpenses': self._safe_value(values.get('Total Expenses')),
                        'operatingIncome': self._safe_value(values.get('Operating Income')),
                        'totalOperatingIncomeAsReported': self._safe_value(values.get('Total Operating Income As Reported')),
                        'interestIncome': self._safe_value(values.get('Interest Income')),
                        'interestExpense': self._safe_value(values.get('Interest Expense')),
                        'netInterestIncome': self._safe_value(values.get('Net Interest Income')),
                        'interestIncomeNonOperating': self._safe_value(values.get('Interest Income Non Operating')),
                        'interestExpenseNonOperating': self._safe_value(values.get('Interest Expense Non Operating')),
                        'netNonOperatingInterestIncomeExpense': self._safe_value(values.get('Net Non Operating Interest Income Expense')),
                        'otherIncomeExpense': self._safe_value(values.get('Other Income Expense')),
                        'otherNonOperatingIncomeExpenses': self._safe_value(values.get('Other Non Operating Income Expenses')),
                        'specialIncomeCharges': self._safe_value(values.get('Special Income Charges')),
                        'restructuringAndMergerAcquisition': self._safe_value(values.get('Restructuring And Mergern Acquisition')),
                        'pretaxIncome': self._safe_value(values.get('Pretax Income')),
                        'taxProvision': self._safe_value(values.get('Tax Provision')),
                        'taxRateForCalcs': self._safe_decimal(values.get('Tax Rate For Calcs')),
                        'taxEffectOfUnusualItems': self._safe_value(values.get('Tax Effect Of Unusual Items')),
                        'netIncome': self._safe_value(values.get('Net Income')),
                        'netIncomeContinuousOperations': self._safe_value(values.get('Net Income Continuous Operations')),
                        'netIncomeIncludingNoncontrollingInterests': self._safe_value(values.get('Net Income Including Noncontrolling Interests')),
                        'netIncomeCommonStockholders': self._safe_value(values.get('Net Income Common Stockholders')),
                        'netIncomeFromContinuingOperationNetMinorityInterest': self._safe_value(values.get('Net Income From Continuing Operation Net Minority Interest')),
                        'netIncomeFromContinuingAndDiscontinuedOperation': self._safe_value(values.get('Net Income From Continuing And Discontinued Operation')),
                        'minorityInterests': self._safe_value(values.get('Minority Interests')),
                        'dilutedNIAvailableToComStockholders': self._safe_value(values.get('Diluted NI Availto Com Stockholders')),
                        'basicEPS': self._safe_decimal(values.get('Basic EPS')),
                        'dilutedEPS': self._safe_decimal(values.get('Diluted EPS')),
                        'basicAverageShares': self._safe_value(values.get('Basic Average Shares')),
                        'dilutedAverageShares': self._safe_value(values.get('Diluted Average Shares')),
                        'averageDilutionEarnings': self._safe_value(values.get('Average Dilution Earnings')),
                        'ebitda': self._safe_value(values.get('EBITDA')),
                        'ebit': self._safe_value(values.get('EBIT')),
                        'normalizedEBITDA': self._safe_value(values.get('Normalized EBITDA')),
                        'reconciledDepreciation': self._safe_value(values.get('Reconciled Depreciation')),
                        'reconciledCostOfRevenue': self._safe_value(values.get('Reconciled Cost Of Revenue')),
                        'normalizedIncome': self._safe_value(values.get('Normalized Income')),
                        'totalUnusualItems': self._safe_value(values.get('Total Unusual Items')),
                        'totalUnusualItemsExcludingGoodwill': self._safe_value(values.get('Total Unusual Items Excluding Goodwill')),
                        'rentExpenseSupplemental': self._safe_value(values.get('Rent Expense Supplemental')),
                        'otherUnderPreferredStockDividend': self._safe_value(values.get('Otherunder Preferred Stock Dividend')),
                    }
                )
                saved_records.append(record)
            return saved_records
        except Exception as e:
            print(f"Error saving annual income statement for {symbol}: {e}")
            return None

    def save_quarterly_balance_sheet(self, symbol, data):
        """Fetch and save quarterly balance sheet data to database"""
        try:
            if data is None:
                return None
            stock = Stock.objects.get(symbol=symbol)
            saved_records = []
            for timestamp, values in data.items():
                fiscal_date = timestamp.date()
                record, created = QuarterlyBalanceSheet.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'treasurySharesNumber': self._safe_value(values.get('Treasury Shares Number')),
                        'ordinarySharesNumber': self._safe_value(values.get('Ordinary Shares Number')),
                        'shareIssued': self._safe_value(values.get('Share Issued')),
                        'totalDebt': self._safe_value(values.get('Total Debt')),
                        'tangibleBookValue': self._safe_value(values.get('Tangible Book Value')),
                        'investedCapital': self._safe_value(values.get('Invested Capital')),
                        'workingCapital': self._safe_value(values.get('Working Capital')),
                        'netTangibleAssets': self._safe_value(values.get('Net Tangible Assets')),
                        'capitalLeaseObligations': self._safe_value(values.get('Capital Lease Obligations')),
                        'commonStockEquity': self._safe_value(values.get('Common Stock Equity')),
                        'totalCapitalization': self._safe_value(values.get('Total Capitalization')),
                        'totalEquityGrossMinorityInterest': self._safe_value(values.get('Total Equity Gross Minority Interest')),
                        'minorityInterest': self._safe_value(values.get('Minority Interest')),
                        'stockholdersEquity': self._safe_value(values.get('Stockholders Equity')),
                        'gainsLossesNotAffectingRetainedEarnings': self._safe_value(values.get('Gains Losses Not Affecting Retained Earnings')),
                        'otherEquityAdjustments': self._safe_value(values.get('Other Equity Adjustments')),
                        'retainedEarnings': self._safe_value(values.get('Retained Earnings')),
                        'additionalPaidInCapital': self._safe_value(values.get('Additional Paid In Capital')),
                        'capitalStock': self._safe_value(values.get('Capital Stock')),
                        'commonStock': self._safe_value(values.get('Common Stock')),
                        'preferredStock': self._safe_value(values.get('Preferred Stock')),
                        'totalLiabilitiesNetMinorityInterest': self._safe_value(values.get('Total Liabilities Net Minority Interest')),
                        'totalNonCurrentLiabilitiesNetMinorityInterest': self._safe_value(values.get('Total Non Current Liabilities Net Minority Interest')),
                        'otherNonCurrentLiabilities': self._safe_value(values.get('Other Non Current Liabilities')),
                        'nonCurrentDeferredLiabilities': self._safe_value(values.get('Non Current Deferred Liabilities')),
                        'nonCurrentDeferredRevenue': self._safe_value(values.get('Non Current Deferred Revenue')),
                        'longTermDebtAndCapitalLeaseObligation': self._safe_value(values.get('Long Term Debt And Capital Lease Obligation')),
                        'longTermCapitalLeaseObligation': self._safe_value(values.get('Long Term Capital Lease Obligation')),
                        'longTermDebt': self._safe_value(values.get('Long Term Debt')),
                        'longTermProvisions': self._safe_value(values.get('Long Term Provisions')),
                        'currentLiabilities': self._safe_value(values.get('Current Liabilities')),
                        'otherCurrentLiabilities': self._safe_value(values.get('Other Current Liabilities')),
                        'currentDeferredLiabilities': self._safe_value(values.get('Current Deferred Liabilities')),
                        'currentDeferredRevenue': self._safe_value(values.get('Current Deferred Revenue')),
                        'currentDebtAndCapitalLeaseObligation': self._safe_value(values.get('Current Debt And Capital Lease Obligation')),
                        'currentCapitalLeaseObligation': self._safe_value(values.get('Current Capital Lease Obligation')),
                        'currentDebt': self._safe_value(values.get('Current Debt')),
                        'otherCurrentBorrowings': self._safe_value(values.get('Other Current Borrowings')),
                        'lineOfCredit': self._safe_value(values.get('Line Of Credit')),
                        'currentProvisions': self._safe_value(values.get('Current Provisions')),
                        'payablesAndAccruedExpenses': self._safe_value(values.get('Payables And Accrued Expenses')),
                        'currentAccruedExpenses': self._safe_value(values.get('Current Accrued Expenses')),
                        'payables': self._safe_value(values.get('Payables')),
                        'totalTaxPayable': self._safe_value(values.get('Total Tax Payable')),
                        'accountsPayable': self._safe_value(values.get('Accounts Payable')),
                        'totalAssets': self._safe_value(values.get('Total Assets')),
                        'totalNonCurrentAssets': self._safe_value(values.get('Total Non Current Assets')),
                        'otherNonCurrentAssets': self._safe_value(values.get('Other Non Current Assets')),
                        'nonCurrentDeferredAssets': self._safe_value(values.get('Non Current Deferred Assets')),
                        'nonCurrentDeferredTaxesAssets': self._safe_value(values.get('Non Current Deferred Taxes Assets')),
                        'investmentsAndAdvances': self._safe_value(values.get('Investments And Advances')),
                        'otherInvestments': self._safe_value(values.get('Other Investments')),
                        'goodwillAndOtherIntangibleAssets': self._safe_value(values.get('Goodwill And Other Intangible Assets')),
                        'otherIntangibleAssets': self._safe_value(values.get('Other Intangible Assets')),
                        'goodwill': self._safe_value(values.get('Goodwill')),
                        'netPPE': self._safe_value(values.get('Net PPE')),
                        'accumulatedDepreciation': self._safe_value(values.get('Accumulated Depreciation')),
                        'grossPPE': self._safe_value(values.get('Gross PPE')),
                        'leases': self._safe_value(values.get('Leases')),
                        'constructionInProgress': self._safe_value(values.get('Construction In Progress')),
                        'otherProperties': self._safe_value(values.get('Other Properties')),
                        'machineryFurnitureEquipment': self._safe_value(values.get('Machinery Furniture Equipment')),
                        'landAndImprovements': self._safe_value(values.get('Land And Improvements')),
                        'properties': self._safe_value(values.get('Properties')),
                        'currentAssets': self._safe_value(values.get('Current Assets')),
                        'otherCurrentAssets': self._safe_value(values.get('Other Current Assets')),
                        'inventory': self._safe_value(values.get('Inventory')),
                        'otherInventories': self._safe_value(values.get('Other Inventories')),
                        'finishedGoods': self._safe_value(values.get('Finished Goods')),
                        'workInProcess': self._safe_value(values.get('Work In Process')),
                        'rawMaterials': self._safe_value(values.get('Raw Materials')),
                        'receivables': self._safe_value(values.get('Receivables')),
                        'accountsReceivable': self._safe_value(values.get('Accounts Receivable')),
                        'cashCashEquivalentsAndShortTermInvestments': self._safe_value(values.get('Cash Cash Equivalents And Short Term Investments')),
                        'otherShortTermInvestments': self._safe_value(values.get('Other Short Term Investments')),
                        'cashAndCashEquivalents': self._safe_value(values.get('Cash And Cash Equivalents')),
                        'cashEquivalents': self._safe_value(values.get('Cash Equivalents')),
                        'cashFinancial': self._safe_value(values.get('Cash Financial')),
                    }
                )
                saved_records.append(record)
            return saved_records
        except Exception as e:
            print(f"Error saving quarterly balance sheet for {symbol}: {e}")
            return None

    def save_annual_balance_sheet(self, symbol, data):
        """Fetch and save annual balance sheet data to database"""
        try:
            if data is None:
                return None
            stock = Stock.objects.get(symbol=symbol)
            saved_records = []
            for timestamp, values in data.items():
                fiscal_date = timestamp.date()
                record, created = AnnualBalanceSheet.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'treasurySharesNumber': self._safe_value(values.get('Treasury Shares Number')),
                        'ordinarySharesNumber': self._safe_value(values.get('Ordinary Shares Number')),
                        'shareIssued': self._safe_value(values.get('Share Issued')),
                        'totalDebt': self._safe_value(values.get('Total Debt')),
                        'tangibleBookValue': self._safe_value(values.get('Tangible Book Value')),
                        'investedCapital': self._safe_value(values.get('Invested Capital')),
                        'workingCapital': self._safe_value(values.get('Working Capital')),
                        'netTangibleAssets': self._safe_value(values.get('Net Tangible Assets')),
                        'capitalLeaseObligations': self._safe_value(values.get('Capital Lease Obligations')),
                        'commonStockEquity': self._safe_value(values.get('Common Stock Equity')),
                        'totalCapitalization': self._safe_value(values.get('Total Capitalization')),
                        'totalEquityGrossMinorityInterest': self._safe_value(values.get('Total Equity Gross Minority Interest')),
                        'minorityInterest': self._safe_value(values.get('Minority Interest')),
                        'stockholdersEquity': self._safe_value(values.get('Stockholders Equity')),
                        'gainsLossesNotAffectingRetainedEarnings': self._safe_value(values.get('Gains Losses Not Affecting Retained Earnings')),
                        'otherEquityAdjustments': self._safe_value(values.get('Other Equity Adjustments')),
                        'retainedEarnings': self._safe_value(values.get('Retained Earnings')),
                        'additionalPaidInCapital': self._safe_value(values.get('Additional Paid In Capital')),
                        'capitalStock': self._safe_value(values.get('Capital Stock')),
                        'commonStock': self._safe_value(values.get('Common Stock')),
                        'preferredStock': self._safe_value(values.get('Preferred Stock')),
                        'totalLiabilitiesNetMinorityInterest': self._safe_value(values.get('Total Liabilities Net Minority Interest')),
                        'totalNonCurrentLiabilitiesNetMinorityInterest': self._safe_value(values.get('Total Non Current Liabilities Net Minority Interest')),
                        'otherNonCurrentLiabilities': self._safe_value(values.get('Other Non Current Liabilities')),
                        'preferredSecuritiesOutsideStockEquity': self._safe_value(values.get('Preferred Securities Outside Stock Equity')),
                        'nonCurrentAccruedExpenses': self._safe_value(values.get('Non Current Accrued Expenses')),
                        'nonCurrentDeferredLiabilities': self._safe_value(values.get('Non Current Deferred Liabilities')),
                        'nonCurrentDeferredRevenue': self._safe_value(values.get('Non Current Deferred Revenue')),
                        'nonCurrentDeferredTaxesLiabilities': self._safe_value(values.get('Non Current Deferred Taxes Liabilities')),
                        'longTermDebtAndCapitalLeaseObligation': self._safe_value(values.get('Long Term Debt And Capital Lease Obligation')),
                        'longTermCapitalLeaseObligation': self._safe_value(values.get('Long Term Capital Lease Obligation')),
                        'longTermDebt': self._safe_value(values.get('Long Term Debt')),
                        'longTermProvisions': self._safe_value(values.get('Long Term Provisions')),
                        'currentLiabilities': self._safe_value(values.get('Current Liabilities')),
                        'otherCurrentLiabilities': self._safe_value(values.get('Other Current Liabilities')),
                        'currentDeferredLiabilities': self._safe_value(values.get('Current Deferred Liabilities')),
                        'currentDeferredRevenue': self._safe_value(values.get('Current Deferred Revenue')),
                        'currentDebtAndCapitalLeaseObligation': self._safe_value(values.get('Current Debt And Capital Lease Obligation')),
                        'currentCapitalLeaseObligation': self._safe_value(values.get('Current Capital Lease Obligation')),
                        'currentDebt': self._safe_value(values.get('Current Debt')),
                        'otherCurrentBorrowings': self._safe_value(values.get('Other Current Borrowings')),
                        'lineOfCredit': self._safe_value(values.get('Line Of Credit')),
                        'currentProvisions': self._safe_value(values.get('Current Provisions')),
                        'payablesAndAccruedExpenses': self._safe_value(values.get('Payables And Accrued Expenses')),
                        'currentAccruedExpenses': self._safe_value(values.get('Current Accrued Expenses')),
                        'interestPayable': self._safe_value(values.get('Interest Payable')),
                        'payables': self._safe_value(values.get('Payables')),
                        'totalTaxPayable': self._safe_value(values.get('Total Tax Payable')),
                        'accountsPayable': self._safe_value(values.get('Accounts Payable')),
                        'totalAssets': self._safe_value(values.get('Total Assets')),
                        'totalNonCurrentAssets': self._safe_value(values.get('Total Non Current Assets')),
                        'otherNonCurrentAssets': self._safe_value(values.get('Other Non Current Assets')),
                        'nonCurrentDeferredAssets': self._safe_value(values.get('Non Current Deferred Assets')),
                        'nonCurrentDeferredTaxesAssets': self._safe_value(values.get('Non Current Deferred Taxes Assets')),
                        'goodwillAndOtherIntangibleAssets': self._safe_value(values.get('Goodwill And Other Intangible Assets')),
                        'otherIntangibleAssets': self._safe_value(values.get('Other Intangible Assets')),
                        'goodwill': self._safe_value(values.get('Goodwill')),
                        'netPPE': self._safe_value(values.get('Net PPE')),
                        'accumulatedDepreciation': self._safe_value(values.get('Accumulated Depreciation')),
                        'grossPPE': self._safe_value(values.get('Gross PPE')),
                        'leases': self._safe_value(values.get('Leases')),
                        'constructionInProgress': self._safe_value(values.get('Construction In Progress')),
                        'otherProperties': self._safe_value(values.get('Other Properties')),
                        'machineryFurnitureEquipment': self._safe_value(values.get('Machinery Furniture Equipment')),
                        'landAndImprovements': self._safe_value(values.get('Land And Improvements')),
                        'properties': self._safe_value(values.get('Properties')),
                        'currentAssets': self._safe_value(values.get('Current Assets')),
                        'otherCurrentAssets': self._safe_value(values.get('Other Current Assets')),
                        'prepaidAssets': self._safe_value(values.get('Prepaid Assets')),
                        'inventory': self._safe_value(values.get('Inventory')),
                        'otherInventories': self._safe_value(values.get('Other Inventories')),
                        'finishedGoods': self._safe_value(values.get('Finished Goods')),
                        'workInProcess': self._safe_value(values.get('Work In Process')),
                        'rawMaterials': self._safe_value(values.get('Raw Materials')),
                        'receivables': self._safe_value(values.get('Receivables')),
                        'accountsReceivable': self._safe_value(values.get('Accounts Receivable')),
                        'cashCashEquivalentsAndShortTermInvestments': self._safe_value(values.get('Cash Cash Equivalents And Short Term Investments')),
                        'otherShortTermInvestments': self._safe_value(values.get('Other Short Term Investments')),
                        'cashAndCashEquivalents': self._safe_value(values.get('Cash And Cash Equivalents')),
                        'cashEquivalents': self._safe_value(values.get('Cash Equivalents')),
                        'cashFinancial': self._safe_value(values.get('Cash Financial')),
                    }
                )
                saved_records.append(record)
            return saved_records
        except Exception as e:
            print(f"Error saving annual balance sheet for {symbol}: {e}")
            return None

    def save_quarterly_cashflow(self, symbol, data):
        """Fetch and save quarterly cash flow data to database"""
        try:
            if data is None:
                return None
            stock = Stock.objects.get(symbol=symbol)
            saved_records = []
            for timestamp, values in data.items():
                fiscal_date = timestamp.date()
                record, created = QuarterlyCashFlow.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'freeCashFlow': self._safe_value(values.get('Free Cash Flow')),
                        'capitalExpenditure': self._safe_value(values.get('Capital Expenditure')),
                        'endCashPosition': self._safe_value(values.get('End Cash Position')),
                        'beginningCashPosition': self._safe_value(values.get('Beginning Cash Position')),
                        'effectOfExchangeRateChanges': self._safe_value(values.get('Effect Of Exchange Rate Changes')),
                        'changesInCash': self._safe_value(values.get('Changes In Cash')),
                        'financingCashFlow': self._safe_value(values.get('Financing Cash Flow')),
                        'cashFlowFromContinuingFinancingActivities': self._safe_value(values.get('Cash Flow From Continuing Financing Activities')),
                        'netOtherFinancingCharges': self._safe_value(values.get('Net Other Financing Charges')),
                        'proceedsFromStockOptionExercised': self._safe_value(values.get('Proceeds From Stock Option Exercised')),
                        'netIssuancePaymentsOfDebt': self._safe_value(values.get('Net Issuance Payments Of Debt')),
                        'netLongTermDebtIssuance': self._safe_value(values.get('Net Long Term Debt Issuance')),
                        'longTermDebtPayments': self._safe_value(values.get('Long Term Debt Payments')),
                        'longTermDebtIssuance': self._safe_value(values.get('Long Term Debt Issuance')),
                        'repaymentOfDebt': self._safe_value(values.get('Repayment Of Debt')),
                        'issuanceOfDebt': self._safe_value(values.get('Issuance Of Debt')),
                        'investingCashFlow': self._safe_value(values.get('Investing Cash Flow')),
                        'cashFlowFromContinuingInvestingActivities': self._safe_value(values.get('Cash Flow From Continuing Investing Activities')),
                        'netInvestmentPurchaseAndSale': self._safe_value(values.get('Net Investment Purchase And Sale')),
                        'saleOfInvestment': self._safe_value(values.get('Sale Of Investment')),
                        'purchaseOfInvestment': self._safe_value(values.get('Purchase Of Investment')),
                        'netBusinessPurchaseAndSale': self._safe_value(values.get('Net Business Purchase And Sale')),
                        'netPPEPurchaseAndSale': self._safe_value(values.get('Net PPE Purchase And Sale')),
                        'purchaseOfPPE': self._safe_value(values.get('Purchase Of PPE')),
                        'operatingCashFlow': self._safe_value(values.get('Operating Cash Flow')),
                        'cashFlowFromContinuingOperatingActivities': self._safe_value(values.get('Cash Flow From Continuing Operating Activities')),
                        'netIncomeFromContinuingOperations': self._safe_value(values.get('Net Income From Continuing Operations')),
                        'changeInWorkingCapital': self._safe_value(values.get('Change In Working Capital')),
                        'changeInOtherWorkingCapital': self._safe_value(values.get('Change In Other Working Capital')),
                        'changeInOtherCurrentAssets': self._safe_value(values.get('Change In Other Current Assets')),
                        'changeInPayablesAndAccruedExpense': self._safe_value(values.get('Change In Payables And Accrued Expense')),
                        'changeInPrepaidAssets': self._safe_value(values.get('Change In Prepaid Assets')),
                        'changeInInventory': self._safe_value(values.get('Change In Inventory')),
                        'changeInReceivables': self._safe_value(values.get('Change In Receivables')),
                        'changesInAccountReceivables': self._safe_value(values.get('Changes In Account Receivables')),
                        'otherNonCashItems': self._safe_value(values.get('Other Non Cash Items')),
                        'stockBasedCompensation': self._safe_value(values.get('Stock Based Compensation')),
                        'assetImpairmentCharge': self._safe_value(values.get('Asset Impairment Charge')),
                        'deferredTax': self._safe_value(values.get('Deferred Tax')),
                        'deferredIncomeTax': self._safe_value(values.get('Deferred Income Tax')),
                        'depreciationAmortizationDepletion': self._safe_value(values.get('Depreciation Amortization Depletion')),
                        'depreciationAndAmortization': self._safe_value(values.get('Depreciation And Amortization')),
                        'depreciation': self._safe_value(values.get('Depreciation')),
                        'operatingGainsLosses': self._safe_value(values.get('Operating Gains Losses')),
                        'netForeignCurrencyExchangeGainLoss': self._safe_value(values.get('Net Foreign Currency Exchange Gain Loss')),
                        'gainLossOnSaleOfPPE': self._safe_value(values.get('Gain Loss On Sale Of PPE')),
                    }
                )
                saved_records.append(record)
            return saved_records
        except Exception as e:
            print(f"Error saving quarterly cash flow for {symbol}: {e}")
            return None

    def save_annual_cashflow(self, symbol, data):
        """Fetch and save annual cash flow data to database"""
        try:
            if data is None:
                return None
            stock = Stock.objects.get(symbol=symbol)
            saved_records = []
            for timestamp, values in data.items():
                fiscal_date = timestamp.date()
                record, created = AnnualCashFlow.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'freeCashFlow': self._safe_value(values.get('Free Cash Flow')),
                        'capitalExpenditure': self._safe_value(values.get('Capital Expenditure')),
                        'interestPaidSupplementalData': self._safe_value(values.get('Interest Paid Supplemental Data')),
                        'incomeTaxPaidSupplementalData': self._safe_value(values.get('Income Tax Paid Supplemental Data')),
                        'endCashPosition': self._safe_value(values.get('End Cash Position')),
                        'beginningCashPosition': self._safe_value(values.get('Beginning Cash Position')),
                        'effectOfExchangeRateChanges': self._safe_value(values.get('Effect Of Exchange Rate Changes')),
                        'changesInCash': self._safe_value(values.get('Changes In Cash')),
                        'financingCashFlow': self._safe_value(values.get('Financing Cash Flow')),
                        'cashFlowFromContinuingFinancingActivities': self._safe_value(values.get('Cash Flow From Continuing Financing Activities')),
                        'netOtherFinancingCharges': self._safe_value(values.get('Net Other Financing Charges')),
                        'proceedsFromStockOptionExercised': self._safe_value(values.get('Proceeds From Stock Option Exercised')),
                        'netCommonStockIssuance': self._safe_value(values.get('Net Common Stock Issuance')),
                        'commonStockIssuance': self._safe_value(values.get('Common Stock Issuance')),
                        'issuanceOfCapitalStock': self._safe_value(values.get('Issuance Of Capital Stock')),
                        'netIssuancePaymentsOfDebt': self._safe_value(values.get('Net Issuance Payments Of Debt')),
                        'netLongTermDebtIssuance': self._safe_value(values.get('Net Long Term Debt Issuance')),
                        'longTermDebtPayments': self._safe_value(values.get('Long Term Debt Payments')),
                        'longTermDebtIssuance': self._safe_value(values.get('Long Term Debt Issuance')),
                        'repaymentOfDebt': self._safe_value(values.get('Repayment Of Debt')),
                        'issuanceOfDebt': self._safe_value(values.get('Issuance Of Debt')),
                        'investingCashFlow': self._safe_value(values.get('Investing Cash Flow')),
                        'cashFlowFromContinuingInvestingActivities': self._safe_value(values.get('Cash Flow From Continuing Investing Activities')),
                        'netOtherInvestingChanges': self._safe_value(values.get('Net Other Investing Changes')),
                        'netInvestmentPurchaseAndSale': self._safe_value(values.get('Net Investment Purchase And Sale')),
                        'saleOfInvestment': self._safe_value(values.get('Sale Of Investment')),
                        'purchaseOfInvestment': self._safe_value(values.get('Purchase Of Investment')),
                        'netBusinessPurchaseAndSale': self._safe_value(values.get('Net Business Purchase And Sale')),
                        'saleOfBusiness': self._safe_value(values.get('Sale Of Business')),
                        'purchaseOfBusiness': self._safe_value(values.get('Purchase Of Business')),
                        'netIntangiblesPurchaseAndSale': self._safe_value(values.get('Net Intangibles Purchase And Sale')),
                        'saleOfIntangibles': self._safe_value(values.get('Sale Of Intangibles')),
                        'purchaseOfIntangibles': self._safe_value(values.get('Purchase Of Intangibles')),
                        'netPPEPurchaseAndSale': self._safe_value(values.get('Net PPE Purchase And Sale')),
                        'purchaseOfPPE': self._safe_value(values.get('Purchase Of PPE')),
                        'operatingCashFlow': self._safe_value(values.get('Operating Cash Flow')),
                        'cashFlowFromContinuingOperatingActivities': self._safe_value(values.get('Cash Flow From Continuing Operating Activities')),
                        'netIncomeFromContinuingOperations': self._safe_value(values.get('Net Income From Continuing Operations')),
                        'changeInWorkingCapital': self._safe_value(values.get('Change In Working Capital')),
                        'changeInOtherWorkingCapital': self._safe_value(values.get('Change In Other Working Capital')),
                        'changeInOtherCurrentLiabilities': self._safe_value(values.get('Change In Other Current Liabilities')),
                        'changeInOtherCurrentAssets': self._safe_value(values.get('Change In Other Current Assets')),
                        'changeInPayablesAndAccruedExpense': self._safe_value(values.get('Change In Payables And Accrued Expense')),
                        'changeInPayable': self._safe_value(values.get('Change In Payable')),
                        'changeInAccountPayable': self._safe_value(values.get('Change In Account Payable')),
                        'changeInPrepaidAssets': self._safe_value(values.get('Change In Prepaid Assets')),
                        'changeInInventory': self._safe_value(values.get('Change In Inventory')),
                        'changeInReceivables': self._safe_value(values.get('Change In Receivables')),
                        'changesInAccountReceivables': self._safe_value(values.get('Changes In Account Receivables')),
                        'otherNonCashItems': self._safe_value(values.get('Other Non Cash Items')),
                        'stockBasedCompensation': self._safe_value(values.get('Stock Based Compensation')),
                        'assetImpairmentCharge': self._safe_value(values.get('Asset Impairment Charge')),
                        'deferredTax': self._safe_value(values.get('Deferred Tax')),
                        'deferredIncomeTax': self._safe_value(values.get('Deferred Income Tax')),
                        'depreciationAmortizationDepletion': self._safe_value(values.get('Depreciation Amortization Depletion')),
                        'depreciationAndAmortization': self._safe_value(values.get('Depreciation And Amortization')),
                        'depreciation': self._safe_value(values.get('Depreciation')),
                        'operatingGainsLosses': self._safe_value(values.get('Operating Gains Losses')),
                        'netForeignCurrencyExchangeGainLoss': self._safe_value(values.get('Net Foreign Currency Exchange Gain Loss')),
                        'gainLossOnSaleOfPPE': self._safe_value(values.get('Gain Loss On Sale Of PPE')),
                    }
                )
                saved_records.append(record)
            return saved_records
        except Exception as e:
            print(f"Error saving annual cash flow for {symbol}: {e}")
            return None