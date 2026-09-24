# MiniMax-Remover: Taming Bad Noise Helps Video Object Removal

Bojia Zi \*

The Chinese University of Hong Kong

Weixuan Peng \*

Shenzhen University

Xianbiao Qi †

IntelliFusion Inc.

Jianan Wang

Astribot Inc.

Shihao Zhao

The University of Hong Kong

Rong Xiao

IntelliFusion Inc.

Kam-Fai Wong

The Chinese University of Hong Kong

Figure 1: Visual Results of MiniMax-Remover. The left side displays the original videos, while the right side shows the edited results. Our method achieves high-quality removal of the target objects: the girl, chameleon, bird, lane line, and red wine glass, as illustrated in the five corresponding video examples. *Best viewed with Acrobat Reader. Click the images to play the animations.*

## Abstract

Recent advances in video diffusion models have driven rapid progress in video editing techniques. However, video object removal, a critical subtask of video editing, remains challenging due to issues such as hallucinated objects and visual artifacts. Furthermore, existing methods often rely on computationally expensive sampling

\*Equal contribution.

†Corresponding author. Email: qixianbiao@gmail.comprocedures and classifier-free guidance (CFG), resulting in slow inference. To address these limitations, we propose **MiniMax-Remover**, a novel two-stage video object removal approach. Motivated by the observation that text condition is not best suited for this task, we simplify the pretrained video generation model by removing textual input and cross-attention layers, resulting in a more lightweight and efficient model architecture in the first stage. In the second stage, we distilled our remover on successful videos produced by the stage-1 model and curated by human annotators, using a minimax optimization strategy to further improve editing quality and inference speed. Specifically, the inner maximization identifies adversarial input noise (“bad noise”) that makes failure removals, while the outer minimization step trains the model to generate high-quality removal results even under such challenging conditions. As a result, our method achieves a state-of-the-art video object removal results with as few as 6 sampling steps and doesn’t rely on CFG, significantly improving inference efficiency. Extensive experiments demonstrate the effectiveness and superiority of MiniMax-Remover compared to existing methods. Codes and Videos are available at: <https://minimax-remover.github.io>.

## 1 Introduction

In recent years, diffusion models [4, 3, 15, 7, 10, 36, 49, 21, 33, 32, 43] have driven remarkable progress in image and video generation. UNet-based architectures, exemplified by models such as AnimateDiff [15] and VideoCrafter2 [7], have demonstrated impressive capabilities in generating high-quality videos. More recently, the field has advanced with the introduction of transformer-based architectures, as seen in groundbreaking works such as Sora [36], HunyuanVideo [21] and Wan2.1 [43], which employ DiT-based structures [37] to achieve unprecedented generation quality. Parallel to these advancements, diffusion-based video editing techniques [6, 50, 45, 11, 29, 46, 2, 19, 55, 27, 47, 12, 9, 22] have also seen significant progress. Among these, *video inpainting* has emerged as a particularly crucial capability, serving as a foundational component for numerous fine-grained video editing applications.

Video object removal focuses on erasing specified objects from videos while preserving background consistency and temporal coherence. ProPainter [54] addressed this by completing optical flow within masked regions and then synthesizing the fill-in content using vision transformers, rather than relying on generative models. More recently, the field has shifted toward diffusion-based methods, with several notable advancements. FFF-VDI [23] uses optical flow and generative model to inpaint videos. DiffuEraser [24] employs DDIM inversion and vision priors to enhance video inpainting quality. Similarly, FloED [14] proposes a dual-branch architecture and a two-stage training strategy to achieve higher fidelity in the regions where objects are intended to be removed.

Despite rapid progress, existing video object removal methods still face multiple challenges. Some methods generate undesired content or artifacts, while others introduce occlusions and blurs within masked regions. Furthermore, most approaches rely heavily on auxiliary priors (*e.g.*, optical flow, text prompts, or DDIM inversion). The complicated model design lead to unsuitability and limit user-friendliness. Moreover, the generative methods require a large number of sampling steps to achieve high visual fidelity and depend on classifier-free guidance (CFG), which requires two model evaluations per sampling step, further exacerbates inference latency, limiting their practicality in real-world applications.

To address these limitations, we propose a two-stage framework for video object removal that simultaneously enhances visual quality and reduces inference cost. In **Stage 1**, we train upon Wan2.1-1.3B[43] and introduce two key modifications: (i) replacing external text prompts with learnable *contrastive condition tokens*, and (ii) removing all cross-attention layers within the DiT blocks, instead injecting contrastive condition tokens directly into the self-attention stream to enable conditional control. This lightweight conditioning approach significantly reduces computational overhead while preserving the structural integrity of the DiT backbone, allowing the same weights to be reused in the next stage, even when conditional control is disabled. In **Stage 2**, we distill the remover on manually curate 10K high-quality object removal samples generated by the model in Stage 1 and introduce a *minimax* optimization strategy to further improve object removal performance. The inner maximization searches for adversarial noise (“bad” noise) that induces model failure, while the outer minimization trains the model to be robust against such challenging cases. This minimaxTable 1: Comparison of our MiniMax-Remover and other Video Inpainting Methods. We compare these methods on a video with 33 frames and 360P resolution on A800 GPUs, using their default configuration. “-” means unknown, while “N/A” means not applicable. Senorita-R means Senorita-2M remover expert.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th rowspan="2">Params</th>
<th colspan="4">•Inference Details</th>
<th colspan="4">•Additional Condition / Prior</th>
<th rowspan="2">Open-Source</th>
</tr>
<tr>
<th>Min Steps</th>
<th>CFG</th>
<th>Latency (s)</th>
<th>GPU Mem (GB)</th>
<th>DDIM Inversion</th>
<th>Optical Flow</th>
<th>Text Prompt</th>
<th>First Frame</th>
</tr>
</thead>
<tbody>
<tr>
<td>AVID[53]</td>
<td>1.95B</td>
<td>-</td>
<td>✓</td>
<td>-</td>
<td>-</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>×</td>
</tr>
<tr>
<td>FFF-VDI[23]</td>
<td>-</td>
<td>50</td>
<td>✓</td>
<td>-</td>
<td>-</td>
<td>✓</td>
<td>✓</td>
<td>×</td>
<td>×</td>
<td>×</td>
</tr>
<tr>
<td>VIVID[19]</td>
<td>5.19B</td>
<td>50</td>
<td>✓</td>
<td>-</td>
<td>-</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>✓</td>
<td>×</td>
</tr>
<tr>
<td>Senorita-R[55]</td>
<td>1.58B</td>
<td>50</td>
<td>✓</td>
<td>-</td>
<td>-</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>×</td>
</tr>
<tr>
<td>MTV-Inpaint[48]</td>
<td>1.32B</td>
<td>30</td>
<td>✓</td>
<td>-</td>
<td>-</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>×</td>
</tr>
<tr>
<td>Propainter[54]</td>
<td>37.5M</td>
<td>N/A</td>
<td>N/A</td>
<td>0.27</td>
<td>13.5</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>×</td>
<td>✓</td>
</tr>
<tr>
<td>VideoComposer[46]</td>
<td>1.31B</td>
<td>50</td>
<td>✓</td>
<td>2.83</td>
<td>49.1</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>✓</td>
</tr>
<tr>
<td>COCOCO[56]</td>
<td>1.45B</td>
<td>50</td>
<td>✓</td>
<td>3.56</td>
<td>36.5</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>✓</td>
</tr>
<tr>
<td>FloED[14]</td>
<td>1.30B</td>
<td>25</td>
<td>✓</td>
<td>1.32</td>
<td>47.6</td>
<td>×</td>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td>✓</td>
</tr>
<tr>
<td>DiffuEraser[24]</td>
<td>2.04B</td>
<td>70</td>
<td>✓</td>
<td>0.35</td>
<td>10.4</td>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td>×</td>
<td>✓</td>
</tr>
<tr>
<td>VideoPainter[2]</td>
<td>5.45B</td>
<td>50</td>
<td>✓</td>
<td>8.14</td>
<td>44.7</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>✓</td>
</tr>
<tr>
<td>VACE[20]</td>
<td>1.66B</td>
<td>25</td>
<td>✓</td>
<td>1.93</td>
<td>23.6</td>
<td>×</td>
<td>×</td>
<td>✓</td>
<td>×</td>
<td>✓</td>
</tr>
<tr>
<td><b>MiniMax-Remover</b></td>
<td>1.05B</td>
<td>6</td>
<td>×</td>
<td>0.18</td>
<td>8.2</td>
<td>×</td>
<td>×</td>
<td>×</td>
<td>×</td>
<td>✓</td>
</tr>
</tbody>
</table>

optimization enables our remover to consistently produce artifact-free results and prevents generating undesired objects without the assistance of CFG. As a result, the final model achieves both superior visual quality and remarkable inference efficiency compared to existing methods.

### Our main contributions are summarized as follows:

1. 1. we propose a lightweight yet effective DiT-based architecture for video object removal. Motivated by the observation that text prompting is not best suited for the task of object removal, we replace the text conditions with learnable contrastive tokens to control the removal process. These tokens are integrated directly into the self-attention stream, allowing us to remove all cross-attention layers within the pretrained video generation model. *As a result, in Stage 1, our model features fewer parameters and no longer depends on ambiguous text instruction.*
2. 2. In Stage 2, we distilled a remover on 10K manually selected video removals produced by the model in Stage 1, with minmax optimization strategy. Specifically, the inner maximization optimization finds a bad input noise that makes model fail, while the outer minimization optimization tries to teach model remove the bad noise added on the successful videos.
3. 3. We conduct extensive experiments across multiple benchmarks, demonstrating that our method achieves superior performance in both inference speed and visual fidelity. As shown in Figure 4 and Table 1, *our model produces high-quality removal results using as few as 6 sampling steps and without relying on classifier-free guidance (CFG).*

