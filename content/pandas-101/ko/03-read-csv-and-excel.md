---
series: pandas-101
episode: 3
title: "Pandas 101 (3/10): CSV와 Excel 읽기"
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
  - CSV
  - Excel
  - DataAnalysis
  - Beginner
seo_description: CSV와 Excel을 정확히 읽는 핵심 옵션과 점검 순서를 정리한 글입니다
last_reviewed: '2026-05-15'
---

# Pandas 101 (3/10): CSV와 Excel 읽기

분석 작업이 자주 실패하는 이유는 복잡한 모델보다 훨씬 앞단에 있습니다. 파일을 처음 읽는 순간 문자 인코딩이 깨지고, 숫자 열이 문자열로 들어오고, 날짜가 날짜로 해석되지 않으면 그 뒤의 계산은 전부 흔들립니다. 읽기 단계는 사소한 준비가 아니라 분석 품질을 결정하는 첫 관문입니다.

이 글은 Pandas 101 시리즈의 3번째 글입니다.

이번 글에서는 `read_csv`와 `read_excel`을 단순한 파일 열기 함수로 보지 않고, 데이터를 의도한 형태로 적재하는 설정 지점으로 보겠습니다.

![Pandas 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/03/03-01-concept-at-a-glance.ko.png)
*Pandas 101 3장 흐름 개요*
> 읽기는 사소한 함수 호출이 아니라 **데이터의 품질과 의도를 정하는 첫 관문**입니다. 여기서의 설정이 이후 모든 분석의 신뢰성을 결정합니다.

## 이 글에서 다룰 문제

- `read_csv`와 `read_excel`에서 가장 먼저 봐야 할 옵션은 무엇일까요?
- 문자 인코딩과 구분자는 왜 자주 문제를 일으킬까요?
- 자료형을 명시하면 어떤 이점이 있을까요?
- 이 기능을 대규모 데이터에 적용할 때 성능 함정은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?

실제 분석의 상당 부분은 적재와 정제에 들어갑니다. 읽는 순간의 작은 실수 하나가 나중에는 자료형 버그, 정렬 오류, 잘못된 집계로 되돌아옵니다.

## 핵심 개념 정의

- **인코딩**: 파일의 문자 표현 방식입니다.
- **구분자**: 열을 나누는 문자입니다.
- **헤더**: 열 이름이 들어 있는 행 위치입니다.
- **자료형 지정**: 열별 타입을 명시하는 설정입니다.
- **날짜 파싱**: 날짜 열을 읽는 시점에 날짜형으로 바꾸는 작업입니다.

## 파일 형식별 read 함수

파일 형식에 따라 다른 read 함수를 사용합니다. 각 형식의 특성과 성능을 이해하면 적절한 선택을 할 수 있습니다.

| 형식 | 함수 | 주요 옵션 | 읽기 속도 | 파일 크기 |
| --- | --- | --- | --- | --- |
| CSV | `read_csv` | `encoding`, `sep`, `dtype` | 보통 | 큼 |
| Excel | `read_excel` | `sheet_name`, `header` | 느림 | 보통 |
| JSON | `read_json` | `orient`, `lines` | 보통 | 보통 |
| Parquet | `read_parquet` | `columns` | 매우 빠름 | 매우 작음 |
| Feather | `read_feather` | `columns` | 가장 빠름 | 작음 |

CSV는 가장 흔하지만 인코딩 문제가 자주 생깁니다. Parquet는 타입 정보가 포함되어 있고 압축도 되어 있어 대용량 처리에 효율적입니다.

## 전과 후

이전 관점: `read_csv`만 호출하고 결과가 이상하면 나중에 고칩니다.

이후 관점: 인코딩, 자료형, 날짜 열, 시트 이름을 읽는 순간부터 의식합니다.

## 실습: 다섯 단계로 읽기

### 1단계 - 기본으로 읽고 즉시 점검하기

```python
import pandas as pd

# 예제용 CSV 생성
csv_content = """product_id,qty,amount,date
A001,10,1500.0,2026-01-15
B002,5,800.0,2026-01-16
C003,20,3200.0,2026-01-17
"""
with open("/tmp/sales.csv", "w") as f:
    f.write(csv_content)

# 읽고 즉시 점검
df = pd.read_csv("/tmp/sales.csv")
print("크기:", df.shape)
print()
print("자료형:")
print(df.dtypes)
print()
print("첫 행:")
print(df.head(2))
```

