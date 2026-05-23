---
title: "Alembic 101 (6/10): 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기"
series: alembic-101
episode: 6
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
- data-migration
- op.execute
- batch
- SQLite
last_reviewed: '2026-05-12'
seo_description: 데이터 마이그레이션은 "schema는 그대로 두고 row를 변환하는 revision"입니다.
---

# Alembic 101 (6/10): 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기

이 글은 Alembic 101 시리즈의 여섯 번째 글입니다. 여기서는 data migration이 schema migration과 어떻게 다른지, 그리고 row 변환 작업을 왜 별도 revision으로 분리해야 하는지 실무 패턴 중심으로 설명합니다.

데이터 마이그레이션은 주변의 schema 변경보다 더 느리고, 더 비가역적이며, 실패했을 때 복구가 더 어렵습니다. 그래서 row 변환을 revision 안에 어떻게 격리하느냐가 lock 시간과 재실행 안정성을 좌우합니다.

![Alembic 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/06/06-01-diagram-the-three-stage-split-for-data-m.ko.png)
*Alembic 101 6장 흐름 개요*

## 먼저 던지는 질문

- data migration은 schema migration과 무엇이 다를까요?
- `op.execute`는 raw SQL과 SQLAlchemy Core 중 어떤 스타일로 쓸 수 있을까요?
- 큰 데이터셋은 어떤 batch 패턴으로 나누어 처리해야 할까요?

## 왜 중요한가

`ALTER TABLE`만 migration은 아닙니다. column rename, enum 값 변경, JSON 구조 변환처럼 schema와 함께 데이터도 바뀌는 작업이 많습니다. 문제는 이런 data migration을 schema revision 안에 그대로 섞으면 큰 데이터셋에서 lock과 timeout이 폭발하고, `downgrade`는 사실상 불가능해진다는 사실입니다.

## 멘탈 모델

> data migration은 **schema는 그대로 두고 row를 변환하는 revision**입니다. 이를 schema-only revision과 분리하면 (1) 거대한 트랜잭션을 작은 batch로 쪼갤 수 있고, (2) 실패 시 schema는 유지한 채 data 단계만 다시 실행할 수 있으며, (3) 리뷰어가 의도를 더 정확히 읽을 수 있습니다.

git 비유로 보면 schema 변경은 코드 refactor이고, data migration은 데이터 변환 스크립트입니다. 둘을 한 commit에 섞으면 history가 흐려집니다.

### 다이어그램: schema와 data를 분리하는 3단계

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

조금 길지만 dialect-agnostic하고, 변환 로직이 복잡할수록 더 안전합니다. 중요한 점은 migration 안에서 live 모델을 import하지 않는다는 사실입니다. 미래에 모델이 바뀌면 과거 migration이 깨질 수 있으므로 `table()`과 `column()`으로 그 시점의 schema만 inline으로 표현해야 합니다.

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
# 이전: 스키마와 데이터가 하나의 개정판에 번들로 포함되어 시간 초과됨
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))
    # 100M 행 업데이트 — 잠금 + 트랜잭션 로그 폭발
    op.execute("UPDATE users SET tier = 'paid' WHERE last_payment_at IS NOT NULL")
    op.alter_column("users", "tier", server_default=None)
```

```python
# 이후: 3개의 개정판으로 분할
# 개정 1: 스키마 추가(nullable=True)
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=True))

# 개정 2: 데이터 백필(일괄 루프)
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

# 개정 3: 스키마 강화
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

## 검증 루틴

```bash
alembic upgrade head
sqlite3 app.db "SELECT COUNT(*) FROM users WHERE tier IS NULL;"
```

**확인할 점:** backfill 뒤 NULL row 수가 0이어야만 다음 tighten revision으로 넘어갑니다. 이 숫자를 확인하지 않으면 NOT NULL 강화는 아직 이릅니다.

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

## 대용량 backfill 운영 스크립트 예시

수백만 건 이상을 처리할 때는 migration 함수 내부 로직만으로는 관측성이 부족합니다. 아래처럼 실행 로그를 명확히 남기면 중단 지점을 파악하기 쉬워집니다.

