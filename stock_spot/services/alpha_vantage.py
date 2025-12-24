from django.conf import settings
import requests
from stock_spot.parser import Parser
from stock_spot.models import Stock, AnnualEarning, QuarterlyEarning
from datetime import datetime


class AlphaVantageService:
    """Service for interacting with Alpha Vantage API"""

    def __init__(self):
        self.base_url = settings.STOCK_API_BASE_URL
        self.api_key = settings.STOCK_API_KEY

    def get_price_today(self, symbol):
        """Fetch current stock price from Alpha Vantage"""
        try:
            response = requests.get(
                f"{self.base_url}/query",
                params={
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            # Extract the price from the response
            price = data.get('Global Quote', {}).get('05. price')
            self._save_price_today(symbol, price)
            return price
        except requests.RequestException as e:
            print(f"Alpha Vantage Error: {e}")
            return None
        
    def _save_price_today(self, symbol, currentPrice):
        """Save current stock price to database"""
        try:
            from decimal import Decimal
            stock = Stock.objects.get(symbol=symbol)
            if currentPrice:
                stock.startingPrice = Decimal(currentPrice)
            stock.save()
            print(f"Price for stock {symbol} saved successfully")
        except Stock.DoesNotExist:
            print(f"Stock {symbol} not found in database")
            return

    def get_eps_data(self, symbol):
        """Fetch EPS data from external Alpha Vantage and save to database"""
        try:
            response = requests.get(
                f"{self.base_url}/query",
                params={
                    'function': 'EARNINGS',
                    'symbol': symbol,
                    'apikey': self.api_key
                }
            )
            response.raise_for_status()
            raw_data = response.json()
            
            # Parse the response
            parsed_data = Parser.parse_eps_data(raw_data)
            
            # Save to database
            self._save_earnings_to_db(symbol, parsed_data)
            
            return parsed_data
        except requests.RequestException as e:
            print(f"Alpha Vantage Error: {e}")
            return None

    def _save_earnings_to_db(self, symbol, parsed_data):
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

    def get_relative_strength_index_data(self, symbol):
        """Fetch RSI data from Alpha Vantage and save to database"""
        try:
            response = requests.get(
                f"{self.base_url}/query",
                params={
                    'function': 'RSI',
                    'symbol': symbol,
                    'interval': 'daily',
                    'time_period': 14,
                    'series_type': 'close',
                    'apikey': self.api_key
                }
            )
            response.raise_for_status()
            rsi_data = response.json()["Technical Analysis: RSI"]
            self._save_first_rsi(symbol, rsi_data)
            return rsi_data
        except Exception as e:
            print(f"Error fetching RSI data for: {symbol}, {e}")
            return None

    def _save_first_rsi(self, symbol, rsi_data):
        """Save the most recent RSI value"""
        try:
            stock = Stock.objects.get(symbol=symbol)
            stock.relativeStrengthIndex = next(iter(rsi_data.values()))["RSI"]
            stock.save()
        except Stock.DoesNotExist:
            print(f"Stock {symbol} not found in database")
            return
        print(f"RSI for stock {symbol} saved successfully")
