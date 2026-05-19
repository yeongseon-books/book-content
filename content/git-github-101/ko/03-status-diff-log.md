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
title: 변경 사항 확인하기 - status, diff, log로 읽기
seo_description: status, diff, log로 변경 위치와 내용, 이력을 읽는 방법을 설명합니다.
---

# 변경 사항 확인하기 - status, diff, log로 읽기

Git을 잘 쓰는 사람은 대개 치기 전에 먼저 읽습니다. `status`, `diff`, `log`를 정확히 읽을 수 있으면 잘못된 commit을 만들기 전에 스스로 한 번 걸러낼 수 있고, 협업에서도 변경을 훨씬 차분하게 설명할 수 있습니다.

이 글은 Git/GitHub 101 시리즈의 세 번째 글입니다. 여기서는 현재 상태를 읽는 `status`, 줄 단위 차이를 읽는 `diff`, 이미 저장된 이력을 읽는 `log`를 한 흐름으로 정리합니다.

## 이 글에서 다룰 문제

> `status`, `diff`, `log`는 각각 지금 변경이 어디에 있는지, 무엇이 어떻게 바뀌었는지, 여기까지 어떤 순서로 왔는지를 보여 주는 읽기 전용 창입니다.

- `git status`의 긴 출력과 짧은 출력은 각각 무엇을 보여 줄까요?
- `git diff`, `git diff --cached`, `git diff HEAD`는 어느 영역끼리 비교할까요?
- 두 commit을 직접 비교할 때는 어떤 순서로 hash를 넣어야 할까요?
- `git log --oneline`, `--graph`, `--stat`, `-p`는 각각 언제 유용할까요?
- commit 전에 어떤 읽기 습관을 들이면 사고를 줄일 수 있을까요?

## 왜 중요한가

이전 글에서 첫 commit 사이클을 만들었다면, 이제는 단순히 변경이 있다는 사실만으로는 부족합니다. 다음 commit에 무엇이 들어갈지, 이미 저장된 이력은 어떤 모양인지, 내가 지금 staging한 내용이 정말 의도한 것인지 읽어 낼 수 있어야 합니다.

세 명령은 역할이 분명히 다릅니다.

- `git status`는 변경이 **어느 영역에 있는지** 보여 줍니다.
- `git diff`는 그 변경의 **실제 내용**을 보여 줍니다.
- `git log`는 commit이 쌓인 **순서와 문맥**을 보여 줍니다.

이 셋을 함께 쓰면 commit 직전 자기 검토가 가능해지고, 그 습관은 곧 좋은 commit message와 작은 PR로 이어집니다.

## 핵심 그림

![Mental Model](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/03/03-01-mental-model.ko.png)

*Mental Model*

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

<!-- toc:begin -->
## 시리즈 목차

- [Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- **변경 사항 확인하기 - status, diff, log로 읽기 (현재 글)**
- branch 이해하기: 분기와 전환 (예정)
- merge와 conflict 해결하기 (예정)
- GitHub repository 만들기와 remote, push, pull (예정)
- Pull Request로 협업하기 (예정)
- Issue와 Project로 일감 관리하기 (예정)
- 좋은 commit message 쓰기 (예정)
- 실전 Git workflow 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Pro Git — Viewing the Commit History](https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History) — `git log --oneline`, `--graph`, `--stat`, `-p`를 어떤 상황에서 읽는지 큰 그림을 제공합니다.
- [git-status manual](https://git-scm.com/docs/git-status) — 긴 형식과 `-s` 짧은 형식이 무엇을 보여 주는지 확인할 수 있습니다.
- [git-diff manual](https://git-scm.com/docs/git-diff) — `git diff`, `git diff --cached`, `git diff HEAD`가 각각 무엇을 비교하는지의 기준 문서입니다.
- [git-log manual](https://git-scm.com/docs/git-log) — log 옵션 조합과 출력 형태를 공식 문법으로 다시 확인할 수 있습니다.
- [git-show manual](https://git-scm.com/docs/git-show) — 글에서 언급한 “한 commit만 짧게 보기” 대안 명령을 보강합니다.
- [gitrevisions manual](https://git-scm.com/docs/gitrevisions) — `HEAD`, `<old> <new>`, range 표기처럼 비교 대상을 지정하는 규칙을 정리한 문서입니다.
Tags: git-status, git-diff, git-log, change-history, working-tree-vs-index, log-formatting
