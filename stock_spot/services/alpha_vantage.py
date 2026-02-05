import logging
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.db import transaction
import requests

from stock_spot.models import (
    Stock, AnnualEarning, QuarterlyEarning,
    AnnualBalanceSheet, QuarterlyBalanceSheet,
    AnnualIncomeStatement, QuarterlyIncomeStatement,
    AnnualCashFlow, QuarterlyCashFlow
)

logger = logging.getLogger(__name__)

class AlphaVantageError(Exception):
    """Custom exception for Alpha Vantage API errors"""
    pass


class StockNotFoundError(Exception):
    """Raised when a stock symbol is not found in the database"""
    pass


class AlphaVantageService:
    """Service for interacting with Alpha Vantage API"""

    # Field definitions for each financial statement type
    BALANCE_SHEET_FIELDS = [
        'totalAssets', 'totalCurrentAssets', 'cashAndCashEquivalentsAtCarryingValue',
        'cashAndShortTermInvestments', 'inventory', 'currentNetReceivables',
        'totalNonCurrentAssets', 'propertyPlantEquipment', 'accumulatedDepreciationAmortizationPPE',
        'intangibleAssets', 'intangibleAssetsExcludingGoodwill', 'goodwill',
        'investments', 'longTermInvestments', 'shortTermInvestments',
        'otherCurrentAssets', 'otherNonCurrentAssets', 'totalLiabilities',
        'totalCurrentLiabilities', 'currentAccountsPayable', 'deferredRevenue',
        'currentDebt', 'shortTermDebt', 'totalNonCurrentLiabilities',
        'capitalLeaseObligations', 'longTermDebt', 'currentLongTermDebt',
        'longTermDebtNoncurrent', 'shortLongTermDebtTotal', 'otherCurrentLiabilities',
        'otherNonCurrentLiabilities', 'totalShareholderEquity', 'treasuryStock',
        'retainedEarnings', 'commonStock', 'commonStockSharesOutstanding',
    ]

    INCOME_STATEMENT_FIELDS = [
        'grossProfit', 'totalRevenue', 'costOfRevenue', 'costofGoodsAndServicesSold',
        'operatingIncome', 'sellingGeneralAndAdministrative', 'researchAndDevelopment',
        'operatingExpenses', 'investmentIncomeNet', 'netInterestIncome',
        'interestIncome', 'interestExpense', 'nonInterestIncome',
        'otherNonOperatingIncome', 'interestAndDebtExpense', 'depreciation',
        'depreciationAndAmortization', 'incomeBeforeTax', 'incomeTaxExpense',
        'netIncomeFromContinuingOperations', 'comprehensiveIncomeNetOfTax',
        'ebit', 'ebitda', 'netIncome',
    ]

    CASH_FLOW_FIELDS = [
        'operatingCashflow', 'paymentsForOperatingActivities', 'proceedsFromOperatingActivities',
        'changeInOperatingLiabilities', 'changeInOperatingAssets', 'depreciationDepletionAndAmortization',
        'changeInReceivables', 'changeInInventory', 'profitLoss',
        'capitalExpenditures', 'cashflowFromInvestment', 'cashflowFromFinancing',
        'proceedsFromRepaymentsOfShortTermDebt', 'paymentsForRepurchaseOfCommonStock',
        'paymentsForRepurchaseOfEquity', 'paymentsForRepurchaseOfPreferredStock',
        'dividendPayout', 'dividendPayoutCommonStock', 'dividendPayoutPreferredStock',
        'proceedsFromIssuanceOfCommonStock', 'proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet',
        'proceedsFromIssuanceOfPreferredStock', 'proceedsFromRepurchaseOfEquity',
        'proceedsFromSaleOfTreasuryStock', 'changeInCashAndCashEquivalents',
        'changeInExchangeRate', 'netIncome',
    ]

    def __init__(self):
        self.base_url = settings.STOCK_API_BASE_URL
        self.api_key = settings.STOCK_API_KEY

    # ==================== Helper Methods ====================

    def _safe_int(self, value):
        """Safely convert value to int, returns 0 for invalid values"""
        if value is None or value == 'None' or value == '':
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def _safe_float(self, value):
        """Safely convert value to float, returns 0.0 for invalid values"""
        if value is None or value == 'None' or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _safe_decimal(self, value):
        """Safely convert value to Decimal, returns Decimal('0') for invalid values"""
        if value is None or value == 'None' or value == '':
            return Decimal('0')
        try:
            return Decimal(value)
        except (ValueError, TypeError):
            return Decimal('0')

    def _get_stock(self, symbol: str) -> Stock:
        """Get stock by symbol or raise StockNotFoundError"""
        try:
            return Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            raise StockNotFoundError(f"Stock '{symbol}' not found in database")

    def _make_api_request(self, params: dict) -> dict:
        """Make API request to Alpha Vantage and return JSON response"""
        try:
            response = requests.get(
                f"{self.base_url}/query",
                params={**params, 'apikey': self.api_key}
            )
            response.raise_for_status()
            data = response.json()

            # Check for API error responses
            if 'Error Message' in data:
                raise AlphaVantageError(f"API Error: {data['Error Message']}")
            if 'Note' in data:
                raise AlphaVantageError(f"API Rate Limit: {data['Note']}")
            if 'Information' in data:
                raise AlphaVantageError(f"API Info: {data['Information']}")

            return data
        except requests.RequestException as e:
            raise AlphaVantageError(f"Request failed: {e}")

    def _save_report(self, stock: Stock, report_data: dict, model_class, int_fields: list):
        """Generic method to save a financial report to database"""
        fiscal_date = datetime.strptime(report_data['fiscalDateEnding'], '%Y-%m-%d').date()

        defaults = {'reportedCurrency': report_data.get('reportedCurrency', 'USD')}
        for field in int_fields:
            defaults[field] = self._safe_int(report_data.get(field))

        model_class.objects.update_or_create(
            stock=stock,
            fiscalDateEnding=fiscal_date,
            defaults=defaults
        )

    def _save_financial_data(self, symbol: str, data: dict, annual_model, quarterly_model, fields: list):
        """Generic method to save annual and quarterly financial data"""
        stock = self._get_stock(symbol)

        with transaction.atomic():
            # Save annual reports
            for report in data.get('annualReports', []):
                self._save_report(stock, report, annual_model, fields)

            # Save quarterly reports
            for report in data.get('quarterlyReports', []):
                self._save_report(stock, report, quarterly_model, fields)

        logger.info(f"Saved {annual_model.__name__} and {quarterly_model.__name__} for {symbol}")

    # ==================== Company Overview ====================

    def get_company_overview(self, symbol: str) -> dict:
        """Fetch company overview from Alpha Vantage"""
        try:
            data = self._make_api_request({'function': 'OVERVIEW', 'symbol': symbol})
            self._save_company_overview(symbol, data)
            return data
        except (AlphaVantageError, StockNotFoundError) as e:
            logger.error(f"Failed to get company overview for {symbol}: {e}")
            raise

    def _save_company_overview(self, symbol: str, overview_data: dict):
        """Save company overview data to database"""
        stock = self._get_stock(symbol)
        stock.companySummary = overview_data.get('Description', '')
        stock.sector = overview_data.get('Sector', '')
        stock.marketCap = overview_data.get('MarketCapitalization', '')
        stock.save()
        logger.info(f"Saved company overview for {symbol}")

    # ==================== Price ====================

    def get_price_today(self, symbol: str) -> Decimal | None:
        """Fetch current stock price from Alpha Vantage"""
        try:
            data = self._make_api_request({'function': 'GLOBAL_QUOTE', 'symbol': symbol})
            price = data.get('Global Quote', {}).get('05. price')
            self._save_price_today(symbol, price)
            return self._safe_decimal(price)
        except (AlphaVantageError, StockNotFoundError) as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            raise

    def _save_price_today(self, symbol: str, current_price):
        """Save current stock price to database"""
        stock = self._get_stock(symbol)
        price = self._safe_decimal(current_price)
        if price:
            stock.startingPrice = price
            stock.currentPrice = price
            stock.save()
            logger.info(f"Saved price {price} for {symbol}")

    # ==================== Earnings ====================

    def get_eps_data(self, symbol: str) -> dict:
        """Fetch EPS data from Alpha Vantage and save to database"""
        try:
            data = self._make_api_request({'function': 'EARNINGS', 'symbol': symbol})
            self._save_earnings_to_db(symbol, data)
            return data
        except (AlphaVantageError, StockNotFoundError) as e:
            logger.error(f"Failed to get EPS data for {symbol}: {e}")
            raise

    def _save_earnings_to_db(self, symbol: str, data: dict):
        """Save earnings data to database"""
        stock = self._get_stock(symbol)

        with transaction.atomic():
            # Save annual earnings
            for annual in data.get('annualEarnings', []):
                fiscal_date = datetime.strptime(annual['fiscalDateEnding'], '%Y-%m-%d').date()
                AnnualEarning.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={'reportedEPS': self._safe_float(annual.get('reportedEPS'))}
                )

            # Save quarterly earnings
            for quarterly in data.get('quarterlyEarnings', []):
                fiscal_date = datetime.strptime(quarterly['fiscalDateEnding'], '%Y-%m-%d').date()
                reported_date = datetime.strptime(quarterly['reportedDate'], '%Y-%m-%d').date()
                QuarterlyEarning.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'reportedDate': reported_date,
                        'reportedEPS': self._safe_float(quarterly.get('reportedEPS')),
                        'estimatedEPS': self._safe_float(quarterly.get('estimatedEPS')),
                        'surprise': self._safe_float(quarterly.get('surprise')),
                        'surprisePercentage': self._safe_float(quarterly.get('surprisePercentage')),
                        'reportTime': quarterly.get('reportTime', '')
                    }
                )

        logger.info(f"Saved earnings data for {symbol}")

    # ==================== Balance Sheet ====================

    def get_balance_sheet_data(self, symbol: str) -> dict:
        """Fetch balance sheet data from Alpha Vantage and save to database"""
        try:
            data = self._make_api_request({'function': 'BALANCE_SHEET', 'symbol': symbol})
            self._save_financial_data(
                symbol, data,
                AnnualBalanceSheet, QuarterlyBalanceSheet,
                self.BALANCE_SHEET_FIELDS
            )
            return data
        except (AlphaVantageError, StockNotFoundError) as e:
            logger.error(f"Failed to get balance sheet for {symbol}: {e}")
            raise

    # ==================== Income Statement ====================

    def get_income_statement_data(self, symbol: str) -> dict:
        """Fetch income statement data from Alpha Vantage and save to database"""
        try:
            data = self._make_api_request({'function': 'INCOME_STATEMENT', 'symbol': symbol})
            self._save_financial_data(
                symbol, data,
                AnnualIncomeStatement, QuarterlyIncomeStatement,
                self.INCOME_STATEMENT_FIELDS
            )
            return data
        except (AlphaVantageError, StockNotFoundError) as e:
            logger.error(f"Failed to get income statement for {symbol}: {e}")
            raise

    # ==================== Cash Flow ====================

    def get_cash_flow_data(self, symbol: str) -> dict:
        """Fetch cash flow data from Alpha Vantage and save to database"""
        try:
            data = self._make_api_request({'function': 'CASH_FLOW', 'symbol': symbol})
            self._save_financial_data(
                symbol, data,
                AnnualCashFlow, QuarterlyCashFlow,
                self.CASH_FLOW_FIELDS
            )
            return data
        except (AlphaVantageError, StockNotFoundError) as e:
            logger.error(f"Failed to get cash flow for {symbol}: {e}")
            raise

    # ==================== RSI ====================

    def get_relative_strength_index_data(self, symbol: str) -> dict:
        """Fetch RSI data from Alpha Vantage and save to database"""
        try:
            data = self._make_api_request({
                'function': 'RSI',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 14,
                'series_type': 'close',
            })

            if "Technical Analysis: RSI" not in data:
                raise AlphaVantageError(f"Unexpected RSI response format for {symbol}")

            rsi_data = data["Technical Analysis: RSI"]
            self._save_first_rsi(symbol, rsi_data)
            return rsi_data
        except (AlphaVantageError, StockNotFoundError) as e:
            logger.error(f"Failed to get RSI for {symbol}: {e}")
            raise

    def _save_first_rsi(self, symbol: str, rsi_data: dict):
        """Save the most recent RSI value"""
        stock = self._get_stock(symbol)
        stock.relativeStrengthIndex = next(iter(rsi_data.values()))["RSI"]
        stock.save()
        logger.info(f"Saved RSI for {symbol}")
