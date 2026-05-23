---
title: "Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기"
series: harness-engineering-101
episode: 2
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
- Reliability
- Production
last_reviewed: '2026-05-12'
seo_description: Agent에게 모호한 지시를 던지면 모호한 결과가 돌아옵니다. Task Harness는 모호한 일을 명확한 입력, 출력,
  완료 조건이 있는…
---

# Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기
에이전트에게 모호한 지시를 던지면 가끔은 그럴듯한 결과가 나옵니다. 문제는 그 결과가 재현되지 않는다는 데 있습니다. 어느 날은 괜찮고 어느 날은 틀리는 시스템은 자동화가 아니라 추측입니다.
사람은 흐린 요구를 받으면 되묻지만, 에이전트는 보통 빈칸을 스스로 채웁니다. 그 빈칸이 데이터 소스, 출력 형식, 완료 기준, 권한 범위로 연결되면 작은 모호함이 곧 비용 사고와 품질 흔들림으로 번집니다.
Task Harness는 이 모호함을 실행 계약으로 바꾸는 층입니다. Goal을 Task로 번역하고, 그 Task를 Goal·Inputs·Outputs·Completion Criteria로 고정해야 나머지 harness도 의미를 갖습니다.
이 글의 핵심은 단순합니다. 에이전트에게 Goal을 주지 말고, 실행 가능한 TaskSpec을 주어야 합니다.

![Task Harness - 모호한 일을 실행 가능한 작업으로 바꾸기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-01-task-harness-turning-vague-work-into-exe.ko.png)
*Task Harness - 모호한 일을 실행 가능한 작업으로 바꾸기*
> Task Harness는 “무엇을 원하나”를 “무엇을 실행하고 어떻게 완료를 증명하나”로 바꾸는 층입니다.

## 먼저 던지는 질문

- 모호한 goal을 그대로 agent에게 주면 실행 단계에서 무엇이 깨질까요?
- Task Harness는 goal을 어떤 실행 단위와 완료 조건으로 번역해야 할까요?
- 좋은 task spec은 다음 agent 실행과 사람 리뷰에 어떤 증거를 남겨야 할까요?

## 왜 이 글이 중요한가
Task Harness가 없으면 시스템은 실패 원인을 모델 탓으로 돌리기 쉽습니다. 하지만 실제로는 실행 단위가 정의되지 않아 무엇을 해야 하고 언제 끝난 것인지가 비어 있는 경우가 많습니다.
TaskSpec은 재시도와 테스트의 기준점이기도 합니다. 태스크가 명확해야 어느 단계에서 다시 시작할지, 무엇을 통과로 볼지, 어떤 케이스를 eval에 넣을지 정할 수 있습니다.
또한 Task Harness는 팀 간 계약입니다. PM이 말하는 Goal, 엔지니어가 구현하는 Task, 검증 시스템이 실행하는 Completion Criteria가 같은 문서를 보고 있어야 drift가 줄어듭니다.
## 핵심 관점
Goal은 방향이고 Task는 지금 시스템이 수행할 수 있는 실행 단위입니다. 이 둘을 섞어 두면 에이전트는 비즈니스 목표를 그때그때 해석하는 데 토큰과 판단력을 소모합니다.
Task Harness의 역할은 사람 언어로 들어온 Goal을 기계가 오해 없이 실행할 수 있는 TaskSpec으로 바꾸는 것입니다. 이 번역이 있어야 tool budget도, verification도, retry 정책도 설계할 수 있습니다.
결국 좋은 시스템은 Goal을 직접 실행하지 않습니다. Goal은 사람이 책임지고, Task는 시스템이 책임지는 구조를 만듭니다.
> Goal은 방향이고 Task는 실행 단위입니다. Task Harness는 방향을 그대로 믿지 않고 실행 가능한 명세로 다시 쓰는 장치입니다.
## 핵심 개념
Agent에게 모호한 지시를 던지면 모호한 결과가 돌아옵니다. Task Harness는 모호한 일을 명확한 입력, 출력, 완료 조건이 있는 실행 가능한 작업으로 변환합니다.

