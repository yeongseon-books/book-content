---
title: "AI App Patterns 101 (4/6): Agent and tool pattern — autonomous tool selection"
series: ai-app-patterns-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-15'
seo_description: An agent is a controller that lets the model choose tool-call paths
  at runtime instead of hardcoding every step ahead of time.
---

# AI App Patterns 101 (4/6): Agent and tool pattern — autonomous tool selection

Some problems stop fitting a fixed chain the moment the next step depends on what the model discovers during execution. At that point, the real design question is not whether agents are powerful, but how narrowly you can define the tool choices and the control loop around them.

This is the 4th post in the AI App Patterns 101 series. Here we examine when the agent-and-tool pattern is justified and how to make tool selection observable and debuggable.

![Fixed chain versus dynamic agent](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-01-fixed-chain-versus-dynamic-agent.en.png)
*Fixed chain versus dynamic agent*
> An agent is a controller that lets the model choose tool-call paths at runtime instead of hardcoding every step ahead of time.

## Questions to Keep in Mind

- When an agent chooses a tool, how much autonomy does it really have?
- What risk appears if tool names and arguments are not validated before execution?
- How can ReAct traces narrow agent failures faster?

## Agent vs chain

### Fixed chain versus dynamic agent

**Chain**: input → step A → step B → output. The execution path is determined at design time.

**Agent**: input → LLM reasons → selects tool → executes tool → observes result → repeats if needed → final answer. The execution path is determined at runtime.

Agents use the ReAct (Reason + Act) loop: Thought → Action → Observation, repeated until the LLM determines it has enough information to answer. The LLM writes its reasoning, names a tool, supplies its arguments, reads the tool output, and then reasons again.

---

## Defining tools

### Tool registry and selection surface

![Tool registry and selection surface](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-02-tool-registry-and-selection-surface.en.png)

*Tool registry and selection surface*
In LangChain, a tool is a Python function decorated with `@tool`. The docstring becomes the description the LLM reads when deciding which tool to use. Write it precisely — a vague docstring leads to wrong tool selection.

```python
import math
import os
from datetime import datetime

from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.
    Examples: '2 + 3 * 4', 'sqrt(16)', 'pow(2, 10)'
    Uses Python expression syntax. Only math functions are allowed.
    """
    try:
        allowed = {
            "sqrt": math.sqrt,
            "pow": math.pow,
            "abs": abs,
            "round": round,
            "pi": math.pi,
            "e": math.e,
        }
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as exc:
        return f"calculation error: {exc}"

@tool
def get_current_time(timezone: str = "Asia/Seoul") -> str:
    """
    Return the current date and time.
    The timezone parameter accepts a timezone name (default: Asia/Seoul).
    """
    now = datetime.now()
    return f"current time: {now.strftime('%Y-%m-%d %H:%M')} ({timezone})"

@tool
def word_count(text: str) -> str:
    """
    Return the word count and character count of the given text.
    """
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    return f"words: {words}, characters: {chars} (excluding spaces: {chars_no_space})"

@tool
def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert a value between units.
    Supported conversions: km/mile, kg/lb, celsius/fahrenheit, m/ft.
    Example: value=100, from_unit='km', to_unit='mile'
    """
    conversions = {
        ("km", "mile"): lambda x: x * 0.621371,
        ("mile", "km"): lambda x: x * 1.60934,
        ("kg", "lb"): lambda x: x * 2.20462,
        ("lb", "kg"): lambda x: x * 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("m", "ft"): lambda x: x * 3.28084,
        ("ft", "m"): lambda x: x * 0.3048,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return f"unsupported conversion: {from_unit} to {to_unit}"
    result = conversions[key](value)
    return f"{value} {from_unit} = {result:.4f} {to_unit}"

@tool
def search_policy(query: str) -> str:
    """
    Search the internal support policy knowledge base.
    Use this for refund rules, shipping delays, account recovery, or SLA questions.
    """
    kb = {
        "refund": "Annual plans can be refunded within 14 days if usage stays below 100 API calls.",
        "shipping": "Orders delayed more than 10 business days qualify for expedited reshipment.",
        "password": "Account recovery requires email verification and one recent billing detail.",
    }
    lowered = query.lower()
    for keyword, answer in kb.items():
        if keyword in lowered:
            return answer
    return "policy not found"
```

