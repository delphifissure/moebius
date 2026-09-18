"""Who owns the band inside the biggest thing's footprint? owners.py <dump> <mask.png> <dir> [<dir>...]"""
import sys, json, glob, numpy as np
from PIL import Image
P, M = sys.argv[1], sys.argv[2]; meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw)
m = np.asarray(Image.open(M)); m = m[..., 0] if m.ndim == 3 else m
if m.shape != (ph, pw): m = np.asarray(Image.fromarray(m).resize((pw, ph), Image.NEAREST))
ids, cnt = np.unique(m[m > 0], return_counts=True); big = int(ids[np.argmax([(band & (m == i)).sum() for i in ids])]); foot = band & (m == big)
import os
if os.environ.get('HEADREG'):   # the headfill.py region: band right of the 9-click head, not the head
    o9 = np.asarray(Image.open(os.environ['HEADREG'])); o9 = o9[..., 0] if o9.ndim == 3 else o9; ys, xs = np.nonzero(o9 == 1); foot = np.zeros((ph, pw), bool); foot[ys.min():ys.max() + 1, xs.min():min(pw, xs.max() + 160)] = True; foot &= band & (o9 != 1); print('head region', foot.sum())
print(f'thing {big}: {foot.sum()} band texels in its footprint, its depth median {np.median(dQ[m == big]):.3f}')
for d in sys.argv[3:]:
    try: who = np.fromfile(f'{P}/{d}/who_stop.i32', np.int32).reshape(ph, pw); ff = np.fromfile(f'{P}/{d}/farField_stop.f32', np.float32).reshape(ph, pw)
    except FileNotFoundError: print(d, 'missing'); continue
    sm = glob.glob(f'{P}/{d}/summary_*.json'); rims = json.load(open(sm[0]))['rims'] if sm else []
    w = who[foot]; f = ff[foot]; u, c = np.unique(w, return_counts=True); o = np.argsort(-c)
    print(f'{d}: {len(u)} owners; far p10/p50/p90 {np.percentile(f, [10, 50, 90]).round(3)}')
    for k in o[:10]:
        s = int(u[k]); r = rims[s] if 0 <= s < len(rims) else {}
        print(f'   sheet {s:5d}: {c[k]:6d} texels ({100 * c[k] / len(w):4.1f} %) far median {np.median(f[w == s]):.3f} | rim depth {r.get("depth", float("nan")):.3f} oid {r.get("oid")} rows {r.get("rows")} cols {r.get("cols")} hedge {r.get("hedge")}')
