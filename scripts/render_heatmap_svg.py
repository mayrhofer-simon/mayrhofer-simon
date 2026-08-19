"""
render_heatmap_svg.py — reads data/contributions.json → contrib-heatmap.svg
Boxes reveal diagonally (slide-down), then freeze. No looping glow.

Usage:
    python scripts/render_heatmap_svg.py
    STATIC=1 python scripts/render_heatmap_svg.py   # frozen frame
"""

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

STATIC   = os.getenv("STATIC") == "1"
DATA     = Path("data/contributions.json")
OUT      = Path("contrib-heatmap.svg")

# ── layout ────────────────────────────────────────────────────────────────────
BOX      = 11    # box size px
GAP      = 3     # gap between boxes
WEEKS    = 53
DAYS     = 7
PAD_L    = 28    # left padding (day labels)
PAD_T    = 24    # top padding (month labels)
PAD_B    = 30    # bottom (stats footer)
PAD_R    = 12
WIDTH    = PAD_L + WEEKS * (BOX + GAP) - GAP + PAD_R
HEIGHT   = PAD_T + DAYS * (BOX + GAP) - GAP + PAD_B + 20

# ── colours ───────────────────────────────────────────────────────────────────
PALETTE  = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG       = "#0d1117"
FG       = "#c9d1d9"
DIM      = "#8b949e"
ACCENT   = "#EAFF00"
FONT     = '"SF Mono","Fira Code",monospace'

DAY_LABELS   = ["Mon", "", "Wed", "", "Fri", "", ""]
MONTH_NAMES  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


def load_data() -> tuple[dict, dict]:
    raw   = json.loads(DATA.read_text())
    days  = {d["date"]: d for d in raw["days"]}
    stats = raw["stats"]
    return days, stats


from typing import Optional


def weeks_grid(days: dict) -> list[list[Optional[dict]]]:
    """Return 53 columns × 7 rows, filling from today backwards."""
    today    = date.today()
    # align to the Sunday of the current week
    end_sun  = today + timedelta(days=(6 - today.weekday()) % 7 + 1)
    start    = end_sun - timedelta(weeks=WEEKS)

    grid: list[list[dict | None]] = []
    cur = start
    while cur <= end_sun:
        week = []
        for _ in range(7):
            key  = cur.strftime("%Y-%m-%d")
            week.append(days.get(key))
            cur += timedelta(days=1)
        grid.append(week)

    return grid[:WEEKS]


def build(days: dict, stats: dict) -> str:
    grid = weeks_grid(days)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}">',
        f'  <rect width="100%" height="100%" fill="{BG}"/>',
    ]

    # ── month labels ──────────────────────────────────────────────────────────
    prev_month = -1
    for wi, week in enumerate(grid):
        for cell in week:
            if cell is None:
                continue
            m = datetime.strptime(cell["date"], "%Y-%m-%d").month
            if m != prev_month:
                x = PAD_L + wi * (BOX + GAP)
                parts.append(
                    f'  <text x="{x}" y="{PAD_T - 6}" font-family={FONT!r} '
                    f'font-size="10" fill="{DIM}">{MONTH_NAMES[m-1]}</text>'
                )
                prev_month = m
            break

    # ── day labels ────────────────────────────────────────────────────────────
    for di, label in enumerate(DAY_LABELS):
        if label:
            y = PAD_T + di * (BOX + GAP) + BOX - 2
            parts.append(
                f'  <text x="{PAD_L - 4}" y="{y}" font-family={FONT!r} '
                f'font-size="9" fill="{DIM}" text-anchor="end">{label}</text>'
            )

    # ── boxes ─────────────────────────────────────────────────────────────────
    anim_idx = 0
    for wi, week in enumerate(grid):
        for di, cell in enumerate(week):
            x      = PAD_L + wi * (BOX + GAP)
            y      = PAD_T + di * (BOX + GAP)
            level  = cell["level"] if cell else 0
            color  = PALETTE[min(level, len(PALETTE) - 1)]
            tip    = cell["date"] if cell else ""

            if STATIC:
                parts.append(
                    f'  <rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                    f'rx="2" fill="{color}"><title>{tip}</title></rect>'
                )
            else:
                # diagonal reveal: column + row index as delay
                delay  = (wi + di) * 0.012
                anim_idx += 1
                parts.append(
                    f'  <rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                    f'rx="2" fill="{color}" opacity="0"><title>{tip}</title>'
                    f'<animate attributeName="opacity" from="0" to="1" '
                    f'dur="0.18s" begin="{delay:.3f}s" fill="freeze"/>'
                    f'</rect>'
                )

    # ── legend ────────────────────────────────────────────────────────────────
    legend_y = PAD_T + DAYS * (BOX + GAP) + 8
    parts.append(
        f'  <text x="{PAD_L}" y="{legend_y + BOX - 1}" font-family={FONT!r} '
        f'font-size="9" fill="{DIM}">Less</text>'
    )
    for li, color in enumerate(PALETTE):
        lx = PAD_L + 30 + li * (BOX + 2)
        parts.append(
            f'  <rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" '
            f'rx="2" fill="{color}"/>'
        )
    more_x = PAD_L + 30 + len(PALETTE) * (BOX + 2) + 4
    parts.append(
        f'  <text x="{more_x}" y="{legend_y + BOX - 1}" font-family={FONT!r} '
        f'font-size="9" fill="{DIM}">More</text>'
    )

    # ── stats footer ──────────────────────────────────────────────────────────
    stats_y = legend_y + BOX + 14
    total   = stats.get("total", 0)
    streak  = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)

    footer = (
        f'{total:,} contributions in the last year  ·  '
        f'current streak: {streak}d  ·  longest: {longest}d'
    )
    parts.append(
        f'  <text x="{WIDTH // 2}" y="{stats_y}" font-family={FONT!r} '
        f'font-size="10" fill="{DIM}" text-anchor="middle">{footer}</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    if not DATA.exists():
        raise FileNotFoundError(f"{DATA} not found — run fetch_contributions.py first.")
    days, stats = load_data()
    svg = build(days, stats)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved → {OUT}  ({stats.get('total',0):,} contributions)")


if __name__ == "__main__":
    main()