---

## Building a ReAct agent

### Thought action observation loop

![Thought action observation loop](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-03-thought-action-observation-loop.en.png)

*Thought action observation loop*
```python
import os

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

tools = [calculate, get_current_time, word_count, unit_convert, search_policy]

# ReAct prompt — instructs the LLM to follow the Thought/Action/Observation loop
react_prompt = PromptTemplate.from_template("""
You are an AI assistant that answers questions using the tools available to you.

Available tools:
{tools}

Tool names: {tool_names}

You MUST follow this exact format:

Question: the question to answer
Thought: think about how to approach the question
Action: the name of the tool to use (must be one from the tool names list)
Action Input: the input to pass to the tool
Observation: the result returned by the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)

questions = [
    "What is 2 to the power of 10?",
    "What time is it now?",
    "How many miles is 100 kilometers?",
    "Count the words in this text, then multiply by 2: 'The quick brown fox jumps over the lazy dog'",
    "What is the refund policy for annual plans?",
]

for question in questions:
    print(f"\n{'=' * 60}")
    print(f"question: {question}")
    result = agent_executor.invoke({"input": question})
    print(f"final answer: {result['output']}")
```

---

## Verify which tool the agent actually picked

### Intermediate-step trace for tool selection

![Execution trace and stopping conditions](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-04-execution-trace-and-stopping-conditions.en.png)

*Execution trace and stopping conditions*
An agent demo is not trustworthy until you can inspect the chosen tool path. `verbose=True` is useful for humans, but structured traces are better when you want regression checks.

```python
def run_with_trace(question: str) -> dict:
    result = agent_executor.invoke({"input": question})
    tool_sequence = [action.tool for action, _ in result["intermediate_steps"]]
    return {
        "question": question,
        "tools": tool_sequence,
        "answer": result["output"],
    }

test_cases = [
    ("What is 2 to the power of 10?", "calculate"),
    ("What is the refund policy for annual plans?", "search_policy"),
    ("How many feet is 3 meters?", "unit_convert"),
]

for question, expected_first_tool in test_cases:
    traced = run_with_trace(question)
    print(f"\nquestion: {traced['question']}")
    print(f"tools used: {traced['tools']}")
    print(f"expected first tool: {expected_first_tool}")
    print(f"answer: {traced['answer']}")
```

**Expected output:**

```text
question: What is the refund policy for annual plans?
tools used: ['search_policy']
expected first tool: search_policy
answer: Annual plans can be refunded within 14 days if usage stays below 100 API calls.
```

This is where agent debugging becomes practical. You stop saying “the model was weird” and instead ask whether the wrong tool was chosen, whether the right tool description was missing, or whether the loop continued longer than it should have.

---

## Observing the agent's reasoning

### Execution trace and stopping conditions

![Execution trace and stopping conditions](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-04-execution-trace-and-stopping-conditions.en.png)

*Execution trace and stopping conditions*
With `verbose=True`, the console prints every Thought, Action, Action Input, and Observation. For a simple question, the agent usually completes in one round. For a two-step question — count words, then multiply — it completes in two rounds, using the output of the first tool as input to the next computation.

`max_iterations` prevents infinite loops. Five to ten iterations cover most practical tasks.

### First checks when the agent picks the wrong tool

When tool choice looks wrong, inspect these in order:

1. **tool description clarity** — does the docstring say when the tool should and should not be used?
2. **overlapping capability** — are two tools both plausible for the same question?
3. **trace length** — is the agent looping because the first Observation was too vague?
4. **stopping criteria** — is `max_iterations` high enough to finish but low enough to fail safely?