## 2 Preliminary

**Flow Matching.** Given an input  $\mathbf{x} \in \mathbb{R}^{f \times w \times h \times c}$ , a pretrained VAE encoder maps it to a latent code  $\mathbf{z}_0 = \mathcal{E}(\mathbf{x}_0) \in \mathbb{R}^{f_1 \times w_1 \times h_1 \times c_1}$ . The model input is a noisy latent  $\mathbf{z}_t$ , where  $\mathbf{z}_t = t\epsilon + (1-t)\mathbf{z}_0$ , where  $\epsilon \sim \mathcal{N}(0, \mathbf{I})$  and  $t \in [0, 1]$ .  $t$  is usually sampled from a logit-normal distribution. The target velocity is  $\mathbf{v} = \epsilon - \mathbf{z}_0$ . The optimization process of Flow Matching is defined as,

$$\theta^* = \operatorname{argmin}_{\theta} \mathbb{E}_{t, \mathbf{z}_t} \left[ \|\mathbf{u}_{\theta}(\mathbf{z}_t, t) - \mathbf{v}\|_2^2 \right], \quad (1)$$

$\mathbf{u}_{\theta}$  denotes the model parameterized by  $\theta$ . The model can be a DiT [37] or UNet [42] architecture.

**Diffusion-based Video Inpainting.** This approach is to reconstruct masked video regions using a conditional diffusion model. The denoising network  $\mathbf{u}_{\theta}$  takes a noisy latent  $\mathbf{z}_t$ , a masked latent  $\mathbf{z}_m$ , a latent code  $\bar{\mathbf{m}}$  for the mask  $\mathbf{m}$ , and a condition  $\mathbf{c}$  as inputs. It optimizes the following objective,

$$\theta^* = \operatorname{argmin}_{\theta} \mathbb{E}_{t, \mathbf{z}_t} \left[ \|\mathbf{u}_{\theta}(\mathbf{z}_t, \mathbf{z}_m, \bar{\mathbf{m}}, \mathbf{c}, t) - \epsilon_t\|_2^2 \right]. \quad (2)$$

Generally,  $\mathbf{c}$  could be optical flow or text prompts.**Classifier-Free Guidance (CFG).** CFG [17] improves conditional generation by training the model with and without condition  $c$ . The network jointly learns the following processes,

$$\mathbf{u}_\theta(\mathbf{z}_t, t, c) \propto -\nabla_{\mathbf{z}_t} \log p_\theta(\mathbf{z}_t|c), \quad \mathbf{u}_\theta(\mathbf{z}_t, t, \emptyset) \propto -\nabla_{\mathbf{z}_t} \log p_\theta(\mathbf{z}_t), \quad (3)$$

In the inference stage, it combines the following two modes:

$$\hat{\mathbf{u}}_\theta(\mathbf{z}_t, t) = \mathbf{u}_\theta(\mathbf{z}_t, t, \emptyset) + w \cdot (\mathbf{u}_\theta(\mathbf{z}_t, t, c) - \mathbf{u}_\theta(\mathbf{z}_t, t, \emptyset)), \quad (4)$$

where  $w$  controls the conditioning strength. However, employing CFG at inference time doubles the computational cost, as it requires two forward passes per sampling step.

**MiniMax Optimization.** It is widely employed in classical convex optimization [5], robustness enhancement and generative adversarial networks (GANs) [13]. The objective is defined as,

$$\theta^* = \underset{\theta}{\operatorname{argmin}} \max_{\mathbf{z}} \mathcal{L}(f(\mathbf{z}, \theta), y) \quad (5)$$

where  $\mathcal{L}$  is the loss function,  $f$  is the model with parameter  $\theta$ ,  $\mathbf{z}$  and  $y$  are the input and ground truth.

### 3 Methodology

#### 3.1 Overall Framework

**Stage 1: Training a lightweight video object removal model.** Our method follows the standard video inpainting pipeline, but with two simple yet effective improvements. First, we design a lightweight architecture by removing irrelevant components. Unlike many existing methods [56, 53, 46, 24], we do not use text prompts or extra inputs such as optical flow and text prompts, allowing us to remove all cross-attention layers. Second, we introduce two contrastive condition tokens to guide the inpainting process: a *positive token*, which encourages the model to fill in content within the masked regions, and a *negative token*, which discourages the model from generating unwanted objects in those areas. It should be noted that *unlike prior works* [53, 54, 23], *we only use object mask and do not rely on additional conditions*.

**Stage 2: Enhancing model robustness and efficiency via human-guided minimax optimization.** We first use the model in Stage 1 to generate inpainted video samples and then ask human annotators to identify successful results. Using this curated subset, we apply a minimax optimization training scheme to enhance the model’s robustness and generation quality. Furthermore, the distilled remover can use as few as 6 steps without the help of CFG, resulting a fast inference. The resulting improved model is referred to as **MiniMax-Remover**.

#### 3.2 Stage 1: A Simple Architecture for Video Object Removal

Our method is built on the pretrained video generation model Wan2.1-1.3B [43], which is a Flow Matching model with DiT architecture.

##### 3.2.1 Model Architecture

**Input Layer.** We start by concatenating three types of latents: a noisy latent  $\mathbf{z}_t$ , a masked latent  $\mathbf{z}_m$ , and a mask latent  $\bar{\mathbf{m}}$ . They are defined as  $\mathbf{z}_t = t\epsilon + (1 - t)\mathbf{z}_0$ , where  $\mathbf{z}_0 = \mathcal{E}(\mathbf{x})$ ,  $\mathbf{z}_m = \mathcal{E}(\mathbf{m} \odot \mathbf{x})$ , and  $\bar{\mathbf{m}} = \mathcal{E}(\mathbf{m})$ . Here,  $\mathbf{x}$  denotes the input video,  $t \in [0, 1]$  is the diffusion timestep, and  $\mathcal{E}$  is the VAE encoder. Each latent has 16 channels, resulting in a concatenated input of 48 channels. To accommodate this input, we modify the pretrained patch embedding layer to accept 48 channels instead of the original 16. Specifically, the first 16 channels retain the pretrained weights, while the remaining 32 channels are zero-initialized.

**Removing Cross Attention from Pretrained DiT Block.** In the pretrained Wan2.1-1.3B [43] model, time information is injected via a *shift table*, a bias-based mechanism to encode timestep information. Additionally, the model employs a cross-attention module to incorporate textual conditioning during video generation. However, for the task of video object removal, textual input is often unnecessary or ambiguous. Therefore, in our model, we remove the textual cross-attention layers in the DiT blocks, while retaining the shift table to preserve time information. **Injecting Contrastive Condition Tokens via Self-Attention.** To enable conditional inpainting, we introduce two learnable condition tokens,Figure 2: The comparison between different blocks. (a) the original Wan2.1 DiT block; (b) DiT block with contrastive tokens (positive or negative token); (c) the block with removing the CFG.

denoted as  $c^+$  (positive token) and  $c^-$  (negative token), as a replacement for text embeddings. We refer to these tokens as **contrastive condition tokens**.

Removing the cross-attention from DiT introduces a challenge: how to effectively inject conditional information without relying on textual prompts. A straightforward approach is to repurpose the shift table to incorporate both timestep and condition information. However, our experiments show that this approach leads to unsatisfactory conditional inpainting results. To achieve more effective conditioning, we instead inject the contrastive condition tokens into the DiT block via the self-attention module. Specifically, we employ a learnable embedding layer to project the conditional token into a high-dimensional feature, and then split the feature into 6 tokens to increase control ability in attention computation process. These condition tokens are concatenated with the original keys and values in the self-attention module, enabling effective conditioning with minimal architectural modifications. For clarity, consider an example: in the original self-attention module, let  $Q \in \mathcal{R}^{n \times d}$ ,  $K \in \mathcal{R}^{n \times d}$ ,  $V \in \mathcal{R}^{n \times d}$ , after injecting the condition tokens,  $Q \in \mathcal{R}^{n \times d}$ ,  $K \in \mathcal{R}^{(n+6) \times d}$ ,  $V \in \mathcal{R}^{(n+6) \times d}$ . The updated DiT block after injecting contrastive condition tokens is illustrated in Figure 2(b).

Figure 3: The pipeline of our two-stage method.

### 3.2.2 Contrastive Conditioning for Object Removal

We employ the positive condition token  $c^+$  to guide the remover network in learning object removal and encourage the model to generate target objects under the guidance of  $c^-$ . Specifically, when applying classifier-free guidance,  $c^+$  serves as the positive condition and  $c^-$  as the negative condition, steering the model away from regenerating the target objects, preventing the reappearance of undesired objects within the masked regions. To train this behavior, we use two complementary strategies: **First, training the model to remove objects.** We randomly select masks from other videos andapply them to the current original video. The original video is used as the ground truth, and the model is conditioned on the positive prompt  $c^+$ . Since these masks usually don’t match any real object in the current video, the model learns to fill the masked areas using information from the surroundings, instead of trying to recreate an object that fits the mask shape. This helps the model focus on inpainting the background rather than generating new objects. **Second, training the model to generate objects.** We use accurate masks that tightly cover real objects in the same video, along with the negative prompt  $c^-$ . This teaches the model to connect the shape of the mask with the object it should generate. During inference, we can use  $c^-$  as a negative signal to prevent the model from reconstructing the object in those areas. More details are provided in the Appendix.

