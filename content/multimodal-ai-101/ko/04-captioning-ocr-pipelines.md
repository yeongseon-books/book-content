---
title: "Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인"
series: multimodal-ai-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- OCR
- Image Captioning
- BLIP
- Tesseract
- PaddleOCR
- Document AI
last_reviewed: '2026-05-12'
seo_description: production multimodal 시스템에서 가장 자주 나오는 질문 두 가지가 있습니다.
---

# Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인

문서 이미지나 화면 캡처를 다루는 팀에서 가장 흔한 오해는 “텍스트만 뽑아 오면 끝”이라는 생각입니다. 실제로는 반대인 경우가 많습니다. OCR은 문자열을 주지만, 표 구조와 시각적 강조, 이미지의 전반적 의미는 별도로 남아 있습니다. 반대로 captioning은 장면의 의미를 주지만, 작은 숫자와 주소 같은 정밀 텍스트는 놓치기 쉽습니다.

그래서 production 파이프라인에서는 captioning과 OCR을 경쟁 관계로 보지 않습니다. 둘은 서로 비어 있는 정보를 메워 주는 단계입니다. 문서 AI, 영수증 처리, UI 이해, 접근성 설명처럼 조금만 현실적인 문제로 가도 두 경로를 함께 설계해야 안정적인 결과가 나옵니다.

현업에서는 선택 기준도 단순하지 않습니다. Tesseract, PaddleOCR, 클라우드 Document AI, BLIP 계열 captioner, VLM 기반 description은 각각 강한 입력과 약한 입력이 다릅니다. 회전 이미지, 한국어, confidence threshold, PII 마스킹처럼 운영 포인트도 따로 챙겨야 합니다.

이 글에서는 image captioning과 OCR을 따로 소개한 뒤, 둘을 하나의 hybrid pipeline으로 묶을 때 어떤 구조가 가장 실용적인지 정리합니다.

문제는 텍스트를 뽑는 데서 끝나지 않고, 어떤 정보를 어느 단계에서 맡길지 분배하는 데서 시작됩니다.

![Multimodal AI 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/04/04-01-big-picture.ko.png)
*Multimodal AI 101 4장 흐름 개요*
> Image Captioning과 OCR 파이프라인의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 왜 “이미지에서 텍스트만 추출하면 된다”는 접근이 실제 문서 처리에서는 자주 실패할까요?
- Captioning 모델과 VLM 기반 설명 생성은 어떤 입력에서 각각 강점과 한계를 보일까요?
- Tesseract, PaddleOCR, Document AI 계열은 어떤 기준으로 선택해야 할까요?

## 왜 이 글이 중요한가

문서와 화면 이해 문제는 멀티모달 시스템이 가장 빨리 가치를 내는 영역입니다. 사용자가 실제로 보내는 파일 대부분이 스캔 문서, 스크린샷, 영수증, 표 이미지 형태이기 때문입니다. 이 영역을 잘 처리하면 검색, 추출, 요약, 분류가 동시에 좋아집니다.

또한 captioning과 OCR은 서로의 실패를 보완합니다. OCR은 문자를 정확히 읽지만 장면 의미를 놓치고, captioning은 장면을 설명하지만 숫자·주소·표 셀처럼 정밀한 텍스트를 놓칩니다. 둘을 결합하면 추출과 설명을 한 파이프라인에서 모두 확보할 수 있습니다.

반대로 이 단계를 소홀히 하면 이후 RAG나 agent 단계에서 계속 품질이 낮은 입력을 소비하게 됩니다. 멀티모달 파이프라인의 성능은 생각보다 초반 ingestion 품질에 크게 좌우됩니다.

## 핵심 관점

OCR은 시각 입력을 문자열로 압축합니다. captioning은 시각 입력을 의미 요약으로 압축합니다. 둘 다 유용하지만, 서로 다른 종류의 정보를 버립니다. 그래서 둘 중 하나만 고르면 필연적으로 사각지대가 남습니다.

실무적으로 좋은 파이프라인은 먼저 OCR로 정밀 텍스트를 확보하고, captioning 또는 VLM description으로 장면 맥락과 레이아웃 의미를 덧붙입니다. 그다음 필요한 경우 규칙 기반 후처리나 structured extraction을 얹습니다. 이 순서가 가장 예측 가능하고 디버깅도 쉽습니다.

