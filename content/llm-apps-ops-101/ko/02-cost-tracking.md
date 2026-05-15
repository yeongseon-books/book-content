---
title: LLM 비용 추적과 최적화
series: llm-apps-ops-101
episode: 2
language: ko
status: publish-ready
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

# LLM 비용 추적과 최적화

LLM 비용은 데모 단계에서는 별일 아닌 것처럼 보이지만, 반복 프롬프트와 트래픽 증가, 배치 작업이 한꺼번에 붙는 순간 갑자기 눈에 띄기 시작합니다.

이 글은 LLM Apps Ops 101 시리즈의 두 번째 글입니다. 여기서는 호출별 토큰 사용량을 실제 비용 피드백 루프로 바꿔서, 캐시·프롬프트 압축·모델 라우팅 같은 최적화 판단을 수치로 검증하는 출발점을 만들겠습니다.

비용 최적화는 “조금 덜 쓰자” 같은 구호로는 잘 되지 않습니다. 어떤 호출이 얼마를 만들었는지 먼저 남겨야, 무엇을 줄이면 실제로 가장 큰 절감이 나는지 보입니다. 비용 추적은 회계가 아니라 운영 의사결정의 계측 장치입니다.

## 이 글에서 다룰 문제

- 반복 호출이 생길 때 토큰 사용량은 어떻게 누적해서 봐야 하는가?
- 단순한 백만 토큰당 단가 모델에는 어느 정도 추상화가 적당한가?
- 비용 절감 효과가 큰 지점을 가장 먼저 드러내는 숫자는 무엇인가?
- 캐시, 프롬프트 압축, 모델 라우팅 실험을 어떤 리포트로 비교해야 하는가?

> 비용 추적은 회계를 위한 회계가 아닙니다. 캐시, 프롬프트 압축, 라우팅 결정이 실제로 효과가 있는지 보여 주는 피드백 루프입니다.

## 큰 그림

![비용 추적 흐름과 최적화 지점](../../../assets/llm-apps-ops-101/02/02-01-big-picture.ko.png)

*비용 추적 흐름과 최적화 지점*

## 왜 이 레이어가 중요한가

![호출별 토큰이 누적 비용으로 모이는 흐름](../../../assets/llm-apps-ops-101/02/02-01-why-this-layer-matters.ko.png)

*호출별 토큰이 누적 비용으로 모이는 흐름*

비용은 기능이 실패할 때보다 오히려 성공할 때 더 중요해지는 지표입니다. 사용량이 늘수록 눈에 띄기 때문입니다.

LLM 비용은 대부분 작게 시작했다가, 반복 호출과 백그라운드 작업이 붙는 순간 갑자기 커집니다. 개발 단계에서는 몇 번의 테스트 호출이라 눈에 잘 띄지 않지만, 같은 프롬프트가 반복되거나 조금 긴 입력이 늘어나기 시작하면 누적 토큰 수가 먼저 튀어 오릅니다.

이 시점에서 호출별 기록이 없으면 최적화는 추측으로 흐릅니다. “캐시를 붙이면 줄어들 것 같다”, “프롬프트를 조금 줄이면 되지 않을까” 같은 말은 방향 정도만 제시할 뿐입니다. 실제로는 어떤 요청이 얼마나 많은 토큰을 쓰는지, 반복 호출이 어느 정도인지, 비용이 입력과 출력 중 어디에서 많이 생기는지를 먼저 봐야 합니다.

예제 파일: `en/02-cost-tracking/main.py`

## 최소 실행 예제

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

## 이 코드에서 먼저 볼 점

![반복 프롬프트가 캐시 후보가 되는 구조](../../../assets/llm-apps-ops-101/02/02-02-what-to-notice-in-this-code.ko.png)

*반복 프롬프트가 캐시 후보가 되는 구조*

- 입력 단가 상수와 출력 단가 상수를 분리해 두면, 이 모델의 실제 Groq 과금 방식과 예제가 맞아떨어집니다.
- 호출마다 `CostRecord`를 남기면 나중에 리포트를 다시 계산하지 않아도 이상치와 반복 패턴을 바로 볼 수 있습니다.
- 예제에서 같은 프롬프트를 일부러 반복한 이유는 캐시 후보를 보여 주기 위해서입니다.

