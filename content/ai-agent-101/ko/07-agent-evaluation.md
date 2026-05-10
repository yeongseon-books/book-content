---
title: Agent 평가
series: ai-agent-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Evaluation
- Testing
- Metrics
last_reviewed: '2026-05-02'
seo_description: Agent를 만드는 것보다 어려운 것이 "이 Agent가 제대로 작동하는지" 평가하는 것입니다.
---

# Agent 평가

> AI Agent 101 시리즈 (7/10)

Agent를 만드는 것보다 어려운 것이 "이 Agent가 제대로 작동하는지" 평가하는 것입니다. 단순 LLM은 응답 품질만 평가하면 되지만, Agent는 도구 호출 정확도, 작업 완료율, 불필요한 단계 수, 비용 효율성 등 여러 지표를 봐야 합니다.

Agent 평가는 크게 세 가지 레벨로 나뉩니다. 개별 도구 호출의 정확성(Tool Use Accuracy), 작업 경로의 효율성(Trajectory Evaluation), 최종 결과의 정확성(End-to-End Success Rate)입니다.

이번 글에서는 Agent 평가 지표, Trajectory 평가 방법, 도구 호출 정확도 측정, 엔드투엔드 테스트 전략, 그리고 벤치마킹 방법을 다룹니다.

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- Agent 평가는 일반 ML 모델 평가와 무엇이 본질적으로 다를까요?
- Trajectory 평가에서 무엇을 보고 성공/실패를 판단해야 할까요?
- 도구 호출 정확도(tool-call accuracy)는 어떻게 측정할까요?
- 엔드투엔드 테스트와 벤치마크는 어디에서 충돌할까요?

<!-- a-grade-intro:end -->

## Agent 평가 지표

Agent 평가는 단순히 "잘 답했는가"가 아닌 여러 차원을 봐야 합니다. 핵심 지표는 다음과 같습니다.

### Task Success Rate (작업 완료율)

Agent가 사용자 요청을 성공적으로 완료한 비율입니다.

```python
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class TestCase:
    """테스트 케이스."""
    task_id: str
    user_input: str
    expected_outcome: dict
    success_criteria: Callable[[dict], bool]

@dataclass
class EvaluationResult:
    """평가 결과."""
    task_id: str
    success: bool
    actual_outcome: dict
    error: str = ""

def evaluate_success_rate(
    agent,
    test_cases: List[TestCase]
) -> dict:
    """Task Success Rate 측정."""
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

# 사용 예시
test_cases = [
    TestCase(
        task_id="weather_seoul",
        user_input="서울 날씨 알려줘",
        expected_outcome={"city": "Seoul", "has_temp": True},
        success_criteria=lambda o: "temperature" in o.get("response", "")
    ),
    TestCase(
        task_id="calc_simple",
        user_input="3 곱하기 4는?",
        expected_outcome={"answer": 12},
        success_criteria=lambda o: "12" in o.get("response", "")
    )
]
metrics = evaluate_success_rate(my_agent, test_cases)
print(f"성공률: {metrics['success_rate']:.1%}")
```

Success Rate는 가장 직관적인 지표지만, "어떻게 성공/실패했는가"는 보여주지 않습니다.

### Cost per Task (작업당 비용)

Agent가 작업 하나를 완료하는 데 든 토큰 비용과 API 호출 횟수입니다.

```python
@dataclass
class CostMetrics:
    """비용 지표."""
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    api_calls: int
    estimated_usd: float

class CostTracker:
    """API 호출 비용 추적."""

    PRICING = {
        "gpt-4": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
        "gpt-3.5-turbo": {"prompt": 0.0015 / 1000, "completion": 0.002 / 1000}
    }

    def __init__(self):
        self.metrics = CostMetrics(0, 0, 0, 0, 0.0)

    def record(self, model: str, prompt_tokens: int, completion_tokens: int):
        """API 호출 기록."""
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

비용 지표는 운영 단계에서 필수입니다. 정확도가 높아도 작업당 $1 이상 들면 비즈니스로 성립하지 않습니다.

### Latency (응답 시간)

사용자 요청부터 최종 응답까지 걸린 시간입니다. Agent는 여러 단계를 거치므로 전체 latency가 길어지기 쉽습니다.

```python
import time
from contextlib import contextmanager

