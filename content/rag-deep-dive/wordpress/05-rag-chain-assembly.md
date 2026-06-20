---
title: "바이브코딩을 위한 RAG 심화 (5/6): RAG Chain 조립"
series: rag-deep-dive
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG심화
- LCEL
- RAGChain
- AI코딩
seo_description: "바이브코딩을 위한 RAG 심화 5편: RAG Chain 조립. RetrievalQA의 한계와 LCEL 파이프라인이 RAG 흐름을 더 명확하게 표현하는 방법을 이해합니다."
---

# 바이브코딩을 위한 RAG 심화 (5/6): RAG Chain 조립

이 글은 바이브코딩을 위한 RAG 심화 시리즈의 5번째 글입니다.

`RetrievalQA`는 편리하지만 내부에서 무슨 일이 일어나는지 잘 보이지 않습니다. 검색 결과가 잘못됐을 때 어디를 수정해야 하는지, 소스 문서가 어떻게 프롬프트에 들어가는지, 파서가 왜 특정 형식을 뽑아내는지 추적하기 어렵습니다. LCEL(LangChain Expression Language)은 retriever, 프롬프트, LLM, 파서를 파이프(`|`)로 명시적으로 연결해 각 단계의 입출력을 직접 볼 수 있게 만듭니다. RAG chain은 질문에서 근거, 프롬프트, 답변으로 이어지는 실행 그래프이며, LCEL은 그 경계를 더 명확하게 드러냅니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 RAG chain 코드를 요청할 때 LCEL 구조, source_documents 보존, StrOutputParser 연결을 명시하지 않으면, 디버깅이 어려운 블랙박스 체인이 생성되기 때문입니다.

> RAG 체인은 질문에서 근거, 프롬프트, 답변으로 이어지는 실행 그래프이며, LCEL은 그 경계를 더 명시적으로 드러냅니다.

---

## 이 글에서 다룰 문제

- `RetrievalQA` 같은 고전 API와 LCEL 조립은 각각 어떤 경계를 숨기고 드러낼까요?
- retriever, prompt, llm, parser를 직접 이으면 디버깅에서 무엇이 쉬워질까요?
- 체인 조립 후 source_documents를 잃지 않으려면 어디서 결과 형태를 고정해야 할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

RAG chain 조립을 이해하면 AI에게 "LCEL로 retriever | prompt | llm | parser를 명시적으로 연결하고 source_documents를 answer와 함께 반환하는 chain 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "LangChain으로 RAG chain 코드 작성해줘"
→ RetrievalQA.from_chain_type 블랙박스 사용
→ 중간 단계 로그 없음
→ source_documents 추적 불가
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "LCEL로 RAG chain을 만들어줘.
    {'context': retriever | format_docs, 'question': RunnablePassthrough()}
    | prompt | llm | StrOutputParser() 구조로 연결해줘.
    source_documents도 함께 반환하는 버전도 만들어줘"
→ 단계별 입출력이 보이는 투명한 chain
→ 소스 문서 추적 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| RetrievalQA만 사용 | 내부 구현 변경 시 제어 불가 | LCEL로 각 단계를 명시적으로 연결 |
| source_documents 버리기 | 답변 근거 추적 불가 | RunnableParallel로 answer와 sources를 함께 반환 |
| StrOutputParser 생략 | AIMessage 객체가 반환되어 후처리 필요 | 파이프라인 끝에 StrOutputParser() 추가 |
| RunnablePassthrough 역할 오해 | question이 context 변환 중 유실 | 입력을 그대로 전달하는 passthrough를 명시 |
| chain.invoke 결과 타입 확인 안 함 | 후속 처리에서 AttributeError | invoke 결과의 타입과 키를 먼저 확인 |

## AI 협업 팁

RAG chain 조립 관련 효과적인 AI 프롬프트 패턴:

1. **LCEL chain 요청**: "retriever, format_docs, ChatPromptTemplate, ChatGroq, StrOutputParser를 LCEL 파이프로 연결하는 rag_chain 코드 작성해줘"
2. **소스 문서 보존 요청**: "RunnableParallel로 answer와 source_documents를 함께 반환하는 chain 버전 작성해줘"
3. **단계별 디버깅 요청**: "chain의 각 단계 출력을 중간에서 확인할 수 있는 디버그 래퍼 함수 작성해줘"

예시 프롬프트:
> "LCEL로 RAG chain을 작성해줘. chain = {'context': retriever | format_docs, 'question': RunnablePassthrough()} | prompt | llm | StrOutputParser(). 별도로 {'answer': rag_chain, 'sources': retriever}를 RunnableParallel로 묶어 소스 문서도 반환해줘."

## 운영 체크리스트

- [ ] retriever, prompt, llm, parser가 LCEL 파이프로 명시적으로 연결됐는가?
- [ ] source_documents를 answer와 함께 반환하는 버전이 있는가?
- [ ] 체인 출력 타입이 str인지 확인했는가?
- [ ] 각 단계를 독립적으로 테스트할 수 있는가?
- [ ] 다음 글에서 이 chain을 RAGAS로 평가하는 데이터셋을 만들 준비가 됐는가?

## 처음 질문으로 돌아가기

RAG chain 조립을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. LCEL 구조를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 RAG chain의 디버깅 편의성은 크게 다릅니다.

## 정리

RAG chain 조립은 바이브코딩을 위한 RAG 심화에서 모든 컴포넌트를 하나의 실행 흐름으로 연결하는 핵심 단계입니다. LCEL의 투명성, source_documents 보존, StrOutputParser의 역할을 이해했습니다. 다음 글에서는 이 chain의 출력을 RAGAS로 자동 평가하고 품질 게이트를 만드는 방법을 다룹니다.

## 참고 자료

- [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/concepts/lcel/)
- [RunnableParallel](https://python.langchain.com/docs/how_to/parallel/)
- [RetrievalQA vs LCEL comparison](https://python.langchain.com/docs/versions/migrating_chains/retrieval_qa/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-deep-dive/ko/05-rag-chain-assembly)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 RAG 심화 (1/6): 문서 로딩과 청크 전략
- 바이브코딩을 위한 RAG 심화 (2/6): 임베딩과 벡터 인덱스
- 바이브코딩을 위한 RAG 심화 (3/6): Retriever 설계
- 바이브코딩을 위한 RAG 심화 (4/6): 프롬프트 구성과 컨텍스트 주입
- **바이브코딩을 위한 RAG 심화 (5/6): RAG Chain 조립 (현재 글)**
- 바이브코딩을 위한 RAG 심화 (6/6): 평가와 품질 게이트
<!-- toc:end -->

Tags: 바이브코딩, RAG심화, LCEL, AI코딩
