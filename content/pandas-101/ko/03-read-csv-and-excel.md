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

이 글은 판다스 101 시리즈의 3번째 글입니다.

분석 작업이 자주 실패하는 이유는 복잡한 모델보다 훨씬 앞단에 있습니다. 파일을 처음 읽는 순간 문자 인코딩이 깨지고, 숫자 열이 문자열로 들어오고, 날짜가 날짜로 해석되지 않으면 그 뒤의 계산은 전부 흔들립니다. 읽기 단계는 사소한 준비가 아니라 분석 품질을 결정하는 첫 관문입니다.

이번 글에서는 `read_csv`와 `read_excel`을 단순한 파일 열기 함수로 보지 않고, 데이터를 의도한 형태로 적재하는 설정 지점으로 보겠습니다.

![Pandas 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pandas-101/03/03-01-concept-at-a-glance.ko.png)
*Pandas 101 3장 흐름 개요*
> 읽기는 사소한 함수 호출이 아니라 **데이터의 품질과 의도를 정하는 첫 관문**입니다. 여기서의 설정이 이후 모든 분석의 신뢰성을 결정합니다.

## 먼저 던지는 질문

- `read_csv`와 `read_excel`에서 가장 먼저 봐야 할 옵션은 무엇일까요?
- 문자 인코딩과 구분자는 왜 자주 문제를 일으킬까요?
- 자료형을 명시하면 어떤 이점이 있을까요?

## 왜 중요한가

실제 분석의 상당 부분은 적재와 정제에 들어갑니다. 읽는 순간의 작은 실수 하나가 나중에는 자료형 버그, 정렬 오류, 잘못된 집계로 되돌아옵니다. 그래서 숙련된 엔지니어일수록 데이터가 들어오는 첫 단계에 더 많은 주의를 둡니다.

## 한눈에 보는 개념

## 핵심 용어

- 인코딩: 파일의 문자 표현 방식입니다.
- 구분자: 열을 나누는 문자입니다.
- 헤더: 열 이름이 들어 있는 행 위치입니다.
- **자료형 지정**: 열별 타입을 명시하는 설정입니다.
- **날짜 파싱**: 날짜 열을 읽는 시점에 날짜형으로 바꾸는 작업입니다.

## 전과 후

이전 관점: `read_csv`만 호출하고 결과가 이상하면 나중에 고칩니다.

이후 관점: 인코딩, 자료형, 날짜 열, 시트 이름을 읽는 순간부터 의식합니다.

## 실습: 다섯 단계로 읽기

### 1단계 - 기본으로 읽기

```python
import pandas as pd
df = pd.read_csv("sales.csv")
print(df.shape, df.dtypes)
```

파일을 읽자마자 크기와 자료형을 함께 보는 이유가 여기 있습니다. 열 개수는 맞아도 자료형이 어긋나면 이후 계산이 모두 흔들릴 수 있습니다.

**예상 출력:**

```text
(3, 3)
product_id    object
qty            int64
amount       float64
dtype: object
```

기본 호출은 빠른 확인에는 좋지만, 그대로 운영 코드가 되면 위험합니다. 읽은 직후 `shape`와 `dtypes`를 같이 보는 습관이 중요합니다.

### 2단계 - 인코딩과 구분자 지정하기

```python
df = pd.read_csv("data.csv", encoding="latin-1", sep=";")
print(df.head())
```

문자가 깨지거나 열이 한 칸으로 뭉쳐 들어오면 가장 먼저 확인할 항목이 인코딩과 구분자입니다. 파일 형식은 CSV처럼 보여도 실제 설정은 제각각인 경우가 많습니다.

## 파일 형식별 read 함수

파일 형식에 따라 다른 read 함수를 사용합니다. 각 형식의 특성과 성능을 이해하면 적절한 선택을 할 수 있습니다.

