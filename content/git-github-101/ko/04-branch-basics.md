---
episode: 4
language: ko
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- git-branch
- git-switch
- git-checkout
- HEAD
- parallel-development
- feature-branch
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: branch 기초 - 만들고 옮기고 비교하기
seo_description: branch를 포인터로 이해하고 만들기, 전환, 비교를 익히는 글입니다.
---

# branch 기초 - 만들고 옮기고 비교하기

branch를 이해하는 순간 Git은 백업 도구에서 병렬 작업 도구로 바뀝니다. 같은 폴더 안에서 로그인 기능도 만들고 버그 수정도 하면서, 각각의 작업 줄기를 안전하게 나눌 수 있기 때문입니다.

이 글은 Git/GitHub 101 시리즈의 네 번째 글입니다. 여기서는 branch를 만들고, 옮기고, 비교하는 흐름을 먼저 익히고 merge는 다음 글로 넘깁니다.

## 이 글에서 다룰 문제

> branch는 폴더 복사가 아니라 특정 commit을 가리키는 움직이는 포인터이며, `HEAD`는 지금 내가 어느 branch에서 작업 중인지 가리키는 또 하나의 포인터입니다.

- branch는 왜 파일 복사본이 아니라 포인터라고 할까요?
- `git branch`와 `git switch`는 역할이 어떻게 다를까요?
- `HEAD`는 branch와 어떤 관계를 가질까요?
- 두 branch가 서로 무엇이 다른지 어떻게 읽을 수 있을까요?
- branch 이름 변경과 삭제는 언제 안전할까요?

## 왜 중요한가

작업이 하나뿐일 때는 `main`만으로도 버틸 수 있습니다. 하지만 기능 개발과 버그 수정이 동시에 진행되는 순간부터는 같은 폴더 안에 여러 작업 줄기를 갖고 싶어집니다. 폴더 복사로도 흉내는 낼 수 있지만, 어느 폴더가 최신인지 기억해야 하고 변경을 다시 합치는 표준 절차도 없습니다.

branch는 같은 저장소 안에서 여러 줄기의 commit을 따로 쌓게 해 줍니다. 실험적인 변경을 `main`에 영향 없이 시도할 수 있고, 기능 작업을 리뷰 전까지 따로 두며, 협업에서는 사람마다 자기 branch에서 작업하고 PR로 합치는 흐름이 자연스럽게 만들어집니다.

## 핵심 그림

![Mental Model](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/04/04-01-mental-model.ko.png)

*Mental Model*

이 그림에서 먼저 붙잡을 것은 두 가지입니다.

- **branch는 가볍습니다.** 결국 commit hash를 저장한 작은 참조 파일입니다.
- **`HEAD`는 현재 branch를 가리킵니다.** branch를 옮기면 working tree도 그 branch가 가리키는 commit 상태에 맞춰 바뀝니다.

이 그림을 알면 "branch를 만들었는데 디스크가 거의 늘지 않았다"거나 "branch를 바꾸자 파일 목록이 달라졌다" 같은 현상이 자연스럽게 설명됩니다.

## 핵심 개념

- **branch**: 특정 commit을 가리키는 이동 가능한 포인터입니다.
- **`main`**: 기본 branch 이름으로 가장 널리 쓰입니다.
- **`HEAD`**: 지금 작업 중인 branch를 가리키는 특별한 포인터입니다.
- **`git branch`**: 목록을 보거나 새 branch를 만듭니다.
- **`git switch`**: branch 전환 전용 명령입니다.
- **`git checkout`**: 예전에는 branch 전환과 파일 복원을 함께 맡던 명령입니다.
- **fast-forward 가능 여부**: merge 시 단순 포인터 이동으로 끝날지, 새 merge commit이 필요한지 판단하는 기준입니다.

## 전후 비교

폴더 복사 방식은 이렇게 시작합니다.

```text
$ cp -r project project-feature-login
$ cp -r project project-bugfix
```

- 폴더 전체가 복제됩니다.
- 어느 폴더가 최신인지 사람이 기억해야 합니다.
- 한쪽 변경을 다른 쪽으로 옮길 표준 도구가 없습니다.

