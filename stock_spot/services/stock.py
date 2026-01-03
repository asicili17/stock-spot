import time
from stock_spot.models import AnnualEarning, AnnualIncomeStatement, QuarterlyIncomeStatement, Stock, QuarterlyEarning
from stock_spot.services.alpha_vantage import AlphaVantageService
from stock_spot.services.yfinance import YFinanceService


class StockService:
    """Service for Stock database operations"""

    def __init__(self):
        self.alpha_vantage_service = AlphaVantageService()
        self.yfinance_service = YFinanceService()

    def get_stock_by_symbol(self, symbol):
        """Retrieve stock from database by symbol"""
        return Stock.objects.get(symbol=symbol)

    def get_all_stocks(self):
        """Retrieve all stocks from database"""
        return Stock.objects.all()
    
    def get_most_recent_RSI(self, symbol):
        """Get most recent RSI for the given stock as of today"""
        return Stock.objects.get(symbol=symbol).relativeStrengthIndex

    def create_stock(self, symbol):
        """Create a new stock entry"""
        new_stock = Stock.objects.create(
            name=None,
            symbol=symbol,
            startingPrice=None,
            currentPrice=None,
            priceWhenBought=None,
            isBought=False,
            sharesOwned=None,
            relativeStrengthIndex=None,
            yoyEPSPercentGrowth=None,
            compoundedAnnualGrowthRate=None
        )
        new_stock.save()

        # Fetch and save external data (with delays to avoid API rate limiting)
        self.yfinance_service.get_stock_info(symbol)
        self.yfinance_service.get_annual_balance_sheet_data(symbol)
        self.yfinance_service.get_quarterly_balance_sheet_data(symbol)
        self.yfinance_service.get_annual_cashflow_data(symbol)
        self.yfinance_service.get_quarterly_cashflow_data(symbol)
        self.yfinance_service.get_annual_income_statement_data(symbol)
        self.yfinance_service.get_quarterly_income_statement_data(symbol)
        self.alpha_vantage_service.get_relative_strength_index_data(symbol)

        # Calculate metrics
        self.calculate_eps_growth_over_past_year(symbol)
        self.calculate_earnings_CAGR(symbol)
        return new_stock

    def calculate_eps_growth_over_past_year(self, symbol):
        """Calculate year-over-year EPS growth from most recent quarterly earnings"""
        try:
            mostRecentQuarterlyEarning = QuarterlyIncomeStatement.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
            if not mostRecentQuarterlyEarning or not mostRecentQuarterlyEarning.dilutedEPS:
                return None
            priorYearQuarterlyEarning = QuarterlyIncomeStatement.objects.filter(
                stock__symbol=symbol,
                fiscalDateEnding__lte=mostRecentQuarterlyEarning.fiscalDateEnding.replace(year=mostRecentQuarterlyEarning.fiscalDateEnding.year - 1)
            ).order_by('-fiscalDateEnding').first()
            if not priorYearQuarterlyEarning or not priorYearQuarterlyEarning.dilutedEPS:
                return None
            mostRecentQuarterlyEPS = mostRecentQuarterlyEarning.dilutedEPS
            priorYearQuarterlyEPS = priorYearQuarterlyEarning.dilutedEPS
            yoyEPSGrowth = ((mostRecentQuarterlyEPS-priorYearQuarterlyEPS)/priorYearQuarterlyEPS)*100
            stock = Stock.objects.get(symbol=symbol)
            stock.yoyEPSPercentGrowth = yoyEPSGrowth
            stock.save()
            return yoyEPSGrowth
        except Exception as e:
            print(f"Error calculating YoY EPS growth for {symbol}: {e}")
            return None


    def calculate_earnings_CAGR(self, symbol):
        """Calculate compounded annual earnings growth rate from 4-5 year interval"""
        try:
            span = 4
            annualEarningsDataCount = AnnualIncomeStatement.objects.filter(stock__symbol=symbol).count()
            if(span > annualEarningsDataCount):
                span = annualEarningsDataCount
            mostRecentAnnualEarning = AnnualIncomeStatement.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
            if not mostRecentAnnualEarning:
                return None
            nYearsAgoAnnualEarning = AnnualIncomeStatement.objects.filter(
                stock__symbol=symbol,
                fiscalDateEnding__gte=mostRecentAnnualEarning.fiscalDateEnding.replace(year=mostRecentAnnualEarning.fiscalDateEnding.year - (span-1))
            ).order_by('-fiscalDateEnding').last()
            if not nYearsAgoAnnualEarning:
                return None
            
            print(mostRecentAnnualEarning.dilutedEPS)
            print(nYearsAgoAnnualEarning.dilutedEPS)
            # Validate EPS values before calculation
            if not nYearsAgoAnnualEarning.dilutedEPS or nYearsAgoAnnualEarning.dilutedEPS == 0:
                print(f"Cannot calculate CAGR for {symbol}: historical EPS is zero or null")
                return None
            if not mostRecentAnnualEarning.dilutedEPS:
                print(f"Cannot calculate CAGR for {symbol}: recent EPS is null")
                return None
            # CAGR with negative values requires different handling
            if nYearsAgoAnnualEarning.dilutedEPS < 0 or mostRecentAnnualEarning.dilutedEPS < 0:
                print(f"Cannot calculate CAGR for {symbol}: negative EPS values present")
                return None
            
            cagr = ((float(mostRecentAnnualEarning.dilutedEPS/nYearsAgoAnnualEarning.dilutedEPS) ** (1/span)) - 1) * 100
            stock = Stock.objects.get(symbol=symbol)
            stock.compoundedAnnualGrowthRate = cagr
            stock.save()
            return cagr
        except Exception as e:
            print(f"Error calculating earnings CAGR for {symbol}: {e}")
            return None

    # TODO: Implement additional methods
    # def calculate_cagr(stock):
    # def get_strength_score(stock):
