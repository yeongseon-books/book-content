---
title: "branch와 merge: 동시에 만든 revision을 합치는 법"
series: alembic-101
episode: 5
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
  - branch
  - merge
  - depends_on
  - SQLite
last_reviewed: '2026-05-03'
---

# branch와 merge: 동시에 만든 revision을 합치는 법

## 이 글에서 배울 것

- alembic의 revision graph가 언제 branch로 갈라지는가
- `branch_labels`와 `depends_on`의 정확한 용도
- `alembic merge`로 두 head를 하나로 합치는 방법
- multi-head 상태에서의 `upgrade`/`downgrade` 동작
- 팀에서 branch 사고를 줄이는 운영 규칙

## 왜 중요한가

여러 사람이 동시에 PR을 만드는 팀에서는 alembic branch가 거의 매주 발생합니다. branch 자체는 정상 동작이지만, 처음 만나면 `Multiple head revisions are present` 에러로 배포가 멈추는 일이 흔합니다. 이 글은 그 상황을 두려워하지 않고 차분히 머지하기 위한 가이드입니다.

## Mental Model

> alembic revision graph는 git 브랜치와 똑같이 **DAG(directed acyclic graph)**입니다. 같은 head에서 두 사람이 revision을 만들면 두 개의 새 head가 생깁니다. `alembic merge`는 두 head를 자식으로 가지는 새 revision을 생성해 단일 head로 되돌립니다.

git으로 비유하면 `alembic merge`는 `git merge`와 같습니다. 다른 점은 머지 결과물에 schema 변경을 새로 넣지 않는다는 것입니다. 단지 graph만 합칩니다.

## 핵심 개념

### branch가 생기는 순간

```
A → B → C  (head: C)
        ↑
      Alice가 D, Bob이 E를 동시에 생성
        ↓
A → B → C → D  (head: D)
            ↘
              E  (head: E)
```

`alembic heads`를 실행하면 두 개의 head가 보입니다.

```bash
$ alembic heads
d1e2f3a4b5c6 (head)
e7f8a9b0c1d2 (head)
```

이 상태에서 `alembic upgrade head`는 ambiguous error를 냅니다.

### `branch_labels`와 `depends_on`

```python
revision = "d1e2f3a4b5c6"
down_revision = "c1234567890a"
branch_labels = ("billing",)        # 이 revision이 속한 브랜치 이름
depends_on = ("e7f8a9b0c1d2",)      # 다른 브랜치의 특정 revision에 의존
```

- `branch_labels`: 의도적으로 별도 브랜치를 운영할 때 사용 (예: 같은 DB에서 별도 도메인의 마이그레이션을 분리). `alembic upgrade billing@head`처럼 호출할 수 있습니다.
- `depends_on`: 한 브랜치의 revision이 다른 브랜치의 revision이 먼저 적용되어 있어야 할 때 사용. cross-branch 의존성을 명시합니다.

대부분의 일반 팀 환경에서는 둘 다 사용하지 않고, branch가 생기면 곧바로 머지로 닫습니다.

### `alembic merge`

```bash
alembic merge -m "merge billing and audit branches" d1e2f3a4b5c6 e7f8a9b0c1d2
```

다음과 같은 머지 revision이 생성됩니다.

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

핵심: `down_revision`이 **튜플**이고 `upgrade`/`downgrade`는 **빈 함수**입니다. 머지는 graph 통합만 합니다.

### multi-head 상태의 명령

```bash
alembic heads                      # 현재 head 목록
alembic upgrade heads              # 모든 head를 끝까지 적용 (s 주의)
alembic upgrade <revision_id>      # 특정 revision까지만
alembic upgrade billing@head       # branch_labels로 지정
```

`head`(단수)와 `heads`(복수)의 차이를 기억하세요. 머지 전에는 `heads`를 써야 합니다.

## Before-After

```text
# Before: 머지 없이 push했다가 배포가 막힌 상태
$ alembic upgrade head
ERROR: Multiple head revisions are present for given argument 'head';
please specify a specific target revision...
```

```bash
# After: heads를 확인하고 머지 → 단일 head로 복귀
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

배포 직전에 머지 revision을 PR로 올리면 같은 상황을 사전에 막을 수 있습니다.

## 단계별 실습

### 1단계: branch 재현

로컬에서 branch를 만들어 보면서 감을 잡습니다.

```bash
# Alice의 작업
git checkout -b feature-a
alembic revision -m "add billing column"

# Bob의 작업 (같은 base에서)
git checkout master
git checkout -b feature-b
alembic revision -m "add audit column"

