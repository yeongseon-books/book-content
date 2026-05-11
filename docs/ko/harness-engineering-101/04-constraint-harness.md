---
title: Constraint Harness — 규칙, 경계, 금지 행동 정의하기
series: harness-engineering-101
episode: 4
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Security
- Policy
last_reviewed: '2026-05-03'
seo_description: Agent에게 자유를 주면 창의적이지만 위험합니다. Constraint Harness는 어떤 행동이 허용되고 어떤 행동이
  금지되는지 명시하는…
---

# Constraint Harness — 규칙, 경계, 금지 행동 정의하기

> Harness Engineering 101 시리즈 (4/10)

Agent에게 자유를 주면 창의적이지만 위험합니다. Constraint Harness는 어떤 행동이 허용되고 어떤 행동이 금지되는지 명시하는 규칙 체계입니다.

---

![Constraint Harness - 규칙, 경계, 금지 행동 정의하기](../../assets/harness-engineering-101/04/04-01-constraint-harness-defining-rules-bounda.ko.png)

*Constraint Harness - 규칙, 경계, 금지 행동 정의하기*

## Agent는 허용된 모든 것을 시도합니다

Agent에게 도구와 권한을 주면 그것을 모두 시도합니다. "고객 데이터를 분석해 줘"라는 task에 데이터베이스 쓰기 권한이 있다면, 분석 도중에 데이터를 수정할 수도 있습니다. "이메일 초안을 작성해 줘"라고 했는데 발송 도구가 노출되어 있다면, 초안을 그대로 보낼 수도 있습니다.

LLM은 명시적으로 금지되지 않은 행동을 안전하다고 가정합니다. 인간은 사회적 규범과 상식으로 경계를 만듭니다. Agent에게는 그런 것이 없습니다. 명시적인 제약이 곧 안전입니다.

Constraint Harness는 Agent가 무엇을 해도 되고 무엇을 하면 안 되는지를 코드로 표현된 규칙으로 정의합니다. 이번 글에서는 제약의 종류, 정책 엔진 설계, 그리고 제약 위반을 감지하는 방법을 다룹니다.

---

## 제약의 4가지 종류

![제약의 4가지 종류](../../assets/harness-engineering-101/04/04-02-four-kinds-of-constraints.ko.png)

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
    """단일 제약 정의."""
    name: str
    type: ConstraintType
    rule: str  # 사람이 읽을 수 있는 규칙
    enforcer: str  # 강제 메커니즘 식별자

@dataclass
class ConstraintPolicy:
    """task에 적용되는 제약 묶음."""
    task_id: str
    constraints: list[Constraint] = field(default_factory=list)

    def by_type(self, t: ConstraintType) -> list[Constraint]:
        return [c for c in self.constraints if c.type == t]

policy = ConstraintPolicy(
    task_id="generate-report",
    constraints=[
        Constraint("read-only", ConstraintType.CAPABILITY, "DB 읽기만 허용", "tool-filter"),
        Constraint("max-cost", ConstraintType.RESOURCE, "최대 0.5 USD", "cost-meter"),
        Constraint("no-pii", ConstraintType.BEHAVIORAL, "출력에 PII 금지", "output-validator"),
        Constraint("apac-only", ConstraintType.SCOPE, "APAC 지역 데이터만", "row-filter"),
    ],
)
```

이 4분류 없이 "Agent가 안전하게 동작하도록"이라는 추상적인 요구만 있으면 강제가 불가능합니다.

---

## Capability Constraints — 도구 화이트리스트

![Capability Constraints - 도구 화이트리스트](../../assets/harness-engineering-101/04/04-03-capability-constraints-tool-whitelisting.ko.png)

*Capability Constraints - 도구 화이트리스트*
가장 단순하고 효과적인 제약은 도구 노출을 제한하는 것입니다. Agent는 받지 않은 도구를 호출할 수 없습니다.

핵심 원칙은 화이트리스트입니다. "이 도구는 금지"가 아니라 "이 도구만 허용". 블랙리스트는 새 도구가 추가될 때마다 업데이트해야 하지만, 화이트리스트는 명시적으로 추가하지 않으면 자동으로 차단됩니다.

```python
from typing import Callable

@dataclass
class Tool:
    name: str
    description: str
    handler: Callable
    danger_level: int  # 0 (안전) ~ 5 (파괴적)

