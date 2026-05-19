---
series: serverless-101
episode: 2
title: Function as a Service
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Serverless
  - FaaS
  - Lambda
  - Runtime
  - Cloud
seo_description: A practical FaaS guide built around a real build-package-run-measure loop instead of isolated packaging tips.
last_reviewed: '2026-05-16'
---

# Function as a Service

This is the second post in the Serverless 101 series.

Once serverless makes sense as a responsibility shift, the next question becomes concrete: **what does that shift look like at the deployment-unit level?** If you cannot answer that, *cold starts*, *package size*, *runtime choice*, and *memory tuning* remain intuition games.

So this post is deliberately narrow. Instead of isolated packaging tips, we will follow one operator loop from start to finish: **write the handler, package it, run the same event locally, inspect the artifact, and only then touch resource tuning**. That loop is what makes FaaS operationally real.

## What You Will Learn

- how the FaaS execution contract is formed by the *handler*, *runtime*, and *deployment package*
- what file layout and command order make a first deployment reproducible
- why package size and dependency count affect runtime behavior directly
- how to troubleshoot the common case where the function works locally but behaves differently in the managed runtime

> FaaS is not a feature for uploading a few lines of code. It is a model that turns handler, runtime, and package into one execution contract.

## Why It Matters

Introductory explanations often make FaaS sound like “just upload a function.” Production reality is the opposite. The runtime initializes before your handler runs. The package is loaded before the event reaches the handler. Initialization cost becomes latency before the business logic even starts.

That is why performance and reliability problems rarely live in the handler body alone. Heavy dependencies, unnecessary files, runtime-version drift, and missing environment variables matter just as much. To understand FaaS is to understand the whole deployment contract, not only the function body.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/02/02-01-concept-at-a-glance.en.png)

*In FaaS, production behavior is shaped as much by package structure and runtime initialization as by the handler itself.*

In practical terms, the flow is simple. You write a handler, bundle its required files, and the platform loads that bundle inside a chosen runtime before invoking the handler. That means real-world FaaS behavior is always the combined result of **handler code + package contents + runtime startup cost**.

## The example contract for this post

We will continue the order-ingest example from post 1. The goal changes, though. Post 1 was about getting the first invocation right. This post is about turning the same handler into a **real FaaS deployment unit**.

Use a minimal layout like this:

```text
faas-demo/
├── app.py
├── smoke_test.py
└── requirements.txt
```

### requirements.txt

```text
requests==2.32.3
```

The dependency list is intentionally small. The first lesson in FaaS packaging is control: know what you shipped, know why it is there, and notice immediately when the artifact gets heavier than expected.

### app.py

```python
import json
from datetime import UTC, datetime


def build_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def handler(event: dict, context) -> dict:
    request_id = getattr(context, "aws_request_id", "local-request")
    payload = json.loads(event.get("body") or "{}")

    order_id = payload.get("order_id")
    items = payload.get("items", [])

    if not order_id or not items:
        return build_response(
            400,
            {
                "ok": False,
                "request_id": request_id,
                "error": "order_id and items are required",
            },
        )

    return build_response(
        202,
        {
            "ok": True,
            "request_id": request_id,
            "accepted_at": datetime.now(UTC).isoformat(),
            "order_id": order_id,
            "item_count": len(items),
        },
    )
```

### smoke_test.py

```python
import json

from app import handler


class LocalContext:
    aws_request_id = "req-smoke-001"


event = {
    "body": json.dumps(
        {
            "order_id": "ord-1001",
            "items": [
                {"sku": "keyboard", "quantity": 1},
                {"sku": "mouse", "quantity": 2},
            ],
        }
    )
}

result = handler(event, LocalContext())
print(json.dumps(result, ensure_ascii=False, indent=2))
```

This separation matters. `app.py` is the deployment entry point. `smoke_test.py` is the smallest reproducible verifier for the same event contract. If those concerns stay mixed, debugging gets blurry very quickly.

## The build → package → run → measure loop

This order is the heart of the post. Resist the urge to skip ahead to memory tuning.

