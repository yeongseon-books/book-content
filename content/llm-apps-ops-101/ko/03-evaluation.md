---
title: "LLM Apps Ops 101 (3/6): LLM 출력 품질 평가"
series: llm-apps-ops-101
episode: 3
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/286"
    published_at: '2026-06-06'
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-14'
seo_description: 운영 초기에 먼저 필요한 평가는 완벽한 의미 판정기가 아니라, 형식 오류와 키워드 누락 같은 명백한 실패를 빠르게 거르는 규칙층입니다.
---

# LLM Apps Ops 101 (3/6): LLM 출력 품질 평가

이 글은 LLM Apps Ops 101 시리즈의 세 번째 글입니다.

"프롬프트 압축하고 저가 모델 라우팅 붙였더니 비용 40% 줄었습니다!" 슬랙에 이 메시지가 올라왔을 때, 진짜 어려운 부분은 비용 절감 자체가 아닙니다. 어려운 부분은 2주 뒤에 옵니다. "고객이 최근 답변이 예전보다 부실하다고 합니다." 비용을 줄인 시점과 품질이 떨어진 시점을 연결할 수 있는 팀은 빠르게 롤백합니다. 연결할 수 없는 팀은 "원래 이랬나?"를 2주 더 논의합니다.

사람이 응답을 읽어야만 품질을 판단할 수 있는 구조에서는, 트래픽이 늘어나는 순간 평가가 멈춥니다. 그래서 평가의 출발점은 정교한 AI 심판이 아닙니다. 명백한 실패를 값싸게, 자주, 자동으로 걸러내는 규칙층, 이것이 출발점입니다.

![LLM 출력 품질 평가 파이프라인](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-01-big-picture.ko.png)
*규칙 기반 평가가 명백한 실패를 먼저 거르고, 의미 평가가 그 다음에 오는 구조*
> 값싼 규칙층이 먼저 있어야 비싼 평가를 정말 필요한 곳에만 쓸 수 있습니다.

## 이 글에서 다룰 문제

- 형식 통과와 품질 통과는 왜 다른 검사여야 할까요?
- 평가 결과가 "실패했다"만 알려주면 왜 운영에 쓸 수 없을까요?
- 배포 전 평가와 배포 후 평가는 무엇이 달라야 할까요?
- 평가 게이트를 배포 파이프라인에 연결하려면 무엇이 필요할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

## 왜 사람 리뷰만으로는 안 되는가

![규칙 기반 평가가 명확한 실패를 거르는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-01-why-this-layer-matters.ko.png)

*규칙 기반 평가가 명확한 실패를 거르는 흐름*

하루에 LLM 호출이 100건이면 사람이 전부 읽을 수 있습니다. 1,000건이면 샘플링을 해야 합니다. 10,000건이면 샘플링조차 운영 부담입니다. 사람이 읽지 않는 9,000건 안에 형식이 깨진 응답, 핵심 정보가 빠진 응답, 허용 길이를 벗어난 응답이 섞여 있어도 아무도 모릅니다.

자동 평가가 필요한 이유는 "사람보다 잘 판단해서"가 아닙니다. "사람이 보지 못하는 9,000건에서 명백한 실패를 즉시 잡아내서"입니다.

| 평가 방식 | 커버리지 | 비용 | 잡아내는 실패 |
|---|---|---|---|
| 사람 샘플 리뷰 | 1-5% | 높음 | 의미 품질, 톤, 정확성 |
| 규칙 기반 자동 | 100% | 거의 0 | 형식 오류, 길이 이탈, 키워드 누락 |
| LLM-as-judge | 5-20% | 중간 | 사실성, 유용성, 근거 품질 |

규칙층이 100% 커버리지로 명백한 실패를 먼저 치우면, 비싼 사람 리뷰와 LLM judge는 정말 애매한 경계 케이스에 집중할 수 있습니다. 반대로 규칙층 없이 사람 리뷰만 하면, 리뷰어의 시간 절반이 "JSON이 깨졌네"처럼 기계적으로 잡을 수 있는 문제에 낭비됩니다.

## 최소 실행 예제 — 실패 이유를 설명하는 평가

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
    failure_reasons: list[str]
    answer_length: int
    quality_score: float  # 0.0 ~ 1.0, 운영 대시보드용 연속 지표

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

