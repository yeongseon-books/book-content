---
title: "LLM Apps Ops 101 (3/6): Evaluating LLM output quality"
series: llm-apps-ops-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-14'
seo_description: The first useful evaluation layer is not a perfect semantic judge. It is a cheap filter that catches obviously bad answers quickly and consistently.
---

# LLM Apps Ops 101 (3/6): Evaluating LLM output quality

As traffic grows, nobody can read every model response by hand.

This is the third post in the LLM Apps Ops 101 series. Here, we will build a minimal quality gate around length, keyword coverage, and format checks.

Early in an ops pipeline, the pragmatic move is not to build a brilliant judge. It is to fail obvious bad output cheaply, consistently, and with enough detail to act on it.

![LLM output quality evaluation pipeline](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-01-big-picture.en.png)
*LLM output quality evaluation pipeline*
> Rule-based checks are the first filter for obvious failures; semantic quality judgment belongs in the next layer.

## Questions to Keep in Mind

- Why should LLM output evaluation not stop at rule-based checks?
- What failures become visible faster when format, length, and keyword checks are separated?
- What decision standard should a batch evaluation report provide for operations?

## Why this layer matters
![Rule checks catch obvious failures first](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-01-why-this-layer-matters.en.png)

*Rule checks catch obvious failures first*

Before adding complex judges, build a rule layer that catches obviously bad output cheaply and consistently.

At scale, nobody reads every answer. A practical pipeline starts by blocking machine-detectable failures: malformed JSON, missing keywords, and answers that are far too short or too long.

Example file: `en/03-evaluation/main.py`

## Minimal runnable example
```python
import json
import os
from dataclasses import asdict, dataclass

from groq import Groq

MODEL = "llama-3.1-8b-instant"

@dataclass
class EvalResult:
    passed: bool
    length_ok: bool
    keywords_ok: bool
    format_ok: bool
    missing_keywords: list[str]
    answer_length: int

def ask_for_json(client: Groq, topic: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return JSON only with keys 'answer' and 'keywords'. "
                    "The answer must be concise and technical."
                ),
            },
            {
                "role": "user",
                "content": f"Explain {topic} in JSON. Include one short answer and a keyword list.",
            },
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "{}"

def evaluate(text: str, expected_keywords: list[str]) -> EvalResult:
    try:
        payload = json.loads(text)
        answer = payload["answer"]
        keywords = payload["keywords"]
        format_ok = isinstance(answer, str) and isinstance(keywords, list)
    except Exception:
        return EvalResult(False, False, False, False, expected_keywords, 0)

    normalized_answer = answer.lower()
    normalized_keywords = {str(item).lower() for item in keywords}
    missing = [
        keyword
        for keyword in expected_keywords
        if keyword.lower() not in normalized_answer and keyword.lower() not in normalized_keywords
    ]
    length_ok = 60 <= len(answer) <= 280
    keywords_ok = not missing
    format_ok = format_ok
    return EvalResult(
        passed=length_ok and keywords_ok and format_ok,
        length_ok=length_ok,
        keywords_ok=keywords_ok,
        format_ok=format_ok,
        missing_keywords=missing,
        answer_length=len(answer),
    )

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    raw = ask_for_json(client, "Python's GIL")
    result = evaluate(raw, ["CPython", "thread", "lock"])
    print(json.dumps({"raw": json.loads(raw), "evaluation": asdict(result)}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

## What to notice in this code
![Format length and keyword checks split](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-02-what-to-notice-in-this-code.en.png)

*Format length and keyword checks split*
- Forcing JSON output narrows the shape of the problem before evaluation starts.
- Returning `missing_keywords` makes failures actionable instead of mysterious.
- Length thresholds should reflect the product, not an abstract best practice.

## What changes when you add JSON Schema

If you want format validation to survive real team usage, do not stop at “the keys exist.” Add schema validation so the response contract becomes explicit.

```python
from jsonschema import ValidationError, validate

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "minLength": 60, "maxLength": 280},
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
    },
    "required": ["answer", "keywords"],
    "additionalProperties": False,
}

def validate_schema(payload: dict) -> tuple[bool, str | None]:
    try:
        validate(instance=payload, schema=ANSWER_SCHEMA)
        return True, None
    except ValidationError as exc:
        return False, exc.message
