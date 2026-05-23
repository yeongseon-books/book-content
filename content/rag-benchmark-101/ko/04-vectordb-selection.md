---
title: "RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준"
series: rag-benchmark-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- VectorDB
- FAISS
- IVF
- Recall
- ANN
last_reviewed: '2026-05-15'
seo_description: VectorDB 비교는 브랜드 비교가 아니라 같은 벡터와 같은 질의를 서로 다른 인덱스 구조에 넣어 보는 실험입니다.
---

# RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준

VectorDB 비교는 브랜드 비교가 아니라 같은 벡터와 같은 질의를 서로 다른 인덱스 구조에 넣어 보는 실험입니다. 이 글은 RAG Benchmark 101 시리즈의 네 번째 글입니다. 여기서는 같은 임베딩 결과를 기준으로 정확도, 검색 지연 시간, 메모리의 트레이드오프를 읽는 방법을 정리하겠습니다.

![같은 벡터를 flat과 IVF에 넣는 비교 구조](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-01-same-vector-flat-and-ivf-comparison-stru.ko.png)
*같은 벡터를 flat과 IVF에 넣는 비교 구조*
> VectorDB 선택은 **브랜드 이름을 고르는 일**이 아닙니다. 같은 임베딩 벡터가 서로 다른 인덱스 구조 안에서 어떻게 동작하는지 측정하는 실험입니다.

## 먼저 던지는 질문

- VectorDB는 기능 목록이 아니라 어떤 운영 조건으로 비교해야 할까요?
- 같은 임베딩과 corpus에서 VectorDB만 바꿔 보려면 무엇을 고정해야 할까요?
- 정확도, latency, 필터링, 운영 복잡도가 충돌할 때 어떤 기준으로 선택해야 할까요?

## 왜 이 주제가 중요한가

벡터 검색 비용은 코퍼스가 커질수록 급격히 커집니다. 문서 수가 적을 때는 어떤 인덱스를 쓰든 큰 차이가 없어 보일 수 있습니다. 하지만 규모가 커지면 brute-force 방식의 flat 검색은 곧 병목이 됩니다.

이때 등장하는 것이 IVF, HNSW 같은 **근사 최근접 탐색(ANN)** 인덱스입니다. 이들은 약간의 정확도를 포기하는 대신 검색 속도를 크게 끌어올립니다. 문제는 그 "약간"이 데이터 분포와 파라미터에 따라 완전히 다르게 나타난다는 사실입니다. 어떤 코퍼스에서는 recall 0.99를 유지하면서 매우 빨라질 수 있지만, 어떤 경우에는 정확도가 크게 무너질 수 있습니다.

그래서 VectorDB 선택은 편의성이나 인지도만으로 결정하면 안 됩니다. 내 코퍼스와 내 질의 세트 위에서 **정확도·속도·메모리**를 함께 측정해야 합니다. 이 글의 예제는 작지만, 어떤 축을 봐야 하는지는 충분히 분명하게 보여 줍니다.

## 기본 멘탈 모델

VectorDB 비교의 골격은 아래와 같습니다.

```text
[fixed] embedding model + corpus embeddings (doc_vectors)
                  │
                  ▼
        [variable] index structure
        ┌─────────┴─────────┐
        ▼                   ▼
   IndexFlatIP           IndexIVFFlat (nprobe=N)
   (exact, slow)         (approximate, fast)
        │                   │
        ▼                   ▼
   recall=1.0            recall<=1.0
   search_lat = X        search_lat = X / k
```

임베딩은 한 번만 계산하고, 같은 벡터를 여러 인덱스 구조에 넣어야 합니다. 그래야 결과 차이를 인덱스 구조 차이로 해석할 수 있습니다.

## 핵심 개념

| 용어 | 의미 |
| --- | --- |
| Flat index | 모든 벡터와 직접 거리를 계산하는 정확 검색 방식 |
| IVF | 코퍼스를 여러 클러스터로 나누고 일부 클러스터만 탐색하는 ANN 방식 |
| HNSW | 그래프 기반 ANN. 빠르고 recall이 높지만 메모리 사용량이 큼 |
| Recall@k | ANN 결과가 flat 기준 결과와 얼마나 일치하는지 |
| nprobe | IVF가 탐색할 클러스터 수. 높을수록 정확, 낮을수록 빠름 |
| nlist | 전체 클러스터 수 |

