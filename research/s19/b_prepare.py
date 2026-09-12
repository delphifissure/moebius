#!/usr/bin/env python3
"""B: working inputs per picture at <= 1280 px long side (the troll's scale): colour, the repo's 8-bit depth resampled, and DA3-Mono-Large 16-bit inverse depth."""
import sys, os, time, json, numpy as np
from PIL import Image
R = '/home/user/moebiusv2'; O = f'{R}/harness/batchB'; os.makedirs(O, exist_ok=True)
PICS = {'bristlecone': ('assets/bristleconeImg.png', 'assets/bristleconeDepth.png'), 'octopus': ('assets/octopusImg.png', 'assets/octopusDepth.png'),
        'room': ('roomImg1.png', 'roomDepth1.png'), 'silverwarrior': ('silverwarrior_color.png', 'silverwarrior_depth.png'),
        'starwatcher': ('starwatcher_color.png', 'starwatcher_depth.png'), 'vermeer': ('vermeer-milkmaid_orig.jpg', None)}
names = sys.argv[1:] or list(PICS)
LONG = 1280
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bakeoff'); sys.path.insert(0, f'{B}/Depth-Anything-3/src')
import torch; from depth_anything_3.api import DepthAnything3
torch.set_num_threads(4)
model = DepthAnything3.from_pretrained('depth-anything/DA3MONO-LARGE').to(device='cpu').eval()
log = {}
for n in names:
    # DA3 runs on the original picture (process_res 1008, upper-bound resize); the WORKING size is DA3's processed size, so the
    # depth map is never resampled (a bilinear upsample made the S9 sigma estimator read 0: half the second differences of a
    # piecewise-linear map are exactly zero). Colour and the repo's depth are resized to that size.
    c, d = PICS[n]; im = Image.open(f'{R}/{c}').convert('RGB'); W, H = im.size
    t0 = time.time()
    with torch.no_grad(): pred = model.inference([f'{R}/{c}'], process_res=1008, process_res_method='upper_bound_resize')
    a = np.asarray(pred.depth[0], dtype=np.float64); h, w = a.shape
    imw = im.resize((w, h), Image.LANCZOS); cp = f'{O}/{n}_color.png'; imw.save(cp)
    if d: Image.open(f'{R}/{d}').convert('L').resize((w, h), Image.LANCZOS).save(f'{O}/{n}_repo8.png')
    valid = np.isfinite(a) & (a > 0); inv = np.where(valid, 1.0 / np.maximum(a, 1e-9), 0.0); lo, hi = inv[valid].min(), inv[valid].max()
    d16 = np.round((inv - lo) / (hi - lo) * 65535).clip(0, 65535).astype(np.uint16); Image.fromarray(d16).save(f'{O}/{n}_da3_16.png')
    log[n] = dict(native=[W, H], working=[w, h], repo_depth=bool(d), da3_seconds=round(time.time() - t0, 1), distinct16=int(len(np.unique(d16))), note='working size = DA3 processed size; depth not resampled')
    print(n, log[n], flush=True)
lp = f'{O}/prepare_log.json'; old = json.load(open(lp)) if os.path.exists(lp) else {}; old.update(log); json.dump(old, open(lp, 'w'), indent=1)
