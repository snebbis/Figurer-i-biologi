"""
DNA Replication Fork Figure  --  VERSION 3 (semiconservative replication)
BioRender-inspired flat 2D vector style.

Builds on Version 2 (macro-scale, text-free). Version 3 illustrates
SEMICONSERVATIVE replication: each unwound parental (template) strand is now
paired with a freshly synthesised daughter strand, so the figure goes from a
single parental double helix into two daughter double helices -- and each
daughter helix is one OLD strand + one NEW strand.

V3 changes vs. Version 2:
  - Daughter strands added. A new complementary strand base-pairs along each
    unwound arm, turning the two bare single-stranded arms of V2 into two
    full double helices.
  - "Slate & Stone" origin-based colouring. Fill colour now encodes STRAND
    ORIGIN rather than base identity (A/T/C/G):
        * Slate (dark blue-grey)  -> original / template strands
                                     (the whole stem + both unwound arms)
        * Stone (light warm grey) -> newly synthesised daughter strands
  - The fork angle was widened so the two daughter helices splay apart
    cleanly. The daughter strands sit on the inner faces of the arms, so a
    narrow fork would make the two new strands collide near the vertex.
  - A short single-stranded template stretch is left at the fork itself (the
    active unzipping point); the remainder of each arm is double-stranded.
  - Base letters stay removed (as in V2).

Base-flag SHAPES still encode A/T/C/G so that complementary bases interlock
(A<->T, C<->G); only the FILL COLOUR is origin-based.

Geometry adaptation (carried over from earlier versions):
  - Flags are built once in a canonical frame and rotated to stay
    perpendicular to the local backbone direction.
  - Each backbone is a continuous round-capped "ribbon" polygon.
  - An arc-length system spaces bases evenly along each curved strand.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import random

# ===================================================================
# PALETTE & BASE GEOMETRY
# ===================================================================

# V3: colour encodes STRAND ORIGIN, not base identity.
SLATE      = "#3B4654"   # dark blue-grey -- original / template strands
STONE      = "#CCC0A8"   # light warm grey -- newly synthesised daughter strands
BACKGROUND = "#FFFFFF"

# Base-flag geometry -- kept verbatim from DNA_input.py
FLAG_WIDTH      = 1.00
FLAG_HEIGHT     = 1.55
BAR_HEIGHT      = 0.26
BASE_SPACING    = 1.18
STRAND_DISTANCE = 2.90

CHEVRON_DEPTH   = 0.40
SWALLOWTAIL_CUT = 0.42
CONCAVE_DEPTH   = 0.34
ARC_SAMPLES     = 48

# ===================================================================
# REPLICATION-FORK LAYOUT  -- tweak these to taste
# ===================================================================

N_DS         = 20     # base PAIRS in the double-stranded parental "stem"
N_SS         = 26     # template bases on each unwound arm
DAUGHTER_GAP = 3      # template bases left single-stranded at the fork itself
FORK_ANGLE   = 45.0   # degrees each arm splays away from horizontal
BEND_RADIUS  = 1.9    # radius of the smooth backbone bend at the fork
BB_OVERHANG  = 0.50   # backbone extension beyond the terminal bases
FIG_SCALE    = 0.45   # inches per data unit (controls overall figure size)
SEED         = 7      # set to None for a fresh random sequence each run

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
# 2D TRANSFORM HELPERS
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
# follows a (possibly bent) centreline.
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
# STRAND RENDERING  -- flags + backbone, coloured by ORIGIN
# ===================================================================

def make_flag(base, anchor, growth):
    """
    Polygon vertices for a base flag anchored at `anchor`, grown so it
    points along the unit vector `growth` (away from its backbone).
    """
    canon = SHAPE_FUNCS[base](0.0, 0.0, 1)          # canonical: grows -y
    rot = np.degrees(np.arctan2(growth[1], growth[0])) + 90.0
    return transform(canon, rot, anchor[0], anchor[1])

def draw_backbone(ax, centerline, color, bbox):
    """Draw one backbone as a round-capped ribbon following `centerline`."""
    ribbon = build_ribbon(np.asarray(centerline, float), BAR_HEIGHT / 2)
    ax.add_patch(Polygon(ribbon, closed=True, linewidth=0,
                         facecolor=color, zorder=2))
    bbox.extend(ribbon)

def draw_flags(ax, seq, anchors, growths, color, bbox):
    """Draw a run of base flags (shape from base identity, fill from origin)."""
    for base, anchor, growth in zip(seq, anchors, growths):
        verts = make_flag(base, anchor, growth)
        ax.add_patch(Polygon(verts, closed=True, linewidth=0,
                             facecolor=color, zorder=3))
        bbox.extend(verts)

# ===================================================================
# STRAND GEOMETRY
# ===================================================================

def template_geometry(side, layout):
    """
    For one parental/template strand return:
      poly      -- its anchor polyline (flat stem -> bend -> angled arm)
      anchors   -- anchor point of every base flag
      growths   -- unit flag-growth vector of every base (toward the fork axis)
      tangents  -- unit backbone tangent at every base
    """
    L1, L2, ext = layout["L1"], layout["L2"], layout["ext"]
    y_flat = side * STRAND_DISTANCE / 2
    poly = build_anchor_polyline(y_flat, L1, BEND_RADIUS, FORK_ANGLE, L2, side)
    cum  = arc_length(poly)

    anchors, growths, tangents = [], [], []
    for i in range(N_DS + N_SS):
        s = ext + i * BASE_SPACING
        pos, tan = point_at(poly, cum, s)
        anchors.append(pos)
        tangents.append(tan)
        growths.append(-side * rot90(tan))          # flag grows toward axis
    return poly, anchors, growths, tangents

def daughter_geometry(t_anchors, t_growths):
    """
    Build the newly synthesised daughter strand for one arm. It base-pairs
    with the template arm, offset by STRAND_DISTANCE onto the arm's inner
    face. The first DAUGHTER_GAP template bases (at the fork) are left
    single-stranded, so the daughter starts a little way into the arm.
    """
    first = N_DS + DAUGHTER_GAP
    d_anchors, d_growths = [], []
    for i in range(first, N_DS + N_SS):
        inward = t_growths[i]                       # unit: template flag dir
        d_anchors.append(t_anchors[i] + inward * STRAND_DISTANCE)
        d_growths.append(-inward)                   # daughter flag faces back
    return d_anchors, d_growths

def daughter_backbone(d_anchors, arm_dir, inward, ext):
    """Straight round-capped centreline running behind the daughter flags."""
    half = BAR_HEIGHT / 2
    start = d_anchors[0]  + inward * half - arm_dir * ext
    end   = d_anchors[-1] + inward * half + arm_dir * ext
    return [start, end]

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
    ext     = BB_OVERHANG + FLAG_WIDTH / 2          # base inset from path end
    n_total = N_DS + N_SS

    # path lengths so bases land BASE_SPACING apart along each strand
    L_total = (n_total - 1) * BASE_SPACING + 2 * ext
    L1      = ext + (N_DS - 1) * BASE_SPACING + FLAG_WIDTH / 2 + 0.35
    L_bend  = BEND_RADIUS * np.radians(FORK_ANGLE)
    L2      = L_total - L1 - L_bend
    layout  = {"L1": L1, "L2": L2, "ext": ext}

    # parental strands: top is random, bottom is its complement, so every
    # base pair (in the stem and along each arm) is biologically valid.
    top_seq = random_sequence(n_total, SEED)
    bot_seq = [COMPLEMENT[b] for b in top_seq]
    template_seqs = {+1: top_seq, -1: bot_seq}

    fig, ax = plt.subplots(dpi=200)
    ax.set_facecolor(BACKGROUND)
    fig.patch.set_facecolor(BACKGROUND)

    bbox = []   # collects every vertex for auto-framing
    first = N_DS + DAUGHTER_GAP

    for side in (+1, -1):
        t_seq = template_seqs[side]
        poly, t_anchors, t_growths, t_tangents = template_geometry(side, layout)

        # --- ORIGINAL / TEMPLATE strand (stem + bend + arm) : SLATE ---
        tang = vertex_tangents(poly)
        nrm  = np.stack([-tang[:, 1], tang[:, 0]], axis=1)
        outward    = side * nrm                     # away from the fork axis
        centerline = poly + outward * (BAR_HEIGHT / 2)
        draw_backbone(ax, centerline, SLATE, bbox)
        draw_flags(ax, t_seq, t_anchors, t_growths, SLATE, bbox)

        # --- NEW / DAUGHTER strand (synthesised along the arm) : STONE ---
        d_anchors, d_growths = daughter_geometry(t_anchors, t_growths)
        d_seq    = [COMPLEMENT[b] for b in t_seq[first:]]
        arm_dir  = t_tangents[first]                # unit, fork -> arm tip
        inward   = t_growths[first]                 # unit, toward fork axis
        d_center = daughter_backbone(d_anchors, arm_dir, inward, ext)
        draw_backbone(ax, d_center, STONE, bbox)
        draw_flags(ax, d_seq, d_anchors, d_growths, STONE, bbox)

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

    print("\nDNA Replication Fork  --  V3 (semiconservative) complete!")
    print(f"  Parental stem (dsDNA)       : {N_DS} base pairs")
    print(f"  Template bases per arm      : {N_SS}")
    print(f"  Daughter (new) bases per arm: {N_SS - DAUGHTER_GAP}")
    print(f"  Single-stranded fork region : {DAUGHTER_GAP} bases per arm")
    print(f"  Slate (original / template) : {SLATE}")
    print(f"  Stone (new / daughter)      : {STONE}")
    print(f"  Saved: {out_png}")
    print(f"  Saved: {out_svg}\n")


if __name__ == "__main__":
    main()
