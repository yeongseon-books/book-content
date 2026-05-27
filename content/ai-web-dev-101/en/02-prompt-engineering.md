---
title: "AI Web Development 101 (2/7): Prompt engineering basics — getting the answer you actually want"
series: ai-web-dev-101
episode: 2
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
seo_description: Learn how role, context, output format, and validation routines change model behavior even when the model stays the same.
---

# AI Web Development 101 (2/7): Prompt engineering basics — getting the answer you actually want

Two developers can use the same model and get very different results. In practice, the difference usually comes from request structure rather than model intelligence. The model does not read your mind. You have to supply context, role, constraints, and output expectations explicitly.

This is the 2nd post in the AI Web Development 101 series.

Here, we will treat prompts as executable contracts, not clever sentences.


![AI Web Development 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-role-layering.en.png)
*AI Web Development 101 chapter 2 flow overview*

## Questions to Keep in Mind

- How is a prompt different from just asking a question?
- What responsibilities belong to `system` and `user` messages?
- Which ingredients make prompts stable enough for application code?

## Why prompt engineering deserves separate attention

In the previous chapter, the main question was how to call the API at all. From here on, the important question becomes how to shape the request so the answer is useful. A vague request tends to produce a generic answer. A structured request tends to produce something closer to the actual job you want done.

The easiest analogy is delegating work to a teammate. “Write a report” leaves topic, audience, length, and format open. “Write a three-bullet update for the product manager, focused on risk and next steps” is much easier to execute. Models behave the same way.

## Separate long-lived rules from the current task

In Chat Completions, the most important split is between `system` and `user`.

- `system`: long-lived role, tone, safety rules, and task style
- `user`: the concrete task and input values for the current turn

That split keeps application prompts easier to reason about. If quality changes, you can ask whether the failure came from the role layer or the task layer.

## Compare a weak prompt and a better one

The fastest way to learn prompt quality is to run the same task twice.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def run_prompt(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content

bad = run_prompt(
    system_prompt="You are a helpful assistant.",
    user_prompt="Write product copy.",
)

better = run_prompt(
    system_prompt=(
        "You write concise ecommerce copy for practical buyers. Avoid hype and keep the tone clear."
    ),
    user_prompt=(
        "Product: silent mechanical keyboard\n"
        "Audience: developers working from home\n"
        "Highlights: low noise, soft typing feel, pastel blue color\n"
        "Output: exactly 3 bullet points, 1 sentence each"
    ),
)

print("[bad]\n", bad)
print("\n[better]\n", better)
```

A better prompt is not “more beautiful.” It simply makes the contract tighter.

![How to improve a vague prompt into a concrete one](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-improvement-example.en.png)

*How to improve a vague prompt into a concrete one*

## Four fundamentals of reliable prompts

### 1. Define the role

“Help me” is weak. “You are a technical editor reviewing internal product documentation” is much stronger.

### 2. Supply the missing context

Who is the answer for? What domain are we in? What must be avoided? Without that context, the model fills in the blanks with generic assumptions.

### 3. Specify output format

If code will parse the answer later, output format is not optional. JSON, bullet count, column names, and length limits reduce downstream ambiguity.

### 4. State constraints and failure behavior

Rules like “answer in Korean,” “do not guess,” or “say you do not know when evidence is missing” make real systems much safer.

![Four prompt design principles that stabilize results](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/four-prompt-principles.en.png)

*Four prompt design principles that stabilize results*

## Turn output format into a real contract

```python
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0,
    messages=[
        {
            "role": "system",
            "content": (
                "You generate customer-support FAQ entries. "
                "Output exactly one JSON object with keys: title, summary, risk."
            ),
        },
        {
            "role": "user",
            "content": "Create a short FAQ entry for password reset in 2 sentences or less.",
        },
    ],
)

payload = json.loads(response.choices[0].message.content)
print(payload)
```

The point is not the JSON itself. The point is that your application can validate the answer mechanically instead of trusting free-form prose.

## When to adjust `temperature` and `max_tokens`

- `temperature` closer to 0 usually gives more repeatable, conservative answers
- higher `temperature` allows more variation and creativity
- `max_tokens` controls output length, so too small a value can create truncated answers

A rough working intuition:

- extraction, classification, code generation: `temperature=0.0 ~ 0.3`
- summaries and explanations: `temperature=0.2 ~ 0.5`
- brainstorming or marketing copy: `temperature=0.7+`

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
prompt = "Write one sentence introducing a TODO app for remote developers."

for temp in (0.1, 0.9):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=temp,
        max_tokens=80,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"temperature={temp}: {response.choices[0].message.content}")
```

![How temperature and token limits affect generation](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/temperature-max-tokens.en.png)

*How temperature and token limits affect generation*

## Debug prompts in a fixed order

When the answer is bad, do not jump straight to “the model is weak.” Check these layers first:

1. Is the role unclear?
2. Is important context missing?
3. Is the output format under-specified?
4. Would an example make the desired shape more obvious?
5. Are generation parameters causing variation or truncation?

You can make that process repeatable with tiny test cases.

```python
test_cases = [
    {"name": "length limit", "user": "Explain the signup benefit in at most 2 sentences."},
    {"name": "format", "user": "Summarize the refund policy in exactly 3 bullet points."},
]

system_prompt = "You summarize support information briefly and precisely."

for case in test_cases:
    answer = run_prompt(system_prompt, case["user"])
    print(f"\n[{case['name']}]\n{answer}")
```

## Common failure modes in real services

- the conversation history becomes too long, so the most important rule gets diluted
- the prompt says what not to do, but not what to do instead
- output format is too weak for the parser that follows
- domain terminology is missing, so the model defaults to generic meaning

Strong prompts are rarely “written once.” They are revised as failure cases accumulate.

![A practical prompt iteration loop](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-iteration-loop.en.png)

*A practical prompt iteration loop*

## Checklist

- [ ] I can explain the difference between `system` and `user`.
- [ ] I specify output format and constraints explicitly.
- [ ] I compared the same task with two prompt versions.
- [ ] I know when to lower or raise `temperature`.
- [ ] I treat prompt refinement as debugging, not as guesswork.

## Summary

Prompt engineering is not about sounding clever. It is about designing a task contract the model can follow consistently.

- `system` holds long-lived rules, while `user` carries the current task.
- Good prompts make role, context, output format, and constraints explicit.
- `temperature` and `max_tokens` are part of the prompting strategy, not separate afterthoughts.
- Stable prompt work comes from repeatable testing and debugging loops.

The next chapter moves from prompt structure to a browser UI, where streaming and state management become part of the experience.

## Answering the Opening Questions

- **How is a prompt different from just asking a question?**
  - The article treats Prompt engineering basics — getting the answer you actually want as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What responsibilities belong to `system` and `user` messages?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Which ingredients make prompts stable enough for application code?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [AI Web Development 101 (1/7): AI API first steps — sending your first request with the OpenAI API](./01-hello-ai-api.md)
- **Prompt engineering basics — getting the answer you actually want (current)**
- Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK (upcoming)
- RAG introduction — answering with your own data (upcoming)
- First steps with AI agents — making the model use tools (upcoming)
- Deploying an AI web app — shipping to Vercel and Azure (upcoming)
- Evaluating and improving an AI app — measuring quality over time (upcoming)

<!-- toc:end -->

## References

- [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Anthropic prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI text generation guides](https://platform.openai.com/docs/guides/text)

Tags: AI, LLM, Web Development, Python, Tutorial
