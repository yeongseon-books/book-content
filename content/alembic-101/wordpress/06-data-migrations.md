---
title: "바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션"
series: alembic-101
episode: 6
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Python
  - Alembic
  - SQLAlchemy
  - Migration
  - DB마이그레이션
---

# 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 여섯 번째 글입니다.

---

AI가 "기존 users.name을 first_name과 last_name으로 분리해줘"라는 요청을 처리합니다. 모델 코드에는 `first_name`, `last_name`이 생기고, `name` 컬럼은 사라집니다. autogenerate를 실행하면 `ADD COLUMN first_name`, `ADD COLUMN last_name`, `DROP COLUMN name`이 나옵니다. 이 revision을 그대로 적용하면 production에 있는 수백만 명의 이름 데이터가 순식간에 사라집니다.

schema 변경과 데이터 이전은 반드시 분리해야 합니다. 바이브코딩에서 AI는 종종 이 두 단계를 하나의 revision에 합쳐버립니다. AI에게 "schema 변경과 데이터 backfill을 별도 revision으로 분리해줘"라고 명시적으로 요청해야 합니다.

데이터 마이그레이션의 세 단계는: 1) 새 컬럼 추가(nullable), 2) 데이터 backfill, 3) 기존 컬럼 제거입니다. 이 순서를 지키면 각 단계에서 롤백이 가능하고, 배포 중에도 서비스가 계속 동작합니다.

> **핵심 인사이트:** schema 변경과 데이터 이전은 항상 별도 revision입니다. AI에게 하나의 revision에 합치지 말라고 명시적으로 요청하세요. 데이터 backfill은 idempotent하게 작성해야 합니다.

## 이 글에서 다룰 문제

- schema 변경과 데이터 이전을 왜 분리해야 할까요?
- expand/migrate/contract 패턴은 무엇이고 왜 중요한가요?
- 데이터 backfill을 idempotent하게 작성하는 방법은 무엇인가요?
- 대용량 데이터 backfill 시 어떤 위험이 있고 어떻게 완화할까요?
- AI가 data migration revision을 만들 때 검토해야 할 것은 무엇인가요?

## expand/migrate/contract 패턴

```python
# Revision 1: Expand - 새 컬럼 추가 (nullable)
def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(100), nullable=True))

# Revision 2: Migrate - 데이터 backfill (idempotent)
def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE users
        SET first_name = split_part(name, ' ', 1),
            last_name = split_part(name, ' ', 2)
        WHERE first_name IS NULL  -- idempotent: 이미 처리된 행은 건너뜀
    """))

# Revision 3: Contract - 기존 컬럼 제거
def upgrade() -> None:
    op.drop_column("users", "name")
```

## 변경 전후 비교

**Before: 한 revision에 schema + 데이터 변경**
```python
def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(100)))
    op.add_column("users", sa.Column("last_name", sa.String(100)))
    op.execute("UPDATE users SET first_name = name")  # 데이터 소실 위험!
    op.drop_column("users", "name")  # rollback 불가
```

**After: 3단계 분리**
- Revision N: ADD COLUMN first_name, last_name (nullable)
- Revision N+1: UPDATE users SET ... WHERE first_name IS NULL
- Revision N+2: DROP COLUMN name (검증 후)

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| schema + 데이터를 한 revision에 | rollback 불가, 데이터 소실 위험 | 3단계로 분리 |
| idempotent 조건 없음 | 재실행 시 중복 처리 | `WHERE ... IS NULL` 조건 추가 |
| 대용량 업데이트를 한 번에 | 테이블 락, 타임아웃 | 배치 처리 |
| contract 전 검증 생략 | 데이터 소실 | `COUNT(*) WHERE = 0` 확인 |
| downgrade에서 삭제된 데이터 복원 불가 | 되돌릴 수 없음 | irreversible 명시 또는 백업 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"users.name을 first_name, last_name으로 분리하는 migration을
expand/migrate/contract 3단계 revision으로 만들어줘.
각 단계는 별도 revision 파일이어야 해"

# 검토 체크리스트:
# 1. backfill UPDATE가 WHERE 조건으로 idempotent한가
# 2. contract(DROP) 전에 NULL 검사가 있는가
# 3. 대용량이면 배치 처리가 있는가
```

## 운영 체크리스트

- [ ] schema 변경과 데이터 이전이 별도 revision이다
- [ ] backfill SQL이 idempotent하게 작성되었다 (`WHERE ... IS NULL`)
- [ ] contract 단계 전에 NULL 데이터가 없는지 확인한다
- [ ] 대용량 backfill은 배치로 처리한다
- [ ] 각 단계에서 rollback이 가능한지 확인한다

## 처음 질문으로 돌아가기

- **schema 변경과 데이터 이전을 왜 분리해야 할까요?** 각 단계에서 독립적 롤백이 가능하고, 배포 중 서비스가 계속 동작합니다.
- **idempotent backfill이란?** 같은 revision을 여러 번 실행해도 동일한 결과가 나오도록 `WHERE first_name IS NULL` 같은 조건을 추가하는 것입니다.
- **AI에게 명시적으로 요청해야 하는 것은?** "schema와 데이터를 분리", "idempotent 조건 추가", "대용량이면 배치 처리"를 명시합니다.

## 정리

데이터 마이그레이션은 바이브코딩에서 가장 위험한 작업입니다. AI가 편의를 위해 한 revision에 모든 것을 넣으려 할 때, 개발자가 3단계로 분리하도록 명시적으로 요청해야 합니다. 다음 글에서는 online과 offline 모드, 그리고 `--sql` 옵션으로 DDL을 미리 검토하는 방법을 다룹니다.

## 참고 자료

- [Alembic 데이터 마이그레이션](https://alembic.sqlalchemy.org/en/latest/ops.html#alembic.operations.Operations.execute)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/06-data-migrations)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- **바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션 (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
