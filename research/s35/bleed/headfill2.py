"""S35 §46: the band beside the sunflowers' big head, read against the DATA beside it. `headfill.py` counted a row as right when
its median fill was sky (d < 0.02) -- a bar taken from the measured arm's own fill. But the visible texels touching the head's
silhouette are sky (0.009) only down to row ~329; below that they are the field's flowers at d 0.14-0.16, so a sky fill in the
lowest sixty rows is the x-ray to the sky, not the answer. Here, per band of 30 rows: the visible texels within six texels of
the scored band region (not band, not the head) give [p10, p90]; a fill texel is CONTINUATION when it lies in that range
widened by one step, BEYOND when deeper (toward the sky), NEARER when nearer; per arm the shares over the whole region and the
per-row-band medians beside the ring's.
  headfill2.py <arm dirs...>"""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
P = '/home/user/moebiusv2/harness/shots/streakclass/room_s35'; meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; step = 2.679e-3
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw)
oid9 = np.asarray(Image.open('/home/user/moebiusv2/harness/shots/objlayers/view_sunflowers/plane_object_ids_sam.png')); oid9 = oid9[..., 0] if oid9.ndim == 3 else oid9
ys, xs = np.nonzero(oid9 == 1); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
reg = np.zeros((ph, pw), bool); reg[y0:y1 + 1, x0:min(pw, x1 + 160)] = True; reg &= band & (oid9 != 1)
head = oid9 == 1; ring = ndimage.binary_dilation(reg, iterations=6) & ~band & ~head
bands = [(a, min(y1 + 1, a + 30)) for a in range(int(y0), int(y1) + 1, 30)]
lo = np.full((ph, pw), np.nan); hi = np.full((ph, pw), np.nan); md = np.full((ph, pw), np.nan)
for a, b in bands:
    r = ring[a:b]
    if r.sum() < 10: continue
    p10, p90 = np.percentile(dQ[a:b][r], [10, 90]); lo[a:b] = p10 - step; hi[a:b] = p90 + step; md[a:b] = np.median(dQ[a:b][r])
okB = np.isfinite(lo) & reg
print(f'big head rows {y0}-{y1}; band region {reg.sum()} texels ({okB.sum()} with a ring); ring by rows: ' + '; '.join(f'{a}-{b} {np.percentile(dQ[a:b][ring[a:b]], 50):.3f}' for a, b in bands if ring[a:b].sum() >= 10))
for d in sys.argv[1:]:
    try: ff = np.fromfile(f'{P}/{d}/farField_stop.f32', np.float32).reshape(ph, pw)
    except FileNotFoundError: print(d, 'missing'); continue
    v = ff[okB]; l = lo[okB]; h = hi[okB]; cont = (v >= l) & (v <= h); bey = v < l; near = v > h; err = np.abs(v - md[okB]) / step; errLow = err[(okB & (np.arange(ph)[:, None] >= 329))[okB]]
    rows = ' '.join(f'{np.median(ff[a:b][reg[a:b]]):.3f}' for a, b in bands if ring[a:b].sum() >= 10)
    print(f'  {d:12s}: continuation {100 * cont.mean():5.1f} %  beyond {100 * bey.mean():5.1f} %  nearer {100 * near.mean():5.1f} %  | |fill - ring| median {np.median(err):5.1f} steps, rows 329+ {np.median(errLow):5.1f} | per-row-band median fill: {rows}')
