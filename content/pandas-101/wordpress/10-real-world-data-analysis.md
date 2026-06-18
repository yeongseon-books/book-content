---
series: pandas-101
episode: 10
title: "바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - 실전분석
  - 데이터파이프라인
  - EDA
seo_description: AI와 함께하는 pandas 실전 분석 흐름. 데이터 적재부터 정제, 집계, 시각화까지 바이브코딩으로 분석 파이프라인을 구성하는 방법을 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 마지막 글입니다.

---

이 시리즈에서 배운 읽기, 정제, 선택, 집계, 시계열, 벡터화는 각각 따로 보면 익숙합니다. 하지만 실제 분석에서는 이것들이 하나의 흐름으로 이어져야 결과가 나옵니다. AI에게 분석을 요청할 때 "CSV를 읽어서 월별 매출을 분석해줘"라고 하면 긴 코드가 나옵니다. 이 코드를 수정하고 검증하고 확장하려면 전체 흐름을 읽을 수 있어야 합니다.

바이브코딩의 목표는 AI가 생성한 코드를 실행하는 것이 아니라, 이해하고 수정하고 더 나은 결과를 만드는 것입니다. 이 마지막 글은 지금까지 배운 모든 개념이 하나의 분석 흐름 안에서 어떻게 연결되는지를 보여줍니다.

데이터를 받았을 때 어디서 시작해서 어디서 끝내야 하는지, AI에게 무엇을 요청해야 하는지, 결과를 어떻게 검증해야 하는지를 실전 예제로 정리합니다.

> **바이브코딩 관점:** AI에게 분석을 맡길 때 "적재 → 정제 → 변형 → 집계 → 시각화"의 각 단계를 함수로 나눠서 작성해달라고 요청하면, 나중에 수정하거나 재사용하기 훨씬 쉽습니다.

## 이 글에서 다룰 질문

- AI가 생성한 긴 분석 코드를 어떻게 단계별로 읽을까요?
- 분석 파이프라인을 함수로 나누면 무엇이 좋아질까요?
- 각 단계에서 결과를 어떻게 검증해야 할까요?
- AI와 함께 분석할 때 좋은 프롬프트 패턴은 무엇일까요?
- 분석 결과를 재현 가능하게 만들려면 무엇을 기록해야 할까요?

---

## 실전 분석의 다섯 단계

AI에게 분석을 요청할 때 이 다섯 단계로 나눠서 요청하면 코드가 훨씬 관리하기 쉽습니다.

| 단계 | 역할 | 핵심 함수 |
|---|---|---|
| **적재 (Load)** | 파일 읽기, 자료형 설정 | `read_csv`, `read_excel` |
| **정제 (Clean)** | 결측치 처리, 자료형 변환 | `dropna`, `fillna`, `astype` |
| **변형 (Transform)** | 파생 열 추가, 날짜 처리 | `assign`, `dt.to_period` |
| **집계 (Aggregate)** | 그룹화, 지표 계산 | `groupby`, `agg` |
| **시각화 (Visualize)** | 결과 확인, 출력 | `plot`, `to_csv` |

---

## Before / After: 분석 코드 구조화

**Before (AI가 자주 생성하는 단일 블록 코드):**
```python
import pandas as pd
df = pd.read_csv("sales.csv")
df = df.dropna()
df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
result = df.groupby("month")["sales"].sum()
result.plot()
```

**After (단계별 함수로 분리):**
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
    return df

def compute_kpi(df):
    return df.groupby("month").agg(
        total=("sales", "sum"),
        n=("sales", "count"),
        mean=("sales", "mean"),
    )

def save_chart(monthly, path):
    monthly["total"].plot(kind="bar", title="Monthly Sales")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# 전체 파이프라인
df = load_data("sales.csv")
df = clean_data(df)
df = add_features(df)
monthly = compute_kpi(df)
save_chart(monthly, "monthly_sales.png")
monthly.to_csv("monthly_kpi.csv")
print(monthly)
```

---

## 단계별 검증 패턴

### 1단계: 적재 후 점검

```python
df = pd.read_csv("sales.csv", parse_dates=["date"])

