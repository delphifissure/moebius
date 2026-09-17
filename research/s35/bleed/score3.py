"""S35 §23 step 1, three arms. Usage: score3.py <name> <color.png> <tag=dir> ...
Per band texel with a single far rim, from its OWN run:
  o = the occluder's edge colour seen from the run (one step before the rim, toward the gap)
  b = a NEUTRAL local clean reference: the median of the run over 8 texels starting past the blend skip
      (local, so it does not favour the run median; clean, so it does not favour the fit window)
  share t = ((fill-b).(o-b))/|o-b|^2 : 0 = the far surface's own colour, 1 = the occluder's.
Reported by the gap g (the fit window is g+1).
SEAM: at the band's outer edge (a band texel whose 4-neighbour is a non-band texel BEHIND it: the visible far surface the
fill continues), |fill - that neighbour's source colour|. This is the seam the viewer sees where the wash meets the picture.
STREAK: |dC| of the fill between neighbouring texels ACROSS the lines (independent per-line reads)."""
import sys, json, numpy as np
from PIL import Image
NAME, C = sys.argv[1], sys.argv[2]
arms = [a.split('=', 1) for a in sys.argv[3:]]
D0 = arms[0][1]
meta = json.load(open(f'{D0}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{D0}/dQ.f32', np.float32); dis = np.fromfile(f'{D0}/disocc.u8', np.uint8) > 0
J = np.fromfile(f'{D0}/farRimJ.i32', np.int32).reshape(N, 2); W = np.fromfile(f'{D0}/farRimW.i32', np.int32).reshape(N, 2)
L = np.fromfile(f'{D0}/farRimL.i32', np.int32).reshape(N, 2); ax = np.fromfile(f'{D0}/farAxis.u8', np.uint8); mix = np.fromfile(f'{D0}/farMix.f32', np.float32)
car = np.fromfile(f'{D0}/carrier.u8', np.uint8) > 0; plateF = np.fromfile(f'{D0}/plateF.f32', np.float32).reshape(ph, pw)[::-1].ravel()
q = float(meta.get('quantum') or meta.get('step') or 1 / 255)
im = Image.open(C).convert('RGB'); col = np.asarray(im if im.size == (pw, ph) else im.resize((pw, ph), Image.BILINEAR)).astype(np.float32).reshape(N, 3)
pc = {t: np.fromfile(f'{d}/plateColor.u8', np.uint8).reshape(N, 4)[:, :3].astype(np.float32) for t, d in arms}
dom = (car | dis) & (ax > 0) & ((J[:, 0] >= 0) | (J[:, 1] >= 0)) & (plateF < dQ - q)
rows = {}
for slot, side in ((0, -1), (1, +1)):
    sel = dom & (J[:, slot] >= 0) & ((mix >= 0.999) if slot == 0 else (mix <= 0.001))
    idxs = np.flatnonzero(sel)
    if not len(idxs): continue
    rng = np.random.RandomState(0); sub = idxs if len(idxs) <= 25000 else idxs[rng.choice(len(idxs), 25000, replace=False)]
    for i in sub:
        jj = int(J[i, slot]); aa = int(ax[i]); ln = int(L[i, slot]); st = 1 if aa == 1 else pw
        jx = jj % pw; jy = jj // pw; ix_ = i % pw; iy_ = i // pw
        lim = (pw - jx if side > 0 else jx + 1) if aa == 1 else (ph - jy if side > 0 else jy + 1)
        n = max(1, min(ln, lim))
        if n < 2: continue
        if not ((jx - side >= 0 and jx - side < pw) if aa == 1 else (jy - side >= 0 and jy - side < ph)): continue
        run = col[jj + side * np.arange(n) * st]; med = np.median(run, 0)
        o = col[jj - side * st]; dev = np.abs(run - med).sum(1); spread = np.median(dev) * 1.4826 + 1e-6; k0 = 0
        while k0 < n - 1:
            d_ = run[k0] - med
            if d_ @ (o - med) > 0 and np.abs(d_).sum() > spread: k0 += 1
            else: break
        b = np.median(run[k0:min(n, k0 + 8)], 0)
        den = ((o - b) ** 2).sum()
        if den < 24 ** 2: continue
        g = abs((ix_ - jx) if aa == 1 else (iy_ - jy))
        key = 'g<=3' if g <= 3 else ('g 4..10' if g <= 10 else ('g 11..40' if g <= 40 else 'g>40'))
        r = rows.setdefault(key, {'n': 0, **{t: [] for t, _ in arms}}); r['n'] += 1
        for t, _ in arms: r[t].append(float(np.clip(((pc[t][i] - b) @ (o - b)) / den, -1, 2)))
print(f'== {NAME}: band {int(dis.sum())}, domain {int(dom.sum())}   arms: ' + ', '.join(t for t, _ in arms))
print('   occluder share of the fill (0 = the far surface, 1 = the occluder), median (mean):')
for key in ('g<=3', 'g 4..10', 'g 11..40', 'g>40'):
    if key not in rows: continue
    r = rows[key]; cells = []
    for t, _ in arms:
        a = np.array(r[t]); cells.append(f'{t} {np.median(a):+.2f} ({a.mean():+.2f})')
    print(f'      {key:9s} ({r["n"]:6d}): ' + ' | '.join(cells))
# seam at the band's outer edge
dm = dis.reshape(ph, pw); dq2 = dQ.reshape(ph, pw); c2 = col.reshape(ph, pw, 3)
seam = {t: [] for t, _ in arms}
for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
    nb = np.roll(np.roll(dm, -dy, 0), -dx, 1); nd = np.roll(np.roll(dq2, -dy, 0), -dx, 1); nc = np.roll(np.roll(c2, -dy, 0), -dx, 1)
    m = dm & ~nb & (nd < dq2 - q)          # the neighbour is BEHIND: the visible far surface
    if dy: m[0 if dy < 0 else -1, :] = False
    if dx: m[:, 0 if dx < 0 else -1] = False
    if not m.any(): continue
    for t, _ in arms: seam[t].append(np.linalg.norm(pc[t].reshape(ph, pw, 3)[m] - nc[m], axis=1))
if seam[arms[0][0]]:
    print('   seam where the fill meets the visible far surface, |dC|:')
    for t, _ in arms:
        d_ = np.concatenate(seam[t]); print(f'      {t:8s} ({len(d_):6d} pairs): median {np.median(d_):.1f} mean {d_.mean():.1f} p90 {np.percentile(d_, 90):.1f}')
axm = ax.reshape(ph, pw)
print('   streaks across the lines, |dC|:')
for t, _ in arms:
    p3 = pc[t].reshape(ph, pw, 3)
    mV = dm[1:, :] & dm[:-1, :] & (axm[1:, :] == 1) & (axm[:-1, :] == 1); dV = np.linalg.norm(p3[1:, :] - p3[:-1, :], axis=2)[mV]
    mH = dm[:, 1:] & dm[:, :-1] & (axm[:, 1:] == 2) & (axm[:, :-1] == 2); dH = np.linalg.norm(p3[:, 1:] - p3[:, :-1], axis=2)[mH]
    d_ = np.concatenate([dV, dH]); print(f'      {t:8s} ({len(d_):6d} pairs): median {np.median(d_):.2f} mean {d_.mean():.2f} p90 {np.percentile(d_, 90):.2f}')
