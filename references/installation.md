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

From the installed skill folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell activation:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Do not install dependencies globally with administrator rights. Keep each bot or publisher in an isolated virtual environment.

Install YouTube and transcription dependencies only when that workflow is needed:

```bash
python -m pip install -r requirements-youtube.txt
```

## Verify discovery and scripts

```bash
python scripts/validate_rich.py assets/rich-post.example.html \
  --media cover=https://example.com/cover.jpg
python scripts/publish_rich.py --help
python scripts/prepare_youtube.py --help
python scripts/transcribe_audio.py --help
```

The first command is offline. It should finish with `VALID` and must not require a bot token.

## Uninstall

Remove only the exact skill directory after inspecting the path. Deleting the skill does not delete Telegram bots, channel permissions, local bot projects, published messages, or API keys.
