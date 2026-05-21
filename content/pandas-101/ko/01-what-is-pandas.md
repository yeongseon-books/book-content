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

## 먼저 던지는 질문

- Pandas는 정확히 어떤 문제를 해결하는 라이브러리일까요?
- Series와 DataFrame은 어떤 관계로 이해해야 할까요?
- 왜 많은 분석 작업이 Pandas에서 시작될까요?

## 큰 그림

![Pandas 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/01/01-01-concept-at-a-glance.ko.png)

*Pandas 101 1장 흐름 개요*

이 그림은 데이터를 처음 받았을 때의 기본 점검 순서를 보여 줍니다. CSV나 Excel 파일이 들어오면 가장 먼저 크기와 자료형을 확인합니다. 이후 모든 선택과 연산은 이 기본기 위에 세워집니다.

> Pandas는 표 데이터를 다루는 **입력 → 점검 → 변형 → 출력**의 기본 공정입니다. 이 원리를 이해하면 뒷장의 모든 기능이 자연스럽게 연결됩니다.

## 왜 중요한가

CSV, Excel, 데이터베이스, API 응답처럼 실무 데이터의 대부분은 결국 표 형태로 도착합니다. 이때 표 데이터를 빠르게 읽고, 열 단위로 다루고, 상태를 점검하는 기본기가 없으면 분석은 시작도 하기 어렵습니다.

메모리에 들어오는 범위의 데이터라면 Pandas는 여전히 가장 실용적인 출발점입니다. 데이터 과학, 리포트 자동화, 머신러닝 전처리, 운영 지표 계산이 모두 여기서 이어집니다.

## 한눈에 보는 개념

## 핵심 용어

- 시리즈: 레이블이 붙은 1차원 배열입니다.
- **데이터프레임**: 행과 열 모두에 이름이 붙은 2차원 표입니다.
- 인덱스: 각 행을 식별하는 레이블입니다.
- **데이터 형식**: 열마다 가지는 자료형입니다.
- 벡터화: 명시적인 반복문 없이 열 단위로 계산하는 방식입니다.

## 설치와 버전 확인

Pandas 작업을 시작하기 전에 환경 설정부터 정리해야 합니다. 설치는 간단하지만, 버전 확인 습관은 팀 협업과 예제 재현에 중요합니다.

### 설치 방법

```bash
pip install pandas
```

만약 Jupyter 환경에서 작업한다면 다음처럼 설치할 수 있습니다:

```python
!pip install pandas
```

### 버전 확인

```python
import pandas as pd
print(pd.__version__)
```

Pandas는 1.x와 2.x 사이에 일부 동작이 바뀌었습니다. 예제 코드를 따라 하다 경고가 나오면 먼저 버전을 확인하세요. 이 시리즈는 Pandas 2.x를 기준으로 작성되었습니다.

### 자주 쓰는 import 패턴

대부분의 Pandas 코드는 다음 형태로 시작합니다:

```python
import pandas as pd
import numpy as np
```

이 import 관례는 거의 모든 Pandas 예제와 문서에서 동일하게 씁니다. 가독성과 일관성을 위해 이 패턴을 따르세요.

## 전과 후

이전 관점: "엑셀처럼 행을 하나씩 돌면서 보자"라는 생각에 머무릅니다.

이후 관점: "표 전체를 DataFrame으로 올리고 열 단위로 계산하자"라는 관점으로 바뀝니다.

## 실습: 처음 해 보는 다섯 단계

### 1단계 - 설치하고 불러오기

```python
# pip install pandas
import pandas as pd
print(pd.__version__)
```

Pandas 작업은 거의 항상 `import pandas as pd`로 시작합니다. 버전을 먼저 확인해 두면 예제 재현이나 팀 내 환경 차이를 점검할 때 도움이 됩니다.

### 2단계 - 시리즈 만들기

```python
s = pd.Series([10, 20, 30], index=["a", "b", "c"])
print(s)
print("sum:", s.sum())
```

시리즈는 값과 인덱스가 함께 움직이는 1차원 구조입니다. 단순한 리스트처럼 보여도 합계, 정렬, 정렬 기반 연산이 바로 가능한 점이 핵심입니다.

## Pandas vs 순수 Python

Pandas를 도입하기 전에 먼저 이런 의문이 듭니다. 파이썬 리스트와 딕셔너리만으로도 표 데이터를 충분히 다룰 수 있지 않을까요. 실제로 가능합니다. 하지만 코드 길이와 성능 차이는 금방 커집니다.

| 작업 | 순수 Python | Pandas |
| --- | --- | --- |
| 필터링 | `[x for x in data if x['age'] > 30]` | `df[df['age'] > 30]` |
| 집계 | `sum([x['amount'] for x in data])` | `df['amount'].sum()` |
| 정렬 | `sorted(data, key=lambda x: x['name'])` | `df.sort_values('name')` |

