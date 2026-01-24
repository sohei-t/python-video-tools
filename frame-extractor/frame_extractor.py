#!/usr/bin/env python3
"""
Frame Extractor
動画から指定間隔で静止画（フレーム）を抽出するツール

Usage:
    python frame_extractor.py [OPTIONS] [INPUT...]
    python frame_extractor.py video.mp4 --interval 1
    python frame_extractor.py video.mp4 --range 00:01:00-00:02:00
    python frame_extractor.py -i ./videos -o ./frames

Requirements:
    pip install opencv-python

Original: 画像キャプチャ.py
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import cv2
except ImportError:
    print("エラー: OpenCVがインストールされていません")
    print("インストール: pip install opencv-python")
    sys.exit(1)


def parse_time(time_str: str) -> float:
    """時間文字列を秒に変換（複数フォーマット対応）"""
    time_str = time_str.strip()

    # 秒のみ（例: 90, 90.5）
    if re.match(r"^[\d.]+$", time_str):
        return float(time_str)

    # MM:SS形式（例: 01:30）
    match = re.match(r"^(\d+):(\d+(?:\.\d+)?)$", time_str)
    if match:
        m, s = match.groups()
        return int(m) * 60 + float(s)

    # HH:MM:SS形式（例: 00:01:30）
    match = re.match(r"^(\d+):(\d+):(\d+(?:\.\d+)?)$", time_str)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)

    raise ValueError(f"無効な時間形式: {time_str}")


def parse_range(range_str: str) -> Tuple[float, float]:
    """時間範囲を解析（例: 00:01:00-00:02:00）"""
    # 区切り文字を正規化
    range_str = range_str.replace("--", "-").strip()

    parts = range_str.split("-")
    if len(parts) == 2:
        return parse_time(parts[0]), parse_time(parts[1])
    elif len(parts) == 4:
        # HH:MM:SS-HH:MM:SS形式の場合
        start = f"{parts[0]}:{parts[1]}"
        end = f"{parts[2]}:{parts[3]}"
        return parse_time(start), parse_time(end)
    elif len(parts) == 6:
        # HH:MM:SS-HH:MM:SS形式の場合
        start = f"{parts[0]}:{parts[1]}:{parts[2]}"
        end = f"{parts[3]}:{parts[4]}:{parts[5]}"
        return parse_time(start), parse_time(end)

    raise ValueError(f"無効な範囲形式: {range_str}")


def parse_ranges(ranges_str: str) -> List[Tuple[float, float]]:
    """複数の時間範囲を解析（カンマ区切り）"""
    ranges = []
    for part in ranges_str.split(","):
        part = part.strip()
        if part:
            ranges.append(parse_range(part))
    return ranges


def format_time(seconds: float) -> str:
    """秒を時間文字列に変換"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