---

## Handling tool errors gracefully

### Returning tool errors as observations

![Returning tool errors as observations](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-05-returning-tool-errors-as-observations.en.png)

*Returning tool errors as observations*
If a tool raises an unhandled exception, the agent stops. Catching exceptions inside the tool and returning a descriptive error string keeps the agent running. The error string becomes the Observation, and the LLM can decide to try a different approach or explain the failure.

```python
@tool
def safe_divide(a: float, b: float) -> str:
    """Divide a by b. Returns an error message if b is zero."""
    if b == 0:
        return "error: cannot divide by zero"
    return str(a / b)
```

---

## What to notice in this code

- `main.py` keeps the tool surface intentionally narrow: arithmetic, time, word counting, unit conversion, and policy lookup.
- `return_intermediate_steps=True` makes the chosen tool path visible enough for regression-style verification.
- Short prompts and narrow tool descriptions reduce tool-selection failure modes.

---

## Where engineers get confused

- Agents are not automatically smarter; they trade predictability for runtime flexibility.
- If the tools are weak, the agent is weak. The bottleneck is often the tool interface, not the LLM.
- A search tool and RAG can look similar from far away, but one is tool invocation and the other is prompt-context injection.

---

## Checklist

- [ ] Each tool has a clear description and input shape
- [ ] The AgentExecutor invokes the calculator tool once
- [ ] The AgentExecutor can choose the policy search tool for a knowledge-base question
- [ ] Intermediate steps make the chosen tool sequence visible to the caller

---

## Orchestration layer for safe tool calls

### Tool input schema validation

Agent autonomy is only safe when tool inputs are validated. Check the schema before each call so invalid arguments become an Observation the agent can retry from.

```python
from pydantic import BaseModel, ValidationError

class UnitConvertArgs(BaseModel):
    value: float
    from_unit: str
    to_unit: str

def call_unit_convert_with_validation(raw_args: dict) -> str:
    try:
        args = UnitConvertArgs.model_validate(raw_args)
    except ValidationError as exc:
        return f"error: invalid arguments - {exc.errors()}"

    return unit_convert.invoke({
        'value': args.value,
        'from_unit': args.from_unit,
        'to_unit': args.to_unit,
    })
```

This layer looks trivial but significantly improves operational stability. When the model stuffs `"100km"` into a numeric field, the error is logged immediately and the agent gets a chance to pick a different strategy.

### FastAPI agent execution endpoint

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    question: str

@app.post('/agent/run')
def run_agent(req: AgentRequest):
    result = agent_executor.invoke({'input': req.question})
    steps = [
        {
            'tool': action.tool,
            'tool_input': str(action.tool_input),
            'observation': observation,
        }
        for action, observation in result['intermediate_steps']
    ]
    return {
        'question': req.question,
        'answer': result['output'],
        'steps': steps,
    }
```

This response shape is the core of agent observability. The caller can trace "why did it answer this way" step by step, and operators can accumulate failure cases as reproducible test fixtures.

## Tool permission boundaries and timeouts

In production, not every tool is exposed to every request. Limit the available tool set by user role, org policy, or request risk level.

```python
ROLE_TOOL_POLICY = {
    'viewer': {'word_count', 'get_current_time'},
    'support': {'word_count', 'get_current_time', 'search_policy'},
    'analyst': {'word_count', 'get_current_time', 'calculate', 'unit_convert'},
}

def allowed_tools_for_role(role: str, all_tools: list):
    allowed_names = ROLE_TOOL_POLICY.get(role, set())
    return [t for t in all_tools if t.name in allowed_names]
```

### Timeout and circuit breaker

When a tool calls an external API, a missing timeout blocks the entire agent loop. Separate timeout and retry policy per tool.

```python
import time

