# wav2mp3

Convert WAV files to 320 kbps MP3 with ID3 tags and cover art.

## Requirements

- Python 3.9+
- ffmpeg (`brew install ffmpeg`)

## Install

```bash
git clone <repo-url>
cd wav2mp3
pip install -e .
```

## Usage

```bash
wav2mp3 /path/to/folder           # convert all WAVs in a folder
wav2mp3 /path/to/track.wav        # convert a single file
wav2mp3 --cover art.jpg .         # use a specific cover image
wav2mp3 --cover https://example.com/cover.jpg /path/to/folder
```

### What it does

1. Scans the folder (or accepts a single `.wav` file) for WAV files and cover art
2. Prompts for shared tags (album, album artist, genre, year)
3. Parses track info from filenames (expected format: `## - Artist - Title.wav`)
4. Lets you review and edit tags before converting
5. Converts to 320 kbps CBR MP3 via ffmpeg
6. Applies ID3v2.4 tags and embeds cover art via mutagen
7. Moves original WAVs to a `wav/` subfolder (skipped in single-file mode)

### Filename formats

The parser handles these formats (in priority order):

- `01 - Artist - Track Title.wav` (preferred)
- `Artist - Track Title.wav`
- `Track Title.wav` (fallback — prompts for artist)

### Cover art

Use `--cover` to specify a local file or URL:

```bash
wav2mp3 --cover ~/Pictures/cover.jpg /path/to/folder
wav2mp3 --cover https://example.com/art.jpg track.wav
```

Without `--cover`, the tool auto-detects images in the folder in this order: `cover.jpg`, `cover.png`, `folder.jpg`, `artwork.jpg`, `artwork.png`, then any `.jpg`/`.png` found.
