---
title: Vision-Language Model 아키텍처
series: multimodal-ai-101
episode: 3
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- VLM
- LLaVA
- Cross-Attention
- Q-Former
- BLIP-2
- Multimodal Fusion
last_reviewed: '2026-05-03'
seo_description: 2편에서 본 CLIP은 image와 text를 같은 공간에 정렬하는 데까지 갔습니다.
---

# Vision-Language Model 아키텍처

> Multimodal AI 101 시리즈 (3/10)

---

<!-- a-grade-intro:begin -->
## 핵심 질문

VLM은 이미지와 텍스트를 어떻게 한 모델에서 함께 처리하나요?

이 글은 그 질문에 답하기 위해 Vision-Language Model 아키텍처의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## VLM은 어떻게 LLM에 "눈"을 다는가

2편에서 본 CLIP은 image와 text를 같은 공간에 정렬하는 데까지 갔습니다. 그런데 GPT-4V나 LLaVA처럼 "이 이미지를 설명하고 표를 markdown으로 변환해 줘" 같은 reasoning을 하려면 한 단계가 더 필요합니다. image vector를 LLM이 token처럼 소화할 수 있도록 연결해야 합니다.

VLM 아키텍처는 이 연결 방식에 따라 크게 세 학파로 나뉩니다. LLaVA의 projection 방식, BLIP-2의 Q-Former 방식, Flamingo의 cross-attention 방식. 이번 편에서 각 패턴이 무엇을 풀려고 했는지, 어떤 trade-off가 있는지를 봅니다.

## 공통 구조: Vision Encoder + Adapter + LLM

VLM은 결국 다음 세 부품의 조합입니다.

```
[Image] -> Vision Encoder (CLIP/SigLIP) -> visual features
                                               |
                                               v
                                          Adapter
                                               |
                                               v
[Text]  -> Tokenizer -> text tokens ----> LLM -> output
```

차이는 Adapter입니다. visual feature를 LLM이 "이해할 수 있는" token sequence로 변환하는 모듈인데, 여기서 학파가 갈립니다.

## 학파 1: LLaVA - 단순 MLP projection

LLaVA는 가장 단순합니다. CLIP image encoder의 출력 (예: 576 patch x 1024 dim)을 그대로 LLM hidden dim으로 projection하고, LLM 입력 sequence 앞에 끼워 넣습니다.

```python
import torch
import torch.nn as nn

class LLaVAProjector(nn.Module):
    def __init__(self, vision_dim: int = 1024, llm_dim: int = 4096):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(vision_dim, llm_dim),
            nn.GELU(),
            nn.Linear(llm_dim, llm_dim),
        )

    def forward(self, vision_features: torch.Tensor) -> torch.Tensor:
        # vision_features: (B, num_patches, vision_dim)
        return self.proj(vision_features)  # (B, num_patches, llm_dim)
```

학습은 두 단계입니다.

1. **Stage 1 (alignment)**: vision encoder와 LLM은 frozen, projection layer만 학습. 데이터는 (image, caption) 쌍.
2. **Stage 2 (instruction tuning)**: LLM과 projection을 함께 학습 (vision encoder는 여전히 frozen). 데이터는 GPT-4가 생성한 (image, instruction, answer) 쌍.

장점은 단순함과 빠른 학습입니다. LLaVA-1.5는 8xA100에서 1일 학습으로 GPT-4V 수준 reasoning 일부를 따라잡았습니다. 단점은 visual token 수가 그대로 LLM context에 누적된다는 점입니다 (576 token은 long-context model이 아니면 부담입니다).

## 학파 2: BLIP-2 - Q-Former로 token 압축

BLIP-2는 visual token이 너무 많다는 문제를 정면으로 풀었습니다. Q-Former라는 작은 Transformer를 만들어, learnable query 32개가 vision feature에서 핵심 정보를 cross-attention으로 끌어옵니다. 결과적으로 LLM이 받는 visual token은 32개로 고정됩니다.

