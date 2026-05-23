---
title: "Alembic 101 (8/10): downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가"
series: alembic-101
episode: 8
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
- downgrade
- expand-contract
- rollback
- SQLite
last_reviewed: '2026-05-12'
seo_description: 'downgrade는 두 종류로 나뉩니다. (1) 가역 변경: 정확한 역연산이 가능하고 데이터 손실이 없다 (예: nullable
  컬럼…'
---

# Alembic 101 (8/10): downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가

이 글은 Alembic 101 시리즈의 여덟 번째 글입니다. 여기서는 reversible change와 irreversible change를 구분하고, downgrade 정책을 코드에 어떻게 정직하게 표현할지 정리합니다.

`downgrade()` 함수가 존재한다고 해서 그 변경이 실제로 안전하게 되돌릴 수 있다는 뜻은 아닙니다. 어떤 revision은 정확하게 되돌릴 수 있지만, 어떤 revision은 되돌리는 순간 데이터 손실을 의미합니다.

![Alembic 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/08/08-01-diagram-deciding-between-reversible-and.ko.png)
*Alembic 101 8장 흐름 개요*

## 먼저 던지는 질문

- production에서 downgrade는 언제 가능하고 언제 사실상 불가능할까요?
- 어떤 종류의 변경이 irreversible하며, 어떻게 다뤄야 할까요?
- expand-contract는 downgrade 가능성을 어떻게 회복시킬까요?

## 왜 중요한가

Alembic을 처음 배울 때 downgrade는 당연한 내장 기능처럼 보입니다. 하지만 실제 production에서는 거의 쓰이지 않거나, 써도 매우 위험합니다. 그렇다고 빈 함수로 두는 것도 답이 아닙니다. downgrade를 어떻게 다룰지는 운영 정책이고, 그 정책은 코드에 명시적으로 드러나야 합니다.

## 멘탈 모델

> downgrade는 두 종류로 나뉩니다. **(1) 가역 변경: 정확한 역연산이 가능하고 데이터 손실이 없다. (2) 비가역 변경: 역연산 자체가 데이터 손실을 뜻한다.** 첫 번째는 진심으로 작성하고, 두 번째는 명시적으로 차단하는 편이 더 정직합니다.

git 비유로 보면 첫 번째는 깔끔하게 revert되는 commit이고, 두 번째는 force-push 없이는 되돌릴 수 없는 합쳐진 history에 가깝습니다.

### 다이어그램: reversible과 irreversible 판단 흐름

## 핵심 개념

### 가역과 비가역의 구분

| 변경 | 가역? | 메모 |
| --- | --- | --- |
| Add nullable column | Yes | Drop reverts precisely |
| Add or drop index | Yes | Recreate to recover |
| Add table | Yes | Drop reverts |
| **Drop column** | No | Data loss |
| **Data migration** | No | Hard to restore pre-transform state |
| **Tighten to NOT NULL** | Effectively no | The default to use is ambiguous |
| Narrow column type (`String(100)` → `String(50)`) | No | Truncation risk |

비가역 변경에는 정직한 downgrade를 쓸 수 없습니다. 막는 편이 오히려 안전합니다.

### “downgrade 금지” 선언

```python
def downgrade() -> None:
    raise NotImplementedError(
        "Irreversible: tier column drop loses data. "
        "If rollback needed, restore from backup."
    )
```

`pass`로 두면 실수로 `alembic downgrade -1`를 실행했을 때 조용히 성공해 버리고, graph만 되감긴 위험한 상태가 됩니다. `NotImplementedError`는 이 상황을 즉시 드러냅니다.

### expand-contract 패턴

비가역 변경을 더 안전한 단계로 쪼개는 가장 강력한 도구입니다.

```text
Phase 1 (expand):   add the new schema, keep the old
Phase 2 (migrate):  move data into the new schema
Phase 3 (deploy):   application starts using the new schema
Phase 4 (contract): remove the old schema
```

각 단계가 **개별적으로는 더 작은 변경**이기 때문에, 사고가 나더라도 한 단계씩 판단하고 대응할 수 있습니다. 예를 들어 column rename은 다음처럼 나눕니다.

```text
1. add display_name (nullable=True)         ← reversible
2. backfill display_name from name          ← data migration (irreversible)
3. app code uses display_name               ← code deploy
4. drop name                                ← irreversible, but with safety nets between phases
```

phase 4로 가기 전까지는 충분한 안전 구간이 있습니다. 반대로 rename을 한 revision에 몰아넣으면 복구 선택지가 급격히 줄어듭니다.

### forward-fix vs downgrade

production 사고가 나면 보통 둘 중 하나를 택합니다.

- **forward-fix**: 문제를 수정하는 새 revision을 추가합니다. 대부분의 경우 기본값입니다.
- **downgrade**: 직전 revision으로 되감습니다. 비가역 작업이 섞이면 위험합니다.

