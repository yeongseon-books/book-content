---
title: CLOVA OCR API로 문서 텍스트 추출
series: korean-ai-stack-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- CLOVA
- OCR
- NaverCloud
- DocumentAI
- Python
last_reviewed: '2026-05-12'
seo_description: 쓸 만한 OCR 결과는 평문이 아니라, 의미 있는 줄로 다시 조립한 구조화된 추출 결과입니다.
---

# CLOVA OCR API로 문서 텍스트 추출

한국어 검색과 RAG 파이프라인은 검색 단계보다 훨씬 앞에서 무너지는 경우가 많습니다. 시작점이 스캔 문서, 영수증, 휴대폰 사진인 경우가 많기 때문입니다. OCR이 의미 있는 한 줄을 잘못 쪼개면, 뒤의 임베딩과 랭킹도 그 손상을 그대로 물려받습니다.

이 글은 Korean AI Stack 101 시리즈의 4번째 글입니다. 여기서는 CLOVA OCR 응답을 줄 단위 텍스트로 재구성해, 검색 코퍼스에 안전하게 넣을 수 있는 형태로 만드는 과정을 다룹니다.

## 이 글에서 다룰 문제

- OCR을 붙일 때는 텍스트 정확도부터 봐야 할까요, 아니면 응답 구조부터 봐야 할까요?
- bounding box와 `lineBreak` 힌트는 후처리에서 왜 그렇게 중요할까요?
- 실제 API 키가 없어도 OCR 파이프라인의 대부분을 왜 검증할 수 있을까요?
- OCR 출력은 왜 임베딩이나 RAG 단계에 들어가기 전에 반드시 다시 정리되어야 할까요?

> 처음으로 쓸 만한 OCR 결과는 평문이 아닙니다. 의미 있는 줄로 다시 조립해야 하는 구조화된 추출 payload가 먼저 나옵니다.

> Korean AI Stack 101 (4/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/04-clova-ocr)

## 왜 이 단계가 중요한가

이 글은 한국어 문서 이미지, 영수증, 세금계산서, 스캔 양식을 CLOVA OCR API로 처리하고, 그 결과를 앞 글의 BGE-M3 코퍼스에 바로 넣을 수 있는 모양으로 정리합니다. 앞 글이 텍스트 코퍼스 검색을 다뤘다면, 이번 글은 그 텍스트를 처음 만들어 내는 단계입니다.

OCR을 별도 단계로 다뤄야 하는 이유는 명확합니다. 한국 기업 검색의 절반은 PDF, 스캔 이미지, 휴대폰 사진에서 시작합니다. OCR이 “공급가액 45,000원”을 “공급가액”과 “45,000원”으로 잘못 나누면, 의미 검색은 처음부터 실패합니다. CLOVA OCR은 한국어 토큰 인식 자체는 강한 편입니다. 진짜 일은 응답 JSON을 다시 줄, 문단, 표 셀로 조립하는 후처리에 있습니다. 이 글은 실제 키 없이도 그 로직을 검증할 수 있도록 번들된 mock 응답을 기본값으로 사용합니다.

## 멘탈 모델

OCR 파이프라인은 네 단계로 분해됩니다.

```text
[document image / PDF]
       |
       v
[CLOVA OCR API call]  --> JSON payload (fields, bbox, confidence, lineBreak)
       |
       v
[post-process: reconstruct lines / paragraphs / tables]  <-- format checks
       |
       v
[clean text + meta] --> BGE-M3 / RAG corpus
```

가장 중요한 것은 세 가지입니다.

- **API는 `fields` 배열만 돌려줍니다**: 줄바꿈, 문단, 표 구조는 `lineBreak`와 좌표를 바탕으로 직접 복원해야 합니다.
- **confidence는 진실이 아닙니다**: 0.99인 토큰도 틀릴 수 있고, 0.85인 토큰도 맞을 수 있습니다. 절대 임계값보다 분포를 보는 편이 낫습니다.
- **mock-first가 더 안전합니다**: 응답 JSON 형식은 키 없이도 코드 안에서 재현할 수 있으므로, CI에서 후처리를 결정적으로 검증할 수 있습니다.

추가로 두 가지를 더 기억하면 좋습니다.

