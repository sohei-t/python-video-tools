#!/usr/bin/env python3
"""
Video Grid Composer
複数の動画を横並び・縦並び・グリッド状に結合するツール

Usage:
    python video_grid_composer.py [OPTIONS]
    python video_grid_composer.py --horizontal           # 横並びで結合
    python video_grid_composer.py --vertical             # 縦並びで結合
    python video_grid_composer.py --grid 2x2             # 2x2グリッドで結合
    python video_grid_composer.py -i a.mp4 b.mp4 -o out.mp4

Requirements:
    pip install opencv-python numpy

Original: 横に結合.py, 縦に結合.py
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import cv2
    import numpy as np
except ImportError:
    print("エラー: opencv-python と numpy が必要です")
    print("インストール: pip install opencv-python numpy")
    sys.exit(1)


def get_video_files(directory: Path) -> List[Path]:
    """ディレクトリから動画ファイルを取得"""
    extensions = {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"}
    videos = []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            videos.append(file)

    return sorted(videos)


def get_video_info(video_path: Path) -> dict:
    """動画の情報を取得"""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"動画を開けません: {video_path}")

    info = {
        "path": video_path,
        "fps": int(cap.get(cv2.CAP_PROP_FPS)),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "capture": cap,
    }
    return info


def draw_filename_overlay(
    frame: np.ndarray,
    filename: str,
    font_scale: float = 1.0,
    color: Tuple[int, int, int] = (255, 255, 255),
    thickness: int = 2,
) -> np.ndarray:
    """フレームにファイル名を描画"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(filename, font, font_scale, thickness)
    text_x = 10
    text_y = text_size[1] + 10

    # 背景を半透明で描画（読みやすくするため）
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (text_x - 5, text_y - text_size[1] - 5),
        (text_x + text_size[0] + 5, text_y + 5),
        (0, 0, 0),
        -1,
    )
    frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    cv2.putText(frame, filename, (text_x, text_y), font, font_scale, color, thickness)
    return frame


def compose_horizontal(
    video_infos: List[dict],
    output_path: Path,
    show_filename: bool = True,
    loop_shorter: bool = True,
) -> None:
    """動画を横並びで結合"""
    output_width = sum(v["width"] for v in video_infos)
    output_height = max(v["height"] for v in video_infos)
    output_fps = min(v["fps"] for v in video_infos)
    output_frames = max(v["frame_count"] for v in video_infos)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        str(output_path), fourcc, output_fps, (output_width, output_height)
    )

    print(f"出力設定: {output_width}x{output_height}, {output_fps}fps, {output_frames}フレーム")

    for frame_num in range(output_frames):
        frames = []

        for info in video_infos:
            ret, frame = info["capture"].read()

            if not ret:
                if loop_shorter:
                    info["capture"].set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = info["capture"].read()
                else:
                    frame = np.zeros((info["height"], info["width"], 3), dtype=np.uint8)

            # 高さを揃える
            frame = cv2.resize(frame, (info["width"], output_height))

            if show_filename:
                frame = draw_filename_overlay(frame, info["path"].name)

            frames.append(frame)

        combined = np.hstack(frames)
        writer.write(combined)

        if frame_num % 100 == 0:
            print(f"処理中: {frame_num}/{output_frames} フレーム ({frame_num*100//output_frames}%)")

    writer.release()
    print(f"完了: {output_path}")


def compose_vertical(
    video_infos: List[dict],
    output_path: Path,
    show_filename: bool = True,
    loop_shorter: bool = True,
) -> None:
    """動画を縦並びで結合"""
    output_width = max(v["width"] for v in video_infos)
    output_height = sum(v["height"] for v in video_infos)
    output_fps = min(v["fps"] for v in video_infos)
    output_frames = max(v["frame_count"] for v in video_infos)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        str(output_path), fourcc, output_fps, (output_width, output_height)
    )

    print(f"出力設定: {output_width}x{output_height}, {output_fps}fps, {output_frames}フレーム")

    for frame_num in range(output_frames):
        frames = []

        for info in video_infos:
            ret, frame = info["capture"].read()

            if not ret:
                if loop_shorter:
                    info["capture"].set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = info["capture"].read()
                else:
                    frame = np.zeros((info["height"], info["width"], 3), dtype=np.uint8)

            # 幅を揃える
            frame = cv2.resize(frame, (output_width, info["height"]))

            if show_filename:
                frame = draw_filename_overlay(frame, info["path"].name)

            frames.append(frame)

        combined = np.vstack(frames)
        writer.write(combined)

        if frame_num % 100 == 0:
            print(f"処理中: {frame_num}/{output_frames} フレーム ({frame_num*100//output_frames}%)")

    writer.release()
    print(f"完了: {output_path}")


