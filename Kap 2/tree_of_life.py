# Figur: Tre-domene-treet med LUCA og endosymbiose
# ================================================
#
# BRUK:  python tree_of_life.py
# KRAV:  pip install matplotlib numpy

import matplotlib
matplotlib.use('Agg')  # Fjern for interaktiv visning
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse
from matplotlib.path import Path as MplPath
import numpy as np
from pathlib import Path

# ══════════════════════════════════════════════
# INNSTILLINGER
# ══════════════════════════════════════════════
FIG_W, FIG_H = 14, 16
DPI          = 300
OUTPUT_FILE  = Path(__file__).parent / "fig_tree_of_life.png"
BG_COLOR     = '#FAFAFA'

# Domenefarger
COL_BAK   = '#F5E6C8'    # Bakterier (gul/beige)
COL_ERK   = '#F2CAC8'    # Erkebakterier (rosa)
COL_EUK   = '#C8D8EE'    # Eukaryoter (blå)

# Grenfarger
BRANCH_COL = '#3A5A90'

# Endosymbiose
COL_MITO  = '#D64080'
COL_KLORO = '#2E8B57'

# Tekst
FONT_DOMAIN = {'fontsize': 17, 'fontweight': 'bold', 'fontfamily': 'sans-serif'}
FONT_TAXON  = {'fontsize': 9.5, 'fontfamily': 'sans-serif'}
FONT_ENDO   = {'fontsize': 9, 'fontfamily': 'sans-serif', 'fontstyle': 'italic'}
FONT_LUCA   = {'fontsize': 13, 'fontweight': 'bold', 'fontfamily': 'sans-serif'}

BRANCH_LW = 1.6


# ══════════════════════════════════════════════
# HJELPEFUNKSJONER
# ══════════════════════════════════════════════

def bezier3(ax, p0, p1, p2, **kwargs):
    """Kvadratisk Bézier-kurve (3 punkter)."""
    defaults = dict(facecolor='none', edgecolor=BRANCH_COL,
                    lw=BRANCH_LW, capstyle='round', zorder=3)
    defaults.update(kwargs)
    verts = [p0, p1, p2]
    codes = [MplPath.MOVETO, MplPath.CURVE3, MplPath.CURVE3]
    ax.add_patch(mpatches.PathPatch(MplPath(verts, codes), **defaults))


def bezier4(ax, p0, p1, p2, p3, **kwargs):
    """Kubisk Bézier-kurve (4 punkter)."""
    defaults = dict(facecolor='none', edgecolor=BRANCH_COL,
                    lw=BRANCH_LW, capstyle='round', zorder=3)
    defaults.update(kwargs)
    verts = [p0, p1, p2, p3]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]
    ax.add_patch(mpatches.PathPatch(MplPath(verts, codes), **defaults))


def line(ax, p0, p1, **kwargs):
    """Rett linje."""
    defaults = dict(color=BRANCH_COL, lw=BRANCH_LW, solid_capstyle='round', zorder=3)
    defaults.update(kwargs)
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], **defaults)


def txt(ax, x, y, text, **kwargs):
    defaults = dict(ha='center', va='center', zorder=5)
    defaults.update(kwargs)
    ax.text(x, y, text, **defaults)


def blob(ax, xy, w, h, color, alpha=0.30, zorder=1):
    x, y = xy
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.4", facecolor=color,
                         edgecolor='none', alpha=alpha, zorder=zorder)
    ax.add_patch(box)


# ══════════════════════════════════════════════
# TEGN FIGUREN
# ══════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI, facecolor=BG_COLOR)
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.2, 15.5)
ax.set_aspect('equal')
ax.axis('off')
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

# ── LUCA ──
LUCA = (5.0, 0.8)
luca_e = Ellipse(LUCA, 1.0, 0.6, facecolor='#F5D5A0',
                 edgecolor='#C8A060', lw=1.5, zorder=4)
ax.add_patch(luca_e)
ax.add_patch(Ellipse((5.0, 0.82), 0.35, 0.18,
                     facecolor='#E8C080', edgecolor='#B89060', lw=1, zorder=5))
txt(ax, 5.0, 0.15, 'LUCA', **FONT_LUCA, color='#5A4020')

