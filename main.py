import sys
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ------------------ Console Input ------------------
input_filename = input("Enter input filename (without extension): ").strip()
output_filename = input("Enter output filename (without extension, optional): ").strip()
width_input = input("Enter ASCII width (default 160): ").strip()
color_mode = input("Choose color mode: 1) Green only  2) Full RGB (default 2): ").strip()

# ------------------ Determine input path ------------------
input_path = None
for ext in ['.mp4', '.avi', '.mov', '.mkv']:
    if Path(input_filename + ext).exists():
        input_path = Path(input_filename + ext)
        break
if input_path is None:
    sys.exit("Input file not found!")

# ------------------ Determine output path ------------------
if not output_filename:
    output_path = input_path.with_name(input_path.stem + "_ascii.mp4")
else:
    output_path = Path(output_filename + ".mp4")

# ------------------ Parameters ------------------
ascii_width = 160
if width_input:
    try:
        ascii_width = max(4, int(width_input))
    except ValueError:
        print("Invalid width, using default 160")

charset = " .:-=+*#%@"
char_aspect = 2.0  # typical console font aspect ratio
font = ImageFont.load_default()

# Determine color mode
if color_mode != "1":
    use_rgb = True
else:
    use_rgb = False

# ------------------ Video Setup ------------------
cap = cv2.VideoCapture(str(input_path))
if not cap.isOpened():
    sys.exit("Failed to open input video")

src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
src_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
ascii_h = max(2, int(round((src_h / src_w) * ascii_width / char_aspect)))

# Measure character size
dummy_img = Image.new("RGB", (100, 100))
dummy_draw = ImageDraw.Draw(dummy_img)
bbox = dummy_draw.textbbox((0, 0), "A", font=font)
char_w = max(1, bbox[2]-bbox[0])
char_h = max(1, bbox[3]-bbox[1])
out_w = char_w * ascii_width
out_h = char_h * ascii_h

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(str(output_path), fourcc, src_fps, (out_w, out_h))
if not writer.isOpened():
    sys.exit("Failed to open output video writer")

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
processed = 0

# ------------------ ASCII Conversion Loop ------------------
try:
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # Resize frame to ASCII grid
        small = cv2.resize(frame, (ascii_width, ascii_h), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        indices = (gray / 256.0 * len(charset)).astype(int)
        indices = np.clip(indices, 0, len(charset)-1)

        # Create output image
        img = Image.new("RGB", (out_w, out_h), color=(0,0,0))
        draw = ImageDraw.Draw(img)

        for y in range(ascii_h):
            for x in range(ascii_width):
                char = charset[indices[y, x]]
                if use_rgb:
                    b, g, r = small[y, x]  # BGR from cv2 frame
                    fill_color = (r, g, b)
                else:
                    fill_color = (0, 255, 0)  # green only
                draw.text((x*char_w, y*char_h), char, font=font, fill=fill_color)

        # Write frame
        bgr_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        writer.write(bgr_frame)

        processed += 1
        if frame_count and processed % 50 == 0:
            pct = 100.0 * processed / frame_count
            print(f"Frames: {processed}/{frame_count} ({pct:.1f}%)")
finally:
    cap.release()
    writer.release()

# ------------------ Audio Muxing ------------------
temp_path = output_path.with_name(output_path.stem + "_temp.mp4")
output_path.rename(temp_path)

cmd = [
    "ffmpeg",
    "-y",
    "-i", str(temp_path),
    "-i", str(input_path),
    "-c:v", "copy",
    "-c:a", "aac",
    "-map", "0:v:0",
    "-map", "1:a:0",
    str(output_path)
]
subprocess.run(cmd)
Path(temp_path).unlink()
print(f"Done! ASCII video saved to: {output_path}")
