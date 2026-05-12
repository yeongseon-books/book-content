---
title: 첫 Agent 만들기
series: ai-agent-101
episode: 10
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Tutorial
- Python
- Hands-on
last_reviewed: '2026-05-02'
seo_description: 이제 배운 내용을 종합해서 실제 Agent를 만들어 봅니다. 이번 글에서는 간단하면서도 실용적인 Agent를 처음부터
  끝까지 구현합니다.
---

# 첫 Agent 만들기

> AI Agent 101 시리즈 (10/10)

이제 배운 내용을 종합해서 실제 Agent를 만들어 봅니다. 이번 글에서는 간단하면서도 실용적인 Agent를 처음부터 끝까지 구현합니다. 컨텍스트 설정, 도구 정의, Workflow 구성, 에러 처리, 테스트까지 전 과정을 다룹니다. 이 글은 AI Agent 101 시리즈의 마지막 글입니다.

추천 프레임워크는 LangGraph와 Crew AI입니다. 두 프레임워크 모두 Agent 구축을 단순화하지만, 접근 방식이 다릅니다. LangGraph는 그래프 기반 Workflow에 강하고, Crew AI는 Multi-Agent 협업에 강합니다.

이번 글에서는 엔드투엔드 구현 예제, LangGraph와 Crew AI 비교, 배포 방법, 그리고 다음 단계 학습 경로를 다룹니다.

---

## 만들 Agent: Research Assistant

이번 글에서는 간단한 리서치 어시스턴트 Agent를 처음부터 끝까지 만들어 봅니다. 이 Agent는 사용자가 질문을 던지면 다음 단계를 거칩니다.

1. 질문을 분석하고 필요한 정보를 파악합니다.
2. 검색 도구를 사용해서 관련 자료를 수집합니다.
3. 계산이 필요하면 계산 도구를 호출합니다.
4. 수집한 정보를 종합해서 답변을 생성합니다.
5. 대화 히스토리를 유지해서 후속 질문에 대응합니다.

이 예제는 작지만 1편부터 9편까지 다룬 모든 개념을 한곳에 모읍니다. 컨텍스트 설정, 도구 정의, Workflow 설계, 메모리, 에러 처리, 평가, 운영까지 모두 포함합니다.

---

## 사전 준비

필요한 패키지를 설치합니다.

```bash
pip install openai pydantic python-dotenv
```

`.env` 파일에 API 키를 저장합니다.

```bash
OPENAI_API_KEY=sk-...
```

전체 코드는 단일 파일 `agent.py`로 작성합니다. 학습 목적이므로 외부 프레임워크 없이 표준 라이브러리와 OpenAI SDK만 사용합니다. 프레임워크 도입은 마지막 섹션에서 다룹니다.

---

## Step 1: 도구 정의

도구는 Agent가 호출할 수 있는 외부 함수입니다. 각 도구는 명확한 입력 스키마와 결정적인 동작이 있어야 합니다.

```python
from typing import Any
from pydantic import BaseModel, Field
import json

class SearchInput(BaseModel):
    """검색 도구 입력 스키마."""
    query: str = Field(..., description="검색어")
    top_k: int = Field(3, description="반환할 결과 수")

class CalculatorInput(BaseModel):
    """계산 도구 입력 스키마."""
    expression: str = Field(..., description="Python 산술식")

def tool_search(query: str, top_k: int = 3) -> list[dict[str, str]]:
    """가짜 검색 도구. 실제로는 외부 API를 호출합니다."""
    fake_db = [
        {"title": "FastAPI 공식 문서", "snippet": "FastAPI는 현대적이고 빠른 Python 웹 프레임워크입니다."},
        {"title": "FastAPI 성능 벤치마크", "snippet": "FastAPI는 Node.js와 Go에 견줄 만한 성능을 제공합니다."},
        {"title": "FastAPI vs Flask", "snippet": "FastAPI는 비동기 지원과 자동 문서화에서 Flask보다 우위입니다."},
    ]
    return fake_db[:top_k]

def tool_calculator(expression: str) -> float:
    """안전한 산술 계산. eval은 위험하므로 제한된 환경을 사용합니다."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError(f"허용되지 않은 문자가 포함되어 있습니다: {expression}")
    return eval(expression, {"__builtins__": {}}, {})
```

도구 등록 테이블을 만듭니다. Agent는 이 테이블을 보고 어떤 도구를 호출할지 결정합니다.

