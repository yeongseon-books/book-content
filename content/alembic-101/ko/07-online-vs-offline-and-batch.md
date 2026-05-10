---
title: 'online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기'
series: alembic-101
episode: 7
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
- online
- offline
- batch
- SQLite
last_reviewed: '2026-05-03'
seo_description: alembic은 두 가지 모드로 실행됩니다. online은 DB에 직접 연결해 SQL을 실행하고, offline은 DB
  없이 SQL 텍스트만…
---

# online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기

## 이 글에서 답할 질문

- alembic의 online 모드와 offline 모드는 각각 어떤 환경을 가정하는가?
- `--sql` 옵션으로 SQL을 미리 보고 DBA 검토를 받는 워크플로우는 어떻게 짜는가?
- SQLite의 ALTER 한계 때문에 `batch_alter_table`이 내부적으로 어떤 일을 대신 해 주는가?
- offline 모드에서 동작하지 않는 op 패턴에는 어떤 것이 있는가?
- online과 offline을 같은 revision으로 안전하게 운용하려면 무엇을 피해야 하는가?

## 이 글에서 다룰 문제

production 배포 전에 "이 마이그레이션이 어떤 SQL을 실행할지"를 보고 싶을 때가 있습니다. 외부 DBA의 검토를 받아야 하거나, 변경 영향이 너무 커서 PR review만으로는 안심이 안 될 때입니다. 이때 사용하는 도구가 alembic의 offline 모드입니다.

또 SQLite는 `ALTER TABLE`이 매우 제한적이라 모든 alembic 사용자가 batch 모드를 한 번은 배워야 합니다. 둘은 같이 익히는 편이 좋습니다.

## Mental Model

> alembic은 두 가지 모드로 실행됩니다. **online은 DB에 직접 연결해 SQL을 실행하고, offline은 DB 없이 SQL 텍스트만 표준출력에 찍습니다.** offline은 dry-run/검토/스크립트화를 위한 모드이고, online은 실제 적용 모드입니다.

`render_as_batch` 옵션을 켜면 SQLite 같은 dialect에서 `op.alter_column` 같은 호출이 내부에서 임시 테이블 + INSERT SELECT + 원본 교체로 풀립니다. batch 모드는 SQLite를 위한 alembic의 안전망입니다.

## 핵심 개념

### online vs offline

| 모드 | DB 연결 | 출력 | 용도 |
| --- | --- | --- | --- |
| online (기본) | 필요 | 적용 결과 로그 | 실제 마이그레이션 적용 |
| offline (`--sql`) | 불필요 | SQL 텍스트 (stdout) | 검토, 스크립트화, dry-run |

```bash
# online (실제 적용)
alembic upgrade head

# offline (SQL 출력만)
alembic upgrade head --sql > migration.sql

# 특정 구간만
alembic upgrade <from>:<to> --sql > step.sql
```

`<from>:<to>` 구문이 핵심입니다. `head` 단독은 `None:head` 의미가 되어 처음부터 head까지의 SQL이 다 출력됩니다. 이미 적용된 부분을 빼고 싶으면 `<현재>:<목표>`로 명시합니다.

### offline 모드의 제약

offline은 DB가 없으므로 다음이 동작하지 않습니다.

- `op.get_bind()` (커넥션이 없음)
- 데이터 검증 쿼리
- introspection을 사용하는 helper
- 조건부 로직 (현재 row 수에 따라 분기 등)

따라서 데이터 마이그레이션은 offline 모드에서 SQL이 의미 있게 출력되지 않습니다. schema 마이그레이션 위주로 사용하는 것이 정석입니다.

### `--sql`로 검토 워크플로우

```bash
# 1) PR에 SQL preview 첨부
alembic upgrade <prev>:head --sql > review.sql
git add review.sql && git commit -m "ddl preview"

# 2) DBA가 review.sql을 검토

# 3) production 배포는 평소와 같이 online
alembic upgrade head
```

대규모 운영 환경에서 자주 사용하는 흐름입니다. PR에 SQL을 첨부해 두면 리뷰어가 op 호출이 아닌 실제 SQL로 영향을 평가할 수 있습니다.

### SQLite와 batch 모드

SQLite는 `ALTER TABLE`이 다음만 지원합니다.

- `RENAME TABLE`
- `RENAME COLUMN` (3.25+)
- `ADD COLUMN`
- `DROP COLUMN` (3.35+)

따라서 type 변경, nullable 변경, default 변경, FK 추가/삭제는 직접 ALTER로 못 합니다. alembic의 `batch_alter_table`은 다음과 같이 자동으로 풀어 줍니다.

```sql
CREATE TABLE _alembic_tmp_users (...);   -- 새 schema로 임시 테이블
INSERT INTO _alembic_tmp_users SELECT ... FROM users;
DROP TABLE users;
ALTER TABLE _alembic_tmp_users RENAME TO users;
-- 원래 인덱스/트리거 재생성
```

이 과정 전체가 한 트랜잭션 안에서 일어나기 때문에 안전하지만, 큰 테이블에서는 시간이 걸립니다.

### `render_as_batch` 자동화

