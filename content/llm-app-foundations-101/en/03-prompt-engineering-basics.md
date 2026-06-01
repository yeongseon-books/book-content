---
title: "LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles"
series: llm-app-foundations-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-06-01'
seo_description: Learn how to structure LLM prompts effectively by separating system, user, and assistant roles to ensure consistent, controllable model behavior.
---

# LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles

Prompt engineering is often described as clever wording. In application work, that description is too weak. The real job is to separate instructions by role — deciding which constraints are shared policy, which content belongs to the current request only, and which history needs to carry into the next turn — and fix that separation as structure.

This is the third post in the LLM App Foundations 101 series.

The difference shows up early. When you push everything into a single string, tone drifts, output format varies between calls, prior conversation gets forgotten, and parameter tuning becomes guesswork. Many problems that feel like model instability actually start from a blurry message array structure.

In chat APIs, `system`, `user`, and `assistant` are not simple labels. They are the minimum separation unit for application policy, the current request, and accumulated history. Once you draw clear boundaries between those three layers, the same model produces far more predictable behavior.

Here we treat the role-based message array as the fundamental unit of prompt design and build stable input structures on top of it.

![Prompt engineering basics: system, user, and assistant roles](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-01-prompt-engineering-basics-system-user-an.en.png)
*Prompt engineering basics: system, user, and assistant roles*

## Questions to Keep in Mind

- What responsibility belongs to `system`, `user`, and `assistant` messages?
- Why is a system message stronger than just writing one more first sentence?
- How do temperature, top_p, and few-shot examples affect answer stability?

## Why this post matters

After the first API call succeeds, the immediate next problem is "why does the same model keep giving different answers?" The first answer to that question is not a model swap — it is an input structure audit. When shared policy, current-request constraints, and carry-over history are all mixed together, inconsistent results are natural.

Prompt engineering is also closer to operational maintainability than to literary style. Collecting shared policy in `system` gives you a single change point. Recording history as `assistant` messages makes multi-turn debugging easier. Writing output format requirements structurally creates a testable contract.

Ultimately, a good prompt is not "a well-worded request to the model." It is "an input design that the application can repeatedly reconstruct." That instinct is what leads naturally into few-shot, conversation state, and structured output.

## The best way to understand role-based prompts: see the message array as three layers — policy, current request, and history — not as one sentence

The message array in a chat API is not a flat list. `system` holds policy that applies across nearly all requests. `user` holds the actual request for this turn. `assistant` re-injects the model's prior answer to restore context. Once you separate these three, it becomes much easier to explain how firmly the model should follow each instruction.

This perspective matters because many conversation-quality problems come from role confusion. Repeating shared rules inside `user` every time, failing to replay history, or combining high creative sampling with strict format expectations all produce unstable results.

> The starting point of prompt engineering is not elegant phrasing — it is a message structure that specifies which instruction belongs to which role.

## Core concepts

To make chat prompts operationally maintainable, you first need to separate the three roles. `system` is overall policy. `user` is the current request. `assistant` is prior answers. Without this structure, the application ends up repeating the same rules in every request and implicitly expecting history that was never provided.

![Roles merged into one messages array](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-01-understanding-the-three-roles.en.png)

*Roles merged into one messages array*

In practical terms:

- `system`: language, tone, safety boundaries, output rules — shared policy
- `user`: current task instruction, question, attached context
- `assistant`: prior model answers to replay into the next turn

The effect of a system message is easiest to see through direct comparison.

![Same question with and without system](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-02-how-a-system-message-changes-the-answer.en.png)

*Same question with and without system*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

question = "Explain the difference between a Python dictionary and a list."

without_system = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": question},
    ],
    temperature=0.2,
)

with_system = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a Python tutor for beginners. "
                "Always answer in English. "
                "Start with one short paragraph, then end with exactly three bullet points. "
                "Do not guess, and keep the explanation beginner-friendly."
            ),
        },
        {"role": "user", "content": question},
    ],
    temperature=0.2,
)

print("[without system]")
print(without_system.choices[0].message.content)
print()
print("[with system]")
print(with_system.choices[0].message.content)
```

What to look for in this comparison is not "which answer do I like better." It is how much more stable the output contract — language, length, bullet count, tone — becomes when a system message is present. If you want to treat prompts as operational assets, that reproducibility is what matters.

The key point: `system` is not an absolute command, but it is the strongest steering input available.

Multi-turn history is not hidden model memory — it is application-reconstructed message arrays.

![Assistant reply replay in the next turn](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-03-building-multi-turn-history-with-assista.en.png)

*Assistant reply replay in the next turn*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You are a Python learning assistant. Be brief and precise.",
    },
    {
        "role": "user",
        "content": "Explain the difference between Python lists and tuples in one paragraph.",
    },
]

first = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

assistant_text = first.choices[0].message.content
print("[assistant turn 1]")
print(assistant_text)
print()

messages.append({"role": "assistant", "content": assistant_text})
messages.append(
    {
        "role": "user",
        "content": "Add a short code example in no more than five lines.",
    }
)

second = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print("[assistant turn 2]")
print(second.choices[0].message.content)
```

