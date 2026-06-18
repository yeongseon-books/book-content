---
series: pandas-101
episode: 3
title: "바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Pandas
  - CSV
  - Excel
  - 데이터분석
seo_description: AI가 생성한 read_csv, read_excel 코드를 제대로 이해하고 수정하기 위한 핵심 옵션 가이드. 인코딩, 자료형 지정, 날짜 파싱 등 실무 패턴을 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기

이 글은 **바이브코딩을 위한 Pandas 기초** 시리즈의 세 번째 글입니다.

---

AI에게 "이 CSV 파일을 읽는 코드를 작성해줘"라고 하면 `pd.read_csv('file.csv')`가 나옵니다. 데이터가 깔끔하면 이 한 줄로 충분합니다. 하지만 현실 데이터는 그렇지 않습니다. 한글이 깨지거나, 숫자가 문자열로 들어오거나, 날짜가 날짜로 인식되지 않는 상황이 생깁니다.

바이브코딩에서 데이터 읽기는 특히 중요합니다. AI가 생성한 `read_csv` 코드가 오류 없이 실행되더라도, 자료형이 틀리면 이후의 모든 분석이 잘못됩니다. AI에게 옵션을 제대로 지정해달라고 요청하려면, 어떤 옵션이 있는지 알아야 합니다.

이번 글에서는 `read_csv`와 `read_excel`의 핵심 옵션을 AI 코드를 수정하는 관점에서 정리합니다. 파일을 읽은 직후 무엇을 확인해야 하는지도 함께 다룹니다.

> **바이브코딩 관점:** AI가 생성한 `read_csv` 코드는 기본 옵션으로 파일을 읽습니다. 인코딩, 자료형, 날짜 열을 명시하지 않으면 이후 분석에서 조용히 오류가 생깁니다. 읽기 코드를 고치는 법을 알아야 AI와의 협업이 안정적입니다.

## 이 글에서 다룰 질문

- AI가 생성한 `read_csv`에서 가장 먼저 확인해야 할 것은 무엇일까요?
- 한글 데이터를 읽을 때 왜 인코딩 오류가 나고 어떻게 고칠까요?
- AI 코드에서 날짜가 문자열로 읽히는 문제를 어떻게 해결할까요?
- 큰 파일을 읽을 때 AI가 놓치기 쉬운 함정은 무엇일까요?
- `read_csv` 직후에 반드시 실행해야 할 점검 코드는 무엇일까요?

---

## 파일 읽기: AI가 놓치는 것들

AI가 생성하는 가장 단순한 읽기 코드:

```python
df = pd.read_csv("sales.csv")
```

이 코드는 오류 없이 실행될 수 있지만, 다음이 틀릴 수 있습니다:
- 한글이 깨져서 들어올 수 있음
- 숫자처럼 보이는 상품 코드가 정수로 읽힐 수 있음 (앞의 0이 사라짐)
- 날짜가 문자열로 읽혀 시계열 계산이 안 될 수 있음
- 구분자가 쉼표가 아닌 파일이면 열이 하나로 뭉칠 수 있음

### 핵심 옵션 용어

| 옵션 | 역할 |
|---|---|
| `encoding` | 파일의 문자 인코딩. 한글은 `utf-8` 또는 `cp949` |
| `sep` | 열 구분자. 기본값은 쉼표(`,`) |
| `dtype` | 열별 자료형을 명시적으로 지정 |
| `parse_dates` | 날짜 열을 읽는 시점에 날짜형으로 변환 |
| `usecols` | 필요한 열만 선택해서 읽기 |
| `chunksize` | 큰 파일을 나눠서 읽기 |

---

## Before / After: 읽기 코드 개선

**Before (AI 기본 생성 코드):**
```python
df = pd.read_csv("sales.csv")
print(df.head())
# 날짜가 object, 상품코드의 앞 0이 사라짐
```

**After (옵션을 명시한 코드):**
```python
df = pd.read_csv(
    "sales.csv",
    encoding="utf-8",
    dtype={"product_id": "string", "qty": "int32"},
    parse_dates=["order_date"],
)
print(df.shape)
print(df.dtypes)
```

---

## AI가 자주 생성하는 읽기 패턴

### 기본 읽기 직후 점검 (가장 중요)

```python
import pandas as pd

df = pd.read_csv("sales.csv")
print(df.shape)   # 행 수, 열 수가 예상과 맞는지
print(df.dtypes)  # 자료형이 올바른지
print(df.head())  # 처음 5행으로 내용 확인
```

파일을 읽자마자 이 세 줄을 실행하는 것이 습관이 되면, 자료형 문제를 초반에 잡을 수 있습니다.

### 인코딩과 구분자 지정

```python
# 한글 데이터 (CP949 인코딩)
df = pd.read_csv("korean_data.csv", encoding="cp949")

# 세미콜론 구분 파일
df = pd.read_csv("data.csv", sep=";")

# 탭 구분 파일
df = pd.read_csv("data.tsv", sep="\t")
```

AI가 생성한 코드에서 열이 하나로 뭉쳐 나오면 `sep` 옵션을 확인하세요.

### 자료형 명시와 날짜 파싱

```python
df = pd.read_csv(
    "sales.csv",
    dtype={"product_id": "string", "qty": "int32"},
    parse_dates=["order_date"],
    date_format="%Y-%m-%d",
)
print(df.dtypes)
```

`parse_dates`를 지정하지 않으면 날짜 열이 `object` 타입으로 읽힙니다. 이후 날짜 계산, 리샘플링, 시계열 분석이 모두 막힙니다.