- CLOVA OCR에는 두 갈래가 있습니다. General OCR은 자유 양식 문서용이고, Template OCR은 영수증이나 신분증처럼 구조가 고정된 문서용입니다.
- 각 field에는 `inferText`, `inferConfidence`, `boundingPoly`, `lineBreak`가 들어 있습니다. 이 글은 가장 자주 쓰는 `inferText` + `lineBreak` 조합에 집중합니다.

> 멘탈 모델을 짧게 말하면 이렇습니다. OCR API는 텍스트를 완성해서 주는 서비스가 아니라, 줄과 표를 다시 만들 재료를 구조화해 주는 서비스입니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| CLOVA OCR | NAVER Cloud Platform의 한국어 지향 OCR API |
| General OCR | 자유 양식 문서용. 좌표와 줄 메타데이터를 반환 |
| Template OCR | 영수증, ID처럼 고정 양식 문서용. 선언된 필드명에 자동 매핑 |
| `inferText` | 인식된 텍스트 토큰 |
| `inferConfidence` | 인식 confidence (0-1) |
| `boundingPoly` | 토큰의 4점 좌표 |
| `lineBreak` | 이 토큰이 한 줄을 닫는지 나타내는 불리언 |
| Mock response | API 호출 없이도 같은 응답 구조를 흉내 내는 코드 기반 JSON |

## Before vs. After

**Before** — raw payload를 그대로 인덱싱하면 각 `inferText` 토큰이 개별 조각으로 코퍼스에 들어갑니다. 검색은 “공급가액”과 “45,000원”을 별도 문서처럼 다뤄서 “공급가액 45,000원”이라는 의미 단위를 잃어버립니다.

**After** — 먼저 `lineBreak`를 따라 줄을 복원하면 코퍼스는 이렇게 바뀝니다.

```python
# Post-processed output (one line per document)
'공급가액 45,000원'      # confidence min: 0.994
'부가세 4,500원'          # confidence min: 0.991
'합계 49,500원'           # confidence min: 0.989
```

중요한 점은 세 가지입니다. 첫째, 줄이 의미 단위로 묶여 있어 BGE-M3가 올바른 줄을 검색할 수 있습니다. 둘째, 줄별 최소 confidence를 보존하면 후속 검토 우선순위를 만들 수 있습니다. 셋째, raw payload를 남겨 두면 나중에 OCR 모델을 교체해도 재처리가 단순합니다.

## 핵심 흐름

![Core flow](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-01-core-flow.ko.png)

*Core flow*

## 왜 mock payload부터 시작할까

![최소 실행 예제](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-01-minimal-runnable-example.ko.png)

*최소 실행 예제*

OCR 연동의 대부분은 API 호출 이후에서 아픕니다. 팀들은 인증보다 행 순서가 꼬이거나 줄이 잘못 합쳐지는 문제를 먼저 만납니다. mock payload를 코드 안에 먼저 재현하면, CI가 같은 입력을 항상 같은 방식으로 검증할 수 있고, 실제 키가 생겼을 때도 달라지는 부분은 응답을 받아 오는 한 줄뿐입니다.

## 단계별 실습

### Step 1 — Define the mock response

```python
MOCK_RESPONSE = {
    'images': [
        {
            'fields': [
                {'inferText': '공급가액', 'inferConfidence': 0.997, 'lineBreak': False},
                {'inferText': '45,000원', 'inferConfidence': 0.994, 'lineBreak': True},
                {'inferText': '부가세',   'inferConfidence': 0.996, 'lineBreak': False},
                {'inferText': '4,500원',  'inferConfidence': 0.991, 'lineBreak': True},
                {'inferText': '합계',     'inferConfidence': 0.998, 'lineBreak': False},
                {'inferText': '49,500원', 'inferConfidence': 0.989, 'lineBreak': True},
            ]
        }
    ]
}
```

실제 키가 생기면 dict를 만드는 부분만 `requests.post(...).json()`으로 바꾸면 됩니다.

### Step 2 — Reconstruct lines

![이 코드에서 주목할 점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-02-what-to-notice-in-this-code.ko.png)

*이 코드에서 주목할 점*

