---
episode: 5
language: ko
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- git-merge
- fast-forward
- three-way-merge
- merge-conflict
- merge-abort
- conflict-markers
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기"
seo_description: merge와 conflict를 fast-forward와 three-way 기준으로 설명합니다.
---

# Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기

branch를 나누는 일보다 더 중요한 것은 다시 합치는 일입니다. merge가 언제 포인터 이동으로 끝나고, 언제 사람이 직접 판단해야 하는 conflict로 이어지는지 알면 협업의 긴장이 크게 줄어듭니다.

이 글은 Git/GitHub 101 시리즈의 다섯 번째 글입니다. 여기서는 fast-forward, three-way merge, conflict 해결 흐름을 한 번에 정리합니다.

## 먼저 던지는 질문

- fast-forward merge는 언제 일어날까요?
- three-way merge는 왜 부모가 두 개인 commit을 만들까요?
- conflict marker의 `HEAD` 쪽과 incoming branch 쪽은 어떻게 읽을까요?

## 큰 그림

![Git & GitHub 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/05/05-01-mental-model.ko.png)

*Git & GitHub 101 5장 흐름 개요*

## 왜 중요한가

branch를 나눠 작업했다면 결국 언젠가는 다시 합쳐야 합니다. PR이 merge될 때도, 동료의 변경을 내 branch에 가져올 때도, 장시간 작업한 기능을 `main`에 올릴 때도 merge가 일어납니다.

merge에 대한 그림이 없으면 두 가지 문제가 빨리 나타납니다. 하나는 "왜 merge commit이 또 생겼지?"라는 의문 속에서 history가 읽기 어려워지는 문제이고, 다른 하나는 conflict가 나자마자 panic에 빠져 reset이나 폴더 복사부터 시도하는 문제입니다.

이 글의 목표는 두 가지입니다. merge가 어떤 모양으로 일어날지 명령을 치기 전에 예측할 수 있게 하고, conflict가 나도 안전하게 풀거나 abort할 수 있게 만드는 것입니다.

## 핵심 그림

세 가지만 기억하면 됩니다.

- **Fast-forward**: 새 commit 없이 branch 포인터만 앞으로 이동합니다.
- **Three-way merge**: 공통 조상과 양쪽 끝 commit을 비교해 새 merge commit을 만듭니다.
- **Conflict**: 같은 파일의 같은 줄을 양쪽에서 다르게 바꾸면 Git이 멈추고 사람이 결정하게 합니다.

## 핵심 개념

- **`git merge <branch>`**: 현재 branch에 다른 branch의 변경을 합칩니다.
- **fast-forward**: 직선 이력에서 가능한 포인터 이동입니다.
- **`--no-ff`**: fast-forward 가능해도 일부러 merge commit을 만듭니다.
- **three-way merge**: 갈라진 두 줄기를 공통 조상 기준으로 다시 합칩니다.
- **conflict**: Git이 자동으로 정할 수 없는 겹치는 변경입니다.
- **conflict marker**: `<<<<<<<`, `=======`, `>>>>>>>` 블록입니다.
- **`git merge --abort`**: 진행 중인 merge를 취소하고 시작 전 상태로 되돌립니다.

## 전후 비교

수동 복사는 이렇게 남습니다.

```text
$ cp feature/login.md main/login.md
$ # if both folders changed the same file, you have to remember which is right
```

무엇을 합쳤는지 history에 남지 않고, 되돌릴 표준 방법도 없습니다.

Git merge는 결과를 이력으로 남깁니다.

```text
$ git switch main
$ git merge feature/login
Updating e7d2c1a..a2b3c4d
Fast-forward
 login.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 login.md
```

## 단계별 실습

### 1. 현재 상태 확인

```text
$ git switch main
Switched to branch 'main'
$ git log --oneline --graph --decorate --all
* a2b3c4d (feature/login) Add login form draft
* e7d2c1a (HEAD -> main) Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

### 2. fast-forward merge

```text
$ git merge feature/login
Updating e7d2c1a..a2b3c4d
Fast-forward
 login.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 login.md
```

```text
$ git log --oneline --graph --decorate --all
* a2b3c4d (HEAD -> main, feature/login) Add login form draft
* e7d2c1a Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

```text
$ git branch -d feature/login
Deleted branch feature/login (was a2b3c4d).
```

### 3. 갈라진 이력 만들기

