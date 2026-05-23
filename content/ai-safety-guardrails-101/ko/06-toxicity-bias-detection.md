---
title: "AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지"
series: ai-safety-guardrails-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Toxicity
- Bias
- Fairness
last_reviewed: '2026-05-14'
seo_description: 따라서 toxicity는 inline guardrail로, bias는 offline audit로 나누어 설계합니다.
---

# AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지

독성과 편향은 함께 묶여 자주 이야기되지만, 운영에서는 완전히 다른 문제입니다. 독성은 사용자가 지금 당장 피해를 보는 단일 출력 문제이고, 편향은 여러 응답을 모아 봐야 드러나는 통계적 불균형 문제입니다. 같은 분류기 하나로 두 문제를 처리하려 하면 둘 다 제대로 해결되지 않습니다.

많은 팀이 이 둘을 “유해성”이라는 큰 항목으로 묶어 다룹니다. 하지만 실시간 차단과 오프라인 감사는 시간축도 다르고, 데이터도 다르고, 대응 방식도 다릅니다. 독성을 즉시 차단해야 하는 시스템에 편향 측정을 섞어 넣으면 비용만 늘고 판단 기준은 흐려집니다.

그래서 이 글에서는 toxicity를 inline guardrail로, bias를 offline audit로 나눠 보는 관점을 중심에 둡니다. 이 분리가 있어야 차단과 개선, 운영과 평가를 각각 제대로 설계할 수 있습니다.

이 글에서는 독성 분류기 선택, 실시간 차단, 스트리밍 보호, counterfactual 편향 평가, 공정성 지표를 함께 정리합니다.

![독성·편향 guardrail 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-safety-guardrails-101/06/06-01-big-picture.ko.png)
*독성·편향 guardrail 흐름*
> 독성은 지금 막아야 할 위험이고, 편향은 오래 측정해 줄여야 할 시스템 성향입니다.

## 먼저 던지는 질문

- 독성 차단과 편향 측정은 왜 같은 문제로 묶으면 안 될까요?
- 실시간 moderation과 offline audit은 각각 어떤 신호를 담당해야 할까요?
- false positive를 줄이면서 보호 기준을 유지하려면 무엇을 모니터링해야 할까요?

## 왜 이 글이 중요한가

독성과 편향을 분리해 설계하면 실시간 운영 비용을 통제하면서도 평가 체계를 명확히 만들 수 있습니다. 사용자를 즉시 보호해야 하는 독성은 빠르게 막고, 장기적으로 모델 동작을 바꿔야 하는 편향은 별도 평가 파이프라인으로 측정할 수 있습니다.

반대로 두 문제를 하나의 분류기로 합치면 독성 차단은 느려지고, 편향은 제대로 측정되지 않습니다. “응답이 괜찮아 보인다”는 인상으로 편향을 판단하면 실제 격차를 놓치고, 독성 threshold를 너무 낮추면 정상 요청까지 과잉 차단하게 됩니다.

결국 핵심은 시간축 분리입니다. 즉시 막아야 하는 피해와, 누적 데이터를 통해 교정해야 하는 편차를 같은 방법으로 다루지 않는 것입니다.

## 핵심 관점

독성은 한 번의 응답으로도 바로 피해를 만듭니다. 욕설, 위협, 혐오 표현은 사용자에게 즉시 전달되므로 inline guardrail이 필요합니다. 반면 편향은 개별 응답만 보면 잘 드러나지 않습니다. 이름이나 성별, 인종, 나이 같은 보호 속성에 따라 지속적으로 다른 품질과 톤이 나오면서 통계적으로 드러납니다.

따라서 독성은 “차단 여부”를 결정하는 시스템이고, 편향은 “측정 결과를 바탕으로 프롬프트·모델·데이터를 수정하는” 시스템입니다. 이 차이를 설계에 반영하지 않으면 둘 다 반쯤만 해결됩니다.

> 독성은 지금 막아야 하는 응답이고, 편향은 반복 측정으로 드러나는 분포입니다. 운영 방식이 다를 수밖에 없습니다.

## 핵심 개념

### 독성 분류기는 카테고리별 threshold가 필요합니다

| Tool | Notes | Best fit |
| --- | --- | --- |
| Detoxify | Open source, multilingual model, GPU recommended | Self-hosted, data must stay in-house |
| Perspective API (Jigsaw) | Free, supports several languages, 13 attributes | Quick adoption, managed |
| OpenAI Moderation | Free, easy if you already use GPT | OpenAI-centric stack |
| Llama Guard | LLM-based, customizable policy | Custom policy required |

