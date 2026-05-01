---
title: 'Document text extraction with CLOVA OCR API'
series: korean-ai-stack-101
episode: 4
language: en
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

# Document text extraction with CLOVA OCR API

> Korean AI Stack 101 (4/6)

Example code: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/04-clova-ocr)

RAG pipelines do not always start from text files. Scanned contracts, receipt images, and tables embedded in PDFs all lock text inside images. OCR (Optical Character Recognition) extracts that text. NAVER CLOVA OCR is a commercial Korean-specialized API that handles everything from printed business documents to handwritten Korean.

Topics:

- basic CLOVA OCR API usage
- extracting text from images and cleaning the output
- bounding box and position data for structured documents
- connecting extracted text to a RAG pipeline

---

## API setup

Create an OCR domain in NAVER Cloud Platform to obtain an API URL and a Secret Key. Set both as environment variables.

```bash
export CLOVA_OCR_API_URL="https://..."
export CLOVA_OCR_SECRET_KEY="..."
```

---

## Basic OCR request

```python
import base64
import json
import os
import time
import uuid
from pathlib import Path

import requests

def ocr_image(image_path: str) -> dict:
    """Send an image to the CLOVA OCR API and return the parsed response."""
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
    """Extract all recognized text from an OCR response into a single string."""
    lines = []
    for image in ocr_result.get("images", []):
        for field in image.get("fields", []):
            lines.append(field.get("inferText", ""))
    return "\n".join(lines)
```

---

## Bounding box and position data

CLOVA OCR returns bounding polygon coordinates for each text block. This is useful for reconstructing reading order in tables and forms.

```python
def extract_text_with_position(ocr_result: dict) -> list[dict]:
    """Return text blocks with position information."""
    blocks = []
    for image in ocr_result.get("images", []):
        for field in image.get("fields", []):
            vertices = field.get("boundingPoly", {}).get("vertices", [])
            top_y = min(v.get("y", 0) for v in vertices) if vertices else 0
            left_x = min(v.get("x", 0) for v in vertices) if vertices else 0

            blocks.append({
                "text": field.get("inferText", ""),
                "confidence": field.get("inferConfidence", 0.0),
                "x": left_x,
                "y": top_y,
            })

    # sort top-to-bottom, left-to-right within each row
    blocks.sort(key=lambda b: (b["y"], b["x"]))
    return blocks

def reconstruct_lines(blocks: list[dict], y_threshold: int = 15) -> list[str]:
    """Group blocks with similar y-coordinates into text lines."""
    if not blocks:
        return []

    lines = []
    current_line = [blocks[0]]

    for block in blocks[1:]:
        if abs(block["y"] - current_line[-1]["y"]) <= y_threshold:
            current_line.append(block)
        else:
            lines.append(" ".join(b["text"] for b in current_line))
            current_line = [block]

    if current_line:
        lines.append(" ".join(b["text"] for b in current_line))

    return lines
```

---

## Cleaning OCR output

Raw OCR output contains recognition errors, stray special characters, and redundant whitespace. Cleaning before embedding improves retrieval quality.

```python
import re

def clean_ocr_text(text: str) -> str:
    """
    Clean OCR text:
    1. remove repeated special characters
    2. normalize whitespace
    3. collapse multiple blank lines
    """
    # remove repeated non-word characters (e.g., "...", "---")
    text = re.sub(r"([^\w\s가-힣])\1{2,}", "", text)

    # tabs to spaces
    text = text.replace("\t", " ")

    # collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    lines = [line.strip() for line in text.split("\n")]

    cleaned_lines = []
    prev_empty = False
    for line in lines:
        is_empty = not line
        if is_empty and prev_empty:
            continue
        cleaned_lines.append(line)
        prev_empty = is_empty

    return "\n".join(cleaned_lines).strip()

sample = """
  Receipt   

Date: 2024-01-15    Time: 14:32

Item               Qty    Price
-------------------
Americano           1    4,500
Cafe Latte          2    9,000
-----------
Total             13,500 KRW

Thank you!!!
"""

print(clean_ocr_text(sample))
```

---

## OCR to RAG pipeline

Extracted and cleaned text feeds directly into the standard chunking → embedding → indexing pipeline.

```python
import os

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

def process_images_to_index(image_paths: list[str]) -> FAISS:
    """OCR → clean → chunk → index a list of image files."""
    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        separators=["\n\n", "\n", ".", " "],
    )

    for image_path in image_paths:
        print(f"processing: {image_path}")

        # in production, replace this with: raw_text = extract_text(ocr_image(image_path))
        raw_text = f"""
        [Sample document: {image_path}]
        Contract date: January 15, 2024
        Parties: Hong Gildong (Party A), ABC Corporation (Party B)
        Contract amount: Five million Korean won (5,000,000 KRW)
        """
        cleaned = clean_ocr_text(raw_text)
        chunks = splitter.split_text(cleaned)
        all_chunks.extend({"text": chunk, "source": image_path} for chunk in chunks)

    texts = [c["text"] for c in all_chunks]
    metadatas = [{"source": c["source"]} for c in all_chunks]
    return FAISS.from_texts(texts=texts, embedding=embedding_model, metadatas=metadatas)

vectorstore = process_images_to_index(["contract_001.jpg", "contract_002.jpg"])
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question based on the scanned document content below.\n\n"
        "Document content:\n{context}",
    ),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[source: {source}]\n{doc.page_content}")
    return "\n\n".join(parts)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("What is the contract amount?")
print(f"answer: {answer}")
```

---

## Conclusion

CLOVA OCR delivers high accuracy on Korean documents including handwritten text. The cleaning step — removing repeated special characters and normalizing whitespace — measurably improves downstream embedding quality. Once cleaned, the extracted text enters the same chunking and indexing pipeline as any other text source.

The next post covers HyperCLOVA X and Solar API: calling Korean-specialized LLMs from Python.

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- **Document text extraction with CLOVA OCR API (current)**
- Using HyperCLOVA X and Solar API (upcoming)
- Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [CLOVA OCR API documentation](https://api.ncloud-docs.com/docs/ai-application-service-ocr)
- [NAVER Cloud Platform OCR](https://www.ncloud.com/product/aiService/ocr)
- [LangChain TextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

Tags: Korean NLP, LLM, Embeddings, OCR
