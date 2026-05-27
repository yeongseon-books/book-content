---
title: "Multimodal AI 101 (7/10): Diffusion으로 Text-to-Image 생성"
series: multimodal-ai-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Diffusion
- Stable Diffusion
- Text-to-Image
- DALL-E
- Image Generation
- ControlNet
last_reviewed: '2026-05-12'
seo_description: 2014~2020년 image generation의 default는 GAN이었습니다.
---

# Multimodal AI 101 (7/10): Diffusion으로 Text-to-Image 생성

텍스트에서 이미지를 생성하는 모델은 한동안 데모의 영역에 머무는 듯 보였습니다. GAN 시절에는 품질이 불안정했고, 프롬프트 제어도 까다로웠습니다. 그런데 diffusion 계열이 자리 잡으면서 분위기가 완전히 바뀌었습니다. 이제는 한 장의 멋진 이미지를 넘어서, 제품 목업, 광고 시안, 게임 콘셉트, 인페인팅, 이미지 편집까지 production 워크플로에 직접 연결되는 수준이 됐습니다.

이 글은 Multimodal AI 101 시리즈의 7번째 글입니다.

Diffusion이 중요한 이유는 생성 품질만이 아닙니다. 텍스트 조건, 이미지 조건, 마스크, depth, edge map 같은 제어 신호를 유연하게 얹을 수 있기 때문입니다. 즉 text-to-image는 독립 기능이 아니라, 점점 더 일반적인 시각 생성 인터페이스가 되고 있습니다.

실무에서는 모델 선택과 추론 비용이 바로 운영 문제로 이어집니다. step 수, CFG, negative prompt, GPU 메모리, safety filter, 저작권 리스크가 모두 같은 테이블 위에서 판단됩니다. 생성형 멀티모달은 품질이 좋을수록 오히려 운영 경계를 더 명확히 잡아야 합니다.

이 글에서는 diffusion을 “이미지를 그려 주는 모델”이 아니라, 노이즈를 점진적으로 제어 가능한 시각 표현으로 되돌리는 생성 프레임워크로 정리합니다.

생성 품질을 올리는 일과 운영 위험을 낮추는 일은 항상 함께 가야 합니다.

![Multimodal AI 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/07/07-01-big-picture.ko.png)
*Multimodal AI 101 7장 흐름 개요*
> Diffusion으로 Text-to-Image 생성의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 왜 diffusion이 GAN을 빠르게 밀어내고 시각 생성의 기본 구조가 되었을까요?
- forward process와 reverse process를 어떤 멘탈 모델로 이해하면 가장 실용적일까요?
- Stable Diffusion의 text encoder, UNet, VAE는 각각 어떤 역할을 맡을까요?

## 왜 이 글이 중요한가

텍스트-이미지 생성은 이미 콘텐츠 제작과 프로토타이핑의 표준 도구가 되었습니다. 디자인 시안, 마케팅 소재, 게임 아트, 데이터 증강처럼 쓰임새가 넓기 때문에 멀티모달을 다루는 엔지니어라면 구조를 이해할 필요가 있습니다.

또한 diffusion 계열은 생성보다 제어가 더 중요해지는 흐름을 보여 줍니다. 같은 base model이라도 ControlNet, inpainting, image-to-image를 어떻게 쓰느냐에 따라 제품 가치가 크게 달라집니다.

반대로 운영 감각 없이 도입하면 비용과 위험이 빠르게 커집니다. 품질이 좋아 보이는 데모와 production 워크플로 사이에는 safety, latency, 저작권, 사용자 기대치 관리라는 큰 간격이 있습니다.

## 핵심 관점

Diffusion 모델의 직관은 surprisingly 단순합니다. 학습 단계에서는 이미지를 조금씩 망가뜨리는 법을 배우고, 추론 단계에서는 그 망가짐을 역방향으로 되돌리는 법을 배웁니다. 그래서 생성 과정 전체가 여러 step의 반복 제어 문제로 보입니다.

이 관점은 CFG, negative prompt, scheduler 선택이 왜 중요한지 설명해 줍니다. 한 번의 결정이 아니라 많은 step에 걸쳐 신호를 누적하기 때문에, 작은 설정 차이도 최종 이미지 품질과 스타일에 크게 영향을 줍니다.

실무적으로도 diffusion을 제어 시스템으로 보면 좋습니다. 어떤 조건 신호를 넣을지, 몇 step까지 허용할지, 어느 시점에서 사람 검수를 붙일지 같은 운영 정책이 자연스럽게 모델 설정으로 연결되기 때문입니다.

