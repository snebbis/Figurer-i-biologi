#!/usr/bin/env python3
"""
Global Biome Classification Map
================================
Generates a production-quality biome map from modeled climate data.

FALLBACK MODE: Since real WorldClim/CHELSA rasters are unavailable (no network),
this script uses a physically-informed mathematical climate model that accounts for:
  - Latitude-based temperature gradients (pole-to-equator)
  - Continentality effects (distance from coast)
  - Orographic precipitation shadows (based on terrain proxy)
  - Monsoon and trade wind moisture patterns
  - Ocean current effects (warm: Gulf Stream, Kuroshio; cold: Humboldt, Benguela)
  - ITCZ seasonal migration
  - Rain shadow effects on leeward mountain sides

Biome boundaries emerge organically from gridded climate fields,
NOT from geometric or rectangular latitude banding.

Robinson projection implemented via the standard interpolation table.
Land mask extracted from the provided SVG world map.
"""
import os
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.path import Path
from matplotlib.collections import PathCollection
import matplotlib.patches as mpatches
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes
from scipy.interpolate import interp1d
from PIL import Image
import re
import warnings
import os
import sys
from xml.etree import ElementTree as ET

warnings.filterwarnings('ignore')

# ============================================================
# 1. SVG PATH PARSER
# ============================================================

def parse_svg_path(d):
    """Parse SVG path 'd' attribute into matplotlib Path vertices and codes."""
    tokens = re.findall(
        r'[MmLlCcSsQqTtAaZzHhVv]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d
    )
    vertices = []
    codes = []
    cx, cy = 0.0, 0.0
    sx, sy = 0.0, 0.0
    last_ctrl = None  # for S/s commands
    i = 0

    def peek():
        if i + 1 < len(tokens):
            t = tokens[i + 1]
            return t not in 'MmLlCcSsQqTtAaZzHhVv'
        return False

    def nf():
        nonlocal i
        i += 1
        return float(tokens[i])

    while i < len(tokens):
        cmd = tokens[i]

        if cmd == 'M':
            cx, cy = nf(), nf()
            sx, sy = cx, cy
            vertices.append((cx, cy)); codes.append(Path.MOVETO)
            while peek():
                cx, cy = nf(), nf()
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'm':
            dx, dy = nf(), nf()
            cx += dx; cy += dy
            sx, sy = cx, cy
            vertices.append((cx, cy)); codes.append(Path.MOVETO)
            while peek():
                dx, dy = nf(), nf()
                cx += dx; cy += dy
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'L':
            while peek():
                cx, cy = nf(), nf()
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'l':
            while peek():
                dx, dy = nf(), nf()
                cx += dx; cy += dy
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'H':
            while peek():
                cx = nf()
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'h':
            while peek():
                cx += nf()
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'V':
            while peek():
                cy = nf()
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'v':
            while peek():
                cy += nf()
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd == 'C':
            while peek():
                x1, y1 = nf(), nf()
                x2, y2 = nf(), nf()
                cx, cy = nf(), nf()
                vertices.extend([(x1, y1), (x2, y2), (cx, cy)])
                codes.extend([Path.CURVE4] * 3)
                last_ctrl = (x2, y2)
        elif cmd == 'c':
            while peek():
                dx1, dy1 = nf(), nf()
                dx2, dy2 = nf(), nf()
                dx, dy = nf(), nf()
                vertices.extend([
                    (cx + dx1, cy + dy1),
                    (cx + dx2, cy + dy2),
                    (cx + dx, cy + dy)
                ])
                codes.extend([Path.CURVE4] * 3)
                last_ctrl = (cx + dx2, cy + dy2)
                cx += dx; cy += dy
        elif cmd == 'S':
            while peek():
                if last_ctrl:
                    rx = 2 * cx - last_ctrl[0]
                    ry = 2 * cy - last_ctrl[1]
                else:
                    rx, ry = cx, cy
                x2, y2 = nf(), nf()
                cx, cy = nf(), nf()
                vertices.extend([(rx, ry), (x2, y2), (cx, cy)])
                codes.extend([Path.CURVE4] * 3)
                last_ctrl = (x2, y2)
        elif cmd == 's':
            while peek():
                if last_ctrl:
                    rx = 2 * cx - last_ctrl[0]
                    ry = 2 * cy - last_ctrl[1]
                else:
                    rx, ry = cx, cy
                dx2, dy2 = nf(), nf()
                dx, dy = nf(), nf()
                vertices.extend([
                    (rx, ry),
                    (cx + dx2, cy + dy2),
                    (cx + dx, cy + dy)
                ])
                codes.extend([Path.CURVE4] * 3)
                last_ctrl = (cx + dx2, cy + dy2)
                cx += dx; cy += dy
        elif cmd in ('a', 'A'):
            while peek():
                rx_a = nf(); ry_a = nf(); rot = nf()
                large = nf(); sweep = nf()
                if cmd == 'A':
                    cx, cy = nf(), nf()
                else:
                    cx += nf(); cy += nf()
                vertices.append((cx, cy)); codes.append(Path.LINETO)
        elif cmd in ('z', 'Z'):
            vertices.append((sx, sy)); codes.append(Path.CLOSEPOLY)
            cx, cy = sx, sy
            last_ctrl = None
        i += 1

    if not vertices:
        return np.array([[0, 0]]), np.array([Path.MOVETO])
    return np.array(vertices, dtype=np.float64), np.array(codes, dtype=np.uint8)


