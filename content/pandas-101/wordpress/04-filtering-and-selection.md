---
series: pandas-101
episode: 4
title: "바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - 필터링
  - loc
  - iloc
seo_description: AI가 생성한 pandas 필터링 코드에서 loc, iloc, 조건 마스크, query의 차이를 이해하고 SettingWithCopyWarning을 해결하는 방법을 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 네 번째 글입니다.

---

AI에게 pandas 필터링 코드를 요청하면 여러 방식이 섞여 나옵니다. `df.loc`, `df.iloc`, `df[조건]`, `df.query()`. 결과가 같아 보여도 동작 방식과 적합한 상황이 다릅니다. 그리고 잘못 쓰면 `SettingWithCopyWarning`이라는 경고와 함께 값이 실제로 바뀌지 않는 조용한 버그가 생깁니다.

바이브코딩을 하다 보면 AI가 생성한 선택 코드를 수정해야 하는 순간이 자주 옵니다. "이 조건에 맞는 행의 특정 열 값을 바꿔줘"라고 했을 때 AI가 경고를 내는 코드를 생성하기도 합니다. 이때 어떻게 고쳐야 하는지 알려면 `loc`와 조건 마스크의 차이를 이해해야 합니다.

이번 글에서는 pandas의 네 가지 선택 방식을 바이브코딩 관점에서 정리합니다. AI 코드에서 `SettingWithCopyWarning`이 왜 나오는지, `loc`를 언제 써야 하는지가 핵심입니다.

> **바이브코딩 관점:** AI가 생성한 `df[df['x'] > 0]['y'] = 100` 코드는 경고를 냅니다. 올바른 코드는 `df.loc[df['x'] > 0, 'y'] = 100`입니다. 이 차이를 이해하면 AI 코드를 안정적으로 수정할 수 있습니다.

## 이 글에서 다룰 질문

- `loc`와 `iloc`는 언제 구분해서 써야 할까요?
- `SettingWithCopyWarning`은 왜 나오고 어떻게 해결할까요?
- 조건 마스크에서 `and/or` 대신 `&/|`를 써야 하는 이유는 무엇일까요?
- `query()`는 어떤 상황에서 코드를 더 읽기 쉽게 만들까요?
- AI가 생성한 체이닝 인덱싱 코드를 어떻게 안전하게 바꿀까요?

---

## 네 가지 선택 방식 비교

| 방식 | 용도 | 특징 |
|---|---|---|
| `df['x']` | 열 선택 | 열 이름으로 직접 |
| `df.loc` | 레이블 기반 | 행과 열을 이름으로. 할당에 안전 |
| `df.iloc` | 위치 기반 | 행과 열을 숫자 위치로 |
| `df[조건]` | 조건 필터링 | 불리언 마스크 |
| `df.query()` | 문자열 조건 | 복잡한 조건에 가독성 좋음 |

---

## Before / After: SettingWithCopyWarning 해결

**Before (AI가 자주 생성하는, 경고가 나오는 패턴):**
```python
# 경고 발생! 값이 실제로 안 바뀔 수 있음
df[df['x'] > 0]['y'] = 100
```

**After (올바른 패턴):**
```python
# loc를 사용해 안전하게 할당
df.loc[df['x'] > 0, 'y'] = 100
```

이 차이가 `SettingWithCopyWarning`의 핵심입니다. 체이닝 인덱싱(`df[조건]['열']`)은 복사본에 쓸 수 있어서 원본이 바뀌지 않을 수 있습니다.

---

## AI가 자주 생성하는 선택 패턴

### 열 선택

```python
import pandas as pd

df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}, index=["a", "b", "c"])

# 열 하나 → Series
print(df["x"])

# 여러 열 → DataFrame
print(df[["x", "y"]])
```

### 레이블로 고르기 (loc)

```python
# 특정 행
print(df.loc["a"])

# 특정 행과 열 동시에
print(df.loc[["a", "c"], "x"])
```

**출력:**
```
a    1
c    3
Name: x, dtype: int64
```

`loc`는 슬라이싱에서 끝점을 포함합니다. `df.loc["a":"c"]`는 a, b, c 모두 포함합니다.

### 위치로 고르기 (iloc)

```python
# 첫 번째 행
print(df.iloc[0])

# 처음 2행, 첫 번째 열
print(df.iloc[0:2, 0])
```

`iloc`는 파이썬 슬라이싱과 같이 끝점을 제외합니다. `df.iloc[0:2]`는 0, 1행만 포함합니다. `loc`와 반대입니다.

