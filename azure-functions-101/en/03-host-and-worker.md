# Host and Worker — Who Actually Runs Your Functions?

> Azure Functions 101 series (3/7)

Over the last two posts, we built up a mental model: triggers wake your function, and bindings wire up its inputs and outputs. But there's still one big question we haven't answered. **Who actually runs the Node.js, Python, or Java code you wrote?**

The Azure Functions Host is written in .NET. Yet we happily write functions in Python, Node.js, and Java. **How does code in another language end up running inside a .NET host?** That's what this post is about.

Here's the one-line answer up front:

> Functions runs the **Host process (.NET)** and a **Worker process (in your language)** as two separate processes, and they talk to each other over **gRPC**.

Let's unpack that line, with diagrams.

---

## The big picture — two processes

A traditional web framework usually does everything inside a single process. Loading code, handling HTTP, calling the database, building the response — all in one chunk.

Functions is different. **At a minimum, two processes are involved** in running your function.

- **Host process** — the .NET runtime. Handles trigger detection, scale signals, logging, and binding resolution.
- **Worker process** — a separate process running your language (Node.js, Python, Java, etc.). **This is where your function code actually executes.**

```mermaid
flowchart LR
    subgraph Container [Function App instance]
        Host[Functions Host<br/>.NET process]
        Worker[Language Worker<br/>Node.js / Python / Java process]
        Host <-- gRPC --> Worker
    end

    Trigger[Trigger event] --> Host
    Worker --> UserCode[(Your function code)]
```

This split is the single most important design decision in Functions. So why was it done this way?

---

## Why split them — the secret behind multi-language support

If Host and Worker lived in the same process, the Host would have to embed every language runtime directly — V8, CPython, JVM, and friends. That's effectively impossible. Each language has its own GC, memory model, and dependency story, and cramming them into one process is a recipe for endless conflicts.

Splitting them makes the answer simple.

- The Host **doesn't get involved in actually executing the function.** It only decides when to run it, what input to pass in, and what output to expect back.
- The Worker **runs on its language's standard runtime, unmodified.** A Node.js Worker is just a regular Node.js process. A Python Worker is just a regular Python process.
- The two sides only ever talk through a **language-neutral protocol (gRPC + Protobuf).**

Adding a new language becomes "implement a gRPC client in that language." You don't have to touch the Host at all. In fact, the [`azure-functions-host`](https://github.com/Azure/azure-functions-host) repo has per-language config files like `worker.config.json` that describe which executable to launch and how.

> ⚠️ **One exception**: the .NET in-process model runs inside the Host process itself. That's a historical quirk, and Microsoft is consolidating .NET onto the isolated worker (separate process) model going forward. For new projects, isolated is the recommended path.

---

## What happens inside a single instance

Here's a sequence diagram of one Function App instance handling traffic.

```mermaid
sequenceDiagram
    autonumber
    participant Trig as Trigger source
    participant Host as Host (.NET)
    participant Worker as Worker (Node.js)
    participant Code as Function code

    Note over Host,Worker: Instance startup
    Host->>Worker: Start process (Process.Start)
    Worker->>Host: gRPC connect + load function metadata
    Host-->>Worker: Function init complete

    Note over Trig,Code: Actual invocation
    Trig->>Host: Event fires
    Host->>Worker: InvocationRequest (gRPC)
    Worker->>Code: Call function handler
    Code-->>Worker: Return result
    Worker-->>Host: InvocationResponse (gRPC)
    Host-->>Trig: Done
```

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

```mermaid
graph TB
    FA[Function App<br/>my-app]
    FA --> I1[Instance #1]
    FA --> I2[Instance #2]
    FA --> Idot[...]

    I1 --> H1[Host]
    H1 --> W1a[Worker A]
    H1 --> W1b[Worker B]

    I2 --> H2[Host]
    H2 --> W2a[Worker A]
    H2 --> W2b[Worker B]
```

When a Function App scales out, the number of instances grows, and each instance gets its own Host and Workers. **Instances don't share memory.** That clever "let me cache this in a global variable for speed" trick only works within a single instance — on every other instance, that cache is empty. We'll come back to this in part 6 on scaling.

---

## How many concurrent invocations can a single instance handle?

"If there's only one Worker process, do invocations get processed one at a time?" — fair question, and the answer is "it depends on the language model."

- **Single-threaded event-loop languages like Node.js and Python**: a single Worker can juggle many invocations concurrently using async I/O. The catch is that CPU-bound work blocks every other invocation. Concurrency limits are tuned via `host.json`.
- **Multi-threaded languages like .NET and Java**: a single Worker handles invocations concurrently across multiple threads.
- Either way, **you can also spin up multiple Worker processes to increase concurrency.** Set the `FUNCTIONS_WORKER_PROCESS_COUNT` environment variable, and you'll have several Workers running inside one instance.

This is a third axis sitting between "scale up" and "scale out." On top of **growing the number of instances (scale out)**, you can also **grow the number of Workers per instance** to push concurrency further.

---

## How to verify any of this — it's all open source

None of the above is speculation. The Functions Host is fully open source at [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host), and anyone can read the code. The protobuf file that defines how Host and Worker communicate lives at [`FunctionRpc.proto`](https://github.com/Azure/azure-functions-host). In other words, every claim in this post is verifiable.

The companion series, **Azure Functions Deep Dive**, walks through that code directly to answer questions like:

- How does the Host actually launch a Worker process? (Following it all the way down to `Process.Start`)
- What does the gRPC EventStream handshake look like, exactly?
- When a trigger fires, how does the Dispatcher pick a Worker, and how does an InvocationRequest get built?
- What does the code behind Placeholder mode (the trick that reduces cold starts) look like?

If you finish this 101 series and want to go deeper, that's where to head next.

---

## Up next

That wraps up the "structure of Functions" portion of the series. The next post gets your hands on the keyboard. We'll cover **the shortest possible path from creating a function locally to deploying it to Azure** — the Functions Core Tools, the VS Code extension, and the one-liner that ends with `func azure functionapp publish`.

---

## Series table of contents

| # | Title |
|---|---|
| 1 | [What is Azure Functions? — A world where events call your functions](./01-what-is-azure-functions.md) |
| 2 | [Triggers and Bindings — Everything about function I/O](./02-triggers-and-bindings.md) |
| 3 | **Host and Worker — Who actually runs your functions** ← current post |
| 4 | Deploying your first function — From local to Azure |
| 5 | The four plans — Consumption / Flex Consumption / Premium / Dedicated |
| 6 | Scaling and cold starts — The two faces of serverless |
| 7 | Monitoring and operational basics |

---

## References

**Official documentation**
- [Azure Functions runtime versions overview](https://learn.microsoft.com/en-us/azure/azure-functions/functions-versions)
- [Use multiple worker processes (`FUNCTIONS_WORKER_PROCESS_COUNT`)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [.NET isolated worker model](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)

**Open source code**
- [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host) — the Host itself
- [`Azure/azure-functions-nodejs-worker`](https://github.com/Azure/azure-functions-nodejs-worker)
- [`Azure/azure-functions-python-worker`](https://github.com/Azure/azure-functions-python-worker)
- [`Azure/azure-functions-java-worker`](https://github.com/Azure/azure-functions-java-worker)

**Related series**
- Azure Functions Deep Dive — a deeper series that traces the Host/Worker split at the code level
