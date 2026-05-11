---
title: 평가 데이터셋 설계하기
series: ai-evaluation-101
episode: 2
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- LLM
- Dataset
- Quality
last_reviewed: '2026-05-03'
seo_description: 좋은 평가 데이터셋은 production 트래픽의 분포를 닮으면서도 edge case를 충분히 포함해야 합니다.
---

# 평가 데이터셋 설계하기

> AI Evaluation 101 시리즈 (2/10)

좋은 평가 데이터셋은 production 트래픽의 분포를 닮으면서도 edge case를 충분히 포함해야 합니다. 이 글은 50-200건 규모의 입문용 eval set을 설계하는 원칙과 데이터를 모으는 방법을 다룹니다.

---
![평가 데이터셋 설계하기](../../assets/ai-evaluation-101/02/02-01-designing-evaluation-datasets.ko.png)

*평가 데이터셋 설계하기*

## 좋은 평가 데이터셋이란 무엇인가요?

![좋은 평가 데이터셋이란 무엇인가요](../../assets/ai-evaluation-101/02/02-02-what-makes-a-good-evaluation-dataset.ko.png)

*좋은 평가 데이터셋이란 무엇인가요*
좋은 eval set은 두 가지를 동시에 만족합니다.

1. **Production 트래픽의 분포를 닮습니다**: 사용자가 실제로 보내는 질문의 비율과 비슷해야 합니다.
2. **Edge case를 충분히 포함합니다**: 평소엔 드물지만 깨지면 큰 사고가 나는 케이스를 의도적으로 모아둡니다.

이 둘이 같이 있어야 "평균 점수는 좋은데 한 케이스에서 처참하게 깨지는" 상황을 잡을 수 있습니다.

```python
from dataclasses import dataclass

@dataclass
class EvalExample:
    id: str
    input: dict
    expected: dict | None       # 결정적 답이 있을 때만 채움
    category: str               # "happy_path", "edge_case", "adversarial" 중 하나
    notes: str = ""
```

`category`를 명시적으로 붙이면 "edge case 점수만 따로 보기"가 가능해집니다. 평균만 보면 다수 케이스가 묻어 가립니다.

## 어디서 데이터를 가져오나요?

![어디서 데이터를 가져오나요](../../assets/ai-evaluation-101/02/02-03-where-do-you-source-the-data.ko.png)

*어디서 데이터를 가져오나요*
3가지 출처를 조합합니다.

### 1. Production trace에서 샘플링

가장 좋은 출처는 실제 사용자 입력입니다. 매주 production log에서 무작위 50건을 추출해 eval set 후보로 모읍니다.

```python
import random

def sample_from_production(traces: list[dict], n: int = 50) -> list[dict]:
    return random.sample(traces, min(n, len(traces)))
```

PII가 들어 있다면 마스킹하거나 합성 데이터로 변환합니다 (Ep9 Observability 참조).

### 2. 실패 케이스 모으기

사용자 불만, on-call에서 잡힌 사고, 내부 dogfooding에서 깨진 케이스를 모두 eval set에 넣습니다. "한 번 깨진 건 다시 깨지지 않게 하는" 회귀 테스트의 시작입니다.

```python
def add_failure_case(eval_set: list[dict], failed_input: dict, expected: dict, source: str):
    eval_set.append({
        "id": f"regression-{len(eval_set)+1:04d}",
        "input": failed_input,
        "expected": expected,
        "category": "regression",
        "notes": f"From: {source}",
    })
```

### 3. 의도적으로 만든 adversarial 케이스

도메인 지식을 가진 사람이 "이건 깨질 것 같다"고 손으로 만든 케이스입니다. Prompt injection, 모호한 질문, 답이 없는 질문 등이 여기 들어갑니다.

## 몇 건이 필요한가요?

![몇 건이 필요한가요](../../assets/ai-evaluation-101/02/02-04-how-many-cases-do-you-need.ko.png)

*몇 건이 필요한가요*
크기는 목적에 따라 다릅니다.

| 목적 | 권장 크기 | 비고 |
|------|----------|------|
| Smoke test (CI에서 매 PR마다) | 10-30 | 빠르게 돌고, 명백한 회귀만 잡습니다 |
| 회귀 테스트 (배포 전) | 100-300 | 차원별로 의미 있는 점수를 냅니다 |
| 모델 비교 (gpt-4o vs claude) | 300-1000 | 통계적으로 유의미한 결론이 가능합니다 |
| 학술 벤치마크 | 1000+ | 일반화 가능성 주장에 필요합니다 |

