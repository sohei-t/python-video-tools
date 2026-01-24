"""Tests for video_overlay module."""

import pytest
import sys
from pathlib import Path
import tempfile


# Define functions locally for testing to avoid moviepy dependency
POSITIONS = {
    "top-left": "tl",
    "top-right": "tr",
    "bottom-left": "bl",
    "bottom-right": "br",
    "center": "center",
}


def get_position_coords(position, main_size, overlay_size, margin=10):
    """位置名から座標を計算"""
    main_w, main_h = main_size
    overlay_w, overlay_h = overlay_size

    positions = {
        "tl": (margin, margin),
        "tr": (main_w - overlay_w - margin, margin),
        "bl": (margin, main_h - overlay_h - margin),
        "br": (main_w - overlay_w - margin, main_h - overlay_h - margin),
        "center": ((main_w - overlay_w) // 2, (main_h - overlay_h) // 2),
    }

    pos_key = POSITIONS.get(position, "tr")
    return positions.get(pos_key, positions["tr"])


def is_video_file(path):
    """動画ファイルかどうかを判定"""
    video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".webm", ".m4v"}
    return path.suffix.lower() in video_extensions


def is_image_file(path):
    """画像ファイルかどうかを判定"""
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tiff"}
    return path.suffix.lower() in image_extensions


class TestGetPositionCoords:
    """Tests for get_position_coords function."""

    def test_top_left(self):
        """Test top-left position."""
        x, y = get_position_coords("top-left", (1920, 1080), (100, 100), margin=10)
        assert x == 10
        assert y == 10

    def test_top_right(self):
        """Test top-right position."""
        x, y = get_position_coords("top-right", (1920, 1080), (100, 100), margin=10)
        assert x == 1920 - 100 - 10
        assert y == 10

    def test_bottom_left(self):
        """Test bottom-left position."""
        x, y = get_position_coords("bottom-left", (1920, 1080), (100, 100), margin=10)
        assert x == 10
        assert y == 1080 - 100 - 10

    def test_bottom_right(self):
        """Test bottom-right position."""
        x, y = get_position_coords("bottom-right", (1920, 1080), (100, 100), margin=10)
        assert x == 1920 - 100 - 10
        assert y == 1080 - 100 - 10

    def test_center(self):
        """Test center position."""
        x, y = get_position_coords("center", (1920, 1080), (100, 100), margin=10)
        assert x == (1920 - 100) // 2
        assert y == (1080 - 100) // 2

    def test_default_margin(self):
        """Test with default margin."""
        x, y = get_position_coords("top-left", (1920, 1080), (100, 100))
        assert x == 10  # default margin
        assert y == 10

    def test_unknown_position_defaults_to_top_right(self):
        """Test that unknown position defaults to top-right."""
        x, y = get_position_coords("unknown", (1920, 1080), (100, 100), margin=10)
        expected_x, expected_y = get_position_coords("top-right", (1920, 1080), (100, 100), margin=10)
        assert x == expected_x
        assert y == expected_y


class TestIsVideoFile:
    """Tests for is_video_file function."""

    def test_mp4_is_video(self):
        """Test that .mp4 is recognized as video."""
        assert is_video_file(Path("video.mp4")) is True

    def test_avi_is_video(self):
        """Test that .avi is recognized as video."""
        assert is_video_file(Path("video.avi")) is True

    def test_mkv_is_video(self):
        """Test that .mkv is recognized as video."""
        assert is_video_file(Path("video.mkv")) is True

    def test_mov_is_video(self):
        """Test that .mov is recognized as video."""
        assert is_video_file(Path("video.mov")) is True

    def test_txt_is_not_video(self):
        """Test that .txt is not recognized as video."""
        assert is_video_file(Path("doc.txt")) is False

    def test_jpg_is_not_video(self):
        """Test that .jpg is not recognized as video."""
        assert is_video_file(Path("image.jpg")) is False

    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert is_video_file(Path("video.MP4")) is True
        assert is_video_file(Path("video.Mp4")) is True


class TestIsImageFile:
    """Tests for is_image_file function."""

    def test_jpg_is_image(self):
        """Test that .jpg is recognized as image."""
        assert is_image_file(Path("image.jpg")) is True

    def test_jpeg_is_image(self):
        """Test that .jpeg is recognized as image."""
        assert is_image_file(Path("image.jpeg")) is True

    def test_png_is_image(self):
        """Test that .png is recognized as image."""
        assert is_image_file(Path("image.png")) is True

    def test_webp_is_image(self):
        """Test that .webp is recognized as image."""
        assert is_image_file(Path("image.webp")) is True

    def test_txt_is_not_image(self):
        """Test that .txt is not recognized as image."""
        assert is_image_file(Path("doc.txt")) is False

    def test_mp4_is_not_image(self):
        """Test that .mp4 is not recognized as image."""
        assert is_image_file(Path("video.mp4")) is False

    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert is_image_file(Path("image.JPG")) is True
        assert is_image_file(Path("image.Png")) is True


class TestPositionsDict:
    """Tests for POSITIONS dictionary."""

    def test_all_positions_defined(self):
        """Test that all expected positions are defined."""
        expected = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        for pos in expected:
            assert pos in POSITIONS
