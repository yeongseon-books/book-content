---
series: ai-evaluation-101
episode: 1
title: "AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - LLMEvaluation
  - Testing
  - CI
  - Quality
  - Pipeline
seo_description: LLM 앱 평가가 필요한 이유, 4단계 평가 파이프라인, 최소 10케이스 원칙, CI 통합 방법을 정리합니다
last_reviewed: '2026-06-20'
---

# AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가

LLM 애플리케이션은 전통적인 소프트웨어와 다릅니다. 동일한 입력에도 비결정적 출력이 나올 수 있고, 프롬프트 한 줄만 바꿔도 전체 동작이 바뀝니다. 모델을 업그레이드하면 일부 케이스는 좋아지지만 다른 케이스가 나빠질 수 있습니다. 이런 특성 때문에 전통적인 단위 테스트만으로는 품질을 보증할 수 없습니다. 체계적인 평가 파이프라인이 없으면 "느낌적으로 좋아진 것 같다"는 판단에 의존하게 됩니다.

이 글은 AI Evaluation 101 시리즈의 1번째 글입니다.

![LLM 평가 파이프라인 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-01-concept-at-a-glance.ko.png)
*LLM 앱 평가의 4단계 파이프라인 구조*

## 이 글에서 다룰 문제

- LLM 앱을 기존 소프트웨어와 같은 방식으로 테스트하기 어려운 이유는 무엇일까요?
- 평가 파이프라인을 구축하지 않으면 어떤 문제가 발생할까요?
- 최소 몇 개의 테스트 케이스가 있어야 의미 있는 평가가 될까요?
- CI/CD 파이프라인에 LLM 평가를 어떻게 통합할 수 있을까요?
- 평가 결과를 어떻게 해석하고 의사결정에 활용할 수 있을까요?

## 핵심 개념 한 줄 정리

- **Golden Dataset**: 검증된 입력-정답 쌍으로 구성된 평가 기준 데이터셋입니다.
- **Regression**: 이전 버전보다 성능이 낮아지는 현상으로, 평가 없이는 감지하기 어렵습니다.
- **Deterministic Metric**: 정답과 예측을 비교해 계산하는 Exact Match, BLEU 같은 지표입니다.
- **LLM-as-Judge**: LLM이 다른 LLM의 출력을 평가하는 방식입니다.
- **Eval Pipeline**: 데이터셋 → 실행 → 채점 → 리포트의 4단계로 구성된 평가 흐름입니다.

## LLM 평가가 어려운 이유

| 특성 | 전통적 소프트웨어 | LLM 애플리케이션 |
|---|---|---|
| 결정성 | 동일 입력 → 동일 출력 | 동일 입력 → 다양한 출력 |
| 테스트 방법 | 단위 테스트, 통합 테스트 | 평가 데이터셋 + 채점 모델 |
| 실패 정의 | 예외 발생, 잘못된 반환값 | 품질 저하, 환각, 불완전한 답변 |
| 변경 영향 | 코드 변경으로 추적 | 프롬프트 변경이 비선형적 영향 |
| 회귀 감지 | 기존 테스트가 자동 감지 | 평가 파이프라인 없으면 수동 확인 |

## 실습 1: 기본 평가 파이프라인

4단계 평가 파이프라인을 구현합니다: 데이터셋 로드 → 모델 실행 → 채점 → 리포트.

