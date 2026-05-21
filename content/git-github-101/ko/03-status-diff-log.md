---
episode: 3
language: ko
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- git-status
- git-diff
- git-log
- change-history
- working-tree-vs-index
- log-formatting
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기"
seo_description: status, diff, log로 변경 위치와 내용, 이력을 읽는 방법을 설명합니다.
---

# Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기

Git을 잘 쓰는 사람은 대개 치기 전에 먼저 읽습니다. `status`, `diff`, `log`를 정확히 읽을 수 있으면 잘못된 commit을 만들기 전에 스스로 한 번 걸러낼 수 있고, 협업에서도 변경을 훨씬 차분하게 설명할 수 있습니다.

이 글은 Git/GitHub 101 시리즈의 세 번째 글입니다. 여기서는 현재 상태를 읽는 `status`, 줄 단위 차이를 읽는 `diff`, 이미 저장된 이력을 읽는 `log`를 한 흐름으로 정리합니다.

## 먼저 던지는 질문

- `git status`의 긴 출력과 짧은 출력은 각각 무엇을 보여 줄까요?
- `git diff`, `git diff --cached`, `git diff HEAD`는 어느 영역끼리 비교할까요?
- 두 commit을 직접 비교할 때는 어떤 순서로 hash를 넣어야 할까요?

## 큰 그림

![Git & GitHub 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/03/03-01-mental-model.ko.png)

*Git & GitHub 101 3장 흐름 개요*

## 왜 중요한가

이전 글에서 첫 commit 사이클을 만들었다면, 이제는 단순히 변경이 있다는 사실만으로는 부족합니다. 다음 commit에 무엇이 들어갈지, 이미 저장된 이력은 어떤 모양인지, 내가 지금 staging한 내용이 정말 의도한 것인지 읽어 낼 수 있어야 합니다.

세 명령은 역할이 분명히 다릅니다.

- `git status`는 변경이 **어느 영역에 있는지** 보여 줍니다.
- `git diff`는 그 변경의 **실제 내용**을 보여 줍니다.
- `git log`는 commit이 쌓인 **순서와 문맥**을 보여 줍니다.

이 셋을 함께 쓰면 commit 직전 자기 검토가 가능해지고, 그 습관은 곧 좋은 commit message와 작은 PR로 이어집니다.

## 핵심 그림

기억할 규칙은 세 줄이면 충분합니다.

- `git diff`는 기본적으로 **WD vs Staging**입니다.
- `git diff --cached`는 **Staging vs HEAD**입니다.
- `git diff HEAD`는 **WD vs HEAD** 전체 비교입니다.

## 핵심 개념

- **`git status` 긴 형식**: 영역과 다음 명령을 문장으로 보여 줍니다.
- **`git status -s` 짧은 형식**: 파일당 두 문자 코드로 요약합니다.
- **`git diff`**: 아직 staging되지 않은 추적 파일의 변경을 보여 줍니다.
- **`git diff --cached`**: 지금 commit하면 들어갈 내용을 보여 줍니다.
- **`git diff HEAD`**: 마지막 commit과 비교한 전체 변경을 보여 줍니다.
- **`git log`**: HEAD부터 과거로 거슬러 commit을 출력합니다.
- **`--oneline` / `--graph` / `--stat` / `-p`**: 같은 이력을 서로 다른 밀도로 읽게 해 주는 옵션입니다.

## 전후 비교

Git 없이 방금 바뀐 내용을 확인하려면 보통 에디터의 실행 취소 기록에 의존합니다.

```text
- You scroll back through Ctrl+Z one keystroke at a time
- Changes in other files are invisible
- Yesterday's edits are likely gone
```

Git을 쓰면 같은 질문을 이렇게 답할 수 있습니다.

```text
$ git status -s
 M README.md
?? draft.md

$ git diff README.md
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

같은 자리에서 파일 상태, 변경 줄, 이력의 흐름을 함께 읽을 수 있다는 점이 핵심입니다.

## 단계별 실습

### 1. `git status`를 두 형식으로 읽기

```text
$ echo "Author: me" >> README.md
$ echo "draft" > draft.md
$ git status
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        draft.md

