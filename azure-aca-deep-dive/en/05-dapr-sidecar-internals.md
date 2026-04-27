# Dapr sidecar internals — the Go process that lives next to your container

> Azure Container Apps Deep Dive series (5/6)

When readers first enable Dapr in Azure Container Apps, the feature looks deceptively light.

You check a box or set a few fields.
An app ID appears.
Suddenly your service can call localhost on port 3500 or 50001 and talk in terms of state stores, pub/sub, service invocation, or secrets.

That surface is tiny.
The runtime change is not.

What actually happened is that the platform arranged for an upstream Dapr sidecar process, `daprd`, to run beside your user container.
That process is written in Go.
It is injected into the pod.
It gets its own ports, args, probes, certificates, and component-loading behavior.

This episode follows that path from pod mutation to localhost API calls.

---

## The shortest accurate sentence

ACA Dapr is upstream Dapr runtime integrated into the Container Apps product surface.

That sentence matters because it rules out two bad mental models.

First, ACA is not faking a Dapr-like API purely in the control plane.
Second, enabling Dapr is not merely adding metadata to your app.

It changes the pod shape.

```mermaid
flowchart LR
    APP[User container] --> LOCAL[localhost]
    LOCAL --> DAPRD[daprd sidecar process]
    DAPRD --> COMP[Environment-scoped Dapr component]
    COMP --> EXT[External service]
```

The app talks locally.
The sidecar talks outward.
That is the basic contract.

---

## Start with the pod mutation model

Upstream Dapr on Kubernetes injects the sidecar through a mutating admission webhook.
Pinned Dapr source shows this in the injector service code and the pod patch path.

The injector receives the admission review, builds a sidecar config from pod annotations and environment state, and generates patch operations that add the Dapr sidecar container.

```mermaid
sequenceDiagram
    participant API as Kubernetes API server
    participant WH as dapr-sidecar-injector webhook
    participant Pod as Incoming pod spec
    participant Patch as JSON patch

    API->>WH: AdmissionReview for pod
    WH->>WH: build SidecarConfig
    WH->>Patch: generate sidecar patch
    Patch->>Pod: add daprd container, env, ports, probes
```

ACA does not expose raw Kubernetes admission mechanics to you.
But the runtime shape is still best explained by the upstream injector model, because the sidecar that appears is the same class of process.

---

## The injector's job is larger than "append one container"

Pinned upstream Dapr source is revealing here.
The pod patch code does more than say "please add `daprd`."

It computes:

- the sidecar image
- trust anchors and cert material
- control plane addresses
- mode and namespace values
- app ID and app protocol
- health and readiness settings
- port numbers
- volume mounts and environment variables

That is why the sidecar should be thought of as a configured runtime process, not a generic helper container.

---

## The sidecar container is literally `daprd`

The upstream `sidecar_container.go` file is a clean anchor for what gets injected.
It builds a container whose command is `/daprd` and whose args are assembled from the sidecar config.

That one file tells you most of what you need to know.

- This is a real executable, not a passive library.
- It gets explicit CLI flags.
- It exposes explicit ports.
- It receives readiness and liveness probes.

```mermaid
flowchart TB
    CFG[SidecarConfig] --> CMD[/daprd]
    CFG --> ARGS[CLI flags]
    CFG --> PORTS[3500 / 50001 / internal / metrics]
    CFG --> PROBES[readiness and liveness probes]
    CFG --> ENV[namespace, pod name, trust data]
```

This is the right resolution for understanding Dapr in ACA.
The product toggles Dapr at the app surface.
The runtime ends up launching a Go process with a nontrivial configuration surface.

---

## Why calling it a Go process is not trivia

Readers sometimes hear "sidecar" and imagine a generic side channel.
Calling `daprd` a Go process is useful because it centers the real runtime unit.

The process has:

- its own startup path
- its own crash modes
- its own logs
- its own health probes
- its own network listeners
- its own configuration load path

If Dapr is misbehaving in ACA, you are not only debugging your app anymore.
You are debugging a neighboring runtime process that your app depends on.

---

## Boot path: `main.go` to `app.Run()` to runtime creation

Pinned upstream Dapr code makes the bootstrap path readable.

`cmd/daprd/main.go` is tiny.
It calls into `app.Run()`.
That bootstrap path then constructs runtime options, logging, security, and finally the Dapr runtime object before calling `Run`.

