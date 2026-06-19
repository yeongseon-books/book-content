---
series: pandas-101
episode: 1
title: "Pandas 101 (1/10): Pandas란 무엇인가?"
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
  - Python
  - DataAnalysis
  - DataFrame
  - Beginner
seo_description: Pandas의 역할과 DataFrame 사고방식을 처음부터 이해하는 입문 글입니다
last_reviewed: '2026-05-15'
---

# Pandas 101 (1/10): Pandas란 무엇인가?

처음 Pandas를 배울 때 가장 헷갈리는 지점은 도구의 성격입니다. 스프레드시트를 조금 더 편하게 다루는 라이브러리처럼 보이기도 하고, 반대로 데이터 분석 전체를 떠받치는 기반 도구처럼 보이기도 합니다. 입문 단계에서 이 감각을 잘못 잡으면 이후의 필터링, 집계, 조인, 시계열 처리도 모두 흩어진 기능 목록처럼 남습니다.

이 글은 Pandas 101 시리즈의 첫 번째 글입니다.

Pandas를 제대로 이해하려면 기능 이름보다 먼저 역할을 잡아야 합니다. Pandas는 표 데이터를 메모리 안에서 읽고, 살펴보고, 변형하고, 집계하는 기본 작업을 매우 짧은 코드로 풀어내게 해 주는 표준 도구입니다.

![Pandas 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/01/01-01-concept-at-a-glance.ko.png)
*Pandas 101 1장 흐름 개요*
> Pandas는 표 데이터를 다루는 **입력 → 점검 → 변형 → 출력**의 기본 공정입니다. 이 원리를 이해하면 뒷장의 모든 기능이 자연스럽게 연결됩니다.

## 이 글에서 다룰 문제

- Pandas는 정확히 어떤 문제를 해결하는 라이브러리일까요?
- Series와 DataFrame은 어떤 관계로 이해해야 할까요?
- 왜 많은 분석 작업이 Pandas에서 시작될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

CSV, Excel, 데이터베이스, API 응답처럼 실무 데이터의 대부분은 결국 표 형태로 도착합니다. 이때 표 데이터를 빠르게 읽고, 열 단위로 다루고, 상태를 점검하는 기본기가 없으면 분석은 시작도 하기 어렵습니다.

메모리에 들어오는 범위의 데이터라면 Pandas는 여전히 가장 실용적인 출발점입니다. 데이터 과학, 리포트 자동화, 머신러닝 전처리, 운영 지표 계산이 모두 여기서 이어집니다.

## 핵심 개념 정의

- **Series**: 레이블이 붙은 1차원 배열입니다.
- **DataFrame**: 행과 열 모두에 이름이 붙은 2차원 표입니다.
- **인덱스**: 각 행을 식별하는 레이블입니다.
- **dtype**: 열마다 가지는 자료형입니다.
- **벡터화**: 명시적인 반복문 없이 열 단위로 계산하는 방식입니다.

## 설치와 버전 확인

Pandas 작업을 시작하기 전에 환경 설정부터 정리해야 합니다. 설치는 간단하지만, 버전 확인 습관은 팀 협업과 예제 재현에 중요합니다.

```bash
pip install pandas
```

```python
import pandas as pd
import numpy as np

print(pd.__version__)   # 예: 2.2.1
```

Pandas는 1.x와 2.x 사이에 일부 동작이 바뀌었습니다. 이 시리즈는 Pandas 2.x를 기준으로 작성되었습니다.

## 전과 후

이전 관점: "엑셀처럼 행을 하나씩 돌면서 보자"라는 생각에 머무릅니다.

이후 관점: "표 전체를 DataFrame으로 올리고 열 단위로 계산하자"라는 관점으로 바뀝니다.

## 실습: 처음 해 보는 다섯 단계

### 1단계 - 시리즈 만들기

```python
import pandas as pd

s = pd.Series([10, 20, 30], index=["a", "b", "c"])
print(s)
print("합계:", s.sum())
print("평균:", s.mean())
print("최댓값:", s.max())
```

**예상 출력:**

```text
a    10
b    20
c    30
dtype: int64
합계: 60
평균: 20.0
최댓값: 30
```

