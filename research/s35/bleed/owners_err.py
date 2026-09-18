"""owners in the band by error against truth: owners_err.py <probe dir> <truth npz> <sheets out dir> [<per-sheet npz dir>]"""
import sys, json, numpy as np
P, T, D = sys.argv[1:4]; RD = sys.argv[4] if len(sys.argv) > 4 else D
m = json.load(open(P + '/meta.json')); pw, ph = m['pw'], m['ph']; outer = m['outer']; pn = m['pn']
band = np.fromfile(P + '/disocc.u8', np.uint8).reshape(ph, pw) > 0; who = np.fromfile(D + '/who_stop.i32', np.int32).reshape(ph, pw); ff = np.fromfile(D + '/farField_stop.f32', np.float32).reshape(ph, pw)
z = np.load(T); cls = z['cls']; w = z['w_disp']; dep = z['depth']; pid = z['pid']; H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
cls = cls[y0:y0 + ph, x0:x0 + pw]; w = w[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]; pid = pid[y0:y0 + ph, x0:x0 + pw]
vis = (cls >= 2) & (cls <= 5) & (w > 0); has = vis.any(-1); kk = np.argmax(vis, -1); dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; pT = np.take_along_axis(pid, kk[..., None], -1)[..., 0]
def depth_of_d(d):
    t = np.clip(d / pn, 0, 1); return outer * (1 - t * t * (3 - 2 * t))
mm = band & has & np.isfinite(dT); e = depth_of_d(ff) - dT
per = {}
try:
    zz = np.load(RD + '/reach_diag.npz'); per = {int(p[0]): p for p in zz['per']}
except Exception: pass
print(f'{D.split("/")[-1]}: band with truth {int(mm.sum())}; |e| median {np.median(np.abs(e[mm])):.4f} p90 {np.percentile(np.abs(e[mm]),90):.3f} mean {e[mm].mean():+.3f}; frac |e|>0.1 m {100*(np.abs(e[mm])>0.1).mean():.1f} %')
u, c = np.unique(who[mm], return_counts=True)
rows = []
for s_, n_ in zip(u, c):
    k = mm & (who == s_); ae = np.abs(e[k]); bad = int((ae > 0.1).sum())
    tp = np.unique(pT[k], return_counts=True); top = tp[0][np.argmax(tp[1])]
    p = per.get(int(s_)); extra = f'pidS {int(p[1])} E {int(p[2])} R {int(p[3])} rims {int(p[4])} comp {int(p[5])}' if p is not None else ''
    rows.append((bad, f'   who {int(s_):5d}: {int(n_):6d} texels, |e| median {np.median(ae):.3f}, >0.1 m: {bad:6d} ({100*bad/max(1,n_):4.1f} %); truth pid mode {int(top)}; {extra}'))
for bad, line in sorted(rows, key=lambda r: -r[0])[:10]: print(line)