`env.py`에서 SQLite일 때만 자동으로 batch 모드가 켜지게 합니다.

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=connection.dialect.name == "sqlite",
)
```

이 옵션이 있어도 명시적 `with op.batch_alter_table(...)` 컨텍스트는 여전히 권장됩니다. 의도가 명확해지고, 같은 batch 안에서 여러 alter를 묶을 수 있기 때문입니다.

## Before-After

```sql
-- Before: SQL을 보지 않고 production에 적용
-- 결과: index drop이 누락된 채 column type 변경, 쿼리 성능 저하
```

```bash
# After: --sql로 미리 확인
$ alembic upgrade <prev>:head --sql

BEGIN;
-- Running upgrade abc123 -> def456, change users.tier type
DROP INDEX ix_users_tier;
ALTER TABLE users ALTER COLUMN tier TYPE VARCHAR(64);
CREATE INDEX ix_users_tier ON users (tier);
COMMIT;
```

PR에 이 SQL이 첨부되어 있었다면 리뷰어가 "DROP INDEX 후 다시 만드는 비용"을 평가할 수 있었을 겁니다. dry-run 워크플로우의 가치는 여기에 있습니다.

## 단계별 실습

### 1단계: offline SQL 출력

```bash
alembic upgrade head --sql > preview.sql
cat preview.sql
```

처음 사용 시에는 `BEGIN;` ... `COMMIT;` 블록과 `INSERT INTO alembic_version` 문장도 포함되는 것을 확인할 수 있습니다.

### 2단계: 특정 revision 구간만

```bash
alembic upgrade abc123:def456 --sql > step.sql
```

이미 production에 abc123까지 적용되어 있고 def456까지 올리고 싶을 때 사용합니다.

### 3단계: SQLite batch 적용

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier",
                           existing_type=sa.String(16),
                           type_=sa.String(64))
        batch.create_index("ix_users_tier", ["tier"])
```

여러 변경을 한 batch로 묶으면 임시 테이블 생성/복사가 한 번에 끝납니다.

### 4단계: offline에서 동작 안 하는 op 식별

```python
def upgrade() -> None:
    bind = op.get_bind()                  # offline에서는 None
    if bind:                              # 가드 추가
        bind.execute(text("UPDATE ..."))
```

또는 데이터 마이그레이션은 별도 revision으로 분리하고 offline 모드에서는 schema-only revision만 미리 보는 식으로 운영합니다.

### 5단계: CI에 `--sql` dry-run 추가

```yaml
- run: alembic upgrade head --sql > /tmp/preview.sql && cat /tmp/preview.sql
```

이 한 줄이 PR에 SQL을 자동으로 표시하는 효과를 줍니다.

## 자주 하는 실수

- **`--sql head`만 실행해 처음부터 끝까지가 다 나오는 것에 당황.** `<from>:<to>` 형식을 익히세요.
- **offline에서 데이터 마이그레이션 SQL을 기대.** offline은 schema 변경 위주로만 의미 있는 출력을 만듭니다.
- **SQLite에서 batch 없이 alter.** "no such function ALTER" 또는 "syntax error"로 깨집니다.
- **batch 모드의 임시 테이블 시간 무시.** 수백만 row 테이블이라면 schema add → data backfill → schema tighten 분리(6편) 패턴이 더 안전합니다.
- **`render_as_batch=True`만 믿고 명시적 batch 컨텍스트 생략.** 의도가 모호해지고 한 batch 묶음 효과를 못 받습니다.

## 실무에서 쓰는 패턴

- **PR에 `--sql` preview 첨부.** DBA 리뷰가 필요한 환경의 표준.
- **CI에서 `--sql`로 dry-run을 자동 출력.** 리뷰어 부담을 낮춥니다.
- **schema 변경은 SQLite에서 항상 batch 컨텍스트로 작성.** PostgreSQL과 동작이 다르다는 사실을 명시적으로 표현.
- **production 배포는 online + transaction.** offline에서 만든 SQL 파일을 손으로 실행하는 운영은 권장하지 않습니다(트랜잭션 경계와 alembic_version 동기화 위험).
- **`alembic upgrade <prev>:head --sql` alias.** `make ddl-preview` 같은 단일 명령으로 정형화.

## 체크리스트

- [ ] `--sql`은 `<from>:<to>` 구문으로 사용한다
- [ ] offline에서는 데이터 마이그레이션 결과를 기대하지 않는다
- [ ] SQLite의 `ALTER` 변경은 항상 `batch_alter_table` 컨텍스트 안에서 한다
- [ ] PR에 SQL preview 첨부 또는 CI 자동 출력이 설정되어 있다
- [ ] production 배포는 online으로 한다 (offline SQL 직접 실행 금지)

## 정리, 다음 글

online은 적용, offline은 검토. 이 두 모드의 분업이 운영 환경에서 안전성을 높여 줍니다. SQLite는 batch 모드를 항상 명시적으로 쓰는 습관을 들이세요.

다음 글은 downgrade 전략입니다. 언제 downgrade를 진심으로 작성하고, 언제 의도적으로 막을지의 기준을 다룹니다.

## 참고 자료

- Alembic: Generating SQL Scripts (Offline Mode) — https://alembic.sqlalchemy.org/en/latest/offline.html
- Alembic: Running Batch Migrations for SQLite and Other Databases — https://alembic.sqlalchemy.org/en/latest/batch.html
- SQLite: ALTER TABLE — https://www.sqlite.org/lang_altertable.html
- Alembic: Operation Reference — https://alembic.sqlalchemy.org/en/latest/ops.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, online, offline, batch, SQLite