forward-fix가 기본이어야 하는 이유는 `alembic_version`, 여러 인스턴스의 상태, application code의 정합성을 모두 한 방향으로 유지하기가 훨씬 쉽기 때문입니다.

## 변경 전후

```python
# 이전: 되돌릴 수 없는 변경 시 다운그레이드 비우기
def upgrade() -> None:
    op.drop_column("users", "legacy_token")  # ← data lost forever

def downgrade() -> None:
    pass  # ← silently "succeeds" on accident
```

```python
# 이후: 명시적 차단
def upgrade() -> None:
    op.drop_column("users", "legacy_token")

def downgrade() -> None:
    raise NotImplementedError(
        "drop column users.legacy_token is irreversible (data loss). "
        "Restore from backup or apply a new revision that re-adds the column."
    )
```

After 버전은 의도를 숨기지 않습니다. 잘못된 downgrade 시도가 곧바로 실패하므로 실제 사고를 막을 수 있습니다.

## 단계별 실습

### 1단계: 가역 revision 작성

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("nickname", sa.String(50), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "nickname")
```

`nullable=True`로 추가한 schema-only 변경은 데이터 손실이 없으므로 실제 downgrade를 작성하는 편이 맞습니다.

### 2단계: 비가역 revision 차단

```python
def upgrade() -> None:
    op.drop_column("users", "old_field")

def downgrade() -> None:
    raise NotImplementedError("drop is irreversible (data loss)")
```

### 3단계: rename을 expand-contract로 분해

revision 1 (expand):
```python
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "display_name")
```

revision 2 (data backfill, irreversible):
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

3단계 전까지는 상대적으로 자유롭게 되감을 수 있습니다. 3단계 이후의 문제는 보통 forward-fix로 다룹니다.

### 4단계: 정책 문서화

`alembic.ini`나 README에 한 줄로 원칙을 남깁니다.

```text
Downgrade policy:
- Reversible revisions: real downgrade()
- Irreversible (drop, data migration): raise NotImplementedError
- Production rollback: forward-fix only; restore from backup if necessary
```

## 검증 루틴

```bash
alembic downgrade -1
```

**확인할 점:** 비가역 revision이라면 조용히 성공하면 안 됩니다. `NotImplementedError`가 즉시 올라와야 운영자가 잘못된 rollback 경로를 밟지 않습니다.

## 자주 하는 실수

- **비가역 변경에 `pass`를 두기.** 조용한 성공이 가장 위험합니다. `NotImplementedError`로 명시하세요.
- **production에서 downgrade를 기본 복구 수단처럼 쓰기.** 다른 인스턴스와 데이터 상태가 쉽게 어긋납니다.
- **큰 변경을 expand-contract 없이 한 번에 처리하기.** rename이나 NOT NULL 강화는 사실상 비가역이 됩니다.
- **downgrade를 테스트하지 않기.** 가역 revision이라면 PR에서 `downgrade -1 && upgrade head`를 확인해야 합니다.
- **schema만 되감으면 끝난다고 착각하기.** 데이터와 application code는 이미 새 상태를 가정하고 있을 수 있습니다.

## 실무 패턴

- **rename, NOT NULL tightening, drop에는 expand-contract를 기본 적용합니다.**
- **deploy script 수준에서 production downgrade를 막습니다.** 사람이 실수로 실행하지 못하게 해야 합니다.
- **PR 체크리스트에 “이 revision은 reversible인가?”를 추가합니다.**
- **backup-and-restore를 진짜 rollback 수단으로 검증합니다.** Alembic downgrade는 백업 대체재가 아닙니다.
- **forward-fix revision 메시지 템플릿을 정합니다.** 예: `fix <old_revision>`.

## 체크리스트

- [ ] 모든 revision을 reversible / irreversible로 분류했다
- [ ] irreversible revision의 `downgrade`는 `NotImplementedError`를 사용한다
- [ ] 큰 변경은 expand-contract 여러 단계로 분리했다
- [ ] reversible revision은 `downgrade -1 && upgrade head`를 통과한다
- [ ] production downgrade 정책이 README 등에 문서화돼 있다
- [ ] backup-and-restore 경로를 실제 rollback 수단으로 확인했다

## 연습 문제

1. column drop revision을 만들고 `downgrade`에 `NotImplementedError`를 넣은 뒤, `alembic downgrade -1`이 실패하는지 확인해 보세요.
2. `name` → `display_name` rename을 3단계 expand-contract로 구현해 보세요.
3. application code가 새 컬럼을 쓰기 시작한 뒤 downgrade를 시도하면 어떤 종류의 문제가 생기는지 관찰해 보세요.

## 정리, 다음 글

downgrade는 기본 기능이 아니라 정책의 문제입니다. 변경을 reversible과 irreversible로 분류하고, 후자는 코드 수준에서 명시적으로 막는 것이 정직한 운영입니다. expand-contract는 비가역 변경을 더 안전한 단계로 되돌려 놓는 가장 강한 도구입니다.

다음 글에서는 migration과 application code를 어떤 순서로 배포해야 하는지, 그리고 blue/green 환경에서 schema 호환성을 어떻게 설계해야 하는지 다룹니다.

## 변경 유형별 downgrade 정책 표준안

팀 정책은 문장보다 표로 고정하는 편이 운영에 유리합니다.

| 변경 유형 | 기본 downgrade 정책 | 비고 |
| --- | --- | --- |
| Add nullable column | 구현 | 역연산이 명확함 |
| Add index | 구현 | 역연산이 명확함 |
| Rename column | 단계 분해 후 일부 구현 | data 단계는 보통 비가역 |
| Drop column | 차단 (`NotImplementedError`) | 데이터 손실 |
| Bulk data transform | 차단 (`NotImplementedError`) | 이전 상태 복원이 어려움 |
| Tighten NOT NULL | 조건부 구현 또는 차단 | NULL 복원 정책이 필요 |

이 표를 PR 템플릿과 함께 쓰면 리뷰어가 "왜 downgrade가 비어 있는가"를 감으로 판단하지 않아도 됩니다.

## forward-fix revision 예시

비가역 revision에서 문제가 발생하면 일반적으로 새 revision으로 복구합니다.

```python
"""fix 8a12c3d4e5f6: restore users.tier default and backfill nulls"""

