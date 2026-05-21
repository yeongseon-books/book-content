---
title: "AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가"
series: ai-evaluation-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- LLM
- Testing
- Quality
last_reviewed: '2026-05-14'
seo_description: LLM은 같은 입력에도 다른 답을 내놓습니다. 평가 없이 운영하면 어제 잘 되던 기능이 오늘 망가지는 것을 알 수 없습니다.
---

# AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가

LLM 기능을 처음 붙일 때 팀은 대개 응답 품질보다 기능 연결부터 끝내려 합니다. 데모 단계에서는 그 선택이 크게 문제처럼 보이지 않습니다. 질문을 넣었더니 답이 나오고, 화면에도 자연스럽게 붙기 때문입니다.

문제는 그다음부터입니다. 프롬프트를 한 줄 손보고, 모델 버전을 바꾸고, 검색 컨텍스트를 추가하는 순간 어제 잘 되던 사례가 오늘은 흔들리기 시작합니다. 그런데 일반 테스트만 돌리고 있으면 이 변화가 품질 개선인지, 조용한 회귀인지 팀이 구분하지 못합니다.

현업에서 저는 이 지점에서 두 종류의 팀을 봤습니다. 한쪽은 '답변이 좀 더 자연스러워진 것 같다'는 감각으로 계속 운영합니다. 다른 한쪽은 작은 평가셋이라도 만들어서 모델, 프롬프트, 정책 변경이 어떤 차이를 만드는지 기록합니다. 시간이 갈수록 후자의 팀이 훨씬 빠르게 안정화됩니다.

이 글은 AI Evaluation 101 시리즈의 첫 번째 글입니다.

여기서는 왜 LLM 평가가 일반 소프트웨어 테스트와 다른지, 무엇을 측정해야 하는지, 그리고 왜 10건짜리 작은 평가셋이라도 지금 바로 시작해야 하는지를 실무 관점에서 정리하겠습니다.


![LLM 애플리케이션 평가의 필요성](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-01-why-evaluate-llm-applications.ko.png)
*LLM 애플리케이션 평가의 필요성*
> LLM 평가는 테스트를 대체하는 장식이 아니라, 품질 변화를 계속 읽게 해 주는 계기판입니다.

## 먼저 던지는 질문

- LLM 앱은 왜 일반 기능 테스트만으로 품질을 판단하기 어려울까요?
- 평가를 붙이지 않고 운영하면 어떤 문제가 가장 늦게 드러날까요?
- 처음 평가 파이프라인은 어떤 작은 단위부터 시작해야 할까요?

## 왜 이 글이 중요한가

평가가 없는 LLM 서비스는 품질을 운영하는 것이 아니라 운에 맡기는 것에 가깝습니다. 기능이 살아 있다는 사실과 답변 품질이 유지된다는 사실은 전혀 다릅니다. 특히 프롬프트, 검색, 모델 공급사 업데이트가 모두 변수가 되는 시스템에서는 더 그렇습니다.

저는 팀이 평가 없이 출시한 뒤 사용자가 문제를 제보하면 그제야 '언제부터 망가졌지?'를 거꾸로 추적하는 장면을 자주 봤습니다. 이 방식은 느릴 뿐 아니라 학습도 남지 않습니다. 반대로 작은 평가셋이라도 있으면 변경 전후의 차이를 비교할 수 있고, 모델 업그레이드도 더 이상 감각의 문제가 아니게 됩니다.

결국 이 글의 핵심은 평가가 연구용 사치가 아니라 변경 관리의 기본 장치라는 점입니다. LLM을 운영하는 순간부터 팀은 답변 품질을 테스트 코드처럼 반복해서 확인할 수 있어야 합니다.

## 핵심 관점

이 주제는 개별 기법을 외우기보다 먼저 어떤 운영 문제를 풀기 위한 장치인지 붙잡아 두는 편이 이해가 빠릅니다. 평가가 없는 LLM 서비스는 품질을 운영하는 것이 아니라 운에 맡기는 것에 가깝습니다. 기능이 살아 있다는 사실과 답변 품질이 유지된다는 사실은 전혀 다릅니다. 특히 프롬프트, 검색, 모델 공급사 업데이트가 모두 변수가 되는 시스템에서는 더 그렇습니다.

