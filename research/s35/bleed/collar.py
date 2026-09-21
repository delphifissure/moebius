"""R7 item 1 / S41: COLLAR statistics as the gate we could not find.

Counterfactual Depth (Issaranon, Zou, Forsyth 2019) is the only paper whose target is ours -- the depth of the surface behind a
mask, not the completed shape of an object -- and the only one that asked WHEN a geometric continuation fails. Their factorial
design predicts a LEARNED model's error from scene attributes at adjusted R^2 0.882 and a Poisson-smoothing baseline's at only
0.632, with the explanation that for the geometric rule "more important is the pool of depths around the object", and they name
the failure outright: smoothing "fails in the obvious way when one side of the background is closer than the other".

Everything this project falsified as a gate (§57 the contested population, S36 the model's visible-region disagreement, S38 the
crossing, S39 sky share / component count / unowned share) is SCENE-level or MODEL-level. None is a collar statistic. But S38's
`lipsp` and `reach` ARE collar statistics and both were monotone in the arm's error -- we set them aside because the crossing
against the model moved between scenes, which is a different question from the gate, and we never aggregated either to a scene.

Statistics, all computed from the OBSERVED depth alone -- no truth, no tuned constant, every length in visible steps:
  oppX/oppY  the disagreement between the far lips on OPPOSITE sides of the hole, per axis. This is the named failure. S38's
             lipsp took max-min over all four directions at once, which conflates the axes and does not isolate opposition.
  opp        max(oppX, oppY) -- the worst opposition at the texel.
  gap        per band component: the largest gap in the sorted far-collar depths over that collar's range. A collar that splits
             into two clusters is the case the rule cannot resolve.
  plres      per band component: the median absolute residual of a least-squares plane fit to the far collar, in steps.
  lipsp      S38's spread, kept as a control.
  reach      S38's reach ratio, kept as a control (needs sheets_info + comp).

The bar is the ARM's OWN ERROR, not which source wins -- the winner label is unstable between S39's best-mask arm and S40's
grey/occluder arm, and a moving target cannot falsify anything. The model's error is nearly flat (0.039-0.096 on the thing class
under grey+occ), so a statistic that predicts the arm's error IS the gate. Two tests: per texel, bin and require monotone (the
S38 protocol, real power); per scene, rank against the arm's error (six scenes, a perfect order is ~1/360 by luck).

  collar.py <scene> <probe dir> <arm dir> [--json out.json]
"""
import sys, os, json, argparse, warnings
import numpy as np
from scipy import ndimage

ap = argparse.ArgumentParser(); ap.add_argument('scene'); ap.add_argument('probe'); ap.add_argument('arm')
ap.add_argument('--json', default=None); A = ap.parse_args()
K = '/home/user/moebiusv2/harness/truthkit/out'; S = A.scene; P = A.probe; D = A.arm
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; outer, pn = meta['outer'], meta['pn']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; vis = ~band
dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw).astype(np.float64)
ff = np.fromfile(f'{D}/farField_stop.f32', np.float32).reshape(ph, pw).astype(np.float64)
step = float(np.median(np.diff(np.unique(dQ[vis])[:200]))) if vis.any() else 1e-3

# --- truth, and the two error scales (R7 item 2: the metre score's gain varies 20x across the kit; d is gain-free)
zt = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = zt['cls']; w = zt['w_disp']; dep = zt['depth']
H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
cls = cls[y0:y0 + ph, x0:x0 + pw]; w = w[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]
v_ = (cls >= 2) & (cls <= 5) & (w > 0); has = v_.any(-1); kk = np.argmax(v_, -1)
dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; dT = np.where(has & np.isfinite(dT), dT, np.nan)
cT = np.take_along_axis(cls, kk[..., None], -1)[..., 0]
sm = lambda s: s ** 2 * (3 - 2 * s)
depth_of_d = lambda d: outer * (1 - sm(np.clip(d / pn, 0, 1)))
_g = np.linspace(0, pn, 4096); _m = depth_of_d(_g)          # monotone decreasing on [0, pn]
d_of_depth = lambda m: np.interp(np.clip(m, _m[-1], _m[0]), _m[::-1], _g[::-1])
dTd = np.where(np.isfinite(dT), d_of_depth(dT), np.nan)     # truth expressed in the app's own d
eM = np.abs(depth_of_d(ff) - dT)                            # arm error, metres
eD = np.abs(ff - dTd)                                       # arm error, d units
t = band & np.isfinite(dT)

