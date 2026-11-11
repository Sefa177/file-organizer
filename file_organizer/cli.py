"""Command-line interface for file-organizer."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .organizer import apply_moves, plan_moves, undo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Sort a messy folder (like Downloads) into category subfolders.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="~/Downloads",
        help="folder to organize (default: ~/Downloads)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="show what would happen without moving anything",
    )
    parser.add_argument(
        "--by-date",
        action="store_true",
        help="also sort into YYYY-MM subfolders by modification date",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="revert the last run in this folder",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = Path(args.path).expanduser().resolve()

    if not source.is_dir():
        print(f"Error: {source} is not a folder.", file=sys.stderr)
        return 1

    if args.undo:
        try:
            restored = undo(source)
        except FileNotFoundError:
            print("Nothing to undo: no log found in this folder.", file=sys.stderr)
            return 1
        print(f"Restored {len(restored)} file(s).")
        return 0

    moves = plan_moves(source, by_date=args.by_date)
    if not moves:
        print("Nothing to organize.")
        return 0

    for move in moves:
        print(f"{move.src.name}  ->  {move.dst.relative_to(source)}")

    if args.dry_run:
        print(f"\nDry run: {len(moves)} file(s) would be moved. Nothing was changed.")
        return 0

    done = apply_moves(moves, source)
    print(f"\nMoved {len(done)} file(s). Run with --undo to revert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
