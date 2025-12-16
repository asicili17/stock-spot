from stock_spot.models import Stock, QuarterlyEarning


class StockService:
    """Service for Stock database operations"""

    @staticmethod
    def get_stock_by_symbol(symbol):
        """Retrieve stock from database by symbol"""
        return Stock.objects.get(symbol=symbol)

    @staticmethod
    def get_all_stocks():
        """Retrieve all stocks from database"""
        return Stock.objects.all()

    @staticmethod
    def create_stock(name, symbol, starting_price, price_when_bought, is_bought, shares_owned):
        """Create a new stock entry"""
        return Stock.objects.create(
            name=name,
            symbol=symbol,
            startingPrice=starting_price,
            priceWhenBought=price_when_bought,
            isBought=is_bought,
            sharesOwned=shares_owned
        )

    @staticmethod
    def calculate_eps_growth_over_past_year(stock):
        mostRecentQuarterlyEarning = QuarterlyEarning.objects.filter(stock=stock).order_by('-fiscalDateEnding').first()
        priorYearQuarterlyEarning = QuarterlyEarning.objects.filter(
            stock=stock,
            fiscalDateEnding__lte=mostRecentQuarterlyEarning.fiscalDateEnding.replace(year=mostRecentQuarterlyEarning.fiscalDateEnding.year - 1)
        ).order_by('-fiscalDateEnding').first()
        mostRecentQuarterlyEPS = mostRecentQuarterlyEarning.reportedEPS
        priorYearQuarterlyEPS = priorYearQuarterlyEarning.reportedEPS
        print(mostRecentQuarterlyEPS)
        print(priorYearQuarterlyEPS)
        yoyEPSGrowth = ((mostRecentQuarterlyEPS-priorYearQuarterlyEPS)/priorYearQuarterlyEPS)*100
        print(yoyEPSGrowth)
        return yoyEPSGrowth

    # TODO: Implement additional methods
    # def calculate_cagr(stock):
    # def get_strength_score(stock):
