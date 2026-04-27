# The Envoy ingress path — how the first request reaches your container

> Azure Container Apps Deep Dive series (6/6)

The public story for ingress in Azure Container Apps is concise.

Enable ingress.
Get an FQDN.
Receive HTTPS traffic.
Optionally split traffic across revisions.

That is enough to ship a service.
It is not enough to explain the first request path.

This final episode follows that path at the right resolution for ACA operators:

external client -> ACA-managed load balancer -> Envoy ingress -> Service -> Pod

Along the way, Envoy terminates TLS, matches the route, applies any revision weights, and forwards to the upstream service for the chosen revision.

---

## Start with the full path, not with the app

The first mistake in ingress debugging is to start at the user container.
The request has already crossed several platform layers before that point.

![Start with the full path, not with the app](../../assets/azure-aca-deep-dive/06/06-01-start-with-the-full-path-not-with-the-ap.en.png)
If you keep this order in your head, ingress incidents become easier to localize.

- No connection at all may be outside the pod entirely.
- Host, TLS, or header issues usually live before the service hop.
- Revision selection happens at the proxy layer.
- App bugs are the last part of the path, not the first.

---

## What Microsoft documents directly about ACA ingress

The ingress overview gives you the product-level contract.

With HTTP ingress, ACA provides:

- TLS termination
- HTTP/1.1 and HTTP/2
- WebSocket and gRPC support
- ports 80 and 443
- automatic HTTP-to-HTTPS redirect by default
- an FQDN
- traffic splitting between revisions
- session affinity

Every bullet in that list implies proxy behavior.
That is why Envoy is the right runtime anchor.

---

## The load balancer is the first managed edge, not the final router

The user does not talk directly to your pod.
The external request first reaches ACA's managed edge infrastructure.

This matters because the public endpoint is a platform endpoint.
Your container is one downstream destination behind it.

![The load balancer is the first managed edge, not the final router](../../assets/azure-aca-deep-dive/06/06-02-the-load-balancer-is-the-first-managed-e.en.png)
The load balancer gets the request into the environment ingress plane.
Envoy handles the HTTP-aware routing decisions after that.

That division is what makes features like TLS termination, route matching, and weighted traffic policy possible without exposing your pod directly.

---

## TLS ends at ingress, not at your container by default

Microsoft documents TLS termination at the ingress point for HTTP ingress.
That means the HTTPS connection from the client is terminated before the request is forwarded to the user container.

![TLS ends at ingress, not at your container by default](../../assets/azure-aca-deep-dive/06/06-03-tls-ends-at-ingress-not-at-your-containe.en.png)
Operationally, this explains several things.

- The app often sees forwarded headers instead of the original TLS socket.
- Certificate handling belongs to the ingress surface.
- Protocol confusion can happen if the app ignores forwarded headers and assumes it owns the client-facing TLS boundary.

This is normal reverse-proxy behavior, and ACA documents the forwarded headers that help your app recover the original request context.

---

## Forwarded headers are part of the ingress contract

ACA ingress documents headers such as:

- `X-Forwarded-Proto`
- `X-Forwarded-For`
- `X-Forwarded-Client-Cert` in the appropriate certificate modes

These headers exist because the app is behind a proxy boundary.

![Forwarded headers are part of the ingress contract](../../assets/azure-aca-deep-dive/06/06-04-forwarded-headers-are-part-of-the-ingres.en.png)
If your app builds absolute URLs, enforces scheme-aware redirects, or logs client IP, these headers are part of the real runtime path, not optional decoration.

---

## The routing step happens before the service hop

After TLS termination and route matching, Envoy must choose an upstream destination.
That choice can be simple or weighted.

If the app has one active revision and no split, the routing target is straightforward.
If multiple revisions are active, Envoy applies traffic weights before forwarding to the selected upstream.

![The routing step happens before the service hop](../../assets/azure-aca-deep-dive/06/06-05-the-routing-step-happens-before-the-serv.en.png)
This is exactly why episode 3 framed traffic splitting as ingress routing data.
The selection must happen here, not later inside the app.

---

## Envoy weight means upstream cluster weight

Repeat the vocabulary carefully.

In Envoy, a cluster is an upstream service target.
It is not a Kubernetes cluster.

Pinned Envoy route API source defines weighted cluster configuration at the routing layer.
That is the right conceptual match for ACA revision traffic splitting.

![Envoy weight means upstream cluster weight](../../assets/azure-aca-deep-dive/06/06-06-envoy-weight-means-upstream-cluster-weig.en.png)
So when readers ask where ACA's 80/20 split "really lives," the best answer is: in ingress routing state that selects among revision upstreams using weighted destinations.

---

## The service hop is easy to forget because ACA hides Kubernetes

From the user's point of view, traffic goes to "the revision."
At runtime there is still a service-style hop between ingress and pod replicas.

![The service hop is easy to forget because ACA hides Kubernetes](../../assets/azure-aca-deep-dive/06/06-07-the-service-hop-is-easy-to-forget-becaus.en.png)
That hop matters because the upstream destination Envoy chooses is not usually one individual pod.
It is the service endpoint set for the chosen revision, which then fans into ready replicas.

This is also where scaling and ingress finally meet.
Envoy can only send traffic to replicas that exist and are ready behind that service.

---

## Readiness is part of the ingress path whether you think about it or not

Episode 3 discussed readiness as the gate before traffic moves to a new revision.
Episode 4 discussed scale activation and replica creation.
Here both ideas meet.

Envoy may know a revision exists.
It still needs healthy upstream endpoints behind the revision service to complete the request path.