Given latent features  $z_t$ , masked latents  $z_m$ , mask latents  $\bar{m}$ , and timestep  $t$ , the network  $u_\theta$  predicts:

$$\hat{z}_{t-1}^+ = u_\theta(z_t, z_m, \bar{m}, c^+, t), \quad \hat{z}_{t-1}^- = u_\theta(z_t, z_m, \bar{m}, c^-, t). \quad (6)$$

Using CFG with guidance weight  $w$ , the final prediction is computed as:

$$\hat{z}_{t-1} = \hat{z}_{t-1}^- + w(\hat{z}_{t-1}^+ - \hat{z}_{t-1}^-). \quad (7)$$

The positive token guides the remover network in learning object removal, and the negative token encourages the model to generate object content. We would like to point out that we employ CFG during Stage 1 of training to facilitate conditional learning. However, CFG is removed in Stage 2 to improve inference efficiency.

### 3.2.3 Limitations of Stage 1

Despite improvements in simplicity and speed, the current model still faces three limitations. (1) CFG doubles the inference time and requires manual tuning of the guidance scale, which can vary across videos. (2) sampling 50 diffusion steps per frame remains time-consuming. (3) Artifacts or undesired object regeneration may occasionally occur within the intended object removal region, indicating that the contrastive signal is not yet fully effective. To address these limitations, we introduce our Stage 2 method, which is designed to enhance robustness, quality, and efficiency.

## 3.3 MiniMax-Remover: Distill a Stronger Video Object Remover from Human Feedback

Although our video object remover is trained with contrastive conditioning, it still produces noticeable artifacts and occasionally reconstructs the very object it is supposed to erase. Upon closer examination, we observe that these failure cases are strongly correlated with specific input noise patterns. This insight motivates our objective: to identify such “bad noise” and train the object removal model to be robust against it.

The minmax optimization also allows us to escape from the CFG usage. In Stage 2, we eliminate CFG to improve sampling efficiency. Specifically, during training, we omit both the positive and the negative condition token. We choose to leave more analysis on this design in Appendix.

Moreover, performing inference with 50 steps is time-consuming. To address this, we distill the model in Stage 1 using the Rectified Flow method [30] to accelerate the sampling process. Specifically, we manually selected 10K video pairs from the 17K generated by the Stage 1 model as training data. This not only reduces the number of sampling steps but, with the help of min-max optimization, also encourages the model to produce better object removal results. Consequently, our model formulation changes from  $u_\theta(z_t, z_m, \bar{m}, c, t)$  to  $u_\theta(z_t, z_m, \bar{m}, t)$ . We formulate our stage-2 training as a minimax optimization problem:

$$\min_{\theta} \max_{\epsilon} \mathbb{E}_t \|u_\theta(z_t, z_m, \bar{m}, t) - v\|^2, \quad \text{where } v = \epsilon - z_{\text{succ}} \text{ and } z_t = t\epsilon + (1-t)z_0. \quad (8)$$

Therefore, the inner maximization seeks bad noise that maximizes the prediction error, effectively finding challenging input noise. The outer minimization then updates the model parameters  $\theta$  to be robust against such adversarial noise. This minimax optimization strategy encourages the model to remain stable even under difficult or misleading input noise.

### 3.3.1 Search for "Bad" Noise

One of the key challenges in Equation 8 is how to effectively identify a “bad” noise sample  $\epsilon$ . Rather than directly maximizing the loss in Equation 8 using successful object removal cases, we insteadminimize the loss with respect to a bad target: specifically, the original video, which fails to meet the objective of object removal. This leads to the following reformulated objective:

$$\min_{\epsilon \sim \mathcal{N}(0, I)} \|\mathbf{u}_\theta(\mathbf{z}_t = \epsilon, \mathbf{z}_m, \bar{\mathbf{m}}, t = 1.0) - \mathbf{v}\|^2, \quad \text{where } \mathbf{v} = \text{sg}(\epsilon) - \mathbf{z}_{\text{org}}, \quad (9)$$

where  $\text{sg}(\cdot)$  is the stop gradient operation and  $\mathbf{z}_{\text{org}}$  denotes the latent code of the original video. It is important to note that, in Equation 9, we omit the expectation  $\mathbb{E}_{t, \mathbf{z}_t}$ , because we fix the diffusion timestep to  $t = 1.0$ , making  $\mathbf{z}_t = \epsilon$ .

Starting from a random noise  $\mathbf{z}_{t=1} = \epsilon$ , we compute the gradient of the loss function with respect to  $\epsilon$  via backpropagation. This gradient is given by:

$$\nabla_\epsilon = \partial \|\mathbf{u}_\theta(\epsilon, \mathbf{z}_m, \bar{\mathbf{m}}, t = 1) - \mathbf{v}\|^2 / \partial \epsilon \quad (10)$$

After obtaining the gradient with respect to the noise, we can construct a new adversarial (“bad”) noise sample  $\epsilon^*$  as follows,

$$\epsilon^* \leftarrow \sqrt{1 - \alpha} \epsilon - \sqrt{\alpha} \text{sign}(\nabla_\epsilon) \cdot |\epsilon'|, \quad (11)$$

where  $\epsilon'$  is a newly sampled noise,  $\text{sign}(\nabla_\epsilon)$  is the sign of the gradient obtained in Equation 10, and  $\alpha \in [0, 1]$  is a randomly sampled scalar. We use only the sign of the gradient to suppress the influence of gradient magnitude, ensuring more stable updates. This resulting noise  $\epsilon^*$  encodes object-related information that tends to reconstruct the original content, thereby serving as a challenging adversarial noise. Meanwhile, the formulation in Equation 11 preserves the approximate distributional properties of standard Gaussian noise, making  $\epsilon^*$  compatible with the diffusion process.

### 3.3.2 Optimize for Robustness to “Bad” Noise

In Stage 2, we enhance the robustness of the model by fine-tuning it on adversarial noise samples. We minimize the following objective,

$$\min_{\theta} \mathbb{E}_{t, \mathbf{z}_t^*} \|\mathbf{u}_\theta(\mathbf{z}_t^*, \mathbf{z}_m, \bar{\mathbf{m}}, t) - \mathbf{v}^*\|^2, \quad \text{where } \mathbf{v}^* = \epsilon^* - \mathbf{z}_{\text{succ}} \text{ and } \mathbf{z}_t^* = t\epsilon^* + (1 - t)\mathbf{z}_{\text{succ}}, \quad (12)$$

$\mathbf{z}_{\text{succ}}$  is the latent for a successful inpainted video. In Equation 12, we sample a timestep  $t$ , and construct a noisy latent input  $\mathbf{z}_t^*$  according to the previously generated  $\epsilon^*$  and  $\mathbf{z}_{\text{succ}}$ . In practice, we train on a mixture of data. Specifically, one-third of training samples are drawn from our curated 10K set with their associated adversarial noises, while the remaining two-thirds are standard WebVid-10M videos with randomly generated object masks. This mixed strategy ensures the model remains effective on both clean and challenging inputs, ultimately leading to improved generalization and resilience against failure cases. We refer to the model after Stage 2 training as MiniMax-Remover.

### 3.3.3 Advantages of MiniMax-Remover

MiniMax-Remover owns several key advantages:

- • **Low Training Overhead.** It only back-propagates once to search the “bad” noise, and trains a remover with simplified architectures which reduces the memory consumption.
- • **Fast Inference Speed.** MiniMax-Remover only uses as few as 6 sampling steps without CFG, resulting in significantly faster inference compared to prior methods.
- • **High Quality.** Since the model is trained to be robust against “bad” noises, it rarely produces unexpected objects or visual artifacts in the masked regions, resulting in a higher quality.

## 4 Experiments

**Training Dataset.** In Stage 1, we use Grounded-SAM2 [28, 41] and captions from CogVLM2 [18] to generate masks on the watermark-free WebVid-10M dataset [1]. Approximately 2.5M video-mask pairs are randomly selected for training. In Stage 2, we collect 17K videos from Pexels [38] and apply the same annotation process as in Stage 1. These are further processed using the model from Stage 1, and 10K videos are manually selected for Stage 2 training.

**Training Details.** For Stage 1, we initialize our model with Wan2.1-1.3B [43]. Newly added layers, such as the embedding layer, are randomly initialized. The first 16 channels of the patch embedder arecopied from Wan2.1, while the remaining 32 are zero-initialized. Training uses a batch size of 128, input frame length of 81, and resolutions randomly sampled from  $336 \times 592$  to  $720 \times 1280$ . We set the first N mask frames to 0 to support the any-length inpainting by applying sliding windows, using a random ratio of 0.1. We use AdamW optimizer[31] with a constant learning rate of  $1e-5$ , weight decay of  $1e-4$ , and train for 10K steps. In Stage 2, we reuse the model from Stage 1, excluding the embedding layer since no external conditions are needed. One-third of the training iterations apply min-max optimization; the rest follow standard training using unrelated masks from WebVid[1]. Hyperparameters remain the same as in Stage 1. All experiments are conducted on 8 A800 GPUs (80GB each) and take about two days in total.

