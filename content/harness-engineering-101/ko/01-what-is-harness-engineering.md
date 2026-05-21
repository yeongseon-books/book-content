---
title: "Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가?"
series: harness-engineering-101
episode: 1
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
last_reviewed: '2026-05-14'
seo_description: 좋은 Agent는 좋은 모델만으로 만들어지지 않습니다. 모델이 일할 수 있는 환경, 제약, 도구, 검증 루프를 함께
  설계해야 합니다.
---

# Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가?
프런티어 모델이 좋아질수록 팀은 같은 기대를 반복합니다. 이제는 정말로 에이전트를 만들 수 있을 것 같고, 더 큰 모델만 쓰면 운영까지 자연스럽게 이어질 것처럼 보입니다. 하지만 실제 프로덕션에서는 같은 모델로도 전혀 다른 결과가 나옵니다.
차이는 대부분 모델이 아니라 환경입니다. 태스크가 모호하고, 컨텍스트가 지저분하고, 도구 권한이 과하게 열려 있고, 완료 조건과 승인 경계가 비어 있으면 모델은 계속 추측합니다. 추측이 쌓이면 시스템은 금방 비싸고 불안정해집니다.
실무에서 저는 이 문제를 모델 품질 문제가 아니라 작업 환경 설계 문제로 봅니다. 좋은 에이전트는 좋은 모델에서만 나오지 않습니다. 모델이 일하는 바깥쪽 구조를 설계해야 비로소 신뢰할 수 있는 시스템이 됩니다.
이 글은 Harness Engineering 101 시리즈의 첫 번째 글입니다.
이 출발점을 정확히 잡아야 뒤에서 다룰 여덟 가지 harness를 각각의 팁이 아니라 하나의 운영 모델로 읽을 수 있습니다.
## 먼저 던지는 질문

- 좋은 모델을 써도 agent가 불안정하다면 먼저 무엇을 의심해야 할까요?
- Harness를 모델 바깥의 작업 환경으로 보면 설계 질문이 어떻게 바뀔까요?
- 프레임워크 선택과 Harness Engineering은 왜 같은 층위의 결정이 아닐까요?

## 큰 그림

![Harness Engineering 개념](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-01-what-is-harness-engineering.ko.png)

*Harness Engineering 개념*

이 그림에서는 모델 자체가 아니라 task, context, constraint, tool, test 같은 바깥 구조가 agent 실행을 지탱하는 모습을 봅니다. Harness Engineering은 모델을 더 세게 밀어붙이는 일이 아니라 모델이 일할 환경을 설계하는 일입니다.

> 좋은 agent는 모델 안쪽보다 모델 바깥의 작업 환경에서 더 많이 결정됩니다.

## 왜 이 글이 중요한가
Harness Engineering을 이해하지 못하면 팀은 계속 모델만 교체합니다. 하지만 같은 입력에 다른 결과가 나오고, 위험한 행동이 자동 실행되고, 무엇이 끝난 상태인지조차 불분명한 문제는 대개 모델 교체로 해결되지 않습니다.
반대로 harness 관점으로 보면 질문 순서가 바뀝니다. 무엇을 해야 하는지, 무엇을 보여줘야 하는지, 어디까지 허용해야 하는지, 어떻게 끝났다고 판정할지부터 정리하게 됩니다. 그 순간 에이전트는 데모가 아니라 운영 가능한 시스템 후보가 됩니다.
특히 시리즈 첫 글에서 이 프레임을 잡아 두는 것이 중요합니다. 뒤의 Task, Context, Constraint, Tool, Test, Feedback, Approval, Observability는 개별 트릭이 아니라 하나의 실행 환경을 나눠 본 설계 층위이기 때문입니다.
## 핵심 관점
Harness는 힘을 묶는 장치가 아니라 원하는 방향으로 전달하는 장치에 가깝습니다. 모델 능력이 있어도 그 힘을 태스크, 컨텍스트, 도구, 검증으로 연결하지 못하면 운영 가능한 결과로 바뀌지 않습니다.
그래서 Harness Engineering은 모델을 바꾸는 기술보다 모델이 일할 수 있는 환경을 정리하는 기술입니다. 모델을 더 똑똑하게 만드는 일보다, 더 덜 망가지게 만드는 일을 먼저 합니다.
이 관점을 잡으면 실패를 보는 방식도 바뀝니다. 답이 이상할 때 모델 탓으로 끝내지 않고, 어떤 harness가 비어 있었는지 역추적하게 됩니다. 이것이 실제 운영에서 훨씬 유용한 디버깅 방식입니다.
> 좋은 에이전트는 모델 안쪽보다 모델 바깥쪽에서 더 많이 결정됩니다. Harness Engineering은 그 바깥쪽을 설계하는 일입니다.
## 핵심 개념
좋은 Agent는 좋은 모델만으로 만들어지지 않습니다. 모델이 일할 수 있는 환경, 제약, 도구, 검증 루프를 함께 설계해야 합니다. Harness Engineering은 Agent가 안정적으로 일하도록 환경을 설계하는 일입니다.

