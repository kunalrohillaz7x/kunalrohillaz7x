#!/usr/bin/env python3
"""
make_ascii_svg.py

Converts source-prepped.png (background-removed, contrast-boosted portrait)
into a monochrome ASCII-art SVG that "types" itself in row by row, like a
terminal. GitHub strips <script> from READMEs but renders SMIL/CSS animation
inside <img>-loaded SVGs, so all the motion lives in the SVG itself.

Tune these:
"""
import os
import numpy as np
from PIL import Image

INPUT = "source-prepped.png"
OUTPUT = "kunal-ascii.svg"

COLS = 110                  # ascii grid width (characters)
ASPECT_CORRECT = 0.55       # monospace chars are taller than wide -- corrects the grid
CONTRAST = 1.15
GAMMA = 0.9
WHITE_FLOOR = 8              # min brightness kept for lit subject pixels (0-255)
ALPHA_THRESHOLD = 40         # below this alpha -> treated as background (space char)

FONT_SIZE = 8
COLOR = "#8b949e"            # single monochrome gray -- never per-character rainbow

ROW_DUR = 0.9                # seconds for one row to finish "typing" across
STAGGER = 0.045              # delay added per row -- creates the cascading type-in

RAMP = " .:-=+*#%@"          # dark -> light density ramp

STATIC = os.environ.get("STATIC") == "1"   # STATIC=1 renders the final frame, no animation


def brightness_to_char(v):
    idx = int(v / 255 * (len(RAMP) - 1))
    return RAMP[max(0, min(len(RAMP) - 1, idx))]


def build_grid():
    img = Image.open(INPUT).convert("RGBA")
    w, h = img.size
    cell_w = w / COLS
    cell_h = cell_w / ASPECT_CORRECT
    rows = max(1, int(h / cell_h))
    small = img.resize((COLS, rows), Image.LANCZOS)
    arr = np.array(small).astype(np.float32)
    rgb = arr[..., :3]
    alpha = arr[..., 3]
    gray = rgb.mean(axis=2)
    gray = 255 * (gray / 255) ** GAMMA
    gray = (gray - 128) * CONTRAST + 128
    gray = np.clip(gray, WHITE_FLOOR, 255)

    grid = []
    for y in range(rows):
        row_chars = []
        for x in range(COLS):
            if alpha[y, x] < ALPHA_THRESHOLD:
                row_chars.append(" ")
            else:
                row_chars.append(brightness_to_char(gray[y, x]))
        grid.append("".join(row_chars))
    return grid


def esc(c):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(c, c)


def render_svg(grid):
    rows = len(grid)
    char_w = FONT_SIZE * 0.6
    char_h = FONT_SIZE * 1.0
    view_w = COLS * char_w
    view_h = rows * char_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w:.0f} {view_h:.0f}" '
        f'font-family="Menlo, Consolas, monospace" font-size="{FONT_SIZE}">'
    ]

    for i, row in enumerate(grid):
        row_text = "".join(esc(c) for c in row)
        y = (i + 1) * char_h - char_h * 0.25
        if STATIC:
            parts.append(f'<text x="0" y="{y:.1f}" fill="{COLOR}" xml:space="preserve">{row_text}</text>')
            continue
        clip_id = f"clip{i}"
        begin = i * STAGGER
        parts.append(
            f'<clipPath id="{clip_id}"><rect x="0" y="0" width="0" height="{char_h*2:.1f}">'
            f'<animate attributeName="width" from="0" to="{view_w:.1f}" '
            f'begin="{begin:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze" calcMode="linear"/>'
            f'</rect></clipPath>'
        )
        parts.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y:.1f}" fill="{COLOR}" xml:space="preserve">{row_text}</text></g>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    grid = build_grid()
    svg = render_svg(grid)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUTPUT}  ({COLS} cols x {len(grid)} rows)  STATIC={STATIC}")


if __name__ == "__main__":
    main()
