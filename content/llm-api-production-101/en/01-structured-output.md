---
episode: 1
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
title: "LLM API Production 101 (1/6): Structured output — JSON mode and response schemas"
seo_description: Define a reliable application contract using JSON mode and Pydantic validation to transform unpredictable LLM text into stable, machine-readable data.
---

# LLM API Production 101 (1/6): Structured output — JSON mode and response schemas

The first production problem in an LLM application is often not answer quality. It is output shape. A demo can render one paragraph of model text and stop there. A real service usually cannot. It needs fields that can be inserted into a database, validated against business rules, passed to another service, or used to drive control flow. At that point, pretty prose is secondary. The important question is whether the application can trust the response format.

This is the first post in the LLM API Production 101 series.

Teams often lose time here because the early version looks deceptively easy. The prompt says, "Return JSON," the code calls `json.loads()`, and the first few tests pass. Then the prompt grows, an edge case appears, the model adds a sentence before the payload, wraps the object in a code fence, or renames a key. The failure is not really about model intelligence. It is about the absence of a contract between text generation and application logic.

This article turns that loose boundary into an explicit interface. We will use Groq's JSON mode with `response_format={"type": "json_object"}` and then validate the parsed object with a Pydantic model. Those two steps matter for different reasons. JSON mode narrows the syntactic shape of the output. Pydantic enforces semantic rules such as allowed values, ranges, and required fields. Together they give you a response path that can fail loudly instead of corrupting state quietly.

Here we focus on building a structured-output contract with JSON mode and response schemas.

![Structured output: JSON mode and response schemas](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-01-structured-output-json-mode-and-response.en.png)
*Structured output: JSON mode and response schemas*
> Structured output in production is not prettier model text; it is a failure boundary the application can trust.

## Questions to Keep in Mind

- Why does free-form text parsing break so quickly in production?
- What does JSON mode guarantee, and what does schema validation still need to guarantee?
- When the structured-output contract fails, where should the system stop and what should it log?

## Why this post matters

Structured output is the gate that opens automation in an LLM application. If a human is reading the response, sentence quality matters most. If another piece of code is consuming the response immediately, format stability matters more. Classification, extraction, downstream API calls, and business rule application all operate safely only when the structure is dependable.

In practice, teams often try to survive this boundary with prompt tricks. They write progressively longer "answer in JSON" instructions and bolt on increasingly clever parsers when it fails. But that approach does not solve the problem. It scatters responsibility between the prompt and post-processing code. What production needs is not smarter string parsing but a clearer contract.

When JSON mode and schema validation work together, failures do not pass silently. A parse failure stops at the parse layer. A semantic violation stops at the validation layer. That explicitness is what makes retry policies, fallback paths, logging, and regression testing designable in the first place.

## Why plain-text parsing does not age well

![Failure path of plain-text parsing](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-01-why-plain-text-parsing-does-not-age-well.en.png)

*Failure path of plain-text parsing*

An early implementation often looks clean and short. But that brevity means the contract is missing. If the model changes the output even slightly, the parser breaks immediately.

```python
raw_text = "positive, confidence=0.91"
label, confidence = raw_text.split(",")
```

The problem is clear: field-name stability, value-type stability, and missing-data handling are all scattered outside the code. In production, you should not split these rules between prompts and string parsers. They belong in a single contract.

## What JSON mode guarantees and what it does not

![Responsibility split between JSON mode and validation](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-02-what-json-mode-guarantees-and-what-it-do.en.png)

*Responsibility split between JSON mode and validation*

Groq's `response_format={"type": "json_object"}` pushes the model strongly toward returning a JSON object. This makes it much more likely you get a machine-readable response without string surgery. However, valid JSON grammar does not mean valid business semantics.

```json
{
  "sentiment": "positive",
  "confidence": "high"
}
```

The syntax is fine, but `confidence` is a string instead of a number. So the real path splits into two steps: first ensure you get a JSON object, then verify that object matches your application schema.

