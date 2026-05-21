---
episode: 10
language: ko
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- github-flow
- git-workflow
- conventional-commits
- semantic-versioning
- code-review
- release-tag
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Git & GitHub 101 (10/10): 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로"
seo_description: issue부터 PR, merge, release tag까지 이어지는 실전 흐름을 설명합니다.
---

# Git & GitHub 101 (10/10): 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로

명령을 따로따로 아는 것과 팀이 실제로 어떻게 출고하는지 아는 것은 다릅니다. 마지막으로 필요한 것은 지금까지의 명령을 하나의 반복 가능한 사이클로 묶는 일입니다.

이 글은 Git/GitHub 101 시리즈의 마지막 글입니다. 여기서는 앞선 1~9편의 도구를 issue, branch, PR, merge, tag 흐름으로 묶어 실전 워크플로를 정리합니다.

![Git & GitHub 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/10/10-01-mental-model.ko.png)
*Git & GitHub 101 10장 흐름 개요*

## 먼저 던지는 질문

- GitHub Flow는 왜 작은 팀에서 특히 잘 맞을까요?
- issue, branch, commit, PR, merge, tag는 어떤 순서로 연결될까요?
- 흐름 중간에 잘못된 branch에 commit하거나, 잘못 push했을 때 어떤 명령으로 회복할까요?

## 왜 중요한가

같은 `git commit`도 어디에 찍느냐에 따라 의미가 달라집니다. feature branch의 중간 commit인지, squash merge 후 `main`에 남을 대표 기록인지, release 직전 태그와 함께 묶일 변경인지에 따라 읽는 방법이 달라집니다. workflow는 결국 팀의 약속입니다.

GitHub Flow는 그 약속을 가장 단순한 형태로 보여 줍니다. `main`은 항상 배포 가능하게 유지하고, 새 작업은 짧은 branch에서 처리하고, PR로 review를 받고, merge 후 필요하면 release tag를 붙입니다. 이 흐름이 몸에 붙으면 잘못된 branch commit, 동료 commit을 덮는 force push, 정리되지 않은 release 같은 사고가 크게 줄어듭니다.

## 핵심 그림

issue가 입구이고, tag와 issue close가 출구입니다. 그 사이의 단계는 모두 앞선 글에서 따로 배운 명령입니다. 이번 글의 목표는 이들을 하나의 문장처럼 이어서 읽게 만드는 것입니다.

## 핵심 개념

| 개념 | 설명 |
| --- | --- |
| GitHub Flow | `main`은 항상 배포 가능, 모든 변경은 짧은 feature branch, merge는 PR 경유 |
| Squash merge | feature branch의 commit을 하나로 묶어 `main`에 올리는 방식 |
| Semantic versioning | `MAJOR.MINOR.PATCH` 버전 규칙 |
| Release tag | 특정 commit에 붙이는 버전 이름표 |
| `--force-with-lease` | remote에 새 작업이 생겼다면 force push를 거부하는 안전 장치 |
| Branch protection | `main` 직접 push 금지, PR/리뷰/CI 강제 설정 |

## 단계별 실습

### 1. issue로 작업 정의하기

```bash
$ gh issue create \
    --title "Add rate limit to login endpoint" \
    --body "Block password-guessing attempts by capping logins from a single IP at 5 per minute."

Creating issue in yeongseon/vacation-notes

https://github.com/yeongseon/vacation-notes/issues/42
```

issue 번호는 `#42`라고 가정합니다.

### 2. feature branch에서 작업 시작하기

```bash
$ git switch main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
$ git pull
Already up to date.
$ git switch -c feat/login-rate-limit
Switched to a new branch 'feat/login-rate-limit'
```

### 3. 작은 commit 두 개 쌓기

```bash
$ git add app/auth/rate_limit.py
$ git commit -m "feat(auth): add per-IP rate limiter"
[feat/login-rate-limit a1b2c3d] feat(auth): add per-IP rate limiter
 1 file changed, 28 insertions(+)
$ git add tests/auth/test_rate_limit.py
$ git commit -m "test(auth): cover rate-limit boundary cases"
[feat/login-rate-limit b2c3d4e] test(auth): cover rate-limit boundary cases
 1 file changed, 34 insertions(+)
```

