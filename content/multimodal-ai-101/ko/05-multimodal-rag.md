---
title: 'Multimodal RAG: 이미지와 텍스트를 함께 검색하기'
series: multimodal-ai-101
episode: 5
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Multimodal RAG
- CLIP Embeddings
- Cross-modal Retrieval
- FAISS
- LangChain
- Vector Search
last_reviewed: '2026-05-03'
seo_description: 전형적인 RAG 시스템은 documents를 chunk로 나누고, embedding을 vector DB에 넣고, query…
---

# Multimodal RAG: 이미지와 텍스트를 함께 검색하기

> Multimodal AI 101 시리즈 (5/10)

---

<!-- a-grade-intro:begin -->
## 핵심 질문

이미지를 포함한 문서를 RAG에서 어떻게 검색·답변에 활용하나요?

이 글은 그 질문에 답하기 위해 multimodal RAG 설계의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 텍스트 RAG로는 풀리지 않는 질문

전형적인 RAG 시스템은 documents를 chunk로 나누고, embedding을 vector DB에 넣고, query embedding으로 nearest를 찾습니다. 그런데 사용자가 "이런 모양의 차트가 들어있는 슬라이드 찾아줘" 또는 "스크린샷에서 빨간 버튼 위치 알려줘" 같은 질문을 던지면 텍스트 chunk로는 답할 수 없습니다.

multimodal RAG는 이런 질문을 image와 text를 같은 vector space에서 검색해 풀어냅니다. 2편의 CLIP, 4편의 OCR/captioning이 이번 편에서 한 파이프라인으로 합쳐집니다.

## 세 가지 인덱싱 전략

### 전략 1: image embedding 단독 인덱스

CLIP image embedding을 vector DB에 넣고, query는 CLIP text encoder로 인코딩해 검색합니다. 가장 단순합니다.

```python
import faiss
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def embed_images(paths: list[str]) -> np.ndarray:
    imgs = [Image.open(p).convert("RGB") for p in paths]
    inputs = proc(images=imgs, return_tensors="pt")
    with torch.no_grad():
        feats = model.get_image_features(**inputs)
    feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().numpy().astype("float32")

paths = ["slides/01.png", "slides/02.png", "slides/03.png"]
vecs = embed_images(paths)
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs)

def search_by_text(q: str, k: int = 3) -> list[str]:
    qi = proc(text=[q], return_tensors="pt", padding=True)
    with torch.no_grad():
        qv = model.get_text_features(**qi)
    qv = (qv / qv.norm(dim=-1, keepdim=True)).cpu().numpy().astype("float32")
    D, I = index.search(qv, k=k)
    return [paths[i] for i in I[0]]

print(search_by_text("a bar chart showing quarterly revenue"))
```

장점은 단순함. 단점은 텍스트 reasoning이 약합니다. "Q3 매출이 떨어진 슬라이드"처럼 숫자 reasoning이 들어간 query는 잘 못 잡습니다.

### 전략 2: caption + OCR 텍스트로 인덱싱

이미지에서 caption (BLIP) + OCR (PaddleOCR)을 뽑고, 그 텍스트를 일반 텍스트 embedding으로 인덱싱합니다. 4편에서 만든 파이프라인의 직접적 활용입니다.

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

def index_text(items: list[dict]):
    texts = [f"{it['caption']}\n\n{it['ocr_text']}" for it in items]
    vecs = embedder.encode(texts, normalize_embeddings=True).astype("float32")
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    return index, items

# 가정: 각 image에 대해 caption / ocr_text를 미리 추출
items = [
    {"path": "slides/01.png",
     "caption": "bar chart of revenue",
     "ocr_text": "Q1: 1.2M Q2: 1.5M Q3: 0.9M"},
    # ...
]
index, items = index_text(items)

def search(q: str, k: int = 3):
    qv = embedder.encode([q], normalize_embeddings=True).astype("float32")
    D, I = index.search(qv, k=k)
    return [items[i] for i in I[0]]

for r in search("Q3 revenue dropped"):
    print(r["path"], r["caption"])
```

장점은 텍스트 reasoning이 강합니다. 단점은 caption/OCR 단계가 추가되고, 시각적 detail (색상, 모양, 위치)이 표현되지 않습니다.

### 전략 3: hybrid (image vector + text vector를 둘 다 인덱싱)

production에서 가장 자주 쓰는 패턴입니다. image와 text 두 벡터를 별도 인덱스에 넣고, query 종류에 따라 한쪽 또는 양쪽을 검색합니다.

```python
class HybridIndex:
    def __init__(self, clip_index, text_index, items):
        self.clip = clip_index   # CLIP image vectors
        self.text = text_index   # caption+OCR text vectors
        self.items = items

    def search(self, query: str, k: int = 5,
               alpha: float = 0.5) -> list[dict]:
        # alpha=0: text only / alpha=1: image only
        d_clip, i_clip = self.clip.search(self._clip_q(query), k=k * 3)
        d_text, i_text = self.text.search(self._text_q(query), k=k * 3)
        scores: dict[int, float] = {}
        for d, i in zip(d_clip[0], i_clip[0]):
            scores[i] = scores.get(i, 0) + alpha * float(d)
        for d, i in zip(d_text[0], i_text[0]):
            scores[i] = scores.get(i, 0) + (1 - alpha) * float(d)
        ranked = sorted(scores.items(), key=lambda x: -x[1])[:k]
        return [self.items[i] for i, _ in ranked]
