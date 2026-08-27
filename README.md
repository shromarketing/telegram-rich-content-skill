# Telegram Rich Content Skill

**Telegram-копирайтер для Codex и Claude Code: превращает сырую мысль, голосовую, статью, документ или видео в самостоятельный пост в вашем tone of voice — от обычного текста до Rich Message с заголовками, таблицами, раскрывающимися блоками, сносками, коллажами и свайп-каруселью.**

Skill помогает агенту:

- распаковать наговорённую или написанную мысль, не обедняя смысл;
- локально расшифровать голосовую, подкаст или видео без платного speech-to-text API;
- превратить статью или чужое видео в самостоятельный материал со ссылкой и авторством, а не в копию;
- провести короткий онбординг и работать по вашему редактируемому voice profile;
- задать только те вопросы, ответы на которые действительно меняют пост;
- выбрать обычный пост, ручную «Статью», альбом или Telegram Rich Message;
- получить из YouTube оригинальное превью, субтитры, метаданные или аудио;
- поднять отдельного бота через BotFather с минимальными правами;
- проверить rich-разметку офлайн и сначала отправить её в приватный тестовый канал;
- не унести токен, cookies или приватные исходники в GitHub.

> Rich Messages появились в Telegram Bot API 10.1. На 27 августа 2026 года актуальна Bot API 10.3, а поддержка `sendRichMessage` есть в `aiogram`. Перед использованием агент должен сверить актуальную [документацию Telegram](https://core.telegram.org/bots/api).

## Что можно дать агенту

```text
сырая мысль / голосовая / статья / документ / видео / несколько источников
                                  ↓
                существенные вопросы и допущения
                                  ↓
            факты, позиция автора, таймкоды, медиа
                                  ↓
          ваш tone of voice + редакционная структура
                                  ↓
         обычный пост / Article / альбом / Rich Message
                                  ↓
       локальная проверка → приватный тест → отдельный продакшн-гейт
```

Skill не обязан делать каждый пост «богатым». Если обычный текст понятнее и совместимее, агент должен выбрать его.

## Быстрая установка

### Codex

```bash
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.codex/skills/telegram-rich-content
```

Перезапустите Codex и попросите:

```text
Используй $telegram-rich-content. Преврати этот материал в подробный пост,
сохрани мой смысл, проверь разметку, но ничего не публикуй.
```

### Claude Code

```bash
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.claude/skills/telegram-rich-content
```

Перезапустите Claude Code и попросите:

```text
Use the telegram-rich-content skill to turn this material into a Telegram post
in my approved voice. Draft and validate it, but do not publish.
```

Проектная установка и Windows-команды: [references/installation.md](references/installation.md).

## Онбординг: превратить skill в вашего копирайтера

Для разовой задачи профиль не обязателен. Для постоянной работы дайте агенту 3–5 одобренных постов и попросите провести короткий онбординг:

```text
Используй $telegram-rich-content. Проведи короткий онбординг, изучи эти пять
эталонных постов и подготовь voice-profile.md. Покажи его мне на согласование,
ничего не публикуй.
```

Агент зафиксирует наблюдаемые правила: аудиторию, задачу канала, ритм, лексику, прямоту, юмор, форматирование, типичный CTA и антипримеры. Это редактируемый рабочий документ, а не скрытый психологический профиль. Шаблон: [assets/voice-profile.template.md](assets/voice-profile.template.md), полный процесс: [references/onboarding.md](references/onboarding.md).

Полезно также подключить к проекту актуальный файл с продуктами, биографией, ссылками и разрешёнными фактами. Тогда агент сможет быть не только оформителем, но и постоянным редактором: распаковывать идеи, предлагать структуру, проверять утверждения, адаптировать материал под аудиторию и сохранять одобренные паттерны.

## Бесплатная локальная транскрибация

Вместо OpenAI API используется open-source `faster-whisper`. Аудио обрабатывается на компьютере: нет API-ключа, лимита загрузки и оплаты за минуты. При первом запуске выбранная модель скачивается локально.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-youtube.txt

python scripts/transcribe_audio.py voice-note.m4a \
  --language ru --timestamps \
  --out transcript.txt
```

По умолчанию используется `small` как практичный баланс. Для финального качества можно выбрать `--model large-v3`; для CPU — `--device cpu --compute-type int8`. На Apple Silicon можно отдельно использовать `mlx-whisper`, но переносимым вариантом skill остаётся `faster-whisper`. Подробнее: [references/youtube-workflow.md](references/youtube-workflow.md).

## YouTube → пост

Сначала получить оригинальное превью, метаданные и доступные субтитры:

```bash
python scripts/prepare_youtube.py 'https://youtu.be/VIDEO_ID' \
  --thumbnail --captions --language 'ru.*,en.*' \
  --output-dir output/video
```

Если субтитров нет, скачать только аудио и расшифровать локально:

```bash
python scripts/prepare_youtube.py 'https://youtu.be/VIDEO_ID' \
  --audio --output-dir output/video

python scripts/transcribe_audio.py output/video/VIDEO_ID.mp3 \
  --language ru --model small --timestamps \
  --out output/video/transcript.txt
```

Для чужого контента skill требует самостоятельный пересказ, ссылку и авторство; он не предназначен для перепубликации полной расшифровки или обхода ограничений доступа.

## Настройка Telegram publisher

Publisher нужен только для автоматической отправки. Создание черновиков, локальная расшифровка и ручная Telegram «Статья» работают без него.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

В `.env` локально указываются токен и ID тестового канала. Проверка без отправки:

```bash
python scripts/publish_rich.py assets/rich-post.example.html \
  --photo cover=path/to/cover.jpg
```

Тестовая отправка требует двух явных флагов:

```bash
python scripts/publish_rich.py assets/rich-post.example.html \
  --photo cover=path/to/cover.jpg \
  --send \
  --confirm-target=-1001234567890
```

Боевой канал выбирается отдельным `--environment production` и тоже требует точного подтверждения target. Успешный тест никогда не считается разрешением на боевую публикацию.

## Примеры запросов

```text
Вот сырая мысль. Сделай из неё подробный Telegram-пост в моём tone of voice.
Не сокращай важные аргументы, задай вопросы только по существенным пробелам.
```

```text
Вот голосовая. Расшифруй её локально без платного API, отдели тезис от повторов
и подготовь две версии поста: обычную и rich. Ничего не отправляй.
```

```text
Преврати эту статью в самостоятельный пост: сохрани ссылки, отдели идеи автора
от моего комментария, не копируй исходник и добавь понятный CTA.
```

```text
Изучи YouTube-ролик, возьми оригинальное превью и субтитры, а если их нет —
локально расшифруй аудио. Сделай подробный rich-пост и подготовь тест.
```

## Состав

- `SKILL.md` — маршрутизация и обязательные правила агента;
- `references/onboarding.md` — первый запуск и подключение tone of voice;
- `references/source-modes.md` — мысль, голос, статья, документ, видео и несколько источников;
- `references/` — установка, BotFather, форматирование, YouTube-процесс и диагностика;
- `scripts/transcribe_audio.py` — локальная транскрибация через `faster-whisper`;
- `scripts/prepare_youtube.py` — превью, метаданные, субтитры и аудио через `yt-dlp`;
- `scripts/validate_rich.py` — офлайн-проверка Rich HTML;
- `scripts/publish_rich.py` — безопасный one-shot publisher;
- `assets/` — пример rich-поста, контент-бриф и шаблон voice profile;
- `tests/` — тесты критичных инвариантов без Telegram, моделей и API.

## Безопасность

Токены не надо присылать агенту сообщением: их вводят локально в `.env`. Локальная транскрибация не требует speech-to-text API-ключа. Если токен бота попал в чат, скриншот или commit, его нужно немедленно отозвать через BotFather и выпустить новый. Подробности: [SECURITY.md](SECURITY.md).

## Лицензия и авторство

Проект распространяется по лицензии MIT. Уведомления о сторонних компонентах: [LICENSE](LICENSE) и [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

<sub>Адаптация и расширение: Roman Sharafutdinov. Основано на MIT-проекте [seozavr/tg-rich-post](https://github.com/seozavr/tg-rich-post): исходная грамматика Rich Messages, минимальный aiogram-пример и результаты живого прогона.</sub>
