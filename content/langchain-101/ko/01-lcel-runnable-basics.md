---
title: LangChain 소개 — LCEL과 Runnable 기본
series: langchain-101
episode: 1
language: ko
status: publish-ready
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
last_reviewed: '2026-05-06'
seo_description: LCEL과 Runnable 인터페이스로 LLM 파이프라인을 한 줄로 잇는 방법을 정리합니다
---

# LangChain 소개 — LCEL과 Runnable 기본

> LangChain 101 시리즈 (1/6)

<!-- a-grade-intro:begin -->

**핵심 질문**: *LCEL* 은 *어떤* *문제* 를 *해결* 하나요?

> *프롬프트* `→` *모델* `→` *파서* 사이의 *글루 코드* 를 *없애* 줍니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *LCEL* 이 *생긴* *이유*
- *Runnable* 인터페이스의 *의미*
- *파이프* `|` 연산자의 *동작*
- *invoke* 와 *입출력 타입* 규약
- *RunnablePassthrough* 의 *역할*

## 왜 중요한가

*같은* *기능* 도 *글루 코드* 가 *길수록* *오류* 가 *섞입니다*. *LCEL* 은 *컴포넌트 합성* 을 *한 줄* 로 *바꿉니다*.

## 개념 한눈에 보기

```mermaid
flowchart LR
    I["입력 (dict)"] --> P[Prompt]
    P --> L[LLM]
    L --> O[OutputParser]
    O --> R["결과 (str)"]
```

## 핵심 용어 정리

- **LCEL**: *LangChain Expression Language*. *컴포넌트* 를 `|` 로 *잇는* *DSL*.
- **Runnable**: `invoke`, `stream`, `batch` 를 *지원* *하는* *공통* *인터페이스*.
- **`invoke`**: *입력* 한 *번* 으로 *결과* 한 *번*.
- **`|` 파이프**: *왼쪽* *출력* 을 *오른쪽* *입력* 으로 *전달*.
- **RunnablePassthrough**: *입력* 을 *그대로* *통과* *시키는* *어댑터*.

## Before/After

**Before**: "*프롬프트* 를 *문자열* 로 *조립* 하고 *LLM* 호출 결과를 *수동* 으로 *파싱* 합니다."

**After**: "`prompt | llm | parser` 한 줄이 *같은* *흐름* 을 *대체* 합니다."

## 실습: LCEL 첫 체인 5단계

### 1단계 — Prompt 준비

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 도우미입니다."),
    ("human", "{topic} 을 한 문장으로 설명해 주세요."),
])
```

### 2단계 — LLM 준비

```python
import os
from langchain_groq import ChatGroq

os.environ.setdefault("GROQ_API_KEY", "your-key-here")
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
```

### 3단계 — Parser 준비

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
```

### 4단계 — `|` 로 잇기

```python
chain = prompt | llm | parser
```

### 5단계 — `invoke`

```python
answer = chain.invoke({"topic": "LCEL"})
print(answer)
# 예상 출력: LCEL은 LangChain 컴포넌트를 파이프로 잇는 표현식 언어입니다.
```

## 이 코드에서 주목할 점

- `|` 는 *왼쪽* *Runnable* 의 *출력 타입* 이 *오른쪽* *입력 타입* 과 *맞아야* *동작* 합니다.
- *체인* 자체도 *Runnable* 입니다. 다시 `|` 로 *잇을* *수* *있습니다*.
- *입력* 은 *항상* *dict* 입니다. *템플릿 변수* 와 *키* 가 *일치* *해야* 합니다.

## 자주 하는 실수 5가지

1. ***템플릿 변수* 와 *invoke 키* 가 *불일치*** — `{topic}` 인데 `{"input": ...}` 을 넘기면 실패합니다.
2. ***OutputParser* 빠뜨리기** — *AIMessage* 객체가 그대로 나와 *문자열* 처럼 *쓰지* *못* 합니다.
3. ***async/sync 혼용*** — `chain.invoke()` 와 `await chain.ainvoke()` 를 *섞어* *씁니다*.
4. ***API 키 미설정*** — `GROQ_API_KEY` 가 *없으면* *401* 입니다.
5. ***체인 변수* *재할당*** — `chain | x` 의 *결과* 를 *새 변수* 에 *받지 않으면* *체인* 이 *그대로* 입니다.

## 실무에서는 이렇게 쓰입니다

*프로덕션* 에서는 *프롬프트 템플릿*, *LLM*, *파서*, *후처리 함수* 를 *한 체인* 으로 *묶고* `invoke` / `stream` / `batch` 를 *상황* 에 *맞게* *호출* 합니다.

*트레이싱* 도구 (LangSmith) 를 *연결* 하면 *체인* 의 *각* *단계* *입출력* 이 *자동* *기록* 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *타입* 이 *맞으면* *합성* 이 *가능* 합니다.
- *파서* 까지 *체인* 안에 *넣어야* *호출 측* 이 *깔끔* 합니다.
- *비용* 은 *모델* 단계, *지연* 은 *전체* 합 으로 봅니다.
- *재시도* 는 *체인* 외부 가 아니라 *Runnable* 옵션으로.
- *테스트* 는 *MockLLM* 으로 *오프라인* 에서.

## 체크리스트

- [ ] `prompt | llm | parser` 형태를 *한 번* *작성*.
- [ ] *템플릿 변수* 와 *입력 키* *일치* *확인*.
- [ ] `GROQ_API_KEY` *환경 변수* *설정*.
- [ ] *예상 출력* 을 *직접* *invoke* 로 *확인*.

## 연습 문제

1. *시스템 메시지* 를 *영어* 로 바꾸고 *결과* 가 *어떻게* *바뀌는지* *비교* 하세요.
2. `temperature` 를 0.7 로 올린 뒤 같은 *invoke* 를 3 번 *반복* 했을 때 *차이* 를 *기록* 하세요.
3. *체인* 끝에 *`lambda x: x.upper()`* 를 *RunnableLambda* 로 *연결* 해 보세요.

## 정리 및 다음 단계

다음 글은 *Prompt와 LLM Chain — 체인 첫 번째 구성* 입니다.

<!-- toc:begin -->
## 시리즈 목차

- **LangChain 소개 — LCEL과 Runnable 기본 (현재 글)**
- Prompt와 LLM Chain — 체인 첫 번째 구성 (예정)
- Retriever — 문서 검색과 컨텍스트 주입 (예정)
- Tool Calling — 외부 도구 연결하기 (예정)
- Streaming — 실시간 출력 처리 (예정)
- 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

## 참고 자료

- [LangChain Expression Language](https://python.langchain.com/docs/concepts/lcel/)
- [Runnable interface](https://python.langchain.com/docs/concepts/runnables/)
- [ChatGroq integration](https://python.langchain.com/docs/integrations/chat/groq/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)

Tags: LangChain, LCEL, Python, LLM
