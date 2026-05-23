---
title: "Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기"
series: harness-engineering-101
episode: 4
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
- Security
- Policy
last_reviewed: '2026-05-14'
seo_description: Agent에게 자유를 주면 창의적이지만 위험합니다. Constraint Harness는 어떤 행동이 허용되고 어떤 행동이
  금지되는지 명시하는…
---

# Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기
에이전트에 도구와 권한을 붙이는 순간 시스템은 유능해지지만 동시에 위험해집니다. 읽기 전용이어야 할 작업이 쓰기 권한을 갖고, 초안만 작성해야 할 작업이 실제 발송까지 하는 식의 사고가 여기서 시작됩니다.
사람은 상식과 조직 규범으로 경계를 어느 정도 추론합니다. 에이전트는 그렇지 않습니다. 명시적으로 금지되지 않은 행동은 허용된 행동으로 해석하는 쪽에 가깝습니다.
Constraint Harness는 프롬프트에 적힌 훈계문이 아니라 시스템이 반드시 통과해야 하는 강제 장치의 모음입니다. 어떤 도구를 보일지, 얼마나 오래 실행할지, 어떤 출력은 차단할지, 어떤 데이터 범위 밖으로는 못 나가게 할지를 따로 설계해야 합니다.
이 글은 Harness Engineering 101 시리즈의 4번째 글입니다.
안전한 에이전트는 착한 프롬프트보다 우회하기 어려운 제약에서 나옵니다.

![Constraint Harness - 규칙, 경계, 금지 행동 정의하기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/04/04-01-constraint-harness-defining-rules-bounda.ko.png)
*Constraint Harness - 규칙, 경계, 금지 행동 정의하기*
> Constraint Harness는 agent에게 “하지 마”라고 말하는 것이 아니라, 할 수 없는 경계를 시스템에 만드는 일입니다.

## 먼저 던지는 질문

- Constraint Harness는 prompt 규칙과 무엇이 달라야 실제로 agent 행동을 제한할까요?
- capability, resource, behavior, scope 제약은 각각 어떤 위험을 막을까요?
- 제약이 실행 계약이 되려면 코드와 로그에 무엇이 남아야 할까요?

## 왜 이 글이 중요한가
Constraint Harness가 중요한 첫 번째 이유는 사고 반경입니다. 잘못된 판단 하나가 데이터 수정, 외부 발송, 비용 폭증으로 이어질 수 있기 때문입니다.
두 번째 이유는 운영 비용입니다. 무한 루프, 과도한 도구 호출, 넓은 검색 범위는 대부분 품질보다 먼저 비용 문제로 드러납니다.
세 번째 이유는 신뢰 가능한 안전성입니다. 시스템 프롬프트에 적힌 금지 문장은 문서화일 뿐이고, 실제 안전성은 노출 제한과 실행 한도, 데이터 계층 제약에서 나옵니다.
## 핵심 관점
에이전트 제약은 하나의 큰 윤리 선언이 아니라 capability, resource, behavioral, scope처럼 여러 메커니즘으로 분리된 실행 계약입니다.
실무에서는 프롬프트보다 메커니즘이 먼저입니다. 위험한 도구를 보여 주고 쓰지 말라고 적는 것은 제약이 아닙니다. 토큰 상한 없이 짧게 끝내라고 적는 것도 제약이 아닙니다.
좋은 설계는 늘 묻습니다. 이 규칙은 어디서 집행되는가, 어떻게 우회될 수 있는가, 로그에는 어떻게 남는가. 이 질문에 답하지 못하는 규칙은 운영에서 무력해지기 쉽습니다.
> 안전한 에이전트는 착한 프롬프트에서 나오지 않습니다. 우회하기 어려운 계층에 제약을 걸고 위반 순간 실행을 멈출 수 있을 때 비로소 안전해집니다.
## 핵심 개념
Agent에게 자유를 주면 창의적이지만 위험합니다. Constraint Harness는 어떤 행동이 허용되고 어떤 행동이 금지되는지 명시하는 규칙 체계입니다.

### Agent는 허용된 모든 것을 시도합니다

Agent에게 도구와 권한을 주면 그것을 모두 시도합니다. "고객 데이터를 분석해 줘"라는 task에 데이터베이스 쓰기 권한이 있다면, 분석 도중에 데이터를 수정할 수도 있습니다. "이메일 초안을 작성해 줘"라고 했는데 발송 도구가 노출되어 있다면, 초안을 그대로 보낼 수도 있습니다.

