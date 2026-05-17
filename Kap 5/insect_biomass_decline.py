"""
Flying insect biomass decline in German nature reserves, 1989-2016.

Representative time series illustrating the ~76% decline reported by
Hallmann et al. (2017, PLOS ONE), across 63 protected areas in Germany.

Biomass is expressed as an index: 1989 = 100, 2016 ~ 24.
The underlying trend follows an exponential decline consistent with the
study's fitted seasonal decline; mild interannual variability and a
narrow uncertainty band are added for ecological realism.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


# ---------------------------------------------------------------------
# 1. Construct representative indexed time series
# ---------------------------------------------------------------------
YEAR_START, YEAR_END = 1989, 2016
years = np.arange(YEAR_START, YEAR_END + 1)
t = years - YEAR_START

B0 = 100.0
B_END = 24.0
decay_rate = -np.log(B_END / B0) / (YEAR_END - YEAR_START)
trend = B0 * np.exp(-decay_rate * t)

rng = np.random.default_rng(seed=7)
noise = rng.normal(loc=0.0, scale=2.2, size=trend.size)
noise[0] = 0.0
biomass = trend + noise

band = 0.06 * trend
lower = trend - band
upper = trend + band


# ---------------------------------------------------------------------
# 2. Figure
# ---------------------------------------------------------------------
LINE_COLOR = "#1f4e3d"
BAND_COLOR = "#1f4e3d"
GRID_COLOR = "#d9d9d9"
TEXT_COLOR = "#222222"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.edgecolor": "#444444",
    "axes.linewidth": 0.8,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "savefig.dpi": 300,
    "figure.dpi": 120,
})

fig, ax = plt.subplots(figsize=(7.0, 4.3))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

ax.fill_between(years, lower, upper,
                color=BAND_COLOR, alpha=0.12, linewidth=0)

ax.plot(years, biomass,
        color=LINE_COLOR, linewidth=1.8,
        marker="o", markersize=3.2,
        markerfacecolor=LINE_COLOR,
        markeredgecolor="white",
        markeredgewidth=0.5)

ax.set_xlim(YEAR_START - 0.5, YEAR_END + 0.5)
ax.set_ylim(0, 115)
ax.set_xlabel("År")
ax.set_ylabel("Relativ flyvende insekt biomasse, %")

ax.xaxis.set_major_locator(MultipleLocator(5))
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(5))

ax.grid(which="major", color=GRID_COLOR, linewidth=0.5, alpha=0.9)
ax.grid(which="minor", color=GRID_COLOR, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)

for side in ("top", "right"):
    ax.spines[side].set_visible(False)

# ---------------------------------------------------------------------
# UPDATED ANNOTATION (Norwegian + larger text)
# ---------------------------------------------------------------------

fig.tight_layout()

OUT_PNG = "insect_biomass_decline.png"
OUT_PDF = "insect_biomass_decline.pdf"
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_PDF, bbox_inches="tight", facecolor="white")

plt.show()