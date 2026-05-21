---
episode: 2
language: ko
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- git-init
- git-status
- git-add
- git-commit
- staging-area
- first-repository
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit"
seo_description: 첫 commit이 working directory에서 repository로 가는 흐름을 설명합니다.
---

# Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit

Git은 첫 commit을 직접 만들어 보는 순간부터 추상적인 개념에서 손에 잡히는 도구로 바뀝니다. 빈 폴더에서 시작해 변경을 staging에 올리고 snapshot으로 저장하는 과정을 한 번 끝까지 따라가면 이후 명령도 훨씬 덜 낯설어집니다.

이 글은 Git/GitHub 101 시리즈의 두 번째 글입니다. 여기서는 `git init`부터 첫 `git commit`까지의 흐름을 손으로 따라가며 Git의 세 영역이 실제로 어떻게 움직이는지 확인합니다.

## 먼저 던지는 질문

- `git init`은 현재 디렉터리에 정확히 무엇을 만들까요?
- `git status`는 파일 상태를 어떤 말로 보여 줄까요?
- `git add`는 단순히 "파일을 추가한다"는 뜻일까요, 아니면 더 정확한 의미가 있을까요?

## 큰 그림

![Git & GitHub 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/02/02-01-mental-model.ko.png)

*Git & GitHub 101 2장 흐름 개요*

## 왜 중요한가

Git 입문에서 가장 어려운 부분은 명령 이름이 아닙니다. 지금 내 변경이 어느 영역에 있는지, 즉 working directory인지 staging area인지 repository인지 머릿속에 그리는 일입니다.

첫 commit을 손으로 만들어 보면 이 그림이 빠르게 선명해집니다. 단순히 파일을 만들었을 때와 `git add`까지 했을 때 `git status`가 어떻게 달라지는지, commit 직후 상태가 왜 깨끗해지는지, `.git/` 디렉터리가 저장소의 출발점이라는 점까지 한 번에 체감할 수 있습니다.

이 한 사이클을 직접 경험하고 나면 이후의 `git diff`, `git log`, `git restore`, `git switch`도 어느 영역을 건드리는 명령인지 예측하기 쉬워집니다.

실무에서 사고가 나는 지점도 거의 여기입니다. 파일은 고쳤는데 staging에 안 올려서 누락 commit이 생기거나, 반대로 staging에 올라간 줄 모르고 비밀 키 파일을 함께 저장하는 경우가 대표적입니다. 첫 commit 단계에서 상태 전이를 정확히 읽는 습관을 들이면 이후 협업 단계의 실수 비용이 크게 줄어듭니다.

아래처럼 같은 작업을 해도 어느 순간의 `status`인지에 따라 해석이 달라집니다.

```text
$ git status
On branch main
Changes not staged for commit:
  modified:   app.py

$ git add app.py
$ git status
On branch main
Changes to be committed:
  modified:   app.py
```

첫 상태는 "수정은 했지만 다음 snapshot에는 아직 안 들어간 상태"이고, 두 번째 상태는 "다음 snapshot 후보로 확정된 상태"입니다. 겉보기에는 한 줄 차이지만, 리뷰나 배포에서 결과 차이는 매우 큽니다.

## 핵심 그림

세 동사가 함께 움직입니다.

- **edit**: 에디터에서 파일을 만들거나 수정합니다.
- **`add`**: 다음 commit에 포함할 변경으로 올립니다.
- **`commit`**: staging에 모인 내용을 하나의 snapshot으로 저장합니다.

`git status`는 이 흐름 전체에서 현재 위치를 알려 주는 안내판입니다. 헷갈릴 때 가장 먼저 보는 명령이 되는 이유가 여기에 있습니다.

## 핵심 개념

- **Working Directory**: 디스크 위에 보이는 현재 파일입니다.
- **Staging Area (Index)**: 다음 commit 후보 목록입니다.
- **`git init`**: 현재 폴더에 `.git/`을 만들어 Git 저장소로 바꿉니다.
- **Untracked / Modified / Staged**: `git status`가 보여 주는 대표 상태입니다.
- **Commit message**: 변경 의도를 한 줄로 요약한 기록입니다.
- **`HEAD`**: 현재 branch의 가장 최근 commit을 가리키는 이름입니다.