```

This is the difference between “the model usually behaves” and “the downstream pipeline can trust the contract.” Schema drift is a quiet way to break batch jobs, dashboards, and storage.

## Connect it to a batch report

Operations work is rarely about one answer. You want to compare prompt versions, model versions, and release candidates across a stable case set.

```python
TEST_CASES = [
    {"topic": "Python's GIL", "expected_keywords": ["CPython", "thread", "lock"]},
    {"topic": "asyncio.gather", "expected_keywords": ["coroutine", "concurrent", "await"]},
]

def run_batch(client: Groq) -> list[dict]:
    batch_results = []
    for case in TEST_CASES:
        raw = ask_for_json(client, case["topic"])
        result = evaluate(raw, case["expected_keywords"])
        batch_results.append(
            {
                "topic": case["topic"],
                "passed": result.passed,
                "missing_keywords": result.missing_keywords,
                "answer_length": result.answer_length,
            }
        )
    return batch_results

print(json.dumps(run_batch(client), indent=2, ensure_ascii=False))
```

**Expected output:**

```text
[
  {
    "topic": "Python's GIL",
    "passed": true,
    "missing_keywords": [],
    "answer_length": 148
  },
  {
    "topic": "asyncio.gather",
    "passed": false,
    "missing_keywords": ["await"],
    "answer_length": 81
  }
]
```

That result is useful because the failure is replayable. The second case did not just “score badly.” It missed `await`, which points you directly toward prompt design, model choice, or task phrasing.

## What comes after the rule layer

In practice, the sequence usually looks like this:

1. **Format checks** keep the pipeline stable.
2. **Length and keyword checks** catch obvious failures cheaply.
3. **Small batch reports** detect regressions across releases.
4. **Human review or LLM-as-judge** is reserved for ambiguous cases.

The point is cost control as much as quality control. Cheap gates should protect expensive ones.

## Where engineers get confused
![Rule checks layer before judge models](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-03-where-engineers-get-confused.en.png)

*Rule checks layer before judge models*
- Passing format checks does not mean the answer is good. Failing format checks usually means the answer is unusable.
- Keyword checks work best in domains with explicit terminology, not creative tasks.
- Even if you later add LLM-as-judge, rule-based checks remain a cheap first-pass guardrail.
- If length thresholds are too rigid, they can reject useful answers for the wrong reason.

## When failures rise, narrow them this way

```bash
# 1) Pull only failed cases from the latest run
python3 -m scripts.eval_report --only-failed

# 2) Group failures by reason
python3 -m scripts.eval_report --group-by reason

# 3) Compare two prompt versions
python3 -m scripts.eval_report --compare prompt_v12 prompt_v13
```

The core questions stay simple. Did failures rise because of format, because of length, or because one keyword family keeps disappearing?

## Checklist
- [ ] Force JSON-only output
- [ ] Define numeric length thresholds
- [ ] Set `expected_keywords` per test case
- [ ] Log missing keywords and failure reasons
- [ ] Store batch results with prompt and model versions

## Summary
Evaluation becomes operationally useful when it fails fast on obvious mistakes before humans ever need to look.

The next layer is not always a smarter judge. Often it is better reporting, better test cases, and better comparison discipline. In the next post, we will connect this quality layer to the security layer, where even well-formed output can still be operationally unsafe.

## Answering the Opening Questions

- **Why should LLM output evaluation not stop at rule-based checks?**
  - Passing format checks does not mean the answer is good. Factuality, usefulness, and grounding still need deeper evaluation.
- **What failures become visible faster when format, length, and keyword checks are separated?**
  - Broken JSON, overly short answers, and missing required terms become visible as separate failure types.
- **What decision standard should a batch evaluation report provide for operations?**
  - It should provide before/after pass rates, failure categories, representative failures, and thresholds that decide whether release is blocked.

<!-- toc:begin -->
## In this series

- [LLM Apps Ops 101 (1/6): Monitoring and logging for LLM apps](./01-monitoring-and-logging.md)
- [LLM Apps Ops 101 (2/6): LLM cost tracking and optimization](./02-cost-tracking.md)
- **LLM Apps Ops 101 (3/6): Evaluating LLM output quality (current)**
- LLM Apps Ops 101 (4/6): LLM app security (upcoming)
- LLM Apps Ops 101 (5/6): LLM app deployment strategies (upcoming)
- LLM Apps Ops 101 (6/6): Completing the LLM ops pipeline (upcoming)

<!-- toc:end -->

---

## References

### Official Docs

- [OpenAI Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs)
- [JSON Schema](https://json-schema.org/)

### Verification-friendly resources

- [G-Eval paper](https://arxiv.org/abs/2303.16634)
- [Promptfoo docs](https://www.promptfoo.dev/docs/)

Tags: LLMOps, Observability, Python, LLM
