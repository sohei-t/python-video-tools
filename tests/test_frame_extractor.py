"""Tests for frame_extractor module."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "frame-extractor"))

from frame_extractor import format_time, parse_range, parse_ranges, parse_time


class TestParseTime:
    """Tests for parse_time function."""

    def test_seconds_only(self):
        """Test parsing seconds as float."""
        assert parse_time("90") == 90.0
        assert parse_time("90.5") == 90.5
        assert parse_time("0") == 0.0

    def test_mm_ss_format(self):
        """Test parsing MM:SS format."""
        assert parse_time("01:30") == 90.0
        assert parse_time("00:30") == 30.0
        assert parse_time("10:00") == 600.0

    def test_hh_mm_ss_format(self):
        """Test parsing HH:MM:SS format."""
        assert parse_time("00:01:30") == 90.0
        assert parse_time("01:00:00") == 3600.0
        assert parse_time("00:00:30") == 30.0

    def test_with_whitespace(self):
        """Test parsing with leading/trailing whitespace."""
        assert parse_time("  90  ") == 90.0
        assert parse_time(" 01:30 ") == 90.0

    def test_invalid_format(self):
        """Test that invalid formats raise ValueError."""
        with pytest.raises(ValueError):
            parse_time("invalid")
        with pytest.raises(ValueError):
            parse_time("1:2:3:4")


class TestParseRange:
    """Tests for parse_range function."""

    def test_simple_range(self):
        """Test parsing simple time ranges."""
        start, end = parse_range("0-90")
        assert start == 0.0
        assert end == 90.0

    def test_mm_ss_range(self):
        """Test parsing MM:SS range format."""
        start, end = parse_range("00:00-01:30")
        assert start == 0.0
        assert end == 90.0

    def test_double_dash_separator(self):
        """Test parsing with double dash separator."""
        start, end = parse_range("00:00:00--00:01:30")
        assert start == 0.0
        assert end == 90.0


class TestParseRanges:
    """Tests for parse_ranges function."""

    def test_single_range(self):
        """Test parsing single range."""
        ranges = parse_ranges("0-90")
        assert len(ranges) == 1
        assert ranges[0] == (0.0, 90.0)

    def test_multiple_ranges(self):
        """Test parsing comma-separated ranges."""
        ranges = parse_ranges("0-30, 60-90")
        assert len(ranges) == 2
        assert ranges[0] == (0.0, 30.0)
        assert ranges[1] == (60.0, 90.0)

    def test_empty_string(self):
        """Test parsing empty string returns empty list."""
        ranges = parse_ranges("")
        assert ranges == []


class TestFormatTime:
    """Tests for format_time function."""

    def test_format_seconds(self):
        """Test formatting seconds to time string."""
        assert format_time(0) == "00:00:00.00"
        assert format_time(90) == "00:01:30.00"
        assert format_time(3661.5) == "01:01:01.50"

    def test_format_large_value(self):
        """Test formatting large time values."""
        assert format_time(7200) == "02:00:00.00"