| 형식 | 함수 | 주요 옵션 | 성능 |
| --- | --- | --- | --- |
| CSV | `read_csv` | `encoding`, `sep`, `dtype` | 빠름 |
| Excel | `read_excel` | `sheet_name`, `header` | 느림 |
| JSON | `read_json` | `orient`, `lines` | 보통 |
| Parquet | `read_parquet` | `columns` | 매우 빠름 |

CSV는 가장 흔하지만 인코딩 문제가 자주 생깁니다. Parquet는 타입 정보가 포함되어 있고 압축도 되어 있어 효율적이지만, 외부 시스템과의 호환성이 떨어지는 경우가 있습니다.

### 3단계 - 자료형을 명시하기

```python
df = pd.read_csv(
    "sales.csv",
    dtype={"product_id": "string", "qty": "int32"},
    parse_dates=["date"],
)
print(df.dtypes)
```

자료형을 명시하면 메모리를 아끼는 것뿐 아니라, 선행 0이 중요한 식별자나 날짜 열을 안정적으로 다룰 수 있습니다. 읽은 뒤에 고치는 것보다 읽을 때 바로 맞추는 편이 낫습니다.

### 4단계 - Excel 읽기

```python
xls = pd.read_excel("report.xlsx", sheet_name="Q1", header=1)
print(xls.head())
```

Excel은 CSV보다 구조 변형이 많습니다. 시트 이름과 헤더 위치를 명시해 두면 사람이 손으로 만든 파일에서도 훨씬 안정적으로 읽을 수 있습니다.

### 5단계 - 큰 파일은 나눠서 읽기

```python
total = 0
for chunk in pd.read_csv("big.csv", chunksize=100_000):
    total += len(chunk)
print(total)
```

청크 단위 적재는 큰 파일을 통째로 메모리에 올리지 않고도 행 수나 부분 집계를 확인할 수 있게 해 줍니다. 운영 환경에서는 이런 중간 확인이 메모리 사고를 예방합니다.

## 쉼표 구분 파일 읽기 함수 옵션 상세 예제

CSV 파일은 가장 보편적이지만 가장 까다로운 형식이기도 합니다. 다양한 옵션을 알아두면 현장의 대부분 문제를 해결할 수 있습니다.

### 인코딩 명시

```python
df = pd.read_csv("data.csv", encoding="cp949")
```

한국어 데이터는 대부분 UTF-8 또는 CP949로 저장됩니다. 문자가 깨지면 먼저 인코딩을 확인하세요.

### 날짜 열 파싱

```python
df = pd.read_csv(
    "sales.csv",
    parse_dates=["order_date", "ship_date"],
    date_format="%Y-%m-%d",
)
print(df.dtypes)
```

날짜를 문자열로 두면 시계열 연산이 불가능합니다. 읽는 시점에 날짜형으로 변환해 두면 이후 처리가 훨씬 간결해집니다.

### 특정 열만 읽기

```python
df = pd.read_csv("large.csv", usecols=["id", "name", "amount"])
print(df.columns)
```

`usecols`로 필요한 열만 골라 읽으면 메모리와 시간을 크게 줄일 수 있습니다. 특히 수백 개의 열이 있는 파일에서 유용합니다.

**예상 출력:**

```text
1000000
```

메모리에 한 번에 올리기 어려운 파일은 `chunksize`를 기준으로 나눠 읽는 편이 안전합니다. 행 수 계산, 부분 집계, 전처리처럼 순차 처리가 가능한 작업에서 특히 유용합니다.

## 이 코드에서 먼저 봐야 할 점

- 비영어권 데이터에서는 인코딩이 첫 번째 함정입니다.
- 자료형을 명시하면 메모리와 정확도를 함께 잡을 수 있습니다.
- `chunksize`는 메모리 한계를 피하는 표준 패턴입니다.

## 자주 하는 실수 다섯 가지