여기서 recall은 1편에서 본 hit rate와 다릅니다. hit rate는 골드 정답 문서가 들어왔는지를 묻고, 여기서의 recall은 **ANN 결과가 exact 검색 결과를 얼마나 잘 복제했는지**를 봅니다. 따라서 기준선은 골드셋이 아니라 flat 검색 결과입니다.

## 도구 이름만 보고 고를 때와 실험으로 고를 때

이전에는 "Chroma가 편하니까 쓰자"처럼 결정할 수 있습니다. 하지만 코퍼스가 커졌을 때 성능이 모자라면 뒤늦게 FAISS나 다른 저장소로 옮겨야 하고, 그 순간 "왜 답변이 예전과 다르지?"를 새로 디버깅해야 합니다.

이후에는 같은 임베딩 벡터를 두 인덱스에 동시에 넣고 한 표에서 비교합니다.

```text
index               recall@5  search_ms  memory_mb
IndexFlatIP         1.00      18.3       384
IndexIVFFlat (n=1)  0.72       2.1       386
IndexIVFFlat (n=4)  0.95       4.7       386
IndexIVFFlat (n=8)  0.99       7.9       386
```

이 표는 의사결정을 훨씬 쉽게 만듭니다. 예를 들어 `nprobe=4`가 품질과 속도의 균형점이라는 사실을 회의 자료에서 바로 설명할 수 있습니다.

## 단계별로 비교 실험 만들기

### 1단계 — 임베딩을 한 번만 계산하기

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
doc_vectors = model.encode(DOC_TEXTS, normalize_embeddings=True).astype("float32")
query_vectors = model.encode(QUERY_TEXTS, normalize_embeddings=True).astype("float32")
dimension = doc_vectors.shape[1]
```

이 단계에서 이미 실험의 절반이 결정됩니다. 임베딩 결과를 고정해 두어야 뒤의 차이를 인덱스 탓으로 돌릴 수 있습니다.

### 2단계 — Flat 인덱스 만들기

실행 코드는 `rag-benchmark-101/en/04-vectordb-selection/main.py`에 있습니다. 05편과 06편은 `GROQ_API_KEY`가 필요합니다.

```bash
cd en/04-vectordb-selection
python3 main.py
```

```python
import faiss

flat_index = faiss.IndexFlatIP(dimension)
flat_index.add(doc_vectors)
```

Flat 인덱스는 정확 검색의 기준선입니다. 느릴 수는 있어도 결과 자체는 비교 기준으로 신뢰할 수 있습니다.

### 3단계 — IVF 인덱스를 학습하고 추가하기

```python
nlist = max(1, int(np.sqrt(len(doc_vectors))))
quantizer = faiss.IndexFlatIP(dimension)
ivf_index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
ivf_index.train(doc_vectors)
ivf_index.add(doc_vectors)
ivf_index.nprobe = 4
```

`train()`이 중요한 이유는 IVF가 코퍼스를 클러스터로 나눠야 하기 때문입니다. Flat에는 없는 초기 비용이며, 운영에서는 재학습 주기까지 고려해야 합니다.

### 4단계 — 순수 검색 시간만 재기

![임베딩 시간과 검색 시간을 분리하는 경계](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-02-boundary-between-embedding-and-search-ti.ko.png)

*임베딩 시간과 검색 시간을 분리하는 경계*

```python
def search_only(index, query_vec, k=5, repeats=20):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        D, I = index.search(query_vec.reshape(1, -1), k)
        times.append((time.perf_counter() - t0) * 1000)
    return np.median(times), I[0]
```

여기서 핵심은 `index.search()`만 재는 것입니다. 임베딩 시간까지 섞으면 인덱스 구조 차이가 가려질 수 있습니다.

### 5단계 — flat 결과를 기준으로 recall 계산하기

```python
def recall_at_k(approx_ids, exact_ids):
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)

