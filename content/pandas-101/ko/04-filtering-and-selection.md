---
series: pandas-101
episode: 4
title: "Pandas 101 (4/10): 필터링과 선택"
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
  - Filtering
  - Selection
  - Indexing
  - Beginner
seo_description: loc, iloc, 조건 마스크, query로 행과 열을 고르는 방법을 정리한 글입니다
last_reviewed: '2026-05-15'
---

# Pandas 101 (4/10): 필터링과 선택

Pandas를 익히다 보면 같은 표에서 원하는 부분을 고르는 방법이 여러 개라는 사실이 먼저 헷갈립니다. `loc`, `iloc`, 조건 마스크, `query`까지 모두 비슷해 보이지만 실제로는 의도가 다릅니다. 이 차이를 이해하지 못하면 선택 코드는 금방 읽기 어려워지고, 할당 시점에는 경고까지 따라옵니다.

이 글은 판다스 101 시리즈의 4번째 글입니다.

이번 글에서는 행과 열을 고르는 네 가지 방식을 기능 목록이 아니라 의도에 맞는 도구 상자로 정리해 보겠습니다.

![Pandas 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/04/04-01-concept-at-a-glance.ko.png)
*Pandas 101 4장 흐름 개요*
> **선택은 의도에 맞는 도구**입니다. 같은 데이터를 고르더라도 `loc`, `iloc`, 조건 마스크, `query` 중 어떤 것을 선택하느냐에 따라 코드의 명확성과 유지보수 비용이 달라집니다.

## 이 글에서 다룰 문제

- `loc`와 `iloc`는 언제 구분해서 써야 할까요?
- 조건 마스크는 어떤 상황에서 가장 자연스러울까요?
- 표현식이 길어질수록 `query`가 왜 읽기 쉬워질까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

분석은 거의 모든 단계에서 부분 집합을 뽑는 작업을 반복합니다. 느리거나 모호한 선택 코드는 이후의 집계, 조인, 시각화까지 함께 흔듭니다.

## 핵심 개념 정의

- **레이블 기반 선택**: 이름으로 행과 열을 고르는 방식입니다.
- **위치 기반 선택**: 숫자 위치로 고르는 방식입니다.
- **불리언 마스크**: 참과 거짓으로 행을 걸러내는 시리즈입니다.
- **문자열 질의**: 문자열 식으로 조건을 적는 방식입니다.
- **집합 포함 검사**: 값이 특정 집합에 속하는지 확인하는 방식입니다.

## 전과 후

이전 관점: `df[조건]`만으로 모든 문제를 풀려다 경고와 혼란을 만납니다.

이후 관점: 레이블, 위치, 조건이라는 의도에 맞춰 `loc`, `iloc`, `query`를 나눠 씁니다.

## 실습: 다섯 단계로 고르기

### 1단계 - 기준 데이터 만들기

```python
import pandas as pd

df = pd.DataFrame({
    "name":   ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "dept":   ["Engineering", "Marketing", "Engineering", "HR", "Marketing"],
    "salary": [95000, 72000, 88000, 65000, 78000],
    "years":  [5, 3, 7, 2, 4],
}, index=["e01", "e02", "e03", "e04", "e05"])

print(df)
```

**예상 출력:**

```text
       name         dept  salary  years
e01   Alice  Engineering   95000      5
e02     Bob    Marketing   72000      3
e03  Charlie  Engineering   88000      7
e04   Diana           HR   65000      2
e05     Eve    Marketing   78000      4
```

### 2단계 - 레이블로 고르기 (loc)

```python
# 단일 행
print(df.loc["e01"])
print()

# 특정 행과 열
print(df.loc[["e01", "e03"], ["name", "salary"]])
print()

# 슬라이싱 (끝점 포함)
print(df.loc["e01":"e03", "name":"salary"])
```

**예상 출력:**

```text
name       Alice
dept     Engineering
salary      95000
years           5
Name: e01, dtype: object

      name  salary
e01  Alice   95000
e03  Charlie   88000

      name         dept  salary
e01  Alice  Engineering   95000
e02    Bob    Marketing   72000
e03  Charlie  Engineering   88000
```

