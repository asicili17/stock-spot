"""A transparent implementation of Stock Spot's conservative valuation heuristic."""

from dataclasses import dataclass
from decimal import Decimal

from stock_spot.models import AnnualBalanceSheet, AnnualIncomeStatement, Stock


@dataclass(frozen=True)
class ConservativeValuationComponents:
    tangible_net_assets: int
    normalized_earnings: int
    estimated_value: int


class ConservativeValuationCalculator:
    """Calculate tangible net assets plus ten times normalized earnings.

    This preserves the project's existing heuristic while making its assumptions
    explicit. It uses only Alpha Vantage fields: stock-based compensation is not
    added because the prior implementation obtained it from Yahoo Finance.
    """

    EARNINGS_MULTIPLE = 10

    def calculate(self, stock: Stock):
        balance_sheet = AnnualBalanceSheet.objects.filter(stock=stock).order_by('-fiscalDateEnding').first()
        income_statement = AnnualIncomeStatement.objects.filter(stock=stock).order_by('-fiscalDateEnding').first()
        if balance_sheet is None or income_statement is None:
            return None
        required_values = {
            'total assets': balance_sheet.totalAssets,
            'total liabilities': balance_sheet.totalLiabilities,
            'continuing-operations income': income_statement.netIncomeFromContinuingOperations,
        }
        if any(value is None for value in required_values.values()):
            return None

        tangible_net_assets = (
            balance_sheet.totalAssets
            - (balance_sheet.goodwill or 0)
            - (balance_sheet.intangibleAssets or 0)
            - balance_sheet.totalLiabilities
        )
        normalized_earnings = (
            income_statement.netIncomeFromContinuingOperations
            + (income_statement.depreciationAndAmortization or 0)
        )
        estimated_value = tangible_net_assets + self.EARNINGS_MULTIPLE * normalized_earnings
        stock.conservativeCompanyValuation = estimated_value
        stock.save(update_fields=['conservativeCompanyValuation'])
        return ConservativeValuationComponents(
            tangible_net_assets=tangible_net_assets,
            normalized_earnings=normalized_earnings,
            estimated_value=estimated_value,
        )
