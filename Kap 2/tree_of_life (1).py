# Figur: Tre-domene-treet — kun linjer, ingen tekst
# =================================================
#
# BRUK:  python tree_of_life.py
# KRAV:  pip install matplotlib numpy scipy

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
from matplotlib.path import Path as MplPath
import numpy as np
from pathlib import Path
from scipy.interpolate import CubicSpline

# ══════════════════════════════════════════════
# INNSTILLINGER
# ══════════════════════════════════════════════
FIG_W, FIG_H = 14, 16
DPI          = 300
OUTPUT_FILE  = Path(__file__).parent / "fig_tree_of_life.png"
BG_COLOR     = '#FAFAFA'

COL_BAK   = '#F5E6C8'
COL_ERK   = '#F2CAC8'
COL_EUK   = '#C8D8EE'

BRANCH_COL = '#3A5A90'

# 🔥 TYKKERE LINJER
BRANCH_LW = 3.5
STEM_LW   = 5.5


# ══════════════════════════════════════════════
# HJELPEFUNKSJONER
# ══════════════════════════════════════════════

def smooth_curve(points, n=80):
    pts = np.array(points, dtype=float)
    if len(pts) < 2:
        return pts
    t = np.linspace(0, 1, len(pts))
    t_fine = np.linspace(0, 1, n)
    cs_x = CubicSpline(t, pts[:, 0], bc_type='natural')
    cs_y = CubicSpline(t, pts[:, 1], bc_type='natural')
    return np.column_stack([cs_x(t_fine), cs_y(t_fine)])


def draw_smooth(ax, points, n=80, **kwargs):
    defaults = dict(color=BRANCH_COL, lw=BRANCH_LW,
                    solid_capstyle='round', solid_joinstyle='round', zorder=3)
    defaults.update(kwargs)
    xy = smooth_curve(points, n)
    ax.plot(xy[:, 0], xy[:, 1], **defaults)


def make_closed_path(points):
    pts = list(points) + [points[0]]
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 1)
    return MplPath(pts, codes)


def interp_border(border_pts, n=60):
    pts = np.array(border_pts, dtype=float)
    t = np.linspace(0, 1, len(pts))
    t_fine = np.linspace(0, 1, n)
    cs_x = CubicSpline(t, pts[:, 0], bc_type='natural')
    cs_y = CubicSpline(t, pts[:, 1], bc_type='natural')
    return list(zip(cs_x(t_fine), cs_y(t_fine)))


# ══════════════════════════════════════════════
# FIGUR
# ══════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI, facecolor=BG_COLOR)
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.2, 15.5)
ax.set_aspect('equal')
ax.axis('off')
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)


# ══════════════════════════════════════════════
# 1. BAKGRUNNSOMRÅDER
# ══════════════════════════════════════════════
Y_BOT = 4.0
Y_TOP = 15.0

be_border = [(3.1, Y_BOT), (3.0, 6.0), (2.9, 8.0), (3.1, 10.0),
             (3.1, 12.0), (3.0, Y_TOP)]
ee_border = [(4.7, Y_BOT), (4.8, 6.0), (4.9, 8.0), (4.7, 10.0),
             (4.6, 12.0), (4.7, Y_TOP)]

be_smooth = interp_border(be_border)
ee_smooth = interp_border(ee_border)

bak_verts = ([(-0.3, Y_BOT)] + be_smooth +
             [(be_smooth[-1][0], Y_TOP), (-0.3, Y_TOP)])
ax.add_patch(mpatches.PathPatch(make_closed_path(bak_verts),
             facecolor=COL_BAK, alpha=0.32, edgecolor='none', zorder=0))

erk_verts = (list(be_smooth) +
             [(be_smooth[-1][0], Y_TOP), (ee_smooth[-1][0], Y_TOP)] +
             list(reversed(ee_smooth)))
ax.add_patch(mpatches.PathPatch(make_closed_path(erk_verts),
             facecolor=COL_ERK, alpha=0.30, edgecolor='none', zorder=0))

euk_verts = (list(ee_smooth) +
             [(ee_smooth[-1][0], Y_TOP), (10.3, Y_TOP), (10.3, Y_BOT)])
ax.add_patch(mpatches.PathPatch(make_closed_path(euk_verts),
             facecolor=COL_EUK, alpha=0.25, edgecolor='none', zorder=0))


# ══════════════════════════════════════════════
# 2. LUCA
# ══════════════════════════════════════════════
LUCA = (5.0, 0.8)
ax.add_patch(Ellipse(LUCA, 1.0, 0.6, facecolor='#F5D5A0',
                     edgecolor='#C8A060', lw=2.5, zorder=4))
ax.add_patch(Ellipse((5.0, 0.82), 0.35, 0.18,
                     facecolor='#E8C080', edgecolor='#B89060', lw=2, zorder=5))


# ══════════════════════════════════════════════
# 3. HOVEDSTAMME
# ══════════════════════════════════════════════
draw_smooth(ax, [(5.0, 1.1), (5.0, 2.0), (5.0, 2.5), (5.0, 3.5)], lw=STEM_LW)


