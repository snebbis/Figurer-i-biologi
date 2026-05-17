"""
Økologisk suksesjon — konseptuelt linjediagram (Oppdatert fargeversjon).
Genererer en ren, vitenskapelig figur av plante-biomasse over tid
gjennom successionstrinnene med en 'Slate & Stone' inspirert palett.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- Tidsakse (konseptuell, 0 = pioneerstadium, 10 = klimaks) ---
t = np.linspace(0, 10, 600)


# --- Hjelpefunksjoner for glatte kurver ---
def gauss(t, mu, sigma, amp):
    """Symmetrisk Gauss-kurve — egnet for arter som stiger og synker."""
    return amp * np.exp(-((t - mu) / sigma) ** 2)


def sigmoid(t, midpoint, steepness, amp):
    """Logistisk kurve — egnet for arter som stiger sakte til en stabil topp."""
    return amp / (1.0 + np.exp(-(t - midpoint) / steepness))


# --- Biomassekurver per art ---
gress      = gauss(t, mu=1.0, sigma=0.9, amp=6.0)   # tidlig topp
busker     = gauss(t, mu=3.0, sigma=1.2, amp=5.0)   # etter gresset
bjorketrar = gauss(t, mu=5.0, sigma=1.5, amp=7.0)   # midt i suksesjonen
lonnetrar   = gauss(t, mu=7.5, sigma=1.8, amp=6.0)  # gradvis økning
grantrar   = sigmoid(t, midpoint=6.5, steepness=0.9, amp=9.0)  # klimaks


# --- Palette: Slate, Stone, Red & Green ---
COLOR_GRESS  = '#689F38'   # Frisk gressgrønn (Tydelig grønn)
COLOR_BUSKER = '#78909C'   # Slate Blue/Grey (Skifer)
COLOR_BJORK  = '#9E9E9E'   # Stone Grey (Stein)
COLOR_LONN   = '#C62828'   # Deep Red (Tydelig rød)
COLOR_GRAN   = '#263238'   # Dark Slate/Anthracite (Mørk "norsk" gran/stein)


# --- Figur ---
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

LW = 2.5 # Litt tykkere linjer for bedre synlighet med de nye fargene
ax.plot(t, gress,      color=COLOR_GRESS,  linewidth=LW)
ax.plot(t, busker,     color=COLOR_BUSKER, linewidth=LW)
ax.plot(t, bjorketrar, color=COLOR_BJORK,  linewidth=LW)
ax.plot(t, lonnetrar,   color=COLOR_LONN,   linewidth=LW)
ax.plot(t, grantrar,   color=COLOR_GRAN,   linewidth=LW)

# Etiketter ved hver kurve
ax.text(1.0, 6.35, 'Gress',      fontsize=12, ha='center', va='bottom', color=COLOR_GRESS, fontweight='bold')
ax.text(3.0, 5.35, 'Busker',     fontsize=12, ha='center', va='bottom', color=COLOR_BUSKER, fontweight='bold')
ax.text(5.0, 7.35, 'Bjørketrær', fontsize=12, ha='center', va='bottom', color=COLOR_BJORK, fontweight='bold')

# Oppdatert navn og flyttet posisjon (x fra 7.6 til 8.2) for å unngå gran-kurven
ax.text(8.2, 5.20, 'Lønnetrær',  fontsize=12, ha='left', va='bottom', color=COLOR_LONN, fontweight='bold')

ax.text(9.4, 9.30, 'Grantrær',   fontsize=12, ha='center', va='bottom', color=COLOR_GRAN, fontweight='bold')

# --- Akser som piler fra origo ---
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])
ax.grid(False)

ax.set_xlim(0, 11)
ax.set_ylim(0, 11)

ARROW_KW = dict(arrowstyle='-|>', color='black', lw=1.2, mutation_scale=18)
ax.annotate('', xy=(10.6, 0), xytext=(0, 0), arrowprops=ARROW_KW)
ax.annotate('', xy=(0, 10.6), xytext=(0, 0), arrowprops=ARROW_KW)

# Akseetiketter
ax.text(10.75, 0,     'Tid',                 fontsize=13, ha='left', va='center')
ax.text(0,     10.85, 'Biomasse av planter', fontsize=13, ha='left', va='bottom')

plt.tight_layout()
plt.savefig('okologisk_suksesjon_oppdatert.png', dpi=300, bbox_inches='tight')
plt.show()

print("Lagret: okologisk_suksesjon_oppdatert.png")