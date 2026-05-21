---
title: "AI Agent 101 (7/10): Agent Evaluation"
series: ai-agent-101
episode: 7
language: en
status: publish-ready
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Evaluation
- Testing
- Metrics
last_reviewed: '2026-05-15'
seo_description: What's harder than building an agent is evaluating "whether this
  agent works properly." Simple LLMs only need response quality evaluation, but…
---

# AI Agent 101 (7/10): Agent Evaluation

What's harder than building an agent is evaluating "whether this agent works properly." Simple LLMs only need response quality evaluation, but agents require multiple metrics: tool calling accuracy, task completion rate, unnecessary step count, cost efficiency, etc.

Agent evaluation is divided into three levels. Individual tool call accuracy (Tool Use Accuracy), task path efficiency (Trajectory Evaluation), and final result accuracy (End-to-End Success Rate).

This is post 7 in the AI Agent 101 series. Here we cover agent evaluation metrics, trajectory evaluation methods, tool calling accuracy measurement, end-to-end test strategies, and benchmarking methods.

![Evaluation signal path](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/07/07-01-evaluation-signal-path.en.png)
*Evaluation signal path*
> Agent evaluation is not answer grading; it is diagnosis across trajectory, tool use, and final outcome.

## Questions to Keep in Mind

- Why is final-answer grading not enough for agent evaluation?
- What failures do trajectory evaluation, tool-call accuracy, and end-to-end success each catch?
- What real requests and failure cases belong in an eval set before production?

## Agent Evaluation Metrics

Agent evaluation must look beyond "did it answer well" to multiple dimensions. The core metrics are below.

### Evaluation signal path

### Task Success Rate

The percentage of user requests the agent completes successfully.

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

# Example usage
test_cases = [
    TestCase(
        task_id="weather_seoul",
        user_input="What's the weather in Seoul?",
        expected_outcome={"city": "Seoul", "has_temp": True},
        success_criteria=lambda o: "temperature" in o.get("response", "")
    ),
    TestCase(
        task_id="calc_simple",
        user_input="What is 3 times 4?",
        expected_outcome={"answer": 12},
        success_criteria=lambda o: "12" in o.get("response", "")
    )
]
metrics = evaluate_success_rate(my_agent, test_cases)
print(f"Success rate: {metrics['success_rate']:.1%}")
```

Success rate is the most intuitive metric, but it doesn't show *how* the agent succeeded or failed.

### Cost per Task

The token cost and number of API calls required to complete a single task.

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

Cost metrics are critical in production. Even with high accuracy, if each task costs over $1, the business won't work.

If you still keep `gpt-3.5-turbo` in an existing system, treat it as a legacy model. Its current legacy pricing is $0.50 per 1M input tokens and $1.50 per 1M output tokens, but for new low-cost budgeting examples `gpt-4o-mini` is the better default.

### Latency

The time from user request to final response. Agents traverse multiple steps, so total latency tends to grow.

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

# Example usage
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

print(f"total {m['total_seconds']:.2f}s, per-step: {m['steps']}")
```

Per-step latency reveals where the bottleneck is.

## Trajectory Evaluation

A trajectory is the path the agent takes from start to goal. For the same outcome, a shorter, more efficient trajectory is better.

### Recording Trajectories

Recording every step enables post-hoc analysis.

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

### Trajectory Efficiency

Use the recorded trajectory to evaluate efficiency.

```python
def evaluate_trajectory_efficiency(traj: Trajectory) -> dict:
    """Analyze trajectory efficiency."""
    tool_calls = [s for s in traj.steps if s.action == "tool_call"]
    thinks = [s for s in traj.steps if s.action == "think"]

    # Detect duplicate tool calls
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

# Compare efficiency
traj_a = recorder_a.finalize("answer A", True)
traj_b = recorder_b.finalize("answer B", True)

eff_a = evaluate_trajectory_efficiency(traj_a)
eff_b = evaluate_trajectory_efficiency(traj_b)
# Same answer; fewer steps means more efficient
```

