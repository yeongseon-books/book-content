---
title: Building a Production Guardrail System
series: ai-safety-guardrails-101
episode: 10
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Guardrails
- Production
- Architecture
last_reviewed: '2026-05-03'
seo_description: AI Safety & Guardrails 101 Series (10/10)
---

# Building a Production Guardrail System

> AI Safety & Guardrails 101 Series (10/10)

---
## Section 1

## Wiring Nine Components Into One System

Episodes 1 through 9 covered guardrails as independent components. In production you need a single architecture diagram that shows where each one sits, the order they run in, and what happens when they fail. This capstone builds that architecture.

Goals:

- Decide which guardrail belongs at each boundary: input, model, tool call, output.
- Make fail-open versus fail-closed policies explicit.
- Keep guardrail cost inside a performance budget.
- Track every block and pass on a single observability surface.

## Four-Layer Architecture

Guardrails live in four positions in an LLM system.

| Layer | When it runs | Guardrails |
| --- | --- | --- |
| Pre-input | Right after the user request arrives | rate limit, jailbreak detection, prompt injection normalization |
| Pre-prompt | Right before the model call | PII masking, context sanitization, system prompt verification |
| Post-output | Right after the model response | moderation, hallucination grounding, PII re-check |
| Audit | All stages | append-only log, decision rationale, cost tracking |

Each layer must be able to fail independently; one layer's failure cannot block the others.

## Pipeline Implementation

A simplified version of the four-layer pipeline. In production each function is replaced by the modules from Episodes 1 through 9.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class GuardrailResult:
    allowed: bool
    stage: str
    reason: str | None = None
    metadata: dict | None = None

class GuardrailPipeline:
    def __init__(self, audit_sink: Callable):
        self.audit = audit_sink

    def run(self, request: dict) -> dict:
        ctx = {"request_id": request["request_id"], "user_id": request["user_id"]}

        # Pre-input
        for check in [self.rate_limit, self.detect_jailbreak, self.sanitize_input]:
            res = check(request)
            self.audit({**ctx, "stage": res.stage, "allowed": res.allowed, "reason": res.reason})
            if not res.allowed:
                return self._block(res)

        # Pre-prompt
        masked_prompt, pii_meta = self.mask_pii(request["prompt"])
        retrieved = self.retrieve(masked_prompt)
        sanitized_chunks = self.sanitize_context(retrieved)

        # Model call
        response = self.call_model(masked_prompt, sanitized_chunks)

        # Post-output
        for check in [self.moderate_output, self.verify_grounding, self.recheck_pii]:
            res = check(response, sanitized_chunks)
            self.audit({**ctx, "stage": res.stage, "allowed": res.allowed, "reason": res.reason})
            if not res.allowed:
                return self._block(res)

        final = self.unmask_pii(response, pii_meta)
        self.audit({**ctx, "stage": "delivered", "allowed": True})
        return {"answer": final}

    def _block(self, res: GuardrailResult) -> dict:
        return {"answer": "We can't process that request.", "blocked": True, "stage": res.stage}
```

The key is that audit records every stage, allowed or blocked, so you can reconstruct any decision later.

## Fail-Open vs Fail-Closed

What happens when a guardrail itself errors? Decide policy in advance.

| Scenario | Recommended policy | Reason |
| --- | --- | --- |
| Rate limiter Redis down | fail-open + alert | Brief over-spend risk less than blocking all users |
| Moderation API down | fail-closed | Risk of harmful content escaping |
| PII masking failure | fail-closed | GDPR violation risk |
| Grounding check timeout | partial-deliver with warning | Drop the verification badge but ship the answer |
| Audit log failure | fail-closed in production, fail-open in dev | Missed audit means compliance violation |

Mark each guardrail with an explicit `on_error` policy.

```python
def safe_call(check_fn, request, on_error="closed"):
    try:
        return check_fn(request)
    except Exception as e:
        log_guardrail_error(check_fn.__name__, e)
        if on_error == "open":
            return GuardrailResult(allowed=True, stage=check_fn.__name__, reason="degraded")
        return GuardrailResult(allowed=False, stage=check_fn.__name__, reason="error")
