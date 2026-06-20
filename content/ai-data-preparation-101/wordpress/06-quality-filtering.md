---
title: "바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링"
series: ai-data-preparation-101
episode: 6
language: ko
tags:
- Quality Filtering
- Heuristic Rules
- Perplexity Filter
- fastText
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 여섯 번째 글입니다.

---

바이브코딩으로 데이터를 정제하고 중복을 제거했는데도 "이 데이터가 정말 학습에 가치 있는가?"라는 질문이 남습니다. 광고 문구, 자동 생성 스팸, 깨진 인코딩, 의미 없는 boilerplate가 통과했을 수 있습니다.

품질 필터링은 이런 저품질 샘플을 걸러내는 단계입니다. 핵심은 "값싼 것부터 먼저"입니다. 길이나 기호 비율 같은 단순 규칙으로 명백한 garbage를 먼저 제거하고, 언어 감지, perplexity 필터, classifier 순서로 비용이 더 드는 방법을 씁니다.

> "좋은 품질 필터는 '얼마나 많이 버렸는가'보다 '어떤 이유로 버렸는지 설명할 수 있는가'가 중요합니다."

## 이 글에서 다룰 질문

1. Heuristic 필터에서 사용하는 7가지 기본 신호는 무엇인가요?
2. 언어 감지와 perplexity 필터는 어떤 종류의 오염을 잡나요?
3. fastText classifier로 품질을 판단하는 방법은?
4. 필터 순서가 왜 "cheap → expensive" 여야 하나요?
5. 소스별로 다른 필터 기준을 적용하는 이유는 무엇인가요?

---

## 품질 필터 4단계 (Cheap → Expensive)

| 순서 | 방법 | 비용 | 잡는 것 |
|------|------|------|--------|
| 1 | Heuristic 규칙 | 매우 낮음 | 명백한 garbage (짧은 텍스트, 기호 과다) |
| 2 | 언어 감지 | 낮음 | 원하는 언어가 아닌 문서 |
| 3 | Perplexity 필터 | 중간 | 깨진 텍스트, 의미 없는 boilerplate |
| 4 | Classifier | 높음 | 애매한 경계선 저품질 샘플 |

## Before / After: 필터 파이프라인 도입

**Before (필터 없이 전체 데이터 사용)**
```python
# 수집된 10만 건 그대로 학습
model.train(all_data)
# 결과: 광고, 스팸, 깨진 텍스트까지 학습
```

**After (단계별 품질 필터 적용)**
```python
from dataclasses import dataclass

@dataclass
class QualitySignals:
    n_chars: int
    n_words: int
    symbol_ratio: float
    digit_ratio: float
    repetition_ratio: float

def compute_signals(text: str) -> QualitySignals:
    words = text.split()
    n_chars = len(text)
    n_words = len(words)

    if n_words == 0:
        return QualitySignals(n_chars, 0, 1.0, 1.0, 1.0)

    symbol_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(n_chars, 1)
    digit_ratio = sum(1 for c in text if c.isdigit()) / max(n_chars, 1)
    grams = [" ".join(words[i:i+5]) for i in range(len(words)-4)]
    repetition_ratio = 1 - len(set(grams)) / max(len(grams), 1)

    return QualitySignals(n_chars, n_words, symbol_ratio, digit_ratio, repetition_ratio)

def passes_heuristic(text: str) -> tuple[bool, str]:
    """Heuristic 규칙으로 명백한 저품질 텍스트를 걸러냅니다."""
    s = compute_signals(text)
    if s.n_words < 50:
        return False, "too_short"
    if s.symbol_ratio > 0.3:
        return False, "symbol_heavy"
    if s.digit_ratio > 0.5:
        return False, "digit_heavy"
    if s.repetition_ratio > 0.3:
        return False, "repetitive"
    return True, "ok"
```

## 언어 감지와 Perplexity 필터

```python
# pip install fasttext-langdetect
from ftlangdetect import detect

def keep_languages(text: str, allowed: set[str] = {"ko", "en"}, min_conf: float = 0.7) -> bool:
    """원하는 언어의 문서만 남깁니다."""
    sample = text[:1000]  # 처음 1000자면 충분
    result = detect(text=sample, low_memory=True)
    return result["lang"] in allowed and result["score"] >= min_conf

# Perplexity filter (KenLM 필요)
class PerplexityFilter:
    def __init__(self, model_path: str, max_perplexity: float = 500.0):
        import kenlm
        self.model = kenlm.Model(model_path)
        self.max_perplexity = max_perplexity

    def score(self, text: str) -> float:
        log_prob = self.model.score(text, bos=True, eos=True)
        n_tokens = len(text.split()) + 1
        return 10 ** (-log_prob / n_tokens)

    def passes(self, text: str) -> bool:
        return self.score(text) <= self.max_perplexity
```

