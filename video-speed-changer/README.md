# Video Speed Changer

動画の再生速度とフレームレートを変更するツール

## 必要条件

- Python 3.8+
- ffmpeg

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/video-speed-changer
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
# 0.5倍速（スローモーション）
python video_speed_changer.py video.mp4 --speed 0.5

# 2倍速
python video_speed_changer.py video.mp4 --speed 2.0

# 0.5倍速 + 30fps出力
python video_speed_changer.py video.mp4 --speed 0.5 --fps 30

# ディレクトリ内の全動画を処理
python video_speed_changer.py -i ./videos --speed 0.5

# 音声を削除
python video_speed_changer.py video.mp4 --speed 0.5 --no-audio

# 出力先を指定
python video_speed_changer.py video.mp4 --speed 0.5 -o ./output
```

## オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `inputs` | 入力ファイルまたはディレクトリ | - |
| `-i`, `--input-dir` | 入力ディレクトリ | カレント |
| `-o`, `--output-dir` | 出力ディレクトリ | `./output` |
| `--speed` | 再生速度の倍率 | 0.5 |
| `--fps` | 出力フレームレート | 元のまま |
| `--audio` | 音声処理モード | adjust |
| `--no-audio` | 音声を削除 | - |
| `--suffix` | 出力ファイル名のサフィックス | 自動生成 |
| `--ffmpeg` | ffmpegのパス | 自動検出 |

## 速度設定

| 速度 | 効果 | 再生時間 |
|-----|------|---------|
| 0.25 | 超スローモーション | 4倍に延長 |
| 0.5 | スローモーション | 2倍に延長 |
| 1.0 | 等速 | 変化なし |
| 2.0 | 2倍速 | 半分に短縮 |
| 4.0 | 4倍速 | 1/4に短縮 |

## 音声処理モード

| モード | 説明 |
|-------|------|
| `adjust` | 音声も速度を調整（ピッチ維持） |
| `remove` | 音声を削除 |
| `copy` | 音声をそのままコピー（同期ずれの可能性） |

### 例

```bash
# 音声も一緒にスロー再生（デフォルト）
python video_speed_changer.py video.mp4 --speed 0.5 --audio adjust

# 音声を削除してスロー再生
python video_speed_changer.py video.mp4 --speed 0.5 --audio remove

# 音声はそのままでスロー再生（BGMなど同期不要な場合）
python video_speed_changer.py video.mp4 --speed 0.5 --audio copy
```

## ユースケース

### 60fps → 30fps スローモーション変換

60fpsで撮影した動画を30fpsで0.5倍速にすると、滑らかなスローモーション映像になります。

```bash
python video_speed_changer.py video_60fps.mp4 --speed 0.5 --fps 30
```

### タイムラプス作成

長時間の動画を高速再生してタイムラプス風にできます。

```bash
python video_speed_changer.py long_video.mp4 --speed 10.0 --no-audio
```

## 対応フォーマット

入力/出力: `.mp4`, `.avi`, `.mkv`, `.mov`, `.flv`, `.wmv`, `.webm`, `.m4v`

## ライセンス

MIT License
