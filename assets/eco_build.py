#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eco_build.py -- single source of truth for the agent ecosystem geometry.

Three consumers need identical numbers:

  1. the inline SVG <symbol> geodesic glyph, referenced by <use> everywhere
  2. the live WebGL view plus its DOM label chips (fed a JS data literal)
  3. the zero-JS static twins served under prefers-reduced-motion

Writing the layout three times guarantees divergence, so it is written once
here and spliced into index.html between markers. Nothing in this file is
random. The glyph is a real icosahedral projection, the operator field is a
golden-angle modulated arc, and every coordinate is a named constant or a
function of one.

Usage:
    python3 assets/eco_build.py            # splice into ../index.html
    python3 assets/eco_build.py --check     # verify index.html is current
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
INDEX = REPO / "index.html"

PHI = (1.0 + 5.0 ** 0.5) / 2.0
GOLDEN_ANGLE = math.pi * (3.0 - 5.0 ** 0.5)

# --------------------------------------------------------------------------
# GLYPH SIZE SCALE. Size encodes rank, never decoration.
# These names are mirrored verbatim in the index.html ecosystem script and
# assert_constants() below fails the build if the two ever drift apart.
# --------------------------------------------------------------------------
GLYPH_PX_CORE          = 104
GLYPH_PX_LOOP          = 52
GLYPH_PX_CHILD         = 26
GLYPH_PX_POLLER        = 26
GLYPH_PX_OPERATOR      = 16

GLYPH_PX_CORE_TALL     = 64
GLYPH_PX_LOOP_TALL     = 40
GLYPH_PX_CHILD_TALL    = 18
GLYPH_PX_POLLER_TALL   = 18
GLYPH_PX_OPERATOR_TALL = 11

# Below this rendered diameter the frequency-2 geodesic turns to mush, so the
# glyph drops to the bare icosahedron instead of shipping unreadable detail.
GLYPH_FACET_THRESHOLD_PX = 30

GLYPH_VIEWBOX = 100.0
GLYPH_RADIUS = 45.0
GLYPH_TILT_X_DEG = -21.0
GLYPH_TILT_Y_DEG = 13.0

# --------------------------------------------------------------------------
# TYPE + CLEARANCE
# --------------------------------------------------------------------------
LABEL_FS = {"core": 12.0, "hub": 11.0, "leaf": 10.0, "poller": 10.0, "group": 10.0}
LABEL_TRACK = {"core": 0.14, "hub": 0.12, "leaf": 0.12, "poller": 0.12, "group": 0.22}
NOTE_FS = 9.5
NOTE_TRACK = 0.12
MONO_ADVANCE = 0.60          # JetBrains Mono advance width, in em
LABEL_GAP = 10.0             # glyph edge to label plate
LABEL_GAP_CORE = 14.0        # the core gets extra air, and a leader line
PLATE_PAD_X = 7.0
PLATE_PAD_Y = 3.0
LINE_STEP = 13.0             # label baseline to note baseline

ARROW_LEN = 9.0
ARROW_HALF = 3.4
ARROW_LEN_TALL = 7.0
ARROW_HALF_TALL = 2.7
EDGE_CLEARANCE = 3.0         # edge stops this far off the glyph silhouette

# No label plate may come within this of another plate or of any glyph
# silhouette. assert_no_label_collisions() fails the build below it, so a
# label overlap can never reach a screenshot again.
LABEL_MIN_CLEARANCE = 6.0


def adv(fs, track):
    return fs * (MONO_ADVANCE + track)


def text_w(s, fs, track):
    return len(s) * adv(fs, track)


# ==========================================================================
# GEODESIC GLYPH
# ==========================================================================

def icosahedron_vertices():
    v = []
    for a in (-1.0, 1.0):
        for b in (-1.0, 1.0):
            v.append((0.0, a, b * PHI))
            v.append((a, b * PHI, 0.0))
            v.append((b * PHI, 0.0, a))
    return [normalize(p) for p in v]


def normalize(p):
    n = math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])
    return (p[0] / n, p[1] / n, p[2] / n)


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def icosahedron_faces(verts):
    n = len(verts)
    pairs = sorted(dist2(verts[i], verts[j]) for i in range(n) for j in range(i + 1, n))
    edge2 = pairs[0]
    eps = edge2 * 0.05
    faces = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(dist2(verts[i], verts[j]) - edge2) > eps:
                continue
            for k in range(j + 1, n):
                if (abs(dist2(verts[i], verts[k]) - edge2) <= eps and
                        abs(dist2(verts[j], verts[k]) - edge2) <= eps):
                    faces.append((i, j, k))
    return faces