```python
import torch
import torch.nn as nn

class QFormer(nn.Module):
    def __init__(self, num_queries: int = 32, vision_dim: int = 1408,
                 hidden_dim: int = 768, num_layers: int = 12):
        super().__init__()
        self.queries = nn.Parameter(torch.randn(num_queries, hidden_dim))
        layer = nn.TransformerDecoderLayer(
            d_model=hidden_dim, nhead=12, batch_first=True
        )
        self.decoder = nn.TransformerDecoder(layer, num_layers=num_layers)
        self.vision_proj = nn.Linear(vision_dim, hidden_dim)

    def forward(self, vision_features: torch.Tensor) -> torch.Tensor:
        # vision_features: (B, num_patches, vision_dim)
        B = vision_features.size(0)
        q = self.queries.unsqueeze(0).expand(B, -1, -1)  # (B, 32, hidden)
        memory = self.vision_proj(vision_features)
        return self.decoder(q, memory)  # (B, 32, hidden)
```

Q-Former 출력 32개 token이 다시 작은 linear projection을 거쳐 LLM에 들어갑니다. context 부담이 LLaVA의 1/18이라서 7B LLM에서도 multi-image batch가 가능합니다.

학습 trade-off: Q-Former 자체가 ITC, ITM, ITG 같은 복합 loss를 단계별로 학습해야 해서 LLaVA보다 파이프라인이 무겁습니다.

## 학파 3: Flamingo - LLM에 cross-attention layer 삽입

Flamingo는 다른 방향을 택했습니다. LLM의 transformer block 사이사이에 새 cross-attention layer를 끼워 넣고, 이 새 layer만 학습합니다. 기존 LLM weight는 모두 frozen입니다.

```
LLM Block 1
GATED CROSS-ATTENTION (new) <- vision features
LLM Block 2
GATED CROSS-ATTENTION (new) <- vision features
LLM Block 3
...
```

gated cross-attention은 처음에 gate=0으로 시작해 학습이 진행되며 천천히 열립니다. 이 덕분에 학습 초기에 LLM 성능이 망가지지 않습니다.

```python
import torch
import torch.nn as nn

class GatedCrossAttention(nn.Module):
    def __init__(self, dim: int, num_heads: int = 8):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, num_heads, batch_first=True)
        self.gate = nn.Parameter(torch.zeros(1))  # tanh-gated
        self.ff = nn.Sequential(nn.Linear(dim, dim * 4), nn.GELU(),
                                nn.Linear(dim * 4, dim))
        self.gate_ff = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor, vision: torch.Tensor) -> torch.Tensor:
        attn_out, _ = self.attn(x, vision, vision)
        x = x + torch.tanh(self.gate) * attn_out
        x = x + torch.tanh(self.gate_ff) * self.ff(x)
        return x
```

장점은 multi-image / video 입력에 가장 자연스럽다는 점입니다. cross-attention이라 sequence 길이를 늘리지 않습니다. 단점은 LLM 내부에 손을 대야 해서, 이미 학습된 LLM에 plug-in하기가 LLaVA보다 어렵습니다.

## 세 학파 비교

| 항목 | LLaVA | BLIP-2 | Flamingo |
| --- | --- | --- | --- |
| Adapter | MLP projection | Q-Former (cross-attn) | Gated cross-attn 삽입 |
| LLM 수정 | 없음 (input prefix만) | 없음 (input prefix만) | 있음 (layer 삽입) |
| Visual tokens to LLM | 256~576 | 32 | 0 (cross-attn) |
| 학습 난이도 | 낮음 (2-stage) | 중간 (3-stage Q-Former) | 높음 |
| Multi-image | 가능하지만 context 부담 | 효율적 | 가장 자연스러움 |
| 대표 모델 | LLaVA-1.5, MiniGPT-4 | BLIP-2, InstructBLIP | Flamingo, IDEFICS |

실무에서 시작점은 거의 LLaVA입니다. open weight, 학습 코드 공개, fine-tuning 비용이 낮기 때문입니다. multi-image / video 워크로드가 본격화되면 BLIP-2 계열이나 IDEFICS-2를 검토합니다.

## LLaVA로 첫 추론 돌리기

```python
import torch
from PIL import Image
from transformers import LlavaForConditionalGeneration, AutoProcessor

model_id = "llava-hf/llava-1.5-7b-hf"
processor = AutoProcessor.from_pretrained(model_id)
model = LlavaForConditionalGeneration.from_pretrained(
    model_id, torch_dtype=torch.float16, device_map="auto"
)

image = Image.open("samples/chart.png").convert("RGB")
prompt = "USER: <image>\n이 차트의 핵심 추세를 한 문장으로 요약하세요.\nASSISTANT:"

inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device)
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=128, do_sample=False)
print(processor.decode(output[0], skip_special_tokens=True))
```

