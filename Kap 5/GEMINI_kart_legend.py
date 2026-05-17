import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def generate_norwegian_map_legend_png():
    # Bruker standard hvit stil
    plt.style.use('default')
    
    # Konfigurasjon for farger (ArcGIS-stil)
    colors = {
        "Naturreservat": "#00441b",          # Mørk grønn
        "Nasjonalparker": "#41ab5d",         # Klar grønn
        "Landskapsvernområder": "#c2e699",    # Lys/olivengrønn
        "Marint verneområder": "#2b8cbe"      # Blåtoner
    }

    descriptions = {
        "Naturreservat": "Områder med strengeste vernegrad, ofte sårbar natur",
        "Nasjonalparker": "Sammenhengende naturområder med høyt vernenivå",
        "Landskapsvernområder": "Vern av kulturlandskap og naturpreg",
        "Marint verneområder": "Beskyttede havområder og kystøkosystemer"
    }

    # Figurstørrelse optimalisert for stor tekst
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_facecolor('white')
    ax.axis('off')

    # Hovedramme rundt forklaringen
    legend_box = mpatches.FancyBboxPatch(
        (0.02, 0.02), 0.96, 0.96, 
        boxstyle="round,pad=0.02", 
        ec="#333333", fc="white", lw=2.0,
        transform=ax.transAxes
    )
    ax.add_patch(legend_box)

    # Tittel - 22pt
    ax.text(0.5, 0.90, "Forklaring av verneområder i Norge", 
            ha='center', va='center', fontsize=24, fontweight='bold', 
            color='#222222', fontname='DejaVu Sans')

    # Posisjonering
    start_y = 0.75
    line_spacing = 0.18 
    square_size = 0.06

    for i, (category, color) in enumerate(colors.items()):
        current_y = start_y - (i * line_spacing)
        
        # Fargefirkant
        rect = mpatches.Rectangle(
            (0.08, current_y - 0.02), square_size, square_size, 
            facecolor=color, edgecolor='#333333', lw=0.8, transform=ax.transAxes
        )
        ax.add_patch(rect)
        
        # Kategorinavn - 16pt
        ax.text(0.18, current_y + 0.02, category, 
                ha='left', va='center', fontsize=18, fontweight='bold', 
                color='#333333', transform=ax.transAxes)
        
        # Forklaringstekst - 13pt
        ax.text(0.18, current_y - 0.04, descriptions[category], 
                ha='left', va='center', fontsize=16, fontstyle='italic', 
                color='#444444', transform=ax.transAxes)

    # Lagrer kun som PNG
    output_name = "forklaring_verneomraader_norge.png"
    plt.savefig(output_name, dpi=300, bbox_inches='tight', pad_inches=0.3)
    
    print(f"Fullført: '{output_name}' er lagret som PNG.")
    plt.show()

if __name__ == "__main__":
    generate_norwegian_map_legend_png()