---
title: "Multimodal AI 101 (5/10): Multimodal RAG: 이미지와 텍스트를 함께 검색하기"
series: multimodal-ai-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Multimodal RAG
- CLIP Embeddings
- Cross-modal Retrieval
- FAISS
- LangChain
- Vector Search
last_reviewed: '2026-05-12'
seo_description: 전형적인 RAG 시스템은 documents를 chunk로 나누고, embedding을 vector DB에 넣고, query…
---

# Multimodal AI 101 (5/10): Multimodal RAG: 이미지와 텍스트를 함께 검색하기

텍스트 RAG는 많은 문제를 해결했지만, 이미지와 문서 레이아웃이 중요한 순간부터 한계가 또렷해집니다. 사용자가 “표 오른쪽 아래 수치가 무엇인가요?”, “이 제품 사진과 가장 비슷한 항목을 찾아 주세요”, “스크린샷 속 경고 아이콘이 의미하는 바가 뭔가요?”라고 묻는 순간 텍스트 청크만으로는 답이 흔들립니다.

이때 필요한 것이 multimodal RAG입니다. 핵심은 단순합니다. 검색 대상을 텍스트에서 이미지·caption·OCR·메타데이터까지 넓히고, 최종 생성 단계에서 VLM이 그 결과를 함께 읽게 만드는 것입니다. 하지만 구현은 텍스트 RAG보다 훨씬 까다롭습니다. 어떤 representation을 인덱싱할지부터, 어떤 modality를 어떤 비용으로 프롬프트에 넣을지까지 선택지가 많기 때문입니다.

실무에서는 특히 인덱싱 전략이 성패를 좌우합니다. 원본 이미지를 직접 검색할지, caption과 OCR을 함께 넣을지, dual index를 둘지에 따라 정확도와 지연 시간이 크게 바뀝니다. 메타데이터 필터와 평가셋 설계도 텍스트 RAG보다 더 중요합니다.

이 글에서는 multimodal RAG를 “이미지까지 검색하는 RAG”가 아니라, 검색 표현과 생성 입력을 함께 다시 설계하는 확장형 retrieval 시스템으로 정리합니다.

검색 대상이 넓어질수록 인덱싱과 평가 전략을 먼저 고정하는 편이 훨씬 안전합니다.

![Multimodal AI 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/05/05-01-big-picture.ko.png)
*Multimodal AI 101 5장 흐름 개요*
> Multimodal RAG: 이미지와 텍스트를 함께 검색하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 텍스트 RAG는 왜 이미지, 표, 레이아웃 정보가 중요한 질문에서 곧바로 성능 한계를 드러낼까요?
- 멀티모달 검색을 위해 원본 이미지, caption/OCR, dual index를 쓰는 세 가지 전략은 어떻게 다를까요?
- 검색 결과를 최종 답변 단계에서 VLM에 넘길 때 어떤 입력 조합이 가장 실용적일까요?

## 왜 이 글이 중요한가

멀티모달 RAG는 실제 제품에서 바로 쓰일 가능성이 높은 패턴입니다. 전자상거래 검색, 문서 비서, 디자인 QA, 화면 기반 지원, 의료·산업 이미지 검색처럼 텍스트와 시각 정보가 섞인 데이터가 이미 많기 때문입니다.

또한 이 패턴은 기존 RAG 자산을 버리지 않고 확장할 수 있다는 장점이 있습니다. caption, OCR, image embedding을 추가하면 텍스트 중심 인프라를 상당 부분 재사용하면서도 검색 표현을 넓힐 수 있습니다.

반대로 성급하게 붙이면 비용과 복잡도가 빠르게 증가합니다. 어떤 representation을 저장하고, 어떤 것을 프롬프트에 직접 넣을지에 대한 원칙이 없으면 멀티모달 RAG는 금세 느리고 비싼 시스템이 됩니다.

## 핵심 관점

많은 팀이 multimodal RAG를 “VLM을 붙인 RAG”라고만 생각합니다. 하지만 실제 병목은 대개 generation보다 retrieval에서 먼저 생깁니다. 텍스트만 검색하면 이미지 의미를 놓치고, 원본 이미지만 검색하면 정밀 텍스트를 잃기 때문입니다.