```mermaid
flowchart LR
    MAIN[cmd/daprd/main.go] --> APP[cmd/daprd/app/app.go]
    APP --> OPTS[parse options and flags]
    OPTS --> CFG[runtime.Config]
    CFG --> RT[runtime.FromConfig]
    RT --> RUN[rt.Run]
```

For ACA readers, the important takeaway is not every bootstrap detail.
It is that enabling Dapr does in fact launch a complete runtime program, with a normal process lifecycle and configuration pipeline.

---

## The sidecar ports are concrete and important

The upstream runtime config defaults define the Dapr HTTP and gRPC API ports.

- HTTP API: 3500
- Public HTTP port: 3501
- gRPC API: 50001

Microsoft's ACA Dapr overview also documents that the sidecar exposes HTTP on 3500 and gRPC on 50001.

```mermaid
flowchart LR
    APP[User container] -->|HTTP| H3500[localhost:3500]
    APP -->|gRPC| G50001[localhost:50001]
    H3500 --> DAPRD[daprd]
    G50001 --> DAPRD
```

Those ports are not theoretical.
They are the local contract between your code and the sidecar.

When an ACA app uses Dapr service invocation or state operations, it is usually talking to one of these local listeners.

---

## Why localhost matters so much

The sidecar pattern works because your app does not need to know the final network path to the external dependency.
It only needs to know the localhost API contract.

That buys portability and decoupling.

Your app says:

- invoke service X
- save key Y
- publish topic Z

The sidecar says:

- I know which component backs that
- I know where to route it
- I know how to authenticate and serialize it

```mermaid
flowchart LR
    CODE[Application code] --> API[Dapr localhost API]
    API --> DAPRD[daprd]
    DAPRD --> COMP[Configured component]
    COMP --> TARGET[Remote backing service]
```

That is why Dapr can make apps simpler while making the pod shape more complex.

---

## Component loading is where ACA's environment boundary reappears

Episode 2 stressed that Dapr components in ACA are environment-level resources.
This episode shows why that is operationally meaningful.

The sidecar runtime loads component definitions according to the Dapr app ID and scopes.
Microsoft's components documentation is clear that scopes map to Dapr app IDs, not Container App names.

```mermaid
flowchart LR
    ENV[Environment component catalog] --> SCOPE[Component scopes]
    SCOPE --> APPID[Dapr app ID]
    APPID --> DAPRD[daprd sidecar loads component]
```

So the environment owns the component registry boundary.
The sidecar makes the final runtime decision about which scoped components become live for that app.

---

## Enabling Dapr in ACA is an app-level switch with environment-level dependencies

This split is subtle and important.

You enable Dapr on the app.
But the sidecar may depend on environment-level component and configuration state.

That means Dapr behavior in ACA always spans at least two scopes.

- app scope for enablement and sidecar attachment
- environment scope for component availability and sharing

```mermaid
flowchart LR
    APPCFG[App Dapr enablement] --> SIDECAR[daprd attached to pod]
    ENVCFG[Environment components] --> SIDECAR
```

If an app-level Dapr setting looks correct but runtime behavior still fails, the missing piece is often at environment scope rather than app scope.

---

## The injector carries more ACA-relevant detail than most readers realize

The upstream sidecar container builder shows several flags that line up directly with what ACA users observe.

Examples include:

- `--dapr-http-port`
- `--dapr-grpc-port`
- `--app-id`
- `--app-port`
- `--app-protocol`
- `--control-plane-address`
- `--sentry-address`
- `--enable-mtls`

You do not set all of these in ACA yourself.
The point is that the runtime process still needs them.
The managed platform is deciding or deriving many of them on your behalf.

That is another way to see what a managed sidecar integration really means.

---

## Dapr is not only the building-block APIs; it is also health and metadata APIs

Microsoft's Dapr overview for ACA distinguishes between building-block APIs and operational APIs.
That matters because a sidecar is also an observable runtime.

Besides state, pub/sub, invocation, and bindings, the sidecar exposes operational surfaces such as:

- health
- metadata

```mermaid
flowchart LR
    APP[Application] --> BUILD[State / pubsub / invocation APIs]
    APP --> OPS[Health / metadata APIs]
    BUILD --> DAPRD[daprd]
    OPS --> DAPRD
```

So the sidecar is not just a convenience wrapper for remote calls.
It is also an addressable operational endpoint in the pod.

---

## App-to-sidecar and sidecar-to-app are separate channels

There are really two local relationships to remember.

