"""S35 §39: the group plate at a crease. For a probe dir and one or more sheets.py output dirs (arms), draw the plate field of one join
group over its domain (grey = disparity, the picture's own dQ scale), the group's visible face boundaries (blue) and the hinge edges
(red), and print a column profile of the plate through the hole for each arm.
  crease_look.py <probe dir> <out.png> <group|auto> <col|auto> <outdir>...
'auto' group = the group whose plate has the largest domain; 'auto' column = the middle of the band's widest row."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
P, OUT, GSEL, CSEL = sys.argv[1:5]; dirs = sys.argv[5:]
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw); band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0
outer, inner, pn, D = meta['outer'], meta['inner'], meta['pn'], meta['D']   # the plate is solved in disparity; back to the app's d by the depth law
def z_of_d(d):
    d = np.clip(d, 0, 1); s1 = d / pn; s2 = (d - pn) / (1 - pn)
    return np.where(d < pn, -outer + outer * (s1 * s1 * (3 - 2 * s1)), inner * (s2 * s2 * (3 - 2 * s2)))
dtab = np.linspace(0, 1, 8193); disptab = 1.0 / np.maximum(1e-4, D - z_of_d(dtab)); order = np.argsort(disptab)
def depth_of_disp(v): return np.where(np.isfinite(v), np.interp(np.nan_to_num(v), disptab[order], dtab[order]), np.nan)
sc = max(1e-6, float(np.percentile(dQ, 99.5)))
g = lambda a: (255 * np.clip(np.nan_to_num(a) / sc, 0, 1) ** 0.6).astype(np.uint8)
tiles = []; prof = {}
base = np.stack([g(dQ)] * 3, -1); base[band] = (base[band] * 0.5 + np.array([40, 40, 90])).clip(0, 255).astype(np.uint8)
tiles.append(('dQ, band', base))
comp = None
for d in dirs:
    z = np.load(f'{d}/group_plates.npz'); comp = np.fromfile(f'{d}/comp.i32', np.int32); cj = np.fromfile(f'{d}/compJ.i32', np.int32)
    groups = sorted(set(int(k[1:-3]) for k in z.files if k.endswith('_om')), key=lambda G: -len(z[f'g{G}_om']))
    G = groups[0] if GSEL == 'auto' else int(GSEL)
    if f'g{G}_om' not in z.files: print(f'{d}: group {G} has no plate'); continue
    om = z[f'g{G}_om']; x = z[f'g{G}_x']; fld = np.full(N, np.nan, np.float32); fld[om] = depth_of_disp(x.astype(np.float64))
    dom = np.zeros(N, bool); dom[om[band.ravel()[om]]] = True    # the plate over the band
    im = np.stack([g(np.where(dom, fld, dQ.ravel()).reshape(ph, pw))] * 3, -1)
    vis = (cj == G) & ~band.ravel()
    Ih = np.arange(N).reshape(ph, pw)[:, :-1].ravel(); Iv = np.arange(N).reshape(ph, pw)[:-1, :].ravel()
    bh = Ih[vis[Ih] & vis[Ih + 1] & (comp[Ih] != comp[Ih + 1])]; bv = Iv[vis[Iv] & vis[Iv + pw] & (comp[Iv] != comp[Iv + pw])]
    fb = np.zeros(N, bool); fb[bh] = True; fb[bv] = True; im.reshape(-1, 3)[fb] = (70, 120, 255)
    hE = z['hE']; vE = z['vE']; hin = np.zeros(N, bool); hin[hE] = True; hin[vE] = True; hin[np.minimum(hE + 1, N - 1)] = True; hin[np.minimum(vE + pw, N - 1)] = True
    im.reshape(-1, 3)[hin & dom] = (255, 60, 40)
    nf = int((z['folds'][:, 0] == G).sum()) if len(z['folds']) else 0
    tiles.append((f'{d.split("/")[-1]}: plate of group {G} ({len(om)} unknowns, {nf} creases continued, {int((hin & dom).sum())} hinge texels)', im))
    prof[d.split('/')[-1]] = (fld.reshape(ph, pw), G, dom.reshape(ph, pw))
cols = 2; rows = (len(tiles) + 1) // 2
sh = Image.new('RGB', (cols * pw, rows * (ph + 14)), (0, 0, 0)); dr = ImageDraw.Draw(sh)
for k, (t, im) in enumerate(tiles):
    x0 = (k % cols) * pw; y0 = (k // cols) * (ph + 14); dr.text((x0 + 3, y0 + 1), t, fill=(255, 230, 90)); sh.paste(Image.fromarray(im), (x0, y0 + 14))
sh.save(OUT); print('wrote', OUT)
if prof:
    wr = np.argmax(band.sum(1)); cs = np.flatnonzero(band[wr]); c = int(np.median(cs)) if CSEL == 'auto' else int(CSEL)
    rr = np.flatnonzero(band[:, c]); r0, r1 = max(0, rr.min() - 8), min(ph, rr.max() + 9)
    names = list(prof); print(f'column {c}, rows {r0}-{r1}: dQ, then plate per arm ' + ' | '.join(names) + '  (. = not on the plate)')
    for r in range(r0, r1, max(1, (r1 - r0) // 40)):
        s = f'row {r:4d} band {int(band[r, c])} dQ {dQ[r, c]:.3f} '
        for n_ in names:
            f_, G, dm = prof[n_]; v = f_[r, c]; s += f' | {v:.3f}' if np.isfinite(v) else ' |   .  '
        print(s)
