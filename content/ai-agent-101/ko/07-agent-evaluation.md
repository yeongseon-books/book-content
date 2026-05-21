---
title: "AI Agent 101 (7/10): Agent 평가"
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

# AI Agent 101 (7/10): Agent 평가

agent를 만드는 일보다 더 어려운 일은 agent가 실제로 잘 작동하는지 판단하는 일입니다. 단순한 텍스트 생성 시스템이라면 답변 품질 중심으로 평가해도 되지만, agent는 도구 사용과 반복 루프와 실패 복구까지 포함하므로 훨씬 많은 관점이 필요합니다.

예를 들어 최종 답이 맞았더라도 불필요한 tool call을 다섯 번 더 했을 수 있고, 같은 작업을 다른 모델에서는 절반 비용으로 끝낼 수도 있습니다. 반대로 최종 답이 틀렸더라도 실제 문제는 reasoning이 아니라 잘못된 tool choice였을 수 있습니다.

그래서 agent 평가는 하나의 점수보다 분해된 지표가 중요합니다. 최종 성공률, tool-call accuracy, trajectory quality, cost, latency를 나눠 봐야 어디를 고쳐야 하는지 보입니다.

이 글은 AI Agent 101 시리즈의 일곱 번째 글입니다.

이 글에서는 agent 평가를 정답 채점이 아니라 시스템 진단 프레임워크로 이해하겠습니다.

## 먼저 던지는 질문

- agent 평가는 왜 최종 답변 채점만으로 부족할까요?
- trajectory, tool-call accuracy, end-to-end success는 각각 어떤 실패를 잡아낼까요?
- 운영 전 eval set에는 어떤 실제 요청과 실패 사례를 넣어야 할까요?

## 큰 그림

![평가 신호 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/07/07-01-evaluation-signal-path.ko.png)

*평가 신호 흐름*

이 그림에서는 사용자 요청에서 tool 호출, 중간 경로, 최종 결과까지 평가 신호가 흐르는 지점을 봅니다. agent 평가는 답이 맞았는지뿐 아니라 그 답에 도달한 경로가 안전하고 재현 가능한지도 봐야 합니다.

> Agent 평가는 정답 채점이 아니라, 실행 경로와 도구 사용과 최종 결과를 함께 진단하는 일입니다.

## 왜 이 글이 중요한가

평가 체계가 없으면 agent 개선은 감각에 의존하게 됩니다. prompt를 조금 바꾸고, 모델을 바꾸고, tool description을 다듬었을 때 실제로 무엇이 좋아졌는지 말할 수 없게 됩니다. 이 상태에서는 운영 최적화도 거의 불가능합니다.

또한 agent는 실패 지점이 여러 곳입니다. reasoning이 틀릴 수도 있고, tool을 잘못 고를 수도 있고, 올바른 tool을 잘못된 인자로 호출할 수도 있고, 중간 결과는 맞았지만 synthesis에서 틀릴 수도 있습니다. 평가를 분해하지 않으면 서로 다른 실패가 하나의 "나쁜 결과"로 뭉개집니다.

현업에서는 특히 trajectory를 보는 습관이 중요합니다. 성공률만 보면 비슷해 보여도 어떤 버전은 평균 두 step 만에 끝내고, 다른 버전은 여섯 step이 걸릴 수 있습니다. 결국 같은 정확도라면 더 짧고 설명 가능한 경로가 운영 친화적입니다.

## 핵심 관점

agent 평가는 "맞혔는가"만 묻는 시험이 아닙니다. 어떤 경로로, 어떤 도구를, 어떤 비용으로, 어느 정도 안정적으로 목표에 도달했는가를 묻는 진단 과정에 가깝습니다. 이 관점이 있어야 개선 포인트가 보입니다.

