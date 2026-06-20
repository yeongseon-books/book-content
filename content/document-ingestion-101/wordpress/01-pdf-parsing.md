---
title: "바이브코딩을 위한 문서 수집 파이프라인 (1/6): PDF 파싱과 텍스트 추출"
series: document-ingestion-101
episode: 1
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG
- Document Processing
- LangChain
- Python
---

# 바이브코딩을 위한 문서 수집 파이프라인 (1/6): PDF 파싱과 텍스트 추출

이 글은 **바이브코딩을 위한 문서 수집 파이프라인** 시리즈의 첫 번째 글입니다. AI에게 코드를 맡기기 전에, 파이프라인의 입력 단계인 PDF 파싱을 직접 이해하고 설계하는 방법을 다룹니다.

---

RAG 시스템을 만들 때 가장 먼저 부딪히는 벽은 PDF입니다. "그냥 텍스트 뽑으면 되지 않나요?"라고 생각했다가, 첫 번째 실제 PDF를 넣는 순간 무너집니다. 인코딩이 깨지거나, 표가 한 줄로 뭉개지거나, 헤더·푸터가 본문과 섞이거나, 이미지 안의 텍스트는 아예 나오지 않습니다. 검색 품질이 나쁜 RAG 시스템의 절반은 파싱 단계에서 이미 망가져 있습니다.

바이브코딩으로 AI에게 "PDF 파서 만들어줘"라고 시키면, AI는 `pypdf`로 텍스트를 뽑는 코드를 순식간에 작성합니다. 그 코드는 동작합니다 — 하지만 언제 동작하고 언제 실패하는지, AI도 당신도 모릅니다. 품질 게이트가 없으면 깨진 텍스트가 벡터 DB에 조용히 쌓입니다.

이 글에서는 PDF 파싱의 실패 지점을 짚고, 품질 게이트와 OCR 폴백, 표 처리 전략을 코드와 함께 설명합니다. AI가 생성한 코드를 검토하고 수정할 수 있는 기준을 갖추는 것이 목표입니다.

> "파싱 품질을 측정하지 않으면, 벡터 DB에 무엇이 들어가는지 알 수 없습니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. `pypdf`와 `pdfplumber`의 차이를 설명할 수 있나요?
2. PDF 파싱 품질을 코드로 측정하는 방법을 알고 있나요?
3. 텍스트 추출이 실패했을 때 OCR로 넘어가는 기준이 있나요?
4. 표(Table)를 파싱할 때 왜 행·열 구조가 무너지나요?
5. 헤더·푸터 텍스트를 본문과 구분하는 방법을 알고 있나요?

---

## pypdf로 기본 추출하기

`pypdf`는 가장 빠르고 의존성이 적은 PDF 텍스트 추출 라이브러리입니다.

```python
from pypdf import PdfReader

def extract_text_pypdf(pdf_path: str) -> list[dict]:
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"page": i + 1, "text": text})
    return pages
```

이 코드는 작동하지만 품질 보장이 없습니다. 텍스트가 나왔다고 해서 올바른 텍스트가 나온 건 아닙니다.

## 품질 게이트 설계

파싱 결과를 그냥 통과시키지 말고 측정하세요.

```python
def quality_gate(text: str, min_chars: int = 100) -> dict:
    char_count = len(text.strip())
    word_count = len(text.split())
    garbled_ratio = sum(1 for c in text if ord(c) > 65535) / max(len(text), 1)

    return {
        "passed": char_count >= min_chars and garbled_ratio < 0.05,
        "char_count": char_count,
        "word_count": word_count,
        "garbled_ratio": garbled_ratio,
    }
```

`char_count`가 너무 적거나 `garbled_ratio`가 높으면 OCR 폴백으로 전환합니다.

## OCR 폴백

품질 게이트를 통과하지 못하면 `pytesseract`로 OCR을 시도합니다.

```python
import pytesseract
from pdf2image import convert_from_path

def extract_text_ocr(pdf_path: str, page_num: int) -> str:
    images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
    if not images:
        return ""
    return pytesseract.image_to_string(images[0], lang="kor+eng")
```

