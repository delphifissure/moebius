Title: OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models

URL Source: https://arxiv.org/html/2503.18033

Published Time: Fri, 17 Oct 2025 00:42:13 GMT

Markdown Content:
\setcctype

by

![Image 1: Refer to caption](https://arxiv.org/html/2503.18033v3/x1.png)

Figure 1. OmnimatteZero is the first training-free generative approach for Omnimatte, leveraging pre-trained video diffusion models to achieve object removal, extraction, and seamless layer compositions in just 0.04 sec/frame (on an A100 GPU). See video examples in the supplemental material.††: ¡short description¿

, Matan Levy The Hebrew University of Jerusalem Israel, Nir Darshan OriginAI Israel, Gal Chechik Bar-Ilan University & NVIDIA Research Israel and Rami Ben-Ari OriginAI Israel

(2025)

###### Abstract.

In Omnimatte, one aims to decompose a given video into semantically meaningful layers, including the background and individual objects along with their associated effects, such as shadows and reflections. Existing methods often require extensive training or costly self-supervised optimization. In this paper, we present OmnimatteZero, a training-free approach that leverages off-the-shelf pre-trained video diffusion models for omnimatte. It can remove objects from videos, extract individual object layers along with their effects, and composite those objects onto new videos. These are accomplished by adapting zero-shot image inpainting techniques for video object removal, a task they fail to handle effectively out-of-the-box. To overcome this, we introduce temporal and spatial attention guidance modules that steer the diffusion process for accurate object removal and temporally consistent background reconstruction. We further show that self-attention maps capture information about the object and its footprints and use them to inpaint the object’s effects, leaving a clean background. Additionally, through simple latent arithmetic, object layers can be isolated and recombined seamlessly with new video layers to produce new videos. Evaluations show that OmnimatteZero not only achieves superior performance in terms of background reconstruction but also sets a new record for the fastest Omnimatte approach, achieving real-time performance with minimal frame runtime. [Project Page.](https://dvirsamuel.github.io/omnimattezero.github.io/)

Omnimatte, Video Diffusion Model, Training-free, Real-time

††ccs: Computing methodologies††ccs: Computing methodologies Machine learning algorithms††journalyear: 2025††copyright: cc††conference: SIGGRAPH Asia 2025 Conference Papers; December 15–18, 2025; Hong Kong, Hong Kong††booktitle: SIGGRAPH Asia 2025 Conference Papers (SA Conference Papers ’25), December 15–18, 2025, Hong Kong, Hong Kong††doi: 10.1145/3757377.3763917††isbn: 979-8-4007-2137-3/2025/12††submissionid: papers_1753
1. Introduction
---------------

Extracting or isolating objects in videos is a central problem in video understanding and editing, with important applications such as removing, modifying, or enhancing elements within a video scene. One important flavor of this task is video matting(Chuang et al., [2002](https://arxiv.org/html/2503.18033v3#bib.bib5)), which involves decomposing a video into a background layer and one or more foreground layers, each representing an individual object. A particularly challenging form of video matting is Omnimatte(Wang and Adelson, [1994](https://arxiv.org/html/2503.18033v3#bib.bib30); Lu et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib21)), where each foreground object is not only isolated but also includes associated effects such as shadows, reflections, and scene perturbations. The layers extracted by video matting facilitate various video editing applications, including object removal, background replacement, retiming (Lu et al., [2020](https://arxiv.org/html/2503.18033v3#bib.bib20)), and object duplication (Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)), many of which require estimating occluded background regions using techniques like video inpainting or omnimatting.

However, despite their promise, existing methods for video inpainting and Omnimatte face significant limitations. Recent inpainting approaches(Li et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib17); Zhou et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib36)), while trained on annotated datasets for object removal, fail to account for the nuanced effects that objects impart on the scene. Similarly, current Omnimatte methods demand computationally intensive self-supervised optimization for each video(Lu et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib21); Suhail et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib27); Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18); Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)). Some approaches further rely on large hand-crafted training datasets(Winter et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib32); Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)) or require 3D scene modeling using meshes or NeRFs(Suhail et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib27); Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18)), resulting in hours of training and slow per-frame rendering.

Given the success of fast, training-free approaches in image editing(Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22); Corneanu et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib6)), a natural question arises: can these methods be effectively adapted to video editing?

In this paper, we present a new approach called OmnimatteZero, the first training-free generative method to Omnimatte. OmnimatteZero (named for its zero training and optimization requirements) leverages off-the-shelf pre-trained video diffusion models to remove all objects from a video, extract individual object layers along with their associated effects, and finally composite them onto new backgrounds. This entire process is performed efficiently during diffusion inference, making it significantly faster than current methods. See Figure [1](https://arxiv.org/html/2503.18033v3#acmlabel1 "Figure 1 ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") for illustration.

We begin by adapting training-free image inpainting methods(Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22); Meng et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib24)) to handle object inpainting in videos using diffusion models. However, we find that simply applying these frame-by-frame techniques to videos leads to poor results: missing regions are not filled convincingly, and temporal consistency breaks down. To address this, we propose two attention guidance modules that can be easily integrated into pre-trained video diffusion models. These modules guide the diffusion process to achieve both accurate object removal and consistent background reconstruction. The first module, Temporal Attention Guidance (TAG), uses background patches from nearby frames. By modifying self-attention layers, it encourages the model to use these patches to reconstruct masked regions, improving temporal coherence. The second module, Spatial Attention Guidance (SAG), operates within each frame to refine local details and enhance visual plausibility.

We also observe that self-attention maps contain cues not just about the object but also its indirect effects, such as shadows and reflections. By leveraging this information, our method can inpaint these subtle traces, yielding cleaner backgrounds. For foreground layer extraction, we find that the object (and its traces) can be isolated by subtracting the latent representation of the clean background from the original video latent. This extracted object layer can then be seamlessly inserted into new backgrounds by simply adding the latents, enabling fast and flexible video composition.

To validate our approach, we apply it to two video diffusion models, LTXVideo (HaCohen et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib11)) and Wan2.1 (video, [2025](https://arxiv.org/html/2503.18033v3#bib.bib28)), and evaluate it on standard Omnimatte benchmarks both quantitatively and qualitatively. Our method outperforms all supervised and self-supervised existing inpainting and Omnimatte techniques across all benchmarks in terms of background reconstruction and object layer extraction. Notably, OmnimatteZero requires no training or additional optimization, functioning entirely within the denoising process of diffusion models. This positions OmnimatteZero as the fastest Omnimatte technique to date.

2. Related Work
---------------

### 2.1. Omnimatte

The first Omnimatte approaches(Kasten et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib13); Lu et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib21)) use motion cues to decompose a video into RGBA matte layers, assuming a static background with planar homographies. Optimization isolates dynamic foreground layers, taking 3 to 8.5 hours per video and ∼\sim 2.5 seconds per frame to render. Later methods enhanced Omnimatte with deep image priors(Lu et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib19); Gu et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib10)) and 3D representations(Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18); Suhail et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib27); Wu et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib33)), but still rely on strict motion assumptions and require extensive training (∼\sim 6 hours) with rendering times of 2.5-3.5 seconds per frame. A recent generative approach(Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)) uses video diffusion priors to remove objects and effects, with test-time optimization for frame reconstruction, taking ∼\sim 9 seconds per frame. In this paper, we propose a novel, training and optimization-free method using off-the-shelf video diffusion models, achieving real-time performance in 0.04 seconds per frame.

