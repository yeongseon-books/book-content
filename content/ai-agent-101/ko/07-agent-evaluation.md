---
title: Agent 평가
series: ai-agent-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Evaluation
- Testing
- Metrics
last_reviewed: '2026-05-12'
seo_description: agent 평가를 성공률, trajectory, 비용 관점에서 정리합니다.
---

# Agent 평가

agent를 만드는 일보다 더 어려운 일은 agent가 실제로 잘 작동하는지 판단하는 일입니다. 단순한 텍스트 생성 시스템이라면 답변 품질 중심으로 평가해도 되지만, agent는 도구 사용과 반복 루프와 실패 복구까지 포함하므로 훨씬 많은 관점이 필요합니다.

예를 들어 최종 답이 맞았더라도 불필요한 tool call을 다섯 번 더 했을 수 있고, 같은 작업을 다른 모델에서는 절반 비용으로 끝낼 수도 있습니다. 반대로 최종 답이 틀렸더라도 실제 문제는 reasoning이 아니라 잘못된 tool choice였을 수 있습니다.

그래서 agent 평가는 하나의 점수보다 분해된 지표가 중요합니다. 최종 성공률, tool-call accuracy, trajectory quality, cost, latency를 나눠 봐야 어디를 고쳐야 하는지 보입니다.

이 글은 AI Agent 101 시리즈의 일곱 번째 글입니다.

이 글에서는 agent 평가를 정답 채점이 아니라 시스템 진단 프레임워크로 이해하겠습니다.

## 이 글에서 다룰 문제

- agent 평가는 일반적인 LLM 평가와 무엇이 다를까요?
- final answer가 맞아도 실패로 봐야 하는 trajectory는 어떤 경우일까요?
- tool-call accuracy는 어떤 기준으로 측정해야 할까요?
- end-to-end 테스트와 개별 컴포넌트 테스트는 어디서 역할이 갈릴까요?
- 비용과 latency를 품질 지표와 함께 읽으려면 어떤 구조가 필요할까요?

## 왜 이 글이 중요한가

평가 체계가 없으면 agent 개선은 감각에 의존하게 됩니다. prompt를 조금 바꾸고, 모델을 바꾸고, tool description을 다듬었을 때 실제로 무엇이 좋아졌는지 말할 수 없게 됩니다. 이 상태에서는 운영 최적화도 거의 불가능합니다.

또한 agent는 실패 지점이 여러 곳입니다. reasoning이 틀릴 수도 있고, tool을 잘못 고를 수도 있고, 올바른 tool을 잘못된 인자로 호출할 수도 있고, 중간 결과는 맞았지만 synthesis에서 틀릴 수도 있습니다. 평가를 분해하지 않으면 서로 다른 실패가 하나의 "나쁜 결과"로 뭉개집니다.

현업에서는 특히 trajectory를 보는 습관이 중요합니다. 성공률만 보면 비슷해 보여도 어떤 버전은 평균 두 step 만에 끝내고, 다른 버전은 여섯 step이 걸릴 수 있습니다. 결국 같은 정확도라면 더 짧고 설명 가능한 경로가 운영 친화적입니다.

## Agent 평가를 이해하는 가장 좋은 방법: 정답 채점이 아니라 실행 경로 진단으로 보는 것입니다

agent 평가는 "맞혔는가"만 묻는 시험이 아닙니다. 어떤 경로로, 어떤 도구를, 어떤 비용으로, 어느 정도 안정적으로 목표에 도달했는가를 묻는 진단 과정에 가깝습니다. 이 관점이 있어야 개선 포인트가 보입니다.

예를 들어 성공률이 80%인 agent가 있다고 해도 의미가 부족합니다. 어떤 실패는 tool schema 수정으로 해결될 수 있고, 어떤 실패는 workflow 패턴 교체가 필요하며, 어떤 실패는 human approval을 추가해야 해결됩니다. 점수 하나만으로는 이 차이가 드러나지 않습니다.

실무에서 강한 팀일수록 최종 답보다 trajectory와 tool telemetry를 먼저 봅니다. 왜 실패했는지 설명할 수 있어야 다음 실험이 작아지고 빨라지기 때문입니다.

