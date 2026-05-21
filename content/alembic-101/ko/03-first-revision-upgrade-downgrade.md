---
title: "Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성"
series: alembic-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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

# Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성

이 글은 Alembic 101 시리즈의 세 번째 글입니다. 여기서는 첫 revision 파일의 구조를 직접 읽어 보고, `upgrade()`와 `downgrade()`를 안전하게 손으로 작성하는 기준을 정리합니다.

autogenerate가 편리하더라도, 한 번은 직접 써 봐야 자동 생성 결과를 비판적으로 읽을 수 있습니다. 손으로 써 본 사람만 “이건 내가 의도한 migration이 아니다”라고 바로 알아챌 수 있기 때문입니다.

## 먼저 던지는 질문

- `alembic revision`이 만들어 주는 파일 구조는 어떻게 생겼을까요?
- `op.create_table`, `op.add_column`, `op.drop_column`, `op.execute`는 각각 언제 쓸까요?
- `upgrade()`와 `downgrade()`를 어떻게 대칭으로 유지할 수 있을까요?

## 큰 그림

![Alembic 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/03/03-01-diagram-the-two-way-contract-inside-a-re.ko.png)

*Alembic 101 3장 흐름 개요*

## 왜 중요한가

autogenerate가 아무리 좋아도 최종 산출물은 결국 같은 `op` 호출들의 조합입니다. 직접 한 번 작성해 본 사람과 그렇지 않은 사람의 차이는 명확합니다. 자동 생성된 파일을 읽고 “여기서 rename이 drop+add로 풀렸다” 같은 문제를 눈치챌 수 있는지가 달라집니다.

또 하나는 `downgrade`입니다. 운영에서 downgrade를 거의 안 쓴다고 해도, 비워 둔 순간 가장 빠른 복구 수단을 스스로 버리게 됩니다. 정말 되돌릴 수 없는 변경이라면 빈 함수가 아니라 그 정책을 코드에 명시해야 합니다.

## 멘탈 모델

> revision 파일은 **`upgrade(): N → N+1`과 `downgrade(): N+1 → N`이라는 함수 쌍**입니다. 둘이 정확한 역연산이면 Alembic은 graph를 자유롭게 오르내릴 수 있고, 한쪽이라도 비대칭이면 사실상 단방향 commit이 됩니다.

git 비유를 그대로 가져오면 `upgrade`는 commit이고 `downgrade`는 그 commit의 정밀한 revert입니다. 좋은 revision은 downgrade가 깔끔하게 정의된 revision입니다.

### 다이어그램: revision 파일의 양방향 계약

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

## 검증 루틴

```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
sqlite3 app.db ".schema orders"
```

**확인할 점:** 세 명령이 모두 성공하고, 마지막 schema 조회에서 `orders` 테이블과 `ix_orders_user_id` 인덱스가 다시 보이면 왕복 대칭성이 확인된 것입니다.

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

## revision 의존성 그래프를 눈으로 확인하는 습관

첫 revision을 만들고 나면 바로 그래프를 확인하는 습관이 필요합니다. `down_revision` 오타는 코드 리뷰에서 놓치기 쉽고, 배포 직전에야 문제가 드러나는 경우가 많기 때문입니다.

```bash
alembic history --verbose
alembic heads
alembic current
```

`history --verbose` 출력에서 각 노드의 `Revises`가 예상 부모를 가리키는지 확인합니다. 특히 두 명 이상이 동시에 작업한 주간에는 `heads`가 2개 이상인지 먼저 확인하는 편이 안전합니다.

## 수동 작성 시 before/after 스키마 앵커

`upgrade`와 `downgrade`를 쓸 때는 머릿속으로만 역연산을 상상하지 말고, 실제 schema를 비교해야 합니다.

```bash
sqlite3 app.db ".schema users" > before.sql
alembic upgrade head
sqlite3 app.db ".schema users" > after-upgrade.sql
alembic downgrade -1
sqlite3 app.db ".schema users" > after-downgrade.sql
```

