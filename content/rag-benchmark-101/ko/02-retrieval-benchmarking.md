---
title: "RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정"
series: rag-benchmark-101
episode: 2
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
- Benchmarking
- Hit-Rate
- Latency
- MRR
last_reviewed: '2026-05-15'
seo_description: 검색 벤치마크는 질문, 정답 문서, 순위 결과, 지표가 같은 루프 안에 묶여 있을 때만 의미가 있습니다.
---

# RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정

검색 벤치마크는 질문, 정답 문서, 순위 결과, 지표가 같은 루프 안에 묶여 있을 때만 의미가 있습니다.

이 글은 RAG 평가와 벤치마크 101 시리즈의 두 번째 글입니다. 여기서는 검색기 변경이 실제 개선인지, 단지 몇 개 예제가 그럴듯해 보인 것인지 구분할 수 있는 최소 측정 루프를 만들겠습니다.

## 먼저 던지는 질문

- 검색 성능을 감이 아니라 벤치마크 루프로 보려면 무엇을 고정해야 할까요?
- hit rate, MRR, latency는 검색기의 어떤 다른 측면을 측정할까요?
- 작은 gold set으로 시작해도 의미 있는 회귀 검사를 만들 수 있을까요?

## 큰 그림

![질의와 지연 시간을 함께 묶는 검색 벤치마크 루프](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-01-benchmark-loop-for-queries-and-latency.ko.png)

*질의와 지연 시간을 함께 묶는 검색 벤치마크 루프*

이 그림에서는 질문, 정답 문서, 검색 결과, 지표 계산이 하나의 반복 가능한 루프로 묶이는 흐름을 봅니다. 벤치마크는 특정 검색기가 아니라 같은 조건으로 다시 관찰할 수 있는 측정 루프입니다.

> 검색 벤치마크의 핵심은 벡터 DB나 인덱스 자체가 아닙니다. **질문, 정답 문서, 순위 결과, 지표 수집이 반복 가능한 하나의 루프**로 묶여 있다는 점이 핵심입니다.

## 왜 이 주제가 중요한가

1편에서는 hit rate, MRR, nDCG를 손으로 계산해 보았습니다. 하지만 실제 RAG 시스템에서 검색기는 고정돼 있지 않습니다. 임베딩 모델을 바꾸고, 청크 크기를 바꾸고, 코퍼스가 늘어날 때마다 검색 결과도 함께 흔들립니다. 이때 측정 루프가 없으면 의사결정은 결국 "체감상 좋아 보인다" 수준에 머무릅니다.

지표를 코드로 옮기는 이유는 세 가지입니다. 첫째, 임베딩이나 청크 전략을 바꿨을 때 **회귀를 즉시 발견할 수 있습니다.** 둘째, 같은 루프를 CI에 넣으면 사람마다 다른 인상 비평을 줄일 수 있습니다. 셋째, 품질 점수와 함께 지연 시간을 기록하면 Recall은 좋아졌지만 응답 시간이 두 배로 늘어난 변경을 초기에 걸러낼 수 있습니다.

이 글에서 만드는 루프는 작지만 완전합니다. 이후 글에서 임베딩 모델 비교와 VectorDB 비교를 할 때도 같은 골격을 그대로 재사용합니다. 따라서 여기서 중요한 것은 특정 라이브러리 사용법보다 **측정 대상을 어떻게 고정하고 어떤 결과를 남기는가**입니다.

## 기본 멘탈 모델

검색 벤치마크는 다음 네 요소를 하나의 흐름으로 묶습니다.

```text
QUERIES (question + gold ids)
   │
   ▼
retriever.invoke(question)  ──►  ranked_ids  ──►  metric(ranked_ids, gold_ids)
   │                                                   │
   ▼                                                   ▼
latency_ms                                       hit_rate / MRR
```

여기서 할 일은 단순합니다. `retriever.invoke()`만 타이머로 감싸 검색 구간의 순수 지연 시간을 분리합니다. 검색 결과를 `metadata["id"]`로 정규화해 두면, 이후 BM25·FAISS·하이브리드 검색기로 바뀌어도 평가 함수는 그대로 재사용할 수 있습니다.

이 멘탈 모델이 중요한 이유는 확장성이 있기 때문입니다. 지금은 단일 검색기지만, 나중에 reranker나 다른 벡터 저장소가 들어와도 이 구조만 유지하면 비교 실험을 같은 틀에서 수행할 수 있습니다.

## 핵심 개념

