---
title: "바이브코딩을 위한 Git & GitHub 기초 (1/10): Git이란 무엇인가? 버전 관리의 시작"
series: git-github-101
episode: 1
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI가 만든 코드를 안전하게 관리하려면 Git의 스냅샷 모델과 세 가지 작업 영역부터 이해해야 합니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (1/10): Git이란 무엇인가? 버전 관리의 시작

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 1번째 글입니다.

AI 도구로 코드를 생성하다 보면 이런 순간이 반드시 옵니다. "어제 AI가 만들어 준 코드가 분명 잘 동작했는데, 오늘 다시 프롬프트를 넣었더니 달라졌어. 이전 버전으로 어떻게 돌아가지?" 바이브코딩 환경에서는 사람이 코드를 한 줄씩 타이핑하지 않기 때문에, 변경 이력을 자동으로 남겨 두는 장치가 없으면 '언제 무엇이 왜 바뀌었는지'를 순식간에 잃게 됩니다.

Git은 이 문제를 해결하는 가장 강력한 도구입니다. AI가 생성한 코드든 직접 작성한 코드든 상관없이, 변경 시점마다 스냅샷을 남기고 언제든 되돌아갈 수 있게 해 줍니다. Claude, Cursor, Copilot 같은 AI 코딩 도구를 쓸수록 Git이 더 중요해지는 이유가 여기에 있습니다.

Git을 명령 목록으로 접근하면 금방 막힙니다. 하지만 '파일의 변경을 시간 순서대로 보관하고 되돌리는 도구'라는 그림을 먼저 잡으면, `add`, `commit`, `push`가 왜 존재하는지 자연스럽게 이해됩니다. 이 글에서는 그 멘탈 모델부터 시작합니다.

> Git은 AI가 만든 코드의 안전망입니다. 스냅샷을 시간 순서대로 저장하고, 모든 상태는 'working directory · staging · repository'라는 세 영역 사이의 이동으로 설명됩니다.

---

## 이 글에서 다룰 문제
- 바이브코딩 환경에서 버전 관리가 왜 더욱 필수적일까요?
- Git이 분산 버전 관리 도구라고 부르는 이유는 무엇일까요?
- Git의 스냅샷 모델은 단순 백업과 무엇이 다를까요?
- AI에게 코드를 생성받을 때 어떤 시점에 commit해야 할까요?
- 초보자가 Git을 처음 설정할 때 가장 자주 놓치는 포인트는 무엇일까요?

바이브코딩을 하다 보면 AI가 한 번에 수십, 수백 줄을 생성합니다. 그 결과물이 마음에 들면 계속 진행하고, 아니면 되돌리고 싶어집니다. 하지만 되돌릴 기준점이 없으면 AI에게 "방금 전으로 돌아가 줘"라고 말해도 정확히 어떤 상태인지 설명하기 어렵습니다.

Git이 있으면 다릅니다. AI와 함께 작업하는 각 단계마다 commit을 남기면, 어느 시점의 코드든 정확히 꺼내볼 수 있습니다. "로그인 기능 추가 전"으로 돌아가거나, "AI가 리팩터링하기 전 버전"을 비교하는 일이 명령 몇 줄로 가능해집니다.

## Git의 세 가지 작업 영역

Git을 한 문장으로 줄이면 **파일의 스냅샷을 시간 순서대로 저장하는 도구**입니다. 내부적으로는 세 영역이 협력합니다.

- **Working Directory**: 지금 편집 중인 파일이 있는 작업 공간입니다.
- **Staging Area**: 다음 commit에 넣을 변경을 모아 두는 버퍼입니다.
- **Repository**: commit이 시간 순서대로 쌓이는 로컬 저장소입니다.

바이브코딩 맥락에서 이 세 영역은 이렇게 읽힙니다. AI가 코드를 생성하면 Working Directory에 변경이 생깁니다. 그 중 '기록으로 남길 것'을 선택해 Staging Area에 올리고(`git add`), 의도가 분명한 제목을 붙여 Repository에 저장합니다(`git commit`). 이 흐름이 반복되면 AI와의 협업 이력이 고스란히 남습니다.

## Before / After

**Git 없이 AI 코딩할 때**

```text
my-project/
my-project-v2/
my-project-before-refactor/
my-project-working-maybe/
```