flat_results = [search_only(flat_index, q)[1] for q in query_vectors]
ivf_results = [search_only(ivf_index, q)[1] for q in query_vectors]
recall = np.mean([recall_at_k(a, e) for a, e in zip(ivf_results, flat_results)])
```

이 recall은 "정답 문서를 찾았는가"가 아니라, "ANN이 exact 검색 결과를 얼마나 따라갔는가"를 보는 값입니다. 따라서 1편의 검색 지표와 목적이 다릅니다.

### 6단계 — `nprobe`를 바꿔 가며 곡선 보기

![nprobe가 속도와 정확도를 조절하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-03-nprobe-trade-off-between-speed-and-accur.ko.png)

*nprobe가 속도와 정확도를 조절하는 흐름*

`nprobe`를 1, 2, 4, 8, 16으로 바꾸면 속도와 정확도 사이의 곡선이 드러납니다. 실제로는 이 곡선 중 어딘가에 항상 선택 가능한 지점이 있습니다. 좋은 비교는 그 지점을 찾는 과정입니다.

## 자주 하는 실수

- **임베딩 시간을 검색 시간에 섞기** — 인덱스 구조 차이를 제대로 읽을 수 없습니다.
- **한 번만 재고 결론 내리기** — 첫 호출은 느립니다. 여러 번 반복해 중앙값을 쓰는 편이 안정적입니다.
- **작은 코퍼스 결과를 일반화하기** — 1천 건에서 괜찮다고 100만 건에서도 같다고 볼 수 없습니다.
- **학습되지 않은 IVF에 `nprobe`만 조정하기** — `train()` 없이 `add()` 하면 오류가 납니다.
- **HNSW의 메모리 비용 무시하기** — 빠른 대신 메모리 요구량이 큽니다.

## 운영 환경으로 가져갈 때

실제 서비스에서는 인덱스 선택이 검색 품질만의 문제가 아닙니다. 설치 방식, 백업, 복구, 확장, 메타데이터 필터링, 업데이트 빈도까지 함께 봐야 합니다. FAISS는 라이브러리로 간단하지만 분산 운영은 직접 설계해야 하고, pgvector는 기존 PostgreSQL과 통합하기 좋지만 검색 특화 기능은 제한될 수 있습니다. Qdrant나 Weaviate는 운영 부담이 늘지만 서버형 기능이 풍부합니다.

또 검색 품질 목표도 도메인마다 다릅니다. 일반적인 RAG 응답이라면 recall 0.95 정도가 실용적일 수 있지만, 법률·의료처럼 누락 비용이 큰 도메인은 0.99 이상을 목표로 잡아야 할 수 있습니다. 따라서 VectorDB 선택은 빠른 것이 아니라 **내 도메인에서 필요한 정확도를 어떤 비용으로 달성하는가**의 문제입니다.

## 체크리스트

![실제 운영 조건으로 인덱스를 고르는 판단 축](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-04-index-decision-axes-for-real-workloads.ko.png)

*실제 운영 조건으로 인덱스를 고르는 판단 축*

- [ ] 임베딩 벡터를 한 번만 계산해 모든 인덱스에 동일하게 넣었는가?
- [ ] `index.search()`만 감싸 순수 검색 지연 시간을 측정했는가?
- [ ] 평균 대신 중앙값 지연 시간을 사용했는가?
- [ ] flat 결과를 기준선으로 recall@k를 계산했는가?
- [ ] `nprobe` 같은 ANN 파라미터를 바꿔 곡선을 확인했는가?

## 연습 문제

1. 코퍼스 크기를 100, 1,000, 10,000으로 늘리며 flat과 IVF의 검색 지연 시간 비율을 비교해 보세요.
2. `IndexHNSWFlat`을 추가해 flat, IVF, HNSW를 같은 표에서 비교해 보세요.
3. `nprobe=1, 4, 16`에서 recall을 재고, recall ≥ 0.95를 만족하는 최소 `nprobe`를 찾아 보세요.

## 정리와 다음 글

이 글에서는 같은 임베딩 벡터를 flat과 IVF 인덱스에 넣고, recall과 검색 지연 시간 사이의 트레이드오프를 비교했습니다. 핵심은 세 가지입니다. **벡터를 다시 만들지 말 것, 검색 시간만 측정할 것, 파라미터 곡선을 직접 볼 것**입니다.

다음 글에서는 검색기 뒤에 LLM을 연결해 종단 간 RAG 파이프라인을 평가합니다. 이제부터는 문서를 찾는 것뿐 아니라 답변 자체도 함께 점수화해야 합니다.

## VectorDB 후보를 동일 기준으로 평가하는 실무 표준

VectorDB 비교에서는 성능 숫자만큼 운영 조건의 동등성이 중요합니다. 아래 항목을 통일하지 않으면 벤치마크 결과는 거의 의미가 없어집니다.

| 항목 | 반드시 고정할 값 |
| --- | --- |
| 벡터 차원 | 동일 임베딩 모델(예: 384d) |
| 거리 함수 | cosine 또는 inner product 통일 |
| top-k | 제품에서 실제 사용하는 값 |
| 필터 조건 | 같은 metadata where clause |
| 하드웨어 | vCPU, RAM, 디스크 유형 동일 |

특히 거리 함수가 다르면 결과 해석 자체가 달라지므로, 보고서 첫 줄에 항상 명시하는 편이 좋습니다.

### 성능 수집 스크립트 예시

아래 코드는 후보별로 P50/P95 지연 시간과 recall@k를 수집하는 최소 골격입니다.

```python
import numpy as np
import time

