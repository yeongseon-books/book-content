---
series: sre-101
episode: 1
title: "SRE 101 (1/10): What is SRE?"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SRE
  - Reliability
  - DevOps
  - Operations
  - Engineering
seo_description: A beginner-friendly overview of Site Reliability Engineering, its origin, how it differs from DevOps, the core activities, and where to start
last_reviewed: '2026-05-14'
---

# SRE 101 (1/10): What is SRE?

Teams usually meet reliability through pain first: midnight pages, releases that suddenly feel dangerous, and a few people carrying too much operational knowledge in their heads. When that happens, adding more effort or more meetings rarely fixes the underlying problem.

SRE starts by changing the frame. Instead of treating operations as heroics, it treats reliability as an engineering system with measurable goals, automation, feedback loops, and explicit trade-offs.

This is the first post in the SRE 101 series. It sets up the mental model for the rest of the series: reliability is part of the product, and operating it well requires code, metrics, and deliberate policies.


![sre 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/01/01-01-concept-at-a-glance.en.png)
*sre 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What does SRE actually mean beyond "the people who handle incidents"?
- How is SRE different from DevOps even though the two ideas often overlap?
- Why does SRE treat reliability work as a software problem instead of a staffing problem?

## Why this topic matters

You can ship features quickly, but if the service keeps going down customers leave. Reliability is part of the product, not a clean-up task after the product ships.

Teams that ignore this usually become dependent on memory, heroics, and manual recovery. Teams that adopt the SRE frame turn those same problems into measurable indicators, automation work, and explicit operating rules. Over time the two cultures diverge completely: one scales with people, the other scales with code.

## Key Terms

| Term | Meaning | Why it matters in practice |
| --- | --- | --- |
| SRE | An engineering approach that treats operations as a software problem | Replaces gut-feel operations with metrics and code |
| reliability | The fraction of time the system behaves as expected | Sets the floor for user-perceived quality |
| SLO | A service-level objective the team agrees on internally | Becomes the reference point between speed and stability |
| error budget | The allowed amount of failure derived from the SLO | Tells the team how much risk it can still take |
| toil | Repetitive, automatable manual work | Reveals operational debt eating human time |
| postmortem | A structured learning document written after an incident | Prevents the team from starting at zero next time |

## The core perspective

If you see SRE only as a job title, confusion is inevitable. It looks like on-call people who handle alerts and stare at dashboards. That description does not explain why some SRE teams are perpetually exhausted while others run larger systems with the same headcount.

A more practical explanation: **SRE treats operations as a software problem.** Repeated responses become automation. Reliability gets a numeric definition. Post-incident learning connects to system changes. If a structure requires humans to keep working harder just to maintain the status quo, SRE considers it an improvement target.

This framing also clarifies the relationship with DevOps. DevOps emphasizes collaboration culture between development and operations. SRE concretizes that collaboration into measurable targets and operational policies. They are complementary rather than competing: SRE often turns DevOps goals into specific operating rules.

## How SRE differs from traditional operations

In traditional operations, experienced engineers respond to incidents using personal knowledge. When the same problem recurs, the team adds a checklist line or updates a runbook. This works at small scale but creates steep people-dependency as services grow.

SRE does not accept recurring work as "just how things are." It asks: why does this call repeat? Which metric should we check first? Can this procedure become code? Is the target realistic? The center of gravity moves from heroic response to reproducible systems.

The difference shows up after incidents too. Traditional ops culture closes the ticket once recovery finishes. SRE culture treats the follow-up—what to change so the same failure is smaller next time—as part of the job.

## Signals that an organization needs SRE

- **Incidents repeat.** The same root cause recurs every few weeks. Response docs exist but never lead to structural fixes.
- **Overtime grows.** Deploys and incident response overflow regular hours. On-call engineers get paged on weekends and vacations. Hiring more people does not reduce the load.
- **Deploys feel risky.** Every release raises tension. Friday deploys are banned. Checklists exist but nobody knows whether they actually reduce risk.

When these signals appear, SRE proposes: instead of adding more staff, automate repetitive work, set measurable reliability targets, and connect post-incident learning to system changes.

## SRE vs DevOps vs Sysadmin

| Dimension | SRE | DevOps | Sysadmin |
| --- | --- | --- | --- |
| **Focus** | Measurement, automation, error budgets | CI/CD, fast feedback loops | Server, network, backup stability |
| **Tools** | Prometheus, Grafana, PagerDuty | Jenkins, GitHub Actions, Terraform | Ansible, Nagios, Bash |
| **Success metric** | SLO achievement, toil reduction, MTTR | Deploy frequency, lead time | Uptime, backup success rate |

