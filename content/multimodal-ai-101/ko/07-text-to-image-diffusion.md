---
title: Diffusion으로 Text-to-Image 생성
series: multimodal-ai-101
episode: 7
language: ko
status: content-ready
targets:
  tistory: true
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
last_reviewed: '2026-05-11'
seo_description: 2014~2020년 image generation의 default는 GAN이었습니다.
---

# Diffusion으로 Text-to-Image 생성

> Multimodal AI 101 시리즈 (7/10)

---


## 왜 Diffusion이 GAN을 밀어냈나

2014~2020년 image generation의 default는 GAN이었습니다. StyleGAN은 인물 사진을 무섭게 잘 만들었지만 두 가지가 약했습니다. mode collapse(특정 패턴만 반복) 문제, 그리고 자유 텍스트로 제어하기 어렵다는 한계입니다.

Diffusion model은 두 문제를 동시에 풉니다. 학습 안정성이 GAN보다 훨씬 좋고, classifier-free guidance와 text encoder를 결합하면 임의의 prompt로 이미지를 만들 수 있습니다. 2022년 Stable Diffusion이 open weight로 공개되면서 이 흐름이 commodity가 됐습니다. 이번 편은 diffusion model을 가져다 쓰는 production 관점에서 핵심을 정리합니다.

## Forward / Reverse process 한눈에

```
원본 이미지 x_0
    | 점진적으로 Gaussian noise 추가 (T 스텝)
    v
순수 noise x_T  ~ N(0, I)
    | 학습된 모델이 noise를 한 스텝씩 제거
    v
복원/생성 이미지 x_0'
```

- Forward: `x_t = sqrt(alpha_t) * x_0 + sqrt(1 - alpha_t) * eps` (학습 시 noise schedule을 미리 정함)
- Reverse: model이 `eps_theta(x_t, t, text)`를 예측해서 noise를 제거
- Loss는 단순합니다. `MSE(eps, eps_theta)`

text conditioning은 cross-attention으로 들어갑니다. CLIP text encoder가 prompt를 embedding으로 만들고, UNet이 각 layer에서 그것에 attend합니다.

## Stable Diffusion 구성 요소

Stable Diffusion(SD)은 3개의 모델로 구성됩니다.

| 컴포넌트 | 역할 | 일반 백본 |
| --- | --- | --- |
| Text encoder | prompt를 embedding으로 | CLIP ViT-L/14 (SD1.5), OpenCLIP-G (SDXL) |
| UNet | latent space에서 noise 예측 | 860M (SD1.5) ~ 2.6B (SDXL) |
| VAE | pixel ↔ latent 변환 (4x downscale) | Autoencoder, ~84M |

핵심 트릭은 latent diffusion입니다. 512x512 pixel(786K dim)이 아니라 64x64x4 latent(16K dim)에서 diffusion을 돌립니다. GPU memory와 속도가 한 자릿수 배 좋아집니다.

## 첫 호출: diffusers로 30초

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

`num_inference_steps`가 reverse 스텝 수입니다. SDXL은 25~40이 sweet spot입니다. `guidance_scale`은 classifier-free guidance(CFG) 강도로 7~9가 일반적입니다. 너무 높이면 색이 타고 saturated 됩니다.

## Negative prompt와 CFG

CFG는 두 번 forward를 돌립니다. text condition이 있을 때와 없을 때를 비교해서 차이를 강하게 밀어주는 방식입니다.

```
eps_guided = eps_uncond + scale * (eps_text - eps_uncond)
```

`negative_prompt`는 "이런 건 빼고"를 unconditional 자리에 넣어 정밀하게 제거하는 트릭입니다. "watermark, text, deformed hands" 같은 빈출 artifact를 negative에 넣으면 결과 안정성이 즉시 올라갑니다.

## ControlNet으로 구도 제어하기

prompt만으로는 사람 자세, 건물 윤곽, 깊이를 정확히 제어하기 어렵습니다. ControlNet은 추가 조건(canny edge, depth, pose, scribble 등)을 UNet에 zero-conv로 주입해서 구도를 강제합니다.

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

production에서 자주 쓰이는 ControlNet 종류는 Canny(외곽선), Depth(깊이맵), OpenPose(인체 자세), Scribble(러프 스케치) 네 가지입니다.

## 모델 진화: SD1.5 → SDXL → SD3 / Flux

| 모델 | 출시 | 해상도 | 강점 | 약점 |
| --- | --- | --- | --- | --- |
| SD 1.5 | 2022.10 | 512 | LoRA·ControlNet 생태계 1순위 | 손, text 약함 |
| SDXL | 2023.07 | 1024 | quality, prompt adherence | VRAM 12GB+ 필요 |
| SD 3 | 2024.06 | 1024 | text 렌더링, 다중 subject | 라이선스 제한 |
| Flux.1 | 2024.08 | 1024 | text·prompt adherence 최상 | 12B 파라미터, 느림 |

