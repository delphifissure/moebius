"""R6 item 2 / S35 §59: Amodal Depth Anything (ICCV 2025, Amodal-DAV2, MIT) scored on our kit truth.

The question R6 raised: the amodal-depth literature is object-centric (ADIW is built by compositing OBJECTS), and our target is
the opposite kind of region -- a forest, a field, a ground continuing behind a figure. Does it transfer? L5 and L6 can say.

Interface, as `infer.py` uses it: the model takes rgb (518x518), a binary GUIDE MASK (the amodal extent of the target, scaled
to [-1, 1]) and an OBSERVATION depth (relative, near = high, min-max normalised, scaled to [-1, 1]), and returns a relative
depth; `infer.py` then keeps the observation outside the mask and the prediction inside it. We supply our own observation (the
kit's own rest depth, which is what the app is given) rather than their base DAV2, so no second checkpoint is needed, and we
invert our own min-max to bring the prediction back into the app's normalised d -- which is exactly the scale-and-shift
alignment to the observed map that the paper specifies.

Mask arms (the load-bearing unknown: what counts as "the amodal extent" when the target is stuff):
  occ    the occluder's silhouette alone -- the hidden region, no visible target inside the mask
  collar the silhouette dilated by the band's own width, so the mask also holds a rim of the visible background
  frame  the whole frame (the background's true amodal extent; out of the model's training distribution)

  amodal_probe.py <scene> <probe dir> <occluder ids png> [--arms occ,collar,frame]
"""
import sys, os, json, argparse
import numpy as np
from PIL import Image
from scipy import ndimage

ADA = '/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/ada'
ap = argparse.ArgumentParser(); ap.add_argument('scene'); ap.add_argument('probe'); ap.add_argument('occ')
ap.add_argument('--arms', default='occ,collar,frame'); A = ap.parse_args()
K = '/home/user/moebiusv2/harness/truthkit/out'; S = A.scene
meta = json.load(open(f'{A.probe}/meta.json')); pw, ph = meta['pw'], meta['ph']; outer, pn = meta['outer'], meta['pn']
band = np.fromfile(f'{A.probe}/disocc.u8', np.uint8).reshape(ph, pw) > 0
rgb = np.asarray(Image.open(f'{K}/{S}/rest_rgb.png').convert('RGB'))
dep16 = np.asarray(Image.open(f'{K}/{S}/rest_depth16.png'))
if dep16.ndim == 3: dep16 = dep16[..., 0]
occ = np.asarray(Image.open(A.occ)); occ = occ[..., 0] if occ.ndim == 3 else occ
assert rgb.shape[:2] == (ph, pw) and dep16.shape == (ph, pw) and occ.shape == (ph, pw), (rgb.shape, dep16.shape, occ.shape, (ph, pw))
d_obs = dep16.astype(np.float64) / 65535.0                      # the app's normalised d: 0 far, higher nearer -- the same polarity the model expects
dmin, dmax = float(d_obs.min()), float(d_obs.max()); rng = max(1e-9, dmax - dmin)
obs_n = (d_obs - dmin) / rng
# truth: the kit's first hidden layer
z = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = z['cls']; w = z['w_disp']; dep = z['depth']
H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
cls = cls[y0:y0 + ph, x0:x0 + pw]; w = w[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]
v_ = (cls >= 2) & (cls <= 5) & (w > 0); has = v_.any(-1); kk = np.argmax(v_, -1)
dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; dT = np.where(has & np.isfinite(dT), dT, np.nan)
cT = np.take_along_axis(cls, kk[..., None], -1)[..., 0]
depth_of_d = lambda d: outer * (1 - np.clip(d / pn, 0, 1) ** 2 * (3 - 2 * np.clip(d / pn, 0, 1)))
occB = occ > 0
reach = int(np.ceil(ndimage.distance_transform_edt(band).max()))   # the band's own half-width: the collar's width, data-derived
masks = {}
if 'occ' in A.arms: masks['occ'] = occB
if 'collar' in A.arms: masks['collar'] = ndimage.binary_dilation(occB, iterations=max(1, reach))
if 'frame' in A.arms: masks['frame'] = np.ones((ph, pw), bool)
print(f'{S}: {pw}x{ph}; band {int(band.sum())}; occluder {int(occB.sum())} texels; band half-width {reach}; observation d range {dmin:.3f}..{dmax:.3f}')

sys.path.insert(0, ADA)
import torch
import torch.nn.functional as F
from torchvision.transforms import InterpolationMode, Resize
from src.models.amodalsynthdrive.dav2 import AmodalDAv2
torch.set_grad_enabled(False)
model = AmodalDAv2(encoder='vitl', pretrained=False).from_pretrained('Zhyever/Amodal-Depth-Anything-DAV2', strict=True).eval()
rs = Resize(size=(518, 518), interpolation=InterpolationMode.NEAREST)
rgb_ts = rs(torch.tensor(rgb).permute(2, 0, 1).unsqueeze(0).float() / 255)
obs_ts = rs(torch.tensor(obs_n).unsqueeze(0).unsqueeze(0).float())
t = band & np.isfinite(dT)
print(f'   band texels with a first hidden layer: {int(t.sum())}; truth classes ' + str({int(c): int((t & (cT == c)).sum()) for c in np.unique(cT[t])}))
for name, m in masks.items():
    m_ts = rs(torch.tensor(m).float().unsqueeze(0).unsqueeze(0)); m_ts = (m_ts > 0).float()
    pred = model(rgb_ts, guide_rgb=None, guide_mask=m_ts * 2 - 1, observation=obs_ts * 2 - 1)
    p = F.interpolate(pred.squeeze().unsqueeze(0).unsqueeze(0), (ph, pw), mode='bilinear', align_corners=False).squeeze().numpy()
    d_pred = np.clip(p, 0, 1) * rng + dmin                       # back into the app's d by the observation's own scale and shift
    e = np.abs(depth_of_d(d_pred) - dT)
    row = f'  mask={name:6s}: whole band |e| median {np.nanmedian(e[t]):.4f} m'
    for c, nm in ((2, 'bg'), (3, 'thing'), (4, 'own side'), (5, 'own interior')):
        mm = t & (cT == c)
        if mm.sum() >= 200: row += f' | {nm} {np.nanmedian(e[mm]):.4f} (n {int(mm.sum())})'
    print(row)
    print(f'     predicted d in the band p10/50/90 {np.percentile(d_pred[band], [10, 50, 90]).round(3)}; the truth there, as d p50 {np.nanmedian(d_obs[band]):.3f} (occluder) ')
    np.save(f'{A.probe}/amodal_{name}.npy', d_pred.astype(np.float32))
