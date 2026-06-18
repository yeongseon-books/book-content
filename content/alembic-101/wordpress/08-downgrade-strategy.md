---
title: "바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략"
series: alembic-101
episode: 8
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

# 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 여덟 번째 글입니다.

---

새벽 3시, production 배포 후 치명적인 버그가 발견됩니다. "rollback하자"는 말이 나옵니다. 코드는 git revert로 되돌릴 수 있습니다. 그런데 DB는? `alembic downgrade -1`을 치면 "downgrade() not implemented"가 뜹니다. AI가 만든 revision의 `downgrade()`가 `pass`였기 때문입니다.

downgrade는 "있으면 좋은 것"이 아니라 production 운영의 필수 안전장치입니다. 그런데 바이브코딩에서 AI는 종종 `downgrade()`를 빈 함수로 만들거나 "구현하기 어렵다"며 생략합니다. 특히 데이터를 삭제하는 `downgrade()`는 더 어렵지만, 바로 그 어려움이 사고 시 가장 필요한 부분입니다.

어떤 경우에는 downgrade가 진짜로 불가능할 수 있습니다. 데이터를 삭제한 revision은 되돌리면 데이터를 복원해야 하는데, backup 없이는 불가능합니다. 이런 경우에는 `downgrade()`에 `raise NotImplementedError("irreversible migration")`를 명시적으로 넣어야 합니다.

> **핵심 인사이트:** 모든 revision의 `downgrade()`는 "진심으로 작성"하거나 "명시적으로 irreversible 선언"해야 합니다. 빈 `pass`는 거짓 안전감을 줍니다.

## 이 글에서 다룰 문제

- 어떤 revision은 downgrade를 진심으로 써야 하고, 어떤 경우에는 막아야 할까요?
- irreversible migration을 명시적으로 표시하는 패턴은 무엇인가요?
- 데이터를 삭제하는 revision의 downgrade는 어떻게 처리할까요?
- production에서 downgrade 정책을 팀 규칙으로 만드는 방법은?
- AI가 만든 revision의 `downgrade()`를 검토하는 기준은?

## downgrade 패턴

```python
# 패턴 1: 완전한 reversible
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16)))

def downgrade() -> None:
    op.drop_column("users", "tier")  # 정확한 역순

# 패턴 2: 명시적 irreversible
def upgrade() -> None:
    op.drop_column("users", "old_field")  # 데이터 소실

def downgrade() -> None:
    raise NotImplementedError(
        "irreversible: old_field data was dropped. Restore from backup."
    )

# 패턴 3: 부분 reversible
def downgrade() -> None:
    # schema는 되돌릴 수 있지만 데이터는 복원 불가
    op.add_column("users", sa.Column("old_field", sa.String(100), nullable=True))
    # 주석: 데이터는 backup에서 수동 복원 필요
```

## 변경 전후 비교

**Before: 빈 downgrade**
```python
def downgrade() -> None:
    pass  # 거짓 안전감 - upgrade를 되돌릴 수 없음
```

**After: 명시적 처리**
```python
def downgrade() -> None:
    # reversible이면: 역순 DDL
    op.drop_column("users", "tier")

    # irreversible이면: 명시적 선언
    # raise NotImplementedError("irreversible migration")
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `downgrade()`가 `pass` | 사고 시 롤백 불가 | reversible이면 역순 작성 |
| irreversible 미표시 | 사고 시 의미 없는 rollback 시도 | `raise NotImplementedError` |
| data migration downgrade 생략 | 데이터 소실 시 복구 경로 없음 | backup 정책과 연계 |
| 팀 downgrade 정책 없음 | 일관성 없는 migration | 팀 규칙 문서화 |
| production downgrade 무제한 허용 | 실수로 DB 과거 상태 적용 | production downgrade는 명시적 승인 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"이 upgrade()에 대응하는 downgrade()를 작성해줘.
데이터 소실이 있으면 NotImplementedError를 명시해줘.
절대 pass만 남기지 말아줘"

# 팀 규칙 예시:
# - 모든 revision은 downgrade()를 작성하거나 NotImplementedError를 명시한다
# - production downgrade는 팀장 승인 후 실행한다
# - data drop revision은 항상 backup 확인 후 진행한다
```

## 운영 체크리스트

- [ ] 모든 revision의 `downgrade()`가 `pass`가 아니다
- [ ] reversible revision은 `upgrade()`의 정확한 역순이다
- [ ] irreversible revision은 `raise NotImplementedError`로 명시한다
- [ ] 팀에 downgrade 정책이 문서화되어 있다
- [ ] production downgrade 전에 backup이 있는지 확인한다

## 처음 질문으로 돌아가기

- **어떤 경우에 진심으로 downgrade를 써야 하나요?** 컬럼 추가, 인덱스 생성 등 schema 변경은 항상 역순으로 작성합니다.
- **irreversible migration은 어떻게 표시하나요?** `raise NotImplementedError("irreversible: ...")`를 명시합니다. 빈 `pass`보다 명확합니다.
- **AI가 만든 `downgrade()`를 검토하는 기준은?** `pass`가 아닌지, upgrade의 역순인지, 데이터 소실 있으면 NotImplementedError인지 확인합니다.

## 정리

downgrade 전략은 production 사고 대응의 핵심입니다. AI가 만든 revision의 `downgrade()`를 항상 검토하고, `pass`로 남긴 것은 반드시 채워야 합니다. 다음 글에서는 배포 순서와 blue/green 배포 시 schema와 application code를 어떻게 안전하게 동기화하는지 다룹니다.

## 참고 자료

- [Alembic downgrade 문서](https://alembic.sqlalchemy.org/en/latest/tutorial.html#relative-migration-identifiers)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/08-downgrade-strategy)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- **바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략 (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
