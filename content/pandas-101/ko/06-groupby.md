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

이번 글에서는 `groupby`를 SQL 문법의 대응물로만 보지 않고, 분할하고 적용한 뒤 다시 결합하는 분석 패턴으로 이해해 보겠습니다.

![Pandas 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/06/06-01-concept-at-a-glance.ko.png)
*Pandas 101 6장 흐름 개요*
> **집계는 분할의 선택으로 시작**합니다. 같은 데이터프레임을 고객별, 날짜별, 지역별로 묶으면 전혀 다른 지표가 나옵니다.

## 먼저 던지는 질문

- `groupby`는 어떤 흐름으로 동작할까요?
- 집계, 변환, 필터는 왜 서로 다른 얼굴일까요?
- 여러 통계를 한 번에 계산할 때는 어떻게 쓰는 편이 좋을까요?

## 왜 중요한가

집계는 분석의 중심입니다. `groupby`를 제대로 쓰면 반복문 수십 줄이 한 줄로 줄어들 뿐 아니라, 계산 의도도 함께 선명해집니다. 비즈니스 지표, 코호트 분석, 특징 생성이 모두 여기서 이어집니다.

## 핵심 용어

- 그룹화: 특정 키를 기준으로 데이터를 여러 묶음으로 나누는 일입니다.
- 집계: 그룹마다 하나의 값을 남기는 계산입니다.
- 변환: 그룹 계산 결과를 원본 길이에 맞춰 되돌리는 방식입니다.
- 필터: 그룹 단위 조건으로 행을 남기거나 버리는 방식입니다.
- **인덱스화 여부**: 그룹 키를 결과 인덱스로 둘지 결정하는 설정입니다.
- 분할-적용-결합: 데이터를 그룹으로 나누고, 계산을 적용한 뒤, 다시 하나의 표로 합치는 패턴입니다.

## 전과 후

이전 관점: 카테고리별 합계를 반복문으로 직접 계산합니다.

이후 관점: 기준 열로 나눈 뒤 요약 규칙을 한 번에 선언합니다.

## 실습: 다섯 단계로 그룹화하기

### 1단계 - 데이터 준비하기

```python
import pandas as pd
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "month": ["Jan", "Feb", "Jan", "Feb"],
    "sales": [100, 120, 80, 95],
})
```

작은 예제지만 `groupby`의 기본 감각을 잡기에는 충분합니다. 어떤 열을 기준으로 묶을지 먼저 정하는 것이 출발점입니다.

### 2단계 - 합계 구하기

```python
print(df.groupby("city")["sales"].sum())
```
단순 합계만 보더라도 split과 combine이 이미 동작한다는 사실을 확인할 수 있습니다. 더 복잡한 통계로 가기 전에, 묶은 결과가 머릿속 계산과 맞는지 먼저 점검하는 습관이 중요합니다.

**예상 출력:**

```text
city
Busan    175
Seoul    220
Name: sales, dtype: int64
```

가장 기본적인 그룹화입니다. 도시별로 묶은 뒤 매출 열의 합계를 계산합니다. 이 한 줄이 `groupby`의 가장 단순한 얼굴입니다.

### groupby 집계 함수 비교

다음 표는 자주 사용하는 집계 함수의 반환 형태와 용도를 정리한 것입니다.

| 함수 | 반환 형태 | 용도 |
|---|---|---|
| `mean()` | 그룹당 한 값 | 그룹 평균 계산 |
| `sum()` | 그룹당 한 값 | 그룹 합계 계산 |
| `count()` | 그룹당 한 값 | 그룹 행 수 계산 |
| `agg()` | 그룹당 한 행 | 여러 통계를 동시에 계산 |
| `transform()` | 원본 행 수 유지 | 그룹 통계를 원본 길이에 맞춰 복원 |
| `apply()` | 가변 | 그룹마다 임의 함수 적용 |

집계 함수는 그룹당 하나의 값을 만들지만, `transform`은 원본 행 수를 유지한 채 그룹 통계를 되돌려 준다는 점이 가장 큰 차이입니다. 특징 생성에는 `transform`이 훨씬 자주 쓰입니다.

### 3단계 - 여러 통계 한 번에 계산하기

```python
print(df.groupby("city").agg(
    total=("sales", "sum"),
    mean=("sales", "mean"),
    n=("sales", "count"),
))
```

이름 붙은 집계를 쓰면 출력 열 이름을 제어할 수 있어 결과 표가 훨씬 읽기 쉬워집니다. 실무에서는 이 패턴을 가장 많이 씁니다.

### 4단계 - 원본 모양을 유지한 채 계산 붙이기

```python
df["share"] = df["sales"] / df.groupby("city")["sales"].transform("sum")
print(df)
```

