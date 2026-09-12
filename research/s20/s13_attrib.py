#!/usr/bin/env python3
"""S13b hole attribution, offline, from a probe dump: rebuild the CPU sweep's coverage (FG quads at source depth, plate quads at
plate depth, near wins; the app's shift law) at a pose, find the in-frame hole cells, and for each hole name the texel that
would have to cover it at the depth of the far surface next to the hole, and why it did not.
Usage: s13_attrib.py <probe dir> fx fy [--plate2]"""
import sys, json, numpy as np, os
from scipy import ndimage
d = sys.argv[1]; fx, fy = float(sys.argv[2]), float(sys.argv[3]); use2 = '--plate2' in sys.argv
m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']; N = pw * ph
outer, inner, pn, D, TW, TH = m['outer'], m['inner'], m['pn'], m['D'], m['terrariumWidth'], m['terrariumHeight']
dQ = np.fromfile(d + '/dQ.f32', np.float32); pF = np.fromfile(d + '/plateF.f32', np.float32).reshape(ph, pw)[::-1].reshape(-1)
dis = np.fromfile(d + '/disocc.u8', np.uint8) > 0; car = np.fromfile(d + '/carrier.u8', np.uint8) > 0
torn = np.fromfile(d + '/fgTorn.u8', np.uint8) > 0 if os.path.exists(d + '/fgTorn.u8') else np.zeros(N, bool)
pF2 = np.fromfile(d + '/plateF2.f32', np.float32).reshape(ph, pw)[::-1].reshape(-1) if os.path.exists(d + '/plateF2.f32') else None
has2 = np.fromfile(d + '/plate2Has.u8', np.uint8) > 0 if os.path.exists(d + '/plate2Has.u8') else None
la, fa = pw / ph, TW / TH; layerW = TW if la > fa else TH * la; pxw = pw / layerW; ex = D * np.tan(np.radians(45)); asp = np.tan(np.radians(30)) / np.tan(np.radians(45))
def fwd(dd):
    dd = np.asarray(dd, np.float64); z = np.where(dd < pn, -outer + outer * ((dd / pn) ** 2 * (3 - 2 * dd / pn)), inner * (((dd - pn) / (1 - pn)) ** 2 * (3 - 2 * (dd - pn) / (1 - pn))))
    return ex * z / np.maximum(1e-4, D - z) * pxw
ox, oy = fx, fy * asp   # pose in units of ex along x and of ex*asp along y -> shift = fwd(d) * (fx, fy*asp)
rimT = m['rimT']
def ze(dd):
    dd = np.asarray(dd, np.float64); z = np.where(dd < pn, -outer + outer * ((dd / pn) ** 2 * (3 - 2 * dd / pn)), inner * (((dd - pn) / (1 - pn)) ** 2 * (3 - 2 * (dd - pn) / (1 - pn)))); return D - z
