---
series: pandas-101
episode: 9
title: "바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - 벡터화
  - apply
  - 성능
seo_description: AI가 생성한 pandas apply 코드를 더 빠른 벡터화 코드로 바꾸는 방법. np.where, map, 열 단위 연산을 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 아홉 번째 글입니다.

---

AI에게 "각 행의 점수가 80 이상이면 'A', 아니면 'B'를 새 열로 추가해줘"라고 하면 `apply(lambda row: 'A' if row['score'] >= 80 else 'B', axis=1)` 코드가 나올 수 있습니다. 동작은 합니다. 그런데 데이터가 10만 행만 넘어도 눈에 띄게 느려집니다.

바이브코딩에서 성능 문제는 보통 `apply(axis=1)` 과다 사용에서 시작됩니다. AI는 문법적으로 정확한 코드를 생성하지만, 항상 가장 빠른 방법을 고르지는 않습니다. `apply(axis=1)`는 편해 보이지만 pandas의 핵심 장점인 벡터화를 포기하는 선택입니다.

이번 글에서는 AI가 `apply`를 생성했을 때 그것을 더 빠른 벡터화 코드로 바꾸는 방법을 정리합니다. `np.where`, `map`, 열 단위 연산이 핵심 도구입니다.

> **바이브코딩 관점:** AI가 `apply(axis=1)`을 생성했다면 "이것을 np.where나 열 단위 연산으로 바꿔줘"라고 요청하세요. 같은 결과를 수십 배 빠르게 얻을 수 있습니다.

## 이 글에서 다룰 질문

- 벡터화는 정확히 무엇이고 왜 `apply`보다 빠를까요?
- AI가 생성한 `apply(axis=1)` 코드를 어떻게 바꿀까요?
- 조건 분기를 `np.where`로 어떻게 표현할까요?
- `map`은 어떤 상황에서 가장 자연스럽게 사용될까요?
- 자료형 불일치가 벡터화를 방해하는 이유는 무엇일까요?

---

## 벡터화 vs apply: 속도 차이

### 핵심 개념 용어

| 개념 | 설명 |
|---|---|
| **벡터화** | 열 전체를 한 번에 계산. NumPy C 코드 활용 |
| **apply(axis=1)** | 각 행을 파이썬 객체로 처리. 느림 |
| **np.where** | 배열 단위 조건 분기. `if-else`의 벡터화 버전 |
| **map** | 시리즈 값을 딕셔너리나 함수로 치환 |
| **assign** | 새 열을 메서드 체이닝으로 추가 |

---

## Before / After: apply를 벡터화로 변환

**Before (AI 생성 코드, 느린 패턴):**
```python
# apply(axis=1): 각 행마다 파이썬 함수 호출
df["total"] = df.apply(lambda r: r["a"] + r["b"], axis=1)

# 조건 분기도 apply로
df["grade"] = df.apply(lambda r: "A" if r["score"] >= 80 else "B", axis=1)
```

**After (벡터화 버전, 수십~수백 배 빠름):**
```python
# 열 단위 연산
df["total"] = df["a"] + df["b"]

# 조건 분기 → np.where
import numpy as np
df["grade"] = np.where(df["score"] >= 80, "A", "B")
```

---

## AI가 자주 생성하는 패턴과 벡터화 대안

### 열 단위 연산 (가장 빠름)

```python
import numpy as np, pandas as pd

df = pd.DataFrame({"a": np.arange(1_000_000), "b": np.arange(1_000_000)})

# 벡터화: NumPy 레벨 계산
df["c"] = df["a"] + df["b"]
print(df.head(3))
```

**출력:**
```
   a  b  c
0  0  0  0
1  1  1  2
2  2  2  4
```

### 조건 분기: np.where

```python
# 2단계 조건
df["flag"] = np.where(df["a"] % 2 == 0, "even", "odd")

# 다단계 조건: np.select
conditions = [df["a"] < 3, df["a"] < 6]
choices = ["low", "mid"]
df["level"] = np.select(conditions, choices, default="high")
```

### 코드 값 치환: map

```python
mapping = {0: "zero", 1: "one", 2: "two"}
series = pd.Series([0, 1, 2, 3])
print(series.map(mapping))
```

**출력:**
```
0    zero
1     one
2     two
3     NaN
dtype: object
```

`map`에서 딕셔너리에 없는 값은 NaN이 됩니다. AI 코드에서 예상치 못한 NaN이 생기면 이 점을 확인하세요.

### apply가 필요한 경우

벡터화로 표현하기 어려운 복잡한 로직에서만 `apply`를 씁니다:

