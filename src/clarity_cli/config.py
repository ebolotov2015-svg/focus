from __future__ import annotations

from pathlib import Path

from .paths import default_music_dir
from .storage import Storage
from .ui import TIMER_COLOR_NAMES

DEFAULTS = {
    "daily_goal": "120",
    "default_music": "false",
    "default_track": "",
    "timer_color": "cyan",
    "time_format": "24h",
    "notifications": "false",
    "music_dir": str(default_music_dir()),
}


class Config:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        for key, value in DEFAULTS.items():
            if self.storage.get_config(key) is None:
                self.storage.set_config(key, value)

    def get(self, key: str) -> str:
        return self.storage.get_config(key) or DEFAULTS.get(key, "")

    def set(self, key: str, value: str) -> None:
        if key not in DEFAULTS:
            raise ValueError(f"Unknown config key: {key}")
        if key == "daily_goal":
            minutes = int(value)
            if minutes <= 0:
                raise ValueError("daily_goal must be greater than zero.")
        if key in {"default_music", "notifications"} and value.lower() not in {"true", "false"}:
            raise ValueError(f"{key} must be true or false.")
        if key == "timer_color":
            value = value.lower()
            if value not in TIMER_COLOR_NAMES:
                colors = ", ".join(TIMER_COLOR_NAMES)
                raise ValueError(f"timer_color must be one of: {colors}.")
        if key == "music_dir":
            Path(value).expanduser().mkdir(parents=True, exist_ok=True)
            value = str(Path(value).expanduser())
        self.storage.set_config(key, value)

    def all(self) -> dict[str, str]:
        items = DEFAULTS | self.storage.config_items()
        return dict(sorted(items.items()))

    def bool(self, key: str) -> bool:
        return self.get(key).lower() == "true"

    def int(self, key: str) -> int:
        return int(self.get(key))