`loc`는 행과 열의 이름을 기준으로 고를 때 가장 명확합니다. 슬라이싱 시 끝점을 포함한다는 점에서 `iloc`와 다릅니다.

### 3단계 - 위치로 고르기 (iloc)

```python
# 첫 번째 행
print(df.iloc[0])
print()

# 처음 3행, 처음 2열
print(df.iloc[:3, :2])
print()

# 마지막 2행
print(df.iloc[-2:])
```

**예상 출력:**

```text
name       Alice
dept     Engineering
salary      95000
years           5
Name: e01, dtype: object

      name         dept
e01  Alice  Engineering
e02    Bob    Marketing
e03  Charlie  Engineering

      name       dept  salary  years
e04  Diana         HR   65000      2
e05    Eve  Marketing   78000      4
```

`iloc`는 순수하게 위치만 중요할 때 씁니다. 슬라이싱 감각은 파이썬 리스트와 동일하며, 끝점을 포함하지 않습니다.

### 4단계 - 조건으로 고르기 (불리언 마스크)

```python
# 단일 조건
high_salary = df[df["salary"] > 80000]
print("고연봉 직원:\n", high_salary)
print()

# 복수 조건 (반드시 괄호와 &/|)
eng_senior = df[(df["dept"] == "Engineering") & (df["years"] >= 5)]
print("Engineering 5년차 이상:\n", eng_senior)
print()

# 부정 조건
not_marketing = df[~(df["dept"] == "Marketing")]
print("Marketing 제외:\n", not_marketing)
```

**예상 출력:**

```text
고연봉 직원:
        name         dept  salary  years
e01   Alice  Engineering   95000      5
e03  Charlie  Engineering   88000      7

Engineering 5년차 이상:
        name         dept  salary  years
e01   Alice  Engineering   95000      5
e03  Charlie  Engineering   88000      7

Marketing 제외:
        name         dept  salary  years
e01   Alice  Engineering   95000      5
e03  Charlie  Engineering   88000      7
e04   Diana           HR   65000      2
```

조건 마스크는 필터링에서 가장 많이 쓰는 패턴입니다. 여러 조건을 묶을 때는 반드시 괄호와 `&`, `|`를 함께 써야 합니다.

### 5단계 - query와 isin 사용하기

```python
# query로 문자열 표현식 사용
result1 = df.query("salary > 80000 and years >= 5")
print("query 결과:\n", result1)
print()

# isin으로 집합 포함 검사
target_depts = ["Engineering", "HR"]
result2 = df[df["dept"].isin(target_depts)]
print("isin 결과:\n", result2)
print()

# between으로 범위 검사
result3 = df[df["salary"].between(70000, 90000)]
print("between 결과:\n", result3)
```

**예상 출력:**

```text
query 결과:
        name         dept  salary  years
e01   Alice  Engineering   95000      5
e03  Charlie  Engineering   88000      7

isin 결과:
        name         dept  salary  years
e01   Alice  Engineering   95000      5
e03  Charlie  Engineering   88000      7
e04   Diana           HR   65000      2

between 결과:
      name       dept  salary  years
e02    Bob  Marketing   72000      3
e03  Charlie  Engineering   88000      7
e05    Eve  Marketing   78000      4
```

조건식이 길어질수록 `query`와 `isin`이 얼마나 읽기 쉬운지 차이가 납니다. 집합 포함 검사는 긴 OR 체인을 대체하는 실전 패턴입니다.

## 인덱싱 방법 비교

| 방법 | 용도 | 끝점 포함 | 속도 | 권장 상황 |
| --- | --- | --- | --- | --- |
| `[]` | 열 선택, 조건 필터링 | - | 빠름 | 간단한 열 선택 |
| `.loc` | 레이블 기반 선택, 할당 | 포함 | 보통 | 이름으로 선택, 값 할당 |
| `.iloc` | 위치 기반 선택 | 미포함 | 빠름 | 위치 기반 슬라이싱 |
| `.at` | 단일 셀 레이블 접근 | - | 매우 빠름 | 반복문 내 단일 값 |
| `.iat` | 단일 셀 위치 접근 | - | 매우 빠름 | 반복문 내 단일 값 |
| `query` | 문자열 조건식 | - | 보통 | 복잡한 조건 가독성 |