def subdivide(verts, faces):
    verts = list(verts)
    cache = {}

    def mid(a, b):
        key = (min(a, b), max(a, b))
        if key not in cache:
            p = normalize(((verts[a][0] + verts[b][0]) / 2.0,
                           (verts[a][1] + verts[b][1]) / 2.0,
                           (verts[a][2] + verts[b][2]) / 2.0))
            verts.append(p)
            cache[key] = len(verts) - 1
        return cache[key]

    out = []
    for (a, b, c) in faces:
        ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
        out += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
    return verts, out


def face_edges(faces):
    e = set()
    for (a, b, c) in faces:
        for (p, q) in ((a, b), (b, c), (c, a)):
            e.add((min(p, q), max(p, q)))
    return sorted(e)


def rotate(p, ax, ay):
    x, y, z = p
    ca, sa = math.cos(ax), math.sin(ax)
    y, z = y * ca - z * sa, y * sa + z * ca
    cb, sb = math.cos(ay), math.sin(ay)
    x, z = x * cb + z * sb, -x * sb + z * cb
    return (x, y, z)


def glyph_paths(frequency):
    verts = icosahedron_vertices()
    faces = icosahedron_faces(verts)
    for _ in range(frequency - 1):
        verts, faces = subdivide(verts, faces)
    edges = face_edges(faces)

    ax = math.radians(GLYPH_TILT_X_DEG)
    ay = math.radians(GLYPH_TILT_Y_DEG)
    rot = [rotate(p, ax, ay) for p in verts]
    c = GLYPH_VIEWBOX / 2.0

    def proj(p):
        return (c + GLYPH_RADIUS * p[0], c - GLYPH_RADIUS * p[1])

    front, back = [], []
    for (i, j) in edges:
        zm = (rot[i][2] + rot[j][2]) / 2.0
        a, b = proj(rot[i]), proj(rot[j])
        seg = "M%s %sL%s %s" % (num(a[0]), num(a[1]), num(b[0]), num(b[1]))
        (front if zm >= -0.02 else back).append(seg)
    return "".join(front), "".join(back)


def num(v, nd=2):
    s = ("%.*f" % (nd, v)).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def build_defs():
    hi_f, hi_b = glyph_paths(2)
    lo_f, lo_b = glyph_paths(1)
    out = []
    out.append('<svg class="eco-defs" aria-hidden="true" focusable="false" '
               'xmlns="http://www.w3.org/2000/svg"><defs>')
    for sid, (f, b) in (("eco-glyph-hi", (hi_f, hi_b)), ("eco-glyph-lo", (lo_f, lo_b))):
        out.append('<symbol id="%s" viewBox="0 0 100 100">' % sid)
        out.append('<path class="eco-glyph-back" vector-effect="non-scaling-stroke" '
                   'fill="none" stroke-opacity=".22" d="%s"/>' % b)
        out.append('<circle class="eco-glyph-rim" vector-effect="non-scaling-stroke" '
                   'fill="none" stroke-opacity=".45" cx="50" cy="50" r="%s"/>'
                   % num(GLYPH_RADIUS))
        out.append('<path class="eco-glyph-front" vector-effect="non-scaling-stroke" '
                   'fill="none" stroke-opacity=".92" d="%s"/>' % f)
        out.append('</symbol>')
    out.append('</defs></svg>')
    return "".join(out)


# ==========================================================================
# LAYOUT PRIMITIVES
# ==========================================================================

def node(nid, label, note, kind, x, y, anchor):
    return {"id": nid, "label": label, "note": note, "kind": kind,
            "x": float(x), "y": float(y), "anchor": anchor}


def radius(kind, tall):
    table = ({"core": GLYPH_PX_CORE_TALL, "hub": GLYPH_PX_LOOP_TALL,
              "leaf": GLYPH_PX_CHILD_TALL, "poller": GLYPH_PX_POLLER_TALL,
              "operator": GLYPH_PX_OPERATOR_TALL, "group": 0}
             if tall else
             {"core": GLYPH_PX_CORE, "hub": GLYPH_PX_LOOP,
              "leaf": GLYPH_PX_CHILD, "poller": GLYPH_PX_POLLER,
              "operator": GLYPH_PX_OPERATOR, "group": 0})
    return table[kind] / 2.0


def seg_shorten(p0, p1, amount):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    t = min(amount / L, 0.9)
    return (p0[0] + dx * t, p0[1] + dy * t)


