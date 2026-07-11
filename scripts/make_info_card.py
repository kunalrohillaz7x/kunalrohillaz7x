#!/usr/bin/env python3
"""
make_info_card.py

Renders a neofetch-style info panel SVG from ROWS below. Edit ROWS + HOST,
then run `python scripts/make_info_card.py` -> info-card.svg.
"""

HOST = "kunalrohillaz7x@github"

ROWS = [
    ("Role", "CSE Student @ IIIT Sonepat"),
    ("Focus", "Backend Engineering + DSA"),
    ("Languages", "C++, Python, JavaScript"),
    ("Backend", "FastAPI, PostgreSQL, SQLAlchemy"),
    ("Tools", "Git, GitHub, VS Code"),
    ("Building", "REST APIs & Backend Projects"),
    ("Learning", "Open Source Development"),
    ("LeetCode", "Kunal_Rohilla"),
]

OUTPUT = "info-card.svg"

W = 490
H = 300              # bump if content overflows; re-match width= in the README table if changed
PAD_X = 24
PAD_TOP = 30
LINE_H = 25.5
LABEL_COLOR = "#8b949e"
VALUE_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
ACCENT = "#58a6ff"
FONT = "Menlo, Consolas, monospace"
FONT_SIZE = 13.5
LABEL_COL_CHARS = max(len(l) for l, _ in ROWS) + 2


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}" font-size="{FONT_SIZE}">',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
    ]

    y = PAD_TOP
    lines.append(f'<text x="{PAD_X}" y="{y}" fill="{ACCENT}" font-weight="bold">{esc(HOST)}</text>')
    y += LINE_H * 0.55
    lines.append(f'<line x1="{PAD_X}" y1="{y:.1f}" x2="{W-PAD_X}" y2="{y:.1f}" stroke="{BORDER}"/>')
    y += LINE_H

    value_x = PAD_X + LABEL_COL_CHARS * 8.15
    for i, (label, value) in enumerate(ROWS):
        row_y = y + i * LINE_H
        begin = 0.15 + i * 0.06
        lines.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<text x="{PAD_X}" y="{row_y:.1f}" fill="{LABEL_COLOR}">{esc(label)}</text>'
            f'<text x="{value_x:.1f}" y="{row_y:.1f}" fill="{VALUE_COLOR}">{esc(value)}</text>'
            f'</g>'
        )

    lines.append("</svg>")
    with open(OUTPUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
