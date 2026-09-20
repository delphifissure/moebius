"""S35 §44: the wrap test as ENCLOSURE. Per contour of the unit (outer and holes, every piece): the span of the front (the
contour less its largest run of non-front texels), closed by the chord between its ends; the share of the unit's own texels
that lie inside those closed spans. A thing's front bends around its mass (a figure on the ground: everything above the
contact chord; a disc: all of it); a surface's front is a line its mass lies beside (a horizon, hills or no hills: the
slivers above the chord). Printed beside the centroid rule's gap and the turning rule's sum (wrap_front.npz from WRAP_DUMP=1).
  wrap_enclose.py <probe dir> <dump dir> [n units] [tangent step]"""
import sys, json, numpy as np, cv2
P, DD = sys.argv[1:3]; NU = int(sys.argv[3]) if len(sys.argv) > 3 else 12; STEP = int(sys.argv[4]) if len(sys.argv) > 4 else 5
m = json.load(open(f'{P}/meta.json')); pw, ph = m['pw'], m['ph']
z = np.load(f'{DD}/wrap_front.npz'); tex = z['tex']; gap = z['gap']; thing = z['thing']; px = z['px']; um = z['unitMap'].reshape(ph, pw)
front = np.zeros(ph * pw, bool); front[tex] = True; front = front.reshape(ph, pw)
def spans(mask, fr, step=STEP):
    """per contour: (ordered points, inSpan flags, signed turning over the span)"""
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE); out = []
    for c in cs:
        pts = c[:, 0, :]; n = len(pts)
        if n < 2 * step + 2: continue
        f = fr[pts[:, 1], pts[:, 0]]
        if not f.any(): continue
        P_ = pts.astype(float); tang = P_[(np.arange(n) + step) % n] - P_[(np.arange(n) - step) % n]
        ang = np.arctan2(tang[:, 1], tang[:, 0]); d = np.diff(np.r_[ang, ang[0]]); d = (d + np.pi) % (2 * np.pi) - np.pi
        if f.all(): out.append((pts, np.ones(n, bool), float(d.sum()))); continue
        nf = ~f; k0 = int(np.argmax(f)); r = np.roll(nf, -k0)
        e = np.diff(np.r_[0, r.astype(int), 0]); st = np.flatnonzero(e == 1); en = np.flatnonzero(e == -1)
        L = en - st; g = int(np.argmax(L)); gs, ge = st[g], en[g]
        inSpan = np.ones(n, bool); inSpan[gs:ge] = False; inSpan = np.roll(inSpan, k0)
        both = inSpan & np.roll(inSpan, -1); out.append((pts, inSpan, float(d[both].sum())))
    return out
def enclosure(mask, fr):
    """(share of the unit's texels inside its closed front spans, net turning, contours with a front)"""
    fill = np.zeros(mask.shape, np.uint8); tot = 0.0; nC = 0
    for pts, inSpan, T in spans(mask, fr):
        nC += 1; tot += T
        # the span in contour order, starting inside it (roll to the first span point after a gap point)
        n = len(pts); k = np.flatnonzero(inSpan & ~np.roll(inSpan, 1)); k = int(k[0]) if len(k) else 0
        order = np.roll(np.arange(n), -k); sp = pts[order][inSpan[order]]
        if len(sp) >= 3: cv2.fillPoly(fill, [sp.astype(np.int32).reshape(-1, 1, 2)], 1)
    inside = int(np.count_nonzero(fill.astype(bool) & mask)); return inside / max(1, int(mask.sum())), tot, nC
if __name__ == '__main__':
    big = np.argsort(-px)[:NU]
    print(f'{"unit":>12s} {"px":>8s} | centroid gap verdict | contours  turning  verdict | enclosed  verdict')
    for u in big:
        if px[u] == 0: continue
        mask = um == u; ys, xs = np.nonzero(mask); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        share, T, nC = enclosure(mask[y0:y1, x0:x1], front[y0:y1, x0:x1])
        name = f'seg {u}' if u < 256 else f'comp {u - 256}'
        print(f'{name:>12s} {int(px[u]):8d} | {np.degrees(gap[u]):6.0f} {"THING" if thing[u] else "surface":7s} | {nC:8d} {np.degrees(T):+8.0f}  {"THING" if abs(T) >= np.pi - 1e-6 else "surface":7s} | {100*share:6.1f} %  {"THING" if share > 0.5 else "surface"}')
