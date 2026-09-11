import sys, os, time, torch, cv2, numpy as np; B=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B); from common import *
from moge.model.v2 import MoGeModel
torch.set_num_threads(4); dev = torch.device("cpu")
model = MoGeModel.from_pretrained("Ruicheng/moge-2-vitl").to(dev).eval()
im = cv2.cvtColor(cv2.imread(IMG), cv2.COLOR_BGR2RGB); x = torch.tensor(im / 255, dtype=torch.float32, device=dev).permute(2, 0, 1)
t0 = time.time()
with torch.no_grad(): out = model.infer(x, fov_x=None, resolution_level=9, use_fp16=False)
d = out["depth"].cpu().numpy().astype(np.float64); m = out["mask"].cpu().numpy().astype(bool); d[~m] = np.inf
K = out["intrinsics"].cpu().numpy(); save("moge2", d, "depth", time.time() - t0, note=f"metres; valid={m.mean():.3f}; fx_norm={K[0,0]:.3f} (hfov {2*np.degrees(np.arctan(0.5/K[0,0])):.1f} deg)")