**예상 출력:**

```text
크기: (3, 4)

자료형:
product_id     object
qty             int64
amount        float64
date           object
dtype: object

첫 행:
  product_id  qty   amount        date
0       A001   10   1500.0  2026-01-15
1       B002    5    800.0  2026-01-16
```

파일을 읽자마자 크기와 자료형을 함께 보는 이유가 여기 있습니다. `date` 열이 object(문자열)로 읽혔습니다. 이 상태로는 시계열 분석이 불가능합니다.

### 2단계 - 자료형과 날짜 명시하기

```python
df = pd.read_csv(
    "/tmp/sales.csv",
    dtype={
        "product_id": "string",
        "qty":        "int32",
        "amount":     "float32",
    },
    parse_dates=["date"],
)
print(df.dtypes)
print()
print(df)
```

**예상 출력:**

```text
product_id            string
qty                    int32
amount               float32
date          datetime64[ns]
dtype: object

  product_id  qty    amount       date
0       A001   10  1500.000 2026-01-15
1       B002    5   800.000 2026-01-16
2       C003   20  3200.000 2026-01-17
```

자료형을 명시하면 메모리를 아끼는 것뿐 아니라, 선행 0이 중요한 식별자나 날짜 열을 안정적으로 다룰 수 있습니다.

### 3단계 - 인코딩과 구분자 지정하기

```python
# 세미콜론 구분 + latin-1 인코딩 CSV 예제
csv_semi = "id;name;value\n1;Müller;100\n2;García;200\n"
with open("/tmp/euro.csv", "w", encoding="latin-1") as f:
    f.write(csv_semi)

# 올바른 읽기
df_euro = pd.read_csv("/tmp/euro.csv", encoding="latin-1", sep=";")
print(df_euro)
print(df_euro.dtypes)
```

**예상 출력:**

```text
   id    name  value
0   1  Müller    100
1   2  García    200
id       int64
name    object
value    int64
dtype: object
```

문자가 깨지거나 열이 한 칸으로 뭉쳐 들어오면 가장 먼저 확인할 항목이 인코딩과 구분자입니다.

### 4단계 - Excel 읽기

```python
import openpyxl   # pip install openpyxl

# 예제 Excel 생성
df_write = pd.DataFrame({
    "제품": ["A", "B", "C"],
    "판매량": [100, 200, 150],
    "매출": [10000, 25000, 18000],
})
df_write.to_excel("/tmp/report.xlsx", sheet_name="Q1", index=False)

# 읽기
xls = pd.read_excel("/tmp/report.xlsx", sheet_name="Q1", dtype={"판매량": "int32"})
print(xls)
print(xls.dtypes)
```

**예상 출력:**

```text
  제품  판매량    매출
0  A   100  10000
1  B   200  25000
2  C   150  18000
제품     object
판매량     int32
매출      int64
dtype: object
```

Excel은 CSV보다 구조 변형이 많습니다. 시트 이름과 헤더 위치를 명시해 두면 사람이 손으로 만든 파일에서도 안정적으로 읽을 수 있습니다.

### 5단계 - 큰 파일은 나눠서 읽기

```python
# 대용량 CSV 시뮬레이션
import numpy as np

large_df = pd.DataFrame({
    "id":     np.arange(500_000),
    "value":  np.random.randn(500_000),
    "label":  np.random.choice(["A", "B", "C"], 500_000),
})
large_df.to_csv("/tmp/large.csv", index=False)

# 청크 단위 읽기
total_rows = 0
total_sum  = 0.0

for chunk in pd.read_csv("/tmp/large.csv", chunksize=100_000):
    total_rows += len(chunk)
    total_sum  += chunk["value"].sum()

print(f"총 행 수: {total_rows:,}")
print(f"value 합계: {total_sum:.2f}")
```

**예상 출력:**

```text
총 행 수: 500,000
value 합계: -12.34
```

청크 단위 적재는 큰 파일을 통째로 메모리에 올리지 않고도 집계나 필터링을 처리할 수 있게 해 줍니다.

## read_csv 핵심 옵션 상세

