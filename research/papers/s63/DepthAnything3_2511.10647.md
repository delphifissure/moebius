Title: Recovering the Visual Space from Any Views

URL Source: https://arxiv.org/html/2511.10647

Published Time: Wed, 17 Dec 2025 23:35:59 GMT

Markdown Content:
]ByteDance Seed \contribution[†]Project Lead \contribution[*]Equal Contribution

Depth Anything 3: 

Recovering the Visual Space from Any Views
--------------------------------------------------------------

Sili Chen Jun Hao Liew Donny Y. Chen Zhenyu Li Guang Shi Jiashi Feng Bingyi Kang [

###### Abstract

We present Depth Anything 3 (DA3), a model that predicts spatially consistent geometry from an arbitrary number of visual inputs, with or without known camera poses. In pursuit of minimal modeling, DA3 yields two key insights: a single plain transformer (e.g., vanilla DINO encoder) is sufficient as a backbone without architectural specialization, and a singular depth-ray prediction target obviates the need for complex multi-task learning. Through our teacher-student training paradigm, the model achieves a level of detail and generalization on par with Depth Anything 2 (DA2). We establish a new visual geometry benchmark covering camera pose estimation, any-view geometry and visual rendering. On this benchmark, DA3 sets a new state-of-the-art across all tasks, surpassing prior SOTA VGGT by an average of 35.7% in camera pose accuracy and 23.6% in geometric accuracy. Moreover, it outperforms DA2 in monocular depth estimation. All models are trained exclusively on public academic datasets.

![Image 1: [Uncaptioned image]](https://arxiv.org/html/2511.10647v1/x1.png)1 1 footnotetext: “Depth Anything 3” marks a new generation for the series, expanding from monocular to any-view inputs, built on our conviction that depth is the cornerstone of understanding the physical world.
###### Contents

1.   [1 Introduction](https://arxiv.org/html/2511.10647v1#S1 "In Depth Anything 3: Recovering the Visual Space from Any Views")
2.   [2 Related Work](https://arxiv.org/html/2511.10647v1#S2 "In Depth Anything 3: Recovering the Visual Space from Any Views")
3.   [3 Depth Anything 3](https://arxiv.org/html/2511.10647v1#S3 "In Depth Anything 3: Recovering the Visual Space from Any Views")
    1.   [3.1 Formulation](https://arxiv.org/html/2511.10647v1#S3.SS1 "In 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    2.   [3.2 Architecture](https://arxiv.org/html/2511.10647v1#S3.SS2 "In 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    3.   [3.3 Training](https://arxiv.org/html/2511.10647v1#S3.SS3 "In 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    4.   [3.4 Implementation Details](https://arxiv.org/html/2511.10647v1#S3.SS4 "In 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

4.   [4 Teacher-Student Learning](https://arxiv.org/html/2511.10647v1#S4 "In Depth Anything 3: Recovering the Visual Space from Any Views")
    1.   [4.1 Constructing the Teacher Model](https://arxiv.org/html/2511.10647v1#S4.SS1 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    2.   [4.2 Teaching Depth Anything 3](https://arxiv.org/html/2511.10647v1#S4.SS2 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    3.   [4.3 Teaching Monocular Model](https://arxiv.org/html/2511.10647v1#S4.SS3 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    4.   [4.4 Teaching Metric Model](https://arxiv.org/html/2511.10647v1#S4.SS4 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

5.   [5 Application: Feed-Forward 3D Gaussian Splattings](https://arxiv.org/html/2511.10647v1#S5 "In Depth Anything 3: Recovering the Visual Space from Any Views")
    1.   [5.1 Pose-Conditioned Feed-Forward 3DGS](https://arxiv.org/html/2511.10647v1#S5.SS1 "In 5 Application: Feed-Forward 3D Gaussian Splattings ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    2.   [5.2 Pose-Adaptive Feed-Forward 3DGS](https://arxiv.org/html/2511.10647v1#S5.SS2 "In 5 Application: Feed-Forward 3D Gaussian Splattings ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    3.   [5.3 Implementation Details](https://arxiv.org/html/2511.10647v1#S5.SS3 "In 5 Application: Feed-Forward 3D Gaussian Splattings ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

6.   [6 Visual Geometry Benchmark](https://arxiv.org/html/2511.10647v1#S6 "In Depth Anything 3: Recovering the Visual Space from Any Views")
    1.   [6.1 Benchmark Pipeline](https://arxiv.org/html/2511.10647v1#S6.SS1 "In 6 Visual Geometry Benchmark ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    2.   [6.2 Metrics](https://arxiv.org/html/2511.10647v1#S6.SS2 "In 6 Visual Geometry Benchmark ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    3.   [6.3 Datasets](https://arxiv.org/html/2511.10647v1#S6.SS3 "In 6 Visual Geometry Benchmark ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

7.   [7 Experiments](https://arxiv.org/html/2511.10647v1#S7 "In Depth Anything 3: Recovering the Visual Space from Any Views")
    1.   [7.1 Comparison with State of the Art](https://arxiv.org/html/2511.10647v1#S7.SS1 "In 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    2.   [7.2 Analysis for Depth Anything 3](https://arxiv.org/html/2511.10647v1#S7.SS2 "In 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
        1.   [7.2.1 Sufficiency of the Depth-Ray Representation](https://arxiv.org/html/2511.10647v1#S7.SS2.SSS1 "In 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
        2.   [7.2.2 Sufficiency of a Single Plain Transformer](https://arxiv.org/html/2511.10647v1#S7.SS2.SSS2 "In 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
        3.   [7.2.3 Ablation and Analysis](https://arxiv.org/html/2511.10647v1#S7.SS2.SSS3 "In 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

    3.   [7.3 Analysis for Depth-Anything-3-Monocular](https://arxiv.org/html/2511.10647v1#S7.SS3 "In 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
        1.   [7.3.1 Teacher Model](https://arxiv.org/html/2511.10647v1#S7.SS3.SSS1 "In 7.3 Analysis for Depth-Anything-3-Monocular ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
        2.   [7.3.2 Student Model](https://arxiv.org/html/2511.10647v1#S7.SS3.SSS2 "In 7.3 Analysis for Depth-Anything-3-Monocular ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

    4.   [7.4 Analysis for Depth-Anything-3-Metric](https://arxiv.org/html/2511.10647v1#S7.SS4 "In 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")
    5.   [7.5 Analysis for Feed-forward 3DGS](https://arxiv.org/html/2511.10647v1#S7.SS5 "In 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

8.   [8 Conclusion and Discussion](https://arxiv.org/html/2511.10647v1#S8 "In Depth Anything 3: Recovering the Visual Space from Any Views")
9.   [A Data Processing](https://arxiv.org/html/2511.10647v1#A1 "In Depth Anything 3: Recovering the Visual Space from Any Views")

![Image 2: Refer to caption](https://arxiv.org/html/2511.10647v1/x2.png)

Figure 1:  Given any number of images and optional camera poses, Depth Anything 3 reconstructs the visual space, producing consistent depth and ray maps that can be fused into accurate point clouds, resulting in high-fidelity 3D Gaussians and geometry. It significantlyoutperforms VGGT in multi-view geometry and pose accuracy; with monocular inputs, it also surpasses Depth Anything 2 while matching its detail and robustness. 

1 Introduction
--------------

The ability to perceive and understand 3D spatial information from visual input is a cornerstone of human spatial intelligence [arterberry2000perception] and a critical requirement for applications like robotics and mixed reality. This fundamental capability has inspired a wide array of 3D vision tasks, including Monocular Depth Estimation [eigen2014depth], Structure from Motion [snavely2006photo], Multi-View Stereo [seitz2006comparison] and Simultaneous Localization and Mapping [mur2015orb]. Despite the strong conceptual overlap between these tasks—often differing by only a single factor, such as the number of input views—the prevailing paradigm has been to develop highly specialized models for each one. While recent efforts [wang2024dust3r, wang2025vggt] have explored unified models to address multiple tasks simultaneously, they typically suffer from key limitations: they often rely on complex, bespoke architectures, are trained via joint optimization over tasks from scratch, and consequently cannot effectively leverage large-scale pretrained models.

In this work, we step back from established 3D task definitions and return to a more fundamental goal inspired by human spatial intelligence: recovering 3D structure from arbitrary visual inputs, be it a single image, multiple views of a scene, or a video stream. Forsaking intricate architectural engineering, we pursue a minimal modeling strategy guided by two central questions. First, is there a minimal set of prediction targets, or is joint modeling across numerous 3D tasks necessary? Second, can a single plain transformer suffice for this objective? Our work provides an affirmative answer to both. We present Depth Anything 3, a single transformer model trained exclusively for joint any-view depth and pose estimation via a specially chosen ray representation. We demonstrate that this minimal approach is sufficient to reconstruct the visual space from any number of images, with or without known camera poses.

Depth Anything 3 formulates the above geometric reconstruction target as a dense prediction task. For a given set of N N input images, the model is trained to output N N corresponding depth maps and ray maps, each pixel-aligned with its respective input. The architecture to achieve this begins with a standard pretrained vision transformer (e.g., oquab2023dinov2), as its backbone, leveraging its powerful feature extraction capabilities. To handle arbitrary view counts, we introduce a key modification: an input-adaptive cross-view self-attention mechanism. This module dynamically rearranges tokens during the forward pass in selected layers, enabling efficient information exchange across all views. For the final prediction, we propose a new dual DPT head designed to jointly outputs both depth and ray values, by processing the same set of features with distinct fusion parameters. To enhance flexibility, the model can optionally incorporate known camera poses via a simple camera encoder, allowing it to adapt to various practical settings. This overall design results in a clean and scalable architecture that directly inherits the scaling properties of its pretrained backbone.

We train Depth Anything 3 via a teacher-student paradigm to unify diverse training data, which is necessary for a generalist model. Our data sources include varied formats like real-world depth camera captures (e.g., baruch2021arkitscenes), 3D reconstruction (e.g., reizenstein2021common), and synthetic data, where real-world depth may be of poor quality ([Fig.˜4](https://arxiv.org/html/2511.10647v1#S4.F4 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views")). To resolve this, we adopt a pseudo-labeling strategy inspired by prior works [yang2024depth, yang2024depthv2]. Specifically, we train a powerful teacher monocular depth model on synthetic data to generate dense, high-quality pseudo-depth for all real-world data. Crucially, to preserve geometric integrity, we align these dense pseudo-depth maps with the original sparse or noisy depth. This approach proved remarkably effective, significantly enhancing label detail and completeness without sacrificing the geometric accuracy.

To better evaluate our model and track progress in the field, we establish a comprehensive benchmark for assessing geometry and pose accuracy. The benchmark comprises 5 distinct datasets, totaling over 89 scenes, ranging from object-level to indoor and outdoor environments. By directly evaluating pose accuracy across scenes and fusing the predicted pose and depth into a 3D point cloud for accuracy assessment, the benchmark faithfully measures the pose and depth accuracy of visual geometry estimators. Experiments show that our model achieves state-of-the-art performance on 18 out of 20 settings. Moreover, on standard monocular benchmarks, our model outperforms Depth Anything 2 [yang2024depthv2].

To further demonstrate the fundamental capability of Depth Anything 3 in advancing other 3D vision tasks, we introduce a challenging benchmark for feed-forward novel view synthesis (FF-NVS), comprising over 160 scenes. We adhere to the minimal modeling strategy and fine-tune our model with an additional DPT head to predict pixel-aligned 3D Gaussian parameters. Extensive experiments yield two key findings: 1) fine-tuning a geometry foundation model for NVS substantially outperforms highly specialized task-specific models [xu2025depthsplat]; 2) enhanced geometric reconstruction capability directly correlates with improved FF-NVS performance, establishing Depth Anything 3 as the optimal backbone for this task.

2 Related Work
--------------

##### Multi-view visual geometry estimation.

Traditional systems [schoenberger2016sfm, schoenberger2016mvs] decompose reconstruction into feature detection and matching, robust relative pose estimation, incremental or global SfM with bundle adjustment, and dense multi-view stereo for per-view depth and fused point clouds. These methods remain strong on well-textured scenes, but their modularity and brittle correspondences complicate robustness under low texture, specularities, or large viewpoint changes. Early learning methods injected robustness at the component level: learned detectors [detone2018superpoint], descriptors for matching [dusmanu2019d2], and differentiable optimization layers that expose pose/depth updates to gradient flow [he2024detector, guo2025multi, pan2024global]. On the dense side, cost-volume networks [yao2018mvsnet, xu2023iterative] for MVS replaced hand-crafted regularization with 3D CNNs, improving depth accuracy especially at large baselines and thin structures compared with classical PatchMatch. Early end-to-end approaches [teed2018deepv2d, wang2024vggsfm] moved beyond modular SfM/MVS pipelines by directly regressing camera poses and per-image depths from pairs of images. These approaches reduced engineering complexity and demonstrated the feasibility of learned joint depth pose estimation, but they often struggled with scalability, generalization, and handling arbitrary input cardinalities.

A turning point came with DUSt3R [dust3r], which leveraged transformers to directly predict point map between two views and compute both depth and relative pose in a purely feed-forward manner. This work laid the foundation for subsequent transformer-based methods aiming to unify multi-view geometry estimation at scale. Follow-up models extended this paradigm with multi-view inputs [fast3r, cut3r, Mv-dust3r+, must3r], video input [monst3r, cut3r, murai2025mast3r, deng2025vggtlong], robust correspondence modeling [mast3r], camera parameter injection [jang2025pow3r, keetha2025mapanything], large-scale SfM [deng2025sailrecon], SLAM applications [maggio2025vggtslam], and view synthesis with 3D Gaussians [flare, smart2024splatt3r, charatan2024pixelsplat, chen2024mvsplat, jiang2025anysplat, xu2025depthsplat]. Among these, [wang2025vggt] push accuracy to a new level through large-scale training, a multi-stage architecture, and redundancy in design. In contrast, we focus on a minimal modeling strategy built around a single, simple transformer.

##### Monocular depth estimation.

Early monocular depth estimation methods relied on fully supervised learning on single-domain datasets, which often produced models specialized to either indoor rooms [silberman2012indoor] or outdoor driving scenes [geiger2013vision]. These early deep models achieved good accuracy within their training domain but struggled to generalize to novel environments, highlighting the challenge of cross-domain depth prediction. Modern generalist approaches [yang2024depth, yang2024depthv2, wang2025moge, bochkovskii2024depth, yin2023metric3d, ke2024repurposing] exemplify this trend by leveraging massive multi-dataset training and advanced architectures like vision transformers [ranftl2021vision] or DiT [peebles2023scalable]. Trained on millions of images, they learn broad visual cues and incorporate techniques such as affine-invariant depth normalization. In contrast, our method is primarily designed for a unified visual geometry estimation task, yet it still demonstrates competitive monocular depth performance.

##### Feed-Forward Novel View Synthesis

Novel view synthesis (NVS) has long been a core problem in computer vision and graphics [levoy1996light, heigl1999plenoptic, buehler2001unstructured], and interest has increased with the rise of neural rendering [sitzmann2019scene, sitzmann2021light, mildenhall2020nerf, kerbl20233d, govindarajan2025radiant]. A particularly promising direction is feed-forward NVS, which produces 3D representations in a single pass through an image-to-3D network, avoiding tedious per-scene optimization. Early methods adopted NeRF as the underlying 3D representation [yu2021pixelnerf, chen2021mvsnerf, lin2022efficient, chen2025explicit, hong2024lrm, xu2024murf], but recent work has largely shifted to 3DGS due to its explicit structure and real-time rendering. Representative approaches improve image-to-3D networks with geometry priors, e.g., epipolar attention [charatan2024pixelsplat], cost volumes [chen2024mvsplat], and depth priors [xu2024murf]. More recently, multi-view geometry foundation models [dust3r, Mv-dust3r+, fast3r, wang2025vggt] have been integrated to improve modeling capacity, particularly in pose-free settings, yet methods built upon such models are often evaluated by relying on a single chosen foundation model [smart2024splatt3r, ye2024no, jiang2025anysplat]. Here, we systematically benchmark the contribution of different geometry foundation models to NVS and propose strategies to better exploit them, enabling feed-forward 3DGS to handle both posed and pose-free inputs, variable numbers of views, and arbitrary resolutions.

![Image 3: Refer to caption](https://arxiv.org/html/2511.10647v1/figs/pdfs/pipeline.png)

Figure 2: Pipeline of Depth Anything 3. Depth Anything 3 employs a single transformer (vanilla DINOv2 model) without any architectural modifications. To enable cross-view reasoning, an input-adaptive cross-view self-attention mechanism is introduced. A dual-DPT head is used to predict depth and ray maps from visual tokens. Camera parameters, if available, are encoded as camera tokens and concatenated with patch tokens, participating in all attention operations. 

3 Depth Anything 3
------------------

We tackle the recovery of consistent 3D geometry from diverse visual inputs—single image, multi-view collections, or videos—and optionally incorporate known camera poses when available.

### 3.1 Formulation

We denote the input as ℐ={𝐈 i}i=1 N v\mathcal{I}=\{\mathbf{I}_{i}\}_{i=1}^{N_{v}} with each 𝐈 i∈ℝ H×W×3\mathbf{I}_{i}\in\mathbb{R}^{H\times W\times 3}. For N v=1 N_{v}=1 this is a monocular image, and for N v>1 N_{v}>1 it represents a video or multi-view set. Each image has depth 𝐃 i∈ℝ H×W\mathbf{D}_{i}\in\mathbb{R}^{H\times W}, camera extrinsics [𝐑 i∣𝐭 i]\big[\mathbf{R}_{i}\mid\mathbf{t}_{i}\big], and intrinsics 𝐊 i\mathbf{K}_{i}. The camera can also be represented as 𝐯 i∈ℝ 9\mathbf{v}_{i}\in\mathbb{R}^{9} with translation 𝐭 i∈ℝ 3\mathbf{t}_{i}\in\mathbb{R}^{3}, rotation quaternion 𝐪 i∈ℝ 4\mathbf{q}_{i}\in\mathbb{R}^{4}, and FOV parameters 𝐟 i∈ℝ 2\mathbf{f}_{i}\in\mathbb{R}^{2}. A pixel 𝐩=(u,v,1)⊤\mathbf{p}=(u,v,1)^{\top} projects to a 3D point 𝐏=(X,Y,Z,1)⊤\mathbf{P}=(X,Y,Z,1)^{\top} by

𝐏=𝐑 i​(𝐃 i​(u,v)​𝐊 i−1​𝐩)+𝐭 i,\mathbf{P}=\mathbf{R}_{i}\big(\mathbf{D}_{i}(u,v)\,\mathbf{K}_{i}^{-1}\mathbf{p}\big)+\mathbf{t}_{i},

through which the underlying 3D visual space can be faithfully recovered.

##### Depth-ray representation.

Predicting a valid rotation matrix 𝐑 i\mathbf{R}_{i} is challenging due to the orthogonality constraint. To avoid this, we represent camera pose implicitly with a per-pixel ray map, aligned with the input image and depth map. For each pixel 𝐩\mathbf{p}, the camera ray 𝐫∈ℝ 6\mathbf{r}\in\mathbb{R}^{6} is defined by its origin 𝐭∈ℝ 3\mathbf{t}\in\mathbb{R}^{3} and direction 𝐝∈ℝ 3\mathbf{d}\in\mathbb{R}^{3}: 𝐫=(𝐭,𝐝)\mathbf{r}=(\mathbf{t},\mathbf{d}). The direction is obtained by backprojecting 𝐩\mathbf{p} into the camera frame and rotating it to the world frame: 𝐝=𝐑𝐊−1​𝐩.\mathbf{d}=\mathbf{R}\mathbf{K}^{-1}\mathbf{p}. The dense ray map 𝐌∈ℝ H×W×6\mathbf{M}\in\mathbb{R}^{H\times W\times 6} stores these parameters for all pixels. We do not normalize 𝐝\mathbf{d}, so its magnitude preserves the projection scale. Thus, a 3D point in world coordinates is simply 𝐏=𝐭+𝐃​(u,v)⋅𝐝.{\mathbf{P}}={\mathbf{t}}+\mathbf{D}(u,v)\cdot\mathbf{d}. This formulation enables consistent point cloud generation by combining predicted depth and ray maps through element-wise operations.

##### Deriving Camera Parameters from the Ray Map.

Given an input image 𝐈∈ℝ H×W×3\mathbf{I}\in\mathbb{R}^{H\times W\times 3}, the corresponding ray map is denoted by 𝐌∈ℝ H×W×6\mathbf{M}\in\mathbb{R}^{H\times W\times 6}. This map comprises per-pixel ray origins, stored in the first three channels (𝐌(:,:,:3)\mathbf{M}(:,:,:3)), and ray directions, stored in the last three (𝐌(:,:,3:)\mathbf{M}(:,:,3:)).

First, the camera center 𝐭 c\mathbf{t}_{c} is estimated by averaging the per-pixel ray origin vectors:

𝐭 c=1 H×W∑h=1 H∑w=1 W 𝐌(h,w,:3).\mathbf{t}_{c}=\frac{1}{H\times W}\sum_{h=1}^{H}\sum_{w=1}^{W}\mathbf{M}(h,w,:3).(1)

To estimate the rotation 𝐑\mathbf{R} and intrinsics 𝐊\mathbf{K}, we formulate the problem as finding a homography 𝐇\mathbf{H}. We begin by defining a “identity” camera with an identity intrinsics matrix, 𝐊 I=𝐈\mathbf{K}_{I}=\mathbf{I}. For a given pixel 𝐩\mathbf{p}, its corresponding ray direction in this canonical camera’s coordinate system is simply 𝐝 I=𝐊 I−1​𝐩=𝐩\mathbf{d}_{I}=\mathbf{K}_{I}^{-1}\mathbf{p}=\mathbf{p}. The transformation from this canonical ray 𝐝 I\mathbf{d}_{I} to the ray direction 𝐝 cam\mathbf{d}_{\text{cam}} in the target camera’s coordinate system is given by 𝐝 cam=𝐊𝐑𝐝 I\mathbf{d}_{\text{cam}}=\mathbf{K}\mathbf{R}\mathbf{d}_{I}. This establishes a direct homography relationship, 𝐇=𝐊𝐑\mathbf{H}=\mathbf{K}\mathbf{R}, between the two sets of rays. We can then solve for this homography by minimizing the geometric error between the transformed canonical rays and a set of pre-computed target rays, 𝐌(h,w,3:)\mathbf{M}(h,w,3:). This leads to the following optimization problem:

𝐇∗=arg min‖𝐇‖=1∑h=1 H∑w=1 W||𝐇𝐩 h,w×𝐌(h,w,3:)||.\mathbf{H}^{*}=\arg\min_{||\mathbf{H}||=1}\sum_{h=1}^{H}\sum_{w=1}^{W}\left|\left|\mathbf{H}\mathbf{p}_{h,w}\times\mathbf{M}(h,w,3:)\right|\right|.(2)

This is a standard least-squares problem that can be efficiently solved using the Direct Linear Transform (DLT) algorithm [abdel2015direct]. Once the optimal homography 𝐇∗\mathbf{H}^{*} is found, we recover the camera parameters. Since the intrinsic matrix 𝐊\mathbf{K} is upper-triangular and the rotation matrix 𝐑\mathbf{R} is orthonormal, we can uniquely decompose 𝐇∗\mathbf{H}^{*} using RQ decomposition to obtain 𝐊\mathbf{K}, 𝐑\mathbf{R}.

##### Minimal prediction targets.

Recent works aim to build unified models for diverse 3D tasks, often using multitask learning with different targets—for example, point maps alone [dust3r], or redundant combinations of pose, local/global point maps, and depth [wang2025vggt, cut3r, fast3r]. While point maps are insufficient to ensure consistency, redundant targets can improve pose accuracy but often introduce entanglement that compromises it. In contrast, our experiments ([Tab.˜6](https://arxiv.org/html/2511.10647v1#S7.T6 "In 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")) show that a depth-ray representation forms a minimal yet sufficient target set for capturing both scene structure and camera motion, outperforming alternatives like point maps or more complex outputs. However, recovering camera pose from the ray map at inference is computationally costly. We address this by adding a lightweight camera head, 𝒟 C\mathcal{D}_{C}. This transformer operates on camera tokens to predict the field of view (𝐟∈ℝ 2\mathbf{f}\in\mathbb{R}^{2}), rotation as a quaternion (𝐪∈ℝ 4\mathbf{q}\in\mathbb{R}^{4}), and translation (𝐭∈ℝ 3\mathbf{t}\in\mathbb{R}^{3}). Since it processes only one token per view, the added cost is negligible.

### 3.2 Architecture

We now detail the architecture of Depth Anything 3, which is illustrated in [Fig.˜2](https://arxiv.org/html/2511.10647v1#S2.F2 "In Feed-Forward Novel View Synthesis ‣ 2 Related Work ‣ Depth Anything 3: Recovering the Visual Space from Any Views"). The network is composed of three main components: a single transformer model as the backbone, an optional camera encoder for pose conditioning, and a Dual-DPT head for generating predictions.

Single transformer backbone. We use a Vision Transformer with L L blocks, pretrained on large-scale monocular image corpora (e.g., DINOv2 [oquab2023dinov2]). Cross-view reasoning is enabled without architectural changes via an input-adaptive self-attention, implemented by rearranging input tokens. We divide the transformer into two groups of sizes L s L_{\text{s}} and L g L_{\text{g}}. The first L s L_{\text{s}} layers apply self-attention within each image, while the subsequent L g L_{\text{g}} layers alternate between cross-view and within-view attention, operating on all tokens jointly through tensor reordering. In practice, we set L s:L g=2:1 L_{\text{s}}:L_{\text{g}}=2:1 with L=L s+L g L=L_{\text{s}}+L_{\text{g}}. As shown in our ablation study in [Tab.˜7](https://arxiv.org/html/2511.10647v1#S7.T7 "In 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), this configuration provides the optimal trade-off between performance and efficiency compared to other arrangements. This design is input-adaptive: with a single image, the model naturally reduces to monocular depth estimation without extra cost.

Camera condition injection. To seamlessly handle both posed and unposed inputs, we prepend each view with a camera token 𝐜 i\mathbf{c}_{i}. If camera parameters (𝐊 i,𝐑 i,𝐭 i)(\mathbf{K}_{i},\mathbf{R}_{i},\mathbf{t}_{i}) are available, the token is obtained via a lightweight MLP ℰ c\mathcal{E}_{c}: 𝐜 i=ℰ c​(𝐟 i,𝐪 i,𝐭 i)\mathbf{c}_{i}=\mathcal{E}_{c}(\mathbf{f}_{i},\mathbf{q}_{i},\mathbf{t}_{i}). Otherwise, a shared learnable token 𝐜 l\mathbf{c}_{l} is used. Concatenated with patch tokens, these camera tokens participate in all attention operations, providing either explicit geometric context or a consistent learned placeholder.

![Image 4: Refer to caption](https://arxiv.org/html/2511.10647v1/x3.png)

Figure 3: Dual-DPT Head. Two branchs share reassembly modules for better outputs alignment.

Dual-DPT head. For the final prediction stage, we propose a novel Dual-DPT head that jointly produces dense depth and ray values. As shown in [Tab.˜6](https://arxiv.org/html/2511.10647v1#S7.T6 "In 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), this design is both powerful and efficient. Given a set of features from the backbone, the Dual-DPT head first processes them through a shared set of reassembly modules. Subsequently, the processed features are fused using two distinct sets of fusion layers: one for the depth branch and one for the ray branch. Finally, two separate output layers produce the final depth and ray map predictions. This architecture ensures that both branches operate on the same set of processed features, differing only in the final fusion stage. Such a design encourages strong interaction between the two prediction tasks, while avoiding redundant intermediate representations.

### 3.3 Training

Teacher-student learning paradigm. Our training data comes from diverse sources, including real-world depth captures, 3D reconstructions, and synthetic datasets. Real-world depth is often noisy and incomplete ([Fig.˜4](https://arxiv.org/html/2511.10647v1#S4.F4 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views")), limiting its supervisory value. To mitigate this, we train a monocular relative depth estimation “teacher” model solely on synthetic data to generate high-quality pseudo-labels. These pseudo-depth maps are aligned with the original sparse or noisy ground truth via RANSAC least squares, enhancing label detail and completeness while preserving geometric accuracy. We term this model Depth-Anything-3-Teacher, trained on a large synthetic corpus covering indoor, outdoor, object-centric, and diverse in-the-wild scenes to capture fine geometry. We detail our teacher design in the [Sec.˜4.1](https://arxiv.org/html/2511.10647v1#S4.SS1 "4.1 Constructing the Teacher Model ‣ 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views").

##### Training objectives.

Following the formulation in [Sec.˜3.1](https://arxiv.org/html/2511.10647v1#S3.SS1 "3.1 Formulation ‣ 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), our model ℱ θ\mathcal{F}_{\theta} maps an input ℐ\mathcal{I} to a set of outputs comprising a depth map 𝐃^\hat{\mathbf{D}}, a ray map 𝐑^\hat{\mathbf{R}}, and an optional camera pose 𝐜^{\color[rgb]{.5,.5,.5}\definecolor[named]{pgfstrokecolor}{rgb}{.5,.5,.5}\pgfsys@color@gray@stroke{.5}\pgfsys@color@gray@fill{.5}\hat{\mathbf{c}}}: ℱ θ:ℐ↦{𝐃^,𝐑^,𝐜^}\mathcal{F}_{\theta}:\mathcal{I}\mapsto\{\hat{\mathbf{D}},\hat{\mathbf{R}},{\color[rgb]{.5,.5,.5}\definecolor[named]{pgfstrokecolor}{rgb}{.5,.5,.5}\pgfsys@color@gray@stroke{.5}\pgfsys@color@gray@fill{.5}\hat{\mathbf{c}}}\}. The gray color indicates that 𝐜^{\color[rgb]{.5,.5,.5}\definecolor[named]{pgfstrokecolor}{rgb}{.5,.5,.5}\pgfsys@color@gray@stroke{.5}\pgfsys@color@gray@fill{.5}\hat{\mathbf{c}}} is an optional output, included primarily for practical convenience. Prior to loss computation, all ground-truth signals are normalized by a common scale factor. This scale is defined as the mean ℓ 2\ell_{2} norm of the valid reprojected point maps 𝐏\mathbf{P}, a step that ensures consistent magnitude across different modalities and stabilizes the training process. The overall training objective is defined as a weighted sum of several terms:

ℒ=ℒ D​(𝐃^,𝐃)+ℒ M​(𝐑^,𝐌)+ℒ P​(𝐃^⊙𝐝+𝐭,𝐏)+β​ℒ C​(𝐜^,𝐯)+α​ℒ grad​(𝐃^,𝐃),\mathcal{L}=\mathcal{L}_{D}(\hat{\mathbf{D}},\mathbf{D})+\mathcal{L}_{M}(\hat{\mathbf{R}},\mathbf{M})+\mathcal{L}_{P}(\hat{\mathbf{D}}\odot\mathbf{d}+\mathbf{t},\mathbf{P})+{\color[rgb]{.5,.5,.5}\definecolor[named]{pgfstrokecolor}{rgb}{.5,.5,.5}\pgfsys@color@gray@stroke{.5}\pgfsys@color@gray@fill{.5}\beta\mathcal{L}_{C}(\hat{\mathbf{c}},\mathbf{v})}+\alpha\mathcal{L}_{\text{grad}}(\hat{\mathbf{D}},\mathbf{D}),

ℒ D​(𝐃^,𝐃;D c)=1 Z Ω​∑p∈Ω m p​(D c,p​|𝐃^p−𝐃 p|−λ c​log⁡D c,p),\mathcal{L}_{D}(\hat{\mathbf{D}},\mathbf{D}\,;\,D_{c})=\tfrac{1}{Z_{\Omega}}\sum_{p\in\Omega}m_{p}\left(D_{c,p}\,\big|\hat{\mathbf{D}}_{p}-\mathbf{D}_{p}\big|-\lambda_{c}\log D_{c,p}\right),

where D c,p D_{c,p} denotes the confidence of depth D p D_{p}. All loss terms are based on the ℓ 1\ell_{1} norm, with weights set to α=1\alpha=1 and β=1\beta=1. The gradient loss, ℒ grad\mathcal{L}_{\text{grad}}, penalizes the depth gradients:

ℒ grad​(𝐃^,𝐃)=‖∇x 𝐃^−∇x 𝐃‖1+‖∇y 𝐃^−∇y 𝐃‖1,\mathcal{L}_{\text{grad}}(\hat{\mathbf{D}},\mathbf{D})=||\nabla_{x}\hat{\mathbf{D}}-\nabla_{x}\mathbf{D}||_{1}+||\nabla_{y}\hat{\mathbf{D}}-\nabla_{y}\mathbf{D}||_{1},(3)

where ∇x\nabla_{x} and ∇y\nabla_{y} are the horizontal and vertical finite difference operators. This loss preserves sharp edges while ensuring smoothness in planar regions. In practice, we set α=1\alpha=1 and β=1\beta=1.

### 3.4 Implementation Details

##### Traing datasets.

We provide our training datasets in Table [1](https://arxiv.org/html/2511.10647v1#S3.T1 "Tab. 1 ‣ Traing datasets. ‣ 3.4 Implementation Details ‣ 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views"). Note that for datasets with potential overlap between training and testing (ScanNet++), we ensure a strict separation at the scene level, i.e., scenes in training and testing are mutually exclusive. Note that using Scannet++ for training is fair to other methods, as it is widely used for training in [wang2025vggt, dust3r].

Table 1: Datasets used in Depth Anything 3 , including number of scenes, data type.

Usage Dataset#Scenes Data Type
Pose-geometry benchmark HiRoom (ours)29 Synthetic
ETH3D [schops2017eth3d]11 LiDAR
DTU [aanaes2016dtu]22 LiDAR
7Scenes [shotton2013sevenscene]7 LiDAR
ScanNet++ [yeshwanth2023scannet++]20 LiDAR
Pose-geometry Training AriaDigitalTwin [pan2023aria]237 Synthetic
AriaSyntheticENV [pan2023aria]99950 Synthetic
ArkitScenes [baruch2021arkitscenes]4388 LiDAR
BlendedMVS [yao2020blendedmvs]503 3D Recon
Co3dv2 [reizenstein2021common]30616 Colmap
DL3DV [ling2024dl3dv]6379 Colmap
HyperSim [roberts2021hypersim]344 Synthetic
MapFree [arnold2022map]921 Colmap
MegaDepth [li2018megadepth]268 Colmap
MegaSynth [jiang2025megasynth]6049 Synthetic
MvsSynth [DeepMVS]121 Synthetic
Objaverse [deitke2023objaverse]505557 Synthetic
Omniobject [wu2023omniobject3d]5885 Synthetic
OmniWorld [zhou2025omniworld]1039 Synthetic
PointOdyssey [zheng2023pointodyssey]44 Synthetic
ReplicaVMAP [straub2019replica]17 Synthetic
ScanNet++ [yeshwanth2023scannet++]230 LiDAR
ScenenetRGBD [mccormac2017scenenet]16866 Synthetic
TartanAir [tartanair2020iros]355 Synthetic
Trellis [xiang2024structured]557408 Synthetic
vKitti2 [cabon2020vkitti2]50 Synthetic
WildRGBD [xia2024rgbd]23050 LiDAR

##### Training details.

We train our model on 128 H100 GPUs for 200k steps, using an 8k-step warm-up and a peak learning rate of 2×10−4 2\times 10^{-4}. The base resolution is 504×504 504\times 504, which is divisible by 2, 3, 4, 6, 9 and 14, making it more compatible with common photo aspect ratios such as 2:3, 3:4, and 9:16. Training image resolutions are randomly sampled from 504×504 504\times 504, 504×378 504\times 378, 504×336 504\times 336, 504×280 504\times 280, 336×504 336\times 504, 896×504 896\times 504, 756×504 756\times 504, 672×504 672\times 504. For the 504×504 504\times 504 resolution, the number of views is sampled uniformly from [2, 18]. The batch size is dynamically adjusted to keep the token count per step approximately constant. Supervision transitions from ground-truth depth to teacher-model labels at 120k steps. Pose conditioning is randomly activated during training with probability 0.2.

4 Teacher-Student Learning
--------------------------

![Image 5: Refer to caption](https://arxiv.org/html/2511.10647v1/x4.png)

Figure 4: Poor quality real-world datasets. We show some examples of the poor quality real-world datasets. 

As shown in [Fig.˜4](https://arxiv.org/html/2511.10647v1#S4.F4 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), the real-world datasets are of poor quality, thus we train the teacher model exclusively on synthetic data to provide supervision for real-world data. Our teacher model is trained as a monocular relative depth predictor. During inference or supervision, noisy ground-truth depth can be used to provide scale and shift parameters, allowing for the alignment of the predicted relative depth with absolute depth measurements.

### 4.1 Constructing the Teacher Model

Building upon Depth Anything 2 [yang2024depth], we extend the approach in several key aspects, including both data and representation. We observe that expanding the training corpus yields clear improvements in depth estimation performance, substantiating the benefits of data scaling. Furthermore, while our revised depth representation may not show striking improvements on standard 2D evaluation metrics, it leads to qualitatively better 3D point clouds, exhibiting fewer geometric distortions and more realistic scene structures. It is important to note that our teacher network backbone is directly aligned with the above DA3 framework, consisting solely of a DINOv2 vision transformer with a DPT decoder—no specialized architectural modifications are introduced. We elaborate on the full design and implementation details in the following sections.

Data scaling. We train the teacher model exclusively on synthetic data to achieve finer geometric detail. The synthetic datasets used in DA2 are relatively limited. In DA3, we substantially expand the training corpus to include: Hypersim [roberts2021hypersim], TartanAir [tartanair2020iros], IRS [wang2019irs], vKITTI2 [cabon2020vkitti2], BlendedMVS [yao2020blendedmvs], SPRING [mehl2023spring], MVSSynth [DeepMVS], UnrealStereo4K [zhang2018unrealstereo], GTA-SfM [wang2020flow], TauAgent [gil2021online], KenBurns [niklaus20193d], MatrixCity [li2023matrixcity], EDEN [le2021eden], ReplicaGSO [replica19arxiv], UrbanSyn [GOMEZ2025130038], PointOdyssey [zheng2023pointodyssey], Structured3D [zheng2020structured3d], Objaverse [deitke2023objaverse], Trellis [xiang2024structured], and OmniObject [wu2023omniobject3d]. This collection spans indoor, outdoor, object-centric, and diverse in-the-wild scenes, improving generalization of the teacher model.

Depth representation. Unlike DA2, which predicts scale–shift-invariant disparity, our teacher outputs scale–shift-invariant depth. Depth is preferable for downstream tasks, such as metric depth estimation and multiview geometry, that directly operate in depth space rather than disparity. To address depth’s reduced sensitivity for near-camera regions comparing to disparity, we predict exponential depth instead of linear depth, enhancing discrimination at small distances.

Training objectives. For geometric supervision, in addition to a standard depth-gradient loss, we adopt ROE alignment with the global–local loss introduced in [wang2025moge]. To further refine local geometry, we introduce a distance-weighted surface-normal loss. For each center pixel, we sample four neighboring points and compute unnormalized normals n i n_{i}. We then weight these normals by:

w i=∑j=0 4‖n j‖−‖n i‖,w_{i}=\sum_{j=0}^{4}\parallel n_{j}\parallel-\parallel n_{i}\parallel,(4)

which downweights contributions from neighbors farther from the center, yielding a mean normal closer to the true local surface normal:

n m=∑i=0 4 w i​n i‖n i‖,n_{m}=\sum_{i=0}^{4}w_{i}\frac{n_{i}}{\parallel n_{i}\parallel},(5)

The final normal loss is

ℒ N=ℰ​(n^m,n m)+∑i=0 4 ℰ​(n^i,n i)\mathcal{L}_{N}=\mathcal{E}(\hat{n}_{m},n_{m})+\sum_{i=0}^{4}\mathcal{E}(\hat{n}_{i},n_{i})(6)

where ℰ\mathcal{E} denotes the angular error between normals. Ground truth is undefined in sky regions and in background areas of object-only datasets. To prevent these regions from degrading the depth prediction and to facilitate downstream use, we jointly predict a sky mask and an object mask aligned with the depth output, supervised with MSE loss. The overall training objective is

ℒ T=α​ℒ grad+ℒ gl+ℒ N+ℒ sky+ℒ obj\mathcal{L}_{T}=\alpha\mathcal{L}_{\text{grad}}+\mathcal{L}_{\text{gl}}+\mathcal{L}_{N}+\mathcal{L}_{\text{sky}}+\mathcal{L}_{\text{obj}}(7)

where α=0.5\alpha=0.5. Here, ℒ grad\mathcal{L}_{\text{grad}}, ℒ gl\mathcal{L}_{\text{gl}}, ℒ sky\mathcal{L}_{\text{sky}}, and ℒ obj\mathcal{L}_{\text{obj}} denote the gradient loss, global–local loss, sky-mask loss, and object-mask loss, respectively.

### 4.2 Teaching Depth Anything 3

Real-world datasets are crucial for generalizing camera pose estimation, yet they rarely provide clean depths; supervision is often noisy or sparse ([Fig.˜4](https://arxiv.org/html/2511.10647v1#S4.F4 "In 4 Teacher-Student Learning ‣ Depth Anything 3: Recovering the Visual Space from Any Views")). Depth Anything 3 Teacher provides high-quality relative depth, which we align to noisy metric measurements (e.g., COLMAP or active sensors) via a robust ransac scale–shift procedure. Let 𝐃~\tilde{\mathbf{D}} denote the teacher’s relative depth and 𝐃\mathbf{D} the available sparse depth with validity mask m p m_{p} over domain Ω\Omega. We estimate scale s s and shift t t by RANSAC least squares, using an inlier threshold equal to the mean absolute deviation from the residual median:

(s^,t^)=arg⁡min s>0,t​∑p∈Ω m p​(s​𝐃~p+t−𝐃 p)2,𝐃 T→M=s^​𝐃~+t^.(\hat{s},\hat{t})=\arg\min_{s>0,\,t}\sum_{p\in\Omega}m_{p}\,\big(s\,\tilde{\mathbf{D}}_{p}+t-\mathbf{D}_{p}\big)^{2},\quad\mathbf{D}^{T\rightarrow M}=\hat{s}\,\tilde{\mathbf{D}}+\hat{t}.(8)

The aligned 𝐃 T→M\mathbf{D}^{T\rightarrow M} provides scale-consistent and pose–depth coherent supervision for Depth Anything 3, complementing our joint depth–ray objectives and improving real-world generalization, as evidenced in [Fig.˜8](https://arxiv.org/html/2511.10647v1#S7.F8 "In Running time. ‣ 7.2.3 Ablation and Analysis ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views").

### 4.3 Teaching Monocular Model

We additionally train a monocular depth model under a teacher–student paradigm. We follow the DA2 framework, training the monocular student on unlabeled images with teacher-generated pseudo-labels. The key difference from DA2 lies in the prediction target: our student predicts depth maps, whereas DA2 predicts disparity. We further supervise the student with the same loss used for the teacher, applied to the pseudo-depth labels. The monocular model also predicts relative depth. Trained solely on unlabeled data with teacher supervision, it achieves state-of-the-art performance on standard monocular depth benchmarks as shown in [Tab.˜10](https://arxiv.org/html/2511.10647v1#S7.T10 "In 7.3.2 Student Model ‣ 7.3 Analysis for Depth-Anything-3-Monocular ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views").

### 4.4 Teaching Metric Model

Next, we demonstrate that our teacher model can be used for training a metric depth estimation model with sharp boundaries. Following Metric3Dv2 [hu2024metric3dv2], we apply canonical camera space transformation to address depth ambiguity caused by varying focal lengths. Specifically, we rescale the ground-truth depth using ratio f c/f f^{c}/f, where f c f^{c} and f f denote the canonical focal length and camera focal length, respectively. To ensure sharp details, we employ Teacher model’s prediction as training labels. We align the scale and shift of the teacher model’s predicted depths with the ground-truth metric depth labels for supervision.

##### Training dataset.

We trained our metric depth model on 14 datasets, including Taskonomy [zamir2018taskonomy], DIML (Outdoor) [cho2021diml], DDAD [ddad], Argoverse [wilson2023argoverse], Lyft [], PandaSet [xiao2021pandaset], Waymo [Sun_2020_CVPR], ScanNet++ [yeshwanth2023scannet++], ARKitScenes [baruch2021arkitscenes], Map-free [arnold2022map], DSEC [Gehrig21ral], Driving Stereo [yang2019drivingstereo] and Cityscapes [cordts2016cityscapes] datasets. For stereo datasets, we leverage the prediction of FoundationStereo [wen2025foundationstereo] as training labels.

##### Implementation Details.

The training largely follows that of the monocular teacher model. All images are trained at a base resolution of 504 with varying aspect ratios (1:1, 1:2, 16:9, 9:16, 3:4, 1:1.5, 1.5:1, 1:1.8). We employ AdamW optimizer and set the learning rate for encoder and decoder to 5e-6 and 5e-5, respectively. We apply random rotation augmentation where training images are rotated at 90 or 270 degree with 5% probability. We set canonical focal length f c f^{c} to 300. We use the aligned prediction from teacher model as supervision. With a probability of 20%, we use the original ground-truth labels for training. We train with batch size of 64 for 160K iterations. The training objective is a weighted sum of depth loss ℒ d​e​p​t​h\mathcal{L}_{depth}, ℒ g​r​a​d\mathcal{L}_{grad} and sky-mask loss ℒ s​k​y\mathcal{L}_{sky}.

5 Application: Feed-Forward 3D Gaussian Splattings
--------------------------------------------------

### 5.1 Pose-Conditioned Feed-Forward 3DGS

Inspired by human spatial intelligence, we believe that consistent depth estimation can greatly enhance downstream 3D vision tasks. We choose feed-forward novel view synthesis (FF-NVS) as the demonstration task, given its growing attention driven by advances in neural 3D representations (i.e., we choose 3DGS) and its relevance to numerous applications. Adhere to the minimal modeling strategy, we perform FF-NVS by fine-tuning with an added DPT head (GS-DPT) to infer pixel-aligned 3D Gaussians [charatan2024pixelsplat, chen2024mvsplat].

GS-DPT head. Given visual tokens for each view extracted via our single transformer backbone ([Sec.˜3.2](https://arxiv.org/html/2511.10647v1#S3.SS2 "3.2 Architecture ‣ 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")), GS-DPT predicts the camera-space 3D Gaussian parameters {σ i,𝐪 i,𝐬 i,𝐜 i}i=1 H×W\{\sigma_{i},\mathbf{q}_{i},\mathbf{s}_{i},\mathbf{c}_{i}\}_{i=1}^{H\times W}, where σ i\sigma_{i}, 𝐪 i∈ℍ\mathbf{q}_{i}\in\mathbb{H}, 𝐬 i∈ℝ 3\mathbf{s}_{i}\in\mathbb{R}^{3}, 𝐜 i∈ℝ 3\mathbf{c}_{i}\in\mathbb{R}^{3} denote the opacity, rotation quaternion, scale, and RGB color of the i i-th 3D Gaussian, respectively. Among them, σ i\sigma_{i} is predicted by the confidence head, while others are predicted by the main GS-DPT head. The estimated depth is unprojected to world coordinates to obtain the global positions 𝐏 i∈ℝ 3{\mathbf{P}}_{i}\in\mathbb{R}^{3} of the 3D Gaussians. These primitives are then rasterized to synthesize novel views from given camera poses.

Training objectives. The NVS model is fine-tuned with two training objectives, namely photometric loss (i.e., ℒ MSE\mathcal{L}_{\mathrm{MSE}} and ℒ LPIPS\mathcal{L}_{\mathrm{LPIPS}}) on rendered novel views and scale-shift-invariant depth loss ℒ D\mathcal{L}_{D} on the estimated depth of observed views, following the teacher–student learning paradigm ([Sec.˜3.3](https://arxiv.org/html/2511.10647v1#S3.SS3 "3.3 Training ‣ 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")).

### 5.2 Pose-Adaptive Feed-Forward 3DGS

Unlike the above pose-conditioned version intended to benchmark DA3 as a strong feed-forward 3DGS backbone, we also present an alternative better suited to in-the-wild evaluation. This version is designed to integrate seamlessly with DA3 using identical pretrained weights, enabling novel view synthesis with or without camera poses, and across varying resolutions and input view counts.

Pose-adaptive formulation. Rather than assuming that all input images are uncalibrated [smart2024splatt3r, ye2024no, flare, jiang2025anysplat], we adopt a pose-adaptive design that accepts both posed and unposed inputs, yielding a flexible framework that works with or without poses. Two design choices are required to achieve this: 1) all 3DGS parameters are predicted in local camera space. 2) the backbone must handle posed and unposed images seamlessly. Our DA3 backbone satisfies both requirements ([Sec.˜3.2](https://arxiv.org/html/2511.10647v1#S3.SS2 "3.2 Architecture ‣ 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")). In particular, when poses are available, we scale (via [umeyama2002least]) and unproject the predicted depth and camera-space 3DGS to world space to align with them. When poses are not available, we directly use the predicted poses for the unprojection to world space.

To reduce the trade-off between accurate surface geometry and rendering quality [guedon2024sugar], we predict an additional depth offset in the GS-DPT head. For more in-the-wild robustness, we replace per 3D Gaussian color with spherical harmonic coefficients to reduce conflicts with geometry via modeling view-dependent surface.

Enhanced training strategies. To avoid unstable training, we initialize the DA3 backbone from pretrained weights and freeze it when training, tuning only the GS-DPT head. To improve in-the-wild performance, we train with varying image resolutions and varying numbers of context views. Specifically, higher-resolution inputs are paired with fewer context views and lower-resolution inputs with more views, which stabilizes training while supporting diverse evaluation scenarios.

### 5.3 Implementation Details

##### Training datasets.

For training the NVS model, we leverage the large-scale DL3DV dataset [ling2024dl3dv], which provides diverse real-world scenes with camera poses estimated by COLMAP. We use 10,015 scenes from DL3DV for training the feed-forward 3DGS model. To ensure fair evaluation, we strictly maintain exclusivity between training and testing splits: the 140 DL3DV scenes used for benchmarking are completely disjoint from the training set, preventing any data leakage.

6 Visual Geometry Benchmark
---------------------------

We further introduce a visual geometry benchmark to assess geometry prediction models. It directly evaluates pose accuracy, depth via reconstruction accuracy and visual rendering quality.

### 6.1 Benchmark Pipeline

##### Pose estimation.

For each scene, we select all available images; if the total number exceeds the limit, we randomly sample 100 images using a fixed random seed. The selected images are then processed through a feed-forward model to generate consistent pose and depth estimations, after which the pose accuracy is computed.

##### Geometry estimation.

For the same image set, we perform reconstruction using the predicted poses together with the predicted depths. To align the reconstructed point cloud with the ground-truth, we employ evo [umeyama2002least] to align the predicted poses to the ground-truth poses, obtaining a transformation that maps the reconstruction into the ground-truth coordinate system. To improve robustness, we adopt a RANSAC-based alignment procedure. Specifically, we repeatedly apply evo on randomly sampled pose subsets and evaluate each candidate transformation by counting the number of inlier poses, where inliers are defined as those with translation errors below the median of the overall pose deviations. The transformation with the largest inlier set is then chosen and applied to fuse the aligned predicted point cloud with the predicted depth maps by TSDF fusion. Finally, reconstruction quality is assessed by comparing the aligned reconstruction with the ground-truth point cloud using the metrics described in Sec. [6.2](https://arxiv.org/html/2511.10647v1#S6.SS2.SSS0.Px2 "Reconstrution metrics. ‣ 6.2 Metrics ‣ 6 Visual Geometry Benchmark ‣ Depth Anything 3: Recovering the Visual Space from Any Views").

##### Visual rendering.

For each testing scene, the number of images typically ranges from 300 to 400 across all benchmark datasets. We sample one out of every 8 images as target novel views for evaluation. From the remaining viewpoints, we use COLMAP camera poses provided by each dataset and apply farthest point sampling, considering both camera translation and rotation distances, to select 12 images as input context views. For DL3DV, we use the official Benchmark set for testing. For Tanks and Temples, all Training Data scenes are included except Courthouse. For MegaDepth, we select scenes numbered from 5000 to 5018, as these are most suitable for NVS.

### 6.2 Metrics

##### Pose metrics.

For assessing pose estimation, we follow the evaluation protocol introduced in [wang2025vggt, wang2023posediffusion] and report results using the AUC. This metric is derived from two components: Relative Rotation Accuracy (RRA) and Relative Translation Accuracy (RTA). RRA and RTA quantify the angular deviation in rotation and translation, respectively, between two images. Each error is compared against a set of thresholds to obtain accuracy values. AUC is then computed as the integral of the accuracy–threshold curve, where the curve is determined by the smaller of RRA and RTA at each threshold. To illustrate performance under different tolerance levels, we primarily report results at thresholds of 3 and 30.

##### Reconstrution metrics.

Let 𝒢\mathcal{G} denote the ground-truth point set and ℛ\mathcal{R} the reconstructed point set under evaluation. We measure accuracy using dist​(ℛ→𝒢)\text{dist}(\mathcal{R}\rightarrow\mathcal{G}) and completeness using dist​(𝒢→ℛ)\text{dist}(\mathcal{G}\rightarrow\mathcal{R}) following [aanaes2016dtu]. The Chamfer Distance (CD) is then defined as the average of these two terms. Based on these distances, we define the precision and recall of the reconstruction ℛ\mathcal{R} with respect to a distance threshold d d. Precision is given by 1|ℛ|​∑[dist​(ℛ i→𝒢)<d]\frac{1}{|\mathcal{R}|}\sum\big[\text{dist}(\mathcal{R}_{i}\rightarrow\mathcal{G})<d\big], and recall by 1|𝒢|​∑[dist​(𝒢 i→ℛ)<d]\frac{1}{|\mathcal{G}|}\sum\big[\text{dist}(\mathcal{G}_{i}\rightarrow\mathcal{R})<d\big], where [⋅]\left[\cdot\right] denotes the Iverson bracket [knapitsch2017tnt]. To jointly capture both measures, we report the F1-score, computed as F1=2×precision×recall precision+recall\text{F1}=\frac{2\times\text{precision}\times\text{recall}}{\text{precision}+\text{recall}}.

### 6.3 Datasets

Our benchmark is built on five datasets: HiRoom [SVLightVerse2025], ETH3D [schops2017eth3d], DTU [aanaes2016dtu], 7Scenes [shotton2013sevenscene], and ScanNet++ [yeshwanth2023scannet++]. Together, they cover diverse scenarios ranging from object-centric captures to complex indoor and outdoor environments, and are widely adopted in prior research. Below, we present more details about the dataset preparation process.

HiRoom is a Blender-rendered synthetic dataset comprising 30 indoor living scenes created by professional artists. We use a threshold d d of 0.05m for the F1 reconstruction metric calculation. For TSDF fusion, we set the parameters voxel size to 0.007m.

ETH3D provides high-resolution indoor and outdoor images with ground-truth depth from laser sensors. We aggregate the ground-truth depth maps with TSDF fusion for GT 3D shapes. We select 11 scenes: courtyard, electro, kicker, pipes, relief, delivery area, facade, office, playground, relief 2, terrains, for the benchmark. All frames are used in the evaluation. We use a threshold d d of 0.25 for the F1 reconstruction metric calculation. For TSDF fusion, we set the parameters voxel size to 0.039m.

DTU is an indoor dataset consisting of 124 different objects, each scene is recorded from 49 views. It provides ground-truth point clouds collected under well-controlled conditions. We evaluate models on the 22 evaluation scans of the DTU dataset following [yao2018mvsnet]. We adopt the RMBG 2.0 [BiRefNet] to remove meaningless background pixels and use the default depth fusion strategy proposed in [zhang2023geomvsnet]. All frames are used in the evaluation.

7Scenes is a challenging real-world dataset, consisting of low-resolution images with severe motion blurs for in-door scenes. We follow the implementation in [zhu2024nicerslam] to fuse RGBD images with TSDF fusion and prepare ground-truth 3D shapes. We downsample the number of frames for each scene by 11 to faciliate evaluation. We use a threshold d d of 0.05m for the F1 reconstruction metric calculation. For TSDF fusion, we set the parameters voxel size to 0.007m.

ScanNet++ is an extensive indoor dataset providing high-resolution images, depth maps from iPhone LiDAR, and high-resolution depth maps sampled from reconstructions of laser scans. We select 20 scenes for the benchmark. As depth maps from iPhone LiDAR lack of invalid ground-truth indicators, we use depth maps sampled from reconstructions of laser scans as ground-truth depth by default. We aggregate the ground-truth depth maps with TSDF fusion for GT 3D shapes. We downsample the number of frames for each scene by 5 to faciliate evaluation. We use a threshold d d of 0.05m for the F1 reconstruction metric calculation. For TSDF fusion, we set the parameters voxel size to 0.02m.

##### Visual rendering quality.

We evaluate visual rendering quality on diverse large-scale scenes. We introduce a new NVS benchmark built from three datasets, including DL3DV [ling2024dl3dv] with 140 scenes, Tanks and Temples [knapitsch2017tanks] with 6, and MegaDepth [li2018megadepth] with 19, each spanning around 300 sampled frames. Ground truth camera poses, estimated with COLMAP, are used directly to ensure accurate and fair comparison across diverse models. We report PSNR, SSIM, and LPIPS metrics on rendered novel views using given camera poses.

7 Experiments
-------------

Table 2: Comparisons with SOTA methods on pose accuracy. We report both Auc3 ↑\uparrow and Auc30 ↑\uparrow metrics. The top-3 results are highlighted as first, second, and third. 

Methods Params HiRoom ETH3D DTU 7Scenes ScanNet++
Auc3 Auc30 Auc3 Auc30 Auc3 Auc30 Auc3 Auc30 Auc3 Auc30
DUSt3R 0.57B 17.6 54.3 4.30 27.3 4.00 74.3 6.90 61.6 8.10 33.9
Fast3R 0.65B 25.9 77.0 8.10 44.4 9.50 79.1 19.0 78.6 17.9 72.5
MapAnything 0.56B 17.9 82.8 19.2 77.4 6.50 72.7 12.6 79.7 20.2 84.1
Pi3 0.96B 67.0 94.8 35.2 87.3 62.5 94.9 25.5 86.3 50.7 92.1
VGGT 1.19B 49.1 88.0 26.3 80.8 79.2 99.8 23.9 85.0 62.6 95.1
DA3-Giant 1.10B 80.3 95.9 48.4 91.2 94.1 99.4 28.5 86.8 85.0 98.1
DA3-Large 0.36B 58.7 94.2 32.2 86.9 70.2 96.7 29.2 86.6 60.2 94.7
DA3-Base 0.11B 19.0 83.2 15.1 74.6 60.1 95.9 20.1 82.9 25.1 83.4
DA3-Small 0.03B 9.49 75.2 8.59 62.1 30.6 91.2 14.0 78.7 10.9 71.9

![Image 6: Refer to caption](https://arxiv.org/html/2511.10647v1/figs/pngs/vis_traj.png)

Figure 5: Comparisons of pose estimation quality. Camera trajectories for two videos are shown. Ground-truth trajectories are derived using COLMAP on images with dynamic objects masked. 

### 7.1 Comparison with State of the Art

##### Baselines.

VGGT [wang2025vggt] is an end-to-end transformer that jointly predicts camera parameters, depth, and 3D points from one or many views. Pi3 [wang2025pi3] further adopts a permutation-equivariant design to recover affine-invariant cameras and scale-invariant point maps from unordered images. MapAnything [keetha2025mapanything] provides a feed-forward framework that can also take camera pose as input for dense geometric prediction. Fast3R [yang2025fast3r] extends point-map regression to hundreds or even thousands of images in a single forward pass. Finally, DUSt3R [wang2024dust3r] tackles uncalibrated image pairs by regressing point maps and aligning them globally. Our method is similar to VGGT [wang2025vggt], but adopts a new architecture and a different camera representation, and it is orthogonal to Pi3 [wang2025pi3].

##### Pose estimation.

As shown in [Tab.˜2](https://arxiv.org/html/2511.10647v1#S7.T2 "In 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views") and [Fig.˜5](https://arxiv.org/html/2511.10647v1#S7.F5 "In 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), comparing against five baselines [dust3r, wang2025vggt, fast3r, wang2025pi3, keetha2025mapanything], our DA3-Giant model attains the best performance on nearly all metrics, with the only exception being Auc30 on the DTU dataset. Notably, on Auc3 our model delivers at least an 8%8\% relative improvement over all competing methods, and on ScanNet++ it achieves a 33%33\% relative gain over the second-best model.

Table 3: Comparisons with SOTA methods on reconstruction accuracy. For all datasets except DTU, we report the F-Score (F1↑\uparrow). For DTU, we report the chamfer distance (CD↓\downarrow, unit: mm). w/o p. and w/ p. denote without pose and with pose, indicating whether ground-truth camera poses are provided for reconstruction. The top-3 results are highlighted as first, second, and third. 

Methods Params HiRoom ETH3D DTU 7Scenes ScanNet++
w/o p.w/ p.w/o p.w/ p.w/o p.w/ p.w/o p.w/ p.w/o p.w/ p.
DUSt3R 0.57B 30.1 39.5 19.7 18.8 7.60 7.97 26.6 39.8 18.9 27.3
Fast3R 0.65B 40.7 48.2 38.5 50.3 6.88 8.20 41.0 49.8 37.1 53.7
MapAnything 0.56B 32.4 69.2 54.8 71.9 7.91 3.97 44.8 55.2 39.4 71.3
Pi3 0.96B 75.8 85.0 72.7 80.6 3.28 1.72 44.2 57.5 63.1 73.3
VGGT 1.19B 56.7 70.2 57.2 66.7 2.05 1.44 47.9 51.4 66.4 70.7
DA3-Giant 1.10B 85.1 95.6 79.0 87.1 1.85 1.85 53.5 56.5 77.0 79.3
DA3-Large 0.36B 69.5 87.1 65.8 75.2 2.08 1.23 56.3 49.2 67.9 75.7
DA3-Base 0.11B 25.9 71.4 49.5 66.7 2.87 2.36 49.9 50.6 47.2 67.8
DA3-Small 0.03B 18.3 52.2 41.6 63.4 5.83 2.49 41.0 46.8 32.3 53.8

![Image 7: Refer to caption](https://arxiv.org/html/2511.10647v1/x5.png)

Figure 6: Comparisons of point cloud quality. Our model produces point clouds that are more geometrically regular and substantially less noisy than those generated by other methods. 

##### Geometry estimation.

As shown in [Tab.˜3](https://arxiv.org/html/2511.10647v1#S7.T3 "In Pose estimation. ‣ 7.1 Comparison with State of the Art ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), our DA3-Gaint establishes a new SOTA in nearly all scenarios, outperforming all competitors in all five pose-free settings. On average, DA3-Gaint achieves a relative improvement of 25.1% over VGGT and 21.5% over Pi3. [Fig.˜7](https://arxiv.org/html/2511.10647v1#S7.F7 "In Geometry estimation. ‣ 7.1 Comparison with State of the Art ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views") and [Fig.˜6](https://arxiv.org/html/2511.10647v1#S7.F6 "In Pose estimation. ‣ 7.1 Comparison with State of the Art ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views") visualize our predicted depth and recovered point clouds. The results are not only clean, accurate, and complete, but also preserve fine-grained geometric details, clearly demonstrating a superiority over other methods. Even more notably, our much smaller DA3-Large (0.30B parameters) demonstrates remarkable efficiency. Despite being 3×\times smaller, it surpasses the prior SOTA VGGT (1.19B parameters) in five out of the ten settings, with particularly strong performance on the ETH3D.

When camera poses are available, both our method and MapAnything can exploit them for improved results, and other methods also benefit from ground-truth pose fusion. Our model shows clear gains on most datasets except 7Scenes, where the limited video setting already saturates performance and reduces the benefit of pose conditioning. Notably, with pose conditioning, performance gains from scaling model size are smaller than in pose-free models, indicating that pose estimation scales more strongly than depth estimation and requires larger models to fully realize improvements.

Monocular depth accuracy also reflects geometry quality. As shown in [Tab.˜4](https://arxiv.org/html/2511.10647v1#S7.T4 "In Geometry estimation. ‣ 7.1 Comparison with State of the Art ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), on the standard monocular depth benchmarks reported in [yang2024depthv2], our model outperforms VGGT and Depth Anything 2. For reference, we also include the results of our teacher model.

Table 4: Monocular depth comparisons.δ 1↑\delta_{1}\uparrow

Method KITTI NYU SINTEL ETH3D DIODE Rank
DA2 94.6 97.9 77.2 86.5 95.2 2.60
VGGT 91.7 97.9 67.9 97.5 95.3 3.75
DA3 95.3 97.4 75.5 98.6 95.4 2.20
Teacher 97.2 97.9 81.4 99.8 96.6 1.00
![Image 8: Refer to caption](https://arxiv.org/html/2511.10647v1/figs/pngs/vis_depth.png)

Figure 7: Comparisons of depth quality. Compared with other methods, our depth maps exhibit finer structural detail and higher semantic correctness across diverse scenes. 

##### Visual rendering.

To fairly evaluate feed-forward novel view synthesis (FF-NVS), we compare against three recent 3DGS models—pixelSplat [charatan2024pixelsplat], MVSplat [chen2024mvsplat], and DepthSplat [xu2025depthsplat]—and further test alternative frameworks by replacing our geometry backbone with Fast3R [yang2025fast3r], MV-DUSt3R [Mv-dust3r+], and VGGT [wang2025vggt]. All models are trained on DL3DV-10K training set under a unified protocol and evaluated on our benchmark ([Sec.˜6.3](https://arxiv.org/html/2511.10647v1#S6.SS3.SSS0.Px1 "Visual rendering quality. ‣ 6.3 Datasets ‣ 6 Visual Geometry Benchmark ‣ Depth Anything 3: Recovering the Visual Space from Any Views")).

As reported in [Tab.˜5](https://arxiv.org/html/2511.10647v1#S7.T5 "In 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), all models perform substantially better on DL3DV than on the other datasets, suggesting that 3DGS-based NVS is sensitive to trajectory and pose distributions standardized by DL3DV, rather than scene content. Comparing the two groups, geometry-model-based frameworks consistently outperform specialized feed-forward models, demonstrating that a simple backbone plus DPT head can surpass complex task-specific designs. The advantage stems from large-scale pretraining, which enables better generalization and scalability than approaches relying on epipolar transformers, cost volumes, or cascaded modules. Within this group, NVS performance correlates with geometry estimation capability, making DA3 the strongest backbone. Looking forward, we expect FF-NVS can be effectively addressed with simple architectures leveraging pretrained geometry backbones, and that the strong spatial understanding of DA3 will benefit other 3D vision tasks.

### 7.2 Analysis for Depth Anything 3

Training our DA3-Giant model requires 128×\times H100 GPUs for approximately 10 days. To reduce carbon footprint and computational cost, all ablation experiments reported in this section are conducted using the ViT-L backbone with a maximum of 10 views, requiring approximately 4 days on 32×\times H100 GPUs.

Table 5: Comparisons with SOTA methods on NVS task. We report NVS comparsions with exisiting feed-forward 3DGS models and counterparts using other backbones. For each scene, we use 12 input context views and test on target views sampled every 8 views over a set of over 300 views. Image resolution is 270×480 270\times 480. 

Methods In-domain Dataset Out-of-domain Datasets
DL3DV-Benchmarks (140)Tanks and Temples (6)MegaDepth (19)
PSNR↑\uparrow SSIM↑\uparrow LPIPS↓\downarrow PSNR↑\uparrow SSIM↑\uparrow LPIPS↓\downarrow PSNR↑\uparrow SSIM↑\uparrow LPIPS↓\downarrow
pixelSplat 16.55 0.456 0.480 13.81 0.347 0.558 13.87 0.367 0.561
MVSplat 18.13 0.559 0.393 14.81 0.391 0.508 14.67 0.398 0.533
DepthSplat 19.24 0.620 0.322 15.80 0.474 0.418 15.90 0.471 0.450
Fast3R 19.30 0.604 0.320 16.24 0.478 0.409 16.43 0.493 0.421
MV-DUSt3R 20.01 0.645 0.294 17.04 0.529 0.370 16.20 0.484 0.437
VGGT 20.96 0.697 0.253 17.18 0.550 0.347 16.45 0.500 0.417
DAv3 (Ours)21.33 0.711 0.241 18.10 0.578 0.311 17.89 0.561 0.351

#### 7.2.1 Sufficiency of the Depth-Ray Representation

To validate our depth-ray representation, we compare different prediction combinations summarized in [Tab.˜6](https://arxiv.org/html/2511.10647v1#S7.T6 "In 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"). All models use a ViT-L backbone, identical training settings (view size: 10, batch size: 128, steps: 120k). We evaluate four heads: 1) 0pt for dense depth maps; 2) pcd for direct 3D point clouds; 3) cam for 9-DoF camera pose 𝐜=(𝐭,𝐪,𝐟)\mathbf{c}=(\mathbf{t},\mathbf{q},\mathbf{f}); and 4) our proposed ray, predicting per-pixel ray maps ([Sec.˜3.1](https://arxiv.org/html/2511.10647v1#S3.SS1 "3.1 Formulation ‣ 3 Depth Anything 3 ‣ Depth Anything 3: Recovering the Visual Space from Any Views")). The ray head uses a Dual-DPT architecture, while pcd uses a separate DPT head. For models without pcd, point clouds are obtained by combining 0ptwith camera parameters from ray or cam. As shown in Table [6](https://arxiv.org/html/2511.10647v1#S7.T6 "Tab. 6 ‣ 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), the minimal 0pt+ ray configuration consistently outperforms 0pt+ pcd + cam and 0pt+ cam across all datasets and metrics, achieving nearly 100% relative gain in Auc3 over 0pt+ cam. Adding an auxiliary cam head (0pt+ ray + cam) yields no further benefit, confirming the sufficiency of the depth-ray representation. We adopt 0pt+ ray + cam as our final representation, as the camera head incurs negligible computational overhead, amounting to approximately 0.1% of the computation cost of the main backbone.

Table 6: Ablations of prediction-target combinations. Note that all experiments in this table do not have camera condition token. The best and second best are highlighted. 

Methods HiRoom ETH3D DTU 7Scenes ScanNet++
Auc3↑\uparrow F1↑\uparrow Auc3↑\uparrow F1↑\uparrow Auc3↑\uparrow CD↓\downarrow Auc3↑\uparrow F1↑\uparrow Auc3↑\uparrow F1↑\uparrow
depth + pcd + cam 9.1 12.8 19.0 60.4 42.3 4.918 20.8 43.4 22.0 43.0
depth + cam 10.8 16.5 9.9 48.0 23.3 5.316 13.0 38.5 13.3 41.0
depth + ray 48.7 60.3 25.5 65.4 46.5 3.919 24.0 46.5 35.5 53.4
0pt+ ray + cam 37.2 45.4 22.3 59.4 56.3 3.066 25.7 45.6 34.1 56.5

Table 7: Ablation study. We evaluate three architectural designs with comparable model sizes (a-c), the effects of the dual-DPT head (d), teacher label supervision (e), and the pose conditioning module (f-g). The best and second best are highlighted. Methods marked with "*" are evaluated with ground-truth pose fusion. 

Methods HiRoom ETH3D DTU 7Scenes ScanNet++
Auc3↑\uparrow F1↑\uparrow Auc3↑\uparrow F1↑\uparrow Auc3↑\uparrow CD↓\downarrow Auc3↑\uparrow F1↑\uparrow Auc3↑\uparrow F1↑\uparrow
a. Proposed Arch.39.2 47.0 21.0 55.4 45.8 3.82 26.2 47.6 30.3 51.1
b. VGGT Style 3.72 14.5 2.31 27.4 1.38 6.93 0.97 21.4 2.03 12.2
c. Full Alt.24.7 29.3 13.1 51.9 44.6 4.23 21.1 48.6 27.7 47.5
d. w/o Dual DPT 5.59 11.5 13.6 33.4 21.7 5.14 14.2 49.4 26.5 46.6
e. w/o Teacher 11.2 16.0 16.2 57.6 52.5 3.29 23.3 40.3 26.2 47.7
f. w/o Pose Cond.*65.8 63.2 3.65 58.4 62.8
g. w/ Pose Cond.*73.8 70.9 2.14 46.0 65.7

#### 7.2.2 Sufficiency of a Single Plain Transformer

We compare a standard ViT-L backbone with a VGGT-style architecture that stacks two distinct transformers, tripling the block count. For fair capacity comparison, the VGGT-style model uses smaller ViT-B backbones, yielding a similar parameter size to our ViT-L. Our backbone supports two attention strategies: Full Alt., which alternates cross-view/within-view attention in all layers (L=L g L=L_{\text{g}}), and our default partial alternation. As shown in Table [7](https://arxiv.org/html/2511.10647v1#S7.T7 "Tab. 7 ‣ 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), the VGGT-style model drops to 79.8% of our baseline performance, confirming the superiority of a single-transformer design at similar scale. We attribute this gap to full pretraining of our backbone versus two-thirds untrained blocks in VGGT. Moreover, the Full Alt. variant degrades across nearly all metrics—except F1 on 7Scenes—indicating that partial alternation is the more effective and robust strategy.

#### 7.2.3 Ablation and Analysis

##### Dual-DPT Head.

We assess the effectiveness of the dual-DPT head via an ablation in which two separate DPT heads predict depth and ray maps independently. Results are reported in [Tab.˜7](https://arxiv.org/html/2511.10647v1#S7.T7 "In 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), item (d). Compared with the model equipped with the dual-DPT head, the variant without it shows consistent drops across metrics, confirming the effectiveness of our dual-DPT design.

##### Teacher model supervision.

We ablate the use of teacher model labels as supervision, with quantitative results reported in [Tab.˜7](https://arxiv.org/html/2511.10647v1#S7.T7 "In 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), item (e). Training without teacher labels yields a slight improvement on DTU but leads to performance drops on 7Scenes and ScanNet++. Notably, the degradation is pronounced on HiRoom. We attribute this to HiRoom’s synthetic nature and its ground truth containing abundant fine structures; supervision from the teacher helps the student capture such details more accurately. Qualitative comparisons in [Fig.˜8](https://arxiv.org/html/2511.10647v1#S7.F8 "In Running time. ‣ 7.2.3 Ablation and Analysis ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views") corroborate this trend: models trained with teacher-label supervision produce depth maps with substantially richer detail and finer structures.

##### Pose conditioning.

To assess the pose-conditioning module, we ablate it on the ViT-L backbone and report results in [Tab.˜7](https://arxiv.org/html/2511.10647v1#S7.T7 "In 7.2.1 Sufficiency of the Depth-Ray Representation ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), items (f) and (g). Unlike other entries in the table, these two are evaluated with ground-truth pose fusion (marked with “*”), whereas the rest use predicted pose fusion. Across metrics, configurations with pose conditioning consistently outperform those without, confirming the effectiveness of the pose-conditioning module.

##### Running time.

We present analysis on Parameters, max number of images and running speed in [Tab.˜8](https://arxiv.org/html/2511.10647v1#S7.T8 "In Running time. ‣ 7.2.3 Ablation and Analysis ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views")

Table 8: Comparison of Models with Parameters and Running Speed. The maximum number of images was tested on an 80 GB A100 GPU. If we store some intermediate tokens in CPU memory, we could process many more images. The running speed was measured on an A100 GPU with a scene of 32 images, and we report the average speed per image. The image resolution is 504×336 504\times 336. 

Model Max # of Images Parameters Running Speed
Backbone DualDPT CameraHead
VGGT(Reference)400-500 0.91B 0.064B 0.22B 34.1 FPS
DA3-Giant 900-1000 1.130B 0.050B 0.018B 37.6 FPS
DA3-Large 1500-1600 0.300B 0.047B 0.008B 78.37 FPS
DA3-Base 2100-2200 0.086B 0.015B 0.004B 126.5 FPS
DA3-Small 4000-4100 0.022B 0.003B 0.001B 160.5 FPS

![Image 9: Refer to caption](https://arxiv.org/html/2511.10647v1/x6.png)

Figure 8: Comparison of teacher-label supervision. Supervision with teacher-generated labels yields depth maps with substantially richer detail and finer structures. 

Table 9: Ablations for teacher model. Training with V3 datasets and multi-resolution strategy yields the best performance. Depth-based geometry achieves the best AbsRel and SqRel. The full teacher-loss outperforms other variants. (AbsRel: ↓\downarrow, SqRel: ↓\downarrow, δ 1\delta_{1}: ↑\uparrow). The results are averaged over KITTI, NYU, ETH3D, SUN-RGBD and DIODE. 

Data Geometry Loss
Data δ 1\delta_{1}AbsRel SqRel Geometry δ 1\delta_{1}AbsRel SqRel Loss δ 1\delta_{1}AbsRel SqRel
V2 0.919 0.087 0.596 Disparity 0.919 0.095 1.033 MAE-Loss 0.918 0.089 0.637
V3 0.929 0.079 0.508 Pointmap 0.912 0.096 0.693 w/o Dist. Nor.0.918 0.087 0.600
V3 + mr.0.938 0.072 0.452 Depth 0.918 0.089 0.637 Full loss 0.919 0.087 0.596

![Image 10: Refer to caption](https://arxiv.org/html/2511.10647v1/x7.png)

Figure 9: Visualizations of camera pose and depth estimation on in-the-wild scenes.

##### More visualizations.

We provide additional visualizations of camera pose and depth estimation on in-the-wild scenes in [Fig.˜9](https://arxiv.org/html/2511.10647v1#S7.F9 "In Running time. ‣ 7.2.3 Ablation and Analysis ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), demonstrating the robustness and quality of our model across diverse real-world scenarios.

### 7.3 Analysis for Depth-Anything-3-Monocular

#### 7.3.1 Teacher Model

The teacher model’s metrics are reported in [Tab.˜4](https://arxiv.org/html/2511.10647v1#S7.T4 "In Geometry estimation. ‣ 7.1 Comparison with State of the Art ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"). Our new teacher consistently outperforms DA2 across all datasets, with the sole exception of NYU, where performance is on par with DA2. For the teacher ablation, we employ a ViT-L backbone and a batch size of 64. Evaluation follows the DA2 benchmark protocol, and we additionally report Squared Relative Error (SqRel), defined as the mean squared error between predictions and ground truth normalized by the ground truth. As shown in [Tab.˜9](https://arxiv.org/html/2511.10647v1#S7.T9 "In Running time. ‣ 7.2.3 Ablation and Analysis ‣ 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), across geometries, depth emerges as the most effective target compared with disparity and point maps. For training objectives, the full teacher loss proposed in this work outperforms both the DA2 loss and a variant without proposed normal-loss term. Finally, data scaling contribute notably to performance: upgrading datasets from V2 to V3 and adopting a multi-resolution training strategy yield consistent improvements in the teacher’s final metrics.

#### 7.3.2 Student Model

As shown in [Tab.˜10](https://arxiv.org/html/2511.10647v1#S7.T10 "In 7.3.2 Student Model ‣ 7.3 Analysis for Depth-Anything-3-Monocular ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), our monocular student model with a ViT-L backbone outperforms the DA2 student across all evaluation datasets. Notably, on the ETH3D [schops2017eth3d] benchmark the new monocular student achieves an improvement of over 10%10\% compared with DA2. The improved performance is attributed to the enhanced teacher model with better geometry supervision and the scaled training data (V3). On challenging datasets like SINTEL, our student also demonstrates substantial gains (+5.1%), validating the effectiveness of our teacher-student distillation framework.

Table 10: Monocular student depth comparisons.δ 1↑\delta_{1}\uparrow

Method KITTI NYU SINTEL ETH3D DIODE
DA2 94.6 97.9 77.2 86.5 95.2
mono-student 97.1 98.0 82.3 98.8 96.5

### 7.4 Analysis for Depth-Anything-3-Metric

We compare with state-of-the-art metric depth estimation methods, including DepthPro [bochkovskiydepth], Metric3D v2 [hu2024metric3dv2], UniDepthv1 [piccinelli2024unidepth] and UniDepthv2 [piccinelli2025unidepthv2], on 5 benchmarks: NYUv2 [silberman2012nyu], KITTI [geiger2013kitti], ETH3D [schops2017eth3d], SUN-RGBD [song2015sunrgbd] and DIODE (indoor) [vasiljevic2019diode].

As shown in [Tab.˜11](https://arxiv.org/html/2511.10647v1#S7.T11 "In 7.4 Analysis for Depth-Anything-3-Metric ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), DA3-metric achieves state-of-the-art performance on ETH3D (δ 1\delta_{1} = 0.917, AbsRel = 0.104), substantially outperforming the second-best method UniDepthv2 (δ 1\delta_{1} = 0.863) by a large margin. DA3-metric also achieves best performance on SUN-RGBD for AbsRel (0.105) and second-best on DIODE (δ 1\delta_{1} = 0.838, AbsRel = 0.128). While UniDepthv1 and UniDepthv2 achieve the best results on NYUv2 and KITTI, DA3-metric demonstrates strong generalization and competitive performance across all benchmarks, particularly excelling on diverse outdoor scenes like ETH3D.

We ablate the Teacher supervision in [Tab.˜11](https://arxiv.org/html/2511.10647v1#S7.T11 "In 7.4 Analysis for Depth-Anything-3-Metric ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"). The results show interesting trade-offs: removing Teacher supervision slightly improves metrics on NYUv2 and KITTI, while maintaining comparable performance on other datasets. As shown in Fig. [10](https://arxiv.org/html/2511.10647v1#S7.F10 "Fig. 10 ‣ 7.4 Analysis for Depth-Anything-3-Metric ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"), Teacher supervision significantly improves sharpness and fine detail quality, demonstrating that Teacher provides complementary knowledge beyond standard metrics.

Table 11: Comparison with state-of-the-arts on metric depth estimation. The best and second best are highlighted. Bottom rows show ablation results with and without teacher supervision. Note that the ablation setting is slightly different from the final model on training resolution, which leads to minor differences in performance.

Methods NYUv2 KITTI ETH3D SUN-RGBD DIODE
δ 1\delta_{1}↑\uparrow AbsRel↓\downarrow δ 1\delta_{1}↑\uparrow AbsRel↓\downarrow δ 1\delta_{1}↑\uparrow AbsRel↓\downarrow δ 1\delta_{1}↑\uparrow AbsRel↓\downarrow δ 1\delta_{1}↑\uparrow AbsRel↓\downarrow
DepthPro [bochkovskiydepth]0.932 0.093 0.843 0.121 0.386 0.349 0.950 0.126 0.734 0.173
Metric3D v2 [hu2024metric3d]0.971 0.067 0.976 0.051 0.830 0.138 0.954 0.132 0.018 0.154
UniDepthv1 [piccinelli2024unidepth]0.980 0.061 0.978 0.051 0.234 0.464 0.971 0.113 0.570 0.266
UniDepthv2 [piccinelli2025unidepthv2]0.968 0.064 0.968 0.076 0.863 0.152 0.977 0.111 0.856 0.123
DA3-metric 0.963 0.070 0.953 0.086 0.917 0.104 0.973 0.105 0.838 0.128
w/ teacher 0.966 0.073 0.947 0.086 0.906 0.105 0.973 0.104 0.824 0.132
w/o teacher 0.969 0.066 0.965 0.067 0.907 0.105 0.975 0.099 0.816 0.134

![Image 11: Refer to caption](https://arxiv.org/html/2511.10647v1/x8.png)

Figure 10: Effectiveness of Teacher model for supervising metric depth estimation. Incorporating Teacher model for supervision significantly improves the metric depth sharpness.

![Image 12: Refer to caption](https://arxiv.org/html/2511.10647v1/x9.png)

Figure 11: Qualitative comparisons with state-of-the-art methods for visual rendering. The first column shows the selected input views, while the remaining columns display novel views rendered by comparison models and ground truth. For each scene, two rendered novel viewpoints are presented in consecutive rows. The first three scenes are from DL3DV, the following two are from Tanks and Temples, and the last three are from MegaDepth. Compared to other methods, our model consistently achieves superior rendering quality across diverse and challenging scenes. 

### 7.5 Analysis for Feed-forward 3DGS

We retrain all compared feed-forward 3DGS models, ensuring that the training configuration matches the testing setup by using 12 input context views selected through farthest point sampling. We apply engineering optimizations such as flash attention and fully shared data parallelism to enable all models to process 12 input views efficiently. Depth training loss are incorporated for all baselines to ensure stable training and convergence. All models are trained on 8 A100 GPUs for 200K steps with a batch size of 1, except for pixelSplat, which is trained for 100K steps due to rather slow epipolar attention. All results are reported at H×W=270×480 H\times W=270\times 480.

##### Visual quality analysis.

We present visual comparisons with other models in [Fig.˜11](https://arxiv.org/html/2511.10647v1#S7.F11 "In 7.4 Analysis for Depth-Anything-3-Metric ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views") under novel view synthesis settings. As illustrated, simply augmenting our DA3 model with a 3D Gaussian DPT head yields significantly improved rendering quality over existing state-of-the-art approaches. Our model demonstrates particular strength in challenging regions, such as thin structures (e.g., columns in the first and third scenes) and large-scale outdoor environments with wide-baseline input views (last two scenes), as shown in [Fig.˜11](https://arxiv.org/html/2511.10647v1#S7.F11 "In 7.4 Analysis for Depth-Anything-3-Metric ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"). These results underscore the importance of a robust geometry backbone for high-quality visual rendering, consistent with our quantitative findings in [Tab.˜5](https://arxiv.org/html/2511.10647v1#S7.T5 "In 7.2 Analysis for Depth Anything 3 ‣ 7 Experiments ‣ Depth Anything 3: Recovering the Visual Space from Any Views"). We anticipate that the strong geometric understanding of DA3 will also benefit other 3D vision tasks.

8 Conclusion and Discussion
---------------------------

Depth Anything 3 shows that a plain transformer, trained on depth-and-ray targets with teacher–student supervision, can unify any-view geometry without ornate architectures. Scale-aware depth, per-pixel rays, and adaptive cross-view attention let the model inherit strong pretrained features while remaining lightweight and easy to extend. On the proposed visual geometry benchmark the approach sets new pose and reconstruction records, with both giant and compact variants surpassing prior models, while the same backbone powers efficient feed-forward novel view synthesis model.

We view Depth Anything 3 as a step toward versatile 3D foundation models. Future work can extend its reasoning to dynamic scenes, integrate language and interaction cues, and explore larger-scale pretraining to close the loop between geometry understanding and actionable world models. We hope the model and dataset releases, benchmark, and simple modeling principles offered here catalyze broader research on general-purpose 3D perception.

Acknowledgement
---------------

We thank Xiaowei Zhou, Sida Peng and Hengkai Guo for their valuable discussions during the development of this project. We are also grateful to Yang Zhao for his engineering support. The input images in the teaser demo were extracted from a publicly available YouTube video [mtsdrones2024], credited to the original creator.

\beginappendix

While synthetic datasets provide large-scale training data with ground-truth depth annotations, many contain quality issues such as invalid backgrounds, spatial misalignments, clipping artifacts, and erroneous depth values that can degrade model training. We therefore apply careful preprocessing to filter problematic samples and clip unrealistic depth ranges, ensuring high-quality supervision for our teacher model.

Appendix A Data Processing
--------------------------

We preprocess the following raw training datasets as follows to train the teacher model.

##### TartanAir.

We remove the amusement scene from training due to its invalid background (skybox) (Fig. [12](https://arxiv.org/html/2511.10647v1#A1.F12 "Fig. 12 ‣ TartanAir. ‣ Appendix A Data Processing ‣ Depth Anything 3: Recovering the Visual Space from Any Views")). We clip the maximum depth values of carwelding, hospital, ocean, office and office2 scenes at 80, 30, 1000, 30 and 30, respectively.

![Image 13: Refer to caption](https://arxiv.org/html/2511.10647v1/x10.png)

Figure 12: Invalid background of amusement scene in TartanAir dataset.

##### IRS.

We noticed that some of the scenes in IRS exhibit spatial misalignment between the image and depth maps (Fig. [13](https://arxiv.org/html/2511.10647v1#A1.F13 "Fig. 13 ‣ IRS. ‣ Appendix A Data Processing ‣ Depth Anything 3: Recovering the Visual Space from Any Views")). To filter those samples with image-depth misalignment, we first run Canny edge detectors on both the image (converted to grayscale) and depth map to extract the boundaries. Next, we dilate the boundaries by 1 pixel and compute the percentage of intersection between image and depth boundaries. Then, we further dilate the boundaries by 3 pixels and compute the intersection between image and depth boundaries. Finally, we compute the ratio between the two intersections and remove samples whose ratio falls below a certain threshold.

![Image 14: Refer to caption](https://arxiv.org/html/2511.10647v1/x11.png)

Figure 13: Image-depth spatial misalignment in IRS dataset.

##### UnrealStereo4K.

We remove the scene 00003 which consists of large erroneous regions. We also remove the scene 00004 which suffers from clipping issue. For scene 00008, we remove samples where the sea does not have depth values (images 9-13, 23-29, 80-82, 86-88, 96, 103-111, 126-136, 144-145, 148-154, 173-176, 178-179, 186-187, 191-192, 198-199) (Fig. [14](https://arxiv.org/html/2511.10647v1#A1.F14 "Fig. 14 ‣ UnrealStereo4K. ‣ Appendix A Data Processing ‣ Depth Anything 3: Recovering the Visual Space from Any Views")).

![Image 15: Refer to caption](https://arxiv.org/html/2511.10647v1/x12.png)

Figure 14: Erroneous samples in UnrealStereo4K dataset. The windows in scene 00003 are transparent; scene 00004 suffers from clipping issue; the sea in scene 00008 does not have depth values.

##### GTA-SfM.

We clip the maximum depth value at 1000.

##### Kenburns.

##### PointOdyssey.

##### TRELLIS.

We remove all samples with suffix stl, abc, STL, PLY, ply as we noticed that these samples do not contain texture.

##### OmniObject3D.

We clip the maximum depth value at 10.
