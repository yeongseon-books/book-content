---
title: Row factory와 type adapter (sqlite3, PEP 249)
series: python-dbapi-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  hashnode: true
  medium: true
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

# Row factory와 type adapter (sqlite3, PEP 249)

`row[3]` 같은 코드는 스키마가 바뀌는 순간 조용히 깨집니다. 이 글에서는 row factory와 type adapter를 함께 다뤄 결과 shape와 값 변환을 한 곳에서 통제하는 방법을 설명합니다.

이 글은 Python DB-API 101 시리즈의 여섯 번째 글입니다.

![Row factory와 type adapter (sqlite3, PEP 249)](../../../assets/python-dbapi-101/06/06-01-row-factories-and-type-adapters-sqlite3.en.png)

*Row factory와 type adapter (sqlite3, PEP 249)*

## 이 글에서 다룰 문제

`row[3]`처럼 인덱스로 컬럼을 꺼내는 코드는 schema가 바뀌는 순간 침묵 속에 깨집니다. `row['name']`처럼 이름으로 꺼내거나, `row.name` 형태의 dataclass를 쓰면 schema 변경이 import error로 즉시 드러납니다.

타입 변환도 마찬가지입니다. SQLite에 금액을 `REAL`(float)로 저장하면 0.1 + 0.2 = 0.30000000000000004 같은 정밀도 사고가 발생합니다. `Decimal`을 등록하고 `TEXT`로 저장하면 정확도를 유지할 수 있습니다.

이 글은 row factory와 type adapter를 한 번에 정리해, repository 레이어가 schema/타입 변경에 견디게 만드는 방법을 코드로 보여 줍니다.

---

## Mental Model — 두 단계 변환

![Mental Model - 두 단계 변환](../../../assets/python-dbapi-101/06/06-02-mental-model-two-step-conversion.en.png)

*Mental Model - 두 단계 변환*
```'
---

# Row factories and type adapters (sqlite3, PEP 249)

Tuple-shaped rows are fast, but they turn schema changes and type drift into subtle bugs. This post shows how row factories and adapters let you centralize both result shape and value conversion before the repository layer gets messy.

This is the 6th article in the Python DB-API 101 series.

![Row factories and type adapters (sqlite3, PEP 249)](../../../assets/python-dbapi-101/06/06-01-row-factories-and-type-adapters-sqlite3.en.png)

*Row factories and type adapters (sqlite3, PEP 249)*
## Questions this post answers

- How do you receive default tuple results as dict, dataclass, or Pydantic models?
- What is `sqlite3.Row` and when is it enough?
- What does `detect_types` actually detect?
- How do you safely map custom types such as `Decimal`, `datetime`, `Enum`, or JSON?
- How do adapters and converters fit into the PEP 249 model?

> Raw tuples returned by the database are fast but dangerous: you must remember column order, and SQLite has only five storage classes (NULL, INTEGER, REAL, TEXT, BLOB). Row factories and type adapters consolidate every conversion in one place.

## What you will learn

This post separates how sqlite3 moves data between SQL and Python into two axes.

1. **Row factory** — the **shape** of `cursor.fetch*()` results (tuple → Row → dict → dataclass → Pydantic).
2. **Type adapter / converter** — the **type of a single value** (Python `Decimal` ↔ SQLite TEXT).
3. **`detect_types`** — selects automatic conversion based on declared column type or `[type-name]` column aliases.
4. **Registering custom types** — `register_adapter` / `register_converter` for `Decimal`, `Enum`, JSON dicts.
5. **Type-safe repository layer** — using Pydantic or dataclass as the result model.

---

## Why this matters

Code like `row[3]` shatters silently the moment the schema changes. `row['name']` (or `row.name` from a dataclass) turns schema changes into immediate import errors.

The same applies to type conversion. Storing money as `REAL` (float) in SQLite leads to precision incidents like `0.1 + 0.2 = 0.30000000000000004`. Registering `Decimal` and storing as `TEXT` keeps full precision.

This post unifies row factories and type adapters so your repository layer survives schema and type changes.

---

## Mental Model — two-step conversion

![Mental model - two-step conversion](../../../assets/python-dbapi-101/06/06-02-mental-model-two-step-conversion.en.png)

*Mental model - two-step conversion*
```

- **adapter / converter** = **단일 값**의 타입 변환 (Python ↔ SQLite storage class).
- **row_factory** = **행 전체**의 shape 변환 (tuple → 원하는 형태).

이 둘을 분리해서 이해하면 코드 위치도 자연히 분리됩니다.

---

## 핵심 개념

![핵심 개념](../../../assets/python-dbapi-101/06/06-03-core-concepts.en.png)

*핵심 개념*
### `sqlite3.Row`

가장 가벼운 row factory. tuple처럼 인덱스로도, dict처럼 이름으로도 접근됩니다.

```

- **adapter / converter** = type conversion of a **single value** (Python ↔ SQLite storage class).
- **row_factory** = shape conversion of an **entire row** (tuple → desired form).

Separating these two concerns naturally separates where they live in code.

---

## Core concepts

![Core concepts](../../../assets/python-dbapi-101/06/06-03-core-concepts.en.png)

*Core concepts*
### `sqlite3.Row`

The lightest row factory. Accessible by index like a tuple AND by name like a dict.

```

dict는 아니지만 80% 케이스에 충분합니다.

### dict factory

진짜 dict가 필요하면:

```

It is not a real dict, but it covers ~80% of cases.

### dict factory

For a true dict:

```

### dataclass factory

타입 안전성과 IDE 자동완성을 원하면:

```

### dataclass factory

For type safety and IDE autocomplete:

```

### Pydantic factory