### 모호한 일은 실행할 수 없습니다

"우리 팀 보고서를 정리해 줘"라는 지시를 Agent에게 던지면 결과는 보장되지 않습니다. 어떤 보고서를 말하는지, 어디서 가져와야 하는지, 정리한다는 것이 요약인지 재구성인지 형식 변환인지 모호합니다. 사람도 이런 지시를 받으면 다시 묻습니다. Agent는 묻지 않고 추측합니다. 그리고 잘못 추측합니다.

Task Harness는 모호한 일을 명확한 입력, 출력, 완료 조건이 있는 실행 가능한 작업으로 변환하는 설계입니다. 이 변환이 없으면 다른 모든 harness가 의미를 잃습니다. Context도 Constraint도 Test도 모두 "어떤 task를 위한 것인가"에서 시작합니다.

이번 글에서는 Task의 구성 요소, Task Spec 작성법, 그리고 모호한 요구를 실행 가능한 task로 분해하는 방법을 다룹니다.

### Task의 4가지 구성 요소

![Task의 4가지 구성 요소](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-02-the-four-components-of-a-task.ko.png)

*Task의 4가지 구성 요소*

실행 가능한 task는 네 가지를 가집니다.

1. **Goal**: 무엇을 달성해야 하는가. 한 문장으로 적습니다.
2. **Inputs**: Agent가 사용할 수 있는 정보와 자원. 데이터 소스, 파라미터, 사전 조건.
3. **Outputs**: Agent가 만들어야 하는 결과물의 형식과 위치.
4. **Completion criteria**: 끝났는지 판단하는 기준. 자동으로 검증 가능해야 합니다.

이 네 가지가 모두 명시되어 있으면 task는 실행 가능합니다. 하나라도 빠지면 Agent는 추측합니다.

```python
from pydantic import BaseModel, Field
from typing import Any

class TaskSpec(BaseModel):
    """Specification for an executable task."""
    goal: str = Field(..., description="Goal to achieve (one sentence)")
    inputs: dict[str, Any] = Field(..., description="Input data and resources")
    outputs: dict[str, Any] = Field(..., description="Output format and location")
    completion_criteria: list[str] = Field(
        ...,
        description="Conditions to verify completion (automatable)",
    )

    def is_executable(self) -> bool:
        """Check whether the task is executable."""
        return bool(
            self.goal
            and self.inputs
            and self.outputs
            and self.completion_criteria
        )

# 예시: 명확한 작업
task = TaskSpec(
    goal="Generate a daily summary report from sales data for the past 7 days",
    inputs={
        "data_source": "postgres://reports/sales",
        "date_range": {"start": "2026-04-26", "end": "2026-05-02"},
        "filters": {"region": "APAC"},
    },
    outputs={
        "format": "markdown",
        "destination": "s3://reports/daily/2026-05-03.md",
        "schema": "ReportSchema",
    },
    completion_criteria=[
        "All required sections are present",
        "All numeric figures match the source data",
        "File is uploaded to the destination",
    ],
)

assert task.is_executable()
```

`completion_criteria`가 자동 검증 가능해야 한다는 점이 중요합니다. "보고서가 좋아야 한다"는 검증할 수 없습니다. "출력이 ReportSchema를 만족하고, 모든 항목이 비어 있지 않아야 한다"는 검증할 수 있습니다.

### 모호한 요구를 분해하기

![모호한 요구를 분해하기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-03-decomposing-vague-requests-into-tasks.ko.png)

*모호한 요구를 분해하기*

처음에는 사용자나 시스템 요구가 모호한 자연어로 옵니다. Task Harness의 첫 단계는 이를 명확한 TaskSpec으로 변환하는 일입니다.

예시: "지난 분기 매출 보고서를 만들어 줘"

분해 과정:

