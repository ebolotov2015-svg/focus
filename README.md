# clarity-cli

`clarity-cli` — локальный CLI-инструмент для фокус-сессий, фоновой музыки и простой статистики продуктивности.

Проект работает офлайн, хранит данные локально и не поставляет музыку в репозитории.

## Возможности

- запуск фокус-сессии из терминала;
- пауза, продолжение, остановка и просмотр статуса;
- учет активного времени без пауз;
- сохранение истории сессий в SQLite;
- статистика за день, неделю и месяц;
- красивый вывод через Rich: таблицы, панели, прогресс;
- добавление локальных `.mp3`, `.wav`, `.ogg` треков;
- локальная конфигурация через `platformdirs`.

## Быстрый запуск

Нужен Python 3.11 или новее.

Если проект уже скачан:

```bash
cd clarity-cli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
focus --help
```

Если запускаешь из GitHub-клона:

```bash
git clone <URL_ТВОЕГО_РЕПОЗИТОРИЯ>
cd <ИМЯ_ПАПКИ_РЕПОЗИТОРИЯ>
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
focus --help
```

На Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
focus --help
```

## Первый запуск

Запустить сессию:

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

Поставить на паузу и продолжить:

```bash
focus pause
focus resume
```

Остановить и сохранить сессию:

```bash
focus stop
```

Если сессия запущена через `focus start`, ее также можно остановить через `Ctrl+C`. Результат будет сохранен.

## Команды

```bash
focus start
focus start --music
focus start --duration 50
focus start --task "Написать документацию"
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

В статистике отображаются:

- сфокусированные минуты;
- количество сессий;
- средняя длительность сессии;
- дневная цель;
- прогресс к дневной цели.

## Музыка

Музыка необязательна. В репозитории нет аудиофайлов, потому что права на музыку зависят от конкретного файла и источника.

Добавить свой трек:

```bash
focus music add ~/Music/rain.ogg
```

Показать список треков:

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

Поддерживаются расширения `.mp3`, `.wav`, `.ogg`.

Для воспроизведения используется `pygame`, если он установлен. Если `pygame` нет, приложение попробует системные плееры: `mpv`, `ffplay`, `afplay` или `paplay`.

Опционально можно установить Python-аудиобэкенд:

```bash
pip install -e ".[audio]"
```

## Конфигурация

Показать текущую конфигурацию:

```bash
focus config
```

Доступные настройки:

- `daily_goal`: дневная цель в минутах;
- `default_music`: включать музыку по умолчанию, `true` или `false`;
- `default_track`: имя трека из `focus music list`;
- `time_format`: пользовательская настройка формата времени;
- `notifications`: пользовательская настройка уведомлений;
- `music_dir`: папка, куда копируются добавленные треки.

Примеры:

```bash
focus config set daily_goal 120
focus config set default_music false
focus config set music_dir ~/Music/clarity-cli
```

## Где хранятся данные

`clarity-cli` использует `platformdirs`, поэтому данные не сохраняются в случайных файлах внутри репозитория.

Показать точные пути:

```bash
focus where
```

Обычно там будут:

- SQLite-база со статистикой;
- папка с добавленными музыкальными файлами;
- локальная конфигурация.

## Разработка

Установить зависимости для разработки:

```bash
python -m venv .venv
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
└── tests/
```

## Частые проблемы

Если команда `focus` не найдена, проверь, что виртуальное окружение активировано:

```bash
source .venv/bin/activate
```

Если музыка не играет, установи один из системных плееров:

```bash
sudo pacman -S mpv
```

или установи опциональный аудиобэкенд:

```bash
pip install -e ".[audio]"
```

Если используешь Linux-дистрибутив с защищенным системным Python, не ставь пакет глобально. Используй `.venv`, как показано выше.

## Вклад в проект

Приветствуются небольшие и понятные pull request'ы. Проект должен оставаться локальным, работать без интернета и не содержать copyrighted музыку.

## Лицензия

MIT
