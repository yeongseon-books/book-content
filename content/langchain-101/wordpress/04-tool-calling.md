---
title: "바이브코딩을 위한 LangChain (4/6): Tool Calling — 외부 도구 연결하기"
series: langchain-101
episode: 4
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangChain
- Tool Calling
- Agent
- Python
---

# 바이브코딩을 위한 LangChain (4/6): Tool Calling — 외부 도구 연결하기

이 글은 **바이브코딩을 위한 LangChain** 시리즈의 네 번째 글입니다. LangChain에서 LLM에게 도구(Tool)를 제공하고 도구 호출 결과를 처리하는 방법을 다룹니다.

---

RAG로 문서 검색을 LLM에 연결했습니다. 이제 계산, 날씨 조회, 데이터베이스 쿼리 같은 외부 기능도 연결하고 싶습니다. Tool Calling은 LLM이 "이 도구를 호출해야겠다"고 판단하면 도구를 실행하고 결과를 다시 LLM에 전달하는 구조입니다.

바이브코딩으로 AI에게 "LangChain으로 Tool Calling 만들어줘"라고 하면 코드가 나옵니다. `@tool` 데코레이터가 무엇을 하는지, 도구 스키마가 LLM에게 어떻게 전달되는지 모르면 새 도구를 추가하거나 오류를 디버깅하기 어렵습니다.

> "Tool Calling은 LLM이 언제 어떤 도구를 쓸지 스스로 결정합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. `@tool` 데코레이터가 함수를 어떻게 변환하나요?
2. docstring이 도구 호출에서 왜 중요한가요?
3. `bind_tools`와 도구를 에이전트에 바인딩하는 차이가 있나요?
4. 도구 호출 결과를 LLM에 다시 전달하는 과정이 어떻게 되나요?
5. 도구 실행 중 오류가 나면 어떻게 처리하나요?

---

## 도구 정의

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """지정한 도시의 현재 날씨를 반환합니다.

    Args:
        city: 날씨를 조회할 도시 이름 (예: 서울, 부산)
    """
    # 실제 구현에서는 날씨 API 호출
    return f"{city}의 현재 날씨: 맑음, 22°C"

@tool
def calculate(expression: str) -> str:
    """수학 식을 계산합니다.

    Args:
        expression: 계산할 수학 식 (예: "2 + 2", "10 * 5")
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"계산 오류: {e}"
```

## LLM에 도구 바인딩

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
tools = [get_weather, calculate]
llm_with_tools = llm.bind_tools(tools)
```

## 도구 호출 실행

```python
from langchain_core.messages import HumanMessage, ToolMessage

def run_tool_loop(question: str) -> str:
    messages = [HumanMessage(content=question)]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # 도구 호출이 없으면 종료
        if not response.tool_calls:
            return response.content

        # 도구 실행
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # 도구 찾아서 실행
            tool_fn = next(t for t in tools if t.name == tool_name)
            result = tool_fn.invoke(tool_args)

            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            ))
```

---

## Before / After

| 항목 | Before (직접 구현) | After (Tool Calling) |
|------|------------------|-----------------------|
| 도구 선택 | 규칙 기반 | LLM이 자동 판단 |
| 도구 추가 | 분기 로직 수정 | @tool 데코레이터 추가 |
| 결과 처리 | 수동 파싱 | ToolMessage 자동 처리 |
| 도구 설명 | 별도 문서 | docstring으로 통합 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| docstring 없음 | LLM이 도구 용도 오해 | 명확한 docstring 필수 |
| Args 타입 힌트 없음 | 스키마 오류 | 파라미터 타입 힌트 명시 |
| tool_call_id 누락 | ToolMessage 연결 오류 | tool_call["id"] 전달 |
| 무한 루프 | 도구 호출 반복 | max_iterations 설정 |

---

## AI 활용 팁

```
@tool 데코레이터로 날씨 조회와 계산 도구를 만들어줘.
각 도구에 Args 타입 힌트와 명확한 docstring을 포함해줘.
llm.bind_tools(tools)로 도구를 바인딩하고, tool_calls가 없을 때까지 루프를 실행해줘.
도구 실행 결과를 ToolMessage로 메시지 리스트에 추가해줘.
```

---

## 체크리스트

- [ ] @tool 데코레이터로 도구 정의
- [ ] 각 도구에 명확한 docstring 작성
- [ ] 파라미터 타입 힌트 명시
- [ ] llm.bind_tools(tools) 바인딩
- [ ] 도구 호출 루프 구현
- [ ] ToolMessage에 tool_call_id 포함

---

## 처음 질문으로 돌아가기

"LLM이 어떻게 어떤 도구를 써야 하는지 아나요?" — `@tool` 데코레이터가 함수의 이름, docstring, 파라미터 타입을 JSON 스키마로 변환합니다. LLM은 이 스키마를 보고 "이 질문에는 이 도구가 맞겠다"고 판단합니다. 좋은 docstring이 좋은 도구 선택을 만듭니다.

---

## 정리

- `@tool` 데코레이터가 함수를 LangChain 도구로 변환한다
- docstring이 LLM의 도구 선택 기준이 되므로 명확하게 작성한다
- `llm.bind_tools(tools)`로 도구 스키마를 LLM에 전달한다
- tool_calls가 없을 때까지 루프를 실행하고 ToolMessage로 결과를 전달한다

---

## 참고 자료

- [LangChain Tool 문서](https://python.langchain.com/docs/concepts/tools/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 도구 정의
- LLM에 도구 바인딩
- 도구 호출 실행
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangChain, Tool Calling, Agent, Python
