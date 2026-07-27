import tempfile
import unittest
from pathlib import Path

from scripts.wiki_validation import valid_author_name, validate_wiki


class AuthorFormatTests(unittest.TestCase):
    def test_accepts_single_and_multiple_full_names(self):
        self.assertTrue(valid_author_name("Ada Lovelace"))
        self.assertTrue(valid_author_name("Marie Skłodowska Curie"))

    def test_rejects_ambiguous_formats(self):
        self.assertFalse(valid_author_name("Lovelace, Ada"))
        self.assertFalse(valid_author_name("ada_lovelace"))
        self.assertFalse(valid_author_name("Ada"))
        self.assertFalse(valid_author_name(["Ada Lovelace"]))

    def test_validates_paper_author_list(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paper_dir = root / "wiki" / "papers"
            paper_dir.mkdir(parents=True)
            (paper_dir / "good.md").write_text(
                "---\nauthors: [Ada Lovelace, Alan Turing]\n---\n", encoding="utf-8"
            )
            self.assertEqual(validate_wiki(root), [])

    def test_reports_invalid_single_author_string(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paper_dir = root / "wiki" / "papers"
            paper_dir.mkdir(parents=True)
            (paper_dir / "bad.md").write_text(
                "---\nauthors: Ada Lovelace\n---\n", encoding="utf-8"
            )
            errors = validate_wiki(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("non-empty list", errors[0])


if __name__ == "__main__":
    unittest.main()