세 영역을 한 문장으로 묶으면 "작업 중인 파일(working)을 선택해(staging) 기록으로 남긴다(repository)"입니다. `git add`를 모르면 두 번째 단계가 비어 있는 채로 commit을 시도하게 되고, `git commit`을 모르면 staging에 올린 변경이 영구 기록으로 남지 않습니다.

### 왜 staging이 따로 있을까요?

많은 입문자가 staging을 중간 단계라서 번거롭다고 느낍니다. 하지만 staging이 없으면 "파일 단위로 어떤 변경을 이번 commit에 넣을지" 제어하기 어렵습니다. 특히 한 파일에서 버그 수정과 리팩터링을 함께 했다면, staging이 있어야 두 작업을 분리 기록할 수 있습니다.

```text
# 같은 파일의 일부만 staging하는 예시
$ git add -p app.py
Stage this hunk [y,n,q,a,d,s,e,?]? y
Stage this hunk [y,n,q,a,d,s,e,?]? n
```

이 기능 덕분에 "기능 추가"와 "오타 수정"을 다른 commit으로 남길 수 있고, 나중에 되돌릴 때도 원하는 단위만 되돌릴 수 있습니다. staging은 불편을 추가하는 장치가 아니라, 기록 품질을 높이는 제어 장치입니다.

### commit message는 왜 신경 써야 할까요?

commit hash는 기계가 읽기 쉽고, message는 사람이 읽기 쉽습니다. 몇 주 뒤 `git log --oneline`을 볼 때 파일 이름만으로는 의도를 복원하기 어렵기 때문에, message 한 줄이 팀의 작업 맥락을 복구하는 핵심 단서가 됩니다.

| 나쁜 예 | 좋은 예 |
| --- | --- |
| `fix` | `fix(auth): reject expired refresh token` |
| `update` | `docs: add onboarding steps for local setup` |
| `final` | `refactor(api): split validation from handler` |

좋은 message의 기준은 화려한 문장이 아니라 "왜 이 변경을 했는지 1초 안에 파악되는가"입니다.

## 전후 비교

Git 없이 메모 파일을 관리하면 보통 이런 식이 됩니다.

```text
$ ls
notes_v1.txt
notes_v2.txt
notes_v2_FINAL.txt
```

- 최신 파일이 무엇인지 파일명으로 추측해야 합니다.
- 두 버전의 차이는 별도 비교 도구를 열어야 알 수 있습니다.
- 왜 바꿨는지는 파일명 어디에도 남지 않습니다.

Git을 쓰면 기록이 이런 모양으로 남습니다.

```text
$ git log --oneline
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

최신은 `HEAD`가 가리키고, 차이는 `git diff`로 확인하며, 변경 의도는 commit message에 남습니다.

## 단계별 실습

### 1. 빈 디렉터리에서 시작

```text
$ mkdir my-first-repo
$ cd my-first-repo
$ ls -A
```

아무것도 보이지 않으면 정말 빈 디렉터리입니다.

### 2. `git init`으로 저장소 만들기

```text
$ git init
Initialized empty Git repository in /Users/me/my-first-repo/.git/
```

`.git/`이 생기면 이 폴더는 Git 저장소가 됩니다.

초기 출력에 보이는 경로는 로컬 환경마다 다릅니다. Linux에서는 `/home/<user>/...`, macOS에서는 `/Users/<user>/...` 형태가 일반적입니다. 핵심은 경로 문자열이 아니라 `.git/` 디렉터리 생성 여부입니다.

```text
$ ls -A
.git
```

`.git/` 안에는 commit 객체, branch 포인터, 설정 파일이 저장됩니다. 초기에 바로 확인 가능한 구조는 보통 아래와 비슷합니다.

```text
$ ls -A .git
HEAD
config
description
hooks/
info/
objects/
refs/
```

여기서 `HEAD`는 현재 branch를 가리키고, `objects/`는 commit/blob/tree 객체를 저장하며, `refs/`는 branch 같은 참조 이름을 보관합니다. 즉 `.git/`은 단순 캐시 폴더가 아니라 저장소의 데이터베이스입니다.

아래는 `git init` 전후 비교입니다.

| 시점 | `ls -A` 결과 | 의미 |
| --- | --- | --- |
| init 전 | (출력 없음) | 일반 디렉터리 |
| init 후 | `.git` | Git 저장소로 전환 |

### 3. 첫 파일을 만들고 status 확인

```text
$ echo "# My First Repo" > README.md
$ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

