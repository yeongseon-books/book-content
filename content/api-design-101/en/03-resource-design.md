---
series: api-design-101
episode: 3
title: "API Design 101 (3/10): Resource Design"
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
  - REST
  - Resources
  - URL
  - Backend
seo_description: A practical guide to modeling REST resources — naming, plurals, hierarchies, sub-resources, and identifiers — for backend juniors.
last_reviewed: '2026-05-15'
---

# API Design 101 (3/10): Resource Design

Public URLs usually outlive the database tables and controller names that inspired them. A sloppy path chosen in week one can still be sitting in SDKs, logs, dashboards, and customer code a year later.

This is post 3 in the API Design 101 series.

Here, we treat a good REST path as the output of a solid resource model rather than a naming exercise. Once the resource boundary, hierarchy, and identifier strategy are clear, methods, docs, and caching rules become much easier to keep coherent.

## Questions to Keep in Mind

- How to draw resource boundaries?
- Rules for nouns, plurals, and hierarchy?
- Modeling sub-resources?

## Big Picture

![api design 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/03/03-01-concept-at-a-glance.en.png)

*api design 101 chapter 3 flow overview*

The diagram shows how resources nest and relate: users have orders, orders have items, and the path structure `/users/{id}/orders/{order_id}` reflects those relationships, making the API predictable.

> Resource design is not about naming — it is about finding the natural hierarchy in your domain and making that hierarchy visible in every URL.

## Why It Matters

Once a URL is public, it is *expensive to change*. A bad resource model warps every later decision — methods, status codes, documentation. Resource design is *half of API design*.

> If your resources wobble, everything wobbles.

When the hierarchy is visible from the path alone, docs and debugging get simpler. When everything collapses into flat query parameters, teams start arguing about what the "real" resource even is.

## Key Terms

- **Collection**: a set of same-kind resources — `/users`.
- **Item**: one element of a collection — `/users/42`.
- **Sub-resource**: a resource that *belongs to* another — `/users/42/orders`.
- **Identifier**: the key that names a resource (id or slug).
- **Canonical URL**: the *official* path for a resource.

## Before / After

**Before (verbs, singular, flat)**

```http
GET /getUserOrder?userId=42&orderId=9
```

**After (nouns, plural, hierarchical)**

```http
GET /users/42/orders/9
```

You can read it and understand it.

## Hands-on: Five Steps to a Resource Model

### Step 1 — Start with Nouns

```text
/users
/orders
/articles
```

Plurals by default — collections hold *many*.

### Step 2 — Attach Identifiers

```text
/users/42
/orders/9
/articles/python-logging
```

Numeric ids and meaningful slugs both work.

### Step 3 — Sub-resources

```text
/users/42/orders          # the orders that belong to user 42
/users/42/orders/9        # order 9 within that scope
```

Ownership is visible in the *shape of the URL*.

### Step 4 — Collection Operations

```python
# 4_collection.py
from flask import Flask, jsonify
app = Flask(__name__)

USERS = {42: {"name": "Yeongseon"}}

@app.get("/users")
def list_users(): return jsonify(list(USERS.values()))

@app.get("/users/<int:uid>")
def get_user(uid): return jsonify(USERS[uid])
```

A collection and a single item are *different endpoints*.

### Step 5 — Restraint on Depth

```text
# Good
/users/42/orders

# Too deep
/users/42/orders/9/items/3/options/red
```

Past three levels, query parameters usually serve you better.

## What to Notice in This Code

- Every collection is plural.
- Each resource has *one* canonical URL.
- Deep nesting breaks *writing* even before it breaks reading.

## Five Common Mistakes

1. **Singular collections.** `/user` — counterintuitive.
2. **Verbs in URLs.** `/users/42/activate` — prefer `POST /users/42:activate` for explicit actions.
3. **Leaking the database schema.** Internal names like `user_tbl`.
4. **Exposing primary keys.** Auto-increment ids hurt security and portability.
5. **Multiple canonical URLs.** Two paths for one resource break caching and SEO.

## How This Shows Up in Production

GitHub's `/repos/{owner}/{repo}/issues/{number}` is the canonical example of nouns + plural + hierarchy. Stripe's `/v1/customers/{id}/sources` follows the same pattern. Larger companies write internal *URL guides* because teams keep drifting otherwise.

## How a Senior Engineer Thinks

- Look at *lifetime* — URLs live for years.
- Separate the database model from the resource model.
- Two levels by default, three by exception.
- Express *actions* as state changes; if unavoidable, mark them with `:verb`.
- Public ids should be *opaque* (UUIDs, slugs).

## Verification Signals and Failure Modes

- **Expected output:** Looking at `/users`, `/users/42`, and `/users/42/orders`, you should be able to explain collection, item, and sub-collection roles without extra narration.
- **First check:** If the same resource appears under `/user/42`, `/users?id=42`, and `/members/42`, you no longer have a stable canonical URL.
- **Failure mode:** Let nesting grow without restraint and caching, authorization, and documentation all become harder—until explicit action endpoints start appearing as damage control.

## Checklist

- [ ] Are all collections plural?
- [ ] No verbs in URLs?
- [ ] Each resource has *one* canonical URL?
- [ ] Depth stays at three or fewer levels?
- [ ] Public ids are decoupled from internal primary keys?

## Practice Problems

1. Sketch the resource model of an internal system — seven collections, five relationships.
2. Extend the Step 4 example with `/users/<uid>/orders`.
3. Rewrite five RPC-style endpoints in REST style.

## Wrap-up and Next Steps

Resources define the shape of your API. The next episode turns to *what actions* live on those resources — HTTP methods and status codes.

## Answering the Opening Questions

- **How to draw resource boundaries?**
  - The article treats Resource Design as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Rules for nouns, plurals, and hierarchy?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Modeling sub-resources?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [API Design 101 (1/10): What Is an API?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST Basics](./02-rest-basics.md)
- **Resource Design (current)**
- HTTP Methods and Status Codes (upcoming)
- Request and Response Schemas (upcoming)
- Pagination and Filtering (upcoming)
- Designing Error Responses (upcoming)
- OpenAPI and Swagger (upcoming)
- API Versioning (upcoming)
- Writing Good API Documentation (upcoming)

<!-- toc:end -->

## References

- [REST Resource Naming Guide (restfulapi.net)](https://restfulapi.net/resource-naming/)
- [Google API Design Guide — Resource Names](https://cloud.google.com/apis/design/resource_names)
- [GitHub REST API: Issues](https://docs.github.com/en/rest/issues/issues)
- [Stripe API Reference](https://stripe.com/docs/api)

Tags: Computer Science, APIDesign, REST, Resources, URL, Backend
