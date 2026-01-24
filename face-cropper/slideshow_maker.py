#!/usr/bin/env python3
"""
Slideshow Maker
画像からスライドショー動画を作成するツール（フェードトランジション付き）

Usage:
    python slideshow_maker.py [OPTIONS]
    python slideshow_maker.py -i ./images -o slideshow.mp4
    python slideshow_maker.py --duration 5 --fps 30

Requirements:
    pip install opencv-python numpy

Original: join_v3.py
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

try:
    import cv2
    import numpy as np
except ImportError as e:
    print(f"エラー: 必要なライブラリがインストールされていません: {e}")
    print("インストール: pip install opencv-python numpy")
    sys.exit(1)


def get_image_files(directory: Path) -> List[Path]:
    """ディレクトリから画像ファイルを取得"""
    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
    images = []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            images.append(file)

    return sorted(images)


def resize_and_pad(
    image: np.ndarray,
    target_size: Tuple[int, int],
    background_color: Tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """画像をリサイズしてパディングを追加（アスペクト比維持）"""
    h, w = image.shape[:2]
    target_w, target_h = target_size

    aspect = w / h
    target_aspect = target_w / target_h

    if aspect > target_aspect:
        # 横長: 幅を基準にリサイズ
        new_w = target_w
        new_h = int(new_w / aspect)
    else:
        # 縦長: 高さを基準にリサイズ
        new_h = target_h
        new_w = int(new_h * aspect)

    resized = cv2.resize(image, (new_w, new_h))

    # パディングを計算
    pad_top = (target_h - new_h) // 2
    pad_bottom = target_h - new_h - pad_top
    pad_left = (target_w - new_w) // 2
    pad_right = target_w - new_w - pad_left

    padded = cv2.copyMakeBorder(
        resized,
        pad_top,
        pad_bottom,
        pad_left,
        pad_right,
        cv2.BORDER_CONSTANT,
        value=background_color,
    )

    return padded


def create_slideshow(
    image_files: List[Path],
    output_path: Path,
    fps: int = 30,
    duration: float = 5.0,
    fade_duration: float = 1.0,
    resolution: Tuple[int, int] = (1920, 1080),
    background_color: Tuple[int, int, int] = (0, 0, 0),
) -> bool:
    """スライドショー動画を作成"""
    if not image_files:
        print("エラー: 画像ファイルがありません")
        return False

    # 出力動画を初期化
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, resolution)

    if not writer.isOpened():
        print("エラー: 動画ファイルを作成できません")
        return False

    # フレーム数を計算
    display_frames = int(fps * duration)
    fade_frames = int(fps * fade_duration)

    total_images = len(image_files)

    for i, image_path in enumerate(image_files):
        print(f"[{i+1}/{total_images}] {image_path.name}")

        # 画像を読み込み
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"  警告: 読み込み失敗、スキップします")
            continue

        # リサイズ・パディング
        processed = resize_and_pad(image, resolution, background_color)

        # 表示フレームを書き込み
        for _ in range(display_frames):
            writer.write(processed)

        # フェードトランジション（最後の画像以外）
        if i < total_images - 1:
            # 次の画像を読み込み
            next_image = cv2.imread(str(image_files[i + 1]))
            if next_image is not None:
                next_processed = resize_and_pad(next_image, resolution, background_color)

                # フェード
                for f in range(fade_frames):
                    alpha = 1 - f / fade_frames
                    beta = f / fade_frames
                    faded = cv2.addWeighted(processed, alpha, next_processed, beta, 0)
                    writer.write(faded)

    writer.release()
    return True


def main():
    parser = argparse.ArgumentParser(
        description="画像からスライドショー動画を作成するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                               # カレントディレクトリの画像から動画作成
  %(prog)s -i ./images -o slideshow.mp4  # 入出力を指定
  %(prog)s --duration 5 --fade 1         # 表示5秒、フェード1秒
  %(prog)s --resolution 1920x1080        # 解像度を指定
  %(prog)s --fps 60                      # 60fpsで出力
        """,
    )

    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=Path.cwd(),
        help="入力画像のディレクトリ（デフォルト: カレントディレクトリ）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="出力動画ファイル（デフォルト: slideshow_YYYYMMDD_HHMM.mp4）",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="各画像の表示時間（秒、デフォルト: 5.0）",
    )
    parser.add_argument(
        "--fade",
        type=float,
        default=1.0,
        help="フェードトランジションの時間（秒、デフォルト: 1.0）",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="フレームレート（デフォルト: 30）",
    )
    parser.add_argument(
        "--resolution",
        type=str,
        default="1920x1080",
        help="出力解像度 (WxH形式、デフォルト: 1920x1080)",
    )
    parser.add_argument(
        "--background",
        type=str,
        default="0,0,0",
        help="背景色 (R,G,B形式、デフォルト: 0,0,0 = 黒)",
    )

    args = parser.parse_args()

    # 解像度をパース
    try:
        w, h = args.resolution.lower().split("x")
        resolution = (int(w), int(h))
    except ValueError:
        print("エラー: 解像度は WxH 形式で指定してください（例: 1920x1080）")
        sys.exit(1)

    # 背景色をパース
    try:
        bg_parts = args.background.split(",")
        background_color = tuple(int(x) for x in bg_parts)
    except ValueError:
        print("エラー: 背景色は R,G,B 形式で指定してください（例: 0,0,0）")
        sys.exit(1)

    # ディレクトリを確認
    input_dir = args.input_dir.resolve()
    if not input_dir.exists():
        print(f"エラー: ディレクトリが存在しません: {input_dir}")
        sys.exit(1)

    # 画像ファイルを取得
    image_files = get_image_files(input_dir)
    if not image_files:
        print("エラー: 画像ファイルが見つかりません")
        sys.exit(1)

    # 出力ファイル名
    if args.output:
        output_path = args.output.resolve()
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = Path.cwd() / f"slideshow_{timestamp}.mp4"

    print(f"入力: {input_dir} ({len(image_files)}画像)")
    print(f"出力: {output_path}")
    print(f"設定: {resolution[0]}x{resolution[1]}, {args.fps}fps")
    print(f"      表示{args.duration}秒, フェード{args.fade}秒")
    print()

    # スライドショー作成
    success = create_slideshow(
        image_files,
        output_path,
        fps=args.fps,
        duration=args.duration,
        fade_duration=args.fade,
        resolution=resolution,
        background_color=background_color,
    )

    if success:
        print()
        print("=" * 50)
        print(f"完了: {output_path}")
        # ファイルサイズを表示
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"ファイルサイズ: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