검증과 직렬화가 함께 필요하면:

```

### Pydantic factory

For combined validation and serialisation:

```

### `detect_types`

```

### `detect_types`

```

- `PARSE_DECLTYPES` — `CREATE TABLE`의 컬럼 declared type(예: `created_at TIMESTAMP`)을 보고 등록된 converter 호출.
- `PARSE_COLNAMES` — `SELECT created_at AS "ts [timestamp]"`처럼 컬럼 별칭에 `[type-name]`을 붙여 강제 변환.

---

## Before / After

### Before — raw tuple + 컬럼 인덱스

```

- `PARSE_DECLTYPES` — looks at the column's declared type from `CREATE TABLE` (e.g., `created_at TIMESTAMP`) and dispatches the registered converter.
- `PARSE_COLNAMES` — forces conversion via aliases like `SELECT created_at AS "ts [timestamp]"`.

---

## Before / After

### Before — raw tuple + column index

```

`SELECT` 컬럼 순서가 바뀌면 가격이 갑자기 name으로 곱해집니다.

### After — Pydantic + Decimal converter

```

If the SELECT column order changes, you suddenly multiply the name string.

### After — Pydantic + Decimal converter

```

컬럼 순서가 바뀌어도 안전하고, 가격은 `Decimal`로 정확합니다.

---

## 단계별 실습

![단계별 실습](../../../assets/python-dbapi-101/06/06-04-step-by-step-walkthrough.en.png)

*단계별 실습*
### 단계 1 — `sqlite3.Row`

```

Order-independent and precise.

---

## Step-by-step walkthrough

![Step-by-step walkthrough](../../../assets/python-dbapi-101/06/06-04-step-by-step-walkthrough.en.png)

*Step-by-step walkthrough*
### Step 1 — `sqlite3.Row`

```

### 단계 2 — `Decimal` adapter/converter

```

### Step 2 — `Decimal` adapter / converter

```

### 단계 3 — `Enum` adapter

```

### Step 3 — `Enum` adapter

```

### 단계 4 — JSON adapter

```

### Step 4 — JSON adapter

```

### 단계 5 — `[type-name]` 컬럼 별칭

declared type을 못 쓰는 view나 임시 컬럼에서는 SELECT 별칭으로 강제할 수 있습니다.

```

### Step 5 — `[type-name]` column aliases

For views or computed columns where declared type is unavailable, force conversion via aliases.

```

### 단계 6 — Pydantic + adapter 통합

```

### Step 6 — Pydantic + adapters together

```

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

```

The repository now deals only in `Order` objects; SQLite storage classes never leak outward.

---

## Common mistakes

1. **Direct column-index access.** `row[0]`, `row[2]` are fragile across schema changes. Start with at least `sqlite3.Row`.
2. **Storing money as `REAL`.** Float precision incidents follow. Always use `Decimal` + `TEXT`, or `INTEGER` (cents).
3. **Forgetting `detect_types`.** You register the adapter, but the converter never fires — and you wonder why bytes come back. Enable `PARSE_DECLTYPES`.
4. **Converters always receive `bytes`, not `str`.** Do not forget `b.decode()`.
5. **Adapter must return one of SQLite's five storage classes** — `int`, `float`, `str`, `bytes`, or `None`. Returning a custom object raises.
6. **Timestamp clashes.** Python 3.12 deprecated the default timestamp converter. Be explicit with your own converter.
7. **Assuming `dict_factory` is fast.** Each row builds a dict via comprehension. For million-row workloads, `sqlite3.Row` (C-implemented) is much faster.
8. **Setting `row_factory` only on the cursor, not the connection.** Set it on the connection — every cursor inherits.

---

## Production application

### Repository layer pattern

```

호출자는 dict 키 오타나 컬럼 순서를 신경 쓸 필요가 없습니다.

### 마이그레이션과 타입

`Decimal`을 도입하면 기존 `REAL` 컬럼을 `TEXT`로 바꿔야 합니다. 이때는 다음 글의 transaction 관리와 함께 `BEGIN IMMEDIATE → ALTER TABLE → 데이터 변환 → COMMIT` 순서로 적용합니다.

### 컬럼 별칭으로 view 처리

view나 join 결과는 declared type이 사라집니다. 별칭에 `[type-name]`을 붙이는 패턴을 운영에서 자주 씁니다.

```

Callers no longer need to remember dict keys or column order.

### Migration and types

Adopting `Decimal` requires migrating `REAL` columns to `TEXT`. Wrap it in `BEGIN IMMEDIATE → ALTER TABLE → data conversion → COMMIT` together with the transaction patterns from the previous post.

### Handling views with column aliases

Views and join results lose declared types. The `[type-name]` alias pattern is widely used in production.

```

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

<!-- toc:begin -->
## 시리즈 목차

- [왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [execute, executemany, fetch 패턴](./03-execute-fetch-patterns.md)
- [Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- [Transaction과 isolation level (sqlite3, PEP 249)](./05-transactions-isolation.md)
- **Row factory와 type adapter (sqlite3, PEP 249) (현재 글)**
- PEP 249 예외 계층과 SQLite 에러 처리 (예정)
- SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 (예정)
- aiosqlite로 비동기 SQLite 다루기 (예정)
- SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 — Row objects](https://docs.python.org/3/library/sqlite3.html#row-objects)
- [Python sqlite3 — Adapters and converters](https://docs.python.org/3/library/sqlite3.html#sqlite3-adapter-converter-recipes)
- [SQLite — Datatypes In SQLite](https://www.sqlite.org/datatype3.html)
- [Pydantic — Models](https://docs.pydantic.dev/latest/concepts/models/)

Tags: Python, DB-API, PEP 249, Database