> LLM 평가는 정답 하나를 맞히는 시험이 아닙니다. 같은 입력이 다른 답을 낳는 환경에서, 팀이 어떤 품질 축을 지키고 어떤 변화는 막아야 하는지를 숫자와 사례로 붙잡는 운영 장치입니다.

이 관점을 먼저 잡아 두면 뒤에 나오는 코드와 지표를 기능 설명이 아니라 운영 설계 관점에서 읽을 수 있습니다. 결국 중요한 것은 수치 이름보다, 그 수치가 어떤 의사결정을 가능하게 하느냐입니다.

## 핵심 개념

### LLM 평가는 왜 일반 테스트와 다른가요?

![LLM 평가와 일반 테스트의 차이](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-02-why-is-llm-evaluation-different-from-reg.ko.png)

*LLM 평가와 일반 테스트의 차이*
전통적인 단위 테스트는 `assert add(2, 3) == 5`처럼 결정적입니다. 같은 입력은 같은 출력을 내고, 정답이 하나입니다.

LLM은 다릅니다.

```python
from openai import OpenAI

client = OpenAI()

def summarize(text: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize in one sentence: {text}"}],
    )
    return resp.choices[0].message.content
```

같은 `text`를 두 번 넣어도 응답 두 줄이 정확히 일치하지 않습니다. "맞다"라고 부를 만한 답이 여러 개 있고, "틀렸다"고 단정하기 어려운 답도 많습니다. `==` 비교만으로는 평가가 불가능합니다.

### 평가 없이 운영하면 무엇이 깨지나요?

![평가 없이 운영하면 무엇이 깨지나요](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-03-what-breaks-if-you-run-without-evaluatio.ko.png)

*평가 없이 운영하면 무엇이 깨지나요*
세 가지가 동시에 깨집니다.

1. **회귀를 발견할 수 없습니다**: prompt를 한 줄 바꿨더니 다른 케이스가 깨졌는데, eval이 없으면 사용자가 알려줄 때까지 모릅니다.
2. **모델 업그레이드를 두려워하게 됩니다**: gpt-4o-mini → gpt-4.1로 바꾸려는데 "더 나은지" 측정할 방법이 없으면 그냥 안 바꾸게 됩니다.
3. **개선했다는 증거가 없습니다**: "이번 prompt가 더 좋아졌어요"라고 말해도 숫자가 없으면 이해관계자를 설득할 수 없습니다.

```python
# eval 없이 프롬프트를 바꿀 때의 모습
# 변경 전: "Summarize in one sentence:"
# 변경 후:  "Summarize concisely in one sentence in a friendly tone:"
# -> 어떤 케이스가 좋아지고 어떤 케이스가 나빠졌는지 알 수 없습니다.
```

### 무엇을 측정해야 하나요?

![무엇을 측정해야 하나요](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-04-what-should-you-measure.ko.png)

*무엇을 측정해야 하나요*
LLM 응답에는 최소 4가지 차원이 있고, 각각 다른 측정 방법이 필요합니다.

```python
from dataclasses import dataclass

@dataclass
class EvalResult:
    correctness: float  # are the facts right
    relevance: float    # does it answer the question
    safety: float       # any harm or bias
    style: float        # does it follow the requested format and tone
```

1. **Correctness (정확성)**: 사실이 맞는가. RAG에서는 retrieved context와 일치하는가.
2. **Relevance (관련성)**: 질문에 답하고 있는가, 아니면 빙빙 도는가.
3. **Safety (안전성)**: PII 유출, 차별 발언, 위험한 조언이 없는가.
4. **Style (문체/형식)**: JSON 스키마, 길이 제한, 톤을 지키는가.

이 시리즈에서는 각 차원에 어떤 지표가 적합한지를 이후 글에서 하나씩 다룹니다.

### 평가 파이프라인의 4단계

![평가 파이프라인의 4단계](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-05-the-four-stages-of-an-evaluation-pipelin.ko.png)

*평가 파이프라인의 4단계*
LLM 평가 시스템은 어떤 도구를 쓰든 동일한 4단계로 구성됩니다.

