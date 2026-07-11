#!/usr/bin/env python3
"""
render_heatmap_svg.py

Reads data/contributions.json (written by fetch_contributions.py) and renders
contrib-heatmap.svg -- a GitHub-style grid of boxes that reveal cell by cell,
with a Less->More legend and real streak stats.
"""
import json
from datetime import datetime

INPUT = "data/contributions.json"
OUTPUT = "contrib-heatmap.svg"

CELL = 11
GAP = 3
RADIUS = 2
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]  # level 0..4
LABEL_COLOR = "#8b949e"
FONT = "Menlo, Consolas, monospace"

STAGGER_MAX = 2.4   # seconds -- spread of the cell-by-cell reveal


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    with open(INPUT) as f:
        data = json.load(f)
    days = data["days"]

    # bucket into weeks (columns) x day-of-week (rows), Sun=0 .. Sat=6
    weeks = []
    week = [None] * 7
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (dt.weekday() + 1) % 7
        if dow == 0 and any(week):
            weeks.append(week)
            week = [None] * 7
        week[dow] = d
    if any(week):
        weeks.append(week)

    cols = len(weeks)
    grid_w = cols * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    top_pad, bottom_pad, left_pad = 34, 40, 4
    view_w = grid_w + left_pad + 10
    view_h = top_pad + grid_h + bottom_pad

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w:.0f} {view_h:.0f}" '
        f'font-family="{FONT}" font-size="11">'
    ]

    header = (f'{data.get("active_days", 0)} active days &middot; '
              f'current streak {data.get("current_streak", 0)} &middot; '
              f'longest streak {data.get("longest_streak", 0)}')
    parts.append(f'<text x="{left_pad}" y="16" fill="{LABEL_COLOR}">{header}</text>')

    total_cells = sum(1 for week in weeks for d in week if d is not None)
    idx = 0
    for c, week in enumerate(weeks):
        for r, d in enumerate(week):
            if d is None:
                continue
            level = min(4, max(0, d.get("level", 0)))
            x = left_pad + c * (CELL + GAP)
            y = top_pad + r * (CELL + GAP)
            begin = (idx / max(1, total_cells)) * STAGGER_MAX
            idx += 1
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RADIUS}" '
                f'fill="{COLORS[level]}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" '
                f'dur="0.5s" fill="freeze"/>'
                f'<title>{esc(d["date"])}: level {level}</title>'
                f'</rect>'
            )

    ly = view_h - 16
    lx = left_pad
    parts.append(f'<text x="{lx}" y="{ly}" fill="{LABEL_COLOR}">Less</text>')
    lx += 34
    for color in COLORS:
        parts.append(f'<rect x="{lx}" y="{ly-10}" width="{CELL}" height="{CELL}" rx="{RADIUS}" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx+4}" y="{ly}" fill="{LABEL_COLOR}">More</text>')

    parts.append("</svg>")
    with open(OUTPUT, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUTPUT}  ({cols} weeks)")


if __name__ == "__main__":
    main()
