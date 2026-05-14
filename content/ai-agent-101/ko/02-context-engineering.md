---
title: 컨텍스트 엔지니어링
series: ai-agent-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Context
- Prompt Engineering
- System Prompt
last_reviewed: '2026-05-12'
seo_description: agent 판단을 좌우하는 역할, 규칙, 도구, 상태 설계를 정리합니다.
---

# 컨텍스트 엔지니어링

agent가 엉뚱한 도구를 고르거나, 이미 알고 있는 정보를 다시 묻거나, 금지된 행동을 시도하는 장면을 보면 많은 팀이 먼저 모델 성능을 의심합니다. 하지만 실제 원인은 모델보다 컨텍스트 구성인 경우가 훨씬 많습니다.

LLM은 현재 prompt 안에 들어온 정보만 보고 판단합니다. system prompt가 모호하면 역할이 흐려지고, tool description이 약하면 잘못된 함수를 고르고, state가 없으면 이미 끝낸 작업을 반복합니다. 즉, agent 품질은 추론 능력만이 아니라 입력 구조의 품질에도 크게 좌우됩니다.

그래서 context engineering은 단순한 "프롬프트 잘 쓰기"가 아닙니다. agent가 어떤 정보를 어떤 순서로 보고, 무엇을 절대 하지 말아야 하며, 어느 범위까지 스스로 결정할 수 있는지를 시스템적으로 설계하는 일입니다.

이 글은 AI Agent 101 시리즈의 두 번째 글입니다.

이 글에서는 컨텍스트를 역할, 규칙, 도구 설명, 상태 정보의 계약으로 나눠서 보는 관점을 정리하겠습니다.

## 이 글에서 다룰 문제

- agent의 컨텍스트를 구성하는 최소 요소는 무엇일까요?
- system prompt에서 가장 먼저 분리해야 할 것은 역할일까요, 규칙일까요?
- tool description이 약하면 어떤 실패가 실제로 생길까요?
- history와 state를 모두 넣어야 할 때 우선순위는 어떻게 정해야 할까요?
- 컨텍스트를 길게 넣는 것과 정확하게 넣는 것은 왜 다른 문제일까요?

## 왜 이 글이 중요한가

context engineering은 agent 품질의 바닥을 결정합니다. 좋은 모델도 잘못된 컨텍스트 안에서는 흔들리고, 상대적으로 작은 모델도 역할과 규칙이 명확하면 꽤 안정적으로 동작합니다. 따라서 이 주제는 모델 튜닝 이전에 먼저 다뤄야 하는 기본기입니다.

운영 관점에서도 중요합니다. 문제가 생겼을 때 "모델이 이상했다"고 말하면 개선 포인트가 남지 않습니다. 반대로 역할 정의가 모호했는지, forbidden action이 빠졌는지, tool schema 설명이 약했는지, 오래된 history가 최신 state를 덮었는지까지 쪼개어 보면 수정 가능한 시스템 문제가 보입니다.

또한 context engineering은 이후의 memory, workflow, evaluation과 직접 연결됩니다. 어떤 정보가 현재 턴에 들어가고 어떤 정보가 외부 저장소로 빠져야 하는지 정하지 않으면 memory 전략도, token budget도, 평가 기준도 함께 흔들립니다.

## 컨텍스트 엔지니어링을 이해하는 가장 좋은 방법: 모델의 입력이 아니라 행동 계약으로 보는 것입니다

컨텍스트를 단순히 "프롬프트에 넣는 텍스트"로 보면 길이 싸움으로 흘러가기 쉽습니다. 하지만 agent 설계에서는 컨텍스트를 **행동 계약**으로 보는 편이 훨씬 실용적입니다. 역할은 정체성을, 규칙은 허용 범위를, 도구 설명은 행동 수단을, state는 현재 위치를 정의합니다.

이렇게 보면 좋은 컨텍스트는 길어서 좋은 것이 아니라, 판단에 필요한 경계를 잘 드러내서 좋습니다. 무엇을 할 수 있는지와 무엇을 하면 안 되는지가 동시에 분명해야 하고, 지금 시점에 필요한 상태만 들어 있어야 하며, 출력 형식도 downstream 시스템이 소비할 수 있도록 고정되어야 합니다.

