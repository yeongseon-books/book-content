---
title: "LangGraph 101 (2/6): State management and checkpoints"
series: langgraph-101
episode: 2
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
seo_description: A checkpointer snapshots graph state so the next invocation can continue
  from the same conversation timeline instead of starting from zero.
---

# LangGraph 101 (2/6): State management and checkpoints

You can get away with hand-waving state when an agent handles one request and disappears. That stops working the moment the workflow has to survive a second turn. Now it matters what the user said earlier, which tool results are still relevant, how many turns already happened, and whether the graph can resume from something real instead of pretending it remembers.

The operational version of this problem is harsher. One session resumes correctly, another loses context after a process restart, and a third retries after a partial failure by repeating work it already paid for. In production, a long-running agent without checkpoints is often less dangerous because it fails, and more dangerous because it cannot recover from failure in a disciplined way.

Once tool calls and multi-turn behavior enter the picture, the naïve fallback—“just resend the last user message”—breaks down quickly. Message accumulation rules vanish. Turn counters vanish. Summary state vanishes. External tool results vanish. Teams I've worked with often discover too late that what looked like a harmless retry path was actually a brand-new execution wearing the clothes of a resumed session.

This is the 2nd post in the LangGraph 101 series. Here I want to frame checkpointing not as a friendly memory feature, but as a **runtime layer that saves state and lets execution continue from the same conversation timeline**. That distinction matters. **State is the graph’s single source of truth, and a checkpoint is the mechanism that preserves that truth across calls.**

Once that model is clear, the rest of the graph speaks the same language. Conditional edges stop looking like isolated branching logic and start looking like routing decisions made from saved state. Tool loops become repeated state transitions on top of the same timeline. If checkpointing remains a fuzzy “memory-like thing,” `thread_id`, merge rules, replay, and time travel all stay fuzzier than they should.

![Resume flow through thread_id](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/02/02-01-minimal-runnable-example.en.png)
*Resume flow through thread_id*
> State is the contract for the current run; a checkpoint is the storage boundary that lets the next call resume that contract.

## Questions to Keep in Mind

- What bugs become easier to avoid when state is the single source of truth in LangGraph?
- How is a checkpoint different from in-memory state, and when does it become a recovery boundary?
- What limit appears if the MemorySaver example is mistaken for production storage?

## Why this structure matters

If checkpointing is explained only as “memory for a conversation,” you get at most half the value. The stronger reason is recovery and reproducibility. The moment an agent stops being single-shot and starts continuing across invocations, state persistence becomes part user experience and part reliability engineering.

Suppose a user names their project in the first call and asks, “What did I say my project was about?” in the second. If no state was saved, maybe the answer quality simply drops. But in real systems there are usually tool calls, accumulated messages, review stages, and external side effects in the mix. Then the cost is no longer just weaker memory. It becomes duplicate work, incorrect recovery, and wasted spend.

I have seen teams repeat the same recovery mistake when no checkpoint exists. A failed request is “retried” by resending only the latest user input, and someone asks afterward why the behavior changed. By then the missing data is not a single sentence. It is the whole execution context: earlier turns, routing evidence, turn count, and sometimes the outputs of expensive tools.

That is why the goal of this post is not simply to show how `MemorySaver` works. The more important goal is to make it obvious why adding checkpointing turns a graph from a one-off function call into a resumable system.

---

## Separating State from Checkpoints

The sentence worth anchoring on is this: **State is the graph’s single source of truth, and a checkpoint is the storage layer that preserves it.** I keep using that wording because it captures persistence in a way that stays useful once workflows become more operationally serious.

Many first-time readers think of a checkpointer as “the option that adds memory.” In practice, that framing is too soft. A checkpointer saves a state snapshot and later feeds that snapshot back into the graph when the same session identifier (`thread_id`) returns. That is not memory magic. It is a resumable execution context.

At the simplest level, the model looks like this.

| Component | Role | Why it matters in practice |
| --- | --- | --- |
| **State** | Shared data such as messages, counters, and accumulated outputs | You can validate what must still exist at each point in time |
| **Checkpoint** | A saved snapshot of state at a particular point | It becomes the starting point for resume and reproducible debugging |
| **thread_id** | The key that identifies one conversation timeline | It prevents unrelated user sessions from bleeding into each other |
| **merge rule** | The rule that decides how new state combines with saved state | It keeps message accumulation and counter updates from being treated the same way |
| **get_state()** | The inspection entry point for currently saved state | It lets you verify persisted data instead of guessing about it |

