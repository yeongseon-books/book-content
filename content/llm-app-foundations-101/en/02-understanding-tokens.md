---
title: "LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows"
series: llm-app-foundations-101
episode: 2
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
seo_description: Master the economics and limits of LLM applications by understanding tokens, context windows, and practical estimation using the tiktoken library.
---

# LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows

When people first connect an LLM API, they usually focus on answer quality. That makes sense at the demo stage. In real applications, though, the first hard constraints show up somewhere else: cost, latency, and length limits. A prompt gets a little longer, and the response slows down. A few more conversation turns are added, and token usage jumps. A large chunk of reference text is attached, and the model starts cutting answers short.

This is the second post in the LLM App Foundations 101 series.

These symptoms look like separate problems, but they share one underlying unit: the token. Models read and generate in token units, not in sentences or words. So an input that looks short in plain text can still be expensive, a block of code can consume more tokens than expected, and a Korean sentence can fragment differently from an English sentence.

From an operational standpoint, you need to internalize this difference early. Tokens are not just a theory term — they are the billing unit, the first explanation for latency, and the boundary of length limits. Once you have this sense, "why was this request heavy?" becomes a number you can read, not a guess you have to make.

Here we treat tokens not as a substring concept but as the operational unit that binds cost, speed, and limits together.

![Understanding tokens: cost, limits, and context windows](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-01-understanding-tokens-cost-limits-and-con.en.png)
*Understanding tokens: cost, limits, and context windows*

## Questions to Keep in Mind

- Why should you treat tokens as budget units instead of word-like pieces?
- What do `prompt_tokens`, `completion_tokens`, and `total_tokens` each tell you?
- Where do the context window, `max_tokens`, and `finish_reason` collide?

## Why this post matters

LLM applications send strings but actually run on token budgets. So whether you are explaining call cost, understanding response speed, or designing length limits, you always end up coming back to tokens. Without this reference point, it is hard to explain why the system suddenly got heavy when the prompt grew.

Token problems also surface faster in production than in demos. A few one-off calls barely show the issue. But once conversation history accumulates, retrieved documents attach, and output-length control is loose, tokens push cost and latency up together. Understanding tokens early pays off more than optimizing them later.

Most importantly, tokens turn problems into numbers. Instead of "the prompt seems too long," you can say `prompt_tokens=3050`. Instead of "the answer seems truncated," you can say `finish_reason=length`. That shift is what operational awareness looks like.

## The best way to understand tokens: see them as the budget unit the model uses, not as text fragments

Humans read sentences and words. Models do not. A model splits text into smaller pieces according to its tokenizer rules, and processes input and generates output based on the count of those pieces. So tokens are simultaneously a question of "how is text split?" and a question of "how much budget is consumed?"

From this angle, cost, latency, and length limits connect into one picture. Longer input means more tokens to read. Longer output means more tokens to generate. The sum of both pushes against the context window. Tokens are not an implementation detail — they are the shared language that explains system behavior.

> If you think of tokens as word substitutes, you will keep getting surprised. If you think of them as the budget unit the model uses, cost and limits become readable at once.

## Core concepts

A token is a text chunk from the model's perspective. That chunk does not map one-to-one to words. Common English combinations may merge into larger pieces, while rare expressions split into smaller ones. Korean, code, numbers, whitespace, and newlines all count toward the token total.

![Text split into model token pieces](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-01-what-a-token-actually-is.en.png)

*Text split into model token pieces*

For example, these three inputs may look similar to a human but can differ widely in token count:

- `hello world`
- `unbelievable`
- `print(user_profile[0]["email"])`

Behind that difference is the BPE (Byte Pair Encoding) principle. You do not need deep theory, but one practical conclusion is enough: **word count is a poor proxy for token count**.

![Similar inputs with uneven token cost](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-02-why-tokens-matter-so-much.en.png)

*Similar inputs with uneven token cost*

Tokens matter for three reasons. First, most LLM APIs charge based on input and output tokens. Second, the model reads and generates token-by-token, so longer input and output tend to increase latency. Third, every model has a maximum token count per request — the context window.

Reduced to operational rules:

- Cost problems are usually token problems.
- Slow responses should be suspected as token problems first.
- Length-limit errors are almost always token budget management failures.

![Usage fields for input output and total](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-03-revisiting-usage-prompt-tokens-completio.en.png)

*Usage fields for input output and total*

In practice, you need to read `usage` as numbers:

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain Python decorators in no more than two paragraphs.",
        }
    ],
)

usage = completion.usage

print(completion.choices[0].message.content)
print()
print(f"finish_reason={completion.choices[0].finish_reason}")
print(f"prompt_tokens={usage.prompt_tokens}")
print(f"completion_tokens={usage.completion_tokens}")
print(f"total_tokens={usage.total_tokens}")
```

`prompt_tokens` is the total input length. `completion_tokens` is the generated output length. `total_tokens` is their sum. A large input with short output may signal prompt bloat. A short input with long output may signal loose length control.

![Token estimate path before API send](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-04-estimating-token-count-with-tiktoken.en.png)

*Token estimate path before API send*

In production, observing after the call is not enough. You need to measure approximate size before sending.

```bash
pip install tiktoken
```

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

text = "Measuring token length before a request makes prompt handling safer."
tokens = encoding.encode(text)

print(tokens)
print(f"token_count={len(tokens)}")
```

