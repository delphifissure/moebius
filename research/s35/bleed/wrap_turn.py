"""S35 §43: the wrap test as the TURNING of the stepped front boundary. The unit's outer contour is traced (oriented); the
contour points that are front texels (in front of a neighbour by a step and by the medians gate, from wrap_front.npz) form
runs; along each run the tangent's signed rotation is accumulated; a unit is wrapped when the net turning over its front
runs reaches a half turn (|sum| >= pi): a figure standing on the ground turns half a turn from foot to foot over the head,
a disc a full turn, a horizon -- hills included -- nets nothing, a table's top edge nothing.
  wrap_turn.py <probe dir> <dump dir> [n units]"""
import sys, json, numpy as np
P, DD = sys.argv[1:3]; NU = int(sys.argv[3]) if len(sys.argv) > 3 else 12
m = json.load(open(f'{P}/meta.json')); pw, ph = m['pw'], m['ph']
z = np.load(f'{DD}/wrap_front.npz'); unit = z['unit']; tex = z['tex']; gap = z['gap']; thing = z['thing']; px = z['px']; um = z['unitMap'].reshape(ph, pw)
front = np.zeros(ph * pw, bool); front[tex] = True; front = front.reshape(ph, pw)
def trace(mask):
    """outer contour of a 4-connected-ish blob as an ordered list of pixel coords (Moore neighbour tracing, 8-connected)"""
    ys, xs = np.nonzero(mask)
    if len(ys) == 0: return []
    H, W = mask.shape
    k = np.argmin(ys * W + xs); sy, sx = int(ys[k]), int(xs[k])   # top-left-most pixel: start, coming from the left
    nbr = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]   # (dy, dx) clockwise from west
    def inside(y, x): return 0 <= y < H and 0 <= x < W and mask[y, x]
    pts = [(sy, sx)]; cy, cx = sy, sx; b = 0   # b: index of the backtrack direction (west)
    for _ in range(8 * mask.sum() + 8):
        found = False
        for j in range(8):
            d = (b + 1 + j) % 8; ny, nx = cy + nbr[d][0], cx + nbr[d][1]
            if inside(ny, nx):
                cy, cx = ny, nx; b = (d + 4) % 8; found = True; break
        if not found: break
        if (cy, cx) == (sy, sx): break
        pts.append((cy, cx))
    return pts
def turning(pts, isF, step=3):
    """net signed turning of the tangent along the front runs of a closed contour"""
    n = len(pts)
    if n < 2 * step + 2: return 0.0, 0
    P_ = np.array(pts, float); tang = P_[(np.arange(n) + step) % n] - P_[(np.arange(n) - step) % n]
    ang = np.arctan2(tang[:, 0], tang[:, 1])
    d = np.diff(np.r_[ang, ang[0]]); d = (d + np.pi) % (2 * np.pi) - np.pi   # rotation from point k to k+1, wrapped
    f = np.array(isF, bool); both = f & np.roll(f, -1)                       # a rotation counts when it happens inside a front run
    runs = int(np.sum(f & ~np.roll(f, 1)))
    return float(np.sum(d[both])), runs
big = np.argsort(-px)[:NU]
print(f'{"unit":>12s} {"px":>8s} | centroid gap verdict | contour pts front pts runs  net turning  verdict')
for u in big:
    if px[u] == 0: continue
    mask = um == u; ys, xs = np.nonzero(mask); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = mask[y0:y1, x0:x1]; pts = trace(sub)
    isF = [front[y0 + y, x0 + x] for (y, x) in pts]
    T, runs = turning(pts, isF)
    name = f'seg {u}' if u < 256 else f'comp {u - 256}'
    print(f'{name:>12s} {int(px[u]):8d} | {np.degrees(gap[u]):6.0f} {"THING" if thing[u] else "surface":7s} | {len(pts):8d} {int(np.sum(isF)):9d} {runs:4d}  {np.degrees(T):+8.0f} deg  {"THING" if abs(T) >= np.pi - 1e-6 else "surface"}')
