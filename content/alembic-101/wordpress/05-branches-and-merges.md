---
title: "바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge"
series: alembic-101
episode: 5
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

# 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 다섯 번째 글입니다.

---

팀원 A가 feature/login 브랜치에서 `revision -m "add users.last_login"`을 만들었습니다. 팀원 B는 feature/posts 브랜치에서 `revision -m "add posts table"`을 만들었습니다. 두 PR이 main에 머지되는 순간, `alembic upgrade head`를 실행하면 에러가 납니다: `FAILED: Multiple head revisions are present`. 바이브코딩 팀에서 AI가 각자의 브랜치에서 revision을 만들면 이 상황이 반드시 옵니다.

Alembic의 revision graph는 DAG(Directed Acyclic Graph)입니다. 두 revision이 같은 parent를 가리키면 branch가 생깁니다. 이것은 버그가 아니라 정상적인 상태입니다. 그러나 배포 전에는 반드시 single head로 정리해야 합니다.

`alembic merge`가 이 문제를 해결합니다. 두 head를 하나의 merge revision으로 합칩니다. 이 merge revision은 실제 DDL이 없는 빈 파일이지만, graph를 single head로 만들어 줍니다.

> **핵심 인사이트:** 바이브코딩 팀에서 branch는 피할 수 없습니다. 중요한 것은 발생했을 때 `alembic merge`로 빠르게 정리하는 것입니다. PR 머지 전에 `alembic heads` 명령으로 head가 하나인지 항상 확인하세요.

## 이 글에서 다룰 문제

- Alembic branch는 왜 발생하고, 왜 배포 전에 정리해야 할까요?
- `alembic merge`로 두 branch를 합치는 절차는 어떻게 되나요?
- merge revision은 실제로 어떻게 생겼고, 어떤 역할을 하나요?
- PR 머지 전에 branch를 예방하는 팀 규칙은 무엇인가요?
- `alembic heads`로 현재 graph 상태를 어떻게 확인할까요?

## branch 해결 절차

```bash
# 1. 현재 head 확인
alembic heads
# Output: abc123 (head), def456 (head)  <- 두 head!

# 2. merge revision 생성
alembic merge -m "merge concurrent heads" abc123 def456

# 3. 결과 확인
alembic heads
# Output: xyz789 (head)  <- single head!

# 4. 배포
alembic upgrade head
```

## 변경 전후 비교

**Before: Multiple head 상태**
```
A -> B -> C (abc123, head)
         \-> D (def456, head)
```

**After: merge 후 single head**
```
A -> B -> C -> M (xyz789, head)
         \-> D /
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `alembic heads` 미확인 후 배포 | Multiple head 에러 | 배포 전 항상 확인 |
| merge revision에 DDL 추가 | graph 복잡성 증가 | merge revision은 빈 파일 유지 |
| branch 상태로 팀 공유 | 다른 팀원 작업 블록 | PR 머지 전 정리 |
| `down_revision` 수동 수정 | graph 손상 | `alembic merge` 명령 사용 |
| CI에서 heads 검사 미적용 | branch 상태 배포 | CI에 `alembic heads` 검사 추가 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"alembic heads를 확인하고, multiple head가 있으면
alembic merge로 정리하는 방법을 알려줘"

# CI 파이프라인에 추가:
alembic heads | grep -c "(head)" | xargs -I{} test {} -eq 1
# head가 1개가 아니면 CI 실패
```

## 운영 체크리스트

- [ ] PR 머지 전에 `alembic heads`로 head 개수를 확인한다
- [ ] Multiple head 발생 시 `alembic merge`로 즉시 정리한다
- [ ] merge revision은 DDL 없이 빈 파일로 유지한다
- [ ] CI 파이프라인에 single head 검사를 추가한다
- [ ] 팀 규칙: feature 브랜치에서 revision 생성은 PR 직전에만 한다

## 처음 질문으로 돌아가기

- **Alembic branch는 왜 발생하나요?** 두 revision이 같은 `down_revision`을 가리킬 때 발생합니다. 여러 사람이 독립적으로 revision을 만들면 자연스럽게 발생합니다.
- **`alembic merge` 절차는?** `alembic heads`로 두 head를 확인하고, `alembic merge -m "merge" <head1> <head2>`로 merge revision을 생성합니다.
- **PR 머지 전 branch 예방 규칙은?** feature 브랜치 개발 중에는 revision을 만들지 않고, PR 머지 직전에 최신 main에서 revision을 생성합니다.

## 정리

branch는 바이브코딩 팀에서 피할 수 없습니다. 중요한 것은 발생했을 때 신속하게 `alembic merge`로 정리하고, CI에 single head 검사를 추가해 배포 전에 자동으로 감지하는 것입니다. 다음 글에서는 schema 변경과 데이터 변경을 분리하는 데이터 마이그레이션을 다룹니다.

## 참고 자료

- [Alembic Branches 문서](https://alembic.sqlalchemy.org/en/latest/branches.html)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/05-branches-and-merges)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- **바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