That table matters because these are the questions operators actually ask. Why did the messages disappear? Why did one user’s session leak into another? Why is the turn count off after a retry? Why did the repeated request call the tool a different number of times? Those are usually state, checkpoint, merge-rule, and identity questions long before they are model-quality questions.

In practice, I look for three things first when a graph uses checkpoints: how much state is persisted, how trustworthy the session key is, and whether merge behavior matches the shape of each field. Once you can answer those three, the system stops feeling like “it remembers” or “it does not remember” and starts feeling understandable.

---

## Minimal runnable example

Start with the smallest possible resume example. The first invocation saves the user message. The second invocation uses the same `thread_id` to continue from the earlier conversation state. Then `get_state()` is used to inspect what was actually persisted.

```python
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    turn_count: int

def assistant(state: ChatState) -> ChatState:
    human_messages = [msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)]
    latest = human_messages[-1]
    remembered = human_messages[:-1]
    memory_line = "No earlier user turns saved yet."
    if remembered:
        memory_line = f"Earlier user turns: {', '.join(remembered)}"
    reply = AIMessage(
        content=(
            f"Turn {state.get('turn_count', 0) + 1}. "
            f"Latest user message: {latest}. {memory_line}"
        )
    )
    return {"messages": [reply], "turn_count": state.get("turn_count", 0) + 1}

def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("assistant", assistant)
    graph.add_edge(START, "assistant")
    graph.add_edge("assistant", END)
    return graph.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    app = build_graph()
    config = {"configurable": {"thread_id": "memory-demo"}}

    first = app.invoke(
        {"messages": [HumanMessage(content="My project is about LangGraph.")], "turn_count": 0},
        config=config,
    )
    print("First reply:")
    print(first["messages"][-1].content)

    second = app.invoke(
        {"messages": [HumanMessage(content="What did I say my project was about?")]},
        config=config,
    )
    print("\nSecond reply after resume:")
    print(second["messages"][-1].content)

    snapshot = app.get_state(config)
    print(f"\nSaved message count: {len(snapshot.values['messages'])}")
    print(f"Saved turn count: {snapshot.values['turn_count']}")
```

This is a small example, but it proves three operationally important things. First, `compile(checkpointer=MemorySaver())` places persistence inside the graph structure instead of leaving it as an implied behavior outside the graph. Second, the second `invoke()` can submit only the new message because the same `thread_id` pulls earlier state back into the execution path. Third, `get_state()` lets you inspect real saved values instead of assuming persistence happened.

That is why I like examples shaped like this. They force checkpointing to read like a verifiable storage layer instead of a vague metaphor about memory. You can see what survives between the first and second invocation, which values accumulate, which values update, and where the session boundary actually lives.

There is another useful contrast here. This code makes the difference visible between “a function that looks conversational” and “a system that can genuinely resume.” That distinction matters a lot once branching and tool loops arrive, because reliable recovery depends on it.

---

## Verify what was actually persisted

The important checkpointing question is not “did the code run?” but “did the graph really save the state we think it saved?” The easiest way to answer that is to inspect the stored snapshot directly after the second turn.

```python
app = build_graph()
config = {"configurable": {"thread_id": "memory-demo"}}

app.invoke(
    {"messages": [HumanMessage(content="My project is about LangGraph.")], "turn_count": 0},
    config=config,
)
app.invoke(
    {"messages": [HumanMessage(content="What did I say my project was about?")]},
    config=config,
)

snapshot = app.get_state(config)

assert snapshot.values["turn_count"] == 2
assert len(snapshot.values["messages"]) == 4
assert any("LangGraph" in message.content for message in snapshot.values["messages"])

print(snapshot.values)
```

**Expected output:**

```text
{
  'messages': [
    HumanMessage(content='My project is about LangGraph.'),
    AIMessage(content='Turn 1. Latest user message: My project is about LangGraph. ...'),
    HumanMessage(content='What did I say my project was about?'),
    AIMessage(content='Turn 2. Latest user message: What did I say my project was about?. Earlier user turns: My project is about LangGraph.')
  ],
  'turn_count': 2
}
```

That small check is doing real operational work. It confirms that message history accumulated, that `turn_count` advanced, and that the graph is persisting a session timeline instead of merely returning nice-looking answers.

