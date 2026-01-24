#!/usr/bin/env python3
"""
Audio Extractor
動画ファイルから音声を抽出してMP3に変換するツール

Usage:
    python audio_extractor.py [OPTIONS] [INPUT...]
    python audio_extractor.py video.mp4
    python audio_extractor.py -i ./videos -o ./audio
    python audio_extractor.py --bitrate 320 video.mp4

Requirements:
    - ffmpeg

Original: 動画からmp3抽出.py
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def find_ffmpeg() -> Optional[str]:
    """ffmpegのパスを検出"""
    # 環境のPATHから検索
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # よくあるインストール場所を確認
    common_paths = [
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]
    for path in common_paths:
        if os.path.isfile(path):
            return path

    return None


def get_video_files(path: Path) -> List[Path]:
    """指定パスから動画ファイルを取得"""
    extensions = {".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".webm", ".m4v"}

    if path.is_file():
        if path.suffix.lower() in extensions:
            return [path]
        return []

    # ディレクトリの場合
    videos = []
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            videos.append(file)

    return sorted(videos)


def extract_audio(
    ffmpeg_path: str,
    input_file: Path,
    output_file: Path,
    bitrate: Optional[int] = None,
    quality: int = 2,
) -> bool:
    """動画から音声を抽出"""
    command = [
        ffmpeg_path,
        "-y",
        "-i", str(input_file),
        "-vn",
        "-acodec", "libmp3lame",
    ]

    if bitrate:
        # ビットレート指定（CBR）
        command.extend(["-b:a", f"{bitrate}k"])
    else:
        # 品質指定（VBR）: 0が最高、9が最低
        command.extend(["-q:a", str(quality)])

    command.append(str(output_file))

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  エラー: {e.stderr[:200] if e.stderr else str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="動画ファイルから音声を抽出してMP3に変換するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s video.mp4                    # 単一ファイルを変換
  %(prog)s *.mp4                        # 複数ファイルを変換
  %(prog)s -i ./videos                  # ディレクトリ内の全動画を変換
  %(prog)s -o ./audio video.mp4         # 出力先を指定
  %(prog)s --bitrate 320 video.mp4      # 320kbpsで出力
  %(prog)s --quality 0 video.mp4        # 最高品質（VBR）で出力

品質について:
  --bitrate: CBRモード（固定ビットレート）128, 192, 256, 320など
  --quality: VBRモード（可変ビットレート）0が最高、9が最低（デフォルト: 2）
        """,
    )

    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="入力ファイルまたはディレクトリ",
    )
    parser.add_argument(
        "-i", "--input-dir",
        type=Path,
        default=None,
        help="入力ディレクトリ（位置引数がない場合に使用）",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="出力ディレクトリ（デフォルト: 入力と同じ場所）",
    )
    parser.add_argument(
        "--bitrate",
        type=int,
        default=None,
        help="出力ビットレート（kbps）: 128, 192, 256, 320など",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=2,
        choices=range(0, 10),
        metavar="0-9",
        help="VBR品質（0=最高、9=最低、デフォルト: 2）",
    )
    parser.add_argument(
        "--ffmpeg",
        type=str,
        default=None,
        help="ffmpegのパス（自動検出されない場合に指定）",
    )

    args = parser.parse_args()

    # ffmpegを検出
    ffmpeg_path = args.ffmpeg or find_ffmpeg()
    if not ffmpeg_path:
        print("エラー: ffmpegが見つかりません")
        print("インストール: brew install ffmpeg (macOS)")
        print("または --ffmpeg オプションでパスを指定してください")
        sys.exit(1)

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
        # カレントディレクトリから検索
        video_files = get_video_files(Path.cwd())

    if not video_files:
        print("エラー: 動画ファイルが見つかりません")
        sys.exit(1)

    # 出力ディレクトリを設定
    output_dir = args.output_dir
    if output_dir:
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    # 設定を表示
    print(f"ffmpeg: {ffmpeg_path}")
    if args.bitrate:
        print(f"ビットレート: {args.bitrate}kbps (CBR)")
    else:
        print(f"品質: {args.quality} (VBR)")
    print(f"対象: {len(video_files)}ファイル")
    print()

    # 処理実行
    success_count = 0
    fail_count = 0

    for i, video_file in enumerate(video_files):
        print(f"[{i+1}/{len(video_files)}] {video_file.name}")

        # 出力ファイル名を決定
        if output_dir:
            output_file = output_dir / f"{video_file.stem}.mp3"
        else:
            output_file = video_file.with_suffix(".mp3")

        # 音声抽出
        if extract_audio(ffmpeg_path, video_file, output_file, args.bitrate, args.quality):
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"  → {output_file.name} ({size_mb:.1f} MB)")
            success_count += 1
        else:
            fail_count += 1

    # 結果表示
    print()
    print("=" * 50)
    print(f"完了: {success_count}ファイル変換")
    if fail_count > 0:
        print(f"失敗: {fail_count}ファイル")


if __name__ == "__main__":
    main()