def benchmark_search(index, queries, exact_results, k=5):
    latencies = []
    recalls = []

    for q_vec, exact_ids in zip(queries, exact_results):
        t0 = time.perf_counter()
        _, approx_ids = index.search(q_vec.reshape(1, -1), k)
        latencies.append((time.perf_counter() - t0) * 1000)
        recalls.append(len(set(approx_ids[0]) & set(exact_ids)) / k)

    return {
        "p50_ms": float(np.percentile(latencies, 50)),
        "p95_ms": float(np.percentile(latencies, 95)),
        "recall@k": float(np.mean(recalls)),
    }
```

이 함수는 라이브러리 의존도가 낮아서 FAISS, HNSW, 서버형 VectorDB 어댑터 모두 같은 출력 형식으로 맞추기 쉽습니다.

### 필터링 성능을 따로 측정해야 하는 이유

RAG 서비스에서는 날짜, 제품군, 고객사 같은 메타데이터 필터가 자주 사용됩니다. 필터 없는 성능만 측정하면 운영 체감과 괴리가 큽니다.

| 시나리오 | 예시 필터 | 관측 지표 |
| --- | --- | --- |
| 기본 검색 | 없음 | recall@k, p95 |
| 날짜 필터 | `year >= 2024` | recall@k, p95 |
| 다중 조건 | `team == "ml" AND severity >= 2` | recall@k, p95, 실패율 |

필터 적용 시 일부 엔진은 recall이 크게 떨어지거나 지연 시간이 급등할 수 있습니다. 그래서 필터 시나리오를 별도 표로 분리하는 편이 안전합니다.

### 서버형 VectorDB 운영 설정 예시

운영에서는 인덱스 알고리즘 파라미터뿐 아니라 네트워크/복제 설정도 함께 품질에 영향을 줍니다.

```yaml
vectordb:
  engine: qdrant
  collection: rag_docs_v2
  vector_size: 384
  distance: cosine
  hnsw:
    m: 32
    ef_construct: 128
    ef_search: 64
  replication:
    factor: 2
  write_consistency: majority
  read_timeout_ms: 500
