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

이 글은 판다스 101 시리즈의 4번째 글입니다.

Pandas를 익히다 보면 같은 표에서 원하는 부분을 고르는 방법이 여러 개라는 사실이 먼저 헷갈립니다. `loc`, `iloc`, 조건 마스크, `query`까지 모두 비슷해 보이지만 실제로는 의도가 다릅니다. 이 차이를 이해하지 못하면 선택 코드는 금방 읽기 어려워지고, 할당 시점에는 경고까지 따라옵니다.

이번 글에서는 행과 열을 고르는 네 가지 방식을 기능 목록이 아니라 의도에 맞는 도구 상자로 정리해 보겠습니다.

![Pandas 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/04/04-01-concept-at-a-glance.ko.png)
*Pandas 101 4장 흐름 개요*
> **선택은 의도에 맞는 도구**입니다. 같은 데이터를 고르더라도 `loc`, `iloc`, 조건 마스크, `query` 중 어떤 것을 선택하느냐에 따라 코드의 명확성과 유지보수 비용이 달라집니다.

## 먼저 던지는 질문

- `loc`와 `iloc`는 언제 구분해서 써야 할까요?
- 조건 마스크는 어떤 상황에서 가장 자연스러울까요?
- 표현식이 길어질수록 `query`가 왜 읽기 쉬워질까요?

## 왜 중요한가

분석은 거의 모든 단계에서 부분 집합을 뽑는 작업을 반복합니다. 느리거나 모호한 선택 코드는 이후의 집계, 조인, 시각화까지 함께 흔듭니다. 그래서 선택 연산은 작은 문법이 아니라 분석의 기본 동작으로 봐야 합니다.

## 핵심 용어

- **레이블 기반 선택**: 이름으로 행과 열을 고르는 방식입니다.
- **위치 기반 선택**: 숫자 위치로 고르는 방식입니다.
- **불리언 마스크**: 참과 거짓으로 행을 걸러내는 시리즈입니다.
- **문자열 질의**: 문자열 식으로 조건을 적는 방식입니다.
- **집합 포함 검사**: 값이 특정 집합에 속하는지 확인하는 방식입니다.

## 전과 후

이전 관점: `df[조건]`만으로 모든 문제를 풀려다 경고와 혼란을 만납니다.

이후 관점: 레이블, 위치, 조건이라는 의도에 맞춰 `loc`, `iloc`, `query`를 나눠 씁니다.

## 실습: 다섯 단계로 고르기

### 1단계 - 열 선택하기

```python
import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}, index=["a", "b", "c"])
print(df["x"])
print(df[["x", "y"]])
```

열 하나를 고르면 시리즈가, 열 여러 개를 고르면 데이터프레임이 나옵니다. 이 차이는 이후 메서드 체인과 할당 방식에 직접 영향을 줍니다.

### 2단계 - 레이블로 고르기

```python
print(df.loc["a"])
print(df.loc[["a", "c"], "x"])
```

레이블 기반 선택은 “어느 행을 뽑았는가”를 바로 읽게 해 줍니다. 위치가 아니라 이름으로 고르는 코드라서 유지보수에도 유리합니다.

**예상 출력:**

```text
a    1
c    3
Name: x, dtype: int64
```

`loc`는 행과 열의 이름을 기준으로 고를 때 가장 명확합니다. 특히 할당과 함께 쓰일 때도 의도가 분명하게 드러납니다.

### 3단계 - 위치로 고르기

```python
print(df.iloc[0])
print(df.iloc[0:2, 0])
```

`iloc`는 순수하게 위치만 중요할 때 쓰면 됩니다. 슬라이싱 감각은 파이썬 리스트와 비슷하지만, 이름이 아닌 위치를 쓴다는 점을 잊지 않아야 합니다.

## 인덱싱 방법 비교

Pandas는 다양한 인덱싱 방법을 제공합니다. 각 방법의 용도와 특성을 이해하면 상황에 맞는 도구를 선택할 수 있습니다.

| 방법 | 용도 | 속도 |
| --- | --- | --- |
| `[]` | 열 선택, 조건 필터링 | 빠름 |
| `.loc` | 레이블 기반 선택, 할당 | 보통 |
| `.iloc` | 위치 기반 선택 | 빠름 |
| `.at` | 단일 셀 레이블 접근 | 매우 빠름 |
| `.iat` | 단일 셀 위치 접근 | 매우 빠름 |

대부분 상황에서 `loc`와 `iloc`만으로 충분하지만, 반복문 안에서 단일 값에 접근할 때는 `.at`과 `.iat`이 성능 측면에서 유리합니다.

### 4단계 - 조건으로 고르기

```python
print(df[df["x"] > 1])
print(df[(df["x"] > 1) & (df["y"] < 30)])
```

조건 마스크는 필터링에서 가장 많이 쓰는 패턴입니다. 단, 여러 조건을 묶을 때는 반드시 괄호와 `&`, `|`를 함께 써야 합니다.

