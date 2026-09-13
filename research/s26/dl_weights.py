#!/usr/bin/env python3
"""Fetch DepthLab's weights within the session's disk allowance: Marigold's fp16 VAE / text encoder + configs, the CLIP-H
image tower converted to fp16 (the 3.9 GB full CLIP file is deleted after conversion), and DepthLab's two UNet state
dicts converted to fp16 one at a time (each 3.46 GB original deleted after conversion). Writes to ./ckpt."""
import os, sys, shutil, torch, time
from huggingface_hub import hf_hub_download, snapshot_download
B = os.path.dirname(os.path.abspath(__file__)); CK = f'{B}/ckpt'; os.makedirs(CK, exist_ok=True)
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
# 1. Marigold pieces (no UNet weights: the UNets are built from the config and filled from DepthLab's state dicts)
mg = f'{CK}/marigold-depth-v1-0'
if not os.path.exists(f'{mg}/vae/diffusion_pytorch_model.fp16.safetensors'):
    snapshot_download('prs-eth/marigold-depth-v1-0', local_dir=mg, allow_patterns=['model_index.json', 'scheduler/*', 'tokenizer/*', 'unet/config.json',
                      'vae/config.json', 'vae/diffusion_pytorch_model.fp16.safetensors', 'text_encoder/config.json', 'text_encoder/model.fp16.safetensors'])
    log('marigold pieces done')
# 2. CLIP-H vision tower with projection, fp16
ce = f'{CK}/clip-h-vision-fp16'
if not os.path.exists(f'{ce}/config.json'):
    from transformers import CLIPVisionModelWithProjection
    src = f'{CK}/clip-h-full'
    snapshot_download('laion/CLIP-ViT-H-14-laion2B-s32B-b79K', local_dir=src, allow_patterns=['config.json', 'model.safetensors', 'preprocessor_config.json'])
    log('clip full downloaded')
    m = CLIPVisionModelWithProjection.from_pretrained(src, torch_dtype=torch.float16); m.save_pretrained(ce)
    shutil.copy(f'{src}/preprocessor_config.json', f'{ce}/preprocessor_config.json'); del m; shutil.rmtree(src); log('clip vision fp16 saved')
# 3. DepthLab state dicts
dl = f'{CK}/DepthLab'; os.makedirs(dl, exist_ok=True)
if not os.path.exists(f'{dl}/mapping_layer.pth'):
    p = hf_hub_download('Johanan0528/DepthLab', 'mapping_layer.pth'); shutil.copy(p, f'{dl}/mapping_layer.pth'); log('mapping layer')
for name in ('reference_unet', 'denoising_unet'):
    if os.path.exists(f'{dl}/{name}.fp16.pth'): continue
    p = hf_hub_download('Johanan0528/DepthLab', f'{name}.pth', local_dir=f'{CK}/tmp'); log(name, 'downloaded')
    sd = torch.load(p, map_location='cpu'); sd = {k: (v.half() if torch.is_floating_point(v) else v) for k, v in sd.items()}
    torch.save(sd, f'{dl}/{name}.fp16.pth'); del sd; os.remove(p); log(name, 'fp16 saved')
shutil.rmtree(f'{CK}/tmp', ignore_errors=True)
log('WEIGHTS_DONE')