revision = "9b23d4e5f6a7"
down_revision = "8a12c3d4e5f6"

def upgrade() -> None:
    op.execute("UPDATE users SET tier = 'free' WHERE tier IS NULL")
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier", existing_type=sa.String(16), nullable=False)

def downgrade() -> None:
    raise NotImplementedError("forward-fix revision")
```

이 패턴은 이력을 앞으로 진행시키므로 incident 타임라인과 감사 로그를 일관되게 유지할 수 있습니다.

## 배포 스크립트에서 downgrade 차단

운영 실수를 줄이려면 사람의 선택에 맡기지 말고 배포 도구에서 막는 편이 좋습니다.

```bash
case "${ALEMBIC_ACTION:-upgrade}" in
  upgrade)
    alembic upgrade head
    ;;
  downgrade)
    echo "Fail: production downgrade is blocked by policy"
    exit 1
    ;;
  *)
    echo "Fail: unknown action"
    exit 1
    ;;
esac
```

정책이 코드화되어 있으면 야간 장애 상황에서도 위험한 명령이 우발적으로 실행될 가능성을 줄일 수 있습니다.

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

- **production에서 downgrade는 언제 가능하고 언제 사실상 불가능할까요?**
  - `sa.Column("nickname", ..., nullable=True)`를 추가하는 정도의 가역 변경은 실제 `downgrade()`를 써 둘 수 있지만, `op.drop_column("users", "legacy_token")`처럼 데이터를 지우는 순간은 사실상 비가역입니다. 그래서 본문도 production 사고의 기본값을 downgrade보다 forward-fix에 두었습니다.
- **어떤 종류의 변경이 irreversible하며, 어떻게 다뤄야 할까요?**
  - 컬럼 drop, 의미 있는 데이터 backfill, 길이 축소 같은 변경은 되돌려도 원래 값을 복원할 수 없으므로 `raise NotImplementedError(...)`로 명시하는 편이 안전합니다. `pass`로 비워 두는 것보다 훨씬 낫다고 한 이유도 잘못된 성공을 막기 위해서입니다.
- **expand-contract는 downgrade 가능성을 어떻게 회복시킬까요?**
  - `display_name`을 먼저 추가하고, 그다음 backfill하고, 마지막에 `name`을 지우는 식으로 쪼개면 phase 4 전까지는 충분한 안전 구간이 생깁니다. 즉, 한 revision에 rename을 몰아넣지 않고 reversible한 구간을 길게 유지하는 것이 이 패턴의 가치입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성](./03-first-revision-upgrade-downgrade.md)
- [Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계](./04-autogenerate-and-its-limits.md)
- [Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법](./05-branches-and-merges.md)
- [Alembic 101 (6/10): 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기](./06-data-migrations.md)
- [Alembic 101 (7/10): online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기](./07-online-vs-offline-and-batch.md)
- **downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 (현재 글)**
- 배포 순서와 blue/green: schema와 application code의 안전한 동기화 (예정)
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Operation Reference](https://alembic.sqlalchemy.org/en/latest/ops.html)
- [Martin Fowler: Evolutionary Database Design](https://martinfowler.com/articles/evodb.html)
- "Refactoring Databases" by Scott Ambler & Pramod Sadalage (expand-contract origin)
- [PostgreSQL Wiki: Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/08-downgrade-strategy)

Tags: Python, Alembic, SQLAlchemy, Migration
