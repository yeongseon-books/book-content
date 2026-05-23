---
title: "Harness Engineering 101 (6/10): Test Harness — 완료 조건을 테스트로 고정하기"
series: harness-engineering-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Testing
- Eval
last_reviewed: '2026-05-14'
seo_description: Agent가 "끝났습니다"라고 말해도 정말 끝났는지는 테스트가 결정합니다.
---

# Harness Engineering 101 (6/10): Test Harness — 완료 조건을 테스트로 고정하기
에이전트 데모는 대개 잘 동작합니다. 입력이 몇 개 없고, 설계자가 기대한 경로로만 흘러가기 때문입니다. 하지만 실제 사용자 요청이 들어오기 시작하면 그 데모 품질은 놀랄 만큼 빨리 무너집니다.
문제는 에이전트가 끝났다고 말하는 순간을 그대로 믿기 쉽다는 데 있습니다. 자연어로 된 "완료했습니다"는 증거가 아닙니다. 완료 조건을 자동 검증 가능한 테스트로 바꾸지 않으면 시스템은 매 릴리스마다 조용히 나빠집니다.
Test Harness는 이 조용한 품질 하락을 막는 층입니다. 무엇을 통과로 볼지 고정하고, 그 기준을 unit, integration, eval로 나눠 반복 실행하게 만듭니다.
이 글은 Harness Engineering 101 시리즈의 6번째 글입니다.
에이전트 품질은 느낌이 아니라 반복 가능한 테스트 결과로 관리해야 합니다.

![Test Harness - 완료 조건을 테스트로 고정하기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-01-test-harness-turning-completion-criteria.ko.png)
*Test Harness - 완료 조건을 테스트로 고정하기*
> Test Harness는 agent가 한 번 맞혔다는 사실보다, 다음 변경 뒤에도 같은 기준을 통과하는지 증명하는 구조입니다.

## 먼저 던지는 질문

- Test Harness는 완료 조건을 자연어 약속에서 무엇으로 바꿔야 할까요?
- unit, trajectory, end-to-end 테스트는 각각 어떤 agent 실패를 잡을까요?
- eval dataset과 regression check는 운영 전에 어떻게 연결되어야 할까요?

## 왜 이 글이 중요한가
Test Harness가 중요한 첫 번째 이유는 증거입니다. 데모에서 몇 번 잘 나온다는 사실은 실제 운영 품질을 보장하지 않습니다. 반복 가능한 체크가 있어야만 변경 전후를 비교할 수 있습니다.
두 번째 이유는 회귀 방지입니다. 프롬프트, 모델, 도구, 정책 어느 하나가 바뀌어도 품질은 쉽게 흔들립니다. 자동 테스트가 없으면 이 흔들림은 실제 사용자에게 먼저 발견됩니다.
세 번째 이유는 디버깅 비용입니다. Unit이 없으면 어디가 깨졌는지 찾기 어렵고, eval이 없으면 전체 품질이 좋아졌는지 나빠졌는지 판단할 수 없습니다. 세 층은 서로 대체 관계가 아닙니다.
## 핵심 관점
에이전트는 전통적인 함수보다 비결정성이 크기 때문에 더 엄격한 검증 체계가 필요합니다. 같은 의미를 다른 문장으로 표현할 수 있고, 때로는 작은 프롬프트 변경이 전체 행동을 바꿉니다.
그래서 Test Harness는 결과를 한 가지 정답 문자열로만 보지 않습니다. 정확 매치가 가능한 부분은 그대로 검사하고, 의미 평가가 필요한 부분은 heuristic과 LLM-as-judge를 섞어 다층적으로 봅니다.
이 글에서 가장 중요한 일은 완료 조건을 사람이 나중에 읽고 판단하도록 남겨 두지 않고, 시스템이 릴리스마다 반복 실행할 수 있는 형태로 고정하는 것입니다.
> "잘 동작한다"는 말은 증거가 아닙니다. 자동으로 다시 돌릴 수 있는 테스트만이 증거입니다.
## 핵심 개념
Agent가 "끝났습니다"라고 말해도 정말 끝났는지는 테스트가 결정합니다. Test Harness는 완료 조건을 자동 검증 가능한 테스트로 고정합니다.

### "잘 동작합니다"라는 말은 증거가 아닙니다

