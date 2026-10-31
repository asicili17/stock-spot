from datetime import date
from decimal import Decimal
from django.test import TestCase
from stock_spot.models import AnnualBalanceSheet, AnnualEarning, AnnualIncomeStatement, QuarterlyEarning, Stock
from stock_spot.services.fundamentals import ConservativeValuationCalculator, EarningsGrowthMetricCalculator
class FundamentalMetricCalculatorTests(TestCase):
    def test_earnings_growth_uses_matching_periods_and_elapsed_years(self):
        stock=Stock.objects.create(symbol='METR',isBought=False)
        QuarterlyEarning.objects.create(stock=stock,fiscalDateEnding=date(2024,3,31),reportedDate=date(2024,4,20),reportedEPS=2,reportTime='bmo'); QuarterlyEarning.objects.create(stock=stock,fiscalDateEnding=date(2025,3,31),reportedDate=date(2025,4,20),reportedEPS=3,reportTime='bmo')
        AnnualEarning.objects.create(stock=stock,fiscalDateEnding=date(2021,12,31),reportedEPS=1); AnnualEarning.objects.create(stock=stock,fiscalDateEnding=date(2025,12,31),reportedEPS=2)
        calculator=EarningsGrowthMetricCalculator()
        self.assertEqual(calculator.calculate_quarterly_yoy_eps_growth(stock),Decimal('50')); self.assertAlmostEqual(float(calculator.calculate_annual_eps_cagr(stock)),18.92,places=2)
    def test_conservative_valuation_exposes_components(self):
        stock=Stock.objects.create(symbol='VAL2',isBought=False)
        AnnualBalanceSheet.objects.create(stock=stock,fiscalDateEnding=date(2025,12,31),totalAssets=1000,goodwill=100,intangibleAssets=50,totalLiabilities=500); AnnualIncomeStatement.objects.create(stock=stock,fiscalDateEnding=date(2025,12,31),netIncomeFromContinuingOperations=100,depreciationAndAmortization=20)
        components=ConservativeValuationCalculator().calculate(stock)
        self.assertEqual((components.tangible_net_assets,components.normalized_earnings,components.estimated_value),(350,120,1550))
