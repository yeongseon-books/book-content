---
title: 결정적 지표 — Exact Match, BLEU, ROUGE
series: ai-evaluation-101
episode: 3
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
- Metrics
- BLEU
last_reviewed: '2026-05-03'
seo_description: 결정적 지표는 빠르고 재현 가능하지만, 의미가 같아도 표현이 다르면 점수가 깎입니다.
---

# 결정적 지표 — Exact Match, BLEU, ROUGE

> AI Evaluation 101 시리즈 (3/10)

결정적 지표는 빠르고 재현 가능하지만, 의미가 같아도 표현이 다르면 점수가 깎입니다. 이 글은 Exact Match, F1, BLEU, ROUGE를 언제 써야 하고 언제 쓰면 안 되는지를 다룹니다.

---
![결정적 지표 - Exact Match, BLEU, ROUGE](../../../assets/ai-evaluation-101/03/03-01-deterministic-metrics-exact-match-bleu-r.ko.png)

*결정적 지표 - Exact Match, BLEU, ROUGE*
## 결정적 지표가 무엇인가요?

![결정적 지표가 무엇인가요](../../../assets/ai-evaluation-101/03/03-02-what-are-deterministic-metrics.ko.png)

*결정적 지표가 무엇인가요*
결정적 지표는 같은 입력과 같은 답이 주어지면 항상 같은 점수를 내는 지표입니다. LLM 호출 없이 문자열·토큰만 비교해서 계산하므로 빠르고 재현 가능합니다.

```python
def exact_match(pred: str, expected: str) -> int:
    return int(pred.strip() == expected.strip())

assert exact_match("Seoul", "Seoul") == 1
assert exact_match("Seoul.", "Seoul") == 0  # 점 하나 차이로 0점
```

빠르다는 장점 뒤에는 큰 약점이 있습니다. "의미는 같지만 표현이 다른" 답이 모두 0점으로 깎입니다. 이 글에서는 4가지 결정적 지표를 다루고, 각각이 언제 쓸 만하고 언제 쓰면 안 되는지를 설명합니다.

## Exact Match — 가장 단순한 지표

![Exact Match - 가장 단순한 지표](../../../assets/ai-evaluation-101/03/03-03-exact-match-the-simplest-metric.ko.png)

*Exact Match - 가장 단순한 지표*
질문: "한국의 수도는?"
정답: "서울"
모델 응답: "한국의 수도는 서울입니다."

Exact match로는 0점입니다. 정답이 한 단어로 정해져 있을 때만 의미가 있습니다.

```python
def exact_match_normalized(pred: str, expected: str) -> int:
    def normalize(s: str) -> str:
        return s.lower().strip().rstrip(".!?")
    return int(normalize(pred) == normalize(expected))
```

Normalization을 추가하면 조금 나아지지만, 본질적으로는 "정답이 1-2 단어로 고정된 QA"에서만 신뢰할 수 있습니다. SQuAD 같은 짧은 답 추출 task에 적합합니다.

## Token-level F1 — Exact Match보다 유연한 비교

![Token-level F1 - Exact Match보다 유연한 비교](../../../assets/ai-evaluation-101/03/03-04-token-level-f1-more-forgiving-than-exact.ko.png)

*Token-level F1 - Exact Match보다 유연한 비교*
F1은 예측과 정답을 토큰 집합으로 보고 정밀도(precision)와 재현율(recall)의 조화 평균을 계산합니다.

```python
from collections import Counter

def token_f1(pred: str, expected: str) -> float:
    pred_tokens = Counter(pred.lower().split())
    exp_tokens = Counter(expected.lower().split())
    common = pred_tokens & exp_tokens
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / sum(pred_tokens.values())
    recall = num_same / sum(exp_tokens.values())
    return 2 * precision * recall / (precision + recall)

print(token_f1("the capital is Seoul", "Seoul"))   # ~0.4 — 부분 점수
print(token_f1("Seoul", "Seoul"))                  # 1.0
```

"한국의 수도는 서울입니다" vs "서울" 같은 케이스에서 부분 점수를 줍니다. 하지만 단어 순서나 어순 변화는 잡지 못합니다. "Seoul is the capital"과 "the capital is Seoul"이 같은 점수를 받습니다.

## BLEU — 기계 번역에서 온 n-gram 중첩 지표

![BLEU - 기계 번역에서 온 n-gram 중첩 지표](../../../assets/ai-evaluation-101/03/03-05-bleu-n-gram-overlap-from-machine-transla.ko.png)

*BLEU - 기계 번역에서 온 n-gram 중첩 지표*
BLEU는 1-gram, 2-gram, 3-gram, 4-gram의 중첩 비율을 계산합니다. 기계 번역 평가에서 표준이지만, LLM 자유 형식 응답에는 한계가 큽니다.

```python
# pip install nltk
from nltk.translate.bleu_score import sentence_bleu

reference = [["the", "cat", "sat", "on", "the", "mat"]]
candidate1 = ["the", "cat", "sat", "on", "the", "mat"]
candidate2 = ["a", "cat", "is", "sitting", "on", "a", "mat"]

print(sentence_bleu(reference, candidate1))  # 1.0
print(sentence_bleu(reference, candidate2))  # ~0.0 — 의미는 같지만 점수 0
```

BLEU의 약점:

1. **동의어를 모릅니다**: "car"와 "automobile"은 다른 토큰입니다.
2. **어순에 민감합니다**: 같은 의미라도 어순이 다르면 깎입니다.
3. **참조 답이 여러 개여야 합니다**: 답이 한 개면 점수가 부풀려지거나 깎입니다.

BLEU는 "여러 개의 참조 번역이 있는 기계 번역" 평가에는 유효하지만, "자유 형식 chatbot 답변" 평가에는 부적합합니다.

## ROUGE — 요약 평가에서 온 recall 기반 지표

ROUGE는 BLEU와 비슷하지만 recall 중심입니다. 특히 ROUGE-L은 longest common subsequence를 사용해 어순 일부 변화에 덜 민감합니다.

```python
# pip install rouge-score
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
scores = scorer.score(
    "The cat sat on the mat",                    # reference
    "A cat is sitting on a mat",                 # prediction
)
print(scores["rouge1"].fmeasure)  # ~0.5
print(scores["rougeL"].fmeasure)  # ~0.5
```

ROUGE는 요약 task에서는 사람 평가와의 상관이 BLEU보다 높지만, 여전히 "사실이 틀렸는데 단어가 비슷하면 높은 점수"를 받는 약점이 있습니다.

## 결정적 지표를 언제 쓰고 언제 쓰면 안 되나요?

| 상황 | 적합한 지표 | 비고 |
|------|------------|------|
| 짧은 추출형 QA (SQuAD 형식) | Exact Match, Token F1 | 정답이 명확할 때 |
| Code generation | Exact Match (정규화 후) + 실행 테스트 | 컴파일·테스트가 ground truth |
| Classification (intent, sentiment) | Exact Match, Accuracy, F1 | 라벨 집합이 닫혀 있을 때 |
| 요약 (단일 reference) | ROUGE (참고만) + LLM-as-judge | ROUGE는 보조 지표로만 |
| 자유 형식 답변 (chatbot) | 결정적 지표 부적합 | LLM-as-judge / rubric 사용 |
| 기계 번역 (다중 reference) | BLEU, chrF | 참조가 여러 개일 때만 의미 있음 |

핵심 규칙: **답이 닫혀 있고 짧으면 결정적 지표가 잘 작동합니다. 답이 자유 형식이고 길면 LLM-as-judge나 rubric으로 가야 합니다.**

## 흔한 실수 5가지

1. **자유 형식 답변에 BLEU 사용**: 의미는 맞지만 표현이 다른 답이 모두 0점이 됩니다. 결과만 보면 "모델이 형편없다"는 잘못된 결론에 도달합니다.
2. **단일 reference로 ROUGE 평가**: ROUGE는 reference가 여럿일 때 의미가 있습니다. 하나만 있으면 paraphrase에 너무 가혹합니다.
3. **Normalization 안 함**: "Seoul"과 "seoul.", "Seoul " 모두 다른 답으로 처리됩니다. lowercase, strip, 마침표 제거를 기본으로 적용하세요.
4. **점수만 보고 케이스를 안 봄**: 평균 0.7이 나와도 어떤 케이스에서 깎였는지 보지 않으면 개선이 불가능합니다. 항상 최저 5건은 직접 읽으세요.
5. **결정적 지표 하나에만 의존**: BLEU 0.5와 ROUGE 0.5가 같이 떨어졌어도 사람 평가는 좋아질 수 있습니다. 항상 LLM-as-judge나 사람 spot check와 병행하세요.

## 핵심 요약

- 결정적 지표는 빠르고 재현 가능하지만 "의미는 같고 표현이 다른" 답을 깎는 약점이 있습니다.
- Exact Match와 Token F1은 짧은 추출형 QA에 적합합니다.
- BLEU는 다중 reference 기계 번역에서만, ROUGE는 요약의 보조 지표로 쓰세요.
- 자유 형식 chatbot 응답에는 결정적 지표가 부적합합니다 — LLM-as-judge로 가세요.
- 결정적 지표 하나에만 의존하지 말고 LLM-as-judge나 사람 spot check와 항상 병행하세요.

다음 글에서는 LLM-as-judge — 강력한 LLM에게 채점을 맡기는 방법, judge prompt 설계, bias 통제, 사람 평가와의 일치도 측정을 다룹니다.

---

<!-- toc:begin -->
## AI Evaluation 101 시리즈

- [왜 LLM 애플리케이션을 평가해야 하는가](./01-why-evaluate-llm-apps.md)
- [평가 데이터셋 설계하기](./02-evaluation-dataset-design.md)
- **결정적 지표 — Exact Match, BLEU, ROUGE (현재 글)**
- LLM-as-Judge (예정)
- Rubric 기반 채점 설계 (예정)
- RAG 시스템 평가하기 (예정)
- Agent 평가하기 (예정)
- 회귀 테스트 (예정)
- LLM A/B 테스팅 (예정)
- 운영 환경에서의 지속적 평가 (예정)
<!-- toc:end -->

## 참고 자료

- [Hugging Face — A guide to LLM evaluation](https://huggingface.co/docs/evaluate/index)
- [Papineni et al. — BLEU paper](https://aclanthology.org/P02-1040/)
- [Lin — ROUGE paper](https://aclanthology.org/W04-1013/)
- [SQuAD — Exact Match and F1](https://rajpurkar.github.io/SQuAD-explorer/)

Tags: AI Evaluation, LLM, Metrics, BLEU
