---
series: pandas-101
episode: 9
title: 적용 함수와 벡터화
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Pandas
  - Vectorization
  - Performance
  - Apply
  - Beginner
seo_description: apply의 한계와 벡터화의 성능 차이를 실전 감각으로 정리한 글입니다
last_reviewed: '2026-05-12'
---

# 적용 함수와 벡터화

Pandas를 어느 정도 쓰기 시작하면 코드가 돌아가는 것과 빠르게 도는 것이 전혀 다른 문제라는 사실을 곧 만나게 됩니다. 특히 `apply(axis=1)`는 편해 보여서 자주 손이 가지만, 데이터가 커지는 순간 병목이 되기 쉽습니다. 성능 문제를 피하려면 Pandas가 잘하는 계산 방식이 무엇인지 먼저 이해해야 합니다.

이 글은 Pandas 101 시리즈의 9번째 글입니다.

이번 글에서는 `apply`를 금지어처럼 다루기보다, 언제 느려지고 왜 벡터화가 Pandas의 본질인지 구조적으로 살펴보겠습니다.

## 이 글에서 다룰 문제

- 벡터화는 정확히 무엇을 뜻할까요?
- `apply`, `map`, NumPy 연산은 어떤 차이가 있을까요?
- 왜 `apply(axis=1)`가 특히 느릴까요?
- 조건 분기는 어떤 식으로 벡터화할 수 있을까요?
- 자료형이 맞지 않으면 왜 성능과 정확도가 함께 무너질까요?

> Pandas의 속도는 표를 행마다 해석할 때가 아니라 열 단위 배열 계산으로 넘길 때 나옵니다. `apply`가 편한 이유와 느린 이유는 사실 같은 곳에서 시작합니다. 파이썬 함수 호출을 행마다 반복하기 때문입니다.

## 왜 중요한가

같은 계산도 벡터화 여부에 따라 수십 배, 수백 배 차이가 날 수 있습니다. ETL, 특징 생성, 대규모 리포트처럼 반복 계산이 많은 작업에서는 이 차이가 곧 실행 시간과 클라우드 비용 차이로 이어집니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Loop["for-loop"] -->|slow| Apply["apply"]
    Apply -->|faster| Vec["vectorized (NumPy / Pandas ops)"]
```

## 핵심 용어

- 벡터화: 명시적인 반복문 없이 배열 단위로 계산하는 방식입니다.
- **적용 함수**: 행이나 열을 따라 파이썬 함수를 반복 적용하는 방식입니다.
- **원소별 매핑**: 시리즈 값마다 함수를 적용하거나 사전을 대응시키는 방식입니다.
- **조건 선택**: 배열 단위 조건 분기입니다.
- **표현식 가속**: 큰 수식 계산을 빠르게 처리하는 방법입니다.

## 전과 후

이전 관점: 행마다 더하는 반복문이나 `apply(axis=1)`로 계산합니다.

이후 관점: 열 연산, 조건 벡터화, 매핑으로 같은 결과를 훨씬 빠르게 얻습니다.

## 실습: 다섯 단계로 성능 감각 잡기

### 1단계 - 기준 데이터 만들기

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"a": np.arange(1_000_000), "b": np.arange(1_000_000)})
```

백만 행 정도만 되어도 반복 계산 방식의 차이가 눈에 보입니다. 작은 데이터에서 잘 보이지 않던 병목이 이 규모부터는 분명해집니다.

### 2단계 - 느린 경로 보기

```python
# %timeit df.apply(lambda r: r["a"] + r["b"], axis=1)
# Very slow — apply(axis=1) is a per-row Python call
```

`apply(axis=1)`는 각 행을 파이썬 객체처럼 다루며 함수를 반복 호출합니다. 문법은 간단하지만 Pandas가 가장 잘하는 계산 경로는 아닙니다.

### 3단계 - 열 단위로 계산하기

```python
df["c"] = df["a"] + df["b"]   # fastest
```

이 한 줄이 벡터화의 핵심입니다. 계산을 배열 단위로 넘기면 Pandas와 NumPy가 내부 최적화 경로를 사용할 수 있습니다.

