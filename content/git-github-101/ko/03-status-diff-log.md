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


![Git & GitHub 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/03/03-01-mental-model.ko.png)
*Git & GitHub 101 3장 흐름 개요*

## 먼저 던지는 질문

- `git status`의 긴 출력과 짧은 출력은 각각 무엇을 보여 줄까요?
- `git diff`, `git diff --cached`, `git diff HEAD`는 어느 영역끼리 비교할까요?
- 두 commit을 직접 비교할 때는 어떤 순서로 hash를 넣어야 할까요?

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

## 비교 범위를 정확히 지정하는 법

`status`, `diff`, `log`를 헷갈리는 가장 큰 이유는 "무엇과 무엇을 비교하는지"를 명령 이름이 아니라 감으로 추측하기 때문입니다. 아래 네 가지를 기준으로 고정하면 대부분의 혼동이 사라집니다.

| 질문 | 명령 | 비교 대상 |
| --- | --- | --- |
| 아직 add하지 않은 변경은? | `git diff` | Working Directory vs Staging(Index) |
| 지금 commit에 들어갈 변경은? | `git diff --cached` | Staging(Index) vs HEAD |
| 마지막 commit부터 지금까지 전체 변경은? | `git diff HEAD` | Working Directory + Index vs HEAD |
| 특정 branch와 내 작업 branch 차이는? | `git diff origin/main...HEAD` | merge base 이후 내 branch 변경 |

특히 `..`와 `...`를 구분해 두면 실수 비용이 크게 줄어듭니다.

- `git diff A..B`는 보통 `git diff A B`와 같은 두 끝점 비교로 읽습니다.
- `git diff A...B`는 merge base 기준으로 B 쪽 변화만 봅니다.

아래 출력은 기능 branch에서 자주 보는 패턴입니다.

```text
$ git diff --name-only origin/main...HEAD
app/auth.py
app/session.py
tests/test_auth.py
```

## `git status`를 운영 신호로 읽기

`git status`는 단순 알림이 아니라 작업 트리의 상태 머신 출력입니다. 긴 형식과 짧은 형식을 연결해서 읽으면 현재 위치를 정확히 파악할 수 있습니다.

```text
$ git status -s
MM app/auth.py
A  app/session.py
 M tests/test_auth.py
?? notes/todo.md
```

각 행은 두 칸(XY)입니다.

- `MM`: index에도 변경이 있고 working directory에도 추가 변경이 있습니다.
- `A `: 새 파일이 staging되어 commit 대기 상태입니다.
- ` M`: staging은 없고 working directory에만 수정이 있습니다.
- `??`: 아직 추적되지 않는 파일입니다.

이 출력이 바로 commit 사고를 줄입니다. 예를 들어 `MM`이 보이면 `git diff --cached app/auth.py`와 `git diff app/auth.py`를 각각 확인해야 staging 이후 추가 편집이 섞였는지 확인할 수 있습니다.

```text
$ git diff --cached -- app/auth.py
@@ -40,6 +40,8 @@ def refresh_session(...):
     token = issue_token(user_id)
+    audit_logger.info("token issued")
+    return token

$ git diff -- app/auth.py
@@ -41,7 +43,7 @@ def refresh_session(...):
-    return token
+    return token, expires_at
```

같은 파일이라도 "commit 예정 내용"과 "아직 staging 안 된 추가 수정"이 분리되어 보입니다. 이 분리를 놓치면 의도하지 않은 API 변경이 commit에 같이 들어갈 수 있습니다.

## `git diff` 출력에서 꼭 읽어야 할 줄

입문 단계에서는 `+`와 `-`만 보는 경우가 많지만, 실무에서는 헤더를 같이 읽어야 원인 파악이 빨라집니다.

```text
diff --git a/app/auth.py b/app/auth.py
index 8d2a1c1..f3a9d72 100644
--- a/app/auth.py
+++ b/app/auth.py
@@ -58,10 +58,14 @@ def validate_refresh_token(token: str) -> dict:
-    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
+    payload = jwt.decode(
+        token,
+        SECRET,
+        algorithms=["HS256"],
+        options={"require": ["exp", "sub"]},
+    )
     return payload
```

- `index 8d2a1c1..f3a9d72 100644`: blob 해시와 파일 모드입니다. 권한 비트가 바뀌었는지도 여기서 확인합니다.
- `@@ -58,10 +58,14 @@`: 왼쪽은 이전 파일 줄 범위, 오른쪽은 이후 파일 줄 범위입니다.
- 함수 시그니처 뒤 문맥(`def validate_refresh_token`)은 hunk 위치를 빠르게 찾게 해 줍니다.

