---
title: "Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법"
series: alembic-101
episode: 5
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
- branch
- merge
- depends_on
- SQLite
last_reviewed: '2026-05-12'
seo_description: alembic revision graph는 git 브랜치와 똑같이 DAG(directed acyclic graph)입니다.
---

# Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법

이 글은 Alembic 101 시리즈의 다섯 번째 글입니다. 여기서는 여러 사람이 동시에 revision을 만들 때 graph가 왜 여러 head로 갈라지는지, 그리고 `alembic merge`로 어떻게 다시 단일 head로 정리하는지 설명합니다.

팀에서 동시에 PR을 열면 revision graph가 갈라지는 일은 예외가 아니라 정상 상태입니다. 이 사실을 모르고 있으면 처음 만나는 `Multiple head revisions are present` 에러가 실제보다 훨씬 더 위협적으로 느껴집니다.

![Alembic 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/05/05-01-diagram-merging-multiple-heads-back-to-o.ko.png)
*Alembic 101 5장 흐름 개요*

## 먼저 던지는 질문

- 언제 Alembic revision graph가 branch로 갈라질까요?
- `branch_labels`와 `depends_on`은 각각 정확히 무슨 역할일까요?
- 두 개의 head를 `alembic merge`로 어떻게 합칠까요?

## 왜 중요한가

여러 사람이 병렬로 PR을 여는 팀에서는 Alembic branch가 거의 매주 생깁니다. branch 자체는 자연스러운 현상이지만, deploy 직전에 `Multiple head revisions are present`가 튀어나오면 공포감이 커집니다. 이 글은 그 순간을 차분하게 정리하는 가이드입니다.

## 멘탈 모델

> alembic revision graph는 git과 같은 **DAG(directed acyclic graph)**입니다. 두 사람이 같은 head에서 revision을 만들면 두 개의 새 head가 생기고, `alembic merge`는 그 둘을 부모로 가지는 새 revision을 만들어 graph를 다시 하나의 head로 되돌립니다.

git 비유로 보면 `alembic merge`는 `git merge`입니다. 다만 merge revision은 새 schema 변경을 넣는 곳이 아니라, 갈라진 graph를 다시 꿰매는 구조적 revision입니다.

### 다이어그램: multi-head를 single head로 되돌리는 merge

## 핵심 개념

### branch가 생기는 순간

```text
A → B → C  (head: C)
        ↑
      Alice generates D, Bob generates E concurrently
        ↓
A → B → C → D  (head: D)
            ↘
              E  (head: E)
```

이 상태에서 `alembic heads`를 실행하면 두 개의 head가 보입니다.

```bash
$ alembic heads
d1e2f3a4b5c6 (head)
e7f8a9b0c1d2 (head)
```

그리고 `alembic upgrade head`는 모호성 오류를 냅니다.

### `branch_labels`와 `depends_on`

```python
revision = "d1e2f3a4b5c6"
down_revision = "c1234567890a"
branch_labels = ("billing",)        # name of the branch this revision belongs to
depends_on = ("e7f8a9b0c1d2",)      # this revision depends on a specific revision in another branch
```

- `branch_labels`: 같은 DB 안에서도 의도적으로 별도 branch를 유지할 때 씁니다. 예를 들어 특정 도메인 migration만 분리하고 싶을 때 `alembic upgrade billing@head`처럼 지정할 수 있습니다.
- `depends_on`: 한 branch의 revision이 다른 branch의 특정 revision을 먼저 필요로 할 때 씁니다. cross-branch dependency를 명시하는 장치입니다.

대부분의 일반적인 팀 환경에서는 둘 다 자주 쓰지 않습니다. branch가 보이면 바로 merge해서 닫는 편이 단순합니다.

### `alembic merge`

```bash
alembic merge -m "merge billing and audit branches" d1e2f3a4b5c6 e7f8a9b0c1d2
```

그러면 다음과 같은 merge revision이 생성됩니다.

