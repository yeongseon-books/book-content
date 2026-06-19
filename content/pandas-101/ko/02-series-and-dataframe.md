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

시리즈는 값만 담는 배열이 아니라 레이블과 이름까지 갖춘 구조입니다. 이후 정렬과 연산은 이 레이블을 기준으로 움직입니다.

이 글은 판다스 101 시리즈의 2번째 글입니다.

Pandas를 쓰기 시작하면 금방 이런 질문이 나옵니다. 시리즈와 데이터프레임은 이름만 다른 두 자료구조일까요, 아니면 하나의 모델을 다른 크기로 보여 주는 걸까요. 이 관계를 초반에 분명히 잡아 두지 않으면 열 선택, 정렬, 산술 연산, 조인에서 계속 감으로만 코드를 쓰게 됩니다.

이번 글의 핵심은 간단합니다. 데이터프레임은 서로 같은 레이블 체계를 공유하는 시리즈의 묶음입니다. 이 관점을 잡으면 Pandas의 많은 동작이 훨씬 자연스럽게 읽힙니다.

![Pandas 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/02/02-01-concept-at-a-glance.ko.png)
*Pandas 101 2장 흐름 개요*
> 데이터프레임은 시리즈의 **묶음**입니다. 이 관점을 갖추면 정렬, 결합, 열 연산이 모두 같은 원리로 작동하는 이유가 명확해집니다.

## 이 글에서 다룰 문제

- 시리즈는 내부적으로 어떤 구조일까요?
- 데이터프레임을 열 중심으로 본다는 말은 무엇을 뜻할까요?
- 인덱스는 왜 단순한 행 번호가 아닐까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

Pandas의 대부분 연산은 결국 시리즈 수준의 계산으로 환원됩니다. 데이터프레임의 한 열이 시리즈라는 사실을 이해하면 열 선택이 왜 특정 타입을 반환하는지, 왜 인덱스 정렬이 자동으로 일어나는지, 왜 레이블이 숫자 배열만큼 중요한지가 한 번에 연결됩니다.

## 핵심 개념 정의

- **Series**: 값과 인덱스를 함께 가진 1차원 구조입니다.
- **DataFrame**: 공통 인덱스를 공유하는 시리즈들의 묶음입니다.
- **값 배열**: 내부 계산에 쓰이는 기저 NumPy 배열입니다.
- **인덱스**: 행 레이블입니다.
- **열 레이블**: 각 시리즈를 구분하는 이름입니다.

## 전과 후

이전 관점: 데이터프레임을 그저 행과 열이 있는 표로만 봅니다.

이후 관점: 데이터프레임을 여러 시리즈가 같은 인덱스 위에 놓인 구조로 이해합니다.

## 실습: 구조를 직접 만들어 보기

### 1단계 - 시리즈 만들고 속성 보기

```python
import pandas as pd

s = pd.Series([1.0, 2.0, 3.0], index=["a", "b", "c"], name="score")
print(s)
print()
print("값 배열:", s.values)
print("인덱스:", s.index.tolist())
print("이름:", s.name)
print("자료형:", s.dtype)
print("메모리:", s.memory_usage(deep=True), "bytes")
```

**예상 출력:**

```text
a    1.0
b    2.0
c    3.0
Name: score, dtype: float64

값 배열: [1. 2. 3.]
인덱스: ['a', 'b', 'c']
이름: score
자료형: float64
메모리: 152 bytes
```

시리즈는 값만 담는 배열이 아니라 레이블과 이름까지 갖춘 구조입니다. 이후 정렬과 연산은 이 레이블을 기준으로 움직입니다.

### 2단계 - 시리즈끼리 계산하기

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20, 30], index=["b", "c", "d"])

print("s1 + s2 (인덱스 정렬 자동 적용):")
print(s1 + s2)
print()
print("fill_value=0 적용:")
print(s1.add(s2, fill_value=0))
```

**예상 출력:**

```text
s1 + s2 (인덱스 정렬 자동 적용):
a     NaN
b    12.0
c    23.0
d     NaN
dtype: float64

