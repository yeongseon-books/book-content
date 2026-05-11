---
title: Image Captioning과 OCR 파이프라인
series: multimodal-ai-101
episode: 4
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- OCR
- Image Captioning
- BLIP
- Tesseract
- PaddleOCR
- Document AI
last_reviewed: '2026-05-03'
seo_description: production multimodal 시스템에서 가장 자주 나오는 질문 두 가지가 있습니다.
---

# Image Captioning과 OCR 파이프라인

> Multimodal AI 101 시리즈 (4/10)

---


## "이미지에서 텍스트만 뽑으면 끝 아닌가요?"

production multimodal 시스템에서 가장 자주 나오는 질문 두 가지가 있습니다.

1. "이 이미지에 무엇이 있는지 한 줄로 설명해 줘" (image captioning)
2. "이 이미지 안의 텍스트를 그대로 읽어 줘" (OCR)

VLM 한 번 호출이면 둘 다 풀린다고 생각하기 쉬운데, 실제로는 비용/지연/정확도 trade-off 때문에 captioning과 OCR을 분리해 다른 모델로 처리하는 경우가 많습니다. 이번 편은 그 두 파이프라인을 어떻게 설계하는지 다룹니다.

## Image Captioning: 두 가지 접근

### BLIP-style 전용 captioning 모델

BLIP, BLIP-2, GIT 같은 caption 전용 모델은 가볍고 빠릅니다. CPU에서도 초당 수 장을 처리하고, GPU에서는 수십 장을 batch로 돌릴 수 있습니다.

```python
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).eval()

def caption(img_path: str, prompt: str | None = None) -> str:
    img = Image.open(img_path).convert("RGB")
    if prompt:
        inputs = processor(img, prompt, return_tensors="pt")
    else:
        inputs = processor(img, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=50)
    return processor.decode(out[0], skip_special_tokens=True)

print(caption("samples/dog.jpg"))
# > a brown dog sitting on a wooden floor
print(caption("samples/dog.jpg", prompt="a photography of"))
# > a photography of a brown dog with a happy face
```

장점은 latency와 비용입니다. BLIP-base는 GPU에서 caption 1건당 50~100ms, OpenAI Vision API의 1/100 수준입니다. e-commerce 카탈로그 수백만 장 처리, log 분석 같은 대량 작업에 맞습니다.

### VLM 호출로 풍부한 caption

reasoning이 필요한 caption (예: "이 차트가 무슨 추세를 보여주는지 설명")은 BLIP 계열로는 어렵습니다. GPT-4o, Claude, Gemini 같은 VLM이 답입니다.

```python
from openai import OpenAI

client = OpenAI()

def rich_caption(image_url: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "이 이미지를 시각장애인 사용자를 위한 alt text로 "
                    "150자 이내 한국어로 설명해 주세요. "
                    "객체, 장면, 그리고 표나 차트가 있다면 핵심 수치를 포함합니다."
                )},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
    )
    return resp.choices[0].message.content
```

선택 기준: caption이 "객체 인식 수준"이면 BLIP, "맥락과 추론 포함"이면 VLM.

## OCR: 무엇을 골라야 하나

OCR 엔진은 크게 4가지 카테고리로 나뉩니다.

| 카테고리 | 대표 도구 | 강점 | 약점 |
| --- | --- | --- | --- |
| 전통 CV | Tesseract | 무료, 안정적, 영어 강함 | 손글씨, 회전, 곡선 약함 |
| Deep learning OSS | PaddleOCR, EasyOCR | 80+ 언어, layout 처리 | 모델 크기, GPU 권장 |
| Cloud API | AWS Textract, Google Vision, Azure | 표·서식 분석 우수 | 페이지당 비용, 데이터 외부 전송 |
| VLM | GPT-4o, Claude | 자연어 질의 가능, document QA | 토큰 비용, 정확도 변동 |

production에서는 보통 두 layer를 둡니다. **빠르고 저렴한 OCR로 raw text를 추출**한 뒤, **VLM은 reasoning이 필요한 단계에서만** 호출합니다.

### Tesseract: 가장 빠른 시작

```python
import pytesseract
from PIL import Image

def ocr_simple(img_path: str, lang: str = "kor+eng") -> str:
    img = Image.open(img_path)
    return pytesseract.image_to_string(img, lang=lang)

print(ocr_simple("samples/screenshot.png"))
```

한국어 인식이 필요하면 시스템에 `tesseract-ocr-kor` 데이터를 깔아야 합니다. CLI 한 번이면 되는 게 매력입니다.

### PaddleOCR: 한국어와 layout이 동시에 필요할 때

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang="korean")

def ocr_with_boxes(img_path: str) -> list[dict]:
    result = ocr.ocr(img_path, cls=True)
    rows = []
    for line in result[0]:
        bbox, (text, conf) = line
        rows.append({
            "text": text,
            "confidence": float(conf),
            "bbox": bbox,  # 4-point polygon
        })
    return rows

for r in ocr_with_boxes("samples/receipt.jpg")[:5]:
    print(f"[{r['confidence']:.2f}] {r['text']}")
```

bbox가 같이 나오기 때문에 영수증, 명함, 표 같은 layout-aware 작업에 강합니다.

### Cloud API: 표 구조 추출이 필요할 때

AWS Textract는 단순 OCR을 넘어 cells, key-value pairs, table을 구조화해 반환합니다. 송장, 보험 청구서 같은 정형 문서에 강합니다.

```python
import boto3

