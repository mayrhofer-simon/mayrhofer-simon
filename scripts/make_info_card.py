"""
make_info_card.py — generates info-card.svg (neofetch-style panel)
Each line fades + slides in with a short stagger; freezes after.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame for preview
"""

import os
from pathlib import Path

STATIC = os.getenv("STATIC") == "1"
OUT    = Path("info-card.svg")

ACCENT  = "#EAFF00"   # your brand yellow
DIM     = "#8b949e"
FG      = "#c9d1d9"
BG      = "#0d1117"
BORDER  = "#30363d"

WIDTH   = 490
FONT    = '"SF Mono","Fira Code",monospace'

LINES = [
    ("title",  "simon@github"),
    ("sep",    "─" * 28),
    ("kv",     ("os",        "design.engineer")),
    ("kv",     ("location",  "graz, austria — 47.07°N")),
    ("kv",     ("role",      "founder · builder · 0→1")),
    ("blank",  ""),
    ("kv",     ("now",       "mooveo — @getmooveo")),
    ("kv",     ("also",      "veloom · simon-mayrhofer.com")),
    ("blank",  ""),
    ("label",  "stack"),
    ("plain",  "typescript · react · next.js · tailwind"),
    ("plain",  "go · node.js · postgres · firebase"),
    ("plain",  "figma · docker · php · wordpress"),
    ("blank",  ""),
    ("label",  "by the numbers"),
    ("plain",  "10+ yrs shipping  ·  5+ products live"),
    ("plain",  "10k+ bookings  ·  0 handoffs"),
    ("blank",  ""),
    ("kv",     ("contact",   "hi@simon-mayrhofer.com")),
]

LINE_H   = 22
PAD_X    = 18
PAD_Y    = 20
TITLE_H  = 36
HEIGHT   = TITLE_H + PAD_Y + len(LINES) * LINE_H + PAD_Y


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def animate(i: int, prop: str = "opacity", frm: str = "0", to: str = "1",
            dur: float = 0.25, delay_step: float = 0.06) -> str:
    if STATIC:
        return ""
    begin = i * delay_step
    return (
        f'<animate attributeName="{prop}" from="{frm}" to="{to}" '
        f'dur="{dur:.2f}s" begin="{begin:.3f}s" fill="freeze"/>'
    )


def build() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}">',
        f'  <rect width="100%" height="100%" fill="{BG}" rx="6"/>',
        f'  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" '
        f'fill="none" stroke="{BORDER}" stroke-width="1" rx="6"/>',
        # title bar
        f'  <rect x="0" y="0" width="{WIDTH}" height="{TITLE_H}" '
        f'fill="{BORDER}" rx="6"/>',
        f'  <rect x="0" y="18" width="{WIDTH}" height="18" fill="{BORDER}"/>',
        # traffic-light dots
        f'  <circle cx="16" cy="18" r="5" fill="#ff5f57"/>',
        f'  <circle cx="32" cy="18" r="5" fill="#febc2e"/>',
        f'  <circle cx="48" cy="18" r="5" fill="#28c840"/>',
        # title text
        f'  <text x="{WIDTH//2}" y="23" text-anchor="middle" '
        f'font-family={FONT!r} font-size="12" fill="{FG}">{esc("simon@github — info-card")}</text>',
    ]

    for idx, (kind, val) in enumerate(LINES):
        y      = TITLE_H + PAD_Y + idx * LINE_H
        anim   = animate(idx)
        opaque = ' opacity="1"' if STATIC else ' opacity="0"'

        if kind == "blank":
            continue

        elif kind == "sep":
            parts.append(
                f'  <text x="{PAD_X}" y="{y}" font-family={FONT!r} '
                f'font-size="12" fill="{BORDER}"{opaque}>'
                f'{esc(val)}{anim}</text>'
            )

        elif kind == "title":
            parts.append(
                f'  <text x="{PAD_X}" y="{y}" font-family={FONT!r} '
                f'font-size="13" font-weight="700" fill="{ACCENT}"{opaque}>'
                f'{esc(val)}{anim}</text>'
            )

        elif kind == "label":
            parts.append(
                f'  <text x="{PAD_X}" y="{y}" font-family={FONT!r} '
                f'font-size="11" font-weight="600" fill="{ACCENT}"{opaque}>'
                f'{esc(val.upper())}{anim}</text>'
            )

        elif kind == "plain":
            parts.append(
                f'  <text x="{PAD_X + 12}" y="{y}" font-family={FONT!r} '
                f'font-size="12" fill="{DIM}"{opaque}>'
                f'{esc(val)}{anim}</text>'
            )

        elif kind == "kv":
            key, value = val
            key_w = len(key) * 7 + 8
            parts += [
                f'  <text x="{PAD_X}" y="{y}" font-family={FONT!r} '
                f'font-size="12" fill="{ACCENT}"{opaque}>'
                f'{esc(key)}{anim}</text>',
                f'  <text x="{PAD_X + key_w + 8}" y="{y}" font-family={FONT!r} '
                f'font-size="12" fill="{FG}"{opaque}>'
                f'{esc(str(value))}{anim}</text>',
            ]

    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    OUT.write_text(build(), encoding="utf-8")
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()
