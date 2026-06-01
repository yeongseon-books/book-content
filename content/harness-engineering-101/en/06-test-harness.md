---
title: "Harness Engineering 101 (6/10): Test Harness — Turning Completion Criteria into Tests"
series: harness-engineering-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Testing
- Eval
last_reviewed: '2026-05-14'
seo_description: When an agent says "done", only tests can confirm whether the work
  is actually done.
---

# Harness Engineering 101 (6/10): Test Harness — Turning Completion Criteria into Tests

Agent demos usually look fine because the inputs were carefully chosen and the path was obvious to the person who built them. Real users immediately invalidate that comfort by bringing messy requests, partial data, and edge cases you did not rehearse.

That is why “the agent says it is done” is not evidence. Completion must be decided by an external test surface that can run again after every prompt, tool, or model change.

This is the 6th post in the Harness Engineering 101 series. Here we turn completion criteria into repeatable unit, integration, and eval checks.

![Test harness - turning completion criteria into tests](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-01-test-harness-turning-completion-criteria.en.png)
*Test harness - turning completion criteria into tests*
> A Test Harness matters less because the agent passed once, and more because it proves future changes still meet the same criteria.

## Questions to Keep in Mind

- What should a Test Harness turn natural-language completion promises into?
- What agent failures do unit, trajectory, and end-to-end tests each catch?
- How should eval datasets and regression checks connect before production?

## "It Works" Is Not Evidence

Build an agent and demo it — it works. Open it to real users and within a week it breaks. The difference is input diversity. A demo runs on five well-shaped inputs; production faces thousands of unexpected ones.

Test Harness closes that gap. Express the agent's completion criteria as automatically runnable tests rather than natural language, and run those tests on every change. The evidence is not "it works" but "these 50 tests pass."

This article covers the kinds of tests for agents, building eval datasets, and automating regression prevention.

---

## Three Tiers of Agent Tests

![Three tiers of agent tests](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-02-three-tiers-of-agent-tests.en.png)

*Three tiers of agent tests*
Similar to traditional software testing, with non-determinism added.

**1. Unit tests**: each tool behaves per its schema. Deterministic and fast.

**2. Integration tests**: tool combinations work in task scenarios. Use real or mock LLMs.

**3. Eval tests**: qualitative quality measured against an eval dataset. Non-deterministic but statistically stable.

```python
import pytest
from dataclasses import dataclass

# 1. Unit test — tool schema
def test_create_user_input_validation():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        CreateUserInput(email="invalid", name="A", role="admin")

# 2. Integration test — task flow
def test_report_generation_flow(mock_llm):
    """The report generation task uses only read_db."""
    agent = build_agent(tools=["read_db"], llm=mock_llm)
    result = agent.run(task=ReportTaskSpec(date="2026-05-03"))
    assert result.status == "completed"
    assert all(call.tool == "read_db" for call in result.tool_calls)

# 3. Eval test — qualitative quality
def test_summary_quality(eval_dataset):
    agent = build_summary_agent()
    scores = []
    for example in eval_dataset:
        output = agent.run(input=example.input)
        scores.append(rubric_score(output, example.expected))
    assert sum(scores) / len(scores) >= 0.85
```

All three are needed. Without unit tests, debugging is impossible. Without eval tests, production quality is not guaranteed.

---

## Building an Eval Dataset

![Building an eval dataset](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-03-building-an-eval-dataset.en.png)

*Building an eval dataset*
Without an eval dataset, quality is unmeasurable. Datasets come from three sources.

**1. Production logs**: sample real user requests. Most realistic but requires PII handling.

**2. Synthetic generation**: have an LLM produce variations. Fast but may diverge from real distribution.

**3. Adversarial examples**: deliberately hard inputs. Edge cases and prompt injection attempts.

```python
@dataclass
class EvalExample:
    """A single eval example."""
    id: str
    input: dict
    expected: dict  # exact match or rubric-evaluated
    category: str  # "happy_path" | "edge" | "adversarial"
    source: str  # "production" | "synthetic" | "manual"

def build_eval_dataset() -> list[EvalExample]:
    """Balance the dataset across categories."""
    examples = []
    examples.extend(sample_from_production_logs(n=50, category="happy_path"))
    examples.extend(generate_synthetic_variations(n=30, category="happy_path"))
    examples.extend(load_manual_edge_cases(n=15, category="edge"))
    examples.extend(load_adversarial_examples(n=5, category="adversarial"))
    return examples
```

