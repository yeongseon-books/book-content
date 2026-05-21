---
title: "LLM Fine-tuning 101 (5/6): 모델 평가"
series: llm-finetuning-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- Evaluation
- Perplexity
- GoldenSet
- Metrics
- Python
last_reviewed: '2026-05-12'
seo_description: 평가는 모델 내부 신호와 사용자 품질을 나눠 볼 때 가장 잘 작동합니다.
---

# LLM Fine-tuning 101 (5/6): 모델 평가

평가는 파인튜닝 데모가 가장 쉽게 오해를 부르는 단계입니다. 이 글은 LLM Finetuning 101 시리즈의 다섯 번째 글입니다. 여기서는 모델 내부 신호와 사용자 관점 품질을 분리해서, 개선과 회귀를 반복 가능한 루프로 어떻게 측정할지 정리하겠습니다.

학습이 끝나면 생성 예시부터 보고 싶어지지만, 운영에서는 그보다 먼저 정량 신호를 봐야 합니다. 그중 가장 기본이 perplexity입니다. 다만 perplexity 하나만으로 품질을 판단하면 금방 잘못된 결론에 도달합니다. 5편의 핵심은 평가를 **자동화 가능한 파이프라인**으로 바꾸는 데 있습니다.

![LLM Fine-tuning 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-02-the-right-way-to-read-perplexity.ko.png)
*LLM Fine-tuning 101 5장 흐름 개요*

## 먼저 던지는 질문

- 파인튜닝 직후 가장 먼저 봐야 할 정량 신호인 perplexity는 어떻게 계산할까요?
- 학습 전후 perplexity 비교만으로는 왜 평가가 충분하지 않을까요?
- 작은 데모 모델에서도 왜 별도의 평가 루프를 유지해야 할까요?

## 왜 이 글이 중요한가

파인튜닝 직후 생성 샘플 몇 개만 보고 판단하면, 우연히 잘 나온 예시를 품질 개선으로 착각하기 쉽습니다. 운영에서는 먼저 정량 신호를 보고, 그다음에 정성 평가를 얹어야 합니다. perplexity는 평가 데이터에서 모델이 토큰을 얼마나 자연스럽게 예측하는지 보여 주는 가장 빠른 기준선입니다.

5편의 진짜 목적은 평가를 감이 아니라 **파이프라인**으로 만드는 것입니다. 매번 사람이 모든 출력을 읽는 방식은 확장되지 않습니다. 빠른 회귀 감지선으로 perplexity를 두고, 그 위에 골든 세트 기반 평가를 쌓아 두면 4편의 1-step 학습 검증처럼 평가도 자동화된 루프로 굴릴 수 있습니다.

## 멘탈 모델

평가는 **모델 내부 신호**와 **사용자 관점 품질**을 분리해서 볼 때 가장 잘 작동합니다.

```text
[Internal signals]              [User-facing quality]
- perplexity                    - answer match rate
- token-level accuracy          - format compliance
- gradient norm                 - human rating
        |                              |
        +--- fast regression line --+  |
                  |                    |
            run in CI            run on a separate
                                 schedule with golden set
```

내부 신호는 수 초에서 수 분 안에 빠르게 돌릴 수 있고, 사용자 관점 품질 평가는 수 분에서 수 시간까지 더 느립니다. 빠른 신호가 회귀하면 즉시 막고, 느린 신호는 주기적으로 추적하는 식이 운영에 맞습니다.

추가로 기억할 사실은 두 가지입니다.

- **perplexity = exp(mean cross-entropy loss)** 입니다. 손실이 내려가면 perplexity도 내려갑니다.
- **평가 데이터는 학습 데이터와 분리돼야 합니다.** 데모에서는 단순화를 위해 겹칠 수 있지만, 실제 프로젝트에서는 hold-out 세트가 필요합니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| Perplexity | 다음 토큰 예측에서 모델이 느끼는 평균 "낯섦"입니다. 낮을수록 좋습니다. |
| Cross-entropy loss | 예측 분포와 정답 분포의 차이입니다. perplexity의 원료가 됩니다. |
| `model.eval()` | 드롭아웃과 배치 정규화를 추론 모드로 바꿉니다. |
| `torch.no_grad()` | 그래디언트 계산을 끄고 메모리와 시간을 절약합니다. |
| Golden set | 사람이 직접 검수한 평가용 입력/출력 쌍입니다. 회귀 감지의 기준점이 됩니다. |
| Hold-out set | 학습에 쓰지 않은 데이터입니다. perplexity 측정에 사용합니다. |
| Task metric | exact match, BLEU, ROUGE 같은 도메인별 지표입니다. |

