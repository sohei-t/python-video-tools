"""Tests for common.utils module."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for common module imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.utils import (
    FFmpegLocator,
    FFmpegRunner,
    MediaFileValidator,
    MediaFormatter,
)


# ---------------------------------------------------------------------------
# FFmpegLocator
# ---------------------------------------------------------------------------


class TestFFmpegLocator:
    """Tests for the FFmpegLocator class."""

    def test_find_ffmpeg_from_path(self) -> None:
        """Test that find_ffmpeg returns a path when ffmpeg is on PATH."""
        with patch("shutil.which", return_value="/usr/local/bin/ffmpeg"):
            result = FFmpegLocator.find_ffmpeg()
            assert result == "/usr/local/bin/ffmpeg"

    def test_find_ffmpeg_from_env(self) -> None:
        """Test that FFMPEG_PATH environment variable takes priority."""
        with (
            patch.dict("os.environ", {"FFMPEG_PATH": "/custom/ffmpeg"}),
            patch("os.path.isfile", return_value=True),
        ):
            result = FFmpegLocator.find_ffmpeg()
            assert result == "/custom/ffmpeg"

    def test_find_ffmpeg_not_found(self) -> None:
        """Test that find_ffmpeg returns None when ffmpeg is not available."""
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("shutil.which", return_value=None),
            patch("os.path.isfile", return_value=False),
        ):
            result = FFmpegLocator.find_ffmpeg()
            assert result is None

    def test_find_ffmpeg_common_paths(self) -> None:
        """Test fallback to common installation paths."""
        def mock_isfile(path: str) -> bool:
            return path == "/opt/homebrew/bin/ffmpeg"

        with (
            patch.dict("os.environ", {}, clear=True),
            patch("shutil.which", return_value=None),
            patch("os.path.isfile", side_effect=mock_isfile),
        ):
            result = FFmpegLocator.find_ffmpeg()
            assert result == "/opt/homebrew/bin/ffmpeg"

    def test_find_ffprobe_from_path(self) -> None:
        """Test that find_ffprobe returns a path when ffprobe is on PATH."""
        with patch("shutil.which", return_value="/usr/local/bin/ffprobe"):
            result = FFmpegLocator.find_ffprobe()
            assert result == "/usr/local/bin/ffprobe"

    def test_find_ffprobe_not_found(self) -> None:
        """Test that find_ffprobe returns None when not available."""
        with (
            patch("shutil.which", return_value=None),
            patch("os.path.isfile", return_value=False),
        ):
            result = FFmpegLocator.find_ffprobe()
            assert result is None

    def test_require_ffmpeg_success(self) -> None:
        """Test require_ffmpeg returns path when ffmpeg exists."""
        with patch.object(FFmpegLocator, "find_ffmpeg", return_value="/usr/bin/ffmpeg"):
            result = FFmpegLocator.require_ffmpeg()
            assert result == "/usr/bin/ffmpeg"

    def test_require_ffmpeg_raises(self) -> None:
        """Test require_ffmpeg raises FileNotFoundError when not found."""
        with patch.object(FFmpegLocator, "find_ffmpeg", return_value=None):
            with pytest.raises(FileNotFoundError):
                FFmpegLocator.require_ffmpeg()


# ---------------------------------------------------------------------------
# MediaFileValidator
# ---------------------------------------------------------------------------


class TestMediaFileValidator:
    """Tests for the MediaFileValidator class."""

    def test_is_video_file(self) -> None:
        """Test video file extension detection."""
        assert MediaFileValidator.is_video_file(Path("video.mp4")) is True
        assert MediaFileValidator.is_video_file(Path("video.avi")) is True
        assert MediaFileValidator.is_video_file(Path("video.mkv")) is True
        assert MediaFileValidator.is_video_file(Path("video.mov")) is True
        assert MediaFileValidator.is_video_file(Path("video.webm")) is True
        assert MediaFileValidator.is_video_file(Path("video.MP4")) is True
        assert MediaFileValidator.is_video_file(Path("doc.txt")) is False
        assert MediaFileValidator.is_video_file(Path("image.png")) is False

    def test_is_audio_file(self) -> None:
        """Test audio file extension detection."""
        assert MediaFileValidator.is_audio_file(Path("music.mp3")) is True
        assert MediaFileValidator.is_audio_file(Path("music.wav")) is True
        assert MediaFileValidator.is_audio_file(Path("music.flac")) is True
        assert MediaFileValidator.is_audio_file(Path("doc.txt")) is False

    def test_is_image_file(self) -> None:
        """Test image file extension detection."""
        assert MediaFileValidator.is_image_file(Path("photo.jpg")) is True
        assert MediaFileValidator.is_image_file(Path("photo.jpeg")) is True
        assert MediaFileValidator.is_image_file(Path("photo.png")) is True
        assert MediaFileValidator.is_image_file(Path("photo.webp")) is True
        assert MediaFileValidator.is_image_file(Path("doc.txt")) is False

    def test_get_video_files_from_directory(self) -> None:
        """Test collecting video files from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["video1.mp4", "video2.avi", "doc.txt", "image.png"]:
                Path(tmpdir, name).touch()

            videos = MediaFileValidator.get_video_files(Path(tmpdir))
            assert len(videos) == 2
            assert all(MediaFileValidator.is_video_file(f) for f in videos)

    def test_get_video_files_single_file(self) -> None:
        """Test get_video_files with a single video file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir, "video.mp4")
            video_path.touch()

            videos = MediaFileValidator.get_video_files(video_path)
            assert len(videos) == 1
            assert videos[0] == video_path

    def test_get_video_files_non_video(self) -> None:
        """Test get_video_files with a non-video file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir, "doc.txt")
            txt_path.touch()

            videos = MediaFileValidator.get_video_files(txt_path)
            assert len(videos) == 0

    def test_get_video_files_sorted(self) -> None:
        """Test that results are sorted alphabetically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["c.mp4", "a.mp4", "b.mp4"]:
                Path(tmpdir, name).touch()

            videos = MediaFileValidator.get_video_files(Path(tmpdir))
            assert videos[0].name == "a.mp4"
            assert videos[1].name == "b.mp4"
            assert videos[2].name == "c.mp4"

    def test_get_video_files_various_extensions(self) -> None:
        """Test that various video extensions are recognized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions = [".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv", ".wmv", ".m4v"]
            for ext in extensions:
                Path(tmpdir, f"video{ext}").touch()

            videos = MediaFileValidator.get_video_files(Path(tmpdir))
            assert len(videos) == len(extensions)

    def test_get_video_files_empty_directory(self) -> None:
        """Test get_video_files on an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            videos = MediaFileValidator.get_video_files(Path(tmpdir))
            assert len(videos) == 0

    def test_get_video_files_recursive(self) -> None:
        """Test recursive scanning of subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "top.mp4").touch()
            subdir = Path(tmpdir, "subdir")
            subdir.mkdir()
            Path(subdir, "nested.mp4").touch()

            # Non-recursive should only find top-level
            videos = MediaFileValidator.get_video_files(Path(tmpdir), recursive=False)
            assert len(videos) == 1

            # Recursive should find both
            videos = MediaFileValidator.get_video_files(Path(tmpdir), recursive=True)
            assert len(videos) == 2

    def test_get_audio_files(self) -> None:
        """Test collecting audio files from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["song.mp3", "sound.wav", "video.mp4", "doc.txt"]:
                Path(tmpdir, name).touch()

            audios = MediaFileValidator.get_audio_files(Path(tmpdir))
            assert len(audios) == 2
            assert all(MediaFileValidator.is_audio_file(f) for f in audios)

    def test_get_image_files(self) -> None:
        """Test collecting image files from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["photo.jpg", "icon.png", "video.mp4", "doc.txt"]:
                Path(tmpdir, name).touch()

            images = MediaFileValidator.get_image_files(Path(tmpdir))
            assert len(images) == 2
            assert all(MediaFileValidator.is_image_file(f) for f in images)