```python
def reconstruct_lines(payload):
    lines = []
    for image in payload['images']:
        current_text, current_conf = [], []
        for field in image['fields']:
            current_text.append(field['inferText'])
            current_conf.append(field['inferConfidence'])
            if field['lineBreak']:
                lines.append({
                    'text': ' '.join(current_text),
                    'min_confidence': min(current_conf),
                })
                current_text, current_conf = [], []
    return lines

lines = reconstruct_lines(MOCK_RESPONSE)
for line in lines:
    print(f"{line['min_confidence']:.3f}  {line['text']}")
```

`lineBreak` 기준으로 토큰을 묶고, 줄별 최소 confidence를 함께 들고 갑니다. 이 작은 함수 하나가 영수증과 계산서 후처리의 대부분을 감당합니다.

### Step 3 — Numeric and amount validation

```python
import re

AMOUNT_RE = re.compile(r'^[\d,]+원$')

for line in lines:
    tokens = line['text'].split()
    amounts = [t for t in tokens if AMOUNT_RE.match(t)]
    if not amounts and ('원' in line['text']):
        print('WARN suspicious amount format:', line['text'])
```

OCR은 “45,000원”을 “45.000원”으로 잘못 읽기도 합니다. 이런 버그는 confidence 임계값보다 도메인 정규식이 더 잘 잡습니다.

### Step 4 — Shape into a corpus document

```python
def to_corpus_doc(image_id, lines):
    return {
        'image_id': image_id,
        'lines': [line['text'] for line in lines],
        'min_confidence': min(line['min_confidence'] for line in lines),
        'raw_payload_path': f's3://ocr-raw/{image_id}.json',
    }

doc = to_corpus_doc('receipt_001', lines)
print(doc)
```

텍스트 옆에 raw payload 경로를 함께 저장해 두면 OCR 모델이 바뀌었을 때 재처리가 쉬워집니다. 텍스트만 저장하면 출처를 잃어버립니다.

### Step 5 — Swap in the real API call (optional)

![엔지니어가 헷갈리는 지점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-03-where-engineers-get-confused.ko.png)

*엔지니어가 헷갈리는 지점*

```python
import os, requests

def call_clova_ocr(image_path):
    url = os.environ['CLOVA_OCR_URL']
    secret = os.environ['CLOVA_OCR_SECRET']
    headers = {'X-OCR-SECRET': secret}
    files = {'file': open(image_path, 'rb')}
    data = {'message': '{"version":"V2","requestId":"x","timestamp":0,"images":[{"format":"jpg","name":"x"}]}'}
    return requests.post(url, headers=headers, files=files, data=data).json()
```

반환 형식은 mock dict와 같으므로 1~4단계 로직은 그대로 재사용됩니다.

## 이 코드에서 먼저 봐야 할 점

- `inferText`만큼이나 `lineBreak`를 꼼꼼히 봐야 합니다. 이 습관 하나가 영수증과 표 정확도를 크게 바꿉니다.
- 줄별 최소 confidence는 자연스러운 재검토 큐를 만듭니다.
- raw payload와 후처리 텍스트를 함께 저장하는 습관이 이후 모델 교체 때 가장 큰 자산이 됩니다.
- 실제 키를 붙인 뒤에도 mock 기반 테스트를 CI에 남겨 두면 빌드가 결정적으로 유지됩니다.

## 자주 하는 실수

- **OCR 정확도가 높으면 RAG도 좋아질 거라고 믿는 것** — 토큰 정확도와 의미 단위 정확도는 다릅니다. 줄 복원이 틀리면 99% OCR도 소용없습니다.
- **절대 confidence 임계값을 쓰는 것** — 0.95라는 숫자는 모델 버전에 따라 의미가 달라집니다. 하위 5% 분포를 보는 편이 안전합니다.
- **PDF와 이미지 OCR을 같은 방식으로 처리하는 것** — PDF에는 실제 텍스트 레이어가 있을 수 있습니다. 그때는 `pdfplumber`가 더 빠르고 정확합니다.
- **raw payload를 버리는 것** — 나중에 모델을 바꾸면 처음부터 다시 호출해야 합니다. 비용과 시간이 모두 큽니다.
- **다중 컬럼 문서를 한 줄로 합치는 것** — `boundingPoly`를 보지 않으면 좌우 컬럼이 섞입니다. 컬럼이 중요하면 x좌표 기준 그룹핑이 필요합니다.
- **mock 경로가 production에 섞이는 것** — 환경 변수 스위치 없이 두면 mock 데이터가 실서비스 경로로 새어 나올 수 있습니다. `os.environ.get('CLOVA_OCR_MODE', 'mock')` 같은 분기가 필요합니다.

