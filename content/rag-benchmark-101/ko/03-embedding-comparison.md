---
title: 임베딩 모델 비교
series: rag-benchmark-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Embedding
- Benchmarking
- Sentence-Transformers
- MTEB
- Latency
last_reviewed: '2026-05-11'
seo_description: 임베딩 비교는 "하나만 바꾼다(one-variable-at-a-time)" 원칙 위에서 동작합니다.
---

# 임베딩 모델 비교

> 임베딩 모델 비교는 어느 모델이 더 "똑똑한가"를 따지는 일이 아닙니다. 같은 retrieval pipeline 안에서 **관련 문서를 더 앞쪽에 배치하는 모델이 무엇인가**를 보는 일입니다.

## 이 글에서 다룰 문제

임베딩 모델은 RAG 품질의 출발점입니다. 같은 chunk, 같은 retriever, 같은 LLM이라도 임베딩 모델이 바뀌면 답변 품질이 크게 흔들립니다. 그런데 모델 카드나 leaderboard 점수만 보고 결정하면 다음 두 가지 함정에 빠집니다.

첫째, **데이터 도메인 미스매치**입니다. MTEB leaderboard는 일반 도메인 평균 점수입니다. 내 회사의 사내 문서, 한국어 의료 데이터, 법률 판례에서는 결과가 뒤집힐 수 있습니다.

둘째, **운영 비용 무시**입니다. 더 큰 모델이 hit rate를 0.05 올린다 해도, latency가 3배 늘면 사용자 체감과 인프라 비용은 함께 망가집니다.

이 글에서 만들 비교는 작지만, "내 데이터·내 query·내 인프라" 위에서 직접 측정한 숫자라는 점에서 leaderboard보다 의사결정에 더 도움이 됩니다.

## Mental Model

임베딩 비교는 **"하나만 바꾼다(one-variable-at-a-time)"** 원칙 위에서 동작합니다.

```text
[고정] corpus  +  [고정] QUERIES  +  [고정] k
                  │
                  ▼
        [변수] embedding model
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   model A 결과         model B 결과
   (hit, MRR, latency)  (hit, MRR, latency)
```

corpus와 query를 고정하지 않으면, 점수 차이가 모델 때문인지 데이터 때문인지 구분할 수 없습니다. 측정 코드는 2편의 루프를 그대로 함수로 감싼 뒤, 모델 이름만 인자로 받게 만듭니다.

## 핵심 개념

| 용어 | 의미 |
| --- | --- |
| Embedding model | 텍스트를 고정 차원의 벡터로 바꾸는 모델 |
| Embedding dimension | 벡터의 차원 수. 클수록 표현력이 높지만 인덱스 크기와 비교 비용이 증가 |
| Sentence-Transformers | 문장 단위 임베딩에 특화된 라이브러리 (SBERT) |
| MTEB | Massive Text Embedding Benchmark — 임베딩 모델용 공개 leaderboard |
| Embedding latency | 한 텍스트를 벡터로 변환하는 데 걸리는 시간 |
| Index build time | corpus 전체를 임베딩하고 vector index를 만드는 시간 |

작은 모델일수록 차원 수가 작고(예: 384) latency가 낮습니다. 큰 모델은 768 또는 1024 차원에 latency가 2~5배 높습니다. 둘 다 측정해야 의사결정에 쓸 수 있습니다.

## Before vs. After

**Before**: "MTEB에서 1위라니까 이걸 쓰자"라고 결정합니다. 인덱스를 다시 빌드하는 데 30분이 걸리고, 응답 latency가 평소의 두 배가 됩니다. 그런데 사내 질문에서는 hit rate가 오히려 떨어집니다.

**After**: 같은 corpus와 query 위에서 두 모델을 돌립니다. 결과는 한 줄짜리 표:

```text
model                    hit@3  MRR   avg_lat_ms  index_build_s
all-MiniLM-L6-v2         1.00   0.83  6.2         3.1
paraphrase-MiniLM-L3-v2  0.67   0.50  4.8         2.4
```

표를 보면 첫 번째 모델이 품질에서 우위, 두 번째가 속도에서 우위라는 사실이 분명해집니다. 트레이드오프를 의식적으로 선택할 수 있습니다.

## 단계별 실습

### 1단계 — 비교 함수 작성

2편의 루프를 함수로 감싸 모델 이름만 받도록 만듭니다.

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

### 2단계 — 두 모델 실행

![같은 코퍼스에서 임베딩 모델만 바꾸는 비교 구조](../../../assets/rag-benchmark-101/03/03-01-fixed-corpus-embedding-comparison-struct.ko.png)

*같은 코퍼스에서 임베딩 모델만 바꾸는 비교 구조*

실행 코드는 `rag-benchmark-101/ko/03-embedding-comparison/main.py`에 있습니다. 05편과 06편은 `GROQ_API_KEY`가 필요합니다.

```bash
cd /root/Github/rag-benchmark-101/ko/03-embedding-comparison
python3 main.py
```

```python
MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/paraphrase-MiniLM-L3-v2",
]
results = [benchmark_model(name) for name in MODELS]
print(json.dumps(results, indent=2, ensure_ascii=False))
```

### 3단계 — 결과 비교

