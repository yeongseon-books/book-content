
# RAG 평가 지표 이해

> RAG Benchmark 101 시리즈 (1/6)

<!-- a-grade-intro:begin -->
## 핵심 질문

RAG 시스템의 품질을 어떤 지표로 정의하고 측정해야 하나요?

이 글은 그 질문에 답하기 위해 RAG 평가 지표의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- RAG retrieval 단계에서 가장 자주 쓰이는 세 지표 — Precision@k, Recall@k, MRR — 의 정의와 차이를 손으로 계산할 수 있습니다.
- 한 쿼리 점수와 여러 쿼리 평균 점수를 분리해서 읽는 습관을 만듭니다.
- LLM 기반 평가로 넘어가기 전에 retrieval 품질을 먼저 분리해 진단해야 하는 이유를 이해합니다.
- Python 한 파일로 평가 지표를 직접 계산하는 minimal example을 실행할 수 있습니다.

![이 글에서 답할 질문](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*

## 이 글에서 답할 질문

- Precision@k, Recall@k, MRR는 각각 무엇을 측정하고, 어떤 질문에 답하는가?
- 왜 retrieval 지표를 LLM 기반 평가와 분리해서 측정해야 하는가?
- 한 쿼리 점수와 전체 평균 점수를 함께 쓰는 것이 왜 위험한가?
- k 값을 어떻게 골라야 하고, k가 바뀌면 세 지표는 어떻게 변하는가?
- Python 한 파일로 이 지표들을 직접 계산하는 가장 짧은 코드는 어떤 모양인가?

## 왜 중요한가

RAG 시스템이 잘못된 답을 내놓을 때 원인은 두 곳 중 하나입니다: **retrieval이 틀린 문서를 줬거나, LLM이 맞는 문서를 줘도 잘못 해석했거나.**
이 두 layer를 섞어서 평가하면 디버깅이 불가능합니다.
"왜 답이 이상하지?" → "모르겠다, 모델 바꿔보자" → "여전히 이상하다" 같은 무한 루프가 시작됩니다.

retrieval 지표는 RAG의 첫 번째 layer를 **LLM과 무관하게** 측정하는 도구입니다.
정답 문서 ID 집합과 검색 결과 ID 리스트만 있으면 계산되므로, LLM 호출 비용 없이 빠르게 반복할 수 있습니다.
이 글에서는 가장 기본이 되는 세 지표를 분해해 봅니다.

## Mental Model

retrieval 지표는 두 개의 집합을 비교하는 작업입니다.

1. **Gold set (정답 문서 집합)** — 이 쿼리에 대해 "관련 있다"고 라벨링된 문서 ID들. 사람이 만들거나 기존 dataset에서 가져옵니다.
2. **Retrieved list (검색 결과 리스트)** — retriever가 반환한 문서 ID들. **순서가 있습니다.**

세 지표는 같은 두 집합에서 다른 질문을 답합니다:

- **Precision@k**: "내가 가져온 top-k 중 몇 개가 정답인가?" → 정확도
- **Recall@k**: "전체 정답 중 몇 개를 top-k에서 찾았는가?" → 누락률의 반대
- **MRR**: "첫 번째 정답이 몇 번째 순위에 등장했는가?" → 순위 품질

세 지표 모두 한 쿼리에서 계산되고, 여러 쿼리 평균으로 시스템 전체 점수가 됩니다.

## 핵심 개념

### 1. Precision@k와 Recall@k

| 쿼리 | 정답 집합 | 검색 결과 (top-3) | Precision@3 | Recall@3 |
| --- | --- | --- | --- | --- |
| Q1 | {A, B, C} | [A, X, B] | 2/3 = 0.67 | 2/3 = 0.67 |
| Q2 | {A} | [A, X, Y] | 1/3 = 0.33 | 1/1 = 1.00 |
| Q3 | {A, B, C, D, E} | [A, B, C] | 3/3 = 1.00 | 3/5 = 0.60 |

Q2는 **Precision은 낮지만 Recall은 완벽**합니다. 정답이 1개뿐인데 top-3을 다 채워야 했기 때문입니다.
Q3은 **Precision은 완벽하지만 Recall은 낮습니다.** 정답 5개 중 3개만 잡았습니다.
이 둘을 함께 보지 않으면 잘못된 결론에 도달합니다.

![상위 k 결과와 정답 집합의 교집합 계산 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-02-top-k-overlap-and-metric-calculation-flo.ko.png)

*상위 k 결과와 정답 집합의 교집합 계산 흐름*

### 2. MRR (Mean Reciprocal Rank)

MRR은 **첫 번째 정답의 순위만** 봅니다. 1번 위치라면 1.0, 2번이면 0.5, 3번이면 0.33...
첫 정답 이후의 결과는 무시합니다.

UX 관점에서 MRR이 중요한 이유: 사용자는 검색 결과 첫 화면에서 빠르게 답을 찾고 싶어 합니다.
"정답이 어딘가에는 있다"보다 "정답이 위쪽에 있다"가 훨씬 중요합니다.

### 3. k의 선택

`k=3`, `k=5`, `k=10`은 RAG context window 크기와 직결됩니다.
LLM에게 5개 청크를 prompt로 넣을 거면 `Recall@5`가 가장 의미 있는 지표입니다.
benchmark에서 k를 임의로 정하면 production 동작과 단절된 점수가 나옵니다.

## Before-After

### Before (LLM output만 보고 판단)

```python
result = rag_pipeline.query("RAG가 뭐예요?")
print(result)  # "RAG는 검색 증강 생성을 의미합니다..."
# → "음, 답이 그럴듯하네." 끝.
```

retrieval이 틀렸는지, LLM이 hallucinate했는지 알 수 없습니다.

### After (retrieval 지표를 먼저 측정)

```python
case = QueryCase(
    question="RAG가 뭐예요?",
    retrieved_ids=retriever.search("RAG가 뭐예요?", k=5),
    relevant_ids={"doc-rag-01", "doc-rag-02"},
)
metrics = evaluate_case(case, k=5)
print(metrics)  # {"precision@5": 0.4, "recall@5": 1.0, "mrr": 0.5}
```

이제 알 수 있습니다: retrieval은 정답을 모두 찾았지만(Recall=1.0), 첫 정답이 2위(MRR=0.5)이고 절반은 노이즈(Precision=0.4)입니다.
다음 단계는 **reranker 도입**이 적절한 가설이 됩니다.

## 단계별 실습

### Step 1: 평가 코드 구조

```python
from dataclasses import dataclass

@dataclass
class QueryCase:
    question: str
    retrieved_ids: list[str]   # 순서 있음
    relevant_ids: set[str]     # 순서 없음

def precision_at_k(case: QueryCase, k: int) -> float:
    top_k = case.retrieved_ids[:k]
    hits = sum(1 for d in top_k if d in case.relevant_ids)
    return hits / k

def recall_at_k(case: QueryCase, k: int) -> float:
    top_k = case.retrieved_ids[:k]
    hits = sum(1 for d in top_k if d in case.relevant_ids)
    return hits / len(case.relevant_ids)

def reciprocal_rank(case: QueryCase) -> float:
    for i, doc_id in enumerate(case.retrieved_ids, start=1):
        if doc_id in case.relevant_ids:
            return 1.0 / i
    return 0.0
```

### Step 2: 여러 쿼리에 적용

```python
cases = [
    QueryCase("Q1", ["A", "X", "B"], {"A", "B", "C"}),
    QueryCase("Q2", ["A", "X", "Y"], {"A"}),
    QueryCase("Q3", ["A", "B", "C"], {"A", "B", "C", "D", "E"}),
]

for case in cases:
    print(f"{case.question}: P@3={precision_at_k(case, 3):.2f}, "
          f"R@3={recall_at_k(case, 3):.2f}, MRR={reciprocal_rank(case):.2f}")

# 평균
import statistics
avg_p = statistics.mean(precision_at_k(c, 3) for c in cases)
avg_r = statistics.mean(recall_at_k(c, 3) for c in cases)
avg_mrr = statistics.mean(reciprocal_rank(c) for c in cases)
print(f"AVG: P@3={avg_p:.2f}, R@3={avg_r:.2f}, MRR={avg_mrr:.2f}")
```

### Step 3: 실행

```bash
cd /root/Github/rag-benchmark-101/ko/01-evaluation-metrics
python3 main.py
```

![Precision@k와 Recall@k가 갈리는 판단 축](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-03-precision-k-versus-recall-k-decision-axe.ko.png)

*Precision@k와 Recall@k가 갈리는 판단 축*

## 자주 하는 실수

- **평균만 보고 끝냄** — 평균 P@3 = 0.6이라도, 어떤 쿼리는 0.0이고 어떤 쿼리는 1.0일 수 있습니다. 항상 per-query 출력을 함께 봐야 합니다.
- **Precision과 Recall 중 하나만 측정** — 한쪽만 보면 "많이 가져왔지만 틀렸다" 또는 "정확하지만 놓쳤다"를 구분할 수 없습니다.
- **MRR을 전체 retrieval 품질로 오해** — MRR은 첫 정답 위치만 봅니다. top-3 안에 정답 3개가 모두 있어도, 첫 정답이 1위면 MRR=1.0입니다.
- **k를 production과 다르게 설정** — RAG가 LLM에 5청크를 주는데 benchmark는 k=10을 쓰면 점수가 부풀려집니다.
- **정답 집합을 너무 좁게 정의** — "이 문서만 정답"이라고 하면 의미상 동등한 다른 문서를 retriever가 찾아도 점수가 깎입니다.

![첫 관련 문서 위치가 MRR을 바꾸는 순위 차이](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-04-rank-position-changes-the-mrr-signal.ko.png)

*첫 관련 문서 위치가 MRR을 바꾸는 순위 차이*

## 실무에서

production RAG 평가의 현실적 가이드:

- **Gold dataset 만들기** — 처음에는 50~100개 질문으로 충분합니다. 도메인 전문가에게 "이 질문에 답하려면 어떤 문서가 필요한가?"를 라벨링 받으세요.
- **여러 k에서 측정** — Recall@1, Recall@3, Recall@5, Recall@10을 함께 보면 retriever의 "rank profile"이 보입니다.
- **실패 사례 분석** — Recall@10이 0인 쿼리가 가장 가치 있습니다. 정답이 top-10에 없으면 retriever가 근본적으로 틀린 것이고, 모델이나 chunking 전략을 바꿔야 합니다.
- **CI에 통합** — embedding 모델이나 chunking 변경 시 metrics가 회귀하지 않는지 자동 검증.
- **다음 단계 지표** — nDCG는 ranking quality를 더 정밀하게 측정하지만 binary 라벨이 아니라 graded relevance가 필요해 데이터 구축 비용이 큽니다.

## 실무에서는 이렇게 생각한다

평가 지표를 도입할 때 가장 흔한 실수는 Precision@k와 Recall@k를 동시에 올리려는 것입니다. k를 늘리면 Recall은 오르지만 Precision은 떨어집니다. 실무에서는 사용자가 실제로 보는 결과 수(k)를 먼저 고정하고, 그 k에서 Recall이 촩분한지를 우선 확인합니다. 사용자가 3개만 보는 UI라면 Recall@3이 우선이고, 검색 결과 페이지가 있다면 Precision@10이 더 중요합니다.

MRR은 "첫 번째 맞는 결과가 몇 번째에 나오는가"만 보므로, 사용자가 첫 결과만 클릭하는 패턴일 때 유용합니다. 하지만 RAG에서는 여러 문서를 context로 넣으므로, MRR만으로는 부족합니다. 대부분의 팀은 Recall@k를 주 지표로, Precision@k를 보조 지표로 쳐다보는 것이 현실적입니다.

평가 지표를 보고하는 단위도 중요합니다. 쿼리 하나당 점수를 보면 노이즈가 많고, 전체 평균만 보면 특정 카테고리의 실패가 숨습니다. 카테고리별 평균(intent별, 문서 타입별)을 나눠 보는 것이 운영에서 가장 쓸모있는 분석 단위입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **검색·생성 분리** — retrieval과 generation 지표를 항상 분리해 원인 분석을 가능하게 합니다.
- **Recall@k와 nDCG** — 검색 품질은 recall@k와 nDCG로 측정 기준을 단일화합니다.
- **Faithfulness 우선** — 생성 품질은 정답성보다 근거 충실도를 먼저 봅니다.
- **LLM-as-judge 한계** — 비용·편향을 인지하고 사람 평가와 교차 검증합니다.
- **회귀 셋 고정** — 지표 정의·데이터·프롬프트를 모두 버전으로 고정합니다.

## 체크리스트

- [ ] 정답 문서 집합(`relevant_ids`)을 쿼리별로 명시했는가?
- [ ] 평가에 쓰는 `k` 값이 production RAG의 context window와 일치하는가?
- [ ] Precision@k, Recall@k, MRR을 모두 측정하는가?
- [ ] 평균과 per-query 출력을 함께 리포트하는가?
- [ ] Recall@k가 0인 쿼리(catastrophic failure)를 별도로 분석하는가?
- [ ] benchmark가 CI에 통합되어 회귀를 잡는가?

## 연습 문제

1. 정답 집합 `{A, B, C}`에 대해 검색 결과가 `[X, A, Y, B, C]`라면 Precision@3, Recall@3, MRR은 각각 얼마입니까?
2. 두 retriever A, B의 평균 Recall@5는 같지만 평균 MRR이 다릅니다. 어느 쪽이 production UX에 더 적합할까요? 이유는?
3. RAG가 LLM에게 정확히 3청크를 prompt로 넣습니다. 가장 중요하게 봐야 할 지표 두 개는 무엇입니까?

![쿼리별 점수와 평균 점수를 함께 읽는 리포트 구조](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-05-per-query-and-average-report-reading-flo.ko.png)

*쿼리별 점수와 평균 점수를 함께 읽는 리포트 구조*

## 정리·다음 글

이번 글의 핵심:

- RAG 평가는 retrieval과 generation을 분리하는 데서 시작합니다.
- Precision@k, Recall@k, MRR은 같은 데이터에서 다른 질문을 답합니다.
- 평균 점수는 per-query 점수와 함께 봐야 의미가 있습니다.
- benchmark의 `k`는 production RAG의 context window와 같아야 합니다.

다음 글에서는 **검색 성능 측정**으로 들어갑니다.
실제 retriever를 벤치마크 루프에 넣어 latency, hit rate, ranking quality를 종합 측정하는 방법을 다룹니다.

---

## 시리즈 목차

- **RAG 평가 지표 이해 (현재 글)**
- 검색 성능 측정 (예정)
- 임베딩 모델 비교 (예정)
- VectorDB 선택 기준 (예정)
- 종단 간 RAG 파이프라인 평가 (예정)
- RAG 벤치마크 완성 (예정)

---

## 참고 자료

- [Wikipedia: Mean reciprocal rank](https://en.wikipedia.org/wiki/Mean_reciprocal_rank)
- [Stanford IR book: Evaluation in information retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)
- [BEIR: A heterogeneous benchmark for zero-shot evaluation of IR models](https://arxiv.org/abs/2104.08663)
- [MTEB: Massive Text Embedding Benchmark](https://arxiv.org/abs/2210.07316)

Tags: RAG, VectorDB, Benchmarking, LLM

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
