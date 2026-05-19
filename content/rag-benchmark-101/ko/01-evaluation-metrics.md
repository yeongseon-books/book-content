---
title: RAG 평가 지표 이해
series: rag-benchmark-101
episode: 1
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
- Precision
- Recall
- MRR
last_reviewed: '2026-05-15'
seo_description: 정답 문서 집합과 검색 결과 목록을 분리해서 보면 Precision@k, Recall@k, MRR가 무엇을 말하는지 훨씬 선명해집니다.
---

# RAG 평가 지표 이해

정답 문서 집합과 검색 결과 목록을 분리해서 보면 Precision@k, Recall@k, MRR가 각각 무엇을 드러내는지 훨씬 선명해집니다.

이 글은 RAG 평가와 벤치마크 101 시리즈의 첫 번째 글입니다. 여기서는 생성 품질을 붙이기 전에 검색 품질을 독립적으로 읽는 법부터 정리하겠습니다.

## 이 글에서 다룰 문제

- Precision@k, Recall@k, MRR는 각각 무엇을 측정하며 어떤 질문에 답할까요?
- 왜 LLM 평가를 붙이기 전에 검색 품질을 먼저 분리해서 봐야 할까요?
- 평균 점수만 보면 왜 위험할까요?
- k 값은 어떻게 정해야 하며, k가 바뀌면 세 지표는 어떻게 달라질까요?
- 세 지표를 끝까지 계산하는 최소 Python 예제는 어떤 모습일까요?

