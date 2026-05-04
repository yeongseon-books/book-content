---
title: Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions
series: harness-engineering-101
episode: 4
language: en
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
---

# Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions

> Harness Engineering 101 Series (4/10)

Give an agent freedom and you get creativity along with risk. The Constraint Harness is the rule system that declares what actions are allowed and what actions are forbidden.

---
## Agents Try Everything They Are Allowed To

Give an agent tools and permissions, and it will try them all. If a "analyze customer data" task has database write access, the agent may modify data while analyzing. If "draft an email" has the send tool exposed, it may send the draft as is.

LLMs assume any action not explicitly forbidden is safe. Humans build boundaries from social norms and common sense. Agents have neither. Explicit constraints are the safety.

Constraint Harness defines, in code-expressed rules, what an agent may and may not do. This article covers the kinds of constraints, policy engine design, and how to detect violations.

---

## Four Kinds of Constraints

Constraints on an agent fall into four categories.

**1. Capability constraints**: which tools may be used. Defined as a whitelist.

**2. Resource constraints**: how much may be used. Caps on tokens, API calls, time, cost.

**3. Behavioral constraints**: how the agent must behave. Forbidden output patterns, required formats, priorities.

**4. Scope constraints**: how far the impact may reach. The set of accessible data and modifiable resources.

Each kind is enforced by a different mechanism. Capability at the tool exposure layer, Resource via runtime metering, Behavioral via output validation, Scope via data-layer permissions.

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

Without this four-way classification, vague demands like "the agent should behave safely" cannot be enforced.

---

## Capability Constraints — Tool Whitelisting

The simplest and most effective constraint is restricting tool exposure. An agent cannot call a tool it never received.

The core principle is whitelisting. Not "this tool is forbidden" but "only this tool is allowed." A blacklist must be updated each time a new tool is added; a whitelist blocks anything not explicitly added.

```python
from typing import Callable
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

# Task: produce an analytical report — read only
exposed = registry.expose(allowed_names={"read_db"}, max_danger=2)
assert all(t.name == "read_db" for t in exposed)
```

The danger_level acts as a second guard. If a dangerous tool ever slips into the whitelist by mistake, the threshold blocks it.

---

## Resource Constraints — Caps on Cost and Time

Agents can fall into infinite loops. They might repeat a wrong tool call 100 times or run 30 more searches. Resource constraints stop these accidents at the cost layer.

Three measurements.

**1. Token budget**: cap on cumulative input + output tokens.
**2. Tool call budget**: maximum tool calls per task.
**3. Wall clock budget**: cap on total execution time.

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

Agents without caps cause cost incidents in production. Real reports describe single misbehaving tasks burning thousands of dollars. The ResourceMeter is insurance.

---

## Behavioral Constraints — Output Policy

The agent's outputs need rules too. No PII allowed, must follow a specific format, must not use a forbidden tone.

Enforce in two stages.

**1. Pre-output validation**: check schema and policy just before output. On violation, request regeneration.

**2. Post-output filtering**: apply a final filter before sending to the user. PII masking, banned-word substitution.

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

When a violation is detected, request the agent to regenerate. Not a flat block — feedback ("rejected for this reason, retry") is the key idea, covered in the next article on Feedback Loop.

---

## Scope Constraints — Permissions at the Data Layer

The strongest constraints come from the data layer. No matter how badly the agent's query is formed, if the database refuses to return out-of-scope rows, you are safe.

Implement this with row-level security or view-based access. Do not give the agent direct table access — expose task-scoped views or filtered queries.

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
        # Naive check — use a real SQL parser in production
        for table in ["users", "orders", "payments"]:
            if table in sql.lower() and table not in self.allowed_tables:
                raise ScopeViolation(f"table not allowed: {table}")

    def _inject_filters(self, sql: str) -> str:
        # Inject region filter into WHERE clause
        if "where" in sql.lower():
            return sql + f" AND region = '{self.region}'"
        return sql + f" WHERE region = '{self.region}'"

    def _execute(self, sql: str) -> list[dict]:
        return []

class ScopeViolation(Exception):
    pass
```

Data-layer constraints contain the blast radius of any agent misbehavior. They are harder to bypass than application-layer checks, and their audit logs are more trustworthy.

---

## Common Mistakes

**1. Constraining only via the system prompt.**
Writing "do not modify the DB" in the prompt is not enough. LLMs may ignore instructions. Either do not expose the tool, or block it at the data layer.

**2. Managing tools by blacklist.**
A "forbidden tools" list breaks every time a new tool is added. Use a whitelist only.

**3. Not setting resource limits.**
Without caps on tokens, tool calls, and wall clock, a misbehaving task generates unbounded cost. Apply caps to every task.

**4. Delegating output validation to humans.**
"A human will review the output" leads to skipped reviews leaking through to production. Automated validation is mandatory.

**5. Checking permissions only at the application layer.**
Validating the agent's SQL inside the application is bypassable. Use database row-level security or views.

---

## Key Takeaways

- LLMs assume any unforbidden action is safe. Constraints must be code-expressed rules.
- Constraints split into Capability, Resource, Behavioral, and Scope, each enforced by a different mechanism.
- Capability constraints expose tools by whitelist and double-protect with a danger level.
- Resource constraints cap tokens, tool calls, and wall clock to prevent cost incidents.
- Scope constraints are strongest when enforced at the data layer; application-layer validation is bypassable.

<!-- toc:begin -->
## In this series

- [What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Context Harness — Designing What the Agent Should Know and Not Know](./03-context-harness.md)
- **Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions (current)**
- Tool Harness — Designing Safe Tools for Agents (upcoming)
- Test Harness — Turning Completion Criteria into Tests (upcoming)
- Feedback Loops — Building Structures That Let Agents Recover from Failure (upcoming)
- Approval Gates — Designing Where Humans Must Approve (upcoming)
- Observability — Tracing and Replaying Agent Work (upcoming)
- Production Harness — Building Operational Environments for Agents (upcoming)

<!-- toc:end -->

---

## References

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OWASP — Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [PostgreSQL — Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Open Policy Agent — Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/)

Tags: AI Agent, Harness, Production, Reliability