Git branch는 같은 상황을 더 작고 명확하게 다룹니다.

```text
$ git branch
* main

$ git switch -c feature/login
Switched to a new branch 'feature/login'

$ git branch
* feature/login
  main
```

같은 폴더를 유지한 채 작업 줄기만 바꾸며, 현재 위치는 `*` 표시로 확인할 수 있습니다.

## 단계별 실습

### 1. 현재 branch 확인

```text
$ git branch
* main
```

```text
$ git status
On branch main
nothing to commit, working tree clean
```

### 2. 새 branch 만들기

```text
$ git branch feature/login
$ git branch
  feature/login
* main
```

branch를 만들었다고 자동으로 이동하지는 않습니다.

### 3. branch 전환하기

```text
$ git switch feature/login
Switched to branch 'feature/login'
$ git branch
* feature/login
  main
```

만들기와 전환을 한 번에 하려면 `-c`를 씁니다.

```text
$ git switch -c feature/signup
Switched to a new branch 'feature/signup'
```

옛 문법은 다음과 같습니다.

```text
$ git checkout feature/login           # move
$ git checkout -b feature/signup       # create and move
```

### 4. branch별 commit 만들기

```text
$ git switch feature/login
$ echo "login form" > login.md
$ git add login.md
$ git commit -m "Add login form draft"
[feature/login a2b3c4d] Add login form draft
 1 file changed, 1 insertion(+)
 create mode 100644 login.md
```

```text
$ git log --oneline
a2b3c4d Add login form draft
e7d2c1a Add author line to README
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

`main`으로 돌아가면 이 파일은 보이지 않습니다.

```text
$ git switch main
Switched to branch 'main'
$ ls
README.md  notes.md
$ git log --oneline
e7d2c1a Add author line to README
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

### 5. 두 branch 비교하기

```text
$ git log --oneline main..feature/login
a2b3c4d Add login form draft
```

```text
$ git log --oneline --graph --decorate --all
* a2b3c4d (feature/login) Add login form draft
* e7d2c1a (HEAD -> main, feature/signup) Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

```text
$ git diff main feature/login
diff --git a/login.md b/login.md
new file mode 100644
index 0000000..2c4e0d2
--- /dev/null
+++ b/login.md
@@ -0,0 +1 @@
+login form
```

`/dev/null`은 `main` 쪽에는 그 파일이 없었다고 읽으면 됩니다.

### 6. 이름 바꾸기와 삭제

```text
$ git switch feature/signup
Switched to branch 'feature/signup'
$ echo "signup form" > signup.md
$ git add signup.md
$ git commit -m "Add signup form draft"
[feature/signup f1e2d3c] Add signup form draft
 1 file changed, 1 insertion(+)
 create mode 100644 signup.md