이 관점으로 접근하면 도구 선택도 더 명확해집니다. OCR 엔진은 문자 정확도와 언어 지원을 기준으로, captioner는 장면 요약 품질과 지연 시간을 기준으로 고르면 됩니다.

> 문서 이미지를 이해한다는 것은 문자를 읽는 일과 장면을 해석하는 일을 동시에 다루는 것입니다. 둘 중 하나만 잘해서는 production 품질이 오래 버티지 못합니다.

## 핵심 개념

### "이미지에서 텍스트만 뽑으면 끝 아닌가요?"

production multimodal 시스템에서 가장 자주 나오는 질문 두 가지가 있습니다.

1. "이 이미지에 무엇이 있는지 한 줄로 설명해 줘" (image captioning)
2. "이 이미지 안의 텍스트를 그대로 읽어 줘" (OCR)

VLM 한 번 호출이면 둘 다 풀린다고 생각하기 쉬운데, 실제로는 비용/지연/정확도 trade-off 때문에 captioning과 OCR을 분리해 다른 모델로 처리하는 경우가 많습니다. 이번 편은 그 두 파이프라인을 어떻게 설계하는지 다룹니다.

### Image Captioning: 두 가지 접근

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
# > 나무 바닥에 앉아 있는 갈색 개
print(caption("samples/dog.jpg", prompt="a photography of"))
# > 행복한 얼굴의 갈색 강아지 사진
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
                    "Describe this image as alt text for visually impaired users "
                    "in 150 characters or less. "
                    "Include the objects, the scene, and key numbers if a chart "
                    "or table is present."
                )},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
    )
    return resp.choices[0].message.content
```

선택 기준: caption이 "객체 인식 수준"이면 BLIP, "맥락과 추론 포함"이면 VLM.

### OCR: 무엇을 골라야 하나

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

textract = boto3.client("textract", region_name="us-east-1")

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

### OCR + VLM hybrid 파이프라인

실무에서 권장하는 패턴은 다음 5단계입니다.

```text
[Image]
   |
   v
1. Image preprocessing (deskew, denoise, rotation)
   |
   v
2. Fast OCR (PaddleOCR/Tesseract) -> raw text + bbox
   |
   v
3. Layout analysis (optional) -> sections, tables
   |
   v
4. VLM (optional) -> NL reasoning, ambiguous-text correction
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
                "The user gives you OCR-extracted text and a question. "
                "Answer while accounting for OCR errors."
            )},
            {"role": "user", "content": (
                f"OCR result:\n```\n{text_block}\n```\n\nQuestion: {question}"
            )},
        ],
    )
    return resp.choices[0].message.content

answer = extract_then_reason("samples/receipt.jpg",
                             "What is the total amount paid and the store name?")
print(answer)
```

이 hybrid는 cost를 90% 이상 줄이면서 VLM-only 대비 정확도를 거의 유지합니다.

### OCR 후처리와 질의 조립 예제

captioning과 OCR을 함께 쓸 때는 마지막 연결 코드가 생각보다 중요합니다. 아래 예제는 실제 질의 입력을 조립하는 방식을 보여 줍니다.

```python
from PIL import Image, ImageOps

def auto_rotate(path: str) -> Image.Image:
    img = Image.open(path)
    return ImageOps.exif_transpose(img)
```
## 이미지 전처리 단계가 OCR 품질을 좌우하는 이유

OCR 성능 문제의 상당수는 모델보다 입력 품질에서 발생합니다. 회전, 그림자, 저해상도, 압축 노이즈가 있는 입력은 고성능 엔진에서도 오류율이 크게 뛰기 때문에 전처리를 독립 단계로 두는 편이 안전합니다. 특히 문서 스캔과 모바일 촬영 이미지를 함께 받는 서비스라면 deskew와 대비 보정이 필수입니다.

```python
import cv2
import numpy as np

def preprocess_for_ocr(path: str) -> np.ndarray:
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 12, 7, 21)
    binarized = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    return binarized
