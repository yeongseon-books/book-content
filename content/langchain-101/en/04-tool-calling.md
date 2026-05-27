---
title: "LangChain 101 (4/6): Tool calling — connecting external tools"
series: langchain-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-15'
seo_description: Tool calling works when the model stops pretending to do the work
  itself and starts choosing which real function should do it.
---

# LangChain 101 (4/6): Tool calling — connecting external tools

As soon as an LLM needs current data, calculations, or side effects, prompt engineering stops being enough. Tool calling is the handoff point where the model chooses what should run and the application decides how safely to run it.

This is the fourth post in the LangChain 101 series. It shows how tool metadata, execution loops, and result reinjection turn model output into real function calls.

![The flow at a glance](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-02-the-flow-at-a-glance.en.png)
*The flow at a glance*
> Tool calling works when the model stops pretending to do the work itself and starts choosing which real function should do it.

## Questions to Keep in Mind

- Does `bind_tools()` give the model execution power, or define a call format?
- What must be validated before a tool call becomes a real function call?
- What failures should a dispatcher prevent when several tools are available?

## Minimal runnable example

```python
import os

from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
response = llm.bind_tools([add_numbers]).invoke("Add 13 and 29.")
print(response.tool_calls)
```

## Defining tools

![Function definition into tool metadata](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-01-defining-tools.en.png)

*Function definition into tool metadata*
The `@tool` decorator turns a Python function into a LangChain tool. The docstring tells the LLM what the tool does and when to use it. Type hints define the input schema.

```python
from langchain_core.tools import tool

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers. Use this when addition is needed."""
    return a + b

@tool
def get_word_count(text: str) -> int:
    """Return the word count of a text string."""
    return len(text.split())

@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32

print(f"name: {add_numbers.name}")
print(f"description: {add_numbers.description}")
print(f"schema: {add_numbers.args_schema.model_json_schema()}")
```

---

## Connecting tools with bind_tools()

![Binding tool metadata to the model](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-02-connecting-tools-with-bind-tools.en.png)

*Binding tool metadata to the model*
`bind_tools()` informs the LLM which tools are available.

```python
import os

from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

tools = [add_numbers, multiply_numbers]

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

llm_with_tools = llm.bind_tools(tools)

response = llm_with_tools.invoke("What is 15 plus 27?")

print(f"content: {response.content!r}")
print(f"tool_calls: {response.tool_calls}")
```

---

## A minimal tool-call loop

![Tool call execution and reinjection loop](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-03-a-minimal-tool-call-loop.en.png)

*Tool call execution and reinjection loop*
After the LLM requests a tool call, the application must execute the function and return the result as a `ToolMessage`.

```python
import os

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers. Use this for arithmetic addition."""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers. Use this for arithmetic multiplication."""
    return a * b

tools = [add_numbers, multiply_numbers]
tool_map = {tool.name: tool for tool in tools}

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = (
    "You must use the provided arithmetic tools for addition and multiplication. "
    "Do not answer from memory when a tool is appropriate. "
    "After tool results arrive, produce one short final answer."
)

def run_with_tools(question: str) -> str:
    """Simple tool-call loop with explicit tool-use instructions."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            result = tool_map[tool_name].invoke(tool_args)
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id,
                )
            )
            print(f"  executed: {tool_name}({tool_args}) = {result}")

questions = [
    "What is 15 plus 27?",
    "What is 7 times 8?",
    "Add 5 and 3, then multiply the result by 4. What do you get?",
]

for q in questions:
    print(f"\nquestion: {q}")
    answer = run_with_tools(q)
    print(f"answer: {answer}")
```

The loop runs until the LLM produces a response with no tool calls. Each tool result is wrapped in a `ToolMessage` and appended to the conversation history. The system message matters too: it makes the success condition explicit, so a simple multiplication question is less likely to slip through as a plain text answer.

---

## Add a dispatcher before you trust the loop

Happy-path demos are not enough in production. You need one place that handles unknown tools, malformed arguments, and runtime exceptions in a uniform way.

```python
from langchain_core.messages import ToolMessage

def execute_tool_call(tool_call: dict) -> ToolMessage:
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_id = tool_call["id"]

    if tool_name not in tool_map:
        return ToolMessage(
            content=f"ERROR: unknown tool '{tool_name}'",
            tool_call_id=tool_id,
        )

    try:
        result = tool_map[tool_name].invoke(tool_args)
        return ToolMessage(content=str(result), tool_call_id=tool_id)
    except Exception as exc:
        return ToolMessage(
            content=f"ERROR: {type(exc).__name__}: {exc}",
            tool_call_id=tool_id,
        )

ok_call = {"name": "add_numbers", "args": {"a": 10, "b": 5}, "id": "call_ok"}
bad_call = {"name": "divide_numbers", "args": {"a": 10, "b": 5}, "id": "call_bad"}

print(execute_tool_call(ok_call).content)
print(execute_tool_call(bad_call).content)
```

With this dispatcher in place, you can tell in one log line whether the failure came from tool routing, bad arguments, or an exception inside the tool itself.

