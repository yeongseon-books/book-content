---
title: "LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화"
series: llm-apps-ops-101
episode: 2
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/285"
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
seo_description: 호출별 토큰과 비용을 먼저 기록해야 캐시, 프롬프트 압축, 모델 라우팅 같은 최적화가 추측이 아니라 검증 가능한 결정이 됩니다.
---

# LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화

이 글은 LLM Apps Ops 101 시리즈의 두 번째 글입니다.

"이번 달 OpenAI 청구서가 왜 3배죠?" 슬랙에 이 메시지가 올라왔을 때, 가장 어려운 부분은 금액 자체가 아닙니다. 어려운 부분은 그 다음 질문입니다. "어떤 엔드포인트에서 많이 썼지?", "언제부터 늘었지?", "누가 긴 프롬프트를 배포했지?" 호출 단위 비용 기록이 없으면, 이 질문들에 답할 방법이 없습니다. 팀은 비용 폭발을 겪은 게 아니라 비용 폭발을 목격만 한 겁니다.

저는 팀들이 데모 단계에서 "LLM 비용은 미미합니다"라고 보고하면서, 정작 반복 호출과 배치 작업이 붙는 순간 청구서가 10배 뛰는 걸 첫 달에야 발견하는 경우를 여러 번 봤습니다. 문제는 비용이 비싼 게 아니라, 비용이 어디서 만들어지는지 모른 채 한 달을 보냈다는 겁니다. 한 달치 최적화 기회가 사라진 셈입니다.

비용 추적의 출발점은 회계가 아닙니다. 운영 의사결정을 수치로 내릴 수 있는 계측 장치, 이것이 출발점입니다.

![비용 추적 흐름과 최적화 지점](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-01-big-picture.ko.png)
*호출 한 건의 토큰 기록이 캐시·라우팅·압축 결정으로 이어지는 흐름*
> 비용은 월말에 발견하는 숫자가 아니라, 요청마다 남겨야 하는 운영 신호입니다.

## 이 글에서 다룰 문제

- LLM 비용은 왜 월말 청구서가 아니라 호출 단위에서 추적해야 할까요?
- 단가표를 코드에서 분리하면 어떤 운영 실험이 쉬워질까요?
- 캐시, 모델 교체, 프롬프트 압축 중 무엇부터 줄일지 어떻게 판단할까요?

## 왜 호출 단위 추적이 월말 청구서를 이기는가

![호출별 토큰이 누적 비용으로 모이는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-01-why-this-layer-matters.ko.png)

*호출별 토큰이 누적 비용으로 모이는 흐름*

월말 청구서는 "이번 달 총 $1,200"이라고 말해 줍니다. 하지만 이 숫자에는 수천 개의 호출이 뭉쳐 있어서, 어떤 요청이 얼마를 만들었는지 분해할 수 없습니다. 호출 단위 기록이 있으면 전혀 다른 질문이 가능해집니다.

| 월말 청구서로 알 수 있는 것 | 호출 단위 추적으로 알 수 있는 것 |
|---|---|
| 총 비용 | route별 비용 기여도 |
| 모델별 합계 | 특정 프롬프트의 반복 패턴 |
| 전월 대비 증감 | 비용 급증 시작 시점 (시간 단위) |
| — | 캐시 후보 자동 식별 |
| — | 프롬프트 버전별 비용 비교 |

저는 한 팀이 월말 청구서만 보고 "모델을 더 싼 걸로 바꾸자"고 결정했다가, 정작 비용의 60%가 반복 호출에서 나오고 있던 걸 나중에 발견한 경우를 알고 있습니다. 캐시 하나 붙였으면 모델 교체 없이 비용을 절반으로 줄일 수 있었습니다. 호출 단위 데이터 없이 내린 최적화 결정은 높은 확률로 방향이 틀립니다.

이 글의 나머지는 이 호출 단위 추적을 어떻게 코드로 만들고, 그 데이터에서 어떤 최적화 판단을 내릴 수 있는지 단계별로 보여드리겠습니다.

## 최소 실행 예제 — 호출 한 건의 비용을 기록하기

