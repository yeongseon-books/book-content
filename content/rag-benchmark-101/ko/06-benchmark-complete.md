---
title: 'RAG 벤치마크 완성'
series: rag-benchmark-101
episode: 6
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

# RAG 벤치마크 완성

## 이 글에서 답할 질문
- 데이터셋 → 검색 → 생성 → 평가를 하나의 실행 파일로 어떻게 묶을까요?
- retrieval 지표와 RAGAS 점수를 한 리포트로 합칠 때 어떤 구분이 필요할까요?
- 최종 파이프라인 벤치마크에서 가장 먼저 고정해야 할 실험 조건은 무엇일까요?

> 완성된 RAG 벤치마크는 하나의 점수가 아니라, retrieval과 generation을 나눠서 같은 실험 조건 아래 반복 실행하는 재현 가능한 파이프라인입니다.

마지막 글에서는 지금까지의 조각을 하나로 연결합니다. 먼저 FAISS retriever로 관련 문서를 찾고, 그 컨텍스트를 Groq LLM에 넣어 답변을 만들고, 마지막으로 retrieval 지표와 RAGAS 점수를 함께 집계합니다. 이렇게 해야 “검색이 문제인지, 답변 생성이 문제인지”를 같은 실행 로그 안에서 볼 수 있습니다.

![이 글에서 답할 질문](../../../assets/rag-benchmark-101/06/06-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

### 검색과 생성과 평가가 한 실행으로 이어지는 파이프라인

![검색과 생성과 평가가 한 실행으로 이어지는 파이프라인](../../../assets/rag-benchmark-101/06/06-01-end-to-end-benchmark-pipeline-in-one-run.ko.png)
실행 코드는 `rag-benchmark-101/ko/06-benchmark-complete/main.py`에 있습니다. 05편과 06편은 `GROQ_API_KEY`가 필요합니다.

```bash
cd /root/Github/rag-benchmark-101/ko/06-benchmark-complete
export GROQ_API_KEY=... && python3 main.py
```

```python
for case in TEST_CASES:
    docs = retriever.invoke(case['question'])
    answer = chain.invoke({'question': case['question'], 'context': context})
    rows.append({'question': case['question'], 'answer': answer, 'contexts': [doc.page_content for doc in docs]})

ragas_result = evaluate(dataset=Dataset.from_list(rows), ...)
```

## 이 코드에서 봐야 할 것

### Retrieval 리포트와 generation 리포트를 나누는 구조

![Retrieval 리포트와 generation 리포트를 나누는 구조](../../../assets/rag-benchmark-101/06/06-02-retrieval-and-generation-report-split.ko.png)
- retrieval 리포트와 generation 리포트를 별도 key로 나눠서 출력해야 병목 분석이 쉬워집니다.
- 질문별로 retrieved ids와 최종 answer를 함께 로그에 남기면 숫자 뒤의 실패 사례를 빠르게 추적할 수 있습니다.
- 전체 파이프라인 벤치마크에서는 코퍼스, 임베딩 모델, top-k, LLM 모델을 고정해야 비교가 의미 있습니다.

## 실무에서 헷갈리는 지점

### 낮은 점수를 검색 문제와 생성 문제로 가르는 분기

![낮은 점수를 검색 문제와 생성 문제로 가르는 분기](../../../assets/rag-benchmark-101/06/06-03-branching-search-failures-from-generatio.ko.png)
- 최종 faithfulness가 낮다고 해서 항상 LLM만 문제인 것은 아닙니다. 검색기가 잘못된 문서를 가져오면 생성기는 그 문서에 충실하게 틀릴 수 있습니다.
- 반대로 retrieval 지표가 좋아도 answer_relevancy가 낮으면 프롬프트나 생성 단계가 질문을 제대로 반영하지 못한 것입니다.
- 전체 점수 하나로만 정렬하면 어떤 레이어를 개선해야 하는지 감이 사라집니다. 최소한 retrieval과 generation을 분리해 유지하세요.

## 체크리스트

### 기준선 비교부터 최종 의사결정까지 이어지는 벤치마크 루프

![기준선 비교부터 최종 의사결정까지 이어지는 벤치마크 루프](../../../assets/rag-benchmark-101/06/06-04-baseline-to-decision-benchmark-loop.ko.png)
- [ ] 검색, 생성, 평가를 한 실행 파일에 묶었다.
- [ ] retrieval 지표와 generation 지표를 분리해 출력했다.
- [ ] 질문별 로그와 최종 요약 리포트를 함께 남겼다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [검색 성능 측정](./02-retrieval-benchmarking.md)
- [임베딩 모델 비교](./03-embedding-comparison.md)
- [VectorDB 선택 기준](./04-vectordb-selection.md)
- [종단 간 RAG 파이프라인 평가](./05-e2e-evaluation.md)
- **RAG 벤치마크 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [RAGAS documentation](https://docs.ragas.io/)
- [LangChain retrieval overview](https://python.langchain.com/docs/concepts/retrieval/)
- [FAISS documentation](https://faiss.ai/)

Tags: RAG, VectorDB, Benchmarking, LLM
