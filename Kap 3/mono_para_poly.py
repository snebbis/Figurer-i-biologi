import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

fig, axes = plt.subplots(1, 3, figsize=(16, 7))
fig.patch.set_facecolor("white")

LINE_COLOR = "#222222"
LW = 4.0

# ══════════════════════════════════════
# Shared tree topology: ((A,B),(C,(D,(E,F))))
# ══════════════════════════════════════
# Terminal y-positions (top to bottom)
y_A = 6.5
y_B = 5.5
y_C = 4.0
y_D = 2.8
y_E = 1.6
y_F = 0.4

# Internal node x-positions
x_root = 0.5
x_main_split = 2.0   # splits (A,B) from (C,D,E,F)
x_AB = 5.0           # A/B split
x_C_DEF = 3.2        # C vs (D,E,F)
x_D_EF = 4.4         # D vs (E,F)
x_EF = 5.6           # E/F split

x_tip = 7.0

# Internal y positions
y_AB = (y_A + y_B) / 2
y_EF = (y_E + y_F) / 2
y_D_EF = (y_D + y_EF) / 2
y_C_DEF = (y_C + y_D_EF) / 2
y_root = (y_AB + y_C_DEF) / 2


def draw_tree(ax):
    """Draw the shared tree structure on the given axes."""
    def hline(x1, x2, y):
        ax.plot([x1, x2], [y, y], color=LINE_COLOR, lw=LW,
                solid_capstyle='round', zorder=3)
    def vline(x, y1, y2):
        ax.plot([x, x], [y1, y2], color=LINE_COLOR, lw=LW,
                solid_capstyle='round', zorder=3)

    # Root stub
    hline(x_root, x_main_split, y_root)
    # Main split
    vline(x_main_split, y_AB, y_C_DEF)
    # (A,B) side
    hline(x_main_split, x_AB, y_AB)
    vline(x_AB, y_A, y_B)
    hline(x_AB, x_tip, y_A)
    hline(x_AB, x_tip, y_B)
    # (C,D,E,F) side
    hline(x_main_split, x_C_DEF, y_C_DEF)
    vline(x_C_DEF, y_C, y_D_EF)
    hline(x_C_DEF, x_tip, y_C)
    hline(x_C_DEF, x_D_EF, y_D_EF)
    vline(x_D_EF, y_D, y_EF)
    hline(x_D_EF, x_tip, y_D)
    hline(x_D_EF, x_EF, y_EF)
    vline(x_EF, y_E, y_F)
    hline(x_EF, x_tip, y_E)
    hline(x_EF, x_tip, y_F)

    # Terminal labels
    for name, y in [("A", y_A), ("B", y_B), ("C", y_C),
                    ("D", y_D), ("E", y_E), ("F", y_F)]:
        ax.text(x_tip + 0.15, y, name, fontsize=15, fontweight='bold',
                va='center', ha='left', color="#222222",
                fontfamily='sans-serif', zorder=4)


def highlight_box(ax, x_start, y_bot, y_top, color, alpha=0.35, pad_x=0.25, pad_y=0.35):
    """Draw a rounded highlight rectangle."""
    rect = patches.FancyBboxPatch(
        (x_start - pad_x, y_bot - pad_y),
        (x_tip + 0.65) - (x_start - pad_x),
        (y_top - y_bot) + 2 * pad_y,
        boxstyle="round,pad=0.05,rounding_size=0.25",
        facecolor=color, edgecolor=color,
        alpha=alpha, linewidth=0, zorder=1
    )
    ax.add_patch(rect)


def setup_panel(ax, title, subtitle, title_color):
    ax.set_xlim(-0.3, 8.2)
    ax.set_ylim(-2.0, 8.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor("white")
    # Title
    ax.text(4.0, 8.2, title, fontsize=17, fontweight='bold',
            color=title_color, ha='center', va='top',
            fontfamily='sans-serif')
    # Subtitle
    ax.text(4.0, -1.0, subtitle, fontsize=11, color="#444444",
            ha='center', va='top', fontfamily='sans-serif',
            style='italic', wrap=True)


# ══════════════════════════════════════
# PANEL 1: MONOFYLETISK
# Highlight: (D,E,F) — common ancestor + ALL descendants
# ══════════════════════════════════════
ax = axes[0]
highlight_box(ax, x_D_EF, y_F, y_D, "#27AE60", alpha=0.35)
draw_tree(ax)
setup_panel(ax, "Monofyletisk",
            "En felles forfader og\nALLE dens etterkommere",
            "#1E7E3E")


# ══════════════════════════════════════
# PANEL 2: PARAFYLETISK
# Highlight: (C,D) — includes MRCA of (C,D,E,F), but excludes E,F
# So highlight the (C,D,E,F) region but NOT including E,F leaves
# ══════════════════════════════════════
ax = axes[1]
# Parafyletisk: common ancestor of C,D,E,F is included, plus C and D,
# but E and F are excluded. We draw a box around C, D and the trunk,
# but NOT covering E/F tips.
# Custom polygon/box that excludes E,F area:
# Simplest: highlight region covering branches to C and D, plus the trunk
# from the MRCA.

# We'll draw a polygon covering: from x_main_split to x_tip, at y levels covering C and D, excluding E,F
# Easier: two separate rounded boxes — one tall one covering C, D's region
# Actually cleanest: one box from y_D to y_C covering the C+D region
highlight_box(ax, x_C_DEF, y_D, y_C, "#E67E22", alpha=0.35, pad_y=0.35)
draw_tree(ax)
setup_panel(ax, "Parafyletisk",
            "En felles forfader og NOEN\n(men ikke alle) etterkommere",
            "#B25608")


# ══════════════════════════════════════
# PANEL 3: POLYFYLETISK
# Highlight: (A,B) and (E,F) together — two separate regions,
# MRCA (root) NOT included in the group
# ══════════════════════════════════════
ax = axes[2]
# Two separate highlight boxes
highlight_box(ax, x_AB, y_B, y_A, "#9B59B6", alpha=0.35, pad_y=0.28)
highlight_box(ax, x_EF, y_F, y_E, "#9B59B6", alpha=0.35, pad_y=0.28)
draw_tree(ax)
setup_panel(ax, "Polyfyletisk",
            "En gruppe der den felles\nforfaderen IKKE er inkludert",
            "#6C3483")


# ══════════════════════════════════════
# Layout
# ══════════════════════════════════════
plt.subplots_adjust(wspace=0.05, left=0.02, right=0.98, top=0.95, bottom=0.05)
plt.savefig("/home/claude/mono_para_poly.png", dpi=250,
            bbox_inches="tight", facecolor="white", edgecolor="none")
plt.savefig("/home/claude/mono_para_poly.svg",
            bbox_inches="tight", facecolor="white", edgecolor="none")
print("Done.")
