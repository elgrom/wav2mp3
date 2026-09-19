from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


def prompt_shared_tags(cover_art: Optional[Path], folder_info: Optional[Dict] = None) -> dict:
    """Prompt for shared album-level tags.

    Args:
        cover_art: Path to cover art image, or None.
        folder_info: Dict from parse_folder_name with keys: artist, album, year.

    Returns dict with keys: album, album_artist, genre, year.
    """
    if cover_art:
        print(f"\nCover art found: {cover_art.name}")
    else:
        print("\nNo cover art found — skipping artwork embedding.")

    folder_info = folder_info or {}
    default_album = folder_info.get("album") or "My Album"
    default_artist = folder_info.get("artist") or "Various Artists"
    default_year = folder_info.get("year") or str(datetime.now().year)

    print("\n── Shared Tags ──────────────────────")
    print("Press Enter to accept [default], or type a new value.\n")

    album = input(f"  Album [{default_album}]: ").strip() or default_album
    album_artist = input(f"  Album Artist [{default_artist}]: ").strip() or default_artist
    label = input(f"  Label []: ").strip()
    genre = input(f"  Genre [Electronic]: ").strip() or "Electronic"
    year = input(f"  Year [{default_year}]: ").strip() or default_year

    return {
        "album": album,
        "album_artist": album_artist,
        "label": label,
        "genre": genre,
        "year": year,
    }


def prompt_track_review(tracks: List[Dict]) -> List[Dict]:
    """Display parsed tracks and allow editing.

    Each track dict has keys: filename, track, artist, title.
    Returns the (possibly modified) list.
    """
    print("\n── Tracks ───────────────────────────")

    # Find column widths
    num_width = max(len(str(t.get("track") or "?")) for t in tracks)
    artist_width = max(len(t.get("artist") or "???") for t in tracks)

    # Print header
    print(f"  {'#':>{num_width}}  {'Artist':<{artist_width}}  Title")

    # Print each track
    for t in tracks:
        num = str(t["track"]) if t["track"] is not None else "?"
        artist = t["artist"] or "???"
        title = t["title"] or "untitled"
        print(f"  {num:>{num_width}}  {artist:<{artist_width}}  {title}")

    print()

    # Edit loop
    while True:
        choice = input("Edit track number (or Enter to accept all): ").strip()
        if not choice:
            break

        try:
            track_num = int(choice)
        except ValueError:
            print("  Enter a track number or press Enter to accept.")
            continue

        # Find the track to edit
        target = None
        for t in tracks:
            if t["track"] == track_num:
                target = t
                break

        if target is None:
            # Try by list index
            idx = track_num - 1
            if 0 <= idx < len(tracks):
                target = tracks[idx]

        if target is None:
            print(f"  Track {track_num} not found.")
            continue

        current_artist = target["artist"] or "???"
        current_title = target["title"] or "untitled"

        new_track = input(f"  Track # [{target['track'] or '?'}]: ").strip()
        if new_track:
            try:
                target["track"] = int(new_track)
            except ValueError:
                pass

        new_artist = input(f"  Artist [{current_artist}]: ").strip()
        if new_artist:
            target["artist"] = new_artist

        new_title = input(f"  Title [{current_title}]: ").strip()
        if new_title:
            target["title"] = new_title

        print()

    # Final confirmation
    proceed = input("Proceed? [Y/n]: ").strip().lower()
    if proceed and proceed != "y":
        print("Aborted.")
        raise SystemExit(0)

    return tracks
