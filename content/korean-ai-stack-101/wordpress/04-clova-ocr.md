---
title: "바이브코딩을 위한 한국어 AI 스택 (4/6): CLOVA OCR API로 문서 텍스트 추출"
series: korean-ai-stack-101
episode: 4
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- Korean NLP
- CLOVA
- OCR
- NaverCloud
---

# 바이브코딩을 위한 한국어 AI 스택 (4/6): CLOVA OCR API로 문서 텍스트 추출

이 글은 **바이브코딩을 위한 한국어 AI 스택** 시리즈의 네 번째 글입니다. 네이버 CLOVA OCR API를 사용해 한국어 문서 이미지에서 텍스트를 추출하는 방법을 다룹니다.

---

스캔된 PDF나 이미지 파일에서 텍스트를 추출해야 합니다. pytesseract로 시도했지만 한국어 인식률이 만족스럽지 않습니다. 특히 손글씨나 특수 폰트, 표 안의 텍스트는 정확도가 낮습니다. 네이버 CLOVA OCR은 한국어에 특화된 OCR 서비스로, 일반 OCR보다 높은 한국어 인식률을 제공합니다.

바이브코딩으로 AI에게 "한국어 OCR 만들어줘"라고 하면 pytesseract 코드가 나올 수 있습니다. CLOVA OCR의 API 구조와 응답 처리 방법을 모르면, 더 나은 선택지를 놓칩니다.

이 글에서는 CLOVA OCR API 호출부터 결과 파싱, 표 구조 보존까지 실전 코드를 다룹니다.

> "한국어 OCR은 CLOVA가 pytesseract보다 정확합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. CLOVA OCR API의 요청 형식이 어떻게 되나요?
2. OCR 결과에서 텍스트의 위치(bounding box) 정보를 활용하는 방법이 있나요?
3. 이미지를 base64로 인코딩하는 이유가 무엇인가요?
4. OCR 결과를 RAG 파이프라인에 연결하려면 어떻게 하나요?
5. CLOVA OCR과 pytesseract를 어떤 기준으로 선택하나요?

---

## CLOVA OCR API 호출

```python
import requests
import base64
import uuid
import time
from pathlib import Path

def clova_ocr(image_path: str, api_url: str, secret_key: str) -> dict:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = Path(image_path).suffix.lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"

    payload = {
        "images": [{
            "format": ext,
            "name": "document",
            "data": image_data,
        }],
        "requestId": str(uuid.uuid4()),
        "timestamp": int(time.time() * 1000),
        "version": "V2",
    }

    response = requests.post(
        api_url,
        headers={
            "X-OCR-SECRET": secret_key,
            "Content-Type": "application/json",
        },
        json=payload,
    )
    return response.json()
```

## 결과 파싱

```python
def parse_ocr_result(result: dict) -> str:
    texts = []
    for image in result.get("images", []):
        if image.get("inferResult") != "SUCCESS":
            continue
        for field in image.get("fields", []):
            text = field.get("inferText", "")
            if text.strip():
                texts.append(text)
    return " ".join(texts)
```

## 표 구조 보존

```python
def parse_table_from_ocr(result: dict) -> list[list[str]]:
    """OCR 결과에서 표 구조를 복원합니다."""
    fields = []
    for image in result.get("images", []):
        fields.extend(image.get("fields", []))

    # y 좌표로 행 그룹화
    rows = {}
    for field in fields:
        vertices = field.get("boundingPoly", {}).get("vertices", [])
        if not vertices:
            continue
        y = int(vertices[0]["y"] / 20) * 20  # 20px 단위로 그룹화
        rows.setdefault(y, []).append((vertices[0]["x"], field.get("inferText", "")))

    table = []
    for y in sorted(rows.keys()):
        row = [text for _, text in sorted(rows[y], key=lambda x: x[0])]
        table.append(row)

    return table
```

---

## Before / After

| 항목 | Before (pytesseract) | After (CLOVA OCR) |
|------|---------------------|-------------------|
| 한국어 인식률 | 70~80% | 95%+ |
| 표 구조 | 무너짐 | bounding box 보존 |
| 손글씨 | 거의 인식 불가 | 지원 |
| 특수 폰트 | 오인식 빈번 | 개선됨 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| API 키 하드코딩 | 보안 위험 | 환경변수 사용 |
| 이미지 형식 오류 | API 거부 | jpg → jpeg 변환 |
| inferResult 확인 없음 | 실패 결과 파싱 | SUCCESS만 처리 |
| 표 구조 무시 | 컨텍스트 손실 | bounding box 활용 |

---

## AI 활용 팁

```
CLOVA OCR API로 한국어 문서 이미지에서 텍스트를 추출하는 함수를 만들어줘.
이미지를 base64로 인코딩하고 API에 전송한 뒤, inferResult가 SUCCESS인 결과만 파싱해줘.
표가 있는 이미지는 bounding box의 y 좌표로 행을 그룹화해서 표 구조를 보존해줘.
```

---

## 체크리스트

- [ ] CLOVA OCR API URL과 Secret Key 환경변수 설정
- [ ] 이미지 base64 인코딩
- [ ] API 호출 및 inferResult 확인
- [ ] 텍스트 파싱(parse_ocr_result)
- [ ] 표 구조 보존(y 좌표 그룹화)
- [ ] 오류 응답 처리

---

## 처음 질문으로 돌아가기

"pytesseract로 한국어 OCR 했는데 인식률이 낮아요" — 한국어 특화 OCR이 필요합니다. CLOVA OCR은 네이버가 한국어에 맞게 학습한 모델로, 일반 문서부터 손글씨까지 높은 정확도를 제공합니다. bounding box 정보로 표 구조도 보존할 수 있습니다.

---

## 정리

- CLOVA OCR은 한국어 문서 인식에 pytesseract보다 높은 정확도를 제공한다
- 이미지를 base64로 인코딩해서 API에 전송한다
- inferResult가 SUCCESS인 결과만 파싱한다
- bounding box의 y 좌표로 표 구조를 복원한다

---

## 참고 자료

- [CLOVA OCR API 공식 문서](https://api.ncloud-docs.com/docs/ai-application-service-ocr)
- [Naver Cloud Console](https://console.ncloud.com/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- CLOVA OCR API 호출
- 결과 파싱
- 표 구조 보존
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, Korean NLP, CLOVA, OCR, NaverCloud
