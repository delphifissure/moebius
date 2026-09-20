"""S35 §55: RIMS THAT ARE BAND TEXELS. A far rim is the first texel of a run behind the band texel along its line (rule 1), and
the construction allows that texel to be in the band itself -- the comment at the scan says "the reveal set holds one texel of
the background at the silhouette", meaning the first background texel past a silhouette, which the app's band marks as band
though it carries background depth. This instrument asks how far that goes: per rim, is it visible or band; if band, how far
from the nearest visible texel, and is its depth the OCCLUDER's (a stretched plate texel: a clone founding a sheet) or a real
far value. Then per sheet: the share of its rims that are band, and what its all-band kind owns in the band -- with --truth S,
the kit's median |error| on the texels those sheets own against the rest.
  bandrims.py <probe dir> <arm dir> <step> [--truth S]"""
import sys, json, numpy as np
from scipy import ndimage
args = sys.argv[1:]; P = args.pop(0); D = args.pop(0); step = float(args.pop(0)); S = None
if args and args[0] == '--truth': args.pop(0); S = args.pop(0)
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw); vis = ~band
z = np.load(f'{D}/sheets_info.npz'); rimIdx = z['rimIdx']; rimPtr = z['rimPtr']
who = np.fromfile(f'{D}/who_stop.i32', np.int32).reshape(ph, pw); ff = np.fromfile(f'{D}/farField_stop.f32', np.float32).reshape(ph, pw)
ry, rx = rimIdx // pw, rimIdx % pw; isB = band[ry, rx]
# the occluder's depth for a band texel = its own dQ (the stretched plate); distance to real data
dist = ndimage.distance_transform_edt(band)
print(f'{P.split("/")[-1]} / {D.rstrip("/").split("/")[-1]}: {len(rimIdx)} rim slots, {100 * isB.mean():.1f} % of them BAND texels')
if isB.any():
    db = dist[ry[isB], rx[isB]]
    print(f'   band rims: distance to the nearest visible texel p50 {np.median(db):.0f}, p90 {np.percentile(db, 90):.0f}, max {db.max():.0f}; more than 1 texel in: {100 * (db > 1).mean():.0f} %, more than 5: {100 * (db > 5).mean():.0f} %')
nS = len(rimPtr) - 1
shB = np.array([isB[rimPtr[s]:rimPtr[s + 1]].mean() if rimPtr[s + 1] > rimPtr[s] else 0.0 for s in range(nS)])
allB = np.r_[shB >= 1.0, False]   # the pseudo-sheet has no rims and is not an all-band sheet
own = np.zeros(nS + 1, np.int64); w = who[band]   # who == nS is the pseudo-sheet past the last surface (the kit's sky from the field)
u, c = np.unique(w[w >= 0], return_counts=True); own[u] = c
print(f'   sheets {nS}: all-band rims {int(allB.sum())} ({100 * allB[:nS].mean():.0f} %), some-band {int(((shB > 0) & ~allB[:nS]).sum())}, none {int((shB == 0).sum())}; band texels owned by all-band sheets {int(own[allB].sum())} ({100 * own[allB].sum() / max(1, own.sum()):.1f} % of owned)')
ownedBy = np.isin(who, np.flatnonzero(allB)) & band
if ownedBy.any():
    print(f'   what all-band sheets own: {int(ownedBy.sum())} texels, fill d p50 {np.median(ff[ownedBy]):.3f}, the occluder there dQ p50 {np.median(dQ[ownedBy]):.3f}, within 3 steps of the occluder (clone) {100 * (np.abs(ff[ownedBy] - dQ[ownedBy]) <= 3 * step).mean():.0f} %')
if S:
    K = '/home/user/moebiusv2/harness/truthkit/out'; outer, pn = meta['outer'], meta['pn']
    zt = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = zt['cls']; wq = zt['w_disp']; dep = zt['depth']; H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls = cls[y0:y0 + ph, x0:x0 + pw]; wq = wq[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]
    v_ = (cls >= 2) & (cls <= 5) & (wq > 0); has = v_.any(-1); kk = np.argmax(v_, -1); dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; dT = np.where(has & np.isfinite(dT), dT, np.nan)
    depth_of_d = lambda d: outer * (1 - np.clip(d / pn, 0, 1) ** 2 * (3 - 2 * np.clip(d / pn, 0, 1)))
    e = np.abs(depth_of_d(ff) - dT); t = band & np.isfinite(dT)
    a = t & ownedBy; b = t & ~ownedBy & (who >= 0)
    print(f'   truth: owned by an all-band sheet {int(a.sum())} texels, median |e| {np.nanmedian(e[a]) if a.any() else np.nan:.4f} m; owned by a sheet with a visible rim {int(b.sum())}, {np.nanmedian(e[b]) if b.any() else np.nan:.4f} m; whole band {np.nanmedian(e[t]):.4f} m')
