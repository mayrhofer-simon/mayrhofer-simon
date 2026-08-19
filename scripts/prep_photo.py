"""
prep_photo.py — background removal + contrast boost → source-prepped.png
Run once whenever you change your source photo.

Usage:
    python scripts/prep_photo.py simon-mayrhofer.webp
"""

import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
from rembg import remove

SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("simon-mayrhofer.webp")
OUT    = Path("data/source-prepped.png")

def main() -> None:
    # 1. Remove background
    with open(SOURCE, "rb") as f:
        raw = remove(f.read())

    img = Image.open(__import__("io").BytesIO(raw)).convert("RGBA")

    # 2. Composite onto pure white
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    gray = bg.convert("L")

    # 3. CLAHE contrast boost
    arr = np.array(gray)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(enhanced).save(OUT)
    print(f"Saved → {OUT}")

if __name__ == "__main__":
    main()
