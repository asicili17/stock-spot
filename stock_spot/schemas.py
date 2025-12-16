from dataclasses import dataclass

@dataclass
class AnnualEarningsData:
    fiscalDateEnding: str
    reportedEPS: float

@dataclass
class QuarterlyEarningsData:
    fiscalDateEnding: str
    reportedDate: str
    reportedEPS: float
    estimatedEPS: float
    surprise: float
    surprisePercentage: float
    reportTime: str

@dataclass
class EarningsData:
    symbol: str
    annualEarnings: list[AnnualEarningsData]
    quarterlyEarnings: list[QuarterlyEarningsData]