# 둘 다 master에 머지된 후
git checkout master
git merge feature-a
git merge feature-b
alembic heads
```

여기서 두 개의 head가 보입니다.

### 2단계: 머지 revision 생성

```bash
alembic merge -m "merge billing and audit" <id1> <id2>
```

생성된 파일은 commit합니다. 보통 `upgrade`/`downgrade`는 비워 둡니다.

### 3단계: 적용

```bash
alembic upgrade head
```

이제 head가 하나로 돌아왔으므로 평소와 같이 진행됩니다.

### 4단계: cross-branch 의존성이 있을 때

`feature-b`가 `feature-a`의 컬럼을 사용한다면 `depends_on`을 명시합니다.

```python
# feature-b의 revision
revision = "e7f8a9b0c1d2"
down_revision = "c1234567890a"
depends_on = ("d1e2f3a4b5c6",)  # feature-a의 revision
```

`alembic upgrade head`는 의존성을 보고 정확한 순서로 적용합니다.

### 5단계: 의도적 long-running branch

별도 도메인을 분리해서 운영할 때만 `branch_labels`를 씁니다.

```python
revision = "abc123"
down_revision = None
branch_labels = ("audit",)
```

`alembic upgrade audit@head`로 audit 브랜치만 적용할 수 있습니다. 일반 팀에는 거의 필요 없습니다.

## 자주 하는 실수

- **`heads`(복수)와 `head`(단수)를 혼동.** 머지 전 상태에서 `head`는 ambiguous error를 냅니다.
- **머지 revision의 `upgrade`에 schema 변경을 넣기.** 머지 단계에서 새 변경을 섞으면 추적이 어려워집니다. 머지는 graph 통합 전용으로.
- **branch_labels를 의미 없이 남용.** 일반 팀의 일상적 branch는 머지로 곧장 닫는 편이 깔끔합니다.
- **PR에서 마이그레이션 충돌을 조기에 발견하지 못함.** CI에 `alembic heads`가 두 개 이상이면 fail로 처리하는 단계를 두세요.
- **머지 후에 down_revision tuple 순서를 손으로 바꾸기.** 의미는 같지만 review가 혼란스러워집니다. autogenerate 결과의 순서를 그대로 둡니다.

## 실무에서 쓰는 패턴

- **CI: head는 항상 1개여야 한다.** `python -c "from alembic.config import Config; from alembic.script import ScriptDirectory; cfg=Config('alembic.ini'); s=ScriptDirectory.from_config(cfg); assert len(list(s.get_heads()))==1"` 같은 가드를 둡니다.
- **PR 충돌 시 nonce-revision 워크플로우.** 두 PR 중 늦게 머지하는 쪽이 머지 revision까지 같이 PR에 포함합니다.
- **머지 revision의 메시지 컨벤션.** `merge <branchA> and <branchB>`로 통일.
- **`depends_on`은 정말 필요할 때만.** 보통은 두 revision을 같은 PR에 묶어서 단일 brunch로 만드는 편이 단순합니다.
- **`alembic history --verbose`로 graph 시각화.** 사고 났을 때 가장 빨리 상황 파악이 됩니다.

## 체크리스트

- [ ] 머지 후 `alembic heads` 결과가 한 줄(head 1개)이다
- [ ] 머지 revision의 `upgrade`/`downgrade`는 비어 있다
- [ ] CI에서 multi-head 상태가 검출된다
- [ ] cross-branch 의존성이 있다면 `depends_on`이 명시되어 있다
- [ ] `branch_labels`는 정말 분리된 도메인일 때만 사용한다
- [ ] 머지 메시지가 `merge <X> and <Y>` 컨벤션을 따른다

## 연습 문제

1. 로컬 SQLite 환경에서 두 개의 head를 만든 뒤 `alembic merge`로 합쳐 보세요.
2. 머지 revision의 `down_revision`이 튜플인지 직접 확인하세요.
3. CI에 head 개수를 검사하는 스크립트를 추가해 multi-head PR이 차단되는지 확인하세요.

## 정리, 다음 글

alembic branch는 git branch와 같은 모델입니다. 두려워할 일이 아니고, `alembic merge`로 graph만 합치면 됩니다. CI에서 head 개수를 강제하는 한 줄이 팀 전체의 사고를 크게 줄여 줍니다.

다음 글은 schema가 아닌 데이터 자체를 바꾸는 데이터 마이그레이션 패턴을 다룹니다.

## 참고 자료

- Alembic: Working with Branches — https://alembic.sqlalchemy.org/en/latest/branches.html
- Alembic: Merging Branches — https://alembic.sqlalchemy.org/en/latest/branches.html#merging-branches
- Alembic: depends_on — https://alembic.sqlalchemy.org/en/latest/branches.html#referencing-dependencies
- Alembic: ScriptDirectory API — https://alembic.sqlalchemy.org/en/latest/api/script.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, branch, merge, depends_on, SQLite
