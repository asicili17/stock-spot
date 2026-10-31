"""Capture what Alpha Vantage actually returns for fundamental-data due diligence."""

from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
import time

from stock_spot.models import FundamentalSnapshot, Stock
from stock_spot.services.alpha_vantage import AlphaVantageService


AUDIT_ENDPOINTS = ('EARNINGS', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW', 'SHARES_OUTSTANDING')


def _hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')
    return sha256(encoded).hexdigest()


def _dates_in(value):
    """Find ISO dates without assuming an undocumented response schema."""
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {'fiscaldateending', 'reporteddate', 'date'} and isinstance(item, str):
                try:
                    found.add(date.fromisoformat(item).isoformat())
                except ValueError:
                    pass
            found.update(_dates_in(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_dates_in(item))
    return found


def _count_records(value):
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return sum(_count_records(item) for item in value.values())
    return 0


class AlphaVantageFundamentalsAuditor:
    """Store immutable payloads so response changes and date coverage are observable."""

    def __init__(self, client=None):
        self.client = client or AlphaVantageService()

    def audit_symbol(self, symbol: str, endpoints=AUDIT_ENDPOINTS, seconds_between: float = 1.1) -> list[dict]:
        stock, _ = Stock.objects.get_or_create(symbol=symbol.upper(), defaults={'isBought': False})
        audits = []
        for index, endpoint in enumerate(endpoints):
            payload = self.client._make_api_request({'function': endpoint, 'symbol': stock.symbol})
            dates = sorted(_dates_in(payload))
            summary = {
                'record_count': _count_records(payload),
                'date_count': len(dates),
                'earliest_date': dates[0] if dates else None,
                'latest_date': dates[-1] if dates else None,
                'has_reported_date': 'reportedDate' in json.dumps(payload),
                'top_level_keys': sorted(payload.keys()),
                'point_in_time_status': (
                    'unverified: snapshot records current provider response; it does not establish '
                    'historical as-reported or restatement coverage'
                ),
            }
            digest = _hash(payload)
            snapshot, created = FundamentalSnapshot.objects.get_or_create(
                stock=stock,
                endpoint=endpoint,
                content_hash=digest,
                defaults={'payload': payload, 'audit_summary': summary},
            )
            audits.append({
                'symbol': stock.symbol,
                'endpoint': endpoint,
                'created_snapshot': created,
                'snapshot_id': snapshot.id,
                **summary,
            })
            if index < len(endpoints) - 1 and seconds_between:
                time.sleep(seconds_between)
        return audits
