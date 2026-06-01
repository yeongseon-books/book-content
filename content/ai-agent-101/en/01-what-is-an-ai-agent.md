---
title: "AI Agent 101 (1/10): What Is an AI Agent?"
series: ai-agent-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- LLM
- Tool Use
- Autonomy
- ReAct
- Automation
last_reviewed: '2026-05-03'
seo_description: A chatbot is a dictionary that gives you an answer. An Agent is an
  intern you hand a task to and walk away from.
---

# AI Agent 101 (1/10): What Is an AI Agent?

When most people first encounter LLMs, they frame them as systems that answer questions well. That mental model feels sufficient in a chat window, but it starts to break the moment you ask the model to finish real work on your behalf.

Classifying customer tickets, creating follow-up tasks, and drafting replies all require more than polished text generation. The model has to interact with external systems, inspect results, and decide what to do next, which is exactly where the line between a chatbot and an Agent becomes useful.

This is the first post in the AI Agent 101 series. Here we build the basic mental model for Agents by separating them from chatbots and walking through the observe → think → act → check loop.

![Agent loop at a glance](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/01/01-01-agent-loop-at-a-glance.en.png)
*Agent loop at a glance*
> An agent starts not with a smarter style of prose, but with a control loop that keeps executing toward a goal.

## Questions to Keep in Mind

- What changes when you separate chatbots and agents by execution responsibility instead of product labels?
- How does the Observe → Think → Act → Check loop help you locate agent failures?
- Which boundary should be defined before choosing tools for a first agent?

## What you will learn

- The essential difference between a chatbot like ChatGPT and an AI Agent
- The core observe → think → act → check loop and why it matters
- A four-question test for deciding whether your use case actually needs an Agent
- A pen-and-paper exercise that mimics an Agent without any framework

## Why it matters

When people first meet LLMs, they usually frame them as "models that answer questions." The ChatGPT chat box becomes a stand-in for the entire field. That mental model breaks the moment you push LLMs into production.

> "Triage 1,000 customer tickets, route each to the right team, and draft a reply for every one."

This sentence is impossible for a chatbot. The model has to call external systems, observe the results, decide what to do next, and retry on failure. That is exactly where chatbots end and Agents begin. Understanding Agents expands LLMs from "conversation partners" to "automatable workers."

## Mental Model

> A chatbot is a dictionary that gives you an answer. An Agent is an intern you hand a task to and walk away from.

A dictionary opens, hands you a definition, and closes. An intern is different. They do not know the answer up front. They look around (observe), decide what to try (think), do something (act), and check whether the result is good (check). If not, they try again. That loop is the essence of an Agent.

## Concept 1 - Chatbot vs Agent

| | Chatbot | Agent |
|---|---|---|
| Input | User message | Goal |
| Output | Text reply | Task done or artifact produced |
| External interaction | None | Tool calls, file/API access |
| Iteration | One turn | N turns until goal is met |
| State | Conversation history | Task state plus memory |

Technically, an Agent is also "an LLM call" under the hood. The difference is whether **a human reads the LLM output, or a system consumes it and triggers the next action**.

## Concept 2 - The Observe → Think → Act → Check loop

Every Agent action is a repetition of this four-step loop.

```text
goal: "Tell me whether I need an umbrella in Tokyo today"

[loop 1]
  observe: known info = (only the goal)
  think:   "I need today's weather; call the weather API"
  act:     get_weather(city="Tokyo")
  check:   result = {temp: 18, condition: "rain"}

[loop 2]
  observe: rain is forecast
  think:   "Rain means yes, an umbrella is needed"
  act:     final_answer("Yes, rain is forecast in Tokyo today")
  check:   goal achieved → stop
```

This loop, implemented as repeated LLM calls, is the ReAct (Reason + Act) pattern, and almost every Agent framework is a variation on it.

## Before / After

**Before (chatbot style)**

```python
response = llm.chat("What's the weather in Tokyo?")
# → "I'm sorry, I don't have access to real-time information."
```

**After (Agent style)**

```python
goal = "Tell me whether I need an umbrella in Tokyo today"
agent = Agent(tools=[get_weather], llm=llm)
result = agent.run(goal)
# → "Yes, rain is forecast in Tokyo today (18°C, rain)"
```

The single key difference is `tools=[get_weather]`. Once the Agent knows a tool exists, the LLM decides on its own when to invoke it.

## Step-by-step exercise - faking an Agent by hand

You can grasp how Agents work without any framework. Two small Python pieces are enough.

### Step 1. Define a tool

```python
def get_weather(city: str) -> dict:
    # In production this calls a real API. Mock here.
    fake = {"Tokyo": {"temp": 18, "condition": "rain"},
            "Seoul": {"temp": 22, "condition": "clear"}}
    return fake.get(city, {"error": "unknown city"})
```

### Step 2. Run one loop manually

You play the role of the LLM.

