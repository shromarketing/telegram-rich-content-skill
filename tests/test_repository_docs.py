from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class RepositoryDocsTests(unittest.TestCase):
    def test_relative_markdown_links_exist(self) -> None:
        broken: list[str] = []
        for document in ROOT.rglob("*.md"):
            if ".git" in document.parts:
                continue
            for raw in LINK_RE.findall(document.read_text(encoding="utf-8")):
                target = raw.strip().split(maxsplit=1)[0].strip("<>")
                if target.startswith(("http://", "https://", "mailto:", "tg://", "#")):
                    continue
                path_text = unquote(target.split("#", 1)[0])
                if path_text and not (document.parent / path_text).exists():
                    broken.append(f"{document.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [])

    def test_skill_description_fits_claude_limit(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r'^description: "([^"]+)"$', skill, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        assert match is not None
        self.assertLessEqual(len(match.group(1)), 200)

    def test_release_version_is_documented(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## [{version}]", changelog)


if __name__ == "__main__":
    unittest.main()
