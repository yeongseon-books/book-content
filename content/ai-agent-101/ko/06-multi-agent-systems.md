---
title: Multi-Agent 시스템
series: ai-agent-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Multi-Agent
- Coordination
- Delegation
last_reviewed: '2026-05-12'
seo_description: multi-agent를 역할 분리와 위임 구조 관점에서 정리합니다.
---

# Multi-Agent 시스템

하나의 agent에 검색, 작성, 검토, 계획, 최종 응답까지 모두 맡기면 처음에는 단순해 보입니다. 하지만 요청이 길어지고 역할이 늘어나면 곧 문제가 생깁니다. 누가 계획을 세우는지, 누가 검증하는지, 누가 최종 책임을 지는지가 흐려지기 때문입니다.

이때 등장하는 해법이 multi-agent 시스템입니다. 다만 중요한 점은 agent 수를 늘리는 것 자체가 목적이 아니라는 사실입니다. 좋은 multi-agent는 역할을 나눠서 더 설명 가능하게 만들고, 나쁜 multi-agent는 역할을 나눠서 더 복잡하게 만듭니다.

실무에서 multi-agent를 잘못 도입하면 token 비용과 handoff 횟수만 늘고 품질은 오히려 떨어질 수 있습니다. 그래서 이 주제는 "여러 agent를 어떻게 띄울까"보다 "어떤 업무가 진짜로 위임 구조를 필요로 하는가"에서 출발해야 합니다.

이 글은 AI Agent 101 시리즈의 여섯 번째 글입니다.

이 글에서는 multi-agent를 모델 개수의 문제가 아니라 역할 분리와 위임 프로토콜의 문제로 정리하겠습니다.

## 이 글에서 다룰 문제

- single-agent로 충분한 작업과 multi-agent가 필요한 작업은 어떻게 구분할까요?
- orchestrator, peer-to-peer, hierarchical 패턴은 각각 어떤 trade-off를 가질까요?
- agent 간 handoff에서 가장 자주 터지는 문제는 무엇일까요?
- shared state를 어디까지 공유해야 하고 어디서 막아야 할까요?
- multi-agent가 좋아 보이지만 실제로는 비용만 키우는 신호는 무엇일까요?

## 왜 이 글이 중요한가

multi-agent는 종종 성능 향상 도구로 소개되지만, 실제 현장에서는 구조화된 위임을 위한 도구에 더 가깝습니다. 어떤 agent가 어떤 종류의 결정을 하고 어떤 산출물만 남겨야 하는지 분리되면, 시스템이 커져도 읽기가 쉬워집니다.

반대로 역할 분리 없이 agent만 여러 개 두면 문제가 더 커집니다. 서로에게 같은 질문을 넘기고, 동일한 정보를 중복 검색하고, 최종 답변 책임이 불명확해지고, 장애가 나도 어디서 틀어졌는지 추적하기 어려워집니다. 즉, multi-agent의 난점은 모델 수가 아니라 프로토콜 설계입니다.

또한 이 주제는 운영과 평가에도 직결됩니다. route 정확도, handoff 수, agent별 latency, shared state 오염, 불필요한 delegation 비율 같은 지표는 multi-agent 구조가 있어야만 드러납니다. 그래서 역할 분리를 도입한다면 관측성도 함께 설계해야 합니다.

## Multi-Agent를 이해하는 가장 좋은 방법: 협업이 아니라 위임 그래프로 보는 것입니다

multi-agent를 "여러 agent가 함께 일한다"고만 설명하면 너무 추상적입니다. 더 실용적인 설명은 누가 어떤 하위 작업을 맡고 어떤 결과만 남기는지 정의된 위임 그래프라는 것입니다. 이 관점이 있어야 supervisor와 worker, reviewer와 writer, manager와 child agent의 차이가 선명해집니다.

이 구조에서 중요한 것은 세 가지입니다. 첫째, 누가 route를 결정하는가. 둘째, 각 agent가 shared state의 어느 부분을 읽고 쓸 수 있는가. 셋째, 누가 최종 답을 사용자에게 돌려주는가. 이 세 가지가 모호하면 agent 수가 늘수록 시스템은 더 읽기 어려워집니다.

실무에서는 multi-agent를 쓰는 이유가 똑똑해 보이기 위해서가 아니라, 책임을 좁히고 실패 범위를 줄이기 위해서여야 합니다. 그래야 비용이 늘어도 얻는 운영 이점이 분명합니다.

> multi-agent 시스템의 핵심은 "agent가 여러 개다"가 아니라, "역할과 handoff 규칙이 코드와 상태에 명시되어 있다"는 데 있습니다.

## 핵심 개념

### Orchestrator 패턴은 중앙 조율에 강합니다

```python
from typing import List, Dict
from openai import OpenAI

class WorkerAgent:
    """A specialized worker agent."""

    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)

    def execute(self, task: str) -> str:
        """Execute a task."""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are a {self.role}."},
                {"role": "user", "content": task}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

class OrchestratorAgent:
    """An orchestrator agent that coordinates workers."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.workers: Dict[str, WorkerAgent] = {}

    def register_worker(self, worker: WorkerAgent) -> None:
        """Register a worker."""
        self.workers[worker.name] = worker

    def plan(self, request: str) -> List[Dict]:
        """Decompose the request into subtasks."""
        worker_list = "
".join([
            f"- {name}: {w.role}"
            for name, w in self.workers.items()
        ])
        prompt = f"""Break down the following request into subtasks and assign each to the appropriate worker.

Available workers:
{worker_list}

Request: {request}

Respond in JSON format:
[
  {{"worker": "worker_name", "task": "task description"}},
  ...
]
"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        import json
        return json.loads(response.choices[0].message.content)

    def handle(self, request: str) -> Dict:
        """Handle the request."""
        subtasks = self.plan(request)
        results = {}
        for subtask in subtasks:
            worker_name = subtask["worker"]
            task = subtask["task"]
            if worker_name in self.workers:
                results[worker_name] = self.workers[worker_name].execute(task)
        return results
```

