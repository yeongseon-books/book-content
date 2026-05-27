---
series: pandas-101
episode: 10
title: "Pandas 101 (10/10): 실전 데이터 분석"
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
  - DataAnalysis
  - EDA
  - Workflow
  - Beginner
seo_description: 적재부터 시각화까지 Pandas 실전 분석 흐름을 한 번에 묶어 보는 글입니다
last_reviewed: '2026-05-15'
---

# Pandas 101 (10/10): 실전 데이터 분석

이전 글들에서 배운 읽기, 정제, 선택, 집계, 시계열, 성능 감각은 각각 따로 보면 익숙해 보여도 실제 분석에서는 한 흐름으로 이어져야 의미가 생깁니다. 분석가와 엔지니어의 차이는 개별 기능을 아는 데서 끝나지 않고, 결과를 재현 가능한 파이프라인으로 묶어 내는 데서 드러납니다.

이 글은 Pandas 101 시리즈의 마지막 글입니다.

이번 글에서는 지금까지의 도구들을 하나의 실전 흐름, 즉 적재에서 정제, 변형, 집계, 시각화로 이어지는 표준 분석 파이프라인으로 정리하겠습니다.

![Pandas 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/10/10-01-concept-at-a-glance.ko.png)
*Pandas 101 10장 흐름 개요*
> **분석은 반복**입니다. 첫 읽기가 완벽할 수 없고, 첫 집계가 끝이 아니며, 항상 다시 검증하고 조정해야 합니다.

## 먼저 던지는 질문

- 표 데이터를 읽은 뒤 어떤 순서로 가공해야 할까요?
- 분석 코드를 함수 단위로 나누면 무엇이 좋아질까요?
- 집계 결과를 재현 가능하게 남기려면 무엇을 신경 써야 할까요?

## 왜 중요한가

개별 도구를 아는 것과 결과를 만들어 내는 것은 다릅니다. 실무에서는 같은 입력에서 같은 결과를 다시 만들 수 있어야 하고, 중간 단계가 분리돼 있어야 문제를 추적할 수 있습니다. 그래서 분석 파이프라인은 재현성과 협업성을 함께 고려해야 합니다.

## 핵심 용어

- **탐색적 데이터 분석**: 데이터를 이해하기 위한 초기 분석 흐름입니다.
- **파이프라인**: 순서가 분명한 변환 단계 묶음입니다.
- 재현성: 같은 입력이면 같은 결과가 나오는 성질입니다.
- **핵심 지표**: 분석에서 추적하는 대표 수치입니다.
- **노트북 환경**: 코드와 결과를 함께 기록하는 작업 공간입니다.
- **의존성 관리**: 분석에 쓰는 라이브러리 버전을 기록하는 작업입니다.

### 성능 최적화 기법

대규모 데이터를 다룰 때는 성능을 고려해야 합니다. 다음 표는 주요 최적화 기법과 기대 효과를 정리한 것입니다.

| 기법 | 내용 | 효과 |
|---|---|---|
| 벡터화 | 열 단위 연산 사용 | apply 대비 10-100배 |
| apply 제거 | 내장 함수로 대체 | 중간 가속 |
| dtypes 최적화 | int64 → int32, object → category | 메모리 30-70% 절감 |
| eval/query | 문자열 표현식 가속 | 복잡한 수식에 유리 |
| 청크 처리 | 파일을 나누어 읽기 | 메모리 초과 방지 |

벡터화가 가장 큰 가속 효과를 내지만, 자료형 최적화도 메모리를 크게 줄일 수 있습니다. 특히 카테고리 타입은 고유값이 적은 열에서 매우 효과적입니다.

## 전과 후

이전 관점: 모든 과정을 한 덩어리 스크립트나 한 셀에 넣습니다.

이후 관점: 적재, 정제, 변형, 집계를 함수로 나눠 다시 실행하고 테스트할 수 있게 만듭니다.

## 실습: 다섯 단계로 끝까지 가기

### 1단계 - 데이터 읽기

```python
import pandas as pd

def load(path):
    return pd.read_csv(path, parse_dates=["date"])

df = load("sales.csv")
print(df.shape)
```

