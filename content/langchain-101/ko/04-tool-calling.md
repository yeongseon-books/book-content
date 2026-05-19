---
title: Tool Calling — 외부 도구 연결하기
series: langchain-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-15'
seo_description: LangChain Tool Calling으로 LLM이 함수를 호출하고 결과를 받아 답하는 방법을 정리합니다
---

# Tool Calling — 외부 도구 연결하기

이 글은 LangChain 101 시리즈의 4번째 글입니다.

LLM은 텍스트를 잘 만듭니다. 하지만 계산, 현재 시각 조회, 데이터베이스 질의, 외부 API 호출은 텍스트 생성만으로 끝나지 않습니다. 그래서 실제 애플리케이션에서는 모델이 모든 일을 "알아서" 하는 것이 아니라, **무엇을 물어봐야 할지 판단하는 역할**을 맡고, 실제 실행은 애플리케이션의 함수나 도구가 담당하게 됩니다.

Tool Calling은 바로 그 경계를 명확히 해 줍니다. 모델은 Python 코드를 직접 실행하는 것이 아니라, 어떤 함수를 어떤 인자로 호출하고 싶은지 구조화된 요청을 내보냅니다. 그 요청을 실행하고 결과를 다시 대화에 넣는 것은 여전히 애플리케이션의 책임입니다.

---

## 이 글에서 다룰 문제

- Tool Calling은 일반 프롬프트 체인과 무엇이 다를까요?
- `@tool`과 타입 힌트는 모델에게 어떤 실행 계약을 노출할까요?
- `bind_tools()` 이후에도 애플리케이션이 직접 책임져야 할 루프는 무엇일까요?
- 도구 사용 성공률을 운에 맡기지 않고 높이려면 무엇을 신경 써야 할까요?
- 어디까지 자동화하고 어디서 멈춰야 안전할까요?

> Tool Calling이 잘 작동하려면, 모델이 직접 일을 하는 척하는 대신 어떤 실제 함수를 호출해야 하는지 판단하도록 만들어야 합니다.