시리즈는 값과 인덱스가 함께 움직이는 1차원 구조입니다. 단순한 리스트처럼 보여도 합계, 평균, 정렬 연산이 레이블 기준으로 동작한다는 점이 핵심입니다.

### 2단계 - 데이터프레임 만들기

```python
df = pd.DataFrame({
    "name": ["Ada", "Linus", "Grace"],
    "age": [36, 54, 85],
    "lang": ["Python", "C", "COBOL"],
})
print(df)
```

**예상 출력:**

```text
    name  age    lang
0    Ada   36  Python
1  Linus   54       C
2  Grace   85   COBOL
```

데이터프레임은 여러 시리즈를 열 단위로 묶은 구조입니다. 이후 대부분의 Pandas 작업은 이 데이터프레임을 기준으로 진행됩니다.

### 3단계 - 기본 점검하기

```python
print("크기:", df.shape)
print()
print("자료형:\n", df.dtypes)
print()
print("기술 통계:\n", df.describe(include="all"))
```

**예상 출력:**

```text
크기: (3, 3)

자료형:
 name    object
age      int64
lang    object
dtype: object
```

`shape`, `dtypes`, `describe()`는 표를 받았을 때 가장 먼저 보는 기본 점검 세트입니다. 데이터 개수, 열 자료형, 분포를 이 세 줄로 빠르게 확인합니다.

### 4단계 - 조건 필터링하기

```python
print(df[df["age"] > 40])
```

**예상 출력:**

```text
    name  age   lang
1  Linus   54      C
2  Grace   85  COBOL
```

조건 필터링은 표를 통째로 올린 뒤 필요한 행만 잘라 내는 첫 경험입니다. 불리언 인덱싱은 Pandas의 가장 중요한 기본 동작 중 하나입니다.

### 5단계 - 열 계산하기

```python
numbers = pd.DataFrame({
    "a": [1, 2, 3, 4, 5],
    "b": [10, 20, 30, 40, 50],
})
numbers["sum_ab"] = numbers["a"] + numbers["b"]
numbers["ratio"]  = numbers["a"] / numbers["b"]
print(numbers)
```

**예상 출력:**

```text
   a   b  sum_ab  ratio
0  1  10      11    0.1
1  2  20      22    0.1
2  3  30      33    0.1
3  4  40      44    0.1
4  5  50      55    0.1
```

열 단위 계산은 반복문 없이 NumPy 기저 연산으로 처리됩니다. 이것이 Pandas 성능의 핵심입니다.

## 판다스와 순수 파이썬 비교

Pandas를 도입하기 전에 먼저 이런 의문이 듭니다. 파이썬 리스트와 딕셔너리만으로도 표 데이터를 충분히 다룰 수 있지 않을까요. 실제로 가능합니다. 하지만 코드 길이와 성능 차이는 금방 커집니다.

| 작업 | 순수 Python | Pandas |
| --- | --- | --- |
| 필터링 | `[x for x in data if x['age'] > 30]` | `df[df['age'] > 30]` |
| 집계 | `sum([x['amount'] for x in data])` | `df['amount'].sum()` |
| 정렬 | `sorted(data, key=lambda x: x['name'])` | `df.sort_values('name')` |
| 열 추가 | `[x['a'] + x['b'] for x in data]` | `df['c'] = df['a'] + df['b']` |
| 그룹 합계 | 딕셔너리 반복문 수십 줄 | `df.groupby('cat')['val'].sum()` |

위 표에서 보듯 순수 Python에서는 반복문과 리스트 컴프리헨션을 여러 번 거쳐야 합니다. Pandas는 이 모든 작업을 열 중심 연산으로 한 줄에 처리합니다. 성능 차이도 있지만 더 중요한 것은 코드 가독성과 의도의 명확성입니다.

## 성능 비교: 반복문 vs 벡터화

실제 성능 차이를 코드로 확인해 봅니다. 100만 행 기준입니다.

```python
import numpy as np
import time

df = pd.DataFrame({
    "a": np.arange(1_000_000),
    "b": np.arange(1_000_000),
})

# 방법 1: 파이썬 반복문
start = time.time()
result_loop = [df["a"][i] + df["b"][i] for i in range(len(df))]
loop_time = time.time() - start

# 방법 2: Pandas 벡터화
start = time.time()
result_vec = df["a"] + df["b"]
vec_time = time.time() - start

print(f"반복문:   {loop_time:.3f}초")
print(f"벡터화:   {vec_time:.4f}초")
print(f"속도 차이: {loop_time / vec_time:.0f}배")
```

