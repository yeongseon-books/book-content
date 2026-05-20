---
title: "Alembic 101 (7/10): online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기"
series: alembic-101
episode: 7
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
- online
- offline
- batch
- SQLite
last_reviewed: '2026-05-12'
seo_description: alembic은 두 가지 모드로 실행됩니다. online은 DB에 직접 연결해 SQL을 실행하고, offline은 DB
  없이 SQL 텍스트만…
---

# Alembic 101 (7/10): online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기

이 글은 Alembic 101 시리즈의 일곱 번째 글입니다. 여기서는 online execution, offline SQL preview, 그리고 SQLite batch mode를 하나의 운영 흐름으로 묶어 설명합니다.

production 배포 직전에는 migration이 실제로 어떤 SQL을 내보낼지 눈으로 보고 싶을 때가 많습니다. 여기에 SQLite의 제한적인 DDL 지원까지 겹치면 offline mode와 batch mode를 같이 이해해야 합니다.

## 먼저 던지는 질문

- Alembic이 제공하는 두 실행 모드, online과 offline은 어떻게 다를까요?
- `--sql`로 실제 SQL을 어떻게 미리 볼 수 있을까요?
- DBA 리뷰용 SQL 스크립트는 어떤 흐름으로 만들까요?

## 큰 그림

![Alembic 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/07/07-01-diagram-how-online-offline-and-batch-mod.ko.png)

*Alembic 101 7장 흐름 개요*

이 그림에서는 online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

외부 DBA 검토가 필요하거나 변경 영향이 커서 PR 리뷰만으로는 불안할 때, migration이 실제로 어떤 SQL을 실행할지 미리 봐야 합니다. 이때 쓰는 도구가 Alembic의 offline mode입니다.

또 SQLite는 `ALTER TABLE` 지원이 약하기 때문에 결국 모든 Alembic 사용자는 batch mode를 익히게 됩니다. 두 주제는 함께 배울 때 가장 이해가 빠릅니다.

## 멘탈 모델

> Alembic은 두 모드로 실행됩니다. **online은 DB에 연결해 SQL을 직접 실행하고, offline은 DB 연결 없이 SQL 텍스트를 표준 출력으로 보냅니다.** offline은 dry-run, 리뷰, 스크립트화용이고, online은 실제 적용용입니다.

`render_as_batch`를 켜면 SQLite에서 `op.alter_column` 같은 호출이 내부적으로 “임시 테이블 생성 → INSERT SELECT → 이름 교체”로 확장됩니다. batch mode는 SQLite를 위한 Alembic의 안전망입니다.

### 다이어그램: online, offline, batch mode의 역할 분담

## 핵심 개념

### online vs offline

| 모드 | DB 연결 | 출력 | 용도 |
| --- | --- | --- | --- |
| online (기본) | 필요 | 적용 로그 | 실제 migration 적용 |
| offline (`--sql`) | 불필요 | SQL 텍스트 (stdout) | 리뷰, 스크립트, dry-run |

```bash
# online (apply)
alembic upgrade head

# offline (SQL only)
alembic upgrade head --sql > migration.sql

# only a specific span
alembic upgrade <from>:<to> --sql > step.sql
```

여기서 반드시 기억할 문법은 `<from>:<to>`입니다. `head`만 쓰면 `None:head`로 해석되어 처음부터 head까지의 SQL이 모두 출력됩니다. 이미 적용된 구간을 빼고 싶다면 `<current>:<target>`을 명시해야 합니다.

### offline mode의 제약

DB 연결이 없기 때문에 offline mode에서는 다음이 동작하지 않습니다.

- `op.get_bind()`
- 데이터 검증 쿼리
- introspection 기반 helper
- row 수에 따라 분기하는 조건 로직

따라서 data migration은 offline mode에서 의미 있는 SQL을 내기 어렵습니다. offline은 schema migration 중심으로 쓰는 것이 맞습니다.

### `--sql` 리뷰 워크플로우

```bash
# 1) attach an SQL preview to the PR
alembic upgrade <prev>:head --sql > review.sql
git add review.sql && git commit -m "ddl preview"

# 2) DBA reviews review.sql

# 3) production deploy uses online as usual
alembic upgrade head
```