```python
def run_evaluation(eval_set: list[dict], system_under_test) -> dict:
    # 1. Generate — 테스트 대상 시스템에 입력을 넣고 응답을 수집
    predictions = [system_under_test(ex["input"]) for ex in eval_set]

    # 2. Score — 각 응답을 채점
    scores = [score_one(ex, pred) for ex, pred in zip(eval_set, predictions)]

    # 3. Aggregate — 점수를 집계
    summary = {
        "accuracy": sum(s["correct"] for s in scores) / len(scores),
        "avg_relevance": sum(s["relevance"] for s in scores) / len(scores),
    }

    # 4. Compare — 이전 버전과 비교
    return summary
```

1. **Generate**: eval set의 입력으로 시스템 응답을 생성합니다.
2. **Score**: 각 응답에 점수를 매깁니다 (결정적 지표, LLM-as-judge, 사람 평가 중 택1 또는 조합).
3. **Aggregate**: 차원별 평균, 통과율, p95 등으로 집계합니다.
4. **Compare**: 이전 버전 또는 baseline과 비교해서 회귀가 없는지 확인합니다.

### 첫 평가 — 10건이라도 시작하세요

"평가는 데이터가 충분히 모이면 시작하겠다"는 1년이 지나도 시작 못 합니다. 10건으로 시작하세요.

```python
eval_set = [
    {"input": "What is RAG?", "expected_keywords": ["retrieval", "generation"]},
    {"input": "Explain async/await", "expected_keywords": ["coroutine", "await"]},
    # ... 8 more
]

def score_one(ex, pred: str) -> dict:
    keywords_found = sum(1 for kw in ex["expected_keywords"] if kw.lower() in pred.lower())
    return {
        "correct": keywords_found == len(ex["expected_keywords"]),
        "keyword_recall": keywords_found / len(ex["expected_keywords"]),
    }

results = run_evaluation(eval_set, summarize)
print(f"Accuracy: {results['accuracy']:.0%}")
```

10건으로도 "5번 케이스에서 prompt 변경 후 점수가 떨어졌다"는 신호를 받을 수 있습니다. 이 신호 하나가 회귀의 90%를 잡습니다.

### 오늘 바로 돌릴 수 있는 최소 평가 하네스

첫 평가를 시작할 때는 거창한 플랫폼보다 작동하는 습관이 중요합니다. 시스템 호출 함수 하나, 작은 평가셋 하나, 실패 케이스를 그대로 보여 주는 출력만 있어도 운영 대화가 달라집니다.

```python
from dataclasses import dataclass

@dataclass
class EvalCase:
    case_id: str
    prompt: str
    must_include: list[str]

def run_smoke_eval(cases: list[EvalCase], system_under_test) -> dict:
    failed_cases = []
    scores = []

    for case in cases:
        answer = system_under_test(case.prompt)
        matched = sum(1 for kw in case.must_include if kw.lower() in answer.lower())
        passed = matched == len(case.must_include)
        scores.append(int(passed))

        if not passed:
            failed_cases.append(
                {
                    "case_id": case.case_id,
                    "answer": answer,
                    "missing": [kw for kw in case.must_include if kw.lower() not in answer.lower()],
                }
            )

    return {
        "pass_rate": sum(scores) / len(scores),
        "failed_cases": failed_cases,
    }

smoke_cases = [
    EvalCase("rag-001", "What is RAG?", ["retrieval", "generation"]),
    EvalCase("async-001", "Explain async/await", ["coroutine", "await"]),
    EvalCase("json-001", "Return valid JSON with a title field", ["title"]),
]

report = run_smoke_eval(smoke_cases, summarize)
print(report)
```

**예상 출력:**

```text
{
  'pass_rate': 0.67,
  'failed_cases': [
    {
      'case_id': 'async-001',
      'answer': '...',
      'missing': ['coroutine']
    }
  ]
}
```

이 정도 출력만 있어도 PR 리뷰가 훨씬 실용적으로 바뀝니다. "이번 응답이 더 자연스러워 보인다"가 아니라 "async-001에서 회귀가 생겼다"처럼 케이스 단위로 대화할 수 있기 때문입니다.

