---
title: "AI Evaluation 101 (7/10): Evaluating Agents — Trajectories, Not Single Responses"
series: ai-evaluation-101
episode: 7
language: en
status: content-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- Agent
- Trajectory
- Tool Use
last_reviewed: '2026-05-14'
seo_description: Agents reach answers through multiple steps. You need to evaluate
  not just the final response but 'which tools, in what order, how many times.' This…
---

# AI Evaluation 101 (7/10): Evaluating Agents — Trajectories, Not Single Responses

Agents reach answers through multiple steps. You need to evaluate not just the final response but 'which tools, in what order, how many times.'

This is post 7 in the AI Evaluation 101 series. Here we cover trajectory-level evaluation.

## Questions to Keep in Mind

- Why should agent evaluation inspect trajectory along with the single final response?
- What operational risk is caught by tool selection, step count, and recovery metrics?
- Which step-level signals belong on an agent evaluation dashboard?

## Big Picture

![Evaluating agents - Trajectories, not single responses](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/07/07-01-evaluating-agents-trajectories-not-singl.en.png)

*Evaluating agents - Trajectories, not single responses*

This picture shows agent evaluation looking at trajectory, tool choice, step efficiency, and recovery rather than only the final response. The execution path itself must be evaluated because it creates product cost and risk.

> Agent evaluation becomes operational only when it evaluates the path as well as the answer.

## Why Agent Evaluation Is Different

![Why agent evaluation is different](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/07/07-02-why-agent-evaluation-is-different.en.png)

*Why agent evaluation is different*
Through Ep1-Ep6 we evaluated **single responses**: one question paired with one answer.

Agents are different. An agent goes through multiple steps to complete a task.

```text
User: "Email me a summary of this week's schedule"
  ↓
Step 1: read_calendar()  → [10 meetings]
Step 2: read_emails()    → [3 emails]
Step 3: summarize(...)   → "This week's summary: ..."
Step 4: send_email(...)  → "sent"
  ↓
Final reply: "Done, I sent the email."
```

Agent evaluation **cannot stop at the final reply**. You must measure five things together:

1. **Task success** — did the user get what they wanted
2. **Tool selection** — was the right tool called
3. **Tool arguments** — were the arguments correct
4. **Trajectory efficiency** — did it take the shortest path
5. **Recovery** — did it bounce back from failures along the way

Let's go through each.

---

## Two Levels of Evaluation — End-to-End vs Step-Level

![Two levels of evaluation - End-to-End vs Step-Level](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/07/07-03-two-levels-of-evaluation-end-to-end-vs-s.en.png)

*Two levels of evaluation - End-to-End vs Step-Level*
Agent evaluation has two perspectives.

### End-to-end (final outcome)

Look only at the result. "Was the email actually sent?"

```python
# agent_eval/end_to_end.py
def end_to_end_success(agent_run: dict) -> bool:
    return agent_run["final_state"]["email_sent"] is True
```

**Pro**: Simple. Maps to user value directly.
**Con**: When it fails, you do not know **where** it broke.

### Step-level

For each step, check whether the agent **called the right tool with the right arguments**.

```python
# agent_eval/step_level.py
expected_trajectory = [
    {"tool": "read_calendar", "args_match": lambda a: "week" in a.get("range", "")},
    {"tool": "read_emails",   "args_match": lambda a: a.get("limit", 0) <= 10},
    {"tool": "summarize",     "args_match": lambda a: True},
    {"tool": "send_email",    "args_match": lambda a: "@" in a.get("to", "")},
]

def step_match_score(actual: list[dict], expected: list[dict]) -> float:
    matches = 0
    for i, exp in enumerate(expected):
        if i >= len(actual):
            break
        a = actual[i]
        if a["tool"] == exp["tool"] and exp["args_match"](a["args"]):
            matches += 1
    return matches / len(expected)
```

**Pro**: Pinpoints which step broke.
**Con**: Multiple valid trajectories exist; strict matching gives false negatives.

**Practical recommendation**: use end-to-end for the headline number, drop into step-level only for failure analysis.

---

## Tool Selection — Confusion Matrix

![Tool selection - confusion matrix](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/07/07-04-tool-selection-confusion-matrix.en.png)

