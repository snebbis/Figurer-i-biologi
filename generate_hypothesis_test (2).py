import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.linewidth': 1.0,
})

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)
fig.subplots_adjust(wspace=0.35)

x = np.linspace(-4, 4, 500)
y = norm.pdf(x, 0, 1)

alpha = 0.05
z_crit = norm.ppf(1 - alpha / 2)

x_left = x[x <= -z_crit]
x_right = x[x >= z_crit]
x_mid = x[(x >= -z_crit) & (x <= z_crit)]

def draw_base(ax):
    ax.set_yticks([])
    ax.set_xlim(-4, 4)
    ax.set_ylim(0, 0.47)
    ax.set_xlabel('Teststørrelse', fontsize=12)

    ax.fill_between(x, y, alpha=0.08, color='black')
    ax.plot(x, y, color='black', linewidth=2)

    # Forkastningsområder (røde haler)
    ax.fill_between(x_left, norm.pdf(x_left, 0, 1), color='#EF5350', alpha=0.35, zorder=2)
    ax.fill_between(x_right, norm.pdf(x_right, 0, 1), color='#EF5350', alpha=0.35, zorder=2)

    # Midtområde (grønt)
    ax.fill_between(x_mid, norm.pdf(x_mid, 0, 1), color='#66BB6A', alpha=0.25, zorder=2)

    # Kritiske verdier
    ax.axvline(-z_crit, color='#C62828', linewidth=1.5, linestyle='--', alpha=0.7, zorder=3)
    ax.axvline(z_crit, color='#C62828', linewidth=1.5, linestyle='--', alpha=0.7, zorder=3)

# ─────────────────────────────────────────
# (a) Beholder nullhypotesen
# ─────────────────────────────────────────
ax = axes[0]
draw_base(ax)
ax.set_title('(a) Beholder H₀', fontsize=15, fontweight='bold', pad=12)

obs_a = 1.1
ax.axvline(obs_a, color='#1565C0', linewidth=2.5, zorder=4)
ax.plot(obs_a, 0.44, 'v', color='#1565C0', markersize=10, zorder=5)

# p-verdi: skravert i begge haler (tosidig test)
x_pval_right_a = x[x >= obs_a]
x_pval_left_a = x[x <= -obs_a]
ax.fill_between(x_pval_right_a, norm.pdf(x_pval_right_a, 0, 1), facecolor='#1565C0', alpha=0.15,
                edgecolor='#1565C0', linewidth=0.8, hatch='////', zorder=4)
ax.fill_between(x_pval_left_a, norm.pdf(x_pval_left_a, 0, 1), facecolor='#1565C0', alpha=0.15,
                edgecolor='#1565C0', linewidth=0.8, hatch='////', zorder=4)


# ─────────────────────────────────────────
# (b) Forkaster nullhypotesen
# ─────────────────────────────────────────
ax = axes[1]
draw_base(ax)
ax.set_title('(b) Forkaster H₀', fontsize=15, fontweight='bold', pad=12)

obs_b = 2.4
ax.axvline(obs_b, color='#1565C0', linewidth=2.5, zorder=4)
ax.plot(obs_b, 0.44, 'v', color='#1565C0', markersize=10, zorder=5)

# p-verdi: skravert over eksisterende farger (begge haler)
x_pval_right_b = x[x >= obs_b]
x_pval_left_b = x[x <= -obs_b]
ax.fill_between(x_pval_right_b, norm.pdf(x_pval_right_b, 0, 1), facecolor='#1565C0', alpha=0.15,
                edgecolor='#1565C0', linewidth=0.8, hatch='////', zorder=4)
ax.fill_between(x_pval_left_b, norm.pdf(x_pval_left_b, 0, 1), facecolor='#1565C0', alpha=0.15,
                edgecolor='#1565C0', linewidth=0.8, hatch='////', zorder=4)


plt.savefig('/home/claude/figur_hypotesetesting.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Figur lagret!")