# ── Hovedstamme ──
line(ax, LUCA, (5.0, 2.5))

# Forgreiningspunkter
SPLIT_1 = (5.0, 2.5)   # Bakterier tar av
SPLIT_2 = (5.0, 3.2)   # Erkebakterier tar av
# Eukaryoter fortsetter oppover

# ══════════════════════════════════════════════
# BAKTERIER (venstre)
# ══════════════════════════════════════════════
blob(ax, (1.8, 9.5), 4.0, 9.5, COL_BAK, alpha=0.28)
txt(ax, 1.6, 13.8, 'BAKTERIER', **FONT_DOMAIN, color='#5A4020')

# Stamme fra split til bakterie-base
BAK_STEM = (2.5, 5.0)
bezier4(ax, SPLIT_1, (4.2, 3.0), (3.2, 4.0), BAK_STEM)

# Bakteriestamme oppover
BAK_MID = (2.2, 7.5)
bezier3(ax, BAK_STEM, (2.3, 6.2), BAK_MID)

BAK_TOP = (1.8, 10.0)
bezier3(ax, BAK_MID, (2.0, 8.8), BAK_TOP)

# Bakterie-grener (forgreiner fra stammen ved ulike høyder)
bak_taxa = [
    # (navn, posisjon, forgreiningspunkt_på_stammen, kontrollpunkt)
    ('Spirochaetes',       (0.5, 5.8),   BAK_STEM,  (1.5, 5.2)),
    ('Chlamydias',         (0.8, 7.0),   (2.4, 5.8), (1.4, 6.2)),
    ('Gram\npositive',     (1.5, 8.2),   (2.3, 6.8), (1.8, 7.4)),
    ('Blågrønn-\nbakterier', (2.0, 10.8), BAK_TOP, (1.9, 10.3)),
    ('Proteo-\nbakterier',  (1.5, 12.5), BAK_TOP, (1.6, 11.2)),
]

for name, pos, stem, cp in bak_taxa:
    bezier3(ax, stem, cp, pos)
    txt(ax, pos[0], pos[1], name, **FONT_TAXON, color='#3A3A5A')


# ══════════════════════════════════════════════
# ERKEBAKTERIER (midten)
# ══════════════════════════════════════════════
blob(ax, (3.9, 7.0), 2.0, 5.5, COL_ERK, alpha=0.25)
txt(ax, 3.9, 9.8, 'ERKE-\nBAKTERIER', **FONT_DOMAIN, color='#8B3A3A')

ERK_STEM = (4.0, 5.0)
bezier4(ax, SPLIT_2, (4.5, 3.5), (4.2, 4.2), ERK_STEM)

ERK_MID = (3.9, 7.0)
bezier3(ax, ERK_STEM, (4.0, 6.0), ERK_MID)

erk_taxa = [
    ('Varme-\nelskende', (3.6, 5.8), ERK_STEM, (3.8, 5.4)),
    ('Salt-\nelskende',  (3.3, 7.5), ERK_MID, (3.5, 7.2)),
    ('Metan-\ndannende', (3.5, 8.8), ERK_MID, (3.6, 8.0)),
]

for name, pos, stem, cp in erk_taxa:
    bezier3(ax, stem, cp, pos)
    txt(ax, pos[0], pos[1], name, **FONT_TAXON, color='#5A2020')


# ══════════════════════════════════════════════
# EUKARYOTER (høyre, stort)
# ══════════════════════════════════════════════
blob(ax, (7.0, 10.0), 6.5, 10.5, COL_EUK, alpha=0.22)
txt(ax, 7.8, 14.8, 'EUKARYOTER', **FONT_DOMAIN, color='#2A4A7A')

# Eukaryot-stamme
EUK_STEM = (5.8, 5.0)
bezier4(ax, (5.0, 3.5), (5.3, 4.0), (5.5, 4.5), EUK_STEM)

EUK_MID1 = (6.2, 7.0)
bezier3(ax, EUK_STEM, (6.0, 6.0), EUK_MID1)

EUK_MID2 = (6.5, 9.0)
bezier3(ax, EUK_MID1, (6.3, 8.0), EUK_MID2)

EUK_MID3 = (6.7, 11.0)
bezier3(ax, EUK_MID2, (6.6, 10.0), EUK_MID3)