### 첫 주에 가장 자주 터지는 실패 양상

| 실패 양상 | 겉으로 보이는 증상 | 바로 취할 조치 |
|---|---|---|
| 보기 좋은 happy path만 넣음 | 평균 점수는 높지만 운영 불만이 계속 나옴 | 최근 사용자 불만 2~3건을 매주 추가 |
| 평균 점수 하나만 봄 | 정확성은 올랐는데 안전성·형식 준수가 떨어져도 못 봄 | correctness, relevance, safety, style를 분리 |
| 케이스 diff를 안 남김 | 점수 하락은 보이는데 왜 떨어졌는지 모름 | failed case id, 원문 답변, 누락 키워드 출력 |
| 수동 실행에만 의존 | "작은 prompt 수정이라 괜찮겠지" 하고 평가를 건너뜀 | smoke eval을 PR 검토나 CI에 연결 |

첫 하네스의 목표는 우아함이 아닙니다. 사용자 제보보다 먼저 회귀를 드러내는 속도입니다.

### 팀이 바로 적용할 수 있는 최소 CI 평가 파이프라인

평가가 문서로만 남으면 한 달 안에 무너집니다. 실제로는 PR마다 같은 조건으로 반복 실행되게 만들어야 합니다. 아래 예시는 가장 작은 형태의 GitHub Actions 기반 평가 파이프라인입니다.

```yaml
# .github/workflows/llm-eval-smoke.yml
name: LLM Eval Smoke

on:
  pull_request:
    paths:
      - "src/**"
      - "prompts/**"
      - "evals/**"

jobs:
  smoke-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - name: Run smoke evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python -m evals.smoke.run --input evals/smoke.jsonl --output evals/result.json
      - name: Enforce gate
        run: python -m evals.smoke.gate --report evals/result.json --min-pass-rate 0.8
```

```python
# evals/smoke/gate.py
import json
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--min-pass-rate", type=float, required=True)
    args = parser.parse_args()

    with open(args.report) as f:
        report = json.load(f)

    pass_rate = report["pass_rate"]
    if pass_rate < args.min_pass_rate:
        print(f"FAIL: pass_rate={pass_rate:.2%} < {args.min_pass_rate:.2%}")
        for case in report.get("failed_cases", []):
            print(f"- {case['case_id']}: missing={case.get('missing', [])}")
        sys.exit(1)

    print(f"PASS: pass_rate={pass_rate:.2%}")

if __name__ == "__main__":
    main()
```

핵심은 화려한 대시보드가 아니라, PR 단계에서 품질 저하를 자동으로 막는 기준선을 만드는 일입니다.

### 4주 도입 로드맵

평가를 처음 도입하는 팀은 도구 선택보다 도입 순서가 더 중요합니다. 아래처럼 4주 단위로 범위를 제한하면 "하네스는 만들었지만 아무도 안 돌리는" 상태를 피하기 쉽습니다.

| 주차 | 목표 | 산출물 |
|---|---|---|
| 1주차 | 10~20건 smoke eval 구축 | `evals/smoke.jsonl`, pass/fail 스크립트 |
| 2주차 | 차원 분리 점수 도입 | correctness/relevance 분리 리포트 |
| 3주차 | PR 자동 게이트 연결 | GitHub Actions fail gate |
| 4주차 | 실패 환류 루프 시작 | 주간 실패 케이스 추가 규칙 |

```python
def weekly_eval_review(summary: dict) -> list[str]:
    actions = []
    if summary["pass_rate"] < 0.8:
        actions.append("핵심 프롬프트 변경 롤백 검토")
    if summary.get("safety_failures", 0) > 0:
        actions.append("safety 케이스를 golden set으로 승격")
    if summary.get("flaky_cases", 0) > 3:
        actions.append("비결정성 높은 케이스를 분리 분석")
    return actions
```

이 로드맵의 목적은 완성도가 아니라 반복성입니다. 작게 시작해도 매주 계속 돌면 품질 운영 능력은 빠르게 올라갑니다.

평가를 도입하는 가장 좋은 순간은 완벽해졌을 때가 아니라, 변경이 잦아지기 시작했을 때입니다.

