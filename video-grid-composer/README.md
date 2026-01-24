# Video Grid Composer

複数の動画を横並び・縦並び・グリッド状に結合するツール

## 機能

- **横並び結合** (`--horizontal`): 動画を左右に並べて結合
- **縦並び結合** (`--vertical`): 動画を上下に並べて結合
- **グリッド結合** (`--grid 2x2`): 動画をグリッド状に配置して結合
- ファイル名オーバーレイ表示（オプション）
- 短い動画の自動ループ

## 必要条件

- Python 3.8+
- OpenCV (`opencv-python`)
- NumPy

## インストール

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools/video-grid-composer
pip install opencv-python numpy
```

## 使用方法

### 基本的な使い方

```bash
# カレントディレクトリの動画を横並びで結合
python video_grid_composer.py --horizontal

# 縦並びで結合
python video_grid_composer.py --vertical

# 2x2グリッドで結合
python video_grid_composer.py --grid 2x2
```

### 入出力ファイルを指定

```bash
# 特定のファイルを指定して結合
python video_grid_composer.py -i video1.mp4 video2.mp4 -o combined.mp4

# 3つの動画を縦並びで結合
python video_grid_composer.py --vertical -i a.mp4 b.mp4 c.mp4 -o vertical.mp4
```

### オプション

```bash
# ファイル名オーバーレイを非表示
python video_grid_composer.py --horizontal --no-filename

# 短い動画をループさせない（黒画面で埋める）
python video_grid_composer.py --horizontal --no-loop

# ファイル名の降順でソート
python video_grid_composer.py --horizontal --sort name-desc
```

## オプション一覧

| オプション | 説明 |
|-----------|------|
| `--horizontal`, `-H` | 横並びで結合（デフォルト） |
| `--vertical`, `-V` | 縦並びで結合 |
| `--grid COLSxROWS`, `-G` | グリッド状に結合（例: 2x2, 3x2） |
| `-i`, `--input` | 入力動画ファイル（複数指定可） |
| `-o`, `--output` | 出力ファイル名 |
| `--no-filename` | ファイル名オーバーレイを非表示 |
| `--no-loop` | 短い動画をループさせない |
| `--sort` | ソート順: name, name-desc, size, none |

## 出力仕様

- 形式: MP4 (mp4v コーデック)
- FPS: 入力動画の最小値
- 解像度:
  - 横並び: 幅の合計 × 高さの最大値
  - 縦並び: 幅の最大値 × 高さの合計
  - グリッド: セルサイズ × グリッド数

## 対応フォーマット

入力: `.mp4`, `.mov`, `.avi`, `.mkv`, `.flv`, `.wmv`
出力: `.mp4`

## ライセンス

MIT License