def trim_ends(pts, r0, r1):
    pts = [tuple(p) for p in pts]
    if r0 > 0:
        pts[0] = seg_shorten(pts[0], pts[1], r0 + EDGE_CLEARANCE)
    if r1 > 0:
        pts[-1] = seg_shorten(pts[-1], pts[-2], r1 + EDGE_CLEARANCE)
    return pts


def arrow_tri(pts, tall):
    ln = ARROW_LEN_TALL if tall else ARROW_LEN
    hw = ARROW_HALF_TALL if tall else ARROW_HALF
    a, b = pts[-2], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = b[0] - ux * ln, b[1] - uy * ln
    nx, ny = -uy * hw, ux * hw
    return [[b[0], b[1]], [bx + nx, by + ny], [bx - nx, by - ny]]


def bow(p0, p1, amount, segments=22):
    mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    cx, cy = mx - (dy / L) * amount, my + (dx / L) * amount
    out = []
    for s in range(segments + 1):
        u = s / float(segments)
        iu = 1.0 - u
        out.append((iu * iu * p0[0] + 2 * iu * u * cx + u * u * p1[0],
                    iu * iu * p0[1] + 2 * iu * u * cy + u * u * p1[1]))
    return out


class Builder(object):
    """Collects nodes and edges for one orientation."""

    def __init__(self, w, h, tall):
        self.w, self.h, self.tall = float(w), float(h), tall
        self.nodes = []
        self.by_id = {}
        self.edges = []

    def add(self, *args):
        n = node(*args)
        self.nodes.append(n)
        self.by_id[n["id"]] = n
        return n

    def pt(self, ref):
        if isinstance(ref, str):
            n = self.by_id[ref]
            return (n["x"], n["y"])
        return (float(ref[0]), float(ref[1]))

    def rad(self, ref):
        if isinstance(ref, str):
            return radius(self.by_id[ref]["kind"], self.tall)
        return 0.0

    def link(self, kind, waypoints, depth, arrow=False, flow=False,
             direction=1, bowed=None):
        """waypoints[0] is the growth origin. Geometry is trimmed here so the
        runtime never has to know a glyph radius."""
        raw = [self.pt(p) for p in waypoints]
        if bowed is not None and len(raw) == 2:
            raw = bow(raw[0], raw[1], bowed)
            r0, r1 = self.rad(waypoints[0]), self.rad(waypoints[-1])
        else:
            r0, r1 = self.rad(waypoints[0]), self.rad(waypoints[-1])
        pts = trim_ends(raw, r0, r1)
        e = {"kind": kind, "pts": [[round(p[0], 1), round(p[1], 1)] for p in pts],
             "depth": depth, "flow": bool(flow), "dir": direction}
        if arrow:
            e["arrow"] = [[round(v, 1) for v in p] for p in arrow_tri(pts, self.tall)]
        self.edges.append(e)
        return e

    def data(self):
        glyph = ({"core": GLYPH_PX_CORE_TALL, "hub": GLYPH_PX_LOOP_TALL,
                  "leaf": GLYPH_PX_CHILD_TALL, "poller": GLYPH_PX_POLLER_TALL,
                  "operator": GLYPH_PX_OPERATOR_TALL, "group": 0}
                 if self.tall else
                 {"core": GLYPH_PX_CORE, "hub": GLYPH_PX_LOOP,
                  "leaf": GLYPH_PX_CHILD, "poller": GLYPH_PX_POLLER,
                  "operator": GLYPH_PX_OPERATOR, "group": 0})
        return {"box": [self.w, self.h], "glyph": glyph,
                "nodes": [{"id": n["id"], "label": n["label"], "note": n["note"],
                           "kind": n["kind"], "x": round(n["x"], 1),
                           "y": round(n["y"], 1), "anchor": n["anchor"]}
                          for n in self.nodes],
                "edges": self.edges}


def operator_arc(cx, cy, rx, ry, a0_deg, a1_deg, count, spread):
    out = []
    for i in range(count):
        t = (i + 0.5) / count
        a = math.radians(a0_deg + t * (a1_deg - a0_deg))
        k = 1.0 + spread * math.cos(i * GOLDEN_ANGLE)
        out.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return out


OPERATOR_COUNT = 16
OPERATOR_GOLDEN_SPREAD = 0.025