# 반드시 확인
print(f"행 수: {len(df)}")
print(f"열 수: {len(df.columns)}")
print(df.dtypes)
print(df.head())
```

### 2단계: 정제 후 점검

```python
df_clean = clean_data(df)

# 정제 전후 비교
print(f"정제 전: {len(df)}행")
print(f"정제 후: {len(df_clean)}행")
print(f"제거된 행: {len(df) - len(df_clean)}행")
print(df_clean.isna().sum())
```

### 3단계: 집계 결과 검증

```python
monthly = compute_kpi(df_clean)

# 결과 검증
print(monthly)
print(f"총 매출: {monthly['total'].sum():,.0f}")
print(f"기간: {monthly.index[0]} ~ {monthly.index[-1]}")
```

---

## AI와 함께하는 실전 분석 워크플로우

### 1. 탐색 단계: 데이터 이해

```python
# AI에게 요청: "이 DataFrame의 기본 정보를 요약해줘"
def explore(df):
    print("=== 기본 정보 ===")
    print(f"Shape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\n결측치:\n{df.isna().sum()}")
    print(f"\n수치형 요약:\n{df.describe()}")

explore(df)
```

### 2. 분석 단계: 핵심 질문에 답하기

실전 분석은 항상 "무엇을 알고 싶은가"에서 시작합니다. AI에게 질문을 구체적으로 전달하세요:

```python
# 예: "상품별 월별 매출 추이를 분석해줘"
product_monthly = df.groupby(["product", "month"]).agg(
    total=("sales", "sum"),
    orders=("sales", "count"),
)
print(product_monthly)
```

### 3. 시각화 단계: 결과 확인

```python
import matplotlib.pyplot as plt

monthly["total"].plot(
    kind="line",
    title="월별 매출 추이",
    xlabel="월",
    ylabel="매출",
    figsize=(10, 4),
)
plt.tight_layout()
plt.savefig("monthly_trend.png", dpi=150)
plt.show()
```

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | 문제 | 해결 방법 |
|---|---|---|
| 단일 블록 코드 | 수정하거나 재실행하기 어려움 | 단계별 함수로 분리 |
| 중간 결과 미확인 | 어느 단계에서 오류가 났는지 모름 | 각 단계 후 `shape`, `head()` 확인 |
| 열 정의 미문서화 | 나중에 열 의미를 알 수 없음 | 주석이나 별도 딕셔너리로 기록 |
| 하드코딩된 경로 | 환경이 바뀌면 오류 | 상수나 파라미터로 분리 |
| 재현성 없음 | 버전, 실행 시점 미기록 | `pd.__version__`, 실행 날짜 기록 |

---

## 완성된 분석 파이프라인 예시

```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 설정
DATA_PATH = "sales.csv"
OUTPUT_DIR = "output/"

def load_data(path):
    """CSV 파일을 읽고 기본 자료형을 설정합니다."""
    df = pd.read_csv(
        path,
        parse_dates=["date"],
        dtype={"product_id": "string"},
    )
    return df

def clean_data(df):
    """결측치를 처리하고 자료형을 정리합니다."""
    before = len(df)
    df = df.dropna(subset=["sales", "product_id"])
    df["sales"] = df["sales"].astype(float)
    print(f"정제: {before}행 → {len(df)}행")
    return df

def add_features(df):
    """분석에 필요한 파생 열을 추가합니다."""
    df["month"] = df["date"].dt.to_period("M")
    df["year"] = df["date"].dt.year
    return df

def compute_kpi(df):
    """월별 핵심 지표를 계산합니다."""
    return df.groupby("month").agg(
        total_sales=("sales", "sum"),
        order_count=("sales", "count"),
        avg_sales=("sales", "mean"),
    ).reset_index()

def save_results(monthly, output_dir):
    """결과를 파일로 저장합니다."""
    monthly.to_csv(f"{output_dir}monthly_kpi.csv", index=False)

    monthly.set_index("month")["total_sales"].plot(
        kind="bar",
        title=f"월별 매출 ({datetime.now().strftime('%Y-%m-%d')})",
    )
    plt.tight_layout()
    plt.savefig(f"{output_dir}monthly_sales.png")
    plt.close()

