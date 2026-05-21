---
episode: 6
language: ko
last_reviewed: '2026-05-12'
series: git-github-101
status: publish-ready
tags:
- github-remote
- git-push
- git-pull
- git-clone
- git-fetch
- origin
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Git & GitHub 101 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기"
seo_description: GitHub remote를 연결하고 push, fetch, pull, clone을 익히는 글입니다.
---

# Git & GitHub 101 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기

지금까지의 Git은 한 대의 컴퓨터 안에서만 움직였습니다. 협업이 본격적으로 시작되는 지점은 로컬 저장소에 원격 보관 장소가 생길 때입니다. 그때부터 같은 history를 다른 사람과 다른 기기에서도 공유할 수 있습니다.

이 글은 Git/GitHub 101 시리즈의 여섯 번째 글입니다. 여기서는 로컬 저장소를 GitHub에 연결하고 첫 push, fetch, pull, clone 흐름을 순서대로 살펴봅니다.

## 먼저 던지는 질문

- remote는 정확히 무엇이고 왜 첫 이름이 보통 `origin`일까요?
- 빈 GitHub 저장소를 로컬 저장소에 연결하는 순서는 어떻게 될까요?
- `git push -u origin main`은 한 번에 무엇을 두 가지나 설정할까요?

## 큰 그림

![Git & GitHub 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/06/06-01-mental-model.ko.png)

*Git & GitHub 101 6장 흐름 개요*

## 왜 중요한가

노트북 안에만 있는 저장소는 협업 관점에서 개인 노트와 크게 다르지 않습니다. 다른 사람과 코드를 공유하거나, 기기를 잃어버려도 history를 잃지 않으려면 저장소가 다른 위치에도 있어야 합니다. GitHub가 그 대표적인 위치입니다.

remote는 외부 저장소의 별칭입니다. URL을 매번 길게 입력하지 않고 짧은 이름으로 부를 수 있게 해 줍니다. 첫 remote 이름으로 `origin`이 널리 쓰이는 이유도, 프로젝트를 처음 가져온 원천이라는 관례가 Git에 깊게 자리 잡았기 때문입니다.

또한 `push`, `fetch`, `pull`을 구분해야 나중에 "다른 사람이 올린 변경을 어떻게 안전하게 가져오지?"라는 질문도 흔들리지 않습니다.

## 핵심 그림

세 가지를 함께 기억하면 충분합니다.

- GitHub 저장소도 결국 또 하나의 Git 저장소입니다.
- 각 협업자는 자기 컴퓨터에 완전한 로컬 사본을 가집니다.
- 동기화는 자동이 아니라 명령으로 일어납니다. push하지 않으면 GitHub는 모르고, pull하지 않으면 로컬은 모릅니다.

## 핵심 개념

| 용어 | 의미 |
| --- | --- |
| remote | 다른 위치의 저장소를 가리키는 별칭 |
| origin | 첫 remote에 흔히 쓰는 기본 이름 |
| upstream | 로컬 branch가 추적하는 remote branch |
| `git remote add` | 새 remote 등록 |
| `git push` | 로컬 commit 업로드 |
| `git fetch` | remote commit 다운로드만 수행 |
| `git pull` | `fetch` 후 자동 merge 또는 rebase |
| `git clone` | remote 저장소 전체를 새 디렉터리에 복제 |
| HTTPS URL | 토큰 인증 방식의 URL |
| SSH URL | SSH key 인증 방식의 URL |

## 전후 비교

remote가 없으면 push할 곳 자체가 없습니다.

```text
$ git log --oneline
1c2d3e4 Demote header to h3
b5d4c6e Merge branch 'feature/header'
...
$ git push
fatal: No configured push destination.
Either specify the URL from the command-line or configure a remote repository using
    git remote add <name> <url>
and then push using the remote name
    git push <name>
```

remote를 연결하면 같은 history를 GitHub에도 올릴 수 있습니다.

```text
$ git remote -v
origin  https://github.com/<your-id>/vacation-notes.git (fetch)
origin  https://github.com/<your-id>/vacation-notes.git (push)
$ git push -u origin main
Enumerating objects: 12, done.
...
To https://github.com/<your-id>/vacation-notes.git
 * [new branch]      main -> main
```

## 단계별 실습

### 1. 빈 GitHub 저장소 만들기

브라우저에서 `https://github.com/new`를 열고 저장소를 만듭니다.

- Repository name: `vacation-notes`
- Description: 선택 사항
- Public / Private: 학습용이면 Public으로 충분
- `Add a README file`, `Add .gitignore`, `Choose a license`는 모두 체크 해제