# The live pulls. These are the reason a quote can be trusted the same
# hour it is asked for, so they get their own rank and their own colour.
FEEDS = [("feed-price", "PRICE BOOK"), ("feed-stock", "STOCK LEVEL"),
         ("feed-lead", "LEAD TIME"), ("feed-freight", "FREIGHT"),
         ("feed-tax", "TAX RULES")]

# The numbers the shop owns. Supplier cost alone is a list price, not a
# quote. These three are what make the number theirs.
ENGINE_NOTE = "SUPPLIER COST + YOUR RATES"


# ==========================================================================
# WIDE LAYOUT  (design box 1240 x 700)
#
# One job, read left to right. A lead arrives, it becomes a scope sheet,
# the engine prices it, the margin gate clears it, the quote leaves. The
# live supplier pulls drop in from above. The shop's own numbers come up
# from below. Every quote that goes out lands in the history field, and the
# field calibrates the engine, which is what closes the loop.
# ==========================================================================

WIDE_SPINE_Y = 300.0
WIDE_FEED_Y = 96.0
WIDE_FEED_X0 = 310.0         # the rack sits over the engine, not the whole box
WIDE_FEED_SPAN = 620.0

# The history field. A shallow wide sweep, not a deep bowl. Sixteen priced
# jobs read as a ledger the engine sits over. A bowl put the two outer jobs
# up beside the shop inputs, which made four unrelated glyphs look like one
# cluster. The field is held clear of the bottom left, because the legend
# plate is painted over that corner by the DOM and is not in this geometry.
WIDE_OPS_CY = 500.0
WIDE_OPS_RX = 470.0
WIDE_OPS_RY = 62.0
WIDE_OPS_LABEL_Y = 620.0


def build_wide():
    b = Builder(1240, 700, tall=False)

    # The spine. The core is the only glyph on the middle band that carries a
    # note, because it is the only station that needs two facts stated.
    b.add("engine", "PRICING ENGINE", ENGINE_NOTE, "core",
          620, WIDE_SPINE_Y, "below")
    b.add("lead", "LEAD IN", "", "leaf", 90, WIDE_SPINE_Y, "above")
    b.add("scope", "SCOPE SHEET", "", "hub", 290, WIDE_SPINE_Y, "above")
    b.add("gate", "MARGIN GATE", "", "hub", 950, WIDE_SPINE_Y, "above")
    b.add("quote", "QUOTE OUT", "", "leaf", 1150, WIDE_SPINE_Y, "above")

    b.add("grp-feeds", "LIVE SUPPLIER FEEDS", "", "group", 620, 30, "center")
    frow = pack_row([lab for _, lab in FEEDS], LABEL_FS["poller"],
                    LABEL_TRACK["poller"], WIDE_FEED_SPAN, 0.0, 14.0)
    for (fid, lab), fx in zip(FEEDS, frow):
        b.add(fid, lab, "", "poller", WIDE_FEED_X0 + fx, WIDE_FEED_Y, "above")

    # The shop's numbers. Rate card and labor hours sit level, one either side
    # of the core, because they are the same kind of fact. They come in wide
    # and shallow on purpose: anything rising steeply into the core would pass
    # under the note plate, and a line that vanishes under type reads as a
    # line that stops. Markup rules hangs off the gate instead, because that
    # is the station the rules are tested at.
    b.add("rate-card", "RATE CARD", "", "leaf", 320, 372, "below")
    b.add("labor", "LABOR HOURS", "", "leaf", 920, 372, "below")
    b.add("markup", "MARKUP RULES", "", "leaf", 1120, 400, "below")

    ops = operator_arc(620, WIDE_OPS_CY, WIDE_OPS_RX, WIDE_OPS_RY, 180, 0,
                       OPERATOR_COUNT, OPERATOR_GOLDEN_SPREAD)
    for i, (ox, oy) in enumerate(ops):
        b.add("op-%d" % i, "", "", "operator", ox, oy, "none")
    b.add("grp-history", "PRICED JOB HISTORY", "", "group", 620,
          WIDE_OPS_LABEL_Y, "center")

    b.link("delegate", ["lead", "scope"], 0, arrow=True, flow=True)
    b.link("delegate", ["scope", "engine"], 0, arrow=True, flow=True)
    b.link("delegate", ["engine", "gate"], 0, arrow=True, flow=True)
    b.link("qagate", ["gate", "quote"], 0, arrow=True, flow=True)

    for fid, _ in FEEDS:
        b.link("inbound", ["engine", fid], 1, flow=True, direction=-1)
    b.link("inbound", ["engine", "rate-card"], 1, flow=True, direction=-1)
    b.link("inbound", ["engine", "labor"], 1, flow=True, direction=-1)
    b.link("inbound", ["gate", "markup"], 1, flow=True, direction=-1)

    # One trunk down into the field, one calibration line back up. Sixteen
    # duplicate lines said the same thing and read as noise.
    b.link("delegate", ["gate", "op-15"], 1, arrow=True, flow=True)
    b.link("evidence", ["engine", "op-0"], 2, flow=True, direction=-1)
    b.link("lateral", ["op-%d" % i for i in range(OPERATOR_COUNT)], 2)

    fix_return_arrows(b)
    return b.data()