# --- far lips along each axis: the nearest visible texel, kept only when it is FARTHER than the occluder (smaller d)
yy, xx = np.mgrid[0:ph, 0:pw]
def lip(axis, rev):
    a = np.where(vis, xx if axis == 1 else yy, -1)
    if rev: a = a[:, ::-1] if axis == 1 else a[::-1]
    a = np.maximum.accumulate(a, axis=axis)
    if rev:
        a = a[:, ::-1] if axis == 1 else a[::-1]
        a = np.where(a < 0, -1, (pw - 1 - a) if axis == 1 else (ph - 1 - a))
    return np.where(a >= 0, dQ[yy, np.clip(a, 0, pw - 1)] if axis == 1 else dQ[np.clip(a, 0, ph - 1), xx], np.nan)
raw = np.stack([lip(1, False), lip(1, True), lip(0, False), lip(0, True)], -1)
far = np.where(np.isfinite(raw) & (raw < dQ[..., None] - 2 * step), raw, np.nan)
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    oppX = np.abs(far[..., 0] - far[..., 1]) / step          # left lip vs right lip: the named failure, per axis
    oppY = np.abs(far[..., 2] - far[..., 3]) / step
    opp = np.fmax(oppX, oppY)
    lipsp = (np.nanmax(far, -1) - np.nanmin(far, -1)) / step  # S38's control

# --- per-component collar statistics.
# The collar is the component's OWN VISIBLE RIM -- the texels immediately outside it. That is parameter-free and it is
# literally the lip. (A first attempt used the band's own half-width as the dilation, as §47 and S38 do for a per-texel
# window; on L7 that is 59 texels, which is a neighbourhood and not a collar, and it mixes in surfaces the hole never
# touches.) Only the FAR part of the rim counts: the visible background around the hole, not the occluder's own edge.
lab, nC = ndimage.label(band)
slices = ndimage.find_objects(lab)
gap = np.full((ph, pw), np.nan); plres = np.full((ph, pw), np.nan); nbig = 0; nfit = 0
for c in range(1, nC + 1):
    sl = slices[c - 1]
    if sl is None: continue
    sl = (slice(max(0, sl[0].start - 2), min(ph, sl[0].stop + 2)), slice(max(0, sl[1].start - 2), min(pw, sl[1].stop + 2)))
    m = lab[sl] == c
    if int(m.sum()) < 200: continue
    nbig += 1
    rim = ndimage.binary_dilation(m) & ~m & vis[sl]
    occd = float(np.median(dQ[sl][m]))                                      # the occluder's own plate depth here
    fc = rim & (dQ[sl] < occd - 2 * step)                                   # the FAR part of the rim
    k = int(fc.sum())
    if k < 30: continue
    nfit += 1
    v = np.sort(dQ[sl][fc]); rng = max(v[-1] - v[0], 1e-9)
    gap[sl][m] = float(np.max(np.diff(v)) / rng) if k > 1 else 0.0
    Y, X = np.nonzero(fc)
    Amat = np.stack([X, Y, np.ones_like(X)], 1).astype(np.float64)
    sol, *_ = np.linalg.lstsq(Amat, dQ[sl][fc], rcond=None)
    plres[sl][m] = float(np.median(np.abs(Amat @ sol - dQ[sl][fc])) / step)

# --- S38's reach, as a control
reach = np.full((ph, pw), np.nan)
try:
    who = np.fromfile(f'{D}/who_stop.i32', np.int32).reshape(ph, pw)
    comp = np.fromfile(f'{D}/comp.i32', np.int32).reshape(ph, pw)
    zi = np.load(f'{D}/sheets_info.npz'); E = zi['E']; compOf = zi['comp']; nS = len(E)
    for s in np.unique(who[band & (who >= 0)]):
        s = int(s)
        if s >= nS: continue
        own = (comp == compOf[s]) & vis
        if not own.any(): continue
        mm = band & (who == s)
        reach[mm] = ndimage.distance_transform_edt(~own)[mm] / max(1.0, float(E[s]))
except Exception as e:
    print(f'   (reach unavailable: {e})')

SIG = [('opp', opp), ('oppX', oppX), ('oppY', oppY), ('gap', gap), ('plres', plres), ('lipsp', lipsp), ('reach', reach)]
thing = t & (cT == 3)
print(f'{S} / {D.rstrip("/").split("/")[-1]}: band {int(band.sum())}, with truth {int(t.sum())}, thing {int(thing.sum())}; '
      f'components >=200 texels {nbig}/{nC} (collar fitted on {nfit}); rim collar; step {step:.3e}')
print(f'   arm |e| median  whole band {np.nanmedian(eM[t]):.4f} m / {np.nanmedian(eD[t]):.4f} d'
      + (f'   thing {np.nanmedian(eM[thing]):.4f} m / {np.nanmedian(eD[thing]):.4f} d' if thing.sum() >= 200 else ''))
