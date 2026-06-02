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

> **Deprecation notice**: This series is superseded by [`llm-app-foundations-101`](../../llm-app-foundations-101/en/) and [`ai-app-patterns-101`](../../ai-app-patterns-101/en/). New readers are encouraged to start with the successor series.

# AI Web Development 101 (2/7): Prompt engineering basics — getting the answer you actually want

Two developers can use the same model and get very different results. In practice, the difference usually comes from request structure rather than model intelligence. The model does not read your mind. You have to supply context, role, constraints, and output expectations explicitly.

This is the 2nd post in the AI Web Development 101 series.

Here, we will treat prompts as executable contracts, not clever sentences.


![AI Web Development 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/02/prompt-role-layering.en.png)
*AI Web Development 101 chapter 2 flow overview*

> A prompt is an executable contract, not a clever sentence — the `system` layer carries long-lived rules and the `user` layer carries the current task, and that split is what makes model behavior stable in application code.

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

## Building a Mini Evaluation Table for Operational Baselines

To manage prompt quality as a team, you need a shared evaluation table instead of "looks good." Starting small — fixing just the minimum criteria per task type — is already effective.

| Task type | Required criteria | Failure signal |
| --- | --- | --- |
| Customer inquiry summary | 2 sentences max, facts only | Exceeds sentence count, speculative additions |
| Policy guidance | 3 bullets, excluded expressions omitted | Missing items, forbidden expressions present |
| Classification | Result within allowed label set | Label typo, value outside set |

The important point: the evaluation table is version-controlled alongside the prompt. Change the prompt, change the table, and leave test results in the PR — this makes regressions easy to find. This approach separates "what caused quality to change" even when model changes, parameter changes, and system prompt edits overlap.

## Designing Reusable Prompt Templates

If you approach prompt engineering as pure wordsmithing, team-level collaboration hits a wall immediately. In practice multiple people touch the same feature, so templates must be treated as explicit contracts. Separating input variables, output format, and forbidden rules makes review criteria clear.

```python
PROMPT_TEMPLATE = """
Role: You are a Korean technical blog editing assistant.
Goal: Refine the user's draft into professional prose.
Constraints:
- Do not speculate on unverified facts.
- Lists must not exceed 5 items.
Output format (JSON):
{{
  "summary": "one-sentence summary",
  "issues": ["problems found"],
  "rewrite": "improved body text"
}}
Input draft:
{draft}
"""
```

When role, goal, constraints, and output format are separated like this, quality variance shrinks even across model versions. It also enables fast root-cause tracing when incidents occur.

## Enforcing the Output Contract via the OpenAI API

Accepting only natural-language results is fast but leads to repeated parse instability when connecting to service APIs. Where possible, enforce structured output or a strict JSON contract.

```python
from openai import OpenAI
import json

client = OpenAI()

def refine_draft(draft: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "Always respond with a JSON object only."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(draft=draft)},
        ],
    )
    raw = response.choices[0].message.content or "{}"
    parsed = json.loads(raw)
    return parsed
```

The critical point: do not bury JSON parse failures under a generic exception. Recording parse failure rate as a separate metric lets you detect prompt degradation early.

## Prompt Boundaries When Combining with RAG

Many teams find answer quality unstable after adding RAG because they blindly concatenate long retrieval results. The prompt must include retrieval results but also specify the criteria by which the model selects and cites documents.

```text
System instructions:
- Use only the provided document chunks as evidence.
- If the evidence documents do not contain the answer, respond with "no evidence."
- Output source_ids as an array at the end of the answer.

User question:
{question}

Retrieved documents:
{retrieved_chunks}
```

This contract cannot eliminate hallucination entirely, but it at least secures traceability of evidence.

## LangChain PromptTemplate Example

The principle is the same when using a framework. Separating template from chain makes experiment automation easier later.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Korean technical support assistant. Speculation without evidence is forbidden."),
    ("human", "Question: {question}\n\nDocuments:\n{context}\n\nFormat: 1-sentence summary + 3 key points")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
chain = prompt | llm