## 통합 필터 파이프라인

```python
def quality_filter_pipeline(docs: list[str]) -> tuple[list[str], dict]:
    """cheap → expensive 순서로 품질 필터를 적용합니다."""
    stats = {"heuristic": 0, "lang": 0, "perplexity": 0, "kept": 0}
    survivors = []

    for doc in docs:
        # 1단계: 가장 빠른 Heuristic
        ok, reason = passes_heuristic(doc)
        if not ok:
            stats["heuristic"] += 1
            continue

        # 2단계: 언어 감지
        if not keep_languages(doc, allowed={"ko", "en"}):
            stats["lang"] += 1
            continue

        # 3단계: Perplexity (KenLM 있을 때만)
        # if not pf.passes(doc):
        #     stats["perplexity"] += 1
        #     continue

        survivors.append(doc)
        stats["kept"] += 1

    return survivors, stats
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| Classifier를 먼저 실행 | 비용 낭비 | Heuristic → 언어 → Perplexity → Classifier 순서 |
| 전체 텍스트로 언어 감지 | 불필요한 처리 비용 | 처음 1000자만 샘플링해 감지 |
| 모든 소스에 같은 threshold | 특정 도메인 데이터 과도 제거 | 소스별 다른 기준 설정 |
| Drop 이유 기록 안 함 | 왜 버렸는지 모름 | stats 딕셔너리로 이유별 집계 |

## AI 팁

필터 threshold는 영원한 고정값이 아닙니다. 배치마다 소스 분포가 변하므로 히스토그램과 백분위로 분포를 보면서 주기적으로 조정해야 합니다.

```python
import numpy as np

def analyze_filter_distribution(docs: list[str]) -> dict:
    """현재 데이터 배치의 품질 신호 분포를 분석합니다."""
    signals = [compute_signals(doc) for doc in docs]
    symbol_ratios = [s.symbol_ratio for s in signals]

    return {
        "symbol_ratio_p50": np.percentile(symbol_ratios, 50),
        "symbol_ratio_p90": np.percentile(symbol_ratios, 90),
        "symbol_ratio_p99": np.percentile(symbol_ratios, 99),
        "suggested_threshold": np.percentile(symbol_ratios, 95)  # 상위 5%를 필터
    }
```

## 체크리스트

- [ ] Heuristic 규칙 → 언어 감지 → Perplexity → Classifier 순서로 적용한다
- [ ] 각 단계별 Drop 이유와 수량을 기록한다
- [ ] 소스 유형별로 다른 threshold를 설정했다
- [ ] 배치마다 품질 신호 분포를 모니터링한다
- [ ] 필터 전후 샘플을 직접 확인했다

## 처음 질문으로 돌아가기

**7가지 기본 Heuristic 신호는?** 단어 수, 평균 단어 길이, symbol 비율, digit 비율, 대문자 비율, 5-gram 반복률, 전체 길이.

**언어 감지와 Perplexity 필터가 각각 잡는 것은?** 언어 감지는 원하는 언어가 아닌 문서를, Perplexity 필터는 깨진 인코딩이나 의미 없는 boilerplate를 잡습니다.

**fastText classifier 사용 방법은?** Wikipedia/고품질 문서를 positive, low-quality 크롤링을 negative로 학습해 품질 점수를 예측합니다.

**필터 순서가 cheap → expensive여야 하는 이유는?** 명백한 garbage를 앞단에서 제거해야 뒤에 오는 비싼 모델(Perplexity, Classifier)이 처리해야 할 데이터가 줄어 비용이 절감됩니다.

**소스별 다른 기준을 쓰는 이유는?** 뉴스, 포럼, 기술 문서는 길이와 기호 분포가 근본적으로 다릅니다. 같은 threshold를 적용하면 특정 도메인이 과도하게 제거됩니다.

## 정리

품질 필터링은 cheap → expensive 순서로 적용하고, 각 단계의 Drop 이유를 기록해야 합니다. Heuristic으로 명백한 garbage를, 언어 감지로 out-of-domain을, Perplexity로 깨진 텍스트를, Classifier로 경계선 샘플을 걸러냅니다.

다음 글에서는 레이블이 부족할 때 데이터를 늘리는 **합성 데이터 생성**을 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: 데이터 품질 필터링](../ko/06-quality-filtering.md)
- [CCNet: Extracting High Quality Monolingual Datasets](https://arxiv.org/abs/1911.00359)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. **바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링 (현재 글)**
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: Quality Filtering, Heuristic Rules, Perplexity Filter, fastText, 바이브코딩
