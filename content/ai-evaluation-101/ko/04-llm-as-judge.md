---
title: "AI Evaluation 101 (4/10): LLM-as-Judge — 모델로 모델을 평가하기"
series: ai-evaluation-101
episode: 4
language: ko
status: publish-ready
targets:
  - tistory
  - github
tags:
  - LLM평가
  - LLM-as-Judge
  - AI품질관리
  - 프롬프트엔지니어링
  - MLOps
seo_description: "LLM-as-Judge 패턴의 3가지 방식(pointwise, pairwise, reference-based)과 위치·길이·자기선호 편향을 실전 코드로 완전 정복합니다."
last_reviewed: '2026-06-20'
---

# AI Evaluation 101 (4/10): LLM-as-Judge — 모델로 모델을 평가하기

> **시리즈 안내:** 이 글은 *AI Evaluation 101* 시리즈의 네 번째 글입니다. 앞선 글에서 결정론적 메트릭(Exact Match, ROUGE)을 다뤘습니다. 이번에는 사람이 작성한 정답이 없어도 품질을 측정할 수 있는 **LLM-as-Judge** 패턴을 다룹니다.

![LLM-as-Judge 개념도](../images/04-llm-as-judge.png)
*그림: 채점자 LLM이 생성 모델의 출력을 평가하는 구조. 좌측이 피평가 모델, 우측이 Judge 모델.*

사람이 매번 응답을 검토하면 정밀하지만 비용과 시간이 너무 많이 듭니다. 정해진 정답(reference)이 없는 창작, 요약, 상담 응답을 ROUGE나 Exact Match로 측정하면 실제 품질과 상관관계가 낮습니다. **LLM-as-Judge**는 GPT-4나 Claude 같은 강력한 모델을 채점자로 사용해 이 공백을 메웁니다. 단, 채점자 모델도 편향을 갖고 있으므로 그 편향을 이해하고 설계해야 합니다.

---

## 이 글에서 다룰 문제

1. LLM-as-Judge는 언제 쓰고 언제 피해야 하는가?
2. Pointwise, Pairwise, Reference-based 방식의 차이는 무엇인가?
3. 위치 편향·길이 편향·자기선호 편향을 어떻게 측정하고 완화하는가?
4. Judge 프롬프트를 어떻게 설계해야 안정적인 점수가 나오는가?
5. Human Agreement Rate로 Judge 신뢰도를 어떻게 검증하는가?

---

## 핵심 개념 한 줄 정리

| 개념 | 설명 |
|------|------|
| **Pointwise** | 응답 하나를 절대 기준으로 1-5점 채점 |
| **Pairwise** | 두 응답을 나란히 놓고 승패 비교 |
| **Reference-based** | 정답 예시와 비교해 유사도·정확도 채점 |
| **위치 편향** | Judge가 프롬프트에서 먼저 나온 응답에 유리하게 채점하는 현상 |
| **길이 편향** | 더 긴 응답을 더 좋은 응답으로 착각하는 현상 |
| **자기선호 편향** | 같은 회사 모델의 출력을 높이 평가하는 현상 |
| **Human Agreement Rate** | Judge 점수와 사람 레이블의 일치율 (목표 ≥ 85%) |

---

## Judge 방식 비교

| 구분 | Pointwise | Pairwise | Reference-based |
|------|-----------|----------|-----------------|
| **정답 필요?** | 불필요 | 불필요 | 필요 |
| **속도** | 빠름 | 느림 (2배 호출) | 빠름 |
| **편향 위험** | 기준 모호성 | 위치 편향 강함 | 정답 품질에 의존 |
| **적합 용도** | 절대 품질 트래킹 | 모델 A vs B 비교 | QA, 사실 확인 |
| **점수 안정성** | 중간 | 낮음 (순서 swap 필요) | 높음 |

---

## 1. Pointwise Judge — 절대 채점

### 프롬프트 설계

Judge 프롬프트의 핵심은 **채점 기준을 숫자 앵커로 명확히 고정**하는 것입니다. "좋은 응답"처럼 모호한 기준을 쓰면 Judge 자체가 할루시네이션합니다.

