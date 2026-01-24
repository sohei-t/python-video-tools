# Audio Remover

動画ファイルから音声トラックを除去するツール

## 必要条件

- Python 3.8+
- ffmpeg

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/audio-remover
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
# 単一ファイルから音声除去
python audio_remover.py video.mp4

# 複数ファイルを処理
python audio_remover.py video1.mp4 video2.mp4

# ディレクトリ内の全動画を処理
python audio_remover.py -i ./videos

# 出力先を指定
python audio_remover.py -o ./muted video.mp4

# サフィックスを変更
python audio_remover.py --suffix _muted video.mp4
# → video_muted.mp4

# プレフィックスを追加
python audio_remover.py --prefix muted_ video.mp4
# → muted_video.mp4
```

## オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `inputs` | 入力ファイルまたはディレクトリ | - |
| `-i`, `--input-dir` | 入力ディレクトリ | カレント |
| `-o`, `--output-dir` | 出力ディレクトリ | 入力と同じ場所 |
| `--prefix` | 出力ファイル名のプレフィックス | - |
| `--suffix` | 出力ファイル名のサフィックス | `_noaudio` |
| `--ffmpeg` | ffmpegのパス | 自動検出 |

## 出力ファイル名

デフォルトでは `_noaudio` サフィックスが追加されます。

```
入力: video.mp4
出力: video_noaudio.mp4
```

`--prefix` と `--suffix` を組み合わせることも可能です：

```bash
python audio_remover.py --prefix muted_ --suffix "" video.mp4
# → muted_video.mp4
```

## 特徴

- **高速処理**: 映像は再エンコードせずコピーするため、処理が高速
- **ファイルサイズ削減**: 音声トラック分のサイズが削減されます
- **品質維持**: 映像品質は元のまま維持されます

## 対応フォーマット

入力/出力: `.mp4`, `.avi`, `.mkv`, `.mov`, `.flv`, `.wmv`, `.webm`, `.m4v`

## ライセンス

MIT License
