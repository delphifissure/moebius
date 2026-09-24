Title: pix2gestalt: Amodal Segmentation by Synthesizing Wholes

URL Source: https://arxiv.org/html/2401.14398

Published Time: Fri, 26 Jan 2024 14:28:54 GMT

Markdown Content:
\contourlength

0.8pt\contournumber 1

Ege Ozguroglu 1 1{}^{1}start_FLOATSUPERSCRIPT 1 end_FLOATSUPERSCRIPT Ruoshi Liu 1 1{}^{1}start_FLOATSUPERSCRIPT 1 end_FLOATSUPERSCRIPT Dídac Surís 1 1{}^{1}start_FLOATSUPERSCRIPT 1 end_FLOATSUPERSCRIPT Dian Chen 2 2{}^{2}start_FLOATSUPERSCRIPT 2 end_FLOATSUPERSCRIPT Achal Dave 2 2{}^{2}start_FLOATSUPERSCRIPT 2 end_FLOATSUPERSCRIPT Pavel Tokmakov 2 2{}^{2}start_FLOATSUPERSCRIPT 2 end_FLOATSUPERSCRIPT Carl Vondrick 1 1{}^{1}start_FLOATSUPERSCRIPT 1 end_FLOATSUPERSCRIPT

1 1{}^{1}start_FLOATSUPERSCRIPT 1 end_FLOATSUPERSCRIPT Columbia University 2 2{}^{2}start_FLOATSUPERSCRIPT 2 end_FLOATSUPERSCRIPT Toyota Research Institute 

