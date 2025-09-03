# AsciiPlayer

AsciiPlayer is a Python-based tool that transforms your videos into fully playable ASCII art while preserving the original audio. Watch your favorite videos in a retro, code-inspired style!  

## Features

- Convert any video to **ASCII art**  
- Preserve **original audio**  
- Adjustable **output width** for detail vs performance  
- Choose between **green-only** or **full RGB color**  

## Requirements

- Python 3.8+  
- [ffmpeg](https://ffmpeg.org/) (for audio merging)  
- Python packages:
  - `opencv-python`
  - `numpy`
  - `Pillow`

> Note: If you are using the standalone `.exe`, no Python installation is needed, but `ffmpeg.exe` should be in the same folder or available in PATH.  

## Installation (Python)

1. Clone the repository or download the script:
   ```bash
   git clone https://github.com/yourusername/AsciiPlayer.git
   cd AsciiPlayer

2.Install required Python packages:
    ```bash
         pip install opencv-python numpy Pillow
               

3.Run the script from the terminal:
  ```bash
        python AsciiPlayer.py