```python
import pandas as pd

# 실무에서 자주 쓰는 옵션 조합
df = pd.read_csv(
    "data.csv",
    encoding="utf-8",           # 인코딩 (utf-8, cp949, latin-1)
    sep=",",                    # 구분자
    header=0,                   # 헤더 행 위치 (0=첫 행)
    usecols=["id", "amount"],   # 필요한 열만 읽기
    dtype={"id": "string"},     # 열별 자료형 지정
    parse_dates=["created_at"], # 날짜 파싱
    na_values=["N/A", "-", ""],  # 결측치로 인식할 값
    nrows=1000,                 # 처음 N행만 읽기
    skiprows=[1, 2],            # 특정 행 건너뛰기
    chunksize=None,             # 청크 크기 (None=전체 로드)
    on_bad_lines="skip",        # 오류 행 처리
)
```

### 특정 열만 읽기

```python
# 수백 열 중 필요한 것만
df_small = pd.read_csv("/tmp/large.csv", usecols=["id", "label"])
print(f"전체 열 중 2개만: {df_small.shape}")
print(df_small.head(3))
```

`usecols`로 필요한 열만 골라 읽으면 메모리와 읽기 시간을 크게 줄일 수 있습니다. 특히 수백 개의 열이 있는 파일에서 유용합니다.

## 읽기 성능 비교

같은 데이터를 다른 형식으로 저장했을 때 읽기 속도와 파일 크기 차이를 확인합니다.

```python
import time, os

# 테스트 데이터
df_bench = pd.DataFrame({
    "id":     np.arange(1_000_000),
    "value":  np.random.rand(1_000_000),
    "label":  np.random.choice(["X", "Y", "Z"], 1_000_000),
})

# CSV 저장
df_bench.to_csv("/tmp/bench.csv", index=False)

# Parquet 저장
df_bench.to_parquet("/tmp/bench.parquet", index=False)

# 읽기 시간 비교
start = time.time()
pd.read_csv("/tmp/bench.csv")
csv_time = time.time() - start

start = time.time()
pd.read_parquet("/tmp/bench.parquet")
pq_time = time.time() - start

csv_mb = os.path.getsize("/tmp/bench.csv") / 1024 / 1024
pq_mb  = os.path.getsize("/tmp/bench.parquet") / 1024 / 1024

print(f"CSV:     {csv_time:.2f}초, {csv_mb:.1f} MB")
print(f"Parquet: {pq_time:.2f}초, {pq_mb:.1f} MB")
print(f"속도 향상: {csv_time / pq_time:.1f}배 빠름")
print(f"크기 절감: {csv_mb / pq_mb:.1f}배 작음")
```

**예상 출력:**

```text
CSV:     1.23초, 28.5 MB
Parquet: 0.18초,  8.2 MB
속도 향상: 6.8배 빠름
크기 절감: 3.5배 작음
```

반복적으로 읽는 데이터라면 CSV 대신 Parquet으로 변환해 두는 것이 실용적입니다.

## 오류 처리 패턴

```python
# 불량 행 처리
df_dirty = pd.read_csv("dirty.csv", on_bad_lines="skip")
print(f"읽힌 행 수: {len(df_dirty)}")

# 인코딩 오류 처리
df_enc = pd.read_csv("data.csv", encoding="utf-8", encoding_errors="replace")

# 읽기 후 검증
def validate_df(df, required_cols, min_rows=1):
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"누락된 열: {missing}")
    if len(df) < min_rows:
        raise ValueError(f"행 수 부족: {len(df)} < {min_rows}")
    return True

# 사용 예
# validate_df(df, required_cols=["id", "amount", "date"])
```

## 여러 파일 통합

실무에서는 여러 파일을 읽어 하나로 통합하는 작업이 자주 등장합니다.

```python
import glob

# 월별 파일 통합 패턴
files = glob.glob("data/sales_2026_*.csv")
dfs = []

for file in files:
    df_part = pd.read_csv(
        file,
        dtype={"product_id": "string", "amount": "float32"},
        parse_dates=["date"],
    )
    df_part["source_file"] = file   # 출처 추적
    dfs.append(df_part)

if dfs:
    combined = pd.concat(dfs, ignore_index=True)
    print(f"통합 결과: {combined.shape}")
else:
    print("파일 없음")
```

여러 파일을 결합할 때는 열 구조가 동일한지 반드시 확인해야 합니다.

## 압축 파일 읽기