### 2.2. Video Inpainting

Earlier video inpainting methods(Chang et al., [2019](https://arxiv.org/html/2503.18033v3#bib.bib4); Wang et al., [2019](https://arxiv.org/html/2503.18033v3#bib.bib29); Hu et al., [2020](https://arxiv.org/html/2503.18033v3#bib.bib12)) used 3D CNNs for spatiotemporal modeling but struggled with long-range propagation due to limited receptive fields. Pixel-flow approaches(Gao et al., [2020](https://arxiv.org/html/2503.18033v3#bib.bib9); Zhang et al., [2022a](https://arxiv.org/html/2503.18033v3#bib.bib34), [b](https://arxiv.org/html/2503.18033v3#bib.bib35)) improved texture and detail restoration by utilizing adjacent frame information. Recently, Zhou et al. ([2023](https://arxiv.org/html/2503.18033v3#bib.bib36)) introduced ProPainter, which enhances reconstruction accuracy and efficiency by leveraging optical flow-based propagation and attention maps. VideoPainter (Bian et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib3)) proposed a dual-stream video inpainting method that injects video context into a pre-trained video diffusion model using a lightweight encoder. (Li et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib17)) proposed DiffuEraser, which combines a pre-trained text-to-image diffusion model with BrushNet, a feature extraction module, to generate temporally consistent videos. In this paper, we propose a single-step object inpainting approach, directly applied during video diffusion model inference, implicitly leveraging spatial and temporal information from adjacent frames for inpainting.

### 2.3. Diffusion Transformers for Video Generation

Recent advancements in diffusion models have significantly improved text-to-video generation. These models, trained on large datasets of video-text pairs, can generate visually compelling videos from text descriptions. Recent work introduced LTX-Video (HaCohen et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib11)), a real-time transformer-based latent diffusion model capable of generating videos at over 24 frames per second. It builds on 3D Video-VAE with a spatiotemporal latent space, a concept also used in Wan2.1 (video, [2025](https://arxiv.org/html/2503.18033v3#bib.bib28)) and the larger HunyuanVideo (Kong, [2024](https://arxiv.org/html/2503.18033v3#bib.bib15)). Unlike traditional methods that treat the video VAE and denoising transformer separately, LTX-Video integrates them within a highly compressed latent space (1:192 compression ratio), optimizing their interaction. This spatiotemporal downscaling results in 32×32×8 32\times 32\times 8 pixels per token while maintaining high-quality video generation. Similarly, HunyuanVideo employs a large-scale video generation framework, integrating an optimized VAE and diffusion-based transformer to achieve excellent visual quality and motion consistency. These models demonstrate the trend of combining high-compression VAEs with transformer-based diffusion models for efficient and scalable video generation.

![Image 2: Refer to caption](https://arxiv.org/html/2503.18033v3/x2.png)

Figure 2. Comparison of object removal results using (a) vanilla image inpainting extended to video, (b) Vid2Vid zero-shot inpainting, and (c) our guidance-based approach. Vanilla methods fail to maintain temporal consistency or clean background reconstruction, while our method achieves coherent, artifact-free inpainting across frames.††: motivation figure

![Image 3: Refer to caption](https://arxiv.org/html/2503.18033v3/x3.png)

Figure 3. Overview of our Object Removal strategy in OmnimatteZero.(a) We first identify potential background correspondences across frames. (b) Temporal Attention Guidance (TAG): Temporal attention scores between a foreground point and its background correspondences are replaced with the average attention between all background pairs, promoting consistent inpainting across time. (c) Spatial Attention Guidance (SAG): Within a frame, the attention from a foreground point to nearby background points is adjusted to reflect the mean attention among background points themselves, improving inpainting quality when temporal context is unavailable.††: method figure

3. Motivation: The failure of image inpainting approaches for videos
--------------------------------------------------------------------

We begin by extending training-free image-diffusion inpainting techniques to video diffusion models. Our reference point is _vanilla image inpainting_(Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22)), a straightforward method that starts with a random noise at the masked area and, at each diffusion step t t, injects Gaussian noise ϵ t\epsilon_{t} into the original background area so the denoiser can reconstruct the masked region while preserving the background during denoising. For video, we apply it across the full video latent to maintain both spatial and temporal coherence, since frame-by-frame inpainting leads to temporal artifacts like flickering. In practice, this vanilla approach does preserve the original background alignment, however causes the masked areas to degrade into incoherent, temporally unstable blobs (Fig.[2](https://arxiv.org/html/2503.18033v3#S2.F2 "Figure 2 ‣ 2.3. Diffusion Transformers for Video Generation ‣ 2. Related Work ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")a). We attribute this breakdown to a core difference between image and video models: image inpainting ensures spatial consistency within a single frame, while video inpainting must also maintain temporal consistency across frames. Unlike image inpainting, which relies heavily on hallucination, video inpainting must infer missing content from both spatial and temporal context, making it significantly more challenging. We further examine a second zero-shot inpainting method: _Vid2Vid_(HaCohen et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib11)) (an adaptation from Img2Img(Meng et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib24))). This method applies heavy noise inside the mask and lighter noise elsewhere in the latent video, then denoises the entire latent. Vid2Vid effectively removes the target object and synthesizes plausible fills, however, it also introduces artifacts into the background and motion (Fig.[2](https://arxiv.org/html/2503.18033v3#S2.F2 "Figure 2 ‣ 2.3. Diffusion Transformers for Video Generation ‣ 2. Related Work ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")b).

While recent diffusion-based solutions (Bian et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib3); Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)) overcome these issues by training dedicated video diffusion models for object removal, we pose the following question: _Can we develop a training free method that simultaneously (i) convincingly fills the masked region, (ii) preserves the background so that it is indistinguishable from the original video, and (iii) eliminates all residual evidence of the object’s presence, including secondary effects like shadows and reflections?_.

4. Preliminaries: Spatio–Temporal Attention in Video Diffusion Transformers
---------------------------------------------------------------------------

Video diffusion transformers interleave spatio-temporal self-attention modules in each diffusion block to model both fine-grained structure within frames and consistent dynamics across time. Given a video, it’s latent tensor is Z∈ℝ f×w×h×c Z\in\mathbb{R}^{f\times w\times h\times c}, where f f is the number of temporally compressed frames, and w w, h h, and c c are the width, height, and channel dimensions in latent space. We reshape Z Z into Z∈ℝ(f×n)×c Z\in\mathbb{R}^{(f\times n)\times c}, where n=h×w n=h\times w is the number of tokens per frame. Self‐attention is then applied over all f×n f\times n tokens:

A=Attention​(Q​(Z),K​(Z))∈ℝ(f×n)×(f×n).A\;=\;\mathrm{Attention}\bigl(Q(Z),\,K(Z)\bigr)\;\in\;\mathbb{R}^{(f\times n)\times(f\times n)}.

where Q,K∈ℝ w×h×c Q,K\in\mathbb{R}^{w\times h\times c} are the queries and keys, respectively. This matrix A A encodes both spatial and temporal interactions in one operation. We denote tokens by (i,p)(i,p) with i=1,…,f i\!=\!1,\dots,f the frame index and p=1,…,n p\!=\!1,\dots,n the spatial position. _Spatial attention_ within frame i i (i.e. interactions among tokens (i,p)(i,p) and (i,q)(i,q)) is given by the in-frame weights A spatial(i)​(p,q)=A(i,p),(i,q).A_{\mathrm{spatial}}^{(i)}(p,q)\;=\;A_{(i,p),(i,q)}._Temporal attention_ between frame i i to frame j≠i j\neq i (i.e. interactions between tokens (i,p)(i,p) and (j,q)(j,q)) is given by A temporal(i,j)​(p,q)=A(i,p),(j,q).A_{\mathrm{temporal}}^{(i,j)}(p,q)\;=\;A_{(i,p),(j,q)}.

5. Method: OmnimatteZero
------------------------

In this section, we first describe how given a video 𝒱∈ℝ F×W×H×3\mathcal{V}\in\mathbb{R}^{F\times W\times H\times 3} and an object mask for each frame M o​b​j∈{0,1}F×H×W M_{obj}\in\{0,1\}^{F\times H\times W}, one can use off-the-shelf video diffusion models to remove the target object (Section [5.1](https://arxiv.org/html/2503.18033v3#S5.SS1 "5.1. Object Removal ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")) and its associated visual effects (Section [5.2](https://arxiv.org/html/2503.18033v3#S5.SS2 "5.2. Removing Associated Object Effects ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")). Next, we detail our strategy for isolating foreground objects together with their residual effects (Section [5.3](https://arxiv.org/html/2503.18033v3#S5.SS3 "5.3. Foreground Extraction ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")). Finally, we demonstrate how to recombine these object–effect layers onto arbitrary background videos (Section [5.4](https://arxiv.org/html/2503.18033v3#S5.SS4 "5.4. Layer Composition ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")), enabling flexible and realistic video editing.

In summary, our pipeline expands masks to capture object effects, inpaints them for clean backgrounds, isolates foregrounds via latent arithmetic, and seamlessly recomposes them onto new scenes.

### 5.1. Object Removal

Zero-shot video inpainting with diffusion models (Meng et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib24); Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22)) frequently struggles because the model must _hallucinate_ content that is coherent both spatially and temporally ( [Section 3](https://arxiv.org/html/2503.18033v3#S3 "3. Motivation: The failure of image inpainting approaches for videos ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")). Recent studies show that the self-attention mechanism within diffusion models is crucial for maintaining coherence during model generation(Luo et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib23)). However, it remains unclear how self-attention can effectively guide the inpainting process.

Our core observation is that in real-world videos, the necessary background information is often readily available in neighboring frames. This principle has been leveraged in traditional video editing techniques (Wexler et al., [2004](https://arxiv.org/html/2503.18033v3#bib.bib31); Criminisi et al., [2004](https://arxiv.org/html/2503.18033v3#bib.bib7)). However, they often produce non-realistic results or do not scale for long videos. Motivated by this, we introduce a method that explicitly guides a video diffusion model to reconstruct missing pixels by leveraging spatial and temporal context, rather than relying on the model to infer this implicitly. To further enhance spatial inpainting within individual frames, particularly when background details are absent from adjacent frames (e.g., due to static scenes or lack of camera/object motion), we exploit contextual cues from regions surrounding the masked area within the same frame. These temporal and spatial guidance are facilitated through careful manipulations of spatial and temporal self-attention.

We thus introduce two novel modules: _Temporal Attention guidance_ (TAG) and _Spatial Attention Guidance_ (SAG). These modules seamlessly integrate into existing pre-trained video diffusion models, effectively steering the diffusion process toward object removal and coherent background reconstruction.

#### Identifying Potential Background Patches from Neighboring Frames

To accurately inpaint masked areas in a specific frame, it is essential to identify corresponding background patches from neighboring frames, while preserving awareness of the video’s underlying 3D structure. This task can be effectively addressed using Track-Any-Point (TAP-Net) (Doersch et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib8)), a real-time tracking framework. TAP-Net captures spatial and temporal coherence by tracking points from one frame to their corresponding locations across subsequent frames, as illustrated in [Figure 3](https://arxiv.org/html/2503.18033v3#S2.F3 "In 2.3. Diffusion Transformers for Video Generation ‣ 2. Related Work ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")a, where points from frame f i f_{i} are matched across other frames. Formally, given a point p p on the object in frame i i, TAP-Net identifies its corresponding point set among frames C={C j|j≠i}C=\{C_{j}|j\neq i\}. To ensure that only background regions are considered, we discard points in C C that intersect the object mask ℳ\mathcal{M} in their respective frames.

#### Temporal Attention Guidance (TAG)

To effectively guide the denoising process toward inpainting using neighboring frames, we explicitly set the temporal attention score between a foreground point p p (in frame i i) and each of its background correspondences c∈C c\in C to be the mean temporal attention observed between all distinct pairs of corresponding background points (see Figure[3](https://arxiv.org/html/2503.18033v3#S2.F3 "Figure 3 ‣ 2.3. Diffusion Transformers for Video Generation ‣ 2. Related Work ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")b). Formally, we first compute the mean temporal attention

(1)A¯t​e​m​p​o​r​a​l=1|C|​(|C|−1)​∑j=1|C|∑k=1 k≠j|C|A t​e​m​p​o​r​a​l(j,k)​(c j,c k).\bar{A}_{temporal}=\frac{1}{|C|(|C|-1)}{\sum_{j=1}^{|C|}{\sum_{\begin{subarray}{c}k=1\\ k\neq j\end{subarray}}^{|C|}{A^{(j,k)}_{temporal}(c_{j},c_{k})}}}.

Since the attention is bidirectional, the denominator |C|​(|C|−1)|C|(|C|-1) correctly enumerates all ordered pairs (c j,c k)(c_{j},c_{k}) where j≠k j\neq k, ensuring that each directional interaction is counted exactly once.

We then replace the temporal-attention score from p p to every background point c c as follows:

A t​e​m​p​o​r​a​l(i,j)​(p,c j)=A¯t​e​m​p​o​r​a​l,∀c j∈C.A_{temporal}^{(i,j)}(p,c_{j})=\bar{A}_{temporal},\quad\mbox{\Large$\forall$}c_{j}\in C.

This assignment transfers a consensus cue from the entire background set to the foreground point, encouraging consistent inpainting across frames.

#### Spatial Attention Guidance (SAG)

To further improve spatial inpainting within each frame and to address cases where a point lacks correspondences in other frames, we reinforce spatial attention within the same frame. Specifically, for any foreground point p p in frame i i, we set its spatial attention scores with surrounding background points S S to be the mean spatial attention computed among all pairs of background points within the same frame (see Figure [3](https://arxiv.org/html/2503.18033v3#S2.F3 "Figure 3 ‣ 2.3. Diffusion Transformers for Video Generation ‣ 2. Related Work ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")c). Formally:

(2)A¯s​p​a​t​i​a​l=1|S|​(|S|−1)​∑j=1|S|∑k=1 k≠j|S|A s​p​a​t​i​a​l(I)​(s j,s k).\bar{A}_{spatial}=\frac{1}{|S|(|S|-1)}{\sum_{j=1}^{|S|}{\sum_{\begin{subarray}{c}k=1\\ k\neq j\end{subarray}}^{|S|}{A^{(I)}_{spatial}(s_{j},s_{k})}}}.

Finally, we replace the spatial-attention score from p p to every background point s s as follows:

A spatial i​(p,s)=A¯s​p​a​t​i​a​l,∀s∈S.A^{i}_{\text{spatial}}(p,s)=\bar{A}_{spatial},\quad\mbox{\Large$\forall$}s\in S.

This strategy ensures coherent spatial inpainting even in the absence of temporal information.

![Image 4: Refer to caption](https://arxiv.org/html/2503.18033v3/x4.png)

Figure 4. Self-attention maps from (a) LTX Video diffusion model and (b) Stable Diffusion (image based). The spatio-temporal video latent ”attends to object associated effects” (e.g., shadow, reflection) where, image models struggles to capture these associations.††: Description

### 5.2. Removing Associated Object Effects

We are interested in masking the object with its associated effects. Recently, (Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)) showed that pretrained video diffusion models can associate objects with their effects by analyzing self-attention maps between query and key tokens related to the object of interest. They leveraged this insight to train diffusion models for object removal along with its associated footprint. In contrast to (Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)), we propose to directly derive the masks from the attention maps, allowing a training-free object removal approach. Specifically, we apply a single noising and denoising step on the video latent and compute the attention weights between query and key tokens associated with the object. More precisely, for each latent frame i i at diffusion layer l l, we calculate the attention map as follows:

(3)A i l=softmax​(Q i l​(M o​b​j⊙K i l)T c)∈ℝ N×N A_{i}^{l}=\text{softmax}\left(\frac{Q_{i}^{l}(M_{obj}\odot K_{i}^{l})^{T}}{\sqrt{c}}\right)\in{\mathbb{R}}^{N\times N}

where Q i l,K i l∈ℝ w×h×c Q^{l}_{i},K^{l}_{i}\in{\mathbb{R}}^{w\times h\times c} are the queries and keys respectively at layer l l and frame i i, N=w×h N=w\times h and c c is the number of channels of the latent.

We then compute a soft-mask per-frame, ℳ i∈[0,1]w×h×c\mathcal{M}_{i}\in[0,1]^{w\times h\times c}, which is aggregated across all diffusion layers:

(4)ℳ i=1 L​∑l=1 L A i l\mathcal{M}_{i}=\frac{1}{L}\sum_{l=1}^{L}A_{i}^{l}

where L L is the number of layers in the video diffusion model. Then we extend ℳ i\mathcal{M}_{i} to the whole video by concatenating all frame masks channel-wise ℳ o​b​j=concat​{ℳ 1,…​ℳ f}∈ℝ w×h×f\mathcal{M}_{obj}=\text{concat}\{\mathcal{M}_{1},...\mathcal{M}_{f}\}\in{\mathbb{R}}^{w\times h\times f} deriving a soft-mask latent. To obtain a binary mask we perform Otsu thresholding (Otsu, [1979](https://arxiv.org/html/2503.18033v3#bib.bib25)) for each latent frame, M^o​b​j=𝕀​(ℳ o​b​j)\hat{M}_{obj}=\mathbb{I}(\mathcal{M}_{obj}). This new mask replaces the mask M o​b​j M_{obj} provided as input by the user. Figure [4](https://arxiv.org/html/2503.18033v3#S5.F4 "Figure 4 ‣ Spatial Attention Guidance (SAG) ‣ 5.1. Object Removal ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")(a) shows self-attention maps from LTX-Video (HaCohen et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib11)) of two video frames. The attention maps reveal the model’s ability to localize not only primary objects—like the cat and the walking person—but also their associated physical effects, such as reflections and shadows. This demonstrates the model’s robustness in consistently tracking these cues even when similar visual patterns are present elsewhere in the scene.

Interestingly, to the best of our knowledge, this approach has not been explored for masking object effects (e.g shadows) in images. Unlike video diffusion models, image models do not capture object effects from still images (Winter et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib32)). [Figure 4](https://arxiv.org/html/2503.18033v3#S5.F4 "In Spatial Attention Guidance (SAG) ‣ 5.1. Object Removal ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")(b) illustrates this by showing self-attention maps extracted using StableDiffusion(Rombach et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib26)), a text-to-image diffusion model, which demonstrates that the object does not attend to its associated effects. We believe that this aligns with the principle of common fate in Gestalt psychology (Köhler, [1992](https://arxiv.org/html/2503.18033v3#bib.bib14)), which suggests that elements moving together are perceived as part of the same object. Video diffusion models seem to implicitly leverage this principle by grouping objects with their effects through motion.

![Image 5: Refer to caption](https://arxiv.org/html/2503.18033v3/x5.png)

Figure 5. (a) Foreground Extraction: The target object is extracted by latent code arithmetic, subtracting the background video encoding from the object+background latent (Latent Diff). This initially results in distortions, which are later corrected by replacing pixel values using the original video and a user-provided mask (Latent Diff + Pixel injection). (b) Layer Composition: The extracted object layer is added to a new background latent (Latent Addition). To improve blending, a few steps of noising-denoising are applied, yielding a more natural integration of the object into the new scene (Latent Addition + Refinement). See video examples in the supp material.††: Description

Table 1. Quantitative comparison: Background Reconstruction. OmnimatteZero outperforms all omnimatte and video inpainting methods, achieving the best PSNR and LPIPS without training or per-video optimization. It also runs significantly faster, with OmnimatteZero [LTXVideo] at 0.04s per frame. ”-” denotes missing values due to unreported data or unavailable public code.

Scene Movie Kubric Average
Metric PSNR↑\uparrow LPIPS↓\downarrow SSIM↑\uparrow PSNR↑\uparrow LPIPS↓\downarrow SSIM↑\uparrow PSNR↑\uparrow LPIPS↓\downarrow SSIM↑\uparrow T t​r​a​i​n T_{train} (hours)T r​u​n T_{run} (s/frame)
ObjectDrop(Winter et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib32))28.05 0.124-34.22 0.083-31.14 0.104---
Video Repaint [LTXVideo]*(Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22))20.13 0.252-21.15 0.289-20.64 0.271-0 0.4
Video Repaint [Wan2.1]*(Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22))21.44 0.244-24.16 0.261-22.8 0.253-0 32
Temporal Enhance [LTXVideo]*(Luo et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib23))21.33 0.248-23.01 0.281-22.8 0.265-0 0.04
Temporal Enhance [Wan2.1]*(Luo et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib23))21.93 0.222-24.26 0.253-23.01 0.237-0 3.2
Lumiere inpainting(Bar-Tal et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib2))26.62 0.148-31.46 0.157-29.04 0.153--9
Propainter(Zhou et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib36))27.44 0.114-34.67 0.056-31.06 0.085--0.083
DiffuEraser(Zhou et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib36))29.51 0.105-35.19 0.048-32.35 0.077--0.8
Ominmatte(Lu et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib21))21.76 0.239 0.736 26.81 0.207 0.831 24.29 0.223 0.783 3 2.5
D2NeRF(Wu et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib33))---34.99 0.113 0.887---3 2.2
LNA(Kasten et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib13))23.10 0.129 0.847------8.5 0.4
OmnimatteRF(Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18))33.86 0.017 0.981 40.91 0.028 0.970 37.38 0.023 0.975 6 3.5
Generative Omnimatte (Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16))32.69 0.030 0.989 44.07 0.010 0.981 38.38 0.020 0.985-9
OmnimatteZero [LTXVideo] (Ours)35.11 0.014 0.992 44.97 0.010 0.988 40.04 0.012 0.990 0 0.04
OmnimatteZero [Wan2.1] (Ours)34.12 0.017 0.993 45.55 0.006 0.987 39.84 0.011 0.990 0 3.2

### 5.3. Foreground Extraction

We can now use our object removal approach to extract object layers along with their associated effects. To isolate a specific object, we apply our method twice: first, removing all objects from the video, leaving only the background, denoted as V b​g∈ℝ F×W×H×3 V_{bg}\in\mathbb{R}^{F\times W\times H\times 3} with its corresponding latent Z b​g Z_{bg}; second, removing all objects except the target object, resulting in a video of the object with the background, denoted as V o​b​j+b​g∈ℝ F×W×H×3 V_{obj+bg}\in\mathbb{R}^{F\times W\times H\times 3} with its corresponding latent Z o​b​j+b​g Z_{obj+bg}. We can now derive the video of the object isolated from the background by simply subtracting the two latents Z o​b​j=Z o​b​j+b​g−Z b​g Z_{obj}=Z_{obj+bg}-Z_{bg}. Applying thresholding on Z o​b​j Z_{obj} results in a latent that is decoded to a video V o​b​j V_{obj} containing only the object and its associated effects (see [Figure 5](https://arxiv.org/html/2503.18033v3#S5.F5 "In 5.2. Removing Associated Object Effects ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")a Latent Diff). While the extracted effects appear convincing, the object itself often suffers from distortions due to latent values falling outside the diffusion model’s learned distribution. To address this issue, we make use of the information available in the pixel-space. We refine the object’s appearance by replacing its values in the pixel-space with those from the original video, based on the user provided mask:

(5)V o​b​j=M o​b​j p⊙V o​b​j+b​g+(1−M o​b​j p)⊙V o​b​j.V_{obj}=M^{p}_{obj}\odot V_{obj+bg}+\left(1-M^{p}_{obj}\right)\odot V_{obj}.

This correction preserves the object’s fidelity while maintaining its associated effects, resulting in high-quality object layers (see [Figure 5](https://arxiv.org/html/2503.18033v3#S5.F5 "In 5.2. Removing Associated Object Effects ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")a Latent Diff + Pixel Injection). A comparison of OmnimatteZero with other baselines for foreground extraction is provided in the Supplemental.

Alpha-Channel Extraction: The alpha-channel is obtained from the soft mask M i M_{i} (Eq.4) by decoding it with the video VAE using only the spatial and temporal upsampling layers, skipping feature re-encoding. This ensures (1) _softness_, the output remains a soft mask that captures graded transitions around boundaries and effects, and (2) _alignment_, the decoded alpha-channel is upsampled to the original resolution, maintaining pixel-wise correspondence with the RGB frames. The result is a temporally and spatially consistent matte that preserves soft boundaries, shadows, and reflections, enabling realistic compositing and evaluation.

### 5.4. Layer Composition

With the object layers extracted, we can now seamlessly compose them onto new videos by adding the object layer latent to a new background latent Z b​g N Z^{N}_{bg}. Specifically,

(6)Z o​b​j+b​g N=Z b​g N+Z o​b​j.Z^{N}_{obj+bg}=Z^{N}_{bg}+Z_{obj}.

Figure [5](https://arxiv.org/html/2503.18033v3#S5.F5 "Figure 5 ‣ 5.2. Removing Associated Object Effects ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")b (Latent Addition) illustrates the initial result with some residual inconsistencies, which we finally fix, by applying a 3 noising-denoising steps. This process helps smooth transitions between the video background and foreground layers, resulting in a more natural and cohesive video (Figure [5](https://arxiv.org/html/2503.18033v3#S5.F5 "Figure 5 ‣ 5.2. Removing Associated Object Effects ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")b Latent Addition + Refinment).

6. Experiments
--------------

Following (Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)), we evaluate OmnimatteZero on three applications: (1) Background Reconstruction, where the foreground is removed to recover a clean background; (2) Foreground Extraction, where objects are extracted, together with their associated effects (_e.g_. shadows and reflections); and (3) Layer Composition, where extracted elements are reinserted into new backgrounds while preserving visual consistency. For qualitative results, each figure shows one representative frame per video; full videos are in the supplementary material.

![Image 6: Refer to caption](https://arxiv.org/html/2503.18033v3/x6.png)

Figure 6. Qualitative Results: Object removal and background reconstruction. The first row shows input video frames with object masks, while the second row presents the reconstructed backgrounds. Our approach effectively removes objects while preserving fine details, reflections, and textures, demonstrating robustness across diverse scenes. Notice the removal of the cat’s reflection in the mirror and water, the shadow of the dog and bicycle (with the rider), and the bending of the trampoline when removing the jumpers. See video examples in the supplemental material ††: Description

### 6.1. Background Layer Reconstruction

##### Compared methods:

We conducted a comparative evaluation of our approach with several SoTA methods. These methods fall into four categories: (A) Omnimatte methods that are trained to decompose a given video into layers: Omnimatte(Lu et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib21)), D2NeRF(Wu et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib33)), LNA(Kasten et al., [2021](https://arxiv.org/html/2503.18033v3#bib.bib13)), OmnimatteRF(Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18)) and Generative Omnimatte(Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)). (B) Video inpainting methods that are trained to remove objects from a video: RePaint(Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22)) adapted for video, Temporal Enhance(Luo et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib23)) applied to vanilla inpainting (Sec [2](https://arxiv.org/html/2503.18033v3#S2.F2 "Figure 2 ‣ 2.3. Diffusion Transformers for Video Generation ‣ 2. Related Work ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")) which enhances general temporal attention during denoising, Lumiere inpainting(Bar-Tal et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib2)), Propainter(Zhou et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib36)), DiffuEraser(Li et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib17)), and VideoPainter(Bian et al., [2025](https://arxiv.org/html/2503.18033v3#bib.bib3)). Finally, (C) An image inpainting method that is applied for each video frame independently: ObjectDrop(Winter et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib32)).

Datasets and Metrics: We evaluate our method on two standard Omnimatte datasets: Movies(Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18)) and Kubric(Wu et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib33)). These datasets provide object masks for each frame and ground truth background layers for evaluation. All methods are assessed using PSNR, SSIM, and LPIPS metrics to measure the accuracy of background reconstruction, along with comparisons of training and runtime efficiency on a single A100 GPU.

Quantitative results:[Table 1](https://arxiv.org/html/2503.18033v3#S5.T1 "In 5.2. Removing Associated Object Effects ‣ 5. Method: OmnimatteZero ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") presents a comparison of OmnimatteZero with the SoTA Omnimatte and inpainting methods on the Movies and Kubric benchmarks. It shows that OmnimatteZero outperforms existing supervised and self-supervised methods designed for object inpainting or omnimatte. It achieves the highest PSNR and lowest LPIPS on both the Movie and Kubric datasets, demonstrating superior background reconstruction. Specifically, OmnimatteZero [LTXVideo] achieves a PSNR of 35.11 (Movie) and 44.97 (Kubric), surpassing Generative Omnimatte(Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)), all while requiring no training or per-video optimization. Notably, this improvement is not due to a stronger video generation model, as both OmnimatteZero and Video RePaint(Lugmayr et al., [2022](https://arxiv.org/html/2503.18033v3#bib.bib22)) use the same generator, yet Video RePaint records the lowest PSNR and highest LPIPS across all benchmarks.

Our method is also significantly faster. OmnimatteZero [LTXVideo] runs at just 0.04s per frame (or 24 frames per second). These results establish OmnimatteZero as the first training-free, real-time video matting method, offering both superior performance and efficiency.

![Image 7: Refer to caption](https://arxiv.org/html/2503.18033v3/x7.png)

Figure 7. Qualitative Comparison: Foreground Extraction. Foreground extraction comparison between OmnimatteZero and OmnimatteRF (Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18)). Our method accurately captures both the object and its associated effects, such as shadows and reflections, in contrast to OmnimatteRF, missing or distorting shadows (row 1) and reflections (row 2). ††: Description

Qualitative results:[Figure 6](https://arxiv.org/html/2503.18033v3#S6.F6 "In 6. Experiments ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") presents qualitative results of our object removal method across various scenes. The first row shows input video frames with masked objects, while the second row displays the reconstructed backgrounds. The videos include (1) a cat running toward a mirror, (2) a static cat looking left and right, (3) a dog running toward a man, (4) two people walking, and (5) multiple people jumping on a trampoline. Our method effectively removes objects like people and animals even when similar objects and effects appear in the video, while preserving fine details and textures. Notably, in the first two columns, OmnimatteZero eliminates the cat without leaving mirror or water reflections. The last column further demonstrates its ability to remove objects while maintaining scene integrity, even correcting the trampoline’s bending effect after removing the jumper. [Figure 10](https://arxiv.org/html/2503.18033v3#A5.F10 "In Appendix E Comparison to Generative-Omnimatte ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models")[11](https://arxiv.org/html/2503.18033v3#A5.F11 "Figure 11 ‣ Appendix E Comparison to Generative-Omnimatte ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") presents a qualitative comparison of OmnimatteZero with SoTA omnimatte and video inpainting methods. Our method consistently produces cleaner and more temporally coherent background reconstructions with fewer artifacts and distortions, especially in challenging scenes involving motion, shadows, and texture continuity. The figures includes diverse videos such as dogs running on grass, a person walking past a building, a woman walking on the beach, swans in a lake and more. In the first three rows of Figure [11](https://arxiv.org/html/2503.18033v3#A5.F11 "Figure 11 ‣ Appendix E Comparison to Generative-Omnimatte ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models"), OmnimatteZero reconstructs textured and complex backgrounds (e.g., grass, water, sand) without the distortions and ghosting present in OmnimatteRF and DiffuEraser (see red boxes). In all rows of Figure [10](https://arxiv.org/html/2503.18033v3#A5.F10 "Figure 10 ‣ Appendix E Comparison to Generative-Omnimatte ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models"), competing methods leave visible shadow remnants, semantic drift, or object traces, while OmnimatteZero removes foregrounds cleanly and fills in semantically appropriate content.

![Image 8: Refer to caption](https://arxiv.org/html/2503.18033v3/x8.png)

Figure 8. Qualitative Comparison: Layer Composition. The extracted foreground objects, along with their shadows and reflections, are seamlessly integrated into diverse backgrounds, demonstrating the effectiveness of our approach in preserving visual coherence and realism across different scenes. See video examples in the supplemental material††: Description

### 6.2. Foreground Extraction

We aim to extract the foreground object along with its associated effects, such as shadows and reflections. [Figure 7](https://arxiv.org/html/2503.18033v3#S6.F7 "In Compared methods: ‣ 6.1. Background Layer Reconstruction ‣ 6. Experiments ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") compares OmnimatteZero for foreground extraction with OmnimatteRF (Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18)). Our training-free method accurately isolates objects while preserving fine details of their interactions with the scene, such as reflections and shadows. In contrast, OmnimatteRF struggles to fully capture the associated effects. Notably, in the second and third rows, our method correctly extracts both the shadow of the cyclist and the reflection of the cat, while OmnimatteRF either distorts or omits these elements. These results demonstrate that OmnimatteZero provides superior, training-free foreground extraction, effectively handling complex visual effects where existing methods fall short.

### 6.3. Layer Composition

The objective here is to take the extracted foreground layers and seamlessly composite them onto new background layers. Figures [8](https://arxiv.org/html/2503.18033v3#S6.F8 "Figure 8 ‣ Compared methods: ‣ 6.1. Background Layer Reconstruction ‣ 6. Experiments ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") and [12](https://arxiv.org/html/2503.18033v3#A5.F12 "Figure 12 ‣ Appendix E Comparison to Generative-Omnimatte ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") presents the results of OmnimatteZero, highlighting its ability to maintain object integrity, shadows, and reflections while enabling smooth re-composition across different scenes. Notably, it demonstrates how the model adaptively integrates the inserted object into the environment, such as enhancing the cat’s reflection in the clear water stain or adjusting the man’s appearance to match the night lighting.

7. Conclusion and Limitations
-----------------------------

In this work, we introduced _OmnimatteZero_, the first training-free approach for video omnimatte. By leveraging pre-trained video diffusion models together with spatial and temporal attention guidance, OmnimatteZero enables real-time object removal, foreground extraction, and seamless layer recomposition without any additional training or test-time optimization. Extensive experiments demonstrate that our method outperforms supervised and self-supervised baselines in both background reconstruction and multi-object handling, while achieving state-of-the-art runtime efficiency.

Nevertheless, several limitations remain. First, since our pipeline relies on VAE compression and decompression, the reconstructed video may exhibit slight deviations from the original input. Second, the quality of temporal correspondence depends on the accuracy of TAP, which can degrade under heavy occlusions or in low-resolution videos. Third, the fidelity of inpainting is ultimately bounded by the capabilities of the underlying video diffusion model, which may struggle in highly complex or unfamiliar scenes. We believe these limitations will be progressively mitigated as future video generative models continue to improve in visual fidelity, temporal consistency, and robustness. OmnimatteZero provides a fast, flexible, and practical framework that can readily incorporate such advances, paving the way for scalable, real-time video editing applications.

###### Acknowledgements.

We thank Yoni Kasten for his insightful input and valuable contributions to this work.

References
----------

*   (1)
*   Bar-Tal et al. (2024) Omer Bar-Tal, Hila Chefer, Omer Tov, Charles Herrmann, Roni Paiss, Shiran Zada, Ariel Ephrat, Junhwa Hur, Guanghui Liu, Amit Raj, Yuanzhen Li, Michael Rubinstein, Tomer Michaeli, Oliver Wang, Deqing Sun, Tali Dekel, and Inbar Mosseri. 2024. Lumiere: A Space-Time Diffusion Model for Video Generation. 
*   Bian et al. (2025) Yuxuan Bian, Zhaoyang Zhang, Xuan Ju, Mingdeng Cao, Liangbin Xie, Ying Shan, and Qiang Xu. 2025. VideoPainter: Any-length Video Inpainting and Editing with Plug-and-Play Context Control. _SIGGRAPH_ (2025). 
*   Chang et al. (2019) Ya-Liang Chang, Zhe Yu Liu, Kuan-Ying Lee, and Winston H. Hsu. 2019. Free-Form Video Inpainting With 3D Gated Convolution and Temporal PatchGAN. In _ICCV_. 9065–9074. 
*   Chuang et al. (2002) Yung-Yu Chuang, Aseem Agarwala, Brian Curless, David H Salesin, and Richard Szeliski. 2002. Video matting of complex scenes. In _Proceedings of the 29th annual conference on Computer graphics and interactive techniques_. 243–248. 
*   Corneanu et al. (2024) Ciprian Corneanu, Raghudeep Gadde, and Aleix M Martinez. 2024. Latentpaint: Image inpainting in latent space with diffusion models. In _WACV_. 
*   Criminisi et al. (2004) A. Criminisi, P. Perez, and K. Toyama. 2004. Region filling and object removal by exemplar-based image inpainting. _IEEE Transactions on Image Processing_ (2004). 
*   Doersch et al. (2023) Carl Doersch, Yi Yang, Mel Vecerik, Dilara Gokay, Ankush Gupta, Yusuf Aytar, Joao Carreira, and Andrew Zisserman. 2023. TAPIR: Tracking any point with per-frame initialization and temporal refinement. In _ICCV_. 
*   Gao et al. (2020) Chen Gao, Ayush Saraf, Jia-Bin Huang, and Johannes Kopf. 2020. Flow-edge Guided Video Completion. In _ECCV_. 713–729. 
*   Gu et al. (2023) Zeqi Gu, Wenqi Xian, Noah Snavely, and Abe Davis. 2023. FactorMatte: Redefining Video Matting for Re-Composition Tasks. _ACM Transactions on Graphics (TOG)_ (2023). 
*   HaCohen et al. (2024) Yoav HaCohen, Nisan Chiprut, Benny Brazowski, Daniel Shalem, David-Pur Moshe, Eitan Richardson, E.I. Levin, Guy Shiran, Nir Zabari, Ori Gordon, Poriya Panet, Sapir Weissbuch, Victor Kulikov, Yaki Bitterman, Zeev Melumian, and Ofir Bibi. 2024. LTX-Video: Realtime Video Latent Diffusion. _ArXiv_ (2024). 
*   Hu et al. (2020) Yuan-Ting Hu, Heng Wang, Nicolas Ballas, Kristen Grauman, and Alexander G. Schwing. 2020. Proposal-Based Video Completion. In _ECCV_, Vol.12372. 38–54. 
*   Kasten et al. (2021) Yoni Kasten, Dolev Ofri, Oliver Wang, and Tali Dekel. 2021. Layered neural atlases for consistent video editing. _ACM Transactions on Graphics (TOG)_ 40, 6 (2021), 1–12. 
*   Köhler (1992) Wolfgang Köhler. 1992. _Gestalt psychology: The definitive statement of the Gestalt theory_. H. Liveright. 
*   Kong (2024) Weijie Kong. 2024. HunyuanVideo: A Systematic Framework For Large Video Generative Models. 
*   Lee et al. (2024) Yao-Chih Lee, Erika Lu, Sarah Rumbley, Michal Geyer, Jia-Bin Huang, Tali Dekel, and Forrester Cole. 2024. Generative Omnimatte: Learning to Decompose Video into Layers. _CVPR_ (2024). 
*   Li et al. (2025) Xiaowen Li, Haolan Xue, Peiran Ren, and Liefeng Bo. 2025. DiffuEraser: A Diffusion Model for Video Inpainting. 
*   Lin et al. (2023) Geng Lin, Chen Gao, Jia-Bin Huang, Changil Kim, Yipeng Wang, Matthias Zwicker, and Ayush Saraf. 2023. OmnimatteRF: Robust Omnimatte with 3D Background Modeling. In _ICCV_. 
*   Lu et al. (2022) Erika Lu, Forrester Cole, Tali Dekel, Weidi Xie, Andrew Zisserman, William T Freeman, and Michael Rubinstein. 2022. Associating Objects and Their Effects in Video Through Coordination Games. In _NeurIPS_. 
*   Lu et al. (2020) Erika Lu, Forrester Cole, Tali Dekel, Weidi Xie, Andrew Zisserman, David Salesin, William T Freeman, and Michael Rubinstein. 2020. Layered neural rendering for retiming people in video. _arXiv:2009.07833_ (2020). 
*   Lu et al. (2021) Erika Lu, Forrester Cole, Tali Dekel, Andrew Zisserman, William T Freeman, and Michael Rubinstein. 2021. Omnimatte: Associating Objects and Their Effects in Video. In _CVPR_. 
*   Lugmayr et al. (2022) Andreas Lugmayr, Martin Danelljan, Andres Romero, Fisher Yu, Radu Timofte, and Luc Van Gool. 2022. Repaint: Inpainting using denoising diffusion probabilistic models. In _CVPR_. 
*   Luo et al. (2025) Yang Luo, Xuanlei Zhao, Mengzhao Chen, Kaipeng Zhang, Wenqi Shao, Kai Wang, Zhangyang Wang, and Yang You. 2025. Enhance-A-Video: Better Generated Video for Free. _ArXiv_ (2025). 
*   Meng et al. (2022) Chenlin Meng, Yutong He, Yang Song, Jiaming Song, Jiajun Wu, Jun-Yan Zhu, and Stefano Ermon. 2022. SDEdit: Guided Image Synthesis and Editing with Stochastic Differential Equations. In _ICLR_. 
*   Otsu (1979) Nobuyuki Otsu. 1979. A Threshold Selection Method from Gray-Level Histograms. _IEEE Trans. Syst. Man Cybern._ (1979). 
*   Rombach et al. (2022) Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Björn Ommer. 2022. High-resolution image synthesis with latent diffusion models. In _CVPR_. 
*   Suhail et al. (2023) Mohammed Suhail, Erika Lu, Zhengqi Li, Noah Snavely, Leonid Sigal, and Forrester Cole. 2023. Omnimatte3D: Associating objects and their effects in unconstrained monocular video. In _CVPR_. 
*   video (2025) Wan video. 2025. Wan: Open and Advanced Large-Scale Video Generative Models. [https://github.com/Wan-Video/Wan2.1](https://github.com/Wan-Video/Wan2.1). 
*   Wang et al. (2019) Chuan Wang, Haibin Huang, Xiaoguang Han, and Jue Wang. 2019. Video Inpainting by Jointly Learning Temporal Structure and Spatial Details. In _AAAI_. 5232–5239. 
*   Wang and Adelson (1994) J.Y.A. Wang and E.H. Adelson. 1994. Representing moving images with layers. _IEEE Transactions on Image Processing_ (1994). 
*   Wexler et al. (2004) Y. Wexler, E. Shechtman, and M. Irani. 2004. Space-time video completion. In _CVPR_. 
*   Winter et al. (2024) Daniel Winter, Matan Cohen, Shlomi Fruchter, Yael Pritch, Alex Rav-Acha, and Yedid Hoshen. 2024. ObjectDrop: Bootstrapping Counterfactuals for Photorealistic Object Removal and Insertion. 
*   Wu et al. (2024) Tianhao Wu, Fangcheng Zhong, Andrea Tagliasacchi, Forrester Cole, and Cengiz Oztireli. 2024. D 2 NeRF: Self-Supervised Decoupling of Dynamic and Static Objects from a Monocular Video. 
*   Zhang et al. (2022a) Kaidong Zhang, Jingjing Fu, and Dong Liu. 2022a. Flow-Guided Transformer for Video Inpainting. In _ECCV_, Vol.13678. 74–90. 
*   Zhang et al. (2022b) Kaidong Zhang, Jingjing Fu, and Dong Liu. 2022b. Inertia-Guided Flow Completion and Style Fusion for Video Inpainting. In _CVPR_. 5972–5981. 
*   Zhou et al. (2023) Shangchen Zhou, Chongyi Li, Kelvin C.K Chan, and Chen Change Loy. 2023. ProPainter: Improving Propagation and Transformer for Video Inpainting. In _ICCV_. 

OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models

DVIR SAMUEL, Bar-Ilan University & OriginAI, Israel

MATAN LEVY, The Hebrew University of Jerusalem, Israel

NIR DARSHAN, OriginAI, Israel

GAL CHECHIK, Bar-Ilan University & NVIDIA Research, Israel

RAMI BEN-ARI, OriginAI, Israel

Appendix A Implementation Details
---------------------------------

We apply OmnimatteZero using two video diffusion models: LTXVideo (HaCohen et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib11)) v0.9.1 and Wan2.1(video, [2025](https://arxiv.org/html/2503.18033v3#bib.bib28)), both running with T steps=30 T_{\text{steps}}=30 denoising steps. The guidance scale was set to 0 (_i.e_. no prompt) as we found no major effect of the prompt on the process, and all result videos were generated using the same random seed.

Quantitative and qualitative results of baselines were obtained from the respective authors. All qualitative results in this paper are based on LTXVideo, as it shows minimal visual differences from Wan2.1. Additionally, due to space constraints, each figure displays a single frame per video for qualitative results. Full videos are available in the supplementary material.

Latent masking: Applying a given mask video directly in latent space is challenging due to the unclear mapping from pixel space to the latent space. We start by taking the object masks (per-frame) and computing a binary video, where the frames are binary images, and pass this video as an RGB input (with duplicated channels) through the VAE encoder as well. This process produces a latent representation where high values indicate the masked object, enabling its spatio-temporal footprint identification via simple thresholding.

Appendix B Ablation Study
-------------------------

To assess the individual contributions of our key architectural components, we perform a series of ablation studies on the Movie benchmark using the LTXVideo dataset(HaCohen et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib11)). Quantitative results are reported in terms of PSNR.

### B.1. Effect of Temporal and Spatial Attention Guidance

We first analyze the impact of temporal and spatial attention mechanisms on reconstruction quality:

Table 2. Effect of temporal and spatial attention guidance. Temporal guidance contributes most significantly, with the highest quality achieved when both cues are combined.

Results indicate that temporal attention is the primary contributor to reconstruction fidelity, with a PSNR improvement of nearly 10 points over the baseline. Spatial attention offers complementary benefits. When integrated, the two mechanisms produce a substantial synergistic effect, resulting in the highest overall performance.

### B.2. Influence of Point Sampling in Track-Any-Point

Next, we evaluate the effect of varying the sampling density of points from the object mask in the Track-Any-Point module:

Table 3. Effect of point sampling density. Using 60% of object pixels is sufficient to match the maximum reconstruction quality.

We observe that increasing the proportion of sampled object pixels leads to improved reconstruction quality, with performance saturating at approximately 60% coverage. This suggests that high-fidelity results can be attained with moderately dense sampling, highlighting the efficiency of our approach in establishing accurate correspondences.

### B.3. Impact of Effect-Aware Masking

We investigate the influence of explicitly incorporating associated object-induced visual effects—such as shadows and reflections—into the masking process:

Table 4. Effect of including associated visual effects (e.g., shadows, reflections) in the mask. These effects are essential for clean background reconstruction.

![Image 9: Refer to caption](https://arxiv.org/html/2503.18033v3/x9.png)

Figure 9. Qualitative examples of multi-object extraction. OmnimatteZero successfully separates multiple dynamic foreground objects (e.g., person, dog, puppies) along with their associated effects such as shadows. The results demonstrate that our method scales to complex scenes with several independently moving objects, preserving fine details and temporal consistency.††: Description

The inclusion of effect-aware masks yields a substantial improvement of +6.0 PSNR, highlighting the critical role of accurately capturing the extended influence of foreground objects on their surrounding environment. This result underscores the importance of modeling object footprints for realistic scene reconstruction.

Appendix C Multi-Object Extraction
----------------------------------

Figure[9](https://arxiv.org/html/2503.18033v3#A2.F9 "Figure 9 ‣ B.3. Impact of Effect-Aware Masking ‣ Appendix B Ablation Study ‣ OmnimatteZero: Fast Training-free Omnimatte with Pre-trained Video Diffusion Models") provides qualitative examples of multiple foreground extractions from a single video. It shows that OmnimatteZero can reliably isolate several dynamic objects together with their associated effects, such as shadows and reflections. Our method maintains temporal consistency and preserves fine details across all layers. This demonstrates the scalability of our framework to complex multi-object scenes. Full video results are provided in the supplementary material.

Appendix D Handling Object Occlusion
------------------------------------

We further evaluated the ability of our method to handle object occlusion, a particularly challenging scenario for video decomposition. To this end, we constructed a benchmark of 20 videos containing significant occlusions between objects. In these experiments, our method successfully produced coherent object removal and background reconstruction in 60% of the cases. This substantially outperforms Generative-Omnimatte(Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)), which succeeded in only 30% of cases, and OmnimatteRF(Lin et al., [2023](https://arxiv.org/html/2503.18033v3#bib.bib18)), which achieved just 1%. These results indicate that the proposed spatial and temporal attention guidance enables improved robustness to occlusions compared to prior approaches. Nonetheless, occlusion remains a difficult challenge, as heavy overlaps can degrade tracking accuracy and limit the available background context. We believe that future advancements in video generative models and more robust tracking mechanisms will further enhance performance in these scenarios.

Appendix E Comparison to Generative-Omnimatte
---------------------------------------------

Here we provide further discussion and comparison with Generative-Omnimatte(Lee et al., [2024](https://arxiv.org/html/2503.18033v3#bib.bib16)). Generative-Omnimatte is a supervised video diffusion method for object removal. While effective in certain cases, it requires annotated training data, per-video test-time optimization, and incurs several seconds of computation per frame. Moreover, it often struggles in scenes containing multiple objects and complex interactions. In contrast, our approach is training-free, requires no test-time optimization, and achieves real-time performance (0.04 seconds per frame on an A100 GPU). Thanks to the proposed spatial and temporal attention guidance, our method can robustly handle scenes with multiple objects while maintaining both temporal consistency and accurate background reconstruction. To further evaluate this difference, we conducted an additional comparison on 20 challenging videos, each containing more than five objects. In these settings, we attempted to remove several objects simultaneously. Our method succeeded in all cases, whereas Generative-Omnimatte failed on 90% of the videos, leaving visible artifacts or incomplete removals. These results highlight the practical advantage of our approach in complex, multi-object scenarios, where supervised and optimization-based methods face severe limitations.

![Image 10: Refer to caption](https://arxiv.org/html/2503.18033v3/x10.png)

Figure 10. Qualitative comparison with state-of-the-art video inpainting methods. OmnimatteZero produces clean, temporally consistent background reconstructions across a diverse range of scenes, including dynamic motion, shadows, reflections, and fine textures. Compared to other methods, it avoids common artifacts such as ghosting, blur, and shadow remnants (highlighted in red boxes), successfully filling in complex backgrounds across varying temporal and spatial contexts. Gray frames indicate failure cases where the inpainting method returned an error. See the supplementary material for full videos.††: Description

![Image 11: Refer to caption](https://arxiv.org/html/2503.18033v3/x11.png)

Figure 11. Qualitative comparison with state-of-the-art video inpainting methods. OmnimatteZero achieves clean, temporally consistent background reconstructions across diverse scenes, preserving fine textures, shadows, and reflections. Compared to prior methods, it avoids common artifacts such as ghosting, blur, and residual shadows (highlighted in red). Gray frames indicate failure cases where the method returned an error. See supplementary material for full video results.††: Description

![Image 12: Refer to caption](https://arxiv.org/html/2503.18033v3/x12.png)

Figure 12. Qualitative Comparison: Layered Composition. From left to right: the original video frame, the extracted foreground (including shadows and reflections), the target background, and our final composite. Across four diverse examples (a swan, a cat, a bicyclist, and a dog), our method preserves accurate shadows, reflections, and object–scene coherence, yielding visually seamless results. See the supplementary material for full videos. ††: Description
