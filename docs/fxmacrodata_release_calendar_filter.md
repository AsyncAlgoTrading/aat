# FXMacroData Release Calendar Filter

FXMacroData exposes a public macro release-calendar endpoint that can be used to
pause entries or reduce sizing around scheduled event risk in an AAT backtest.
The snippet below loads confirmed tier-one USD events and checks them from a
strategy callback before submitting new orders.

```python
from datetime import datetime, timedelta, timezone
import json
from urllib.parse import urlencode
from urllib.request import urlopen


FXMD_CALENDAR_URL = "https://fxmacrodata.com/api/v1/calendar/{currency}"


def load_macro_blackout_dates(start_date, end_date):
    params = urlencode({"start_date": start_date, "end_date": end_date})
    url = FXMD_CALENDAR_URL.format(currency="USD") + "?" + params

    with urlopen(url, timeout=20) as response:
        payload = json.load(response)

    blackout_dates = set()
    for event in payload.get("data", []):
        if not event.get("release_date_confirmed"):
            continue
        if int(event.get("market_tier") or 99) > 1:
            continue

        event_date = datetime.fromtimestamp(
            int(event["announcement_datetime"]),
            tz=timezone.utc,
        ).date()
        blackout_dates.add(event_date.isoformat())

    return blackout_dates


def can_submit_order(event_timestamp, blackout_dates):
    trading_date = event_timestamp.date().isoformat()
    return trading_date not in blackout_dates
```

Example use inside a strategy:

```python
blackout_dates = load_macro_blackout_dates("2026-07-01", "2026-07-31")

async def onTrade(self, event):
    if not can_submit_order(event.timestamp, blackout_dates):
        return

    # Continue with order creation here.
```