```python
from openai import OpenAI
from dataclasses import dataclass
import json
from datetime import datetime

client = OpenAI()


@dataclass
class EvalCase:
    case_id: str
    input: str
    expected: str
    category: str = "general"
    metadata: dict = None


@dataclass
class EvalResult:
    case_id: str
    input: str
    expected: str
    actual: str
    passed: bool
    score: float
    latency_ms: float


def run_model(prompt: str, system: str = "") -> tuple[str, float]:
    """모델을 실행하고 응답과 레이턴시를 반환합니다."""
    import time
    start = time.time()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=512,
        temperature=0,  # 결정적 출력을 위해 temperature=0 사용
    )

    latency = (time.time() - start) * 1000
    return response.choices[0].message.content, latency


def score_exact_match(expected: str, actual: str) -> float:
    """정확 일치 여부를 확인합니다."""
    return 1.0 if expected.strip().lower() == actual.strip().lower() else 0.0


def score_contains_keywords(expected: str, actual: str) -> float:
    """정답의 핵심 키워드가 응답에 포함되었는지 확인합니다."""
    keywords = [w for w in expected.lower().split() if len(w) > 3]
    if not keywords:
        return 0.0
    found = sum(1 for kw in keywords if kw in actual.lower())
    return found / len(keywords)


def run_eval_pipeline(
    cases: list[EvalCase],
    system_prompt: str = "",
    scorer: str = "keywords",
    pass_threshold: float = 0.7,
) -> dict:
    """평가 파이프라인을 실행하고 결과를 반환합니다."""
    results = []

    for case in cases:
        actual, latency = run_model(case.input, system_prompt)

        if scorer == "exact":
            score = score_exact_match(case.expected, actual)
        else:
            score = score_contains_keywords(case.expected, actual)

        results.append(EvalResult(
            case_id=case.case_id,
            input=case.input,
            expected=case.expected,
            actual=actual,
            passed=score >= pass_threshold,
            score=score,
            latency_ms=latency,
        ))

    passed = sum(1 for r in results if r.passed)
    return {
        "total": len(results),
        "passed": passed,
        "pass_rate": passed / len(results) if results else 0.0,
        "avg_score": sum(r.score for r in results) / len(results) if results else 0.0,
        "avg_latency_ms": sum(r.latency_ms for r in results) / len(results) if results else 0.0,
        "results": results,
        "timestamp": datetime.utcnow().isoformat(),
    }


# 최소 10케이스 예시
eval_cases = [
    EvalCase("e001", "파이썬에서 리스트를 정렬하는 방법은?", "sort() 또는 sorted()"),
    EvalCase("e002", "HTTP 상태 코드 404는 무엇을 의미하나요?", "Not Found"),
    EvalCase("e003", "Python의 GIL이란 무엇인가요?", "Global Interpreter Lock"),
    EvalCase("e004", "REST와 GraphQL의 차이는?", "쿼리 방식, 오버페칭"),
    EvalCase("e005", "도커(Docker)란 무엇인가요?", "컨테이너 플랫폼"),
    EvalCase("e006", "SQL의 JOIN 유형을 설명하세요.", "INNER, LEFT, RIGHT, FULL"),
    EvalCase("e007", "비동기 프로그래밍이란 무엇인가요?", "async await"),
    EvalCase("e008", "머신러닝과 딥러닝의 차이는?", "신경망 레이어"),
    EvalCase("e009", "API란 무엇인가요?", "Application Programming Interface"),
    EvalCase("e010", "클라우드 컴퓨팅의 장점은?", "확장성, 비용 효율"),
]

report = run_eval_pipeline(
    eval_cases,
    system_prompt="당신은 IT 기술 전문가입니다. 간결하고 정확하게 답하세요.",
)
print(f"통과율: {report['pass_rate']:.1%} ({report['passed']}/{report['total']})")
print(f"평균 점수: {report['avg_score']:.3f}")
print(f"평균 레이턴시: {report['avg_latency_ms']:.0f}ms")
```

## 실습 2: CI 통합 평가

GitHub Actions에서 LLM 평가를 자동으로 실행하고 회귀를 감지합니다.

```python
import sys
import json
from pathlib import Path


def load_baseline(path: str) -> dict:
    """이전 평가 결과(기준선)를 로드합니다."""
    baseline_file = Path(path)
    if not baseline_file.exists():
        return {}
    return json.loads(baseline_file.read_text())


def save_results(results: dict, path: str) -> None:
    """평가 결과를 파일로 저장합니다."""
    Path(path).write_text(
        json.dumps(
            {
                "pass_rate": results["pass_rate"],
                "avg_score": results["avg_score"],
                "timestamp": results["timestamp"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def check_regression(
    current: dict,
    baseline: dict,
    max_drop: float = 0.05,
) -> tuple[bool, str]:
    """현재 결과와 기준선을 비교해 회귀 여부를 판단합니다."""
    if not baseline:
        return True, "기준선 없음, 첫 실행으로 저장"

    current_rate = current["pass_rate"]
    baseline_rate = baseline.get("pass_rate", 0.0)
    drop = baseline_rate - current_rate

    if drop > max_drop:
        return False, (
            f"회귀 감지: 통과율 {baseline_rate:.1%} → {current_rate:.1%} "
            f"({drop:.1%} 하락, 허용 최대: {max_drop:.1%})"
        )
    return True, f"통과: {current_rate:.1%} (기준선: {baseline_rate:.1%})"


# CI 실행 예시
BASELINE_PATH = "eval_baseline.json"
RESULTS_PATH = "eval_results.json"

report = run_eval_pipeline(eval_cases)
baseline = load_baseline(BASELINE_PATH)
passed, message = check_regression(report, baseline)

print(f"[CI Eval] {message}")
save_results(report, RESULTS_PATH)

if not passed:
    print("[CI] 평가 실패: PR 병합 차단")
    sys.exit(1)
else:
    print("[CI] 평가 통과")
    # 처음 실행이거나 성능 향상 시 기준선 업데이트
    if not baseline or report["pass_rate"] > baseline.get("pass_rate", 0.0):
        save_results(report, BASELINE_PATH)
        print("[CI] 기준선 업데이트")
```

## 실습 3: 카테고리별 실패 분석

어떤 카테고리에서 실패가 집중되는지 분석합니다.