production 의사결정은 단순합니다. 빠른 inference가 필요하면 SDXL Turbo나 LCM-LoRA로 4 step 생성을, 최고 품질이면 Flux dev, 자유로운 finetune 생태계가 필요하면 SDXL입니다.

## inpainting과 image-to-image

`StableDiffusionInpaintPipeline`은 mask 영역만 다시 그립니다. 광고 이미지에서 배경만 교체하거나, 결함 객체를 지우는 production 작업에 자주 쓰입니다.

```python
from diffusers import StableDiffusionInpaintPipeline
from diffusers.utils import load_image

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",
    torch_dtype=torch.float16,
).to("cuda")

init = load_image("samples/product.png")
mask = load_image("samples/product_mask.png")  # 흰색=교체, 검은색=유지

result = pipe(
    prompt="a wooden desk with morning sunlight, soft shadow",
    image=init, mask_image=mask,
    num_inference_steps=30, guidance_scale=7.5,
).images[0]
result.save("product_recomposed.png")
```

image-to-image는 input 이미지를 noise로 일부 망가뜨린 뒤 prompt 조건으로 다시 복원하는 방식입니다. `strength` 파라미터(0~1)로 변형 정도를 조절합니다.

## DALL-E API와 비교

OpenAI DALL-E 3은 prompt adherence가 뛰어나지만 finetune이나 ControlNet을 못 씁니다. self-host가 부담스러우면 좋은 시작점입니다.

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

가격은 1024 standard가 0.04 USD, hd가 0.08 USD입니다. 월 1만 장 이상이면 SDXL self-host(GPU 시간당 1~2 USD)가 cost 우위에 들어갑니다.

## 흔히 놓치는 함정 다섯 가지

### 1. prompt engineering을 token 단위로 안 봄

CLIP text encoder의 입력은 77 token입니다. 긴 prompt를 그대로 던지면 뒤가 잘립니다. SDXL은 dual encoder라 사정이 조금 낫지만, "주요 명사를 앞쪽에" 원칙은 여전히 유효합니다.

### 2. NSFW / safety filter 우회 가능

오픈 모델은 default safety checker를 끌 수 있습니다. production에서는 별도 NSFW classifier(예: `Falconsai/nsfw_image_detection`)와 prompt blocklist를 앞단에 둬야 합니다.

### 3. 저작권·인물 학습 risk

특정 작가 스타일이나 실존 인물 이름을 prompt에 넣는 것은 법적 risk입니다. enterprise에서는 prompt를 LLM으로 사전 검수하거나 명사 화이트리스트를 둡니다.

### 4. GPU memory와 batch

SDXL 1024는 fp16에서 약 9GB VRAM, batch 4면 12~14GB로 뜁니다. `enable_model_cpu_offload()`나 `enable_xformers_memory_efficient_attention()`을 켜면 추가 절감됩니다.

```python
pipe.enable_model_cpu_offload()
pipe.enable_xformers_memory_efficient_attention()
```

### 5. latency와 step 수의 trade-off

30 step 생성은 SDXL 기준 RTX 4090에서 약 5초입니다. user-facing service는 SDXL Turbo + 4 step(0.6초) 또는 LCM-LoRA로 8 step 정도까지 줄여서 씁니다. quality는 약간 떨어지지만 throughput이 7~10배 좋아집니다.

## 핵심 요약

- Diffusion은 forward(noise 추가)와 reverse(noise 제거) process로 구성되며, text conditioning은 cross-attention으로 들어갑니다.
- Stable Diffusion은 text encoder, UNet, VAE 3개 모델 조합이며 latent space에서 diffusion을 돌려 GPU 효율을 확보합니다.
- diffusers 라이브러리로 SDXL, ControlNet, inpainting, image-to-image를 한 API 패턴으로 다룹니다.
- 모델 선택은 SDXL(생태계), Flux(최고 품질), DALL-E API(가벼운 시작)로 나뉩니다.
- prompt token 한계, NSFW/저작권, GPU memory, step-vs-latency trade-off는 production 도입 전 점검 필수입니다.

---

<!-- toc:begin -->
## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- [오디오 처리와 Whisper STT](./06-audio-whisper.md)
- **Diffusion으로 Text-to-Image 생성 (현재 글)**
- Multimodal Embedding과 cross-modal 검색 (예정)
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Rombach et al. - High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752)
- [Hugging Face diffusers Documentation](https://huggingface.co/docs/diffusers)
- [Zhang et al. - Adding Conditional Control to Text-to-Image Diffusion Models (ControlNet)](https://arxiv.org/abs/2302.05543)
- [Stability AI - Stable Diffusion XL Technical Report](https://arxiv.org/abs/2307.01952)

Tags: Diffusion, Stable Diffusion, Text-to-Image, DALL-E, Image Generation, ControlNet