**Inference Details.** We perform inference using RTX 4090 GPUs. With an input resolution of 480p and a frame length of 81, *the inference takes approximately 24 seconds per video* and consumes around 14GB peak GPU memory(DiT for 8GB, VAE decoding for 6GB), using 6 sampling steps.

**Baselines.** We compare our method with Propainter [54], VideoComposer [46], COCOCO [56], FloED [14], DiffuEraser [24], VideoPainter [2] and VACE [20]. We set the evaluate frame length as 32. To evaluate with same frame length, we expand input frame length for VideoComposer [46] and FloED [14]. The rest video inpainters are used their default frame length of their code bases. The frame resolutions are used with their default resolutions.

**Metrics.** We evaluate background preservation using SSIM and PSNR. TC evaluates the temporal consistency, follows COCOCO [56] and AVID[53] with CLIP-ViT-h-b14 [40] to compute features. GPT-O3 [35] serve as objective metrics. We evaluate these metrics on DAVIS datasets and 200 randomly selected Pexels videos to show generalizations across different datasets. Note that the 200 Pexels videos are not contained in our training datasets, and masks are extracted by Grounded-SAM2. In the user study, participants are presented with a multiple-choice questionnaire to identify which video most effectively removed the target objects from the original video, without introducing blurring, visual artifacts, or hallucinated content within the masked areas.

Table 2: Comparison of different methods on the DAVIS [39] and Pexels [38] datasets. The best results are highlighted in **bold**. “TC” denotes temporal consistency, “VQ” stands for visual quality, and “Succ” represents the success rate.

<table border="1">
<thead>
<tr>
<th rowspan="3">Method</th>
<th colspan="6">DAVIS Dataset</th>
<th colspan="6">Pexels Dataset</th>
</tr>
<tr>
<th colspan="3">Quantitative Results</th>
<th colspan="2">GPT-O3 Eval</th>
<th rowspan="2">User Preference</th>
<th colspan="3">Quantitative Results</th>
<th colspan="2">GPT-O3 Eval</th>
<th rowspan="2">User Preference</th>
</tr>
<tr>
<th>SSIM</th>
<th>PSNR</th>
<th>TC</th>
<th>VQ</th>
<th>Succ</th>
<th>SSIM</th>
<th>PSNR</th>
<th>TC</th>
<th>VQ</th>
<th>Succ</th>
</tr>
</thead>
<tbody>
<tr>
<td>Propainter [54]</td>
<td>0.9748</td>
<td>35.33</td>
<td>0.9769</td>
<td>5.68</td>
<td>56.67</td>
<td>34.55%</td>
<td>0.9746</td>
<td>35.76</td>
<td>0.9813</td>
<td>5.07</td>
<td>35.5</td>
<td>23.28%</td>
</tr>
<tr>
<td>VideoComp [46]</td>
<td>0.8689</td>
<td>30.66</td>
<td>0.9529</td>
<td>2.12</td>
<td>7.78</td>
<td>0.25%</td>
<td>0.8865</td>
<td>30.26</td>
<td>0.9573</td>
<td>3.10</td>
<td>14.5</td>
<td>0.245%</td>
</tr>
<tr>
<td>COCOCO [56]</td>
<td>0.8863</td>
<td>32.10</td>
<td>0.9511</td>
<td>3.40</td>
<td>12.22</td>
<td>1.96%</td>
<td>0.9145</td>
<td>30.84</td>
<td>0.9693</td>
<td>4.32</td>
<td>30.0</td>
<td>0.245%</td>
</tr>
<tr>
<td>FloED [14]</td>
<td>0.9053</td>
<td>32.02</td>
<td>0.9630</td>
<td>5.13</td>
<td>45.56</td>
<td>10.54%</td>
<td>0.9350</td>
<td>34.82</td>
<td>0.9688</td>
<td>4.19</td>
<td>24.5</td>
<td>12.01%</td>
</tr>
<tr>
<td>DiffuEraser [24]</td>
<td>0.9818</td>
<td>34.42</td>
<td>0.9767</td>
<td>5.71</td>
<td>56.67</td>
<td>42.40%</td>
<td>0.9859</td>
<td>34.41</td>
<td>0.9800</td>
<td>5.89</td>
<td>59.0</td>
<td>20.83%</td>
</tr>
<tr>
<td>VideoPainter [2]</td>
<td>0.9654</td>
<td>34.60</td>
<td>0.9620</td>
<td>3.80</td>
<td>17.98</td>
<td>1.47%</td>
<td>0.9821</td>
<td>36.49</td>
<td>0.9847</td>
<td>5.68</td>
<td>48.0</td>
<td>7.11%</td>
</tr>
<tr>
<td>VACE [20]</td>
<td>0.9102</td>
<td>31.92</td>
<td>0.9747</td>
<td>3.12</td>
<td>8.89</td>
<td>2.21%</td>
<td>0.9102</td>
<td>32.33</td>
<td>0.9898</td>
<td>6.27</td>
<td>49.5</td>
<td>23.77%</td>
</tr>
<tr>
<td>Ours (6 steps)</td>
<td>0.9842</td>
<td>36.56</td>
<td>0.9770</td>
<td>6.26</td>
<td>82.22</td>
<td>58.08%</td>
<td>0.9873</td>
<td>36.98</td>
<td>0.9905</td>
<td>6.87</td>
<td>76.5</td>
<td>62.01%</td>
</tr>
<tr>
<td>Ours (12 steps)</td>
<td>0.9846</td>
<td>36.62</td>
<td>0.9772</td>
<td>6.36</td>
<td>84.44</td>
<td>63.24%</td>
<td>0.9872</td>
<td><b>37.02</b></td>
<td><b>0.9906</b></td>
<td>6.86</td>
<td>80.5</td>
<td><b>67.15%</b></td>
</tr>
<tr>
<td>Ours (50 steps)</td>
<td><b>0.9847</b></td>
<td><b>36.66</b></td>
<td><b>0.9776</b></td>
<td><b>6.48</b></td>
<td><b>91.11</b></td>
<td><b>64.22%</b></td>
<td><b>0.9878</b></td>
<td>36.98</td>
<td>0.9905</td>
<td><b>6.90</b></td>
<td><b>81.0</b></td>
<td>63.97%</td>
</tr>
</tbody>
</table>

#### 4.1 Quantitative Comparison

As show in Table 2, our method outperforms previous baselines on all 90 DAVIS videos, achieving an SSIM of 0.9847 and a PSNR of 36.66. Notably, even with only 6 sampling steps, our approach can generate high-quality videos while effectively preserving background details. Furthermore, our method exhibits superior temporal consistency, significantly outperforming generative models such as VACE [20], and even surpassing the traditional inpainting method Propainter [54]. These results demonstrate that our model consistently produces visually pleasing and high-quality video object removal. A similar trend is observed on 200 Pexels videos, where our method achieves the highest SSIM, PSNR, and temporal consistency scores. Moreover, reducing the number of sampling steps does not significantly degrade the removal performance.Figure 4: The visual results of our object remover. The video on the left depicts the original video, while the video on the right displays the edited videos. *Best viewed with Acrobat Reader. Click the images to play the animation clips.*

## 4.2 Qualitative Results

To assess the visual quality and object removal success rate, we utilize GPT-O3 [35], a powerful reasoning large language model, by querying it with evaluation prompts. The quality score ranges from 1 (worst) to 10 (best). According to GPT-O3 evaluation, our method achieves a higher score of 6.48, compared to 5.71 from the best previous method, indicating clearer and more visually appealing removal results. Regarding removal success rate, we prompt the GPT-O3 to determine whether the target objects were effectively removed. Our method achieves a remarkable 91.11% success rate on the DAVIS dataset, far surpassing the previous best of 56.67%. On the Pexels dataset, our method also outperforms previous state-of-the-art approaches, with an 81% success rate compared to 59.0%. Additionally, our method achieves a higher score 6.90, versus 6.27 from prior best methods. For the user preference, it has similar trends, our method achieves the best score on both two datasets compared with previous best remover, 64% vs 42.40% and 67.15% vs 23.77%, respectively.

