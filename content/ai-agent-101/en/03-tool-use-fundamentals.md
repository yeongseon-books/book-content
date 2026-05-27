---
title: "AI Agent 101 (3/10): Tool Use Fundamentals"
series: ai-agent-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Tool Use
- Function Calling
- Integration
last_reviewed: '2026-05-27'
seo_description: Agents differ from simple conversational models because they can
  use tools. They can call weather APIs, query databases, read and write files.
---

# AI Agent 101 (3/10): Tool Use Fundamentals

The first thing that makes an agent more than a chatbot is the ability to reach outside itself—calling a weather API, querying a database, reading a file. The moment the model can trigger real code, it shifts from narrator to execution orchestrator.

But tool use is trickier than it looks. Calling a tool does not automatically make the system safe. A vague name causes wrong selection; a weak schema causes malformed arguments; a clumsy result-injection pattern causes unnecessary loops.

This is the 3rd post in the AI Agent 101 series. We cover the basic flow of function calling, schema design as a safety boundary, error handling, and tool selection strategies.

![Tool-calling loop](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/03/03-01-tool-calling-loop.en.png)
*Tool-calling loop*
> Tool use separates model reasoning from code execution and connects them with schemas and validation.

## Questions to Keep in Mind

- Where does the model decision end and application execution begin in function calling?
- How does an ambiguous tool schema make an agent fail?
- What should be validated before tool output is fed back to the model?

## Why This Matters

Tool use is the first interface where an agent system touches the real world. If this boundary is weak, no model improvement stabilizes automation. If this boundary is well-designed, even a modest model can drive a strong automation loop.

Operationally, function calling errors often look like LLM problems but are actually schema design, parameter validation, or result serialization issues. Understanding this topic lets you reduce agent failures to system problems faster.

Later topics—reliability, evaluation, operations—all start here. Metrics like wrong-tool-selection rate, invalid-argument rate, per-tool latency, and fallback-path coverage all require a tool-use layer to measure.

## Core Concept

Function calling is not the model directly invoking an API. The model proposes which tool to call with which arguments; application code performs the actual call. This separation is what creates a responsibility boundary.

Two benefits follow. First, the model decides *what* while code handles *how*—separation of concerns. Second, the application controls validation, authorization, retry, and timeout—safety is enforceable.

> Good tool-use design does not give the model more freedom; it constrains the model's choices to forms that code can safely execute.

## The Four-Step Flow

```python
import openai

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retrieves current weather for a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., Seoul, New York)"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="auto"
)
```

Step 1 shows the model which tools exist. The name, description, and parameter schema are the model's entire interface—weak descriptions cause routing errors; weak types cause argument errors.

```python
# LLM response: a tool-call proposal (nothing executed yet)
{
    "role": "assistant",
    "content": null,
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "Seoul"}'
            }
        }
    ]
}
```

Step 2: the model proposes a call. Crucially, nothing has been executed. The model only requested; the system now owns validation and execution.

```python
import json

def execute_tool(tool_name: str, arguments: str) -> str:
    params = json.loads(arguments)
    if tool_name == "get_weather":
        weather_data = get_weather_api(params["location"])
        return json.dumps(weather_data)
    return json.dumps({"error": "Unknown tool"})

tool_call = response.choices[0].message.tool_calls[0]
result = execute_tool(tool_call.function.name, tool_call.function.arguments)
```

Step 3: application code executes the tool. In production this function grows thick—parsing, validation, auth checks, timeouts, retries all live here.

```python
messages = [
    {"role": "user", "content": "What's the weather in Seoul?"},
    response.choices[0].message,
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
    }
]

final_response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=messages
)
print(final_response.choices[0].message.content)
# "The current weather in Seoul is sunny with a temperature of 15°C."
```

Step 4: feed the result back for a final answer. A broken `tool_call_id` link destabilizes multi-tool turns; an overly verbose result burns context budget fast.

### The Agent Loop

Single tool calls are rarely enough. Search, refine, summarize—multi-step is the norm. Wrapping the flow in a loop makes it an agent:

```python
from typing import Dict, Any, List
import openai, json

def agent_with_tools(
    user_query: str,
    tools: List[Dict[str, Any]],
    max_iterations: int = 5
) -> str:
    messages = [{"role": "user", "content": user_query}]

    for iteration in range(max_iterations):
        response = openai.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            return assistant_message.content

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            result = execute_tool(tool_call.function.name, tool_call.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    return "Max iterations reached without completion."
```

Understanding only the single-call example leads to underestimating cost, error paths, and termination conditions in real agents.

### Schema Quality Drives Tool Selection Quality

- Names should reveal intent: `search_customer_history` not `tool1`.
- Descriptions should specify *when* to use the tool, not just *what* it does.
- Parameters need explicit types, enums, and `required` fields in JSON Schema.
- Invalid input must be caught at the execution layer, not hoped away.

The model picks tools by reading names, descriptions, and schemas. Most tool-use quality is therefore an interface design problem, not a prompt engineering problem.

## Practical Design Reinforcement

### Tool Schemas Are Safety Boundaries, Not API Docs

The point of a detailed schema is not compensating for a dumb model—it is enforcing execution boundaries in code. Constraints like `additionalProperties: false`, enum restrictions, and length limits reduce incident cost more than they save tokens.

```json
{
  "type": "function",
  "name": "create_incident",
  "description": "Creates an incident ticket.",
  "parameters": {
    "type": "object",
    "properties": {
      "severity": {"type": "string", "enum": ["SEV-1", "SEV-2", "SEV-3"]},
      "title": {"type": "string", "minLength": 10, "maxLength": 120},
      "service": {"type": "string"}
    },
    "required": ["severity", "title", "service"],
    "additionalProperties": false
  }
}
```

