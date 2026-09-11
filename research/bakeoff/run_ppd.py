import sys, os, time, torch, cv2, numpy as np; B=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B); from common import *
os.chdir(f"{B}/pixel-perfect-depth"); sys.path.insert(0, os.getcwd())
import torch.nn.functional as F
from ppd.utils.set_seed import set_seed
from ppd.models.ppd import PixelPerfectDepth
set_seed(666); torch.set_num_threads(4)
model = PixelPerfectDepth(semantics_model="DA2", semantics_pth=f"{B}/ckpt/depth_anything_v2_vitl.pth", sampling_steps=4)
model.load_state_dict(torch.load(f"{B}/ckpt/ppd.pth", map_location="cpu"), strict=False); model = model.to(torch.device("cpu")).eval()
# CPU: the repo's infer_image autocasts to fp16/bf16 on CUDA; run the same steps in float32 here
image = cv2.imread(IMG); Hh, Ww = image.shape[:2]
from ppd.utils.transform import image2tensor, resize_keep_aspect
t0 = time.time(); rimg = resize_keep_aspect(image); x = image2tensor(rimg).to(model.device)
with torch.no_grad(): depth = model.forward_test(x)
depth = F.interpolate(depth, size=(Hh, Ww), mode="bilinear", align_corners=False)[0, 0].cpu().numpy()
save("ppd", depth, "depth", time.time() - t0, note=f"raw PPD output (4 steps, DA2 semantics, float32 on CPU); processed {rimg.shape[:2]}; sign checked offline")
