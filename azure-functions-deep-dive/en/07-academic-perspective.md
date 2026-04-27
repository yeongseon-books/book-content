# An Academic Perspective — Papers That Analyzed Azure Functions

> Azure Functions Deep Dive series (7/7) · final episode

Over the past six episodes, we followed the host's code directly — boot, worker process, gRPC, Dispatcher, scaling, Placeholder. In this final episode, we take a step back and look at **the academic papers that analyzed Azure Functions**.

This post has two goals.

1. Through a **paper based on real Azure Functions operational data**, published by Microsoft researchers themselves, see "what real workloads actually look like" — something the code alone cannot tell you.
2. Connect the mechanisms we saw in episode 6 — Placeholder, Always Ready, target-based scaling — back to **the academic observations they came from**.

Code tells you "how it works"; papers tell you "why it was built that way." When the two meet, your understanding of the system becomes three-dimensional.

---

## The core paper — Shahrad et al., USENIX ATC 2020

### "Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider"

This is the paper cited most often throughout this series, and it is the centerpiece of this post.

- **Authors**: Mohammad Shahrad, Rodrigo Fonseca, Íñigo Goiri, Gohar Chaudhry, Paul Batum, Jason Cooke, Eduardo Laureano, Colby Tresness, Mark Russinovich, Ricardo Bianchini
- **Affiliation**: Microsoft Azure + Microsoft Research
- **Venue**: USENIX ATC 2020, **Community Award Winner**
- **Links**: [USENIX page](https://www.usenix.org/conference/atc20/presentation/shahrad) · [arXiv:2003.03423](https://arxiv.org/abs/2003.03423)

Look closely at the author list. **Mark Russinovich (Azure CTO)** is a co-author. Paul Batum, Eduardo Laureano, and Colby Tresness are engineers on the Azure Functions team. In other words, this paper is **not an outside researcher's guesswork — it is written by the people who actually build Azure Functions, analyzing operational data from their own system**. The level of credibility is on a different plane.

### The question the paper answered

> "What do FaaS workloads actually look like in the wild? And once we know their characteristics, how can we use that to reduce cold starts?"

The limitation in prior academic work was clear. **Real operational data from commercial FaaS platforms** like AWS Lambda, Azure Functions, and GCF **had never been published.** Researchers either generated synthetic traffic with their own load generators, or relied on small case studies. This paper filled that gap.

### Key findings (as the paper itself reports them)

Quoting directly from the abstract:

> "We show for example that **most functions are invoked very infrequently**, but there is an **8-order-of-magnitude range of invocation frequencies**."
> — Shahrad et al., 2020

Two sentences contain the whole thesis.

**1. Most functions are invoked very infrequently.**

If most functions are rarely invoked, a naive policy of "kill the instance the moment a call finishes" mass-produces cold starts. You don't know when the next call will come, and on average that interval is very long.

**2. The dynamic range of invocation frequencies spans 8 orders of magnitude.**

Functions invoked millions of times per minute and functions barely invoked once a day coexist on the same platform. Handling both well with a single policy is essentially impossible. **You need different policies for different functions.**

These two findings drive the paper's central proposal.

### The proposal (in brief)

> "We then propose a practical resource management policy that **significantly reduces the number of function cold starts, while spending fewer resources** than state-of-the-practice policies."
> — Shahrad et al., 2020

Instead of a simple "fixed idle timeout," the paper proposes **a policy that learns each function's invocation pattern, predicts when the next call will arrive, and keeps instances alive accordingly**. Frequently invoked functions are kept alive longer; rarely invoked ones, shorter. The exact algorithm is reported in the paper, and the result is that **cold starts went down while the resources spent on kept-alive instances also went down**.

> The exact algorithm name and numbers are as reported in the paper; here we cite only "the publicly reported tone of results." For exact savings figures, please refer to the [original paper](https://www.usenix.org/conference/atc20/presentation/shahrad).

### Dataset release

Another major contribution to the academic community was that the paper **released the anonymized trace dataset**.

- **Azure Functions Trace 2019** (the data used in this paper)

This dataset has been used as a baseline in dozens of follow-up academic papers. It became the standard input for any subsequent research that wanted to "evaluate my new policy on a real FaaS workload."

> The dataset link can be found in the paper's "Code, Data, Media" section, or in the [Microsoft AzurePublicDataset repository](https://github.com/Azure/AzurePublicDataset).

### Connecting back to the host code — what we saw in episode 6

In episode 6 we looked at Placeholder and Always Ready. Mapping this paper's message down to the code level, the correspondence looks like this:

| Paper's observation | Mechanism the host adopted |
|---|---|
| Most functions are invoked rarely | **Placeholder pool** — quickly specialize regardless of which function arrives |
| Invocation frequency spans 8 orders of magnitude | **Per-function/per-plan differentiated policies** — Consumption is pay-per-use, Premium uses Always Ready, Flex uses per-function scaling |
| Predicting the next invocation has value | **User-specified Always Ready instance count** — assumes the user knows their own function's pattern |
| Pre-set policy over real-time learning | Flex Consumption's **target-based scaling** — decisions driven by the direct signal of queue length |

It is not that the paper's claims were transplanted verbatim into production, but **the core insight that "no single policy can satisfy everyone"** is clearly reflected in the four plans of episode 4 and the per-function scaling of Flex in episode 5.

---

## Adjacent papers — systems research in the same lineage

These are not as directly tied to this series as Shahrad et al., but two important papers in the same problem space deserve a brief mention.

### Cortez et al., SOSP 2017 — Resource Central

- **Title**: "Resource Central: Understanding and Predicting Workloads for Improved Resource Management in Large Cloud Platforms"
- **Authors**: Eli Cortez, Anand Bonde, Alexandre Muzio, Mark Russinovich, Marcus Fontoura, Ricardo Bianchini
- **Affiliation**: Microsoft

A paper analyzing VM workloads, but **its methodology and philosophy are a direct ancestor of the Shahrad paper**. They share the same convictions: "if you understand workloads well, you can manage resources well," and "let prediction drive operational policy." It is no accident that Russinovich and Bianchini appear on both papers.

### Ambati et al., OSDI 2020 — Harvest VMs

- **Title**: "Providing SLOs for Resource-Harvesting VMs in Cloud Platforms"
- **Affiliation**: Microsoft

A paper on mechanisms for dynamically reclaiming and using leftover capacity. The mindset of "guarantee only what is committed, and use the rest as best-effort" is philosophically of a piece with Functions' **Pre-warmed instances and the differentiated guarantees of Always Ready**.

> The two papers above do not directly address Azure Functions. Treat them as systems research from the same group and the same school of thought.

---

## Closing the series — what did we see?

A one-line summary of each of the seven episodes:

| Ep. | What we saw | Key code/concept |
|---|---|---|
| 1 | How the host boots | `WebJobsScriptHostService`, `ScriptHost.InitializeAsync` |
| 2 | How worker processes are spun up | `RpcWorkerProcess`, `worker.config.json` |
| 3 | How host and worker talk | `FunctionRpc.proto`, `EventStream`, `StreamingMessage` |
| 4 | How an actual call is dispatched into the worker | `FunctionInvocationDispatcher`, `InvocationRequest` |
| 5 | How instances grow | `IScaleMonitor`, `ITargetScaler`, Flex per-function scaling |
| 6 | What it takes to make the first call fast | Placeholder mode, `StandbyManager`, Specialization |
| 7 | The academic basis behind all of these decisions | Shahrad et al., USENIX ATC 2020 |

### One conclusion

The Azure Functions host is **not a giant monolithic abstraction**. Boot, IPC, dispatch, scaling, and warming each exist as independent modules, and each module has a clear interface and a clear source — either public code or a public paper. The impression that "Functions just works like magic" is an illusion produced by well-crafted abstractions; underneath, there is ordinary .NET code we can follow and ordinary systems research we can read.

I hope this series helped peel back one layer of that illusion.

---

## Series table of contents

| # | Title |
|---|---|
| 1 | [Host bootstrap — from `WebJobsScriptHostService` to `ScriptHost`](./01-host-bootstrap.md) |
| 2 | [The worker process — `RpcWorkerProcess` and how language workers start](./02-worker-process.md) |
| 3 | [The gRPC event stream — what host and worker exchange](./03-grpc-event-stream.md) |
| 4 | [Dispatcher and Invocation — how a function call reaches the worker](./04-dispatcher-and-invocation.md) |
| 5 | [Scaling internals — how instances grow](./05-scaling-internals.md) |
| 6 | [Cold start and Placeholder — why the first call can be fast](./06-cold-start-placeholder.md) |
| 7 | **An academic perspective — papers that analyzed Azure Functions** ← current post |

---

## Back to the introductory series

If you have finished the deep-dive series, I recommend going back to the [introductory series (Azure Functions 101)](../../azure-functions-101/ko/01-what-is-azure-functions.md) and looking at the same topics through beginner's eyes again. The same words will sound different.

---

## References

**Core paper**
- Shahrad et al. (2020). *Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider*. USENIX ATC 2020. [USENIX page](https://www.usenix.org/conference/atc20/presentation/shahrad) · [arXiv:2003.03423](https://arxiv.org/abs/2003.03423)

**Related papers**
- Cortez et al. (2017). *Resource Central: Understanding and Predicting Workloads for Improved Resource Management in Large Cloud Platforms*. SOSP 2017.
- Ambati et al. (2020). *Providing SLOs for Resource-Harvesting VMs in Cloud Platforms*. OSDI 2020.

**Dataset**
- [Azure Public Dataset repository](https://github.com/Azure/AzurePublicDataset)

**Host code (commit `5e59423`)**
- [Azure/azure-functions-host](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