이 코드가 좋은 출발점인 이유는 계산이 단순해서가 아니라, 비용이 호출 단위로 분해되어 남기 때문입니다. 누적 합계만 있으면 “비싸다”는 사실만 알 수 있습니다. 하지만 호출별 레코드가 있으면 어떤 프롬프트가 반복되고 있는지, 특정 작업이 유난히 토큰을 많이 쓰는지, 비용이 어디서 새고 있는지를 나중에 다시 추적할 수 있습니다.

## 단가표를 코드 구조로 먼저 분리하기

운영에서는 금방 두 가지 요구가 생깁니다. 첫째, 모델마다 단가가 다릅니다. 둘째, 입력 토큰과 출력 토큰 단가가 다를 수 있습니다. 처음부터 이 분리를 코드 구조에 넣어 두면, 나중에 가격표가 바뀌어도 보고서 형태를 다시 뜯어고칠 필요가 없습니다.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PriceCard:
    input_per_million: float
    output_per_million: float

PRICE_CARDS = {
    "llama-3.1-8b-instant": PriceCard(input_per_million=0.05, output_per_million=0.08),
    "llama-3.1-70b-versatile": PriceCard(input_per_million=0.59, output_per_million=0.79),
}

def estimate_split_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    price = PRICE_CARDS[model]
    input_cost = (prompt_tokens / 1_000_000) * price.input_per_million
    output_cost = (completion_tokens / 1_000_000) * price.output_per_million
    return round(input_cost + output_cost, 8)
```

이렇게 나누면 모델 라우팅 실험도 더 현실적으로 비교할 수 있습니다. 예를 들어 “입력은 긴데 출력은 짧은 작업”과 “입력은 짧고 출력이 긴 작업”은 같은 총토큰 수라도 실제 과금 패턴이 다를 수 있습니다. 단순 총합만 보면 이 차이가 가려집니다.

## 캐시 후보와 프롬프트 압축 효과를 함께 보는 리포트

비용 절감은 한 가지 레버만으로 끝나지 않습니다. 반복 호출은 캐시로 줄이고, 긴 system prompt는 압축으로 줄이고, 쉬운 작업은 더 싼 모델로 라우팅하는 식으로 여러 레버를 함께 씁니다. 중요한 것은 각 실험을 같은 리포트 형태로 비교하는 일입니다.

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

def build_optimization_report(records: list[CostRecord]) -> OptimizationReport:
    prompt_counter = Counter(record.prompt for record in records)
    repeated = sum(count for count in prompt_counter.values() if count > 1)
    return OptimizationReport(
        total_calls=len(records),
        repeated_prompt_count=repeated,
        cache_candidate_ratio=round(repeated / len(records), 3),
        total_prompt_tokens=sum(record.prompt_tokens for record in records),
        total_completion_tokens=sum(record.completion_tokens for record in records),
        total_cost_usd=round(sum(record.cost_usd for record in records), 8),
    )

report = build_optimization_report(records)
print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
```

**Expected output:**

```text
{
  "total_calls": 3,
  "repeated_prompt_count": 2,
  "cache_candidate_ratio": 0.667,
  "total_prompt_tokens": 126,
  "total_completion_tokens": 74,
  "total_cost_usd": 0.00001
}
```

이 출력에서 바로 읽을 수 있는 질문은 세 가지입니다. 반복 프롬프트 비율이 높은가, 비용 대부분이 입력에서 생기는가, 출력이 길어서 더 비싼가입니다. 이런 질문이 보여야 캐시를 붙일지, 프롬프트를 줄일지, 모델을 바꿀지 우선순위를 정할 수 있습니다.

## 실무에서는 무엇부터 줄일까

운영 초반에는 보통 다음 순서가 효율적입니다.

1. **반복 호출을 찾습니다.** 같은 질문이 반복되면 가장 먼저 캐시 후보입니다.
2. **system prompt 길이를 봅니다.** 모든 요청에 붙는 긴 지시문은 누적 비용을 빠르게 키웁니다.
3. **출력 길이를 봅니다.** 지나치게 장황한 응답은 품질 향상 없이 비용만 늘릴 수 있습니다.
4. **모델 라우팅을 실험합니다.** 쉬운 요청을 더 싼 모델로 보내되, 품질 게이트를 함께 둡니다.

