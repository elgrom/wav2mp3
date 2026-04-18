import re
from pathlib import Path


def parse_filename(filename: str) -> dict:
    """Parse a WAV filename into track number, artist, and title.

    Tries patterns in order:
    1. ## - Artist - Title.wav
    2. Artist - Title.wav
    3. Title.wav (fallback)
    """
    stem = Path(filename).stem

    # Pattern 1: track_number <sep> artist <sep> title
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

    # Pattern 2: artist <sep> title (no track number)
    # Only match if there's exactly one separator and the left side
    # doesn't look like a track number
    match = re.match(r"^(.+?)\s*[-_]\s*(.+)$", stem)
    if match:
        left, right = match.groups()
        if not re.match(r"^\d{1,3}$", left.strip()):
            return {
                "track": None,
                "artist": left.strip(),
                "title": right.strip(),
            }

    # Pattern 3: fallback — entire stem is the title
    return {"track": None, "artist": None, "title": stem.strip()}