### 좋은 모델만으로는 부족합니다

GPT-4, Claude 3.5, Gemini 1.5 같은 최신 모델이 등장할 때마다 "이제는 진짜 Agent가 가능하다"는 기대가 따라옵니다. 하지만 같은 모델로 누군가는 안정적인 자동화 시스템을 만들고, 누군가는 매번 다른 결과를 받으며 좌절합니다. 차이는 모델이 아니라 **모델 주변의 환경**에 있습니다.

같은 사람이라도 책상이 어지럽고 도구가 망가져 있으면 좋은 결과를 내기 어렵습니다. Agent도 마찬가지입니다. 모델에게 적절한 작업 정의, 깨끗한 컨텍스트, 안전한 도구, 명확한 완료 조건, 실패를 회복할 루프, 위험한 행동에 대한 승인 흐름, 그리고 무엇을 했는지 추적할 관측 가능성이 없으면 능력 있는 모델도 무능해 보입니다.

Harness Engineering은 이 환경을 설계하는 일입니다. 좋은 Agent를 만드는 일은 좋은 모델을 고르는 일이 아니라, 모델이 잘 일할 수 있는 시스템을 짓는 일입니다.

### Harness란 무엇인가

영어 "harness"는 말이나 동물에 채우는 마구를 뜻합니다. 단순히 묶는 도구가 아니라 동물의 힘을 원하는 방향으로 전달하기 위한 장치입니다. 마구가 없으면 말의 힘은 분산되고 통제가 안 됩니다. 마구가 있으면 같은 말이 마차를 끌고 밭을 갈고 사람을 태웁니다.

Harness Engineering의 harness도 같은 의미입니다. AI 모델의 능력을 원하는 방향으로 전달하기 위한 장치입니다. 모델 자체를 바꾸지 않고 모델이 일하는 환경, 입력, 제약, 도구, 검증을 설계함으로써 모델이 안정적으로 일하게 만듭니다.

소프트웨어 엔지니어링에서 harness라는 단어는 이미 쓰입니다. 테스트 harness는 함수가 동작하는 환경(setup, teardown, fixture)을 제공합니다. 임베디드 시스템의 cable harness는 여러 부품을 정해진 방식으로 연결합니다. AI Agent harness도 같은 발상입니다. 모델이 동작할 환경을 미리 짜 놓고, 모델은 그 안에서 일합니다.

### Harness가 없는 Agent와 있는 Agent

![Harness가 없는 Agent와 있는 Agent](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-02-agents-without-and-with-a-harness.ko.png)

Harness 없이 Agent를 만들면 다음 같은 코드가 됩니다.

```python
from openai import OpenAI

client = OpenAI()

def run_agent(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}],
    )
    return response.choices[0].message.content or ""

# Usage
answer = run_agent("Build a sales report for our company")
print(answer)
```

