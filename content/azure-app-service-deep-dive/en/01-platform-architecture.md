# App Service platform architecture — Front-End, Worker, File Server

> Azure App Service Deep Dive series (1/6)

The intro series established the three-plane model: Management, Runtime, and SCM.
This deep-dive series zooms into the Runtime and SCM substrate underneath that model.
We will follow where a request enters,
where user code actually runs,
where deployed files live,
and how scaling and warm-up signals move through the platform.

One connection matters up front.
**Azure Functions runs on this same App Service infrastructure.**
The Functions Deep Dive series zoomed into the function-host process and its gRPC worker model.
This series zooms into the App Service substrate underneath it.
That is the boundary line:
Functions Deep Dive looked inside the host process;
this series looks at the platform that hosts it.

---

## The big picture — one request through App Service

This is the map for the rest of the series.
Each later episode zooms into one of these boxes.
Get the layout into your head first and the lower-level details land much more cleanly.

![Request path through App Service](../../../assets/azure-app-service-deep-dive/01/01-01-the-big-picture-one-request-through-app.en.png)
The global entry and client edge are intro-series territory.
The Front-End and ARR path are episode 2.
Workers and the per-worker sandbox are episode 3.
Kudu and the file placement path are episode 4.
Worker allocation and scale-out are episode 5.
First-request cost and warm-up signals are episode 6.

---

## Why the three-plane model is not enough here

The three-plane model is great for operations.
It is not detailed enough for internals.

For this series, it helps to redraw App Service as five physical boxes:

1. Front-End
2. ARR-based routing
3. Worker instances
4. Shared file server
5. Kudu deployment engine

You need all five boxes in the picture to explain questions like these in one straight line:

- Why do some requests stay on the same worker?
- Why do multiple workers see the same `/home` content?
- Why can deployment succeed while the first request is still slow?
- Why is a successful Kudu deployment not the same thing as a healthy runtime?

---

## Canonical public architecture — Front-End, Worker, shared storage

Microsoft's public App Service material repeatedly describes the same high-level architecture.

- **Front-End machines** are the HTTP/HTTPS entry point.
- **Worker machines** run the actual app workload.
- **shared storage** lets all workers see the same app content.

The local-cache documentation makes the shared-content point especially explicit.
App content is stored in a durable shared content store,
and that content is shared across multiple VM instances.

![Canonical public architecture — Front-End, Worker, shared storage](../../../assets/azure-app-service-deep-dive/01/01-02-canonical-public-architecture-front-end.en.png)
The critical property here is not raw speed.
It is shared visibility.
The storage is shared,
it survives restarts,
and every worker sees the same mounted path.
That is why deployed content under `/home/site/wwwroot` stays coherent across scaled-out workers.

---

## The Front-End is more than a network hop

The App Service Front-End is not just a TCP pass-through.
It accepts the request,
maps the request to the app,
selects a worker,
and can use affinity cookies to keep the same client on the same worker.

This series stays inside what Microsoft has publicly documented.
Within that boundary, three things are safe to say:

- The Front-End is the public entry point for App Service.
- ARR runs there.
- ARR Affinity cookies can keep requests for a client on the same worker.

That is why App Service fits stateless apps best.
If session state lives in process memory,
scale-in,
worker replacement,
affinity disablement,
or orchestrated restart all become visible to the user.

---

## Workers are what “instance count” actually means

When the portal says the app has three instances,
that count is materializing as execution capacity in the worker pool.

One easy mistake appears over and over.
An app instance is not the same thing as a whole dedicated VM.

The more accurate picture is this:

- The App Service Plan owns worker capacity.
- Apps are placed on that capacity.
- Scale-out increases the app's running instances across workers.

![Workers are what “instance count” actually means](../../../assets/azure-app-service-deep-dive/01/01-03-workers-are-what-instance-count-actually.en.png)
Workers are where user code really runs.
For Windows code apps, the key process is IIS-hosted `w3wp.exe`.
For Linux apps, the key execution unit is a container.
That split matters enough that episode 3 is dedicated to it.

---

## The file server is the common base for deployed content

If you think about App Service like a VM fleet,
it is easy to imagine deployment copying files to each machine's local disk.
The public App Service model points the other way.

There is a shared content store,
and multiple instances look at it.

For Linux apps, the paths readers most often touch are these:

- `/home/site/wwwroot` — deployed app content
- `/home/LogFiles` — logs
- `/home/data` — package and support data

Run-from-package changes the behavior again.
Instead of extracting files into `wwwroot`,
App Service mounts the ZIP package itself as the read-only `wwwroot`.
That distinction matters enough to get its own section in episode 4.

---

## Kudu is the deployment buddy site

The most useful mental model for Kudu is more specific than “separate endpoint.”
Kudu is the app's **SCM buddy site**.

The Kudu architecture wiki describes it as a single-tenant service that sits beside the real site.
That buddy site can reach the real site's files and run deployment logic against them.