### 4. origin에 push하기

```bash
$ git push -u origin feat/login-rate-limit
Enumerating objects: 12, done.
Counting objects: 100% (12/12), done.
Writing objects: 100% (8/8), 1.42 KiB | 1.42 MiB/s, done.
Total 8 (delta 4), reused 0 (delta 0)
remote:
remote: Create a pull request for 'feat/login-rate-limit' on GitHub by visiting:
remote:      https://github.com/yeongseon/vacation-notes/pull/new/feat/login-rate-limit
remote:
To github.com:yeongseon/vacation-notes.git
 * [new branch]      feat/login-rate-limit -> feat/login-rate-limit
Branch 'feat/login-rate-limit' set up to track 'origin/feat/login-rate-limit'.
```

### 5. PR 만들고 issue 연결하기

```bash
$ gh pr create \
    --base main \
    --title "feat(auth): add login rate limit" \
    --body "Closes #42

Returns 429 once the per-minute cap is hit. The limiter starts as an
in-memory dict and moves to a Redis backend in the next PR."

Creating pull request for feat/login-rate-limit into main in yeongseon/vacation-notes

https://github.com/yeongseon/vacation-notes/pull/17
```

### 6. 리뷰 피드백을 amend와 safe force push로 반영하기

```bash
$ # rename the test variable, then
$ git add tests/auth/test_rate_limit.py
$ git commit --amend --no-edit
[feat/login-rate-limit c3d4e5f] test(auth): cover rate-limit boundary cases
 Date: Tue May 5 14:08:11 2026 +0900
 1 file changed, 2 insertions(+), 2 deletions(-)
$ git push --force-with-lease
To github.com:yeongseon/vacation-notes.git
 + b2c3d4e...c3d4e5f feat/login-rate-limit -> feat/login-rate-limit (forced update)
```

### 7. squash merge로 `main`에 반영하기

```bash
$ gh pr merge 17 --squash --delete-branch
✓ Squashed and merged pull request #17 (feat(auth): add login rate limit)
✓ Deleted branch feat/login-rate-limit and switched to branch main
$ git pull
Updating 9c8b7a6..d5e6f7a
Fast-forward
 app/auth/rate_limit.py        | 28 ++++++++++++++++
 tests/auth/test_rate_limit.py | 34 +++++++++++++++++++
 2 files changed, 62 insertions(+)
```

### 8. release tag 찍기

```bash
$ git tag -a v0.3.0 -m "Add per-IP login rate limit (#17)"
$ git push --tags
Enumerating objects: 1, done.
To github.com:yeongseon/vacation-notes.git
 * [new tag]         v0.3.0 -> v0.3.0
```

### 9. issue가 닫혔는지 확인하기

```bash
$ gh issue view 42
Add rate limit to login endpoint
Closed • yeongseon opened about 1 hour ago

  Block password-guessing attempts by capping logins from a single IP at 5 per minute.

  ...

  Closed by pull request #17 (Squashed and merged)
```

## merge 직전 의사결정 흐름

실전에서는 "PR을 열었다"와 "이제 merge해도 된다" 사이에 생각보다 많은 판단이 들어갑니다. 아래 흐름은 작은 팀이 GitHub Flow를 운영할 때 최소한으로 확인할 질문을 정리한 것입니다.

![merge 직전 의사결정 흐름](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/10/10-01-the-decision-flow-before-you-press-merge.ko.png)

*Issue 범위 점검부터 merge 방식과 release tag 판단까지 이어지는 GitHub Flow 의사결정 흐름*

이 흐름을 팀이 공유하면 merge 버튼이 단순히 "눌러도 되는 버튼"이 아니라, 사전 조건이 충족됐을 때만 쓰는 마지막 단계라는 감각이 생깁니다.

## merge 직전에 보는 검증 루틴

issue부터 tag까지 한 번에 가르친 글일수록 마지막 검증 순서가 있어야 실제 운영에서 덜 흔들립니다. 최소한 아래 순서는 고정해 두는 편이 좋습니다.