실무에서 저는 system prompt를 "설명문"보다 "계약서"처럼 쓰는 편이 더 안정적이라고 봅니다. 추상적인 친절함보다 검증 가능한 행동 제약이 중요하기 때문입니다.

> context engineering의 핵심은 모델에게 많은 정보를 주는 것이 아니라, 올바른 결정을 내릴 수 있도록 역할·규칙·도구·상태의 경계를 명시하는 데 있습니다.

## 핵심 개념

### agent 컨텍스트는 네 가지 축으로 나눠 보는 편이 좋습니다

- **System Prompt**: agent의 정체성과 기본 행동 규칙
- **Conversation History**: 직전 대화 맥락과 이미 교환된 사실
- **Tool Descriptions**: 사용 가능한 수단과 입력 계약
- **State Information**: 현재 작업 단계와 남은 일

아래 예시는 각각이 어떤 정보를 담아야 하는지 보여 줍니다.

```python
system_prompt = """
You are a code review agent helping Python developers.

Responsibilities:
- Identify code quality issues
- Provide specific improvement suggestions
- Follow PEP 8 style guidelines

Constraints:
- Only mention issues verifiable in the code, no speculation
- Focus on constructive suggestions rather than criticism
"""
```

역할과 제약을 함께 적는 이유는 agent가 무엇을 해야 하는지뿐 아니라 어디서 멈춰야 하는지도 동시에 알게 하기 위해서입니다. "도움이 되는 비서" 같은 추상 표현은 읽기에는 부드럽지만, 운영에서는 거의 아무 경계도 제공하지 못합니다.

```python
history = [
    {"role": "user", "content": "Review this function: def calc(x, y): return x + y"},
    {"role": "assistant", "content": "Function name is ambiguous. Use add_numbers instead of calc."},
    {"role": "user", "content": "Can you add type hints too?"}
]
```

history는 친절한 기억 장치가 아니라 현재 턴 해석에 필요한 누적 맥락입니다. 길다고 좋은 것이 아니며, 최신 의사결정에 직접 필요한 부분만 남기는 편이 안전합니다. 그렇지 않으면 오래된 대화가 최신 state를 덮어버리는 일이 생깁니다.

```python
tools = [
    {
        "name": "run_pylint",
        "description": "Runs pylint on Python code and returns quality score and warning list.",
        "parameters": {
            "code": "str - Python code to analyze"
        }
    },
    {
        "name": "search_docs",
        "description": "Searches Python official documentation for keywords.",
        "parameters": {
            "keyword": "str - Keyword to search"
        }
    }
]
```

도구 설명은 생각보다 강력합니다. 이름이 모호하거나 description이 비어 있으면 모델은 사용자 의도를 보고도 적절한 도구를 고르지 못합니다. 반대로 설명이 구체적이면 planner 없이도 상당수 요청을 안정적으로 라우팅합니다.

```python
state = {
    "task": "Review 5 endpoints in FastAPI app sequentially",
    "completed": ["GET /users", "POST /users"],
    "current": "GET /users/{id}",
    "remaining": ["PUT /users/{id}", "DELETE /users/{id}"]
}
```

state는 현재 위치를 알려 주는 신호입니다. workflow가 길어질수록 history만으로는 현재 단계 복원이 어렵기 때문에 state를 별도 필드로 두는 편이 좋습니다. 특히 agent가 여러 단계를 오가거나 재시도할 때는 더 그렇습니다.

### system prompt는 설명문보다 계약서에 가깝게 써야 합니다

아래 예시는 역할과 금지 범위를 같이 보여 줍니다.

```python
# Bad example
system_prompt_bad = "You are a helpful assistant."

# Good example
system_prompt_good = """
You are a sales team support assistant agent.

Can do:
- Book meeting rooms (Outlook Calendar API)
- Draft and send emails
- Look up customer information in CRM

Cannot do:
- Approve contracts (requires human verification)
- Access customer credit card information
- Make independent pricing decisions
"""
```

좋은 system prompt는 무엇을 할 수 있는가와 할 수 없는가를 동시에 드러냅니다. 그래야 모델이 경계 안에서 자율적으로 움직일 수 있습니다. agent는 자유롭게 두는 것보다 안전하게 자유롭게 두는 것이 중요합니다.

### 출력 형식과 few-shot은 downstream 안정성을 위해 필요합니다

