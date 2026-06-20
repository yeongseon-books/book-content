---
title: "바이브코딩을 위한 RAG 벤치마크 (2/6): 검색 성능 측정"
series: rag-benchmark-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG벤치마크
- 검색성능
- HitRate
- AI코딩
seo_description: "바이브코딩을 위한 RAG 벤치마크 2편: 검색 성능 측정. 질문, 정답 문서, 순위 결과, 지표 수집을 하나의 반복 가능한 루프로 만드는 방법을 이해합니다."
---

# 바이브코딩을 위한 RAG 벤치마크 (2/6): 검색 성능 측정

이 글은 바이브코딩을 위한 RAG 벤치마크 시리즈의 2번째 글입니다.

임베딩을 바꾸고, 청크 크기를 바꾸고, 코퍼스가 늘어날 때마다 검색 결과도 함께 흔들립니다. 측정 루프가 없으면 의사결정은 결국 "체감상 좋아 보인다" 수준에 머무릅니다. 검색 성능 측정의 핵심은 질문, 정답 문서, 순위 결과, 지표 수집이 반복 가능한 하나의 루프로 묶여 있다는 점입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 검색 벤치마크 코드를 요청할 때 gold set, top-k, latency 측정을 명시하지 않으면, 생성된 코드가 재현 가능한 비교를 지원하지 못하기 때문입니다.

> 검색 벤치마크의 핵심은 벡터 DB나 인덱스 자체가 아닙니다. 질문, 정답 문서, 순위 결과, 지표 수집이 반복 가능한 하나의 루프로 묶여 있다는 점이 핵심입니다.

---

## 이 글에서 다룰 문제

- 검색 성능을 감이 아니라 벤치마크 루프로 보려면 무엇을 고정해야 할까요?
- hit rate, MRR, latency는 검색기의 어떤 다른 측면을 측정할까요?
- 작은 gold set으로도 의미 있는 회귀 검사를 만들 수 있을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

벤치마크 루프를 이해하면 AI에게 "고정된 gold set으로 latency와 hit rate를 함께 측정하는 루프"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "RAG 검색 성능 측정 코드 작성해줘"
→ 단일 쿼리에 대한 일회성 측정
→ gold set 없어 객관적 비교 불가
→ latency 측정 없어 속도 트레이드오프 확인 불가
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "gold_set을 고정하고 각 쿼리에 대해
    top-5 hit rate, MRR, 검색 latency를 측정하는
    벤치마크 루프를 작성해줘.
    결과를 CSV로 저장하고 평균도 출력해줘"
→ 재현 가능한 반복 측정
→ 품질과 속도 트레이드오프 동시 확인
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| gold set 없이 "느낌"으로 평가 | 회귀가 생겨도 감지 불가 | 최소 20개 이상의 (query, gold_doc_id) 쌍 구성 |
| 단일 지표만 사용 | 다른 축의 변화를 놓침 | hit rate + MRR + latency 함께 측정 |
| top-k를 실험마다 다르게 설정 | 비교가 의미 없어짐 | 동일한 k로 모든 실험 고정 |
| latency를 별도로 측정 안 함 | 품질 개선이 속도 손해를 동반해도 모름 | time.perf_counter()로 검색 시간 기록 |
| 결과를 저장하지 않음 | 어제 실험과 비교 불가 | CSV/JSON으로 run_id와 함께 저장 |

## AI 협업 팁

검색 벤치마크 관련 효과적인 AI 프롬프트 패턴:

1. **루프 구성 요청**: "gold_set을 받아 각 쿼리별로 top-k 검색, hit rate, MRR, latency를 측정하는 benchmark_retrieval 함수 작성해줘"
2. **회귀 감지 요청**: "이전 실험 CSV와 비교해 hit rate가 5% 이상 하락하면 경고를 출력하는 코드 작성해줘"
3. **보고서 요청**: "쿼리별 점수와 하위 20% 실패 케이스를 함께 출력하는 리포트 함수 작성해줘"

예시 프롬프트:
> "gold_set(query, gold_ids 쌍 목록)과 retriever를 받아 Precision@5, MRR, 쿼리당 latency를 측정하고 결과를 CSV로 저장하는 벤치마크 루프를 작성해줘."

## 운영 체크리스트

- [ ] gold set이 최소 20개 이상의 (query, gold_doc_id) 쌍으로 구성됐는가?
- [ ] hit rate, MRR, latency를 같은 루프에서 함께 측정하는가?
- [ ] top-k가 모든 실험에서 동일하게 고정됐는가?
- [ ] 결과를 run_id와 함께 저장해 이전 실험과 비교할 수 있는가?
- [ ] 다음 글에서 임베딩 모델만 바꾸는 비교 실험에 이 루프를 재사용할 수 있는가?

## 처음 질문으로 돌아가기

검색 성능 측정을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 반복 가능한 루프를 요청하는 사람과 그렇지 않은 사람이 AI에게 받는 벤치마크 코드의 재현성은 크게 다릅니다.

## 정리

검색 성능 측정은 바이브코딩을 위한 RAG 벤치마크 시리즈의 핵심 인프라입니다. gold set, top-k 고정, latency 측정, 결과 저장이 하나의 루프로 묶여야 재현 가능한 비교가 가능합니다. 다음 글에서는 이 루프에 임베딩 모델 비교를 적용합니다.

## 참고 자료

- [BEIR benchmark](https://github.com/beir-cellar/beir)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [LangChain retriever evaluation](https://docs.langchain.com/docs/use-cases/evaluation)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-benchmark-101/ko/02-retrieval-benchmarking)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 RAG 벤치마크 (1/6): RAG 평가 지표 이해
- **바이브코딩을 위한 RAG 벤치마크 (2/6): 검색 성능 측정 (현재 글)**
- 바이브코딩을 위한 RAG 벤치마크 (3/6): 임베딩 모델 비교
- 바이브코딩을 위한 RAG 벤치마크 (4/6): VectorDB 선택 기준
- 바이브코딩을 위한 RAG 벤치마크 (5/6): 종단 간 RAG 파이프라인 평가
- 바이브코딩을 위한 RAG 벤치마크 (6/6): RAG 벤치마크 완성
<!-- toc:end -->

Tags: 바이브코딩, RAG벤치마크, 검색성능, AI코딩
