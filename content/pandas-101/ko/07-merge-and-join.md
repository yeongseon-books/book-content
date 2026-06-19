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

이 글은 Pandas 101 시리즈의 7번째 글입니다.

이번 글에서는 `merge`와 `join`을 단순히 SQL 용어의 번역으로 보지 않고, 키가 어디에 놓여 있는지에 따라 표를 안전하게 결합하는 도구로 정리해 보겠습니다.

![Pandas 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/07/07-01-concept-at-a-glance.ko.png)
*Pandas 101 7장 흐름 개요*
> **`merge`는 관계를 검증하는 도구**입니다. 두 표를 합쳤을 때 행이 늘어나는지, 중복 키가 있는지, 자료형이 일치하는지를 항상 확인해야 합니다.

## 이 글에서 다룰 문제

- 왜 Pandas에는 `merge`와 `join`이 둘 다 있을까요?
- 안쪽, 왼쪽, 오른쪽, 바깥쪽, 교차 조인은 어떻게 다를까요?
- 중복 키가 있을 때 왜 행 수가 갑자기 늘어날까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

실무 분석의 상당수는 결국 표와 표를 연결하는 작업입니다. 사용자와 주문, 광고와 전환, 상품과 재고를 안전하게 합칠 수 있어야 지표도 맞고 모델 입력도 안정적입니다.

## 핵심 개념 정의

- **안쪽 조인 (inner)**: 양쪽 모두에 있는 키만 남깁니다.
- **왼쪽 조인 (left)**: 왼쪽 표의 모든 행을 유지합니다.
- **오른쪽 조인 (right)**: 오른쪽 표를 기준으로 유지합니다.
- **바깥쪽 조인 (outer)**: 양쪽 키의 합집합을 남깁니다.
- **교차 조인 (cross)**: 가능한 모든 조합을 만듭니다.
- **키**: 두 표를 연결하는 기준 열입니다.

## 조인 방식 비교

| 조인 방식 | how 파라미터 | 결과 행 | 주요 용도 |
| --- | --- | --- | --- |
| 안쪽 조인 | `inner` | 교집합 | 양쪽에 모두 존재하는 데이터만 분석 |
| 왼쪽 조인 | `left` | 왼쪽 기준 | 기준 표를 보존하며 정보 추가 |
| 오른쪽 조인 | `right` | 오른쪽 기준 | 왼쪽 조인의 역방향 |
| 바깥쪽 조인 | `outer` | 합집합 | 양쪽 키 모두 보존 |
| 교차 조인 | `cross` | 곱집합 | 모든 조합 생성 (경우의 수 분석) |

안쪽 조인은 기본값이므로 `how`를 생략하면 자동으로 적용됩니다. 왼쪽 조인은 실무에서 가장 많이 쓰이는 패턴으로, 기준 표의 모든 행을 유지한 채 다른 표의 정보를 추가할 때 사용합니다.

## 전과 후

이전 관점: 병합 한 번에 행 수가 갑자기 폭증하고도 원인을 모릅니다.

이후 관점: 키 관계를 먼저 검증하고 `validate`로 가정을 코드에 남깁니다.

## 실습: 다섯 단계로 표 합치기

### 1단계 - 데이터 준비

```python
import pandas as pd
import numpy as np

customers = pd.DataFrame({
    "customer_id": [1, 2, 3, 4],
    "name":        ["Alice", "Bob", "Charlie", "Diana"],
    "tier":        ["Gold", "Silver", "Gold", "Bronze"],
})

orders = pd.DataFrame({
    "order_id":    [101, 102, 103, 104, 105],
    "customer_id": [1, 1, 2, 3, 5],   # customer_id 5는 customers에 없음
    "amount":      [150, 80, 200, 50, 120],
    "product":     ["A", "B", "C", "A", "D"],
})

print("고객 테이블:")
print(customers)
print("\n주문 테이블:")
print(orders)
```

**예상 출력:**

