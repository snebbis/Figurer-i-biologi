"""
Oxygen depth profile: healthy (oligotrophic) vs eutrophic (polluted) lake.

Visualises the classic orthograde vs clinograde dissolved-oxygen profiles
that are diagnostic of lake health. The healthy lake shows gentle O2 decline
with depth; the eutrophic lake shows supersaturated surface (from algal
blooms) collapsing through the thermocline into a hypoxic/anoxic dead zone.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

# ---- Colour palette (matches the illustrative version) ------------------
COLOR_HEALTHY = "#1D9E75"   # teal  — well-oxygenated, living water
COLOR_EUTROPHIC = "#D85A30"  # coral — oxygen-depleted, dead zone
COLOR_HYPOXIC = "#993C1D"    # dark coral for threshold / warning text
COLOR_ORTHOGRADE_LABEL = "#0F6E56"  # dark teal for healthy annotation

# ---- Depth grid ----------------------------------------------------------
depth = np.linspace(0, 20, 400)

# ---- Healthy lake: orthograde profile ------------------------------------
# Oxygen stays high throughout the water column. Small decline with depth
# reflects modest biological oxygen demand at the bottom and reduced
# photosynthesis below the euphotic zone.
healthy_depths = np.array([0, 5, 10, 15, 20])
healthy_o2 = np.array([10.0, 9.7, 9.3, 8.6, 8.0])
healthy_curve = PchipInterpolator(healthy_depths, healthy_o2)(depth)

# ---- Eutrophic lake: clinograde profile ----------------------------------
# Surface is supersaturated because the algal bloom photosynthesises hard
# during the day. Below the thermocline (~5-8 m) oxygen collapses as
# sinking dead algae are decomposed by bacteria that consume O2 faster
# than it can be replenished. Bottom waters become hypoxic (<2 mg/L) and
# eventually anoxic (~0 mg/L).
eutrophic_depths = np.array([0, 2, 4, 5.5, 7, 9, 11, 14, 20])
eutrophic_o2 = np.array([11.5, 10.5, 8.5, 5.0, 2.0, 0.5, 0.1, 0.0, 0.0])
eutrophic_curve = PchipInterpolator(eutrophic_depths, eutrophic_o2)(depth)

# ---- Plot ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))

# Hypoxic zone shading (0-2 mg/L, full depth)
ax.axvspan(0, 2, alpha=0.08, color=COLOR_EUTROPHIC, zorder=0)

# Hypoxic threshold line
ax.axvline(2, color=COLOR_HYPOXIC, linestyle="--",
           linewidth=0.9, alpha=0.7, zorder=1)

# Curves
ax.plot(healthy_curve, depth, color=COLOR_HEALTHY, linewidth=3,
        label="Healthy lake (oligotrophic)", zorder=3)
ax.plot(eutrophic_curve, depth, color=COLOR_EUTROPHIC, linewidth=3,
        label="Eutrophic lake (polluted)", zorder=3)

# Axes: depth increases downward, oxygen on top axis
ax.invert_yaxis()
ax.set_xlim(0, 12)
ax.set_ylim(20, 0)
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")
ax.set_xlabel("Dissolved oxygen (mg/L)", fontsize=12, labelpad=10)
ax.set_ylabel("Depth (m)", fontsize=12)

# Grid
ax.grid(True, linestyle=":", alpha=0.35, zorder=0)
ax.set_axisbelow(True)

# Spines: keep it clean
for spine in ("right",):
    ax.spines[spine].set_visible(False)

# ---- Annotations --------------------------------------------------------
ax.text(7.6, 1.6, "Surface supersaturation\n(algal bloom)",
        ha="center", fontsize=10, color=COLOR_EUTROPHIC, style="italic")

ax.text(7.8, 6.3, "Sharp collapse\nthrough thermocline",
        ha="left", fontsize=10, color=COLOR_HYPOXIC, style="italic")

ax.text(5.2, 15, "Gradual decline\n(orthograde profile)",
        ha="center", fontsize=10, color=COLOR_ORTHOGRADE_LABEL,
        style="italic")

ax.text(0.25, 18.3, "Anoxic zone\nno aerobic life",
        ha="left", fontsize=10, color=COLOR_HYPOXIC, style="italic")

ax.text(2.2, 0.6, "2 mg/L — hypoxia threshold",
        ha="left", fontsize=9, color=COLOR_HYPOXIC)

# Legend
ax.legend(loc="lower right", fontsize=10, framealpha=0.95,
          edgecolor="#cccccc")

# Title — extra pad because x-axis sits at the top
ax.set_title("Dissolved oxygen profiles: healthy vs eutrophic lake",
             fontsize=14, pad=45, fontweight="medium")

plt.tight_layout()
plt.savefig("/home/claude/oxygen_depth_profile.png",
            dpi=150, bbox_inches="tight", facecolor="white")
print("Saved: oxygen_depth_profile.png")
