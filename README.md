# clarity-cli

`clarity-cli` is a local-first command-line focus timer for focused work sessions, optional background music, and simple productivity statistics.

It is designed as an independent open-source tool. It works offline, stores data locally, and does not include any music files.

## Features

- Start, pause, resume, stop, and inspect focus sessions.
- Track active time without counting pauses.
- Save session history in SQLite.
- Show daily, weekly, and monthly stats with Rich tables and progress bars.
- Add and manage local `.mp3`, `.wav`, and `.ogg` tracks.
- Store configuration in the user's app config/data directories.

## Installation

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

After installation, the `focus` command is available.

```bash
focus --help
```

## Quick Start

Start a focus session:

```bash
focus start --task "Write README"
```

Start a 50-minute session:

```bash
focus start --duration 50 --task "Deep work"
```

Check status from another terminal:

```bash
focus status
```

Pause and resume:

```bash
focus pause
focus resume
```

Stop and save the session:

```bash
focus stop
```

`focus start` also stops and saves the session when you press `Ctrl+C`.

## Commands

```bash
focus start
focus start --music
focus start --duration 50
focus start --task "Write documentation"
focus pause
focus resume
focus stop
focus status
focus stats
focus stats --today
focus stats --week
focus stats --month
focus music list
focus music play <track>
focus music add <path>
focus music remove <track>
focus config
focus config set daily_goal 120
focus config set default_music true
focus where
```

## Music

Music is optional. No audio files are shipped with this repository because music rights vary by file and source.

Add your own local track:

```bash
focus music add ~/Music/rain.ogg
```

List tracks:

```bash
focus music list
```

Play a track:

```bash
focus music play rain.ogg
```

Start a session with the default track:

```bash
focus config set default_track rain.ogg
focus config set default_music true
focus start --music
```

Supported file extensions are `.mp3`, `.wav`, and `.ogg`. Playback uses `pygame` when available, otherwise it tries common system players such as `mpv`, `ffplay`, `afplay`, or `paplay`.

To install the optional Python audio backend:

```bash
pip install -e ".[audio]"
```

## Configuration

Show config:

```bash
focus config
```

Available keys:

- `daily_goal`: daily focus target in minutes.
- `default_music`: `true` or `false`.
- `default_track`: track name from `focus music list`.
- `time_format`: currently stored for user preference.
- `notifications`: currently stored for user preference.
- `music_dir`: directory where added tracks are copied.

## Data Storage

`clarity-cli` uses `platformdirs` to keep user data out of the repository.

Show exact local paths:

```bash
focus where
```

The SQLite database is stored in the user data directory. Music files are copied into the configured music directory.

## Development

Run tests:

```bash
pytest
```

Project layout:

```text
.
├── assets/
│   └── music/
├── src/
│   └── clarity_cli/
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── music.py
│       ├── paths.py
│       ├── stats.py
│       ├── storage.py
│       └── ui.py
└── tests/
```

## Contributing

Small, focused pull requests are preferred. Keep the tool local-first, avoid network requirements, and do not commit copyrighted music.

## License

MIT