```

전처리 결과를 바로 OCR에 넣기보다, 샘플링된 문서셋에서 문자 단위 CER(Character Error Rate)와 필드 단위 추출 정확도를 같이 측정해야 합니다. 운영에서 중요한 것은 문장을 그럴듯하게 읽는 능력보다 총액, 날짜, 계좌번호 같은 핵심 필드 오류를 줄이는 능력이기 때문입니다.

## Captioning + OCR 결과를 Vision API로 교차 검증

captioning과 OCR 결과가 충돌할 때 GPT-4V나 Claude를 심판기로 두면 오탐을 줄일 수 있습니다. 예를 들어 OCR은 "8"로 읽고 caption은 "3"이라고 서술하는 경우, 원본 이미지를 포함한 교차 질의를 통해 충돌을 정리할 수 있습니다.

```python
def build_validation_prompt(caption: str, ocr_text: str) -> str:
    return (
        "You are validating extracted information from a document image. "
        "Compare the caption summary and OCR text. "
        "Return a JSON object with fields: conflicts, corrected_values, confidence.

"
        f"caption:
{caption}

ocr:
{ocr_text}"
    )
```

이 교차 검증은 전량 실행이 아니라 "OCR confidence 평균 0.7 미만" 또는 "금액/날짜 필드 불일치" 같은 규칙에서만 호출하면 비용을 관리하기 쉽습니다.

## 필드 추출 품질을 높이는 구조화 후처리

OCR 결과를 그대로 LLM에 전달하면 동일한 문서에서도 출력 포맷이 흔들리기 쉽습니다. 먼저 정규식과 좌표 정보를 이용해 필드 후보를 구조화하고, 그 결과를 모델에 넘기는 편이 안정적입니다. 특히 금액, 날짜, 사업자번호처럼 포맷이 명확한 필드는 룰 기반이 LLM보다 더 신뢰할 수 있습니다.

```python
import re

