# Telegram Rich Content Skill

**Оформленные Telegram-посты из текста, статьи, интервью или YouTube-ролика — с заголовками, таблицами, раскрывающимися блоками, сносками, коллажами и настоящей свайп-каруселью.**

Публичный skill для Codex и Claude Code. Он помогает агенту:

- выбрать между ручной «Статьёй», обычным альбомом и Rich Message;
- создать rich-разметку без выдуманных Telegram-тегов;
- поднять отдельного бота через BotFather и выдать ему минимальные права;
- проверить публикацию локально и сначала отправить её в приватный тестовый канал;
- получить из YouTube оригинальное превью, субтитры, метаданные или аудио;
- транскрибировать аудио, если субтитров нет;
- не унести токен бота или ключ API в GitHub.

> Rich Messages появились в Telegram Bot API 10.1. На 27 августа 2026 года актуальна Bot API 10.3, а поддержка `sendRichMessage` есть в `aiogram`. Перед использованием агент должен сверить актуальную [документацию Telegram](https://core.telegram.org/bots/api).

## Что получится

```text
YouTube / статья / интервью / черновик
                ↓
       факты, таймкоды, медиа
                ↓
   Rich HTML или Rich Markdown
                ↓
       локальная валидация
                ↓
       приватный тестовый канал
                ↓
      проверка mobile + desktop
                ↓
   отдельное подтверждение продакшна
```

## Быстрая установка

### Codex

```bash
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.codex/skills/telegram-rich-content
```

Перезапустите Codex и попросите: `Используй $telegram-rich-content и оформи этот материал как rich-пост для Telegram`.

### Claude Code

```bash
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.claude/skills/telegram-rich-content
```

Перезапустите Claude Code и попросите: `Use the telegram-rich-content skill to turn this material into a Telegram rich post`.

Проектная установка и Windows-команды находятся в [references/installation.md](references/installation.md).

## Настройка publisher

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

В `.env` локально указываются токен и ID тестового канала. Файл уже исключён из Git.

Для опционального YouTube-конвейера:

```bash
python -m pip install -r requirements-youtube.txt
```

Проверка без отправки:

```bash
python scripts/publish_rich.py assets/rich-post.example.html \
  --photo cover=path/to/cover.jpg
```

Отправка в тестовый канал требует двух явных флагов:

```bash
python scripts/publish_rich.py assets/rich-post.example.html \
  --photo cover=path/to/cover.jpg \
  --send \
  --confirm-target=-1001234567890
```

Боевой канал выбирается отдельным `--environment production` и также требует точного подтверждения target. Тестовая отправка никогда не считается разрешением на боевую.

## YouTube → rich-пост

Сначала получить превью, метаданные и доступные субтитры:

```bash
python scripts/prepare_youtube.py 'https://youtu.be/VIDEO_ID' \
  --thumbnail --captions --language 'ru.*,en.*' \
  --output-dir output/video
```

Если субтитров нет, скачать только аудио:

```bash
python scripts/prepare_youtube.py 'https://youtu.be/VIDEO_ID' \
  --audio --output-dir output/video
```

Затем, при наличии локально настроенного `OPENAI_API_KEY`:

```bash
python scripts/transcribe_audio.py output/video/audio.mp3 \
  --language ru --out output/video/transcript.txt
```

Подробности и границы использования чужого контента: [references/youtube-workflow.md](references/youtube-workflow.md).

## Состав

- `SKILL.md` — маршрутизация и обязательные правила для агента;
- `references/` — установка, BotFather, форматирование, YouTube-процесс и диагностика;
- `scripts/validate_rich.py` — офлайн-проверка Rich HTML;
- `scripts/publish_rich.py` — безопасный one-shot publisher;
- `scripts/prepare_youtube.py` — превью, метаданные, субтитры и аудио через `yt-dlp`;
- `scripts/transcribe_audio.py` — транскрибация через OpenAI API с разбиением больших файлов;
- `requirements-youtube.txt` — отдельные зависимости YouTube-конвейера;
- `assets/` — нейтральный пример поста и шаблон контент-брифа;
- `tests/` — тесты критичных инвариантов без Telegram и API.

## Безопасность

Токены и ключи не надо присылать агенту сообщением. Их вводят локально в `.env`. Если токен бота попал в чат, скриншот или commit, его нужно немедленно отозвать через BotFather и выпустить новый. Политика раскрытия уязвимостей описана в [SECURITY.md](SECURITY.md).

## Лицензия и авторство

Проект распространяется по лицензии MIT. Подробности и уведомления о сторонних компонентах: [LICENSE](LICENSE) и [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

<sub>Адаптация и расширение: Roman Sharafutdinov. Основано на MIT-проекте [seozavr/tg-rich-post](https://github.com/seozavr/tg-rich-post): исходная грамматика Rich Messages, минимальный aiogram-пример и результаты живого прогона.</sub>