## Sending a JSON-mode request with the Groq SDK

![JSON mode request and parse flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-03-sending-a-json-mode-request-with-the-gro.en.png)

*JSON mode request and parse flow*

The example below extracts `category`, `priority`, and `summary` from a customer support message.

```python
import json
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
            "You classify customer support tickets. "
            "category must be one of billing/account/bug/shipping. "
            "priority must be an integer from 1 to 5. "
            "summary must be a string between 8 and 120 characters. "
            "Return exactly one JSON object with the keys category, priority, and summary."
        ),
    },
    {
        "role": "user",
        "content": (
            "Ticket: payment succeeded but the order is missing from my order history. "
            "I do not want a refund yet. I need the status checked quickly."
        ),
    },
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    response_format={"type": "json_object"},
    temperature=0,
)

content = completion.choices[0].message.content
payload = json.loads(content)

print(payload)
```

Three details matter here. The system prompt still says "exactly one JSON object" so the contract is legible in the prompt itself. `temperature=0` reduces variation for extraction work. And `json.loads()` only confirms parseable JSON — it says nothing about domain correctness.

## Locking the response with Pydantic

![Relationship between model output and schema checks](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-04-locking-the-response-with-pydantic.en.png)

*Relationship between model output and schema checks*

This is where structured output becomes an actual operational boundary.

```python
import json
import os
from enum import Enum

from groq import Groq
from pydantic import BaseModel, Field, ValidationError

class Category(str, Enum):
    billing = "billing"
    account = "account"
    bug = "bug"
    shipping = "shipping"

class TicketClassification(BaseModel):
    category: Category
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)
    customer_needs_followup: bool

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "Classify the support request. "
                "category must be one of billing/account/bug/shipping. "
                "priority must be an integer from 1 to 5. "
                "summary must be a string between 8 and 120 characters. "
                "customer_needs_followup must be a boolean. "
                "Return exactly one JSON object with the keys category, priority, summary, and customer_needs_followup."
            ),
        },
        {
            "role": "user",
            "content": (
                "Ticket: password reset emails never arrive. "
                "I need access restored today because work is blocked."
            ),
        },
    ],
    response_format={"type": "json_object"},
    temperature=0,
)

raw = completion.choices[0].message.content
data = json.loads(raw)

try:
    ticket = TicketClassification.model_validate(data)
except ValidationError as exc:
    print("validation failed")
    print(exc)
    raise

print(ticket.model_dump())
```

Once validation is attached, the response boundary becomes strong. Disallowed categories, wrong types, and missing fields all fail immediately. In production, loud failure is far safer than silent corruption.

## Thinking in failure layers

![Failure layers in structured output handling](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-05-thinking-in-failure-layers.en.png)

*Failure layers in structured output handling*

Separating failures into request layer, JSON parsing layer, and schema validation layer makes logs and recovery policies precise.

```python
import json
import logging
import os

from groq import Groq
from pydantic import BaseModel, Field, ValidationError
from enum import Enum

class Category(str, Enum):
    billing = "billing"
    account = "account"
    bug = "bug"
    shipping = "shipping"

class TicketClassification(BaseModel):
    category: Category
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)
    customer_needs_followup: bool

logger = logging.getLogger(__name__)
client = Groq(api_key=os.environ["GROQ_API_KEY"])

try:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the support request. "
                    "category must be one of billing/account/bug/shipping. "
                    "priority must be an integer from 1 to 5. "
                    "summary must be a string between 8 and 120 characters. "
                    "customer_needs_followup must be a boolean. "
                    "Return exactly one JSON object with the keys category, priority, summary, and customer_needs_followup."
                ),
            },
            {
                "role": "user",
                "content": "Ticket: payment was approved but the order is missing.",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = completion.choices[0].message.content
    data = json.loads(raw)
    ticket = TicketClassification.model_validate(data)
except json.JSONDecodeError:
    logger.exception("json parse failed")
except ValidationError:
    logger.exception("schema validation failed")
except Exception:
    logger.exception("llm request failed")
```