![품질 점수와 지연 시간을 함께 보는 비교 축](../../../assets/rag-benchmark-101/03/03-02-quality-and-latency-comparison-axes.ko.png)

*품질 점수와 지연 시간을 함께 보는 비교 축*

품질(hit rate, MRR)과 latency를 함께 봅니다. 한쪽만 보면 잘못된 결정을 내리기 쉽습니다.

### 4단계 — index build time도 측정

운영에서는 인덱스 재빌드도 비용입니다. corpus 크기가 1만 건을 넘기면 분 단위로 늘어납니다.

```python
t0 = time.perf_counter()
vectorstore = FAISS.from_documents(DOCUMENTS, embeddings)
index_build_s = round(time.perf_counter() - t0, 2)
```

## 자주 하는 실수

![한 번에 한 변수만 바꿔야 하는 실험 경계](../../../assets/rag-benchmark-101/03/03-03-one-variable-at-a-time-experiment-bounda.ko.png)

*한 번에 한 변수만 바꿔야 하는 실험 경계*

- **변수를 동시에 바꾸기** — 임베딩 모델과 chunk size를 같이 바꾸면 어느 쪽이 차이를 만들었는지 알 수 없습니다. 한 번에 한 변수만 바꿔야 합니다.
- **hit rate만 보고 결정** — hit rate가 같아도 MRR이 0.4 vs 0.8이면 답변 품질은 크게 달라집니다. LLM은 상위 문서 순서에 민감합니다.
- **Leaderboard 점수만 신뢰** — MTEB는 평균 점수입니다. 내 도메인에서는 순위가 뒤집힐 수 있습니다.
- **Embedding latency 누락** — 검색 latency만 측정하고 embedding 호출은 빼면, 실제 사용자 응답 시간을 과소평가하게 됩니다.
- **첫 호출 포함** — 모델 다운로드와 워밍업 시간이 latency에 섞입니다. warm-up 호출 후 측정합니다.

## 실무 적용

- **dimension과 인덱스 비용**: 1024차원 모델은 384차원 모델 대비 인덱스가 2.7배 큽니다. 메모리 예산도 함께 보세요.
- **다국어 vs. 단일어**: 한국어가 섞이면 multilingual 모델(`paraphrase-multilingual-MiniLM-L12-v2` 등)을 후보에 넣어야 합니다.
- **GPU 가용성**: 큰 모델을 CPU로 돌리면 latency가 10배 이상 차이 납니다. 인프라가 GPU 없는 환경이면 작은 모델로 시작합니다.
- **재빌드 주기**: 코퍼스가 자주 바뀌면 index build time이 SLO에 들어갑니다.
- **OpenAI/Cohere 같은 API 임베딩**: latency가 네트워크에 좌우되고, 비용은 토큰 단위입니다. 같은 표 위에서 비교해야 공정합니다.

## 실무에서는 이렇게 생각한다

임베딩 모델 교체는 생각보다 비용이 큽니다. 모델을 바꾸면 벡터 DB 전체를 다시 인덱싱해야 하므로, 문서 수십만 건 규모에서는 수 시간이 걸릴 수 있습니다. 그래서 모델 비교는 본번 인덱싱 전에 샘플 데이터로 충분히 검증하는 것이 원칙입니다.

리더보드 상위 모델이 내 데이터에서도 최고일 것이라는 보장은 없습니다. 특히 한국어 데이터, 전문 용어가 많은 도메인, 문서 길이가 그고르지 않은 코퍼스에서는 벤치마크 순위와 실제 성능이 다를 수 있습니다. 내 데이터로 직접 측정하는 것 외에 신뢰할 수 있는 방법은 없습니다.

## 체크리스트

![속도와 정확도와 비용을 합치는 선택 흐름](../../../assets/rag-benchmark-101/03/03-04-speed-quality-and-cost-selection-flow.ko.png)

*속도와 정확도와 비용을 합치는 선택 흐름*

- [ ] 동일한 corpus, 동일한 query set, 동일한 k로 두 모델을 평가했다.
- [ ] hit rate와 MRR을 함께 비교했다.
- [ ] retrieval latency뿐 아니라 embedding latency, index build time도 기록했다.
- [ ] 모델 이름, dimension, device(CPU/GPU)를 결과 표에 함께 남겼다.
- [ ] 도메인 질문으로 한 번 더 검증할 계획을 세웠다.

## 정리 · 다음 글

이번 글에서는 retriever 구조를 그대로 두고 임베딩 모델만 바꿔서 hit rate, MRR, latency를 비교했습니다. 핵심은 **한 번에 한 변수만 바꾸기**와 **품질·속도·비용을 같은 표에서 보기**입니다.

다음 글(4편)에서는 같은 사고방식을 vector DB 선택에 적용합니다. FAISS, Chroma, pgvector 같은 후보를 같은 측정 루프 위에 올려 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [검색 성능 측정](./02-retrieval-benchmarking.md)
- **임베딩 모델 비교 (현재 글)**
- VectorDB 선택 기준 (예정)
- 종단 간 RAG 파이프라인 평가 (예정)
- RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Sentence Transformers model catalog](https://www.sbert.net/docs/pretrained_models.html)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [LangChain HuggingFaceEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub/)
- [FAISS index types](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

Tags: RAG, VectorDB, Benchmarking, LLM