out = {'scene': S, 'arm': D, 'band': int(band.sum()), 'nComp': nbig, 'nFit': nfit, 'step': step,
       'eM_band': float(np.nanmedian(eM[t])), 'eD_band': float(np.nanmedian(eD[t])),
       'eM_thing': float(np.nanmedian(eM[thing])) if thing.sum() >= 200 else None,
       'eD_thing': float(np.nanmedian(eD[thing])) if thing.sum() >= 200 else None, 'sig': {}}
for nm, sg in SIG:
    v = sg[t]; ok = np.isfinite(v)
    if ok.sum() < 1000:
        print(f'   {nm:6s}: defined on {int(ok.sum())} of {int(t.sum())} band texels -- too few'); continue
    # Edges: quintiles when the signal is continuous; the distinct values when it is a per-component constant (gap, plres) or
    # piles up on a single value (opp is exactly 0 wherever both opposing far lips sit on the same surface, which is the
    # reliable case and is most of the band). Deduplicate, or the tied edges silently empty their bins.
    u = np.unique(v[ok])
    edges = list(u[:-1]) if len(u) <= 12 else sorted(set(np.nanpercentile(v[ok], [20, 40, 60, 80]).tolist()))
    prev = -np.inf; rows = []
    for hi in list(edges) + [np.inf]:
        mm = t & (sg > prev) & (sg <= hi)
        prev = hi
        if mm.sum() < 200: continue
        rows.append((float(np.nanmedian(eM[mm])), float(np.nanmedian(eD[mm])), int(mm.sum())))
    if len(rows) < 3:
        print(f'   {nm:6s}: defined on {int(ok.sum())} texels, {len(u)} distinct values, only {len(rows)} populated bins'); continue
    em = [r[0] for r in rows]
    mono = all(em[i] <= em[i + 1] + 1e-12 for i in range(len(em) - 1))
    # the scene aggregate: the band-weighted median of the signal
    agg = float(np.nanmedian(v[ok])); frac = float(ok.sum()) / float(t.sum())
    # scene-level aggregates: the median is 0 for `opp` in five of six scenes, so the median alone cannot order scenes.
    aggs = {'median': agg, 'mean': float(np.nanmean(v[ok])), 'p75': float(np.nanpercentile(v[ok], 75)),
            'p90': float(np.nanpercentile(v[ok], 90)), 'fracPos': float(np.mean(v[ok] > 1.0)), 'defined': frac}
    print(f'   {nm:6s}: defined {frac:5.1%}  agg {agg:9.3f} | arm |e| by bin ' + ' '.join(f'{e:.4f}' for e in em)
          + f'  ratio {em[-1] / max(em[0], 1e-9):6.1f}x  {"MONOTONE" if mono else "not monotone"}')
    out['sig'][nm] = {**aggs, 'agg': agg, 'eM_bins': em, 'eD_bins': [r[1] for r in rows],
                      'n_bins': [r[2] for r in rows], 'monotone': bool(mono)}
# --- the named failure as a BINARY condition, which is how the paper states it: "one side of the background is closer than
# the other". Quintiles hide this, because `opp` is exactly 0 wherever the two opposing far lips sit on the same surface and
# that is most of the band -- so four of the five quintile edges land on 0 and the bins collapse.
for nm, sg in (('opp', opp), ('oppX', oppX), ('oppY', oppY)):
    ok = t & np.isfinite(sg)
    a = ok & (sg <= 1.0)            # the two opposing far lips agree to within one visible step
    b = ok & (sg > 1.0)
    if a.sum() < 200 or b.sum() < 200:
        print(f'   split {nm:4s}: agree {int(a.sum())} / disagree {int(b.sum())} -- one side too small'); continue
    ea, eb = float(np.nanmedian(eM[a])), float(np.nanmedian(eM[b]))
    da, db = float(np.nanmedian(eD[a])), float(np.nanmedian(eD[b]))
    print(f'   split {nm:4s}: lips AGREE n {int(a.sum()):6d} |e| {ea:.4f} m / {da:.4f} d   '
          f'DISAGREE n {int(b.sum()):6d} |e| {eb:.4f} m / {db:.4f} d   ratio {eb / max(ea, 1e-9):8.1f}x')
    out.setdefault('split', {})[nm] = {'n_agree': int(a.sum()), 'n_dis': int(b.sum()), 'eM_agree': ea, 'eM_dis': eb,
                                       'eD_agree': da, 'eD_dis': db}
if A.json:
    json.dump(out, open(A.json, 'w'), indent=1); print(f'   -> {A.json}')
