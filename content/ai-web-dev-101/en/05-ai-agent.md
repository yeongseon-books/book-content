---
title: "AI Web Development 101 (5/7): First steps with AI agents — making the model use tools"
series: ai-web-dev-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- Web Development
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: Learn how tool use works, how function calls are structured, and how to build a small multi-tool agent loop safely.
---

> **Deprecation notice**: This series is superseded by [`llm-app-foundations-101`](../../llm-app-foundations-101/en/) and [`ai-app-patterns-101`](../../ai-app-patterns-101/en/). New readers are encouraged to start with the successor series.

# AI Web Development 101 (5/7): First steps with AI agents — making the model use tools

So far, the AI features in this series only exchanged text. They could answer questions, but they could not actually fetch live weather, run a calculator, or query an external system. To move beyond text-only answers, you need a loop where the model can request tools.

This is the 5th post in the AI Web Development 101 series.

Here, we will focus on tool use, function calling, and the boundary between model judgment and application execution.


![AI Web Development 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/05/assistant-vs-agent.en.png)
*AI Web Development 101 chapter 5 flow overview*

> An agent is a chatbot plus a tool-use loop — the model proposes which function to call, but the application owns validation and execution, and that boundary is the entire safety story.

## Questions to Keep in Mind

- What makes an agent different from a normal chatbot?
- How does function calling work as a contract?
- How does the model ask for a function invocation?

## Chatbot versus agent

A normal chatbot generates text from the information already available in the prompt or the model weights. An agent goes one step further. It can decide that a tool is needed, request the tool call, read the result, and then continue.

- chatbot: answer from existing context
- agent: ask for tools such as APIs, databases, calculators, or search systems

## The basic tool-use loop

1. the application tells the model which tools exist
2. the model decides which tool is needed
3. the model emits a function-call request with arguments
4. the application validates and executes the function
5. the result goes back into the conversation so the model can produce the final answer

The key point is execution ownership. The model proposes. The application decides whether and how to execute.

![How model judgment and function execution interact](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/05/function-calling-cycle.en.png)

*How model judgment and function execution interact*

## A minimal tool definition

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Returns the current weather for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, such as Seoul or Busan"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

The model does not read your Python implementation. It reads the tool description and parameter schema. Weak descriptions often lead to weak tool selection.

## Example 1: weather lookup agent

```python
import json
from openai import OpenAI

client = OpenAI()

def get_weather(location: str) -> str:
    if "Seoul" in location:
        return json.dumps({"location": "Seoul", "temperature": "25C", "condition": "Sunny"})
    if "Busan" in location:
        return json.dumps({"location": "Busan", "temperature": "22C", "condition": "Partly cloudy"})
    return json.dumps({"location": location, "temperature": "Unknown", "condition": "No data"})

messages = [{"role": "user", "content": "What is the weather in Seoul today?"}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

tool_calls = response.choices[0].message.tool_calls

if tool_calls:
    tool_call = tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    function_response = get_weather(location=function_args["location"])

    messages.append(response.choices[0].message)
    messages.append({
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": function_name,
        "content": function_response,
    })

    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    print(final_response.choices[0].message.content)
```

The important boundary is visible here. The model never directly executes `get_weather`. It only asks for it.

## Example 2: a multi-tool loop

Tool use becomes more interesting when more than one step is required.

```python
import ast
import json
import operator as op

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](safe_eval(node.left), safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](safe_eval(node.operand))
    raise ValueError("Unsupported expression")

def get_exchange_rate(from_currency, to_currency):
    rates = {"USD_KRW": 1350}
    pair = f"{from_currency}_{to_currency}"
    return json.dumps({"pair": pair, "rate": rates.get(pair, 1300)})

def calculate(expression):
    tree = ast.parse(expression, mode="eval")
    return str(safe_eval(tree.body))
```

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Gets an exchange rate between two currencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string"},
                    "to_currency": {"type": "string"}
                },
                "required": ["from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluates a simple arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    }
]
```

```python
def run_agent(user_prompt):
    messages = [{"role": "user", "content": user_prompt}]

    for _ in range(5):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if name == "get_exchange_rate":
                result = get_exchange_rate(**args)
            elif name == "calculate":
                result = calculate(**args)
            else:
                result = "Unknown tool"

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": name,
                "content": result,
            })

    return messages[-1].content
