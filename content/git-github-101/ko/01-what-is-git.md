---
title: Git이란 무엇인가? 버전 관리의 시작
series: git-github-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- git-basics
- version-control
- distributed-vcs
- snapshot-model
- git-install
- git-config
last_reviewed: '2026-05-12'
seo_description: Git의 스냅샷 모델과 세 가지 작업 영역을 이해하고, 초기 설정부터 도움말 활용법까지 실습하며 분산 버전 관리의 기본 멘탈 모델을 정립합니다.
---

# Git이란 무엇인가? 버전 관리의 시작

버전 관리를 처음 배울 때 많은 사람이 명령부터 외웁니다. 그런데 Git은 명령 목록으로 접근하면 금방 막히고, 파일의 변경을 시간 순서대로 보관하고 되돌리는 도구라는 그림을 먼저 잡으면 훨씬 빨리 익숙해집니다.

이 글은 Git/GitHub 101 시리즈의 첫 번째 글입니다. 여기서는 Git 자체를 어떤 멘탈 모델로 이해해야 이후의 `add`, `commit`, `push`가 자연스럽게 읽히는지 정리합니다.

## 이 글에서 다룰 문제

> Git의 핵심은 파일의 상태를 시간 순서대로 스냅샷으로 남기는 일이며, 그 스냅샷은 working directory, staging area, repository라는 세 영역을 거쳐 만들어집니다.

- 버전 관리 도구는 정확히 어떤 문제를 해결할까요?
- Git이 분산 버전 관리 도구라고 부르는 이유는 무엇일까요?
- Git의 스냅샷 모델은 "변경된 줄만 저장하는 도구"와 무엇이 다를까요?
- Git을 설치하고 처음 설정할 때 무엇을 끝내 두면 좋을까요?
- 다음 글의 첫 commit 실습 전에 어떤 준비가 되어 있어야 할까요?

## 왜 중요한가

혼자 코드를 짜더라도 시간이 지나면 비슷한 질문을 반복하게 됩니다. 어제는 되던 코드가 왜 오늘은 안 되는지, 한 달 전 이 함수가 어떤 모양이었는지, 여러 파일을 동시에 바꾸다가 어디서부터 꼬였는지 알고 싶어집니다.

Git은 이런 질문에 답하는 기본 도구입니다. 어느 시점의 코드든 다시 꺼내 볼 수 있고, 누가 언제 무엇을 바꿨는지도 추적할 수 있습니다. 협업이 시작되면 가치는 더 커집니다. 같은 파일을 여러 명이 수정해도 충돌한 부분만 사람이 판단하면 되기 때문입니다.

실무에서는 Git을 모르면 협업 흐름 전체가 흐릿해집니다. Pull Request도, CI도, 배포 자동화도 결국 commit과 branch를 전제로 돌아갑니다. 그래서 Git은 선택 기능이라기보다 팀이 공유하는 작업 언어에 가깝습니다.

## Git을 이해하는 가장 좋은 방법

Git을 한 문장으로 줄이면 **파일의 스냅샷을 시간 순서대로 저장하는 도구**입니다. 각 commit은 그 순간 추적 중이던 파일들의 상태를 찍어 둔 사진이라고 보면 됩니다.

![Mental Model](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/01/01-01-mental-model.ko.png)

*Mental Model*

Git은 로컬에서 세 영역을 구분합니다.

- **Working Directory**: 지금 편집 중인 파일이 있는 작업 공간입니다.
- **Staging Area**: 다음 commit에 넣을 변경을 모아 두는 버퍼입니다.
- **Repository**: commit이 시간 순서대로 쌓이는 로컬 저장소입니다. remote는 이 세 영역 바깥에 있는 별도 저장소입니다.

이 그림을 먼저 잡아 두면 `add`, `commit`, `push`가 왜 서로 다른 명령인지 설명이 됩니다. 편집한 내용을 곧바로 저장소에 넣지 않고, 먼저 staging으로 모은 뒤, 그다음 commit으로 굳히기 때문입니다.

## 핵심 개념