따라서 먼저 정해야 할 것은 어떤 표현을 인덱싱할지입니다. CLIP embedding, OCR 텍스트, caption, 메타데이터를 어떤 조합으로 저장할지에 따라 시스템 성격이 거의 결정됩니다. 생성 단계는 그 위에서 최종 컨텍스트를 조립하는 층에 가깝습니다.

이 관점으로 접근하면 평가도 달라집니다. 정답 생성만 보지 말고, 어떤 질의에서 어떤 modality의 증거가 실제로 회수되었는지를 retrieval 단계부터 분리해서 확인해야 합니다.

> 멀티모달 RAG의 난점은 VLM 호출 자체보다, 무엇을 검색 가능한 표현으로 만들고 무엇을 최종 컨텍스트에 넣을지 결정하는 데 있습니다.

## 핵심 개념

### 텍스트 RAG로는 풀리지 않는 질문

전형적인 RAG 시스템은 documents를 chunk로 나누고, embedding을 vector DB에 넣고, query embedding으로 nearest를 찾습니다. 그런데 사용자가 "이런 모양의 차트가 들어있는 슬라이드 찾아줘" 또는 "스크린샷에서 빨간 버튼 위치 알려줘" 같은 질문을 던지면 텍스트 chunk로는 답할 수 없습니다.

multimodal RAG는 이런 질문을 image와 text를 같은 vector space에서 검색해 풀어냅니다. 2편의 CLIP, 4편의 OCR/captioning이 이번 편에서 한 파이프라인으로 합쳐집니다.

### 세 가지 인덱싱 전략

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

# 이미지에 대해 caption / ocr_text가 사전에 상담해 드립니다
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
        # alpha=0: 텍스트만 / alpha=1: 이미지만
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

### 답변 생성 단계: 검색 결과를 VLM에 넘기기

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

### 평가: multimodal RAG는 어떻게 측정하나

retrieval 정확도와 generation 품질을 분리해서 측정합니다.

```python
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

## 멀티모달 RAG 평가셋을 만드는 방법

멀티모달 RAG는 텍스트 질문만으로 평가하면 실제 성능을 과대평가하게 됩니다. 평가셋을 만들 때는 질문 유형을 명시적으로 나눠야 합니다. 최소한 시각 패턴 질문, 수치/표 질문, OCR 오류 복원 질문, 이미지-텍스트 결합 질문 네 가지를 포함하는 편이 좋습니다.

```python
from dataclasses import dataclass

@dataclass
class MMQuery:
    query: str
    answer: str
    evidence_image_id: str
    query_type: str  # visual | numeric | ocr_repair | mixed

benchmark = [
    MMQuery("빨간 경고 아이콘이 나온 화면을 찾아줘", "settings_error_12", "img_104", "visual"),
    MMQuery("Q3 매출이 가장 낮은 그래프는?", "slide_27", "img_342", "numeric"),
]
```

이렇게 유형을 분리하면 특정 인덱싱 전략의 약점이 바로 드러납니다. 예를 들어 image embedding 단독 전략은 visual 질문에서는 강하지만 numeric 질문에서 급락하는 패턴이 자주 보입니다.

## 재순위화 계층: CLIP 후보 + GPT-4V/Claude 판정

검색 계층을 두 단계로 두면 품질이 안정됩니다. 1단계에서는 CLIP과 텍스트 인덱스로 빠르게 top-30을 뽑고, 2단계에서는 GPT-4V 또는 Claude로 top-5를 재판정합니다.

```python
def fuse_scores(clip_score: float, text_score: float, beta: float = 0.55) -> float:
    return beta * clip_score + (1 - beta) * text_score

def should_rerank_with_vlm(query_type: str, top1_margin: float) -> bool:
    if query_type in {"numeric", "mixed"}:
        return True
    return top1_margin < 0.08
