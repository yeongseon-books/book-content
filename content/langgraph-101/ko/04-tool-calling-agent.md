---
title: '도구 호출 에이전트'
series: langgraph-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangGraph
- Agent
- Python
- LLM
last_reviewed: '2026-05-01'
---

# 도구 호출 에이전트

## 이 글에서 답할 질문

- LangGraph에서 `ToolNode`는 어떤 책임을 맡을까요?
- `ChatGroq.bind_tools()`와 조건부 엣지를 어떻게 연결해야 할까요?
- 도구 호출 루프가 언제 끝나는지 그래프는 어떻게 판단할까요?

> 도구 호출 에이전트는 LLM이 도구 필요 여부를 판단하고, ToolNode가 실행하고, 다시 LLM이 결과를 읽는 루프입니다.

예제 코드: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/ko/04-tool-calling-agent)

에이전트에서 중요한 건 LLM이 똑똑해 보이는지가 아니라 도구 호출 흐름이 명확하게 드러나는지입니다. LangGraph 0.4.5에서는 `ToolNode`와 `tools_condition` 조합으로 이 패턴을 가장 깔끔하게 표현할 수 있습니다.

![이 글에서 답할 질문](../../../assets/langgraph-101/04/04-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

```python
import ast
import json
import math
import operator
from typing import Any, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
ALLOWED_FUNCTIONS: dict[str, Callable[..., Any]] = {
    name: value
    for name, value in math.__dict__.items()
    if not name.startswith("_") and callable(value)
}
ALLOWED_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}

def evaluate_math_expression(expression: str) -> float:
    def _evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp):
            left = _evaluate(node.left)
            right = _evaluate(node.right)
            operation = ALLOWED_BINARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("unsupported operator")
            return float(operation(left, right))
        if isinstance(node, ast.UnaryOp):
            operand = _evaluate(node.operand)
            operation = ALLOWED_UNARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("unsupported unary operator")
            return float(operation(operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function = ALLOWED_FUNCTIONS.get(node.func.id)
            if function is None or node.keywords:
                raise ValueError("unsupported function")
            arguments = [_evaluate(argument) for argument in node.args]
            return float(function(*arguments))
        if isinstance(node, ast.Name):
            value = ALLOWED_CONSTANTS.get(node.id)
            if value is not None:
                return float(value)
            raise ValueError("unsupported constant")
        raise ValueError("unsupported expression")

    parsed = ast.parse(expression, mode="eval")
    return _evaluate(parsed.body)

@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression with safe math functions like sqrt(16) or pi * 2."""

    try:
        result = evaluate_math_expression(expression)
    except Exception as exc:
        return f"calculation error: {exc}"
    return str(result)

@tool
def word_stats(text: str) -> str:
    """Return word and character counts for a piece of text."""

    return json.dumps({"words": len(text.split()), "characters": len(text)})

TOOLS = [calculator, word_stats]

def call_model(state: MessagesState):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, stop_sequences=None).bind_tools(TOOLS)
    system = SystemMessage(
        content="You are a precise assistant. Use tools for calculations or counting tasks."
    )
    response = llm.invoke([system, *state["messages"]])
    return {"messages": [response]}

def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
    graph.add_edge("tools", "agent")
    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    for question in [
        "What is sqrt(144) + 25? Use a tool.",
        "Count the words in this sentence: LangGraph makes tool loops explicit.",
    ]:
        result = app.invoke({"messages": [HumanMessage(content=question)]})
        print(f"Question: {question}")
        print(f"Answer: {result['messages'][-1].content}\n")
```

실행 파일: `/root/Github/langgraph-101/ko/04-tool-calling-agent/main.py`

실행:

```bash
export GROQ_API_KEY=... && python main.py
```

## 이 코드에서 봐야 할 것

- `@tool` docstring이 곧 모델이 읽는 도구 설명입니다.
- `ToolNode(TOOLS)`가 실제 호출과 `ToolMessage` 생성 책임을 가져갑니다.
- `tools_condition`은 마지막 AI 메시지에 tool call이 있으면 `tools`, 없으면 `END`로 보냅니다.

## 실무에서 헷갈리는 지점

- 도구 실행 코드를 직접 루프 안에 쓰기 시작하면 나중에 재시도, 로깅, 테스트가 모두 꼬입니다. `ToolNode`로 분리하는 편이 낫습니다.
- `bind_tools()`만 한다고 그래프가 도구를 자동 실행하지는 않습니다. 실행 노드와 복귀 엣지가 따로 있어야 합니다.
- 계산 도구처럼 결정적이어야 디버깅이 쉽습니다. 계산 도구는 raw `eval()` 대신 엄격한 산술 파서를 유지하는 편이 안전합니다.

## 체크리스트

- [ ] 도구 설명이 입력 형식과 반환 형식을 분명히 말하는가
- [ ] `agent -> tools -> agent` 루프가 코드에 명시돼 있는가
- [ ] 도구를 쓰지 않는 답변은 `END`로 바로 빠지는가

## 정리

여기까지 오면 LangGraph가 단순 오케스트레이션 도구가 아니라 에이전트 런타임처럼 느껴지기 시작합니다. 다음 글에서는 이 패턴을 확장해 감독자와 작업자가 협력하는 멀티 에이전트 그래프로 넘어갑니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- **도구 호출 에이전트 (현재 글)**
- 멀티 에이전트 시스템 (예정)
- LangGraph 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangGraph tool-calling how-to](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [ToolNode API 레퍼런스](https://langchain-ai.github.io/langgraph/reference/prebuilt/#toolnode)
- [LangChain tool docs](https://python.langchain.com/docs/concepts/tools/)

Tags: LangGraph, Agent, Python, LLM
