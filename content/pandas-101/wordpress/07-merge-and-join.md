---
series: pandas-101
episode: 7
title: "바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - merge
  - join
  - 데이터분석
seo_description: AI가 생성한 pandas merge 코드를 이해하고 안전하게 수정하는 방법. inner/left/outer 조인의 차이, 행 수 폭증 원인, validate 옵션 활용을 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 일곱 번째 글입니다.

---

AI에게 "두 데이터를 합쳐줘"라고 하면 `df1.merge(df2, on='id')`가 나옵니다. 기본 조인 방식은 `inner`입니다. 그런데 실행하면 예상보다 행이 훨씬 많아지거나, 반대로 데이터가 사라지는 경우가 생깁니다. 왜 이런 일이 생기는지 이해하지 못하면 잘못된 분석 결과를 그대로 사용하게 됩니다.

바이브코딩에서 `merge`는 특히 주의가 필요합니다. AI가 생성한 `merge` 코드는 실행은 되지만 조인 방식이 의도와 다를 수 있습니다. 또한 중복 키가 있는 경우 행이 곱셈처럼 늘어나는 카르테시안 폭증이 생길 수 있습니다. 이를 알아채지 못하면 집계 결과가 몇 배로 부풀려집니다.

이번 글에서는 `merge`의 다섯 가지 조인 방식과 안전하게 병합하는 방법을 바이브코딩 관점에서 정리합니다.

> **바이브코딩 관점:** AI가 `merge`를 생성했을 때 "병합 전후 행 수가 얼마나 달라지는지" 반드시 확인해야 합니다. 중복 키 문제로 행이 폭증해도 코드는 오류 없이 실행됩니다.

## 이 글에서 다룰 질문

- inner 조인과 left 조인은 어떤 상황에서 선택해야 할까요?
- AI 코드에서 병합 후 행 수가 늘어났다면 어떤 문제일까요?
- `validate` 옵션으로 키 관계를 어떻게 검증할까요?
- 열 이름이 충돌할 때 AI가 생성하는 코드를 어떻게 개선할까요?
- 병합 후 NaN이 생기는 이유와 처리 방법은 무엇일까요?

---

## 다섯 가지 조인 방식

| 조인 방식 | `how` 값 | 결과 | 언제 쓸까 |
|---|---|---|---|
| 안쪽 조인 | `inner` (기본값) | 양쪽 모두 있는 키만 | 양쪽에 반드시 존재해야 할 때 |
| 왼쪽 조인 | `left` | 왼쪽 전체 유지 | 기준 표를 보존하며 정보 추가 |
| 오른쪽 조인 | `right` | 오른쪽 전체 유지 | left 조인의 역방향 |
| 바깥쪽 조인 | `outer` | 양쪽 키의 합집합 | 양쪽 모두 보존해야 할 때 |
| 교차 조인 | `cross` | 모든 조합 | 모든 쌍이 필요할 때 |

---

## Before / After: 병합 안전하게 하기

**Before (AI 기본 생성 코드, 행 수 확인 없음):**
```python
result = users.merge(orders, on="uid")
print(result.head())
# 행 수를 확인하지 않아 폭증 여부 모름
```

**After (검증이 포함된 안전한 병합):**
```python
print(f"users: {len(users)}행")
print(f"orders: {len(orders)}행")

result = users.merge(orders, on="uid", how="left", indicator=True)

print(f"병합 후: {len(result)}행")
print(result["_merge"].value_counts())
```

---

## AI가 자주 생성하는 병합 패턴

### 기본 병합 (inner join)

```python
import pandas as pd

users = pd.DataFrame({"uid": [1, 2, 3], "name": ["a", "b", "c"]})
orders = pd.DataFrame({"uid": [1, 1, 2], "amount": [100, 200, 50]})

# 기본값은 inner join
print(users.merge(orders, on="uid"))
```

기본 `how="inner"`이므로 users에 있는 uid=3 행은 사라집니다. AI가 left 조인이 필요한 상황에서 inner를 생성하면 데이터가 손실됩니다.

### left 조인과 indicator

```python
# 왼쪽 조인: users의 모든 행 유지
result = users.merge(orders, on="uid", how="left", indicator=True)
print(result)
```

**출력:**
```
   uid name  amount     _merge
0    1    a   100.0       both
1    1    a   200.0       both
2    2    b    50.0       both
3    3    c     NaN  left_only
```

