import matplotlib.pyplot as plt
import numpy as np
import os

# ── Konfigurasjon ──
FIG_SIZE = (18, 9)
LINE_COLOR = "#5C3A2E"  # mørk brun
LINE_WIDTH = 8.25        # 50 % tykkere
BG_COLOR = "white"       # hvit bakgrunn
TOP = 10.5

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
tx = [1.8, 3.5, 5.5, 7.2, 9.0, 10.8, 12.5, 14.5, 16.2]
root = (0.5, 0.5)
n1   = (2.8, 2.2)
n2   = (4.8, 3.2)
n3   = (6.8, 4.0)
n4   = (9.0, 4.8)
n5   = (9.5, 5.5)
n6   = (11.0, 6.5)
n7   = (13.8, 6.0)

# ── TRUNK SEGMENTS ──
draw(ax, root, (1.0, 0.9), (2.0, 1.6), n1)
draw(ax, n1, (3.3, 2.5), (4.0, 2.8), n2)
draw(ax, n2, (5.4, 3.4), (6.0, 3.7), n3)
draw(ax, n3, (7.5, 4.2), (8.2, 4.5), n4)
draw(ax, n4, (9.1, 5.0), (9.3, 5.3), n5)
draw(ax, n5, (10.0, 5.8), (10.5, 6.2), n6)
draw(ax, n4, (10.2, 5.0), (12.0, 5.5), n7)

# ── BRANCHES TO TERMINALS ──
draw(ax, root, (0.8, 1.8), (1.3, 5.0), (tx[0], TOP))    # svamper
draw(ax, n1, (2.9, 3.5), (3.2, 6.5), (tx[1], TOP))      # huldyr
draw(ax, n2, (5.0, 4.5), (5.3, 7.0), (tx[2], TOP))      # flatmark
draw(ax, n3, (7.0, 5.2), (7.1, 7.5), (tx[3], TOP))      # rundmark
draw(ax, n5, (9.4, 6.5), (9.2, 8.5), (tx[4], TOP))      # blotdyr
draw(ax, n6, (10.9, 7.5), (10.8, 9.0), (tx[5], TOP))    # leddmark
draw(ax, n6, (11.5, 7.2), (12.0, 8.8), (tx[6], TOP))    # leddyr
draw(ax, n7, (14.0, 7.2), (14.2, 8.8), (tx[7], TOP))    # pigghuder
draw(ax, n7, (14.5, 6.8), (15.5, 8.5), (tx[8], TOP))    # ryggstrengdyr

# ── Akse-innstillinger ──
ax.set_xlim(-0.5, 17.5)
ax.set_ylim(-0.5, 11.5)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()

# ── Lagre filer ──
save_dir = r"C:\Users\sebastianb_a\OneDrive - Akershus fylkeskommune\Skrivebord\FORFATTER\Biologi 1\Figurer\Kap 3"
os.makedirs(save_dir, exist_ok=True)

plt.savefig(os.path.join(save_dir, "kladogram_dyr.png"), dpi=250, bbox_inches="tight", facecolor=BG_COLOR)
plt.savefig(os.path.join(save_dir, "kladogram_dyr.svg"), bbox_inches="tight", facecolor=BG_COLOR)

plt.show()
print("Ferdig! Filer lagret med hvit bakgrunn og 50% tykkere linjer.")