어느 폴더가 최신인지 기억해야 하고, AI가 바꾼 내용이 무엇인지 직접 비교해야 합니다.

**Git으로 AI 코딩할 때**

```bash
$ git log --oneline
a3f1c0e feat: AI가 추가한 소셜 로그인 기능
7b2d8f1 refactor: AI 리팩터링 적용 - auth 모듈 분리
1c9a3e2 feat: 로그인 폼 초기 구현
```

각 단계의 의도가 기록으로 남고, 언제든 `git checkout`으로 돌아갈 수 있습니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| AI가 코드 생성할 때마다 commit 안 함 | 어느 시점이 '좋은 버전'인지 모름 | 기능 단위로 즉시 commit |
| `git add .`로 모든 파일 추가 | AI가 생성한 임시 파일, 시크릿도 포함될 수 있음 | `git status`로 확인 후 선택적 add |
| commit message를 "AI 코드 추가"로만 작성 | 나중에 무엇이 바뀐 건지 알 수 없음 | 기능/목적 중심 메시지 작성 |
| `.gitignore` 없이 시작 | API 키, `.env` 파일이 저장소에 올라감 | 첫 commit 전에 `.gitignore` 설정 |
| GitHub와 Git을 같은 도구로 혼동 | remote 개념에서 자주 막힘 | Git=로컬 도구, GitHub=원격 서비스로 구분 |

## AI에게 Git 관련 질문하는 팁

AI 코딩 도구와 함께 Git을 쓸 때 이런 프롬프트가 효과적입니다.

- "방금 네가 만든 코드를 commit하려고 해. 어떤 commit message가 적절할까?"
- "이 변경을 되돌리고 싶어. `git revert`와 `git reset` 중 어느 것을 써야 할까?"
- "`.gitignore`에 파이썬 프로젝트에서 무시해야 할 파일 목록을 추가해 줘."
- "Git 초기 설정을 알려줘. `user.name`과 `user.email`을 포함해서."

AI는 Git 명령의 옵션과 용도를 빠르게 설명해 줄 수 있습니다. 하지만 '어떤 시점에 commit할지'는 사람이 판단해야 합니다.

## 운영 체크리스트

- [ ] `git --version`이 정상 출력되는지 확인했습니다.
- [ ] `git config --global user.name`과 `user.email`을 설정했습니다.
- [ ] `git config --global init.defaultBranch main`을 설정했습니다.
- [ ] Working Directory, Staging Area, Repository를 각각 설명할 수 있습니다.
- [ ] Git과 GitHub의 차이를 한 문장으로 설명할 수 있습니다.
- [ ] AI로 작업할 때 commit 시점 기준을 정했습니다.

## 처음 질문으로 돌아가기

바이브코딩 환경에서 버전 관리가 왜 필수인가? AI는 한 번에 많은 코드를 바꿉니다. Git이 없으면 그 변경의 역사가 사라집니다. Git이 있으면 AI와의 모든 작업 단계가 기록으로 남아, 언제든 원하는 시점으로 돌아갈 수 있습니다. 스냅샷 모델, 세 가지 작업 영역, 그리고 commit 습관이 바이브코딩의 안전망입니다.

## 정리

Git은 파일의 스냅샷을 시간 순서대로 저장하는 분산 버전 관리 도구입니다. 변경은 Working Directory에서 시작해 Staging Area를 거쳐 Repository에 commit으로 남습니다. 바이브코딩 환경에서는 AI가 코드를 생성할 때마다 의미 있는 단위로 commit하는 습관이 핵심입니다. 처음 사용할 때는 `user.name`, `user.email`, `init.defaultBranch`를 먼저 설정해 두세요.

## 참고 자료

### 공식 문서
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)

### 관련 시리즈
- [GitHub Actions 101](../../github-actions-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Git & GitHub 기초 (1/10): Git이란 무엇인가? 버전 관리의 시작 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (2/10): 첫 commit 만들기 - init, status, add, commit
- 바이브코딩을 위한 Git & GitHub 기초 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기
- 바이브코딩을 위한 Git & GitHub 기초 (4/10): branch 기초 - 만들고 옮기고 비교하기
- 바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기
- 바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기
- 바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지
- 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
