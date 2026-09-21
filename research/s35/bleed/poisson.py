"""S45 / Sprint 25: is the GRADIENT contract actually better than the ABSOLUTE contract? Measured before building it.

R7 recommends, from InpaintFusion, that the inpainting stage return the depth GRADIENT rather than the depth, and that we
recover the depth by Poisson integration with the observed depth as the Dirichlet boundary condition. The claimed benefits
are that the seam becomes exact by construction, the representation is scale-free, and the solve is a sparse Laplacian on a
thin band. All three are properties of the formulation. What the literature does NOT tell us is whether it is better ON OUR
DATA once the returned values are WRONG, which they will be -- a model's gradients carry error just as its depths do.

So: take the kit truth as the thing a perfect model would return, corrupt it, and compare the two contracts under the same
corruption.

  absolute   the model returns d on the band. Three arms, so the rival is tested at its strongest: as given; after a GLOBAL
             shift pinning its mean to the observed depth at the band rim; and after a PER-COMPONENT shift pinning each band
             component separately, which is the best an absolute contract can do without changing its form.
  gradient   the model returns (dd/dx, dd/dy) on the band. We solve grad^2 d = div(g) inside each band component with
             d = observed on its visible rim, by Gauss-Seidel with SOR.

Two corruptions, because they are the two ways a predictor is wrong and they hurt the two contracts differently:
  noise      independent per texel: hurts the gradient arm more (it integrates) -- the pessimistic case for R7's advice
  bias       a constant offset over the band: hurts the absolute arm and is INVISIBLE to the gradient arm, since a constant
             added to d has zero gradient. This is the scale error PatchRefiner found IS the synthetic-to-real gap.

  poisson.py [--scenes L1,L5,L6,L7,L8,L9] [--iters 4000]
"""
import sys, os, json, argparse
import numpy as np
from scipy import ndimage
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit')
from tk import app_norm_depth, depth_scores

ap = argparse.ArgumentParser()
ap.add_argument('--scenes', default='L1,L5,L6,L7,L8,L9')
ap.add_argument('--iters', type=int, default=4000)
A = ap.parse_args()
K = '/home/user/moebiusv2/harness/truthkit/out'; P0 = '/home/user/moebiusv2/harness/shots/a257probe'
PROBE = {'L1': 'L1_16plane', 'L5': 'L5_16plane', 'L6': 'L6_16plane', 'L7': 'L7_16plane', 'L8': 'L8_16plane', 'L9': 'L9_16plane'}


def poisson_band(gx, gy, band, bc, iters=4000, omega=1.9, anchor=None, lam=0.0):
    """Solve the discrete Poisson equation on `band` with Dirichlet data `bc` on its rim.
    gx[i] approximates d[x+1] - d[x] at i, gy[i] approximates d[y+1] - d[y]. The divergence at an interior texel is
    (gx[x] - gx[x-1]) + (gy[y] - gy[y-1]); the update is the mean of the four neighbours minus that divergence, over 4.
    Gauss-Seidel with successive over-relaxation, red-black so the sweeps are vectorised.

    With `anchor` and lam > 0 this becomes a SCREENED Poisson solve: minimise ||grad d - g||^2 + lam*||d - anchor||^2 over
    the band, still with d = bc on the rim. lam = 0 is the pure gradient contract, lam -> infinity is the absolute one. The
    measurement below is what motivated it: on our bands the pure gradient form wins the seam and loses the interior, which
    is the textbook signature of a problem that wants both terms."""
    ph, pw = band.shape
    d = np.where(band, np.nan, bc)
    # seed the interior with the mean of the boundary data it will be pinned to, so the solve starts in range
    seed = np.nanmean(bc[~band]) if (~band).any() else 0.0
    d = np.where(band, seed, bc).astype(np.float64)
    div = np.zeros((ph, pw))
    div[:, 1:] += gx[:, 1:] - gx[:, :-1]
    div[1:, :] += gy[1:, :] - gy[:-1, :]
    yy, xx = np.mgrid[0:ph, 0:pw]
    red = ((xx + yy) % 2 == 0) & band
    blk = ((xx + yy) % 2 == 1) & band
    for _ in range(iters):
        for m in (red, blk):
            nb = np.zeros((ph, pw))
            nb[:, :-1] += d[:, 1:]; nb[:, 1:] += d[:, :-1]
            nb[:-1, :] += d[1:, :]; nb[1:, :] += d[:-1, :]
            cnt = np.full((ph, pw), 4.0)
            cnt[0, :] -= 1; cnt[-1, :] -= 1; cnt[:, 0] -= 1; cnt[:, -1] -= 1
            nb = nb + np.where(cnt < 4, 0.0, 0.0)          # a frame-edge texel simply has fewer neighbours (Neumann there)
            if lam > 0 and anchor is not None: new = (nb - div + lam * anchor) / (np.maximum(cnt, 1.0) + lam)
            else: new = (nb - div) / np.maximum(cnt, 1.0)
            d[m] = d[m] + omega * (new[m] - d[m])
    return d


