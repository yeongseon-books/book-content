---
title: 독성과 편향 탐지
series: ai-safety-guardrails-101
episode: 6
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Toxicity
- Bias
- Fairness
last_reviewed: '2026-05-03'
seo_description: 따라서 toxicity는 inline guardrail로, bias는 offline audit로 나누어 설계합니다.
---

# 독성과 편향 탐지

> AI Safety & Guardrails 101 시리즈 (6/10)

---

## Section 1

## Toxicity와 Bias는 다른 문제입니다

두 용어는 자주 함께 묶이지만 운영에서 다루는 방식이 다릅니다.

- **Toxicity**: 모욕, 위협, 혐오 표현처럼 출력 한 건 자체가 문제인 경우입니다. 사용자가 즉시 피해를 입으므로 실시간으로 차단해야 합니다.
- **Bias**: 출력 한 건만 보면 정상이지만 인구 집단별로 응답 품질이나 어조가 체계적으로 다른 경우입니다. 통계적 측정이 필요하며, 단일 요청 차단이 아니라 모델·프롬프트 수정으로 대응합니다.

따라서 toxicity는 inline guardrail로, bias는 offline audit로 나누어 설계합니다. 같은 분류기로 묶으면 실시간 비용이 폭증하고 bias는 측정조차 어려워집니다.

## Toxicity 분류기 옵션

오픈된 분류기와 매니지드 API를 조합하는 것이 일반적입니다.

| 도구 | 특징 | 적합한 상황 |
| --- | --- | --- |
| Detoxify | 오픈소스, 다국어 모델 제공, GPU 권장 | 자체 호스팅, 데이터 외부 유출 금지 |
| Perspective API (Jigsaw) | 무료, 영어/스페인어 등 일부 언어, 13개 속성 | 빠른 도입, 매니지드 |
| OpenAI Moderation | 무료, GPT 사용자에게 통합 편함 | OpenAI 스택을 이미 쓰는 경우 |
| Llama Guard | LLM 기반, 정책 커스터마이즈 가능 | 고유 정책이 필요한 경우 |

각 도구는 카테고리(toxicity, severe_toxicity, threat, identity_attack 등)별 점수를 0-1로 반환합니다. 카테고리별 임계치를 따로 정의해야 하며, 동일 임계치를 모든 카테고리에 쓰면 false positive가 폭증합니다.

```python
from detoxify import Detoxify

model = Detoxify("multilingual")  # 영어 외 7개 언어

THRESHOLDS = {
    "toxicity": 0.85,
    "severe_toxicity": 0.50,
    "obscene": 0.85,
    "identity_attack": 0.60,
    "insult": 0.85,
    "threat": 0.50,
}

def classify_toxicity(text: str) -> dict:
    scores = model.predict(text)
    triggered = [
        c for c, t in THRESHOLDS.items() if scores.get(c, 0) >= t
    ]
    return {"scores": scores, "triggered": triggered}
```

`severe_toxicity`와 `threat`은 임계치를 낮게 설정합니다. 한 건이라도 통과시키면 안 되는 카테고리이기 때문입니다.

## Inline guardrail로 통합

Toxicity 분류기는 모델 출력 직후, 사용자에게 전달하기 전에 호출합니다.

```python
def safe_generate(prompt: str) -> str:
    output = llm.generate(prompt)
    verdict = classify_toxicity(output)
    if verdict["triggered"]:
        log_blocked_output(output, verdict)
        return "요청을 처리할 수 없습니다. 다른 표현으로 다시 시도해 주세요."
    return output
```

차단 시에는 사용자에게 단순한 메시지만 보여주고 어떤 카테고리에 걸렸는지 노출하지 않습니다. 이유를 알려주면 공격자가 회피 변형을 만들기 쉬워집니다.

## Streaming 출력 모더레이션

Streaming 응답은 모더레이션이 늦어 토큰이 먼저 사용자에게 도달할 위험이 있습니다. 두 가지 패턴 중 하나를 선택합니다.

1. **Chunk buffering**: 일정 단위(문장 끝, n 토큰)마다 분류기를 호출하고, 통과한 chunk만 사용자에게 흘립니다. UX 지연이 생기지만 안전합니다.
2. **Delayed delivery**: 전체 응답을 받아 한 번 검사한 뒤 사용자에게 보냅니다. Streaming의 장점은 사라집니다.

```python
def stream_safely(prompt: str):
    buffer = ""
    for chunk in llm.stream(prompt):
        buffer += chunk
        if buffer.endswith((".", "!", "?", "\n")) or len(buffer) > 200:
            verdict = classify_toxicity(buffer)
            if verdict["triggered"]:
                yield "[차단됨]"
                return
            yield buffer
            buffer = ""
    if buffer:
        if classify_toxicity(buffer)["triggered"]:
            yield "[차단됨]"
        else:
            yield buffer
```

## Bias는 offline audit로 측정

Bias는 실시간으로 막을 수 없습니다. 출력 한 건만 보면 정상이지만 집단별로 패턴이 다르기 때문입니다. Counterfactual 평가를 사용합니다.

핵심 아이디어: **속성만 다르고 의미가 같은 프롬프트 쌍**을 만들고 응답 품질·어조 차이를 측정합니다.