1. Your app calls the sidecar over localhost.
2. The sidecar also calls into your app for certain patterns, such as service invocation delivery or pub/sub handlers.

```mermaid
flowchart LR
    APP[User container] -->|localhost:3500 / 50001| DAPRD[daprd]
    DAPRD -->|app-port / app-protocol| APP
```

That second arrow matters because app port and app protocol settings are not decorative.
They tell the sidecar how to reach your code.

---

## Why sidecar logs belong in your incident timeline

Microsoft's environment documentation notes that Dapr sidecar logs are part of the shared logging destination.
That is exactly what you want during incidents.

If a request fails, the sidecar may know something your user container does not.

- component load failure
- auth issue
- service invocation resolution issue
- connection timeout to backing service
- sidecar startup failure

```mermaid
flowchart LR
    APPLOG[App logs] --> TIMELINE[Incident timeline]
    DAPRLOG[Dapr sidecar logs] --> TIMELINE
    SCALELOG[Scale events] --> TIMELINE
```

Treat sidecar logs as first-class evidence, not as noisy adjunct data.

---

## The mTLS and trust material story is another clue that this is a real runtime

The injector code includes trust anchors, certificate material, Sentry addresses, and identity-related configuration.
That is not cosmetic metadata.

It is the configuration needed for a real security-aware distributed runtime to operate.

This matters because Dapr service invocation is not just a friendly client library experience.
There is actual sidecar-to-sidecar infrastructure and identity plumbing underneath.

Even when ACA abstracts the management details away, the runtime complexity remains.

---

## Putting the whole sidecar lifecycle in one diagram

```mermaid
flowchart LR
    ENABLE[Enable Dapr on app] --> INJECT[Injector mutates pod]
    INJECT --> POD[Pod with user container + daprd]
    POD --> BOOT[daprd bootstrap and runtime config]
    BOOT --> LOAD[Load scoped environment components]
    LOAD --> LOCAL[Expose localhost HTTP/gRPC APIs]
    LOCAL --> RUN[Serve app requests and component calls]
```

That is the compact lifecycle that turns a single ACA checkbox into a second runtime process in your pod.

---

## What this means for ACA operators

There are three practical takeaways.

First, Dapr problems are rarely only "my app code is wrong."
They can be sidecar bootstrap, component scope, environment config, or sidecar-to-backing-service issues.

Second, environment design matters for Dapr because component scope lives there.

Third, localhost success does not mean the external dependency path is healthy.
It only proves your app reached the sidecar.

That last distinction is especially important when diagnosing timeouts.

---

## Episode 5 wrap

The compressed model is this.

> In Azure Container Apps, enabling Dapr causes a real upstream `daprd` sidecar process to be injected into the pod. That Go process exposes the Dapr HTTP and gRPC APIs on localhost, loads environment-scoped components according to Dapr app ID scopes, and becomes the runtime intermediary between your code and remote services.

That is what "Dapr enabled" means at runtime.

---

## Where this fits in the series

The previous part explained how ACA scales revisions. This part explained how ACA mutates the pod shape of those revisions when Dapr is enabled. The final part returns to ingress and follows the first external request through the ACA-managed load balancer, Envoy, service routing, and the pod that may now contain both your container and the sidecar described here.

---

## References

### Primary sources
- [`dapr/dapr` tree at `v1.13.0`](https://github.com/dapr/dapr/tree/v1.13.0)
- [`daprd` entrypoint](https://github.com/dapr/dapr/blob/v1.13.0/cmd/daprd/main.go)
- [`daprd` application bootstrap](https://github.com/dapr/dapr/blob/v1.13.0/cmd/daprd/app/app.go)
- [`Dapr runtime` config defaults](https://github.com/dapr/dapr/blob/v1.13.0/pkg/runtime/config.go)
- [`Dapr injector` pod patch logic](https://github.com/dapr/dapr/blob/v1.13.0/pkg/injector/service/pod_patch.go)
- [`Dapr sidecar container` construction](https://github.com/dapr/dapr/blob/v1.13.0/pkg/injector/patcher/sidecar_container.go)

### Secondary sources
- [Microservice APIs Powered by Dapr](https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview)
- [Dapr Components in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/dapr-components)
- [Azure Container Apps environments](https://learn.microsoft.com/en-us/azure/container-apps/environment)

### Related series
- [Azure Container Apps 101](../../azure-aca-101/en/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/en/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/en/)