@contextmanager
def measure_latency():
    """Latency 측정 context manager."""
    start = time.time()
    metrics = {"steps": []}
    yield metrics
    metrics["total_seconds"] = time.time() - start

def record_step(metrics: dict, step_name: str, duration: float):
    metrics["steps"].append({"name": step_name, "seconds": duration})

# 사용 예시
with measure_latency() as m:
    t0 = time.time()
    plan = agent.plan(user_input)
    record_step(m, "planning", time.time() - t0)

    t0 = time.time()
    tools_result = agent.execute_tools(plan)
    record_step(m, "tool_calls", time.time() - t0)

    t0 = time.time()
    final = agent.synthesize(tools_result)
    record_step(m, "synthesis", time.time() - t0)

print(f"전체 {m['total_seconds']:.2f}s, 단계별: {m['steps']}")
```

단계별 latency를 측정하면 어디가 병목인지 파악할 수 있습니다.

## Trajectory 평가

Trajectory는 Agent가 시작점에서 목표까지 도달하는 경로입니다. 같은 결과라도 짧고 효율적인 경로가 더 좋은 Trajectory입니다.

### Trajectory 기록

Agent의 모든 단계를 기록하면 사후 분석이 가능합니다.

```python
from datetime import datetime
from typing import Any

@dataclass
class TrajectoryStep:
    """Trajectory의 한 단계."""
    step_number: int
    action: str           # "think", "tool_call", "respond"
    input: Any
    output: Any
    timestamp: datetime
    duration_ms: int

@dataclass
class Trajectory:
    """전체 경로."""
    task_id: str
    steps: List[TrajectoryStep]
    final_answer: str
    success: bool