fill_value=0 적용:
a     1.0
b    12.0
c    23.0
d    30.0
dtype: float64
```

Pandas는 단순히 같은 위치의 값을 더하지 않습니다. 먼저 인덱스를 맞춘 뒤 계산하고, 맞지 않는 위치는 `NaN`으로 남깁니다. `fill_value`로 기본값을 지정하면 NaN 없이 처리할 수 있습니다.

### 3단계 - 데이터프레임 만들기

```python
df = pd.DataFrame({
    "x": [1, 2, 3],
    "y": [10, 20, 30],
    "z": [100, 200, 300],
}, index=["a", "b", "c"])
print(df)
print()
print("열 목록:", df.columns.tolist())
print("인덱스:", df.index.tolist())
```

**예상 출력:**

```text
   x   y    z
a  1  10  100
b  2  20  200
c  3  30  300

열 목록: ['x', 'y', 'z']
인덱스: ['a', 'b', 'c']
```

이 데이터프레임은 같은 인덱스를 공유하는 세 개의 시리즈를 옆으로 붙여 둔 것처럼 볼 수 있습니다. 그래서 열 단위 연산이 자연스럽습니다.

### 4단계 - 열 하나를 고르면 시리즈가 나옵니다

```python
col = df["x"]
print(type(col))        # <class 'pandas.core.series.Series'>
print(col)
print()
# 1열 DataFrame은 대괄호 두 겹
col_df = df[["x"]]
print(type(col_df))     # <class 'pandas.core.frame.DataFrame'>
print(col_df)
```

**예상 출력:**

```text
<class 'pandas.core.series.Series'>
a    1
b    2
c    3
Name: x, dtype: int64

<class 'pandas.core.frame.DataFrame'>
   x
a  1
b  2
c  3
```

`df["x"]`가 데이터프레임이 아니라 시리즈라는 사실은 매우 중요합니다. 열 선택 뒤에 이어지는 메서드와 연산이 모두 시리즈 문법으로 연결되기 때문입니다.

### 5단계 - 다양한 DataFrame 생성법 비교

```python
import numpy as np

# 방법 1: 딕셔너리
df1 = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

# 방법 2: 리스트 of 딕셔너리 (JSON API 응답 형태)
records = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
df2 = pd.DataFrame(records)

# 방법 3: NumPy 배열
arr = np.random.randint(0, 100, size=(3, 4))
df3 = pd.DataFrame(arr, columns=["w", "x", "y", "z"])

# 방법 4: 시리즈에서
s_a = pd.Series([10, 20, 30], name="sales")
s_b = pd.Series([1.0, 2.0, 3.0], name="growth")
df4 = pd.DataFrame({"sales": s_a, "growth": s_b})

print("딕셔너리 방식:\n", df1)
print("\n레코드 방식:\n", df2)
print("\nNumPy 방식:\n", df3)
print("\n시리즈 방식:\n", df4)
```

각 방법은 데이터 원본 형태에 따라 선택하면 됩니다. API 응답처럼 행별로 오는 데이터는 레코드 방식이 자연스럽고, 수치 행렬은 NumPy 방식이 편합니다.

## 시리즈와 데이터프레임 비교

| 항목 | Series | DataFrame |
| --- | --- | --- |
| 차원 | 1차원 | 2차원 |
| 인덱스 | 행 레이블 | 행 레이블 (공유) |
| 열 레이블 | 없음 (name 속성) | 있음 (columns) |
| 생성 방법 | `pd.Series(list, index=...)` | `pd.DataFrame(dict)` |
| 열 선택 결과 | - | Series 반환 |
| 사용 예 | 단일 측정값 시리즈 | 복수 열 데이터 테이블 |

DataFrame은 같은 인덱스를 공유하는 Series의 묶음으로 볼 수 있습니다. 그래서 `df['column']`은 Series를 반환하고, `df[['column']]`은 1열 DataFrame을 반환합니다.

## 자료형 확인과 변환

데이터프레임의 각 열은 자료형을 가집니다. 이 자료형을 명시적으로 확인하고 변환하는 것이 후속 연산의 정확성을 보장합니다.

```python
df = pd.DataFrame({
    "id":    ["001", "002", "003"],
    "score": ["85.5", "90.0", "78.5"],   # 문자열로 읽힌 경우
    "grade": ["A", "A", "B"],
})
print("변환 전:\n", df.dtypes)
print()

