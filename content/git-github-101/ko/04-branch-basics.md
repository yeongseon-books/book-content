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
title: "Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기"
seo_description: branch를 포인터로 이해하고 만들기, 전환, 비교를 익히는 글입니다.
---

# Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기

branch를 이해하는 순간 Git은 백업 도구에서 병렬 작업 도구로 바뀝니다. 같은 폴더 안에서 로그인 기능도 만들고 버그 수정도 하면서, 각각의 작업 줄기를 안전하게 나눌 수 있기 때문입니다.

이 글은 Git/GitHub 101 시리즈의 네 번째 글입니다. 여기서는 branch를 만들고, 옮기고, 비교하는 흐름까지만 다루고, branch 사이를 합치는 merge는 별도 글에서 다룹니다.


![Git & GitHub 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/04/04-01-mental-model.ko.png)
*Git & GitHub 101 4장 흐름 개요*

## 먼저 던지는 질문

- branch는 왜 파일 복사본이 아니라 포인터라고 할까요?
- `git branch`와 `git switch`는 역할이 어떻게 다를까요?
- `HEAD`는 branch와 어떤 관계를 가질까요?

## 왜 중요한가

작업이 하나뿐일 때는 `main`만으로도 버틸 수 있습니다. 하지만 기능 개발과 버그 수정이 동시에 진행되는 순간부터는 같은 폴더 안에 여러 작업 줄기를 갖고 싶어집니다. 폴더 복사로도 흉내는 낼 수 있지만, 어느 폴더가 최신인지 기억해야 하고 변경을 다시 합치는 표준 절차도 없습니다.

branch는 같은 저장소 안에서 여러 줄기의 commit을 따로 쌓게 해 줍니다. 실험적인 변경을 `main`에 영향 없이 시도할 수 있고, 기능 작업을 리뷰 전까지 따로 두며, 협업에서는 사람마다 자기 branch에서 작업하고 PR로 합치는 흐름이 자연스럽게 만들어집니다.

## 핵심 그림

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

실수 목록을 그냥 암기하면 금방 잊습니다. 그래서 아래처럼 "왜 이 실수가 생기고, 어떻게 예방하는지"를 함께 묶어두는 편이 좋습니다.

### 실수 1) branch를 만들고 이동했다고 착각하기

`git branch feature/x`는 포인터만 만들고 현재 위치를 바꾸지 않습니다. 이 한 줄 때문에 "분명 feature에서 작업했다고 생각했는데 main에 commit이 쌓였다"는 사고가 자주 납니다.

```text
$ git branch feature/payment
$ git branch
  feature/payment
* main

$ git status
On branch main
nothing to commit, working tree clean
```

예방은 단순합니다. 새 branch를 만들 때는 기본을 `git switch -c`로 고정합니다.

```text
$ git switch -c feature/payment
Switched to a new branch 'feature/payment'
```

### 실수 2) 작업 중인 변경을 확인하지 않고 branch 전환하기

전환 직전 `git status -s`를 생략하면, 현재 변경이 새 branch로 함께 넘어가면서 의도하지 않은 혼합 작업이 생깁니다.

```text
$ git status -s
 M app.py
?? notes-tmp.md
```

이 상태에서 `git switch bugfix/login`을 하면 변경이 그대로 따라갈 수 있습니다. 다른 작업 줄기까지 섞이지 않게 하려면 전환 전에 아래 셋 중 하나를 고릅니다.

- 지금 branch에 commit한다
- 임시 저장이 필요하면 `git stash push -m "wip"`를 사용한다
- 정말 버릴 변경이면 삭제한다

### 실수 3) detached HEAD를 모른 채 commit 쌓기

commit hash로 직접 이동하면 branch가 아니라 특정 commit에 붙습니다.

```text
$ git switch --detach e7d2c1a
HEAD is now at e7d2c1a Add author line to README
```

여기서 commit은 가능하지만 어떤 branch도 자동으로 따라오지 않습니다. 나중에 찾기 어려워지는 이유입니다.

```text
$ git commit -am "Try old baseline tweak"
[detached HEAD c9d8e7f] Try old baseline tweak
 1 file changed, 1 insertion(+)
```

이 commit을 살리고 싶으면 즉시 branch를 만듭니다.

```text
$ git switch -c experiment/old-baseline
Switched to a new branch 'experiment/old-baseline'
```

### 실수 4) 안전 삭제(`-d`)와 강제 삭제(`-D`)를 같은 것으로 보기

`-d`는 merge 여부를 확인해 주는 안전장치입니다. 거절 메시지는 오류가 아니라 보호 기능입니다.

```text
$ git branch -d feature/report
error: The branch 'feature/report' is not fully merged.
If you are sure you want to delete it, run 'git branch -D feature/report'.
```

