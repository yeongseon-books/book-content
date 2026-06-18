---
series: pandas-101
episode: 5
title: "바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - 결측치
  - NaN
  - 데이터정제
seo_description: AI가 생성한 pandas 결측치 처리 코드를 이해하고 수정하는 방법. dropna, fillna, interpolate의 차이와 상황에 맞는 선택 기준을 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 다섯 번째 글입니다.

---

AI에게 "데이터를 정제해줘"라고 하면 `df.dropna()`가 코드에 들어옵니다. 빠르고 간단합니다. 그런데 실행하고 나면 데이터가 절반 이하로 줄어버리는 경우가 있습니다. 반대로 `df.fillna(0)`을 쓰면 숫자가 없어야 할 곳에 0이 들어가 분석이 왜곡됩니다.

바이브코딩에서 결측치 처리는 AI가 자주 틀리는 영역입니다. AI는 코드를 실행 가능하게 만드는 데는 능숙하지만, 어떤 처리 방식이 데이터의 의미를 보존하는지는 판단하기 어렵습니다. 이 판단은 사람이 해야 합니다.

이번 글에서는 NaN이 무엇인지, 어떻게 진단하는지, 상황에 맞는 처리 방식을 어떻게 선택하는지를 정리합니다. AI 코드에서 `dropna`와 `fillna`를 언제 어떻게 바꿔야 하는지가 핵심입니다.

> **바이브코딩 관점:** AI가 `dropna()`를 생성했을 때 "얼마나 많은 행이 사라지는지" 먼저 확인해야 합니다. AI는 코드를 실행 가능하게 만들지만, 데이터 손실 비용은 사람이 판단해야 합니다.

## 이 글에서 다룰 질문

- AI가 생성한 `dropna()`는 어떤 상황에서 문제가 될까요?
- `fillna(0)`이 분석을 왜곡하는 이유는 무엇일까요?
- 결측치를 처리하기 전에 반드시 해야 할 진단은 무엇일까요?
- 시계열 데이터의 결측치에 적합한 처리 방법은 무엇일까요?
- AI 코드에서 결측치 처리 방식을 바꿔야 할 때 어떻게 판단할까요?

---

## 결측치의 종류와 진단

NaN, None, `pd.NA` 모두 pandas에서 결측을 나타내지만 자료형에 따라 구분됩니다. 실무에서는 대부분 NaN을 만납니다.

### 핵심 개념 용어

| 개념 | 설명 |
|---|---|
| **NaN** | 숫자형 결측. `float('nan')`과 같음 |
| **dropna()** | 결측이 있는 행 또는 열을 제거 |
| **fillna()** | 결측을 특정 값으로 채움 |
| **ffill / bfill** | 앞/뒤 값으로 채우기. 시계열에 자주 사용 |
| **interpolate()** | 주변 값으로 추정해서 채우기 |

---

## Before / After: 결측치 처리의 함정

**Before (AI가 자주 생성하는 코드):**
```python
# 간단하지만 데이터를 많이 잃을 수 있음
df = df.dropna()
print(df.shape)  # 행이 얼마나 줄었는지 모름
```

**After (진단 후 선택적 처리):**
```python
# 먼저 진단
print(df.isna().sum())          # 열별 결측 개수
missing_ratio = df.isna().sum() / len(df) * 100
print(missing_ratio)            # 열별 결측 비율

# 특정 열에만 dropna 적용
df = df.dropna(subset=["price", "quantity"])
print(f"처리 후 행 수: {len(df)}")
```

---

## AI가 자주 생성하는 결측치 패턴

### 결측치 진단 (가장 먼저)

```python
import numpy as np, pandas as pd

df = pd.DataFrame({"x": [1, np.nan, 3], "y": [np.nan, 2, 3]})

# 기본 진단
print(df.isna())          # 각 위치의 결측 여부
print(df.isna().sum())    # 열별 결측 개수

# 결측 비율
missing_ratio = df.isna().sum() / len(df) * 100
print(missing_ratio)
```

**출력:**
```
x    1
y    1
dtype: int64
```

### 행 또는 열 제거

```python
# 결측이 있는 행 제거
print(df.dropna())

# 특정 열에만 결측이 있는 행 제거
print(df.dropna(subset=["x"]))

# 결측이 있는 열 제거
print(df.dropna(axis=1))
```

### 값 채우기

```python
# 상수로 채우기
print(df.fillna(0))

# 열별 평균으로 채우기
print(df.fillna(df.mean(numeric_only=True)))

# 각 열에 다른 값으로
print(df.fillna({"x": 0, "y": df["y"].median()}))
```

### 앞/뒤 값으로 채우기 (시계열 친화)

```python
# 앞 값으로 채우기 (ffill)
print(df.ffill())

# 뒤 값으로 채우기 (bfill)
print(df.bfill())
```

### 선형 보간

