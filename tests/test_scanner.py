import pytest
from pathlib import Path
from wav2mp3.scanner import find_wav_files, find_cover_art


class TestFindWavFiles:
    """Test WAV file discovery in a folder."""

    def test_finds_wav_files(self, tmp_path):
        (tmp_path / "track1.wav").touch()
        (tmp_path / "track2.wav").touch()
        result = find_wav_files(tmp_path)
        assert len(result) == 2
        assert all(f.suffix == ".wav" for f in result)

    def test_finds_uppercase_wav(self, tmp_path):
        (tmp_path / "track1.WAV").touch()
        result = find_wav_files(tmp_path)
        assert len(result) == 1

    def test_ignores_non_wav(self, tmp_path):
        (tmp_path / "track1.wav").touch()
        (tmp_path / "track2.mp3").touch()
        (tmp_path / "track3.flac").touch()
        result = find_wav_files(tmp_path)
        assert len(result) == 1

    def test_returns_empty_when_no_wavs(self, tmp_path):
        (tmp_path / "readme.txt").touch()
        result = find_wav_files(tmp_path)
        assert result == []

    def test_sorted_by_name(self, tmp_path):
        (tmp_path / "02 - B.wav").touch()
        (tmp_path / "01 - A.wav").touch()
        result = find_wav_files(tmp_path)
        assert result[0].name == "01 - A.wav"
        assert result[1].name == "02 - B.wav"


class TestFindCoverArt:
    """Test cover art detection with priority order."""

    def test_prefers_cover_jpg(self, tmp_path):
        (tmp_path / "cover.jpg").touch()
        (tmp_path / "artwork.jpg").touch()
        result = find_cover_art(tmp_path)
        assert result.name == "cover.jpg"

    def test_prefers_cover_png_over_folder(self, tmp_path):
        (tmp_path / "cover.png").touch()
        (tmp_path / "folder.jpg").touch()
        result = find_cover_art(tmp_path)
        assert result.name == "cover.png"

    def test_falls_back_to_folder_jpg(self, tmp_path):
        (tmp_path / "folder.jpg").touch()
        result = find_cover_art(tmp_path)
        assert result.name == "folder.jpg"

    def test_falls_back_to_artwork(self, tmp_path):
        (tmp_path / "artwork.png").touch()
        result = find_cover_art(tmp_path)
        assert result.name == "artwork.png"

    def test_falls_back_to_first_image(self, tmp_path):
        (tmp_path / "random_photo.jpg").touch()
        result = find_cover_art(tmp_path)
        assert result.name == "random_photo.jpg"

    def test_returns_none_when_no_images(self, tmp_path):
        (tmp_path / "track.wav").touch()
        result = find_cover_art(tmp_path)
        assert result is None
