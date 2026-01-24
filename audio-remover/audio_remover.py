#!/usr/bin/env python3
"""
Audio Remover
動画ファイルから音声トラックを除去するツール

Usage:
    python audio_remover.py [OPTIONS] [INPUT...]
    python audio_remover.py video.mp4
    python audio_remover.py -i ./videos -o ./muted
    python audio_remover.py --suffix _muted video.mp4

Requirements:
    - ffmpeg

Original: mp4から音声消去.py, 動画から音声消去.py
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
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

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

    videos = []
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            videos.append(file)

    return sorted(videos)


def remove_audio(
    ffmpeg_path: str,
    input_file: Path,
    output_file: Path,
) -> bool:
    """動画から音声を除去"""
    command = [
        ffmpeg_path,
        "-y",
        "-i", str(input_file),
        "-an",  # 音声トラックを除去
        "-c:v", "copy",  # 映像は再エンコードせずコピー
        str(output_file),
    ]

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


def get_output_path(
    input_file: Path,
    output_dir: Optional[Path],
    prefix: str,
    suffix: str,
) -> Path:
    """出力ファイルパスを生成"""
    new_name = f"{prefix}{input_file.stem}{suffix}{input_file.suffix}"

    if output_dir:
        return output_dir / new_name
    else:
        return input_file.parent / new_name


def main():
    parser = argparse.ArgumentParser(
        description="動画ファイルから音声トラックを除去するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s video.mp4                    # 単一ファイルから音声除去
  %(prog)s *.mp4                        # 複数ファイルを処理
  %(prog)s -i ./videos                  # ディレクトリ内の全動画を処理
  %(prog)s -o ./muted video.mp4         # 出力先を指定
  %(prog)s --suffix _muted video.mp4    # video_muted.mp4として出力
  %(prog)s --prefix muted_ video.mp4    # muted_video.mp4として出力

出力ファイル名:
  デフォルトでは「_noaudio」サフィックスが追加されます
  例: video.mp4 → video_noaudio.mp4
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
        help="入力ディレクトリ",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="出力ディレクトリ（デフォルト: 入力と同じ場所）",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="出力ファイル名のプレフィックス",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="_noaudio",
        help="出力ファイル名のサフィックス（デフォルト: _noaudio）",
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
        video_files = get_video_files(Path.cwd())

    if not video_files:
        print("エラー: 動画ファイルが見つかりません")
        sys.exit(1)

    # 出力ディレクトリを設定
    output_dir = None
    if args.output_dir:
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    # 設定を表示
    print(f"ffmpeg: {ffmpeg_path}")
    print(f"対象: {len(video_files)}ファイル")
    if output_dir:
        print(f"出力先: {output_dir}")
    print()

    # 処理実行
    success_count = 0
    fail_count = 0

    for i, video_file in enumerate(video_files):
        print(f"[{i+1}/{len(video_files)}] {video_file.name}")

        output_file = get_output_path(
            video_file,
            output_dir,
            args.prefix,
            args.suffix,
        )

        # 入力と出力が同じ場合はスキップ
        if output_file.resolve() == video_file.resolve():
            print("  エラー: 入力と出力が同じファイルです。--suffix または --prefix を指定してください")
            fail_count += 1
            continue

        if remove_audio(ffmpeg_path, video_file, output_file):
            # ファイルサイズを表示
            input_size = video_file.stat().st_size / (1024 * 1024)
            output_size = output_file.stat().st_size / (1024 * 1024)
            reduction = (1 - output_size / input_size) * 100 if input_size > 0 else 0

            print(f"  → {output_file.name}")
            print(f"     {input_size:.1f}MB → {output_size:.1f}MB ({reduction:.1f}%削減)")
            success_count += 1
        else:
            fail_count += 1

    # 結果表示
    print()
    print("=" * 50)
    print(f"完了: {success_count}ファイルから音声を除去")
    if fail_count > 0:
        print(f"失敗: {fail_count}ファイル")


if __name__ == "__main__":
    main()
