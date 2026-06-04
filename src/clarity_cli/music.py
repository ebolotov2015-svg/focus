from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import Config
from .storage import Storage

SUPPORTED_AUDIO = {".mp3", ".wav", ".ogg"}


class MusicLibrary:
    def __init__(self, storage: Storage, config: Config) -> None:
        self.storage = storage
        self.config = config

    @property
    def music_dir(self) -> Path:
        path = Path(self.config.get("music_dir")).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def add(self, source: Path) -> tuple[str, Path]:
        source = source.expanduser()
        if not source.exists() or not source.is_file():
            raise ValueError(f"Audio file does not exist: {source}")
        if source.suffix.lower() not in SUPPORTED_AUDIO:
            raise ValueError("Supported audio formats: .mp3, .wav, .ogg")
        destination = self.music_dir / source.name
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        self.storage.add_track(destination.name, destination)
        return destination.name, destination

    def remove(self, name: str, *, delete_file: bool = False) -> bool:
        path = self.storage.track_path(name)
        removed = self.storage.remove_track(name)
        if removed and delete_file and path and path.exists() and path.parent == self.music_dir:
            path.unlink()
        return removed

    def list(self) -> list[tuple[str, Path, bool]]:
        return [(row["name"], Path(row["path"]), Path(row["path"]).exists()) for row in self.storage.tracks()]

    def resolve(self, name: str | None) -> Path | None:
        if not name:
            return None
        path = self.storage.track_path(name)
        return path if path and path.exists() else None


class MusicPlayer:
    def __init__(self) -> None:
        self._pygame = None
        self._process: subprocess.Popen[bytes] | None = None

    def play_loop(self, path: Path) -> None:
        try:
            import pygame
        except ImportError:
            self._play_with_system_player(path)
            return
        pygame.mixer.init()
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.play(loops=-1)
        self._pygame = pygame

    def stop(self) -> None:
        if self._pygame is not None:
            self._pygame.mixer.music.stop()
            self._pygame.mixer.quit()
            self._pygame = None
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def _play_with_system_player(self, path: Path) -> None:
        candidates = [
            ["mpv", "--no-video", "--loop=inf", "--really-quiet", str(path)],
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-loop", "0", str(path)],
            ["afplay", str(path)],
            ["paplay", str(path)],
        ]
        for command in candidates:
            if shutil.which(command[0]) is None:
                continue
            self._process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        raise RuntimeError(
            "No audio backend found. Install pygame with `pip install clarity-cli[audio]` "
            "or install a system player such as mpv or ffplay."
        )
