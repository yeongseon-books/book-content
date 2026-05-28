---
series: sre-101
episode: 6
title: "SRE 101 (6/10): Incident Response"
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
  - Incident
  - Response
  - OnCall
  - Operations
seo_description: A beginner-friendly guide to incident response covering definitions, severity levels, roles, communications, and closure procedures
last_reviewed: '2026-05-14'
---

# SRE 101 (6/10): Incident Response

When an outage starts, the technical problem is only half the problem. The other half is human coordination: who decides priorities, who works the fix, who updates customers, and who keeps the timeline coherent enough for later learning.

Teams that decide those things during the outage usually lose time in confusion. Teams that decide them beforehand recover faster because the response structure is already available when stress is highest.

This is the 6th post in the SRE 101 series. Here we treat incident response as a team system with roles, severity levels, communication rules, and explicit closure criteria.


![sre 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/06/06-01-concept-at-a-glance.en.png)
*sre 101 chapter 6 flow overview*

## Questions to Keep in Mind

- Why does incident response depend so heavily on team structure instead of only on technical skill?
- Why should severity be defined by impact rather than intuition?
- What should an Incident Commander do directly, and what should they deliberately avoid doing?

## Why this topic matters

Chaos magnifies impact. A technically recoverable issue can become a prolonged incident when decisions stall and communication lags behind the actual state of the system.

The response process also shapes trust. Customers, leadership, and the team itself all experience the incident through the quality of updates, coordination, and follow-through. A good response process does not just speed up recovery—it preserves customer trust, creates records, and feeds naturally into the postmortem that follows.

> Incident response is a team activity with fixed roles and a fixed order.

## Key Terms

| Term | Meaning | Role in practice |
| --- | --- | --- |
| incident | An abnormal state with real user impact | Distinguishes events that require a coordinated response |
| severity | The magnitude of impact | Sets response intensity and participation scope |
| IC | Incident Commander | Coordinates priorities and decisions |
| ops lead | The person leading recovery work | Organizes and executes technical actions |
| comms lead | The person handling internal/external updates | Protects the trust axis with customers and the organization |

## Why role separation comes first

When an outage hits, the person with the most technical knowledge naturally dominates the conversation. But deep technical skill does not automatically translate to coordination skill. That is why response frameworks separate roles.

The Incident Commander does not solve every problem personally. They decide what matters most right now, assign tasks to the right people, and keep the response moving forward. Meanwhile ops leads and subject-matter experts focus on the actual fix. This separation prevents decision-making from blocking execution and vice versa.

## Severity classification

Severity defined subjectively leads to inconsistency—one person calls 1,000 affected users a major incident while another only escalates when the issue persists for an hour. Written criteria fix this.

| Severity | Impact criteria | Response time | Escalation | Example |
| --- | --- | --- | --- | --- |
| SEV1 | Full service down or core functionality completely broken | Immediate (< 5 min) | All on-call + leadership | Payment API total outage, DB cluster down |
| SEV2 | Major feature severely degraded, many users affected | < 15 min | Related team on-call | Home feed latency > 5 s, login failure rate 20 % |
| SEV3 | Non-core feature issue, some users affected | < 1 hour | Owning team only | Profile image upload slow, notification delay |
| SEV4 | No feature impact, internal monitoring issue | Next business day | Assigned owner checks | Dashboard display error, log collection delay |

Each severity level has a clear response-time expectation. This removes guesswork about whom to call and how fast to move. Without these criteria, over-response and under-response alternate unpredictably.

## Hands-on: Defining the Process

### Step 1 — Severity mapping

```python
def severity(impact_users, duration_min):
    if impact_users > 10000 or duration_min > 60:
        return "SEV1"
    if impact_users > 1000:
        return "SEV2"
    return "SEV3"
```

Severity should be determined by impact criteria—affected user count, duration, whether a core revenue function is down—not by how stressed the reporter feels.

### Step 2 — Assign IC

```python
def assign_ic(on_call):
    return on_call[0]
```

The IC creates a single coordination axis during response. They listen to everyone but do not delay the next decision waiting for consensus. Consensus-seeking during outages extends downtime.

### Step 3 — Create the channel

```python
def channel(name):
    return f"#inc-{name}"
```

A dedicated channel preserves the record and concentrates response communication in one place. When response conversations are scattered across DMs and verbal exchanges, recovery may finish but learning is lost.

### Step 4 — Status updates

```python
def update(channel, msg, every_min=15):
    return {"channel": channel, "msg": msg, "every": every_min}
```

Even when the root cause is unknown, regular updates are needed. Communicating current impact, workarounds, and the next update time preserves trust. Silence makes things worse.

### Step 5 — Closure check

```python
def can_close(mitigated, customer_impact_zero):
    return mitigated and customer_impact_zero
```

"Fixed" and "closeable" are not always the same. A workaround may be in place but customer impact may linger, or handoff to another timezone may be needed.

## Incident timeline writing