대부분 상황에서 `loc`와 `iloc`만으로 충분하지만, 반복문 안에서 단일 값에 접근할 때는 `.at`과 `.iat`이 성능 측면에서 유리합니다.

## 성능 비교: loc vs at

```python
import numpy as np
import time

df_perf = pd.DataFrame({
    "value": np.arange(100_000),
})

# loc 방식 (단일 값 반복 접근)
start = time.time()
total = 0
for i in range(1000):
    total += df_perf.loc[i, "value"]
loc_time = time.time() - start

# at 방식 (단일 값 최적화)
start = time.time()
total = 0
for i in range(1000):
    total += df_perf.at[i, "value"]
at_time = time.time() - start

# 벡터화 방식 (가장 빠름)
start = time.time()
total = df_perf["value"][:1000].sum()
vec_time = time.time() - start

print(f".loc 반복:   {loc_time*1000:.2f}ms")
print(f".at 반복:    {at_time*1000:.2f}ms")
print(f"벡터화:      {vec_time*1000:.3f}ms")
print(f"loc vs at:  {loc_time/at_time:.1f}배")
print(f"loc vs vec: {loc_time/vec_time:.0f}배")
```

**예상 출력:**

```text
.loc 반복:   18.45ms
.at 반복:     4.21ms
벡터화:       0.08ms
loc vs at:   4.4배
loc vs vec: 230배
```

단일 값 반복 접근은 `.at`이 `.loc`보다 빠르고, 벡터화가 압도적으로 빠릅니다.

## 체이닝 인덱싱 경고 해결

```python
df_fix = df.copy()

# 나쁜 패턴 - SettingWithCopyWarning 발생 가능
# df_fix[df_fix["dept"] == "Engineering"]["salary"] = 100000

# 좋은 패턴 1: loc 사용
df_fix.loc[df_fix["dept"] == "Engineering", "salary"] = 100000

# 좋은 패턴 2: 명시적 복사본 생성 후 수정
eng_copy = df[df["dept"] == "Engineering"].copy()
eng_copy["salary"] = 100000
print(eng_copy[["name", "salary"]])
```

**예상 출력:**

```text
        name  salary
e01   Alice  100000
e03  Charlie  100000
```

## 멀티인덱스 활용

```python
# 멀티인덱스 생성
index = pd.MultiIndex.from_tuples([
    ("Engineering", "senior"),
    ("Engineering", "junior"),
    ("Marketing", "senior"),
    ("Marketing", "junior"),
    ("HR", "senior"),
], names=["dept", "level"])

df_multi = pd.DataFrame({
    "headcount": [5, 8, 3, 6, 2],
    "avg_salary": [95000, 72000, 85000, 65000, 80000],
}, index=index)

print(df_multi)
print()

# 첫 번째 레벨로 선택
print("Engineering 부서:")
print(df_multi.loc["Engineering"])
print()

# 특정 조합 선택
print("Engineering senior:")
print(df_multi.loc[("Engineering", "senior")])
```

**예상 출력:**

```text
                     headcount  avg_salary
dept        level
Engineering senior          5       95000
            junior          8       72000
Marketing   senior          3       85000
            junior          6       65000
HR          senior          2       80000

Engineering 부서:
        headcount  avg_salary
level
senior          5       95000
junior          8       72000
```

## 실전 예제: 고객 세그먼트 분할

```python
customers = pd.DataFrame({
    "customer_id": range(1, 11),
    "age":         [25, 35, 45, 55, 65, 28, 38, 48, 58, 30],
    "purchase":    [100, 200, 150, 300, 250, 80, 220, 170, 310, 130],
    "region":      ["서울", "부산", "서울", "대구", "부산",
                    "서울", "서울", "부산", "대구", "서울"],
})

# 연령대별 분할
young  = customers[customers["age"] < 35]
middle = customers[(customers["age"] >= 35) & (customers["age"] < 55)]
senior = customers[customers["age"] >= 55]

print(f"청년층: {len(young)}명, 평균 구매: {young['purchase'].mean():.0f}원")
print(f"중년층: {len(middle)}명, 평균 구매: {middle['purchase'].mean():.0f}원")
print(f"노년층: {len(senior)}명, 평균 구매: {senior['purchase'].mean():.0f}원")
print()

# 서울 고연령 고구매 고객
vip = customers.query(
    "region == '서울' and age >= 30 and purchase >= 150"
)
print("서울 VIP 고객:")
print(vip[["customer_id", "age", "purchase", "region"]])
```