```

## Performance Budget

Running every guardrail serially adds large latency. Control cost with these patterns.

1. **Parallelize independent checks**: bundle non-dependent checks (PII masking and jailbreak detection) with `asyncio.gather`.
2. **Order serial checks by cost**: regex (<1 ms), embedding (<50 ms), LLM judge (<800 ms). Block early to skip expensive layers.
3. **Cache by input hash**: PII masking and grounding results commonly use a 5-minute TTL.
4. **Sample expensive checks**: do not run full grounding on every request; sample a fraction as a regression signal.

Example target: P95 guardrail overhead under 300 ms, excluding the model call.

## Observability

Always show on the dashboard:

| Group | Metric |
| --- | --- |
| Traffic | RPS, input and output tokens per minute, dollars per minute |
| Blocking | Per-category block rate, false positive rate |
| Latency | Per-stage P50 and P95 |
| Trust | Hallucination flag rate, grounding fail rate |
| Cost | Cumulative dollars per model and per user |
| Security | Jailbreak detection rate, PII discovery rate |

Split Slack alerts into two streams.

- **Page**: SLO violations (P95 > 500 ms for 5 minutes, sudden block-rate spike, audit log failure).
- **Daily digest**: suspected false positives, new jailbreak patterns, drift signals.

## Regression Set in CI

Code review alone cannot keep guardrails safe. Run a regression suite per PR.

```python
def run_regression():
    suites = {
        "jailbreak_attacks": load_jailbreak_set(),
        "benign_prompts": load_benign_set(),
        "pii_examples": load_pii_set(),
        "moderation_cases": load_moderation_set(),
        "rag_grounding": load_rag_set(),
    }
    return {name: evaluate_pipeline(pipeline, cases) for name, cases in suites.items()}
```

In GitHub Actions, block merges if any of the following regress.

- Jailbreak recall < 0.95
- Benign false positive > 1%
- PII recall < 0.98
- Grounding precision < 0.85

## Gradual Rollout

Never enable a guardrail change for 100 percent of traffic in one step.

1. **Shadow mode (1 week)**: log results in audit only; do not actually block. Watch metrics.
2. **5 percent canary (3 days)**: enable on 5 percent of traffic. Watch per-stage block rate and user complaints.
3. **50 percent rollout (3 days)**: expand if no SLO violations.
4. **100 percent**: full coverage. Monitor the dashboard intensely for one week.

If something looks wrong, roll back through the same feature flag immediately.

## Human Procedures

Some risk does not yield to technical guardrails alone.

- **On-call**: 24/7 staffing for guardrail alerts.
- **Red team review**: quarterly simulation of new jailbreak patterns.
- **Compliance review**: quarterly sampling of audit logs.
- **Complaint handling**: first reply to a false-positive report within 24 hours.

## Common Mistakes

1. **Running every guardrail serially.** Latency explodes. Parallelize and order by cost.
2. **No explicit failure policy.** Behavior diverges per incident, escalating outages. Pin `on_error` policy on every check.
3. **Treating audit as optional.** Without rationale you cannot answer regulators. Audit is a first-class component.
4. **Shipping without a regression set.** A one-line threshold change can blow up false positives. Gate merges on the regression suite.
5. **Flipping to 100 percent at once.** Skip shadow and canary, and a single bug hits every user. Always step through the rollout phases.

## Key Takeaways

- Split guardrails across pre-input, pre-prompt, post-output, and audit layers so each boundary owns a clear responsibility.
- Predefine fail-open or fail-closed per check to keep behavior consistent during incidents.
- Hold P95 guardrail overhead under 300 ms with parallelization, cost ordering, caching, and sampling.
- Wire a regression suite into CI and gate merges on jailbreak recall, PII recall, grounding precision, and similar SLOs.
- Combine technical layers with on-call, red team, and compliance reviews, and roll changes out shadow → canary → full.
## References

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Google - Responsible AI practices](https://ai.google/responsibility/responsible-ai-practices/)
- [Anthropic - Responsible Scaling Policy](https://www.anthropic.com/news/anthropics-responsible-scaling-policy)
