---
title: "LangGraph 101 (1/6): LangGraph introduction and graph basics"
series: langgraph-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangGraph
- Agent
- Python
- LLM
last_reviewed: '2026-05-14'
seo_description: StateGraph is a blueprint that turns node functions plus transition
  rules into an executable workflow over shared state.
---

# LangGraph 101 (1/6): LangGraph introduction and graph basics

When teams wire their first LangChain-style agent together, they usually hit the same wall. Change the prompt, and the answer changes. Change one helper function, and some requests improve while others get worse. The system still runs, but nobody can explain clearly why it behaved the way it did. What looks like “the model being flaky” is often just hidden control flow.

That problem gets louder once you start operating the thing instead of demoing it. One request finishes cleanly, another calls the same tool twice, a third cannot be reproduced because the intermediate state never got captured anywhere. Teams I've worked with often describe this as “the agent feels unstable,” but in production the deeper issue is usually simpler: the workflow is real, yet the workflow is not visible in the code structure.

This is the first article in the LangGraph 101 series. Here I want to frame LangGraph not as a convenient agent utility, but as a **graph runtime where state moves explicitly from step to step**. That is the mental shift that matters. **LangGraph is less about writing clever prompts and more about refusing to hide state transitions.**

Once that click happens, the later pieces start to make more sense. Checkpointing stops looking like “memory magic” and starts reading like state snapshot storage. Conditional edges stop looking like a dressed-up `if` statement and start reading like runtime routing rules. Tool loops change too. Teams that separate node, edge, and state tend to debug by tracing stages. Teams that keep thinking in one long chain usually jump straight to the final string.

I've seen that difference decide whether LangGraph feels obvious or frustrating. Memorizing `StateGraph`, `add_node()`, `add_edge()`, and `invoke()` is not the same thing as understanding why a graph is easier to operate. The real win is learning to read where state changes, why the next step was selected, and which stage to inspect when the final answer looks wrong.

![Basic graph flow from START to END](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/01/01-01-minimal-runnable-example.en.png)
*Basic graph flow from START to END*
> LangGraph is not valuable because the graph has a shape; it is valuable because state changes and next-step choices stay visible in code.

## Questions to Keep in Mind

- Why is LangGraph easier to reason about as an explicit state machine than as a longer chain?
- What responsibilities do nodes, edges, and state each carry in the execution flow?
- After running the first graph, which state values should be checked before trusting the final prose?

## Why this structure matters

If you describe LangGraph only as “a graph-based agent framework,” the description is technically correct and practically weak. The more useful answer is this: once an agent has multiple steps, the team needs a structure that can explain itself. Not eventually. Immediately.

Imagine a flow that receives a request, chooses a topic, builds an outline, and assembles a final answer. You can absolutely write that as a sequence of ordinary functions. It will run. But the moment someone asks, “Why did this step happen first?”, “Which stage changed this field?”, or “Where should we debug when the final answer looks off?”, the abstraction starts leaking. In production, that loss of explainability turns directly into maintenance cost.

I have seen teams underestimate this because the first prototype is small. A short chain feels fine while there is only one route and one obvious output. Then a tool call gets added, then conversation state, then branching, and suddenly the workflow that used to fit in one person’s head becomes a guessing game. LangGraph pays off right there, because it leaves the flow in the structure instead of leaving it in your memory.

So the purpose of this post is not merely to get a first graph to execute. It is to make the state-machine lens feel natural, because that lens is what makes checkpointing, branching, and tool loops feel like extensions of one system rather than unrelated features.

---

## Reading LangGraph as a State Machine

The most useful sentence I know for LangGraph is this: **LangGraph is an explicit state machine.** I keep coming back to that wording because it stays useful even as the workflow grows. Nodes read state and update part of it. Edges define how execution moves forward. `invoke()` drives the transitions and gives you the final state after the graph is done.

Many introductions phrase LangGraph as “a way to compose chains into a graph.” That is not wrong, but it is not enough. It explains shape, not operational value. The practical difference is not the number of calls. The practical difference is that **state and transitions are made explicit instead of implied.**

At the simplest level, the model looks like this.

| Component | What it means in LangGraph | Why it matters in practice |
| --- | --- | --- |
| **State** | The shared data contract across the graph | You can trace which stage read or wrote which field |
| **Node** | A unit of work that updates part of state | You can isolate responsibility and shrink test scope |
| **Edge** | The rule that chooses the next step | You can keep execution order and branch logic visible |
| **START / END** | The graph entry and exit points | You can make lifecycle boundaries explicit |
| **invoke()** | The execution entry point that takes initial state and returns final state | You validate the full workflow result, not just one function output |

