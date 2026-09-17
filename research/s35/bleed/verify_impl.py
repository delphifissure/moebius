"""Does the app's new fill equal the offline law? Ring texels are Dirichlet, so a ring texel with a SINGLE rim (mix 0 or 1)
carries exactly that rim's colour. Recompute both laws offline for those texels and compare. Also the run-length distribution."""
import sys, json, numpy as np
from PIL import Image
BEF, AFT, C = sys.argv[1], sys.argv[2], sys.argv[3]
meta = json.load(open(f'{AFT}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{AFT}/dQ.f32', np.float32); dis = np.fromfile(f'{AFT}/disocc.u8', np.uint8) > 0
J = np.fromfile(f'{AFT}/farRimJ.i32', np.int32).reshape(N, 2); W = np.fromfile(f'{AFT}/farRimW.i32', np.int32).reshape(N, 2)
L = np.fromfile(f'{AFT}/farRimL.i32', np.int32).reshape(N, 2); ax = np.fromfile(f'{AFT}/farAxis.u8', np.uint8); mix = np.fromfile(f'{AFT}/farMix.f32', np.float32)
car = np.fromfile(f'{AFT}/carrier.u8', np.uint8) > 0
col = np.asarray(Image.open(C).convert('RGB').resize((pw, ph), Image.BILINEAR)).astype(np.float32).reshape(N, 3)
pcA = np.fromfile(f'{AFT}/plateColor.u8', np.uint8).reshape(N, 4)[:, :3].astype(np.float32)
pcB = np.fromfile(f'{BEF}/plateColor.u8', np.uint8).reshape(N, 4)[:, :3].astype(np.float32)
have = dis & (ax > 0) & ((J[:, 0] >= 0) | (J[:, 1] >= 0))
plateF = np.fromfile(f'{AFT}/plateF.f32', np.float32).reshape(ph, pw)[::-1].ravel()
q = float(meta.get('quantum') or meta.get('step') or 1/255)
dom = (car | dis) & have & (plateF < dQ - q)
dom2 = dom.reshape(ph, pw); ring = dom2.copy()
inner = np.ones_like(dom2); inner[1:-1,1:-1] = dom2[:-2,1:-1] & dom2[2:,1:-1] & dom2[1:-1,:-2] & dom2[1:-1,2:]
ring = (dom2 & ~inner).ravel()
print('domain', int(dom.sum()), 'ring', int(ring.sum()))
have = have & ring
single0 = have & (J[:, 0] >= 0) & ((J[:, 1] < 0) | (mix >= 1.0)); single1 = have & (J[:, 1] >= 0) & ((J[:, 0] < 0) | (mix <= 0.0))
print(f'band {int(dis.sum())}; with a rim {int(have.sum())}; single-rim slot0 {int(single0.sum())} slot1 {int(single1.sum())}')
for slot, side, sel in ((0, -1, single0), (1, +1, single1)):
    idxs = np.flatnonzero(sel)
    if len(idxs) == 0: continue
    j = J[idxs, slot]; ln = L[idxs, slot]; w = W[idxs, slot]; a = ax[idxs]
    print(f'  slot {slot}: run length p10 {np.percentile(ln,10):.0f} median {np.median(ln):.0f} p90 {np.percentile(ln,90):.0f}; fit window w median {np.median(w):.0f}; runs < 4 texels: {100*(ln<4).mean():.1f} %')
    # recompute both laws for a sample
    rng = np.random.RandomState(0); sub = rng.choice(len(idxs), min(4000, len(idxs)), replace=False)
    okA = []; okB = []
    for n in sub:
        jj = int(j[n]); aa = int(a[n]); st = 1 if aa == 1 else pw; jx = jj % pw; jy = jj // pw
        lim = (pw - jx if side > 0 else jx + 1) if aa == 1 else (ph - jy if side > 0 else jy + 1)
        nR = max(1, min(int(ln[n]), lim)); nW = max(1, min(int(w[n]), lim))
        run = col[jj + side * np.arange(nR) * st]
        med = np.median(run, 0); k0 = 0
        if nR > 1 and ((jx - side >= 0 and jx - side < pw) if aa == 1 else (jy - side >= 0 and jy - side < ph)):
            o = col[jj - side * st] - med; dev = np.abs(run - med).sum(1); spread = np.median(dev) * 1.4826 + 1e-6
            while k0 < nR - 1:
                d = run[k0] - med
                if d @ o > 0 and np.abs(d).sum() > spread: k0 += 1
                else: break
            if k0 > 0: med = np.median(run[k0:], 0)
        okA.append(np.abs(pcA[idxs[n]] - med).max()); okB.append(np.abs(pcB[idxs[n]] - run[:nW].mean(0)).max())
    okA = np.array(okA); okB = np.array(okB)
    print(f'     AFTER  fill vs offline run-median+skip: |max channel diff| median {np.median(okA):.2f}, <= 1 on {100*(okA<=1).mean():.1f} %, <= 2 on {100*(okA<=2).mean():.1f} %')
    print(f'     BEFORE fill vs offline fit-window mean: |max channel diff| median {np.median(okB):.2f}, <= 1 on {100*(okB<=1).mean():.1f} %')
