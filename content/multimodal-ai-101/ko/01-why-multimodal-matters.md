---
title: "Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유"
series: multimodal-ai-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Multimodal AI
- CLIP
- GPT-4V
- Flamingo
- Vision Language
- Modality Fusion
last_reviewed: '2026-05-14'
seo_description: ChatGPT가 등장한 2022년 말 이후, "LLM 하나면 거의 모든 문제가 풀린다"는 인식이 잠깐 자리잡았습니다.
---

# Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유

ChatGPT가 대중화된 뒤 한동안은 텍스트 LLM 하나만 잘 붙이면 대부분의 업무가 해결될 것처럼 보였습니다. 초기 프로토타입 단계에서는 실제로 그 가정이 꽤 잘 맞았습니다. 하지만 사용자가 실제로 보내는 입력은 곧 텍스트를 벗어났습니다. 영수증 사진, 차트 캡처, 오류 화면, 스캔 PDF처럼 의미의 절반이 시각 정보 안에 들어 있는 입력이 기본값이 됐습니다.

이 글은 Multimodal AI 101 시리즈의 첫 번째 글입니다.

이 지점에서 팀은 두 가지 선택을 하게 됩니다. 이미지에서 텍스트만 억지로 뽑아 기존 파이프라인에 밀어 넣거나, 처음부터 텍스트와 시각 신호를 함께 다루는 모델로 문제를 다시 정의하는 것입니다. 전자는 빨리 붙일 수 있지만 레이아웃, 색상, 시각적 관계, 누락된 맥락을 계속 잃습니다. 후자는 설계가 조금 더 무겁지만, 한 번 멘탈 모델을 제대로 잡아 두면 이후의 검색·추출·분류·생성 문제를 훨씬 일관되게 다룰 수 있습니다.

실무에서는 정확도보다 먼저 운영 경계가 바뀝니다. 이미지 한 장이 곧 토큰 비용으로 바뀌고, 해상도 전처리가 품질 문제로 바뀌며, 텍스트와 이미지가 충돌할 때 어느 쪽을 신뢰할지 정책 문제가 생깁니다. 그래서 멀티모달은 단순히 입력 종류를 늘리는 기능이 아니라, 추론 비용과 검증 전략을 다시 설계하게 만드는 아키텍처 변화에 가깝습니다.

이 글은 그 출발점에서 필요한 감각을 정리합니다. 왜 멀티모달이 필요한지, 어떤 구조로 작동하는지, 그리고 도입 전에 무엇을 먼저 의심해야 하는지를 초반에 단단히 잡아 두면 이후 9편의 세부 주제를 훨씬 덜 헤매고 따라갈 수 있습니다.

먼저 문제의 크기를 현실적으로 보고, 그다음에 모델과 파이프라인을 선택하는 순서가 중요합니다.

![Multimodal AI 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/01/01-01-mental-model-multimodal-expands-the-reas.ko.png)
*Multimodal AI 101 1장 흐름 개요*
> Multimodal AI가 중요한 이유의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 텍스트 LLM만으로는 왜 문서 QA, 시각 검색, 화면 이해 문제에서 한계가 빠르게 드러날까요?
- 멀티모달 시스템은 어떤 종류의 업무에서 기존 OCR + 규칙 기반 파이프라인보다 강한가요?
- 여러 modality를 결합하는 early fusion, late fusion, hybrid fusion은 무엇이 다를까요?

## 왜 이 글이 중요한가

멀티모달은 더 화려한 데모를 만들기 위한 기술이 아닙니다. 문서, 이미지, 차트, 영상처럼 실제 업무에서 이미 섞여 들어오는 입력을 모델이 있는 그대로 처리하게 만드는 기본 인프라입니다. 텍스트만 남기고 나머지를 버리는 설계는 이제 예외 처리에 가깝습니다.

특히 엔지니어링 조직에서는 입력 변환 비용이 크게 줄어듭니다. 예전에는 OCR, 레이아웃 분석, 룰 기반 파싱, 후처리기를 여러 단계로 붙여야 했던 작업을 하나의 시각-언어 호출로 시작할 수 있기 때문입니다. 이 단순화는 구현 속도뿐 아니라 장애 지점 수를 줄인다는 점에서도 중요합니다.