**예상 출력:**

```text
청년층: 4명, 평균 구매: 103원
중년층: 4명, 평균 구매: 185원
노년층: 2명, 평균 구매: 280원

서울 VIP 고객:
   customer_id  age  purchase region
6            7   38       220     서울
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 조건에서 `and/or` 사용 | `ValueError: 값의 진리가 모호함` | `&`, `|` 사용 |
| 체이닝 인덱싱으로 할당 | SettingWithCopyWarning, 값 미반영 | `.loc[조건, 열]` 사용 |
| `loc` 끝점 포함 미인지 | 예상 밖 행 포함 | `loc`와 `iloc` 차이 숙지 |
| `iloc`에 레이블 입력 | `TypeError` | 레이블은 `loc`, 위치는 `iloc` |
| OR 체인 남용 | 장황하고 오류 가능한 코드 | `isin()` 사용 |

## 실무에서는 이렇게 생각합니다

- 복잡한 조건은 먼저 변수로 분리합니다.
- 할당할 때는 항상 `loc`를 우선합니다.
- `query`는 읽기 쉬워질 때만 씁니다.
- `isin`, `between` 같은 도구로 코드를 줄입니다.
- 경고를 무시하지 않습니다.

## 운영 체크리스트

- [ ] `loc`와 `iloc`를 구분할 수 있습니다.
- [ ] 여러 조건을 괄호와 `&/|`로 표현할 수 있습니다.
- [ ] 체이닝 인덱싱을 피해야 하는 이유를 알고 있습니다.
- [ ] `query`와 `isin`의 용도를 설명할 수 있습니다.
- [ ] 성능이 필요한 단일 값 접근에 `.at`을 쓸 수 있습니다.

## 연습 문제

1. `loc`로 특정 레이블의 부분 집합을 뽑아 보세요.
2. `iloc`로 처음 5행, 마지막 2열을 출력해 보세요.
3. 두 개 이상의 조건을 `query`로 표현해 보세요.
4. 반복문 내 단일 값 접근에서 `.loc`와 `.at`의 속도를 직접 측정해 보세요.

## 정리와 다음 글

선택은 분석에서 가장 자주 반복되는 기본 동작입니다. 의도에 맞는 선택 도구를 고를 수 있어야 이후의 정제와 집계도 안정적으로 이어집니다. 다음 글에서는 결측치를 어떻게 진단하고 다룰지 다루겠습니다.

## 처음 질문으로 돌아가기

- **`loc`와 `iloc`는 언제 구분해서 써야 할까요?**
  - 이름(레이블)으로 선택할 때는 `loc`, 위치(정수)로 선택할 때는 `iloc`를 씁니다. 값 할당에는 항상 `loc`를 사용합니다.
- **조건 마스크는 어떤 상황에서 가장 자연스러울까요?**
  - 특정 값을 기준으로 행을 걸러내는 모든 상황에서 자연스럽습니다. 복잡한 조건은 변수로 분리해 읽기 쉽게 만들 수 있습니다.
- **표현식이 길어질수록 `query`가 왜 읽기 쉬워질까요?**
  - `query`는 문자열로 조건을 적으므로 괄호 중첩이 없고 SQL WHERE 절처럼 읽힙니다. 조건이 세 개 이상이면 `query`가 훨씬 명확합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- **Pandas 101 (4/10): 필터링과 선택 (현재 글)**
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — Indexing and selecting data](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [pandas — query](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html)
- [pandas — Boolean indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing)
- [Real Python — Pandas DataFrame Indexing](https://realpython.com/pandas-dataframe/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Filtering, Selection, Indexing, Beginner
