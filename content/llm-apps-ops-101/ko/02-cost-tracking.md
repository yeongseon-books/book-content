---
title: LLM 비용 추적과 최적화
series: llm-apps-ops-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-01'
seo_description: 비용 추적은 회계가 아니라 피드백 루프입니다. 호출 한 건이 얼마였는지 알아야 캐시, 프롬프트 압축, 모델 라우팅이
  의미를 가집니다.
---

# LLM 비용 추적과 최적화

LLM 기능은 처음에는 싸게 보이지만, 반복 호출과 트래픽이 붙는 순간 비용 구조가 갑자기 선명해집니다. 호출 한 건의 토큰과 비용을 기록하지 않으면 최적화는 감이 아니라 추측으로 흘러가기 쉽습니다.

이 글은 LLM 앱 운영 101 시리즈의 2번째 글입니다. 여기서는 비용 추적을 단순한 집계가 아니라 캐시, 프롬프트 압축, 모델 라우팅 판단으로 이어지는 피드백 루프로 설계하는 방법을 다루겠습니다.

## 이 글에서 다룰 문제
- 반복 호출이 생길 때 토큰 사용량은 어떻게 누적해서 봐야 하는가?
- 단순한 백만 토큰당 단가 모델에는 어느 정도 추상화가 적당한가?
- 비용 절감 효과가 큰 지점을 가장 먼저 드러내는 숫자는 무엇인가?

> 비용 추적은 회계를 위한 회계가 아닙니다. 캐시, 프롬프트 압축, 라우팅 결정이 실제로 효과가 있는지 보여 주는 피드백 루프입니다.

## 큰 그림
![비용 추적 흐름과 최적화 지점](../../../assets/llm-apps-ops-101/02/02-01-big-picture.ko.png)

*비용 추적 흐름과 최적화 지점*
## 왜 이 레이어가 필요한가
![호출별 토큰이 누적 비용으로 모이는 흐름](../../../assets/llm-apps-ops-101/02/02-01-why-this-layer-matters.ko.png)

*호출별 토큰이 누적 비용으로 모이는 흐름*
비용은 LLM 기능이 성공할수록 더 중요해지는 운영 지표입니다. 그래서 초기에 계산식을 코드로 박아 두는 편이 낫습니다.

LLM 비용은 대부분 작게 시작해서 갑자기 커집니다. 개발 단계에서는 몇 원 수준이라 무시되지만, 배치 작업이나 반복 질문이 붙는 순간 토큰 누적량이 먼저 폭발합니다.

예제 파일: `/root/Github/llm-apps-ops-101/ko/02-cost-tracking/main.py`

## 최소 실행 예제
```python
import json
import os
from dataclasses import asdict, dataclass

from groq import Groq

MODEL = "llama-3.1-8b-instant"
PRICE_PER_MILLION_TOKENS = 0.05

@dataclass
class CostRecord:
    prompt: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float

def estimate_cost(total_tokens: int) -> float:
    return round((total_tokens / 1_000_000) * PRICE_PER_MILLION_TOKENS, 8)

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
        cost_usd=estimate_cost(usage.total_tokens),
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
        "price_per_million_tokens": PRICE_PER_MILLION_TOKENS,
        "total_calls": len(records),
        "total_tokens": sum(record.total_tokens for record in records),
        "total_cost_usd": round(sum(record.cost_usd for record in records), 8),
        "records": [asdict(record) for record in records],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

## 이 코드에서 봐야 할 것
![반복 프롬프트가 캐시 후보로 분리되는 구조](../../../assets/llm-apps-ops-101/02/02-02-what-to-notice-in-this-code.ko.png)

*반복 프롬프트가 캐시 후보로 분리되는 구조*
- `PRICE_PER_MILLION_TOKENS`를 상수로 두면 공급자나 플랜이 바뀌어도 계산식은 유지됩니다.
- 호출별 `CostRecord`를 남겨 두면 어떤 프롬프트가 비싼지 다시 계산하지 않아도 됩니다.
- 동일 프롬프트 두 번 호출을 일부러 넣어 두면 캐시 전후 비교 실험의 기준점이 생깁니다.

## 실무에서 헷갈리는 지점
![최적화 레버와 품질 확인이 맞물리는 구조](../../../assets/llm-apps-ops-101/02/02-03-where-engineers-get-confused.ko.png)

*최적화 레버와 품질 확인이 맞물리는 구조*
- 입력 토큰과 출력 토큰 단가가 다른 모델도 많습니다. 예제가 단순하더라도 분리 가능한 구조를 염두에 두는 편이 좋습니다.
- 누적 비용만 보면 이상 징후를 놓칩니다. 호출 수, 평균 토큰, 최댓값을 같이 봐야 합니다.
- 비용 최적화는 품질 저하와 함께 오기 쉽기 때문에 다음 장의 평가 레이어와 붙여서 봐야 합니다.

## 체크리스트
- [ ] 호출별 total_tokens를 저장한다
- [ ] 단가 상수를 코드 한 곳에서 관리한다
- [ ] 누적 비용과 호출별 비용을 함께 출력한다
- [ ] 반복 프롬프트를 분리해서 캐시 후보를 찾는다

## 정리
비용을 줄이려면 먼저 비용이 어디서 생기는지 보여야 합니다. 그 출발점이 호출별 토큰 기록입니다.

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

- [Groq pricing](https://groq.com/pricing/)
- [OpenAI pricing patterns](https://openai.com/api/pricing/)
- [Anthropic API pricing](https://www.anthropic.com/pricing#api)

Tags: LLMOps, Observability, Python, LLM
