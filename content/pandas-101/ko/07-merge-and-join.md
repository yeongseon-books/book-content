---
series: pandas-101
episode: 7
title: 병합과 조인
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Pandas
  - Merge
  - Join
  - SQL
  - Beginner
seo_description: 데이터 병합과 조인 전략을 익힙니다. Inner, Left 조인의 차이와 키 관계 검증, 행 수 폭증 방지 등 안전한 결합 패턴을 정리합니다.
last_reviewed: '2026-05-15'
---

# 병합과 조인

실무 데이터는 거의 항상 여러 표로 나뉘어 있습니다. 사용자 정보는 한 표에, 주문 기록은 다른 표에, 광고 지표는 또 다른 표에 있습니다. 그래서 두 표를 어떻게 합치느냐는 데이터 분석의 보조 기술이 아니라 핵심 능력에 가깝습니다.

이 글은 Pandas 101 시리즈의 7번째 글입니다.

이번 글에서는 `merge`와 `join`을 단순히 SQL 용어의 번역으로 보지 않고, 키가 어디에 놓여 있는지에 따라 표를 안전하게 결합하는 도구로 정리해 보겠습니다.

## 이 글에서 다룰 문제

- 왜 Pandas에는 `merge`와 `join`이 둘 다 있을까요?
- 안쪽, 왼쪽, 오른쪽, 바깥쪽, 교차 조인은 어떻게 다를까요?
- 중복 키가 있을 때 왜 행 수가 갑자기 늘어날까요?
- `indicator`, `suffixes`, `validate`는 어떤 상황에서 유용할까요?
- 조인 전후에 무엇을 반드시 확인해야 할까요?

> 병합은 두 표를 이어 붙이는 일이 아니라 두 키 체계가 어떤 관계인지 검증하는 일입니다. 행 수 변화와 키 중복을 보지 않으면 조인은 성공한 것처럼 보여도 결과 표는 이미 틀어져 있을 수 있습니다.

## 왜 중요한가

실무 분석의 상당수는 결국 표와 표를 연결하는 작업입니다. 사용자와 주문, 광고와 전환, 상품과 재고를 안전하게 합칠 수 있어야 지표도 맞고 모델 입력도 안정적입니다.

## 한눈에 보는 개념

![키 관계와 행 수 변화를 함께 점검하는 안전한 병합 흐름](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/07/07-01-concept-at-a-glance.ko.png)
*키 관계와 행 수 변화를 함께 점검하는 안전한 병합 흐름*

## 핵심 용어

- **안쪽 조인**: 양쪽 모두에 있는 키만 남깁니다.
- **왼쪽 조인**: 왼쪽 표의 모든 행을 유지합니다.
- **오른쪽 조인**: 오른쪽 표를 기준으로 유지합니다.
- **바깥쪽 조인**: 양쪽 키의 합집합을 남깁니다.
- **교차 조인**: 가능한 모든 조합을 만듭니다.

## 전과 후

이전 관점: 병합 한 번에 행 수가 갑자기 폭증하고도 원인을 모릅니다.

이후 관점: 키 관계를 먼저 검증하고 `validate`로 가정을 코드에 남깁니다.

## 실습: 다섯 단계로 표 합치기

### 1단계 - 데이터 준비하기

```python
import pandas as pd
users = pd.DataFrame({"uid": [1, 2, 3], "name": ["a", "b", "c"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})
```

작은 예제지만 이미 중요한 함정이 숨어 있습니다. `orders`에는 같은 `uid`가 두 번 나오므로, 키 관계를 의식하지 않으면 결과 행 수가 달라질 수 있습니다.

### 2단계 - 안쪽 조인하기

```python
print(users.merge(orders, on="uid"))
```

기본 `how`는 안쪽 조인입니다. 양쪽에 모두 있는 키만 남기므로 결과를 보면 사용자 3번은 빠집니다.

### 3단계 - 왼쪽 조인과 바깥쪽 조인하기

```python
print(users.merge(orders, on="uid", how="left"))
print(users.merge(orders, on="uid", how="outer", indicator=True))
```

조인 결과를 눈으로 확인할 때는 값보다 `_merge` 열이 더 중요할 때가 많습니다. 어느 키가 양쪽에 있었고, 어느 키가 한쪽에만 있었는지를 즉시 알려 주기 때문입니다.

**예상 출력:**

```text
   uid name  amount     _merge
0    1    a   100.0       both
1    1    a   200.0       both
2    2    b    50.0       both
3    3    c     NaN  left_only
```

