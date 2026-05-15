import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# =========================
# SETTINGS
# =========================
IMAGE_FILE = 'petriskål_kap1.png'
OUTPUT_FILE = 'fig_kvalitativ_kvantitativ.png'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 13
})

# =========================
# LOAD IMAGE
# =========================
img = Image.open(IMAGE_FILE)
img_arr = np.array(img)
h, w = img_arr.shape[:2]

# =========================
# FIGURE SETUP
# =========================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7.5), facecolor='white')
fig.subplots_adjust(top=0.88, bottom=0.02, left=0.02, right=0.98, wspace=0.12)

# =========================
# LEFT: KVALITATIV
# =========================
ax1.imshow(img_arr)
ax1.set_title('Kvalitativ beskrivelse', fontsize=20, fontweight='bold', pad=15, color='#2B6E52')
ax1.axis('off')

qual_items = [
    (0.18*w, 0.08*h, "«Mange kolonier\nover hele skålen»"),
    (0.82*w, 0.10*h, "«Koloniene er runde\nog blanke»"),
    (0.15*w, 0.92*h, "«Varierende\nstørrelser»"),
    (0.82*w, 0.92*h, "«Stort sett godt\nadskilte kolonier»"),
]

for x, y, text in qual_items:
    ax1.annotate(
        text,
        xy=(x, y),
        fontsize=13,
        ha='center',
        va='center',
        color='#1B5E20',
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor='#E8F5E9',
            edgecolor='#4CAF50',
            alpha=0.95,
            linewidth=1.5
        )
    )

# =========================
# RIGHT: KVANTITATIV
# =========================
ax2.imshow(img_arr)
ax2.set_title('Kvantitativ analyse', fontsize=20, fontweight='bold', pad=15, color='#1565C0')
ax2.axis('off')

quant_items = [
    (0.50*w, 0.05*h, "Estimert antall kolonier: ~140"),
    (0.15*w, 0.20*h, "Gjennomsnittlig\ndiameter: ~1,8 mm"),
    (0.85*w, 0.25*h, "Dekningsgrad:\n~18 %"),
    (0.50*w, 0.95*h, "Areal per koloni:\n0,8–19,6 mm²"),
]

for x, y, text in quant_items:
    ax2.annotate(
        text,
        xy=(x, y),
        fontsize=13,
        ha='center',
        va='center',
        color='#0D47A1',
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor='#E3F2FD',
            edgecolor='#1976D2',
            alpha=0.95,
            linewidth=1.5
        )
    )

# =========================
# MEASUREMENT BRACKETS  |____|
# =========================

def draw_measurement_bracket(ax, x_center, y_colony_bottom, half_width,
                             tick_height, label,
                             color='#D32F2F', lw=2.5,
                             gap=0, label_offset=18, fontsize=13):
    """
    Draw a |____| bracket below a colony, with a label below the bracket.
    The bracket is open at the top so the colony sits just inside the opening.
    """
    x_left = x_center - half_width
    x_right = x_center + half_width
    y_top_of_bars = y_colony_bottom + gap          # tops of the vertical bars (just below colony)
    y_horizontal = y_top_of_bars + tick_height     # bottom horizontal line

    # Two vertical bars
    ax.plot([x_left, x_left], [y_top_of_bars, y_horizontal],
            color=color, lw=lw, solid_capstyle='round', zorder=5)
    ax.plot([x_right, x_right], [y_top_of_bars, y_horizontal],
            color=color, lw=lw, solid_capstyle='round', zorder=5)
    # Bottom horizontal line
    ax.plot([x_left, x_right], [y_horizontal, y_horizontal],
            color=color, lw=lw, solid_capstyle='round', zorder=5)

    # Label below bracket
    ax.text(
        x_center, y_horizontal + label_offset,
        label,
        ha='center', va='top',
        fontsize=fontsize, fontweight='bold', color=color,
        bbox=dict(facecolor='white', edgecolor=color,
                  alpha=0.95, pad=4, linewidth=1.5),
        zorder=6
    )

# Large yellow colony on the left side  (centroid (381, 521), ~5 mm)
cx1, cy1 = 0.304*w, 0.415*h
r1 = 0.029*w           # half-width = colony radius
draw_measurement_bracket(
    ax2,
    x_center=cx1,
    y_colony_bottom=cy1 + r1,
    half_width=r1,
    tick_height=0.018*h,
    label='~5 mm',
    fontsize=13,
)

# Smaller yellow colony near the centre  (centroid (578, 668), ~4 mm)
cx2, cy2 = 0.461*w, 0.532*h
r2 = 0.027*w
draw_measurement_bracket(
    ax2,
    x_center=cx2,
    y_colony_bottom=cy2 + r2,
    half_width=r2,
    tick_height=0.016*h,
    label='~4 mm',
    fontsize=12,
)

# =========================
# SAVE FIGURE
# =========================
fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches='tight',
    facecolor='white',
    edgecolor='none'
)

print(f"Figure saved as {OUTPUT_FILE}")

plt.close()
