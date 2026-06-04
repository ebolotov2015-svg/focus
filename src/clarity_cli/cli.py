from __future__ import annotations

import contextlib
import os
import sys
import time
from pathlib import Path
from typing import Annotated, Callable, Iterator

import typer
from rich.live import Live

from .config import Config
from .music import MusicLibrary, MusicPlayer
from .stats import summarize
from .storage import Storage
from .ui import active_timer_panel, console, show_active, show_config, show_stats, show_stopped, show_tracks

app = typer.Typer(help="Local-first focus timer with stats and optional music.")
music_app = typer.Typer(help="Manage local music tracks.")
config_app = typer.Typer(help="View and update local configuration.")
app.add_typer(music_app, name="music")
app.add_typer(config_app, name="config")


def services() -> tuple[Storage, Config, MusicLibrary]:
    storage = Storage()
    config = Config(storage)
    music = MusicLibrary(storage, config)
    return storage, config, music


def minutes_to_seconds(value: int | None) -> int | None:
    if value is None:
        return None
    if value <= 0:
        raise typer.BadParameter("Duration must be greater than zero.")
    return value * 60


@contextlib.contextmanager
def raw_key_reader() -> Iterator[Callable[[], str | None]]:
    if not sys.stdin.isatty():
        yield lambda: None
        return

    if os.name == "nt":
        import msvcrt

        def read_windows_key() -> str | None:
            if not msvcrt.kbhit():
                return None
            key = msvcrt.getwch()
            return "\x03" if key == "\x03" else key.lower()

        yield read_windows_key
        return

    import select
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)

        def read_posix_key() -> str | None:
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if not ready:
                return None
            key = sys.stdin.read(1)
            return "\x03" if key == "\x03" else key.lower()

        yield read_posix_key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def run_focus_timer(storage: Storage, player: MusicPlayer, *, music_label: str) -> None:
    with raw_key_reader() as read_key:
        with Live(console=console, refresh_per_second=4, transient=False) as live:
            while True:
                current = storage.active_session()
                if current is None:
                    live.stop()
                    console.print("[yellow]Session ended from another command.[/yellow]")
                    return

                live.update(active_timer_panel(current, music_label=music_label))
                key = read_key()
                if key == "\x03":
                    raise KeyboardInterrupt
                if key in {"s", "q"}:
                    record = storage.stop_session()
                    live.update(active_timer_panel(current, music_label=music_label))
                    live.stop()
                    show_stopped(record)
                    return
                if key in {" ", "p"}:
                    if current.is_paused:
                        current = storage.resume_session()
                        player.resume()
                    else:
                        current = storage.pause_session()
                        player.pause()
                    live.update(active_timer_panel(current, music_label=music_label))
                elif key == "r" and current.is_paused:
                    current = storage.resume_session()
                    player.resume()
                    live.update(active_timer_panel(current, music_label=music_label))

                current = storage.active_session()
                if current and current.duration_seconds and Storage.current_active_seconds(current) >= current.duration_seconds:
                    record = storage.stop_session()
                    live.stop()
                    show_stopped(record)
                    return
                time.sleep(0.25)


