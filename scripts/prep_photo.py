#!/usr/bin/env python3
"""
prep_photo.py <input.jpg> <output.png>

One-time local prep: removes the background and boosts local contrast (CLAHE)
so the subject sits on blank space with real highlights/shadows instead of
being a dark blob.

Note: uses OpenCV GrabCut for background removal. rembg (listed in
requirements-local.txt) generally gives a cleaner cutout -- swap it in below
if you have network access; it needs to download model weights on first run.
"""
import sys
import cv2
import numpy as np

CLIP_LIMIT = 3.0     # CLAHE clip limit -- raise for punchier local contrast
TILE_GRID = (8, 8)


def remove_background(img):
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    rect = (int(w * 0.04), int(h * 0.02), int(w * 0.92), int(h * 0.97))
    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 8, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    mask2 = cv2.GaussianBlur(mask2.astype(np.float32), (5, 5), 0)
    b, g, r = cv2.split(img)
    alpha = (mask2 * 255).astype(np.uint8)
    return cv2.merge([b, g, r, alpha])


def clahe_contrast(bgr):
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=TILE_GRID)
    l2 = clahe.apply(l)
    lab2 = cv2.merge([l2, a, b])
    return cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)


def main():
    if len(sys.argv) != 3:
        print("usage: prep_photo.py <input> <output.png>")
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    img = cv2.imread(src, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f"could not read {src}")
    img = clahe_contrast(img)
    rgba = remove_background(img)
    cv2.imwrite(dst, rgba)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