LLM은 명시적으로 금지되지 않은 행동을 안전하다고 가정합니다. 인간은 사회적 규범과 상식으로 경계를 만듭니다. Agent에게는 그런 것이 없습니다. 명시적인 제약이 곧 안전입니다.

Constraint Harness는 Agent가 무엇을 해도 되고 무엇을 하면 안 되는지를 코드로 표현된 규칙으로 정의합니다. 이번 글에서는 제약의 종류, 정책 엔진 설계, 그리고 제약 위반을 감지하는 방법을 다룹니다.

### 제약의 4가지 종류

![제약의 4가지 종류](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/04/04-02-four-kinds-of-constraints.ko.png)

*제약의 4가지 종류*

Agent에 가하는 제약은 네 가지로 분류됩니다.

**1. Capability constraints**: 어떤 도구를 쓸 수 있는가. 화이트리스트 방식으로 정의합니다.

**2. Resource constraints**: 얼마나 쓸 수 있는가. 토큰, API 호출, 시간, 비용의 상한.

**3. Behavioral constraints**: 어떻게 행동해야 하는가. 금지된 출력 패턴, 필수 형식, 우선순위.

**4. Scope constraints**: 어디까지 영향을 미칠 수 있는가. 접근 가능한 데이터, 수정 가능한 리소스의 범위.

각 종류는 다른 메커니즘으로 강제됩니다. Capability는 도구 노출 단계에서, Resource는 실행 시간 측정으로, Behavioral은 출력 검증으로, Scope는 데이터 레이어 권한으로.

```python
from dataclasses import dataclass, field
from enum import Enum

class ConstraintType(Enum):
    CAPABILITY = "capability"
    RESOURCE = "resource"
    BEHAVIORAL = "behavioral"
    SCOPE = "scope"

@dataclass
class Constraint:
    """A single constraint definition."""
    name: str
    type: ConstraintType
    rule: str  # Human-readable rule
    enforcer: str  # Identifier of the enforcement mechanism

@dataclass
class ConstraintPolicy:
    """The set of constraints applied to a task."""
    task_id: str
    constraints: list[Constraint] = field(default_factory=list)

    def by_type(self, t: ConstraintType) -> list[Constraint]:
        return [c for c in self.constraints if c.type == t]

policy = ConstraintPolicy(
    task_id="generate-report",
    constraints=[
        Constraint("read-only", ConstraintType.CAPABILITY, "Read-only DB access", "tool-filter"),
        Constraint("max-cost", ConstraintType.RESOURCE, "Max 0.5 USD", "cost-meter"),
        Constraint("no-pii", ConstraintType.BEHAVIORAL, "No PII in output", "output-validator"),
        Constraint("apac-only", ConstraintType.SCOPE, "APAC region only", "row-filter"),
    ],
)
```

이 4분류 없이 "Agent가 안전하게 동작하도록"이라는 추상적인 요구만 있으면 강제가 불가능합니다.

### Capability Constraints — 도구 화이트리스트

![Capability Constraints - 도구 화이트리스트](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/04/04-03-capability-constraints-tool-whitelisting.ko.png)

*Capability Constraints - 도구 화이트리스트*

가장 단순하고 효과적인 제약은 도구 노출을 제한하는 것입니다. Agent는 받지 않은 도구를 호출할 수 없습니다.

핵심 원칙은 화이트리스트입니다. "이 도구는 금지"가 아니라 "이 도구만 허용". 블랙리스트는 새 도구가 추가될 때마다 업데이트해야 하지만, 화이트리스트는 명시적으로 추가하지 않으면 자동으로 차단됩니다.

```python
from collections.abc import Callable
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    description: str
    handler: Callable
    danger_level: int  # 0 (safe) to 5 (destructive)

class ToolRegistry:
    """Registers all tools and filters them per task."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def expose(self, allowed_names: set[str], max_danger: int = 2) -> list[Tool]:
        """Expose only allowed tools within the danger threshold."""
        return [
            t for name, t in self._tools.items()
            if name in allowed_names and t.danger_level <= max_danger
        ]

registry = ToolRegistry()
registry.register(Tool("read_db", "Query DB", lambda q: ..., danger_level=0))
registry.register(Tool("write_db", "Modify DB", lambda r: ..., danger_level=4))
registry.register(Tool("send_email", "Send email", lambda m: ..., danger_level=3))

# 작업: 분석 보고서 생성 — 읽기 전용
exposed = registry.expose(allowed_names={"read_db"}, max_danger=2)
assert all(t.name == "read_db" for t in exposed)
```