---

## The limits of the in-memory example

`MemorySaver` is a good teaching tool, but it also helps to say out loud what it does **not** guarantee.

- **A process restart clears the in-memory checkpoint store.**  
  That is fine for learning. It is not the final persistence shape for a long-lived service.

- **A weak `thread_id` strategy still produces confusing recovery.**  
  If session keys are unstable or too broad, the graph may either fail to resume or resume the wrong conversation.

- **Different fields need different merge behavior.**  
  `messages` should accumulate. `turn_count` should overwrite with the latest value. Treating every field the same way produces graphs that “remember” in a shallow sense while still corrupting the timeline.

That is why I encourage readers to ask two questions together: is the saved value correct, and would this storage pattern still hold up under the service boundary we actually care about? `get_state()` answers the first one immediately. Session-key and storage design answer the second.

---

## What to notice in this code

Do not try to interpret every line at once. Three observations matter first.

![Message accumulation and turn_count updates](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/02/02-02-what-to-notice-in-this-code.en.png)

*Message accumulation and turn_count updates*

- `add_messages` appends new messages instead of overwriting history.
- `graph.compile(checkpointer=MemorySaver())` attaches persistence in one place.
- The second `invoke()` sends only the new message, but the same `thread_id` restores prior state automatically.

The first point is merge behavior for messages. `messages` is not an overwrite field. It is an accumulation field. That is why `add_messages` matters. In production, I have seen teams treat message history like an ordinary value, only to discover that the graph resumed while the conversation itself quietly disappeared.

The second point is where checkpointing gets attached. `MemorySaver()` is not a decorative helper. It is a runtime layer that makes the graph resumable across invocations. Because the persistence layer is visible in the structure, you can answer an important question directly from the code: is this graph actually designed to resume?

The third point is the session key. Give the graph the same `thread_id`, and the prior state comes back. That sounds simple, but operating systems built on this idea is not simple at all. Weak keys mix sessions. Overly volatile keys prevent anything from resuming. Checkpoint design quickly becomes both state-store design and session-boundary design.

---

## Where engineers get confused

The most common mistake in checkpointing is believing that “saved” automatically means “safe.” In practice, what matters more is **what gets merged, how it gets merged, and under which key it survives.**

![Checkpointer and merge rule relationships](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/02/02-03-where-engineers-get-confused.en.png)

*Checkpointer and merge rule relationships*

- A checkpointer does not automatically merge every field the way you want.
- A weak `thread_id` strategy can mix sessions from different users.
- Fields that should accumulate, such as messages, need explicit modeling in state.

The failure mode I see most often is **The Stateless Replay Anti-pattern**. A team implements retry behavior without checkpoints and simply resends the latest user input. At first that feels efficient. In reality, the replay is missing earlier messages, turn count, tool outputs, and the evidence that shaped earlier branch decisions. It looks like recovery from the outside, but it is often a completely new execution path.

Why is that dangerous in production? First, reproducibility collapses because what looks like “the same session” is now running on different state. Second, once external APIs or tools are involved, duplicate work and duplicate cost become normal. Third, after a partial failure, the team no longer has a principled place to resume from, so “start over” becomes the only fallback.

Another trap is applying one merge strategy to every field. `messages` should accumulate. `turn_count` should update to the latest value. Treat both the same way, and you either lose history or keep far more state than the workflow really needs. Time behaves differently for different fields, and the state model has to reflect that.

Teams I've worked with tend to stabilize checkpointing once they classify fields deliberately: accumulating fields, overwrite fields, derived fields, and fields that should not be persisted at all. If you wait until after the checkpointer is attached to think about merge rules, you are already late. The state model itself is part of the recovery strategy.

---

## First operating checklist

Once checkpointing exists, these stop being feature checks and become stability checks.

- [ ] Do you have a clear `thread_id` rule for session identity
- [ ] Did you model accumulating fields separately from overwrite fields
- [ ] Did the team agree on which state should be reused on retry and which should be recalculated
- [ ] Did you verify real saved values with `get_state()` after another turn
- [ ] Did you test whether the same timeline survives a process restart

The key question here is not “does it remember?” It is “can it recover, and can we explain how it recovered?” A checkpointer is not just a convenience feature. It is also a fault-handling boundary.

---

## How senior teams think about this in practice