위 표에서 보듯 순수 Python에서는 반복문과 리스트 컴프리헨션을 여러 번 거쳐야 합니다. Pandas는 이 모든 작업을 열 중심 연산으로 한 줄에 처리합니다. 성능 차이도 있지만 더 중요한 것은 코드 가독성입니다. 표 데이터를 다루는 의도가 문법으로 명확하게 드러나는 것이 Pandas의 핵심 가치입니다.

### 3단계 - 데이터프레임 만들기

```python
df = pd.DataFrame({
    "name": ["Ada", "Linus", "Grace"],
    "age": [36, 54, 85],
})
print(df)
```

실제로는 표 전체가 한 번에 출력되는지 확인하는 것이 중요합니다. 열 이름, 행 수, 값 모양을 눈으로 먼저 보는 습관이 이후 실수를 줄여 줍니다.

**예상 출력:**

```text
    name  age
0    Ada   36
1  Linus   54
2  Grace   85
```

데이터프레임은 여러 시리즈를 열 단위로 묶은 구조라고 생각하면 이해가 빠릅니다. 이후 대부분의 Pandas 작업은 이 데이터프레임을 기준으로 진행됩니다.

### 4단계 - 처음 요약해 보기

```python
print(df.shape)
print(df.dtypes)
print(df.describe(include="all"))
```

`shape`, `dtypes`, `describe()`는 표를 받았을 때 가장 먼저 보는 기본 점검 세트입니다. 데이터 개수, 열 자료형, 분포를 이 세 줄로 빠르게 확인할 수 있습니다.

### 5단계 - 처음 필터링해 보기

```python
print(df[df["age"] > 40])
```

조건 필터링은 표를 통째로 올린 뒤 필요한 행만 잘라 내는 첫 경험입니다. 결과가 한두 행으로 줄어드는지 바로 확인해 두면 조건식이 제대로 동작하는지 빠르게 검증할 수 있습니다.

**예상 출력:**

```text
    name  age
1  Linus   54
2  Grace   85
```

조건식으로 행을 고르는 불리언 인덱싱은 Pandas의 가장 중요한 기본 동작 중 하나입니다. 이후의 조건 선택, 이상치 탐지, 데이터 분할이 모두 여기서 이어집니다.

## 이 코드에서 먼저 봐야 할 점

- 데이터프레임은 열 중심 구조라서 열마다 자료형이 다를 수 있습니다.
- `describe()`는 숫자 요약을 확인하는 첫 도구입니다.
- 불리언 인덱싱은 SQL의 `WHERE`에 해당하는 감각으로 보면 됩니다.

## 자주 하는 실수 다섯 가지

1. 반복문으로 행을 하나씩 순회하면서 Pandas의 장점을 버립니다.
2. 자료형을 확인하지 않아 숫자처럼 보이는 문자열을 놓칩니다.
3. `SettingWithCopyWarning`를 단순 경고로 넘깁니다.
4. 인덱스의 의미를 이해하지 못한 채 `reset_index`가 필요한 시점을 놓칩니다.
5. `df.info()` 같은 메모리 점검 없이 데이터 크기부터 키웁니다.

## 실무에서는 이렇게 이어집니다

데이터 정제, 지표 계산, 리포트 생성, 머신러닝 전처리까지 거의 모든 분석 파이프라인은 Pandas에서 출발합니다. 특히 노트북 환경에서는 Pandas가 표 데이터를 이해하는 기본 언어 역할을 합니다.

## 실무에서는 이렇게 생각합니다

- 데이터를 받으면 먼저 크기와 자료형부터 확인합니다.
- 벡터화가 가능한데도 `apply`부터 쓰지 않습니다.
- 인덱스를 의미 없는 번호가 아니라 식별 키로 볼 수 있는지 판단합니다.
- 복사와 뷰의 차이를 의식합니다.
- 메모리가 한계라면 그때 Polars나 Dask 같은 다음 도구를 검토합니다.

## Pandas 생태계

Pandas는 단독으로 동작하는 라이브러리가 아니라 파이썬 데이터 과학 생태계의 중심 축입니다. 대부분의 데이터 작업은 여러 라이브러리를 조합하는 방식으로 이루어집니다.

### NumPy와의 관계

Pandas는 내부적으로 NumPy 배열을 기반으로 동작합니다. 그래서 Pandas의 빠른 연산 속도는 NumPy에서 나옵니다. 시리즈나 데이터프레임의 `.values` 속성은 바로 NumPy 배열을 반환합니다.

```python
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
s = pd.Series(arr)
print(type(s.values))  # <class 'numpy.ndarray'>
```

NumPy를 직접 다룰 필요는 없지만, Pandas를 깊이 이해하려면 NumPy의 배열 개념을 알아 두는 편이 좋습니다.

### Matplotlib과의 연계

Pandas 데이터프레임은 바로 시각화로 이어질 수 있습니다. 내장 `.plot()` 메서드는 Matplotlib을 백엔드로 씁니다.

```python
import matplotlib.pyplot as plt
df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
df.plot(x='x', y='y', kind='line')
plt.show()
```

복잡한 시각화는 Seaborn이나 Plotly로 넘어가지만, 빠른 탐색에서는 Pandas 내장 그래프만으로도 충분합니다.

### scikit-learn과의 연동

