---
series: pandas-101
episode: 6
title: "Pandas 101 (6/10): 그룹화와 집계"
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
  - GroupBy
  - Aggregation
  - DataAnalysis
  - Beginner
seo_description: groupby 분할-적용-결합 모델을 이해합니다. 집계, 변환, 필터의 차이와 실무에서 자주 쓰이는 특징 생성 패턴, 최적화 전략을 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (6/10): 그룹화와 집계

분석이 표를 읽는 단계에서 끝나는 경우는 거의 없습니다. 결국은 도시별 매출, 사용자군별 전환율, 월별 지표처럼 어떤 기준으로 묶고 요약해야 의미가 생깁니다. 그래서 `groupby`는 Pandas의 옵션 하나가 아니라 분석 자체를 움직이는 핵심 축에 가깝습니다.

이 글은 Pandas 101 시리즈의 6번째 글입니다.

이번 글에서는 `groupby`를 SQL 문법의 대응물로만 보지 않고, 분할하고 적용한 뒤 다시 결합하는 분석 패턴으로 이해해 보겠습니다.

![Pandas 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/06/06-01-concept-at-a-glance.ko.png)
*Pandas 101 6장 흐름 개요*
> **집계는 분할의 선택으로 시작**합니다. 같은 데이터프레임을 고객별, 날짜별, 지역별로 묶으면 전혀 다른 지표가 나옵니다.

## 이 글에서 다룰 문제

- `groupby`는 어떤 흐름으로 동작할까요?
- 집계, 변환, 필터는 왜 서로 다른 얼굴일까요?
- 여러 통계를 한 번에 계산할 때는 어떻게 쓰는 편이 좋을까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

집계는 분석의 중심입니다. `groupby`를 제대로 쓰면 반복문 수십 줄이 한 줄로 줄어들 뿐 아니라, 계산 의도도 함께 선명해집니다.

## 핵심 개념 정의

- **그룹화**: 특정 키를 기준으로 데이터를 여러 묶음으로 나누는 일입니다.
- **집계 (agg)**: 그룹마다 하나의 값을 남기는 계산입니다.
- **변환 (transform)**: 그룹 계산 결과를 원본 길이에 맞춰 되돌리는 방식입니다.
- **필터 (filter)**: 그룹 단위 조건으로 행을 남기거나 버리는 방식입니다.
- **분할-적용-결합**: 데이터를 나누고, 계산을 적용한 뒤, 다시 하나의 표로 합치는 패턴입니다.

## 전과 후

이전 관점: 카테고리별 합계를 반복문으로 직접 계산합니다.

이후 관점: 기준 열로 나눈 뒤 요약 규칙을 한 번에 선언합니다.

## 실습: 다섯 단계로 그룹화하기

### 1단계 - 기준 데이터 준비

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "city":     ["Seoul", "Seoul", "Busan", "Busan", "Seoul", "Busan"],
    "category": ["A", "B", "A", "B", "A", "A"],
    "month":    ["Jan", "Jan", "Jan", "Feb", "Feb", "Feb"],
    "sales":    [100, 120, 80, 95, 110, 90],
    "visits":   [50, 60, 40, 45, 55, 42],
})
print(df)
```

**예상 출력:**

```text
     city category month  sales  visits
0   Seoul        A   Jan    100      50
1   Seoul        B   Jan    120      60
2   Busan        A   Jan     80      40
3   Busan        B   Feb     95      45
4   Seoul        A   Feb    110      55
5   Busan        A   Feb     90      42
```

### 2단계 - 단일 키 집계

```python
# 도시별 합계
city_total = df.groupby("city")["sales"].sum()
print("도시별 총 매출:\n", city_total)
print()

# 여러 함수 적용
city_stats = df.groupby("city")["sales"].agg(["sum", "mean", "count", "std"])
print("도시별 통계:\n", city_stats.round(1))
```

**예상 출력:**

```text
도시별 총 매출:
 city