def coverage(depth, mask, sign, tear=True, keepAll=None):
    """near-wins z-buffer over quads (texel, right, down, diag) warped by their own depth shifts; returns zb, own"""
    zb = np.full(N, -1.0); own = np.full(N, -1, np.int64)
    X, Y = np.meshgrid(np.arange(pw), np.arange(ph)); X = X.reshape(-1).astype(np.float64); Y = Y.reshape(-1).astype(np.float64)
    s = sign * fwd(depth); wx = X + s * ox; wy = Y + s * oy
    idx = np.arange(N); q = idx[(idx % pw < pw - 1) & (idx // pw < ph - 1)]
    if mask is not None: q = q[mask[q] & mask[q + 1] & mask[q + pw] & mask[q + pw + 1]]
    if tear:   # the rim law: a quad with an unjoined edge is not drawn (keepAll marks quads kept regardless: carrier-carrier, seams stretched)
        Z = ze(depth); e = np.ones(len(q), bool)
        for a, b in [(0, 1), (0, pw), (1, pw + 1), (pw, pw + 1)]:
            r = np.maximum(Z[q + a], Z[q + b]) / np.minimum(Z[q + a], Z[q + b]); e &= (r <= rimT)
        if keepAll is not None: e |= keepAll[q] & keepAll[q + 1] & keepAll[q + pw] & keepAll[q + pw + 1]
        q = q[e]
    c = [q, q + 1, q + pw, q + pw + 1]
    mnx = np.floor(np.min([wx[k] for k in c], 0)).astype(int); mxx = np.floor(np.max([wx[k] for k in c], 0)).astype(int)
    mny = np.floor(np.min([wy[k] for k in c], 0)).astype(int); mxy = np.floor(np.max([wy[k] for k in c], 0)).astype(int)
    dq = np.max([depth[k] for k in c], 0)   # farthest-corner rule would be min; the app takes the near corner for the FG and interpolates for the plate — use the mean as a middle ground
    dq = np.mean([depth[k] for k in c], 0)
    # fill boxes (vectorised per box size class would be complex; loop over quads whose box is small, which is nearly all)
    for k in range(len(q)):
        x0, x1, y0, y1 = max(0, mnx[k]), min(pw - 1, mxx[k]), max(0, mny[k]), min(ph - 1, mxy[k])
        if x1 < x0 or y1 < y0: continue
        sub = (slice(y0, y1 + 1), slice(x0, x1 + 1)); zz = zb.reshape(ph, pw)[sub]; oo = own.reshape(ph, pw)[sub]
        w = dq[k] > zz; zz[w] = dq[k]; oo[w] = q[k]
    return zb, own
res = {}
for sign in (1, -1):
    zbF, ownF = coverage(dQ.astype(np.float64), ~torn, sign)
    plateMask = np.ones(N, bool)
    zbP, ownP = coverage(pF.astype(np.float64), None, sign, tear=True, keepAll=car)
    # combine: near wins
    zb = np.maximum(zbF, zbP); own = np.where(zbF >= zbP, np.where(zbF >= 0, -2, -1), ownP); own = np.where((zbF < 0) & (zbP < 0), -1, own)
    if use2 and pF2 is not None and has2 is not None:
        zb2, own2 = coverage(pF2.astype(np.float64), has2, sign, tear=True, keepAll=has2); better = (zb2 > zb); zb = np.where(better, zb2, zb); own = np.where(better, own2 + N, own)
    hole = (own == -1).reshape(ph, pw)
    lab, n = ndimage.label(hole); border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    interior = hole & ~np.isin(lab, list(border)); res[sign] = (interior, own, zb)
    print(f'sign {sign:+d}: hole cells {int(hole.sum())}, interior {int(interior.sum())}')
sign = max(res, key=lambda s: res[s][0].sum()) if False else (1 if res[1][0].sum() < res[-1][0].sum() else -1)
# the app's sign: the one whose interior hole count is the plausible one is unknown a priori; report both, attribute the larger? No: attribute the one matching the classmap (the caller compares)
for sign in (1, -1):
    interior, own, zb = res[sign]; ys, xs = np.nonzero(interior)
    if len(xs) == 0: continue
    ownP = own.reshape(ph, pw); zbm = zb.reshape(ph, pw)
    cls = {'beyond frame': 0, 'never demanded (not in band)': 0, 'in band, far side too NEAR (> tol)': 0, 'in band, far side too FAR (> tol)': 0, 'in band, depth matches (coverage gap)': 0, 'no far surface next to the hole': 0}
    tol = 0.01; R = 6; plate2could = 0
    for y, x in zip(ys, xs):
        y0, y1, x0, x1 = max(0, y - R), min(ph, y + R + 1), max(0, x - R), min(pw, x + R + 1)
        o = ownP[y0:y1, x0:x1]; zz = zbm[y0:y1, x0:x1]; sel = (o != -1)
        if not sel.any(): cls['no far surface next to the hole'] += 1; continue
        dneed = float(np.min(zz[sel])); s = sign * float(fwd(dneed)); tx, ty = int(round(x - s * ox)), int(round(y - s * oy))
        if tx < 0 or ty < 0 or tx >= pw or ty >= ph: cls['beyond frame'] += 1; continue
        t = ty * pw + tx
        if not dis[t]: cls['never demanded (not in band)'] += 1; continue
        if pF[t] > dneed + tol: cls['in band, far side too NEAR (> tol)'] += 1
        elif pF[t] < dneed - tol: cls['in band, far side too FAR (> tol)'] += 1
        else: cls['in band, depth matches (coverage gap)'] += 1
        if pF2 is not None and has2 is not None and has2[t] and abs(pF2[t] - dneed) <= tol: plate2could += 1
    print(f'sign {sign:+d} attribution of {len(xs)} interior hole cells: ' + json.dumps(cls) + f'; plate 2 at the needed depth for {plate2could} of them')