no changes added to commit (use "git add" and/or "git commit -a")
```

```text
$ git status -s
 M README.md
?? draft.md
```

왼쪽 문자는 staging 상태, 오른쪽 문자는 working directory 상태입니다. `??`는 Git이 아직 모르는 새 파일입니다.

### 2. `git diff`로 staging 전 변경 보기

```text
$ git diff
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

위에서부터 읽으면 파일명, 이전/이후 blob hash, 비교 양쪽, hunk 범위, 추가/삭제 줄 순서로 해석할 수 있습니다.

### 3. `git diff --cached`로 staging된 변경 보기

```text
$ git add README.md
$ git diff
$ git diff --cached
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

이제 plain `git diff`는 비고, `--cached`에만 내용이 남습니다. commit 직전에 가장 유용한 점검입니다.

```text
$ git status
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        draft.md
```

### 4. `git diff HEAD`로 전체 차이 보기

```text
$ git diff HEAD
diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

`draft.md`는 여기에 보이지 않습니다. `git diff`는 추적 중인 파일의 변경만 보여 주기 때문입니다.

### 5. 두 commit 비교하기

```text
$ git diff 4f1a2c0 9b8c3e2
diff --git a/README.md b/README.md
index a1b2c3d..6e85ca6 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,3 @@
 # My First Repo
+
+Some notes.
```

순서는 항상 오래된 쪽에서 새로운 쪽으로 읽는 편이 자연스럽습니다. 하나의 commit만 보고 싶다면 `git show <hash>`가 더 짧습니다.

### 6. `git log` 모양 바꾸기

```text
$ git commit -m "Add author line to README"
[main e7d2c1a] Add author line to README
 1 file changed, 1 insertion(+)
```

```text
$ git log --oneline
e7d2c1a Add author line to README
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

```text
$ git log --oneline --graph
* e7d2c1a Add author line to README
* 9b8c3e2 Add intro paragraph to notes
* 4f1a2c0 Initial commit
```

```text
$ git log --stat
commit e7d2c1a4b9f0c5d2e1a8b7c6d5e4f3a2b1c0d9e8
Author: Me <me@example.com>
Date:   Mon May 4 10:30:00 2026 +0900

    Add author line to README

 README.md | 1 +
 1 file changed, 1 insertion(+)
```

```text
$ git log -p -1
commit e7d2c1a4b9f0c5d2e1a8b7c6d5e4f3a2b1c0d9e8
Author: Me <me@example.com>
Date:   Mon May 4 10:30:00 2026 +0900

    Add author line to README

diff --git a/README.md b/README.md
index 6e85ca6..b7f5a1e 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My First Repo

 Some notes.