`before.sql`과 `after-downgrade.sql`이 의미상 동일하면 대칭성이 확보된 것입니다. 이 검증이 없으면 `downgrade`가 형식상 존재해도 실제로는 불완전한 경우가 많습니다.

## 자주 깨지는 downgrade 패턴

다음 패턴은 리뷰에서 자주 보이며, production에서 즉시 문제를 일으킵니다.

```python
def upgrade() -> None:
    op.create_table("orders", ...)
    op.create_index("ix_orders_user_id", "orders", ["user_id"])

def downgrade() -> None:
    op.drop_table("orders")
    op.drop_index("ix_orders_user_id", table_name="orders")  # 이미 테이블이 없어 실패
```

정답은 reverse order입니다. 객체를 만든 순서의 정확한 역순으로 정리해야 합니다.


## 실전 부록: 운영 앵커 모음

아래 블록은 migration 리뷰와 배포 검증에서 반복해서 쓰는 공통 앵커입니다.

### 1) DDL 미리 보기

```bash
alembic upgrade <from>:<to> --sql > migration-preview.sql
```

리뷰 시점에서 실제 SQL을 확인하면 `DROP`, `ALTER`, 인덱스 재생성 비용을 사전에 파악할 수 있습니다.

### 2) revision 그래프 확인

```bash
alembic history --verbose
alembic heads
alembic current
```

`heads`가 2개 이상이면 기능 결함이 아니라 그래프 정리 이슈입니다. merge revision으로 정리한 뒤 배포해야 안전합니다.

### 3) schema 전후 비교

```bash
sqlite3 app.db ".schema" > before.sql
alembic upgrade head
sqlite3 app.db ".schema" > after.sql
```

변경 의도와 실제 결과를 텍스트로 남기면 코드 리뷰 품질이 올라갑니다.

### 4) data migration 검증 쿼리

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
SELECT tier, COUNT(*) FROM users GROUP BY tier ORDER BY tier;
```

`NULL` 잔여 수와 분포를 함께 보면 backfill 완료 여부를 빠르게 판단할 수 있습니다.

### 5) env.py 핵심 설정

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,
    compare_server_default=True,
    render_as_batch=connection.dialect.name == "sqlite",
)
```

type/default 비교 옵션과 SQLite batch 옵션은 drift 탐지와 호환성 유지에 직접적인 영향을 줍니다.

### 6) blue/green 배포 게이트

```text
Gate A: expand 적용 후 v1 정상
Gate B: v2 배포 후 overlap 정상
Gate C: NULL row 0 확인 후 tighten
Gate D: 구 컬럼 사용 중단 확인 후 contract
```

게이트를 코드화하면 배포 순서 실수를 줄일 수 있습니다.

### 7) 비가역 변경 정책

```python
def downgrade() -> None:
    raise NotImplementedError("irreversible revision by policy")
```

비가역 변경에서 침묵하는 `pass`보다 명시적 예외가 훨씬 안전합니다.

### 8) CI 최소 게이트