1. 인코딩을 생략해 글자가 깨진 채로 분석을 시작합니다.
2. 식별자 열을 숫자로 읽어 선행 0을 잃습니다.
3. 날짜를 문자열로 둔 채 나중까지 끌고 갑니다.
4. 헤더 위치가 다른 Excel 파일을 기본값으로 읽습니다.
5. `sheet_name`을 지정하지 않아 첫 시트만 읽고 끝냅니다.

## 실무에서는 이렇게 이어집니다

ERP CSV, 회계 Excel, 외부 기관 데이터처럼 실무 파일은 형식이 늘 일정하지 않습니다. 그래서 팀 단위로는 읽기 옵션을 표준 함수로 감싸 두고, 인코딩과 자료형 설정을 코드에 고정하는 경우가 많습니다.

## 실무에서는 이렇게 생각합니다

- 파일 읽기 코드는 별도 모듈로 분리합니다.
- 자료형은 가능한 한 명시적으로 적습니다.
- `parse_dates` 대상은 항상 검토합니다.
- 큰 파일은 `chunksize`로 메모리를 방어합니다.
- 원본 파일은 손대지 않고 읽기 로직만 조정합니다.

## 실전 예제: 여러 파일 통합

실무에서는 여러 파일을 읽어 하나로 통합하는 작업이 자주 등장합니다.

```python
import glob
files = glob.glob("data/*.csv")
dfs = []
for file in files:
    df = pd.read_csv(file)
    dfs.append(df)
combined = pd.concat(dfs, ignore_index=True)
print(combined.shape)
```

여러 파일을 결합할 때는 열 구조가 동일한지 반드시 확인해야 합니다.

## 오류 처리

파일을 읽다가 오류가 발생하면 전체 파이프라인이 멈춘 수 있습니다. 오류 처리 옵션을 활용하면 더 강건한 코드를 작성할 수 있습니다.

### 라인 오류 건너뛰기

```python
df = pd.read_csv("dirty.csv", on_bad_lines="skip")
print(f"Loaded {len(df)} rows")
```

형식이 맞지 않는 행을 건너뛰고 나머지만 읽을 수 있습니다. 다만 몇 행이 누락되었는지 기록해 두는 편이 좋습니다.

### 인코딩 오류 처리

```python
df = pd.read_csv("data.csv", encoding="utf-8", encoding_errors="ignore")
```

인코딩 오류를 무시하고 계속 읽을 수 있지만, 데이터가 손상될 수 있으므로 주의가 필요합니다. 가능하면 올바른 인코딩을 찾아 명시하는 편이 좋습니다.
## 대용량 파일 처리

메모리에 한 번에 올리기 어려운 파일을 다룰 때는 청크 단위 처리가 필수입니다.

### chunksize로 나눠 읽기

```python
chunk_iter = pd.read_csv("big.csv", chunksize=50000)
for i, chunk in enumerate(chunk_iter):
    print(f"Chunk {i}: {len(chunk)} rows")
    # 각 chunk를 처리
```

각 청크는 독립적인 데이터프레임입니다. 필터링, 집계, 변환 등을 처리한 뒤 결과만 모으면 메모리 부담을 크게 줄일 수 있습니다.

### 부분 집계 예제

```python
total_amount = 0
for chunk in pd.read_csv("sales.csv", chunksize=100000):
    total_amount += chunk["amount"].sum()
print(f"Total: {total_amount}")
```

전체 합계를 구할 때 전체 데이터를 메모리에 올리지 않고도 원하는 결과를 얻을 수 있습니다.

### 메모리 모니터링

```python
df = pd.read_csv("data.csv")
print(df.info(memory_usage="deep"))
```

`info()` 메서드의 `memory_usage` 옵션으로 실제 메모리 사용량을 확인할 수 있습니다. 특히 문자열 열이 많은 경우 메모리가 예상보다 훨씬 크게 잡힐 수 있습니다.

## 체크리스트

- [ ] 인코딩을 항상 검토합니다.
- [ ] 필요한 열의 자료형을 지정합니다.
- [ ] 날짜 열을 읽는 시점에 처리할지 판단합니다.
- [ ] Excel에서는 시트 이름과 헤더 위치를 확인합니다.

