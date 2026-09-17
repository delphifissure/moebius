"""S35 §25 score: the app's per-line fill vs the sheets' per-surface fill, on the same picture.
  CLONE: band texels whose fill is within the source noise of their OWN source colour (the occluder's) — the fill showing
         the foreground as background. Measured against the picture's own colour noise (MAD of first differences).
  STREAK: |dC| between neighbouring band texels ACROSS the lines (independent per-line reads in the app; one surface in the
         sheets), median / mean / p90.
  SMOOTH: the same along the lines, for reference.
Usage: score5.py <name> <streakclass dump> <app probe dump> <sheet out dir>"""
import sys, json, numpy as np
from PIL import Image
NAME, S, A, D = sys.argv[1:5]
ms = json.load(open(f'{S}/meta.json')); pw, ph = ms['pw'], ms['ph']
band = np.fromfile(f'{S}/disocc.u8', np.uint8).reshape(ph, pw) > 0
src = np.asarray(Image.open(f'{S}/color.png').convert('RGB')).astype(np.float32)
sheet = np.asarray(Image.open(f'{D}/color_stop.png').convert('RGB')).astype(np.float32)
ma = json.load(open(f'{A}/meta.json')); app = np.fromfile(f'{A}/plateColor.u8', np.uint8).reshape(ma['ph'], ma['pw'], 4)[..., :3].astype(np.float32)
if (ma['pw'], ma['ph']) != (pw, ph): app = np.asarray(Image.fromarray(app.astype(np.uint8)).resize((pw, ph), Image.NEAREST)).astype(np.float32)
noise = float(np.median(np.abs(np.diff(src, axis=1)).sum(2)) * 1.4826)
print(f'== {NAME}: band {int(band.sum())}, source colour noise (MAD of first differences, L1 over channels) {noise:.1f}')
for tag, f in (('app (per-line)', app), ('sheets (per-surface)', sheet)):
    d0 = np.abs(f - src).sum(2)[band]
    clone = (d0 <= noise).mean()
    dV = np.linalg.norm(f[1:, :] - f[:-1, :], axis=2)[band[1:, :] & band[:-1, :]]
    dH = np.linalg.norm(f[:, 1:] - f[:, :-1], axis=2)[band[:, 1:] & band[:, :-1]]
    print(f'   {tag:22s}: fill within the noise of its own source colour (a clone) on {100 * clone:5.1f} % of the band; '
          f'|dC| vertical median {np.median(dV):5.2f} mean {dV.mean():5.2f} p90 {np.percentile(dV, 90):5.2f}; horizontal median {np.median(dH):5.2f} mean {dH.mean():5.2f} p90 {np.percentile(dH, 90):5.2f}')
