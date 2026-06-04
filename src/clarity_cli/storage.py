from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import ActiveSession, SessionRecord
from .paths import database_path


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def parse_dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


def dump_dt(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


class Storage:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self.connect() as con:
            con.executescript(
                """
                create table if not exists sessions (
                    id integer primary key autoincrement,
                    task text,
                    mode text not null,
                    music text,
                    started_at text not null,
                    ended_at text not null,
                    active_seconds integer not null,
                    paused_seconds integer not null
                );

                create table if not exists active_session (
                    id integer primary key check (id = 1),
                    task text,
                    mode text not null,
                    music text,
                    started_at text not null,
                    duration_seconds integer,
                    is_paused integer not null default 0,
                    pause_started_at text,
                    paused_seconds integer not null default 0
                );

                create table if not exists music_tracks (
                    name text primary key,
                    path text not null unique,
                    added_at text not null
                );

                create table if not exists config (
                    key text primary key,
                    value text not null
                );
                """
            )

    def active_session(self) -> ActiveSession | None:
        with self.connect() as con:
            row = con.execute("select * from active_session where id = 1").fetchone()
        return self._active_from_row(row) if row else None

    def start_session(
        self,
        *,
        task: str | None,
        mode: str,
        music: str | None,
        duration_seconds: int | None,
        now: datetime | None = None,
    ) -> ActiveSession:
        if self.active_session() is not None:
            raise ValueError("A focus session is already active.")
        started_at = now or utc_now()
        with self.connect() as con:
            con.execute(
                """
                insert into active_session
                    (id, task, mode, music, started_at, duration_seconds, is_paused, pause_started_at, paused_seconds)
                values (1, ?, ?, ?, ?, ?, 0, null, 0)
                """,
                (task, mode, music, dump_dt(started_at), duration_seconds),
            )
        active = self.active_session()
        if active is None:
            raise RuntimeError("Failed to create active session.")
        return active

    def pause_session(self, now: datetime | None = None) -> ActiveSession:
        active = self.active_session()
        if active is None:
            raise ValueError("No active focus session.")
        if active.is_paused:
            raise ValueError("Focus session is already paused.")
        pause_started_at = now or utc_now()
        with self.connect() as con:
            con.execute(
                "update active_session set is_paused = 1, pause_started_at = ? where id = 1",
                (dump_dt(pause_started_at),),
            )
        return self.active_session()  # type: ignore[return-value]

    def resume_session(self, now: datetime | None = None) -> ActiveSession:
        active = self.active_session()
        if active is None:
            raise ValueError("No active focus session.")
        if not active.is_paused or active.pause_started_at is None:
            raise ValueError("Focus session is not paused.")
        resumed_at = now or utc_now()
        extra_pause = max(0, int((resumed_at - active.pause_started_at).total_seconds()))
        with self.connect() as con:
            con.execute(
                """
                update active_session
                set is_paused = 0,
                    pause_started_at = null,
                    paused_seconds = paused_seconds + ?
                where id = 1
                """,
                (extra_pause,),
            )
        return self.active_session()  # type: ignore[return-value]

    def stop_session(self, now: datetime | None = None) -> SessionRecord:
        active = self.active_session()
        if active is None:
            raise ValueError("No active focus session.")
        ended_at = now or utc_now()
        paused_seconds = self.current_paused_seconds(active, ended_at)
        active_seconds = max(0, int((ended_at - active.started_at).total_seconds()) - paused_seconds)
        with self.connect() as con:
            cur = con.execute(
                """
                insert into sessions
                    (task, mode, music, started_at, ended_at, active_seconds, paused_seconds)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    active.task,
                    active.mode,
                    active.music,
                    dump_dt(active.started_at),
                    dump_dt(ended_at),
                    active_seconds,
                    paused_seconds,
                ),
            )
            con.execute("delete from active_session where id = 1")
            session_id = int(cur.lastrowid)
        return SessionRecord(
            id=session_id,
            task=active.task,
            mode=active.mode,
            music=active.music,
            started_at=active.started_at,
            ended_at=ended_at,
            active_seconds=active_seconds,
            paused_seconds=paused_seconds,
        )

    def sessions_between(self, start: datetime, end: datetime) -> list[SessionRecord]:
        with self.connect() as con:
            rows = con.execute(
                """
                select * from sessions
                where ended_at >= ? and ended_at < ?
                order by ended_at desc
                """,
                (dump_dt(start), dump_dt(end)),
            ).fetchall()
        return [self._session_from_row(row) for row in rows]

    def add_track(self, name: str, path: Path) -> None:
        with self.connect() as con:
            con.execute(
                "insert or replace into music_tracks (name, path, added_at) values (?, ?, ?)",
                (name, str(path), dump_dt(utc_now())),
            )

    def remove_track(self, name: str) -> bool:
        with self.connect() as con:
            cur = con.execute("delete from music_tracks where name = ?", (name,))
        return cur.rowcount > 0

    def tracks(self) -> list[sqlite3.Row]:
        with self.connect() as con:
            return con.execute("select name, path, added_at from music_tracks order by name").fetchall()

    def track_path(self, name: str) -> Path | None:
        with self.connect() as con:
            row = con.execute("select path from music_tracks where name = ?", (name,)).fetchone()
        return Path(row["path"]) if row else None

    def get_config(self, key: str) -> str | None:
        with self.connect() as con:
            row = con.execute("select value from config where key = ?", (key,)).fetchone()
        return str(row["value"]) if row else None

    def set_config(self, key: str, value: Any) -> None:
        with self.connect() as con:
            con.execute(
                "insert into config (key, value) values (?, ?) on conflict(key) do update set value = excluded.value",
                (key, str(value)),
            )

    def config_items(self) -> dict[str, str]:
        with self.connect() as con:
            rows = con.execute("select key, value from config order by key").fetchall()
        return {row["key"]: row["value"] for row in rows}

    @staticmethod
    def current_paused_seconds(active: ActiveSession, now: datetime | None = None) -> int:
        current = now or utc_now()
        total = active.paused_seconds
        if active.is_paused and active.pause_started_at is not None:
            total += max(0, int((current - active.pause_started_at).total_seconds()))
        return total

    @staticmethod
    def current_active_seconds(active: ActiveSession, now: datetime | None = None) -> int:
        current = now or utc_now()
        elapsed = max(0, int((current - active.started_at).total_seconds()))
        return max(0, elapsed - Storage.current_paused_seconds(active, current))

    @staticmethod
    def _active_from_row(row: sqlite3.Row) -> ActiveSession:
        return ActiveSession(
            id=row["id"],
            task=row["task"],
            mode=row["mode"],
            music=row["music"],
            started_at=parse_dt(row["started_at"]),  # type: ignore[arg-type]
            duration_seconds=row["duration_seconds"],
            is_paused=bool(row["is_paused"]),
            pause_started_at=parse_dt(row["pause_started_at"]),
            paused_seconds=row["paused_seconds"],
        )

    @staticmethod
    def _session_from_row(row: sqlite3.Row) -> SessionRecord:
        return SessionRecord(
            id=row["id"],
            task=row["task"],
            mode=row["mode"],
            music=row["music"],
            started_at=parse_dt(row["started_at"]),  # type: ignore[arg-type]
            ended_at=parse_dt(row["ended_at"]),  # type: ignore[arg-type]
            active_seconds=row["active_seconds"],
            paused_seconds=row["paused_seconds"],
        )