`transform`은 원본 행 수를 유지한 채 그룹 정보를 되돌려 준다는 점이 핵심입니다. 그래서 각 도시 안에서 자기 매출 비중이 얼마인지 같은 특징을 바로 붙일 수 있습니다.

**예상 출력:**

```text
    city month  sales     share
0  Seoul   Jan    100  0.454545
1  Seoul   Feb    120  0.545455
2  Busan   Jan     80  0.457143
3  Busan   Feb     95  0.542857
```

`transform`은 그룹별 계산 결과를 원본 행 수에 맞춰 되돌려 줍니다. 그래서 비율, 평균 대비 편차, 표준화 같은 특징 생성에 잘 맞습니다.

### 다중 컬럼 groupby와 agg

실무에서는 여러 키로 묶고 여러 열에 대해 각기 다른 통계를 계산해야 할 때가 많습니다.

```python
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "category": ["A", "B", "A", "B"],
    "sales": [100, 120, 80, 95],
    "visits": [50, 60, 40, 45],
})

result = df.groupby(["city", "category"]).agg(
    total_sales=("sales", "sum"),
    avg_sales=("sales", "mean"),
    total_visits=("visits", "sum"),
)
print(result)
```

**예상 출력:**

```text
               total_sales  avg_sales  total_visits
city  category
Busan A                 80       80.0            40
      B                 95       95.0            45
Seoul A                100      100.0            50
      B                120      120.0            60
```

여러 컬럼으로 묶으면 결과 인덱스가 계층형 인덱스가 됩니다. `reset_index()`를 호출하면 인덱스를 열로 풀어 평평한 표로 바꿀 수 있습니다. 이 패턴은 복잡한 비즈니스 리포트에서 매우 자주 등장합니다.

```python
print(result.reset_index())
```

**예상 출력:**

```text
    city category  total_sales  avg_sales  total_visits
0  Busan        A           80       80.0            40
1  Busan        B           95       95.0            45
2  Seoul        A          100      100.0            50
3  Seoul        B          120      120.0            60
```

계층 인덱스를 그대로 두면 `.loc[]`으로 그룹을 선택하기 편하지만, 다른 표와 조인할 때는 평평한 형태가 더 안전합니다. 상황에 맞게 선택하세요.

### 5단계 - 그룹 조건으로 걸러내기

```python
big = df.groupby("city").filter(lambda g: g["sales"].sum() > 200)
print(big)
```

`filter`는 그룹 전체가 조건을 만족할 때 그 그룹의 행을 남깁니다. 개별 행 조건이 아니라 그룹 수준 조건이라는 점이 핵심입니다.

### groupby 성능 팁

그룹화는 분석의 핵심이지만, 데이터가 커지면 병목이 되기 쉬운 연산이기도 합니다. 다음 팁은 groupby 성능을 개선하는 데 도움이 됩니다.

#### 1. 카테고리 타입 활용

그룹 키 열의 고유값이 적다면 카테고리 타입으로 바꾸면 메모리와 속도가 개선됩니다.

```python
df["city"] = df["city"].astype("category")
print(df.groupby("city")["sales"].sum())
```

카테고리 타입은 내부적으로 정수 코드로 저장하므로 문자열 비교보다 빠릅니다. 특히 그룹 수가 적고 데이터가 클 때 효과가 큽니다.

#### 2. 불필요한 열 제거

집계하기 전에 필요한 열만 선택하면 불필요한 계산을 줄일 수 있습니다.

```python
# 느림: 모든 열을 그룹화
df.groupby("city").mean()

# 빠름: 필요한 열만 집계
df.groupby("city")["sales"].mean()
```

#### 3. apply 대신 내장 함수 우선

`apply`는 느립니다. 가능하면 내장 집계 함수나 `agg`를 먼저 검토하세요.

```python
# 느림
df.groupby("city").apply(lambda g: g["sales"].sum())

# 빠름
df.groupby("city")["sales"].sum()
```

#### 4. sort=False 옵션

결과 정렬이 필요 없다면 `sort=False`를 전달해 정렬 비용을 제거할 수 있습니다.

```python
df.groupby("city", sort=False)["sales"].sum()
```

이 네 가지 팁만 기억해도 groupby 속도를 눈에 띄게 개선할 수 있습니다. 특히 카테고리 타입과 열 선택은 코드 한 줄로 큰 차이를 만들 수 있는 실용적인 방법입니다.

### 실무 예제: 코호트 분석

그룹화는 코호트 분석처럼 실무 분석의 핵심입니다.

```python
import pandas as pd

# 사용자 가입 데이터
df = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_month": ["2026-01", "2026-01", "2026-02", "2026-02", "2026-03"],
    "purchase_month": ["2026-02", "2026-03", "2026-02", "2026-04", "2026-03"],
    "amount": [100, 150, 80, 200, 120],
})

# 가입 월별 평균 구매액
cohort = df.groupby("signup_month").agg(
    users=("user_id", "count"),
    avg_amount=("amount", "mean"),
    total_amount=("amount", "sum"),
)
print(cohort)
```

