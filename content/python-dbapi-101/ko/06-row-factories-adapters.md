---
title: "Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249)"
series: python-dbapi-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  hashnode: false
  medium: false
  mkdocs: true
  ebook: true
tags:
- Python
- SQLite
- Row Factory
- Type Adapter
- Pydantic
- PEP 249
last_reviewed: '2026-05-12'
seo_title: Row factory와 type adapter
seo_description: '[col1, col2, col3] row_factory │ ─────────────► {''id'': 1, ''name'':
  ''Alice''} ▼…'
---

# Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249)

`row[3]` 같은 코드는 스키마가 바뀌는 순간 조용히 깨집니다. 이 글에서는 row factory와 type adapter를 함께 다뤄 결과 shape와 값 변환을 한 곳에서 통제하는 방법을 설명합니다.

이 글은 Python DB-API 101 시리즈의 여섯 번째 글입니다.

![Row factory와 type adapter (sqlite3, PEP 249)](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/06/06-01-row-factories-and-type-adapters-sqlite3.ko.png)

*Row factory와 type adapter (sqlite3, PEP 249)*

![Python DB-API 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/06/06-02-mental-model-two-step-conversion.ko.png)
*Python DB-API 101 6장 흐름 개요*

## 먼저 던지는 질문

- Row factory와 type adapter (sqlite3, PEP 249)를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- Row factory와 type adapter (sqlite3, PEP 249)에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- Row factory와 type adapter (sqlite3, PEP 249)를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## Mental Model — 두 단계 변환

> SQLite에서 Python으로 값이 넘어올 때는 먼저 **값 단위 타입 변환**이 일어나고, 그다음에 **행 단위 shape 변환**이 일어납니다. 이 순서를 분리해서 보면 adapter/converter와 row factory를 어디에 둘지 명확해집니다.

- **adapter / converter** = **단일 값**의 타입 변환 (Python ↔ SQLite storage class).
- **row_factory** = **행 전체**의 shape 변환 (tuple → 원하는 형태).

이 둘을 분리해서 이해하면 코드 위치도 자연히 분리됩니다.

---

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/06/06-03-core-concepts.ko.png)

*핵심 개념*
### `sqlite3.Row`

가장 가벼운 row factory. tuple처럼 인덱스로도, dict처럼 이름으로도 접근됩니다.

```python
con.row_factory = sqlite3.Row
row = con.execute('SELECT id, name FROM users WHERE id=?', (1,)).fetchone()
print(row[0], row['name'], row.keys())
```

dict는 아니지만 80% 케이스에 충분합니다.

### dict 팩토리

진짜 dict가 필요하면:

### dataclass 팩토리

타입 안전성과 IDE 자동완성을 원하면:

### Pydantic 팩토리

검증과 직렬화가 함께 필요하면:

### `detect_types`

자동 변환은 connection을 열 때 `detect_types` 플래그로 켭니다.

- `PARSE_DECLTYPES` — `CREATE TABLE`의 컬럼 declared type(예: `created_at TIMESTAMP`)을 보고 등록된 converter 호출.
- `PARSE_COLNAMES` — `SELECT created_at AS "ts [timestamp]"`처럼 컬럼 별칭에 `[type-name]`을 붙여 강제 변환.

---

## 적용 전후 비교
### Before — raw tuple + 컬럼 인덱스

`SELECT` 컬럼 순서가 바뀌면 가격이 갑자기 name으로 곱해집니다.

### 적용 후 — Pydantic + Decimal 변환기

컬럼 순서가 바뀌어도 안전하고, 가격은 `Decimal`로 정확합니다.

---

## 단계별 실습

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/06/06-04-step-by-step-walkthrough.ko.png)

*단계별 실습*
### 단계 1 — `sqlite3.Row`

컬럼 이름 기반 접근을 도입하는 가장 가벼운 출발점입니다.

### 단계 2 — `Decimal` 어댑터/컨버터
금액과 정밀 수치를 float 대신 `Decimal`로 정확하게 왕복시킵니다.

### 단계 3 — `Enum` 어댑터
문자열 코드 대신 도메인 enum을 바로 받게 만들 수 있습니다.

### 단계 4 — JSON 어댑터
JSON 문자열을 애플리케이션 dict로 복원해 repository 밖으로 새지 않게 합니다.