> 좋은 agent 평가는 모델의 정답률을 재는 것이 아니라, 시스템이 어떤 경로와 비용으로 목표에 도달했는지 설명 가능하게 만드는 것입니다.

## 핵심 개념

### 먼저 end-to-end 성공률을 봅니다

```python
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class TestCase:
    """A test case."""
    task_id: str
    user_input: str
    expected_outcome: dict
    success_criteria: Callable[[dict], bool]

@dataclass
class EvaluationResult:
    """An evaluation result."""
    task_id: str
    success: bool
    actual_outcome: dict
    error: str = ""

def evaluate_success_rate(
    agent,
    test_cases: List[TestCase]
) -> dict:
    """Measure task success rate."""
    results: List[EvaluationResult] = []

    for test in test_cases:
        try:
            outcome = agent.run(test.user_input)
            success = test.success_criteria(outcome)
            results.append(EvaluationResult(
                task_id=test.task_id,
                success=success,
                actual_outcome=outcome
            ))
        except Exception as e:
            results.append(EvaluationResult(
                task_id=test.task_id,
                success=False,
                actual_outcome={},
                error=str(e)
            ))

    total = len(results)
    succeeded = sum(1 for r in results if r.success)
    return {
        "success_rate": succeeded / total if total else 0.0,
        "total": total,
        "succeeded": succeeded,
        "failed_cases": [r for r in results if not r.success]
    }
```

end-to-end 성공률은 가장 직관적인 출발점입니다. 다만 이것만으로는 왜 성공하거나 실패했는지 알 수 없습니다. 따라서 반드시 하위 지표와 함께 봐야 합니다.

### 비용과 latency는 품질과 함께 읽어야 합니다

```python
@dataclass
class CostMetrics:
    """Cost metrics."""
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    api_calls: int
    estimated_usd: float

class CostTracker:
    """Tracks API call cost."""

    PRICING = {
        "gpt-4": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
        "gpt-4o-mini": {"prompt": 0.15 / 1_000_000, "completion": 0.60 / 1_000_000}
    }

    def __init__(self):
        self.metrics = CostMetrics(0, 0, 0, 0, 0.0)

    def record(self, model: str, prompt_tokens: int, completion_tokens: int):
        """Record an API call."""
        self.metrics.api_calls += 1
        self.metrics.prompt_tokens += prompt_tokens
        self.metrics.completion_tokens += completion_tokens
        self.metrics.total_tokens += prompt_tokens + completion_tokens

        if model in self.PRICING:
            cost = (
                prompt_tokens * self.PRICING[model]["prompt"] +
                completion_tokens * self.PRICING[model]["completion"]
            )
            self.metrics.estimated_usd += cost

    def report(self) -> dict:
        return {
            "api_calls": self.metrics.api_calls,
            "total_tokens": self.metrics.total_tokens,
            "estimated_usd": round(self.metrics.estimated_usd, 4)
        }
```

기존 시스템에서 `gpt-3.5-turbo`를 계속 써야 한다면 legacy 모델로 보고 계산해야 합니다. 현재 legacy 단가는 입력 1M tokens당 $0.50, 출력 1M tokens당 $1.50이며, 새 저비용 예시는 `gpt-4o-mini`를 기본값으로 두는 편이 더 적절합니다.

```python
import time
from contextlib import contextmanager

@contextmanager
def measure_latency():
    """Latency-measuring context manager."""
    start = time.time()
    metrics = {"steps": []}
    yield metrics
    metrics["total_seconds"] = time.time() - start

def record_step(metrics: dict, step_name: str, duration: float):
    metrics["steps"].append({"name": step_name, "seconds": duration})
```

정확도만 보면 괜찮아 보여도 작업당 비용이 지나치게 높거나 step latency가 길면 배포하기 어렵습니다. 따라서 평가표에는 success와 함께 api_calls, total_tokens, total_seconds가 반드시 있어야 합니다.

### trajectory를 기록해야 개선이 가능합니다

