"""
Shared utilities for python-video-tools.

Provides reusable classes for locating ffmpeg/ffprobe, validating media files,
formatting display values, and running ffmpeg commands with consistent error
handling. These utilities are shared across multiple tools to eliminate
code duplication and ensure uniform behavior.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


class FFmpegLocator:
    """Locate ffmpeg and ffprobe executables on the system.

    Searches the system PATH and common installation directories
    to find ffmpeg and ffprobe binaries. Also supports discovery
    via the FFMPEG_PATH environment variable.
    """

    _COMMON_FFMPEG_PATHS: list[str] = [
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]

    _COMMON_FFPROBE_PATHS: list[str] = [
        "/usr/local/bin/ffprobe",
        "/opt/homebrew/bin/ffprobe",
        "/usr/bin/ffprobe",
    ]

    @staticmethod
    def find_ffmpeg() -> str | None:
        """Locate the ffmpeg executable.

        Search order:
            1. FFMPEG_PATH environment variable
            2. System PATH (via shutil.which)
            3. Common installation directories

        Returns:
            Path to the ffmpeg executable, or None if not found.
        """
        # Check environment variable first
        ffmpeg_env = os.environ.get("FFMPEG_PATH")
        if ffmpeg_env and os.path.isfile(ffmpeg_env):
            return ffmpeg_env

        # Search system PATH
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return ffmpeg_path

        # Check common installation paths
        for path in FFmpegLocator._COMMON_FFMPEG_PATHS:
            if os.path.isfile(path):
                return path

        return None

    @staticmethod
    def find_ffprobe() -> str | None:
        """Locate the ffprobe executable.

        Search order:
            1. System PATH (via shutil.which)
            2. Common installation directories

        Returns:
            Path to the ffprobe executable, or None if not found.
        """
        ffprobe_path = shutil.which("ffprobe")
        if ffprobe_path:
            return ffprobe_path

        for path in FFmpegLocator._COMMON_FFPROBE_PATHS:
            if os.path.isfile(path):
                return path

        return None

    @staticmethod
    def require_ffmpeg() -> str:
        """Locate ffmpeg or raise FileNotFoundError.

        Returns:
            Path to the ffmpeg executable.

        Raises:
            FileNotFoundError: If ffmpeg cannot be found on the system.
        """
        ffmpeg_path = FFmpegLocator.find_ffmpeg()
        if not ffmpeg_path:
            raise FileNotFoundError(
                "ffmpegが見つかりません。ffmpegをインストールするか、"
                "FFMPEG_PATH環境変数でパスを指定してください。"
            )
        return ffmpeg_path


class MediaFileValidator:
    """Validate and filter media files by their extensions.

    Provides class-level constants for recognized video, audio, and image
    file extensions, along with helper methods to discover matching files
    in a given directory or validate a single file path.
    """

    VIDEO_EXTENSIONS: set[str] = {
        ".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".webm", ".m4v",
        ".mpg", ".asf", ".ogm",
    }

    AUDIO_EXTENSIONS: set[str] = {
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma",
    }

    IMAGE_EXTENSIONS: set[str] = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
    }

    @classmethod
    def is_video_file(cls, path: Path) -> bool:
        """Check whether a file path has a recognized video extension.

        Args:
            path: The file path to check.

        Returns:
            True if the file extension is a recognized video format.
        """
        return path.suffix.lower() in cls.VIDEO_EXTENSIONS

    @classmethod
    def is_audio_file(cls, path: Path) -> bool:
        """Check whether a file path has a recognized audio extension.

        Args:
            path: The file path to check.

        Returns:
            True if the file extension is a recognized audio format.
        """
        return path.suffix.lower() in cls.AUDIO_EXTENSIONS

    @classmethod
    def is_image_file(cls, path: Path) -> bool:
        """Check whether a file path has a recognized image extension.

        Args:
            path: The file path to check.

        Returns:
            True if the file extension is a recognized image format.
        """
        return path.suffix.lower() in cls.IMAGE_EXTENSIONS

    @classmethod
    def get_video_files(cls, path: Path, recursive: bool = False) -> list[Path]:
        """Collect video files from a path.

        If *path* is a single file with a recognized video extension it is
        returned as a one-element list.  If *path* is a directory its
        immediate children (or all descendants when *recursive* is True) are
        scanned for video files.

        Args:
            path: A file or directory path to scan.
            recursive: When True and *path* is a directory, search recursively.

        Returns:
            Sorted list of Path objects pointing to video files.
        """
        if path.is_file():
            if cls.is_video_file(path):
                return [path]
            return []

        if recursive:
            videos = [
                f for f in path.rglob("*")
                if f.is_file() and cls.is_video_file(f)
            ]
        else:
            videos = [
                f for f in path.iterdir()
                if f.is_file() and cls.is_video_file(f)
            ]

        return sorted(videos)

    @classmethod
    def get_audio_files(cls, path: Path, recursive: bool = False) -> list[Path]:
        """Collect audio files from a path.

        Args:
            path: A file or directory path to scan.
            recursive: When True and *path* is a directory, search recursively.

        Returns:
            Sorted list of Path objects pointing to audio files.
        """
        if path.is_file():
            if cls.is_audio_file(path):
                return [path]
            return []

        if recursive:
            audios = [
                f for f in path.rglob("*")
                if f.is_file() and cls.is_audio_file(f)
            ]
        else:
            audios = [
                f for f in path.iterdir()
                if f.is_file() and cls.is_audio_file(f)
            ]

        return sorted(audios)

    @classmethod
    def get_image_files(cls, path: Path, recursive: bool = False) -> list[Path]:
        """Collect image files from a path.

        Args:
            path: A file or directory path to scan.
            recursive: When True and *path* is a directory, search recursively.

        Returns:
            Sorted list of Path objects pointing to image files.
        """
        if path.is_file():
            if cls.is_image_file(path):
                return [path]
            return []

        if recursive:
            images = [
                f for f in path.rglob("*")
                if f.is_file() and cls.is_image_file(f)
            ]
        else:
            images = [
                f for f in path.iterdir()
                if f.is_file() and cls.is_image_file(f)
            ]

        return sorted(images)


class MediaFormatter:
    """Format media-related values for human-readable display.

    Provides static methods to convert raw byte sizes and durations into
    friendly string representations.
    """

    @staticmethod
    def format_size(bytes_val: int) -> str:
        """Format a byte count as a human-readable string.

        Converts the given byte value to the most appropriate unit
        (B, KB, MB, GB, or TB) with one decimal place.

        Args:
            bytes_val: The size in bytes.

        Returns:
            A formatted string such as ``"12.3 MB"`` or ``"1.5 GB"``.
        """
        size = float(bytes_val)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format a duration in seconds as ``HH:MM:SS.ss``.

        Args:
            seconds: Duration in seconds (may include fractional seconds).

        Returns:
            A formatted time string such as ``"01:23:45.67"``.
        """
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:05.2f}"