> Diffusion의 힘은 한 번에 완성된 이미지를 내는 데 있지 않습니다. 매 step에서 조건 신호를 조금씩 반영하며 결과를 통제할 수 있다는 데 있습니다.

## 핵심 개념

### 왜 Diffusion이 GAN을 밀어냈나

2014~2020년 image generation의 default는 GAN이었습니다. StyleGAN은 인물 사진을 무섭게 잘 만들었지만 두 가지가 약했습니다. mode collapse(특정 패턴만 반복) 문제, 그리고 자유 텍스트로 제어하기 어렵다는 한계입니다.

Diffusion model은 두 문제를 동시에 풉니다. 학습 안정성이 GAN보다 훨씬 좋고, classifier-free guidance와 text encoder를 결합하면 임의의 prompt로 이미지를 만들 수 있습니다. 2022년 Stable Diffusion이 open weight로 공개되면서 이 흐름이 commodity가 됐습니다. 이번 편은 diffusion model을 가져다 쓰는 production 관점에서 핵심을 정리합니다.

### Forward / Reverse process 한눈에

```text
original image x_0
    | progressively add Gaussian noise (T steps)
    v
pure noise x_T  ~ N(0, I)
    | trained model removes noise step by step
    v
restored / generated image x_0'
```

- Forward: `x_t = sqrt(alpha_t) * x_0 + sqrt(1 - alpha_t) * eps` (학습 시 noise schedule을 미리 정함)
- Reverse: model이 `eps_theta(x_t, t, text)`를 예측해서 noise를 제거
- Loss는 단순합니다. `MSE(eps, eps_theta)`

text conditioning은 cross-attention으로 들어갑니다. CLIP text encoder가 prompt를 embedding으로 만들고, UNet이 각 layer에서 그것에 attend합니다.

### Stable Diffusion 구성 요소

Stable Diffusion(SD)은 3개의 모델로 구성됩니다.

| 컴포넌트 | 역할 | 일반 백본 |
| --- | --- | --- |
| Text encoder | prompt를 embedding으로 | CLIP ViT-L/14 (SD1.5), OpenCLIP-G (SDXL) |
| UNet | latent space에서 noise 예측 | 860M (SD1.5) ~ 2.6B (SDXL) |
| VAE | pixel ↔ latent 변환 (4x downscale) | Autoencoder, ~84M |

핵심 트릭은 latent diffusion입니다. 512x512 pixel(786K dim)이 아니라 64x64x4 latent(16K dim)에서 diffusion을 돌립니다. GPU memory와 속도가 한 자릿수 배 좋아집니다.

### 첫 호출: diffusers로 30초

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

### Negative prompt와 CFG

CFG는 두 번 forward를 돌립니다. text condition이 있을 때와 없을 때를 비교해서 차이를 강하게 밀어주는 방식입니다.

```text
eps_guided = eps_uncond + scale * (eps_text - eps_uncond)
```

`negative_prompt`는 "이런 건 빼고"를 unconditional 자리에 넣어 정밀하게 제거하는 트릭입니다. "watermark, text, deformed hands" 같은 빈출 artifact를 negative에 넣으면 결과 안정성이 즉시 올라갑니다.

### ControlNet으로 구도 제어하기

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

### 모델 진화: SD1.5 → SDXL → SD3 / Flux

| 모델 | 출시 | 해상도 | 강점 | 약점 |
| --- | --- | --- | --- | --- |
| SD 1.5 | 2022.10 | 512 | LoRA·ControlNet 생태계 1순위 | 손, text 약함 |
| SDXL | 2023.07 | 1024 | quality, prompt adherence | VRAM 12GB+ 필요 |
| SD 3 | 2024.06 | 1024 | text 렌더링, 다중 subject | 라이선스 제한 |
| Flux.1 | 2024.08 | 1024 | text·prompt adherence 최상 | 12B 파라미터, 느림 |

production 의사결정은 단순합니다. 빠른 inference가 필요하면 SDXL Turbo나 LCM-LoRA로 4 step 생성을, 최고 품질이면 Flux dev, 자유로운 finetune 생태계가 필요하면 SDXL입니다.

### inpainting과 image-to-image

`StableDiffusionInpaintPipeline`은 mask 영역만 다시 그립니다. 광고 이미지에서 배경만 교체하거나, 결함 객체를 지우는 production 작업에 자주 쓰입니다.

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

image-to-image는 input 이미지를 noise로 일부 망가뜨린 뒤 prompt 조건으로 다시 복원하는 방식입니다. `strength` 파라미터(0~1)로 변형 정도를 조절합니다.