Orchestrator는 중앙에서 route와 fallback을 관리하기 좋습니다. 단계가 명확하고 승인 지점을 넣기 쉬우며, 로그를 한곳에서 모으기도 쉽습니다. 대신 단일 병목과 단일 실패 지점이 생긴다는 단점이 있습니다.

### Peer-to-Peer는 유연하지만 프로토콜이 약하면 금방 흐려집니다

```python
from typing import List, Optional

class PeerAgent:
    """A peer agent."""

    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)
        self.peers: List["PeerAgent"] = []
        self.message_history: List[Dict] = []

    def add_peer(self, peer: "PeerAgent") -> None:
        """Add a peer."""
        if peer not in self.peers:
            self.peers.append(peer)

    def send_message(self, recipient: "PeerAgent", message: str) -> str:
        """Send a message to a peer."""
        msg = {
            "from": self.name,
            "to": recipient.name,
            "content": message
        }
        self.message_history.append(msg)
        return recipient.receive_message(self, message)

    def receive_message(self, sender: "PeerAgent", message: str) -> str:
        """Receive a message and respond."""
        prompt = f"""You are {self.name}, a {self.role}.
Message from {sender.name}: {message}

Respond appropriately. If you need help from another peer, mention it."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        reply = response.choices[0].message.content

        self.message_history.append({
            "from": sender.name,
            "to": self.name,
            "content": message,
            "reply": reply
        })
        return reply
```

이 패턴은 창의적 협업이나 리뷰-피드백 흐름에는 자연스럽습니다. 하지만 누가 종료를 선언하는지, 어느 시점에 escalation하는지, 동일 요청을 다시 보내면 어떻게 막을지 같은 규칙이 없으면 곧 루프와 중복이 생깁니다.

### Hierarchical 패턴은 큰 조직 구조를 닮습니다

부모 agent가 자식 agent에게 위임하고, 자식은 더 작은 하위 작업을 맡습니다. 규모가 큰 업무를 계층적으로 분해할 때 유용하지만, 깊이가 늘수록 context 손실과 보고 비용도 함께 커집니다. 따라서 child가 남기는 출력 계약을 매우 좁게 설계해야 합니다.

### shared state는 최소 계약만 노출하는 편이 좋습니다

- route, current_owner, worker_result 같은 핵심 필드만 공유합니다.
- 각 agent 전용 scratchpad를 전역 shared state로 노출하지 않습니다.
- handoff마다 입력과 출력 스키마를 고정합니다.
- 최종 조립 책임은 한 agent 또는 별도 finalizer에 둡니다.
- delegation 사유를 로그에 남겨 route 품질을 평가할 수 있게 합니다.

## 흔히 헷갈리는 지점

- agent를 여러 개 두면 자동으로 품질이 올라갈 것이라 기대하기 쉽지만, 실제로는 역할 경계가 먼저 필요합니다.
- orchestrator가 모든 세부 작업까지 하도록 만들면 결국 single-agent와 다를 바가 없어집니다.
- shared state를 넓게 열어 두면 유연할 것 같지만, 곧 결합도와 디버깅 난이도가 폭증합니다.
- peer-to-peer는 자유로워 보여도 종료 규칙이 없으면 무한 handoff가 생기기 쉽습니다.
- multi-agent는 전문성이 높아 보이지만, 실제로는 single-agent + better tools로 충분한 문제도 많습니다.

## 운영 체크리스트

- [ ] multi-agent가 정말 필요한지 single-agent 대안과 비교했는가
- [ ] 누가 route를 결정하고 누가 최종 답을 책임지는지 명시했는가
- [ ] handoff 입력/출력 스키마와 종료 조건이 정의되어 있는가
- [ ] shared state를 최소 필드로 제한했는가
- [ ] agent별 latency, route accuracy, handoff count를 측정하는가

## 정리

multi-agent 시스템은 여러 모델을 멋지게 묶는 기술이 아닙니다. 역할을 분리하고, 위임 경계를 명확히 하고, 최종 책임 위치를 고정해서 더 설명 가능한 자동화 구조를 만드는 방법입니다. 그래서 핵심은 agent 수보다 프로토콜 품질에 있습니다.

좋은 multi-agent 설계는 각 agent를 더 작게 만들고, shared state를 더 좁게 만들며, 최종 조립 지점을 더 선명하게 만듭니다. 반대로 나쁜 설계는 agent를 늘릴수록 누가 무엇을 했는지 알기 어려워집니다.

다음 글에서는 이런 시스템을 어떻게 평가할지 다룹니다. route가 적절했는지, trajectory가 효율적이었는지, 최종 성공률이 유지되는지를 측정하지 않으면 multi-agent의 비용을 정당화할 수 없기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- [Agent Workflow 설계](./04-agent-workflow-design.md)
- [Memory와 State](./05-memory-and-state.md)
- **Multi-Agent 시스템 (현재 글)**
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph - Multi-agent workflows](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [OpenAI Platform - Agents guide](https://platform.openai.com/docs/guides/agents)
- [CrewAI Documentation](https://docs.crewai.com/)

### 관련 시리즈

- [LangGraph 101 - 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Evaluation 101 - 시스템 평가 관점](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md)

Tags: AI Agent, LLM, Tool Use, Python