```python
def complex_logic(row):
    if row["type"] == "A" and row["value"] > 100:
        return row["value"] * 1.1
    elif row["type"] == "B":
        return row["value"] * 0.9
    else:
        return row["value"]

# 이런 경우에만 apply 사용
df["adjusted"] = df.apply(complex_logic, axis=1)
```

단순한 계산에 `apply`를 쓰는 것은 피하세요.

---

## 성능 비교

```python
import pandas as pd, numpy as np, time

df = pd.DataFrame({"a": np.arange(1_000_000), "b": np.arange(1_000_000)})

# apply(axis=1)
start = time.time()
df["c_slow"] = df.apply(lambda r: r["a"] + r["b"], axis=1)
print(f"apply(axis=1): {time.time() - start:.3f}초")

# 벡터화
start = time.time()
df["c_fast"] = df["a"] + df["b"]
print(f"벡터화: {time.time() - start:.3f}초")
```

백만 행 기준으로 `apply(axis=1)`은 수 초, 벡터화는 수 밀리초입니다. 수백 배 이상 차이가 납니다.

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | AI 코드 | 개선된 코드 |
|---|---|---|
| apply로 단순 덧셈 | `df.apply(lambda r: r['a']+r['b'], axis=1)` | `df['a'] + df['b']` |
| apply로 조건 분기 | `df.apply(lambda r: 'A' if r['s']>80 else 'B', axis=1)` | `np.where(df['s']>80, 'A', 'B')` |
| 반복문으로 누적 | `for i, r in df.iterrows(): total += r['v']` | `df['v'].sum()` |
| map 결과 NaN 미확인 | `s.map(d)` 이후 NaN 처리 없음 | `s.map(d).fillna('unknown')` |
| 자료형 혼합 | `object` 열에 수식 적용 | `astype()`으로 자료형 통일 후 계산 |

---

## AI 팁: 이런 프롬프트를 써보세요

**apply 최적화 요청:**
> "이 apply(axis=1) 코드를 np.where나 열 단위 연산으로 바꿔줘: `df.apply(lambda r: r['price'] * r['qty'], axis=1)`"

**다단계 조건 요청:**
> "score 열이 90 이상이면 'A', 70 이상이면 'B', 나머지는 'C'로 분류하는 열을 np.select를 사용해서 추가해줘."

**코드 값 치환 요청:**
> "country_code 열의 'KR', 'US', 'JP' 값을 각각 '한국', '미국', '일본'으로 바꾸는 코드를 map을 사용해서 작성해줘."

---

## 체크리스트

- [ ] 열 단위 연산이 `apply(axis=1)`보다 훨씬 빠른 이유를 설명할 수 있다
- [ ] `np.where`로 2단계 조건 분기를 작성할 수 있다
- [ ] `np.select`로 다단계 조건을 작성할 수 있다
- [ ] `map`으로 코드 값을 치환할 수 있다
- [ ] `apply`가 필요한 상황과 벡터화로 대체 가능한 상황을 구분할 수 있다

---

## 처음 질문으로 돌아가기

- **벡터화는 정확히 무엇이고 왜 `apply`보다 빠를까요?**
  - 벡터화는 열 전체를 NumPy의 C 코드로 한 번에 계산합니다. `apply`는 각 행을 파이썬 객체로 만들어 함수를 반복 호출하므로 훨씬 느립니다.
- **AI가 생성한 `apply(axis=1)` 코드를 어떻게 바꿀까요?**
  - 단순 계산은 열 단위 연산(`df['a'] + df['b']`)으로, 조건 분기는 `np.where`나 `np.select`로 바꿉니다.
- **`map`은 어떤 상황에서 가장 자연스럽게 사용될까요?**
  - 코드 값을 다른 값으로 치환할 때 딕셔너리를 `map`에 전달하면 간결합니다. 딕셔너리에 없는 값은 NaN이 되므로 범위를 확인해야 합니다.

---

## 정리

벡터화는 pandas의 성능과 문법을 함께 이해하는 핵심입니다. AI가 `apply`를 생성하면 "벡터화로 바꿔달라"고 요청하는 것만으로도 코드가 더 짧고 빠르고 읽기 쉬워집니다. 다음 글에서는 지금까지 배운 내용을 하나의 실전 분석 흐름으로 묶어 정리합니다.

---

## 참고 자료

- [pandas Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [pandas apply 문서](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [NumPy Universal functions](https://numpy.org/doc/stable/reference/ufuncs.html)
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
- **바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화 (현재 글)**
- 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석
<!-- toc:end -->

Tags: 바이브코딩, Pandas, 벡터화, apply, 성능