| 항목 | 모호한 표현 | 명확한 정의 |
| --- | --- | --- |
| Goal | 매출 보고서 만들기 | "2026 Q1 매출을 부서별로 집계한 PDF 보고서 생성" |
| Inputs | (불명) | "sales_db의 2026-01-01 ~ 2026-03-31 transactions 테이블, departments 마스터 테이블" |
| Outputs | (불명) | "ReportSchema(quarter, total_revenue, by_department[], generated_at)" |
| Criteria | "잘 만들어야" | "스키마 검증 통과, 부서 합계 = 전체 합계, generated_at은 현재 시각 ±5분" |

이렇게 분해한 결과를 코드로 옮기면 다음과 같습니다.

```python
def decompose_goal(goal: str) -> list[TaskSpec]:
    """Decompose a Goal into executable Tasks."""
    # 목표: "고객 지원 품질 향상"
    # → Tasks:
    return [
        TaskSpec(
            goal="Answer the 12 unanswered tickets from the past 24 hours",
            inputs={"queue": "support", "status": "unanswered", "max_age_hours": 24},
            outputs={"format": "ticket_reply", "destination": "zendesk"},
            completion_criteria=[
                "All 12 tickets have a reply",
                "Each reply uses an approved template",
                "Each reply links to a knowledge base article",
            ],
        ),
        TaskSpec(
            goal="Group last week's tickets by topic and produce statistics",
            inputs={"date_range": "last_week", "queue": "support"},
            outputs={"format": "json", "destination": "reports/topics.json"},
            completion_criteria=[
                "All tickets are assigned to a topic",
                "Each topic has count and percentage",
                "Top 5 topics include sample ticket IDs",
            ],
        ),
    ]
```

원래 한 문장이 네 가지 항목으로 분해되었습니다. 이제 Agent는 무엇을 해야 하는지 명확히 알고, 시스템은 결과가 끝났는지 판단할 수 있습니다.

### 작은 task로 쪼개기

큰 task는 보통 실행 가능하지 않습니다. "신규 회원 가입 기능을 구현해 줘"는 너무 큽니다. 한 번의 LLM 호출로 처리할 수 없고, 도구 호출 횟수도 예측 불가능합니다. 작은 task로 쪼개야 합니다.

좋은 task 크기의 신호는 다음과 같습니다.

- 한 가지 결과물을 만듭니다.
- 5번 이내의 도구 호출로 끝납니다.
- 완료 조건이 1~3개입니다.
- 사람이 읽으면 무엇을 해야 하는지 즉시 이해됩니다.

위 예시를 쪼개면 다음과 같습니다.

```python
from collections.abc import Callable

class VerifiableTask(TaskSpec):
    """Task with executable completion criteria."""
    verifier: Callable[[Any], bool] = Field(..., exclude=True)

    def verify(self, output: Any) -> bool:
        """Verify the output."""
        return self.verifier(output)

def verify_report(output: dict) -> bool:
    """Verifier for the daily summary report."""
    required_sections = ["summary", "metrics", "anomalies", "next_actions"]
    return (
        all(section in output for section in required_sections)
        and isinstance(output.get("metrics"), dict)
        and len(output.get("anomalies", [])) >= 0
    )

task = VerifiableTask(
    goal="Generate the daily summary report",
    inputs={"date": "2026-05-03"},
    outputs={"format": "json"},
    completion_criteria=[
        "Required sections are present",
        "metrics is a dict",
        "anomalies field exists",
    ],
    verifier=verify_report,
)

# 에이전트의 출력을 검증합니다
result = {"summary": "...", "metrics": {}, "anomalies": [], "next_actions": []}
assert task.verify(result)
```

각 task는 독립적으로 실행 가능하고 검증할 수 있습니다. 큰 작업이 작은 task의 시퀀스로 변환되었습니다. 이를 직접 작성하기 어렵다면 plan 단계를 별도 Agent에게 맡기는 패턴(planner-executor)도 있습니다. 4편에서 다시 다룹니다.

