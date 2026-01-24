#!/usr/bin/env python3
"""
Video Player
Webブラウザベースの動画プレイヤー

Usage:
    python video_player.py [OPTIONS]
    python video_player.py -d ./videos
    python video_player.py --port 9000

Requirements:
    pip install flask pillow opencv-python

Original: moves-player _20250503.py
"""

import argparse
import glob
import io
import os
import sys
import time
import webbrowser
from threading import Thread

try:
    from flask import Flask, render_template_string, send_from_directory, jsonify, send_file
    from PIL import Image, ImageDraw
    import cv2
except ImportError as e:
    print(f"エラー: 必要なライブラリがインストールされていません: {e}")
    print("インストール: pip install flask pillow opencv-python")
    sys.exit(1)


# Flaskアプリケーションの初期化
app = Flask(__name__)


# グローバル設定
class Config:
    upload_folder = os.getcwd()
    thumbnail_dir = None
    thumbnail_prefix = 'thumb_'
    max_content_length = 1024 * 1024 * 1024  # 1GB


config = Config()


def get_video_files():
    """指定ディレクトリから動画ファイルを取得"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    video_files = []

    for ext in video_extensions:
        pattern = os.path.join(config.upload_folder, f'*{ext}')
        found_files = glob.glob(pattern)
        video_files.extend([os.path.basename(f) for f in found_files])

    # thumbnailsフォルダ内のファイルを除外
    video_files = [f for f in video_files if not f.startswith(('templates', 'static', 'thumbnails'))]
    video_files.sort()
    return video_files


def get_thumbnail_path(video_name):
    """ビデオ名からサムネイルのパスを生成"""
    base_name = os.path.splitext(video_name)[0]
    return os.path.join(config.thumbnail_dir, f"{config.thumbnail_prefix}{base_name}.jpg")


def generate_thumbnail(video_path, force=False):
    """動画からサムネイルを生成"""
    video_name = os.path.basename(video_path)
    thumbnail_path = get_thumbnail_path(video_name)

    if os.path.exists(thumbnail_path) and not force:
        return thumbnail_path

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count == 0:
            return None

        cap.set(cv2.CAP_PROP_POS_FRAMES, min(frame_count // 2, 100))
        success, frame = cap.read()

        if success:
            frame = cv2.resize(frame, (240, 135))
            cv2.imwrite(thumbnail_path, frame)
            return thumbnail_path
        return None
    except Exception as e:
        print(f"サムネイル生成エラー: {e}")
        return None
    finally:
        if 'cap' in locals() and cap is not None:
            cap.release()


def check_and_generate_thumbnails():
    """全動画のサムネイルをチェックして生成"""
    print("サムネイルをチェックしています...")
    video_files = get_video_files()
    generated_count = 0

    for video in video_files:
        video_path = os.path.join(config.upload_folder, video)
        thumbnail_path = get_thumbnail_path(video)

        if not os.path.exists(thumbnail_path):
            if generate_thumbnail(video_path):
                generated_count += 1
                print(f"  生成: {video}")

    print(f"サムネイル生成完了: {generated_count}個の新しいサムネイルを生成")


# HTMLテンプレート
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>動画プレイヤー</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #1a1a2e; color: #eee; }
        .container { display: flex; height: 100vh; }
        .sidebar { width: 280px; background-color: #16213e; display: flex; flex-direction: column; }
        .sidebar-header { padding: 15px; border-bottom: 1px solid #0f3460; }
        .sidebar-header h2 { font-size: 1.1rem; color: #e94560; }
        .thumbnail-container { flex: 1; overflow-y: auto; padding: 10px; }
        .thumbnail-item { margin-bottom: 12px; cursor: pointer; border-radius: 6px; overflow: hidden; transition: transform 0.2s, box-shadow 0.2s; position: relative; background: #0f3460; }
        .thumbnail-item:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3); }
        .thumbnail-item.active { border: 2px solid #e94560; }
        .thumbnail-img { width: 100%; height: 135px; object-fit: cover; display: block; }
        .thumbnail-title { padding: 8px; background-color: rgba(0, 0, 0, 0.8); color: #fff; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; position: absolute; bottom: 0; width: 100%; }
        .main-content { flex: 1; padding: 20px; display: flex; flex-direction: column; background: #1a1a2e; }
        .video-container { max-width: 1200px; margin: 0 auto; width: 100%; }
        video { width: 100%; height: auto; max-height: 75vh; background-color: #000; border-radius: 8px; }
        .video-info { margin: 15px 0; }
        .video-info h2 { font-size: 1.2rem; color: #fff; }
        .controls { display: flex; gap: 10px; margin-top: 15px; align-items: center; flex-wrap: wrap; }
        button { padding: 10px 20px; background-color: #e94560; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95rem; transition: background-color 0.2s; }
        button:hover { background-color: #ff6b6b; }
        button:disabled { background-color: #4a4a6a; cursor: not-allowed; }
        #speedInfo { padding: 10px 15px; background-color: #0f3460; border-radius: 6px; font-weight: bold; color: #e94560; }
        .shortcuts { margin-top: 20px; padding: 15px; background: #16213e; border-radius: 8px; font-size: 0.85rem; color: #888; }
        .shortcuts kbd { background: #0f3460; padding: 2px 8px; border-radius: 4px; margin: 0 2px; }
        @media (max-width: 768px) {
            .container { flex-direction: column; }
            .sidebar { width: 100%; height: 180px; }
            .thumbnail-container { display: flex; overflow-x: auto; }
            .thumbnail-item { width: 180px; flex-shrink: 0; margin-right: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-header"><h2>📹 動画一覧</h2></div>
            <div class="thumbnail-container" id="thumbnailContainer"></div>
        </div>
        <div class="main-content">
            <div class="video-container">
                <video id="videoPlayer" controls></video>
                <div class="video-info"><h2 id="videoTitle">動画を選択してください</h2></div>
                <div class="controls">
                    <button id="prevBtn">◀ 前へ</button>
                    <button id="nextBtn">次へ ▶</button>
                    <button id="slowDownBtn">🐢 遅く</button>
                    <button id="speedUpBtn">🐇 速く</button>
                    <span id="speedInfo">1.0x</span>
                </div>
                <div class="shortcuts">
                    ショートカット: <kbd>←</kbd><kbd>→</kbd> 前後の動画 / <kbd>Space</kbd> 再生/停止 / <kbd>,</kbd><kbd>.</kbd> 速度変更
                </div>
            </div>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const videoPlayer = document.getElementById('videoPlayer');
            const videoTitle = document.getElementById('videoTitle');
            const thumbnailContainer = document.getElementById('thumbnailContainer');
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            const speedUpBtn = document.getElementById('speedUpBtn');
            const slowDownBtn = document.getElementById('slowDownBtn');
            const speedInfo = document.getElementById('speedInfo');

            let videos = [];
            let currentVideoIndex = 0;
            let playbackRate = 1.0;

            async function fetchVideos() {
                try {
                    const response = await fetch('/videos');
                    videos = await response.json();
                    if (videos.length > 0) {
                        renderThumbnails();
                        loadVideo(0);
                    } else {
                        videoTitle.textContent = '動画ファイルが見つかりません';
                    }
                } catch (error) {
                    console.error('動画一覧の取得に失敗しました:', error);
                }
            }

            function renderThumbnails() {
                thumbnailContainer.innerHTML = '';
                videos.forEach((video, index) => {
                    const item = document.createElement('div');
                    item.className = 'thumbnail-item' + (index === currentVideoIndex ? ' active' : '');
                    item.dataset.index = index;
                    item.innerHTML = `<img class="thumbnail-img" src="${video.thumbnail}" alt="${video.name}" onerror="this.src='/placeholder'"><div class="thumbnail-title">${video.name}</div>`;
                    item.addEventListener('click', () => loadVideo(index));
                    thumbnailContainer.appendChild(item);
                });
            }

            function loadVideo(index) {
                if (index < 0 || index >= videos.length) return;
                currentVideoIndex = index;
                const video = videos[index];
                videoPlayer.src = video.path;
                videoTitle.textContent = video.name;
                videoPlayer.playbackRate = playbackRate;
                videoPlayer.load();
                videoPlayer.play().catch(() => {});
                document.querySelectorAll('.thumbnail-item').forEach((item, i) => {
                    item.classList.toggle('active', i === index);
                    if (i === index) item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                });
                updateButtonState();
            }

            function updateButtonState() {
                prevBtn.disabled = currentVideoIndex <= 0;
                nextBtn.disabled = currentVideoIndex >= videos.length - 1;
            }

            function updatePlaybackRate(rate) {
                playbackRate = Math.max(0.25, Math.min(16, rate));
                videoPlayer.playbackRate = playbackRate;
                speedInfo.textContent = playbackRate.toFixed(2) + 'x';
            }

            videoPlayer.addEventListener('ended', () => { if (currentVideoIndex < videos.length - 1) loadVideo(currentVideoIndex + 1); });
            prevBtn.addEventListener('click', () => loadVideo(currentVideoIndex - 1));
            nextBtn.addEventListener('click', () => loadVideo(currentVideoIndex + 1));
            speedUpBtn.addEventListener('click', () => updatePlaybackRate(playbackRate * 2));
            slowDownBtn.addEventListener('click', () => updatePlaybackRate(playbackRate / 2));

            document.addEventListener('keydown', (e) => {
                switch(e.key) {
                    case 'ArrowRight': loadVideo(currentVideoIndex + 1); break;
                    case 'ArrowLeft': loadVideo(currentVideoIndex - 1); break;
                    case '.': case '>': updatePlaybackRate(playbackRate * 2); break;
                    case ',': case '<': updatePlaybackRate(playbackRate / 2); break;
                    case ' ': videoPlayer.paused ? videoPlayer.play() : videoPlayer.pause(); e.preventDefault(); break;
                }
            });

            fetchVideos();
        });
    </script>
</body>
</html>'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/videos')
def get_videos():
    video_files = get_video_files()
    videos = []
    for idx, video in enumerate(video_files):
        videos.append({
            'id': idx,
            'name': video,
            'path': f'/video/{video}',
            'thumbnail': f'/thumbnail/{video}'
        })
    return jsonify(videos)


@app.route('/video/<path:filename>')
def serve_video(filename):
    return send_from_directory(config.upload_folder, filename)


@app.route('/thumbnail/<path:filename>')
def serve_thumbnail(filename):
    thumbnail_path = get_thumbnail_path(filename)
    if os.path.exists(thumbnail_path):
        return send_from_directory(config.thumbnail_dir, os.path.basename(thumbnail_path))
    return create_placeholder()


@app.route('/placeholder')
def create_placeholder():
    img = Image.new('RGB', (240, 135), color=(22, 33, 62))
    draw = ImageDraw.Draw(img)
    draw.text((80, 60), "No Preview", fill=(233, 69, 96))
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


def open_browser(url, delay=1.5):
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print(f"ブラウザで開きました: {url}")
    except Exception as e:
        print(f"ブラウザを開けませんでした: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Webブラウザベースの動画プレイヤー",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                        # カレントディレクトリの動画を再生
  %(prog)s -d ./videos            # 指定ディレクトリの動画を再生
  %(prog)s --port 9000            # ポート9000で起動
  %(prog)s --no-browser           # ブラウザを自動で開かない

キーボードショートカット:
  ← →     前後の動画に移動
  Space   再生/一時停止
  , .     再生速度を変更（0.25x〜16x）
        """,
    )

    parser.add_argument(
        "-d", "--directory",
        type=str,
        default=os.getcwd(),
        help="動画ファイルのあるディレクトリ（デフォルト: カレントディレクトリ）",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8080,
        help="サーバーのポート番号（デフォルト: 8080）",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="ブラウザを自動で開かない",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="サーバーのホスト（デフォルト: localhost）",
    )

    args = parser.parse_args()

    # 設定を更新
    config.upload_folder = os.path.abspath(args.directory)
    config.thumbnail_dir = os.path.join(config.upload_folder, 'thumbnails')
    os.makedirs(config.thumbnail_dir, exist_ok=True)

    if not os.path.isdir(config.upload_folder):
        print(f"エラー: ディレクトリが存在しません: {config.upload_folder}")
        sys.exit(1)

    # サムネイルを生成
    check_and_generate_thumbnails()

    # 動画数を表示
    video_count = len(get_video_files())
    print(f"\n動画ファイル: {video_count}個")
    print(f"ディレクトリ: {config.upload_folder}")

    url = f"http://{args.host}:{args.port}/"
    print(f"\n動画プレイヤーを起動中... {url}")

    # ブラウザを開く
    if not args.no_browser:
        browser_thread = Thread(target=lambda: open_browser(url))
        browser_thread.daemon = True
        browser_thread.start()

    # サーバー起動
    try:
        app.run(debug=False, host=args.host, port=args.port, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            alt_port = args.port + 1000
            print(f"ポート{args.port}は使用中です。ポート{alt_port}で再試行します...")
            url = f"http://{args.host}:{alt_port}/"
            if not args.no_browser:
                browser_thread = Thread(target=lambda: open_browser(url))
                browser_thread.daemon = True
                browser_thread.start()
            app.run(debug=False, host=args.host, port=alt_port, threaded=True)
        else:
            raise


if __name__ == '__main__':
    main()