### 5단계 - 문자열 식과 포함 검사 쓰기

```python
print(df.query("x > 1 and y < 30"))
print(df[df["x"].isin([1, 3])])
```

조건식이 길어질수록 `query`와 `isin`이 얼마나 읽기 쉬운지 차이가 납니다. 특히 집합 포함 검사는 긴 OR 체인을 대체하는 실전 패턴입니다.

**예상 출력:**

```text
   x   y
b  2  20

   x   y
a  1  10
c  3  30
```

조건이 길어지면 `query`가 가독성을 높여 줄 수 있습니다. 특정 값 집합을 기준으로 고를 때는 `isin`이 긴 OR 체인보다 낫습니다.

## 불리언 인덱싱 상세

불리언 인덱싱은 Pandas에서 가장 자주 쓰는 패턴 중 하나입니다. 조건식을 명확하게 작성하는 법을 익히면 코드 가독성이 크게 높아집니다.

### 단일 조건

```python
df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
mask = df["x"] > 1
print(mask)
print(df[mask])
```

조건식 `df["x"] > 1`은 불리언 Series를 반환합니다. 이 Series를 DataFrame에 다시 적용하면 True인 행만 남습니다.

### 복수 조건

```python
result = df[(df["x"] > 1) & (df["y"] < 30)]
print(result)
```

여러 조건을 합칠 때는 반드시 괄호로 각 조건을 감싸야 합니다. `and`/`or` 대신 `&`/`|`를 써야 하는 점도 주의하세요.

### 부정 조건

```python
not_match = df[~(df["x"] > 1)]
print(not_match)
```

`~` 연산자로 조건을 반전시킬 수 있습니다. 이는 "특정 조건을 만족하지 않는 행"을 골라낼 때 유용합니다.

## 이 코드에서 먼저 봐야 할 점

- `loc`는 끝점을 포함하고 `iloc`는 끝점을 제외합니다.
- `&`와 `|`는 비트 연산자이며 `and/or`와 다릅니다.
- 조건식이 길어질수록 `query`가 읽기 쉬운 선택지가 될 수 있습니다.

## 자주 하는 실수 다섯 가지

1. 마스크 조건에서 `and/or`를 써서 오류를 냅니다.
2. 체이닝 인덱싱으로 `SettingWithCopyWarning`를 만듭니다.
3. `loc`가 끝점을 포함한다는 사실을 놓칩니다.
4. `iloc`에 레이블을 넣어 선택하려고 합니다.
5. `isin` 대신 `|`를 길게 이어 붙입니다.

## 실무에서는 이렇게 이어집니다

지표 대시보드, 이상치 탐지, 실험군 분리처럼 조건 기반 선택은 분석 함수의 중심입니다. 그래서 많은 팀이 할당에는 `loc`를 기본 규칙으로 삼고, 복잡한 조건은 이름 붙은 변수로 분리해 읽기 쉽게 유지합니다.

## 실무에서는 이렇게 생각합니다

- 복잡한 조건은 먼저 변수로 분리합니다.
- 할당할 때는 항상 `loc`를 우선합니다.
- `query`는 읽기 쉬워질 때만 씁니다.
- `isin`, `between` 같은 도구로 코드를 줄입니다.
- 경고를 무시하지 않습니다.

## 멀티인덱스

MultiIndex는 행이나 열에 여러 레벨의 인덱스를 설정하는 기능입니다. 계층적 데이터를 다룰 때 특히 유용합니다.

### 멀티인덱스 생성

```python
index = pd.MultiIndex.from_tuples([
    ("A", 1),
    ("A", 2),
    ("B", 1),
    ("B", 2),
], names=["category", "id"])
df = pd.DataFrame({"value": [10, 20, 30, 40]}, index=index)
print(df)
```

**예상 출력:**

```text
               value
category id       
A        1       10
         2       20
B        1       30
         2       40
```

계층적 구조를 가진 데이터를 나타내기에 적합합니다. 예를 들어 도시별, 날짜별 집계 결과를 표현할 때 유용합니다.

### 멀티인덱스 접근

```python
print(df.loc["A"])
print(df.loc[("A", 1)])
```

MultiIndex는 튜플을 키로 사용하거나, 첫 번째 레벨만으로 접근할 수 있습니다. 이 기능은 groupby 결과를 다룰 때도 자주 등장합니다.

### 평탄화

```python
flat = df.reset_index()
print(flat)
```

MultiIndex를 일반 컴럼으로 변환할 때는 `reset_index()`를 사용합니다. 이렇게 하면 인덱스가 컴럼으로 이동하고, 새 정수 인덱스가 생성됩니다.

## 체크리스트

- [ ] `loc`와 `iloc`를 구분할 수 있습니다.
- [ ] 여러 조건을 괄호와 `&/|`로 표현할 수 있습니다.
- [ ] 체이닝 인덱싱을 피해야 하는 이유를 알고 있습니다.
- [ ] `query`와 `isin`의 용도를 설명할 수 있습니다.