## Before vs. After

**Before**

"손실이 줄었으니 학습이 된 것 같다"는 막연한 인상만 남습니다. 며칠 뒤 같은 결과를 다시 보여 달라고 하면 재현하기 어렵습니다.

**After**

5편의 평가 루프를 도입하면 결과는 아래 한 줄로 요약됩니다.

```text
{'before_ppl': 27431.84, 'after_ppl': 26890.17, 'delta_pct': -1.97}
```

중요한 것은 절대값이 아니라, (1) 평가가 학습과 분리되어 있고, (2) 같은 데이터로 전후를 비교하며, (3) CI에서도 같은 계산이 반복된다는 점입니다.

## perplexity를 올바르게 읽는 법

perplexity는 낮을수록 좋지만, 절대값만 보고 품질을 단정하면 안 됩니다. 작은 데모 모델, 작은 데이터셋, 짧은 컨텍스트 길이에서는 값이 크게 출렁일 수 있습니다. 그래서 perplexity는 실무에서 **회귀 감지 기준선**으로 가장 유용합니다. 무엇이 나빠졌는지, 혹은 설정을 바꾼 뒤 추세가 좋아졌는지를 빠르게 보는 데 강합니다.

![perplexity를 올바르게 읽는 법](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-01-the-right-way-to-read-perplexity.ko.png)

*perplexity를 올바르게 읽는 법*

## 단계별 설명

### 1단계 — 평가 함수를 작성합니다

```python
import math
import torch

def perplexity(model, dataset) -> float:
    losses = []
    model.eval()
    for row in dataset:
        batch = {key: torch.tensor([value]) for key, value in row.items()}
        with torch.no_grad():
            loss = model(**batch).loss
        losses.append(loss.item())
    return math.exp(sum(losses) / len(losses))
```

### 2단계 — 학습 전후를 측정합니다

```python
before = perplexity(peft_model, eval_dataset)
trainer.train()
after = perplexity(peft_model, eval_dataset)

delta = (after - before) / before * 100
print({"before_ppl": before, "after_ppl": after, "delta_pct": delta})
```

### 3단계 — 골든 세트를 정의합니다

```python
golden = [
    {"prompt": "Q: How to sort a Python list?", "expected_contains": "sorted"},
    {"prompt": "Q: What is HTTP 404?", "expected_contains": "not found"},
]
```

각 항목은 프롬프트와 기대 키워드의 쌍입니다. 작은 모델에서는 exact match보다 특정 핵심 단어가 포함되는지 보는 편이 더 현실적입니다.

### 4단계 — 골든 세트를 채점합니다

```python
def score_golden(model, tokenizer, golden) -> float:
    hits = 0
    for item in golden:
        ids = tokenizer(item["prompt"], return_tensors="pt").input_ids
        out = model.generate(ids, max_new_tokens=32)
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        if item["expected_contains"] in text:
            hits += 1
    return hits / len(golden)
```

### 5단계 — 두 신호를 함께 출력합니다

```python
print({
    "ppl_after": after,
    "golden_score": score_golden(peft_model, tokenizer, golden),
})
```

이 두 줄이 한 화면에 함께 나오면, 빠른 정량 기준선과 사용자 관점 품질 신호를 동시에 볼 수 있게 됩니다.

## 이 코드에서 봐야 할 것

![평균 손실에서 perplexity로 가는 계산 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-03-what-to-notice-in-this-code.ko.png)

*평균 손실에서 perplexity로 가는 계산 흐름*

- 평가 함수는 학습 루프와 분리되어 있어야 합니다. 그렇지 않으면 손실을 읽는 동안 파라미터를 바꾸는 실수를 저지를 수 있습니다.
- `torch.no_grad()`와 `model.eval()`은 메모리 사용과 드롭아웃 동작을 안정화하는 가장 기본적인 보호장치입니다.
- 이 예제는 추세 확인용입니다. 실제 프로젝트에서는 hold-out 세트, 태스크 지표, 사람 검토가 함께 필요합니다.
- 골든 세트 채점은 사람이 모든 출력을 읽지 않아도 회귀를 잡을 수 있게 해 주는 가장 가벼운 자동화입니다.