For estimating a message bundle:

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

messages = [
    {"role": "system", "content": "You are a concise Python tutor."},
    {"role": "user", "content": "Explain the difference between a list and a tuple."},
    {"role": "assistant", "content": "Lists are mutable, while tuples are immutable."},
    {"role": "user", "content": "Add one short code example too."},
]

serialized = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
estimated_prompt_tokens = len(encoding.encode(serialized))

print(serialized)
print()
print(f"estimated_prompt_tokens={estimated_prompt_tokens}")
```

One important caveat: `cl100k_base` is a practical estimation tool, not the billing ground truth for Groq. The authoritative accounting value is always the provider's `usage` field.

The context window should be understood as a shared budget for input and output, not as an input-only limit. The working equation is one line:

`input tokens + output tokens <= context window`

So a long system prompt, long conversation history, retrieved documents, and a long answer all compete for the same window. Designs that push right up to the theoretical maximum are fragile. Always leave headroom.

![Context overflow and length cutoff branches](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/02/02-05-detecting-long-prompt-problems-with-fini.en.png)

*Context overflow and length cutoff branches*

Output length is controlled with `max_tokens`, and truncation is detected via `finish_reason`:

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain the difference between a Python generator and a list with examples.",
        }
    ],
    max_tokens=80,
)

print(completion.choices[0].message.content)
print()
print(f"completion_tokens={completion.usage.completion_tokens}")
print(f"finish_reason={completion.choices[0].finish_reason}")
```

A monitoring pattern that handles long input with a small output cap together:

```python
import os

import tiktoken
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
encoding = tiktoken.get_encoding("cl100k_base")

long_text = " ".join(
    [
        "Explain why a Python web application should keep both request logs and exception logs."
    ]
    * 200
)

instruction = "Read the following text and summarize the key points as 10 bullets."
user_content = instruction + "\n\n" + long_text
estimated_prompt_tokens = len(encoding.encode(user_content))
print(f"estimated_prompt_tokens={estimated_prompt_tokens}")

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": user_content,
        }
    ],
    max_tokens=60,
)

choice = completion.choices[0]

print(choice.message.content)
print()
print(f"prompt_tokens={completion.usage.prompt_tokens}")
print(f"completion_tokens={completion.usage.completion_tokens}")
print(f"total_tokens={completion.usage.total_tokens}")
print(f"finish_reason={choice.finish_reason}")

if choice.finish_reason == "length":
    print("Warning: the response stopped because it hit a length limit.")
```

In practice, printing this much already gives you actionable signals. If `estimated_prompt_tokens` and actual `prompt_tokens` diverge heavily, your estimation method is too coarse. If `finish_reason=length` repeats, input trimming or `max_tokens` redesign comes first. Conversely, if input is short but `completion_tokens` keeps climbing, the output format request is probably too loose.

A pre-call guard function makes long-input handling safer:

```python
def should_compress_prompt(
    estimated_prompt_tokens: int,
    reserved_output_tokens: int,
    context_window: int,
    safety_margin: int = 500,
) -> bool:
    usable_budget = context_window - reserved_output_tokens - safety_margin
    return estimated_prompt_tokens > usable_budget

context_window = 128_000
reserved_output_tokens = 1_000

if should_compress_prompt(
    estimated_prompt_tokens=3_050,
    reserved_output_tokens=reserved_output_tokens,
    context_window=context_window,
):
    print("Compress or trim the prompt before sending it.")
else:
    print("Prompt budget looks safe.")
```

This kind of pre-call guard is useful for preventing failures, but its more important role is fixing policy in code. It lets you codify decisions like how many search results to attach, how many conversation turns to keep, and how much output headroom to reserve.

## Common misconceptions

- Treating tokens as roughly equivalent to words leads to constant errors whenever Korean, code, or symbols dominate the input.
- It is easy to mistake `tiktoken` estimates for billing-accurate values, but the final authority is the provider's `usage` field.
- The context window is not an input-only limit. Output shares the same window.
- Setting `max_tokens` high feels like enough, but if input is already large, actual remaining output space may be much smaller.
- Ignoring `finish_reason=length` as a mild warning is risky — it can mean mid-sentence truncation or lost code blocks.

## Turning token budgets into operational policy

Once you understand tokens, the next step is fixing numbers into policy. The most practical starting point is a per-request-type budget table. Instead of "keep it short," explicitly stating input and output caps lets the team design prompts against the same standard.

| Request type | Input cap | Output cap | Safety margin | Notes |
|---|---:|---:|---:|---|
| General Q&A | 2,000 | 600 | 300 | Response speed priority |
| Document summary | 5,000 | 900 | 500 | Long body allowed |
| Policy decision | 3,500 | 500 | 400 | Format stability priority |
| Code explanation | 4,500 | 1,000 | 500 | Code block headroom needed |

Translating this table into code makes pre-call validation straightforward:

