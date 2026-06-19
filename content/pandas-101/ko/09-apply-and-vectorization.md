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

Pandas를 어느 정도 쓰기 시작하면 코드가 돌아가는 것과 빠르게 도는 것이 전혀 다른 문제라는 사실을 곧 만나게 됩니다. 특히 `apply(axis=1)`는 편해 보여서 자주 손이 가지만, 데이터가 커지는 순간 병목이 되기 쉽습니다. 성능 문제를 피하려면 Pandas가 잘하는 계산 방식이 무엇인지 먼저 이해해야 합니다.

이 글은 판다스 101 시리즈의 9번째 글입니다.

이번 글에서는 `apply`를 금지어처럼 다루기보다, 언제 느려지고 왜 벡터화가 Pandas의 본질인지 구조적으로 다루겠습니다.

![Pandas 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/09/09-01-concept-at-a-glance.ko.png)
*Pandas 101 9장 흐름 개요*
> **벡터화는 Pandas의 핵심 이점**입니다. `apply`에 손을 대기 전에 먼저 내장 함수, NumPy 연산, `np.where`로 충분한지 확인하세요.

## 이 글에서 다룰 문제

- 벡터화는 정확히 무엇을 뜻할까요?
- `apply`, `map`, NumPy 연산은 어떤 차이가 있을까요?
- 왜 `apply(axis=1)`가 특히 느릴까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

같은 계산도 벡터화 여부에 따라 수십 배, 수백 배 차이가 날 수 있습니다. ETL, 특징 생성, 대규모 리포트처럼 반복 계산이 많은 작업에서는 이 차이가 곧 실행 시간과 비용 차이로 이어집니다.

## 핵심 개념 정의

- **벡터화**: 명시적인 반복문 없이 배열 단위로 계산하는 방식입니다.
- **apply**: 행이나 열을 따라 파이썬 함수를 반복 적용하는 방식입니다.
- **map**: 시리즈 값마다 함수를 적용하거나 사전을 대응시키는 방식입니다.
- **np.where**: 배열 단위 조건 분기 함수입니다.
- **eval/query**: 문자열 표현식을 최적화 경로로 실행하는 방법입니다.

## 전과 후

이전 관점: 행마다 더하는 반복문이나 `apply(axis=1)`로 계산합니다.

이후 관점: 열 연산, 조건 벡터화, 매핑으로 같은 결과를 훨씬 빠르게 얻습니다.

## 실습: 다섯 단계로 성능 감각 잡기

### 1단계 - 벤치마크 데이터 만들기

```python
import numpy as np
import pandas as pd
import time

n = 1_000_000
df = pd.DataFrame({
    "a": np.arange(n, dtype="float64"),
    "b": np.arange(n, dtype="float64"),
    "category": np.random.choice(["X", "Y", "Z"], n),
})
print(df.shape)
print(df.head(3))
```

**예상 출력:**

```text
(1000000, 3)
     a    b category
0  0.0  0.0        Y
1  1.0  1.0        X
2  2.0  2.0        Z
```

백만 행 정도만 되어도 반복 계산 방식의 차이가 눈에 보입니다.

### 2단계 - 속도 비교: 반복문 vs 벡터화

```python
# 방법 1: Python 반복문
start = time.time()
result_loop = [df["a"][i] + df["b"][i] for i in range(len(df))]
t_loop = time.time() - start

# 방법 2: apply(axis=1) - 행 단위 Python 호출
start = time.time()
result_apply = df.apply(lambda r: r["a"] + r["b"], axis=1)
t_apply = time.time() - start

# 방법 3: 벡터화
start = time.time()
result_vec = df["a"] + df["b"]
t_vec = time.time() - start

# 방법 4: NumPy 직접 연산
start = time.time()
result_np = np.add(df["a"].values, df["b"].values)
t_np = time.time() - start

print(f"Python 반복문:  {t_loop:.3f}초")
print(f"apply(axis=1):  {t_apply:.3f}초")
print(f"벡터화 (Pandas): {t_vec:.4f}초")
print(f"NumPy 직접:     {t_np:.4f}초")
print()
print(f"loop vs vec:   {t_loop/t_vec:.0f}배")
print(f"apply vs vec:  {t_apply/t_vec:.0f}배")
```