The core question of trajectory evaluation is "did we reach the same result in fewer steps?"

## Tool Call Accuracy

Agent tool calls split into two parts: (1) Did it pick the right tool, (2) Did it call it with the right arguments?

```python
@dataclass
class ToolCallExpectation:
    """Expected tool call."""
    tool_name: str
    required_args: dict
    optional_args: dict = None

def evaluate_tool_call(
    actual_tool: str,
    actual_args: dict,
    expected: ToolCallExpectation
) -> dict:
    """Evaluate a single tool call."""
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

# Example usage
expected = ToolCallExpectation(
    tool_name="get_weather",
    required_args={"city": "Seoul"}
)
actual_tool = "get_weather"
actual_args = {"city": "Seoul", "unit": "celsius"}
print(evaluate_tool_call(actual_tool, actual_args, expected))
# {'tool_correct': True, 'args_correct': True, ...}
```

Aggregating tool-call accuracy across the whole test set surfaces agent weaknesses.

## End-to-End Testing

Unit tests aren't enough. An agent is the result of multiple components interacting, so end-to-end scenario tests are required.

```python
class E2ETestSuite:
    """End-to-end test suite."""

    def __init__(self, agent):
        self.agent = agent
        self.results = []

    def run_scenario(self, scenario: dict) -> dict:
        """Run a single scenario."""
        recorder = TrajectoryRecorder(scenario["id"])

        try:
            # Run multi-turn conversation
            for turn in scenario["turns"]:
                response = self.agent.chat(turn["user"])

            # Final assertions
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

# Define a scenario
scenario = {
    "id": "booking_flow",
    "turns": [
        {"user": "Find me a KTX from Seoul to Busan tomorrow"},
        {"user": "Show me morning departures"},
        {"user": "Book the first one"}
    ],
    "assertions": [
        {"type": "contains", "value": "booking confirmed"},
        {"type": "contains", "value": "KTX"}
    ]
}
```

End-to-end tests validate multi-turn dialogue, state retention, and tool chains all at once.

## Benchmarking

Standard benchmarks let you compare your agent against other systems.

### Public Agent Benchmarks

- **AgentBench** — Measures agent reasoning and tool use across 8 environments
- **WebArena** — Measures task completion on real websites
- **GAIA** — Evaluates general AI assistants on real problem solving
- **SWE-bench** — Measures GitHub issue resolution (for code agents)

### Building Your Own Benchmark

Domain-specific agents need their own benchmarks.

```python
class AgentBenchmark:
    """Benchmark runner."""

    def __init__(self, name: str):
        self.name = name
        self.test_cases: List[TestCase] = []
        self.cost_tracker = CostTracker()

    def add_case(self, case: TestCase):
        self.test_cases.append(case)

    def run(self, agent, repeat: int = 3) -> dict:
        """Run the benchmark, repeating to reduce noise."""
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

        # Aggregate
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

Benchmark results become the baseline for regression testing on every agent improvement.

## Common Mistakes

### Mistake 1: Judging by Success Rate Alone

Even at 90% success, $5 per task makes operations untenable.

```python
# Bad
if benchmark["success_rate"] > 0.9:
    deploy_to_production()  # Ignores cost and latency

# Good
if (benchmark["success_rate"] > 0.9 and
    benchmark["cost"]["estimated_usd"] / benchmark["total_runs"] < 0.10 and
    benchmark["avg_latency_seconds"] < 5.0):
    deploy_to_production()
```

Success rate, cost, and latency must be weighed together.

### Mistake 2: Single-Run Evaluation

LLMs are non-deterministic. A single run can't be trusted.

```python
# Bad
result = agent.run(test_input)
if result == expected:
    print("Pass")

