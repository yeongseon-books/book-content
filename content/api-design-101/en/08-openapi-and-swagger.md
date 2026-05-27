---
series: api-design-101
episode: 8
title: "API Design 101 (8/10): OpenAPI and Swagger"
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
  - OpenAPI
  - Swagger
  - Documentation
  - Backend
seo_description: A practical introduction to OpenAPI 3 and Swagger UI, comparing code-first and schema-first approaches for backend juniors.
last_reviewed: '2026-05-15'
---

# API Design 101 (8/10): OpenAPI and Swagger

Once documentation starts lagging behind the code, teams quietly stop trusting it. They probe the API directly, SDKs fall out of sync, and review conversations move away from the contract that callers are supposed to rely on.

This is the 8th post in the API Design 101 series.

Here, we treat OpenAPI and Swagger as contract automation, not just documentation tooling. A single spec needs to drive validation, examples, SDK generation, and mock behavior if it is going to be the source of truth in practice.


![api design 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/08/08-01-concept-at-a-glance.en.png)
*api design 101 chapter 8 flow overview*
> OpenAPI is not a documentation tool — it is a single source of truth that prevents documentation and code from drifting apart.

## Questions to Keep in Mind

- The structure of the OpenAPI 3 spec?
- Swagger UI and Redoc?
- Code-first vs schema-first?

## Why It Matters

A single spec file produces *docs + validation + client code + mock server*. Hand-written docs *always* drift from code — automation is the answer.

> Keep one *single source of truth*.

The real shift is organizational: the spec stops being a secondary artifact and becomes the contract that PRs review. That is what keeps one changed request field from silently diverging across docs, code, and generated clients.

## Key Terms

- **OpenAPI**: the API spec standard (formerly Swagger spec).
- **Swagger UI**: renders the spec as *clickable docs*.
- **Redoc**: an alternative, more readable renderer.
- **Code-first**: the spec is *generated* from code decorators.
- **Schema-first**: the spec is *written first*, code is generated.

## Before / After

**Before (hand-written docs)**

```text
README.md "GET /users/{id} returns user. id is integer."
```

**After (slice of OpenAPI)**

```yaml
paths:
  /users/{id}:
    get:
      parameters:
        - name: id
          in: path
          required: true
          schema: {type: integer}
      responses:
        '200':
          description: User
          content:
            application/json:
              schema: {$ref: '#/components/schemas/User'}
```

## Hands-on: Five OpenAPI Steps

### Step 1 — Minimal spec

```yaml
# openapi.yaml
openapi: 3.0.0
info: {title: Demo API, version: '1.0'}
paths:
  /health:
    get:
      responses:
        '200': {description: OK}
```

Open it in Swagger UI and you get a *try-it-now* button for free.

### Step 2 — components / schemas

```yaml
components:
  schemas:
    User:
      type: object
      required: [id, name]
      properties:
        id: {type: integer}
        name: {type: string}
```

Schemas are *reusable* via `$ref`.

### Step 3 — Code-first (FastAPI)

```python
# 3_codefirst.py
from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    id: int; name: str

app = FastAPI()
@app.get("/users/{uid}")
def user(uid: int) -> User: return User(id=uid, name="Y")
# /docs and /openapi.json are generated automatically
```

### Step 4 — Swagger UI / Redoc

```http
GET /docs        # Swagger UI (try it)
GET /redoc       # Redoc (read it)
GET /openapi.json
```

Two faces of the same spec.

### Step 5 — Generate clients

```bash
# 5_gen.sh
openapi-generator-cli generate \
  -i openapi.json -g python -o ./client
```

Dozens of SDKs from *one command*.

## What to Notice in This Code

- The spec grows *with the code*.
- The same schema powers validation, docs, and SDKs.
- Hand-written docs disappear.

## Five Common Mistakes

1. **Spec and code live *separately*.** They will *certainly* drift.
2. **No examples.** Clients cannot see *what to send*.
3. **Missing error responses.** Only 200 is documented; 4xx/5xx is a *secret*.
4. **No spec versioning.** No way to track changes.
5. **Internal info in the public spec.** Internal endpoints and fields leak.

## How This Shows Up in Production

GitHub publishes its OpenAPI spec at `api.github.com/openapi`. Internally, having CI check that the spec changes whenever the code changes makes drift disappear. FastAPI and NestJS export the spec by default.

## How a Senior Engineer Thinks

- Pick *one* approach — code-first or schema-first, never both.
- Commit the spec to git and review it via PR diffs.
- Always fill in examples — users *copy-paste* to start.
- Document 4xx and 5xx in the spec, not just 200.
- Separate *public* and *internal* specs.

## Verification Signals and Failure Modes

- **Expected output:** `/openapi.json` and `/docs` should describe the same endpoints, schemas, and examples, and CI should fail if they drift.
- **First check:** If the code changes with no spec diff, or the spec changes with no code review, contract drift has already started.
- **Failure mode:** Document only 200 responses and the try-it surface stops teaching users how failure paths actually behave.

## Checklist

- [ ] Is the spec kept in sync with the code (checked in CI)?
- [ ] Does every endpoint have examples?
- [ ] Are 4xx / 5xx defined in the spec?
- [ ] Are `components/schemas` reused with `$ref`?
- [ ] Are public and internal specs separated?

## Practice Problems

1. Express your largest endpoint as OpenAPI.
2. Add `POST /users` to the Step 3 FastAPI app.
3. Sketch a workflow that makes spec changes part of *PR review*.

## Wrap-up and Next Steps

OpenAPI is the API's *protocol, documentation, and code* in one. The next episode looks at the discipline of *changing* a contract — versioning.

## Answering the Opening Questions

- **The structure of the OpenAPI 3 spec?**
  - The article treats OpenAPI and Swagger as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Swagger UI and Redoc?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Code-first vs schema-first?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [API Design 101 (1/10): What Is an API?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST Basics](./02-rest-basics.md)
- [API Design 101 (3/10): Resource Design](./03-resource-design.md)
- [API Design 101 (4/10): HTTP Methods and Status Codes](./04-http-methods-and-status.md)
- [API Design 101 (5/10): Request and Response Schemas](./05-request-and-response-schema.md)
- [API Design 101 (6/10): Pagination and Filtering](./06-pagination-and-filtering.md)
- [API Design 101 (7/10): Designing Error Responses](./07-error-response-design.md)
- **OpenAPI and Swagger (current)**
- API Versioning (upcoming)
- Writing Good API Documentation (upcoming)

<!-- toc:end -->

## References

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Redoc](https://redocly.com/redoc/)
- [FastAPI: Automatic docs](https://fastapi.tiangolo.com/features/)

Tags: Computer Science, APIDesign, OpenAPI, Swagger, Documentation, Backend
