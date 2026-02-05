import time
from decimal import Decimal
from stock_spot.models import AnnualEarning, AnnualIncomeStatement, QuarterlyIncomeStatement, Stock, QuarterlyEarning, AnnualBalanceSheet, AnnualCashFlow
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

    def create_yfinance_stock_profile(self, symbol):
        """Create a new stock entry or update existing one with latest data"""
        stock, created = Stock.objects.update_or_create(
            symbol=symbol,
            defaults={
                'isBought': False if not Stock.objects.filter(symbol=symbol).exists() else Stock.objects.get(symbol=symbol).isBought,
            }
        )
        
        # Preserve existing user-set fields if updating
        if not created:
            # Keep existing user-controlled fields (don't overwrite with defaults)
            pass

        # Fetch and save external data (these already use update_or_create internally)
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
        self.calculate_conservative_company_valuation(symbol)
        
        # Refresh from DB to get all updated fields
        stock.refresh_from_db()
        return stock

    def create_alphavantage_stock_profile(self, symbol):
        """Create a new stock entry or update existing one with latest data"""
        stock, created = Stock.objects.update_or_create(
            symbol=symbol,
            defaults={
                'isBought': False if not Stock.objects.filter(symbol=symbol).exists() else Stock.objects.get(symbol=symbol).isBought,
            }
        )
        
        # Preserve existing user-set fields if updating
        if not created:
            # Keep existing user-controlled fields (don't overwrite with defaults)
            pass

        # Fetch and save external data (these already use update_or_create internally)
        self.alpha_vantage_service.get_price_today(symbol)
        time.sleep(20)  # Alpha Vantage free tier: 5 calls/min, 1 call/second
        self.alpha_vantage_service.get_eps_data(symbol)
        time.sleep(20)
        self.alpha_vantage_service.get_company_overview(symbol)
        time.sleep(20)
        self.alpha_vantage_service.get_income_statement_data(symbol)
        time.sleep(20)
        self.alpha_vantage_service.get_balance_sheet_data(symbol)
        time.sleep(20)
        self.alpha_vantage_service.get_cash_flow_data(symbol)
        time.sleep(20)  
        self.alpha_vantage_service.get_relative_strength_index_data(symbol)
    
        # Calculate metrics
        self.calculate_eps_growth_over_past_year(symbol)
        self.calculate_earnings_CAGR(symbol)
        self.calculate_conservative_company_valuation(symbol)

        return stock

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
            span = 4
            annualEarningsDataCount = AnnualEarning.objects.filter(stock__symbol=symbol).count()
            if(span > annualEarningsDataCount):
                span = annualEarningsDataCount
            mostRecentAnnualEarning = AnnualEarning.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
            if not mostRecentAnnualEarning:
                return None
            nYearsAgoAnnualEarning = AnnualEarning.objects.filter(
                stock__symbol=symbol,
                fiscalDateEnding__gte=mostRecentAnnualEarning.fiscalDateEnding.replace(year=mostRecentAnnualEarning.fiscalDateEnding.year - (span-1))
            ).order_by('-fiscalDateEnding').last()
            if not nYearsAgoAnnualEarning:
                return None
            
            print(mostRecentAnnualEarning.reportedEPS)
            print(nYearsAgoAnnualEarning.reportedEPS)
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

    def calculate_conservative_company_valuation(self, symbol):
        """Calculate a conservative valuation for the company based on earnings and shares outstanding"""
        try:
            latest_balance_sheet = AnnualBalanceSheet.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
            latest_cashflow_statement = AnnualCashFlow.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()
            latest_income_statement = AnnualIncomeStatement.objects.filter(stock__symbol=symbol).order_by('-fiscalDateEnding').first()

            # Check if required data exists
            if not latest_balance_sheet or not latest_cashflow_statement or not latest_income_statement:
                print(f"Cannot calculate conservative company valuation for {symbol}: missing financial statements")
                return None
            
            # Get required fields (already validated above)
            assets = latest_balance_sheet.totalAssets
            liabilities = latest_balance_sheet.totalLiabilities
            netIncomeFromOperations = latest_income_statement.netIncomeFromContinuingOperations # TODO:Check on this field
            
            # Optional fields: check if present before using
            goodwill = latest_balance_sheet.goodwill
            intangibles = latest_balance_sheet.intangibleAssets
            depreciationAndAmortization = latest_income_statement.depreciationAndAmortization
            stockBasedCompensation = self.yfinance_service.get_latest_stock_based_comp(symbol) # Does not exist in Alpha Vantage data

            # Calculate net worth and earnings
            net_worth = assets - goodwill - intangibles - liabilities
            earnings = netIncomeFromOperations + depreciationAndAmortization + stockBasedCompensation

            # Calculate conservative valuation (Django will auto-convert to Decimal when saving)
            conservative_company_valuation = net_worth + (earnings * 10)

            stock = Stock.objects.get(symbol=symbol)
            stock.conservativeCompanyValuation = conservative_company_valuation
            stock.save()

            return conservative_company_valuation
        except Exception as e:
            print(f"Error calculating conservative company valuation for {symbol}: {e}")
            return None