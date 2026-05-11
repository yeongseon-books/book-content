---
title: Multimodal AI가 중요한 이유
series: multimodal-ai-101
episode: 1
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Multimodal AI
- CLIP
- GPT-4V
- Flamingo
- Vision Language
- Modality Fusion
last_reviewed: '2026-05-03'
seo_description: ChatGPT가 등장한 2022년 말 이후, "LLM 하나면 거의 모든 문제가 풀린다"는 인식이 잠깐 자리잡았습니다.
---

# Multimodal AI가 중요한 이유

> Multimodal AI 101 시리즈 (1/10)

---


## "텍스트 LLM만으로는 왜 부족한가요?"

ChatGPT가 등장한 2022년 말 이후, "LLM 하나면 거의 모든 문제가 풀린다"는 인식이 잠깐 자리잡았습니다. 그런데 GPT-4V(Vision)가 2023년 9월 공개되고 Gemini, Claude 3 Opus가 vision modality를 기본 기능으로 내놓으면서 분위기가 바뀌었습니다. 사용자들은 더 이상 텍스트만 입력하지 않습니다. 스크린샷을 붙여넣고, 차트 이미지를 던지고, PDF를 통째로 올립니다.

실무에서 multimodal이 텍스트-only를 이기는 지점은 명확합니다. 영수증 OCR + 카테고리 분류, 제품 이미지 + 설명 결합 검색, 의료 영상 + 환자 기록 통합 진단, 코드 스크린샷 + 에러 메시지 디버깅 같은 작업은 single modality로는 정확도가 한참 떨어집니다.

이 시리즈는 multimodal AI를 production에 도입하려는 엔지니어를 대상으로 합니다. 1편에서는 왜 multimodal이 필요한지, 핵심 아키텍처 흐름은 무엇인지, 그리고 실무 도입 전에 알아야 할 다섯 가지 함정을 다룹니다.

## Multimodal AI가 풀 수 있는 문제 유형

| 작업 유형 | 텍스트-only 한계 | Multimodal 해결 방식 |
| --- | --- | --- |
| Document QA | 표·그림 정보 손실 | VLM이 layout과 figure를 함께 이해 |
| 시각적 검색 | 키워드 부정확 | CLIP embedding으로 image-text cross-search |
| 화면 자동화 | DOM 의존 | screenshot 기반 visual grounding |
| 콘텐츠 moderation | 텍스트 우회 가능 | image + text 통합 분류 |
| 의료·산업 영상 | 도메인 지식 필요 | image encoder + LLM reasoning |

각 영역에 특화된 모델이 따로 있던 시대(예: ResNet 분류, OCR 엔진, image captioning 모델)에서, 하나의 VLM(Vision-Language Model)이 모두 처리하는 시대로 빠르게 이동하고 있습니다.

## Modality Fusion의 세 가지 기본 패턴

multimodal 모델 설계는 결국 "서로 다른 modality를 어떻게 같은 representation space에 올릴 것인가"의 문제입니다. 크게 세 가지 패턴이 있습니다.

1. **Early fusion**: raw 입력을 합쳐서 모델에 넣습니다. 단순하지만 modality별 특성을 살리기 어렵습니다.
2. **Late fusion**: modality별로 따로 인코딩한 뒤, 마지막 layer에서 결합합니다. 구현은 쉽지만 cross-modal interaction이 약합니다.
3. **Hybrid (cross-attention) fusion**: image encoder와 language model 사이에 cross-attention을 두고, 단계별로 정보를 교환합니다. CLIP, BLIP-2, LLaVA, Flamingo가 모두 이 계열입니다.

다음 다이어그램이 hybrid fusion의 전형적인 흐름입니다.

```
[Image] -> Vision Encoder (ViT) -> visual tokens
                                        |
                                        v
[Text]  -> Tokenizer -> text tokens -> LLM (cross-attention) -> output
```

핵심은 vision encoder가 출력한 visual token을 LLM이 마치 추가 텍스트 토큰처럼 처리한다는 점입니다. 그래서 LLaVA류 모델은 GPT-4V 수준의 reasoning에 가까이 가면서도, base LLM 학습은 거의 그대로 유지할 수 있습니다.

## 첫 multimodal 호출: GPT-4V로 영수증 분석

가장 빠르게 multimodal 가치를 체감하는 방법은 OpenAI Vision API 한 번 호출입니다. 다음 코드는 영수증 이미지를 받아 항목과 금액을 JSON으로 추출합니다.

```python
import base64
from openai import OpenAI

client = OpenAI()

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_receipt(image_path: str) -> dict:
    b64 = encode_image(image_path)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "이 영수증에서 각 품목명과 금액을 추출해 "
                        "JSON 배열로 반환하세요. "
                        '형식: [{"item": "...", "price": 0}]'
                    )},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content

print(analyze_receipt("samples/receipt.jpg"))
```