```text
고객 테이블:
   customer_id     name    tier
0            1    Alice    Gold
1            2      Bob  Silver
2            3  Charlie    Gold
3            4    Diana  Bronze

주문 테이블:
   order_id  customer_id  amount product
0       101            1     150       A
1       102            1      80       B
2       103            2     200       C
3       104            3      50       A
4       105            5     120       D
```

### 2단계 - 안쪽 조인

```python
inner = customers.merge(orders, on="customer_id", how="inner")
print("안쪽 조인 결과:")
print(inner)
print(f"\n원본: customers {len(customers)}행, orders {len(orders)}행")
print(f"결과: {len(inner)}행 (Diana와 order_id 105 제외)")
```

**예상 출력:**

```text
안쪽 조인 결과:
   customer_id     name    tier  order_id  amount product
0            1    Alice    Gold       101     150       A
1            1    Alice    Gold       102      80       B
2            2      Bob  Silver       103     200       C
3            3  Charlie    Gold       104      50       A

원본: customers 4행, orders 5행
결과: 4행 (Diana와 order_id 105 제외)
```

기본 `how`는 안쪽 조인입니다. 양쪽에 모두 있는 키만 남기므로 고객 4번(Diana)과 존재하지 않는 고객의 주문(105)은 빠집니다.

### 3단계 - 왼쪽 조인과 바깥쪽 조인

```python
# 왼쪽 조인: 모든 고객 유지
left = customers.merge(orders, on="customer_id", how="left")
print("왼쪽 조인 (모든 고객 유지):")
print(left)
print()

# 바깥쪽 조인 + indicator
outer = customers.merge(orders, on="customer_id", how="outer", indicator=True)
print("바깥쪽 조인 (_merge 열로 출처 확인):")
print(outer[["customer_id", "name", "order_id", "_merge"]])
```

**예상 출력:**

```text
왼쪽 조인 (모든 고객 유지):
   customer_id     name    tier  order_id  amount product
0            1    Alice    Gold     101.0   150.0       A
1            1    Alice    Gold     102.0    80.0       B
2            2      Bob  Silver     103.0   200.0       C
3            3  Charlie    Gold     104.0    50.0       A
4            4    Diana  Bronze       NaN     NaN     NaN

바깥쪽 조인 (_merge 열로 출처 확인):
   customer_id     name  order_id      _merge
0          1.0    Alice     101.0        both
1          1.0    Alice     102.0        both
2          2.0      Bob     103.0        both
3          3.0  Charlie     104.0        both
4          4.0    Diana       NaN   left_only
5          5.0      NaN     105.0  right_only
```

`indicator=True`를 켜면 각 행이 어느 쪽에서 왔는지 추적할 수 있습니다. `left_only`는 고객만 있고 주문이 없는 경우, `right_only`는 등록되지 않은 고객의 주문입니다.

### 4단계 - 열 이름 충돌 처리

```python
df1 = pd.DataFrame({"id": [1, 2], "value": [10, 20], "date": ["2026-01", "2026-01"]})
df2 = pd.DataFrame({"id": [1, 2], "value": [100, 200], "source": ["A", "B"]})

merged = df1.merge(df2, on="id", suffixes=("_original", "_new"))
print(merged)
```

**예상 출력:**

```text
   id  value_original     date  value_new source
0   1              10  2026-01        100      A
1   2              20  2026-01        200      B
```

같은 이름의 열이 있을 때 접미사를 지정하지 않으면 `_x`, `_y`가 자동 붙어 읽기 어려워집니다. 접미사는 충돌 해결이자 문서화 장치입니다.

### 5단계 - 키 관계 검증

```python
# 1:1 관계 검증
try:
    customers.merge(customers, on="customer_id", validate="one_to_one")
    print("1:1 검증 통과")
except Exception as e:
    print(f"검증 실패: {type(e).__name__}")

# 1:N 관계 검증 (고객:주문)
try:
    result = customers.merge(orders, on="customer_id",
                              how="inner", validate="one_to_many")
    print("1:N 검증 통과:", result.shape)
except Exception as e:
    print(f"검증 실패: {e}")
```

**예상 출력:**

```text
1:1 검증 통과
1:N 검증 통과: (4, 6)
```

