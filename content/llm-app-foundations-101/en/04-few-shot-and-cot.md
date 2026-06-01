---
title: "LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers"
series: llm-app-foundations-101
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
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-15'
seo_description: Improve LLM performance on complex tasks using few-shot prompting for style consistency and chain-of-thought reasoning for logical accuracy.
---

# LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers

Post 03 established the basic shape of prompt design: split policy into `system`, put the current request in `user`, and replay earlier answers as `assistant` when you need conversation state. Once that foundation is in place, the next practical question shows up immediately. Why does the same model sometimes follow the format you want very closely, while other times it gives something that feels almost right but not dependable enough to automate?

This is the fourth post in the LLM App Foundations 101 series.

In application work, two of the first steering tools you reach for are few-shot prompting and chain-of-thought prompting. Few-shot means showing the model one or more examples of the behavior you want. Chain-of-thought means nudging the model to solve the task in intermediate steps instead of jumping straight to the final answer. Neither technique retrains the model. Both are ways to make an already capable model behave more predictably on the request in front of it.

A common misunderstanding needs clearing up front: adding more examples does not automatically improve results, and appending "step by step" does not inject knowledge the model never had. The real skill is knowing which tasks need which type of steering.

![Few-shot and chain-of-thought: steering better answers](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/04/04-01-few-shot-and-chain-of-thought-steering-b.en.png)
*Few-shot and chain-of-thought: steering better answers*

## Questions to Keep in Mind

- What does few-shot teach, and what does chain-of-thought teach?
- When should you choose zero-shot, few-shot, or CoT?
- Why can weak examples make the answer worse?

## Why this post matters

Early LLM applications usually reach "roughly correct" answers quickly. The trouble starts after that. The format drifts slightly across runs; classification labels vary in wording; multi-step calculations skip an intermediate check; policy decisions miss a condition in the middle. From that point, the model's general ability matters less than how clearly the input demonstrates the expected pattern.

Few-shot and CoT are the most practical tools for closing that gap. Few-shot shows the model what the answer should look like. CoT slows down the model's path to the answer by making intermediate states visible. One stabilizes format; the other stabilizes multi-step reasoning.

These two techniques also help with debugging, not just answer quality. When an output is wrong, you can distinguish whether the examples were bad, the reasoning order was off, or the task simply requires knowledge the model does not have. Good steering produces not only better answers but also more explainable failures.

## The best way to think about better steering: showing patterns and check-orders, not forcing correct answers

The essence of few-shot is "given this kind of question, answer in this shape." The essence of CoT is "do not jump — verify each intermediate step." Neither changes the model's weights, but both make the criteria for a good answer more explicit within the current request.

This distinction matters because many teams confuse writing longer prompts with writing better prompts. Good steering comes from pattern clarity, not length. Two short, consistent examples often outperform six verbose ones, and a single step-by-step instruction often beats a paragraph of explanation.

> Few-shot shows the answer shape; chain-of-thought shows the path to the answer. Good prompt design starts by picking which axis the task actually needs.

## Few-shot prompting teaches by example inside the messages array

![Example pairs steering the final answer](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/04/04-01-few-shot-prompting-teaches-by-example-in.en.png)

*Example pairs steering the final answer*

Few-shot prompting is the practice of placing one or more worked examples before the real question. In chat APIs, those examples are not stored in a separate training field. They live in the same `messages` array as everything else, usually as paired `user` and `assistant` turns.

The basic pattern looks like this:

1. put the global rules in `system`
2. add an example `user` request
3. add the example `assistant` answer you want the model to imitate
4. repeat with one or two more examples if needed
5. add the real `user` request at the end

From the model's point of view, this behaves like short in-context pattern learning. The weights do not change, but the request now contains a miniature demonstration of what counts as a good answer for this task. That is especially useful for formatting, label normalization, style control, and other short transformation jobs.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
            "You classify customer support tickets. "
            "Always answer in exactly this format:\n"
            "category: <billing|technical|account>\n"
            "priority: <low|medium|high>\n"
            "reason: <one sentence>"
        ),
    },
    {"role": "user", "content": "The payment went through, but I never received the receipt email."},
    {
        "role": "assistant",
        "content": (
            "category: billing\n"
            "priority: medium\n"
            "reason: The issue is part of the payment follow-up flow rather than a product bug."
        ),
    },
    {"role": "user", "content": "I changed my password, but I still cannot log in."},
    {
        "role": "assistant",
        "content": (
            "category: account\n"
            "priority: high\n"
            "reason: Loss of account access can block the user from using the service at all."
        ),
    },
    {"role": "user", "content": "The server throws an error whenever I upload a CSV file."},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