### Task와 Goal의 차이

자주 혼동되는 두 용어를 구분합니다.

| 항목 | Goal | Task |
| --- | --- | --- |
| 추상도 | 높음 | 낮음 |
| 실행 가능성 | 직접 실행 어려움 | 한 번에 실행 가능 |
| 예시 | "고객 만족도를 높인다" | "지난주 NPS 응답을 카테고리별로 분류한다" |
| 완료 판단 | 어려움 | 자동 검증 가능 |

Goal은 비즈니스 목표이고 Task는 실행 단위입니다. Agent에게 Goal을 직접 주면 동작이 모호해집니다. Goal을 여러 Task로 분해해서 주어야 합니다. Task Harness의 본질이 이 분해입니다.

### Completion Criteria 작성법

좋은 completion criteria는 다음 세 가지 조건을 만족합니다.

**1. 객관적입니다.** 사람의 주관 없이 판정 가능해야 합니다.
- 나쁜 예: "보고서가 잘 정리되어 있어야 함"
- 좋은 예: "보고서에 4개 섹션(요약, 매출, 비용, 결론)이 모두 존재함"

**2. 자동 검증 가능합니다.** 코드로 확인할 수 있어야 합니다.
- 나쁜 예: "관련 자료가 충분히 인용되어 있어야 함"
- 좋은 예: "본문에 최소 3개의 footnote가 존재하고, 각 footnote는 유효한 URL을 가짐"

**3. 측정 가능합니다.** 통과/실패가 명확해야 합니다.
- 나쁜 예: "응답이 빨라야 함"
- 좋은 예: "전체 작업이 60초 이내에 완료됨"

코드로 표현하면 다음과 같습니다.

```python
class TaskCandidate(BaseModel):
    """Candidate task — incomplete spec."""
    description: str
    missing_fields: list[str] = []

    def to_spec(self, **filled) -> TaskSpec | None:
        """Convert to a TaskSpec. Returns None if fields are missing."""
        if self.missing_fields:
            return None
        return TaskSpec(**filled)

def request_to_tasks(request: str) -> list[TaskCandidate]:
    """Convert a vague request into task candidates."""
    # 운영 환경에서는 LLM + 템플릿으로 구성합니다.
    return [
        TaskCandidate(
            description="Send a weekly retrospective summary",
            missing_fields=["recipient", "data_source"],
        ),
        TaskCandidate(
            description="Visualize the meeting load",
            missing_fields=["chart_type", "time_range"],
        ),
    ]

# Workflow
candidates = request_to_tasks("Do something about productivity")
for c in candidates:
    if c.missing_fields:
        print(f"Need clarification: {c.description}")
        print(f"  Missing fields: {c.missing_fields}")
```

이렇게 정의된 criteria는 6편의 Test Harness와 직접 연결됩니다. 완료 조건이 곧 테스트 케이스가 됩니다.

### Task Spec을 시스템 프롬프트로 변환하기

![Task Spec을 시스템 프롬프트로 변환하기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/02/02-04-task-spec-as-single-source-of-truth.ko.png)

*Task Spec을 시스템 프롬프트로 변환하기*

TaskSpec을 정의했다면 Agent에게 전달할 시스템 프롬프트를 자동으로 생성할 수 있습니다.

```python
def task_to_system_prompt(task: TaskSpec) -> str:
    """Generate a system prompt from a TaskSpec."""
    criteria = "\n".join(f"- {c}" for c in task.completion_criteria)
    return f"""You are an AI agent.

Goal: {task.goal}

Completion criteria (all required):
{criteria}

Output format: {task.outputs.get('format')}
Output destination: {task.outputs.get('destination')}

Available inputs:
{task.inputs}

Verify each criterion before reporting completion.
"""

def task_to_eval_dataset(task: TaskSpec, n: int = 10) -> list[dict]:
    """Generate eval cases from a TaskSpec."""
    # 입력을 변형하여 테스트 케이스를 생성합니다
    return [
        {"task": task.model_dump(), "variation": i, "expected_pass": True}
        for i in range(n)
    ]
```

