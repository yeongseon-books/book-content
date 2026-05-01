---
title: 'LangGraph 완성'
series: langgraph-101
episode: 6
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

# LangGraph 완성

## 이 글에서 답할 질문

- 체크포인트, 조건 분기, 도구 호출을 한 그래프에 어떻게 합칠까요?
- 어떤 질문은 직접 답하고 어떤 질문은 도구 루프로 보내려면 구조를 어떻게 짜야 할까요?
- 완성형 예제를 검증할 때 무엇을 확인해야 할까요?

> 완성형 LangGraph 에이전트는 하나의 거대한 프롬프트가 아니라 supervisor, tool agent, checkpoint가 함께 상태 전이를 관리하는 시스템입니다.

예제 코드: [github.com/yeongseon-books/langgraph-101](https://github.com/yeongseon-books/langgraph-101/tree/main/ko/06-langgraph-complete)

이제 시리즈의 조각들을 한 그래프에 모읍니다. 질문을 먼저 분류하고, 단순 설명은 직접 답하고, 계산이나 카운팅은 도구 호출 루프로 보내고, 전체 대화는 `MemorySaver`에 저장합니다. 이 정도 구성만 해도 실제 서비스용 프로토타입의 뼈대가 됩니다.

![이 글에서 답할 질문](../../../assets/langgraph-101/06/06-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

```python
import ast
import json
import math
import operator
from typing import Any, Callable, Literal, cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
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

class CompleteState(MessagesState):
    route: str

def base_llm() -> ChatGroq:
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0, stop_sequences=None)

def supervisor(state: CompleteState) -> dict[str, str]:
    latest_question = str(state["messages"][-1].content).lower()
    if any(keyword in latest_question for keyword in ("count", "calculate", "math", "sqrt")):
        route = "tool_agent"
    else:
        route = "direct_answer"
    return {"route": route}

def route_after_supervisor(state: CompleteState) -> Literal["direct_answer", "tool_agent"]:
    return cast(Literal["direct_answer", "tool_agent"], state["route"])

def direct_answer(state: CompleteState) -> dict[str, object]:
    system = SystemMessage(
        content=(
            "You are explaining LangGraph from the LangChain ecosystem. "
            "Answer clearly using the full conversation history when it matters."
        )
    )
    response = base_llm().invoke([system, *state["messages"]])
    return {"messages": [response]}

def tool_agent(state: CompleteState) -> dict[str, object]:
    system = SystemMessage(
        content=(
            "You are a precise assistant. Use tools for calculations or counting tasks, "
            "then answer in one concise paragraph."
        )
    )
    response = base_llm().bind_tools(TOOLS).invoke([system, *state["messages"]])
    return {"messages": [response]}

def build_graph():
    graph = StateGraph(CompleteState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("direct_answer", direct_answer)
    graph.add_node("tool_agent", tool_agent)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"direct_answer": "direct_answer", "tool_agent": "tool_agent"},
    )
    graph.add_edge("direct_answer", END)
    graph.add_conditional_edges("tool_agent", tools_condition, {"tools": "tools", "__end__": END})
    graph.add_edge("tools", "tool_agent")

    return graph.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    app = build_graph()
    config: RunnableConfig = {"configurable": {"thread_id": "complete-demo"}}

    first = app.invoke(
        {"messages": [HumanMessage(content="Explain what explicit state means in LangGraph.")], "route": ""},
        config=config,
    )
    print("First turn:")
    print(first["messages"][-1].content)

    second = app.invoke(
        {"messages": [HumanMessage(content="Now calculate sqrt(81) + 5 and use a tool.")]},
        config=config,
    )
    print("\nSecond turn:")
    print(second["messages"][-1].content)

    snapshot = app.get_state(config)
    print(f"\nCheckpoint message count: {len(snapshot.values['messages'])}")
```

~~~
출력 결과
First turn:
In the context of LangGraph, a component of the LangChain ecosystem, "explicit state" refers to the idea of making the state of a conversation or application explicit and manageable.

In traditional conversational AI systems, the state of the conversation is often implicit, meaning it's buried within the conversation history or the internal workings of the model. This can make it difficult to manage, debug, and scale the system.

In contrast, LangGraph uses an explicit state approach, where the state of the conversation is represented as a graph data structure. This graph contains nodes and edges that represent the different components of the conversation, such as entities, intents, and context.

By making the state explicit, LangGraph allows developers to:

1. **Visualize** the conversation state: The graph representation provides a clear and visual understanding of the conversation state, making it easier to debug and understand the system.
2. **Manage** the conversation state: The explicit state allows developers to manipulate the conversation state programmatically, enabling more fine-grained control over the system.
3. **Scale** the system: The explicit state approach enables LangGraph to handle complex conversations and scale to larger applications, as the state is no longer buried within the model.

In summary, explicit state in LangGraph refers to the practice of representing the conversation state as a manageable and visual graph data structure, allowing for more control, scalability, and debuggability in conversational AI systems.

Second turn:
The result of the calculation sqrt(81) + 5 is 14.0.

Checkpoint message count: 6
~~~

실행 파일: `/root/Github/langgraph-101/ko/06-langgraph-complete/main.py`

실행:

```bash
export GROQ_API_KEY=... && python main.py
```

## 이 코드에서 봐야 할 것

- supervisor가 먼저 direct path와 tool path를 나눠 그래프 복잡도를 통제합니다.
- `tool_agent -> ToolNode -> tool_agent` 루프가 계산형 질문만 처리합니다.
- `compile(checkpointer=MemorySaver())` 덕분에 멀티턴 대화가 같은 `thread_id`로 이어집니다.

## 실무에서 헷갈리는 지점

- 완성형 예제라고 해서 모든 질문을 도구 루프로 보내면 오히려 느리고 비쌉니다. 먼저 라우팅해서 값비싼 경로를 줄여야 합니다.
- 체크포인터가 있더라도 라우팅 기준은 최신 메시지 중심으로 단순하게 두는 편이 디버깅에 유리합니다.
- ToolNode가 있다고 평가 체계가 자동으로 생기지는 않습니다. 실제 서비스에서는 별도의 테스트 케이스와 회귀 검증이 필요하고, 계산 도구도 raw `eval()` 대신 엄격한 산술 파서를 유지하는 편이 안전합니다.

## 체크리스트

- [ ] direct answer 경로와 tool 경로가 분리되어 있는가
- [ ] 같은 `thread_id`로 재호출했을 때 상태가 이어지는가
- [ ] 도구 질문과 비도구 질문이 기대한 경로로 라우팅되는가
- [ ] 최종 답변 전 루프 종료 조건이 분명한가

## 정리

이 시리즈의 핵심은 LangGraph API를 외우는 것이 아니라 상태, 엣지, 체크포인트를 조합해 흐름을 설계하는 감각을 만드는 데 있습니다. 이제 작은 튜토리얼 그래프를 넘어서 실제 업무용 에이전트 뼈대를 직접 만들 수 있는 단계에 들어왔습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [조건부 엣지와 분기 흐름](./03-conditional-edges.md)
- [도구 호출 에이전트](./04-tool-calling-agent.md)
- [멀티 에이전트 시스템](./05-multi-agent.md)
- **LangGraph 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [LangGraph tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [LangGraph prebuilt components](https://langchain-ai.github.io/langgraph/reference/prebuilt/)

Tags: LangGraph, Agent, Python, LLM
