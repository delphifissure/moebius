#!/usr/bin/env python3
"""c_bundle_check.py <audit dir>: the bundle.zip's plane_* files against the same bake's dumped arrays."""
import sys, os, io, json, zipfile, numpy as np
from PIL import Image
D = sys.argv[1]; z = zipfile.ZipFile(os.path.join(D, 'bundle.zip')); names = set(z.namelist())
meta = json.loads(z.read('meta.json')); dj = json.load(open(os.path.join(D, 'dump.json')))
pl = meta.get('plane'); 
if not pl: print('NO plane set in the bundle'); sys.exit(1)
pw, ph = pl['nativeRes']; N = pw * ph
def arr(n, ty):
    p = os.path.join(D, n); return np.fromfile(p, ty) if os.path.exists(p) else None
def img(n):
    im = Image.open(io.BytesIO(z.read(n))); return im, np.array(im)
def unflip(a): return a.reshape(ph, pw)[::-1].reshape(-1)
dQ = arr('dQ.f32', np.float32); pF = arr('plateF.f32', np.float32); dis = arr('disocc.u8', np.uint8); car = arr('carrier.u8', np.uint8)
paint = arr('platePaint.u8', np.uint8); tier = arr('bandTier.u8', np.uint8); pc = arr('plateColor.u8', np.uint8); pF2 = arr('plateF2.f32', np.float32); has2 = arr('plate2Has.u8', np.uint8); pc2 = arr('plateColor2.u8', np.uint8)
torn = arr('plateTorn.u8', np.uint8); sky = arr('skyColor.u8', np.uint8); bp = arr('bandPose.f32', np.float32)
rows = []
def chk16(name, ref):
    if name not in names: rows.append((name, 'MISSING', '')); return
    im, a = img(name); ok = im.mode in ('I;16', 'I;16B', 'I') and a.shape == (ph, pw)
    if ref is None: rows.append((name, 'no ref', im.mode)); return
    rr = ref.reshape(ph, pw).astype(np.float64); nOut = int(((rr < 0) | (rr > 1)).sum()); err = np.abs(a.astype(np.float64) / 65535 - np.clip(rr, 0, 1)); rows.append((name, 'OK' if ok and err.max() <= 0.5 / 65535 + 1e-9 else 'FAIL', f'{im.mode} {a.shape[1]}x{a.shape[0]} max|err| {err.max() * 65535:.3f}/65535; ref range [{rr.min():.5f}, {rr.max():.5f}], {nOut} outside [0,1] (clamped)'))
def chkmask(name, ref, desc=''):
    if name not in names: rows.append((name, 'MISSING' if ref is not None else 'absent (ok)', desc)); return
    im, a = img(name); a = a[..., 0] if a.ndim == 3 else a; ref2 = ref.reshape(ph, pw)
    d = int((a != ref2).sum()); rows.append((name, 'OK' if d == 0 else 'FAIL', f'{d} texels differ; white {int((a == 255).sum())}'))
def chkrgb(name, ref):
    if name not in names: rows.append((name, 'MISSING' if ref is not None else 'absent (ok)', '')); return
    im, a = img(name); a = a[..., :3]; r = ref.reshape(ph, pw, 4)[..., :3]; d = int((a != r).any(-1).sum()); rows.append((name, 'OK' if d == 0 else 'FAIL', f'{d} texels differ'))
chk16('plane_source_depth16.png', dQ); chk16('plane_plate_depth16.png', unflip(pF) if pF is not None else None)
chkrgb('plane_plate_color.png', pc)
if paint is not None:
    chkmask('plane_mask_inpaint.png', (paint > 0).astype(np.uint8) * 255); chkmask('plane_mask_class.png', paint * 60)
    if tier is not None: chkmask('plane_mask_inpaint_tier.png', (paint == 1).astype(np.uint8) * 255)
    # the class law itself: hasC (paint>0) vs band/tier
    c1 = int((paint == 1).sum()); c2 = int((paint == 2).sum()); c3 = int((paint == 3).sum())
    bad = int(((paint == 3) & (dis > 0)).sum()) + int(((paint == 1) & (dis == 0)).sum()) + int(((paint == 2) & (dis == 0)).sum())
    rows.append(('class law', 'OK' if bad == 0 else 'FAIL', f'paint {c1}, band-outside-tier {c2}, carrier-only {c3}; band {int(dis.sum())}, carriers {int(car.sum()) if car is not None else "-"}; law violations {bad}'))
    if car is not None: rows.append(('placeholders subset of carriers', 'OK' if int(((paint > 0) & (car == 0)).sum()) == 0 else 'FAIL', ''))
