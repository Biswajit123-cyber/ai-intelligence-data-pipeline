from datetime import datetime, timedelta, timezone
import re
from dateutil import parser as date_parser

RELATIVE = re.compile(
    r"^\s*(\d+)\s+(minute|minutes|hour|hours|day|days)\s+ago\s*$",
    re.I,
)

def normalize_datetime(value: str | datetime | None, now: datetime | None = None) -> datetime | None:
    if not value:
        return None
    now = now or datetime.now(timezone.utc)

    if isinstance(value, datetime):
        dt = value
    else:
        text = value.strip()
        m = RELATIVE.match(text)
        if m:
            amount = int(m.group(1))
            unit = m.group(2).lower()
            seconds = amount * (
                60 if unit.startswith("minute")
                else 3600 if unit.startswith("hour")
                else 86400
            )
            return now - timedelta(seconds=seconds)
        try:
            dt = date_parser.parse(text, fuzzy=True)
        except (ValueError, TypeError, OverflowError):
            return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def is_fresh_24h(value, now=None) -> bool:
    now = now or datetime.now(timezone.utc)
    dt = normalize_datetime(value, now)
    return bool(dt and timedelta(0) <= now - dt <= timedelta(hours=24))