EUK_TOP = (6.8, 12.5)
bezier3(ax, EUK_MID3, (6.7, 11.8), EUK_TOP)

# Eukaryot-grener (forgreiner ved ulike høyder langs stammen)
euk_taxa = [
    # Tidlige avgreninger (nedre del)
    ('Øyealger',              (4.8, 6.0),  EUK_STEM, (5.3, 5.5)),
    ('Diplomonader',          (7.5, 6.5),  EUK_STEM, (6.8, 5.8)),
    ('Cellulære\nslimsopp',   (8.2, 7.2),  EUK_MID1, (7.5, 7.0)),
    ('Plasmodiale\nslimsopp', (8.8, 8.2),  EUK_MID1, (7.8, 7.8)),
    ('Amøber',                (9.2, 9.2),  EUK_MID2, (8.2, 8.8)),

    # Midtre avgreninger
    ('Egg-\nsporesopp',      (5.2, 8.0),  EUK_MID1, (5.6, 7.5)),
    ('Stråledyr',            (7.8, 9.5),  EUK_MID2, (7.3, 9.2)),
    ('Poredyr',              (8.0, 10.5), EUK_MID2, (7.5, 10.0)),
    ('Sporedyr',             (5.5, 9.5),  EUK_MID2, (5.8, 9.2)),
    ('Flimmerdyr',           (5.0, 10.2), EUK_MID2, (5.4, 9.8)),

    # Øvre avgreninger
    ('Fureflagellater',      (5.0, 11.2), EUK_MID3, (5.6, 11.0)),
    ('Kisealger',            (7.5, 11.5), EUK_MID3, (7.2, 11.2)),
    ('Brunalger',            (5.5, 12.2), EUK_MID3, (5.9, 11.8)),
    ('Rødalger',             (7.0, 12.8), EUK_TOP,  (6.9, 12.6)),

    # Topp
    ('Sopp',                 (8.5, 12.8), EUK_TOP,  (7.8, 12.6)),
    ('Dyr',                  (9.0, 13.5), EUK_TOP,  (8.2, 13.0)),
    ('Grønn-\nalger',        (8.0, 13.8), EUK_TOP,  (7.5, 13.2)),
    ('Planter',              (6.8, 14.2), EUK_TOP,  (6.8, 13.5)),
]

for name, pos, stem, cp in euk_taxa:
    bezier3(ax, stem, cp, pos)
    txt(ax, pos[0], pos[1], name, **FONT_TAXON, color='#2A3A6A')


# ══════════════════════════════════════════════
# ENDOSYMBIOSEPILER
# ══════════════════════════════════════════════
# Proteobakterier → Mitokondrium
proto = bak_taxa[4][1]  # Proteobakterier pos
arr1 = FancyArrowPatch((proto[0] + 0.6, proto[1] - 0.3),
                       (EUK_MID3[0] - 0.3, EUK_MID3[1] + 0.3),
                       connectionstyle="arc3,rad=-0.25",
                       arrowstyle='->', mutation_scale=20,
                       color=COL_MITO, lw=2.8, zorder=4)
ax.add_patch(arr1)
txt(ax, 3.0, 12.0, '(Mito-\nkondrium)', **FONT_ENDO, color=COL_MITO)

# Blågrønnbakterier → Kloroplaster
blaa = bak_taxa[3][1]   # Blågrønnbakterier pos
arr2 = FancyArrowPatch((blaa[0] + 0.6, blaa[1] + 0.2),
                       (EUK_MID3[0] - 0.5, EUK_MID3[1] - 0.3),
                       connectionstyle="arc3,rad=-0.20",
                       arrowstyle='->', mutation_scale=20,
                       color=COL_KLORO, lw=2.8, zorder=4)
ax.add_patch(arr2)
txt(ax, 3.2, 11.2, '(Kloro-\nplaster)', **FONT_ENDO, color=COL_KLORO)


# ── Lagre ──
fig.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches='tight',
            facecolor=BG_COLOR, edgecolor='none', pad_inches=0.1)
print(f"Figur lagret: {OUTPUT_FILE}")
print(f"Oppløsning:   {DPI} DPI")
plt.close()
