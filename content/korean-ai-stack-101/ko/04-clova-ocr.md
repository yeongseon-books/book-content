---
title: 'CLOVA OCR API로 문서 텍스트 추출'
series: korean-ai-stack-101
episode: 4
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-01'
---

# CLOVA OCR API로 문서 텍스트 추출

> 한국어 AI 스택 101 시리즈 (4/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/04-clova-ocr)

RAG 파이프라인에서 문서 소스는 텍스트 파일만이 아닙니다. 스캔한 계약서, 영수증 이미지, PDF 내 표처럼 텍스트가 이미지로 묶여 있는 경우가 많습니다. OCR(Optical Character Recognition)은 이미지에서 텍스트를 추출하는 기술입니다. 네이버 CLOVA OCR은 한국어 인식에 특화된 상용 API로, 한글 손글씨부터 인쇄된 문서까지 폭넓게 지원합니다.

다룰 내용은 다음과 같습니다.

- CLOVA OCR API 기본 사용
- 이미지에서 텍스트 추출 후 임베딩까지
- OCR 결과 정제 (노이즈 제거)
- 추출한 텍스트를 RAG 파이프라인에 연결

---

## CLOVA OCR API 설정

네이버 클라우드 플랫폼에서 OCR 도메인을 생성하면 API URL과 Secret Key를 받습니다. 두 값을 환경 변수로 설정합니다.

```bash
export CLOVA_OCR_API_URL="https://..."
export CLOVA_OCR_SECRET_KEY="..."
```

---

## 기본 OCR 요청

```python
import base64
import json
import os
import time
import uuid
from pathlib import Path

import requests

def ocr_image(image_path: str) -> dict:
    """
    이미지 파일을 CLOVA OCR API에 전송하고 결과를 반환합니다.
    """
    api_url = os.environ["CLOVA_OCR_API_URL"]
    secret_key = os.environ["CLOVA_OCR_SECRET_KEY"]

    image_path = Path(image_path)
    suffix = image_path.suffix.lower().lstrip(".")
    format_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "pdf": "pdf"}
    image_format = format_map.get(suffix, "jpeg")

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    request_body = {
        "images": [
            {
                "format": image_format,
                "name": image_path.name,
                "data": image_data,
            }
        ],
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(time.time() * 1000),
    }

    headers = {
        "X-OCR-SECRET": secret_key,
        "Content-Type": "application/json",
    }

    response = requests.post(
        api_url,
        headers=headers,
        data=json.dumps(request_body),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

def extract_text(ocr_result: dict) -> str:
    """
    OCR 결과에서 텍스트만 추출해 하나의 문자열로 반환합니다.
    """
    lines = []
    for image in ocr_result.get("images", []):
        for field in image.get("fields", []):
            lines.append(field.get("inferText", ""))
    return "\n".join(lines)

# 사용 예시
# result = ocr_image("receipt.jpg")
# text = extract_text(result)
# print(text)
```

---

## 바운딩 박스와 위치 정보

CLOVA OCR은 각 텍스트 블록의 위치 정보도 반환합니다. 표나 양식 같은 구조화된 문서에서 유용합니다.

```python
def extract_text_with_position(ocr_result: dict) -> list[dict]:
    """
    텍스트와 위치 정보를 함께 반환합니다.
    """
    blocks = []
    for image in ocr_result.get("images", []):
        for field in image.get("fields", []):
            bounding_poly = field.get("boundingPoly", {})
            vertices = bounding_poly.get("vertices", [])

            if vertices:
                # y 좌표로 행 위치 파악 (위에서 아래로)
                top_y = min(v.get("y", 0) for v in vertices)
                left_x = min(v.get("x", 0) for v in vertices)
            else:
                top_y, left_x = 0, 0

            blocks.append({
                "text": field.get("inferText", ""),
                "confidence": field.get("inferConfidence", 0.0),
                "x": left_x,
                "y": top_y,
            })

    # y좌표 기준 정렬 (위에서 아래로, 같은 행이면 x 기준)
    blocks.sort(key=lambda b: (b["y"], b["x"]))
    return blocks

def reconstruct_lines(blocks: list[dict], y_threshold: int = 15) -> list[str]:
    """
    비슷한 y좌표를 가진 블록들을 같은 행으로 묶어 텍스트 행을 재구성합니다.
    """
    if not blocks:
        return []

    lines = []
    current_line = [blocks[0]]

    for block in blocks[1:]:
        prev_y = current_line[-1]["y"]
        if abs(block["y"] - prev_y) <= y_threshold:
            current_line.append(block)
        else:
            line_text = " ".join(b["text"] for b in current_line)
            lines.append(line_text)
            current_line = [block]

    if current_line:
        lines.append(" ".join(b["text"] for b in current_line))

    return lines
```