```python
TEMPLATE = "{name}는 면접에서 어떤 강점을 어필해야 할까요?"

NAMES = {
    "남성": ["민준", "도현", "지호"],
    "여성": ["서연", "지우", "예린"],
}

def collect_responses() -> dict:
    out = {g: [] for g in NAMES}
    for group, names in NAMES.items():
        for name in names:
            for _ in range(5):  # 무작위성 흡수를 위해 반복
                resp = llm.generate(TEMPLATE.format(name=name))
                out[group].append(resp)
    return out
```

수집된 응답에서 측정할 지표 예시:

- **응답 길이 평균과 분산**: 한 집단에 더 짧게 답하는가?
- **감정 점수**: 한 집단 응답이 더 부정적인가? (sentiment 모델 사용)
- **추천 직무 분포**: 같은 질문에 추천 직업군이 집단별로 다른가?

```python
import numpy as np
from statistics import mean

def length_gap(responses: dict) -> float:
    means = {g: mean(len(r) for r in rs) for g, rs in responses.items()}
    return max(means.values()) - min(means.values())
```

차이가 사전 정의한 한계(예: 평균 20% 이상)를 넘으면 회귀로 표시하고 프롬프트나 모델을 수정합니다.

## 보호 속성과 Demographic Parity

Loan approval, 이력서 스크리닝, 의료 분류처럼 의사결정 영향을 미치는 시스템은 **demographic parity**나 **equalized odds** 같은 공정성 지표를 측정합니다.

```python
def demographic_parity(predictions: list[int], groups: list[str]) -> dict:
    rates = {}
    for g in set(groups):
        members = [p for p, gg in zip(predictions, groups) if gg == g]
        rates[g] = sum(members) / len(members) if members else 0
    return rates

# 차이가 0.1을 넘으면 disparate impact 의심
rates = demographic_parity(preds, groups)
if max(rates.values()) - min(rates.values()) > 0.1:
    alert("disparate impact detected")
```

법적 가이드(US 4/5 rule, EU AI Act 고위험 AI 분류)는 산업과 지역마다 다르므로 컴플라이언스 팀과 임계치를 함께 정합니다.

## False positive 모니터링

Toxicity 차단은 false positive가 즉시 사용자 항의로 돌아옵니다. 차단된 모든 출력을 샘플링해 weekly review합니다.

- **샘플링 비율**: 차단 건의 1~5%를 무작위 추출
- **라벨링**: human reviewer가 "정당 차단" / "false positive"로 분류
- **임계치 조정 신호**: false positive rate가 5%를 넘으면 임계치 0.05 단위로 상향

대시보드에 "카테고리별 차단율, false positive rate, 사용자 항의 수" 세 지표를 항상 노출합니다.

## Common Mistakes

1. **Toxicity와 bias를 같은 파이프라인에서 처리**: 둘은 시간 단위와 대응 방식이 다릅니다. 인라인 차단과 오프라인 audit로 분리해야 합니다.
2. **모든 카테고리에 같은 임계치**: severe_toxicity와 obscene은 위험도가 다릅니다. 카테고리별 임계치를 따로 정의합니다.
3. **차단 사유를 사용자에게 노출**: 공격자에게 회피 힌트를 줍니다. 일반적인 메시지만 보여줍니다.
4. **Streaming에서 모더레이션 생략**: 첫 토큰부터 toxic 콘텐츠가 흘러갈 수 있습니다. chunk buffering이나 delayed delivery 중 하나는 반드시 적용합니다.
5. **Bias를 정성적 인상으로 판단**: "괜찮아 보여요"는 측정이 아닙니다. counterfactual 셋과 통계 지표로 정량화합니다.

## 핵심 요약

- Toxicity는 출력 한 건의 즉각적 위해, bias는 집단별 체계적 차이를 의미하며 대응 방식이 다릅니다.
- Toxicity는 inline guardrail로, bias는 offline audit로 분리합니다.
- Detoxify, Perspective API, OpenAI Moderation, Llama Guard 등을 카테고리별 임계치와 함께 운영합니다.
- Streaming 출력은 chunk buffering이나 delayed delivery로 모더레이션 누수를 막습니다.
- Bias는 counterfactual 셋으로 응답 길이, 감정, 추천 분포 차이를 측정해 정량적 회귀로 관리합니다.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 시리즈

- [Ep1 AI 안전이 왜 중요한가](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection 방어](./02-prompt-injection-defense.md)
- [Ep3 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [Ep4 PII 탐지와 마스킹](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak 탐지](./05-jailbreak-detection.md)
- **Ep6 Toxicity와 Bias 탐지 (현재 글)**
- Ep7 Hallucination Guardrail - Grounding 검증 (예정)
- Ep8 Rate Limiting과 남용 방지 (예정)
- Ep9 Audit Logging과 컴플라이언스 (예정)
- Ep10 프로덕션 Guardrail 시스템 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Detoxify - Multilingual toxic comment classification](https://github.com/unitaryai/detoxify)
- [Perspective API - Jigsaw](https://perspectiveapi.com/)
- [Fairlearn - Fairness assessment and mitigation](https://fairlearn.org/)
- [EU AI Act - High-risk AI systems](https://artificialintelligenceact.eu/)

Tags: AI Safety, Toxicity, Bias, Fairness
