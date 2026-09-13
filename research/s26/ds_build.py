#!/usr/bin/env python3
"""Sprint 18 — depth-stage test, step 1: build the "completed layer" pictures from the truth kit.

For a scene with an env45 truth (scope_gt.npz on the 1600x900 canvas; the plate is the central pw x ph):
  peel1 : the picture with the front surface removed at every texel that has an ever-visible hidden layer
          (the first hidden layer's exact colour, any class 2-5) — a depth-peeled composite; the plane law is
          scored against this same "first ever-visible hidden layer" in check_app_band.py
  bg    : the picture with the occluding OBJECT removed entirely — at every texel whose first hidden layer is
          background / another thing (class 2/3) the first such layer's colour; texels whose hidden layers are all
          the object's own back faces (class 4/5) keep the source colour (no background was ever seen there)
Sky revealed behind an occluder (sky_hidden & sky_w_disp > 0, no finite depth) gets the scene's sky colour in
both pictures and is excluded from the metres error (as in check_app_band.py).

Writes out/<S>/{peel1,bg}.png and out/<S>/truth.npz with: d_vis (k0 depth, inf for sky), d_peel1, m_peel1,
d_bg, m_bg, sky (revealed-sky mask), cls_first, and the visible-fit mask m_fit = ~m_peel1 & ~sky & finite(d_vis).
Usage: python3 ds_build.py S15 [S2 ...]
"""
import sys, os, json
import numpy as np
from PIL import Image

TK = '/home/user/moebiusv2/harness/truthkit'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

def build(S):
    meta = json.load(open(f'{TK}/out/{S}/meta.json')); pw, ph = meta['nx'], meta['ny']
    g = np.load(f'{TK}/out/{S}_env45/scope_gt.npz')
    cls = g['cls']; dep = g['depth']; w = g['w_disp'].astype(np.float32); rgb = g['rgb']
    H, W, K = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    sl = (slice(y0, y0 + ph), slice(x0, x0 + pw))
    c = cls[sl]; d = dep[sl]; wc = w[sl]; col = rgb[sl]
    rest = np.array(Image.open(f'{TK}/out/{S}/rest_rgb.png').convert('RGB').resize((pw, ph), Image.NEAREST))
    d_vis = d[..., 0].astype(np.float32); d_vis[c[..., 0] < 0] = np.inf          # nothing hit at rest = sky
    vh = (c >= 2) & (c <= 5) & (wc > 0)
    # peel1: first ever-visible hidden layer of any class
    m1 = vh.any(-1); k1 = np.argmax(vh, -1)
    d1 = np.take_along_axis(d, k1[..., None], -1)[..., 0].astype(np.float32); d1[~m1] = np.nan
    c1 = np.take_along_axis(c, k1[..., None], -1)[..., 0]; c1[~m1] = -1
    col1 = np.take_along_axis(col, k1[..., None, None], -2)[..., 0, :]
    # bg: first ever-visible hidden layer that is NOT the object's own surface (class 2/3)
    vb = vh & (c <= 3)
    mb = vb.any(-1); kb = np.argmax(vb, -1)
    db = np.take_along_axis(d, kb[..., None], -1)[..., 0].astype(np.float32); db[~mb] = np.nan
    colb = np.take_along_axis(col, kb[..., None, None], -2)[..., 0, :]
    # revealed sky
    sky = np.zeros((ph, pw), bool)
    if 'sky_hidden' in g.files:
        sky = (g['sky_hidden'] & (g['sky_w_disp'].astype(np.float32) > 0))[sl]
    sky_seen = ~np.isfinite(d_vis)
    sky_col = np.median(rest[sky_seen].reshape(-1, 3), axis=0) if sky_seen.any() else np.array([135, 175, 225])
    peel1 = rest.copy(); peel1[m1] = col1[m1]; peel1[sky & ~m1] = sky_col
    bg = rest.copy(); bg[mb] = colb[mb]; bg[sky & ~mb] = sky_col
    m_fit = ~m1 & ~sky & np.isfinite(d_vis)
    od = f'{OUT}/{S}'; os.makedirs(od, exist_ok=True)
    Image.fromarray(rest).save(f'{od}/rest.png'); Image.fromarray(peel1).save(f'{od}/peel1.png'); Image.fromarray(bg).save(f'{od}/bg.png')
    np.savez_compressed(f'{od}/truth.npz', d_vis=d_vis, d_peel1=d1, m_peel1=m1, cls_first=c1, d_bg=db, m_bg=mb, sky=sky, m_fit=m_fit,
                        outer=meta['outer'], inner=meta['inner'], pn=meta['pn'], pw=pw, ph=ph)
    info = dict(scene=S, plate=[pw, ph], peel1_px=int(m1.sum()), bg_px=int(mb.sum()), own_only_px=int((m1 & ~mb).sum()), sky_reveal_px=int(sky.sum()),
                fit_px=int(m_fit.sum()), first_class_counts={int(k): int(v) for k, v in zip(*np.unique(c1[m1], return_counts=True))},
                d_peel1_median=float(np.nanmedian(d1)), d_vis_median=float(np.median(d_vis[np.isfinite(d_vis)])), outer=meta['outer'])
    json.dump(info, open(f'{od}/info.json', 'w'), indent=1); print(json.dumps(info))

if __name__ == '__main__':
    for S in sys.argv[1:]: build(S)