## 자주 하는 실수

![과적합 신호와 비교 기준 판단 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-04-where-engineers-get-confused.ko.png)

*과적합 신호와 비교 기준 판단 흐름*

- **perplexity만 보고 배포를 결정하는 실수**: 형식 준수, 사실성, 안전성은 별도 평가가 필요합니다. perplexity는 한 축일 뿐입니다.
- **학습 데이터와 평가 데이터를 같게 쓰는 실수**: 숫자가 지나치게 낙관적으로 보입니다. 데모에서는 단순화를 위해 같게 쓸 수 있어도, 실제로는 반드시 분리해야 합니다.
- **골든 세트를 한 번 만들고 끝내는 실수**: 모델이 바뀌면 평가 항목도 함께 자라야 합니다. 매주 5~10개씩 추가하는 루틴이 유용합니다.
- **`model.eval()`을 빼먹는 실수**: 드롭아웃이 살아 있어 같은 입력에도 다른 출력이 나옵니다. 재현성이 무너집니다.
- **마지막 체크포인트만 평가하는 실수**: 언제부터 나빠졌는지 알 수 없습니다. `eval_steps`로 중간중간 측정해야 합니다.
- **CI에서 평가를 생략하는 실수**: 사람이 수동으로 돌리면 언젠가는 빠집니다. 5분짜리 perplexity 검사는 PR마다 돌릴 가치가 충분합니다.

## 실무 메모

- **두 단 구조를 유지합니다**: 빠른 perplexity 체크는 CI에서, 느린 골든 세트 평가는 nightly에서 함께 돌립니다.
- **회귀 허용폭을 정합니다**: perplexity가 5% 이상 나빠지면 PR을 막는 식의 기준이 실용적입니다.
- **골든 세트를 카테고리로 나눕니다**: 형식, 사실성, 안전성, 도메인 지식처럼 묶으면 약점이 더 빨리 드러납니다.
- **사람 평가는 페어 비교로 합니다**: 두 모델 출력을 나란히 놓고 어느 쪽이 더 나은지만 묻는 방식이 절대 점수보다 안정적입니다.
- **자동 평가는 어디까지나 보조선입니다**: BLEU, ROUGE, LLM-as-judge 모두 한계가 있습니다. 최종 판단은 사람 검토와 함께 가야 합니다.

## 체크리스트

- [ ] perplexity가 평균 손실의 지수값이라는 점을 이해했습니다.
- [ ] 평가 루프에서 `no_grad`와 `eval`을 쓰는 이유를 설명할 수 있습니다.
- [ ] `python main.py`를 실행해 학습 전후 perplexity 출력이 실제로 나오는지 확인했습니다.
- [ ] 골든 세트의 의미와 한계를 설명할 수 있습니다.
- [ ] 서빙 전에 최소한의 정량 평가를 수행하는 습관을 잡았습니다.

## 연습 문제

1. 평가 데이터셋을 2개에서 20개 항목으로 늘려 보세요. perplexity 분산이 줄어드나요?
2. 골든 세트에 수학 계산 항목 5개를 추가하고, 파인튜닝 전후 점수를 비교해 보세요. 모든 카테고리가 같은 폭으로 좋아지나요?
3. `model.eval()` 호출을 빼고 perplexity 함수를 두 번 실행해 보세요. 결과가 어떻게 달라지나요?

## 정리 · 다음 글

평가는 화려하지 않지만 파인튜닝 파이프라인의 신뢰를 만드는 단계입니다. 생성 예시를 보기 전에 기준선을 세워 두면 이후 실험이 감에 덜 의존하게 됩니다. 실무 패턴은 분명합니다. 아래에는 빠른 정량 신호인 perplexity를 두고, 위에는 느린 정성 평가인 골든 세트와 사람 검토를 둡니다.

다음 글인 6편에서는 서빙을 다룹니다. LoRA 어댑터를 베이스 모델과 분리한 채 배포하는 방법과, 추론 시 메모리와 지연 시간을 어떻게 다뤄야 하는지 보겠습니다.

