---
title: 'Prompt와 LLM Chain — 체인 첫 번째 구성'
series: langchain-101
episode: 2
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
---

# Prompt와 LLM Chain — 체인 첫 번째 구성

> LangChain 101 시리즈 (2/6)

지난 글에서 LCEL의 기본 구조를 잡았다면, 이번 글에서는 실제로 자주 쓰는 패턴을 하나씩 만들어 봅니다. `ChatPromptTemplate`을 깊이 이해하고, 출력 파서를 선택하고, 체인에 변수를 넣는 방법을 다룹니다.

이번 글에서 다룰 내용은 다음과 같습니다.

- `ChatPromptTemplate`의 메시지 역할과 포맷
- 여러 변수를 가진 프롬프트 만들기
- `StrOutputParser`, `JsonOutputParser` 선택하기
- `RunnablePassthrough`로 입력을 그대로 넘기기
- 완성된 체인 테스트하기

---

## ChatPromptTemplate 구조

`ChatPromptTemplate`은 대화 형식의 프롬프트를 만드는 클래스입니다. 메시지 목록을 받아 LLM에 전달할 형식으로 렌더링합니다.

세 가지 메시지 역할이 있습니다.

- `system`: 모델의 행동 방식을 지정합니다. 페르소나, 제약, 출력 형식 등을 씁니다.
- `human`: 사용자 입력입니다.
- `ai`: 이전 어시스턴트 응답입니다. 멀티턴 시 이력을 넣을 때 씁니다.

```python
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {language} 전문가입니다. 명확하고 간결하게 설명합니다."),
    ("human", "{question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm

response = chain.invoke({
    "language": "파이썬",
    "question": "리스트 컴프리헨션은 언제 쓰는 게 좋나요?",
})

print(response.content)
```

`{language}`와 `{question}` 같은 자리 표시자는 `invoke()`에 넘기는 딕셔너리 키와 일치해야 합니다.

---

## 여러 변수를 가진 프롬프트

복잡한 태스크일수록 프롬프트에 여러 변수가 필요합니다. 모두 딕셔너리로 넘깁니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 코드 리뷰 전문가입니다. "
        "언어: {language}. 리뷰 관점: {review_focus}.",
    ),
    ("human", "다음 코드를 리뷰해 주세요:\n\n```{language}\n{code}\n```"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | StrOutputParser()

result = chain.invoke({
    "language": "python",
    "review_focus": "가독성과 예외 처리",
    "code": """
def read_file(path):
    f = open(path)
    return f.read()
""",
})

print(result)
```

---

## StrOutputParser vs JsonOutputParser

출력 파서는 LLM 응답을 원하는 형태로 변환합니다. 두 가지가 자주 쓰입니다.

**StrOutputParser**: `AIMessage.content`를 문자열로 꺼냅니다. 대부분의 경우 이걸로 충분합니다.

**JsonOutputParser**: 모델이 JSON을 출력하도록 유도하고, 그 결과를 Python 딕셔너리로 파싱합니다. 모델에게 JSON 형식으로 응답하도록 프롬프트를 명시해야 합니다.

```python
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 JSON만 출력합니다. 다른 텍스트는 포함하지 마세요.",
    ),
    (
        "human",
        "{topic}에 대한 정보를 다음 JSON 형식으로 출력하세요:\n"
        '{{"name": "이름", "description": "설명", "use_case": "활용 사례"}}',
    ),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | JsonOutputParser()

result = chain.invoke({"topic": "FAISS"})

print(f"타입: {type(result)}")
print(f"name: {result.get('name')}")
print(f"description: {result.get('description')}")
print(f"use_case: {result.get('use_case')}")
```

JSON 파싱이 불안정하다면 LangChain의 `with_structured_output()`을 쓰는 편이 더 안정적입니다. 이 방법은 llm-api-production-101 시리즈에서 다룹니다.

---

## RunnablePassthrough — 입력을 그대로 전달

파이프 체인에서 입력 일부를 그대로 뒤로 전달하고 싶을 때 `RunnablePassthrough`를 씁니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "문서를 참고해서 질문에 답하세요."),
    ("human", "문서: {context}\n\n질문: {question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# context는 그대로, question은 그대로 — 이 체인은 입력을 직접 전달
chain = (
    {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 더 일반적인 패턴: 딕셔너리 입력을 그대로 활용
chain2 = prompt | llm | StrOutputParser()

result = chain2.invoke({
    "context": "FAISS는 Facebook AI Research에서 만든 벡터 검색 라이브러리입니다.",
    "question": "FAISS는 누가 만들었나요?",
})

print(result)
```

`RunnablePassthrough`는 나중에 Retriever와 체인을 연결할 때 자주 씁니다. 4편(Retriever)에서 실제 패턴을 볼 수 있습니다.

---

## 체인에 fallback 추가하기

모델 호출이 실패할 때 대체 체인을 실행하도록 `.with_fallbacks()`를 씁니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("human", "{question}"),
])

primary_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

fallback_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

primary_chain = prompt | primary_llm | StrOutputParser()
fallback_chain = prompt | fallback_llm | StrOutputParser()

chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])

result = chain_with_fallback.invoke({"question": "파이썬 예외 처리 방법은?"})
print(result)
```

이 패턴은 주 모델이 다운되거나 속도 제한에 걸렸을 때 자동으로 대체 모델로 전환합니다.

---

## 마무리

`ChatPromptTemplate`으로 다중 변수 프롬프트를 만들고, `StrOutputParser`와 `JsonOutputParser`의 차이를 확인했습니다. `RunnablePassthrough`는 다음 글들에서 더 자주 나옵니다.

다음 글에서는 Retriever를 체인에 연결해서 문서 검색 결과를 컨텍스트로 주입하는 방법을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangChain 소개 — LCEL과 Runnable 기본](./01-lcel-runnable-basics.md)
- **Prompt와 LLM Chain — 체인 첫 번째 구성 (현재 글)**
- Retriever — 문서 검색과 컨텍스트 주입 (예정)
- Tool Calling — 외부 도구 연결하기 (예정)
- Streaming — 실시간 출력 처리 (예정)
- 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [ChatPromptTemplate 공식 문서](https://python.langchain.com/docs/modules/model_io/prompts/quick_start/)
- [Output parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [RunnablePassthrough](https://python.langchain.com/docs/expression_language/primitives/passthrough/)

Tags: LangChain, LCEL, Python, LLM