Table 3: Ablation Study for two stages’ training. The best results are **boldfaced**.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th rowspan="2">Stage</th>
<th rowspan="2">Structure</th>
<th rowspan="2">Condition</th>
<th colspan="3">•Quantitative Results</th>
<th colspan="2">•GPT-O3 Evaluation</th>
</tr>
<tr>
<th>SSIM</th>
<th>PSNR</th>
<th>TC</th>
<th>Visual Quality</th>
<th>Success Rate</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ab-1</td>
<td>Stage 1</td>
<td>ShiftTable+Cross-Attn</td>
<td>Prompt</td>
<td>0.9737</td>
<td>34.77</td>
<td>0.9756</td>
<td>6.27</td>
<td>51.11</td>
</tr>
<tr>
<td>Ab-2</td>
<td>Stage 1</td>
<td>ShiftTable+Cross-Attn</td>
<td>Tokens</td>
<td>0.9747</td>
<td>35.09</td>
<td>0.9752</td>
<td>6.37</td>
<td>56.67</td>
</tr>
<tr>
<td>Ab-3</td>
<td>Stage 1</td>
<td>ShiftTable</td>
<td>Tokens</td>
<td>0.9682</td>
<td>34.87</td>
<td>0.9743</td>
<td>6.42</td>
<td>53.33</td>
</tr>
<tr>
<td>Ab-4</td>
<td>Stage 1</td>
<td>ShiftTable+Self-Attn</td>
<td>Tokens</td>
<td><b>0.9798</b></td>
<td><b>35.87</b></td>
<td><b>0.9773</b></td>
<td><b>6.39</b></td>
<td><b>71.11</b></td>
</tr>
<tr>
<th>Method</th>
<th>Stage</th>
<th>Data Type</th>
<th>Input Noise</th>
<th colspan="3">•Quantitative Results</th>
<th colspan="2">•GPT-O3 Evaluation</th>
</tr>
<tr>
<th></th>
<th></th>
<th></th>
<th></th>
<th>SSIM</th>
<th>PSNR</th>
<th>TC</th>
<th>Visual Quality</th>
<th>Success Rate</th>
</tr>
<tr>
<td>Ab-1</td>
<td>Stage 2</td>
<td>WebVid Data</td>
<td>Random Noise</td>
<td>0.9781</td>
<td>35.49</td>
<td>0.9759</td>
<td>6.27</td>
<td>65.56</td>
</tr>
<tr>
<td>Ab-2</td>
<td>Stage 2</td>
<td>Human Data</td>
<td>Random Noise</td>
<td>0.9796</td>
<td>35.21</td>
<td>0.9772</td>
<td>6.36</td>
<td>72.22</td>
</tr>
<tr>
<td>Ab-3</td>
<td>Stage 2</td>
<td>Human Data</td>
<td>Bad Noise-Adv</td>
<td><b>0.9847</b></td>
<td><b>36.66</b></td>
<td><b>0.9776</b></td>
<td><b>6.48</b></td>
<td><b>91.11</b></td>
</tr>
</tbody>
</table>

## 4.3 Ablation Study

To understand the impact of each component and modification in our method, we conduct a step-by-step ablation study. All experiments use 50 sampling steps.**Stage 1.** We begin by examining the role of the text encoder and prompt-based conditioning. In the comparison between Ab-1 and Ab-2 (Table 3), we replace the text encoder and prompts with learnable contrastive tokens. The results show no significant drop in performance, indicating that the text encoder is redundant for the removal task when suitable learnable tokens are used instead. Next, comparing Ab-2 and Ab-3, we observe a slight performance degradation after removing the cross-attention module from the DiT. However, when we introduce learnable contrastive condition tokens into the self-attention layers (Ab-4), the results not only recover but also surpass that of Ab-1. This demonstrates the effectiveness of our simplified DiT architecture.

**Stage 2.** We compare models trained with and without human-annotated data. The results (Ab-1 vs. Ab-2) show that using manually labeled data alone does not significantly improve performance, likely due to the limited size (10K videos) and diversity of the dataset, which hinders generalization. Furthermore, we compare different noise types used during training (Ab-2 to Ab-3). We find that adding “bad noise” (artificially degraded inputs) into training helps improve performance significantly.

## 5 Conclusion

In this paper, we propose *MiniMax Remover*, a two-stage framework for object removal in videos. In Stage 1, we simplify the pretrained DiT by removing cross-attention and replacing prompt embeddings with contrastive condition tokens. In Stage 2, we apply min-max optimization: the *max* step searches for challenging noise inputs that lead to failure cases, while the *min* step trains the model to successfully reconstruct the target from these adversarial inputs. Through this two-stage training, our method achieves cleaner and more visually pleasing removal results. Since it requires no classifier-free guidance (CFG) and uses only 6 sampling steps, inference is significantly faster. Extensive experiments demonstrate that our model delivers impressive removal performance across multiple benchmarks.

## References

