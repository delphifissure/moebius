"""S35 §43-44: the wrap test as the TURNING of the stepped front over ALL of a unit's contours (outer and holes, every piece):
the discrete Gauss-Bonnet of the front. Along each contour the tangent's signed rotation is summed over the runs of front
texels; the unit is wrapped when the net turning over all its contours reaches a half turn in magnitude.
  wrap_turn2.py <probe dir> <dump dir> [n units] [tangent step]"""
import sys, json, numpy as np, cv2
P, DD = sys.argv[1:3]; NU = int(sys.argv[3]) if len(sys.argv) > 3 else 12; STEP = int(sys.argv[4]) if len(sys.argv) > 4 else 5
m = json.load(open(f'{P}/meta.json')); pw, ph = m['pw'], m['ph']
z = np.load(f'{DD}/wrap_front.npz'); unit = z['unit']; tex = z['tex']; gap = z['gap']; thing = z['thing']; px = z['px']; um = z['unitMap'].reshape(ph, pw)
front = np.zeros(ph * pw, bool); front[tex] = True; front = front.reshape(ph, pw)
def turning_of(mask, fr, step=STEP):
    """net signed turning of the tangent along the front runs of every contour of mask (fr: front flags, same shape)"""
    cs, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    total = 0.0; nF = 0; nRuns = 0; nC = 0
    for c in cs:
        pts = c[:, 0, :]; n = len(pts)
        if n < 2 * step + 2: continue
        f = fr[pts[:, 1], pts[:, 0]]
        if not f.any(): continue
        nC += 1
        P_ = pts.astype(float); tang = P_[(np.arange(n) + step) % n] - P_[(np.arange(n) - step) % n]
        ang = np.arctan2(tang[:, 1], tang[:, 0])
        d = np.diff(np.r_[ang, ang[0]]); d = (d + np.pi) % (2 * np.pi) - np.pi
        both = f & np.roll(f, -1)
        total += float(np.sum(d[both])); nF += int(f.sum()); nRuns += int(np.sum(f & ~np.roll(f, 1)))
    return total, nF, nRuns, nC
if __name__ == '__main__':
    big = np.argsort(-px)[:NU]
    print(f'{"unit":>12s} {"px":>8s} | centroid gap verdict | contours front pts runs  net turning  verdict')
    for u in big:
        if px[u] == 0: continue
        mask = um == u; ys, xs = np.nonzero(mask); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        T, nF, nR, nC = turning_of(mask[y0:y1, x0:x1], front[y0:y1, x0:x1])
        name = f'seg {u}' if u < 256 else f'comp {u - 256}'
        print(f'{name:>12s} {int(px[u]):8d} | {np.degrees(gap[u]):6.0f} {"THING" if thing[u] else "surface":7s} | {nC:8d} {nF:9d} {nR:4d}  {np.degrees(T):+8.0f} deg  {"THING" if abs(T) >= np.pi - 1e-6 else "surface"}')
