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


![Git & GitHub 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/06/06-01-mental-model.ko.png)
*Git & GitHub 101 6장 흐름 개요*

## 먼저 던지는 질문

- remote는 정확히 무엇이고 왜 첫 이름이 보통 `origin`일까요?
- 빈 GitHub 저장소를 로컬 저장소에 연결하는 순서는 어떻게 될까요?
- `git push -u origin main`은 한 번에 무엇을 두 가지나 설정할까요?

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

여기서 `upstream`은 초급 단계에서 자주 혼동되는 단어입니다. 문맥에 따라 두 가지 뜻으로 쓰이기 때문입니다.

1. **Git 설정 용어로서의 upstream**: 현재 로컬 branch가 기본으로 비교/동기화할 remote branch를 뜻합니다. 예를 들어 로컬 `main`의 upstream이 `origin/main`이면 `git push`, `git pull`을 짧게 쓸 수 있습니다.
2. **협업 관례 용어로서의 upstream**: 포크 기반 협업에서 "원본 저장소"를 뜻합니다. 내 포크가 `origin`이고, 원본 프로젝트가 `upstream`인 구성입니다.

이 글에서는 1번 의미를 기본으로 사용하지만, 실무에서 2번을 자주 만나므로 함께 기억해 두는 편이 좋습니다.

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

여기서 `-v`는 verbose를 뜻합니다. 단순히 이름만 보여주는 `git remote`와 달리 fetch URL, push URL을 함께 보여줍니다. 처음에는 둘이 같은 주소로 보이지만, 실무에서는 읽기 전용 mirror를 fetch에 두고 push는 내부 저장소로 보내는 식으로 분리하기도 합니다.

```text
$ git remote
origin
$ git remote -v
origin  https://github.com/<your-id>/vacation-notes.git (fetch)
origin  https://github.com/<your-id>/vacation-notes.git (push)
```

또한 remote 이름은 반드시 `origin`일 필요가 없습니다. 다만 협업 문서와 튜토리얼 대부분이 `origin`을 기본 전제로 설명하므로, 특별한 이유가 없다면 관례를 따르는 편이 커뮤니케이션 비용이 낮습니다.

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

`fetch`와 `pull`의 차이를 단순 문장 하나로만 외우면 실제 상황에서 흔들리기 쉽습니다. 아래처럼 "어떤 ref가 움직이는가"로 보면 훨씬 안정적입니다.

| 명령 | 내려받기 | `origin/main` 갱신 | 로컬 `main` 갱신 | 충돌 가능 시점 |
| --- | --- | --- | --- | --- |
| `git fetch` | 수행 | 수행 | 수행 안 함 | 없음 (작업 트리 불변) |
| `git pull` | 수행 | 수행 | 수행 (merge/rebase) | 있음 |
| `git push` | 로컬에서 remote로 업로드 | remote 쪽 ref 갱신 | 로컬 불변 | 서버 거절 가능 |

이 표를 운영 관점으로 해석하면 다음과 같습니다.

- 지금 당장 파일 충돌을 마주하고 싶지 않다면 먼저 `git fetch`로 정보만 가져옵니다.
- 현재 브랜치를 바로 최신으로 맞춰야 하고 충돌 처리도 지금 하겠다면 `git pull`을 씁니다.
- 내가 가진 commit을 공유 저장소 기준선으로 올릴 때 `git push`를 씁니다.

특히 팀에서 아침 첫 명령을 `git pull`로 고정하면, 전날 남겨 둔 변경과 바로 충돌할 수 있습니다. `git fetch` → `git status` → 필요 시 `git pull --ff-only` 순서를 습관화하면 예측 가능성이 높아집니다.

## origin과 upstream을 함께 쓰는 포크 협업

이제 많이 쓰는 실무 패턴을 하나 더 보겠습니다. 회사나 오픈소스에서 자주 쓰는 구조는 아래와 같습니다.

- `upstream`: 팀의 공식 저장소(원본)
- `origin`: 내가 포크한 저장소(내 쓰기 권한이 있는 저장소)

```text
$ git remote -v
origin    git@github.com:<your-id>/project-fork.git (fetch)
origin    git@github.com:<your-id>/project-fork.git (push)
upstream  git@github.com:org/project.git (fetch)
upstream  git@github.com:org/project.git (push)
```

여기서 중요한 운영 규칙은 단순합니다. **최신 기준선은 `upstream/main`에서 받고, 내 작업 공유는 `origin/<feature-branch>`로 보낸다**는 규칙입니다.