text-only LLM이라면 사용자가 영수증을 직접 타이핑해서 넘겨야 합니다. multimodal 호출 한 번으로 OCR + parsing + 구조화가 동시에 끝납니다.

## CLIP으로 cross-modal 검색 미리 보기

CLIP(OpenAI, 2021)은 multimodal AI의 진입점이라고 불러도 좋습니다. image와 text를 같은 vector space에 넣어, "고양이 사진"이라는 텍스트로 고양이 이미지를 검색할 수 있습니다.

```python
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

images = [Image.open(p) for p in ["cat.jpg", "dog.jpg", "car.jpg"]]
queries = ["a photo of a cat", "a vehicle on the street"]

inputs = processor(text=queries, images=images,
                   return_tensors="pt", padding=True)

with torch.no_grad():
    out = model(**inputs)

# image-text similarity matrix (queries x images)
logits = out.logits_per_text
probs = logits.softmax(dim=-1)
print(probs)
```

production에서는 image embedding을 미리 FAISS index에 넣어두고, 사용자 query를 CLIP text encoder에 통과시켜 nearest image를 찾는 구조를 자주 씁니다. 이 패턴은 5편(Multimodal RAG)에서 자세히 다룹니다.

## 흔히 놓치는 함정 다섯 가지

### 1. token 비용이 텍스트보다 훨씬 비싸다

GPT-4o vision은 image 한 장이 보통 765~2000 token을 차지합니다. 1280x1280 고해상도는 한 번 호출에 수천 token이 들어갑니다. cost dashboard에 image token line item을 따로 두지 않으면 비용이 어디서 새는지 못 잡습니다.

### 2. resolution 전처리를 하지 않으면 정확도가 떨어진다

VLM마다 권장 입력 해상도가 다릅니다. CLIP은 224x224, GPT-4V는 768x768 또는 1024x2048 분할입니다. 원본 4K 이미지를 그대로 보내면 모델이 detail을 놓치거나 비용만 폭증합니다.

```python
from PIL import Image

def prepare_for_vlm(path: str, max_side: int = 1024) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = min(max_side / max(w, h), 1.0)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)),
                         Image.LANCZOS)
    return img
```

### 3. text-only 평가 셋으로는 multimodal 성능을 못 잡는다

기존 텍스트 QA benchmark만 돌려서는 vision capability가 안 보입니다. MMMU, ChartQA, DocVQA 같은 multimodal benchmark를 따로 준비해야 합니다.

### 4. modality 간 정보 충돌 처리가 없다

이미지와 텍스트가 서로 다른 정보를 담는 경우가 많습니다. "이 영수증은 5만원짜리"라는 사용자 텍스트와 영수증 이미지의 7만원이 충돌할 때, 어느 쪽을 신뢰할지 정책이 필요합니다. system prompt에 명시적 우선순위를 넣어야 안전합니다.

### 5. PII가 이미지에 그대로 노출된다

이미지에 신분증, 명함, 화면 캡처 속 메일 주소가 들어있으면 텍스트 수준 PII 필터로는 못 잡습니다. multimodal 시스템은 image-side PII detection (예: Tesseract OCR -> regex, AWS Rekognition Face)을 따로 둬야 합니다.

## 핵심 요약

- Multimodal AI는 텍스트 LLM이 풀지 못하던 document QA, 시각적 검색, 화면 자동화, 영상 분석 영역을 한 모델로 처리합니다.
- modality fusion 패턴은 early / late / hybrid (cross-attention) 셋이며, 현재 SOTA는 hybrid 계열입니다.
- GPT-4o vision API 한 번이면 OCR + parsing + 구조화가 끝납니다. CLIP은 cross-modal 검색의 진입점입니다.
- Image token 비용, 해상도 전처리, multimodal benchmark, modality 충돌 정책, image-side PII는 production 도입 전에 반드시 점검합니다.
- 다음 편(2편)부터는 image encoder의 핵심인 CLIP과 ViT 아키텍처를 깊이 다룹니다.

---

<!-- toc:begin -->
## Multimodal AI 101 시리즈

- **Multimodal AI가 중요한 이유 (현재 글)**
- Image Encoder: CLIP과 ViT (예정)
- Vision-Language Model 아키텍처 (예정)
- Image Captioning과 OCR 파이프라인 (예정)
- Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (예정)
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 텍스트에서 이미지 생성 (예정)
- Multimodal Embedding과 cross-modal 검색 (예정)
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [OpenAI - GPT-4V(ision) System Card](https://openai.com/index/gpt-4v-system-card/)
- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [Alayrac et al. - Flamingo: a Visual Language Model for Few-Shot Learning](https://arxiv.org/abs/2204.14198)
- [Liu et al. - Visual Instruction Tuning (LLaVA)](https://arxiv.org/abs/2304.08485)

Tags: Multimodal AI, CLIP, GPT-4V, Flamingo, Vision Language, Modality Fusion