# ============================================================
# 2. LOAD SVG AND CREATE LAND MASK
# ============================================================

def create_land_mask_from_svg(svg_path, width=1800, height=900):
    """Parse SVG land paths and rasterize to a boolean mask."""
    print("  Parsing SVG file...")
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    svg_paths = root.findall('.//svg:path', ns)

    svg_w = float(root.get('width', 2754))
    svg_h = float(root.get('height', 1398))

    land_path_ids = []
    land_paths_data = []
    for p in svg_paths:
        pid = p.get('id', '')
        if pid == 'ocean':
            continue  # skip ocean
        d = p.get('d', '')
        if len(d) > 100:  # skip trivial paths
            land_path_ids.append(pid)
            land_paths_data.append(d)
            print(f"    Found land path: {pid} ({len(d)} chars)")

    # Rasterize by rendering to a matplotlib figure
    print("  Rasterizing land paths...")
    fig, ax = plt.subplots(1, 1, figsize=(width/100, height/100), dpi=100)
    ax.set_xlim(0, svg_w)
    ax.set_ylim(svg_h, 0)  # SVG y is inverted
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    for d_str in land_paths_data:
        try:
            verts, cds = parse_svg_path(d_str)
            # Clip invalid codes
            valid = cds <= Path.CLOSEPOLY
            verts = verts[valid]
            cds = cds[valid]
            if len(verts) < 2:
                continue
            path = Path(verts, cds)
            patch = mpatches.PathPatch(path, facecolor='white', edgecolor='none', linewidth=0)
            ax.add_patch(patch)
        except Exception as e:
            print(f"    Warning: path parse error: {e}")
            continue

    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    fig.canvas.draw()

    # Extract raster
    buf = fig.canvas.buffer_rgba()
    img = np.asarray(buf)
    plt.close(fig)

    # Resize to target
    pil_img = Image.fromarray(img)
    pil_img = pil_img.resize((width, height), Image.LANCZOS)
    gray = np.array(pil_img.convert('L'))
    mask = gray > 128

    # Clean up mask
    mask = binary_fill_holes(mask)

    print(f"  Land mask: {mask.sum()} land pixels out of {mask.size} ({100*mask.sum()/mask.size:.1f}%)")
    return mask


# ============================================================
# 3. ROBINSON PROJECTION
# ============================================================

# Robinson projection lookup table (latitude -> X factor, Y factor)
_robinson_table = np.array([
    [0,  1.0000, 0.0000],
    [5,  0.9986, 0.0620],
    [10, 0.9954, 0.1240],
    [15, 0.9900, 0.1860],
    [20, 0.9822, 0.2480],
    [25, 0.9730, 0.3100],
    [30, 0.9600, 0.3720],
    [35, 0.9427, 0.4340],
    [40, 0.9216, 0.4958],
    [45, 0.8962, 0.5571],
    [50, 0.8679, 0.6176],
    [55, 0.8350, 0.6769],
    [60, 0.7986, 0.7346],
    [65, 0.7597, 0.7903],
    [70, 0.7186, 0.8435],
    [75, 0.6732, 0.8936],
    [80, 0.6213, 0.9394],
    [85, 0.5722, 0.9761],
    [90, 0.5322, 1.0000],
])

_rob_lat = _robinson_table[:, 0]
_rob_X = interp1d(_rob_lat, _robinson_table[:, 1], kind='cubic', fill_value='extrapolate')
_rob_Y = interp1d(_rob_lat, _robinson_table[:, 2], kind='cubic', fill_value='extrapolate')

def robinson_project(lon, lat):
    """Project lon/lat (degrees) to Robinson x/y coordinates."""
    abs_lat = np.abs(lat)
    x_factor = _rob_X(abs_lat)
    y_factor = _rob_Y(abs_lat)
    x = 0.8487 * x_factor * np.radians(lon)
    y = 1.3523 * y_factor * np.sign(lat)
    return x, y


