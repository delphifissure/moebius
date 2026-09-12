#!/usr/bin/env python3
"""S14 step 0 — per-tile noise statistics of raw depth maps (no app): in 32x32 tiles, the MAD-sigma of the second differences
(both axes, in units of the map's grid) and their lag-1 autocorrelation rho. White texel noise gives rho = -2/3 (cov of
adjacent second differences of white noise = -4 var, var = 6 var); a smooth surface gives rho -> +1; uniform quantisation
error alone (var q^2/12) gives a second-difference sigma of sqrt(6/12) q = 0.707 q. Classes per tile: EXACT (sigma <= 0.707 q),
NOISE (sigma > 0.707 q and rho < 0), STRUCTURE (sigma > 0.707 q and rho >= 0)."""
import sys, os, numpy as np
from PIL import Image
T = 32
def stats(path):
    im = Image.open(path); a = np.asarray(im).astype(np.float64)
    if a.ndim == 3: a = a[..., 0]
    q = 1 / 65535 if im.mode.startswith('I') else 1 / 255; a = a * q if im.mode.startswith('I') else a / 255
    h, w = a.shape; ny, nx = h // T, w // T; cls = np.zeros((ny, nx), np.uint8); sig = np.zeros((ny, nx)); rho = np.full((ny, nx), np.nan); cls3 = np.zeros((ny, nx), np.uint8); sig3 = np.zeros((ny, nx))
    for ty in range(ny):
        for tx in range(nx):
            b = a[ty * T:(ty + 1) * T, tx * T:(tx + 1) * T]
            dx = b[:, 2:] - 2 * b[:, 1:-1] + b[:, :-2]; dy = b[2:, :] - 2 * b[1:-1, :] + b[:-2, :]
            d2 = np.concatenate([np.abs(dx).ravel(), np.abs(dy).ravel()]); med = np.median(d2); s = med / (0.6745 * np.sqrt(6)) / q; sig[ty, tx] = s
            px = np.concatenate([dx[:, :-1].ravel(), dy[:-1, :].ravel()]); py = np.concatenate([dx[:, 1:].ravel(), dy[1:, :].ravel()])
            if px.std() > 0 and py.std() > 0: rho[ty, tx] = np.corrcoef(px, py)[0, 1]
            d3x = b[:, 3:] - 3 * b[:, 2:-1] + 3 * b[:, 1:-2] - b[:, :-3]; d3y = b[3:, :] - 3 * b[2:-1, :] + 3 * b[1:-2, :] - b[:-3, :]
            d3 = np.concatenate([np.abs(d3x).ravel(), np.abs(d3y).ravel()]); s3 = np.median(d3) / (0.6745 * np.sqrt(20)) / q; sig3[ty, tx] = s3
            cls3[ty, tx] = 1 if s3 > np.sqrt(20 / 12) else 0
            if s <= np.sqrt(0.5): cls[ty, tx] = 0
            elif np.isnan(rho[ty, tx]) or rho[ty, tx] < 0: cls[ty, tx] = 1
            else: cls[ty, tx] = 2
    n = cls.size; return dict(mode=im.mode, size=(w, h), tiles=n, exact=int((cls == 0).sum()) / n, noise=int((cls == 1).sum()) / n, structure=int((cls == 2).sum()) / n,
                              sig_med_noisy=float(np.median(sig[cls == 1])) if (cls == 1).any() else 0, rho_med_noisy=float(np.nanmedian(rho[cls == 1])) if (cls == 1).any() else float('nan'),
                              rho_med_struct=float(np.nanmedian(rho[cls == 2])) if (cls == 2).any() else float('nan'), sig_global=float(np.median(sig)), noise3=int(cls3.sum()) / n, sig3_med_noisy=float(np.median(sig3[cls3 == 1])) if cls3.any() else 0, agree=float(((cls3 == 1) == (cls == 1)).mean())), cls, sig, rho, cls3
R = '/home/user/moebiusv2'; K = R + '/harness/truthkit/out'; B = R + '/harness/batchB'
maps = [(f'kit {S}', f'{K}/{S}/rest_depth16.png') for S in ['S15', 'S32', 'S31', 'S11', 'S2', 'S26', 'S16', 'S27', 'S5', 'S7']]
maps += [('troll DA3 16-bit', f'{R}/depth_da3mono16.png'), ('troll DA2 16-bit', f'{R}/depth16.png'), ('troll old 8-bit', f'{R}/defaultImgDepth.png')]
maps += [(f'{P} DA3 16-bit', f'{B}/{P}_da3_16.png') for P in ['bristlecone', 'octopus', 'room', 'silverwarrior', 'starwatcher', 'vermeer']]
maps += [(f'{P} repo 8-bit', f'{B}/{P}_repo8.png') for P in ['octopus', 'room', 'silverwarrior', 'starwatcher']]
out = sys.argv[1] if len(sys.argv) > 1 else None; tiles = []
print(f"{'map':24s} {'mode':6s} {'tiles':>5s} {'exact%':>7s} {'noise%':>7s} {'struct%':>8s} {'sig(noisy) /q':>13s} {'rho noisy':>9s} {'rho struct':>10s} {'sig global /q':>13s} {'D3 noise%':>9s} {'sig3 /q':>8s} {'agree':>6s}")
for name, p in maps:
    if not os.path.exists(p): print(name, 'missing'); continue
    r, cls, sig, rho, cls3 = stats(p)
    print(f"{name:24s} {r['mode']:6s} {r['tiles']:5d} {100*r['exact']:7.1f} {100*r['noise']:7.1f} {100*r['structure']:8.1f} {r['sig_med_noisy']:13.2f} {r['rho_med_noisy']:9.2f} {r['rho_med_struct']:10.2f} {r['sig_global']:13.2f} {100*r['noise3']:9.1f} {r['sig3_med_noisy']:8.2f} {100*r['agree']:6.1f}")
    tiles.append((name, np.where(cls3 == 1, 1, np.where(cls == 2, 2, 0))))
if out:
    from PIL import ImageDraw
    W = 260; sheet = Image.new('RGB', (W * 6, 150 * ((len(tiles) + 5) // 6)), (18, 18, 18)); dr = ImageDraw.Draw(sheet)
    for k, (name, cls) in enumerate(tiles):
        rgb = np.zeros(cls.shape + (3,), np.uint8); rgb[cls == 0] = (60, 60, 60); rgb[cls == 1] = (230, 80, 60); rgb[cls == 2] = (60, 160, 230)
        im = Image.fromarray(rgb).resize((W - 10, int((W - 10) * cls.shape[0] / cls.shape[1])), Image.NEAREST); x, y = (k % 6) * W, (k // 6) * 150
        sheet.paste(im, (x + 5, y + 16)); dr.text((x + 5, y + 2), name, fill=(255, 255, 255))
    dr.text((4, sheet.size[1] - 14), 'grey = exact (sigma <= 0.707 q), red = noise (rho < 0), blue = structure (rho >= 0)', fill=(255, 255, 255)); sheet.save(out); print('sheet', out)