이 Agent는 한 번 답하고 끝납니다. 도구가 없고, 메모리가 없고, 검증도 없습니다. 결과가 좋은지 나쁜지 판단할 방법이 없고, 같은 질문에 매번 다른 답이 옵니다. 프로덕션에서는 쓸 수 없습니다.

같은 작업을 harness가 있는 Agent로 만들면 다음과 같이 변합니다.

```python
from typing import Any
from pydantic import BaseModel

class TaskSpec(BaseModel):
    """Task Harness: clear inputs and completion criteria."""
    goal: str
    inputs: dict[str, Any]
    completion_criteria: list[str]

class AgentContext(BaseModel):
    """Context Harness: what to show and what to hide."""
    system_prompt: str
    allowed_data_sources: list[str]
    forbidden_topics: list[str]

class ToolPolicy(BaseModel):
    """Constraint + Tool Harness: allowed and forbidden actions."""
    allowed_tools: list[str]
    require_approval: list[str]
    max_iterations: int = 5

def run_agent_with_harness(task: TaskSpec, ctx: AgentContext, policy: ToolPolicy) -> dict[str, Any]:
    """Agent execution with harnesses applied."""
    trace = []  # Observability Harness: record every step

    for iteration in range(policy.max_iterations):
        decision = think_with_context(task, ctx, trace)
        trace.append({"iteration": iteration, "decision": decision})

        if decision["action"] in policy.require_approval:
            if not request_human_approval(decision):
                trace.append({"approval": "denied"})
                break

        result = execute_tool(decision, policy.allowed_tools)
        trace.append({"result": result})

        if check_completion(result, task.completion_criteria):
            return {"status": "success", "trace": trace, "result": result}

    return {"status": "incomplete", "trace": trace}
```

코드량은 늘어났지만 이제 이 Agent는 다음을 보장합니다.

- 무엇을 해야 하는지 명확합니다 (Task Harness).
- 어떤 정보를 보고 어떤 정보를 숨길지 정해져 있습니다 (Context Harness).
- 어떤 도구를 쓰고 어떤 행동에 사람 승인이 필요한지 명시되어 있습니다 (Constraint Harness).
- 무한 루프를 막는 한계가 있습니다 (Tool Harness).
- 무엇을 했는지 모두 기록됩니다 (Observability).

같은 모델이지만 결과는 완전히 다릅니다.

문서 수준 설명에서 한 걸음 더 내려오면 차이가 더 분명해집니다. Harness가 없는 쪽은 사실상 "자연어를 한번 흘려보내고 답을 받는 호출"에 가깝습니다. 반면 Harness가 있는 쪽은 태스크 명세, 허용 도구, 승인 경계, 완료 판정, 추적 로그를 시스템 바깥에서도 읽을 수 있는 실행으로 바뀝니다.

```text
Harness 없는 실행
- 입력: "영업 보고서를 만들어 줘"
- 출력: 자유 형식 텍스트
- 검증: 없음
- 재현 경로: 없음

Harness 있는 실행
- 입력: TaskSpec + 범위가 정해진 Context + ToolPolicy
- 출력: 구조화된 결과 + trace
- 검증: completion criteria 검사 가능
- 재현 경로: trace와 도구 호출 기록 존재
```

**Expected output:** Harness가 있는 버전은 다른 시스템이 받아서 통과/실패를 판정하거나 사람 승인을 걸 수 있는 형태를 남깁니다. Harness가 없는 버전은 답변 문자열만 남기기 쉽습니다.

### 8가지 Harness 개요

![8가지 Harness 개요](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-03-the-eight-harnesses.ko.png)

이 시리즈는 다음 여덟 가지 harness를 다룹니다. 각각은 Agent의 한 측면을 설계합니다.

