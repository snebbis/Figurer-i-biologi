"""
Bildekollasj: De syv livsprosessene (REN VERTIKAL KOLONNE)
Alle bildene i én kolonne langs venstresiden av en A4-side.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# ──────────────────────────────────────────────
# FILSTIER
# ──────────────────────────────────────────────
base_dir = os.path.dirname(__file__)

image_paths = [
    os.path.join(base_dir, "1.jpg"),
    os.path.join(base_dir, "2.jpg"),
    os.path.join(base_dir, "3.jpg"),
    os.path.join(base_dir, "4.jpg"),
    os.path.join(base_dir, "5.png"),
    os.path.join(base_dir, "6.jpg"),
    os.path.join(base_dir, "7.jpg"),
]

labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)']

# ──────────────────────────────────────────────
# LAST INN BILDER
# ──────────────────────────────────────────────
images = []
for path in image_paths:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Finner ikke fil: {path}")
    images.append(Image.open(path))

# ──────────────────────────────────────────────
# CROP TIL KVADRAT
# ──────────────────────────────────────────────
def center_crop_square(img):
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))

images_sq = [center_crop_square(img) for img in images]

# ──────────────────────────────────────────────
# A4 FORMAT (stående)
# ──────────────────────────────────────────────
A4_width = 8.27
A4_height = 11.69

fig = plt.figure(figsize=(A4_width, A4_height), facecolor='white')

# ──────────────────────────────────────────────
# KOLLASJ (én kolonne til venstre)
# ──────────────────────────────────────────────
left_margin = 0.05
bottom_margin = 0.04
top_margin = 0.04

collage_width = 0.35   # smal kolonne → plass til tekst til høyre
usable_height = 1 - bottom_margin - top_margin

n = 7
gap = 0.01

cell_h = (usable_height - (n - 1) * gap) / n

# ──────────────────────────────────────────────
# TEGN BILDENE (én kolonne)
# ──────────────────────────────────────────────
for i in range(n):
    y = 1 - top_margin - (i + 1) * cell_h - i * gap
    x = left_margin

    ax = fig.add_axes([x, y, collage_width, cell_h])
    ax.imshow(np.array(images_sq[i]))
    ax.axis('off')

    ax.text(
        0.03, 0.95, labels[i],
        transform=ax.transAxes,
        fontsize=12,
        fontweight='bold',
        color='white',
        va='top',
        ha='left',
        bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.2', edgecolor='none')
    )

# ──────────────────────────────────────────────
# LAGRE
# ──────────────────────────────────────────────
output_path = os.path.join(base_dir, "fig_livsprosesser_kolonne.png")

fig.savefig(
    output_path,
    dpi=300,
    bbox_inches='tight',
    facecolor='white',
    edgecolor='none'
)

print(f"Lagret: {output_path}")

plt.close()