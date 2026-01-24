#!/usr/bin/env python3
"""
Video Overlay
動画に画像や別の動画をオーバーレイ（重ねて）合成するツール

Usage:
    python video_overlay.py [OPTIONS] VIDEO OVERLAY
    python video_overlay.py video.mp4 logo.png --position top-right
    python video_overlay.py video.mp4 sub_video.mp4 --position bottom-right --size 30

Requirements:
    pip install moviepy

Original: 右画像貼り付け.ipynb, 右動画貼り付け.ipynb
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    from moviepy.editor import (
        VideoFileClip,
        ImageClip,
        CompositeVideoClip,
        concatenate_videoclips,
    )
except ImportError:
    print("エラー: moviepyがインストールされていません")
    print("インストール: pip install moviepy")
    sys.exit(1)


POSITIONS = {
    "top-left": "tl",
    "top-right": "tr",
    "bottom-left": "bl",
    "bottom-right": "br",
    "center": "center",
}


def get_position_coords(
    position: str,
    main_size: Tuple[int, int],
    overlay_size: Tuple[int, int],
    margin: int = 10,
) -> Tuple[int, int]:
    """位置名から座標を計算"""
    main_w, main_h = main_size
    overlay_w, overlay_h = overlay_size

    positions = {
        "tl": (margin, margin),
        "tr": (main_w - overlay_w - margin, margin),
        "bl": (margin, main_h - overlay_h - margin),
        "br": (main_w - overlay_w - margin, main_h - overlay_h - margin),
        "center": ((main_w - overlay_w) // 2, (main_h - overlay_h) // 2),
    }

    pos_key = POSITIONS.get(position, "tr")
    return positions.get(pos_key, positions["tr"])


def resize_overlay(
    overlay_clip,
    main_size: Tuple[int, int],
    size_percent: float,
) -> any:
    """オーバーレイのサイズを調整（アスペクト比維持）"""
    main_w, main_h = main_size
    overlay_w, overlay_h = overlay_clip.w, overlay_clip.h

    overlay_ratio = overlay_w / overlay_h
    main_ratio = main_w / main_h

    if overlay_ratio > main_ratio:
        new_width = int(main_w * size_percent / 100)
        new_height = int(new_width / overlay_ratio)
    else:
        new_height = int(main_h * size_percent / 100)
        new_width = int(new_height * overlay_ratio)

    return overlay_clip.resize((new_width, new_height))


def is_video_file(path: Path) -> bool:
    """動画ファイルかどうかを判定"""
    video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".webm", ".m4v"}
    return path.suffix.lower() in video_extensions


def is_image_file(path: Path) -> bool:
    """画像ファイルかどうかを判定"""
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tiff"}
    return path.suffix.lower() in image_extensions


def overlay_image_on_video(
    video_path: Path,
    image_path: Path,
    output_path: Path,
    position: str = "top-right",
    size_percent: float = 30,
    margin: int = 10,
    opacity: float = 1.0,
) -> bool:
    """動画に画像をオーバーレイ"""
    try:
        print(f"  動画を読み込み中: {video_path.name}")
        video = VideoFileClip(str(video_path))

        print(f"  画像を読み込み中: {image_path.name}")
        image = ImageClip(str(image_path))

        # 画像のサイズを調整
        image = resize_overlay(image, (video.w, video.h), size_percent)

        # 位置を計算
        x, y = get_position_coords(position, (video.w, video.h), (image.w, image.h), margin)
        image = image.set_position((x, y))

        # 透明度を設定
        if opacity < 1.0:
            image = image.set_opacity(opacity)

        # 動画の長さに合わせる
        image = image.set_duration(video.duration)

        # 合成
        print("  合成中...")
        final = CompositeVideoClip([video, image])

        # 保存
        print(f"  保存中: {output_path.name}")
        final.write_videofile(
            str(output_path),
            fps=video.fps,
            audio_codec="aac",
            preset="medium",
            verbose=False,
            logger=None,
        )

        # クリーンアップ
        video.close()
        final.close()

        return True

    except Exception as e:
        print(f"  エラー: {e}")
        return False


def overlay_video_on_video(
    main_video_path: Path,
    sub_video_path: Path,
    output_path: Path,
    position: str = "top-right",
    size_percent: float = 30,
    margin: int = 10,
    loop_sub: bool = True,
    sub_audio: bool = False,
) -> bool:
    """動画に別の動画をオーバーレイ"""
    try:
        print(f"  メイン動画を読み込み中: {main_video_path.name}")
        main_video = VideoFileClip(str(main_video_path), audio=True)

        print(f"  サブ動画を読み込み中: {sub_video_path.name}")
        sub_video = VideoFileClip(str(sub_video_path), audio=sub_audio)

        # サブ動画のサイズを調整
        sub_video = resize_overlay(sub_video, (main_video.w, main_video.h), size_percent)

        # サブ動画をメイン動画の長さに合わせる
        if loop_sub and sub_video.duration < main_video.duration:
            repeats = int(main_video.duration / sub_video.duration) + 1
            sub_video = concatenate_videoclips([sub_video] * repeats)
        sub_video = sub_video.subclip(0, main_video.duration)

        # 位置を計算
        x, y = get_position_coords(position, (main_video.w, main_video.h), (sub_video.w, sub_video.h), margin)
        sub_video = sub_video.set_position((x, y))

        # 合成
        print("  合成中...")
        final = CompositeVideoClip([main_video, sub_video])

        # 保存
        print(f"  保存中: {output_path.name}")
        final.write_videofile(
            str(output_path),
            fps=main_video.fps,
            audio_codec="aac",
            preset="medium",
            verbose=False,
            logger=None,
        )

        # クリーンアップ
        main_video.close()
        sub_video.close()
        final.close()

        return True

    except Exception as e:
        print(f"  エラー: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="動画に画像や別の動画をオーバーレイ合成するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s video.mp4 logo.png                        # 右上に画像を配置
  %(prog)s video.mp4 logo.png --position top-left    # 左上に配置
  %(prog)s video.mp4 logo.png --size 20              # サイズを20%%に
  %(prog)s video.mp4 sub.mp4 --position bottom-right # 右下に動画を配置
  %(prog)s video.mp4 logo.png --opacity 0.7          # 透明度70%%で配置

位置オプション:
  top-left, top-right (デフォルト), bottom-left, bottom-right, center
        """,
    )

    parser.add_argument(
        "video",
        type=Path,
        help="メインとなる動画ファイル",
    )
    parser.add_argument(
        "overlay",
        type=Path,
        help="オーバーレイする画像または動画ファイル",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="出力ファイル名（デフォルト: {入力}_overlay.mp4）",
    )
    parser.add_argument(
        "-p", "--position",
        type=str,
        default="top-right",
        choices=list(POSITIONS.keys()),
        help="オーバーレイの位置（デフォルト: top-right）",
    )
    parser.add_argument(
        "-s", "--size",
        type=float,
        default=30,
        help="オーバーレイのサイズ（メイン動画に対する%%、デフォルト: 30）",
    )
    parser.add_argument(
        "-m", "--margin",
        type=int,
        default=10,
        help="端からの余白（ピクセル、デフォルト: 10）",
    )
    parser.add_argument(
        "--opacity",
        type=float,
        default=1.0,
        help="透明度（0.0-1.0、画像オーバーレイのみ、デフォルト: 1.0）",
    )
    parser.add_argument(
        "--no-loop",
        action="store_true",
        help="サブ動画をループしない（動画オーバーレイのみ）",
    )
    parser.add_argument(
        "--sub-audio",
        action="store_true",
        help="サブ動画の音声を含める（動画オーバーレイのみ）",
    )

    args = parser.parse_args()

    # 入力ファイルの確認
    if not args.video.exists():
        print(f"エラー: 動画ファイルが見つかりません: {args.video}")
        sys.exit(1)

    if not args.overlay.exists():
        print(f"エラー: オーバーレイファイルが見つかりません: {args.overlay}")
        sys.exit(1)

    if not is_video_file(args.video):
        print(f"エラー: 動画ファイルではありません: {args.video}")
        sys.exit(1)

    # 出力ファイル名
    if args.output:
        output_path = args.output.resolve()
    else:
        output_path = args.video.parent / f"{args.video.stem}_overlay.mp4"

    # 設定を表示
    overlay_type = "画像" if is_image_file(args.overlay) else "動画"
    print(f"メイン動画: {args.video.name}")
    print(f"オーバーレイ: {args.overlay.name} ({overlay_type})")
    print(f"位置: {args.position}")
    print(f"サイズ: {args.size}%")
    print()

    # 処理実行
    if is_image_file(args.overlay):
        success = overlay_image_on_video(
            args.video,
            args.overlay,
            output_path,
            position=args.position,
            size_percent=args.size,
            margin=args.margin,
            opacity=args.opacity,
        )
    elif is_video_file(args.overlay):
        success = overlay_video_on_video(
            args.video,
            args.overlay,
            output_path,
            position=args.position,
            size_percent=args.size,
            margin=args.margin,
            loop_sub=not args.no_loop,
            sub_audio=args.sub_audio,
        )
    else:
        print(f"エラー: サポートされていないファイル形式: {args.overlay}")
        sys.exit(1)

    if success:
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print()
        print("=" * 50)
        print(f"完了: {output_path}")
        print(f"ファイルサイズ: {size_mb:.1f} MB")
    else:
        print()
        print("処理に失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
