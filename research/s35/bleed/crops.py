"""Crop comparison of the fill across arms. crops.py <out.png> <color.png> <y0> <y1> <x0> <x1> <tag=dir> ..."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
OUT, C = sys.argv[1], sys.argv[2]; y0, y1, x0, x1 = map(int, sys.argv[3:7]); arms = [a.split('=', 1) for a in sys.argv[7:]]
meta = json.load(open(f'{arms[0][1]}/meta.json')); pw, ph = meta['pw'], meta['ph']
dQ = np.fromfile(f'{arms[0][1]}/dQ.f32', np.float32).reshape(ph, pw); dis = np.fromfile(f'{arms[0][1]}/disocc.u8', np.uint8).reshape(ph, pw) > 0
im = Image.open(C).convert('RGB'); col = np.asarray(im if im.size == (pw, ph) else im.resize((pw, ph), Image.BILINEAR))
edge = dis & ~(np.roll(dis, 1, 1) & np.roll(dis, -1, 1) & np.roll(dis, 1, 0) & np.roll(dis, -1, 0))
def gam(d): return (np.clip(d, 0, 1) ** 0.5 * 255).astype(np.uint8)
panels = [('colour + band edge', np.where(edge[..., None], np.array([255, 0, 0], np.uint8), col)), ('depth', np.stack([gam(dQ)] * 3, -1))]
for t, d in arms:
    pc = np.fromfile(f'{d}/plateColor.u8', np.uint8).reshape(ph, pw, 4)[..., :3].copy(); pc[~dis] //= 3
    panels.append((t + ' fill', pc))
scale = max(1, min(6, 1400 // max(1, (x1 - x0) * len(panels))))
W = (x1 - x0) * scale; H = (y1 - y0) * scale
sheet = Image.new('RGB', (W * len(panels) + 10 * (len(panels) - 1), H + 16), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
for k, (n, a) in enumerate(panels):
    sheet.paste(Image.fromarray(np.ascontiguousarray(a[y0:y1, x0:x1])).resize((W, H), Image.NEAREST), (k * (W + 10), 16)); dr.text((k * (W + 10) + 3, 2), n, fill=(255, 255, 0))
sheet.save(OUT); print('wrote', OUT, sheet.size)