예를 들어 성공률이 80%인 agent가 있다고 해도 의미가 부족합니다. 어떤 실패는 tool schema 수정으로 해결될 수 있고, 어떤 실패는 workflow 패턴 교체가 필요하며, 어떤 실패는 human approval을 추가해야 해결됩니다. 점수 하나만으로는 이 차이가 드러나지 않습니다.

실무에서 강한 팀일수록 최종 답보다 trajectory와 tool telemetry를 먼저 봅니다. 왜 실패했는지 설명할 수 있어야 다음 실험이 작아지고 빨라지기 때문입니다.

> 좋은 agent 평가는 모델의 정답률을 재는 것이 아니라, 시스템이 어떤 경로와 비용으로 목표에 도달했는지 설명 가능하게 만드는 것입니다.

## 핵심 개념

### 먼저 end-to-end 성공률을 봅니다

```python
from dataclasses import dataclass
from collections.abc import Callable
from typing import List

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

## 실전 설계 보강

### 평가셋은 질문 모음이 아니라 실패 가설 모음입니다

agent 평가를 제대로 하려면 샘플을 무작위로 모으는 대신 실패 가설 중심으로 분류해야 합니다. 예를 들어 도구 미호출, 잘못된 도구 선택, 과잉 반복, 위험 정책 위반 같은 가설을 먼저 정하고 케이스를 수집하는 방식입니다.

| 평가 축 | 설명 | 예시 metric |
| --- | --- | --- |
| 과업 달성 | 목표를 실제로 완료했는가 | task_success_rate |
| 경로 품질 | 불필요 step이 많은가 | avg_steps, detour_rate |
| 도구 적합성 | 올바른 도구를 골랐는가 | tool_precision |
| 안전성 | 금지 행동을 피했는가 | policy_violation_rate |

### 실행 로그 기반 채점 예시

```python
def score_run(run: dict) -> dict:
    success = run.get("stop_reason") == "goal_achieved"
    steps = run.get("steps", 0)
    violations = len(run.get("policy_violations", []))
    return {
        "task_success": 1 if success else 0,
        "step_efficiency": max(0.0, 1.0 - max(0, steps - 4) * 0.1),
        "safety": 1 if violations == 0 else 0,
    }