| 용어 | 의미 | 단위 |
| --- | --- | --- |
| Gold set | 질문과 관련 문서 ID 집합 | 질문 수 |
| Hit rate@k | 상위 k개에 정답 문서가 한 번이라도 등장한 질의의 비율 | 0.0–1.0 |
| MRR | 첫 정답 문서 순위의 역수 평균 | 0.0–1.0 |
| Retrieval latency | `retriever.invoke()` 한 번의 소요 시간 | 밀리초 |
| p95 latency | 전체 지연 시간의 95퍼센타일 | 밀리초 |

평균 지연 시간만 보면 꼬리 구간을 놓칩니다. 실제 사용자 불만은 보통 느린 일부 요청에서 터지므로, 평균과 함께 p95를 반드시 보는 습관이 필요합니다.

## 측정 루프가 없을 때와 있을 때

이전에는 "임베딩 모델을 바꿨더니 좀 더 좋아진 것 같다"는 말이 근거가 됩니다. 손으로 몇 개 질문을 던져 보고 느낌을 말하는 수준입니다. 며칠 뒤 다른 도메인 질문에서 성능이 떨어져도, 그 변경 때문인지 다른 변경 때문인지 설명할 수 없습니다.

이후에는 같은 `QUERIES` 집합으로 두 검색기를 돌리고, hit rate·MRR·평균 latency·p95 latency를 한 줄에서 비교합니다. 만약 hit rate가 0.90에서 1.00으로 올랐지만 p95 latency가 80ms에서 250ms로 뛰었다면, 이 변경을 받아들일지 말지를 분명한 근거 위에서 판단할 수 있습니다.

## 단계별로 벤치마크 만들기

### 1단계 — 골드셋 정의하기

먼저 질문과 관련 문서 ID를 짝지어 적습니다. 처음에는 3~5개만 있어도 충분합니다.

```python
QUERIES = [
    ("What distance does FAISS use by default?", {"doc-faiss-basics"}),
    ("What does MRR measure?", {"doc-mrr-intro"}),
    ("Why is chunk size important in RAG?", {"doc-chunking"}),
]
```

작게 시작해도 괜찮습니다. 이 단계의 목표는 완벽한 데이터셋이 아니라, 같은 질문 세트를 반복 실행할 수 있는 루프를 만드는 것입니다.

### 2단계 — 측정 루프 만들기

실행 코드는 `rag-benchmark-101/en/02-retrieval-benchmarking/main.py`에 있습니다. 05편과 06편은 `GROQ_API_KEY`가 필요합니다.

```bash
cd en/02-retrieval-benchmarking
python3 main.py
```

```python
import time
import numpy as np

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
latencies_ms = []
all_ranked = []

for question, _ in QUERIES[:1]:
    retriever.invoke(question)  # warm-up

for question, relevant_ids in QUERIES:
    started_at = time.perf_counter()
    docs = retriever.invoke(question)
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    ranked_ids = [doc.metadata["id"] for doc in docs]
    latencies_ms.append(elapsed_ms)
    all_ranked.append((question, ranked_ids, relevant_ids))

p95_latency_ms = float(np.percentile(latencies_ms, 95))
```

여기서 중요한 점은 두 가지입니다. 첫째, 짧은 구간은 `time.perf_counter()`로 측정합니다. 둘째, 결과를 문서 ID 목록으로 정규화해 둡니다. 그래야 뒤의 평가 함수가 검색기 구현에 묶이지 않습니다.

워밍업 호출도 실무에서는 거의 필수입니다. 첫 호출에는 모델 로드, 파일 시스템 캐시, 네트워크 초기화가 섞일 수 있습니다. 워밍업 없이 평균을 내면 실제 운영에서 반복 호출될 때의 성능보다 더 느리게 기록될 수 있습니다.

### 3단계 — 지표 계산하기

![Hit rate와 MRR를 함께 읽는 검색 품질 축](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-02-retrieval-quality-axes-with-hit-rate-and.ko.png)

*Hit rate와 MRR를 함께 읽는 검색 품질 축*

```python
def hit_rate(ranked, gold):
    return 1.0 if any(d in gold for d in ranked) else 0.0

def reciprocal_rank(ranked, gold):
    for idx, doc_id in enumerate(ranked, start=1):
        if doc_id in gold:
            return 1.0 / idx
    return 0.0

hits = [hit_rate(r, g) for _, r, g in all_ranked]
rrs = [reciprocal_rank(r, g) for _, r, g in all_ranked]

print(f"hit_rate@3 = {sum(hits)/len(hits):.2f}")
print(f"MRR        = {sum(rrs)/len(rrs):.2f}")
print(f"avg latency = {sum(latencies_ms)/len(latencies_ms):.1f} ms")
print(f"p95 latency = {p95_latency_ms:.1f} ms")
```

