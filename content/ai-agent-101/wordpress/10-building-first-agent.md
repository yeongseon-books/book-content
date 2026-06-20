---
title: "바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기"
series: ai-agent-101
episode: 10
language: ko
tags:
- First Agent
- Pydantic
- Tool Registry
- 바이브코딩
- Vibe Coding
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 마지막 글입니다.

---

시리즈의 마지막에 왔습니다. 앞의 9편에서 에이전트의 개념, 컨텍스트 엔지니어링, 도구 사용, 워크플로우 설계, 메모리, 멀티 에이전트, 평가, 오류 처리, 프로덕션 운영을 모두 다뤘습니다. 이제 이 모든 것을 통합해 실제로 동작하는 첫 번째 에이전트를 만들어 봅니다.

바이브코딩에서 "첫 번째 에이전트"는 작게 시작하는 게 핵심입니다. 웹 검색과 계산 두 가지 도구만 가진 연구 에이전트를 만들고, 그것이 실제로 동작하는 것을 확인하는 데 집중합니다. 도구를 더 추가하거나 복잡한 워크플로우를 붙이는 것은 그 다음입니다.

> "완벽한 에이전트보다 동작하는 에이전트가 먼저입니다. 두 도구로 시작하고 검증하세요."

## 이 글에서 다룰 질문

1. 처음부터 완전한 에이전트를 만들려고 하면 어떤 문제가 생기나요?
2. 도구 레지스트리(Tool Registry)를 사용하는 이유는 무엇인가요?
3. Pydantic으로 도구 파라미터를 검증하는 방법은 무엇인가요?
4. 슬라이딩 윈도우 메모리는 어떻게 구현하나요?
5. 에이전트를 처음 배포할 때 가장 중요한 것은 무엇인가요?

---

## 첫 번째 에이전트의 구성 요소

| 구성 요소 | 역할 | 이 글에서의 구현 |
|----------|------|----------------|
| 도구 정의 | 에이전트가 할 수 있는 행동 | 웹 검색 + 계산기 |
| 도구 레지스트리 | 도구 관리와 스키마 자동 생성 | TOOLS 딕셔너리 |
| 메모리 | 대화 히스토리 유지 | 슬라이딩 윈도우 |
| 에이전트 루프 | Observe → Think → Act 반복 | ReAct 패턴 |
| 실행 설정 | 최대 스텝, 예산 한도 | RunConfig |

## Pydantic으로 도구 파라미터 검증

```python
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., description="검색할 질문이나 키워드")
    max_results: int = Field(default=5, ge=1, le=20, description="반환할 결과 수")

class CalculatorInput(BaseModel):
    expression: str = Field(..., description="계산할 수식 (예: '1350 * 88000')")

def tool_search(query: str, max_results: int = 5) -> dict:
    """웹에서 정보를 검색합니다."""
    validated = SearchInput(query=query, max_results=max_results)
    # 실제 검색 API 호출...
    return {"results": [{"title": "...", "url": "...", "snippet": "..."}]}

def tool_calculator(expression: str) -> dict:
    """수식을 계산합니다."""
    validated = CalculatorInput(expression=expression)
    try:
        result = eval(validated.expression, {"__builtins__": {}})
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e), "expression": expression}
```

## 도구 레지스트리와 OpenAI 형식 변환

```python
TOOLS = {
    "search": {
        "function": tool_search,
        "description": "웹에서 최신 정보를 검색합니다. 실시간 데이터나 학습 이후 정보가 필요할 때 사용하세요.",
        "schema": SearchInput
    },
    "calculator": {
        "function": tool_calculator,
        "description": "수학 계산을 수행합니다. 환율 변환, 통계 계산 등에 사용하세요.",
        "schema": CalculatorInput
    }
}

def tools_to_openai_format(tools: dict) -> list[dict]:
    """도구 딕셔너리를 OpenAI Function Calling 형식으로 변환합니다."""
    result = []
    for name, tool_info in tools.items():
        schema = tool_info["schema"].model_json_schema()
        result.append({
            "type": "function",
            "function": {
                "name": name,
                "description": tool_info["description"],
                "parameters": schema
            }
        })
    return result
```

## 슬라이딩 윈도우 메모리

```python
class ConversationMemory:
    def __init__(self, max_messages: int = 20):
        self.messages = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # 시스템 메시지는 보존, 오래된 대화만 제거
        while len(self.messages) > self.max_messages:
            for i, msg in enumerate(self.messages):
                if msg["role"] != "system":
                    self.messages.pop(i)
                    break

    def get_messages(self) -> list[dict]:
        return self.messages.copy()
```

## 연구 에이전트: 전체 구조