```python
goal = "Tell me whether I need an umbrella in Tokyo today"

# observe
context = {"goal": goal, "history": []}

# think (you decide)
next_action = ("get_weather", {"city": "Tokyo"})

# act
result = get_weather(**next_action[1])
context["history"].append((next_action, result))

# check
print(context)
# {'goal': '...', 'history': [(('get_weather', {'city': 'Tokyo'}),
#                              {'temp': 18, 'condition': 'rain'})]}
```

### Step 3. Hand `think` to an LLM

Hand the current context to an LLM and ask it to reply with the next tool to call as JSON. That is the simplest possible Agent. The next episode covers the actual ReAct prompt.

## Common Mistakes

### Mistake 1. Assuming "smarter LLMs will answer in one shot"

The essence of Agents is not model size but **interaction with external systems**. Even GPT-5 does not know real-time weather without a weather API. There is no such thing as a tool-free Agent.

### Mistake 2. Using Agents for everything

Summarization, translation, and simple Q&A are fine on a chatbot. Agents make 5-20x more LLM calls, which inflates cost and latency. Without external action, there is no reason to pay the Agent tax.

### Mistake 3. Skipping result verification

A common bug is an Agent that proceeds as if a failed API call had succeeded, because the LLM "felt" the call worked. Make the check step explicit and define retry or fallback paths on failure.

### Mistake 4. Ignoring infinite loops

A confused LLM will call the same tool forever. Always cap maximum steps (for example 10) and force-stop on overflow.

### Mistake 5. Letting context grow unbounded

Every loop appends to history, which lands in the prompt, which blows up tokens. You need memory compression, summarization, or a sliding window (covered in Ep5).

## How practitioners think about this

Before adopting Agents in production, ask these questions.

- **Do you need external action?** If not, a chatbot or RAG is enough.
- **Do you need multi-step reasoning?** Search → compare → conclude is where Agents shine.
- **Can you absorb the failure modes?** Agents fail more ways than chatbots. High-stakes flows like financial transactions require human-in-the-loop.
- **Does the cost pencil out?** Expect 5-15 LLM calls per task, so your unit economics shift significantly.

Two or more "yes" answers means it is time to seriously evaluate Agents.

---

## Practical design reinforcement

### Fix the execution contract in a document first

Before writing any agent code, pin down the execution contract as a document. The contract does not need to be elaborate. Four elements matter: goal schema, allowed tools, stop conditions, and human-approval triggers. When these four are agreed on paper first, prompt and code align in the same direction.

```json
{
  "goal_schema": {
    "task": "string",
    "constraints": ["string"],
    "deadline": "ISO-8601"
  },
  "allowed_tools": ["search_docs", "lookup_ticket", "send_report"],
  "stop_conditions": ["goal_achieved", "max_steps_exceeded", "safety_violation"],
  "human_approval": {
    "required_for": ["external_write", "billing_action"],
    "channel": "slack:#ops-approval"
  }
}
```

With this contract in place, you can verify whether the system follows the right execution path before worrying about whether the model gives good answers. In production, that ordering matters. Prompt quality improves iteratively, but if the execution contract is ambiguous, failure logs themselves become uninterpretable.

### Minimum log fields for a working agent

Fixing a per-step log schema like the one below connects evaluation and operations from the start.

```python
from pydantic import BaseModel

class StepLog(BaseModel):
    run_id: str
    step: int
    thought_summary: str
    tool_name: str | None = None
    tool_args: dict | None = None
    tool_latency_ms: int | None = None
    observation_digest: str | None = None
    stop_reason: str | None = None
```

Two design choices worth noting. First, store `thought_summary` instead of the full thought text. This reduces the risk of logging PII or sensitive policy content while keeping enough signal for debugging. Second, making `tool_latency_ms` a required field lets you separate quality problems from performance problems during incident triage.

### OpenAI Responses API loop example

```python
from openai import OpenAI
import json

client = OpenAI()

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Look up today's weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        },
        "required": ["city"],
        "additionalProperties": False
    }
}]

def run(goal: str) -> str:
    messages = [{"role": "user", "content": goal}]
    for _ in range(6):
        res = client.responses.create(
            model="gpt-4.1-mini", input=messages, tools=tools
        )
        item = res.output[0]
        if item.type == "message":
            return item.content[0].text
        if item.type == "function_call" and item.name == "get_weather":
            args = json.loads(item.arguments)
            obs = {"city": args["city"], "condition": "rain", "temp": 18}
            messages.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(obs),
            })
    return "max_steps_exceeded"
```

This code is a minimal educational example, but production agents benefit from keeping the same shape. When the loop cap, tool schema, and call-result injection point are all explicit, reproducible failure analysis becomes possible.

---

## Deep operations notes

### Failure classification template

In production, you do not close a failure with "the model got it wrong." Splitting failures along multiple axes makes improvement priorities clear.