코드 리뷰에서는 "무엇이 바뀌었는가"보다 "어디 맥락에서 바뀌었는가"가 더 중요합니다. 그래서 헤더를 먼저 읽고 본문을 읽는 순서가 안전합니다.

## 파일 단위 요약과 통계 읽기

줄 단위 diff만 계속 보면 피로도가 높아집니다. 먼저 요약으로 범위를 좁히고, 필요한 파일만 상세 diff로 들어가는 방식이 효율적입니다.

```text
$ git diff --stat HEAD
 app/auth.py         | 21 ++++++++++++++++-----
 app/session.py      | 34 ++++++++++++++++++++++++++++++
 tests/test_auth.py  | 19 +++++++++++++++--
 3 files changed, 67 insertions(+), 7 deletions(-)

$ git diff --name-status HEAD
M	app/auth.py
A	app/session.py
M	tests/test_auth.py
```

`--stat`은 변경량 감각을 주고, `--name-status`는 파일 성격(M/A/D/R)을 빠르게 알려 줍니다. PR 초안 작성 전에는 이 두 출력만 봐도 설명의 뼈대를 만들 수 있습니다.

## rename과 이동을 읽는 방법

파일 이동이 섞이면 "삭제 + 새 파일"처럼 보이는 경우가 있습니다. 이때 rename 감지를 켜면 이력 해석이 쉬워집니다.

```text
$ git diff --find-renames --summary HEAD~1 HEAD
 rename app/token.py => app/auth/token_service.py (92%)
 create mode 100644 app/auth/__init__.py
```

퍼센트는 유사도입니다. 92%면 대부분 같은 내용이 위치만 이동했다는 뜻입니다. 리뷰어에게도 "기능 추가"와 "구조 이동"을 분리해 설명하기 좋아집니다.

## `git log`를 질문별로 읽기

`git log`는 옵션을 모르면 길고, 질문을 먼저 정하면 짧아집니다.

질문별 추천 명령은 다음과 같습니다.

| 알고 싶은 것 | 명령 |
| --- | --- |
| 최근 commit 제목 흐름 | `git log --oneline -n 15` |
| branch 구조 포함한 흐름 | `git log --oneline --graph --decorate --all` |
| 작성자/시간 포함 상세 | `git log --pretty=fuller -n 5` |
| 파일별 변경량 중심 | `git log --stat -n 10` |
| patch까지 포함한 정밀 리뷰 | `git log -p -n 3` |

실제 출력은 아래처럼 읽습니다.

```text
$ git log --oneline --graph --decorate -n 8
* 9ac21d4 (HEAD -> feature/auth-session) fix(auth): handle expired refresh token
* 51be7ae test(auth): add refresh token edge cases
* a5d9c6f feat(auth): add session refresh service
| * 743de19 (origin/main, main) docs: update onboarding steps
|/
* 1d20fce chore: configure pre-commit hooks
* c84a9a1 feat: initial auth module
```

이 출력 하나로 현재 branch 위치, 원격 main과의 관계, commit 묶음을 동시에 확인할 수 있습니다.

## commit 검색과 추적

협업에서는 "누가 이 줄을 왜 바꿨는지"를 찾아야 할 때가 많습니다. `log`에 검색 옵션을 결합하면 해결 시간이 크게 줄어듭니다.

```text
$ git log --oneline --grep "refresh token"
9ac21d4 fix(auth): handle expired refresh token
a5d9c6f feat(auth): add session refresh service

$ git log --oneline --author "kim" -n 5
743de19 docs: update onboarding steps
3bc6221 refactor(auth): split token helpers
```

코드 단위 추적은 `-S`가 유용합니다.

```text
$ git log -S "require\": [\"exp\", \"sub\"]" -- app/auth.py
commit 9ac21d4...
Author: Kim Dev <kim@example.com>
Date:   Tue May 12 09:18:10 2026 +0900

    fix(auth): require exp/sub claims in refresh token
```

문자열이 등장하거나 사라진 commit을 찾아 주기 때문에 "이 검증 로직이 언제 들어왔는가" 같은 질문에 바로 답할 수 있습니다.

## 문제 상황별 트러블슈팅

### 1) `git diff`가 비어 있는데 분명히 바꾼 것 같을 때

가장 흔한 원인은 이미 staging된 상태입니다.

```text
$ git diff
# (no output)

$ git diff --cached --name-only
app/auth.py
```

해결은 단순합니다. commit 예정이면 그대로 진행하고, 아직 묶고 싶지 않다면 `git restore --staged app/auth.py`로 unstage한 뒤 다시 확인합니다.

### 2) 줄바꿈(CRLF/LF) 때문에 diff가 과도하게 클 때