- **버전 관리 시스템(VCS)**: 파일의 변경을 기록하고 이전 상태를 복구하는 도구입니다.
- **분산 버전 관리**: clone만 해도 전체 이력을 로컬에 갖는 구조입니다. Git이 대표 사례입니다.
- **스냅샷 모델**: Git은 commit 시점의 추적 파일 상태를 저장합니다. 내부적으로는 동일한 파일을 재사용해 공간을 아낍니다.
- **Commit**: 변경의 단위입니다. 메시지, 작성자, 시간, 부모 commit 정보를 함께 기록합니다.
- **Branch**: 특정 commit을 가리키는 이동 가능한 포인터입니다.
- **Remote**: GitHub 같은 외부 저장소입니다. 로컬 저장소와 별도의 commit 그래프를 가집니다.

## 전후 비교

작은 팀이 Git 없이 코드를 공유할 때는 이런 식이 흔합니다.

```text
project_v1.zip
project_v2_FINAL.zip
project_v2_FINAL_real.zip
project_v2_FINAL_real_alice_edits.zip
```

이 방식에는 세 가지 문제가 있습니다.

- 최신 파일이 무엇인지 파일명으로 추측해야 합니다.
- 어떤 줄이 바뀌었는지 알아보려면 압축을 풀고 직접 비교해야 합니다.
- 두 사람의 작업을 합칠 표준 절차가 없습니다.

Git으로 바꾸면 기록 방식이 달라집니다.

```text
$ git log --oneline
b3a1c0f Add login form (alice)
8e2f5d1 Refactor session helper (bob)
1a9b2c4 Initial commit (alice)
```

이제는 변경의 작성자와 순서가 한 줄씩 남고, `git diff`로 차이를 확인할 수 있으며, `git merge`가 자동으로 합칠 수 있는 부분은 처리해 줍니다.

## 단계별 실습

### 1. Git 설치 확인

```text
$ git --version
git version 2.43.0
```

설치돼 있지 않다면 운영체제에 맞게 설치합니다.

- macOS: `brew install git` 또는 Xcode Command Line Tools에 포함된 git 사용
- Ubuntu/Debian: `sudo apt update && sudo apt install git`
- Windows: [Git for Windows](https://git-scm.com/download/win) 설치

설치 후에는 새 셸을 열고 다시 `git --version`을 실행해 출력이 보이는지 확인합니다.

### 2. 사용자 정보 설정

```text
$ git config --global user.name "Ada Lovelace"
$ git config --global user.email "ada@example.com"
```

이 설정은 홈 디렉터리의 `.gitconfig`에 저장됩니다. 특정 저장소에서만 다른 이메일을 쓰고 싶다면 그 저장소 안에서 `--global` 없이 같은 명령을 다시 실행하면 됩니다.

### 3. 기본 branch 이름 설정

```text
$ git config --global init.defaultBranch main
```

새 저장소의 기본 branch를 `main`으로 통일하면 이후 문서와 협업 흐름이 단순해집니다.

### 4. 설정 확인

```text
$ git config --global --list
user.name=Ada Lovelace
user.email=ada@example.com
init.defaultBranch=main
```

### 5. 도움말 시스템 익히기

```text
$ git help                # list of common Git commands
$ git help commit         # full manual (browser or man page)
$ git commit --help       # same manual as `git help commit`
$ git commit -h           # one-screen option summary (short usage)
```

`git help <cmd>`와 `git <cmd> --help`는 같은 자세한 매뉴얼을 엽니다. `-h`는 짧은 옵션 요약만 보고 싶을 때 유용합니다.

## 자주 하는 실수

- 전역 이메일을 회사 메일로 두고 개인 저장소에도 그대로 쓰는 경우가 많습니다.
- 설치만 하고 `user.name`, `user.email`을 설정하지 않아 첫 commit에서 막히기도 합니다.
- GUI만 쓰고 명령행을 피하면 문제 상황에서 원인을 읽기가 어려워집니다.
- 너무 오래된 git 바이너리를 쓰면 `git switch`, `git restore` 같은 명령을 바로 쓰지 못할 수 있습니다.
- `.git/` 없이 프로젝트 폴더만 압축해 백업하면 이력이 사라집니다.
- Git과 GitHub를 같은 도구라고 생각하면 이후 remote 개념에서 자주 헷갈립니다.

## 실무에서는 이렇게 본다

Git은 개인 프로젝트의 안전망이면서 팀 협업의 공통어입니다. 어제 작업을 한 번에 되돌릴 수 있다는 점도 크지만, 더 중요한 것은 같은 변경을 팀이 같은 방식으로 읽고 토론할 수 있다는 점입니다.

또한 CI/CD도 대부분 commit과 PR 이벤트를 기준으로 동작합니다. Terraform, Kubernetes manifest 같은 인프라 코드도 텍스트 파일이므로 결국 Git으로 관리됩니다. 즉 Git은 애플리케이션 코드만의 도구가 아니라, 변경을 기록하는 거의 모든 엔지니어링 흐름의 바닥층입니다.

## 체크리스트

- [ ] `git --version`이 정상적으로 출력됩니다.
- [ ] `git config --global user.name`과 `user.email`을 설정했습니다.
- [ ] `git config --global init.defaultBranch`를 설정했습니다.
- [ ] Working Directory, Staging Area, Repository를 각각 한 문장으로 설명할 수 있습니다.
- [ ] Git과 GitHub의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] `git help <command>`, `git <command> --help`, `git <command> -h`의 차이를 알고 있습니다.

