
# Which Plan Should You Pick? — Consumption / Flex / Premium / Dedicated

The deployment chapter created the app on Flex Consumption because that is the current default candidate for new serverless work. Classic Consumption still matters historically and operationally, but current Microsoft Learn guidance recommends **evaluating Flex Consumption first for new serverless apps**.

That does not make Consumption irrelevant. You still need to understand all four hosting models to make a sound decision. This chapter covers **Consumption / Flex Consumption / Premium / Dedicated (App Service Plan)** side by side, with the current caveats left intact.

The goal is simple: **understand what each plan gives you, what it constrains, and which one fits your workload**.

---

## Questions this chapter answers

- What does each plan (Consumption, Premium, Dedicated) bill against?
- When should cold-start tolerance drive the plan choice instead of price?
- Which platform features (VNet integration, always-ready instances) lock you into Premium or Dedicated?
- What is each plan's scale ceiling, and where does that hit your peak load?
- How do you build a monthly cost simulation that does not lie?

## One-line definitions

| Plan | One-line definition |
|---|---|
| **Consumption** | The simplest pay-per-use serverless plan. An older path, and Windows-first in practice. |
| **Flex Consumption** | Microsoft's recommended Linux-based pay-per-use plan for new serverless apps, with VNet support, selectable memory, and per-function scaling. |
| **Premium** | A higher-end plan that reduces or avoids cold starts through Always Ready and prewarmed capacity, with VNet support and larger SKUs. |
| **Dedicated (App Service Plan)** | Functions running on regular App Service infrastructure, where scaling is managed through App Service rules instead of event-driven platform scaling. |

If your mental shortcut has been “Functions = autoscale,” this is where that model needs refinement. **The scaling model and operating posture change quite a bit across these plans.**

---

## Big picture

![Plan differences in billing, warm capacity, scaling](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/05/05-01-big-picture.en.png)

*Plan differences in billing, warm capacity, scaling*
Now put the differences on one table.

---

## Comparison table

| Feature | Consumption | Flex Consumption | Premium | Dedicated |
|---|---|---|---|---|
| **Current status** | Older path | Default serverless recommendation | Advanced serverless | App Service family |
| **Billing model** | Execution-based pay-per-use | Execution-based pay-per-use, plus Always Ready capacity if enabled | Instance time and provisioned capacity | App Service Plan SKU |
| **Cost at zero traffic** | 0 | 0 if Always Ready stays at 0 | Minimum instance cost remains | Always billed |
| **Cold starts** | Present | Reduced when needed via Always Ready | Usually avoidable | Effectively absent when always running |
| **OS** | Windows-first; Linux Consumption availability varies by region | Linux only | Windows / Linux | Windows / Linux |
| **VNet integration** | No | Yes | Yes | Yes |
| **Max instances** | Roughly 200; lower in some OS and platform cases | Up to 1000, subject to regional 250-core default quota | Roughly 20-100+, depending on OS, region, and restrictions | Defined by App Service Plan SKU and autoscale rules |
| **Event-driven autoscale** | Yes (event-driven) | Yes (per-function, target-based) | Yes (target-based optional) | Manual via App Service autoscale rules |
| **Per-function scaling** | No | Yes | No | No |
| **Instance memory** | Fixed at 1.5 GB | 512 / 2048 / 4096 MB | Varies by SKU | Depends on App Service Plan SKU |
| **Deployment slots** | Limited | No; use the rolling update path | Yes | Yes |
| **Warmup trigger** | No | Yes | Yes | Yes |

> Sources: Microsoft Learn — [Function scale and hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale), [Flex Consumption plan](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan), [Event-driven scaling](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling), and [Target-based scaling](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling). Instance ceilings vary by plan, OS, region, and platform restrictions.

When you read the table, the three columns that eliminate options fastest are usually **OS, VNet, and scale behavior**. Cost often comes after those constraints, not before.

---

## Consumption — still the simplest, but no longer the default starting point

Consumption is still easy to explain. No traffic means no bill, and the setup path is simple. The problem is that it is no longer the default answer for a new serverless app.

**Pick it when:**

- You need the simplest demo, experiment, or PoC path
- You have Windows-specific constraints
- You do not need VNet integration
- Some first-request latency is acceptable

**Weaknesses:**

- Cold starts
- No VNet integration
- Fixed 1.5 GB memory
- Long-term migration risk if Microsoft guidance continues shifting away from this plan
- Linux Consumption availability varies by region, making it a less stable target for new architecture decisions

That is why the deployment chapter included Consumption only as a reference path for those with specific constraints. For a new production design, start with Flex unless a concrete requirement points elsewhere.

---

## Flex Consumption — the default candidate for new serverless apps

Flex Consumption is the plan Microsoft now recommends for new serverless workloads. It keeps the economic shape of serverless while removing several of the platform limits that used to push teams toward Premium.

**Key differentiators:**

- **VNet integration** for private resources
- **Selectable memory sizes** at 512 MB, 2048 MB, and 4096 MB
- **Always Ready** for keeping chosen function groups warm; the default is still 0
- **Per-function scaling** instead of scaling the whole app as one unit
- **Large scale range** up to 1000 instances per app, though regional core quota can become the real limit earlier

**Important caveats:**

