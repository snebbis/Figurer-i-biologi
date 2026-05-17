import matplotlib.pyplot as plt
import numpy as np
import os

# ── Lagrepath (Windows) ──
save_path = r"C:\Users\sebastianb_a\OneDrive - Akershus fylkeskommune\Skrivebord\FORFATTER\Biologi 1\Figurer\Kap 3"
os.makedirs(save_path, exist_ok=True)

png_file = os.path.join(save_path, "fylogenetisk_tre_anatomi.png")
svg_file = os.path.join(save_path, "fylogenetisk_tre_anatomi.svg")

# ── Figur ──
fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

LINE_COLOR = "#222222"
LW = 4.5
LABEL_COLOR = "#222222"

# ── Y-posisjoner ──
y_A, y_B, y_C, y_D, y_E = 7.0, 5.5, 3.5, 2.0, 0.3

# ── X-posisjoner ──
x_root = 0.5
x_n1 = 2.5
x_n2 = 4.5
x_AB = 6.5
x_CD = 6.5
x_tip = 9.0

# ── Hjelpefunksjoner ──
def hline(x1, x2, y):
    ax.plot([x1, x2], [y, y], color=LINE_COLOR, lw=LW,
            solid_capstyle='round')

def vline(x, y1, y2):
    ax.plot([x, x], [y1, y2], color=LINE_COLOR, lw=LW,
            solid_capstyle='round')

# ── Beregn noder ──
y_AB = (y_A + y_B) / 2
y_CD = (y_C + y_D) / 2
y_ABCD = (y_AB + y_CD) / 2
y_all = (y_ABCD + y_E) / 2

# ── Tegn treet ──
hline(x_root, x_n1, y_all)
vline(x_n1, y_ABCD, y_E)

hline(x_n1, x_n2, y_ABCD)
hline(x_n1, x_tip, y_E)

vline(x_n2, y_AB, y_CD)
hline(x_n2, x_AB, y_AB)
hline(x_n2, x_CD, y_CD)

vline(x_AB, y_A, y_B)
hline(x_AB, x_tip, y_A)
hline(x_AB, x_tip, y_B)

vline(x_CD, y_C, y_D)
hline(x_CD, x_tip, y_C)
hline(x_CD, x_tip, y_D)

# ── Labels ──
for name, y in [("Art A", y_A), ("Art B", y_B),
                ("Art C", y_C), ("Art D", y_D), ("Art E", y_E)]:
    ax.text(x_tip + 0.2, y, name,
            fontsize=16, fontweight='bold',
            va='center', ha='left', color=LABEL_COLOR)

# ── Tidsakse ──
arrow_y = -1.5
ax.annotate("", xy=(x_tip, arrow_y), xytext=(x_root, arrow_y),
            arrowprops=dict(arrowstyle='->', lw=2))

ax.text((x_root + x_tip)/2, arrow_y - 0.5, "Tid",
        ha='center', fontsize=13, style='italic')
ax.text(x_root, arrow_y - 0.5, "fortid", ha='left', fontsize=10)
ax.text(x_tip, arrow_y - 0.5, "nåtid", ha='right', fontsize=10)

# ── Rydd opp ──
ax.set_xlim(-1.5, 11)
ax.set_ylim(-2.8, 9)
ax.axis('off')

plt.tight_layout()

# ── Lagre ──
plt.savefig(png_file, dpi=250, bbox_inches="tight",
            facecolor="white", edgecolor="none")
plt.savefig(svg_file, bbox_inches="tight",
            facecolor="white", edgecolor="none")

plt.show()

print(f"Lagret til:\n{png_file}\n{svg_file}")