이 변환이 있으면 TaskSpec 하나에서 시스템 프롬프트, 검증 함수, 평가 데이터셋이 모두 파생됩니다. Task가 단일 진실 공급원이 됩니다.

### TaskSpec JSON Schema와 계약 테스트

Task Harness를 팀 단위로 운영하면 "문서에는 있는데 런타임에서는 안 지켜지는 필드"가 빠르게 생깁니다. 이 문제를 막으려면 TaskSpec을 JSON Schema로 고정하고, API 입력 단계에서 바로 검증해야 합니다. 사람이 읽는 설명과 기계가 강제하는 계약을 분리하지 않는 것이 핵심입니다.

```python
from jsonschema import Draft202012Validator

TASK_SPEC_SCHEMA = {
    "type": "object",
    "required": [
        "task_id",
        "goal",
        "inputs",
        "outputs",
        "completion_criteria",
        "constraints",
    ],
    "properties": {
        "task_id": {"type": "string", "pattern": r"^task-[a-z0-9\-]{8,}$"},
        "goal": {"type": "string", "minLength": 10, "maxLength": 300},
        "inputs": {
            "type": "object",
            "required": ["source", "parameters"],
            "properties": {
                "source": {"type": "string"},
                "parameters": {"type": "object"},
            },
            "additionalProperties": False,
        },
        "outputs": {
            "type": "object",
            "required": ["format", "destination", "schema"],
            "properties": {
                "format": {"enum": ["json", "markdown", "csv"]},
                "destination": {"type": "string"},
                "schema": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "completion_criteria": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 8},
        },
        "constraints": {
            "type": "object",
            "required": ["max_tool_calls", "max_runtime_seconds", "approval_required"],
            "properties": {
                "max_tool_calls": {"type": "integer", "minimum": 1, "maximum": 20},
                "max_runtime_seconds": {"type": "integer", "minimum": 5, "maximum": 300},
                "approval_required": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

validator = Draft202012Validator(TASK_SPEC_SCHEMA)

def validate_task_spec(payload: dict) -> list[str]:
    return [f"{e.json_path}: {e.message}" for e in validator.iter_errors(payload)]
```

```json
{
  "task_id": "task-refund-20260512",
  "goal": "지난 7일 환불 요청 중 승인 대기 상태를 요약 보고서로 생성한다",
  "inputs": {
    "source": "postgres://ops/refunds",
    "parameters": {
      "from": "2026-05-05",
      "to": "2026-05-12",
      "status": "pending_approval"
    }
  },
  "outputs": {
    "format": "json",
    "destination": "s3://ops-reports/refund-pending-2026-05-12.json",
    "schema": "RefundPendingSummaryV1"
  },
  "completion_criteria": [
    "요약 레코드 수가 원본 조건 쿼리 결과 수와 일치한다",
    "각 항목에 request_id, amount, requested_at, approver_group 필드가 존재한다"
  ],
  "constraints": {
    "max_tool_calls": 6,
    "max_runtime_seconds": 90,
    "approval_required": false
  }
}
```