nothing added to commit but untracked files present (use "git add" to track)
```

`README.md`는 아직 Git이 모르는 파일이므로 `Untracked`입니다.

여기서 "모른다"는 뜻은 디스크에 없다는 의미가 아닙니다. 파일은 존재하지만 Git 인덱스(index)에 항목이 없다는 의미입니다. 그래서 `git add README.md`를 실행하는 순간 Git이 "이 파일을 추적 목록에 넣겠다"고 상태를 바꿉니다.

여러 파일을 동시에 만들면 `Untracked files` 아래에 모두 표시됩니다.

```text
$ touch app.py .env notes.txt
$ git status
Untracked files:
  .env
  README.md
  app.py
  notes.txt
```

이 단계에서 `.env`가 보이면 바로 `.gitignore`를 먼저 만들고 제외하는 습관이 필요합니다. 초반에 놓치면 나중에 기록 정리가 훨씬 번거로워집니다.

### 4. `git add`로 staging에 올리기

```text
$ git add README.md
$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
```

상태가 `Untracked`에서 `Changes to be committed`로 이동했습니다. 이것이 staging입니다.

같은 시점에 파일 내용을 다시 수정하면 어떤 일이 생길까요? 많은 입문자가 이 부분에서 혼란을 겪습니다.

```text
$ git add README.md
$ echo "One more line" >> README.md
$ git status
Changes to be committed:
  new file:   README.md

Changes not staged for commit:
  modified:   README.md
```

한 파일이 두 영역에 동시에 나타납니다. staging에는 "add 당시의 버전"이 있고, working directory에는 "그 이후 추가 수정"이 있기 때문입니다. 이 상태에서 commit하면 staging 버전만 기록되고, 마지막 한 줄은 다음 commit 대상으로 남습니다.

이 동작을 정확히 이해하면 "왜 방금 수정한 코드가 commit에 안 들어갔지?" 같은 질문을 스스로 해결할 수 있습니다.

### 5. `git commit -m`으로 snapshot 저장

```text
$ git commit -m "Initial commit"
[main (root-commit) 4f1a2c0] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

첫 commit에는 `root-commit`이라는 표시가 붙습니다. 부모 commit이 없기 때문입니다.

첫 commit 이후에는 branch 포인터와 `HEAD`가 이 commit hash를 가리키게 됩니다. 눈으로 확인하면 아래처럼 읽힙니다.

```text
$ git log --oneline --decorate
4f1a2c0 (HEAD -> main) Initial commit
```

`HEAD -> main`은 "현재 체크아웃한 branch(main)의 최신 commit이 4f1a2c0"이라는 뜻입니다.

```text
$ git status
On branch main
nothing to commit, working tree clean
```

`working tree clean`은 "변경이 없다"가 아니라 "Git이 추적 중인 변경 중 commit 후보가 없는 상태"입니다. untracked 파일이 있으면 clean이 아니라는 점도 함께 기억해 두면 좋습니다.

### 6. 한 번 더 같은 사이클 돌리기

```text
$ echo "" >> README.md
$ echo "Some notes." >> README.md
$ git status
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md

no changes added to commit (use "git add" and/or "git commit -a")
```

이번에는 새 파일이 아니라 추적 중인 파일을 수정했으므로 `modified`로 보입니다.

```text
$ git add README.md
$ git commit -m "Add intro paragraph to notes"
[main 9b8c3e2] Add intro paragraph to notes
 1 file changed, 2 insertions(+)
```

```text
$ git log --oneline
9b8c3e2 Add intro paragraph to notes
4f1a2c0 Initial commit
```

이제 두 번째 commit까지 생겼으므로 전후 차이를 읽는 연습을 붙일 수 있습니다.

```text
$ git diff 4f1a2c0..9b8c3e2
diff --git a/README.md b/README.md
index 19b3f2a..2a7f11c 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,3 @@
 # My First Repo
+
+Some notes.
```

commit을 "저장"으로만 보면 여기서 멈추기 쉽습니다. 하지만 commit의 실제 가치는 비교 가능성입니다. 어떤 줄이 언제 들어왔는지 추적 가능한 기록이 되어야 협업에서도 힘을 발휘합니다.