### 단계 5 — `[type-name]` 컬럼 별칭

선언된 타입을 쓸 수 없는 view나 임시 컬럼에서는 SELECT 별칭으로 강제할 수 있습니다.

### 단계 6 — Pydantic + adapter 통합

행 shape와 값 변환을 함께 묶으면 repository는 도메인 모델만 다루게 됩니다.

이제 repository는 `Order` 객체만 다루며, SQLite의 storage class는 외부에 새지 않습니다.

---

## 자주 하는 실수

1. **컬럼 인덱스 직접 접근** — `row[0]`, `row[2]`는 schema 변경에 매우 취약합니다. 최소 `sqlite3.Row`로 시작하세요.
2. **`REAL`로 금액 저장** — float 정밀도 사고. 항상 `Decimal` + `TEXT` 또는 `INTEGER`(센트 단위) 사용.
3. **`detect_types` 누락** — adapter는 등록했는데 converter가 안 불려서 "왜 그대로 bytes로 나오지?" 함정. `PARSE_DECLTYPES`를 켜야 합니다.
4. **converter는 항상 `bytes` 입력** — `str`이 아닙니다. `b.decode()`를 잊지 마세요.
5. **adapter는 SQLite storage class 5종으로만 반환** — `int`, `float`, `str`, `bytes`, `None`. 새 객체를 그대로 반환하면 에러.
6. **timestamp 충돌** — Python 3.12부터 default timestamp converter가 deprecated. 사용자 정의 converter로 명시하는 것이 안전합니다.
7. **dict_factory 성능 가정** — 매 row마다 dict comprehension. 초당 100만 row 같은 워크로드라면 `sqlite3.Row`(C 구현)가 훨씬 빠릅니다.
8. **row_factory를 cursor에만 설정하고 connection에 안 함** — `con.row_factory = ...`로 connection에 두면 모든 cursor가 상속받습니다.

---

## 실무 적용

### Repository 레이어 패턴

호출자는 dict 키 오타나 컬럼 순서를 기억할 필요 없이, 도메인 모델만 받아서 쓰면 됩니다.

### 마이그레이션과 타입

`Decimal`을 도입하면 기존 `REAL` 컬럼을 `TEXT`로 바꿔야 합니다. 이때는 다음 글의 transaction 관리와 함께 `BEGIN IMMEDIATE → ALTER TABLE → 데이터 변환 → COMMIT` 순서로 적용합니다.

### 컬럼 별칭으로 view 처리

view나 join 결과는 선언된 타입 정보가 사라집니다. 별칭에 `[type-name]`을 붙이는 패턴을 운영에서 자주 씁니다.

### 성능 vs 안전 균형

- 보고서/배치: `sqlite3.Row`로 충분 (C 구현, 빠름).
- API 핸들러: dataclass/Pydantic (검증·직렬화 결합).
- 핫 루프: tuple + 명시적 unpack `for id, name in cur:`도 정당. 단, 함수 1~2개로 한정.

---

## 체크리스트

- [ ] connection 생성 시 `row_factory`를 명시적으로 설정한다.
- [ ] 인덱스로 컬럼을 꺼내는 코드는 hot path 외에는 사용하지 않는다.
- [ ] 금액·정밀 수치는 `Decimal` adapter + `TEXT` 컬럼 또는 `INTEGER`(소수점 환산).
- [ ] adapter/converter를 사용할 때 `detect_types=PARSE_DECLTYPES`를 켠다.
- [ ] view/join 결과에는 `SELECT col AS "x [type]"` 별칭으로 converter를 강제한다.
- [ ] `Enum`, `JSON`, `Decimal`, `datetime` 같은 도메인 타입은 한 번만 등록하고 모듈 import 시 자동 적용한다.
- [ ] Repository 레이어가 외부에 SQLite storage class를 노출하지 않는다.

---

## 정리
row factory는 **shape**, adapter/converter는 **value**를 다룬다는 두 축만 분리하면 sqlite3의 데이터 변환은 단순해집니다. Repository 레이어를 Pydantic 모델 위에 올려 두면 schema 변경이 import error로 잡히고, 도메인 타입(`Decimal`, `Enum`, JSON)이 안전하게 흐릅니다.

