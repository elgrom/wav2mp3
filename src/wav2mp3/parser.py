import re
from pathlib import Path


def parse_filename(filename: str) -> dict:
    """Parse a WAV filename into track number, artist, and title.

    Tries patterns in order:
    1. ## - Artist - Title.wav  (dash/underscore separator)
    2. ##. Artist - Title.wav   (dot separator)
    3. ## Artist - Title.wav    (space-only after track number)
    4. ##. Title.wav            (dot separator, no artist)
    5. Artist - Title.wav
    6. Title.wav (fallback)
    """
    stem = Path(filename).stem

    # Pattern 1: track_number <dash/underscore> artist <dash/underscore> title
    match = re.match(
        r"^(\d{1,3})\s*[-_]\s*(.+?)\s*[-_]\s*(.+)$",
        stem,
    )
    if match:
        track_str, artist, title = match.groups()
        return {
            "track": int(track_str),
            "artist": artist.strip(),
            "title": title.strip(),
        }

    # Pattern 2: track_number. artist - title  (dot after track number)
    match = re.match(
        r"^(\d{1,3})\.\s*(.+?)\s*[-_]\s*(.+)$",
        stem,
    )
    if match:
        track_str, artist, title = match.groups()
        return {
            "track": int(track_str),
            "artist": artist.strip(),
            "title": title.strip(),
        }

    # Pattern 3: track_number <space> artist - title  (space only after number)
    match = re.match(
        r"^(\d{1,3})\s+(.+?)\s*[-_]\s*(.+)$",
        stem,
    )
    if match:
        track_str, artist, title = match.groups()
        return {
            "track": int(track_str),
            "artist": artist.strip(),
            "title": title.strip(),
        }

    # Pattern 4: track_number. title  (dot, no artist)
    match = re.match(r"^(\d{1,3})\.\s*(.+)$", stem)
    if match:
        track_str, title = match.groups()
        return {
            "track": int(track_str),
            "artist": None,
            "title": title.strip(),
        }

    # Pattern 5: artist <sep> title (no track number)
    match = re.match(r"^(.+?)\s*[-_]\s*(.+)$", stem)
    if match:
        left, right = match.groups()
        if not re.match(r"^\d{1,3}$", left.strip()):
            return {
                "track": None,
                "artist": left.strip(),
                "title": right.strip(),
            }

    # Pattern 6: fallback — entire stem is the title
    return {"track": None, "artist": None, "title": stem.strip()}


def build_output_filename(track: dict) -> str:
    """Build a clean output filename from track tags.

    Format: "## - Artist - Title" if track number exists,
            "Artist - Title" if no track number.
    """
    parts = []
    if track.get("track") is not None:
        parts.append(f"{track['track']:02d}")
    if track.get("artist"):
        parts.append(track["artist"])
    parts.append(track.get("title") or "Untitled")
    return " - ".join(parts)


def parse_folder_name(folder_name: str) -> dict:
    """Parse a folder name into artist and album.

    Tries patterns:
    1. Artist - Album (Year)
    2. Artist - Album
    3. Album (fallback)
    """
    # Pattern 1: Artist - Album (Year)
    match = re.match(r"^(.+?)\s*[-_]\s*(.+?)\s*\((\d{4})\)\s*$", folder_name)
    if match:
        artist, album, year = match.groups()
        return {
            "artist": artist.strip(),
            "album": album.strip(),
            "year": year,
        }

    # Pattern 2: Artist - Album
    match = re.match(r"^(.+?)\s*[-_]\s*(.+)$", folder_name)
    if match:
        artist, album = match.groups()
        return {
            "artist": artist.strip(),
            "album": album.strip(),
            "year": None,
        }

    # Pattern 3: fallback — folder name is the album
    return {"artist": None, "album": folder_name.strip(), "year": None}
