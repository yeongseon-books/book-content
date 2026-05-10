---
title: Evaluating LLM output quality
series: llm-apps-ops-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-01'
seo_description: The first useful evaluation layer is not a perfect semantic judge.
  It is a cheap filter that catches obviously bad answers quickly and consistently.
---

# Evaluating LLM output quality

## Questions this post answers
- How do you automate max-length checks for model output?
- When does keyword coverage become a useful quality gate?
- How far should format validation go before you add schema validation?

> The first useful evaluation layer is not a perfect semantic judge. It is a cheap filter that catches obviously bad answers quickly and consistently.

## Big picture
![LLM output quality evaluation pipeline](../../assets/llm-apps-ops-101/03/03-01-big-picture.en.png)

*LLM output quality evaluation pipeline*
## Why this layer matters
![Rule checks catch obvious failures first](../../assets/llm-apps-ops-101/03/03-01-why-this-layer-matters.en.png)

*Rule checks catch obvious failures first*
Before adding complex judges, build a rule layer that catches obviously bad output cheaply and consistently.

At scale, nobody reads every answer. A practical pipeline starts by blocking machine-detectable failures: malformed JSON, missing keywords, and answers that are far too short or too long.

Example file: `/root/Github/llm-apps-ops-101/en/03-evaluation/main.py`

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
![Format length and keyword checks split](../../assets/llm-apps-ops-101/03/03-02-what-to-notice-in-this-code.en.png)

*Format length and keyword checks split*
- Forcing JSON output narrows the shape of the problem before evaluation starts.
- Returning `missing_keywords` makes failures actionable instead of mysterious.
- Length thresholds should reflect the product, not an abstract best practice.

## Where engineers get confused
![Rule checks layer before judge models](../../assets/llm-apps-ops-101/03/03-03-where-engineers-get-confused.en.png)

*Rule checks layer before judge models*
- Passing format checks does not mean the answer is good. Failing format checks usually means the answer is unusable.
- Keyword checks work best in domains with explicit terminology, not creative tasks.
- Even if you later add LLM-as-judge, rule-based checks remain a cheap first-pass guardrail.

## Checklist
- [ ] Force JSON-only output
- [ ] Define numeric length thresholds
- [ ] Set expected_keywords per test case
- [ ] Log missing keywords on failure

## Summary
Evaluation becomes operationally useful when it fails fast on obvious mistakes before humans ever need to look.

<!-- toc:begin -->
## In this series

- [Monitoring and logging for LLM apps](./01-monitoring-and-logging.md)
- [LLM cost tracking and optimization](./02-cost-tracking.md)
- **Evaluating LLM output quality (current)**
- LLM app security (upcoming)
- LLM app deployment strategies (upcoming)
- Completing the LLM ops pipeline (upcoming)

<!-- toc:end -->

---

## References

- [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs)
- [JSON Schema](https://json-schema.org/)
- [G-Eval paper](https://arxiv.org/abs/2303.16634)
