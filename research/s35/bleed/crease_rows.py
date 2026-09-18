"""S35 §39: the fill's error against the truth by truth primitive and by row band, over the background class of the band -- the
crease shows as a row band of error where the truth changes primitive (wall to floor).
  crease_rows.py <scene> <probe dir> <outdir>... """
import sys, json, numpy as np
S, P = sys.argv[1:3]; dirs = sys.argv[3:]; K = '/home/user/moebiusv2/harness/truthkit/out'
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; outer, pn = meta['outer'], meta['pn']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0
z = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = z['cls']; w = z['w_disp']; dep = z['depth']; pid = z['pid']; H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
sl = (slice(y0, y0 + ph), slice(x0, x0 + pw)); cls = cls[sl]; w = w[sl]; dep = dep[sl]; pid = pid[sl]
vis = (cls >= 2) & (cls <= 5) & (w > 0); has = vis.any(-1); kk = np.argmax(vis, -1)
dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; cT = np.take_along_axis(cls, kk[..., None], -1)[..., 0]; pT = np.take_along_axis(pid, kk[..., None], -1)[..., 0]
def depth_of_d(d): t = np.clip(d / pn, 0, 1); return outer * (1 - t * t * (3 - 2 * t))
names = {p['pid']: p['name'] for p in json.load(open(f'{K}/{S}/meta.json'))['prims']} if 'prims' in json.load(open(f'{K}/{S}/meta.json')) else {}
for d in dirs:
    ff = np.fromfile(f'{d}/farField_stop.f32', np.float32).reshape(ph, pw); who = np.fromfile(f'{d}/who_stop.i32', np.int32).reshape(ph, pw)
    err = depth_of_d(ff) - dT; ok = band & has & (cT == 2) & (who >= 0)
    print(f'{d.split("/")[-1]}: background band texels {ok.sum()} (unreached {int((band & has & (cT == 2) & (who < 0)).sum())}): median |e| {np.median(np.abs(err[ok])):.4f} m, p90 {np.percentile(np.abs(err[ok]), 90):.4f}, mean {err[ok].mean():+.4f}; share over 1 cm {100 * (np.abs(err[ok]) > 0.01).mean():.1f} %')
    for p in np.unique(pT[ok]):
        mm = ok & (pT == p); print(f'   truth {names.get(int(p), p)}: n {mm.sum()} med|e| {np.median(np.abs(err[mm])):.4f} p90 {np.percentile(np.abs(err[mm]), 90):.4f} mean {err[mm].mean():+.4f} over 1 cm {100 * (np.abs(err[mm]) > 0.01).mean():.1f} %')
    ys = np.flatnonzero(ok.any(1)); step = max(1, (ys.max() - ys.min()) // 12)
    for r0 in range(ys.min(), ys.max() + 1, step):
        mm = ok.copy(); mm[:r0] = False; mm[r0 + step:] = False
        if mm.sum(): print(f'   rows {r0}-{r0 + step}: n {mm.sum():6d} med|e| {np.median(np.abs(err[mm])):.4f} p90 {np.percentile(np.abs(err[mm]), 90):.4f} mean {err[mm].mean():+.4f}  truth ' + ', '.join(f'{names.get(int(k), k)} {v}' for k, v in zip(*np.unique(pT[mm], return_counts=True))))