danger_level은 두 번째 보호막입니다. 실수로 위험한 도구를 화이트리스트에 넣어도, danger 임계값이 막아 줍니다.

### Resource Constraints — 비용과 시간의 상한

Agent는 무한 루프에 빠질 수 있습니다. 잘못된 도구 호출을 100번 반복할 수도 있고, 검색을 30번 더 시도할 수도 있습니다. Resource constraint는 이 사고를 비용으로 막습니다.

세 가지를 측정합니다.

**1. Token budget**: 누적 입력+출력 토큰의 상한.
**2. Tool call budget**: task당 최대 도구 호출 수.
**3. Wall clock budget**: 전체 실행 시간 상한.

```python
import time
from dataclasses import dataclass, field

@dataclass
class ResourceMeter:
    """Tracks resource use and enforces caps."""
    max_tokens: int = 50_000
    max_tool_calls: int = 20
    max_wall_seconds: float = 60.0

    used_tokens: int = 0
    used_tool_calls: int = 0
    started_at: float = field(default_factory=time.time)

    def record_tokens(self, n: int) -> None:
        self.used_tokens += n
        if self.used_tokens > self.max_tokens:
            raise ResourceExhausted(f"token budget exceeded: {self.used_tokens}/{self.max_tokens}")

    def record_tool_call(self) -> None:
        self.used_tool_calls += 1
        if self.used_tool_calls > self.max_tool_calls:
            raise ResourceExhausted(f"tool call budget exceeded: {self.used_tool_calls}/{self.max_tool_calls}")

    def check_wall_clock(self) -> None:
        elapsed = time.time() - self.started_at
        if elapsed > self.max_wall_seconds:
            raise ResourceExhausted(f"wall clock exceeded: {elapsed:.1f}s")

class ResourceExhausted(Exception):
    pass
```

상한을 정하지 않은 Agent는 production에서 비용 사고로 이어집니다. 실제 사례로 한 번의 잘못된 task가 수천 USD를 태운 보고가 여러 번 있었습니다. ResourceMeter는 보험입니다.

### Behavioral Constraints — 출력 정책

Agent가 만드는 출력에도 규칙이 있어야 합니다. PII를 포함하면 안 되고, 특정 형식을 따라야 하고, 금지된 톤을 쓰면 안 됩니다.

이 제약은 두 단계로 강제합니다.

**1. Pre-output validation**: 출력 직전에 schema와 정책을 검사합니다. 위반하면 재생성을 요청합니다.

**2. Post-output filtering**: 사용자에게 보내기 전에 마지막 필터를 적용합니다. PII 마스킹, 금칙어 치환.

```python
import re
from typing import Protocol

class OutputPolicy(Protocol):
    def check(self, output: str) -> tuple[bool, str]:
        """Returns (passed, reason)."""
        ...

class NoSecrets:
    """Checks output contains no secrets."""
    def check(self, output: str) -> tuple[bool, str]:
        if re.search(r"sk-[a-zA-Z0-9]{20,}", output):
            return False, "API key detected"
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", output):
            return False, "SSN detected"
        return True, ""

class ApprovedTone:
    """Allows only approved tone."""
    BANNED_PHRASES = {"absolutely guaranteed", "100% safe", "no risk"}

    def check(self, output: str) -> tuple[bool, str]:
        lower = output.lower()
        for phrase in self.BANNED_PHRASES:
            if phrase in lower:
                return False, f"banned phrase: {phrase}"
        return True, ""

def enforce_policies(output: str, policies: list[OutputPolicy]) -> None:
    for p in policies:
        ok, reason = p.check(output)
        if not ok:
            raise PolicyViolation(reason)

class PolicyViolation(Exception):
    pass
```

위반이 발견되면 Agent에게 재생성을 요청합니다. 단순한 차단이 아니라 "이런 이유로 거부됨, 다시 시도"라는 피드백이 핵심입니다 (다음 글의 Feedback Loop 주제).

### Scope Constraints — 데이터 레이어 권한

![Scope Constraints - 데이터 레이어 권한](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/04/04-04-scope-constraints-permissions-at-the-dat.ko.png)

*Scope Constraints - 데이터 레이어 권한*

가장 강력한 제약은 데이터 레이어에서 만듭니다. Agent가 아무리 잘못된 쿼리를 보내도, DB가 권한 밖 데이터를 반환하지 않으면 안전합니다.

이 패턴은 row-level security 또는 view-based access로 구현합니다. Agent에게 직접 테이블 접근을 주지 않고, task에 맞춘 view나 filtered query만 노출합니다.