rows = []
for S in A.scenes.split(','):
    P = f'{P0}/{PROBE[S]}'
    meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; outer, pn, inner = meta['outer'], meta['pn'], meta['inner']
    band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0
    dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw).astype(np.float64)
    step = float(np.median(np.diff(np.unique(dQ[~band])[:200])))
    z = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = z['cls']; w = z['w_disp']; dep = z['depth']
    H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls = cls[y0:y0+ph, x0:x0+pw]; w = w[y0:y0+ph, x0:x0+pw]; dep = dep[y0:y0+ph, x0:x0+pw]
    v_ = (cls >= 2) & (cls <= 5) & (w > 0); has = v_.any(-1); kk = np.argmax(v_, -1)
    dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; dT = np.where(has & np.isfinite(dT), dT, np.nan)
    dTn = np.where(np.isfinite(dT), app_norm_depth(-dT, pn, outer, inner), np.nan)
    ok = band & np.isfinite(dTn)
    # the field a perfect model would describe: the truth on the band, the observed depth outside it
    truth = np.where(band, np.where(np.isfinite(dTn), dTn, dQ), dQ)

    # how many band components can be pinned at all? A component with no visible rim has no Dirichlet data and the solve is
    # determined only up to a constant -- the one structural risk in the gradient contract, so it is counted, not assumed.
    lab, nC = ndimage.label(band)
    rim_ok = 0; rim_no = 0; px_no = 0
    for c in range(1, nC + 1):
        m = lab == c
        if (ndimage.binary_dilation(m) & ~m & ~band).any(): rim_ok += 1
        else: rim_no += 1; px_no += int(m.sum())

    r = {'scene': S, 'band': int(band.sum()), 'nComp': nC, 'pinned': rim_ok, 'unpinned': rim_no, 'unpinnedPx': px_no, 'step': step}
    rng = np.random.RandomState(0)
    rimband = ndimage.binary_dilation(band) & ~band
    # Corruption levels in the app's own d, so they are comparable with S43: the learned model's measured error on the
    # hidden-thing class is 0.035-0.096 d, so 0.04 is "a good model" and 0.01 is "a very good one".
    for tag, noise, bias in (('exact', 0.0, 0.0), ('noise 0.01 d', 0.01, 0.0), ('noise 0.04 d', 0.04, 0.0),
                             ('bias 0.02 d', 0.0, 0.02), ('bias 0.05 d', 0.0, 0.05), ('noise 0.04 + bias 0.02', 0.04, 0.02)):
        # what the model returns, under this corruption
        absolute = truth + bias + noise * rng.randn(ph, pw)
        gx = np.zeros((ph, pw)); gy = np.zeros((ph, pw))
        gx[:, :-1] = truth[:, 1:] - truth[:, :-1]
        gy[:-1, :] = truth[1:, :] - truth[:-1, :]
        # a gradient carries the same per-texel noise, but a DIFFERENCE of two noisy samples has sqrt(2) times the noise of
        # one, so the gradient arm is handed the harder version of the same corruption rather than an easier one
        if noise: gx = gx + noise * np.sqrt(2) * rng.randn(ph, pw); gy = gy + noise * np.sqrt(2) * rng.randn(ph, pw)
        # bias is invisible to a gradient by construction -- that is the point of the arm, so nothing is added here
        rec = poisson_band(gx, gy, band, dQ, iters=A.iters)
        recS = {L: poisson_band(gx, gy, band, dQ, iters=A.iters, anchor=absolute, lam=L) for L in (0.25, 1.0, 4.0)}
        # the absolute arm at its strongest: a global shift, and a per-component shift
        shift = float(np.nanmean(dQ[rimband]) - np.nanmean(absolute[rimband])) if rimband.any() else 0.0
        absolute_s = absolute + shift
        absolute_c = absolute.copy()
        for c in range(1, nC + 1):
            m = lab == c; rm = ndimage.binary_dilation(m) & ~m & ~band
            if not rm.any(): continue
            absolute_c[m] += float(np.nanmean(dQ[rm]) - np.nanmean(absolute[rm]))
        e = lambda f: float(np.nanmedian(np.abs(f - dTn)[ok]))
        # THE SEAM. The first version of this measured |f - nearest observed depth| at the rim, which is the REAL geometric
        # step across a silhouette, not a defect -- it read 0.00 for exact data and that caught the error. What a viewer
        # reads as a crease is the reconstruction being wrong exactly where it meets the visible surface, so the seam is the
        # band error RESTRICTED TO THE RIM: |f - truth| at band texels touching a visible one. Poisson is anchored there by
        # its boundary condition; an absolute return is anchored nowhere.
        edge = band & ndimage.binary_dilation(~band) & ok
        seam = lambda f: (float(np.nanmedian(np.abs(f - dTn)[edge])) if edge.any() else float('nan'))
        r[tag] = {'abs': e(absolute), 'absShift': e(absolute_s), 'absComp': e(absolute_c), 'poisson': e(rec),
                  'seamAbs': seam(absolute), 'seamShift': seam(absolute_s), 'seamComp': seam(absolute_c), 'seamPoisson': seam(rec)}
        for L, f in recS.items(): r[tag]['scr%.2f' % L] = e(f); r[tag]['seamScr%.2f' % L] = seam(f)
        # THE CANDIDATE CONTRACT: the screened solve anchored on the PER-COMPONENT SHIFTED absolute return. The screening
        # buys noise rejection (two noisy measurements of one field beat either alone); the per-component shift buys bias
        # immunity, which screening on the raw return does not. lam = 1 weights a value residual equally with a gradient
        # residual, which is the natural choice and, per the 0.25/1/4 sweep, sits on a flat optimum rather than a tuned one.
        both = poisson_band(gx, gy, band, dQ, iters=A.iters, anchor=absolute_c, lam=1.0)
        r[tag]['both'] = e(both); r[tag]['seamBoth'] = seam(both)
    rows.append(r)

