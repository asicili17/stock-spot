# Application architecture

Stock Spot is a Django application with SQLite for local development. It has
three layers: provider ingestion, persistent research data, and strategy
calculation.

## Provider ingestion

`AlphaVantageService` fetches company profile fundamentals. `DailyPriceCacheService`
validates and stores raw OHLCV, adjusted close, dividends, and split information.
`AlphaVantageFundamentalsAuditor` stores immutable, content-hashed raw responses
for earnings, statements, and share counts.

## Persistent research records

`Stock` holds the current display profile. `DailyPrice` stores historical bars.
`FundamentalSnapshot` preserves provider responses, while `ShareCountObservation`
normalizes share-count rows with a source snapshot. `FreeCashFlowYieldSignal`
records its inputs, availability proxy, and result. `MomentumBacktestRun` stores
parameters, monthly holdings, and results for a reproducible run.

## Calculations

`EarningsGrowthMetricCalculator` and `ConservativeValuationCalculator` update
latest-profile display metrics. `FreeCashFlowYieldService` calculates trailing
four-quarter free cash flow divided by raw-price market capitalization.
`MonthlyMomentumBacktester` ranks 12-1 momentum and can blend it with FCF-yield
percentile rank using `value_weight`.

Raw close is used with raw share counts for historical market capitalization.
Adjusted close is used for return calculations. Mixing adjusted prices with
unadjusted share counts produces incorrect market caps around stock splits.