In practice many organizations don't separate these into distinct teams. One team applies both SRE and DevOps perspectives: SRE emphasizes measurement-driven decisions while DevOps emphasizes flow speed across the value stream. They complement each other.

## Google's five SRE principles

1. **Treat operations as a software problem.** Repetitive manual work is an automation candidate. Operational procedures should be expressible as code.
2. **Define reliability via SLOs.** Instead of vague stability, set measurable targets that the whole team shares. SLOs become the reference between shipping speed and stability.
3. **Manage risk with error budgets.** Rather than eliminating failure entirely, declare how much failure is acceptable and move faster within that envelope.
4. **Reduce toil.** Toil is repetitive, automatable, and produces no lasting value. If more than 50% of SRE time goes to toil, the organization must prioritize improvement.
5. **Learn through postmortems.** Incidents are learning opportunities, not blame targets. Focus on what system changes prevent recurrence.

## Hands-on: Your First SLO

### Step 1 — Pick the indicator

```python
# Example: HTTP success ratio
indicator = "http_2xx / http_total"
```

SRE starts with measurement. A good indicator reflects customer experience rather than internal server state. CPU can spike without users noticing, but a drop in success ratio hits them immediately.

### Step 2 — Set the target

```python
slo = {"indicator": indicator, "target": 0.999, "window": "30d"}
```

An indicator without a target allows observation but not judgment. Targets need both a number and a time window: "99.9% over 30 days" is actionable; "99.9%" alone is not.

### Step 3 — Measure

```python
def availability(success, total):
    return success / total
```

Simple but crucial: reliability must be a computable value, not a feeling. When the team looks at the same number, arguments decrease and priorities become clear.

### Step 4 — Error budget

```python
def error_budget(target, total):
    return (1 - target) * total
```

Once you have a target, the allowed failure range calculates itself. SRE does not promise zero failure—it declares how much failure the team will tolerate and uses that headroom deliberately.

### Step 5 — Use it for decisions

```python
def can_release(spent, budget):
    return spent < budget
```

This is where SRE becomes an operating system rather than a document. If budget remains, experiment faster. If budget is burning quickly, prioritize stabilization. Numbers must drive behavior.

## Key metrics to measure first

### Availability

```
availability = successful_requests / total_requests
```

99.9% availability allows ~43 minutes of downtime per month. 99.99% allows ~4.3 minutes. That gap changes infrastructure investment, deploy strategy, rollback speed, and detection time.

### Latency

Average latency is misleading. Most requests may be fast while a tail of requests is painfully slow. Use percentiles:

```
p50 — median experience
p95 — most users
p99 — worst-case users notice
```

A large gap between p50 and p99 signals tail-latency problems—often caused by database locks, cache misses, or garbage collection under specific conditions.

### Error rate

```
error_rate = failed_requests / total_requests
```

Ratio matters more than absolute count. Traffic growth raises absolute errors even if the system is healthy. If the ratio stays stable, the system is likely fine.

### Toil percentage

```python
def toil_percentage(toil_hours, total_hours):
    return toil_hours / total_hours * 100

# Example: 18 hours of toil in a 40-hour week
print(f"Toil: {toil_percentage(18, 40):.0f}%")  # 45%
```

Track this weekly. The highest-time repetitive tasks become automation candidates first.

## Before-and-after scenario

```
BEFORE SRE (Payments team, 5 engineers):
  Monthly incidents: 3–4
  MTTR: 45 min
  Deploy frequency: 1/week (no Fridays)
  Night pages: 8–10/month
  Repetitive tasks: cert renewal, log cleanup, manual scaling

AFTER SRE (same team, 6 months later):
  Monthly incidents: 1–2
  MTTR: 15 min
  Deploy frequency: 3–4/week (canary deploys)
  Night pages: 2–3/month
  Automated: cert renewal, log archiving, auto-scaling
```

| Metric | Before | After | Change |
| --- | --- | --- | --- |
| MTTR | 45 min | 15 min | −67% |
| Monthly incidents | 3–4 | 1–2 | −50% |
| Deploy frequency | 1/week | 3–4/week | +3–4× |
| Night pages | 8–10/month | 2–3/month | −70% |
| Toil ratio | 55% | 30% | −25pp |