```

재순위화 판단 기준을 명시적으로 두면 무분별한 Vision API 호출을 막을 수 있습니다. 특히 `top1_margin`을 쓰면 후보 간 점수 격차가 작은 불확실 상황만 선별할 수 있습니다.

## 생성 단계에서 근거 추적 필드 남기기

최종 답변은 자연어만 반환하지 말고, 어떤 이미지와 OCR 블록을 근거로 썼는지 함께 남겨야 합니다. 이 필드가 있어야 hallucination 감사와 사용자 이의 제기가 가능합니다.

```python
response = {
    "answer": "Q3 매출은 0.9M으로 가장 낮습니다.",
    "citations": [
        {"image_id": "img_342", "bbox": [411, 298, 588, 346], "source": "ocr"},
        {"image_id": "img_342", "source": "chart_bar_3"},
    ],
    "retrieval_scores": {"clip": 0.41, "text": 0.67, "fused": 0.54},
}
```

이 구조를 먼저 고정하면 모델을 바꿔도 운영 품질 지표를 일관되게 비교할 수 있습니다.

## 인덱스 운영: 갱신 주기와 재색인 정책

멀티모달 인덱스는 한 번 만들고 끝나는 자산이 아닙니다. 이미지가 추가되거나 캡션 모델이 바뀌면 재색인이 필요하며, 이때 전체 재빌드를 할지 증분 반영을 할지 기준이 필요합니다. 실무에서는 "모델 버전 변경"과 "데이터 추가"를 구분해 관리합니다.

```python
from dataclasses import dataclass

@dataclass
class IndexEvent:
    kind: str  # add | delete | reembed
    item_id: str
    model_version: str
```

또한 운영 중에는 stale 인덱스 탐지가 중요합니다. 최근 업로드 자산이 검색 top-k에 거의 등장하지 않으면 증분 파이프라인이 지연되었을 가능성이 큽니다. 이런 지표를 대시보드에 두면 검색 품질 저하를 조기에 발견할 수 있습니다.

## 검색 품질 저하를 빠르게 탐지하는 모니터링

멀티모달 RAG에서는 생성 모델이 자연어를 잘 만들어도 retrieval이 무너지면 답변 신뢰도가 급락합니다. 따라서 운영 지표는 생성 품질보다 retrieval 신호를 먼저 감시해야 합니다. 대표적으로 top-1 점수 하락, top-k 다양성 감소, 최신 문서 회수율 저하를 경고 지표로 두는 것이 실용적입니다.

```python
def detect_retrieval_drift(avg_top1: float, latest_doc_hit_rate: float) -> bool:
    if avg_top1 < 0.22:
        return True
    if latest_doc_hit_rate < 0.15:
        return True
    return False
```

또한 멀티모달 RAG는 이미지 자산의 라이프사이클 영향을 많이 받습니다. 이미지 URL 만료, 썸네일 손상, OCR 캐시 누락이 발생하면 retrieval 정확도가 급격히 흔들릴 수 있습니다. 그래서 데이터 계층 상태를 함께 모니터링하는 것이 중요합니다.

운영 관점에서 좋은 시스템은 모델 정답률뿐 아니라 "근거 회수율"을 안정적으로 유지합니다. 이 값이 유지되어야 상위 생성 모델 교체도 안전하게 시도할 수 있습니다.

## Query intent 분류와 가중치 자동 조정

질의 의도를 분류해 검색 가중치를 조정하면 멀티모달 RAG 성능이 안정됩니다. 시각 묘사 중심 질문은 이미지 점수를 높이고, 숫자/사실 질문은 OCR·텍스트 점수를 높이는 방식이 효과적입니다.

```python
def choose_alpha(intent: str) -> float:
    if intent == "visual":
        return 0.75
    if intent == "numeric":
        return 0.25
    return 0.5