```python
import json
import os
from dataclasses import asdict, dataclass

from groq import Groq

MODEL = "llama-3.1-8b-instant"
INPUT_PRICE_PER_MILLION_TOKENS = 0.05
OUTPUT_PRICE_PER_MILLION_TOKENS = 0.08

@dataclass
class CostRecord:
    prompt: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float

def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    prompt_cost = (prompt_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION_TOKENS
    completion_cost = (completion_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION_TOKENS
    return round(prompt_cost + completion_cost, 8)

def run_prompt(client: Groq, prompt: str) -> CostRecord:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a concise Python assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    usage = response.usage
    if usage is None:
        raise RuntimeError("usage metadata missing from Groq response")
    return CostRecord(
        prompt=prompt,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
        cost_usd=estimate_cost(usage.prompt_tokens, usage.completion_tokens),
    )

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompts = [
        "Summarize Python decorators in one sentence.",
        "Summarize Python decorators in one sentence.",
        "Summarize asyncio.gather in one sentence.",
    ]
    records = [run_prompt(client, prompt) for prompt in prompts]
    report = {
        "input_price_per_million_tokens": INPUT_PRICE_PER_MILLION_TOKENS,
        "output_price_per_million_tokens": OUTPUT_PRICE_PER_MILLION_TOKENS,
        "total_calls": len(records),
        "total_tokens": sum(record.total_tokens for record in records),
        "total_cost_usd": round(sum(record.cost_usd for record in records), 8),
        "records": [asdict(record) for record in records],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

이 코드에서 중요한 점은 계산 로직이 아닙니다. 중요한 점은 설계 결정 세 가지입니다.

![반복 프롬프트가 캐시 후보가 되는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-02-what-to-notice-in-this-code.ko.png)

*반복 프롬프트가 캐시 후보가 되는 구조*

**첫째, 입력과 출력 단가를 분리합니다.** 대부분의 LLM 벤더는 입력 토큰과 출력 토큰의 가격을 다르게 책정합니다. 이 분리를 처음부터 코드에 넣어 두면, 나중에 "비용이 입력에서 생기는가, 출력에서 생기는가"를 바로 확인할 수 있습니다. 총합만 기록하면 이 구분이 영원히 불가능합니다.

**둘째, 호출마다 CostRecord를 남깁니다.** 누적 합계만 있으면 "비싸다"는 사실만 알 수 있습니다. 하지만 호출별 레코드가 있으면 어떤 프롬프트가 반복되고 있는지, 특정 작업이 유난히 토큰을 많이 쓰는지를 나중에 다시 추적할 수 있습니다.

**셋째, 같은 프롬프트를 일부러 반복합니다.** 예제에서 "Summarize Python decorators"를 두 번 보낸 이유는 캐시 후보를 보여 주기 위해서입니다. 실제 운영에서도 반복 호출 비율을 먼저 확인하는 것이 비용 절감의 가장 안전한 출발점입니다.

## 단가표를 코드 구조로 분리하는 이유

운영에서는 금방 두 가지 요구가 생깁니다. 모델마다 단가가 다르고, 모델을 교체하는 실험을 자주 해야 한다는 겁니다. 단가 상수가 비용 계산 함수 안에 하드코딩되어 있으면, 모델 비교 실험을 할 때마다 코드를 수정해야 합니다. 분리해 두면 설정만 바꿔서 실험을 돌릴 수 있습니다.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PriceCard:
    input_per_million: float
    output_per_million: float

PRICE_CARDS = {
    "llama-3.1-8b-instant": PriceCard(input_per_million=0.05, output_per_million=0.08),
    "llama-3.1-70b-versatile": PriceCard(input_per_million=0.59, output_per_million=0.79),
    "gpt-4o-mini": PriceCard(input_per_million=0.15, output_per_million=0.60),
}

def estimate_split_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    price = PRICE_CARDS[model]
    input_cost = (prompt_tokens / 1_000_000) * price.input_per_million
    output_cost = (completion_tokens / 1_000_000) * price.output_per_million
    return round(input_cost + output_cost, 8)
```

이 분리가 만드는 실제 차이를 예로 들겠습니다. "입력은 2,000토큰인데 출력은 50토큰인 요약 작업"과 "입력은 100토큰인데 출력은 1,500토큰인 생성 작업"은 총 토큰 수가 비슷해도 과금 패턴이 완전히 다릅니다. 요약 작업은 입력 단가가 싼 모델로 보내는 게 유리하고, 생성 작업은 출력 단가가 싼 모델로 보내는 게 유리합니다. 단가표가 분리되어 있어야 이 비교가 가능합니다.

