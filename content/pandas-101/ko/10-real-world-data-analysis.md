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

이 글은 Pandas 101 시리즈의 10번째 글입니다.

이번 글에서는 지금까지의 도구들을 하나의 실전 흐름, 즉 적재에서 정제, 변형, 집계, 시각화로 이어지는 표준 분석 파이프라인으로 정리하겠습니다.

## 먼저 던지는 질문

- 표 데이터를 읽은 뒤 어떤 순서로 가공해야 할까요?
- 분석 코드를 함수 단위로 나누면 무엇이 좋아질까요?
- 집계 결과를 재현 가능하게 남기려면 무엇을 신경 써야 할까요?

## 큰 그림

![Pandas 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/10/10-01-concept-at-a-glance.ko.png)

*Pandas 101 10장 흐름 개요*

이 그림은 읽기부터 요약까지의 전체 흐름을 보여줍니다. Pandas의 모든 기능은 이 흐름 속에서 특정 단계의 일부일 뿐, 단독으로 의미를 갖지 않습니다.

> **분석은 반복**입니다. 첫 읽기가 완벽할 수 없고, 첫 집계가 끝이 아니며, 항상 다시 검증하고 조정해야 합니다.

## 왜 중요한가

개별 도구를 아는 것과 결과를 만들어 내는 것은 다릅니다. 실무에서는 같은 입력에서 같은 결과를 다시 만들 수 있어야 하고, 중간 단계가 분리돼 있어야 문제를 추적할 수 있습니다. 그래서 분석 파이프라인은 재현성과 협업성을 함께 고려해야 합니다.

## 한눈에 보는 개념

## 핵심 용어

- **탐색적 데이터 분석**: 데이터를 이해하기 위한 초기 분석 흐름입니다.
- **파이프라인**: 순서가 분명한 변환 단계 묶음입니다.
- 재현성: 같은 입력이면 같은 결과가 나오는 성질입니다.
- **핵심 지표**: 분석에서 추적하는 대표 수치입니다.
- **노트북 환경**: 코드와 결과를 함께 기록하는 작업 공간입니다.

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
  - 본문의 기준은 실전 데이터 분석를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **분석 코드를 함수 단위로 나누면 무엇이 좋아질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **집계 결과를 재현 가능하게 남기려면 무엇을 신경 써야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Pandas, DataAnalysis, EDA, Workflow, Beginner
