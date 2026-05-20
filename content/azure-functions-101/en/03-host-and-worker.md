---
title: "Azure Functions 101 (3/7): Host and Worker — Who Actually Runs Your Functions?"
series: azure-functions-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Azure Functions
- Serverless
- Cloud
last_reviewed: '2026-05-15'
seo_description: 'Over the last two posts, we built up a mental model: triggers wake
  your function, and bindings wire up its inputs and outputs.'
---

# Azure Functions 101 (3/7): Host and Worker — Who Actually Runs Your Functions?

Over the last two posts, we built up a mental model: triggers wake your function, and bindings wire up its inputs and outputs. But there's still one big question we haven't answered. **Who actually runs the Node.js, Python, or Java code you wrote?**

The Azure Functions Host is written in .NET. Yet we happily write functions in Python, Node.js, and Java. **How does code in another language end up running inside a .NET host?** That is what this chapter is about.

Here’s the one-line answer up front:

> Functions runs the **Host process (.NET)** and a **Worker process (in your language)** as two separate processes, and they talk to each other over **gRPC**.

Let’s unpack that line with diagrams.

This is the third post in the Azure Functions 101 series. Here, we trace how the Host and Worker split turns your code into a real execution model.

## Questions to Keep in Mind

- Why are the Functions Host and the language worker separate processes?
- What message flow runs over the gRPC channel between Host and worker?
- How many function instances does one worker run concurrently?

## Big Picture

![azure functions 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/03/03-01-the-big-picture-two-processes.en.png)

*azure functions 101 chapter 3 flow overview*

This picture places Host and Worker — Who Actually Runs Your Functions? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Host and Worker — Who Actually Runs Your Functions? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Host and worker as two processes

A traditional web framework usually does everything inside a single process. Loading code, handling HTTP, calling the database, building the response — all in one chunk.

Functions is different. **At a minimum, two processes are involved** in running your function.

- **Host process** — the .NET runtime. Handles trigger detection, scale signals, logging, and binding resolution.
- **Worker process** — a separate process running your language (Node.js, Python, Java, etc.). **This is where your function code actually executes.**

This split is the single most important design decision in Functions. So why was it done this way?

---

## Why split them — how one host works with multiple runtimes

If Host and Worker lived in the same process, the Host would have to embed every language runtime directly: V8, CPython, the JVM, and everything around them. That is a messy architecture. Each runtime brings its own GC, memory model, and dependency story, and packing them into one process is an invitation to conflict.

Splitting them makes the answer simple.

- The Host **doesn't get involved in actually executing the function.** It only decides when to run it, what input to pass in, and what output to expect back.
- The Worker **runs on its language's standard runtime, unmodified.** A Node.js Worker is just a regular Node.js process. A Python Worker is just a regular Python process.
- The two sides only ever talk through a **language-neutral protocol (gRPC + Protobuf).**