## 연습 문제

1. Git을 설치하고 `git --version` 출력 결과를 적어 보세요.
2. `git config --global user.name`, `user.email`을 설정한 뒤 `git config --global --list`로 확인해 보세요.
3. `git config --global init.defaultBranch main`을 설정한 뒤 새 디렉터리에서 `git init`을 실행해 기본 branch가 `main`인지 확인해 보세요.
4. `git help commit`, `git commit --help`, `git commit -h`를 각각 실행해 차이를 비교해 보세요.
5. Working Directory, Staging Area, Repository를 자신의 말로 한 문장씩 정의해 보세요.

## 정리와 다음 글

Git은 파일의 스냅샷을 시간 순서대로 저장하는 분산 버전 관리 도구입니다. 변경은 Working Directory에서 시작해 Staging Area를 거쳐 Repository에 commit으로 남습니다. 처음 사용할 때는 `user.name`, `user.email`, `init.defaultBranch`를 먼저 설정해 두면 이후 실습이 부드럽습니다.

다음 글에서는 빈 디렉터리에서 출발해 첫 commit을 직접 만듭니다. `git init`, `git status`, `git add`, `git commit`이 어떤 순서로 연결되는지 손으로 따라가 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **Git이란 무엇인가? 버전 관리의 시작 (현재 글)**
- 첫 commit 만들기: init, add, commit (예정)
- 변경 사항 확인하기: status, diff, log (예정)
- branch 이해하기: 분기와 전환 (예정)
- merge와 conflict 해결하기 (예정)
- GitHub repository 만들기와 remote, push, pull (예정)
- Pull Request로 협업하기 (예정)
- Issue와 Project로 일감 관리하기 (예정)
- 좋은 commit message 쓰기 (예정)
- 실전 Git workflow 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Pro Git — About Version Control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) — 버전 관리 도구가 해결하는 문제와 중앙집중형·분산형 차이를 글의 출발점으로 잡아 줍니다.
- [Pro Git — What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F) — 스냅샷 모델과 분산 저장소 구조를 이 글의 멘탈 모델과 직접 연결해 읽을 수 있습니다.
- [Pro Git — First-Time Git Setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) — `user.name`, `user.email` 같은 첫 설정 흐름을 공식 예시로 확인할 수 있습니다.
- [git-config manual](https://git-scm.com/docs/git-config) — `git config --global`과 `init.defaultBranch` 문법을 정확히 확인할 때 기준이 되는 문서입니다.
- [Git downloads](https://git-scm.com/downloads) — 운영체제별 공식 설치 경로를 확인할 수 있습니다.
- [GitHub Docs — Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git) — GitHub와 함께 쓸 때 필요한 초기 설정을 한 번에 정리한 문서입니다.
Tags: git-basics, version-control, distributed-vcs, snapshot-model, git-install, git-config