def evaluate(
    text: str,
    expected_keywords: list[str],
    min_len: int = 60,
    max_len: int = 280,
) -> EvalResult:
    """형식 → 길이 → 키워드 순서로 검사합니다. 이유를 반드시 남깁니다."""
    reasons: list[str] = []

    # Layer 1: 형식 검사
    try:
        payload = json.loads(text)
        answer = payload["answer"]
        keywords = payload["keywords"]
        format_ok = isinstance(answer, str) and isinstance(keywords, list)
        if not format_ok:
            reasons.append("type_mismatch: answer must be str, keywords must be list")
    except json.JSONDecodeError:
        reasons.append("json_parse_failed")
        return EvalResult(False, False, False, False, reasons, 0, 0.0)
    except KeyError as e:
        reasons.append(f"missing_key: {e}")
        return EvalResult(False, False, False, False, reasons, 0, 0.0)

    # Layer 2: 길이 검사
    length_ok = min_len <= len(answer) <= max_len
    if not length_ok:
        reasons.append(
            f"length_out_of_range: {len(answer)} chars (expected {min_len}-{max_len})"
        )

    # Layer 3: 키워드 검사
    normalized = answer.lower() + " " + " ".join(str(k).lower() for k in keywords)
    missing = [kw for kw in expected_keywords if kw.lower() not in normalized]
    keywords_ok = not missing
    if missing:
        reasons.append(f"missing_keywords: {missing}")

    # 품질 점수 계산 (통과한 레이어 비율 기반)
    checks_passed = sum([format_ok, length_ok, keywords_ok])
    quality_score = round(checks_passed / 3, 2)

    return EvalResult(
        passed=format_ok and length_ok and keywords_ok,
        length_ok=length_ok,
        keywords_ok=keywords_ok,
        format_ok=format_ok,
        failure_reasons=reasons,
        answer_length=len(answer),
        quality_score=quality_score,
    )

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    raw = ask_for_json(client, "Python's GIL")
    result = evaluate(raw, ["CPython", "thread", "lock"])
    print(
        json.dumps(
            {"raw": json.loads(raw), "evaluation": asdict(result)},
            indent=2,
            ensure_ascii=False,
        )
    )

if __name__ == "__main__":
    main()
```

이 코드에서 라이브러리 사용법은 중요하지 않습니다. 중요한 것은 설계 결정 세 가지입니다.

![형식·길이·키워드 검사가 분리된 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-02-what-to-notice-in-this-code.ko.png)

*형식·길이·키워드 검사가 분리된 구조*

**첫째, 검사를 Layer 1/2/3으로 분리합니다.** 형식이 깨지면 길이를 볼 필요가 없고, 길이가 벗어나도 키워드를 볼 수는 있습니다. 이렇게 나누면 실패 시 "그냥 품질이 낮다"가 아니라 "형식이 깨졌는지, 길이가 벗어났는지, 키워드가 빠졌는지"를 즉시 분류할 수 있습니다.

**둘째, `failure_reasons`가 행동 가능한 정보를 남깁니다.** `passed: false`만으로는 운영에 쓸 수 없습니다. `missing_keywords: ["lock"]`이면 프롬프트에 해당 용어를 강조하는 지시를 추가하면 됩니다. `length_out_of_range: 312`이면 max_tokens를 조정하거나 프롬프트에 길이 제약을 명시하면 됩니다.

**셋째, `quality_score`를 연속 지표로 남깁니다.** pass/fail 이진값 외에 0.0~1.0 사이의 점수를 남기면, 대시보드에서 "이번 주 평균 품질 점수가 0.87에서 0.72로 떨어졌다"처럼 추세를 볼 수 있습니다.

## JSON Schema로 형식 계약을 명확하게

규칙 기반 검사의 다음 단계는 스키마 검증입니다. 키 존재 여부만 보는 것은 "answer가 있나?"까지만 확인합니다. 스키마는 "answer가 문자열이고 60자 이상 280자 이하인가?", "keywords가 최소 1개 이상인 문자열 배열인가?"까지 한 번에 검사합니다.

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
            "maxItems": 10,
        },
    },
    "required": ["answer", "keywords"],
    "additionalProperties": False,  # 예상치 못한 필드 차단
}

def validate_schema(payload: dict) -> tuple[bool, list[str]]:
    """JSON 스키마로 형식 계약을 검증합니다.
    additionalProperties: false가 없으면 모델이 임의 필드를 추가해도 통과합니다."""
    errors: list[str] = []
    try:
        validate(instance=payload, schema=ANSWER_SCHEMA)
    except ValidationError as exc:
        errors.append(f"schema_violation: {exc.json_path} — {exc.message}")
    return (not errors), errors
```