# 자료형 변환
df["id"]    = df["id"].astype("string")
df["score"] = pd.to_numeric(df["score"])   # errors="coerce"로 오류 처리 가능
df["grade"] = df["grade"].astype("category")

print("변환 후:\n", df.dtypes)
print()
print(df)
```

**예상 출력:**

```text
변환 전:
 id       object
score    object
grade    object
dtype: object

변환 후:
 id      string
score    float64
grade    category
dtype: object
```

Pandas는 자동으로 자료형을 추론하지만, 항상 정확한 것은 아닙니다. 문자열로 저장된 숫자나 범주형 데이터는 명시적 변환이 필요합니다.

## 메모리 효율: 자료형 선택의 중요성

```python
import numpy as np

n = 1_000_000
df_mem = pd.DataFrame({
    "int_default": np.arange(n, dtype="int64"),
    "int_small":   np.arange(n, dtype="int32"),
    "float64":     np.random.rand(n),
    "float32":     np.random.rand(n).astype("float32"),
    "str_col":     ["category_A"] * (n // 2) + ["category_B"] * (n // 2),
})

print("기본 메모리 사용량 (MB):")
for col in df_mem.columns:
    mb = df_mem[col].memory_usage(deep=True) / 1024 / 1024
    print(f"  {col}: {mb:.1f} MB")

# category 변환 후
df_mem["str_cat"] = df_mem["str_col"].astype("category")
orig_mb = df_mem["str_col"].memory_usage(deep=True) / 1024 / 1024
cat_mb  = df_mem["str_cat"].memory_usage(deep=True) / 1024 / 1024
print(f"\nstring → category 절감: {orig_mb:.1f}MB → {cat_mb:.1f}MB")
```

**예상 출력:**

```text
기본 메모리 사용량 (MB):
  int_default: 7.6 MB
  int_small: 3.8 MB
  float64: 7.6 MB
  float32: 3.8 MB
  str_col: 58.5 MB

string → category 절감: 58.5MB → 0.7MB
```

고유값이 적은 문자열 열은 category 타입으로 변환하면 메모리를 80배 이상 절감할 수 있습니다.

## copy vs view 주의사항

```python
df_orig = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})

# view - 원본 공유 (Pandas 2.x에서는 경고 발생)
subset_view = df_orig[["x"]]

# copy - 독립적인 복사본 (안전)
subset_copy = df_orig[["x"]].copy()

# 복사본 수정은 원본에 영향 없음
subset_copy["x"] = 999
print("원본:", df_orig["x"].tolist())     # [1, 2, 3] 유지
print("복사본:", subset_copy["x"].tolist())  # [999, 999, 999]
```

할당을 할 때는 복사본을 명시적으로 만들어 `SettingWithCopyWarning`을 피하세요.

## 메서드 체이닝 패턴

Pandas는 메서드 체이닝을 지원하여 여러 연산을 가독성 있게 연결할 수 있습니다.

```python
result = (
    pd.DataFrame({
        "product": ["A", "B", "C", "A", "B"],
        "qty":     [10, 5, 8, 12, 3],
        "price":   [100, 200, 150, 100, 200],
    })
    .assign(revenue=lambda x: x["qty"] * x["price"])
    .query("revenue > 500")
    .sort_values("revenue", ascending=False)
    .reset_index(drop=True)
)
print(result)
```

**예상 출력:**

```text
  product  qty  price  revenue
0       A   12    100     1200
1       A   10    100     1000
2       C    8    150     1200
```

메서드 체이닝은 코드를 읽기 쉽게 만들어 줍니다. 너무 길어지면 디버깅이 어려워지므로 적절한 길이로 나누는 것이 좋습니다.

## 인덱스 연산 심화

```python
# 시계열 예제: 날짜 인덱스
dates = pd.date_range("2026-01-01", periods=5, freq="D")
temp    = pd.Series([15, 16, 14, 17, 16], index=dates, name="temperature")
humid   = pd.Series([60, 65, 55, 70, 68], index=dates, name="humidity")

weather = pd.DataFrame({"temp": temp, "humidity": humid})
print(weather)
print()
print("평균 기온:", weather["temp"].mean())
print("최고 습도:", weather["humidity"].max())
print()