### Python Tool Execution Wrapper

```python
import time

def call_tool(name: str, args: dict, registry: dict[str, callable]) -> dict:
    started = time.time()
    if name not in registry:
        return {"ok": False, "error_type": "unknown_tool", "retryable": False}
    try:
        data = registry[name](**args)
        return {
            "ok": True,
            "data": data,
            "latency_ms": int((time.time() - started) * 1000)
        }
    except TimeoutError:
        return {"ok": False, "error_type": "timeout", "retryable": True}
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__, "retryable": False}
```

Including `retryable` in the return lets the planner branch cleanly on next action. Throwing exceptions instead loses failure data and breaks the agent loop.

### Parallel Tool Calls and Merge Strategy

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_lookup(city: str):
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(get_weather, city)
        f2 = ex.submit(get_air_quality, city)
        return {"weather": f1.result(), "air": f2.result()}
```

When using parallel calls, define merge rules upfront. Conflicting data needs a tiebreaker—latest timestamp, confidence score, etc. Without one, the same input produces inconsistent final answers.

### Observability Dashboard Minimums

| Metric | Meaning | Alert threshold example |
| --- | --- | --- |
| tool_call_count | Call volume | 2× spike vs baseline |
| tool_error_rate | Failure ratio | 5-min avg > 3% |
| p95_tool_latency | Tail latency | > 1500 ms |
| unknown_tool_rate | Unregistered tool requests | > 0.5% |

Tool use is simultaneously the foundation of agent accuracy and a source of operational risk. Without metrics, accuracy drops masquerade as model problems.

## Operational Notes

### Failure Classification Template

In production, do not close failures with "the model got it wrong." Separate failure axes to clarify improvement priorities:

| Axis | Question | Example |
| --- | --- | --- |
| Planning failure | Did it decompose the goal incorrectly? | Unnecessary step repeated 6× |
| Execution failure | Did the tool call itself fail? | timeout, 429, schema mismatch |
| Verification failure | Did it accept a bad observation? | Wrong observation adopted |
| Policy failure | Did it cross a safety boundary? | Attempted external send of sensitive data |

Pin this table in your runbook so on-call engineers classify incidents consistently.

### Prompt / Tool Version Pinning

Teams struggling with change tracking typically separate prompt and tool schemas from code releases. Stable teams pin version fields in the request context:

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-en-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

Version fields alone accelerate regression analysis dramatically—you can immediately narrow whether a quality drop is model, prompt, or tool change.

### Observability Event Example

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

Structured logs first; migrate to OpenTelemetry / ELK / Grafana later with minimal cost.

### Deployment Checklist

- Model API keys separated into env vars / Secret Manager.
- `max_steps`, `timeout_ms`, `retry_budget` defaults verified against production profile.
- Fallback response wording does not convey false confidence to users.
- Alert thresholds (`error_rate`, `p95_latency`, `policy_violation_rate`) consistent between docs and code.

### Cost Control Points

| Item | Description | Recommended default |
| --- | --- | --- |
| max_steps | Max loops per execution | 4–8 |
| max_tool_calls | Tool call ceiling | 3–6 |
| input_token_budget | Input token cap | Service-specific |
| output_token_budget | Output token cap | Service-specific |

Cost control is not a post-optimization add-on. Fix execution budgets from day one so the service stays stable during usage spikes.

### CI Quality Gate Example

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

Automating minimum quality gates in the deploy pipeline prevents "accidentally good-looking builds" from reaching production.

## Common Confusion Points

- A tool-call response does not mean the API was already called—execution responsibility belongs to application code.
- A good name alone is not enough; description quality dominates routing accuracy.
- Feeding raw results back to the model seems fine until the payload size hits token cost.
- A schema does not replace server-side validation and authorization checks.
- A single working example does not imply production readiness—multi-tool loops and failure paths must be tested together.

## Key Takeaways

- Tool use is the core feature that makes agents practical automation tools.
- Tool schemas must be clear and specific for models to call them correctly.
- Error handling and tool selection strategies determine agent reliability.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Defined one tool with the OpenAI function-calling spec and exercised it.
- [ ] Observed how a bad schema confuses the model.
- [ ] Logged which tool the model picks when given 2-3 candidates.
- [ ] Closed the loop: tool output back into the model for the final answer.

<!-- a-grade-example:end -->

## Answering the Opening Questions

- **Where does the model decision end and application execution begin in function calling?**
  - The model requests which tool to call and with which arguments; application code validates that request and executes the real API or function.
- **How does an ambiguous tool schema make an agent fail?**
  - A vague name or argument contract makes the model choose similar tools or fill invalid values, which hides whether the failure came from the model or the schema.
- **What should be validated before tool output is fed back to the model?**
  - Validate argument types, allowed ranges, error shape, sensitive data exposure, and whether only the minimal useful result returns to the model.

<!-- toc:begin -->
## In this series

- [AI Agent 101 (1/10): What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): Context Engineering](./02-context-engineering.md)
- **AI Agent 101 (3/10): Tool Use Fundamentals (current)**
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

- [OpenAI function calling guide](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic tool use overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview)
- [LangChain tools](https://python.langchain.com/docs/concepts/tools/)
- [JSON Schema reference](https://json-schema.org/understanding-json-schema)

Tags: AI Agent, LLM, Tool Use, Python
