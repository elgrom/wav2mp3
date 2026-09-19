import subprocess
import pytest
from pathlib import Path
from mutagen.id3 import ID3
from wav2mp3.tagger import apply_tags


def _make_mp3(path: Path) -> Path:
    """Generate a minimal silent MP3 via ffmpeg for testing."""
    mp3 = path / "test.mp3"
    subprocess.run(
        [
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "0.1", "-codec:a", "libmp3lame", "-b:a", "128k",
            "-y", str(mp3),
        ],
        capture_output=True,
        check=True,
    )
    return mp3


@pytest.fixture
def mp3_file(tmp_path):
    return _make_mp3(tmp_path)


class TestApplyTags:
    """Test ID3 tag writing via apply_tags."""

    def test_label_written_as_tpub(self, mp3_file):
        apply_tags(mp3_file, {"label": "Metalheadz"})
        tag = ID3(mp3_file)
        assert "TPUB" in tag
        assert str(tag["TPUB"]) == "Metalheadz"

    def test_label_omitted_when_empty(self, mp3_file):
        apply_tags(mp3_file, {"label": ""})
        tag = ID3(mp3_file)
        assert "TPUB" not in tag

    def test_label_omitted_when_absent(self, mp3_file):
        apply_tags(mp3_file, {})
        tag = ID3(mp3_file)
        assert "TPUB" not in tag

    def test_title_written(self, mp3_file):
        apply_tags(mp3_file, {"title": "Deep Cut"})
        tag = ID3(mp3_file)
        assert str(tag["TIT2"]) == "Deep Cut"

    def test_artist_written(self, mp3_file):
        apply_tags(mp3_file, {"artist": "Goldie"})
        tag = ID3(mp3_file)
        assert str(tag["TPE1"]) == "Goldie"

    def test_album_artist_written(self, mp3_file):
        apply_tags(mp3_file, {"album_artist": "Various Artists"})
        tag = ID3(mp3_file)
        assert str(tag["TPE2"]) == "Various Artists"

    def test_album_written(self, mp3_file):
        apply_tags(mp3_file, {"album": "Timeless"})
        tag = ID3(mp3_file)
        assert str(tag["TALB"]) == "Timeless"

    def test_track_written(self, mp3_file):
        apply_tags(mp3_file, {"track": 3})
        tag = ID3(mp3_file)
        assert str(tag["TRCK"]) == "3"

    def test_year_written(self, mp3_file):
        apply_tags(mp3_file, {"year": "1995"})
        tag = ID3(mp3_file)
        assert str(tag["TDRC"]) == "1995"

    def test_genre_written(self, mp3_file):
        apply_tags(mp3_file, {"genre": "Drum and Bass"})
        tag = ID3(mp3_file)
        assert str(tag["TCON"]) == "Drum and Bass"

    def test_all_tags_together(self, mp3_file):
        tags = {
            "title": "Inner City Life",
            "artist": "Goldie",
            "album_artist": "Goldie",
            "album": "Timeless",
            "track": 2,
            "year": "1995",
            "genre": "Drum and Bass",
            "label": "FFRR",
        }
        apply_tags(mp3_file, tags)
        tag = ID3(mp3_file)
        assert str(tag["TIT2"]) == "Inner City Life"
        assert str(tag["TPE1"]) == "Goldie"
        assert str(tag["TPUB"]) == "FFRR"
