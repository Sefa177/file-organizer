# file-organizer

A tiny command-line tool that cleans up a messy folder, like your Downloads, by sorting files into category subfolders. No dependencies, just Python.

```
$ file-organizer ~/Downloads --dry-run
holiday.jpg      ->  Images/holiday.jpg
invoice.pdf      ->  Documents/invoice.pdf
setup.exe        ->  Installers/setup.exe
song.mp3         ->  Audio/song.mp3

Dry run: 4 file(s) would be moved. Nothing was changed.
```

## Features

- Sorts files into `Images`, `Documents`, `Spreadsheets`, `Presentations`, `Videos`, `Audio`, `Archives`, `Installers`, `Code` and `Other`
- **Dry run** mode to preview every move before anything changes
- **Undo** to revert the last run
- Never overwrites: name clashes become `file (1).ext`, `file (2).ext`, ...
- Skips hidden files, symlinks and unfinished downloads (`.crdownload`, `.part`, `.tmp`)
- Optional `YYYY-MM` subfolders by modification date
- Only touches files directly inside the folder, never existing subfolders

## Installation

Requires Python 3.10 or newer.

```bash
pip install sefa177-file-organizer
```

If `pip` is not recognized, use `python -m pip install sefa177-file-organizer` (or `py -m pip ...` on Windows).

To install from source instead:

```bash
git clone https://github.com/Sefa177/file-organizer
cd file-organizer
pip install .
```

Then check that it works:

```bash
file-organizer --help
```

## Usage

```bash
file-organizer                      # organize ~/Downloads
file-organizer path/to/folder       # organize any folder
file-organizer --dry-run            # preview only
file-organizer --by-date            # Images/2026-11/photo.jpg
file-organizer --undo               # revert the last run
```

| Option | Description |
| --- | --- |
| `path` | Folder to organize (default: `~/Downloads`) |
| `-n`, `--dry-run` | Show what would happen without moving anything |
| `--by-date` | Also sort into `YYYY-MM` subfolders |
| `--undo` | Revert the last run in the folder |
| `-V`, `--version` | Show the version |

Each run saves a small log (`.file-organizer-log.json`) in the organized folder. `--undo` reads it to put every file back, and removes category folders that end up empty. Only the most recent run can be undone.

## Customizing categories

Edit the `CATEGORIES` dictionary in `file_organizer/organizer.py` to add extensions or new categories.

## License

MIT, see [LICENSE](LICENSE).