With this separation, a transport failure becomes a retry candidate, a JSON parse failure triggers raw-response capture and prompt review, and a schema failure points toward contract simplification or field definition hardening. Each layer maps to a different recovery action.

## Deliberately reproducing validation failures

Useful production tests do not end with one success case. You also need to verify what logs and exceptions appear when the contract breaks. The code below reproduces schema failures without calling the model at all.

```python
from enum import Enum

from pydantic import BaseModel, Field, ValidationError

class Category(str, Enum):
    billing = "billing"
    account = "account"
    bug = "bug"
    shipping = "shipping"

class TicketClassification(BaseModel):
    category: Category
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)
    customer_needs_followup: bool

invalid_payload = {
    "category": "refund",
    "priority": 9,
    "summary": "short",
    "customer_needs_followup": "later",
}

try:
    TicketClassification.model_validate(invalid_payload)
except ValidationError as exc:
    print(exc)
```

This output matters because it gives you direct fault-classification data. Whether it is an enum violation, a range violation, or a string-length problem is immediately visible. That clarity means you can redirect toward contract hardening or prompt narrowing rather than blind retries. Regression test suites should always include deliberate failure payloads.

## Validating tool-call arguments with the same schema layer

A gap that structured-output discussions often miss: the model does not only produce direct user-facing answers. In the next step it produces function-call arguments. Validating `response_format` JSON and validating `tool_calls` arguments are not different techniques — they are the same principle applied to different outputs.

The example below validates order-lookup function arguments with Pydantic. The topic here is structured output, but in production this boundary feeds directly into tool execution, so understanding both together is safer.

```python
import json
from enum import Enum

from pydantic import BaseModel, Field, ValidationError

class Locale(str, Enum):
    ko = "ko"
    en = "en"

class OrderLookupArgs(BaseModel):
    order_id: str = Field(min_length=6, max_length=32)
    include_history: bool = False
    locale: Locale = Locale.ko

raw_tool_arguments = '{"order_id":"ORD-1001","include_history":true,"locale":"ko"}'

try:
    args_dict = json.loads(raw_tool_arguments)
    args = OrderLookupArgs.model_validate(args_dict)
    print(args.model_dump())
except json.JSONDecodeError as exc:
    print("tool args json parse failed", exc)
except ValidationError as exc:
    print("tool args schema validation failed", exc)
```

The benefit is clear. The function body only receives validated types, so implementation stays simple. Failures stop consistently before execution. Structured-output contracts extend beyond "model answer parsing" into "execution-boundary validation."

## Response contract versioning

A common production event is field addition. When you add `root_cause` to a schema that previously only had `summary`, new code and old responses can mix in the same path. Instead of only changing the prompt, you should explicitly bump the contract version.

```python
from pydantic import BaseModel, Field

class TicketClassificationV2(BaseModel):
    schema_version: str = "v2"
    category: str
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)
    root_cause: str = Field(min_length=3, max_length=200)

def build_contract_context() -> dict:
    return {
        "schema_version": "v2",
        "allowed_categories": ["billing", "account", "bug", "shipping"],
    }
```

The version field looks trivial but contributes significantly to reducing production incidents. Logs instantly show which contract produced a given response. Cache keys and test fixtures can be isolated per version. When structured output flows to multiple downstream services, this version field becomes the compatibility reference point.

## Regression testing structured-output quality

To keep production quality stable, you need to answer "did schema failure rate increase in this deployment?" with a number. Fixing a set of sample inputs and computing pass rate lets you catch prompt or model changes quickly.