def fix_return_arrows(b):
    """Inbound and evidence edges are stored core-outward so the reveal grows
    from the core, but the arrow belongs at the core end and points into it."""
    for e in b.edges:
        if e["kind"] in ("inbound", "evidence") and "arrow" not in e:
            pts = [(p[0], p[1]) for p in e["pts"]]
            tri = arrow_tri([pts[1], pts[0]], b.tall)
            e["arrow"] = [[round(v, 1) for v in p] for p in tri]


# ==========================================================================
# TALL LAYOUT  (design box 322 x 640)
#
# The same pipeline stood on end. A phone has no room for two label columns
# on one baseline, so there is only one column. Every station sits on a
# single spine near the right edge and every label hangs off it to the left,
# which keeps the spine itself clear of type from top to bottom. The core
# note is dropped here: at this width it would push the plate off the box,
# and the sentence it carries is already in the copy beside the figure. The
# supplier feeds move to a rank on the right at the engine's own height and
# give up their names, because five slate spheres under one group label say
# enough on a phone and the names are in the text alternative.
# ==========================================================================

TALL_BOX_W = 322.0
TALL_BOX_H = 640.0
TALL_CX = TALL_BOX_W / 2.0

TALL_SPINE_X = 190.0         # right of centre, so labels hang left with room
TALL_FEED_X = 288.0          # feed rank, clear of every plate on the spine
TALL_FEED_Y0 = 224.0
TALL_FEED_STEP = 28.0

TALL_RETURN_X = 52.0         # calibration runs up the left gutter
TALL_RETURN_Y = 340.0        # and turns in below the core plate, not through it
TALL_OPS_Y = 572.0
TALL_OPS_LABEL_Y = 626.0
TALL_OPS_RISE = 14.0
TALL_OPS_X0 = 26.0
TALL_OPS_SPAN = 270.0

# Row pitch is set against the plate height, not by eye. Hub rows get the
# wider berth because their plates are the widest on the spine.
TALL_ROWS = [("lead", "LEAD IN", "leaf", 80.0),
             ("scope", "SCOPE SHEET", "hub", 160.0),
             ("engine", "PRICING ENGINE", "core", 280.0),
             ("gate", "MARGIN GATE", "hub", 400.0),
             ("quote", "QUOTE OUT", "leaf", 470.0)]


def pack_row(labels, fs, track, box_w, margin, min_gap):
    """Centre positions for a row of centred labels, packed by measured
    width so the gaps are equal and never negative. Even spacing puts long
    names shoulder to shoulder while short ones float, which is how
    STEERING and HEAVY ended up touching."""
    widths = [text_w(s, fs, track) + 2 * PLATE_PAD_X for s in labels]
    total = sum(widths)
    span = box_w - 2 * margin
    gap = (span - total) / float(len(labels) - 1)
    if gap < min_gap:
        sys.stderr.write("eco_build: label row does not fit, gap %.1f\n" % gap)
        sys.exit(1)
    out, x = [], margin
    for w in widths:
        out.append(x + w / 2.0)
        x += w + gap
    return out