### 조건 필터링 (불리언 마스크)

```python
# 단일 조건
print(df[df["x"] > 1])

# 복수 조건 (반드시 괄호와 &, | 사용)
print(df[(df["x"] > 1) & (df["y"] < 30)])

# 부정 조건
print(df[~(df["x"] > 1)])
```

**중요:** `and`/`or` 대신 반드시 `&`/`|`를 써야 합니다. `and`는 두 배열 전체를 비교하려 해서 오류가 납니다.

### query()로 가독성 높이기

```python
# 조건이 길어질수록 query가 읽기 쉬움
print(df.query("x > 1 and y < 30"))

# 변수 참조
threshold = 1
print(df.query("x > @threshold"))
```

### isin으로 목록 필터링

```python
# 긴 OR 체인 대신
print(df[df["x"].isin([1, 3])])
```

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | 잘못된 코드 | 올바른 코드 |
|---|---|---|
| 조건에 and/or 사용 | `df[df['x'] > 1 and df['y'] < 30]` | `df[(df['x'] > 1) & (df['y'] < 30)]` |
| 체이닝 인덱싱으로 할당 | `df[df['x'] > 0]['y'] = 100` | `df.loc[df['x'] > 0, 'y'] = 100` |
| loc에서 끝점 혼동 | `df.loc[0:2]` (0,1,2 포함) | 의도 확인 후 iloc 사용 고려 |
| iloc에 레이블 사용 | `df.iloc['a']` | `df.loc['a']` |
| isin 대신 OR 체인 | `df[(df['x']==1)\|(df['x']==2)\|(df['x']==3)]` | `df[df['x'].isin([1,2,3])]` |

---

## AI 팁: 이런 프롬프트를 써보세요

**SettingWithCopyWarning 해결 요청:**
> "이 코드에서 SettingWithCopyWarning 경고가 납니다. loc를 사용해서 안전하게 바꿔줘: `df[df['score'] > 80]['grade'] = 'A'`"

**복잡한 조건 정리 요청:**
> "이 조건 필터링 코드를 query()를 사용해서 더 읽기 쉽게 바꿔줘."

**조건 변수 분리 요청:**
> "이 복잡한 조건 마스크를 이름 있는 변수로 나눠서 읽기 쉽게 만들어줘."

---

## 체크리스트

- [ ] `loc`(레이블)와 `iloc`(위치)의 차이를 설명할 수 있다
- [ ] 조건 마스크에서 `&`/`|`를 써야 하는 이유를 안다
- [ ] `SettingWithCopyWarning`이 왜 나오는지 이해한다
- [ ] 체이닝 인덱싱을 `loc`로 바꿀 수 있다
- [ ] `isin`으로 목록 필터링을 할 수 있다

---

## 처음 질문으로 돌아가기

- **`loc`와 `iloc`는 언제 구분해서 써야 할까요?**
  - 행/열 이름으로 고를 때는 `loc`, 숫자 위치로 고를 때는 `iloc`를 씁니다. 할당이 필요할 때는 항상 `loc`를 우선합니다.
- **`SettingWithCopyWarning`은 왜 나오고 어떻게 해결할까요?**
  - 체이닝 인덱싱(`df[조건]['열']`)이 복사본을 만들어 원본이 바뀌지 않을 수 있기 때문입니다. `df.loc[조건, '열']`로 바꾸면 해결됩니다.
- **조건 마스크에서 `and/or` 대신 `&/|`를 써야 하는 이유는?**
  - `and`/`or`는 단일 값에 쓰이는 파이썬 논리 연산자로, 배열에 적용하면 오류가 납니다. `&`/`|`는 배열 단위로 동작합니다.

---

## 정리

선택은 분석에서 가장 자주 반복되는 기본 동작입니다. AI가 생성한 선택 코드를 안전하게 수정하려면 `loc`/`iloc`의 차이와 체이닝 인덱싱의 위험성을 이해해야 합니다. 다음 글에서는 결측치를 어떻게 진단하고 처리할지 다룹니다.

---

## 참고 자료

- [pandas Indexing and selecting data](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [pandas query 문서](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html)
- [예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pandas 기초 (1/10): Pandas란 무엇인가?
- 바이브코딩을 위한 Pandas 기초 (2/10): 시리즈와 데이터프레임
- 바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기
- **바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택 (현재 글)**
- 바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리
- 바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계
- 바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인
- 바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기
- 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화
- 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석
<!-- toc:end -->

Tags: 바이브코딩, Pandas, 필터링, loc, iloc
