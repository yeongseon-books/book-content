---
title: Test Harness — Turning Completion Criteria into Tests
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

# Test Harness — Turning Completion Criteria into Tests

Agent demos usually look fine because the inputs were carefully chosen and the path was obvious to the person who built them. Real users immediately invalidate that comfort by bringing messy requests, partial data, and edge cases you did not rehearse.

That is why “the agent says it is done” is not evidence. Completion must be decided by an external test surface that can run again after every prompt, tool, or model change.

This is post 6 in the Harness Engineering 101 series. Here we turn completion criteria into repeatable unit, integration, and eval checks.

---

## Questions this chapter answers

- What is the same and different between agent testing and traditional software testing?
- Why should unit, integration, and eval checks exist as separate layers?
- Where do useful eval examples come from in practice?
- How do you score agent outputs when there is no single exact string answer?
- Why must these checks live inside CI instead of manual review habit?

> “Works in the demo” is not proof. A test you can rerun on every change is proof.

![Test harness - turning completion criteria into tests](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-01-test-harness-turning-completion-criteria.en.png)

*Test harness - turning completion criteria into tests*
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

<!-- toc:begin -->
## In this series

- [What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Context Harness — Designing What the Agent Should Know and Not Know](./03-context-harness.md)
- [Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions](./04-constraint-harness.md)
- [Tool Harness — Designing Safe Tools for Agents](./05-tool-harness.md)
- **Test Harness — Turning Completion Criteria into Tests (current)**
- Feedback Loops — Building Structures That Let Agents Recover from Failure (upcoming)
- Approval Gates — Designing Where Humans Must Approve (upcoming)
- Observability — Tracing and Replaying Agent Work (upcoming)
- Production Harness — Building Operational Environments for Agents (upcoming)

<!-- toc:end -->

---

## References

### Official docs and references

- [OpenAI Evals Framework](https://github.com/openai/evals)
- [Anthropic — Evaluating LLMs](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [LangSmith — LLM Evaluation](https://docs.smith.langchain.com/evaluation)
- [Eugene Yan — Evaluating LLM-Based Applications](https://eugeneyan.com/writing/evals/)

Tags: AI Agent, Harness, Production, Reliability