That table matters because it answers the questions people actually ask while operating agents. Which node chose the wrong route? Why did the workflow stop there? When did the state first drift away from expectation? Those are not model-quality questions. They are Node, Edge, and State questions.

In practice, I see two kinds of teams. One group compares only the final output string. The other inspects state fields and transition order together. The first group debugs symptoms. The second group debugs causes. LangGraph is valuable because it nudges you toward the second habit.

---

## Minimal runnable example

Start with the smallest graph that still shows the core idea. A user request comes in, one node chooses a topic, another builds an outline, and a final node assembles the answer text. The example is deliberately plain, but it already contains the parts that matter later.

```python
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

class ArticleState(TypedDict):
    user_request: str
    topic: str
    outline: list[str]
    answer: str

def choose_topic(state: ArticleState) -> ArticleState:
    request = state["user_request"].lower()
    if "checkpoint" in request:
        topic = "checkpoints"
    elif "tool" in request:
        topic = "tool calling"
    else:
        topic = "graph basics"
    return {"topic": topic}

def build_outline(state: ArticleState) -> ArticleState:
    outline = [
        f"Define {state['topic']}",
        "Show the nodes in the graph",
        "Explain how invoke() runs the graph",
    ]
    return {"outline": outline}

def write_answer(state: ArticleState) -> ArticleState:
    bullet_lines = "\n".join(f"- {item}" for item in state["outline"])
    answer = (
        f"Request: {state['user_request']}\n"
        f"Chosen topic: {state['topic']}\n"
        "Teaching outline:\n"
        f"{bullet_lines}"
    )
    return {"answer": answer}

def build_graph():
    graph = StateGraph(ArticleState)
    graph.add_node("choose_topic", choose_topic)
    graph.add_node("build_outline", build_outline)
    graph.add_node("write_answer", write_answer)

    graph.add_edge(START, "choose_topic")
    graph.add_edge("choose_topic", "build_outline")
    graph.add_edge("build_outline", "write_answer")
    graph.add_edge("write_answer", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke(
        {
            "user_request": "Explain how a LangGraph StateGraph works.",
            "topic": "",
            "outline": [],
            "answer": "",
        }
    )
    print(result["answer"])
```

This snippet is doing more than demonstrating syntax. From an operating perspective, it already proves three things. First, the state contract is centralized in `ArticleState`, so you can see where each field is expected to come from. Second, the `choose_topic -> build_outline -> write_answer` sequence is fixed in the graph rather than hidden inside nested calls. Third, the result of `invoke()` tells you that what comes back is not one node’s output, but the state after the whole transition path completes.

That is why I prefer starting with examples this small. If you introduce an LLM call or a tool loop too early, the real lesson gets buried. Here the only moving part is state transition itself. Once that is clear, memory, branching, and tools feel like additional structure on top of the same model rather than a different model altogether.

You can keep the runnable-file path around if you want, but the more important point is this: the code is your first exercise in reading a graph as a state machine rather than as function composition. Small examples are where that reading habit becomes easy enough to practice.

---

## Validate the full state, not just the final prose

The fastest way to miss the real lesson in this example is to print only the final answer string. A graph becomes much easier to reason about once you verify the final state object directly.

```python
app = build_graph()
result = app.invoke(
    {
        "user_request": "Explain how a LangGraph StateGraph works.",
        "topic": "",
        "outline": [],
        "answer": "",
    }
)

assert result["topic"] == "graph basics"
assert result["outline"] == [
    "Define graph basics",
    "Show the nodes in the graph",
    "Explain how invoke() runs the graph",
]
assert "Chosen topic: graph basics" in result["answer"]

print(result)
```

**Expected output:**

```text
{
  'user_request': 'Explain how a LangGraph StateGraph works.',
  'topic': 'graph basics',
  'outline': [
    'Define graph basics',
    'Show the nodes in the graph',
    'Explain how invoke() runs the graph'
  ],
  'answer': 'Request: Explain how a LangGraph StateGraph works.\n...'
}
```

That check matters because it keeps `invoke()` from being mentally reduced to “the last function call.” You can see directly that `topic`, `outline`, and `answer` all survive as graph state after execution finishes.

---

## How to narrow down the first failures

