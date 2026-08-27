from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_rich import MediaSpec, validate_rich


class ValidateRichTests(unittest.TestCase):
    def test_valid_markup_and_media(self) -> None:
        markup = '<h2>Title</h2><img src="tg://photo?id=cover"/><p>Body</p>'
        result = validate_rich(
            markup,
            [MediaSpec("cover", "https://example.com/cover.jpg", "photo")],
        )
        self.assertTrue(result.ok, result.errors)

    def test_missing_media_is_rejected(self) -> None:
        result = validate_rich('<img src="tg://photo?id=cover"/>', [])
        self.assertFalse(result.ok)
        self.assertTrue(any("undeclared" in error for error in result.errors))

    def test_unused_media_is_rejected(self) -> None:
        result = validate_rich(
            "<p>Text only</p>",
            [MediaSpec("cover", "https://example.com/cover.jpg", "photo")],
        )
        self.assertFalse(result.ok)
        self.assertTrue(any("unused" in error for error in result.errors))

    def test_media_type_must_match_reference(self) -> None:
        result = validate_rich(
            '<video src="tg://video?id=clip"></video>',
            [MediaSpec("clip", "https://example.com/clip.mp4", "photo")],
        )
        self.assertFalse(result.ok)
        self.assertTrue(any("declared as photo" in error for error in result.errors))

    def test_unsupported_named_entity_is_rejected(self) -> None:
        result = validate_rich("<p>&copy;</p>", [])
        self.assertFalse(result.ok)
        self.assertTrue(any("unsupported named" in error for error in result.errors))

    def test_mismatched_tags_are_rejected(self) -> None:
        result = validate_rich("<p><b>Broken</p></b>", [])
        self.assertFalse(result.ok)
        self.assertTrue(any("does not match" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
