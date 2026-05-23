---
series: pandas-101
episode: 7
title: "Pandas 101 (7/10): 병합과 조인"
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

# Pandas 101 (7/10): 병합과 조인

실무 데이터는 거의 항상 여러 표로 나뉘어 있습니다. 사용자 정보는 한 표에, 주문 기록은 다른 표에, 광고 지표는 또 다른 표에 있습니다. 그래서 두 표를 어떻게 합치느냐는 데이터 분석의 보조 기술이 아니라 핵심 능력에 가깝습니다.

이번 글에서는 `merge`와 `join`을 단순히 SQL 용어의 번역으로 보지 않고, 키가 어디에 놓여 있는지에 따라 표를 안전하게 결합하는 도구로 정리해 보겠습니다.

![Pandas 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/07/07-01-concept-at-a-glance.ko.png)
*Pandas 101 7장 흐름 개요*
> **`merge`는 관계를 검증하는 도구**입니다. 두 표를 합쳤을 때 행이 늘어나는지, 중복 키가 있는지, 자료형이 일치하는지를 항상 확인해야 합니다.

## 먼저 던지는 질문

- 왜 Pandas에는 `merge`와 `join`이 둘 다 있을까요?
- 안쪽, 왼쪽, 오른쪽, 바깥쪽, 교차 조인은 어떻게 다를까요?
- 중복 키가 있을 때 왜 행 수가 갑자기 늘어날까요?

## 왜 중요한가

실무 분석의 상당수는 결국 표와 표를 연결하는 작업입니다. 사용자와 주문, 광고와 전환, 상품과 재고를 안전하게 합칠 수 있어야 지표도 맞고 모델 입력도 안정적입니다.

## 핵심 용어

- **안쪽 조인**: 양쪽 모두에 있는 키만 남깁니다.
- **왼쪽 조인**: 왼쪽 표의 모든 행을 유지합니다.
- **오른쪽 조인**: 오른쪽 표를 기준으로 유지합니다.
- **바깥쪽 조인**: 양쪽 키의 합집합을 남깁니다.
- **교차 조인**: 가능한 모든 조합을 만듭니다.
- **키**: 두 표를 연결하는 기준 열입니다.

### 조인 방식 비교

다음 표는 다섯 가지 조인 방식의 차이와 사용 조건을 정리한 것입니다.

| 조인 방식 | how 파라미터 | 왼쪽 키 | 오른쪽 키 | 결과 행 | 주요 용도 |
|---|---|---|---|---|---|
| 안쪽 조인 | `inner` | 매칭된 행만 | 매칭된 행만 | 교집합 | 양쪽에 모두 존재하는 데이터만 분석 |
| 왼쪽 조인 | `left` | 전체 유지 | 매칭된 행만 | 왼쪽 기준 | 기준 표를 보존하며 정보 추가 |
| 오른쪽 조인 | `right` | 매칭된 행만 | 전체 유지 | 오른쪽 기준 | 왼쪽 조인의 역방향 |
| 바깥쪽 조인 | `outer` | 전체 유지 | 전체 유지 | 합집합 | 양쪽 키 모두 보존 |
| 교차 조인 | `cross` | 모든 행 | 모든 행 | 곱집합 | 모든 조합 생성 |

안쪽 조인은 기본값이므로 `how`를 생략하면 자동으로 적용됩니다. 왼쪽 조인은 실무에서 가장 많이 쓰이는 패턴으로, 기준 표의 모든 행을 유지한 채 다른 표의 정보를 추가할 때 사용합니다.

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

### 결측치 처리 전략

조인을 하면 왼쪽이나 오른쪽 표에만 있는 키 때문에 결측치가 생길 수 있습니다. 이 결측치를 어떻게 다룰지는 분석 목적에 따라 달라집니다.

| 전략 | 조건 | 장점 | 단점 |
|---|---|---|---|
| 삭제 | 결측이 소수 | 간단하고 명확 | 정보 손실 |
| 대체 | 합리적 기본값 존재 | 행 수 유지 | 왜곡 가능성 |
| 보간 | 시간/순서 데이터 | 추세 반영 | 추가 가정 필요 |
| 플래그 추가 | 결측 여부가 중요 | 정보 유지 | 열 증가 |

```python
users = pd.DataFrame({"uid": [1, 2, 3], "name": ["a", "b", "c"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})

merged = users.merge(orders, on="uid", how="left")

# 전략 1: 결측 삭제
print(merged.dropna())

# 전략 2: 기본값 대체
merged["amount"] = merged["amount"].fillna(0)
print(merged)

# 전략 4: 결측 플래그
merged["has_order"] = merged["amount"].notna()
print(merged)
```

**예상 출력 (플래그 추가):**