팀 작업에서는 먼저 `git log --oneline main..feature/report`로 남은 commit을 확인하고 삭제 여부를 결정합니다.

## branch 포인터를 눈으로 읽는 법

branch를 포인터라고 이해해도, 실제로는 히스토리 모양이 머릿속에서 잘 안 그려지는 경우가 많습니다. 그래서 텍스트 다이어그램으로 현재 위치를 반복해서 읽는 연습이 효과적입니다.

### 상태 A: main 하나만 있을 때

```text
C1 --- C2 --- C3 (main, HEAD)
```

- `main`이 C3를 가리킵니다.
- `HEAD`는 현재 branch인 `main`을 가리킵니다.

### 상태 B: feature branch를 만든 직후

```text
C1 --- C2 --- C3 (main, feature/login, HEAD->main)
```

- branch를 만들기만 하면 포인터가 같은 commit(C3)을 함께 가리킵니다.
- 저장소 크기가 거의 늘지 않는 이유가 여기 있습니다.

### 상태 C: feature/login으로 이동 후 commit 2개 추가

```text
              F1 --- F2 (feature/login, HEAD)
             /
C1 --- C2 --- C3 (main)
```

- `main`은 그대로 C3에 남아 있습니다.
- `feature/login`만 앞으로 이동합니다.

이 모양은 `git log --oneline --graph --decorate --all`에서 아래처럼 보입니다.

```text
$ git log --oneline --graph --decorate --all
* b91fa20 (HEAD -> feature/login) Add login API validation
* 2a11f9c Add login form draft
* e7d2c1a (main) Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

### 상태 D: main에서 다른 버그 수정 branch를 만들고 commit

```text
              F1 --- F2 (feature/login)
             /
C1 --- C2 --- C3 --- B1 (bugfix/header, HEAD)
```

같은 저장소 안에서 서로 다른 줄기가 동시에 자라는 모습입니다. branch 전략의 핵심은 이 줄기들을 짧게 유지하고, 리뷰 가능한 단위로 다시 합치는 것입니다.

## 실전 시나리오 1: 기능 개발과 긴급 버그 수정을 동시에 처리하기

현업에서 가장 자주 만나는 상황입니다. 로그인 기능을 만들던 중 운영 버그가 들어온 경우를 가정합니다.

1) 기능 branch에서 작업 중

```text
$ git switch feature/login
$ git status -s
 M login.md
```

2) 긴급 수정이 필요하므로 현재 변경을 저장

```text
$ git add login.md
$ git commit -m "WIP: draft login flow text"
[feature/login 20ac3c1] WIP: draft login flow text
 1 file changed, 5 insertions(+)
```

3) `main`으로 이동해서 hotfix branch 생성

```text
$ git switch main
Switched to branch 'main'

$ git switch -c hotfix/header-null
Switched to a new branch 'hotfix/header-null'
```

4) 수정 후 commit

```text
$ git add app.py
$ git commit -m "fix: guard null header in auth middleware"
[hotfix/header-null 5de82a4] fix: guard null header in auth middleware
 1 file changed, 3 insertions(+), 1 deletion(-)
```

5) 작업 줄기 비교

```text
$ git branch
  feature/login
* hotfix/header-null
  main

$ git log --oneline --graph --decorate --all
* 5de82a4 (HEAD -> hotfix/header-null) fix: guard null header in auth middleware
| * 20ac3c1 (feature/login) WIP: draft login flow text
|/
* e7d2c1a (main) Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

핵심은 "한 번에 하나의 목적"입니다. 기능 branch와 hotfix branch가 분리되어 있으면 리뷰와 배포 판단이 훨씬 명확해집니다.

## 실전 시나리오 2: 같은 기능을 두 접근으로 비교 실험하기

로그인 화면 문구를 A안/B안으로 동시에 실험한다고 가정합니다.

```text
$ git switch main
$ git switch -c experiment/login-copy-a
Switched to a new branch 'experiment/login-copy-a'

$ git switch main
$ git switch -c experiment/login-copy-b
Switched to a new branch 'experiment/login-copy-b'
```

각 branch에서 독립적으로 commit한 뒤 비교합니다.

```text
$ git log --oneline experiment/login-copy-a..experiment/login-copy-b
8cb1d10 Update login CTA with urgency tone

$ git diff experiment/login-copy-a experiment/login-copy-b
diff --git a/login-copy.md b/login-copy.md
index 4f13abc..8bc299a 100644
--- a/login-copy.md
+++ b/login-copy.md
@@ -1,3 +1,3 @@
-지금 로그인하면 설정을 이어서 관리할 수 있습니다.
+지금 로그인하면 설정을 잃지 않고 바로 이어서 관리할 수 있습니다.
```