실제 운영에서는 이 흐름이 자주 쓰입니다. `op` 호출이 아니라 실제 SQL을 PR에 붙여 두면 리뷰어가 비용과 위험을 더 정확히 읽을 수 있습니다.

### SQLite와 batch mode

SQLite가 지원하는 `ALTER TABLE`은 다음 정도에 그칩니다.

- `RENAME TABLE`
- `RENAME COLUMN` (3.25+)
- `ADD COLUMN`
- `DROP COLUMN` (3.35+)

따라서 타입 변경, nullable 변경, default 변경, FK 추가/삭제는 직접 ALTER로 처리할 수 없습니다. Alembic의 `batch_alter_table`은 이를 다음처럼 확장합니다.

```sql
CREATE TABLE _alembic_tmp_users (...);   -- temp table with the new schema
INSERT INTO _alembic_tmp_users SELECT ... FROM users;
DROP TABLE users;
ALTER TABLE _alembic_tmp_users RENAME TO users;
-- recreate the original indexes/triggers
```

이 전체 과정은 한 transaction 안에서 일어나기 때문에 안전하지만, 큰 테이블에서는 비용이 큽니다.

### `render_as_batch` 자동화

`env.py`에서는 SQLite일 때만 자동으로 batch mode를 켜면 됩니다.

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=connection.dialect.name == "sqlite",
)
```

그래도 `with op.batch_alter_table(...)`를 명시적으로 쓰는 편이 좋습니다. 의도가 분명해지고, 여러 변경을 하나의 batch로 묶을 수 있기 때문입니다.

## 변경 전후

```sql
-- Before: applied to production without looking at the SQL
-- Result: column type changed without dropping the index, query performance regresses
```

```bash
# After: previewed with --sql
$ alembic upgrade <prev>:head --sql

BEGIN;
-- Running upgrade abc123 -> def456, change users.tier type
DROP INDEX ix_users_tier;
ALTER TABLE users ALTER COLUMN tier TYPE VARCHAR(64);
CREATE INDEX ix_users_tier ON users (tier);
COMMIT;
```

이 SQL이 PR에 붙어 있었다면 “인덱스를 드롭하고 다시 만든다”는 비용을 리뷰 단계에서 바로 볼 수 있었을 것입니다. 그것이 dry-run workflow의 가치입니다.

## 단계별 실습

### 1단계: offline SQL 출력

```bash
alembic upgrade head --sql > preview.sql
cat preview.sql
```

처음 보면 `BEGIN;` ... `COMMIT;` 블록과 `INSERT INTO alembic_version` 문까지 포함된다는 점이 눈에 들어옵니다.

### 2단계: 특정 revision 구간만 출력

```bash
alembic upgrade abc123:def456 --sql > step.sql
```

production이 이미 `abc123`에 있고 `def456`까지만 올리고 싶을 때 쓰는 형태입니다.

### 3단계: SQLite batch 적용

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier",
                           existing_type=sa.String(16),
                           type_=sa.String(64))
        batch.create_index("ix_users_tier", ["tier"])
```

여러 변경을 하나의 batch로 묶으면 임시 테이블 생성과 데이터 복사가 한 번만 일어납니다.

### 4단계: offline에서 동작하지 않는 연산 구분

```python
def upgrade() -> None:
    bind = op.get_bind()                  # None in offline mode
    if bind:                              # add a guard
        bind.execute(text("UPDATE ..."))
```

혹은 data migration을 별도 revision으로 분리하고, offline에서는 schema-only revision만 preview하는 편이 더 깔끔합니다.

### 5단계: CI에 `--sql` dry-run 추가

```yaml
- run: alembic upgrade head --sql > /tmp/preview.sql && cat /tmp/preview.sql
```

이 한 줄만으로도 모든 PR에서 SQL이 자동 출력됩니다.

## 검증 루틴

```bash
alembic upgrade current:head --sql > preview.sql
python3 - <<'PY'
from pathlib import Path
text = Path('preview.sql').read_text()
print('BEGIN;' in text, 'INSERT INTO alembic_version' in text)
PY
```