The key: the team did not grow. Measurement and automation let the same five engineers cover a larger surface area reliably.

## A typical SRE week

| Activity | Share | Description |
| --- | --- | --- |
| Project engineering | 50% | Automation, tooling, system improvements |
| On-call response | 15% | Alert handling, incident response |
| Code / design review | 15% | Reliability feedback on changes |
| Capacity planning | 10% | Growth forecasting, resource planning |
| Learning / postmortems | 10% | Incident analysis, tech research |

If toil exceeds 50%, that is a signal to invest in automation—not to hire more people. SRE time belongs to making systems better, not to repeating manual steps.

## What to Notice in This Code

- SRE begins with choosing an indicator, but only becomes meaningful when target and action rules follow.
- Indicators closer to customer experience simplify team conversation.
- Error budget is not a device to justify failure—it is a device to make risk tolerance explicit.
- Numbers let speed and stability live in the same conversation.

## Five Common Mistakes

1. **Setting 100% availability as the goal.** Impossible to achieve and inflates cost without proportional customer benefit.
2. **Mistaking a technical metric for a customer metric.** CPU load is not an SLI; request success rate is.
3. **Treating SLOs as a document, not a tool.** If the SLO does not change release or alert behavior, it is decoration.
4. **Doing operations manually when repetition is obvious.** Toil that persists is structural debt.
5. **Running SRE in isolation from development.** SRE without product-team alignment cannot enforce error-budget policies.

## Common early mistakes when adopting SRE

**Trying to SLO everything at once.** Internal APIs and rarely-used paths do not need SLOs on day one. Start with the single most critical user journey.

**Setting targets too high.** 99.99% allows only 4.3 minutes of downtime per month. Unrealistic targets demoralize the team and turn SLOs into paperwork.

**Writing the SLO and stopping there.** If the number does not trigger concrete actions (enhanced review at 50%, freeze at 100%), it remains a report nobody reads.

## How a Senior Engineer Thinks

A senior engineer does not see SRE as more ops work—they see it as reducing the ops work that requires humans. When pages increase, the question is not "who do we hire?" but "why are these pages happening and which parts can become code?"

Reliability is also not an infrastructure-only concern. How a product feature reaches users is itself a reliability question. Strong teams have product and platform engineers referencing the same SLO when making trade-offs.

## Checklist

- [ ] One key SLO defined for the most critical user path.
- [ ] Error budget computed and connected to release decisions.
- [ ] Toil ratio measured weekly.
- [ ] At least one automation candidate identified from repetitive work.
- [ ] Team agrees that post-incident learning needs a structured process.

## Practice Problems

1. Your service handles 10 million requests per month with an SLO of 99.9%. How many failed requests does the error budget allow?
2. A team's toil ratio is 60%. Name two structural changes (not hiring) that could bring it below 50%.
3. Explain in one sentence why 100% availability is not a good SLO target.

## Wrap-up and Next Steps

SRE is not about working harder at operations. It is about treating operations as a measurable, automatable engineering problem. With this perspective, SLO, error budget, monitoring, incident response, postmortem, and toil reduction connect into a single operating system rather than scattered concepts.

Next, we look at *reliability* more concretely—what dimensions it has and how to measure each one.

## Answering the Opening Questions

- **SRE isn't just another name for the operations team—what does it actually mean?**
  SRE distinguishes operational boundaries (input → validation → signal) and defines what to measure and decide at each boundary. It's a discipline that applies software engineering practices to operations problems.
- **Why are SRE and DevOps frequently mentioned together but not synonymous?**
  DevOps emphasizes collaboration culture; SRE concretizes that collaboration into measurable targets and automation. The step-by-step SLO construction in this article reveals exactly this difference.
- **What practical difference does treating reliability as a product feature make?**
  The core is using error budget—calculated failure headroom—as the reference point for both release velocity and stabilization work, placing two seemingly unrelated activities within the same decision framework.

<!-- toc:begin -->
## In this series

- **What is SRE? (current)**
- Reliability (upcoming)
- SLI, SLO, SLA (upcoming)
- Error Budget (upcoming)
- Monitoring (upcoming)
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)
- [What is SRE - Google Cloud](https://cloud.google.com/architecture/devops)
- [Site Reliability Engineering - Wikipedia](https://en.wikipedia.org/wiki/Site_reliability_engineering)

Tags: SRE, Reliability, DevOps, Operations, Engineering