- [1] Max Bain, Arsha Nagrani, Gül Varol, and Andrew Zisserman. Frozen in time: A joint video and image encoder for end-to-end retrieval. In *Proceedings of the IEEE/CVF International Conference on Computer Vision*, pages 1728–1738, 2021.
- [2] Yuxuan Bian, Zhaoyang Zhang, Xuan Ju, Mingdeng Cao, Liangbin Xie, Ying Shan, and Qiang Xu. Videopainter: Any-length video inpainting and editing with plug-and-play context control. *arXiv preprint arXiv:2503.05639*, 2025.
- [3] Black Forest Labs. Black forest labs. <https://github.com/black-forest-labs/flux/>, 2024.
- [4] Andreas Blattmann, Robin Rombach, Huan Ling, Tim Dockhorn, Seung Wook Kim, Sanja Fidler, and Karsten Kreis. Align your latents: High-resolution video synthesis with latent diffusion models. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 22563–22575, 2023.
- [5] Stephen P Boyd and Lieven Vandenberghe. *Convex optimization*. Cambridge university press, 2004.
- [6] Tim Brooks, Aleksander Holynski, and Alexei A Efros. Instructpix2pix: Learning to follow image editing instructions. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 18392–18402, 2023.
- [7] Haoxin Chen, Yong Zhang, Xiaodong Cun, Menghan Xia, Xintao Wang, Chao Weng, and Ying Shan. Videocrafter2: Overcoming data limitations for high-quality video diffusion models. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, 2024.
- [8] Jiaxin Cheng, Tianjun Xiao, and Tong He. Consistent video-to-video transfer using synthetic dataset. In *The Twelfth International Conference on Learning Representations*, 2024.
- [9] Yuren Cong, Mengmeng Xu, Christian Simon, Shoufa Chen, Jiawei Ren, Yanping Xie, Juan-Manuel Perez-Rua, Bodo Rosenhahn, Tao Xiang, and Sen He. Flatten: optical flow-guided attention for consistent text-to-video editing. *arXiv preprint arXiv:2310.05922*, 2023.- [10] Gen-3. Introducing gen-3 alpha: A new frontier for video generation. <https://runwayml.com/research/introducing-gen-3-alpha/>, 2024.
- [11] Zigang Geng, Binxin Yang, Tiankai Hang, Chen Li, Shuyang Gu, Ting Zhang, Jianmin Bao, Zheng Zhang, Houqiang Li, Han Hu, et al. Instructdiffusion: A generalist modeling interface for vision tasks. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 12709–12720, 2024.
- [12] Michal Geyer, Omer Bar-Tal, Shai Bagon, and Tali Dekel. Tokenflow: Consistent diffusion features for consistent video editing. *arXiv preprint arXiv:2307.10373*, 2023.
- [13] Ian J Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing Xu, David Warde-Farley, Sherjil Ozair, Aaron Courville, and Yoshua Bengio. Generative adversarial nets. *Advances in neural information processing systems*, 27, 2014.
- [14] Bohai Gu, Hao Luo, Song Guo, and Peiran Dong. Advanced video inpainting using optical flow-guided efficient diffusion. *arXiv preprint arXiv:2412.00857*, 2024.
- [15] Yuwei Guo, Ceyuan Yang, Anyi Rao, Yaohui Wang, Yu Qiao, Dahua Lin, and Bo Dai. Animatediff: Animate your personalized text-to-image diffusion models without specific tuning. *arXiv preprint arXiv:2307.04725*, 2023.
- [16] Yoav HaCohen, Nisan Chiprut, Benny Brazowski, Daniel Shalem, Dudu Moshe, Eitan Richardson, Eran Levin, Guy Shiran, Nir Zabari, Ori Gordon, Poriya Panet, Sapir Weissbuch, Victor Kulikov, Yaki Bitterman, Zeev Melumian, and Ofir Bibi. Ltx-video: Realtime video latent diffusion. *arXiv preprint arXiv:2501.00103*, 2024.
- [17] Jonathan Ho and Tim Salimans. Classifier-free diffusion guidance. *arXiv preprint arXiv:2207.12598*, 2022.
- [18] Wenyi Hong, Weihan Wang, Ming Ding, Wenmeng Yu, Qingsong Lv, Yan Wang, Yean Cheng, Shiyu Huang, Junhui Ji, Zhao Xue, et al. Cogvlm2: Visual language models for image and video understanding. *arXiv preprint arXiv:2408.16500*, 2024.
- [19] Jiahao Hu, Tianxiong Zhong, Xuebo Wang, Boyuan Jiang, Xingye Tian, Fei Yang, Pengfei Wan, and Di Zhang. Vivid-10m: A dataset and baseline for versatile and interactive video local editing. *arXiv preprint arXiv:2411.15260*, 2024.
- [20] Zeyinzi Jiang, Zhen Han, Chaojie Mao, Jingfeng Zhang, Yulin Pan, and Yu Liu. Vace: All-in-one video creation and editing. *arXiv preprint arXiv:2503.07598*, 2025.
- [21] Weijie Kong, Qi Tian, Zijian Zhang, Rox Min, Zuozhuo Dai, Jin Zhou, Jiangfeng Xiong, Xin Li, Bo Wu, Jianwei Zhang, et al. Hunyuanvideo: A systematic framework for large video generative models. *arXiv preprint arXiv:2412.03603*, 2024.
- [22] Max Ku, Cong Wei, Weiming Ren, Huan Yang, and Wenhui Chen. Anyv2v: A plug-and-play framework for any video-to-video editing tasks. *arXiv preprint arXiv:2403.14468*, 2024.
- [23] Minhyeok Lee, Suhwan Cho, Chajin Shin, Jungho Lee, Sunghun Yang, and Sangyoun Lee. Video diffusion models are strong video inpainter. In *Proceedings of the AAAI Conference on Artificial Intelligence*, volume 39, pages 4526–4533, 2025.
- [24] Xiaowen Li, Haolan Xue, Peiran Ren, and Liefeng Bo. Diffueraser: A diffusion model for video inpainting. *arXiv preprint arXiv:2501.10018*, 2025.
- [25] Chang Liu, Rui Li, Kaidong Zhang, Yunwei Lan, and Dong Liu. Stablev2v: Stabilizing shape consistency in video-to-video editing. *arXiv preprint arXiv:2411.11045*, 2024.
- [26] Shaoteng Liu, Tianyu Wang, Jui-Hsien Wang, Qing Liu, Zhifei Zhang, Joon-Young Lee, Yijun Li, Bei Yu, Zhe Lin, Soo Ye Kim, et al. Generative video propagation. *arXiv preprint arXiv:2412.19761*, 2024.
- [27] Shaoteng Liu, Yuechen Zhang, Wenbo Li, Zhe Lin, and Jiaya Jia. Video-p2p: Video editing with cross-attention control. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 8599–8608, 2024.- [28] Shilong Liu, Zhaoyang Zeng, Tianhe Ren, Feng Li, Hao Zhang, Jie Yang, Chunyuan Li, Jianwei Yang, Hang Su, Jun Zhu, et al. Grounding dino: Marrying dino with grounded pre-training for open-set object detection. *arXiv preprint arXiv:2303.05499*, 2023.
- [29] Shiyu Liu, Yucheng Han, Peng Xing, Fukun Yin, Rui Wang, Wei Cheng, Jiaqi Liao, Yingming Wang, Honghao Fu, Chunrui Han, Guopeng Li, Yuang Peng, Quan Sun, Jingwei Wu, Yan Cai, Zheng Ge, Ranchen Ming, Lei Xia, Xianfang Zeng, Yibo Zhu, Binxing Jiao, Xiangyu Zhang, Gang Yu, and Daxin Jiang. Step1x-edit: A practical framework for general image editing. *arXiv preprint arXiv:2504.17761*, 2025.
- [30] Xingchao Liu, Chengyue Gong, and Qiang Liu. Flow straight and fast: Learning to generate and transfer data with rectified flow. *arXiv preprint arXiv:2209.03003*, 2022.
- [31] Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. *arXiv preprint arXiv:1711.05101*, 2017.
- [32] Guoqing Ma, Haoyang Huang, Kun Yan, Liangyu Chen, Nan Duan, Shengming Yin, Changyi Wan, Ranchen Ming, Xiaoniu Song, Xing Chen, et al. Step-video-t2v technical report: The practice, challenges, and future of video foundation model. *arXiv preprint arXiv:2502.10248*, 2025.
- [33] Mochi-1. Mochi-1. <https://www.genmo.ai/blog>, 2024.
- [34] Chong Mou, Mingdeng Cao, Xintao Wang, Zhaoyang Zhang, Ying Shan, and Jian Zhang. Revideo: Remake a video with motion and content control. *arXiv preprint arXiv:2405.13865*, 2024.
- [35] Introducing OpenAI o3 and o4 mini. <https://openai.com/index/introducing-o3-and-o4-mini/>, 2025.
- [36] OpenAI. Sora: Creating video from text. <https://openai.com/index/sora/>, 2024.
- [37] William Peebles and Saining Xie. Scalable diffusion models with transformers. *arXiv preprint arXiv:2212.09748*, 2022.
- [38] Pexels. <https://www.pexels.com/>, 2024.
- [39] Jordi Pont-Tuset, Federico Perazzi, Sergi Caelles, Pablo Arbeláez, Alex Sorkine-Hornung, and Luc Van Gool. The 2017 davis challenge on video object segmentation. *arXiv preprint arXiv:1704.00675*, 2017.
- [40] Aditya Ramesh, Mikhail Pavlov, Gabriel Goh, Scott Gray, Chelsea Voss, Alec Radford, Mark Chen, and Ilya Sutskever. Zero-shot text-to-image generation. In *International Conference on Machine Learning*, pages 8821–8831. PMLR, 2021.
- [41] Nikhila Ravi, Valentin Gabeur, Yuan-Ting Hu, Ronghang Hu, Chaitanya Ryali, Tengyu Ma, Haitham Khedr, Roman Rädle, Chloe Rolland, Laura Gustafson, Eric Mintun, Junting Pan, Kalyan Vasudev Alwala, Nicolas Carion, Chao-Yuan Wu, Ross Girshick, Piotr Dollár, and Christoph Feichtenhofer. Sam 2: Segment anything in images and videos. *arXiv preprint arXiv:2408.00714*, 2024.
- [42] Olaf Ronneberger, Philipp Fischer, and Thomas Brox. U-net: Convolutional networks for biomedical image segmentation. In *Medical Image Computing and Computer-Assisted Intervention—MICCAI 2015: 18th International Conference, Munich, Germany, October 5-9, 2015, Proceedings, Part III 18*, pages 234–241. Springer, 2015.
- [43] Ang Wang, Baole Ai, Bin Wen, Chaojie Mao, Chen-Wei Xie, Di Chen, Feiwu Yu, Haiming Zhao, Jianxiao Yang, Jianyuan Zeng, Jiayu Wang, Jingfeng Zhang, Jingren Zhou, Jinkai Wang, Jixuan Chen, Kai Zhu, Kang Zhao, Keyu Yan, Lianghua Huang, Mengyang Feng, Ningyi Zhang, Pandeng Li, Pingyu Wu, Ruihang Chu, Ruili Feng, Shiwei Zhang, Siyang Sun, Tao Fang, Tianxing Wang, Tianyi Gui, Tingyu Weng, Tong Shen, Wei Lin, Wei Wang, Wei Wang, Wenmeng Zhou, Wente Wang, Wenting Shen, Wenyuan Yu, Xianzhong Shi, Xiaoming Huang, Xin Xu, Yan Kou, Yangyu Lv, Yifei Li, Yijing Liu, Yiming Wang, Yingya Zhang, Yitong Huang,Yong Li, You Wu, Yu Liu, Yulin Pan, Yun Zheng, Yuntao Hong, Yupeng Shi, Yutong Feng, Zeyinzi Jiang, Zhen Han, Zhi-Fan Wu, and Ziyu Liu. Wan: Open and advanced large-scale video generative models. *arXiv preprint arXiv:2503.20314*, 2025.

[44] Jiuniu Wang, Hangjie Yuan, Dayou Chen, Yingya Zhang, Xiang Wang, and Shiwei Zhang. Modelscope text-to-video technical report, 2023.

[45] Su Wang, Chitwan Saharia, Ceslee Montgomery, Jordi Pont-Tuset, Shai Noy, Stefano Pellegrini, Yasumasa Onoe, Sarah Laszlo, David J Fleet, Radu Soricut, et al. Imagen editor and editbench: Advancing and evaluating text-guided image inpainting. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 18359–18369, 2023.

[46] Xiang Wang, Hangjie Yuan, Shiwei Zhang, Dayou Chen, Jiuniu Wang, Yingya Zhang, Yujun Shen, Deli Zhao, and Jingren Zhou. Videocomposer: Compositional video synthesis with motion controllability. *Advances in Neural Information Processing Systems*, 2024.

[47] Jay Zhangjie Wu, Yixiao Ge, Xintao Wang, Stan Weixian Lei, Yuchao Gu, Yufei Shi, Wynne Hsu, Ying Shan, Xiaohu Qie, and Mike Zheng Shou. Tune-a-video: One-shot tuning of image diffusion models for text-to-video generation. In *Proceedings of the IEEE/CVF International Conference on Computer Vision*, pages 7623–7633, 2023.

[48] Shiyuan Yang, Zheng Gu, Liang Hou, Xin Tao, Pengfei Wan, Xiaodong Chen, and Jing Liao. Mtv-inpaint: Multi-task long video inpainting. *arXiv preprint arXiv:2503.11412*, 2025.

[49] Zhuoyi Yang, Jiayan Teng, Wendi Zheng, Ming Ding, Shiyu Huang, JiaZheng Xu, Yuanming Yang, Xiaohan Zhang, Xiaotao Gu, Guanyu Feng, Da Yin, Wenyi Hong, Weihan Wang, Yeon Cheng, Yuxuan Zhang, Ting Liu, Bin Xu, Yuxiao Dong, and Jie Tang. Cogvideox: Text-to-video diffusion models with an expert transformer. 2024.

[50] Kai Zhang, Lingbo Mo, Wenhui Chen, Huan Sun, and Yu Su. Magicbrush: A manually annotated dataset for instruction-guided image editing. *Advances in Neural Information Processing Systems*, 36, 2024.

[51] Lvmin Zhang and Maneesh Agrawala. Packing input frame context in next-frame prediction models for video generation. *arXiv preprint arXiv:2504.12626*, 2025.

[52] Lvmin Zhang, Anyi Rao, and Maneesh Agrawala. Adding conditional control to text-to-image diffusion models. In *Proceedings of the IEEE/CVF International Conference on Computer Vision*, pages 3836–3847, 2023.

[53] Zhixing Zhang, Bichen Wu, Xiaoyan Wang, Yaqiao Luo, Luxin Zhang, Yinan Zhao, Peter Vajda, Dimitris Metaxas, and Licheng Yu. Avid: Any-length video inpainting with diffusion model. *arXiv preprint arXiv:2312.03816*, 2023.

