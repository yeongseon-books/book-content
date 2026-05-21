---
title: "RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교"
series: rag-benchmark-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- Embedding
- Benchmarking
- Sentence-Transformers
- MTEB
- Latency
last_reviewed: '2026-05-12'
seo_description: 임베딩 비교는 코퍼스, 질문 집합, top-k를 고정하고 모델 하나만 바꿀 때만 의미가 있습니다.
---

# RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교

임베딩 비교는 코퍼스, 질문 집합, top-k를 고정하고 모델 하나만 바꿀 때만 의미가 있습니다. 이 글은 RAG Benchmark 101 시리즈의 세 번째 글입니다. 여기서는 같은 검색 파이프라인 안에서 어떤 임베딩 모델이 관련 문서를 더 앞쪽에 놓는지, 그리고 그 대가로 어느 정도의 속도와 비용을 치르는지 비교하겠습니다.

## 먼저 던지는 질문

- 임베딩 모델을 리더보드 점수만 보고 고르면 왜 위험할까요?
- 같은 corpus와 query에서 모델만 바꾸려면 어떤 조건을 고정해야 할까요?
- 품질이 좋아져도 latency나 비용이 커지면 어떻게 판단해야 할까요?

## 큰 그림

![같은 코퍼스에서 임베딩 모델만 바꾸는 비교 구조](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/03/03-01-fixed-corpus-embedding-comparison-struct.ko.png)

*같은 코퍼스에서 임베딩 모델만 바꾸는 비교 구조*

이 그림에서는 같은 질문과 문서 집합을 두고 임베딩 모델만 바꿔 검색 결과와 지표를 비교하는 흐름을 봅니다. 모델 비교는 이름 비교가 아니라 동일 조건에서 품질, 속도, 비용을 함께 보는 실험입니다.

> 임베딩 모델 비교는 어느 모델이 더 "똑똑한가"를 고르는 작업이 아닙니다. 같은 검색 파이프라인 안에서 **관련 문서를 더 앞순위에 배치하는 모델이 무엇인가**를 확인하는 작업입니다.

## 왜 이 주제가 중요한가

임베딩 모델은 RAG 품질의 출발점입니다. 청크 전략, 검색기, LLM이 모두 같아도 임베딩 모델 하나만 바뀌면 검색 품질과 최종 답변 품질이 함께 흔들립니다. 그래서 많은 팀이 모델 카드나 공개 리더보드를 보고 빠르게 결정을 내리고 싶어 합니다. 하지만 그 접근에는 두 가지 함정이 있습니다.

첫째는 **도메인 미스매치**입니다. MTEB 같은 공개 벤치마크는 일반 도메인 평균입니다. 사내 문서, 한국어 기술 문서, 의료·법률 텍스트처럼 특정 도메인에서는 순위가 뒤집힐 수 있습니다.

둘째는 **운영 비용을 무시하기 쉽다**는 점입니다. 품질이 조금 좋아지는 대신 임베딩 지연 시간과 인덱스 재구축 시간이 크게 늘어나면 사용자 경험과 인프라 비용 모두 악화될 수 있습니다. 따라서 임베딩 비교는 정확도만 보는 실험이 아니라 **품질·속도·운영 비용을 함께 보는 실험**이어야 합니다.

## 기본 멘탈 모델

임베딩 비교의 핵심 원칙은 **한 번에 한 변수만 바꾸기**입니다.

```text
[fixed] corpus  +  [fixed] QUERIES  +  [fixed] k
                  │
                  ▼
        [variable] embedding model
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   model A result       model B result
   (hit, MRR, latency)  (hit, MRR, latency)
```

코퍼스나 질문 세트가 함께 바뀌면, 점수 차이가 모델 때문인지 데이터 때문인지 설명할 수 없습니다. 따라서 2편에서 만든 검색 측정 루프를 그대로 함수로 감싸고, 입력 변수로 모델 이름만 바꾸는 방식이 가장 안전합니다.

이 구조는 단순하지만 매우 강력합니다. 실험 설계를 지켜 주기 때문입니다. 모델이 바뀌어도 질문 집합과 평가 방법이 같다면, 결과 차이를 비교적 자신 있게 모델 차이로 해석할 수 있습니다.

## 핵심 개념