이 방식의 장점은 실험 흔적이 commit 단위로 남는다는 점입니다. 팀 토론에서 "어떤 문구가 왜 바뀌었는지"를 감이 아니라 이력으로 확인할 수 있습니다.

## 실무에서는 이렇게 본다

branch는 작업 단위마다 짧게 만들고 빨리 닫는 편이 좋습니다. branch 수명이 길수록 `main`과 멀어지고, 나중 merge 비용도 커집니다. 그래서 팀에서는 보통 `feature/<summary>`, `bugfix/<summary>` 같은 규칙을 정하고 짧은 주기로 merge합니다.

또한 branch를 옮기기 전 `git status -s`를 먼저 보는 습관이 중요합니다. 지금 working tree에 떠다니는 변경이 있는지 미리 보면 branch 전환 중 생길 혼란을 크게 줄일 수 있습니다.

추가로, 팀이 커질수록 branch를 "기술 기능"이 아니라 "커뮤니케이션 단위"로 보는 관점이 중요해집니다. branch 이름은 작업 의도를 드러내고, commit 묶음은 리뷰 단위를 드러내며, PR 제목은 배포 노트의 원재료가 됩니다. 즉 branch 관리 품질이 곧 협업 비용과 직결됩니다.

예를 들어 다음 규칙은 단순하지만 효과가 큽니다.

- branch 이름은 `type/short-summary` 형식으로 통일합니다. 예: `feature/login-api`, `bugfix/token-refresh`.
- 하루 이상 걸리는 작업은 중간 commit을 숨기지 말고 논리 단위로 남깁니다.
- 장기 branch를 만들었다면 매일 `main`과의 거리(`git log --oneline main..HEAD`)를 확인합니다.
- merge 직전에는 `git log --oneline --graph --decorate --all`로 줄기 모양을 다시 읽고, 의도와 다른 commit 유입이 없는지 확인합니다.

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

- **branch는 왜 파일 복사본이 아니라 포인터라고 할까요?**
  - branch는 "특정 commit hash를 가리키는 이름"이기 때문입니다. `feature/login`을 만들 때 디스크 전체가 복사되지 않고, 기존 commit(C3)을 가리키는 포인터 하나만 추가됩니다. 이후 commit이 쌓일 때 그 branch 포인터만 앞으로 이동합니다.
- **`git branch`와 `git switch`는 역할이 어떻게 다를까요?**
  - `git branch`는 branch를 만들거나 목록을 보는 명령이고, `git switch`는 현재 작업 branch를 바꾸는 명령입니다. 둘을 분리해 쓰면 "생성"과 "전환"이 혼동되지 않아 실수가 줄어듭니다. 만들고 바로 이동할 때는 `git switch -c`를 사용합니다.
- **`HEAD`는 branch와 어떤 관계를 가질까요?**
  - `HEAD`는 "지금 내가 붙어 있는 위치"를 나타냅니다. 보통은 현재 branch를 가리키지만, commit hash에 직접 붙으면 detached HEAD가 됩니다. 그래서 `git status`, `git branch`, `git log --decorate`로 현재 위치를 자주 확인하는 습관이 필요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- **branch 기초 - 만들고 옮기고 비교하기 (현재 글)**
- merge와 conflict 해결하기 - 두 줄기를 다시 합치기 (예정)
- GitHub repository 만들기 - remote, push, pull 한 번에 익히기 (예정)
- Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (예정)
- Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (예정)
- 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (예정)
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [Pro Git — Branches in a Nutshell](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell) — branch와 `HEAD`를 포인터로 이해하는 이 글의 핵심 멘탈 모델을 뒷받침합니다.
- [git-branch manual](https://git-scm.com/docs/git-branch) — branch 만들기, 목록 보기, 이름 변경, 삭제 문법의 기준 문서입니다.
- [git-switch manual](https://git-scm.com/docs/git-switch) — `git switch`와 `git switch -c`로 전환하는 최신 흐름을 공식적으로 확인할 수 있습니다.
- [git-checkout manual](https://git-scm.com/docs/git-checkout) — 예전 문법이 branch 전환과 파일 복원을 함께 맡았던 이유를 이해하는 데 도움이 됩니다.
- [git-log manual](https://git-scm.com/docs/git-log) — `main..feature/login`, `--graph --decorate --all`처럼 branch 차이를 읽는 명령과 연결됩니다.
- [git-diff manual](https://git-scm.com/docs/git-diff) — `git diff main feature/login`으로 branch 간 파일 차이를 비교하는 단계의 기준이 됩니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/04-branch-basics)

Tags: git-branch, git-switch, git-checkout, HEAD, parallel-development, feature-branch