amount_pattern = re.compile(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?")

def extract_amount_candidates(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        out.extend(amount_pattern.findall(line))
    return out
```

후처리 단계에서 "신뢰도 낮은 필드"만 Vision API 재검증 경로로 보내면 전체 비용을 크게 줄일 수 있습니다. 이 계층이 있으면 OCR 엔진을 바꿔도 상위 인터페이스를 거의 유지할 수 있습니다.

## 문서 유형별 파이프라인 분기 전략

OCR와 captioning을 항상 동일한 순서로 돌리면 불필요한 비용이 발생할 수 있습니다. 문서 유형을 먼저 분류하면 파이프라인을 더 효율적으로 운영할 수 있습니다. 예를 들어 영수증은 OCR 중심, 제품 사진은 caption 중심, 차트 이미지는 OCR+VLM 검증 중심으로 분기하는 방식입니다.

이 분기는 복잡한 분류기 없이도 해상도, 텍스트 밀도, 선분 패턴 같은 휴리스틱으로 시작할 수 있습니다. 중요한 점은 분기 이유와 결과를 로그로 남기는 것입니다. 그래야 어떤 경로가 품질과 비용에서 유리한지 주기적으로 조정할 수 있습니다.

```python
def route_document_path(text_density: float, has_table_lines: bool) -> str:
    if has_table_lines:
        return "ocr_plus_vlm"
    if text_density > 0.35:
        return "ocr_first"
    return "caption_first"
```

실무에서는 이 분기 정책 하나만으로 평균 지연 시간을 크게 줄일 수 있습니다. 동시에 고난도 문서를 별도 경로로 모아 품질 개선 루프를 돌리기 쉬워집니다.

## OCR 신뢰도 기반 재처리 큐

운영에서 가장 실용적인 패턴은 저신뢰 샘플만 재처리 큐로 보내는 것입니다. 전체 문서를 고성능 경로로 보내면 비용이 급격히 증가하므로, confidence와 필드 중요도를 함께 기준으로 두는 편이 좋습니다.

```python
def need_reprocess(avg_conf: float, has_amount: bool, has_date: bool) -> bool:
    if avg_conf < 0.72:
        return True
    if (not has_amount) or (not has_date):
        return True
    return False
```

이 재처리 큐는 사람 검수와도 연결하기 쉽습니다. 중요한 필드가 누락된 문서를 우선순위로 올리면 운영 효율이 높아집니다.

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

- **회전된 이미지 그대로 OCR** 스마트폰으로 찍은 영수증은 EXIF orientation 메타데이터를 가집니다. PIL은 자동 회전을 안 해주므로 명시적으로 처리해야 합니다.
- **한국어 모델 가중치 누락** Tesseract는 `kor.traineddata`, EasyOCR은 `["ko"]`, PaddleOCR은 `lang="korean"`로 명시해야 합니다. 영어 기본값으로 한국어 이미지를 돌리면 결과가 무의미합니다.
- **confidence threshold 무시** OCR 출력에는 항상 confidence가 따라옵니다. 0.6 미만은 제외하거나 별도 verification queue로 보내는 게 안전합니다. confidence를 무시하면 downstream LLM이 garbage를 reasoning합니다.
- **caption을 SEO/접근성에 그대로 사용** BLIP의 caption은 "a person sitting" 같이 짧고 generic합니다. alt text 기준(WCAG 1.1.1)이 요구하는 맥락이 부족합니다. SEO나 접근성에는 BLIP raw 결과를 후처리하거나 VLM을 따로 호출합니다.
- **PII가 caption/OCR 결과에 그대로 노출** 영수증의 카드번호, 명함의 전화번호, 여권 사진의 주민등록번호는 OCR로 다 읽힙니다. caption/OCR 결과에 PII filter를 한 번 더 거쳐야 합니다 (ai-data-preparation-101 4편 참고).

## 운영 체크리스트

- [ ] OCR 이전에 orientation correction과 해상도 정규화를 수행하는가
- [ ] 한국어·영문 등 실제 입력 언어에 맞는 OCR 가중치와 사전을 적용하는가
- [ ] confidence threshold와 human review fallback 기준을 수치로 정했는가
- [ ] caption과 OCR 결과를 합친 뒤 PII 마스킹 단계를 다시 수행하는가
- [ ] 문서 유형별로 OCR-only, caption-only, hybrid 경로를 분기하는가

## 정리

OCR과 captioning은 서로 대체재가 아니라 보완재입니다. OCR은 정밀 텍스트를, captioning은 장면 의미를 담당합니다. 현실적인 문서 파이프라인은 이 둘을 함께 설계할 때 가장 강해집니다.

도구 선택은 기술 취향보다 입력 특성에 맞춰야 합니다. 회전 문서, 한국어, 표 구조, 비용 제약 같은 운영 조건이 엔진 선택에 직접 영향을 줍니다.

이 글의 핵심은 hybrid pipeline 감각입니다. 이후 멀티모달 RAG와 production 앱에서도 결국 좋은 caption/OCR 산출물이 상위 단계의 검색과 생성 품질을 결정하게 됩니다.

## 처음 질문으로 돌아가기

- **왜 “이미지에서 텍스트만 추출하면 된다”는 접근이 실제 문서 처리에서는 자주 실패할까요?**
  - 본문의 기준은 Image Captioning과 OCR 파이프라인를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Captioning 모델과 VLM 기반 설명 생성은 어떤 입력에서 각각 강점과 한계를 보일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Tesseract, PaddleOCR, Document AI 계열은 어떤 기준으로 선택해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- **Image Captioning과 OCR 파이프라인 (현재 글)**
- Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (예정)
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 Text-to-Image 생성 (예정)
- Multimodal Embedding과 Cross-modal 검색 (예정)
- Video 이해 - Frame Sampling에서 Video-LLaVA까지 (예정)
- Production Multimodal Application 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Li et al. - BLIP: Bootstrapping Language-Image Pre-training](https://arxiv.org/abs/2201.12086)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [Tesseract OCR User Manual](https://tesseract-ocr.github.io/tessdoc/)
- [AWS Textract Developer Guide](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)

### 관련 시리즈

- [문서 수집과 인덱싱 101 - PDF 파싱과 텍스트 추출](../../document-ingestion-101/ko/01-pdf-parsing.md)
- [AI 앱 패턴 101 - 문서 어시스턴트](../../ai-app-patterns-101/ko/03-document-assistant.md)
- [문서 수집과 인덱싱 101 - 다중 포맷 문서 파이프라인](../../document-ingestion-101/ko/05-multi-format-pipeline.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/04-captioning-ocr-pipelines)

Tags: OCR, Image Captioning, BLIP, Tesseract, PaddleOCR, Document AI