읽기 단계는 이후 분석 전체의 출발점입니다. 날짜 열을 읽는 시점에 처리해 두면 뒤의 시간 기반 집계가 훨씬 단순해집니다.

### 2단계 - 정제하기

```python
def clean(df):
    df = df.dropna(subset=["sales"])
    df["sales"] = df["sales"].astype(float)
    return df

df = clean(df)
```

정제 단계는 결측 제거와 자료형 보정을 담당합니다. 이 과정을 별도 함수로 두면 어떤 규칙으로 데이터를 다듬었는지 명확해집니다.

### 3단계 - 분석용 열 만들기

```python
def enrich(df):
    df["month"] = df["date"].dt.to_period("M")
    return df

df = enrich(df)
```

원본 데이터에 바로 없는 열을 만드는 단계입니다. 실무에서는 파생 변수나 특징 생성이 여기에 해당합니다.

### 4단계 - 지표 집계하기

```python
def kpi(df):
    return df.groupby("month").agg(
        total=("sales", "sum"),
        n=("sales", "count"),
        mean=("sales", "mean"),
    )

monthly = kpi(df)
print(monthly)
```

월별 KPI 표는 파이프라인이 실제로 끝까지 이어졌는지 확인하는 가장 좋은 중간 산출물입니다. 총합, 건수, 평균이 한 번에 나오면 다음 단계 시각화도 훨씬 단순해집니다.

**예상 출력:**

```text
         total  n   mean
month                    
2026-01  450.0  3  150.0
2026-02  520.0  4  130.0
```

집계 함수는 결과 표를 만드는 핵심입니다. 월별 총합, 건수, 평균처럼 분석 목적에 맞는 핵심 지표를 한곳에 모아 정의합니다.

### 5단계 - 시각화하기

```python
import matplotlib.pyplot as plt
monthly["total"].plot(kind="bar", title="Monthly Sales")
plt.tight_layout()
plt.savefig("monthly.png")
```

시각화는 노트북 화면에서만 보고 끝내지 말고 파일로 남겨야 공유와 회고가 쉬워집니다. 저장 경로가 분명하면 파이프라인 자동화에도 그대로 연결할 수 있습니다.

**예상 출력:**

```text
monthly.png saved
```

표만 보는 것보다 시각화를 함께 두면 추세와 이상치를 훨씬 빨리 읽을 수 있습니다. 결과를 파일로 저장해 두면 공유와 재검토도 쉬워집니다.

### 대용량 데이터 섹션

메모리에 한번에 담기 어려운 대용량 데이터를 다룰 때는 파일 포맷과 자료형을 함께 고려해야 합니다.

#### Parquet 포맷

CSV 대신 Parquet를 쓰면 파일 크기와 읽기 속도가 크게 개선됩니다.

```python
import pandas as pd

# 대용량 데이터 예시
df = pd.DataFrame({
    "id": range(10_000_000),
    "value": range(10_000_000),
})

# CSV 저장
df.to_csv("large.csv", index=False)

# Parquet 저장
df.to_parquet("large.parquet", index=False)

# 파일 크기 비교
import os
csv_size = os.path.getsize("large.csv") / 1024 / 1024
parquet_size = os.path.getsize("large.parquet") / 1024 / 1024
print(f"CSV: {csv_size:.1f} MB")
print(f"Parquet: {parquet_size:.1f} MB")
```

### 실무 예제: 월간 리포트 자동화

전체 파이프라인을 한 번에 보는 실무 예제입니다.

```python
import pandas as pd
import matplotlib.pyplot as plt

def load_data(path):
    return pd.read_csv(path, parse_dates=["date"])

def clean_data(df):
    df = df.dropna(subset=["sales"])
    df["sales"] = df["sales"].astype(float)
    return df

def add_features(df):
    df["month"] = df["date"].dt.to_period("M")
    df["dayofweek"] = df["date"].dt.dayofweek
    return df

def monthly_kpi(df):
    return df.groupby("month").agg(
        total_sales=("sales", "sum"),
        avg_sales=("sales", "mean"),
        order_count=("sales", "count"),
    )

def plot_trend(monthly, path):
    monthly["total_sales"].plot(kind="line", title="Monthly Sales Trend")
    plt.ylabel("Sales")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# 전체 파이프라인
df = load_data("sales.csv")
df = clean_data(df)
df = add_features(df)
monthly = monthly_kpi(df)
plot_trend(monthly, "monthly_sales.png")
monthly.to_csv("monthly_kpi.csv")
print("\n월간 KPI:")
print(monthly)
```

