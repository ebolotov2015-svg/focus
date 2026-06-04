from __future__ import annotations

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

from .models import ActiveSession, SessionRecord, StatsSummary
from .storage import Storage

console = Console()


def format_duration(seconds: int) -> str:
    minutes, sec = divmod(max(0, seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {sec}s"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def show_active(active: ActiveSession) -> None:
    elapsed = Storage.current_active_seconds(active)
    paused = Storage.current_paused_seconds(active)
    lines = [
        "[bold green]Focus session is running[/bold green]" if not active.is_paused else "[bold yellow]Focus session is paused[/bold yellow]",
        f"Task: {active.task or '-'}",
        f"Mode: {active.mode}",
        f"Elapsed: {format_duration(elapsed)}",
        f"Paused: {'yes' if active.is_paused else 'no'} ({format_duration(paused)})",
        f"Music: {active.music or '-'}",
    ]
    if active.duration_seconds:
        lines.append(f"Target: {format_duration(active.duration_seconds)}")
    console.print(Panel("\n".join(lines), title="Status"))


def show_stopped(record: SessionRecord) -> None:
    console.print(
        Panel(
            "\n".join(
                [
                    "[bold green]Focus session saved[/bold green]",
                    f"Task: {record.task or '-'}",
                    f"Focused: {format_duration(record.active_seconds)}",
                    f"Paused: {format_duration(record.paused_seconds)}",
                ]
            ),
            title="Stopped",
        )
    )


def show_stats(summary: StatsSummary) -> None:
    focused_minutes = summary.focused_seconds // 60
    average_minutes = summary.average_seconds // 60
    goal = summary.daily_goal_minutes
    progress_value = min(100, int((focused_minutes / goal) * 100)) if goal else 0

    table = Table(title=summary.label)
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Focused", f"{focused_minutes} min")
    table.add_row("Sessions", str(summary.sessions))
    table.add_row("Average session", f"{average_minutes} min")
    table.add_row("Daily goal", f"{goal} min")
    table.add_row("Progress", f"{progress_value}%")
    console.print(table)

    progress = Progress(TextColumn("Goal"), BarColumn(), TextColumn("{task.percentage:>3.0f}%"), console=console)
    with progress:
        progress.add_task("daily-goal", total=goal, completed=min(focused_minutes, goal))


def show_tracks(tracks: list[tuple[str, object, bool]]) -> None:
    table = Table(title="Music library")
    table.add_column("Track")
    table.add_column("Path")
    table.add_column("Available")
    for name, path, exists in tracks:
        table.add_row(name, str(path), "yes" if exists else "missing")
    console.print(table)


def show_config(items: dict[str, str]) -> None:
    table = Table(title="Config")
    table.add_column("Key")
    table.add_column("Value")
    for key, value in items.items():
        table.add_row(key, value)
    console.print(table)


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")