**예상 출력:**

```text
Python 반복문:  1.823초
apply(axis=1):  12.450초
벡터화 (Pandas): 0.003초
NumPy 직접:     0.002초

loop vs vec:   607배
apply vs vec:  4150배
```

`apply(axis=1)`는 각 행을 파이썬 Series 객체로 변환한 뒤 함수를 호출합니다. 이 오버헤드 때문에 단순 덧셈에서도 벡터화보다 수천 배 느립니다.

### 3단계 - 조건 분기 벡터화

```python
# 나쁜 방법: apply로 조건 분기
start = time.time()
df["grade_slow"] = df["a"].apply(
    lambda x: "high" if x > 500000 else ("mid" if x > 250000 else "low")
)
t_slow = time.time() - start

# 좋은 방법: np.select
start = time.time()
conditions = [
    df["a"] > 500000,
    df["a"] > 250000,
]
choices = ["high", "mid"]
df["grade_fast"] = np.select(conditions, choices, default="low")
t_fast = time.time() - start

print(f"apply 방식:    {t_slow:.3f}초")
print(f"np.select 방식: {t_fast:.4f}초")
print(f"속도 향상: {t_slow/t_fast:.0f}배")
print()
print(df[["a", "grade_fast"]].head(5))
print(df[["a", "grade_fast"]].tail(3))
```

**예상 출력:**

```text
apply 방식:    8.234초
np.select 방식: 0.025초
속도 향상: 329배

         a grade_fast
0      0.0        low
1      1.0        low
2      2.0        low
3      3.0        low
4      4.0        low
           a grade_fast
999997  999997.0       high
999998  999998.0       high
999999  999999.0       high
```

### 4단계 - map으로 코드 값 치환

```python
# 카테고리 코드 → 이름 매핑
code_map = {"X": "Category X", "Y": "Category Y", "Z": "Category Z"}

# 나쁜 방법: apply
start = time.time()
df["cat_slow"] = df["category"].apply(lambda x: code_map.get(x, "Unknown"))
t_slow = time.time() - start

# 좋은 방법: map
start = time.time()
df["cat_fast"] = df["category"].map(code_map)
t_fast = time.time() - start

print(f"apply.get:  {t_slow:.3f}초")
print(f"map:        {t_fast:.4f}초")
print(f"속도 향상: {t_slow/t_fast:.0f}배")
print()
print(df[["category", "cat_fast"]].head(5))
```

**예상 출력:**

```text
apply.get:  0.342초
map:        0.018초
속도 향상: 19배

  category     cat_fast
0        Y   Category Y
1        X   Category X
2        Z   Category Z
3        X   Category X
4        Y   Category Y
```

`map`은 코드 값 치환처럼 원소별 대응이 분명한 작업에 잘 맞습니다. 정의되지 않은 값은 `NaN`으로 남으므로 사전 범위를 점검하는 데도 도움이 됩니다.

### 5단계 - eval로 복잡한 수식 가속

```python
large_df = pd.DataFrame(np.random.rand(500_000, 4), columns=["a", "b", "c", "d"])

# 방법 1: 일반 연산
start = time.time()
result1 = (large_df["a"] + large_df["b"]) * (large_df["c"] - large_df["d"])
t1 = time.time() - start

# 방법 2: eval
start = time.time()
result2 = large_df.eval("(a + b) * (c - d)")
t2 = time.time() - start

print(f"일반 연산: {t1:.4f}초")
print(f"eval:      {t2:.4f}초")
print(f"속도 향상: {t1/t2:.1f}배")
```

**예상 출력:**

```text
일반 연산: 0.018초
eval:      0.011초
속도 향상: 1.6배
```

`eval`은 복잡한 수식에서 중간 임시 배열을 줄여 메모리와 속도를 개선합니다. 간단한 연산에서는 큰 차이가 없지만 복잡한 수식에서 유리합니다.

## apply가 적합한 상황

모든 `apply`가 나쁜 것은 아닙니다. 다음 상황에서는 `apply`가 합리적입니다.