The moment checkpointing is attached, the graph stops being a set of one-off calls and becomes a session system. That changes the operating questions. Instead of asking only whether the answer was good, you start asking whether the session key is stable, whether this field should really be persisted, and where the right resume point would be if you needed something closer to time travel than to replay.

In practice, I evaluate checkpointing together with storage design. An in-memory example is a good starting point, but real services have process restarts and multi-instance behavior to think about. Where state lives affects cost and performance, but it also determines how strong your recovery guarantees can honestly be.

Another distinction worth keeping sharp is replay versus time travel. Replay may mean sending the same input again. Time travel is closer to restarting from a specific saved state boundary. If those ideas get blurred together, debugging, experimentation, and operational recovery all get blurrier too. Adding checkpointing does not magically give you full time travel, but it does create the precondition for it.

I have seen strong teams review the state persistence strategy before they review the prompt. That is not because prompts do not matter. It is because broken session boundaries and broken merge rules are much harder to unwind later. The practical lesson from this chapter is simple: **long-term agent quality depends on a recovery strategy before it depends on a polished conversational surface.**

---

## Summary: checkpointing is not a memory feature, but the layer that makes a graph resumable

Checkpointing is easy to describe as “the feature that remembers prior conversation.” That explanation is not wrong, but it is too weak for operational thinking. The stronger explanation is that checkpointing stores graph state and reloads it under the same session identity so execution can continue instead of pretending to restart cleanly.

The core ideas from this post are straightforward. First, State is the graph’s single source of truth. Second, a Checkpoint preserves that State across invocations. Third, `thread_id` and merge behavior decide not only whether the graph “remembers,” but how reliably one session recovers from interruption or failure.

That matters immediately for the next chapter on conditional edges. Routing decisions are made from current state. If the saved state is missing, mixed, or merged incorrectly, routing quality will drift with it. Checkpointing is not a side topic about persistence. It is part of the foundation for reliable branching.

When I look at a checkpointed graph, I do not first ask whether it feels conversational. I ask whether failure is now explainable. Can we say what was stored, under which key, and which fields were accumulated versus overwritten? If the answer is yes, the foundation is in the right place.

In the next post, we will use that saved state to decide which node should run next with conditional edges. That is where the relationship between persistence and routing becomes much more concrete.

---

## Operating checklist

- [ ] Is `thread_id` mapped consistently to a user session or conversation unit
- [ ] Did you separate fields that should be persisted from fields that should not
- [ ] Did the team define replay and time travel as different concepts
- [ ] Did you document the resume point after a partial failure
- [ ] Do you have a procedure for inspecting saved state with `get_state()`

## Answering the Opening Questions

- **What bugs become easier to avoid when state is the single source of truth in LangGraph?**
  - Centralized state reduces missing messages, mismatched fields, and lost intermediate results because nodes no longer invent separate local truth.
- **How is a checkpoint different from in-memory state, and when does it become a recovery boundary?**
  - A checkpoint is not the in-run memory itself. It is the saved boundary that lets the graph reload state across calls, failures, and multi-turn sessions.
- **What limit appears if the MemorySaver example is mistaken for production storage?**
  - MemorySaver is an in-process teaching tool. It does not guarantee restart safety, multi-instance coordination, or long-term retention; production graphs need an external saver.

<!-- toc:begin -->
## In this series

- [LangGraph 101 (1/6): LangGraph introduction and graph basics](./01-graph-basics.md)
- **LangGraph 101 (2/6): State management and checkpoints (current)**
- LangGraph 101 (3/6): Conditional edges and branching (upcoming)
- LangGraph 101 (4/6): Tool-calling agents (upcoming)
- LangGraph 101 (5/6): Multi-agent systems (upcoming)
- LangGraph 101 (6/6): Completing LangGraph (upcoming)

<!-- toc:end -->

---

## References

### Official Documentation
- [LangGraph persistence guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [MemorySaver reference](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [Working with messages in graph state](https://langchain-ai.github.io/langgraph/concepts/low_level/#working-with-messages-in-graph-state)

### Source code and examples
- [LangGraph checkpoint package source](https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint)
- [LangGraph memory tutorial](https://langchain-ai.github.io/langgraph/tutorials/get-started/3-add-memory/)

### Related Series
- [LangGraph introduction and graph basics](./01-graph-basics.md)
- [LangChain 101](../../langchain-101/en/)

---

Tags: LangGraph, Agent, Python, LLM
