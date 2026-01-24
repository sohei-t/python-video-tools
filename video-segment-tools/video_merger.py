#!/usr/bin/env python3
"""
Video Merger
複数の動画ファイルを結合するツール

Usage:
    python video_merger.py [OPTIONS]
    python video_merger.py -i ./segments -o output.mp4
    python video_merger.py -i ./folder   # フォルダ内のcompディレクトリを自動検索

Original: 複数ファイル繋ぎあわせ_v4_0505.py (v4 05/05)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple


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


def get_video_files(directory: Path, pattern: str = "*.mp4") -> List[Path]:
    """ディレクトリから動画ファイルを取得（ソート済み）"""
    files = list(directory.glob(pattern))
    return sorted(files)


def get_common_prefix(files: List[Path]) -> str:
    """ファイル名の共通プレフィックスを取得"""
    if not files:
        return "merged"

    names = [f.stem for f in files]
    prefix = os.path.commonprefix(names)

    # 末尾のアンダースコアと数字を除去
    if prefix.endswith("_"):
        prefix = prefix[:-1]
    while prefix and prefix[-1].isdigit():
        prefix = prefix[:-1]
    if prefix.endswith("_"):
        prefix = prefix[:-1]

    return prefix if prefix else "merged"


def merge_videos_concat_demuxer(
    ffmpeg_path: str,
    video_files: List[Path],
    output_file: Path,
) -> bool:
    """concat demuxerを使用して動画を結合（高速、同一形式のみ）"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as list_file:
        for video in video_files:
            # シングルクォートをエスケープ
            escaped_path = str(video.absolute()).replace("'", "'\\''")
            list_file.write(f"file '{escaped_path}'\n")
        list_file_path = list_file.name

    try:
        cmd = [
            ffmpeg_path,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file_path,
            "-c",
            "copy",
            str(output_file),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    finally:
        os.unlink(list_file_path)


def merge_videos_filter_complex(
    ffmpeg_path: str,
    video_files: List[Path],
    output_file: Path,
    include_audio: bool = True,
) -> bool:
    """filter_complexを使用して動画を結合（異なる形式対応、低速）"""
    n = len(video_files)

    # 入力ファイルの引数を構築
    input_args = []
    for video in video_files:
        input_args.extend(["-i", str(video)])

    # フィルタを構築
    if include_audio:
        filter_parts = []
        for i in range(n):
            filter_parts.append(f"[{i}:v]")
            filter_parts.append(f"[{i}:a]")
        filter_str = "".join(filter_parts) + f"concat=n={n}:v=1:a=1[v][a]"
        output_args = ["-map", "[v]", "-map", "[a]"]
    else:
        filter_parts = [f"[{i}:v]" for i in range(n)]
        filter_str = "".join(filter_parts) + f"concat=n={n}:v=1[v]"
        output_args = ["-map", "[v]"]

    cmd = [
        ffmpeg_path,
        "-y",
        *input_args,
        "-filter_complex",
        filter_str,
        *output_args,
        str(output_file),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def merge_videos(
    ffmpeg_path: str,
    video_files: List[Path],
    output_file: Path,
    method: str = "auto",
    include_audio: bool = True,
) -> Tuple[bool, str]:
    """動画を結合"""
    if len(video_files) == 0:
        return False, "結合する動画ファイルがありません"

    if len(video_files) == 1:
        # 1ファイルの場合はコピー
        shutil.copy2(video_files[0], output_file)
        return True, "コピー完了"

    if method == "auto" or method == "fast":
        # まずconcat demuxerを試行
        print("  高速モードで結合中...")
        if merge_videos_concat_demuxer(ffmpeg_path, video_files, output_file):
            return True, "高速モードで結合完了"

        if method == "fast":
            return False, "高速モードでの結合に失敗"

        print("  高速モード失敗、再エンコードモードで再試行...")

    # filter_complexで結合
    print("  再エンコードモードで結合中...")
    if merge_videos_filter_complex(ffmpeg_path, video_files, output_file, include_audio):
        return True, "再エンコードモードで結合完了"

    return False, "結合に失敗しました"


def process_directory(
    ffmpeg_path: str,
    directory: Path,
    output_dir: Optional[Path],
    method: str,
    include_audio: bool,
    comp_subdir: bool,
) -> Tuple[int, int]:
    """ディレクトリを処理"""
    success_count = 0
    error_count = 0

    if comp_subdir:
        # サブディレクトリのcompフォルダを検索
        for entry in directory.iterdir():
            if entry.is_dir():
                comp_dir = entry / "comp"
                if comp_dir.exists() and comp_dir.is_dir():
                    video_files = get_video_files(comp_dir)
                    if video_files:
                        prefix = get_common_prefix(video_files)
                        out_dir = output_dir or entry
                        output_file = out_dir / f"{prefix}_merged.mp4"

                        if output_file.exists():
                            print(f"スキップ: {output_file.name} (既存)")
                            continue

                        print(f"\n処理中: {entry.name}/comp ({len(video_files)}ファイル)")

                        success, message = merge_videos(
                            ffmpeg_path,
                            video_files,
                            output_file,
                            method,
                            include_audio,
                        )

                        if success:
                            print(f"  完了: {output_file.name}")
                            success_count += 1
                        else:
                            print(f"  エラー: {message}")
                            error_count += 1
    else:
        # 直接ディレクトリの動画を結合
        video_files = get_video_files(directory)
        if video_files:
            prefix = get_common_prefix(video_files)
            out_dir = output_dir or directory
            output_file = out_dir / f"{prefix}_merged.mp4"

            if output_file.exists():
                print(f"スキップ: {output_file.name} (既存)")
                return 0, 0

            print(f"\n処理中: {directory.name} ({len(video_files)}ファイル)")

            success, message = merge_videos(
                ffmpeg_path,
                video_files,
                output_file,
                method,
                include_audio,
            )

            if success:
                print(f"  完了: {output_file.name}")
                success_count = 1
            else:
                print(f"  エラー: {message}")
                error_count = 1

    return success_count, error_count


def main():
    parser = argparse.ArgumentParser(
        description="複数の動画ファイルを結合するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s -i ./segments              # segmentsディレクトリの動画を結合
  %(prog)s -i ./segments -o out.mp4   # 出力ファイル名を指定
  %(prog)s --comp-subdir              # 各サブディレクトリのcompフォルダを検索
  %(prog)s --no-audio                 # 音声なしで結合
  %(prog)s --method slow              # 再エンコードモード（異なる形式対応）

結合モード:
  fast  - 再エンコードなし（高速、同一形式のみ）
  slow  - 再エンコードあり（低速、異なる形式対応）
  auto  - fastを試行し、失敗したらslowにフォールバック
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path.cwd(),
        help="入力ディレクトリ (デフォルト: カレントディレクトリ)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="出力ファイルまたはディレクトリ",
    )
    parser.add_argument(
        "--method",
        choices=["auto", "fast", "slow"],
        default="auto",
        help="結合方法 (デフォルト: auto)",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="音声を含めない",
    )
    parser.add_argument(
        "--comp-subdir",
        action="store_true",
        help="各サブディレクトリのcompフォルダを検索",
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

    input_path = args.input.resolve()
    if not input_path.exists():
        print(f"エラー: パスが存在しません: {input_path}")
        sys.exit(1)

    # 出力先を決定
    output_path = args.output
    if output_path and output_path.suffix:
        # ファイル名が指定された場合
        output_dir = output_path.parent
        os.makedirs(output_dir, exist_ok=True)

        video_files = get_video_files(input_path)
        if not video_files:
            print("エラー: 動画ファイルが見つかりませんでした")
            sys.exit(1)

        print(f"対象動画: {len(video_files)}件")
        success, message = merge_videos(
            ffmpeg_path,
            video_files,
            output_path,
            args.method,
            not args.no_audio,
        )

        if success:
            print(f"\n完了: {output_path}")
        else:
            print(f"\nエラー: {message}")
            sys.exit(1)
    else:
        # ディレクトリモード
        output_dir = output_path.resolve() if output_path else None

        success, errors = process_directory(
            ffmpeg_path,
            input_path,
            output_dir,
            args.method,
            not args.no_audio,
            args.comp_subdir,
        )

        print(f"\n完了: 成功={success}, エラー={errors}")


if __name__ == "__main__":
    main()
