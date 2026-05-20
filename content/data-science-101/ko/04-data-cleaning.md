---
series: data-science-101
episode: 4
title: "Data Science 101 (4/10): 데이터 정제"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - DataCleaning
  - Pandas
  - Quality
  - Beginner
seo_description: 결측, 중복, 이상치, 타입 문제를 다루는 데이터 정제의 기본 순서를 설명합니다
last_reviewed: '2026-05-15'
---

# Data Science 101 (4/10): 데이터 정제

이 글은 Data Science 101 시리즈의 네 번째 글입니다.

많은 사람이 데이터 작업의 핵심을 모델링이라고 생각하지만, 실제 시간을 가장 많이 잡아먹는 단계는 대개 정제입니다. 수집한 데이터를 그대로 쓰는 일은 거의 없습니다. 문자열이어야 할 값이 숫자로 들어오기도 하고, 날짜가 문자로 저장되기도 하고, 같은 사용자가 여러 번 들어오거나 결측치가 조용히 섞여 들어오기도 합니다.

정제는 지루한 사전 작업처럼 보일 수 있지만, 사실상 분석의 보험입니다. 입력이 불안정하면 그 위에 쌓은 시각화, 지표, 모델도 모두 흔들립니다. 이 글에서는 실무에서 가장 자주 만나는 네 가지 품질 문제와 이를 점검하는 기본 순서를 정리합니다.

## 먼저 던지는 질문

- 데이터 정제를 어떤 순서로 진행하면 좋을까요?
- 결측치, 중복, 이상치, 타입 불일치는 왜 가장 먼저 확인해야 할까요?
- `0`으로 채우기처럼 단순한 처리가 왜 위험할까요?

## 큰 그림

![Data Science 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/04/04-01-concept-at-a-glance.ko.png)

*Data Science 101 4장 흐름 개요*

이 그림에서는 데이터 정제를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 데이터 정제의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배우는 내용

- 가장 흔한 네 가지 데이터 품질 문제
- 결측치를 다루는 기본 전략
- 이상치를 탐지하는 가장 기초적인 방법
- 5단계 정제 실습 흐름
- 정제 단계에서 자주 생기는 함정 다섯 가지

## 왜 중요한가

오염된 입력에서 좋은 결과가 나오길 기대하기는 어렵습니다. 모델이 아무리 좋아도 입력이 틀리면 결과도 틀립니다. 그래서 정제는 미관을 위한 손질이 아니라, 분석 가능 여부를 결정하는 검증 단계입니다.

특히 입문 단계에서는 정제를 “모델링 전에 하는 귀찮은 준비”로 오해하기 쉽습니다. 하지만 실무에서는 정제가 부실한 프로젝트일수록 이후의 설명 비용과 디버깅 비용이 훨씬 더 커집니다.

> 정제는 분석을 가능하게 만드는 안전장치입니다.

## 핵심 개념 한눈에 보기

## 핵심 용어

- **Missing**: `NaN`, `None`, 빈 문자열처럼 값이 비어 있는 상태입니다.
- **Duplicate**: 같은 키를 가진 행이 여러 번 들어온 상태입니다.
- **Outlier**: 다른 값들과 통계적으로 멀리 떨어진 값입니다.
- **Type coercion**: 문자열을 숫자나 날짜로 변환하는 작업입니다.
- **Imputation**: 결측치를 일정한 규칙으로 채우는 전략입니다.

## Before / After

**Before**: `signup_at` 컬럼이 문자열 상태라 날짜 비교가 틀린 결과를 냅니다. 최근 가입자만 보려 했는데 사전순 비교가 되어 버리는 식입니다.

**After**: `pd.to_datetime`으로 타입을 맞추고 나면 비교가 의도대로 동작합니다. 정제는 종종 이런 기본적인 오류를 바로잡는 작업입니다.

## 실습: 5단계 정제

### 1단계 — 타입 정리

```python
import pandas as pd
df = pd.read_csv("users.csv")
df["signup_at"] = pd.to_datetime(df["signup_at"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
```

타입 정리는 거의 모든 정제의 출발점입니다. 날짜가 문자열인 상태에서는 날짜 필터가 위험하고, 숫자가 문자열이면 집계 결과도 흔들립니다. `errors="coerce"`를 쓰면 변환 실패가 결측으로 드러나기 때문에 이상값 위치를 파악하기 쉽습니다.

### 2단계 — 중복 제거

```python
print("before:", len(df))
df = df.drop_duplicates(subset=["user_id"], keep="last")
print("after :", len(df))
```

중복은 단순히 지우는 것으로 끝내면 아쉬울 때가 많습니다. 왜 중복이 생겼는지 알아야 다음 수집 단계에서 같은 문제가 반복되지 않기 때문입니다. 정제는 임시 수리고, 원인 추적은 별도 과제라는 관점이 필요합니다.

### 3단계 — 결측 처리

```python
# Inspect missingness
print(df.isna().mean().sort_values(ascending=False).head())

# Strategy: drop critical, fill optional
df = df.dropna(subset=["user_id", "signup_at"])
df["country"] = df["country"].fillna("UNKNOWN")
```