print('Band components that can be pinned (a component with no visible rim is determined only up to a constant):')
for r in rows:
    print(f"  {r['scene']:4s} {r['nComp']:5d} components, {r['pinned']:5d} pinned, {r['unpinned']:4d} unpinned "
          f"({r['unpinnedPx']} texels, {100*r['unpinnedPx']/max(1,r['band']):.3f}% of the band)")
print()
hdr = (f"{'scene':5s} {'corruption':22s} | {'abs':>8s} {'+perComp':>8s} {'poisson':>8s} {'scr 1':>8s} {'BOTH':>8s} | "
       f"{'s abs':>8s} {'s +pc':>8s} {'s pois':>8s} {'s BOTH':>8s}")
print(hdr); print('-' * len(hdr))
TAGS = ('exact', 'noise 0.01 d', 'noise 0.04 d', 'bias 0.02 d', 'bias 0.05 d', 'noise 0.04 + bias 0.02')
for r in rows:
    for tag in TAGS:
        v = r[tag]
        print(f"{r['scene']:5s} {tag:22s} | {v['abs']:8.5f} {v['absComp']:8.5f} {v['poisson']:8.5f} "
              f"{v['scr1.00']:8.5f} {v['both']:8.5f} | "
              f"{v['seamAbs']:8.5f} {v['seamComp']:8.5f} {v['seamPoisson']:8.5f} {v['seamBoth']:8.5f}")
    print()
print("all numbers are the median |d - truth| in the app's normalised depth. The first block is over the whole band; the")
print("SEAM block is the same error restricted to band texels that touch a visible one, which is where a viewer reads a")
print("crease. Poisson is anchored there by its Dirichlet boundary; an absolute return is anchored nowhere.")