| Harness | 다루는 질문 | 회 차 |
| --- | --- | --- |
| Task | "Agent가 무엇을 해야 하는가" | 2 |
| Context | "Agent에게 무엇을 보여줄 것인가" | 3 |
| Constraint | "Agent가 무엇을 하면 안 되는가" | 4 |
| Tool | "Agent가 무엇을 사용할 수 있는가" | 5 |
| Test | "끝났는지 어떻게 확인하는가" | 6 |
| Feedback | "실패하면 어떻게 회복하는가" | 7 |
| Approval | "사람이 어디서 멈춰야 하는가" | 8 |
| Observability | "무엇을 했는지 어떻게 추적하는가" | 9 |

10편에서는 이 모든 harness를 한 시스템으로 통합한 Production Harness를 만듭니다.

각 harness는 독립적이지 않습니다. Tool Harness는 Constraint Harness 안에서 정의되고, Approval Gate는 Tool Harness의 특정 행동을 가로챕니다. Observability는 모든 harness의 상태를 기록합니다. 8가지를 함께 설계해야 일관된 시스템이 됩니다.

### Harness vs Framework

LangChain, LangGraph, CrewAI 같은 프레임워크와 Harness Engineering의 관계를 자주 묻습니다. 둘은 다른 층위입니다.

| 항목 | 프레임워크 | Harness Engineering |
| --- | --- | --- |
| 무엇 | 코드 라이브러리 | 설계 원칙과 패턴 |
| 제공 | API, 추상화, 유틸리티 | 어떤 환경을 만들지에 대한 의사결정 |
| 예시 | LangGraph 노드/엣지 | Task Harness 정의 |
| 선택 | 한 번 결정 | 매 Agent마다 설계 |

프레임워크는 도구이고 Harness Engineering은 그 도구로 무엇을 짤지에 대한 사고법입니다. LangGraph로도 harness가 없는 Agent를 만들 수 있고, 표준 라이브러리만으로도 harness가 잘 갖춰진 Agent를 만들 수 있습니다.

실제로는 이렇게 결합합니다. Harness Engineering으로 "이 Agent는 어떤 task, context, constraint, tool, test, feedback, approval, observability를 가져야 하는가"를 먼저 설계합니다. 그다음 그 설계를 코드로 옮길 때 LangGraph나 CrewAI 같은 프레임워크의 추상화를 사용합니다. 설계가 먼저고 프레임워크는 그다음입니다.

### Harness Engineering이 필요한 시점

모든 LLM 사용에 harness가 필요한 것은 아닙니다. 다음 신호가 보이면 harness 설계를 시작해야 합니다.

Agent가 비결정적으로 동작한다면 Task와 Context Harness가 부족하다는 뜻입니다. 입력 정의와 컨텍스트 범위가 명확하지 않습니다.

사용자가 "왜 이렇게 답했냐"고 물었을 때 답할 수 없다면 Observability Harness가 없습니다. 모든 결정과 도구 호출이 기록되어야 합니다.

DB 삭제, 메일 발송, 결제 같은 행동을 사람 확인 없이 한다면 Approval Gate가 필요합니다.

Agent가 같은 검색을 100번 반복하거나 무한 루프에 빠진다면 Constraint와 Tool Harness가 부족합니다.

Test Harness가 없으면 Agent가 "완료했습니다"라고 말해도 진짜 완료인지 알 수 없습니다.

이 중 하나라도 해당하면 모델 교체로는 해결되지 않습니다. Harness 설계가 필요합니다.

### 작은 예: 이메일 분류 Agent

![작은 예: 이메일 분류 Agent](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/01/01-04-a-small-example-email-classification-age.ko.png)

추상적인 설명을 끝내고 작은 사례를 봅니다. "들어오는 이메일을 우선순위별로 분류한다"는 작업을 harness 없이 짜면 다음과 같습니다.

```python
def classify_email(email_body: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Classify the email as high, medium, or low."},
            {"role": "user", "content": email_body},
        ],
    )
    return response.choices[0].message.content or ""
```

