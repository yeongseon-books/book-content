---
title: AI Agent란 무엇인가?
series: ai-agent-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- LLM
- Tool Use
- Autonomy
- ReAct
- Automation
last_reviewed: '2026-05-11'
seo_description: Chatbot은 "질문에 답하는 사전"이라면, Agent는 "할 일을 받고 알아서 끝내고 오는 인턴"입니다.
---

# AI Agent란 무엇인가?

> AI Agent 101 시리즈 (1/10)

LLM을 처음 만나면 많은 사람이 이를 그저 질문에 답하는 모델로 이해합니다. 채팅창에서 답변이 잘 나오면 충분하다고 느끼지만, 실제 업무 자동화로 넘어가는 순간 이 관점은 빠르게 한계를 드러냅니다.

고객 문의를 분류하고 담당 팀에 티켓을 만들고 응답 초안까지 작성하게 하려면, 모델은 말만 잘하는 것을 넘어 외부 system을 호출하고 결과를 보고 다음 행동을 정해야 합니다. 이 지점에서 chatbot과 Agent의 차이가 분명해집니다.

이 글은 AI Agent 101 시리즈의 첫 번째 글입니다. 여기서는 chatbot과 Agent의 차이, 그리고 observe → think → act → check 루프로 Agent를 이해하는 기본 멘탈 모델을 설명합니다.

---

## 이 글에서 다룰 문제

LLM을 처음 만나면 대부분 "질문하면 답하는 모델"로 이해합니다. 그래서 ChatGPT의 채팅창이 곧 LLM의 전부라고 생각하기 쉽습니다. 하지만 실무에서 LLM을 production에 쓰는 순간 한계가 드러납니다.

> "고객 문의 1,000건을 분류하고, 각각 적절한 담당팀에 티켓을 만들고, 응답 초안까지 작성해줘."

이 한 줄은 chatbot으로는 불가능합니다. 모델이 외부 system을 호출해야 하고, 결과를 보고 다음 행동을 결정해야 하고, 실패하면 retry해야 합니다. 이 지점이 chatbot과 Agent가 갈라지는 곳입니다. Agent를 이해하면 LLM의 역할이 "대화 상대"에서 "자동화 가능한 worker"로 확장됩니다.

## Mental Model

> Chatbot은 "질문에 답하는 사전"이라면, Agent는 "할 일을 받고 알아서 끝내고 오는 인턴"입니다.

사전은 펼치면 답이 있지만, 다시 덮으면 그걸로 끝입니다. 인턴은 다릅니다. 처음에는 무엇을 해야 하는지 모르지만, 주변을 둘러보고(observe), 무엇을 할지 정하고(think), 손을 움직이고(act), 결과를 확인합니다(check). 결과가 만족스럽지 않으면 다시 시도합니다. 이 루프가 Agent의 본질입니다.

## 핵심 개념 1 - Chatbot vs Agent

| | Chatbot | Agent |
|---|---|---|
| 입력 | 사용자 메시지 | 목표(goal) |
| 출력 | 텍스트 응답 | 작업 완료 또는 산출물 |
| 외부 상호작용 | 없음 | tool 호출, file/API 접근 |
| 반복 | 1턴 | 목표 달성까지 N턴 |
| 상태 | 대화 history | 작업 상태 + memory |

기술적으로 Agent도 내부에서는 LLM 호출입니다. 차이는 **LLM의 출력을 사람이 읽느냐, 시스템이 받아서 다음 행동을 실행하느냐** 입니다.

## 핵심 개념 2 - Observe → Think → Act → Check 루프

Agent의 모든 동작은 이 4단계 루프의 반복입니다.

```text
goal: "오늘 도쿄 날씨를 확인하고 우산 필요 여부를 알려줘"

[loop 1]
  observe: 현재 정보 = (목표만 있음)
  think:   "날씨를 알아야 하니 weather API 호출이 필요하다"
  act:     get_weather(city="Tokyo") 호출
  check:   결과 = {temp: 18, condition: "rain"}

[loop 2]
  observe: 비 예보가 있음
  think:   "비가 오므로 우산이 필요하다고 답하면 된다"
  act:     final_answer("도쿄에 비 예보가 있어 우산이 필요합니다")
  check:   목표 달성 → 종료
```

이 루프를 LLM 호출로 구현한 것이 ReAct(Reason + Act) pattern이고, 거의 모든 Agent framework가 이 변형입니다.

## Before / After

**Before (chatbot 방식)**

```python
response = llm.chat("도쿄 날씨 알려줘")
# → "죄송하지만 저는 실시간 정보에 접근할 수 없습니다."
```

**After (Agent 방식)**

```python
goal = "도쿄 날씨를 확인하고 우산 필요 여부를 알려줘"
agent = Agent(tools=[get_weather], llm=llm)
result = agent.run(goal)
# → "도쿄에 비 예보가 있어 우산이 필요합니다 (기온 18°C, rain)"
```

핵심 차이는 `tools=[get_weather]` 한 줄입니다. Agent에게 "이 도구를 쓸 수 있다"고 알려주면 LLM은 스스로 호출 시점을 결정합니다.

## 단계별 실습 - 손으로 Agent 흉내 내기

framework 없이도 Agent의 동작을 이해할 수 있습니다. 작은 Python 함수 두 개만 있으면 됩니다.

### Step 1. tool 정의

```python
def get_weather(city: str) -> dict:
    # 실제로는 OpenWeather API를 호출합니다. 여기서는 모의 데이터를 사용합니다.
    fake = {"Tokyo": {"temp": 18, "condition": "rain"},
            "Seoul": {"temp": 22, "condition": "clear"}}
    return fake.get(city, {"error": "unknown city"})
```