def build_tall():
    b = Builder(TALL_BOX_W, TALL_BOX_H, tall=True)
    for nid, lab, kind, y in TALL_ROWS:
        b.add(nid, lab, "", kind, TALL_SPINE_X, y, "left")

    b.add("grp-feeds", "SUPPLIER FEEDS", "", "group", 262, 190, "center")
    for i, (fid, _) in enumerate(FEEDS):
        b.add(fid, "", "", "poller", TALL_FEED_X,
              TALL_FEED_Y0 + i * TALL_FEED_STEP, "none")

    ops = []
    for i in range(OPERATOR_COUNT):
        t = (i + 0.5) / OPERATOR_COUNT
        k = 1.0 + OPERATOR_GOLDEN_SPREAD * math.cos(i * GOLDEN_ANGLE)
        ops.append((TALL_OPS_X0 + t * TALL_OPS_SPAN,
                    TALL_OPS_Y + TALL_OPS_RISE * math.sin(math.pi * t) * k))
    for i, (ox, oy) in enumerate(ops):
        b.add("op-%d" % i, "", "", "operator", ox, oy, "none")
    b.add("grp-history", "PRICED JOB HISTORY", "", "group",
          TALL_CX, TALL_OPS_LABEL_Y, "center")

    b.link("delegate", ["lead", "scope"], 0, arrow=True, flow=True)
    b.link("delegate", ["scope", "engine"], 0, arrow=True, flow=True)
    b.link("delegate", ["engine", "gate"], 0, arrow=True, flow=True)
    b.link("qagate", ["gate", "quote"], 0, arrow=True, flow=True)

    for fid, _ in FEEDS:
        b.link("inbound", ["engine", fid], 1, flow=True, direction=-1)

    # The trunk clears the quote plate on the right. The calibration return
    # is gutter routed on the left, because a straight line from the field to
    # the core would have to cross two plates on the way.
    b.link("delegate", ["gate", "op-15"], 1, arrow=True, flow=True)
    b.link("evidence", ["engine", (TALL_RETURN_X, TALL_RETURN_Y),
                        (TALL_RETURN_X, TALL_OPS_Y), "op-0"], 2,
           flow=True, direction=-1)

    b.link("lateral", ["op-%d" % i for i in range(OPERATOR_COUNT)], 2)

    fix_return_arrows(b)
    return b.data()


# ==========================================================================
# STATIC SVG TWIN
# ==========================================================================

def path_d(pts):
    d = "M%s %s" % (num(pts[0][0], 1), num(pts[0][1], 1))
    for p in pts[1:]:
        d += "L%s %s" % (num(p[0], 1), num(p[1], 1))
    return d


def label_geometry(n, glyph):
    """Returns a list of (x, y, anchor, text, fs, track, cls) plus a plate rect."""
    kind = n["kind"]
    if not n["label"]:
        return None
    fs = LABEL_FS.get(kind, LABEL_FS["leaf"])
    tr = LABEL_TRACK.get(kind, LABEL_TRACK["leaf"])
    r = glyph.get(kind, 0) / 2.0
    gap = LABEL_GAP_CORE if kind == "core" else LABEL_GAP
    lines = [(n["label"], fs, tr)]
    if n["note"]:
        lines.append((n["note"], NOTE_FS, NOTE_TRACK))
    bw = max(text_w(s, f, t) for s, f, t in lines)
    bh = fs * 1.15 + (LINE_STEP if n["note"] else 0)
    anchor = n["anchor"]
    x, y = n["x"], n["y"]
    if anchor == "below":
        px, py, ta = x, y + r + gap, "middle"
        rect = (x - bw / 2.0 - PLATE_PAD_X, py - PLATE_PAD_Y,
                bw + 2 * PLATE_PAD_X, bh + 2 * PLATE_PAD_Y)
    elif anchor == "above":
        py = y - r - gap - bh
        px, ta = x, "middle"
        rect = (x - bw / 2.0 - PLATE_PAD_X, py - PLATE_PAD_Y,
                bw + 2 * PLATE_PAD_X, bh + 2 * PLATE_PAD_Y)
    elif anchor == "right":
        px, py, ta = x + r + gap, y - bh / 2.0, "start"
        rect = (px - PLATE_PAD_X, py - PLATE_PAD_Y,
                bw + 2 * PLATE_PAD_X, bh + 2 * PLATE_PAD_Y)
    elif anchor == "left":
        px, py, ta = x - r - gap, y - bh / 2.0, "end"
        rect = (px - bw - PLATE_PAD_X, py - PLATE_PAD_Y,
                bw + 2 * PLATE_PAD_X, bh + 2 * PLATE_PAD_Y)
    else:
        px, py, ta = x, y - bh / 2.0, "middle"
        rect = None
    return {"x": px, "y": py, "anchor": ta, "lines": lines, "rect": rect,
            "kind": kind}


def _plate_rects(layout):
    """Every label plate in design units, as (id, x0, y0, x1, y1)."""
    out = []
    for n in layout["nodes"]:
        g = label_geometry(n, layout["glyph"])
        if not g or not g["rect"]:
            continue
        x, y, w, h = g["rect"]
        out.append((n["id"], x, y, x + w, y + h))
    return out