작은 평가 루프라도 팀의 변경 속도를 늦추지 않으면서 품질 사고를 줄이는 효과가 분명히 나타납니다.

## 이 코드에서 먼저 봐야 할 점

- `EvalResult`처럼 품질 차원을 구조체로 나누는 부분부터 보시면 좋습니다. 이 시점부터 팀의 대화가 '좋아졌다'가 아니라 '정확성은 올랐고 안전성은 유지됐다'로 바뀝니다.
- `run_evaluation` 예제는 어떤 도구를 쓰든 평가 파이프라인이 생성 → 채점 → 집계 → 비교라는 네 단계로 반복된다는 점을 보여 줍니다.
- 마지막 10건짜리 예제는 규모보다 습관이 중요하다는 메시지입니다. 작은 평가라도 있으면 프롬프트 변경 직후 회귀를 바로 잡을 수 있습니다.

이 세 지점을 먼저 읽고 나면 세부 구현과 지표 해석이 훨씬 빨라집니다. 코드가 길어 보여도 운영 질문은 대개 여기로 다시 돌아옵니다.

## 어디서 자주 헷갈릴까요?

1. **production이 안정되면 평가하겠다**: 평가가 없으면 안정되었는지를 알 수 없습니다. 첫날부터 10건으로 시작하세요.
2. **단일 점수에 집착**: "정확도 87%"만 보면 안전성이 떨어진 걸 놓칩니다. 항상 차원별로 보세요.
3. **eval set을 prompt 작성자가 직접 만듦**: 자기가 만든 prompt에 유리한 케이스만 골라 측정 결과가 부풀려집니다. 다른 사람 또는 production trace에서 가져오세요.
4. **결정적 지표만 사용**: BLEU만 보면 "의미는 맞지만 표현이 다른" 답이 모두 깎입니다. LLM-as-judge나 rubric 평가를 함께 쓰세요.
5. **평가를 한 번만 돌림**: LLM은 stochastic이라 같은 입력에도 점수가 달라질 수 있습니다. 중요한 비교는 3-5회 반복해서 분산을 함께 보세요.

현업에서 제가 가장 자주 보는 문제는 결과 숫자만 보고 원인 분해를 건너뛰는 습관입니다. 평가가 개선을 돕지 못하고 보고서용 숫자로만 남는 순간, 팀은 다시 감각에 의존하게 됩니다.

## 첫 번째 운영 체크리스트

- [ ] 현재 운영 중인 핵심 사용자 질문 10건을 바로 뽑을 수 있는가
- [ ] 정확성, 관련성, 안전성, 형식 가운데 무엇을 먼저 지킬지 합의했는가
- [ ] 프롬프트나 모델 변경 전후를 비교할 기준선이 있는가
- [ ] 변경 후 품질 저하를 사용자 제보보다 먼저 감지할 수 있는가
- [ ] 평가 결과를 숫자와 사례로 팀에 공유하는 흐름이 있는가

## 실무에서는 이렇게 생각한다

실무에서는 '평가를 언제 붙일까'보다 '평가 없이 무엇을 바꿀 수 있나'를 먼저 묻는 편이 더 맞습니다. 대부분의 경우 답은 거의 없습니다. 모델이나 프롬프트를 건드리는 순간 품질이 움직이기 때문입니다.

강한 팀들은 첫 평가가 완벽하길 바라지 않습니다. 대신 아주 작은 셋이라도 먼저 만들고, 운영 중 생긴 실패 사례를 계속 추가합니다. 이렇게 쌓인 평가셋이 나중에는 프롬프트 자산보다 더 중요한 운영 자산이 됩니다.

이 시리즈의 다음 글들이 모두 여기서 출발합니다. 어떤 데이터셋을 만들고, 어떤 지표를 고르고, 어떤 비교를 해야 하는지도 결국 '왜 평가가 필요한가'를 명확히 이해해야 흔들리지 않습니다.

## 정리: 평가를 붙인 순간부터 LLM 기능은 제품이 아니라 시스템이 됩니다