왼쪽 조인은 기준 표를 보존하고, 바깥쪽 조인은 양쪽 키를 모두 살립니다. `indicator=True`를 켜면 각 행이 어느 쪽에서 왔는지 추적할 수 있습니다.

### 4단계 - 같은 이름의 열 충돌 피하기

```python
df1 = pd.DataFrame({"k": [1], "v": [10]})
df2 = pd.DataFrame({"k": [1], "v": [20]})
print(df1.merge(df2, on="k", suffixes=("_a", "_b")))
```

같은 이름의 열이 있을 때 접미사를 지정하지 않으면 결과 열이 읽기 어려워집니다. 접미사는 충돌 해결이자 문서화 장치입니다.

### 5단계 - 키 관계를 검증하기

```python
try:
    users.merge(orders, on="uid", validate="one_to_one")
except Exception as e:
    print("expected:", type(e).__name__)
```

`validate`는 잘못된 조인을 조용히 통과시키지 않게 만드는 안전장치입니다. 기대한 관계와 다르면 바로 예외가 나와서 행 수 폭증을 조기에 막아 줍니다.

**예상 출력:**

```text
expected: MergeError
```

`validate`는 조인 가정을 코드에 선언하는 매우 좋은 방법입니다. 기대한 관계와 실제 데이터 관계가 다르면 즉시 오류를 내서 조용한 데이터 오염을 막아 줍니다.

## 이 코드에서 먼저 봐야 할 점

- `indicator=True`는 각 행의 출처를 보여 줍니다.
- `suffixes`는 같은 이름의 열 충돌을 정리합니다.
- `validate`는 조인 가정을 코드에 남기는 장치입니다.

## 자주 하는 실수 다섯 가지

1. 중복 키 때문에 행 수가 폭증하는데도 그대로 넘어갑니다.
2. 기본 조인 방식이 안쪽 조인이라는 사실을 놓칩니다.
3. 접미사를 지정하지 않아 결과 열 해석이 어려워집니다.
4. 왼쪽과 오른쪽 키의 자료형이 다른 채로 병합합니다.
5. 인덱스 정리를 하지 않아 다음 단계에서 충돌을 만듭니다.

## 실무에서는 이렇게 이어집니다

고객 데이터와 주문 데이터, 광고 데이터와 전환 데이터처럼 실무 분석은 대부분 조인 위에 세워집니다. 그래서 행 수 추적, 키 중복 확인, 자료형 일치 여부는 병합 전후의 기본 점검 항목이 됩니다.

## 실무에서는 이렇게 생각합니다

- 병합 전후 행 수를 항상 비교합니다.
- `validate`로 키 관계 가정을 명시합니다.
- 조인 키의 자료형을 먼저 맞춥니다.
- 병합 전에 중복을 정리할지 의도적으로 결정합니다.
- 결과 표를 한 번 더 점검해 예상과 맞는지 확인합니다.

## 체크리스트

- [ ] 다섯 가지 조인 방식의 차이를 설명할 수 있습니다.
- [ ] `validate`를 이용해 조인 가정을 검증할 수 있습니다.
- [ ] `indicator`로 행 출처를 확인할 수 있습니다.
- [ ] `suffixes`로 열 이름 충돌을 정리할 수 있습니다.

## 연습 문제

1. 왼쪽 조인과 바깥쪽 조인의 행 수 차이를 비교해 보세요.
2. `validate="one_to_one"`가 실패하는 예제를 만들어 오류를 확인해 보세요.
3. `indicator` 열을 이용해 오른쪽 표에만 있는 행을 찾아보세요.

## 정리와 다음 글

병합은 데이터를 이어 붙이는 기술이 아니라 데이터 관계를 검증하는 기술입니다. 키와 행 수를 함께 보아야 조인이 안전해집니다. 다음 글에서는 시간 축이 붙은 데이터를 다루는 시계열 작업을 살펴보겠습니다.

<!-- toc:begin -->
- [Pandas란 무엇인가?](./01-what-is-pandas.md)
- [시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [필터링과 선택](./04-filtering-and-selection.md)
- [결측치 처리](./05-missing-values.md)
- [그룹화와 집계](./06-groupby.md)
- **병합과 조인 (현재 글)**
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)
<!-- toc:end -->

## 참고 자료

- [pandas — Merge, join, concatenate and compare](https://pandas.pydata.org/docs/user_guide/merging.html)
- [pandas — merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- [pandas — join](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html)
- [SQL Joins Explained — Mode Analytics](https://mode.com/sql-tutorial/sql-joins/)

Tags: Pandas, Merge, Join, SQL, Beginner
