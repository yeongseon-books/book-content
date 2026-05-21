---
title: "AI Agent 101 (1/10): AI Agent란 무엇인가?"
series: ai-agent-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- LLM
- Tool Use
- Autonomy
- ReAct
- Automation
last_reviewed: '2026-05-12'
seo_description: chatbot과 agent를 가르는 기준과 기본 실행 루프를 정리합니다.
---

# AI Agent 101 (1/10): AI Agent란 무엇인가?

많은 팀이 LLM을 처음 도입할 때 가장 먼저 보는 장면은 채팅창입니다. 질문을 넣으면 대답이 나오고, 말투도 그럴듯하며, 요약과 설명도 빠르게 해냅니다. 여기까지만 보면 LLM은 결국 "똑똑한 답변 엔진"처럼 보입니다.

문제는 실제 업무를 맡기는 순간 시작됩니다. 고객 문의를 분류하고, 검색 결과를 모으고, 필요한 API를 호출하고, 실패 시 다시 시도하고, 마지막으로 작업 결과를 정리해 반환하려면 텍스트 생성만으로는 부족합니다. 시스템은 외부 도구를 호출하고, 중간 결과를 읽고, 다음 행동을 결정해야 합니다.

그래서 현업에서는 chatbot과 agent를 같은 범주로 두지 않습니다. 둘 다 LLM을 쓰더라도 운영 관점에서 보는 추상화 수준이 다르기 때문입니다. chatbot은 응답 품질이 중심이고, agent는 목표 달성 과정 전체가 중심입니다.

이 글은 AI Agent 101 시리즈의 첫 번째 글입니다.

이 글에서는 AI Agent를 "말을 잘하는 모델"이 아니라 "목표를 받고 작업 루프를 실행하는 시스템"으로 이해해 보겠습니다.

## 먼저 던지는 질문

- 챗봇과 agent를 가르는 기준을 기능 이름이 아니라 실행 책임으로 보면 무엇이 달라질까요?
- Observe → Think → Act → Check 루프는 agent 실패를 어디서 나눠 보게 해 줄까요?
- 처음 agent를 설계할 때 tool보다 먼저 정해야 할 경계는 무엇일까요?

## 큰 그림

![agent 루프 한눈에 보기](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/01/01-01-agent-loop-at-a-glance.ko.png)

*agent 루프 한눈에 보기*

이 그림에서는 목표를 받은 agent가 관찰하고, 판단하고, 행동하고, 결과를 확인하는 반복 흐름을 봅니다. 챗봇과 agent의 차이는 답변 품질보다 이 루프를 누가 책임지고 끝내는지에서 갈립니다.

> Agent의 출발점은 더 똑똑한 말투가 아니라, 목표를 향해 반복 실행되는 제어 루프입니다.

## 왜 이 글이 중요한가

AI Agent라는 표현은 이미 너무 넓게 쓰이고 있습니다. 어떤 문맥에서는 단순한 function calling 래퍼도 agent라고 부르고, 어떤 문맥에서는 장기 메모리와 멀티 에이전트 협업까지 들어가야 agent라고 부릅니다. 용어 경계가 흐리면 설계 경계도 같이 흐려집니다.

이 혼선은 제품 설계에서 바로 비용으로 이어집니다. 외부 행동이 필요 없는 작업에 agent 루프를 붙이면 지연 시간과 토큰 비용만 커지고, 반대로 실제로는 다단계 실행이 필요한 업무를 단일 응답 모델로 처리하면 실패를 설명하거나 복구하기 어려워집니다. 즉, agent를 정확히 정의하는 일은 철학이 아니라 아키텍처 결정입니다.

무엇보다 이후 시리즈 전체를 읽기 위한 공통 멘탈 모델이 여기서 정해집니다. context engineering, tool use, workflow, memory, evaluation, operations 모두 결국 "goal을 받고 루프를 어떻게 안전하게 돌릴 것인가"라는 한 문장 위에 쌓입니다.

## 핵심 관점

AI Agent를 가장 안정적으로 이해하는 방법은 agent를 하나의 앱 기능이 아니라 **작업 루프를 가진 실행 시스템**으로 보는 것입니다. 입력이 단순 메시지인지, 목표인지부터 구분해 보면 차이가 선명해집니다. chatbot은 대체로 한 턴 응답에서 끝나지만, agent는 목표를 달성할 때까지 관찰하고 결정하고 실행하고 점검합니다.