```python
"""merge billing and audit branches

Revision ID: f9a8b7c6d5e4
Revises: d1e2f3a4b5c6, e7f8a9b0c1d2
Create Date: 2026-05-03 12:00:00.000000
"""
revision = "f9a8b7c6d5e4"
down_revision = ("d1e2f3a4b5c6", "e7f8a9b0c1d2")
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
```

여기서 기억할 점은 `down_revision`이 **tuple**이라는 사실과, `upgrade`/`downgrade`가 **비어 있다**는 점입니다. merge는 graph만 통합합니다.

### multi-head 상태에서 쓰는 명령

```bash
alembic heads                      # list current heads
alembic upgrade heads              # apply every head all the way (note the s)
alembic upgrade <revision_id>      # only up to a specific revision
alembic upgrade billing@head       # target by branch_labels
```

`head`와 `heads`의 차이를 반드시 기억해야 합니다. merge 전에는 복수형인 `heads`가 필요합니다.

## 변경 전후

```text
# Before: pushed without merging, deploy is stuck
$ alembic upgrade head
ERROR: Multiple head revisions are present for given argument 'head';
please specify a specific target revision...
```

```bash
# After: confirm heads, merge, return to single head
$ alembic heads
d1e2f3a4b5c6 (head)
e7f8a9b0c1d2 (head)

$ alembic merge -m "merge feature-billing into trunk" d1e2f3a4b5c6 e7f8a9b0c1d2
Generating versions/f9a8b7c6d5e4_merge_feature_billing_into_trunk.py ... done

$ alembic heads
f9a8b7c6d5e4 (head)

$ alembic upgrade head
INFO  Running upgrade ... -> f9a8b7c6d5e4, merge feature-billing into trunk
```

merge revision이 deploy 전에 PR에 포함되면 같은 종류의 사고는 다시 거의 발생하지 않습니다.

## 단계별 실습

### 1단계: branch 재현

로컬에서 일부러 branch를 한 번 만들어 보면 감이 빨리 옵니다.

```bash
# Alice's work
git checkout -b feature-a
alembic revision -m "add billing column"

# Bob's work (from the same base)
git checkout master
git checkout -b feature-b
alembic revision -m "add audit column"

# After both PRs land on master
git checkout master
git merge feature-a
git merge feature-b
alembic heads
```

그러면 head가 두 개 보입니다.

### 2단계: merge revision 생성

```bash
alembic merge -m "merge billing and audit" <id1> <id2>
```

생성된 파일을 커밋합니다. `upgrade`와 `downgrade`는 그대로 비워 둡니다.

### 3단계: 적용

```bash
alembic upgrade head
```

이제 다시 single head 상태이므로 평소처럼 진행됩니다.

### 4단계: cross-branch dependency가 있을 때

`feature-b`가 `feature-a`의 컬럼을 사용해야 한다면 `depends_on`으로 명시합니다.

```python
# feature-b's revision
revision = "e7f8a9b0c1d2"
down_revision = "c1234567890a"
depends_on = ("d1e2f3a4b5c6",)  # feature-a's revision
```

그러면 `alembic upgrade head`가 dependency를 읽고 순서를 맞춰 적용합니다.

### 5단계: 의도적인 장기 branch

`branch_labels`는 정말로 별도 도메인을 장기간 분리 운영할 때만 씁니다.

```python
revision = "abc123"
down_revision = None
branch_labels = ("audit",)
```

이후 `alembic upgrade audit@head`로 audit branch만 적용할 수 있습니다. 대부분 팀에는 필요 없습니다.

## 검증 루틴

```bash
alembic heads
alembic merge -m "merge local heads" <id1> <id2>
alembic heads
```

**확인할 점:** merge 전에는 head가 둘 이상 보이고, merge 후에는 `alembic heads`가 정확히 하나의 head만 반환해야 합니다.

## 자주 하는 실수