1. `git status`로 working tree가 깨끗한지 확인합니다.
2. `git log --oneline origin/main..HEAD`로 PR에 들어갈 commit 목록을 읽습니다.
3. `git diff --stat origin/main...HEAD`로 범위가 예상보다 커지지 않았는지 봅니다.
4. PR 본문에 `Closes #N`, 검증 방법, release tag 필요 여부가 있는지 확인합니다.
5. CI 결과와 required review가 모두 통과했는지 확인합니다.
6. merge 후 `main`을 pull하고, 필요하면 annotated tag를 만들고, 사용한 branch를 삭제합니다.

이 루틴은 화려한 자동화보다 먼저 팀의 실수를 줄여 줍니다. 특히 3번과 4번은 PR이 비대해지거나 issue 연결이 빠지는 문제를 초기에 잡아냅니다.

## squash, merge commit, rebase merge를 어떻게 고를까

입문 단계에서는 "팀 기본값을 하나 정하고 대부분은 그걸 따른다"고 이해하는 편이 좋습니다. 그래도 판단 기준은 알아 두는 편이 좋습니다.

| 방식 | 잘 맞는 상황 | 주의할 점 |
| --- | --- | --- |
| Squash merge | PR 단위로 `main` log를 짧고 읽기 좋게 유지하고 싶을 때 | branch 안 commit 세부 이력은 `main`에서 사라집니다 |
| Merge commit | feature branch 구조와 병합 시점을 history에 그대로 남기고 싶을 때 | `main` 그래프가 더 빨리 복잡해집니다 |
| Rebase merge | merge bubble 없이 개별 commit을 선형으로 유지하고 싶을 때 | commit hash가 바뀌므로 추적 문맥을 함께 읽어야 합니다 |

작은 팀이나 입문 저장소에서는 squash merge가 가장 설명하기 쉽습니다. 반대로 여러 commit 자체가 중요한 학습 자료거나, branch 구조를 history에서 보존해야 한다면 merge commit이 더 낫습니다.

## 회복 흐름 표

| 상황 | 회복 명령 | 메모 |
| --- | --- | --- |
| 잘못된 branch에 commit함, 아직 push 전 | `git log -1 --format=%H` → `git switch <correct-branch>` → `git cherry-pick <hash>` → 원래 branch에서 `git reset --hard HEAD~1` | push 전일 때만 안전 |
| 직전 message만 고치고 싶음 | `git commit --amend -m "..."` | hash 변경 |
| 이미 push한 commit을 취소하고 싶음 | `git revert <hash>` → `git push` | 새 commit으로 되돌림 |
| squash merge된 PR을 되돌리고 싶음 | `git revert <squash-commit-hash>` → `git push` | `main`에는 보통 하나의 squash commit만 남음 |
| 로컬 작업을 잃어버림 | `git reflog` → 이전 HEAD hash 확인 → `git switch -c rescue <hash>` | reflog는 일정 기간 유지 |
| secret을 push함 | secret 회수 → `git filter-repo`로 history 정리 → 협업자 재clone 안내 | 회수가 먼저 |
| force push로 동료 commit을 덮음 | reflog에서 잃은 hash 찾기 → 해당 hash로 branch 생성 → `--force-with-lease`로 복구 | 그래서 plain `--force`를 피함 |

## 자주 하는 실수

- `main`에 직접 commit해 흐름 전체를 무너뜨립니다.
- PR을 너무 크게 만들어 리뷰가 멈춥니다.
- plain `--force`를 습관처럼 사용합니다.
- merge 직후 tag를 잊어 release 시점을 나중에 찾기 어렵게 만듭니다.
- issue 없이 PR부터 열어 작업 의도가 흩어집니다.

## 실무에서는 이렇게 본다

팀 단위에서는 사람의 기억보다 자동 장치가 더 중요합니다. `main`에 branch protection을 걸고, PR template을 두고, CODEOWNERS로 리뷰어를 자동 지정하고, required CI로 lint/test/build를 강제합니다. 여기에 commit message lint까지 붙이면 흐름이 스스로 유지됩니다.

또한 squash merge를 기본으로 두면 `main`의 log가 PR 단위로 정리되어 읽기 쉬워집니다. feature branch 안에서는 작은 atomic commit을 자유롭게 쌓되, 공유 이력에서는 한 PR이 한 줄로 보이게 만드는 방식입니다.

