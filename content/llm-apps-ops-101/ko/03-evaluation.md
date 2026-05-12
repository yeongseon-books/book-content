---
title: LLM 출력 품질 평가
series: llm-apps-ops-101
episode: 3
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
seo_description: 평가 자동화의 첫 단계는 의미를 완벽히 이해하는 심판을 만드는 것이 아니라, 명확하게 실패한 응답을 빠르게 걸러내는
  체를 만드는 것입니다.
---

# LLM 출력 품질 평가

LLM 앱은 응답이 눈앞에 보일 때는 그럴듯해 보여도, 호출 수가 늘어나면 사람이 일일이 품질을 확인할 수 없습니다. 그래서 초반 운영 단계에서는 완벽한 심판보다도 명백한 실패를 빠르게 걸러내는 규칙층이 더 실용적입니다.

이 글은 LLM 앱 운영 101 시리즈의 3번째 글입니다. 여기서는 길이, 키워드, 형식 같은 신호로 출력 품질을 자동 점검하는 가장 단순한 평가 레이어를 구성해 보겠습니다.

## 이 글에서 다룰 문제
- 모델 출력에 최대 길이 검사를 어떻게 자동화하는가?
- 키워드 포함 여부가 언제 유용한 품질 게이트가 되는가?
- 스키마 검증을 붙이기 전에 형식 검증은 어디까지 해야 하는가?

> 처음에 필요한 평가 레이어는 완벽한 의미 판단기가 아닙니다. 명백히 나쁜 답변을 빠르고 일관되게 걸러내는 값싼 필터입니다.

## 큰 그림
![LLM 출력 품질 평가 파이프라인](../../../assets/llm-apps-ops-101/03/03-01-big-picture.ko.png)

*LLM 출력 품질 평가 파이프라인*
## 왜 이 레이어가 필요한가
![규칙 기반 평가가 명확한 실패를 거르는 흐름](../../../assets/llm-apps-ops-101/03/03-01-why-this-layer-matters.ko.png)

*규칙 기반 평가가 명확한 실패를 거르는 흐름*
자동 평가는 모델을 심판으로 쓰기 전에, 기계적으로 실패를 걸러내는 규칙층부터 만드는 편이 실용적입니다.

실무에서는 모든 응답을 사람이 읽을 수 없습니다. 그래서 처음부터 완벽한 semantic judge를 만들기보다, 길이 초과·키워드 누락·형식 오류 같은 기계적으로 잡히는 실패를 먼저 막는 편이 훨씬 효율적입니다.

예제 파일: `/root/Github/llm-apps-ops-101/ko/03-evaluation/main.py`

## 최소 실행 예제
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
    missing_keywords: list[str]
    answer_length: int

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

def evaluate(text: str, expected_keywords: list[str]) -> EvalResult:
    try:
        payload = json.loads(text)
        answer = payload["answer"]
        keywords = payload["keywords"]
        format_ok = isinstance(answer, str) and isinstance(keywords, list)
    except Exception:
        return EvalResult(False, False, False, False, expected_keywords, 0)

    normalized_answer = answer.lower()
    normalized_keywords = {str(item).lower() for item in keywords}
    missing = [
        keyword
        for keyword in expected_keywords
        if keyword.lower() not in normalized_answer and keyword.lower() not in normalized_keywords
    ]
    length_ok = 60 <= len(answer) <= 280
    keywords_ok = not missing
    format_ok = format_ok
    return EvalResult(
        passed=length_ok and keywords_ok and format_ok,
        length_ok=length_ok,
        keywords_ok=keywords_ok,
        format_ok=format_ok,
        missing_keywords=missing,
        answer_length=len(answer),
    )

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    raw = ask_for_json(client, "Python's GIL")
    result = evaluate(raw, ["CPython", "thread", "lock"])
    print(json.dumps({"raw": json.loads(raw), "evaluation": asdict(result)}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

## 이 코드에서 봐야 할 것
![형식 길이 키워드 검사가 분리된 구조](../../../assets/llm-apps-ops-101/03/03-02-what-to-notice-in-this-code.ko.png)

*형식 길이 키워드 검사가 분리된 구조*
- `response_format={"type": "json_object"}`로 모델 출력 형태를 먼저 좁혀 두면 검사기가 단순해집니다.
- 평가 함수가 `missing_keywords`를 반환하면 fail 이유를 바로 대시보드에 올릴 수 있습니다.
- 길이 기준을 너무 빡빡하게 잡으면 좋은 응답도 버려집니다. 제품 문맥에 맞는 범위를 직접 정해야 합니다.

## 실무에서 헷갈리는 지점
![규칙 평가와 심판 모델이 층으로 쌓이는 구조](../../../assets/llm-apps-ops-101/03/03-03-where-engineers-get-confused.ko.png)

*규칙 평가와 심판 모델이 층으로 쌓이는 구조*
- 형식 검사가 통과했다고 품질이 좋은 것은 아닙니다. 반대로 형식 실패는 거의 항상 운영 실패입니다.
- 키워드 기반 평가는 도메인 용어가 분명할 때만 강력합니다. 창의적 글쓰기에는 맞지 않습니다.
- LLM-as-judge를 나중에 붙이더라도, 규칙 기반 평가층은 여전히 값싼 1차 방어선으로 남습니다.

## 체크리스트
- [ ] 모델에게 JSON only를 강제한다
- [ ] 길이 기준을 숫자로 명시한다
- [ ] expected_keywords를 테스트 케이스마다 정의한다
- [ ] 실패 시 missing_keywords를 함께 기록한다

## 정리
품질 평가는 거창한 점수 체계보다도, 명확한 실패를 얼마나 빨리 발견하느냐에서 운영 가치가 생깁니다.

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

- [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs)
- [JSON Schema](https://json-schema.org/)
- [G-Eval paper](https://arxiv.org/abs/2303.16634)

Tags: LLMOps, Observability, Python, LLM
