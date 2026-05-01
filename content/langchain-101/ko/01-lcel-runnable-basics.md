---
title: 'LangChain 소개 — LCEL과 Runnable 기본'
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
last_reviewed: '2026-05-01'
---

# LangChain 소개 — LCEL과 Runnable 기본

## 이 글에서 답할 질문

- LCEL은 왜 생겼고, 어떤 연결 코드를 줄여 주는가
- Runnable 인터페이스는 어떤 공통 호출 방식을 강제하는가
- `invoke()`, `batch()`, `stream()`은 언제 각각 쓰는가
- `|` 연산자로 연결한 체인은 내부에서 어떤 순서로 흘러가는가

> LangChain에서는 입력과 출력 타입만 맞으면 거의 모든 컴포넌트를 같은 파이프 규칙으로 연결할 수 있습니다.

![이 글에서 답할 질문](../../../assets/langchain-101/01/01-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_template("{topic}을 한 문단으로 설명해 주세요.")
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
chain = prompt | llm | StrOutputParser()

print(chain.invoke({"topic": "LCEL"}))
```

## 이 코드에서 봐야 할 것

- `ChatPromptTemplate`은 딕셔너리 입력을 받아 메시지로 바꿉니다.
- `ChatGroq`는 메시지를 받아 `AIMessage`를 반환합니다.
- `StrOutputParser`가 마지막에 붙으면서 체인 출력 타입이 문자열로 고정됩니다.
- 이 세 단계가 모두 Runnable이라서 `|` 하나로 조립됩니다.

## 실무에서 헷갈리는 지점

- LCEL은 새 모델이 아니라 컴포넌트 연결 문법입니다.
- `invoke()`와 `stream()`은 체인 정의가 아니라 호출 방식만 다릅니다.
- `RunnableLambda`는 복잡한 비즈니스 로직용 프레임워크가 아니라 가벼운 변환용 연결점에 가깝습니다.

## 체크리스트

- [ ] 어떤 값이 프롬프트로 들어가고 어떤 값이 문자열로 나오는지 설명할 수 있다
- [ ] `invoke()`, `batch()`, `stream()`의 용도 차이를 구분할 수 있다
- [ ] `prompt | llm | parser` 구조를 직접 실행해 볼 수 있다

LangChain 101 시리즈 (1/6)

예제 코드: [github.com/yeongseon-books/langchain-101](https://github.com/yeongseon-books/langchain-101/tree/main/01-lcel-runnable-basics)

## 이 글에서 답할 질문

- LCEL은 왜 `|` 연산자로 컴포넌트를 연결할까
- Runnable 인터페이스는 어떤 메서드를 공통으로 제공할까
- Prompt, LLM, Parser가 체인 안에서 어떤 타입으로 이어질까
- `invoke()`와 `batch()`는 언제 구분해서 써야 할까

> LCEL은 프롬프트, 모델, 파서를 같은 Runnable 규약으로 묶어 한 번의 데이터 흐름으로 실행하는 방법입니다.

## 핵심 흐름 한눈에 보기

![핵심 흐름 한눈에 보기](../../../assets/langchain-101/01/01-02-the-flow-at-a-glance.ko.png)
LangChain을 처음 접하면 코드보다 용어가 더 먼저 막힙니다. LCEL, Runnable, Chain, Pipe — 개념은 많은데 어떤 게 핵심인지 잘 보이지 않습니다. 이번 글은 LangChain의 설계 중심인 LCEL(LangChain Expression Language)과 Runnable 인터페이스가 무엇인지, 그리고 왜 이런 구조를 썼는지부터 잡습니다.

이 시리즈는 LangChain을 API로 사용하는 방법에 집중합니다. 챗봇, RAG, 에이전트 같은 애플리케이션 패턴은 별도 시리즈(ai-app-patterns-101)에서 다룹니다.

이번 글에서 다룰 내용은 다음과 같습니다.

- LangChain이 해결하려는 문제
- Runnable 인터페이스와 `invoke()`, `batch()`, `stream()`
- LCEL 파이프 연산자 `|`로 체인 만들기
- 가장 단순한 체인 실행
- 왜 이 구조가 유용한가

---

## LangChain이 해결하려는 문제

LLM 앱을 만들면 반복되는 작업이 나타납니다. 프롬프트를 조립하고, LLM에 보내고, 응답을 파싱해서, 다음 단계로 넘기는 패턴입니다. 이 과정에서 연결 코드가 점점 늘어납니다.

```python
# 연결 코드가 늘어나는 전형적인 패턴
prompt_text = f"다음 텍스트를 요약하세요: {user_input}"
response = client.chat.completions.create(model="...", messages=[{"role": "user", "content": prompt_text}])
raw_output = response.choices[0].message.content
parsed = raw_output.strip()
next_prompt = f"이 요약을 번역하세요: {parsed}"
# ...반복
```

LangChain은 이 연결 코드를 컴포넌트로 추상화합니다. 핵심 아이디어는 단순합니다. 모든 컴포넌트가 같은 인터페이스를 가지면, 파이프처럼 연결할 수 있습니다.

---

## Runnable 인터페이스

LangChain의 거의 모든 컴포넌트는 `Runnable` 인터페이스를 구현합니다. 세 가지 핵심 메서드가 있습니다.

- `invoke(input)` — 입력을 받아 출력을 반환합니다. 동기 단일 호출입니다.
- `batch(inputs)` — 입력 목록을 받아 출력 목록을 반환합니다.
- `stream(input)` — 출력을 토큰 단위로 순차 반환합니다.

이 세 메서드가 일관되게 있기 때문에, 어떤 컴포넌트든 교체 가능하고 조합 가능합니다.

```python
import os

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# invoke: 단일 호출
response = llm.invoke("파이썬의 장점을 두 문장으로 설명해 주세요.")
print(response.content)
```

`ChatGroq`는 `Runnable`을 구현하므로 `invoke()`를 바로 쓸 수 있습니다.

---

## LCEL과 파이프 연산자

LCEL은 `|` 연산자로 Runnable 컴포넌트를 연결하는 문법입니다. 왼쪽 컴포넌트의 출력이 오른쪽 컴포넌트의 입력이 됩니다.

```python
chain = component_a | component_b | component_c
result = chain.invoke(input)
```

이것이 LangChain에서 가장 자주 보이는 패턴입니다. 구체적인 예를 보겠습니다.

```bash
pip install langchain langchain-groq
```

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# 컴포넌트 준비
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 간결하게 설명하는 전문가입니다."),
    ("human", "{topic}을 두 문장으로 설명해 주세요."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

parser = StrOutputParser()

# 체인 조립
chain = prompt | llm | parser

# 실행
result = chain.invoke({"topic": "임베딩 벡터"})
print(result)
```

세 컴포넌트가 하는 일을 각각 보겠습니다.

**`ChatPromptTemplate`**: 딕셔너리를 받아 메시지 목록을 반환합니다. `{topic}` 자리에 입력값을 넣습니다.

**`ChatGroq`**: 메시지 목록을 받아 `AIMessage` 객체를 반환합니다.

**`StrOutputParser`**: `AIMessage`를 받아 `.content` 문자열을 반환합니다.

파이프 연산자가 이 세 단계를 하나의 체인으로 묶습니다. `chain.invoke({"topic": "임베딩 벡터"})`를 부르면 세 단계가 순서대로 실행됩니다.

---

## 각 컴포넌트를 개별 실행해 보기

파이프로 묶기 전에 각 컴포넌트를 따로 실행해 보면 내부 흐름이 더 명확해집니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 간결하게 설명하는 전문가입니다."),
    ("human", "{topic}을 두 문장으로 설명해 주세요."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

parser = StrOutputParser()

# 1단계: 프롬프트 렌더링
messages = prompt.invoke({"topic": "임베딩 벡터"})
print("=== 1단계: 메시지 ===")
for m in messages.messages:
    print(f"  [{m.type}] {m.content}")

# 2단계: LLM 호출
ai_message = llm.invoke(messages)
print(f"\n=== 2단계: AIMessage ===")
print(f"  타입: {type(ai_message).__name__}")
print(f"  내용: {ai_message.content[:80]}...")

# 3단계: 파싱
text = parser.invoke(ai_message)
print(f"\n=== 3단계: 문자열 ===")
print(f"  {text}")
```

---

## RunnableLambda — 함수를 Runnable로

파이프 체인에 커스텀 Python 함수를 끼워 넣으려면 `RunnableLambda`를 씁니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("human", "{text}를 한 문장으로 요약해 주세요."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

def add_word_count(text: str) -> str:
    return f"{text}\n\n(글자 수: {len(text)}자)"

chain = prompt | llm | StrOutputParser() | RunnableLambda(add_word_count)

result = chain.invoke({"text": "벡터 검색은 텍스트를 숫자 벡터로 변환해 의미 기반으로 검색합니다."})
print(result)
```

`RunnableLambda`는 일반 Python 함수를 파이프 체인에 넣을 수 있게 해줍니다. 출력 후처리, 로깅, 변환 같은 간단한 작업에 유용합니다.

---

## batch()로 여러 입력 처리

`batch()`는 입력 목록을 받아 각각 처리한 뒤 결과 목록을 반환합니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("human", "{topic}을 한 문장으로 설명해 주세요."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | StrOutputParser()

topics = [
    {"topic": "임베딩"},
    {"topic": "FAISS"},
    {"topic": "RAG"},
]

results = chain.batch(topics)

for topic_dict, result in zip(topics, results):
    print(f"[{topic_dict['topic']}] {result}\n")
```

`batch()`는 내부적으로 병렬 처리를 시도합니다. API 속도 제한이 있는 환경에서는 `max_concurrency` 옵션으로 동시 요청 수를 제어할 수 있습니다.

```python
results = chain.batch(topics, config={"max_concurrency": 2})
```

---

## 이 코드에서 봐야 할 것

- `prompt | llm | parser`는 문자열 결합이 아니라 Runnable 간 입출력 계약을 연결하는 파이프라인입니다.
- `ChatPromptTemplate`의 출력은 최종 문자열이 아니라 메시지 객체이며, 그 다음 단계인 `ChatGroq`가 그 객체를 그대로 입력으로 받습니다.
- `StrOutputParser`를 끝에 두면 `AIMessage`를 후속 코드가 다루기 쉬운 일반 문자열로 정리할 수 있습니다.
- `batch()`는 체인 구조를 바꾸지 않고 입력만 여러 개 넣는 방식이라, 단건 `invoke()`를 이해한 뒤 확장하기 좋습니다.

## 실무에서 헷갈리는 지점

- LCEL을 새 문법으로 보기 쉽지만, 실제 핵심은 컴포넌트마다 같은 `Runnable` 인터페이스를 가진다는 점입니다.
- `invoke()` 결과 타입이 단계마다 달라집니다. 프롬프트 단계는 메시지 묶음, 모델 단계는 `AIMessage`, 파서 뒤는 문자열입니다.
- `RunnableLambda`는 편리하지만 비즈니스 로직이 길어지면 체인 가독성을 해칠 수 있습니다. 후처리는 얇게 유지하는 편이 좋습니다.

## 체크리스트

- [ ] `ChatPromptTemplate`, `ChatGroq`, `StrOutputParser`가 어떤 입력과 출력을 주고받는지 설명할 수 있다
- [ ] `invoke()`와 `batch()`를 같은 체인에서 각각 호출해 볼 수 있다
- [ ] plain Python 함수를 `RunnableLambda`로 체인에 넣는 이유를 이해했다

## 마무리

LCEL과 Runnable 인터페이스가 왜 편리한지 이해했습니다. 모든 컴포넌트가 같은 `invoke` / `batch` / `stream` 인터페이스를 가지므로, `|`로 연결하는 것만으로 파이프라인이 됩니다.

다음 글에서는 `ChatPromptTemplate`을 더 깊이 다루고, `ChatGroq`와 연결해서 실용적인 체인을 만들어 봅니다.

<!-- blog-only:start -->
다음 글: [Prompt와 LLM Chain — 체인 첫 번째 구성](./02-prompt-llm-chain.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- **LangChain 소개 — LCEL과 Runnable 기본 (현재 글)**
- Prompt와 LLM Chain — 체인 첫 번째 구성 (예정)
- Retriever — 문서 검색과 컨텍스트 주입 (예정)
- Tool Calling — 외부 도구 연결하기 (예정)
- Streaming — 실시간 출력 처리 (예정)
- 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain LCEL 공식 문서](https://python.langchain.com/docs/expression_language/)
- [Runnable 인터페이스](https://python.langchain.com/docs/expression_language/interface/)
- [ChatGroq 통합](https://python.langchain.com/docs/integrations/chat/groq/)
- [langchain-groq PyPI](https://pypi.org/project/langchain-groq/)

Tags: LangChain, LCEL, Python, LLM