다음 글에서는 **error handling과 exception hierarchy**를 다룹니다. PEP 249가 정의한 8개 예외 클래스, sqlite3의 매핑(IntegrityError, OperationalError, ProgrammingError 등), `BUSY`와 `LOCKED`의 차이, 그리고 retry 전략을 코드로 정리합니다.

## 실전 패턴 추가: connection/cursor/transaction 경계를 명시하는 운영 코드

DB-API 코드는 SQL 문장보다 경계 관리가 더 중요합니다. 연결 수명, 커서 재사용 범위, 커밋/롤백 시점을 코드로 드러내야 장애 시 복구가 쉬워집니다.

```python
import sqlite3
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def db_connection(path: str) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(path, timeout=5.0)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def transfer(conn: sqlite3.Connection, sender: int, receiver: int, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")

    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender))
    cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, receiver))

def list_recent(conn: sqlite3.Connection, limit: int = 100) -> list[tuple[int, int, int]]:
    cur = conn.cursor()
    cur.execute(
        "SELECT sender_id, receiver_id, amount FROM transfers ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return cur.fetchall()
```

이 패턴은 세 가지를 보장합니다. 첫째, 트랜잭션 성공/실패 경계를 컨텍스트 매니저 한 곳에서 통제합니다. 둘째, `execute` 파라미터 바인딩을 강제해 SQL 인젝션 리스크를 줄입니다. 셋째, 읽기/쓰기 함수를 분리해 장애 분석 시 어떤 쿼리가 상태를 바꿨는지 추적이 쉬워집니다. 소규모 서비스라도 이 구조를 일찍 도입하면 운영 중 데이터 정합성 이슈를 크게 줄일 수 있습니다.

## 추가 실무 메모: 트랜잭션 로그를 남기는 기준

쓰기 작업은 SQL 자체보다 실패 맥락을 남기는 편이 중요합니다. `order_id`, 영향 row 수, 예외 타입을 같은 로그 라인에 남기면 재시도 정책을 설계할 때 근거가 생깁니다. DB-API에서는 `except` 블록에서 롤백 후 재상승시키는 패턴을 기본값으로 두는 편이 안전합니다.

## 심화 앵커: 타입 변환 규칙 중앙화 템플릿

row factory와 converter를 파일마다 다르게 두면 데이터 모양이 흔들립니다. connection 팩토리에서 한 번에 등록하는 방식이 유지보수에 유리합니다.

```python
import sqlite3
from decimal import Decimal

sqlite3.register_adapter(Decimal, lambda v: format(v, "f"))
sqlite3.register_converter("DECIMAL", lambda b: Decimal(b.decode()))

conn = sqlite3.connect(
    "app.db",
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
)
conn.row_factory = sqlite3.Row
```

| row 방식 | 장점 | 단점 |
| --- | --- | --- |
| tuple | 빠름 | 컬럼 순서 의존 |
| `sqlite3.Row` | 이름 접근 가능 | dict 변환 추가 필요 |
| dataclass/Pydantic | 타입 검증 | 변환 비용 증가 |

row shape와 값 타입 변환을 분리하면 스키마 변경 시 장애 반경을 빠르게 줄일 수 있습니다.

## 추가 심화 노트: 운영 품질 게이트

아래 항목은 개발 환경에서는 자주 생략되지만, 운영에서는 장애 예방에 직접 영향을 줍니다.

### A. 배포 전 검증 스크립트 예시

```bash
python -m pytest tests/test_dbapi_contract.py -q
python scripts/check_sql_bindings.py
python scripts/check_transaction_boundaries.py
```

### B. 계약 테스트 예시

```python
def test_dbapi_contract(conn):
    cur = conn.cursor()
    cur.execute("SELECT 1")
    assert cur.fetchone()[0] == 1
    cur.close()
```

### C. 관측성 필드 표준

| 필드 | 설명 |
| --- | --- |
| `db.driver` | sqlite3 / psycopg2 |
| `db.operation` | SELECT/INSERT/UPDATE/DELETE |
| `db.retry.count` | 재시도 횟수 |
| `db.elapsed_ms` | 실행 시간 |
| `db.tx.state` | commit/rollback |

### D. 성능 측정 루틴

```python
import time

def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    v = fn(*args, **kwargs)
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"metric=db.elapsed_ms value={elapsed:.1f}")
    return v
```

### E. 장애 대응 기본 규칙

