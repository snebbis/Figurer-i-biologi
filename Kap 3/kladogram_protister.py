import matplotlib.pyplot as plt
import numpy as np
import os

# ── Konfigurasjon ──
FIG_SIZE = (18, 8)
LINE_COLOR = "#5C3A2E"
LINE_WIDTH = 8.25      # 50 % tykkere
BG_COLOR = "white"      # Hvitt bakgrunn
TOP = 9.5

# ── Bezier-funksjoner ──
def bezier(p0, p1, p2, p3, n=150):
    t = np.linspace(0, 1, n)
    mt = 1 - t
    pts = (
        (mt**3)[:, None] * np.array(p0) +
        (3 * mt**2 * t)[:, None] * np.array(p1) +
        (3 * mt * t**2)[:, None] * np.array(p2) +
        (t**3)[:, None] * np.array(p3)
    )
    return pts[:, 0], pts[:, 1]

def draw(ax, p0, p1, p2, p3):
    x, y = bezier(p0, p1, p2, p3)
    ax.plot(x, y, color=LINE_COLOR, lw=LINE_WIDTH, solid_capstyle='round')

# ── Opprett figur og akse ──
fig, ax = plt.subplots(figsize=FIG_SIZE)
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# ── Node-koordinater ──
tx = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
root = (0.5, 0.5)
n1   = (3.0, 1.6)
n2   = (5.0, 2.4)
n3   = (7.0, 3.1)
n4   = (9.0, 3.7)
n5   = (11.0, 4.2)
n6   = (13.5, 4.8)   # siste split: rodalger / brunalger

# ── Tegn treet ──
# TRUNK
draw(ax, root, (1.2, 0.8), (2.2, 1.2), n1)
draw(ax, n1, (3.6, 1.8), (4.2, 2.1), n2)
draw(ax, n2, (5.6, 2.6), (6.2, 2.9), n3)
draw(ax, n3, (7.6, 3.3), (8.2, 3.5), n4)
draw(ax, n4, (9.6, 3.9), (10.2, 4.1), n5)
draw(ax, n5, (11.6, 4.4), (12.8, 4.6), n6)

# BRANCHES
draw(ax, root, (0.7, 1.8), (1.3, 5.0), (tx[0], TOP))    # trypanosoma
draw(ax, n1, (3.1, 2.8), (3.5, 5.5), (tx[1], TOP))      # slimsopper
draw(ax, n2, (5.2, 3.6), (5.5, 6.2), (tx[2], TOP))      # flagellater
draw(ax, n3, (7.2, 4.3), (7.5, 6.8), (tx[3], TOP))      # ciliater
draw(ax, n4, (9.2, 4.9), (9.5, 7.0), (tx[4], TOP))      # sporedyr
draw(ax, n5, (11.2, 5.4), (11.5, 7.2), (tx[5], TOP))    # grønnalger
draw(ax, n6, (13.5, 6.0), (13.8, 7.8), (tx[6], TOP))    # rodalger
draw(ax, n6, (14.2, 5.6), (15.2, 7.5), (tx[7], TOP))    # brunalger

# ── Akse-innstillinger ──
ax.set_xlim(-0.5, 17.5)
ax.set_ylim(-0.5, 10.5)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()

# ── Lagre filer ──
save_dir = r"C:\Users\sebastianb_a\OneDrive - Akershus fylkeskommune\Skrivebord\FORFATTER\Biologi 1\Figurer\Kap 3"
os.makedirs(save_dir, exist_ok=True)

plt.savefig(os.path.join(save_dir, "kladogram_protister.png"), dpi=250, bbox_inches="tight", facecolor=BG_COLOR)
plt.savefig(os.path.join(save_dir, "kladogram_protister.svg"), bbox_inches="tight", facecolor=BG_COLOR)

plt.show()
print("Ferdig! Filer lagret med hvit bakgrunn og 50% tykkere linjer.")