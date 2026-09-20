"""S35 §45: what fills the band inside the troll's footprint, read against the DATA beside it instead of fixed depth bands.
`trollfill.py` counted 'forest' as d in 0.12..0.45 and 'gap' as d < 0.05; but the troll's own depth is 0.19-0.35 and the visible
forest touching his silhouette is 0.02-0.07 between his arms and 0.1-0.2 at his feet, so a fill at his own depth read as
'forest' and the continuation of the forest beside him read as 'gap'. Here, per band of rows: the depths of the visible texels
within six texels of his footprint (the ring; not his, not band) give [p10, p90]; a fill texel is CONTINUATION when it lies in
that range widened by one visible step, BEYOND when deeper, NEARER when nearer; and separately OWN when it lies within his own
depth's p10..p90 (a clone of the occluder). Rows are banded by 100.
  trollfill2.py <arm dirs...>"""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
P = '/home/user/moebiusv2/harness/shots/streakclass/troll_s35'; meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw)
m13 = np.asarray(Image.open('/home/user/moebiusv2/harness/shots/objlayers/view_troll_v2/plane_object_ids_sam.png')); m13 = m13[..., 0] if m13.ndim == 3 else m13
if m13.shape != (ph, pw): m13 = np.asarray(Image.fromarray(m13).resize((pw, ph), Image.NEAREST))
ids, cnt = np.unique(m13[m13 > 0], return_counts=True); troll = int(ids[np.argmax(cnt)]); sel = band & (m13 == troll)
ring = ndimage.binary_dilation(sel, iterations=6) & ~band & (m13 != troll)
q = float(meta.get('quantum', 1 / 65535)); step = 1.760e-3   # the visible step used in the runs
own = np.percentile(dQ[sel], [10, 90])
ys = np.nonzero(sel)[0]; bands = [(r, r + 100) for r in range(int(ys.min()) // 100 * 100, int(ys.max()) + 1, 100)]
lo = np.full((ph, pw), np.nan); hi = np.full((ph, pw), np.nan)
for a, b in bands:
    r = ring[a:b]
    if r.sum() < 20: continue
    p10, p90 = np.percentile(dQ[a:b][r], [10, 90]); lo[a:b] = p10 - step; hi[a:b] = p90 + step
print(f'troll id {troll}: {sel.sum()} band texels; own depth p10..p90 {own[0]:.3f}..{own[1]:.3f}; ring {ring.sum()} texels, by rows:')
for a, b in bands:
    r = ring[a:b]
    if r.sum() >= 20: print(f'   rows {a}-{b}: ring d p10/p50/p90 {np.percentile(dQ[a:b][r], [10, 50, 90]).round(3)}, footprint {sel[a:b].sum()} texels')
okB = np.isfinite(lo) & sel
for d in sys.argv[1:]:
    try: ff = np.fromfile(f'{P}/{d}/farField_stop.f32', np.float32).reshape(ph, pw)
    except FileNotFoundError: print(d, 'missing'); continue
    v = ff[okB]; l = lo[okB]; h = hi[okB]
    cont = (v >= l) & (v <= h); bey = v < l; near = v > h; isOwn = (v >= own[0]) & (v <= own[1])
    print(f'  {d:12s}: continuation {100 * cont.mean():5.1f} %  beyond {100 * bey.mean():5.1f} %  nearer {100 * near.mean():5.1f} %  | at his own depth {100 * isOwn.mean():5.1f} %  | fill p10/p50/p90 {np.percentile(v, 10):.3f}/{np.median(v):.3f}/{np.percentile(v, 90):.3f}')