textract = boto3.client("textract", region_name="ap-northeast-2")

def extract_tables(img_path: str) -> list:
    with open(img_path, "rb") as f:
        resp = textract.analyze_document(
            Document={"Bytes": f.read()},
            FeatureTypes=["TABLES"],
        )
    tables = [b for b in resp["Blocks"] if b["BlockType"] == "TABLE"]
    return tables
```

비용은 페이지당 약 0.05~0.065 USD입니다. 월 100만 페이지 처리한다면 self-hosted PaddleOCR + 후처리가 더 쌉니다.

## OCR + VLM hybrid 파이프라인

실무에서 권장하는 패턴은 다음 5단계입니다.

```
[Image]
   |
   v
1. Image preprocessing (회전 보정, deskew, denoising)
   |
   v
2. Fast OCR (PaddleOCR/Tesseract) -> raw text + bbox
   |
   v
3. Layout 분석 (선택) -> sections, tables
   |
   v
4. VLM (선택) -> 자연어 reasoning, ambiguous text 보정
   |
   v
[Structured output]
```

다음 코드는 그 hybrid 흐름의 최소 구현입니다.

```python
from PIL import Image
from paddleocr import PaddleOCR
from openai import OpenAI

ocr = PaddleOCR(use_angle_cls=True, lang="korean")
client = OpenAI()

def extract_then_reason(img_path: str, question: str) -> str:
    raw = ocr.ocr(img_path, cls=True)[0]
    text_block = "\n".join(line[1][0] for line in raw)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "사용자가 OCR로 추출한 텍스트와 질문을 줍니다. "
                "OCR 오류를 감안해 답변하세요."
            )},
            {"role": "user", "content": (
                f"OCR 결과:\n```\n{text_block}\n```\n\n질문: {question}"
            )},
        ],
    )
    return resp.choices[0].message.content

answer = extract_then_reason("samples/receipt.jpg",
                             "총 결제 금액과 매장 이름을 알려줘.")
print(answer)
```

이 hybrid는 cost를 90% 이상 줄이면서 VLM-only 대비 정확도를 거의 유지합니다.

## 흔히 놓치는 함정 다섯 가지

### 1. 회전된 이미지 그대로 OCR

스마트폰으로 찍은 영수증은 EXIF orientation 메타데이터를 가집니다. PIL은 자동 회전을 안 해주므로 명시적으로 처리해야 합니다.

```python
from PIL import Image, ImageOps

def auto_rotate(path: str) -> Image.Image:
    img = Image.open(path)
    return ImageOps.exif_transpose(img)
```

### 2. 한국어 모델 가중치 누락

Tesseract는 `kor.traineddata`, EasyOCR은 `["ko"]`, PaddleOCR은 `lang="korean"`로 명시해야 합니다. 영어 기본값으로 한국어 이미지를 돌리면 결과가 무의미합니다.

### 3. confidence threshold 무시

OCR 출력에는 항상 confidence가 따라옵니다. 0.6 미만은 제외하거나 별도 verification queue로 보내는 게 안전합니다. confidence를 무시하면 downstream LLM이 garbage를 reasoning합니다.

### 4. caption을 SEO/접근성에 그대로 사용

BLIP의 caption은 "a person sitting" 같이 짧고 generic합니다. alt text 기준(WCAG 1.1.1)이 요구하는 맥락이 부족합니다. SEO나 접근성에는 BLIP raw 결과를 후처리하거나 VLM을 따로 호출합니다.

### 5. PII가 caption/OCR 결과에 그대로 노출

영수증의 카드번호, 명함의 전화번호, 여권 사진의 주민등록번호는 OCR로 다 읽힙니다. caption/OCR 결과에 PII filter를 한 번 더 거쳐야 합니다 (ai-data-preparation-101 4편 참고).

## 핵심 요약

- Image captioning은 빠른 BLIP 계열과 reasoning 강한 VLM 둘 다 필요합니다. 작업 성격에 따라 분리합니다.
- OCR은 Tesseract (간단), PaddleOCR (한국어+layout), Cloud API (표 구조), VLM (자연어 reasoning) 순서로 검토합니다.
- production에서는 fast OCR -> layout -> VLM의 hybrid 파이프라인이 cost와 정확도 모두 최선입니다.
- EXIF 회전, 한국어 모델 가중치, confidence threshold, alt text 후처리, PII 필터는 production 도입 전에 점검합니다.
- 다음 편(5편)에서는 OCR/caption 결과를 어떻게 vector DB에 인덱스해 multimodal RAG를 만드는지 다룹니다.

---

<!-- toc:begin -->
## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- **Image Captioning과 OCR 파이프라인 (현재 글)**
- Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (예정)
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 텍스트에서 이미지 생성 (예정)
- Multimodal Embedding과 cross-modal 검색 (예정)
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Li et al. - BLIP: Bootstrapping Language-Image Pre-training](https://arxiv.org/abs/2201.12086)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [Tesseract OCR User Manual](https://tesseract-ocr.github.io/tessdoc/)
- [AWS Textract Developer Guide](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)

Tags: OCR, Image Captioning, BLIP, Tesseract, PaddleOCR, Document AI