def get_video_files(path: Path) -> List[Path]:
    """指定パスから動画ファイルを取得"""
    extensions = {".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".webm", ".m4v"}

    if path.is_file():
        if path.suffix.lower() in extensions:
            return [path]
        return []

    videos = []
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            videos.append(file)

    return sorted(videos)


def read_config(config_path: Path) -> dict:
    """config.txtを読み込み"""
    config = {}
    if not config_path.exists():
        return config

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    return config


def extract_frames(
    video_path: Path,
    output_dir: Path,
    interval: float = 1.0,
    ranges: Optional[List[Tuple[float, float]]] = None,
    format: str = "jpg",
    quality: int = 95,
    prefix: str = "",
) -> int:
    """動画からフレームを抽出"""
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print(f"  エラー: 動画を開けません")
        return 0

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    # 範囲が指定されていない場合は全体
    if not ranges:
        ranges = [(0, duration)]

    video_name = video_path.stem
    if prefix:
        base_name = f"{prefix}{video_name}"
    else:
        base_name = video_name

    interval_frames = int(fps * interval)
    saved_count = 0
    frame_index = 1

    # 保存オプション
    if format.lower() == "jpg":
        ext = ".jpg"
        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    elif format.lower() == "png":
        ext = ".png"
        params = [cv2.IMWRITE_PNG_COMPRESSION, min(9, (100 - quality) // 10)]
    else:
        ext = f".{format}"
        params = []

    for start_time, end_time in ranges:
        start_frame = int(fps * start_time)
        end_frame = min(int(fps * end_time), total_frames)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        frame_count = start_frame

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame_count > end_frame:
                break

            if (frame_count - start_frame) % interval_frames == 0:
                output_path = output_dir / f"{base_name}_{frame_index:04d}{ext}"
                cv2.imwrite(str(output_path), frame, params)
                saved_count += 1
                frame_index += 1

            frame_count += 1

    cap.release()
    return saved_count


def main():
    parser = argparse.ArgumentParser(
        description="動画から指定間隔で静止画を抽出するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s video.mp4                          # 1秒間隔で全フレームを抽出
  %(prog)s video.mp4 --interval 0.5           # 0.5秒間隔で抽出
  %(prog)s video.mp4 --range 00:01:00-00:02:00  # 1分〜2分の範囲のみ
  %(prog)s video.mp4 --range "0:00-1:00,2:00-3:00"  # 複数範囲
  %(prog)s -i ./videos -o ./frames            # ディレクトリ処理
  %(prog)s video.mp4 --format png --quality 100  # PNG形式で保存

時間指定形式:
  秒:      90, 90.5
  MM:SS:   01:30
  HH:MM:SS: 00:01:30

config.txtを使用する場合:
  interval=1
  periods=00:00:00--00:04:53,00:10:00--00:15:00
        """,
    )

    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="入力ファイルまたはディレクトリ",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=None,
        help="入力ディレクトリ",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="出力ディレクトリ（デフォルト: ./comp）",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="フレーム抽出間隔（秒、デフォルト: 1.0）",
    )
    parser.add_argument(
        "--range",
        type=str,
        default=None,
        help="抽出する時間範囲（例: 00:01:00-00:02:00）複数はカンマ区切り",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="jpg",
        choices=["jpg", "png", "bmp"],
        help="出力フォーマット（デフォルト: jpg）",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="画質（1-100、デフォルト: 95）",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="出力ファイル名のプレフィックス",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="設定ファイルのパス（config.txt形式）",
    )
    parser.add_argument(
        "--no-move",
        action="store_true",
        help="処理後に元ファイルを移動しない",
    )

    args = parser.parse_args()

    # config.txtの読み込み
    config = {}
    if args.config:
        config = read_config(args.config)
    elif Path("config.txt").exists() and not args.inputs and not args.input_dir:
        config = read_config(Path("config.txt"))

    # パラメータの決定（CLIオプション > config.txt > デフォルト）
    interval = args.interval or float(config.get("interval", 1.0))

    ranges = None
    if args.range:
        ranges = parse_ranges(args.range)
    elif "periods" in config:
        ranges = parse_ranges(config["periods"])

    # 入力ファイルを収集
    video_files = []

    if args.inputs:
        for input_path in args.inputs:
            if not input_path.exists():
                print(f"警告: ファイルが見つかりません: {input_path}")
                continue
            video_files.extend(get_video_files(input_path))
    elif args.input_dir:
        if not args.input_dir.exists():
            print(f"エラー: ディレクトリが存在しません: {args.input_dir}")
            sys.exit(1)
        video_files = get_video_files(args.input_dir)
    else:
        video_files = get_video_files(Path.cwd())

    if not video_files:
        print("エラー: 動画ファイルが見つかりません")
        sys.exit(1)

    # 出力ディレクトリ
    output_dir = (args.output_dir or Path("./comp")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    done_dir = Path("./done").resolve()
    if not args.no_move:
        done_dir.mkdir(parents=True, exist_ok=True)

    # 設定を表示
    print(f"抽出間隔: {interval}秒")
    if ranges:
        range_strs = [f"{format_time(s)}-{format_time(e)}" for s, e in ranges]
        print(f"時間範囲: {', '.join(range_strs)}")
    else:
        print("時間範囲: 全体")
    print(f"出力: {output_dir}")
    print(f"対象: {len(video_files)}ファイル")
    print()

    # 処理実行
    total_frames = 0

    for i, video_file in enumerate(video_files):
        print(f"[{i+1}/{len(video_files)}] {video_file.name}")

        saved = extract_frames(
            video_file,
            output_dir,
            interval=interval,
            ranges=ranges,
            format=args.format,
            quality=args.quality,
            prefix=args.prefix,
        )

        print(f"  → {saved}フレーム抽出")
        total_frames += saved

        # 元ファイルを移動
        if not args.no_move and video_file.parent != done_dir:
            try:
                shutil.move(str(video_file), str(done_dir / video_file.name))
            except Exception as e:
                print(f"  警告: ファイル移動失敗: {e}")

    # 結果表示
    print()
    print("=" * 50)
    print(f"完了: {len(video_files)}動画から{total_frames}フレームを抽出")
    print(f"出力先: {output_dir}")


if __name__ == "__main__":
    main()
