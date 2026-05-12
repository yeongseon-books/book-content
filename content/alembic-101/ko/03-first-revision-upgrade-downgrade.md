---
title: '첫 revision: upgrade와 downgrade를 손으로 작성'
series: alembic-101
episode: 3
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
- revision
- upgrade
- downgrade
- SQLite
last_reviewed: '2026-05-03'
seo_description: 'revision 파일은 upgrade(): N → N+1과 downgrade(): N+1 → N이라는 함수 쌍입니다.'
---

# 첫 revision: upgrade와 downgrade를 손으로 작성

revision 파일은 결국 `upgrade()`와 `downgrade()`를 어떻게 쓰느냐의 문제입니다. 처음 한 번 손으로 작성해 봐야 autogenerate 결과도 비판적으로 읽을 수 있습니다.

이 글은 Alembic 101 시리즈의 3번째 글입니다. 여기서는 첫 revision 파일의 구조와 안전한 upgrade·downgrade 작성 원칙을 정리합니다.

## 핵심 질문

첫 마이그레이션을 만들 때 upgrade와 downgrade를 어떻게 짜야 안전하게 되돌릴 수 있을까요?

이 글은 그 질문에 답하기 위해 첫 리비전과 업/다운그레이드의 핵심 결정과 실무 함정을 살펴봅니다.


## 이 글에서 다룰 문제

autogenerate가 아무리 좋아도 결국 만들어 주는 것은 같은 op 호출의 조합입니다. 손으로 한 번 작성해 본 사람과 그렇지 않은 사람의 차이는 큽니다. 자동 생성된 파일을 읽고 "이 부분은 의도와 다르다"라고 잡아낼 수 있느냐의 차이이기 때문입니다.

또 한 가지, `downgrade`를 진심으로 작성해 두는 것 자체가 production을 안전하게 합니다. "절대 downgrade는 안 한다"는 정책도 가능하지만, downgrade를 빈 함수로 두는 순간 실수로 적용된 잘못된 마이그레이션을 빠르게 되돌릴 수단이 사라집니다.

## Mental Model

> revision 파일은 **`upgrade(): N → N+1`과 `downgrade(): N+1 → N`이라는 함수 쌍**입니다. 둘이 정확히 역연산이 되도록 짜면 alembic은 그래프를 자유롭게 위아래로 이동할 수 있습니다. 한쪽이라도 비대칭이면 그 revision은 사실상 단방향 commit이 됩니다.

git에 비유하면 `upgrade`는 commit이고 `downgrade`는 그 commit의 정확한 revert입니다. revert가 깔끔히 되도록 작성하는 commit이 좋은 commit인 것처럼, downgrade가 정확한 revision이 좋은 revision입니다.

## 핵심 개념

### 자동 생성된 revision 파일

```python
"""add users.tier

Revision ID: 3f9c8b21de7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-05-03 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "3f9c8b21de7a"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

위에서부터 읽으면 (1) 이 revision의 ID와 부모 ID, (2) `upgrade`/`downgrade` 한 쌍이 전부입니다. `branch_labels`와 `depends_on`은 5편에서 다룹니다.

### `op` 모듈

`op`는 alembic이 제공하는 DDL 헬퍼입니다. 자주 쓰는 것만 정리하면 다음과 같습니다.

| 연산 | 용도 |
| --- | --- |
| `op.create_table(name, *columns)` | 테이블 생성 |
| `op.drop_table(name)` | 테이블 삭제 |
| `op.add_column(table, column)` | 컬럼 추가 |
| `op.drop_column(table, name)` | 컬럼 삭제 |
| `op.alter_column(table, name, ...)` | 타입/nullable/default 변경 |
| `op.create_index(name, table, cols)` | 인덱스 생성 |
| `op.drop_index(name, table)` | 인덱스 삭제 |
| `op.execute(sql)` | 임의 SQL 실행 |

### `down_revision` 그래프

새 revision이 생성될 때 alembic은 현재 head의 ID를 `down_revision`에 자동으로 박습니다. 이 한 줄이 그래프를 만듭니다. revision ID는 보통 hash로 충분히 유일하지만, 같은 시점에 두 사람이 head에서 revision을 생성하면 두 revision이 같은 `down_revision`을 가리키게 되고 → branch가 됩니다(5편).

## Before-After

```python
# Before: downgrade가 비어 있는 위험한 revision
def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])

def downgrade() -> None:
    pass  # ← 빈 채로 두면 단방향 commit
```

```python
# After: 정확한 역연산
def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])

