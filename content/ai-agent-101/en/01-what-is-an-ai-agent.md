---
title: What Is an AI Agent?
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

# What Is an AI Agent?

> AI Agent 101 series (1/10)

When most people first encounter LLMs, they frame them as systems that answer questions well. That mental model feels sufficient in a chat window, but it starts to break the moment you ask the model to finish real work on your behalf.

Classifying customer tickets, creating follow-up tasks, and drafting replies all require more than polished text generation. The model has to interact with external systems, inspect results, and decide what to do next, which is exactly where the line between a chatbot and an Agent becomes useful.

This is the first post in the AI Agent 101 series. Here we build the basic mental model for Agents by separating them from chatbots and walking through the observe → think → act → check loop.

---

<!-- a-grade-intro:begin -->

## Key Questions

- What essentially separates a chatbot from an agent?
- Why is the Observe → Think → Act → Check loop necessary?
- What is the minimum bar for calling something an agent?
- What scope of agents does this series cover?

<!-- a-grade-intro:end -->

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

<!-- toc:begin -->
## In this series

- **What Is an AI Agent? (current)**
- Context Engineering (upcoming)
- Tool Use Fundamentals (upcoming)
- Agent Workflow Design (upcoming)
- Memory and State (upcoming)
- Multi-Agent Systems (upcoming)
- Agent Evaluation (upcoming)
- Error Handling and Reliability (upcoming)
- Production Operations (upcoming)
- Building Your First Agent (upcoming)

<!-- toc:end -->

---

## References

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain Agents - conceptual guide](https://python.langchain.com/docs/concepts/agents/)
- [OpenAI - Function calling guide](https://platform.openai.com/docs/guides/function-calling)

Tags: AI Agent, LLM, Tool Use, Python