실무에서 자주 보는 실수는 `additionalProperties: false`를 빠뜨리는 것입니다. 이걸 안 넣으면 모델이 `confidence`, `source`, `reasoning` 같은 필드를 임의로 추가해도 스키마가 통과합니다. 다운스트림 파이프라인이 예상하지 못한 필드 때문에 깨지는 건 배포 한참 뒤에야 발견됩니다.

## 배치 평가로 변경 전후를 비교하기

한 건씩 평가하는 것은 실시간 가드레일입니다. 배치 평가는 다른 역할입니다. 프롬프트 버전 A와 B를 같은 입력 세트에 돌려서, 합격률과 실패 유형이 어떻게 달라졌는지 비교하는 것입니다.

```python
TEST_CASES = [
    {"topic": "Python's GIL", "expected_keywords": ["CPython", "thread", "lock"]},
    {"topic": "asyncio.gather", "expected_keywords": ["coroutine", "concurrent", "await"]},
    {"topic": "HTTP/2 multiplexing", "expected_keywords": ["stream", "frame", "connection"]},
    {"topic": "Python dataclasses", "expected_keywords": ["decorator", "field", "type"]},
    {"topic": "Redis pub/sub", "expected_keywords": ["channel", "subscribe", "message"]},
]

def run_batch(client: Groq, prompt_version: str = "v1.0") -> dict:
    """테스트 케이스 전체를 돌려 pass_rate와 실패 분포를 반환합니다."""
    results = []
    for case in TEST_CASES:
        raw = ask_for_json(client, case["topic"])
        result = evaluate(raw, case["expected_keywords"])
        results.append({
            "topic": case["topic"],
            "prompt_version": prompt_version,
            "passed": result.passed,
            "quality_score": result.quality_score,
            "failure_reasons": result.failure_reasons,
            "answer_length": result.answer_length,
        })

    passed_count = sum(1 for r in results if r["passed"])
    avg_quality = sum(r["quality_score"] for r in results) / len(results)

    # 실패 유형 분포
    reason_counts: dict[str, int] = {}
    for r in results:
        for reason in r["failure_reasons"]:
            category = reason.split(":")[0]
            reason_counts[category] = reason_counts.get(category, 0) + 1

    return {
        "prompt_version": prompt_version,
        "total": len(results),
        "passed": passed_count,
        "pass_rate": round(passed_count / len(results) * 100, 1),
        "avg_quality_score": round(avg_quality, 3),
        "failure_distribution": reason_counts,
        "failures": [r for r in results if not r["passed"]],
    }
```

배치 평가의 핵심 규칙 하나: 테스트 케이스를 코드 저장소에 버전 관리합니다. 프롬프트 v12에서 통과하던 케이스가 v13에서 실패하면, git diff로 프롬프트 변경과 실패 변경을 같은 커밋 히스토리에서 추적할 수 있습니다.

## 평가 결과를 배포 게이트로 쓰기

![규칙층 위에 judge 모델이 올라가는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-03-where-engineers-get-confused.ko.png)

*평가 레이어가 배포 결정에 영향을 미치는 흐름*

평가가 운영 도구가 되려면, 결과가 배포 결정에 실제로 영향을 미쳐야 합니다. "평가 돌렸는데 실패가 많네요, 그래도 배포할게요"가 반복되면 평가 시스템은 무시되기 시작합니다.

