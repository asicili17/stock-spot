"""Refresh a stock profile from Alpha Vantage and update its latest display metrics."""

from stock_spot.models import Stock
from stock_spot.services.alpha_vantage import AlphaVantageService
from stock_spot.services.fundamentals import ConservativeValuationCalculator, EarningsGrowthMetricCalculator


class StockProfileRefreshService:
    """Coordinates external profile refreshes without embedding metric formulas."""

    def __init__(self):
        self.alpha_vantage = AlphaVantageService()
        self.earnings_growth = EarningsGrowthMetricCalculator()
        self.conservative_valuation = ConservativeValuationCalculator()

    def refresh(self, symbol: str):
        stock, _ = Stock.objects.get_or_create(symbol=symbol.upper(), defaults={'isBought': False})
        self.alpha_vantage.get_price_today(stock.symbol)
        self.alpha_vantage.get_eps_data(stock.symbol)
        self.alpha_vantage.get_company_overview(stock.symbol)
        self.alpha_vantage.get_income_statement_data(stock.symbol)
        self.alpha_vantage.get_balance_sheet_data(stock.symbol)
        self.alpha_vantage.get_cash_flow_data(stock.symbol)

        stock.refresh_from_db()
        self.earnings_growth.calculate_quarterly_yoy_eps_growth(stock)
        self.earnings_growth.calculate_annual_eps_cagr(stock)
        self.conservative_valuation.calculate(stock)
        stock.refresh_from_db()
        return stock