# ============================================================
# 4. CLIMATE MODEL (Physically-informed mathematical model)
# ============================================================

def generate_climate_fields(lons, lats, land_mask):
    """
    Generate realistic temperature (BIO1 proxy) and precipitation (BIO12 proxy)
    fields using physically-informed models.

    The model accounts for:
    - Latitude-temperature gradient
    - Altitude proxy (major mountain ranges)
    - Continentality (distance from coast)
    - Ocean current effects
    - ITCZ and trade wind moisture
    - Rain shadow effects
    """
    ny, nx = lats.shape
    lat = lats
    lon = lons

    # ---- TEMPERATURE MODEL (°C, proxy for BIO1) ----

    # Base: latitude gradient (empirical fit to global mean annual temp)
    # Tropics ~27°C, sub-arctic ~-5°C, poles ~-25°C
    # Use a smoother polynomial that doesn't get too cold too quickly
    abs_lat = np.abs(lat)
    temp = 27.0 - 0.003 * abs_lat**2 - 0.15 * abs_lat
    # Extra cooling near poles (>65°)
    polar_extra = np.clip((abs_lat - 65) / 25, 0, 1)
    temp -= polar_extra * 15

    # Altitude proxy: create synthetic elevation for major ranges
    elev = np.zeros_like(lat, dtype=np.float64)

    def add_mountain(lon_c, lat_c, lon_w, lat_w, height, lon_range=None, lat_range=None):
        """Add a mountain range as a Gaussian bump."""
        if lon_range:
            mask_lon = (lon >= lon_range[0]) & (lon <= lon_range[1])
        else:
            mask_lon = np.ones_like(lon, dtype=bool)
        if lat_range:
            mask_lat = (lat >= lat_range[0]) & (lat <= lat_range[1])
        else:
            mask_lat = np.ones_like(lat, dtype=bool)
        d = ((lon - lon_c) / lon_w)**2 + ((lat - lat_c) / lat_w)**2
        bump = height * np.exp(-d)
        return bump * mask_lon * mask_lat

    # Major mountain ranges (approximate centers, widths, heights in m)
    # Himalayas / Tibetan Plateau
    elev += add_mountain(85, 32, 15, 5, 4000, lon_range=(65, 105), lat_range=(25, 45))
    elev += add_mountain(90, 35, 20, 8, 3500, lon_range=(70, 110), lat_range=(25, 50))
    # Andes
    elev += add_mountain(-68, -15, 4, 30, 4000, lon_range=(-80, -60), lat_range=(-55, 10))
    elev += add_mountain(-70, -33, 4, 10, 3500, lon_range=(-80, -60), lat_range=(-45, -20))
    # Rocky Mountains
    elev += add_mountain(-110, 42, 8, 15, 3000, lon_range=(-125, -100), lat_range=(30, 60))
    # Alps
    elev += add_mountain(10, 46.5, 5, 2, 2500, lon_range=(-5, 20), lat_range=(42, 50))
    # East African highlands
    elev += add_mountain(37, 0, 5, 8, 2500, lon_range=(28, 45), lat_range=(-15, 15))
    # Atlas Mountains
    elev += add_mountain(-2, 33, 5, 3, 2000, lon_range=(-10, 10), lat_range=(28, 38))
    # Ural Mountains
    elev += add_mountain(59, 56, 3, 12, 1200, lon_range=(54, 65), lat_range=(48, 68))
    # Scandinavian Mountains
    elev += add_mountain(14, 63, 4, 8, 1500, lon_range=(5, 22), lat_range=(58, 72))
    # Ethiopian Highlands
    elev += add_mountain(39, 9, 5, 5, 2800, lon_range=(33, 48), lat_range=(3, 16))
    # Caucasus
    elev += add_mountain(44, 42.5, 5, 1.5, 3000, lon_range=(36, 50), lat_range=(40, 45))
    # Central Asian highlands
    elev += add_mountain(72, 40, 10, 5, 3500, lon_range=(60, 85), lat_range=(33, 48))
    # Greenland ice sheet (effective elevation - moderate)
    elev += add_mountain(-42, 72, 10, 8, 1500, lon_range=(-60, -20), lat_range=(60, 85))
    # Antarctic ice sheet (moderate - lat already makes it cold)
    elev += add_mountain(0, -80, 90, 10, 1500, lat_range=(-90, -65))

    # Temperature lapse rate: ~5°C per 1000m (slightly reduced from 6.5 for mean annual)
    temp -= 5.0 * (elev / 1000.0)

    # Continentality effect: interior continents are more extreme
    from scipy.ndimage import distance_transform_edt
    if land_mask is not None:
        coast_dist = distance_transform_edt(land_mask).astype(float)
        coast_dist /= max(coast_dist.max(), 1)
        continentality = coast_dist * 0.4
        # At high latitudes, continentality lowers mean annual temp
        temp -= continentality * 4.0 * np.clip(np.abs(lat) / 55.0, 0, 1)
        # Coastal areas at mid-latitudes are moderated
        coastal = 1.0 - continentality
        temp += coastal * 1.5 * ((np.abs(lat) > 30) & (np.abs(lat) < 60))

    # Ocean current effects (warm currents raise temp, cold currents lower)
    # Gulf Stream / North Atlantic Drift (warms Western Europe significantly)
    gulf_stream = 6.0 * np.exp(-(((lon + 5) / 25)**2 + ((lat - 55) / 15)**2))
    gulf_stream += 5.0 * np.exp(-(((lon + 20) / 20)**2 + ((lat - 50) / 12)**2))
    gulf_stream += 3.0 * np.exp(-(((lon - 10) / 15)**2 + ((lat - 62) / 10)**2))
    temp += gulf_stream

    # Kuroshio Current (warms Japan/East Asia coast)
    kuroshio = 2.5 * np.exp(-(((lon - 140) / 15)**2 + ((lat - 35) / 10)**2))
    temp += kuroshio

    # Humboldt Current (cools west coast South America)
    humboldt = -3.0 * np.exp(-(((lon + 78) / 8)**2 + ((lat + 20) / 15)**2))
    temp += humboldt

    # Benguela Current (cools SW Africa)
    benguela = -2.5 * np.exp(-(((lon - 12) / 8)**2 + ((lat + 25) / 10)**2))
    temp += benguela

    # California Current (cools US west coast)
    california = -2.0 * np.exp(-(((lon + 122) / 8)**2 + ((lat - 38) / 12)**2))
    temp += california

    # Smooth temperature field for organic boundaries
    temp = gaussian_filter(temp, sigma=4)

    # ---- PRECIPITATION MODEL (mm/year, proxy for BIO12) ----

    # Base: ITCZ tropical belt (high rainfall near equator)
    precip = 300 + 1800 * np.exp(-(lat / 12)**2)

    # Subtropical dry zones (~20-30° N and S)
    precip -= 600 * np.exp(-((np.abs(lat) - 25) / 8)**2)

    # Mid-latitude cyclonic precipitation
    precip += 500 * np.exp(-((np.abs(lat) - 50) / 15)**2)

    # Polar desert (low precip at poles)
    precip -= 400 * np.exp(-((np.abs(lat) - 80) / 12)**2)

    # Monsoon regions (seasonal heavy rainfall)
    # South/Southeast Asian Monsoon
    monsoon_asia = 1200 * np.exp(-(((lon - 90) / 25)**2 + ((lat - 20) / 10)**2))
    monsoon_asia += 800 * np.exp(-(((lon - 105) / 15)**2 + ((lat - 15) / 10)**2))
    precip += monsoon_asia

    # West African Monsoon
    monsoon_africa = 600 * np.exp(-(((lon + 5) / 20)**2 + ((lat - 8) / 8)**2))
    precip += monsoon_africa

    # Amazon basin (orographic + convective)
    amazon = 1500 * np.exp(-(((lon + 60) / 20)**2 + ((lat + 3) / 12)**2))
    precip += amazon

    # Congo basin
    congo = 800 * np.exp(-(((lon - 22) / 12)**2 + ((lat + 1) / 8)**2))
    precip += congo

    # Maritime Southeast Asia / Indonesia
    maritime_sea = 1200 * np.exp(-(((lon - 115) / 20)**2 + ((lat + 2) / 10)**2))
    precip += maritime_sea

    # Pacific Northwest (orographic)
    pnw = 600 * np.exp(-(((lon + 124) / 5)**2 + ((lat - 47) / 8)**2))
    precip += pnw

    # Patagonian / Chilean coast
    chile = 500 * np.exp(-(((lon + 74) / 4)**2 + ((lat + 44) / 8)**2))
    precip += chile

    # Norway / western Scandinavia
    norway = 400 * np.exp(-(((lon - 6) / 5)**2 + ((lat - 62) / 8)**2))
    precip += norway

    # Western Europe oceanic
    w_europe = 300 * np.exp(-(((lon + 3) / 15)**2 + ((lat - 50) / 10)**2))
    precip += w_europe

    # Southeastern United States (humid subtropical)
    se_us = 700 * np.exp(-(((lon + 85) / 12)**2 + ((lat - 33) / 8)**2))
    se_us += 500 * np.exp(-(((lon + 80) / 10)**2 + ((lat - 38) / 8)**2))
    precip += se_us

    # Eastern China / Korea / Japan (East Asian monsoon)
    e_asia = 600 * np.exp(-(((lon - 115) / 12)**2 + ((lat - 30) / 10)**2))
    e_asia += 400 * np.exp(-(((lon - 130) / 10)**2 + ((lat - 35) / 8)**2))
    precip += e_asia

    # Indian subcontinent (boost monsoon)
    india_monsoon = 800 * np.exp(-(((lon - 78) / 10)**2 + ((lat - 18) / 8)**2))
    india_monsoon += 600 * np.exp(-(((lon - 82) / 8)**2 + ((lat - 22) / 6)**2))
    precip += india_monsoon

    # Southern Brazil / Mata Atlantica
    s_brazil = 500 * np.exp(-(((lon + 47) / 10)**2 + ((lat + 22) / 8)**2))
    precip += s_brazil

    # East African coast (not as dry)
    e_africa_coast = 300 * np.exp(-(((lon - 40) / 6)**2 + ((lat + 5) / 8)**2))
    precip += e_africa_coast

    # Central American isthmus
    c_america = 600 * np.exp(-(((lon + 85) / 10)**2 + ((lat - 12) / 6)**2))
    precip += c_america

    # New Zealand / Tasmania
    nz_rain = 400 * np.exp(-(((lon - 172) / 5)**2 + ((lat + 42) / 5)**2))
    precip += nz_rain

    # Madagascar
    madagascar = 500 * np.exp(-(((lon - 48) / 4)**2 + ((lat + 19) / 6)**2))
    precip += madagascar

    # Rain shadow effects (reduced precip on lee side of mountains)
    # East of Andes (Patagonian steppe)
    precip -= 500 * np.exp(-(((lon + 65) / 6)**2 + ((lat + 42) / 10)**2))

    # Interior Australia (desert)
    precip -= 500 * np.exp(-(((lon - 134) / 15)**2 + ((lat + 25) / 10)**2))

    # Sahara
    precip -= 400 * np.exp(-(((lon - 10) / 25)**2 + ((lat - 24) / 8)**2))
    precip -= 300 * np.exp(-(((lon - 30) / 15)**2 + ((lat - 22) / 6)**2))

    # Arabian desert
    precip -= 350 * np.exp(-(((lon - 45) / 12)**2 + ((lat - 23) / 8)**2))

    # Central Asian deserts (Gobi, Taklamakan)
    precip -= 400 * np.exp(-(((lon - 90) / 20)**2 + ((lat - 42) / 8)**2))
    precip -= 300 * np.exp(-(((lon - 80) / 10)**2 + ((lat - 39) / 5)**2))

    # Kalahari
    precip -= 250 * np.exp(-(((lon - 22) / 8)**2 + ((lat + 24) / 6)**2))

    # Namib
    precip -= 300 * np.exp(-(((lon - 15) / 5)**2 + ((lat + 22) / 8)**2))

    # Great Basin (western US interior)
    precip -= 300 * np.exp(-(((lon + 115) / 8)**2 + ((lat - 40) / 8)**2))

    # Continentality reduces precip in deep interiors
    if land_mask is not None:
        precip -= continentality * 200

    # Elevation boost for orographic precip on windward slopes
    elev_precip = np.gradient(elev, axis=1)  # W-E gradient
    # Windward sides (where prevailing winds hit mountains) get more precip
    precip += np.clip(elev_precip * 0.3, 0, 400)

    # Ensure non-negative
    precip = np.clip(precip, 5, 5000)

    # Smooth precipitation field
    precip = gaussian_filter(precip, sigma=4)

    return temp, precip, elev