```python
def evaluate_batch_for_gate(
    results: list[dict],
    pass_rate_threshold: float = 0.90,
    quality_score_threshold: float = 0.80,
    previous_pass_rate: float | None = None,
) -> dict:
    """배포 게이트 판정. 하나라도 임계치를 넘으면 차단합니다."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    pass_rate = passed / total if total > 0 else 0.0
    avg_quality = sum(r.get("quality_score", 0.0) for r in results) / total if total > 0 else 0.0

    # 실패 유형 분포
    reason_counts: dict[str, int] = {}
    for r in results:
        for reason in r.get("failure_reasons", []):
            category = reason.split(":")[0]
            reason_counts[category] = reason_counts.get(category, 0) + 1

    gate_checks = {
        "pass_rate_ok": pass_rate >= pass_rate_threshold,
        "quality_score_ok": avg_quality >= quality_score_threshold,
    }

    # 이전 버전과 비교 (regression check)
    regression_detected = False
    if previous_pass_rate is not None:
        regression_detected = pass_rate < previous_pass_rate - 0.03  # 3%p 이상 하락
        gate_checks["no_regression"] = not regression_detected

    gate_passed = all(gate_checks.values())
    return {
        "gate_passed": gate_passed,
        "pass_rate": round(pass_rate * 100, 1),
        "avg_quality_score": round(avg_quality, 3),
        "threshold": pass_rate_threshold * 100,
        "regression_detected": regression_detected,
        "failure_distribution": reason_counts,
        "gate_checks": gate_checks,
        "action": "deploy" if gate_passed else "block",
        "recommended_fix": _get_recommended_fix(reason_counts) if not gate_passed else None,
    }

def _get_recommended_fix(reason_counts: dict[str, int]) -> str:
    """실패 분포에서 가장 빈번한 원인에 대한 수정 방향을 제안합니다."""
    if not reason_counts:
        return "실패 원인을 특정할 수 없습니다"
    top_reason = max(reason_counts, key=lambda k: reason_counts[k])
    fixes = {
        "json_parse_failed": "response_format 파라미터 확인, 프롬프트에 JSON 형식 명시",
        "missing_key": "프롬프트에 필수 필드 명시, few-shot 예시 추가",
        "length_out_of_range": "max_tokens 조정 또는 프롬프트에 길이 제약 명시",
        "missing_keywords": "프롬프트에 핵심 용어 언급 지시 추가",
        "type_mismatch": "스키마 예시를 프롬프트에 포함",
    }
    return fixes.get(top_reason, f"{top_reason} 관련 프롬프트 수정 검토")
```

권장하는 게이트 구조:

| 단계 | 기준 | 실패 시 행동 |
|---|---|---|
| 형식 게이트 | 스키마 실패율 < 5% | 배포 차단, 프롬프트 수정 |
| 핵심 시나리오 게이트 | 필수 테스트 케이스 전체 통과 | 배포 차단, 회귀 분석 |
| 품질 게이트 | pass_rate >= 이전 버전 - 3%p | 경고, 릴리스 노트에 명시 |

여기서 중요한 점은 "평균만 보면 안 된다"는 것입니다. 전체 pass_rate가 92%여도 특정 도메인 질문에서만 40%로 떨어질 수 있습니다. 카테고리별로 분해해서 하위 10% 구간을 반드시 확인해야 합니다.

## 오프라인 평가와 온라인 평가의 차이

배포 전에 돌리는 평가(오프라인)와 배포 후 실트래픽에서 돌리는 평가(온라인)는 같은 규칙을 쓰되 운영 방식이 다릅니다.

**오프라인 평가**는 고정된 테스트셋에서 결정적(deterministic) 결과를 기대합니다. 같은 프롬프트 버전을 같은 입력에 돌리면 pass_rate가 일정해야 합니다. 이게 흔들리면 모델 API의 비결정성(temperature > 0, 서버 측 변경)을 의심해야 합니다.

**온라인 평가**는 실트래픽의 분포가 테스트셋과 다를 수 있다는 전제에서 출발합니다. 테스트셋에 없는 질문 유형이 들어올 수 있고, 입력 길이의 분포가 달라질 수 있습니다. 그래서 온라인 평가는 "합격/불합격" 판정보다 "실패율 추이 모니터링"에 초점을 맞춥니다.

```python
from collections import deque
from dataclasses import dataclass, field

@dataclass
class OnlineEvalTracker:
    """실시간 트래픽에서 품질 지표를 슬라이딩 윈도우로 추적합니다."""
    window_size: int = 1000
    _results: deque = field(default_factory=lambda: deque(maxlen=1000))

    def record(self, result: EvalResult) -> None:
        self._results.append(result)

    def current_stats(self) -> dict:
        if not self._results:
            return {"status": "no-data"}
        n = len(self._results)
        passed = sum(1 for r in self._results if r.passed)
        avg_quality = sum(r.quality_score for r in self._results) / n
        format_fails = sum(1 for r in self._results if not r.format_ok)
        return {
            "window_size": n,
            "pass_rate": round(passed / n, 4),
            "avg_quality_score": round(avg_quality, 4),
            "format_fail_rate": round(format_fails / n, 4),
            "alert": passed / n < 0.85,  # 85% 이하면 알람
        }
```

