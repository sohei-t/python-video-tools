#!/usr/bin/env python3
"""
Video Compressor
動画ファイルを分割→圧縮→結合してファイルサイズを縮小するツール

Usage:
    python video_compressor.py [OPTIONS]
    python video_compressor.py --crf 28 --scale 0.5
    python video_compressor.py -i video.mp4 -o compressed.mp4

Original: size_small.py, size_small_20240730.py
"""

import argparse
import configparser
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
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


def get_video_files(directory: Path) -> List[Path]:
    """ディレクトリから動画ファイルを取得"""
    extensions = {".avi", ".asf", ".mov", ".mpg", ".wmv", ".ogm", ".mp4", ".mkv"}
    videos = []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            videos.append(file)

    return sorted(videos)


def load_config(config_path: Path) -> dict:
    """設定ファイルを読み込む"""
    config = {}
    if config_path.exists():
        parser = configparser.ConfigParser()
        parser.read(config_path)
        if "Settings" in parser:
            settings = parser["Settings"]
            if "resolution_scale" in settings:
                config["scale"] = float(settings["resolution_scale"])
            if "crf" in settings:
                config["crf"] = int(settings["crf"])
    return config


def compress_video(
    ffmpeg_path: str,
    input_path: Path,
    output_path: Path,
    crf: int = 28,
    preset: str = "fast",
    scale: Optional[float] = None,
    segment_seconds: int = 5,
) -> bool:
    """動画を圧縮する（分割→圧縮→結合方式）"""

    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Step 1: 動画を分割
        print(f"  分割中... ({segment_seconds}秒ごと)")
        segment_pattern = temp_path / "segment_%03d.mp4"
        split_cmd = [
            ffmpeg_path,
            "-y",
            "-i", str(input_path),
            "-c", "copy",
            "-map", "0",
            "-segment_time", str(segment_seconds),
            "-f", "segment",
            "-reset_timestamps", "1",
            str(segment_pattern),
        ]

        result = subprocess.run(split_cmd, capture_output=True)
        if result.returncode != 0:
            print(f"    分割エラー: {result.stderr.decode()[:200]}")
            return False

        # 分割されたファイルを取得
        segments = sorted(temp_path.glob("segment_*.mp4"))
        if not segments:
            print("    エラー: 分割されたセグメントがありません")
            return False

        print(f"    {len(segments)}セグメントに分割完了")

        # Step 2: 各セグメントを圧縮
        print(f"  圧縮中... (CRF={crf}, preset={preset})")
        compressed_segments = []

        for i, segment in enumerate(segments):
            compressed_path = temp_path / f"compressed_{segment.name}"

            # スケールフィルタを構築
            if scale and scale != 1.0:
                # 偶数にする（libx264の要件）
                scale_filter = f"scale=ceil(iw*{scale}/2)*2:ceil(ih*{scale}/2)*2,setsar=1"
            else:
                scale_filter = "scale=ceil(iw/2)*2:ceil(ih/2)*2,setsar=1"

            compress_cmd = [
                ffmpeg_path,
                "-y",
                "-i", str(segment),
                "-vf", scale_filter,
                "-vcodec", "libx264",
                "-crf", str(crf),
                "-preset", preset,
                "-acodec", "aac",
                "-b:a", "128k",
                str(compressed_path),
            ]

            result = subprocess.run(compress_cmd, capture_output=True)
            if result.returncode != 0:
                print(f"    セグメント{i+1}の圧縮エラー")
                continue

            compressed_segments.append(compressed_path)

            # 進捗表示
            if (i + 1) % 10 == 0 or i == len(segments) - 1:
                print(f"    {i+1}/{len(segments)} セグメント圧縮完了")

        if not compressed_segments:
            print("    エラー: 圧縮されたセグメントがありません")
            return False

        # Step 3: 結合
        print("  結合中...")
        concat_list = temp_path / "concat_list.txt"
        with open(concat_list, "w") as f:
            for seg in compressed_segments:
                f.write(f"file '{seg}'\n")

        concat_cmd = [
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output_path),
        ]

        result = subprocess.run(concat_cmd, capture_output=True)
        if result.returncode != 0:
            print(f"    結合エラー: {result.stderr.decode()[:200]}")
            return False

    return True