### Excel 읽기

```python
# 기본 읽기
xls = pd.read_excel("report.xlsx")

# 시트와 헤더 위치 지정
xls = pd.read_excel("report.xlsx", sheet_name="Q1", header=1)
print(xls.head())
```

Excel 파일은 시트 이름과 헤더 위치가 다양합니다. AI가 기본값으로 읽으면 틀린 시트나 잘못된 헤더를 읽을 수 있습니다.

### 큰 파일 나눠 읽기

```python
# 전체 행 수 계산
total = 0
for chunk in pd.read_csv("big.csv", chunksize=100_000):
    total += len(chunk)
print(total)
```

---

## 파일 형식별 읽기 함수 비교

| 형식 | 함수 | 주요 확인 옵션 | 주의사항 |
|---|---|---|---|
| CSV | `read_csv` | `encoding`, `sep`, `dtype` | 인코딩, 구분자 확인 |
| Excel | `read_excel` | `sheet_name`, `header` | 시트 이름, 헤더 위치 |
| JSON | `read_json` | `orient`, `lines` | 구조 형태 확인 |
| Parquet | `read_parquet` | `columns` | 타입 정보 포함되어 있음 |

---

## AI 코드에서 자주 보이는 실수 패턴

| 실수 유형 | 문제 | 해결 방법 |
|---|---|---|
| 인코딩 생략 | 한글이 깨져서 들어옴 | `encoding="utf-8"` 또는 `"cp949"` 명시 |
| 식별자 열 숫자 처리 | 앞의 0이 사라짐 (예: `007` → `7`) | `dtype={"id": "string"}` |
| 날짜 파싱 누락 | 날짜가 문자열로 읽힘 | `parse_dates=["date_col"]` |
| Excel 시트 미지정 | 첫 시트만 읽음 | `sheet_name="Q1"` 명시 |
| 메모리 미고려 | 큰 파일에서 메모리 부족 | `chunksize` 또는 `usecols` 사용 |

---

## AI 팁: 이런 프롬프트를 써보세요

**인코딩 문제 해결 요청:**
> "이 CSV 파일을 읽었는데 한글이 깨집니다. encoding 옵션을 자동으로 감지하거나 올바른 값을 찾는 코드를 작성해줘."

**자료형 최적화 요청:**
> "이 DataFrame의 메모리 사용량을 줄이기 위해 read_csv 단계에서 dtype을 최적화하는 코드를 작성해줘."

**읽기 검증 코드 요청:**
> "read_csv로 파일을 읽은 후 열 이름, 자료형, 결측치 개수를 한 번에 확인하는 검증 함수를 작성해줘."

---

## 체크리스트

- [ ] `read_csv` 직후 `shape`, `dtypes`, `head()`로 점검할 수 있다
- [ ] 한글 CSV를 읽을 때 `encoding` 옵션을 지정할 수 있다
- [ ] 날짜 열을 `parse_dates`로 처리할 수 있다
- [ ] `dtype` 딕셔너리로 열별 자료형을 명시할 수 있다
- [ ] Excel에서 시트 이름과 헤더 위치를 지정할 수 있다

---

## 처음 질문으로 돌아가기

- **AI가 생성한 `read_csv`에서 가장 먼저 확인해야 할 것은?**
  - 읽기 직후 `df.shape`와 `df.dtypes`를 확인합니다. 열 수와 자료형이 예상과 다르면 옵션을 조정해야 합니다.
- **한글 데이터를 읽을 때 인코딩 오류가 나면?**
  - `encoding="cp949"` 또는 `encoding="utf-8"`을 명시합니다. `encoding="utf-8-sig"`는 BOM이 있는 파일에 필요합니다.
- **날짜가 문자열로 읽히는 문제를 어떻게 해결할까요?**
  - `parse_dates=["date_column"]`을 `read_csv`에 추가합니다.

---

## 정리

좋은 분석은 좋은 데이터 읽기에서 시작합니다. AI가 생성한 `read_csv` 코드는 대부분 기본 옵션만 사용합니다. 인코딩, 자료형, 날짜 열을 명시하는 습관을 들이면 이후 분석의 신뢰도가 크게 높아집니다. 다음 글에서는 읽어온 DataFrame에서 필요한 행과 열을 고르는 방법을 다룹니다.

---

## 참고 자료

- [pandas read_csv 문서](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas read_excel 문서](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas IO tools 가이드](https://pandas.pydata.org/docs/user_guide/io.html)
- [예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Pandas 기초 (1/10): Pandas란 무엇인가?
- 바이브코딩을 위한 Pandas 기초 (2/10): 시리즈와 데이터프레임
- **바이브코딩을 위한 Pandas 기초 (3/10): CSV와 Excel 읽기 (현재 글)**
- 바이브코딩을 위한 Pandas 기초 (4/10): 필터링과 선택
- 바이브코딩을 위한 Pandas 기초 (5/10): 결측치 처리
- 바이브코딩을 위한 Pandas 기초 (6/10): 그룹화와 집계
- 바이브코딩을 위한 Pandas 기초 (7/10): 병합과 조인
- 바이브코딩을 위한 Pandas 기초 (8/10): 시계열 데이터 다루기
- 바이브코딩을 위한 Pandas 기초 (9/10): 적용 함수와 벡터화
- 바이브코딩을 위한 Pandas 기초 (10/10): 실전 데이터 분석
<!-- toc:end -->

Tags: 바이브코딩, Pandas, CSV, Excel, 데이터분석