```python
TOOLS = {
    "search": {
        "function": tool_search,
        "schema": SearchInput,
        "description": "키워드로 자료를 검색합니다.",
    },
    "calculator": {
        "function": tool_calculator,
        "schema": CalculatorInput,
        "description": "산술식을 계산합니다.",
    },
}

def tools_to_openai_format() -> list[dict[str, Any]]:
    """OpenAI Function Calling 형식으로 변환합니다."""
    result = []
    for name, info in TOOLS.items():
        result.append({
            "type": "function",
            "function": {
                "name": name,
                "description": info["description"],
                "parameters": info["schema"].model_json_schema(),
            },
        })
    return result
```

---

## Step 2: 메모리 구현

대화 히스토리를 저장하는 단순한 메모리 클래스입니다. 5편에서 다룬 슬라이딩 윈도우 패턴을 적용합니다.

```python
class ConversationMemory:
    """슬라이딩 윈도우 대화 메모리."""

    def __init__(self, system_prompt: str, max_messages: int = 20):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.messages: list[dict[str, Any]] = []

    def add(self, role: str, content: str, **extra: Any) -> None:
        """메시지를 추가합니다."""
        msg = {"role": role, "content": content, **extra}
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def to_openai(self) -> list[dict[str, Any]]:
        """OpenAI Chat Completions 형식으로 반환합니다."""
        return [{"role": "system", "content": self.system_prompt}] + self.messages
```

`max_messages`로 컨텍스트 길이를 제한합니다. 토큰 기반 압축은 5편을 참고하세요.

---

## Step 3: Agent 루프

Agent의 핵심은 LLM과 도구 사이의 루프입니다. LLM이 도구를 호출하면 결과를 다시 LLM에 전달하고, 더 이상 호출이 없으면 최종 답변을 반환합니다.

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """당신은 리서치 어시스턴트입니다.
사용자 질문에 답하기 위해 search와 calculator 도구를 사용할 수 있습니다.
도구 결과를 종합해서 정확하고 간결한 답변을 제공하세요.
모르는 것은 모른다고 답하세요."""

