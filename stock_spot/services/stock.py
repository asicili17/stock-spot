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

    def create_stock(self, name, symbol, is_bought, shares_owned):
        """Create a new stock entry"""
        new_stock = Stock.objects.create(
            name=name,
            symbol=symbol,
            startingPrice=None,
            priceWhenBought=None,
            isBought=is_bought,
            sharesOwned=shares_owned,
            relativeStrengthIndex=None,
            yoyEPSPercentGrowth=None,
            compoundedAnnualGrowthRate=None
        )
        new_stock.save()
        # Fetch and save external data
        price = self.alpha_vantage_service.get_price_today(symbol)
        rsi = self.alpha_vantage_service.get_relative_strength_index_data(symbol)
        self.alpha_vantage_service.get_eps_data(symbol)
        # Update stock with fetched data
        if price:
            new_stock.startingPrice = price
        if rsi:
            new_stock.relativeStrengthIndex = rsi
        new_stock.save()
        # Calculate metrics
        self.calculate_eps_growth_over_past_year(symbol)
        self.calculate_earnings_CAGR(symbol)
        return new_stock

    def calculate_eps_growth_over_past_year(self, symbol):
        """Calculate year-over-year EPS growth from most recent quarterly earnings"""
        mostRecentQuarterlyEarning = QuarterlyEarning.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
        if not mostRecentQuarterlyEarning:
            return None
        priorYearQuarterlyEarning = QuarterlyEarning.objects.filter(
            stock__symbol=symbol,
            fiscalDateEnding__lte=mostRecentQuarterlyEarning.fiscalDateEnding.replace(year=mostRecentQuarterlyEarning.fiscalDateEnding.year - 1)
        ).order_by('-fiscalDateEnding').first()
        mostRecentQuarterlyEPS = mostRecentQuarterlyEarning.reportedEPS
        priorYearQuarterlyEPS = priorYearQuarterlyEarning.reportedEPS
        print(mostRecentQuarterlyEPS)
        print(priorYearQuarterlyEPS)
        yoyEPSGrowth = ((mostRecentQuarterlyEPS-priorYearQuarterlyEPS)/priorYearQuarterlyEPS)*100
        print(yoyEPSGrowth)
        stock = Stock.objects.get(symbol=symbol)
        stock.yoyEPSPercentGrowth = yoyEPSGrowth
        stock.save()
        return yoyEPSGrowth


    def calculate_earnings_CAGR(self, symbol):
        """Calculate compounded annual earnings growth rate from 4-5 year interval"""
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
        cagr = (float(mostRecentAnnualEarning.reportedEPS/nYearsAgoAnnualEarning.reportedEPS) ** (1/span)) - 1
        stock = Stock.objects.get(symbol=symbol)
        stock.compoundedAnnualGrowthRate = cagr
        stock.save()
        return cagr

    # TODO: Implement additional methods
    # def calculate_cagr(stock):
    # def get_strength_score(stock):