result = chain.invoke({
    "question": "Tell me why token costs suddenly increased",
    "context": "Since last week the full log text started being included in prompts"
})
```

Even with LangChain, the quality of the template itself still determines the result.

## Prompt Quality Evaluation Metrics

When improving prompts, use measurable metrics instead of "looks better."

- Accuracy: match rate against a ground-truth dataset
- Format compliance: JSON parse success rate, required field missing rate
- Length fitness: ratio of responses exceeding the specified token range
- Safety: forbidden-topic response block rate
- Cost: average total_tokens per request

Even a simple regression test script like this prevents quality drops from prompt changes.

```python
CASES = [
    {"q": "What is the refund policy?", "must_include": ["business days"], "must_not_include": ["not sure but"]},
    {"q": "Give me a medical diagnosis", "must_include": ["cannot answer"], "must_not_include": ["dosage"]},
]
```

## Prompt Version Control Rules

Treating prompts like code requires version rules. For example, increment numbers like `answer_v1`, `answer_v2` and leave a one-line reason for each change — this is the simplest approach that works in practice.

- `v1 -> v2`: Added `confidence` field to output JSON
- `v2 -> v3`: Unified forbidden-topic response wording to match policy phrasing
- `v3 -> v4`: Fixed RAG citation format to `source_ids` array

This change history helps enormously when tracing quality score drops later. Most "quality dropped with no model change" incidents start from prompt changes.

## A/B Prompt Comparison with Experiment Logs

The most common trap in prompt improvement is impression-based evaluation: "this version looks better." In practice, run A/B on the same input set and compare format compliance and user feedback together.

```python
def run_prompt_ab(cases, prompt_a, prompt_b):
    report = []
    for case in cases:
        out_a = call_model(prompt_a, case["question"])
        out_b = call_model(prompt_b, case["question"])
        report.append({
            "id": case["id"],
            "a_json_ok": is_valid_json(out_a),
            "b_json_ok": is_valid_json(out_b),
            "a_len": len(out_a),
            "b_len": len(out_b),
        })
    return report
```

If JSON compliance goes up and response length variance drops, real user experience is likely to stabilize too. Conversely, if scores improve but token usage spikes, you must assess whether operational cost is manageable.

## Recording Prompt Failure Cases

Documenting specific failure cases like this dramatically accelerates team learning.

- Case 1: Answered forbidden topic using circumlocution → Strengthened forbidden pattern dictionary
- Case 2: Output in markdown instead of JSON → Re-stated "no output other than JSON" in system instructions
- Case 3: Exceeded length limit → Added "5 sentences maximum" constraint

These records are not just documentation — they become input data for the next experiment.

## Pre-Deployment Prompt Checklist

Before deployment, pass through this checklist.

- Is the role statement clear in one line?
- Does the output format match the parser requirements?
- Are forbidden rules included without exception?
- Are length limits and tone limits declared together?
- Is a fallback message defined for failure cases?

These five items look small, but they prevent the majority of operational incidents preemptively.

### Practical Note

The principles in this section become more important as features grow. Especially as team size increases, documented rules create a bigger quality difference than individual intuition. So do not stop at copying example code — redefine rules to fit your team's current incident patterns and operational constraints. A small checklist returns the largest long-term cost savings.


## Summary

Prompt engineering is not about sounding clever. It is about designing a task contract the model can follow consistently.

- `system` holds long-lived rules, while `user` carries the current task.
- Good prompts make role, context, output format, and constraints explicit.
- `temperature` and `max_tokens` are part of the prompting strategy, not separate afterthoughts.
- Stable prompt work comes from repeatable testing and debugging loops.

The next chapter moves from prompt structure to a browser UI, where streaming and state management become part of the experience.

## Answering the Opening Questions

- **How is a prompt different from a simple question?**
  - A simple question leaves blanks for the model to fill, but a prompt is a work contract that includes role, context, output format, and constraints. The difference between the `bad` example's "write a product description" and the `better` example's specified `target audience`, `emphasis points`, and `output format` was exactly this contract difference. That's why this article treats prompts not as sentence intuition but as reproducible input structures.
- **What responsibilities do the `system` and `user` roles each carry?**
  - `system` fixes long-term rules and prohibitions like "you are a customer support FAQ generator," while `user` delivers the current task like "turn the password reset policy into a FAQ of 2 sentences or fewer." In the `PROMPT_TEMPLATE` example too, role, goal, constraints, and JSON output format were grouped as system-level concerns, with only `draft` injected as an input variable. This separation is what lets you isolate whether the prompt version changed or the request data changed.
- **What information does a good prompt never leave out?**
  - A good prompt never omits at minimum: role, domain context, output contract, and prohibition rules. The article fixed JSON keys to `title`, `summary`, `risk`, and in the RAG example specified a `source_ids` array and the rule "if no evidence, say no evidence" for exactly this reason. The pre-deployment checklist asking you to verify role statement, length limit, prohibition rules, and fallback text together is ultimately the same principle compressed for operations.
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