The timeline is the most important artifact from incident response. Recording who saw what, when, and what actions followed means the postmortem does not depend on fading memories.

### What every timeline entry must include

| Field | Description | Example |
| --- | --- | --- |
| Time | Minute-level timestamp (HH:MM) | 14:32 |
| Event | What happened | Redis cluster primary OOM killed |
| Action | Who did what | @alice ran failover command |
| Result | What changed after the action | Replica promoted, latency normalized |
| Link | Related log/metric/screenshot | [Grafana link] |

### Timeline example

```
14:12 - Redis cluster primary node OOM killed
14:13 - Home feed latency alert fires (p99 > 5 s)
14:15 - @bob designated as IC, #inc-0519-redis channel created
14:18 - @alice checks Redis memory usage: 99% reached
14:20 - @bob approves failover command
14:22 - Replica promotion complete, cluster healthy
14:25 - Some requests confirmed serving via DB fallback path
14:30 - Home feed p99 latency recovered below 800 ms
14:37 - @bob declares incident closed
```

This timeline enables fact-based answers during the postmortem: "Why was recovery delayed?" and "Which action actually helped?" become answerable without memory arguments.

## PagerDuty webhook handler example

Automating the initial response—creating a Slack channel, assigning the IC, posting the first update—removes minutes of setup time that compound during every incident.

```python
from fastapi import FastAPI, Request
import requests
import json
from datetime import datetime

app = FastAPI()

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
SLACK_TOKEN = "xoxb-your-slack-bot-token"
ON_CALL_SCHEDULE = ["alice", "bob", "charlie"]

def create_incident_channel(incident_id: str) -> str:
    """Create a dedicated Slack channel for the incident."""
    channel_name = f"inc-{datetime.now().strftime('%m%d')}-{incident_id}"
    
    response = requests.post(
        "https://slack.com/api/conversations.create",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"name": channel_name, "is_private": False}
    )
    
    if response.json().get("ok"):
        return channel_name
    return None

def assign_ic() -> str:
    """Assign the current on-call person as IC."""
    hour = datetime.now().hour
    index = (hour // 8) % len(ON_CALL_SCHEDULE)
    return ON_CALL_SCHEDULE[index]

def post_initial_update(channel: str, incident_id: str,
                        summary: str, severity: str):
    """Send the initial status update."""
    ic = assign_ic()
    message = (
        f":rotating_light: **Incident {incident_id} - {severity}**\n\n"
        f"**Summary:** {summary}\n"
        f"**Time:** {datetime.now().strftime('%H:%M')}\n"
        f"**IC:** @{ic}\n"
        f"**Channel:** #{channel}\n\n"
        f"**Next steps:**\n"
        f"1. Confirm current blast radius\n"
        f"2. Evaluate workaround options\n"
        f"3. Status update in 15 minutes\n"
    )
    
    requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message, "channel": f"#{channel}"}
    )

@app.post("/webhook/pagerduty")
async def pagerduty_webhook(request: Request):
    """
    Receive PagerDuty webhook and start automated response.
    
    On incident.triggered:
    1. Create dedicated Slack channel
    2. Auto-assign IC
    3. Post initial status update
    """
    payload = await request.json()
    
    for message in payload.get("messages", []):
        event = message.get("event")
        
        if event == "incident.triggered":
            incident = message.get("incident", {})
            incident_id = incident.get("id")
            summary = incident.get("summary")
            urgency = incident.get("urgency", "high")
            
            severity = "SEV1" if urgency == "high" else "SEV2"
            channel = create_incident_channel(incident_id)
            
            if channel:
                post_initial_update(channel, incident_id,
                                    summary, severity)
                return {
                    "status": "success",
                    "channel": channel,
                    "ic": assign_ic(),
                    "severity": severity
                }
    
    return {"status": "ignored"}
```

This automation eliminates the manual overhead of channel creation, role assignment, and first notification—allowing the team to start technical work immediately.

## IC role: responsibilities and boundaries

The Incident Commander is the center of response but not the person who fixes everything.

**What the IC does:**

- Assesses the situation and sets priorities
- Assigns roles (ops lead, comms lead, specialists)
- Maintains the timeline and checks progress
- Makes escalation decisions (more people, leadership notification)
- Confirms closure criteria are met and declares resolution

**What the IC must not do:**

- Debug code directly
- SSH into servers and run commands
- Manually analyze log files
- Perform multiple technical tasks simultaneously

The IC is a coordinator, not an executor. Technical decisions belong to the ops lead and specialists. The IC judges how those decisions fit the overall response flow.

## Blameless culture and incident response

Blamelessness is not just good culture—it directly affects response quality. In blame-heavy organizations, people hide facts or frame explanations defensively. That obscures the real cause and lets the same failure repeat.

A blameless environment enables:

- Honest explanation of why information was incomplete during the incident
- Disclosure of warning signs that were dismissed and why
- Admission that procedures were unclear or tools were lacking
- Focus on system design gaps rather than individual judgment errors

### Blameless vs. blame-oriented questions