저는 한 팀이 PriceCard 분리 없이 6개월을 운영하다가, 모델을 교체할 때 비용 비교를 하려고 과거 데이터를 뒤졌는데 입력/출력 분리가 안 되어 있어서 결국 2주간 A/B 테스트를 다시 돌려야 했던 경우를 봤습니다. 처음부터 분리해 뒀으면 기존 데이터만으로 시뮬레이션할 수 있었습니다.

## 캐시 후보와 최적화 우선순위를 데이터로 정하기

비용 절감은 한 가지 레버만으로 끝나지 않습니다. 반복 호출은 캐시로 줄이고, 긴 시스템 프롬프트는 압축으로 줄이고, 쉬운 작업은 더 싼 모델로 라우팅합니다. 문제는 이 레버들의 우선순위를 어떻게 정하느냐입니다. 감으로 정하면 효과가 작은 곳에 시간을 쓰게 됩니다.

```python
from collections import Counter
from dataclasses import asdict, dataclass

@dataclass
class OptimizationReport:
    total_calls: int
    repeated_prompt_count: int
    cache_candidate_ratio: float
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost_usd: float
    input_cost_ratio: float  # input cost / total cost

def build_optimization_report(records: list[CostRecord]) -> OptimizationReport:
    prompt_counter = Counter(record.prompt for record in records)
    repeated = sum(count for count in prompt_counter.values() if count > 1)
    total_input = sum(record.prompt_tokens for record in records)
    total_output = sum(record.completion_tokens for record in records)
    input_cost = (total_input / 1_000_000) * INPUT_PRICE_PER_MILLION_TOKENS
    output_cost = (total_output / 1_000_000) * OUTPUT_PRICE_PER_MILLION_TOKENS
    total_cost = input_cost + output_cost
    return OptimizationReport(
        total_calls=len(records),
        repeated_prompt_count=repeated,
        cache_candidate_ratio=round(repeated / len(records), 3),
        total_prompt_tokens=total_input,
        total_completion_tokens=total_output,
        total_cost_usd=round(total_cost, 8),
        input_cost_ratio=round(input_cost / total_cost, 3) if total_cost > 0 else 0.0,
    )
```

이 리포트에서 읽을 수 있는 판단 기준은 세 가지입니다.

| 리포트 필드 | 읽는 방법 | 다음 행동 |
|---|---|---|
| `cache_candidate_ratio > 0.3` | 반복 호출이 30% 이상 | 의미 캐시(semantic cache) 도입 검토 |
| `input_cost_ratio > 0.7` | 비용 대부분이 입력에서 발생 | 시스템 프롬프트 압축, context 축소 |
| `input_cost_ratio < 0.3` | 비용 대부분이 출력에서 발생 | max_tokens 제한, 출력 포맷 간소화 |

이 표가 중요한 이유는, 최적화 우선순위를 사람의 직관이 아니라 데이터에서 결정하기 때문입니다. 실제로 많은 팀이 "프롬프트가 길어서 비쌀 것이다"라고 가정하고 프롬프트 압축부터 시작하지만, 데이터를 보면 반복 호출이 비용의 주범인 경우가 훨씬 많습니다.

## 비용 경고를 감정이 아니라 조건문으로 다루기

비용 추적은 숫자를 쌓는 데서 끝나면 효과가 약합니다. 비용이 오르는 조건을 자동으로 탐지하고, 어떤 행동을 취해야 하는지 바로 이어져야 합니다. 그래서 비용 코드는 `수집 → 분석 → 조치` 세 단계로 나눠야 합니다.

