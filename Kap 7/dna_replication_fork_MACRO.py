"""
DNA Replication Fork Figure  --  VERSION 2 (macro-scale)
BioRender-inspired flat 2D vector style.

Adapted from DNA_input.py (v8). That script drew flat, horizontal dsDNA
only: every flag grew straight up/down and every backbone was a horizontal
rounded bar. This version generalises that math so a strand can follow an
arbitrary path. The double helix runs flat on the left ("stem"), then each
strand bends away through a smooth arc and continues as an angled single
strand, producing the classic Y-shaped replication fork.

V2 changes vs. the first version:
  - Much longer fork: more base pairs in the stem and more bases per arm,
    so the figure reads as a macro-scale replication structure.
  - Base letters removed -- the focus is now the overall fork geometry,
    not the individual bases. FIG_SCALE was reduced to keep the (now far
    wider) figure at a sensible physical size while staying high-res.

What was changed vs. the original DNA_input.py:
  - Flags are built once in a canonical frame (anchored at the origin,
    growing toward -y) using the ORIGINAL shape functions, then rotated so
    they stay perpendicular to the local backbone direction.
  - Backbones are no longer FancyBboxPatch rectangles; each strand backbone
    is one continuous rounded "ribbon" polygon that follows the bent path.
  - A path/arc-length system places bases evenly along each curved strand.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import random

# ===================================================================
# PALETTE & BASE GEOMETRY  -- kept verbatim from DNA_input.py
# ===================================================================

BASE_COLORS = {
    "A": "#00ADEF",   # cyan-blue
    "C": "#ED1C24",   # coral-red
    "G": "#A1559C",   # magenta-purple
    "T": "#20B37F",   # green-teal
}
LABEL_COLOR    = "#FFFFFF"
BACKBONE_COLOR = "#3A4148"   # dark grey
BACKGROUND     = "#FFFFFF"

FLAG_WIDTH      = 1.00
FLAG_HEIGHT     = 1.55
BAR_HEIGHT      = 0.26
BASE_SPACING    = 1.18
STRAND_DISTANCE = 2.90

CHEVRON_DEPTH   = 0.40
SWALLOWTAIL_CUT = 0.42
CONCAVE_DEPTH   = 0.34
ARC_SAMPLES     = 48

LETTER_OFFSET_FRAC = {
    "A": 0.36, "C": 0.34, "G": 0.36, "T": 0.34,
}

# ===================================================================
# REPLICATION-FORK LAYOUT  -- tweak these to taste
# ===================================================================

N_DS        = 20     # base PAIRS in the double-stranded "stem"
N_SS        = 26     # bases on each unzipped single-stranded arm
FORK_ANGLE  = 32.0   # degrees each arm splays away from horizontal
BEND_RADIUS = 1.9    # radius of the smooth backbone bend at the fork
BB_OVERHANG = 0.50   # backbone extension beyond the terminal bases
FIG_SCALE   = 0.55   # inches per data unit (controls overall figure size)
SEED        = 7      # set to None for a fresh random sequence each run

# ===================================================================
# SHAPE BUILDERS  -- verbatim from DNA_input.py
# Called with (0, 0, dir=1) to produce a CANONICAL flag: anchored at the
# origin, growing toward -y. It is then rotated/translated into place.
# ===================================================================

def shape_A(x_c, y_anchor, dir):
    W, r = FLAG_WIDTH, FLAG_WIDTH / 2
    rect_h = FLAG_HEIGHT - r
    x_l, x_r = x_c - W / 2, x_c + W / 2
    y_rect_end = y_anchor - dir * rect_h

    verts = [(x_l, y_anchor), (x_r, y_anchor), (x_r, y_rect_end)]
    for i in range(1, ARC_SAMPLES):
        theta = np.pi * i / ARC_SAMPLES
        x = x_c + r * np.cos(theta)
        y = y_rect_end - dir * r * np.sin(theta)
        verts.append((x, y))
    verts.append((x_l, y_rect_end))
    return verts

def shape_T(x_c, y_anchor, dir):
    W, d = FLAG_WIDTH, CONCAVE_DEPTH
    half_w = W / 2
    x_l, x_r = x_c - half_w, x_c + half_w
    y_bot = y_anchor - dir * FLAG_HEIGHT

    k_local = d / 2 - half_w**2 / (2 * d)
    R = d - k_local
    angle_right = np.arctan2(0 - k_local, half_w)
    angle_left  = np.arctan2(0 - k_local, -half_w)

    verts = [(x_l, y_anchor), (x_r, y_anchor), (x_r, y_bot)]
    angles = np.linspace(angle_right, angle_left, ARC_SAMPLES + 1)
    for theta in angles[1:-1]:
        x = x_c + R * np.cos(theta)
        y_local = k_local + R * np.sin(theta)
        y = y_bot + dir * y_local
        verts.append((x, y))
    verts.append((x_l, y_bot))
    return verts

def shape_C(x_c, y_anchor, dir):
    W, d = FLAG_WIDTH, CHEVRON_DEPTH
    rect_h = FLAG_HEIGHT - d
    x_l, x_r = x_c - W / 2, x_c + W / 2
    y_rect_end = y_anchor - dir * rect_h
    y_point = y_anchor - dir * FLAG_HEIGHT
    return [(x_l, y_anchor), (x_r, y_anchor), (x_r, y_rect_end),
            (x_c, y_point), (x_l, y_rect_end)]

def shape_G(x_c, y_anchor, dir):
    W, cut = FLAG_WIDTH, SWALLOWTAIL_CUT
    x_l, x_r = x_c - W / 2, x_c + W / 2
    y_bot = y_anchor - dir * FLAG_HEIGHT
    y_cut_apex = y_bot + dir * cut
    return [(x_l, y_anchor), (x_r, y_anchor), (x_r, y_bot),
            (x_c, y_cut_apex), (x_l, y_bot)]

SHAPE_FUNCS = {"A": shape_A, "C": shape_C, "G": shape_G, "T": shape_T}

# ===================================================================
# 2D TRANSFORM HELPERS  -- this is the core "adaptation" math
# ===================================================================

def transform(verts, rot_deg, tx, ty):
    """Rotate a list of (x, y) verts about the origin, then translate."""
    a = np.radians(rot_deg)
    ca, sa = np.cos(a), np.sin(a)
    return [(x * ca - y * sa + tx, x * sa + y * ca + ty) for (x, y) in verts]

def rot90(v):
    """Rotate a 2D vector +90 degrees (counter-clockwise)."""
    return np.array([-v[1], v[0]])

# ===================================================================
# PATH / ARC-LENGTH SYSTEM  -- lets bases ride along a curved strand
# ===================================================================

def build_anchor_polyline(y_flat, L1, R, theta_deg, L2, side):
    """
    Build the path that flags anchor onto: a flat segment, a smooth
    circular bend, then an angled straight arm.

      side = +1  -> upper strand (bends upward)
      side = -1  -> lower strand (bends downward)
    """
    theta = np.radians(theta_deg)
    pts = []

    # 1. Flat segment, from (0, y_flat) heading +x
    for x in np.linspace(0.0, L1, 80):
        pts.append((x, y_flat))

    # 2. Smooth circular bend (tangent to the flat segment and the arm)
    T1 = np.array([L1, y_flat])
    O  = np.array([L1, y_flat + side * R])          # arc centre
    a0 = np.arctan2(T1[1] - O[1], T1[0] - O[0])     # angle of O->T1
    for a in np.linspace(a0, a0 + side * theta, 50)[1:]:
        pts.append((O[0] + R * np.cos(a), O[1] + R * np.sin(a)))

    # 3. Angled straight arm
    arm_dir = np.array([np.cos(theta), side * np.sin(theta)])
    start = np.array(pts[-1])
    for s in np.linspace(0.0, L2, 110)[1:]:
        p = start + arm_dir * s
        pts.append((p[0], p[1]))

    return np.array(pts, dtype=float)

def arc_length(poly):
    """Cumulative arc length along a polyline."""
    d = np.diff(poly, axis=0)
    seg = np.hypot(d[:, 0], d[:, 1])
    return np.concatenate([[0.0], np.cumsum(seg)])

def point_at(poly, cum, s):
    """Return (position, unit tangent) at arc length s along the polyline."""
    s = np.clip(s, 0.0, cum[-1])
    i = int(np.searchsorted(cum, s) - 1)
    i = max(0, min(i, len(poly) - 2))
    f = (s - cum[i]) / (cum[i + 1] - cum[i] + 1e-12)
    pos = poly[i] * (1 - f) + poly[i + 1] * f
    tan = poly[i + 1] - poly[i]
    tan = tan / (np.linalg.norm(tan) + 1e-12)
    return pos, tan

def vertex_tangents(poly):
    """Smooth unit tangent at every vertex of a polyline."""
    m = len(poly)
    tang = np.zeros((m, 2))
    for i in range(m):
        if i == 0:
            d = poly[1] - poly[0]
        elif i == m - 1:
            d = poly[-1] - poly[-2]
        else:
            a = poly[i] - poly[i - 1]
            b = poly[i + 1] - poly[i]
            a = a / (np.linalg.norm(a) + 1e-12)
            b = b / (np.linalg.norm(b) + 1e-12)
            d = a + b
        tang[i] = d / (np.linalg.norm(d) + 1e-12)
    return tang

# ===================================================================
# RIBBON BACKBONE  -- a constant-thickness, round-capped polygon that
# follows a (possibly bent) centreline. Replaces the FancyBboxPatch bar.
# ===================================================================

def build_ribbon(centerline, half, cap_samples=24):
    centerline = np.asarray(centerline, dtype=float)
    tang = vertex_tangents(centerline)
    nrm  = np.stack([-tang[:, 1], tang[:, 0]], axis=1)
    left  = centerline + nrm * half
    right = centerline - nrm * half

    verts = [tuple(p) for p in left]

    # rounded cap at the far end (bulges along +tangent)
    c, t, n = centerline[-1], tang[-1], nrm[-1]
    for k in range(1, cap_samples):
        phi = np.pi * k / cap_samples
        verts.append(tuple(c + half * (n * np.cos(phi) + t * np.sin(phi))))

    verts += [tuple(p) for p in right[::-1]]

    # rounded cap at the near end (bulges along -tangent)
    c, t, n = centerline[0], tang[0], nrm[0]
    for k in range(1, cap_samples):
        phi = np.pi * k / cap_samples
        verts.append(tuple(c + half * (-n * np.cos(phi) - t * np.sin(phi))))

    return verts

# ===================================================================
# STRAND RENDERING
# ===================================================================

def make_flag(base, anchor, growth):
    """
    Build a base flag at `anchor`, oriented so it grows along `growth`
    (a unit vector pointing away from the backbone).
    Returns (polygon verts, letter x, letter y, letter rotation deg).
    """
    canon = SHAPE_FUNCS[base](0.0, 0.0, 1)          # canonical: grows -y
    # rotation mapping the canonical growth (-y, i.e. angle -90) onto `growth`
    rot = np.degrees(np.arctan2(growth[1], growth[0])) + 90.0
    verts = transform(canon, rot, anchor[0], anchor[1])

    # letter sits inside the flag; keep it the right way up
    off = LETTER_OFFSET_FRAC[base] * FLAG_HEIGHT
    lx, ly = transform([(0.0, -off)], rot, anchor[0], anchor[1])[0]
    text_rot = rot
    while text_rot > 90.0:   text_rot -= 180.0
    while text_rot <= -90.0: text_rot += 180.0
    return verts, lx, ly, text_rot

def draw_strand(ax, seq, y_flat, side, layout, font_size, bbox):
    """Draw one full strand: bent ribbon backbone + rotated base flags."""
    L1, R, L2 = layout["L1"], BEND_RADIUS, layout["L2"]
    ext       = layout["ext"]

    poly = build_anchor_polyline(y_flat, L1, R, FORK_ANGLE, L2, side)
    cum  = arc_length(poly)

    # --- backbone ribbon (offset outward from the anchor path) ---
    tang    = vertex_tangents(poly)
    nrm     = np.stack([-tang[:, 1], tang[:, 0]], axis=1)
    outward = side * nrm                            # away from the fork axis
    centerline = poly + outward * (BAR_HEIGHT / 2)
    ribbon = build_ribbon(centerline, BAR_HEIGHT / 2)
    ax.add_patch(Polygon(ribbon, closed=True, linewidth=0,
                         facecolor=BACKBONE_COLOR, zorder=2))
    bbox.extend(ribbon)

    # --- base flags ---
    for i, base in enumerate(seq):
        s = ext + i * BASE_SPACING
        pos, tan = point_at(poly, cum, s)
        growth = -side * rot90(tan)                 # points toward the fork
        verts, lx, ly, trot = make_flag(base, pos, growth)
        ax.add_patch(Polygon(verts, closed=True, linewidth=0,
                             facecolor=BASE_COLORS[base], zorder=3))
        bbox.extend(verts)
        # V2: base letters removed -- focus is the macro-scale fork, not
        # the individual bases. (Original label-drawing block kept below,
        # commented out, in case per-base letters are wanted again.)
        # ax.text(lx, ly, base, ha="center", va="center", fontsize=font_size,
        #         fontweight="bold", color=LABEL_COLOR, family="DejaVu Sans",
        #         rotation=trot, rotation_mode="anchor", zorder=5)

# ===================================================================
# SEQUENCE
# ===================================================================

COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C"}

def random_sequence(n, seed):
    rng = random.Random(seed)
    return [rng.choice("ACGT") for _ in range(n)]

# ===================================================================
# FIGURE ASSEMBLY
# ===================================================================

def main():
    n_total = N_DS + N_SS
    ext     = BB_OVERHANG + FLAG_WIDTH / 2          # base inset from path end

    # path lengths so bases land BASE_SPACING apart along each strand
    L_total = (n_total - 1) * BASE_SPACING + 2 * ext
    L1      = ext + (N_DS - 1) * BASE_SPACING + FLAG_WIDTH / 2 + 0.35
    L_bend  = BEND_RADIUS * np.radians(FORK_ANGLE)
    L2      = L_total - L1 - L_bend
    layout  = {"L1": L1, "L2": L2, "ext": ext}

    # leading/top strand is random; lagging/bottom strand is its complement,
    # so every base pair is biologically valid (A-T, C-G)
    top_seq = random_sequence(n_total, SEED)
    bot_seq = [COMPLEMENT[b] for b in top_seq]

    font_size = round(25 * FIG_SCALE)               # keeps letters in-flag

    fig, ax = plt.subplots(dpi=200)
    ax.set_facecolor(BACKGROUND)
    fig.patch.set_facecolor(BACKGROUND)

    bbox = []   # collects every vertex for auto-framing
    draw_strand(ax, top_seq, +STRAND_DISTANCE / 2, +1, layout, font_size, bbox)
    draw_strand(ax, bot_seq, -STRAND_DISTANCE / 2, -1, layout, font_size, bbox)

    # auto frame + size the figure (aspect-equal => no distortion)
    xy = np.array(bbox)
    x0, y0 = xy.min(axis=0)
    x1, y1 = xy.max(axis=0)
    M = 0.7
    ax.set_xlim(x0 - M, x1 + M)
    ax.set_ylim(y0 - M, y1 + M)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.set_size_inches((x1 - x0 + 2 * M) * FIG_SCALE,
                        (y1 - y0 + 2 * M) * FIG_SCALE)
    plt.tight_layout()

    out_png = "dna_replication_fork.png"
    out_svg = "dna_replication_fork.svg"
    plt.savefig(out_png, dpi=300, bbox_inches="tight",
                facecolor=BACKGROUND, pad_inches=0.3)
    plt.savefig(out_svg, bbox_inches="tight",
                facecolor=BACKGROUND, pad_inches=0.3)
    plt.close()

    print("\nDNA Replication Fork -- drawing complete!")
    print(f"  Stem (dsDNA) : {N_DS} base pairs")
    print(f"  Each arm     : {N_SS} bases (ssDNA)")
    print(f"  Top strand   : 5'-{''.join(top_seq)}-3'")
    print(f"  Bottom strand: 3'-{''.join(bot_seq)}-5'")
    print(f"  Saved: {out_png}")
    print(f"  Saved: {out_svg}\n")


if __name__ == "__main__":
    main()