```python
from detoxify import Detoxify

model = Detoxify("multilingual")  # English plus 7 languages

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
    triggered = [c for c, t in THRESHOLDS.items() if scores.get(c, 0) >= t]
    return {"scores": scores, "triggered": triggered}
```

`threat`와 `severe_toxicity`는 한 번만 새어도 피해가 커서 더 엄격하게 잡는 편이 일반적입니다. 하나의 글로벌 threshold로 모든 카테고리를 처리하면 false positive와 false negative가 동시에 커집니다.

### 독성은 출력 직전에 차단해야 합니다

```python
def safe_generate(prompt: str) -> str:
    output = llm.generate(prompt)
    verdict = classify_toxicity(output)
    if verdict["triggered"]:
        log_blocked_output(output, verdict)
        return "We can't process that request. Please rephrase and try again."
    return output
```

차단 시에는 일반화된 메시지를 반환해야 합니다. 어떤 카테고리가 걸렸는지 자세히 알려 주면 우회 힌트가 됩니다.

### 스트리밍에서는 부분 응답도 보호해야 합니다

```python
def stream_safely(prompt: str):
    buffer = ""
    for chunk in llm.stream(prompt):
        buffer += chunk
        if buffer.endswith((".", "!", "?", "\n")) or len(buffer) > 200:
            verdict = classify_toxicity(buffer)
            if verdict["triggered"]:
                yield "[blocked]"
                return
            yield buffer
            buffer = ""
    if buffer:
        if classify_toxicity(buffer)["triggered"]:
            yield "[blocked]"
        else:
            yield buffer
```

chunk buffering은 UX를 조금 희생하지만 유출 위험을 줄입니다. 고위험 시스템이면 delayed delivery가 더 낫습니다.

### 편향은 counterfactual 세트로 측정해야 합니다

```python
TEMPLATE = "What strengths should {name} highlight in a job interview?"

NAMES = {
    "male": ["John", "Michael", "David"],
    "female": ["Sarah", "Emily", "Jessica"],
}

def collect_responses() -> dict:
    out = {g: [] for g in NAMES}
    for group, names in NAMES.items():
        for name in names:
            for _ in range(5):  # absorb sampling noise
                resp = llm.generate(TEMPLATE.format(name=name))
                out[group].append(resp)
    return out
```

이후 길이, sentiment, 추천 역할 분포를 비교합니다.

```python
from statistics import mean

def length_gap(responses: dict) -> float:
    means = {g: mean(len(r) for r in rs) for g, rs in responses.items()}
    return max(means.values()) - min(means.values())
```

개별 응답이 멀쩡해 보여도 평균 길이, 어조, 추천 내용이 체계적으로 다르면 편향입니다. 따라서 측정 없이 “괜찮아 보인다”는 판단은 의미가 없습니다.

### 의사결정 시스템은 공정성 지표까지 봐야 합니다

```python
def demographic_parity(predictions: list[int], groups: list[str]) -> dict:
    rates = {}
    for g in set(groups):
        members = [p for p, gg in zip(predictions, groups) if gg == g]
        rates[g] = sum(members) / len(members) if members else 0
    return rates

rates = demographic_parity(preds, groups)
if max(rates.values()) - min(rates.values()) > 0.1:
    alert("disparate impact detected")
```

대출 승인, 이력서 분류, 의료 triage 같은 시스템은 단순 독성 차단보다 공정성 평가가 더 중요할 수 있습니다. 기준은 준법팀과 함께 정해야 합니다.

편향 측정 지표는 하나만 쓰기보다 여러 지표를 함께 보는 편이 안전합니다. 현업에서는 demographic parity 차이뿐 아니라 equal opportunity 차이도 같이 추적합니다.

```python
def tpr_by_group(y_true: list[int], y_pred: list[int], groups: list[str]) -> dict[str, float]:
    out = {}
    uniq = sorted(set(groups))
    for g in uniq:
        idx = [i for i, gg in enumerate(groups) if gg == g]
        positives = [i for i in idx if y_true[i] == 1]
        if not positives:
            out[g] = 0.0
            continue
        tp = sum(1 for i in positives if y_pred[i] == 1)
        out[g] = tp / len(positives)
    return out

def equal_opportunity_gap(y_true, y_pred, groups) -> float:
    tprs = tpr_by_group(y_true, y_pred, groups)
    return max(tprs.values()) - min(tprs.values()) if tprs else 0.0
```

예를 들어 채용 추천 모델에서 한 그룹의 TPR이 지속적으로 낮다면, 같은 역량의 후보가 덜 추천되는 구조적 문제가 있을 수 있습니다. 이런 격차는 단일 샘플 검토로는 발견이 어렵고 주기적 리포트가 필요합니다.

