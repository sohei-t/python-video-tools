# Python Video Tools

動画編集用のPythonツール集

## ツール一覧

| ディレクトリ | 説明 |
|-------------|------|
| [video-segment-tools](./video-segment-tools/) | 動画の切り出し・分割・結合ツール |
| [video-grid-composer](./video-grid-composer/) | 複数動画の横並び・縦並び・グリッド結合ツール |
| [video-compressor](./video-compressor/) | 動画ファイルサイズ縮小ツール |
| [face-cropper](./face-cropper/) | 画像から顔を検出・切り出し＆スライドショー作成ツール |
| [audio-extractor](./audio-extractor/) | 動画から音声を抽出してMP3に変換するツール |
| [frame-extractor](./frame-extractor/) | 動画から指定間隔で静止画を抽出するツール |
| [audio-remover](./audio-remover/) | 動画から音声トラックを除去するツール |
| [image-combiner](./image-combiner/) | 複数画像を横並び・縦並びで1枚に結合するツール |
| [video-speed-changer](./video-speed-changer/) | 動画の再生速度・フレームレート変更ツール |

## 必要条件

- Python 3.8+
- ffmpeg（video-segment-tools, video-compressor用）
- OpenCV, NumPy（video-grid-composer, face-cropper用）
- dlib（face-cropper用）
- Pillow（image-combiner用）

## ライセンス

MIT License

## 作者

sohei-t
