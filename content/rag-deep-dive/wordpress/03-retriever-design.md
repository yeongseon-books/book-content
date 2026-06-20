---
title: "바이브코딩을 위한 RAG 심화 (3/6): Retriever 설계"
series: rag-deep-dive
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG심화
- Retriever
- MMR
- AI코딩
seo_description: "바이브코딩을 위한 RAG 심화 3편: Retriever 설계. VectorStoreRetriever와 MMR이 관련성과 다양성을 어떻게 균형잡는지 이해합니다."
---

# 바이브코딩을 위한 RAG 심화 (3/6): Retriever 설계

이 글은 바이브코딩을 위한 RAG 심화 시리즈의 3번째 글입니다.

최근접 이웃을 가져오는 것과 좋은 컨텍스트를 가져오는 것은 다릅니다. similarity 검색은 관련성 높은 문서를 가져오지만, 같은 내용을 담은 청크를 여러 개 가져올 수 있습니다. 이 경우 컨텍스트 창이 중복 내용으로 채워져 LLM이 다양한 근거를 보지 못하게 됩니다. MMR(Maximum Marginal Relevance)은 관련성과 다양성을 동시에 고려해 이 문제를 해결합니다. retriever는 최근접 이웃 몇 개를 가져오는 도구가 아니라, 후보 근거를 최종 컨텍스트로 바꾸는 정책 계층입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 retriever 코드를 요청할 때 검색 유형(similarity vs mmr), fetch_k, lambda_mult를 명시하지 않으면, 중복 문서를 LLM에 전달하는 기본 설정으로 동작하는 코드가 생성되기 때문입니다.

> Retriever는 최근접 이웃 몇 개를 가져오는 도구가 아닙니다. 후보 근거를 최종 컨텍스트로 바꾸는 정책 계층입니다.

---

## 이 글에서 다룰 문제

- `similarity`, `similarity_score_threshold`, `mmr`는 각각 어떤 검색 실패를 줄이려는 선택일까요?
- MMR의 `fetch_k`와 `lambda_mult`는 결과를 어떻게 바꿀까요?
- 검색 결과가 이상할 때 어떻게 디버깅할 수 있을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Retriever 설계를 이해하면 AI에게 "MMR로 관련성과 다양성을 균형잡고 score_threshold로 무관한 문서를 필터링하는 retriever 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "FAISS에서 관련 문서를 가져오는 retriever 코드 작성해줘"
→ similarity 기본 설정으로 중복 문서 반환
→ score threshold 없어 무관한 문서 포함
→ 검색 파라미터 설명 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "vectorstore.as_retriever를 사용해 MMR 검색으로
    k=3, fetch_k=10, lambda_mult=0.6으로 설정해줘.
    관련성과 다양성 균형을 위한 파라미터 설명도 추가해줘.
    similarity_score_threshold=0.5로 낮은 유사도 문서를 필터링해줘"
→ 중복 제거된 다양한 컨텍스트
→ 무관한 문서 자동 필터링
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| similarity 기본값만 사용 | 중복 내용 청크가 LLM 컨텍스트 점유 | MMR로 전환해 다양성 확보 |
| fetch_k를 k와 같게 설정 | MMR 재순위를 위한 후보 풀이 너무 작음 | fetch_k를 k의 3~5배로 설정 |
| score_threshold 미설정 | 의미 없는 문서도 컨텍스트에 포함 | 최소 유사도 기준선 명시 |
| lambda_mult 의미 파악 없이 조정 | 관련성/다양성 트레이드오프를 모름 | 0에 가까울수록 다양성, 1에 가까울수록 관련성 |
| retriever 결과를 검사 안 함 | 잘못된 설정이 조용히 통과 | 알려진 질문으로 smoke test 실행 |

## AI 협업 팁

Retriever 설계 관련 효과적인 AI 프롬프트 패턴:

1. **MMR 설정 요청**: "vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': 3, 'fetch_k': 10, 'lambda_mult': 0.6})로 설정하는 코드 작성해줘"
2. **threshold 필터 요청**: "similarity_score_threshold=0.5로 낮은 유사도 문서를 자동 필터링하는 retriever 설정 코드 작성해줘"
3. **비교 실험 요청**: "같은 쿼리로 similarity와 mmr retriever를 모두 실행하고 반환된 문서를 나란히 비교하는 코드 작성해줘"

예시 프롬프트:
> "FAISS vectorstore에서 MMR retriever를 만들어줘. k=3, fetch_k=10, lambda_mult=0.6. 같은 쿼리로 similarity retriever와 MMR retriever 결과를 비교하고 중복 문서 수를 출력해줘."

## 운영 체크리스트

- [ ] 검색 유형(similarity vs mmr)을 도메인 특성에 맞게 선택했는가?
- [ ] MMR 사용 시 fetch_k가 k의 충분한 배수로 설정됐는가?
- [ ] score_threshold로 무관한 문서를 필터링하고 있는가?
- [ ] 알려진 질문으로 retriever 결과를 검증했는가?
- [ ] 다음 글에서 이 retriever를 프롬프트 템플릿과 연결할 준비가 됐는가?

## 처음 질문으로 돌아가기

Retriever 설계를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 검색 정책을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 retriever 코드의 품질은 크게 다릅니다.

## 정리

Retriever 설계는 바이브코딩을 위한 RAG 심화에서 검색 결과의 관련성과 다양성을 제어하는 핵심 계층입니다. similarity와 MMR의 차이, fetch_k와 lambda_mult의 역할을 이해했습니다. 다음 글에서는 이 retriever가 가져온 컨텍스트를 LLM 입력으로 변환하는 프롬프트 설계를 다룹니다.

## 참고 자료

- [LangChain Retriever documentation](https://python.langchain.com/docs/concepts/retrievers/)
- [Maximum Marginal Relevance](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)
- [VectorStore as_retriever API](https://python.langchain.com/api_reference/core/vectorstores/langchain_core.vectorstores.base.VectorStore.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-deep-dive/ko/03-retriever-design)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 RAG 심화 (1/6): 문서 로딩과 청크 전략
- 바이브코딩을 위한 RAG 심화 (2/6): 임베딩과 벡터 인덱스
- **바이브코딩을 위한 RAG 심화 (3/6): Retriever 설계 (현재 글)**
- 바이브코딩을 위한 RAG 심화 (4/6): 프롬프트 구성과 컨텍스트 주입
- 바이브코딩을 위한 RAG 심화 (5/6): RAG Chain 조립
- 바이브코딩을 위한 RAG 심화 (6/6): 평가와 품질 게이트
<!-- toc:end -->

Tags: 바이브코딩, RAG심화, Retriever, AI코딩