그리고 회복 명령은 문제를 만든 뒤 찾기보다, 팀 문서에 표로 미리 넣어 두는 편이 훨씬 낫습니다. 잘못된 branch commit, revert, safe force push, secret 회수 같은 항목을 runbook처럼 옆에 두면 실수한 뒤에도 더 침착하게 대응할 수 있습니다.

## 체크리스트

- [ ] issue가 먼저 있고 PR 본문에 `Closes #N`이 들어갔습니까?
- [ ] feature branch 이름이 `<type>/<slug>` 규칙을 따릅니까?
- [ ] commit이 atomic하고 Conventional Commits 형식입니까?
- [ ] PR 제목도 같은 형식을 따르고 본문에 왜가 적혀 있습니까?
- [ ] force push가 필요할 때 `--force-with-lease`를 사용했습니까?
- [ ] squash merge 후 branch를 정리했습니까?
- [ ] release 시 annotated tag를 만들고 `--tags`로 push했습니까?

## 연습 문제

1. 개인 저장소에서 `feat/<slug>` branch를 만들고 두 개의 작은 commit으로 작업한 뒤 PR을 열어 보세요.
2. `git config --global alias.fpush "push --force-with-lease"`를 등록하고 이후 safe force push만 사용해 보세요.
3. 작은 PR을 squash merge한 뒤 `git tag -a v0.0.1 -m "first tagged release"`를 찍고 GitHub에 보이는지 확인해 보세요.
4. `.github/pull_request_template.md`를 만들고 요약, 관련 issue, 테스트 방법, release tag 여부 섹션을 넣어 보세요.

## 실전 CLI 시나리오

