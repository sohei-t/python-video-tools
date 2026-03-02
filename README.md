# Python Video Tools

[![CI](https://github.com/sohei-t/python-video-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/sohei-t/python-video-tools/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive collection of 11 modular command-line utilities for video, audio, and image processing. Each tool is self-contained with its own dependencies and documentation, built on top of ffmpeg, OpenCV, and other established multimedia libraries.

---

## Table of Contents

- [Overview](#overview)
- [Tools](#tools)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Python Video Tools provides a toolkit of focused, single-purpose CLI utilities for common multimedia processing tasks. Rather than a monolithic application, each tool is an independent module that can be used in isolation or combined in shell pipelines for complex workflows.

Key design principles:

- **Modular** -- Each tool is self-contained in its own directory with dedicated dependencies
- **CLI-first** -- All tools are invoked from the command line with clear argument interfaces
- **Batch-capable** -- Tools support processing multiple files in a single invocation
- **Cross-platform** -- Compatible with macOS, Linux, and Windows (where dependencies are available)

---

## Tools

### Video Processing

| Tool | Description | Key Dependencies |
|------|-------------|------------------|
| [video-segment-tools](./video-segment-tools/) | Extract, split, and merge video segments by timestamp | ffmpeg |
| [video-grid-composer](./video-grid-composer/) | Compose multiple videos into side-by-side, stacked, or grid layouts | ffmpeg |
| [video-compressor](./video-compressor/) | Reduce video file size with configurable quality presets | ffmpeg |
| [video-speed-changer](./video-speed-changer/) | Adjust playback speed and frame rate | ffmpeg |
| [video-overlay](./video-overlay/) | Overlay images or videos onto a base video | moviepy |
| [video-player](./video-player/) | Browser-based video player with a Flask backend | Flask |

### Audio Processing

| Tool | Description | Key Dependencies |
|------|-------------|------------------|
| [audio-extractor](./audio-extractor/) | Extract audio tracks from video files as MP3 | ffmpeg |
| [audio-remover](./audio-remover/) | Strip audio tracks from video files | ffmpeg |

### Image Processing

| Tool | Description | Key Dependencies |
|------|-------------|------------------|
| [face-cropper](./face-cropper/) | Detect and crop faces from images, generate slideshows | dlib, OpenCV |
| [frame-extractor](./frame-extractor/) | Extract still frames from video at specified intervals | OpenCV |
| [image-combiner](./image-combiner/) | Combine multiple images in horizontal, vertical, or grid layouts | Pillow |

---

## Tech Stack

| Technology | Version | Role |
|-----------|---------|------|
| Python | 3.9+ | Runtime |
| ffmpeg | Latest | Video/audio encoding and manipulation |
| OpenCV | 4.x | Computer vision and frame extraction |
| moviepy | 1.x | Video compositing and overlay |
| dlib | Latest | Face detection |
| Pillow (PIL) | Latest | Image manipulation |
| NumPy | Latest | Numerical operations for image processing |
| Flask | Latest | Web-based video player backend |

---

## Prerequisites

### Python

Python 3.9 or later is required. Verify your installation:

```bash
python3 --version
```

### ffmpeg

Most tools depend on ffmpeg for video and audio processing.

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu / Debian:**

```bash
sudo apt install ffmpeg
```

**Windows:**

Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your system PATH.

### dlib (for face-cropper only)

The face-cropper tool requires dlib, which may need CMake for compilation:

**macOS:**

```bash
brew install cmake
pip install dlib
```

**Ubuntu / Debian:**

```bash
sudo apt install cmake libboost-all-dev
pip install dlib
```

---

## Installation

```bash
git clone https://github.com/sohei-t/python-video-tools.git
cd python-video-tools
```

Each tool manages its own dependencies. Install them per-tool as needed:

```bash
# Example: install dependencies for the face-cropper tool
cd face-cropper
pip install -r requirements.txt
```

Or install common dependencies for all tools:

```bash
pip install opencv-python numpy pillow moviepy flask dlib
```

---

## Usage Examples

### Extract audio from a video file

```bash
cd audio-extractor
python audio_extractor.py input.mp4 -o output.mp3
```

### Compress a video to reduce file size

```bash
cd video-compressor
python video_compressor.py input.mp4 -o compressed.mp4 --quality medium
```

### Create a 2x2 grid from four videos

```bash
cd video-grid-composer
python video_grid_composer.py video1.mp4 video2.mp4 video3.mp4 video4.mp4 -o grid.mp4 --layout 2x2
```

### Extract frames every 5 seconds

```bash
cd frame-extractor
python frame_extractor.py input.mp4 -o frames/ --interval 5
```

### Detect and crop faces from an image

```bash
cd face-cropper
python face_cropper.py photo.jpg -o faces/
```

### Change video playback speed

```bash
cd video-speed-changer
python video_speed_changer.py input.mp4 -o fast.mp4 --speed 2.0
```

### Combine images side by side

```bash
cd image-combiner
python image_combiner.py img1.png img2.png -o combined.png --direction horizontal
```

### Remove audio from a video

```bash
cd audio-remover
python audio_remover.py input.mp4 -o silent.mp4
```

---

## Testing

The project uses pytest for automated testing:

```bash
# Install test dependencies
pip install pytest pillow

# Run all tests
pytest tests/ -v
```

Tests are located in the `tests/` directory and cover core functionality for each tool.

---

## Contributing

Contributions are welcome. To add a new tool or improve an existing one:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-tool`
3. Add your tool in a new directory with its own `README.md` and `requirements.txt`
4. Add tests in the `tests/` directory
5. Ensure code passes formatting checks:

```bash
pip install black isort
black .
isort .
```

6. Open a pull request

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

**Author:** [@sohei-t](https://github.com/sohei-t)