# Good
results = [agent.run(test_input) for _ in range(10)]
pass_rate = sum(1 for r in results if r == expected) / 10
print(f"Pass rate: {pass_rate:.0%}")
```

Run 5-10 times minimum and average.

### Mistake 3: Test Cases Too Similar to Training Data

The LLM may have already seen similar data. Include out-of-distribution cases on purpose.

```python
# Bad
test_cases = [
    "What is the capital of France?",  # Pattern the LLM has seen countless times
    "Who wrote Hamlet?"
]

# Good
test_cases = [
    "What's the next milestone for the user's just-created 'Project Atlas'?",  # Real domain
    "Cancel order ID 7842 and issue a refund"  # Real operational scenario
]
```

Tests reflecting real usage patterns are meaningful.

### Mistake 4: Ignoring Trajectory, Evaluating Only Outcome

Two agents reaching the same answer with 10 vs. 2 tool calls are not equivalent.

```python
# Bad
def evaluate(agent, task):
    result = agent.run(task)
    return result == expected_answer

# Good
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

Evaluate correctness *and* path efficiency together.

### Mistake 5: No Regression Testing Before Deploy

You think you've improved, but other cases regressed.

```python
# Bad
# Test only the few new cases right before v2 ships
new_cases = [test1, test2]
if all(agent_v2.run(c) for c in new_cases):
    deploy_v2()  # Existing cases may have broken

# Good
# Run the full benchmark for regression
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
    print(f"Regressions found: {regressions}")
```

Pre-deploy regression testing is mandatory.

## Key Takeaways

- Agent evaluation must consider Success Rate, Cost per Task, and Latency together
- Trajectory evaluation measures whether the same result was reached in fewer steps
- Tool-call accuracy splits into tool selection and argument correctness
- End-to-end scenario tests validate multi-turn dialogue, state, and tool chains together
- Use both standard and custom benchmarks to catch regressions
- Evaluate by averaging 5-10 runs, not a single execution

<!-- a-grade-example:begin -->

## Checklist

- [ ] Split agent metrics into task / step / tool levels.
- [ ] Hand-scored a single trajectory step by step.
- [ ] Wrote a small script that auto-measures tool-call accuracy.
- [ ] Compared E2E and benchmark scores on the same task.

<!-- a-grade-example:end -->

## Answering the Opening Questions

- **Why is final-answer grading not enough for agent evaluation?**
  - An agent can call the wrong tool and still produce plausible text. Final-answer grading misses cost, risk, and accidental success.
- **What failures do trajectory evaluation, tool-call accuracy, and end-to-end success each catch?**
  - Trajectory evaluation catches wasted or wrong paths, tool-call accuracy catches tool choice and argument errors, and end-to-end success checks user-visible completion.
- **What real requests and failure cases belong in an eval set before production?**
  - Include frequent real requests, boundary cases, tool failures, ambiguous inputs, and cases that trigger expensive loops.

<!-- toc:begin -->
## In this series

- [AI Agent 101 (1/10): What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): Context Engineering](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use Fundamentals](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow Design](./04-agent-workflow-design.md)
- [AI Agent 101 (5/10): Memory and State](./05-memory-and-state.md)
- [AI Agent 101 (6/10): Multi-Agent Systems](./06-multi-agent-systems.md)
- **AI Agent 101 (7/10): Agent Evaluation (current)**
- AI Agent 101 (8/10): Error Handling and Reliability (upcoming)
- AI Agent 101 (9/10): Production Operations (upcoming)
- AI Agent 101 (10/10): Building Your First Agent (upcoming)

<!-- toc:end -->

## References

- [OpenAI evals design guide](https://platform.openai.com/docs/guides/evals)
- [LangSmith evaluation](https://docs.smith.langchain.com/evaluation)
- [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688)
- [GAIA: a benchmark for General AI Assistants](https://arxiv.org/abs/2311.12983)

Tags: AI Agent, LLM, Tool Use, Python