```python
POINTWISE_JUDGE_PROMPT = """\
당신은 AI 응답 품질을 평가하는 전문 채점자입니다.

## 평가 기준
아래 루브릭에 따라 1-5점 정수로 채점하세요.

5점: 질문에 완전히 답변하며 사실이 정확하고 간결함
4점: 질문에 대부분 답변하나 사소한 불완전함이 있음
3점: 질문에 부분적으로 답변하거나 관련 없는 내용이 포함됨
2점: 질문에 거의 답변하지 못하거나 오류가 있음
1점: 질문과 무관하거나 명백히 잘못된 정보를 제공함

## 입력
질문: {question}
응답: {answer}

## 출력 형식 (JSON만 출력, 다른 텍스트 금지)
{{
  "score": <1-5 정수>,
  "reason": "<30자 이내 채점 근거>"
}}
"""
```

### 구현: 안정적인 JSON 파싱

```python
import json
import re
from dataclasses import dataclass
from openai import OpenAI

client = OpenAI()

@dataclass
class JudgeResult:
    score: int
    reason: str
    raw_response: str

def pointwise_judge(
    question: str,
    answer: str,
    model: str = "gpt-4o",
    temperature: float = 0.0,
) -> JudgeResult:
    """Pointwise LLM-as-Judge 채점."""
    prompt = POINTWISE_JUDGE_PROMPT.format(
        question=question,
        answer=answer,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,  # 재현성을 위해 0으로 고정
        response_format={"type": "json_object"},  # JSON 모드 강제
    )

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
        score = int(data["score"])
        if not 1 <= score <= 5:
            raise ValueError(f"점수 범위 초과: {score}")
        return JudgeResult(score=score, reason=data["reason"], raw_response=raw)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # 파싱 실패 시 정규식으로 점수 추출
        match = re.search(r'"score"\s*:\s*(\d)', raw)
        if match:
            return JudgeResult(
                score=int(match.group(1)),
                reason="파싱 폴백",
                raw_response=raw,
            )
        raise RuntimeError(f"Judge 응답 파싱 실패: {e}\n원문: {raw}")


# 사용 예시
result = pointwise_judge(
    question="파이썬에서 리스트와 튜플의 차이는?",
    answer="리스트는 변경 가능하고 튜플은 변경 불가능합니다.",
)
print(f"점수: {result.score}/5 — {result.reason}")
# 출력: 점수: 3/5 — 기본 차이는 맞지만 사용 시나리오 누락
```

---

## 2. Pairwise Judge — 승패 비교

Pairwise는 "A가 더 좋다 / B가 더 좋다 / 동등하다" 세 가지로 판정합니다. **위치 편향**이 강하게 나타나므로 반드시 순서를 바꾸어 두 번 호출한 뒤 결과를 집계해야 합니다.

```python
from enum import Enum
from typing import Optional

class PairwiseVerdict(str, Enum):
    A_WINS = "A"
    B_WINS = "B"
    TIE = "TIE"

PAIRWISE_PROMPT = """\
두 AI 응답 중 어느 것이 더 나은지 판정하세요.

질문: {question}

[응답 A]
{answer_a}

[응답 B]
{answer_b}

판정 기준: 정확성 > 완전성 > 간결성

JSON으로만 출력:
{{"winner": "A" | "B" | "TIE", "reason": "<30자 이내>"}}
"""

def pairwise_judge(
    question: str,
    answer_a: str,
    answer_b: str,
    model: str = "gpt-4o",
) -> dict:
    """위치 편향 제거를 위해 순서를 바꿔 두 번 호출."""

    def _call(q, a, b) -> PairwiseVerdict:
        prompt = PAIRWISE_PROMPT.format(question=q, answer_a=a, answer_b=b)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        return PairwiseVerdict(data["winner"])

    # 정방향: A=answer_a, B=answer_b
    verdict_fwd = _call(question, answer_a, answer_b)
    # 역방향: A=answer_b, B=answer_a (레이블 반전 필요)
    verdict_rev_raw = _call(question, answer_b, answer_a)
    verdict_rev = {
        PairwiseVerdict.A_WINS: PairwiseVerdict.B_WINS,
        PairwiseVerdict.B_WINS: PairwiseVerdict.A_WINS,
        PairwiseVerdict.TIE: PairwiseVerdict.TIE,
    }[verdict_rev_raw]

    # 두 결과가 일치하면 확정, 불일치하면 TIE 처리
    if verdict_fwd == verdict_rev:
        final = verdict_fwd
        consistent = True
    else:
        final = PairwiseVerdict.TIE
        consistent = False

    return {
        "verdict": final.value,
        "consistent": consistent,
        "forward": verdict_fwd.value,
        "reversed": verdict_rev.value,
    }


# 사용 예시
result = pairwise_judge(
    question="머신러닝에서 과적합이란?",
    answer_a="훈련 데이터에 너무 맞춰져 새 데이터에서 성능이 낮아지는 현상입니다.",
    answer_b="과적합은 모델 복잡도가 높을 때 발생하며 드롭아웃, 정규화로 방지합니다.",
)
print(result)
# {'verdict': 'B', 'consistent': True, 'forward': 'B', 'reversed': 'B'}
```

