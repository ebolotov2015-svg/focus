from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import StatsSummary
from .storage import Storage


def local_now() -> datetime:
    return datetime.now().astimezone()


def period_bounds(period: str, now: datetime | None = None) -> tuple[str, datetime, datetime]:
    current = now or local_now()
    if period == "today":
        start = current.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        label = "Today"
    elif period == "week":
        start = (current - timedelta(days=current.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        label = "This week"
    elif period == "month":
        start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        label = "This month"
    else:
        raise ValueError("Unknown stats period.")
    return label, start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def summarize(storage: Storage, period: str, daily_goal_minutes: int) -> StatsSummary:
    label, start, end = period_bounds(period)
    sessions = storage.sessions_between(start, end)
    focused_seconds = sum(session.active_seconds for session in sessions)
    average_seconds = focused_seconds // len(sessions) if sessions else 0
    return StatsSummary(
        label=label,
        sessions=len(sessions),
        focused_seconds=focused_seconds,
        average_seconds=average_seconds,
        daily_goal_minutes=daily_goal_minutes,
    )