핵심은 최적화 순서를 감으로 정하지 않는 데 있습니다. 어떤 필드가 실제로 큰 비용 기여도를 보였는지부터 확인해야 합니다.

## 어디서 자주 헷갈릴까요?

![최적화 레버에 품질 검증이 함께 필요한 구조](../../../assets/llm-apps-ops-101/02/02-03-where-engineers-get-confused.ko.png)

*최적화 레버에 품질 검증이 함께 필요한 구조*

- 많은 벤더는 입력 토큰과 출력 토큰의 단가를 다르게 책정합니다. 비용 레코드도 처음부터 그 분리를 반영하는 편이 안전합니다.
- 총비용 한 숫자만 보면 어디서 급증했는지가 가려집니다. 호출 수와 토큰 분포를 같이 봐야 합니다.
- 품질 검증 없이 비용만 줄이면, 결국 더 싼 대신 더 나쁜 제품을 만들 가능성이 큽니다.
- 캐시 적중률이 높아 보여도, 캐시 무효화 기준이 불안정하면 오래된 답변을 더 싸게 뿌리는 문제가 생길 수 있습니다.

현업에서는 “비용 최적화”라는 말을 너무 빨리 쓰는 경우가 많습니다. 실제로는 비용을 줄이는 행동이 품질을 함께 망가뜨릴 수 있습니다. 긴 프롬프트를 무조건 자르면 정확도가 떨어질 수 있고, 더 싼 모델로 라우팅하면 재시도와 사용자 불만이 늘 수 있습니다. 그래서 비용 추적은 반드시 품질 측정과 나란히 가야 합니다.

## 장애나 급증이 보이면 이렇게 확인합니다

비용 그래프가 갑자기 튀면, 우선 아래 순서로 좁혀 보는 편이 빠릅니다.

```bash
# 1) 특정 기간의 호출 수와 평균 토큰 수를 먼저 비교
python3 -m scripts.cost_report --since 2026-05-01 --until 2026-05-02

# 2) 반복 프롬프트 비율과 상위 프롬프트를 확인
python3 -m scripts.cost_report --top-prompts 20

# 3) 모델별 비용 분포를 확인
python3 -m scripts.cost_report --group-by model
```

실제 스크립트 이름은 달라질 수 있지만, 분석 질문은 거의 같습니다. 호출 수가 늘었는지, 호출당 토큰이 늘었는지, 특정 프롬프트나 모델이 급증했는지를 먼저 나눠 보면 원인을 훨씬 빨리 찾을 수 있습니다.

## 체크리스트

- [ ] 호출별 `prompt_tokens`, `completion_tokens`, `total_tokens`를 저장한다
- [ ] 단가 상수는 한 곳에 모으고 모델별로 분리한다
- [ ] 누적 비용과 호출별 비용을 함께 리포트한다
- [ ] 반복 프롬프트를 캐시 후보로 표시한다
- [ ] 비용 절감 실험에는 항상 품질 검증 결과를 같이 붙인다

## 정리

책임 있게 비용을 줄이려면, 무엇이 비용을 만들었는지 호출 단위로 먼저 가리킬 수 있어야 합니다. 그래야 캐시, 프롬프트 압축, 모델 라우팅이 감이 아니라 검증 가능한 최적화가 됩니다.

이 글의 핵심은 비용 수치를 하나 더 만드는 것이 아닙니다. 비용 신호를 운영 질문으로 번역하는 것입니다. 다음 글에서는 이 비용 최적화가 품질 저하를 만들지 확인하려면 어떤 평가 레이어가 필요한지 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- **LLM 비용 추적과 최적화 (현재 글)**
- LLM 출력 품질 평가 (예정)
- LLM 앱 보안 (예정)
- LLM 앱 배포 전략 (예정)
- LLM 앱 운영 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [OpenAI API Pricing](https://openai.com/api/pricing/)
- [Anthropic API Pricing](https://www.anthropic.com/pricing#api)
- [Google AI Studio pricing](https://ai.google.dev/gemini-api/docs/pricing)

### 검증에 도움 되는 자료

- [OpenAI Prompt Caching 101](https://cookbook.openai.com/examples/prompt_caching101)

Tags: LLMOps, Observability, Python, LLM