Busan    265
Seoul    330
Name: sales, dtype: int64

도시별 통계:
         sum   mean  count   std
city
Busan    265   88.3      3   7.6
Seoul    330  110.0      3   10.0
```

### 3단계 - 이름 붙은 집계 (Named Aggregation)

```python
result = df.groupby("city").agg(
    total_sales  =("sales",  "sum"),
    avg_sales    =("sales",  "mean"),
    max_sales    =("sales",  "max"),
    order_count  =("sales",  "count"),
    total_visits =("visits", "sum"),
    conversion   =("visits", "mean"),
)
print(result.round(1))
```

**예상 출력:**

```text
       total_sales  avg_sales  max_sales  order_count  total_visits  conversion
city
Busan          265       88.3         95            3           127        42.3
Seoul          330      110.0        120            3           165        55.0
```

이름 붙은 집계를 쓰면 출력 열 이름을 제어할 수 있어 결과 표가 훨씬 읽기 쉬워집니다. 실무에서는 이 패턴을 가장 많이 씁니다.

### 4단계 - transform으로 원본 모양 유지

```python
# 각 행에 그룹 통계 붙이기
df["city_total"] = df.groupby("city")["sales"].transform("sum")
df["share"]      = df["sales"] / df["city_total"]
df["rank"]       = df.groupby("city")["sales"].rank(ascending=False)
df["z_score"]    = df.groupby("city")["sales"].transform(
    lambda x: (x - x.mean()) / x.std()
)
print(df[["city", "sales", "city_total", "share", "rank", "z_score"]].round(3))
```

**예상 출력:**

```text
     city  sales  city_total  share  rank  z_score
0   Seoul    100         330  0.303   3.0   -1.007
1   Seoul    120         330  0.364   1.0    0.877
2   Busan     80         265  0.302   3.0   -1.066
3   Busan     95         265  0.358   2.0    0.877
4   Seoul    110         330  0.333   2.0    0.131
5   Busan     90         265  0.340   2.5    0.189
```

`transform`은 원본 행 수를 유지한 채 그룹 정보를 되돌려 줍니다. 그래서 비율, 순위, z-score 같은 특징을 원본 표에 바로 붙일 수 있습니다.

### 5단계 - 다중 키 그룹화

```python
multi = df.groupby(["city", "category"]).agg(
    total=("sales",  "sum"),
    n    =("sales",  "count"),
    mean =("sales",  "mean"),
).reset_index()
print(multi)
```

**예상 출력:**

```text
     city category  total  n    mean
0   Busan        A    170  2    85.0
1   Busan        B     95  1    95.0
2   Seoul        A    210  2   105.0
3   Seoul        B    120  1   120.0
```

`reset_index()`를 호출하면 인덱스를 열로 풀어 평평한 표로 바꿀 수 있습니다. 이 패턴은 복잡한 비즈니스 리포트에서 매우 자주 등장합니다.

## groupby 집계 함수 비교

| 함수 | 반환 형태 | 행 수 | 주요 용도 |
| --- | --- | --- | --- |
| `sum()` | 그룹당 한 값 | 그룹 수 | 합계 |
| `mean()` | 그룹당 한 값 | 그룹 수 | 평균 |
| `agg()` | 그룹당 한 행 | 그룹 수 | 여러 통계 동시 계산 |
| `transform()` | 원본과 동일 | 원본 행 수 | 그룹 통계를 각 행에 붙이기 |
| `apply()` | 가변 | 가변 | 그룹마다 임의 함수 적용 |
| `filter()` | 원본 서브셋 | 조건 만족 행 수 | 그룹 단위 조건 필터링 |

집계 함수는 그룹당 하나의 값을 만들지만, `transform`은 원본 행 수를 유지한 채 그룹 통계를 되돌려 준다는 점이 가장 큰 차이입니다.

## 필터와 조건 그룹화

```python
# 총 매출 200 이상인 도시만 남기기
big_cities = df.groupby("city").filter(lambda g: g["sales"].sum() > 200)
print("매출 200 이상 도시:\n", big_cities[["city", "sales"]])
print()

