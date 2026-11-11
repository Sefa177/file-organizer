"""Core logic: decide where files belong and move them."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

CATEGORIES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".tiff", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".epub"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".odp", ".key"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".apk"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".sh", ".ipynb"},
}
OTHER = "Other"

# Files still being downloaded by browsers; never touch these.
PARTIAL_SUFFIXES = {".crdownload", ".part", ".tmp", ".download", ".partial"}

LOG_NAME = ".file-organizer-log.json"


@dataclass(frozen=True)
class Move:
    src: Path
    dst: Path


def categorize(path: Path) -> str:
    """Return the category folder name for a file, based on its extension."""
    ext = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return OTHER


def is_skipped(path: Path) -> bool:
    """Hidden files, partial downloads, symlinks and our own log are left alone."""
    return (
        path.name.startswith(".")
        or path.suffix.lower() in PARTIAL_SUFFIXES
        or path.name == LOG_NAME
        or path.is_symlink()
    )


def unique_destination(dest: Path, reserved: set[Path] | None = None) -> Path:
    """Return a path that does not exist yet, adding ' (1)', ' (2)'... if needed."""
    reserved = reserved if reserved is not None else set()
    candidate = dest
    counter = 1
    while candidate.exists() or candidate in reserved:
        candidate = dest.with_name(f"{dest.stem} ({counter}){dest.suffix}")
        counter += 1
    return candidate


def plan_moves(source: Path, by_date: bool = False) -> list[Move]:
    """Work out where every top-level file in `source` should go. Moves nothing."""
    moves: list[Move] = []
    reserved: set[Path] = set()
    for item in sorted(source.iterdir()):
        if not item.is_file() or is_skipped(item):
            continue
        folder = source / categorize(item)
        if by_date:
            stamp = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m")
            folder = folder / stamp
        dst = unique_destination(folder / item.name, reserved)
        reserved.add(dst)
        moves.append(Move(item, dst))
    return moves


def apply_moves(moves: list[Move], source: Path) -> list[Move]:
    """Perform the moves and save a log so the run can be undone."""
    done: list[Move] = []
    try:
        for move in moves:
            move.dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.src), str(move.dst))
            done.append(move)
    finally:
        _write_log(source, done)
    return done


def _write_log(source: Path, moves: list[Move]) -> None:
    if not moves:
        return
    data = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "moves": [{"from": str(m.src), "to": str(m.dst)} for m in moves],
    }
    (source / LOG_NAME).write_text(json.dumps(data, indent=2), encoding="utf-8")


def undo(source: Path) -> list[Move]:
    """Revert the last run in `source`. Raises FileNotFoundError if there is no log."""
    log = source / LOG_NAME
    if not log.exists():
        raise FileNotFoundError(f"No undo log found in {source}")
    data = json.loads(log.read_text(encoding="utf-8"))
    restored: list[Move] = []
    for entry in reversed(data["moves"]):
        moved = Path(entry["to"])
        original = Path(entry["from"])
        if not moved.exists():
            continue
        target = unique_destination(original)
        shutil.move(str(moved), str(target))
        restored.append(Move(moved, target))
        _prune_empty_dirs(moved.parent, stop=source)
    log.unlink()
    return restored


def _prune_empty_dirs(folder: Path, stop: Path) -> None:
    """Remove now-empty category folders, but never `stop` itself or anything above."""
    while folder != stop and stop in folder.parents:
        try:
            folder.rmdir()
        except OSError:
            break
        folder = folder.parent