처음부터 GitHub 쪽에서 commit이 생기지 않게 비워 두는 것이 중요합니다.

### 2. remote 등록하기

```text
$ git remote add origin https://github.com/<your-id>/vacation-notes.git
$ git remote -v
origin  https://github.com/<your-id>/vacation-notes.git (fetch)
origin  https://github.com/<your-id>/vacation-notes.git (push)
```

`git remote add`는 출력이 없으니 `git remote -v`로 확인합니다.

### 3. 첫 push와 upstream 설정

```text
$ git push -u origin main
Enumerating objects: 24, done.
Counting objects: 100% (24/24), done.
Delta compression using up to 8 threads
Compressing objects: 100% (16/16), done.
Writing objects: 100% (24/24), 2.31 KiB | 1.16 MiB/s, done.
Total 24 (delta 5), reused 0 (delta 0)
remote: Resolving deltas: 100% (5/5), completed with 0 local objects.
To https://github.com/<your-id>/vacation-notes.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

`-u`는 두 가지를 동시에 합니다.

1. 로컬 `main`이 `origin/main`을 추적하게 만듭니다.
2. 이후부터 `git push`만 쳐도 같은 대상으로 보내게 합니다.

### 4. 두 번째 commit과 짧아진 push

```text
$ printf "## Quickstart\n\n1. Clone the repo.\n2. Open notes.md.\n" > quickstart.md
$ git add quickstart.md
$ git commit -m "Add quickstart section"
[main 2b3c4d5] Add quickstart section
 1 file changed, 4 insertions(+)
$ git push
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 8 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 351 bytes | 351.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0)
To https://github.com/<your-id>/vacation-notes.git
   1c2d3e4..2b3c4d5  main -> main
```

### 5. 다른 위치에 clone하기

```text
$ cd /tmp
$ git clone https://github.com/<your-id>/vacation-notes.git
Cloning into 'vacation-notes'...
remote: Enumerating objects: 27, done.
remote: Counting objects: 100% (27/27), done.
remote: Compressing objects: 100% (18/18), done.
remote: Total 27 (delta 5), reused 27 (delta 5), pack-reused 0
Receiving objects: 100% (27/27), 2.66 KiB | 2.66 MiB/s, done.
Resolving deltas: 100% (5/5), done.
$ cd vacation-notes
$ git log --oneline -3
2b3c4d5 Add quickstart section
1c2d3e4 Demote header to h3
b5d4c6e Merge branch 'feature/header'
$ git remote -v
origin  https://github.com/<your-id>/vacation-notes.git (fetch)
origin  https://github.com/<your-id>/vacation-notes.git (push)
```

`git clone`은 새 디렉터리 생성, `.git` 복제, `origin` 자동 등록, 기본 branch checkout까지 한 번에 처리합니다.

### 6. 다른 쪽에서 push하고 내 쪽에서 fetch와 pull하기

```text
$ printf "## Deployment\n\nDeploy by pushing to main.\n" > deployment.md
$ git add deployment.md
$ git commit -m "Add deployment notes"
[main 7e8f9a0] Add deployment notes
 1 file changed, 3 insertions(+)
$ git push
...
To https://github.com/<your-id>/vacation-notes.git
   2b3c4d5..7e8f9a0  main -> main
```

원래 작업 디렉터리에서 먼저 fetch합니다.

```text
$ git fetch
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 3 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), 358 bytes | 358.00 KiB/s, done.
From https://github.com/<your-id>/vacation-notes
   2b3c4d5..7e8f9a0  main       -> origin/main
$ git status
On branch main
Your branch is behind 'origin/main' by 1 commit, and can be fast-forwarded.
  (use "git pull" to update your local branch)

nothing to commit, working tree clean
```

이제 pull로 로컬 branch를 따라잡습니다.

```text
$ git pull
Updating 2b3c4d5..7e8f9a0
Fast-forward
 deployment.md | 3 +++
 1 file changed, 3 insertions(+)
