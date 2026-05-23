---
series: pandas-101
episode: 9
title: "Pandas 101 (9/10): 적용 함수와 벡터화"
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
  - Vectorization
  - Performance
  - Apply
  - Beginner
seo_description: 성능을 결정하는 벡터화 원리와 apply 한계 및 대안을 익힙니다. np.where, map 등 효율적인 데이터 처리 패턴을 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (9/10): 적용 함수와 벡터화

이 글은 판다스 101 시리즈의 9번째 글입니다.

Pandas를 어느 정도 쓰기 시작하면 코드가 돌아가는 것과 빠르게 도는 것이 전혀 다른 문제라는 사실을 곧 만나게 됩니다. 특히 `apply(axis=1)`는 편해 보여서 자주 손이 가지만, 데이터가 커지는 순간 병목이 되기 쉽습니다. 성능 문제를 피하려면 Pandas가 잘하는 계산 방식이 무엇인지 먼저 이해해야 합니다.

이번 글에서는 `apply`를 금지어처럼 다루기보다, 언제 느려지고 왜 벡터화가 Pandas의 본질인지 구조적으로 다루겠습니다.

![Pandas 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/09/09-01-concept-at-a-glance.ko.png)
*Pandas 101 9장 흐름 개요*
> **벡터화는 Pandas의 핵심 이점**입니다. `apply`에 손을 대기 전에 먼저 내장 함수, 리스트 컴프리헨션, NumPy 연산으로 충분한지 확인하세요.

## 먼저 던지는 질문

- 벡터화는 정확히 무엇을 뜻할까요?
- `apply`, `map`, NumPy 연산은 어떤 차이가 있을까요?
- 왜 `apply(axis=1)`가 특히 느릴까요?

## 왜 중요한가

같은 계산도 벡터화 여부에 따라 수십 배, 수백 배 차이가 날 수 있습니다. ETL, 특징 생성, 대규모 리포트처럼 반복 계산이 많은 작업에서는 이 차이가 곧 실행 시간과 클라우드 비용 차이로 이어집니다.

## 핵심 용어

- 벡터화: 명시적인 반복문 없이 배열 단위로 계산하는 방식입니다.
- **적용 함수**: 행이나 열을 따라 파이썬 함수를 반복 적용하는 방식입니다.
- **원소별 매핑**: 시리즈 값마다 함수를 적용하거나 사전을 대응시키는 방식입니다.
- **조건 선택**: 배열 단위 조건 분기입니다.
- **표현식 가속**: 큰 수식 계산을 빠르게 처리하는 방법입니다.

### reshape 함수 비교

다음 표는 Pandas의 주요 reshape 함수들이 어떻게 데이터를 변환하는지 정리한 것입니다.

| 함수 | 입력 형태 | 출력 형태 | 주요 용도 |
|---|---|---|---|
| `pivot()` | Long (id-var-value) | Wide (var as columns) | 간단한 wide 변환 |
| `melt()` | Wide (many columns) | Long (id-var-value) | Wide를 long으로 |
| `stack()` | Wide DataFrame | MultiIndex Series | 열을 인덱스로 |
| `unstack()` | MultiIndex Series/DF | Wide DataFrame | 인덱스를 열로 |
| `pivot_table()` | Long with duplicates | Wide (aggregated) | 집계를 포함한 wide |

`pivot`과 `melt`는 서로 반대 방향입니다. `pivot`는 열을 늘리고, `melt`는 열을 행으로 쌓습니다. 이 두 함수를 잘 다루면 데이터 모양을 자유롭게 변형할 수 있습니다.

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
# 매우 느림 — apply(axis=1)은 행 단위 Python 호출
```

`apply(axis=1)`는 각 행을 파이썬 객체처럼 다루며 함수를 반복 호출합니다. 문법은 간단하지만 Pandas가 가장 잘하는 계산 경로는 아닙니다.

### 3단계 - 열 단위로 계산하기

```python
df["c"] = df["a"] + df["b"]   # fastest
```

열 단위 계산은 백만 행처럼 큰 데이터에서도 같은 문법으로 유지됩니다. 실제 결과를 몇 행만 확인해도 루프 없이 전체가 한 번에 계산됐다는 감각을 잡을 수 있습니다.

**예상 출력:**

```text
   a  b  c
