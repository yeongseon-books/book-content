---
episode: 2
language: en
last_reviewed: '2026-05-15'
series: llm-api-production-101
status: publish-ready
tags:
- LLM
- OpenAI
- Streaming
- Python
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: false
title: "LLM API Production 101 (2/6): Tool calling — connecting functions to the model"
seo_description: Implement a secure tool-calling loop that connects LLMs to application functions while maintaining control over execution and permissions.
---

# LLM API Production 101 (2/6): Tool calling — connecting functions to the model

Once structured output is working, the next request usually arrives quickly: the model should not stop at answering the user, it should connect to application functions. A customer asks about an order, and you want the model to trigger `get_order_status()`. Someone asks about exchange rates, and you want the model to call an internal lookup. A scheduling request should lead to a calendar action instead of a paragraph about calendars.

This is the second post in the LLM API Production 101 series.

At that point, many first implementations still rely on string conventions. The model is asked to emit a function name and some arguments in text, and the application maps that result with custom parsing or a pile of `if` statements. It works for a toy example, but it creates a loose execution boundary. Typos in function names, missing parameters, extra keys, and unsafe dispatch logic start accumulating quickly.

Tool calling matters not because the model executes code — it does not. It matters because the application publishes allowed function names, descriptions, and argument schemas explicitly, and the model selects from within that boundary. Execution authority, validation, and side-effect control remain with the application.

In this post, we will build the full loop with Groq's `tools` parameter and the `tool_calls` response field: model selection, argument validation, function execution, and result reinjection.

Here we focus on connecting model responses to application functions through a controlled tool-calling loop.

![Tool calling: connecting functions to the model](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-01-tool-calling-connecting-functions-to-the.en.png)
*Tool calling: connecting functions to the model*
> Tool calling is not model autonomy; it is an application-owned execution boundary.

## Questions to Keep in Mind

- Is tool calling model autonomy, or an execution boundary designed by the application?
- What should you validate in the `tools` definition and the returned `tool_calls`?
- What guardrails close the function-execution loop safely in production?

## Why this post matters

Tool calling is the first execution boundary where an LLM application meets the outside world. If structured output was about "how do we safely receive data," tool calling is about "what do we let the system execute based on that data." Making this boundary loose may let the model appear smart, but the system quickly becomes dangerous.

In practice, problems grow the moment read-only tools and state-changing tools are treated at the same trust level. Looking up an order status and cancelling an order look like the same tool-call mechanism, but their trust assumptions are entirely different. That is why tool calling should be seen not as a feature extension but as an execution interface with permissions and validation attached.

Tool calling is also a traceability concern. When a user asks "why did I get the wrong answer?", you need a timeline showing which tool was called with what arguments and what result came back. Without that explainability, operational quality degrades quickly.

## Why string-based dispatch does not scale

![Comparison between string dispatch and tool contracts](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-01-why-string-based-dispatch-does-not-scale.en.png)

*Comparison between string dispatch and tool contracts*

String-based routing is the easiest first pattern to try. But the contract ends up hidden between code and prompts.

```python
if "shipping" in user_question:
    result = get_order_status(order_id)
elif "refund" in user_question:
    result = get_refund_policy()
```

Or the model is told to emit text such as `{"function": "get_order_status", "order_id": "ORD-1001"}` and the application parses it manually. Neither approach is impossible, but because the function set, argument requirements, and response structure are not explicitly surfaced, the operational boundary stays weak.

## What goes into the `tools` parameter

![Structure of a tool definition](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-02-what-goes-into-the-tools-parameter.en.png)

*Structure of a tool definition*

A tool definition is a function descriptor containing a name, description, and argument schema. The name is part of the allowlist, the description is the model's selection criterion, and the parameters are the call contract.

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "An order identifier such as ORD-1001",
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]
```

Constraints like `additionalProperties=False` look minor but matter. They reduce invented keys and prevent arguments the application cannot understand from reaching the execution path.

## Sending the first tool-enabled request

![First tool-enabled request flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-03-sending-the-first-tool-enabled-request.en.png)

*First tool-enabled request flow*

Now we let the model actually choose a tool.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "Use tools when order questions require a live lookup.",
        },
        {
            "role": "user",
            "content": "Please check the shipping status for order ORD-1001.",
        },
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0,
)

message = completion.choices[0].message
print(message.tool_calls)
```

`tool_choice="auto"` lets the model decide whether a tool is needed. At this point the response is not a final user answer — it is an execution request. The application still has one more step to complete.

## Parsing `tool_calls` and routing them safely

Before execution, two checks are needed: is the function name in the allowlist, and do the arguments match the expected shape?