Most early failures here are not syntax problems. They come from reading the structure incorrectly.

1. **Keep the initial state explicit.**  
   If the call site stops initializing fields such as `topic`, `outline`, and `answer`, the graph contract becomes harder to inspect and easier to misuse.

2. **Inspect upstream fields before patching the last node.**  
   When the final prose looks wrong, the cause is often that `choose_topic()` chose poorly or `build_outline()` returned the wrong structure.

3. **Do not let one node quietly absorb another node’s job.**  
   Once `choose_topic()` starts building outlines or `build_outline()` starts formatting final prose, the graph still runs but the responsibility boundaries stop explaining themselves.

This is the operational habit I want readers to leave with: inspect the state contract, inspect which fields each node owns, then inspect the final state object. That order turns “the model feels flaky” into a much more concrete debugging question.

---

## What to notice in this code

Do not try to absorb the entire file at once. On a first pass, there are three things worth locking in.

![Request to state field mapping](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/01/01-02-what-to-notice-in-this-code.en.png)

*Request to state field mapping*

- `StateGraph(ArticleState)` declares the shared schema for the whole workflow.
- Each node receives full state and returns only the fields it wants to update.
- `START -> choose_topic -> build_outline -> write_answer -> END` makes execution order explicit in code.

The first point is the state contract. Just by reading `ArticleState`, you can infer what the graph is supposed to move around. In production, I have seen debugging cost climb quickly once state definitions get scattered across helper layers. When the contract lives in one place, questions like “who is responsible for this field?” become much cheaper to answer.

The second point is how nodes return updates. A LangGraph node does not need to reconstruct the entire state object every time. It should return the part it is responsible for changing. That sounds small, but it keeps responsibility boundaries sharp and makes it much easier to see where a specific update came from.

The third point is the edge structure. In ordinary chain code, execution order often lives in your head. In a graph, the order is embedded in the structure. When you are operating a workflow and need to ask, “Why did this stage run before that one?”, that visibility is not cosmetic. It is operational leverage.

---

## Where engineers get confused

The first mistakes people make here are rarely syntax mistakes. They are mental-model mistakes. Three confusions come up over and over.

![Execution flow from definition to invoke](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/01/01-03-where-engineers-get-confused.en.png)

*Execution flow from definition to invoke*

- A node does not need to reconstruct the entire state object. Returning changed fields is enough.
- `StateGraph` is not limited to DAG-style pipelines. The same abstraction can grow into loops and branches.
- `invoke()` returns the final state, not just the output of the last node.

I've seen the same scene play out more than once. The graph is tiny. `START -> choose_topic -> build_outline -> write_answer -> END`. The result looks wrong, and everyone immediately patches the last node. “The final answer string looks off, so `write_answer()` must be the problem.” But the actual defect is often upstream: `topic` was chosen incorrectly, or `outline` never got shaped the way the last node expected.

That is the first failure pattern worth naming: **The Implicit State Anti-pattern**. The team looks only at the final output and does not inspect how state changed on the way there. Once that habit sets in, the bug is created in one place and repaired in another. Debugging takes longer, local patches pile up, and the structure gets more brittle right before you add branching or checkpointing.

The second one is **The Full Rewrite State Anti-pattern**. Engineers assume a node is “safer” if it reconstructs the whole state on every pass. In practice, that often widens the blast radius of small changes. A node that only needed to update one field ends up rewriting everything, and now stale defaults or accidental resets become part of normal execution. In production, those are the kinds of mistakes that stay invisible until the graph grows one more stage.

The last confusion matters just as much: reading `invoke()` as “the last function call” instead of “the final state snapshot.” If you choose the first model, you stop validating intermediate state. If you choose the second, fields like `topic`, `outline`, and `answer` become first-class debugging checkpoints. That distinction pays off immediately once the workflow gains memory, branching, or tool loops.

Teams I've worked with tend to stabilize faster once they adopt a simple habit: inspect state transitions before you inspect the final prose. LangGraph is strong precisely because the flow does not have to stay hidden. The more you lean into that, the less mysterious agent behavior feels while you are operating it.

---

## First operating checklist

If you check these items while the graph is still small, the next steps—checkpointing and branching—become much less fragile.

- [ ] Does state contain only fields that another node actually needs
- [ ] Are node names descriptive enough to read the flow quickly
- [ ] Is each node limited to the fields it truly owns
- [ ] Is the path from `START` to `END` free of unnecessary steps
- [ ] Does the team know which state field to inspect first when the final answer looks wrong