## 실무 적용

- **두 단계 OCR**: 전체 페이지는 General OCR로 읽고, 영수증이나 신분증처럼 특정 구역은 Template OCR로 다시 돌리면 정확도와 비용 균형이 좋아집니다.
- **PDF 분기**: `pdfplumber`를 먼저 시도하고, 텍스트 레이어가 없는 페이지에만 OCR을 적용하면 비용을 크게 줄일 수 있습니다.
- **재처리 큐**: confidence 하위 5% 줄에 `needs_review` 태그를 달아 사람 검수로 보내면 절대 임계값 알람보다 훨씬 실용적입니다.
- **표 복원**: `boundingPoly`의 y좌표로 행을 묶고 x좌표로 열을 정렬하면 표 구조가 살아납니다. `lineBreak`만으로는 부족합니다.
- **이미지 전처리**: 기울기 보정, 노이즈 제거, 이진화를 OCR 전에 수행하면 평균 confidence가 눈에 띄게 올라갑니다.
- **모니터링**: 일별 처리량, 평균 confidence, 재구성 실패율을 대시보드로 보면 모델 변경 여파를 빨리 감지할 수 있습니다.

## 체크리스트

- [ ] raw payload와 후처리 텍스트를 함께 저장합니다.
- [ ] downstream에서 `lineBreak`, 좌표, confidence 중 무엇이 필요한지 정했습니다.
- [ ] 금액, 날짜, 식별자에 전용 정규식 검증을 붙였습니다.
- [ ] 임베딩 단계로 넘기기 전에 줄 또는 문단 재구성을 먼저 검증했습니다.
- [ ] mock-first 테스트를 CI에 넣었습니다.

## 연습 문제

1. mock 응답에 세 줄을 더 추가하고, `lineBreak: False`가 연속으로 두 번 나오는 케이스를 넣어 보세요. 재구성 함수가 어떻게 동작하는지 보고 보강 방안을 적어 보세요.
2. `boundingPoly`가 채워진 mock 응답을 만들고, x좌표 기준으로 좌우 컬럼을 나누는 함수를 작성해 보세요.
3. PDF 페이지에 대해 먼저 `pdfplumber`를 시도하고, 텍스트 레이어가 없을 때만 mock CLOVA 호출로 떨어지는 래퍼 함수를 작성해 보세요.

## 정리

CLOVA OCR 예제의 가치는 텍스트 정확도보다 먼저 응답 구조를 이해하게 만든다는 데 있습니다. `lineBreak`로 줄을 묶고, 줄별 confidence를 보존하고, raw payload를 함께 저장하는 세 가지 약속만 지켜도 OCR 결과를 RAG 코퍼스에 훨씬 안전하게 넣을 수 있습니다. 이 단계가 정리되어 있어야 다음 글에서 생성 API에 어떤 문맥을 넘길지 차분하게 판단할 수 있습니다.

다음 글에서는 5편 HyperCLOVA X와 Solar API를 다룹니다. OCR 텍스트나 BGE-M3 검색 결과를 한국어 LLM에 넘길 때 어떤 호출 계약과 프롬프트 패턴이 안전한지 구체적인 API 코드와 함께 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- [BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
- **CLOVA OCR API로 문서 텍스트 추출 (현재 글)**
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

## 참고 자료

- [NAVER Cloud CLOVA OCR overview](https://www.ncloud.com/product/aiService/ocr)
- [CLOVA OCR API guide](https://api.ncloud-docs.com/docs/ai-application-service-ocr-ocr)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [OCR post-processing patterns](https://cloud.google.com/document-ai/docs/process-documents-client-libraries)

Tags: Korean NLP, LLM, Embeddings, OCR
