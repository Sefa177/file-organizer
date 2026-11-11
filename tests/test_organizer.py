import tempfile
import unittest
from pathlib import Path

from file_organizer.cli import main
from file_organizer.organizer import (
    LOG_NAME,
    apply_moves,
    categorize,
    plan_moves,
    undo,
)


def touch(folder: Path, name: str, text: str = "x") -> Path:
    path = folder / name
    path.write_text(text)
    return path


class CategorizeTests(unittest.TestCase):
    def test_known_extensions(self):
        self.assertEqual(categorize(Path("a.PNG")), "Images")
        self.assertEqual(categorize(Path("report.pdf")), "Documents")
        self.assertEqual(categorize(Path("setup.exe")), "Installers")

    def test_unknown_extension_goes_to_other(self):
        self.assertEqual(categorize(Path("weird.xyz")), "Other")
        self.assertEqual(categorize(Path("noextension")), "Other")


class OrganizeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def test_moves_files_into_categories(self):
        touch(self.root, "photo.jpg")
        touch(self.root, "notes.txt")
        apply_moves(plan_moves(self.root), self.root)
        self.assertTrue((self.root / "Images" / "photo.jpg").exists())
        self.assertTrue((self.root / "Documents" / "notes.txt").exists())

    def test_skips_hidden_and_partial_downloads(self):
        touch(self.root, ".hidden.txt")
        touch(self.root, "movie.mp4.crdownload")
        self.assertEqual(plan_moves(self.root), [])

    def test_does_not_touch_existing_folders(self):
        (self.root / "Projects").mkdir()
        touch(self.root / "Projects", "keep.txt")
        self.assertEqual(plan_moves(self.root), [])

    def test_name_collision_gets_numbered(self):
        (self.root / "Documents").mkdir()
        touch(self.root / "Documents", "a.txt", "old")
        touch(self.root, "a.txt", "new")
        apply_moves(plan_moves(self.root), self.root)
        self.assertEqual((self.root / "Documents" / "a.txt").read_text(), "old")
        self.assertEqual((self.root / "Documents" / "a (1).txt").read_text(), "new")

    def test_dry_run_changes_nothing(self):
        touch(self.root, "photo.jpg")
        code = main([str(self.root), "--dry-run"])
        self.assertEqual(code, 0)
        self.assertTrue((self.root / "photo.jpg").exists())
        self.assertFalse((self.root / "Images").exists())

    def test_by_date_adds_month_folder(self):
        touch(self.root, "photo.jpg")
        moves = plan_moves(self.root, by_date=True)
        parts = moves[0].dst.relative_to(self.root).parts
        self.assertEqual(parts[0], "Images")
        self.assertRegex(parts[1], r"^\d{4}-\d{2}$")

    def test_undo_restores_files_and_removes_empty_folders(self):
        touch(self.root, "photo.jpg")
        touch(self.root, "notes.txt")
        apply_moves(plan_moves(self.root), self.root)
        self.assertTrue((self.root / LOG_NAME).exists())
        undo(self.root)
        self.assertTrue((self.root / "photo.jpg").exists())
        self.assertTrue((self.root / "notes.txt").exists())
        self.assertFalse((self.root / "Images").exists())
        self.assertFalse((self.root / LOG_NAME).exists())

    def test_undo_without_log_raises(self):
        with self.assertRaises(FileNotFoundError):
            undo(self.root)

    def test_cli_undo_without_log_returns_error(self):
        self.assertEqual(main([str(self.root), "--undo"]), 1)

    def test_cli_missing_folder_returns_error(self):
        self.assertEqual(main([str(self.root / "nope")]), 1)


if __name__ == "__main__":
    unittest.main()
