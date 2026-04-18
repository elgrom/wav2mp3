import pytest
from wav2mp3.parser import parse_filename


class TestParseFilename:
    """Test filename parsing into (track_number, artist, title)."""

    def test_full_format_with_leading_zero(self):
        result = parse_filename("01 - Some Artist - Track One.wav")
        assert result == {"track": 1, "artist": "Some Artist", "title": "Track One"}

    def test_full_format_without_leading_zero(self):
        result = parse_filename("3 - Another Artist - My Song.wav")
        assert result == {"track": 3, "artist": "Another Artist", "title": "My Song"}

    def test_full_format_double_digit(self):
        result = parse_filename("12 - DJ Name - Deep Cut.wav")
        assert result == {"track": 12, "artist": "DJ Name", "title": "Deep Cut"}

    def test_artist_title_no_track(self):
        result = parse_filename("Some Artist - Track One.wav")
        assert result == {"track": None, "artist": "Some Artist", "title": "Track One"}

    def test_title_only_fallback(self):
        result = parse_filename("my song.wav")
        assert result == {"track": None, "artist": None, "title": "my song"}

    def test_dash_separator_no_spaces(self):
        result = parse_filename("02-Artist-Title.wav")
        assert result == {"track": 2, "artist": "Artist", "title": "Title"}

    def test_underscore_separator(self):
        result = parse_filename("05_Cool Artist_Great Track.wav")
        assert result == {"track": 5, "artist": "Cool Artist", "title": "Great Track"}

    def test_extra_whitespace_stripped(self):
        result = parse_filename("01 -  Some Artist  -  Track One .wav")
        assert result == {"track": 1, "artist": "Some Artist", "title": "Track One"}

    def test_title_with_hyphens_in_name(self):
        result = parse_filename("01 - Artist - My Song - Extended Mix.wav")
        assert result == {"track": 1, "artist": "Artist", "title": "My Song - Extended Mix"}

    def test_case_insensitive_extension(self):
        result = parse_filename("01 - Artist - Title.WAV")
        assert result == {"track": 1, "artist": "Artist", "title": "Title"}
