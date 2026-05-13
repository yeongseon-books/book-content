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
last_reviewed: '2026-05-12'
seo_description: 데이터 마이그레이션은 "schema는 그대로 두고 row를 변환하는 revision"입니다.
---

# 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기

이 글은 Alembic 101 시리즈의 여섯 번째 글입니다. 여기서는 data migration이 schema migration과 어떻게 다른지, 그리고 row 변환 작업을 왜 별도 revision으로 분리해야 하는지 실무 패턴 중심으로 설명합니다.

데이터 마이그레이션은 주변의 schema 변경보다 더 느리고, 더 비가역적이며, 실패했을 때 복구가 더 어렵습니다. 그래서 row 변환을 revision 안에 어떻게 격리하느냐가 lock 시간과 재실행 안정성을 좌우합니다.

## 이 글에서 다룰 문제

- data migration은 schema migration과 무엇이 다를까요?
- `op.execute`는 raw SQL과 SQLAlchemy Core 중 어떤 스타일로 쓸 수 있을까요?
- 큰 데이터셋은 어떤 batch 패턴으로 나누어 처리해야 할까요?
- 왜 schema-only revision과 data-only revision을 분리해야 할까요?
- idempotency와 안전한 재실행은 어떻게 확보할까요?

## 왜 중요한가

`ALTER TABLE`만 migration은 아닙니다. column rename, enum 값 변경, JSON 구조 변환처럼 schema와 함께 데이터도 바뀌는 작업이 많습니다. 문제는 이런 data migration을 schema revision 안에 그대로 섞으면 큰 데이터셋에서 lock과 timeout이 폭발하고, `downgrade`는 사실상 불가능해진다는 점입니다.

## 멘탈 모델

> data migration은 **schema는 그대로 두고 row를 변환하는 revision**입니다. 이를 schema-only revision과 분리하면 (1) 거대한 트랜잭션을 작은 batch로 쪼갤 수 있고, (2) 실패 시 schema는 유지한 채 data 단계만 다시 실행할 수 있으며, (3) 리뷰어가 의도를 더 정확히 읽을 수 있습니다.

git 비유로 보면 schema 변경은 코드 refactor이고, data migration은 데이터 변환 스크립트입니다. 둘을 한 commit에 섞으면 history가 흐려집니다.

## 핵심 개념

### `op.execute`의 두 가지 스타일

**Raw SQL**

```python
def upgrade() -> None:
    op.execute("UPDATE users SET tier = 'free' WHERE tier IS NULL")
```

빠르고 단순하지만 dialect에 묶이고 IDE 도움도 적습니다.

**SQLAlchemy core**

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

조금 길지만 dialect-agnostic하고, 변환 로직이 복잡할수록 더 안전합니다. 중요한 점은 migration 안에서 live 모델을 import하지 않는다는 것입니다. 미래에 모델이 바뀌면 과거 migration이 깨질 수 있으므로 `table()`과 `column()`으로 그 시점의 schema만 inline으로 표현해야 합니다.

### batch 처리

수백만 row에 대한 단일 `UPDATE`는 lock과 transaction log를 크게 키웁니다. SQLite에서는 concurrency 이슈가, PostgreSQL과 MySQL에서는 다른 transaction 차단이 발생합니다.

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

루프 안에서 명시적으로 commit을 끊어 주면 더 안전해집니다. SQLite는 single-writer이기 때문에 긴 transaction이 다른 작업을 막는 시간을 줄이는 것이 특히 중요합니다.

### schema revision과 data revision 분리

표준 패턴은 세 단계입니다.

1. **schema add**: 새 컬럼이나 테이블을 `nullable=True`로 추가합니다. 빠릅니다.
2. **data backfill**: 기존 row를 채우는 data migration을 수행합니다. 느리고 batch가 필요합니다.
3. **schema tighten**: `nullable=False`를 강제하거나 default를 제거합니다. 다시 빠른 단계입니다.

각 단계는 별도 revision이어야 하고, deploy 시점도 분리하는 편이 맞습니다. 9편의 expand-contract가 이 패턴을 운영 정책으로 정리합니다.

## 변경 전후

```python
# Before: schema and data bundled into one revision and timing out
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))
    # 100M-row UPDATE — lock + transaction log explosion
    op.execute("UPDATE users SET tier = 'paid' WHERE last_payment_at IS NOT NULL")
    op.alter_column("users", "tier", server_default=None)
```