`<image>` 토큰이 visual prefix가 들어갈 자리를 잡아주고, processor가 자동으로 image feature를 끼워 넣습니다.

## 흔히 놓치는 함정 다섯 가지

### 1. visual token이 LLM context를 잠식

LLaVA는 image 한 장에 576 token을 씁니다. context 4096짜리 모델이라면 system prompt와 question을 빼고 남는 용량이 빠르게 줄어듭니다. multi-turn conversation에서는 한 번에 1~2장만 유지하는 정책을 둡니다.

### 2. instruction tuning data 품질이 결과를 좌우

LLaVA의 핵심 비밀은 GPT-4가 만든 158K instruction dataset입니다. 자체 fine-tuning을 한다면 instruction data 품질이 모델 capability의 상한을 정합니다. low-quality instruction은 hallucination을 키웁니다.

### 3. fine-tuning 시 vision encoder를 같이 unfreeze

LLaVA-1.5는 vision encoder를 frozen으로 두는 게 기본입니다. 같이 학습하면 catastrophic forgetting으로 zero-shot 일반화가 무너집니다. 도메인 특화 fine-tuning이라도 처음에는 projection만 학습합니다.

### 4. 다국어에 약한 base LLM

LLaVA-1.5의 base LLM은 Vicuna(LLaMA)입니다. 한국어 reasoning이 약합니다. 한국어 multimodal이 필요하면 KoLLaVA, Qwen2-VL, InternVL2처럼 다국어가 강한 base를 선택합니다.

### 5. evaluation을 단일 benchmark로만 검증

VLM은 OCR, chart, diagram, real-world photo, document 등 task spectrum이 넓습니다. MMMU, ChartQA, DocVQA, TextVQA, RealWorldQA를 함께 봐야 모델의 약점이 보입니다.

## 핵심 요약

- VLM은 vision encoder + adapter + LLM 구조이며, adapter 설계로 학파가 갈립니다.
- LLaVA: MLP projection. 단순하고 학습 쉬움. open source 시작점.
- BLIP-2: Q-Former로 visual token을 32개로 압축. multi-image에 효율적.
- Flamingo: LLM 안에 gated cross-attention 삽입. 가장 자연스러운 multi-image/video 처리.
- 실무 진입점은 LLaVA. 다국어가 필요하면 Qwen2-VL이나 InternVL2를 검토.
- visual token context 부담, instruction data 품질, vision encoder freeze 정책, 다국어 base 선택, 다중 benchmark 평가는 production 도입 전에 점검.

---

<!-- toc:begin -->
## 시니어 엔지니어는 이렇게 생각합니다

- **세 가지 패턴** — Cross-attention, projector, Q-Former 패턴별 장단점을 비교합니다.
- **Projector가 핵심** — 이미지 토큰을 LLM 토큰 공간으로 투영하는 층이 품질을 결정합니다.
- **토큰 예산 관리** — 이미지당 토큰 수가 컨텍스트와 비용을 잠식하지 않도록 설계합니다.
- **학습 데이터 품질** — 캡션 품질이 모델 행동을 좌우하므로 평가 시 데이터까지 의심합니다.
- **오픈 vs 클로즈드** — 재현성과 비용은 오픈, 품질·안정성은 클로즈드라는 트레이드오프를 명시합니다.

## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- **Vision-Language Model 아키텍처 (현재 글)**
- Image Captioning과 OCR 파이프라인 (예정)
- Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (예정)
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 텍스트에서 이미지 생성 (예정)
- Multimodal Embedding과 cross-modal 검색 (예정)
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Liu et al. - Visual Instruction Tuning (LLaVA)](https://arxiv.org/abs/2304.08485)
- [Li et al. - BLIP-2: Bootstrapping Language-Image Pre-training](https://arxiv.org/abs/2301.12597)
- [Alayrac et al. - Flamingo: a Visual Language Model for Few-Shot Learning](https://arxiv.org/abs/2204.14198)
- [HuggingFace - LLaVA model docs](https://huggingface.co/docs/transformers/model_doc/llava)

Tags: VLM, LLaVA, Cross-Attention, Q-Former, BLIP-2, Multimodal Fusion