Dataset size depends on task complexity. Simple classification: 50–100 examples. Complex multi-step tasks: 200–500.

---

## Rubric-Based Scoring

How do you score an eval result? Exact match against expected output rarely works for agents, since the same meaning can be expressed in different words.

Three scoring approaches.

**1. Exact match**: use where possible. JSON fields, numbers, IDs.

**2. Heuristic checks**: regex, length, required-word presence. Fast and deterministic.

**3. LLM-as-judge**: hand scoring to another LLM. Costly but enables semantic evaluation.

```python
from collections.abc import Callable

@dataclass
class Rubric:
    """A bundle of scoring criteria."""
    name: str
    weight: float
    check: Callable[[dict, dict], float]  # (output, expected) -> 0.0..1.0

def has_required_sections(output: dict, expected: dict) -> float:
    required = expected.get("required_sections", [])
    if not required:
        return 1.0
    present = sum(1 for s in required if s in output.get("text", ""))
    return present / len(required)

def numbers_match(output: dict, expected: dict) -> float:
    e_nums = expected.get("numbers", {})
    o_nums = output.get("numbers", {})
    if not e_nums:
        return 1.0
    correct = sum(1 for k, v in e_nums.items() if abs(o_nums.get(k, 0) - v) < 0.01)
    return correct / len(e_nums)

def llm_judge_helpfulness(output: dict, expected: dict) -> float:
    """Have an LLM rate helpfulness from 0 to 1."""
    return 0.85  # actual: call judge LLM

RUBRICS = [
    Rubric("structure", weight=0.3, check=has_required_sections),
    Rubric("accuracy", weight=0.5, check=numbers_match),
    Rubric("helpfulness", weight=0.2, check=llm_judge_helpfulness),
]

def rubric_score(output: dict, expected: dict, rubrics=RUBRICS) -> float:
    return sum(r.check(output, expected) * r.weight for r in rubrics)
```

LLM-as-judge is powerful but risky. The judge model's bias flows directly into the scores. Calibrate against human evaluation regularly.

---

## Automating Regression Prevention

![Automating regression prevention](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-04-automating-regression-prevention.en.png)

*Automating regression prevention*
Tests that exist but don't run are worthless. Wire them into CI/CD to run on every change.

Three tiers.

**1. Fast unit tests**: every PR. Under 1 minute.
**2. Integration tests**: every PR with mock LLM. Under 5 minutes.
**3. Full eval suite**: daily or on model/prompt changes. Can take 30+ minutes.

```python
# .github/workflows/agent-tests.yml
"""
name: Agent Tests
on: [pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit -x --timeout=60

  integration:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/integration -x --timeout=300
        env:
          USE_MOCK_LLM: "true"

  eval:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'run-eval')
    steps:
      - run: python scripts/run_eval.py --dataset eval/v1 --threshold 0.85
"""

def run_eval_suite(dataset_path: str, threshold: float) -> bool:
    """Run the full eval and compare to threshold."""
    examples = load_dataset(dataset_path)
    results = []
    for ex in examples:
        output = run_agent(ex.input)
        score = rubric_score(output, ex.expected)
        results.append((ex.id, score))

    avg = sum(s for _, s in results) / len(results)
    failed = [(eid, s) for eid, s in results if s < 0.7]

    print(f"Average: {avg:.3f}, Threshold: {threshold}")
    print(f"Failed (<0.7): {len(failed)}")
    return avg >= threshold
```

If a regression appears, do not merge. That is the core value of Test Harness — a guarantee that quality does not drop when code, prompts, or models change.

---

## Snapshot Testing

When you want to catch tiny shifts in agent output, snapshot tests help. Save the first run's output and fail if subsequent runs differ.