## 스트리밍 읽기 패턴

대용량 파일을 처리할 때는 전체를 메모리에 올리지 않고 스트리밍 방식으로 처리하는 것이 안전합니다.

```python
def process_large_csv(filename):
    result = []
    for chunk in pd.read_csv(filename, chunksize=100000):
        # 필터링
        filtered = chunk[chunk["amount"] > 100]
        # 집계
        summary = filtered.groupby("category")["amount"].sum()
        result.append(summary)
    return pd.concat(result).groupby(level=0).sum()

total = process_large_csv("sales.csv")
print(total)
```

이 패턴은 메모리 한계를 넘는 데이터를 다룰 때 표준적으로 사용됩니다.

### 데이터 검증

파일을 읽은 직후에는 항상 검증 단계를 거쳐야 합니다.

```python
def validate_dataframe(df, expected_columns, expected_dtypes):
    assert set(df.columns) == set(expected_columns), "Column mismatch"
    for col, dtype in expected_dtypes.items():
        assert df[col].dtype == dtype, f"{col} dtype mismatch"
    return True

df = pd.read_csv("data.csv")
validate_dataframe(df, ["id", "name", "amount"], {"id": "int64", "amount": "float64"})
```

## 압축 파일 읽기

Pandas는 압축된 파일도 직접 읽을 수 있습니다.

```python
# gzip
df = pd.read_csv("data.csv.gz", compression="gzip")

# zip
df = pd.read_csv("data.zip")

# 자동 감지
df = pd.read_csv("data.csv.bz2", compression="infer")
```

압축 파일은 디스크 공간을 절약하면서도 직접 읽을 수 있어 편리합니다.

압축 파일을 사용하면 네트워크 전송 시간도 줄일 수 있어 클라우드 환경에서 특히 유용합니다.

Pandas는 `.csv.gz`, `.csv.zip` 같은 압축 파일도 자동으로 인식해 읽을 수 있습니다. 스토리지를 아끼고 전송 시간을 줄이는 데 유용합니다.

## 연습 문제

1. UTF-8이 아닌 CSV를 읽고 자료형을 출력해 보세요.
2. `parse_dates` 유무에 따라 출력 자료형이 어떻게 달라지는지 비교해 보세요.
3. `chunksize`를 이용해 행 수를 세는 함수를 작성해 보세요.

## 정리와 다음 글

좋은 분석은 대개 좋은 적재에서 시작합니다. 파일을 읽는 순간부터 데이터 계약을 의식하면 뒤의 정제와 해석이 훨씬 단단해집니다. 다음 글에서는 읽어 온 표에서 필요한 행과 열을 고르는 방법을 다루겠습니다.

## 처음 질문으로 돌아가기

- **`read_csv`와 `read_excel`에서 가장 먼저 봐야 할 옵션은 무엇일까요?**
  - 본문의 기준은 CSV와 Excel 읽기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **문자 인코딩과 구분자는 왜 자주 문제를 일으킬까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **자료형을 명시하면 어떤 이점이 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Pandas 101 (1/10): Pandas란 무엇인가?](./01-what-is-pandas.md)
- [Pandas 101 (2/10): 시리즈와 데이터프레임](./02-series-and-dataframe.md)
- **CSV와 Excel 읽기 (현재 글)**
- 필터링과 선택 (예정)
- 결측치 처리 (예정)
- 그룹화와 집계 (예정)
- 병합과 조인 (예정)
- 시계열 데이터 다루기 (예정)
- 적용 함수와 벡터화 (예정)
- 실전 데이터 분석 (예정)

<!-- toc:end -->

## 참고 자료

- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas — read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas — IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Real Python — Reading and Writing CSV Files](https://realpython.com/python-csv/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/pandas-101/ko)

Tags: Pandas, CSV, Excel, DataAnalysis, Beginner