So Kudu is not just a diagnostics shell.
It is the deployment engine.
It is the public code path for ZipDeploy and publish APIs.
And for Windows App Service deployment internals, it is the primary open-source window.

![Kudu is the deployment buddy site](../../../assets/azure-app-service-deep-dive/01/01-01-kudu-is-the-deployment-buddy-site.en.png)
Kudu ultimately affects file placement and app reload behavior.
That is why deployment incidents belong in Kudu logs,
while runtime incidents belong in app logs plus platform signals.

---

## Where Functions fits in this picture

If you already read the Functions Deep Dive, one question shows up immediately.

“Where is the Functions host in this map?”

Inside the worker.

- App Service provides the worker, filesystem, and request substrate.
- The Functions host starts on top of that substrate.
- That host then launches language workers and opens the gRPC channel.

![Where Functions fits in this picture](../../../assets/azure-app-service-deep-dive/01/01-05-where-functions-fits-in-this-picture.en.png)
The two series therefore complement each other.
The Functions series zooms into a specific runtime living on App Service.
This series zooms into the general-purpose web platform underneath it.

---

## Where operational failures usually attach

Once the architecture is split into boxes,
incidents split into boxes too.

### Front-End smells

- Only some users stay stuck on a problematic instance
- Traffic is not spreading evenly because affinity is still on
- Requests hit a worker before the app is ready

### Worker smells

- App process startup fails
- Sandbox limits block a library
- Container readiness takes too long

### File server smells

- Deployment reports success but expected files are missing
- Shared content is treated like a local disk and hits locking or latency issues

### Kudu smells

- Build detection succeeds but runtime startup still fails
- Oryx build succeeds but the startup contract fails afterward

This is the operational payoff.
“App Service is acting weird” becomes a short list of boxes to inspect.

---

## Why this series refuses to invent closed-source internals

App Service is not fully open source.
Front-End behavior and worker allocation details are not all available in public repositories.

So the rule for this series is simple.

- If Learn documents it, say it from Learn.
- If Kudu or Oryx exposes it publicly, cite the tagged GitHub source.
- If the detail is not public, do not guess.

That rule matters because deep dives fail fastest when they drift from “documented detail” into “plausible internal fiction.”

---

## Episode 1 wrap

The point of episode 1 is to load one clean map into your head.

> A request enters through the App Service Front-End, where ARR chooses a worker. The worker runs user code. Multiple workers see the same shared `/home` content. Kudu sits beside the app as the SCM buddy site and drives deployment into that shared content path. Azure Functions runs on the same substrate; the Functions Deep Dive looked at the host process on top, while this series looks at the App Service platform underneath.

Episode 2 now zooms into the left-middle part of that map.
We will follow the Front-End and ARR path,
and explain why disabling ARR Affinity is often the right move for stateless apps.

---

## Where this fits in the series

This post is the entry point to the App Service Deep Dive series and places all later topics on one page.
Episode 2 covers Front-End and ARR, episode 3 covers workers and the sandbox, episode 4 covers Kudu and deployment, episode 5 follows scale-out decisions, and episode 6 explains cold starts and warm-up.

---

<!-- toc:begin -->
## In this series

- **App Service platform architecture — Front-End, Worker, File Server (current)**
- Front-End and ARR — how a request reaches a worker (upcoming)
- Workers and the sandbox — where user code actually runs (upcoming)
- Deployment and Kudu — build, sync, release from the inside (upcoming)
- Scaling internals — how Scale Out decisions become new workers (upcoming)
- Cold start and warmup — why the first request is expensive (upcoming)

<!-- toc:end -->

---

## References

### Primary sources
- [Kudu architecture](https://github.com/projectkudu/kudu/wiki/Kudu-architecture/863125fba81e8b30950676bf495c7b7d74c00b92)
- [PushDeploymentController.cs @ S62](https://github.com/projectkudu/kudu/blob/S62/Kudu.Services/Deployment/PushDeploymentController.cs)
- [NinjectServices.cs @ S62](https://github.com/projectkudu/kudu/blob/S62/Kudu.Services.Web/App_Start/NinjectServices.cs)
- [Oryx README @ 20240408.1](https://github.com/microsoft/Oryx/blob/20240408.1/README.md)
- [Oryx BuildScriptGenerator directory @ 20240408.1](https://github.com/microsoft/Oryx/tree/20240408.1/src/BuildScriptGenerator)

### Secondary sources
- [Overview of Azure App Service](https://learn.microsoft.com/azure/app-service/overview)
- [Local Cache in Azure App Service](https://learn.microsoft.com/azure/app-service/overview-local-cache)
- [Run your app in Azure App Service directly from a ZIP package](https://learn.microsoft.com/azure/app-service/deploy-run-package)
- [Kudu service overview](https://learn.microsoft.com/azure/app-service/resources-kudu)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/en/01-host-bootstrap.md)

Tags: Azure, App Service, Distributed Systems, Platform Engineering
