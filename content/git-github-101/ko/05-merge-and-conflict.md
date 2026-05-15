---
episode: 5
language: ko
last_reviewed: '2026-05-12'
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
title: merge와 conflict 해결하기 - 두 줄기를 다시 합치기
seo_description: merge와 conflict를 fast-forward와 three-way 기준으로 설명합니다.
---

# merge와 conflict 해결하기 - 두 줄기를 다시 합치기

branch를 나누는 일보다 더 중요한 것은 다시 합치는 일입니다. merge가 언제 포인터 이동으로 끝나고, 언제 사람이 직접 판단해야 하는 conflict로 이어지는지 알면 협업의 긴장이 크게 줄어듭니다.

이 글은 Git/GitHub 101 시리즈의 다섯 번째 글입니다. 여기서는 fast-forward, three-way merge, conflict 해결 흐름을 한 번에 정리합니다.

## 이 글에서 다룰 문제

> merge는 두 줄기의 commit을 하나의 공유 이력으로 다시 묶는 동작이며, 줄기가 아직 한 직선 위에 있으면 포인터만 옮기고, 갈라져 있으면 두 부모를 가진 새 merge commit을 만듭니다.

- fast-forward merge는 언제 일어날까요?
- three-way merge는 왜 부모가 두 개인 commit을 만들까요?
- conflict marker의 `HEAD` 쪽과 incoming branch 쪽은 어떻게 읽을까요?
- merge 도중 `git status`는 무엇을 더 보여 줄까요?
- `git merge --abort`는 언제 안전한 출구가 될까요?

## 왜 중요한가

branch를 나눠 작업했다면 결국 언젠가는 다시 합쳐야 합니다. PR이 merge될 때도, 동료의 변경을 내 branch에 가져올 때도, 장시간 작업한 기능을 `main`에 올릴 때도 merge가 일어납니다.

merge에 대한 그림이 없으면 두 가지 문제가 빨리 나타납니다. 하나는 "왜 merge commit이 또 생겼지?"라는 의문 속에서 history가 읽기 어려워지는 문제이고, 다른 하나는 conflict가 나자마자 panic에 빠져 reset이나 폴더 복사부터 시도하는 문제입니다.

이 글의 목표는 두 가지입니다. merge가 어떤 모양으로 일어날지 명령을 치기 전에 예측할 수 있게 하고, conflict가 나도 안전하게 풀거나 abort할 수 있게 만드는 것입니다.

## 핵심 그림

![Mental Model](../../../assets/git-github-101/05/05-01-mental-model.ko.png)

*Mental Model*

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

<!-- toc:begin -->
## 시리즈 목차

- [Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- **merge와 conflict 해결하기 - 두 줄기를 다시 합치기 (현재 글)**
- GitHub repository 만들기와 remote, push, pull (예정)
- Pull Request로 협업하기 (예정)
- Issue와 Project로 일감 관리하기 (예정)
- 좋은 commit message 쓰기 (예정)
- 실전 Git workflow 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- Git Reference Manual: <https://git-scm.com/doc>
- Pro Git Book - "Basic Branching and Merging": <https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging>
- `git help merge`, `git help mergetool`

Tags: git-merge, fast-forward, three-way-merge, merge-conflict, merge-abort, conflict-markers
