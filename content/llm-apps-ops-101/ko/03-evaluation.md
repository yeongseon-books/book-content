# LLM 출력 품질 평가

> LLM 앱 운영 101 (3/6)

모델을 교체하거나 프롬프트를 수정할 때 "더 좋아졌는가"를 어떻게 판단하나요? 사람이 직접 읽어보는 것도 방법이지만, 수천 건의 응답을 수작업으로 검토할 수는 없습니다. 이 포스트에서는 LLM-as-judge 패턴, 사실 일관성 검사, 형식 준수 검사로 자동 평가 파이프라인을 구축합니다.

---

## 평가의 세 축

LLM 출력 품질은 세 가지 차원에서 측정합니다.

- **관련성**: 질문에 제대로 답했는가
- **사실 일관성**: 주어진 컨텍스트와 모순되지 않는가
- **형식 준수**: 요청한 구조(JSON, 불릿, 길이 제한)를 지켰는가

셋 중 하나라도 실패하면 사용자 경험에 직접적인 영향을 줍니다.

---

## LLM-as-judge 평가기

```python
import json
import os
import re
from dataclasses import dataclass
from typing import Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

JUDGE_SYSTEM = """당신은 AI 응답 품질 평가 전문가입니다.
주어진 질문, 컨텍스트, 응답을 보고 다음 세 가지를 1–5점으로 평가하세요.

평가 기준:
- relevance: 질문에 직접 답하는가 (1=전혀 무관, 5=완전히 답변)
- faithfulness: 컨텍스트 내용에만 근거하는가 (1=환각 심각, 5=컨텍스트만 사용)
- completeness: 질문의 모든 부분을 다루는가 (1=핵심 누락, 5=완전히 포괄)

반드시 아래 JSON 형식으로만 응답하세요:
{"relevance": <1-5>, "faithfulness": <1-5>, "completeness": <1-5>, "reason": "<한 문장 근거>"}"""

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
    def __init__(self, judge_model: str = "llama-3.1-8b-instant"):
        self.llm = ChatGroq(
            model=judge_model,
            api_key=os.environ["GROQ_API_KEY"],
            temperature=0.0,
        )

    def evaluate(self, question: str, context: str, response: str) -> EvalResult:
        user_msg = f"질문: {question}\n\n컨텍스트: {context}\n\n응답: {response}"
        messages = [
            SystemMessage(content=JUDGE_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        raw = self.llm.invoke(messages).content

        try:
            # JSON 블록 추출
            match = re.search(r"\{[^}]+\}", raw, re.DOTALL)
            if not match:
                raise ValueError("JSON 없음")
            data = json.loads(match.group())
            return EvalResult(
                relevance=float(data.get("relevance", 3)),
                faithfulness=float(data.get("faithfulness", 3)),
                completeness=float(data.get("completeness", 3)),
                reason=data.get("reason", ""),
                raw=raw,
            )
        except Exception:
            return EvalResult(relevance=3.0, faithfulness=3.0, completeness=3.0, reason="파싱 실패", raw=raw)
```

---

## 형식 준수 검사기

```python
import re
from typing import Callable

@dataclass
class FormatCheck:
    name: str
    passed: bool
    detail: str = ""

class FormatChecker:
    """응답이 요청된 형식을 지켰는지 검사합니다."""

    def check_json(self, text: str) -> FormatCheck:
        try:
            json.loads(text.strip())
            return FormatCheck("json", True)
        except json.JSONDecodeError as e:
            return FormatCheck("json", False, str(e))

    def check_max_length(self, text: str, max_chars: int) -> FormatCheck:
        if len(text) <= max_chars:
            return FormatCheck("max_length", True)
        return FormatCheck("max_length", False, f"{len(text)} > {max_chars}자")

    def check_bullet_list(self, text: str, min_items: int = 2) -> FormatCheck:
        bullets = re.findall(r"^[-*•]\s+.+", text, re.MULTILINE)
        if len(bullets) >= min_items:
            return FormatCheck("bullet_list", True, f"{len(bullets)}개")
        return FormatCheck("bullet_list", False, f"{len(bullets)} < {min_items}개")

    def check_no_hallucination_markers(self, text: str) -> FormatCheck:
        """모델이 불확실성을 표현하는 패턴을 탐지합니다."""
        patterns = [
            r"I (?:think|believe|guess|suppose)",
            r"(?:might|may|could) be",
            r"I'm not (?:sure|certain)",
            r"(?:approximately|roughly|about) \d",
        ]
        found = [p for p in patterns if re.search(p, text, re.IGNORECASE)]
        if not found:
            return FormatCheck("no_hallucination_markers", True)
        return FormatCheck("no_hallucination_markers", False, f"발견된 패턴: {found}")
```

---

## 배치 평가 파이프라인

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
    """테스트 케이스 배치 평가를 실행합니다."""
    responder = ChatGroq(
        model=responder_model, api_key=os.environ["GROQ_API_KEY"], temperature=0.0
    )
    judge = LLMJudge(judge_model)
    checker = FormatChecker()

    results = []
    for tc in test_cases:
        # 응답 생성
        prompt = f"컨텍스트:\n{tc.context}\n\n질문: {tc.question}"
        response = responder.invoke([HumanMessage(content=prompt)]).content

        # 품질 평가
        eval_result = judge.evaluate(tc.question, tc.context, response)

        # 키워드 포함 여부 검사
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
            question="파이썬 GIL이란 무엇인가요?",
            context="GIL(Global Interpreter Lock)은 CPython 인터프리터에서 한 번에 하나의 스레드만 Python 바이트코드를 실행하도록 제한하는 뮤텍스입니다. I/O 바운드 작업에서는 GIL이 해제됩니다.",
            expected_keywords=["뮤텍스", "스레드", "CPython"],
        ),
        TestCase(
            question="리스트와 튜플의 차이는?",
            context="리스트는 가변(mutable) 자료구조입니다. 튜플은 불변(immutable) 자료구조로, 생성 후 변경할 수 없습니다. 튜플은 딕셔너리 키로 사용할 수 있습니다.",
            expected_keywords=["가변", "불변", "딕셔너리"],
        ),
    ]

    report = run_eval_suite(test_cases)
    print(json.dumps(report, indent=2, ensure_ascii=False))
```

---

## 평가 자동화의 한계

LLM-as-judge는 빠르고 확장 가능하지만, 평가 모델이 응답 모델과 같은 편향을 공유할 수 있습니다. 고위험 영역(의료, 법률, 금융)에서는 인간 검토 레이어를 반드시 유지해야 합니다.

키워드 커버리지와 형식 검사는 자동화가 완전히 가능합니다. LLM-as-judge는 이 두 가지가 통과한 응답의 의미적 품질을 추가로 검증하는 데 씁니다. 세 레이어를 조합하면 수작업 없이도 신뢰할 수 있는 품질 게이트를 만들 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- [LLM 비용 추적과 최적화](./02-cost-tracking.md)
- **LLM 출력 품질 평가 (현재 글)**
- LLM 앱 보안 (예정)
- LLM 앱 배포 전략 (예정)
- LLM 앱 운영 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [RAGAS 평가 프레임워크](https://docs.ragas.io/)
- [LangChain 평가 모듈](https://python.langchain.com/docs/guides/evaluation/)
- [G-Eval 논문](https://arxiv.org/abs/2303.16634)

Tags: LLMOps, Observability, Python, LLM
