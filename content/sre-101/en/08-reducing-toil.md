---
series: sre-101
episode: 8
title: "SRE 101 (8/10): Reducing Toil"
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
  - Toil
  - Automation
  - Productivity
  - Operations
seo_description: A beginner-friendly guide to reducing toil covering definitions, measurement, automation priorities, savings strategies, and tech-debt connections
last_reviewed: '2026-05-14'
---

# SRE 101 (8/10): Reducing Toil

Teams can be very busy and still spend too much of their time on work that should not stay manual. The danger is that repetitive recovery, repeated validation, and copied communication all start to look normal simply because the service still runs.

In SRE the term for this kind of work is *toil*. Reducing toil is not about comfort—it is about reclaiming engineer time for work that compounds: safer releases, better observability, and structural fixes that prevent next week's pages.

This is the 8th post in the SRE 101 series. Here we define toil in operational terms, measure its cost, rank automation candidates, calculate break-even, and connect toil to operational debt.


![sre 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/08/08-01-concept-at-a-glance.en.png)
*sre 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What separates toil from valuable operational work that still takes time?
- How can a team measure how much capacity is disappearing into repetitive work?
- Which automation candidates should move first if time is limited?

## Why this topic matters

When toil becomes a large share of the week, improvement stops. The team is still working hard, but more of that effort goes into keeping the current system upright rather than making the next week better.

Toil is also invisible debt. The service appears to run fine, but underneath it relies on night calls, manual recovery, and repeated checks performed by humans. That structure hits a wall as scale grows.

## Key Terms

| Term | Meaning | Why it matters in practice |
| --- | --- | --- |
| toil | Repetitive, automatable manual work | Silently erodes team productivity over time |
| runbook | A written procedure a human follows step by step | May be a stepping stone toward full automation |
| automation | Code that performs the procedure | Removes human involvement and speeds execution |
| toil ratio | Fraction of team hours consumed by toil | Makes team health visible as a number |
| break-even | The point where automation investment pays back its build cost | Decides which automation to fund first |

## Why toil is not the same as hard work

Being busy does not mean a task is toil. Designing a deployment pipeline for the first time or analyzing a novel failure mode takes effort but creates lasting understanding. In contrast, restarting the same service by hand every night is toil.

Three criteria overlap to create toil: **repetitive**, **manual**, and **automatable**. When all three apply, the team pays the same cost week after week with no compounding return. Toil is therefore a structural problem, not a fatigue problem.

## Toil classification criteria

Precisely classifying toil requires explicit criteria. The table below shows five attributes—when all five overlap, the task is high-priority toil.

| Criterion | Description | Toil example | Non-toil example |
| --- | --- | --- | --- |
| Manual | A human must execute it | Restarting a server by hand | An auto-restart script |
| Repetitive | Same procedure runs again and again | Daily manual log collection | One-time incident analysis |
| Automatable | Can be expressed as code | Certificate renewal steps | Designing a new architecture |
| Tactical | Urgent response without root-cause fix | Manual restart on every failure | Health-check with auto-failover design |
| No lasting value | Low contribution to reliability or business | Meaningless report generation | Improving customer-impact monitoring |

A task that meets all five is P0 toil. A task that meets only some is lower priority. Tasks that meet none are engineering work and should stay with humans.

## Without measurement, priorities drift

Teams easily remember the most annoying tasks. But the tasks that burn the most cumulative time are often invisible without logging. Strong teams sort automation discussions by frequency × duration, not by gut frustration.

This framing also keeps automation realistic. Rather than building impressive tooling, eliminating the highest-cost repetitive task first usually delivers more relief.

## The 50-percent toil budget

Google SRE recommends that no team spend more than 50% of its time on toil. The remaining half should go to engineering work—automation, monitoring improvements, and reliability investments.

Why the budget matters:

1. **Scale ceiling** — Toil grows linearly. Double the services, double the toil. Without automation the team never catches up.
2. **Compound returns** — Engineering work compounds. Better monitoring finds failures faster; one automation makes the next automation cheaper.
3. **Skill atrophy** — Teams stuck in toil stop learning new tools and patterns.
4. **Hiring and retention** — High-toil teams struggle to attract strong engineers who want growth, not repetition.