![이 글에서 답할 질문](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*

## 최소 실행 예제

```python
import os

from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
response = llm.bind_tools([add_numbers]).invoke("Add 13 and 29.")
print(response.tool_calls)
```

<!-- injected-output:start -->
**Output**

    [{'name': 'add_numbers', 'args': {'a': 13, 'b': 29}, 'id': '0r7b2zrqg', 'type': 'tool_call'}]

<!-- injected-output:end -->

이 결과를 보면 핵심이 분명합니다. 모델은 `42`를 바로 출력한 것이 아니라, `add_numbers(a=13, b=29)`를 호출하겠다는 구조화된 요청을 보냈습니다. **도구 메타데이터를 보고 함수 호출 계획을 세운 것**이지, 함수를 실제로 실행한 것이 아닙니다.

## 전체 흐름 한눈에 보기

![전체 흐름 한눈에 보기](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-02-the-flow-at-a-glance.ko.png)

*전체 흐름 한눈에 보기*

LLM은 텍스트 생성기입니다. 계산, 날씨 조회, DB 질의, 외부 시스템 호출 같은 일은 외부 도구가 해야 합니다. Tool Calling은 모델이 "이 도구를 이런 인자로 호출해 달라"고 요청하고, 애플리케이션이 그 도구를 실행한 뒤 결과를 다시 대화에 붙여 최종 답변을 완성하는 패턴입니다.

이 글에서는 다음 순서로 살펴보겠습니다.

- `@tool`로 도구 정의하기
- `bind_tools()`로 모델에 연결하기
- 최소한의 tool-call loop 만들기
- 여러 도구를 섞은 예제
- 안전성과 품질을 위해 무엇을 봐야 하는지

---

## 도구 정의하기

![함수 정의가 도구 메타데이터로 바뀌는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-01-defining-tools.ko.png)

*함수 정의가 도구 메타데이터로 바뀌는 흐름*

`@tool` 데코레이터는 Python 함수를 LangChain 도구로 바꿉니다. 여기서 모델이 읽는 것은 주로 두 가지입니다. **docstring은 이 도구가 언제 필요한지 설명하고, type hint는 어떤 인자를 받아야 하는지 정의합니다.**

```python
from langchain_core.tools import tool

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers. Use this when addition is needed."""
    return a + b

@tool
def get_word_count(text: str) -> int:
    """Return the word count of a text string."""
    return len(text.split())

@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32

print(f"name: {add_numbers.name}")
print(f"description: {add_numbers.description}")
print(f"schema: {add_numbers.args_schema.model_json_schema()}")
```

운영 관점에서 여기서 가장 중요한 것은 설명 품질입니다. 도구 이름이 멋있느냐보다, **모델이 언제 이 도구를 써야 하는지 헷갈리지 않게 만드는 것**이 훨씬 중요합니다. 설명이 겹치면 잘못된 도구 선택이 늘고, 설명이 빈약하면 모델이 도구를 아예 쓰지 않기도 합니다.

---

## bind_tools()로 연결하기

![도구 메타데이터를 모델에 바인딩하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-02-connecting-tools-with-bind-tools.ko.png)

*도구 메타데이터를 모델에 바인딩하는 흐름*

`bind_tools()`는 모델에게 현재 사용할 수 있는 도구 목록을 알려 줍니다. 즉, 어떤 함수 이름이 있고 어떤 인자를 받는지 모델이 알게 됩니다.

```python
import os

from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

tools = [add_numbers, multiply_numbers]

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

llm_with_tools = llm.bind_tools(tools)

response = llm_with_tools.invoke("What is 15 plus 27?")

print(f"content: {response.content!r}")
print(f"tool_calls: {response.tool_calls}")
```

<!-- injected-output:start -->
**Output**

    content: ''
    tool_calls: [{'name': 'add_numbers', 'args': {'a': 15, 'b': 27}, 'id': 'yc5j64vch', 'type': 'tool_call'}]

<!-- injected-output:end -->

여기서 `content`가 비어 있는 것은 이상한 일이 아닙니다. 아직 최종 답변을 한 것이 아니라, 먼저 도구를 호출해야 하기 때문입니다. Tool Calling에서는 **빈 텍스트와 도구 호출 요청이 정상적인 중간 상태**라는 점을 기억해야 합니다.

---

## 최소 tool-call loop

![도구 요청 실행 후 다시 주입하는 루프](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-03-a-minimal-tool-call-loop.ko.png)

*도구 요청 실행 후 다시 주입하는 루프*

모델이 도구 호출을 요청하면, 애플리케이션은 해당 함수를 실행하고 결과를 `ToolMessage`로 돌려줘야 합니다. 이 재주입이 있어야 모델은 중간 결과를 보고 최종 답을 계속 생성할 수 있습니다.

```python
import os

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers. Use this for arithmetic addition."""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers. Use this for arithmetic multiplication."""
    return a * b

tools = [add_numbers, multiply_numbers]
tool_map = {tool.name: tool for tool in tools}

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = (
    "You must use the provided arithmetic tools for addition and multiplication. "
    "Do not answer from memory when a tool is appropriate. "
    "After tool results arrive, produce one short final answer."
)

def run_with_tools(question: str) -> str:
    """Simple tool-call loop with explicit tool-use instructions."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            result = tool_map[tool_name].invoke(tool_args)
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id,
                )
            )
            print(f"  executed: {tool_name}({tool_args}) = {result}")

questions = [
    "What is 15 plus 27?",
    "What is 7 times 8?",
    "Add 5 and 3, then multiply the result by 4. What do you get?",
]

for q in questions:
    print(f"\nquestion: {q}")
    answer = run_with_tools(q)
    print(f"answer: {answer}")
```

<!-- injected-output:start -->
**Output**

    question: What is 15 plus 27?
      executed: add_numbers({'a': 15, 'b': 27}) = 42.0
    answer: 15 plus 27 is 42.

    question: What is 7 times 8?
      executed: multiply_numbers({'a': 7, 'b': 8}) = 56.0
    answer: 7 times 8 is 56.

    question: Add 5 and 3, then multiply the result by 4. What do you get?
      executed: add_numbers({'a': 5, 'b': 3}) = 8.0
      executed: multiply_numbers({'a': 8, 'b': 4}) = 32.0
    answer: Add 5 and 3 to get 8, then multiply by 4 to get 32.

<!-- injected-output:end -->

이 루프를 보면 Tool Calling의 책임 분리가 또렷해집니다. 특히 system 메시지로 “산수는 반드시 도구를 쓰라”는 기준을 명시했기 때문에, 두 번째 질문처럼 단순 계산도 텍스트 생성으로 얼버무리지 않고 실제 tool call로 이어집니다.

- 모델: 어떤 도구를 어떤 인자로 호출할지 결정
- 애플리케이션: 실제 함수 실행
- `ToolMessage`: 실행 결과를 다시 대화 흐름에 연결

운영 관점에서는 여기서 로깅이 매우 중요합니다. 어떤 질문에서 어떤 도구가 몇 번 호출됐는지 남겨 두지 않으면, 잘못된 도구 선택과 반복 루프를 나중에 추적하기 어렵습니다.

---

## 실패 모드를 먼저 막는 dispatcher

실전에서는 “도구가 정상적으로 호출되는 happy path”만 보면 부족합니다. unknown tool, 잘못된 인자, 도구 내부 예외를 같은 방식으로 다뤄야 나중에 루프가 무너지지 않습니다.

```python
from langchain_core.messages import ToolMessage

def execute_tool_call(tool_call: dict) -> ToolMessage:
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_id = tool_call["id"]

    if tool_name not in tool_map:
        return ToolMessage(
            content=f"ERROR: unknown tool '{tool_name}'",
            tool_call_id=tool_id,
        )

    try:
        result = tool_map[tool_name].invoke(tool_args)
        return ToolMessage(content=str(result), tool_call_id=tool_id)
    except Exception as exc:
        return ToolMessage(
            content=f"ERROR: {type(exc).__name__}: {exc}",
            tool_call_id=tool_id,
        )

ok_call = {"name": "add_numbers", "args": {"a": 10, "b": 5}, "id": "call_ok"}
bad_call = {"name": "divide_numbers", "args": {"a": 10, "b": 5}, "id": "call_bad"}

print(execute_tool_call(ok_call).content)
print(execute_tool_call(bad_call).content)
```

<!-- injected-output:start -->
**Output**

    15.0
    ERROR: unknown tool 'divide_numbers'

<!-- injected-output:end -->

이 작은 dispatcher 하나만 있어도 장애 분석이 쉬워집니다. 모델이 잘못된 이름을 골랐는지, 인자가 틀렸는지, 도구 안에서 예외가 터졌는지 로그 한 줄로 바로 구분할 수 있기 때문입니다.

---

## 여러 도구를 섞는 예제

실전 애플리케이션은 산수 도구 하나로 끝나지 않습니다. 조회, 계산, 텍스트 처리처럼 성격이 다른 도구가 함께 들어갑니다. 여기서는 결과가 매번 달라지는 현재 시각 대신, 검증하기 쉬운 정적 조회 도구를 섞어 보겠습니다.

```python
import os

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def get_office_hours(team: str) -> str:
    """Return office hours for a named team."""
    hours = {
        "support": "09:00-18:00 KST",
        "ml-platform": "10:00-19:00 KST",
    }
    return hours[team]

@tool
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI from weight in kg and height in meters."""
    return round(weight_kg / (height_m ** 2), 2)

@tool
def word_frequency(text: str, word: str) -> int:
    """Count how many times a word appears in a text."""
    return text.lower().split().count(word.lower())

tools = [get_office_hours, calculate_bmi, word_frequency]
tool_map = {t.name: t for t in tools}

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools)

def run_with_tools(question: str) -> str:
    messages = [HumanMessage(content=question)]
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for tc in response.tool_calls:
            result = tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            print(f"  {tc['name']}({tc['args']}) = {result}")

print(run_with_tools("When is the support team available?"))
print(run_with_tools("What is the BMI for someone weighing 70 kg at 1.75 m?"))
print(run_with_tools("How many times does 'vector' appear in 'vector search makes vector retrieval practical'?"))
```

<!-- injected-output:start -->
**Output**

      get_office_hours({'team': 'support'}) = 09:00-18:00 KST
    The support team is available from 09:00 to 18:00 KST.
      calculate_bmi({'height_m': 1.75, 'weight_kg': 70}) = 22.86
    The BMI for someone weighing 70 kg at 1.75 m is 22.86.
      word_frequency({'text': 'vector search makes vector retrieval practical', 'word': 'vector'}) = 2
    The word 'vector' appears 2 times.

<!-- injected-output:end -->

이 예제는 서로 다른 종류의 도구가 같은 loop 안에서 어떻게 다뤄지는지 보여 줍니다. 동시에 검증 포인트도 분명합니다. 실행 로그 한 줄만 봐도 어떤 질문이 어떤 도구로 라우팅됐는지, 인자가 어떻게 채워졌는지, 최종 답변이 도구 결과를 제대로 반영했는지 바로 확인할 수 있습니다.

---

## 주의할 점

![잘못된 도구 요청을 막는 가드레일](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-04-what-to-watch-out-for.ko.png)

*잘못된 도구 요청을 막는 가드레일*

**Docstring이 도구 선택을 좌우합니다.** 모델은 docstring을 읽고 어떤 도구를 언제 써야 하는지 판단합니다. 설명이 겹치거나 모호하면 틀린 도구를 고르기 쉽습니다.

**도구 안에서 입력 검증이 필요합니다.** 타입 힌트는 스키마를 정의하지만, 런타임에 잘못된 값이 들어오는 것까지 막아 주지는 않습니다. 부작용이 있는 도구라면 더더욱 실제 실행 전에 검증해야 합니다.

**무한 루프 방지가 필요합니다.** 종료 조건이 명확하지 않은 도구 루프는 최대 반복 수를 두는 것이 안전합니다.

```python
MAX_ITERATIONS = 10

def run_with_tools_safe(question: str) -> str:
    messages = [HumanMessage(content=question)]
    for _ in range(MAX_ITERATIONS):
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for tc in response.tool_calls:
            result = tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    return "Max iterations reached."
```

실무에서는 여기에 더해 권한 분리, allowlist, 타임아웃, 감사 로그를 붙입니다. 특히 외부 시스템을 변경하는 도구라면 "모델이 요청했다"는 이유만으로 실행해 버리면 안 됩니다. 먼저 read-only 도구로 loop를 안정화하고, 그다음 쓰기 권한이 있는 도구를 아주 제한적으로 여는 순서가 안전합니다.

---

## 이 코드에서 주목할 점

- `@tool`의 docstring과 타입 힌트는 모델이 보는 설명과 인자 스키마가 됩니다.
- `bind_tools()`는 에이전트를 만들어 주는 것이 아니라, 모델이 도구 호출 요청을 만들 수 있게 메타데이터를 붙입니다.
- 응답에 `tool_calls`가 나타나면 애플리케이션이 함수를 실행하고, 그 결과를 `ToolMessage`로 다시 넣어야 reasoning loop가 이어집니다.
- dispatcher를 두면 unknown tool, runtime exception, 정상 결과를 같은 메시지 형태로 돌려보낼 수 있습니다.
- 여러 도구 예제가 중요한 이유는 요청 → 실행 → 재주입 루프를 더 분명하게 보여 주기 때문입니다.

## 엔지니어가 자주 헷갈리는 지점

- Tool Calling을 모델 측 실행으로 오해하기 쉽지만, 실제 함수 호출은 항상 애플리케이션이 담당합니다.
- 애매한 도구 설명은 잘못된 도구 선택이나 malformed argument를 부릅니다.
- 반복 상한은 선택 사항이 아닙니다. 잘못된 루프는 계속 잘못된 호출을 재생성할 수 있습니다.

## 체크리스트

- [ ] `@tool`, `bind_tools()`, `ToolMessage`의 역할을 설명할 수 있다
- [ ] 모델이 도구를 요청한 뒤 어떤 순서가 이어지는지 말할 수 있다
- [ ] tool loop에 명시적 종료 조건이 필요한 이유를 이해했다

## 정리

Tool Calling 루프는 세 부분으로 이루어집니다. `@tool`로 도구를 정의하고, `bind_tools()`로 모델에 연결하고, 실행 결과를 `ToolMessage`로 다시 대화에 넣는 것입니다. 루프는 모델이 더 이상 도구를 요청하지 않을 때까지 이어집니다.

다음 글에서는 Streaming으로 넘어가, 같은 체인을 유지한 채 결과를 토큰 단위로 즉시 사용자에게 보여 주는 방식을 살펴보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangChain 소개 — LCEL과 Runnable 기본](./01-lcel-runnable-basics.md)
- [Prompt와 LLM Chain — 체인 첫 번째 구성](./02-prompt-llm-chain.md)
- [Retriever — 문서 검색과 컨텍스트 주입](./03-retriever.md)
- **Tool Calling — 외부 도구 연결하기 (현재 글)**
- Streaming — 실시간 출력 처리 (예정)
- 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain tool calling guide](https://python.langchain.com/docs/how_to/tool_calling/)
- [Defining custom tools](https://python.langchain.com/docs/how_to/custom_tools/)
- [ToolMessage and message types](https://python.langchain.com/docs/concepts/messages/)
- [Groq tool use](https://console.groq.com/docs/tool-use)

### 관련 시리즈

- [LangGraph 101](../../langgraph-101/ko/01-graph-basics.md) — tool loop가 길어지고 분기와 상태가 필요해질 때는 단일 while 루프보다 그래프 기반 제어가 더 읽기 쉬워집니다.

Tags: LangChain, LCEL, Python, LLM
