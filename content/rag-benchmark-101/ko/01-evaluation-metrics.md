---
title: 'RAG 평가 지표 이해'
series: rag-benchmark-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- VectorDB
- Benchmarking
- LLM
last_reviewed: '2026-05-01'
---

# RAG 평가 지표 이해

## 이 글에서 답할 질문
- Precision@k, Recall@k, MRR은 각각 무엇을 놓치지 않고 보여줄까요?
- 한 쿼리 점수와 여러 쿼리 평균 점수를 어떻게 나눠서 읽어야 할까요?
- 검색 지표를 직접 계산해 보면 RAG 디버깅이 왜 쉬워질까요?

> RAG 평가는 점수표를 외우는 일이 아니라, 어떤 쿼리에서 검색기가 왜 틀렸는지 순위 기준으로 해부하는 작업입니다.

첫 글에서는 검색 품질을 가장 작은 단위부터 분해합니다. LLM 평가로 바로 넘어가기 전에 Precision@k, Recall@k, MRR을 손으로 계산할 수 있어야 이후 실험 결과를 해석할 수 있습니다. 이 글의 예제는 정답 문서 집합과 실제 검색 결과 목록만으로 점수를 계산합니다.

![이 글에서 답할 질문](../../../assets/rag-benchmark-101/01/01-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

### 상위 k 결과와 정답 집합의 교집합 계산 흐름

![상위 k 결과와 정답 집합의 교집합 계산 흐름](../../../assets/rag-benchmark-101/01/01-02-top-k-overlap-and-metric-calculation-flo.ko.png)
실행 코드는 `rag-benchmark-101/ko/01-evaluation-metrics/main.py`에 있습니다. 05편과 06편은 `GROQ_API_KEY`가 필요합니다.

```bash
cd /root/Github/rag-benchmark-101/ko/01-evaluation-metrics
python3 main.py
```

```python
from dataclasses import dataclass

@dataclass
class QueryCase:
    question: str
    retrieved_ids: list[str]
    relevant_ids: set[str]

for case in cases:
    metrics = evaluate_case(case, k=3)
    print(case.question, metrics.as_dict())
```

## 이 코드에서 봐야 할 것

### Precision@k와 Recall@k가 갈리는 판단 축

![Precision@k와 Recall@k가 갈리는 판단 축](../../../assets/rag-benchmark-101/01/01-03-precision-k-versus-recall-k-decision-axe.ko.png)
- `retrieved_ids[:k]`만 잘라서 상위 k개만 평가합니다.
- Precision@k와 Recall@k를 분리해 두면 “많이 가져왔지만 틀렸다”와 “적게 가져왔지만 맞았다”를 구분할 수 있습니다.
- MRR은 첫 관련 문서가 몇 번째에 들어왔는지만 보므로, 검색 결과 첫 화면 UX와 직접 연결됩니다.

## 실무에서 헷갈리는 지점

### 첫 관련 문서 위치가 MRR을 바꾸는 순위 차이

![첫 관련 문서 위치가 MRR을 바꾸는 순위 차이](../../../assets/rag-benchmark-101/01/01-04-rank-position-changes-the-mrr-signal.ko.png)
- Precision@k가 높아도 Recall@k가 낮을 수 있습니다. 상위 몇 개만 정확하게 맞히고 나머지 관련 문서를 놓친 경우입니다.
- MRR은 첫 관련 문서 이후의 품질을 반영하지 않습니다. 따라서 MRR 하나만으로는 전체 top-k 품질을 판단할 수 없습니다.
- 쿼리 수가 적을 때 평균 점수만 보면 특정 실패 케이스가 가려집니다. 반드시 쿼리별 출력도 함께 봐야 합니다.

## 체크리스트

### 쿼리별 점수와 평균 점수를 함께 읽는 리포트 구조

![쿼리별 점수와 평균 점수를 함께 읽는 리포트 구조](../../../assets/rag-benchmark-101/01/01-05-per-query-and-average-report-reading-flo.ko.png)
- [ ] 정답 문서 집합을 쿼리별로 명시했다.
- [ ] 평가할 k 값을 코드와 리포트에서 동일하게 사용했다.
- [ ] 평균 점수와 쿼리별 점수를 함께 확인했다.

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

- [Wikipedia: Mean reciprocal rank](https://en.wikipedia.org/wiki/Mean_reciprocal_rank)
- [Stanford IR book: Evaluation in information retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)

Tags: RAG, VectorDB, Benchmarking, LLM
