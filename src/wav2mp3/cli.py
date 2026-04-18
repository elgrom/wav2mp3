import argparse
import shutil
import sys
from pathlib import Path

from wav2mp3.scanner import find_wav_files, find_cover_art
from wav2mp3.parser import parse_filename
from wav2mp3.prompts import prompt_shared_tags, prompt_track_review
from wav2mp3.converter import check_ffmpeg, convert_wav_to_mp3
from wav2mp3.tagger import apply_tags


def main():
    parser = argparse.ArgumentParser(
        description="Convert WAV files to 320 kbps MP3 with ID3 tags and cover art."
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Path to folder containing WAV files",
    )
    args = parser.parse_args()

    folder = args.folder.resolve()

    if not folder.is_dir():
        print(f"Error: {folder} is not a directory.")
        sys.exit(1)

    if not check_ffmpeg():
        print("Error: ffmpeg is not installed.")
        print("Install it with: brew install ffmpeg")
        sys.exit(1)

    # Step 1: Scan
    wav_files = find_wav_files(folder)
    if not wav_files:
        print(f"No WAV files found in {folder}")
        sys.exit(0)

    cover_art = find_cover_art(folder)

    print(f"\nFound {len(wav_files)} WAV file(s) in {folder}")

    # Step 2: Shared tags
    shared = prompt_shared_tags(cover_art)

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

        converted += 1
        print("OK")

    # Step 7: Move WAVs
    if converted > 0:
        wav_dir = folder / "wav"
        wav_dir.mkdir(exist_ok=True)
        for wav in wav_files:
            if wav.exists():
                shutil.move(str(wav), str(wav_dir / wav.name))

    # Step 8: Summary
    print(f"\n── Done ─────────────────────────────")
    print(f"  Converted: {converted}")
    if failed:
        print(f"  Failed:    {failed}")
    if converted > 0:
        print(f"  WAVs moved to: {folder / 'wav'}")
    print()


if __name__ == "__main__":
    main()