```python
from collections import defaultdict


def analyze_failures(results: dict) -> dict:
    """카테고리별 통과율과 실패 패턴을 분석합니다."""
    category_stats = defaultdict(lambda: {"total": 0, "passed": 0, "failures": []})

    for result in results["results"]:
        case = next((c for c in eval_cases if c.case_id == result.case_id), None)
        category = case.category if case else "unknown"

        category_stats[category]["total"] += 1
        if result.passed:
            category_stats[category]["passed"] += 1
        else:
            category_stats[category]["failures"].append({
                "case_id": result.case_id,
                "input": result.input[:60],
                "expected": result.expected[:60],
                "actual": result.actual[:60],
                "score": result.score,
            })

    analysis = {}
    for cat, stats in category_stats.items():
        analysis[cat] = {
            "pass_rate": stats["passed"] / stats["total"] if stats["total"] > 0 else 0.0,
            "total": stats["total"],
            "passed": stats["passed"],
            "top_failures": stats["failures"][:3],  # 최대 3개 실패 사례
        }

    return analysis


failure_analysis = analyze_failures(report)
for category, stats in failure_analysis.items():
    print(f"\n[{category}] 통과율: {stats['pass_rate']:.1%} ({stats['passed']}/{stats['total']})")
    if stats["top_failures"]:
        print(f"  대표 실패 케이스:")
        for f in stats["top_failures"][:2]:
            print(f"  - [{f['case_id']}] 점수: {f['score']:.2f}")
```

## 운영 체크리스트

- [ ] 최소 10개, 권장 50개 이상의 평가 케이스를 보유하고 있습니다.
- [ ] 평가가 CI 파이프라인에서 자동으로 실행됩니다.
- [ ] 이전 결과 대비 회귀 감지 기준이 설정되어 있습니다.
- [ ] 카테고리별 통과율을 추적해 약점 영역을 파악합니다.
- [ ] 평가 결과가 버전과 함께 저장되어 추세를 분석할 수 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 평가 없이 프롬프트 변경 배포 | 회귀 후에야 문제 인지 | CI에서 평가를 배포 전 필수 단계로 설정 |
| 케이스 수가 너무 적음 (1-3개) | 통계적 의미 없는 결과 | 최소 10개, 각 카테고리당 3개 이상 |
| temperature=0 미설정 | 비결정적 출력으로 평가 불안정 | 평가 시 temperature=0 고정 |
| 기준선 없이 절대 점수만 봄 | 개선/악화 여부 판단 불가 | 이전 버전 대비 상대 비교 |
| 실패 케이스 분석 미실시 | 어느 영역이 약한지 파악 불가 | 카테고리별 실패율 추적 |

## 처음 질문으로 돌아가기

- **LLM 앱을 기존 소프트웨어와 같은 방식으로 테스트하기 어려운 이유는 무엇일까요?**
  LLM은 동일한 입력에도 비결정적 출력을 생성하고, 프롬프트 변경이 비선형적으로 품질에 영향을 미칩니다. 단순히 "예외 없음"이 통과 기준이 아니라 출력 품질 자체를 측정해야 하므로, 전통적인 단위 테스트만으로는 부족합니다.

- **최소 몇 개의 테스트 케이스가 있어야 의미 있는 평가가 될까요?**
  최소 10개, 실용적으로는 50개 이상을 권장합니다. 카테고리가 3개라면 각 카테고리당 최소 3-5개가 필요합니다. 통과율의 신뢰구간이 95% CI ±10% 이하가 되려면 약 100개가 필요합니다.

- **CI/CD 파이프라인에 LLM 평가를 어떻게 통합할 수 있을까요?**
  평가 스크립트가 기준선 대비 회귀를 감지하면 0이 아닌 종료 코드를 반환해 PR 병합을 차단합니다. 처음 실행이거나 성능이 향상되면 기준선을 업데이트해 다음 비교의 기준으로 사용합니다.

<!-- toc:begin -->
## 시리즈 목차

- **AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가 (현재 글)**
- [AI Evaluation 101 (2/10): 평가 데이터셋 설계하기](./02-evaluation-dataset-design.md)
- [AI Evaluation 101 (3/10): 결정적 지표](./03-deterministic-metrics.md)
- [AI Evaluation 101 (4/10): LLM-as-Judge](./04-llm-as-judge.md)
- [AI Evaluation 101 (5/10): 루브릭 기반 채점](./05-rubric-based-scoring.md)
- [AI Evaluation 101 (6/10): RAG 평가](./06-rag-evaluation.md)
- [AI Evaluation 101 (7/10): 에이전트 평가](./07-agent-evaluation.md)
- [AI Evaluation 101 (8/10): 회귀 테스트](./08-regression-testing.md)
- [AI Evaluation 101 (9/10): A/B 테스트](./09-ab-testing-llms.md)
- [AI Evaluation 101 (10/10): 프로덕션 평가](./10-production-evaluation.md)

<!-- toc:end -->

## 참고 자료

- [OpenAI — Evals Framework](https://github.com/openai/evals)
- [Anthropic — Model Evaluation](https://www.anthropic.com/research)
- [RAGAS — RAG Evaluation](https://docs.ragas.io/)
- [DeepEval — LLM Testing Framework](https://docs.confident-ai.com/)
- [book-examples — ai-evaluation-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-evaluation-101/ko)

Tags: LLMEvaluation, Testing, CI, Quality, Pipeline