반대로 준비 없이 도입하면 비용과 품질이 동시에 흔들립니다. 이미지 토큰은 비싸고, 벤치마크는 텍스트 평가와 분리되어야 하며, 개인정보 필터는 이미지 쪽에서 다시 설계해야 합니다. 초반에 올바른 멘탈 모델을 잡는 이유가 여기에 있습니다.

## 핵심 관점

멀티모달을 “이미지도 받는 LLM” 정도로 이해하면 곧바로 세부 구현으로 빠집니다. 더 좋은 출발점은 추론 경계가 어디까지 확장되는지 보는 것입니다. 텍스트 전용 시스템은 사용자가 미리 정리한 의미만 읽습니다. 반면 멀티모달 시스템은 정리되기 전의 원본 신호, 즉 화면 배치와 시각 단서까지 추론 대상에 포함합니다.

이 관점으로 보면 OCR, 분류, 검색, 요약이 따로 떨어진 문제가 아니라는 사실이 보입니다. 핵심은 서로 다른 입력을 같은 표현 공간으로 가져와 최종 판단을 한 모델 또는 한 파이프라인 안에서 내리게 만드는 것입니다. 그래서 CLIP의 공통 임베딩 공간과 GPT-4o Vision의 단일 호출 예제가 같은 흐름 위에 놓입니다.

현업에서 중요한 차이도 여기서 생깁니다. 단순히 입력 타입이 늘어난 것이 아니라 검증 대상이 바뀌었기 때문에, 비용 계측·충돌 정책·PII 필터·해상도 정책이 모두 재설계 대상이 됩니다. 멀티모달을 기능 추가가 아니라 시스템 경계 확장으로 보면 어떤 체크리스트를 먼저 세워야 하는지가 자연스럽게 정리됩니다.

> 멀티모달의 핵심은 이미지를 읽는 능력 자체가 아니라, 텍스트로 환원되기 전에 존재하던 정보를 추론 경로 안으로 다시 가져오는 데 있습니다.

## 핵심 개념

### "텍스트 LLM만으로는 왜 부족한가요?"

ChatGPT가 등장한 2022년 말 이후, "LLM 하나면 거의 모든 문제가 풀린다"는 인식이 잠깐 자리잡았습니다. 그런데 GPT-4V(Vision)가 2023년 9월 공개되고 Gemini, Claude 3 Opus가 vision modality를 기본 기능으로 내놓으면서 분위기가 바뀌었습니다. 사용자들은 더 이상 텍스트만 입력하지 않습니다. 스크린샷을 붙여넣고, 차트 이미지를 던지고, PDF를 통째로 올립니다.

실무에서 multimodal이 텍스트-only를 이기는 지점은 명확합니다. 영수증 OCR + 카테고리 분류, 제품 이미지 + 설명 결합 검색, 의료 영상 + 환자 기록 통합 진단, 코드 스크린샷 + 에러 메시지 디버깅 같은 작업은 single modality로는 정확도가 한참 떨어집니다.

이 시리즈는 multimodal AI를 production에 도입하려는 엔지니어를 대상으로 합니다. 1편에서는 왜 multimodal이 필요한지, 핵심 아키텍처 흐름은 무엇인지, 그리고 실무 도입 전에 알아야 할 다섯 가지 함정을 다룹니다.

### Multimodal AI가 풀 수 있는 문제 유형

| 작업 유형 | 텍스트-only 한계 | Multimodal 해결 방식 |
| --- | --- | --- |
| Document QA | 표·그림 정보 손실 | VLM이 layout과 figure를 함께 이해 |
| 시각적 검색 | 키워드 부정확 | CLIP embedding으로 image-text cross-search |
| 화면 자동화 | DOM 의존 | screenshot 기반 visual grounding |
| 콘텐츠 moderation | 텍스트 우회 가능 | image + text 통합 분류 |
| 의료·산업 영상 | 도메인 지식 필요 | image encoder + LLM reasoning |

각 영역에 특화된 모델이 따로 있던 시대(예: ResNet 분류, OCR 엔진, image captioning 모델)에서, 하나의 VLM(Vision-Language Model)이 모두 처리하는 시대로 빠르게 이동하고 있습니다.

### Modality Fusion의 세 가지 기본 패턴

multimodal 모델 설계는 결국 "서로 다른 modality를 어떻게 같은 representation space에 올릴 것인가"의 문제입니다. 크게 세 가지 패턴이 있습니다.

