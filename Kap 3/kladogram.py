import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Path for saving figures ──
save_path = r"C:\Users\sebastianb_a\OneDrive - Akershus fylkeskommune\Skrivebord\FORFATTER\Biologi 1\Figurer\Kap 3"
os.makedirs(save_path, exist_ok=True)

# ── Configuration ──
fig, ax = plt.subplots(figsize=(12, 7.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Colors
BRANCH_COLOR = "#2E7D32"    # dark green
NODE_COLOR = "#1B5E20"      # darker green for dots
LABEL_COLOR = "#1B5E20"
TEXT_COLOR = "#333333"
LIGHT_GREEN = "#E8F5E9"     # background highlight for clades

LINE_WIDTH = 4.0
NODE_SIZE = 8

# ── Tree topology ──
sp = {"A": 1, "B": 3, "C": 4.5, "D": 7, "E": 8.5}

bc_x = (sp["B"] + sp["C"]) / 2       # 3.75
bc_t = 8

left_x = (sp["A"] + bc_x) / 2         # 2.375
left_t = 30

right_x = (sp["D"] + sp["E"]) / 2     # 7.75
right_t = 15

root_x = (left_x + right_x) / 2       # ~5.06
root_t = 45

def draw_branch(x_parent, x_child, y_split, y_child):
    ax.plot([x_parent, x_child], [y_split, y_split], color=BRANCH_COLOR,
            linewidth=LINE_WIDTH, solid_capstyle="round")
    ax.plot([x_child, x_child], [y_split, y_child], color=BRANCH_COLOR,
            linewidth=LINE_WIDTH, solid_capstyle="round")

def draw_node(x, y, size=NODE_SIZE):
    ax.plot(x, y, "o", color=NODE_COLOR, markersize=size, zorder=5)

# ── Draw the tree ──
ax.plot([root_x, root_x], [root_t, root_t + 4], color=BRANCH_COLOR,
        linewidth=LINE_WIDTH, solid_capstyle="round")
draw_branch(root_x, left_x, root_t, left_t)
draw_branch(root_x, right_x, root_t, right_t)
draw_node(root_x, root_t)

# Left ancestor → A & BC ancestor
draw_branch(left_x, sp["A"], left_t, 0)
draw_branch(left_x, bc_x, left_t, bc_t)
draw_node(left_x, left_t)

# BC ancestor → B & C
draw_branch(bc_x, sp["B"], bc_t, 0)
draw_branch(bc_x, sp["C"], bc_t, 0)
draw_node(bc_x, bc_t)

# Right ancestor → D & E
draw_branch(right_x, sp["D"], right_t, 0)
draw_branch(right_x, sp["E"], right_t, 0)
draw_node(right_x, right_t)

# ── Species labels at y=0 ──
for name, x in sp.items():
    ax.text(x, -2.5, f"Art {name}", ha="center", va="top", fontsize=16,
            fontweight="bold", color=LABEL_COLOR, fontfamily="sans-serif")

# ── Clade annotations ──
ax.annotate("", xy=(sp["B"] - 0.4, -5.5), xytext=(sp["C"] + 0.4, -5.5),
            arrowprops=dict(arrowstyle="-", color="#66BB6A", lw=3))
ax.text((sp["B"] + sp["C"]) / 2, -7, "Klade 1\n(B + C)", ha="center", va="top",
        fontsize=12, color="#2E7D32", fontfamily="sans-serif", style="italic")

ax.annotate("", xy=(sp["A"] - 0.4, -10), xytext=(sp["C"] + 0.4, -10),
            arrowprops=dict(arrowstyle="-", color="#43A047", lw=3))
ax.text((sp["A"] + sp["C"]) / 2, -11.5, "Klade 2\n(A + B + C)", ha="center", va="top",
        fontsize=12, color="#2E7D32", fontfamily="sans-serif", style="italic")

# ── Time axis annotations ──
time_ticks = [0, 8, 15, 30, 45]
time_labels = ["Nåtid", "8", "15", "30", "45"]
for t, lab in zip(time_ticks, time_labels):
    ax.plot([-0.3, 0], [t, t], color="#999999", linewidth=1.2)
    ax.text(-0.5, t, lab, ha="right", va="center", fontsize=16,
            color="#666666", fontfamily="sans-serif")

ax.set_ylabel("Millioner år siden", fontsize=16, color=TEXT_COLOR,
              fontfamily="sans-serif", labelpad=30)
ax.set_xlim(-1.5, 13)
ax.set_ylim(-13, 52)
ax.invert_yaxis()
ax.set_xticks([])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.set_yticks([])

plt.tight_layout()
plt.savefig(f"{save_path}\\kladogram.png", dpi=200, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.savefig(f"{save_path}\\kladogram.pdf", bbox_inches="tight", facecolor="white", edgecolor="none")
plt.close(fig)
print("Cladogram saved.")