Hit rate는 정답이 상위 k 안에 한 번이라도 들어왔는지만 보고, MRR은 첫 정답의 순위를 봅니다. 둘을 함께 봐야 "찾기는 찾는데 뒤에 나온다" 같은 실패를 구분할 수 있습니다.

### 4단계 — 결과를 남기기

평균값만 저장하면 디버깅이 막힙니다. 질문별 `ranked_ids`를 로그에 남겨야 어느 질문에서 회귀가 났는지 확인할 수 있습니다. 실제 운영에서는 평균 점수보다 **무너진 질문 목록**이 더 큰 가치를 가집니다.

```python
report_rows = []
for question, ranked_ids, relevant_ids in all_ranked:
    report_rows.append({
        "question": question,
        "ranked_ids": ranked_ids,
        "relevant_ids": sorted(relevant_ids),
        "hit": hit_rate(ranked_ids, relevant_ids),
        "rr": reciprocal_rank(ranked_ids, relevant_ids),
    })

summary = {
    "hit_rate@3": round(sum(hits) / len(hits), 2),
    "MRR": round(sum(rrs) / len(rrs), 2),
    "avg_latency_ms": round(sum(latencies_ms) / len(latencies_ms), 1),
    "p95_latency_ms": round(p95_latency_ms, 1),
}

print(summary)
for row in report_rows:
    print(row)
```

```text
{'hit_rate@3': 0.67, 'MRR': 0.56, 'avg_latency_ms': 4.8, 'p95_latency_ms': 6.1}
{'question': 'What distance does FAISS use by default?', 'ranked_ids': ['doc-faiss-basics', 'doc-ann-overview', 'doc-chunking'], 'relevant_ids': ['doc-faiss-basics'], 'hit': 1.0, 'rr': 1.0}
{'question': 'What does MRR measure?', 'ranked_ids': ['doc-bm25', 'doc-mrr-intro', 'doc-ranking'], 'relevant_ids': ['doc-mrr-intro'], 'hit': 1.0, 'rr': 0.5}
```

이 출력은 바로 행동으로 이어집니다. 두 번째 질문처럼 hit는 1.0인데 rr이 0.5라면, 검색 자체보다 순위화 품질을 먼저 의심해야 합니다.

### 5단계 — 결과를 읽고 첫 번째 점검 순서를 정하기

| 관측값 | 먼저 볼 것 | 흔한 원인 |
| --- | --- | --- |
| hit rate 낮음, latency 양호 | 임베딩/청크 전략 | 관련 문서를 아예 못 찾음 |
| hit rate 높음, MRR 낮음 | reranker, 검색 점수 결합 방식 | 정답은 있지만 뒤쪽에 배치됨 |
| quality 양호, p95만 높음 | 인프라, 캐시, 네트워크 | 일부 요청만 느림 |
| 평균 양호, 특정 질문만 붕괴 | 질문별 로그 | 도메인 편향, gold set 누락 |

이 표가 중요한 이유는 "숫자가 이상하다"에서 끝나지 않게 해 주기 때문입니다. 벤치마크는 결국 **다음 수정 방향을 좁혀 주는 도구**여야 합니다.

## 자주 하는 실수

![Hit rate는 높지만 순위 품질은 약한 실패 패턴](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-03-high-hit-rate-with-weak-ranking.ko.png)

*Hit rate는 높지만 순위 품질은 약한 실패 패턴*

- **Hit rate만 믿기** — hit rate가 1.0이어도 MRR이 낮으면 정답이 늘 뒤쪽에 배치된 상태입니다.
- **임베딩 시간까지 같이 재기** — 검색기 자체의 속도를 보고 싶다면 `retriever.invoke()`만 재야 합니다.
- **`time.time()` 사용하기** — 시스템 시계 변화에 민감합니다. 짧은 구간은 `time.perf_counter()`가 맞습니다.
- **첫 호출까지 그대로 집계하기** — 첫 호출에는 모델 로드와 캐시 워밍이 섞입니다. 워밍업 호출 후 본 측정을 하는 편이 안정적입니다.
- **작은 코퍼스 결과를 일반화하기** — 5개 문서에서 완벽하게 나왔다고 운영 환경에서도 같을 것이라고 생각하면 안 됩니다. 초기에는 검색기 성능보다 **측정 루프가 제대로 동작하는지**를 먼저 검증해야 합니다.