```python
# gzip 압축 파일
df = pd.read_csv("data.csv.gz", compression="gzip")

# zip 파일
df = pd.read_csv("data.zip")

# 자동 감지
df = pd.read_csv("data.csv.bz2", compression="infer")
```

압축 파일은 디스크 공간을 절약하면서도 직접 읽을 수 있어 클라우드 환경에서 특히 유용합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 인코딩 생략 | 한국어/유럽어 글자 깨짐 | `encoding="cp949"` 또는 `"utf-8"` 명시 |
| 식별자를 숫자로 읽음 | 선행 0 손실 ("007" → 7) | `dtype={"id": "string"}` |
| 날짜를 문자열로 방치 | 시계열 연산 불가 | `parse_dates=["date"]` 사용 |
| Excel 헤더 위치 무시 | 열 이름 오류 | `header=1` 등 정확히 지정 |
| `sheet_name` 미지정 | 첫 시트만 읽힘 | 시트 이름 또는 인덱스 명시 |

## 실무에서는 이렇게 생각합니다

- 파일 읽기 코드는 별도 모듈로 분리합니다.
- 자료형은 가능한 한 명시적으로 적습니다.
- `parse_dates` 대상은 항상 검토합니다.
- 큰 파일은 `chunksize`로 메모리를 방어합니다.
- 원본 파일은 손대지 않고 읽기 로직만 조정합니다.

## 운영 체크리스트

- [ ] 인코딩을 항상 검토합니다.
- [ ] 필요한 열의 자료형을 지정합니다.
- [ ] 날짜 열을 읽는 시점에 처리할지 판단합니다.
- [ ] Excel에서는 시트 이름과 헤더 위치를 확인합니다.
- [ ] 읽기 후 `shape`와 `dtypes`로 즉시 점검합니다.

## 연습 문제

1. UTF-8이 아닌 CSV를 읽고 자료형을 출력해 보세요.
2. `parse_dates` 유무에 따라 출력 자료형이 어떻게 달라지는지 비교해 보세요.
3. `chunksize`를 이용해 행 수를 세는 함수를 작성해 보세요.
4. 같은 데이터를 CSV와 Parquet로 저장한 뒤 파일 크기와 읽기 속도를 비교해 보세요.

## 정리와 다음 글

좋은 분석은 대개 좋은 적재에서 시작합니다. 파일을 읽는 순간부터 데이터 계약을 의식하면 뒤의 정제와 해석이 훨씬 단단해집니다. 다음 글에서는 읽어 온 표에서 필요한 행과 열을 고르는 방법을 다루겠습니다.

## 처음 질문으로 돌아가기

- **`read_csv`와 `read_excel`에서 가장 먼저 봐야 할 옵션은 무엇일까요?**
  - `encoding`(인코딩), `dtype`(자료형), `parse_dates`(날짜 파싱)를 먼저 확인합니다. 읽은 직후 `dtypes`로 결과를 점검하는 습관도 중요합니다.
- **문자 인코딩과 구분자는 왜 자주 문제를 일으킬까요?**
  - 파일 작성자의 환경(OS, 언어 설정)에 따라 인코딩이 제각각이고, CSV는 표준이 없어 구분자도 다양하기 때문입니다.
- **자료형을 명시하면 어떤 이점이 있을까요?**
  - 메모리 절감, 선행 0 보존, 날짜 연산 가능, 이후 계산의 정확도 보장 등 다방면에서 이점이 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- **Pandas 101 (3/10): CSV와 Excel 읽기 (현재 글)**
- [Pandas 101 (4/10): 필터링과 선택](./04-filtering-and-selection.md)
- [Pandas 101 (5/10): 결측치 처리](./05-missing-values.md)
- [Pandas 101 (6/10): 그룹화와 집계](./06-groupby.md)
- [Pandas 101 (7/10): 병합과 조인](./07-merge-and-join.md)
- [Pandas 101 (8/10): 시계열 데이터 다루기](./08-time-series.md)
- [Pandas 101 (9/10): 적용 함수와 벡터화](./09-apply-and-vectorization.md)
- [실전 데이터 분석](./10-real-world-data-analysis.md)

<!-- toc:end -->

## 참고 자료

- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas — read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas — IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Real Python — Reading and Writing CSV Files](https://realpython.com/python-csv/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, CSV, Excel, DataAnalysis, Beginner
