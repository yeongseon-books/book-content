---
title: "바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템"
series: ai-agent-101
episode: 6
language: ko
tags:
- Multi-Agent
- Orchestrator
- 바이브코딩
- Vibe Coding
- Message Bus
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 여섯 번째 글입니다.

---

바이브코딩으로 에이전트를 만들다 보면 "하나의 에이전트가 너무 많은 걸 하려고 한다"는 문제를 만납니다. 검색도 하고, 분석도 하고, 글도 쓰고, 리뷰도 해야 하는 에이전트는 프롬프트가 복잡해지고 품질이 떨어집니다. 이때 등장하는 해결책이 **멀티 에이전트 시스템**입니다.

멀티 에이전트 시스템은 각자 전문화된 에이전트들이 협력해 복잡한 목표를 달성합니다. 글쓰기 에이전트, 검색 에이전트, 리뷰 에이전트가 각자 자신의 역할에 집중하면 전체 품질이 올라갑니다. 하지만 이 구조에는 조율과 통신이라는 새로운 복잡성이 생깁니다.

> "멀티 에이전트 시스템은 팀과 같습니다. 각자 전문성이 있지만, 조율 없이는 팀이 아닌 개인들의 모음입니다."

## 이 글에서 다룰 질문

1. 오케스트레이터 패턴과 피어투피어 패턴은 언제 각각 적합한가요?
2. 에이전트 간 통신은 어떤 구조로 설계하나요?
3. 여러 에이전트가 공유 상태를 어떻게 안전하게 접근하나요?
4. 멀티 에이전트 시스템에서 디버깅이 어려운 이유는 무엇인가요?
5. 에이전트 수를 늘릴수록 항상 좋아지나요?

---

## 멀티 에이전트 패턴 비교

| 패턴 | 특징 | 장점 | 단점 |
|------|------|------|------|
| 오케스트레이터-워커 | 중앙 에이전트가 조율 | 제어가 쉬움, 추적 용이 | 오케스트레이터가 병목 |
| 피어투피어 | 에이전트들이 직접 통신 | 유연함, 병렬 처리 용이 | 통신 복잡도 증가 |
| 계층형 | 오케스트레이터의 오케스트레이터 | 대규모 확장 가능 | 설계 복잡도 매우 높음 |

## Before / After: 단일 vs 멀티 에이전트

**Before (단일 에이전트 - 모든 역할)**
```python
# 한 에이전트가 연구, 작성, 리뷰를 모두 담당
agent = Agent(system_prompt="""
당신은 연구자이자 작가이자 편집자입니다.
주제를 연구하고, 글을 쓰고, 스스로 리뷰하세요.
""")
result = agent.run("AI 에이전트 시장 동향 리포트 작성")
# 문제: 역할이 혼재되어 품질이 낮음
```

**After (오케스트레이터-워커 패턴)**
```python
class ResearchOrchestrator:
    def __init__(self):
        self.researcher = WorkerAgent("연구 전문가", tools=[web_search])
        self.writer = WorkerAgent("기술 작가", tools=[document_writer])
        self.reviewer = WorkerAgent("편집자", tools=[grammar_check])

    def run(self, goal: str) -> str:
        # 1. 연구
        research = self.researcher.execute(f"다음 주제를 조사하세요: {goal}")

        # 2. 초안 작성
        draft = self.writer.execute(f"연구 결과를 바탕으로 리포트를 작성하세요:\n{research}")

        # 3. 리뷰
        final = self.reviewer.execute(f"다음 리포트를 개선하세요:\n{draft}")

        return final
```

## 공유 상태와 메시지 버스

여러 에이전트가 협력할 때는 상태 공유와 통신 방식을 명확히 정의해야 합니다.

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = ""
    content: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class MessageBus:
    def __init__(self):
        self.messages: list[Message] = []
        self.subscribers: dict[str, list] = {}

    def publish(self, message: Message):
        self.messages.append(message)
        for handler in self.subscribers.get(message.to_agent, []):
            handler(message)

    def subscribe(self, agent_id: str, handler):
        self.subscribers.setdefault(agent_id, []).append(handler)
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 에이전트 수를 무조건 늘림 | 통신 오버헤드, 조율 복잡도 증가 | 실제로 필요할 때만 분리 |
| 공유 상태에 락(lock) 없음 | 경쟁 조건(race condition) 발생 | 공유 상태 접근을 명시적으로 제어 |
| 에이전트 간 통신 로그 없음 | 디버깅 불가 | 모든 메시지를 로깅 |
| 오케스트레이터가 너무 많이 알아야 함 | 단일 실패 지점 | 워커가 더 자율적으로 동작하도록 설계 |

## AI 팁

멀티 에이전트 시스템에서 가장 중요한 디버깅 도구는 **에이전트 간 메시지 로그**입니다. 어떤 에이전트가 무엇을 누구에게 보냈고, 어떤 결과를 받았는지 기록하면 문제 원인을 빠르게 파악할 수 있습니다.

```python
# cross_agent_hops 메트릭으로 통신 횟수 추적
metrics = {
    "cross_agent_hops": 0,
    "total_tokens": 0,
    "agent_latencies": {}
}
```

에이전트 간 홉(hop) 수가 늘어날수록 지연 시간과 비용이 증가합니다. 3-5 홉 이내로 설계하는 것이 일반적으로 효율적입니다.

## 체크리스트

- [ ] 에이전트 역할과 책임 경계를 명확히 정의했다
- [ ] 에이전트 간 모든 메시지를 로깅한다
- [ ] 공유 상태에 동시 접근 시 안전하게 처리한다
- [ ] 에이전트 수가 실제로 필요한 최소치인지 검토했다
- [ ] 오케스트레이터 실패 시 폴백 처리를 구현했다

## 처음 질문으로 돌아가기

**오케스트레이터 vs 피어투피어 패턴 언제?** 오케스트레이터 패턴은 명확한 작업 흐름이 있을 때, 피어투피어는 에이전트들이 유연하게 협력해야 할 때 적합합니다.

**에이전트 간 통신 구조는?** 메시지 버스(Message Bus) 패턴으로 발신자와 수신자를 분리하면 에이전트 추가/제거가 쉬워집니다.

**공유 상태 안전 접근은?** 읽기/쓰기에 락을 걸거나, 이벤트 소싱 패턴으로 상태 변경을 직렬화합니다.

**멀티 에이전트 디버깅이 어려운 이유는?** 여러 에이전트가 동시에 실행되고 상호작용하기 때문입니다. 모든 메시지와 상태 변경을 로깅하는 것이 유일한 해결책입니다.

**에이전트를 많이 쓸수록 좋은가요?** 아닙니다. 에이전트가 늘어날수록 통신 오버헤드, 조율 복잡도, 디버깅 난이도가 증가합니다. 단순한 작업은 단일 에이전트가 더 효율적입니다.

## 정리

멀티 에이전트 시스템은 복잡한 작업을 전문화된 에이전트들이 협력해 처리하는 구조입니다. 역할 분리, 메시지 통신, 공유 상태 관리, 전체 로깅이 핵심입니다. 바이브코딩에서 단일 에이전트의 품질 한계를 느낄 때 멀티 에이전트를 고려하되, 필요한 최소한의 에이전트로 시작하는 것이 좋습니다.

다음 글에서는 에이전트 시스템의 품질을 측정하는 **에이전트 평가**를 다룹니다.

## 참고 자료

- [AI Agent 기초 원문: 멀티 에이전트 시스템](../ko/06-multi-agent-systems.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. **바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템 (현재 글)**
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: Multi-Agent, Orchestrator, 바이브코딩, Vibe Coding, Message Bus