실무에서 자주 보는 실수: 오프라인 테스트셋을 한 번 만들고 6개월간 갱신하지 않는 것입니다. 그사이 사용자 질문 유형이 바뀌면, 테스트셋 pass_rate는 95%인데 실트래픽 만족도는 떨어지는 괴리가 생깁니다. 최소 월 1회, 실패한 실트래픽 샘플 10-20건을 테스트셋에 추가하는 루틴이 필요합니다.

## 가드레일 패턴 — 응답 품질을 실시간으로 제어하기

평가가 배포 게이트 역할만 하면 절반의 활용입니다. 운영 중에도 응답 품질이 기준 이하로 떨어지는 순간 자동으로 개입하는 "가드레일" 패턴이 필요합니다.

```python
from enum import Enum

class GuardrailAction(Enum):
    PASS = "pass"        # 그대로 사용자에게 전달
    RETRY = "retry"      # 프롬프트 수정 후 재시도
    FALLBACK = "fallback"  # 저품질 응답 대신 기본 답변 반환
    ESCALATE = "escalate"  # 사람 검토 큐에 추가

@dataclass
class GuardrailDecision:
    action: GuardrailAction
    reason: str
    eval_result: EvalResult
    retry_hint: str | None = None  # RETRY 시 프롬프트 수정 방향

def apply_guardrail(
    eval_result: EvalResult,
    retry_budget: int = 1,  # 남은 재시도 횟수
) -> GuardrailDecision:
    """평가 결과를 받아 다음 행동을 결정합니다."""
    if eval_result.passed:
        return GuardrailDecision(
            action=GuardrailAction.PASS,
            reason="all checks passed",
            eval_result=eval_result,
        )

    # 형식 오류 + 재시도 예산 있음 → 재시도
    if not eval_result.format_ok and retry_budget > 0:
        return GuardrailDecision(
            action=GuardrailAction.RETRY,
            reason="format check failed",
            eval_result=eval_result,
            retry_hint="Please respond in valid JSON format with 'answer' and 'keywords' keys only.",
        )

    # 길이/키워드 실패 + 재시도 예산 있음 → 재시도 with hint
    if retry_budget > 0:
        hints = []
        if not eval_result.length_ok:
            hints.append("Keep the answer between 60 and 280 characters.")
        if not eval_result.keywords_ok:
            hints.append("Make sure to include all technical keywords in the answer.")
        return GuardrailDecision(
            action=GuardrailAction.RETRY,
            reason=f"quality checks failed: {eval_result.failure_reasons}",
            eval_result=eval_result,
            retry_hint=" ".join(hints),
        )

    # 재시도 예산 소진 → 폴백
    return GuardrailDecision(
        action=GuardrailAction.FALLBACK,
        reason="retry budget exhausted",
        eval_result=eval_result,
    )
```

가드레일 패턴의 핵심은 "어떤 실패에는 자동 재시도, 어떤 실패에는 폴백"을 사전에 명시하는 것입니다. 이 결정이 코드에 없으면, 품질 실패가 발생할 때마다 담당자가 수동으로 판단해야 합니다.

## 실무에서 자주 겪는 혼동

**"정교한 LLM judge가 없으면 평가가 아니다"라는 착각.** 실제 운영에서 가장 많은 가치를 만드는 평가는 규칙층입니다. JSON이 깨졌거나, 필수 키가 빠졌거나, 답변이 10자밖에 안 되는 경우는 AI 심판을 붙일 필요가 없습니다.

**"형식이 맞으면 좋은 답변이다"라는 반대쪽 착각.** 형식 통과는 필요조건이지 충분조건이 아닙니다. JSON이 완벽하고 길이도 적절한데, 내용이 완전히 틀린 응답은 규칙층을 통과합니다. 규칙층 위에 의미 평가 레이어(LLM-as-judge, 사람 리뷰)가 필요합니다.

**길이 기준을 절대값으로 고정하는 실수.** "모든 답변은 100-300자"라고 고정하면, 코드 생성 응답이나 목록 응답이 불필요하게 잘립니다. 엔드포인트별로, 또는 질문 유형별로 기준을 다르게 설정해야 합니다.