*Tool selection - confusion matrix*
Agents pick the wrong tool more often than you would think — calling `draft_email` instead of `send_email`. Treat tool selection as a classification problem.

```python
# agent_eval/tool_confusion.py
from sklearn.metrics import classification_report

# 100 test cases
expected_tools = ["send_email", "read_calendar", "send_email", ...]
actual_tools   = ["draft_email","read_calendar", "send_email", ...]

print(classification_report(expected_tools, actual_tools))
#                precision  recall  f1-score
# read_calendar      0.95    0.98    0.96
# send_email         0.85    0.70    0.77   ← often confused with draft_email
# draft_email        0.60    0.90    0.72
```

**Reading**: send_email recall of 0.70 means 30% of cases the agent called draft instead. **Add an explicit example to the prompt**: "Use send, not draft."

---

## Trajectory Efficiency — Step Count

![Trajectory efficiency - step count](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/07/07-05-trajectory-efficiency-step-count.en.png)

*Trajectory efficiency - step count*
An agent that finishes in 4 steps is not the same as one that finishes in 12. Twelve steps means 3x tokens, 3x latency, and 3x failure surface.

```python
# agent_eval/efficiency.py
def trajectory_metrics(agent_run: dict, expected_steps: int) -> dict:
    actual_steps = len(agent_run["steps"])
    return {
        "step_count":      actual_steps,
        "step_overhead":   actual_steps / expected_steps,  # 1.0 = optimal
        "total_latency_s": sum(s["latency_s"] for s in agent_run["steps"]),
        "total_tokens":    sum(s["tokens"] for s in agent_run["steps"]),
        "tool_calls":      sum(1 for s in agent_run["steps"] if "tool" in s),
    }

overheads = [trajectory_metrics(r, 4)["step_overhead"] for r in runs]
print(f"avg step overhead: {sum(overheads)/len(overheads):.2f}")
# avg step overhead: 1.8  ← agent uses ~2x more steps than needed
```

**Rule of thumb**: step overhead above 2.0 means the prompt or tool design needs rework.

---

## Recovery — Does the Agent Bounce Back

Production agents hit tool failures (API rate limits, network errors). The question is whether the agent **retries or finds an alternative path**.

```python
# agent_eval/recovery.py
def evaluate_recovery(agent_run: dict) -> str:
    steps = agent_run["steps"]
    for i, s in enumerate(steps):
        if s.get("tool_result", {}).get("error"):
            if i + 1 >= len(steps):
                return "GAVE_UP"
            next_step = steps[i + 1]
            if next_step.get("tool") == s["tool"]:
                return "RETRIED"
            if "tool" in next_step:
                return "ALTERNATIVE"
            return "GAVE_UP"
    return "NO_FAILURE"

# 50 runs with injected failures
results = [evaluate_recovery(r) for r in fault_injected_runs]
from collections import Counter
print(Counter(results))
# Counter({'RETRIED': 30, 'ALTERNATIVE': 12, 'GAVE_UP': 8})
# → 16% of cases the agent gave up. Reinforce recovery in the prompt.
```

**Fault injection pattern**: deliberately inject errors into a subset of tool calls during evaluation and see how the agent reacts (automated as a regression test in Ep8).

---

## Putting It Together — An Agent Eval Dashboard

Five metrics in one dashboard tells the full story.

```python
# agent_eval/dashboard.py
import pandas as pd

results = []
for run in agent_runs:  # 100 runs
    results.append({
        "task_success":    end_to_end_success(run),
        "tool_f1":         step_match_score(run["steps"], expected),
        "step_overhead":   trajectory_metrics(run, 4)["step_overhead"],
        "recovered":       evaluate_recovery(run) in ("RETRIED", "ALTERNATIVE"),
    })

df = pd.DataFrame(results)
print(df.describe())
#                  task_success  tool_f1  step_overhead  recovered
# mean             0.78          0.85     1.6            0.72
# std              0.41          0.18     0.7            0.45
```

**Reading**:
- task_success 0.78 → 22% failure. Too high.
- tool_f1 0.85 → tool selection is OK.
- step_overhead 1.6 → 60% extra steps. Cost issue.
- recovered 0.72 → 28% caves on failures. Needs work.