$ git log --oneline -2
7e8f9a0 Add deployment notes
2b3c4d5 Add quickstart section
```

## 자주 하는 실수

- GitHub 저장소 생성 때 README나 `.gitignore`를 같이 넣어 첫 push를 복잡하게 만드는 경우가 많습니다.
- HTTPS remote에 비밀번호로 인증하려다 실패하기도 합니다. 지금은 PAT나 SSH key가 필요합니다.
- 아침 첫 명령으로 무조건 `git pull`을 치면 로컬 미정리 변경과 충돌할 수 있습니다.
- `git fetch`만 하고 로컬 branch가 따라왔다고 오해하는 경우도 흔합니다.
- remote URL을 바꾼 뒤 `git remote -v` 확인을 안 해서 엉뚱한 곳에 push하는 사고도 생깁니다.

## 실무에서는 이렇게 본다

HTTPS와 SSH 중 무엇을 쓸지는 네트워크 환경과 인증 습관이 결정합니다. SSH 포트를 막는 환경이면 HTTPS가 편하고, 그렇지 않다면 SSH key를 한 번 등록해 두는 편이 더 덜 번거롭습니다.

또한 실무 저장소의 `main`은 직접 push가 막힌 경우가 많습니다. 그때부터는 이번 글의 push와 pull이 자기 작업 branch를 GitHub와 동기화하는 도구로 자리를 옮기고, `main` 반영은 Pull Request를 통해 이뤄집니다.

## 체크리스트

- [ ] remote를 한 문장으로 설명할 수 있습니다.
- [ ] 왜 첫 remote 이름이 `origin`인지 설명할 수 있습니다.
- [ ] 빈 GitHub 저장소를 만들고 로컬 저장소와 연결할 수 있습니다.
- [ ] `git push -u origin main`이 설정하는 두 가지를 알고 있습니다.
- [ ] `git fetch`와 `git pull`의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] `git clone`이 자동으로 등록하는 것이 무엇인지 알고 있습니다.
- [ ] `git remote -v`로 등록된 remote를 확인할 수 있습니다.
- [ ] HTTPS와 SSH URL 형식을 구분할 수 있습니다.

## 연습 문제

1. 새 빈 GitHub 저장소를 만든 뒤 `git init` → 첫 commit → `git remote add origin ...` → `git push -u origin main` 순서를 직접 따라 해 보세요.
2. 저장소를 다른 디렉터리에 clone해 두 작업 사본 사이에서 commit과 push/pull을 번갈아 해 보세요.
3. `git fetch` 후 `git status`와 `git log --oneline --decorate --all`이 어떻게 달라지는지 확인해 보세요.

## 정리와 다음 글

remote는 다른 위치의 저장소를 가리키는 별칭이고, 첫 이름은 보통 `origin`입니다. `git push`는 로컬 commit을 올리고, `git fetch`는 가져오기만 하며, `git pull`은 가져온 뒤 합칩니다. `git push -u origin main`은 upstream까지 설정해 이후 명령을 짧게 만들어 줍니다. `git clone`은 새 로컬 사본을 만들고 `origin`도 자동으로 등록합니다.

다음 글에서는 GitHub 협업의 핵심 단위인 Pull Request를 다룹니다. branch에서 작업한 변경이 리뷰를 거쳐 `main`으로 들어가는 과정을 따라가 보겠습니다.


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

- **remote는 정확히 무엇이고 왜 첫 이름이 보통 `origin`일까요?**
  - 본문의 기준은 GitHub repository 만들기 - remote, push, pull 한 번에 익히기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **빈 GitHub 저장소를 로컬 저장소에 연결하는 순서는 어떻게 될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`git push -u origin main`은 한 번에 무엇을 두 가지나 설정할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- [Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기](./05-merge-and-conflict.md)
- **GitHub repository 만들기 - remote, push, pull 한 번에 익히기 (현재 글)**
- Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (예정)
- Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (예정)
- 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (예정)
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [Pro Git — Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes) — remote, origin, fetch, push, pull을 하나의 멘탈 모델로 묶어 이해하는 데 가장 적합합니다.
- [git-push manual](https://git-scm.com/docs/git-push) — `git push -u origin main`이 upstream을 어떻게 설정하는지 공식 문법으로 확인할 수 있습니다.
- [git-fetch manual](https://git-scm.com/docs/git-fetch) — remote commit을 내려받기만 하고 로컬 branch는 움직이지 않는 이유를 설명합니다.
- [git-pull manual](https://git-scm.com/docs/git-pull) — `pull = fetch + merge/rebase`라는 글의 핵심 구분을 뒷받침합니다.
- [git-clone manual](https://git-scm.com/docs/git-clone) — clone이 새 디렉터리, `.git`, 기본 branch checkout, `origin` 등록까지 함께 처리함을 확인할 수 있습니다.
- [GitHub Docs — About remote repositories](https://docs.github.com/en/get-started/git-basics/about-remote-repositories) — HTTPS와 SSH URL 형식, `origin` 별칭, remote URL 선택 기준을 GitHub 기준으로 정리합니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/06-github-repository)

Tags: github-remote, git-push, git-pull, git-clone, git-fetch, origin
