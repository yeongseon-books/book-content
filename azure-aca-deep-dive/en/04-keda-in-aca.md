# KEDA inside ACA — what a scale rule actually creates

> Azure Container Apps Deep Dive series (4/6)

At the product surface, scaling in Azure Container Apps is only a handful of fields.

You set `minReplicas`.
You set `maxReplicas`.
You add an HTTP, TCP, or custom rule.
The platform handles the rest.

That surface is intentionally terse.
The real question is what the platform has to create underneath in order for those rules to turn into replica counts.

The answer is KEDA.

Microsoft documents Container Apps scaling as KEDA-powered.
That tells you two things immediately.

1. The platform is using event-driven autoscaling concepts rather than inventing a wholly separate model.
2. ACA scale rules should map onto the same broad control-loop shape as KEDA `ScaledObject`-driven scaling, even though ACA does not expose those Kubernetes objects directly.

This episode follows that hidden mapping.

---

## The short version: a scale rule is not the scaler itself

In ACA, the scale rule you author is product configuration.
It is not the runtime scaler object.

The platform has to translate that rule into something KEDA can reconcile.

The right mental model is this.

![The short version: a scale rule is not the scaler itself](../../assets/azure-aca-deep-dive/04/04-01-the-short-version-a-scale-rule-is-not-th.en.png)
You never see the hidden object directly.
You still need to understand it, because the behavior you observe is downstream of that translation.

---

## Why KEDA is the correct anchor

KEDA upstream is built around a clean contract.

- A `ScaledObject` describes the target and triggers.
- The KEDA operator reconciles it.
- KEDA creates and updates an HPA.
- The metrics adapter answers external-metric queries for the HPA.

Upstream KEDA source makes this concrete.
The `ScaledObject` type defines trigger metadata, cooldown, min and max replica counts, and target references.
The controller reconciles it and builds the HPA spec.

That is why the quality gate for ACA deep dives insists on pinned KEDA references.
Even though ACA itself is closed-source, KEDA behavior explains the shape of the hidden autoscaling loop.

---

## What ACA exposes versus what KEDA needs

The mapping becomes easier when put side by side.

![What ACA exposes versus what KEDA needs](../../assets/azure-aca-deep-dive/04/04-02-what-aca-exposes-versus-what-keda-needs.en.png)
KEDA needs a scale target, metrics or trigger definitions, and limits.
ACA already has those ideas in its revision template.

That is why the conceptual jump from ACA scale rule to hidden KEDA object is small, even if the product keeps the actual object private.

---

## The first key behavior: scaling is per revision

ACA traffic is app-facing.
Scaling is revision-facing.

That means when you change a scale rule, you are changing a revision-scope property and therefore minting a new revision.
Microsoft's revisions documentation says so directly.

This matters because the scaling engine is attached to immutable revision snapshots, not to one endlessly mutable deployment identity.

![The first key behavior: scaling is per revision](../../assets/azure-aca-deep-dive/04/04-03-the-first-key-behavior-scaling-is-per-re.en.png)
If two revisions are active at once, they can each carry their own scaling behavior while sharing one app-level ingress surface.

That is one of the reasons rollout math and scaling math should never be collapsed into the same concept.

---

## A `ScaledObject` creates HPA behavior, not a replacement for HPA

This is the most common KEDA misunderstanding.
KEDA does not replace HPA with a magical entirely different subsystem.
KEDA manages and feeds HPA behavior.

Upstream KEDA source shows this clearly.
The controller reconciles `ScaledObject` resources and builds HPA specs.
The HPA creation logic sets min and max replica counts, metric targets, and scale target references.

![A `ScaledObject` creates HPA behavior, not a replacement for HPA](../../assets/azure-aca-deep-dive/04/04-04-a-scaledobject-creates-hpa-behavior-not.en.png)
In ACA, you should assume the same broad division of labor.
The product surface gives KEDA enough information to produce HPA-like decisions for the revision.

