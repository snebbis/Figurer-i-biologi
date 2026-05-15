"""
Figur: Sammenhengen mellom toleranse og måleusikkerhet
======================================================
Viser at toleranse er én av flere bidragsytere til den totale
måleusikkerheten. Toleransen er et smalt intervall rundt sann verdi;
måleusikkerheten er et bredere intervall som også inkluderer
avlesning og andre feilkilder.

Fargepalett: stone (varm) for toleranse, slate (kjølig) for måleusikkerhet.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ---- Stone & slate fargepalett ----
# Stone (varm) – brukes for toleranse
STONE_FYLL    = "#D6D3D1"   # stone-300
STONE_KANT    = "#44403C"   # stone-700
STONE_TEKST   = "#1C1917"   # stone-900

# Slate (kjølig) – brukes for måleusikkerhet
SLATE_FYLL    = "#E2E8F0"   # slate-200
SLATE_KANT    = "#475569"   # slate-600
SLATE_TEKST   = "#1E293B"   # slate-800

# Aksenter
SANN_VERDI    = "#0F172A"   # slate-900 – mørkest, mest framtredende
MAALING       = "#292524"   # stone-800
TALLINJE      = "#57534E"   # stone-600

# ---- Figurkoordinater (langs en tallinje fra 0 til 100) ----
sann_verdi          = 50
halv_toleranse      = 3      # ±3 enheter
halv_usikkerhet     = 25     # ±25 enheter
maaling             = 66     # ligger innenfor måleusikkerheten,
                             # men utenfor toleranseintervallet

# ---- Lag figur ----
fig, ax = plt.subplots(figsize=(9, 4.5))

# Måleusikkerhet (bredt slate-bånd)
ax.add_patch(Rectangle(
    (sann_verdi - halv_usikkerhet, -0.4),
    2 * halv_usikkerhet, 0.8,
    facecolor=SLATE_FYLL, edgecolor=SLATE_KANT, linewidth=1.5, zorder=1,
))

# Toleranse (smalt stone-bånd, oppå)
ax.add_patch(Rectangle(
    (sann_verdi - halv_toleranse, -0.9),
    2 * halv_toleranse, 1.8,
    facecolor=STONE_FYLL, edgecolor=STONE_KANT, linewidth=1.5, zorder=2,
))

# Tallinje
ax.hlines(0, sann_verdi - 35, sann_verdi + 35,
          color=TALLINJE, linewidth=2, zorder=3)
ax.vlines([sann_verdi - 35, sann_verdi + 35], -0.5, 0.5,
          color=TALLINJE, linewidth=2, zorder=3)

# Sann verdi (vertikal strek)
ax.vlines(sann_verdi, -1.6, 1.6,
          color=SANN_VERDI, linewidth=3.5, zorder=4)
ax.text(sann_verdi, 2.0, "Sann verdi",
        ha="center", va="bottom",
        color=SANN_VERDI, fontsize=12, fontweight="bold")

# Én måling (punkt + leader-linje + label)
ax.plot(maaling, 0, "o", color=MAALING, markersize=11,
        markeredgecolor=MAALING, zorder=5)
ax.annotate(
    "Én måling",
    xy=(maaling, 0.15), xytext=(maaling + 8, 2.2),
    color=MAALING, fontsize=12, fontweight="bold",
    arrowprops=dict(arrowstyle="-", color=MAALING,
                    linewidth=1.0, linestyle=(0, (3, 2))),
)

# Klamme + label for toleranse
y_tol = -2.0
ax.plot([sann_verdi - halv_toleranse, sann_verdi - halv_toleranse,
         sann_verdi + halv_toleranse, sann_verdi + halv_toleranse],
        [y_tol + 0.15, y_tol, y_tol, y_tol + 0.15],
        color=STONE_KANT, linewidth=2)
ax.text(sann_verdi, y_tol - 0.45, "Toleranse",
        ha="center", va="top",
        color=STONE_TEKST, fontsize=12, fontweight="bold")
ax.text(sann_verdi, y_tol - 1.05,
        "instrumentets feilmargin",
        ha="center", va="top",
        color=STONE_TEKST, fontsize=10, style="italic")

# Klamme + label for måleusikkerhet
y_us = -3.5
ax.plot([sann_verdi - halv_usikkerhet, sann_verdi - halv_usikkerhet,
         sann_verdi + halv_usikkerhet, sann_verdi + halv_usikkerhet],
        [y_us + 0.15, y_us, y_us, y_us + 0.15],
        color=SLATE_KANT, linewidth=2)
ax.text(sann_verdi, y_us - 0.45, "Måleusikkerhet",
        ha="center", va="top",
        color=SLATE_TEKST, fontsize=12, fontweight="bold")
ax.text(sann_verdi, y_us - 1.05,
        "toleranse + avlesning + andre feilkilder",
        ha="center", va="top",
        color=SLATE_TEKST, fontsize=10, style="italic")

# Rydd opp aksene
ax.set_xlim(sann_verdi - 38, sann_verdi + 38)
ax.set_ylim(-5.5, 3.2)
ax.set_aspect("auto")
ax.axis("off")

plt.tight_layout()

# ---- Lagre i samme mappe som scriptet ----
plt.savefig("toleranse_figur.png", dpi=200,
            bbox_inches="tight", facecolor="white")
plt.savefig("toleranse_figur.svg",
            bbox_inches="tight", facecolor="white")
plt.savefig("toleranse_figur.pdf",
            bbox_inches="tight", facecolor="white")

print("Lagret PNG, SVG og PDF i samme mappe som scriptet.")