"""S38 (Phase D item 1): an ARM-SIDE confidence. S36 gave us a truth-free confidence for the learned model (its disagreement
with the observed depth over the visible region, monotone in its band error). To choose between the arm and the model we need
the same for the arm: an observable that rises with the arm's own error, using no truth and no tuned constant.

Four candidates, all already implied by the construction:
  reach   the texel's distance from its owning sheet's OWN visible patch, over that sheet's own extent E -- how far beyond its
          evidence the sheet is reaching (the ratio the reach law of S35 §30 bounds, here used as a degree rather than a gate)
  lipsp   the spread of the hole's far lips at the texel (max - min over the axes that have one), in steps: how much the data
          around the hole disagrees about what is behind
  sky     the owner is a sky-valued sheet -- the fall-back winner when nothing else reaches
  unowned no sheet owns the texel (it holds the occluder's depth by construction, S35 §47)

Each is scored the way S36 scored the model's: bin the band texels by the signal and report the arm's true error per bin. A
signal is useful only if the error rises monotonically with it, and useful for CHOOSING only if the crossing against the
model's error happens at the same place in every scene.

  armconf.py <scene> <probe dir> <arm dir> [--model amodal_frame.npy]
"""
import sys, os, json, argparse
import numpy as np
from PIL import Image
from scipy import ndimage

ap = argparse.ArgumentParser(); ap.add_argument('scene'); ap.add_argument('probe'); ap.add_argument('arm')
ap.add_argument('--model', default=None); A = ap.parse_args()
K = '/home/user/moebiusv2/harness/truthkit/out'; S = A.scene; P = A.probe; D = A.arm
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; outer, pn = meta['outer'], meta['pn']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; vis = ~band
dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw)
ff = np.fromfile(f'{D}/farField_stop.f32', np.float32).reshape(ph, pw)
who = np.fromfile(f'{D}/who_stop.i32', np.int32).reshape(ph, pw)
comp = np.fromfile(f'{D}/comp.i32', np.int32).reshape(ph, pw)
z = np.load(f'{D}/sheets_info.npz'); E = z['E']; sky = z['sky']; compOf = z['comp']
step = float(np.median(np.diff(np.unique(dQ[vis])[:200]))) if vis.any() else 1e-3
# truth
zt = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = zt['cls']; w = zt['w_disp']; dep = zt['depth']
H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
cls = cls[y0:y0 + ph, x0:x0 + pw]; w = w[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]
v_ = (cls >= 2) & (cls <= 5) & (w > 0); has = v_.any(-1); kk = np.argmax(v_, -1)
dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; dT = np.where(has & np.isfinite(dT), dT, np.nan)
d_of = lambda d: outer * (1 - np.clip(d / pn, 0, 1) ** 2 * (3 - 2 * np.clip(d / pn, 0, 1)))
eArm = np.abs(d_of(ff) - dT)
t = band & np.isfinite(dT)
eMod = None
if A.model and os.path.exists(f'{P}/{A.model}'):
    eMod = np.abs(d_of(np.load(f'{P}/{A.model}').astype(np.float64)) - dT)

# --- signal 1: reach, the distance from the owning sheet's own visible patch over that sheet's extent
nS = len(E); reach = np.full((ph, pw), np.nan)
owners = np.unique(who[band & (who >= 0)])
for s in owners:
    s = int(s)
    if s >= nS: continue
    own = (comp == compOf[s]) & vis
    if not own.any(): continue
    m = band & (who == s)
    dist = ndimage.distance_transform_edt(~own)
    reach[m] = dist[m] / max(1.0, float(E[s]))
# --- signal 2: the spread of the far lips
yy, xx = np.mgrid[0:ph, 0:pw]
def lip(axis, rev):
    a = np.where(vis, xx if axis == 1 else yy, -1)
    if rev: a = a[:, ::-1] if axis == 1 else a[::-1]
    a = np.maximum.accumulate(a, axis=axis)
    if rev: a = a[:, ::-1] if axis == 1 else a[::-1]; a = np.where(a < 0, -1, (pw - 1 - a) if axis == 1 else (ph - 1 - a))
    return np.where(a >= 0, dQ[yy, np.clip(a, 0, pw - 1)] if axis == 1 else dQ[np.clip(a, 0, ph - 1), xx], np.nan)
L = np.stack([lip(1, False), lip(1, True), lip(0, False), lip(0, True)], -1)
L = np.where(np.isfinite(L) & (L < dQ[..., None] - 2 * step), L, np.nan)
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    lipsp = (np.nanmax(L, -1) - np.nanmin(L, -1)) / max(step, 1e-9)
# --- signals 3, 4
skyOwn = band & (who >= 0) & np.r_[sky, False][np.clip(who, 0, nS)]
unowned = band & (who < 0)

print(f'{S} / {D.rstrip("/").split("/")[-1]}: band {int(band.sum())}, with truth {int(t.sum())}; arm |e| median {np.nanmedian(eArm[t]):.4f} m'
      + (f"; model |e| median {np.nanmedian(eMod[t]):.4f} m" if eMod is not None else ""))
for nm, sig in (('reach  (dist / own extent)', reach), ('lipsp  (lip spread, steps)', lipsp)):
    v = sig[t]; ok = np.isfinite(v)
    if ok.sum() < 1000: print(f'   {nm}: too few finite values'); continue
    q = np.nanpercentile(v[ok], [20, 40, 60, 80]); prev = -np.inf; print(f'   {nm}:')
    for hi in list(q) + [np.inf]:
        m = t & (sig > prev) & (sig <= hi)
        if m.sum() < 200: prev = hi; continue
        row = f'      <= {hi if np.isfinite(hi) else 9999:8.2f}: n {int(m.sum()):6d}  arm |e| {np.nanmedian(eArm[m]):.4f}'
        if eMod is not None: row += f'  model |e| {np.nanmedian(eMod[m]):.4f}  {"MODEL" if np.nanmedian(eMod[m]) < np.nanmedian(eArm[m]) else "arm"}'
        print(row); prev = hi
for nm, m in (('owner is sky', t & skyOwn), ('owner is not sky', t & ~skyOwn & (who >= 0)), ('unowned', t & unowned)):
    if m.sum() < 200: continue
    row = f'   {nm:18s}: n {int(m.sum()):6d}  arm |e| {np.nanmedian(eArm[m]):.4f}'
    if eMod is not None: row += f'  model |e| {np.nanmedian(eMod[m]):.4f}  {"MODEL" if np.nanmedian(eMod[m]) < np.nanmedian(eArm[m]) else "arm"}'
    print(row)