이 패턴을 쓰면 Task Harness가 문서 표준이 아니라 런타임 계약이 됩니다. 이후 Test Harness에서는 이 스키마 자체를 fixture로 재사용하면 됩니다.
## 흔히 헷갈리는 지점
- Goal을 그대로 Task로 넘기면 시스템이 스스로 잘게 쪼개 줄 것이라고 기대하기 쉽지만, 대부분의 비용 사고와 품질 흔들림이 여기서 시작됩니다.
- completion criteria를 자연어 감상문처럼 적어 두고 나중에 사람이 보겠다고 미루기 쉽지만, 자동 검증이 안 되면 재시도 정책도 만들 수 없습니다.
- 큰 작업 하나가 더 효율적일 것처럼 보여도, 실제로는 작은 태스크 여러 개가 retry, rollback, eval 단위로 훨씬 다루기 쉽습니다.
- 입력을 느슨하게 두고 필요한 데이터는 알아서 찾게 만들면 도구 호출 범위와 비용이 급격히 커집니다.
- 출력 형식을 JSON이라고만 적고 스키마를 생략하면 후속 파이프라인이 불안정해집니다.
## 운영 체크리스트
- [ ] 모든 에이전트 실행 전에 Goal, Inputs, Outputs, Completion Criteria가 모두 채워진 TaskSpec이 존재하는지 확인합니다.
- [ ] 한 태스크가 하나의 산출물만 만들도록 분해합니다.
- [ ] completion criteria를 코드로 표현 가능한 문장으로 다시 씁니다.
- [ ] 필요한 필드가 비어 있는 요청은 추측하지 말고 명확화 질문으로 되돌립니다.
- [ ] 프롬프트, verifier, eval 데이터셋이 같은 TaskSpec에서 파생되는지 점검합니다.
## 정리
Task Harness는 모호한 일을 예쁘게 문서화하는 작업이 아닙니다. 시스템이 무엇을 실행하고 무엇을 검증해야 하는지 오해 없이 고정하는 인터페이스를 만드는 일입니다.
이 글에서 중요한 차이는 Goal과 Task의 분리입니다. Goal은 사람이 책임져야 할 방향이고, Task는 시스템이 책임져야 할 실행 단위입니다. 이 둘을 섞어 두면 나머지 harness도 전부 애매해집니다.
다음 글에서는 Context Harness로 넘어갑니다. Task가 정해졌다면 이제 그 태스크를 풀기 위해 에이전트에게 무엇을 보여주고, 무엇을 의도적으로 숨길지 설계해야 합니다.

## 처음 질문으로 돌아가기

- **모호한 goal을 그대로 agent에게 주면 실행 단계에서 무엇이 깨질까요?**
  - 입력 범위, 성공 기준, 금지 행동이 비어 있어 agent가 임의로 작업을 쪼개거나 끝났다고 착각합니다. 그 결과 반복 호출과 누락이 생깁니다.
- **Task Harness는 goal을 어떤 실행 단위와 완료 조건으로 번역해야 할까요?**
  - 작업 목표, 입력, 허용 범위, 산출물 형식, 완료 기준, 실패 시 멈출 조건으로 번역해야 합니다.
- **좋은 task spec은 다음 agent 실행과 사람 리뷰에 어떤 증거를 남겨야 할까요?**
  - 무엇을 실행했는지, 어떤 기준으로 완료됐는지, 어떤 입력과 제약을 썼는지가 task spec에 남아야 재실행과 리뷰가 가능합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- **Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기 (현재 글)**
- Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기 (예정)
- Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기 (예정)
- Harness Engineering 101 (5/10): Tool Harness — Agent가 사용할 도구를 안전하게 설계하기 (예정)
- Harness Engineering 101 (6/10): Test Harness — 완료 조건을 테스트로 고정하기 (예정)
- Harness Engineering 101 (7/10): Feedback Loop — 실패를 고치게 만드는 반복 구조 (예정)
- Harness Engineering 101 (8/10): Approval Gate — 사람 승인이 필요한 지점 설계하기 (예정)
- Harness Engineering 101 (9/10): Observability — Agent 작업을 추적하고 재현하기 (예정)
- Harness Engineering 101 (10/10): Production Harness — 운영 가능한 Agent 작업 환경 만들기 (예정)

<!-- toc:end -->

## 참고 자료
### 공식 문서

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI — A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [Pydantic Documentation — Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Google — Agent Design Patterns](https://cloud.google.com/architecture/ai-agent-patterns)
### 관련 시리즈

- [LangGraph 101 — 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Safety & Guardrails 101 — 운영 가드레일 시스템 구축](../../ai-safety-guardrails-101/ko/10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/harness-engineering-101/ko/02-task-harness)

Tags: AI Agent, Harness, Production, Reliability