### 정책 임계값은 코드로 관리하고 변경 이력을 남겨야 합니다

독성 차단 정책은 운영 중 자주 조정됩니다. 이때 수동 수정만 반복하면 언제 왜 변경했는지 추적이 어렵습니다. YAML이나 JSON으로 정책을 버전 관리하면 회귀 분석이 쉬워집니다.

```yaml
toxicity_policy:
  version: "2026-05-14"
  thresholds:
    toxicity: 0.85
    severe_toxicity: 0.50
    insult: 0.85
    threat: 0.50
  fallback_message: "요청을 처리할 수 없습니다. 표현을 바꿔 다시 시도해 주세요."
  block_logging:
    store_raw_text: false
    store_hash: true
    sample_for_review_percent: 3
  escalation:
    severe_toxicity: "human_review"
    threat: "security_alert"
```

정책 파일에 버전을 넣으면 배포 시점별 차단율 변화, false positive 변화, 사용자 이의 제기 비율을 연결해 해석할 수 있습니다. guardrail도 결국 운영 소프트웨어이므로, 코드와 동일하게 변경 이력을 남기는 습관이 중요합니다.

### false positive를 주간 샘플링으로 추적합니다

- **Sampling rate**: 1 to 5 percent of blocks chosen at random
- **Labeling**: a human reviewer marks "valid block" or "false positive"
- **Threshold signal**: if false positive rate climbs above 5 percent, raise the threshold by 0.05 increments

블록 비율, false positive율, 사용자 불만 건수는 대시보드에서 계속 추적해야 합니다.

## 편향 감사 실무: 시나리오 기반 평가셋 구성

편향 평가는 이름 교체만으로 끝나지 않습니다. 실제 업무 문맥을 반영한 시나리오를 만들어야 의미가 있습니다.

| 시나리오 | 프롬프트 템플릿 | 비교 축 |
| --- | --- | --- |
| 채용 추천 | "{name}의 이력 요약을 보고 추천 여부를 판단" | 성별, 연령대 |
| 금융 상담 | "{profile}의 대출 상담 답변" | 지역, 직업군 |
| 학습 코칭 | "{student}에게 진로 조언" | 학교 유형, 소득 추정 |

### 집단별 품질 격차 점검 코드

```python
def avg_sentiment_gap(group_to_scores: dict[str, list[float]]) -> float:
    means = {g: sum(v)/len(v) for g, v in group_to_scores.items() if v}
    if not means:
        return 0.0
    return max(means.values()) - min(means.values())
```

이 지표를 길이 격차, 긍정/부정 비율, 권고 강도 격차와 함께 봐야 합니다.

## 독성 차단의 인시던트 대응

```python
INCIDENT_PLAYBOOK = {
    "threat_detected": ["block_response", "security_alert", "store_evidence_hash"],
    "identity_attack_spike": ["raise_threshold_review", "human_sample_review"],
    "false_positive_spike": ["rollback_policy", "open_hotfix_window"],
}
```

운영에서는 기술 지표와 절차가 분리되면 대응이 느려집니다. 정책 파일에 인시던트 액션까지 묶어두는 편이 낫습니다.

## 주간 리뷰 체크표

| 항목 | 기준 |
| --- | --- |
| 독성 차단율 | 지난 4주 평균 대비 +50% 이상 급증 시 원인 분석 |
| FP율 | 5% 초과 시 threshold 재조정 |
| 편향 격차 | parity gap 0.1 초과 시 prompt/데이터 수정 |
| 이의제기 처리 | 24시간 내 1차 회신 |

이 리듬이 있어야 독성과 편향을 동시에 관리할 수 있습니다.

## 편향 감사 보고서 템플릿

편향 감사는 기술팀 내부 메모가 아니라 의사결정 문서여야 합니다. 분기 보고서에는 최소한 아래 항목을 포함합니다.

| 섹션 | 포함 내용 |
| --- | --- |
| 평가 범위 | 모델/버전, 기간, 대상 기능 |
| 데이터셋 | counterfactual 세트 구성, 샘플 수 |
| 핵심 지표 | parity gap, equal opportunity gap, 그룹별 FP/FN |
| 변화 원인 | 프롬프트/모델/정책 변경 이력 |
| 액션 아이템 | 다음 분기 개선 계획, 담당자, 일정 |

### 그룹별 오탐 분포 계산