![이 글에서 답할 질문](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*

> 검색 지표의 핵심은 정답 집합과 검색 결과 목록을 분리해서 보는 것입니다. 같은 데이터를 놓고도 Precision@k, Recall@k, MRR는 서로 다른 실패를 드러냅니다.

## 왜 이 주제가 중요한가

RAG 시스템이 틀린 답을 낼 때 원인은 대개 두 층 중 하나입니다. **검색기가 틀린 문서를 가져왔거나, LLM이 맞는 문서를 보고도 잘못 답했거나** 둘 중 하나입니다. 이 두 층을 섞어서 보면 디버깅이 막막해집니다. 답이 이상하면 모델부터 바꾸고, 그래도 이상하면 프롬프트를 손대고, 그래도 원인을 설명하지 못하는 식의 악순환이 반복됩니다.

검색 지표는 이 문제를 단순하게 만듭니다. 정답 문서 ID 집합과 검색 결과 순위 목록만 있으면 계산할 수 있기 때문입니다. LLM 호출도, 추가 토큰 비용도 필요 없습니다. 그래서 검색 실험은 빠르게 반복할 수 있고, 생성 단계로 넘어가기 전에 어디가 약한지 먼저 가늠할 수 있습니다.

이 글에서는 가장 기본이 되는 세 지표를 다룹니다. Precision@k, Recall@k, MRR는 모두 같은 데이터를 보지만 서로 다른 질문에 답합니다. 이 차이를 분명히 이해해야 이후 글에서 검색기 비교, 임베딩 비교, 종단 간 평가를 제대로 읽을 수 있습니다.

## 기본 멘탈 모델

검색 지표는 두 대상을 비교합니다.

1. **정답 집합(Gold set)** — 특정 질문에 대해 관련 있다고 라벨링된 문서 ID 집합입니다. 사람이 만들거나 공개 데이터셋에서 가져옵니다.
2. **검색 결과 목록(Retrieved list)** — 검색기가 반환한 문서 ID 목록입니다. **순서가 중요합니다.**

같은 두 대상을 놓고도 지표마다 묻는 질문이 다릅니다.

- **Precision@k**: "내가 반환한 상위 k개 중 실제 정답은 몇 개인가?"
- **Recall@k**: "전체 정답 중 상위 k개 안에 들어온 것은 몇 개인가?"
- **MRR**: "첫 번째 정답 문서는 몇 번째 순위에 나타나는가?"

중요한 점은 이 값들이 모두 **질문 하나마다 먼저 계산된다**는 사실입니다. 시스템 점수는 그다음에 여러 질문의 평균으로 계산합니다. 평균만 먼저 보면 개별 실패 패턴을 놓치기 쉽습니다.

## 핵심 개념

### Precision@k와 Recall@k는 서로 다른 실패를 보여 줍니다

| Query | Gold set | Retrieved (top-3) | Precision@3 | Recall@3 |
| --- | --- | --- | --- | --- |
| Q1 | {A, B, C} | [A, X, B] | 2/3 = 0.67 | 2/3 = 0.67 |
| Q2 | {A} | [A, X, Y] | 1/3 = 0.33 | 1/1 = 1.00 |
| Q3 | {A, B, C, D, E} | [A, B, C] | 3/3 = 1.00 | 3/5 = 0.60 |

Q2는 **Precision은 낮지만 Recall은 완벽**합니다. 정답이 하나뿐인데 상위 3개를 모두 채워야 하므로, 남는 칸에 잡음이 들어갑니다. 반대로 Q3는 **Precision은 완벽하지만 Recall은 낮습니다.** 상위 3개는 모두 맞았지만, 실제로는 정답 5개 중 2개를 놓쳤기 때문입니다.

이 차이는 실무에서도 중요합니다. Precision이 낮으면 상위 슬롯에 잡음이 많다는 뜻이고, Recall이 낮으면 정답 문서를 아예 빠뜨리고 있다는 뜻입니다. 둘은 서로 다른 개선 전략으로 이어집니다.

![상위 k 결과와 정답 집합의 교집합 계산 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-02-top-k-overlap-and-metric-calculation-flo.ko.png)

*상위 k 결과와 정답 집합의 교집합 계산 흐름*

### MRR은 첫 번째 정답의 순위만 봅니다

MRR(Mean Reciprocal Rank)은 첫 번째 관련 문서가 어디에 놓였는지만 봅니다. 1위면 1.0, 2위면 0.5, 3위면 0.33입니다. 첫 번째 정답 뒤에 다른 정답이 더 있더라도 MRR 계산에는 반영되지 않습니다.

이 지표가 중요한 이유는 사용자 경험과 직접 연결되기 때문입니다. 사용자는 결과 목록 어딘가에 정답이 있다는 사실보다, **정답이 얼마나 빨리 눈앞에 나타나는지**에 더 민감합니다. 특히 RAG에서는 상위 몇 개 문서만 컨텍스트로 들어가므로, 첫 관련 문서가 뒤로 밀리면 생성 품질도 흔들리기 쉽습니다.

### k는 실제 운영 조건과 맞아야 합니다

`k=3`, `k=5`, `k=10`은 임의 숫자가 아닙니다. RAG 시스템이 실제로 LLM에 몇 개 청크를 넣는지와 연결됩니다. 만약 운영 환경에서 5개 청크를 프롬프트에 넣는다면, 가장 먼저 봐야 할 값은 `Recall@5`입니다.

운영에서는 5개만 보는데 벤치마크에서 10개를 측정하면 점수가 부풀려질 수 있습니다. 반대로 운영에서 3개를 쓰는데 1개만 측정하면 실제 실패를 과장할 수 있습니다. **지표의 k는 시스템의 실제 k와 맞아야 합니다.**

## 검색 지표를 도입하기 전과 후

### 이전: LLM 출력만 보고 판단할 때

```python
result = rag_pipeline.query("What is RAG?")
print(result)  # "RAG stands for retrieval-augmented generation..."
# → "Looks fine, I guess." End of analysis.
```

이 상태에서는 검색이 틀렸는지, 검색은 맞았는데 LLM이 헛소리를 했는지 구분할 수 없습니다.

### 이후: 검색을 먼저 계량할 때

```python
case = QueryCase(
    question="What is RAG?",
    retrieved_ids=retriever.search("What is RAG?", k=5),
    relevant_ids={"doc-rag-01", "doc-rag-02"},
)
metrics = evaluate_case(case, k=5)
print(metrics)  # {"precision@5": 0.4, "recall@5": 1.0, "mrr": 0.5}
```

이제는 해석이 가능합니다. 정답 문서는 모두 찾았고(Recall=1.0), 첫 정답은 2위에 있으며(MRR=0.5), 상위 슬롯의 60%는 잡음입니다(Precision=0.4). 다음 실험 가설도 분명해집니다. 예를 들어 재순위화기(reranker)를 붙여 상위 순서를 더 개선할 수 있습니다.

## 단계별로 직접 계산해 보기

### 1단계 — 평가 골격 만들기

```python
from dataclasses import dataclass

@dataclass
class QueryCase:
    question: str
    retrieved_ids: list[str]   # ordered
    relevant_ids: set[str]     # unordered

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

def evaluate_case(case: QueryCase, k: int) -> dict[str, float]:
    return {
        f"precision@{k}": round(precision_at_k(case, k), 2),
        f"recall@{k}": round(recall_at_k(case, k), 2),
        "mrr": round(reciprocal_rank(case), 2),
    }
```

이 코드는 세 지표가 실제로 무엇을 세는지 그대로 보여 줍니다. Precision과 Recall은 모두 상위 k개에서 관련 문서 개수를 세지만, 분모가 다릅니다. MRR은 첫 관련 문서를 발견하는 순간 계산을 끝냅니다.

### 2단계 — 여러 질문에 적용하기

```python
cases = [
    QueryCase("Q1", ["A", "X", "B"], {"A", "B", "C"}),
    QueryCase("Q2", ["A", "X", "Y"], {"A"}),
    QueryCase("Q3", ["A", "B", "C"], {"A", "B", "C", "D", "E"}),
]

for case in cases:
    print(f"{case.question}: P@3={precision_at_k(case, 3):.2f}, "
          f"R@3={recall_at_k(case, 3):.2f}, MRR={reciprocal_rank(case):.2f}")

import statistics
avg_p = statistics.mean(precision_at_k(c, 3) for c in cases)
avg_r = statistics.mean(recall_at_k(c, 3) for c in cases)
avg_mrr = statistics.mean(reciprocal_rank(c) for c in cases)
print(f"AVG: P@3={avg_p:.2f}, R@3={avg_r:.2f}, MRR={avg_mrr:.2f}")
```

여기서부터 중요한 습관이 생깁니다. 평균을 출력하되, 질문별 결과를 항상 함께 남기는 것입니다. 평균은 요약용이고, 질문별 점수는 원인 분석용입니다.

### 3단계 — 직접 실행하기

```bash
cd en/01-evaluation-metrics
python3 main.py
```

```text
Q1: P@3=0.67, R@3=0.67, MRR=1.00
Q2: P@3=0.33, R@3=1.00, MRR=1.00
Q3: P@3=1.00, R@3=0.60, MRR=1.00
AVG: P@3=0.67, R@3=0.76, MRR=1.00
```

이 출력은 평균만으로는 잘 보이지 않는 차이를 바로 드러냅니다. Q2는 **정답은 찾았지만 잡음이 많고**, Q3는 **상위 슬롯은 깨끗하지만 전체 정답을 다 가져오지 못합니다.** 둘 다 평균 P@3만 보면 비슷해 보일 수 있지만, 실제로는 개선 방향이 전혀 다릅니다.

### 4단계 — 질문별 리포트를 남기기

실험이 조금만 커지면 `print()` 한 줄로는 해석이 막힙니다. 질문별 점수를 구조화해 남겨 두어야 어느 쿼리에서 회귀가 났는지 바로 찾을 수 있습니다.

```python
report_rows = []
for case in cases:
    metrics = evaluate_case(case, k=3)
    report_rows.append({
        "question": case.question,
        "retrieved_ids": case.retrieved_ids,
        "relevant_ids": sorted(case.relevant_ids),
        **metrics,
    })

for row in report_rows:
    print(row)
```

```text
{'question': 'Q1', 'retrieved_ids': ['A', 'X', 'B'], 'relevant_ids': ['A', 'B', 'C'], 'precision@3': 0.67, 'recall@3': 0.67, 'mrr': 1.0}
{'question': 'Q2', 'retrieved_ids': ['A', 'X', 'Y'], 'relevant_ids': ['A'], 'precision@3': 0.33, 'recall@3': 1.0, 'mrr': 1.0}
{'question': 'Q3', 'retrieved_ids': ['A', 'B', 'C'], 'relevant_ids': ['A', 'B', 'C', 'D', 'E'], 'precision@3': 1.0, 'recall@3': 0.6, 'mrr': 1.0}
```

이 정도 정보만 있어도 다음 질문이 자연스럽게 나옵니다. Q2는 reranker를 붙일 문제인지, Q3는 청크 전략이나 임베딩을 바꿔야 하는 문제인지 구분할 수 있기 때문입니다.

### 5단계 — 점수 조합으로 실패를 분류하기

| 패턴 | 해석 | 먼저 의심할 것 |
| --- | --- | --- |
| Precision 낮음, Recall 높음 | 정답은 가져왔지만 잡음이 많음 | reranker, top-k 축소, 필터링 |
| Precision 높음, Recall 낮음 | 상위 결과는 깨끗하지만 정답 일부를 놓침 | 청크 크기, 임베딩, 쿼리 확장 |
| MRR 낮음 | 첫 정답이 너무 뒤에 있음 | 순위화 품질, 하이브리드 검색 |
| Recall@k = 0 | 상위 k 안에 정답이 전혀 없음 | 검색 파이프라인 자체 |

실무에서는 이 표가 의외로 유용합니다. 점수를 본 직후 "다음에 무엇을 바꿔야 하는가"를 빠르게 연결해 주기 때문입니다.

![Precision@k와 Recall@k가 갈리는 판단 축](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-03-precision-k-versus-recall-k-decision-axe.ko.png)

*Precision@k와 Recall@k가 갈리는 판단 축*

## 자주 하는 실수

- **평균만 보고 끝내기** — 평균 P@3가 0.6이어도 어떤 질문은 0.0이고 어떤 질문은 1.0일 수 있습니다. 평균만으로는 망가진 질문을 찾을 수 없습니다.
- **Precision 또는 Recall 하나만 보기** — 한쪽만 보면 "너무 많이 가져오는지"와 "정답을 빠뜨리는지"를 구분할 수 없습니다.
- **MRR을 전체 검색 품질로 오해하기** — MRR은 첫 정답 위치만 봅니다. 뒤에 있는 다른 정답은 반영하지 않습니다.
- **운영과 다른 k 사용하기** — 실제로는 5개 청크만 넣는데 `k=10`으로 측정하면 현업 체감보다 좋은 점수가 나올 수 있습니다.
- **정답 집합을 지나치게 좁게 정의하기** — 의미상 같은 문서를 찾았는데도 "이 정확한 문서만 정답"으로 라벨링해 두면 검색기를 과도하게 벌주게 됩니다.

![첫 관련 문서 위치가 MRR을 바꾸는 순위 차이](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-04-rank-position-changes-the-mrr-signal.ko.png)

*첫 관련 문서 위치가 MRR을 바꾸는 순위 차이*

## 실무에서는 이렇게 씁니다

실무에서 검색 평가를 시작할 때는 완벽한 데이터셋이 먼저 필요하지 않습니다. 보통 50~100개 질문만 있어도 출발할 수 있습니다. 도메인 전문가에게 "이 질문에 답하려면 어떤 문서가 필요합니까?"를 묻고 관련 문서 ID를 정리하면 됩니다.

그다음에는 여러 k 값을 함께 봅니다. Recall@1, Recall@3, Recall@5, Recall@10을 같이 보면 검색기가 상위 순위에서 얼마나 빨리 정답을 끌어올리는지 보입니다. 특히 Recall@10이 0인 질문은 매우 중요합니다. 상위 10개 안에도 정답이 없다면, 이 경우는 재순위화 문제가 아니라 검색 자체가 틀린 경우이기 때문입니다.

이런 평가는 가능하면 CI에 붙이는 편이 좋습니다. 임베딩 모델, 청크 크기, 인덱스 설정을 바꿀 때마다 같은 질문 세트로 자동 측정하면 회귀를 빨리 발견할 수 있습니다. 나중에는 nDCG 같은 더 정교한 지표도 고려할 수 있지만, 그 전에 Precision@k, Recall@k, MRR를 정확히 읽는 습관을 먼저 갖추는 편이 훨씬 중요합니다.

또 한 가지 권장할 점은 **평가 결과를 JSON으로 남기는 것**입니다. Markdown 표는 읽기 좋지만, CI 회귀 비교에는 구조화된 산출물이 훨씬 유리합니다. 예를 들어 질문별 점수와 평균 점수를 한 JSON 파일에 저장해 두면, 다음 실행과 diff를 만들어 PR에 바로 붙일 수 있습니다.

## 체크리스트

- [ ] 모든 질문에 대해 `relevant_ids`를 정의했는가?
- [ ] 평가에 쓰는 k가 실제 운영 환경의 컨텍스트 창과 맞는가?
- [ ] Precision@k, Recall@k, MRR를 함께 보고 있는가?
- [ ] 평균 점수와 질문별 점수를 함께 출력하는가?
- [ ] `Recall@k = 0`인 질문을 별도로 분석하는가?
- [ ] 벤치마크를 CI에 연결해 회귀를 잡고 있는가?

## 연습 문제

1. 정답 집합이 `{A, B, C}`이고 검색 결과가 `[X, A, Y, B, C]`일 때 Precision@3, Recall@3, MRR를 계산해 보세요.
2. 두 검색기 A와 B가 평균 Recall@5는 같지만 평균 MRR이 다르다면, 실제 사용자 경험에는 어느 쪽이 더 유리할까요?
3. RAG 시스템이 정확히 3개 청크만 LLM에 전달한다면 어떤 지표를 가장 먼저 봐야 할까요?

![질문별 결과와 평균 결과를 함께 읽는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/01/01-05-per-query-and-average-report-reading-flo.ko.png)

*질문별 결과와 평균 결과를 함께 읽는 흐름*

## 정리와 다음 글

이 글의 핵심은 네 가지입니다.

- RAG 평가는 검색과 생성을 분리하는 데서 시작합니다.
- Precision@k, Recall@k, MRR는 같은 데이터에서 서로 다른 질문에 답합니다.
- 평균 점수는 질문별 점수와 함께 읽어야 의미가 있습니다.
- 벤치마크의 k는 실제 운영 환경과 맞아야 합니다.

다음 글에서는 이 손계산 감각을 실제 검색기로 옮깁니다. 질문 집합, 정답 문서, 검색 결과, 지표를 한 루프에 묶어 **검색 성능을 계량하는 벤치마크 골격**을 만들겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **RAG 평가 지표 이해 (현재 글)**
- 검색 성능 측정 (예정)
- 임베딩 모델 비교 (예정)
- VectorDB 선택 기준 (예정)
- 종단 간 RAG 파이프라인 평가 (예정)
- RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Stanford IR Book — Evaluation of ranked retrieval results](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)
- [PyTerrier documentation — Evaluation and experiment analysis](https://pyterrier.readthedocs.io/en/latest/experiments.html)
- [ranx documentation — Metrics reference](https://amenra.github.io/ranx/metrics/)
- [BEIR: A heterogeneous benchmark for zero-shot evaluation of IR models](https://arxiv.org/abs/2104.08663)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)

Tags: RAG, VectorDB, Benchmarking, LLM