```python
from dataclasses import dataclass
from openai import OpenAI
import json

@dataclass
class RunConfig:
    max_steps: int = 10
    max_cost_usd: float = 0.50
    verbose: bool = True

class ResearchAgent:
    def __init__(self, config: RunConfig = None):
        self.client = OpenAI()
        self.config = config or RunConfig()
        self.memory = ConversationMemory()
        self.tools_schema = tools_to_openai_format(TOOLS)
        self.total_cost = 0.0

    def run(self, goal: str) -> str:
        self.memory.add("system", f"""당신은 정보 연구 에이전트입니다.
        목표: {goal}
        도구를 사용해 정확한 정보를 수집하고 종합하세요.
        확인되지 않은 정보는 추측하지 마세요.""")

        self.memory.add("user", goal)

        for step in range(self.config.max_steps):
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.memory.get_messages(),
                tools=self.tools_schema,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # 비용 추적
            tokens = response.usage.total_tokens
            self.total_cost += tokens * 0.00000015  # gpt-4o-mini 단가
            if self.total_cost > self.config.max_cost_usd:
                return f"예산 초과로 중단 (${self.total_cost:.4f})"

            # 도구 호출이 없으면 최종 답변
            if not message.tool_calls:
                return message.content

            # 도구 실행
            self.memory.add("assistant", message.content or "")
            for tool_call in message.tool_calls:
                result = self._execute_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments)
                )
                self.memory.add("tool", json.dumps(result, ensure_ascii=False))

        return "최대 스텝 도달 — 현재까지 수집된 정보로 답변합니다."

    def _execute_tool(self, name: str, args: dict) -> dict:
        if name not in TOOLS:
            return {"error": f"도구 '{name}'를 찾을 수 없습니다"}
        try:
            return TOOLS[name]["function"](**args)
        except Exception as e:
            return {"error": str(e)}
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 처음부터 10개 도구 추가 | 복잡도 증가, 디버깅 어려움 | 2-3개로 시작해 검증 후 추가 |
| 도구 파라미터 검증 없음 | 잘못된 인자로 오류 | Pydantic으로 검증 |
| 비용 추적 없음 | 예상치 못한 청구 | total_cost 실시간 추적 |
| max_steps 없음 | 무한 루프 위험 | RunConfig로 상한 설정 |

## AI 팁

처음 에이전트를 테스트할 때는 `verbose=True`로 모든 단계를 출력하세요. 에이전트가 어떤 도구를 왜 호출하는지, 어떤 결과를 받아 다음 결정을 내리는지 확인할 수 있습니다. 모든 게 예상대로 동작하면 그때 로그를 줄이거나 파일로 리다이렉트하세요.

첫 번째 에이전트를 배포하기 전에 다음 테스트를 반드시 실행하세요:
1. 도구 실패 시 에이전트가 포기하지 않고 대안을 시도하는지
2. max_steps에 도달했을 때 적절한 메시지를 반환하는지
3. 예산 한도를 초과할 때 즉시 중단하는지

## 체크리스트

- [ ] 2-3개 도구로 시작해 동작을 검증했다
- [ ] 모든 도구 파라미터에 Pydantic 검증을 적용했다
- [ ] RunConfig로 max_steps와 max_cost를 설정했다
- [ ] 도구 실패 시 에이전트가 적절히 처리하는지 테스트했다
- [ ] 전체 대화 흐름을 로그로 확인했다

## 처음 질문으로 돌아가기

**처음부터 완전한 에이전트를 만들면?** 복잡도 폭발로 디버깅이 불가능해집니다. 2개 도구로 시작해 동작을 검증한 뒤 하나씩 추가하는 것이 훨씬 효율적입니다.

**도구 레지스트리를 사용하는 이유는?** 도구를 딕셔너리로 관리하면 추가/제거가 쉽고, OpenAI 형식으로 자동 변환할 수 있으며, 코드 중복을 줄입니다.

**Pydantic으로 검증하는 방법은?** 각 도구의 파라미터를 `BaseModel`로 정의하면 입력 검증과 스키마 자동 생성을 동시에 해결할 수 있습니다.

**슬라이딩 윈도우 메모리는?** 시스템 메시지는 보존하고 오래된 대화부터 제거해 컨텍스트 윈도우를 일정 크기 이하로 유지합니다.

**처음 배포할 때 가장 중요한 것은?** max_steps와 max_cost 설정, 그리고 모든 단계를 로깅하는 관측성입니다.

## 정리

이 시리즈를 통해 AI 에이전트의 개념부터 프로덕션 운영까지 바이브코딩 관점에서 살펴봤습니다. 첫 번째 에이전트는 작게 시작하는 것이 핵심입니다. 두 개의 도구, 슬라이딩 윈도우 메모리, 명확한 종료 조건 — 이 세 가지로 시작해 동작하는 것을 확인한 뒤 점진적으로 발전시키세요.

바이브코딩에서 에이전트를 만드는 것은 AI의 능력을 실제 작업에 연결하는 가장 효과적인 방법입니다. 이 시리즈가 그 첫 발걸음에 도움이 되길 바랍니다.

## 참고 자료

- [AI Agent 기초 원문: 첫 번째 에이전트 만들기](../ko/10-building-first-agent.md)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. **바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기 (현재 글)**
<!-- toc:end -->

Tags: First Agent, Pydantic, Tool Registry, 바이브코딩, Vibe Coding