1. **Early fusion**: raw 입력을 합쳐서 모델에 넣습니다. 단순하지만 modality별 특성을 살리기 어렵습니다.
2. **Late fusion**: modality별로 따로 인코딩한 뒤, 마지막 layer에서 결합합니다. 구현은 쉽지만 cross-modal interaction이 약합니다.
3. **Hybrid (cross-attention) fusion**: image encoder와 language model 사이에 cross-attention을 두고, 단계별로 정보를 교환합니다. CLIP, BLIP-2, LLaVA, Flamingo가 모두 이 계열입니다.

다음 다이어그램이 hybrid fusion의 전형적인 흐름입니다.

```text
[Image] -> Vision Encoder (ViT) -> visual tokens
                                        |
                                        v
[Text]  -> Tokenizer -> text tokens -> LLM (cross-attention) -> output
```

핵심은 비전 인코더가 출력한 시각 토큰을 LLM이 추가 텍스트 토큰처럼 처리한다는 사실입니다. 그래서 LLaVA류 모델은 GPT-4V에 가까운 추론 능력을 보여 주면서도, 기반 LLM 학습은 거의 그대로 유지할 수 있습니다.

### 첫 multimodal 호출: GPT-4V로 영수증 분석

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
                        "Extract each item name and price from this receipt "
                        "and return a JSON array. "
                        'Format: [{"item": "...", "price": 0}]'
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

### CLIP으로 cross-modal 검색 미리 보기

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