Examples must demonstrate the desired output pattern, not just a related topic. Few-shot is not a tool for adding common sense — it is a tool for stabilizing format and interpretation rhythm.

## Zero-shot versus few-shot on the same request

![Zero-shot and few-shot stability comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/04/04-02-zero-shot-versus-few-shot-on-the-same-re.en.png)

*Zero-shot and few-shot stability comparison*

Zero-shot means you ask for the task directly with no examples. You rely on the model's general training and instruction-following ability. That often works surprisingly well, especially for simple classification or summarization tasks. The weakness is consistency. The model may understand the task but still vary the label wording, the answer structure, or the level of explanation.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

ticket = "We are on the team plan, but this month's invoice is almost double what we expected."

system_prompt = (
    "You classify SaaS support tickets. "
    "Always answer in exactly this format:\n"
    "category: <billing|technical|account>\n"
    "priority: <low|medium|high>\n"
    "reason: <one sentence>"
)

zero_shot = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": ticket},
    ],
    temperature=0.2,
)

few_shot = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "My refund still does not appear on my card statement."},
        {
            "role": "assistant",
            "content": (
                "category: billing\n"
                "priority: medium\n"
                "reason: The problem is part of payment reconciliation after the original charge."
            ),
        },
        {"role": "user", "content": "I receive the two-factor code, but login still fails."},
        {
            "role": "assistant",
            "content": (
                "category: account\n"
                "priority: high\n"
                "reason: An access failure can immediately block the user from their work."
            ),
        },
        {"role": "user", "content": ticket},
    ],
    temperature=0.2,
)

print("[zero-shot]")
print(zero_shot.choices[0].message.content)
print()
print("[few-shot]")
print(few_shot.choices[0].message.content)
```

The value of few-shot shows up in repeatability more than raw accuracy. It tends to stabilize the label vocabulary, the line order, the explanation length, and the way ambiguous cases are interpreted. Applications care less about one impressive answer than about hundreds of answers arriving in a shape the rest of the system can rely on.

## Example quality can help or hurt

![Weak and strong example comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/04/04-03-example-quality-can-help-or-hurt.en.png)

*Weak and strong example comparison*

Few-shot prompting is only as good as the examples you provide. Developers add examples expecting an automatic boost, and the outputs become less consistent instead of more consistent.

Bad examples usually fail in one of four ways:

- the labels are inconsistent across examples
- the answer format changes from one example to the next
- the examples are verbose and hide the actual pattern
- the examples are too easy and do not resemble the real task

Good examples share these traits: short, mutually consistent, close to the real inputs you expect, and rich in edge-case signal rather than surface variety. Example count matters less than pattern clarity.

Rather than checking example quality by eye, a small verification script makes the judgment repeatable.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_prompt = (
    "You classify SaaS support tickets. "
    "Always answer in exactly this format:\n"
    "category: <billing|technical|account>\n"
    "priority: <low|medium|high>\n"
    "reason: <one sentence>"
)

evaluation_tickets = [
    "The API returns 500 whenever I upload an image.",
    "My receipt never arrived after the payment completed.",
    "I cannot access the account even after resetting the password.",
]

few_shot_prefix = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "My refund still does not appear on my card statement."},
    {
        "role": "assistant",
        "content": (
            "category: billing\n"
            "priority: medium\n"
            "reason: The problem is part of payment reconciliation after the original charge."
        ),
    },
]

for ticket in evaluation_tickets:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[*few_shot_prefix, {"role": "user", "content": ticket}],
        temperature=0.2,
    )
    print("---")
    print(ticket)
    print(completion.choices[0].message.content)
```

Running this over a saved evaluation set lets you check whether label vocabulary and line order remain stable across inputs. In production, you keep this set pinned and re-run it after any example change as a regression check.

## Measuring few-shot quality with simple metrics

"Looks good" is not durable. To turn prompt tuning from intuition into engineering, measure format compliance and label consistency after every example change.

```python
from collections import Counter

def parse_category(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("category:"):
            return line.split(":", 1)[1].strip()
    return "unknown"

def score_outputs(outputs: list[str]) -> dict[str, float]:
    categories = [parse_category(output) for output in outputs]
    valid_format = sum(
        1
        for output in outputs
        if "category:" in output and "priority:" in output and "reason:" in output
    )
    counter = Counter(categories)
    return {
        "format_compliance": valid_format / len(outputs),
        "unknown_ratio": counter["unknown"] / len(outputs),
    }
```

