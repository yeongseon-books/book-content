---
title: Tool Harness — Designing Safe Tools for Agents
series: harness-engineering-101
episode: 5
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Tool Design
- Sandboxing
last_reviewed: '2026-05-03'
---

# Tool Harness — Designing Safe Tools for Agents

> Harness Engineering 101 Series (5/10)

Tools are the hands and feet of an agent. Poorly designed tools can corrupt data or blow up costs. The Tool Harness is about designing tools that are safe, predictable, and easy for the agent to use correctly.

---
## Tools Are an Agent's Hands and Feet

Tools determine what an agent can do. Without tools, an agent is just a text-generating model. DB queries, file writes, API calls, code execution — all are tools. The agent's range of action is exactly the range of its tools.

The problem is that poorly designed tools destabilize every action the agent takes. An ambiguous tool schema produces wrong arguments. An overly powerful tool can wreck a system in one call. Unhelpful error messages cause the agent to repeat the same mistake.

Tool Harness is the principle of designing tools that are safe and predictable for agents. This article covers five tool design principles, safe schema design, and how to make tool errors something the agent can act on.

---

## Five Principles of a Good Tool

Five rules to follow when designing a tool.

**1. Single responsibility**: one tool does one thing. Not `manage_user`, but `create_user`, `delete_user`, `update_user_email`.

**2. Idempotent when possible**: calling with the same input multiple times produces the same result. Agents retry frequently. Non-idempotent tools cause incidents.

**3. Explicit side effects**: if there is a side effect, name and describe it. Don't hide that `send_email` actually sends.

**4. Structured output**: return results as a schema, not free text. Easier for the agent to parse and validate.

**5. Actionable errors**: when failing, return errors the agent can act on. Not "error" but "which error, why, how to fix it."

```python
from pydantic import BaseModel, Field
from typing import Literal


# Bad — too many responsibilities
def manage_user(action: str, user_id: str, **kwargs):
    """Manage a user."""
    ...


# Good — single responsibility, explicit schema
class CreateUserInput(BaseModel):
    email: str = Field(..., description="A valid email address")
    name: str = Field(..., min_length=1, max_length=100)
    role: Literal["admin", "user", "guest"]


class CreateUserOutput(BaseModel):
    user_id: str
    created_at: str
    status: Literal["created", "already_exists"]


def create_user(input: CreateUserInput) -> CreateUserOutput:
    """Create a new user. Returns already_exists if the email already exists."""
    ...
```

If even one of the five principles is missing, the agent's behavior becomes unpredictable.

---

## Precision in Schema Design

A tool's input schema is the user manual for the agent. Ambiguous schemas produce ambiguous calls.

Three things must be explicit.

**1. Meaning of each field**: write a `description`. Instead of "user id", write "the user's UUID, retrievable via get_user."

**2. Constraints**: express length, range, allowed values in the schema. Do not defer validation to the application layer.

**3. Dependencies**: conditions like "this field is required only when type is X" go in the schema, not in a separate document.

```python
from pydantic import BaseModel, Field, model_validator
from typing import Literal


class SendNotificationInput(BaseModel):
    """Send a notification."""
    channel: Literal["email", "sms", "push"] = Field(
        ...,
        description="Send channel. email needs an email address; sms needs a phone number.",
    )
    recipient: str = Field(..., description="Recipient identifier (varies by channel)")
    template_id: str = Field(..., pattern=r"^TPL-\d{4}$", description="Format: TPL-0001")
    variables: dict[str, str] = Field(
        default_factory=dict,
        description="Template variables. Example: {'name': 'Alice', 'order_id': '12345'}",
    )

    @model_validator(mode="after")
    def validate_recipient_format(self):
        if self.channel == "email" and "@" not in self.recipient:
            raise ValueError(f"channel=email requires email address, got: {self.recipient}")
        if self.channel == "sms" and not self.recipient.startswith("+"):
            raise ValueError(f"channel=sms requires E.164 phone (+countrycode), got: {self.recipient}")
        return self
```

Schemas like this have two effects. First, the agent is less likely to construct invalid arguments before calling. Second, invalid calls are rejected immediately, preventing side effects.

---

## The Idempotency Key Pattern

Agents retry often — network errors, timeouts, "couldn't confirm" cases all lead to repeating the same tool call. Non-idempotent tools then run twice and cause incidents.

The fix is the idempotency key. The agent sends a unique key per call, and the server refuses to execute the same key twice.

```python
import hashlib
from dataclasses import dataclass


@dataclass
class IdempotencyStore:
    """Stores results per idempotency key."""
    _cache: dict[str, dict] = None

    def __post_init__(self):
        self._cache = self._cache or {}

    def get_or_run(self, key: str, fn, *args, **kwargs) -> dict:
        if key in self._cache:
            return self._cache[key]
        result = fn(*args, **kwargs)
        self._cache[key] = result
        return result


def create_charge(amount: int, currency: str, idempotency_key: str, store: IdempotencyStore) -> dict:
    """Create a charge. Same idempotency_key runs only once."""
    def _do_charge():
        return {
            "charge_id": "ch_" + hashlib.sha256(idempotency_key.encode()).hexdigest()[:12],
            "amount": amount,
        }
    return store.get_or_run(idempotency_key, _do_charge)


# The agent uses a key unique per task
store = IdempotencyStore()
key = "task-abc123-charge-001"
r1 = create_charge(1000, "USD", key, store)
r2 = create_charge(1000, "USD", key, store)
assert r1 == r2  # Same result, executed once
```