+Author: me
```

`--graph`는 branch가 생기면 더 빛나고, `--stat`은 PR 설명 초안에 자주 쓰이며, `-p`는 리뷰에 가장 정직한 정보입니다.

## 자주 하는 실수

- `git diff`가 비어 있으니 변경이 없다고 착각하지만, 실제로는 staging에 이미 올라간 경우가 많습니다.
- `git diff <a> <b>`의 순서를 바꿔 `+`와 `-`를 거꾸로 읽는 일도 흔합니다.
- `git status -s`의 두 글자를 한 덩어리로 읽으면 상태를 잘못 해석합니다.
- untracked 파일이 `git diff`에 안 보인다고 사라진 것으로 오해하기도 합니다.
- `git log`가 페이지 출력으로 열렸을 때 `q`를 몰라 빠져나오지 못하는 경우도 자주 있습니다.

## 실무에서는 이렇게 본다

commit 전에 `git status -s`를 보고, 이어서 `git diff --cached`를 한 번 읽는 습관은 비용 대비 효과가 가장 큽니다. 작은 자기 검토만으로도 엉뚱한 파일을 commit에 섞는 사고를 크게 줄일 수 있습니다.

PR 설명을 쓸 때도 `git log --oneline origin/main..HEAD`와 `git log -p origin/main..HEAD`는 매우 유용합니다. 무엇을 바꿨는지와 왜 작은 commit들로 쪼갰는지를 스스로 먼저 읽어 볼 수 있기 때문입니다.

## 체크리스트

- [ ] `git status`의 긴 형식과 `-s` 짧은 형식을 모두 읽어 봤습니다.
- [ ] `git diff`, `git diff --cached`, `git diff HEAD`가 각각 무엇을 비교하는지 설명할 수 있습니다.
- [ ] `@@ -1,3 +1,4 @@` 같은 hunk 헤더의 뜻을 설명할 수 있습니다.
- [ ] `git log --oneline`, `--graph`, `--stat`, `-p`를 나란히 비교해 봤습니다.
- [ ] `git diff <a> <b>`에서 인자 순서의 의미를 알고 있습니다.
- [ ] `git log` 출력에서 `q`로 빠져나오는 것을 기억합니다.

## 연습 문제

1. `README.md`를 한 줄 수정하고 `git diff`와 `git diff --cached` 출력을 각각 비교해 보세요.
2. 변경을 staging한 뒤 plain `git diff`는 비고 `git diff HEAD`는 계속 보이는지 확인해 보세요.
3. 자신의 첫 두 commit을 `git diff <old> <new>`로 비교하고 `git show <new>`와도 비교해 보세요.
4. `git log --oneline --graph --stat`를 실행하고 각 옵션이 어떤 정보를 더하는지 한 문장으로 적어 보세요.
5. 새 파일을 만들고 `git status -s`의 `??`가 `git add` 후 어떻게 바뀌는지 확인해 보세요.

## 정리와 다음 글

`git status`는 변경의 위치를, `git diff`는 변경의 내용을, `git log`는 이미 저장된 이력의 흐름을 보여 줍니다. 세 명령을 함께 읽는 습관이 생기면 commit 직전 검토가 훨씬 정확해집니다.

다음 글에서는 같은 폴더 안에서 작업 줄기를 나누는 branch를 다룹니다. branch가 폴더 복사가 아니라 포인터라는 점을 중심으로 만들기, 전환, 비교를 살펴보겠습니다.


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

- **`git status`의 긴 출력과 짧은 출력은 각각 무엇을 보여 줄까요?**
  - 본문의 기준은 변경 사항 확인하기 - status, diff, log로 읽기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`git diff`, `git diff --cached`, `git diff HEAD`는 어느 영역끼리 비교할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **두 commit을 직접 비교할 때는 어떤 순서로 hash를 넣어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- **변경 사항 확인하기 - status, diff, log로 읽기 (현재 글)**
- branch 기초 - 만들고 옮기고 비교하기 (예정)
- merge와 conflict 해결하기 - 두 줄기를 다시 합치기 (예정)
- GitHub repository 만들기 - remote, push, pull 한 번에 익히기 (예정)
- Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (예정)
- Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (예정)
- 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (예정)
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [Pro Git — Viewing the Commit History](https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History) — `git log --oneline`, `--graph`, `--stat`, `-p`를 어떤 상황에서 읽는지 큰 그림을 제공합니다.
- [git-status manual](https://git-scm.com/docs/git-status) — 긴 형식과 `-s` 짧은 형식이 무엇을 보여 주는지 확인할 수 있습니다.
- [git-diff manual](https://git-scm.com/docs/git-diff) — `git diff`, `git diff --cached`, `git diff HEAD`가 각각 무엇을 비교하는지의 기준 문서입니다.
- [git-log manual](https://git-scm.com/docs/git-log) — log 옵션 조합과 출력 형태를 공식 문법으로 다시 확인할 수 있습니다.
- [git-show manual](https://git-scm.com/docs/git-show) — 글에서 언급한 “한 commit만 짧게 보기” 대안 명령을 보강합니다.
- [gitrevisions manual](https://git-scm.com/docs/gitrevisions) — `HEAD`, `<old> <new>`, range 표기처럼 비교 대상을 지정하는 규칙을 정리한 문서입니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/03-status-diff-log)

Tags: git-status, git-diff, git-log, change-history, working-tree-vs-index, log-formatting
