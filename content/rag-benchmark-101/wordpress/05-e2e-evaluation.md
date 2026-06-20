---
title: "바이브코딩을 위한 RAG 벤치마크 (5/6): 종단 간 RAG 파이프라인 평가"
series: rag-benchmark-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG벤치마크
- RAGAS
- Faithfulness
- AI코딩
seo_description: "바이브코딩을 위한 RAG 벤치마크 5편: 종단 간 RAG 파이프라인 평가. RAGAS로 faithfulness와 answer relevancy를 측정해 검색 품질과 생성 품질을 분리합니다."
---

# 바이브코딩을 위한 RAG 벤치마크 (5/6): 종단 간 RAG 파이프라인 평가

이 글은 바이브코딩을 위한 RAG 벤치마크 시리즈의 5번째 글입니다.

검색 지표가 좋은데도 최종 답변이 나쁜 경우가 있습니다. 검색기가 맞는 문서를 가져왔지만 LLM이 컨텍스트를 무시하고 엉뚱한 답을 냈거나, 검색은 잘못됐는데 LLM이 기존 학습 지식으로 그럴듯한 답을 만들어 낸 경우입니다. 이 두 실패는 검색 지표만으로는 구분이 되지 않습니다. 종단 간 평가가 필요한 이유는 바로 여기에 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 RAG 평가 코드를 요청할 때 question, contexts, answer를 하나의 데이터셋으로 묶고 faithfulness와 answer_relevancy를 함께 측정하도록 명시하지 않으면, 검색 지표만 재는 불완전한 평가 코드가 생성되기 때문입니다.

> 종단 간 평가는 "답이 맞아 보이는가"를 묻는 인상 비평이 아닙니다. 답변이 컨텍스트에 근거하고 실제 질문에 답하는지를 구조화된 점수로 읽는 과정입니다.

---

## 이 글에서 다룰 문제

- 검색 지표가 좋아도 최종 답변이 나쁘면 어느 단계를 다시 봐야 할까요?
- RAGAS의 faithfulness와 answer_relevancy는 각각 어떤 실패를 드러낼까요?
- 검색 실패와 생성 실패를 한 리포트에서 어떻게 분리해 읽을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

종단 간 평가를 이해하면 AI에게 "question, contexts, answer 데이터셋으로 RAGAS faithfulness와 answer_relevancy를 측정하는 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "RAG 시스템 평가 코드 작성해줘"
→ 검색 지표만 재는 코드 생성
→ LLM 답변 품질 측정 없음
→ 환각 감지 불가
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "question, contexts(List[str]), answer를 컬럼으로 갖는
    HuggingFace Dataset을 만들고
    RAGAS Faithfulness와 AnswerRelevancy로 평가해줘.
    평가 LLM은 temperature=0, max_workers=1로 설정해줘"
→ 검색과 생성 품질 동시 측정
→ faithfulness로 환각 수치화
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `contexts`를 문자열 하나로 넘기기 | RAGAS는 `List[str]` 기대, 오류 발생 | contexts 컬럼은 반드시 List[str]로 구성 |
| 생성과 평가에 같은 LLM 사용 | 자기 답을 자기가 채점해 편향 발생 | 생성 모델과 평가 모델 분리 |
| `temperature > 0`으로 평가 | 같은 데이터셋 두 번 평가 시 점수 흔들림 | 평가 LLM은 `temperature=0` 고정 |
| `max_workers` 크게 설정 | 외부 API rate limit으로 평가 실패 | 처음에는 `max_workers=1`로 보수적 시작 |
| RAGAS 버전 차이 무시 | 0.1.x와 0.2.x는 API가 다름 | 버전과 코드를 함께 고정 |

## AI 협업 팁

종단 간 RAG 평가 관련 효과적인 AI 프롬프트 패턴:

1. **데이터셋 구성 요청**: "question, contexts(List[str]), answer 컬럼을 가진 HuggingFace Dataset을 생성하는 코드 작성해줘"
2. **RAGAS 평가 요청**: "Faithfulness와 AnswerRelevancy로 평가하고 결과를 DataFrame으로 CSV에 저장하는 코드 작성해줘"
3. **실패 분류 요청**: "faithfulness가 낮고 answer_relevancy가 높은 샘플을 별도로 출력하는 필터 코드 작성해줘"

예시 프롬프트:
> "질문 20개로 RAG 파이프라인을 실행해 (question, contexts, answer) 데이터셋을 만들고 RAGAS Faithfulness와 AnswerRelevancy로 평가해줘. 평가 LLM은 ChatGroq temperature=0, max_workers=1. 결과를 ragas_report.csv로 저장하고 최악 사례 3개를 출력해줘."

## 운영 체크리스트

- [ ] `contexts` 컬럼이 `List[str]`로 구성됐는가?
- [ ] 평가 LLM을 생성 LLM과 분리했는가?
- [ ] `temperature=0`이고 `max_workers`를 보수적으로 잡았는가?
- [ ] faithfulness와 answer_relevancy를 검색 지표와 함께 보고 있는가?
- [ ] 샘플별 점수를 질문, 컨텍스트, 답변과 함께 저장했는가?

## 처음 질문으로 돌아가기

종단 간 RAG 평가를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 검색과 생성 품질을 함께 측정하도록 명시한 사람과 그렇지 않은 사람이 AI에게 받는 평가 코드의 완성도는 크게 다릅니다.

## 정리

종단 간 RAG 파이프라인 평가는 바이브코딩을 위한 RAG 벤치마크에서 검색과 생성을 하나의 흐름으로 묶는 핵심 단계입니다. faithfulness가 낮고 answer_relevancy가 높은 경우가 가장 위험하다는 것을 이해했습니다. 다음 글에서는 이 모든 평가를 하나의 재현 가능한 파이프라인으로 완성합니다.

## 참고 자료

- [RAGAS documentation](https://docs.ragas.io/)
- [RAGAS GitHub repository](https://github.com/explodinggradients/ragas)
- [HuggingFace Datasets](https://huggingface.co/docs/datasets)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-benchmark-101/ko/05-e2e-evaluation)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 RAG 벤치마크 (1/6): RAG 평가 지표 이해
- 바이브코딩을 위한 RAG 벤치마크 (2/6): 검색 성능 측정
- 바이브코딩을 위한 RAG 벤치마크 (3/6): 임베딩 모델 비교
- 바이브코딩을 위한 RAG 벤치마크 (4/6): VectorDB 선택 기준
- **바이브코딩을 위한 RAG 벤치마크 (5/6): 종단 간 RAG 파이프라인 평가 (현재 글)**
- 바이브코딩을 위한 RAG 벤치마크 (6/6): RAG 벤치마크 완성
<!-- toc:end -->

Tags: 바이브코딩, RAG벤치마크, RAGAS, AI코딩