### DALL-E API와 비교

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

### 추가 생성 경로 예제

text-to-image만 이해하면 생성 파이프라인의 절반만 본 셈입니다. 아래 예제는 실제 서비스에서 자주 이어 붙이는 추가 생성 경로를 보여 줍니다.

```python
pipe.enable_model_cpu_offload()
pipe.enable_xformers_memory_efficient_attention()
```
## 추론 파라미터를 실험 설계로 고정하기

Diffusion 품질은 모델 이름보다 실험 프로토콜에 더 민감합니다. 프롬프트 한 줄만 바꾸고 좋다/나쁘다를 판단하면 설정 편향이 크게 들어갑니다. 운영에서는 최소한 `num_inference_steps`, `guidance_scale`, `scheduler`, `seed`를 고정한 실험표를 만들고 비교해야 합니다.

```python
from dataclasses import dataclass

@dataclass
class DiffusionRun:
    steps: int
    cfg: float
    scheduler: str
    seed: int

grid = [
    DiffusionRun(20, 6.5, "euler_a", 42),
    DiffusionRun(30, 7.5, "dpmpp_2m", 42),
    DiffusionRun(40, 8.0, "dpmpp_2m", 42),
]
```

평가는 FID 같은 오프라인 지표만으로 충분하지 않습니다. 실제 제품에서는 브랜드 가이드 준수율, 텍스트 삽입 정확도, 사람이 보는 미학 점수, 안전 정책 위반률을 함께 기록해야 합니다. 특히 텍스트 렌더링 품질은 모델 세대에 따라 편차가 커서 별도 벤치마크가 필요합니다.

## 생성 결과 검수: Vision API 이중 안전망

생성 이미지를 바로 사용자에게 반환하지 않고 GPT-4V 또는 Claude로 정책 위반 여부를 한 번 더 검사하면 사고를 줄일 수 있습니다. 이때 이미지 분류기와 VLM을 함께 쓰면 정확도가 더 안정적입니다.

```python
def moderation_prompt() -> str:
    return (
        "Inspect the generated image. Return JSON with fields: "
        "nsfw, violence, personal_data, trademark_risk, confidence."
    )
```

검수 결과는 단순 block/allow로 끝내지 않고, 어떤 항목에서 차단됐는지 사용자에게 명확한 피드백을 제공하는 편이 좋습니다. 그래야 프롬프트 재작성 루프가 빠르게 돌아갑니다.

## 이미지 후처리와 저장 파이프라인

생성형 서비스에서는 최종 저장 단계도 품질 일부입니다. 원본 PNG를 그대로 저장하면 용량이 커져 전송 지연이 생길 수 있으므로, 품질 손실을 통제한 WebP 변환을 기본 경로로 두는 팀이 많습니다.

```python
from PIL import Image

def optimize_output(path_in: str, path_out: str) -> None:
    img = Image.open(path_in).convert("RGB")
    img.save(path_out, format="WEBP", quality=92, method=6)
```

또한 생성 메타데이터(프롬프트, 시드, 스텝, 모델 버전)를 함께 저장해야 재현성과 감사가 확보됩니다. 이 메타데이터가 없으면 품질 이슈를 회귀 테스트하기 어렵습니다.

## 프롬프트 템플릿과 버전 관리

텍스트-이미지 생성 서비스는 프롬프트가 사실상 코드 역할을 합니다. 따라서 프롬프트 템플릿을 코드 저장소에서 버전으로 관리하고, 변경 시 샘플셋 회귀 테스트를 돌리는 절차가 필요합니다. 템플릿 관리가 없으면 팀원이 바뀔 때 출력 스타일이 크게 흔들립니다.

```python
PROMPT_TEMPLATE_V3 = (
    "{subject}, {style}, {lighting}, high detail, clean composition, "
    "no watermark, no text artifacts"
)

def build_prompt(subject: str, style: str, lighting: str) -> str:
    return PROMPT_TEMPLATE_V3.format(subject=subject, style=style, lighting=lighting)
```

이 버전 필드를 생성 메타데이터에 남기면 고객 피드백이 들어왔을 때 어떤 프롬프트 정책에서 문제가 발생했는지 추적할 수 있습니다.

## 제품 운영에서 필요한 생성 요청 큐 설계

생성 요청은 사용자 체감 지연이 크기 때문에 큐 설계가 중요합니다. 요청이 몰릴 때 무제한 동시 실행을 허용하면 GPU 메모리 부족으로 전체 서비스가 불안정해질 수 있습니다. 그래서 보통 모델별 동시 실행 슬롯을 고정하고, 초과 요청은 큐에서 대기시키는 방식이 안전합니다.