def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
```

After 버전은 정확히 역순(인덱스 → 테이블)으로 정리합니다. 이 순서는 외래키와 인덱스 의존성 때문에 중요합니다.

## 단계별 실습

### 1단계: 빈 revision 생성

```bash
alembic revision -m "create orders"
```

`versions/<hash>_create_orders.py`가 생성됩니다. `upgrade`와 `downgrade`가 빈 함수로 들어 있습니다.

### 2단계: `upgrade` 작성

```python
def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
```

`server_default=sa.func.current_timestamp()`처럼 default를 DB 측에 두면 application 코드 변경 없이 기존 row에도 값이 채워집니다.

### 3단계: `downgrade` 작성 (역순)

```python
def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
```

생성 순서: 테이블 → 인덱스. 삭제 순서: 인덱스 → 테이블. 외래키가 있으면 자식 테이블부터 drop합니다.

### 4단계: 적용과 되돌리기

```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

세 번 모두 깔끔하게 동작하면 upgrade/downgrade가 대칭이라는 증명이 됩니다.

### 5단계: SQLite에서 컬럼 변경 (batch 모드)

SQLite는 컬럼 type/nullable 변경을 직접 못 합니다. batch 모드로 감쌉니다.

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("tier", sa.String(16), nullable=False, server_default="free"))

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("tier")
```

2편에서 `render_as_batch=True`를 켜 두었다면 자동으로 batch가 적용되지만, 명시적으로 `batch_alter_table` 컨텍스트 매니저를 쓰는 편이 의도가 분명합니다.

### 6단계: `op.execute`로 데이터 보정

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100)))
    op.execute("UPDATE users SET display_name = name WHERE display_name IS NULL")
```

스키마와 데이터 변경을 같은 revision에 묶을 수 있습니다. 다만 큰 데이터셋은 별도 데이터 마이그레이션(6편)으로 분리하는 게 안전합니다.

## 자주 하는 실수

- **`downgrade`를 비워 두기.** "안 쓸 거니까"라고 하다가 사고가 났을 때 빠른 회복 수단이 사라집니다. 비워 두려면 차라리 `raise NotImplementedError`로 명시합니다.
- **`upgrade`만 테스트.** PR 로컬에서 한 번씩 `downgrade -1 && upgrade head`를 돌려야 대칭성이 확인됩니다.
- **외래키 의존을 무시한 drop 순서.** child → parent 순서로 지웁니다. 그렇지 않으면 FK violation.
- **autogenerate를 그대로 commit.** 자동 생성은 시작점일 뿐입니다. table 생성 순서, 인덱스 이름, server_default 등은 사람이 검토합니다.
- **SQLite에서 batch 없이 ALTER.** "syntax error" 또는 "not supported"로 깨집니다.

## 실무에서 쓰는 패턴

- **`upgrade` ↔ `downgrade` 페어 리뷰.** PR 리뷰 체크리스트에 "downgrade 시 역순으로 정확한가" 항목을 둡니다.
- **`server_default`는 DB-side default.** `default`(SQLAlchemy default)는 ORM 호출 경로에서만 동작합니다. 마이그레이션에는 `server_default`가 정답입니다.
- **revision 메시지는 명령형 한 줄.** `add users.tier`, `create orders`처럼 짧고 직접적으로.
- **하나의 revision에 한 가지 변경.** add column 두 개를 하나로 묶어도 되지만, 다른 모듈의 변경을 같은 revision에 합치지 않습니다. 회귀 시 분리 회복이 어렵습니다.
- **drop은 두 단계로.** 컬럼 사용 제거 코드 → 다음 release에서 컬럼 drop revision. 9편에서 자세히.

## 체크리스트

- [ ] `upgrade()`와 `downgrade()`가 정확히 역연산이다
- [ ] 외래키·인덱스 의존성을 고려해 순서를 잡았다
- [ ] SQLite에서는 `batch_alter_table` 컨텍스트를 명시적으로 썼다
- [ ] `server_default`로 DB 측 default를 지정했다 (application default와 혼동 금지)
- [ ] revision 메시지가 명령형 한 줄이고 의도가 분명하다
- [ ] 로컬에서 `downgrade -1 && upgrade head` 사이클을 한 번 돌려 검증했다
- [ ] autogenerate 출력이라면 사람 검토를 거쳤다

## 정리, 다음 글

revision 파일은 결국 `upgrade`/`downgrade` 한 쌍입니다. 둘을 대칭으로 짜는 습관 하나가 production에서 가장 큰 안전선이 됩니다. SQLite에서는 batch 모드가 거의 필수라는 점도 같이 기억합니다.

다음 글은 손으로 작성하던 이 작업을 자동으로 만들어 주는 `--autogenerate` 옵션을 본격적으로 다룹니다. 자동으로 잡는 것과 못 잡는 것의 경계가 어디인지가 핵심입니다.

## 참고 자료

- Alembic: Operation Reference — https://alembic.sqlalchemy.org/en/latest/ops.html
- Alembic: Working with Branches — https://alembic.sqlalchemy.org/en/latest/branches.html
- Alembic: Batch Mode — https://alembic.sqlalchemy.org/en/latest/batch.html
- SQLAlchemy: Schema Definition — https://docs.sqlalchemy.org/en/20/core/schema.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, revision, upgrade, downgrade, SQLite