That append step is the core of chatbot memory. Post 05 covers this in depth, but the key takeaway for now: conversation state is a data structure outside the model.

Sampling parameters are also part of prompt design.

![Low and high sampling control comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-04-temperature-and-top-p-consistency-versus.en.png)

*Low and high sampling control comparison*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

prompt = "Introduce FastAPI to a beginner in three sentences."

for temperature in (0.0, 0.9):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a technical editor. Keep answers concise.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )

    print(f"[temperature={temperature}]")
    print(completion.choices[0].message.content)
    print()
```

At the beginner stage, two principles are enough: start with low `temperature` when format stability matters, and do not make large changes to both `temperature` and `top_p` simultaneously.

The most reusable prompt structure is the instruction + context + output format pattern:

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a Python tutor for backend beginners. "
                "Answer in English and do not guess."
            ),
        },
        {
            "role": "user",
            "content": (
                "Instruction: explain what a dataclass is.\n"
                "Context: the reader knows basic Python syntax but has never used dataclasses.\n"
                "Output format: 1) two-sentence explanation 2) code example in six lines or less 3) one-line use case"
            ),
        },
    ],
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

To make role separation repeatable in code, use a message-building function:

```python
from typing import Iterable

def build_messages(
    system_prompt: str,
    user_prompt: str,
    history: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    return messages

history = [
    {"role": "assistant", "content": "Lists are mutable, while tuples are immutable."},
]

messages = build_messages(
    system_prompt="You are a concise Python tutor.",
    user_prompt="Add one short example that shows when a tuple is safer.",
    history=history,
)

for message in messages:
    print(message)
```

With this structure fixed, failure modes become faster to read. If shared policy drifts, look at `system`. If prior turns are forgotten, look at the `assistant` replay logic. If output format is inconsistent, look at the output rules in `user` together with `temperature`. A prompt that does not separate roles also mixes the causes of its problems.

Few-shot examples also go inside the same `messages` array:

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You explain Python concepts as a one-line definition followed by a one-line analogy.",
    },
    {"role": "user", "content": "What is a class?"},
    {
        "role": "assistant",
        "content": "Definition: A class is a blueprint for creating objects.\nAnalogy: It is like a mold used to produce many objects with the same shape.",
    },
    {"role": "user", "content": "What is inheritance?"},
    {
        "role": "assistant",
        "content": "Definition: Inheritance lets a new class reuse attributes and behavior from an existing class.\nAnalogy: It is like starting from a base template and extending it instead of rebuilding from scratch.",
    },
    {"role": "user", "content": "What is a decorator?"},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

![Prompt mistakes that destabilize output](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-05-common-prompt-design-mistakes.en.png)

*Prompt mistakes that destabilize output*

## Common misconceptions

- Repeating shared policy in `user` every time seems fine, but it multiplies change points and reduces stability.
- Multi-turn conversation feels like built-in model memory, but it is actually application logic that re-sends `assistant` messages.
- Expecting strict format from high `temperature` creates a conflict that cannot be resolved by prompt wording alone.
- Adding more few-shot examples always seems better, but long examples can spend tokens without sharpening the pattern.
- Vague terms like "better," "in detail," or "nicely" feel like sufficient control, but specific constraints — paragraph count, bullet count, key names — are far stronger.

## Reusable prompt template patterns

Managing prompts as text blobs makes change history tangled quickly. In practice, separating templates and slots — keeping policy, context, and output contract as distinct variables — is safer.

```python
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    system_policy: str
    instruction: str
    output_contract: str

BASE_TEMPLATE = PromptTemplate(
    system_policy=(
        "You are a backend Python tutor. "
        "Do not guess unknown facts. "
        "If information is missing, say what is missing explicitly."
    ),
    instruction="",
    output_contract=(
        "Return exactly this structure:\n"
        "summary: <2 sentences>\n"
        "example: <code block>\n"
        "pitfall: <1 sentence>"
    ),
)

def build_user_prompt(task: str, context: str) -> str:
    return (
        f"Instruction: {task}\n"
        f"Context: {context}\n"
        f"Output format: {BASE_TEMPLATE.output_contract}"
    )
```

The advantage of this structure is that policy updates are centralized. When you need to strengthen a "no guessing" rule, changing `system_policy` in one place updates every path simultaneously.

### Prompt regression testing patterns

Prompt changes create regressions just like code changes. Maintaining a minimal snapshot test catches the moment output format breaks.

```python
EXPECTED_KEYS = ["summary:", "example:", "pitfall:"]

def assert_output_contract(text: str) -> None:
    for key in EXPECTED_KEYS:
        if key not in text:
            raise AssertionError(f"Missing contract key: {key}")

def assert_no_forbidden_phrase(text: str) -> None:
    forbidden = ["I guess", "maybe", "not sure"]
    lowered = text.lower()
    for phrase in forbidden:
        if phrase in lowered:
            raise AssertionError(f"Forbidden uncertainty phrase found: {phrase}")
```

If prompt engineering is to remain more than guesswork, these small, solid contract checks are necessary.

### Provider role-mapping considerations

Role names are similar across providers, but SDK surfaces differ. OpenAI has both `responses` and `chat.completions` paths; Anthropic centers on `messages`. So it is better to fix roles to an internal standard first with a team-shared interface.

```python
def normalize_messages(system_text: str, history: list[dict[str, str]], user_text: str):
    return [{"role": "system", "content": system_text}, *history, {"role": "user", "content": user_text}]
```

The part that breaks most often when switching providers is not model performance — it is the message serialization layer. Separating that layer early makes future expansion far simpler.

## Operational checklist

- [ ] `system` holds shared policy, `user` holds the current request, `assistant` holds replay history.
- [ ] You compared the same question with and without a system message to confirm the output difference directly.
- [ ] Reusable system prompts are extracted to a constant or config file.
- [ ] Multi-turn tests verify that `assistant` messages are explicitly re-sent.
- [ ] Format requirements use concrete constraints — paragraph count, bullet count, key structure — not vague adjectives.

## Summary

The starting point of prompt engineering is not elegant phrasing. It is a role-separated message array. `system` fixes policy, `user` carries the current request, `assistant` restores history needed for the next turn. With this base structure in place, the same model produces far more predictable behavior.

Three things to remember from this post. Shared rules belong in `system`. Multi-turn memory is application-reconstructed. Parameter tuning must be read alongside prompt structure. Once these three are separated, "why did the answer drift?" becomes much easier to explain.

In practice, adding one more layer greatly improves stability: treat prompts as versioned change assets, and include template versioning and regression tests in your operational workflow. The ability to trace why results changed from the same model is what keeps a system maintainable long-term.

Longer prompts do not guarantee better quality. Prompts with clear structure and explicit contracts produce more stable results than prompts that are merely longer.

In operations, this principle connects directly to cost reduction and fewer incidents. Short, clear structure wins.

The next post covers few-shot and chain-of-thought. This post was about separating roles. The next is about layering examples and step-by-step reasoning on top to steer answer patterns more strongly.

## Answering the Opening Questions

- What responsibility belongs to `system`, `user`, and `assistant` messages?
  - `system` carries shared policy and role, `user` carries the current request, and `assistant` carries prior answer history.

- Why is a system message stronger than just writing one more first sentence?
  - A system message enters as a higher-priority instruction frame that the model should follow first on each request, making it more stable than an ordinary sentence inside the user prompt.

- How do temperature, top_p, and few-shot examples affect answer stability?
  - Temperature and top_p control sampling variance, while few-shot examples lock in the desired answer shape by demonstrating the pattern to follow.

<!-- toc:begin -->
## In this series

- [LLM App Foundations 101 (1/6): LLM API first call — sending your first request](./01-llm-api-first-call.md)
- [LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows](./02-understanding-tokens.md)
- **LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles (current)**
- LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers (upcoming)
- LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot (upcoming)
- LLM App Foundations 101 (6/6): Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

### Official docs

- [Groq Docs: Text chat](https://console.groq.com/docs/text-chat)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [OpenAI Platform Docs: Messages and roles](https://platform.openai.com/docs/guides/text)
- [Anthropic Docs: Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

### Related series

- [Few-shot and chain-of-thought — steering better answers](./04-few-shot-and-cot.md)
- [Managing conversation state — building a multi-turn chatbot](./05-conversation-state.md)
- [Tool calling — connecting functions to the model](../../llm-api-production-101/en/02-tool-calling.md)

Tags: LLM, OpenAI, Prompt Engineering, Python