- `IntegrityError`: 재시도하지 않고 입력/업무 규칙 오류로 처리합니다.
- `OperationalError`의 BUSY/LOCKED 계열: 짧은 백오프 재시도를 적용합니다.
- `ProgrammingError`: 코드 수정 대상이므로 즉시 알림합니다.
- `DatabaseError`의 손상 징후: 복구 런북으로 전환합니다.

이 노트는 새로운 개념을 추가하기보다, 본문의 원칙을 운영 절차로 고정하는 데 목적이 있습니다.

## 최종 보강: 실무 FAQ

### Q1. 왜 작은 프로젝트에서도 DB-API 경계를 엄격히 지켜야 하나요?

초기에는 코드량이 작아 보이지만, 운영 장애는 대부분 경계가 모호한 코드에서 시작됩니다. connect/execute/commit/close 경계를 명시하면 장애 원인을 단계별로 좁힐 수 있습니다.

### Q2. SQLite와 PostgreSQL을 함께 고려할 때 가장 먼저 맞춰야 할 것은 무엇인가요?

파라미터 바인딩 규칙과 트랜잭션 종료 규칙입니다. paramstyle 차이(`?` vs `%s`)는 어댑터로 흡수하고, 커밋/롤백 시점은 애플리케이션 레벨에서 동일하게 고정해야 합니다.

### Q3. 성능보다 먼저 챙겨야 할 지표는 무엇인가요?

`db.elapsed_ms`, `db.retry.count`, `db.busy_rate`, `db.tx.rollback.count` 네 가지입니다. 이 네 지표만 있어도 병목과 실패 패턴을 빠르게 분리할 수 있습니다.

### Q4. 운영 중 가장 자주 반복되는 실수는 무엇인가요?

- 예외를 `except Exception`으로 한 번에 처리해 재시도 가능/불가를 구분하지 않는 실수
- 문자열 결합 SQL이 테스트 없이 섞여 들어가는 실수
- 트랜잭션 경계를 함수 밖으로 흘려 보내는 실수
- 백업 성공 여부만 보고 복구 리허설을 생략하는 실수

### Q5. 팀 단위로 품질을 유지하려면 어떤 합의가 필요하나요?

코드 스타일 합의보다 더 중요한 것은 실패 처리 합의입니다. 어떤 예외를 retry할지, 어떤 예외를 즉시 실패로 처리할지, 어떤 로그 필드를 남길지를 문서와 테스트로 고정해야 합니다.

## 보충 메모: 릴리스 전 점검

릴리스 직전에는 코드 품질보다 운영 안전성을 먼저 점검합니다.

- 트랜잭션이 열리는 함수마다 commit/rollback 경로가 모두 존재하는지 확인합니다.
- cursor가 함수 경계를 넘어 누수되지 않는지 확인합니다.
- 예외 분기에서 retry 가능한 코드와 불가능한 코드를 분리했는지 확인합니다.
- 관측 로그에 최소 필드(`db.operation`, `db.elapsed_ms`, `db.tx.state`)가 남는지 확인합니다.

짧은 점검이지만 장애를 크게 줄이는 효과가 있습니다.

## 처음 질문으로 돌아가기

- **Row factory와 type adapter (sqlite3, PEP 249)를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 Row factory와 type adapter (sqlite3, PEP 249)를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Row factory와 type adapter (sqlite3, PEP 249)에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Row factory와 type adapter (sqlite3, PEP 249)를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Python DB-API 101 (2/10): Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [Python DB-API 101 (3/10): execute, executemany, fetch 패턴](./03-execute-fetch-patterns.md)
- [Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- [Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249)](./05-transactions-isolation.md)
- **Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249) (현재 글)**
- Python DB-API 101 (7/10): PEP 249 예외 계층과 SQLite 에러 처리 (예정)
- Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 (예정)
- Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기 (예정)
- Python DB-API 101 (10/10): SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 — Row objects](https://docs.python.org/3/library/sqlite3.html#row-objects)
- [Python sqlite3 — Adapters and converters](https://docs.python.org/3/library/sqlite3.html#sqlite3-adapter-converter-recipes)
- [SQLite — Datatypes In SQLite](https://www.sqlite.org/datatype3.html)
- [Pydantic — Models](https://docs.pydantic.dev/latest/concepts/models/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-dbapi-101/ko)

Tags: Python, DB-API, PEP 249, Database