이 관점이 중요한 이유는 agent의 실패 모드도 여기서 나오기 때문입니다. 잘못된 도구를 고를 수 있고, 같은 도구를 반복 호출할 수 있고, 중간 결과를 잘못 해석할 수 있고, 이미 실패한 계획을 끝까지 밀어붙일 수 있습니다. 즉, agent는 정답 생성 문제이면서 동시에 제어 흐름 문제입니다.

실무에서는 이 구조를 먼저 받아들인 팀이 더 빨리 안정화합니다. 답변 품질만이 아니라 step 수, tool 선택, retry, stop 조건, state 누수까지 함께 설계하기 때문입니다.

> Agent의 핵심은 "LLM이 똑똑한가"보다 "목표를 향해 관찰·판단·행동·검증을 반복하는 제어 루프를 안전하게 만들었는가"에 있습니다.

## 핵심 개념

### Chatbot과 Agent를 먼저 분리해야 합니다

| 구분 | Chatbot | Agent |
| --- | --- | --- |
| 입력 | 사용자 메시지 | 목표(goal) |
| 출력 | 텍스트 응답 | 작업 완료 또는 산출물 |
| 외부 상호작용 | 거의 없음 | tool 호출, file/API 접근 |
| 반복 | 보통 1턴 | 목표 달성까지 N턴 |
| 상태 | 대화 기록 | 작업 상태 + memory |

기술적으로 agent도 내부에서는 LLM 호출입니다. 하지만 시스템 설계에서는 차이가 큽니다. 사람이 읽고 끝나는 텍스트를 만들면 chatbot에 가깝고, 시스템이 그 출력을 받아 다음 행동을 실행하면 agent에 가까워집니다. 이 차이를 분리해 두면 어떤 기능에 human-in-the-loop가 필요한지도 훨씬 빨리 판단할 수 있습니다.

### 거의 모든 agent는 같은 루프를 반복합니다

아래 루프는 단순해 보이지만, 실제 agent framework 대부분이 이 구조의 변형입니다.

```text
goal: "Tell me whether I need an umbrella in Tokyo today"

[loop 1]
  observe: known info = (only the goal)
  think:   "I need today's weather; call the weather API"
  act:     get_weather(city="Tokyo")
  check:   result = {temp: 18, condition: "rain"}

[loop 2]
  observe: rain is forecast
  think:   "Rain means yes, an umbrella is needed"
  act:     final_answer("Yes, rain is forecast in Tokyo today")
  check:   goal achieved → stop
```

Observe → Think → Act → Check 루프를 머리에 넣어 두면 ReAct, workflow graph, tool loop, checkpoint 같은 용어가 모두 같은 그림 위에 놓입니다. 또한 디버깅할 때도 어느 단계가 무너졌는지 나눠서 볼 수 있습니다. 도구 호출이 틀렸는지, 생각 단계가 틀렸는지, 체크 단계가 빠졌는지 구분할 수 있어야 운영이 됩니다.

### tool use가 붙는 순간 시스템 성격이 바뀝니다

```python
response = llm.chat("What's the weather in Tokyo?")
# → "I'm sorry, I don't have access to real-time information."
```

```python
goal = "Tell me whether I need an umbrella in Tokyo today"
agent = Agent(tools=[get_weather], llm=llm)
result = agent.run(goal)
# → "Yes, rain is forecast in Tokyo today (18°C, rain)"
```

차이를 만드는 핵심은 `tools=[get_weather]`입니다. 도구가 등록되는 순간 모델은 단순 답변 엔진이 아니라 외부 시스템을 경유할 수 있는 제어기 역할을 맡게 됩니다. 그래서 agent 설계에서는 model choice 못지않게 tool contract가 중요합니다. 어떤 도구가 있고, 어떤 입력을 받고, 어떤 실패를 반환하는지가 agent 품질을 좌우합니다.

### 손으로 한 번 흉내 내보면 구조가 명확해집니다

```python
def get_weather(city: str) -> dict:
    # In production this calls a real API. Mock here.
    fake = {"Tokyo": {"temp": 18, "condition": "rain"},
            "Seoul": {"temp": 22, "condition": "clear"}}
    return fake.get(city, {"error": "unknown city"})
```