```python
import json
import os

from groq import Groq
from pydantic import BaseModel

class OrderStatusArgs(BaseModel):
    order_id: str

def get_order_status(order_id: str) -> dict:
    fake_db = {
        "ORD-1001": {"status": "in_transit", "eta_days": 2},
        "ORD-1002": {"status": "delivered", "eta_days": 0},
    }
    return fake_db.get(order_id, {"status": "not_found", "eta_days": None})

available_tools = {
    "get_order_status": get_order_status,
}

client = Groq(api_key=os.environ["GROQ_API_KEY"])

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "Use tools for order lookup requests."},
        {"role": "user", "content": "Check ORD-1001 for me."},
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0,
)

message = completion.choices[0].message

for tool_call in message.tool_calls or []:
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name not in available_tools:
        raise ValueError(f"unknown tool: {function_name}")

    validated_args = OrderStatusArgs.model_validate(arguments)
    result = available_tools[function_name](**validated_args.model_dump())
    print(function_name, arguments, result)
```

This stage is not the final answer yet. The model requested a tool, the application executed that request. Now the result must be fed back into the conversation to complete the user response.

## Building the full function-execution loop

![Round-trip tool execution loop](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-04-building-the-full-function-execution-loo.en.png)

*Round-trip tool execution loop*

The full loop follows the structure: "model chooses, application executes, model explains."

```python
import json
import os

from groq import Groq
from pydantic import BaseModel

class OrderStatusArgs(BaseModel):
    order_id: str

def get_order_status(order_id: str) -> dict:
    fake_db = {
        "ORD-1001": {
            "status": "in_transit",
            "location": "Seoul hub",
            "eta_days": 2,
        }
    }
    return fake_db.get(order_id, {"status": "not_found"})

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]

available_tools = {"get_order_status": get_order_status}

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {"role": "system", "content": "Use tools for order lookups, then answer briefly."},
    {"role": "user", "content": "What is happening with order ORD-1001?"},
]

first = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=0,
)

assistant_message = first.choices[0].message
messages.append(assistant_message.model_dump())

if not assistant_message.tool_calls:
    print(assistant_message.content)
    raise SystemExit(0)

for tool_call in assistant_message.tool_calls or []:
    function_name = tool_call.function.name
    if function_name not in available_tools:
        raise ValueError(f"unknown tool: {function_name}")

    try:
        arguments = json.loads(tool_call.function.arguments)
        validated_args = OrderStatusArgs.model_validate(arguments)
    except json.JSONDecodeError as exc:
        raise ValueError("tool arguments were not valid JSON") from exc

    tool_result = available_tools[function_name](**validated_args.model_dump())

    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(tool_result, ensure_ascii=False),
        }
    )

final = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    tools=tools,
    temperature=0,
)

print(final.choices[0].message.content)
```

The advantage of this structure is role separation. The model proposes which tool is needed, the application handles actual execution and validation, and the final response is again composed by the model in natural language.

## Returning structured failures from tool calls

Making only the success path clean leaves production half-done. When a tool times out or hits a permission error, the application should return a standardized error payload that the model can interpret, rather than exposing raw exception strings.

```python
import json

from pydantic import BaseModel, ValidationError

class OrderStatusArgs(BaseModel):
    order_id: str

def run_tool(function_name: str, raw_arguments: str) -> dict:
    try:
        arguments = json.loads(raw_arguments)
        validated = OrderStatusArgs.model_validate(arguments)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error_type": "invalid_json",
            "message": str(exc),
        }
    except ValidationError as exc:
        return {
            "ok": False,
            "error_type": "invalid_arguments",
            "message": exc.errors()[0]["msg"],
        }

    if function_name != "get_order_status":
        return {
            "ok": False,
            "error_type": "unknown_tool",
            "message": f"unsupported tool: {function_name}",
        }

    return {
        "ok": True,
        "data": {
            "order_id": validated.order_id,
            "status": "in_transit",
            "eta_days": 2,
        },
    }

print(run_tool("get_order_status", '{"order_id": 1001}'))
print(run_tool("cancel_order", '{"order_id": "ORD-1001"}'))
```

This pattern is practical because failures come back as contracted data rather than natural-language exceptions. The model sees `ok: false` and `error_type` and can produce explanations like "the order ID format was invalid." The application uses the same fields for metrics and alerting. For state-changing tools especially, this standardization naturally extends to audit logs and re-execution prevention policies.

## Fixing the tool router as an explicit table

![Operational guardrails before tool execution](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-05-what-to-guard-in-production.en.png)

*Operational guardrails before tool execution*

When you have two or three functions, a simple dictionary suffices. But in production, permissions, timeouts, and audit fields differ per function, so a routing table with metadata is safer.