## 표 파싱

표는 `pdfplumber`가 강합니다.

```python
import pdfplumber

def extract_table_as_text(pdf_path: str, page_num: int) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]
        tables = page.extract_tables()
        result = []
        for table in tables:
            rows = [" | ".join(cell or "" for cell in row) for row in table]
            result.append("\n".join(rows))
        return "\n\n".join(result)
```

표를 파이프(`|`)로 연결하면 LLM이 구조를 인식하기 더 쉽습니다.

---

## Before / After

| 항목 | Before (품질 게이트 없음) | After (품질 게이트 적용) |
|------|--------------------------|------------------------|
| 깨진 텍스트 | 벡터 DB에 그대로 적재 | OCR 폴백으로 재추출 |
| 표 구조 | 한 줄로 뭉개짐 | 행·열 구조 유지 |
| 빈 페이지 | 빈 청크 생성 | 건너뜀 |
| 문제 감지 | 검색 실패 후 발견 | 파싱 단계에서 즉시 감지 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 품질 측정 없이 적재 | 검색 품질 저하 | 문자 수·가비지 비율 게이트 |
| 표를 raw 텍스트로 추출 | 구조 손실 | pdfplumber + 파이프 포맷 |
| OCR 언어 설정 누락 | 한국어 인식 실패 | `lang="kor+eng"` 명시 |
| 헤더·푸터 포함 | 노이즈 삽입 | 위·아래 영역 제외 처리 |

---

## AI 활용 팁

바이브코딩으로 PDF 파서를 짤 때 이 프롬프트를 쓰세요:

```
pypdf로 PDF 텍스트를 추출하고, 페이지별로 품질을 측정해줘.
품질 기준: 최소 100자, garbled_ratio < 5%.
품질 미달 페이지는 pytesseract OCR로 재추출.
표가 있는 페이지는 pdfplumber로 별도 처리.
결과는 {page, text, quality, method} 딕셔너리 리스트로 반환.
```

AI가 생성한 코드에서 반드시 확인할 항목:
- 품질 측정 기준이 하드코딩 없이 파라미터로 분리되어 있는가
- OCR 폴백이 자동으로 트리거되는가
- 예외 처리가 페이지 단위로 격리되어 있는가

---

## 체크리스트

- [ ] pypdf로 텍스트 추출 구현
- [ ] 페이지별 품질 게이트(문자 수, 가비지 비율) 추가
- [ ] OCR 폴백 구현(pytesseract + pdf2image)
- [ ] pdfplumber로 표 구조 보존
- [ ] 헤더·푸터 제외 로직 추가
- [ ] 결과에 추출 방법(method) 메타데이터 포함

---

## 처음 질문으로 돌아가기

"그냥 텍스트 뽑으면 되지 않나요?" — 이제 답할 수 있습니다. pypdf는 대부분의 PDF에서 작동하지만, 품질 게이트 없이 사용하면 깨진 텍스트가 조용히 RAG 파이프라인에 쌓입니다. OCR 폴백과 표 처리 전략을 갖춰야 비로소 신뢰할 수 있는 파싱 단계가 됩니다.

---

## 정리

- `pypdf`로 텍스트를 추출하고, 문자 수와 가비지 비율로 품질을 측정한다
- 품질 미달 페이지는 `pytesseract` OCR로 재추출한다
- 표는 `pdfplumber`로 행·열 구조를 보존한다
- 파싱 결과에 추출 방법(method) 메타데이터를 포함시켜 추적을 가능하게 한다

---

## 참고 자료

- [pypdf 공식 문서](https://pypdf.readthedocs.io/)
- [pdfplumber GitHub](https://github.com/jsvine/pdfplumber)
- [pytesseract 한국어 설정](https://github.com/madmaze/pytesseract)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- pypdf로 기본 추출하기
- 품질 게이트 설계
- OCR 폴백
- 표 파싱
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, RAG, Document Processing, LangChain, Python
