import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, FancyArrow, FancyArrowPatch, PathPatch, Wedge
from matplotlib.path import Path
import numpy as np

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# ── Colors ──
GRAY = '#9B9880'
BLUE = '#2E5CB8'
PINK_MID = '#A74D8E'
PINK = '#C42065'
LIGHT_PURPLE = '#D6BFE3'
DARK_PURPLE = '#4A148C'
RED = '#E53935'
LEADER_BLUE = '#5DA7D4'

# ══════════════════════════════════════
# Gray Y-shape (trunk + two diverging arrows)
# ══════════════════════════════════════

# Trunk rectangle
trunk = patches.Rectangle((0.3, 2.5), 3.3, 1.2,
                          facecolor=GRAY, edgecolor='none',
                          alpha=0.55, zorder=1)
ax.add_patch(trunk)

# Upper arrow (blue → pink, eventually new species)
upper_arrow = FancyArrow(
    3.2, 3.1, 7.3, 3.1,
    width=1.3, head_width=2.0, head_length=1.3,
    facecolor=GRAY, edgecolor='none', alpha=0.55,
    length_includes_head=True, zorder=1
)
ax.add_patch(upper_arrow)

# Lower arrow (stays blue, original species)
lower_arrow = FancyArrow(
    3.2, 3.1, 7.3, -2.6,
    width=1.3, head_width=2.0, head_length=1.3,
    facecolor=GRAY, edgecolor='none', alpha=0.55,
    length_includes_head=True, zorder=1
)
ax.add_patch(lower_arrow)


# ══════════════════════════════════════
# Helper functions
# ══════════════════════════════════════
def blob(center, color, r=0.26, zorder=5):
    ax.add_patch(Circle(center, r, facecolor=color,
                        edgecolor='none', zorder=zorder))

def gene_flow(p1, p2, shrink=9):
    arrow = FancyArrowPatch(
        p1, p2, arrowstyle='<|-|>', mutation_scale=11,
        color='#222222', lw=1.3, zorder=6,
        shrinkA=shrink, shrinkB=shrink
    )
    ax.add_patch(arrow)


# ══════════════════════════════════════
# Populations
# ══════════════════════════════════════

# Original population cluster (left trunk)
orig = [(0.9, 3.35), (1.15, 2.80), (1.65, 3.25)]
for pos in orig:
    blob(pos, BLUE)
gene_flow(orig[0], orig[1])
gene_flow(orig[1], orig[2])
gene_flow(orig[0], orig[2])

# Middle populations
mid = [(2.55, 3.25), (2.95, 2.80)]
for pos in mid:
    blob(pos, BLUE)
gene_flow(mid[0], mid[1])

# Upper branch: gradual color change blue → pink
upper_positions = [
    ((4.5, 3.55), BLUE),
    ((5.6, 4.10), BLUE),
    ((6.7, 4.65), '#5B3E8E'),  # blue-purple
    ((7.8, 5.20), PINK_MID),
    ((8.9, 5.75), PINK),
]
for pos, color in upper_positions:
    blob(pos, color)

# Lower branch: stays blue, gene flow maintained
lower_positions = [(4.5, 2.65), (5.6, 2.10), (6.7, 1.55), (7.8, 1.00), (8.9, 0.45)]
for pos in lower_positions:
    blob(pos, BLUE)
for i in range(len(lower_positions) - 1):
    gene_flow(lower_positions[i], lower_positions[i+1])


# ══════════════════════════════════════
# Red divergence line
# ══════════════════════════════════════
# Solid bezier from split area curving along upper branch
solid_verts = [
    (3.05, 2.95),
    (3.50, 3.70),
    (5.00, 4.00),
    (7.50, 5.15),
]
solid_codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
red_path = Path(solid_verts, solid_codes)
ax.add_patch(PathPatch(red_path, facecolor='none', edgecolor=RED,
                       lw=3.8, zorder=7, capstyle='round'))

# Dashed continuation toward the new species region
t = np.linspace(0, 1, 40)
dx = np.linspace(7.50, 9.40, 40)
dy = np.linspace(5.15, 5.90, 40)
ax.plot(dx, dy, color=RED, lw=3.8, linestyle=(0, (3, 2.5)),
        zorder=7, solid_capstyle='round', dash_capstyle='round')


# ══════════════════════════════════════
# New species region (lilac arrow on the right)
# ══════════════════════════════════════
new_species = FancyArrow(
    10.2, 5.30, 1.4, 0,
    width=1.6, head_width=2.3, head_length=0.8,
    facecolor=LIGHT_PURPLE, edgecolor=LIGHT_PURPLE,
    alpha=0.75, length_includes_head=True, zorder=2
)
ax.add_patch(new_species)

# Dark black curved line at the boundary of the new species region
# (representing the "separation barrier")
boundary_verts = [
    (10.00, 6.05),
    (9.70, 5.30),
    (10.00, 4.55),
]
bcodes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
bpath = Path(boundary_verts, bcodes)
ax.add_patch(PathPatch(bpath, facecolor='none', edgecolor='#333333',
                       lw=1.8, zorder=3))

# Dark purple dots inside (new species)
for pos in [(10.50, 5.85), (10.80, 5.30), (10.55, 4.78)]:
    blob(pos, DARK_PURPLE, r=0.18, zorder=6)


# ══════════════════════════════════════
# Label leader lines (thin blue, pointing up/down)
# ══════════════════════════════════════
def leader(x_start, y_start, x_end, y_end, bar_width=0.5):
    ax.plot([x_start, x_end], [y_start, y_end],
            color=LEADER_BLUE, lw=1.2, zorder=8)
    ax.plot([x_end - bar_width/2, x_end + bar_width/2], [y_end, y_end],
            color=LEADER_BLUE, lw=1.2, zorder=8)

# Leaders from key features upward
leader(1.25, 3.6, 1.25, 7.0)     # original population
leader(2.75, 3.4, 2.75, 7.5)     # middle cluster
leader(6.70, 4.90, 6.70, 7.8)    # upper changing (intermediate)
leader(10.60, 5.85, 11.40, 7.3)  # new species
# Leaders pointing down
leader(6.70, 1.40, 6.70, -1.3)   # lower branch


# ══════════════════════════════════════
# Axis
# ══════════════════════════════════════
ax.set_xlim(-0.3, 12.8)
ax.set_ylim(-2.0, 8.3)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
plt.savefig("/home/claude/speciation.png", dpi=250,
            bbox_inches="tight", facecolor="white", edgecolor="none")
plt.savefig("/home/claude/speciation.svg",
            bbox_inches="tight", facecolor="white", edgecolor="none")
print("Done.")