```

`alpha`를 query intent로 동적으로 정합니다. 시각적 query면 0.7, 사실/숫자 query면 0.2 같은 식입니다.

## 답변 생성 단계: 검색 결과를 VLM에 넘기기

검색만으로 끝나는 RAG는 거의 없습니다. retrieved image를 VLM이 읽고 답을 만들어야 합니다.

```python
import base64
from openai import OpenAI

client = OpenAI()

def encode(p: str) -> str:
    return base64.b64encode(open(p, "rb").read()).decode()

def answer(question: str, top_paths: list[str]) -> str:
    content = [{"type": "text", "text": question}]
    for p in top_paths[:3]:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encode(p)}"},
        })
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
    )
    return resp.choices[0].message.content
```

검색 -> top-K image -> VLM에 inline -> 답변. 텍스트 RAG와 구조는 같지만 context에 image가 들어간다는 점이 다릅니다.

## 평가: multimodal RAG는 어떻게 측정하나

retrieval 정확도와 generation 품질을 분리해서 측정합니다.

```python
from typing import Iterable

def hit_at_k(predictions: list[list[str]],
             gold: list[str], k: int = 5) -> float:
    hits = sum(1 for pred, g in zip(predictions, gold) if g in pred[:k])
    return hits / len(gold)

def mrr(predictions: list[list[str]], gold: list[str]) -> float:
    total = 0.0
    for pred, g in zip(predictions, gold):
        if g in pred:
            total += 1.0 / (pred.index(g) + 1)
    return total / len(predictions)
```

- Retrieval: Recall@k, MRR, nDCG
- Generation: faithfulness (VLM이 retrieved image의 정보만 썼는가), answer relevancy

ai-evaluation-101 시리즈에서 이 평가 프레임워크를 자세히 다뤘습니다.

## 흔히 놓치는 함정 다섯 가지

### 1. CLIP과 텍스트 embedding을 같은 인덱스에 섞기

CLIP은 자체 latent space, BGE/OpenAI embedding은 다른 latent space입니다. 두 vector를 한 인덱스에 넣으면 거리가 의미를 잃습니다. 인덱스를 따로 두고 score를 가중평균합니다.

### 2. 고해상도 이미지 모두 base64 inline

VLM에 inline하는 이미지는 base64 한 장당 수십 KB~수백 KB입니다. retrieval top-10을 모두 inline하면 token 비용과 latency 모두 폭증합니다. top-3로 제한하거나 URL 참조 방식을 씁니다.

### 3. caption/OCR을 미리 안 만들고 query 시점에 생성

매 query마다 caption을 새로 뽑으면 latency가 초 단위로 느려집니다. ingestion 단계에서 caption/OCR을 함께 저장합니다.

### 4. metadata filter 없이 검색

production index는 보통 1000만 장 이상으로 커집니다. user_id, document_type, date_range 같은 metadata filter 없이 ANN 검색하면 권한 누수와 성능 저하가 동시에 옵니다.

### 5. evaluation set이 텍스트 query만

multimodal RAG는 텍스트 query뿐 아니라 image-by-image 검색, image+text 혼합 query도 평가해야 합니다. 평가 셋 설계 단계부터 multimodal query를 포함합니다.

## 핵심 요약

- multimodal RAG는 image embedding 인덱스, caption+OCR 텍스트 인덱스, hybrid 셋 중 하나를 선택합니다.
- 가장 자주 쓰이는 패턴은 hybrid: 두 벡터를 따로 인덱싱하고 query별로 가중치 alpha를 조정합니다.
- 검색 후 VLM에 inline image를 넘겨 답변을 생성합니다. top-K는 3 정도가 cost/quality 균형점입니다.
- 평가는 retrieval(Recall@k, MRR)과 generation(faithfulness, relevancy)을 분리해 측정합니다.
- 인덱스 분리, base64 inline 제한, ingestion 단계 caption/OCR 저장, metadata filter, multimodal query evaluation은 production 도입 전에 점검합니다.

---

<!-- toc:begin -->
## 시니어 엔지니어는 이렇게 생각합니다

- **이미지 색인 전략** — 원본 임베딩 vs 캡션 임베딩 vs 둘 다인지 검색 의도에 맞춰 결정합니다.
- **청크 단위** — 페이지/블록/이미지 묶음 단위를 답변 정밀도와 함께 정합니다.
- **랭킹 신호** — 텍스트와 이미지 점수를 가중 합산하는 단순 룰부터 시작합니다.
- **증거 표시** — 이미지 출처와 좌표를 답변에 함께 노출해 신뢰를 만듭니다.
- **평가 데이터** — 이미지가 결정적인 질의 셋을 따로 만들어 회귀 테스트로 묶습니다.

## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- **Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (현재 글)**
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 텍스트에서 이미지 생성 (예정)
- Multimodal Embedding과 cross-modal 검색 (예정)
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [LangChain - Multi-Modal RAG](https://python.langchain.com/docs/use_cases/question_answering/multi_modal_rag/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [BAAI BGE Embedding Model Card](https://huggingface.co/BAAI/bge-base-en-v1.5)

Tags: Multimodal RAG, CLIP Embeddings, Cross-modal Retrieval, FAISS, LangChain, Vector Search