- **`head`와 `heads`를 혼동하기.** merge 전 상태에서 `head`는 모호성 오류를 냅니다.
- **merge revision의 `upgrade`에 새 schema 변경을 넣기.** merge는 구조 통합 전용이어야 합니다.
- **`branch_labels`를 남용하기.** 일반적인 팀 branch는 즉시 merge해서 닫는 편이 더 읽기 쉽습니다.
- **PR에서 migration 충돌을 조기에 못 잡기.** `alembic heads` 결과가 2개 이상이면 실패시키는 CI가 필요합니다.
- **merge 후 `down_revision` tuple 순서를 손으로 바꾸기.** 의미는 같아도 리뷰어를 헷갈리게 만듭니다.

## 실무 패턴

- **CI에서 head 개수는 항상 1이어야 합니다.** `python -c "from alembic.config import Config; from alembic.script import ScriptDirectory; cfg=Config('alembic.ini'); s=ScriptDirectory.from_config(cfg); assert len(list(s.get_heads()))==1"` 같은 가드가 유용합니다.
- **충돌한 두 PR 중 늦게 머지되는 쪽이 merge revision을 포함합니다.** 가장 단순한 late-merger workflow입니다.
- **merge 메시지 컨벤션을 정합니다.** `merge <branchA> and <branchB>` 형식을 권장합니다.
- **`depends_on`은 꼭 필요할 때만 씁니다.** 대개는 두 revision을 한 PR로 묶는 편이 더 단순합니다.
- **`alembic history --verbose`로 graph를 읽습니다.** 사고가 났을 때 가장 빠른 파악 도구입니다.

## 체크리스트

- [ ] merge 후 `alembic heads`가 single head를 반환한다
- [ ] merge revision의 `upgrade`와 `downgrade`는 비어 있다
- [ ] CI가 multi-head 상태를 감지한다
- [ ] cross-branch dependency가 있으면 `depends_on`이 명시돼 있다
- [ ] `branch_labels`는 정말 분리된 도메인일 때만 사용한다
- [ ] merge 메시지가 `merge <X> and <Y>` 컨벤션을 따른다

## 연습 문제

1. 로컬 SQLite 환경에서 head 두 개를 만들고 `alembic merge`로 하나로 합쳐 보세요.
2. merge revision을 열어 `down_revision`이 tuple인지 확인해 보세요.
3. head 개수를 검사하는 CI 스크립트를 추가하고, multi-head PR을 막는지 검증해 보세요.

## 정리, 다음 글

Alembic branch는 git branch와 같은 모델로 이해하면 됩니다. 두려워할 대상이 아니라, `alembic merge`로 graph만 다시 묶으면 되는 정상 상태입니다. CI에서 “head는 정확히 하나”를 강제하는 규칙만으로도 팀 차원의 사고를 크게 줄일 수 있습니다.

다음 글에서는 schema가 아니라 row 자체를 바꾸는 data migration을 다룹니다.

## 충돌을 줄이는 협업 규칙

branch 자체는 정상 상태지만, 팀 규칙이 없으면 충돌이 일상화됩니다. 실무에서는 아래 세 가지 규칙만 지켜도 multi-head 발생 빈도를 크게 줄일 수 있습니다.

- **migration 파일 생성 시점을 늦춥니다.** 기능 코드를 먼저 안정화하고 PR 마무리 단계에서 revision을 만들면 재작업이 줄어듭니다.
- **PR 템플릿에 Alembic 확인 항목을 둡니다.** `alembic heads` 결과, `upgrade head` 성공 여부, `--sql` 출력 검토 여부를 체크하게 만듭니다.
- **머지 직전 재생성 원칙을 둡니다.** 오래 열린 PR은 기준 head가 바뀌었을 가능성이 높으므로, 최신 main 기준으로 migration을 다시 점검합니다.

핵심은 도구 문제가 아니라 프로세스 문제라는 사실입니다. `alembic merge`는 사후 복구 도구로 매우 유용하지만, 근본적으로는 충돌을 덜 만들도록 팀 흐름을 설계하는 편이 더 큰 효과를 냅니다.

## multi-head 사고를 줄이는 운영 가드

branch 자체는 정상 상태지만, 운영에서는 multi-head를 오래 방치하지 않는 것이 중요합니다. 다음 가드를 CI에 넣으면 배포 직전 충돌을 크게 줄일 수 있습니다.

