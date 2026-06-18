---
title: "바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드"
series: alembic-101
episode: 7
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

# 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 일곱 번째 글입니다.

---

DBA가 "production에는 직접 `alembic upgrade head`를 치면 안 되고, SQL 스크립트를 먼저 검토해야 한다"고 말합니다. 그런데 어떻게 실제로 적용하지 않고 SQL만 뽑아낼 수 있을까요? 혹은 SQLite로 개발 중인데 `ALTER TABLE`이 계속 실패합니다. 이 두 상황 모두 Alembic의 offline 모드와 batch 모드를 알면 해결됩니다.

바이브코딩 팀에서 AI는 항상 online 모드(`alembic upgrade head`)를 안내합니다. 하지만 production 배포에서는 `--sql` 옵션으로 DDL을 먼저 검토하는 것이 표준입니다. AI가 만든 revision이 실제로 어떤 SQL을 실행하는지 배포 전에 확인하세요.

SQLite 사용 중이라면 `batch_alter_table`이 필수입니다. SQLite는 컬럼 변경/삭제를 직접 지원하지 않아 Alembic이 임시 테이블을 만들고 데이터를 복사하는 방식으로 처리합니다.

> **핵심 인사이트:** production 배포 전에는 `alembic upgrade head --sql > review.sql`로 실행될 DDL을 반드시 확인하세요. SQLite 프로젝트에서는 컬럼 변경 시 `batch_alter_table`을 사용해야 합니다.

## 이 글에서 다룰 문제

- online 모드와 offline 모드(`--sql`)의 차이는 무엇인가요?
- production 배포 전에 DDL을 검토하는 워크플로우는 어떻게 만들까요?
- SQLite에서 컬럼 변경이 실패하는 이유와 `batch_alter_table` 해결법은?
- `--sql` 출력에서 확인해야 할 위험 신호는 무엇인가요?
- CI 파이프라인에서 offline 모드를 어떻게 활용할 수 있나요?

## --sql로 DDL 미리 확인

```bash
# 실제 적용 없이 SQL만 출력
alembic upgrade head --sql > review.sql

# 특정 구간의 SQL 출력
alembic upgrade <prev_rev>:<head_rev> --sql

# review.sql 확인 포인트:
# 1. DROP이 의도치 않게 포함되지 않았는가
# 2. ALTER TABLE이 안전한가 (락 발생 가능성)
# 3. alembic_version 업데이트 SQL이 포함되었는가
```

## SQLite batch_alter_table

```python
# SQLite에서 컬럼 추가/삭제 시 필요
def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("phone", sa.String(20), nullable=True))
        batch_op.drop_column("old_field")

def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("old_field", sa.String(100)))
        batch_op.drop_column("phone")
```

## 변경 전후 비교

**Before: production에 직접 실행**
```bash
alembic upgrade head  # 검토 없이 바로 적용, 롤백 불가
```

**After: 검토 후 적용**
```bash
alembic upgrade head --sql > review.sql  # SQL 확인
# 팀 리뷰 후
alembic upgrade head  # 적용
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| production에 검토 없이 upgrade | 의도치 않은 DDL 실행 | `--sql`로 먼저 확인 |
| SQLite에서 batch 미사용 | `ALTER TABLE` 실패 | `batch_alter_table` 사용 |
| `--sql` 없이 CI 통과 | DDL 품질 보장 불가 | CI에 `--sql` 출력 추가 |
| review.sql의 DROP 확인 생략 | 데이터 소실 | `grep DROP review.sql` 확인 |
| offline 모드에서 data migration | 데이터 접근 불가 | data migration은 online만 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"이 revision을 SQLite와 PostgreSQL 양쪽에서 동작하도록 만들어줘.
SQLite라면 batch_alter_table을 사용해줘"

# production 배포 스크립트:
alembic upgrade head --sql > /tmp/migration-$(date +%Y%m%d).sql
grep -i "DROP TABLE\|DROP COLUMN" /tmp/migration-*.sql && echo "WARNING: DROP detected"
```

## 운영 체크리스트

- [ ] production 배포 전에 `alembic upgrade head --sql`로 DDL을 확인한다
- [ ] `review.sql`에서 DROP, ALTER, 인덱스 재생성 여부를 확인한다
- [ ] SQLite 프로젝트에서는 컬럼 변경 시 `batch_alter_table`을 사용한다
- [ ] CI에서 `--sql` 출력을 artifact로 저장한다
- [ ] data migration은 offline 모드에서 실행할 수 없음을 인지한다

## 처음 질문으로 돌아가기

- **online과 offline 모드의 차이는?** online은 DB에 직접 연결해 실행하고, offline(`--sql`)은 SQL 스크립트만 생성합니다.
- **production 배포 전 DDL 검토 워크플로우는?** `--sql`로 SQL을 뽑고, DROP/위험 ALTER를 확인하고, 팀 리뷰 후 적용합니다.
- **SQLite에서 `batch_alter_table`이 필요한 이유는?** SQLite는 컬럼 변경/삭제를 직접 지원하지 않아 임시 테이블 방식이 필요합니다.

## 정리

`--sql` 옵션은 production 배포의 안전장치입니다. AI가 만든 revision이 실제로 어떤 SQL을 실행하는지 항상 확인하세요. 다음 글에서는 downgrade 전략, 즉 어떤 경우에 downgrade를 진심으로 준비하고 어떤 경우에 막아야 하는지를 다룹니다.

## 참고 자료

- [Alembic offline 모드](https://alembic.sqlalchemy.org/en/latest/offline.html)
- [SQLite batch operations](https://alembic.sqlalchemy.org/en/latest/batch.html)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- **바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드 (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