아래 예시는 feature branch에서 작업하고 main으로 합치는 가장 보편적인 흐름입니다. 핵심은 "작업 단위를 작게 자르고, 상태를 자주 확인하며, 충돌은 빠르게 해결한다"는 운영 원칙입니다.

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/auth-session
git status
git add app/auth.py tests/test_auth.py
git commit -m "feat(auth): add session refresh flow"
git push -u origin feature/auth-session
```

`git pull --ff-only`를 앞단에 두면 로컬 main이 원격과 어긋난 상태에서 오래된 기반으로 branch를 파는 실수를 줄일 수 있습니다. 또한 `git status`를 commit 직전에 반복하면 불필요한 파일이 함께 올라가는 문제를 예방할 수 있습니다.

## 브랜치 전략을 선택하는 기준

실무에서는 전략 자체보다 "팀이 어떤 리듬으로 릴리스를 내는가"가 더 중요합니다. 아래 표는 초급 팀이 자주 비교하는 세 가지 전략입니다.

| 전략 | 특징 | 적합한 상황 | 주의할 점 |
| --- | --- | --- | --- |
| Trunk-based | 짧은 branch 수명, 빠른 머지 | 배포 빈도가 높고 테스트 자동화가 있는 팀 | 작은 PR 규율이 없으면 main이 불안정해집니다 |
| GitHub Flow | main + feature branch + PR | SaaS, 웹 서비스처럼 연속 배포 중심 | 환경별 배포 정책을 별도로 정의해야 합니다 |
| Git Flow | develop/release/hotfix 등 다중 branch | 릴리스 윈도우가 고정된 제품형 조직 | 브랜치가 많아 운영 복잡도가 커집니다 |

입문 단계에서는 GitHub Flow로 시작하는 편이 안전합니다. 규칙이 단순하고 Pull Request 중심의 협업 도구와 잘 맞기 때문입니다. 이후 릴리스 요구가 복잡해지면 release branch를 추가하는 방식으로 확장하면 됩니다.

## Git Flow vs GitHub Flow vs Trunk-Based 상세 비교

아래 표는 팀이 전략을 선택할 때 바로 회의 문서에 붙일 수 있는 비교 기준입니다.

| 항목 | GitHub Flow | Trunk-Based Development | Git Flow |
| --- | --- | --- | --- |
| 기본 branch 구조 | `main` + 짧은 feature branch | `main`(trunk) 중심, branch 수명 매우 짧음 | `main` + `develop` + `release/*` + `hotfix/*` |
| 배포 리듬 | 수시 배포(continuous delivery)에 적합 | 하루 여러 번 배포하는 고빈도 환경에 적합 | 정해진 릴리스 주기(예: 2주/월간) 환경에 적합 |
| PR 크기 기대치 | 작을수록 좋음(보통 1 기능/1 버그) | 매우 작아야 함(수 시간 단위) | release branch로 묶여 PR 단위가 커지기 쉬움 |
| CI 요구 수준 | lint/test/build 필수 | 매우 강한 자동화 필수(빠른 피드백, flaky test 관리) | 중간~높음(릴리스 분기와 병합 검증 필요) |
| rollback 방식 | revert commit + 재배포 | revert/feature flag off + 재배포 | hotfix branch로 수정 후 `main`/`develop` 동시 반영 |
| hotfix 처리 | `main`에서 짧은 `hotfix/*` PR 권장 | trunk에서 즉시 수정 후 빠른 배포 | `hotfix/*`가 공식 루트, 릴리스 이력 관리 용이 |
| 릴리스 태그 운영 | merge 후 `vX.Y.Z` 태그 | 배포 가능한 commit마다 태그 또는 자동 릴리스 태그 | `release/*` 검증 후 `main` 병합 시 태그 |
| 팀 인지 부하 | 낮음 | 낮아 보이지만 규율 미흡 시 급상승 | 높음(branch 종류와 병합 규칙 다층) |
| 잘 맞는 조직 | 스타트업, SaaS, 소규모 웹 팀 | 자동화 성숙도가 높은 제품 팀 | 다수 버전 동시 운영, 레거시 제품 라인 |

중요한 것은 전략 이름보다 팀 규칙의 명확성입니다

## release tagging을 설계하는 방법

태그는 "이 commit이 고객에게 나간 기준점"을 남기는 작업입니다.

아래는 release tagging에 자주 쓰는 최소 명령 세트입니다.

```bash
# 최신 main 기준으로 릴리스 기준점 확정
git switch main
git pull --ff-only origin main

# annotated tag 생성 (권장)
git tag -a v1.4.0 -m "Release v1.4.0: auth hardening, cache tuning"

# 태그 push
git push origin v1.4.0

# 원격 태그 확인
git ls-remote --tags origin
```

실무에서는 `annotated tag`를 기본값으로 두는 편이 좋습니다. 작성자, 날짜, 메시지를 함께 남길 수 있어 추적성이 높기 때문입니다.

## Semantic Versioning과 태그를 연결하는 규칙

`MAJOR.MINOR.PATCH`는 변경 영향도를 커뮤니케이션하는 계약입니다.

| 버전 증가 | 의미 | 태그 예시 | PR/릴리스 판단 기준 |
| --- | --- | --- | --- |
| PATCH | 하위 호환 버그 수정 | `v1.4.3` | API 계약 변경 없음, 회귀 수정/안정화 중심 |
| MINOR | 하위 호환 기능 추가 | `v1.5.0` | 기존 사용법 유지 + 기능 확장 |
| MAJOR | 비호환 변경 포함 | `v2.0.0` | API/동작 계약이 깨짐, 마이그레이션 가이드 필요 |

실수 방지를 위해 팀 문서에 "버전 판단 체크 질문"을 넣어 두는 것이 좋습니다.

1. 기존 클라이언트 코드가 수정 없이 동작합니까?
2. 공개 API의 요청/응답 스키마가 바뀌었습니까?
3. 설정값, 환경변수, 권한 정책에 비호환 변경이 있습니까?

이 세 질문 중 2번 또는 3번이 "예"라면 MAJOR 가능성을 먼저 검토하는 편이 안전합니다.

## hotfix branch 운영: 긴급 수정에도 기록을 남기는 방법

hotfix는 속도와 추적성을 동시에 잡아야 합니다.

```bash
# 1) 프로덕션 기준 main에서 hotfix 브랜치 생성
git switch main
git pull --ff-only origin main
git switch -c hotfix/login-null-check

# 2) 수정 + 테스트
git add app/auth.py tests/test_auth.py
git commit -m "fix(auth): guard null token path in login"

# 3) 원격 push 후 PR 생성
git push -u origin hotfix/login-null-check
gh pr create --base main --title "fix(auth): hotfix null token login crash" --body "Closes #108"
```

핵심은 hotfix도 PR을 거쳐 승인 로그를 남기고, 배포 후 재발 방지 issue를 분리하는 것입니다.

Git Flow를 쓰는 팀이라면 hotfix merge 방향을 한 번 더 명확히 적어 두어야 합니다. 즉, `hotfix/*`를 `main`에 먼저 병합하고 태그를 찍은 뒤, 같은 변경을 `develop`에도 반영해야 다음 릴리스에서 수정이 유실되지 않습니다.

## CI/CD에 workflow를 연결하기

좋은 workflow는 파이프라인으로 유지됩니다. 아래 네 가지는 최소 자동화 항목입니다.

1. PR 열림/업데이트마다 `lint + test + build` 실행
2. `main` 보호 규칙에 required status check 연결
3. 태그 push(`v*`) 시 릴리스 노트 생성 및 배포 job 실행
4. 실패 시 배포 중단과 알림 전송

아래는 GitHub Actions 기준의 최소 예시입니다.

```yaml
name: ci-cd

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
    tags:
      - "v*"

jobs:
  verify:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q

  release:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/release.sh
```

핵심은 "통과하지 못하면 merge할 수 없게 만든다"는 제약입니다

## 팀 conventions 문서 예시

workflow를 말로만 공유하면 사람마다 해석이 달라집니다. 저장소에 운영 문서를 고정해 두는 편이 좋습니다.

```md
# Team Git Conventions

## 1) Branch naming
- feature: `feat/<scope>-<slug>`
- bugfix: `fix/<scope>-<slug>`
- hotfix: `hotfix/<slug>`

## 2) Commit message
- Conventional Commits 사용
- 한 commit은 한 의도(atomic)

## 3) Pull Request
- 본문에 반드시 `Closes #N`
- "무엇"보다 "왜"를 먼저 기술
- 테스트 방법(재현 명령) 필수

## 4) Merge policy
- 기본 merge 방식: squash
- required review 1명 이상
- required checks: lint, test, build

## 5) Release tagging
- 버전 규칙: Semantic Versioning
- 태그 형식: `vMAJOR.MINOR.PATCH`
- annotated tag만 허용

## 6) Emergency hotfix
- `main` 기준 `hotfix/*` 생성
- PR 승인 후 배포
- 배포 후 재발 방지 issue 생성
```

이 문서의 목적은 완벽한 규칙집이 아니라 "팀의 기본값을 하나로 맞추는 기준점"입니다.

## 충돌 해결 절차를 표준화하기

충돌은 실패가 아니라 동시 작업의 자연스러운 신호입니다. 중요한 것은 해결 순서와 검증 절차를 팀 공통 규칙으로 맞추는 일입니다.

1. 충돌 파일을 확인하고, 어느 변경이 도메인 규칙에 맞는지 먼저 결정합니다.
2. 마커(`<<<<<<<`, `=======`, `>>>>>>>`)를 제거하면서 의도한 최종 코드를 남깁니다.
3. 단위 테스트와 정적 검사를 실행해 문법/동작 회귀를 확인합니다.
4. 충돌 해결 commit을 별도로 남겨 리뷰어가 판단 근거를 읽을 수 있게 합니다.

```bash
git fetch origin
git switch feature/auth-session
git merge origin/main
# 충돌 해결 후
git add app/auth.py tests/test_auth.py
git commit -m "merge: resolve auth-session conflicts with main"
pytest -q
git push
```

`merge` 대신 `rebase`를 쓰는 팀이라면 마지막 히스토리 모양이 달라질 뿐, 충돌을 해결하고 검증해야 한다는 원칙은 같습니다. 충돌 직후 테스트를 생략하면 "머지는 됐지만 동작은 깨진" 상태가 만들어지므로 반드시 자동 검증을 붙여야 합니다.

## 리뷰 품질을 올리는 운영 팁

- PR 설명에는 "무엇을 바꿨는가"보다 "왜 이 선택을 했는가"를 먼저 적는 편이 좋습니다.
- 파일 수가 많다면 기능 단위로 commit을 분리해 reviewer가 논리 흐름을 추적하기 쉽게 만듭니다.
- `git range-diff`를 사용하면 리뷰 피드백 반영 전후의 commit 변경을 선명하게 비교할 수 있습니다.
- 긴급 수정(hotfix)은 main으로 직접 넣는 대신 작은 PR로 남겨 이력과 승인 기록을 보존합니다.

이 네 가지를 지키면 Git 명령을 많이 아는 것보다 훨씬 빠르게 협업 안정성이 올라갑니다.

## 정리

issue로 작업을 정의하고, 짧은 feature branch에서 atomic commit을 쌓고, PR로 review를 받고, squash merge로 `main`에 반영하고, 필요하면 tag를 찍는 것까지가 하나의 실전 사이클입니다. 사고가 나면 회복 표를 다시 펼치고, 팀 차원에서는 branch protection, PR template, CODEOWNERS, CI로 흐름을 자동 강제하는 편이 가장 안정적입니다.

이번 글로 Git/GitHub 101 시리즈를 마칩니다. 다음 단계는 이 흐름에 GitHub Actions 같은 자동화를 더해 PR마다 검사하고 tag마다 release note를 만드는 일입니다.

## 처음 질문으로 돌아가기

- **GitHub Flow는 왜 작은 팀에서 특히 잘 맞을까요?**
  - 규칙 수가 적고 PR 중심 도구와 바로 맞물려, issue부터 merge/tag까지 같은 리듬으로 반복하기 쉽기 때문입니다. branch protection과 required CI를 함께 두면 소규모 팀에서도 품질 하한을 안정적으로 유지할 수 있습니다.
- **issue, branch, commit, PR, merge, tag는 어떤 순서로 연결될까요?**
  - issue로 작업 범위를 정의하고, feature 또는 hotfix branch에서 atomic commit을 만든 뒤, PR 리뷰와 CI 검증을 통과해 `main`에 병합합니다. 마지막으로 Semantic Versioning 기준으로 태그를 붙여 배포 기준점을 확정합니다.
- **흐름 중간에 잘못된 branch에 commit하거나, 잘못 push했을 때 어떤 명령으로 회복할까요?**
  - push 전에는 `cherry-pick`과 `reset`으로 복구하고, push 후에는 `revert`를 기본으로 사용합니다. 이력 재작성(force push)이 필요하면 반드시 `--force-with-lease`를 사용하고, 사고 대응 절차를 팀 conventions 문서에 고정해 재발을 막는 것이 핵심입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- [Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기](./05-merge-and-conflict.md)
- [Git & GitHub 101 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기](./06-github-repository.md)
- [Git & GitHub 101 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지](./07-pull-request.md)
- [Git & GitHub 101 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법](./08-issue-and-project.md)
- [Git & GitHub 101 (9/10): 좋은 commit message 쓰기: Conventional Commits와 좋은 본문](./09-good-commit-message.md)
- **실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [GitHub Docs — GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow) — issue, branch, PR, merge, branch 정리까지 이어지는 이 글의 전체 흐름을 공식적으로 정리합니다.
- [GitHub Docs — About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github) — squash merge, merge commit, rebase merge의 선택 기준을 비교할 때 직접 참고할 수 있습니다.
- [git-push manual](https://git-scm.com/docs/git-push#Documentation/git-push.txt---force-with-lease) — `--force-with-lease`가 plain `--force`보다 왜 안전한지 설명하는 기준 문서입니다.
- [git-tag manual](https://git-scm.com/docs/git-tag) — annotated tag 생성과 release 시점 표시 방법을 공식 문법으로 확인할 수 있습니다.
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) — `MAJOR.MINOR.PATCH` 버전 증가 규칙을 release tagging 판단과 연결해 읽을 수 있습니다.
- [GitHub Docs — About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches) — direct push 금지, review, status checks 같은 guardrail을 GitHub 설정 기준으로 설명합니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/10-real-world-workflow)

Tags: github-flow, git-workflow, conventional-commits, semantic-versioning, code-review, release-tag