Even this minimal metric catches regressions quickly. If you add a new example and `format_compliance` drops, the problem is example quality, not example count.

## Chain-of-thought helps the model decompose the task

![Stepwise reasoning path to final_answer](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/04/04-04-chain-of-thought-helps-the-model-decompo.en.png)

*Stepwise reasoning path to final_answer*

If few-shot is about answer patterns, chain-of-thought is about solution process. Multi-step tasks become easier when the model is nudged to compute or check intermediate states instead of leaping directly to the conclusion. The model is not gaining new facts — it is being guided to use its existing knowledge more methodically.

This is the simplest zero-shot CoT pattern.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

question = (
    "An online course costs 120000 won. Apply a 10% coupon first, "
    "then add 10% VAT to the discounted price. What is the final payment amount?"
)

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "You explain calculations carefully and stay numerically precise.",
        },
        {
            "role": "user",
            "content": (
                question
                + " Let's think step by step. Put the last line in the form final_answer: <number> won."
            ),
        },
    ],
    temperature=0.0,
)

print(completion.choices[0].message.content)
```

This pattern is especially useful for tasks with words like "first," "then," "except," or "only if" — exactly the cases where skipping an intermediate check causes the answer to drift.

## Zero-shot CoT and few-shot CoT are different tools

Zero-shot CoT tells the model to reason step by step but does not show an example of that reasoning. It is cheap in tokens and easy to try first. Few-shot CoT goes further: the examples show not only the final answer format but also the reasoning rhythm the model should imitate.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
            "You calculate order totals. "
            "Always answer with numbered steps followed by final_answer."
        ),
    },
    {
        "role": "user",
        "content": "The base price is 50000 won. After a 20% discount, add a 3000 won shipping fee. What is the total?",
    },
    {
        "role": "assistant",
        "content": (
            "1) 20% of 50000 won is 10000 won.\n"
            "2) After the discount, the subtotal is 40000 won.\n"
            "3) Add the 3000 won shipping fee to get 43000 won.\n"
            "final_answer: 43000 won"
        ),
    },
    {
        "role": "user",
        "content": "The base price is 80000 won. After a 25% discount, add a 5000 won shipping fee. What is the total?",
    },
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.0,
)

print(completion.choices[0].message.content)
```

For most beginner projects, a good operating order is to start with zero-shot CoT and only pay for few-shot CoT when the reasoning structure keeps drifting.

## Combining few-shot and CoT fixes both the answer shape and the reasoning path

In real applications, these two techniques are often strongest together. You may want the model to follow a stable output schema while also checking rules in a specific order. That combination shows up in policy decisions, operations triage, eligibility checks, and other business tasks where the route to the answer matters almost as much as the answer itself.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

policy = (
    "Refund policy:\n"
    "- Full refund if the purchase was within 7 days and watch progress is under 20%\n"
    "- No refund if the purchase was within 7 days but watch progress is 20% or more\n"
    "- No refund if more than 7 days have passed, regardless of watch progress"
)

messages = [
    {
        "role": "system",
        "content": (
            "You review refund requests for an online course service. "
            "Always answer with 1) policy_check 2) decision 3) reason."
        ),
    },
    {"role": "user", "content": policy},
    {
        "role": "user",
        "content": "It has been 3 days since purchase, and the watch progress is 10%. Decide whether the refund should be approved.",
    },
    {
        "role": "assistant",
        "content": (
            "policy_check:\n"
            "1) The request is within 7 days of purchase.\n"
            "2) Watch progress is under 20%.\n"
            "decision: approved\n"
            "reason: The request satisfies both the time window and the watch-progress requirement for a full refund."
        ),
    },
    {
        "role": "user",
        "content": "It has been 5 days since purchase, and the watch progress is 35%. Decide whether the refund should be approved.",
    },
    {
        "role": "assistant",
        "content": (
            "policy_check:\n"
            "1) The request is within 7 days of purchase.\n"
            "2) Watch progress is 20% or more.\n"
            "decision: denied\n"
            "reason: The request is inside the time window, but the watch-progress threshold has already been crossed."
        ),
    },
    {
        "role": "user",
        "content": "It has been 10 days since purchase, and the watch progress is 0%. Decide whether the refund should be approved.",
    },
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.0,
)