def format_size(size_bytes: int) -> str:
    """バイト数を人間が読みやすい形式に変換"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="動画ファイルを圧縮してファイルサイズを縮小するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                           # カレントディレクトリの動画を圧縮
  %(prog)s --crf 28                  # CRF値を指定（大きいほど圧縮率高）
  %(prog)s --scale 0.5               # 解像度を50%%に縮小
  %(prog)s -i video.mp4 -o out.mp4   # 入出力ファイルを指定
  %(prog)s --preset slow             # 圧縮速度/品質を指定

CRF値の目安:
  18-23: 高品質（ファイルサイズ大）
  24-28: 標準品質（バランス良好）
  29-35: 低品質（ファイルサイズ小）

preset:
  ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
  （遅いほど圧縮効率が良い）
        """,
    )

    parser.add_argument(
        "-i", "--input",
        nargs="+",
        type=Path,
        default=None,
        help="入力動画ファイル（指定しない場合はカレントディレクトリの動画）",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="出力ディレクトリ（デフォルト: ./comp）",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=28,
        help="CRF値 (0-51, デフォルト: 28)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="解像度のスケール (例: 0.5 で50%%に縮小)",
    )
    parser.add_argument(
        "--preset",
        type=str,
        default="fast",
        choices=["ultrafast", "superfast", "veryfast", "faster", "fast",
                 "medium", "slow", "slower", "veryslow"],
        help="エンコードプリセット（デフォルト: fast）",
    )
    parser.add_argument(
        "--segment-seconds",
        type=int,
        default=5,
        help="分割セグメントの秒数（デフォルト: 5）",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.txt"),
        help="設定ファイルのパス（デフォルト: config.txt）",
    )
    parser.add_argument(
        "--move-original",
        action="store_true",
        help="処理完了後に元ファイルをdoneディレクトリに移動",
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

    # 設定ファイルを読み込み（引数で上書き）
    config = load_config(args.config)
    crf = args.crf if args.crf != 28 else config.get("crf", args.crf)
    scale = args.scale if args.scale else config.get("scale")

    # 入力動画を取得
    if args.input:
        video_files = [p.resolve() for p in args.input if p.exists()]
        if not video_files:
            print("エラー: 指定された動画ファイルが見つかりません")
            sys.exit(1)
    else:
        video_files = get_video_files(Path.cwd())
        if not video_files:
            print("エラー: カレントディレクトリに動画ファイルが見つかりません")
            sys.exit(1)

    # 出力ディレクトリを作成
    output_dir = args.output_dir or Path.cwd() / "comp"
    output_dir.mkdir(parents=True, exist_ok=True)

    # doneディレクトリを作成（必要な場合）
    if args.move_original:
        done_dir = Path.cwd() / "done"
        done_dir.mkdir(parents=True, exist_ok=True)

    print(f"入力動画: {len(video_files)}件")
    print(f"出力先: {output_dir}")
    print(f"設定: CRF={crf}, scale={scale or '元のまま'}, preset={args.preset}")
    print()

    # 処理実行
    success_count = 0
    total_original_size = 0
    total_compressed_size = 0

    for i, input_file in enumerate(video_files):
        print(f"[{i+1}/{len(video_files)}] {input_file.name}")

        original_size = input_file.stat().st_size
        total_original_size += original_size

        # 出力ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"{input_file.stem}_{timestamp}.mp4"

        # 圧縮実行
        success = compress_video(
            ffmpeg_path,
            input_file,
            output_file,
            crf=crf,
            preset=args.preset,
            scale=scale,
            segment_seconds=args.segment_seconds,
        )

        if success and output_file.exists():
            compressed_size = output_file.stat().st_size
            total_compressed_size += compressed_size
            ratio = (1 - compressed_size / original_size) * 100

            print(f"  完了: {format_size(original_size)} → {format_size(compressed_size)} ({ratio:.1f}%削減)")

            # 元ファイルを移動
            if args.move_original:
                shutil.move(str(input_file), str(done_dir / input_file.name))
                print(f"  元ファイルをdoneに移動しました")

            success_count += 1
        else:
            print(f"  失敗")

        print()

    # サマリー
    print("=" * 50)
    print(f"完了: {success_count}/{len(video_files)} ファイル")
    if total_original_size > 0 and total_compressed_size > 0:
        total_ratio = (1 - total_compressed_size / total_original_size) * 100
        print(f"合計: {format_size(total_original_size)} → {format_size(total_compressed_size)} ({total_ratio:.1f}%削減)")


if __name__ == "__main__":
    main()