```text
$ git switch -c feature/header
Switched to a new branch 'feature/header'
$ echo "# My Project" > header.md
$ git add header.md
$ git commit -m "Add project header"
[feature/header d4e5f6a] Add project header
 1 file changed, 1 insertion(+)
 create mode 100644 header.md
```

```text
$ git switch main
Switched to branch 'main'
$ echo "Released on 2026-05-04." >> notes.md
$ git add notes.md
$ git commit -m "Append release note"
[main c1a8e9f] Append release note
 1 file changed, 1 insertion(+)
```

```text
$ git log --oneline --graph --decorate --all
* c1a8e9f (HEAD -> main) Append release note
| * d4e5f6a (feature/header) Add project header
|/
* a2b3c4d Add login form draft
* e7d2c1a Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

### 4. three-way merge

```text
$ git merge feature/header
Merge made by the 'ort' strategy.
 header.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 header.md
```

```text
$ git log --oneline --graph --decorate --all
*   b5d4c6e (HEAD -> main) Merge branch 'feature/header'
|\
| * d4e5f6a (feature/header) Add project header
* | c1a8e9f Append release note
|/
* a2b3c4d Add login form draft
* e7d2c1a Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

### 5. conflict 만들기

```text
$ git switch -c feature/header-emoji
Switched to a new branch 'feature/header-emoji'
$ printf "## My Project\n" > header.md
$ git add header.md
$ git commit -m "Use h2 for project header"
[feature/header-emoji a7b8c9d] Use h2 for project header
 1 file changed, 1 insertion(+), 1 deletion(-)
```

```text
$ git switch main
Switched to branch 'main'
$ printf "# Awesome Project\n" > header.md
$ git add header.md
$ git commit -m "Rename project header"
[main e2f3a4b] Rename project header
 1 file changed, 1 insertion(+), 1 deletion(-)
```

```text
$ git merge feature/header-emoji
Auto-merging header.md
CONFLICT (content): Merge conflict in header.md
Automatic merge failed; fix conflicts and then commit the result.
```

### 6. conflict 해결하기

```text
$ git status
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   header.md

no changes added to commit (use "git add" and/or "git commit -a")
```

```text
<<<<<<< HEAD
# Awesome Project
=======
## My Project
>>>>>>> feature/header-emoji
```

- `<<<<<<< HEAD`와 `=======` 사이가 현재 branch(`main`) 내용입니다.
- `=======`와 `>>>>>>> feature/header-emoji` 사이가 합치려던 branch 내용입니다.

예를 들어 이름은 `main` 쪽을, 헤딩 수준은 feature 쪽을 택하면 해결 결과는 이렇게 됩니다.

```text
## Awesome Project
```

```text
$ git add header.md
$ git status
On branch main
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
	modified:   header.md

$ git commit
[main f3a4b5c] Merge branch 'feature/header-emoji'
```

### 7. `--abort`로 돌아가기

```text
$ git switch -c feature/header-bold
Switched to a new branch 'feature/header-bold'
$ printf "**Awesome Project**\n" > header.md
$ git add header.md
$ git commit -m "Bold the header"
[feature/header-bold 9d8e7f6] Bold the header
 1 file changed, 1 insertion(+), 1 deletion(-)
$ git switch main
Switched to branch 'main'
$ printf "### Awesome Project\n" > header.md
$ git add header.md
$ git commit -m "Demote header to h3"
[main 1c2d3e4] Demote header to h3
 1 file changed, 1 insertion(+), 1 deletion(-)
$ git merge feature/header-bold
Auto-merging header.md
CONFLICT (content): Merge conflict in header.md
Automatic merge failed; fix conflicts and then commit the result.
```

```text
$ git merge --abort
$ git status
On branch main
nothing to commit, working tree clean
```

merge가 진행 중일 때만 `--abort`가 동작합니다.

## 자주 하는 실수

- fast-forward와 three-way merge를 같은 것으로 생각하면 history를 읽기 어려워집니다.
- conflict marker를 남긴 채 commit하면 코드를 깨뜨립니다.
- 해결 후 `git add`를 빼먹으면 Git은 아직 충돌이 끝나지 않은 것으로 봅니다.
- 헷갈린다고 폴더를 지우고 다시 clone하는 것보다 `git merge --abort`가 훨씬 안전합니다.
- `--no-ff`를 무조건 쓰거나 무조건 피하는 것도 팀 규칙과 어긋날 수 있습니다.
- merge 중간에 다른 branch로 이동하려 하면 상태가 더 복잡해집니다.