## 평가 지표 묶음: perplexity 하나로 끝내지 않는 구성

perplexity는 빠르고 유용하지만 단독 지표로는 부족합니다. 실무에서는 아래처럼 지표를 층으로 묶는 편이 안정적입니다.

| 층 | 지표 | 실행 주기 | 목적 |
| --- | --- | --- | --- |
| 빠른 회귀 감지 | perplexity, eval loss | PR/커밋마다 | 즉시 실패 차단 |
| 태스크 성능 | exact match, F1, format pass rate | daily/nightly | 기능 품질 추적 |
| 사용자 체감 | 사람 평가, pairwise preference | 주간/릴리스 전 | 배포 의사결정 |

이 구조를 쓰면 "빠른 신호는 자동, 느린 신호는 집중"이라는 운영 원칙이 자연스럽게 자리 잡습니다.

## perplexity 계산 시 흔한 함정과 보정 방법

| 함정 | 잘못된 결론 | 보정 방법 |
| --- | --- | --- |
| 학습 데이터와 평가 데이터 겹침 | 과도한 낙관 | hold-out 분리 |
| 길이 분포 차이 무시 | 모델 회귀 오판 | 동일 길이 버킷 비교 |
| 드롭아웃 활성 상태 평가 | 재현성 붕괴 | `model.eval()` 강제 |
| 샘플 수 너무 적음 | 분산 과대 | 최소 수십~수백 샘플 |

평가 자동화에서 중요한 것은 숫자 자체보다, 언제나 같은 조건으로 계산되도록 만드는 것입니다.

## 골든 세트 채점 포맷 예시

아래처럼 JSONL로 평가셋을 두면 CI와 수동 검토를 함께 운용하기 쉽습니다.

```json
{"id": "fmt-001", "prompt": "FastAPI 400 에러 예시", "must_include": ["HTTPException", "400"], "must_not_include": ["Django"]}
{"id": "fmt-002", "prompt": "리스트 뒤집기 방법", "must_include": ["[::-1]", "reverse"], "must_not_include": ["numpy"]}
```

채점 함수는 단순 키워드 포함부터 시작해도 충분합니다. 중요한 것은 "같은 프롬프트를 같은 규칙으로 반복 평가"하는 체계를 갖추는 것입니다.

## 평가 출력 예시: 사람이 바로 읽을 수 있는 리포트

```text
run_id=2026-05-20-lora-r16
eval_samples=320
before_ppl=18.42
after_ppl=16.95
delta_pct=-7.98
golden_pass_rate=0.81
format_pass_rate=0.93
blocked=0
```

이 형식은 콘솔에서도 읽기 쉽고, 이후 CSV/대시보드로 옮기기도 쉽습니다.

## loss curve와 perplexity를 함께 읽는 패턴

평가 시점에 아래 관계를 함께 확인하면 해석이 빨라집니다.

1. train loss 하강 + eval perplexity 하강: 정상 개선 가능성 높음
2. train loss 하강 + eval perplexity 정체/상승: 과적합 또는 데이터 누수 의심
3. train loss 진동 + eval perplexity 진동: 학습률 과대, 배치 불안정 의심

즉 "학습 손실만 좋아진 모델"은 배포 후보가 아닙니다. 평가 지표의 방향이 함께 맞아야 합니다.

## before/after 생성 비교: 정량 지표의 의미를 확인하는 앵커

```text
[Prompt]
HTTP 401과 403의 차이를 2문장으로 설명해 주세요.

[Before]
401 and 403 are authentication errors and related with forbidden access.

[After]
401은 인증 정보가 없거나 유효하지 않을 때 반환됩니다.
403은 인증은 되었지만 해당 자원에 대한 권한이 없을 때 반환됩니다.
```

정량 지표가 좋아졌다면 이런 비교에서도 일관된 품질 상승이 함께 보여야 합니다.

## 평가 자동화 스크립트 골격

```python
def evaluate_run(model, tokenizer, eval_dataset, golden_set):
    ppl = perplexity(model, eval_dataset)
    golden_score = score_golden(model, tokenizer, golden_set)
    return {
        "perplexity": round(ppl, 4),
        "golden_score": round(golden_score, 4),
    }

result = evaluate_run(peft_model, tokenizer, eval_dataset, golden)
print(result)
```