---

## 3. Reference-based Judge — 정답 비교

정답 예시(reference)가 있을 때 Judge에게 정답과 비교해 채점하도록 지시합니다. QA 시스템에서 가장 신뢰도 높은 방식입니다.

```python
REFERENCE_JUDGE_PROMPT = """\
정답 예시와 비교해 AI 응답의 품질을 채점하세요.

질문: {question}
정답 예시: {reference}
AI 응답: {answer}

채점 기준:
- 사실 일치도 (0-5): 정답의 핵심 사실을 얼마나 포함하는가
- 추가 오류 (0-5): 정답에 없는 잘못된 정보가 있는가 (없으면 5점)

JSON으로만 출력:
{{"factual_match": <0-5>, "no_hallucination": <0-5>, "reason": "<30자>"}}
"""

def reference_judge(
    question: str,
    reference: str,
    answer: str,
    model: str = "gpt-4o",
) -> dict:
    prompt = REFERENCE_JUDGE_PROMPT.format(
        question=question,
        reference=reference,
        answer=answer,
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    composite = (data["factual_match"] * 0.6 + data["no_hallucination"] * 0.4)
    data["composite_score"] = round(composite, 2)
    return data
```

---

## 4. 편향 측정 및 완화

### 위치 편향 측정

```python
import pandas as pd

def measure_position_bias(
    eval_cases: list[dict],
    model: str = "gpt-4o",
) -> float:
    """
    위치 편향 계수 반환 (0에 가까울수록 편향 없음).
    eval_cases: [{"question": ..., "answer_a": ..., "answer_b": ...}, ...]
    """
    first_wins = 0
    total = len(eval_cases)

    for case in eval_cases:
        fwd = _single_pairwise(case["question"], case["answer_a"], case["answer_b"], model)
        rev = _single_pairwise(case["question"], case["answer_b"], case["answer_a"], model)
        # 정방향에서 A가 이기고 역방향에서도 A(=원래 B)가 이기면 위치 편향
        if fwd == "A" and rev == "A":
            first_wins += 1

    bias_rate = first_wins / total
    print(f"위치 편향 비율: {bias_rate:.1%} (기준: < 20%)")
    return bias_rate

def _single_pairwise(question, a, b, model) -> str:
    prompt = PAIRWISE_PROMPT.format(question=question, answer_a=a, answer_b=b)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)["winner"]
```

### 길이 편향 측정

```python
def measure_length_bias(
    eval_cases: list[dict],
    model: str = "gpt-4o",
) -> float:
    """
    Judge가 더 긴 응답을 얼마나 선호하는지 측정.
    반환값: 긴 응답 선호율 (기준: < 60%)
    """
    longer_wins = 0
    total = len(eval_cases)

    for case in eval_cases:
        a, b = case["answer_a"], case["answer_b"]
        result = pairwise_judge(case["question"], a, b, model)
        winner = result["verdict"]

        a_longer = len(a) > len(b)
        if (winner == "A" and a_longer) or (winner == "B" and not a_longer):
            longer_wins += 1

    bias_rate = longer_wins / total
    print(f"길이 편향 비율: {bias_rate:.1%} (기준: < 60%)")
    return bias_rate
```

### 완화 전략 정리

```python
# 전략 1: 길이 제한 지시문 추가
LENGTH_PENALTY_INSTRUCTION = """
평가 시 응답 길이는 무시하세요. 짧지만 정확한 응답이 길지만 부정확한 응답보다 낫습니다.
"""

# 전략 2: Chain-of-Thought 채점 (이유 먼저 작성 후 점수)
COT_JUDGE_SUFFIX = """
먼저 각 기준에 대한 분석을 작성한 다음, 최종 점수를 JSON으로 출력하세요.
분석: <여기에 분석 작성>
JSON: {"score": ..., "reason": ...}
"""

# 전략 3: 앙상블 (여러 Judge 모델 평균)
def ensemble_judge(question: str, answer: str, judges: list[str]) -> float:
    scores = []
    for judge_model in judges:
        result = pointwise_judge(question, answer, model=judge_model)
        scores.append(result.score)
    return sum(scores) / len(scores)

# 사용 예시
avg_score = ensemble_judge(
    question="HTTP와 HTTPS의 차이는?",
    answer="HTTPS는 SSL/TLS로 암호화된 HTTP입니다.",
    judges=["gpt-4o", "gpt-4o-mini"],
)
print(f"앙상블 점수: {avg_score:.1f}/5")
```