| 용어 | 의미 |
| --- | --- |
| Embedding model | 텍스트를 고정 차원 벡터로 바꾸는 모델 |
| Embedding dimension | 출력 벡터 차원 수. 커질수록 표현력은 늘지만 인덱스 크기와 비교 비용도 증가 |
| Sentence-Transformers | 문장 단위 임베딩에 특화된 라이브러리 |
| MTEB | 공개 임베딩 모델 리더보드 |
| Embedding latency | 텍스트 하나를 벡터로 바꾸는 데 드는 시간 |
| Index build time | 코퍼스 전체를 임베딩하고 인덱스를 만드는 시간 |

일반적으로 작은 모델은 차원이 작고 빠르며, 큰 모델은 차원이 크고 더 느립니다. 하지만 그 차이가 실제 질문 세트에서 얼마만큼의 품질 차이로 이어지는지는 직접 측정해 보기 전까지 알 수 없습니다.

## 리더보드만 볼 때와 직접 비교할 때

이전에는 "MTEB 1위니까 이걸 쓰자"라는 식으로 결정합니다. 그런데 막상 인덱스를 다시 만드는 데 30분이 걸리고, 응답 지연 시간이 두 배로 늘고, 사내 질문에서는 hit rate가 오히려 떨어질 수 있습니다.

이후에는 같은 코퍼스와 같은 질문 세트에 두 모델을 올리고 한 표에서 비교합니다.

```text
model                    hit@3  MRR   avg_lat_ms  index_build_s
all-MiniLM-L6-v2         1.00   0.83  6.2         3.1
paraphrase-MiniLM-L3-v2  0.67   0.50  4.8         2.4
```

이제는 무엇을 선택해야 하는지 훨씬 분명해집니다. 첫 번째 모델은 품질이 낫고, 두 번째 모델은 속도가 빠릅니다. 트레이드오프가 수치로 드러나기 때문입니다.

## 단계별로 비교 실험 만들기

### 1단계 — 기존 측정 루프를 함수로 감싸기

```python
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def benchmark_model(model_name: str):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vectorstore = FAISS.from_documents(DOCUMENTS, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    hits, rrs, latencies = [], [], []
    for question, gold in QUERIES:
        t0 = time.perf_counter()
        docs = retriever.invoke(question)
        latencies.append((time.perf_counter() - t0) * 1000)
        ranked = [d.metadata["id"] for d in docs]
        hits.append(hit_rate(ranked, gold))
        rrs.append(reciprocal_rank(ranked, gold))

    return {
        "model": model_name,
        "hit@3": round(sum(hits) / len(hits), 2),
        "MRR": round(sum(rrs) / len(rrs), 2),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 1),
    }
```

여기서 중요한 것은 함수가 모델 이름만 입력으로 받는다는 점입니다. 나머지 코퍼스, 질문 집합, k는 모두 동일해야 합니다.

### 2단계 — 두 모델을 같은 조건에서 실행하기

실행 코드는 `rag-benchmark-101/en/03-embedding-comparison/main.py`에 있습니다. 05편과 06편은 `GROQ_API_KEY`가 필요합니다.

```bash
cd en/03-embedding-comparison
python3 main.py
```

```python
MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/paraphrase-MiniLM-L3-v2",
]
results = [benchmark_model(name) for name in MODELS]
print(json.dumps(results, indent=2))
```

같은 질문과 같은 코퍼스를 기준으로 한 결과라야 비교가 의미를 갖습니다. 그래야 숫자 차이를 모델 차이로 읽을 수 있습니다.

### 3단계 — 품질과 속도를 함께 읽기

![품질과 지연 시간을 함께 보는 비교 축](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/03/03-02-quality-and-latency-comparison-axes.ko.png)

*품질과 지연 시간을 함께 보는 비교 축*

결과를 볼 때는 hit rate와 MRR를 함께 읽어야 합니다. hit rate가 같아도 MRR이 낮으면 관련 문서가 상단에 오르지 못한다는 뜻입니다. 또 지연 시간도 함께 봐야 합니다. 검색 품질이 조금 좋아지는 대신 응답 시간이 크게 늘어나면 실제 서비스에서는 받아들이기 어려울 수 있습니다.

### 4단계 — 인덱스 구축 시간도 재기