머신러닝 전처리는 거의 항상 Pandas로 시작합니다. 데이터를 읽고, 정제하고, 특징을 추출한 뒤 NumPy 배열이나 Pandas 데이터프레임 형태로 scikit-learn에 넘깁니다.

```python
from sklearn.linear_model import LinearRegression
X = df[['feature1', 'feature2']].values
y = df['target'].values
model = LinearRegression().fit(X, y)
```

Pandas는 전처리 계층, scikit-learn은 모델 계층으로 보면 역할이 명확해집니다.

## 체크리스트

- [ ] 데이터프레임을 직접 만들 수 있습니다.
- [ ] `shape`, `dtypes`, `describe()`를 바로 호출할 수 있습니다.
- [ ] 불리언 인덱싱으로 조건 필터링을 할 수 있습니다.
- [ ] 시리즈와 데이터프레임의 차이를 설명할 수 있습니다.

## 실전 예제: 판매 데이터 분석

이제까지 배운 내용을 종합하여 간단한 판매 데이터를 분석해 보겠습니다.

```python
sales = pd.DataFrame({
    "product": ["A", "B", "C", "A", "B"],
    "quantity": [10, 15, 8, 12, 20],
    "price": [100, 150, 80, 100, 150],
})
sales["total"] = sales["quantity"] * sales["price"]
print(sales)
print("\n총 매출:", sales["total"].sum())
print("제품별 평균 판매량:", sales.groupby("product")["quantity"].mean())
```

이 예제는 DataFrame 생성, 열 추가, 집계, 그룹화를 모두 포함합니다. 실무에서는 이보다 훨씬 복잡한 데이터를 다루지만, 기본 원리는 동일합니다.

## 디버깅 팁

Pandas 코드를 작성할 때 자주 마주치는 문제와 해결 방법을 정리해 두면 디버깅 시간을 크게 줄일 수 있습니다.

### 예상과 다른 결과

먼저 데이터의 크기와 타입을 확인하세요:

```python
print(df.shape)    # (rows, columns)
print(df.dtypes)   # column types
print(df.head())   # first 5 rows
```

### 연산 결과가 이상할 때

열 이름을 다시 확인하고, 인덱스가 예상대로 정렬되어 있는지 확인하세요:

```python
print(df.columns.tolist())
print(df.index)
```

### SettingWithCopyWarning

이 경고는 쳋인 인덱싱을 사용할 때 나타납니다. `.loc`를 사용하여 명시적으로 할당하세요:

```python
# Bad
df[df['x'] > 0]['y'] = 100

# Good
df.loc[df['x'] > 0, 'y'] = 100
```


## Pandas와 다른 도구의 비교

Pandas가 유일한 선택은 아닙니다. 다른 도구와의 차이를 알아두면 상황에 맞는 선택을 할 수 있습니다.

### Polars

Polars는 현대적인 DataFrame 라이브러리로 Rust로 작성되었습니다. Pandas보다 빠르고 메모리 효율적이지만, 생태계와 커뮤니티는 아직 Pandas가 훨씬 큽니다.

```python
# Pandas
df = pd.read_csv("data.csv")
result = df[df["x"] > 10]

# Polars
import polars as pl
df = pl.read_csv("data.csv")
result = df.filter(pl.col("x") > 10)
```

### Dask

Dask는 Pandas API를 그대로 유지하면서 병렬 처리를 지원합니다. 메모리보다 큰 데이터를 다룰 때 유용하지만, 단일 머신 환경에서는 Pandas가 더 빠르고 간편합니다.




### 선택 기준

- 메모리에 올라가는 데이터 (<10GB): Pandas
- 병렬 처리 필요 (>10GB): Dask
- 분산 클러스터: Spark
- 최고 성능: Polars

대부분의 분석 작업은 Pandas로 충분합니다.

## 연습 문제

1. 3행 4열 데이터프레임을 만들고 각 열의 평균을 출력해 보세요.
2. 시리즈와 파이썬 리스트의 차이를 세 가지 적어 보세요.
3. `describe()`와 `describe(include="all")`의 출력 차이를 비교해 보세요.

## 정리와 다음 글

Pandas는 표 데이터를 다루는 파이썬의 표준 작업대입니다. 이 출발점을 잡아 두면 이후 장에서 등장할 선택, 집계, 병합, 시계열 처리도 모두 같은 문법 안에서 이어집니다. 다음 글에서는 시리즈와 데이터프레임의 내부 구조를 더 구체적으로 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **Pandas는 정확히 어떤 문제를 해결하는 라이브러리일까요?**
  - 본문의 기준은 Pandas란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Series와 DataFrame은 어떤 관계로 이해해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 많은 분석 작업이 Pandas에서 시작될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Pandas란 무엇인가? (현재 글)**
- 시리즈와 데이터프레임 (예정)
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

- [pandas — Official Documentation](https://pandas.pydata.org/docs/)
- [10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)
- [Real Python — Pandas Tutorials](https://realpython.com/learning-paths/pandas-data-science/)

Tags: Pandas, Python, DataAnalysis, DataFrame, Beginner
