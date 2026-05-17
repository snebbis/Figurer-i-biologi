import matplotlib.pyplot as plt
import numpy as np
import os

# ── Konfigurasjon ──
FIG_SIZE = (16, 9)
LINE_COLOR = "#3E6B52"
LINE_WIDTH = 8.25       # 50 % tykkere (5.5 * 1.5)
BG_COLOR = "white"      # Hvitt bakgrunn
TOP = 10.5

# ── Definer Bezier-funksjon ──
def bezier(p0, p1, p2, p3, n=120):
    """Returner x, y-koordinater for en kubisk Bezier-kurve fra 4 kontrollpunkter."""
    t = np.linspace(0, 1, n)
    mt = 1 - t
    pts = (
        (mt**3)[:, None] * np.array(p0) +
        (3 * mt**2 * t)[:, None] * np.array(p1) +
        (3 * mt * t**2)[:, None] * np.array(p2) +
        (t**3)[:, None] * np.array(p3)
    )
    return pts[:, 0], pts[:, 1]

def draw_bezier(ax, p0, p1, p2, p3, color=LINE_COLOR, lw=LINE_WIDTH):
    """Tegn en Bezier-kurve på ax."""
    x, y = bezier(p0, p1, p2, p3)
    ax.plot(x, y, color=color, lw=lw, solid_capstyle='round')

# ── Opprett figur og akse ──
fig, ax = plt.subplots(figsize=FIG_SIZE)
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# ── Node-koordinater ──
tx = [2.0, 3.8, 5.8, 7.5, 9.8, 12.0, 13.8]
root  = (0.5, 0.5)
n2    = (3.0, 2.5)
n_kar = (5.5, 4.5)
n3    = (7.5, 3.5)
n4    = (11.5, 5.8)

# ── Tegn treet ──
draw_bezier(ax, root, (0.7, 1.5), (1.4, 4.5), (tx[0], TOP))       # root → moser
draw_bezier(ax, root, (1.0, 1.0), (2.0, 1.8), n2)                  # root → n2
draw_bezier(ax, n2, (3.1, 3.5), (3.4, 6.5), (tx[1], TOP))          # n2 → bregner
draw_bezier(ax, n2, (3.5, 3.2), (4.5, 3.8), n_kar)                 # n2 → karspore
draw_bezier(ax, n2, (4.0, 2.8), (6.0, 3.2), n3)                    # n2 → n3
draw_bezier(ax, n_kar, (5.5, 5.5), (5.6, 7.8), (tx[2], TOP))       # karspore → sneller
draw_bezier(ax, n_kar, (5.9, 5.3), (6.8, 7.5), (tx[3], TOP))       # karspore → kråkefot
draw_bezier(ax, n3, (7.8, 4.5), (8.8, 7.0), (tx[4], TOP))          # n3 → nakenfrøede
draw_bezier(ax, n3, (8.5, 3.8), (10.0, 4.8), n4)                   # n3 → n4
draw_bezier(ax, n4, (11.6, 7.0), (11.8, 8.8), (tx[5], TOP))        # n4 → enfrøbladede
draw_bezier(ax, n4, (12.1, 6.5), (13.0, 8.2), (tx[6], TOP))        # n4 → tofrøbladede

# ── Akse-innstillinger ──
ax.set_xlim(-0.5, 15.5)
ax.set_ylim(-0.5, 11.5)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()

# ── Lagre filer ──
save_dir = r"C:\Users\sebastianb_a\OneDrive - Akershus fylkeskommune\Skrivebord\FORFATTER\Biologi 1\Figurer\Kap 3"
os.makedirs(save_dir, exist_ok=True)

plt.savefig(os.path.join(save_dir, "kladogram_planter.png"), dpi=250, bbox_inches="tight", facecolor=BG_COLOR)
plt.savefig(os.path.join(save_dir, "kladogram_planter.svg"), bbox_inches="tight", facecolor=BG_COLOR)

plt.show()
print("Ferdig! Filer lagret i Kap 3-mappen med hvit bakgrunn og 50 % tykkere linjer.")