# ============================================================
# 5. BIOME CLASSIFICATION (Whittaker-style)
# ============================================================

BIOME_NAMES = [
    'Polare områder',
    'Tundra',
    'Taiga (barskog)',
    'Temperert skog',
    'Gressland / steppe',
    'Ørken',
    'Tropisk regnskog',
]

# Beautiful biome colors (atlas-quality)
BIOME_COLORS = [
    '#F2F2F2',  # 0 Polare områder
    '#9ECAE1',  # 1 Tundra
    '#4C7F7A',  # 2 Taiga (myk blågrønn)
    '#31A354',  # 3 Temperert skog
    '#A1D99B',  # 4 Gressland / steppe
    '#F16913',  # 5 Ørken
    '#0B3D2E',  # 6 Tropisk regnskog
]


def classify_biomes(temp, precip):
    """
    Whittaker-style biome classification based on mean annual temperature
    and annual precipitation.

    Decision boundaries (approximate):
      Polar:            T < -10°C
      Tundra:           -10 <= T < -2°C  AND  P < 500mm
      Taiga:            -2 <= T < 5°C    OR   (-10 <= T < -2 AND P >= 500)
      Temperate Forest: 5 <= T < 20°C    AND  P >= 500mm
      Grassland/Steppe: 5 <= T < 20°C    AND  200 <= P < 500mm
      Desert:           P < 200mm        AND  T >= -2°C
      Tropical Forest:  T >= 20°C        AND  P >= 1000mm

    Additional rules handle transition zones.
    """
    biome = np.full_like(temp, 4, dtype=np.int32)  # default: grassland

    # Polar / Ice (very cold)
    biome[temp < -12] = 0

    # Tundra (cold, low growth)
    mask_tundra = (temp >= -12) & (temp < -3)
    biome[mask_tundra] = 1

    # Taiga / Boreal Forest (cold winters, some warmth in summer)
    mask_taiga = (temp >= -3) & (temp < 5)
    biome[mask_taiga] = 2
    # Cold but wet enough -> boreal forest instead of tundra
    biome[(temp >= -12) & (temp < -3) & (precip >= 400)] = 2

    # Desert (very dry, not freezing)
    mask_desert = (precip < 250) & (temp >= 0)
    biome[mask_desert] = 5
    # Hot desert (warm and dry)
    mask_hot_desert = (temp >= 18) & (precip < 350)
    biome[mask_hot_desert] = 5

    # Grassland / Steppe (moderate conditions, moderate precipitation)
    mask_grass = (temp >= 5) & (temp < 22) & (precip >= 250) & (precip < 700)
    biome[mask_grass] = 4

    # Temperate Forest (moderate temp, good precipitation)
    mask_temp_forest = (temp >= 5) & (temp < 22) & (precip >= 700)
    biome[mask_temp_forest] = 3

    # Warm grassland / savanna
    mask_savanna = (temp >= 20) & (precip >= 500) & (precip < 1000)
    biome[mask_savanna] = 4

    # Tropical Forest (hot and very wet)
    mask_trop = (temp >= 20) & (precip >= 1000)
    biome[mask_trop] = 6

    # Ensure polar stays polar for very cold areas
    biome[temp < -12] = 0

    return biome


