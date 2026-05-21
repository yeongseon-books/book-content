---
series: api-design-101
episode: 5
title: "API Design 101 (5/10): Request and Response Schemas"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - APIDesign
  - JSON
  - Schema
  - Validation
  - Backend
seo_description: A junior backend engineer's guide to JSON schemas, content types, naming, validation, and date and money handling in REST APIs.
last_reviewed: '2026-05-15'
---

# API Design 101 (5/10): Request and Response Schemas

At first, schemas look like a minor JSON-formatting concern. A few months later, they are often where APIs hurt the most: field names drift, time zones disagree, and one silent nullability change breaks multiple clients at once.

This is post 5 in the API Design 101 series.

Here, we treat schemas as boundary contracts that must be enforced, not as optional documentation. Input validation, response serialization, and standard handling for time and money all need to line up if you want later versioning to stay manageable.


![api design 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/05/05-01-concept-at-a-glance.en.png)
*api design 101 chapter 5 flow overview*
> A schema is not documentation — it is a testable promise that every request and response will match the shape the client and server agreed upon.

## Questions to Keep in Mind

- JSON and content types?
- Field naming conventions?
- Where and how to validate?

## Why It Matters

If schemas wobble, *everything* on the client wobbles. Good schemas are *readable* and *evolvable*. Validating at the boundary keeps the inner code *clean*.

> A schema is the *grammar* of your data.

That separation keeps handlers focused on business logic instead of ad hoc coercion. Once validation leaks inward, type fixing, defaulting, and edge-case cleanup start spreading across the service layer.

## Key Terms

- **Schema**: the format and meaning of data.
- **Content-Type**: the body's representation — `application/json` and friends.
- **Validation**: checking incoming data against the schema.
- **Serialization**: turning internal objects into an external representation.
- **ISO 8601**: the *standard* notation for dates and times.

## Before / After

**Before (free form)**

```json
{"u": "Y", "ct": 1714800000, "act": "ok"}
```

**After (meaningful schema)**

```json
{
  "username": "yeongseon",
  "created_at": "2026-05-04T12:00:00Z",
  "active": true
}
```

You read it once and know what it is.

## Hands-on: Five Steps Through Schemas

### Step 1 — JSON body and headers

```python
# 1_json.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.post("/echo")
def echo():
    if request.headers.get("Content-Type") != "application/json":
        return jsonify(error="json required"), 415
    return jsonify(request.get_json())
```

The *server* checks the content type.

### Step 2 — Validation library

```python
# 2_validate.py
from pydantic import BaseModel, Field
class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: str
```

Pydantic, marshmallow, and friends express schemas as *code*.

### Step 3 — Separate response schema

```python
# 3_response.py
from pydantic import BaseModel
class UserOut(BaseModel):
    id: int
    username: str
    created_at: str   # ISO 8601 string
```

Input and output are *different schemas* — common naming is `In` / `Out`.

### Step 4 — Dates and time zones

```python
# 4_time.py
from datetime import datetime, timezone
now = datetime.now(timezone.utc).isoformat()
print(now)   # "2026-05-04T12:00:00+00:00"
```

Store and transmit in *UTC + ISO 8601*.

### Step 5 — Numbers and money

```python
# 5_money.py
# Money: integer minor units — 1.99 USD = 199 cents
amount = 199
currency = "USD"
```

Never use floats for money.

## What to Notice in This Code

- Validation and the handler are *separated*.
- Input and output schemas are distinct.
- Time is UTC, money is integer.

## Five Common Mistakes

1. **Validation inside the handler.** The handler gets dirty and the same checks repeat.
2. **Returning the internal model directly.** Internal change becomes external break.
3. **Ignoring time zones.** Each client interprets time differently.
4. **Floats for money.** A cent disappears to rounding.
5. **Cryptic field names.** `u`, `ct`, `act` — unreadable in six months.

## How This Shows Up in Production

Large APIs converge on *snake_case*, ISO 8601, and integer minor-unit currency (Stripe). Frameworks like FastAPI and NestJS turn schemas into *decorators* — schema is documentation, validation, and type, all at once.

## How a Senior Engineer Thinks

- Put the schema at the *first line* of the boundary.
- Make inputs strict; make outputs evolvable.
- Use *standard* formats for time and money.
- Add new fields; never reinterpret existing ones.
- Design responses so clients can *ignore unknown fields*.

## Verification Signals and Failure Modes

- **Expected output:** The wrong `Content-Type` should fail with `415`, missing required fields should trigger validation errors, and valid payloads should come back in a predictable JSON shape.
- **First check:** If response examples expose ORM field names or temporary abbreviations, input and output schemas are not truly separated.
- **Failure mode:** Leave time zones and money representation undefined early on, and every downstream client and analytics job starts inventing its own correction logic.

## Checklist

- [ ] Does every endpoint have an input schema?
- [ ] Are response schemas separate from input?
- [ ] Are timestamps in UTC + ISO 8601?
- [ ] Is money in integer minor units?
- [ ] Are field names spelled out enough to *read*?

## Practice Problems

1. Express your most-used response schema as a Pydantic model.
2. Outline how to migrate data accidentally stored in KST back to UTC.
3. Decide whether your input schema should *reject* or *ignore* unknown fields, and write down the trade-offs.

## Wrap-up and Next Steps

Schemas are the grammar of data. The next episode tackles a topic that no list endpoint can avoid — pagination and filtering.

## Answering the Opening Questions

- **JSON and content types?**
  - The article treats Request and Response Schemas as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Field naming conventions?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Where and how to validate?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [API Design 101 (1/10): What Is an API?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST Basics](./02-rest-basics.md)
- [API Design 101 (3/10): Resource Design](./03-resource-design.md)
- [API Design 101 (4/10): HTTP Methods and Status Codes](./04-http-methods-and-status.md)
- **Request and Response Schemas (current)**
- Pagination and Filtering (upcoming)
- Designing Error Responses (upcoming)
- OpenAPI and Swagger (upcoming)
- API Versioning (upcoming)
- Writing Good API Documentation (upcoming)

<!-- toc:end -->

## References

- [JSON Schema](https://json-schema.org/)
- [pydantic Documentation](https://docs.pydantic.dev/)
- [ISO 8601 Date and Time Format](https://en.wikipedia.org/wiki/ISO_8601)
- [Stripe API: Working with Money](https://stripe.com/docs/currencies)

Tags: Computer Science, APIDesign, JSON, Schema, Validation, Backend