```bash
# 1) 원본 최신 이력 가져오기
git fetch upstream

# 2) 내 로컬 main을 원본 기준선에 맞추기
git switch main
git merge --ff-only upstream/main

# 3) 기능 브랜치 생성 후 작업
git switch -c feature/readme-cleanup

# 4) 내 포크(origin)로 push
git push -u origin feature/readme-cleanup
```

왜 이런 분리를 쓰는지 이유를 이해하면 실수 확률이 크게 줄어듭니다.

1. 원본 저장소에 직접 push 권한이 없는 상황에서도 정상적으로 작업할 수 있습니다.
2. 내 포크에서 실험 브랜치를 자유롭게 관리할 수 있습니다.
3. `upstream`과 `origin`의 역할이 분리되어 어떤 방향으로 동기화하는지 명확합니다.

반대로 remote 이름을 뒤섞으면 `git push upstream main` 같은 위험한 명령을 실수로 실행할 수 있습니다. 그래서 팀 온보딩 문서에 remote 역할을 먼저 명시하는 것이 좋습니다.

## SSH vs HTTPS 인증 선택 기준

GitHub remote URL은 같은 저장소라도 두 형식이 있습니다.

```text
# HTTPS
https://github.com/<your-id>/vacation-notes.git

# SSH
git@github.com:<your-id>/vacation-notes.git
```

둘 다 같은 Git 객체를 다루지만 인증 경로가 다릅니다.

| 항목 | HTTPS | SSH |
| --- | --- | --- |
| 인증 재료 | PAT(Personal Access Token) | SSH key (public/private) |
| 초기 설정 난이도 | 낮음 | 중간 |
| 반복 사용 편의성 | 토큰 캐시 설정에 따라 다름 | 키 등록 후 편함 |
| 네트워크 제약 | 443 포트 환경에 유리 | 22 포트 차단 시 제약 가능 |
| 조직 보안 정책 대응 | SSO/PAT 정책과 연동 쉬움 | 키 로테이션/등록 정책 필요 |

초급 단계에서는 HTTPS로 시작해도 충분합니다. 다만 장기간 한 저장소를 자주 다루면 SSH가 더 편해지는 경우가 많습니다. 반대로 회사 네트워크가 SSH를 제한하면 HTTPS가 현실적인 기본값이 됩니다.

인증 실패 메시지도 자주 보게 됩니다.

```text
$ git push
remote: Support for password authentication was removed on August 13, 2021.
fatal: Authentication failed for 'https://github.com/<your-id>/vacation-notes.git/'
```

이 경우 비밀번호가 아니라 PAT 또는 SSH key를 써야 합니다. 즉, 문제의 본질은 Git 명령이 아니라 인증 방식입니다.

이미 등록된 remote를 HTTPS에서 SSH로 바꾸는 절차는 간단합니다.

```bash
git remote set-url origin git@github.com:<your-id>/vacation-notes.git
git remote -v
```

반대로 SSH에서 HTTPS로 바꿀 때도 같은 명령을 사용합니다. 변경 직후에는 반드시 `git remote -v`로 fetch/push URL이 기대와 맞는지 확인해야 합니다.

## `.gitignore`를 먼저 잡아 두는 이유

GitHub 저장소를 만들고 첫 push를 하기 전, `.gitignore` 기준을 먼저 정하면 history 품질이 크게 달라집니다. 초반에 실수로 올라간 빌드 산출물, 캐시, 비밀 파일은 나중에 지우더라도 commit history에 흔적이 남기 때문입니다.

아래는 Python 기준으로 실무에서 자주 쓰는 패턴입니다.

```gitignore
# Python cache
__pycache__/
*.py[cod]

# Virtual environments
.venv/
venv/

# Test / coverage artifacts
.pytest_cache/
.coverage
htmlcov/

# Build artifacts
dist/
build/
*.egg-info/

# IDE/editor
.vscode/
.idea/

# Secrets
.env
.env.*
```

패턴을 읽는 기본 규칙도 함께 익혀 두면 좋습니다.

- `dir/`는 디렉터리 전체를 무시합니다.
- `*.log`는 확장자 패턴을 무시합니다.
- `!keep.log`처럼 `!`를 붙이면 무시 규칙에서 예외를 만듭니다.
- 루트 기준으로만 지정하고 싶으면 `/`를 앞에 붙입니다. 예: `/dist/`