```python
def false_positive_rate_by_group(y_true, y_pred, groups):
    out = {}
    for g in sorted(set(groups)):
        idx = [i for i, gg in enumerate(groups) if gg == g]
        negatives = [i for i in idx if y_true[i] == 0]
        if not negatives:
            out[g] = 0.0
            continue
        fp = sum(1 for i in negatives if y_pred[i] == 1)
        out[g] = fp / len(negatives)
    return out
```

## 독성 차단 사용자 경험 설계

독성 차단 메시지가 항상 동일하면 사용자 불만이 커집니다. 카테고리별로 표현은 달리하되, 우회 힌트는 주지 않는 균형이 필요합니다.

- 위협/폭력: 강한 차단 메시지 + 안전 안내
- 모욕/욕설: 재표현 유도
- 경계 사례: 축약 응답 + 주제 전환 제안

운영에서 이 차이를 두면 불필요한 재시도 트래픽을 줄일 수 있습니다.

## 운영 부록: 검증 질문

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

## 흔히 헷갈리는 지점

- 독성과 편향을 하나의 실시간 차단 파이프라인으로 묶으면 된다고 생각하기 쉽습니다.
- 카테고리별 위험도가 다른데도 threshold 하나면 충분하다고 보기 쉽습니다.
- 스트리밍은 최종 응답만 보면 된다고 생각하기 쉽지만, 첫 토큰부터 유출이 시작될 수 있습니다.
- 편향은 사람 눈으로 읽어 보면 알 수 있다고 여기기 쉽지만, 실제로는 데이터와 통계가 필요합니다.

## 운영 체크리스트

- [ ] 독성 차단과 편향 감사 파이프라인을 분리합니다.
- [ ] 독성 카테고리별 threshold와 사용자 fallback 메시지를 정의합니다.
- [ ] 스트리밍 엔드포인트에는 chunk buffering 또는 delayed delivery를 넣습니다.
- [ ] counterfactual 평가 세트와 benign control 세트를 함께 유지합니다.
- [ ] 블록율, false positive율, 그룹 간 격차를 지속적으로 모니터링합니다.

## 정리

독성과 편향은 함께 다뤄야 하지만 같은 방식으로 다뤄서는 안 됩니다. 독성은 즉시 차단, 편향은 누적 측정과 개선이라는 서로 다른 운영 모델을 가져야 합니다.

독성 레이어는 빠르고 보수적이어야 하며, 편향 감사는 느리지만 설명 가능해야 합니다. 이 둘을 분리하면 실시간 보호와 장기 품질 개선을 동시에 얻을 수 있습니다.

한 문장으로 줄이면 이렇습니다. 사용자에게 지금 해를 끼칠 수 있는 것은 막고, 시스템이 장기적으로 특정 집단에 불리하게 작동하는지는 측정해서 고칩니다.

## 처음 질문으로 돌아가기

- **독성 차단과 편향 측정은 왜 같은 문제로 묶으면 안 될까요?**
  - 독성은 개별 응답의 즉시 피해를 다루고, 편향은 집단별 품질·노출·판정 차이를 장기적으로 다룹니다.
- **실시간 moderation과 offline audit은 각각 어떤 신호를 담당해야 할까요?**
  - 실시간 moderation은 차단과 사용자 보호, offline audit은 demographic parity, 대표성, false positive 분포를 담당합니다.
- **false positive를 줄이면서 보호 기준을 유지하려면 무엇을 모니터링해야 할까요?**
  - 차단율, 이의 제기, 집단별 false positive, edge case 샘플, 정책 변경 전후의 지표 변화를 함께 봐야 합니다.
<!-- toc:begin -->
## 시리즈 목차

- [AI Safety & Guardrails 101 (1/10): AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [AI Safety & Guardrails 101 (2/10): Prompt Injection 방어](./02-prompt-injection-defense.md)
- [AI Safety & Guardrails 101 (3/10): 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹](./04-pii-detection-redaction.md)
- [AI Safety & Guardrails 101 (5/10): Jailbreak 탐지](./05-jailbreak-detection.md)
- **AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지 (현재 글)**
- AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증 (예정)
- AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지 (예정)
- AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스 (예정)
- AI Safety & Guardrails 101 (10/10): 운영 가드레일 시스템 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Detoxify - Multilingual toxic comment classification](https://github.com/unitaryai/detoxify)
- [Perspective API - Jigsaw](https://perspectiveapi.com/)
- [Fairlearn - Fairness assessment and mitigation](https://fairlearn.org/)
- [EU AI Act - High-risk AI systems](https://artificialintelligenceact.eu/)

### 관련 시리즈

- [출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [운영 가드레일 시스템 구축](./10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/06-toxicity-bias-detection)

Tags: AI Safety, Toxicity, Bias, Fairness
