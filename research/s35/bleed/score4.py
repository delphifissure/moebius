"""S35 §23 step 1, headline instrument. Usage: score4.py <name> <color.png> <tag=dir> ...
The mechanism lives at the SILHOUETTE: band texels whose 4-neighbour is a non-band texel BEHIND them (the visible far
surface). Their fill is a Dirichlet value for the membrane, so their colour sets the whole band's. For each such texel, along
the direction into the far surface:
  o  = the occluder's own colour: the source at the band texel itself (it is inside the occluder's footprint)
  b  = the far surface's clean local colour: median of the source over texels 4..12 out
  blend = the source at texels 1..2 out (the anti-aliased edge)
  share t = ((fill - b).(o - b))/|o - b|^2 : 0 = the far surface, 1 = the occluder.
Also |fill - b| (does the wash match the surface it continues) and |fill - blend|."""
import sys, json, numpy as np
from PIL import Image
NAME, C = sys.argv[1], sys.argv[2]
arms = [a.split('=', 1) for a in sys.argv[3:]]; D0 = arms[0][1]
meta = json.load(open(f'{D0}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{D0}/dQ.f32', np.float32).reshape(ph, pw); dis = np.fromfile(f'{D0}/disocc.u8', np.uint8).reshape(ph, pw) > 0
q = float(meta.get('quantum') or meta.get('step') or 1 / 255)
im = Image.open(C).convert('RGB'); col = np.asarray(im if im.size == (pw, ph) else im.resize((pw, ph), Image.BILINEAR)).astype(np.float32)
pc = {t: np.fromfile(f'{d}/plateColor.u8', np.uint8).reshape(ph, pw, 4)[..., :3].astype(np.float32) for t, d in arms}
res = {t: {'share': [], 'db': [], 'dbl': []} for t, _ in arms}; nTot = 0
for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
    nb = np.roll(np.roll(dis, -dy, 0), -dx, 1); nd = np.roll(np.roll(dQ, -dy, 0), -dx, 1)
    m = dis & ~nb & (nd < dQ - q)
    m[:3, :] = m[-3:, :] = m[:, :3] = m[:, -3:] = False
    ys, xs = np.nonzero(m)
    keep = (ys + 12 * dy < ph - 1) & (ys + 12 * dy >= 0) & (xs + 12 * dx < pw - 1) & (xs + 12 * dx >= 0)
    ys, xs = ys[keep], xs[keep]
    if not len(ys): continue
    o = col[ys, xs]
    deep = np.stack([col[ys + k * dy, xs + k * dx] for k in range(4, 13)], 0); b = np.median(deep, 0)
    blend = 0.5 * (col[ys + dy, xs + dx] + col[ys + 2 * dy, xs + 2 * dx])
    den = ((o - b) ** 2).sum(1); ok = den > 24 ** 2
    if not ok.any(): continue
    nTot += int(ok.sum())
    for t, _ in arms:
        f = pc[t][ys, xs]
        res[t]['share'].append(np.clip((((f - b) * (o - b)).sum(1) / np.maximum(1e-6, den))[ok], -1, 2))
        res[t]['db'].append(np.linalg.norm(f - b, axis=1)[ok]); res[t]['dbl'].append(np.linalg.norm(f - blend, axis=1)[ok])
print(f'== {NAME}: silhouette texels with an occluder/background contrast: {nTot}')
for t, _ in arms:
    s = np.concatenate(res[t]['share']); db = np.concatenate(res[t]['db']); dbl = np.concatenate(res[t]['dbl'])
    print(f'   {t:8s}: occluder share median {np.median(s):+.2f} mean {s.mean():+.2f} p90 {np.percentile(s, 90):+.2f} | |fill - clean background| median {np.median(db):5.1f} | |fill - blend| median {np.median(dbl):5.1f}')