```text
$ git diff --stat
 app/auth.py | 220 ++++++++++++++++++++++++++-------------------------
 1 file changed, 110 insertions(+), 110 deletions(-)
```

실제 로직 변경이 없는데 대규모 수정처럼 보이면 줄바꿈 규칙부터 확인해야 합니다. 팀 `.gitattributes`와 에디터 EOL 설정을 맞춘 뒤 최소 단위 commit으로 분리합니다.

### 3) merge 후 이력이 복잡해서 읽기 어려울 때

```text
$ git log --oneline --graph --decorate --all --simplify-by-decoration
* 1f2ab09 (HEAD -> main, origin/main) merge: release 1.4.0
* 2cc8d1f (tag: v1.4.0) chore: cut release
* 9ac21d4 (feature/auth-session) fix(auth): handle expired refresh token
```

태그와 브랜치 기준으로 단순화하면 경계를 분리해서 읽을 수 있습니다.

## commit 직전 60초 점검 루틴

아래 순서를 습관으로 만들면 "엉뚱한 파일 포함", "staging 이후 추가 수정 누락", "메시지와 내용 불일치"를 대부분 방지할 수 있습니다.

```bash
git status -s
git diff --cached --stat
git diff --cached
git diff
git log --oneline -n 3
```

읽는 기준은 간단합니다.

- `status -s`: 포함/제외 파일이 의도와 맞는지 확인합니다.
- `diff --cached --stat`: 변경량이 예상 규모인지 확인합니다.
- `diff --cached`: commit 메시지와 코드 변경이 일치하는지 확인합니다.
- `diff`: staging 이후 추가 수정이 남아 있는지 확인합니다.
- `log -n 3`: 직전 commit들과 중복 메시지나 충돌하는 의도가 없는지 확인합니다.

## 작은 실전 예제: 잘못된 staging 복구

아래는 테스트 파일이 실수로 섞인 상황입니다.

```text
$ git status -s
M  app/auth.py
M  tests/test_auth.py

$ git diff --cached --name-only
app/auth.py
tests/test_auth.py
```

이번 commit은 기능 코드만 포함해야 한다면 다음처럼 복구합니다.

```bash
git restore --staged tests/test_auth.py
git status -s
git diff --cached --name-only
```

복구 후 상태:

```text
$ git status -s
M  app/auth.py
 M tests/test_auth.py

$ git diff --cached --name-only
app/auth.py
```

이제 `tests/test_auth.py`는 working directory 변경으로 남고, commit 대상에서는 제외됩니다. "한 commit, 한 의도" 원칙을 지키기 쉬워집니다.

## 팀 규칙으로 정리할 최소 합의

다음 네 가지는 초급 팀에서도 바로 적용할 수 있습니다.

1. commit 전 `git diff --cached`를 필수로 본다.
2. PR 설명에 `git diff --stat origin/main...HEAD` 요약을 포함한다.
3. merge 직후 `git log --oneline --graph -n 20`으로 히스토리 형태를 확인한다.
4. 이슈 추적 시 `git log -S` 또는 `--grep`으로 근거 commit을 남긴다.

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

다음 글에서는 같은 폴더 안에서 작업 줄기를 나누는 branch를 다룹니다. branch가 폴더 복사가 아니라 포인터라는 점을 중심으로 만들기, 전환, 비교를 봅니다.


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
  - 본문에서 본 것처럼 `git status` 긴 출력은 작업 위치와 다음 행동 힌트를 문장으로 보여 주고, `git status -s`는 파일별 XY 코드(예: `M `, `??`, `A `, ` M`)로 상태를 한눈에 빠르게 보여 줍니다. 스크립트로 상태를 파싱해야 할 때는 `-s` 형식이 안정적입니다.
- **`git diff`, `git diff --cached`, `git diff HEAD`는 어느 영역끼리 비교할까요?**
  - 본문 예시처럼 `git diff`는 Working Directory vs Index(아직 stage 안 한 변경), `git diff --cached`는 Index vs HEAD(이번 commit에 들어갈 변경), `git diff HEAD`는 Working Directory + Index vs HEAD(아직 commit 안 된 모든 변경)를 비교합니다. 세 명령의 차이가 곧 Git의 세 영역 모델 그 자체입니다.
- **두 commit을 직접 비교할 때는 어떤 순서로 hash를 넣어야 할까요?**
  - 본문에서 강조했듯이 보통 `git diff <old> <new>` 순서로 읽습니다. 그래야 `+` 라인이 "새 commit에서 추가된 줄", `-` 라인이 "이전 commit에서 사라진 줄"로 자연스럽게 해석되고, 순서를 바꾸면 `+`/`-` 의미가 정반대로 뒤집힙니다.

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