## 자주 하는 실수

- 홈 디렉터리에서 `git init`을 실행해 전체 홈 폴더를 저장소로 만들어 버리는 경우가 있습니다.
- `git add` 없이 `git commit`부터 시도하면 staging이 비어 있어 저장할 것이 없다는 메시지를 보게 됩니다.
- `git add .`로 의도하지 않은 파일까지 올리는 일도 흔합니다.
- 빈 commit message를 넣거나 `.git/` 내부 파일을 손으로 건드리는 것도 피해야 합니다.
- 이미 추적 중인 파일을 수정하고 `add`를 빼먹은 채 commit하려다 일부만 저장하는 실수도 자주 나옵니다.

실수별로 즉시 복구하는 명령까지 같이 기억해 두면 현장에서 당황할 일이 줄어듭니다.

| 상황 | 증상 | 빠른 복구 |
| --- | --- | --- |
| 잘못된 위치에서 `git init` 실행 | 홈 디렉터리 전체가 저장소처럼 보임 | `.git/` 위치 확인 후 잘못 만든 저장소라면 해당 디렉터리의 `.git` 제거 |
| `git add .`로 민감 파일 포함 | `git status`에 `.env`, 키 파일이 staged | `git restore --staged <file>`로 즉시 제외 후 `.gitignore` 추가 |
| message 없이 commit 시도 | 에디터 열림 또는 에러 | `git commit -m "의도가 드러나는 한 줄"`로 다시 실행 |
| staging 버전과 작업 버전 혼동 | commit 후 최신 수정이 누락됨 | `git status`에서 staged/unstaged를 분리 확인하고 필요 시 재-add |

특히 초보 단계에서 가장 흔한 문제는 "명령이 틀린 것"보다 "현재 상태를 잘못 읽은 것"입니다. 그래서 복구의 출발점도 항상 `git status`입니다.

### 트러블슈팅: commit이 안 될 때

아래는 첫 commit 단계에서 자주 만나는 에러와 원인입니다.

```text
$ git commit -m "Initial commit"
Author identity unknown
*** Please tell me who you are.
```

Git 사용자 정보가 없을 때 나오는 메시지입니다. 로컬 전역 또는 저장소 단위로 이름/이메일을 설정한 뒤 다시 commit하면 됩니다.

```text
$ git config --global user.name "Your Name"
$ git config --global user.email "you@example.com"
```

또 다른 사례는 staging이 비어 있을 때입니다.

```text
$ git commit -m "Initial commit"
On branch main
Initial commit
nothing to commit (create/copy files and use "git add" to track)
```

이때는 파일 생성 여부보다 `git add` 수행 여부를 먼저 확인하면 해결이 빠릅니다.

## 실무에서는 이렇게 본다

새 프로젝트를 시작할 때도, 작은 기능을 쪼개 기록할 때도 결국 흐름은 같습니다. 편집하고, 상태를 확인하고, staging으로 올리고, 의도가 분명한 commit으로 저장합니다. 이 기본기가 있어야 나중에 리뷰와 되돌리기, 충돌 해결도 쉬워집니다.

특히 `git status`를 자주 보는 습관은 실무에서 매우 중요합니다. 변경을 한 뒤 무엇이 staging에 올라가 있고 무엇이 아직 작업 중인지 읽는 능력이 곧 사고를 줄여 줍니다.

여기에 한 가지를 더 붙이면, commit 단위를 작게 가져가는 습관입니다. 예를 들어 "버그 수정 + 테스트 추가 + 문서 보완"을 한 번에 묶지 않고 2~3개 commit으로 나누면 코드 리뷰가 빨라지고 롤백도 쉬워집니다. 첫 commit을 만들 때부터 "작업의 경계 = commit 경계"라는 감각을 같이 훈련하면 이후 브랜치 협업이 훨씬 매끄럽습니다.

```text
# 권장되는 작은 commit 흐름 예시
$ git add app/auth.py
$ git commit -m "fix(auth): handle missing refresh token"

$ git add tests/test_auth.py
$ git commit -m "test(auth): add missing-refresh-token case"
```

또한 commit 전에 아래 두 명령을 기본 점검으로 두면 품질이 안정됩니다.

