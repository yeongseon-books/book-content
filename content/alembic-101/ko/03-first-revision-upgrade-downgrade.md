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
last_reviewed: '2026-05-12'
seo_description: 'revision 파일은 upgrade(): N → N+1과 downgrade(): N+1 → N이라는 함수 쌍입니다.'
---

# 첫 revision: upgrade와 downgrade를 손으로 작성

이 글은 Alembic 101 시리즈의 세 번째 글입니다. 여기서는 첫 revision 파일의 구조를 직접 읽어 보고, `upgrade()`와 `downgrade()`를 안전하게 손으로 작성하는 기준을 정리합니다.

autogenerate가 편리하더라도, 한 번은 직접 써 봐야 자동 생성 결과를 비판적으로 읽을 수 있습니다. 손으로 써 본 사람만 “이건 내가 의도한 migration이 아니다”라고 바로 알아챌 수 있기 때문입니다.

## 이 글에서 다룰 문제

- `alembic revision`이 만들어 주는 파일 구조는 어떻게 생겼을까요?
- `op.create_table`, `op.add_column`, `op.drop_column`, `op.execute`는 각각 언제 쓸까요?
- `upgrade()`와 `downgrade()`를 어떻게 대칭으로 유지할 수 있을까요?
- `down_revision`은 revision graph를 어떻게 형성할까요?
- SQLite에서는 왜 explicit batch mode 패턴을 익혀야 할까요?

## 왜 중요한가

autogenerate가 아무리 좋아도 최종 산출물은 결국 같은 `op` 호출들의 조합입니다. 직접 한 번 작성해 본 사람과 그렇지 않은 사람의 차이는 명확합니다. 자동 생성된 파일을 읽고 “여기서 rename이 drop+add로 풀렸다” 같은 문제를 눈치챌 수 있는지가 달라집니다.

또 하나는 `downgrade`입니다. 운영에서 downgrade를 거의 안 쓴다고 해도, 비워 둔 순간 가장 빠른 복구 수단을 스스로 버리게 됩니다. 정말 되돌릴 수 없는 변경이라면 빈 함수가 아니라 그 정책을 코드에 명시해야 합니다.

## 멘탈 모델

> revision 파일은 **`upgrade(): N → N+1`과 `downgrade(): N+1 → N`이라는 함수 쌍**입니다. 둘이 정확한 역연산이면 Alembic은 graph를 자유롭게 오르내릴 수 있고, 한쪽이라도 비대칭이면 사실상 단방향 commit이 됩니다.

git 비유를 그대로 가져오면 `upgrade`는 commit이고 `downgrade`는 그 commit의 정밀한 revert입니다. 좋은 revision은 downgrade가 깔끔하게 정의된 revision입니다.

## 핵심 개념

### 자동 생성 revision 파일의 형태

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

위에서부터 읽으면 (1) revision 자신의 ID와 부모 ID, (2) `upgrade`/`downgrade` 쌍이 전부입니다. `branch_labels`와 `depends_on`은 5편에서 다룹니다.

### `op` 모듈

`op`는 Alembic이 노출하는 DDL helper입니다. 자주 쓰는 연산은 다음과 같습니다.

| 연산 | 용도 |
| --- | --- |
| `op.create_table(name, *columns)` | 테이블 생성 |
| `op.drop_table(name)` | 테이블 삭제 |
| `op.add_column(table, column)` | 컬럼 추가 |
| `op.drop_column(table, name)` | 컬럼 삭제 |
| `op.alter_column(table, name, ...)` | 타입 / nullable / default 변경 |
| `op.create_index(name, table, cols)` | 인덱스 생성 |
| `op.drop_index(name, table)` | 인덱스 삭제 |
| `op.execute(sql)` | 임의 SQL 실행 |

### `down_revision` graph

새 revision을 만들 때 Alembic은 현재 head의 ID를 `down_revision`에 자동으로 찍습니다. 그래프를 만드는 핵심은 이 한 줄입니다. 두 사람이 같은 head에서 동시에 revision을 만들면 두 revision이 같은 `down_revision`을 가리키고, 그 순간 branch가 생깁니다. 이 부분은 5편에서 이어집니다.

## 변경 전후

```python
# Before: a dangerous revision with empty downgrade
def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])

def downgrade() -> None:
    pass  # ← leaving this empty makes it a one-way commit
```

```python
# After: a precise inverse
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

After 버전은 index → table 순서로 정확히 역순 정리합니다. 외래키와 인덱스 의존성 때문에 이 순서는 중요합니다.

## 단계별 실습

### 1단계: 빈 revision 생성

```bash
alembic revision -m "create orders"
```

그러면 `versions/<hash>_create_orders.py`가 생성되고, 안에는 비어 있는 `upgrade`와 `downgrade`가 들어 있습니다.

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

`server_default=sa.func.current_timestamp()`처럼 DB 쪽 default를 주면 기존 row까지 데이터베이스 차원에서 값을 채울 수 있습니다.

### 3단계: `downgrade` 작성 (역순)

```python
def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
```

생성 순서는 table → index이고, 삭제 순서는 index → table입니다. foreign key가 있으면 child부터 내려야 합니다.

### 4단계: 적용과 되돌리기

```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

