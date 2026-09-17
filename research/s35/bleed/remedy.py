"""Preview of the remedy on the rim windows: occluder share of the colour a band texel would get from (a) the app's window
(mean over w = min(len, g+1) texels from the rim), (b) the median over the far run's full length (the run the app already has:
consecutive texels joined by the app's law along the axis), (c) the run median after skipping leading texels that are blends
of the occluder colour (a texel whose projection onto the occluder->run line exceeds the run's own colour spread, no constant).
Occluder share t: 0 = the run's own colour (median of texels 4..12 beyond the rim), 1 = the occluder edge texel's colour."""
import sys, json, numpy as np
from PIL import Image
D, C = sys.argv[1], sys.argv[2]
meta = json.load(open(f'{D}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{D}/dQ.f32', np.float32).astype(np.float64); dis = np.fromfile(f'{D}/disocc.u8', np.uint8) > 0
J = np.fromfile(f'{D}/farRimJ.i32', np.int32).reshape(N, 2); W = np.fromfile(f'{D}/farRimW.i32', np.int32).reshape(N, 2); ax = np.fromfile(f'{D}/farAxis.u8', np.uint8)
col = np.asarray(Image.open(C).convert('RGB').resize((pw, ph), Image.BILINEAR)).astype(np.float64).reshape(N, 3)
outer, inner, pn, Dz, t = meta['outer'], meta['inner'], meta['pn'], meta.get('D', 0.2), meta['rimT']; skyQ = 0.5 / 65535
Q = float(meta.get('quantum') or meta.get('step') or 1 / 255)
def z_of_d(d):
    d = np.clip(d, 0, 1); s1 = d / pn; s2 = (d - pn) / (1 - pn)
    return np.where(d < pn, -outer + outer * (s1 * s1 * (3 - 2 * s1)), inner * (s2 * s2 * (3 - 2 * s2)))
def ze(d): return np.maximum(1e-4, Dz - z_of_d(d))
def disp(d): return 1.0 / ze(d)
def tolAt(d): return np.abs(disp(np.minimum(1, d + Q)) - disp(np.maximum(0, d - Q))) + 1e-9
DISP = disp(dQ); ZE = ze(dQ); TOL = tolAt(dQ)
def joined_arr(I, Jj):
    dA = dQ[I]; dB = dQ[Jj]; skyA = dA < skyQ; skyB = dB < skyQ
    a = ZE[I]; b = ZE[Jj]; ratio = np.where(a > b, a / b, b / a) <= t
    xi = I % pw; yi = I // pw; xj = Jj % pw; yj = Jj // pw; dx = xj - xi; dy = yj - yi
    da = DISP[I]; db = DISP[Jj]; tl = np.maximum(TOL[I], TOL[Jj])
    xp = xi - dx; yp = yi - dy; okp = (xp >= 0) & (xp < pw) & (yp >= 0) & (yp < ph)
    pr = np.zeros_like(da); pr[okp] = 2 * da[okp] - DISP[yp[okp] * pw + xp[okp]]; lin1 = okp & (np.abs(db - pr) <= tl)
    xn = xj + dx; yn = yj + dy; okn = (xn >= 0) & (xn < pw) & (yn >= 0) & (yn < ph)
    pn_ = np.zeros_like(da); pn_[okn] = 2 * db[okn] - DISP[yn[okn] * pw + xn[okn]]; lin2 = okn & (np.abs(da - pn_) <= tl)
    return np.where(skyA | skyB, skyA & skyB, ratio | lin1 | lin2)
idx = np.arange(N).reshape(ph, pw)
jh = joined_arr(idx[:, :-1].ravel(), idx[:, 1:].ravel()).reshape(ph, pw - 1); jv = joined_arr(idx[:-1, :].ravel(), idx[1:, :].ravel()).reshape(ph - 1, pw)
# run extents along each axis: runEnd[+x], runEnd[-x], runEnd[+y], runEnd[-y] as the number of joined texels ahead
def run_len(joined, axis):
    # joined[y, x] : texel (y,x) joined to (y,x+1) for axis 0. length ahead in + direction
    if axis == 0:
        L = np.zeros((ph, pw), np.int32)
        for x in range(pw - 2, -1, -1): L[:, x] = np.where(joined[:, x], L[:, x + 1] + 1, 0)
        Lm = np.zeros((ph, pw), np.int32)
        for x in range(1, pw): Lm[:, x] = np.where(joined[:, x - 1], Lm[:, x - 1] + 1, 0)
    else:
        L = np.zeros((ph, pw), np.int32)
        for y in range(ph - 2, -1, -1): L[y, :] = np.where(joined[y, :], L[y + 1, :] + 1, 0)
        Lm = np.zeros((ph, pw), np.int32)
        for y in range(1, ph): Lm[y, :] = np.where(joined[y - 1, :], Lm[y - 1, :] + 1, 0)
    return L.ravel(), Lm.ravel()
Lxp, Lxm = run_len(jh, 0); Lyp, Lym = run_len(jv, 1)
K = 24; res = []
for slot, side in ((0, -1), (1, 1)):
    ok = dis & (J[:, slot] >= 0) & (ax > 0); j = J[ok, slot]; w = W[ok, slot]; a = ax[ok]
    key = j.astype(np.int64) * 4 + slot * 2 + (a - 1); _, first = np.unique(key, return_index=True); j = j[first]; w = w[first]; a = a[first]
    st = np.where(a == 1, 1, pw) * side
    Lx_ = Lxp if side > 0 else Lxm; Ly_ = Lyp if side > 0 else Lym; ahead = np.where(a == 1, Lx_[j], Ly_[j])   # joined texels beyond the rim texel
    runlen = ahead + 1
    jx = j % pw; jy = j // pw
    prof = np.full((len(j), K, 3), np.nan)
    for k in range(K):
        tx = np.where(a == 1, jx + side * k, jx); ty = np.where(a == 1, jy, jy + side * k); ins = (tx >= 0) & (tx < pw) & (ty >= 0) & (ty < ph) & (k < runlen)
        prof[ins, k] = col[ty[ins] * pw + tx[ins]]
    bx = np.where(a == 1, jx - side, jx); by = np.where(a == 1, jy, jy - side); okb = (bx >= 0) & (bx < pw) & (by >= 0) & (by < ph)
    occ = np.full((len(j), 3), np.nan); occ[okb] = col[by[okb] * pw + bx[okb]]
    ref = np.nanmedian(prof[:, 4:12], axis=1)
    valid = np.isfinite(ref[:, 0]) & np.isfinite(occ[:, 0]) & (np.linalg.norm(occ - ref, axis=1) > 24) & (runlen >= 4)
    P = prof[valid]; o = occ[valid]; r = ref[valid]; wv = np.minimum(w[valid], K); rl = np.minimum(runlen[valid], K)
    def share(c): return np.clip(((c - r) * (o - r)).sum(1) / np.maximum(1e-6, ((o - r) ** 2).sum(1)), -1, 2)
    # (a) the app's window mean
    ca = np.array([np.nanmean(P[n, :wv[n]], axis=0) for n in range(len(P))])
    # (b) the run median
    cb = np.array([np.nanmedian(P[n, :rl[n]], axis=0) for n in range(len(P))])
    # (c) run median after skipping blended leading texels: spread = MAD of the run's colour about its median (per channel, summed);
    #     a leading texel is a blend while its distance to the median exceeds that spread and it lies toward the occluder
    cc = np.zeros_like(cb); nskip = np.zeros(len(P), int)
    for n in range(len(P)):
        run = P[n, :rl[n]]; med = np.nanmedian(run, axis=0); spread = np.nanmedian(np.abs(run - med).sum(1)) * 1.4826 + 1e-6
        k = 0
        while k < rl[n] - 1:
            c = run[k]; toward = ((c - med) * (o[n] - med)).sum() > 0
            if toward and np.abs(c - med).sum() > spread: k += 1
            else: break
        nskip[n] = k; cc[n] = np.nanmedian(run[k:], axis=0)
    ta, tb, tc = share(ca), share(cb), share(cc)
    res.append((valid.sum(), np.median(ta), ta.mean(), np.median(tb), tb.mean(), np.median(tc), tc.mean(), np.median(nskip), np.mean(nskip), np.median(rl)))
for k, (n, a1, a2, b1, b2, c1, c2, s1, s2, rlm) in enumerate(res):
    print(f'{D.split("/")[-1]} slot {k}: {n} rim windows (run >= 4, colour contrast); occluder share: app window median {a1:.2f} mean {a2:.2f} | run median {b1:.2f} mean {b2:.2f} | run median after skipping blends {c1:.2f} mean {c2:.2f} (texels skipped median {s1:.0f} mean {s2:.2f}; run length median {rlm:.0f})')