def call_with_timeout(tool_fn, kwargs: dict, timeout_sec: float = 2.0):
    start = time.time()
    result = tool_fn(**kwargs)
    elapsed = time.time() - start
    if elapsed > timeout_sec:
        return f"error: tool_timeout elapsed={elapsed:.2f}s"
    return result
```

Without this layer, it becomes impossible to tell whether an agent failure stems from model reasoning or external tool latency.

## Agent failure classification and playbook

Classifying agent failures by type speeds up response time. Common failure types:

- `tool_not_found`: model generated a disallowed tool name
- `tool_argument_invalid`: input schema mismatch
- `tool_runtime_error`: exception inside the tool
- `max_iterations_exceeded`: loop cap reached

```python
def classify_agent_failure(result: dict) -> str:
    if result.get('output'):
        return 'success'

    steps = result.get('intermediate_steps', [])
    if not steps:
        return 'no_action_generated'

    last_obs = str(steps[-1][1]).lower()
    if 'invalid arguments' in last_obs:
        return 'tool_argument_invalid'
    if 'timeout' in last_obs:
        return 'tool_runtime_error'
    return 'unknown_failure'
```

### Playbook

```text
if tool_argument_invalid -> strengthen schema hints + add few-shot examples
if tool_runtime_error -> review timeout/retry policy
if max_iterations_exceeded -> clarify termination conditions in prompt
```

This classification turns vague reports like "the agent is sometimes weird" into actionable improvement tasks.

## System prompt minimum template

Agent quality depends on constraint clarity more than prompt length. Short, fixed rules for tool selection stabilize the loop.

```text
You are a tool-based assistant.
Rule 1) Generate an Action only for questions that need a tool.
Rule 2) Tool arguments must follow the JSON schema.
Rule 3) If the Observation is an error, explain the cause and retry at most once.
Rule 4) When evidence is sufficient, write the Final Answer and stop.
```

Even brief rules significantly reduce repeated failures. An agent becomes more stable when told what NOT to do rather than given broad freedom.

### Tool selection regression test

Maintain a fixed set of at least 20 questions and verify that the first tool choice matches expectations. This test catches prompt edits that silently break tool routing.

---

## Conclusion

The agent pattern extends chain-based LLM apps into systems that can reason across multiple steps and tools. The docstring is the only signal the LLM has for tool selection — treat it as a contract, not a comment. Keep tools narrow and focused: one clear responsibility each, error messages instead of exceptions, and deterministic behavior for the same input.

The next post covers workflow automation: designing multi-step chains where each stage transforms data and passes it to the next.

## Answering the Opening Questions

- **When an agent chooses a tool, how much autonomy does it really have?**
  The agent can request a tool only within the list and schema the application exposes. That is bounded autonomy.

- **What risk appears if tool names and arguments are not validated before execution?**
  Without validation, unknown tool calls, invalid arguments, unauthorized actions, or duplicate execution can reach real functions.

- **How can ReAct traces narrow agent failures faster?**
  ReAct traces show the thought, selected tool, and arguments, making it easier to separate prompt issues, tool-description issues, and execution errors.

<!-- toc:begin -->
## In this series

- [AI App Patterns 101 (1/6): Chatbot pattern — managing conversation history and state](./01-chatbot-pattern.md)
- [AI App Patterns 101 (2/6): RAG Q&A pattern — document-based question answering](./02-rag-qa-pattern.md)
- [AI App Patterns 101 (3/6): Document assistant — summarization, extraction, classification](./03-document-assistant.md)
- **AI App Patterns 101 (4/6): Agent and tool pattern — autonomous tool selection (current)**
- AI App Patterns 101 (5/6): Workflow automation — designing multi-step chains (upcoming)
- AI App Patterns 101 (6/6): Human-in-the-loop — designing for human intervention (upcoming)

<!-- toc:end -->

---

## References

- [LangChain agents overview](https://python.langchain.com/docs/modules/agents/)
- [ReAct paper (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- [LangChain tool definition](https://python.langchain.com/docs/modules/tools/)

Tags: LLM, RAG, Agent, Python
