#!/usr/bin/env python3
"""Sprint 18: DepthLab (Liu et al., Dec 2024; Apache-2.0) on the completed-layer pictures, CPU.
Input per picture: RGB (peel1 or bg), the KNOWN depth = the true visible depth on the texels whose colour is the
source picture's (m_fit), MASK = 1 on the hidden set + sky + anything without a finite depth. DepthLab returns
depth in the known depth's units (it normalises by the known min/max and de-normalises the output), so no
alignment is needed; ds_score.py still reports the visible-fit variant for comparability.
Settings: README defaults except denoise_steps 20 (README: 20-50 for DDIM), processing_res 768 (README: 640-768
for dense completion), strength 0.8, blend on, guidance 1, normalize_scale 1, seed 0. Everything fp32 on CPU (bf16 autocast
fails inside the reference-attention concat). Run with the depthlab venv python.
  python ds_depthlab.py S15 S2 ...   -> out/<S>/depthlab_{peel1,bg}.npy
"""
import sys, os, json, time, math
import numpy as np, torch
from PIL import Image
DL = '/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/depthlab'
sys.path.insert(0, f'{DL}/DepthLab-main')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); CK = f'{DL}/ckpt'; MG = f'{CK}/marigold-depth-v1-0'
STEPS = int(os.environ.get('DL_STEPS', 20)); RES = int(os.environ.get('DL_RES', 768)); STRENGTH = float(os.environ.get('DL_STRENGTH', 0.8)); TAG = os.environ.get('DL_TAG', ''); NAME = 'depthlab' + TAG
torch.set_num_threads(4); torch.manual_seed(0); np.random.seed(0)
from diffusers import DDIMScheduler, AutoencoderKL
from transformers import CLIPTextModel, CLIPTokenizer, CLIPVisionModelWithProjection, CLIPImageProcessor
from src.models.unet_2d_condition import UNet2DConditionModel
from src.models.unet_2d_condition_main import UNet2DConditionModel_main
from src.models.projection import My_proj
from inference.depthlab_pipeline import DepthLabPipeline
scenes = sys.argv[1:]; PICS = ('peel1', 'bg')
jobs = [(S, pic) for S in scenes for pic in PICS if not os.path.exists(f'{OUT}/{S}/{NAME}_{pic}.npy')]
if not jobs: print('nothing to do'); sys.exit(0)
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

# ---- 1. conditioning: CLIP-H image embeds through the mapping layer, and the empty-text embed (then free the encoders)
mapping = My_proj(); mapping.load_state_dict(torch.load(f'{CK}/DepthLab/mapping_layer.pth', map_location='cpu'), strict=False); mapping.eval()
img_enc = CLIPVisionModelWithProjection.from_pretrained(f'{CK}/clip-h-vision-fp16', torch_dtype=torch.float32).eval(); proc = CLIPImageProcessor()
tok = CLIPTokenizer.from_pretrained(MG, subfolder='tokenizer'); txt = CLIPTextModel.from_pretrained(MG, subfolder='text_encoder', variant='fp16', torch_dtype=torch.float32).eval()
with torch.no_grad():
    ids = tok('', padding='do_not_pad', max_length=tok.model_max_length, truncation=True, return_tensors='pt').input_ids
    uncond = txt(ids)[0][:, 0, :].unsqueeze(0)                                   # (1,1,1024)
    cond = {}
    for S, pic in jobs:
        im = Image.open(f'{OUT}/{S}/{pic}.png').convert('RGB')
        e = img_enc(proc.preprocess(im, return_tensors='pt').pixel_values).image_embeds.unsqueeze(1)
        cond[(S, pic)] = mapping(e)                                                # (1,1,1024)
del img_enc, txt; log('conditioning done for', len(jobs), 'pictures')

# ---- 2. the pipeline: UNets from Marigold's config, DepthLab's weights, bf16; VAE float32
cfg = json.load(open(f'{MG}/unet/config.json'))
den = UNet2DConditionModel_main.from_config({**cfg, 'in_channels': 12, 'sample_size': 96})
den.load_state_dict(torch.load(f'{CK}/DepthLab/denoising_unet.fp16.pth', map_location='cpu'), strict=False)
ref = UNet2DConditionModel.from_config({**cfg, 'in_channels': 4, 'sample_size': 96})
ref.load_state_dict(torch.load(f'{CK}/DepthLab/reference_unet.fp16.pth', map_location='cpu'))
den = den.float().eval(); ref = ref.float().eval()          # fp32 weights; the UNets run under CPU bf16 autocast (AMX)
vae = AutoencoderKL.from_pretrained(MG, subfolder='vae', variant='fp16', torch_dtype=torch.float32).eval()
sched = DDIMScheduler.from_pretrained(MG, subfolder='scheduler')
class Dummy(torch.nn.Module):
    device = torch.device('cpu'); dtype = torch.float32
