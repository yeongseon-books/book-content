---
title: Feedback Loop — 실패를 고치게 만드는 반복 구조
series: harness-engineering-101
episode: 7
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Feedback
- Reflection
last_reviewed: '2026-05-03'
seo_description: Agent는 한 번에 성공하지 못합니다. Feedback Loop는 실패한 결과를 다시 Agent에게 돌려주어 스스로
  고치게 만드는 반복…
---

# Feedback Loop — 실패를 고치게 만드는 반복 구조

> Harness Engineering 101 시리즈 (7/10)

Agent는 한 번에 성공하지 못합니다. Feedback Loop는 실패한 결과를 다시 Agent에게 돌려주어 스스로 고치게 만드는 반복 구조입니다.

---

![Feedback Loop - 실패를 고치게 만드는 반복 구조](../../assets/harness-engineering-101/07/07-01-feedback-loops-building-structures-that.ko.png)

*Feedback Loop - 실패를 고치게 만드는 반복 구조*

## 한 번에 성공하는 Agent는 없습니다

Agent는 첫 시도에서 자주 실패합니다. 잘못된 도구를 호출하고, 인자를 틀리고, 형식이 맞지 않는 출력을 만듭니다. 이 실패를 어떻게 처리하느냐가 production 품질을 결정합니다.

가장 나쁜 패턴은 실패를 그대로 사용자에게 돌려주는 것입니다. 두 번째로 나쁜 패턴은 같은 호출을 그대로 재시도하는 것입니다. 좋은 패턴은 실패의 원인을 Agent에게 피드백으로 돌려서 다음 시도를 개선하게 만드는 것입니다.

Feedback Loop는 실패를 Agent의 학습 신호로 변환하는 구조입니다. 이번 글에서는 retry vs reflect의 차이, 피드백의 구성, 그리고 무한 루프 방지를 다룹니다.

---

## Retry와 Reflect의 차이

![Retry와 Reflect의 차이](../../assets/harness-engineering-101/07/07-02-retry-vs-reflect.ko.png)

*Retry와 Reflect의 차이*
실패에 대한 두 가지 응답.

**Retry**: 같은 입력으로 다시 시도. 일시적 오류 (네트워크, 타임아웃, rate limit)에 적합.

**Reflect**: 실패 원인을 Agent에게 알려주고 새 시도를 유도. 추론 오류 (잘못된 인자, 형식 위반)에 적합.

두 전략은 다른 도구입니다. retry로 풀어야 할 문제에 reflect를 쓰면 비용이 폭발합니다. reflect가 필요한 문제에 retry를 쓰면 영원히 실패합니다.

```python
from dataclasses import dataclass
from enum import Enum

class FailureMode(Enum):
    TRANSIENT = "transient"  # 재시도하면 풀림 (네트워크, rate limit)
    DETERMINISTIC = "deterministic"  # 다시 시도해도 같은 결과
    REASONING = "reasoning"  # Agent가 다른 시도를 해야 함

@dataclass
class FailureClassification:
    mode: FailureMode
    feedback: str  # Agent에게 줄 메시지 (reflect 시)
    retry_after: float = 0.0  # backoff 시간 (retry 시)

def classify_failure(error: Exception) -> FailureClassification:
    if isinstance(error, TimeoutError):
        return FailureClassification(FailureMode.TRANSIENT, "", retry_after=1.0)
    if isinstance(error, ToolError) and error.code == ErrorCode.RATE_LIMITED:
        return FailureClassification(FailureMode.TRANSIENT, "", retry_after=5.0)
    if isinstance(error, ToolError) and error.code == ErrorCode.INVALID_INPUT:
        return FailureClassification(FailureMode.REASONING, error.to_agent_message())
    if isinstance(error, PolicyViolation):
        return FailureClassification(FailureMode.REASONING, f"Policy violation: {error}. Try a different approach.")
    return FailureClassification(FailureMode.DETERMINISTIC, str(error))
```

분류가 첫 단계입니다. 분류가 없으면 모든 실패에 같은 전략을 쓰게 됩니다.

---

## Reflect의 구성

Agent에게 주는 피드백은 정보가 많을수록 좋지 않습니다. 무엇이 틀렸는지, 왜 틀렸는지, 다음에 어떻게 시도할지의 세 가지에 집중합니다.

