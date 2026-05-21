---
title: "Multimodal AI 101 (7/10): Text-to-Image with Diffusion"
series: multimodal-ai-101
episode: 7
language: en
status: content-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Diffusion
- Stable Diffusion
- Text-to-Image
- DALL-E
- Image Generation
- ControlNet
last_reviewed: '2026-05-03'
seo_description: From 2014 to around 2020, GANs were the default for image generation.
  StyleGAN produced eerily realistic faces, but it had two persistent…
---

# Multimodal AI 101 (7/10): Text-to-Image with Diffusion

This is post 7 in the Multimodal AI 101 series.

> Multimodal AI 101 series (7/10)

## Questions to Keep in Mind

- What boundary should you inspect first when applying Text-to-Image with Diffusion?
- Which signal should the example or diagram make visible for Text-to-Image with Diffusion?
- What failure should be prevented first when Text-to-Image with Diffusion reaches a real system?

## Big Picture

![Multimodal AI 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/07/07-01-big-picture.en.png)

*Multimodal AI 101 chapter 7 flow overview*

This picture places Text-to-Image with Diffusion inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why diffusion replaced GANs

From 2014 to around 2020, GANs were the default for image generation. StyleGAN produced eerily realistic faces, but it had two persistent weaknesses: mode collapse (the same patterns appearing over and over), and limited control via free-form text.

Diffusion models address both. Training is far more stable than GANs, and combining classifier-free guidance with a text encoder lets you generate images from arbitrary prompts. When Stable Diffusion was released as open weights in 2022, this approach became commodity. This episode covers what you need to use diffusion models in production.

## Forward / reverse process at a glance

```text
original image x_0
    | progressively add Gaussian noise (T steps)
    v
pure noise x_T  ~ N(0, I)
    | trained model removes noise step by step
    v
restored / generated image x_0'
```

- Forward: `x_t = sqrt(alpha_t) * x_0 + sqrt(1 - alpha_t) * eps` with a fixed noise schedule
- Reverse: model predicts `eps_theta(x_t, t, text)` and removes noise
- Loss is simple: `MSE(eps, eps_theta)`

Text conditioning enters through cross-attention. A CLIP text encoder turns the prompt into embeddings, and the UNet attends to them at each layer.

## Stable Diffusion components

Stable Diffusion (SD) is built from three models.

| Component | Role | Typical backbone |
| --- | --- | --- |
| Text encoder | prompt to embedding | CLIP ViT-L/14 (SD1.5), OpenCLIP-G (SDXL) |
| UNet | noise prediction in latent space | 860M (SD1.5) to 2.6B (SDXL) |
| VAE | pixel <-> latent (4x downscale) | autoencoder, ~84M |

The key trick is latent diffusion. Instead of running diffusion at 512x512 pixels (786K dim), it runs at 64x64x4 latents (16K dim). GPU memory and speed improve by an order of magnitude.

## First call: 30 seconds with diffusers

```python
import torch
from diffusers import StableDiffusionXLPipeline

pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16",
).to("cuda")

prompt = (
    "A cozy reading nook with a warm lamp, an open book, "
    "a steaming mug of tea, late afternoon light, photorealistic, 35mm"
)
negative = "blurry, low quality, watermark, text, deformed hands"

image = pipe(
    prompt=prompt,
    negative_prompt=negative,
    num_inference_steps=30,
    guidance_scale=7.0,
    height=1024, width=1024,
).images[0]

image.save("nook.png")
```

`num_inference_steps` is the number of reverse steps. SDXL works best at 25-40. `guidance_scale` controls classifier-free guidance (CFG); 7-9 is typical. Push it too high and colors burn out and oversaturate.

## Negative prompts and CFG

CFG runs the forward pass twice. It compares the result with and without the text condition and pushes the difference harder.

```text
eps_guided = eps_uncond + scale * (eps_text - eps_uncond)
```

`negative_prompt` is the trick of placing "leave these out" content in the unconditional slot to suppress them precisely. Putting common artifacts like "watermark, text, deformed hands" in the negative prompt immediately stabilizes results.

## Composition control with ControlNet

Prompts alone cannot precisely control human pose, building outlines, or depth. ControlNet injects additional conditions (canny edges, depth, pose, scribble, etc.) into the UNet through zero-conv layers, forcing the composition.

```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers.utils import load_image
from controlnet_aux import OpenposeDetector

openpose = OpenposeDetector.from_pretrained("lllyasviel/Annotators")
control_image = openpose(load_image("samples/dancer.jpg"))

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-openpose", torch_dtype=torch.float16
)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16,
).to("cuda")

image = pipe(
    "an astronaut dancing on the moon, dramatic lighting, cinematic",
    image=control_image,
    num_inference_steps=30,
    controlnet_conditioning_scale=1.0,
).images[0]
image.save("astronaut_pose.png")
```

The four ControlNet variants used most often in production are Canny (outlines), Depth (depth map), OpenPose (human pose), and Scribble (rough sketch).

## Model evolution: SD1.5 -> SDXL -> SD3 / Flux