```python
import time
from dataclasses import dataclass
from typing import Callable

@dataclass
class ToolSpec:
    func: Callable
    timeout_seconds: float
    side_effect: bool

def get_order_status(order_id: str) -> dict:
    return {"order_id": order_id, "status": "in_transit"}

def cancel_order(order_id: str, reason: str) -> dict:
    return {"order_id": order_id, "cancelled": True, "reason": reason}

TOOL_REGISTRY: dict[str, ToolSpec] = {
    "get_order_status": ToolSpec(func=get_order_status, timeout_seconds=2.0, side_effect=False),
    "cancel_order": ToolSpec(func=cancel_order, timeout_seconds=5.0, side_effect=True),
}

def run_registered_tool(name: str, **kwargs) -> dict:
    spec = TOOL_REGISTRY.get(name)
    if spec is None:
        raise ValueError(f"unknown tool: {name}")

    started = time.monotonic()
    result = spec.func(**kwargs)
    elapsed = time.monotonic() - started

    return {
        "ok": True,
        "tool": name,
        "side_effect": spec.side_effect,
        "elapsed_ms": int(elapsed * 1000),
        "data": result,
    }
```

The benefits are clear. The callable tool set is defined in one place, dangerous tools are easy to classify separately, and log fields are standardized. When you later need approval workflows, user permissions, or maximum execution times, you extend the same table.

## Idempotency keys for state-changing tools

The most dangerous segment of tool calling is retries. A request that failed due to a network error may have already succeeded on the server side. Read-only tools can be safely re-called, but state-changing tools like cancel/create/charge can cause duplicate side effects without an idempotency key.

```python
from dataclasses import dataclass

@dataclass
class ToolExecutionContext:
    request_id: str
    idempotency_key: str

executed: dict[str, dict] = {}

def cancel_order_with_idempotency(order_id: str, reason: str, ctx: ToolExecutionContext) -> dict:
    if ctx.idempotency_key in executed:
        return executed[ctx.idempotency_key]

    result = {
        "order_id": order_id,
        "cancelled": True,
        "reason": reason,
        "request_id": ctx.request_id,
    }
    executed[ctx.idempotency_key] = result
    return result
```

In production, this key should be stored in Redis or a database rather than in-memory. The core principle is that "a retry must produce the same effect exactly once," guaranteed at both code and storage levels. Once you have completed the tool-calling loop, idempotency is always the next step.

## Common misconceptions

- The model returning `tool_calls` does not mean it executed code itself.
- Vague tool descriptions are usually a contract design issue, not a model quality issue.
- Going straight from `json.loads()` to `**arguments` skips the validation layer entirely.
- Read-only tools and state-changing tools should not share the same verification procedure.
- The final user-facing answer is often produced after the second model call, not the first.

## Operational checklist

- [ ] Wrote each tool's name and description so the trigger condition is explicit
- [ ] Specified type, required, and `additionalProperties: false` on parameter schemas
- [ ] Validated function name against allowlist and arguments against schema before execution
- [ ] Implemented the loop that posts tool output back as a `role: tool` message
- [ ] Added max call count and error standardization to prevent infinite loops and unclear failures

## Closing

In this post, we treated tool calling not as model autonomy but as an application-designed execution boundary. The `tools` parameter publishes allowed function sets and argument contracts, and `tool_calls` returns the model's structured execution requests. The application validates and executes those requests, then feeds results back to the model for a final response.

The model has no execution authority. It proposes tools; the application owns execution responsibility. That separation of responsibility is what lets you attach lookups, searches, data access, and external API integrations while maintaining operational quality.

The next post applies the same contract-first perspective to streaming. If tool calling dealt with function execution boundaries, streaming deals with how to reliably consume partial responses that arrive over time.

## Answering the Opening Questions

- **Is tool calling model autonomy, or an execution boundary designed by the application?**
  Tool calling is not model autonomy. It is a contract where the model can request only the tools and parameters the application explicitly exposes.

- **What should you validate in the `tools` definition and the returned `tool_calls`?**
  In `tools`, validate names, descriptions, and parameter schemas. In `tool_calls`, verify the selected name is in the allowlist and arguments match the expected shape.

- **What guardrails close the function-execution loop safely in production?**
  Allowlists, input validation, timeouts, structured error responses, and result reinjection close the loop safely.

<!-- toc:begin -->
## In this series

- [LLM API Production 101 (1/6): Structured output — JSON mode and response schemas](./01-structured-output.md)
- **LLM API Production 101 (2/6): Tool calling — connecting functions to the model (current)**
- LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery (upcoming)
- LLM API Production 101 (4/6): Caching strategies — reducing cost and latency (upcoming)
- LLM API Production 101 (5/6): Retry and error handling — making API calls reliable (upcoming)
- LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Groq tool use guide](https://console.groq.com/docs/tool-use)
- [JSON Schema fundamentals](https://json-schema.org/understanding-json-schema/)

### Verification-Friendly References

- [Pydantic validation errors](https://docs.pydantic.dev/latest/errors/errors/)

### Related Series

- [Structured output — JSON mode and response schemas](./01-structured-output.md)
- [Streaming in depth — chunk handling and error recovery](./03-streaming-in-depth.md)

Tags: LLM, OpenAI, Streaming, Python
