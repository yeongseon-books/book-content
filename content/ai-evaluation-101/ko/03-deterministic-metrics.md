---
series: ai-evaluation-101
episode: 3
title: "AI Evaluation 101 (3/10): 결정적 지표"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - ExactMatch
  - BLEU
  - ROUGE
  - TokenF1
  - Metrics
seo_description: Exact Match, Token F1, BLEU, ROUGE 등 결정적 LLM 평가 지표의 특성과 적합한 사용 상황을 정리합니다
last_reviewed: '2026-06-20'
---

# AI Evaluation 101 (3/10): 결정적 지표

LLM 출력을 측정하는 가장 단순한 방법은 정답과 직접 비교하는 것입니다. Exact Match, Token F1, BLEU, ROUGE는 이런 결정적(deterministic) 지표들입니다. LLM이나 사람의 판단 없이 계산할 수 있어 빠르고 재현 가능하지만, 표현이 다른 동의어나 자연스러운 언어 변형에는 취약합니다. 각 지표의 특성을 이해하고 적절한 상황에 사용하는 것이 중요합니다.

이 글은 AI Evaluation 101 시리즈의 3번째 글입니다.

![결정적 지표 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/03/03-01-concept-at-a-glance.ko.png)
*결정적 평가 지표의 특성과 적합 상황 비교*

## 이 글에서 다룰 문제

- Exact Match가 높은데 실제 품질이 낮을 수 있는 이유는 무엇일까요?
- Token F1은 어떤 상황에서 Exact Match보다 더 적합할까요?
- BLEU와 ROUGE의 핵심 차이는 무엇이고, 각각 어디에 써야 할까요?
- 결정적 지표의 한계를 보완하려면 어떤 접근이 필요할까요?
- 여러 지표를 조합해 종합 평가 점수를 만들 때 주의할 점은 무엇일까요?

## 핵심 개념 한 줄 정리

- **Exact Match (EM)**: 예측이 정답과 완전히 일치할 때만 1점을 주는 가장 엄격한 지표입니다.
- **Token F1**: 토큰 수준에서 정밀도와 재현율의 조화평균으로, 부분 일치를 인정합니다.
- **BLEU**: 예측에서 정답의 n-gram이 얼마나 많이 나타나는지 측정하는 번역 평가 지표입니다.
- **ROUGE**: 정답에서 예측의 n-gram이 얼마나 많이 나타나는지 측정하는 요약 평가 지표입니다.
- **N-gram**: 연속된 N개의 토큰 시퀀스입니다.

## 지표 특성 비교

| 지표 | 방향 | 부분 일치 | 적합 상황 | 한계 |
|---|---|---|---|---|
| Exact Match | 완전 일치 | 없음 | 분류, 짧은 QA | 표현 변형에 취약 |
| Token F1 | 단어 레벨 | 있음 | QA, 정보 추출 | 어순 무시 |
| BLEU | 예측 → 정답 | n-gram | 번역 | 재현율 무시 |
| ROUGE-1 | 정답 → 예측 | 단어 | 요약 | 유창성 무시 |
| ROUGE-L | 정답 → 예측 | LCS | 요약 | 계산 비용 |

## 실습 1: Exact Match 구현

```python
import re
from typing import Callable


def normalize_text(text: str) -> str:
    """텍스트를 정규화합니다 (소문자, 공백 정리, 특수문자 제거)."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def exact_match(
    prediction: str,
    reference: str,
    normalize: bool = True,
) -> float:
    """정확 일치 점수를 계산합니다."""
    if normalize:
        prediction = normalize_text(prediction)
        reference = normalize_text(reference)
    return 1.0 if prediction == reference else 0.0


def exact_match_score(
    predictions: list[str],
    references: list[str],
    normalize: bool = True,
) -> dict:
    """여러 케이스에 대한 Exact Match 점수를 계산합니다."""
    if len(predictions) != len(references):
        raise ValueError("예측과 정답의 수가 다릅니다.")

    scores = [
        exact_match(p, r, normalize)
        for p, r in zip(predictions, references)
    ]

    return {
        "exact_match": sum(scores) / len(scores),
        "total": len(scores),
        "correct": int(sum(scores)),
        "scores": scores,
    }


# 분류 문제 예시
predictions = ["긍정", "부정", "중립", "긍정"]
references = ["긍정", "부정", "부정", "긍정"]  # 3번째 케이스 오류

result = exact_match_score(predictions, references)
print(f"Exact Match: {result['exact_match']:.1%} ({result['correct']}/{result['total']})")
```

## 실습 2: Token F1