# ---------------------------------------------------------------------------
# MediaFormatter
# ---------------------------------------------------------------------------


class TestMediaFormatter:
    """Tests for the MediaFormatter class."""

    def test_format_size_bytes(self) -> None:
        """Test formatting small byte values."""
        assert MediaFormatter.format_size(0) == "0.0 B"
        assert MediaFormatter.format_size(512) == "512.0 B"

    def test_format_size_kilobytes(self) -> None:
        """Test formatting kilobyte values."""
        assert MediaFormatter.format_size(1024) == "1.0 KB"
        assert MediaFormatter.format_size(1536) == "1.5 KB"

    def test_format_size_megabytes(self) -> None:
        """Test formatting megabyte values."""
        assert MediaFormatter.format_size(1024 * 1024) == "1.0 MB"
        assert MediaFormatter.format_size(10 * 1024 * 1024) == "10.0 MB"

    def test_format_size_gigabytes(self) -> None:
        """Test formatting gigabyte values."""
        assert MediaFormatter.format_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_format_size_terabytes(self) -> None:
        """Test formatting terabyte values."""
        assert MediaFormatter.format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_format_duration_zero(self) -> None:
        """Test formatting zero duration."""
        assert MediaFormatter.format_duration(0) == "00:00:00.00"

    def test_format_duration_seconds(self) -> None:
        """Test formatting seconds-only duration."""
        assert MediaFormatter.format_duration(30) == "00:00:30.00"
        assert MediaFormatter.format_duration(30.5) == "00:00:30.50"

    def test_format_duration_minutes(self) -> None:
        """Test formatting durations with minutes."""
        assert MediaFormatter.format_duration(90) == "00:01:30.00"

    def test_format_duration_hours(self) -> None:
        """Test formatting durations with hours."""
        assert MediaFormatter.format_duration(3661.5) == "01:01:01.50"
        assert MediaFormatter.format_duration(7200) == "02:00:00.00"


