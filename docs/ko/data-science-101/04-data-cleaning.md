---
series: data-science-101
episode: 4
title: 데이터 정제
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - DataCleaning
  - Pandas
  - Quality
  - Beginner
seo_description: 결측, 중복, 이상치, 타입 불일치까지 데이터 품질 문제를 발견하고 고치는 5단계 정제 가이드
last_reviewed: '2026-05-04'
---

# 데이터 정제

> Data Science 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *결측, 중복, 이상치, 타입 불일치* 를 *어떤 순서* 로 발견하고 고칠까요?

> *분석 시간의 *80%* 는 정제에 쓰인다 — 좋은 정제는 *나머지 20%* 를 *진짜 분석* 으로 만든다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *데이터 품질* 의 *4대 문제*
- *결측치 처리* 전략
- *이상치* 탐지 기본
- 5단계 정제 실습
- 흔한 함정 5가지

## 왜 중요한가

*Garbage in, garbage out*. *모델* 이 아무리 좋아도 *입력이 더러우면* 결과는 *쓰레기* 입니다. 정제는 *검증* 의 단계입니다.

> *정제는 *분석의 보험* 이다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Raw["Raw Data"] --> Type["Fix Types"]
    Type --> Dup["Drop Duplicates"]
    Dup --> Null["Handle Missing"]
    Null --> Out["Detect Outliers"]
    Out --> Clean["Clean Data"]
```

## 핵심 용어 정리

- **Missing**: 값이 *비어 있음*. `NaN`, `None`, `''` 등.
- **Duplicate**: *같은 키* 의 행이 *여러 번*.
- **Outlier**: *통계적으로 멀리 떨어진* 값.
- **Type Coercion**: *문자열 → 숫자/날짜* 같은 *타입 변환*.
- **Imputation**: 결측을 *채우는* 전략.

## Before/After

**Before**: `signup_at` 컬럼이 *문자열* 이라 *날짜 비교* 가 *틀린 결과*.

**After**: `pd.to_datetime` 으로 변환 후 *비교* 가 *정확*.

## 실습: 5단계 정제

### 1단계 — 타입 정리

```python
import pandas as pd
df = pd.read_csv("users.csv")
df["signup_at"] = pd.to_datetime(df["signup_at"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
```

### 2단계 — 중복 제거

```python
print("before:", len(df))
df = df.drop_duplicates(subset=["user_id"], keep="last")
print("after :", len(df))
```

### 3단계 — 결측 처리

```python
# 결측 비율 확인
print(df.isna().mean().sort_values(ascending=False).head())

# 전략: 핵심 컬럼은 drop, 보조 컬럼은 채움
df = df.dropna(subset=["user_id", "signup_at"])
df["country"] = df["country"].fillna("UNKNOWN")
```

### 4단계 — 이상치 탐지

```python
q1, q3 = df["amount"].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
df["amount_flag"] = ~df["amount"].between(lower, upper)
print(df["amount_flag"].mean())
```

### 5단계 — 검증 리포트

```python
report = {
    "rows": len(df),
    "nulls": df.isna().sum().to_dict(),
    "outlier_rate": float(df["amount_flag"].mean()),
}
print(report)
```

## 이 코드에서 주목할 점

- *타입 정리* 가 *모든 정제의 출발*.
- *결측 비율* 을 *먼저* 본다.
- *이상치* 는 *제거가 아니라 *flag* 부터 시작.

## 자주 하는 실수 5가지

1. ***결측* 을 *0* 으로 채운다.** 평균이 *왜곡*.
2. ***중복* 을 *조용히* 지운다.** *왜* 생겼는지 *모른다*.
3. ***이상치* 를 *바로* 삭제.** *진짜 신호* 일 수 있다.
4. ***타입 변환 실패* 를 *무시*.** `errors="raise"` 로 *드러내자*.
5. ***정제 단계* 를 *문서* 에 적지 않는다.** 재현이 *불가능*.

## 실무에서는 이렇게 쓰입니다

데이터팀은 정제 단계를 *Great Expectations* 같은 *검증 도구* 로 *테스트* 합니다. CI 에서 *데이터 품질 알람* 이 울리면 *파이프라인이 멈춥니다*.

## 시니어 엔지니어는 이렇게 생각합니다

- *결측 비율* 을 *대시보드* 에 둔다.
- *이상치* 는 *flag → 검토 → 결정*.
- *정제 코드* 를 *함수* 로 분리해 *재사용*.
- *원본은 건드리지 않는다*. 정제는 *복사본* 에서.
- *검증 테스트* 를 *코드* 처럼 *PR* 한다.

## 체크리스트

- [ ] *결측/중복/이상치/타입* 을 *순서대로* 본다.
- [ ] *Imputation* 전략을 설명할 수 있다.
- [ ] *IQR* 의 의미를 안다.
- [ ] *검증 리포트* 를 만든다.

## 연습 문제

1. *공개 데이터셋* 한 개의 *결측 비율* 을 출력해 보세요.
2. *이상치 flag* 를 만들고, *제거 vs 유지* 의 *효과* 를 비교해 보세요.
3. *타입 변환 실패* 가 *분석* 을 어떻게 망쳤는지 사례를 적어 보세요.

## 정리 및 다음 단계

정제는 *조용한 노동* 이지만 *분석의 모든 결론* 을 떠받칩니다. 다음 글에서는 깨끗해진 데이터를 *탐색* 하는 *EDA* 를 살펴봅니다.

<!-- toc:begin -->
- [Data Science란 무엇인가?](./01-what-is-data-science.md)
- [문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [데이터 수집](./03-data-collection.md)
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
- [Tidy Data — Hadley Wickham](https://vita.had.co.nz/papers/tidy-data.pdf)
