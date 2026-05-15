import numpy as np
import matplotlib.pyplot as plt

# --- Styling ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 13,  # generell font for figurtitler, overskrifter
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 1.0,
})

fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=200)
fig.subplots_adjust(wspace=0.35)

# ─────────────────────────────────────────────
# (a) Søylediagram – Gjennomsnittlig bladareal
# ─────────────────────────────────────────────
ax = axes[0]
arter = ['Bjørk', 'Eik', 'Lønn', 'Hassel', 'Selje']
bladareal = [18.2, 38.5, 52.1, 28.7, 12.4]
feil = [2.1, 4.3, 5.8, 3.2, 1.6]
colors_bar = ['#5B9E6F', '#4A8A5E', '#3D7A52', '#6BAE7E', '#7CBE8E']

bars = ax.bar(arter, bladareal, color=colors_bar, edgecolor='white', linewidth=0.8,
              yerr=feil, capsize=4, error_kw={'linewidth': 1.2, 'color': '#444444'})
ax.set_ylabel('Gjennomsnittlig bladareal (cm²)', fontsize=13)
ax.set_xlabel('Art', fontsize=13)
ax.set_title('(a) Søylediagram', fontsize=14, fontweight='bold', pad=12)
ax.set_ylim(0, 65)
ax.tick_params(axis='x', rotation=20, labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# ─────────────────────────────────────────────
# (b) Linjediagram – Populasjonsvekst over tid
# ─────────────────────────────────────────────
ax = axes[1]
dager = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])

# Logistisk vekst med litt støy
np.random.seed(42)
K = 950  # bæreevne
r = 0.35
N0 = 50
populasjon = K / (1 + ((K - N0) / N0) * np.exp(-r * dager))
populasjon_noise = populasjon + np.random.normal(0, 25, len(dager))
populasjon_noise = np.clip(populasjon_noise, 30, 1000)

ax.plot(dager, populasjon_noise, color='#D4602A', linewidth=2.2, marker='o',
        markersize=5, markerfacecolor='#D4602A', markeredgecolor='white', markeredgewidth=1)
ax.fill_between(dager, populasjon_noise - 40, populasjon_noise + 40,
                color='#D4602A', alpha=0.12)
ax.set_ylabel('Antall individer', fontsize=13)
ax.set_xlabel('Tid (dager)', fontsize=13)
ax.set_title('(b) Linjediagram', fontsize=14, fontweight='bold', pad=12)
ax.set_ylim(0, 1100)
ax.set_xlim(-0.5, 20.5)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# Legg til bæreevne-linje
ax.axhline(K, color='#888888', linestyle='--', linewidth=1, alpha=0.7)
ax.text(20.3, K + 20, 'K', fontsize=10, color='#888888', va='bottom')

# ─────────────────────────────────────────────
# (c) Punktdiagram – Kroppsmasse vs. hjerterate
# ─────────────────────────────────────────────
ax = axes[2]

np.random.seed(7)
masse = np.array([0.02, 0.03, 0.18, 0.3, 0.5, 2, 4, 5, 25, 35, 60, 75, 180, 400, 600, 4000])
hjerterate_base = 220 * masse ** (-0.25)
hjerterate = hjerterate_base * (1 + np.random.normal(0, 0.08, len(masse)))

dyrenavn = ['Mus', 'Spissmus', 'Rotte', '', 'Kanin', 'Katt', '', 'Hund', '',
            'Gris', 'Menneske', '', 'Hjort', 'Ku', 'Hest', 'Elefant']

ax.scatter(masse, hjerterate, color='#4A6FA5', s=55, edgecolor='white', linewidth=0.8, zorder=3)

# Trendlinje
masse_fit = np.logspace(np.log10(0.015), np.log10(5000), 200)
hjerterate_fit = 220 * masse_fit ** (-0.25)
ax.plot(masse_fit, hjerterate_fit, color='#4A6FA5', linewidth=1.5, alpha=0.4, linestyle='--')

# Annotere dyr
for i, navn in enumerate(dyrenavn):
    if navn:
        offset_x = 5
        offset_y = 8
        if navn == 'Mus':
            offset_x, offset_y = 8, 5
        elif navn == 'Spissmus':
            offset_x, offset_y = 8, -12
        elif navn == 'Elefant':
            offset_x, offset_y = -10, 10
            ax.annotate(navn, (masse[i], hjerterate[i]), fontsize=9.5, color='#555555',
                        textcoords='offset points', xytext=(offset_x, offset_y),
                        ha='right')
            continue
        ax.annotate(navn, (masse[i], hjerterate[i]), fontsize=9.5, color='#555555',
                    textcoords='offset points', xytext=(offset_x, offset_y))

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylabel('Hjerterate (slag/min)', fontsize=13)
ax.set_xlabel('Kroppsmasse (kg)', fontsize=13)
ax.set_title('(c) Punktdiagram', fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(0.01, 8000)
ax.set_ylim(15, 800)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

plt.savefig('/home/claude/figur_diagramtyper.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("Figur lagret!")