```

![An agent using multiple tools in sequence](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/05/multi-tool-example-flow.en.png)

*An agent using multiple tools in sequence*

## How to read the agent loop

1. user input
2. model judgment
3. tool-call request
4. application execution
5. result observation
6. either final answer or another loop iteration

That order matters because it keeps debugging grounded. When the behavior looks strange, you can ask whether the issue came from tool selection, argument generation, execution, or result interpretation.

![The repeating agent loop of judgment and action](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/05/agent-loop-overview.en.png)

*The repeating agent loop of judgment and action*

## Safety rules you need immediately

- clear tool descriptions
- argument validation before execution
- retry limits and timeouts
- maximum loop count
- permission boundaries for side-effecting tools

The core rule is simple: never execute model-generated arguments blindly.

![Tool permission boundaries and safety checks](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/05/tool-permission-boundary.en.png)

*Tool permission boundaries and safety checks*

## Checklist

- [ ] Tool descriptions and parameter schemas are explicit enough.
- [ ] The application validates arguments before execution.
- [ ] The loop has a maximum number of iterations.
- [ ] High-risk tools have stricter permission boundaries.

## Implementing the Tool Call Loop Explicitly

The core of an agent is the repeated loop: "model decides, system executes, model summarizes again." Without making this loop explicit in code, root-cause analysis during incidents becomes nearly impossible. The example below is the smallest operational pattern for OpenAI tool calls.

```python
from openai import OpenAI
import json

client = OpenAI()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Look up current weather by city name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    }
]

def run_agent(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    for _ in range(3):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump())

        if not msg.tool_calls:
            return msg.content or ""

        for tool_call in msg.tool_calls:
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "get_weather":
                result = {"city": args["city"], "temperature": "22C", "condition": "clear"}
            else:
                result = {"error": "unknown tool"}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    return "Tool call iteration limit exceeded."
```

The key is `for _ in range(3)` — an iteration cap. Without it, abnormal calls can spiral into infinite loops.

## Prompt Template: Fixing Tool Use Policy in Text

To prevent the model from abusing tools unnecessarily, state the policy explicitly in the prompt.

```text
You are a Korean work assistant.
Tool use policy:
- Call tools only when factual lookup is needed.
- Prefer the calculation tool over internal reasoning for math.
- If a tool result contains an error field, explain the cause to the user and offer retry options.
Final answer format:
1) Conclusion
2) Evidence
3) Next action
```

Without policy, variance in whether the model uses tools for the same question grows large.

## Combining RAG and Agents

In practice, a common flow is: the agent calls a search tool first, then additional tools as needed. For example, an "incident root cause analysis" question might sequentially need document search, log lookup, and status page check.

```python
TOOLS = [search_docs_tool, get_service_status_tool, summarize_incident_tool]
```

The important point: do not leave tool dependency ordering entirely to the model. Enforce minimal sequencing at the orchestration layer — for example, skip status page lookup if search results are empty.

## LangChain AgentExecutor Example

Frameworks reduce boilerplate for the iteration loop. However, as abstraction increases, log design becomes even more important.

```python
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = initialize_agent(
    tools=my_tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)

result = agent.invoke({"input": "Is it raining in Seoul today? If so, recommend an umbrella."})
```

Rather than using `verbose=True` logs directly in production, convert them to structured event logs for storage — this is better for later analysis.

## Evaluation Metrics: Call Quality Before Accuracy

Looking only at simple accuracy when evaluating agent quality misses important problems. Track these metrics together.

- Tool selection accuracy: ratio of correctly choosing the needed tool
- Tool argument accuracy: schema validation pass rate
- Average call count: detecting excessive chaining
- Call failure recovery rate: ratio of returning normal answers after tool errors
- Response termination rate: ratio of normal completion before hitting loop cap

Collecting these metrics lets you quickly identify "agents that get the right answer but at excessive cost."

## Regression Testing on Tool Schema Changes

Even small tool parameter changes can drastically destabilize agent behavior. For example, renaming `city` to `city_name` can cause the model to keep calling the old name. Therefore schema changes must always be accompanied by regression tests.

```python
TEST_QUESTIONS = [
    "Tell me the weather in Seoul",
    "What is the current temperature in Busan?",
    "Tokyo weather and whether I need an umbrella",
]
```

If tool call failure rate spikes in test results, update the tool description and example inputs in the prompt together.

## Pre-Deployment Agent Simulation Scenarios

Agents break more often on exception paths than normal paths. Before deployment, run these scenarios automatically.

1. Tool returns a normal response
2. Tool times out
3. Tool returns a field not in the schema
4. Model tries to call a non-existent tool

```python
def safe_tool_dispatch(name, args):
    if name not in TOOL_REGISTRY:
        return {"error": "tool_not_found", "name": name}
    try:
        return TOOL_REGISTRY[name](**args)
    except TimeoutError:
        return {"error": "tool_timeout"}
    except Exception as exc:
        return {"error": "tool_exception", "detail": str(exc)}