```python
from dataclasses import dataclass

@dataclass
class CostAlert:
    key: str
    current_usd: float
    baseline_usd: float
    increase_ratio: float

def aggregate_daily_cost(rows: list[dict]) -> dict[str, float]:
    """route|model|prompt_version 단위로 일간 비용 집계."""
    totals: dict[str, float] = {}
    for row in rows:
        key = f"{row['route']}|{row['model']}|{row['prompt_version']}"
        totals[key] = totals.get(key, 0.0) + row["estimated_cost_usd"]
    return totals

def detect_cost_alerts(
    current: dict[str, float],
    baseline: dict[str, float],
    ratio_threshold: float = 1.5,
    min_delta_usd: float = 5.0,
) -> list[CostAlert]:
    """baseline 대비 ratio_threshold 이상 증가하고, 절대 증가분이 min_delta_usd 이상이면 경고."""
    alerts: list[CostAlert] = []
    for key, curr in current.items():
        base = baseline.get(key, 0.0)
        if base <= 0:
            continue
        ratio = curr / base
        if ratio >= ratio_threshold and curr - base >= min_delta_usd:
            alerts.append(CostAlert(key, round(curr, 2), round(base, 2), round(ratio, 2)))
    return alerts
```

이 코드에서 `prompt_version`을 집계 키에 포함하는 이유가 있습니다. 같은 route라도 프롬프트 변경 이후 비용이 늘었는지 즉시 확인할 수 있어야 하기 때문입니다. 저는 한 팀이 시스템 프롬프트에 few-shot 예시 3개를 추가한 뒤 입력 토큰이 40% 증가했는데, route 단위로만 집계하고 있어서 원인을 찾는 데 3일이 걸린 경우를 봤습니다. `prompt_version`이 키에 있었으면 당일 경고가 떴을 겁니다.

baseline은 7일 이동 평균으로 두는 편이 안전합니다. 요일별 트래픽 패턴이 있는 서비스에서 단일 전일 대비로 비교하면 월요일마다 거짓 경고가 울립니다.

## 모델 라우팅과 캐시를 비용/품질 함께 평가하기

비용 최적화에서 가장 자주 실패하는 패턴은 비용만 보고 결정을 내리는 겁니다. 저가 모델로 전환해 비용은 줄였지만 재시도율이 늘어 총 비용이 다시 올라가는 경우, 캐시 적중률이 높아 보이지만 캐시 무효화 기준이 느슨해서 오래된 답변을 더 싸게 뿌리는 경우. 두 시나리오 모두 비용만 보면 성공으로 보이지만 제품은 나빠지고 있습니다.

![최적화 레버에 품질 검증이 함께 필요한 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-03-where-engineers-get-confused.ko.png)

*최적화 레버에 품질 검증이 함께 필요한 구조*

그래서 운영 기준은 "호출 단가" 하나가 아니라 네 가지 지표의 묶음입니다.

| 실험 항목 | 변경 전 | 변경 후 | 판정 기준 |
|---|---|---|---|
| 캐시 히트율 | 12% | 41% | 히트율 30% 이상이면 유지 |
| 요청당 평균 비용 | $0.018 | $0.011 | 30% 이상 절감이면 유지 |
| 품질 실패율 | 2.1% | 2.5% | 3% 이하면 허용 |
| 재시도율 | 5.8% | 4.9% | 증가하지 않으면 통과 |

이 표를 반드시 채운 뒤에 최적화 결정을 내려야 합니다. 비용은 줄었지만 품질 실패율이 임계치를 넘었다면 즉시 롤백합니다. 비용 레이어의 목표는 가장 싼 모델을 찾는 것이 아니라, 제품 품질을 유지하면서 예측 가능한 단가를 만드는 것입니다.

실무에서 안전한 우선순위는 다음과 같습니다.

1. **반복 호출에 캐시를 적용합니다.** 무손실 절감이라 품질 위험이 가장 낮습니다.
2. **시스템 프롬프트를 정리합니다.** 모든 요청에 붙는 긴 지시문은 누적 비용을 빠르게 키웁니다.
3. **품질 여유가 있는 작업을 저가 모델로 라우팅합니다.** 분류, 라벨링처럼 정답이 명확한 작업부터 시작합니다.
4. **배치 가능한 작업을 실시간 경로에서 분리합니다.** 배치 API는 보통 50% 할인을 제공합니다.

## 매일 보는 비용 지표 — 월말을 기다리지 않기

월말 청구서는 늦습니다. 비용 이상을 하루 단위로 잡으려면 매일 같은 네 가지 숫자를 봐야 합니다.

