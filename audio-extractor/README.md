# Audio Extractor

動画ファイルから音声を抽出してMP3に変換するツール

## 必要条件

- Python 3.8+
- ffmpeg

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/audio-extractor
```

### ffmpegのインストール

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

## 使用方法

```bash
# 単一ファイルを変換
python audio_extractor.py video.mp4

# 複数ファイルを変換
python audio_extractor.py video1.mp4 video2.mp4

# ディレクトリ内の全動画を変換
python audio_extractor.py -i ./videos

# 出力先を指定
python audio_extractor.py -o ./audio video.mp4

# ビットレートを指定（CBRモード）
python audio_extractor.py --bitrate 320 video.mp4

# 品質を指定（VBRモード）
python audio_extractor.py --quality 0 video.mp4
```

## オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `inputs` | 入力ファイルまたはディレクトリ | - |
| `-i`, `--input-dir` | 入力ディレクトリ | カレント |
| `-o`, `--output-dir` | 出力ディレクトリ | 入力と同じ場所 |
| `--bitrate` | ビットレート (kbps) | - |
| `--quality` | VBR品質 (0-9) | 2 |
| `--ffmpeg` | ffmpegのパス | 自動検出 |

## 品質設定について

### CBRモード（`--bitrate`）

固定ビットレートで出力します。

| ビットレート | 用途 |
|------------|------|
| 128 | 標準品質、ファイルサイズ小 |
| 192 | 良好な品質 |
| 256 | 高品質 |
| 320 | 最高品質 |

### VBRモード（`--quality`）

可変ビットレートで出力します。音声の複雑さに応じてビットレートが変動し、効率的にエンコードされます。

| 品質値 | 概要 |
|-------|------|
| 0 | 最高品質（約245kbps） |
| 2 | 高品質（約190kbps）**デフォルト** |
| 4 | 標準品質（約165kbps） |
| 6 | 低品質（約130kbps） |

## 対応フォーマット

入力: `.mp4`, `.avi`, `.mkv`, `.mov`, `.flv`, `.wmv`, `.webm`, `.m4v`
出力: `.mp3`

## ライセンス

MIT License