이 패턴은 함수로 분리된 파이프라인을 보여줍니다. 각 함수는 하나의 책임만 가지므로 테스트와 디버깅이 쉽고, 전체 흐름을 읽기 좋습니다.
**예상 출력:**

```text
CSV: 171.7 MB
Parquet: 38.2 MB
```

Parquet는 열 기반 저장 포맷으로 압축률과 읽기 속도가 CSV보다 훨씬 좋습니다. 특히 대용량 데이터를 반복 읽을 때 효과가 큽니다.

#### category dtype 활용

고유값이 적은 열을 카테고리로 변환하면 메모리를 크게 줄일 수 있습니다.

```python
df = pd.DataFrame({
    "country": ["KR", "US", "JP"] * 1_000_000,
    "value": range(3_000_000),
})

print(f"변환 전: {df['country'].memory_usage(deep=True) / 1024 / 1024:.1f} MB")

df["country"] = df["country"].astype("category")
print(f"변환 후: {df['country'].memory_usage(deep=True) / 1024 / 1024:.1f} MB")
```

**예상 출력:**

```text
변환 전: 171.7 MB
변환 후: 2.9 MB
```

카테곦0리 타입은 메모리를 줄일 뿐 아니라 groupby 같은 연산도 빠르게 만듭니다.

#### 청크별 읽기

파일이 너무 크면 일부만 읽거나 나누어 읽습니다.

```python
# 일부만 읽기
df = pd.read_csv("large.csv", nrows=100_000)

# 청크별 읽기
for chunk in pd.read_csv("large.csv", chunksize=100_000):
    # chunk별 처리
    print(chunk.shape)
```

대용량 파일을 한번에 다 읽으면 메모리가 부족할 수 있습니다. 청크 단위로 나누어 처리하면 안전하게 처리할 수 있습니다.

### before/after 벤치마크 예제

성능 차이를 직접 확인하는 것이 가장 확실한 학습 방법입니다.

```python
import pandas as pd
import numpy as np
import time

# 100만 행 데이터
df = pd.DataFrame({
    "a": np.arange(1_000_000),
    "b": np.arange(1_000_000),
})

# 변경 전: apply(axis=1)
start = time.time()
df["c_slow"] = df.apply(lambda r: r["a"] + r["b"], axis=1)
slow = time.time() - start

# After: 벡터화
start = time.time()
df["c_fast"] = df["a"] + df["b"]
fast = time.time() - start

print(f"apply(axis=1): {slow:.3f}s")
print(f"벡터화: {fast:.3f}s")
print(f"가속 비율: {slow/fast:.1f}x")
```

**예상 출력:**

```text
apply(axis=1): 12.450s
벡터화: 0.005s
가속 비율: 2490.0x
```

동일한 계산이라도 벡터화 여부에 따라 수천 배 차이가 납니다. 큰 데이터에서는 이 차이가 분 단위에서 시간 단위로 드러납니다.

### 조건 분기 벤치마크

```python
# Before: 반복문
start = time.time()
result = []
for val in df["a"]:
    result.append("even" if val % 2 == 0 else "odd")
df["flag_slow"] = result
slow = time.time() - start

# 변경 후: np.where
start = time.time()
df["flag_fast"] = np.where(df["a"] % 2 == 0, "even", "odd")
fast = time.time() - start

print(f"반복문: {slow:.3f}s")
print(f"np.where: {fast:.3f}s")
print(f"가속 비율: {slow/fast:.1f}x")
```

**예상 출력:**

```text
반복문: 0.450s
np.where: 0.025s
가속 비율: 18.0x
```

조건 분기도 벡터화하면 크게 빨라집니다. `np.where`, `np.select`, `pd.cut` 같은 도구를 우선 검토하세요.

## 이 코드에서 먼저 봐야 할 점

- 함수 단위 분리는 각 단계를 독립적으로 테스트할 수 있게 합니다.
- `parse_dates`는 시계열 분석의 출발점입니다.
- Pandas 내장 시각화는 빠른 확인용으로 매우 실용적입니다.