```text
$ git diff --staged
$ git status
```

첫 번째 명령은 "이번 commit에 실제로 들어갈 줄"을 보여 주고, 두 번째 명령은 누락 파일이 남아 있는지 확인합니다. 이 두 단계를 빼먹지 않으면 "의도와 다른 commit"의 비율이 눈에 띄게 줄어듭니다.

## 체크리스트

- [ ] `git init`이 만든 `.git/` 디렉터리를 확인했습니다.
- [ ] `Untracked`, `modified`, `Changes to be committed` 상태를 각각 봤습니다.
- [ ] `git add` 전후로 `git status`가 어떻게 바뀌는지 설명할 수 있습니다.
- [ ] `git commit -m "..."`으로 commit을 만들고 `git log --oneline`으로 확인했습니다.
- [ ] commit 후 `git status`가 `working tree clean`으로 돌아오는 것을 확인했습니다.
- [ ] `root-commit`이 무엇을 뜻하는지 설명할 수 있습니다.

## 연습 문제

1. 빈 디렉터리에서 `git init`을 실행하고 `.git/` 안에 무엇이 생겼는지 확인해 보세요.
2. `README.md`를 만들고 `git status`에서 `Untracked` 상태를 본 뒤 `git add` 후 상태를 비교해 보세요.
3. 첫 commit 뒤 `README.md`에 한 줄을 더 추가하고 다시 commit한 다음 `git log --oneline`이 두 줄로 늘었는지 확인해 보세요.
4. `git commit -m ""`을 시도해 Git이 어떤 메시지를 출력하는지 읽어 보세요.
5. 새 파일 두 개를 만들고 하나만 `git add`한 뒤 commit해 보세요. 다른 파일이 어떤 상태로 남는지 `git status`로 확인해 보세요.

연습을 더 촘촘하게 하려면 아래 시나리오를 추가해 보세요.

6. `README.md`를 수정한 뒤 `git add README.md`를 실행하고, 다시 한 줄을 더 수정한 뒤 `git status`에서 staged/unstaged가 동시에 나타나는지 확인해 보세요.
7. `git add -p README.md`로 일부 hunk만 선택해 commit해 보고 `git show --stat`으로 실제 반영 범위를 읽어 보세요.
8. 의도적으로 `.env` 파일을 만든 뒤 `git status`에서 노출되는 것을 확인하고, `.gitignore`에 추가한 뒤 다시 상태가 사라지는지 비교해 보세요.

## 정리와 다음 글

`git init`은 현재 폴더를 저장소로 바꾸고, `git status`는 각 변경이 어느 영역에 있는지 알려 주며, `git add`와 `git commit`은 그 변경을 snapshot으로 저장합니다. 첫 commit을 직접 한 번 만들어 보면 이후 명령이 왜 그런 모양인지 설명이 붙습니다.

다음 글에서는 `git status`를 더 자세히 읽고 `git diff`, `git log`로 변경 내용을 해석하는 법을 다룹니다.


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

첫 commit 학습과 연결해서 보면, 이 시나리오도 결국 같은 원리입니다. 어떤 branch에서 작업하든 `edit -> add -> commit`의 구조는 동일하고, `status`가 현재 좌표를 알려 줍니다. 차이는 단지 로컬 단독 작업인지, 원격 협업이 섞였는지뿐입니다.

아래는 실무에서 자주 쓰는 "commit 직전 30초 점검" 템플릿입니다.

```bash
git status
git diff --staged
git log --oneline -5
```

이 세 줄만으로 "현재 상태", "이번 commit 내용", "최근 기록과의 연결"을 빠르게 확인할 수 있습니다. 작은 루틴이지만 PR 품질에 직접 영향을 줍니다.

## 브랜치 전략을 선택하는 기준

실무에서는 전략 자체보다 "팀이 어떤 리듬으로 릴리스를 내는가"가 더 중요합니다. 아래 표는 초급 팀이 자주 비교하는 세 가지 전략입니다.

