from django.conf import settings
import requests
from stock_spot.parser import Parser
from stock_spot.models import Stock, AnnualEarning, QuarterlyEarning
from datetime import datetime


class AlphaVantageService:
    """Service for interacting with Alpha Vantage API"""

    BASE_URL = settings.STOCK_API_BASE_URL
    API_KEY = settings.STOCK_API_KEY

    @staticmethod
    def get_eps_change(symbol):
        """Fetch EPS data from external Alpha Vantage and save to database"""
        try:
            response = requests.get(
                f"{AlphaVantageService.BASE_URL}/query",
                params={
                    'function': 'EARNINGS',
                    'symbol': symbol,
                    'apikey': AlphaVantageService.API_KEY
                }
            )
            response.raise_for_status()
            raw_data = response.json()
            
            # Parse the response
            parsed_data = Parser.parse_eps_data(raw_data)
            
            # Save to database
            AlphaVantageService._save_earnings_to_db(symbol, parsed_data)
            
            return parsed_data
        except requests.RequestException as e:
            print(f"Alpha Vantage Error: {e}")
            return None

    @staticmethod
    def _save_earnings_to_db(symbol, parsed_data):
        """Save parsed earnings data to database"""
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            print(f"Stock {symbol} not found in database")
            return
        
        # Save annual earnings
        for annual in parsed_data.annualEarnings:
            try:
                fiscal_date = datetime.strptime(annual.fiscalDateEnding, '%Y-%m-%d').date()
                AnnualEarning.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={'reportedEPS': annual.reportedEPS}
                )
            except Exception as e:
                print(f"Error saving annual earning: {e}")
        
        # Save quarterly earnings
        for quarterly in parsed_data.quarterlyEarnings:
            try:
                fiscal_date = datetime.strptime(quarterly.fiscalDateEnding, '%Y-%m-%d').date()
                reported_date = datetime.strptime(quarterly.reportedDate, '%Y-%m-%d').date()
                QuarterlyEarning.objects.update_or_create(
                    stock=stock,
                    fiscalDateEnding=fiscal_date,
                    defaults={
                        'reportedDate': reported_date,
                        'reportedEPS': quarterly.reportedEPS,
                        'estimatedEPS': quarterly.estimatedEPS,
                        'surprise': quarterly.surprise,
                        'surprisePercentage': quarterly.surprisePercentage,
                        'reportTime': quarterly.reportTime
                    }
                )
            except Exception as e:
                print(f"Error saving quarterly earning: {e}")

    @staticmethod
    def get_price_today(symbol):
        """Fetch current stock price from Alpha Vantage"""
        try:
            response = requests.get(
                f"{AlphaVantageService.BASE_URL}/query",
                params={
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': AlphaVantageService.API_KEY
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Alpha Vantage Error: {e}")
            return None
