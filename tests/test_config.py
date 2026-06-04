from __future__ import annotations

import pytest

from clarity_cli.config import Config
from clarity_cli.storage import Storage


def test_timer_color_defaults_to_cyan(tmp_path):
    config = Config(Storage(tmp_path / "test.sqlite3"))

    assert config.get("timer_color") == "cyan"


def test_timer_color_accepts_known_colors_and_normalizes(tmp_path):
    config = Config(Storage(tmp_path / "test.sqlite3"))

    config.set("timer_color", "GREEN")

    assert config.get("timer_color") == "green"


def test_timer_color_rejects_unknown_color(tmp_path):
    config = Config(Storage(tmp_path / "test.sqlite3"))

    with pytest.raises(ValueError, match="timer_color must be one of"):
        config.set("timer_color", "red")