| 지표 | 왜 매일 봐야 하는가 | 이상 신호 |
|---|---|---|
| 요청당 평균 비용 | 전체 합계보다 단가 추이가 민감 | 전일 대비 20% 이상 증가 |
| 상위 10개 고비용 route | 비용 집중 지점 변화 확인 | 새로운 route가 상위에 진입 |
| 캐시 미스 비중 | 캐시 효과 퇴화 탐지 | 미스율 60% 이상으로 증가 |
| 출력 토큰 편차 | 응답 장황화, 프롬프트 드리프트 탐지 | 표준편차가 평균의 2배 초과 |

특히 출력 토큰 편차가 커지는 날은 주의가 필요합니다. 모델이 갑자기 장문 응답을 생성하기 시작했거나, 프롬프트 변경으로 출력 포맷이 불안정해진 신호일 수 있습니다.

이 지표를 팀 대시보드에 고정해 두면, 엔지니어링과 제품 팀이 같은 숫자를 보고 우선순위를 합의할 수 있습니다. 비용 논의가 감정적 논쟁에서 데이터 기반 실험으로 바뀌는 지점이 바로 여기입니다.

## 비용 급증 시 1시간 안에 원인 좁히기

비용 그래프가 갑자기 튀었을 때 "왜 올랐지?"를 1시간 안에 답하지 못하면, 다음 날까지 같은 비율로 비용이 빠져나갑니다. 압박 상황에서 즉석으로 분석 질문을 만들면 빠뜨리는 항목이 생깁니다. 그래서 절차를 미리 고정해 둬야 합니다.

**0-15분: 트래픽량 확인.** 요청 수가 그대로인데 비용만 늘었다면 단가, 토큰 수, 재시도 중 하나입니다. 트래픽이 함께 늘었다면 자연 증가인지 이상 유입인지 분리합니다.

**15-30분: 상위 고비용 route + 모델 조합 확인.** 특정 route에 비용이 집중되고 있다면 그 route의 프롬프트와 모델을 확인합니다.

**30-45분: 프롬프트 버전 변경 이력 + 캐시 히트율 확인.** 최근 배포에서 프롬프트가 바뀌었는지, 캐시 무효화가 대량 발생했는지 봅니다.

**45-60분: 품질 실패율 + 재시도율 확인.** 품질이 떨어져서 재시도가 늘었다면 표면상 비용 문제지만 실제 원인은 품질 회귀입니다.

```bash
# 1) 특정 기간의 호출 수와 평균 토큰 수 비교
python3 -m scripts.cost_report --since 2026-05-01 --until 2026-05-02

# 2) 반복 프롬프트 비율과 상위 프롬프트 확인
python3 -m scripts.cost_report --top-prompts 20

# 3) 모델별 비용 분포 확인
python3 -m scripts.cost_report --group-by model
```

이 절차를 런북에 두고 당번 엔지니어가 그대로 실행하면, 비용 이슈도 장애처럼 재현 가능한 대응 체계로 전환됩니다.

## 비용 최적화 실험을 안전하게 굴리기

비용 최적화는 기능 실험과 달리 실패 비용이 바로 청구서에 반영됩니다. 프롬프트를 잘못 줄이면 재시도가 늘어 오히려 비용이 증가할 수 있습니다. 그래서 실험 절차를 먼저 고정해야 합니다.

가설은 반드시 측정 가능한 문장이어야 합니다. "프롬프트 앞부분 요약을 제거하면 요청당 입력 토큰이 15% 감소한다"처럼 쓰면 성공/실패를 수치로 판정할 수 있습니다. "비용을 줄이자"는 가설이 아니라 구호입니다.

실험 절차는 다섯 단계입니다.

1. **가설 정의** — 측정 가능한 예측 문장으로 씁니다.
2. **샘플 트래픽 적용** — 전체의 10% 정도에만 적용합니다.
3. **비용 + 품질 동시 측정** — 24시간 이상 측정합니다.
4. **롤백 기준 확인** — 품질 실패율 1.5배 이상 증가 시 중단, 재시도율 20% 이상 증가 시 중단.
5. **전면 적용** — 4번 기준을 통과한 경우에만 확대합니다.

롤백 기준이 미리 정해져 있어야 합니다. 이 기준이 없으면 최적화가 성공인지 실패인지 매번 논쟁으로 끝납니다. 저는 롤백 기준 없이 "일단 적용하고 보자"로 시작한 팀이 품질 저하를 2주 뒤에야 발견하고, 그 사이 사용자 이탈이 늘어난 경우를 본 적 있습니다.