# ============================================================
# 6. RENDERING
# ============================================================

def render_biome_map(lons, lats, biome, land_mask, output_prefix='biome_map'):
    """Render the biome map in Robinson projection with smooth filled rendering."""
    print("  Projecting to Robinson...")

    ny, nx = biome.shape

    # Create RGBA color array from biome classification
    biome_rgba = np.zeros((ny, nx, 4), dtype=np.float32)
    for b_id, hex_color in enumerate(BIOME_COLORS):
        r, g, b = int(hex_color[1:3], 16)/255, int(hex_color[3:5], 16)/255, int(hex_color[5:7], 16)/255
        mask = (biome == b_id) & land_mask
        biome_rgba[mask] = [r, g, b, 1.0]

    # Find Robinson projection extent
    x_at_equator, _ = robinson_project(np.array([-180, 180]), np.array([0, 0]))
    _, y_at_meridian = robinson_project(np.array([0, 0]), np.array([-90, 90]))

    x_extent = max(abs(x_at_equator[0]), abs(x_at_equator[1])) * 1.02
    y_extent = max(abs(y_at_meridian[0]), abs(y_at_meridian[1])) * 1.02

    img_w, img_h = 3200, 1600
    rx_lin = np.linspace(-x_extent, x_extent, img_w)
    ry_lin = np.linspace(y_extent, -y_extent, img_h)  # top (north) to bottom (south)
    rx_grid, ry_grid = np.meshgrid(rx_lin, ry_lin)

    # Inverse Robinson projection: Robinson (x,y) -> (lon, lat)
    # For each pixel in the target image, find the source lat/lon
    print("  Inverse projecting image grid...")
    # y -> lat via inverse Y lookup
    abs_y = np.abs(ry_grid) / 1.3523
    # Clip to valid range
    abs_y = np.clip(abs_y, 0, 1.0)

    # Build inverse Y table
    y_table = _rob_Y(_rob_lat)
    lat_from_y = interp1d(y_table, _rob_lat, kind='cubic', fill_value='extrapolate', bounds_error=False)
    inv_lat = lat_from_y(abs_y) * np.sign(ry_grid)

    # x -> lon
    x_factor = _rob_X(np.abs(inv_lat))
    inv_lon = np.degrees(rx_grid / (0.8487 * np.where(x_factor > 0.01, x_factor, 0.01)))

    # Clip to valid range
    inv_lon = np.clip(inv_lon, -180, 180)
    inv_lat = np.clip(inv_lat, -90, 90)

    # Check which pixels are inside the Robinson boundary
    boundary_x = 0.8487 * _rob_X(np.abs(inv_lat)) * np.pi
    inside_robinson = np.abs(rx_grid) <= boundary_x * 1.005

    # Sample biome colors from source grid
    # Convert lon/lat to grid indices
    lon_1d = lons[0, :]
    lat_1d = lats[:, 0]
    col_idx = np.clip(((inv_lon - lon_1d[0]) / (lon_1d[1] - lon_1d[0])).astype(int), 0, nx - 1)
    row_idx = np.clip(((lat_1d[0] - inv_lat) / (lat_1d[0] - lat_1d[1])).astype(int), 0, ny - 1)

    # Build output image
    ocean_color = np.array([42/255, 74/255, 127/255, 1.0])  # #2a4a7f
    bg_color = np.array([26/255, 39/255, 68/255, 1.0])  # #1a2744

    output_img = np.full((img_h, img_w, 4), bg_color, dtype=np.float32)

    # Fill ocean inside Robinson boundary
    output_img[inside_robinson] = ocean_color

    # Fill land with biome colors
    land_pixels = inside_robinson & (biome_rgba[row_idx, col_idx, 3] > 0)
    output_img[land_pixels] = biome_rgba[row_idx[land_pixels], col_idx[land_pixels]]

    # Add subtle coastline highlight at land-ocean boundaries
    from scipy.ndimage import binary_erosion
    land_in_img = inside_robinson & (biome_rgba[row_idx, col_idx, 3] > 0)
    eroded = binary_erosion(land_in_img, iterations=1)
    coastline = land_in_img & ~eroded
    coast_color = np.array([0.22, 0.35, 0.55, 1.0])  # subtle dark blue-grey
    output_img[coastline] = coast_color

    # ---- RENDER ----
    print("  Rendering main map...")
    fig, ax = plt.subplots(1, 1, figsize=(22, 11), dpi=300)
    fig.patch.set_facecolor('#1a2744')
    ax.set_facecolor('#1a2744')

    ax.imshow(output_img, extent=[-x_extent, x_extent, -y_extent, y_extent],
              aspect='equal', interpolation='nearest')

    # Robinson outline
    outline_lats = np.linspace(-90, 90, 500)
    ox_pos, oy_pos = robinson_project(np.full(500, 180), outline_lats)
    ox_neg, oy_neg = robinson_project(np.full(500, -180), outline_lats)
    outline_x = np.concatenate([ox_neg, ox_pos[::-1], [ox_neg[0]]])
    outline_y = np.concatenate([oy_neg, oy_pos[::-1], [oy_neg[0]]])
    ax.plot(outline_x, outline_y, color='#5a8abf', linewidth=0.8, zorder=5)

    # Subtle graticule
    for grat_lat in range(-60, 90, 30):
        glon = np.linspace(-180, 180, 360)
        gx, gy = robinson_project(glon, np.full(360, grat_lat))
        ax.plot(gx, gy, color='#ffffff', alpha=0.10, linewidth=0.3, zorder=6)
    for grat_lon in range(-150, 180, 30):
        glat = np.linspace(-90, 90, 180)
        gx, gy = robinson_project(np.full(180, grat_lon), glat)
        ax.plot(gx, gy, color='#ffffff', alpha=0.10, linewidth=0.3, zorder=6)

    ax.set_xlim(-x_extent, x_extent)
    ax.set_ylim(-y_extent, y_extent)
    ax.axis('off')
    plt.tight_layout(pad=0.3)

    png_path = os.path.join(OUTPUT_DIR, f"{output_prefix}.png")
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                transparent=True)
    print(f"  Saved: {png_path}")

    svg_path = os.path.join(OUTPUT_DIR, f"{output_prefix}.svg")
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                transparent=True)
    print(f"  Saved: {svg_path}")

    plt.close(fig)
    return png_path, svg_path


