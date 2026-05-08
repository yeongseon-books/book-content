
# CSV와 Excel 읽기

> Pandas 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *데이터를 잘 읽는 것* 은 *분석의 절반* 일까요?

> *나쁜 적재는 *나쁜 분석* 의 시작입니다. read_csv 옵션을 *처음부터 정확히* 잡으세요.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *read_csv* 와 *read_excel* 의 *핵심 옵션*
- *인코딩* 과 *구분자* 처리
- *dtype* 명시의 가치
- 5단계 적재 실습
- 흔한 함정 5가지

## 왜 중요한가

분석의 *80%* 는 *적재와 정제* 입니다. *적재 단계의 실수* 는 *나중에 디버깅 비용* 으로 돌아옵니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    File["CSV / Excel"] --> Read["read_csv / read_excel"]
    Read --> Check["dtypes / shape / head"]
    Check --> Fix["fix encoding / dtype / header"]
```

## 핵심 용어 정리

- **encoding**: 파일의 *문자 인코딩* (utf-8, cp949, euc-kr).
- **sep**: *구분자* — 콤마, 탭, 세미콜론.
- **header**: *헤더 행 위치* — 0이 기본, None이면 헤더 없음.
- **dtype**: *열별 타입 명시* — 메모리·정확도 향상.
- **parse_dates**: *날짜 열* 자동 파싱.

## Before/After

**Before**: *“그냥 read_csv”* — 한글 깨짐, 숫자가 문자열로.

**After**: *“encoding, dtype, parse_dates 명시”* — *데이터가 의도대로* 들어옴.

## 실습: 5단계 적재 실습

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
- *dtype* 명시로 *메모리* 와 *타입 안정성* 을 잡습니다.
- *chunksize* 는 *메모리 한계* 를 회피하는 표준 패턴.

## 자주 하는 실수 5가지

1. ***인코딩 미지정* 으로 한글 깨짐.**
2. ***ID 열* 을 숫자로 읽어 *0이 사라짐*.**
3. ***날짜를 문자열로 둠.** parse_dates를 안 씀.**
4. ***헤더 위치* 가 다른 Excel을 그대로 읽음.**
5. ***sheet_name* 미지정으로 *첫 시트만* 읽음.**

## 실무에서는 이렇게 쓰입니다

ERP 추출 CSV, 회계 Excel, 외부 API의 CSV 응답 — *제대로 읽기* 위해 *옵션 5–10개* 를 *고정 패턴* 으로 잡아둡니다. 적재 함수는 *재사용 가능한 모듈* 로 분리합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *적재 함수* 를 *별도 모듈* 로 만든다.
- *dtype* 을 *명시적으로* 지정한다.
- *parse_dates* 를 *항상 검토* 한다.
- *chunksize* 로 *메모리 가드* 한다.
- *원본 파일* 은 *원본 그대로* 보관한다.

## 체크리스트

- [ ] *encoding* 을 *항상 명시* 한다.
- [ ] *dtype* 을 *지정* 한다.
- [ ] *parse_dates* 를 *검토* 한다.
- [ ] *Excel sheet_name* 을 *명시* 한다.

## 연습 문제

1. *cp949* 로 저장된 *한글 CSV* 를 읽고 *dtype* 을 출력하세요.
2. *parse_dates* 를 *안 줄 때* 와 *줄 때* 의 *dtype 차이* 를 비교하세요.
3. *chunksize* 로 *행 수* 를 세는 함수를 작성하세요.

## 정리 및 다음 단계

좋은 적재가 *좋은 분석의 출발점* 입니다. 다음 글에서는 *filtering과 selection* 을 다룹니다.

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
## 참고 자료

- [pandas — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [pandas — read_excel](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [pandas — IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Real Python — Reading and Writing CSV Files](https://realpython.com/python-csv/)

Tags: Pandas, CSV, Excel, DataAnalysis, Beginner

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
