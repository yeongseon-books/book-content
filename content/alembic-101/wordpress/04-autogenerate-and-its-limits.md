---
title: "바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계"
series: alembic-101
episode: 4
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

# 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 네 번째 글입니다.

---

AI에게 "모든 모델 변경에 대해 Alembic migration을 자동으로 만들어줘"라고 부탁하면 자신 있게 `alembic revision --autogenerate`를 사용하라고 안내합니다. 그리고 대부분의 경우 잘 동작합니다. 그런데 어느 날 stored procedure를 바꿨는데 revision이 비어 있고, view를 추가했는데 아무 변화가 없고, 체크 제약조건을 걸었는데 감지가 안 됩니다.

autogenerate는 강력하지만 만능이 아닙니다. 특히 바이브코딩에서 AI는 "autogenerate가 잡을 수 없는" 변경을 아무렇지 않게 만들어 냅니다. AI는 SQLAlchemy ORM이 표현할 수 없는 DB 수준의 객체(view, trigger, stored procedure, partial index 등)를 모델 코드에 직접 넣지 않기 때문입니다.

autogenerate가 잡는 것과 못 잡는 것의 경계를 알면, AI가 만든 변경을 검토할 때 무엇을 직접 revision에 추가해야 하는지 알 수 있습니다.

> **핵심 인사이트:** autogenerate는 SQLAlchemy ORM이 표현할 수 있는 것만 감지합니다. view, trigger, stored procedure, partial index는 직접 revision에 추가해야 합니다. AI에게 "autogenerate가 못 잡는 변경도 revision에 포함시켜줘"라고 명시적으로 요청하세요.

## 이 글에서 다룰 문제

- autogenerate가 감지하는 변경과 못 하는 변경은 어떻게 구분할까요?
- view, trigger, stored procedure는 왜 autogenerate로 잡을 수 없을까요?
- AI가 만든 모델 코드를 autogenerate로 처리할 때 놓칠 수 있는 것은 무엇인가요?
- autogenerate 결과를 검토하는 최소 리뷰 기준은 무엇인가요?
- partial index와 함수 기반 index는 어떻게 revision에 추가할까요?

## autogenerate가 잡는 것과 못 잡는 것

| 구분 | 잡는 것 | 못 잡는 것 |
|------|---------|------------|
| 테이블 | 추가, 삭제 | - |
| 컬럼 | 추가, 삭제, 타입 변경 | 일부 타입 세부사항 |
| 인덱스 | 기본 인덱스 | partial index, 함수 기반 index |
| 제약조건 | NOT NULL, UNIQUE, FK | CHECK 제약조건 |
| DB 객체 | - | view, trigger, stored procedure |
| 시퀀스 | - | 커스텀 시퀀스 |

## 변경 전후 비교

**Before: autogenerate 결과를 무검토 적용**
```bash
alembic revision --autogenerate -m "add view"
# upgrade()가 비어 있음 - view가 없음!
alembic upgrade head  # view가 실제로 생성 안 됨
```

**After: 수동으로 view 추가**
```python
def upgrade() -> None:
    op.execute("""
        CREATE VIEW active_users AS
        SELECT * FROM users WHERE is_active = true
    """)

def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS active_users")
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| autogenerate 결과 무검토 | 중요한 변경이 누락됨 | 생성 후 반드시 diff 확인 |
| view를 ORM으로 관리 기대 | autogenerate 미감지 | `op.execute()`로 직접 작성 |
| CHECK 제약 누락 | DB 무결성 보장 불가 | 수동으로 revision에 추가 |
| 빈 upgrade() 배포 | 실제 변경이 없음 | `alembic upgrade head --sql`로 미리 확인 |
| partial index 미추가 | 성능 최적화 누락 | `op.create_index(postgresql_where=...)` |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"active_users view를 만드는 alembic revision을 추가해줘.
autogenerate가 view를 못 잡으니 op.execute()로 직접 작성해줘"

# 검토 체크리스트:
# autogenerate 결과 파일에서 확인:
# 1. 의도한 테이블/컬럼 변경이 모두 있는가
# 2. view/trigger/stored proc이 있다면 수동 추가되었는가
# 3. partial index나 함수 index가 있다면 포함되었는가
```

## 운영 체크리스트

- [ ] autogenerate 후 `git diff alembic/versions`로 변경 내용을 확인한다
- [ ] `upgrade()`가 비어 있으면 감지 못한 변경이 있는지 확인한다
- [ ] view, trigger, stored procedure는 수동으로 revision에 추가한다
- [ ] `alembic upgrade head --sql`로 실행될 DDL을 미리 확인한다
- [ ] CHECK 제약조건은 autogenerate 결과에서 빠질 수 있음을 인지한다

## 처음 질문으로 돌아가기

- **autogenerate가 감지하는 것과 못 하는 것의 경계는?** SQLAlchemy ORM이 표현할 수 있는 것만 감지합니다. view, trigger, stored procedure, partial index는 직접 추가해야 합니다.
- **AI가 만든 변경을 처리할 때 놓칠 수 있는 것은?** AI는 종종 view와 trigger를 별도 SQL로 만듭니다. 이것이 revision에 포함되지 않으면 누락됩니다.
- **autogenerate 결과 검토 기준은?** upgrade()가 비어 있지 않은지, 의도한 변경이 모두 포함되었는지, DROP이 의도치 않게 섞이지 않았는지 확인합니다.

## 정리

autogenerate는 바이브코딩의 속도를 유지하면서도 migration을 관리하는 강력한 도구입니다. 하지만 그 한계를 알고 사용해야 합니다. 다음 글에서는 여러 사람이 동시에 revision을 만들 때 발생하는 branch와 merge를 다룹니다.

## 참고 자료

- [Alembic autogenerate 문서](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/04-autogenerate-and-its-limits)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- **바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계 (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