`validate`는 잘못된 조인을 조용히 통과시키지 않게 만드는 안전장치입니다. 기대한 관계와 다르면 바로 예외가 나와서 행 수 폭증을 조기에 막아 줍니다.

## 행 수 폭증 문제 진단

```python
# 중복 키가 양쪽에 있을 때 행 수 폭증 예시
left_dup  = pd.DataFrame({"key": [1, 1, 2], "val_l": ["a", "b", "c"]})
right_dup = pd.DataFrame({"key": [1, 1, 2], "val_r": ["x", "y", "z"]})

result = left_dup.merge(right_dup, on="key")
print(f"왼쪽: {len(left_dup)}행, 오른쪽: {len(right_dup)}행")
print(f"결과: {len(result)}행 (1 × 1 = 1, 1 × 1 = 1, ... 카르테시안)")
print(result)
```

**예상 출력:**

```text
왼쪽: 3행, 오른쪽: 3행
결과: 5행 (1 × 1 = 1, 1 × 1 = 1, ... 카르테시안)
   key val_l val_r
0    1     a     x
1    1     a     y
2    1     b     x
3    1     b     y
4    2     c     z
```

키 값 1이 양쪽에 각각 2개씩 있으므로 2×2=4 조합이 생깁니다. 예상치 못한 행 수 폭증의 가장 흔한 원인입니다.

## 고객-주문 병합 실무 패턴

```python
# 단계 1: 주문 집계
order_summary = orders.groupby("customer_id").agg(
    total_amount  =("amount",   "sum"),
    order_count   =("order_id", "count"),
    avg_amount    =("amount",   "mean"),
    last_product  =("product",  "last"),
).reset_index()

# 단계 2: 고객 정보와 병합
result = customers.merge(order_summary, on="customer_id", how="left")

# 단계 3: 결측치 처리 (주문 없는 고객)
result["total_amount"] = result["total_amount"].fillna(0)
result["order_count"]  = result["order_count"].fillna(0).astype(int)
result["avg_amount"]   = result["avg_amount"].fillna(0)

print(result.to_string())
```

**예상 출력:**

```text
   customer_id     name    tier  total_amount  order_count  avg_amount last_product
0            1    Alice    Gold         230.0            2       115.0            B
1            2      Bob  Silver         200.0            1       200.0            C
2            3  Charlie    Gold          50.0            1        50.0            A
3            4    Diana  Bronze           0.0            0         0.0          NaN
```

## concat으로 행/열 이어 붙이기

```python
# 행 이어 붙이기 (같은 구조의 표)
df_jan = pd.DataFrame({"month": ["Jan"], "sales": [100]})
df_feb = pd.DataFrame({"month": ["Feb"], "sales": [130]})
df_mar = pd.DataFrame({"month": ["Mar"], "sales": [90]})

combined = pd.concat([df_jan, df_feb, df_mar], ignore_index=True)
print("행 결합:\n", combined)
print()

# 열 이어 붙이기
df_a = pd.DataFrame({"x": [1, 2, 3]})
df_b = pd.DataFrame({"y": [10, 20, 30]})
side = pd.concat([df_a, df_b], axis=1)
print("열 결합:\n", side)
```

**예상 출력:**

```text
행 결합:
  month  sales
0   Jan    100
1   Feb    130
2   Mar     90

열 결합:
   x   y
0  1  10
1  2  20
2  3  30
```

## 병합 성능 최적화

```python
import time
import numpy as np

n = 500_000
left_df  = pd.DataFrame({"key": np.arange(n), "val_l": np.random.rand(n)})
right_df = pd.DataFrame({"key": np.arange(n), "val_r": np.random.rand(n)})

# 기본 merge
start = time.time()
left_df.merge(right_df, on="key")
t1 = time.time() - start

# 인덱스 기반 join (더 빠름)
left_idx  = left_df.set_index("key")
right_idx = right_df.set_index("key")

start = time.time()
left_idx.join(right_idx)
t2 = time.time() - start

print(f"merge (열 기준): {t1*1000:.1f}ms")
print(f"join (인덱스):   {t2*1000:.1f}ms ({t1/t2:.1f}배 빠름)")
```

