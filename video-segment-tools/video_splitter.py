#!/usr/bin/env python3
"""
Video Splitter
動画を指定した時間間隔で分割するツール

Usage:
    python video_splitter.py [OPTIONS]
    python video_splitter.py -d 00:10:00              # 10分ごとに分割
    python video_splitter.py -d 00:05:00 -i video.mp4 # 特定ファイルを5分ごとに分割

Original: 指定時間で分割する.py
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def find_ffmpeg() -> str:
    """ffmpegのパスを検出"""
    ffmpeg_env = os.environ.get("FFMPEG_PATH")
    if ffmpeg_env and os.path.isfile(ffmpeg_env):
        return ffmpeg_env

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    common_paths = [
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]
    for path in common_paths:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(
        "ffmpegが見つかりません。ffmpegをインストールするか、"
        "FFMPEG_PATH環境変数でパスを指定してください。"
    )


def find_ffprobe() -> str:
    """ffprobeのパスを検出"""
    ffprobe_env = os.environ.get("FFPROBE_PATH")
    if ffprobe_env and os.path.isfile(ffprobe_env):
        return ffprobe_env

    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        return ffprobe_path

    common_paths = [
        "/usr/local/bin/ffprobe",
        "/usr/bin/ffprobe",
        "/opt/homebrew/bin/ffprobe",
    ]
    for path in common_paths:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError("ffprobeが見つかりません。ffmpegをインストールしてください。")


def parse_duration(duration_str: str) -> float:
    """HH:MM:SS形式の文字列を秒数に変換"""
    parts = duration_str.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    else:
        return float(duration_str)


def format_duration(seconds: float) -> str:
    """秒数をHH:MM:SS形式に変換"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


def get_video_duration(ffprobe_path: str, video_path: Path) -> float:
    """動画の長さを取得（秒）"""
    cmd = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"動画の長さを取得できません: {video_path}")
    return float(result.stdout.strip())


def get_video_files(directory: Path) -> List[Path]:
    """動画ファイルのリストを取得"""
    extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}
    videos = []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            videos.append(file)

    return sorted(videos)


def split_video(
    ffmpeg_path: str,
    ffprobe_path: str,
    video_path: Path,
    split_duration: float,
    output_dir: Optional[Path] = None,
    overhead: float = 10.0,
) -> int:
    """動画を指定時間で分割"""
    if output_dir is None:
        output_dir = video_path.parent

    os.makedirs(output_dir, exist_ok=True)

    # 動画の長さを取得
    try:
        total_duration = get_video_duration(ffprobe_path, video_path)
    except Exception as e:
        print(f"エラー: {e}")
        return 0

    print(f"動画の長さ: {format_duration(total_duration)}")
    print(f"分割間隔: {format_duration(split_duration)}")

    base_name = video_path.stem
    ext = video_path.suffix
    current_time = 0.0
    index = 1
    success_count = 0

    while current_time < total_duration:
        remaining = total_duration - current_time

        # 残りが分割時間+オーバーヘッド以下なら最後のセグメント
        if remaining <= split_duration + overhead:
            segment_duration = remaining
        else:
            segment_duration = split_duration

        output_file = output_dir / f"{base_name}_{index:04d}{ext}"

        print(
            f"  セグメント {index}: "
            f"{format_duration(current_time)} - "
            f"{format_duration(current_time + segment_duration)}"
        )

        cmd = [
            ffmpeg_path,
            "-y",
            "-ss",
            str(current_time),
            "-i",
            str(video_path),
            "-t",
            str(segment_duration),
            "-c",
            "copy",
            str(output_file),
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        if result.returncode == 0 and output_file.exists():
            print(f"    完了: {output_file.name}")
            success_count += 1
        else:
            print(f"    エラー: 分割に失敗しました")

        current_time += segment_duration
        index += 1

    return success_count


def main():
    parser = argparse.ArgumentParser(
        description="動画を指定した時間間隔で分割するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s -d 00:10:00              # カレントディレクトリの動画を10分ごとに分割
  %(prog)s -d 00:05:00 -i video.mp4 # 特定ファイルを5分ごとに分割
  %(prog)s -d 00:30:00 -o ./output  # 出力先を指定

注意:
  - 高速化のため再エンコードなし（-c copy）で分割します
  - 最後のセグメントが短い場合は前のセグメントと結合されます（オーバーヘッド: 10秒）
        """,
    )

    parser.add_argument(
        "-d",
        "--duration",
        type=str,
        required=True,
        help="分割時間間隔 (HH:MM:SS形式)",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=None,
        help="入力動画ファイルまたはディレクトリ (デフォルト: カレントディレクトリ)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="出力ディレクトリ (デフォルト: 入力と同じディレクトリ)",
    )
    parser.add_argument(
        "--overhead",
        type=float,
        default=10.0,
        help="最後のセグメントを結合するオーバーヘッド秒数 (デフォルト: 10)",
    )
    parser.add_argument(
        "--ffmpeg",
        type=str,
        default=None,
        help="ffmpegの実行ファイルパス",
    )

    args = parser.parse_args()

    # ffmpeg/ffprobeのパスを取得
    try:
        ffmpeg_path = args.ffmpeg or find_ffmpeg()
        ffprobe_path = find_ffprobe()
        print(f"ffmpeg: {ffmpeg_path}")
    except FileNotFoundError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    # 分割時間をパース
    try:
        split_duration = parse_duration(args.duration)
        if split_duration <= 0:
            raise ValueError("分割時間は正の値である必要があります")
    except ValueError as e:
        print(f"エラー: 無効な時間形式です: {args.duration}")
        sys.exit(1)

    # 入力を取得
    if args.input is None:
        input_path = Path.cwd()
    else:
        input_path = args.input.resolve()

    if not input_path.exists():
        print(f"エラー: パスが存在しません: {input_path}")
        sys.exit(1)

    # 動画ファイルリストを作成
    if input_path.is_file():
        video_files = [input_path]
    else:
        video_files = get_video_files(input_path)

    if not video_files:
        print("エラー: 動画ファイルが見つかりませんでした")
        sys.exit(1)

    print(f"対象動画: {len(video_files)}件")
    print(f"分割間隔: {format_duration(split_duration)}")

    # 分割実行
    total_segments = 0
    for video_file in video_files:
        print(f"\n処理中: {video_file.name}")
        output_dir = args.output_dir or video_file.parent
        segments = split_video(
            ffmpeg_path,
            ffprobe_path,
            video_file,
            split_duration,
            output_dir,
            args.overhead,
        )
        total_segments += segments

    print(f"\n完了: {total_segments}セグメントを作成しました")


if __name__ == "__main__":
    main()
