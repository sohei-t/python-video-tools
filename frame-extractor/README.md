# Frame Extractor

動画から指定間隔で静止画（フレーム）を抽出するツール

## 必要条件

- Python 3.8+
- OpenCV (`opencv-python`)

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/frame-extractor
pip install opencv-python
```

## 使用方法

```bash
# 1秒間隔で全フレームを抽出
python frame_extractor.py video.mp4

# 0.5秒間隔で抽出
python frame_extractor.py video.mp4 --interval 0.5

# 時間範囲を指定（1分〜2分）
python frame_extractor.py video.mp4 --range 00:01:00-00:02:00

# 複数の時間範囲を指定
python frame_extractor.py video.mp4 --range "0:00-1:00,2:00-3:00"

# ディレクトリ内の全動画を処理
python frame_extractor.py -i ./videos -o ./frames

# PNG形式で高画質保存
python frame_extractor.py video.mp4 --format png --quality 100

# 元ファイルを移動しない
python frame_extractor.py video.mp4 --no-move
```

## オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `inputs` | 入力ファイルまたはディレクトリ | - |
| `-i`, `--input-dir` | 入力ディレクトリ | カレント |
| `-o`, `--output-dir` | 出力ディレクトリ | `./comp` |
| `--interval` | 抽出間隔（秒） | 1.0 |
| `--range` | 抽出する時間範囲 | 全体 |
| `--format` | 出力フォーマット (jpg/png/bmp) | jpg |
| `--quality` | 画質 (1-100) | 95 |
| `--prefix` | 出力ファイル名のプレフィックス | - |
| `--config` | 設定ファイルのパス | - |
| `--no-move` | 処理後に元ファイルを移動しない | 無効 |

## 時間指定形式

以下の形式に対応しています：

| 形式 | 例 |
|-----|-----|
| 秒 | `90`, `90.5` |
| MM:SS | `01:30` |
| HH:MM:SS | `00:01:30` |

### 範囲指定

```bash
# 単一範囲
--range 00:01:00-00:02:00

# 複数範囲（カンマ区切り）
--range "00:00:00-00:01:00,00:05:00-00:06:00"
```

## config.txt形式

CLIオプションの代わりに設定ファイルを使用することもできます。

```text
# 静止画を取得する間隔（秒）
interval=1

# 静止画取得する期間（複数指定可）
periods=00:00:00--00:04:53,00:10:00--00:15:00
```

```bash
# config.txtを使用
python frame_extractor.py --config config.txt

# カレントディレクトリにconfig.txtがあれば自動読み込み
python frame_extractor.py
```

## 出力ファイル

抽出されたフレームは以下の命名規則で保存されます：

```
{動画名}_{連番}.{拡張子}
例: video_0001.jpg, video_0002.jpg, ...
```

## 対応フォーマット

入力: `.mp4`, `.avi`, `.mkv`, `.mov`, `.flv`, `.wmv`, `.webm`, `.m4v`
出力: `.jpg`, `.png`, `.bmp`

## ライセンス

MIT License