```python
def toil_budget_status(team_hours_per_week, toil_hours):
    """
    Check toil budget health.

    50% rule: more than half of team time on toil triggers action.
    """
    toil_pct = (toil_hours / team_hours_per_week) * 100
    budget_limit = team_hours_per_week * 0.5
    remaining = budget_limit - toil_hours

    status = {
        "toil_hours": toil_hours,
        "toil_pct": toil_pct,
        "budget_limit": budget_limit,
        "remaining_budget": remaining,
        "engineering_hours": team_hours_per_week - toil_hours,
    }

    if toil_pct <= 30:
        status["health"] = "healthy"
    elif toil_pct <= 50:
        status["health"] = "warning"
    else:
        status["health"] = "critical"

    return status


# Example: 5-person team, 40 h/week each = 200 h total
team_hours = 200
toil_hours = 60  # 60 hours/week on toil

result = toil_budget_status(team_hours, toil_hours)
print(f"Toil: {result['toil_hours']}h ({result['toil_pct']:.1f}%)")
print(f"Engineering: {result['engineering_hours']}h")
print(f"Health: {result['health']}")
```

Track this weekly. When the number crosses 50%, automation becomes the top priority—not a nice-to-have.

## Priority matrix — what to automate first

Not every toil task can be automated at once. Sorting by frequency and risk clarifies the queue:

| Frequency \ Risk | High | Medium | Low |
| --- | --- | --- | --- |
| **5+ per week** | Automate now (P0) | This quarter (P1) | Next quarter (P2) |
| **2–4 per week** | This quarter (P1) | Next quarter (P2) | Document, defer (P3) |
| **0–1 per week** | Next quarter (P2) | Document, defer (P3) | Runbook only |

High-frequency + high-risk tasks go first. Low-frequency + low-risk tasks may stay as runbooks indefinitely—and that is fine.

## Hands-on: Measure and Automate Toil

### Step 1 — Log toil time

```python
def log_toil(task, minutes):
    return {"task": task, "minutes": minutes}
```

Before discussing automation, record the data. Which tasks occur, how often, how long each takes—without this the team argues from anecdote.

### Step 2 — Toil ratio

```python
def toil_ratio(toil_min, total_min):
    return toil_min / total_min
```

This single number shows how much improvement capacity the team is losing. The issue is not operations itself, but the share consumed by automatable repetition.

### Step 3 — Score automation candidates

```python
def score(freq_per_week, minutes_each):
    return freq_per_week * minutes_each
```

Multiplying frequency by duration ranks candidates objectively. The most irritating task is not always the most expensive one—scoring reveals the difference.

### Step 4 — Break-even

```python
def break_even(saved_per_week, build_minutes):
    return build_minutes / saved_per_week
```

Automation is not free. The build cost and weekly savings together tell you when the investment pays back. This turns "should we automate?" from a debate into arithmetic.

### Step 5 — Write the automation

```python
def auto_restart(service):
    return f"systemctl restart {service}"
```

The code may look trivial, but the point is clear: moving a repeated human step into a script cuts recovery time and frees attention for harder problems.

## Example: Certificate renewal automation

SSL/TLS certificates that expire cause outages. Manually tracking expiry dates and running renewal commands is classic toil. The script below automates the check-and-renew cycle:

```python
import subprocess
import datetime

def check_cert_expiry(domain: str) -> int:
    """Return days until certificate expires, or -1 on error."""
    cmd = [
        "openssl", "s_client",
        "-connect", f"{domain}:443",
        "-servername", domain,
    ]
    try:
        proc = subprocess.run(cmd, input=b"", capture_output=True, timeout=10)
        for line in proc.stdout.decode().split("\n"):
            if "Not After" in line:
                date_str = line.split(":", 1)[1].strip()
                expiry = datetime.datetime.strptime(
                    date_str, "%b %d %H:%M:%S %Y %Z"
                )
                return (expiry - datetime.datetime.now()).days
    except Exception as e:
        print(f"Error checking {domain}: {e}")
    return -1


def renew_certificate(domain: str) -> bool:
    """Renew via certbot; return True on success."""
    result = subprocess.run(
        ["certbot", "renew", "--cert-name", domain, "--non-interactive"],
        capture_output=True,
        timeout=300,
    )
    return result.returncode == 0
```

Schedule via cron:

```bash
# /etc/cron.d/cert-renewal
0 3 * * * root /usr/local/bin/renew-certs.py >> /var/log/cert-renewal.log 2>&1
```

This runs daily at 03:00, renews certificates expiring within 30 days, and eliminates the calendar-watching toil entirely.

## Example: Auto-rollback on bad deploy

```python
import time
import requests

def check_metrics(api_url, threshold_error=0.05, threshold_latency_ms=3000):
    """Return True if metrics exceed thresholds."""
    data = requests.get(f"{api_url}/metrics").json()
    return (
        data["error_rate"] > threshold_error
        or data["latency_p99_ms"] > threshold_latency_ms
    )

def rollback(service, prev_version):
    return f"kubectl set image deployment/{service} {service}={prev_version}"

# Wait 5 min post-deploy, then check
time.sleep(300)
if check_metrics("http://api.example.com"):
    cmd = rollback("api", "v2.0.5")
    print(f"Rolling back: {cmd}")
else:
    print("Deployment healthy")
```

