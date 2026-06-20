---
title: "바이브코딩을 위한 LangChain (2/6): Prompt와 LLM Chain — 체인 첫 번째 구성"
series: langchain-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangChain
- Prompt
- Python
- LLM
---

# 바이브코딩을 위한 LangChain (2/6): Prompt와 LLM Chain — 체인 첫 번째 구성

이 글은 **바이브코딩을 위한 LangChain** 시리즈의 두 번째 글입니다. ChatPromptTemplate, 출력 파서, RunnablePassthrough를 사용해 실용적인 체인을 구성하는 방법을 다룹니다.

---

LCEL과 Runnable의 기본을 알았습니다. 이제 실제로 쓸 수 있는 체인을 만들어야 합니다. "ChatPromptTemplate이 왜 필요한가요? f-string으로 프롬프트 만들면 되지 않나요?" — f-string으로 시작해서 프롬프트가 복잡해지면, 역할 분리가 어렵고 재사용이 힘들어집니다.

바이브코딩으로 AI에게 "LangChain으로 요약 체인 만들어줘"라고 하면 코드가 나옵니다. ChatPromptTemplate의 변수 바인딩, 출력 파서의 역할, fallback 처리를 모르면 체인을 수정하거나 확장하기 어렵습니다.

이 글에서는 실용적인 체인 구성 패턴을 코드와 함께 설명합니다.

> "프롬프트 템플릿은 프롬프트의 재사용 가능한 설계도입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. `ChatPromptTemplate.from_messages`와 `from_template`의 차이가 무엇인가요?
2. `StrOutputParser`와 `JsonOutputParser`는 각각 언제 쓰나요?
3. `RunnablePassthrough`가 왜 필요한가요?
4. 체인에 fallback을 추가하는 이유가 무엇인가요?
5. 시스템 프롬프트와 사용자 메시지를 분리하는 이유가 있나요?

---

## ChatPromptTemplate

```python
from langchain_core.prompts import ChatPromptTemplate

# 시스템 + 사용자 메시지 분리
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role}입니다. 한국어로 답변하세요."),
    ("human", "{question}"),
])

# 단일 템플릿
simple_prompt = ChatPromptTemplate.from_template(
    "다음 텍스트를 요약해주세요:\n\n{text}"
)
```

## 출력 파서

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel

class SummaryOutput(BaseModel):
    summary: str
    keywords: list[str]

# 문자열 출력
str_chain = simple_prompt | llm | StrOutputParser()

# JSON 출력
json_chain = (
    ChatPromptTemplate.from_template(
        "다음을 JSON으로 요약해주세요:\n{text}\n\n출력 형식: {{\"summary\": \"...\", \"keywords\": [...]}}"
    )
    | llm
    | JsonOutputParser()
)
```

## RunnablePassthrough로 컨텍스트 전달

```python
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {
        "context": retriever,  # 검색 결과
        "question": RunnablePassthrough(),  # 원본 질문 그대로 전달
    }
    | ChatPromptTemplate.from_messages([
        ("system", "컨텍스트를 기반으로 답변하세요:\n{context}"),
        ("human", "{question}"),
    ])
    | llm
    | StrOutputParser()
)
```

## Fallback

```python
from langchain_openai import ChatOpenAI

primary_llm = ChatOpenAI(model="gpt-4o")
fallback_llm = ChatOpenAI(model="gpt-4o-mini")

# primary가 실패하면 fallback으로
robust_llm = primary_llm.with_fallbacks([fallback_llm])
chain = prompt | robust_llm | StrOutputParser()
```

---

## Before / After

| 항목 | Before (f-string) | After (ChatPromptTemplate) |
|------|------------------|---------------------------|
| 재사용 | 복붙 | 템플릿 변수로 재사용 |
| 역할 분리 | 한 문자열에 혼합 | system/human 분리 |
| JSON 파싱 | 수동 json.loads | JsonOutputParser |
| 오류 복구 | 없음 | fallback LLM |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 변수명 불일치 | KeyError | 템플릿 변수와 invoke 키 일치 |
| 중괄호 이스케이프 누락 | 템플릿 파싱 오류 | JSON 예시는 `{{}}` 사용 |
| 파서 없음 | AIMessage 객체 반환 | StrOutputParser 추가 |
| fallback 없음 | API 오류 시 전체 중단 | with_fallbacks 설정 |

---

## AI 활용 팁

```
LangChain으로 문서 요약 체인을 만들어줘.
ChatPromptTemplate.from_messages로 system/human 역할을 분리하고,
출력이 JSON이면 JsonOutputParser, 텍스트면 StrOutputParser를 사용해줘.
RunnablePassthrough로 원본 텍스트를 체인 내내 유지해줘.
primary LLM 실패 시 fallback LLM으로 전환하는 로직도 포함해줘.
```

---

## 체크리스트

- [ ] ChatPromptTemplate.from_messages로 system/human 분리
- [ ] 템플릿 변수명과 invoke 딕셔너리 키 일치 확인
- [ ] StrOutputParser 또는 JsonOutputParser 추가
- [ ] RunnablePassthrough로 원본 입력 유지
- [ ] with_fallbacks로 fallback LLM 설정
- [ ] JSON 프롬프트에서 중괄호 이스케이프(`{{}}`)

---

## 처음 질문으로 돌아가기

"f-string으로 프롬프트 만들면 되는 거 아닌가요?" — 간단한 체인에는 됩니다. 시스템 역할과 사용자 메시지를 분리하고, JSON 출력을 파싱하고, 여러 체인에서 같은 템플릿을 재사용하는 순간 ChatPromptTemplate이 필요합니다.

---

## 정리

- ChatPromptTemplate.from_messages로 system/human 역할을 명확히 분리한다
- StrOutputParser는 텍스트, JsonOutputParser는 구조화 JSON 출력에 사용한다
- RunnablePassthrough로 원본 입력을 체인의 다른 단계에 전달한다
- with_fallbacks로 API 오류 시 자동 백업 모델로 전환한다

---

## 참고 자료

- [ChatPromptTemplate 문서](https://python.langchain.com/docs/concepts/prompt_templates/)
- [출력 파서 목록](https://python.langchain.com/docs/concepts/output_parsers/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- ChatPromptTemplate
- 출력 파서
- RunnablePassthrough
- Fallback
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangChain, Prompt, Python, LLM
