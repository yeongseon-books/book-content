---
title: "바이브코딩을 위한 RAG 심화 (4/6): 프롬프트 구성과 컨텍스트 주입"
series: rag-deep-dive
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG심화
- PromptTemplate
- 컨텍스트주입
- AI코딩
seo_description: "바이브코딩을 위한 RAG 심화 4편: 프롬프트 구성과 컨텍스트 주입. PromptTemplate이 검색된 컨텍스트를 LLM 입력으로 변환하는 방식을 이해합니다."
---

# 바이브코딩을 위한 RAG 심화 (4/6): 프롬프트 구성과 컨텍스트 주입

이 글은 바이브코딩을 위한 RAG 심화 시리즈의 4번째 글입니다.

검색기가 올바른 문서를 가져와도 그것을 LLM에 전달하는 프롬프트 형식이 잘못되면 답변 품질이 떨어집니다. 컨텍스트가 질문보다 뒤에 오거나, 시스템 메시지와 사용자 메시지가 섞이거나, 여러 문서를 구분 없이 이어 붙이면 LLM이 어디서 답을 찾아야 하는지 혼란스러워합니다. PromptTemplate과 ChatPromptTemplate은 단순한 문자열 포맷팅 도구가 아닙니다. 구조화된 입력 계약을 검증하고 검색 결과를 LLM이 읽는 실제 형식으로 변환하는 계층입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 RAG 프롬프트 코드를 요청할 때 context와 question의 역할 분리, 시스템 메시지 위치, 문서 구분자를 명시하지 않으면, LLM이 근거와 질문을 뒤섞어 읽는 프롬프트가 생성되기 때문입니다.

> 프롬프트 계층은 구조화된 retrieval 결과가 모델이 실제로 읽는 입력 계약으로 바뀌는 곳입니다.

---

## 이 글에서 다룰 문제

- 프롬프트 템플릿은 문자열 포맷팅이 아니라 어떤 입력 계약을 검증할까요?
- 검색된 context를 메시지에 주입할 때 순서와 역할이 왜 중요할까요?
- RAG 프롬프트에서 질문과 근거를 분리하지 않으면 어떤 디버깅 문제가 생길까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

프롬프트 구성을 이해하면 AI에게 "시스템 메시지에 역할 지시, human 메시지에 context와 question을 분리해 주입하는 ChatPromptTemplate 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "RAG 프롬프트 코드 작성해줘"
→ 문서와 질문을 구분 없이 이어 붙임
→ 시스템/사용자 역할 구분 없음
→ 컨텍스트 누락 시 조용히 빈 답변
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ChatPromptTemplate으로 프롬프트를 만들어줘.
    system: '제공된 context만 사용해 답변하세요. 모르면 모른다고 하세요.'
    human: 'Context:\n{context}\n\nQuestion: {question}'
    context는 문서 리스트를 '\n\n---\n\n'으로 구분해 합쳐줘"
→ 역할이 명확한 구조화된 프롬프트
→ 근거와 질문이 분리된 디버깅 가능한 형식
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 문서를 구분자 없이 이어 붙임 | LLM이 문서 경계를 인식하지 못함 | `\n\n---\n\n`으로 문서 간 구분 명시 |
| 시스템 메시지 없이 한 번에 주입 | 역할 지시 없어 환각 위험 | system에 "context만 사용" 지시 명시 |
| context 변수 누락 시 에러 처리 없음 | 검색 결과 0건 시 빈 context 전달 | 빈 context 시 "관련 문서를 찾지 못했습니다" 처리 |
| 템플릿 변수명과 chain 입력 불일치 | KeyError로 조용한 실패 | partial_variables나 명시적 매핑으로 연결 |
| context 길이 제한 없음 | 토큰 한도 초과로 답변 잘림 | 최대 청크 수나 토큰 수 제한 추가 |

## AI 협업 팁

프롬프트 구성과 컨텍스트 주입 관련 효과적인 AI 프롬프트 패턴:

1. **ChatPromptTemplate 요청**: "system에 역할 지시, human에 context와 question을 분리해 넣는 ChatPromptTemplate 작성해줘"
2. **문서 포맷터 요청**: "Document 리스트를 받아 page_content를 구분자로 합치고 source 메타데이터를 각 문서 앞에 붙이는 format_docs 함수 작성해줘"
3. **입력 검증 요청**: "context가 비거나 question이 없을 때 안전하게 처리하는 프롬프트 래퍼 함수 작성해줘"

예시 프롬프트:
> "ChatPromptTemplate.from_messages로 RAG 프롬프트를 만들어줘. system='아래 context만 참고해 답변하세요. context에 없으면 모른다고 하세요.' human='Context:\n{context}\n\nQuestion: {question}\nAnswer:'. format_docs 함수로 Document 리스트를 '\n\n---\n\n'으로 결합."

## 운영 체크리스트

- [ ] 시스템 메시지에 "context만 사용" 지시가 명시됐는가?
- [ ] 여러 문서 사이에 구분자가 있는가?
- [ ] context가 비었을 때 안전하게 처리되는가?
- [ ] 템플릿 변수명이 chain 입력 키와 일치하는가?
- [ ] 다음 글에서 이 프롬프트를 retriever, llm과 LCEL로 연결할 준비가 됐는가?

## 처음 질문으로 돌아가기

프롬프트 구성과 컨텍스트 주입을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 역할과 구조를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 RAG 프롬프트의 품질은 크게 다릅니다.

## 정리

프롬프트 구성과 컨텍스트 주입은 바이브코딩을 위한 RAG 심화에서 검색 결과를 LLM이 읽을 수 있는 형식으로 변환하는 핵심 계층입니다. 시스템 메시지 역할 지시, 문서 구분자, context 빈 값 처리의 중요성을 이해했습니다. 다음 글에서는 retriever, 프롬프트, LLM을 LCEL로 연결하는 RAG chain 조립을 다룹니다.

## 참고 자료

- [LangChain PromptTemplate](https://python.langchain.com/docs/concepts/prompt_templates/)
- [ChatPromptTemplate API](https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.chat.ChatPromptTemplate.html)
- [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/concepts/lcel/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-deep-dive/ko/04-prompt-construction-and-context-injection)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 RAG 심화 (1/6): 문서 로딩과 청크 전략
- 바이브코딩을 위한 RAG 심화 (2/6): 임베딩과 벡터 인덱스
- 바이브코딩을 위한 RAG 심화 (3/6): Retriever 설계
- **바이브코딩을 위한 RAG 심화 (4/6): 프롬프트 구성과 컨텍스트 주입 (현재 글)**
- 바이브코딩을 위한 RAG 심화 (5/6): RAG Chain 조립
- 바이브코딩을 위한 RAG 심화 (6/6): 평가와 품질 게이트
<!-- toc:end -->

Tags: 바이브코딩, RAG심화, PromptTemplate, AI코딩