# 카테고리별 필터
active_cats = df.groupby("category").filter(lambda g: len(g) >= 3)
print("3건 이상 카테고리:\n", active_cats[["category", "sales"]])
```

**예상 출력:**

```text
매출 200 이상 도시:
     city  sales
0   Seoul    100
1   Seoul    120
2   Busan     80
4   Seoul    110

카테고리별 필터:
  category  sales
0        A    100
2        A     80
4        A    110
5        A     90
```

`filter`는 개별 행 조건이 아니라 그룹 수준 조건이라는 점이 핵심입니다.

## 실전 예제: 코호트 분석

```python
cohort = pd.DataFrame({
    "user_id":       range(1, 9),
    "signup_month":  ["2026-01", "2026-01", "2026-02", "2026-02",
                      "2026-03", "2026-03", "2026-01", "2026-02"],
    "purchase_month":["2026-02", "2026-03", "2026-02", "2026-04",
                      "2026-03", "2026-04", "2026-01", "2026-03"],
    "amount":        [100, 150, 80, 200, 120, 90, 60, 110],
})

summary = cohort.groupby("signup_month").agg(
    users        =("user_id", "count"),
    avg_amount   =("amount",  "mean"),
    total_amount =("amount",  "sum"),
    max_amount   =("amount",  "max"),
).round(1)
print("가입월별 코호트 지표:\n", summary)
```

**예상 출력:**

```text
가입월별 코호트 지표:
              users  avg_amount  total_amount  max_amount
signup_month
2026-01           3      103.3         310.0       150.0
2026-02           3      130.0         390.0       200.0
2026-03           2      105.0         210.0       120.0
```

## groupby 성능 최적화

```python
import time
import numpy as np

n = 1_000_000
df_large = pd.DataFrame({
    "city":   np.random.choice(["Seoul", "Busan", "Daegu"], n),
    "sales":  np.random.randint(1000, 10000, n),
})

# 방법 1: 문자열 열 그룹화 (기본)
start = time.time()
df_large.groupby("city")["sales"].sum()
t1 = time.time() - start

# 방법 2: category 타입으로 변환 후
df_large["city_cat"] = df_large["city"].astype("category")
start = time.time()
df_large.groupby("city_cat")["sales"].sum()
t2 = time.time() - start

# 방법 3: sort=False 옵션
start = time.time()
df_large.groupby("city", sort=False)["sales"].sum()
t3 = time.time() - start

print(f"문자열 groupby: {t1*1000:.1f}ms")
print(f"category 변환:  {t2*1000:.1f}ms ({t1/t2:.1f}배 빠름)")
print(f"sort=False:     {t3*1000:.1f}ms ({t1/t3:.1f}배 빠름)")
```

**예상 출력:**

```text
문자열 groupby: 48.3ms
category 변환:  11.2ms (4.3배 빠름)
sort=False:     39.7ms (1.2배 빠름)
```

### 성능 팁 요약

```python
# 1. 불필요한 열 제거 후 집계
df.groupby("city")["sales"].sum()          # 빠름
df.groupby("city").mean()                   # 느림 (모든 열)

# 2. apply 대신 내장 함수
df.groupby("city")["sales"].sum()          # 빠름
df.groupby("city").apply(lambda g: g["sales"].sum())  # 느림

# 3. category 타입 활용
df["city"] = df["city"].astype("category")  # 메모리+속도 개선

# 4. sort 불필요 시 끄기
df.groupby("city", sort=False)["sales"].sum()
```

## 피벗 테이블과 crosstab

```python
# 피벗 테이블: groupby의 시각적 표현
pivot = df.pivot_table(
    index="city",
    columns="category",
    values="sales",
    aggfunc="sum",
    fill_value=0,
)
print("피벗 테이블:\n", pivot)
print()

