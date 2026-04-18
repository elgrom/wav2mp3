from pathlib import Path
from typing import Optional
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TRCK, TDRC, TCON, APIC
from mutagen.mp3 import MP3


def apply_tags(mp3_path: Path, tags: dict, cover_art_path: Optional[Path] = None) -> None:
    """Apply ID3v2.4 tags and optional cover art to an MP3 file.

    Args:
        mp3_path: Path to the MP3 file.
        tags: Dict with keys: title, artist, album_artist, album, track, year, genre.
        cover_art_path: Optional path to cover art image (JPEG or PNG).
    """
    audio = MP3(mp3_path, ID3=ID3)

    # Ensure ID3 tag exists
    try:
        audio.add_tags()
    except Exception:
        pass

    tag = audio.tags

    if tags.get("title"):
        tag.add(TIT2(encoding=3, text=tags["title"]))
    if tags.get("artist"):
        tag.add(TPE1(encoding=3, text=tags["artist"]))
    if tags.get("album_artist"):
        tag.add(TPE2(encoding=3, text=tags["album_artist"]))
    if tags.get("album"):
        tag.add(TALB(encoding=3, text=tags["album"]))
    if tags.get("track") is not None:
        tag.add(TRCK(encoding=3, text=str(tags["track"])))
    if tags.get("year"):
        tag.add(TDRC(encoding=3, text=str(tags["year"])))
    if tags.get("genre"):
        tag.add(TCON(encoding=3, text=tags["genre"]))

    if cover_art_path and cover_art_path.exists():
        mime = "image/jpeg" if cover_art_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        with open(cover_art_path, "rb") as img:
            tag.add(APIC(
                encoding=3,
                mime=mime,
                type=3,  # Front cover
                desc="Cover",
                data=img.read(),
            ))

    audio.save(v2_version=4)
