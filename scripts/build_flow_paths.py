"""Precomputes the flow-map routes and arrowheads (js/specs/02_flow_map.vg.json).

Why precompute: an arrowhead has to point along the route as it is drawn on screen, and the route
has to stop at the arrowhead's base so the two don't overlap (Jenny et al. 2017). Vega-Lite can't
project a point inside an expression, so this script does it with the same projection the map uses
(Equal Earth, rotated to centre on 140°E) and writes data/flow_paths.json:
  - path:  the route from Canberra, as lon/lat points, trimmed to the arrowhead's base
  - arrow: the arrowhead triangle as lon/lat points
Routes follow great circles, except Kuala Lumpur, which is bent away from the Britain route so the
two don't run on top of each other. Arrowheads scale with line width, with a minimum size so thin
flows still get a readable arrow.

Run from the repo root:  python scripts/build_flow_paths.py
"""
import csv, json, math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
O = (149.13, -35.2809)                       # Canberra (lon, lat)
ROT = -140.0                                 # projection.rotate([-140, 0, 0])
REF_W = 735                                  # chart width the sizes below are tuned for (desktop, 8 of 12 columns)
K = REF_W / 5.45                             # px per projected unit at REF_W (spec: scale = width / 5.45)
MAX_W = 22                                   # widest line (Britain, 1,905 places) at REF_W
NODE_GAP = 6                                 # px between arrow tip and destination centre (node radius + stroke)

# --- Equal Earth (same constants as d3-geo) ---
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2

def fwd(lon, lat):
    lam = math.radians(((lon + ROT + 180) % 360) - 180)
    l = math.asin(M * math.sin(math.radians(lat)))
    l2 = l * l; l6 = l2 ** 3
    x = lam * math.cos(l) / (M * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)))
    y = l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2))
    return x, y

def inv(x, y):
    l = y
    for _ in range(12):
        l2 = l * l; l6 = l2 ** 3
        fy = l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2)) - y
        fpy = A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)
        d = fy / fpy; l -= d
        if abs(d) < 1e-12: break
    l2 = l * l; l6 = l2 ** 3
    lam = M * x * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)) / math.cos(l)
    lon = math.degrees(lam) - ROT
    lon = ((lon + 180) % 360) - 180
    return lon, math.degrees(math.asin(math.sin(l) / M))

def great_circle(a, b, n=160):
    def vec(p):
        lo, la = map(math.radians, p); return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
    va, vb = vec(a), vec(b)
    om = math.acos(max(-1, min(1, sum(i * j for i, j in zip(va, vb)))))
    pts = []
    for i in range(n + 1):
        t = i / n
        s1, s2 = math.sin((1 - t) * om) / math.sin(om), math.sin(t * om) / math.sin(om)
        v = [s1 * p + s2 * q for p, q in zip(va, vb)]
        pts.append((math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(v[2] / math.hypot(*v)))))
    return pts

def bent(a, b, bend, n=160):
    """Quadratic curve drawn in projected space, bent sideways by `bend` (fraction of its length)."""
    (x0, y0), (x1, y1) = fwd(*a), fwd(*b)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    cx, cy = mx + nx * bend * L, my + ny * bend * L
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        pts.append(inv(x, y))
    return pts

def point_back(proj, dist):
    """Point `dist` projected units back from the end of a projected polyline: (x, y, index)."""
    acc = 0
    for i in range(len(proj) - 1, 0, -1):
        (x1, y1), (x0, y0) = proj[i], proj[i - 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        if acc + seg >= dist:
            t = (dist - acc) / seg
            return x1 + (x0 - x1) * t, y1 + (y0 - y1) * t, i
        acc += seg
    return proj[0][0], proj[0][1], 1

def clockwise(ring):
    area = sum((ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]) for i in range(len(ring) - 1))
    return ring if area < 0 else ring[::-1]

# --- destinations: same grouping and averaging as the spec ---
rows = [r for r in csv.DictReader(open(ROOT / 'data' / 'games.csv', encoding='utf-8')) if r['home'] == 'Away']
def dest(r):
    if r['host'] in ('England', 'Scotland', 'Wales'): return 'Britain'
    if r['host'] == 'New Zealand': return 'New Zealand'
    if r['city'] in ('Vancouver', 'Victoria', 'Edmonton'): return 'Western Canada'
    return r['city']
groups = defaultdict(list)
for r in rows: groups[dest(r)].append(r)

BEND = {'Kuala Lumpur': 0.38}                # positive = bend to the west (left of the route as drawn)
out = []
for d, rs in groups.items():
    D = (sum(float(r['lon']) for r in rs) / len(rs), sum(float(r['lat']) for r in rs) / len(rs))
    places = sum(int(r['aus_team']) for r in rs)
    w = 1 + (MAX_W - 1) * places / 1905                      # line width in px at REF_W
    aw = max(1.35 * w, 13)                                   # arrow width: scaled, enlarged for thin flows
    al = max(0.8 * aw, 11)                                   # arrow length
    pts = bent(O, D, BEND[d]) if d in BEND else great_circle(O, D)
    proj = [fwd(*p) for p in pts]
    tx, ty, _ = point_back(proj, NODE_GAP / K)
    bx, by, bi = point_back(proj, (NODE_GAP + al) / K)
    ux, uy = tx - bx, ty - by; n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
    px, py = -uy, ux
    h = aw / 2 / K
    tip, c1, c2 = inv(tx, ty), inv(bx + px * h, by + py * h), inv(bx - px * h, by - py * h)
    # the line stops just inside the arrow's base so no gap shows
    ex, ey, _ = point_back(proj, (NODE_GAP + al - 1.5) / K)
    path = [list(map(lambda v: round(v, 4), p)) for p in pts[:bi]] + [[round(v, 4) for v in inv(ex, ey)]]
    ring = clockwise([tip, c1, c2, tip])
    out.append({'dest': d, 'path': path, 'arrow': [[round(a, 4), round(b, 4)] for a, b in ring]})

(ROOT / 'data' / 'flow_paths.json').write_text(json.dumps(out, separators=(',', ':')), encoding='utf-8')
print('wrote', len(out), 'routes')