# crosstab: 빈도 분석
ct = pd.crosstab(df["city"], df["category"])
print("빈도표:\n", ct)
```

**예상 출력:**

```text
피벗 테이블:
category    A    B
city
Busan     170   95
Seoul     210  120

빈도표:
category  A  B
city
Busan     2  1
Seoul     2  1
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `agg`와 `transform` 혼동 | 행 수 불일치 오류 | 원본 행 유지 필요 → `transform`, 집계 → `agg` |
| `as_index=False` 미의식 | 예상 밖 인덱스 | 다음 단계와 조인 전 `reset_index()` 확인 |
| `reset_index()` 누락 | 멀티인덱스로 조인 오류 | 집계 후 항상 `reset_index()` 검토 |
| `apply` 남용 | 매우 느린 실행 | 내장 함수로 대체 가능 여부 먼저 확인 |
| 대용량에 문자열 키 사용 | 느린 groupby | `astype("category")` 변환 |

## 실무에서는 이렇게 생각합니다

- 먼저 `agg`를 생각하고 `apply`는 마지막에 검토합니다.
- 출력 열 이름은 이름 붙은 집계로 명확하게 만듭니다.
- 특징 생성에는 `transform`을 적극적으로 씁니다.
- 여러 키 그룹화는 복합 키 인덱스처럼 다룹니다.
- 그룹 키를 인덱스로 둘지 열로 둘지 의도적으로 결정합니다.

## 운영 체크리스트

- [ ] 분할, 적용, 결합 모델을 설명할 수 있습니다.
- [ ] 집계, 변환, 필터의 차이를 이해하고 있습니다.
- [ ] 이름 붙은 집계를 사용할 수 있습니다.
- [ ] 여러 키 기준 그룹화를 할 수 있습니다.
- [ ] category 타입으로 groupby 성능을 개선할 수 있습니다.

## 연습 문제

1. 카테고리별 평균과 표준편차를 이름 붙은 집계로 출력해 보세요.
2. 그룹 평균을 원본 데이터프레임에 `transform`으로 붙여 보세요.
3. 합계가 특정 기준을 넘는 그룹만 `filter`로 남겨 보세요.
4. 100만 행 데이터에서 문자열 키와 category 키의 groupby 속도를 비교해 보세요.

## 정리와 다음 글

`groupby`는 분석 결과를 만드는 핵심 동력입니다. 데이터를 묶고, 계산하고, 다시 표로 되돌리는 감각을 익혀 두면 이후의 지표 계산이 훨씬 빨라집니다. 다음 글에서는 여러 표를 하나로 합치는 병합과 조인을 다루겠습니다.

## 처음 질문으로 돌아가기

- **`groupby`는 어떤 흐름으로 동작할까요?**
  - 분할(키 기준으로 나누기) → 적용(각 그룹에 함수 실행) → 결합(결과 합치기)의 3단계로 동작합니다.
- **집계, 변환, 필터는 왜 서로 다른 얼굴일까요?**
  - 집계는 그룹을 하나의 값으로 줄이고, 변환은 원본 행 수를 유지하며, 필터는 조건을 만족하는 그룹만 남깁니다. 결과 형태가 완전히 다릅니다.
- **여러 통계를 한 번에 계산할 때는 어떻게 쓰는 편이 좋을까요?**
  - `agg(이름=("열", "함수"))` 형태의 이름 붙은 집계를 사용하면 열 이름을 제어하면서 여러 통계를 한 번에 계산할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- **Pandas 101 (6/10): 그룹화와 집계 (현재 글)**
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — Group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas — agg](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.agg.html)
- [pandas — transform](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.transform.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, GroupBy, Aggregation, DataAnalysis, Beginner
