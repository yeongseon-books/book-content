---
title: Building Your First Agent
series: ai-agent-101
episode: 10
language: en
status: draft
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Tutorial
- Python
- Hands-on
last_reviewed: '2026-05-02'
---

# Building Your First Agent

> AI Agent 101 Series (10/10)

Now let's synthesize what we've learned and build a real agent. This article implements a simple yet practical agent from start to finish. We'll cover the entire process: context setup, tool definition, workflow composition, error handling, and testing.

Recommended frameworks are LangGraph and Crew AI. Both simplify agent construction but have different approaches. LangGraph is strong in graph-based workflows, while Crew AI is strong in multi-agent collaboration.

This article covers end-to-end implementation examples, LangGraph vs Crew AI comparison, deployment methods, and next step learning paths.

---
## What We Are Building: A Research Assistant

In this episode, you build a small research assistant agent end to end. The user asks a question and the agent goes through these steps.

1. Analyze the question and identify what information is needed.
2. Use a search tool to gather relevant material.
3. Call a calculator tool when arithmetic is required.
4. Synthesize the gathered information into an answer.
5. Maintain conversation history to handle follow-up questions.

This example is small but it pulls together every concept covered in episodes 1 through 9: context setup, tool definition, workflow design, memory, error handling, evaluation, and operations.

---

## Prerequisites

Install the required packages.

```bash
pip install openai pydantic python-dotenv
```

Save your API key in a `.env` file.

```bash
OPENAI_API_KEY=sk-...
```

The full code lives in a single file `agent.py`. For learning purposes we use only the standard library and the OpenAI SDK with no external framework. We discuss frameworks in the last section.

---

## Step 1: Define the Tools

Tools are external functions the agent can call. Each tool needs a clear input schema and deterministic behavior.

```python
from typing import Any
from pydantic import BaseModel, Field
import json

class SearchInput(BaseModel):
    """Input schema for the search tool."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(3, description="Number of results to return")

class CalculatorInput(BaseModel):
    """Input schema for the calculator tool."""
    expression: str = Field(..., description="Python arithmetic expression")

def tool_search(query: str, top_k: int = 3) -> list[dict[str, str]]:
    """Fake search tool. In production this would call an external API."""
    fake_db = [
        {"title": "FastAPI Official Docs", "snippet": "FastAPI is a modern, fast Python web framework."},
        {"title": "FastAPI Performance Benchmarks", "snippet": "FastAPI delivers performance comparable to Node.js and Go."},
        {"title": "FastAPI vs Flask", "snippet": "FastAPI beats Flask in async support and automatic documentation."},
    ]
    return fake_db[:top_k]

def tool_calculator(expression: str) -> float:
    """Safe arithmetic. Plain eval is dangerous, so we use a restricted environment."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError(f"Disallowed characters in expression: {expression}")
    return eval(expression, {"__builtins__": {}}, {})
```

Build a tool registry. The agent reads this table to decide which tool to call.

```python
TOOLS = {
    "search": {
        "function": tool_search,
        "schema": SearchInput,
        "description": "Search for material by keyword.",
    },
    "calculator": {
        "function": tool_calculator,
        "schema": CalculatorInput,
        "description": "Evaluate an arithmetic expression.",
    },
}

def tools_to_openai_format() -> list[dict[str, Any]]:
    """Convert the registry to OpenAI Function Calling format."""
    result = []
    for name, info in TOOLS.items():
        result.append({
            "type": "function",
            "function": {
                "name": name,
                "description": info["description"],
                "parameters": info["schema"].model_json_schema(),
            },
        })
    return result
```

---

## Step 2: Implement Memory

A simple memory class for conversation history. It applies the sliding window pattern from episode 5.

```python
class ConversationMemory:
    """Sliding window conversation memory."""

    def __init__(self, system_prompt: str, max_messages: int = 20):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.messages: list[dict[str, Any]] = []

    def add(self, role: str, content: str, **extra: Any) -> None:
        """Append a message."""
        msg = {"role": role, "content": content, **extra}
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def to_openai(self) -> list[dict[str, Any]]:
        """Return messages in OpenAI Chat Completions format."""
        return [{"role": "system", "content": self.system_prompt}] + self.messages
```

`max_messages` caps the context length. For token-based compression, see episode 5.

---

## Step 3: The Agent Loop