```python
from datetime import datetime
from typing import Any

@dataclass
class TrajectoryStep:
    """A single step in a trajectory."""
    step_number: int
    action: str           # "think", "tool_call", "respond"
    input: Any
    output: Any
    timestamp: datetime
    duration_ms: int

@dataclass
class Trajectory:
    """The full path."""
    task_id: str
    steps: List[TrajectoryStep]
    final_answer: str
    success: bool

class TrajectoryRecorder:
    """Records trajectories."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.steps: List[TrajectoryStep] = []
        self._step_counter = 0
```

trajectory를 남기면 같은 실패도 성격을 나눌 수 있습니다. 첫 tool choice가 틀렸는지, 중간 observation 해석이 틀렸는지, final synthesis에서 어긋났는지 구분할 수 있기 때문입니다. 특히 multi-agent나 long workflow에서는 이 기록이 없으면 원인 분석이 거의 불가능합니다.

### 평가셋은 실제 운영 요청을 닮아야 합니다

- happy path뿐 아니라 invalid input과 timeout 상황을 포함합니다.
- tool ambiguity가 있는 요청을 별도로 만듭니다.
- follow-up 질문과 memory 의존 요청을 섞습니다.
- 비용이 큰 장문 요청과 짧은 요청을 모두 넣습니다.
- 최종 정답뿐 아니라 허용 경로와 금지 경로도 문서화합니다.

## 흔히 헷갈리는 지점

- final answer만 맞으면 성공이라고 보기 쉽지만, 불필요한 step 폭증은 운영 실패 신호일 수 있습니다.
- benchmark 점수가 높으면 production readiness도 높다고 생각하기 쉽지만, 실제 운영 입력은 더 지저분합니다.
- tool accuracy와 task success를 같은 지표로 섞으면 어디를 고쳐야 하는지 알기 어렵습니다.
- 평가를 한 번만 돌리면 충분하다고 보기 쉽지만, prompt와 tool이 바뀔 때마다 회귀 검사가 필요합니다.
- 사람의 인상 평가만으로도 충분하다고 생각하기 쉽지만, trajectory가 남지 않으면 재현이 안 됩니다.

## 운영 체크리스트

- [ ] end-to-end success, cost, latency, tool accuracy를 분리해서 측정하는가
- [ ] trajectory를 저장해 실패 원인을 사후 분석할 수 있는가
- [ ] happy path 외에 timeout, ambiguity, invalid input 케이스가 포함되어 있는가
- [ ] 프롬프트나 도구 변경 시 자동 회귀 평가를 돌리는가
- [ ] 품질 개선과 비용 최적화를 함께 보는 대시보드가 있는가

## 정리

agent 평가는 단순한 정답 채점이 아닙니다. 어떤 도구를 어떤 순서로 불렀는지, 어디서 실패했는지, 얼마의 비용과 시간이 들었는지까지 포함한 시스템 진단입니다. 이 관점이 있어야 개선 실험이 작아지고 빨라집니다.

좋은 평가 체계는 모델과 프롬프트를 비교하는 데서 끝나지 않습니다. tool schema, workflow, memory, retry 정책까지 모두 같은 프레임 안에서 비교할 수 있어야 합니다. 그래야 "왜 좋아졌는가"를 설명할 수 있습니다.

다음 글에서는 이렇게 발견한 실패를 어떻게 처리하고 시스템 신뢰성을 높일지 살펴봅니다. 결국 평가가 문제를 드러내면, reliability 설계가 그 문제를 운영 가능한 수준으로 낮춰야 하기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- [Agent Workflow 설계](./04-agent-workflow-design.md)
- [Memory와 State](./05-memory-and-state.md)
- [Multi-Agent 시스템](./06-multi-agent-systems.md)
- **Agent 평가 (현재 글)**
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OpenAI Evals design guide](https://platform.openai.com/docs/guides/evals)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangSmith documentation](https://docs.smith.langchain.com/)
- [DeepEval documentation](https://docs.confident-ai.com/)

### 관련 시리즈

- [AI Evaluation 101](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md)
- [LangGraph 101 - trajectory와 상태 추적](../../langgraph-101/ko/02-state-and-checkpoints.md)

Tags: AI Agent, LLM, Tool Use, Python
