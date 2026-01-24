# Video Segment Tools

動画の切り出し・分割・結合を行うPythonツール集

## 機能

| ツール | 機能 |
|--------|------|
| `video_segment_extractor.py` | 設定ファイルで指定した時間範囲で動画を切り出し |
| `video_splitter.py` | 動画を指定した時間間隔で分割 |
| `video_merger.py` | 複数の動画ファイルを結合 |

## 必要条件

- Python 3.8+
- ffmpeg（動画処理用）

### ffmpegのインストール

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
[ffmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロードし、PATHを設定

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/video-segment-tools
```

追加のPythonパッケージは不要です（標準ライブラリのみ使用）。

## 使用方法

### 1. video_segment_extractor.py - 時間範囲で切り出し

設定ファイルで指定した複数の時間範囲を一括で切り出します。

```bash
# 基本的な使い方（カレントディレクトリのconfig.txtを使用）
python video_segment_extractor.py

# 設定ファイルを指定
python video_segment_extractor.py -c my_config.txt

# 入出力ディレクトリを指定
python video_segment_extractor.py -i ./videos -o ./output

# 高速モード（再エンコードなし）
python video_segment_extractor.py --fast
```

**設定ファイルの書式（example.config.txt）:**
```
start_end_times=01:00-01:30,02:15-02:45,05:00-05:30
output_dir=segments
```

### 2. video_splitter.py - 時間間隔で分割

長い動画を指定した時間ごとに分割します。

```bash
# 10分ごとに分割
python video_splitter.py -d 00:10:00

# 特定のファイルを5分ごとに分割
python video_splitter.py -d 00:05:00 -i video.mp4

# 出力先を指定
python video_splitter.py -d 00:30:00 -o ./output
```

### 3. video_merger.py - 動画を結合

複数の動画ファイルを1つに結合します。

```bash
# ディレクトリ内の動画を結合
python video_merger.py -i ./segments

# 出力ファイル名を指定
python video_merger.py -i ./segments -o combined.mp4

# サブディレクトリのcompフォルダを自動検索
python video_merger.py --comp-subdir

# 音声なしで結合
python video_merger.py --no-audio
```

## オプション

### 共通オプション

| オプション | 説明 |
|-----------|------|
| `--ffmpeg PATH` | ffmpegの実行ファイルパスを指定 |

### video_segment_extractor.py

| オプション | 説明 |
|-----------|------|
| `-c, --config` | 設定ファイルのパス（デフォルト: config.txt） |
| `-i, --input-dir` | 入力動画のディレクトリ |
| `-o, --output-dir` | 出力ディレクトリ |
| `--fast` | 高速モード（再エンコードなし） |

### video_splitter.py

| オプション | 説明 |
|-----------|------|
| `-d, --duration` | 分割時間間隔（HH:MM:SS形式）**必須** |
| `-i, --input` | 入力動画ファイルまたはディレクトリ |
| `-o, --output-dir` | 出力ディレクトリ |
| `--overhead` | 最後のセグメントを結合するオーバーヘッド秒数（デフォルト: 10） |

### video_merger.py

| オプション | 説明 |
|-----------|------|
| `-i, --input` | 入力ディレクトリ |
| `-o, --output` | 出力ファイルまたはディレクトリ |
| `--method` | 結合方法: auto/fast/slow（デフォルト: auto） |
| `--no-audio` | 音声を含めない |
| `--comp-subdir` | サブディレクトリのcompフォルダを検索 |

## 環境変数

| 変数 | 説明 |
|------|------|
| `FFMPEG_PATH` | ffmpegの実行ファイルパス |
| `FFPROBE_PATH` | ffprobeの実行ファイルパス |

## 対応フォーマット

入力: `.mp4`, `.mov`, `.avi`, `.mkv`, `.flv`, `.wmv`
出力: `.mp4`

## ライセンス

MIT License
