---
title: "downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가"
series: alembic-101
episode: 8
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
  - downgrade
  - expand-contract
  - rollback
  - SQLite
last_reviewed: '2026-05-03'
---

# downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가

## 이 글에서 배울 것

- production downgrade가 언제는 가능하고 언제는 사실상 불가능한가
- 비가역(irreversible) 변경의 종류와 처리 전략
- expand-contract 패턴이 downgrade 가능성을 어떻게 회복시키는가
- "downgrade 금지" 정책을 코드 차원에서 명시하는 방법
- 사고 시 forward-fix와 downgrade 중 어느 쪽을 선택할지의 기준

## 이 글에서 답할 질문

- production에서 downgrade가 사실상 불가능해지는 변경은 어떤 것들인가?
- 비가역(irreversible) 변경을 만났을 때 코드와 데이터를 어떻게 분리해 다루는가?
- expand-contract 패턴은 downgrade 가능성을 어떻게 회복시키는가?
- "downgrade 금지" 정책을 코드와 CI 차원에서 어떻게 명시할 수 있는가?
- 사고 시 forward-fix와 downgrade 중 어느 쪽을 선택해야 하는지 판단 기준은 무엇인가?

## 왜 중요한가

downgrade는 alembic을 처음 배울 때는 당연한 기본 기능처럼 보이지만, 실제 production에서는 거의 사용되지 않거나 위험합니다. 그렇다고 빈 함수로 두는 것도 답이 아닙니다. "downgrade를 어떻게 다룰 것인가"는 운영 정책의 영역이고, 그 정책이 코드에 명시적으로 표현되어야 합니다.

## Mental Model

> downgrade는 두 종류로 나뉩니다. **(1) 가역 변경: 정확한 역연산이 가능하고 데이터 손실이 없다 (예: nullable 컬럼 추가). (2) 비가역 변경: 역연산이 데이터 손실을 의미한다 (예: 컬럼 drop, 데이터 마이그레이션).** 1은 진심으로 작성하고, 2는 명시적으로 차단하는 것이 정직합니다.

git에 비유하면 1은 깔끔하게 revert되는 commit, 2는 한 번 push하면 force-push 없이는 되돌릴 수 없는 합쳐진 history입니다.

## 핵심 개념

### 가역과 비가역의 분류

| 변경 | 가역? | 메모 |
| --- | --- | --- |
| nullable 컬럼 추가 | 가역 | drop으로 정확히 되돌림 |
| 인덱스 추가/삭제 | 가역 | 재생성으로 복구 |
| 테이블 추가 | 가역 | drop으로 되돌림 |
| **컬럼 drop** | 비가역 | 데이터 손실 |
| **데이터 마이그레이션** | 비가역 | 변환 전 상태 복원 어려움 |
| **NOT NULL로 강화** | 사실상 비가역 | 어떤 default를 쓸지 모호 |
| 컬럼 type narrow (`String(100)` → `String(50)`) | 비가역 | truncation 위험 |

비가역 변경은 downgrade를 진심으로 짤 수 없으므로 차단하는 편이 정직합니다.

### "downgrade 금지" 명시

```python
def downgrade() -> None:
    raise NotImplementedError(
        "Irreversible: tier column drop loses data. "
        "If rollback needed, restore from backup."
    )
```

`pass`로 두면 누군가 `alembic downgrade -1`을 실수로 실행했을 때 silently 성공해 graph만 되감기고 schema는 그대로인 위험한 상태가 됩니다. `raise NotImplementedError`는 이를 막아 줍니다.

### expand-contract 패턴

비가역 변경을 가역으로 만드는 가장 강력한 도구입니다.

```text
Phase 1 (expand):  새 schema 추가, 기존 schema 유지
Phase 2 (migrate): 데이터를 새 schema로 옮김
Phase 3 (deploy):  애플리케이션이 새 schema 사용
Phase 4 (contract): 기존 schema 제거
```

각 단계가 **개별 가역 변경**이므로 어느 단계에서 사고가 나도 한 단계씩 되돌릴 수 있습니다. column rename을 예로 들면:

```text
1. add display_name (nullable=True)         ← 가역
2. backfill display_name from name          ← 데이터 마이그레이션 (비가역)
3. app code uses display_name               ← 코드 배포
4. drop name                                ← 비가역, 그러나 단계 사이에 안전망 있음
```

3단계까지 production이 안정되어야 4단계로 넘어갑니다. 4단계 전이라면 언제든 2단계까지 되감을 수 있습니다.

### forward-fix vs downgrade

production 사고 시 둘 중 하나를 선택합니다.

- **forward-fix**: 새 revision으로 문제 보정 (대부분 권장)
- **downgrade**: 직전 revision으로 되감기 (비가역이 섞이면 위험)

forward-fix가 기본이어야 하는 이유: alembic_version 테이블 동기화, 다른 인스턴스의 상태, application 코드와의 정합성 등을 모두 한 방향으로 정리하기가 더 쉽습니다.

## Before-After

```python
# Before: 비가역 변경에 빈 downgrade
def upgrade() -> None:
    op.drop_column("users", "legacy_token")  # ← 데이터 영원히 사라짐

def downgrade() -> None:
    pass  # ← 사고 시 silent하게 "성공"
```