def _gap(a, b):
    """Separation between two axis aligned rects. Negative means overlap."""
    dx = max(b[1] - a[3], a[1] - b[3])
    dy = max(b[2] - a[4], a[2] - b[4])
    if dx >= 0 or dy >= 0:
        return max(dx, dy)
    return max(dx, dy)


def _seg_hits_rect(p0, p1, rect):
    """True if segment p0->p1 enters rect. Liang Barsky, clipped in place."""
    x0, y0, x1, y1 = rect
    t0, t1 = 0.0, 1.0
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    for num_, den in ((x0 - p0[0], dx), (p0[0] - x1, -dx),
                      (y0 - p0[1], dy), (p0[1] - y1, -dy)):
        if den == 0:
            if num_ > 0:
                return False
            continue
        t = num_ / den
        if den > 0:
            if t > t1:
                return False
            t0 = max(t0, t)
        else:
            if t < t0:
                return False
            t1 = min(t1, t)
    return t0 <= t1


def assert_no_label_collisions(layout, name):
    """Type is the layer a reader actually reads, so nothing is allowed to
    touch it. Checks every label plate against every other plate, against
    every glyph silhouette, and against every drawn edge. A line that runs
    under a plate reads as a broken line, which is why edges count too."""
    bad = []
    rects = _plate_rects(layout)
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            d = _gap(rects[i], rects[j])
            if d < LABEL_MIN_CLEARANCE:
                bad.append("%s: label %s and label %s clear by only %.1f"
                           % (name, rects[i][0], rects[j][0], d))
    for rid, x0, y0, x1, y1 in rects:
        for n in layout["nodes"]:
            r = layout["glyph"].get(n["kind"], 0) / 2.0
            if not r or n["id"] == rid:
                continue
            cx = min(max(n["x"], x0), x1)
            cy = min(max(n["y"], y0), y1)
            d = math.hypot(n["x"] - cx, n["y"] - cy) - r
            if d < LABEL_MIN_CLEARANCE:
                bad.append("%s: label %s and glyph %s clear by only %.1f"
                           % (name, rid, n["id"], d))
    for rid, x0, y0, x1, y1 in rects:
        grown = (x0 - 1.0, y0 - 1.0, x1 + 1.0, y1 + 1.0)
        for e in layout["edges"]:
            pts = e["pts"]
            for k in range(len(pts) - 1):
                if _seg_hits_rect(pts[k], pts[k + 1], grown):
                    bad.append("%s: %s edge runs under label %s"
                               % (name, e["kind"], rid))
                    break
    if bad:
        sys.stderr.write("eco_build: label collision\n  " +
                         "\n  ".join(bad) + "\n")
        sys.exit(1)


def build_static(layout, cls):
    box = layout["box"]
    glyph = layout["glyph"]
    out = ['<svg class="eco-svg %s" viewBox="0 0 %s %s" '
           'preserveAspectRatio="xMidYMid meet" '
           'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
           'focusable="false">' % (cls, num(box[0]), num(box[1]))]

    out.append('<g class="eco-svg-edges">')
    for e in layout["edges"]:
        out.append('<path class="eco-svg-edge eco-svg-edge--%s" d="%s"/>'
                   % (e["kind"], path_d(e["pts"])))
        if "arrow" in e:
            tri = e["arrow"]
            out.append('<path class="eco-svg-arrow eco-svg-arrow--%s" d="M%s %sL%s %sL%s %sZ"/>'
                       % (e["kind"], num(tri[0][0], 1), num(tri[0][1], 1),
                          num(tri[1][0], 1), num(tri[1][1], 1),
                          num(tri[2][0], 1), num(tri[2][1], 1)))
    out.append('</g>')

    # Core leader line, drawn instead of a box over the sphere.
    core = next(n for n in layout["nodes"] if n["kind"] == "core")
    cr = glyph["core"] / 2.0
    if core["anchor"] == "below":
        out.append('<line class="eco-svg-leader" x1="%s" y1="%s" x2="%s" y2="%s"/>'
                   % (num(core["x"]), num(core["y"] + cr + 2),
                      num(core["x"]), num(core["y"] + cr + LABEL_GAP_CORE)))

    out.append('<g class="eco-svg-glyphs">')
    for n in layout["nodes"]:
        if n["kind"] == "group":
            continue
        d = glyph[n["kind"]]
        sym = "eco-glyph-hi" if d >= GLYPH_FACET_THRESHOLD_PX else "eco-glyph-lo"
        out.append('<use class="eco-svg-glyph eco-svg-glyph--%s" href="#%s" '
                   'x="%s" y="%s" width="%s" height="%s"/>'
                   % (n["kind"], sym, num(n["x"] - d / 2.0, 1),
                      num(n["y"] - d / 2.0, 1), num(d), num(d)))
    out.append('</g>')

    out.append('<g class="eco-svg-labels">')
    for n in layout["nodes"]:
        g = label_geometry(n, glyph)
        if not g:
            continue
        if g["rect"]:
            rx, ry, rw, rh = g["rect"]
            out.append('<rect class="eco-svg-plate" x="%s" y="%s" width="%s" '
                       'height="%s" rx="3"/>'
                       % (num(rx, 1), num(ry, 1), num(rw, 1), num(rh, 1)))
        base = g["y"]
        for idx, (s, fs, tr) in enumerate(g["lines"]):
            cls2 = "eco-svg-label" if idx == 0 else "eco-svg-note"
            base_y = base + fs * 0.82 + (LINE_STEP if idx else 0)
            out.append('<text class="%s %s--%s" x="%s" y="%s" '
                       'text-anchor="%s">%s</text>'
                       % (cls2, cls2, g["kind"], num(g["x"], 1), num(base_y, 1),
                          g["anchor"], s))
    out.append('</g>')
    out.append('</svg>')
    return "".join(out)