```python
from collections import Counter


def token_f1(prediction: str, reference: str) -> float:
    """토큰 수준 F1 점수를 계산합니다."""
    pred_tokens = normalize_text(prediction).split()
    ref_tokens = normalize_text(reference).split()

    if not pred_tokens or not ref_tokens:
        return 0.0 if (pred_tokens or ref_tokens) else 1.0

    pred_counter = Counter(pred_tokens)
    ref_counter = Counter(ref_tokens)

    # 공통 토큰 수
    common = sum((pred_counter & ref_counter).values())

    if common == 0:
        return 0.0

    precision = common / len(pred_tokens)
    recall = common / len(ref_tokens)
    f1 = 2 * precision * recall / (precision + recall)

    return f1


def token_f1_score(
    predictions: list[str],
    references: list[str],
) -> dict:
    """여러 케이스의 Token F1 점수를 계산합니다."""
    scores = [token_f1(p, r) for p, r in zip(predictions, references)]
    return {
        "token_f1": sum(scores) / len(scores),
        "scores": scores,
    }


# QA 예시: 정답과 일부 일치하는 경우
qa_predictions = [
    "파이썬은 인터프리터 언어입니다",
    "머신러닝은 데이터로 학습하는 알고리즘입니다",
    "REST API는 HTTP를 사용합니다",
]
qa_references = [
    "파이썬은 객체지향 인터프리터 언어입니다",
    "머신러닝은 데이터에서 패턴을 학습하는 알고리즘입니다",
    "REST API는 HTTP 프로토콜을 기반으로 합니다",
]

f1_result = token_f1_score(qa_predictions, qa_references)
print(f"Token F1: {f1_result['token_f1']:.3f}")
for i, score in enumerate(f1_result["scores"]):
    print(f"  케이스 {i+1}: {score:.3f}")
```

## 실습 3: ROUGE 점수

```python
def get_ngrams(tokens: list[str], n: int) -> Counter:
    """n-gram Counter를 반환합니다."""
    return Counter(tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1))


def rouge_n(prediction: str, reference: str, n: int = 1) -> dict:
    """ROUGE-N 점수를 계산합니다."""
    pred_tokens = normalize_text(prediction).split()
    ref_tokens = normalize_text(reference).split()

    pred_ngrams = get_ngrams(pred_tokens, n)
    ref_ngrams = get_ngrams(ref_tokens, n)

    common = sum((pred_ngrams & ref_ngrams).values())
    pred_total = sum(pred_ngrams.values())
    ref_total = sum(ref_ngrams.values())

    precision = common / pred_total if pred_total > 0 else 0.0
    recall = common / ref_total if ref_total > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)

    return {"precision": precision, "recall": recall, "f1": f1}


def rouge_l(prediction: str, reference: str) -> dict:
    """ROUGE-L 점수를 계산합니다 (최장 공통 부분 수열 기반)."""
    pred_tokens = normalize_text(prediction).split()
    ref_tokens = normalize_text(reference).split()

    m, n = len(pred_tokens), len(ref_tokens)
    if m == 0 or n == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    # LCS 계산
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if pred_tokens[i-1] == ref_tokens[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    lcs = dp[m][n]
    precision = lcs / m
    recall = lcs / n
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)

    return {"precision": precision, "recall": recall, "f1": f1}


# 요약 평가 예시
summaries = [
    "딥러닝은 신경망을 사용한 머신러닝 기법입니다",
    "RAG는 검색 기반 답변 생성 방식입니다",
]
references = [
    "딥러닝은 다층 신경망 구조를 활용한 머신러닝의 한 분야입니다",
    "RAG는 외부 문서 검색 결과를 LLM 입력에 포함해 답변을 생성하는 방식입니다",
]

for pred, ref in zip(summaries, references):
    r1 = rouge_n(pred, ref, n=1)
    rl = rouge_l(pred, ref)
    print(f"예측: {pred[:40]}...")
    print(f"  ROUGE-1 F1: {r1['f1']:.3f}, ROUGE-L F1: {rl['f1']:.3f}")
```

## 실습 4: 종합 평가 스코어카드

