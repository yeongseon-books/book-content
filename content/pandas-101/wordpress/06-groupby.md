---
series: pandas-101
episode: 6
title: "바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - groupby
  - 집계
  - 데이터분석
seo_description: AI가 생성한 pandas groupby 코드를 이해하고 수정하는 방법. agg, transform, filter의 차이와 named aggregation 패턴을 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 여섯 번째 글입니다.

---

AI에게 "카테고리별 매출 합계를 구해줘"라고 하면 `df.groupby('category')['sales'].sum()` 코드가 나옵니다. 이 한 줄이 반복문 수십 줄을 대체합니다. 그런데 "평균과 합계를 동시에 구해줘"나 "그룹별 비율을 원본에 붙여줘"같은 요청을 하면 AI가 `agg`, `transform`, `apply` 중 하나를 선택합니다. 이 세 가지가 어떻게 다른지 모르면 AI가 맞는 코드를 생성했는지 알 수 없습니다.

바이브코딩에서 `groupby`는 분석 요청의 핵심입니다. "부서별 평균 급여", "상품별 판매 추이", "사용자별 활동 요약"처럼 분석 요청의 대부분이 그룹화와 집계입니다. AI가 생성한 `groupby` 코드를 수정하거나 확장할 수 있으면 분석 작업의 상당 부분을 소화할 수 있습니다.

이번 글에서는 `groupby`의 세 가지 연산(집계, 변환, 필터)을 바이브코딩 관점에서 정리합니다. AI 코드에서 `agg`와 `transform`을 언제 바꿔야 하는지가 핵심입니다.

> **바이브코딩 관점:** AI가 `groupby().mean()`을 생성했는데 "그룹 평균을 원본 데이터프레임에 열로 추가"하고 싶다면 `transform`으로 바꿔야 합니다. `agg`는 그룹당 하나의 행, `transform`은 원본 행 수를 유지합니다.

## 이 글에서 다룰 질문

- `agg`와 `transform`은 결과 형태가 어떻게 다를까요?
- AI가 생성한 집계 코드에서 열 이름을 어떻게 지정할까요?
- 그룹별 비율이나 평균 대비 편차는 어떻게 계산할까요?
- `groupby` 결과를 원본 DataFrame과 합치려면 어떻게 할까요?
- `apply`와 `agg` 중 어느 것이 더 나은 선택일까요?

---

## 분할-적용-결합 모델

`groupby`의 동작 원리: **데이터를 기준별로 나누고(Split), 각 그룹에 계산을 적용하고(Apply), 결과를 하나로 합친다(Combine).**

### 핵심 개념 용어

| 개념 | 설명 |
|---|---|
| **agg** | 그룹당 하나의 값을 계산. 결과가 그룹 수만큼의 행 |
| **transform** | 원본 행 수를 유지하면서 그룹 통계 반환 |
| **filter** | 그룹 단위 조건으로 행을 남기거나 제거 |
| **named aggregation** | `agg(열이름=(원본열, 함수))` 형태로 출력 열 이름을 지정 |

---

## Before / After: agg vs transform

**Before (AI 코드: 그룹 평균을 구했는데 원본에 붙이려고 merge 사용):**
```python
# 불필요하게 복잡한 방식
group_mean = df.groupby("city")["sales"].mean().reset_index()
group_mean.columns = ["city", "city_mean"]
df = df.merge(group_mean, on="city")
```

**After (transform을 사용한 간결한 방식):**
```python
# transform: 원본 행 수 유지, merge 불필요
df["city_mean"] = df.groupby("city")["sales"].transform("mean")
```

---

## AI가 자주 생성하는 groupby 패턴

### 기본 집계

```python
import pandas as pd

df = pd.DataFrame({
    "city": ["Seoul", "Seoul", "Busan", "Busan"],
    "month": ["Jan", "Feb", "Jan", "Feb"],
    "sales": [100, 120, 80, 95],
})

# 단순 합계
print(df.groupby("city")["sales"].sum())
```

**출력:**
```
city
Busan    175
Seoul    220
Name: sales, dtype: int64
```

### 이름 있는 집계 (named aggregation)

AI가 `agg`를 생성할 때 열 이름을 지정하지 않으면 읽기 어려운 결과가 나옵니다. 이름 있는 집계를 요청하세요:

```python
print(df.groupby("city").agg(
    total=("sales", "sum"),
    mean=("sales", "mean"),
    n=("sales", "count"),
))
```

**출력:**
```
       total   mean  n
city
Busan    175   87.5  2
Seoul    220  110.0  2
```

### transform: 그룹 통계를 원본에 붙이기

```python
# 그룹 합계 대비 비율 계산
df["share"] = df["sales"] / df.groupby("city")["sales"].transform("sum")
print(df)
```