class ToolRegistry:
    """모든 도구를 등록하고 task별로 필터링합니다."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def expose(self, allowed_names: set[str], max_danger: int = 2) -> list[Tool]:
        """task에 허용된 도구만, 위험도 임계값 안에서 노출합니다."""
        return [
            t for name, t in self._tools.items()
            if name in allowed_names and t.danger_level <= max_danger
        ]

registry = ToolRegistry()
registry.register(Tool("read_db", "DB 조회", lambda q: ..., danger_level=0))
registry.register(Tool("write_db", "DB 수정", lambda r: ..., danger_level=4))
registry.register(Tool("send_email", "이메일 발송", lambda m: ..., danger_level=3))

# task: 분석 보고서 생성 — 읽기만 허용
exposed = registry.expose(allowed_names={"read_db"}, max_danger=2)
assert all(t.name == "read_db" for t in exposed)
```

danger_level은 두 번째 보호막입니다. 실수로 위험한 도구를 화이트리스트에 넣어도, danger 임계값이 막아 줍니다.

---

## Resource Constraints — 비용과 시간의 상한

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
    """task의 자원 사용량을 추적하고 상한을 강제합니다."""
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

---

## Behavioral Constraints — 출력 정책

Agent가 만드는 출력에도 규칙이 있어야 합니다. PII를 포함하면 안 되고, 특정 형식을 따라야 하고, 금지된 톤을 쓰면 안 됩니다.

이 제약은 두 단계로 강제합니다.

**1. Pre-output validation**: 출력 직전에 schema와 정책을 검사합니다. 위반하면 재생성을 요청합니다.

**2. Post-output filtering**: 사용자에게 보내기 전에 마지막 필터를 적용합니다. PII 마스킹, 금칙어 치환.

```python
import re
from typing import Protocol

class OutputPolicy(Protocol):
    def check(self, output: str) -> tuple[bool, str]:
        """(pass, reason) 반환."""
        ...

class NoSecrets:
    """출력에 비밀 정보가 없는지 검사합니다."""
    def check(self, output: str) -> tuple[bool, str]:
        if re.search(r"sk-[a-zA-Z0-9]{20,}", output):
            return False, "API key detected"
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", output):
            return False, "SSN detected"
        return True, ""

class ApprovedTone:
    """승인된 톤만 사용합니다."""
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

---

## Scope Constraints — 데이터 레이어 권한

![Scope Constraints - 데이터 레이어 권한](../../assets/harness-engineering-101/04/04-04-scope-constraints-permissions-at-the-dat.ko.png)

*Scope Constraints - 데이터 레이어 권한*
가장 강력한 제약은 데이터 레이어에서 만듭니다. Agent가 아무리 잘못된 쿼리를 보내도, DB가 권한 밖 데이터를 반환하지 않으면 안전합니다.

이 패턴은 row-level security 또는 view-based access로 구현합니다. Agent에게 직접 테이블 접근을 주지 않고, task에 맞춘 view나 filtered query만 노출합니다.

```python
@dataclass
class ScopedDataAccess:
    """task의 scope에 맞춰 데이터 접근을 제한합니다."""
    user_id: str
    region: str
    allowed_tables: set[str]

    def query(self, sql: str) -> list[dict]:
        """SQL을 검사하고 scope를 강제합니다."""
        self._validate_tables(sql)
        scoped_sql = self._inject_filters(sql)
        return self._execute(scoped_sql)

    def _validate_tables(self, sql: str) -> None:
        # 매우 단순한 검증 — 실제로는 SQL parser 사용
        for word in sql.lower().split():
            if word.startswith("from") or word.startswith("join"):
                continue
            for table in ["users", "orders", "payments"]:
                if table in sql.lower() and table not in self.allowed_tables:
                    raise ScopeViolation(f"table not allowed: {table}")

    def _inject_filters(self, sql: str) -> str:
        # WHERE 절에 region 필터를 주입합니다
        if "where" in sql.lower():
            return sql + f" AND region = '{self.region}'"
        return sql + f" WHERE region = '{self.region}'"

    def _execute(self, sql: str) -> list[dict]:
        # 실제 DB 실행
        return []

class ScopeViolation(Exception):
    pass
```

데이터 레이어 제약은 Agent의 잘못된 동작이 어떻게 발생하든 영향 범위를 막아줍니다. application 레이어 제약보다 우회가 어렵고, audit log도 더 신뢰할 수 있습니다.

---

## Common Mistakes

**1. 시스템 프롬프트로만 제약합니다.**
"DB를 수정하지 마세요"라고 프롬프트에 적는 것으로는 충분하지 않습니다. LLM은 지시를 무시할 수 있습니다. 도구를 노출하지 않거나, 데이터 레이어에서 막아야 합니다.

**2. 블랙리스트로 도구를 관리합니다.**
"이 도구들은 금지" 목록은 새 도구가 추가될 때마다 깨집니다. 화이트리스트만 사용합니다.

**3. Resource limit을 정하지 않습니다.**
token, tool call, wall clock의 상한이 없으면 잘못된 task가 무한 비용을 만듭니다. 모든 task에 상한을 둡니다.

**4. 출력 검증을 사람에게 맡깁니다.**
"출력은 사람이 검토할 거니까"라는 가정으로 자동 검증을 생략하면, 검토를 누락한 출력이 production으로 흘러갑니다. 자동 검증은 필수입니다.

**5. Application 레이어에서만 권한을 검사합니다.**
Agent가 만든 SQL을 application에서 검사하는 것은 우회 가능합니다. DB의 row-level security나 view를 사용합니다.

---

## 핵심 요약

- LLM은 명시적으로 금지되지 않은 행동을 안전하다고 가정합니다. 제약은 코드로 표현된 규칙이어야 합니다.
- 제약은 Capability, Resource, Behavioral, Scope의 4가지로 분류되며 각각 다른 메커니즘으로 강제합니다.
- Capability constraint는 화이트리스트로 도구를 노출하고 danger level로 이중 보호합니다.
- Resource constraint는 token, tool call, wall clock의 상한으로 비용 사고를 막습니다.
- Scope constraint는 데이터 레이어에서 강제할 때 가장 강력합니다. application 레이어 검증은 우회 가능합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- **Constraint Harness — 규칙, 경계, 금지 행동 정의하기 (현재 글)**
- Tool Harness — Agent가 사용할 도구를 안전하게 설계하기 (예정)
- Test Harness — 완료 조건을 테스트로 고정하기 (예정)
- Feedback Loop — 실패를 고치게 만드는 반복 구조 (예정)
- Approval Gate — 사람 승인이 필요한 지점 설계하기 (예정)
- Observability — Agent 작업을 추적하고 재현하기 (예정)
- Production Harness — 운영 가능한 Agent 작업 환경 만들기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OWASP — Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [PostgreSQL — Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Open Policy Agent — Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/)