세 단계가 모두 깨끗하게 성공하면 `upgrade`와 `downgrade`가 대칭이라는 뜻입니다.

### 5단계: SQLite에서 컬럼 변경하기 (batch mode)

SQLite는 컬럼 타입과 nullability를 직접 바꾸지 못합니다. batch mode로 감쌉니다.

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("tier", sa.String(16), nullable=False, server_default="free"))

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("tier")
```

2편에서 `render_as_batch=True`를 켰더라도, 이렇게 `batch_alter_table`을 명시하면 의도가 더 선명해집니다.

### 6단계: `op.execute`로 데이터 보정

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100)))
    op.execute("UPDATE users SET display_name = name WHERE display_name IS NULL")
```

스키마 변경과 간단한 데이터 보정을 한 revision에 묶을 수는 있습니다. 다만 데이터가 커지면 6편처럼 별도 data migration으로 분리하는 편이 훨씬 안전합니다.

## 자주 하는 실수

- **`downgrade`를 비워 두기.** 정말 막고 싶다면 차라리 `raise NotImplementedError`로 의도를 명시하세요.
- **`upgrade`만 테스트하기.** PR마다 최소 한 번은 `downgrade -1 && upgrade head`를 돌려 대칭성을 확인해야 합니다.
- **drop 순서에서 foreign key 의존성을 무시하기.** child → parent 순서를 지키지 않으면 FK violation이 납니다.
- **autogenerate 결과를 그대로 커밋하기.** 시작점일 뿐입니다. 생성 순서, 인덱스 이름, `server_default`는 사람이 검토해야 합니다.
- **SQLite에서 batch 없이 ALTER를 시도하기.** 지원되지 않는 문법 오류로 실패합니다.

## 실무 패턴

- **`upgrade`와 `downgrade`를 한 쌍으로 리뷰합니다.** “정확한 역순인가?”를 PR 체크리스트에 넣습니다.
- **`server_default`는 DB-side default입니다.** SQLAlchemy의 `default`는 ORM 경로에서만 동작하므로 migration에는 맞지 않습니다.
- **revision 메시지는 명령형 한 줄로 씁니다.** `add users.tier`, `create orders`처럼 짧고 직접적으로 씁니다.
- **하나의 revision에는 하나의 논리 변경만 넣습니다.** 서로 무관한 모듈 변경을 묶으면 회복이 어려워집니다.
- **drop은 보통 두 단계로 나눕니다.** 먼저 코드가 사용을 멈추고, 다음 배포에서 컬럼을 내립니다. 9편에서 자세히 다룹니다.

## 체크리스트

- [ ] `upgrade()`와 `downgrade()`가 정확한 역연산이다
- [ ] 외래키와 인덱스 의존성을 고려해 순서를 잡았다
- [ ] SQLite에서는 `batch_alter_table`을 명시적으로 사용했다
- [ ] DB-side default에는 `server_default`를 썼다
- [ ] revision 메시지가 명령형 한 줄이고 의도가 분명하다
- [ ] 로컬에서 `downgrade -1 && upgrade head`를 검증했다
- [ ] autogenerate 결과였다면 사람이 직접 검토했다

## 연습 문제

1. `users`에 `tier`, `last_login_at` 두 컬럼을 수동으로 추가하는 revision을 작성하고 `downgrade`가 동작하는지 확인해 보세요.
2. `orders` 테이블을 만든 뒤 `downgrade -1 && upgrade head`를 다섯 번 연속 실행해 무결성을 확인해 보세요.
3. SQLite에서 `op.alter_column`으로 nullability를 바꾸는 migration을 batch mode 유무 두 경우로 비교해 보세요.

## 정리, 다음 글

revision 파일은 결국 `upgrade`와 `downgrade` 한 쌍으로 귀결됩니다. 이 둘을 대칭으로 유지하는 습관이 production에서 가장 강한 안전선입니다. SQLite에서는 batch mode를 사실상 기본으로 생각하는 편이 좋습니다.

다음 글에서는 `--autogenerate`를 본격적으로 다룹니다. 자동으로 잘 잡는 것과 사람이 반드시 직접 봐야 하는 것의 경계가 핵심입니다.

<!-- toc:begin -->
<!-- toc:end -->

## 참고 자료

- Alembic: Operation Reference — https://alembic.sqlalchemy.org/en/latest/ops.html
- Alembic: Working with Branches — https://alembic.sqlalchemy.org/en/latest/branches.html
- Alembic: Batch Mode — https://alembic.sqlalchemy.org/en/latest/batch.html
- SQLAlchemy: Schema Definition — https://docs.sqlalchemy.org/en/20/core/schema.html

Tags: Python, Alembic, revision, upgrade, downgrade, SQLite