print(completion.choices[0].message.content)
```

This pattern improves debuggability. If the output is wrong, you can inspect which policy check went wrong rather than treating the whole response as a black box.

However, combined few-shot + CoT prompts consume significant tokens. Before shipping such a prompt, measure its cost.

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

messages = [
    {"role": "system", "content": "You review refund requests carefully."},
    {"role": "user", "content": "Example 1 input ..."},
    {"role": "assistant", "content": "Example 1 reasoning ..."},
    {"role": "user", "content": "Example 2 input ..."},
    {"role": "assistant", "content": "Example 2 reasoning ..."},
    {"role": "user", "content": "Real request ... Let's think step by step."},
]

serialized = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
estimated_tokens = len(encoding.encode(serialized))

print(f"estimated_tokens={estimated_tokens}")
if estimated_tokens > 2000:
    print("Trim examples before shipping this prompt.")
```

## Controlling CoT exposure in production

CoT is valuable for accuracy, but not all intermediate reasoning should reach the end user. In production, separate internal reasoning from external output.

```python
instruction = (
    "Solve step by step internally. "
    "Return only final output in this format:\n"
    "decision: <approve|reject>\n"
    "reason: <one sentence>"
)
```

This pattern has two advantages. First, user-facing output stays concise. Second, the output contract that downstream systems parse remains stable regardless of how complex the internal reasoning becomes.

## Reducing few-shot size under rate-limit pressure

When traffic spikes, dynamically reducing example count keeps the system running. Quality drops slightly, but availability is preserved.

| State | Example count | temperature | Purpose |
|---|---:|---:|---|
| Normal | 3 | 0.2 | Maximum format stability |
| Caution | 2 | 0.2 | Begin token savings |
| Warning (429 rising) | 1 | 0.1 | Survival mode |

Few-shot and CoT are powerful but not free. Deciding in advance "when to use full steering and when to degrade" is part of operating these prompts in production.

## Common misconceptions

- Few-shot is not model retraining. It is in-context pattern demonstration within the current request.
- More examples do not automatically improve output. Verbose examples can consume tokens while blurring the pattern.
- CoT does not create new knowledge. It guides the model to use existing knowledge in a more ordered way.
- CoT is not always beneficial. For strict JSON or CSV output, it can make the model overly verbose.
- Combining few-shot and CoT is not always optimal. Context budget and latency cost rise together.

## Where these techniques stop helping

![When prompting should yield to other tools](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/04/04-05-where-these-techniques-stop-helping.en.png)

*When prompting should yield to other tools*

Neither technique creates missing facts. If the task depends on current events or private data, you need retrieval or tools, not a more elaborate prompt. If the context window is already crowded with conversation history or retrieved passages, adding more examples may reduce headroom for the real task. If the output must be rigid JSON or CSV, CoT verbosity can interfere with format compliance. If your examples are easy but the real task is full of ambiguous edge cases, few-shot will not rescue the gap.

## Operational checklist

- [ ] Few-shot examples include the desired output shape, not just the input
- [ ] You compared output stability and token cost at 1, 3, and 5 examples
- [ ] You audited examples for ones that would steer the model wrong
- [ ] Multi-step reasoning tasks include an explicit "think step by step" instruction
- [ ] Combined few-shot + CoT calls fit inside the model's context window
- [ ] Token budget is estimated before shipping combined prompts

## Answering the Opening Questions

- What does few-shot teach, and what does chain-of-thought teach?
  - Few-shot teaches the output pattern through examples; chain-of-thought teaches a stepwise path toward the answer.

- When should you choose zero-shot, few-shot, or CoT?
  - Start with zero-shot, add few-shot when the answer shape drifts, and consider CoT when the task needs decomposition.

- Why can weak examples make the answer worse?
  - The model imitates example quality, so weak or unrepresentative examples inject the wrong format and the wrong decision rule.

<!-- toc:begin -->
## In this series

- [LLM App Foundations 101 (1/6): LLM API first call — sending your first request](./01-llm-api-first-call.md)
- [LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows](./02-understanding-tokens.md)
- [LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles](./03-prompt-engineering-basics.md)
- **LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers (current)**
- LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot (upcoming)
- LLM App Foundations 101 (6/6): Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

### Official docs

- [Groq Docs: Text chat](https://console.groq.com/docs/text-chat)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [OpenAI Platform Docs: Prompt engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Docs: Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

### Research

- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)

### Related series

- [Managing conversation state — building a multi-turn chatbot](./05-conversation-state.md)
- [Prompt engineering basics — system, user, and assistant roles](./03-prompt-engineering-basics.md)
- [Tool calling — connecting functions to the model](../../llm-api-production-101/en/02-tool-calling.md)

Tags: LLM, OpenAI, Prompt Engineering, Python
