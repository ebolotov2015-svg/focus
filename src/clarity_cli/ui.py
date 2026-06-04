from __future__ import annotations

from datetime import datetime

from rich.console import Console
from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from rich.table import Table

from .models import ActiveSession, SessionRecord, StatsSummary
from .storage import Storage

console = Console()

TIMER_PALETTES = (
    ("cyan", "bold bright_cyan"),
    ("green", "bold bright_green"),
    ("yellow", "bold yellow"),
    ("magenta", "bold bright_magenta"),
    ("blue", "bold bright_blue"),
    ("white", "bold white"),
)

BIG_DIGITS = {
    "0": (" ██████ ", "██    ██", "██    ██", "██    ██", "██    ██", "██    ██", " ██████ "),
    "1": ("   ██   ", " ████   ", "   ██   ", "   ██   ", "   ██   ", "   ██   ", "███████ "),
    "2": (" ██████ ", "      ██", "      ██", " ██████ ", "██      ", "██      ", "████████"),
    "3": ("███████ ", "      ██", "      ██", " ██████ ", "      ██", "      ██", "███████ "),
    "4": ("██    ██", "██    ██", "██    ██", "████████", "      ██", "      ██", "      ██"),
    "5": ("████████", "██      ", "██      ", "███████ ", "      ██", "      ██", "███████ "),
    "6": (" ██████ ", "██      ", "██      ", "███████ ", "██    ██", "██    ██", " ██████ "),
    "7": ("████████", "      ██", "     ██ ", "    ██  ", "   ██   ", "  ██    ", "  ██    "),
    "8": (" ██████ ", "██    ██", "██    ██", " ██████ ", "██    ██", "██    ██", " ██████ "),
    "9": (" ██████ ", "██    ██", "██    ██", " ███████", "      ██", "      ██", " ██████ "),
    ":": ("        ", "   ██   ", "   ██   ", "        ", "   ██   ", "   ██   ", "        "),
}


def format_duration(seconds: int) -> str:
    minutes, sec = divmod(max(0, seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {sec}s"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def format_clock(seconds: int) -> str:
    minutes, sec = divmod(max(0, seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def big_clock(value: str) -> str:
    rows = [""] * 7
    for char in value:
        glyph = BIG_DIGITS.get(char, BIG_DIGITS[":"])
        for index, line in enumerate(glyph):
            rows[index] += line + " "
    return "\n".join(row.rstrip() for row in rows)


def palette_style(index: int) -> str:
    return TIMER_PALETTES[index % len(TIMER_PALETTES)][1]


def palette_label(index: int) -> str:
    return TIMER_PALETTES[index % len(TIMER_PALETTES)][0]


def active_timer_panel(active: ActiveSession, *, music_label: str, digit_style: str = "bold bright_cyan") -> Panel:
    elapsed = Storage.current_active_seconds(active)
    paused = Storage.current_paused_seconds(active)
    if active.duration_seconds:
        remaining = max(0, active.duration_seconds - elapsed)
        clock = format_clock(remaining)
        timer_label = "remaining"
    else:
        clock = format_clock(elapsed)
        timer_label = "elapsed"

    state = "PAUSED" if active.is_paused else "FOCUS"
    state_style = "bold yellow" if active.is_paused else "bold green"
    details = Text()
    details.append(f"{state}", style=state_style)
    details.append(f"  {timer_label}")
    details.append(f"  task: {active.task or active.mode}")
    details.append(f"  focused: {format_duration(elapsed)}")
    details.append(f"  paused: {format_duration(paused)}")
    details.append(f"  music: {music_label}")

    if active.duration_seconds:
        total = active.duration_seconds
        filled = int((elapsed / total) * 24) if total else 0
        filled = min(24, max(0, filled))
        details.append(f"\n[{'█' * filled}{'░' * (24 - filled)}] {min(100, int((elapsed / total) * 100))}%")

    body = Text(big_clock(clock) + "\n", style=digit_style)
    body.append_text(details)
    return Panel(Align.center(body), title="Focus timer", border_style="cyan" if not active.is_paused else "yellow")


def active_timer_screen(active: ActiveSession, *, music_label: str, color_index: int) -> Layout:
    elapsed = Storage.current_active_seconds(active)
    paused = Storage.current_paused_seconds(active)
    state = "paused" if active.is_paused else "focus"
    border_style = "yellow" if active.is_paused else "cyan"

    header = Text()
    header.append(" focus ", style="bold green")
    header.append(f"{state} session", style="bold yellow" if active.is_paused else "bold green")
    header.append(f"  task: {active.task or active.mode}")
    header.append(f"  focused: {format_duration(elapsed)}")
    header.append(f"  paused: {format_duration(paused)}")
    header.append(f"  music: {music_label}")
    header.append(f"  digits: {palette_label(color_index)}", style=palette_style(color_index))

    menu = Table.grid(expand=True)
    menu.add_column(justify="center")
    menu.add_row("[bold]Space[/bold]/[bold]p[/bold] pause-resume   [bold]c[/bold] color   [bold]s[/bold]/[bold]q[/bold] stop-save   [bold]Ctrl+C[/bold] stop-save")

    layout = Layout()
    layout.split_column(
        Layout(Panel(header, border_style=border_style), name="header", size=3),
        Layout(active_timer_panel(active, music_label=music_label, digit_style=palette_style(color_index)), name="timer", ratio=1),
        Layout(Panel(Align.center(menu), title="Menu", border_style=border_style), name="menu", size=5),
    )
    return layout


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