운영에서는 검색 지연 시간만큼 인덱스 재구축 시간도 중요합니다. 코퍼스가 커질수록 이 시간은 분 단위로 늘어납니다.

```python
t0 = time.perf_counter()
vectorstore = FAISS.from_documents(DOCUMENTS, embeddings)
index_build_s = round(time.perf_counter() - t0, 2)
```

검색 질의당 지연 시간은 좋아도, 모델 교체 때마다 인덱스를 다시 만드는 시간이 너무 길면 운영 부담이 커집니다.

## 자주 하는 실수

![한 번에 한 변수만 바꿔야 하는 실험 경계](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/03/03-03-one-variable-at-a-time-experiment-bounda.ko.png)

*한 번에 한 변수만 바꿔야 하는 실험 경계*

- **두 변수를 동시에 바꾸기** — 임베딩 모델과 청크 크기를 함께 바꾸면 어느 쪽 영향인지 알 수 없습니다.
- **Hit rate만 보고 결정하기** — 같은 hit rate라도 MRR 차이가 크면 실제 답변 품질은 크게 달라집니다.
- **리더보드만 신뢰하기** — 공개 평균 성적과 내 도메인 성적은 다를 수 있습니다.
- **임베딩 지연 시간을 빼먹기** — 검색 지연 시간만 재면 실제 사용자 응답 시간을 과소평가합니다.
- **첫 호출을 그대로 집계하기** — 모델 다운로드와 워밍업이 섞여 측정이 왜곡될 수 있습니다.

## 운영 환경으로 가져갈 때

운영에서는 메모리와 장치 조건도 함께 봐야 합니다. 1024차원 모델은 384차원 모델보다 인덱스가 훨씬 커집니다. GPU가 없는 환경에서 큰 모델을 CPU로 돌리면 지연 시간 차이가 훨씬 더 벌어질 수 있습니다.

또 한국어처럼 영어 외 언어가 섞인다면, 다국어 모델 후보를 반드시 하나는 넣어 보는 편이 좋습니다. 공개 리더보드의 상위권 모델이 영어에서는 강해도 한국어 질의에서는 기대 이하일 수 있기 때문입니다.

API 기반 임베딩도 같은 표에 올려야 합니다. 네트워크 지연과 토큰 비용이 있기 때문에, 로컬 모델과 비교할 때 단순 품질 점수만 봐서는 안 됩니다. 결국 의사결정은 **품질·속도·비용을 같은 실험표에서 읽는 것**으로 귀결됩니다.

## 체크리스트

![속도, 품질, 비용을 함께 보는 선택 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/03/03-04-speed-quality-and-cost-selection-flow.ko.png)

*속도, 품질, 비용을 함께 보는 선택 흐름*

- [ ] 모든 모델을 같은 코퍼스, 같은 질문 집합, 같은 k로 비교했는가?
- [ ] hit rate와 MRR를 함께 보고 있는가?
- [ ] 검색 지연 시간, 임베딩 지연 시간, 인덱스 구축 시간을 모두 기록하는가?
- [ ] 모델 이름, 차원 수, CPU/GPU 조건을 결과와 함께 남기는가?
- [ ] 실제 도메인 질문으로 다시 검증할 계획이 있는가?

## 연습 문제

1. `paraphrase-multilingual-MiniLM-L12-v2`를 세 번째 모델로 추가해 다국어 질문에서 비교해 보세요.
2. 임베딩 모델을 고정한 채 청크 크기를 200, 500, 1000으로 바꾸면 무엇이 더 크게 흔들릴까요?
3. `benchmark_model()`이 모델 카드의 차원 수까지 함께 출력하도록 확장해 보세요.

## 정리와 다음 글

이 글에서는 검색기 구조는 그대로 둔 채 임베딩 모델만 바꾸어 hit rate, MRR, 지연 시간을 비교했습니다. 핵심은 단순합니다. **한 번에 한 변수만 바꾸고, 품질과 속도와 비용을 같은 표에서 읽는 것**입니다.

다음 글에서는 같은 접근을 VectorDB 선택에 적용합니다. 같은 임베딩 벡터를 두고 인덱스 구조가 달라질 때 어떤 트레이드오프가 생기는지 보겠습니다.

### 모델 비교 표를 먼저 고정하기

