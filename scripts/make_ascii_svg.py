"""
make_ascii_svg.py — converts data/source-prepped.png → simon-ascii.svg
Each row wipes left-to-right; rows stagger top-to-bottom (prints once, freezes).

Usage:
    python scripts/make_ascii_svg.py
"""

from pathlib import Path
import numpy as np
from PIL import Image

# ── tunables ──────────────────────────────────────────────────────────────────
COLS       = 90          # character columns
CHAR_W     = 7.2         # px per character (monospace)
CHAR_H     = 14          # px per row
FONT_SIZE  = 12
FG_COLOR   = "#c9d1d9"   # GitHub dark-mode text colour
BG_COLOR   = "transparent"
RAMP       = " .`:-=+*cs#%@"   # bright → dark
ROW_DELAY  = 0.03        # seconds between row reveals
WIPE_DUR   = 0.25        # seconds per row wipe
SOURCE     = Path("data/source-prepped.png")
OUT        = Path("simon-ascii.svg")
# ─────────────────────────────────────────────────────────────────────────────


def img_to_chars(path: Path, cols: int) -> list[str]:
    img   = Image.open(path).convert("L")
    ratio = CHAR_H / CHAR_W            # characters are taller than wide
    rows  = int(cols * img.height / img.width / ratio)
    img   = img.resize((cols, rows), Image.LANCZOS)
    arr   = np.array(img)
    lines = []
    for row in arr:
        line = "".join(RAMP[int(p / 255 * (len(RAMP) - 1))] for p in row)
        lines.append(line)
    return lines


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(lines: list[str]) -> str:
    n_rows = len(lines)
    n_cols = max(len(l) for l in lines)
    width  = int(n_cols * CHAR_W)
    height = int(n_rows * CHAR_H)

    # total animation duration: last row starts at (n_rows-1)*ROW_DELAY and
    # takes WIPE_DUR to complete → add 1 s freeze buffer
    total  = n_rows * ROW_DELAY + WIPE_DUR + 1.0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     width="{width}" height="{height}"',
        f'     viewBox="0 0 {width} {height}">',
        f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>',
        f'  <style>',
        f'    .c {{ font-family: "SF Mono","Fira Code",monospace;',
        f'          font-size: {FONT_SIZE}px; fill: {FG_COLOR}; white-space: pre; }}',
        f'  </style>',
        f'  <defs>',
    ]

    # one clipPath per row — a rect that wipes from left to right
    for i in range(n_rows):
        y      = i * CHAR_H
        begin  = i * ROW_DELAY
        parts += [
            f'    <clipPath id="r{i}">',
            f'      <rect x="0" y="{y}" width="{width}" height="{CHAR_H}">',
            f'        <animate attributeName="width"',
            f'                 from="0" to="{width}"',
            f'                 dur="{WIPE_DUR:.2f}s"',
            f'                 begin="{begin:.3f}s"',
            f'                 fill="freeze"/>',
            f'      </rect>',
            f'    </clipPath>',
        ]

    parts.append('  </defs>')

    for i, line in enumerate(lines):
        y = (i + 1) * CHAR_H - 2   # baseline
        parts.append(
            f'  <text x="0" y="{y}" class="c"'
            f' clip-path="url(#r{i})">{escape(line)}</text>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"{SOURCE} not found — run prep_photo.py first."
        )
    lines = img_to_chars(SOURCE, COLS)
    svg   = build_svg(lines)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved → {OUT}  ({len(lines)} rows × {COLS} cols)")


if __name__ == "__main__":
    main()