# 이미지-텍스트 유사성 행렬(x 이미지 쿼리)
logits = out.logits_per_text
probs = logits.softmax(dim=-1)
print(probs)
```

production에서는 image embedding을 미리 FAISS index에 넣어두고, 사용자 query를 CLIP text encoder에 통과시켜 nearest image를 찾는 구조를 자주 씁니다. 이 패턴은 5편(Multimodal RAG)에서 자세히 다룹니다.

### 어떤 문제를 먼저 멀티모달로 옮길 것인가

멀티모달 도입은 모든 입력 경로를 한 번에 바꾸는 프로젝트가 아닙니다. 가장 먼저 옮길 대상은 이미 사람이 눈으로 보고 판단하고 있는 업무입니다. 영수증 검수, 상품 이미지 검색, 스크린샷 기반 지원처럼 사람이 시각 단서를 읽고 텍스트 판단을 덧붙이는 문제는 ROI가 빠르게 나옵니다.

반대로 이미지가 사실상 장식이고 최종 판단이 거의 텍스트만으로 끝나는 업무라면 굳이 초기에 멀티모달을 붙일 필요가 없습니다. 비용과 복잡도만 늘고 품질 이득은 작을 수 있습니다. 그래서 도입 순서는 모델 유행이 아니라 입력 구조를 기준으로 정하는 편이 안전합니다.

현업에서는 보통 세 가지 질문으로 선별합니다. 첫째, 현재 사람이 이미지를 먼저 보고 판단하는가. 둘째, OCR만으로는 자주 놓치는 정보가 있는가. 셋째, 이미지와 텍스트를 함께 볼 때만 정확도가 올라가는가. 이 세 질문에 모두 예라고 답할 수 있으면 멀티모달 우선순위가 높습니다.

### 도입 순서를 잘못 잡으면 생기는 일

멀티모달을 붙인다고 해서 곧바로 전체 시스템이 좋아지지는 않습니다. 준비 없이 vision 호출부터 늘리면 가장 먼저 드러나는 것은 비용 폭증입니다. 그다음은 평가 공백입니다. 기존 텍스트 벤치마크는 통과하는데 실제 문서 이미지 질의에서만 계속 실패하는 상황이 반복됩니다.

또 하나 자주 보는 문제는 책임 경계가 흐려지는 것입니다. OCR이 할 일, captioner가 할 일, VLM이 최종 판단할 일을 나누지 않으면 모든 문제를 큰 모델 하나로 밀어 넣게 됩니다. 처음에는 편하지만, 장애가 나면 어디서 품질이 무너졌는지 설명하기 어려워집니다.

그래서 초기에 해야 할 일은 모델 추가보다 입력 정책 정의입니다. 허용 해상도, 비용 상한, PII 필터, 충돌 해결 규칙, 평가셋 범위를 먼저 정해 두면 이후의 모델 선택이 훨씬 단순해집니다.

### 팀이 합의해야 할 운영 정책

멀티모달 시스템은 모델 선택보다 정책 선택이 더 오래 갑니다. 예를 들어 이미지와 사용자 텍스트가 충돌할 때 무엇을 진실로 볼지, 고해상도 이미지를 언제 리사이즈할지, 원본 이미지를 어디까지 저장할지 같은 질문은 제품 전체의 기본 규칙이 됩니다.

이 정책은 프롬프트 한 줄로 끝나지 않습니다. 업로드 레이어, 전처리 레이어, 추론 레이어, 감사 로그 레이어가 모두 같은 결정을 따라야 합니다. 특히 개인정보와 보안 규칙은 모델 앞단에서 먼저 막는 편이 훨씬 안전합니다.

멀티모달을 일찍 도입해도 운영 정책이 늦으면 결국 사람 검수에 계속 기대게 됩니다. 반대로 정책이 먼저 서면, 모델은 조금씩 교체해도 시스템 전체 동작은 안정적으로 유지됩니다.

### 멀티모달 도입 전 데이터 준비 기준

기술 검토만큼 중요한 것이 입력 자산 정리입니다. 영수증, 계약서 스캔본, 화면 캡처, 제품 이미지처럼 실제로 들어올 파일 유형을 먼저 모아 두지 않으면 모델 비교가 전부 감에 의존하게 됩니다. 멀티모달은 synthetic 예제보다 실제 샘플 편차의 영향을 훨씬 크게 받습니다.

여기서 특히 봐야 할 것은 해상도 분포와 노이즈 패턴입니다. 흐린 촬영, 잘린 문서, 압축 artifacts, 회전된 사진, 일부만 보이는 스크린샷은 데모 환경보다 production 환경에서 훨씬 자주 등장합니다. 이 데이터 현실을 먼저 봐야 어떤 전처리와 어떤 평가셋이 필요한지 감이 생깁니다.

좋은 팀은 모델 PoC보다 먼저 입력 카탈로그를 만듭니다. 어떤 입력 유형이 있고, 현재는 사람이 어떻게 해석하고 있으며, 어떤 실패가 자주 나오는지 적어 두면 멀티모달 도입 우선순위가 훨씬 명확해집니다.

### 작은 성공 사례를 먼저 만드는 방법

멀티모달은 한 번에 크게 붙일수록 실패 비용이 커집니다. 그래서 가장 좋은 출발점은 정답 형식이 비교적 명확하고, 사람이 눈으로 이미 검수하던 업무를 고르는 것입니다. 영수증 품목 추출, 화면 캡처 분류, 상품 이미지 매칭 같은 작업이 대표적입니다.

이런 문제는 효과 측정도 쉽습니다. 기존 수작업 시간, OCR-only 대비 정확도, 재처리 비율, 이미지 토큰당 비용을 함께 보면 멀티모달의 실질 가치를 설명하기가 수월합니다. 조직 설득은 대개 이 첫 번째 성공 사례의 품질에 달려 있습니다.

멀티모달 전략은 거창한 비전보다, 작지만 측정 가능한 문제 하나를 제대로 푸는 데서 시작하는 편이 훨씬 오래 갑니다.

### 멀티모달과 기존 시스템의 역할 분담

현실적으로는 멀티모달이 기존 OCR, 규칙 엔진, 검색 시스템을 모두 즉시 대체하지는 않습니다. 오히려 좋은 구조는 기존 강점을 유지하면서, 시각 정보가 빠질 때 생기던 손실만 멀티모달로 메우는 방식에 가깝습니다.

예를 들어 정밀 숫자 추출은 여전히 전용 OCR이 더 안정적일 수 있고, 최종 설명이나 충돌 해석은 VLM이 더 잘할 수 있습니다. 이런 역할 분담을 인정하면 시스템 설계가 훨씬 현실적이 됩니다.

결국 멀티모달의 첫 승리는 모든 것을 바꾸는 데서 나오지 않습니다. 기존 시스템이 보지 못하던 신호를 하나씩 복구하면서, 전체 파이프라인의 손실을 줄이는 데서 시작됩니다.

### 해상도 전처리 기준

멀티모달은 모델 선택만큼 입력 준비가 중요합니다. 아래 보조 코드는 VLM 호출 전에 해상도와 크기를 안정적으로 맞출 때 바로 쓸 수 있는 기본 예제입니다.

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

**예상 결과:** 이 전처리 함수는 긴 변이 `max_side`를 넘는 이미지를 축소하되, 이미 충분히 작은 이미지는 그대로 유지해야 합니다. 전처리 뒤에도 비용이 급격히 튄다면 원본 업로드 경로에서 EXIF 회전, PNG 압축률, 중복 재인코딩 여부를 먼저 확인하는 편이 빠릅니다.

### 도입 전에 먼저 만들어야 하는 검증 세트

멀티모달 도입은 모델 선택보다 샘플 정리가 더 먼저입니다. 영수증, 계약서 스캔, 차트 캡처, 제품 이미지처럼 실제로 들어오는 입력 유형을 먼저 모아 두지 않으면 PoC가 지나치게 낙관적으로 보입니다. synthetic 예제는 거의 항상 실제 운영보다 깨끗합니다.

특히 다음 네 가지는 초반부터 따로 섞어 두는 편이 좋습니다.

- 정상 입력: 조명과 해상도가 양호한 대표 샘플
- 경계 입력: 잘리거나 흐리거나 회전된 이미지
- 충돌 입력: 사용자 텍스트와 이미지 내용이 어긋나는 사례
- 개인정보 입력: 명함, 영수증, 신분증처럼 PII가 섞인 사례

이 네 묶음이 있어야 모델이 좋아졌는지, 아니면 단지 쉬운 샘플만 잘 맞는지를 구분할 수 있습니다.
## 흔히 헷갈리는 지점

- **token 비용이 텍스트보다 훨씬 비싸다** GPT-4o vision은 image 한 장이 보통 765~2000 token을 차지합니다. 1280x1280 고해상도는 한 번 호출에 수천 token이 들어갑니다. cost dashboard에 image token line item을 따로 두지 않으면 비용이 어디서 새는지 못 잡습니다.
- **resolution 전처리를 하지 않으면 정확도가 떨어진다** VLM마다 권장 입력 해상도가 다릅니다. CLIP은 224x224, GPT-4V는 768x768 또는 1024x2048 분할입니다. 원본 4K 이미지를 그대로 보내면 모델이 detail을 놓치거나 비용만 폭증합니다.
- **text-only 평가 셋으로는 multimodal 성능을 못 잡는다** 기존 텍스트 QA benchmark만 돌려서는 vision capability가 안 보입니다. MMMU, ChartQA, DocVQA 같은 multimodal benchmark를 따로 준비해야 합니다.
- **modality 간 정보 충돌 처리가 없다** 이미지와 텍스트가 서로 다른 정보를 담는 경우가 많습니다. "이 영수증은 5만원짜리"라는 사용자 텍스트와 영수증 이미지의 7만원이 충돌할 때, 어느 쪽을 신뢰할지 정책이 필요합니다. system prompt에 명시적 우선순위를 넣어야 안전합니다.
- **PII가 이미지에 그대로 노출된다** 이미지에 신분증, 명함, 화면 캡처 속 메일 주소가 들어있으면 텍스트 수준 PII 필터로는 못 잡습니다. multimodal 시스템은 image-side PII detection (예: Tesseract OCR -> regex, AWS Rekognition Face)을 따로 둬야 합니다.

## 운영 체크리스트

- [ ] 이미지 토큰 비용을 텍스트 비용과 분리해 계측하고 있는가
- [ ] 모델별 권장 해상도와 리사이즈 정책을 문서화했는가
- [ ] 텍스트 벤치마크와 별도로 DocVQA·ChartQA·MMMU 같은 평가 셋을 갖췄는가
- [ ] 텍스트와 이미지가 충돌할 때 우선순위 정책을 프롬프트와 코드 양쪽에 명시했는가
- [ ] OCR·얼굴·식별자 검출을 포함한 이미지 측 PII 필터 단계를 따로 두었는가

## 정리

멀티모달 AI가 중요한 이유는 입력을 하나 더 받기 때문이 아닙니다. 실제 업무 데이터의 상당수가 원래부터 문서, 표, 차트, 스크린샷, 사진처럼 복합 신호였고, 이제 모델이 그 복합성을 직접 다룰 수 있게 되었기 때문입니다.

이 글에서 본 fusion 패턴, GPT-4o Vision 호출, CLIP 기반 cross-modal 검색은 이후 시리즈 전체의 공통 뼈대입니다. 뒤의 글들은 이 뼈대를 각각 image encoder, VLM adapter, OCR 파이프라인, RAG, production 운영으로 세분화합니다.

초반에 꼭 가져가야 할 감각은 단 하나입니다. 멀티모달을 붙이는 순간 비용, 평가, 정책, 개인정보 처리까지 함께 설계해야 한다는 사실입니다. 그 현실을 먼저 받아들이면 기술 선택이 훨씬 안정적이 됩니다.

## 처음 질문으로 돌아가기

- **텍스트 LLM만으로는 왜 문서 QA, 시각 검색, 화면 이해 문제에서 한계가 빠르게 드러날까요?**
  - 텍스트 LLM은 사용자가 이미 정리해 준 문자열만 읽기 때문에 표·그림·레이아웃이 중요한 문서 QA나 스크린샷 이해에서 원본 신호를 잃기 쉽습니다. 본문에서 본 영수증 분석 코드처럼 `image_url`을 함께 보내야 OCR, parsing, 구조화가 한 번에 일어나고, CLIP 예제처럼 공통 임베딩 공간이 있어야 텍스트로 이미지를 찾을 수 있습니다.
- **멀티모달 시스템은 어떤 종류의 업무에서 기존 OCR + 규칙 기반 파이프라인보다 강한가요?**
  - 사람이 먼저 이미지를 보고 판단한 뒤 텍스트 해석을 덧붙이는 업무에서 특히 강합니다. 글에서 예로 든 영수증 품목 추출, 제품 이미지 검색, 스크린샷 기반 지원, 의료 영상과 기록 결합 같은 문제는 OCR 문자열만으로는 빠지는 맥락을 VLM과 CLIP 기반 검색이 함께 복구해 줍니다.
- **여러 modality를 결합하는 early fusion, late fusion, hybrid fusion은 무엇이 다를까요?**
  - early fusion은 raw 입력을 처음부터 함께 넣어 단순하지만 modality별 특성을 잃기 쉽고, late fusion은 마지막에 합쳐 구현은 쉽지만 상호작용이 약합니다. hybrid fusion은 본문 도식처럼 ViT가 만든 visual tokens를 LLM이 cross-attention으로 읽게 해 CLIP·BLIP-2·LLaVA·Flamingo 계열의 핵심 구조를 만듭니다.

<!-- toc:begin -->
## 시리즈 목차

- **Multimodal AI가 중요한 이유 (현재 글)**
- Image Encoder: CLIP과 ViT (예정)
- Vision-Language Model 아키텍처 (예정)
- Image Captioning과 OCR 파이프라인 (예정)
- Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (예정)
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 Text-to-Image 생성 (예정)
- Multimodal Embedding과 Cross-modal 검색 (예정)
- Video 이해 - Frame Sampling에서 Video-LLaVA까지 (예정)
- Production Multimodal Application 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OpenAI 이미지 입력 가이드](https://platform.openai.com/docs/guides/images)
- [Anthropic Claude Vision 문서](https://docs.anthropic.com/en/docs/build-with-claude/vision)
- [Google Gemini Vision 문서](https://ai.google.dev/gemini-api/docs/vision)

### 논문과 시스템 참고 자료

- [OpenAI - GPT-4V(ision) System Card](https://openai.com/index/gpt-4v-system-card/)
- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [Alayrac et al. - Flamingo: a Visual Language Model for Few-Shot Learning](https://arxiv.org/abs/2204.14198)
- [Liu et al. - Visual Instruction Tuning (LLaVA)](https://arxiv.org/abs/2304.08485)

### 관련 시리즈

- [Vector Search 101 - FAISS 입문](../../vector-search-101/ko/04-faiss-fundamentals.md)
- [LLM API 프로덕션 101 - 구조화 출력](../../llm-api-production-101/ko/01-structured-output.md)
- [문서 수집과 인덱싱 101 - 다중 포맷 문서 파이프라인](../../document-ingestion-101/ko/05-multi-format-pipeline.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/01-why-multimodal-matters)

Tags: Multimodal AI, CLIP, GPT-4V, Flamingo, Vision Language, Modality Fusion