# ══════════════════════════════════════════════
# 4. BAKTERIER
# ══════════════════════════════════════════════
BAK_STEM = (2.5, 5.0)
BAK_MID  = (2.2, 7.5)
BAK_TOP  = (1.8, 10.0)

bak_stem_pts = [(5.0, 2.5), (4.0, 3.2), (3.2, 4.0), BAK_STEM,
                (2.35, 6.2), BAK_MID, (2.0, 8.8), BAK_TOP]
draw_smooth(ax, bak_stem_pts, lw=STEM_LW)

bak_branches = [
    [BAK_STEM, (1.8, 5.5), (1.0, 5.6), (0.5, 5.8)],
    [(2.4, 5.8), (1.6, 6.2), (1.0, 6.8), (0.8, 7.0)],
    [(2.3, 6.8), (1.9, 7.4), (1.6, 7.9), (1.5, 8.2)],
    [BAK_TOP, (1.9, 10.3), (2.0, 10.6), (2.0, 10.8)],
    [BAK_TOP, (1.7, 11.0), (1.5, 12.0), (1.5, 12.5)],
]

for pts in bak_branches:
    draw_smooth(ax, pts)


# ══════════════════════════════════════════════
# 5. ERKEBAKTERIER
# ══════════════════════════════════════════════
ERK_STEM = (4.0, 5.0)
ERK_MID  = (3.9, 7.0)

draw_smooth(ax, [(5.0, 3.2), (4.5, 3.8), (4.2, 4.3), ERK_STEM,
                 (4.0, 6.0), ERK_MID], lw=STEM_LW)

erk_branches = [
    [ERK_STEM, (3.8, 5.4), (3.6, 5.8)],
    [ERK_MID, (3.5, 7.2), (3.3, 7.5)],
    [ERK_MID, (3.6, 7.8), (3.5, 8.3), (3.5, 8.8)],
]

for pts in erk_branches:
    draw_smooth(ax, pts)


# ══════════════════════════════════════════════
# 6. EUKARYOTER
# ══════════════════════════════════════════════
EUK_STEM = (5.8, 5.0)
EUK_MID1 = (6.2, 7.0)
EUK_MID2 = (6.5, 9.0)
EUK_MID3 = (6.7, 11.0)
EUK_TOP  = (6.8, 12.5)

euk_stem_pts = [(5.0, 3.5), (5.3, 4.0), (5.5, 4.5), EUK_STEM,
                (6.0, 6.0), EUK_MID1, (6.3, 8.0), EUK_MID2,
                (6.6, 10.0), EUK_MID3, (6.7, 11.8), EUK_TOP]
draw_smooth(ax, euk_stem_pts, lw=STEM_LW)

euk_branches = [
    [EUK_STEM, (5.4, 5.6), (5.0, 5.8), (4.8, 6.0)],
    [EUK_STEM, (6.5, 5.6), (7.1, 6.1), (7.5, 6.5)],
    [EUK_MID1, (7.0, 7.0), (7.7, 7.1), (8.2, 7.2)],
    [EUK_MID1, (7.2, 7.4), (8.2, 7.9), (8.8, 8.2)],
    [EUK_MID2, (7.5, 9.0), (8.5, 9.1), (9.2, 9.2)],
    [EUK_MID1, (5.8, 7.4), (5.4, 7.7), (5.2, 8.0)],
    [EUK_MID2, (7.0, 9.2), (7.5, 9.4), (7.8, 9.5)],
    [EUK_MID2, (7.2, 9.6), (7.7, 10.1), (8.0, 10.5)],
    [EUK_MID2, (6.0, 9.0), (5.7, 9.3), (5.5, 9.5)],
    [EUK_MID2, (5.8, 9.4), (5.3, 9.9), (5.0, 10.2)],
    [EUK_MID3, (6.0, 11.0), (5.4, 11.1), (5.0, 11.2)],
    [EUK_MID3, (7.0, 11.2), (7.3, 11.4), (7.5, 11.5)],
    [EUK_MID3, (6.2, 11.5), (5.8, 11.9), (5.5, 12.2)],
    [EUK_TOP, (6.9, 12.6), (7.0, 12.8)],
    [EUK_TOP, (7.5, 12.6), (8.1, 12.7), (8.5, 12.8)],
    [EUK_TOP, (7.8, 12.8), (8.5, 13.2), (9.0, 13.5)],
    [EUK_TOP, (7.3, 13.0), (7.7, 13.5), (8.0, 13.8)],
    [EUK_TOP, (6.8, 13.2), (6.8, 13.8), (6.8, 14.2)],
]

for pts in euk_branches:
    draw_smooth(ax, pts)


# ══════════════════════════════════════════════
# LAGRE
# ══════════════════════════════════════════════
fig.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches='tight',
            facecolor=BG_COLOR, edgecolor='none', pad_inches=0.1)
print(f"Figur lagret: {OUTPUT_FILE}")
plt.close()