| Blame-oriented | Blameless alternative |
| --- | --- |
| Why didn't you check the backup? | Was the backup verification procedure documented? |
| Why did you miss the alert? | Was the alert firing frequently enough to cause fatigue? |
| Why didn't you roll back faster? | Was the rollback button easy to find and reach? |
| Why didn't you predict this failure? | What signals existed before the failure that we could detect next time? |

Same facts, different direction. Blameless questions produce answers that improve systems and procedures.

## Communication templates

Consistent formatting during incidents saves time and prevents omissions.

**Initial notification:**

```
[Incident] {service_name}
- Start time: {HH:MM}
- Blast radius: {all users / partial functionality}
- Symptom: {brief description}
- Current action: {recovery in progress}
- Next update: {in 15 minutes}
```

**Progress update:**

```
[Update] {service_name}
- Current time: {HH:MM}
- Root cause: {investigating / identified}
- Recovery status: {workaround applied / fix in progress}
- Impact: {still ongoing / partially mitigated}
- Next update: {in 15 minutes}
```

**Resolution notification:**

```
[Resolved] {service_name}
- Recovery time: {HH:MM}
- Total duration: {N minutes}
- Cause: {brief summary}
- Follow-up: {postmortem scheduled for DATE}
```

Having these templates ready before an incident removes the communication burden during high-stress moments.

## Postmortem preparation

When response ends, transition to the postmortem immediately while details are fresh.

| Item | Source | How it's used in the postmortem |
| --- | --- | --- |
| Timeline | Slack channel message timestamps | Reconstructs event sequence |
| Blast radius | Monitoring dashboard numbers | Quantifies severity and business impact |
| Action log | Commands executed, deploy logs | Documents recovery steps and workarounds |
| Communications | Notification text, update timestamps | Evaluates quality of customer communication |

The dedicated channel's conversation history is effectively the first draft of the postmortem. Delaying documentation means relying on memory, which loses detail.

## What to Notice in This Code

- Severity is defined by impact criteria, not subjective feel.
- The IC is the single coordination axis—not the single doer.
- A separate channel preserves the record and focuses communication.
- Closure criteria must be explicit; otherwise incidents stay ambiguously open.

## Five Common Mistakes

1. **Delaying decisions by consensus instead of using an IC.** Consensus-seeking extends downtime.
2. **Estimating impact subjectively.** Written criteria eliminate inconsistency.
3. **Skipping customer communication until the fix is done.** Users prefer honest unknowns over silence.
4. **Vague closure criteria.** Dashboard numbers stabilizing briefly does not mean user impact is gone.
5. **Returning to work without a record.** No timeline means no postmortem, which means no learning.

## How This Shows Up in Production

PagerDuty triggers create Slack channels and assign the IC automatically. Statuspage updates go out at fixed intervals using templates. Postmortem documents are pre-populated from the incident channel timeline. Weekly incident review meetings track mean time to detect (MTTD) and mean time to recover (MTTR) as team KPIs.

## How a Senior Engineer Thinks

- Response gets faster with *training*, not with heroics during the outage.
- The IC decides; experts execute. This separation prevents both from being blocked.
- Communication is the axis of trust—silence during an incident destroys credibility faster than the outage itself.
- Closure is done carefully because premature "all clear" followed by recurrence is worse than staying in incident mode a bit longer.
- Preparation happens before the call. The best time to build the playbook is when there is no fire.

## Checklist

- [ ] Severity defined with numeric impact criteria and response-time expectations.
- [ ] IC, ops lead, and comms lead roles documented and practiced.
- [ ] Dedicated channel and regular update cadence established.
- [ ] Closure criteria and handoff rules documented.
- [ ] Incident records feed directly into postmortem process.

## Practice Problems

1. Describe the IC role in one sentence, focusing on what they do *not* do.
2. Give an example of a SEV2 incident and explain why it is not SEV1.
3. Explain why regular status updates are needed even when root cause is unknown.

## Wrap-up and Next Steps

Next, we cover *postmortems*—how to turn incident records into systemic improvements that prevent the same failure from recurring.

## Answering the Opening Questions

- **Why is incident response driven more by team structure than individual skill?**
  When roles are separated, the IC focuses on coordination, the ops lead on recovery, and the comms lead on announcements. Eliminating role conflicts enables faster response.
- **Why must severity be defined by impact criteria, not gut feeling?**
  Defining severity by affected user count, duration, and whether core functionality is down lets anyone reach a similar judgment. Response intensity and escalation scope then follow consistently.
- **What should an Incident Commander do directly, and what should they not?**
  The IC handles priority decisions, role assignment, timeline recording, escalation, and closure declaration. Technical work—code debugging, server access, log analysis—goes to the ops lead and subject-matter experts.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- **Incident Response (current)**
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)
- [Incident Response - PagerDuty](https://response.pagerduty.com/)
- [Incident Command System](https://en.wikipedia.org/wiki/Incident_Command_System)
- [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook)

Tags: SRE, Incident, Response, OnCall, Operations
