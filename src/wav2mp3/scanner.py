from pathlib import Path
from typing import Optional


COVER_ART_PRIORITY = [
    "cover.jpg",
    "cover.png",
    "folder.jpg",
    "artwork.jpg",
    "artwork.png",
]


def find_wav_files(folder: Path) -> list[Path]:
    """Find all WAV files in a folder, sorted by name."""
    wavs = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() == ".wav"
    ]
    return sorted(wavs, key=lambda f: f.name.lower())


def find_cover_art(folder: Path) -> Optional[Path]:
    """Find cover art image in a folder using priority order.

    Returns the first match from the priority list, or falls back
    to the first .jpg/.png found. Returns None if no images exist.
    """
    for name in COVER_ART_PRIORITY:
        candidate = folder / name
        if candidate.exists():
            return candidate

    for f in sorted(folder.iterdir(), key=lambda f: f.name.lower()):
        if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png"):
            return f

    return None