# 실행
df = load_data(DATA_PATH)
df = clean_data(df)
df = add_features(df)
monthly = compute_kpi(df)
save_results(monthly, OUTPUT_DIR)
print(monthly)
```

---

## AI 팁: 이런 프롬프트를 써보세요

**파이프라인 요청:**
> "sales.csv를 분석하는 코드를 load_data, clean_data, compute_kpi, save_results 함수로 나눠서 작성해줘. 각 함수 사이에 결과를 검증하는 출력도 포함해줘."

**검증 코드 요청:**
> "이 분석 파이프라인의 각 단계에서 데이터 품질을 검증하는 assertion 코드를 추가해줘."

**재현성 확보 요청:**
> "이 분석 코드에 실행 날짜, pandas 버전, 입력 파일 경로를 기록하는 헤더를 추가해줘."

---

## 체크리스트

- [ ] 분석 코드를 적재/정제/변형/집계/시각화 단계로 나눌 수 있다
- [ ] 각 단계 후 `shape`, `dtypes`, `head()`로 검증할 수 있다
- [ ] 함수로 분리된 파이프라인을 작성하거나 AI에게 요청할 수 있다
- [ ] 결과를 CSV와 이미지 파일로 저장할 수 있다
- [ ] 분석 코드의 재현성을 위해 무엇을 기록해야 하는지 안다

---

## 처음 질문으로 돌아가기

- **AI가 생성한 긴 분석 코드를 어떻게 단계별로 읽을까요?**
  - 적재(read), 정제(dropna/fillna), 변형(assign/dt), 집계(groupby/agg), 시각화(plot) 순서로 단계를 나눠서 읽습니다.
- **분석 파이프라인을 함수로 나누면 무엇이 좋아질까요?**
  - 각 단계를 독립적으로 테스트하고 수정할 수 있습니다. 코드 재사용과 디버깅이 쉬워집니다.
- **분석 결과를 재현 가능하게 만들려면 무엇을 기록해야 할까요?**
  - 입력 파일 경로, pandas 버전, 실행 날짜, 처리 기준(예: 어떤 결측치를 어떻게 처리했는지)을 기록합니다.

---

## 정리: 시리즈를 마치며

이 시리즈를 통해 AI가 생성하는 pandas 코드를 읽고, 이해하고, 수정하는 기초를 쌓았습니다.

- **1장**: pandas가 무엇을 하는 도구인지, DataFrame의 기본 구조
- **2장**: Series와 DataFrame의 관계, 인덱스 정렬 원리
- **3장**: CSV와 Excel을 안전하게 읽는 핵심 옵션
- **4장**: loc/iloc/조건 필터링, SettingWithCopyWarning 해결
- **5장**: 결측치 진단과 상황에 맞는 처리 방식
- **6장**: groupby의 agg/transform/filter 차이
- **7장**: merge의 조인 방식과 행 수 폭증 방지
- **8장**: 시계열 준비(날짜 인덱스)와 resample/rolling
- **9장**: apply를 벡터화로 바꾸는 방법
- **10장**: 전체 흐름을 함수형 파이프라인으로 구성

다음 단계로는 Plotly/Matplotlib으로 시각화를 확장하거나, scikit-learn으로 머신러닝 전처리로 이어갈 수 있습니다.

---

## 참고 자료

- [pandas Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [pandas Visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)
- [Wes McKinney - Python for Data Analysis](https://wesmckinney.com/book/)
- [Kaggle Pandas Course](https://www.kaggle.com/learn/pandas)
- [예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pandas 기초 (1/10): Pandas란 무엇인가?
- 바이브코딩을 위한 Pandas 기초 (2/10): 시리즈와 데이터프레임
- 바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기
- 바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택
- 바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리
- 바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계
- 바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인
- 바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기
- 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화
- **바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Pandas, 실전분석, 데이터파이프라인, EDA
