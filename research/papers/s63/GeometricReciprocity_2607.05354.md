Title: Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation

URL Source: https://arxiv.org/html/2607.05354

Published Time: Tue, 07 Jul 2026 02:33:48 GMT

Markdown Content:
###### Abstract

Monocular-to-stereo conversion synthesizes stereoscopic content from 2D videos for immersive 3D experiences. In modern Depth-Image-Based Rendering (DIBR) approaches, stereo inpainting of disocclusions is the critical bottleneck. Training-based methods achieve superior quality but rely on scarce stereo pairs or synthetic data with domain gaps. We address this through the first self-supervised framework learning from monocular videos via cycle consistency. Our key contribution is the Geometric Reciprocity Theorem (GRT): under the nearest-neighbor DIBR formulation, the disocclusion mask when synthesizing a target view equals the mask of pixels lost when warping back from target to source, enabling analytical computation of test-time disocclusion masks directly from monocular images. This yields train-test consistency for the stated warping formulation, supporting self-supervised learning from unlimited monocular videos and substantial improvements over training-free and supervised state-of-the-art methods. Project page: [https://visual-ai.github.io/grt/](https://visual-ai.github.io/grt/)

Stereoscopic Video Generation, Self-Supervised Learning, Geometric Consistency

## 1 Introduction

The demand for immersive 3D experiences on VR/AR devices, 3D cinema, and stereoscopic displays has made stereoscopic video generation a fundamental problem. The task is to convert monocular videos to stereoscopic format by synthesizing one view from the other (conventionally right-eye from left-eye, or vice versa).

Modern approaches predominantly adopt the Depth-Image-Based Rendering (DIBR) framework(Wang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib5 "Stereodiffusion: training-free stereo image generation using latent diffusion models"); Shi et al., [2024](https://arxiv.org/html/2607.05354#bib.bib4 "StereoCrafter-Zero: zero-shot stereo video generation with noisy restart"); Dai et al., [2024](https://arxiv.org/html/2607.05354#bib.bib7 "SVG: 3D stereoscopic video generation via denoising frame matrix"); Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos"); Huang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib6 "ReStereo: diffusion stereo video generation and restoration"); Shvetsova et al., [2026](https://arxiv.org/html/2607.05354#bib.bib2 "M2SVid: end-to-end inpainting and refinement for monocular-to-stereo video conversion")), which decomposes the problem into three sequential stages: estimating depth from the input frame, warping the image to synthesize an initial target view, and inpainting the resulting disocclusions. These disocclusions are regions newly visible in the target view that were occluded in the source, creating geometrically structured missing patterns that general-purpose inpainting methods cannot handle (see [Appendix A7](https://arxiv.org/html/2607.05354#A7 "Appendix A7 Discussion of General Inpainting Models ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")). This domain gap has made the stereo inpainting stage the critical bottleneck.

Due to the scarcity of training data, recent training-free methods(Wang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib5 "Stereodiffusion: training-free stereo image generation using latent diffusion models"); Dai et al., [2024](https://arxiv.org/html/2607.05354#bib.bib7 "SVG: 3D stereoscopic video generation via denoising frame matrix")) manipulate pretrained diffusion models for zero-shot stereo inpainting, but lack stereo-specific geometric priors and produce inferior results. Training-based approaches(Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos"); Huang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib6 "ReStereo: diffusion stereo video generation and restoration"); Shvetsova et al., [2026](https://arxiv.org/html/2607.05354#bib.bib2 "M2SVid: end-to-end inpainting and refinement for monocular-to-stereo video conversion")) learn these priors yet face a fundamental challenge in training data quality and availability. Existing methods either rely on scarce and often proprietary real stereo pairs with error-prone stereo matching for disocclusion identification(Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos"); Shvetsova et al., [2026](https://arxiv.org/html/2607.05354#bib.bib2 "M2SVid: end-to-end inpainting and refinement for monocular-to-stereo video conversion")), or resort to synthetic data that suffers from inevitable domain gaps(Huang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib6 "ReStereo: diffusion stereo video generation and restoration")) (see [Appendix A8](https://arxiv.org/html/2607.05354#A8 "Appendix A8 Training Data Challenges ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") for more details).

To address the data bottleneck, we propose the first self-supervised framework that learns stereo inpainting from monocular videos alone, eliminating the need for stereo pairs or synthetic data. Our approach exploits the inherent bidirectional symmetry of stereo view relationships, enabling right-left-right cycle consistency where generating the left view from right through DIBR and then reconstructing the right from the synthesized left should recover the original input.

Table 1: Comparison of training data construction approaches. Our Geometric Reciprocity Theorem enables constructing scalable, high-quality training data with train-inference consistent masks from arbitrary real-world monocular videos.

While cycle consistency provides self-supervision in principle, naive implementation requires multiple sequential model inferences and backpropagation through non-differentiable warping operations, making video-scale training computationally prohibitive. We resolve this through a geometric insight: the stereo warping process itself encodes all information needed to compute cycle consistency losses without executing the cycle. Through rigorous geometric analysis, we discover that in the right-left-right cycle, the intermediate steps of inpainting the left view, estimating its depth, and performing pixel warping operations are redundant under the nearest-neighbor DIBR formulation. We formalize this as the Geometric Reciprocity Theorem (GRT): for any right (target) view to be synthesized from a left (source) view, the disocclusion mask required equals the mask of pixels that would be lost when warping back from target to source. This theorem reveals that the cycle consistency supervision signal can be computed analytically from the target view alone using only its depth estimate, with no synthesis, no intermediate views, and no cycling required.

GRT fundamentally transforms training data construction. By treating any monocular image as a target view, we directly compute its _inference-time_ disocclusion mask via GRT, yielding the mask induced by the same DIBR geometry used at test time. The image itself then serves as ground truth for these disocclusions, enabling self-supervised training from unlimited monocular videos with train-inference consistency that substantially outperforms both training-free methods and supervised state-of-the-art. We summarize the above comparisons in [Table 1](https://arxiv.org/html/2607.05354#S1.T1 "In 1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation").

Our contributions are: (1) the first self-supervised stereo inpainting framework learning from monocular videos without requiring stereo pairs or synthetic data, (2) the Geometric Reciprocity Theorem enabling analytical cycle consistency computation without executing the cycle, (3) the first comprehensive datasets (ImageNet-GRT, Kinetics-GRT, and DAVIS-GRT) with geometrically consistent disocclusion masks for training and evaluation, and (4) state-of-the-art performance surpassing both training-free and supervised methods. Code, precomputed masks, and trained weights will be released at [https://github.com/Visual-AI/GRT](https://github.com/Visual-AI/GRT).

## 2 Related work

### 2.1 Monocular-to-Stereo Video Conversion

Monocular-to-stereo video conversion synthesizes a right-eye view from standard 2D video (assumed as left-eye input) for immersive 3D experiences on stereoscopic displays, 3D cinemas, and VR/AR devices. Early work (Xie et al., [2016](https://arxiv.org/html/2607.05354#bib.bib1 "Deep3d: fully automatic 2d-to-3d video conversion with deep convolutional neural networks")) attempted direct regression using end-to-end CNNs but was limited by lack of robust depth priors. Modern approaches predominantly adopt Depth-Image-Based Rendering (DIBR), which first estimates per-frame depth maps with pretrained models like Depth Anything (Yang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib11 "Depth anything: unleashing the power of large-scale unlabeled data")), then warps the left view to synthesize an initial right view. This warping uncovers disocclusions—areas occluded in the left view—framing monocular-to-stereo conversion as stereo inpainting: filling newly visible regions.

Recent solutions tackle this challenge in various ways. Training-free methods leverage pretrained models without fine-tuning. StereoDiffusion(Wang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib5 "Stereodiffusion: training-free stereo image generation using latent diffusion models")) performs zero-shot inpainting by manipulating latents in pretrained image diffusion models. StereoCrafter-Zero(Shi et al., [2024](https://arxiv.org/html/2607.05354#bib.bib4 "StereoCrafter-Zero: zero-shot stereo video generation with noisy restart")) uses noisy restart and iterative refinement on video diffusion models. SVG(Dai et al., [2024](https://arxiv.org/html/2607.05354#bib.bib7 "SVG: 3D stereoscopic video generation via denoising frame matrix")) contributes a Frame Matrix architecture for video consistency while remaining training-free.

Training-based methods demonstrate superior quality and consistency by learning stereo-specific priors from datasets. StereoCrafter(Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos")) fine-tunes Stable Video Diffusion using auto-regressive strategies for temporal coherence. Restereo(Huang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib6 "ReStereo: diffusion stereo video generation and restoration")) jointly addresses stereo generation and video restoration via training on synthetically degraded data. M2SVid(Shvetsova et al., [2026](https://arxiv.org/html/2607.05354#bib.bib2 "M2SVid: end-to-end inpainting and refinement for monocular-to-stereo video conversion")) improves efficiency through single-step feed-forward prediction conditioned on both original left and warped right views. However, without ready-to-use stereo inpainting datasets, these methods construct training data through preprocessing pipelines. Methods using real stereo pairs face stereo matching errors and copyright restrictions, while those using synthetic data face domain gaps between rendered and real videos, limiting generalization.

### 2.2 Monocular Depth Estimation

Monocular Depth Estimation (MDE) infers dense depth maps from single images. Early methods trained on single-domain datasets like KITTI(Geiger et al., [2012](https://arxiv.org/html/2607.05354#bib.bib8 "Are we ready for autonomous driving? the kitti vision benchmark suite")) or NYU-D(Silberman et al., [2012](https://arxiv.org/html/2607.05354#bib.bib9 "Indoor segmentation and support inference from rgbd images")) performed well in specific scenarios but lacked generalization. Recent foundation models achieve zero-shot capabilities through multi-dataset aggregation (MiDaS(Ranftl et al., [2020](https://arxiv.org/html/2607.05354#bib.bib10 "Towards robust monocular depth estimation: mixing datasets for zero-shot cross-dataset transfer"))) and massive unlabeled datasets (Depth Anything(Yang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib11 "Depth anything: unleashing the power of large-scale unlabeled data")), DepthPro(Bochkovskii et al., [2025](https://arxiv.org/html/2607.05354#bib.bib12 "Depth pro: sharp monocular metric depth in less than a second"))). Advances include generative models like Marigold(Ke et al., [2024](https://arxiv.org/html/2607.05354#bib.bib13 "Repurposing diffusion-based image generators for monocular depth estimation")), Vision Transformer architectures(Ranftl et al., [2021](https://arxiv.org/html/2607.05354#bib.bib14 "Vision transformers for dense prediction")), and robustness improvements under adverse conditions(Kong et al., [2023](https://arxiv.org/html/2607.05354#bib.bib15 "RoboDepth: robust out-of-distribution depth estimation under corruptions"); Zheng et al., [2023](https://arxiv.org/html/2607.05354#bib.bib16 "STEPS: joint self-supervised nighttime image enhancement and depth estimation"); Sun et al., [2025](https://arxiv.org/html/2607.05354#bib.bib17 "Depth anything at any condition")). For DIBR-based monocular-to-stereo conversion, predicted depth maps govern warping by defining per-pixel horizontal displacement, with closer objects shifted more than distant ones to create stereoscopic effects.

### 2.3 Cycle Consistency

Cycle consistency enables unsupervised learning by enforcing bidirectional consistency (A\to B\to A). CycleGAN(Zhu et al., [2017](https://arxiv.org/html/2607.05354#bib.bib18 "Unpaired image-to-image translation using cycle-consistent adversarial networks")) demonstrated this for unpaired image-to-image translation. Applications span domain adaptation(Hoffman et al., [2018](https://arxiv.org/html/2607.05354#bib.bib19 "CyCADA: cycle-consistent adversarial domain adaptation"); Singh, [2021](https://arxiv.org/html/2607.05354#bib.bib24 "CLDA: contrastive learning for semi-supervised domain adaptation")), temporal learning(Dwibedi et al., [2019](https://arxiv.org/html/2607.05354#bib.bib20 "Temporal cycle-consistency learning"); Yang et al., [2021](https://arxiv.org/html/2607.05354#bib.bib21 "Self-supervised video object segmentation by motion grouping")), 3D dense correspondence(Zhou et al., [2016](https://arxiv.org/html/2607.05354#bib.bib22 "Learning dense correspondence via 3d-guided cycle consistency")), and super-resolution(Yuan et al., [2018](https://arxiv.org/html/2607.05354#bib.bib23 "Unsupervised image super-resolution using cycle-in-cycle generative adversarial networks")). TrajectoryCrafter(Yu et al., [2025a](https://arxiv.org/html/2607.05354#bib.bib35 "TrajectoryCrafter: redirecting camera trajectory for monocular videos via diffusion models")) extends cycle consistency to multi-view synthesis through explicit forward-backward reprojection, requiring two full rendering passes. In contrast, our GRT reveals the analytical redundancy in this cycle and enables direct disocclusion mask derivation from target-view geometry alone.

## 3 Method

We present a self-supervised approach for training stereo inpainting networks using monocular videos (images). Building on the DIBR framework ([Section 3.1](https://arxiv.org/html/2607.05354#S3.SS1 "3.1 Preliminaries ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")), we identify data scarcity and domain gaps as key bottlenecks ([Section 3.2](https://arxiv.org/html/2607.05354#S3.SS2 "3.2 Motivation ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")). We introduce cycle consistency ([Section 3.3](https://arxiv.org/html/2607.05354#S3.SS3 "3.3 Cycle Consistency ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")) as a self-supervision mechanism and prove the Geometric Reciprocity Theorem (GRT) ([Section 3.4](https://arxiv.org/html/2607.05354#S3.SS4 "3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")), which eliminates the computational overhead of cycle consistency while preserving equivalent geometric constraints, enabling self-supervised learning from monocular videos (images) without requiring paired stereo data ([Section 3.5](https://arxiv.org/html/2607.05354#S3.SS5 "3.5 Model Architecture ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")).

### 3.1 Preliminaries

Stereoscopic video generation synthesizes stereo pairs from monocular input for immersive 3D visualization. Given a monocular frame as the left-eye view I_{L}, the task is to generate the corresponding right-eye view I_{R}. While the reverse direction is equally valid, we adopt the left-to-right formulation for clarity. Modern approaches employ the Depth-Image-Based Rendering (DIBR) framework, which reduces stereoscopic generation to a stereo inpainting problem. First, a depth estimation model \mathcal{D} predicts disparity, which is inversely proportional to depth:

d_{L}=\mathcal{D}(I_{L}),\quad d_{L}=\frac{bf}{Z_{L}},(1)

where d_{L}(x,y) denotes the disparity at pixel (x,y), Z_{L}(x,y) is the corresponding depth, b is the baseline, and f is the focal length. We adopt the convention that disparity values are positive, with larger values indicating closer objects. Second, warping projects the input to the target viewpoint. Specifically, W_{L\to R} establishes pixel correspondences between views. For each pixel (x,y) in the left view, its corresponding position (x^{\prime},y^{\prime}) in the right view is computed as:

x^{\prime}=x-d_{L}(x,y),\quad y^{\prime}=y,(2)

where the horizontal coordinate is shifted by the disparity value, while the vertical coordinate remains unchanged due to rectified stereo geometry. During warping, multiple source pixels may map to the same target location (collision), or some target pixels may receive no mapping (disocclusion). The warping operation outputs the warped image \tilde{I}_{R} and the disocclusion mask M_{\text{dis}}^{L\to R}:

\tilde{I}_{R},M_{\text{dis}}^{L\to R}=W_{L\to R}(I_{L},d_{L}),(3)

where M_{\text{dis}}^{L\to R}(x,y)=1 indicates pixels that are disoccluded in \tilde{I}_{R} and require inpainting. Third, a stereo inpainting network fills these holes:

\hat{I}_{R}=G(\tilde{I}_{R},M_{\text{dis}}^{L\to R}),(4)

where G represents the stereo inpainting network.

### 3.2 Motivation

The primary bottleneck in DIBR-based stereoscopic generation is training the stereo inpainting network G, stemming from the unique characteristics of stereoscopic disocclusion patterns and the scarcity of suitable training data.

Domain gap in disocclusion patterns. Stereoscopic disocclusion masks M_{\text{dis}}^{L\to R} exhibit geometrically structured patterns fundamentally different from typical inpainting masks (random strokes, rectangular regions, or object instances). This domain gap causes general inpainting methods and training-free methods(Wang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib5 "Stereodiffusion: training-free stereo image generation using latent diffusion models"); Dai et al., [2024](https://arxiv.org/html/2607.05354#bib.bib7 "SVG: 3D stereoscopic video generation via denoising frame matrix")) to produce suboptimal results, lacking stereo-specific geometric priors for plausible disocclusion filling.

![Image 1: Refer to caption](https://arxiv.org/html/2607.05354v1/x1.png)

Figure 1: Cycle consistency framework. Given right view I_{R}, the complete cycle synthesizes left view through depth estimation (\mathcal{D}), forward warping (W_{R\to L}), and inpainting (G), then reconstructs the right view via depth estimation on the synthesized left view, backward warping (W_{L\to R}), and inpainting. The reconstruction loss \mathcal{L}_{\text{cycle}}=\|\hat{I}_{R}^{\text{recon}}-I_{R}\| provides self-supervision.

Data scarcity for supervised training. Supervised approaches(Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos"); Huang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib6 "ReStereo: diffusion stereo video generation and restoration")) require training pairs (I_{R},M_{\text{dis}}^{L\to R}), where the stereo inpainting network takes masked right view I_{R}\odot(1-M_{\text{dis}}^{L\to R}) and disocclusion mask M_{\text{dis}}^{L\to R} as input, using I_{R} for supervision. However, no ready-to-use datasets exist. To construct such data from real stereo pairs, StereoCrafter(Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos")) collects real stereo video pairs and generates training data by aligning left to right views to identify disocclusion regions M_{\text{dis}}^{L\to R}. However, this alignment introduces stereo matching errors that severely degrade data quality. Moreover, high-quality stereo videos predominantly come from copyrighted 3D films with restricted access, further limiting availability. Synthetic data approaches, such as Restereo(Huang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib6 "ReStereo: diffusion stereo video generation and restoration")) using Kubric(Greff et al., [2022](https://arxiv.org/html/2607.05354#bib.bib25 "Kubric: a scalable dataset generator")), avoid stereo matching errors but suffer significant domain gaps between rendered and real-world videos, limiting real-world generalization.

To overcome these limitations, we propose the first self-supervised approach leveraging abundant monocular videos (images) for training stereo inpainting networks. Our method demonstrates that, based on cycle consistency, disocclusion masks M_{\text{dis}}^{L\to R} can be directly derived from right views I_{R} to construct training data, eliminating the need for stereo pairs or synthetic data.

### 3.3 Cycle Consistency

We introduce right-left-right cycle consistency as a self-supervision mechanism for stereoscopic generation. As illustrated in [Figure 1](https://arxiv.org/html/2607.05354#S3.F1 "In 3.2 Motivation ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), the principle is geometric and bidirectional: synthesizing the left view from the right, then reconstructing the right from this synthesized left, should recover the original input. Given a frame I_{R}, we first synthesize a pseudo left-eye view through the DIBR framework:

d_{R}=\mathcal{D}(I_{R}),(5)

\tilde{I}_{L},M_{\text{dis}}^{R\to L}=W_{R\to L}(I_{R},d_{R}),(6)

\hat{I}_{L}=G(\tilde{I}_{L},M_{\text{dis}}^{R\to L}).(7)

The right view is then reconstructed from \hat{I}_{L}:

\hat{d}_{L}=\mathcal{D}(\hat{I}_{L}),(8)

\tilde{I}_{R},M_{\text{dis}}^{L\to R}=W_{L\to R}(\hat{I}_{L},\hat{d}_{L}),(9)

\hat{I}_{R}^{\text{recon}}=G(\tilde{I}_{R},M_{\text{dis}}^{L\to R}).(10)

The cycle consistency loss enforces that reconstruction matches input:

\mathcal{L}_{\text{cycle}}=\|\hat{I}_{R}^{\text{recon}}-I_{R}\|.(11)

While cycle consistency enables self-supervised training without paired stereo data, naive implementation is computationally prohibitive. End-to-end differentiability requires backpropagating through warping operations W(\cdot,\cdot) that depend on estimated disparity \mathcal{D}(\cdot), yet warping involves discrete pixel coordinate mapping and scattered writes to irregular locations, operations fundamentally non-differentiable in nature. Differentiable rendering approximations introduce substantial overhead and complexity. More critically, the cycle demands four sequential model inferences per training step: disparity estimation from I_{R}, left view inpainting, disparity re-estimation from \hat{I}_{L}, and final right view inpainting. This doubles memory requirements and training costs while accumulating errors through multiple non-linear transformations, making video-scale training computationally infeasible.

### 3.4 Geometric Reciprocity Theorem

![Image 2: Refer to caption](https://arxiv.org/html/2607.05354v1/x2.png)

Figure 2: Progressive simplification of cycle consistency to Geometric Reciprocity.(i) Inpainted regions in \hat{I}_{L} do not affect \hat{I}_{R}^{\text{recon}}, allowing us to skip left view inpainting (marked with \times) and directly use \tilde{I}_{L}. (ii) Right-to-left warping transfers disparity from d_{R} to \tilde{I}_{L}, allowing us to skip left view disparity estimation and directly reuse \tilde{d}_{L}. (iii) Transferred disparity ensures perfect round-trips for all validly warped pixels, enabling analytical computation of M_{\text{dis}}^{L\to R} as pixels lost during right-to-left warping and eliminating all warping operations (marked with \times). The final result reveals that M_{\text{dis}}^{L\to R}=M_{\text{lost}}^{R\to L} can be computed directly from (I_{R},d_{R}) alone.

We resolve all aforementioned challenges through a key geometric insight: the stereo warping process itself inherently encodes all information needed to enforce cycle consistency. Building on this insight, we mathematically prove that the entire gradient-intensive left view synthesis steps, including inpainting the left view, estimating its depth, and performing pixel warping operations, do not affect the cycle consistency loss \mathcal{L}_{\text{cycle}} and can therefore be eliminated entirely. We formalize this result as follows:

Geometric Reciprocity Theorem (GRT). Under the nearest-neighbor DIBR formulation, for any right (target) view I_{R} synthesized from a left (source) view, the disocclusion mask required for synthesis is mathematically equivalent to the mask of pixels that would be lost when warping from right (target) to left (source):

M_{\text{dis}}^{L\to R}=M_{\text{lost}}^{R\to L},(12)

where M_{\text{lost}}^{R\to L} identifies pixels in I_{R} that would be lost due to boundary violations or depth occlusions during right-to-left warping with estimated disparity d_{R}=\mathcal{D}(I_{R}). By treating any monocular image as a right (target) view, GRT enables us to directly compute the inference-time disocclusion mask that would emerge when synthesizing it from a left (source) view, using only depth estimation from I_{R}. The image itself then serves as ground truth for these disocclusions, enabling self-supervised training from monocular videos (images) while bypassing the entire synthesis pipeline.

#### 3.4.1 Proof of GRT

We prove the GRT by progressively simplifying the cycle consistency framework through three geometric observations visualized in [Figure 2](https://arxiv.org/html/2607.05354#S3.F2 "In 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). Remarkably, we demonstrate that each computational step in the naive cycle can be eliminated without affecting the final result, revealing an elegant mathematical structure underlying stereoscopic generation. Note that this proof assumes nearest-neighbor warping; we extend to soft interpolation warping in [Appendix A9](https://arxiv.org/html/2607.05354#A9 "Appendix A9 Extension to Soft Interpolation Warping ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation").

Eliminating left view inpainting. We first observe that the inpainted left view content, \hat{I}_{L}=G(\tilde{I}_{L},M_{\text{dis}}^{R\to L}), is geometrically irrelevant to the cycle consistency loss. Consider pixels where M_{\text{dis}}^{R\to L}=1: these regions were disoccluded during right-to-left warping and thus have no physical counterpart in the original I_{R}. When warping back from left to right, these inpainted pixels cannot produce valid mappings since they represent content absent from the actual scene geometry. Consequently, the disocclusion mask M_{\text{dis}}^{L\to R} computed from the incomplete warped view \tilde{I}_{L} is identical to that computed from the fully inpainted \hat{I}_{L}. This geometric property allows us to bypass the entire left view inpainting step:

\tilde{I}_{R},M_{\text{dis}}^{L\to R}=W_{L\to R}(\tilde{I}_{L},\mathcal{D}(\tilde{I}_{L})).(13)

Eliminating left view disparity estimation. Having established that we can work directly with \tilde{I}_{L} in the previous step, we recognize that disparity estimation from the left view is redundant. During forward warping, each pixel (x_{R},y_{R}) in I_{R} projects to position (x_{L},y_{L}) where:

x_{L}=x_{R}+d_{R}(x_{R},y_{R}),\quad y_{L}=y_{R}.(14)

Treating disparity as a single-channel image, this projection simultaneously transfers both color and disparity to non-disoccluded pixels:

\displaystyle\tilde{I}_{L}(x_{L},y_{L})\displaystyle=I_{R}(x_{R},y_{R}),(15)
\displaystyle\tilde{d}_{L}(x_{L},y_{L})\displaystyle=d_{R}(x_{R},y_{R}),

where (x_{L},y_{L}) receives projection from (x_{R},y_{R}). Note that \tilde{d}_{L} contains valid disparity values only at non-disoccluded pixels transferred from I_{R}, while disoccluded regions (where M_{\text{dis}}^{R\to L}=1) remain undefined. The crucial observation is that the previous step eliminated the need for complete left view information. We only need disparity values for non-disoccluded pixels in \tilde{I}_{L}, precisely those already transferred from I_{R}. Disoccluded regions do not participate in backward warping and thus do not require disparity estimation. Therefore, we directly use the transferred disparity \tilde{d}_{L} instead of re-estimating via \mathcal{D}(\tilde{I}_{L}), eliminating another computational bottleneck:

\tilde{I}_{R},M_{\text{dis}}^{L\to R}=W_{L\to R}(\tilde{I}_{L},\tilde{d}_{L}).(16)

Eliminating warping operations. Our final observation is that even the warping operations themselves can be eliminated. After removing both left view inpainting and disparity estimation, the cycle reduces to forward-backward warping: estimate disparity d_{R} from I_{R}, forward warp to obtain \tilde{I}_{L} and \tilde{d}_{L}, then backward warp to compute \tilde{I}_{R} and M_{\text{dis}}^{L\to R}. We observe that pixels completing the round-trip warping return to their exact original positions:

\displaystyle x_{R}^{\prime}\displaystyle=x_{L}-\tilde{d}_{L}(x_{L},y_{L})(17)
\displaystyle=[x_{R}+d_{R}(x_{R},y_{R})]-[d_{R}(x_{R},y_{R})]
\displaystyle=x_{R}.

This reveals the fundamental structure: pixels completing the forward-backward cycle remain unchanged, while those failing to complete it form the disocclusion mask. From a self-supervised learning perspective, this structure naturally provides supervision. Pixels completing the cycle correspond to regions where ground truth exists in I_{R}, while M_{\text{dis}}^{L\to R} identifies regions requiring inpainting. Rather than explicitly performing warping operations to identify these regions, we determine which pixels from I_{R} fail to complete the round-trip. A pixel (x_{R},y_{R}) is lost under two mutually exclusive conditions:

(a) Boundary violation: The pixel projects outside the image domain during forward warping:

M_{\text{oob}}^{R\to L}(x_{R},y_{R})=\mathbb{I}[x_{R}+d_{R}(x_{R},y_{R})\notin[0,W)],(18)

where W is image width and \mathbb{I}[\cdot] is the indicator function.

(b) Depth occlusion: Multiple pixels from I_{R} map to the same location (x_{L},y_{L}) during forward warping. Only the closest pixel is retained using a depth buffer:

B[x_{L},y_{L}]=\max_{(x_{R},y_{R})\to(x_{L},y_{L})}d_{R}(x_{R},y_{R}),(19)

where (x_{R},y_{R})\to(x_{L},y_{L}) denotes all pixels from I_{R} projecting to (x_{L},y_{L}) with y_{R}=y_{L}. A pixel is occluded if its disparity is less than this maximum:

M_{\text{occl}}^{R\to L}(x_{R},y_{R})=\mathbb{I}[d_{R}(x_{R},y_{R})<B[x_{L},y_{L}]],(20)

where (x_{L},y_{L}) is the projected location from (x_{R},y_{R}). The complete lost pixel mask combines both cases:

M_{\text{lost}}^{R\to L}=M_{\text{oob}}^{R\to L}\vee M_{\text{occl}}^{R\to L}.(21)

Both conditions depend only on (I_{R},d_{R}) and require no warping operations, only analytical computation. This remarkable result establishes the GRT: by eliminating all three computational steps (left view inpainting, left view disparity estimation, and warping operations), we arrive at the elegant equivalence M_{\text{dis}}^{L\to R}=M_{\text{lost}}^{R\to L}. Note that if we start from the left-right-left cycle instead, we can derive the symmetric result M_{\text{dis}}^{R\to L}=M_{\text{lost}}^{L\to R}.

#### 3.4.2 Equivalence to Full Supervision

Unlike most self-supervised methods (Zhu et al., [2017](https://arxiv.org/html/2607.05354#bib.bib18 "Unpaired image-to-image translation using cycle-consistent adversarial networks"); Yang et al., [2021](https://arxiv.org/html/2607.05354#bib.bib21 "Self-supervised video object segmentation by motion grouping")) that provide weak, indirect supervision for downstream tasks, GRT fundamentally differs by producing the same mask supervision as paired stereo data under the stated DIBR formulation. By treating any monocular image as a target view I_{R}, GRT directly computes M_{\text{dis}}^{L\to R}=M_{\text{lost}}^{R\to L} from disparity estimation alone. This is the same mask that emerges when a source view synthesizes I_{R} via DIBR ([Figure 3](https://arxiv.org/html/2607.05354#S3.F3 "In 3.4.3 Application of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), top), yet requires neither source view synthesis nor paired stereo data. As shown in the green-highlighted regions of [Figure 3](https://arxiv.org/html/2607.05354#S3.F3 "In 3.4.3 Application of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), the mask-conditioned inpainting process during training matches that at inference, ensuring train-inference consistency.

#### 3.4.3 Application of GRT

GRT enables self-supervised training data construction by computing inference-identical disocclusion masks from monocular images ([Figure 3](https://arxiv.org/html/2607.05354#S3.F3 "In 3.4.3 Application of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), bottom). Each mask can be computed once offline and reused during training. Given a target view I_{R}, we estimate d_{R}=\mathcal{D}(I_{R}) and compute M_{\text{dis}}^{L\to R}=M_{\text{lost}}^{R\to L} to construct triplets (X_{\text{input}},M_{\text{dis}}^{L\to R},I_{R}) where X_{\text{input}}=I_{R}\odot(1-M_{\text{dis}}^{L\to R}) with I_{R} as ground truth. The training objective is:

\mathcal{L}=\|G(X_{\text{input}},M_{\text{dis}}^{L\to R})-I_{R}\|.(22)

Training and evaluation datasets. We construct the first comprehensive datasets for stereo inpainting from widely-adopted benchmarks: ImageNet-GRT and Kinetics-GRT from ImageNet(Russakovsky et al., [2015](https://arxiv.org/html/2607.05354#bib.bib26 "ImageNet large scale visual recognition challenge")) and Kinetics(Kay et al., [2017](https://arxiv.org/html/2607.05354#bib.bib27 "The Kinetics human action video dataset")) for training. Building on the established equivalence ([Section 3.4.2](https://arxiv.org/html/2607.05354#S3.SS4.SSS2 "3.4.2 Equivalence to Full Supervision ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")), we create DAVIS-GRT from DAVIS(Perazzi et al., [2016](https://arxiv.org/html/2607.05354#bib.bib28 "A benchmark dataset and evaluation methodology for video object segmentation")) for evaluation (green-highlighted regions, [Figure 3](https://arxiv.org/html/2607.05354#S3.F3 "In 3.4.3 Application of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")) to faithfully reflect real-world inference performance (details in [Appendix A2](https://arxiv.org/html/2607.05354#A2 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")).

![Image 3: Refer to caption](https://arxiv.org/html/2607.05354v1/x3.png)

Figure 3: Equivalence to Full Supervision.Top: inference synthesizes I_{R} from I_{L} via DIBR and obtains M_{\text{dis}}^{L\to R} for inpainting. Bottom: GRT treats a monocular frame as I_{R} and computes the same mask analytically from I_{R} alone for training and DAVIS-GRT evaluation.

### 3.5 Model Architecture

We adopt LaMa(Suvorov et al., [2022](https://arxiv.org/html/2607.05354#bib.bib30 "Resolution-robust large mask inpainting with Fourier convolutions")), which leverages Fast Fourier Convolutions, for image stereo inpainting and ProPainter(Zhou et al., [2023](https://arxiv.org/html/2607.05354#bib.bib36 "Propainter: improving propagation and transformer for video inpainting")) for video stereo inpainting. ProPainter features recurrent flow completion and sparse video transformers to handle temporal consistency. Both models are fine-tuned on ImageNet-GRT and Kinetics-GRT respectively, using a combined loss of L1 and perceptual components.

## 4 Experiments

### 4.1 Experimental Setup

Baselines. For image stereo inpainting, we compare against StereoDiffusion(Wang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib5 "Stereodiffusion: training-free stereo image generation using latent diffusion models")), ZeroStereo(Wang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib41 "ZeroStereo: zero-shot stereo matching from single images")), and Mono2Stereo(Yu et al., [2025b](https://arxiv.org/html/2607.05354#bib.bib40 "Mono2Stereo: a benchmark and empirical study for stereo conversion")). For video stereoscopic generation, we evaluate against SVG(Dai et al., [2024](https://arxiv.org/html/2607.05354#bib.bib7 "SVG: 3D stereoscopic video generation via denoising frame matrix")) and StereoCrafter(Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos")). We denote our methods as Ours-Image and Ours-Video.

Datasets and Metrics. We conduct evaluations on two complementary benchmarks. DAVIS-GRT isolates the stereo inpainting sub-task under geometrically consistent masks with clean ground truth, while Inria 3DMovie evaluates the full left-to-right stereoscopic generation pipeline on real stereo footage. On DAVIS-GRT, which comprises 50 video clips with 3,455 frames, we report PSNR, SSIM(Wang et al., [2004](https://arxiv.org/html/2607.05354#bib.bib31 "Image quality assessment: from error visibility to structural similarity")), and LPIPS(Zhang et al., [2018](https://arxiv.org/html/2607.05354#bib.bib32 "The unreasonable effectiveness of deep features as a perceptual metric")) to assess stereo inpainting quality, along with CLIP Temporal Consistency (CTC), which measures frame-to-frame CLIP feature cosine similarity, to evaluate temporal coherence. Image-based methods are evaluated per-frame on this dataset. Per-frame inference time is reported at 512\times 512 resolution. On the Inria 3DMovie Dataset(Alahari et al., [2013](https://arxiv.org/html/2607.05354#bib.bib42 "Pose estimation and segmentation of people in 3d movies")), which contains 36 stereo video pairs, we evaluate video stereo generation methods using SIoU(Yu et al., [2025b](https://arxiv.org/html/2607.05354#bib.bib40 "Mono2Stereo: a benchmark and empirical study for stereo conversion")) and MEt3R(Asim et al., [2025](https://arxiv.org/html/2607.05354#bib.bib43 "Met3r: measuring multi-view consistency in generated images")) to measure viewing comfort and geometric consistency, reflecting the quality of stereoscopic viewing experience.

### 4.2 Quantitative Results

DAVIS-GRT. As shown in [Table 2](https://arxiv.org/html/2607.05354#S4.T2 "In 4.2 Quantitative Results ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), both Ours-Image and Ours-Video achieve superior performance across all metrics compared to existing methods, while being significantly faster with inference times of 0.05s and 0.24s per frame, respectively. This improvement stems from our self-supervised training paradigm that ensures train-inference alignment through GRT-derived data, enabling more accurate geometric understanding without relying on imperfect stereo pair collections.

Table 2: DAVIS-GRT stereo inpainting results. Video methods additionally report temporal consistency (CTC).

Inria 3DMovie Dataset. Leveraging improved stereo inpainting capabilities, our methods deliver more comfortable viewing experiences. As shown in [Table 3](https://arxiv.org/html/2607.05354#S4.T3 "In 4.2 Quantitative Results ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), Ours-Video demonstrates substantially superior geometric consistency and viewing comfort compared to video stereoscopic generation baselines.

Table 3: Evaluation on Inria 3DMovie.

### 4.3 Qualitative Results

Visual comparisons in [Figure 4](https://arxiv.org/html/2607.05354#S4.F4 "In 4.3 Qualitative Results ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") demonstrate the effectiveness of our approach. We compare against StereoDiffusion, the top-performing image baseline, as well as all video stereo inpainting methods. Our GRT-based training enables precise geometric understanding, producing natural textures in disoccluded regions with smooth boundary transitions.

![Image 4: Refer to caption](https://arxiv.org/html/2607.05354v1/x4.png)

Figure 4: Qualitative comparison. Our method produces more natural textures and smoother boundaries.

### 4.4 Effectiveness of GRT Training Data

To validate the broad applicability of GRT-derived training data, we fine-tune several foundation models using our datasets. For images, we adapt LaMa(Suvorov et al., [2022](https://arxiv.org/html/2607.05354#bib.bib30 "Resolution-robust large mask inpainting with Fourier convolutions")) and pretrained Stable Diffusion(Rombach et al., [2022](https://arxiv.org/html/2607.05354#bib.bib34 "High-resolution image synthesis with latent diffusion models")) inpainting models (SD1.5, SD2.1, and SDXL); for videos, we fine-tune ProPainter(Zhou et al., [2023](https://arxiv.org/html/2607.05354#bib.bib36 "Propainter: improving propagation and transformer for video inpainting")) and StereoCrafter. As shown in [Table 4](https://arxiv.org/html/2607.05354#S4.T4 "In 4.4 Effectiveness of GRT Training Data ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), all models achieve substantial improvements across metrics after fine-tuning on GRT data. Notably, even StereoCrafter, purpose-built for stereoscopic generation, benefits considerably, demonstrating that GRT provides higher-quality supervision than existing stereo pair collection strategies. These results confirm our self-supervised training paradigm is broadly applicable across diverse architectures.

Table 4: GRT fine-tuning results across image and video inpainting backbones.

## 5 Conclusion

We present a self-supervised framework for training stereo inpainting networks from monocular videos, addressing the data bottleneck in monocular-to-stereo conversion. Our key contribution is the Geometric Reciprocity Theorem (GRT): under the stated DIBR formulation, the disocclusion mask for a target view equals the pixels lost when warping back to source. This enables computing training masks from depth alone, eliminating stereo pairs or synthetic data. We achieve state-of-the-art quality with scalable training from real-world videos.

## Acknowledgements

This work is supported by Hong Kong Research Grants Council – General Research Fund (Grant Nos. 17213825 and 17211024), Hong Kong Innovation and Technology Commission – Innovation and Technology Fund (Project No. ITS/488/24FP), and HKU Seed Fund for PI Research.

## Impact Statement

This paper presents work whose goal is to advance the field of machine learning. There are many potential societal consequences of our work, none of which we feel must be specifically highlighted here.

## References

*   K. Alahari, G. Seguin, J. Sivic, and I. Laptev (2013)Pose estimation and segmentation of people in 3d movies. In ICCV, Cited by: [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p2.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   M. Asim, C. Wewer, T. Wimmer, B. Schiele, and J. E. Lenssen (2025)Met3r: measuring multi-view consistency in generated images. In CVPR, Cited by: [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p2.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   A. Bochkovskii, A. Delaunoy, H. Germain, M. Santos, Y. Zhou, S. R. Richter, and V. Koltun (2025)Depth pro: sharp monocular metric depth in less than a second. In ICLR, Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   S. Chen, H. Guo, S. Zhu, F. Zhang, Z. Huang, J. Feng, and B. Kang (2025)Video depth anything: consistent depth estimation for super-long videos. In CVPR, Cited by: [Appendix A2](https://arxiv.org/html/2607.05354#A2.p2.5 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   P. Dai, F. Tan, Q. Xu, D. Futschik, R. Du, S. Fanello, X. Qi, and Y. Zhang (2024)SVG: 3D stereoscopic video generation via denoising frame matrix. arXiv preprint arXiv:2407.00367. Cited by: [§1](https://arxiv.org/html/2607.05354#S1.p2.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§1](https://arxiv.org/html/2607.05354#S1.p3.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p2.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.2](https://arxiv.org/html/2607.05354#S3.SS2.p2.1 "3.2 Motivation ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p1.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   D. Dwibedi, Y. Aytar, J. Tompson, P. Sermanet, and A. Zisserman (2019)Temporal cycle-consistency learning. In CVPR, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   A. Geiger, P. Lenz, and R. Urtasun (2012)Are we ready for autonomous driving? the kitti vision benchmark suite. In CVPR, Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   K. Greff, F. Belletti, L. Beyer, C. Doersch, Y. Du, D. Duckworth, D. J. Fleet, D. Gnanapragasam, F. Golemo, C. Herrmann, et al. (2022)Kubric: a scalable dataset generator. In CVPR, Cited by: [§3.2](https://arxiv.org/html/2607.05354#S3.SS2.p3.5 "3.2 Motivation ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   J. Hoffman, E. Tzeng, T. Park, J. Zhu, P. Isola, K. Saenko, A. Efros, and T. Darrell (2018)CyCADA: cycle-consistent adversarial domain adaptation. In ICML, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   X. Huang, A. K. Singh, F. Dubost, C. N. Vasconcelos, S. Khattar, L. Shi, C. Theobalt, C. Oztireli, and G. Singh (2025)ReStereo: diffusion stereo video generation and restoration. arXiv preprint arXiv:2506.06023. Cited by: [Appendix A8](https://arxiv.org/html/2607.05354#A8.p1.1 "Appendix A8 Training Data Challenges ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§1](https://arxiv.org/html/2607.05354#S1.p2.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§1](https://arxiv.org/html/2607.05354#S1.p3.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p3.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.2](https://arxiv.org/html/2607.05354#S3.SS2.p3.5 "3.2 Motivation ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   W. Kay, J. Carreira, K. Simonyan, B. Zhang, C. Hillier, S. Vijayanarasimhan, F. Viola, T. Green, T. Back, P. Natsev, et al. (2017)The Kinetics human action video dataset. arXiv preprint arXiv:1705.06950. Cited by: [Appendix A2](https://arxiv.org/html/2607.05354#A2.p4.1 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.4.3](https://arxiv.org/html/2607.05354#S3.SS4.SSS3.p2.1 "3.4.3 Application of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   B. Ke, A. Obukhov, S. Huang, N. Metzger, R. C. Daudt, and K. Schindler (2024)Repurposing diffusion-based image generators for monocular depth estimation. In CVPR, Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   L. Kong, S. Xie, H. Hu, L. X. Ng, B. Cottereau, and W. T. Ooi (2023)RoboDepth: robust out-of-distribution depth estimation under corruptions. In NeurIPS, Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   H. Lin, S. Chen, J. Liew, D. Y. Chen, Z. Li, G. Shi, J. Feng, and B. Kang (2025)Depth anything 3: recovering the visual space from any views. arXiv preprint arXiv:2511.10647. Cited by: [Appendix A2](https://arxiv.org/html/2607.05354#A2.p2.5 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   J. Min, J. Kim, C. Min, M. Kim, Y. Jeon, and M. Choi (2025)DepthFocus: controllable depth estimation for see-through scenes. arXiv preprint arXiv:2511.16993. Cited by: [Appendix A2](https://arxiv.org/html/2607.05354#A2.p2.5 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   F. Perazzi, J. Pont-Tuset, B. McWilliams, L. Van Gool, M. Gross, and A. Sorkine-Hornung (2016)A benchmark dataset and evaluation methodology for video object segmentation. In CVPR, Cited by: [Appendix A2](https://arxiv.org/html/2607.05354#A2.p5.1 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.4.3](https://arxiv.org/html/2607.05354#S3.SS4.SSS3.p2.1 "3.4.3 Application of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   R. Ranftl, A. Bochkovskiy, and V. Koltun (2021)Vision transformers for dense prediction. In ICCV, Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   R. Ranftl, K. Lasinger, D. Hafner, K. Schindler, and V. Koltun (2020)Towards robust monocular depth estimation: mixing datasets for zero-shot cross-dataset transfer. IEEE TPAMI. Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   R. Rombach, A. Blattmann, D. Lorenz, P. Esser, and B. Ommer (2022)High-resolution image synthesis with latent diffusion models. In CVPR, Cited by: [§4.4](https://arxiv.org/html/2607.05354#S4.SS4.p1.1 "4.4 Effectiveness of GRT Training Data ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   O. Russakovsky, J. Deng, H. Su, J. Krause, S. Satheesh, S. Ma, Z. Huang, A. Karpathy, A. Khosla, M. Bernstein, et al. (2015)ImageNet large scale visual recognition challenge. IJCV. Cited by: [Appendix A2](https://arxiv.org/html/2607.05354#A2.p3.1 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.4.3](https://arxiv.org/html/2607.05354#S3.SS4.SSS3.p2.1 "3.4.3 Application of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   J. Shi, Q. Wang, Z. Li, R. Idoughi, and P. Wonka (2024)StereoCrafter-Zero: zero-shot stereo video generation with noisy restart. arXiv preprint arXiv:2411.14295. Cited by: [§1](https://arxiv.org/html/2607.05354#S1.p2.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p2.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   N. Shvetsova, G. Bhat, P. Truong, H. Kuehne, and F. Tombari (2026)M2SVid: end-to-end inpainting and refinement for monocular-to-stereo video conversion. In International Conference on 3D Vision (3DV), Cited by: [§1](https://arxiv.org/html/2607.05354#S1.p2.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§1](https://arxiv.org/html/2607.05354#S1.p3.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p3.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   N. Silberman, D. Hoiem, P. Kohli, and R. Fergus (2012)Indoor segmentation and support inference from rgbd images. In ECCV, Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   A. Singh (2021)CLDA: contrastive learning for semi-supervised domain adaptation. In NeurIPS, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   B. Sun, M. Jin, B. Yin, and Q. Hou (2025)Depth anything at any condition. arXiv preprint arXiv:2507.01634. Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   R. Suvorov, E. Logacheva, A. Mashikhin, A. Remizova, A. Ashukha, A. Silvestrov, N. Kong, H. Goka, K. Park, and V. Lempitsky (2022)Resolution-robust large mask inpainting with Fourier convolutions. In WACV, Cited by: [Appendix A4](https://arxiv.org/html/2607.05354#A4.p1.1 "Appendix A4 Model Architecture and Training ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.5](https://arxiv.org/html/2607.05354#S3.SS5.p1.1 "3.5 Model Architecture ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§4.4](https://arxiv.org/html/2607.05354#S4.SS4.p1.1 "4.4 Effectiveness of GRT Training Data ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   L. Wang, J. R. Frisvad, M. B. Jensen, and S. A. Bigdeli (2024)Stereodiffusion: training-free stereo image generation using latent diffusion models. In CVPR, Cited by: [§1](https://arxiv.org/html/2607.05354#S1.p2.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§1](https://arxiv.org/html/2607.05354#S1.p3.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p2.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.2](https://arxiv.org/html/2607.05354#S3.SS2.p2.1 "3.2 Motivation ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p1.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   X. Wang, H. Yang, G. Xu, J. Cheng, M. Lin, Y. Deng, J. Zang, Y. Chen, and X. Yang (2025)ZeroStereo: zero-shot stereo matching from single images. In ICCV, Cited by: [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p1.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli (2004)Image quality assessment: from error visibility to structural similarity. IEEE TIP. Cited by: [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p2.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   J. Xie, R. Girshick, and A. Farhadi (2016)Deep3d: fully automatic 2d-to-3d video conversion with deep convolutional neural networks. In ECCV, Cited by: [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p1.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   C. Yang, H. Lamdouar, E. Lu, A. Zisserman, and W. Xie (2021)Self-supervised video object segmentation by motion grouping. In ICCV, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.4.2](https://arxiv.org/html/2607.05354#S3.SS4.SSS2.p1.3 "3.4.2 Equivalence to Full Supervision ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   L. Yang, B. Kang, Z. Huang, X. Xu, J. Feng, and H. Zhao (2024)Depth anything: unleashing the power of large-scale unlabeled data. In CVPR, Cited by: [Appendix A2](https://arxiv.org/html/2607.05354#A2.p2.5 "Appendix A2 Dataset Details ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p1.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   M. Yu, W. Hu, J. Xing, and Y. Shan (2025a)TrajectoryCrafter: redirecting camera trajectory for monocular videos via diffusion models. In ICCV, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   S. Yu, Y. Chen, Z. Qi, Z. Xie, Y. Wang, L. Wang, Y. Shan, and H. Lu (2025b)Mono2Stereo: a benchmark and empirical study for stereo conversion. In CVPR, Cited by: [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p1.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p2.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   Y. Yuan, S. Liu, J. Zhang, Y. Zhang, C. Dong, and L. Lin (2018)Unsupervised image super-resolution using cycle-in-cycle generative adversarial networks. In CVPRW, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   R. Zhang, P. Isola, A. A. Efros, E. Shechtman, and O. Wang (2018)The unreasonable effectiveness of deep features as a perceptual metric. In CVPR, Cited by: [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p2.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   S. Zhao, W. Hu, X. Cun, Y. Zhang, X. Li, Z. Kong, X. Gao, M. Niu, and Y. Shan (2024)StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos. arXiv preprint arXiv:2409.07447. Cited by: [Appendix A8](https://arxiv.org/html/2607.05354#A8.p1.1 "Appendix A8 Training Data Challenges ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§1](https://arxiv.org/html/2607.05354#S1.p2.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§1](https://arxiv.org/html/2607.05354#S1.p3.1 "1 Introduction ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§2.1](https://arxiv.org/html/2607.05354#S2.SS1.p3.1 "2.1 Monocular-to-Stereo Video Conversion ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.2](https://arxiv.org/html/2607.05354#S3.SS2.p3.5 "3.2 Motivation ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§4.1](https://arxiv.org/html/2607.05354#S4.SS1.p1.1 "4.1 Experimental Setup ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   Y. Zheng, C. Zhong, P. Li, H. Gao, Y. Zheng, B. Jin, L. Wang, H. Zhao, G. Zhou, Q. Zhang, et al. (2023)STEPS: joint self-supervised nighttime image enhancement and depth estimation. In ICRA, Cited by: [§2.2](https://arxiv.org/html/2607.05354#S2.SS2.p1.1 "2.2 Monocular Depth Estimation ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   S. Zhou, C. Li, K. C. Chan, and C. C. Loy (2023)Propainter: improving propagation and transformer for video inpainting. In ICCV, Cited by: [Appendix A4](https://arxiv.org/html/2607.05354#A4.p1.1 "Appendix A4 Model Architecture and Training ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.5](https://arxiv.org/html/2607.05354#S3.SS5.p1.1 "3.5 Model Architecture ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§4.4](https://arxiv.org/html/2607.05354#S4.SS4.p1.1 "4.4 Effectiveness of GRT Training Data ‣ 4 Experiments ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   T. Zhou, P. Krahenbuhl, M. Aubry, Q. Huang, and A. A. Efros (2016)Learning dense correspondence via 3d-guided cycle consistency. In CVPR, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 
*   J. Zhu, T. Park, P. Isola, and A. A. Efros (2017)Unpaired image-to-image translation using cycle-consistent adversarial networks. In ICCV, Cited by: [§2.3](https://arxiv.org/html/2607.05354#S2.SS3.p1.1 "2.3 Cycle Consistency ‣ 2 Related work ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), [§3.4.2](https://arxiv.org/html/2607.05354#S3.SS4.SSS2.p1.3 "3.4.2 Equivalence to Full Supervision ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). 

## Appendix A1 Code and Data Release

The project repository is [https://github.com/Visual-AI/GRT](https://github.com/Visual-AI/GRT). We will release source code, precomputed GRT masks, and trained weights under the Apache 2.0 license.

## Appendix A2 Dataset Details

We construct three datasets by applying the Geometric Reciprocity Theorem (GRT) ([Section 3.4](https://arxiv.org/html/2607.05354#S3.SS4 "3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")) to widely-adopted vision benchmarks. For each image or video frame, we treat it as a right (target) view, estimate its monocular depth, and compute a binary disocclusion mask M_{\text{dis}}^{L\to R} following the GRT procedure. This yields self-supervised training samples and test-aligned evaluation samples for stereo inpainting, where each RGB image or frame is paired with its corresponding GRT-derived disocclusion mask.

Depth estimation and GRT mask generation. We use Depth Anything V2-Large(Yang et al., [2024](https://arxiv.org/html/2607.05354#bib.bib11 "Depth anything: unleashing the power of large-scale unlabeled data")) to estimate monocular depth for each image or frame, following previous stereoscopic video generation literature. The predicted relative (inverse) depth is converted to a disparity map and linearly rescaled to [0,\alpha W], where W is the image width and \alpha=0.1 for training and \alpha=0.06 for evaluation. We then apply the GRT procedure ([Section 3.4](https://arxiv.org/html/2607.05354#S3.SS4 "3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation")) to compute M_{\text{dis}}^{L\to R} by identifying lost pixels through boundary violations and depth occlusions. On average, disoccluded regions comprise approximately 10% of pixels for training data. Note that our framework flexibly accommodates alternative depth estimators, such as Video Depth Anything(Chen et al., [2025](https://arxiv.org/html/2607.05354#bib.bib39 "Video depth anything: consistent depth estimation for super-long videos")) for temporally consistent depth, Depth Anything V3(Lin et al., [2025](https://arxiv.org/html/2607.05354#bib.bib38 "Depth anything 3: recovering the visual space from any views")) for metric depth, or DepthFocus(Min et al., [2025](https://arxiv.org/html/2607.05354#bib.bib37 "DepthFocus: controllable depth estimation for see-through scenes")) for multi-layer depth to handle transparent surfaces. We adopt Depth Anything V2 to follow prior works and ensure fair comparisons.

ImageNet-GRT. ImageNet-GRT uses the complete ImageNet-1K training split(Russakovsky et al., [2015](https://arxiv.org/html/2607.05354#bib.bib26 "ImageNet large scale visual recognition challenge")), containing \sim 1.28M images across 1,000 object categories. We utilize all images without filtering and disregard class labels, treating ImageNet purely as a diverse source of natural imagery.

Kinetics-GRT. Kinetics-GRT uses the Kinetics-400 training split(Kay et al., [2017](https://arxiv.org/html/2607.05354#bib.bib27 "The Kinetics human action video dataset")), comprising \sim 240K videos across 400 human action categories with rich temporal dynamics and camera motion. We decode all frames at their original resolution and frame rate while preserving temporal order.

DAVIS-GRT. DAVIS-GRT uses all 50 videos (3,455 frames) from DAVIS 2016(Perazzi et al., [2016](https://arxiv.org/html/2607.05354#bib.bib28 "A benchmark dataset and evaluation methodology for video object segmentation")), a video segmentation benchmark known for high-quality annotations and challenging scenarios. DAVIS-GRT serves _exclusively_ for testing; no DAVIS frames are used during training or model selection, ensuring unbiased assessment of generalization.

## Appendix A3 Pseudocode

We provide pseudocode in [Figure A1](https://arxiv.org/html/2607.05354#A3.F1 "In Appendix A3 Pseudocode ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") implementing the Geometric Reciprocity Theorem (GRT) presented in [Section 3.4](https://arxiv.org/html/2607.05354#S3.SS4 "3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"). Given a disparity map, the function computes the disocclusion mask by identifying pixels that would be lost during warping due to boundary violations or depth occlusions.

1 def compute_grt_mask(disparity,direction=’R2L’):

2"""

3 Compute GRT-based disocclusion mask via geometric warping.

4

5 Args:

6 disparity:[B,H,W]disparity map(positive values)

7 direction:’R2L’for right-to-left warp(finds L->R disocclusions)

8’L2R’for left-to-right warp(finds R->L disocclusions)

9 Returns:

10 mask:[B,H,W]binary mask(True=disoccluded pixel)

11"""

12 B,H,W=disparity.shape

13

14

15 x=torch.arange(W)[None,None,:]

16 if direction==’R2L’:

17 x_target=round(x+disparity)

18 else:

19 x_target=round(x-disparity)

20

21

22 mask_oob=(x_target<0)|(x_target>=W)

23

24

25

26 valid_idx=torch.where(~mask_oob)

27 x_tgt=x_target[valid_idx]

28 d_src=disparity[valid_idx]

29

30

31 d_winner=scatter_max(d_src,index=x_tgt,dim_size=W)

32

33

34 mask_occ=torch.zeros_like(mask_oob)

35 is_occluded=(d_src<d_winner[valid_idx])

36 mask_occ[valid_idx][is_occluded]=True

37

38

39 return mask_oob|mask_occ

Figure A1: Pseudocode implementing the Geometric Reciprocity Theorem (GRT). Given a disparity map, the function computes the disocclusion mask by identifying pixels lost during warping due to boundary violations (mask_oob) or depth occlusions (mask_occ).

## Appendix A4 Model Architecture and Training

Our model builds upon the LaMa architecture(Suvorov et al., [2022](https://arxiv.org/html/2607.05354#bib.bib30 "Resolution-robust large mask inpainting with Fourier convolutions")) with Fast Fourier Convolutions (FFC) for image stereo inpainting, and ProPainter(Zhou et al., [2023](https://arxiv.org/html/2607.05354#bib.bib36 "Propainter: improving propagation and transformer for video inpainting")) for video stereo inpainting.

### A4.1 Image Stereo Inpainting

Architecture. We use the Big LaMa-Fourier generator (27M parameters): 3 downsampling blocks, 9 FFC-based residual blocks, and 3 upsampling blocks. The network takes 4-channel input (masked RGB + mask) and outputs 3-channel RGB. FFC blocks provide image-wide receptive fields by processing features in both spatial (local) and frequency (global) domains.

Training. We fine-tune the model on ImageNet-GRT with realistic disocclusion masks generated via GRT for 30 epochs at 256\times 256 resolution. We use combined L1 and LPIPS loss with Adam optimizer (learning rate 10^{-4}), batch size 32, and cosine annealing scheduler on two NVIDIA V100 GPUs.

### A4.2 Video Stereo Inpainting

Architecture. We adopt ProPainter which comprises three key components: (1) Recurrent Flow Completion (RFC) network that completes corrupted optical flows using deformable alignment with 8\times downsampled features; (2) Dual-domain propagation combining global image propagation (with flow consistency check) and local feature propagation (flow-guided deformable alignment); (3) Mask-guided sparse video Transformer with 8 blocks, window size 5\times 9, and extended size equal to half of the window size. The Transformer applies sparse attention only to query windows intersecting mask regions and uses temporal stride of 2 for key/value space to reduce redundancy.

Training. We fine-tune from pretrained ProPainter weights on Kinetics-GRT for 10,000 steps at 432\times 240 resolution. We use combined L1 reconstruction loss and T-PatchGAN adversarial loss (weight 0.01) with Adam optimizer (learning rate 10^{-4}) and batch size 8. The model processes local sequences of length 10 during training and length 20 during inference on two NVIDIA V100 GPUs.

## Appendix A5 Additional Analyses

Naive cycle consistency. GRT precomputes masks offline and reduces online optimization to standard inpainting, while naive cycle consistency requires multiple sequential model inferences and gradient approximations through warping. A controlled LaMa comparison is summarized in [Table A1](https://arxiv.org/html/2607.05354#A5.T1 "In Appendix A5 Additional Analyses ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation").

Table A1: Efficiency and quality comparison with naive cycle consistency.

Mask agreement. We compare analytically computed GRT masks with cycle-consistency masks under different depth and warping settings. The high agreement in [Table A2](https://arxiv.org/html/2607.05354#A5.T2 "In Appendix A5 Additional Analyses ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") indicates that the derived masks capture the same disocclusion structure in practice.

Table A2: Pixel-level mask agreement with GRT masks.

Depth estimator robustness. GRT is depth-estimator-agnostic and only requires a disparity map as input. [Table A3](https://arxiv.org/html/2607.05354#A5.T3 "In Appendix A5 Additional Analyses ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") shows that performance degrades gradually with weaker depth backbones but remains close.

Table A3: Depth estimator sensitivity on Inria 3DMovie.

GRT mask components. The boundary-violation and depth-occlusion terms are jointly required to identify geometrically lost pixels. Ablating either component degrades downstream inpainting quality.

Table A4: Ablation of GRT mask components on LaMa trained with ImageNet-GRT.

Data scaling. Because GRT requires no paired stereo capture, it can benefit from larger monocular video corpora. [Table A5](https://arxiv.org/html/2607.05354#A5.T5 "In Appendix A5 Additional Analyses ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") shows monotonic gains as the training set grows.

Table A5: Dataset scale ablation for ProPainter trained on GRT data.

## Appendix A6 Limitations

GRT inherits the assumptions of DIBR-based stereoscopic generation. It relies on rectified stereo geometry and the quality of the input disparity map; transparent or reflective surfaces, inaccurate depth discontinuities, and non-Lambertian effects can therefore lead to incorrect masks or visually implausible inpainting. The nearest-neighbor formulation gives exact mask consistency under the theorem statement, while bilinear interpolation introduces a small approximation gap as discussed in [Appendix A9](https://arxiv.org/html/2607.05354#A9 "Appendix A9 Extension to Soft Interpolation Warping ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation").

![Image 5: Refer to caption](https://arxiv.org/html/2607.05354v1/x5.png)

Figure A2: Performance of SDXL Inpainting on different mask patterns. The model handles large contiguous masks well (General Inpainting) but struggles with thin scattered disocclusion masks along object boundaries (Stereo Inpainting).

## Appendix A7 Discussion of General Inpainting Models

General-purpose image inpainting models are designed to fill large contiguous missing regions by hallucinating plausible content from surrounding context. While these models are powerful, stereo disocclusions present a fundamentally different mask pattern. Disocclusion masks are thin, elongated, and scattered along depth discontinuities at object boundaries, with significantly smaller total area compared to typical inpainting masks. More critically, disocclusions reveal previously hidden background content that is often visually and semantically distinct from the adjacent occluding foreground. For example, a disocclusion behind a person might expose a wall or furniture with no visual similarity to the person’s appearance. This domain gap in both mask geometry and content semantics causes general inpainting models to produce inferior results on stereo disocclusions. As we demonstrate in Figure[A2](https://arxiv.org/html/2607.05354#A6.F2 "Figure A2 ‣ Appendix A6 Limitations ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), while these models succeed on large contiguous masks, they fail on the thin scattered masks characteristic of stereo disocclusions.

![Image 6: Refer to caption](https://arxiv.org/html/2607.05354v1/x6.png)

Figure A3: Stereo matching methods produce distorted disocclusion masks and misaligned inpainting triplets. Our GRT approach generates geometrically accurate masks at test-time.

## Appendix A8 Training Data Challenges

Constructing high-quality training data remains a significant bottleneck for stereo inpainting. Methods relying on real stereo pairs, such as StereoCrafter(Zhao et al., [2024](https://arxiv.org/html/2607.05354#bib.bib3 "StereoCrafter: diffusion-based generation of long and high-fidelity stereoscopic 3D from monocular videos")), face a fundamental paradox: they rely on stereo matching algorithms to extract pixel correspondences from stereo pairs and subsequently derive disocclusion masks, yet stereo matching itself is prone to errors and particularly unreliable in disoccluded regions. As shown in Fig.[A3](https://arxiv.org/html/2607.05354#A7.F3 "Figure A3 ‣ Appendix A7 Discussion of General Inpainting Models ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation"), stereo matching produces distorted masks with alignment errors. StereoCrafter confirms this limitation, acknowledging the prevalence of large stereo matching errors that force them to employ complex manual alignment and aggressive filtering strategies (e.g., discarding samples where warping PSNR <25 dB), resulting in substantial data waste. Alternatively, approaches utilizing synthetic data(Huang et al., [2025](https://arxiv.org/html/2607.05354#bib.bib6 "ReStereo: diffusion stereo video generation and restoration")) provide precise geometry but suffer from inevitable Sim2Real domain gaps. Our GRT-based approach resolves these dilemmas by deriving geometrically consistent masks directly from monocular data, avoiding both error-prone matching and synthetic domain shifts.

## Appendix A9 Extension to Soft Interpolation Warping

The GRT proof in [Section 3.4.1](https://arxiv.org/html/2607.05354#S3.SS4.SSS1 "3.4.1 Proof of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") assumes nearest-neighbor warping, where each pixel (x_{R},y_{R}) maps to discrete coordinates (x_{L},y_{L})=(\mathrm{round}(x_{R}+d_{R}(x_{R},y_{R})),y_{R}). In practice, bilinear warping is sometimes preferred for smoother synthesis. We show that GRT extends to this soft interpolation setting by reformulating the problem at the renderer level rather than the pixel level, though this introduces a subtle train-test consistency trade-off.

Renderer-based formulation. Under bilinear warping, we treat each pixel (x_{R},y_{R}) in the right view I_{R} as a renderer that carries appearance and geometry information. Each renderer projects to continuous coordinates:

x_{L}^{\prime}=x_{R}+d_{R}(x_{R},y_{R}),\quad y_{L}^{\prime}=y_{R},(23)

and distributes its contribution to a 2\times 2 neighborhood in the left view via bilinear weights w_{x_{R},y_{R}}(x_{L},y_{L}). This splatting process synthesizes the left view as a weighted blend of renderer contributions.

Forward warping with occlusion handling. For each left-view pixel (x_{L},y_{L}), let S(x_{L},y_{L}) denote all renderers whose bilinear kernels overlap it. To handle occlusions, we maintain a depth buffer that tracks the maximum disparity among contributing renderers:

d_{L}^{\max}(x_{L},y_{L})=\max_{(x_{R},y_{R})\in S(x_{L},y_{L})}d_{R}(x_{R},y_{R}).(24)

Only renderers at maximum disparity are retained, as nearer objects occlude farther ones. Let S_{\max}(x_{L},y_{L}) denote renderers at maximum disparity:

\displaystyle S_{\max}(x_{L},y_{L})=\{\displaystyle(x_{R},y_{R})\in S(x_{L},y_{L}):(25)
\displaystyle d_{R}(x_{R},y_{R})=d_{L}^{\max}(x_{L},y_{L})\}.

The warped left view is synthesized as:

\tilde{I}_{L}(x_{L},y_{L})=\frac{\sum_{(x_{R},y_{R})\in S_{\max}}w_{x_{R},y_{R}}\cdot I_{R}(x_{R},y_{R})}{\sum_{(x_{R},y_{R})\in S_{\max}}w_{x_{R},y_{R}}},(26)

where we abbreviate S_{\max}(x_{L},y_{L}) as S_{\max} for notational simplicity.

Lost renderer criteria. A renderer (x_{R},y_{R}) is lost if it fails to contribute to any left-view pixel. This occurs under two conditions. First, boundary violation occurs when the renderer’s bilinear kernel support lies entirely outside the valid image domain:

M_{\text{oob}}^{R\to L}(x_{R},y_{R})=\mathbb{I}\left[\lfloor x_{L}^{\prime}\rfloor,\lceil x_{L}^{\prime}\rceil\notin[-1,W]\right],(27)

where the range [-1,W] ensures at least one neighbor in [0,W) has non-zero weight. Second, depth occlusion occurs when the renderer is occluded at all left-view locations in its support. Let S^{*}(x_{R},y_{R}) denote valid left-view pixels overlapping (x_{R},y_{R})’s bilinear kernel. The occlusion mask is:

\displaystyle M_{\text{occl}}^{R\to L}(x_{R},y_{R})=\mathbb{I}\big[\displaystyle d_{R}(x_{R},y_{R})<d_{L}^{\max}(x_{L},y_{L}),(28)
\displaystyle\forall(x_{L},y_{L})\in S^{*}(x_{R},y_{R})\big].

The complete lost mask combines both conditions:

M_{\text{lost}}^{R\to L}=M_{\text{oob}}^{R\to L}\vee M_{\text{occl}}^{R\to L}.(29)

GRT validity at the renderer level. The Geometric Reciprocity relation M_{\text{dis}}^{L\to R}=M_{\text{lost}}^{R\to L} continues to hold when formulated at the renderer level. The three-step simplification in [Section 3.4.1](https://arxiv.org/html/2607.05354#S3.SS4.SSS1 "3.4.1 Proof of GRT ‣ 3.4 Geometric Reciprocity Theorem ‣ 3 Method ‣ Geometric Reciprocity: Unlocking Self-Supervision for Stereoscopic Video Generation") remains geometrically valid: disoccluded regions lack scene correspondence, each renderer co-transfers disparity with its appearance, and renderers completing the round-trip return to their original positions. Therefore, lost renderers in the forward pass correspond exactly to disoccluded regions in the backward pass.

Train-test consistency. While GRT holds mathematically at the renderer level, bilinear warping introduces a subtle inconsistency. During training, M_{\text{lost}}^{R\to L} is computed from discrete renderers in the original image I_{R}. During testing, the synthesized view \hat{I}_{L} contains blended pixel values, and backward warping treats each blended pixel as a single renderer rather than the multiple discrete renderers that created it. This approximation causes slight differences in disocclusion masks, though the effect is minor for typical stereo baseline ranges.

Implementation. We adopt nearest-neighbor warping to maintain consistency with the theorem statement and to improve computational efficiency. Both variants produce visually similar results, while nearest-neighbor warping keeps training masks aligned with the stereoscopic generation pipeline.