Agent를 만들고 데모를 돌리면 잘 동작합니다. 실제 사용자에게 풀면 한 주 안에 망가집니다. 두 상황의 차이는 입력의 다양성입니다. 데모는 5개의 잘 짜인 입력으로 동작하지만, production은 수천 개의 예측 못 한 입력을 마주합니다.

이 간극을 메우는 것이 Test Harness입니다. Agent의 완료 조건을 자연어가 아니라 자동 실행 가능한 테스트로 표현하고, 모든 변경에 대해 그 테스트를 돌립니다. "잘 동작합니다"가 아니라 "이 50개의 테스트가 통과합니다"가 증거입니다.

이번 글에서는 Agent용 테스트의 종류, 평가 데이터셋 만들기, 그리고 회귀 방지 자동화를 다룹니다.

### Agent 테스트의 3 계층

![Agent 테스트의 3 계층](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-02-three-tiers-of-agent-tests.ko.png)

*Agent 테스트의 3 계층*

전통적인 소프트웨어 테스트와 비슷하지만, 비결정성이 추가됩니다.

**1. Unit tests**: 각 도구가 schema대로 동작하는지. 결정적, 빠릅니다.

**2. Integration tests**: 도구 조합이 task 시나리오에서 동작하는지. 실제 LLM 또는 mock LLM 사용.

**3. Eval tests**: 평가 데이터셋에 대해 정성적 품질을 측정. 비결정적이지만 통계적으로 안정.

```python
import pytest
from dataclasses import dataclass

# 1. 단위 테스트 - 도구 스키마
def test_create_user_input_validation():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        CreateUserInput(email="invalid", name="A", role="admin")

# 2. 통합 테스트 - 작업 흐름
def test_report_generation_flow(mock_llm):
    """The report generation task uses only read_db."""
    agent = build_agent(tools=["read_db"], llm=mock_llm)
    result = agent.run(task=ReportTaskSpec(date="2026-05-03"))
    assert result.status == "completed"
    assert all(call.tool == "read_db" for call in result.tool_calls)

# 3. 평가 테스트 - 정성적 품질
def test_summary_quality(eval_dataset):
    agent = build_summary_agent()
    scores = []
    for example in eval_dataset:
        output = agent.run(input=example.input)
        scores.append(rubric_score(output, example.expected))
    assert sum(scores) / len(scores) >= 0.85
```

세 계층 모두 필요합니다. Unit이 빠진 채 Eval만 있으면 디버깅이 불가능합니다. Eval이 빠진 채 Unit만 있으면 production 품질을 보장 못 합니다.

### Eval Dataset 만들기

![Eval Dataset 만들기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-03-building-an-eval-dataset.ko.png)

*Eval Dataset 만들기*

평가 데이터셋이 없으면 품질 측정이 불가능합니다. 데이터셋은 세 가지 출처에서 만듭니다.

**1. Production logs**: 실제 사용자의 요청을 샘플링합니다. 가장 현실적이지만 PII 처리가 필요합니다.

**2. Synthetic generation**: LLM으로 다양한 변형을 생성합니다. 빠르지만 실제 분포와 다를 수 있습니다.

**3. Adversarial examples**: 일부러 어렵게 만든 입력. Edge case와 prompt injection 시도.

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

데이터셋 크기는 task의 복잡도에 따라 다릅니다. 단순 분류는 50~100개, 복잡한 multi-step task는 200~500개가 일반적입니다.

### Rubric 기반 채점

Eval 결과를 어떻게 점수화할 것인가. 기대 출력과의 정확 매치는 Agent 출력에는 거의 안 맞습니다. 같은 의미를 다른 단어로 표현하기 때문입니다.

세 가지 채점 방식.

**1. Exact match**: 가능한 곳에는 사용. JSON 필드, 숫자, ID.

**2. Heuristic checks**: 정규식, 길이, 필수 단어 포함. 빠르고 결정적.

**3. LLM-as-judge**: 다른 LLM에게 채점을 맡깁니다. 비용 들지만 의미적 평가 가능.

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

LLM-as-judge는 강력하지만 위험합니다. judge 모델의 편향이 점수에 그대로 반영됩니다. 사람 평가와 정기적으로 비교해서 calibration을 맞춥니다.

### 회귀 방지 자동화

![회귀 방지 자동화](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/06/06-04-automating-regression-prevention.ko.png)

*회귀 방지 자동화*

