---
title: '데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기'
series: alembic-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- Alembic
- data-migration
- op.execute
- batch
- SQLite
last_reviewed: '2026-05-03'
seo_description: 데이터 마이그레이션은 "schema는 그대로 두고 row를 변환하는 revision"입니다.
---

# 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기

## 핵심 질문

스키마와 함께 데이터를 옮겨야 할 때 안전하게 수행하려면 어떻게 분리해야 할까요?

이 글은 그 질문에 답하기 위해 데이터 마이그레이션의 핵심 결정과 실무 함정을 살펴봅니다.


## 이 글에서 다룰 문제

`ALTER TABLE`만 마이그레이션이 아닙니다. column rename, enum 값 변경, JSON 구조 변환 같은 작업은 schema와 함께 데이터도 변경해야 합니다. 데이터 마이그레이션을 schema와 같은 revision에 섞으면 큰 데이터셋에서 lock 문제와 timeout이 발생하고, downgrade가 사실상 불가능해집니다.

## Mental Model

> 데이터 마이그레이션은 **"schema는 그대로 두고 row를 변환하는 revision"**입니다. schema-only revision과 분리하면 (1) 큰 트랜잭션을 작은 batch로 쪼갤 수 있고, (2) 실패 시 schema 부분은 살리고 데이터 부분만 재실행할 수 있고, (3) 리뷰어가 의도를 분명하게 읽을 수 있습니다.

git에 비유하면 schema 변경은 코드 리팩터링, 데이터 변경은 데이터베이스 마이그레이션 스크립트입니다. 한 commit에 섞으면 history가 흐려집니다.

## 핵심 개념

### `op.execute` 두 가지 스타일

**raw SQL 방식**

```python
def upgrade() -> None:
    op.execute("UPDATE users SET tier = 'free' WHERE tier IS NULL")
```

빠르고 단순하지만 dialect 의존이 있고 IDE의 도움을 받기 어렵습니다.

**SQLAlchemy core 방식**

```python
from sqlalchemy import table, column, String

def upgrade() -> None:
    users = table("users", column("tier", String))
    op.execute(
        users.update()
        .where(users.c.tier.is_(None))
        .values(tier="free")
    )
```

조금 길지만 dialect-agnostic이고, 변환 로직이 복잡할 때 안전합니다. **주의**: 마이그레이션에서는 `Base.metadata`의 모델을 import하지 않습니다. 모델이 미래에 바뀌면 과거 마이그레이션이 깨지기 때문입니다. 위처럼 `table()`/`column()`로 inline schema를 만들어 그 시점의 schema만 표현합니다.

### batch 단위 처리

수백만 row를 한 번에 UPDATE하면 lock과 트랜잭션 로그가 폭발합니다. SQLite에서는 동시성 문제가, PostgreSQL/MySQL에서는 다른 트랜잭션 차단이 발생합니다.

```python
def upgrade() -> None:
    bind = op.get_bind()
    batch_size = 1000
    while True:
        result = bind.execute(text(
            "UPDATE users SET tier = 'free' "
            "WHERE id IN (SELECT id FROM users WHERE tier IS NULL LIMIT :n)"
        ), {"n": batch_size})
        if result.rowcount == 0:
            break
```

루프 안에서 commit을 명시적으로 끊어 주면 더 안전합니다. SQLite는 단일 writer이므로 큰 트랜잭션이 다른 작업을 막는 시간이 줄어듭니다.

### schema/data revision 분리

세 단계로 나누는 것이 정석입니다.

1. **schema add**: `nullable=True`로 새 컬럼/테이블 추가 (빠름).
2. **data backfill**: 기존 row를 채우는 데이터 마이그레이션 (느림, batch).
3. **schema tighten**: `nullable=False`, default 제거 등 제약 강화 (빠름).

이 세 단계를 각자 별도 revision으로 만들어 deploy 시점도 분리합니다. 9편의 expand-contract 패턴이 이를 정식화합니다.

## Before-After

```python
# Before: schema와 데이터를 한 revision에 묶어 timeout
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))
    # 1억 row UPDATE — lock + 트랜잭션 로그 폭증
    op.execute("UPDATE users SET tier = 'paid' WHERE last_payment_at IS NOT NULL")
    op.alter_column("users", "tier", server_default=None)
```

```python
# After: 세 revision으로 분리
# revision 1: schema add (nullable=True)
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=True))

# revision 2: data backfill (batch loop)
def upgrade() -> None:
    bind = op.get_bind()
    while True:
        result = bind.execute(text(
            "UPDATE users SET tier = CASE "
            "  WHEN last_payment_at IS NOT NULL THEN 'paid' ELSE 'free' END "
            "WHERE id IN (SELECT id FROM users WHERE tier IS NULL LIMIT 1000)"
        ))
        if result.rowcount == 0:
            break

# revision 3: schema tighten
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier", existing_type=sa.String(16), nullable=False)
```

