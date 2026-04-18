import pytest
from wav2mp3.parser import parse_filename, parse_folder_name, build_output_filename


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

    def test_dot_separator_with_artist(self):
        result = parse_filename("01. Artist - Title.wav")
        assert result == {"track": 1, "artist": "Artist", "title": "Title"}

    def test_dot_separator_no_space(self):
        result = parse_filename("03.Artist - Great Song.wav")
        assert result == {"track": 3, "artist": "Artist", "title": "Great Song"}

    def test_dot_separator_title_only(self):
        result = parse_filename("01. My Song.wav")
        assert result == {"track": 1, "artist": None, "title": "My Song"}

    def test_space_only_after_track(self):
        result = parse_filename("01 Artist - Title.wav")
        assert result == {"track": 1, "artist": "Artist", "title": "Title"}

    def test_dot_separator_double_digit(self):
        result = parse_filename("12. DJ Name - Deep Cut.wav")
        assert result == {"track": 12, "artist": "DJ Name", "title": "Deep Cut"}


class TestParseFolderName:
    """Test folder name parsing into artist and album."""

    def test_artist_dash_album(self):
        result = parse_folder_name("Some Artist - Great Album")
        assert result == {"artist": "Some Artist", "album": "Great Album", "year": None}

    def test_artist_dash_album_with_year(self):
        result = parse_folder_name("Some Artist - Great Album (2024)")
        assert result == {"artist": "Some Artist", "album": "Great Album", "year": "2024"}

    def test_album_only_fallback(self):
        result = parse_folder_name("Just An Album")
        assert result == {"artist": None, "album": "Just An Album", "year": None}

    def test_underscore_separator(self):
        result = parse_folder_name("Artist_Album Name")
        assert result == {"artist": "Artist", "album": "Album Name", "year": None}

    def test_whitespace_stripped(self):
        result = parse_folder_name("  Artist  -  Album  ")
        assert result == {"artist": "Artist", "album": "Album", "year": None}


class TestBuildOutputFilename:
    """Test output filename construction from track tags."""

    def test_with_track_artist_title(self):
        result = build_output_filename({"track": 1, "artist": "Artist", "title": "Title"})
        assert result == "01 - Artist - Title"

    def test_with_track_no_artist(self):
        result = build_output_filename({"track": 3, "artist": None, "title": "My Song"})
        assert result == "03 - My Song"

    def test_no_track_with_artist(self):
        result = build_output_filename({"track": None, "artist": "Artist", "title": "Title"})
        assert result == "Artist - Title"

    def test_no_track_no_artist(self):
        result = build_output_filename({"track": None, "artist": None, "title": "Just A Song"})
        assert result == "Just A Song"

    def test_double_digit_track(self):
        result = build_output_filename({"track": 12, "artist": "DJ", "title": "Beat"})
        assert result == "12 - DJ - Beat"

    def test_missing_title_uses_untitled(self):
        result = build_output_filename({"track": 1, "artist": "Artist", "title": None})
        assert result == "01 - Artist - Untitled"