### Step 1 — Install dependencies into a packaging directory

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt -t package
cp app.py package/
```

The important detail is `-t package`. A FaaS deployment artifact is ultimately just the exact set of files the runtime needs. You are not shipping your whole local environment. You are shipping a controlled execution bundle.

### Step 2 — Create one zip artifact

```bash
cd package
zip -r ../function.zip .
cd ..
```

Before you celebrate success, inspect intent. Which files actually ended up in the archive? Did you accidentally include test data, local notes, caches, or development-only assets?

### Step 3 — Run a local smoke test with the same event contract

```bash
python3 smoke_test.py
```

Expected output:

```json
{
  "statusCode": 202,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"ok\": true, \"request_id\": \"req-smoke-001\", \"accepted_at\": \"2026-05-16T10:00:00+00:00\", \"order_id\": \"ord-1001\", \"item_count\": 2}"
}
```

If the handler fails here, deployment is not the next problem to solve. If this step passes, later differences in the managed runtime can be investigated as **environment differences** rather than basic handler bugs.

### Step 4 — Inspect artifact size and contents

```bash
ls -lh function.zip
python3 -m zipfile -l function.zip | sed -n '1,20p'
```

An initial result might look like this:

```text
-rw-r--r--  1 user  staff    1.1M May 16 10:05 function.zip
```

```text
File Name                                             Modified             Size
app.py                                         2026-05-16 10:04:00         1034
requests/__init__.py                           2026-05-16 10:04:00         4963
requests/sessions.py                           2026-05-16 10:04:00        30373
urllib3/__init__.py                            2026-05-16 10:04:00         6979
...
```

This check matters more than many beginners expect. In practice, package obesity is often a better first target than memory tuning. Raising memory without understanding the artifact is like increasing engine power before removing unnecessary cargo.

### Step 5 — Only after measuring do you tune memory and CPU

On many platforms, memory and CPU are coupled. More memory can reduce duration enough to lower total cost. But that is not a rule you memorize. It is a rule you test.

#### A decision flow for memory tuning

1. **Trim dependencies first.**
   - Remove unused libraries, large SDKs, and development-only files.
2. **Rebuild the package and inspect size again.**
   - If the artifact is unexpectedly large, fix that cause first.
3. **Run the same local parity test again.**
   - Confirm that the contract is unchanged.
4. **Then adjust memory and compare duration.**
   - Sometimes higher memory lowers total cost. Sometimes it does not.

That sequence matters because the first FaaS tuning tool is not the memory slider. It is usually **smaller initialization cost and a lighter artifact**.

## When it works locally but not in the managed runtime

This is one of the most common first-response incidents in FaaS. The instinct is often to blame the platform. Usually the explanation is simpler.

### First troubleshooting flow

1. **Is the runtime version the same?**
   - Local Python 3.12 and managed Python 3.11 can behave differently enough to matter.
2. **Are environment variables and secrets really present?**
   - A local default may be hiding a missing managed setting.
3. **Did the artifact include every required file?**
   - The handler may be present while config files or templates are missing.
4. **Is the handler path configured correctly?**
   - The code may be valid but the runtime may be pointing to the wrong `module.function`.

Running this checklist first usually separates “my code is broken” from “my deployment contract is broken” very quickly. The most dangerous debugging habit in FaaS is skipping verification order and jumping straight to retries or memory settings.

## Common Confusions

### Is initialization outside the handler always bad?

No. Reusable clients and configuration loading often belong outside the handler. The catch is that this cost becomes part of cold start behavior, so it should be measured rather than assumed harmless.

### Is a zip package always the right answer?

It is excellent for small simple functions. If you depend on system libraries or need stronger build reproducibility, a container image may be the better deployment unit. The real question is whether you can control artifact contents intentionally.

### Is lower memory always cheaper?

No. If lower memory stretches execution time significantly, total cost can rise. That is why comparisons must use the same input, the same code, and the same measurement baseline.

## Checklist

- [ ] `requirements.txt`, handler code, and smoke test are separated
- [ ] Artifact size and file contents are inspected before deployment
- [ ] Dependency trimming happens before memory tuning
- [ ] The first troubleshooting checks for managed-runtime drift are known

## Wrap-up and Next Steps

FaaS is not just “running a function.” It is an operating contract that binds together **handler, runtime, package, and measurement loop**. Strong teams do not deploy immediately after the code compiles. They package, run the same event locally, inspect the artifact, and only then tune performance.

In the next post, we will move from packaging to delivery semantics and follow a concrete path from **HTTP request to queue, consumer, idempotency check, and DLQ replay**.

<!-- toc:begin -->
- [What is Serverless?](./01-what-is-serverless.md)
- **Function as a Service (current)**
- Trigger and Event (upcoming)
- Cold Start (upcoming)
- Scaling (upcoming)
- State Management (upcoming)
- Queue and Event-driven Architecture (upcoming)
- Observability (upcoming)
- Cost (upcoming)
- Designing a Serverless App (upcoming)
<!-- toc:end -->

## References

### Official Docs

- [AWS Lambda Python handler](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Lambda zip deployment packages](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)
- [AWS Lambda container images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Azure Functions hosting and scale](https://learn.microsoft.com/azure/azure-functions/functions-scale)

### Code and Runtime Examples

- [AWS Lambda developer guide examples (GitHub)](https://github.com/awsdocs/aws-lambda-developer-guide)
- [Azure Functions Python worker samples (GitHub)](https://github.com/Azure/azure-functions-python-worker)
- [Google Cloud Run functions build and deploy guide](https://cloud.google.com/functions/docs/building)

Tags: Serverless, FaaS, Lambda, Runtime, Cloud
