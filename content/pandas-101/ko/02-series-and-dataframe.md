---
series: pandas-101
episode: 2
title: "Pandas 101 (2/10): 시리즈와 데이터프레임"
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
  - Series
  - DataFrame
  - Python
  - Beginner
seo_description: 시리즈와 데이터프레임의 관계를 이해합니다. 인덱스 정렬 원리, 열 중심 사고방식, 레이블 연산 등 Pandas 데이터 모델링 기초를 정리합니다.
last_reviewed: '2026-05-15'
---

# Pandas 101 (2/10): 시리즈와 데이터프레임

이 글은 판다스 101 시리즈의 2번째 글입니다.

Pandas를 쓰기 시작하면 금방 이런 질문이 나옵니다. 시리즈와 데이터프레임은 이름만 다른 두 자료구조일까요, 아니면 하나의 모델을 다른 크기로 보여 주는 걸까요. 이 관계를 초반에 분명히 잡아 두지 않으면 열 선택, 정렬, 산술 연산, 조인에서 계속 감으로만 코드를 쓰게 됩니다.

이번 글의 핵심은 간단합니다. 데이터프레임은 서로 같은 레이블 체계를 공유하는 시리즈의 묶음입니다. 이 관점을 잡으면 Pandas의 많은 동작이 훨씬 자연스럽게 읽힙니다.

![Pandas 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/02/02-01-concept-at-a-glance.ko.png)
*Pandas 101 2장 흐름 개요*
> 데이터프레임은 시리즈의 **묶음**입니다. 이 관점을 갖추면 정렬, 결합, 열 연산이 모두 같은 원리로 작동하는 이유가 명확해집니다.

## 먼저 던지는 질문

- 시리즈는 내부적으로 어떤 구조일까요?
- 데이터프레임을 열 중심으로 본다는 말은 무엇을 뜻할까요?
- 인덱스는 왜 단순한 행 번호가 아닐까요?

## 왜 중요한가

Pandas의 대부분 연산은 결국 시리즈 수준의 계산으로 환원됩니다. 데이터프레임의 한 열이 시리즈라는 사실을 이해하면 열 선택이 왜 특정 타입을 반환하는지, 왜 인덱스 정렬이 자동으로 일어나는지, 왜 레이블이 숫자 배열만큼 중요한지가 한 번에 연결됩니다.

## 핵심 용어

- 시리즈: 값과 인덱스를 함께 가진 1차원 구조입니다.
- **데이터프레임**: 공통 인덱스를 공유하는 시리즈들의 묶음입니다.
- **값 배열**: 내부 계산에 쓰이는 기저 배열입니다.
- 인덱스: 행 레이블입니다.
- **열 레이블**: 각 시리즈를 구분하는 이름입니다.

## 전과 후

이전 관점: 데이터프레임을 그저 행과 열이 있는 표로만 봅니다.

이후 관점: 데이터프레임을 여러 시리즈가 같은 인덱스 위에 놓인 구조로 이해합니다.

## 실습: 구조를 직접 만들어 보기

### 1단계 - 시리즈 만들고 속성 보기

```python
import pandas as pd
s = pd.Series([1.0, 2.0, 3.0], index=["a", "b", "c"], name="x")
print(s.values, s.index, s.name)
```

시리즈는 값만 담는 배열이 아니라 레이블과 이름까지 갖춘 구조입니다. 이후 정렬과 연산은 이 레이블을 기준으로 움직입니다.

### 2단계 - 시리즈끼리 계산하기

```python
print(s * 10)
print(s + s)
```

시리즈 산술은 단순 반복문이 아니라 인덱스가 붙은 배열 연산입니다. 이 차이가 나중에 정렬 기반 계산의 핵심이 됩니다.

## 시리즈와 데이터프레임 비교

이 두 구조의 관계는 표로 정리하면 명확해집니다.

| 항목 | Series | DataFrame |
| --- | --- | --- |
| 차원 | 1차원 | 2차원 |
| 인덱스 | 행 레이블 | 행 레이블 (공유) |
| 생성 방법 | `pd.Series(list, index=...)` | `pd.DataFrame(dict)` |