```python
# 1. 열 단위 apply (axis=0) - 괜찮음
df_small = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
col_stats = df_small.apply(lambda col: col.max() - col.min())
print("열별 범위:\n", col_stats)
print()

# 2. 복잡한 비즈니스 로직 (벡터화 불가)
def complex_rule(row):
    if row["a"] > 100 and row["b"] < 50:
        return "special_case_A"
    elif pd.isna(row["b"]):
        return "missing"
    else:
        return "normal"

df_logic = pd.DataFrame({"a": [150, 80, 200], "b": [30, 60, np.nan]})
df_logic["result"] = df_logic.apply(complex_rule, axis=1)
print("비즈니스 로직:\n", df_logic)
```

**예상 출력:**

```text
열별 범위:
 x    2
y    2
dtype: int64

비즈니스 로직:
     a     b         result
0  150  30.0  special_case_A
1   80  60.0          normal
2  200   NaN         missing
```

## wide ↔ long 변환

데이터 형태 변환도 빠른 내장 함수를 씁니다.

```python
# long → wide (pivot)
df_long = pd.DataFrame({
    "id":  [1, 1, 2, 2],
    "var": ["A", "B", "A", "B"],
    "val": [10, 20, 30, 40],
})
df_wide = df_long.pivot(index="id", columns="var", values="val")
print("pivot (long→wide):\n", df_wide)
print()

# wide → long (melt)
df_wide2 = pd.DataFrame({"id": [1, 2], "A": [10, 30], "B": [20, 40]})
df_long2 = df_wide2.melt(id_vars=["id"], var_name="var", value_name="val")
print("melt (wide→long):\n", df_long2)
```

**예상 출력:**

```text
pivot (long→wide):
var   A   B
id
1    10  20
2    30  40

melt (wide→long):
   id var  val
0   1   A   10
1   2   A   30
2   1   B   20
3   2   B   40
```

## 성능 선택 기준 비교

| 작업 | 느린 방법 | 빠른 방법 | 속도 차이 |
| --- | --- | --- | --- |
| 열 덧셈 | `apply(axis=1)` | `df["a"] + df["b"]` | 수천 배 |
| 조건 분기 | `apply(lambda x: ...)` | `np.where` / `np.select` | 수백 배 |
| 값 치환 | `apply(dict.get)` | `.map(dict)` | 10-50배 |
| 복잡한 수식 | 연산자 중첩 | `.eval()` | 1.5-3배 |
| 열 통계 | `apply(np.mean)` | `.mean()` | 5-20배 |
| 문자열 처리 | `apply(str.lower)` | `.str.lower()` | 5-15배 |

## str accessor로 문자열 벡터화

```python
s = pd.Series(["Hello World", "foo BAR", "  PYTHON  ", "data science"])

print(s.str.lower())         # 소문자
print()
print(s.str.strip())         # 공백 제거
print()
print(s.str.contains("o"))   # 패턴 포함 여부
print()
print(s.str.extract(r"(\w+)\s(\w+)"))  # 정규식 추출
```

**예상 출력:**

```text
0    hello world
1        foo bar
2       python
3   data science
dtype: object
...
```

`.str` accessor는 문자열 연산을 벡터화합니다. `apply(lambda x: x.lower())`보다 훨씬 빠르고 읽기 쉽습니다.

## 실전 예제: A/B 테스트 결과 분석

```python
ab_test = pd.DataFrame({
    "user_id":   range(1, 10001),
    "variant":   np.random.choice(["A", "B"], 10000),
    "converted": np.random.choice([0, 1], 10000, p=[0.85, 0.15]),
    "revenue":   np.random.choice([0, 50, 100, 200], 10000, p=[0.85, 0.08, 0.05, 0.02]),
})

# 나쁜 방법: apply로 파생 열 계산
start = time.time()
ab_test["has_revenue_slow"] = ab_test["revenue"].apply(lambda x: 1 if x > 0 else 0)
t_slow = time.time() - start

# 좋은 방법: 벡터화
start = time.time()
ab_test["has_revenue"] = (ab_test["revenue"] > 0).astype(int)
t_fast = time.time() - start

print(f"apply 방식: {t_slow*1000:.2f}ms")
print(f"벡터화:     {t_fast*1000:.3f}ms")
print()

# 집계
result = ab_test.groupby("variant").agg(
    users       =("user_id",     "count"),
    conversions =("converted",   "sum"),
    total_rev   =("revenue",     "sum"),
    avg_rev     =("revenue",     "mean"),
).round(2)

result["cvr"]  = (result["conversions"] / result["users"] * 100).round(2)
result["arpu"] = result["avg_rev"].round(2)
print("A/B 테스트 결과:\n", result)
```