문제가 많습니다. 출력 형식이 보장되지 않습니다. 같은 메일에 다른 결과가 나옵니다. 분류 기준이 모호합니다. 잘못된 분류를 감지할 방법이 없습니다.

Harness를 적용하면 다음과 같이 바뀝니다.

```python
from enum import Enum
from pydantic import BaseModel, Field

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ClassificationResult(BaseModel):
    """Test Harness: schema pins down completion criteria."""
    priority: Priority
    reason: str = Field(..., min_length=10)
    confidence: float = Field(..., ge=0.0, le=1.0)

SYSTEM_PROMPT = """You are an email priority classifier.

Classification criteria (Context Harness):
- high: response required within 24 hours. Customer complaints, payment failures, security issues.
- medium: response required within 3 business days. General inquiries, feature requests.
- low: response optional. Marketing, notifications, automated emails.

Rules (Constraint Harness):
- Use only one of the three categories above.
- Reason must be a single sentence explaining the basis for the label.
- Confidence must be a number between 0.0 and 1.0.
- Do not infer information not present in the email body."""

def classify_email_with_harness(email_body: str) -> ClassificationResult:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_body},
        ],
        response_format=ClassificationResult,  # Test Harness
    )
    return ClassificationResult.model_validate_json(response.choices[0].message.content)
```

이제 이 함수는 다음을 보장합니다.

- 출력은 항상 `ClassificationResult` 스키마를 따릅니다 (Test Harness).
- 분류 기준이 시스템 프롬프트에 명시되어 있습니다 (Context Harness).
- 허용되지 않은 카테고리는 나오지 않습니다 (Constraint Harness).
- `confidence`로 낮은 확신도를 감지하고 사람 검토로 보낼 수 있습니다 (Approval 연계).

같은 모델, 같은 작업이지만 harness가 있는 버전은 프로덕션에서 쓸 수 있는 시스템입니다.

### 아주 작은 검증기부터 붙여 보기

Harness의 가치는 설명보다 검증기에서 더 선명하게 드러납니다. 결과를 구조화해 두면 테스트, 피드백 루프, 승인 게이트가 같은 기준을 공유할 수 있습니다.

```python
from pydantic import BaseModel, ValidationError

class ReportResult(BaseModel):
    title: str
    summary: str
    next_actions: list[str]

def verify_report_result(payload: dict) -> tuple[bool, str]:
    try:
        result = ReportResult.model_validate(payload)
    except ValidationError as exc:
        return False, f"schema validation failed: {exc.errors()}"

    if len(result.next_actions) < 2:
        return False, "후속 액션은 최소 2개여야 합니다."

    return True, "pass"
```

이 검증기는 단순하지만 중요한 분기점을 만듭니다. 이제 시스템은 "완료했습니다"라는 자연어 선언을 곧바로 믿지 않고, 스키마와 최소 품질 기준을 바깥에서 다시 확인할 수 있습니다.

### Harness가 없을 때 가장 먼저 깨지는 것

실무에서 처음 드러나는 실패는 대개 모델 지능 부족이 아닙니다. 보통 다음 셋 중 하나입니다.

- 같은 요청을 실행할 때마다 출력 형식이 달라집니다.
- 위험한 도구가 노출되어 초안 작성이 실제 실행으로 번집니다.
- 무엇을 근거로 그렇게 답했는지 추적할 기록이 없습니다.

