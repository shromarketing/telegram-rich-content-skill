<div align="center">

![Telegram Rich Content — исходный материал превращается в структурированный и безопасно публикуемый пост](assets/showcase/hero.png)

# Telegram Rich Content Skill

**Превращает сырую мысль, голосовую, статью, документ, подкаст или видео в
самостоятельный Telegram-пост в вашем согласованном tone of voice — от обычного текста
до Rich Message с заголовками, таблицами, раскрывающимися блоками, сносками, медиа и
свайп-каруселью.**

[![release](https://img.shields.io/github/v/release/shromarketing/telegram-rich-content-skill?display_name=tag&style=flat-square)](https://github.com/shromarketing/telegram-rich-content-skill/releases)
[![tests](https://img.shields.io/github/actions/workflow/status/shromarketing/telegram-rich-content-skill/test.yml?branch=main&style=flat-square&label=tests)](https://github.com/shromarketing/telegram-rich-content-skill/actions)
[![license](https://img.shields.io/github/license/shromarketing/telegram-rich-content-skill?style=flat-square)](LICENSE)

[English](README.md) · [Быстрый старт](#установка-за-минуту) ·
[Пример](docs/SHOWCASE.md) · [Безопасность](docs/SECURITY_MODEL.md)

</div>

## Это не очередной «генератор постов»

Обычный AI-копирайтер начинает с пустого листа и заканчивает сгенерированным текстом.
Этот skill даёт Codex или Claude Code полноценный редакционный процесс:

- принять мысль, аудио, ссылку, документ, YouTube-ролик или несколько источников;
- локально расшифровать аудио открытой Whisper-моделью без платного speech-to-text API;
- до написания текста собрать карту доказательств и не потерять источники утверждений;
- провести онбординг по 3–5 одобренным постам и работать по редактируемому voice profile;
- выбрать минимально достаточный формат: обычный пост, ручная «Статья», альбом или Rich
  Message;
- строго проверить Rich HTML до любого сетевого действия;
- сделать локальное превью, протестировать пост в приватном канале и отдельно запросить
  разрешение на продакшн.

![Процесс от источника до поста](assets/showcase/pipeline.svg)

## Кому подойдёт

- экспертам и предпринимателям, которые думают голосовыми, а публикуют содержательные
  посты;
- редакторам и контент-командам, перерабатывающим интервью, статьи и видео;
- агентствам, которым нужен воспроизводимый и проверяемый процесс для клиентов;
- разработчикам, изучающим Telegram Bot API Rich Messages;
- пользователям Codex и Claude Code, которым нужен постоянный AI-редактор, а не один
  удачный промпт.

Это не спам-инструмент, не способ обхода авторских прав и не автономный продакшн-бот.

## Что умеет

| Возможность | Результат | Сеть по умолчанию? |
|---|---|---|
| Agent skill | Редакторская логика, работа с источниками, онбординг, гейты | Нет |
| Пакет материала | Источник → транскрипт → доказательства → бриф → версии → QA | Нет |
| YouTube helper | Метаданные, оригинальное превью, субтитры или аудио через `yt-dlp` | Да |
| Локальная транскрибация | TXT, Markdown, SRT, VTT, JSON, checkpoint, word timestamps | Только загрузка модели |
| Voice guardrails | Объяснимые проверки фраз, длины, эмодзи и CTA | Нет |
| Rich validator | Теги, атрибуты, URL, лимиты, вложенность, entities, media IDs | Нет |
| Локальное превью | Приблизительное отображение в браузере | Нет |
| Publisher | Rich Message, обычный пост или альбом из 2–10 фото/видео | Только с `--send` |
| Doctor | Диагностика установки; опциональная read-only проверка Telegram | Нет, если не попросить |

## Установка за минуту

### Codex

```bash
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.codex/skills/telegram-rich-content
```

### Claude Code

```bash
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.claude/skills/telegram-rich-content
```

Перезапустите агента и попросите:

```text
Используй $telegram-rich-content. Преврати этот материал в подробный пост в моём
согласованном tone of voice. Сохрани доказательства, подготовь обычную и rich-версию,
всё проверь, но ничего не публикуй.
```

Оба агента находят инструкции через корневой [`SKILL.md`](SKILL.md). Проектная установка
и Windows-команды описаны в [`references/installation.md`](references/installation.md).

## Дополнительные инструменты — только нужные

Для helper scripts нужен Python 3.11+. Сначала посмотрите план, затем примените и
проверьте. Если системный Python старее, замените `python3`, например, на `python3.12`:

```bash
python3 scripts/bootstrap.py --features all
python3 scripts/bootstrap.py --features all --apply
.venv/bin/python scripts/doctor.py
```

Группы: `publisher`, `youtube`, `transcription` и опциональная `apple` для Apple Silicon.
Установщик создаёт изолированную `.venv`, не перезаписывает существующий `.env` и не
обращается к Telegram. Добавьте `--init-env`, только если нужна настройка publisher.

## Из любого полезного источника

### Сырая мысль или голосовая

Агент отделяет тезис от повторов, задаёт только вопросы, способные изменить смысл, и не
обедняет материал механическим сокращением.

### Статья или документ

Агент разделяет мысли автора источника и ваш комментарий, сохраняет ссылки и авторство,
делает самостоятельный материал, а не копию.

### YouTube-ролик

```bash
python scripts/prepare_youtube.py 'https://youtu.be/VIDEO_ID' \
  --thumbnail --captions --language 'ru.*,en.*' --output-dir output/video
```

Если субтитров нет, достаточно скачать аудио и расшифровать его локально:

```bash
python scripts/prepare_youtube.py URL --audio --output-dir output/video
python scripts/transcribe_audio.py output/video/VIDEO_ID.mp3 \
  --language ru --out output/video/transcript.md \
  --checkpoint output/video/progress.jsonl
```

Доступны `txt`, `md`, `srt`, `vtt`, `json`, таймкоды слов, смысловые блоки и продолжение
длинной расшифровки через `--resume`. Переносимый backend — `faster-whisper`; на Apple
Silicon можно подключить `mlx-whisper`. OpenAI API и оплата за минуты не нужны. При
первом запуске модель может скачаться локально. Подробнее:
[`references/youtube-workflow.md`](references/youtube-workflow.md).

## Ваш стиль — без выдуманного «процента похожести»

Дайте агенту 3–5 одобренных постов. Он подготовит проектный voice profile с наблюдаемыми
правилами: аудитория, ритм, лексика, прямота, юмор, форматирование, CTA, работа с фактами
и антипримеры. Вы его проверяете и редактируете.

Для объективных ограничений можно подключить:

```bash
python scripts/check_voice.py post-plain.md --profile style-check.json
```

Проверка называет каждое сработавшее правило и не изображает измерение личности,
аутентичности или художественного качества. Шаблоны:
[`voice-profile.template.md`](assets/voice-profile.template.md) и
[`style-check.template.json`](assets/style-check.template.json).

## Один проверяемый пакет на каждый материал

```bash
python scripts/init_material.py "интервью о запуске"
```

```text
materials/интервью-о-запуске/
├── source.md                 # происхождение, права, сырой материал
├── transcript.md             # таймкоды и спикеры
├── evidence-map.md           # утверждение → источник → уверенность
├── brief.md                  # аудитория, цель, CTA, ограничения
├── voice-profile-used.md     # версия профиля и примеры
├── post-plain.md             # совместимый fallback
├── post-rich.html            # Telegram Rich Message
├── media/                    # явные медиафайлы
└── validation-report.md      # техническая и человеческая приёмка
```

Полный синтетический пример: [`examples/source-to-post`](examples/source-to-post).

## Проверка и превью — без отправки

```bash
python scripts/validate_rich.py examples/source-to-post/post-rich.html
python scripts/preview_rich.py examples/source-to-post/post-rich.html \
  --out output/preview.html
```

Валидатор ориентирован на Telegram Bot API 10.3 и отклоняет неподдерживаемые теги и
атрибуты, event handlers, inline styles, опасные URL-схемы, сломанную вложенность,
неподдерживаемые named entities, превышение лимитов и ошибки сопоставления media ID.
Браузерное превью намеренно приблизительное: финальная проверка — в актуальных Telegram
Desktop и mobile.

## Безопасная отправка в Telegram

Создайте отдельного бота через `@BotFather`, сначала добавьте его только в приватный
тестовый канал и выдайте минимальное право **Post Messages**. Токен храните в локальном
`.env`, не вставляйте в промпты и не коммитьте.

Dry run:

```bash
python scripts/publish_rich.py draft.html --photo cover=cover.jpg
python scripts/publish_fallback.py post-plain.md --mode plain
```

Реальная тестовая отправка требует двух независимых гейтов:

```bash
python scripts/publish_rich.py draft.html --photo cover=cover.jpg \
  --send --confirm-target=-1001234567890
```

Продакшн дополнительно выбирается `--environment production`, но всё равно требует
`--send` и точного совпадения target. Успешный тест не является разрешением на боевую
публикацию. Полная инструкция: [`references/botfather-setup.md`](references/botfather-setup.md).

## Когда Rich действительно нужен

Rich Messages поддерживают заголовки, чек-листы, таблицы, цитаты, `details`, сноски,
математику, карты, документы, коллажи и настоящие свайп-слайдшоу. Старые клиенты могут
их не отобразить, поэтому workflow всегда предусматривает обычный пост или альбом.

## Принципы

1. **Смысл важнее оформления.** Каждый rich-блок должен помогать читателю.
2. **Доказательства раньше текста.** Утверждения, цитаты, ссылки и таймкоды проверяемы.
3. **Local first.** Без платных API и лишних загрузок исходников.
4. **Progressive disclosure.** Агент читает только нужные разделы skill.
5. **Dry run по умолчанию.** Черновик не равен публикации, тест не равен продакшну.
6. **Человек сохраняет власть.** Voice, права, target и финальный вид подтверждает он.

## Честные ограничения

- Rich Messages требуют актуальных клиентов Telegram.
- Валидатор не заменяет сервер Telegram.
- Локальное превью не является эмулятором Telegram.
- Диаризация спикеров не встроена: это отдельный тяжёлый pipeline с собственными
  моделями и условиями лицензирования.
- Публичный чужой материал нужно трансформировать и атрибутировать; skill не даёт права
  перепубликовать полный транскрипт или обходить ограничения доступа.

## Устройство репозитория

- [`SKILL.md`](SKILL.md) — инструкции агента и обязательные гейты;
- [`references/`](references) — онбординг, источники, установка, форматирование,
  Telegram, YouTube, troubleshooting и полный workflow;
- [`scripts/`](scripts) — детерминированные локальные инструменты;
- [`assets/`](assets) — шаблоны, пример Rich HTML и визуалы;
- [`examples/source-to-post`](examples/source-to-post) — полный синтетический пример;
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — архитектура и границы доверия;
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — правила разработки.

## Вклад в проект

Приветствуются баг-репорты, точечные функции, Telegram-обновления, синтетические примеры
и улучшение кроссплатформенности. Core-тесты должны оставаться офлайн; приватные
материалы нельзя использовать как fixtures. См. [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Лицензия и авторство

MIT. См. [`LICENSE`](LICENSE), [`SECURITY.md`](SECURITY.md) и
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

<sub>Создание и расширение: Roman Sharafutdinov. Грамматика Rich Messages и исходный
минимальный эксперимент с aiogram адаптированы из MIT-проекта
[seozavr/tg-rich-post](https://github.com/seozavr/tg-rich-post).</sub>
