import time
from stock_spot.models import AnnualEarning, Stock, QuarterlyEarning
from stock_spot.services.alpha_vantage import AlphaVantageService


class StockService:
    """Service for Stock database operations"""

    def __init__(self):
        self.alpha_vantage_service = AlphaVantageService()

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
        self.alpha_vantage_service.get_price_today(symbol)
        time.sleep(3)  # Alpha Vantage free tier: 5 calls/min, 1 call/second
        self.alpha_vantage_service.get_relative_strength_index_data(symbol)
        time.sleep(3)  # Alpha Vantage free tier: 5 calls/min, 1 call/second
        self.alpha_vantage_service.get_eps_data(symbol)
        # Calculate metrics
        self.calculate_eps_growth_over_past_year(symbol)
        self.calculate_earnings_CAGR(symbol)
        return new_stock

    def calculate_eps_growth_over_past_year(self, symbol):
        """Calculate year-over-year EPS growth from most recent quarterly earnings"""
        try:
            mostRecentQuarterlyEarning = QuarterlyEarning.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
            if not mostRecentQuarterlyEarning or not mostRecentQuarterlyEarning.reportedEPS:
                return None
            priorYearQuarterlyEarning = QuarterlyEarning.objects.filter(
                stock__symbol=symbol,
                fiscalDateEnding__lte=mostRecentQuarterlyEarning.fiscalDateEnding.replace(year=mostRecentQuarterlyEarning.fiscalDateEnding.year - 1)
            ).order_by('-fiscalDateEnding').first()
            if not priorYearQuarterlyEarning or not priorYearQuarterlyEarning.reportedEPS:
                return None
            mostRecentQuarterlyEPS = mostRecentQuarterlyEarning.reportedEPS
            priorYearQuarterlyEPS = priorYearQuarterlyEarning.reportedEPS
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
            span = 5
            annualEarningsDataCount = AnnualEarning.objects.filter(stock__symbol=symbol).count()
            if(span > annualEarningsDataCount):
                span = annualEarningsDataCount
            mostRecentAnnualEarning = AnnualEarning.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
            if not mostRecentAnnualEarning:
                return None
            nYearsAgoAnnualEarning = AnnualEarning.objects.filter(
                stock__symbol=symbol,
                fiscalDateEnding__lte=mostRecentAnnualEarning.fiscalDateEnding.replace(year=mostRecentAnnualEarning.fiscalDateEnding.year - span)
            ).order_by('-fiscalDateEnding').first()
            if not nYearsAgoAnnualEarning:
                return None
            
            # Validate EPS values before calculation
            if not nYearsAgoAnnualEarning.reportedEPS or nYearsAgoAnnualEarning.reportedEPS == 0:
                print(f"Cannot calculate CAGR for {symbol}: historical EPS is zero or null")
                return None
            if not mostRecentAnnualEarning.reportedEPS:
                print(f"Cannot calculate CAGR for {symbol}: recent EPS is null")
                return None
            # CAGR with negative values requires different handling
            if nYearsAgoAnnualEarning.reportedEPS < 0 or mostRecentAnnualEarning.reportedEPS < 0:
                print(f"Cannot calculate CAGR for {symbol}: negative EPS values present")
                return None
            
            cagr = ((float(mostRecentAnnualEarning.reportedEPS/nYearsAgoAnnualEarning.reportedEPS) ** (1/span)) - 1) * 100
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