**테스트 케이스의 expected_keywords를 너무 빡빡하게 잡는 실수.** "반드시 CPython이라는 단어가 들어가야 한다"고 정하면, 모델이 "C로 작성된 Python 구현체"라고 우회 표현할 때 불합격 처리됩니다. 핵심 개념의 동의어까지 고려한 키워드 세트를 만들거나, 키워드 검사 대신 의미 유사도 검사로 올려야 할 수 있습니다.

## 운영 체크리스트

- [ ] 형식 검사(JSON 파싱, 필수 키, 타입)를 별도 레이어로 분리한다
- [ ] 실패 시 `failure_reasons`에 수정 가능한 정보를 남긴다
- [ ] `quality_score`를 0.0~1.0 연속값으로 대시보드에 추적한다
- [ ] 엔드포인트별 길이 기준을 매개변수로 관리한다
- [ ] 배치 테스트 케이스를 코드 저장소에 버전 관리한다
- [ ] 평가 결과가 배포를 실제로 차단하는 게이트를 연결한다
- [ ] 이전 버전 대비 pass_rate 회귀를 자동 탐지한다
- [ ] 월 1회 실트래픽 실패 샘플을 테스트셋에 추가한다
- [ ] 가드레일 패턴으로 품질 실패 시 자동 재시도 또는 폴백을 구성한다

## 정리

평가가 운영 도구로 동작하는 순간은, 사람이 보기 전에 명백한 실패를 자동으로 걸러내기 시작할 때입니다. 형식 → 길이 → 키워드 순서의 규칙층이 100% 트래픽을 먼저 걸러내면, 비싼 LLM judge나 사람 리뷰는 정말 판단이 필요한 경계 케이스에만 집중할 수 있습니다.

다음 글에서는 이 평가 레이어를 통과한 응답이라도, 입력에 위험한 지시가 들어오거나 출력에 민감 정보가 새어 나갈 수 있는 보안 레이어를 다루겠습니다.

## 처음 질문으로 돌아가기

- **형식 통과와 품질 통과는 왜 다른 검사여야 할까요?**
  - 형식 통과는 "JSON이 파싱되고 필수 키가 있는가"이고, 품질 통과는 "내용이 기대 수준을 충족하는가"입니다. 형식은 완전히 자동화 가능하고 비용이 0에 가깝습니다. 품질은 도메인 지식이 필요하고 비용이 높습니다. 두 가지를 분리해야 자원을 효율적으로 배분할 수 있습니다.

- **평가 결과가 "실패했다"만 알려주면 왜 운영에 쓸 수 없을까요?**
  - "실패했다"는 "어디를 고쳐야 하는가"를 알려주지 않습니다. `failure_reasons`에 `missing_keywords: ["lock"]`이 있으면 프롬프트 수정 방향이 즉시 나옵니다. 이유 없는 실패 판정은 재발을 막지 못합니다.

- **배포 전 평가와 배포 후 평가는 무엇이 달라야 할까요?**
  - 배포 전 평가는 고정 테스트셋에서 "이 프롬프트 버전이 기준을 통과하는가"를 결정적으로 판단합니다. 배포 후 평가는 실트래픽에서 "현재 실패율이 기준선을 벗어나고 있는가"를 지속적으로 모니터링합니다. 같은 규칙층이지만 사용 목적과 집계 방식이 다릅니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- [LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화](./02-cost-tracking.md)
- **LLM Apps Ops 101 (3/6): LLM 출력 품질 평가 (현재 글)**
- [LLM Apps Ops 101 (4/6): LLM 앱 보안](./04-security.md)
- [LLM Apps Ops 101 (5/6): LLM 앱 배포 전략](./05-deployment.md)
- [LLM Apps Ops 101 (6/6): LLM 앱 운영 완성](./06-ops-complete.md)

<!-- toc:end -->

---

## 참고 자료

- [LLM Apps Ops 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/llm-apps-ops-101/ko)

### 공식 문서

- [OpenAI Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs)
- [JSON Schema](https://json-schema.org/)

### 검증에 도움 되는 자료

- [G-Eval paper](https://arxiv.org/abs/2303.16634)
- [Promptfoo docs](https://www.promptfoo.dev/docs/)

Tags: LLMOps, Observability, Python, LLM