**예상 출력:**

```text
A/B 테스트 결과:
         users  conversions  total_rev  avg_rev   cvr  arpu
variant
A         5032          757    17650.0     3.51  15.04  3.51
B         4968          743    17100.0     3.44  14.96  3.44
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `apply(axis=1)` 기본 사용 | 수천 배 느린 실행 | 열 연산, `np.where`, `np.select`로 대체 |
| Python 반복문으로 열 계산 | 메모리 낭비, 느림 | 벡터화 연산 사용 |
| `apply(dict.get)` 패턴 | `map`보다 20배 느림 | `.map(dict)` 사용 |
| `map`에서 생긴 NaN 미확인 | 후속 연산 오류 | `.map(dict).fillna("기본값")` |
| 자료형 불일치로 벡터화 실패 | object 타입으로 전환 | `astype` 후 연산 |

## 실무에서는 이렇게 생각합니다

- 먼저 벡터화 가능성을 확인합니다.
- 벡터화가 불가능할 때만 `apply`를 검토합니다.
- 가능하면 `axis=1`은 피합니다.
- 계산 전 자료형을 맞춥니다.
- 실제 병목을 측정한 뒤 최적화합니다.

## 운영 체크리스트

- [ ] 벡터화와 `apply`의 차이를 설명할 수 있습니다.
- [ ] `np.where`와 `np.select`로 조건 분기를 작성할 수 있습니다.
- [ ] `map`으로 코드 값을 치환할 수 있습니다.
- [ ] `axis=1` 적용 함수가 느린 이유를 알고 있습니다.
- [ ] `str` accessor로 문자열 연산을 벡터화할 수 있습니다.

## 연습 문제

1. 벡터화된 덧셈과 `apply(axis=1)`의 실행 시간을 100만 행으로 비교해 보세요.
2. 세 단계 조건을 `np.where` 중첩 대신 `np.select`로 표현해 보세요.
3. 국가 코드를 국가 이름으로 바꾸는 매핑을 `map`으로 작성하고, 미등록 코드가 NaN으로 처리되는지 확인해 보세요.
4. `.str.lower()`, `.str.strip()`, `.str.contains()`를 적용하고 각 결과를 출력해 보세요.

## 정리와 다음 글

벡터화는 Pandas의 성능과 문법을 함께 이해하는 핵심입니다. 행마다 함수를 부르기보다 열 단위 계산으로 넘기는 감각을 익히면 코드가 더 짧고 빠르고 읽기 쉬워집니다. 다음 글에서는 지금까지 배운 내용을 하나의 실전 분석 흐름으로 묶어 보겠습니다.

## 처음 질문으로 돌아가기

- **벡터화는 정확히 무엇을 뜻할까요?**
  - Python 반복문 없이 NumPy의 C 수준 배열 연산을 활용해 전체 열을 한 번에 처리하는 방식입니다.
- **`apply`, `map`, NumPy 연산은 어떤 차이가 있을까요?**
  - `apply`는 Python 함수를 원소/행에 반복 적용(느림), `map`은 Series 원소를 사전/함수로 1:1 변환(보통), NumPy 연산은 C 수준 배열 연산(가장 빠름)입니다.
- **왜 `apply(axis=1)`가 특히 느릴까요?**
  - 각 행을 독립적인 Series 객체로 변환하고 Python 함수를 호출하는 오버헤드가 매 행마다 발생하기 때문입니다. 100만 행에서는 수천 배 차이가 납니다.

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
- **Pandas 101 (9/10): 적용 함수와 벡터화 (현재 글)**
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [pandas — apply](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [NumPy — Universal functions](https://numpy.org/doc/stable/reference/ufuncs.html)
- [Real Python — Fast, Flexible, Easy and Intuitive Pandas](https://realpython.com/fast-flexible-pandas/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Vectorization, Performance, Apply, Beginner