```

With this defensive code, even when the agent fails it can deliver an explainable error to the user.


## Summary

An agent is not “the model doing everything by itself.” It is a controlled loop where the model requests external actions and the application remains the execution owner.

- Tool use lets the model ask for functions rather than guess everything from text alone.
- The application validates and executes those functions.
- Multi-step tool loops make agent behavior feel more capable, but they also expand the risk surface.
- Safety controls are not optional once tools can cause side effects.

The next chapter shifts from tool use to deployment, where these AI features have to run in real environments with logs, secrets, and cost limits.

## Answering the Opening Questions

- **What distinguishes a regular chatbot from an agent?**
  - A regular chatbot generates text within its existing knowledge, while an agent invokes external tools like `get_weather`, `get_exchange_rate`, and `calculate` as needed to assemble answers. The article split "How's the weather in Seoul?" and "Convert $100 to KRW and subtract 10% fee" into separate examples precisely to show this difference. The agent's core is not producing more text but bringing necessary external actions into the loop.
- **What contract governs Tool Use / Function Calling?**
  - The contract is defined by the `name`, `description`, `parameters`, and `required` schema inside the `tools` array. The model produces `tool_calls` based on this specification; actual execution happens in the application after `json.loads(tool_call.function.arguments)` passes allowlist and type checks. The article emphasized that poor `description` or renamed schemas degrade call quality before they affect answer accuracy.
- **How does the model request "please execute this function"?**
  - The model does not execute functions directly—it places the function name and arguments in `response.choices[0].message.tool_calls`. The application then appends `{"role": "tool", ...}` with the result and calls `client.chat.completions.create(...)` again for the final answer. Loop bounds like `for _ in range(3)` or `for i in range(5)` exist to prevent this request-execute-re-judge cycle from running indefinitely.
<!-- toc:begin -->
## In this series

- [AI Web Development 101 (1/7): AI API first steps — sending your first request with the OpenAI API](./01-hello-ai-api.md)
- [AI Web Development 101 (2/7): Prompt engineering basics — getting the answer you actually want](./02-prompt-engineering.md)
- [AI Web Development 101 (3/7): Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK](./03-ai-chatbot.md)
- [AI Web Development 101 (4/7): RAG introduction — answering with your own data](./04-rag-intro.md)
- **First steps with AI agents — making the model use tools (current)**
- Deploying an AI web app — shipping to Vercel and Azure (upcoming)
- Evaluating and improving an AI app — measuring quality over time (upcoming)

<!-- toc:end -->

## References

- [OpenAI: Function calling guide](https://platform.openai.com/docs/guides/function-calling) — canonical spec for `tools`, `tool_choice`, and the `tool_calls` response flow
- [OpenAI: Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) — enforcing tool and response schemas with JSON Schema
- [OpenAI Cookbook: function calling and tools](https://cookbook.openai.com/topic/tools) — runnable examples of the tool-calling loop
- [Anthropic: Tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — how a different provider defines the same tool-use pattern, useful for cross-checking
- [LangGraph: Agent runtime](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/) — what a framework-managed agent loop looks like when you stop hand-rolling it
- [JSON Schema specification](https://json-schema.org/specification.html) — keywords and validation rules behind the `parameters` schema

Tags: AI, LLM, Web Development, Python, Tutorial
