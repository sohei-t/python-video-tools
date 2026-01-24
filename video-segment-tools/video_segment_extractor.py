#!/usr/bin/env python3
"""
Video Segment Extractor
設定ファイルで指定した時間範囲で動画を切り出すツール

Usage:
    python video_segment_extractor.py [OPTIONS]
    python video_segment_extractor.py -c config.txt -i ./videos -o ./output

Original: move_cut4.py (v6 2024-12-03)
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def find_ffmpeg() -> str:
    """ffmpegのパスを検出"""
    # 環境変数から取得
    ffmpeg_env = os.environ.get("FFMPEG_PATH")
    if ffmpeg_env and os.path.isfile(ffmpeg_env):
        return ffmpeg_env

    # PATHから検索
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # 一般的なインストール場所をチェック
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


def read_config_file(file_path: Path) -> Optional[Dict]:
    """設定ファイルを読み込み、辞書形式で返す"""
    config = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "start_end_times":
                        time_pairs = [pair.split("-") for pair in value.split(",")]
                        config[key] = [(start.strip(), end.strip()) for start, end in time_pairs]
                    else:
                        config[key] = value
    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{file_path}' が見つかりません。")
        return None
    except Exception as e:
        print(f"エラー: 設定ファイルの読み込みに失敗しました: {e}")
        return None

    return config


def normalize_time_format(time_str: str) -> str:
    """
    時間フォーマットを正規化する
    MM:SS -> 00:MM:SS
    MM:SS.s -> 00:MM:SS.s
    HH:MM:SS.s -> そのまま
    """
    time_str = time_str.strip()

    if re.match(r"^\d{1,2}:\d{2}(\.\d+)?$", time_str):
        # M:SS or MM:SS format
        return f"00:{time_str.zfill(5)}"
    elif re.match(r"^\d{1,2}:\d{2}:\d{2}(\.\d+)?$", time_str):
        # H:MM:SS or HH:MM:SS format
        return time_str
    else:
        raise ValueError(f"無効な時間フォーマット: {time_str}")


def get_video_files(directory: Path) -> List[Path]:
    """動画ファイルのリストを取得"""
    extensions = {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"}
    videos = []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            videos.append(file)

    return sorted(videos)


def extract_segments(
    ffmpeg_path: str,
    video_files: List[Path],
    time_ranges: List[Tuple[str, str]],
    output_dir: Path,
    codec_copy: bool = False,
) -> Tuple[int, int]:
    """動画から指定時間範囲を切り出す"""
    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    error_count = 0
    total_files = len(video_files)
    total_segments = len(time_ranges)

    for file_idx, input_file in enumerate(video_files, start=1):
        base_name = input_file.stem
        print(f"\n[{file_idx}/{total_files}] 処理中: {input_file.name}")

        # 既存ファイルの最大インデックスを取得
        existing_indices = []
        for f in output_dir.iterdir():
            match = re.search(rf"{re.escape(base_name)}_(\d+)\.mp4$", f.name)
            if match:
                existing_indices.append(int(match.group(1)))
        current_index = max(existing_indices) if existing_indices else 0

        for seg_idx, (start_time, end_time) in enumerate(time_ranges, start=1):
            try:
                normalized_start = normalize_time_format(start_time)
                normalized_end = normalize_time_format(end_time)
            except ValueError as e:
                print(f"  スキップ: {e}")
                error_count += 1
                continue

            current_index += 1
            output_file = output_dir / f"{base_name}_{current_index:03d}.mp4"

            print(
                f"  セグメント {seg_idx}/{total_segments}: "
                f"{normalized_start} - {normalized_end}"
            )

            # ffmpegコマンド構築
            if codec_copy:
                # 高速モード（再エンコードなし）
                command = [
                    ffmpeg_path,
                    "-y",
                    "-ss",
                    normalized_start,
                    "-i",
                    str(input_file),
                    "-to",
                    normalized_end,
                    "-c",
                    "copy",
                    str(output_file),
                ]
            else:
                # 再エンコードモード（より正確なカット）
                command = [
                    ffmpeg_path,
                    "-y",
                    "-i",
                    str(input_file),
                    "-ss",
                    normalized_start,
                    "-to",
                    normalized_end,
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    str(output_file),
                ]

            try:
                result = subprocess.run(
                    command,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )

                if result.returncode != 0:
                    print(f"    エラー: ffmpegが失敗しました")
                    error_count += 1
                    continue

                if not output_file.exists() or output_file.stat().st_size == 0:
                    print(f"    エラー: 出力ファイルが空です")
                    error_count += 1
                    continue

                print(f"    完了: {output_file.name}")
                success_count += 1

            except Exception as e:
                print(f"    エラー: {e}")
                error_count += 1

    return success_count, error_count


def main():
    parser = argparse.ArgumentParser(
        description="設定ファイルで指定した時間範囲で動画を切り出すツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                           # カレントディレクトリのconfig.txtを使用
  %(prog)s -c myconfig.txt           # 設定ファイルを指定
  %(prog)s -i ./videos -o ./output   # 入出力ディレクトリを指定
  %(prog)s --fast                    # 高速モード（再エンコードなし）

設定ファイル形式:
  start_end_times=03:03-03:14,05:55-06:15,08:25-09:10
  output_dir=segments
        """,
    )

    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.txt"),
        help="設定ファイルのパス (デフォルト: config.txt)",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=None,
        help="入力動画のディレクトリ (デフォルト: 設定ファイルと同じディレクトリ)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="出力ディレクトリ (デフォルト: 設定ファイルのoutput_dirまたはsegments)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="高速モード（再エンコードなし、カット位置が不正確な場合あり）",
    )
    parser.add_argument(
        "--ffmpeg",
        type=str,
        default=None,
        help="ffmpegの実行ファイルパス",
    )

    args = parser.parse_args()

    # ffmpegのパスを取得
    try:
        ffmpeg_path = args.ffmpeg or find_ffmpeg()
        print(f"ffmpeg: {ffmpeg_path}")
    except FileNotFoundError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    # 設定ファイルを読み込み
    config_path = args.config.resolve()
    if not config_path.exists():
        print(f"エラー: 設定ファイルが見つかりません: {config_path}")
        sys.exit(1)

    config = read_config_file(config_path)
    if config is None:
        sys.exit(1)

    # 時間範囲を取得
    time_ranges = config.get("start_end_times", [])
    if not time_ranges:
        print("エラー: 設定ファイルにstart_end_timesが定義されていません")
        sys.exit(1)

    # ディレクトリを設定
    input_dir = args.input_dir or config_path.parent
    output_dir = args.output_dir or (config_path.parent / config.get("output_dir", "segments"))

    print(f"入力ディレクトリ: {input_dir}")
    print(f"出力ディレクトリ: {output_dir}")
    print(f"切り出し範囲: {len(time_ranges)}件")

    # 動画ファイルを取得
    video_files = get_video_files(input_dir)
    if not video_files:
        print("エラー: 動画ファイルが見つかりませんでした")
        sys.exit(1)

    print(f"対象動画: {len(video_files)}件")

    # 切り出し実行
    success, errors = extract_segments(
        ffmpeg_path,
        video_files,
        time_ranges,
        output_dir,
        codec_copy=args.fast,
    )

    print(f"\n完了: 成功={success}, エラー={errors}")


if __name__ == "__main__":
    main()
