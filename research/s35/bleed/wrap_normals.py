"""S35 §43: the wrap test on OUTWARD NORMALS. For every unit's stepped front boundary (wrap_front.npz from WRAP_DUMP=1), the
direction from each front texel to its far-side 4-neighbour (the texel across the step); a unit is 'wrapped' when those
directions are not contained in an open half-plane (largest angular gap <= pi: two opposite directions suffice). Prints, per
large unit, the centroid rule's gap and verdict beside the normals' gap and verdict.
  wrap_normals.py <probe dir> <dump dir> [n units]"""
import sys, json, numpy as np
P, DD = sys.argv[1:3]; NU = int(sys.argv[3]) if len(sys.argv) > 3 else 12
m = json.load(open(f'{P}/meta.json')); pw, ph = m['pw'], m['ph']
dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw)
z = np.load(f'{DD}/wrap_front.npz'); unit = z['unit']; tex = z['tex']; gap = z['gap']; thing = z['thing']; px = z['px']; um = z['unitMap'].reshape(ph, pw)
outer, inner, pn, D = m['outer'], m['inner'], m['pn'], m['D']; q = float(m.get('quantum', 1 / 65535))
def z_of_d(d):
    d = np.clip(d, 0, 1); s1 = d / pn; s2 = (d - pn) / (1 - pn); return np.where(d < pn, -outer + outer * (s1 * s1 * (3 - 2 * s1)), inner * (s2 * s2 * (3 - 2 * s2)))
disp = lambda d: 1.0 / np.maximum(1e-4, D - z_of_d(d)); DISP = disp(dQ.astype(float)); TOL = np.abs(disp(np.minimum(1, dQ + q)) - disp(np.maximum(0, dQ - q)))
# outward normals: for each front texel, the 4-neighbours in another unit that are behind it by a step
tx = tex % pw; ty = tex // pw; dirs = []; units = []
for (dx, dy, ang) in ((1, 0, 0.0), (-1, 0, np.pi), (0, 1, np.pi / 2), (0, -1, -np.pi / 2)):
    xn = tx + dx; yn = ty + dy; ok = (xn >= 0) & (xn < pw) & (yn >= 0) & (yn < ph)
    i = np.where(ok, yn * pw + xn, 0)
    far = ok & (um.ravel()[i] != unit) & (DISP.ravel()[tex] > DISP.ravel()[i] + np.maximum(TOL.ravel()[tex], TOL.ravel()[i]))
    dirs.append(np.where(far, ang, np.nan)); units.append(unit)
A = np.concatenate(dirs); U = np.concatenate(units); okA = np.isfinite(A); A = A[okA]; U = U[okA]
print(f'units with a front: {len(np.unique(U))}; normals {len(A)}')
big = np.argsort(-px)[:NU]
print(f'{"unit":>12s} {"px":>8s} | centroid gap  verdict | normals: L R U D  gap  verdict')
for u in big:
    if px[u] == 0: continue
    a = np.sort(A[U == u])
    if len(a) == 0: ng = 2 * np.pi; cnt = (0, 0, 0, 0)
    else:
        g = np.diff(a); ng = max(float(g.max()) if len(g) else 0.0, float(2 * np.pi - (a[-1] - a[0])))
        cnt = tuple(int((np.isclose(a, v)).sum()) for v in (np.pi, 0.0, -np.pi / 2, np.pi / 2))
    name = f'seg {u}' if u < 256 else f'comp {u - 256}'
    print(f'{name:>12s} {int(px[u]):8d} | {np.degrees(gap[u]):6.0f}  {"THING" if thing[u] else "surface":7s} | {cnt[0]:5d} {cnt[1]:5d} {cnt[2]:5d} {cnt[3]:5d}  {np.degrees(ng):4.0f}  {"THING" if ng <= np.pi + 1e-9 else "surface"}')