0  0  0  0
1  1  1  2
2  2  2  4
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

`map`은 코드 값 치환처럼 원소별 대응이 분명한 작업에 잘 맞습니다. 정의되지 않은 값은 `NaN`으로 남으므로 사전 범위를 점검하는 데도 도움이 됩니다.

**예상 출력:**

```text
0    zero
1     one
2     NaN
dtype: object
```

값 치환이나 코드 변환은 `map`이 잘 맞습니다. 모든 경우를 `apply`로 처리하려고 하면 코드도 느려지고 의도도 흐려집니다.

### crosstab 섹션

`crosstab`은 빈도를 세는 특수한 형태의 피벗 테이블입니다. 두 범주형 변수 간의 교차 빈도를 확인할 때 자주 쓰입니다.

#### 기본 예제

```python
import pandas as pd

df = pd.DataFrame({
    "gender": ["M", "F", "M", "F", "M", "F"],
    "product": ["A", "A", "B", "B", "A", "C"],
})

ct = pd.crosstab(df["gender"], df["product"])
print(ct)
```

**예상 출력:**

```text
product  A  B  C
gender          
F        1  1  1
M        2  1  0
```

`crosstab`은 각 조합의 발생 횟수를 세어 표로 만듭니다. 설문 분석, A/B 테스트 결과, 고객 세그먼트 분포를 볼 때 매우 유용합니다.

#### 비율 표시

`normalize` 옵션을 쓰면 빈도 대신 비율을 볼 수 있습니다.

```python
ct_norm = pd.crosstab(df["gender"], df["product"], normalize="index")
print(ct_norm)
```

**예상 출력:**

```text
product         A         B         C
gender                              
F        0.333333  0.333333  0.333333
M        0.500000  0.250000  0.000000
```

`normalize="index"`로 하면 행 합이 1이 되도록 비율로 바꿑니다. 각 성별 내에서 제품 선호도가 어떻게 분포하는지 비교하기 좋습니다.

#### margins 추가

`margins=True`를 쓰면 행/열 합계를 함께 볼 수 있습니다.

```python
ct_margin = pd.crosstab(df["gender"], df["product"], margins=True)
print(ct_margin)
```

**예상 출력:**

```text
product  A  B  C  All
gender              
F        1  1  1    3
M        2  1  0    3
All      3  2  1    6
```

`margins=True`는 각 행과 열의 합계를 함께 표시합니다. 전체 분포를 한눈에 보면서 비율도 쉽게 계산할 수 있습니다.

### wide ↔ long 변환 예제

reshape의 핵심은 wide와 long 형태를 자유롭게 오가는 것입니다.

#### pivot: long → wide

```python
import pandas as pd

# long 형태
df_long = pd.DataFrame({
    "id": [1, 1, 2, 2],
    "var": ["A", "B", "A", "B"],
    "val": [10, 20, 30, 40],
})

# wide 형태로 변환
df_wide = df_long.pivot(index="id", columns="var", values="val")
print(df_wide)
```

**예상 출력:**

```text
var   A   B
id         
1    10  20
2    30  40
```

`pivot`은 행 식별자, 열 이름, 값을 각각 지정해 wide 형태로 펼칩니다.

#### melt: wide → long

```python
# wide 형태
df_wide2 = pd.DataFrame({
    "id": [1, 2],
    "A": [10, 30],
    "B": [20, 40],
})

# long 형태로 변환
df_long2 = df_wide2.melt(id_vars=["id"], value_vars=["A", "B"],
                          var_name="var", value_name="val")
print(df_long2)
```