**예상 출력:**

```text
반복문:   1.823초
벡터화:   0.003초
속도 차이: 607배
```

같은 결과를 내는 코드지만 속도는 수백 배 차이가 납니다. 벡터화는 NumPy의 최적화된 C 코드를 활용하기 때문입니다.

## 판다스 생태계

Pandas는 단독으로 동작하는 라이브러리가 아니라 파이썬 데이터 과학 생태계의 중심 축입니다.

### NumPy와의 관계

Pandas는 내부적으로 NumPy 배열을 기반으로 동작합니다. 시리즈나 데이터프레임의 `.values` 속성은 NumPy 배열을 반환합니다.

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
s = pd.Series(arr)
print(type(s.values))    # <class 'numpy.ndarray'>
print(s.values * 2)      # NumPy 연산 그대로 사용 가능
```

### Matplotlib과의 연계

Pandas 데이터프레임은 내장 `.plot()` 메서드로 바로 시각화할 수 있습니다.

```python
import matplotlib.pyplot as plt

df_plot = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar", "Apr"],
    "sales": [100, 130, 90, 150],
})
df_plot.plot(x="month", y="sales", kind="bar", title="월별 매출")
plt.tight_layout()
plt.show()
```

### scikit-learn과의 연동

머신러닝 전처리는 거의 항상 Pandas로 시작합니다.

```python
from sklearn.linear_model import LinearRegression

train = pd.DataFrame({
    "feature1": [1, 2, 3, 4, 5],
    "feature2": [10, 20, 30, 40, 50],
    "target":   [2, 4, 6, 8, 10],
})

X = train[["feature1", "feature2"]].values
y = train["target"].values
model = LinearRegression().fit(X, y)
print("계수:", model.coef_)
```

Pandas는 전처리 계층, scikit-learn은 모델 계층으로 보면 역할이 명확해집니다.

### 도구 선택 기준

| 데이터 규모 | 추천 도구 | 이유 |
| --- | --- | --- |
| < 1GB | Pandas | 성숙한 생태계, 직관적 API |
| 1–10GB | Pandas + category dtype | 타입 최적화로 메모리 절감 |
| > 10GB (단일 머신) | Dask | Pandas API 유지, 병렬 처리 |
| 최고 성능 필요 | Polars | Rust 기반, 매우 빠름 |
| 분산 클러스터 | Spark | 대규모 분산 처리 |

대부분의 실무 분석 작업은 Pandas로 충분합니다.

## 실전 예제: 판매 데이터 분석

지금까지 배운 내용을 종합하여 간단한 판매 데이터를 분석해 봅니다.

```python
sales = pd.DataFrame({
    "product":  ["A", "B", "C", "A", "B", "C"],
    "region":   ["서울", "서울", "부산", "부산", "부산", "서울"],
    "quantity": [10, 15, 8, 12, 20, 5],
    "price":    [100, 150, 80, 100, 150, 80],
})

# 총 매출 열 추가
sales["revenue"] = sales["quantity"] * sales["price"]

# 기본 집계
print("=== 전체 요약 ===")
print(f"총 매출: {sales['revenue'].sum():,}원")
print(f"평균 단가: {sales['price'].mean():.0f}원")
print()

# 제품별 집계
print("=== 제품별 총 매출 ===")
print(sales.groupby("product")["revenue"].sum())
print()

# 지역별 집계
print("=== 지역별 평균 판매량 ===")
print(sales.groupby("region")["quantity"].mean())
```

**예상 출력:**

```text
=== 전체 요약 ===
총 매출: 9,450원
평균 단가: 110원

=== 제품별 총 매출 ===
product
A    2200
B    5250
C    1040
Name: revenue, dtype: int64

