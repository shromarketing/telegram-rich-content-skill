from __future__ import annotations

import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from bootstrap import parse_features
from check_voice import check_text
from doctor import local_checks
from init_material import FILES, slug
from preview_rich import render as render_preview
from publish_fallback import validate as validate_fallback
from validate_rich import MediaSpec


class WorkflowToolsTests(unittest.TestCase):
    def test_all_features_excludes_optional_apple_runtime(self) -> None:
        self.assertEqual(parse_features("all"), ["publisher", "youtube", "transcription"])

    def test_material_package_has_auditable_outputs(self) -> None:
        self.assertIn("evidence-map.md", FILES)
        self.assertIn("validation-report.md", FILES)
        self.assertEqual(slug("Новая мысль!"), "новая-мысль")

    def test_doctor_does_not_include_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Path(directory) / ".env"
            secret = "123456:DO_NOT_PRINT_THIS"
            env.write_text(f"TELEGRAM_BOT_TOKEN={secret}\n", encoding="utf-8")
            output = json.dumps([item.__dict__ for item in local_checks(env)])
            self.assertNotIn(secret, output)

    def test_voice_check_is_explainable(self) -> None:
        findings = check_text(
            "В современном мире всё меняется.",
            {"banned_phrases": ["в современном мире"]},
        )
        self.assertEqual(findings[0].rule, "banned_phrase")
        self.assertEqual(findings[0].level, "FAIL")

    def test_preview_is_clearly_labelled(self) -> None:
        preview = render_preview("<h1>Title</h1>")
        self.assertIn("Approximate local preview", preview)
        self.assertIn("<h1>Title</h1>", preview)

    def test_plain_and_album_fallback_limits(self) -> None:
        plain = Namespace(mode="plain", photo=[], video=[])
        self.assertEqual(validate_fallback(plain, "x" * 4096), [])
        self.assertTrue(validate_fallback(plain, "x" * 4097))
        album = Namespace(
            mode="album",
            photo=[MediaSpec("a", "a.jpg", "photo"), MediaSpec("b", "b.jpg", "photo")],
            video=[],
        )
        self.assertEqual(validate_fallback(album, "caption"), [])
        self.assertTrue(validate_fallback(album, "x" * 1025))


if __name__ == "__main__":
    unittest.main()