---

## Multi-tool example

Real applications mix different types of tools. To keep verification easy, this example uses deterministic lookups instead of a clock-based tool.

```python
import os

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def get_office_hours(team: str) -> str:
    """Return office hours for a named team."""
    hours = {
        "support": "09:00-18:00 KST",
        "ml-platform": "10:00-19:00 KST",
    }
    return hours[team]

@tool
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI from weight in kg and height in meters."""
    return round(weight_kg / (height_m ** 2), 2)

@tool
def word_frequency(text: str, word: str) -> int:
    """Count how many times a word appears in a text."""
    return text.lower().split().count(word.lower())

tools = [get_office_hours, calculate_bmi, word_frequency]
tool_map = {t.name: t for t in tools}

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools)

def run_with_tools(question: str) -> str:
    messages = [HumanMessage(content=question)]
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for tc in response.tool_calls:
            result = tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            print(f"  {tc['name']}({tc['args']}) = {result}")

print(run_with_tools("When is the support team available?"))
print(run_with_tools("What is the BMI for someone weighing 70 kg at 1.75 m?"))
print(run_with_tools("How many times does 'vector' appear in 'vector search makes vector retrieval practical'?"))
```

---

This example makes the verification surface explicit. The execution log shows which tool was selected, what arguments the model supplied, and whether the final natural-language answer actually reflects the tool result.

---

## What to watch out for

![Guardrails for invalid tool requests](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/04/04-04-what-to-watch-out-for.en.png)

*Guardrails for invalid tool requests*
**Docstrings drive tool selection.** The LLM reads docstrings to decide which tool to use and when. Vague or overlapping descriptions cause wrong tool selection.

**Validate inputs inside the tool.** Type hints define the schema but do not prevent the LLM from passing invalid values at runtime. For tools with side effects, validate inputs before executing.

**Guard against infinite loops.** Add a maximum iteration count when the loop is not bounded by a known termination condition.

```python
MAX_ITERATIONS = 10

def run_with_tools_safe(question: str) -> str:
    messages = [HumanMessage(content=question)]
    for _ in range(MAX_ITERATIONS):
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for tc in response.tool_calls:
            result = tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    return "Max iterations reached."
```

---

## What to notice in this code

- The `@tool` docstring and type hints become the model-facing description and argument schema.
- `bind_tools()` does not create an agent by itself. It attaches tool metadata to the model so tool-call requests become possible.
- When `tool_calls` appears in the response, the application must execute the function and return the result as `ToolMessage` for the reasoning loop to continue.
- A dispatcher gives you one place to normalize unknown tools, runtime exceptions, and successful results into the same message shape.
- The multi-tool example is valuable because it makes the request → execute → reinject loop explicit.

## Where engineers get confused

- Tool calling is often mistaken for model-side execution, but the application always owns the real function call.
- Vague tool descriptions lead to wrong tool selection or malformed arguments.
- Iteration limits are not optional. A bad tool loop can keep regenerating invalid calls forever.

## Checklist

- [ ] I can explain the role of `@tool`, `bind_tools()`, and `ToolMessage`
- [ ] I can describe the exact sequence after the model asks for a tool
- [ ] I understand why a tool loop needs an explicit stop condition

## Conclusion

The tool-calling loop has three moving parts: define tools with `@tool`, connect them with `bind_tools()`, and feed results back as `ToolMessage`. The loop runs until the LLM stops requesting tools.

The next post covers streaming — receiving LLM output token by token as it is generated.

## Answering the Opening Questions

- **Does `bind_tools()` give the model execution power, or define a call format?**
  `bind_tools()` defines the names and argument schemas the model may request; it does not hand over unrestricted execution power.

- **What must be validated before a tool call becomes a real function call?**
  Validate tool name, argument schema, required values, allowed ranges, and user permissions before invoking the function.

- **What failures should a dispatcher prevent when several tools are available?**
  A dispatcher should block unknown tools, invalid arguments, duplicate execution, long-running calls, and unstructured errors.

<!-- toc:begin -->
## In this series

- [LangChain 101 (1/6): LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- [LangChain 101 (2/6): Prompt and LLM chain — assembling your first chain](./02-prompt-llm-chain.md)
- [LangChain 101 (3/6): Retriever — document search and context injection](./03-retriever.md)
- **LangChain 101 (4/6): Tool calling — connecting external tools (current)**
- LangChain 101 (5/6): Streaming — handling real-time output (upcoming)
- LangChain 101 (6/6): Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [LangChain tool calling guide](https://python.langchain.com/docs/how_to/tool_calling/)
- [Defining custom tools](https://python.langchain.com/docs/how_to/custom_tools/)
- [ToolMessage and message types](https://python.langchain.com/docs/concepts/messages/)
- [Groq tool use](https://console.groq.com/docs/tool-use)

### Related Series

- [LangGraph 101](../../langgraph-101/en/01-graph-basics.md) — once your tool loop needs explicit state, branching, or retries, the graph-based control flow becomes easier to maintain than a single while loop.

Tags: LangChain, LCEL, Python, LLM
