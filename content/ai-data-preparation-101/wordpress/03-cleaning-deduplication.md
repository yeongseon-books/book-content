---
title: "바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거"
series: ai-data-preparation-101
episode: 3
language: ko
tags:
- Data Cleaning
- Deduplication
- MinHash
- LSH
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 세 번째 글입니다.

---

바이브코딩으로 데이터를 모으고 나면 "이제 바로 학습하면 되나요?"라고 묻고 싶지만, 실제로는 그렇지 않습니다. 수집된 원본 데이터에는 HTML 태그, 깨진 인코딩, 특수문자, 과도한 공백, 그리고 수도 없이 많은 중복이 숨어 있습니다.

특히 중복은 생각보다 심각합니다. 웹 크롤링 데이터의 20-40%가 중복인 경우도 있습니다. 중복이 많으면 모델이 특정 패턴을 과도하게 학습하고, 평가 데이터가 학습 데이터에 이미 포함되는 오염 문제도 생깁니다. 중복 제거는 단순한 정리가 아니라 모델 품질을 위한 필수 단계입니다.

> "중복 데이터는 학습 데이터에 '같은 페이지를 100번 읽히는 것'과 같습니다. 모델이 그 패턴을 과도하게 학습합니다."

## 이 글에서 다룰 질문

1. 텍스트 정제에서 순서가 중요한 이유는 무엇인가요?
2. 정확 중복(exact dedup)과 근사 중복(near dedup)은 어떻게 다른가요?
3. MinHash+LSH로 대규모 근사 중복을 빠르게 찾는 방법은?
4. 의미 중복(semantic dedup)은 언제 필요한가요?
5. 정제 전후 품질 변화를 어떻게 측정하나요?

---

## 중복 제거 단계

| 단계 | 방법 | 속도 | 적합한 상황 |
|------|------|------|------------|
| 정확 중복 | sha256 해시 | 매우 빠름 | 완전히 동일한 텍스트 |
| 근사 중복 | MinHash + LSH | 빠름 | 약간 다르지만 같은 내용 |
| 의미 중복 | 임베딩 + 코사인 유사도 | 느림 | 표현은 다르지만 같은 의미 |

## Before / After: 텍스트 정제

**Before (원본 텍스트)**
```
"  <p>안녕하세요!!!  </p>\n\n고객  센터에  문의해주세요...  "
```

**After (정제된 텍스트)**
```
"안녕하세요! 고객 센터에 문의해주세요."
```

정제는 순서가 중요합니다. HTML 태그 제거 → 인코딩 정규화 → 공백 정리 → 특수문자 정리 순서를 지켜야 합니다.

```python
import re
import unicodedata

def clean_text(text: str) -> str:
    """텍스트 정제 6단계를 순서대로 적용합니다."""
    # 1. HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 2. Unicode 정규화 (NFC: 한국어에 적합)
    text = unicodedata.normalize('NFC', text)
    # 3. 과도한 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()
    # 4. 과도한 구두점 정리 (!!!!! → !)
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    # 5. 제어 문자 제거
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # 6. 줄 끝 공백 제거
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    return text
```

## 정확 중복 제거

```python
import hashlib

def exact_dedup(texts: list[str]) -> list[str]:
    """sha256 해시로 정확히 동일한 텍스트를 제거합니다."""
    seen = set()
    unique = []

    for text in texts:
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if text_hash not in seen:
            seen.add(text_hash)
            unique.append(text)

    removed = len(texts) - len(unique)
    print(f"정확 중복 제거: {removed}개 ({removed/len(texts):.1%})")
    return unique
```

## 근사 중복 제거: MinHash + LSH

```python
from datasketch import MinHash, MinHashLSH

def near_dedup(texts: list[str], threshold: float = 0.8, num_perm: int = 128) -> list[str]:
    """MinHash LSH로 유사도 임계값 이상인 중복을 제거합니다."""
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    minhashes = []
    unique_indices = []

    for i, text in enumerate(texts):
        m = MinHash(num_perm=num_perm)
        for word in text.split():
            m.update(word.encode('utf-8'))

        # 이미 유사한 문서가 있으면 건너뜀
        result = lsh.query(m)
        if not result:
            lsh.insert(str(i), m)
            unique_indices.append(i)
        minhashes.append(m)

    print(f"근사 중복 제거: {len(texts) - len(unique_indices)}개")
    return [texts[i] for i in unique_indices]
```

