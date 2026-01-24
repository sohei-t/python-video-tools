#!/usr/bin/env python3
"""
Image Combiner
複数の画像を横並び・縦並びで1枚に結合するツール

Usage:
    python image_combiner.py [OPTIONS] [IMAGES...]
    python image_combiner.py image1.jpg image2.jpg
    python image_combiner.py --vertical image1.jpg image2.jpg
    python image_combiner.py -i ./images -o combined.jpg

Requirements:
    pip install Pillow

Original: 合体画像作成.py
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from PIL import Image
except ImportError:
    print("エラー: Pillowがインストールされていません")
    print("インストール: pip install Pillow")
    sys.exit(1)


def get_image_files(path: Path) -> List[Path]:
    """指定パスから画像ファイルを取得"""
    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".tiff"}

    if path.is_file():
        if path.suffix.lower() in extensions:
            return [path]
        return []

    images = []
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            images.append(file)

    return sorted(images)


def parse_color(color_str: str) -> Tuple[int, int, int]:
    """色文字列をRGBタプルに変換"""
    parts = color_str.split(",")
    return tuple(int(x.strip()) for x in parts)


def combine_images_horizontal(
    images: List[Image.Image],
    gap: int = 0,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    align: str = "center",
) -> Image.Image:
    """画像を横並びで結合"""
    if not images:
        raise ValueError("画像がありません")

    # 最大の高さを取得
    max_height = max(img.height for img in images)

    # 各画像をアスペクト比を維持してリサイズ
    resized_images = []
    for img in images:
        if img.height != max_height:
            ratio = max_height / img.height
            new_width = int(img.width * ratio)
            img = img.resize((new_width, max_height), Image.LANCZOS)
        resized_images.append(img)

    # 合計幅を計算
    total_width = sum(img.width for img in resized_images) + gap * (len(resized_images) - 1)

    # 新しい画像を作成
    combined = Image.new("RGB", (total_width, max_height), background_color)

    # 画像を配置
    x_offset = 0
    for img in resized_images:
        # RGBAの場合はRGBに変換
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, background_color)
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        combined.paste(img, (x_offset, 0))
        x_offset += img.width + gap

    return combined


def combine_images_vertical(
    images: List[Image.Image],
    gap: int = 0,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    align: str = "center",
) -> Image.Image:
    """画像を縦並びで結合"""
    if not images:
        raise ValueError("画像がありません")

    # 最大の幅を取得
    max_width = max(img.width for img in images)

    # 各画像をアスペクト比を維持してリサイズ
    resized_images = []
    for img in images:
        if img.width != max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        resized_images.append(img)

    # 合計高さを計算
    total_height = sum(img.height for img in resized_images) + gap * (len(resized_images) - 1)

    # 新しい画像を作成
    combined = Image.new("RGB", (max_width, total_height), background_color)

    # 画像を配置
    y_offset = 0
    for img in resized_images:
        # RGBAの場合はRGBに変換
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, background_color)
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # 水平方向の配置
        if align == "left":
            x_offset = 0
        elif align == "right":
            x_offset = max_width - img.width
        else:  # center
            x_offset = (max_width - img.width) // 2

        combined.paste(img, (x_offset, y_offset))
        y_offset += img.height + gap

    return combined


def main():
    parser = argparse.ArgumentParser(
        description="複数の画像を横並び・縦並びで1枚に結合するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s image1.jpg image2.jpg              # 2枚を横並びで結合
  %(prog)s *.jpg                              # 全てのJPGを横並びで結合
  %(prog)s --vertical image1.jpg image2.jpg   # 縦並びで結合
  %(prog)s -i ./images -o combined.jpg        # ディレクトリ内の画像を結合
  %(prog)s --gap 10 image1.jpg image2.jpg     # 10px間隔で結合
  %(prog)s --background 0,0,0 *.png           # 黒背景で結合

出力ファイル:
  デフォルトでは combined_画像名.jpg として保存されます
        """,
    )

    parser.add_argument(
        "images",
        nargs="*",
        type=Path,
        help="結合する画像ファイル",
    )
    parser.add_argument(
        "-i", "--input-dir",
        type=Path,
        default=None,
        help="入力ディレクトリ（画像を自動収集）",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="出力ファイル名（デフォルト: combined_image.jpg）",
    )
    parser.add_argument(
        "-v", "--vertical",
        action="store_true",
        help="縦並びで結合（デフォルト: 横並び）",
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=0,
        help="画像間のギャップ（ピクセル、デフォルト: 0）",
    )
    parser.add_argument(
        "--background",
        type=str,
        default="255,255,255",
        help="背景色 (R,G,B形式、デフォルト: 255,255,255 = 白)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="JPEG品質（1-100、デフォルト: 95）",
    )

    args = parser.parse_args()

    # 背景色をパース
    try:
        background_color = parse_color(args.background)
    except ValueError:
        print("エラー: 背景色は R,G,B 形式で指定してください（例: 255,255,255）")
        sys.exit(1)

    # 画像ファイルを収集
    image_files = []

    if args.images:
        for img_path in args.images:
            if not img_path.exists():
                print(f"警告: ファイルが見つかりません: {img_path}")
                continue
            image_files.extend(get_image_files(img_path))
    elif args.input_dir:
        if not args.input_dir.exists():
            print(f"エラー: ディレクトリが存在しません: {args.input_dir}")
            sys.exit(1)
        image_files = get_image_files(args.input_dir)
    else:
        image_files = get_image_files(Path.cwd())

    if len(image_files) < 2:
        print("エラー: 少なくとも2枚の画像が必要です")
        sys.exit(1)

    # 出力ファイル名
    if args.output:
        output_path = args.output.resolve()
    else:
        output_path = Path.cwd() / "combined_image.jpg"

    # 設定を表示
    direction = "縦並び" if args.vertical else "横並び"
    print(f"結合方向: {direction}")
    print(f"画像数: {len(image_files)}枚")
    if args.gap > 0:
        print(f"ギャップ: {args.gap}px")
    print()

    # 画像を読み込み
    print("画像を読み込み中...")
    images = []
    for i, img_path in enumerate(image_files):
        print(f"  [{i+1}/{len(image_files)}] {img_path.name}")
        try:
            img = Image.open(img_path)
            images.append(img)
        except Exception as e:
            print(f"    警告: 読み込み失敗: {e}")

    if len(images) < 2:
        print("エラー: 読み込めた画像が2枚未満です")
        sys.exit(1)

    # 結合
    print()
    print("画像を結合中...")

    if args.vertical:
        combined = combine_images_vertical(images, args.gap, background_color)
    else:
        combined = combine_images_horizontal(images, args.gap, background_color)

    # 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix.lower() in [".jpg", ".jpeg"]:
        combined.save(output_path, "JPEG", quality=args.quality)
    else:
        combined.save(output_path)

    # 結果表示
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print()
    print("=" * 50)
    print(f"完了: {output_path}")
    print(f"サイズ: {combined.width} x {combined.height} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