- It is **Linux only**.
- **Blob trigger support requires the Event Grid source.** Do not assume the same polling-based blob trigger behavior you may be used to on classic Consumption.
- **Some bindings and platform features have Flex-specific constraints.** No deployment slots and no in-place migration from another hosting plan are examples.
- **Per-function scaling still uses scale groups.** HTTP triggers scale together, Blob Event Grid triggers scale together, and Durable Functions scale together. It is not “every function always gets fully isolated scale behavior.”

**Pick it when:**

- You are starting a new serverless project
- You need to reach resources inside a VNet
- You want better scaling flexibility than classic Consumption
- Linux is acceptable

This is the first candidate for a new build. The safe mental model is “Flex fixes many of Consumption's practical limits,” not “Flex removes every meaningful constraint.”

---

## Premium — when cold-start control and Windows support both matter

Premium solves the problem by keeping baseline capacity ready. You pay for that baseline, but you gain much stronger control over startup latency.

**Pick it when:**

- First-request latency is a business problem
- You need Windows and VNet at the same time
- You need larger CPU or memory SKUs
- You want to place multiple Function Apps on the same Premium plan

**Weaknesses:**

- Minimum instance cost remains even at zero traffic
- New Linux workloads almost always deserve a Flex comparison first
- The effective max instance count varies enough by OS, region, and networking constraints that “it scales to 100” is too blunt to rely on

Premium is less about pure serverless billing and more about keeping the Functions operating model while buying stronger performance guarantees.

---

## Dedicated — Functions with App Service operating rules

Dedicated is easier to understand if you ignore the label and look at the behavior. It is **Functions running on top of a regular App Service Plan**. That means you can colocate it with other web apps and budget it like App Service.

**Pick it when:**

- You already have an App Service Plan with spare capacity
- You want Functions on the same infrastructure as other web apps
- You want predictable fixed-plan billing
- Event-driven autoscale is not a requirement

**The defining trade-off:**

- **You do not get Consumption/Flex/Premium-style event-driven autoscale.** Scaling is manual or driven by App Service autoscale rules that you define yourself.

Teams often choose Dedicated on instinct and then discover that queues do not automatically fan out the way they expected. Dedicated uses the Functions programming model, but operationally it behaves much more like App Service.

---

## Decision tree

![Hosting plan choice by requirements](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/05/05-02-decision-tree.en.png)

*Hosting plan choice by requirements*
Dedicated sits outside the main path on purpose. It is not a bad plan. It is a plan for cases where you can **explicitly give up event-driven platform scaling**.

---

## Recommendation for new projects

The short version is straightforward.

1. **For a new serverless app, start with Flex Consumption.** That is the current official direction.
2. **If you need Windows or tighter cold-start control, evaluate Premium.**
3. **Use Consumption only for the simplest demo path or for existing assets you are intentionally keeping.**

One more qualifier matters. Flex Consumption is strong, but **Blob triggers require the Event Grid source, some bindings and features have Flex-specific constraints, and scaling behavior should be understood in terms of per-function scale groups.** The accurate message is not “always use Flex.” It is “Flex is the default candidate, then validate the plan-specific constraints.”

---

## Where this leads operationally

Once the plan is chosen, the next question follows naturally: **how do instances actually scale, and why is the first call slower?** The scaling chapter walks through event-driven scaling, target-based scaling, and cold starts in one model.

---

## Series context

The deployment chapter showed the path end to end; this chapter decides what hosting target that deployment should land on. The scaling chapter picks up from here and explains how those plan choices turn into real scaling behavior and cold-start trade-offs.

---

## Plan change example

```bash
az functionapp plan create \
  --resource-group $RG --name $PLAN \
  --location koreacentral \
  --sku EP1 --is-linux
```

## Operational checklist

- [ ] Documented the billing unit for each plan in a single table
- [ ] Agreed that cold-start tolerance is the first plan-decision criterion
- [ ] Folded platform-feature requirements (VNet, etc.) into the comparison
- [ ] Compared per-plan scale ceilings against your workload peak
- [ ] Simulated monthly cost across realistic scenarios

## In this series

- [What Is Azure Functions? — A World Where Events Call Your Code](./01-what-is-azure-functions.md)
- [Triggers and Bindings — Everything About Function I/O](./02-triggers-and-bindings.md)
- [Host and Worker — Who Actually Runs Your Functions?](./03-host-and-worker.md)
- [Deploy a Function App — From Localhost to Azure](./04-first-deploy.md)
- **Which Plan Should You Pick? — Consumption / Flex / Premium / Dedicated (current)**
- Scaling and Cold Starts — When Serverless Feels Fast and When It Doesn’t (upcoming)
- Monitoring and Operations Fundamentals (upcoming)

---

## References

**Official docs**
- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Function scale and hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Event-driven scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Target-based scaling](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)
- [Azure Functions Premium plan](https://learn.microsoft.com/en-us/azure/azure-functions/functions-premium-plan)
- [Dedicated hosting plans for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan)
- [Migrate from Consumption to Flex Consumption](https://learn.microsoft.com/en-us/azure/azure-functions/migration/migrate-plan-consumption-to-flex)

Tags: Azure, Azure Functions, Serverless, Cloud

---

© 2026 YeongseonBooks. All rights reserved.