def compose_grid(
    video_infos: List[dict],
    output_path: Path,
    cols: int,
    rows: int,
    show_filename: bool = True,
    loop_shorter: bool = True,
) -> None:
    """動画をグリッド状に結合"""
    cell_width = max(v["width"] for v in video_infos)
    cell_height = max(v["height"] for v in video_infos)
    output_width = cell_width * cols
    output_height = cell_height * rows
    output_fps = min(v["fps"] for v in video_infos)
    output_frames = max(v["frame_count"] for v in video_infos)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        str(output_path), fourcc, output_fps, (output_width, output_height)
    )

    print(f"出力設定: {output_width}x{output_height} ({cols}x{rows}グリッド), {output_fps}fps")

    for frame_num in range(output_frames):
        grid_rows = []

        for row in range(rows):
            row_frames = []
            for col in range(cols):
                idx = row * cols + col

                if idx < len(video_infos):
                    info = video_infos[idx]
                    ret, frame = info["capture"].read()

                    if not ret:
                        if loop_shorter:
                            info["capture"].set(cv2.CAP_PROP_POS_FRAMES, 0)
                            ret, frame = info["capture"].read()
                        else:
                            frame = np.zeros((cell_height, cell_width, 3), dtype=np.uint8)

                    frame = cv2.resize(frame, (cell_width, cell_height))

                    if show_filename:
                        frame = draw_filename_overlay(frame, info["path"].name, font_scale=0.7)
                else:
                    frame = np.zeros((cell_height, cell_width, 3), dtype=np.uint8)

                row_frames.append(frame)

            grid_rows.append(np.hstack(row_frames))

        combined = np.vstack(grid_rows)
        writer.write(combined)

        if frame_num % 100 == 0:
            print(f"処理中: {frame_num}/{output_frames} フレーム ({frame_num*100//output_frames}%)")

    writer.release()
    print(f"完了: {output_path}")


def parse_grid_size(grid_str: str) -> Tuple[int, int]:
    """グリッドサイズをパース（例: '2x2' -> (2, 2)）"""
    try:
        cols, rows = grid_str.lower().split("x")
        return int(cols), int(rows)
    except ValueError:
        raise ValueError(f"無効なグリッドサイズ: {grid_str} (例: 2x2, 3x2)")


def main():
    parser = argparse.ArgumentParser(
        description="複数の動画を横並び・縦並び・グリッド状に結合するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s --horizontal                    # カレントディレクトリの動画を横並びで結合
  %(prog)s --vertical                      # 縦並びで結合
  %(prog)s --grid 2x2                      # 2x2グリッドで結合
  %(prog)s -i a.mp4 b.mp4 -o combined.mp4  # 入出力ファイルを指定
  %(prog)s --horizontal --no-filename      # ファイル名オーバーレイなし

注意:
  - OpenCV (opencv-python) と NumPy が必要です
  - 出力形式は MP4 (mp4v コーデック) です
        """,
    )

    # レイアウト選択（排他的）
    layout_group = parser.add_mutually_exclusive_group()
    layout_group.add_argument(
        "--horizontal", "-H",
        action="store_true",
        help="横並びで結合（デフォルト）",
    )
    layout_group.add_argument(
        "--vertical", "-V",
        action="store_true",
        help="縦並びで結合",
    )
    layout_group.add_argument(
        "--grid", "-G",
        type=str,
        metavar="COLSxROWS",
        help="グリッド状に結合（例: 2x2, 3x2）",
    )

    parser.add_argument(
        "-i", "--input",
        nargs="+",
        type=Path,
        default=None,
        help="入力動画ファイル（指定しない場合はカレントディレクトリの動画）",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="出力ファイル名（デフォルト: combined_YYYYMMDD.mp4）",
    )
    parser.add_argument(
        "--no-filename",
        action="store_true",
        help="ファイル名のオーバーレイを表示しない",
    )
    parser.add_argument(
        "--no-loop",
        action="store_true",
        help="短い動画をループさせない（黒画面で埋める）",
    )
    parser.add_argument(
        "--sort",
        choices=["name", "name-desc", "size", "none"],
        default="name",
        help="動画のソート順（デフォルト: name）",
    )

    args = parser.parse_args()

    # 入力動画を取得
    if args.input:
        video_files = [p.resolve() for p in args.input if p.exists()]
        if not video_files:
            print("エラー: 指定された動画ファイルが見つかりません")
            sys.exit(1)
    else:
        video_files = get_video_files(Path.cwd())
        if not video_files:
            print("エラー: カレントディレクトリに動画ファイルが見つかりません")
            sys.exit(1)

    # ソート
    if args.sort == "name":
        video_files.sort(key=lambda p: p.name)
    elif args.sort == "name-desc":
        video_files.sort(key=lambda p: p.name, reverse=True)
    elif args.sort == "size":
        video_files.sort(key=lambda p: p.stat().st_size, reverse=True)

    print(f"入力動画: {len(video_files)}件")
    for f in video_files:
        print(f"  - {f.name}")

    # 動画情報を取得
    try:
        video_infos = [get_video_info(f) for f in video_files]
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    # 出力ファイル名
    if args.output:
        output_path = args.output.resolve()
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        output_path = Path.cwd() / f"combined_{date_str}.mp4"

    print(f"出力ファイル: {output_path}")

    # 結合実行
    try:
        if args.grid:
            cols, rows = parse_grid_size(args.grid)
            compose_grid(
                video_infos,
                output_path,
                cols,
                rows,
                show_filename=not args.no_filename,
                loop_shorter=not args.no_loop,
            )
        elif args.vertical:
            compose_vertical(
                video_infos,
                output_path,
                show_filename=not args.no_filename,
                loop_shorter=not args.no_loop,
            )
        else:
            # デフォルトは横並び
            compose_horizontal(
                video_infos,
                output_path,
                show_filename=not args.no_filename,
                loop_shorter=not args.no_loop,
            )
    finally:
        # リソース解放
        for info in video_infos:
            info["capture"].release()


if __name__ == "__main__":
    main()
