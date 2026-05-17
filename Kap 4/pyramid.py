import matplotlib.pyplot as plt
import numpy as np

ages = ['0–4','5–9','10–14','15–19','20–24','25–29','30–34','35–39','40–44',
        '45–49','50–54','55–59','60–64','65–69','70–74','75–79','80+']
y = np.arange(len(ages))

ng_m = [7.7,6.9,6.2,5.4,4.6,3.9,3.2,2.6,2.1,1.6,1.2,0.9,0.7,0.5,0.3,0.2,0.1]
ng_f = [7.5,6.7,6.0,5.3,4.6,4.0,3.3,2.7,2.2,1.7,1.3,1.0,0.8,0.6,0.4,0.3,0.2]
jp_m = [1.8,2.0,2.1,2.2,2.3,2.5,2.7,2.9,3.2,3.7,4.2,4.0,3.5,3.2,3.8,3.0,3.5]
jp_f = [1.7,1.9,2.0,2.1,2.2,2.4,2.6,2.8,3.1,3.6,4.1,3.9,3.5,3.3,4.0,3.4,5.5]

fig, axes = plt.subplots(1, 2, figsize=(13, 8), sharey=True, dpi=300)
male_c, female_c = '#378ADD', '#D4537E'

for ax, (title, m, f) in zip(axes, [('Nigeria', ng_m, ng_f), ('Japan', jp_m, jp_f)]):
    ax.barh(y, [-v for v in m], color=male_c, edgecolor='white', linewidth=0.3, label='Menn')
    ax.barh(y, f, color=female_c, edgecolor='white', linewidth=0.3, label='Kvinner')
    ax.set_title(title, fontsize=18, fontweight='bold', pad=12)
    ax.set_xlim(-9, 9)
    ax.set_xticks(range(-8, 9, 2))
    ax.set_xticklabels([f'{abs(t)}%' for t in range(-8, 9, 2)], fontsize=15)
    ax.set_xlabel('Andel av befolkning (%)', fontsize=14)
    ax.axvline(0, color='#444', linewidth=0.6)
    ax.grid(axis='x', linestyle=':', alpha=0.4)
    ax.set_axisbelow(True)
    for s in ['top','right']: ax.spines[s].set_visible(False)

axes[0].set_yticks(y)
axes[0].set_yticklabels(ages, fontsize=15)
axes[0].set_ylabel('Aldersgruppe (år)', fontsize=14)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=2, frameon=False,
           fontsize=14, bbox_to_anchor=(0.5, -0.01))
fig.suptitle('Befolkningspyramide: Nigeria og Japan',
             fontsize=19, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('/mnt/user-data/outputs/befolkningspyramide_nigeria_japan.png',
            dpi=300, bbox_inches='tight', facecolor='white')