After 버전은 각 단계를 빠르게 마치고 다음으로 넘어갑니다. revision 2가 길어져도 다른 단계는 영향받지 않습니다.

## 단계별 실습

### 1단계: schema 추가

```bash
alembic revision -m "add users.tier (nullable)"
```

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

### 2단계: 데이터 backfill revision

```bash
alembic revision -m "backfill users.tier"
```

```python
from sqlalchemy import text

def upgrade() -> None:
    bind = op.get_bind()
    batch = 1000
    while True:
        result = bind.execute(text(
            "UPDATE users SET tier = 'free' "
            "WHERE id IN (SELECT id FROM users WHERE tier IS NULL LIMIT :n)"
        ), {"n": batch})
        if result.rowcount == 0:
            break

def downgrade() -> None:
    pass  # 데이터 마이그레이션은 보통 되돌리지 않음 (raise NotImplementedError도 OK)
```

### 3단계: schema 강화

```bash
alembic revision -m "tighten users.tier NOT NULL"
```

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier", existing_type=sa.String(16), nullable=False)

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier", existing_type=sa.String(16), nullable=True)
```

### 4단계: 멱등성 확보

마이그레이션이 중간에 실패해 다시 실행돼도 이상이 없도록 작성합니다.

```python
op.execute("UPDATE users SET tier = 'free' WHERE tier IS NULL")  # 멱등
op.execute("UPDATE users SET counter = counter + 1")              # 비멱등 (위험)
```

`WHERE`로 이미 처리된 row를 제외해 멱등하게 만듭니다.

### 5단계: 검증 쿼리

```python
def upgrade() -> None:
    bind = op.get_bind()
    # ... backfill 작업 ...
    remaining = bind.execute(text("SELECT COUNT(*) FROM users WHERE tier IS NULL")).scalar()
    assert remaining == 0, f"backfill incomplete: {remaining} rows remain"
```

assertion으로 backfill 완성도를 검증합니다. 실패하면 transaction이 rollback되어 schema 강화 단계로 넘어가지 않습니다.

## 자주 하는 실수

- **schema와 데이터를 한 revision에 묶기.** 큰 데이터셋에서 timeout, lock 사고의 주 원인.
- **모델 import해서 사용.** 미래에 모델이 바뀌면 과거 revision이 깨집니다. inline `table()`/`column()`로 대체.
- **batch 없이 전체 UPDATE.** 수백만 row에서 트랜잭션이 폭발합니다.
- **멱등성 무시.** 재실행하면 같은 row를 두 번 처리하는 비멱등 코드는 위험.
- **데이터 마이그레이션의 downgrade를 진심으로 작성.** 일반적으로 데이터는 한 방향만 가는 commit으로 봅니다. `pass` 또는 `raise NotImplementedError`가 정직합니다.

## 실무에서 쓰는 패턴

- **schema/data/tighten 3단계 분리.** 표준 expand-contract 패턴(9편).
- **`op.get_bind()`로 connection을 얻어 SQLAlchemy core 사용.** 높은 portability.
- **inline schema (`table`/`column`)로 시점 고정.** 모델 의존을 끊습니다.
- **batch loop + 명시적 commit.** SQLite/PostgreSQL/MySQL 모두에서 안전.
- **검증 쿼리로 끝맺음.** assertion 한 줄이 운영 사고를 막습니다.
- **CI에서 데이터 마이그레이션의 dry-run.** 작은 dataset으로 batch 루프가 정상 종료하는지 확인.

## 체크리스트

- [ ] schema와 데이터 마이그레이션이 별도 revision으로 분리되어 있다
- [ ] 모델 import 없이 inline `table()`/`column()`을 사용했다
- [ ] 큰 UPDATE는 batch loop로 처리한다
- [ ] WHERE 조건으로 멱등성을 확보했다
- [ ] backfill 완성도를 검증하는 assertion이 있다
- [ ] 데이터 마이그레이션 downgrade는 의도적으로 비웠거나 `NotImplementedError`다

## 정리, 다음 글

데이터 마이그레이션은 schema 마이그레이션과 분리해 별도 revision으로 작성하는 것이 정석입니다. batch loop와 멱등성, 검증 assertion 세 가지가 핵심 도구입니다.

다음 글은 `--sql` 옵션과 SQLite 전용 batch 모드를 깊게 다루는 online vs offline DDL 이야기입니다.

## 참고 자료

- Alembic: Operation Reference (`op.execute`) — https://alembic.sqlalchemy.org/en/latest/ops.html#alembic.operations.Operations.execute
- Alembic: Run Code at Migration Time — https://alembic.sqlalchemy.org/en/latest/cookbook.html#run-arbitrary-python-during-migrations
- SQLAlchemy: SQL Expression Language Tutorial — https://docs.sqlalchemy.org/en/20/tutorial/index.html
- Alembic: Working With Custom Types and Data — https://alembic.sqlalchemy.org/en/latest/cookbook.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, data-migration, op.execute, batch, SQLite
