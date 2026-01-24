# Image Combiner

複数の画像を横並び・縦並びで1枚に結合するツール

## 必要条件

- Python 3.8+
- Pillow

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/image-combiner
pip install Pillow
```

## 使用方法

```bash
# 2枚を横並びで結合
python image_combiner.py image1.jpg image2.jpg

# 複数の画像を横並びで結合
python image_combiner.py *.jpg

# 縦並びで結合
python image_combiner.py --vertical image1.jpg image2.jpg

# ディレクトリ内の画像を結合
python image_combiner.py -i ./images -o combined.jpg

# 画像間に10pxのギャップを追加
python image_combiner.py --gap 10 image1.jpg image2.jpg

# 黒背景で結合
python image_combiner.py --background 0,0,0 *.png
```

## オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `images` | 結合する画像ファイル | - |
| `-i`, `--input-dir` | 入力ディレクトリ | - |
| `-o`, `--output` | 出力ファイル名 | `combined_image.jpg` |
| `-v`, `--vertical` | 縦並びで結合 | 無効（横並び） |
| `--gap` | 画像間のギャップ（ピクセル） | 0 |
| `--background` | 背景色 (R,G,B) | 255,255,255 (白) |
| `--quality` | JPEG品質 (1-100) | 95 |

## 結合方向

### 横並び（デフォルト）

```bash
python image_combiner.py image1.jpg image2.jpg image3.jpg
```

```
┌─────┬─────┬─────┐
│  1  │  2  │  3  │
└─────┴─────┴─────┘
```

### 縦並び

```bash
python image_combiner.py --vertical image1.jpg image2.jpg image3.jpg
```

```
┌─────┐
│  1  │
├─────┤
│  2  │
├─────┤
│  3  │
└─────┘
```

## サイズ調整

- **横並び**: すべての画像の高さを最大の高さに合わせ、アスペクト比を維持してリサイズ
- **縦並び**: すべての画像の幅を最大の幅に合わせ、アスペクト比を維持してリサイズ

## 対応フォーマット

入力: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp`, `.gif`, `.tiff`
出力: `.jpg`, `.png`, `.bmp`, `.webp`

## ライセンス

MIT License
