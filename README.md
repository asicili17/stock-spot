# Django Project Setup

This is a Django project configured for development.

## Setup Instructions

### 1. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Create .env File
Copy `.env.example` to `.env` and update with your settings:
```powershell
copy .env.example .env
```

### 4. Run Migrations
```powershell
python manage.py migrate
```

### 5. Create Superuser (Optional)
```powershell
python manage.py createsuperuser
```

### 6. Start Development Server
```powershell
python manage.py runserver
```

The server will be available at `http://localhost:8000`

## Project Structure

- `config/` - Django configuration (settings, URLs, WSGI, ASGI)
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `manage.py` - Django management script
- `requirements.txt` - Python dependencies

## Features

- Django REST Framework configured
- CORS headers enabled for frontend integration
- SQLite database (can be changed to PostgreSQL)
- Static files configuration
- Debug toolbar ready

## Quant research proof of concept

The proof of concept caches validated Alpha Vantage bars locally, runs a
long-only monthly 12-1 momentum baseline, and saves an immutable audit trail
for the fundamental responses used during due diligence.

Run migrations first:

```powershell
python manage.py migrate
```

For a no-premium-key momentum experiment, cache Alpha Vantage's full monthly
adjusted series. It provides enough history for a monthly strategy while the
daily full-history endpoint requires a premium entitlement:

```powershell
python manage.py refresh_av_prices --monthly-adjusted AAPL MSFT NVDA
python manage.py backtest_momentum AAPL MSFT NVDA --top-n 2 --require-adjusted
```

`DailyPrice` records raw OHLCV, adjusted close when available, dividends,
split coefficients, source, and retrieval timestamp. Every price row is
validated before it is cached; rejected rows are recorded in the fetch audit.

With a premium daily-data entitlement, use daily bars instead:

```powershell
python manage.py refresh_av_prices --adjusted AAPL MSFT NVDA
```

The momentum command ranks each symbol by its 12-month return excluding the
most recent month, selects the top `N`, rebalances monthly, applies optional
turnover costs, and persists holdings and results in `MomentumBacktestRun`.
It is a price-momentum baseline, not an investment recommendation. Use
`--require-adjusted` for total-return research; without it the command reports
when it falls back to raw close prices.

To add the value factor, first audit the three statement/share endpoints for
every symbol. The value pipeline builds four-quarter free cash flow as
operating cash flow minus capital expenditures, then divides it by raw-close
market capitalization (raw close times basic shares outstanding). The raw
price is intentional: Alpha Vantage share counts and split-adjusted prices are
not interchangeable.

```powershell
python manage.py audit_av_fundamentals AAPL MSFT NVDA --seconds-between 1.1
python manage.py build_fcf_yield AAPL MSFT NVDA --as-of 2026-10-27
python manage.py backtest_momentum AAPL MSFT NVDA --top-n 2 --require-adjusted --value-weight 0.5
```

`--value-weight 0` is momentum only, `0.5` gives equal percentile-rank weight
to momentum and free-cash-flow yield, and `1` is value only. A stock is
excluded from a combined rebalance when four available cash-flow quarters, a
share count, or a stored raw close are missing. Statement endpoints do not
include publication dates, so the current version uses the matching
`EARNINGS.reportedDate` as an explicitly labelled availability proxy.

Audit Alpha Vantage's current fundamental and share-count responses before
using them in a value factor:

```powershell
python manage.py audit_av_fundamentals AAPL
```

The command stores a content-hashed, immutable raw snapshot of `EARNINGS`,
`INCOME_STATEMENT`, `BALANCE_SHEET`, `CASH_FLOW`, and `SHARES_OUTSTANDING` and
prints observed record and date coverage. A current response does not prove
that Alpha Vantage offers historical as-reported values or revisions, so value
backtests remain provisional until that point-in-time coverage is confirmed.

## Next Steps

1. Create Django apps with: `python manage.py startapp app_name`
2. Define models in each app's `models.py`
3. Create serializers for REST API
4. Register URLs in `config/urls.py`
