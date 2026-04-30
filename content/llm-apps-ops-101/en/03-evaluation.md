# Evaluating LLM output quality

> LLM Apps Ops 101 (3/6)

When you swap models or revise a prompt, how do you confirm things actually improved? Manual review works for a handful of examples, but it does not scale to thousands of responses. This post builds an automated evaluation pipeline: LLM-as-judge scoring, factual consistency checks, and format compliance validation.

---

## Three evaluation axes

LLM output quality lives across three dimensions.

- **Relevance**: did the model actually answer the question?
- **Faithfulness**: does the answer stay within the given context, or does it hallucinate?
- **Completeness**: did it cover every part of the question?

A failure on any axis affects user experience directly.

---

## LLM-as-judge

```python
import json
import os
import re
from dataclasses import dataclass

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

JUDGE_SYSTEM = """You are an expert AI response evaluator.
Given a question, context, and response, score these three dimensions from 1 to 5.

Criteria:
- relevance: does the response directly answer the question? (1=unrelated, 5=fully answers)
- faithfulness: is the response grounded only in the context? (1=severe hallucination, 5=context-only)
- completeness: does it address every part of the question? (1=major gaps, 5=fully covered)

Respond only with this JSON:
{"relevance": <1-5>, "faithfulness": <1-5>, "completeness": <1-5>, "reason": "<one sentence>"}"""

@dataclass
class EvalResult:
    relevance: float
    faithfulness: float
    completeness: float
    reason: str
    raw: str = ""

    @property
    def average(self) -> float:
        return (self.relevance + self.faithfulness + self.completeness) / 3

    def passed(self, threshold: float = 3.5) -> bool:
        return self.average >= threshold

    def to_dict(self) -> dict:
        return {
            "relevance": self.relevance,
            "faithfulness": self.faithfulness,
            "completeness": self.completeness,
            "average": round(self.average, 2),
            "passed": self.passed(),
            "reason": self.reason,
        }

class LLMJudge:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.llm = ChatGroq(
            model=model,
            api_key=os.environ["GROQ_API_KEY"],
            temperature=0.0,
        )

    def evaluate(self, question: str, context: str, response: str) -> EvalResult:
        user_msg = f"Question: {question}\n\nContext: {context}\n\nResponse: {response}"
        raw = self.llm.invoke([
            SystemMessage(content=JUDGE_SYSTEM),
            HumanMessage(content=user_msg),
        ]).content

        try:
            match = re.search(r"\{[^}]+\}", raw, re.DOTALL)
            if not match:
                raise ValueError("no JSON found")
            data = json.loads(match.group())
            return EvalResult(
                relevance=float(data.get("relevance", 3)),
                faithfulness=float(data.get("faithfulness", 3)),
                completeness=float(data.get("completeness", 3)),
                reason=data.get("reason", ""),
                raw=raw,
            )
        except Exception:
            return EvalResult(3.0, 3.0, 3.0, "parse failed", raw=raw)
```

---

## Format compliance checker

```python
import re
from dataclasses import dataclass

@dataclass
class FormatCheck:
    name: str
    passed: bool
    detail: str = ""

class FormatChecker:
    def check_json(self, text: str) -> FormatCheck:
        try:
            json.loads(text.strip())
            return FormatCheck("json", True)
        except json.JSONDecodeError as e:
            return FormatCheck("json", False, str(e))

    def check_max_length(self, text: str, max_chars: int) -> FormatCheck:
        if len(text) <= max_chars:
            return FormatCheck("max_length", True)
        return FormatCheck("max_length", False, f"{len(text)} > {max_chars}")

    def check_bullet_list(self, text: str, min_items: int = 2) -> FormatCheck:
        bullets = re.findall(r"^[-*]\s+.+", text, re.MULTILINE)
        if len(bullets) >= min_items:
            return FormatCheck("bullet_list", True, f"{len(bullets)} items")
        return FormatCheck("bullet_list", False, f"{len(bullets)} < {min_items}")

    def check_no_uncertainty_markers(self, text: str) -> FormatCheck:
        patterns = [
            r"I (?:think|believe|guess|suppose)",
            r"(?:might|may|could) be",
            r"I'm not (?:sure|certain)",
        ]
        found = [p for p in patterns if re.search(p, text, re.IGNORECASE)]
        if not found:
            return FormatCheck("no_uncertainty_markers", True)
        return FormatCheck("no_uncertainty_markers", False, f"found: {found}")
```

---

## Batch evaluation pipeline

```python
from dataclasses import dataclass, field

@dataclass
class TestCase:
    question: str
    context: str
    expected_keywords: list[str] = field(default_factory=list)

def run_eval_suite(
    test_cases: list[TestCase],
    responder_model: str = "llama-3.1-8b-instant",
    judge_model: str = "llama-3.1-8b-instant",
) -> dict:
    responder = ChatGroq(
        model=responder_model, api_key=os.environ["GROQ_API_KEY"], temperature=0.0
    )
    judge = LLMJudge(judge_model)

    results = []
    for tc in test_cases:
        prompt = f"Context:\n{tc.context}\n\nQuestion: {tc.question}"
        response = responder.invoke([HumanMessage(content=prompt)]).content

        eval_result = judge.evaluate(tc.question, tc.context, response)

        keyword_hits = [kw for kw in tc.expected_keywords if kw.lower() in response.lower()]
        keyword_coverage = len(keyword_hits) / len(tc.expected_keywords) if tc.expected_keywords else 1.0

        results.append({
            "question": tc.question,
            "response_preview": response[:150],
            "eval": eval_result.to_dict(),
            "keyword_coverage": round(keyword_coverage, 2),
            "keyword_hits": keyword_hits,
        })

    avg_score = sum(r["eval"]["average"] for r in results) / len(results) if results else 0
    pass_rate = sum(1 for r in results if r["eval"]["passed"]) / len(results) if results else 0

    return {
        "total": len(results),
        "avg_score": round(avg_score, 2),
        "pass_rate": round(pass_rate, 2),
        "details": results,
    }

if __name__ == "__main__":
    test_cases = [
        TestCase(
            question="What is Python's GIL?",
            context="The GIL (Global Interpreter Lock) is a mutex in CPython that allows only one thread to execute Python bytecode at a time. The GIL is released during I/O operations.",
            expected_keywords=["mutex", "thread", "CPython"],
        ),
        TestCase(
            question="What is the difference between a list and a tuple?",
            context="Lists are mutable data structures. Tuples are immutable — they cannot be changed after creation. Tuples can be used as dictionary keys; lists cannot.",
            expected_keywords=["mutable", "immutable", "dictionary"],
        ),
    ]

    report = run_eval_suite(test_cases)
    print(json.dumps(report, indent=2))
```

---

## Limits of automated evaluation

LLM-as-judge is fast and scalable, but the judge model may share biases with the responder model. For high-stakes domains — medical, legal, financial — a human review layer is non-negotiable.

Keyword coverage and format checks are fully automatable. LLM-as-judge adds semantic quality scoring on top. Combining all three layers gives you a reliable quality gate without manual inspection at scale.

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

- [RAGAS evaluation framework](https://docs.ragas.io/)
- [LangChain evaluation module](https://python.langchain.com/docs/guides/evaluation/)
- [G-Eval paper](https://arxiv.org/abs/2303.16634)

Tags: LLMOps, Observability, Python, LLM
