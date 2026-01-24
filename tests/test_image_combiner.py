"""Tests for image_combiner module."""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "image-combiner"))

from image_combiner import (
    parse_color,
    get_image_files,
    combine_images_horizontal,
    combine_images_vertical,
)


class TestParseColor:
    """Tests for parse_color function."""

    def test_parse_rgb(self):
        """Test parsing RGB color string."""
        assert parse_color("255,255,255") == (255, 255, 255)
        assert parse_color("0,0,0") == (0, 0, 0)
        assert parse_color("128, 64, 32") == (128, 64, 32)

    def test_parse_with_whitespace(self):
        """Test parsing with whitespace."""
        assert parse_color(" 255 , 255 , 255 ") == (255, 255, 255)


class TestGetImageFiles:
    """Tests for get_image_files function."""

    def test_get_from_directory(self):
        """Test getting image files from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test image files
            for name in ["test1.jpg", "test2.png", "test3.txt"]:
                Path(tmpdir, name).touch()

            images = get_image_files(Path(tmpdir))
            assert len(images) == 2
            assert all(f.suffix.lower() in [".jpg", ".png"] for f in images)

    def test_get_single_file(self):
        """Test getting a single image file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = Path(tmpdir, "test.jpg")
            img_path.touch()

            images = get_image_files(img_path)
            assert len(images) == 1
            assert images[0] == img_path

    def test_non_image_file(self):
        """Test that non-image files are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir, "test.txt")
            txt_path.touch()

            images = get_image_files(txt_path)
            assert len(images) == 0


class TestCombineImagesHorizontal:
    """Tests for combine_images_horizontal function."""

    def test_combine_two_images(self):
        """Test combining two images horizontally."""
        img1 = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img2 = Image.new("RGB", (100, 100), color=(0, 255, 0))

        result = combine_images_horizontal([img1, img2], gap=0)

        assert result.width == 200
        assert result.height == 100

    def test_combine_with_gap(self):
        """Test combining with gap between images."""
        img1 = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img2 = Image.new("RGB", (100, 100), color=(0, 255, 0))

        result = combine_images_horizontal([img1, img2], gap=10)

        assert result.width == 210
        assert result.height == 100

    def test_combine_different_heights(self):
        """Test combining images with different heights."""
        img1 = Image.new("RGB", (100, 50), color=(255, 0, 0))
        img2 = Image.new("RGB", (100, 100), color=(0, 255, 0))

        result = combine_images_horizontal([img1, img2], gap=0)

        # Both should be resized to max height
        assert result.height == 100

    def test_empty_list_raises(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError):
            combine_images_horizontal([])


class TestCombineImagesVertical:
    """Tests for combine_images_vertical function."""

    def test_combine_two_images(self):
        """Test combining two images vertically."""
        img1 = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img2 = Image.new("RGB", (100, 100), color=(0, 255, 0))

        result = combine_images_vertical([img1, img2], gap=0)

        assert result.width == 100
        assert result.height == 200

    def test_combine_with_gap(self):
        """Test combining with gap between images."""
        img1 = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img2 = Image.new("RGB", (100, 100), color=(0, 255, 0))

        result = combine_images_vertical([img1, img2], gap=10)

        assert result.width == 100
        assert result.height == 210

    def test_combine_different_widths(self):
        """Test combining images with different widths."""
        img1 = Image.new("RGB", (50, 100), color=(255, 0, 0))
        img2 = Image.new("RGB", (100, 100), color=(0, 255, 0))

        result = combine_images_vertical([img1, img2], gap=0)

        # Both should be resized to max width
        assert result.width == 100