```python
def compute_all_metrics(
    predictions: list[str],
    references: list[str],
) -> dict:
    """여러 지표를 한 번에 계산합니다."""
    em = exact_match_score(predictions, references)
    f1 = token_f1_score(predictions, references)

    rouge1_scores = [rouge_n(p, r, 1)["f1"] for p, r in zip(predictions, references)]
    rougel_scores = [rouge_l(p, r)["f1"] for p, r in zip(predictions, references)]

    return {
        "exact_match": em["exact_match"],
        "token_f1": f1["token_f1"],
        "rouge1_f1": sum(rouge1_scores) / len(rouge1_scores),
        "rougel_f1": sum(rougel_scores) / len(rougel_scores),
        "sample_count": len(predictions),
    }


# 종합 평가
all_preds = ["긍정 감성입니다", "부정 감성입니다"]
all_refs = ["긍정 감성입니다", "중립 감성입니다"]

scorecard = compute_all_metrics(all_preds, all_refs)
print("\n=== 평가 스코어카드 ===")
for metric, score in scorecard.items():
    if isinstance(score, float):
        print(f"  {metric}: {score:.3f}")
    else:
        print(f"  {metric}: {score}")
```

## 운영 체크리스트

- [ ] 분류 작업에는 Exact Match를 기본으로 사용합니다.
- [ ] QA나 정보 추출에는 Token F1을 함께 사용합니다.
- [ ] 요약 평가에는 ROUGE-1과 ROUGE-L을 함께 보고합니다.
- [ ] 결정적 지표만으로 부족할 때 LLM-as-Judge를 보완합니다.
- [ ] 지표 계산 전 텍스트 정규화를 일관되게 적용합니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 정규화 없이 EM 계산 | 대소문자 차이로 오답 처리 | 소문자 변환, 공백/특수문자 정리 후 비교 |
| BLEU/ROUGE를 QA에 사용 | 표현이 달라도 동의어는 낮은 점수 | QA에는 Token F1 또는 LLM-as-Judge 사용 |
| 단일 지표만 보고 | 지표 특성에 따른 편향 | 최소 2개 지표를 조합해 보고 |
| 짧은 응답에 ROUGE 적용 | 1-2 단어 응답에서 ROUGE 불안정 | 짧은 응답은 Exact Match 우선 |
| 한국어 형태소 무시 | "갑니다"와 "간다"가 다른 토큰으로 처리 | 형태소 분석기(KoNLPy 등) 적용 고려 |

## 처음 질문으로 돌아가기

- **Exact Match가 높은데 실제 품질이 낮을 수 있는 이유는 무엇일까요?**
  테스트 케이스가 너무 쉽거나, 정답 표현이 고정되어 있어 약간의 표현 차이도 오답으로 처리될 때 EM이 실제 품질을 반영하지 못합니다. 케이스 다양성을 높이고 Token F1을 함께 사용해야 합니다.

- **BLEU와 ROUGE의 핵심 차이는 무엇일까요?**
  BLEU는 "예측이 정답을 얼마나 잘 포함하는가"(정밀도 중심), ROUGE는 "정답이 예측에 얼마나 잘 포함되는가"(재현율 중심)입니다. 번역은 BLEU, 요약은 ROUGE가 더 적합합니다.

- **결정적 지표의 한계를 보완하려면 어떤 접근이 필요할까요?**
  의미적으로 동등한 표현을 다르게 채점하는 문제는 LLM-as-Judge나 BERTScore 같은 의미 기반 지표로 보완합니다. 다음 글에서 LLM-as-Judge 패턴을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가](./01-why-evaluate-llm-apps.md)
- [AI Evaluation 101 (2/10): 평가 데이터셋 설계하기](./02-evaluation-dataset-design.md)
- **AI Evaluation 101 (3/10): 결정적 지표 (현재 글)**
- [AI Evaluation 101 (4/10): LLM-as-Judge](./04-llm-as-judge.md)
- [AI Evaluation 101 (5/10): 루브릭 기반 채점](./05-rubric-based-scoring.md)
- [AI Evaluation 101 (6/10): RAG 평가](./06-rag-evaluation.md)
- [AI Evaluation 101 (7/10): 에이전트 평가](./07-agent-evaluation.md)
- [AI Evaluation 101 (8/10): 회귀 테스트](./08-regression-testing.md)
- [AI Evaluation 101 (9/10): A/B 테스트](./09-ab-testing-llms.md)
- [AI Evaluation 101 (10/10): 프로덕션 평가](./10-production-evaluation.md)

<!-- toc:end -->

## 참고 자료

- [Papineni et al. — BLEU: a Method for Automatic Evaluation of Machine Translation](https://aclanthology.org/P02-1040/)
- [Lin — ROUGE: A Package for Automatic Evaluation of Summaries](https://aclanthology.org/W04-1013/)
- [SQuAD — Exact Match and F1](https://rajpurkar.github.io/SQuAD-explorer/)
- [sacrebleu — Python BLEU Implementation](https://github.com/mjpost/sacrebleu)
- [book-examples — ai-evaluation-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-evaluation-101/ko)

Tags: ExactMatch, BLEU, ROUGE, TokenF1, Metrics