### 4단계 - 조건 분기 벡터화하기

```python
df["flag"] = np.where(df["a"] % 2 == 0, "even", "odd")
```

조건 분기를 행 반복문으로 쓰지 않아도 됩니다. `np.where`는 배열 전체에 대해 한 번에 조건을 적용하는 대표적인 도구입니다.

### 5단계 - 코드 값을 이름으로 바꾸기

```python
mapping = {0: "zero", 1: "one"}
print(pd.Series([0, 1, 2]).map(mapping))
```

값 치환이나 코드 변환은 `map`이 잘 맞습니다. 모든 경우를 `apply`로 처리하려고 하면 코드도 느려지고 의도도 흐려집니다.

## 이 코드에서 먼저 봐야 할 점

- `axis=1` 적용 함수는 행마다 파이썬 호출이 일어나 가장 느립니다.
- 열 단위 연산은 내부 저수준 계산 경로를 타므로 훨씬 빠릅니다.
- `np.where`는 벡터화된 조건 분기입니다.

## 자주 하는 실수 다섯 가지

1. `apply(axis=1)`를 기본 해법처럼 남용합니다.
2. 파이썬 반복문으로 행별 계산을 직접 누적합니다.
3. 큰 표현식을 단순 파이썬 계산으로만 처리합니다.
4. `map`에서 생긴 `NaN`을 확인하지 않습니다.
5. 자료형 불일치로 벡터화가 깨져 객체형으로 흘러갑니다.

## 실무에서는 이렇게 이어집니다

대규모 정제, 특징 생성, 리포트 계산처럼 반복이 많은 파이프라인에서는 벡터화가 가장 쉬운 비용 절감 수단입니다. 같은 결과라도 더 짧고 빠른 코드를 만들 수 있기 때문입니다.

## 실무에서는 이렇게 생각합니다

- 먼저 벡터화 가능성을 확인합니다.
- 벡터화가 불가능할 때만 `apply`를 검토합니다.
- 가능하면 `axis=1`은 피합니다.
- 계산 전 자료형을 맞춥니다.
- 실제 병목을 측정한 뒤 최적화합니다.

## 체크리스트

- [ ] 벡터화와 `apply`의 차이를 설명할 수 있습니다.
- [ ] `np.where`로 조건 분기를 작성할 수 있습니다.
- [ ] `map`으로 코드 값을 치환할 수 있습니다.
- [ ] `axis=1` 적용 함수가 느린 이유를 알고 있습니다.

## 연습 문제

1. 벡터화된 덧셈과 `apply(axis=1)`의 실행 시간을 비교해 보세요.
2. 세 단계 조건을 `np.where`로 표현해 보세요.
3. 국가 코드를 국가 이름으로 바꾸는 매핑을 작성해 보세요.

## 정리와 다음 글

벡터화는 Pandas의 성능과 문법을 함께 이해하는 핵심입니다. 행마다 함수를 부르기보다 열 단위 계산으로 넘기는 감각을 익히면 코드가 더 짧고 빠르고 읽기 쉬워집니다. 다음 글에서는 지금까지 배운 내용을 하나의 실전 분석 흐름으로 묶어 보겠습니다.

<!-- toc:begin -->
- [Pandas란 무엇인가?](./01-what-is-pandas.md)
- [시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [필터링과 선택](./04-filtering-and-selection.md)
- [결측치 처리](./05-missing-values.md)
- [그룹화와 집계](./06-groupby.md)
- [병합과 조인](./07-merge-and-join.md)
- [시계열 데이터 다루기](./08-time-series.md)
- **적용 함수와 벡터화 (현재 글)**
- 실전 데이터 분석 (예정)
<!-- toc:end -->

## 참고 자료

- [pandas — Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [pandas — apply](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [NumPy — Universal functions](https://numpy.org/doc/stable/reference/ufuncs.html)
- [Real Python — Fast, Flexible, Easy and Intuitive Pandas](https://realpython.com/fast-flexible-pandas/)

Tags: Pandas, Vectorization, Performance, Apply, Beginner
