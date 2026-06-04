from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ActiveSession:
    id: int
    task: str | None
    mode: str
    music: str | None
    started_at: datetime
    duration_seconds: int | None
    is_paused: bool
    pause_started_at: datetime | None
    paused_seconds: int


@dataclass(frozen=True)
class SessionRecord:
    id: int
    task: str | None
    mode: str
    music: str | None
    started_at: datetime
    ended_at: datetime
    active_seconds: int
    paused_seconds: int


@dataclass(frozen=True)
class StatsSummary:
    label: str
    sessions: int
    focused_seconds: int
    average_seconds: int
    daily_goal_minutes: int
