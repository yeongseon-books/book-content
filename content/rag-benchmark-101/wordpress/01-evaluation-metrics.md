---
title: "바이브코딩을 위한 RAG 벤치마크 (1/6): RAG 평가 지표 이해"
series: rag-benchmark-101
episode: 1
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG벤치마크
- 평가지표
- Precision
- AI코딩
seo_description: "바이브코딩을 위한 RAG 벤치마크 1편: RAG 평가 지표. Precision@k, Recall@k, MRR가 같은 결과에서 서로 다른 실패를 드러내는 방식을 이해합니다."
---

# 바이브코딩을 위한 RAG 벤치마크 (1/6): RAG 평가 지표 이해

이 글은 바이브코딩을 위한 RAG 벤치마크 시리즈의 1번째 글입니다.

RAG 시스템이 틀린 답을 낼 때 원인은 두 층 중 하나입니다. 검색기가 틀린 문서를 가져왔거나, LLM이 맞는 문서를 보고도 잘못 답했거나. 이 두 층을 섞어 보면 디버깅이 막막해집니다. 검색 지표는 이 문제를 단순하게 만듭니다. 정답 문서 ID 집합과 검색 결과 목록만 있으면 LLM 호출 없이 계산할 수 있기 때문입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 RAG 평가 코드를 요청할 때 어떤 지표가 어떤 실패를 드러내는지 모르면, 생성된 코드가 실제로 필요한 신호를 주는지 확인할 수 없기 때문입니다.

> 검색 지표의 핵심은 정답 집합과 검색 결과 목록을 분리해서 보는 것입니다. 같은 데이터를 놓고도 Precision@k, Recall@k, MRR는 서로 다른 실패를 드러냅니다.

---

## 이 글에서 다룰 문제

- Precision@k, Recall@k, MRR는 같은 결과 목록에서 각각 어떤 실패를 보여 줄까요?
- RAG 답변이 틀렸을 때 검색 문제와 생성 문제를 어떻게 분리할 수 있을까요?
- 평균 점수만 보면 왜 질문별 실패 패턴을 놓칠 수 있을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

검색 지표를 이해하면 AI에게 "Precision@k, MRR 계산, 질문별 점수 분리 출력" 같은 정확한 요청을 할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "RAG 시스템 성능 측정 코드 작성해줘"
→ 전체 정확도만 출력하는 단일 지표
→ 검색과 생성 품질이 섞인 결과
→ 질문별 실패 패턴 파악 불가
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "gold set과 retrieved list를 받아
    Precision@5, Recall@5, MRR을 계산하는 함수를 작성해줘.
    질문별 점수와 평균을 모두 출력하고
    검색 단계만 독립적으로 측정해줘"
→ 검색과 생성 품질 분리 측정
→ 질문별 실패 패턴 가시화
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 검색과 생성 품질을 함께 평가 | 어느 단계가 문제인지 알 수 없음 | 검색 지표를 생성 이전에 독립 측정 |
| 평균만 보고 결론 | 특정 질문 유형에서 0점인 케이스를 놓침 | 질문별 점수 분포도 함께 확인 |
| top-k를 고정하지 않음 | k가 달라지면 지표가 달라져 비교 불가 | k=5 또는 k=10으로 고정 후 비교 |
| gold set을 직접 만들지 않음 | 평가 기준이 주관적 | 사람이 검수한 정답 문서 ID 집합 필요 |
| MRR과 MAP를 같다고 생각 | 첫 번째 정답과 전체 정답 위치가 다를 때 차이 | MRR은 첫 정답, MAP는 전체 정답 위치 |

## AI 협업 팁

RAG 평가 지표 관련 효과적인 AI 프롬프트 패턴:

1. **지표 구현 요청**: "gold_ids와 retrieved_ids를 받아 Precision@k, Recall@k, MRR을 계산하는 함수 작성해줘"
2. **질문별 분석 요청**: "질문별 점수를 DataFrame으로 출력하고 하위 20% 질문을 별도로 표시해줘"
3. **검색-생성 분리 요청**: "검색 지표는 LLM 없이 벡터 검색 결과만으로 계산하는 코드 작성해줘"

예시 프롬프트:
> "queries와 gold_dict를 받아 Precision@5, Recall@5, MRR을 질문별로 계산하고 평균과 함께 출력하는 evaluate_retrieval 함수를 작성해줘."

## 운영 체크리스트

- [ ] Precision@k, Recall@k, MRR이 각각 어떤 실패를 드러내는지 설명할 수 있는가?
- [ ] 검색 지표를 LLM 호출 없이 독립적으로 계산할 수 있는가?
- [ ] 질문별 점수와 평균 점수를 함께 보는 이유를 이해했는가?
- [ ] gold set의 의미와 만드는 방법을 알고 있는가?
- [ ] 다음 글에서 이 지표를 벤치마크 루프로 자동화하는 방법을 연결할 수 있는가?

## 처음 질문으로 돌아가기

RAG 평가 지표를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 어떤 지표가 어떤 실패를 드러내는지 아는 사람과 그렇지 않은 사람이 AI에게 받는 평가 코드의 유용성은 크게 다릅니다.

## 정리

RAG 평가 지표는 바이브코딩을 위한 RAG 벤치마크 시리즈의 출발점입니다. Precision@k, Recall@k, MRR가 같은 결과를 보고 다른 실패를 드러낸다는 것을 이해했습니다. 다음 글에서는 이 지표들을 반복 가능한 벤치마크 루프로 만드는 방법을 다룹니다.

## 참고 자료

- [Evaluation metrics for information retrieval](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval))
- [BEIR benchmark](https://github.com/beir-cellar/beir)
- [RAGAS](https://github.com/explodinggradients/ragas)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-benchmark-101/ko/01-evaluation-metrics)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 RAG 벤치마크 (1/6): RAG 평가 지표 이해 (현재 글)**
- 바이브코딩을 위한 RAG 벤치마크 (2/6): 검색 성능 측정
- 바이브코딩을 위한 RAG 벤치마크 (3/6): 임베딩 모델 비교
- 바이브코딩을 위한 RAG 벤치마크 (4/6): VectorDB 선택 기준
- 바이브코딩을 위한 RAG 벤치마크 (5/6): 종단 간 RAG 파이프라인 평가
- 바이브코딩을 위한 RAG 벤치마크 (6/6): RAG 벤치마크 완성
<!-- toc:end -->

Tags: 바이브코딩, RAG벤치마크, 평가지표, AI코딩