Adding a new language becomes “implement a Worker for that language and make it speak the protocol.” The Host-side process management lives in [`azure-functions-host`](https://github.com/Azure/azure-functions-host), while per-language `worker.config.json` files live in the language worker repositories. Those config files tell the platform which executable to launch and with which arguments.

> Note: the .NET in-process model runs inside the Host process itself. It is the historical exception. For new projects, the isolated worker model is the safer default.

---

## What happens inside a single instance

Here's a sequence diagram of one Function App instance handling traffic.

![Invocation flow inside one instance](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/03/03-02-what-happens-inside-a-single-instance.en.png)

*Invocation flow inside one instance*
Two things to remember from this flow:

1. **The Host never calls your function code directly.** It just sends a gRPC request that says, "Hey Worker, run this function with this input."
2. **The Worker never receives trigger events directly.** The Host receives them, massages them, and hands them off to the Worker.

These two facts matter operationally, too. If your function falls into an infinite loop and the Worker stops responding, the Host can simply restart the Worker — the Host itself stays healthy. Conversely, if there's a problem with trigger infrastructure (say, a Service Bus connection issue), it'll show up in Host logs while Worker logs stay clean. **This split helps you decide where to look when things break.**

---

## Function App, Host, Worker — the hierarchy of three terms

Three similar-sounding words, easy to mix up at first. Here's how they line up:

| Term | What it is | Unit |
|---|---|---|
| **Function App** | The unit of deployment, billing, and scaling. A container concept that groups multiple functions | The Azure resource you actually see |
| **Host** | The .NET runtime process running on a Function App instance | One per instance |
| **Worker** | The language runtime process the Host spawns | One or more per instance (tunable via `FUNCTIONS_WORKER_PROCESS_COUNT`) |

![Hierarchy among Function App, host, worker](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/03/03-03-function-app-host-worker-the-hierarchy-o.en.png)

*Hierarchy among Function App, host, worker*
When a Function App scales out, the number of instances grows, and each instance gets its own Host and Workers. **Instances don't share memory.** That clever "let me cache this in a global variable for speed" trick only works within a single instance — on every other instance, that cache is empty. We will come back to this in the scaling chapter.

---

## How many concurrent invocations can a single instance handle?

"If there's only one Worker process, do invocations get processed one at a time?" — fair question, and the answer for Python is more specific than the usual “single-threaded event loop” shorthand. **Synchronous `def` functions run on a thread pool inside the Python worker**, so one worker can execute multiple sync invocations concurrently. **Asynchronous `async def` functions share a single asyncio event loop in that worker**, which is great for overlapping I/O but still means CPU-bound work blocks progress differently than it would in a multithreaded runtime.

That is why Python on Functions does not behave like Node.js in a one-to-one sense. The worker is still a **single Python process under the GIL**, so concurrency comes from a mix of thread-pool execution for sync functions and cooperative async scheduling for `async def`, not from a pure “one event loop for everything” model. You can widen concurrency further with `FUNCTIONS_WORKER_PROCESS_COUNT`, which starts multiple worker processes inside one instance.

One more caveat matters operationally on **Flex Consumption**: the default per-instance HTTP concurrency for Python is **1** unless you deliberately tune it. In practice, that means HTTP scale behavior is shaped not only by instance count, but also by Python thread-pool settings such as `PYTHON_THREADPOOL_THREAD_COUNT` and the per-instance HTTP concurrency settings in Functions host/HTTP configuration. So there is a third axis between scale up and scale out: **how much concurrency you allow inside each instance before the platform adds another one**.

## You can verify the split locally in two minutes

The Host/Worker model does not have to stay conceptual. Once you run `func start`, you can inspect the process split on your own machine.

```bash
# Terminal 1
func start --verbose

# Terminal 2
ps -ef | grep -E "func|python.*worker" | grep -v grep
```

```text
...
Worker process started and initialized.
Functions:
    hello: [GET,POST] http://localhost:7071/api/hello
...
python ... azure_functions_worker ...
```

Those two lines are the key artifact. `Worker process started and initialized.` shows the Host brought up a language worker, and the `azure_functions_worker` process shows your code is not running inside the same process as the Host. That small inspection step makes the later discussion about logs, restarts, and concurrency much more concrete.

---

## How to verify any of this — the architecture is open source

None of the above is speculative. The Functions Host is open source at [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host), and the protocol contract between Host and Worker is published separately at [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf). Every core claim in this chapter is traceable to code.

The companion series, **Azure Functions Deep Dive**, walks through that code directly to answer questions like:

- How does the Host actually launch a Worker process? (Following it all the way down to `Process.Start`)
- What does the gRPC EventStream handshake look like, exactly?
- When a trigger fires, how does the Dispatcher pick a Worker, and how does an InvocationRequest get built?
- What does the code behind Placeholder mode (the trick that reduces cold starts) look like?

If you finish this 101 series and want to go deeper, that's where to head next.

---

## Why this execution boundary matters operationally

That wraps up the "structure of Functions" portion of the series. The practical consequence is straightforward: when you create, run, and deploy a function app, you are packaging code that will eventually sit behind this Host/Worker split. That is why local runs and Azure deployments are worth understanding as concrete runtime behavior, not just CLI ceremony.

---

The earlier chapters established the mental model, triggers, and bindings; this one explains the execution boundary between the Host and the Worker. The deployment and operations chapters build directly on that boundary.

---

## Key host.json settings

```json
{
  "version": "2.0",
  "functionTimeout": "00:05:00",
  "extensions": {
    "http": { "maxConcurrentRequests": 100 }
  }
}
```

## Operational checklist

- [ ] Confirmed whether your language uses in-process or out-of-process workers
- [ ] Tuned concurrency limits (`maxConcurrentRequests`, etc.) from workload data
- [ ] Set up the environment so Host and worker logs are separable
- [ ] Tested automatic recovery when a worker crashes
- [ ] Managed key host.json settings via infrastructure IaC

## Answering the Opening Questions

- **Why are the Functions Host and the language worker separate processes?**
  - The article treats Host and Worker — Who Actually Runs Your Functions? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What message flow runs over the gRPC channel between Host and worker?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How many function instances does one worker run concurrently?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Functions 101 (1/7): What Is Azure Functions? — A World Where Events Call Your Code](./01-what-is-azure-functions.md)
- [Azure Functions 101 (2/7): Triggers and Bindings — Everything About Function I/O](./02-triggers-and-bindings.md)
- **Azure Functions 101 (3/7): Host and Worker — Who Actually Runs Your Functions? (current)**
- Azure Functions 101 (4/7): Deploy a Function App — From Localhost to Azure (upcoming)
- Azure Functions 101 (5/7): Which Plan Should You Pick? — Consumption / Flex / Premium / Dedicated (upcoming)
- Azure Functions 101 (6/7): Scaling and Cold Starts — When Serverless Feels Fast and When It Doesn’t (upcoming)
- Azure Functions 101 (7/7): Monitoring and Operations Fundamentals (upcoming)

<!-- toc:end -->

---

## References

**Official Docs**
- [Azure Functions runtime versions overview](https://learn.microsoft.com/en-us/azure/azure-functions/functions-versions)
- [Use multiple worker processes (`FUNCTIONS_WORKER_PROCESS_COUNT`)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [.NET isolated worker model](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)

**Source Code**
- [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host) — the Host itself
- [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf) — the Host/Worker protocol contract
- [`Azure/azure-functions-nodejs-worker`](https://github.com/Azure/azure-functions-nodejs-worker)
- [`Azure/azure-functions-python-worker`](https://github.com/Azure/azure-functions-python-worker)
- [`Azure/azure-functions-java-worker`](https://github.com/Azure/azure-functions-java-worker)

**Related Series**
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/en/) — a deeper series that traces the Host/Worker split at the code level

Tags: Azure, Azure Functions, Serverless, Cloud