chkmask('plane_mask_band.png', dis * 255); 
if car is not None: chkmask('plane_mask_carriers.png', car * 255)
if torn is not None: chkmask('plane_plate_torn.png', torn * 255)
if bp is not None and 'plane_band_first_uncover.png' in names:
    im, a = img('plane_band_first_uncover.png'); v = np.where(bp > 1, 0, np.round(np.clip(bp, 0, 1) * 255)).astype(np.uint8).reshape(ph, pw); al = np.where(bp > 1, 0, 255).astype(np.uint8).reshape(ph, pw)
    rows.append(('plane_band_first_uncover.png', 'OK' if (a[..., 0] == v).all() and (a[..., 3] == al).all() else 'FAIL', f'in band {int((al == 255).sum())}'))
if pF2 is not None and has2 is not None:
    chk16('plane_plate2_depth16.png', unflip(pF2)); chkmask('plane_plate2_mask.png', has2 * 255); chkrgb('plane_plate2_color.png', pc2)
else: rows.append(('plate 2', 'absent (ok)' if 'plane_plate2_mask.png' not in names else 'FAIL: file without dump', ''))
if dj.get('skyOn'):
    chkmask('plane_sky_mask.png', (dQ < dj['skyQ']).astype(np.uint8) * 255); chkrgb('plane_sky_color.png', sky)
mg = dj.get('margin')
if mg and dj.get('plugMargin'):
    Mx, My = mg['Mx'], mg['My']; W2, H2 = pw + 2 * Mx, ph + 2 * My
    im, a = img('plane_out_mask_outpaint.png'); a = a[..., 0]; ref = np.ones((H2, W2), np.uint8) * 255; ref[My:My + ph, Mx:Mx + pw] = 0
    rows.append(('plane_out_mask_outpaint.png', 'OK' if a.shape == (H2, W2) and (a == ref).all() else 'FAIL', f'{a.shape[1]}x{a.shape[0]} margin ({Mx},{My})'))
    im, a = img('plane_out_depth16.png'); ext = np.pad(np.clip(unflip(pF).reshape(ph, pw), 0, 1), ((My, My), (Mx, Mx)), mode='edge'); err = np.abs(a / 65535 - ext).max()
    rows.append(('plane_out_depth16.png', 'OK' if im.mode in ('I;16', 'I;16B', 'I') and err <= 0.5 / 65535 + 1e-9 else 'FAIL', f'{im.mode} max|err| {err * 65535:.3f}/65535'))
    im, a = img('plane_out_color.png'); ext = np.pad(pc.reshape(ph, pw, 4)[..., :3], ((My, My), (Mx, Mx), (0, 0)), mode='edge'); d = int((a[..., :3] != ext).any(-1).sum())
    rows.append(('plane_out_color.png', 'OK' if d == 0 else 'FAIL', f'{d} texels differ'))
legacy = [n for n in names if n.startswith('src_')]; rows.append(('legacy src_* omitted', 'OK' if not legacy else 'FAIL', str(legacy) + ' meta.legacy_omitted=' + str(bool(meta.get('legacy_omitted')))))
print(f"{'file / check':36s} {'result':12s} detail")
for r in rows: print(f'{r[0]:36s} {r[1]:12s} {r[2]}')
print('counts (meta.plane):', json.dumps(pl['counts']))
print('files in bundle:', len(names), ' plane_*:', len([n for n in names if n.startswith('plane_')]), ' zip bytes:', os.path.getsize(os.path.join(D, 'bundle.zip')))
print('ALL OK' if all(r[1].startswith('OK') or r[1].startswith('absent') or r[1] == 'no ref' for r in rows) else 'FAILURES PRESENT')
