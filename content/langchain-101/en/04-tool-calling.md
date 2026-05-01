---
title: 'Tool calling — connecting external tools'
series: langchain-101
episode: 4
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
---

# Tool calling — connecting external tools

> LangChain 101 (4/6)

Example code: [github.com/yeongseon-books/langchain-101](https://github.com/yeongseon-books/langchain-101/tree/main/en/04-tool-calling)

LLMs generate text. Calculation, weather lookup, database queries — those require external tools. Tool calling is the pattern where the LLM produces a structured request ("call this function with these arguments"), the application executes the actual function, and the result goes back to the LLM.

This post covers defining tools with the `@tool` decorator, connecting them to an LLM with `bind_tools()`, and handling tool results in a simple loop.

Topics:

- defining tools with `@tool`
- connecting tools to an LLM with `bind_tools()`
- a minimal tool-call loop
- a multi-tool example
- what to watch out for

---

## Defining tools

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

When `tool_calls` is non-empty, the LLM is requesting a tool execution.

```
content: ''
tool_calls: [{'name': 'add_numbers', 'args': {'a': 15.0, 'b': 27.0}, 'id': 'call_...'}]
```

---

## A minimal tool-call loop

After the LLM requests a tool call, the application must execute the function and return the result as a `ToolMessage`.

```python
import os

from langchain_core.messages import HumanMessage, ToolMessage
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
tool_map = {t.name: t for t in tools}

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools)

def run_with_tools(question: str) -> str:
    """Simple tool-call loop."""
    messages = [HumanMessage(content=question)]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            if tool_name in tool_map:
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

The loop runs until the LLM produces a response with no tool calls. Each tool result is wrapped in a `ToolMessage` and appended to the conversation history.

---

## Multi-tool example

Real applications mix different types of tools.

```python
import os
from datetime import datetime

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

@tool
def get_current_time() -> str:
    """Return the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI from weight in kg and height in meters."""
    return round(weight_kg / (height_m ** 2), 2)

@tool
def word_frequency(text: str, word: str) -> int:
    """Count how many times a word appears in a text."""
    return text.lower().split().count(word.lower())

tools = [get_current_time, calculate_bmi, word_frequency]
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

print(run_with_tools("What time is it now?"))
print(run_with_tools("What is the BMI for someone weighing 70 kg at 1.75 m?"))
```

---

## What to watch out for

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

## Conclusion

The tool-calling loop has three moving parts: define tools with `@tool`, connect them with `bind_tools()`, and feed results back as `ToolMessage`. The loop runs until the LLM stops requesting tools.

The next post covers streaming — receiving LLM output token by token as it is generated.

<!-- toc:begin -->
## In this series

- [LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- [Prompt and LLM chain — assembling your first chain](./02-prompt-llm-chain.md)
- [Retriever — document search and context injection](./03-retriever.md)
- **Tool calling — connecting external tools (current)**
- Streaming — handling real-time output (upcoming)
- Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [LangChain tool calling guide](https://python.langchain.com/docs/how_to/tool_calling/)
- [Defining custom tools](https://python.langchain.com/docs/how_to/custom_tools/)
- [Groq tool use](https://console.groq.com/docs/tool-use)

Tags: LangChain, LCEL, Python, LLM