```python
import json
from pathlib import Path
import hashlib

def assert_snapshot(name: str, actual: dict, snapshot_dir: Path = Path("tests/snapshots")):
    """Compare against a saved snapshot."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_file = snapshot_dir / f"{name}.json"

    actual_str = json.dumps(actual, sort_keys=True, indent=2)

    if not snapshot_file.exists():
        snapshot_file.write_text(actual_str)
        print(f"snapshot created: {snapshot_file}")
        return

    expected_str = snapshot_file.read_text()
    if actual_str != expected_str:
        actual_hash = hashlib.sha256(actual_str.encode()).hexdigest()[:8]
        expected_hash = hashlib.sha256(expected_str.encode()).hexdigest()[:8]
        raise AssertionError(
            f"snapshot mismatch for {name}\n"
            f"  expected: {expected_hash}\n"
            f"  actual:   {actual_hash}\n"
        )

def test_classification_snapshot(deterministic_agent):
    """The classification task's output does not change."""
    result = deterministic_agent.classify("This product is amazing!")
    assert_snapshot("positive_review_classification", result)
```

Snapshot tests are weak against intentional changes. When you intentionally change the output, you must update the snapshot — and a human must judge whether the update is intent or mistake. Make this a key item in PR review.

### Trajectory Testing and Tool-Call Contracts

A commonly missed testing dimension is intermediate-path verification. If you only check the final output, you cannot distinguish between accidentally correct results and reliably correct ones. Trajectory tests verify which tools were called, in what order, and within what budget.

```python
from dataclasses import dataclass

@dataclass
class ExpectedStep:
    tool: str
    max_calls: int

def assert_trajectory(actual_calls: list[dict], expected: list[ExpectedStep]) -> None:
    counts: dict[str, int] = {}
    for call in actual_calls:
        counts[call["tool"]] = counts.get(call["tool"], 0) + 1

    for step in expected:
        used = counts.get(step.tool, 0)
        if used == 0:
            raise AssertionError(f"required tool not called: {step.tool}")
        if used > step.max_calls:
            raise AssertionError(f"tool overused: {step.tool} ({used}>{step.max_calls})")

def test_refund_trajectory(refund_agent):
    result = refund_agent.run({"intent": "refund", "order_id": "ord_1001", "amount": 250})
    assert result.status == "completed"
    assert_trajectory(
        actual_calls=result.tool_calls,
        expected=[
            ExpectedStep("lookup_order", 1),
            ExpectedStep("calc_refund", 1),
            ExpectedStep("issue_refund", 1),
        ],
    )
```

This test serves a different purpose than a functional test. Even if the output text is identical, trajectory tests catch regressions where unnecessary tool calls creep in.

### Eval Metrics Design: Beyond Pass/Fail

A single average score is insufficient for production deployments. At minimum, track pass rate, safety violation rate, cost, latency, and approval bypass rate together.

```python
@dataclass
class EvalMetrics:
    pass_rate: float
    policy_violation_rate: float
    approval_bypass_rate: float
    avg_tool_calls: float
    p95_latency_ms: float
    avg_cost_usd: float

def compute_metrics(rows: list[dict]) -> EvalMetrics:
    n = len(rows)
    lat = sorted(r["latency_ms"] for r in rows)
    p95 = lat[int(max(0, n - 1) * 0.95)] if n else 0.0
    return EvalMetrics(
        pass_rate=sum(1 for r in rows if r["passed"]) / n if n else 0.0,
        policy_violation_rate=sum(1 for r in rows if r["policy_violation"]) / n if n else 0.0,
        approval_bypass_rate=sum(1 for r in rows if r["approval_bypass"]) / n if n else 0.0,
        avg_tool_calls=sum(r["tool_calls"] for r in rows) / n if n else 0.0,
        p95_latency_ms=p95,
        avg_cost_usd=sum(r["cost_usd"] for r in rows) / n if n else 0.0,
    )
```

Practical thresholds as a starting point: pass_rate ≥ 0.90, policy_violation_rate ≤ 0.01, approval_bypass_rate = 0, p95 latency ≤ 8 s, avg_cost_usd per run ≤ $0.05. Adjust numbers per service, but maintain the principle of watching multiple dimensions simultaneously.

### Failure-to-Regression Loop

Where a Test Harness truly raises team quality is in the speed of converting production failures into eval cases. If you defer a discovered failure to next week, the same failure repeats. The ideal flow: create a minimal reproduction case on the day of the incident, and include it in the regression suite starting with the next PR.