```python
from dataclasses import dataclass

@dataclass
class ScopedDataAccess:
    """Restricts data access to the task's scope."""
    user_id: str
    region: str
    allowed_tables: set[str]

    def query(self, sql: str) -> list[dict]:
        """Validates SQL and enforces scope."""
        self._validate_tables(sql)
        scoped_sql = self._inject_filters(sql)
        return self._execute(scoped_sql)

    def _validate_tables(self, sql: str) -> None:
        # 단순 검사 — 운영 환경에서는 실제 SQL 파서를 사용하세요
        for table in ["users", "orders", "payments"]:
            if table in sql.lower() and table not in self.allowed_tables:
                raise ScopeViolation(f"table not allowed: {table}")

    def _inject_filters(self, sql: str) -> str:
        # WHERE 절에 지역 필터를 주입합니다
        if "where" in sql.lower():
            return sql + f" AND region = '{self.region}'"
        return sql + f" WHERE region = '{self.region}'"

    def _execute(self, sql: str) -> list[dict]:
        return []

class ScopeViolation(Exception):
    pass
```

데이터 레이어 제약은 Agent의 잘못된 동작이 어떻게 발생하든 영향 범위를 막아줍니다. application 레이어 제약보다 우회가 어렵고, audit log도 더 신뢰할 수 있습니다.

### 정책 구성 파일과 위반 코드 체계

Constraint Harness를 확장 가능한 시스템으로 운영하려면 정책을 코드에서 분리해야 합니다. 아래처럼 YAML에 정책을 선언하고, 실행 단계에서는 위반 코드를 구조화해 반환하면 approval, alert, postmortem에서 같은 분류를 재사용할 수 있습니다.

```yaml
# constraint_policy.yaml
policy_id: policy-support-v3
capability:
  allowed_tools: [read_ticket, search_kb, summarize_case]
  denied_tools: [send_email, write_db]
resource:
  max_prompt_tokens: 18000
  max_completion_tokens: 2000
  max_tool_calls: 8
  max_runtime_seconds: 75
behavioral:
  deny_regex:
    - '(?i)sk-[a-z0-9]{20,}'
    - '(?i)password\s*[:=]'
scope:
  allowed_regions: [apac]
  allowed_tables: [tickets, kb_articles]
```

```python
from enum import Enum
from dataclasses import dataclass

class ViolationCode(Enum):
    TOOL_NOT_ALLOWED = "tool_not_allowed"
    TOKEN_BUDGET_EXCEEDED = "token_budget_exceeded"
    TOOL_BUDGET_EXCEEDED = "tool_budget_exceeded"
    OUTPUT_POLICY_VIOLATION = "output_policy_violation"
    SCOPE_VIOLATION = "scope_violation"

@dataclass
class Violation:
    code: ViolationCode
    message: str
    block: bool

def enforce_tool_allowlist(tool_name: str, allowed: set[str]) -> Violation | None:
    if tool_name not in allowed:
        return Violation(
            code=ViolationCode.TOOL_NOT_ALLOWED,
            message=f"tool '{tool_name}' is not in allowlist",
            block=True,
        )
    return None
```

운영 관점에서 중요한 점은 위반이 발생했을 때 단순 텍스트가 아니라 코드로 남기는 것입니다. scope_violation이 급증하면 데이터 접근 정책을 먼저 보고, token_budget_exceeded가 늘면 Context Harness의 budget 분배를 먼저 점검하는 식으로 대응 우선순위가 선명해집니다.

제약 시스템은 배포 후에도 drift를 감시해야 합니다. 예를 들어 `tool_not_allowed` 위반이 갑자기 0으로 떨어진다면 안전해진 것이 아니라, 우회 경로로 직접 API 호출이 생겼을 가능성도 있습니다. 반대로 `output_policy_violation`이 증가하면 prompt 변경보다 입력 데이터의 분포 변화를 먼저 의심해야 합니다. Constraint Harness는 정책 정의와 집행 로그를 함께 운영해야 의미가 있습니다.

또한 정책 예외 처리도 명시해야 합니다. 고위험 유지보수 윈도우에서 일시적으로 상한을 완화할 필요가 있다면, 예외 정책의 시작·종료 시각과 승인자를 함께 기록해야 합니다. 예외가 로그에 남지 않으면 사고 후 원인 분석에서 "정책 위반인지 승인된 예외인지"를 구분할 수 없습니다.