---

## Common Mistakes

### Mistake 1: Evaluating only the final answer

If you only check whether the email was sent, an agent that sent five wrong emails before the sixth correct one still gets a PASS. **Always include trajectory metrics.**

### Mistake 2: Allowing only one expected trajectory

Multiple paths can solve the same task. "send_email first" or "summarize first" should both be acceptable if the outcome matches. **Define expected as a set or partial order.**

### Mistake 3: Step-level passing without end-to-end check

Every step can pass while the final outcome is wrong (bad argument combinations). **Always pair with end-to-end success.**

### Mistake 4: Skipping recovery evaluation

API failures are constant in production. Without recovery testing you ship into a flood of user-facing errors. **Inject failures into 30% of runs** and measure.

### Mistake 5: Ignoring token cost and latency

The same task solved in 1K tokens vs 10K tokens looks identical on accuracy but the latter is unfit for production. **Put step_overhead, total_tokens, and total_latency_s on the dashboard.**

---

## Key Takeaways

- Agent evaluation is not single-response evaluation. Measure **task success and trajectory together**.
- Five metrics: task success, tool selection, tool arguments, trajectory efficiency, recovery.
- Use end-to-end for the headline number and step-level for failure analysis.
- Tool selection → `classification_report`. Recovery → fault injection.
- Token cost and latency are production metrics on equal footing with accuracy.

The next post integrates evaluation into **CI** so regressions are blocked automatically.

---

## Operational checklist

- [ ] Track task success and trajectory metrics together, not as separate projects.
- [ ] Measure tool confusion so prompt and tool-schema fixes are evidence-based.
- [ ] Watch step overhead, token cost, and latency on the same dashboard as success rate.
- [ ] Inject failures deliberately to confirm the agent retries or finds an alternative path.
- [ ] Allow multiple valid trajectories when the task can be solved in different orders.

## Answering the Opening Questions

- **Why should agent evaluation inspect trajectory along with the single final response?**
  - An agent can reach a correct-looking answer through the wrong path, or spend too much cost and risk to get a correct answer.
- **What operational risk is caught by tool selection, step count, and recovery metrics?**
  - Tool selection catches wrong tools, step count catches inefficiency and loops, and recovery measures whether the agent can recover after failure.
- **Which step-level signals belong on an agent evaluation dashboard?**
  - The dashboard should include step list, tool calls, arguments, errors, retries, cost, latency, and final success by request.
<!-- toc:begin -->
## In this series

- [AI Evaluation 101 (1/10): Why Evaluate LLM Applications](./01-why-evaluate-llm-apps.md)
- [AI Evaluation 101 (2/10): Designing Evaluation Datasets](./02-evaluation-dataset-design.md)
- [AI Evaluation 101 (3/10): Deterministic Metrics — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- [AI Evaluation 101 (4/10): LLM-as-Judge — Evaluating Models with Models](./04-llm-as-judge.md)
- [AI Evaluation 101 (5/10): Designing Rubric-Based Scoring](./05-rubric-based-scoring.md)
- [AI Evaluation 101 (6/10): Evaluating RAG Systems](./06-rag-evaluation.md)
- **AI Evaluation 101 (7/10): Evaluating Agents — Trajectories, Not Single Responses (current)**
- AI Evaluation 101 (8/10): Regression Testing — Don't Let Yesterday's Wins Break Today (upcoming)
- AI Evaluation 101 (9/10): A/B Testing LLMs — Which Prompt Is Better? (upcoming)
- AI Evaluation 101 (10/10): Continuous Evaluation in Production (upcoming)

<!-- toc:end -->

## References

### Official docs

- [LangSmith — Agent evaluation tutorial](https://docs.smith.langchain.com/evaluation/tutorials/agents)
- [OpenAI — Built-in tools guide](https://platform.openai.com/docs/guides/tools)
- [scikit-learn — classification_report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html)

### Papers and background

- [Yao et al. (2022). ReAct — Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [AgentBench — Evaluating LLMs as Agents (Liu et al., 2023)](https://arxiv.org/abs/2308.03688)

Tags: AI Evaluation, Agent, Trajectory, Tool Use
