# focus

`focus` — локальный CLI-инструмент для фокус-сессий, фоновой музыки и простой статистики продуктивности.

Репозиторий: [ebolotov2015-svg/focus](https://github.com/ebolotov2015-svg/focus)

Проект можно скачать с GitHub, установить в виртуальное окружение Python и сразу использовать из терминала командой `focus`. Данные хранятся локально на компьютере пользователя: история сессий, настройки и добавленные треки не отправляются в интернет.

## Что умеет

- запускать фокус-сессии из терминала;
- показывать живой таймер прямо во время сессии;
- запускать сессию на заданное количество минут;
- сохранять задачу или заметку к сессии;
- ставить текущую сессию на паузу и продолжать ее из того же терминала;
- останавливать сессию и сохранять активное время без пауз;
- показывать статус активной сессии;
- вести статистику за день, неделю и месяц;
- хранить историю в локальной SQLite-базе;
- добавлять локальные `.mp3`, `.wav`, `.ogg` треки;
- запускать фоновую музыку во время работы;
- показывать, где именно лежат локальные данные.

## Требования

- Python 3.11 или новее;
- Git;
- терминал: Linux, macOS или Windows PowerShell.

Музыка необязательна. Для воспроизведения можно использовать `pygame` или системный плеер: `mpv`, `ffplay`, `afplay` или `paplay`.

## Установка

Склонируйте репозиторий:

```bash
git clone https://github.com/ebolotov2015-svg/focus.git
cd focus
```

Создайте и активируйте виртуальное окружение.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Установите проект:

```bash
pip install -e .
```

Проверьте, что команда доступна:

```bash
focus --help
```

Для установки вместе с Python-аудиобэкендом:

```bash
pip install -e ".[audio]"
```

Для разработки и запуска тестов:

```bash
pip install -e ".[dev]"
```

## Быстрый старт

Запустить обычную фокус-сессию:

```bash
focus start
```

Во время сессии команда показывает таймер. Управление работает без второго терминала:

- `Space` или `p` — пауза/продолжить;
- `r` — продолжить paused-сессию;
- `s` или `q` — остановить и сохранить;
- `Ctrl+C` — остановить и сохранить.

Запустить сессию с названием задачи:

```bash
focus start --task "Написать README"
```

Запустить сессию на 50 минут:

```bash
focus start --duration 50 --task "Глубокая работа"
```

Посмотреть статус из другого терминала:

```bash
focus status
```

Поставить на паузу и продолжить из другого терминала:

```bash
focus pause
focus resume
```

Остановить сессию и сохранить результат:

```bash
focus stop
```

Если сессия запущена через `focus start`, ей можно управлять прямо в этом же окне: `Space`/`p` ставит на паузу и продолжает, `s`/`q` или `Ctrl+C` останавливает и сохраняет результат.

## Основные команды

```bash
focus start
focus start --duration 50
focus start --task "Написать документацию"
focus start --music
focus start --track rain.ogg
focus pause
focus resume
focus stop
focus status
focus stats
focus stats --today
focus stats --week
focus stats --month
focus music list
focus music add <path>
focus music play <track>
focus music remove <track>
focus config
focus config set daily_goal 120
focus config set default_music true
focus config set default_track rain.ogg
focus where
```

## Статистика

Показать статистику за сегодня:

```bash
focus stats --today
```

За неделю:

```bash
focus stats --week
```

За месяц:

```bash
focus stats --month
```

В статистике отображаются сфокусированные минуты, количество сессий, средняя длительность сессии, дневная цель и прогресс к ней.

## Музыка

В репозитории нет аудиофайлов. Это сделано намеренно: права на музыку зависят от конкретного файла и источника. Пользователь добавляет свои локальные треки сам.

Поддерживаемые расширения:

- `.mp3`
- `.wav`
- `.ogg`

Добавить трек:

```bash
focus music add ~/Music/rain.ogg
```

Показать добавленные треки:

```bash
focus music list
```

Проиграть трек:

```bash
focus music play rain.ogg
```

Сделать трек треком по умолчанию:

```bash
focus config set default_track rain.ogg
focus config set default_music true
```

Запустить сессию с музыкой:

```bash
focus start --music
```

Запустить сессию с конкретным треком:

```bash
focus start --track rain.ogg
```

Если музыка не воспроизводится, установите аудиозависимость:

```bash
pip install -e ".[audio]"
```

Или установите системный плеер, например `mpv`.

## Настройки

Показать текущую конфигурацию:

```bash
focus config
```

Изменить дневную цель:

```bash
focus config set daily_goal 120
```

Включить музыку по умолчанию:

```bash
focus config set default_music true
```

Изменить папку для добавленных треков:

```bash
focus config set music_dir ~/Music/focus
```

Доступные настройки:

- `daily_goal` — дневная цель в минутах;
- `default_music` — включать музыку по умолчанию, `true` или `false`;
- `default_track` — имя трека из `focus music list`;
- `time_format` — формат времени;
- `notifications` — настройка уведомлений;
- `music_dir` — папка, куда копируются добавленные треки.

## Где хранятся данные

Проект использует `platformdirs`, поэтому данные сохраняются в стандартных пользовательских папках операционной системы, а не внутри репозитория.

Показать точные пути на своем компьютере:

```bash
focus where
```

Обычно там находятся:

- SQLite-база со статистикой;
- локальная конфигурация;
- папка с добавленными музыкальными файлами.

## Обновление

Если проект уже был скачан с GitHub, обновите его так:

```bash
cd focus
git pull
source .venv/bin/activate
pip install -e .
```

На Windows PowerShell:

```powershell
cd focus
git pull
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Разработка

Установить зависимости для разработки:

```bash
git clone https://github.com/ebolotov2015-svg/focus.git
cd focus
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Запустить тесты:

```bash
pytest
```

Структура проекта:

```text
.
├── assets/
│   └── music/
├── src/
│   └── clarity_cli/
│       ├── cli.py
│       ├── config.py
│       ├── main.py
│       ├── models.py
│       ├── music.py
│       ├── paths.py
│       ├── stats.py
│       ├── storage.py
│       └── ui.py
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

## Частые проблемы

### Команда `focus` не найдена

Проверьте, что виртуальное окружение активировано:

```bash
source .venv/bin/activate
```

На Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

После этого переустановите проект:

```bash
pip install -e .
```

### PowerShell запрещает активацию окружения

Если Windows PowerShell не дает выполнить `Activate.ps1`, разрешите запуск скриптов для текущего пользователя:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Затем снова активируйте окружение:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Музыка не играет

Установите аудиозависимость:

```bash
pip install -e ".[audio]"
```

Или установите системный плеер. Например, на Arch Linux:

```bash
sudo pacman -S mpv
```

На Ubuntu/Debian:

```bash
sudo apt install mpv
```

### Не хочется ставить пакет глобально

Глобально ставить не нужно. Используйте `.venv`, как показано в разделе установки.

## Вклад в проект

Pull request'ы приветствуются. Желательно, чтобы изменения были небольшими, понятными и покрытыми тестами, если меняется логика.

Важные правила проекта:

- инструмент должен оставаться локальным;
- базовые команды должны работать без интернета;
- copyrighted музыку нельзя коммитить в репозиторий;
- пользовательские данные не должны сохраняться в рабочую папку проекта.

## Лицензия

MIT. Подробнее см. [LICENSE](LICENSE).