```python
from sqlalchemy import text
from alembic import op

def upgrade() -> None:
    bind = op.get_bind()
    batch_size = 2000
    total = 0

    while True:
        result = bind.execute(text(
            """
            UPDATE users
               SET tier = CASE
                   WHEN last_payment_at IS NOT NULL THEN 'paid'
                   ELSE 'free'
               END
             WHERE id IN (
                 SELECT id FROM users
                  WHERE tier IS NULL
                  ORDER BY id
                  LIMIT :n
             )
            """
        ), {"n": batch_size})

        changed = result.rowcount or 0
        total += changed
        if changed == 0:
            break

    remaining = bind.execute(text("SELECT COUNT(*) FROM users WHERE tier IS NULL")).scalar_one()
    assert remaining == 0, f"backfill incomplete: {remaining}"
```

여기서 `ORDER BY id`를 넣는 이유는 배치 스캔 패턴을 안정화하기 위해서입니다. 데이터 분포가 불균등한 테이블에서 순서 없는 `LIMIT`만 사용하면 실행마다 처리 집합이 흔들려 관측이 어려워집니다.

## schema/data 분리 시 revision 의존성

3단계 분리 패턴에서 revision 의존성을 명확히 적어 두면 사고 분석이 쉬워집니다.

```text
rev_a_add_users_tier_nullable
  -> rev_b_backfill_users_tier
      -> rev_c_tighten_users_tier_not_null
```

이렇게 이름만 읽어도 현재 단계가 expand/migrate/contract 중 어디인지 보이게 하는 것이 중요합니다. 사고 시점에 `current`가 `rev_b`라면 "데이터 채우는 중"이라는 맥락을 즉시 얻을 수 있습니다.

## 실패 시 복구 전략

data migration이 중간에 실패하면 일반적으로 다음 순서로 대응합니다.

1. `alembic current`로 멈춘 revision 확인
2. 검증 쿼리(`NULL` 개수, 불일치 개수)로 부분 완료 상태 파악
3. 같은 revision 재실행이 안전한지(idempotent) 확인
4. 필요하면 forward-fix revision으로 보정

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
SELECT tier, COUNT(*) FROM users GROUP BY tier;
```

핵심은 "되감기"보다 "정방향 복구"입니다. 데이터 변경은 대체로 비가역이므로 downgrade보다 forward-fix가 안전합니다.

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

## 처음 질문으로 돌아가기

- **data migration은 schema migration과 무엇이 다를까요?**
  - schema migration은 `op.add_column()`처럼 구조를 바꾸는 작업이고, data migration은 `UPDATE users SET tier = 'free'`처럼 이미 있는 row 값을 바꾸는 작업입니다. 그래서 본문도 schema add, backfill, schema tighten을 서로 다른 revision으로 나누라고 권했습니다.
- **`op.execute`는 raw SQL과 SQLAlchemy Core 중 어떤 스타일로 쓸 수 있을까요?**
  - 간단한 한 줄이면 raw SQL이 빠르지만, `table("users", column("tier", String))`처럼 SQLAlchemy Core로 쓰면 dialect 차이에 덜 묶이고 의도가 더 또렷해집니다. 본문이 live 모델 import를 피하고 inline table/column 정의를 쓴 이유도 과거 migration을 미래 모델 변화에서 분리하기 위해서입니다.
- **큰 데이터셋은 어떤 batch 패턴으로 나누어 처리해야 할까요?**
  - 본문 예시처럼 `LIMIT 1000`으로 `id` 묶음을 끊어 `while True` 루프로 backfill하는 방식이 기본입니다. 한 번에 100M row를 업데이트하기보다 batch로 나누어 lock과 transaction log를 줄이는 것이 핵심입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성](./03-first-revision-upgrade-downgrade.md)
- [Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계](./04-autogenerate-and-its-limits.md)
- [Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법](./05-branches-and-merges.md)
- **데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기 (현재 글)**
- online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 (예정)
- downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 (예정)
- 배포 순서와 blue/green: schema와 application code의 안전한 동기화 (예정)
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Operation Reference (`op.execute`)](https://alembic.sqlalchemy.org/en/latest/ops.html#alembic.operations.Operations.execute)
- [Alembic: Run Code at Migration Time](https://alembic.sqlalchemy.org/en/latest/cookbook.html#run-arbitrary-python-during-migrations)
- [SQLAlchemy: SQL Expression Language Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html)
- [Alembic: Working With Custom Types and Data](https://alembic.sqlalchemy.org/en/latest/cookbook.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/06-data-migrations)

Tags: Python, Alembic, SQLAlchemy, Migration