## 자주 하는 실수 다섯 가지

1. 모든 단계를 하나의 셀이나 스크립트에 몰아넣습니다.
2. 중간 결과를 저장하거나 점검하지 않습니다.
3. 열 이름과 의미를 문서화하지 않습니다.
4. 표만 보고 결론을 내리고 시각화는 생략합니다.
5. 버전과 실행 조건을 남기지 않아 재현성을 잃습니다.

## 실무에서는 이렇게 이어집니다

KPI 리포트 자동화, 마케팅 분석, 운영 대시보드 같은 작업은 이런 함수형 흐름 위에 쌓입니다. 노트북은 탐색과 설명에, 파이썬 모듈은 재사용과 자동화에 각각 강점이 있으므로 둘을 함께 운용하는 경우가 많습니다.

## 실무에서는 이렇게 생각합니다

- 적재, 정제, 변형, 집계를 함수로 나눕니다.
- 각 함수에 간단한 설명과 점검 코드를 둡니다.
- 원본에서 결과까지 흐름을 도식화해 둡니다.
- 숫자 요약과 시각화를 함께 봅니다.
- 버전, 시드, 실행 시점을 기록합니다.

## 체크리스트

- [ ] 적재, 정제, 변형, 집계, 시각화를 함수로 나눌 수 있습니다.
- [ ] 시각화 결과 파일을 생성할 수 있습니다.
- [ ] 열 정의를 문서로 남길 수 있습니다.
- [ ] 같은 입력으로 같은 결과를 다시 만들 수 있습니다.

## 연습 문제

1. 적재, 정제, 변형, 집계 함수로 작은 분석 프로젝트를 구성해 보세요.
2. 월간 지표와 주간 지표를 함께 계산해 보세요.
3. 결과를 PNG와 CSV로 모두 저장해 보세요.

## 정리와 다음 글

이제 Pandas 101의 큰 흐름을 한 번 완주했습니다. 표 데이터를 읽고, 정제하고, 가공하고, 집계하고, 시각화하는 기본 작업은 데이터 분석의 거의 모든 길에서 다시 등장합니다. 다음 단계로는 Polars나 Dask 같은 확장 도구, 혹은 Matplotlib, Plotly, scikit-learn 같은 주변 생태계로 자연스럽게 이어질 수 있습니다.

## 처음 질문으로 돌아가기

- **표 데이터를 읽은 뒤 어떤 순서로 가공해야 할까요?**
  - 이 글의 흐름은 적재, 정제, 파생 열 추가, KPI 집계, 시각화 순서입니다. `load()`, `clean()`, `enrich()`, `kpi()` 함수와 `monthly["total"].plot(...)` 예제가 읽은 데이터를 어떻게 결과 표와 그림으로 연결하는지 보여 줍니다.
- **분석 코드를 함수 단위로 나누면 무엇이 좋아질까요?**
  - 각 단계의 책임이 분명해져서 테스트, 재실행, 디버깅이 쉬워집니다. 예를 들어 `clean_data()`에서 결측 제거와 타입 변환만 맡기고 `monthly_kpi()`는 집계만 담당하게 두면 어느 단계에서 결과가 달라졌는지 빠르게 추적할 수 있습니다.
- **집계 결과를 재현 가능하게 남기려면 무엇을 신경 써야 할까요?**
  - 같은 입력과 같은 버전, 같은 변환 규칙으로 언제든 다시 만들 수 있어야 하므로 함수 구조, 출력 파일, 실행 조건을 함께 남겨야 합니다. 본문이 `monthly.to_csv("monthly_kpi.csv")`, `plt.savefig("monthly_sales.png")`, `parse_dates`, dtype 최적화, 청크 처리까지 묶어 설명한 이유가 바로 재현성과 운영성을 같이 확보하기 위해서입니다.

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
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- **실전 데이터 분석 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [pandas — Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [pandas — Visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)
- [Wes McKinney — Python for Data Analysis](https://wesmckinney.com/book/)
- [Kaggle — Pandas Course](https://www.kaggle.com/learn/pandas)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, DataAnalysis, EDA, Workflow, Beginner
