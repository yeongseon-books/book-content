---
series: pandas-101
episode: 3
title: CSV와 Excel 읽기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Pandas
  - CSV
  - Excel
  - DataAnalysis
  - Beginner
seo_description: read_csv와 read_excel의 핵심 옵션과 인코딩·dtype·헤더 처리까지 데이터 적재의 정석을 정리한 입문 글
last_reviewed: '2026-05-11'
---

# CSV와 Excel 읽기

> Pandas 101 시리즈 (3/10)


## 이 글에서 다룰 문제

분석의 *80%* 는 *적재와 정제* 입니다. *적재 단계의 실수* 는 *나중에 디버깅 비용* 으로 돌아옵니다.

## 전체 흐름
```mermaid
flowchart LR
    File["CSV / Excel"] --> Read["read_csv / read_excel"]
    Read --> Check["dtypes / shape / head"]
    Check --> Fix["fix encoding / dtype / header"]
```

## Before/After

**Before**: *“그냥 read_csv”* — 한글 깨짐, 숫자가 문자열로.

**After**: *“encoding, dtype, parse_dates 명시”* — *데이터가 의도대로* 들어옴.

## 5단계 적재 실습

### 1단계 — 기본 read_csv

```python
import pandas as pd
df = pd.read_csv("sales.csv")
print(df.shape, df.dtypes)
```

### 2단계 — 인코딩과 구분자

```python
df = pd.read_csv("ko_data.csv", encoding="cp949", sep=";")
print(df.head())
```

### 3단계 — dtype 명시

```python
df = pd.read_csv(
    "sales.csv",
    dtype={"product_id": "string", "qty": "int32"},
    parse_dates=["date"],
)
print(df.dtypes)
```

### 4단계 — Excel 읽기

```python
xls = pd.read_excel("report.xlsx", sheet_name="Q1", header=1)
print(xls.head())
```

### 5단계 — 큰 파일은 chunksize

```python
total = 0
for chunk in pd.read_csv("big.csv", chunksize=100_000):
    total += len(chunk)
print(total)
```

## 이 코드에서 주목할 점

- *encoding* 은 *한글 데이터의 첫 함정*.
- `dtype`를 명시하면 메모리를 아끼고 타입 안정성도 확보할 수 있습니다.
- *chunksize* 는 *메모리 한계* 를 회피하는 표준 패턴.

## 자주 하는 실수 5가지

1. ***인코딩 미지정* 으로 한글 깨짐.**
2. ***ID 열* 을 숫자로 읽어 *0이 사라짐*.**
3. ***날짜를 문자열로 둠.** parse_dates를 안 씀.**
4. ***헤더 위치* 가 다른 Excel을 그대로 읽음.**
5. ***sheet_name* 미지정으로 *첫 시트만* 읽음.**

## 실무에서는 이렇게 쓰입니다

ERP 추출 CSV, 회계 Excel, 외부 API의 CSV 응답 — *제대로 읽기* 위해 *옵션 5–10개* 를 *고정 패턴* 으로 잡아둡니다. 적재 함수는 *재사용 가능한 모듈* 로 분리합니다.

## 체크리스트

- [ ] *encoding* 을 *항상 명시* 한다.
- [ ] `dtype`을 지정한다.
- [ ] `parse_dates` 사용 여부를 검토한다.
- [ ] Excel의 `sheet_name`을 명시한다.

## 정리 및 다음 단계

좋은 적재가 *좋은 분석의 출발점* 입니다. 다음 글에서는 *filtering과 selection* 을 다룹니다.

<!-- toc:begin -->
- [Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Series와 DataFrame](./02-series-and-dataframe.md)
- **CSV와 Excel 읽기 (현재 글)**
- filtering과 selection (예정)
- missing value 처리 (예정)
- groupby (예정)
- merge와 join (예정)
- time series (예정)
- apply와 vectorization (예정)
- 실전 데이터 분석 (예정)
<!-- toc:end -->

## 참고 자료

- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas — read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas — IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Real Python — Reading and Writing CSV Files](https://realpython.com/python-csv/)

Tags: Pandas, CSV, Excel, DataAnalysis, Beginner
