---
title: Monitoring and Operations Fundamentals
series: azure-functions-101
episode: 7
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Azure Functions
- Serverless
- Cloud
last_reviewed: '2026-04-29'
seo_description: Once the app is deployed, the questions change. You stop asking whether
  the function runs at all and start asking why failure rate jumped, why…
---

# Monitoring and Operations Fundamentals

Once the app is deployed, the questions change. You stop asking whether the function runs at all and start asking why failure rate jumped, why instance count climbed, whether the bottleneck is downstream, and where cost is leaking. This chapter covers the screens, metrics, queries, and alert priorities that matter first when you operate Azure Functions.

The scope is practical: the baseline observability view, a small KQL toolkit for incident response, the right signals for instance count and cost, and the first alerts worth wiring up.

---

> 90% of operations is the ability to see 'what is different from baseline' inside 30 seconds.

## Questions this chapter answers

- How do Application Insights and Log Analytics divide responsibilities for Functions ops?
- Which queries actually surface per-function latency, failure rate, and dependency calls?
- When does Live Metrics beat stream logs, and vice versa?
- Which metrics tell you cost is about to spike before the bill does?
- What absolutely must be in the incident runbook?

## Application Insights Is the Starting Point

Most of the operational data you need for Azure Functions ends up in Application Insights. Requests, exceptions, dependency calls, logs, and custom metrics converge there, which makes App Insights integration one of the most important choices you make when standing up a Function App.

```bash
# Simplest way to connect Application Insights after app creation
az monitor app-insights component create \
    --app ai-hello --location koreacentral --resource-group $RG

az functionapp config appsettings set \
    --name $APP --resource-group $RG \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="<your-connection-string>"
```

Once connected, these are the main operational building blocks:

- **Requests** — invocation records
- **Exceptions** — failures thrown inside the function
- **Dependencies** — outbound calls to HTTP, databases, Storage, and other services
- **Traces** — logs written from Python with calls such as `logging.info()`
- **Metrics / customMetrics** — platform metrics, custom metrics, and in some environments additional warm-up related signals

One caveat matters here. Documentation examples often present **Performance Counters = CPU and memory collected automatically**, but that is not universal. Automatic Performance Counters collection is not supported on Linux. Since Flex Consumption is Linux-only, do not assume a Windows-style per-instance CPU/memory view is always available there.

---

## The First Screen to Open During an Incident — Live Metrics

For a live situation, **Application Insights → Live Metrics** is the fastest starting point. It gives you near-real-time visibility into request volume, failure rate, latency movement, and the number of currently active instances.

![Live Metrics signals for early triage](../../../assets/azure-functions-101/07/07-01-the-first-screen-to-open-during-an-incid.en.png)

*Live Metrics signals for early triage*
Live Metrics answers the immediate question: what is happening right now? Just keep the Linux caveat in mind. Instance activity is useful broadly, but infrastructure counters such as CPU and memory depend on OS and environment support.

---

## Five Query and Lookup Patterns Worth Keeping Close

Dashboards help, but incident response usually needs direct queries plus metric lookups. These five patterns cover a large share of day-2 work.

**1) Invocation count and failure rate over the last hour**

```kusto
requests
| where timestamp > ago(1h)
| summarize Total=count(), Failed=countif(success == false) by bin(timestamp, 1m)
| extend FailureRate = round(100.0 * Failed / Total, 2)
| order by timestamp desc
```

**2) Top 10 most frequent exceptions**

```kusto
exceptions
| where timestamp > ago(24h)
| summarize Count=count() by problemId, type
| top 10 by Count
```

**3) Top 10 slowest functions by P95**

```kusto
requests
| where timestamp > ago(24h)
| summarize p95=percentile(duration, 95), Count=count() by name
| top 10 by p95
```

**4) Cold starts are inferred, not measured directly**

Azure Functions does not emit one universal “cold start count” metric you can trust across plans. Using `Host started` traces as a stand-in is too loose for publication-quality guidance because restart, deployment, scale-out, and other host lifecycle events can all produce similar signals.

In practice, operators usually correlate these instead:

- **`InstanceCount`** trends — when the platform added or removed instances
- **`FunctionExecutionUnits`** trends — when actual execution load increased
- **warm-up related signals in App Insights `customMetrics` where available** — Premium and Flex can surface extra warm-up clues in some environments

That gives you a heuristic, not a direct measurement. You can estimate periods where cold starts were likely, but you cannot turn those signals into an exact cold-start counter without losing accuracy.

```bash
az monitor metrics list \
    --resource "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP" \
    --metric "InstanceCount" "FunctionExecutionUnits" \
    --interval PT5M
```

**5) Downstream dependency failures**

```kusto
dependencies
| where timestamp > ago(1h) and success == false
| summarize Count=count() by target, type, resultCode
| order by Count desc
```

---

## Four Alert Priorities Are Enough to Start

With alerts, signal quality matters more than alert volume. These four are a solid baseline.

| Priority | Alert target | Example threshold | Why |
|---|---|---|---|
| P0 | Spike in function failure rate | Failure rate > 5% over 5 minutes | Direct user impact |
| P0 | Spike in response time | P95 is 3× the baseline | Users feel this before a full outage |
| P1 | Approaching the instance ceiling | `InstanceCount` is near the configured limit | The app may stop absorbing more load |
| P2 | Cost spike | Daily invocation count is 5× baseline | Bug, retry storm, or abnormal traffic |