# ---------------------------------------------------------------------------
# FFmpegRunner
# ---------------------------------------------------------------------------


class TestFFmpegRunner:
    """Tests for the FFmpegRunner class."""

    def test_init_with_explicit_paths(self) -> None:
        """Test initialization with explicit ffmpeg/ffprobe paths."""
        runner = FFmpegRunner(
            ffmpeg_path="/custom/ffmpeg",
            ffprobe_path="/custom/ffprobe",
        )
        assert runner.ffmpeg == "/custom/ffmpeg"
        assert runner.ffprobe == "/custom/ffprobe"

    def test_init_auto_detect(self) -> None:
        """Test initialization with auto-detection."""
        with (
            patch.object(FFmpegLocator, "find_ffmpeg", return_value="/auto/ffmpeg"),
            patch.object(FFmpegLocator, "find_ffprobe", return_value="/auto/ffprobe"),
        ):
            runner = FFmpegRunner()
            assert runner.ffmpeg == "/auto/ffmpeg"
            assert runner.ffprobe == "/auto/ffprobe"

    def test_run_raises_without_ffmpeg(self) -> None:
        """Test that run raises FileNotFoundError when ffmpeg is not set."""
        runner = FFmpegRunner(ffmpeg_path=None)
        runner.ffmpeg = None
        with pytest.raises(FileNotFoundError):
            runner.run(["-version"])

    def test_run_executes_command(self) -> None:
        """Test that run properly calls subprocess."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            runner = FFmpegRunner(ffmpeg_path="/usr/bin/ffmpeg")
            runner.run(["-y", "-i", "input.mp4", "output.mp4"])

            mock_run.assert_called_once_with(
                ["/usr/bin/ffmpeg", "-y", "-i", "input.mp4", "output.mp4"],
                check=True,
                capture_output=True,
                text=True,
            )

    def test_get_duration_raises_without_ffprobe(self) -> None:
        """Test get_duration raises when ffprobe is not available."""
        runner = FFmpegRunner(ffmpeg_path="/usr/bin/ffmpeg")
        runner.ffprobe = None
        with pytest.raises(FileNotFoundError):
            runner.get_duration("video.mp4")

    def test_get_duration_success(self) -> None:
        """Test successful duration retrieval."""
        mock_result = MagicMock()
        mock_result.stdout = '{"format": {"duration": "120.5"}}'

        with patch("subprocess.run", return_value=mock_result):
            runner = FFmpegRunner(
                ffmpeg_path="/usr/bin/ffmpeg",
                ffprobe_path="/usr/bin/ffprobe",
            )
            duration = runner.get_duration("video.mp4")
            assert duration == 120.5

    def test_get_resolution_success(self) -> None:
        """Test successful resolution retrieval."""
        mock_result = MagicMock()
        mock_result.stdout = '{"streams": [{"codec_type": "video", "width": 1920, "height": 1080}]}'

        with patch("subprocess.run", return_value=mock_result):
            runner = FFmpegRunner(
                ffmpeg_path="/usr/bin/ffmpeg",
                ffprobe_path="/usr/bin/ffprobe",
            )
            width, height = runner.get_resolution("video.mp4")
            assert width == 1920
            assert height == 1080

    def test_get_resolution_raises_without_ffprobe(self) -> None:
        """Test get_resolution raises when ffprobe is not available."""
        runner = FFmpegRunner(ffmpeg_path="/usr/bin/ffmpeg")
        runner.ffprobe = None
        with pytest.raises(FileNotFoundError):
            runner.get_resolution("video.mp4")

    def test_get_resolution_no_video_stream(self) -> None:
        """Test get_resolution raises when no video stream is found."""
        mock_result = MagicMock()
        mock_result.stdout = '{"streams": [{"codec_type": "audio"}]}'

        with patch("subprocess.run", return_value=mock_result):
            runner = FFmpegRunner(
                ffmpeg_path="/usr/bin/ffmpeg",
                ffprobe_path="/usr/bin/ffprobe",
            )
            with pytest.raises(RuntimeError):
                runner.get_resolution("audio_only.mp4")

    def test_get_video_info_success(self) -> None:
        """Test successful video info retrieval."""
        mock_result = MagicMock()
        mock_result.stdout = (
            '{"streams": ['
            '{"codec_type": "video", "r_frame_rate": "30/1"},'
            '{"codec_type": "audio"}'
            "]}"
        )

        with patch("subprocess.run", return_value=mock_result):
            runner = FFmpegRunner(
                ffmpeg_path="/usr/bin/ffmpeg",
                ffprobe_path="/usr/bin/ffprobe",
            )
            info = runner.get_video_info("video.mp4")
            assert info["fps"] == 30.0
            assert info["has_audio"] is True

    def test_get_video_info_no_ffprobe(self) -> None:
        """Test get_video_info returns defaults when ffprobe is not available."""
        runner = FFmpegRunner(ffmpeg_path="/usr/bin/ffmpeg")
        runner.ffprobe = None
        info = runner.get_video_info("video.mp4")
        assert info["fps"] is None
        assert info["has_audio"] is False

    def test_get_video_info_handles_exception(self) -> None:
        """Test get_video_info handles subprocess errors gracefully."""
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ffprobe")):
            runner = FFmpegRunner(
                ffmpeg_path="/usr/bin/ffmpeg",
                ffprobe_path="/usr/bin/ffprobe",
            )
            info = runner.get_video_info("nonexistent.mp4")
            assert info["fps"] is None
            assert info["has_audio"] is False