---

## minReplicas can be zero, and that changes everything

ACA explicitly allows `minReplicas: 0`.
That is the scale-to-zero story.

This is where KEDA's event-driven model matters more than a plain HPA mental model.
A traditional HPA-only framing does not naturally explain activation from zero against event signals.
KEDA does.

![minReplicas can be zero, and that changes everything](../../assets/azure-aca-deep-dive/04/04-05-minreplicas-can-be-zero-and-that-changes.en.png)
Microsoft's scaling docs also note that cooldown behavior is especially relevant when scaling from the final replica down to zero.
That is exactly the kind of lifecycle that makes KEDA the right conceptual anchor.

---

## The control loop: how a custom rule becomes replicas

For custom rules, the flow is easiest to visualize.

![The control loop: how a custom rule becomes replicas](../../assets/azure-aca-deep-dive/04/04-06-the-control-loop-how-a-custom-rule-becom.en.png)
That flow is the right abstraction even when you cannot inspect the actual Kubernetes objects under the product.

---

## HTTP scaling is built in, but the shape still resembles KEDA thinking

ACA has a built-in HTTP scaler based on request concurrency.
Microsoft documents the rule in terms of concurrent requests and a 15-second measurement window.

This is where a careful distinction matters.

Do not say ACA HTTP scaling is literally the upstream `kedacore/http-add-on` product.
That would overstate what the sources prove.

Do say this instead.

- ACA exposes HTTP scaling as a built-in product feature.
- The scaling model is conceptually aligned with KEDA's event-driven autoscaling design.
- The trigger input is request concurrency.

![HTTP scaling is built in, but the shape still resembles KEDA thinking](../../assets/azure-aca-deep-dive/04/04-07-http-scaling-is-built-in-but-the-shape-s.en.png)
That wording stays accurate without pretending the product uses the upstream HTTP add-on one-to-one.

---

## TCP scaling follows the same broad pattern

ACA also exposes TCP concurrency scaling.
The surface looks parallel to HTTP.

- Define a concurrent connection threshold.
- Observe demand over the measurement window.
- Increase replicas when the threshold is exceeded.

The deeper story is the same as HTTP.
The platform owns the product implementation.
The shape still fits a KEDA-style autoscaling loop that turns trigger state into replica changes.

---

## Custom rules are the clearest KEDA-shaped part of ACA

Microsoft's scaling guide is explicit that custom ACA rules map from KEDA scalers.
It even walks the reader through translating KEDA scaler metadata and authentication into ACA rule fields.

That is as close as the product gets to saying, "yes, think in KEDA terms here."

![Custom rules are the clearest KEDA-shaped part of ACA](../../assets/azure-aca-deep-dive/04/04-08-custom-rules-are-the-clearest-keda-shape.en.png)
This documentation pattern is a giveaway.
The product is intentionally exposing a curated KEDA surface, not inventing an unrelated autoscaling language.

---

## Authentication for scale rules is another translation boundary

Upstream KEDA often uses `TriggerAuthentication` resources or identity configuration.
ACA does not expose those raw objects directly.

Instead, the product lets you express the same intent with:

- secrets referenced by scale rule auth fields
- managed identity settings for supported Azure triggers

![Authentication for scale rules is another translation boundary](../../assets/azure-aca-deep-dive/04/04-09-authentication-for-scale-rules-is-anothe.en.png)
The shape remains recognizable.
The resource model is productized.

---

## Why the metrics adapter matters, even when you never name it

Upstream KEDA includes a metrics adapter because HPA needs metric answers.
The KEDA HPA logic attaches external metric selectors so the adapter can answer the HPA's queries for the correct scaled object.

That is an important hidden link.

![Why the metrics adapter matters, even when you never name it](../../assets/azure-aca-deep-dive/04/04-10-why-the-metrics-adapter-matters-even-whe.en.png)
In ACA you never configure the adapter directly.
You still see its consequences every time an external event source or concurrency rule changes replica count.

