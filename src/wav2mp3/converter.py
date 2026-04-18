import shutil
import subprocess
from pathlib import Path
from typing import Optional


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available on the system."""
    return shutil.which("ffmpeg") is not None


def convert_wav_to_mp3(wav_path: Path) -> Optional[Path]:
    """Convert a WAV file to 320 kbps CBR MP3 using ffmpeg.

    Returns the path to the MP3 file on success, or None on failure.
    """
    mp3_path = wav_path.with_suffix(".mp3")
    result = subprocess.run(
        [
            "ffmpeg", "-i", str(wav_path),
            "-codec:a", "libmp3lame",
            "-b:a", "320k",
            "-y",
            str(mp3_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  Error converting {wav_path.name}: {result.stderr}")
        return None
    return mp3_path