테스트가 있어도 안 돌리면 의미가 없습니다. CI/CD에 통합해서 모든 변경에 대해 자동 실행합니다.

세 단계로 구성합니다.

**1. Fast unit tests**: PR마다 실행. 1분 이내.
**2. Integration tests**: PR마다 실행, mock LLM 사용. 5분 이내.
**3. Full eval suite**: 매일 또는 모델/프롬프트 변경 시 실행. 30분 이상 가능.

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

회귀가 발견되면 PR을 머지하지 않습니다. 이것이 Test Harness의 핵심 가치입니다 — 코드, 프롬프트, 모델 어느 것이 바뀌어도 품질이 떨어지지 않는다는 보장.

### 스냅샷 테스트

Agent 출력의 미세한 변화를 잡고 싶을 때 snapshot test가 유용합니다. 첫 실행 결과를 저장하고, 다음 실행이 그 결과와 다르면 실패합니다.

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

Snapshot test는 의도적인 변경에는 약합니다. 의도적으로 출력을 바꾸면 snapshot을 갱신해야 하는데, 그 갱신이 실수인지 의도인지 사람이 검토해야 합니다. PR 리뷰의 핵심 항목으로 만듭니다.

### Trajectory 테스트와 도구 호출 계약

Agent 테스트에서 자주 빠지는 영역이 중간 경로 검증입니다. 최종 출력만 맞으면 통과시키면, 우연히 맞은 경우와 안정적으로 맞은 경우를 구분할 수 없습니다. trajectory 테스트는 어떤 도구를 어떤 순서로, 어떤 제약 안에서 호출했는지까지 검사합니다.

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

이 테스트는 기능 테스트와 역할이 다릅니다. 출력 텍스트가 동일해도 불필요한 도구 호출이 늘어나는 회귀를 즉시 발견할 수 있습니다.

### 평가 메트릭 설계: Pass/Fail를 넘어서기

운영 배포에서는 평균 점수 하나로는 부족합니다. 최소한 성공률, 안전성 위반률, 비용, 지연, 승인 우회율을 함께 봐야 합니다.

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

실무 기준 예시는 다음처럼 둡니다. pass_rate 0.90 이상, policy_violation_rate 0.01 이하, approval_bypass_rate 0, p95 latency 8초 이하, avg_cost_usd/run 0.05 이하입니다. 숫자는 서비스 특성에 맞게 조정하되, 여러 지표를 동시에 보는 원칙은 유지해야 합니다.

### 실패 케이스의 운영 반영 루프

Test Harness가 실제로 팀 품질을 올리는 지점은 실패 케이스를 eval에 반영하는 속도입니다. 운영에서 발견된 실패를 다음 주까지 미루면 같은 실패가 반복됩니다. 이상적인 흐름은 사고가 난 당일에 최소 재현 케이스를 만들고, 다음 PR부터 regression에 편입하는 것입니다.

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

이 구조의 장점은 postmortem 문서와 테스트 코드를 연결한다는 점입니다. trace_id를 케이스 메타데이터에 남겨 두면 "왜 이 테스트가 생겼는가"를 나중에 바로 추적할 수 있습니다.

운영팀과 개발팀이 같은 케이스를 재사용할 수 있다는 점도 큽니다. 장애 회의에서 나온 실패 패턴을 곧바로 테스트 이름으로 고정하면, 개선 작업이 "좋아질 것 같다" 수준이 아니라 다음 릴리스에서 통과 여부로 확인됩니다.

### 흔한 실수

"개발하면서 만들겠다"는 보통 안 만듭니다. 첫 task부터 최소 20개의 예시를 준비합니다.

PII가 포함되어 있고, happy path에 편향되어 있습니다. 샘플링 + 마스킹 + adversarial 추가가 필요합니다.

judge 모델의 편향이 점수에 반영됩니다. 정기적으로 사람 평가와 비교합니다.

수동으로 가끔 돌리는 테스트는 곧 안 돌리게 됩니다. PR마다 자동 실행이 필수입니다.

