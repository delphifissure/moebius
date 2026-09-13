#!/usr/bin/env python3
"""Sprint 18 step 2: run a depth model on the truth-kit pictures (rest = the source picture, the control;
peel1 / bg = the completed-layer pictures) and store the raw output at plate resolution.
  python3 ds_run.py da3 S15 S2 ...      -> out/<S>/da3_<pic>.npy   (DA3-Mono-Large, CPU, process_res 1008 as in the S8 bake-off)
  python3 ds_run.py moge3 S15 S2 ...    -> out/<S>/moge3_<pic>.npy (+ _mask.npy; MoGe-3 ViT-L, fov_x unknown, refine 3)
Raw output only; alignment and scoring are in ds_score.py. Appends timings to out/timing.json.
"""
import sys, os, json, time
import numpy as np
from PIL import Image
B = '/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/bakeoff'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
PICS = ('rest', 'peel1', 'bg')
model_name = sys.argv[1]; scenes = sys.argv[2:]
import torch; torch.set_num_threads(4)
tl = f'{OUT}/timing.json'; T = json.load(open(tl)) if os.path.exists(tl) else {}

def log(S, pic, sec, extra=''):
    T[f'{model_name}/{S}/{pic}'] = round(sec, 1); json.dump(T, open(tl, 'w'), indent=1); print(model_name, S, pic, f'{sec:.1f}s', extra, flush=True)

if model_name == 'da3':
    sys.path.insert(0, f'{B}/Depth-Anything-3/src')
    from depth_anything_3.api import DepthAnything3
    model = DepthAnything3.from_pretrained('depth-anything/DA3MONO-LARGE').to(device='cpu').eval()
    for S in scenes:
        for pic in PICS:
            p = f'{OUT}/{S}/{pic}.png'; o = f'{OUT}/{S}/da3_{pic}.npy'
            if os.path.exists(o): continue
            t0 = time.time()
            with torch.no_grad(): pred = model.inference([p], process_res=1008, process_res_method='upper_bound_resize')
            d = np.asarray(pred.depth[0], np.float32); W, H = Image.open(p).size
            if d.shape != (H, W): d = np.array(Image.fromarray(d, mode='F').resize((W, H), Image.BILINEAR), np.float32)
            np.save(o, d); log(S, pic, time.time() - t0, f'range {d.min():.3f}..{d.max():.3f}')
elif model_name == 'moge3':
    sys.path.insert(0, f'{B}/MoGe')
    # MoGe-3's sparse 3D refiner needs FlexGEMM (CUDA/Triton kernels, no CPU build): stub its import, build the model
    # WITHOUT the refiner and run refine_steps=0 = MoGe-3's base (pre-refinement) prediction. Labelled as such.
    import types
    fg = types.ModuleType('flex_gemm'); fgnn = types.ModuleType('flex_gemm.nn'); fgops = types.ModuleType('flex_gemm.ops')
    class _Stub(torch.nn.Module):
        def __init__(self, *a, **k): super().__init__()
    for n in ('SubmanifoldConv3d', 'SparsePool3d', 'SparseUpsample3d'): setattr(fgnn, n, _Stub)
    fgops.NeighborCache = _Stub; fg.nn = fgnn; fg.ops = fgops
    sys.modules.update({'flex_gemm': fg, 'flex_gemm.nn': fgnn, 'flex_gemm.ops': fgops})
    from moge.model.v3 import MoGeModel
    from huggingface_hub import hf_hub_download
    ck = torch.load(hf_hub_download('Ruicheng/moge-3-vitl', 'model.pt'), map_location='cpu', weights_only=True)
    cfg = dict(ck['model_config']); cfg.pop('refiner', None); cfg.pop('refiner_depth_resolution', None)
    model = MoGeModel(**cfg); missing, unexpected = model.load_state_dict(ck['model'], strict=False)
    print('moge3 base model: missing', len(missing), 'unexpected (refiner)', len(unexpected), flush=True); model = model.to('cpu').eval()
    for S in scenes:
        for pic in PICS:
            p = f'{OUT}/{S}/{pic}.png'; o = f'{OUT}/{S}/moge3_{pic}.npy'
            if os.path.exists(o): continue
            im = np.array(Image.open(p).convert('RGB')); x = torch.tensor(im / 255, dtype=torch.float32).permute(2, 0, 1)
            t0 = time.time()
            with torch.no_grad(): out = model.infer(x, fov_x=None, resolution_level=9, refine_steps=0, use_fp16=False)
            d = out['depth'].cpu().numpy().astype(np.float32); m = out['mask'].cpu().numpy().astype(bool)
            K = out['intrinsics'].cpu().numpy(); np.save(o, d); np.save(o.replace('.npy', '_mask.npy'), m)
            log(S, pic, time.time() - t0, f'valid {m.mean():.3f} hfov {2*np.degrees(np.arctan(0.5/K[0,0])):.1f} range {d[m].min():.3f}..{d[m].max():.3f}')
print('DONE', model_name, flush=True)