$ git switch main
Switched to branch 'main'
```

```text
$ git branch -m feature/signup feature/sign-up
```

```text
$ git branch -d feature/sign-up
error: The branch 'feature/sign-up' is not fully merged.
If you are sure you want to delete it, run 'git branch -D feature/sign-up'.
```

```text
$ git branch -D feature/sign-up
Deleted branch feature/sign-up (was f1e2d3c).
```

소문자 `-d`는 안전한 삭제이고, 대문자 `-D`는 강제 삭제입니다.

## 자주 하는 실수

- `git branch <name>`만 실행하고 이미 이동했다고 착각하는 경우가 많습니다.
- 미완료 변경이 있는데 branch를 옮기려다 충돌하거나 전환이 거부되기도 합니다.
- `git checkout <branch>`와 `git checkout -- <file>`를 헷갈리는 문제도 오래된 문법에서 자주 나왔습니다.
- 공백, 대문자, 특수문자가 섞인 branch 이름은 협업에서 마찰을 만듭니다.
- 아직 merge하지 않은 branch를 `-D`로 지워 버리면 복구가 어려워질 수 있습니다.
- commit hash에 직접 붙는 detached HEAD 상태를 모르고 작업을 이어 가다 기록을 잃는 경우도 있습니다.

## 실무에서는 이렇게 본다

branch는 작업 단위마다 짧게 만들고 빨리 닫는 편이 좋습니다. branch 수명이 길수록 `main`과 멀어지고, 나중 merge 비용도 커집니다. 그래서 팀에서는 보통 `feature/<summary>`, `bugfix/<summary>` 같은 규칙을 정하고 짧은 주기로 merge합니다.

또한 branch를 옮기기 전 `git status -s`를 먼저 보는 습관이 중요합니다. 지금 working tree에 떠다니는 변경이 있는지 미리 보면 branch 전환 중 생길 혼란을 크게 줄일 수 있습니다.

## 체크리스트

- [ ] `git branch`의 `*` 표시로 현재 branch를 확인했습니다.
- [ ] `git switch -c`로 만들기와 전환을 한 번에 해 봤습니다.
- [ ] 두 branch에 서로 다른 commit을 만들고 `git log --oneline --graph --decorate --all`로 비교했습니다.
- [ ] `main..feature/login`의 의미를 설명할 수 있습니다.
- [ ] `git switch`와 `git checkout`이 왜 분리됐는지 설명할 수 있습니다.
- [ ] `-d`와 `-D`의 차이를 알고 있습니다.

## 연습 문제

1. `git branch feature/notes`만 실행한 뒤 아직 `main`에 머무는지 `git status`와 `git branch`로 확인해 보세요.
2. `git switch -c feature/notes-2`로 branch를 만들고 `notes.md`를 commit한 뒤 `main`으로 돌아와 파일이 보이지 않는지 확인해 보세요.
3. `git log --oneline --graph --decorate --all`을 실행해 두 branch가 갈라지는 모양을 직접 읽어 보세요.
4. `git diff main feature/notes-2`를 실행하고 `/dev/null`이 어느 쪽에 나타나는지 설명해 보세요.
5. `git branch -d feature/notes-2`의 거절 메시지를 읽고, 이후 `git branch -D feature/notes-2` 결과를 확인해 보세요.

## 정리와 다음 글

branch는 commit을 가리키는 가벼운 포인터이고, `HEAD`는 현재 작업 branch를 가리키는 또 다른 포인터입니다. `git branch`는 만들기, `git switch`는 이동, `git switch -c`는 두 동작을 한 번에 처리합니다. branch끼리의 차이는 `git log A..B`와 `git diff A B`로 읽습니다.

다음 글에서는 갈라진 branch를 다시 합치는 `git merge`와 conflict 해결 흐름을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- **branch 기초 - 만들고 옮기고 비교하기 (현재 글)**
- merge와 conflict 해결하기 (예정)
- GitHub repository 만들기와 remote, push, pull (예정)
- Pull Request로 협업하기 (예정)
- Issue와 Project로 일감 관리하기 (예정)
- 좋은 commit message 쓰기 (예정)
- 실전 Git workflow 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Pro Git — Branches in a Nutshell](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell) — branch와 `HEAD`를 포인터로 이해하는 이 글의 핵심 멘탈 모델을 뒷받침합니다.
- [git-branch manual](https://git-scm.com/docs/git-branch) — branch 만들기, 목록 보기, 이름 변경, 삭제 문법의 기준 문서입니다.
- [git-switch manual](https://git-scm.com/docs/git-switch) — `git switch`와 `git switch -c`로 전환하는 최신 흐름을 공식적으로 확인할 수 있습니다.
- [git-checkout manual](https://git-scm.com/docs/git-checkout) — 예전 문법이 branch 전환과 파일 복원을 함께 맡았던 이유를 이해하는 데 도움이 됩니다.
- [git-log manual](https://git-scm.com/docs/git-log) — `main..feature/login`, `--graph --decorate --all`처럼 branch 차이를 읽는 명령과 연결됩니다.
- [git-diff manual](https://git-scm.com/docs/git-diff) — `git diff main feature/login`으로 branch 간 파일 차이를 비교하는 단계의 기준이 됩니다.
Tags: git-branch, git-switch, git-checkout, HEAD, parallel-development, feature-branch