복잡한 프레임워크를 바로 도입하지 않아도, 이런 작은 함수 하나로 "평가 없는 학습" 상태를 빠르게 벗어날 수 있습니다.

## 실전 패턴 추가: 데이터 준비, LoRA 설정, 학습 입력 검증을 한 흐름으로 점검하기

파인튜닝 품질은 모델 아키텍처보다 입력 계약에서 먼저 결정됩니다. 데이터셋 템플릿, LoRA 설정, 길이 통계를 따로 보지 말고 같은 파이프라인에서 검증해야 디버깅 비용이 줄어듭니다.

```python
from dataclasses import dataclass
from typing import Iterable

from peft import LoraConfig

@dataclass
class Sample:
    instruction: str
    input: str
    output: str

def render(sample: Sample) -> str:
    return (
        "### Instruction:
" + sample.instruction + "

"
        "### Input:
" + sample.input + "

"
        "### Response:
" + sample.output
    )

def build_lora_config() -> LoraConfig:
    return LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

def length_stats(lengths: Iterable[int]) -> tuple[int, float, int]:
    data = sorted(lengths)
    if not data:
        return 0, 0.0, 0
    avg = sum(data) / len(data)
    p95 = data[int(len(data) * 0.95) - 1]
    return min(data), avg, p95
```

운영 관점에서는 `target_modules`와 데이터 템플릿이 함께 관리되어야 합니다. 템플릿이 바뀌면 토큰 길이 분포가 바뀌고, 이는 배치 크기와 학습 안정성에 바로 영향을 줍니다. 따라서 데이터 버전, LoRA 설정 버전, 평가 지표를 같은 실험 단위로 묶어 기록하는 것이 필수입니다. 이렇게 해야 특정 품질 변화가 데이터 문제인지, 어댑터 설정 문제인지 빠르게 분리할 수 있습니다.

## 평가셋 설계: 카테고리 기반으로 회귀를 잡는 방법

골든 세트를 무작위로 모으기만 하면 회귀 원인을 설명하기 어렵습니다. 카테고리 태그를 붙여 관리하면 훨씬 유용합니다.

| 카테고리 | 예시 프롬프트 수 | 주요 지표 |
| --- | --- | --- |
| 형식 준수 | 30 | format pass rate |
| 사실성 | 40 | keyword + human check |
| 도메인 용어 | 30 | exact/contains |
| 안전성 | 20 | blocked response rate |

운영에서는 카테고리별 점수를 주간 단위로 보고, 하락한 구간만 집중 리뷰하는 방식이 효율적입니다.

## 평가 결과 표준 출력 포맷

```text
model=llama-3-8b + adapter:v3
dataset=eval_2026_05
perplexity=15.84
golden_total=120
golden_pass=98
format_pass_rate=0.95
safety_block_rate=0.99
```

이 포맷을 고정하면 실험 노트, CI 로그, 대시보드가 같은 언어를 사용하게 됩니다.

## before/after 생성 품질 비교: 평가 보고서에 포함할 최소 예시

```text
[Prompt]
Flask에서 404 예외 처리 예시를 보여 주세요.

[Before]
Flask has error handling and you can customize 404 pages.

[After]
@app.errorhandler(404)
def handle_404(_):
    return {"error": "not found"}, 404
```

정량 지표와 함께 이런 샘플 5~10개를 같이 보관하면 릴리스 회의에서 결론을 빠르게 낼 수 있습니다.

## perplexity와 사용자 지표가 충돌할 때의 판단 규칙

| 상황 | 권장 판단 |
| --- | --- |
| perplexity 개선, 골든 점수 하락 | 배포 보류, 데이터/프롬프트 점검 |
| perplexity 악화, 골든 점수 개선 | 소폭이면 허용 가능, 장기 추세 관찰 |
| 둘 다 악화 | 즉시 롤백 후보 |
| 둘 다 개선 | 배포 후보 |

평가의 핵심은 단일 숫자가 아니라 의사결정 규칙을 미리 정해 두는 것입니다.

## 평가 실행 예시: CLI 출력으로 남기는 최소 리포트