```python
@dataclass
class ReflectMessage:
    """실패에서 새 시도로 가는 다리."""
    attempt_number: int
    failed_action: str  # 무엇을 시도했는가
    failure_reason: str  # 왜 실패했는가
    suggested_change: str  # 다음에 어떻게 다르게 할 것인가
    constraint: str  # 다시 같은 실수를 안 하게 하는 제약

    def to_prompt(self) -> str:
        return f"""Attempt #{self.attempt_number} failed.

What you tried: {self.failed_action}
Why it failed: {self.failure_reason}
What to try next: {self.suggested_change}
Constraint for next attempt: {self.constraint}

Now produce a new attempt that satisfies the constraint."""

# 예시
msg = ReflectMessage(
    attempt_number=2,
    failed_action="Called create_user with email='alice'",
    failure_reason="email field requires a valid address (must contain @)",
    suggested_change="Provide the full email like alice@example.com",
    constraint="email must match RFC 5322 format",
)
```

피드백에 "다시 시도해 봐"만 있으면 Agent는 같은 실수를 반복합니다. 구체적인 제약이 있어야 행동이 바뀝니다.

---

## 무한 루프 방지

![무한 루프 방지](../../assets/harness-engineering-101/07/07-03-preventing-infinite-loops.ko.png)

*무한 루프 방지*
Reflect 루프는 무한히 돌 수 있습니다. Agent가 같은 실수를 반복하거나, 새 실수와 기존 실수 사이를 진동할 수 있습니다. 세 가지 안전장치가 필요합니다.

**1. Max attempts**: 최대 시도 횟수 제한. 보통 3~5회.

**2. Cumulative cost limit**: 누적 토큰/비용 상한 (Constraint Harness의 ResourceMeter 재사용).

**3. Repetition detection**: 같은 종류의 실패가 N번 반복되면 escalate.

```python
from collections import Counter
from dataclasses import dataclass, field

@dataclass
class FeedbackLoop:
    """retry/reflect 루프를 안전하게 관리합니다."""
    max_attempts: int = 5
    max_repetitions: int = 2  # 같은 실패 코드가 N번 반복되면 중단
    attempts: int = 0
    failure_history: list[FailureClassification] = field(default_factory=list)

    def should_continue(self, latest: FailureClassification) -> bool:
        self.attempts += 1
        self.failure_history.append(latest)

        if self.attempts >= self.max_attempts:
            return False

        # 같은 종류의 실패가 반복되면 중단
        recent_modes = Counter(f.mode for f in self.failure_history[-3:])
        if any(count >= self.max_repetitions + 1 for count in recent_modes.values()):
            return False

        return True

    def escalate(self) -> dict:
        """루프가 끝났을 때 escalation payload 생성."""
        return {
            "status": "escalated",
            "attempts": self.attempts,
            "failure_history": [{"mode": f.mode.value, "feedback": f.feedback[:200]} for f in self.failure_history],
            "recommended_action": "human_review",
        }

def run_with_feedback(agent, task, loop: FeedbackLoop) -> dict:
    """피드백 루프로 task를 실행합니다."""
    while True:
        try:
            return agent.run(task)
        except Exception as e:
            classification = classify_failure(e)
            if not loop.should_continue(classification):
                return loop.escalate()

            if classification.mode == FailureMode.TRANSIENT:
                import time
                time.sleep(classification.retry_after)
            elif classification.mode == FailureMode.REASONING:
                task = task.with_feedback(classification.feedback)
            else:
                return loop.escalate()
```

`escalate`는 사람에게 넘기는 출구입니다. 루프가 풀지 못하는 문제는 사람이 풀어야 합니다 (다음 글의 Approval Gate 주제).

---

## Self-Critique 패턴

Agent가 자신의 출력을 직접 비판하게 만드는 패턴입니다. 외부 검증보다 약하지만 검증 도구가 없을 때 유용합니다.

```python
def self_critique(agent, draft: str, criteria: list[str]) -> tuple[bool, str]:
    """Agent에게 자신의 draft를 검토하게 합니다."""
    critique_prompt = f"""Review the following draft against these criteria.

Criteria:
{chr(10).join(f'- {c}' for c in criteria)}

Draft:
{draft}

Respond in JSON:
{{
  "passes_all": true/false,
  "violations": ["criterion that failed: reason"],
  "suggested_fix": "concrete change to make"
}}"""
    response = agent.complete(critique_prompt)
    parsed = parse_json(response)
    return parsed["passes_all"], parsed.get("suggested_fix", "")

def generate_with_critique(agent, prompt: str, criteria: list[str], max_rounds: int = 3) -> str:
    """draft → critique → revise를 반복합니다."""
    draft = agent.complete(prompt)
    for _ in range(max_rounds):
        passes, fix = self_critique(agent, draft, criteria)
        if passes:
            return draft
        draft = agent.complete(f"{prompt}\n\nPrevious draft:\n{draft}\n\nApply this fix: {fix}")
    return draft
```

