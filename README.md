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

## Install

Requires Python 3.8 or newer.

```bash
pip install sefa177-file-organizer
```

The package is called `sefa177-file-organizer` on PyPI (the plain `file-organizer` name belongs to another project), but the command it installs is still `file-organizer`.

Or install from source:

```bash
git clone https://github.com/Sefa177/file-organizer.git
cd file-organizer
pip install .
```

Or run it without installing:

```bash
python -m file_organizer ~/Downloads
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

## Development

```bash
python -m unittest discover -s tests -v
```

## Publishing to PyPI (maintainers)

1. Create an account on [pypi.org](https://pypi.org), turn on two-factor authentication, then create an API token under *Account settings > API tokens*.
2. Bump the version in both `pyproject.toml` and `file_organizer/__init__.py`. PyPI never lets you upload the same version twice.
3. Build and check the package:

   ```bash
   python -m pip install --upgrade build twine
   python -m build
   python -m twine check dist/*
   ```

4. Upload it. When asked, use `__token__` as the username and your API token as the password:

   ```bash
   python -m twine upload dist/*
   ```

To rehearse first, create an account on [test.pypi.org](https://test.pypi.org) and upload there with `python -m twine upload --repository testpypi dist/*`.

## License

MIT, see [LICENSE](LICENSE).