`indicator=True`를 추가하면 각 행이 어느 쪽에서 왔는지 `_merge` 열로 확인할 수 있습니다. 병합 후 디버깅에 매우 유용합니다.

### 열 이름 충돌 처리

```python
df1 = pd.DataFrame({"k": [1], "v": [10]})
df2 = pd.DataFrame({"k": [1], "v": [20]})

# suffixes로 충돌 해결
print(df1.merge(df2, on="k", suffixes=("_a", "_b")))
```

**출력:**
```
   k  v_a  v_b
0  1   10   20
```

### 키 관계 검증 (validate)

```python
try:
    users.merge(orders, on="uid", validate="one_to_one")
except Exception as e:
    print("예상된 오류:", type(e).__name__)
    # MergeError: 중복 키 발견
```

`validate` 옵션은 조인 가정을 코드에 명시합니다. 기대한 관계가 아니면 즉시 오류를 발생시켜 조용한 데이터 오염을 막습니다.

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | 문제 | 해결 방법 |
|---|---|---|
| 중복 키 미확인 | 행 수가 폭증해도 오류 없이 실행됨 | 병합 전후 `len()` 비교, `validate` 사용 |
| inner join을 기본 사용 | 한쪽에만 있는 데이터 손실 | 의도에 맞게 `how` 명시 |
| suffixes 미지정 | 같은 이름 열이 `_x`, `_y`로 자동 지정 | `suffixes=('_left', '_right')` 명시 |
| 키 자료형 불일치 | 정수 키와 문자열 키를 병합하면 매칭 안 됨 | 병합 전 자료형 통일 |
| 병합 후 NaN 미처리 | 이후 계산에서 예상 밖 오류 | `fillna()` 또는 조건 처리 추가 |

---

## AI 팁: 이런 프롬프트를 써보세요

**병합 방식 선택 도움 요청:**
> "고객 테이블과 주문 테이블을 병합하는데, 주문이 없는 고객도 결과에 포함해야 합니다. 어떤 조인 방식이 적절한지 설명하고 코드를 작성해줘."

**행 수 폭증 해결 요청:**
> "이 merge 코드를 실행했더니 예상보다 행 수가 훨씬 많아졌습니다. 원인을 파악하고 중복을 제거하는 코드를 작성해줘."

**validate 추가 요청:**
> "이 merge 코드에 validate 옵션을 추가해서 one_to_many 관계임을 검증하는 코드로 바꿔줘."

---

## 체크리스트

- [ ] inner, left, outer 조인의 차이를 설명할 수 있다
- [ ] 병합 전후 행 수를 확인하는 습관이 있다
- [ ] `indicator=True`로 각 행의 출처를 확인할 수 있다
- [ ] `suffixes`로 열 이름 충돌을 해결할 수 있다
- [ ] `validate` 옵션으로 키 관계를 검증할 수 있다

---

## 처음 질문으로 돌아가기

- **inner 조인과 left 조인은 어떤 상황에서 선택해야 할까요?**
  - 기준 표(왼쪽)의 모든 행을 유지해야 한다면 left 조인, 양쪽 모두에 존재하는 데이터만 필요하면 inner 조인을 씁니다.
- **AI 코드에서 병합 후 행 수가 늘어났다면 어떤 문제일까요?**
  - 오른쪽 테이블에 중복 키가 있어서 한 행이 여러 행에 매칭되는 카르테시안 폭증입니다. `validate="one_to_many"` 등으로 미리 검증하거나 중복을 제거해야 합니다.
- **`validate` 옵션으로 키 관계를 어떻게 검증할까요?**
  - `merge(..., validate="one_to_one")`이나 `"one_to_many"` 등을 지정하면 관계가 맞지 않을 때 즉시 오류를 냅니다.

---

## 정리

병합은 데이터를 이어 붙이는 것이 아니라 관계를 검증하는 작업입니다. AI가 생성한 `merge` 코드는 실행은 되지만 조인 방식과 키 관계가 의도와 다를 수 있습니다. 병합 전후 행 수 확인과 `validate` 옵션을 습관으로 만들면 조용한 데이터 오염을 예방할 수 있습니다. 다음 글에서는 시계열 데이터를 다루는 방법을 알아봅니다.

---

## 참고 자료

- [pandas Merge, join, concatenate and compare](https://pandas.pydata.org/docs/user_guide/merging.html)
- [pandas merge 문서](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
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
- **바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인 (현재 글)**
- 바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기
- 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화
- 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석
<!-- toc:end -->

Tags: 바이브코딩, Pandas, merge, join, 데이터분석