=== 지역별 평균 판매량 ===
region
부산    13.333333
서울     6.666667
Name: quantity, dtype: float64
```

이 예제는 DataFrame 생성, 열 추가, 집계, 그룹화를 모두 포함합니다.

## 디버깅 팁

Pandas 코드를 작성할 때 자주 마주치는 문제를 정리합니다.

### 예상과 다른 결과

먼저 데이터의 크기와 타입을 확인하세요.

```python
print(df.shape)       # (행 수, 열 수)
print(df.dtypes)      # 각 열의 자료형
print(df.head(3))     # 첫 3행
print(df.info())      # 메모리 포함 전체 요약
```

### SettingWithCopyWarning 해결

```python
# 나쁜 패턴 - 경고 발생
df[df["age"] > 0]["score"] = 100

# 좋은 패턴 - loc 사용
df.loc[df["age"] > 0, "score"] = 100
```

### 자료형 문제 진단

```python
# 숫자처럼 보이지만 문자열인 경우
df["price"] = pd.to_numeric(df["price"], errors="coerce")
print(df["price"].dtype)    # float64 확인
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 반복문으로 행 순회 | 느린 실행, 장황한 코드 | 벡터화 연산으로 대체 |
| 자료형 미확인 | 숫자 열이 object로 읽힘 | `dtypes` 먼저 점검 |
| SettingWithCopyWarning 무시 | 수정이 반영되지 않음 | `.loc` 사용 |
| 인덱스 의미 미파악 | `reset_index` 필요 시점 혼란 | 인덱스 역할 명확히 정의 |
| 메모리 점검 생략 | 대용량 로드 시 OOM | `df.info()` 선행 확인 |

## 실무에서는 이렇게 생각합니다

- 데이터를 받으면 먼저 크기와 자료형부터 확인합니다.
- 벡터화가 가능한데도 `apply`부터 쓰지 않습니다.
- 인덱스를 의미 없는 번호가 아니라 식별 키로 볼 수 있는지 판단합니다.
- 복사와 뷰의 차이를 의식합니다.
- 메모리가 한계라면 그때 Polars나 Dask 같은 다음 도구를 검토합니다.

## 운영 체크리스트

- [ ] 데이터프레임을 직접 만들 수 있습니다.
- [ ] `shape`, `dtypes`, `describe()`를 바로 호출할 수 있습니다.
- [ ] 불리언 인덱싱으로 조건 필터링을 할 수 있습니다.
- [ ] 시리즈와 데이터프레임의 차이를 설명할 수 있습니다.
- [ ] 벡터화와 반복문의 성능 차이를 이해하고 있습니다.

## 연습 문제

1. 3행 4열 데이터프레임을 만들고 각 열의 평균을 출력해 보세요.
2. 시리즈와 파이썬 리스트의 차이를 세 가지 적어 보세요.
3. `describe()`와 `describe(include="all")`의 출력 차이를 비교해 보세요.
4. 100만 행 데이터프레임에서 반복문과 벡터화의 실행 시간을 직접 측정해 보세요.

## 정리와 다음 글

Pandas는 표 데이터를 다루는 파이썬의 표준 작업대입니다. 이 출발점을 잡아 두면 이후 장에서 등장할 선택, 집계, 병합, 시계열 처리도 모두 같은 문법 안에서 이어집니다. 다음 글에서는 시리즈와 데이터프레임의 내부 구조를 더 구체적으로 다루겠습니다.

## 처음 질문으로 돌아가기

- **Pandas는 정확히 어떤 문제를 해결하는 라이브러리일까요?**
  - 표 데이터를 메모리에서 읽고, 변형하고, 집계하는 작업을 짧은 코드로 풀어주는 도구입니다. CSV, Excel, DB에서 온 데이터를 모두 같은 방식으로 다룹니다.
- **Series와 DataFrame은 어떤 관계로 이해해야 할까요?**
  - DataFrame은 같은 인덱스를 공유하는 Series들의 묶음입니다. 열 하나를 선택하면 Series가 반환됩니다.
- **왜 많은 분석 작업이 Pandas에서 시작될까요?**
  - 데이터 형식에 관계없이 표 구조로 통일한 뒤, 벡터화된 연산으로 빠르게 가공할 수 있기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- **Pandas 101 (1/10): Pandas란 무엇인가? (현재 글)**
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
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

- [pandas — Official Documentation](https://pandas.pydata.org/docs/)
- [10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)
- [Real Python — Pandas Tutorials](https://realpython.com/learning-paths/pandas-data-science/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, Python, DataAnalysis, DataFrame, Beginner
