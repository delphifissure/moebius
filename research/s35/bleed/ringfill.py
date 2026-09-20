"""S35 §47: the fill read against the DATA beside the hole, one instrument for every picture (and, with --truth, the kit).
trollfill2 / headfill2 were per picture and per occluder, their rings drawn by hand. A first generic form took, per band
texel, the 64 nearest visible texels behind the occluder within 120 texels: on vermeer that ring's median was d 0.345 where
the wall behind the milkmaid is 0.005-0.009 -- the table and the foreground, behind her but not behind the hole, filled the
ring, and 90 % of every arm's fill read as 'beyond'. The ring must be the hole's own far lip. Here it is the LINE lip, as the
band itself is drawn: along the texel's row and its column, the first visible texel in each direction; those BEHIND the
occluder (dQ at a band texel is the occluder's stretched depth; behind = d < dQ - 2 steps) are the texel's far lips, one to
four values; a texel with at least one is scored. A fill is CONTINUATION when it lies in [min lip - step, max lip + step],
BEYOND when deeper, NEARER when nearer; CLONE when within three steps of the occluder's depth (a subset of nearer). Texels whose
lip median is sky (d < 0.02) are reported apart from surface lips, since continuing to the sky is the easy case. With
--truth S the kit's first hidden layer gives the true depth and the median |error| in metres per lip class per arm -- the
calibration of this instrument against the kit.
  ringfill.py <probe dir> <step> [--truth S] <arm dirs...>"""
import sys, json, numpy as np
args = sys.argv[1:]; P = args.pop(0); step = float(args.pop(0)); S = None
if args and args[0] == '--truth': args.pop(0); S = args.pop(0)
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw)
vis = ~band; yy, xx = np.mgrid[0:ph, 0:pw]
def lip(axis, rev):
    a = np.where(vis, xx if axis == 1 else yy, -1)
    if rev: a = a[:, ::-1] if axis == 1 else a[::-1]
    a = np.maximum.accumulate(a, axis=axis)
    if rev: a = a[:, ::-1] if axis == 1 else a[::-1]
    if rev: a = np.where(a < 0, -1, (pw - 1 - a) if axis == 1 else (ph - 1 - a))
    d = np.where(a >= 0, dQ[yy, np.clip(a, 0, pw - 1)] if axis == 1 else dQ[np.clip(a, 0, ph - 1), xx], np.nan)
    return d
lips = np.stack([lip(1, False), lip(1, True), lip(0, False), lip(0, True)], -1)   # left, right, up, down
occ = dQ[..., None]; lips = np.where(np.isfinite(lips) & (lips < occ - 2 * step), lips, np.nan)
by, bx = np.nonzero(band); L = lips[by, bx]; occ = dQ[by, bx]
n = np.isfinite(L).sum(1); scored = n >= 1
lo = np.nanmin(np.where(np.isfinite(L), L, np.inf), 1) - step; hi = np.nanmax(np.where(np.isfinite(L), L, -np.inf), 1) + step
p50 = np.nanmedian(np.where(scored[:, None], L, np.nan), 1) if scored.any() else np.full(len(by), np.nan); skyR = p50 < 0.02
spread = (hi - lo) / step - 2
print(f'{P.split("/")[-1]}: band {band.sum()}, scored {100 * scored.mean():.1f} % (a far lip on >= 1 axis; >= 2 lips {100 * (n >= 2).mean():.1f} %); sky lips {100 * (skyR & scored).sum() / max(1, scored.sum()):.1f} % of scored; lip median d p10/p50/p90 {np.nanpercentile(p50[scored], [10, 50, 90]).round(3)}; lip spread (max-min) median {np.nanmedian(spread[n >= 2]):.1f} steps')
dT = None
if S:
    K = '/home/user/moebiusv2/harness/truthkit/out'; outer, pn = meta['outer'], meta['pn']
    z = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = z['cls']; w = z['w_disp']; dep = z['depth']; H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls = cls[y0:y0 + ph, x0:x0 + pw]; w = w[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]
    v_ = (cls >= 2) & (cls <= 5) & (w > 0); has = v_.any(-1); kk = np.argmax(v_, -1); dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]
    dT = np.where(has & np.isfinite(dT), dT, np.nan)[by, bx]
    depth_of_d = lambda d: outer * (1 - np.clip(d / pn, 0, 1) ** 2 * (3 - 2 * np.clip(d / pn, 0, 1)))
    t0 = scored & np.isfinite(dT); eL = np.abs(depth_of_d(p50) - dT)
    print(f'   truth: {100 * np.isfinite(dT[scored]).mean():.0f} % of scored texels have a first hidden layer; the LIP itself as the fill: median |e| {np.median(eL[t0]):.3f} m, surface lips {np.median(eL[t0 & ~skyR]) if (t0 & ~skyR).sum() else np.nan:.3f} m, sky lips {np.median(eL[t0 & skyR]) if (t0 & skyR).sum() else np.nan:.3f} m')
for d in args:
    D = d if d.startswith('/') else f'{P}/{d}'; d = d.rstrip('/').split('/')[-1]
    try: ff = np.fromfile(f'{D}/farField_stop.f32', np.float32).reshape(ph, pw)[by, bx]
    except FileNotFoundError: print(f'  {d:12s}: missing'); continue
    try: who = np.fromfile(f'{D}/who_stop.i32', np.int32).reshape(ph, pw)[by, bx]
    except FileNotFoundError: who = np.zeros(len(by), np.int32)
    unr = who < 0; kept = unr & (ff == occ); m = scored   # unowned texels hold the fall-back (the occluder's depth by default: a clone by construction; there are no holes)
    cont = (ff >= lo) & (ff <= hi) & m; bey = (ff < lo) & m; near = (ff > hi) & m; clone = (np.abs(ff - occ) <= 3 * step) & m
    err = np.abs(ff - p50) / step
    line = f'  {d:12s}: unowned {100 * (unr & scored).sum() / max(1, scored.sum()):4.1f} % (kept the occluder {100 * (kept & scored).sum() / max(1, scored.sum()):4.1f} %) |'
    for nm, sel in (('surface lips', m & ~skyR), ('sky lips', m & skyR)):
        if sel.sum() == 0: continue
        line += f' {nm}: cont {100 * cont[sel].mean():5.1f} % beyond {100 * bey[sel].mean():5.1f} % nearer {100 * near[sel].mean():5.1f} % (clone {100 * clone[sel].mean():4.1f} %), |fill-lip| {np.median(err[sel]):5.1f} steps |'
    print(line)
    if dT is not None:
        e = np.abs(depth_of_d(ff) - dT); t = m & np.isfinite(dT)
        parts = [f'{nm} {np.median(e[t & sel]):.3f} m (n {int((t & sel).sum())})' for nm, sel in (('all', np.ones_like(m)), ('surface', ~skyR), ('sky', skyR), ('cont', cont), ('beyond', bey), ('nearer', near), ('clone', clone)) if (t & sel).sum() >= 50]
        print(f'      truth median |e| by lip class: ' + ', '.join(parts))