실험 전에 어떤 모델을 비교할지 표로 고정하면 회의와 재현이 쉬워집니다. 아래는 한국어 기술 문서 RAG에서 자주 후보로 올리는 모델군 예시입니다.

| 모델 | 차원 | 다국어 | 상대 속도(기준=MiniLM-L6) | MTEB(평균, 참고용) |
| --- | ---: | --- | ---: | ---: |
| all-MiniLM-L6-v2 | 384 | 제한적 | 1.0x | 60대 후반 |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | 지원 | 0.8x | 60대 중반 |
| bge-m3 | 1024 | 강함 | 0.4x | 60대 후반~70대 초반 |
| e5-large-v2 | 1024 | 중간 | 0.35x | 70대 초반 |

여기서 MTEB 점수는 절대 기준이 아니라 후보를 줄이는 1차 필터로만 쓰는 편이 안전합니다. 실제 선택은 반드시 내 질문 세트의 hit@k와 MRR, 그리고 지연 시간으로 확정해야 합니다.

### 코사인 유사도 계산 경로를 명시하기

임베딩 비교에서는 검색 라이브러리 내부 구현에만 의존하지 말고, 핵심 유사도 계산을 별도 코드로 검증해 두는 편이 좋습니다. 그래야 정규화 여부와 점수 해석을 팀 내에서 통일할 수 있습니다.

```python
import numpy as np

def l2_normalize(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)

def cosine_similarity_matrix(query_vecs: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    q = l2_normalize(query_vecs.astype("float32"))
    d = l2_normalize(doc_vecs.astype("float32"))
    return q @ d.T

def top_k_ids(sim_matrix: np.ndarray, k: int) -> np.ndarray:
    return np.argsort(-sim_matrix, axis=1)[:, :k]
```

정규화된 벡터에서는 inner product와 cosine similarity가 동일하게 동작합니다. 이 사실을 코드로 명시해 두면 FAISS에서 `IndexFlatIP`를 선택한 이유를 설명하기 쉽습니다.

### MTEB 점수를 해석할 때의 실무 규칙

MTEB는 강력한 출발점이지만, 세 가지 규칙을 같이 두는 편이 좋습니다.

1. **언어 분포를 분리해서 본다**: 영어 중심 평균 점수와 한국어 질의 성능이 다를 수 있습니다.
2. **태스크 유형을 확인한다**: 분류, 검색, 중복 탐지 성적은 서로 다르게 나타날 수 있습니다.
3. **운영 지연 시간을 함께 기록한다**: 2점 향상을 위해 지연 시간이 2배 늘면 제품 요구사항과 충돌할 수 있습니다.

실무에서 가장 설득력 있는 리포트는 "MTEB 상위권 모델 중 우리 도메인 질문에서 MRR이 가장 높고, P95 지연 시간이 목표 안에 든 모델"을 명확히 보여 주는 형태입니다. 즉, 공개 점수는 후보 축소용이고 최종 의사결정은 사내 벤치마크용입니다.

## 처음 질문으로 돌아가기

- **임베딩 모델을 리더보드 점수만 보고 고르면 왜 위험할까요?**
  리더보드는 일반 벤치마크일 뿐 내 문서, 언어, 쿼리 분포, 지연 시간 제약을 대신 측정하지 않습니다.

- **같은 corpus와 query에서 모델만 바꾸려면 어떤 조건을 고정해야 할까요?**
  corpus, chunking, query set, gold labels, k, VectorDB 설정, 측정 코드를 고정하고 embedding model만 바꿔야 합니다.

- **품질이 좋아져도 latency나 비용이 커지면 어떻게 판단해야 할까요?**
  품질 향상이 운영 지연, 인프라 비용, 재인덱싱 비용을 감당할 만큼 큰지 기준표로 판단해야 합니다. 최고 점수 모델이 항상 제품 선택은 아닙니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG Evaluation and Benchmarking 101 (1/6): RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정](./02-retrieval-benchmarking.md)
- **RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교 (현재 글)**
- RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준 (예정)
- RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가 (예정)
- RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Sentence Transformers model catalog](https://www.sbert.net/docs/pretrained_models.html)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [LangChain HuggingFaceEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub/)
- [FAISS index types](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-benchmark-101/ko/03-embedding-comparison)

Tags: RAG, VectorDB, Benchmarking, LLM