Self-critique는 두 가지 위험이 있습니다. (1) Agent가 자신의 실수를 못 봅니다 (false positive). (2) 매 턴마다 비용이 두 배 이상 듭니다. 외부 검증이 가능한 곳은 외부 검증을 우선합니다.

---

## Failure Memory

![Failure memory](../../assets/harness-engineering-101/07/07-04-failure-memory.ko.png)

*Failure memory*
같은 task가 여러 번 실행될 때, 과거의 실패를 기억하면 같은 실수를 줄일 수 있습니다. Failure memory는 task별로 어떤 접근이 실패했는지를 누적합니다.

```python
from datetime import datetime
import json
from pathlib import Path

@dataclass
class FailureRecord:
    task_type: str
    failed_approach: str
    failure_reason: str
    timestamp: str
    fixed_in_next_attempt: bool

class FailureMemory:
    """task type별 실패 기록을 누적합니다."""

    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.records: list[FailureRecord] = self._load()

    def _load(self) -> list[FailureRecord]:
        if not self.store_path.exists():
            return []
        data = json.loads(self.store_path.read_text())
        return [FailureRecord(**r) for r in data]

    def add(self, record: FailureRecord) -> None:
        self.records.append(record)
        self.store_path.write_text(json.dumps([r.__dict__ for r in self.records], indent=2))

    def warnings_for(self, task_type: str, recent: int = 5) -> list[str]:
        """이 task type에서 최근 실패한 접근의 경고."""
        relevant = [r for r in self.records if r.task_type == task_type][-recent:]
        return [f"Previously failed: {r.failed_approach} (reason: {r.failure_reason})" for r in relevant]
```

Agent의 첫 시도 프롬프트에 failure_memory의 경고를 포함시키면, 과거 실수를 피하는 방향으로 시작합니다. 이는 학습 없이도 시간이 지날수록 품질이 올라가게 만듭니다.

---

## Common Mistakes

**1. 모든 실패를 retry로 풀려고 합니다.**
추론 오류는 retry로 안 풀립니다. 분류 후 reflect를 사용합니다.

**2. Reflect 메시지가 너무 일반적입니다.**
"다시 시도해 봐"는 정보가 0입니다. What/Why/How와 구체적 제약을 포함합니다.

**3. 무한 루프 방지가 없습니다.**
max attempts, cost limit, repetition detection이 모두 없으면 한 task가 비용을 폭주시킵니다.

**4. Escalation 경로가 없습니다.**
루프가 풀지 못하는 문제는 사람에게 가야 합니다. 자동 retry만 있고 escalate가 없으면 실패가 사용자에게 그대로 갑니다.

**5. Failure memory를 안 만듭니다.**
같은 실수를 매번 새로 만나는 Agent는 시간이 지나도 좋아지지 않습니다. 실패 기록은 무료에 가까운 학습 신호입니다.

---

## 핵심 요약

- 한 번에 성공하는 Agent는 없습니다. 실패를 다음 시도의 학습 신호로 만드는 것이 Feedback Loop의 본질입니다.
- 실패는 transient, reasoning, deterministic으로 분류한 후 retry vs reflect를 선택합니다.
- Reflect 메시지는 What/Why/How와 구체적 제약을 포함해야 Agent의 행동이 바뀝니다.
- 무한 루프 방지는 max attempts, cost limit, repetition detection의 세 안전장치로 합니다.
- Failure memory로 task type별 과거 실수를 다음 시도의 프롬프트에 포함시키면 시간이 지날수록 품질이 올라갑니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- [Constraint Harness — 규칙, 경계, 금지 행동 정의하기](./04-constraint-harness.md)
- [Tool Harness — Agent가 사용할 도구를 안전하게 설계하기](./05-tool-harness.md)
- [Test Harness — 완료 조건을 테스트로 고정하기](./06-test-harness.md)
- **Feedback Loop — 실패를 고치게 만드는 반복 구조 (현재 글)**
- Approval Gate — 사람 승인이 필요한 지점 설계하기 (예정)
- Observability — Agent 작업을 추적하고 재현하기 (예정)
- Production Harness — 운영 가능한 Agent 작업 환경 만들기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Shinn et al. — Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Madaan et al. — Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651)
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph — Reflection Patterns](https://langchain-ai.github.io/langgraph/tutorials/reflection/reflection/)