```

이 구성값을 실험 리포트에 같이 보관하면 "같은 엔진인데 왜 지난달과 점수가 다르지"라는 질문에 즉시 답할 수 있습니다.

### 장애 상황을 가정한 성능 수치도 필요합니다

정상 상태만 측정하면 실제 운영 리스크를 과소평가하게 됩니다. 최소한 아래 두 가지는 별도 실행이 필요합니다.

1. 인덱스 워밍 전 첫 질의 100개
2. 리더 노드 장애 후 복구 중 질의 100개

예시 리포트:

```text
scenario                     recall@5   p95_ms
normal                       0.98       9.4
cold-start                   0.98       42.1
replica-recovery-in-progress 0.96       27.8
```

이 값이 있으면 SRE 팀과 SLA 논의를 할 때 훨씬 현실적인 기준을 세울 수 있습니다.

### 선택 규칙을 점수 함수로 명시하기

최종 선택을 회의 감으로 하지 않으려면 점수 함수를 선언하는 방법이 유효합니다.

```text
final_score = 0.5 * recall_norm + 0.3 * latency_norm + 0.2 * operability_norm
```

`operability_norm`에는 백업 난이도, 모니터링 통합성, 온콜 부담 같은 비기능 지표를 반영합니다. 이 규칙을 문서화해 두면 팀이 바뀌어도 같은 기준으로 다시 평가할 수 있습니다.

## 실전 부록: VectorDB 벤치마크 리포트 표준 필드

팀 간 공유를 위해 리포트 필드를 고정하면 회고와 재현이 쉬워집니다.

### JSON 필드 예시

```json
{
  "run_id": "20260521T021000-7d8e9f0",
  "embedding_model": "all-MiniLM-L6-v2",
  "vector_dim": 384,
  "distance": "cosine",
  "dataset_size": 100000,
  "candidate": "faiss-ivf",
  "params": {"nlist": 316, "nprobe": 8},
  "metrics": {
    "recall@5_vs_flat": 0.989,
    "p50_ms": 7.4,
    "p95_ms": 11.3,
    "memory_mb": 386
  }
}
```

이 스키마를 고정하면 후보가 늘어나도 같은 대시보드에서 비교할 수 있습니다.

### 필터 시나리오별 성능 표를 반드시 분리하기

| candidate | scenario | recall@5 | p95_ms |
| --- | --- | ---: | ---: |
| flat | no-filter | 1.00 | 24.7 |
| ivf(nprobe=8) | no-filter | 0.99 | 11.3 |
| ivf(nprobe=8) | year>=2024 | 0.98 | 14.8 |
| hnsw(ef=64) | team=ml | 0.97 | 12.1 |

필터 시나리오를 분리하지 않으면 운영 체감과 벤치마크 결과가 어긋나는 상황이 자주 발생합니다.

### 성능 측정 반복 횟수 권장값

- 코퍼스 10만 미만: 쿼리당 20회 반복, 중앙값 사용
- 코퍼스 10만~100만: 쿼리당 10회 반복, 중앙값 + p95 사용
- 코퍼스 100만 이상: 샘플 쿼리 200개 이상, 샤드별로 독립 측정

반복 횟수가 너무 적으면 일시적 캐시 효과를 실제 성능으로 오해할 수 있습니다.

### 운영 전환 시 필수 검증 항목

1. 백업/복구 테스트를 실제로 1회 이상 수행했는가?
2. 인덱스 재빌드 시간을 운영 점검 창 안에서 소화할 수 있는가?
3. 장애 시 fallback 검색 경로(flat 또는 이전 인덱스)가 준비되어 있는가?
4. 모니터링에서 p95, 오류율, timeout을 분리 관찰하는가?

VectorDB 선택은 단순한 성능 비교가 아니라 운영 체계 선택이라는 점을 끝까지 유지해야 합니다.

### 쿼리 부하 단계별 성능 테스트 예시

| QPS 구간 | candidate | recall@5 | p95(ms) | timeout rate |
| --- | --- | ---: | ---: | ---: |
| 10 | ivf(nprobe=8) | 0.99 | 10.9 | 0.0% |
| 50 | ivf(nprobe=8) | 0.99 | 14.2 | 0.1% |
| 100 | ivf(nprobe=8) | 0.98 | 28.6 | 0.9% |

정적 벤치마크뿐 아니라 부하 구간별 측정을 같이 수행해야 실제 운영 한계를 읽을 수 있습니다.

또한 결과 리포트에는 측정 시점의 데이터 적재율과 인덱스 파편화 수준을 함께 남기는 편이 좋습니다. 같은 후보라도 인덱스가 부분 갱신을 반복한 상태인지, 완전 재구축 직후인지에 따라 지연 시간과 recall 분포가 달라질 수 있기 때문입니다.

실무에서는 인덱스 파라미터를 변경할 때마다 이전 파라미터를 즉시 폐기하지 않고 A/B 섀도우 실행을 24시간 이상 유지하는 방법이 안전합니다. 트래픽 패턴이 시간대별로 달라질 수 있어서, 짧은 벤치마크만으로는 실제 운영 변동성을 충분히 포착하기 어렵습니다.

### VectorDB 벤치마크 결과 예시

아래 표는 동일한 100k 문서 벡터(384차원), 동일한 top-k=5 조건에서 측정한 예시입니다. 숫자는 환경에 따라 달라지지만, 해석 방법은 그대로 적용할 수 있습니다.

| 후보 | 파라미터 | Recall@5 (vs Flat) | P50 검색 지연(ms) | P95 검색 지연(ms) | 메모리(MB) |
| --- | --- | ---: | ---: | ---: | ---: |
| FAISS FlatIP | exact | 1.00 | 18.1 | 24.7 | 382 |
| FAISS IVFFlat | nlist=316, nprobe=4 | 0.95 | 4.8 | 7.2 | 386 |
| FAISS IVFFlat | nlist=316, nprobe=8 | 0.99 | 7.6 | 11.4 | 386 |
| HNSW | M=32, efSearch=64 | 0.98 | 3.9 | 6.0 | 514 |

이 표는 "무조건 가장 빠른 후보"를 고르는 데 쓰는 표가 아닙니다. 제품 요구사항(예: recall 0.97 이상, P95 10ms 이하)을 만족하는 후보를 빠르게 걸러내는 표입니다.

### 연결 설정 예시를 코드로 남기기

벤치마크 리포트에는 인덱스 성능만이 아니라 연결 설정도 함께 남겨야 재현이 가능합니다. 로컬 라이브러리형과 서버형 VectorDB를 함께 쓰는 팀에서는 설정 누락이 가장 흔한 재현 실패 원인입니다.

```python
# Qdrant 클라이언트 예시
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(
    url="http://qdrant:6333",
    api_key="${QDRANT_API_KEY}",
    timeout=5.0,
)