```bash
alembic check
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

drift, downgrade 결함, 체인 무결성을 PR 단계에서 차단할 수 있습니다.

### 9) 에러 시그널 해석

```text
Multiple head revisions are present -> merge 필요
Can't locate revision identified by ... -> revision chain 점검 필요
table already exists -> baseline/stamp 전략 점검 필요
```

에러 유형별 대응 경로를 정해 두면 incident 대응 시간이 짧아집니다.

### 10) 팀 운영 원칙

```text
- one PR = one revision
- migration-first deploy
- expand-contract 기본 적용
- production 사고는 forward-fix 우선
```

원칙을 문서가 아니라 PR 템플릿과 CI로 강제하는 것이 핵심입니다.



## 확장 부록: 배포/복구 실습 시나리오

### 시나리오 A: add column + backfill + tighten

```bash
alembic revision -m "add users.phone nullable"
alembic revision -m "backfill users.phone"
alembic revision -m "tighten users.phone not null"
alembic upgrade head
```

```sql
SELECT COUNT(*) FROM users WHERE phone IS NULL;
```

`COUNT(*) = 0`이 아니라면 tighten 단계는 멈춰야 합니다.

### 시나리오 B: 동시에 생성된 head 정리

```bash
alembic heads
alembic merge -m "merge concurrent heads" <head1> <head2>
alembic heads
```

merge 후 head가 하나여야 합니다.

### 시나리오 C: offline SQL 승인 흐름

```bash
alembic upgrade <prev>:head --sql > review.sql
```

검토 포인트는 `DROP`, `ALTER`, 인덱스 재생성, `alembic_version` 갱신 SQL 포함 여부입니다.

### 시나리오 D: incident first checks

```bash
alembic current
alembic heads
```

```sql
SELECT version_num FROM alembic_version;
```

애플리케이션 `/health`의 기대 버전과 DB 버전이 다르면 drift 가능성을 먼저 의심합니다.

### 운영 스크립트 예시

```bash
set -euo pipefail
alembic check
alembic upgrade head
alembic upgrade head --sql > /tmp/migration-preview.sql
```

### 품질 게이트 정리

```text
- autogenerate 결과 수동 검토
- downgrade 정책 명시
- data migration idempotency 확보
- migration-first 배포
- post-deploy smoke test
```

이 게이트들은 Alembic 자체 기능이라기보다 팀 운영 안전장치입니다.



## 보강 메모: 검증 중심 운영 노트

Alembic 운영에서 가장 큰 차이는 "명령 실행"이 아니라 "검증 기록"입니다. 같은 `upgrade head`를 실행해도 검증 쿼리, SQL preview, head 개수 확인을 함께 남기면 문제 재현성이 크게 높아집니다.

```bash
alembic heads
alembic current
alembic upgrade head --sql > /tmp/ddl.sql
```

```sql
SELECT version_num FROM alembic_version;
```

또한 data migration이 포함된 경우에는 진행률을 관찰 가능한 숫자로 남겨야 합니다.

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
```

운영자는 이 숫자를 기준으로 tighten 단계 진행 여부를 결정해야 합니다. 값이 0이 아니면 단계 진행을 멈추고 backfill을 계속해야 합니다.

배포 실패 대응의 기본 원칙은 다음과 같습니다.

```text
1) 현재 revision 위치를 먼저 확정한다.
2) graph 상태(single head인지)를 확인한다.
3) backward-compatible 여부를 판단한다.
4) 가능하면 forward-fix revision으로 복구한다.
```

이 네 단계는 엔진(SQLite/PostgreSQL)과 무관하게 공통으로 적용됩니다.



## 보강 메모: 검증 중심 운영 노트

Alembic 운영에서 가장 큰 차이는 "명령 실행"이 아니라 "검증 기록"입니다. 같은 `upgrade head`를 실행해도 검증 쿼리, SQL preview, head 개수 확인을 함께 남기면 문제 재현성이 크게 높아집니다.

```bash
alembic heads
alembic current
alembic upgrade head --sql > /tmp/ddl.sql
```

```sql
SELECT version_num FROM alembic_version;
```

