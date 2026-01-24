#!/usr/bin/env python3
"""
Face Cropper
画像から顔を検出して切り出し、正方形にリサイズするツール

Usage:
    python face_cropper.py [OPTIONS]
    python face_cropper.py --size 1080
    python face_cropper.py -i ./images -o ./faces --margin 0.5

Requirements:
    pip install opencv-python dlib numpy

Note:
    dlibの顔検出モデルを使用します。
    初回実行時にモデルのダウンロードが必要な場合があります。

Original: face_cut_v3.py
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import cv2
    import dlib
    import numpy as np
except ImportError as e:
    print(f"エラー: 必要なライブラリがインストールされていません: {e}")
    print("インストール: pip install opencv-python dlib numpy")
    sys.exit(1)


def get_image_files(directory: Path) -> List[Path]:
    """ディレクトリから画像ファイルを取得"""
    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
    images = []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            images.append(file)

    return sorted(images)


def crop_face(
    image: np.ndarray,
    face: dlib.rectangle,
    margin_ratio: float = 0.5,
) -> np.ndarray:
    """顔領域を切り出す"""
    x, y = face.left(), face.top()
    w, h = face.width(), face.height()

    # マージンを計算
    margin_w = int(w * margin_ratio)
    margin_h = int(h * margin_ratio)

    # マージンを追加した矩形を計算（画像境界内に収める）
    new_x = max(x - margin_w, 0)
    new_y = max(y - margin_h, 0)
    new_w = min(w + 2 * margin_w, image.shape[1] - new_x)
    new_h = min(h + 2 * margin_h, image.shape[0] - new_y)

    return image[new_y : new_y + new_h, new_x : new_x + new_w]


def resize_to_square(
    image: np.ndarray,
    size: int,
    background_color: Tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """画像を正方形にリサイズ（アスペクト比維持、パディング追加）"""
    h, w = image.shape[:2]
    aspect_ratio = w / h

    # 出力画像を作成（背景色で初期化）
    output = np.full((size, size, 3), background_color, dtype=np.uint8)

    if aspect_ratio > 1:
        # 横長
        new_width = size
        new_height = int(size / aspect_ratio)
        resized = cv2.resize(image, (new_width, new_height))
        y_offset = (size - new_height) // 2
        output[y_offset : y_offset + new_height, :] = resized
    else:
        # 縦長または正方形
        new_height = size
        new_width = int(size * aspect_ratio)
        resized = cv2.resize(image, (new_width, new_height))
        x_offset = (size - new_width) // 2
        output[:, x_offset : x_offset + new_width] = resized

    return output


def process_images(
    detector: dlib.fhog_object_detector,
    input_dir: Path,
    output_dir: Path,
    done_dir: Path,
    size: int = 1080,
    margin: float = 0.5,
    background_color: Tuple[int, int, int] = (0, 0, 0),
    move_original: bool = True,
    prefix: str = "face_",
) -> Tuple[int, int, int]:
    """画像を処理して顔を切り出す"""
    output_dir.mkdir(parents=True, exist_ok=True)
    if move_original:
        done_dir.mkdir(parents=True, exist_ok=True)

    image_files = get_image_files(input_dir)
    total_images = len(image_files)
    total_faces = 0
    failed_count = 0

    for i, image_path in enumerate(image_files):
        print(f"[{i+1}/{total_images}] {image_path.name}", end=" ")

        try:
            image = cv2.imread(str(image_path))
            if image is None:
                print("- 読み込み失敗")
                failed_count += 1
                continue

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 顔を検出
            faces = detector(gray)

            if len(faces) == 0:
                print("- 顔が見つかりません")
                continue

            print(f"- {len(faces)}個の顔を検出")

            # 各顔を処理
            for face_idx, face in enumerate(faces):
                # 顔を切り出し
                cropped = crop_face(image, face, margin)

                # 正方形にリサイズ
                output_image = resize_to_square(cropped, size, background_color)

                # ファイル名を生成
                if len(faces) == 1:
                    output_name = f"{prefix}{image_path.stem}{image_path.suffix}"
                else:
                    output_name = f"{prefix}{image_path.stem}_{face_idx+1}{image_path.suffix}"

                output_path = output_dir / output_name
                cv2.imwrite(str(output_path), output_image)
                total_faces += 1

            # 元ファイルを移動
            if move_original:
                shutil.move(str(image_path), str(done_dir / image_path.name))

        except Exception as e:
            print(f"- エラー: {e}")
            failed_count += 1

    return total_images, total_faces, failed_count


def main():
    parser = argparse.ArgumentParser(
        description="画像から顔を検出して切り出し、正方形にリサイズするツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                           # カレントディレクトリの画像を処理
  %(prog)s --size 1080               # 1080x1080で出力
  %(prog)s --margin 0.5              # 顔の周囲に50%%のマージンを追加
  %(prog)s -i ./images -o ./faces    # 入出力ディレクトリを指定
  %(prog)s --no-move                 # 元ファイルを移動しない

マージンについて:
  マージンは顔のサイズに対する割合で指定します。
  0.5 = 顔の高さ/幅の50%を周囲に追加（デフォルト）
  1.0 = 顔の高さ/幅と同じ分を周囲に追加
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
        "--output-dir",
        type=Path,
        default=None,
        help="出力ディレクトリ（デフォルト: ./comp）",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=1080,
        help="出力画像のサイズ（正方形、デフォルト: 1080）",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.5,
        help="顔の周囲に追加するマージンの割合（デフォルト: 0.5）",
    )
    parser.add_argument(
        "--background",
        type=str,
        default="0,0,0",
        help="背景色 (R,G,B形式、デフォルト: 0,0,0 = 黒)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="face_",
        help="出力ファイル名のプレフィックス（デフォルト: face_）",
    )
    parser.add_argument(
        "--no-move",
        action="store_true",
        help="処理後に元ファイルを移動しない",
    )

    args = parser.parse_args()

    # 背景色をパース
    try:
        bg_parts = args.background.split(",")
        background_color = tuple(int(x) for x in bg_parts)
    except ValueError:
        print("エラー: 背景色は R,G,B 形式で指定してください（例: 0,0,0）")
        sys.exit(1)

    # ディレクトリを設定
    input_dir = args.input_dir.resolve()
    output_dir = (args.output_dir or input_dir / "comp").resolve()
    done_dir = input_dir / "done"

    if not input_dir.exists():
        print(f"エラー: ディレクトリが存在しません: {input_dir}")
        sys.exit(1)

    # 顔検出器を初期化
    print("顔検出器を初期化中...")
    try:
        detector = dlib.get_frontal_face_detector()
    except Exception as e:
        print(f"エラー: 顔検出器の初期化に失敗しました: {e}")
        sys.exit(1)

    print(f"入力: {input_dir}")
    print(f"出力: {output_dir}")
    print(f"サイズ: {args.size}x{args.size}")
    print(f"マージン: {args.margin}")
    print()

    # 処理実行
    total, faces, failed = process_images(
        detector,
        input_dir,
        output_dir,
        done_dir,
        size=args.size,
        margin=args.margin,
        background_color=background_color,
        move_original=not args.no_move,
        prefix=args.prefix,
    )

    print()
    print("=" * 50)
    print(f"完了: {total}画像から{faces}個の顔を切り出しました")
    if failed > 0:
        print(f"失敗: {failed}ファイル")


if __name__ == "__main__":
    main()
