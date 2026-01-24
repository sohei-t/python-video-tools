# Face Cropper

画像から顔を検出して切り出し、正方形画像を生成するツールセット

## ツール一覧

| スクリプト | 機能 |
|-----------|------|
| `face_cropper.py` | 画像から顔を検出→切り出し→正方形にリサイズ |
| `slideshow_maker.py` | 画像からスライドショー動画を作成（フェード付き） |

## 必要条件

- Python 3.8+
- OpenCV (`opencv-python`)
- dlib
- NumPy

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/face-cropper
pip install -r requirements.txt
```

### dlibのインストールについて

dlibのインストールにはCMakeが必要な場合があります。

**macOS:**
```bash
brew install cmake
pip install dlib
```

**Ubuntu/Debian:**
```bash
sudo apt install cmake
pip install dlib
```

## 使用方法

### face_cropper.py - 顔切り出し

```bash
# カレントディレクトリの画像から顔を切り出し
python face_cropper.py

# 出力サイズを指定
python face_cropper.py --size 1080

# マージン（顔周囲の余白）を調整
python face_cropper.py --margin 0.5

# 入出力ディレクトリを指定
python face_cropper.py -i ./photos -o ./faces
```

#### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-i`, `--input-dir` | 入力ディレクトリ | カレント |
| `-o`, `--output-dir` | 出力ディレクトリ | `./comp` |
| `--size` | 出力サイズ（正方形） | 1080 |
| `--margin` | 顔周囲のマージン割合 | 0.5 |
| `--background` | 背景色 (R,G,B) | 0,0,0 |
| `--prefix` | 出力ファイル名プレフィックス | `face_` |
| `--no-move` | 元ファイルを移動しない | 無効 |

### slideshow_maker.py - スライドショー作成

```bash
# カレントディレクトリの画像からスライドショー作成
python slideshow_maker.py

# 入出力を指定
python slideshow_maker.py -i ./images -o slideshow.mp4

# 表示時間とフェード時間を調整
python slideshow_maker.py --duration 5 --fade 1

# 解像度を指定
python slideshow_maker.py --resolution 1920x1080
```

#### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-i`, `--input-dir` | 入力ディレクトリ | カレント |
| `-o`, `--output` | 出力ファイル | `slideshow_日時.mp4` |
| `--duration` | 各画像の表示時間（秒） | 5.0 |
| `--fade` | フェード時間（秒） | 1.0 |
| `--fps` | フレームレート | 30 |
| `--resolution` | 出力解像度 (WxH) | 1920x1080 |
| `--background` | 背景色 (R,G,B) | 0,0,0 |

## ワークフロー例

顔切り出し → スライドショー作成の一連の流れ:

```bash
# 1. 画像から顔を切り出し
python face_cropper.py -i ./photos --size 1080

# 2. 切り出した顔からスライドショーを作成
python slideshow_maker.py -i ./comp -o faces_slideshow.mp4
```

## 対応フォーマット

入力画像: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp`
出力動画: `.mp4` (mp4v コーデック)

## 注意事項

- 顔が検出されない画像はスキップされます
- 1つの画像に複数の顔がある場合、すべて切り出されます
- dlibの正面顔検出器を使用するため、横顔は検出されにくい場合があります

## ライセンス

MIT License