## 운영 환경으로 가져갈 때

운영에 가까워질수록 결과와 함께 메타데이터를 남겨야 합니다. 임베딩 모델 이름, 청크 크기, 검색기 유형, 코퍼스 해시가 없으면 같은 결과를 다시 재현하기 어렵습니다.

지연 시간도 평균만으로는 부족합니다. 평균은 빠른 요청에 끌려 내려가기 쉽기 때문에 p95, 가능하면 p99도 함께 기록해야 합니다. 그리고 PR마다 전량을 돌리기 부담스러워지면, 계층 표본 추출로 50~100개 정도를 빠르게 돌리고 전체 데이터셋은 야간 작업으로 분리하는 방식이 현실적입니다.

결국 이 벤치마크의 목적은 숫자를 예쁘게 만드는 것이 아닙니다. **같은 질문 세트에 대해 같은 검색기를 반복 관찰할 수 있게 만드는 것**이 목적입니다. 이 루프가 있어야 3편과 4편의 비교 실험도 의미를 갖습니다.

## 체크리스트

![질문과 정답 ID를 함께 남기는 벤치마크 기록](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-04-benchmark-record-with-gold-ids-and-logs.ko.png)

*질문과 정답 ID를 함께 남기는 벤치마크 기록*

- [ ] 질문별 관련 문서 ID를 적었다.
- [ ] `retriever.invoke()`만 감싸서 검색 지연 시간을 분리했다.
- [ ] hit rate, MRR, 평균 latency, p95 latency를 함께 본다.
- [ ] 질문별 순위 결과 ID도 출력에 남긴다.
- [ ] 실행에 사용한 임베딩 모델, 청크 크기, k를 기록한다.

## 연습 문제

1. 한 번의 실행에서 `k=1`, `k=3`, `k=5`의 hit rate를 함께 출력하도록 루프를 바꿔 보세요. k가 커질수록 hit rate와 MRR는 어떻게 움직일까요?
2. `time.perf_counter()`를 `time.time()`으로 바꾸고 문서를 읽어 보세요. 어떤 상황에서 측정이 틀릴 수 있을까요?
3. 루프 앞에 워밍업 호출을 하나 추가해 보세요. 워밍업 유무에 따라 첫 측정 지연 시간이 얼마나 달라지나요?

## 정리와 다음 글

이 글에서는 손으로 계산하던 지표를 실제 검색기에 올려, hit rate·MRR·latency를 함께 수집하는 루프를 만들었습니다. 핵심은 특정 라이브러리보다 **반복 가능한 입력 집합과 결과 기록 방식**입니다.

다음 글에서는 같은 루프를 그대로 둔 채 임베딩 모델만 바꿔 봅니다. 코드 변경은 한 줄에 가깝지만, 결과 해석은 의외로 까다롭습니다.

## 처음 질문으로 돌아가기

- **검색 성능을 감이 아니라 벤치마크 루프로 보려면 무엇을 고정해야 할까요?**
  질문 집합, gold 문서 ID, 평가 k, 문서 버전, 측정 코드를 고정해야 변경 전후를 비교할 수 있습니다.

- **hit rate, MRR, latency는 검색기의 어떤 다른 측면을 측정할까요?**
  hit rate는 정답이 포함됐는지, MRR은 첫 정답 순위, latency는 검색 응답 시간을 측정합니다. 셋을 함께 봐야 품질과 속도 균형을 읽을 수 있습니다.

- **작은 gold set으로 시작해도 의미 있는 회귀 검사를 만들 수 있을까요?**
  작은 gold set도 핵심 질문을 잘 대표하면 회귀 감지에 유용합니다. 다만 대표 범위와 한계를 결과에 명시해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG Evaluation and Benchmarking 101 (1/6): RAG 평가 지표 이해](./01-evaluation-metrics.md)
- **RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정 (현재 글)**
- RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교 (예정)
- RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준 (예정)
- RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가 (예정)
- RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain FAISS integration](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [FAISS documentation](https://faiss.ai/)
- [Python `time.perf_counter`](https://docs.python.org/3/library/time.html#time.perf_counter)
- [BEIR: heterogeneous benchmark for IR](https://github.com/beir-cellar/beir)

Tags: RAG, VectorDB, Benchmarking, LLM