## 정제 전후 비교

```python
def summarize_before_after(original: list[str], cleaned: list[str]) -> dict:
    """정제 전후 주요 지표를 비교합니다."""
    avg_len_before = sum(len(t) for t in original) / max(len(original), 1)
    avg_len_after = sum(len(t) for t in cleaned) / max(len(cleaned), 1)

    return {
        "행 수": {"before": len(original), "after": len(cleaned), "제거율": 1 - len(cleaned)/len(original)},
        "평균 길이": {"before": avg_len_before, "after": avg_len_after},
        "총 글자 수": {"before": sum(len(t) for t in original), "after": sum(len(t) for t in cleaned)}
    }
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 정제 순서 바꿈 | 처리 결과가 달라짐 | HTML 제거 → 인코딩 → 공백 순서 유지 |
| 정확 중복만 제거 | 표현 조금 다른 중복 남음 | MinHash로 근사 중복도 제거 |
| threshold 너무 낮음 | 다른 내용까지 제거 | 0.8-0.9 범위에서 시작 |
| 정제 전 sha256 기록 | 원본 추적 불가 | 정제 전 원본 sha256 먼저 기록 |

## AI 팁

MinHash 임계값을 결정할 때는 여러 threshold 값에서 제거되는 샘플을 직접 눈으로 확인하세요. 0.8에서 제거되는 샘플이 실제로 중복인지, 의미 있는 변형인지 판단이 필요합니다.

```python
def evaluate_threshold(texts: list[str], thresholds: list[float] = [0.7, 0.8, 0.9]) -> dict:
    """여러 threshold에서 제거 비율을 비교합니다."""
    results = {}
    for threshold in thresholds:
        unique = near_dedup(texts[:1000], threshold=threshold)  # 샘플로 테스트
        results[threshold] = {
            "unique_count": len(unique),
            "removed_ratio": 1 - len(unique) / 1000
        }
    return results
```

## 체크리스트

- [ ] clean_text 6단계를 순서대로 적용했다
- [ ] 정확 중복을 sha256으로 먼저 제거했다
- [ ] 근사 중복을 MinHash+LSH로 제거했다
- [ ] 정제 전후 행 수와 품질 지표를 비교했다
- [ ] threshold 값을 샘플로 검증했다

## 처음 질문으로 돌아가기

**정제 순서가 중요한 이유는?** HTML 태그를 제거하기 전에 공백을 정리하면 태그 안의 텍스트가 붙어버립니다. 순서를 지켜야 올바른 결과가 나옵니다.

**정확 중복 vs 근사 중복은?** 정확 중복은 sha256 해시가 같은 경우, 근사 중복은 약간 다르지만 내용이 거의 같은 경우(예: 날짜만 다른 같은 기사). MinHash+LSH로 근사 중복을 효율적으로 찾습니다.

**MinHash+LSH 동작 방식은?** 텍스트를 단어 단위로 해시해 MinHash 서명을 만들고, LSH(Locality Sensitive Hashing)로 유사한 서명끼리 같은 버킷에 모아 빠르게 유사 문서를 찾습니다.

**의미 중복은 언제?** 표현은 완전히 다르지만 같은 내용인 경우(번역본, 패러프레이즈). 임베딩 기반 코사인 유사도로 찾지만 비용이 높아 중요도가 높은 데이터에만 적용합니다.

**정제 전후 측정은?** 행 수, 평균 텍스트 길이, 중복 제거 비율을 before/after로 비교합니다.

## 정리

데이터 정제와 중복 제거는 학습 데이터 품질의 핵심입니다. 6단계 텍스트 정제를 순서대로 적용하고, sha256으로 정확 중복을, MinHash+LSH로 근사 중복을 제거합니다. 정제 전후 지표를 비교하면 어느 정도의 노이즈가 제거됐는지 파악할 수 있습니다.

다음 글에서는 개인정보를 탐지하고 익명화하는 **PII 탐지와 익명화**를 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: 데이터 정제와 중복 제거](../ko/03-cleaning-deduplication.md)
- [datasketch - MinHash LSH Library](https://ekzhu.com/datasketch/lsh.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. **바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거 (현재 글)**
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: Data Cleaning, Deduplication, MinHash, LSH, 바이브코딩