| Model | Released | Resolution | Strengths | Weaknesses |
| --- | --- | --- | --- | --- |
| SD 1.5 | 2022.10 | 512 | top LoRA / ControlNet ecosystem | weak hands and text |
| SDXL | 2023.07 | 1024 | quality, prompt adherence | needs 12GB+ VRAM |
| SD 3 | 2024.06 | 1024 | text rendering, multi-subject | license restrictions |
| Flux.1 | 2024.08 | 1024 | best text and prompt adherence | 12B params, slow |

Production decisions are simple. For fast inference, use SDXL Turbo or LCM-LoRA at four steps. For top quality, use Flux dev. For a free-form fine-tune ecosystem, use SDXL.

## Inpainting and image-to-image

`StableDiffusionInpaintPipeline` regenerates only a masked region. It is a workhorse in production for swapping product backgrounds or removing defects.

```python
from diffusers import StableDiffusionInpaintPipeline
from diffusers.utils import load_image

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",
    torch_dtype=torch.float16,
).to("cuda")

init = load_image("samples/product.png")
mask = load_image("samples/product_mask.png")  # white = replace, black = keep

result = pipe(
    prompt="a wooden desk with morning sunlight, soft shadow",
    image=init, mask_image=mask,
    num_inference_steps=30, guidance_scale=7.5,
).images[0]
result.save("product_recomposed.png")
```

Image-to-image partially destroys the input with noise and then reconstructs it under prompt conditioning. The `strength` parameter (0-1) controls how much it transforms.

## Comparing with the DALL-E API

OpenAI DALL-E 3 has excellent prompt adherence but does not support fine-tuning or ControlNet. It is the easiest starting point if you do not want to self-host.

```python
from openai import OpenAI

client = OpenAI()
resp = client.images.generate(
    model="dall-e-3",
    prompt="A cozy reading nook with warm lamp, late afternoon light",
    size="1024x1024", quality="hd", n=1,
)
print(resp.data[0].url)
```

Pricing is 0.04 USD for 1024 standard and 0.08 USD for HD. Above roughly 10K images per month, SDXL self-host (1-2 USD per GPU hour) starts winning on cost.

## Five common pitfalls

### 1. Ignoring prompt token length

The CLIP text encoder takes 77 tokens. Long prompts get truncated at the end. SDXL's dual encoder is more forgiving, but the "key nouns up front" rule still applies.

### 2. Bypassable NSFW / safety filter

The default safety checker in open models can be disabled. In production, place a separate NSFW classifier (for example `Falconsai/nsfw_image_detection`) and a prompt blocklist in front of the pipeline.

### 3. Copyright and personal-likeness risk

Putting a specific artist's name or a real person's name in the prompt is legally risky. Enterprise pipelines pre-screen prompts with an LLM or use a noun whitelist.

### 4. GPU memory and batch size

SDXL 1024 needs about 9GB VRAM in fp16; batch 4 jumps to 12-14GB. `enable_model_cpu_offload()` and `enable_xformers_memory_efficient_attention()` cut this further.

```python
pipe.enable_model_cpu_offload()
pipe.enable_xformers_memory_efficient_attention()
```

### 5. Latency vs step count trade-off

A 30-step SDXL generation takes about 5 seconds on an RTX 4090. User-facing services drop to SDXL Turbo at four steps (0.6 seconds) or LCM-LoRA at around eight steps. Quality drops slightly, but throughput improves 7-10x.

## Key takeaways

- Diffusion has a forward (add noise) and reverse (remove noise) process; text conditioning enters through cross-attention.
- Stable Diffusion combines text encoder, UNet, and VAE, running diffusion in latent space for GPU efficiency.
- The diffusers library exposes SDXL, ControlNet, inpainting, and image-to-image through one API pattern.
- Model selection comes down to SDXL (ecosystem), Flux (top quality), or DALL-E API (lightweight start).
- Verify prompt token limits, NSFW / copyright filters, GPU memory, and the step-vs-latency trade-off before going to production.

---

## Answering the Opening Questions

- **What boundary should you inspect first when applying Text-to-Image with Diffusion?**
  - The article treats Text-to-Image with Diffusion as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Text-to-Image with Diffusion?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Text-to-Image with Diffusion reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Multimodal AI 101 (1/10): Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model Architecture](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning and OCR Pipelines](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: Searching Images and Text Together](./05-multimodal-rag.md)
- [Multimodal AI 101 (6/10): Audio Processing and Whisper STT](./06-audio-whisper.md)
- **Text-to-Image with Diffusion (current)**
- Multimodal Embeddings and Cross-modal Search (upcoming)
- Video Understanding - From Frame Sampling to Video-LLaVA (upcoming)
- Building a Production Multimodal Application (upcoming)

<!-- toc:end -->

## References

- [Rombach et al. - High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752)
- [Hugging Face diffusers Documentation](https://huggingface.co/docs/diffusers)
- [Zhang et al. - Adding Conditional Control to Text-to-Image Diffusion Models (ControlNet)](https://arxiv.org/abs/2302.05543)
- [Stability AI - Stable Diffusion XL Technical Report](https://arxiv.org/abs/2307.01952)

Tags: Diffusion, Stable Diffusion, Text-to-Image, DALL-E, Image Generation, ControlNet