class ResearchAgent:
    """리서치 어시스턴트 Agent."""

    def __init__(self, model: str = "gpt-4o-mini", max_iterations: int = 5):
        self.model = model
        self.max_iterations = max_iterations
        self.memory = ConversationMemory(SYSTEM_PROMPT)

    def run(self, user_input: str) -> str:
        """사용자 질문을 처리하고 답변을 반환합니다."""
        self.memory.add("user", user_input)

        for iteration in range(self.max_iterations):
            response = client.chat.completions.create(
                model=self.model,
                messages=self.memory.to_openai(),
                tools=tools_to_openai_format(),
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                self.memory.add("assistant", msg.content or "")
                return msg.content or ""

            self.memory.add(
                "assistant",
                msg.content or "",
                tool_calls=[tc.model_dump() for tc in msg.tool_calls],
            )

            for tool_call in msg.tool_calls:
                result = self._execute_tool(tool_call)
                self.memory.add(
                    "tool",
                    json.dumps(result, ensure_ascii=False),
                    tool_call_id=tool_call.id,
                )

        return "최대 반복 횟수에 도달했습니다. 답변을 생성하지 못했습니다."

    def _execute_tool(self, tool_call: Any) -> Any:
        """도구를 안전하게 실행합니다."""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
            tool = TOOLS.get(name)
            if not tool:
                return {"error": f"알 수 없는 도구: {name}"}
            validated = tool["schema"](**args)
            result = tool["function"](**validated.model_dump())
            return {"result": result}
        except Exception as exc:
            return {"error": str(exc)}
```

핵심 포인트는 다음과 같습니다.

- `max_iterations`로 무한 루프를 방지합니다.
- 도구 실행은 `_execute_tool`로 격리해서 예외를 잡습니다.
- 입력 스키마는 Pydantic으로 검증합니다.
- 도구 응답도 메시지 히스토리에 추가합니다.

---

## Step 4: 실행과 테스트

간단한 CLI로 Agent를 실행해 봅니다.

```python
if __name__ == "__main__":
    agent = ResearchAgent()
    print("Research Assistant. 종료하려면 'quit'를 입력하세요.")
    while True:
        user_input = input("\n질문: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        try:
            answer = agent.run(user_input)
            print(f"\n답변: {answer}")
        except Exception as exc:
            print(f"\n[에러] {exc}")
```

실행 예시입니다.

```text
질문: FastAPI 성능은 어떤가요?
답변: FastAPI는 Node.js와 Go에 견줄 만한 성능을 제공하는 현대적인 Python 웹 프레임워크입니다.
검색 결과에 따르면 비동기 지원과 자동 문서화에서 Flask보다 우위에 있습니다.

질문: 요청 1000개를 0.5초씩 처리하면 총 몇 초인가요?
답변: 1000 * 0.5 = 500초 입니다.
```

후속 질문에서 컨텍스트가 유지되는지도 확인해 봅니다.

```text
질문: 그럼 동시에 100개씩 처리하면요?
답변: 1000개를 동시에 100개씩 처리하면 10배 빠릅니다. 즉 50초가 걸립니다.
```

---

## Step 5: 자동화 평가

7편에서 다룬 평가 프레임워크를 적용합니다. 작은 골드 데이터셋을 만들고 회귀를 감지합니다.

```python
GOLD_CASES = [
    {
        "input": "FastAPI는 어떤 프레임워크인가요?",
        "must_contain": ["Python", "웹"],
    },
    {
        "input": "100 더하기 200은?",
        "must_contain": ["300"],
    },
]

def run_eval() -> dict[str, Any]:
    """골드 데이터셋으로 평가를 실행합니다."""
    passed = 0
    failures = []
    for case in GOLD_CASES:
        agent = ResearchAgent()
        answer = agent.run(case["input"])
        if all(kw in answer for kw in case["must_contain"]):
            passed += 1
        else:
            failures.append({"input": case["input"], "answer": answer})
    return {
        "total": len(GOLD_CASES),
        "passed": passed,
        "pass_rate": passed / len(GOLD_CASES),
        "failures": failures,
    }

if __name__ == "__main__" and os.getenv("RUN_EVAL"):
    result = run_eval()
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

`RUN_EVAL=1 python agent.py`로 실행하면 평가 결과를 확인할 수 있습니다. 키워드 매칭은 단순하지만 회귀 감지에 충분합니다. LLM-as-Judge 평가는 7편을 참고하세요.

---

## 프레임워크 비교: 직접 구현 vs LangGraph vs CrewAI

위 예제는 직접 구현한 버전입니다. 실제 프로덕션에서는 검증된 프레임워크를 쓰는 것이 좋습니다. 대표적으로 LangGraph와 CrewAI가 있습니다.

| 항목 | 직접 구현 | LangGraph | CrewAI |
| --- | --- | --- | --- |
| 학습 곡선 | 낮음 | 중간 | 낮음 |
| 유연성 | 매우 높음 | 매우 높음 | 중간 |
| Multi-Agent | 직접 작성 | 직접 설계 | 빌트인 |
| 그래프 시각화 | 없음 | 있음 | 제한적 |
| Streaming | 직접 구현 | 빌트인 | 빌트인 |
| 체크포인트 | 직접 구현 | 빌트인 | 제한적 |
| 적합 사례 | 학습, 단순 Agent | 복잡한 Workflow | Role 기반 협업 |

LangGraph 예시는 다음과 같습니다.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    iterations: int

def call_model(state: AgentState) -> AgentState:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=state["messages"],
        tools=tools_to_openai_format(),
    )
    msg = response.choices[0].message
    state["messages"].append(msg.model_dump())
    state["iterations"] += 1
    return state

def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if not last.get("tool_calls") or state["iterations"] >= 5:
        return END
    return "tools"

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", execute_tools_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
app = graph.compile()
```

LangGraph는 노드와 엣지로 Workflow를 표현합니다. 복잡한 분기와 루프를 명시적으로 다룰 수 있습니다.

CrewAI 예시는 다음과 같습니다.

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="주제에 대한 자료를 수집한다",
    backstory="당신은 꼼꼼한 리서처입니다.",
    tools=[search_tool],
)

writer = Agent(
    role="Writer",
    goal="수집한 자료로 답변을 작성한다",
    backstory="당신은 명확하게 쓰는 작가입니다.",
)

task1 = Task(description="FastAPI에 대해 조사한다", agent=researcher)
task2 = Task(description="조사 내용을 요약한다", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
result = crew.kickoff()
```

CrewAI는 Role 기반 Multi-Agent 협업에 강합니다. Agent마다 역할과 목표를 부여하고 Task를 할당합니다.

선택 가이드입니다.

- 간단한 단일 Agent 학습 단계: 직접 구현
- 복잡한 Workflow와 분기, 체크포인트가 필요: LangGraph
- 여러 Agent가 역할을 나눠 협업하는 시나리오: CrewAI

---

## 배포 준비

학습용 코드를 프로덕션으로 옮기려면 몇 가지가 더 필요합니다.

### FastAPI 래퍼

CLI 대신 HTTP 엔드포인트로 노출합니다.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    message: str

SESSIONS: dict[str, ResearchAgent] = {}

@app.post("/chat")
def chat(req: ChatRequest) -> dict[str, str]:
    agent = SESSIONS.setdefault(req.session_id, ResearchAgent())
    try:
        answer = agent.run(req.message)
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(500, detail=str(exc))
```

세션별로 Agent 인스턴스를 분리해서 대화를 격리합니다. 실제 서비스에서는 Redis나 DB로 메모리를 외부화합니다.

### 환경 변수와 시크릿

API 키는 코드에 절대 하드코딩하지 않습니다. `.env` 파일은 `.gitignore`에 포함하고, 운영에서는 Secret Manager(Vault, AWS Secrets Manager 등)를 사용합니다.

### 컨테이너 이미지

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이미지 크기를 줄이려면 multi-stage build를 사용합니다. 9편의 운영 체크리스트도 함께 적용합니다.

---

## 흔한 실수

**1. 무한 루프 방지를 잊는다.**
LLM이 같은 도구를 반복 호출하는 사례가 있습니다. `max_iterations`는 반드시 설정합니다.

**2. 도구 실행에서 예외를 잡지 않는다.**
도구 하나가 실패하면 전체 Agent가 죽습니다. 모든 도구 실행은 `try/except`로 감쌉니다.

**3. 시스템 프롬프트를 매 호출마다 새로 만든다.**
시스템 프롬프트는 한 번만 정의하고 메모리에서 관리합니다. 매 호출마다 다시 작성하면 일관성이 깨집니다.

**4. 평가 없이 프롬프트를 수정한다.**
프롬프트를 바꾸면 회귀가 생길 수 있습니다. 작은 골드 데이터셋이라도 만들고 평가를 자동화하세요.

**5. 프레임워크부터 도입한다.**
LangGraph나 CrewAI는 강력하지만 학습 비용이 있습니다. 먼저 직접 구현해서 동작 원리를 이해한 다음 프레임워크로 옮기는 것이 좋습니다.

---

## 다음 단계

이번 시리즈를 마쳤다면 다음 학습 경로를 추천합니다.

1. **RAG 통합**: 사내 문서를 검색하는 RAG Agent를 만들어 봅니다. `vector-search-101`과 `rag-deep-dive` 시리즈를 참고하세요.
2. **함수 호출 고도화**: OpenAI 외에 Anthropic, Gemini 등 멀티 모델 지원을 추가합니다.
3. **장기 메모리**: 대화를 요약해서 벡터 DB에 저장하고 후속 세션에서 검색합니다.
4. **Multi-Agent 시스템**: 6편에서 다룬 Coordinator-Worker 패턴으로 확장합니다.
5. **프로덕션 운영**: 9편의 Observability와 비용 추적을 실제로 적용합니다.

이 시리즈는 Agent 개발의 출발점입니다. 작은 Agent부터 시작해서 점진적으로 복잡도를 높여 나가세요. 모든 Agent는 결국 같은 패턴을 따릅니다. 도구를 정의하고, 컨텍스트를 관리하고, 루프를 안정화하고, 평가를 자동화하는 일입니다.

---

## 핵심 요약

- 직접 Agent를 만들면 LLM-도구 루프, 메모리, 에러 처리의 동작 원리를 깊이 이해할 수 있습니다.
- `max_iterations`와 `try/except`는 모든 Agent 루프의 필수 안전장치입니다.
- 도구는 Pydantic 스키마로 입력을 검증하고 결정적으로 동작해야 합니다.
- 평가 자동화는 작은 골드 데이터셋만으로도 충분히 시작할 수 있습니다.
- 직접 구현으로 원리를 익힌 다음 LangGraph나 CrewAI 같은 프레임워크로 확장하세요.

<!-- a-grade-example:begin -->

## 체크리스트

- [ ] Research Assistant의 입력·출력·범위를 한 단락으로 적었다.
- [ ] 도구 → 메모리 → 루프 순서로 직접 코드를 짜 보았다.
- [ ] 직접 구현 vs LangGraph vs CrewAI 비교 표를 만들었다.
- [ ] Step 5의 자동 평가 루프를 1회 이상 실행해 결과를 봤다.

<!-- a-grade-example:end -->

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- [Agent Workflow 설계](./04-agent-workflow-design.md)
- [Memory와 State](./05-memory-and-state.md)
- [Multi-Agent 시스템](./06-multi-agent-systems.md)
- [Agent 평가](./07-agent-evaluation.md)
- [에러 처리와 안정성](./08-error-handling-reliability.md)
- [운영](./09-production-operations.md)
- **첫 Agent 만들기 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Building Effective Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)

Tags: AI Agent, LLM, Tool Use, Python