```python
goal = "Tell me whether I need an umbrella in Tokyo today"

# observe
context = {"goal": goal, "history": []}

# think (you decide)
next_action = ("get_weather", {"city": "Tokyo"})

# act
result = get_weather(**next_action[1])
context["history"].append((next_action, result))

# check
print(context)
# {'goal': '...', 'history': [(('get_weather', {'city': 'Tokyo'}),
#                              {'temp': 18, 'condition': 'rain'})]}
```

이 연습이 좋은 이유는 framework가 본질을 가리기 전에 구조를 먼저 보게 해주기 때문입니다. 결국 모든 agent는 현재 컨텍스트를 보고 다음 행동을 정하고, 그 행동의 결과를 다시 컨텍스트에 넣는 시스템입니다. 프레임워크는 이 반복을 편하게 만들 뿐, 구조 자체를 바꾸지는 않습니다.

### 루프 제어를 코드로 명시하면 운영 안정성이 올라갑니다

agent를 처음 구현할 때는 tool 호출 데모에 집중하기 쉽지만, 실제 운영에서는 루프 제어 조건이 더 중요합니다. `max_steps`, `allowed_tools`, `retry_budget`, `stop_reason`를 구조화해 두면 실패 원인을 재현하기 쉬워집니다.

```python
from dataclasses import dataclass, field

@dataclass
class AgentState:
    goal: str
    step: int = 0
    max_steps: int = 6
    history: list[dict] = field(default_factory=list)
    stop_reason: str | None = None

def run_agent(goal: str, planner, tools: dict[str, callable]) -> AgentState:
    state = AgentState(goal=goal)

    while state.step < state.max_steps:
        state.step += 1
        action = planner(goal=state.goal, history=state.history)

        if action["type"] == "final":
            state.history.append({"step": state.step, "final": action["answer"]})
            state.stop_reason = "goal_achieved"
            return state

        tool_name = action["tool"]
        if tool_name not in tools:
            state.stop_reason = f"unknown_tool:{tool_name}"
            return state

        result = tools[tool_name](**action.get("args", {}))
        state.history.append({"step": state.step, "action": action, "result": result})

    state.stop_reason = "max_steps_exceeded"
    return state
```

이 형태의 장점은 간단합니다. 종료 조건이 자연어가 아니라 코드로 고정되기 때문에, 관찰 가능한 실패 분류가 생깁니다. `goal_achieved`인지 `max_steps_exceeded`인지부터 구분되면 평가 지표를 설계할 때도 훨씬 유리합니다.

### ReAct 패턴은 추론과 행동 로그를 분리해 기록하는 습관이 핵심입니다

ReAct를 쓰면 모델이 생각과 행동을 번갈아 내놓습니다. 여기서 중요한 점은 "생각을 길게 쓰는 것"이 아니라, 행동 결정 근거를 최소한으로 남기고 실제 호출은 구조화된 형태로 분리하는 것입니다.

```text
Thought: 사용자의 질문은 오늘 도쿄 우산 필요 여부입니다. 최신 강수 정보를 확인해야 합니다.
Action: get_weather
Action Input: {"city": "Tokyo", "date": "today"}
Observation: {"temp": 18, "condition": "rain", "precip_prob": 0.82}
Thought: 강수 확률이 높으므로 우산 필요로 결론낼 수 있습니다.
Final Answer: 오늘 도쿄는 비 예보라서 우산을 챙기는 편이 좋습니다.
```

실무에서는 위 형식을 그대로 사용자에게 노출하지 않고, 내부 telemetry로 수집합니다. 사용자 응답에는 최종 답만 제공하고, 시스템 로그에는 `Action`, `Action Input`, `Observation`을 남기는 방식이 일반적입니다. 그래야 도구 오용과 추론 오류를 분리해서 디버깅할 수 있습니다.

## 흔히 헷갈리는 지점

- "답변을 잘하면 agent다"라고 생각하기 쉽지만, 실제 기준은 외부 행동과 반복 실행입니다.
- tool이 없는 시스템도 넓게는 agent라고 부를 수 있지만, 실무에서는 tool use가 없는 경우 운영상 이점이 크게 줄어듭니다.
- 더 강한 모델이면 agent가 필요 없다고 생각하기 쉽지만, 실시간 정보와 외부 action은 모델 크기로 해결되지 않습니다.
- 모든 자동화 문제에 agent를 붙이면 좋아질 것 같지만, 외부 행동이 없으면 chatbot이나 RAG가 더 단순하고 안정적입니다.
- 최종 답변만 맞으면 된다고 보기 쉽지만, production에서는 경로와 비용과 재시도 횟수도 평가 대상입니다.

