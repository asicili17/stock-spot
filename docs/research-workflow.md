# Research workflow

## Monthly baseline

At each month-end, momentum is the return from month `M-12` through month
`M-1`. The strategy enters after month `M`, holds for one month, selects the
top `N` eligible stocks, and equal weights them. Optional cost is turnover times
the configured basis points.

FCF yield is trailing four available quarterly operating cash flows less capital
expenditures, divided by raw-close market capitalization. A statement endpoint
does not provide a report date, so the matching earnings `reportedDate` is an
availability proxy. Backtests using it are provisional until genuine
point-in-time statement history is confirmed.

## Commands

```powershell
python manage.py refresh_av_prices --adjusted AAPL MSFT
python manage.py audit_av_fundamentals AAPL --seconds-between 1.1
python manage.py build_fcf_yield AAPL --as-of 2026-10-30
python manage.py backtest_momentum AAPL MSFT --top-n 10 --require-adjusted --value-weight 0.5
```

The current universe is the symbols supplied to a command, or all stored stocks
when no symbols are supplied to the backtest. A future S&P 500 universe loader
must retain effective membership dates to avoid survivorship bias. Financials
should remain outside the first FCF-yield universe because their cash-flow and
debt economics differ from operating companies.