Without this script, an on-call engineer must watch dashboards for five minutes after every deploy and decide manually whether to roll back. The script converts that toil into a deterministic policy.

## Change Failure Rate (CFR)

CFR measures what fraction of changes result in a rollback or hotfix. It quantifies the quality of your release process:

```python
def change_failure_rate(total_changes, failed_changes):
    """
    CFR = failed / total * 100

    DORA benchmarks:
      Elite: 0-15%   High: 16-30%
      Medium: 31-45% Low: 46%+
    """
    if total_changes == 0:
        return 0
    return (failed_changes / total_changes) * 100

cfr = change_failure_rate(total_changes=80, failed_changes=4)
print(f"CFR: {cfr:.1f}%")  # 5.0% — Elite
```

A high CFR signals insufficient testing, missing canary validation, or bottlenecked rollback paths. Lowering it requires pipeline, test coverage, and monitoring improvements working together.

## What to Notice in This Code

- Measurement is the starting point of prioritization—not automation skill.
- A numeric score sorts candidates so the team agrees on order.
- Break-even turns "should we automate?" into arithmetic, not debate.
- A runbook is not the end state—it is a waypoint toward code.

## Five Common Mistakes

1. **No measurement of toil time.** Without data, priority follows whoever complains loudest.
2. **Automating by gut feel without scoring.** The most annoying task is not always the most expensive one.
3. **Stacking runbooks without converting them to code.** Documentation helps, but if a human still executes the steps weekly, toil remains.
4. **Ignoring automation maintenance cost.** Automation is code—it needs an owner, tests, and a maintenance plan.
5. **Skipping post-launch operational cost.** Automation that breaks silently creates worse toil than the original manual step.

## How a Senior Engineer Thinks

A senior engineer treats toil as operational debt, not mere annoyance. Frequent manual calls mean some part of the system or process has not yet been translated into code.

Night recovery, log collection, cache clearing, notification drafting—these often yield large gains from small automation. Attacking the highest-repetition task first is usually wiser than building an impressive but niche tool.

The 50% line is not arbitrary: below it the team compounds improvements; above it the team treads water.

## Checklist

- [ ] Toil ratio measured and tracked weekly.
- [ ] Automation candidate list scored by frequency × duration.
- [ ] Break-even calculated for top candidates.
- [ ] Each automation script has an owner and maintenance plan.
- [ ] Runbook-to-code migration backlog maintained.

## Practice Problems

1. Define toil in one sentence that distinguishes it from hard-but-valuable ops work.
2. A task takes 20 minutes and occurs 8 times per week. Automation takes 12 hours to build. Calculate break-even in weeks.
3. Your team's toil ratio is 55%. Name two concrete actions to bring it below 50%.

## Wrap-up and Next Steps

Toil is the state where repetitive, automatable manual work continuously burns human time. The key is not just reducing annoyance but measuring time, ranking candidates, and converting investment into compounding savings.

Next, we cover *capacity planning*—how to forecast incoming demand and decide how much headroom to keep.

## Answering the Opening Questions

- **How does toil differ from normal operational work?**
  Toil is "repetitive, manual, automatable, scales linearly with service growth, yet produces no lasting value." Not all ops work is toil—design reviews, incident retrospectives, and system-understanding work aren't classified as toil even if repeated.
- **How do you measure how much team time goes to repetitive manual work?**
  Rather than vague feelings, label on-call tickets, repeated PRs, and manual ops tasks over one or two weeks and sum the hours. Compare against the SRE guideline of "under 50% of engineer time"—some toil isn't worth automating when you see automation cost vs. labor cost together.
- **Which tasks should you automate first for maximum ROI?**
  Prioritize tasks where frequency, time-per-occurrence, and error risk are all high. Without automation the team stays trapped in repetitive work and reliability improvements or feature development time shrinks. Items where "build once, save N hours/week + reduce human error" is clearest go to the automation backlog first.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
- **Reducing Toil (current)**
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Eliminating Toil - Google SRE Book](https://sre.google/sre-book/eliminating-toil/)
- [Identifying and Tracking Toil - Google SRE Workbook](https://sre.google/workbook/eliminating-toil/)
- [Automating Operations - Google SRE Book](https://sre.google/sre-book/automation-at-google/)
- [Toil Reduction - Atlassian](https://www.atlassian.com/incident-management/devops/toil)

Tags: SRE, Toil, Automation, Productivity, Operations