DataFrame은 같은 인덱스를 공유하는 Series의 묶음으로 볼 수 있습니다. 그래서 `df['column']`은 Series를 반환하고, `df[['column']]`은 1열 DataFrame을 반환합니다. 이 차이를 인지하는 것이 중요합니다.

### 3단계 - 데이터프레임 만들기

```python
df = pd.DataFrame({
    "x": [1, 2, 3],
    "y": [10, 20, 30],
}, index=["a", "b", "c"])
print(df)
```

데이터프레임을 시리즈 묶음으로 본다는 말은 출력 형태에서도 바로 드러납니다. 같은 인덱스를 공유하는 두 열이 한 표 안에 나란히 놓여 있는지 확인해 보세요.

**예상 출력:**

```text
   x   y
a  1  10
b  2  20
c  3  30
```

이 데이터프레임은 같은 인덱스를 공유하는 두 개의 시리즈를 옆으로 붙여 둔 것처럼 볼 수 있습니다. 그래서 열 단위 연산이 자연스럽습니다.

### 4단계 - 열 하나를 고르면 시리즈가 나옵니다

```python
col = df["x"]
print(type(col), col)
```

`df["x"]`가 데이터프레임이 아니라 시리즈라는 사실은 매우 중요합니다. 열 선택 뒤에 이어지는 메서드와 연산이 모두 시리즈 문법으로 연결되기 때문입니다.

### 5단계 - 인덱스가 자동으로 맞춰집니다

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20, 30], index=["b", "c", "d"])
print(s1 + s2)
```

여기서 핵심은 값이 아니라 인덱스 정렬입니다. 겹치지 않는 레이블에는 `NaN`이 생기고, 공통 레이블에서만 실제 덧셈이 일어납니다.

**예상 출력:**

```text
a     NaN
b    12.0
c    23.0
d     NaN
dtype: float64
```

Pandas는 단순히 같은 위치의 값을 더하지 않습니다. 먼저 인덱스를 맞춘 뒤 계산하고, 맞지 않는 위치는 `NaN`으로 남깁니다.

## 다양한 DataFrame 생성법

DataFrame을 만드는 방법은 여러 가지입니다. 각 방법은 데이터의 원본 형태에 따라 선택하면 됩니다.

### 딕셔너리로 만들기

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30],
})
print(df)
```

가장 직관적인 방법입니다. 딕셔너리의 키가 열 이름이 되고, 값 리스트가 각 열의 내용이 됩니다.

### 리스트 of 딕셔너리로 만들기

```python
data = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
]
df = pd.DataFrame(data)
print(df)
```

JSON API 응답이나 로그 파싱 결과처럼 행별로 데이터가 오는 경우에 자주 씁니다.

### NumPy 배열로 만들기

```python
import numpy as np
arr = np.array([[1, 2], [3, 4], [5, 6]])
df = pd.DataFrame(arr, columns=["x", "y"])
print(df)
```

내부적으로 Pandas는 NumPy 배열을 기반으로 동작하므로 이 방법도 매우 자연스럽습니다.
## 이 코드에서 먼저 봐야 할 점

- `df["x"]`는 시리즈를 반환합니다.
- 시리즈 산술에서는 인덱스 정렬이 자동으로 일어납니다.
- `NaN`은 정렬이 맞지 않았다는 중요한 단서가 될 수 있습니다.

## 자주 하는 실수 다섯 가지

1. `df["x"]`를 데이터프레임으로 착각합니다.
2. 인덱스가 어긋나 생긴 `NaN`을 단순 결측치로만 봅니다.
3. 항상 `values`로 넘겨 레이블 정보를 잃어버립니다.
4. `name` 속성을 무시해 시리즈 식별이 어려워집니다.
5. 두 데이터프레임의 행 순서가 같다고 가정한 채 더합니다.

## 실무에서는 이렇게 이어집니다

