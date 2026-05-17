import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

def lv(state, t, a, b, c, d):
    prey, pred = state
    dprey = a * prey - b * prey * pred
    dpred = -c * pred + d * prey * pred
    return [dprey, dpred]

# 4 full cycles (IKKE siste peak)
t = np.linspace(0, 28, 2000)

sol = odeint(lv, [10, 5], t, args=(1.1, 0.4, 0.9, 0.1))
lemmings = sol[:, 0]
foxes = sol[:, 1]

def norm(y, lo, hi):
    y = (y - y.min()) / (y.max() - y.min())
    return lo + y * (hi - lo)

lemmings_n = norm(lemmings, 0.20, 0.92)
foxes_n    = norm(foxes,    0.28, 0.65)

fig, ax = plt.subplots(figsize=(11, 6.4), dpi=150)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

ax.set_xlim(t[0], t[-1])
ax.set_ylim(0, 1)

# Curves
ax.plot(t, lemmings_n, color="#B8672E", linewidth=2.8,
        solid_capstyle="round", label="Lemen (byttedyr)")
ax.plot(t, foxes_n, color="#4A6B82", linewidth=2.8,
        solid_capstyle="round", label="Fjellrev (predator)")

# Labels (bigger font)
ax.set_xlabel("Tid", fontsize=20, labelpad=15)
ax.set_ylabel("Populasjonsstørrelse", fontsize=20, labelpad=15)

ax.set_xticks([])
ax.set_yticks([])

# Remove default spines
for side in ("top", "right", "bottom", "left"):
    ax.spines[side].set_visible(False)

# Axis arrows
ax.annotate("", xy=(t[-1], 0), xytext=(t[0], 0),
            arrowprops=dict(arrowstyle="->", linewidth=1.8, color="black"))

ax.annotate("", xy=(t[0], 1), xytext=(t[0], 0),
            arrowprops=dict(arrowstyle="->", linewidth=1.8, color="black"))

# Legend
ax.legend(frameon=False, fontsize=20, ncol=2,
          loc="lower center", bbox_to_anchor=(0.5, 1.02))

plt.tight_layout()

# Save (Windows path)
save_path = r"C:\Users\sebastianb_a\OneDrive - Akershus fylkeskommune\Skrivebord\FORFATTER\Biologi 1\Figurer\Kap 4\tundra_cycles.png"

plt.savefig(save_path, dpi=200, facecolor="white", bbox_inches="tight")
plt.show()

print("Lagret til:", save_path)