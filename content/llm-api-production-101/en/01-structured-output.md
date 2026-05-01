---
episode: 1
language: en
last_reviewed: '2026-05-01'
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
  tistory: true
title: Structured output — JSON mode and response schemas
---

# Structured output — JSON mode and response schemas

> LLM API Production 101 (1/6)

Example code: [github.com/yeongseon-books/llm-api-production-101](https://github.com/yeongseon-books/llm-api-production-101/tree/main/en/01-structured-output)

The first production problem in an LLM application is often not answer quality. It is output shape. A demo can render one paragraph of model text and stop there. A real service usually cannot. It needs fields that can be inserted into a database, validated against business rules, passed to another service, or used to drive control flow. At that point, pretty prose is secondary. The important question is whether the application can trust the response format.

Teams often lose time here because the early version looks deceptively easy. The prompt says, "Return JSON," the code calls `json.loads()`, and the first few tests pass. Then the prompt grows, an edge case appears, the model adds a sentence before the payload, wraps the object in a code fence, or renames a key. The failure is not really about model intelligence. It is about the absence of a contract between text generation and application logic.

This article turns that loose boundary into an explicit interface. We will use Groq's JSON mode with `response_format={"type": "json_object"}` and then validate the parsed object with a Pydantic model. Those two steps matter for different reasons. JSON mode narrows the syntactic shape of the output. Pydantic enforces semantic rules such as allowed values, ranges, and required fields. Together they give you a response path that can fail loudly instead of corrupting state quietly.

We will cover five things: why natural-language parsing breaks under production pressure, what JSON mode does and does not guarantee, how to request structured output with the Groq Python SDK, how to validate it with Pydantic, and how to think about logging and recovery when the contract fails.

The main idea is simple: **structured output in production is a contract design problem, not a prompt trick**.

---

<!-- ebook-only:start -->

**The key idea**: Structured Output constrains the model to a JSON schema. A Pydantic model locks the output shape and eliminates parsing errors.

## Where this chapter fits

This is chapter 1 of 6 in the series.
After this chapter, the next one moves on to **Tool calling — connecting functions to the model**.
<!-- ebook-only:end -->

## Runtime setup

To run the examples as written, start with Python 3.10 or later and install the two packages used in this article.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq pydantic
export GROQ_API_KEY="your-issued-key"
```

All examples in this post assume `llama-3.1-8b-instant` and the official `groq` SDK.

---

## Why plain-text parsing does not age well

An early implementation often looks like this: ask the model to classify a support ticket, get a small text answer back, and split the string.

```python
raw_text = "positive, confidence=0.91"
label, confidence = raw_text.split(",")
```

It feels fast because it is short. It is also fragile because nothing in that code defines a durable interface. If the model changes `positive` to `Positive`, inserts a short explanation, or emits `confidence: 0.91` instead of `confidence=0.91`, the parser breaks. Worse, the logs rarely make it obvious whether the problem came from prompt behavior, model variability, or parsing assumptions.

Production systems usually need three guarantees at the same time:

- field names should stay stable
- value types should stay stable
- invalid or missing data should fail immediately

Imagine a ticket classifier. `category` should come from a finite set. `priority` should be an integer inside a specific range. `summary` should not be empty. If you rely on plain text plus custom parsing, those rules end up scattered across prompts, regexes, and post-processing code. JSON mode plus schema validation brings them back into one place.

---

## What JSON mode guarantees and what it does not

Groq's `response_format={"type": "json_object"}` pushes the model toward returning a JSON object instead of free-form prose. That is useful because it creates a minimum syntactic contract. Your response is much more likely to be machine-readable without string surgery.

Still, JSON mode is not the whole solution. It reduces formatting failures. It does not automatically guarantee business correctness.

For example, this is valid JSON:

```json
{
  "sentiment": "positive",
  "confidence": "high"
}
```

The syntax is fine, but `confidence` is a string instead of the numeric value your application may expect. Or the object may omit a required field entirely. That is why it helps to separate the response path into two steps:

1. make the model return a JSON object
2. validate that object against an application schema

If the first step is missing, parsing becomes unreliable. If the second step is missing, your code accepts structurally valid but semantically wrong data. Production stability needs both.

---

## Sending a JSON-mode request with the Groq SDK

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

Three details matter here.

First, the system prompt still says "exactly one JSON object." JSON mode is a provider-side constraint, but it is still helpful to make the contract legible in the prompt itself.

Second, `temperature=0` reduces variation. For extraction work, consistency matters more than creativity.

Third, `json.loads()` only answers one question: is this string parseable JSON? It does not answer whether the payload matches your domain rules. That is why validation comes next.

---

## Locking the response with Pydantic

This is where structured output becomes operationally useful. The code below parses the model output and validates it against a typed schema.

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

This gives you a much stronger application boundary. If the model returns an unknown category, an out-of-range priority, a missing field, or the wrong type, validation fails immediately. That is a good thing. In production, explicit failure is safer than silently storing bad data and discovering the damage later.

There is also a downstream benefit. Once validation succeeds, the rest of your code gets real typed values. `ticket.priority` is already an integer. `ticket.category` is already a constrained enum. `ticket.customer_needs_followup` is already a boolean. The rest of the pipeline becomes simpler because defensive parsing logic is no longer spread everywhere.

---

## Thinking in failure layers

Structured output failures are easier to operate if you separate them into layers.

The first layer is the **request layer**. Authentication problems, timeouts, and network failures belong here. These are normal API concerns and may be retryable.

The second layer is the **JSON parsing layer**. Even with JSON mode, you should still assume that empty strings, truncated payloads, or malformed data are possible in edge cases. When parsing fails, keep the raw response for inspection.

The third layer is the **schema validation layer**. This is often the most informative one. The payload is valid JSON, but it violates domain rules. Maybe `priority=7`, maybe `summary` is empty, maybe `category` is outside the enum.

A layered implementation keeps logging precise:

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

That split also leads to better recovery decisions. A transport failure may justify a retry. A JSON parse failure may justify a prompt adjustment or raw-response capture. A schema failure may justify tighter instructions, simpler field definitions, or a fallback path that asks the model again with narrower constraints.

---

## Contract first, prompt second

It is tempting to keep tuning prompt wording whenever structured output feels unstable. Prompt quality matters, but it should not be the first line of defense. In production, the order is better reversed: define the contract, validate the contract, then improve prompt quality inside that boundary.

Three practical rules help:

- start with a small field set
- encode enums and ranges in code, not only in prose
- log the raw response when validation fails

Trying to extract too many fields at once increases both model error surface and validation complexity. A smaller schema is easier to stabilize. Also, values such as `priority: 1..5` are much easier to enforce than vague instructions like "high priority when urgent." And when validation fails, the raw model output is usually the fastest way to see whether the schema is too ambitious or the prompt is too loose.

---

## Closing

In this first production-focused post, we turned model output into an application contract. `response_format={"type": "json_object"}` narrows the response shape to machine-readable JSON. Pydantic adds typed validation on top of that shape. Together they move you away from brittle string parsing and toward explicit, observable boundaries.

If the earlier series taught the basic request and response loop, this is the point where that loop becomes safe to automate. The next step is to put function execution on top of the same contract and let the model choose tools without letting the surrounding system become ambiguous.

<!-- blog-only:start -->
Next: [Tool calling — connecting functions to the model](./02-tool-calling.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **Structured output — JSON mode and response schemas (current)**
- Tool calling — connecting functions to the model (upcoming)
- Streaming in depth — chunk handling and error recovery (upcoming)
- Caching strategies — reducing cost and latency (upcoming)
- Retry and error handling — making API calls reliable (upcoming)
- Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

---

## References

- <https://console.groq.com/docs/text-chat>
- <https://console.groq.com/docs/text-chat#json-mode>
- <https://docs.pydantic.dev/latest/concepts/models/>

Tags: LLM, OpenAI, Streaming, Python
