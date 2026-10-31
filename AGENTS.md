# Stock Spot contributor guide

## Purpose

Stock Spot is a Django research application for monthly, long-only U.S. equity
factor research. Alpha Vantage is the sole market-data provider. The current
research baseline combines 12-1 momentum with trailing free-cash-flow yield.

## Architecture

- `stock_spot/models/`: persisted market data, factor signals, and legacy
  company-profile fundamentals.
- `stock_spot/services/market_data.py`: validated price ingestion and monthly
  portfolio simulation.
- `stock_spot/services/value.py`: FCF-yield signal construction with source
  snapshot provenance.
- `stock_spot/services/fundamentals/`: latest-profile metric calculators.
- `stock_spot/management/commands/`: operator-facing import, audit, signal,
  and backtest commands.
- `docs/`: the durable explanation of application behavior and research limits.

## Required checks

Run these before committing Python changes:

```powershell
python manage.py test stock_spot
python manage.py check
python manage.py makemigrations --check --dry-run
```

Tests must mock Alpha Vantage and Mailgun. Do not make network calls from unit
tests or expose credentials in commands, output, documentation, or fixtures.

## Documentation maintenance

Update documentation in the same change when you modify any of the following:

- a model or migration: update `docs/application-architecture.md`;
- a signal, ranking, availability rule, or portfolio assumption: update
  `docs/research-workflow.md` and relevant tests;
- a command, configuration value, endpoint, or developer workflow: update
  `README.md` and `docs/developer-guide.md`.

Keep naming specific: services and commands should state the data source,
domain, or operation they perform. Preserve raw data and source provenance;
never replace historical research inputs without an audit trail.