```

작게 시작해도 충분합니다. 의도 분류를 복잡하게 만들기보다, 오답 로그를 모아 규칙을 점진적으로 늘리는 편이 운영 리스크가 낮습니다.

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

짧게 정리하면, 멀티모달 RAG의 품질은 생성 모델 선택보다 retrieval 설계와 증거 관리 정책에서 먼저 결정됩니다. 따라서 인덱스 품질 지표와 근거 회수율을 주간 운영 지표로 고정해 두는 편이 좋습니다.

## 흔히 헷갈리는 지점

- **CLIP과 텍스트 embedding을 같은 인덱스에 섞기** CLIP은 자체 latent space, BGE/OpenAI embedding은 다른 latent space입니다. 두 vector를 한 인덱스에 넣으면 거리가 의미를 잃습니다. 인덱스를 따로 두고 score를 가중평균합니다.
- **고해상도 이미지 모두 base64 inline** VLM에 inline하는 이미지는 base64 한 장당 수십 KB~수백 KB입니다. retrieval top-10을 모두 inline하면 token 비용과 latency 모두 폭증합니다. top-3로 제한하거나 URL 참조 방식을 씁니다.
- **caption/OCR을 미리 안 만들고 query 시점에 생성** 매 query마다 caption을 새로 뽑으면 latency가 초 단위로 느려집니다. ingestion 단계에서 caption/OCR을 함께 저장합니다.
- **metadata filter 없이 검색** production index는 보통 1000만 장 이상으로 커집니다. user_id, document_type, date_range 같은 metadata filter 없이 ANN 검색하면 권한 누수와 성능 저하가 동시에 옵니다.
- **evaluation set이 텍스트 query만** multimodal RAG는 텍스트 query뿐 아니라 image-by-image 검색, image+text 혼합 query도 평가해야 합니다. 평가 셋 설계 단계부터 multimodal query를 포함합니다.

## 운영 체크리스트

- [ ] 원본 이미지·OCR 텍스트·caption 중 어떤 표현을 인덱싱할지 명시적으로 구분했는가
- [ ] CLIP류 이미지 인덱스와 텍스트 인덱스의 점수 결합 방식을 정의했는가
- [ ] 대용량 이미지를 무분별하게 inline하지 않고 썸네일·URL·선별 업로드 전략을 두었는가
- [ ] 메타데이터 필터와 권한 필터를 retrieval 단계에 포함했는가
- [ ] 텍스트 질의뿐 아니라 이미지 질의·복합 질의를 포함한 평가셋을 갖췄는가

## 정리

멀티모달 RAG는 단순히 이미지까지 넣는 RAG가 아닙니다. 어떤 표현을 검색 가능한 증거로 저장할지, 그리고 어떤 증거를 최종 생성 입력으로 조합할지를 다시 설계하는 패턴입니다.

성공하는 시스템은 retrieval 표현을 분리해서 생각합니다. CLIP embedding, OCR, caption, 메타데이터는 각각 다른 종류의 질문을 잘 처리하며, 어느 하나만으로는 충분하지 않은 경우가 많습니다.

다음 주제들로 넘어가더라도 오늘의 기준은 계속 유효합니다. 멀티모달 시스템의 품질은 결국 좋은 표현을 인덱싱하고, 그 표현을 비용 안에서 적절히 조합하는 능력에 달려 있습니다.

## 처음 질문으로 돌아가기

- **텍스트 RAG는 왜 이미지, 표, 레이아웃 정보가 중요한 질문에서 곧바로 성능 한계를 드러낼까요?**
  - 본문의 기준은 Multimodal RAG: 이미지와 텍스트를 함께 검색하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **멀티모달 검색을 위해 원본 이미지, caption/OCR, dual index를 쓰는 세 가지 전략은 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **검색 결과를 최종 답변 단계에서 VLM에 넘길 때 어떤 입력 조합이 가장 실용적일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- **Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (현재 글)**
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 Text-to-Image 생성 (예정)
- Multimodal Embedding과 Cross-modal 검색 (예정)
- Video 이해 - Frame Sampling에서 Video-LLaVA까지 (예정)
- Production Multimodal Application 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [LangChain - Multi-Modal RAG](https://python.langchain.com/docs/use_cases/question_answering/multi_modal_rag/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [BAAI BGE Embedding Model Card](https://huggingface.co/BAAI/bge-base-en-v1.5)

### 관련 시리즈

- [Vector Search 101 - 벡터 검색 파이프라인](../../vector-search-101/ko/06-vector-search-pipeline.md)
- [RAG Deep Dive - Retriever 설계](../../rag-deep-dive/ko/03-retriever-design.md)
- [RAG 평가와 벤치마크 101 - 종단 간 RAG 파이프라인 평가](../../rag-benchmark-101/ko/05-e2e-evaluation.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/05-multimodal-rag)

Tags: Multimodal RAG, CLIP Embeddings, Cross-modal Retrieval, FAISS, LangChain, Vector Search