class TrajectoryRecorder:
    """Trajectory 기록기."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.steps: List[TrajectoryStep] = []
        self._step_counter = 0

    def record(self, action: str, input_data: Any, output_data: Any, duration_ms: int):
        self._step_counter += 1
        self.steps.append(TrajectoryStep(
            step_number=self._step_counter,
            action=action,
            input=input_data,
            output=output_data,
            timestamp=datetime.now(),
            duration_ms=duration_ms
        ))

    def finalize(self, final_answer: str, success: bool) -> Trajectory:
        return Trajectory(
            task_id=self.task_id,
            steps=self.steps,
            final_answer=final_answer,
            success=success
        )
```

### Trajectory 효율성 평가

기록된 Trajectory로 효율성을 평가합니다.

```python
def evaluate_trajectory_efficiency(traj: Trajectory) -> dict:
    """Trajectory 효율성 분석."""
    tool_calls = [s for s in traj.steps if s.action == "tool_call"]
    thinks = [s for s in traj.steps if s.action == "think"]

    # 중복 도구 호출 감지
    tool_signatures = [
        (s.input.get("tool"), str(s.input.get("args")))
        for s in tool_calls
    ]
    duplicate_calls = len(tool_signatures) - len(set(tool_signatures))

    return {
        "total_steps": len(traj.steps),
        "tool_calls": len(tool_calls),
        "thinking_steps": len(thinks),
        "duplicate_tool_calls": duplicate_calls,
        "total_duration_ms": sum(s.duration_ms for s in traj.steps),
        "avg_step_ms": sum(s.duration_ms for s in traj.steps) / len(traj.steps)
            if traj.steps else 0
    }

# 효율성 비교
traj_a = recorder_a.finalize("답변 A", True)
traj_b = recorder_b.finalize("답변 B", True)

eff_a = evaluate_trajectory_efficiency(traj_a)
eff_b = evaluate_trajectory_efficiency(traj_b)
# 같은 답이라도 단계 수가 적은 쪽이 더 효율적
```

Trajectory 평가의 핵심은 "같은 결과라면 더 적은 단계로 도달했는가"입니다.

## 도구 호출 정확도 측정

Agent의 도구 호출은 두 단계로 나뉩니다. (1) 적절한 도구를 골랐는가, (2) 올바른 인자로 호출했는가.

```python
@dataclass
class ToolCallExpectation:
    """기대되는 도구 호출."""
    tool_name: str
    required_args: dict
    optional_args: dict = None

def evaluate_tool_call(
    actual_tool: str,
    actual_args: dict,
    expected: ToolCallExpectation
) -> dict:
    """단일 도구 호출 평가."""
    result = {
        "tool_correct": actual_tool == expected.tool_name,
        "args_correct": True,
        "missing_args": [],
        "wrong_args": []
    }

    for key, expected_val in expected.required_args.items():
        if key not in actual_args:
            result["missing_args"].append(key)
            result["args_correct"] = False
        elif actual_args[key] != expected_val:
            result["wrong_args"].append({
                "key": key,
                "expected": expected_val,
                "actual": actual_args[key]
            })
            result["args_correct"] = False

    return result

# 사용 예시
expected = ToolCallExpectation(
    tool_name="get_weather",
    required_args={"city": "Seoul"}
)
actual_tool = "get_weather"
actual_args = {"city": "Seoul", "unit": "celsius"}
print(evaluate_tool_call(actual_tool, actual_args, expected))
# {'tool_correct': True, 'args_correct': True, ...}
```

전체 테스트셋에서 도구 호출 정확도를 집계하면 Agent 약점을 찾을 수 있습니다.

## 엔드투엔드 테스트

단위 테스트로는 부족합니다. Agent는 여러 컴포넌트의 상호작용 결과이므로 엔드투엔드 시나리오 테스트가 필요합니다.

```python
class E2ETestSuite:
    """엔드투엔드 테스트 모음."""

    def __init__(self, agent):
        self.agent = agent
        self.results = []

    def run_scenario(self, scenario: dict) -> dict:
        """시나리오 한 건 실행."""
        recorder = TrajectoryRecorder(scenario["id"])

        try:
            # 시나리오의 멀티턴 대화 실행
            for turn in scenario["turns"]:
                response = self.agent.chat(turn["user"])

            # 최종 검증
            assertions_passed = all(
                self._check_assertion(response, a)
                for a in scenario["assertions"]
            )
            return {
                "scenario_id": scenario["id"],
                "passed": assertions_passed,
                "trajectory": recorder.finalize(response, assertions_passed)
            }
        except Exception as e:
            return {
                "scenario_id": scenario["id"],
                "passed": False,
                "error": str(e)
            }

    def _check_assertion(self, response: str, assertion: dict) -> bool:
        if assertion["type"] == "contains":
            return assertion["value"] in response
        if assertion["type"] == "not_contains":
            return assertion["value"] not in response
        if assertion["type"] == "regex":
            import re
            return bool(re.search(assertion["pattern"], response))
        return False

# 시나리오 정의
scenario = {
    "id": "booking_flow",
    "turns": [
        {"user": "내일 서울에서 부산 가는 KTX 알려줘"},
        {"user": "오전 시간대로 보여줘"},
        {"user": "첫 번째 걸로 예약해줘"}
    ],
    "assertions": [
        {"type": "contains", "value": "예약 완료"},
        {"type": "contains", "value": "KTX"}
    ]
}
```

엔드투엔드 테스트는 멀티턴 대화, 상태 유지, 도구 체인을 한꺼번에 검증합니다.

## 벤치마킹

표준 벤치마크로 Agent를 다른 시스템과 비교할 수 있습니다.

### 공개 Agent 벤치마크

- **AgentBench** — 8개 환경에서 Agent의 추론/도구 사용 능력 측정
- **WebArena** — 실제 웹사이트에서 작업 완료율 측정
- **GAIA** — 일반 AI Assistant의 실제 문제 해결 능력 평가
- **SWE-bench** — GitHub 이슈 해결 능력 측정 (코드 Agent용)

### 자체 벤치마크 구축

도메인 특화 Agent라면 자체 벤치마크가 필수입니다.

```python
class AgentBenchmark:
    """벤치마크 실행기."""

    def __init__(self, name: str):
        self.name = name
        self.test_cases: List[TestCase] = []
        self.cost_tracker = CostTracker()

    def add_case(self, case: TestCase):
        self.test_cases.append(case)

    def run(self, agent, repeat: int = 3) -> dict:
        """벤치마크 실행. 노이즈 줄이기 위해 반복."""
        all_results = []

        for run_idx in range(repeat):
            for case in self.test_cases:
                start = time.time()
                outcome = agent.run(case.user_input)
                duration = time.time() - start

                all_results.append({
                    "run": run_idx,
                    "case_id": case.task_id,
                    "success": case.success_criteria(outcome),
                    "duration_seconds": duration
                })

        # 집계
        cases = {c.task_id for c in self.test_cases}
        per_case = {}
        for case_id in cases:
            case_runs = [r for r in all_results if r["case_id"] == case_id]
            per_case[case_id] = {
                "success_rate": sum(1 for r in case_runs if r["success"]) / len(case_runs),
                "avg_duration": sum(r["duration_seconds"] for r in case_runs) / len(case_runs)
            }

        return {
            "benchmark": self.name,
            "agent": agent.__class__.__name__,
            "total_runs": len(all_results),
            "overall_success_rate": sum(1 for r in all_results if r["success"]) / len(all_results),
            "per_case": per_case,
            "cost": self.cost_tracker.report()
        }
```

벤치마크 결과는 Agent를 개선할 때마다 회귀 검증의 기준이 됩니다.

## 흔한 실수 5가지

### 실수 1: Success Rate만 보고 판단

성공률 90%라도 작업당 $5씩 들면 운영이 불가능합니다.

```python
# 나쁜 예
if benchmark["success_rate"] > 0.9:
    deploy_to_production()  # 비용/속도 무시

# 좋은 예
if (benchmark["success_rate"] > 0.9 and
    benchmark["cost"]["estimated_usd"] / benchmark["total_runs"] < 0.10 and
    benchmark["avg_latency_seconds"] < 5.0):
    deploy_to_production()
```

성공률, 비용, 속도를 함께 봐야 합니다.

### 실수 2: 단일 실행 결과로 평가

LLM은 비결정적입니다. 한 번의 결과로는 신뢰할 수 없습니다.

```python
# 나쁜 예
result = agent.run(test_input)
if result == expected:
    print("Pass")

# 좋은 예
results = [agent.run(test_input) for _ in range(10)]
pass_rate = sum(1 for r in results if r == expected) / 10
print(f"통과율: {pass_rate:.0%}")
```

최소 5-10회 반복 실행 후 평균을 봐야 합니다.

### 실수 3: 테스트 케이스가 학습 데이터와 비슷

LLM이 이미 비슷한 데이터로 학습했을 수 있습니다. 의도적으로 분포 밖(out-of-distribution) 케이스를 포함해야 합니다.

```python
# 나쁜 예
test_cases = [
    "What is the capital of France?",  # LLM이 무수히 본 패턴
    "Who wrote Hamlet?"
]

# 좋은 예
test_cases = [
    "사용자가 방금 만든 'Project Atlas'의 다음 마일스톤은?",  # 실제 도메인
    "ID가 7842인 주문을 취소하고 환불해줘"  # 실제 운영 시나리오
]
```

실제 사용 패턴을 반영한 테스트가 의미있습니다.

### 실수 4: Trajectory를 무시하고 결과만 평가

같은 답이라도 도구를 10번 호출한 Agent와 2번 호출한 Agent는 다릅니다.

```python
# 나쁜 예
def evaluate(agent, task):
    result = agent.run(task)
    return result == expected_answer

# 좋은 예
def evaluate(agent, task):
    recorder = TrajectoryRecorder(task["id"])
    result = agent.run(task, recorder=recorder)
    traj = recorder.finalize(result, result == expected_answer)
    eff = evaluate_trajectory_efficiency(traj)
    return {
        "correct": result == expected_answer,
        "efficient": eff["tool_calls"] <= task["max_tool_calls"],
        "no_duplicates": eff["duplicate_tool_calls"] == 0
    }
```

결과의 정확성과 경로의 효율성을 함께 봅니다.

### 실수 5: 회귀 테스트 없이 배포

Agent를 개선했다고 생각하지만 다른 케이스가 망가지는 경우가 흔합니다.

```python
# 나쁜 예
# v2 출시 직전 새 케이스 몇 개만 테스트
new_cases = [test1, test2]
if all(agent_v2.run(c) for c in new_cases):
    deploy_v2()  # 기존 케이스가 망가질 수 있음

# 좋은 예
# 전체 벤치마크 회귀 실행
v1_results = benchmark.run(agent_v1)
v2_results = benchmark.run(agent_v2)
regressions = [
    case_id for case_id in v1_results["per_case"]
    if v1_results["per_case"][case_id]["success_rate"] >
       v2_results["per_case"][case_id]["success_rate"]
]
if not regressions:
    deploy_v2()
else:
    print(f"회귀 발생: {regressions}")
```

배포 전 회귀 테스트는 필수입니다.

## 핵심 요약

- Agent 평가는 Success Rate, Cost per Task, Latency를 모두 봐야 합니다
- Trajectory 평가는 같은 결과를 더 적은 단계로 달성했는지 측정합니다
- 도구 호출 정확도는 도구 선택과 인자 정확성을 따로 측정합니다
- 엔드투엔드 시나리오 테스트로 멀티턴, 상태, 도구 체인을 한꺼번에 검증합니다
- 표준 벤치마크와 자체 벤치마크를 함께 사용해 회귀를 방지합니다
- 단일 실행이 아닌 5-10회 반복 후 평균으로 평가해야 신뢰할 수 있습니다

<!-- a-grade-example:begin -->

## 시니어 엔지니어는 이렇게 생각합니다

- **결과 vs 과정** — 최종 결과뿐 아니라 step별 행동도 평가합니다.
- **골든 trace** — 성공 trace 묶음을 회귀 자산으로 보존합니다.
- **LLM-judge 한계** — judge 비용·편향을 인지하고 사람 평가와 교차 검증합니다.
- **회귀 게이트** — 임계 미달 시 배포를 막는 자동 게이트를 둡니다.
- **Cost·Latency** — 품질과 함께 비용·지연을 동일 보드에서 추적합니다.

## 체크리스트

- [ ] Agent 평가 지표를 task-level / step-level / tool-level로 분리해 적었다.
- [ ] 한 trajectory에 대해 step별 평가를 직접 채점해 봤다.
- [ ] 도구 호출 정확도를 자동으로 측정하는 작은 스크립트를 작성했다.
- [ ] 동일 작업에 대해 E2E 점수와 벤치마크 점수를 비교했다.

<!-- a-grade-example:end -->

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

1. **AgentBench: Evaluating LLMs as Agents** - https://arxiv.org/abs/2308.03688  
   Tsinghua/Stanford의 종합 Agent 벤치마크 논문. 8개 환경에서 LLM Agent의 추론과 도구 사용을 평가합니다.

2. **GAIA: A Benchmark for General AI Assistants** - https://arxiv.org/abs/2311.12983  
   Meta의 General AI Assistant 벤치마크. 실제 문제 해결 능력을 측정하는 466개 질문 모음입니다.

3. **LangSmith: Agent Evaluation** - https://docs.smith.langchain.com/evaluation  
   LangChain의 Agent 평가 도구 문서. Trajectory 기록과 자동 평가 파이프라인을 제공합니다.

4. **OpenAI Evals Framework** - https://github.com/openai/evals  
   OpenAI의 모델 평가 프레임워크. Agent를 포함한 다양한 LLM 시스템에 적용 가능합니다.

Tags: AI Agent, LLM, Tool Use, Python
