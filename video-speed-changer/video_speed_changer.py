#!/usr/bin/env python3
"""
Video Speed Changer
動画の再生速度とフレームレートを変更するツール

Usage:
    python video_speed_changer.py [OPTIONS] [INPUT...]
    python video_speed_changer.py video.mp4 --speed 0.5
    python video_speed_changer.py video.mp4 --speed 2.0 --fps 30
    python video_speed_changer.py -i ./videos --speed 0.5 --fps 30

Requirements:
    - ffmpeg

Original: 60fpsを30fpsに変換.ipynb
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


def find_ffprobe() -> Optional[str]:
    """ffprobeのパスを検出"""
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        return ffprobe_path

    common_paths = [
        "/usr/local/bin/ffprobe",
        "/opt/homebrew/bin/ffprobe",
        "/usr/bin/ffprobe",
    ]
    for path in common_paths:
        if os.path.isfile(path):
            return path

    return None


def get_video_info(ffprobe_path: str, video_path: Path) -> dict:
    """動画情報を取得"""
    command = [
        ffprobe_path,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        str(video_path),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        import json

        data = json.loads(result.stdout)

        info = {"fps": None, "has_audio": False}

        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                # FPSを取得
                fps_str = stream.get("r_frame_rate", "0/1")
                if "/" in fps_str:
                    num, den = fps_str.split("/")
                    info["fps"] = float(num) / float(den) if float(den) > 0 else 0
            elif stream.get("codec_type") == "audio":
                info["has_audio"] = True

        return info
    except Exception:
        return {"fps": None, "has_audio": False}


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


def change_video_speed(
    ffmpeg_path: str,
    input_file: Path,
    output_file: Path,
    speed: float,
    output_fps: Optional[int],
    audio_mode: str = "adjust",
) -> bool:
    """動画の速度を変更"""
    # PTS（Presentation Time Stamp）の倍率を計算
    # speed=0.5 (スロー) → pts_multiplier=2.0 (時間を2倍に引き伸ばす)
    # speed=2.0 (高速) → pts_multiplier=0.5 (時間を半分に圧縮)
    pts_multiplier = 1.0 / speed

    # ビデオフィルターを構築
    video_filter = f"setpts={pts_multiplier}*PTS"
    if output_fps:
        video_filter += f",fps=fps={output_fps}"

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_file),
    ]

    if audio_mode == "remove":
        # 音声を削除
        command.extend(
            [
                "-filter:v",
                video_filter,
                "-an",
            ]
        )
    elif audio_mode == "adjust":
        # 音声も速度を調整
        # atempo は 0.5〜2.0 の範囲のみサポート
        # 範囲外の場合は複数回適用が必要
        audio_filter = build_atempo_filter(speed)
        command.extend(
            [
                "-filter_complex",
                f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
                "-map",
                "[v]",
                "-map",
                "[a]",
            ]
        )
    else:  # copy
        # 音声はそのままコピー（動画と同期しなくなる可能性あり）
        command.extend(
            [
                "-filter:v",
                video_filter,
                "-c:a",
                "copy",
            ]
        )

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
        # 音声がない場合のフォールバック
        if "does not contain any stream" in (e.stderr or ""):
            # 音声なしで再試行
            command_no_audio = [
                ffmpeg_path,
                "-y",
                "-i",
                str(input_file),
                "-filter:v",
                video_filter,
                "-an",
                str(output_file),
            ]
            try:
                subprocess.run(command_no_audio, check=True, capture_output=True)
                return True
            except subprocess.CalledProcessError:
                pass

        print(f"  エラー: {e.stderr[:300] if e.stderr else str(e)}")
        return False


def build_atempo_filter(speed: float) -> str:
    """atempoフィルターを構築（0.5〜2.0の範囲制限に対応）"""
    filters = []

    # atempoは0.5〜2.0の範囲のみサポート
    remaining_speed = speed

    while remaining_speed < 0.5:
        filters.append("atempo=0.5")
        remaining_speed /= 0.5

    while remaining_speed > 2.0:
        filters.append("atempo=2.0")
        remaining_speed /= 2.0

    if 0.5 <= remaining_speed <= 2.0:
        filters.append(f"atempo={remaining_speed}")

    return ",".join(filters) if filters else "atempo=1.0"


def main():
    parser = argparse.ArgumentParser(
        description="動画の再生速度とフレームレートを変更するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s video.mp4 --speed 0.5              # 0.5倍速（スローモーション）
  %(prog)s video.mp4 --speed 2.0              # 2倍速
  %(prog)s video.mp4 --speed 0.5 --fps 30     # 0.5倍速 + 30fps出力
  %(prog)s -i ./videos --speed 0.5            # ディレクトリ内の全動画を処理
  %(prog)s video.mp4 --speed 0.5 --no-audio   # 音声を削除

速度について:
  0.5 = 0.5倍速（スローモーション、再生時間2倍）
  1.0 = 等速（変更なし）
  2.0 = 2倍速（再生時間半分）

音声処理:
  --audio adjust (デフォルト): 音声も速度を調整
  --audio remove: 音声を削除
  --audio copy: 音声をそのままコピー（同期がずれる可能性）
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
        help="出力ディレクトリ（デフォルト: ./output）",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.5,
        help="再生速度の倍率（デフォルト: 0.5）",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=None,
        help="出力フレームレート（指定しない場合は元のまま）",
    )
    parser.add_argument(
        "--audio",
        type=str,
        choices=["adjust", "remove", "copy"],
        default="adjust",
        help="音声処理モード（デフォルト: adjust）",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="音声を削除（--audio remove と同じ）",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default=None,
        help="出力ファイル名のサフィックス（デフォルト: 自動生成）",
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
        sys.exit(1)

    ffprobe_path = find_ffprobe()

    # 音声モード
    audio_mode = "remove" if args.no_audio else args.audio

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
    output_dir = (args.output_dir or Path("./output")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # サフィックスを決定
    if args.suffix:
        suffix = args.suffix
    else:
        fps_str = f"_{args.fps}fps" if args.fps else ""
        suffix = f"_{args.speed}x{fps_str}"

    # 設定を表示
    print(f"ffmpeg: {ffmpeg_path}")
    print(f"速度: {args.speed}x")
    if args.fps:
        print(f"出力FPS: {args.fps}")
    print(f"音声: {audio_mode}")
    print(f"対象: {len(video_files)}ファイル")
    print(f"出力先: {output_dir}")
    print()

    # 処理実行
    success_count = 0
    fail_count = 0

    for i, video_file in enumerate(video_files):
        print(f"[{i+1}/{len(video_files)}] {video_file.name}")

        # 元の動画情報を取得
        if ffprobe_path:
            info = get_video_info(ffprobe_path, video_file)
            if info["fps"]:
                print(f"  元FPS: {info['fps']:.2f}")

        # 出力ファイル名
        output_file = output_dir / f"{video_file.stem}{suffix}{video_file.suffix}"

        if change_video_speed(
            ffmpeg_path,
            video_file,
            output_file,
            args.speed,
            args.fps,
            audio_mode,
        ):
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"  → {output_file.name} ({size_mb:.1f} MB)")
            success_count += 1
        else:
            fail_count += 1

    # 結果表示
    print()
    print("=" * 50)
    print(f"完了: {success_count}ファイルを変換")
    if fail_count > 0:
        print(f"失敗: {fail_count}ファイル")


if __name__ == "__main__":
    main()
