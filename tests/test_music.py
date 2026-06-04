from __future__ import annotations

from clarity_cli.config import Config
from clarity_cli.music import MusicLibrary
from clarity_cli.storage import Storage


def test_music_add_copies_supported_file(tmp_path):
    storage = Storage(tmp_path / "test.sqlite3")
    config = Config(storage)
    config.set("music_dir", str(tmp_path / "music"))
    library = MusicLibrary(storage, config)
    source = tmp_path / "rain.ogg"
    source.write_bytes(b"fake audio")

    name, destination = library.add(source)

    assert name == "rain.ogg"
    assert destination.exists()
    assert library.resolve("rain.ogg") == destination


def test_music_remove_deletes_library_record(tmp_path):
    storage = Storage(tmp_path / "test.sqlite3")
    config = Config(storage)
    config.set("music_dir", str(tmp_path / "music"))
    library = MusicLibrary(storage, config)
    source = tmp_path / "rain.ogg"
    source.write_bytes(b"fake audio")
    library.add(source)

    assert library.remove("rain.ogg")
    assert library.resolve("rain.ogg") is None