결측치는 먼저 비율부터 봐야 합니다. 얼마나 비었는지, 특정 컬럼에 몰려 있는지, 중요한 컬럼인지에 따라 전략이 달라집니다. 핵심 키가 비었으면 보통 제거하고, 보조 컬럼은 채우는 편이 낫습니다.

### 4단계 — 이상치 탐지

```python
q1, q3 = df["amount"].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
df["amount_flag"] = ~df["amount"].between(lower, upper)
print(df["amount_flag"].mean())
```

이상치는 무조건 제거 대상이 아닙니다. 데이터 오류일 수도 있지만, 오히려 중요한 신호일 수도 있습니다. 그래서 보통은 먼저 표시한 뒤 도메인 맥락에서 검토합니다.

### 5단계 — 검증 리포트 만들기

```python
report = {
    "rows": len(df),
    "nulls": df.isna().sum().to_dict(),
    "outlier_rate": float(df["amount_flag"].mean()),
}
print(report)
```

정제가 끝났다면 무엇이 얼마나 바뀌었는지 남겨야 합니다. 행 수가 얼마나 줄었는지, 어떤 컬럼의 결측이 얼마나 남았는지, 이상치 비율이 얼마인지 적어 두면 다음 실행과 비교하기 쉬워집니다.

**Expected output:** 남은 행 수, 컬럼별 결측 수, 이상치 비율을 담은 검증 리포트를 얻습니다.

## 이 코드에서 먼저 봐야 할 점

- 타입 정리는 모든 정제의 출발점입니다.
- 결측 비율을 먼저 봐야 처리 전략을 정할 수 있습니다.
- 이상치는 바로 삭제하지 말고 먼저 표시해 두는 편이 안전합니다.

## 자주 하는 실수 다섯 가지

1. **결측치를 무조건 `0`으로 채우는 실수**: 평균과 분포가 쉽게 왜곡됩니다.
2. **중복을 조용히 지우는 실수**: 원인을 배우지 못해 같은 문제가 반복됩니다.
3. **이상치를 즉시 삭제하는 실수**: 실제 중요한 신호를 버릴 수도 있습니다.
4. **타입 변환 실패를 무시하는 실수**: 실패 지점을 드러내지 않으면 오류가 숨어 버립니다.
5. **정제 과정을 기록하지 않는 실수**: 재현 가능한 분석이 아니게 됩니다.

## 실무에서는 이렇게 나타납니다

실무 팀은 Great Expectations 같은 도구로 정제 규칙을 테스트하기도 합니다. 결측률이 일정 기준을 넘거나 허용하지 않은 값이 들어오면 파이프라인을 멈추게 만듭니다. 중요한 점은 정제를 사람의 감에만 맡기지 않고 규칙으로 끌어올린다는 것입니다.

## 시니어는 이렇게 생각합니다

- 결측률은 대시보드로 계속 봐야 합니다.
- 이상치는 표시 → 검토 → 결정 순서로 다룹니다.
- 정제 로직은 재사용 가능한 함수로 분리합니다.
- 원본은 건드리지 않고 복사본에서 작업합니다.
- 검증 규칙도 코드처럼 리뷰해야 합니다.

## 체크리스트

- [ ] 결측, 중복, 이상치, 타입을 어떤 순서로 볼지 알고 있습니다.
- [ ] imputation 전략을 설명할 수 있습니다.
- [ ] IQR이 무엇인지 알고 있습니다.
- [ ] 검증 리포트를 만들 수 있습니다.

## 연습 문제

1. 공개 데이터셋 하나를 골라 결측 비율을 출력해 보세요.
2. 이상치 플래그를 만든 뒤, 유지했을 때와 제거했을 때 차이를 비교해 보세요.
3. 타입 변환 실패가 분석을 깨뜨린 사례를 하나 문서화해 보세요.

## 정리 및 다음 글

데이터 정제는 조용하지만 가장 많은 결론을 떠받치는 작업입니다. 입력이 정리되어야 이후 EDA와 모델링도 믿을 수 있습니다. 다음 글에서는 이렇게 정리한 데이터를 실제로 읽고 이해하는 탐색적 데이터 분석을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **데이터 정제를 어떤 순서로 진행하면 좋을까요?**
  - 본문의 기준은 데이터 정제를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **결측치, 중복, 이상치, 타입 불일치는 왜 가장 먼저 확인해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`0`으로 채우기처럼 단순한 처리가 왜 위험할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science 101 (1/10): Data Science란 무엇인가?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): 데이터 수집](./03-data-collection.md)
- **데이터 정제 (현재 글)**
- 탐색적 데이터 분석 (예정)
- 시각화 (예정)
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Working with Missing Data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Great Expectations — Data Quality Tests](https://docs.greatexpectations.io/docs/)
- [Wikipedia — Interquartile Range](https://en.wikipedia.org/wiki/Interquartile_range)
- [Hadley Wickham — Tidy Data](https://vita.had.co.nz/papers/tidy-data.pdf)

Tags: DataScience, DataCleaning, Pandas, Quality, Beginner