| 전략 | 특징 | 적합한 상황 | 주의할 점 |
| --- | --- | --- | --- |
| Trunk-based | 짧은 branch 수명, 빠른 머지 | 배포 빈도가 높고 테스트 자동화가 있는 팀 | 작은 PR 규율이 없으면 main이 불안정해집니다 |
| GitHub Flow | main + feature branch + PR | SaaS, 웹 서비스처럼 연속 배포 중심 | 환경별 배포 정책을 별도로 정의해야 합니다 |
| Git Flow | develop/release/hotfix 등 다중 branch | 릴리스 윈도우가 고정된 제품형 조직 | 브랜치가 많아 운영 복잡도가 커집니다 |

입문 단계에서는 GitHub Flow로 시작하는 편이 안전합니다. 규칙이 단순하고 Pull Request 중심의 협업 도구와 잘 맞기 때문입니다. 이후 릴리스 요구가 복잡해지면 release branch를 추가하는 방식으로 확장하면 됩니다.

첫 commit 글에서 이 내용을 다루는 이유는 단순합니다. commit은 개인 기록이지만, branch 전략은 그 기록이 팀에서 어떻게 소비되는지를 결정합니다. 같은 commit 품질이라도 전략이 다르면 리뷰 속도와 배포 리듬이 달라집니다.

그래서 초급 팀에서는 아래 두 규칙만 먼저 고정해도 효과가 큽니다.

- main에는 직접 push하지 않고 PR로만 반영합니다.
- 한 PR에는 하나의 의도만 담고, commit message도 그 의도를 유지합니다.

이 두 가지가 지켜지면 "첫 commit 품질"이 곧 "협업 품질"로 자연스럽게 이어집니다.

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

- **`git init`은 현재 디렉터리에 정확히 무엇을 만들까요?**
  - 본문의 기준은 첫 commit 만들기 - init, status, add, commit를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
  - `git init`은 현재 폴더에 `.git/`을 만들고, 그 안에 `HEAD`, `objects/`, `refs/`, `config` 같은 저장소 메타데이터를 생성합니다. 이 순간부터 폴더는 일반 디렉터리가 아니라 Git 데이터베이스를 가진 저장소가 됩니다.
- **`git status`는 파일 상태를 어떤 말로 보여 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
  - 대표 문구는 `Untracked files`, `Changes not staged for commit`, `Changes to be committed`입니다. 같은 파일도 `add` 전후, 추가 수정 여부에 따라 두 영역에 동시에 나타날 수 있으며, 이 차이가 commit 결과를 결정합니다.
- **`git add`는 단순히 "파일을 추가한다"는 뜻일까요, 아니면 더 정확한 의미가 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.
  - 더 정확한 의미는 "다음 snapshot 후보를 인덱스에 기록한다"입니다. 파일 생성 명령이 아니라 commit 경계를 설계하는 명령이며, `git add -p`를 쓰면 한 파일에서도 필요한 변경만 선택해 기록 품질을 높일 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- **첫 commit 만들기 - init, status, add, commit (현재 글)**
- 변경 사항 확인하기 - status, diff, log로 읽기 (예정)
- branch 기초 - 만들고 옮기고 비교하기 (예정)
- merge와 conflict 해결하기 - 두 줄기를 다시 합치기 (예정)
- GitHub repository 만들기 - remote, push, pull 한 번에 익히기 (예정)
- Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (예정)
- Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (예정)
- 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (예정)
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [Pro Git — Recording Changes to the Repository](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) — working directory에서 staging, commit으로 넘어가는 첫 저장 흐름을 가장 직접적으로 설명합니다.
- [git-init manual](https://git-scm.com/docs/git-init) — `git init`이 저장소를 어떻게 만들고 어떤 옵션을 갖는지 확인할 수 있습니다.
- [git-status manual](https://git-scm.com/docs/git-status) — `Untracked`, `modified`, `Changes to be committed` 같은 상태 문구의 기준 문서입니다.
- [git-add manual](https://git-scm.com/docs/git-add) — `git add`가 단순 추가가 아니라 staging을 채우는 동작임을 정확히 짚어 줍니다.
- [git-commit manual](https://git-scm.com/docs/git-commit) — `git commit -m`과 첫 snapshot 저장 규칙을 공식 문법으로 확인할 수 있습니다.
- [git-log manual](https://git-scm.com/docs/git-log) — 실습 마지막의 `git log --oneline`으로 첫 두 commit을 확인하는 단계와 연결됩니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/02-first-commit)

Tags: git-init, git-status, git-add, git-commit, staging-area, first-repository