```bash
python eval.py \
  --base-model meta-llama/Llama-3-8B-Instruct \
  --adapter artifacts/adapter-v3 \
  --eval-jsonl data/eval.jsonl \
  --golden-jsonl data/golden.jsonl
```

```text
Pass  run_id=2026-05-21-v3
Pass  perplexity=15.42 (baseline=16.10, delta=-4.22%)
Pass  golden_pass_rate=0.84 (threshold=0.80)
Pass  format_pass_rate=0.95 (threshold=0.92)
Fail  safety_block_rate=0.97 (threshold=0.99)
```

이런 출력은 릴리스 의사결정에 바로 사용할 수 있습니다. 어떤 지표가 왜 실패했는지 명확히 보이기 때문입니다.

## 평가 데이터셋 누수 방지 체크

| 점검 항목 | 확인 방법 |
| --- | --- |
| 학습/평가 중복 | 해시 기반 중복 검사 |
| 템플릿 누수 | 동일 프롬프트 패턴 비율 확인 |
| 날짜 누수 | 최신 데이터가 과도하게 평가셋에 편향됐는지 확인 |
| 정답 누수 | expected 문구가 프롬프트에 직접 포함되는지 검사 |

누수는 지표를 인위적으로 좋게 보이게 만들고, 실제 배포 후 품질 하락으로 이어집니다.

## 메트릭 확장 예시: 형식 준수율 채점 함수

```python
def format_pass_rate(outputs):
    passed = 0
    for text in outputs:
        cond_1 = "```python" in text or "@app" in text
        cond_2 = len(text.strip()) > 20
        if cond_1 and cond_2:
            passed += 1
    return passed / len(outputs)
```

도메인에 맞는 형식 규칙을 이렇게 함수로 명시하면, 평가 기준을 팀 전체가 같은 코드로 공유할 수 있습니다.

## 평가 결과 저장 포맷 권장안

```json
{
  "run_id": "2026-05-21-v3",
  "model": "llama-3-8b + lora-v3",
  "perplexity": 15.42,
  "golden_pass_rate": 0.84,
  "format_pass_rate": 0.95,
  "safety_block_rate": 0.97,
  "decision": "hold"
}
```

이런 결과 파일을 남기면 6편의 서빙 릴리스 자동화에서 배포 게이트로 바로 연결할 수 있습니다.

평가 자동화의 목표는 점수를 예쁘게 만드는 것이 아니라, 회귀를 빨리 발견해 배포 리스크를 줄이는 데 있습니다. 이 관점을 팀 합의로 고정해 두면 지표 해석 갈등이 크게 줄어듭니다.

그래서 평가 문서에는 항상 "통과 기준"과 "실패 시 조치"를 한 줄로 같이 적는 편이 좋습니다.

이렇게 해야 평가 결과가 실제 운영 행동으로 연결됩니다.

끝.

## 처음 질문으로 돌아가기

- **파인튜닝 직후 가장 먼저 봐야 할 정량 신호인 perplexity는 어떻게 계산할까요?**
  - 본문의 기준은 모델 평가를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **학습 전후 perplexity 비교만으로는 왜 평가가 충분하지 않을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **작은 데모 모델에서도 왜 별도의 평가 루프를 유지해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Fine-tuning 101 (1/6): LLM 파인튜닝 입문](./01-intro.md)
- [LLM Fine-tuning 101 (2/6): 데이터셋 준비와 전처리](./02-dataset.md)
- [LLM Fine-tuning 101 (3/6): LoRA 어댑터 구성](./03-lora.md)
- [LLM Fine-tuning 101 (4/6): 학습 루프와 하이퍼파라미터](./04-training.md)
- **LLM Fine-tuning 101 (5/6): 모델 평가 (현재 글)**
- LLM Fine-tuning 101 (6/6): 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Perplexity of fixed-length models](https://huggingface.co/docs/transformers/perplexity)
- [Evaluation best practices for language models](https://huggingface.co/docs/evaluate/index)
- [LLM-as-a-judge survey](https://arxiv.org/abs/2306.05685)
- [HELM: Holistic Evaluation of Language Models](https://crfm.stanford.edu/helm/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-finetuning-101/ko/05-evaluation)

Tags: Fine-tuning, LoRA, LLM, Python