pipe = DepthLabPipeline(reference_unet=ref, denoising_unet=den, mapping_layer=mapping, vae=vae, text_encoder=None, tokenizer=None, image_enc=Dummy(), scheduler=sched)
# the VAE stays in full fp32 (depth precision): its calls opt out of the autocast region
def _fp32(fn):
    def w(x):
        with torch.autocast('cpu', enabled=False): return fn(x.float())
    return w
pipe.decode_depth = _fp32(pipe.decode_depth); pipe.encode_depth = _fp32(pipe.encode_depth); pipe.encode_RGB = _fp32(pipe.encode_RGB)
from src.models.mutual_self_attention import ReferenceAttentionControl
log('pipeline ready')

def resize_to(a, W, H, nearest):
    return np.array(Image.fromarray(a).resize((W, H), Image.NEAREST if nearest else Image.BICUBIC))

with torch.no_grad():
    for S, pic in jobs:
        t = np.load(f'{OUT}/{S}/truth.npz'); pw, ph = int(t['pw']), int(t['ph'])
        hid = t['m_peel1'] if pic == 'peel1' else t['m_bg']
        known = t['m_fit'] & np.isfinite(t['d_vis']); mask = ~known                  # 1 = predict
        # as infer.py does before calling the pipeline (get_filled_for_latents): the unknown region of the known-depth map
        # is filled with the NEAREST known value, so the depth latent carries no artificial near value in the holes.
        # (The first run of this driver left zeros there; DepthLab then read every hole as 'nearest possible'. Rerun.)
        from scipy import ndimage
        idx = ndimage.distance_transform_edt(~known, return_distances=False, return_indices=True)
        dknown = t['d_vis'][tuple(idx)].astype(np.float32); dknown[~np.isfinite(dknown)] = float(np.nanmax(np.where(known, t['d_vis'], np.nan)))
        im = Image.open(f'{OUT}/{S}/{pic}.png').convert('RGB')
        s = min(RES / pw, RES / ph); W = int(pw * s) // 8 * 8; H = int(ph * s) // 8 * 8
        rgb = np.asarray(im.resize((W, H), Image.BICUBIC)).astype(np.float32) / 255 * 2 - 1
        m_r = resize_to(mask.astype(np.uint8), W, H, True).astype(np.float32)
        d_r = resize_to(dknown, W, H, True).astype(np.float32)
        image = torch.from_numpy(rgb.transpose(2, 0, 1))[None]; depth = torch.from_numpy(d_r)[None, None]; mk = torch.from_numpy(m_r)[None, None]
        ehs = torch.cat([uncond, cond[(S, pic)]], 0)
        writer = ReferenceAttentionControl(ref, do_classifier_free_guidance=True, mode='write', batch_size=1, fusion_blocks='full')
        reader = ReferenceAttentionControl(den, do_classifier_free_guidance=True, mode='read', batch_size=1, fusion_blocks='full')
        t0 = time.time(); torch.manual_seed(0)
        if True:   # fp32 throughout: CPU bf16 autocast trips on the reference-attention concat
          pred, vmax, vmin = pipe.single_infer(image=image, depth=depth, mask=mk, num_inference_steps=STEPS, show_pbar=False, guidance_scale=1, encoder_hidden_states=ehs,
                                               reference_control_writer=writer, reference_control_reader=reader, strength=STRENGTH, blend=True, normalize_scale=1, generator=None)
        d = (pred.float() * (vmax - vmin) + vmin).squeeze().cpu().numpy().astype(np.float32)
        d = np.array(Image.fromarray(d, mode='F').resize((pw, ph), Image.BILINEAR), np.float32).clip(min=0)
        np.save(f'{OUT}/{S}/{NAME}_{pic}.npy', d)
        e = np.abs(d - t['d_vis'])[known]
        log(NAME, S, pic, f'{time.time()-t0:.0f}s', f'visible median |err| {np.median(e):.4f} m, hidden median pred {np.median(d[hid]):.3f} m')
print('DONE depthlab', flush=True)
