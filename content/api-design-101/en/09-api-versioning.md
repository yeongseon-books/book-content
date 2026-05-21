---
series: api-design-101
episode: 9
title: "API Design 101 (9/10): API Versioning"
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
  - Versioning
  - Compatibility
  - Deprecation
  - Backend
seo_description: A backend junior's guide to URL and header versioning, compatibility policy, and the deprecation and sunset workflow for REST APIs.
last_reviewed: '2026-05-15'
---

# API Design 101 (9/10): API Versioning

Running an API for a long time teaches the same lesson repeatedly: the hard part is not changing the contract, but changing it without breaking trust. A field tweak that feels minor to the backend can still be a production incident for clients that upgrade months later.

This is post 9 in the API Design 101 series.

Here, we treat versioning as change-management discipline rather than just `/v1` syntax. First define what counts as breaking. Then choose how URLs, headers, deprecation notices, and sunset timelines make that policy visible.


![api design 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/09/09-01-concept-at-a-glance.en.png)
*api design 101 chapter 9 flow overview*
> API versioning is not admitting defeat — it is the contract recognizing that both client and server evolve, and building compatibility into that evolution from the start.

## Questions to Keep in Mind

- Distinguishing breaking from non-breaking changes?
- URL versioning vs header versioning?
- Compatibility policy (semver, calver)?

## Why It Matters

External clients depend on your API. One break stops *dozens or hundreds* of clients at once. Good versioning gives you the *freedom to change* — but only with discipline.

> Compatibility is not free.

That transition has to be operational, not symbolic. Usage monitoring, successor links, and explicit sunset headers must keep moving after the code ships, or clients will still be surprised on shutdown day.

## Key Terms

- **Breaking change**: clients must be updated to keep working.
- **Non-breaking change**: new field, new endpoint, etc.
- **URL versioning**: `/v1/...`, `/v2/...`.
- **Header versioning**: `X-API-Version: 2026-05-01` or `Accept: application/vnd.api+json;version=2`.
- **Sunset**: the official end-of-life date for a version.

## Before / After

**Before (silently broken)**

```text
PATCH /users/42  → response date format changes one day
```

**After (explicit version)**

```text
PATCH /v2/users/42
Sunset: Wed, 31 Jan 2027 23:59:59 GMT  (set on v1 responses)
```

## Hands-on: Five Versioning Steps

### Step 1 — URL versioning

```python
# 1_url.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/v1/users/<int:uid>")
def v1(uid): return jsonify(id=uid, name="Y")

@app.get("/v2/users/<int:uid>")
def v2(uid): return jsonify(id=uid, full_name="Y", username="y")
```

The most *intuitive* choice — caching, logs, and routing stay simple.

### Step 2 — Header versioning

```python
# 2_header.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.get("/users/<int:uid>")
def user(uid):
    v = request.headers.get("X-API-Version", "1")
    return jsonify(id=uid, name="Y") if v == "1" else jsonify(id=uid, full_name="Y")
```

URLs stay clean, but *debugging and caching get harder*.

### Step 3 — Non-breaking additions

```text
Add a new field to a response → non-breaking (if clients can ignore it)
Add an *optional* field to a request → non-breaking
```

Adding fields is *usually* safe.

### Step 4 — Deprecation notice

```python
# 4_deprecate.py
@app.get("/v1/users/<int:uid>")
def v1(uid):
    resp = jsonify(id=uid, name="Y")
    resp.headers["Deprecation"] = "true"
    resp.headers["Sunset"] = "Wed, 31 Jan 2027 23:59:59 GMT"
    resp.headers["Link"] = '</v2/users>; rel="successor-version"'
    return resp
```

Standard headers send a *quiet notice* — paired with release notes.

### Step 5 — Sunset procedure

```text
1. Ship the new version + start sending Deprecation
2. Monitor usage (identify clients)
3. Announce sunset 6-12 months out by email
4. Simulate 410 Gone for 30 days before sunset
5. Sunset — return 410 Gone or 308 Permanent Redirect
```

## What to Notice in This Code

- Two versions *coexist*.
- Notices come from a *combination* — headers + docs + email.
- Sunset has a clear *date*.

## Five Common Mistakes

1. **Deploying without versioning.** When external clients break, you cannot trace why.
2. **Treating every change as breaking.** Frequent v3, v4 — operational load explodes.
3. **Killing a version with no notice.** Trust gone.
4. **Keeping every version *forever*.** Code becomes geological strata.
5. **Using `if version == ...` inside one handler.** Every version lives in one place.

## How This Shows Up in Production

Stripe uses *date-based versions* (calver) in headers (`Stripe-Version: 2024-04-10`). GitHub mixes URL versions with `X-GitHub-Api-Version`. AWS versions almost everything explicitly and maintains backwards compatibility for *years*.

## How a Senior Engineer Thinks

- Document the compatibility policy — define *what counts as breaking*.
- New versions are *rare* — most changes can be additive.
- Use *standard headers + an explicit sunset* to deprecate.
- Quantify the *internal cost* of multiple versions (code, tests, docs).
- Sunset only after usage drops — let data decide.

## Verification Signals and Failure Modes

- **Expected output:** After a new version launches, responses from the old version should consistently carry `Deprecation`, `Sunset`, and successor `Link` signals.
- **First check:** If five recent changes get classified differently by different engineers, the compatibility policy itself is still too vague.
- **Failure mode:** Announce a sunset date without measuring actual client usage, and the remaining integrations all fail at once when the deadline arrives.

## Checklist

- [ ] Is the compatibility policy documented?
- [ ] Is the version channel (URL or header) consistent?
- [ ] Are deprecation headers and sunset dates set?
- [ ] Is usage tracked *per client*?
- [ ] Is there a cap on simultaneously live versions?

## Practice Problems

1. Classify five recent changes in your API as breaking / non-breaking.
2. Add code to Step 4 that logs a *warning* when v1 is used.
3. Decide between URL and header versioning for your situation, and write down the trade-offs.

## Wrap-up and Next Steps

Versioning reconciles *contracts* with *change*. The final episode turns to making all those promises *readable* — writing good API documentation.

## Answering the Opening Questions

- **Distinguishing breaking from non-breaking changes?**
  - The article treats API Versioning as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **URL versioning vs header versioning?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Compatibility policy (semver, calver)?**
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
- [API Design 101 (8/10): OpenAPI and Swagger](./08-openapi-and-swagger.md)
- **API Versioning (current)**
- Writing Good API Documentation (upcoming)

<!-- toc:end -->

## References

- [Stripe API Versioning](https://stripe.com/docs/upgrades)
- [GitHub REST API: API Versions](https://docs.github.com/en/rest/overview/api-versions)
- [Sunset HTTP Header (RFC 8594)](https://www.rfc-editor.org/rfc/rfc8594)
- [Deprecation HTTP Header](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-deprecation-header)

Tags: Computer Science, APIDesign, Versioning, Compatibility, Deprecation, Backend