A/B 테스트 비교, 시계열 정렬, 여러 소스의 데이터 결합에서 Pandas가 강한 이유는 바로 인덱스 정렬입니다. 눈에 잘 보이지 않지만, 이 동작이 많은 계산의 정확도를 지탱합니다.

## 실무에서는 이렇게 생각합니다

- 먼저 인덱스가 무엇을 의미하는지 분명히 합니다.
- 열 선택은 곧 시리즈 사고방식으로 넘어가는 순간이라고 봅니다.
- 정렬 불일치에서 생긴 `NaN`을 디버깅 단서로 활용합니다.
- `df.values` 의존도를 낮춥니다.
- 시리즈 이름을 적극적으로 붙여 흐름을 읽기 쉽게 만듭니다.

## 실전 예제: 시계열 데이터

시리즈와 데이터프레임의 관계를 시계열 데이터로 확인해 보겠습니다.

```python
dates = pd.date_range("2024-01-01", periods=5, freq="D")
temp = pd.Series([15, 16, 14, 17, 16], index=dates, name="temperature")
humidity = pd.Series([60, 65, 55, 70, 68], index=dates, name="humidity")
weather = pd.DataFrame({"temp": temp, "humidity": humidity})
print(weather)
print("\n평균 기온:", weather["temp"].mean())
```

시계열에서는 인덱스가 날짜가 되고, 각 열은 시간에 따른 관측값을 나타냅니다. 이 구조를 이해하면 시계열 분석이 훨씬 수월해집니다.

## 성능 고려사항

Series와 DataFrame의 내부 구조를 이해하면 성능 최적화에도 도움이 됩니다.

### 벡터화를 우선하세요

```python
# Slow - 반복문
result = []
for val in df["x"]:
    result.append(val * 2)

# Fast - 벡터화
result = df["x"] * 2
```

반복문 대신 열 단위 연산을 사용하면 NumPy의 최적화된 C 코드를 활용할 수 있습니다.

### 메모리 효율적인 타입 선택

```python
# 기본 int64는 8바이트
df["count"] = df["count"].astype("int32")  # 4바이트로 절반
df["category"] = df["category"].astype("category")  # 범주형 데이터
print(df.memory_usage(deep=True))
```

대용량 데이터를 다룰 때는 타입 선택이 메모리 사용량에 크게 영향을 줍니다.

### copy vs view

```python
# view - 원본 데이터 공유
subset = df[["x", "y"]]

# copy - 독립적인 복사본
subset = df[["x", "y"]].copy()
```

할당을 할 때는 복사본을 명시적으로 만들어 SettingWithCopyWarning을 피하세요.
## 자료형 확인과 변환

데이터프레임의 각 열은 자료형을 가집니다. 이 자료형을 명시적으로 확인하고 변환하는 것이 후속 연산의 정확성을 보장합니다.

### 자료형 확인

```python
df = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "score": [85.5, 90.0, 78.5],
})
print(df.dtypes)
```

**예상 출력:**

```text
id         int64
name      object
score    float64
dtype: object
```

Pandas는 자동으로 자료형을 추론하지만, 항상 정확한 것은 아닙니다. 그래서 명시적 변환이 필요할 때가 많습니다.

### 자료형 변환

```python
df["id"] = df["id"].astype("string")
df["score"] = df["score"].astype("int32")
print(df.dtypes)
```

`astype()`을 사용하면 모5시적으로 타입을 바꿀 수 있습니다. 실수를 정수로, 숫자를 문자열로 바꾸는 작업이 자주 등장합니다.

### 메모리 효율을 위한 타입 선택

Pandas 1.0 이후로 `int8`, `int16`, `int32` 같은 작은 정수형과 `string` 타입을 적극 활용하면 메모리를 크게 줄일 수 있습니다. 특히 대용량 데이터를 다룰 때 타입 선택은 성능에 직접 영향을 줍니다.

## 체크리스트