```python
# After: split into three revisions
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

After 패턴은 각 단계의 책임을 분리합니다. revision 2가 오래 걸리더라도 schema add와 schema tighten은 여전히 짧고 명확합니다.

## 단계별 실습

### 1단계: schema 추가 revision

```bash
alembic revision -m "add users.tier (nullable)"
```

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

### 2단계: data backfill revision

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
    pass  # data migrations usually do not roll back (raise NotImplementedError is also fine)
```

### 3단계: schema tighten revision

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

### 4단계: idempotency 확보

재실행돼도 깨지지 않도록 작성해야 합니다.

```python
op.execute("UPDATE users SET tier = 'free' WHERE tier IS NULL")  # idempotent
op.execute("UPDATE users SET counter = counter + 1")              # non-idempotent (dangerous)
```

이미 처리한 row를 제외하는 `WHERE` 절이 핵심입니다.

### 5단계: 검증 쿼리 추가

```python
def upgrade() -> None:
    bind = op.get_bind()
    # ... backfill work ...
    remaining = bind.execute(text("SELECT COUNT(*) FROM users WHERE tier IS NULL")).scalar()
    assert remaining == 0, f"backfill incomplete: {remaining} rows remain"
```

assertion은 backfill이 끝났는지 검증합니다. 실패하면 transaction이 롤백되고 schema tighten 단계는 진행되지 않습니다.

## 자주 하는 실수

- **schema와 data를 한 revision에 섞기.** 큰 데이터셋에서 timeout과 lock 사고의 가장 흔한 원인입니다.
- **migration 안에서 모델을 import하기.** 미래의 모델 변경이 과거 revision을 깨뜨립니다. inline `table()` / `column()`을 쓰세요.
- **전체 테이블을 한 번에 UPDATE하기.** row 수가 커질수록 transaction이 감당되지 않습니다.
- **idempotency를 무시하기.** 재실행 시 같은 row를 두 번 처리하면 위험합니다.
- **data migration에 진지한 `downgrade`를 쓰려고 하기.** 보통 데이터는 one-way commit입니다. `pass`나 `NotImplementedError`가 더 정직합니다.

## 실무 패턴

- **schema / data / tighten의 3단계 분리**를 기본형으로 가져갑니다.
- **`op.get_bind()`와 SQLAlchemy Core를 사용합니다.** 이식성과 가독성의 균형이 좋습니다.
- **inline schema로 시점을 고정합니다.** live 모델 의존성을 끊을 수 있습니다.
- **batch loop와 explicit commit을 검토합니다.** SQLite, PostgreSQL, MySQL 모두에서 안전성이 올라갑니다.
- **마지막에 verification query를 넣습니다.** 단일 assertion 하나가 production 사고를 막습니다.
- **CI에서 소규모 dry-run을 돌립니다.** batch loop가 종료되는지, 재실행이 안전한지 확인합니다.

## 체크리스트

- [ ] schema migration과 data migration을 별도 revision으로 분리했다
- [ ] 모델 import 없이 inline `table()` / `column()`을 사용했다
- [ ] 큰 `UPDATE`는 batch loop로 나눴다
- [ ] `WHERE` 절로 idempotency를 확보했다
- [ ] verification assertion으로 backfill 완료를 확인했다
- [ ] data migration의 `downgrade`는 의도적으로 비우거나 `NotImplementedError`를 사용했다

## 연습 문제

1. `users`에 `display_name` 컬럼을 추가하고 `name`에서 backfill한 뒤, 별도 revision에서 `name`을 제거하는 3단계 migration을 만들어 보세요.
2. 100만 개의 fake row를 넣고 batch loop가 얼마나 걸리는지 측정해 보세요.
3. backfill assertion이 실패하도록 만들어 transaction이 롤백되는지 확인해 보세요.

## 정리, 다음 글

data migration의 기본형은 schema 변경과 분리된 별도 revision입니다. batch loop, idempotency, verification assertion이 핵심 도구입니다.

다음 글에서는 `--sql` 기반의 offline DDL 미리 보기와 SQLite 전용 batch mode를 함께 다루며, online과 offline의 역할 분담을 정리합니다.

<!-- toc:begin -->
<!-- toc:end -->

## 참고 자료

- Alembic: Operation Reference (`op.execute`) — https://alembic.sqlalchemy.org/en/latest/ops.html#alembic.operations.Operations.execute
- Alembic: Run Code at Migration Time — https://alembic.sqlalchemy.org/en/latest/cookbook.html#run-arbitrary-python-during-migrations
- SQLAlchemy: SQL Expression Language Tutorial — https://docs.sqlalchemy.org/en/20/tutorial/index.html
- Alembic: Working With Custom Types and Data — https://alembic.sqlalchemy.org/en/latest/cookbook.html

Tags: Python, Alembic, data-migration, op.execute, batch, SQLite