```text
   uid name  amount  has_order
0    1    a   100.0       True
1    1    a   200.0       True
2    2    b    50.0       True
3    3    c     0.0      False
```

결측치를 그냥 두면 이후 계산에서 예상치 못한 오류가 생길 수 있습니다. 조인 직후 결측 패턴을 확인하고 명시적으로 처리하는 습관이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- `indicator=True`는 각 행의 출처를 보여 줍니다.
- `suffixes`는 같은 이름의 열 충돌을 정리합니다.
- `validate`는 조인 가정을 코드에 남기는 장치입니다.

### fillna와 interpolate 예제

조인 후 결측치를 보간하는 패턴은 시계열 데이터나 순서가 있는 데이터에서 자주 등장합니다.

```python
import pandas as pd
import numpy as np

# 시간순 데이터
df = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=5),
    "value": [10, np.nan, np.nan, 40, 50],
})

# 선형 보간
df["interpolated"] = df["value"].interpolate(method="linear")

# 앞 값으로 채우기
df["ffill"] = df["value"].fillna(method="ffill")

# 뒤 값으로 채우기
df["bfill"] = df["value"].fillna(method="bfill")

print(df)
```

**예상 출력:**

```text
        date  value  interpolated  ffill  bfill
0 2026-01-01   10.0          10.0   10.0   10.0
1 2026-01-02    NaN          20.0   10.0   40.0
2 2026-01-03    NaN          30.0   10.0   40.0
3 2026-01-04   40.0          40.0   40.0   40.0
4 2026-01-05   50.0          50.0   50.0   50.0
```

보간은 결측 구간의 값을 추정해서 채우는 방식입니다. 시계열 분석에서는 선형 보간이 자주 쓰이지만, 보간이 항상 정답은 아니므로 데이터 특성에 맞게 선택해야 합니다.

### 결측 패턴 시각화

조인 후 결측치가 어디에 얼마나 있는지 시각적으로 확인하면 패턴을 빠르게 파악할 수 있습니다.

```python
import pandas as pd
import numpy as np

users = pd.DataFrame({"uid": [1, 2, 3, 4, 5], "name": ["a", "b", "c", "d", "e"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})

merged = users.merge(orders, on="uid", how="left")

# 결측 여부를 0/1로 변환
missing_map = merged.isnull().astype(int)
print(missing_map)

# 열별 결측 비율
print(merged.isnull().mean())
```

**예상 출력:**

```text
   uid  name  amount
0    0     0       0
1    0     0       0
2    0     0       0
3    0     0       1
4    0     0       1

uid       0.0
name      0.0
amount    0.4
dtype: float64
```

결측 비율을 먼저 보면 조인이 제대로 됐는지 감을 잡을 수 있습니다. 예상보다 결측이 많다면 키 관계나 조인 방식을 다시 점검해야 합니다.

### 실무 예제: 고객-주문 병합

실무에서 가장 자주 마주치는 패턴은 고객 테이블과 주문 테이블을 합치는 것입니다.

```python
import pandas as pd

customers = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "tier": ["Gold", "Silver", "Gold"],
})

orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "customer_id": [1, 1, 2, 3],
    "amount": [100, 150, 80, 200],
})

# 주문 총액 계산
order_sum = orders.groupby("customer_id").agg(
    total_amount=("amount", "sum"),
    order_count=("order_id", "count"),
)

# 고객 정보와 병합
result = customers.merge(order_sum, on="customer_id", how="left")
result["total_amount"] = result["total_amount"].fillna(0)
result["order_count"] = result["order_count"].fillna(0)
print(result)
```

**예상 출력:**

```text
   customer_id     name    tier  total_amount  order_count
0            1    Alice    Gold         250.0          2.0
1            2      Bob  Silver          80.0          1.0
2            3  Charlie    Gold         200.0          1.0
```

이 패턴은 고객별 KPI를 만들 때 기본이 됩니다. 주문 테이블을 먼저 그룹화해 집계한 다음, 고객 테이블과 병합하면 고객 수준의 통계를 얻을 수 있습니다.

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

병합은 데이터를 이어 붙이는 기술이 아니라 데이터 관계를 검증하는 기술입니다. 키와 행 수를 함께 보아야 조인이 안전해집니다. 다음 글에서는 시간 축이 붙은 데이터를 다루는 시계열 작업을 다루겠습니다.

## 처음 질문으로 돌아가기

- **왜 Pandas에는 `merge`와 `join`이 둘 다 있을까요?**
  - 본문의 기준은 병합과 조인를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **안쪽, 왼쪽, 오른쪽, 바깥쪽, 교차 조인은 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **중복 키가 있을 때 왜 행 수가 갑자기 늘어날까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Merge, Join, SQL, Beginner