```python
from dataclasses import dataclass

@dataclass
class TokenBudget:
    max_prompt: int
    max_output: int
    safety_margin: int

BUDGETS = {
    "qa": TokenBudget(max_prompt=2000, max_output=600, safety_margin=300),
    "summary": TokenBudget(max_prompt=5000, max_output=900, safety_margin=500),
    "policy": TokenBudget(max_prompt=3500, max_output=500, safety_margin=400),
    "code": TokenBudget(max_prompt=4500, max_output=1000, safety_margin=500),
}

def assert_budget_ok(estimated_prompt_tokens: int, use_case: str, context_window: int) -> None:
    budget = BUDGETS[use_case]
    allowed_prompt = context_window - budget.max_output - budget.safety_margin
    if estimated_prompt_tokens > allowed_prompt:
        raise ValueError(
            f"Prompt too long: estimated={estimated_prompt_tokens}, allowed={allowed_prompt}, use_case={use_case}"
        )
```

### Token-based rate limit defense

Rate limits are not just about request count. Many providers also enforce token-per-minute limits. If you design only around requests per second, long prompts can trigger repeated `429` errors.

```python
import time

class TokenRateLimiter:
    def __init__(self, tokens_per_minute: int):
        self.tokens_per_minute = tokens_per_minute
        self.window_started = time.time()
        self.used_tokens = 0

    def consume(self, estimated_tokens: int) -> None:
        now = time.time()
        if now - self.window_started >= 60:
            self.window_started = now
            self.used_tokens = 0

        if self.used_tokens + estimated_tokens > self.tokens_per_minute:
            sleep_s = 60 - (now - self.window_started)
            if sleep_s > 0:
                time.sleep(sleep_s)
            self.window_started = time.time()
            self.used_tokens = 0

        self.used_tokens += estimated_tokens
```

This limiter is coarse but effective. It throttles before hitting the provider's limit when token-heavy requests cluster together, reducing `429` storms.

### Quick monthly cost estimation

For operational decisions, monthly totals matter more than per-call prices. A conservative table like this lets you check budget impact before adding features:

| Daily calls | Avg total tokens | Monthly tokens (30d) | Price assumption (USD/1M) | Monthly cost estimate |
|---:|---:|---:|---|---:|
| 5,000 | 900 | 135,000,000 | 0.35 | 47.25 |
| 20,000 | 1,200 | 720,000,000 | 0.35 | 252.00 |
| 50,000 | 1,600 | 2,400,000,000 | 0.35 | 840.00 |

Token cost is sensitive to model changes and prompt-length shifts. So when doing cost retrospectives, "average `prompt_tokens` grew by X" is a more accurate starting point than "the pricing table changed."

## Operational checklist

- [ ] You record `prompt_tokens`, `completion_tokens`, and `total_tokens` from every real call.
- [ ] You estimate input length with `tiktoken` or equivalent before calls.
- [ ] You confirmed the context window limit for your model in official documentation.
- [ ] You do not leave `max_tokens` at its default — you set it as explicit output-length policy.
- [ ] You log `finish_reason` and have defined follow-up actions for `length` occurrences.

## Summary

Tokens are the unit that matters more than sentences in LLM systems. The model reads in tokens, generates in tokens, the provider bills in tokens, and the context window is bounded in tokens. So explaining cost, speed, and limits in a single language requires a token-centric mental model.

The practical instinct to take from this post is clear. After calls, read `usage`. Before calls, estimate with `tiktoken`. Control output with `max_tokens`. Detect truncation with `finish_reason`. When those four axes come together, length-related issues become far less mysterious.

One more thing to remember: token optimization is not a cost-cutting technique that degrades model quality. It is a design technique for getting more stable results within the same budget. Trimming unnecessary repetition, selectively compressing history, and specifying output format can improve quality and cost simultaneously.

The next post covers role-based prompt design on top of the same chat API. Now that you can read the token budget, it is time to design input structures that draw more stable behavior from the same model.

## Answering the Opening Questions

- Why should you treat tokens as budget units instead of word-like pieces?
  - Because models process input and output in token units, and most costs and limits are also calculated in this unit.

- What do `prompt_tokens`, `completion_tokens`, and `total_tokens` each tell you?
  - `prompt_tokens` shows the input cost you sent, `completion_tokens` shows the generated output cost, and `total_tokens` shows the full budget of one call.

- Where do the context window, `max_tokens`, and `finish_reason` collide?
  - Input and output share the context window together. Even if `max_tokens` is set high, when remaining window is insufficient, you need to check `finish_reason` to confirm a length problem.

<!-- toc:begin -->
## In this series

- [LLM App Foundations 101 (1/6): LLM API first call — sending your first request](./01-llm-api-first-call.md)
- **LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows (current)**
- LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles (upcoming)
- LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers (upcoming)
- LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot (upcoming)
- LLM App Foundations 101 (6/6): Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [tiktoken GitHub repository](https://github.com/openai/tiktoken)
- [OpenAI tokenizer](https://platform.openai.com/tokenizer)

Tags: LLM, OpenAI, Prompt Engineering, Python