```python
ts = pd.Series([1.0, np.nan, np.nan, 4.0])
print(ts.interpolate())
```

**출력:**
```
0    1.0
1    2.0
2    3.0
3    4.0
dtype: float64
```

보간은 앞뒤 값을 이어 빈 구간을 메웁니다. 시계열 데이터에서 자연스럽고, 단순 상수 대체보다 데이터 흐름을 더 잘 보존합니다.

---

## 결측치 처리 방법 비교

| 방법 | 함수 | 언제 쓸까 | 주의사항 |
|---|---|---|---|
| 제거 | `dropna()` | 결측 비율이 낮을 때 | 표본 크기 감소 |
| 상수 대체 | `fillna(0)` | 0이 의미 있을 때 | 분포 왜곡 가능 |
| 평균 대체 | `fillna(mean)` | 연속값의 임시 처리 | 분산 감소 |
| 앞/뒤 값 | `ffill()/bfill()` | 순서 있는 데이터 | 끝단 결측 남을 수 있음 |
| 보간 | `interpolate()` | 시계열, 연속적 흐름 | 추가 가정 필요 |

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | 문제 | 해결 방법 |
|---|---|---|
| `dropna()` 남용 | 행 대부분 사라짐 | 진단 후 `subset` 지정 |
| `fillna(0)` 무조건 적용 | 결측이 0을 의미하지 않을 때 분포 왜곡 | 데이터 맥락 확인 후 결정 |
| `ffill`만 사용 | 첫 행이 결측이면 NaN 남음 | `bfill`과 조합 또는 선두 처리 따로 |
| 범주형 열에 평균 | `object` 열에 평균을 채울 수 없음 | 최빈값이나 특정 문자열 사용 |
| 처리 기준 미기록 | 나중에 왜 이렇게 처리했는지 알 수 없음 | 코드 주석이나 문서로 기록 |

---

## AI 팁: 이런 프롬프트를 써보세요

**결측 진단 요청:**
> "이 DataFrame에서 각 열의 결측 개수와 비율을 한눈에 볼 수 있는 코드를 작성해줘."

**처리 방식 선택 요청:**
> "이 DataFrame에서 'price' 열의 결측을 처리하는데, 0으로 채우는 것과 중앙값으로 채우는 것 중 어느 것이 더 적절한지 설명하고 코드를 작성해줘."

**시계열 결측 처리 요청:**
> "날짜 인덱스를 가진 이 시계열 데이터에서 결측치를 선형 보간으로 채우는 코드를 작성해줘."

---

## 체크리스트

- [ ] `isna().sum()`으로 결측 현황을 진단할 수 있다
- [ ] `dropna(subset=[...])`으로 특정 열 기준으로 제거할 수 있다
- [ ] `fillna()`에 상수, 평균, 딕셔너리를 사용할 수 있다
- [ ] `ffill()`과 `bfill()`의 차이와 적합한 상황을 안다
- [ ] 결측 비율이 높을 때 `dropna`의 위험성을 이해한다

---

## 처음 질문으로 돌아가기

- **AI가 생성한 `dropna()`는 어떤 상황에서 문제가 될까요?**
  - 결측 비율이 높을 때 대부분의 행이 사라집니다. 처리 전 `isna().sum() / len(df)`로 비율을 먼저 확인해야 합니다.
- **`fillna(0)`이 분석을 왜곡하는 이유는?**
  - 결측이 "측정값이 없음"을 의미하는데 0으로 채우면 "값이 0"처럼 계산됩니다. 평균, 합계, 분포가 모두 달라집니다.
- **시계열 데이터의 결측치에 적합한 처리 방법은?**
  - `ffill()`(앞 값으로 채우기)이나 `interpolate()`(선형 보간)이 흐름을 보존하면서 채우는 자연스러운 방법입니다.

---

## 정리

결측치 처리는 데이터를 깨끗하게 만드는 것이 아니라 데이터의 의미를 보존하는 작업입니다. AI가 생성한 `dropna()`나 `fillna(0)` 코드는 실행은 되지만 항상 올바른 처리는 아닙니다. 진단을 먼저 하고, 데이터의 맥락에 맞는 방식을 선택하는 것이 중요합니다. 다음 글에서는 데이터를 그룹별로 집계하는 `groupby`를 다룹니다.

---

## 참고 자료

- [pandas Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [pandas fillna 문서](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)
- [pandas interpolate 문서](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html)
- [예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pandas 기초 (1/10): Pandas란 무엇인가?
- 바이브코딩을 위한 Pandas 기초 (2/10): 시리즈와 데이터프레임
- 바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기
- 바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택
- **바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리 (현재 글)**
- 바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계
- 바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인
- 바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기
- 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화
- 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석
<!-- toc:end -->

Tags: 바이브코딩, Pandas, 결측치, NaN, 데이터정제