client.recreate_collection(
    collection_name="rag_docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)
```

```python
# pgVector 연결 예
import psycopg

conn = psycopg.connect(
    "host=pgvector-db port=5432 dbname=rag user=rag_app password=${PG_PASSWORD}"
)
with conn.cursor() as cur:
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    cur.execute("SELECT 1")
```

연결 예시를 남길 때는 타임아웃, 인증 방식, 벡터 차원, 거리 함수를 반드시 포함하는 편이 좋습니다. 이 네 가지가 다르면 같은 이름의 벤치마크라도 결과 해석이 달라집니다.

### 결과 해석을 의사결정 규칙으로 변환하기

벤치마크 숫자는 보고서로 끝나기 쉽습니다. 그래서 팀 규칙으로 연결하는 마지막 단계가 필요합니다. 예를 들면 아래처럼 명시할 수 있습니다.

- 검색 SLA가 `P95 <= 12ms`이고 recall 하한이 `0.97`이면 `IVF(nprobe=8)` 또는 `HNSW`만 후보로 유지합니다.
- 필터링 복잡도와 운영 단순성이 우선이면 `pgvector`를 우선 검토하고, 대규모 고QPS이면 전용 VectorDB를 우선 검토합니다.
- 모델 차원 변경(384 -> 1024)이 발생하면 기존 벤치마크를 폐기하고 동일 절차로 재측정합니다.

이처럼 선택 규칙을 숫자와 함께 문서화하면 "왜 이 VectorDB를 선택했는가"를 다음 분기에도 설명할 수 있습니다.

## 처음 질문으로 돌아가기

- **VectorDB는 기능 목록이 아니라 어떤 운영 조건으로 비교해야 할까요?**
  데이터 크기, latency 목표, 필터 조건, 업데이트 빈도, 운영팀 역량, 비용 모델을 기준으로 비교해야 합니다.

- **같은 임베딩과 corpus에서 VectorDB만 바꿔 보려면 무엇을 고정해야 할까요?**
  임베딩, chunking, query set, gold labels, metadata schema, top_k, 하드웨어 조건을 고정해야 VectorDB 차이를 볼 수 있습니다.

- **정확도, latency, 필터링, 운영 복잡도가 충돌할 때 어떤 기준으로 선택해야 할까요?**
  제품 요구사항별 가중치를 정해 tradeoff를 판단해야 합니다. 예를 들어 필터 정확성이 핵심이면 약간 느린 후보가 더 나을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG Evaluation and Benchmarking 101 (1/6): RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정](./02-retrieval-benchmarking.md)
- [RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교](./03-embedding-comparison.md)
- **RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준 (현재 글)**
- RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가 (예정)
- RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [FAISS indexes wiki](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [pgvector](https://github.com/pgvector/pgvector)
- [Qdrant benchmarks](https://qdrant.tech/benchmarks/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-benchmark-101/ko/04-vectordb-selection)

Tags: RAG, VectorDB, Benchmarking, LLM
