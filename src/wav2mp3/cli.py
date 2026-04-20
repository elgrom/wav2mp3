import argparse
import shutil
import sys
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

from wav2mp3.scanner import find_wav_files, find_cover_art
from wav2mp3.parser import parse_filename, parse_folder_name, build_output_filename
from wav2mp3.prompts import prompt_shared_tags, prompt_track_review
from wav2mp3.converter import check_ffmpeg, convert_wav_to_mp3
from wav2mp3.tagger import apply_tags


def _resolve_cover_art(cover_arg: str) -> Path:
    """Resolve a --cover argument to a local file path.

    Accepts a local file path or a URL (http/https). URLs are downloaded
    to a temporary file. Returns the path to the image.
    """
    if cover_arg.startswith(("http://", "https://")):
        # Guess extension from URL
        lower = cover_arg.lower().split("?")[0]
        if lower.endswith(".png"):
            suffix = ".png"
        else:
            suffix = ".jpg"
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        try:
            print(f"Downloading cover art from {cover_arg}...")
            urllib.request.urlretrieve(cover_arg, tmp.name)
        except (urllib.error.URLError, OSError) as e:
            print(f"Warning: could not download cover art: {e}")
            return None
        return Path(tmp.name)

    path = Path(cover_arg).resolve()
    if not path.is_file():
        print(f"Warning: cover art file not found: {path}")
        return None
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Convert WAV files to 320 kbps MP3 with ID3 tags and cover art."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Path to folder containing WAV files, or a single .wav file (default: current directory)",
    )
    parser.add_argument(
        "--cover",
        type=str,
        default=None,
        help="Cover art image: local file path or URL (http/https)",
    )
    args = parser.parse_args()

    target = args.path.resolve()

    # Determine single-file vs folder mode
    single_file = target.is_file() and target.suffix.lower() == ".wav"

    if single_file:
        folder = target.parent
        wav_files = [target]
    elif target.is_dir():
        folder = target
        wav_files = find_wav_files(folder)
        if not wav_files:
            print(f"No WAV files found in {folder}")
            sys.exit(0)
    else:
        print(f"Error: {target} is not a directory or WAV file.")
        sys.exit(1)

    if not check_ffmpeg():
        print("Error: ffmpeg is not installed.")
        print("Install it with: brew install ffmpeg")
        sys.exit(1)

    # Resolve cover art: --cover flag takes priority, then auto-detect
    if args.cover:
        cover_art = _resolve_cover_art(args.cover)
    else:
        cover_art = find_cover_art(folder)

    print(f"\nFound {len(wav_files)} WAV file(s) in {folder}")

    # Parse folder name for defaults (skip in single-file mode)
    folder_info = None if single_file else parse_folder_name(folder.name)

    # Shared tags
    shared = prompt_shared_tags(cover_art, folder_info)

    # Step 3: Parse per-track tags
    tracks = []
    for wav in wav_files:
        parsed = parse_filename(wav.name)
        parsed["filename"] = wav.name
        tracks.append(parsed)

    # Step 4: Review per-track tags
    tracks = prompt_track_review(tracks)

    # Step 5 & 6: Convert and tag
    print("\n── Converting ───────────────────────")
    converted = 0
    failed = 0

    for i, (wav, track) in enumerate(zip(wav_files, tracks), 1):
        print(f"  [{i}/{len(wav_files)}] {wav.name}...", end=" ", flush=True)

        mp3_path = convert_wav_to_mp3(wav)
        if mp3_path is None:
            failed += 1
            print("FAILED")
            continue

        tags = {
            "title": track["title"],
            "artist": track["artist"],
            "album_artist": shared["album_artist"],
            "album": shared["album"],
            "track": track["track"],
            "year": shared["year"],
            "genre": shared["genre"],
        }
        apply_tags(mp3_path, tags, cover_art)

        # Rename to clean format
        clean_name = build_output_filename(track) + ".mp3"
        clean_path = mp3_path.parent / clean_name
        if clean_path != mp3_path:
            mp3_path.rename(clean_path)

        converted += 1
        print("OK")

    # Step 7: Move original WAVs (skip in single-file mode)
    if converted > 0 and not single_file:
        wav_dir = folder / "wav"
        wav_dir.mkdir(exist_ok=True)
        for wav in wav_files:
            if wav.exists():
                shutil.move(str(wav), str(wav_dir / wav.name))

    # Clean up any downloaded cover art temp file
    if args.cover and cover_art and "/tmp" in str(cover_art):
        try:
            cover_art.unlink()
        except OSError:
            pass

    # Step 8: Summary
    print(f"\n── Done ─────────────────────────────")
    print(f"  Converted: {converted}")
    if failed:
        print(f"  Failed:    {failed}")
    if converted > 0 and not single_file:
        print(f"  WAVs moved to: {folder / 'wav'}")
    print()


if __name__ == "__main__":
    main()