### Step 2. 루프 한 번 흉내 내기

LLM 없이 사람이 LLM 역할을 합니다.

```python
goal = "도쿄 날씨를 확인하고 우산 필요 여부를 알려줘"

# 관찰
context = {"goal": goal, "history": []}

# 생각(사람이 결정)
next_action = ("get_weather", {"city": "Tokyo"})

# 실행
result = get_weather(**next_action[1])
context["history"].append((next_action, result))

# 확인
print(context)
# 예시 출력: {'goal': '...', 'history': [(('get_weather', {'city': 'Tokyo'}),
#           예시 계속:                          {'temp': 18, 'condition': 'rain'})]}
```

### Step 3. LLM에게 think를 맡기기

`think` 단계에서 LLM에게 "지금 context를 보고 다음에 어떤 tool을 호출할지 JSON으로 답하라"고 시키면, 이것이 가장 단순한 Agent입니다. 다음 글에서 ReAct prompt와 함께 다룹니다.

## 자주 하는 실수

### 실수 1. "LLM이 더 똑똑해지면 Agent도 한 번에 답할 수 있다"고 가정

Agent의 본질은 모델 크기가 아니라 **외부 system과의 상호작용**입니다. GPT-5가 와도 weather API 없이는 실시간 날씨를 모릅니다. tool 없는 Agent는 불가능합니다.

### 실수 2. 모든 작업에 Agent를 쓰려고 한다

요약, 번역, 단순 Q&A는 chatbot으로 충분합니다. Agent는 LLM 호출이 여러 번 일어나므로 비용과 latency가 5-20배 늘어납니다. 외부 action이 필요 없으면 Agent를 쓸 이유가 없습니다.

### 실수 3. tool 호출 결과를 검증하지 않는다

Agent가 호출한 API가 에러를 반환했는데도 LLM이 "성공한 것처럼" 다음 단계를 진행하는 경우가 흔합니다. check 단계를 명시적으로 두고, 실패 시 retry나 fallback 경로를 정의해야 합니다.

### 실수 4. 무한 루프 가능성을 무시한다

LLM이 잘못된 판단을 반복하면 같은 tool을 영원히 호출합니다. 항상 최대 step 수(예: 10)를 정해 두고, 초과하면 강제 종료해야 합니다.

### 실수 5. context가 무한히 커진다

매 루프마다 history가 prompt에 들어가므로 token이 폭발합니다. memory 압축, 요약, 또는 sliding window가 필요합니다(Ep5에서 다룸).

## 실무에서는 이렇게 생각한다

production에서 Agent 도입을 결정할 때는 다음 질문을 먼저 던집니다.

- **외부 action이 필요한가?** 없으면 chatbot 또는 RAG로 충분합니다.
- **multi-step 추론이 필요한가?** "검색 → 비교 → 결론" 같은 흐름이 있어야 Agent의 가치가 살아납니다.
- **실패 가능성을 감당할 수 있는가?** Agent는 chatbot보다 실패 mode가 많습니다. 금융 거래처럼 실패 비용이 큰 영역은 human-in-the-loop이 필수입니다.
- **비용이 정당화되는가?** 작업당 평균 5-15회 LLM 호출이 발생하므로 chatbot 대비 단가가 크게 올라갑니다.

이 4개 중 2개 이상에 "yes"가 나오면 Agent를 진지하게 검토합니다.

## 체크리스트

- [ ] chatbot과 Agent의 차이를 한 문장으로 설명할 수 있다
- [ ] observe → think → act → check 루프를 그릴 수 있다
- [ ] 우리 use case가 Agent에 적합한지 4개 질문으로 판단할 수 있다
- [ ] 무한 루프와 context bloat 위험을 알고 있다

## 정리

- AI Agent는 목표를 받고 observe → think → act → check 루프를 반복하는 LLM-기반 자동화 시스템입니다.
- chatbot과의 차이는 외부 tool 호출 능력과 multi-turn 자율 의사 결정입니다.
- 모든 작업에 Agent가 필요한 것은 아니며, 외부 action + multi-step 판단이 결합될 때 가치가 가장 큽니다.
- 무한 루프, context bloat, tool 실패는 Agent 도입 시 가장 먼저 설계해야 할 risk입니다.
- framework 없이도 손으로 루프를 한 번 그려보면 모든 Agent framework의 구조가 같다는 것이 보입니다.

## 다음 글

다음 글에서는 Agent의 결정 품질을 좌우하는 **context engineering** - 무엇을 prompt에 넣고, 무엇을 빼야 할지를 다룹니다.

<!-- a-grade-example:begin -->

## 체크리스트

- [ ] Chatbot과 Agent의 차이를 한 문장으로 설명할 수 있다.
- [ ] Observe→Think→Act→Check 루프를 손으로 한 사이클 흉내 냈다.
- [ ] Agent의 자율성 수준을 분류 기준으로 평가할 수 있다.
- [ ] 이 시리즈가 다루는 범위와 다루지 않는 범위를 적었다.

<!-- a-grade-example:end -->

<!-- toc:begin -->
## 시리즈 목차

- **AI Agent란 무엇인가? (현재 글)**
- 컨텍스트 엔지니어링 (예정)
- Tool Use 기초 (예정)
- Agent Workflow 설계 (예정)
- Memory와 State (예정)
- Multi-Agent 시스템 (예정)
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain Agents - conceptual guide](https://python.langchain.com/docs/concepts/agents/)
- [OpenAI - Function calling guide](https://platform.openai.com/docs/guides/function-calling)

Tags: AI Agent, LLM, Tool Use, Python
