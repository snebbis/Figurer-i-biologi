"""
Figur til FRA FORSKERVERDEN: E. coli Long-Term Evolution Experiment (LTEE)

Genererer et linjediagram over relativ fitness gjennom ~60 000 generasjoner,
basert på publiserte data fra Wiser et al. (2013) Science og Lenski et al. (2015)
Proc. R. Soc. B. Verdiene er omtrentlige gjennomsnitt over 12 populasjoner.

Citrat-hendelsen (Ara-3, ~gen. 31 500) er markert spesielt.

BRUK:
  Legg ltee_data.csv i samme mappe som dette scriptet og kjør:
    python make_ltee_fig.py

AVHENGIGHETER:
  pip install matplotlib numpy pandas

Kilde:
  Wiser MJ, Ribeck N, Lenski RE (2013) Science 342:1364-1367
  Lenski RE et al. (2015) Proc R Soc B 282:20152292
"""

import matplotlib
matplotlib.use('Agg')  # Fjern denne linjen hvis du vil vise figuren interaktivt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path

# ──────────────────────────────────────────────
# LES DATA
# ──────────────────────────────────────────────
datadir = Path(__file__).parent
df = pd.read_csv(datadir / "ltee_data.csv")

# Gjennomsnitt (12 populasjoner) — dropp rader uten snitt-data
snitt = df.dropna(subset=["fitness_snitt"])
gen = snitt["generasjon"].values
fit = snitt["fitness_snitt"].values
se  = snitt["fitness_se"].values

# Ara-3 (citrat-populasjonen) — dropp rader uten Ara-3-data
ara3 = df.dropna(subset=["ara3_fitness"])
ara3_gen = ara3["generasjon"].values
ara3_fit = ara3["ara3_fitness"].values

# ──────────────────────────────────────────────
# FIGUR
# ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6), facecolor='white')

# Gjennomsnitt over 12 populasjoner (med feilstolper)
ax.errorbar(gen, fit, yerr=se,
            fmt='o-', color='#1565C0', markersize=5, linewidth=2,
            capsize=3, capthick=1.2, ecolor='#90CAF9',
            label='Gjennomsnitt (12 populasjoner)', zorder=3)

# Ara-3: citrat-populasjonen
ax.plot(ara3_gen, ara3_fit, 's--', color='#E65100', markersize=5,
        linewidth=1.8, label='Populasjon Ara\u22123 (Cit\u207A)', zorder=4)

# Marker citrat-hendelsen
ax.annotate('Evolusjon av citratbruk\n(~generasjon 31 500)',
            xy=(31500, 1.63), xytext=(38000, 1.40),
            fontsize=9.5, color='#BF360C', fontweight='medium',
            arrowprops=dict(arrowstyle='->', color='#E65100', lw=1.5),
            bbox=dict(facecolor='#FFF3E0', edgecolor='#E65100',
                      boxstyle='round,pad=0.4', alpha=0.95))

# Referanselinje: stamfaren
ax.axhline(y=1.0, color='gray', linestyle=':', linewidth=1, alpha=0.7)
ax.text(61000, 1.005, 'Stamfar\n(1988)', fontsize=8, color='gray',
        va='bottom', ha='left', fontstyle='italic')

# ──────────────────────────────────────────────
# FORMATERING
# ──────────────────────────────────────────────
ax.set_xlabel('Generasjoner (tusen)', fontsize=12, labelpad=8)
ax.set_ylabel('Relativ fitness', fontsize=12, labelpad=8)
ax.set_title('E. coli Long-Term Evolution Experiment (LTEE)',
             fontsize=14, fontweight='bold', pad=12, color='#1A237E')

ax.set_xlim(-1500, 65000)
ax.set_ylim(0.95, 2.15)
ax.xaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, _: f'{int(x/1000)}' if x >= 1000 else '0'))
ax.xaxis.set_major_locator(ticker.MultipleLocator(10000))
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))

# Sekundaer akse med omtrentlige arstall
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
year_ticks  = [0, 10000, 20000, 30000, 40000, 50000, 60000]
year_labels = ['1988', '1993', '1997', '2002', '2006', '2010', '2014']
ax2.set_xticks(year_ticks)
ax2.set_xticklabels(year_labels, fontsize=8, color='#666666')
ax2.set_xlabel('Omtrentlig arstall', fontsize=9, color='#666666', labelpad=6)
ax2.tick_params(axis='x', colors='#999999', length=3)

# Bakgrunn og rutenett
ax.set_facecolor('#FAFAFA')
ax.grid(True, alpha=0.3, linestyle='-', color='#CCCCCC')
ax.tick_params(labelsize=10)

# ──────────────────────────────────────────────
# ANNOTASJONER
# ──────────────────────────────────────────────
ax.annotate('Rask tilpasning\n(de forste 5 000 gen.)',
            xy=(3000, 1.25), xytext=(8000, 1.08),
            fontsize=9, color='#1565C0', fontstyle='italic',
            arrowprops=dict(arrowstyle='->', color='#1565C0', lw=1.2),
            bbox=dict(facecolor='#E3F2FD', edgecolor='#1565C0',
                      boxstyle='round,pad=0.3', alpha=0.9))

# Flyttet annotasjon for fortsatt økning opp og til venstre, pil med bue
ax.annotate('Fortsatt økning \u2013 ingen\nobservert øvre grense',
            xy=(55000, 1.77), xytext=(40000, 2.05),
            fontsize=9, color='#1565C0', fontstyle='italic',
            arrowprops=dict(arrowstyle='->', color='#1565C0', lw=1.2,
                            connectionstyle="arc3,rad=-0.2"),
            bbox=dict(facecolor='#E3F2FD', edgecolor='#1565C0',
                      boxstyle='round,pad=0.3', alpha=0.9))

# Legend
ax.legend(loc='lower right', fontsize=10, framealpha=0.95,
          edgecolor='#CCCCCC', fancybox=True)

# ──────────────────────────────────────────────
# LAGRE
# ──────────────────────────────────────────────
output_path = datadir / "fig_LTEE_fitness.png"
fig.tight_layout()
fig.savefig(output_path, dpi=250, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"Figur lagret: {output_path}")
plt.close()