```python
import asyncio

class GenerationQueue:
    def __init__(self, max_concurrency: int = 2):
        self.sem = asyncio.Semaphore(max_concurrency)

    async def run(self, coro):
        async with self.sem:
            return await coro
```

또한 요청 우선순위를 두면 운영이 훨씬 수월해집니다. 예를 들어 결제 사용자 요청을 우선 처리하고 무료 사용자 요청은 백그라운드 큐로 보내는 정책을 적용할 수 있습니다.

이 계층을 명시적으로 두면 모델이 바뀌어도 서비스 품질 예측이 쉬워집니다. 생성형 기능은 모델 성능보다 큐 정책이 체감 품질을 더 크게 바꾸는 경우가 많습니다.

## A/B 테스트: 모델 교체 전 검증 루틴

생성 모델 교체는 반드시 A/B 테스트로 진행해야 합니다. 동일 프롬프트셋, 동일 시드셋으로 두 모델 출력을 비교하고, 내부 평가자 점수와 자동 지표를 함께 기록하는 방식이 안전합니다.

```python
AB_PROMPTS = [
    "제품 사진형 광고 배너",
    "자연광 인물 포스터",
    "텍스트가 포함된 인포그래픽",
]
```

특히 텍스트 렌더링과 손가락 형태처럼 자주 깨지는 항목은 별도 체크리스트를 두어야 회귀를 빠르게 잡을 수 있습니다.

## 운영 검증 루프: 주간 점검 항목을 고정하기

멀티모달 시스템은 모델 정확도만으로 상태를 판단하면 늦게 대응하게 됩니다. 그래서 주간 운영 회의에서 항상 같은 항목을 점검하는 루프를 고정하는 편이 좋습니다. 예를 들어 요청량, 평균 지연 시간, P95 지연, 오류율, 재시도율, 캐시 히트율, 사용자 불만 비율을 동일 포맷으로 기록하면 작은 이상 징후를 초기에 잡을 수 있습니다.

또한 지표는 기능별로 분해해야 합니다. 단일 "성공률" 수치만 보면 어떤 단계에서 손실이 났는지 알기 어렵습니다. 입력 검증 단계, 전처리 단계, 검색 단계, 생성 단계를 분리해 성공률을 기록하면 병목 구간이 명확해집니다. 이 분해 지표는 모델 교체나 파이프라인 변경 후 회귀를 탐지하는 데 특히 유용합니다.

```python
weekly_health = {
    "request_count": 0,
    "avg_latency_ms": 0,
    "p95_latency_ms": 0,
    "error_rate": 0.0,
    "retry_rate": 0.0,
    "cache_hit_rate": 0.0,
    "user_downvote_rate": 0.0,
}
```

운영 루프를 고정하면 기술 선택도 더 현실적으로 바뀝니다. 새 모델을 도입할 때 "정확도 상승"만 보지 않고, 지연 증가와 비용 증가를 같은 표에서 비교할 수 있기 때문입니다. 결국 프로덕션 품질은 한 번의 모델 업그레이드가 아니라, 반복 가능한 점검 루프를 통해 유지됩니다.

## 흔히 헷갈리는 지점

- **prompt engineering을 token 단위로 안 봄** CLIP text encoder의 입력은 77 token입니다. 긴 prompt를 그대로 던지면 뒤가 잘립니다. SDXL은 dual encoder라 사정이 조금 낫지만, "주요 명사를 앞쪽에" 원칙은 여전히 유효합니다.
- **NSFW / safety filter 우회 가능** 오픈 모델은 default safety checker를 끌 수 있습니다. production에서는 별도 NSFW classifier(예: `Falconsai/nsfw_image_detection`)와 prompt blocklist를 앞단에 둬야 합니다.
- **저작권·인물 학습 risk** 특정 작가 스타일이나 실존 인물 이름을 prompt에 넣는 것은 법적 risk입니다. enterprise에서는 prompt를 LLM으로 사전 검수하거나 명사 화이트리스트를 둡니다.
- **GPU memory와 batch** SDXL 1024는 fp16에서 약 9GB VRAM, batch 4면 12~14GB로 뜁니다. `enable_model_cpu_offload()`나 `enable_xformers_memory_efficient_attention()`을 켜면 추가 절감됩니다.
- **latency와 step 수의 trade-off** 30 step 생성은 SDXL 기준 RTX 4090에서 약 5초입니다. user-facing service는 SDXL Turbo + 4 step(0.6초) 또는 LCM-LoRA로 8 step 정도까지 줄여서 씁니다. quality는 약간 떨어지지만 throughput이 7~10배 좋아집니다.

