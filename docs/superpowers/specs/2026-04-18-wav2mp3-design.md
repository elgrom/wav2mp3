# wav2mp3 — Design Spec

## Overview

A Python CLI tool that batch-converts WAV files in a folder to 320 kbps CBR MP3, applies ID3v2.4 tags (parsed from filenames with interactive override), embeds cover art, and moves original WAVs to a `wav/` subfolder.

## Goals

- Convert WAV to high-quality MP3 locally
- Parse ID3 tag data from filenames with interactive review and override
- Embed album cover art from a single image per folder
- Installable via pip from a git repo for portability across machines

## Non-Goals

- Batch renaming files
- Fetching metadata from online databases (MusicBrainz, Discogs, etc.)
- GUI

## Dependencies

- **Python 3.9+**
- **ffmpeg** — system dependency installed via Homebrew
- **mutagen** — Python library for ID3 tagging and cover art embedding

## Installation

```bash
git clone <repo-url>
cd wav2mp3
pip install -e .
```

Provides a `wav2mp3` CLI command via entry point.

## Usage

```bash
wav2mp3 /path/to/folder
```

## Project Structure

```
wav2mp3/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/
│   └── wav2mp3/
│       ├── __init__.py
│       ├── cli.py          # Argument parsing, main entry point
│       ├── scanner.py      # Find WAVs and cover art in a folder
│       ├── parser.py       # Filename to tag parsing logic
│       ├── prompts.py      # Interactive tag review/editing
│       ├── converter.py    # ffmpeg WAV to MP3 conversion
│       └── tagger.py       # ID3 tagging and cover art embedding
└── tests/
    ├── test_parser.py
    ├── test_scanner.py
    └── test_converter.py
```

## Workflow

1. **Scan folder** — find all `.wav` files and detect cover art image
2. **Set shared tags** — prompt for album, album artist, genre, year (year defaults to current year)
3. **Parse per-track tags** — attempt to extract track number, artist, title from each filename
4. **Review per-track tags** — display table of parsed results, allow editing by track number or accept all
5. **Convert** — run ffmpeg for each WAV to MP3 at 320 kbps CBR
6. **Tag** — apply ID3v2.4 tags and embed cover art via mutagen
7. **Move WAVs** — move originals to `wav/` subfolder
8. **Summary** — print conversion results

## Filename Parsing

Tries these patterns in order on each filename (after stripping the `.wav` extension):

1. `## - Artist - Title` — track number, artist, title (primary format)
2. `Artist - Title` — artist and title, no track number
3. `Title` — fallback, filename becomes title, artist left blank

Handles:
- Leading zeros in track numbers (`01`, `1`)
- Separator variations: ` - `, `-`, `_`
- Extra whitespace

## Cover Art Detection

Searches the folder for images in this priority order:

1. `cover.jpg`
2. `cover.png`
3. `folder.jpg`
4. `artwork.jpg`
5. `artwork.png`
6. First `.jpg` or `.png` file found

If no image is found, prints a warning and continues without embedding art.

## Interactive Prompts

### Shared Tags

```
Cover art found: cover.jpg

── Shared Tags ──────────────────────
Album:        [My Album]
Album Artist: [Various Artists]
Genre:        [Electronic]
Year:         [2026]
```

Each field shows a default in brackets. Press Enter to accept, or type a new value.

### Per-Track Review

```
── Tracks ───────────────────────────
 #  Artist          Title
 1  Some Artist     Track One
 2  Another Artist  Track Two
 3  ???             untitled

Edit track number (or Enter to accept all): 3
  Artist [???]: Real Artist
  Title [untitled]: Real Title

Proceed? [Y/n]:
```

Tracks with unparseable fields show `???` to flag them for review.

## Conversion

- Uses ffmpeg via subprocess
- Command: `ffmpeg -i input.wav -codec:a libmp3lame -b:a 320k output.mp3`
- Output MP3 is written to the same folder as the source WAV

## ID3 Tagging

Uses mutagen to write ID3v2.4 tags:

- `TIT2` — title
- `TPE1` — artist
- `TPE2` — album artist
- `TALB` — album
- `TRCK` — track number
- `TDRC` — year
- `TCON` — genre
- `APIC` — cover art (front cover, JPEG or PNG)

## File Organization

After successful conversion and tagging:

- MP3 files remain in the original folder
- WAV files are moved to a `wav/` subfolder (created if it doesn't exist)
- Cover art image stays in the original folder

## Error Handling

- **ffmpeg not installed:** print install instructions (`brew install ffmpeg`) and exit
- **No WAV files found:** print message and exit
- **Conversion failure on a track:** skip that track, report the error, continue with remaining tracks
- **No cover art found:** warn and continue without embedding art

## Testing

### test_parser.py

- Parses `01 - Artist - Title.wav` correctly (track, artist, title)
- Parses `Artist - Title.wav` (no track number)
- Parses `Title.wav` (fallback)
- Handles separator variations (`-`, ` - `, `_`)
- Handles leading zeros in track numbers
- Handles extra whitespace and special characters

### test_scanner.py

- Finds all `.wav` files in a folder
- Finds cover art following priority order
- Returns `None` when no images exist
- Ignores non-WAV audio files

### test_converter.py

- Verifies correct ffmpeg command construction (mocked subprocess)
- Handles conversion failure gracefully (mocked subprocess returning non-zero)