이미 추적 중인 파일에는 `.gitignore`가 자동 적용되지 않는다는 점도 중요합니다. 예를 들어 `.env`를 이미 commit한 뒤 ignore를 추가하면 파일은 계속 추적됩니다. 이때는 index에서 추적을 제거해야 합니다.

```bash
git rm --cached .env
git commit -m "Stop tracking .env"
```

핵심은 간단합니다. `.gitignore`는 "앞으로 추적하지 않을 것"을 정의하는 규칙이지, 이미 올라간 민감 파일을 자동으로 없애 주는 기능이 아닙니다.

## README를 첫날부터 관리하는 규칙

GitHub 저장소는 코드 보관소이면서 동시에 팀 문서의 첫 진입점입니다. 그래서 README를 "나중에 채우는 파일"로 미루기보다 첫 push 시점부터 최소 구조를 갖추는 편이 좋습니다.

초급 팀에서도 바로 적용하기 좋은 README 최소 템플릿은 아래와 같습니다.

```markdown
# project-name

한 줄 설명: 이 저장소가 해결하는 문제를 짧게 설명합니다.

## Quickstart
1. 의존성 설치
2. 실행 방법
3. 테스트 실행

## Requirements
- Python 3.12+
- uv or pip

## Project Structure
- `app/`: 애플리케이션 코드
- `tests/`: 테스트 코드

## Git Workflow
- `main`: 배포 가능한 기준선
- `feature/*`: 작업 브랜치

## License
MIT
```

README를 이렇게 시작하면 얻는 장점이 분명합니다.

1. 새 팀원이 저장소 목적과 실행 방법을 1분 안에 파악할 수 있습니다.
2. Pull Request 리뷰 시 "실행 방법이 문서와 다른데요" 같은 피드백을 빠르게 받을 수 있습니다.
3. 릴리스가 쌓일수록 운영 지식이 이슈 댓글이 아니라 저장소 루트에 남습니다.

또한 README와 `.gitignore`를 GitHub에서 자동 생성할지, 로컬에서 만들지 기준을 정해 두면 초기 충돌을 줄일 수 있습니다.

- 로컬에 이미 commit이 있는 상태라면: GitHub 저장소는 비워 두고 로컬에서 push하는 방식이 안전합니다.
- 아직 로컬 작업이 없다면: GitHub에서 README/.gitignore를 생성해 시작해도 무방합니다.

이번 글의 실습은 첫 번째 경우를 기준으로 했습니다. 그래서 저장소를 만들 때 README와 `.gitignore` 체크를 해제했습니다.

## push 전 점검 루틴

실무에서 품질을 올리는 가장 쉬운 습관은 "push 직전 30초 점검"입니다. 다음 순서를 고정해 두면 사고가 눈에 띄게 줄어듭니다.

```bash
git status
git branch -vv
git remote -v
git log --oneline --decorate -5
```

각 명령이 확인하는 질문은 명확합니다.

- `git status`: 지금 commit되지 않은 변경이 남아 있는가?
- `git branch -vv`: 현재 브랜치 upstream이 어디인가? ahead/behind는 몇 개인가?
- `git remote -v`: push 대상 URL이 맞는가?
- `git log --oneline --decorate -5`: 방금 만든 commit이 의도한 순서와 메시지인가?

이 점검은 복잡한 자동화보다 먼저 적용해야 할 기본 안전장치입니다.

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
  - remote는 다른 위치의 Git 저장소 URL에 붙인 별칭입니다. 긴 URL 대신 `origin` 같은 짧은 이름으로 fetch/push 대상을 지정합니다. `origin`은 "처음 가져온 원천"이라는 관례에서 온 기본 이름이라 협업 문서와 예제가 거의 이 이름을 전제로 합니다.
- **빈 GitHub 저장소를 로컬 저장소에 연결하는 순서는 어떻게 될까요?**
  - GitHub에서 빈 저장소를 만든 뒤, 로컬에서 `git remote add origin <URL>`로 연결하고 `git push -u origin main`으로 첫 업로드와 upstream 설정을 동시에 수행합니다. 이후에는 `git push`, `git pull` 같은 짧은 명령으로 같은 흐름을 반복할 수 있습니다.
- **`git push -u origin main`은 한 번에 무엇을 두 가지나 설정할까요?**
  - 첫째, 로컬 `main`의 commit을 `origin/main`으로 업로드합니다. 둘째, 로컬 `main`의 upstream을 `origin/main`으로 등록해 이후 push/pull 기본 대상을 고정합니다.

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
