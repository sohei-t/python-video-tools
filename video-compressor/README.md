# Video Compressor

動画ファイルを分割→圧縮→結合してファイルサイズを縮小するツール

## 機能

- 動画ファイルの圧縮（H.264エンコード）
- 解像度のスケーリング
- 設定ファイルによるパラメータ指定
- バッチ処理（複数ファイル一括処理）
- 圧縮率の表示

## 仕組み

1. 動画を数秒単位のセグメントに分割
2. 各セグメントを個別に圧縮（メモリ効率向上）
3. 圧縮されたセグメントを結合
4. 一時ファイルを自動削除

## 必要条件

- Python 3.8+
- ffmpeg

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/video-compressor
```

## 使用方法

### 基本的な使い方

```bash
# カレントディレクトリの動画を圧縮
python video_compressor.py

# CRF値を指定（大きいほど圧縮率高）
python video_compressor.py --crf 28

# 解像度を50%に縮小
python video_compressor.py --scale 0.5
```

### 入出力を指定

```bash
# 特定のファイルを圧縮
python video_compressor.py -i video.mp4 -o ./output

# 複数ファイルを指定
python video_compressor.py -i video1.mp4 video2.mp4
```

### 詳細オプション

```bash
# 高品質設定（ファイルサイズ大）
python video_compressor.py --crf 20 --preset slow

# 高圧縮設定（ファイルサイズ小）
python video_compressor.py --crf 32 --scale 0.5

# 処理後に元ファイルをdoneフォルダに移動
python video_compressor.py --move-original
```

## オプション一覧

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-i`, `--input` | 入力動画ファイル | カレントディレクトリの動画 |
| `-o`, `--output-dir` | 出力ディレクトリ | `./comp` |
| `--crf` | CRF値 (0-51) | 28 |
| `--scale` | 解像度スケール | なし（元のまま） |
| `--preset` | エンコードプリセット | fast |
| `--segment-seconds` | 分割セグメント秒数 | 5 |
| `--config` | 設定ファイルパス | `config.txt` |
| `--move-original` | 元ファイルをdoneに移動 | 無効 |
| `--ffmpeg` | ffmpegのパス | 自動検出 |

## CRF値の目安

| CRF | 品質 | 用途 |
|-----|------|------|
| 18-23 | 高品質 | アーカイブ、編集用素材 |
| 24-28 | 標準品質 | 一般的な視聴用 |
| 29-35 | 低品質 | プレビュー、容量重視 |

## プリセット

| プリセット | 速度 | 圧縮効率 |
|-----------|------|---------|
| ultrafast | 最速 | 低 |
| fast | 速い | 標準 |
| medium | 標準 | 良好 |
| slow | 遅い | 高 |
| veryslow | 最遅 | 最高 |

## 設定ファイル

`config.txt` で設定を保存できます。

```ini
[Settings]
resolution_scale = 0.5
crf = 28
```

## 対応フォーマット

入力: `.avi`, `.asf`, `.mov`, `.mpg`, `.wmv`, `.ogm`, `.mp4`, `.mkv`
出力: `.mp4` (H.264)

## ライセンス

MIT License
