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
wav2mp3 /path/to/folder
```

### What it does

1. Scans the folder for `.wav` files and a cover art image
2. Prompts for shared tags (album, album artist, genre, year)
3. Parses track info from filenames (expected format: `## - Artist - Title.wav`)
4. Lets you review and edit tags before converting
5. Converts to 320 kbps CBR MP3 via ffmpeg
6. Applies ID3v2.4 tags and embeds cover art via mutagen
7. Moves original WAVs to a `wav/` subfolder

### Filename formats

The parser handles these formats (in priority order):

- `01 - Artist - Track Title.wav` (preferred)
- `Artist - Track Title.wav`
- `Track Title.wav` (fallback — prompts for artist)

### Cover art

Looks for images in this order: `cover.jpg`, `cover.png`, `folder.jpg`, `artwork.jpg`, `artwork.png`, then any `.jpg`/`.png` in the folder.