[54] Shangchen Zhou, Chongyi Li, Kelvin CK Chan, and Chen Change Loy. Propainter: Improving propagation and transformer for video inpainting. In *Proceedings of the IEEE/CVF International Conference on Computer Vision*, 2023.

[55] Bojia Zi, Penghui Ruan, Marco Chen, Xianbiao Qi, Shaozhe Hao, Shihao Zhao, Youze Huang, Bin Liang, Rong Xiao, and Kam-Fai Wong. Senorita-2m: A high-quality instruction-based dataset for general video editing by video specialists. *arXiv preprint arXiv:2502.06734*, 2025.

[56] Bojia Zi, Shihao Zhao, Xianbiao Qi, Jianan Wang, Yukai Shi, Qianyu Chen, Bin Liang, Kam-Fai Wong, and Lei Zhang. Cococo: Improving text-guided video inpainting for better consistency, controllability and compatibility. *arXiv preprint arXiv:2403.12035*, 2024.## 6 Related Work

Video diffusion models have witnessed remarkable progress in recent years [46, 44, 15, 7, 36, 49, 32, 21, 16, 51, 43], accompanied by the emergence of various video editing techniques [26, 47, 52, 25, 34, 9, 12, 22, 8, 55]. Among these techniques, video inpainting plays a crucial role by enabling the regeneration of content in corrupted or missing regions [46, 56, 2, 20, 48, 55, 19, 53, 54, 14, 24, 55, 23]. Generally, video inpainting tasks can be categorized into two main types: one focuses on generating or editing objects within specified regions with prompts, while the other aims to remove objects based on provided masks.

**Text-guided Video Inpainting.** For the first type of video inpainting, which involves generating or editing content within a masked region, significant progress has been made in recent years. VideoComposer [46] is the first diffusion model capable of performing text-guided video inpainting. It supports multiple conditioning inputs and can handle various tasks within a unified framework. AVID [53] proposed a method for text-guided video inpainting of arbitrary-length sequences using natural language prompts. COCOCO [56] improves consistency and controllability through damped global attention and enhanced cross-attention to text. VIVID [19] introduces a large-scale dataset with 10M image and video samples for localized editing, enabling training of a powerful text-guided inpainter. MTV-Inpaint [48] is capable of handling both traditional scene completion and novel object insertion. VideoPainter [2] performs inpainting using a DiT-based architecture, incorporating an efficient context encoder to process masked inputs and injecting backbone-aware background information into a pre-trained video DiT for plug-and-play consistent video inpainting.

**Video Object Removal.** In contrast to text-guided inpainting, some methods focus specifically on removing objects from videos. ProPainter [54] uses optical flow to first complete the motion in masked regions, then synthesizes inpainted content accordingly. FFF-VDI [23] propagates noise latents from future frames to fill masked areas in the initial latent space, then finetunes a pre-trained image-to-video diffusion model for final synthesis. FloED [14] integrates both optical flow and text prompts, injecting embeddings from both modalities into the inpainting model for object removal. DiffuEraser [24] combines a flow-guided inpainting model with DDIM inversion for improved inpainting fidelity. Senorita-Remover, proposed in [55], introduces instruction-based object removal, using positive prompts to guide removal and negative prompts to suppress unintended object generation in masked areas.

**Remark.** Compared with previous methods, our **MiniMax-Remover** does not rely on additional prior or prompts. It offers fast inference speed with only 6 sampling steps, no CFG. Despite its simplicity, it achieves a higher object removal success rate and prevent hallucinated object and artifacts generation.

## 7 More Details of Stage-1 Training

Here, we provide further details on the training process of Stage 1. We adopt the same mask selection strategy as in Senorita-Remover [55]. In this paper, we propose to simplify the pretrained DiT architecture and replace the prompts with learnable contrastive condition tokens.

The most challenging issue in object removal is the undesired regeneration problem, where the model tends to regenerate objects in the masked region that share a similar shape to the mask itself. To address this issue, as illustrated in Figure 5, we introduce contrastive condition tokens: a positive token  $c^+$  to guide the model towards object removal, and a negative token  $c^-$  to guide object generation within the masked region. This allows the model to leverage CFG for effective object removal while preventing the reappearance of similar objects in the masked areas.

In Figure 5(a), when selecting masks, we randomly select masks from other unrelated videos, and paste the masks into the input video. These masks are designed to differ in shape from the actual objects within the masked region of the input video. As a result, the model, trained on such data, tends to generate content that differs from the mask shape during inference. This process is considered as the positive condition  $c^+$ . The position condition learns to remove the masked objects.

In Figure 5(b), we incorporate training samples using their corresponding precise masks. In these cases, the masked region contains an object whose shape closely matches the mask. Training on such data encourages the model to regenerate similar objects in the masked region when conditioned on  $c^-$ . This contrastive training strategy helps the model distinguish between removal and generation tasksmore effectively. This process is considered as the negative condition  $c^-$ . The negative condition learns to generate the masked objects.

The diagram illustrates the training framework of the Stage-1, divided into two parts: (a) Learn Removal and (b) Learn Generation.

**(a) Learn Removal:** A video is processed to create a 'Masked Video' and an 'Unrelated Mask' (randomly selected). The 'Masked Video' is used as the positive condition  $c^+$  for the 'Simplified DiT' model. The model consists of  $\times N$  stages, each containing a 'Patchify' layer, a 'DiT Block', a 'Norm' layer, and a 'Linear and Reshape' layer. The output is a 'Removal Pred' which is compared with a 'Target' using an 'MSE Loss'. The masked area **doesn't contain** same shaped objects.

**(b) Learn Generation:** A video is processed to create a 'Masked Video' and a 'Precise Mask' (generated by SAM2). The 'Masked Video' is used as the negative condition  $c^-$  for the 'Simplified DiT' model. The model's output is a 'Gen Pred' which is compared with a 'Target' using an 'MSE Loss'. The masked area **contains** same shaped objects.

Figure 5: Training framework of the Stage-1. (a) denotes the positive condition process, and the position condition learns to remove the masked objects. and (b) represents the negative process, and the negative condition learns to generate the masked objects..

## 8 Explanation Of Why CFG Can Be Discarded

### 8.1 MiniMax Optimization

In our work, we formulate the min-max remover using the following objective:

$$\min_{\theta} \max_{\epsilon^*} \|\mathbf{u}_{\theta}(\epsilon^*, z_m, \bar{m}) - z^*\|^2, \quad (13)$$

where  $\mathbf{u}$  is a DiT network parameterized by  $\theta$ , and  $\mathbf{v}^* = \epsilon^* - z_{\text{succ}}$ , with  $z_{\text{succ}} = \mathcal{E}(\mathbf{x}_{\text{succ}})$ . Here,  $\mathbf{x}_{\text{succ}}$  is a video clip filtered and accepted by human annotators, and  $\mathcal{E}$  is the autoencoder.

In practice, to search for the “bad” noise, we replace the inner maximization with:

$$\min_{\epsilon^*} \|\mathbf{u}_{\theta}(\epsilon^*, z_m, \bar{m}) - \mathbf{v}^*\|^2, \quad (14)$$

where  $\mathbf{v}^* = \epsilon^* - z_{\text{org}}$ , and  $z_{\text{org}}$  corresponds to an undesired generation. This approach finds a noise  $\epsilon^*$  that causes  $\mathbf{u}_{\theta}$  to fail. By subsequently training  $\theta$  to minimize the objective even under such challenging noise, the model learns to produce outputs that deviate from the poor generation target  $\mathbf{v}^*$ .

### 8.2 Minimax Optimization Encourages Correct Removal and Discourages "Bad" Removal

**Minimax Optimization Encourages Correct Removal.** Based on the principles of minimax optimization discussed above, we have that:

$$\|\mathbf{u}_{\theta}(\epsilon, z_m, \bar{m}) - (\epsilon - z_{\text{succ}})\|^2 \leq \|\mathbf{u}_{\theta}(\epsilon^*, z_m, \bar{m}) - (\epsilon^* - z_{\text{succ}})\|^2. \quad (15)$$

This inequality implies that minimizing the loss on the "bad" input noise  $\epsilon^*$  leads to improved performance on the clean input noise  $\epsilon$ . Consequently, the model is incentivized to generate outputs that increasingly align with desired removals.**Minimax Optimization Discourages "Bad" Removals.** As shown in the formulation,

$$\min_{\theta} \|u_{\theta}(\epsilon^*, z_m, \bar{m}) - (\epsilon^* - z_{\text{succ}})\|^2,$$

the model is optimized to ensure that, upon convergence, no "bad" input noise  $\epsilon^*$  can lead to a failure-inducing removal. Consequently, the model inherently avoids generating such "bad" removals.

In summary, this min-max training strategy enables the model to avoid producing poor outputs (aligned with the Stage 1 negative condition  $c^-$ ) while encouraging alignment with high-quality generations (aligned with the Stage 1 positive condition  $c^+$ ). Therefore, after the minimax optimization, we can discard the classifier-free guidance (CFG), and the quality of removal results remains unaffected.

