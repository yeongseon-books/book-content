---
series: api-design-101
episode: 10
title: Writing Good API Documentation
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - APIDesign
  - Documentation
  - DeveloperExperience
  - Examples
  - Backend
seo_description: A practical guide to API docs that get adopted — Getting Started, Tutorials, Reference, Changelog, and SDKs as a single system.
last_reviewed: '2026-05-04'
---

# Writing Good API Documentation

Good API docs are a system, not a reference dump. Getting Started, tutorials, reference, changelog, and SDK guidance all matter.

This is the final post in the API Design 101 series.

## What You Will Learn

- The five axes of documentation
- Reaching the first call in *under five minutes*
- The weight of examples
- The role of changelogs and SDKs
- How docs grow over time

## Why It Matters

Documentation drives *adoption* more than the API itself. The same endpoint can take five minutes to call — or half a day — depending on the docs.

> Documentation is *part of the product*.

## Concept at a Glance

```mermaid
flowchart LR
    A["Getting Started"] --> B["Tutorials"]
    B --> C["Reference"]
    C --> D["Changelog"]
    D --> E["SDKs / CLIs"]
```

## Key Terms

- **Getting Started**: from zero to *first call* in five minutes.
- **Tutorial**: walks through one scenario *end to end*.
- **Reference**: the *dictionary* of endpoints and fields.
- **Changelog**: the record of every version change.
- **SDK**: a per-language client library.

## Before / After

**Before (reference only)**

```text
- /users (GET, POST, ...)
- /orders (GET, POST, ...)
```

The names alone don't tell you what to do.

**After (all five axes)**

```text
1. Getting Started — first call in five minutes
2. Tutorials — checkout flow, sign-up flow
3. Reference — every endpoint
4. Changelog — versioned changes
5. SDKs — Python, JS, Ruby
```

## Hands-on: Five Steps to Better Docs

### Step 1 — Getting Started

```markdown
# Getting Started

1. Sign up at https://example.com → get an API key
2. First call (curl):
   ```bash
   curl https://api.example.com/v1/health \
     -H "Authorization: Bearer <YOUR_KEY>"
   ```
3. Seeing `{"status": "ok"}` means success.
```text

The *five-minute rule* — the user must have *something working* in five minutes.

### Step 2 — Tutorial (scenario-driven)

```markdown
# Accept Your First Payment

1. Create a customer (POST /v1/customers)
2. Create a payment intent (POST /v1/payment_intents)
3. Confirm
4. Receive the webhook
```

Not a feature list — the flow toward a *goal*.

### Step 3 — Reference + examples

```markdown
## POST /v1/customers
Input: {name, email}
Response (201):
```json
{"id": "cus_abc", "name": "Y", "email": "y@example.com"}
```

Errors:
| code | status | meaning |
|------|--------|---------|
| validation_error | 422 | name or email missing |
| email.duplicate | 409 | email already registered |
```text

Every reference page needs *examples + an error table*.

### Step 4 — Changelog

```markdown
# Changelog

## 2026-05-01
- BREAKING: removed `name` from /v1/users. Use `full_name`.
- ADD: /v2/users gains `created_at`.

## 2026-04-15
- DEPRECATE: /v1 — sunset 2027-01-31.
```

*Date and category for every change*.

### Step 5 — SDKs and a try-it environment

```python
# 5_sdk.py
from example_api import Client
c = Client(api_key="...")
print(c.users.get(42))
```

*Copy-paste-able* code and a *clickable* try-it surface (Swagger UI).

## What to Notice in This Code

- The first screen is *Getting Started*.
- Every reference page has *examples*.
- The changelog reads in *reverse chronological* order.

## Five Common Mistakes

1. **Reference only.** New users have no idea *where to start*.
2. **Missing or incorrect examples.** Even with copy-paste, *nothing runs*.
3. **No changelog.** Users cannot track changes.
4. **Errors are not documented.** The 4xx body is a *secret*.
5. **Docs in a *separate repo*.** Sync with code becomes *impossible*.

## How This Shows Up in Production

Stripe and Twilio set the *gold standard* — their five axes are consistent and well-maintained. Treat your *internal* APIs like public ones and adoption rises while support requests fall — that is what *DX* means.

## How a Senior Engineer Thinks

- Keep docs *in the same repo* as code.
- *Test* examples (run them in CI).
- *Auto-generate* the changelog (PR labels → release notes).
- *Measure* the five-minute rule — observe real users.
- Improve the most-visited pages first.

## Checklist

- [ ] Does Getting Started reach a first call in five minutes?
- [ ] Do all endpoints have examples?
- [ ] Is the changelog up to date?
- [ ] Are errors tabulated in the reference?
- [ ] Is there an SDK or a try-it surface?

## Practice Problems

1. Rewrite your API's Getting Started against the five-minute rule.
2. Add *three scenario* examples to the most-used endpoint.
3. Outline a CI step that *runs* example code on each PR.

## Wrap-up and Series Conclusion

An API is the *sum* of its contracts, behaviors, and documentation. We started in episode 1 with *the contract* — and worked through REST, resources, methods, schemas, pagination, errors, OpenAPI, and versioning — finishing with *documentation*. Before moving on, build a small API end-to-end yourself. That is the deepest learning.

<!-- toc:begin -->
- [What Is an API?](./01-what-is-an-api.md)
- [REST Basics](./02-rest-basics.md)
- [Resource Design](./03-resource-design.md)
- [HTTP Methods and Status Codes](./04-http-methods-and-status.md)
- [Request and Response Schemas](./05-request-and-response-schema.md)
- [Pagination and Filtering](./06-pagination-and-filtering.md)
- [Designing Error Responses](./07-error-response-design.md)
- [OpenAPI and Swagger](./08-openapi-and-swagger.md)
- [API Versioning](./09-api-versioning.md)
- **Writing Good API Documentation (current)**
<!-- toc:end -->

## References

- [Stripe Documentation](https://stripe.com/docs)
- [Twilio Documentation](https://www.twilio.com/docs)
- [Write the Docs — API documentation](https://www.writethedocs.org/topic-guides/api-documentation/)
- [Diataxis Framework (tutorials/how-to/reference/explanation)](https://diataxis.fr/)

Tags: Computer Science, APIDesign, Documentation, DeveloperExperience, Examples, Backend