또한 data migration이 포함된 경우에는 진행률을 관찰 가능한 숫자로 남겨야 합니다.

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
```

운영자는 이 숫자를 기준으로 tighten 단계 진행 여부를 결정해야 합니다. 값이 0이 아니면 단계 진행을 멈추고 backfill을 계속해야 합니다.

배포 실패 대응의 기본 원칙은 다음과 같습니다.

```text
1) 현재 revision 위치를 먼저 확정한다.
2) graph 상태(single head인지)를 확인한다.
3) backward-compatible 여부를 판단한다.
4) 가능하면 forward-fix revision으로 복구한다.
```

이 네 단계는 엔진(SQLite/PostgreSQL)과 무관하게 공통으로 적용됩니다.



## 보강 메모: 검증 중심 운영 노트

Alembic 운영에서 가장 큰 차이는 "명령 실행"이 아니라 "검증 기록"입니다. 같은 `upgrade head`를 실행해도 검증 쿼리, SQL preview, head 개수 확인을 함께 남기면 문제 재현성이 크게 높아집니다.

```bash
alembic heads
alembic current
alembic upgrade head --sql > /tmp/ddl.sql
```

```sql
SELECT version_num FROM alembic_version;
```

또한 data migration이 포함된 경우에는 진행률을 관찰 가능한 숫자로 남겨야 합니다.

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
```

운영자는 이 숫자를 기준으로 tighten 단계 진행 여부를 결정해야 합니다. 값이 0이 아니면 단계 진행을 멈추고 backfill을 계속해야 합니다.

배포 실패 대응의 기본 원칙은 다음과 같습니다.

```text
1) 현재 revision 위치를 먼저 확정한다.
2) graph 상태(single head인지)를 확인한다.
3) backward-compatible 여부를 판단한다.
4) 가능하면 forward-fix revision으로 복구한다.
```

이 네 단계는 엔진(SQLite/PostgreSQL)과 무관하게 공통으로 적용됩니다.



## 보강 메모: 검증 중심 운영 노트

Alembic 운영에서 가장 큰 차이는 "명령 실행"이 아니라 "검증 기록"입니다. 같은 `upgrade head`를 실행해도 검증 쿼리, SQL preview, head 개수 확인을 함께 남기면 문제 재현성이 크게 높아집니다.

```bash
alembic heads
alembic current
alembic upgrade head --sql > /tmp/ddl.sql
```

```sql
SELECT version_num FROM alembic_version;
```

또한 data migration이 포함된 경우에는 진행률을 관찰 가능한 숫자로 남겨야 합니다.

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
```

운영자는 이 숫자를 기준으로 tighten 단계 진행 여부를 결정해야 합니다. 값이 0이 아니면 단계 진행을 멈추고 backfill을 계속해야 합니다.

배포 실패 대응의 기본 원칙은 다음과 같습니다.

```text
1) 현재 revision 위치를 먼저 확정한다.
2) graph 상태(single head인지)를 확인한다.
3) backward-compatible 여부를 판단한다.
4) 가능하면 forward-fix revision으로 복구한다.
```

이 네 단계는 엔진(SQLite/PostgreSQL)과 무관하게 공통으로 적용됩니다.


## 처음 질문으로 돌아가기

- **`alembic revision`이 만들어 주는 파일 구조는 어떻게 생겼을까요?**
  - 본문의 기준은 첫 revision: upgrade와 downgrade를 손으로 작성를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`op.create_table`, `op.add_column`, `op.drop_column`, `op.execute`는 각각 언제 쓸까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`upgrade()`와 `downgrade()`를 어떻게 대칭으로 유지할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- **첫 revision: upgrade와 downgrade를 손으로 작성 (현재 글)**
- autogenerate: 잡는 것과 못 잡는 것의 경계 (예정)
- branch와 merge: 동시에 만든 revision을 합치는 법 (예정)
- 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기 (예정)
- online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 (예정)
- downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 (예정)
- 배포 순서와 blue/green: schema와 application code의 안전한 동기화 (예정)
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Operation Reference](https://alembic.sqlalchemy.org/en/latest/ops.html)
- [Alembic: Working with Branches](https://alembic.sqlalchemy.org/en/latest/branches.html)
- [Alembic: Batch Mode](https://alembic.sqlalchemy.org/en/latest/batch.html)
- [SQLAlchemy: Schema Definition](https://docs.sqlalchemy.org/en/20/core/schema.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/03-first-revision-upgrade-downgrade)

Tags: Python, Alembic, SQLAlchemy, Migration