```python
# After: 명시적 차단
def upgrade() -> None:
    op.drop_column("users", "legacy_token")

def downgrade() -> None:
    raise NotImplementedError(
        "drop column users.legacy_token is irreversible (data loss). "
        "Restore from backup or apply a new revision that re-adds the column."
    )
```

After는 의도를 명시합니다. 누군가 사고로 `alembic downgrade -1`을 실행해도 즉시 실패하고 진짜 사고를 막아 줍니다.

## 단계별 실습

### 1단계: 가역 revision 작성

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("nickname", sa.String(50), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "nickname")
```

`nullable=True`로 추가하면 schema-only이고 데이터가 없으니 drop이 안전합니다. 진심으로 downgrade를 작성합니다.

### 2단계: 비가역 revision 차단

```python
def upgrade() -> None:
    op.drop_column("users", "old_field")

def downgrade() -> None:
    raise NotImplementedError("drop is irreversible (data loss)")
```

### 3단계: expand-contract로 rename 처리

revision 1 (expand):
```python
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "display_name")
```

revision 2 (data backfill, 비가역):
```python
def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("UPDATE users SET display_name = name WHERE display_name IS NULL"))

def downgrade() -> None:
    raise NotImplementedError("data migration is irreversible")
```

revision 3 (contract):
```python
def upgrade() -> None:
    op.drop_column("users", "name")

def downgrade() -> None:
    raise NotImplementedError("drop name is irreversible")
```

3을 적용하기 전에는 1, 2 사이를 자유롭게 오갈 수 있습니다. 3을 적용한 후의 사고는 forward-fix로 대응합니다.

### 4단계: 정책 문서화

`alembic.ini`나 README에 한 줄을 둡니다.

```text
Downgrade policy:
- Reversible revisions: real downgrade()
- Irreversible (drop, data migration): raise NotImplementedError
- Production rollback: forward-fix only; restore from backup if necessary
```

## 자주 하는 실수

- **비가역 변경에 `pass`.** silent 성공이 가장 위험. `NotImplementedError`로 명시.
- **production에서 downgrade 적극 사용.** 다른 인스턴스, 데이터 상태와의 동기화가 깨지기 쉽습니다. forward-fix가 기본.
- **expand-contract 없이 큰 변경.** rename, type 강화는 한 revision으로 처리하면 사실상 비가역.
- **downgrade를 테스트하지 않음.** PR에서 `downgrade -1 && upgrade head`를 한 번 돌려야 가역성이 검증됩니다.
- **downgrade가 실제로 가역적이라 가정.** schema는 되돌렸지만 데이터가 변경되었거나 application이 새 schema를 가정하는 상태는 흔합니다.

## 실무에서 쓰는 패턴

- **3단 분리(expand-contract).** rename, NOT NULL 강화, 컬럼 drop 모두 이 패턴.
- **production downgrade 비활성화 옵션.** 운영 환경에서 `alembic downgrade`가 사람의 실수로 실행되지 않도록 deploy script 차원에서 차단.
- **PR 체크리스트에 "가역인가?" 항목.** 코드 리뷰 단계에서 명시적 결정.
- **backup-and-restore가 진짜 rollback 도구.** alembic downgrade를 백업의 대체로 보지 않습니다.
- **forward-fix revision 템플릿.** "fix `<old_revision>`" 형식으로 의도 표현.

## 체크리스트

- [ ] 모든 revision의 가역/비가역이 분류되어 있다
- [ ] 비가역 revision의 `downgrade`는 `NotImplementedError`다
- [ ] 큰 변경(rename, NOT NULL, drop)은 expand-contract 3단으로 나뉘어 있다
- [ ] 가역 revision은 PR에서 `downgrade -1 && upgrade head` 사이클을 통과했다
- [ ] production downgrade 정책이 README에 명시되어 있다
- [ ] backup-and-restore가 실제 rollback 수단으로 검증되어 있다

## 연습 문제

1. 컬럼 drop revision을 만들고 `downgrade()`에 `NotImplementedError`를 명시한 뒤, `alembic downgrade -1`이 실패하는 것을 확인하세요.
2. `name` → `display_name` rename을 expand-contract 3단으로 작성하세요.
3. application 코드에서 새 컬럼을 사용하기 시작한 뒤 downgrade를 시도해 어떤 에러가 발생하는지 직접 보세요.

## 정리, 다음 글

downgrade는 "기본 켜진 기능"이 아니라 "정책으로 결정되는 기능"입니다. 가역과 비가역을 분류하고 후자를 명시적으로 차단하는 것이 정직한 운영입니다. expand-contract 패턴이 비가역을 가역으로 회복시키는 가장 강력한 도구입니다.

다음 글은 application 코드와 schema 변경의 배포 순서를 다루는 deploy ordering과 blue/green 안전 규칙입니다.

## 참고 자료

- Alembic: Operation Reference — https://alembic.sqlalchemy.org/en/latest/ops.html
- Strong Loop / Martin Fowler: Evolutionary Database Design — https://martinfowler.com/articles/evodb.html
- "Refactoring Databases" by Scott Ambler & Pramod Sadalage (expand-contract origin)
- PostgreSQL Wiki: Don't Do This — https://wiki.postgresql.org/wiki/Don%27t_Do_This

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, downgrade, expand-contract, rollback, SQLite
