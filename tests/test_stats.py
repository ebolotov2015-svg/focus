from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from clarity_cli.stats import period_bounds


def test_period_bounds_for_week_start_on_monday():
    now = datetime(2026, 6, 4, 18, 0, tzinfo=ZoneInfo("UTC"))

    label, start, end = period_bounds("week", now)

    assert label == "This week"
    assert start.isoformat() == "2026-06-01T00:00:00+00:00"
    assert end.isoformat() == "2026-06-08T00:00:00+00:00"


def test_period_bounds_for_month():
    now = datetime(2026, 12, 4, 18, 0, tzinfo=ZoneInfo("UTC"))

    _, start, end = period_bounds("month", now)

    assert start.isoformat() == "2026-12-01T00:00:00+00:00"
    assert end.isoformat() == "2027-01-01T00:00:00+00:00"