# ==========================================================================
# SPLICE
# ==========================================================================

CONST_PATTERN = [
    ("GLYPH_PX_CORE", GLYPH_PX_CORE), ("GLYPH_PX_LOOP", GLYPH_PX_LOOP),
    ("GLYPH_PX_CHILD", GLYPH_PX_CHILD), ("GLYPH_PX_POLLER", GLYPH_PX_POLLER),
    ("GLYPH_PX_OPERATOR", GLYPH_PX_OPERATOR),
    ("GLYPH_PX_CORE_TALL", GLYPH_PX_CORE_TALL),
    ("GLYPH_PX_LOOP_TALL", GLYPH_PX_LOOP_TALL),
    ("GLYPH_PX_CHILD_TALL", GLYPH_PX_CHILD_TALL),
    ("GLYPH_PX_POLLER_TALL", GLYPH_PX_POLLER_TALL),
    ("GLYPH_PX_OPERATOR_TALL", GLYPH_PX_OPERATOR_TALL),
    ("GLYPH_FACET_THRESHOLD_PX", GLYPH_FACET_THRESHOLD_PX),
]


def assert_constants(html):
    bad = []
    for name, want in CONST_PATTERN:
        m = re.search(r"\bvar\s+%s\s*=\s*(\d+)\s*;" % re.escape(name), html)
        if not m:
            bad.append("%s is not declared in index.html" % name)
        elif int(m.group(1)) != want:
            bad.append("%s is %s in index.html, %s here" % (name, m.group(1), want))
    if bad:
        sys.stderr.write("eco_build: constant drift\n  " + "\n  ".join(bad) + "\n")
        sys.exit(1)


def splice(html, marker, payload, js=False):
    begin = ("/* %s:BEGIN */" if js else "<!-- %s:BEGIN -->") % marker
    end = ("/* %s:END */" if js else "<!-- %s:END -->") % marker
    i = html.find(begin)
    j = html.find(end)
    if i < 0 or j < 0:
        sys.stderr.write("eco_build: marker %s missing\n" % marker)
        sys.exit(1)
    return html[:i + len(begin)] + "\n" + payload + "\n" + html[j:]


def main():
    check = "--check" in sys.argv
    html = INDEX.read_text(encoding="utf-8")
    assert_constants(html)

    wide = build_wide()
    tall = build_tall()
    assert_no_label_collisions(wide, "wide")
    assert_no_label_collisions(tall, "tall")

    defs = build_defs()
    static = (build_static(wide, "eco-svg--wide") +
              build_static(tall, "eco-svg--tall"))
    data = ("var ECO_LAYOUT = " +
            json.dumps({"wide": wide, "tall": tall}, separators=(",", ":")) + ";")

    out = splice(html, "ECO-DEFS", defs)
    out = splice(out, "ECO-STATIC", static)
    out = splice(out, "ECO-DATA", data, js=True)

    if check:
        if out != html:
            sys.stderr.write("eco_build: index.html is stale, rerun without --check\n")
            return 1
        print("ok\tindex.html geometry is current")
        return 0

    if out != html:
        INDEX.write_text(out, encoding="utf-8")
        print("wrote\t%s" % INDEX)
    else:
        print("ok\t%s already current" % INDEX)
    return 0


if __name__ == "__main__":
    sys.exit(main())