```python
@dataclass
class RegressionCase:
    case_id: str
    source_trace_id: str
    input_payload: dict
    expected_constraints: dict
    severity: str

def build_regression_case_from_trace(trace: dict) -> RegressionCase:
    return RegressionCase(
        case_id=f"reg-{trace['trace_id']}",
        source_trace_id=trace["trace_id"],
        input_payload=trace["input"],
        expected_constraints={
            "no_policy_violation": True,
            "max_tool_calls": 6,
            "approval_bypass": False,
        },
        severity=trace.get("severity", "medium"),
    )

def test_regression_case(agent, case: RegressionCase):
    result = agent.run(case.input_payload)
    assert not result.policy_violation
    assert len(result.tool_calls) <= case.expected_constraints["max_tool_calls"]
    assert not result.approval_bypass
```

This structure links postmortem documents to test code. Keeping the `trace_id` in case metadata lets anyone trace back to "why does this test exist" immediately.

The reusability across ops and dev teams is equally important. When a failure pattern from an incident review is pinned as a test name, improvement work is no longer "should get better" — it is confirmed by pass/fail in the next release.

---

## Common Mistakes

**1. Starting without an eval dataset.**
"I'll build it as I go" usually never builds it. Prepare 20+ examples before the first task.

**2. Using production logs raw.**
PII included, happy-path biased. You need sampling + masking + adversarial additions.

**3. Trusting LLM-as-judge without calibration.**
Judge model bias flows into scores. Compare against human evaluation regularly.

**4. Not wiring tests into CI.**
Tests run manually only sometimes soon become tests run never. Auto-run on every PR is mandatory.

**5. Auto-approving every snapshot diff.**
"There's a diff, update!" defeats the purpose. Diffs require human review.

---

## Key Takeaways

- "It works" is not evidence. Automatically runnable tests are.
- Agent testing has three tiers: Unit, Integration, Eval.
- Eval datasets blend production logs, synthetic, and adversarial sources in balance.
- Score with exact match, heuristics, and LLM-as-judge in combination, calibrating the judge against humans.
- Wire all tests into CI for every PR. Manual tests soon become unrun tests.

## Operational checklist

- [ ] Split tests into unit, integration, and eval layers rather than collapsing them into one suite.
- [ ] Build an initial eval dataset before shipping the first serious task.
- [ ] Mix production-derived, synthetic, and adversarial cases in the dataset.
- [ ] Use exact checks, heuristics, and judge models together, then recalibrate judges against humans.
- [ ] Run the suites automatically in CI and block merges on failed thresholds.

## Answering the Opening Questions

- **What should a Test Harness turn natural-language completion promises into?**
  - It should turn completion promises into executable assertions, rubrics, snapshots, and eval cases.
- **What agent failures do unit, trajectory, and end-to-end tests each catch?**
  - Unit tests catch tools and small functions, trajectory tests catch intermediate paths and tool choices, and end-to-end tests catch user-visible completion.
- **How should eval datasets and regression checks connect before production?**
  - Put real failures and representative requests into the eval dataset, then run regression checks automatically for code, prompt, and tool changes.

<!-- toc:begin -->
## In this series

- [Harness Engineering 101 (1/10): What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Harness Engineering 101 (3/10): Context Harness — Designing What the Agent Should Know and Not Know](./03-context-harness.md)
- [Harness Engineering 101 (4/10): Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions](./04-constraint-harness.md)
- [Harness Engineering 101 (5/10): Tool Harness — Designing Safe Tools for Agents](./05-tool-harness.md)
- **Harness Engineering 101 (6/10): Test Harness — Turning Completion Criteria into Tests (current)**
- Harness Engineering 101 (7/10): Feedback Loops — Building Structures That Let Agents Recover from Failure (upcoming)
- Harness Engineering 101 (8/10): Approval Gates — Designing Where Humans Must Approve (upcoming)
- Harness Engineering 101 (9/10): Observability — Tracing and Replaying Agent Work (upcoming)
- Harness Engineering 101 (10/10): Production Harness — Building Operational Environments for Agents (upcoming)

<!-- toc:end -->

---

## References

### Official docs and references

- [OpenAI Evals Framework](https://github.com/openai/evals)
- [Anthropic — Evaluating LLMs](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [LangSmith — LLM Evaluation](https://docs.smith.langchain.com/evaluation)
- [Eugene Yan — Evaluating LLM-Based Applications](https://eugeneyan.com/writing/evals/)

Tags: AI Agent, Harness, Production, Reliability