---

## 5. Human Agreement Rate — Judge 신뢰도 검증

Judge를 실제 배포 전에 반드시 사람 레이블과 비교해야 합니다. 목표는 **85% 이상 일치**입니다.

```python
from sklearn.metrics import cohen_kappa_score
import numpy as np

def compute_human_agreement(
    human_scores: list[int],
    judge_scores: list[int],
    tolerance: int = 1,
) -> dict:
    """
    human_scores: 사람 채점자 점수 리스트
    judge_scores: LLM Judge 점수 리스트
    tolerance: 허용 오차 (기본 1점 이내이면 일치로 간주)
    """
    assert len(human_scores) == len(judge_scores)

    exact_matches = sum(h == j for h, j in zip(human_scores, judge_scores))
    tolerance_matches = sum(
        abs(h - j) <= tolerance for h, j in zip(human_scores, judge_scores)
    )
    n = len(human_scores)

    # Cohen's Kappa: 우연 일치를 보정한 일치도
    kappa = cohen_kappa_score(human_scores, judge_scores)

    return {
        "exact_agreement": exact_matches / n,
        "tolerance_agreement": tolerance_matches / n,
        "cohen_kappa": round(kappa, 3),
        "sample_size": n,
        "pass": tolerance_matches / n >= 0.85,
    }


# 사용 예시 (50개 케이스 검증)
human = [4, 3, 5, 2, 4, 3, 5, 5, 2, 3]  # 실제 사람 점수
judge = [4, 3, 5, 3, 4, 3, 4, 5, 2, 3]  # LLM Judge 점수

result = compute_human_agreement(human, judge)
print(result)
# {
#   'exact_agreement': 0.8,
#   'tolerance_agreement': 0.9,
#   'cohen_kappa': 0.743,
#   'sample_size': 10,
#   'pass': True
# }

if not result["pass"]:
    print("경고: Judge 신뢰도 부족. 프롬프트 재설계 필요.")
```

---

## 6. 실전 Judge 파이프라인

```python
import asyncio
from dataclasses import dataclass, field

@dataclass
class EvalCase:
    question: str
    answer: str
    reference: str | None = None
    judge_score: int | None = None
    judge_reason: str | None = None

async def run_judge_pipeline(
    cases: list[EvalCase],
    judge_model: str = "gpt-4o",
    concurrency: int = 5,
) -> list[EvalCase]:
    """비동기 Judge 파이프라인 (동시 5개 호출)."""
    sem = asyncio.Semaphore(concurrency)

    async def _judge_one(case: EvalCase) -> EvalCase:
        async with sem:
            result = pointwise_judge(case.question, case.answer, model=judge_model)
            case.judge_score = result.score
            case.judge_reason = result.reason
            return case

    return await asyncio.gather(*[_judge_one(c) for c in cases])


async def main():
    cases = [
        EvalCase(question="파이썬 GIL이란?", answer="글로벌 인터프리터 락으로 멀티스레딩을 제한합니다."),
        EvalCase(question="REST API란?", answer="HTTP 기반 무상태 인터페이스 설계 원칙입니다."),
        EvalCase(question="SQL JOIN 종류는?", answer="INNER, LEFT, RIGHT, FULL OUTER JOIN이 있습니다."),
    ]

    results = await run_judge_pipeline(cases)

    for r in results:
        print(f"[{r.judge_score}/5] {r.question[:20]}... — {r.judge_reason}")
        # [4/5] 파이썬 GIL이란?... — 핵심 정의 맞으나 예시 부재
        # [5/5] REST API란?... — 정확하고 간결함
        # [5/5] SQL JOIN 종류는?... — 모든 종류 포함

asyncio.run(main())
```

---

## 운영 체크리스트

- [ ] Judge 프롬프트에 숫자 앵커(각 점수별 설명) 포함
- [ ] Temperature = 0.0으로 고정해 재현성 확보
- [ ] JSON 모드 강제 (`response_format={"type": "json_object"}`)
- [ ] Pairwise 사용 시 순서 swap 두 번 호출
- [ ] 위치 편향 비율 < 20% 검증
- [ ] 길이 편향 비율 < 60% 검증
- [ ] Human Agreement Rate ≥ 85% 달성 후 배포
- [ ] 앙상블 Judge (2개 이상 모델) 고비용 케이스에 적용
- [ ] Judge 호출 비용 모니터링 (token/case × 케이스 수)

