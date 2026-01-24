"""Tests for video_speed_changer module."""

import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "video-speed-changer"))

from video_speed_changer import build_atempo_filter, get_video_files


class TestBuildAtempoFilter:
    """Tests for build_atempo_filter function."""

    def test_normal_speed(self):
        """Test normal speed (1.0x)."""
        result = build_atempo_filter(1.0)
        assert result == "atempo=1.0"

    def test_double_speed(self):
        """Test 2x speed."""
        result = build_atempo_filter(2.0)
        assert result == "atempo=2.0"

    def test_half_speed(self):
        """Test 0.5x speed (slowmo)."""
        result = build_atempo_filter(0.5)
        assert result == "atempo=0.5"

    def test_very_fast_speed(self):
        """Test very fast speed requiring multiple atempo filters."""
        result = build_atempo_filter(4.0)
        # Should chain atempo filters since max is 2.0
        assert "atempo=2.0" in result
        assert result.count("atempo") == 2

    def test_very_slow_speed(self):
        """Test very slow speed requiring multiple atempo filters."""
        result = build_atempo_filter(0.25)
        # Should chain atempo filters since min is 0.5
        assert "atempo=0.5" in result
        assert result.count("atempo") == 2


class TestGetVideoFiles:
    """Tests for get_video_files function."""

    def test_get_from_directory(self):
        """Test getting video files from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for name in ["video1.mp4", "video2.avi", "doc.txt"]:
                Path(tmpdir, name).touch()

            videos = get_video_files(Path(tmpdir))
            assert len(videos) == 2
            assert all(f.suffix.lower() in [".mp4", ".avi"] for f in videos)

    def test_get_single_file(self):
        """Test getting a single video file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir, "video.mp4")
            video_path.touch()

            videos = get_video_files(video_path)
            assert len(videos) == 1
            assert videos[0] == video_path

    def test_non_video_file(self):
        """Test that non-video files are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir, "doc.txt")
            txt_path.touch()

            videos = get_video_files(txt_path)
            assert len(videos) == 0

    def test_various_extensions(self):
        """Test various video extensions are recognized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions = [".mp4", ".avi", ".mkv", ".mov", ".webm"]
            for ext in extensions:
                Path(tmpdir, f"video{ext}").touch()

            videos = get_video_files(Path(tmpdir))
            assert len(videos) == len(extensions)

    def test_sorted_output(self):
        """Test that output is sorted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["c.mp4", "a.mp4", "b.mp4"]:
                Path(tmpdir, name).touch()

            videos = get_video_files(Path(tmpdir))
            assert videos[0].name == "a.mp4"
            assert videos[1].name == "b.mp4"
            assert videos[2].name == "c.mp4"