class FFmpegRunner:
    """Execute ffmpeg/ffprobe commands with consistent error handling.

    Wraps subprocess calls to ffmpeg and ffprobe, providing convenient
    methods for common probe operations (duration, resolution) and a
    generic ``run`` method for arbitrary ffmpeg invocations.

    Args:
        ffmpeg_path: Explicit path to ffmpeg. When ``None``,
            :meth:`FFmpegLocator.find_ffmpeg` is used.
        ffprobe_path: Explicit path to ffprobe. When ``None``,
            :meth:`FFmpegLocator.find_ffprobe` is used.
    """

    def __init__(
        self,
        ffmpeg_path: str | None = None,
        ffprobe_path: str | None = None,
    ) -> None:
        self.ffmpeg: str | None = ffmpeg_path or FFmpegLocator.find_ffmpeg()
        self.ffprobe: str | None = ffprobe_path or FFmpegLocator.find_ffprobe()

    def run(
        self,
        args: list[str],
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Run an ffmpeg command.

        The ffmpeg executable path is prepended to *args* automatically.

        Args:
            args: Command-line arguments (without the leading ``ffmpeg``).
            capture_output: Whether to capture stdout/stderr.

        Returns:
            The completed process result.

        Raises:
            FileNotFoundError: If ffmpeg has not been located.
            subprocess.CalledProcessError: If ffmpeg exits with a non-zero
                return code.
        """
        if not self.ffmpeg:
            raise FileNotFoundError("ffmpegが見つかりません")

        cmd = [self.ffmpeg] + args
        return subprocess.run(
            cmd,
            check=True,
            capture_output=capture_output,
            text=True,
        )

    def get_duration(self, filepath: str) -> float:
        """Retrieve the duration of a media file in seconds.

        Uses ffprobe to read the container-level duration.

        Args:
            filepath: Path to the media file.

        Returns:
            Duration in seconds.

        Raises:
            FileNotFoundError: If ffprobe has not been located.
            RuntimeError: If the duration cannot be determined.
        """
        if not self.ffprobe:
            raise FileNotFoundError("ffprobeが見つかりません")

        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            filepath,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration_str = data.get("format", {}).get("duration")
        if duration_str is None:
            raise RuntimeError(f"動画の長さを取得できません: {filepath}")
        return float(duration_str)

    def get_resolution(self, filepath: str) -> tuple[int, int]:
        """Retrieve the resolution (width, height) of a video file.

        Uses ffprobe to inspect the first video stream.

        Args:
            filepath: Path to the video file.

        Returns:
            A ``(width, height)`` tuple.

        Raises:
            FileNotFoundError: If ffprobe has not been located.
            RuntimeError: If the resolution cannot be determined.
        """
        if not self.ffprobe:
            raise FileNotFoundError("ffprobeが見つかりません")

        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            filepath,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                width = stream.get("width")
                height = stream.get("height")
                if width is not None and height is not None:
                    return (int(width), int(height))

        raise RuntimeError(f"解像度を取得できません: {filepath}")

    def get_video_info(self, filepath: str) -> dict[str, object]:
        """Retrieve basic video stream information.

        Returns a dictionary containing ``fps`` (float or None) and
        ``has_audio`` (bool).

        Args:
            filepath: Path to the video file.

        Returns:
            A dict with keys ``"fps"`` and ``"has_audio"``.
        """
        if not self.ffprobe:
            return {"fps": None, "has_audio": False}

        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            filepath,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            info: dict[str, object] = {"fps": None, "has_audio": False}

            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    fps_str = stream.get("r_frame_rate", "0/1")
                    if "/" in fps_str:
                        num, den = fps_str.split("/")
                        info["fps"] = (
                            float(num) / float(den) if float(den) > 0 else 0
                        )
                elif stream.get("codec_type") == "audio":
                    info["has_audio"] = True

            return info
        except Exception:
            return {"fps": None, "has_audio": False}