def render_legend(output_prefix='biome_legend'):
    """Render a standalone legend figure."""
    print("  Rendering legend...")
    fig, ax = plt.subplots(1, 1, figsize=(5, 4.5), dpi=300)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    y_positions = np.arange(len(BIOME_NAMES))[::-1]

    for idx, (name, color) in enumerate(zip(BIOME_NAMES, BIOME_COLORS)):
        y = y_positions[idx]
        rect = mpatches.FancyBboxPatch(
            (0.05, y - 0.35), 0.4, 0.7,
            boxstyle="round,pad=0.05",
            facecolor=color, edgecolor='#ffffff40', linewidth=0.5
        )
        ax.add_patch(rect)
        ax.text(0.55, y, name, va='center', ha='left',
                fontsize=15, color='#e0e8f0',
                fontfamily='sans-serif', fontweight='medium')

    ax.set_xlim(-0.1, 3.5)
    ax.set_ylim(-0.8, len(BIOME_NAMES) - 0.2)
    ax.axis('off')

    ax.text(0.05, len(BIOME_NAMES) - 0.05, 'BIOMKLASSIFISERING',
            fontsize=15, fontweight='bold', color='#ffffff',
            fontfamily='sans-serif', va='bottom')

    plt.tight_layout(pad=0.8)

    png_path = os.path.join(OUTPUT_DIR, f"{output_prefix}.png")
    fig.savefig(png_path, dpi=300, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    svg_path = os.path.join(OUTPUT_DIR, f"{output_prefix}.svg")
    fig.savefig(svg_path, format='svg', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print(f"  Saved: {png_path}, {svg_path}")
    plt.close(fig)
    return png_path, svg_path


# ============================================================
# 7. MAIN PIPELINE
# ============================================================

def main():
    svg_file = r"C:\Users\sebastianb_a\OneDrive - Akershus fylkeskommune\Skrivebord\FORFATTER\Biologi 1\Figurer\Kap 4\WorldMap-Blank-Noborders.svg"

    # Grid resolution
    RESOLUTION = 0.4  # degrees (900 x 450 grid -> smoother result)
    lon_1d = np.arange(-180, 180, RESOLUTION)
    lat_1d = np.arange(90, -90, -RESOLUTION)  # top to bottom
    nx = len(lon_1d)
    ny = len(lat_1d)
    print(f"Grid: {nx} x {ny} = {nx*ny} cells at {RESOLUTION}° resolution")

    lons, lats = np.meshgrid(lon_1d, lat_1d)

    # Step 1: Create land mask from SVG
    print("\n[1/5] Creating land mask from SVG...")
    land_mask = create_land_mask_from_svg(svg_file, width=nx, height=ny)

    # Step 2: Generate climate fields
    print("\n[2/5] Generating climate fields...")
    temp, precip, elev = generate_climate_fields(lons, lats, land_mask)
    print(f"  Temperature range: {temp[land_mask].min():.1f} to {temp[land_mask].max():.1f} °C")
    print(f"  Precipitation range: {precip[land_mask].min():.0f} to {precip[land_mask].max():.0f} mm/yr")

    # Step 3: Classify biomes
    print("\n[3/5] Classifying biomes...")
    biome = classify_biomes(temp, precip)

    # Smooth biome boundaries using iterative majority filter
    from scipy.ndimage import generic_filter
    def mode_filter(values):
        vals = values.astype(int)
        counts = np.bincount(vals, minlength=len(BIOME_NAMES))
        return np.argmax(counts)

    print("  Smoothing biome boundaries...")
    for iteration in range(4):
        biome = generic_filter(biome.astype(float), mode_filter, size=3).astype(int)
    # One more pass with larger kernel for macro-scale smoothness
    biome = generic_filter(biome.astype(float), mode_filter, size=5).astype(int)

    # Apply land mask
    biome[~land_mask] = -1

    # Print biome statistics
    for b_id, b_name in enumerate(BIOME_NAMES):
        count = np.sum(biome[land_mask] == b_id)
        pct = 100 * count / land_mask.sum()
        print(f"  {b_name}: {pct:.1f}%")

    # Step 4: Render map
    print("\n[4/5] Rendering biome map...")
    map_png, map_svg = render_biome_map(lons, lats, biome, land_mask)

    # Step 5: Render legend
    print("\n[5/5] Rendering legend...")
    leg_png, leg_svg = render_legend()

    # Copy to output
    import shutil
    os.makedirs('/mnt/user-data/outputs', exist_ok=True)
    shutil.copy(map_png, os.path.join(OUTPUT_DIR, "biome_map.png"))
    shutil.copy(map_svg, os.path.join(OUTPUT_DIR, "biome_map.svg"))
    shutil.copy(leg_png, os.path.join(OUTPUT_DIR, "biome_legend.png"))
    shutil.copy(leg_svg, os.path.join(OUTPUT_DIR, "biome_legend.svg"))

    print("\n✓ All outputs saved to /mnt/user-data/outputs/")
    print("  - biome_map.png  (300 DPI)")
    print("  - biome_map.svg")
    print("  - biome_legend.png  (300 DPI)")
    print("  - biome_legend.svg")


if __name__ == '__main__':
    main()
