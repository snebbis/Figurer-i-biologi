"""
Bildekollasj: De syv livsprosessene
Lager et 4+3 grid med bokstavlabels (a)-(g).
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# ──────────────────────────────────────────────
# FILSTIER (samme mappe som scriptet)
# ──────────────────────────────────────────────
base_dir = os.path.dirname(__file__)

image_paths = [
    os.path.join(base_dir, "1.jpg"),
    os.path.join(base_dir, "2.jpg"),
    os.path.join(base_dir, "3.jpg"),
    os.path.join(base_dir, "4.jpg"),
    os.path.join(base_dir, "5.png"),  # eneste PNG
    os.path.join(base_dir, "6.jpg"),
    os.path.join(base_dir, "7.jpg"),
]

labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)']

# ──────────────────────────────────────────────
# LAST INN BILDER (med feilsjekk)
# ──────────────────────────────────────────────
images = []
for path in image_paths:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Finner ikke fil: {path}")
    images.append(Image.open(path))

# ──────────────────────────────────────────────
# CROP TIL KVADRAT (center crop)
# ──────────────────────────────────────────────
def center_crop_square(img):
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))

images_sq = [center_crop_square(img) for img in images]

# ──────────────────────────────────────────────
# LAYOUT: 4 oppe, 3 nede (sentrert)
# ──────────────────────────────────────────────
cell_size = 3.0  # inches per bilde
gap = 0.12       # mellomrom
ncols = 4

fig_w = ncols * cell_size + (ncols - 1) * gap
fig_h = 2 * cell_size + gap

fig = plt.figure(figsize=(fig_w, fig_h), facecolor='white')

# ──────────────────────────────────────────────
# TOPP-RAD (4 bilder)
# ──────────────────────────────────────────────
for i in range(4):
    x = (i * (cell_size + gap)) / fig_w
    y = (cell_size + gap) / fig_h
    w = cell_size / fig_w
    h = cell_size / fig_h

    ax = fig.add_axes([x, y, w, h])
    ax.imshow(np.array(images_sq[i]))
    ax.axis('off')

    ax.text(
        0.04, 0.96, labels[i],
        transform=ax.transAxes,
        fontsize=16,
        fontweight='bold',
        color='white',
        va='top',
        ha='left',
        bbox=dict(
            facecolor='black',
            alpha=0.6,
            boxstyle='round,pad=0.25',
            edgecolor='none'
        )
    )

# ──────────────────────────────────────────────
# BUNN-RAD (3 bilder, sentrert)
# ──────────────────────────────────────────────
offset_x = (fig_w - (3 * cell_size + 2 * gap)) / 2

for i in range(3):
    x = (offset_x + i * (cell_size + gap)) / fig_w
    y = 0
    w = cell_size / fig_w
    h = cell_size / fig_h

    ax = fig.add_axes([x, y, w, h])
    ax.imshow(np.array(images_sq[4 + i]))
    ax.axis('off')

    ax.text(
        0.04, 0.96, labels[4 + i],
        transform=ax.transAxes,
        fontsize=16,
        fontweight='bold',
        color='white',
        va='top',
        ha='left',
        bbox=dict(
            facecolor='black',
            alpha=0.6,
            boxstyle='round,pad=0.25',
            edgecolor='none'
        )
    )

# ──────────────────────────────────────────────
# LAGRE FIL
# ──────────────────────────────────────────────
output_path = os.path.join(base_dir, "fig_livsprosesser_kollasj.png")

fig.savefig(
    output_path,
    dpi=300,
    bbox_inches='tight',
    facecolor='white',
    edgecolor='none',
    pad_inches=0.05
)

print(f"Kollasj lagret som: {output_path}")

plt.close()