```

이처럼 단순한 채점 함수라도 있으면 모델/프롬프트/도구 변경의 영향을 수치로 비교할 수 있습니다.

### 오프라인 + 온라인 평가 분리

```text
오프라인: 고정 평가셋으로 회귀 테스트, 배포 전 품질 게이트
온라인: 실제 트래픽 샘플링, 사용자 피드백/실패 리포트 반영
```

오프라인만 보면 실제 사용자 다양성이 반영되지 않고, 온라인만 보면 회귀를 놓치기 쉽습니다. 두 계층을 분리해 운영해야 품질이 장기적으로 유지됩니다.

### 평가 대시보드 권장 항목

| 지표 | 목표 예시 |
| --- | --- |
| task_success_rate | 0.85 이상 |
| policy_violation_rate | 0.5% 이하 |
| p95_latency | 8초 이하 |
| avg_cost_per_run | 기준 예산 이하 |

평가 체계가 있으면 "좋아진 것 같다"가 아니라 "어떤 축이 얼마나 바뀌었는가"로 의사결정할 수 있습니다.

## 심화 운영 노트

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

### 배포 체크 항목

- 모델 API 키를 환경 변수와 Secret Manager로 분리했는지 확인합니다.
- `max_steps`, `timeout_ms`, `retry_budget` 기본값이 운영 프로필에 맞는지 검증합니다.
- 장애 시 fallback 응답 문구가 사용자에게 과장된 확신을 주지 않는지 점검합니다.
- 알람 임계치(`error_rate`, `p95_latency`, `policy_violation_rate`)를 문서와 코드에서 동일하게 유지합니다.

이 항목은 기능 개발보다 눈에 덜 띄지만, 실제 장애 빈도를 줄이는 데 직접적으로 기여합니다.

### 비용 통제 포인트

| 항목 | 설명 | 권장 기본값 |
| --- | --- | --- |
| max_steps | 1회 실행당 최대 루프 | 4~8 |
| max_tool_calls | 도구 호출 상한 | 3~6 |
| input_token_budget | 입력 토큰 예산 | 서비스별 정책 |
| output_token_budget | 출력 토큰 예산 | 서비스별 정책 |

비용 통제는 성능 최적화 이후에 붙이는 부가기능이 아닙니다. 처음부터 실행 예산을 고정해야 사용량 급증 시 서비스가 안정적으로 유지됩니다.

### 품질 회귀를 막는 CI 게이트 예시

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_ko.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

배포 파이프라인에서 최소 품질 게이트를 자동화하면 "우연히 좋아 보이는 빌드"가 운영으로 유입되는 일을 줄일 수 있습니다.

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

### 배포 체크 항목

- 모델 API 키를 환경 변수와 Secret Manager로 분리했는지 확인합니다.
- `max_steps`, `timeout_ms`, `retry_budget` 기본값이 운영 프로필에 맞는지 검증합니다.
- 장애 시 fallback 응답 문구가 사용자에게 과장된 확신을 주지 않는지 점검합니다.
- 알람 임계치(`error_rate`, `p95_latency`, `policy_violation_rate`)를 문서와 코드에서 동일하게 유지합니다.

이 항목은 기능 개발보다 눈에 덜 띄지만, 실제 장애 빈도를 줄이는 데 직접적으로 기여합니다.

### 비용 통제 포인트

| 항목 | 설명 | 권장 기본값 |
| --- | --- | --- |
| max_steps | 1회 실행당 최대 루프 | 4~8 |
| max_tool_calls | 도구 호출 상한 | 3~6 |
| input_token_budget | 입력 토큰 예산 | 서비스별 정책 |
| output_token_budget | 출력 토큰 예산 | 서비스별 정책 |

비용 통제는 성능 최적화 이후에 붙이는 부가기능이 아닙니다. 처음부터 실행 예산을 고정해야 사용량 급증 시 서비스가 안정적으로 유지됩니다.

### 품질 회귀를 막는 CI 게이트 예시

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_ko.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

배포 파이프라인에서 최소 품질 게이트를 자동화하면 "우연히 좋아 보이는 빌드"가 운영으로 유입되는 일을 줄일 수 있습니다.

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

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

## 처음 질문으로 돌아가기

- **agent 평가는 왜 최종 답변 채점만으로 부족할까요?**
  - agent는 중간에 잘못된 도구를 부르고도 그럴듯한 답을 만들 수 있습니다. 최종 답변만 보면 비용, 위험, 우연한 성공을 놓칩니다.
- **trajectory, tool-call accuracy, end-to-end success는 각각 어떤 실패를 잡아낼까요?**
  - trajectory는 경로 낭비와 잘못된 순서를, tool-call accuracy는 도구 선택과 인자 오류를, end-to-end success는 사용자 관점의 완료 여부를 잡습니다.
- **운영 전 eval set에는 어떤 실제 요청과 실패 사례를 넣어야 할까요?**
  - 실제 상위 요청, 경계 조건, tool 실패, ambiguous input, 비용이 커지는 반복 사례를 eval set에 넣어야 운영 위험을 먼저 볼 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent 101 (1/10): AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use 기초](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow 설계](./04-agent-workflow-design.md)
- [AI Agent 101 (5/10): Memory와 State](./05-memory-and-state.md)
- [AI Agent 101 (6/10): Multi-Agent 시스템](./06-multi-agent-systems.md)
- **AI Agent 101 (7/10): Agent 평가 (현재 글)**
- AI Agent 101 (8/10): 에러 처리와 안정성 (예정)
- AI Agent 101 (9/10): 운영 (예정)
- AI Agent 101 (10/10): 첫 Agent 만들기 (예정)

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/ko/07-agent-evaluation)

Tags: AI Agent, LLM, Tool Use, Python