```bash
python3 - <<'PY'
from alembic.config import Config
from alembic.script import ScriptDirectory

cfg = Config("alembic.ini")
script = ScriptDirectory.from_config(cfg)
heads = list(script.get_heads())
if len(heads) != 1:
    raise SystemExit(f"Fail: expected single head, got {len(heads)} -> {heads}")
print(f"Pass: single head {heads[0]}")
PY
```

이 검사는 migration 변경이 없는 PR에서도 빠르게 통과하고, 충돌 PR에서는 즉시 실패합니다. 결과적으로 merge revision을 기능 배포 전에 만들도록 팀 행동을 유도합니다.

## merge revision 파일 리뷰 포인트

`alembic merge`로 생성된 파일은 변경이 없어 보여서 대충 넘어가기 쉽습니다. 그래도 다음은 반드시 확인해야 합니다.

1. `down_revision`이 tuple인지
2. tuple에 포함된 revision ID가 실제 current heads와 일치하는지
3. `upgrade`/`downgrade`에 불필요한 DDL이 없는지

```python
revision = "f9a8b7c6d5e4"
down_revision = ("d1e2f3a4b5c6", "e7f8a9b0c1d2")

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
```

merge revision은 구조 정리 전용입니다. DDL이 섞이면 merge의 목적이 흐려지고, 장애 시 원인 추적도 어려워집니다.

## 의존성 그래프 예시

```text
A -> B -> C -> D(head)
          \-> E(head)

merge(D, E) => M(head)

A -> B -> C -> D
          \-> E
               \ 
                 M(head)
```

이 도식이 머릿속에 들어오면 `Multiple head revisions` 에러를 기능 결함이 아니라 그래프 정리 작업으로 인식할 수 있습니다.

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

- **언제 Alembic revision graph가 branch로 갈라질까요?**
  - 같은 `down_revision`을 부모로 두고 Alice의 `D`와 Bob의 `E`처럼 두 revision이 동시에 생기면 graph가 갈라지고 `alembic heads`에 head가 두 개 보입니다. 본문에서 `Multiple head revisions are present` 오류가 나는 이유도 그 동시 생성 때문입니다.
- **`branch_labels`와 `depends_on`은 각각 정확히 무슨 역할일까요?**
  - `branch_labels = ("billing",)`는 이 revision이 어느 branch에 속하는지 이름을 붙이고, `depends_on = ("e7f8...")`는 다른 branch의 특정 revision이 먼저 필요하다는 뜻입니다. 둘 다 일반적인 팀 개발에서는 자주 쓰지 않지만, cross-branch 의존성을 문서화해야 할 때는 분명한 표식이 됩니다.
- **두 개의 head를 `alembic merge`로 어떻게 합칠까요?**
  - `alembic merge -m "merge billing and audit branches" d1e2... e7f8...`를 실행하면 `down_revision`이 튜플인 merge revision이 하나 생성됩니다. 그 revision의 `upgrade()`와 `downgrade()`가 `pass`여도 graph는 다시 단일 head로 닫힙니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성](./03-first-revision-upgrade-downgrade.md)
- [Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계](./04-autogenerate-and-its-limits.md)
- **branch와 merge: 동시에 만든 revision을 합치는 법 (현재 글)**
- 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기 (예정)
- online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 (예정)
- downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 (예정)
- 배포 순서와 blue/green: schema와 application code의 안전한 동기화 (예정)
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Working with Branches](https://alembic.sqlalchemy.org/en/latest/branches.html)
- [Alembic: Merging Branches](https://alembic.sqlalchemy.org/en/latest/branches.html#merging-branches)
- [Alembic: depends_on](https://alembic.sqlalchemy.org/en/latest/branches.html#referencing-dependencies)
- [Alembic: ScriptDirectory API](https://alembic.sqlalchemy.org/en/latest/api/script.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/05-branches-and-merges)

Tags: Python, Alembic, SQLAlchemy, Migration