The heart of the agent is the loop between LLM and tools. When the LLM emits a tool call, the result is fed back to the LLM. When there are no more calls, the agent returns the final answer.

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a research assistant.
Use the search and calculator tools to answer user questions.
Synthesize tool results into accurate, concise answers.
Say you do not know when you do not."""

class ResearchAgent:
    """Research assistant agent."""

    def __init__(self, model: str = "gpt-4o-mini", max_iterations: int = 5):
        self.model = model
        self.max_iterations = max_iterations
        self.memory = ConversationMemory(SYSTEM_PROMPT)

    def run(self, user_input: str) -> str:
        """Process a user question and return an answer."""
        self.memory.add("user", user_input)

        for iteration in range(self.max_iterations):
            response = client.chat.completions.create(
                model=self.model,
                messages=self.memory.to_openai(),
                tools=tools_to_openai_format(),
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                self.memory.add("assistant", msg.content or "")
                return msg.content or ""

            self.memory.add(
                "assistant",
                msg.content or "",
                tool_calls=[tc.model_dump() for tc in msg.tool_calls],
            )

            for tool_call in msg.tool_calls:
                result = self._execute_tool(tool_call)
                self.memory.add(
                    "tool",
                    json.dumps(result, ensure_ascii=False),
                    tool_call_id=tool_call.id,
                )

        return "Max iterations reached without producing an answer."

    def _execute_tool(self, tool_call: Any) -> Any:
        """Execute a tool safely."""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
            tool = TOOLS.get(name)
            if not tool:
                return {"error": f"Unknown tool: {name}"}
            validated = tool["schema"](**args)
            result = tool["function"](**validated.model_dump())
            return {"result": result}
        except Exception as exc:
            return {"error": str(exc)}
```

Key points:

- `max_iterations` prevents infinite loops.
- Tool execution is isolated inside `_execute_tool` so exceptions are caught.
- Inputs are validated with Pydantic schemas.
- Tool responses are also added to the message history.

---

## Step 4: Run and Test

A simple CLI to drive the agent.

```python
if __name__ == "__main__":
    agent = ResearchAgent()
    print("Research Assistant. Type 'quit' to exit.")
    while True:
        user_input = input("\nQuestion: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        try:
            answer = agent.run(user_input)
            print(f"\nAnswer: {answer}")
        except Exception as exc:
            print(f"\n[error] {exc}")
```

Sample run:

```text
Question: How does FastAPI perform?
Answer: FastAPI is a modern Python web framework with performance comparable to Node.js and Go.
The search results note it beats Flask in async support and automatic documentation.

Question: If I process 1000 requests at 0.5 seconds each, how many seconds total?
Answer: 1000 * 0.5 = 500 seconds.
```

Verify that follow-up questions retain context:

```text
Question: What if I process them 100 at a time concurrently?
Answer: Processing 1000 requests 100 at a time concurrently is 10x faster, so it takes 50 seconds.
```

---

## Step 5: Automated Evaluation

Apply the evaluation framework from episode 7. Build a small golden dataset and detect regressions.

```python
GOLD_CASES = [
    {
        "input": "What kind of framework is FastAPI?",
        "must_contain": ["Python", "web"],
    },
    {
        "input": "What is 100 plus 200?",
        "must_contain": ["300"],
    },
]

def run_eval() -> dict[str, Any]:
    """Run evaluation against the golden dataset."""
    passed = 0
    failures = []
    for case in GOLD_CASES:
        agent = ResearchAgent()
        answer = agent.run(case["input"])
        if all(kw in answer for kw in case["must_contain"]):
            passed += 1
        else:
            failures.append({"input": case["input"], "answer": answer})
    return {
        "total": len(GOLD_CASES),
        "passed": passed,
        "pass_rate": passed / len(GOLD_CASES),
        "failures": failures,
    }

if __name__ == "__main__" and os.getenv("RUN_EVAL"):
    result = run_eval()
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

Run with `RUN_EVAL=1 python agent.py` to see the evaluation output. Keyword matching is simple but sufficient for regression detection. For LLM-as-Judge evaluation, see episode 7.

---

## Framework Comparison: From Scratch vs LangGraph vs CrewAI

The example above is built from scratch. In production you usually want a battle-tested framework. The two leading options are LangGraph and CrewAI.

| Aspect | From Scratch | LangGraph | CrewAI |
| --- | --- | --- | --- |
| Learning curve | Low | Medium | Low |
| Flexibility | Very high | Very high | Medium |
| Multi-agent | Hand-written | Designed by you | Built-in |
| Graph visualization | None | Built-in | Limited |
| Streaming | Hand-written | Built-in | Built-in |
| Checkpoints | Hand-written | Built-in | Limited |
| Best fit | Learning, simple agents | Complex workflows | Role-based collaboration |

LangGraph example:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    iterations: int

def call_model(state: AgentState) -> AgentState:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=state["messages"],
        tools=tools_to_openai_format(),
    )
    msg = response.choices[0].message
    state["messages"].append(msg.model_dump())
    state["iterations"] += 1
    return state

def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if not last.get("tool_calls") or state["iterations"] >= 5:
        return END
    return "tools"

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", execute_tools_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
app = graph.compile()
```

LangGraph expresses workflows as nodes and edges. Complex branches and loops become explicit and inspectable.

CrewAI example:

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Gather material on the given topic",
    backstory="You are a meticulous researcher.",
    tools=[search_tool],
)

writer = Agent(
    role="Writer",
    goal="Write an answer from the gathered material",
    backstory="You are a writer who values clarity.",
)

task1 = Task(description="Research FastAPI", agent=researcher)
task2 = Task(description="Summarize the research", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
result = crew.kickoff()
```

CrewAI is strong at role-based multi-agent collaboration. Each agent gets a role and goal, and tasks are assigned across them.

Selection guide:

- Learning a single simple agent: build from scratch.
- Complex workflow with branches and checkpoints: LangGraph.
- Multiple agents collaborating with distinct roles: CrewAI.

---

## Preparing for Deployment

Moving learning code to production requires a few more pieces.

### FastAPI Wrapper

Expose the agent as an HTTP endpoint instead of a CLI.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    message: str

SESSIONS: dict[str, ResearchAgent] = {}

@app.post("/chat")
def chat(req: ChatRequest) -> dict[str, str]:
    agent = SESSIONS.setdefault(req.session_id, ResearchAgent())
    try:
        answer = agent.run(req.message)
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(500, detail=str(exc))
```

Each session gets its own agent instance to isolate conversations. In a real service you would externalize memory to Redis or a database.

### Environment Variables and Secrets

Never hardcode API keys. Add `.env` to `.gitignore` and use a secret manager (Vault, AWS Secrets Manager, etc.) in production.

### Container Image

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Use multi-stage builds to shrink image size. Also apply the operations checklist from episode 9.

---

## Common Mistakes

**1. Forgetting to prevent infinite loops.**
LLMs sometimes call the same tool repeatedly. Always set `max_iterations`.

**2. Not catching exceptions in tool execution.**
A single failing tool can crash the entire agent. Wrap every tool call in `try/except`.

**3. Rebuilding the system prompt on every call.**
Define the system prompt once and manage it through memory. Re-creating it per call breaks consistency.

**4. Changing prompts without evaluation.**
Prompt changes can cause regressions. Build even a tiny golden dataset and automate evaluation.

**5. Reaching for a framework first.**
LangGraph and CrewAI are powerful but carry learning costs. Build from scratch first to internalize the mechanics, then migrate to a framework.

---

## Next Steps

After finishing this series, the recommended learning path is:

1. **RAG integration**: Build a RAG agent that searches your internal documents. See the `vector-search-101` and `rag-deep-dive` series.
2. **Advanced function calling**: Add support for additional models like Anthropic and Gemini.
3. **Long-term memory**: Summarize conversations, store them in a vector database, and retrieve them in later sessions.
4. **Multi-agent systems**: Extend with the Coordinator-Worker pattern from episode 6.
5. **Production operations**: Apply the observability and cost tracking from episode 9 to a real deployment.

This series is the starting point of agent development. Begin with small agents and grow complexity gradually. Every agent ultimately follows the same pattern: define tools, manage context, stabilize the loop, and automate evaluation.

---

## Key Takeaways

- Building an agent from scratch teaches the inner mechanics of the LLM-tool loop, memory, and error handling.
- `max_iterations` and `try/except` are mandatory safety nets for every agent loop.
- Tools should validate inputs with Pydantic schemas and behave deterministically.
- Evaluation can start with a small golden dataset and still catch real regressions.
- Build from scratch first to internalize the principles, then scale with frameworks like LangGraph or CrewAI.

<!-- toc:begin -->
## In this series

- [What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [Context Engineering](./02-context-engineering.md)
- [Tool Use Fundamentals](./03-tool-use-fundamentals.md)
- [Agent Workflow Design](./04-agent-workflow-design.md)
- [Memory and State](./05-memory-and-state.md)
- [Multi-Agent Systems](./06-multi-agent-systems.md)
- [Agent Evaluation](./07-agent-evaluation.md)
- [Error Handling and Reliability](./08-error-handling-reliability.md)
- [Production Operations](./09-production-operations.md)
- **Building Your First Agent (current)**

<!-- toc:end -->

---

## References

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Building Effective Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)

Tags: AI Agent, LLM, Tool Use, Python