**예상 출력:**

```text
              users  avg_amount  total_amount
signup_month                                  
2026-01           2       125.0           250
2026-02           2       140.0           280
2026-03           1       120.0           120
```

코호트 분석은 같은 시점에 가입한 사용자 그룹의 행동을 추적하는 방법입니다. 가입 월별로 묶어 평균 구매액을 비교하면 어느 시점 사용자가 더 가치 있는지 파악할 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `agg`는 그룹당 한 행을 만들고 `transform`은 원본 모양을 유지합니다.
- 이름 붙은 집계는 결과 열 이름을 읽기 좋게 만듭니다.
- `filter`는 참과 거짓을 반환하는 함수가 아니라 행을 남기는 도구입니다.

## 자주 하는 실수 다섯 가지

1. `agg`와 `transform`의 결과 모양 차이를 혼동합니다.
2. `as_index=False`를 의식하지 않아 예상 밖 인덱스를 만납니다.
3. `reset_index()`를 빼먹어 다음 조인이 불편해집니다.
4. 여러 키 그룹화에서 대괄호 문법을 놓칩니다.
5. `apply`를 남용해 속도와 가독성을 함께 잃습니다.

## 실무에서는 이렇게 이어집니다

세그먼트 분석, 유지율 계산, 월별 지표 집계처럼 `groupby`는 사실상 비즈니스 인텔리전스의 기본 엔진입니다. 특히 `transform`은 그룹 평균 대비 점수나 그룹 내 비중 같은 특징을 만들 때 자주 쓰입니다.

## 실무에서는 이렇게 생각합니다

- 먼저 `agg`를 생각하고 `apply`는 마지막에 검토합니다.
- 출력 열 이름은 이름 붙은 집계로 명확하게 만듭니다.
- 특징 생성에는 `transform`을 적극적으로 씁니다.
- 여러 키 그룹화는 복합 키 인덱스처럼 다룹니다.
- 그룹 키를 인덱스로 둘지 열로 둘지 의도적으로 결정합니다.

## 체크리스트

- [ ] 분할, 적용, 결합 모델을 설명할 수 있습니다.
- [ ] 집계, 변환, 필터의 차이를 이해하고 있습니다.
- [ ] 이름 붙은 집계를 사용할 수 있습니다.
- [ ] 여러 키 기준 그룹화를 할 수 있습니다.

## 연습 문제

1. 카테고리별 평균과 표준편차를 이름 붙은 집계로 출력해 보세요.
2. 그룹 평균을 원본 데이터프레임에 다시 붙여 보세요.
3. 합계가 특정 기준을 넘는 그룹만 `filter`로 남겨 보세요.

## 정리와 다음 글

`groupby`는 분석 결과를 만드는 핵심 동력입니다. 데이터를 묶고, 계산하고, 다시 표로 되돌리는 감각을 익혀 두면 이후의 지표 계산이 훨씬 빨라집니다. 다음 글에서는 여러 표를 하나로 합치는 병합과 조인을 다루겠습니다.

## 처음 질문으로 돌아가기

- **`groupby`는 어떤 흐름으로 동작할까요?**
  - `groupby`는 데이터를 기준 키로 나누고, 각 그룹에 계산을 적용한 뒤, 결과를 다시 하나의 표로 결합하는 split-apply-combine 흐름으로 동작합니다. `df.groupby("city")["sales"].sum()` 예제는 도시별로 나눈 뒤 합계를 계산하고 시리즈로 다시 모으는 가장 기본적인 형태입니다.
- **집계, 변환, 필터는 왜 서로 다른 얼굴일까요?**
  - 집계는 그룹당 한 값을 남기고, 변환은 그룹 계산 결과를 원본 길이에 맞춰 되돌리며, 필터는 그룹 전체를 남길지 버릴지 결정합니다. 본문에서 `agg(total=("sales", "sum"))`, `transform("sum")`, `filter(lambda g: g["sales"].sum() > 200)`를 따로 보여 준 이유가 바로 결과 모양과 쓰임이 다르기 때문입니다.
- **여러 통계를 한 번에 계산할 때는 어떻게 쓰는 편이 좋을까요?**
  - 이름 붙은 집계를 써서 `total`, `mean`, `n`처럼 결과 열 이름을 명시하는 편이 가장 읽기 좋습니다. `df.groupby("city").agg(total=("sales", "sum"), mean=("sales", "mean"), n=("sales", "count"))` 패턴은 여러 통계를 한 번에 계산하면서도 다음 단계 조인과 리포트에 바로 쓰기 좋습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- **그룹화와 집계 (현재 글)**
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas — agg](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.agg.html)
- [pandas — transform](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.transform.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, GroupBy, Aggregation, DataAnalysis, Beginner
