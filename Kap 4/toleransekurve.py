import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 40, 500)
mu, sigma = 20, 5
y = np.exp(-(x - mu)**2 / (2 * sigma**2))

# Zone boundaries
min_lo, min_hi = 5, 11
opt_lo, opt_hi = 17, 23
max_lo, max_hi = 29, 35

fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

# Shade zones
ax.fill_between(x, 0, y, where=(x <= min_hi), color='#F7C1C1', alpha=0.7)
ax.fill_between(x, 0, y, where=(x >= max_lo), color='#F7C1C1', alpha=0.7)
ax.fill_between(x, 0, y, where=((x > min_hi) & (x < opt_lo)), color='#FAC775', alpha=0.6)
ax.fill_between(x, 0, y, where=((x > opt_hi) & (x < max_lo)), color='#FAC775', alpha=0.6)
ax.fill_between(x, 0, y, where=((x >= opt_lo) & (x <= opt_hi)), color='#97C459', alpha=0.7)

# Curve
ax.plot(x, y, color='#185FA5', linewidth=2.8)

# Vertical guide lines (uten labels)
for xv in [min_hi, mu, max_lo]:
    ax.axvline(xv, color='#444', linestyle='--', linewidth=1, alpha=0.6)

# Axes labels (større skrift)
ax.set_xlabel('Abiotisk faktor (f.eks. temperatur) →', fontsize=18)
ax.set_ylabel('Ytelse / overlevelse / trivsel →', fontsize=18)

# Fjernet tittel
# ax.set_title(...)

ax.set_xlim(0, 40)
ax.set_ylim(0, 1.25)

ax.set_xticks([])
ax.set_yticks([])

# Fjern topp og høyre kant
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)

ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# Større tick-labels (selv om ticks er skjult nå, beholdes for fleksibilitet)
ax.tick_params(axis='both', labelsize=14)

# Fjernet legend
# ax.legend(...)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/toleransekurve.png',
            dpi=300, bbox_inches='tight', facecolor='white')