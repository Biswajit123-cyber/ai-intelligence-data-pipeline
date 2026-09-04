from datetime import datetime, timezone, timedelta
from src.date_utils import normalize_datetime, is_fresh_24h

def test_relative_hour():
    now = datetime(2026, 9, 3, 12, tzinfo=timezone.utc)
    dt = normalize_datetime("2 hours ago", now)
    assert dt == now - timedelta(hours=2)

def test_fresh():
    now = datetime(2026, 9, 3, 12, tzinfo=timezone.utc)
    assert is_fresh_24h(now - timedelta(hours=23), now)
    assert not is_fresh_24h(now - timedelta(hours=25), now)
