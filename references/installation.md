# Installation: Codex and Claude Code

The repository root is the skill folder: it contains `SKILL.md`, `references/`, `scripts/`, and `assets/`.

## Codex — user installation

macOS or Linux:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.codex/skills/telegram-rich-content
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
git clone https://github.com/shromarketing/telegram-rich-content-skill.git `
  "$HOME\.codex\skills\telegram-rich-content"
```

Restart Codex after the first installation. Invoke it explicitly once:

```text
Use $telegram-rich-content to turn this article into a Telegram rich post. Validate it, but do not publish.
```

## Claude Code — user installation

macOS or Linux:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/shromarketing/telegram-rich-content-skill.git \
  ~/.claude/skills/telegram-rich-content
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
git clone https://github.com/shromarketing/telegram-rich-content-skill.git `
  "$HOME\.claude\skills\telegram-rich-content"
```

Restart Claude Code after the first installation. Claude Code also supports a project-only copy at:

```text
<project>/.claude/skills/telegram-rich-content/SKILL.md
```

Use a project installation when bot configuration and templates belong to only one repository. Do not commit that folder with a real `.env`.

## Update

Codex:

```bash
git -C ~/.codex/skills/telegram-rich-content pull --ff-only
```

Claude Code:

```bash
git -C ~/.claude/skills/telegram-rich-content pull --ff-only
```

Review changes before updating production automation.

## Python environment for the helper scripts

The editorial skill itself is plain Markdown. Helper scripts require Python 3.11 or
newer. On an older macOS, `/usr/bin/python3` may still be 3.9 even when a newer Homebrew
Python is installed. Check first:

```bash
python3 --version
```

From the installed skill folder, inspect the plan using your 3.11+ interpreter. Replace
`python3` with `python3.12`, for example, when needed:

```bash
python3 scripts/bootstrap.py --features all
python3 scripts/bootstrap.py --features all --apply
.venv/bin/python scripts/doctor.py
```

`bootstrap.py` creates an isolated environment. Add `--init-env` only when publisher
configuration is needed; it copies `.env.example` only when `.env` does not exist and
never overwrites an existing secret file. Select only what you need with `--features
publisher`, `youtube`, `transcription`, or a comma-separated combination.

Equivalent manual Windows PowerShell setup:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-youtube.txt -r requirements-transcription.txt
Copy-Item .env.example .env
```

Do not install dependencies globally with administrator rights. Keep each bot or publisher in an isolated virtual environment.

Optional Apple Silicon MLX backend:

```bash
python -m pip install -r requirements-apple-silicon.txt
```

No speech-to-text API key is required. The selected Whisper model downloads on first
use, so reserve disk space and use a trusted network for that one-time download. Start
with `small`; choose `large-v3` when final quality matters more than speed and memory.

## Verify discovery and scripts

```bash
python scripts/validate_rich.py assets/rich-post.example.html \
  --media cover=https://example.com/cover.jpg
python scripts/publish_rich.py --help
python scripts/prepare_youtube.py --help
python scripts/transcribe_audio.py --help
python scripts/doctor.py
```

The first command is offline. It should finish with `VALID` and must not require a bot token.

## Uninstall

Remove only the exact skill directory after inspecting the path. Deleting the skill does not delete Telegram bots, channel permissions, local bot projects, published messages, or API keys.