**Experiments.** Here, we conduct experiments to demonstrate that discarding CFG does not significantly affect performance. To ensure a fair comparison, we use the human-annotated data from Stage 2 and reuse the Stage 1 model without removing the tokens injected into the self-attention layer. Thus, the ablation variant *ab-I* applies CFG by introducing two learnable contrastive tokens,  $c^+$  and  $c^-$ . The sampling process consists of 50 steps, while all other training and inference settings remain consistent with those described in the main text. As shown in Table 4, using CFG leads to a slight improvement in background preservation and temporal consistency, but results in marginal decreases in visual quality and success rate. These results further support that the model performs robustly even without CFG.

Table 4: Comparison of results with/without CFG on the DAVIS [39] dataset. TC indicates Temporal Consistency, while Succ Rate stands for Success Rate. The best results are **boldfaced**.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th colspan="3">• Quantitative Results</th>
<th colspan="2">• GPT-O3 Evaluation</th>
</tr>
<tr>
<th>SSIM</th>
<th>PSNR</th>
<th>TC</th>
<th>Quality</th>
<th>Succ Rate</th>
</tr>
</thead>
<tbody>
<tr>
<td>MiniMax-Remover(w CFG)</td>
<td><b>0.9853</b></td>
<td><b>36.76</b></td>
<td><b>0.9778</b></td>
<td>6.45</td>
<td>90.00</td>
</tr>
<tr>
<td>MiniMax-Remover(w/o CFG)</td>
<td>0.9847</td>
<td>36.66</td>
<td>0.9776</td>
<td><b>6.48</b></td>
<td><b>91.11</b></td>
</tr>
</tbody>
</table>

## 9 Why Use Adversarial-Based Noise?

Table 5: Ablation study on different noise types using the DAVIS dataset [39]. TC denotes Temporal Consistency, and Succ Rate indicates Success Rate. The best results are highlighted in **bold**.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th rowspan="2">Input Noise</th>
<th colspan="3">• Quantitative Metrics</th>
<th colspan="2">• GPT-O3 Evaluation</th>
</tr>
<tr>
<th>SSIM</th>
<th>PSNR</th>
<th>TC</th>
<th>Quality</th>
<th>Succ Rate</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ablation Study-1</td>
<td>Random Noise</td>
<td>0.9796</td>
<td>35.21</td>
<td>0.9772</td>
<td>6.36</td>
<td>72.22</td>
</tr>
<tr>
<td>Ablation Study-2</td>
<td>Inversion-Based Noise</td>
<td>0.9797</td>
<td>35.80</td>
<td>0.9768</td>
<td>5.81</td>
<td>70.00</td>
</tr>
<tr>
<td>Ablation Study-3 (Ours)</td>
<td>Adversarial-Based Noise</td>
<td><b>0.9847</b></td>
<td><b>36.66</b></td>
<td><b>0.9776</b></td>
<td><b>6.48</b></td>
<td><b>91.11</b></td>
</tr>
</tbody>
</table>

### 9.1 Comparison of Adversarial-Based Noise with Other Types of Noise

It might seem intuitive to replace adversarial-based noise with either random or inversion-based noise. However, our experiments clearly justify the use of adversarial noise.

**Random noise** fails to guide the model towards adversarial directions. As a result, when training on limited data for a large number of iterations, it often leads to overfitting without improving model robustness or performance.

**Inversion-based noise**, on the other hand, typically requires many optimization steps to reconstruct noise from latent representations. To keep the computational cost comparable to adversarial noise, we restrict this process to just three steps. However, such shallow inversion retains a significant amount of information from the latents, violating the assumption that noise follows a standard Gaussian distribution  $\mathcal{N}(\mathbf{0}, \mathbf{I})$ . Consequently, it cannot be considered "random" noise in a true sense.Figure 6: Visual results of the Stage-1 Object Remover under inversion-based noises. The top row presents the original video, random noise, removal results, the corresponding histogram, and QQ plot. Rows 2 to 5 at the bottom display the removal results with inversion-based noise, the inversion-based noise itself, and its associated histogram and QQ plot, respectively. *Best viewed with Acrobat Reader. Click the images to play the animation clips.*

In contrast, **adversarial noise** is constructed by updating the input noise in a direction that maximizes model failure, while still keeping it within the  $\mathcal{N}(\mathbf{0}, \mathbf{I})$  distribution. Specifically, we apply the update rule:

$$\epsilon^* \leftarrow \sqrt{1 - \alpha} \epsilon - \sqrt{\alpha} \cdot \text{sign}(\nabla_{\epsilon}) \cdot |\epsilon'|$$

This allows us to craft noise that remains statistically valid but strategically challenging for the model.

As shown in Table 5, adversarial-based noise significantly outperforms both random and inversion-based noise across all evaluation metrics, demonstrating its effectiveness in improving model robustness and generalization.

## 9.2 Determining Whether the Noise is Gaussian

To assess whether the noise follows a Gaussian distribution, we typically use visual tools such as histograms and QQ-plots. The histogram provides an overview of the noise distribution, while the QQ-plot compares the quantiles of the observed noise with those of a standard Gaussian distribution. If the points in the QQ-plot lie approximately along a straight line, this suggests that the noise is likely Gaussian.

**Inversion-Based Noise is Non-Gaussian.** As shown in Figure 6, both the histogram and QQ-plot reveal a clear deviation from the characteristics of Gaussian noise. Inversion-based noise exhibits a distribution that significantly differs from that of random noise. These visualizations support the conclusion that inversion-based noise does not follow a Gaussian distribution and is therefore unsuitable for training purposes. Moreover, the visualizations suggest that inversion-based noiseFigure 7: Visual results of the Stage-1 Object Remover under adversarial-based noises. The top row illustrates the original video, random noise input, the resulting object removal output, along with the corresponding noise histogram and QQ plot. The lower section comprises the object removal results under adversarial-based noise (second row), the visualization of the adversarial noise (third row), and its associated histogram and QQ plot (fourth row). *Best viewed with Acrobat Reader. Click the images to play the animation clips.*

retains information from the original latent representations, further compromising its utility as pure noise. In addition, generating such noise requires multiple iterations of the inversion process, making it computationally expensive and impractical for large-scale applications.

**Adversarial-Based Noise Approximates a Gaussian Distribution.** Figure 7 presents the histogram and QQ-plot for adversarial-based noise. The visual evidence indicates that this type of noise closely approximates a Gaussian distribution. The visualizations also suggest that the noise is random and does not retain any information from the original latent representations. Both the histogram and QQ-plot are highly similar to those of standard Gaussian random noise. As a result, adversarial-based noise not only effectively perturbs model predictions but also serves as a suitable and reliable noise source for training. Notably, it can be generated efficiently using a single step of backpropagation.

Figure 8: Visual Results of the Minimax-Remover with Adversarial-Based Noise. Adversarial-based noise is integrated into the Minimax-Remover, yielding visually robust and consistent removal performance. *Best viewed with Acrobat Reader. Click the images to play the animation clips.*### 9.3 Testing Adversarial-Based Noise on the Robust MiniMax-Remover

We assess the performance of the robust Minimax-Remover when subjected to adversarial-based noise. Specifically, we apply adversarial noise to Minimax-Remover and gradually increase the noise level  $\alpha$  from 0.001 to 0.8. As illustrated in Figure 8, our method successfully removes objects from video frames effectively, maintaining high visual quality when  $\alpha < 0.5$ . Even as the noise level increases beyond 0.5, the removal results may become slightly blurred, but no regenerated objects or visual artifacts are observed. This demonstrates that the MiniMax-Remover is resilient to high levels of adversarial-based noise and can still produce clean and reliable removal results under challenging conditions.

## 10 The Prompt used for GPT-O3 Evaluation

The evaluation is conducted using the GPT-03-2025-04-16 model. We employ the following prompt to assess visual quality and success rate.

#### Prompt for Quality Evaluation

**Human:** Please evaluate the visual quality of the object-removal result in image pairs: the left panel shows the original frame with the target object highlighted by a blue mask, and the right panel shows the frame after the object has been removed. Rate the quality of the removal on a scale from 1 to 10, where 10 means a seamless, high-resolution result with no visible artifacts, 5 indicates some noise or artifacts but overall acceptable quality, and 1 corresponds to an unacceptable, very poor result. Return only the numeric score.

<Image> Image 1</Image>  
<Image> Image 2</Image>

...

**GPT-03:** ...

#### Prompt for Success Rate Evaluation

**Human:** This is a video object removal task. The object to be removed is already marked in blue in the image on the left. Please determine whether the object has been successfully removed. A successful removal is defined by the following criteria:

1. 1. The object has been completely removed.
2. 2. There is no visible blurriness in the removal area (not background blur, but unnatural foreground blur that is inconsistent with the surrounding context).
3. 3. There are no moiré patterns or artifacts in the region (e.g., unnatural textures that differ significantly from human visual expectations).
4. 4. No new, unwanted objects have been generated in the area (e.g., the tiger is removed but a bear appears instead, or another tiger is generated).
5. 5. Shadows not in the masked region are considered successfully removed.

Think it step by step. Then provide a final judgment by answering with "yes" or "no"

<Image> Image 1</Image>  
<Image> Image 2</Image>

...

**GPT-03:** ...

## 11 Limitation and Future Work

In this study, we present a fast and effective method for video object removal that does not rely on CFG. However, our approach has some limitations. First, the object remover in Stage 2 was trained using only 10,000 videos. Second, while the DiT model is efficient, a large portion of the computational overhead comes from the VAE encoding and decoding processes. In future work, weplan to expand the dataset to enhance the remover's robustness and explore the use of a smaller VAE to speed up inference.
