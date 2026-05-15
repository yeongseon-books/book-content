---
title: 'branch와 merge: 동시에 만든 revision을 합치는 법'
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

# branch와 merge: 동시에 만든 revision을 합치는 법

이 글은 Alembic 101 시리즈의 다섯 번째 글입니다. 여기서는 여러 사람이 동시에 revision을 만들 때 graph가 왜 여러 head로 갈라지는지, 그리고 `alembic merge`로 어떻게 다시 단일 head로 정리하는지 설명합니다.

팀에서 동시에 PR을 열면 revision graph가 갈라지는 일은 예외가 아니라 정상 상태입니다. 이 사실을 모르고 있으면 처음 만나는 `Multiple head revisions are present` 에러가 실제보다 훨씬 더 위협적으로 느껴집니다.

## 이 글에서 다룰 문제

- 언제 Alembic revision graph가 branch로 갈라질까요?
- `branch_labels`와 `depends_on`은 각각 정확히 무슨 역할일까요?
- 두 개의 head를 `alembic merge`로 어떻게 합칠까요?
- multi-head 상태에서 `upgrade`와 `downgrade`는 어떻게 동작할까요?
- 팀 차원에서 branch 사고를 줄이려면 어떤 운영 규칙이 필요할까요?

## 왜 중요한가

여러 사람이 병렬로 PR을 여는 팀에서는 Alembic branch가 거의 매주 생깁니다. branch 자체는 자연스러운 현상이지만, deploy 직전에 `Multiple head revisions are present`가 튀어나오면 공포감이 커집니다. 이 글은 그 순간을 차분하게 정리하는 가이드입니다.

## 멘탈 모델

> alembic revision graph는 git과 같은 **DAG(directed acyclic graph)**입니다. 두 사람이 같은 head에서 revision을 만들면 두 개의 새 head가 생기고, `alembic merge`는 그 둘을 부모로 가지는 새 revision을 만들어 graph를 다시 하나의 head로 되돌립니다.

git 비유로 보면 `alembic merge`는 `git merge`입니다. 다만 merge revision은 새 schema 변경을 넣는 곳이 아니라, 갈라진 graph를 다시 꿰매는 구조적 revision입니다.

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

핵심은 `down_revision`이 **tuple**이라는 점과, `upgrade`/`downgrade`가 **비어 있다**는 점입니다. merge는 graph만 통합합니다.

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

<!-- toc:begin -->
<!-- toc:end -->

## 참고 자료

- Alembic: Working with Branches — https://alembic.sqlalchemy.org/en/latest/branches.html
- Alembic: Merging Branches — https://alembic.sqlalchemy.org/en/latest/branches.html#merging-branches
- Alembic: depends_on — https://alembic.sqlalchemy.org/en/latest/branches.html#referencing-dependencies
- Alembic: ScriptDirectory API — https://alembic.sqlalchemy.org/en/latest/api/script.html

Tags: Python, Alembic, branch, merge, depends_on, SQLite
