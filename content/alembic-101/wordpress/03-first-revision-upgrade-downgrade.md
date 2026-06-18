---
title: "바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade"
series: alembic-101
episode: 3
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

# 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 세 번째 글입니다.

---

AI가 `alembic revision --autogenerate -m "add users table"`을 실행해 파일을 만들어 줬습니다. 파일을 열면 `upgrade()`와 `downgrade()` 두 함수가 있습니다. `upgrade()`에는 테이블 생성 코드가 있고, `downgrade()`는... 비어 있습니다. AI가 종종 `downgrade()`를 빠뜨립니다. 그 순간 rollback은 불가능해집니다.

바이브코딩에서 첫 revision을 손으로 작성해 보는 것이 중요한 이유가 여기 있습니다. autogenerate가 만든 파일이 올바른지 판단하려면, 올바른 revision이 어떻게 생겼는지 알아야 합니다. `upgrade()`는 변경을 적용하고, `downgrade()`는 그것을 정확히 되돌립니다. 이 두 함수가 대칭을 이루어야 롤백이 가능합니다.

revision 파일은 배포의 일부입니다. PR에 코드가 들어갈 때 revision 파일도 함께 들어가야 하고, 리뷰어는 `upgrade()`와 `downgrade()`가 짝을 이루는지 확인해야 합니다. 바이브코딩 팀에서 이 습관이 없으면 production 사고는 시간 문제입니다.

> **핵심 인사이트:** `upgrade()`와 `downgrade()`는 항상 대칭이어야 합니다. AI가 한쪽만 만들었다면 반드시 나머지를 추가하세요. rollback 없는 migration은 일방통행입니다.

## 이 글에서 다룰 문제

- revision 파일의 `upgrade()`와 `downgrade()`는 왜 항상 대칭이어야 할까요?
- AI가 만든 revision 파일에서 어떤 부분을 반드시 검토해야 할까요?
- `op.add_column`과 `op.drop_column`의 짝은 어떻게 맞춰야 할까요?
- `server_default`와 ORM `default`의 차이를 모르면 어떤 사고가 생길까요?
- revision 파일을 PR에 포함시키는 워크플로우는 어떻게 만들까요?

## 올바른 revision 파일 구조

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16),
                  nullable=False, server_default="free"))
    op.create_index("ix_users_tier", "users", ["tier"])

def downgrade() -> None:
    op.drop_index("ix_users_tier", table_name="users")
    op.drop_column("users", "tier")  # upgrade의 역순
```

## 변경 전후 비교

**Before: downgrade 없음**
```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16)))

def downgrade() -> None:
    pass  # 롤백 불가!
```

**After: 대칭 구조**
```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16)))

def downgrade() -> None:
    op.drop_column("users", "tier")  # 정확한 역순
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `downgrade()`가 `pass` | 롤백 불가 | upgrade의 역순으로 작성 |
| `server_default`와 ORM `default` 혼동 | DB와 ORM 불일치 | DB 레벨 기본값은 `server_default` |
| 인덱스 drop 순서 오류 | foreign key 제약 위반 | 역순 보장 |
| 이미 push된 revision 수정 | 다른 환경 충돌 | 새 revision으로 수정 |
| SQLite에서 `batch_alter_table` 미사용 | 컬럼 변경 실패 | SQLite는 batch 모드 필수 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"users 테이블에 tier 컬럼을 추가하는 alembic revision을 만들어줘.
downgrade()에서 op.drop_column으로 정확히 되돌아오도록 해줘"

# 검토할 사항:
# 1. upgrade()에서 만든 것을 downgrade()가 역순으로 제거하는가
# 2. server_default가 필요한 nullable=False 컬럼인가
# 3. SQLite라면 batch_alter_table이 필요한가
```

## 운영 체크리스트

- [ ] `upgrade()`와 `downgrade()`가 대칭을 이룬다
- [ ] `server_default`와 ORM `default`를 구분하여 사용했다
- [ ] 인덱스 생성/삭제가 올바른 순서로 되어 있다
- [ ] revision 파일이 기능 코드와 같은 PR에 포함된다
- [ ] `alembic downgrade -1`로 rollback이 실제로 동작하는지 테스트했다

## 처음 질문으로 돌아가기

- **`upgrade()`와 `downgrade()`는 왜 항상 대칭이어야 할까요?** `downgrade()`가 없으면 production 장애 시 롤백이 불가능합니다. 선택이 아닌 필수입니다.
- **AI가 만든 revision에서 무엇을 검토해야 할까요?** `downgrade()` 완성 여부, `server_default` vs ORM `default`, 순서 역전 여부입니다.
- **revision 파일을 PR에 포함시키는 이유는?** 코드 리뷰 대상이 되고, 기능-마이그레이션-테스트가 하나의 단위로 배포됩니다.

## 정리

revision 파일은 DB 변경의 계약서입니다. AI가 만들어도 사람이 검토해야 합니다. 특히 `downgrade()`가 올바른지 확인하는 것은 바이브코딩 팀의 필수 습관입니다. 다음 글에서는 autogenerate가 잡는 것과 못 잡는 것의 경계를 다룹니다.

## 참고 자료

- [Alembic Operations Reference](https://alembic.sqlalchemy.org/en/latest/ops.html)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/03-first-revision-upgrade-downgrade)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- **바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