| Failure axis | Diagnostic question | Example |
|---|---|---|
| Planning failure | Did the agent decompose the goal incorrectly? | Unnecessary 6-step repetition |
| Execution failure | Did a tool call fail? | timeout, 429, schema mismatch |
| Verification failure | Did the agent accept a bad observation? | Adopted incorrect tool output |
| Policy failure | Did the agent cross a safety boundary? | Attempted to send sensitive data externally |

Pin this table in the team runbook so on-call engineers classify incidents with the same vocabulary.

### Prompt and tool version pinning

Teams that struggle with change tracking usually manage prompts and tool schemas separately from code releases. Stable teams embed version fields in the request context:

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-en-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

Version fields alone accelerate regression analysis significantly. When quality degrades at a specific point in time, you can immediately narrow whether it was a model change, a prompt change, or a tool change.

### Observability event example

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

Adopting structured logs first keeps migration cost low when you later move to OpenTelemetry, ELK, or Grafana.

### Deployment checklist

- Verify model API keys are separated into environment variables and a Secret Manager.
- Confirm `max_steps`, `timeout_ms`, and `retry_budget` defaults match the production profile.
- Check that fallback response messages do not give users false confidence during outages.
- Keep alert thresholds (`error_rate`, `p95_latency`, `policy_violation_rate`) identical in documentation and code.

These items get less attention than feature work, but they directly reduce incident frequency.

### Cost control points

| Parameter | Purpose | Recommended default |
|---|---|---|
| max_steps | Maximum loops per execution | 4-8 |
| max_tool_calls | Tool call cap | 3-6 |
| input_token_budget | Input token budget | Service-specific policy |
| output_token_budget | Output token budget | Service-specific policy |

Cost control is not a post-optimization add-on. Fixing execution budgets from the start keeps the service stable when traffic spikes.

### CI quality gates

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

Automating minimum quality gates in the deployment pipeline prevents "accidentally good-looking builds" from reaching production.

## Checklist

- [ ] I can state the chatbot vs Agent difference in one sentence
- [ ] I can draw the observe → think → act → check loop
- [ ] I can apply the four-question test to my use case
- [ ] I understand the infinite-loop and context-bloat risks

## Practice

1. Classify each task as "needs Agent" or "chatbot is enough":
   - "Summarize today's meeting notes"
   - "Triage GitHub issues by label and assign owners"
   - "Review this Python code"
   - "Reply 'ack' to every Slack message that mentioned me today"
2. Add a `send_email` tool alongside `get_weather`. Invent one new use case the Agent now enables.

## Summary

- An AI Agent is an LLM-driven system that takes a goal and repeats the observe → think → act → check loop until done.
- The difference from a chatbot is external tool use plus multi-turn autonomous decisions.
- Agents are not always the answer; their value peaks when external action and multi-step judgment combine.
- Infinite loops, context bloat, and tool failures are the first risks to design for.
- Drawing the loop by hand once shows that every Agent framework is the same shape.

## Next

The next episode covers **context engineering** - the discipline of deciding what enters and what leaves the prompt, which determines Agent decision quality.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Can state the chatbot vs agent distinction in one sentence.
- [ ] Walked through one full Observe→Think→Act→Check loop by hand.
- [ ] Can rate an agent's autonomy on a simple scale.
- [ ] Wrote down what this series covers and what it does not.

<!-- a-grade-example:end -->

## Answering the Opening Questions

- **What changes when you separate chatbots and agents by execution responsibility instead of product labels?**
  - A chatbot usually produces a reply for a human to read. An agent owns the path to completion, so the design unit becomes the execution loop, not the final sentence.
- **How does the Observe → Think → Act → Check loop help you locate agent failures?**
  - The loop lets you separate missing observation, bad reasoning, failed action, and absent checking instead of blaming the whole agent at once.
- **Which boundary should be defined before choosing tools for a first agent?**
  - Define the goal, allowed actions, stop condition, and human-intervention boundary first. Tools are execution mechanisms inside that boundary.

<!-- toc:begin -->
## In this series

- **AI Agent 101 (1/10): What Is an AI Agent? (current)**
- AI Agent 101 (2/10): Context Engineering (upcoming)
- AI Agent 101 (3/10): Tool Use Fundamentals (upcoming)
- AI Agent 101 (4/10): Agent Workflow Design (upcoming)
- AI Agent 101 (5/10): Memory and State (upcoming)
- AI Agent 101 (6/10): Multi-Agent Systems (upcoming)
- AI Agent 101 (7/10): Agent Evaluation (upcoming)
- AI Agent 101 (8/10): Error Handling and Reliability (upcoming)
- AI Agent 101 (9/10): Production Operations (upcoming)
- AI Agent 101 (10/10): Building Your First Agent (upcoming)

<!-- toc:end -->

---

## References

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain Agents - conceptual guide](https://python.langchain.com/docs/concepts/agents/)
- [OpenAI - Function calling guide](https://platform.openai.com/docs/guides/function-calling)

Tags: AI Agent, LLM, Tool Use, Python
