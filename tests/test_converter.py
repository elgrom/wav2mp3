import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from wav2mp3.converter import convert_wav_to_mp3, check_ffmpeg


class TestCheckFfmpeg:
    """Test ffmpeg availability check."""

    @patch("shutil.which", return_value="/usr/local/bin/ffmpeg")
    def test_returns_true_when_installed(self, mock_which):
        assert check_ffmpeg() is True

    @patch("shutil.which", return_value=None)
    def test_returns_false_when_missing(self, mock_which):
        assert check_ffmpeg() is False


class TestConvertWavToMp3:
    """Test WAV to MP3 conversion via ffmpeg."""

    @patch("subprocess.run")
    def test_calls_ffmpeg_with_correct_args(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0)
        wav_path = tmp_path / "01 - Artist - Title.wav"
        wav_path.touch()

        result = convert_wav_to_mp3(wav_path)

        expected_mp3 = tmp_path / "01 - Artist - Title.mp3"
        mock_run.assert_called_once_with(
            [
                "ffmpeg", "-i", str(wav_path),
                "-codec:a", "libmp3lame",
                "-b:a", "320k",
                "-y",
                str(expected_mp3),
            ],
            capture_output=True,
            text=True,
        )
        assert result == expected_mp3

    @patch("subprocess.run")
    def test_returns_none_on_failure(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=1, stderr="error")
        wav_path = tmp_path / "bad.wav"
        wav_path.touch()

        result = convert_wav_to_mp3(wav_path)
        assert result is None

    @patch("subprocess.run")
    def test_output_path_matches_input_directory(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0)
        wav_path = tmp_path / "song.wav"
        wav_path.touch()

        result = convert_wav_to_mp3(wav_path)
        assert result.parent == wav_path.parent
        assert result.suffix == ".mp3"
        assert result.stem == "song"