## 실전 예제: 조건별 데이터 분할

실무에서는 조건에 따라 데이터를 나누어 처리하는 경우가 많습니다.

```python
df = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "age": [25, 35, 45, 55, 65],
    "purchase": [100, 200, 150, 300, 250],
})

# 연령대별 분할
young = df[df["age"] < 40]
middle = df[(df["age"] >= 40) & (df["age"] < 60)]
senior = df[df["age"] >= 60]

print(f"Young: {len(young)}, Middle: {len(middle)}, Senior: {len(senior)}")
print(f"Young avg purchase: {young['purchase'].mean()}")
```

이런 분할은 A/B 테스트, 코호트 분석, 세그먼트별 지표 계산에서 자주 사용됩니다.

## 성능 팁

선택 연산의 성능을 최적화하는 방법을 알아두면 대용량 데이터에서 유리합니다.

### Boolean indexing vs query

```python
# Boolean indexing - 빠름
result1 = df[(df["x"] > 10) & (df["y"] < 50)]

# query - 긴 조건에서 가독성 좋음
result2 = df.query("x > 10 and y < 50")
```

단순 조건은 boolean indexing이 빠르지만, 복잡한 조건은 query가 읽기 좋습니다.

## 성능 최적화 팁

대용량 데이터를 다룰 때는 선택 연산의 성능이 중요합니다.

### at/iat 활용

```python
# Slow
for i in range(len(df)):
    value = df.loc[i, "column"]
    
# Fast  
for i in range(len(df)):
    value = df.iat[i, 0]
```

단일 값 접근에서는 at/iat이 훨씬 빠릅니다.

### 벡터화 우선

```python
# Slow - apply
df["result"] = df["x"].apply(lambda x: x * 2 if x > 10 else x)

# Fast - vectorized
df["result"] = df["x"].where(df["x"] <= 10, df["x"] * 2)
```

가능하면 apply 대신 벡터화 연산을 사용하세요.

### 체이닝 인덱싱 경고 해결

```python
# Bad - 경고 발생
df[df["x"] > 0]["y"] = 100

# Good - loc 사용
df.loc[df["x"] > 0, "y"] = 100

# Good - copy 명시
subset = df[df["x"] > 0].copy()
subset["y"] = 100
```

loc를 사용하거나 명시적 복사본을 만드는 것이 안전합니다.

## 고급 인덱싱 패턴

### 크로스 섹션

```python
# MultiIndex에서 특정 레벨 선택
result = df.xs("A", level="category")
print(result)
```

### IndexSlice

```python
idx = pd.IndexSlice
result = df.loc[idx["A":"B", 1:2], :]
print(result)
```

MultiIndex를 다룰 때 IndexSlice를 사용하면 슬라이싱이 더 직관적입니다.

MultiIndex는 복잡해 보이지만, 계층적 데이터를 표현하는 강력한 도구입니다. groupby 결과도 종종 MultiIndex를 반환합니다.

## 인덱싱 성능 비교

인덱싱 방법에 따라 속도 차이가 발생합니다. 대량 데이터에서는 이 차이가 더 두드러집니다.

```python
import time

df = pd.DataFrame({"x": range(100000)})
start = time.time()
for i in range(1000):
    val = df.loc[i, "x"]
print(f".loc 소요 시간: {time.time() - start:.4f}초")

start = time.time()
for i in range(1000):
    val = df.at[i, "x"]
print(f".at 소요 시간: {time.time() - start:.4f}초")
```

`.at`은 단일 값 접근에 최적화되어 있어 `.loc`보다 빠릅니다. 반복문 안에서 단일 값을 읽을 때는 `.at`을 우선하세요.

## 연습 문제

1. `loc`로 특정 레이블의 부분 집합을 뽑아 보세요.
2. `iloc`로 처음 5행을 출력해 보세요.
3. 두 개 이상의 조건을 `query`로 표현해 보세요.

## 정리와 다음 글

선택은 분석에서 가장 자주 반복되는 기본 동작입니다. 의도에 맞는 선택 도구를 고를 수 있어야 이후의 정제와 집계도 안정적으로 이어집니다. 다음 글에서는 결측치를 어떻게 진단하고 다룰지 다루겠습니다.

## 처음 질문으로 돌아가기

- **`loc`와 `iloc`는 언제 구분해서 써야 할까요?**
  - 본문의 기준은 필터링과 선택를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **조건 마스크는 어떤 상황에서 가장 자연스러울까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **표현식이 길어질수록 `query`가 왜 읽기 쉬워질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- **필터링과 선택 (현재 글)**
- 결측치 처리 (예정)
- 그룹화와 집계 (예정)
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Indexing and selecting data](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [pandas — query](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html)
- [pandas — Boolean indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing)
- [Real Python — Pandas DataFrame Indexing](https://realpython.com/pandas-dataframe/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Filtering, Selection, Indexing, Beginner