**확인할 점:** preview SQL 안에 transaction 경계와 `alembic_version` 갱신 SQL이 함께 보여야 합니다. 그래야 리뷰 대상이 실제 배포 단위와 맞아 있습니다.

## 자주 하는 실수

- **`--sql head`를 실행하고 처음부터 끝까지 다 출력돼 놀라기.** `<from>:<to>` 구문을 익혀야 합니다.
- **offline에서 data migration SQL까지 기대하기.** offline은 주로 schema 변경용입니다.
- **SQLite에서 batch 없이 ALTER하기.** 지원되지 않는 문법 오류를 만납니다.
- **batch mode의 임시 테이블 비용을 무시하기.** 큰 테이블은 6편의 schema add → data backfill → schema tighten 패턴이 더 안전합니다.
- **`render_as_batch=True`만 믿고 explicit batch context를 생략하기.** 의도가 흐려지고 batch bundling 효과도 놓칩니다.

## 실무 패턴

- **PR에 `--sql` preview를 붙입니다.** DBA 리뷰가 필요한 환경에서는 사실상 표준입니다.
- **CI가 dry-run SQL을 자동 출력합니다.** 리뷰 비용을 줄여 줍니다.
- **SQLite schema 변경은 항상 batch context 안에 씁니다.** PostgreSQL과 동작 차이를 코드에 명시할 수 있습니다.
- **production deploy는 online + transaction으로 수행합니다.** offline SQL 파일을 수동으로 돌리면 transaction 경계와 `alembic_version` 동기화 리스크가 생깁니다.
- **`alembic upgrade <prev>:head --sql`을 `make ddl-preview` 같은 명령으로 고정합니다.** 팀 전체의 습관을 표준화하기 쉽습니다.

## 체크리스트

- [ ] `--sql`을 쓸 때 `<from>:<to>` 구문을 이해하고 있다
- [ ] offline mode에서 data migration 결과를 기대하지 않는다
- [ ] SQLite의 `ALTER` 계열 변경은 항상 `batch_alter_table` 안에서 실행한다
- [ ] SQL preview를 PR에 붙이거나 CI에서 자동 출력한다
- [ ] production deploy는 online 모드로 수행한다

## 연습 문제

1. 임의의 schema 변경을 만들고 `alembic upgrade head --sql > out.sql`로 출력 구조를 확인해 보세요.
2. SQLite에서 `op.alter_column`을 batch context 없이 실행해 오류를 관찰해 보세요.
3. `<prev>:<head>` 구문으로 마지막 한 단계의 SQL만 뽑아 보세요.

## 정리, 다음 글

online은 적용용이고 offline은 리뷰용입니다. 이 역할 분담을 분명히 하면 운영 안전성이 크게 올라갑니다. SQLite를 쓴다면 batch mode를 항상 명시적으로 쓰는 습관을 들이는 편이 좋습니다.

다음 글에서는 downgrade를 언제 진지하게 작성하고, 언제 의도적으로 막아야 하는지 다룹니다.

## 처음 질문으로 돌아가기

- **Alembic이 제공하는 두 실행 모드, online과 offline은 어떻게 다를까요?**
  - 본문의 기준은 online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`--sql`로 실제 SQL을 어떻게 미리 볼 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **DBA 리뷰용 SQL 스크립트는 어떤 흐름으로 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성](./03-first-revision-upgrade-downgrade.md)
- [Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계](./04-autogenerate-and-its-limits.md)
- [Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법](./05-branches-and-merges.md)
- [Alembic 101 (6/10): 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기](./06-data-migrations.md)
- **online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 (현재 글)**
- downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 (예정)
- 배포 순서와 blue/green: schema와 application code의 안전한 동기화 (예정)
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Generating SQL Scripts (Offline Mode)](https://alembic.sqlalchemy.org/en/latest/offline.html)
- [Alembic: Running Batch Migrations for SQLite and Other Databases](https://alembic.sqlalchemy.org/en/latest/batch.html)
- [SQLite: ALTER TABLE](https://www.sqlite.org/lang_altertable.html)
- [Alembic: Operation Reference](https://alembic.sqlalchemy.org/en/latest/ops.html)

Tags: Python, Alembic, SQLAlchemy, Migration