이 세 실패는 모두 프롬프트를 조금 더 길게 쓰는 것으로는 잘 해결되지 않습니다. Task, Tool, Observability Harness가 빠졌다는 신호로 읽는 편이 훨씬 빠릅니다.
## 흔히 헷갈리는 지점
- 모델을 바꾸면 시스템 신뢰성도 자동으로 올라간다고 생각하기 쉽지만, harness가 없으면 좋은 모델도 불안정한 자동화로 끝납니다.
- Harness를 프레임워크 기능 목록처럼 이해하면 설계 책임이 사라집니다. 프레임워크는 구현 도구이고 harness는 운영 설계입니다.
- 처음부터 여덟 가지를 한 번에 완성해야 한다고 생각하기 쉽지만, 실제로는 Task와 Context부터 시작해 통증 지점에 맞춰 확장하는 편이 낫습니다.
- Observability를 나중에 붙이면 된다고 미루기 쉽지만, 기록이 없으면 나중에 무엇을 고쳐야 하는지도 알 수 없습니다.
- 테스트 환경에서는 Approval Gate가 없어도 된다고 생각하기 쉽지만, 위험한 도구는 환경과 무관하게 처음부터 게이트를 거치는 편이 안전합니다.
## 운영 체크리스트
- [ ] 모델 선택 전에 Task, Context, Constraint, Tool, Test, Feedback, Approval, Observability 중 무엇이 비어 있는지 먼저 점검합니다.
- [ ] 같은 입력에 다른 결과가 나올 때 프롬프트 길이보다 task 정의와 context 범위를 먼저 확인합니다.
- [ ] 위험한 행동을 수행하는 도구는 Approval Gate 없이 직접 노출하지 않습니다.
- [ ] 결과 품질뿐 아니라 trace, 비용, 재현 가능성까지 포함해 시스템을 평가합니다.
- [ ] 프레임워크 도입 문서와 별도로 harness 설계 문서를 유지합니다.
## 정리
Harness Engineering은 좋은 모델을 고르는 기술이 아니라, 모델이 좋은 결과를 낼 수밖에 없도록 환경을 설계하는 기술입니다. 이 관점을 놓치면 팀은 계속 모델을 바꾸고 프롬프트를 덧붙이면서도, 왜 시스템이 불안정한지 설명하지 못합니다.
이 글에서 가장 먼저 가져가야 할 문장은 단순합니다. 에이전트 품질은 모델 안쪽보다 모델 바깥쪽에서 더 많이 결정됩니다. 태스크, 컨텍스트, 제약, 도구, 검증, 피드백, 승인, 관측성은 부가 옵션이 아니라 운영 환경의 본체입니다.
다음 글부터는 그 환경을 구성하는 각 harness를 하나씩 분해합니다. 첫 번째 출발점은 Task Harness입니다. 모호한 일을 실행 가능한 작업으로 바꾸지 못하면, 나머지 harness도 설 자리가 없습니다.

## 처음 질문으로 돌아가기

- **좋은 모델을 써도 agent가 불안정하다면 먼저 무엇을 의심해야 할까요?**
  - 모델 성능보다 task 정의, context, tool 권한, 완료 검증, 승인 경계가 비어 있는지 먼저 봐야 합니다. 같은 모델도 환경이 다르면 전혀 다르게 동작합니다.
- **Harness를 모델 바깥의 작업 환경으로 보면 설계 질문이 어떻게 바뀔까요?**
  - 질문이 “어떤 모델을 쓸까”에서 “무엇을 시킬까, 무엇을 보여줄까, 어디까지 허용할까, 어떻게 끝났다고 볼까”로 바뀝니다.
- **프레임워크 선택과 Harness Engineering은 왜 같은 층위의 결정이 아닐까요?**
  - 프레임워크는 실행을 도와주는 도구이고 harness는 그 실행이 안전하고 검증 가능하도록 만드는 운영 설계층입니다. 프레임워크를 바꿔도 harness 질문은 남습니다.

<!-- toc:begin -->
## 시리즈 목차

- **Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가? (현재 글)**
- Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기 (예정)
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

- [Building Effective Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [LLM Powered Autonomous Agents — Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [The Rise of Agent Engineering](https://www.langchain.com/blog)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
### 관련 시리즈

- [LangGraph 101 — 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Safety & Guardrails 101 — 운영 가드레일 시스템 구축](../../ai-safety-guardrails-101/ko/10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/harness-engineering-101/ko/01-what-is-harness-engineering)

Tags: AI Agent, Harness, Production, Reliability