---

## OCR 결과 정제

실제 OCR 결과에는 인식 오류, 특수문자, 불필요한 공백이 섞입니다. 텍스트를 임베딩하기 전에 정제 과정이 필요합니다.

```python
import re

def clean_ocr_text(text: str) -> str:
    """
    OCR 텍스트 정제:
    1. 과도한 공백 제거
    2. 인식 오류 패턴 제거 (반복 특수문자)
    3. 빈 행 정리
    """
    # 반복되는 특수문자 제거 (예: "...", "---", "===")
    text = re.sub(r"([^\w\s가-힣])\1{2,}", "", text)

    # 탭을 공백으로
    text = text.replace("\t", " ")

    # 연속 공백을 하나로
    text = re.sub(r" {2,}", " ", text)

    # 각 줄 앞뒤 공백 제거
    lines = [line.strip() for line in text.split("\n")]

    # 빈 줄이 연속으로 오면 하나로
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        is_empty = not line
        if is_empty and prev_empty:
            continue
        cleaned_lines.append(line)
        prev_empty = is_empty

    return "\n".join(cleaned_lines).strip()

# 정제 테스트
sample_ocr_output = """
  영수증   

날짜: 2024-01-15    시간: 14:32

상품명          수량    금액
-------------------
아메리카노       1    4,500
카페라떼         2    9,000
-----------
합계            13,500원

감사합니다!!!
"""

cleaned = clean_ocr_text(sample_ocr_output)
print("정제된 텍스트:")
print(cleaned)
```

---

## OCR → 임베딩 → RAG 파이프라인

OCR로 추출한 텍스트를 임베딩하고 검색 가능한 인덱스를 만듭니다.

```python
import os
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding_model = HuggingFaceEmbeddings(
    model_name="BM-K/KoSimCSE-roberta-multitask",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

def process_image_to_index(image_paths: list[str]) -> FAISS:
    """이미지 목록을 OCR → 정제 → 청킹 → 인덱싱."""
    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        separators=["\n\n", "\n", "。", ". ", " "],
    )

    for image_path in image_paths:
        print(f"처리 중: {image_path}")

        # OCR 결과 (실제로는 API 호출, 여기서는 샘플)
        raw_text = f"""
        [샘플 문서: {image_path}]
        이 문서에는 한국어 텍스트가 포함되어 있습니다.
        계약서 날짜: 2024년 1월 15일
        계약 당사자: 홍길동 (갑), ABC주식회사 (을)
        계약 금액: 일금 오백만원정 (₩5,000,000)
        """
        cleaned = clean_ocr_text(raw_text)
        chunks = splitter.split_text(cleaned)

        # 메타데이터로 출처 추적
        all_chunks.extend([
            {"text": chunk, "source": image_path}
            for chunk in chunks
        ])

    texts = [c["text"] for c in all_chunks]
    metadatas = [{"source": c["source"]} for c in all_chunks]
    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
    )
    return vectorstore

# 샘플 사용
image_files = ["contract_001.jpg", "contract_002.jpg"]
vectorstore = process_image_to_index(image_files)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "스캔된 문서에서 추출한 내용을 바탕으로 질문에 답하세요.\n\n"
        "문서 내용:\n{context}",
    ),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    texts = []
    for doc in docs:
        source = doc.metadata.get("source", "알 수 없음")
        texts.append(f"[출처: {source}]\n{doc.page_content}")
    return "\n\n".join(texts)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("계약 금액이 얼마인가요?")
print(f"답변: {answer}")
```

---

## 마무리

CLOVA OCR은 한국어 문서 텍스트 추출에서 높은 정확도를 보입니다. OCR 후 정제 단계를 거치면 임베딩 품질이 올라갑니다. 추출한 텍스트는 일반 텍스트와 동일하게 청킹 → 임베딩 → 인덱싱 파이프라인에 넣을 수 있습니다.

다음 글에서는 HyperCLOVA X와 Solar API를 사용해서 한국어에 특화된 LLM을 호출하는 방법을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- [BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
- **CLOVA OCR API로 문서 텍스트 추출 (현재 글)**
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [CLOVA OCR API 공식 문서](https://api.ncloud-docs.com/docs/ai-application-service-ocr)
- [네이버 클라우드 플랫폼 OCR](https://www.ncloud.com/product/aiService/ocr)
- [LangChain TextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

Tags: Korean NLP, LLM, Embeddings, OCR