# 날짜 슬라이싱
print("1월 3일 이후:")
print(weather.loc["2026-01-03":])
```

**예상 출력:**

```text
            temp  humidity
2026-01-01    15        60
2026-01-02    16        65
2026-01-03    14        55
2026-01-04    17        70
2026-01-05    16        68

평균 기온: 15.6
최고 습도: 70

1월 3일 이후:
            temp  humidity
2026-01-03    14        55
2026-01-04    17        70
2026-01-05    16        68
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `df["x"]`를 DataFrame으로 착각 | `.columns` 호출 오류 | `type()` 확인 후 `df[["x"]]` 사용 |
| 인덱스 어긋남 NaN을 결측치로만 봄 | 의도치 않은 NaN 발생 | `fill_value` 또는 인덱스 정렬 확인 |
| `values`로 넘겨 레이블 정보 손실 | 인덱스 기반 연산 불가 | Series/DataFrame 그대로 전달 |
| `name` 속성 무시 | groupby 후 열 이름 혼란 | `.rename()` 또는 `name=` 명시 |
| 행 순서가 같다고 가정하고 더함 | 잘못된 값 계산 | 인덱스 기준 연산 사용 |

## 실무에서는 이렇게 생각합니다

- 먼저 인덱스가 무엇을 의미하는지 분명히 합니다.
- 열 선택은 곧 시리즈 사고방식으로 넘어가는 순간이라고 봅니다.
- 정렬 불일치에서 생긴 `NaN`을 디버깅 단서로 활용합니다.
- `df.values` 의존도를 낮춥니다.
- 시리즈 이름을 적극적으로 붙여 흐름을 읽기 쉽게 만듭니다.

## 운영 체크리스트

- [ ] 시리즈와 데이터프레임을 구분할 수 있습니다.
- [ ] 인덱스와 열 레이블의 역할을 설명할 수 있습니다.
- [ ] `df["col"]`이 시리즈임을 알고 있습니다.
- [ ] 인덱스 정렬이 자동이라는 점을 이해하고 있습니다.
- [ ] category 타입 변환으로 메모리를 절감할 수 있습니다.

## 연습 문제

1. 시리즈 세 개를 만든 뒤 하나의 데이터프레임으로 합쳐 공통 인덱스를 확인해 보세요.
2. 서로 다른 인덱스를 가진 두 시리즈를 더해 `NaN` 위치를 살펴보세요.
3. `df["x"]`와 `df[["x"]]`의 타입 차이를 코드로 확인해 보세요.
4. 문자열 열을 category로 바꾸기 전후의 메모리 사용량을 비교해 보세요.

## 정리와 다음 글

데이터프레임은 시리즈를 공통 인덱스 위에 모아 둔 구조입니다. 이 기본 모델을 이해하면 이후의 선택, 집계, 병합도 모두 한층 단단하게 읽힙니다. 다음 글에서는 CSV와 Excel 파일을 정확하게 읽는 방법을 다루겠습니다.

## 처음 질문으로 돌아가기

- **시리즈는 내부적으로 어떤 구조일까요?**
  - NumPy 배열과 인덱스를 별도로 관리합니다. 값은 `.values`, 레이블은 `.index`, 이름은 `.name`으로 접근합니다.
- **데이터프레임을 열 중심으로 본다는 말은 무엇을 뜻할까요?**
  - 각 열이 독립적인 시리즈이므로, 열 단위 연산이 행 반복보다 훨씬 빠르고 자연스럽습니다.
- **인덱스는 왜 단순한 행 번호가 아닐까요?**
  - 인덱스는 연산의 기준 레이블입니다. 두 시리즈를 더할 때 위치가 아니라 레이블을 맞춰 계산하기 때문에 레이블 불일치 시 NaN이 발생합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- **Pandas 101 (2/10): 시리즈와 데이터프레임 (현재 글)**
- [Pandas 101 (3/10): CSV와 Excel 읽기](./03-read-csv-and-excel.md)
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — Series API](https://pandas.pydata.org/docs/reference/series.html)
- [pandas — DataFrame API](https://pandas.pydata.org/docs/reference/frame.html)
- [pandas — Intro to data structures](https://pandas.pydata.org/docs/user_guide/dsintro.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Series, DataFrame, Python, Beginner