- [ ] 시리즈와 데이터프레임을 구분할 수 있습니다.
- [ ] 인덱스와 열 레이블의 역할을 설명할 수 있습니다.
- [ ] `df["col"]`이 시리즈임을 알고 있습니다.
- [ ] 인덱스 정렬이 자동이라는 점을 이해하고 있습니다.

## 인덱스 연산

인덱스가 있는 시리즈끼리 연산할 때는 인덱스 정렬이 자동으로 일어납니다. 이 동작을 이해하면 데이터 병합과 조인의 원리를 더 쉽게 파악할 수 있습니다.

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20], index=["b", "c"])
print(s1 + s2)
```

인덱스가 맞지 않는 위치에는 NaN이 생깁니다. 이 동작이 Pandas의 강력한 기능이자 조심해야 할 부분입니다.

### 주의사항

인덱스 불일치로 생긴 NaN은 의도한 것인지 확인이 필요합니다. 필요하다면 `fill_value` 파라미터로 기본값을 지정할 수 있습니다.

```python
result = s1.add(s2, fill_value=0)
print(result)
```

이렇게 하면 인덱스가 없는 위치에 0이 채워집니다.

## 데이터프레임 메서드 체이닝

Pandas는 메서드 체이닝을 지원하여 여러 연산을 연결할 수 있습니다.

```python
result = (df
    .assign(total=lambda x: x["price"] * x["qty"])
    .query("total > 100")
    .sort_values("total", ascending=False)
    .head(10)
)
print(result)
```

이 패턴은 코드를 읽기 쉽게 만들어 줍니다.

메서드 체이닝은 Pandas의 강력한 기능이지만, 너무 길어지면 디버깅이 어려워질 수 있습니다. 적절한 길이로 나누는 것이 좋습니다.

## 시리즈 내부 구조

Series는 내부적으로 NumPy 배열과 인덱스를 별도로 관리합니다. 이 구조를 이해하면 성능 최적화와 메모리 관리에 도움이 됩니다.

```python
s = pd.Series([1, 2, 3], index=["a", "b", "c"])
print("Data type:", s.dtype)
print("Array:", s.values)
print("Index:", s.index)
print("Memory:", s.memory_usage(deep=True), "bytes")
```

Series는 동일한 자료형만 담을 수 있습니다. 여러 자료형이 섞이면 `object` 타입으로 변환되어 성능이 떨어집니다. 따라서 생성 시 자료형을 명시적으로 설정하는 편이 좋습니다.

## 연습 문제

1. 시리즈 세 개를 만든 뒤 하나의 데이터프레임으로 합쳐 공통 인덱스를 확인해 보세요.
2. 서로 다른 인덱스를 가진 두 시리즈를 더해 `NaN` 위치를 살펴보세요.
3. `df["x"]`와 `df[["x"]]`의 타입 차이를 코드로 확인해 보세요.

## 정리와 다음 글

데이터프레임은 시리즈를 공통 인덱스 위에 모아 둔 구조입니다. 이 기본 모델을 이해하면 이후의 선택, 집계, 병합도 모두 한층 단단하게 읽힙니다. 다음 글에서는 CSV와 Excel 파일을 정확하게 읽는 방법을 다루겠습니다.

## 처음 질문으로 돌아가기

- **시리즈는 내부적으로 어떤 구조일까요?**
  - 본문의 기준은 시리즈와 데이터프레임를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **데이터프레임을 열 중심으로 본다는 말은 무엇을 뜻할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **인덱스는 왜 단순한 행 번호가 아닐까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- **시리즈와 데이터프레임 (현재 글)**
- CSV와 Excel 읽기 (예정)
- 필터링과 선택 (예정)
- 결측치 처리 (예정)
- 그룹화와 집계 (예정)
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — Series API](https://pandas.pydata.org/docs/reference/series.html)
- [pandas — DataFrame API](https://pandas.pydata.org/docs/reference/frame.html)
- [pandas — Intro to data structures](https://pandas.pydata.org/docs/user_guide/dsintro.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Series, DataFrame, Python, Beginner
