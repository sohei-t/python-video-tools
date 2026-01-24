# Python Video Tools

[![CI](https://github.com/sohei-t/python-video-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/sohei-t/python-video-tools/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

動画・画像編集用のPythonツール集。ffmpegやOpenCVを活用した、CLIで簡単に使えるツールを提供します。

## ツール一覧

### 動画処理

| ツール | 説明 |
|-------|------|
| [video-segment-tools](./video-segment-tools/) | 動画の切り出し・分割・結合 |
| [video-grid-composer](./video-grid-composer/) | 複数動画の横並び・縦並び・グリッド結合 |
| [video-compressor](./video-compressor/) | 動画ファイルサイズ縮小 |
| [video-speed-changer](./video-speed-changer/) | 再生速度・フレームレート変更 |
| [video-overlay](./video-overlay/) | 画像・動画のオーバーレイ合成 |
| [video-player](./video-player/) | Webブラウザベースの動画プレイヤー |

### 音声処理

| ツール | 説明 |
|-------|------|
| [audio-extractor](./audio-extractor/) | 動画から音声をMP3に抽出 |
| [audio-remover](./audio-remover/) | 動画から音声トラックを除去 |

### 画像処理

| ツール | 説明 |
|-------|------|
| [face-cropper](./face-cropper/) | 顔検出・切り出し＆スライドショー作成 |
| [frame-extractor](./frame-extractor/) | 動画から指定間隔で静止画抽出 |
| [image-combiner](./image-combiner/) | 複数画像を横並び・縦並びで結合 |

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools
```

各ツールのディレクトリに移動して、必要な依存関係をインストールしてください。

## 必要条件

- Python 3.9+
- ffmpeg（動画処理ツール用）
- OpenCV, NumPy（画像・動画処理用）
- dlib（顔検出用）
- Pillow（画像処理用）
- moviepy（動画オーバーレイ用）
- Flask（動画プレイヤー用）

### ffmpegのインストール

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

## 開発

### テストの実行

```bash
pip install pytest pillow
pytest tests/ -v
```

### コードフォーマット

```bash
pip install black isort
black .
isort .
```

## ライセンス

MIT License

## 作者

[@sohei-t](https://github.com/sohei-t)