**출력:**
```
    city month  sales     share
0  Seoul   Jan    100  0.454545
1  Seoul   Feb    120  0.545455
2  Busan   Jan     80  0.457143
3  Busan   Feb     95  0.542857
```

### 여러 키로 그룹화

```python
result = df.groupby(["city", "month"]).agg(
    total_sales=("sales", "sum"),
)
print(result)
print(result.reset_index())  # 인덱스를 열로 변환
```

### filter: 그룹 단위 조건

```python
# 합계가 200 이상인 그룹의 행만 남김
big = df.groupby("city").filter(lambda g: g["sales"].sum() > 200)
print(big)
```

---

## groupby 함수 비교

| 함수 | 결과 행 수 | 주요 용도 | AI 코드 예시 |
|---|---|---|---|
| `sum()`, `mean()` 등 | 그룹 수 | 단순 집계 | `df.groupby('city')['sales'].mean()` |
| `agg()` | 그룹 수 | 여러 통계 동시 계산 | `df.groupby('city').agg(total=('sales','sum'))` |
| `transform()` | 원본과 동일 | 그룹 통계를 원본에 붙이기 | `df.groupby('city')['sales'].transform('mean')` |
| `apply()` | 가변 | 임의 함수 적용 | 가능하면 `agg`로 대체 |
| `filter()` | 조건 충족 그룹의 행 | 그룹 단위 필터링 | `df.groupby('city').filter(lambda g: ...)` |

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | 문제 | 해결 방법 |
|---|---|---|
| agg와 transform 혼동 | 원본에 붙이려는데 행 수가 달라짐 | 원본 행 유지 목적이면 `transform` |
| 열 이름 없는 agg | 결과 열 이름이 불명확함 | named aggregation `agg(name=(col, func))` |
| `reset_index()` 누락 | 다음 조인에서 인덱스 충돌 | 결과를 열로 쓰려면 `reset_index()` 추가 |
| `apply` 남용 | 느리고 읽기 어려움 | 내장 함수나 `agg`로 대체 |
| 그룹 키가 인덱스 | `as_index=False` 없어 불편 | `groupby(..., as_index=False)` 또는 `reset_index()` |

---

## AI 팁: 이런 프롬프트를 써보세요

**이름 있는 집계 요청:**
> "city 컬럼으로 그룹화해서 sales의 합계, 평균, 개수를 각각 total, mean, count라는 이름의 열로 계산해줘."

**transform 요청:**
> "각 도시별 매출 합계 대비 개별 행의 비율을 'share'라는 새 열로 원본 DataFrame에 추가해줘. transform을 사용해줘."

**성능 개선 요청:**
> "이 groupby apply 코드를 더 빠른 agg나 내장 함수로 바꿔줘."

---

## 체크리스트

- [ ] `groupby().agg()`로 여러 통계를 동시에 계산할 수 있다
- [ ] `agg`와 `transform`의 결과 행 수 차이를 설명할 수 있다
- [ ] named aggregation `agg(name=(col, func))`을 쓸 수 있다
- [ ] 그룹 통계를 원본에 붙일 때 `transform`을 선택할 수 있다
- [ ] `reset_index()`가 필요한 시점을 안다

---

## 처음 질문으로 돌아가기

- **`agg`와 `transform`은 결과 형태가 어떻게 다를까요?**
  - `agg`는 그룹당 하나의 행을 반환합니다. `transform`은 원본과 같은 행 수를 유지하며 각 행에 그룹 통계값을 붙입니다.
- **AI가 생성한 집계 코드에서 열 이름을 어떻게 지정할까요?**
  - `agg(total=('sales', 'sum'), mean=('sales', 'mean'))` 형태의 named aggregation을 사용합니다.
- **`apply`와 `agg` 중 어느 것이 더 나은 선택일까요?**
  - 내장 함수로 표현 가능하면 `agg`가 훨씬 빠릅니다. `apply`는 내장 함수로 표현하기 어려운 복잡한 계산에만 씁니다.

---

## 정리

`groupby`는 분석 요청의 핵심 도구입니다. AI가 생성하는 집계 코드를 읽고 수정하려면 `agg`(그룹 요약)와 `transform`(원본 유지)의 차이를 이해하는 것이 가장 중요합니다. 다음 글에서는 여러 표를 하나로 합치는 병합과 조인을 다룹니다.

---

## 참고 자료

- [pandas Group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas agg 문서](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.agg.html)
- [pandas transform 문서](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.transform.html)
- [예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pandas 기초 (1/10): Pandas란 무엇인가?
- 바이브코딩을 위한 Pandas 기초 (2/10): 시리즈와 데이터프레임
- 바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기
- 바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택
- 바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리
- **바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계 (현재 글)**
- 바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인
- 바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기
- 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화
- 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석
<!-- toc:end -->

Tags: 바이브코딩, Pandas, groupby, 집계, 데이터분석