**예상 출력:**

```text
   id var  val
0   1   A   10
1   2   A   30
2   1   B   20
3   2   B   40
```

`melt`는 wide 표를 long 형태로 녹여 내립니다. 다중 열을 하나의 변수 열과 값 열로 합칠 때 사용합니다.

#### pivot_table: 집계를 포함한 wide

중복 키가 있을 때는 `pivot` 대신 `pivot_table`을 쓰면 자동으로 집계합니다.

```python
df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "category": ["A", "A", "B", "B"],
    "sales": [100, 120, 80, 95],
})

pt = df.pivot_table(index="city", columns="category", values="sales", aggfunc="sum")
print(pt)
```

**예상 출력:**

```text
category     A      B
city               
Busan      NaN  175.0
Seoul    220.0    NaN
```

`pivot_table`은 같은 키 조합이 여러 번 나와도 집계 함수로 합쳐 주므로 실무에서 매우 유용합니다.

### 실무 예제: A/B 테스트 결과 분석

벡터화와 reshape를 함께 사용하는 실무 패턴입니다.

```python
import pandas as pd

# A/B 테스트 데이터
df = pd.DataFrame({
    "user_id": range(1, 7),
    "variant": ["A", "B", "A", "B", "A", "B"],
    "converted": [1, 0, 1, 1, 0, 1],
    "revenue": [100, 0, 150, 80, 0, 120],
})

# 변형별 집계
result = df.groupby("variant").agg(
    users=("user_id", "count"),
    conversions=("converted", "sum"),
    total_revenue=("revenue", "sum"),
)

# 전환율 계산 (벡터화)
result["cvr"] = result["conversions"] / result["users"]
result["arpu"] = result["total_revenue"] / result["users"]

print(result)
```

**예상 출력:**

```text
         users  conversions  total_revenue       cvr       arpu
variant                                                         
A            3            2            250  0.666667  83.333333
B            3            2            200  0.666667  66.666667
```

이 예제는 그룹화, 벡터화, 파생 지표 계산을 한 흐름에 보여줍니다. 전환율과 사용자당 매출을 벡터화로 계산하면 코드가 간결하고 빠릅니다.

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

## 처음 질문으로 돌아가기

- **벡터화는 정확히 무엇을 뜻할까요?**
  - 벡터화는 행마다 파이썬 함수를 호출하지 않고 배열이나 열 전체를 한 번에 계산하는 방식입니다. `df["c"] = df["a"] + df["b"]` 한 줄이 백만 행 전체에 그대로 적용되는 예제가 그 의미를 가장 직접적으로 보여 줍니다.
- **`apply`, `map`, NumPy 연산은 어떤 차이가 있을까요?**
  - `apply`는 임의 함수를 반복 적용하는 범용 도구이고, `map`은 시리즈의 값 치환이나 일대일 대응에 맞으며, NumPy 연산은 조건 분기와 수치 계산을 빠르게 처리합니다. 그래서 본문도 코드 치환은 `Series.map(mapping)`으로, 짝수/홀수 분기는 `np.where(df["a"] % 2 == 0, "even", "odd")`로 풀었습니다.
- **왜 `apply(axis=1)`가 특히 느릴까요?**
  - `axis=1`은 각 행을 사실상 파이썬 객체처럼 꺼내 함수에 넘기므로 내부 최적화 경로를 거의 타지 못합니다. 같은 계산을 `df.apply(lambda r: r["a"] + r["b"], axis=1)` 대신 `df["a"] + df["b"]`로 바꿨을 때 큰 속도 차이가 나는 이유가 바로 여기에 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- **적용 함수와 벡터화 (현재 글)**
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [pandas — apply](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [NumPy — Universal functions](https://numpy.org/doc/stable/reference/ufuncs.html)
- [Real Python — Fast, Flexible, Easy and Intuitive Pandas](https://realpython.com/fast-flexible-pandas/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Vectorization, Performance, Apply, Beginner