![Readiness is part of the ingress path whether you think about it or not](../../assets/azure-aca-deep-dive/06/06-08-readiness-is-part-of-the-ingress-path-wh.en.png)
That is why ingress debugging is inseparable from revision state and replica readiness.
The request path is cross-cutting by design.

---

## The first request to a scale-to-zero revision is special

ACA supports scale-to-zero.
That means the first request path may target a revision with no warm replicas yet.

The exact private product orchestration is Microsoft-owned and closed-source.
Still, the operator-level shape is clear.

![The first request to a scale-to-zero revision is special](../../assets/azure-aca-deep-dive/06/06-09-the-first-request-to-a-scale-to-zero-rev.en.png)
This is the point where ingress and autoscaling stop being separate topics.
The first request may be the event that forces the data plane to wait for the scale path to produce a ready upstream.

---

## Why the first request can feel slower even when the platform is healthy

If a revision is at zero, the first request is paying for several hidden steps.

- activation decision
- replica creation
- image start path if needed
- app startup
- probe success
- sidecar startup if Dapr is enabled

![Why the first request can feel slower even when the platform is healthy](../../assets/azure-aca-deep-dive/06/06-10-why-the-first-request-can-feel-slower-ev.en.png)
That latency is not only an app concern.
It is the whole ingress-to-readiness path compressed into one user-visible moment.

---

## Dapr adds another runtime participant behind the ingress path

If Dapr is enabled, the pod that finally receives the request may contain both your container and `daprd`.

The ingress path itself still ends at the pod and user container endpoint.
But what happens after that can immediately involve the sidecar.

![Dapr adds another runtime participant behind the ingress path](../../assets/azure-aca-deep-dive/06/06-11-dapr-adds-another-runtime-participant-be.en.png)
This is why one failing end-user request can span ingress routing, revision readiness, pod startup, and sidecar behavior in one chain.

---

## Session affinity lives at ingress too

ACA documents sticky sessions as an ingress feature.
That is another clue that ingress owns more than coarse routing.

If session affinity is enabled, Envoy-style ingress behavior tries to keep requests from one client pinned consistently.
That happens before the request reaches the app.

The important point for this series is not every sticky-session detail.
It is that revision and replica selection are still proxy concerns.

---

## Internal ingress follows the same broad shape without the public edge

For internal-only apps, the internet-facing part disappears.
The service still sits behind the environment's ingress and service-routing machinery.

![Internal ingress follows the same broad shape without the public edge](../../assets/azure-aca-deep-dive/06/06-12-internal-ingress-follows-the-same-broad.en.png)
The transport path changes at the edge.
The proxy-routing and service-upstream logic stays recognizably similar.

---

## A practical ingress debugging ladder

When the request fails, walk the path in order.

1. Can the client resolve and reach the public FQDN?
2. Is ingress enabled with the expected external or internal posture?
3. Is TLS termination and scheme handling correct?
4. Is traffic being routed to the expected revision or label?
5. Does the chosen revision have ready replicas behind its service?
6. Does the user container respond correctly once the request arrives?

![A practical ingress debugging ladder](../../assets/azure-aca-deep-dive/06/06-13-a-practical-ingress-debugging-ladder.en.png)
This ladder is just the request path turned into an operator checklist.

---

## The whole request path in one diagram

![The whole request path in one diagram](../../assets/azure-aca-deep-dive/06/06-14-the-whole-request-path-in-one-diagram.en.png)
This is the final "all boxes connected" picture for the series.

The environment contains the network boundary.
Revisions provide immutable deployment targets.
KEDA ensures replicas exist.
Dapr may be present beside the app.
Envoy is the router that glues the whole external path together.

---

## Episode 6 wrap

The compressed model is this.

> In Azure Container Apps, the first external HTTP request does not go straight to your container. It passes through an ACA-managed load balancer into Envoy, where TLS is terminated, routes are matched, and revision traffic weights are applied. Envoy then forwards to the chosen revision's service, which sends the request to a ready pod replica.

That is the ingress path that ties the whole series together.

---

## Where this fits in the series

This final part closed the loop on every earlier concept in the series. The environment supplied the network boundary, revisions supplied immutable traffic targets, KEDA supplied ready replicas, and Dapr could supply an additional sidecar runtime once the request reached the pod. If you want the product-level on-ramp before revisiting these internals, the ACA 101 series is the right companion, and the AKS and Azure Functions deep dives provide useful contrast in how much of the underlying platform each service exposes.

---

<!-- toc:begin -->
## In this series

- [ACA architecture — what Microsoft layered on a hidden Kubernetes](./01-aca-architecture.md)
- [Environment internals — the network, observability, and Dapr scope boundary](./02-environment-internals.md)
- [Revisions and traffic splitting — where Envoy weights come from](./03-revision-and-traffic-split.md)
- [KEDA inside ACA — what a scale rule actually creates](./04-keda-in-aca.md)
- [Dapr sidecar internals — the Go process that lives next to your container](./05-dapr-sidecar-internals.md)
- **The Envoy ingress path — how the first request reaches your container (current)**

<!-- toc:end -->

---

## References

### Primary sources
- [`Envoy` route components at `v1.30.0`](https://github.com/envoyproxy/envoy/blob/v1.30.0/api/envoy/config/route/v3/route_components.proto)
- [`Envoy` router implementation at `v1.30.0`](https://github.com/envoyproxy/envoy/blob/v1.30.0/source/common/router/config_impl.cc)

### Secondary sources
- [Ingress in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Traffic splitting in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting)
- [Update and deploy changes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Scaling in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)

### Related series
- [Azure Container Apps 101](../../azure-aca-101/en/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/en/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/en/)

Tags: Container Apps, KEDA, Dapr, Envoy