운영 조직이 커질수록 "누가 어떤 실험을 언제 켰는지"도 중요해집니다. 실험 ID를 비용 로그에 남기면, 월말에 "이 증가분은 실험 EXP-042 때문"이라고 바로 설명할 수 있습니다.

## 운영 체크리스트

- [ ] 호출별 `prompt_tokens`, `completion_tokens`, `total_tokens`를 저장하고 있다
- [ ] 단가 상수는 한 곳에 모으고 모델별로 분리되어 있다
- [ ] 누적 비용과 호출별 비용을 함께 리포트하고 있다
- [ ] 반복 프롬프트를 캐시 후보로 자동 표시하고 있다
- [ ] 비용 절감 실험에는 항상 품질 검증 결과를 같이 붙이고 있다
- [ ] 비용 경고 임계치와 롤백 기준이 문서화되어 있다

## 정리

책임 있게 비용을 줄이려면, 무엇이 비용을 만들었는지 호출 단위로 먼저 가리킬 수 있어야 합니다. 그래야 캐시, 프롬프트 압축, 모델 라우팅이 감이 아니라 검증 가능한 최적화가 됩니다.

이 글의 핵심은 비용 수치를 하나 더 만드는 것이 아닙니다. 비용 신호를 운영 질문으로 번역하는 것입니다. "비싸다"는 사실을 "어디서, 왜, 얼마나"로 분해해야 행동으로 이어집니다. 다음 글에서는 비용을 줄인 뒤 품질이 떨어지지 않았는지 확인하는 평가 레이어를 다루겠습니다.

## 처음 질문으로 돌아가기

- **LLM 비용은 왜 월말 청구서가 아니라 호출 단위에서 추적해야 할까요?**
  월말 총액만 보면 어떤 route, 모델, 프롬프트가 비용을 만들었는지 알 수 없어 최적화 방향이 틀릴 수 있습니다. 호출 단위 기록이 있으면 반복 패턴, 비용 집중 지점, 급증 시작 시점을 바로 확인할 수 있습니다.
- **단가표를 코드에서 분리하면 어떤 운영 실험이 쉬워질까요?**
  모델 비교, 캐시 효과 시뮬레이션, 프롬프트 압축 전후 비용 재산출을 과거 데이터만으로 할 수 있습니다. 분리되어 있지 않으면 A/B 테스트를 다시 돌려야 합니다.
- **캐시, 모델 교체, 프롬프트 압축 중 무엇부터 줄일지 어떻게 판단할까요?**
  OptimizationReport의 `cache_candidate_ratio`와 `input_cost_ratio`를 봅니다. 반복이 많으면 캐시, 입력 비용 비율이 높으면 프롬프트 압축, 품질 여유가 있으면 저가 모델 라우팅 순서입니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- **LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화 (현재 글)**
- [LLM Apps Ops 101 (3/6): LLM 출력 품질 평가](./03-evaluation.md)
- [LLM Apps Ops 101 (4/6): LLM 앱 보안](./04-security.md)
- [LLM Apps Ops 101 (5/6): LLM 앱 배포 전략](./05-deployment.md)
- [LLM Apps Ops 101 (6/6): LLM 앱 운영 완성](./06-ops-complete.md)

<!-- toc:end -->

---

## 참고 자료

- [LLM Apps Ops 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/llm-apps-ops-101/ko)
### 공식 문서

- [OpenAI API Pricing](https://openai.com/api/pricing/)
- [Anthropic API Pricing](https://www.anthropic.com/pricing#api)
- [Google AI Studio pricing](https://ai.google.dev/gemini-api/docs/pricing)

### 검증에 도움 되는 자료

- [OpenAI Prompt Caching 101](https://cookbook.openai.com/examples/prompt_caching101)

### 관련 시리즈

- [AI Evaluation 101](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md) — 이 시리즈가 운영 단계에서 추적하는 "LLM 품질"을 릴리스 전 단계에서 어떻게 측정할지 다룹니다. 모니터링 지표가 흔들릴 때, 어떤 평가 방식으로 회귀 여부를 확인할지 결정하는 데 도움이 됩니다.

Tags: LLMOps, Observability, Python, LLM