마지막으로 제약 테스트는 실패 케이스 중심으로 유지해야 합니다. 정상 요청만 통과하는 테스트보다, 금지 도구 호출·범위 외 SQL·PII 포함 출력이 실제로 차단되는지를 확인하는 negative test가 운영 안전성을 더 직접적으로 보장합니다.

### 흔한 실수

"DB를 수정하지 마세요"라고 프롬프트에 적는 것으로는 충분하지 않습니다. LLM은 지시를 무시할 수 있습니다. 도구를 노출하지 않거나, 데이터 레이어에서 막아야 합니다.

"이 도구들은 금지" 목록은 새 도구가 추가될 때마다 깨집니다. 화이트리스트만 사용합니다.

token, tool call, wall clock의 상한이 없으면 잘못된 task가 무한 비용을 만듭니다. 모든 task에 상한을 둡니다.

"출력은 사람이 검토할 거니까"라는 가정으로 자동 검증을 생략하면, 검토를 누락한 출력이 production으로 흘러갑니다. 자동 검증은 필수입니다.

Agent가 만든 SQL을 application에서 검사하는 것은 우회 가능합니다. DB의 row-level security나 view를 사용합니다.
## 흔히 헷갈리는 지점
- 시스템 프롬프트에 금지 문장을 적어 두면 제약이 구현된 것처럼 느끼기 쉽지만, 프롬프트는 강제 장치가 아닙니다.
- blacklist만 잘 유지하면 충분하다고 생각하기 쉽지만, 새 도구가 생길 때마다 구멍이 생깁니다.
- 토큰과 시간 상한은 대규모 시스템에서만 필요하다고 보기 쉽지만, 작은 시스템일수록 한 번의 루프가 더 치명적입니다.
- 출력 검토는 나중에 사람이 보면 된다고 미루기 쉽지만, 수동 검토는 자주 생략되고 누락됩니다.
- 애플리케이션에서 SQL 문자열만 검사해도 scope가 지켜진다고 생각하기 쉽지만, 가장 강한 제약은 데이터 계층에 두어야 합니다.
## 운영 체크리스트
- [ ] 모든 태스크에 capability, resource, behavioral, scope 제약이 각각 어떻게 구현되는지 명시합니다.
- [ ] 도구 노출은 blacklist가 아니라 whitelist로 관리합니다.
- [ ] 토큰, 도구 호출, wall clock 상한을 기본 제약으로 넣습니다.
- [ ] 출력 정책 위반은 자동 검증하고, 위반 이유를 피드백 신호로 남깁니다.
- [ ] 데이터 접근 범위는 가능하면 row-level security나 view 기반으로 제한합니다.
## 정리
Constraint Harness는 에이전트에게 덜 자유를 주기 위한 장치가 아니라, 시스템이 감당 가능한 자유만 남기는 장치입니다.
실무에서 제약은 문장보다 메커니즘이어야 합니다. 보이지 않는 도구, 초과하면 멈추는 자원 계측기, 위반 시 재생성을 강제하는 출력 검증기, 범위를 벗어나면 데이터를 아예 내주지 않는 데이터 계층이 있어야 합니다.
다음 글에서는 Tool Harness를 다룹니다. 제약이 행동 범위를 정한다면, 도구 설계는 그 범위 안에서 어떤 인터페이스를 제공할지 결정합니다.

## 처음 질문으로 돌아가기

- **Constraint Harness는 prompt 규칙과 무엇이 달라야 실제로 agent 행동을 제한할까요?**
  - prompt 규칙은 모델이 따르기를 기대하는 문장이지만 Constraint Harness는 tool whitelist, 권한, budget, policy check처럼 코드가 강제하는 경계여야 합니다.
- **capability, resource, behavior, scope 제약은 각각 어떤 위험을 막을까요?**
  - capability는 쓸 수 있는 도구, resource는 비용과 시간, behavior는 출력과 행동 정책, scope는 데이터와 권한 범위를 제한합니다.
- **제약이 실행 계약이 되려면 코드와 로그에 무엇이 남아야 할까요?**
  - 허용·차단 판단, 사용한 제약 이름, 실패 이유, 우회 시도 여부가 코드 경로와 로그에 남아야 실행 계약으로 검증됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- **Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기 (현재 글)**
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
- [OWASP — Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [PostgreSQL — Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Open Policy Agent — Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/)
### 관련 시리즈

- [LangGraph 101 — 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Safety & Guardrails 101 — 운영 가드레일 시스템 구축](../../ai-safety-guardrails-101/ko/10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/harness-engineering-101/ko/04-constraint-harness)

Tags: AI Agent, Harness, Production, Reliability