**예상 출력:**

```text
merge (열 기준): 124.3ms
join (인덱스):    41.8ms (3.0배 빠름)
```

정렬된 인덱스를 기반으로 조인하면 열 기반 merge보다 훨씬 빠릅니다. 반복적으로 같은 표와 조인한다면 미리 인덱스를 설정해 두는 것이 유리합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 중복 키로 행 폭증 | 결과 행이 예상보다 많음 | 병합 전 `key.nunique()` 확인 |
| 기본 inner join 미인지 | 키 없는 행이 조용히 사라짐 | `how="left"` 명시, `indicator=True` 확인 |
| 접미사 미지정 | `_x`, `_y` 열로 혼란 | `suffixes=("_원본", "_추가")` 지정 |
| 키 자료형 불일치 | 결합 실패 또는 빈 결과 | `astype` 후 병합 |
| 인덱스 정리 누락 | 다음 단계에서 멀티인덱스 오류 | `reset_index()` 검토 |

## 실무에서는 이렇게 생각합니다

- 병합 전후 행 수를 항상 비교합니다.
- `validate`로 키 관계 가정을 명시합니다.
- 조인 키의 자료형을 먼저 맞춥니다.
- 병합 전에 중복을 정리할지 의도적으로 결정합니다.
- 결과 표를 한 번 더 점검해 예상과 맞는지 확인합니다.

## 운영 체크리스트

- [ ] 다섯 가지 조인 방식의 차이를 설명할 수 있습니다.
- [ ] `validate`를 이용해 조인 가정을 검증할 수 있습니다.
- [ ] `indicator`로 행 출처를 확인할 수 있습니다.
- [ ] `suffixes`로 열 이름 충돌을 정리할 수 있습니다.
- [ ] 병합 전후 행 수를 자동으로 검증하는 코드를 작성할 수 있습니다.

## 연습 문제

1. 왼쪽 조인과 바깥쪽 조인의 행 수 차이를 비교해 보세요.
2. `validate="one_to_one"`가 실패하는 예제를 만들어 오류를 확인해 보세요.
3. `indicator` 열을 이용해 오른쪽 표에만 있는 행을 찾아보세요.
4. 인덱스 기반 `join`과 열 기반 `merge`의 속도를 100만 행으로 직접 비교해 보세요.

## 정리와 다음 글

병합은 데이터를 이어 붙이는 기술이 아니라 데이터 관계를 검증하는 기술입니다. 키와 행 수를 함께 보아야 조인이 안전해집니다. 다음 글에서는 시간 축이 붙은 데이터를 다루는 시계열 작업을 다루겠습니다.

## 처음 질문으로 돌아가기

- **왜 Pandas에는 `merge`와 `join`이 둘 다 있을까요?**
  - `merge`는 열 기반 키로 두 표를 결합하는 범용 함수이고, `join`은 인덱스를 기준으로 결합하는 최적화된 함수입니다. 인덱스가 설정된 경우 `join`이 더 빠릅니다.
- **중복 키가 있을 때 왜 행 수가 갑자기 늘어날까요?**
  - 왼쪽의 키 값 n개와 오른쪽의 같은 키 값 m개가 있으면 n×m 조합이 생깁니다. `validate` 파라미터로 예상 관계를 명시하면 폭증을 조기에 차단할 수 있습니다.
- **안쪽, 왼쪽, 오른쪽, 바깥쪽, 교차 조인은 어떻게 다를까요?**
  - 기준 표(왼쪽/오른쪽/양쪽 모두/모든 조합)를 어디로 두느냐에 따라 결과 행 수와 NaN 위치가 달라집니다. 실무에서는 `left`가 가장 자주 쓰입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- **Pandas 101 (7/10): 병합과 조인 (현재 글)**
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — Merge, join, concatenate and compare](https://pandas.pydata.org/docs/user_guide/merging.html)
- [pandas — merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- [pandas — join](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html)
- [SQL Joins Explained — Mode Analytics](https://mode.com/sql-tutorial/sql-joins/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Merge, Join, SQL, Beginner