[gestalt.cs.columbia.edu](https://gestalt.cs.columbia.edu/)

###### Abstract

We introduce pix2gestalt, a framework for zero-shot amodal segmentation, which learns to estimate the shape and appearance of whole objects that are only partially visible behind occlusions. By capitalizing on large-scale diffusion models and transferring their representations to this task, we learn a conditional diffusion model for reconstructing whole objects in challenging zero-shot cases, including examples that break natural and physical priors, such as art. As training data, we use a synthetically curated dataset containing occluded objects paired with their whole counterparts. Experiments show that our approach outperforms supervised baselines on established benchmarks. Our model can furthermore be used to significantly improve the performance of existing object recognition and 3D reconstruction methods in the presence of occlusions.

1 Introduction
--------------

Although only parts of the objects in Figure[1](https://arxiv.org/html/2401.14398v1#S1.F1 "Figure 1 ‣ 1 Introduction ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") are visible, you are able to visualize the whole object, recognize the category, and imagine its 3D geometry. Amodal completion is the task of predicting the whole shape and appearance of objects that are not fully visible, and this ability is crucial for many downstream applications in vision, graphics, and robotics. Learned by children from an early age [[30](https://arxiv.org/html/2401.14398v1#bib.bib30)], the ability can be partly explained by experience, but we seem to be able to generalize to challenging situations that break natural priors and physical constraints with ease. In fact, we can imagine the appearance of objects during occlusions that cannot exist in the physical world, such as the horse in Magritte’s The Blank Signature.

What makes amodal completion challenging compared to other synthesis tasks is that it requires grouping for both the visible and hidden parts of an object. To complete an object, we must be able to first recognize the object from partial observations, then synthesize only the missing regions for the object. Computer vision researchers and gestalt psychologists have extensively studied amodal completion in the past [[10](https://arxiv.org/html/2401.14398v1#bib.bib10), [49](https://arxiv.org/html/2401.14398v1#bib.bib49), [53](https://arxiv.org/html/2401.14398v1#bib.bib53), [18](https://arxiv.org/html/2401.14398v1#bib.bib18), [33](https://arxiv.org/html/2401.14398v1#bib.bib33), [35](https://arxiv.org/html/2401.14398v1#bib.bib35), [21](https://arxiv.org/html/2401.14398v1#bib.bib21), [17](https://arxiv.org/html/2401.14398v1#bib.bib17)], creating models that explicitly learn figure-ground separation. However, the prior work has been limited to representing objects in closed-world settings, restricted to only operating on the datasets on which they trained.

In this paper, we propose an approach for zero-shot amodal segmentation and reconstruction by learning to synthesize whole objects first. Our approach capitalizes on denoising diffusion models [[14](https://arxiv.org/html/2401.14398v1#bib.bib14)], which are excellent representations of the natural image manifold and capture all different types of whole objects and their occlusions. Due to their large-scale training data, we hypothesize such pre-trained models have implicitly learned amodal representations (Figure [2](https://arxiv.org/html/2401.14398v1#S2.F2 "Figure 2 ‣ 2.1 Amodal Completion and Segmentation ‣ 2 Related Work ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes")), which we can reconfigure to encode object grouping and perform amodal completion. By learning from a synthetic dataset of occlusions and their whole counterparts, we create a conditional diffusion model that, given an RGB image and a point prompt, generates whole objects behind occlusions and other obstructions.

Our main result is showing that we are able to achieve state-of-the-art amodal segmentation results in a zero-shot setting, outperforming the methods that were specifically supervised on those benchmarks. We furthermore show that our method can be used as a drop-in module to significantly improve the performance of existing object recognition and 3D reconstruction methods in the presence of occlusions. An additional benefit of the diffusion framework is that it allows sampling several variations of the reconstruction, naturally handling the inherent ambiguity of the occlusions.

![Image 1: Refer to caption](https://arxiv.org/html/2401.14398v1/x1.png)

Figure 1: Amodal Segmentation and Reconstruction via Synthesis. We present pix2gestalt, a method to synthesize whole objects from only partially visible ones, enabling amodal segmentation, recognition, novel-view synthesis, and 3D reconstruction of occluded objects. 

2 Related Work
--------------

We briefly review related work in amodal completion, analysis by synthesis, and denoising diffusion models for vision.

### 2.1 Amodal Completion and Segmentation

In this work, we define amodal completion as the task of generating the image of the whole object[[10](https://arxiv.org/html/2401.14398v1#bib.bib10), [49](https://arxiv.org/html/2401.14398v1#bib.bib49)], amodal segmentation as generating the segmentation mask of the whole object[[53](https://arxiv.org/html/2401.14398v1#bib.bib53), [18](https://arxiv.org/html/2401.14398v1#bib.bib18), [33](https://arxiv.org/html/2401.14398v1#bib.bib33), [35](https://arxiv.org/html/2401.14398v1#bib.bib35), [21](https://arxiv.org/html/2401.14398v1#bib.bib21)], and amodal detection as predicting the bounding box of the whole object[[17](https://arxiv.org/html/2401.14398v1#bib.bib17), [15](https://arxiv.org/html/2401.14398v1#bib.bib15)]. Most prior work focuses on the latter two tasks, due to the challenges in generating the (possibly ambiguous) pixels behind an occlusion. In addition, to our knowledge, all prior work on these tasks is limited to a small closed-world of objects[[49](https://arxiv.org/html/2401.14398v1#bib.bib49), [21](https://arxiv.org/html/2401.14398v1#bib.bib21), [18](https://arxiv.org/html/2401.14398v1#bib.bib18), [33](https://arxiv.org/html/2401.14398v1#bib.bib33), [17](https://arxiv.org/html/2401.14398v1#bib.bib17)] or to synthetic data[[10](https://arxiv.org/html/2401.14398v1#bib.bib10)]. For example, PCNet[[49](https://arxiv.org/html/2401.14398v1#bib.bib49)], the previous state-of-the-art method for amodal segmentation, operates only on a closed-world set of classes in Amodal COCO[[53](https://arxiv.org/html/2401.14398v1#bib.bib53)].

Our approach, by contrast, provides rich image completions with accurate masks, generalizing to diverse zero-shot settings, while still outperforming state-of-the-art methods in a closed-world. To achieve this degree of generalization, we capitalize on large-scale diffusion models, which implicitly learn internal representations of whole objects. We propose to unlock this capability by fine-tuning a diffusion model on a synthetically generated, realistic dataset of varied occlusions.

![Image 2: Refer to caption](https://arxiv.org/html/2401.14398v1/x2.png)

Figure 2: Whole Objects. Pre-trained diffusion models are able to generate all kinds of whole objects. We show samples conditioned on a category from Stable Diffusion. We leverage this synthesis ability for zero-shot amodal reconstruction and segmentation.

![Image 3: Refer to caption](https://arxiv.org/html/2401.14398v1/x3.png)

Figure 3: pix2gestalt is an amodal completion model using a latent diffusion architecture. Conditioned on an input occlusion image and a region of interest, the whole (amodal) form is synthesized, thereby allowing other visual tasks to be performed on it too. For conditioning details, see section [3.2](https://arxiv.org/html/2401.14398v1#S3.SS2 "3.2 Conditional Diffusion ‣ 3 Amodal Completion via Generation ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes").

### 2.2 Analysis by Synthesis

Our approach is heavily inspired by analysis by synthesis[[47](https://arxiv.org/html/2401.14398v1#bib.bib47)] – a generative approach for visual reasoning. Image parsing[[42](https://arxiv.org/html/2401.14398v1#bib.bib42)] was a representative work that unifies segmentation, recognition, and detection by generation. Prior works have applied the analysis by synthesis approaches on various problems including face recognition[[42](https://arxiv.org/html/2401.14398v1#bib.bib42), [5](https://arxiv.org/html/2401.14398v1#bib.bib5)], pose estimation[[51](https://arxiv.org/html/2401.14398v1#bib.bib51), [27](https://arxiv.org/html/2401.14398v1#bib.bib27)], 3D reconstruction[[22](https://arxiv.org/html/2401.14398v1#bib.bib22), [23](https://arxiv.org/html/2401.14398v1#bib.bib23)], semantic image editing[[1](https://arxiv.org/html/2401.14398v1#bib.bib1), [24](https://arxiv.org/html/2401.14398v1#bib.bib24), [52](https://arxiv.org/html/2401.14398v1#bib.bib52)]. In this paper, we aim to harness the power of generative models trained with internet-scale data for the task of amodal completion, thereby aiding various tasks such as recognition, segmentation, and 3D reconstruction in the presence of occlusions.

### 2.3 Diffusion Models

Recently, Denoising Diffusion Probabilistic Model[[14](https://arxiv.org/html/2401.14398v1#bib.bib14)], or DDPM, has emerged as one of the most widely used generative architectures in computer vision due to its ability to model multi-modal distributions, training stability, and scalability. [[8](https://arxiv.org/html/2401.14398v1#bib.bib8)] first showed that diffusion models outperform GANs[[12](https://arxiv.org/html/2401.14398v1#bib.bib12)] in image synthesis. Stable Diffusion[[36](https://arxiv.org/html/2401.14398v1#bib.bib36)], trained on LAION-5B[[39](https://arxiv.org/html/2401.14398v1#bib.bib39)], applied diffusion model in the latent space of a variational autoencoder[[19](https://arxiv.org/html/2401.14398v1#bib.bib19)] to improve computational efficiency. Later, a series of major improvements were made to improve diffusion model performance[[13](https://arxiv.org/html/2401.14398v1#bib.bib13), [41](https://arxiv.org/html/2401.14398v1#bib.bib41)]. With the release of Stable Diffusion as a strong generative prior, many works have adapted it to solve tasks in different domain such as image editing[[6](https://arxiv.org/html/2401.14398v1#bib.bib6), [11](https://arxiv.org/html/2401.14398v1#bib.bib11), [37](https://arxiv.org/html/2401.14398v1#bib.bib37)], 3D[[25](https://arxiv.org/html/2401.14398v1#bib.bib25), [7](https://arxiv.org/html/2401.14398v1#bib.bib7), [45](https://arxiv.org/html/2401.14398v1#bib.bib45)], and modal segmentation[[46](https://arxiv.org/html/2401.14398v1#bib.bib46), [2](https://arxiv.org/html/2401.14398v1#bib.bib2), [3](https://arxiv.org/html/2401.14398v1#bib.bib3)]. In this work, we leverage the strong occlusion and complete object priors provided by internet-pretrained diffusion model to solve the zero-shot amodal completion task.

3 Amodal Completion via Generation
----------------------------------

Given an RGB image x 𝑥 x italic_x with an occluded object that is partially visible, our goal is to predict a new image with the shape and appearance of the whole object, and only the whole object. Our approach will accept any point or mask as a prompt p 𝑝 p italic_p indicating the modal object:

x^p=f θ⁢(x,p)subscript^𝑥 𝑝 subscript 𝑓 𝜃 𝑥 𝑝\displaystyle\hat{x}_{p}=f_{\theta}(x,p)over^ start_ARG italic_x end_ARG start_POSTSUBSCRIPT italic_p end_POSTSUBSCRIPT = italic_f start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT ( italic_x , italic_p )

where x^p subscript^𝑥 𝑝\hat{x}_{p}over^ start_ARG italic_x end_ARG start_POSTSUBSCRIPT italic_p end_POSTSUBSCRIPT is our estimate of the whole object indicated by p 𝑝 p italic_p. Mapping from x 𝑥 x italic_x to this unified whole form, _i.e_.gestalt of the occluded object, we name our method pix2gestalt. We want x^^𝑥\hat{x}over^ start_ARG italic_x end_ARG to be perceptually similar to the true but unobserved whole of the object as if there was no occlusion. We will use a conditional diffusion model (see Figure[3](https://arxiv.org/html/2401.14398v1#S2.F3 "Figure 3 ‣ 2.1 Amodal Completion and Segmentation ‣ 2 Related Work ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes")) for f θ subscript 𝑓 𝜃 f_{\theta}italic_f start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT.

An advantage of this approach is that, once we estimate an image of the whole object x^^𝑥\hat{x}over^ start_ARG italic_x end_ARG, we are able to perform any other computer vision task on it, providing a unified method to handle occlusions across different tasks. Since we will directly synthesize the pixels of the whole object, we can aid off-the-shelf approaches to perform segmentation, recognition, and 3D reconstruction of occluded objects.

To perform amodal completion, f 𝑓 f italic_f needs to learn a representation of whole objects in the visual world. Due to their scale of training data, we will capitalize on large pretrained diffusion models, such as Stable Diffusion, which are excellent representations of the natural image manifold and have the support to generate unoccluded objects. However, although they generate high-quality images, their representations do not explicitly encode the grouping of objects and their boundaries to the background.

### 3.1 Whole-Part Pairs

To learn the conditional diffusion model f 𝑓 f italic_f with the ability for grouping, we build a large-scale paired dataset of occluded objects and their whole counterparts. Unfortunately, collecting a natural image dataset of these pairs is challenging at scale. Prior datasets provide amodal segmentation annotations [[53](https://arxiv.org/html/2401.14398v1#bib.bib53), [33](https://arxiv.org/html/2401.14398v1#bib.bib33)], but they do not reveal the pixels behind an occlusion. Other datasets have relied on graphical simulation [[16](https://arxiv.org/html/2401.14398v1#bib.bib16)], which lack the realistic complexity and scale of everyday object categories.

We build paired data by automatically overlaying objects over natural images. The original images provide ground-truth for the content behind occlusions. However, we need to ensure that we only occlude whole objects in this construction, as otherwise our model could learn to generate incomplete objects. To this end, we use a heuristic that, if the object is closer to the camera than its neighboring objects, then it is likely a whole object. We use Segment Anything[[20](https://arxiv.org/html/2401.14398v1#bib.bib20)] to automatically find object candidates in the SA-1B dataset, and use the off-the-shelf monocular depth estimator MiDaS[[4](https://arxiv.org/html/2401.14398v1#bib.bib4)] to select which objects are whole. For each image with at least one whole object, we sample an occluder and superimpose it, resulting in a paired dataset of 837⁢K 837 𝐾 837K 837 italic_K images and their whole counterparts. Figure [4](https://arxiv.org/html/2401.14398v1#S3.F4 "Figure 4 ‣ 3.2 Conditional Diffusion ‣ 3 Amodal Completion via Generation ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") illustrates this construction and shows examples of the heuristic.

### 3.2 Conditional Diffusion

Given pairs of an image x 𝑥 x italic_x and its whole counterpart x^p subscript^𝑥 𝑝\hat{x}_{p}over^ start_ARG italic_x end_ARG start_POSTSUBSCRIPT italic_p end_POSTSUBSCRIPT, we fine-tune a conditional diffusion model to perform amodal completion while maintaining the zero-shot capabilities of the pre-trained model. We solve for the following latent diffusion objective:

min θ⁡𝔼 z∼ℰ⁢(x),t,ϵ∼𝒩⁢(0,1)⁢[‖ϵ−ϵ θ⁢(z t,ℰ⁢(x),t,ℰ⁢(p),𝒞⁢(x))‖2 2]subscript 𝜃 subscript 𝔼 formulae-sequence similar-to 𝑧 ℰ 𝑥 𝑡 similar-to italic-ϵ 𝒩 0 1 delimited-[]superscript subscript norm italic-ϵ subscript italic-ϵ 𝜃 subscript 𝑧 𝑡 ℰ 𝑥 𝑡 ℰ 𝑝 𝒞 𝑥 2 2\displaystyle\min_{\theta}\;\mathbb{E}_{z\sim\mathcal{E}(x),t,\epsilon\sim% \mathcal{N}(0,1)}\left[||\epsilon-\epsilon_{\theta}(z_{t},\mathcal{E}(x),t,% \mathcal{E}(p),\mathcal{C}(x))||_{2}^{2}\right]roman_min start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT blackboard_E start_POSTSUBSCRIPT italic_z ∼ caligraphic_E ( italic_x ) , italic_t , italic_ϵ ∼ caligraphic_N ( 0 , 1 ) end_POSTSUBSCRIPT [ | | italic_ϵ - italic_ϵ start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT ( italic_z start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT , caligraphic_E ( italic_x ) , italic_t , caligraphic_E ( italic_p ) , caligraphic_C ( italic_x ) ) | | start_POSTSUBSCRIPT 2 end_POSTSUBSCRIPT start_POSTSUPERSCRIPT 2 end_POSTSUPERSCRIPT ]

where 0≤t<1000 0 𝑡 1000 0\leq t<1000 0 ≤ italic_t < 1000 is the diffusion time step, z t subscript 𝑧 𝑡 z_{t}italic_z start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT is the embedding of the noised amodal target image x^p subscript^𝑥 𝑝\hat{x}_{p}over^ start_ARG italic_x end_ARG start_POSTSUBSCRIPT italic_p end_POSTSUBSCRIPT. 𝒞⁢(x)𝒞 𝑥\mathcal{C}(x)caligraphic_C ( italic_x ) is the CLIP embedding of the input image, and ℰ⁢(⋅)ℰ⋅\mathcal{E}(\cdot)caligraphic_E ( ⋅ ) is a VAE embedding. Following [[6](https://arxiv.org/html/2401.14398v1#bib.bib6), [25](https://arxiv.org/html/2401.14398v1#bib.bib25)], we apply classifier-free guidance (CFG) [[13](https://arxiv.org/html/2401.14398v1#bib.bib13)] by setting the conditional information to a null vector randomly.

Amodal completion requires reasoning about the whole shape, its appearance, and contextual visual cues of the scene. We adapt the design in [[6](https://arxiv.org/html/2401.14398v1#bib.bib6), [25](https://arxiv.org/html/2401.14398v1#bib.bib25)] to condition the diffusion model ϵ θ subscript italic-ϵ 𝜃\epsilon_{\theta}italic_ϵ start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT in two separate streams. 𝒞⁢(x)𝒞 𝑥\mathcal{C}(x)caligraphic_C ( italic_x ) conditions the diffusion model ϵ θ subscript italic-ϵ 𝜃\epsilon_{\theta}italic_ϵ start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT via cross-attention on the semantic features of the partially visible object in x 𝑥 x italic_x as specified by p 𝑝 p italic_p, providing high-level perception. On the VAE stream, we channel concatenate ℰ⁢(x)ℰ 𝑥\mathcal{E}(x)caligraphic_E ( italic_x ) and z t subscript 𝑧 𝑡 z_{t}italic_z start_POSTSUBSCRIPT italic_t end_POSTSUBSCRIPT, providing low-level visual details (shade, color, texture), as well as ℰ⁢(p)ℰ 𝑝\mathcal{E}(p)caligraphic_E ( italic_p ) to indicate the visible region of the object.

After ϵ θ subscript italic-ϵ 𝜃\epsilon_{\theta}italic_ϵ start_POSTSUBSCRIPT italic_θ end_POSTSUBSCRIPT is trained, f 𝑓 f italic_f can generate x^p subscript^𝑥 𝑝\hat{x}_{p}over^ start_ARG italic_x end_ARG start_POSTSUBSCRIPT italic_p end_POSTSUBSCRIPT by performing iterative denoising [[36](https://arxiv.org/html/2401.14398v1#bib.bib36)]. The CFG can be scaled to control impact of the conditioning on the completion.

![Image 4: Refer to caption](https://arxiv.org/html/2401.14398v1/extracted/5356073/figures/dataset.png)

Figure 4: Constructing Training Data. To ensure we only occlude whole objects, we use a heuristic that objects closer to the camera than its neighbors are likely whole objects. The green outline around the object shows where the estimated depth is closer to the camera than the background (the red shows when it is not).

### 3.3 Amodal Base Representations

Since we synthesize RGB images of the whole object, our approach makes it straightforward to equip various computer vision methods with the ability to handle occlusions. We discuss a few common cases.

Image Segmentation aims to find the spatial boundaries of an object given an image x 𝑥 x italic_x and an initial prompt p 𝑝 p italic_p. We can perform amodal segmentation by completing an occluded object with f 𝑓 f italic_f, then thresholding the result to obtain an amodal segmentation map. Note that this problem is under-constrained as there are multiple possible solutions. Given the uncertainty, we found that sampling multiple completions and performing a majority vote on the segmentation masks works best in practice.

Object Recognition is the task of classifying an object located in an bounding box or mask p 𝑝 p italic_p. We can zero-shot recognize significantly occluded objects by first completing the whole object with f 𝑓 f italic_f, then classifying the amodal completion with CLIP.

3D Reconstruction estimates the appearance and geometry of an object. We can zero-shot reconstruct objects with partial occlusions by first completing the whole object with f 𝑓 f italic_f, then applying SyncDreamer and Score Distillation Sampling[[32](https://arxiv.org/html/2401.14398v1#bib.bib32)] to estimate a textured mesh.

4 Experiments
-------------

We evaluate pix2gestalt’s ability to perform zero-shot amodal completion for three tasks: amodal segmentation, occluded object recognition, and amodal 3D reconstruction. We show that our method provides amodal completions that directly lead to strong results in all tasks.

![Image 5: Refer to caption](https://arxiv.org/html/2401.14398v1/x4.png)

Figure 5: In-the-wild Amodal Completion and Segmentation. We find that pix2gestalt is able to synthesize whole objects in novel situations, including artistic pieces, images taken by an iPhone, and illusions.

![Image 6: Refer to caption](https://arxiv.org/html/2401.14398v1/x5.png)

Figure 6: Amodal Completion and Segmentation Qualitative Results on Amodal COCO. In blue circles, we highlight completion regions that, upon a closer look, have a distorted texture in the PCNet baseline, and a correct one in our results.

### 4.1 Amodal Segmentation

Setup. Amodal segmentation requires segmenting the full extent of a (possibly occluded) object. We evaluate this task on the Amodal COCO (COCO-A)[[53](https://arxiv.org/html/2401.14398v1#bib.bib53)] and Amodal Berkeley Segmentation (BSDS-A) datasets[[28](https://arxiv.org/html/2401.14398v1#bib.bib28)]. For evaluation, COCO-A provides 13,000 amodal annotations of objects in 2,500 images, while BSDS-A provides 650 objects from 200 images. For both datasets, we evaluate methods that take as input an image and a (modal) mask of the visible extent of an object, and output an amodal mask of the full-extent of the object. Following[[49](https://arxiv.org/html/2401.14398v1#bib.bib49)], we evaluate segmentations using mean intersection-over-union (mIoU). We follow the strategy in [Section 3.3](https://arxiv.org/html/2401.14398v1#S3.SS3 "3.3 Amodal Base Representations ‣ 3 Amodal Completion via Generation ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") to convert our amodal completions into segmentation masks.

We evaluate three baselines for amodal segmentation. The first method is PCNet[[49](https://arxiv.org/html/2401.14398v1#bib.bib49)], which is trained for amodal segmentation specifically for COCO-A. Next, we compare to two zero-shot methods, which do not train on COCO-A: Segment Anything (SAM)[[20](https://arxiv.org/html/2401.14398v1#bib.bib20)], a strong modal segmentation method, and Inpainting using Stable Diffusion-XL [[31](https://arxiv.org/html/2401.14398v1#bib.bib31)]. To evaluate inpainting methods, we provide as input an image with all but the visible object region erased, and convert the completed image output by the method into an amodal segmentation mask following the same strategy as for our method.

Results. Table [1](https://arxiv.org/html/2401.14398v1#S4.T1 "Table 1 ‣ 4.1 Amodal Segmentation ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") compares pix2gestalt with prior work. Despite never training on the COCO-A dataset, our method outperforms all baselines, including PCNet, which uses COCO-A images for training, and even PCNet-Sup, which is supervised using human-annotated amodal segmentations from COCO-A’s training set. Compared to other zero-shot methods, our improvements are dramatic, validating the generalization abilities of our method. Notably, we also outperform the inpainting baseline which is based off a larger, more recent variant of Stable Diffusion [[31](https://arxiv.org/html/2401.14398v1#bib.bib31)]. This demonstrates that internet-scale training alone is not sufficient and our fine-tuning approach is key to reconfigure priors from pre-training for amodal completion.

We further analyze amodal completions qualitatively in Figure [6](https://arxiv.org/html/2401.14398v1#S4.F6 "Figure 6 ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes"). While SD-XL often hallucinates extraneous, unrealistic details (e.g. person in front of the bus in the second row), PCNet tends to fail to recover the full extent of objects—often only generating the visible region, as in the Mario example in the third row. In contrast, pix2gestalt provides accurate, complete reconstructions of occluded objects on both COCO-A (Figure [6](https://arxiv.org/html/2401.14398v1#S4.F6 "Figure 6 ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes")) and BSDS-A (Figure [7](https://arxiv.org/html/2401.14398v1#S4.F7 "Figure 7 ‣ 4.1 Amodal Segmentation ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes")). Our method generalizes well beyond the typical occlusion scenarios found in those benchmarks. Figure[5](https://arxiv.org/html/2401.14398v1#S4.F5 "Figure 5 ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") shows several examples of out-of-distribution images, including art pieces, illusions, and images taken by ourselves that are successfully handled by our method. Note that no prior work has shown open-world generalization (see [2.1](https://arxiv.org/html/2401.14398v1#S2.SS1 "2.1 Amodal Completion and Segmentation ‣ 2 Related Work ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes")).

Figure[8](https://arxiv.org/html/2401.14398v1#S4.F8 "Figure 8 ‣ 4.1 Amodal Segmentation ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") illustrates the ability of the approach to generate diverse samples in shape and appearance when there is uncertainty in the final completion. For example, it is able to synthesize several plausible completions of the occluded house in the painting. We quantitatively evaluate the diversity of our samples in the last row of Table[1](https://arxiv.org/html/2401.14398v1#S4.T1 "Table 1 ‣ 4.1 Amodal Segmentation ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") by sampling from our model three times and reporting the performance for the best sample (“Best of 3”). Finally, we found limitations of our approach in situations that require commonsense or physical reasoning. We show two examples in Figure [9](https://arxiv.org/html/2401.14398v1#S4.F9 "Figure 9 ‣ 4.2 Occluded Object Recognition ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes").

![Image 7: Refer to caption](https://arxiv.org/html/2401.14398v1/x6.png)

Figure 7: Amodal Berkeley Segmentation Dataset Qualitative Results. Our method provides accurate, complete reconstructions of occluded objects.

![Image 8: Refer to caption](https://arxiv.org/html/2401.14398v1/x7.png)

Figure 8: Diversity in Samples. Amodal completion has inherent uncertainties. By sampling from the diffusion process multiple times, the method synthesizes multiple plausible wholes that are consistent with the input observations.

Table 1: Amodal Segmentation Results. We report mIoU (%)↑normal-↑\uparrow↑ on Amodal COCO [[53](https://arxiv.org/html/2401.14398v1#bib.bib53)] and on Amodal Berkeley Segmentation Dataset [[53](https://arxiv.org/html/2401.14398v1#bib.bib53), [28](https://arxiv.org/html/2401.14398v1#bib.bib28)]. *{}^{*}start_FLOATSUPERSCRIPT * end_FLOATSUPERSCRIPT PCNet-Sup trains using ground truth amodal masks from COCO-Amodal. See [Section 4.1](https://arxiv.org/html/2401.14398v1#S4.SS1 "4.1 Amodal Segmentation ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") for analysis.

### 4.2 Occluded Object Recognition

Next, we evaluate the utility of our method for recognizing occluded objects.

Setup. We use the Occluded and Separated COCO benchmarks[[48](https://arxiv.org/html/2401.14398v1#bib.bib48)] for evaluating classification accuracy under occlusions. The former consists of partially occluded objects, whereas Separated COCO contains objects whose modal region is separated into disjoint segments by the occluder(s), resulting in a more challenging problem setting. We evaluate on all 80 COCO semantic categories in the datasets using Top 1 and Top 3 accuracy.

We use CLIP[[34](https://arxiv.org/html/2401.14398v1#bib.bib34)] as the base open-vocabulary classifier. As baselines, we evaluate CLIP without any completion, reporting three variants: providing the entire image (CLIP), providing the entire image with a visual prompt (a red circle, as in Shtedritski _et al_.[[40](https://arxiv.org/html/2401.14398v1#bib.bib40)]) around the occluded object, or providing an image with all but the visible portion of the occluded object masked out. To evaluate our approach, we first utilize it to complete the occluded object, and then classify the output image using CLIP.

Results. Table [2](https://arxiv.org/html/2401.14398v1#S4.T2 "Table 2 ‣ 4.2 Occluded Object Recognition ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") compares our method with the baselines. Visual prompting with a red circle (RC) and masking all but the visible object (Vis.Obj.) provide improvements over directly passing the image to CLIP on the simpler Occluded COCO benchmark, but fail to improve, and some times even decreases the performance of the baseline CLIP on the more challenging Separated COCO variant. Our method (Ours + CLIP), however, strongly outperforms all baselines for both the occluded and separated datasets, verifying the quality of our completions.

Table 2: Occluded Object Recognition. We report zero-shot classification accuracy on Occluded and Separated COCO [[48](https://arxiv.org/html/2401.14398v1#bib.bib48)]. While simple baselines fail to improve CLIP performance in the more challenging Separated COCO setting, our method consistently improves recognition accuracy by large margins. See [Section 4.2](https://arxiv.org/html/2401.14398v1#S4.SS2 "4.2 Occluded Object Recognition ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") for analysis.

![Image 9: Refer to caption](https://arxiv.org/html/2401.14398v1/x8.png)

Figure 9: Common-sense and Physics Failures. Left: reconstruction has the car going in the wrong direction. Right: reconstruction contradicts physics, failing to capture that a hand must be holding the donut box.

![Image 10: Refer to caption](https://arxiv.org/html/2401.14398v1/x9.png)

Figure 10: Amodal 3D Reconstruction qualitative results. The object of interest is specified by a point prompt, shown in yellow. Incorporating pix2gestalt as a drop-in module to state-of-the-art 3D reconstruction models allows us to address challenging and diverse occlusion scenarios with ease.

### 4.3 Amodal 3D Reconstruction

Finally, we evaluate our method for improving 3D reconstruction of occluded objects.

Setup. We focus on two tasks: Novel-view synthesis and single-view 3D reconstruction.

To demonstrate pix2gestalt’s performance as a drop-in module to 3D foundation models [[25](https://arxiv.org/html/2401.14398v1#bib.bib25), [26](https://arxiv.org/html/2401.14398v1#bib.bib26), [38](https://arxiv.org/html/2401.14398v1#bib.bib38)], we replicate the evaluation procedure of Zero-1-to-3[[26](https://arxiv.org/html/2401.14398v1#bib.bib26), [25](https://arxiv.org/html/2401.14398v1#bib.bib25)] on Google Scanned Objects (GSO) [[9](https://arxiv.org/html/2401.14398v1#bib.bib9)], a dataset of common household objects 3D scanned for use in embodied, synthetic, and 3D perception tasks. We use 30 randomly sampled objects from GSO ranging from daily objects to animals. For each object, we render a 256x256 image with synthetic occlusions sampled from the full dataset of 1,030 objects in GSO. We render from a randomly sampled view to avoid canonical poses, and generate two occluded images for each of the 30 objects, resulting in 60 samples.

For amodal novel-view synthesis, we quantitatively evaluate our method using 3 metrics: PSNR, SSIM [[44](https://arxiv.org/html/2401.14398v1#bib.bib44)], and LPIPS [[50](https://arxiv.org/html/2401.14398v1#bib.bib50)], measuring the image-similarity of the input and ground truth views. For 3D reconstruction, we use the Volumetric IoU and Chamfer Distance metrics. We compare our approach with SyncDreamer [[26](https://arxiv.org/html/2401.14398v1#bib.bib26)], a 3D generative model that fine-tunes Zero123-XL [[7](https://arxiv.org/html/2401.14398v1#bib.bib7), [25](https://arxiv.org/html/2401.14398v1#bib.bib25)] for multi-view consistent novel view synthesis and consequent 3D reconstruction with NeuS [[43](https://arxiv.org/html/2401.14398v1#bib.bib43)] and NeRF [[29](https://arxiv.org/html/2401.14398v1#bib.bib29)]. Our first baseline provides as input to SyncDreamer the segmentation mask of all foreground objects, following the standard protocol. To avoid reconstructing occluded objects, we additionally evaluate two variants that use SAM[[20](https://arxiv.org/html/2401.14398v1#bib.bib20)] to estimate the mask of only the object of interest, or the ground truth mask for the object of interest (GT Mask). Finally, to evaluate our method, we provide as input the full object completed by our method, along with the corresponding amodal mask. We evaluate two variants of our method: One where we provide a modal mask for the object of interested as estimated by SAM (Ours (SAM Mask)) and one where we use the ground truth modal mask (Ours (GT Mask)).

Table 3: Single-view 3D Reconstruction. We report Chamfer Distance and Volumetric IoU for Google Scanned Objects. See [Section 4.3](https://arxiv.org/html/2401.14398v1#S4.SS3 "4.3 Amodal 3D Reconstruction ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") for analysis.

Results. We compare our approach with the two baselines in Table[4](https://arxiv.org/html/2401.14398v1#S4.T4 "Table 4 ‣ 4.3 Amodal 3D Reconstruction ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") for novel view synthesis and Table[3](https://arxiv.org/html/2401.14398v1#S4.T3 "Table 3 ‣ 4.3 Amodal 3D Reconstruction ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") for 3D reconstruction. Quantitative results demonstrate that we strongly outperform the baselines for both tasks. In novel-view synthesis, we outperform SAM + SyncDreamer on the image reconstruction metrics, LPIPS [[50](https://arxiv.org/html/2401.14398v1#bib.bib50)] and PSNR [[44](https://arxiv.org/html/2401.14398v1#bib.bib44)]. Compared to SAM as a modal pre-processor, we obtain these improvements as a drop-in module to SyncDreamer while still retaining equivalent image quality (Table[4](https://arxiv.org/html/2401.14398v1#S4.T4 "Table 4 ‣ 4.3 Amodal 3D Reconstruction ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes"), SSIM [[44](https://arxiv.org/html/2401.14398v1#bib.bib44)]). With ground truth mask inputs, we obtain further image reconstruction gains. Moreover, even though our approach utilizes an additional diffusion step compared to SyncDreamer only, we demonstrate less image quality degradation.

For reconstruction of the 3D geometry, our fully automatic method outperforms all of the baselines for both volumetric IoU and Chamfer distance metrics, even the baselines that use ground masks. Providing the ground truth to our approach further improves the results. Figure [10](https://arxiv.org/html/2401.14398v1#S4.F10 "Figure 10 ‣ 4.2 Occluded Object Recognition ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") shows qualitative evaluation for 3D reconstruction of occluded objects, ranging from an Escher lithograph to in-the-wild images.

Table 4: Novel-view synthesis from one image. We report results on Google Scanned Objects [[9](https://arxiv.org/html/2401.14398v1#bib.bib9)]. Note SSIM measures image quality, not novel-view accuracy. See [Section 4.3](https://arxiv.org/html/2401.14398v1#S4.SS3 "4.3 Amodal 3D Reconstruction ‣ 4 Experiments ‣ pix2gestalt: Amodal Segmentation by Synthesizing Wholes") for analysis.

5 Conclusion
------------

In this work, we proposed a novel approach for zero-shot amodal segmentation via synthesis. Our model capitalizes on whole object priors learned by internet-scale diffusion models and unlocks them via fine-tuning on a synthetically generated dataset of realistic occlusions. We then demonstrated that synthesizing the whole object makes it straightforward to equip various computer vision methods with the ability to handle occlusions. In particular, we reported state-of-the art results on several benchmarks for amodal segmentation, occluded object recognition and 3D reconstruction.

Acknowledgements: This research is based on work partially supported by the Toyota Research Institute, the DARPA MCS program under Federal Agreement No. N660011924032, the NSF NRI Award #1925157, and the NSF AI Institute for Artificial and Natural Intelligence Award #2229929. DS is supported by the Microsoft PhD Fellowship.

References
----------

*   Abdal et al. [2019] Rameen Abdal, Yipeng Qin, and Peter Wonka. Image2StyleGAN: How to embed images into the stylegan latent space? In _ICCV_, 2019. 
*   Amit et al. [2021] Tomer Amit, Tal Shaharbany, Eliya Nachmani, and Lior Wolf. Segdiff: Image segmentation with diffusion probabilistic models. _arXiv preprint arXiv:2112.00390_, 2021. 
*   Baranchuk et al. [2021] Dmitry Baranchuk, Ivan Rubachev, Andrey Voynov, Valentin Khrulkov, and Artem Babenko. Label-efficient semantic segmentation with diffusion models. _arXiv preprint arXiv:2112.03126_, 2021. 
*   Birkl et al. [2023] Reiner Birkl, Diana Wofk, and Matthias Müller. Midas v3.1 – a model zoo for robust monocular relative depth estimation. _arXiv preprint arXiv:2307.14460_, 2023. 
*   Blanz and Vetter [2023] Volker Blanz and Thomas Vetter. A morphable model for the synthesis of 3d faces. In _Seminal Graphics Papers: Pushing the Boundaries, Volume 2_, pages 157–164. 2023. 
*   Brooks et al. [2023] Tim Brooks, Aleksander Holynski, and Alexei A. Efros. Instructpix2pix: Learning to follow image editing instructions. In _CVPR_, 2023. 
*   Deitke et al. [2023] Matt Deitke, Ruoshi Liu, Matthew Wallingford, Huong Ngo, Oscar Michel, Aditya Kusupati, Alan Fan, Christian Laforte, Vikram Voleti, Samir Yitzhak Gadre, et al. Objaverse-xl: A universe of 10m+ 3d objects. _arXiv preprint arXiv:2307.05663_, 2023. 
*   Dhariwal and Nichol [2021] Prafulla Dhariwal and Alexander Nichol. Diffusion models beat gans on image synthesis. _NeurIPS_, 2021. 
*   Downs et al. [2022] Laura Downs, Anthony Francis, Nate Koenig, Brandon Kinman, Ryan Hickman, Krista Reymann, Thomas B. McHugh, and Vincent Vanhoucke. Google scanned objects: A high-quality dataset of 3D scanned household items. In _ICRA_, 2022. 
*   Ehsani et al. [2018] Kiana Ehsani, Roozbeh Mottaghi, and Ali Farhadi. Segan: Segmenting and generating the invisible. In _CVPR_, 2018. 
*   Gal et al. [2022] Rinon Gal, Yuval Alaluf, Yuval Atzmon, Or Patashnik, Amit H Bermano, Gal Chechik, and Daniel Cohen-Or. An image is worth one word: Personalizing text-to-image generation using textual inversion. _arXiv preprint arXiv:2208.01618_, 2022. 
*   Goodfellow et al. [2014] Ian Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu, David Warde-Farley, Sherjil Ozair, Aaron Courville, and Yoshua Bengio. Generative adversarial nets. _NeurIPS_, 2014. 
*   Ho and Salimans [2022] Jonathan Ho and Tim Salimans. Classifier-free diffusion guidance. _arXiv preprint arXiv:2207.12598_, 2022. 
*   Ho et al. [2020] Jonathan Ho, Ajay Jain, and Pieter Abbeel. Denoising diffusion probabilistic models. _NeurIPS_, 33, 2020. 
*   Hsieh et al. [2023] Cheng-Yen Hsieh, Tarasha Khurana, Achal Dave, and Deva Ramanan. Tracking any object amodally, 2023. 
*   Hu et al. [2019] Y.-T. Hu, H.-S. Chen, K. Hui, J.-B. Huang, and A.G. Schwing. SAIL-VOS: Semantic Amodal Instance Level Video Object Segmentation – A Synthetic Dataset and Baselines. In _Proc. CVPR_, 2019. 
*   Kar et al. [2015] Abhishek Kar, Shubham Tulsiani, Joao Carreira, and Jitendra Malik. Amodal completion and size constancy in natural scenes. In _ICCV_, 2015. 
*   Ke et al. [2021] Lei Ke, Yu-Wing Tai, and Chi-Keung Tang. Deep occlusion-aware instance segmentation with overlapping bilayers. In _CVPR_, 2021. 
*   Kingma and Welling [2013] Diederik P Kingma and Max Welling. Auto-encoding variational bayes. _arXiv preprint arXiv:1312.6114_, 2013. 
*   Kirillov et al. [2023] Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, Chloe Rolland, Laura Gustafson, Tete Xiao, Spencer Whitehead, Alexander C. Berg, Wan-Yen Lo, Piotr Dollár, and Ross Girshick. Segment anything. In _ICCV_, 2023. 
*   Ling et al. [2020] Huan Ling, David Acuna, Karsten Kreis, Seung Wook Kim, and Sanja Fidler. Variational amodal object completion. _NeurIPS_, 2020. 
*   Liu and Vondrick [2023] Ruoshi Liu and Carl Vondrick. Humans as light bulbs: 3d human reconstruction from thermal reflection. In _CVPR_, 2023. 
*   Liu et al. [2022] Ruoshi Liu, Sachit Menon, Chengzhi Mao, Dennis Park, Simon Stent, and Carl Vondrick. Shadows shed light on 3d objects. _arXiv preprint arXiv:2206.08990_, 2022. 
*   Liu et al. [2023a] Ruoshi Liu, Chengzhi Mao, Purva Tendulkar, Hao Wang, and Carl Vondrick. Landscape learning for neural network inversion. In _ICCV_, 2023a. 
*   Liu et al. [2023b] Ruoshi Liu, Rundi Wu, Basile Van Hoorick, Pavel Tokmakov, Sergey Zakharov, and Carl Vondrick. Zero-1-to-3: Zero-shot one image to 3d object. In _ICCV_, 2023b. 
*   Liu et al. [2023c] Yuan Liu, Cheng Lin, Zijiao Zeng, Xiaoxiao Long, Lingjie Liu, Taku Komura, and Wenping Wang. Syncdreamer: Learning to generate multiview-consistent images from a single-view image. _arXiv preprint arXiv:2309.03453_, 2023c. 
*   Ma et al. [2022] Wufei Ma, Angtian Wang, Alan Yuille, and Adam Kortylewski. Robust category-level 6D pose estimation with coarse-to-fine rendering of neural features. In _ECCV_, 2022. 
*   Martin et al. [2001] D. Martin, C. Fowlkes, D. Tal, and J. Malik. A database of human segmented natural images and its application to evaluating segmentation algorithms and measuring ecological statistics. In _ICCV_, 2001. 
*   Mildenhall et al. [2020] Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, and Ren Ng. Nerf: Representing scenes as neural radiance fields for view synthesis. In _ECCV_, 2020. 
*   Piaget [2013] Jean Piaget. _The construction of reality in the child_. Routledge, 2013. 
*   Podell et al. [2023] Dustin Podell, Zion English, Kyle Lacey, Andreas Blattmann, Tim Dockhorn, Jonas Müller, Joe Penna, and Robin Rombach. Sdxl: Improving latent diffusion models for high-resolution image synthesis, 2023. 
*   Poole et al. [2022] Ben Poole, Ajay Jain, Jonathan T Barron, and Ben Mildenhall. Dreamfusion: Text-to-3d using 2d diffusion. _arXiv preprint arXiv:2209.14988_, 2022. 
*   Qi et al. [2019] Lu Qi, Li Jiang, Shu Liu, Xiaoyong Shen, and Jiaya Jia. Amodal instance segmentation with KINS dataset. In _CVPR_, 2019. 
*   Radford et al. [2021] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, and Ilya Sutskever. Learning transferable visual models from natural language supervision, 2021. 
*   Reddy et al. [2022] N Dinesh Reddy, Robert Tamburo, and Srinivasa G Narasimhan. Walt: Watch and learn 2d amodal representation from time-lapse imagery. In _CVPR_, 2022. 
*   Rombach et al. [2022] Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Björn Ommer. High-resolution image synthesis with latent diffusion models. In _CVPR_, 2022. 
*   Ruiz et al. [2023] Nataniel Ruiz, Yuanzhen Li, Varun Jampani, Yael Pritch, Michael Rubinstein, and Kfir Aberman. Dreambooth: Fine tuning text-to-image diffusion models for subject-driven generation. In _CVPR_, 2023. 
*   Sargent et al. [2023] Kyle Sargent, Zizhang Li, Tanmay Shah, Charles Herrmann, Hong-Xing Yu, Yunzhi Zhang, Eric Ryan Chan, Dmitry Lagun, Li Fei-Fei, Deqing Sun, and Jiajun Wu. ZeroNVS: Zero-shot 360-degree view synthesis from a single real image. _arXiv preprint arXiv:2310.17994_, 2023. 
*   Schuhmann et al. [2022] Christoph Schuhmann, Romain Beaumont, Richard Vencu, Cade Gordon, Ross Wightman, Mehdi Cherti, Theo Coombes, Aarush Katta, Clayton Mullis, Mitchell Wortsman, et al. Laion-5B: An open large-scale dataset for training next generation image-text models. _NeurIPS_, 2022. 
*   Shtedritski et al. [2023] Aleksandar Shtedritski, Christian Rupprecht, and Andrea Vedaldi. What does clip know about a red circle? visual prompt engineering for vlms. In _ICCV_, 2023. 
*   Song et al. [2020] Jiaming Song, Chenlin Meng, and Stefano Ermon. Denoising diffusion implicit models. _arXiv preprint arXiv:2010.02502_, 2020. 
*   Tu et al. [2005] Zhuowen Tu, Xiangrong Chen, Alan L Yuille, and Song-Chun Zhu. Image parsing: Unifying segmentation, detection, and recognition. _International Journal of computer vision_, 63:113–140, 2005. 
*   Wang et al. [2021] Peng Wang, Lingjie Liu, Yuan Liu, Christian Theobalt, Taku Komura, and Wenping Wang. Neus: Learning neural implicit surfaces by volume rendering for multi-view reconstruction. _arXiv preprint arXiv:2106.10689_, 2021. 
*   Wang et al. [2004] Zhou Wang, Alan C Bovik, Hamid R Sheikh, and Eero P Simoncelli. Image quality assessment: from error visibility to structural similarity. _IEEE Transactions on Image Processing_, 13(4):600–612, 2004. 
*   Wu et al. [2023] Rundi Wu, Ruoshi Liu, Carl Vondrick, and Changxi Zheng. Sin3dm: Learning a diffusion model from a single 3d textured shape. _arXiv preprint arXiv:2305.15399_, 2023. 
*   Xu et al. [2023] Jiarui Xu, Sifei Liu, Arash Vahdat, Wonmin Byeon, Xiaolong Wang, and Shalini De Mello. Open-Vocabulary Panoptic Segmentation with Text-to-Image Diffusion Models. _arXiv preprint arXiv:2303.04803_, 2023. 
*   Yuille and Kersten [2006] Alan Yuille and Daniel Kersten. Vision as bayesian inference: analysis by synthesis? _Trends in cognitive sciences_, 10(7):301–308, 2006. 
*   Zhan et al. [2022] Guanqi Zhan, Weidi Xie, and Andrew Zisserman. A tri-layer plugin to improve occluded detection. _BMVC_, 2022. 
*   Zhan et al. [2020] Xiaohang Zhan, Xingang Pan, Bo Dai, Ziwei Liu, Dahua Lin, and Chen Change Loy. Self-supervised scene de-occlusion. In _CVPR_, 2020. 
*   Zhang et al. [2018] Richard Zhang, Phillip Isola, Alexei A Efros, Eli Shechtman, and Oliver Wang. The unreasonable effectiveness of deep features as a perceptual metric. In _CVPR_, 2018. 
*   Zhang et al. [2023] Yi Zhang, Pengliang Ji, Angtian Wang, Jieru Mei, Adam Kortylewski, and Alan Yuille. 3D-Aware neural body fitting for occlusion robust 3d human pose estimation. In _ICCV_, 2023. 
*   Zhu et al. [2020] Jiapeng Zhu, Yujun Shen, Deli Zhao, and Bolei Zhou. In-domain GAN inversion for real image editing. In _ECCV_, 2020. 
*   Zhu et al. [2017] Yan Zhu, Yuandong Tian, Dimitris Metaxas, and Piotr Dollár. Semantic amodal segmentation. In _CVPR_, 2017.