처음에는 10-30건으로 시작하고, 매주 production trace에서 5-10건씩 추가하면 3개월 안에 200건에 도달합니다.

## 라벨링 — `expected`를 어떻게 채우나요?

![라벨링 - expected 값 채우기](../../assets/ai-evaluation-101/02/02-05-labeling-how-do-you-fill-expected.ko.png)

*라벨링 - expected 값 채우기*
라벨링 방식은 3가지가 있고, 케이스마다 다른 방식을 쓸 수 있습니다.

```python
@dataclass
class Label:
    style: str  # "exact", "keywords", "rubric"
    payload: dict
```

1. **Exact answer**: "한국의 수도는?" → "서울". 정답이 하나뿐일 때 사용합니다.
2. **Required keywords**: 요약 결과에 반드시 들어가야 할 단어 리스트.
3. **Rubric**: 정답이 여럿일 때 "정확성 5점 만점 중 X점" 같은 차원별 점수 (Ep5에서 자세히 다룹니다).

```python
examples = [
    EvalExample(
        id="qa-001",
        input={"question": "What is the capital of Korea?"},
        expected={"style": "exact", "answer": "Seoul"},
        category="happy_path",
    ),
    EvalExample(
        id="summary-001",
        input={"text": "..."},
        expected={"style": "keywords", "must_include": ["microservice", "latency"]},
        category="happy_path",
    ),
    EvalExample(
        id="advice-001",
        input={"question": "How should I structure my React app?"},
        expected={"style": "rubric"},
        category="edge_case",
    ),
]
```

## Eval set을 어떻게 버전 관리하나요?

Eval set은 코드와 함께 버전 관리되어야 합니다. JSONL 파일로 저장하고 git에 커밋하세요.

```python
import json
from pathlib import Path

def save_eval_set(eval_set: list[EvalExample], path: Path):
    with path.open("w") as f:
        for ex in eval_set:
            f.write(json.dumps({
                "id": ex.id,
                "input": ex.input,
                "expected": ex.expected,
                "category": ex.category,
                "notes": ex.notes,
            }, ensure_ascii=False) + "\n")

def load_eval_set(path: Path) -> list[EvalExample]:
    with path.open() as f:
        return [EvalExample(**json.loads(line)) for line in f]
```

파일명에 버전을 박는 것도 좋은 습관입니다: `evals/customer-support/v3.jsonl`. 새 버전을 만들 때 옛 버전을 지우지 말고 이름을 늘리세요.

## 흔한 실수 5가지

1. **Eval set을 prompt 작성자가 만듦**: 자기 prompt에 유리한 케이스만 모이고, "잘된다"는 잘못된 결론이 나옵니다. 다른 팀원이나 production에서 가져오세요.
2. **Happy path만 모음**: edge case가 없으면 "평균 90%인데 1% 사용자가 망가지는" 상황을 못 잡습니다. category 비율을 의도적으로 관리하세요.
3. **PII를 그대로 저장**: 실제 사용자 데이터를 git에 커밋하면 큰 사고입니다. 라벨링 전에 마스킹하세요.
4. **`expected`를 한 가지 방식으로만 채움**: 모든 케이스에 exact match를 강제하면 자유 형식 답이 모두 0점이 됩니다. 케이스별로 적절한 라벨 스타일을 고르세요.
5. **Eval set을 한 번 만들고 안 갱신**: production 트래픽 분포가 바뀌면 옛 eval set은 의미가 없어집니다. 매주 5-10건씩 갱신하세요.

## 핵심 요약

- 좋은 eval set은 production 분포 + edge case를 함께 담습니다.
- 출처는 production trace 샘플링, 실패 케이스, 의도적 adversarial 3가지를 조합하세요.
- Smoke 10-30건, 회귀 100-300건, 모델 비교 300-1000건이 목표 크기입니다.
- 라벨은 exact, keywords, rubric 3가지 스타일을 케이스별로 골라 쓰세요.
- JSONL로 git에 커밋하고 파일명에 버전을 박으세요.

다음 글에서는 결정적 지표 — Exact Match, F1, BLEU, ROUGE를 언제 써야 하고 언제 쓰면 안 되는지를 다룹니다.
## 참고 자료

- [Hamel Husain — Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
- [OpenAI — Evals framework](https://github.com/openai/evals)
- [LangSmith — Dataset best practices](https://docs.smith.langchain.com/evaluation/concepts)
- [Eugene Yan — Building eval datasets](https://eugeneyan.com/writing/evals/)