## 실무에서는 이렇게 본다

merge 전에는 가능한 한 `main`을 최신으로 맞추는 편이 좋습니다. 또한 같은 줄을 여러 branch가 동시에 건드리지 않도록 큰 포매터 변경과 기능 변경을 분리하는 것이 conflict 면적을 줄여 줍니다.

무엇보다 conflict marker를 지웠다고 끝이 아닙니다. merge 후에는 반드시 빌드와 테스트를 다시 돌려 결과가 여전히 정상인지 확인해야 합니다.

## 체크리스트

- [ ] fast-forward가 언제 일어나고 Git이 어떤 문구를 출력하는지 설명할 수 있습니다.
- [ ] three-way merge commit이 왜 부모를 둘 가지는지 설명할 수 있습니다.
- [ ] conflict marker 세 줄이 각각 어느 쪽 branch를 뜻하는지 설명할 수 있습니다.
- [ ] conflict 해결 순서를 edit → `git add` → `git commit`으로 말할 수 있습니다.
- [ ] `git merge --abort`가 언제 동작하고 언제 안 되는지 알고 있습니다.
- [ ] `git log --oneline --graph --decorate --all`에서 fast-forward와 three-way merge를 구분할 수 있습니다.

## 연습 문제

1. 단순한 새 파일 추가 branch를 만들어 fast-forward merge를 직접 확인해 보세요.
2. 서로 다른 파일을 양쪽 branch에서 수정한 뒤 merge해 `Merge made by the 'ort' strategy.` 문구를 확인해 보세요.
3. 같은 줄을 양쪽에서 다르게 수정해 conflict를 만들고 `both modified` 상태를 확인한 뒤 해결해 보세요.
4. 같은 conflict를 다시 만든 뒤 이번에는 `git merge --abort`로 되돌려 보세요.
5. fast-forward 가능한 상황에서 `git merge --no-ff`를 써 보고 그래프 모양이 어떻게 달라지는지 비교해 보세요.

## 정리와 다음 글

merge에는 크게 두 가지가 있습니다. 직선 이력이면 fast-forward로 포인터만 이동하고, 갈라진 이력이면 three-way merge로 새 commit을 만듭니다. conflict가 나면 Git은 멈추고 marker를 남기며, 사람은 파일을 고친 뒤 `git add`, `git commit`으로 마무리합니다. 어렵게 느껴지면 `git merge --abort`가 중간 탈출구가 됩니다.

다음 글에서는 로컬 저장소를 GitHub remote에 연결하고 `git remote`, `git push`, `git pull`을 순서대로 다룹니다.


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

## 처음 질문으로 돌아가기

- **fast-forward merge는 언제 일어날까요?**
  - 본문의 기준은 merge와 conflict 해결하기 - 두 줄기를 다시 합치기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **three-way merge는 왜 부모가 두 개인 commit을 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **conflict marker의 `HEAD` 쪽과 incoming branch 쪽은 어떻게 읽을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- **merge와 conflict 해결하기 - 두 줄기를 다시 합치기 (현재 글)**
- GitHub repository 만들기 - remote, push, pull 한 번에 익히기 (예정)
- Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (예정)
- Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (예정)
- 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (예정)
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [Pro Git — Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging) — fast-forward와 기본 merge 흐름을 가장 입문적으로 정리한 장입니다.
- [Pro Git — Advanced Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging) — conflict가 생겼을 때 어떤 관점으로 읽고 풀어야 하는지 한 단계 더 깊게 설명합니다.
- [git-merge manual](https://git-scm.com/docs/git-merge) — `git merge`, `--no-ff`, `--abort` 동작을 정확한 용어로 확인할 수 있습니다.
- [git-mergetool manual](https://git-scm.com/docs/git-mergetool) — 실무 메모에서 언급한 GUI/도구 기반 conflict 해결 보조 흐름과 연결됩니다.
- [git-status manual](https://git-scm.com/docs/git-status) — merge 중 `unmerged paths`, `both modified` 같은 상태 문구의 기준 문서입니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/05-merge-and-conflict)

Tags: git-merge, fast-forward, three-way-merge, merge-conflict, merge-abort, conflict-markers