---

## 자주 하는 실수

| 실수 | 증상 | 해결책 |
|------|------|--------|
| Judge 프롬프트에 앵커 없음 | 같은 응답에 매번 다른 점수 | 각 점수별 구체적 기준 문장 추가 |
| Temperature > 0 사용 | 점수 분산이 커서 신뢰 불가 | `temperature=0.0` 고정 |
| Pairwise를 한 방향만 호출 | 위치 편향 결과를 신뢰함 | 순서 swap 두 번 호출 필수 |
| JSON 파싱 에러 무시 | 잘못된 점수가 DB에 저장됨 | 파싱 실패 시 예외 처리 + 재시도 |
| Human Agreement 검증 생략 | 엉터리 Judge를 배포에 사용 | 최소 50개 케이스로 반드시 검증 |
| 자기 회사 모델을 Judge로 사용 | 자기선호 편향으로 점수 과장 | 서로 다른 벤더 모델 사용 권장 |
| Judge 비용 예측 없이 배포 | 월 수십만 원 청구 폭탄 | 케이스 수 × 토큰 × 단가 사전 계산 |

---

## 처음 질문으로 돌아가기

**Q1. LLM-as-Judge는 언제 쓰고 언제 피해야 하는가?**
정답이 하나로 정해지지 않는 생성 작업(창작, 요약, 상담)에는 LLM-as-Judge가 효과적입니다. 반면 사실 확인처럼 정답이 명확할 때는 Exact Match나 Reference-based 방식이 더 저렴하고 신뢰도가 높습니다.

**Q2. Pointwise, Pairwise, Reference-based 방식의 차이는?**
Pointwise는 절대 품질을 빠르게 추적할 때, Pairwise는 두 모델을 직접 비교할 때, Reference-based는 정답 데이터셋이 있는 QA 시스템에 씁니다. 비용 대비 효과는 Pointwise > Reference-based > Pairwise 순입니다.

**Q3. 편향을 어떻게 측정하고 완화하는가?**
위치 편향은 순서 swap 두 번 호출로 측정하고, 불일치 시 TIE 처리합니다. 길이 편향은 Judge 프롬프트에 "길이 무시" 지시를 추가합니다. 자기선호 편향은 서로 다른 벤더 모델 앙상블로 완화합니다.

**Q4. Judge 프롬프트는 어떻게 설계해야 하는가?**
각 점수(1-5)에 구체적 기준 문장을 달고, JSON 출력 모드를 강제하며, Temperature를 0으로 고정합니다. "좋다/나쁘다"처럼 모호한 기준 대신 "질문에 완전히 답변하며 사실이 정확하다"처럼 행동 기반으로 서술합니다.

**Q5. Human Agreement Rate로 어떻게 신뢰도를 검증하는가?**
최소 50개 케이스를 사람이 먼저 채점한 뒤 Judge 결과와 비교합니다. 1점 오차 허용 일치율 ≥ 85%가 배포 기준이며, Cohen's Kappa ≥ 0.6이면 중간 수준의 일치도로 수용 가능합니다.

---

<!-- toc:begin -->
## 목차
1. [Judge 방식 비교](#judge-방식-비교)
2. [Pointwise Judge](#1-pointwise-judge--절대-채점)
3. [Pairwise Judge](#2-pairwise-judge--승패-비교)
4. [Reference-based Judge](#3-reference-based-judge--정답-비교)
5. [편향 측정 및 완화](#4-편향-측정-및-완화)
6. [Human Agreement Rate](#5-human-agreement-rate--judge-신뢰도-검증)
7. [실전 Judge 파이프라인](#6-실전-judge-파이프라인)
<!-- toc:end -->

---

## 참고 자료

- Zheng et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685
- Pangakis et al. (2023). *Automated Annotation with Generative AI Requires Validation*. arXiv:2306.00176
- OpenAI. *GPT-4 System Card* — 자기선호 편향 관련 섹션
- LangChain Docs. [LLM-as-Judge Evaluators](https://docs.langchain.com/docs/guides/evaluation/string/criteria_eval_chain)
- LMSYS Chatbot Arena. [Bradley-Terry 모델 기반 Elo 랭킹](https://chat.lmsys.org/)