The idempotency key applies not only at the tool call level but at the task level too. The same task running twice should produce the same result.

---

## Designing Actionable Errors

When a tool call fails, the agent must decide what to do next. If the error is "Internal Server Error," the agent retries the same call. If the message is clear, the agent fixes the arguments and tries again.

A good error includes three parts.

**1. What**: what failed, specifically.
**2. Why**: why it failed, the cause.
**3. How**: how to fix it, the next action for the agent.

```python
from enum import Enum
from dataclasses import dataclass


class ErrorCode(Enum):
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMITED = "rate_limited"
    UPSTREAM_TIMEOUT = "upstream_timeout"


@dataclass
class ToolError(Exception):
    code: ErrorCode
    what: str
    why: str
    how: str
    retryable: bool

    def to_agent_message(self) -> str:
        return f"""Tool call failed.
Code: {self.code.value}
What: {self.what}
Why: {self.why}
How to fix: {self.how}
Retryable: {self.retryable}"""


def get_user(user_id: str) -> dict:
    if not user_id.startswith("usr_"):
        raise ToolError(
            code=ErrorCode.INVALID_INPUT,
            what="user_id format is invalid",
            why=f"user_id must start with 'usr_', got: {user_id}",
            how="Call list_users to find a valid user_id, or check the format.",
            retryable=False,
        )
    raise ToolError(
        code=ErrorCode.NOT_FOUND,
        what=f"user not found: {user_id}",
        why="No user with this id exists in the database.",
        how="Verify the id with list_users, or create_user if intended.",
        retryable=False,
    )
```

The `retryable` flag matters. On `retryable=False`, the agent immediately tries a different approach. On `retryable=True`, it retries after backoff.

---

## Sandboxing Dangerous Tools

Code execution, filesystem access, and arbitrary shell commands are extremely powerful and extremely dangerous. These tools must not be exposed without sandboxing.

Three isolation techniques.

**1. Process isolation**: run in a separate process with resource limits.
**2. Filesystem isolation**: only operate inside an isolated temp directory.
**3. Network isolation**: block external network access or whitelist it.

```python
import subprocess
import tempfile
from pathlib import Path


def execute_python_safely(code: str, timeout: float = 5.0) -> dict:
    """Execute Python code in an isolated environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "script.py"
        script_path.write_text(code)
        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,  # Isolated working directory
                env={"PATH": "/usr/bin:/bin"},  # Minimal env
            )
            return {
                "stdout": result.stdout[:10_000],  # Cap output size
                "stderr": result.stderr[:10_000],
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            raise ToolError(
                code=ErrorCode.UPSTREAM_TIMEOUT,
                what="code execution exceeded timeout",
                why=f"Execution did not complete in {timeout}s.",
                how="Reduce the work done in code, or split into multiple calls.",
                retryable=False,
            )
```

Stronger isolation uses containers (gVisor, Firecracker) or WebAssembly runtimes. If a production agent exposes arbitrary code execution, container-grade isolation is the minimum.

---

## Common Mistakes

**1. Tool names hide their behavior.**
If `process_order` also charges payment, the name should reveal that. `charge_and_fulfill_order` is honest.

**2. Stuffing too many options into one tool.**
Dispatcher tools like `manage_user(action="create"|"delete"|"update", ...)` weaken the schema and let the agent build invalid combinations. Split them.

**3. Ignoring idempotency.**
In environments where retries are common, non-idempotent tools cause duplicate charges, duplicate emails, duplicate notifications.

**4. Error messages too short.**
"Bad request" gives the agent zero information. Always include What/Why/How.

**5. Exposing dangerous tools raw.**
Shell execution, file writes, and unbounded HTTP calls cause production incidents without sandboxing.

---

## Key Takeaways

- Good tools follow five principles: single responsibility, idempotency, explicit side effects, structured output, actionable errors.
- Schemas must express not just types but meaning, constraints, and dependencies for the agent to call them correctly.
- The idempotency key pattern prevents duplicate execution on retry.
- Errors must include What/Why/How, with a retryable flag to guide the agent's next action.
- Dangerous tools like code execution and file/network access require process, filesystem, and network isolation together.

---

<!-- toc:begin -->
## Harness Engineering 101 Series

- [What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Context Harness — Designing What to Show and Hide from the Agent](./03-context-harness.md)
- [Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions](./04-constraint-harness.md)
- **Tool Harness — Designing Safe Tools for Agents (current)**
- Test Harness — Pinning Completion Criteria with Tests (upcoming)
- Feedback Loop — A Repeating Structure That Forces Failures to Be Fixed (upcoming)
- Approval Gate — Designing Where Human Approval Is Required (upcoming)
- Observability — Tracing and Reproducing Agent Work (upcoming)
- Production Harness — Building an Operable Agent Work Environment (upcoming)
<!-- toc:end -->

## References

- [Anthropic — Tool Use Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [OpenAI — Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Stripe — Idempotent Requests](https://docs.stripe.com/api/idempotent_requests)
- [gVisor — Sandboxed Container Runtime](https://gvisor.dev/docs/)

Tags: AI Agent, Harness, Tool Design, Sandboxing