## 운영 체크리스트

- [ ] 이 기능이 정말 외부 action을 필요로 하는지 먼저 분리했는가
- [ ] Observe → Think → Act → Check 루프를 글이나 다이어그램으로 설명할 수 있는가
- [ ] 최대 step 수와 종료 조건을 설계했는가
- [ ] tool 실패와 잘못된 중간 판단을 분리해서 기록할 수 있는가
- [ ] chatbot, RAG, agent 중 어떤 추상화가 맞는지 비용 기준까지 포함해 판단했는가

## 정리

AI Agent는 단순히 말을 잘하는 모델이 아닙니다. 목표를 받고, 필요한 외부 도구를 호출하고, 중간 결과를 바탕으로 다음 행동을 정하며, 검증까지 포함한 루프를 반복하는 시스템입니다. 이 정의를 먼저 분명히 해야 이후 설계 선택이 흔들리지 않습니다.

현업에서는 "agent를 쓴다"는 말보다 "어떤 업무를 어떤 루프로 자동화한다"는 표현이 더 유용합니다. 그래야 stop condition, tool contract, retry, memory, evaluation을 같은 그림 안에서 설계할 수 있습니다. 결국 agent 설계는 모델 프롬프트만의 문제가 아니라 제어 흐름과 운영 경계의 문제입니다.

이 글의 목적은 화려한 예제를 보여 주는 데 있지 않습니다. 시리즈 전체를 읽는 동안 계속 재사용할 기준선을 만드는 데 있습니다. 다음 글부터는 이 기준선 위에서 context engineering, tool use, workflow, memory를 하나씩 더 구체적으로 쌓아 올리겠습니다.

## 처음 질문으로 돌아가기

- **챗봇과 agent를 가르는 기준을 기능 이름이 아니라 실행 책임으로 보면 무엇이 달라질까요?**
  - 챗봇은 대체로 사람이 읽을 답변을 만들고 끝나지만, agent는 시스템이 다음 행동을 실행할 수 있도록 목표 달성 과정을 책임집니다. 그래서 설계 기준도 응답 문장이 아니라 실행 루프가 됩니다.
- **Observe → Think → Act → Check 루프는 agent 실패를 어디서 나눠 보게 해 줄까요?**
  - 이 루프를 쓰면 관찰이 부족했는지, 판단이 틀렸는지, 행동이 실패했는지, 결과 확인이 빠졌는지 단계별로 나눠 볼 수 있습니다.
- **처음 agent를 설계할 때 tool보다 먼저 정해야 할 경계는 무엇일까요?**
  - 먼저 목표, 허용 행동, 중단 조건, 사람이 개입해야 할 지점을 정해야 합니다. tool은 그 경계 안에서만 붙이는 실행 수단입니다.

<!-- toc:begin -->
## 시리즈 목차

- **AI Agent 101 (1/10): AI Agent란 무엇인가? (현재 글)**
- AI Agent 101 (2/10): 컨텍스트 엔지니어링 (예정)
- AI Agent 101 (3/10): Tool Use 기초 (예정)
- AI Agent 101 (4/10): Agent Workflow 설계 (예정)
- AI Agent 101 (5/10): Memory와 State (예정)
- AI Agent 101 (6/10): Multi-Agent 시스템 (예정)
- AI Agent 101 (7/10): Agent 평가 (예정)
- AI Agent 101 (8/10): 에러 처리와 안정성 (예정)
- AI Agent 101 (9/10): 운영 (예정)
- AI Agent 101 (10/10): 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain Agents - conceptual guide](https://python.langchain.com/docs/concepts/agents/)
- [OpenAI Platform - Function calling guide](https://platform.openai.com/docs/guides/function-calling)

### 관련 시리즈

- [LangGraph 101 - 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Evaluation 101 - 평가 관점 확장](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/ko/01-what-is-an-ai-agent)

Tags: AI Agent, LLM, Tool Use, Python