The point of this checklist is not just “does it run?” It is “does it explain itself?” Early graphs need both. Over time, lack of explainability is usually what gets expensive first.

---

## How senior teams think about this in practice

This may sound early for an introductory chapter, but I think it is healthy to attach operating questions to the very first graph. Questions like: if this node becomes an external API call later, where will retries live? If this state field gets checkpointed, will it still mean the same thing on the next turn? If this path grows into conditional routing, will the current node names still make sense?

The point is not to overengineer a toy example. It is the opposite. LangGraph is useful because it lets you expose tomorrow’s structure in a very small form today. Once the habit of separating node, edge, and state is in place, adding memory or routing feels like extending one design instead of escaping into a new one.

In production, I have seen strong teams review the state contract before they review the prompt. That is not because prompts do not matter. It is because hidden flow is harder to unwind than a weak prompt. The operating lesson worth carrying out of this first post is simple: **the base unit of LangGraph is not answer generation, but state-transition design.**

---

## Summary: LangGraph is not a chain assembler, but a runtime that exposes state transitions

When people first encounter LangGraph, APIs like `add_node()` and `add_edge()` naturally stand out. That is fine. But the longer you operate these workflows, the less the method names matter and the more the real questions matter: what state survives, which rule selected the next step, and where should you look when behavior drifts.

The core ideas from this post are straightforward. First, `StateGraph` is not just a bundle of functions. It is a structure that places execution rules on top of a shared state contract. Second, a node is not where you rewrite the whole world; it is where you update the fields you actually own. Third, `invoke()` gives you the final state after the graph runs, not merely the output of one last function.

Those ideas matter because everything else in the series depends on them. Checkpointing is how you persist that state across calls. Conditional edges are how you choose the next node from that state. Tool loops are what happen when state and transitions repeat under controlled rules. If the state-machine view does not click here, later topics feel like feature accumulation. If it does click here, later topics feel like one model being extended carefully.

I do not judge a first LangGraph lesson by whether the code ran once. I judge it by whether someone can explain the graph after reading it. What state exists, which node changes it, why the order is what it is, and where you would debug if the answer looked wrong. If the reader can do that, the foundation is doing its job.

In the next post, we will keep that state alive across calls with checkpoints and `thread_id`. That is where this small example starts showing why it was the right starting point.

---

## Operating checklist

- [ ] Is the state schema easy to read at a glance
- [ ] Can each node’s responsibility be described in one sentence
- [ ] Does the team validate intermediate state, not just the final answer
- [ ] Would this field structure still make sense once checkpointing is added
- [ ] Would the current node names and edges still hold up once branching or loops appear

## Answering the Opening Questions

- **Why is LangGraph easier to reason about as an explicit state machine than as a longer chain?**
  - A chain mostly extends order; LangGraph exposes where state changes and how the next step is chosen, which makes failures easier to localize.
- **What responsibilities do nodes, edges, and state each carry in the execution flow?**
  - Nodes read and update state, edges decide the next node, and state is the shared execution record across the graph.
- **After running the first graph, which state values should be checked before trusting the final prose?**
  - Check input fields, intermediate fields, selected paths, and accumulated messages before trusting the final text.

<!-- toc:begin -->
## In this series

- **LangGraph 101 (1/6): LangGraph introduction and graph basics (current)**
- LangGraph 101 (2/6): State management and checkpoints (upcoming)
- LangGraph 101 (3/6): Conditional edges and branching (upcoming)
- LangGraph 101 (4/6): Tool-calling agents (upcoming)
- LangGraph 101 (5/6): Multi-agent systems (upcoming)
- LangGraph 101 (6/6): Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

### Official Documentation
- [LangGraph concepts: low level](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [StateGraph API reference](https://langchain-ai.github.io/langgraph/reference/graphs/)
- [LangGraph introduction tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

### Source code and examples
- [langchain-ai/langgraph GitHub repository](https://github.com/langchain-ai/langgraph)
- [LangGraph quickstart](https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot/)

### Related Series
- [LangChain 101](../../langchain-101/en/01-lcel-runnable-basics.md) — covers the Runnable and LCEL primitives that LangGraph invokes inside each node. Drop down to it whenever the question is not about the graph itself but about what actually executes inside one of its nodes.
- [AI Agent 101](../../ai-agent-101/en/)

---

Tags: LangGraph, Agent, Python, LLM