```python
system_prompt_with_format = """
You are a code review agent.

Output format:
{
  "issues": [
    {"line": 15, "severity": "error", "message": "Issue description"},
    {"line": 23, "severity": "warning", "message": "Warning content"}
  ],
  "suggestions": [
    {"line": 15, "fix": "Specific fix approach"}
  ],
  "summary": "Overall assessment summary (1-2 sentences)"
}

Important: Respond only in JSON format, no additional explanation text.
"""
```

```python
system_prompt_with_examples = """
You are an agent that converts user requests to SQL queries.

Example 1:
Input: "Show me 10 users who joined last month"
Output: SELECT * FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH) LIMIT 10;

Example 2:
Input: "How many premium users in LA?"
Output: SELECT COUNT(*) FROM users WHERE city='Los Angeles' AND plan='premium';

Example 3:
Input: "Delete all users"
Output: Sorry, I cannot execute DELETE statements.
"""
```

출력 형식 지정은 사람이 읽기 좋게 하려는 장식이 아닙니다. 후속 코드가 실패하지 않게 하려는 계약입니다. few-shot 역시 모델을 감동시키려는 예시가 아니라, 허용 행동과 금지 행동의 경계 샘플을 제공하는 수단입니다.

## 흔히 헷갈리는 지점

- 컨텍스트를 많이 넣을수록 좋아진다고 생각하기 쉽지만, 실제로는 불필요한 history가 판단을 흐릴 수 있습니다.
- system prompt만 잘 쓰면 된다고 보기 쉽지만, tool description과 state 품질이 동일하게 중요합니다.
- 역할 설명과 행동 규칙을 섞어 쓰면 나중에 수정 포인트가 흐려집니다.
- 출력 형식을 프롬프트 맨 아래에 한 줄 적는 것으로 충분하다고 생각하기 쉽지만, 실제로는 예시와 금지 규칙까지 같이 있어야 안정적입니다.
- history를 memory의 전부로 생각하기 쉽지만, 장기적으로는 state와 long-term memory를 분리해야 합니다.

## 운영 체크리스트

- [ ] 역할, 규칙, 도구 설명, 상태 정보를 서로 다른 계층으로 설계했는가
- [ ] system prompt에 금지 행동과 escalation 조건이 명시되어 있는가
- [ ] tool description이 언제 써야 하는지까지 설명하는가
- [ ] history 축약 기준과 최신 state 우선순위가 정해져 있는가
- [ ] 출력 형식이 downstream 코드에서 바로 검증 가능하도록 고정되어 있는가

## 정리

컨텍스트 엔지니어링은 프롬프트 문장을 예쁘게 다듬는 작업이 아닙니다. agent가 어떤 정체성을 갖고, 어떤 경계 안에서, 어떤 수단을 통해, 현재 어느 위치에서 판단하는지를 설계하는 일입니다. 그래서 이 주제는 UX보다 시스템 계약에 가깝습니다.

좋은 컨텍스트는 agent를 더 창의적으로 만드는 것이 아니라 더 예측 가능하게 만듭니다. 예측 가능성이 생겨야 디버깅이 가능하고, 디버깅이 가능해야 평가와 운영 자동화가 붙습니다. 결국 안정적인 agent의 시작점은 모델보다 컨텍스트 구조에 있습니다.

다음 글에서는 이 구조 위에서 실제로 도구를 어떻게 정의하고 호출 루프에 연결하는지 살펴보겠습니다. context engineering이 행동 계약이라면, tool use는 그 계약이 실제 시스템 호출로 이어지는 첫 번째 지점입니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- **컨텍스트 엔지니어링 (현재 글)**
- Tool Use 기초 (예정)
- Agent Workflow 설계 (예정)
- Memory와 State (예정)
- Multi-Agent 시스템 (예정)
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI Platform - Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [LangChain - Agents conceptual guide](https://python.langchain.com/docs/concepts/agents/)
- [OpenAI Platform - Structured outputs guide](https://platform.openai.com/docs/guides/structured-outputs)

### 관련 시리즈

- [Prompt Engineering 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [LangGraph 101 - 상태와 라우팅 설계](../../langgraph-101/ko/02-state-and-checkpoints.md)

Tags: AI Agent, LLM, Tool Use, Python