---

## The KEDA defaults explain ACA behavior readers often notice later

Microsoft's scaling docs call out default polling and cooldown values for custom rules.
Those numbers align with KEDA's control-loop style.

Common observed behaviors that this helps explain:

- Scale changes are not continuous every millisecond.
- Scale-in from one replica to zero has a cooldown flavor that stands out operationally.
- Event-driven activation from zero can feel different from steady-state scaling between nonzero counts.

Those behaviors are not arbitrary product quirks.
They follow from an event-driven autoscaling loop with polling and cooldown semantics.

---

## One rule can wake the revision up

ACA docs also point out that if multiple scale rules exist, the app begins to scale once the first rule condition is met.

That is exactly how you should picture the activation logic.

![One rule can wake the revision up](../../assets/azure-aca-deep-dive/04/04-11-one-rule-can-wake-the-revision-up.en.png)
The deep-dive implication is that rules are not averaged into one giant threshold.
They are multiple activation paths into the same scaling target.

---

## Scale rules belong to the revision template for a reason

Why did ACA choose to make scale rules revision-scope?

Because scaling is part of runtime behavior, not just metadata.

A canary revision might need different limits or trigger thresholds than the currently stable revision.
A new version could change request handling efficiency and therefore justify a different concurrency threshold.

If scale rules were app-scope only, rollout experiments would lose one of the most important control knobs.

![Scale rules belong to the revision template for a reason](../../assets/azure-aca-deep-dive/04/04-12-scale-rules-belong-to-the-revision-templ.en.png)
Revision-scope scaling is what makes that split possible.

---

## What you should not claim

There are two mistakes worth eliminating explicitly.

First, do not claim ACA HTTP scaling is the same thing as the upstream KEDA HTTP add-on.
The conceptual family resemblance is real.
The one-to-one implementation claim is not established by the sources.

Second, do not claim KEDA replaces HPA.
Upstream KEDA source shows it manages and feeds HPA behavior.
ACA inherits that shape conceptually.

Those two corrections keep the story accurate.

---

## The whole autoscaling picture in one diagram

![The whole autoscaling picture in one diagram](../../assets/azure-aca-deep-dive/04/04-13-the-whole-autoscaling-picture-in-one-dia.en.png)
If you remember this diagram, you have the autoscaling internals at the right level of fidelity.

---

## Episode 4 wrap

The compressed model is this.

> In Azure Container Apps, a scale rule is product configuration that the platform translates into KEDA-driven autoscaling behavior for one revision. KEDA then manages the HPA-style control loop that turns trigger state, concurrency, or external metrics into replica counts, including scale-to-zero when `minReplicas` is 0.

That is the hidden machinery behind the friendly Scale blade.

---

## Where this fits in the series

Part 3 explained how revisions receive traffic. This part explained how those same revisions gain or lose replicas underneath the traffic policy. The next part follows the other major hidden sidecar mechanism in ACA, Dapr, from injection to localhost APIs, before the final part returns to Envoy and traces the request path that meets both scaling and routing decisions in motion.

---

## References

### Primary sources
- [`kedacore/keda` tree at `v2.14.0`](https://github.com/kedacore/keda/tree/v2.14.0)
- [`ScaledObject` type in KEDA](https://github.com/kedacore/keda/blob/v2.14.0/apis/keda/v1alpha1/scaledobject_types.go)
- [`ScaledObjectReconciler` in KEDA](https://github.com/kedacore/keda/blob/v2.14.0/controllers/keda/scaledobject_controller.go)
- [`HPA generation in KEDA`](https://github.com/kedacore/keda/blob/v2.14.0/controllers/keda/hpa.go)

### Secondary sources
- [Scaling in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Update and deploy changes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)

### Related series
- [Azure Container Apps 101](../../azure-aca-101/en/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/en/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/en/)