Start with the two P0 alerts if you want the smallest reliable set. Noisy alerts train teams to ignore the whole system.

---

## Where to Check Instance Count

There are two supported answers to “how many instances are active right now?” that operators should reach for first.

1. **The Servers panel in Live Metrics** — the quickest visual answer.
2. **The Azure Monitor `InstanceCount` metric** — the current metric name is **`InstanceCount`**, not `FunctionInstanceCount`. In the portal it appears as *Automatic Scaling Instance Count*.

If you want the app's current site configuration from the CLI, `az functionapp show --name $APP --resource-group $RG --query siteConfig` is the supported operator path. You can combine that with Application Insights and Azure Monitor metrics for the day-to-day scaling view.

You may still see **`/admin/host/scale/status`** mentioned in deep-dive discussions or diagnostics, but treat it as an internal troubleshooting endpoint rather than a stable public surface for normal operations.

---

## Cost Analysis Starts with Trigger-Specific Retry Semantics

When cost rises unexpectedly, the usual suspects are invocation spikes, retry storms, and excessive logging. Queue triggers need special care because retry semantics differ by service.

**Service Bus triggers**

Service Bus uses `maxDeliveryCount` and a dead-letter queue. A repeatedly failing message increments delivery count and is eventually moved aside when it crosses the configured threshold. That is the first safety rail to inspect when the same work appears to be happening over and over.

**Storage Queue triggers**

Storage Queue does not use the same dead-letter terminology or delivery-count model. Messages become visible again with an increasing dequeue count, and after the retry limit they typically move to a **poison queue**. So “queue triggers are protected by maxDeliveryCount and DLQ” is correct for Service Bus, not for Storage Queue.

Two other common cost leaks show up often:

- **Timer frequency is too aggressive** — every 5 seconds multiplies invocations quickly.
- **Logs are too verbose** — large payloads written every invocation increase App Insights ingestion cost.

```bash
# Quickest CLI example to inspect daily invocation count trend
az monitor app-insights events show \
    --app ai-hello --resource-group $RG \
    --type requests --offset 7d
```

Use `--offset` for a relative window such as “the last 7 days.” If you prefer `--start-time`, pass an explicit ISO-8601 timestamp.

---

## A Useful 3am Incident Order of Operations

The first five minutes of an incident usually follow the same pattern.

![First-response checks during an incident](../../../assets/azure-functions-101/07/07-02-a-useful-3am-incident-order-of-operation.en.png)

*First-response checks during an incident*
Failure rate, latency, instance count, and dependency health cover a surprising amount of ground if you check them in that order.

---

## Closing the 101 Series

This chapter closes the Azure Functions 101 series. Taken together, the series moves from the event-driven execution model to triggers and bindings, the host/worker split, plan trade-offs, scaling and cold starts, and finally operations centered on Application Insights. This chapter is the operational layer that turns the earlier mental model into day-2 practice.

If you want to go deeper into the implementation, continue with [Deep Dive — Scaling internals](../../azure-functions-deep-dive/en/05-scaling-internals.md) and [Deep Dive — Cold starts and Placeholder Mode](../../azure-functions-deep-dive/en/06-cold-start-placeholder.md). The 101 series is about making good engineering decisions quickly; the deep-dive series shows how those behaviors are built inside the host.

---

## Operational checklist

- [ ] Added per-function latency and failure-rate charts to the default dashboard
- [ ] Enabled distributed traces on key dependencies (DB, external APIs)
- [ ] Set cost alarms (execution count, GB-s)
- [ ] Specified the first-five-minutes actions in the incident runbook
- [ ] Shared Live Metrics access with the on-call team

<!-- toc:begin -->
## In this series

- [What Is Azure Functions? — A World Where Events Call Your Code](./01-what-is-azure-functions.md)
- [Triggers and Bindings — Everything About Function I/O](./02-triggers-and-bindings.md)
- [Host and Worker — Who Actually Runs Your Functions?](./03-host-and-worker.md)
- [Deploy a Function App — From Localhost to Azure](./04-first-deploy.md)
- [Which Plan Should You Pick? — Consumption / Flex / Premium / Dedicated](./05-choosing-a-plan.md)
- [Scaling and Cold Starts — When Serverless Feels Fast and When It Doesn’t](./06-scaling-and-cold-start.md)
- **Monitoring and Operations Fundamentals (current)**

<!-- toc:end -->

---

## References

**Official Docs**
- [Monitor Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Application Insights overview](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Metrics supported for Microsoft.Web/sites](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-web-sites-metrics)
- [Kusto Query Language reference](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Configure monitoring for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/configure-monitoring)

**Related Series**
- [Azure Functions 101 — Scaling and cold starts](./06-scaling-and-cold-start.md)
- [Azure Functions Deep Dive — Scaling internals](../../azure-functions-deep-dive/en/05-scaling-internals.md)
- [Azure Functions Deep Dive — Cold starts and Placeholder Mode](../../azure-functions-deep-dive/en/06-cold-start-placeholder.md)

Tags: Azure, Azure Functions, Serverless, Cloud
