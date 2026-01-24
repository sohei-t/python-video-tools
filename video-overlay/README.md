# Video Overlay

動画に画像や別の動画をオーバーレイ（重ねて）合成するツール

## 必要条件

- Python 3.8+
- moviepy

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/video-overlay
pip install moviepy
```

## 使用方法

### 画像オーバーレイ

```bash
# 右上にロゴを配置（デフォルト）
python video_overlay.py video.mp4 logo.png

# 左上に配置
python video_overlay.py video.mp4 logo.png --position top-left

# 右下に配置、サイズ20%
python video_overlay.py video.mp4 logo.png --position bottom-right --size 20

# 透明度70%で配置
python video_overlay.py video.mp4 logo.png --opacity 0.7

# 出力ファイル名を指定
python video_overlay.py video.mp4 logo.png -o output.mp4
```

### 動画オーバーレイ（ピクチャーインピクチャー）

```bash
# 右上にサブ動画を配置
python video_overlay.py main.mp4 sub.mp4

# 右下に配置、サイズ50%
python video_overlay.py main.mp4 sub.mp4 --position bottom-right --size 50

# サブ動画をループしない
python video_overlay.py main.mp4 sub.mp4 --no-loop

# サブ動画の音声も含める
python video_overlay.py main.mp4 sub.mp4 --sub-audio
```

## オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `video` | メインとなる動画ファイル | 必須 |
| `overlay` | オーバーレイする画像/動画 | 必須 |
| `-o`, `--output` | 出力ファイル名 | `{入力}_overlay.mp4` |
| `-p`, `--position` | オーバーレイの位置 | `top-right` |
| `-s`, `--size` | オーバーレイのサイズ (%) | 30 |
| `-m`, `--margin` | 端からの余白 (px) | 10 |
| `--opacity` | 透明度 (0.0-1.0) | 1.0 |
| `--no-loop` | サブ動画をループしない | - |
| `--sub-audio` | サブ動画の音声を含める | - |

## 位置オプション

| 位置 | 説明 |
|-----|------|
| `top-left` | 左上 |
| `top-right` | 右上（デフォルト） |
| `bottom-left` | 左下 |
| `bottom-right` | 右下 |
| `center` | 中央 |

```
┌─────────────────┐
│ TL          TR  │
│                 │
│      CENTER     │
│                 │
│ BL          BR  │
└─────────────────┘
```

## ユースケース

### ロゴ/ウォーターマークの追加

```bash
python video_overlay.py video.mp4 logo.png --size 15 --opacity 0.8
```

### ピクチャーインピクチャー

メイン動画の隅に別の動画を小さく表示します。

```bash
python video_overlay.py main.mp4 webcam.mp4 --position bottom-right --size 25
```

### 複数のオーバーレイ

複数のオーバーレイを重ねる場合は、順番に実行します。

```bash
# まずロゴを追加
python video_overlay.py video.mp4 logo.png -o temp.mp4

# 次にサブ動画を追加
python video_overlay.py temp.mp4 sub.mp4 --position bottom-left -o final.mp4
```

## 対応フォーマット

入力動画: `.mp4`, `.avi`, `.mkv`, `.mov`, `.flv`, `.wmv`, `.webm`, `.m4v`
入力画像: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`, `.gif`, `.tiff`
出力: `.mp4`

## ライセンス

MIT License
