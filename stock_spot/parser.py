from stock_spot.schemas import (
    EarningsData, AnnualEarningsData, QuarterlyEarningsData,
    BalanceSheetData, AnnualBalanceSheetData, QuarterlyBalanceSheetData,
    IncomeStatementData, AnnualIncomeStatementData, QuarterlyIncomeStatementData,
    CashFlowData, AnnualCashFlowData, QuarterlyCashFlowData
)


class Parser:
    @staticmethod
    def _safe_float(value):
        """Safely convert value to float, returns None if value is None or 'None' string"""
        if value is None or value == 'None' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(value):
        """Safely convert value to int, returns None if value is None or 'None' string"""
        if value is None or value == 'None' or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def parse_eps_data(api_response: dict) -> EarningsData:
        """Convert Alpha Vantage API response to EarningsData object"""
        
        # Extract symbol from response
        symbol = api_response.get('symbol', '')
        
        # Parse annual earnings - convert list of dicts to list of AnnualEarningsData objects
        annual_earnings_list = []
        for annual in api_response.get('annualEarnings', []):
            annual_obj = AnnualEarningsData(
                fiscalDateEnding=annual.get('fiscalDateEnding', ''),
                reportedEPS=Parser._safe_float(annual.get('reportedEPS'))
            )
            annual_earnings_list.append(annual_obj)
        
        # Parse quarterly earnings - convert list of dicts to list of QuarterlyEarningsData objects
        quarterly_earnings_list = []
        for quarterly in api_response.get('quarterlyEarnings', []):
            quarterly_obj = QuarterlyEarningsData(
                fiscalDateEnding=quarterly.get('fiscalDateEnding', ''),
                reportedDate=quarterly.get('reportedDate', ''),
                reportedEPS=Parser._safe_float(quarterly.get('reportedEPS')),
                estimatedEPS=Parser._safe_float(quarterly.get('estimatedEPS')),
                surprise=Parser._safe_float(quarterly.get('surprise')),
                surprisePercentage=Parser._safe_float(quarterly.get('surprisePercentage')),
                reportTime=quarterly.get('reportTime', '')
            )
            quarterly_earnings_list.append(quarterly_obj)
        
        # Create and return EarningsData object with all parsed data
        return EarningsData(
            symbol=symbol,
            annualEarnings=annual_earnings_list,
            quarterlyEarnings=quarterly_earnings_list
        )

    @staticmethod
    def _parse_balance_sheet_report(report: dict, data_class):
        """Helper to parse a single balance sheet report (annual or quarterly)"""
        return data_class(
            fiscalDateEnding=report.get('fiscalDateEnding', ''),
            reportedCurrency=report.get('reportedCurrency', 'USD'),
            # Assets
            totalAssets=Parser._safe_int(report.get('totalAssets')),
            totalCurrentAssets=Parser._safe_int(report.get('totalCurrentAssets')),
            cashAndCashEquivalentsAtCarryingValue=Parser._safe_int(report.get('cashAndCashEquivalentsAtCarryingValue')),
            cashAndShortTermInvestments=Parser._safe_int(report.get('cashAndShortTermInvestments')),
            inventory=Parser._safe_int(report.get('inventory')),
            currentNetReceivables=Parser._safe_int(report.get('currentNetReceivables')),
            totalNonCurrentAssets=Parser._safe_int(report.get('totalNonCurrentAssets')),
            propertyPlantEquipment=Parser._safe_int(report.get('propertyPlantEquipment')),
            accumulatedDepreciationAmortizationPPE=Parser._safe_int(report.get('accumulatedDepreciationAmortizationPPE')),
            intangibleAssets=Parser._safe_int(report.get('intangibleAssets')),
            intangibleAssetsExcludingGoodwill=Parser._safe_int(report.get('intangibleAssetsExcludingGoodwill')),
            goodwill=Parser._safe_int(report.get('goodwill')),
            investments=Parser._safe_int(report.get('investments')),
            longTermInvestments=Parser._safe_int(report.get('longTermInvestments')),
            shortTermInvestments=Parser._safe_int(report.get('shortTermInvestments')),
            otherCurrentAssets=Parser._safe_int(report.get('otherCurrentAssets')),
            otherNonCurrentAssets=Parser._safe_int(report.get('otherNonCurrentAssets')),
            # Liabilities
            totalLiabilities=Parser._safe_int(report.get('totalLiabilities')),
            totalCurrentLiabilities=Parser._safe_int(report.get('totalCurrentLiabilities')),
            currentAccountsPayable=Parser._safe_int(report.get('currentAccountsPayable')),
            deferredRevenue=Parser._safe_int(report.get('deferredRevenue')),
            currentDebt=Parser._safe_int(report.get('currentDebt')),
            shortTermDebt=Parser._safe_int(report.get('shortTermDebt')),
            totalNonCurrentLiabilities=Parser._safe_int(report.get('totalNonCurrentLiabilities')),
            capitalLeaseObligations=Parser._safe_int(report.get('capitalLeaseObligations')),
            longTermDebt=Parser._safe_int(report.get('longTermDebt')),
            currentLongTermDebt=Parser._safe_int(report.get('currentLongTermDebt')),
            longTermDebtNoncurrent=Parser._safe_int(report.get('longTermDebtNoncurrent')),
            shortLongTermDebtTotal=Parser._safe_int(report.get('shortLongTermDebtTotal')),
            otherCurrentLiabilities=Parser._safe_int(report.get('otherCurrentLiabilities')),
            otherNonCurrentLiabilities=Parser._safe_int(report.get('otherNonCurrentLiabilities')),
            # Equity
            totalShareholderEquity=Parser._safe_int(report.get('totalShareholderEquity')),
            treasuryStock=Parser._safe_int(report.get('treasuryStock')),
            retainedEarnings=Parser._safe_int(report.get('retainedEarnings')),
            commonStock=Parser._safe_int(report.get('commonStock')),
            commonStockSharesOutstanding=Parser._safe_int(report.get('commonStockSharesOutstanding')),
        )

    @staticmethod
    def parse_balance_sheet_data(api_response: dict) -> BalanceSheetData:
        """Convert Alpha Vantage API response to BalanceSheetData object"""
        symbol = api_response.get('symbol', '')

        annual_reports = [
            Parser._parse_balance_sheet_report(report, AnnualBalanceSheetData)
            for report in api_response.get('annualReports', [])
        ]

        quarterly_reports = [
            Parser._parse_balance_sheet_report(report, QuarterlyBalanceSheetData)
            for report in api_response.get('quarterlyReports', [])
        ]

        return BalanceSheetData(
            symbol=symbol,
            annualReports=annual_reports,
            quarterlyReports=quarterly_reports
        )

    @staticmethod
    def _parse_income_statement_report(report: dict, data_class):
        """Helper to parse a single income statement report (annual or quarterly)"""
        return data_class(
            fiscalDateEnding=report.get('fiscalDateEnding', ''),
            reportedCurrency=report.get('reportedCurrency', 'USD'),
            # Revenue & Cost
            grossProfit=Parser._safe_int(report.get('grossProfit')),
            totalRevenue=Parser._safe_int(report.get('totalRevenue')),
            costOfRevenue=Parser._safe_int(report.get('costOfRevenue')),
            costofGoodsAndServicesSold=Parser._safe_int(report.get('costofGoodsAndServicesSold')),
            # Operating
            operatingIncome=Parser._safe_int(report.get('operatingIncome')),
            sellingGeneralAndAdministrative=Parser._safe_int(report.get('sellingGeneralAndAdministrative')),
            researchAndDevelopment=Parser._safe_int(report.get('researchAndDevelopment')),
            operatingExpenses=Parser._safe_int(report.get('operatingExpenses')),
            # Interest & Investment
            investmentIncomeNet=Parser._safe_int(report.get('investmentIncomeNet')),
            netInterestIncome=Parser._safe_int(report.get('netInterestIncome')),
            interestIncome=Parser._safe_int(report.get('interestIncome')),
            interestExpense=Parser._safe_int(report.get('interestExpense')),
            nonInterestIncome=Parser._safe_int(report.get('nonInterestIncome')),
            otherNonOperatingIncome=Parser._safe_int(report.get('otherNonOperatingIncome')),
            interestAndDebtExpense=Parser._safe_int(report.get('interestAndDebtExpense')),
            # Depreciation
            depreciation=Parser._safe_int(report.get('depreciation')),
            depreciationAndAmortization=Parser._safe_int(report.get('depreciationAndAmortization')),
            # Income & Tax
            incomeBeforeTax=Parser._safe_int(report.get('incomeBeforeTax')),
            incomeTaxExpense=Parser._safe_int(report.get('incomeTaxExpense')),
            netIncomeFromContinuingOperations=Parser._safe_int(report.get('netIncomeFromContinuingOperations')),
            comprehensiveIncomeNetOfTax=Parser._safe_int(report.get('comprehensiveIncomeNetOfTax')),
            # EBIT/EBITDA
            ebit=Parser._safe_int(report.get('ebit')),
            ebitda=Parser._safe_int(report.get('ebitda')),
            # Net Income
            netIncome=Parser._safe_int(report.get('netIncome')),
        )

    @staticmethod
    def parse_income_statement_data(api_response: dict) -> IncomeStatementData:
        """Convert Alpha Vantage API response to IncomeStatementData object"""
        symbol = api_response.get('symbol', '')

        annual_reports = [
            Parser._parse_income_statement_report(report, AnnualIncomeStatementData)
            for report in api_response.get('annualReports', [])
        ]

        quarterly_reports = [
            Parser._parse_income_statement_report(report, QuarterlyIncomeStatementData)
            for report in api_response.get('quarterlyReports', [])
        ]

        return IncomeStatementData(
            symbol=symbol,
            annualReports=annual_reports,
            quarterlyReports=quarterly_reports
        )

    @staticmethod
    def _parse_cash_flow_report(report: dict, data_class):
        """Helper to parse a single cash flow report (annual or quarterly)"""
        return data_class(
            fiscalDateEnding=report.get('fiscalDateEnding', ''),
            reportedCurrency=report.get('reportedCurrency', 'USD'),
            # Operating Activities
            operatingCashflow=Parser._safe_int(report.get('operatingCashflow')),
            paymentsForOperatingActivities=Parser._safe_int(report.get('paymentsForOperatingActivities')),
            proceedsFromOperatingActivities=Parser._safe_int(report.get('proceedsFromOperatingActivities')),
            changeInOperatingLiabilities=Parser._safe_int(report.get('changeInOperatingLiabilities')),
            changeInOperatingAssets=Parser._safe_int(report.get('changeInOperatingAssets')),
            depreciationDepletionAndAmortization=Parser._safe_int(report.get('depreciationDepletionAndAmortization')),
            changeInReceivables=Parser._safe_int(report.get('changeInReceivables')),
            changeInInventory=Parser._safe_int(report.get('changeInInventory')),
            profitLoss=Parser._safe_int(report.get('profitLoss')),
            # Investing Activities
            capitalExpenditures=Parser._safe_int(report.get('capitalExpenditures')),
            cashflowFromInvestment=Parser._safe_int(report.get('cashflowFromInvestment')),
            # Financing Activities
            cashflowFromFinancing=Parser._safe_int(report.get('cashflowFromFinancing')),
            proceedsFromRepaymentsOfShortTermDebt=Parser._safe_int(report.get('proceedsFromRepaymentsOfShortTermDebt')),
            paymentsForRepurchaseOfCommonStock=Parser._safe_int(report.get('paymentsForRepurchaseOfCommonStock')),
            paymentsForRepurchaseOfEquity=Parser._safe_int(report.get('paymentsForRepurchaseOfEquity')),
            paymentsForRepurchaseOfPreferredStock=Parser._safe_int(report.get('paymentsForRepurchaseOfPreferredStock')),
            dividendPayout=Parser._safe_int(report.get('dividendPayout')),
            dividendPayoutCommonStock=Parser._safe_int(report.get('dividendPayoutCommonStock')),
            dividendPayoutPreferredStock=Parser._safe_int(report.get('dividendPayoutPreferredStock')),
            proceedsFromIssuanceOfCommonStock=Parser._safe_int(report.get('proceedsFromIssuanceOfCommonStock')),
            proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet=Parser._safe_int(report.get('proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet')),
            proceedsFromIssuanceOfPreferredStock=Parser._safe_int(report.get('proceedsFromIssuanceOfPreferredStock')),
            proceedsFromRepurchaseOfEquity=Parser._safe_int(report.get('proceedsFromRepurchaseOfEquity')),
            proceedsFromSaleOfTreasuryStock=Parser._safe_int(report.get('proceedsFromSaleOfTreasuryStock')),
            # Cash Changes
            changeInCashAndCashEquivalents=Parser._safe_int(report.get('changeInCashAndCashEquivalents')),
            changeInExchangeRate=Parser._safe_int(report.get('changeInExchangeRate')),
            # Net Income
            netIncome=Parser._safe_int(report.get('netIncome')),
        )

    @staticmethod
    def parse_cash_flow_data(api_response: dict) -> CashFlowData:
        """Convert Alpha Vantage API response to CashFlowData object"""
        symbol = api_response.get('symbol', '')

        annual_reports = [
            Parser._parse_cash_flow_report(report, AnnualCashFlowData)
            for report in api_response.get('annualReports', [])
        ]

        quarterly_reports = [
            Parser._parse_cash_flow_report(report, QuarterlyCashFlowData)
            for report in api_response.get('quarterlyReports', [])
        ]

        return CashFlowData(
            symbol=symbol,
            annualReports=annual_reports,
            quarterlyReports=quarterly_reports
        )