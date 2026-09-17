"""Direct measurement on the app's own plate colour. Inner ring = band texels with a 4-neighbour that is not band and is nearer by
more than a quantum (the occluder's silhouette). For each: the FILL colour (plateColor) vs (a) that occluder neighbour's source
colour and (b) the far surface's own colour = median source colour of the texel's rim window tail (texels 4..12 beyond the
rim). Also the same for band texels 6 texels further from the silhouette (the membrane interior)."""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
D, C = sys.argv[1], sys.argv[2]
meta = json.load(open(f'{D}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{D}/dQ.f32', np.float32).reshape(ph, pw); dis = np.fromfile(f'{D}/disocc.u8', np.uint8).reshape(ph, pw) > 0
pc = np.fromfile(f'{D}/plateColor.u8', np.uint8).reshape(ph, pw, 4)[..., :3].astype(np.float32)
J = np.fromfile(f'{D}/farRimJ.i32', np.int32).reshape(N, 2); ax = np.fromfile(f'{D}/farAxis.u8', np.uint8)
col = np.asarray(Image.open(C).convert('RGB').resize((pw, ph), Image.BILINEAR)).astype(np.float32)
q = meta.get('quantum', meta.get('step', 1 / 255)) if isinstance(meta, dict) else 1 / 255
q = float(q) if q else 1 / 255
# occluder neighbour: not band and nearer than the band texel by > q
occ = np.zeros((ph, pw), bool); occCol = np.zeros((ph, pw, 3), np.float32)
for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
    nb = np.roll(np.roll(dis, dy, 0), dx, 1); nd = np.roll(np.roll(dQ, dy, 0), dx, 1); nc = np.roll(np.roll(col, dy, 0), dx, 1)
    m = dis & ~nb & (nd > dQ + q) & ~occ; occ |= m; occCol[m] = nc[m]
# far colour per band texel: tail of its rim window along its axis, side from the slot
far = np.full((ph, pw, 3), np.nan, np.float32); Jf = J.reshape(ph, pw, 2); axm = ax.reshape(ph, pw)
for slot, side in ((0, -1), (1, 1)):
    j = Jf[..., slot]; ok = dis & (j >= 0) & (axm > 0)
    ys, xs = np.nonzero(ok); jj = j[ys, xs]; a = axm[ys, xs]; jx = jj % pw; jy = jj // pw
    acc = np.zeros((len(ys), 3), np.float32); cnt = np.zeros(len(ys), np.float32)
    for k in range(4, 12):
        tx = np.where(a == 1, jx + side * k, jx); ty = np.where(a == 1, jy, jy + side * k); ins = (tx >= 0) & (tx < pw) & (ty >= 0) & (ty < ph)
        acc[ins] += col[ty[ins], tx[ins]]; cnt[ins] += 1
    have = cnt > 0; cur = far[ys, xs]; newv = acc / np.maximum(1, cnt)[:, None]
    take = have & np.isnan(cur[:, 0]); far[ys[take], xs[take]] = newv[take]
def report(mask, label):
    m = mask & occ2 & np.isfinite(far[..., 0]) & (np.linalg.norm(occC2 - far, axis=2) > 24)   # only where occluder and far colours differ
    if m.sum() == 0: print(f'  {label}: no texels'); return
    f = pc[m]; o = occC2[m]; b = far[m]
    dO = np.linalg.norm(f - o, axis=1); dB = np.linalg.norm(f - b, axis=1); t = np.clip(((f - b) * (o - b)).sum(1) / np.maximum(1e-6, ((o - b) ** 2).sum(1)), -1, 2)
    print(f'  {label}: {m.sum()} texels; fill closer to the OCCLUDER colour than to the far surface: {100 * (dO < dB).mean():.1f} %; occluder share of the fill (0 = far colour, 1 = occluder colour) median {np.median(t):.2f} mean {t.mean():.2f} p90 {np.percentile(t, 90):.2f}')
occ2 = occ; occC2 = occCol
print(D.split('/')[-1], 'band', int(dis.sum()), 'inner ring (silhouette)', int(occ.sum()))
report(occ, 'inner ring    ')
# 6 texels in: dilate the occluder-adjacent set by 6 within the band and take its outer boundary; propagate occluder colour by nearest
dist, (iy, ix) = ndimage.distance_transform_edt(~occ, return_indices=True)
occ2 = dis & (dist >= 5.5) & (dist < 6.5); occC2 = occCol[iy, ix]
report(occ2, '6 texels inside')
occ2 = dis & (dist >= 14.5) & (dist < 15.5); report(occ2, '15 texels inside')