@app.command()
def start(
    duration: Annotated[int | None, typer.Option("--duration", "-d", help="Session duration in minutes.")] = None,
    task: Annotated[str | None, typer.Option("--task", "-t", help="Task or note for this session.")] = None,
    music: Annotated[bool, typer.Option("--music", help="Play the default music track.")] = False,
    track: Annotated[str | None, typer.Option("--track", help="Track name from the music library.")] = None,
    mode: Annotated[str, typer.Option("--mode", help="Session mode label.")] = "focus",
) -> None:
    """Start a focus session and keep it running until stopped."""
    storage, config, music_library = services()
    use_music = music or config.bool("default_music")
    selected_track = track or (config.get("default_track") if use_music else None)
    music_path = music_library.resolve(selected_track)
    if selected_track and music_path is None:
        raise typer.BadParameter(f"Track not found: {selected_track}")

    try:
        active = storage.start_session(
            task=task,
            mode=mode,
            music=selected_track if music_path else None,
            duration_seconds=minutes_to_seconds(duration),
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    player = MusicPlayer()
    if music_path:
        player.play_loop(music_path)
    music_label = selected_track if music_path else "off"

    try:
        run_focus_timer(storage, player, music_label=music_label)
    except KeyboardInterrupt:
        record = storage.stop_session()
        show_stopped(record)
    finally:
        player.stop()


@app.command()
def pause() -> None:
    """Pause the active focus session."""
    storage, _, _ = services()
    try:
        active = storage.pause_session()
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    show_active(active)


@app.command()
def resume() -> None:
    """Resume a paused focus session."""
    storage, _, _ = services()
    try:
        active = storage.resume_session()
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    show_active(active)


@app.command()
def stop() -> None:
    """Stop the active session and save it to statistics."""
    storage, _, _ = services()
    try:
        record = storage.stop_session()
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    show_stopped(record)


@app.command()
def status() -> None:
    """Show the current focus session status."""
    storage, _, _ = services()
    active = storage.active_session()
    if active is None:
        console.print("[yellow]No active focus session.[/yellow]")
        return
    show_active(active)


@app.command()
def stats(
    today: Annotated[bool, typer.Option("--today", help="Show today's stats.")] = False,
    week: Annotated[bool, typer.Option("--week", help="Show this week's stats.")] = False,
    month: Annotated[bool, typer.Option("--month", help="Show this month's stats.")] = False,
) -> None:
    """Show focus statistics."""
    storage, config, _ = services()
    period = "today"
    if week:
        period = "week"
    if month:
        period = "month"
    if today:
        period = "today"
    show_stats(summarize(storage, period, config.int("daily_goal")))


@music_app.command("list")
def music_list() -> None:
    """List added music tracks."""
    _, _, music_library = services()
    tracks = music_library.list()
    if not tracks:
        console.print("[yellow]No tracks added yet.[/yellow]")
        return
    show_tracks(tracks)


@music_app.command("add")
def music_add(path: Annotated[Path, typer.Argument(help="Path to a .mp3, .wav, or .ogg file.")]) -> None:
    """Copy a local audio file into the music library."""
    _, _, music_library = services()
    try:
        name, destination = music_library.add(path)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    console.print(f"[green]Added track[/green]: {name}")
    console.print(str(destination))


@music_app.command("remove")
def music_remove(
    track: Annotated[str, typer.Argument(help="Track name to remove.")],
    delete_file: Annotated[bool, typer.Option("--delete-file", help="Also delete the copied file.")] = False,
) -> None:
    """Remove a track from the local library."""
    _, _, music_library = services()
    if not music_library.remove(track, delete_file=delete_file):
        console.print(f"[red]Track not found: {track}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Removed track[/green]: {track}")


@music_app.command("play")
def music_play(track: Annotated[str, typer.Argument(help="Track name to play.")]) -> None:
    """Play a track until Ctrl+C."""
    _, _, music_library = services()
    path = music_library.resolve(track)
    if path is None:
        console.print(f"[red]Track not found: {track}[/red]")
        raise typer.Exit(1)
    player = MusicPlayer()
    try:
        player.play_loop(path)
        console.print(f"[green]Playing[/green]: {track}")
        console.print("Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped.[/yellow]")
    finally:
        player.stop()


@config_app.callback(invoke_without_command=True)
def config_root(ctx: typer.Context) -> None:
    """Show local configuration."""
    if ctx.invoked_subcommand is not None:
        return
    _, config, _ = services()
    show_config(config.all())


@config_app.command("set")
def config_set(
    key: Annotated[str, typer.Argument(help="Config key.")],
    value: Annotated[str, typer.Argument(help="New config value.")],
) -> None:
    """Set a configuration value."""
    _, config, _ = services()
    try:
        config.set(key, value)
    except (ValueError, TypeError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    console.print(f"[green]Updated[/green]: {key} = {config.get(key)}")


@app.command("where")
def where() -> None:
    """Show where clarity-cli stores local data."""
    storage, config, _ = services()
    console.print(f"Database: {storage.path}")
    console.print(f"Music directory: {config.get('music_dir')}")
