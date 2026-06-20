---
title: "바이브코딩을 위한 LangChain (1/6): LangChain 소개 — LCEL과 Runnable 기본"
series: langchain-101
episode: 1
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangChain
- LCEL
- Python
- LLM
---

# 바이브코딩을 위한 LangChain (1/6): LangChain 소개 — LCEL과 Runnable 기본

이 글은 **바이브코딩을 위한 LangChain** 시리즈의 첫 번째 글입니다. LangChain Expression Language(LCEL)와 Runnable 인터페이스를 통해 LangChain의 핵심 개념을 설명합니다.

---

LangChain을 처음 쓸 때 가장 많이 하는 실수는 "LangChain이 복잡하다"고 생각하는 것입니다. LangChain의 모든 컴포넌트는 Runnable 인터페이스를 구현합니다. invoke, batch, stream — 세 가지 메서드만 알면 LangChain의 모든 컴포넌트를 같은 방식으로 사용할 수 있습니다.

바이브코딩으로 AI에게 "LangChain으로 LLM 호출해줘"라고 하면 코드가 나옵니다. 그런데 파이프(`|`) 연산자가 무엇을 하는지, 왜 `.invoke()`를 쓰는지 이해 없이 사용하면 오류가 나도 어디가 문제인지 모릅니다.

이 글에서는 LCEL의 파이프 연산자와 Runnable 인터페이스를 코드 예시와 함께 설명합니다.

> "LangChain의 모든 컴포넌트는 Runnable입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. `chain.invoke({"input": "..."})` 에서 invoke의 역할이 무엇인가요?
2. `|` 연산자가 LangChain에서 무엇을 의미하나요?
3. `batch()`와 `invoke()`의 차이가 무엇인가요?
4. `RunnableLambda`는 어떤 상황에서 쓰나요?
5. 체인의 중간 결과를 어떻게 확인하나요?

---

## Runnable 인터페이스

모든 LangChain 컴포넌트는 세 가지 메서드를 지원합니다.

```python
from langchain_core.runnables import RunnableLambda

# 단일 입력
result = chain.invoke({"question": "LangChain이란?"})

# 여러 입력 동시 처리
results = chain.batch([
    {"question": "질문1"},
    {"question": "질문2"},
])

# 스트리밍
for chunk in chain.stream({"question": "답변을 스트리밍으로 받고 싶어요"}):
    print(chunk, end="", flush=True)
```

## 파이프 연산자로 체인 연결

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("다음 질문에 답하세요: {question}")
llm = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke({"question": "Python이란 무엇인가요?"})
```

## RunnableLambda로 커스텀 단계 추가

```python
from langchain_core.runnables import RunnableLambda

def add_context(inputs: dict) -> dict:
    inputs["context"] = "추가 컨텍스트"
    return inputs

chain = RunnableLambda(add_context) | prompt | llm | parser
```

## 중간 결과 확인

```python
from langchain_core.runnables import RunnablePassthrough

chain_with_debug = (
    RunnablePassthrough.assign(formatted=prompt)  # prompt 결과를 formatted에 저장
    | {"input": lambda x: x["formatted"], "original": RunnablePassthrough()}
)
```

---

## Before / After

| 항목 | Before (직접 호출) | After (LCEL 체인) |
|------|------------------|--------------------|
| 단계 연결 | 중간 변수 할당 | `|` 연산자 |
| 배치 처리 | 루프 작성 | `.batch()` 자동 병렬 |
| 스트리밍 | 별도 구현 | `.stream()` 바로 사용 |
| 재사용 | 복붙 | 체인 변수 재사용 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| dict 대신 str 입력 | 오류 | invoke에는 dict 전달 |
| 파이프 순서 오류 | 타입 불일치 | prompt → llm → parser 순서 |
| 스트림 without 파서 | AIMessageChunk 반환 | StrOutputParser 추가 |
| batch에 단일 항목 | 불필요한 리스트 래핑 | 단일이면 invoke 사용 |

---

## AI 활용 팁

```
LangChain LCEL로 간단한 QA 체인을 만들어줘.
ChatPromptTemplate → ChatOpenAI → StrOutputParser를 파이프로 연결해.
invoke, batch, stream 세 가지 호출 방법을 모두 예시로 보여줘.
RunnableLambda로 중간에 입력을 변환하는 단계도 추가해줘.
```

---

## 체크리스트

- [ ] langchain-openai, langchain-core 설치
- [ ] OPENAI_API_KEY 환경변수 설정
- [ ] ChatPromptTemplate + ChatOpenAI + StrOutputParser 체인 구성
- [ ] invoke/batch/stream 각각 테스트
- [ ] RunnableLambda로 전처리 단계 추가
- [ ] 체인 중간 결과 디버그 방법 확인

---

## 처음 질문으로 돌아가기

"LangChain이 복잡해서 어디서 시작해야 할지 모르겠어요" — Runnable 인터페이스가 기초입니다. invoke(단일), batch(여러), stream(스트리밍) — 이 세 가지를 이해하면 LangChain의 모든 컴포넌트를 같은 방식으로 사용할 수 있습니다. 파이프 연산자로 연결하면 체인이 됩니다.

---

## 정리

- 모든 LangChain 컴포넌트는 Runnable 인터페이스(invoke/batch/stream)를 구현한다
- `|` 연산자로 컴포넌트를 연결해 체인을 만든다
- RunnableLambda로 임의의 Python 함수를 체인에 끼울 수 있다
- 체인 연결 순서: prompt → llm → parser

---

## 참고 자료

- [LangChain LCEL 공식 문서](https://python.langchain.com/docs/concepts/lcel/)
- [Runnable 인터페이스](https://python.langchain.com/docs/concepts/runnables/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- Runnable 인터페이스
- 파이프 연산자로 체인 연결
- RunnableLambda로 커스텀 단계 추가
- 중간 결과 확인
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangChain, LCEL, Python, LLM