```python
import json
from dataclasses import dataclass

from pydantic import BaseModel, Field, ValidationError

class TicketClassification(BaseModel):
    category: str
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)

@dataclass
class EvalCase:
    name: str
    raw_json: str

cases = [
    EvalCase("valid", '{"category":"bug","priority":4,"summary":"Password reset mail is missing"}'),
    EvalCase("bad-priority", '{"category":"bug","priority":9,"summary":"Password reset mail is missing"}'),
    EvalCase("bad-json", '{"category":"bug","priority":4,"summary":"oops"'),
]

passed = 0
for case in cases:
    try:
        payload = json.loads(case.raw_json)
        TicketClassification.model_validate(payload)
        passed += 1
    except (json.JSONDecodeError, ValidationError):
        pass

print({"total": len(cases), "passed": passed, "pass_rate": round(passed / len(cases), 2)})
```

This test does not replace model-quality evaluation, but it guards the lower bound of contract stability. Combined with tool calling in the next episode, it extends to "pre-execution schema pass rate" — a more direct operational metric.

## Common misconceptions

- Enabling JSON mode does not automatically enforce business rules.
- `json.loads()` success is not the same as schema validation success.
- Trying to fix structured-output failures by prompt wording alone obscures the root cause.
- Enum, range, and required-field rules belong in code validation first, not only in prompt instructions.
- Treating validation failures as "model quality issues" delays proper logging and recovery design.

## Operational checklist

- [ ] Declared output shape with a Pydantic model or JSON Schema
- [ ] Separated logging and retry criteria by failure layer (request / parse / schema)
- [ ] Encoded enum, range, and required-field rules in code validation
- [ ] Preserved raw response on validation failure for traceability
- [ ] Ran sample-input regression tests to verify schema-change impact

## Closing

In this post, we treated structured output as a response contract rather than a prompt trick. `response_format={"type": "json_object"}` narrows the syntactic shape. Pydantic checks whether that shape satisfies application rules. Together they replace string-parsing hope with an operational data boundary.

The important result is that failure is no longer ambiguous. Whether parsing failed, JSON was correct but the schema was wrong, or the request itself failed — each case surfaces at its own layer. That distinction is what makes retry policies, fallback design, and quality logging all take realistic shape.

The next post in this series extends this contract to function execution requests. If structured output was about safely receiving data, tool calling is about safely connecting application capabilities on top of that data.

## Answering the Opening Questions

- **Why does free-form text parsing break so quickly in production?**
  Free-form text breaks because small variations — extra prose, code fences, renamed keys, changed casing — invalidate parsers that have no durable contract.

- **What does JSON mode guarantee, and what does schema validation still need to guarantee?**
  JSON mode pushes the model toward parseable JSON; schema validation enforces required fields, allowed values, and business meaning after parsing.

- **When the structured-output contract fails, where should the system stop and what should it log?**
  Stop at the parsing or validation layer that failed, and log the raw response, validation error, and request identifier so retries and fallbacks stay separate.

<!-- toc:begin -->
## In this series

- **LLM API Production 101 (1/6): Structured output — JSON mode and response schemas (current)**
- LLM API Production 101 (2/6): Tool calling — connecting functions to the model (upcoming)
- LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery (upcoming)
- LLM API Production 101 (4/6): Caching strategies — reducing cost and latency (upcoming)
- LLM API Production 101 (5/6): Retry and error handling — making API calls reliable (upcoming)
- LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)
- [Groq JSON mode guide](https://console.groq.com/docs/text-chat#json-mode)
- [Pydantic model concepts](https://docs.pydantic.dev/latest/concepts/models/)

### Verification-Friendly References

- [JSON Schema object reference](https://json-schema.org/understanding-json-schema/reference/object)

### Related Series

- [Tool calling — connecting functions to the model](./02-tool-calling.md)
- [LLM API Production 101 series](../)
- [LLM App Foundations 101](../../llm-app-foundations-101/en/01-llm-api-first-call.md) — covers what comes before this series: first API call, tokens, and basic prompting. Step back to it when structured output or tool calling feels like it is built on top of message patterns you never solidified.

Tags: LLM, OpenAI, Streaming, Python
