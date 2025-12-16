from stock_spot.schemas import EarningsData, AnnualEarningsData, QuarterlyEarningsData


class Parser:
    @staticmethod
    def _safe_float(value):
        """Safely convert value to float, returns None if value is None or 'None' string"""
        if value is None or value == 'None' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def parse_eps_data(api_response: dict) -> EarningsData:
        """Convert Alpha Vantage API response to EarningsData object"""
        
        # Extract symbol from response
        symbol = api_response.get('symbol', '')
        
        # Parse annual earnings - convert list of dicts to list of AnnualEarningsData objects
        annual_earnings_list = []
        for annual in api_response.get('annualEarnings', []):
            annual_obj = AnnualEarningsData(
                fiscalDateEnding=annual.get('fiscalDateEnding', ''),
                reportedEPS=Parser._safe_float(annual.get('reportedEPS'))
            )
            annual_earnings_list.append(annual_obj)
        
        # Parse quarterly earnings - convert list of dicts to list of QuarterlyEarningsData objects
        quarterly_earnings_list = []
        for quarterly in api_response.get('quarterlyEarnings', []):
            quarterly_obj = QuarterlyEarningsData(
                fiscalDateEnding=quarterly.get('fiscalDateEnding', ''),
                reportedDate=quarterly.get('reportedDate', ''),
                reportedEPS=Parser._safe_float(quarterly.get('reportedEPS')),
                estimatedEPS=Parser._safe_float(quarterly.get('estimatedEPS')),
                surprise=Parser._safe_float(quarterly.get('surprise')),
                surprisePercentage=Parser._safe_float(quarterly.get('surprisePercentage')),
                reportTime=quarterly.get('reportTime', '')
            )
            quarterly_earnings_list.append(quarterly_obj)
        
        # Create and return EarningsData object with all parsed data
        return EarningsData(
            symbol=symbol,
            annualEarnings=annual_earnings_list,
            quarterlyEarnings=quarterly_earnings_list
        )
        