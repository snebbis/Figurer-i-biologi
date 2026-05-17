import numpy as np
import matplotlib.pyplot as plt

# Miljøgradient (x-akse)
x = np.linspace(0, 10, 500)

def gauss(x, mu, sigma, amp):
    return amp * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

# Tre Gauss-kurver
fundamental_A = gauss(x, mu=5.0, sigma=2.3, amp=1.00)  # bred potensiell nisje
realisert_A   = gauss(x, mu=6.5, sigma=1.3, amp=0.88)  # smalere, forskjøvet
konkurrent_B  = gauss(x, mu=3.0, sigma=1.5, amp=0.92)  # overlappende konkurrent

# Figur
fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Fundamental nisje — stiplet omriss
ax.plot(x, fundamental_A, color="#0C447C", linewidth=2.2,
        linestyle=(0, (7, 5)), label="Fundamental nisje (art A)")

# Realisert nisje — fylt
ax.fill_between(x, realisert_A, color="#378ADD", alpha=0.32)
ax.plot(x, realisert_A, color="#0C447C", linewidth=2.0,
        label="Realisert nisje (art A)")

# Konkurrerende art — fylt
ax.fill_between(x, konkurrent_B, color="#D85A30", alpha=0.28)
ax.plot(x, konkurrent_B, color="#993C1D", linewidth=2.0,
        label="Konkurrerende art (B)")

# Akser
ax.set_xlabel("Miljøgradient (f.eks. temperatur, ressurstilgang)", fontsize=15)
ax.set_ylabel("Populasjonsytelse / sannsynlighet for forekomst", fontsize=15)

ax.set_xlim(0, 10)
ax.set_ylim(0, 1.15)
ax.set_xticks([])
ax.set_yticks([])

# Rens opp rammen — behold kun venstre og bunn
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.spines["left"].set_linewidth(1.2)
ax.spines["bottom"].set_linewidth(1.2)

ax.legend(frameon=False, fontsize=12, loc="upper right")

plt.tight_layout()
plt.savefig("/home/claude/nisje_diagram.png", dpi=150, facecolor="white")
plt.savefig("/mnt/user-data/outputs/nisje_diagram.png", dpi=150, facecolor="white")
print("Lagret.")