"diff가 있네, 갱신!"으로 매번 통과시키면 snapshot의 의미가 없습니다. 차이는 사람이 검토합니다.
## 흔히 헷갈리는 지점
- eval 데이터셋은 나중에 쌓이면 된다고 생각하기 쉽지만, 대부분의 팀은 그렇게 미루다가 끝내 만들지 못합니다.
- production 로그를 그대로 쓰면 현실적이라고 보기 쉽지만, PII와 happy-path 편향 때문에 그대로는 쓸 수 없습니다.
- LLM-as-judge를 쓰면 사람이 전혀 필요 없다고 생각하기 쉽지만, judge 편향은 정기적으로 사람 평가와 맞춰야 합니다.
- 테스트를 수동으로 돌려도 된다고 생각하기 쉽지만, 수동 테스트는 곧 아무도 돌리지 않는 테스트가 됩니다.
- snapshot diff는 자동 승인해도 된다고 여기기 쉽지만, intentional change인지 regression인지 사람 검토가 필요합니다.
## 운영 체크리스트
- [ ] unit, integration, eval 세 층을 분리해 관리합니다.
- [ ] 최소 20개 이상의 초기 eval 예시를 준비한 뒤 첫 태스크를 배포합니다.
- [ ] production 로그, synthetic, adversarial 사례를 섞어 eval 데이터셋을 구성합니다.
- [ ] exact match, heuristic, LLM-as-judge를 함께 사용하고 judge를 정기적으로 보정합니다.
- [ ] 모든 테스트를 CI에서 자동 실행하고, eval은 임계값 미달 시 merge를 막습니다.
## 정리
Test Harness는 에이전트가 끝났다고 말하는 순간을 믿지 않고, 시스템 바깥의 검증 기준으로 다시 판정하는 층입니다. 이것이 있어야 데모와 운영 사이의 간극을 줄일 수 있습니다.
중요한 것은 하나의 거대한 테스트가 아니라 세 층의 조합입니다. Unit은 디버깅을 가능하게 만들고, integration은 흐름을 보장하며, eval은 전체 품질 변화를 수치로 보여 줍니다.
다음 글에서는 Feedback Loop를 다룹니다. 테스트가 실패했을 때 시스템은 그 실패를 사용자에게 그대로 돌려주지 않고, 다음 시도를 더 낫게 만드는 신호로 바꿔야 합니다.

## 처음 질문으로 돌아가기

- **Test Harness는 완료 조건을 자연어 약속에서 무엇으로 바꿔야 할까요?**
  - 완료 조건을 사람이 읽는 약속에서 자동 실행 가능한 assertion, rubric, snapshot, eval case로 바꿔야 합니다.
- **unit, trajectory, end-to-end 테스트는 각각 어떤 agent 실패를 잡을까요?**
  - unit test는 tool과 작은 함수, trajectory test는 중간 경로와 tool 선택, end-to-end test는 사용자 관점의 최종 완료를 잡습니다.
- **eval dataset과 regression check는 운영 전에 어떻게 연결되어야 할까요?**
  - 실제 실패와 대표 요청을 eval dataset에 넣고, 코드·prompt·tool 변경마다 regression check가 자동으로 돌도록 연결해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- [Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기](./04-constraint-harness.md)
- [Harness Engineering 101 (5/10): Tool Harness — Agent가 사용할 도구를 안전하게 설계하기](./05-tool-harness.md)
- **Harness Engineering 101 (6/10): Test Harness — 완료 조건을 테스트로 고정하기 (현재 글)**
- Harness Engineering 101 (7/10): Feedback Loop — 실패를 고치게 만드는 반복 구조 (예정)
- Harness Engineering 101 (8/10): Approval Gate — 사람 승인이 필요한 지점 설계하기 (예정)
- Harness Engineering 101 (9/10): Observability — Agent 작업을 추적하고 재현하기 (예정)
- Harness Engineering 101 (10/10): Production Harness — 운영 가능한 Agent 작업 환경 만들기 (예정)

<!-- toc:end -->

## 참고 자료
### 공식 문서

- [OpenAI Evals Framework](https://github.com/openai/evals)
- [Anthropic — Evaluating LLMs](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [LangSmith — LLM Evaluation](https://docs.smith.langchain.com/evaluation)
- [Eugene Yan — Evaluating LLM-Based Applications](https://eugeneyan.com/writing/evals/)
### 관련 시리즈

- [LangGraph 101 — 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Safety & Guardrails 101 — 운영 가드레일 시스템 구축](../../ai-safety-guardrails-101/ko/10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/harness-engineering-101/ko/06-test-harness)

Tags: AI Agent, Harness, Production, Reliability