- LLM 응답은 결정적이지 않으므로 `==` 비교가 불가능합니다.
- 평가 없이 운영하면 회귀, 모델 업그레이드, 개선 증명 모두 불가능해집니다.
- 최소 4가지 차원(correctness, relevance, safety, style)을 별도로 측정하세요.
- 평가 파이프라인은 generate → score → aggregate → compare 4단계입니다.
- 데이터를 모을 때까지 기다리지 말고 10건으로라도 오늘 시작하세요.

다음 글에서는 이 출발점을 실제 평가 데이터셋 설계로 연결합니다. 어떤 사례를 모아야 하고, 얼마나 모아야 하며, 어떤 라벨을 붙여야 하는지부터 잡아야 이후의 모든 지표가 의미를 갖습니다.

## 운영 체크리스트

- [ ] 평가 없는 프롬프트 변경을 기본적으로 위험 변경으로 취급하기
- [ ] 정확성 외 최소 한 개 이상의 보조 품질 축을 함께 측정하기
- [ ] 작더라도 반복 가능한 평가셋을 버전 관리에 넣기
- [ ] 모델 변경 시 체감이 아니라 비교 결과로 의사결정하기
- [ ] 사용자 불만이 아니라 평가 결과가 먼저 경보를 울리게 만들기

## 처음 질문으로 돌아가기

- **LLM 앱은 왜 일반 기능 테스트만으로 품질을 판단하기 어려울까요?**
  - LLM 출력은 표현이 달라도 맞을 수 있고, 그럴듯해 보여도 틀릴 수 있어 단순 assert만으로 의미 품질을 잡기 어렵습니다.
- **평가를 붙이지 않고 운영하면 어떤 문제가 가장 늦게 드러날까요?**
  - 비용 증가, 특정 케이스 퇴행, hallucination, safety miss처럼 최종 사용자나 운영 지표에 쌓인 뒤에야 보이는 문제가 늦게 드러납니다.
- **처음 평가 파이프라인은 어떤 작은 단위부터 시작해야 할까요?**
  - 대표 요청 10개 정도의 작은 eval set과 명확한 expected 기준, 실패 로그부터 시작해 반복 가능한 평가 루프를 만듭니다.
<!-- toc:begin -->
## 시리즈 목차

- **AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가 (현재 글)**
- AI Evaluation 101 (2/10): 평가 데이터셋 설계하기 (예정)
- AI Evaluation 101 (3/10): 결정적 지표 — Exact Match, BLEU, ROUGE (예정)
- AI Evaluation 101 (4/10): LLM-as-Judge — 모델로 모델을 평가하기 (예정)
- AI Evaluation 101 (5/10): Rubric 기반 채점 설계 (예정)
- AI Evaluation 101 (6/10): RAG 시스템 평가하기 (예정)
- AI Evaluation 101 (7/10): 에이전트 평가하기 — 단일 응답이 아닌 trajectory (예정)
- AI Evaluation 101 (8/10): 회귀 테스트 — 어제 잘 되던 게 오늘 망가지지 않게 (예정)
- AI Evaluation 101 (9/10): LLM A/B 테스팅 — 어느 prompt가 더 나은가 (예정)
- AI Evaluation 101 (10/10): 운영 환경에서의 지속적 평가 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OpenAI — Evals framework](https://github.com/openai/evals)
- [Anthropic — Building evals](https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests)
- [Hugging Face — Evaluating LLMs](https://huggingface.co/learn/cookbook/en/llm_judge)
- [Eugene Yan — LLM evaluation patterns](https://eugeneyan.com/writing/llm-evaluators/)

### 관련 시리즈

- [다음 글 — 평가 데이터셋 설계하기](./02-evaluation-dataset-design.md)
- [시리즈 현재 위치 다시 보기](./01-why-evaluate-llm-apps.md)
- [LLM Apps Ops 101](../../llm-apps-ops-101/ko/01-monitoring-and-logging.md) — 같은 "LLM 정확성" 문제를 운영 단계에서 다룹니다. 이 시리즈가 릴리스 전 게이트를 만든다면, ops 시리즈는 릴리스 후에 모니터링·로깅·알림으로 같은 신호를 추적합니다.

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-evaluation-101/ko/01-why-evaluate-llm-apps)

Tags: AI Evaluation, LLM, Testing, Quality
