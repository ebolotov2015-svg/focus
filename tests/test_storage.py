from __future__ import annotations

from datetime import datetime, timezone

import pytest

from clarity_cli.storage import Storage


def dt(second: int) -> datetime:
    return datetime(2026, 1, 1, 12, 0, second, tzinfo=timezone.utc)


def test_session_lifecycle_counts_active_time_without_pauses(tmp_path):
    storage = Storage(tmp_path / "test.sqlite3")

    storage.start_session(task="write", mode="focus", music=None, duration_seconds=None, now=dt(0))
    storage.pause_session(now=dt(10))
    storage.resume_session(now=dt(20))
    record = storage.stop_session(now=dt(50))

    assert record.active_seconds == 40
    assert record.paused_seconds == 10
    assert record.task == "write"
    assert storage.active_session() is None


def test_cannot_start_second_active_session(tmp_path):
    storage = Storage(tmp_path / "test.sqlite3")

    storage.start_session(task=None, mode="focus", music=None, duration_seconds=None, now=dt(0))

    with pytest.raises(ValueError, match="already active"):
        storage.start_session(task=None, mode="focus", music=None, duration_seconds=None, now=dt(1))


def test_pause_and_resume_require_valid_state(tmp_path):
    storage = Storage(tmp_path / "test.sqlite3")

    with pytest.raises(ValueError, match="No active"):
        storage.pause_session(now=dt(0))

    storage.start_session(task=None, mode="focus", music=None, duration_seconds=None, now=dt(0))
    storage.pause_session(now=dt(5))

    with pytest.raises(ValueError, match="already paused"):
        storage.pause_session(now=dt(6))

    storage.resume_session(now=dt(10))

    with pytest.raises(ValueError, match="not paused"):
        storage.resume_session(now=dt(11))
