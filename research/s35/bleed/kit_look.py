"""Look at the buffer for a kit scene: rest colour, dQ, band, the app's per-line far field, sheets' far fields (dirs given), the
truth's first hidden layer (normalised the app's way) and the signed error of the last dir. l2_look.py <S> <probe dir> <out.png> <dir>..."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
S, P, OUT = sys.argv[1:4]; dirs = sys.argv[4:]; K = '/home/user/moebiusv2/harness/truthkit/out'
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; outer, pn = meta['outer'], meta['pn']
dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw); band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0
ffApp = np.fromfile(f'{P}/farField.f32', np.float32).reshape(ph, pw)
z = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = z['cls']; w = z['w_disp']; dep = z['depth']; H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
cls = cls[y0:y0 + ph, x0:x0 + pw]; w = w[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]
vis = (cls >= 2) & (cls <= 5) & (w > 0); has = vis.any(-1); kk = np.argmax(vis, -1); dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; cT = np.take_along_axis(cls, kk[..., None], -1)[..., 0]
def d_of_depth(depth_m):
    s = np.clip(1.0 - depth_m / outer, 0, 1); t = 0.5 - np.sin(np.arcsin(1 - 2 * s) / 3); return np.where(depth_m <= 0, pn, np.clip(t, 0, 1) * pn)
def depth_of_d(d):
    t = np.clip(d / pn, 0, 1); return outer * (1 - t * t * (3 - 2 * t))
dTn = np.where(has & np.isfinite(dT), d_of_depth(dT), np.nan)
g = lambda a: (255 * np.clip(np.nan_to_num(a) / max(1e-6, np.nanpercentile(dQ, 99.5)), 0, 1) ** 0.6).astype(np.uint8)
col = np.asarray(Image.open(f'{K}/{S}/rest_rgb.png').convert('RGB'))
tiles = [('colour', col), ('dQ', np.stack([g(dQ)] * 3, -1)), ('band + truth class (2 bg, 3 thing, 6 sky)', None), ('app per-line far', np.stack([g(ffApp)] * 3, -1)), ('truth hidden depth (norm)', np.stack([g(np.nan_to_num(dTn))] * 3, -1))]
cm = np.zeros((ph, pw, 3), np.uint8); cm[band] = (60, 60, 60); cm[band & (cT == 2)] = (60, 160, 60); cm[band & (cT == 3)] = (200, 80, 200); cm[band & (cT == 6)] = (80, 140, 255); tiles[2] = (tiles[2][0], cm)
for d in dirs:
    ff = np.fromfile(f'{P}/{d}/farField_stop.f32', np.float32).reshape(ph, pw); tiles.append((f'{d} far', np.stack([g(ff)] * 3, -1)))
    e = depth_of_d(ff) - np.nan_to_num(dT); m = band & has & np.isfinite(dT)
    em = np.zeros((ph, pw, 3), np.uint8); sc = np.clip(np.abs(e) / max(1e-6, np.nanpercentile(np.abs(e[m]), 95)), 0, 1) if m.any() else 0
    em[..., 0] = (255 * sc * (e < 0)).astype(np.uint8); em[..., 2] = (255 * sc * (e > 0)).astype(np.uint8); em[~m] = 0; tiles.append((f'{d} error (red nearer than truth, blue farther); median |e| {np.median(np.abs(e[m])):.3f} m', em))
    for c_, nm in ((2, 'bg'), (3, 'thing'), (6, 'sky')):
        mm = m & (cT == c_)
        if mm.any(): print(f'{d}: class {nm}: {int(mm.sum())} texels, median |e| {np.median(np.abs(e[mm])):.3f} m, mean {e[mm].mean():+.3f}; truth d median {np.nanmedian(dTn[mm]):.3f}, fill d median {np.median(ff[mm]):.3f}')
cols = 3; rows = (len(tiles) + cols - 1) // cols; sh = Image.new('RGB', (cols * pw, rows * (ph + 14)), (15, 15, 15)); dr = ImageDraw.Draw(sh)
for k, (t, im) in enumerate(tiles):
    x = (k % cols) * pw; y = (k // cols) * (ph + 14); dr.text((x + 3, y + 1), t, fill=(255, 230, 90)); sh.paste(Image.fromarray(im), (x, y + 14))
sh.save(OUT); print('wrote', OUT)
