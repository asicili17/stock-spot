# Developer guide

## Setup

Create `.env` from `.env.example` and set `STOCK_API_KEY`. Mail reports also
require the configured Mailgun variables. Run `python manage.py migrate`, then
start Django with `python manage.py runserver`.

## Verification

Run the three required commands in `AGENTS.md`. Use Django's test database; do
not use the local `db.sqlite3` as a fixture. Test provider behavior with fake
responses and mock email delivery.

## Data safety

The application treats fetched prices and fundamental snapshots as durable local
research records. Keep raw observations, provider source, retrieval time, and
response hashes. A new source revision should be auditable rather than silently
overwriting research provenance.