## 운영 체크리스트

- [ ] 모델별 권장 해상도와 step 수를 기준값으로 고정했는가
- [ ] negative prompt와 CFG 범위를 실험으로 수치화했는가
- [ ] safety filter와 NSFW 정책을 프론트엔드·백엔드 양쪽에 반영했는가
- [ ] 저작권·초상권 리스크가 있는 입력과 출력에 대한 가이드라인을 마련했는가
- [ ] GPU 메모리 사용량과 요청당 평균 latency를 모델 버전별로 기록하는가

## 정리

Diffusion은 GAN을 대체한 새로운 유행이 아니라, 시각 생성과 편집을 하나의 프레임워크로 묶은 구조입니다. 텍스트 조건, 이미지 조건, 마스크 조건을 유연하게 다루기 때문에 production 활용 범위가 넓습니다.

Stable Diffusion 계열을 이해하면 text-to-image뿐 아니라 inpainting, image-to-image, ControlNet 같은 확장 기능이 왜 자연스럽게 연결되는지도 보입니다. 모두 같은 역확산 루프 위에서 작동하기 때문입니다.

실무에서 중요한 것은 품질 지표만이 아닙니다. 비용, safety, 저작권, latency를 함께 설계해야 실제 제품에 넣을 수 있습니다. 생성형 멀티모달은 기술보다 운영이 먼저 무너지기 쉬운 영역입니다.

## 처음 질문으로 돌아가기

- **왜 diffusion이 GAN을 빠르게 밀어내고 시각 생성의 기본 구조가 되었을까요?**
  - GAN의 mode collapse와 프롬프트 제어 한계를 넘어서, 안정적인 학습과 자유 텍스트 조건부 생성을 함께 제공했기 때문입니다. 본문이 정리한 Stable Diffusion과 SDXL 흐름처럼 open weight 생태계, CFG, ControlNet, inpainting이 붙으면서 생성 품질뿐 아니라 제어 가능성까지 표준이 됐습니다.
- **forward process와 reverse process를 어떤 멘탈 모델로 이해하면 가장 실용적일까요?**
  - 학습에서는 `x_0`에 가우시안 노이즈를 점점 더해 `x_T`로 보내고, 추론에서는 모델이 `eps_theta(x_t, t, text)`를 예측해 그 노이즈를 단계적으로 걷어 내는 제어 루프로 이해하면 됩니다. 이 관점이 있어야 `num_inference_steps`, `guidance_scale`, `negative_prompt`, scheduler가 왜 최종 품질과 스타일에 큰 영향을 주는지 자연스럽게 연결됩니다.
- **Stable Diffusion의 text encoder, UNet, VAE는 각각 어떤 역할을 맡을까요?**
  - text encoder는 프롬프트를 임베딩으로 만들고, UNet은 latent 공간에서 각 step의 노이즈를 예측하며, VAE는 픽셀 이미지를 더 작은 latent와 다시 픽셀로 변환합니다. 본문 표처럼 이 latent diffusion 구조 덕분에 512x512 픽셀 대신 64x64x4 latent에서 계산해 VRAM과 속도를 크게 줄이면서도 ControlNet과 inpainting 같은 확장 기능을 같은 뼈대 위에 얹을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- [Multimodal AI 101 (6/10): 오디오 처리와 Whisper STT](./06-audio-whisper.md)
- **Diffusion으로 Text-to-Image 생성 (현재 글)**
- Multimodal Embedding과 Cross-modal 검색 (예정)
- Video 이해 - Frame Sampling에서 Video-LLaVA까지 (예정)
- Production Multimodal Application 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Rombach et al. - High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752)
- [Hugging Face diffusers Documentation](https://huggingface.co/docs/diffusers)
- [Zhang et al. - Adding Conditional Control to Text-to-Image Diffusion Models (ControlNet)](https://arxiv.org/abs/2302.05543)
- [Stability AI - Stable Diffusion XL Technical Report](https://arxiv.org/abs/2307.01952)

### 관련 시리즈

- [LLM API 프로덕션 101 - 캐싱 전략](../../llm-api-production-101/ko/04-caching-strategies.md)
- [AI 앱 패턴 101 - 워크플로 자동화](../../ai-app-patterns-101/ko/05-workflow-automation.md)
- [AI Agent 101 - 운영](../../ai-agent-101/ko/09-production-operations.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/07-text-to-image-diffusion)

Tags: Diffusion, Stable Diffusion, Text-to-Image, DALL-E, Image Generation, ControlNet
