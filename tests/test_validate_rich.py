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

    def test_unknown_tag_is_rejected(self) -> None:
        result = validate_rich("<script>alert(1)</script>", [])
        self.assertFalse(result.ok)
        self.assertTrue(any("unsupported Rich HTML tag" in error for error in result.errors))

    def test_unknown_attribute_is_rejected(self) -> None:
        result = validate_rich('<p class="hidden">Text</p>', [])
        self.assertFalse(result.ok)
        self.assertTrue(any("unsupported attribute" in error for error in result.errors))

    def test_javascript_url_is_rejected(self) -> None:
        result = validate_rich('<a href="javascript:alert(1)">Click</a>', [])
        self.assertFalse(result.ok)
        self.assertTrue(any("URL scheme" in error for error in result.errors))

    def test_internal_footnote_anchor_is_accepted(self) -> None:
        result = validate_rich(
            '<p>Claim<a href="#note-1">[1]</a></p>'
            '<tg-reference name="note-1">Source</tg-reference>',
            [],
        )
        self.assertTrue(result.ok, result.errors)

    def test_draft_tag_requires_explicit_opt_in(self) -> None:
        markup = "<tg-thinking>Working</tg-thinking>"
        self.assertFalse(validate_rich(markup, []).ok)
        self.assertTrue(validate_rich(markup, [], allow_draft_tags=True).ok)

    def test_current_rich_components_are_accepted(self) -> None:
        markup = (
            "<blockquote expandable>Quote</blockquote>"
            '<table bordered compact><tr><th align="left">A</th>'
            '<td colspan="2">B</td></tr></table>'
            '<tg-button-row align="center"><tg-button type="url" '
            'url="https://example.com">Open</tg-button></tg-button-row>'
        )
        result = validate_rich(markup, [])
        self.assertTrue(result.ok, result.errors)


if __name__ == "__main__":
    unittest.main()
