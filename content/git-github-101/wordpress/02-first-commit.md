---
title: "바이브코딩을 위한 Git & GitHub 기초 (2/10): 첫 commit 만들기 - init, status, add, commit"
series: git-github-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 첫 코드를 Git에 안전하게 저장하는 init, status, add, commit 흐름을 실습합니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (2/10): 첫 commit 만들기 - init, status, add, commit

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 2번째 글입니다.

AI 도구로 프로젝트를 시작하면 순식간에 수십 개의 파일이 생성됩니다. Cursor나 Claude가 "프로젝트 구조를 잡아 드릴게요"라고 하면서 폴더와 파일을 뚝딱 만들어 내는 순간, 여기서 바로 Git을 시작해야 합니다. 그 첫 순간을 놓치면 "어떤 파일이 AI가 만든 것이고 어떤 게 내가 수정한 것인지" 나중에 구분하기 어려워집니다.

첫 commit은 단순히 "저장" 버튼이 아닙니다. Working Directory에서 Staging Area를 거쳐 Repository로 이어지는 한 사이클을 직접 경험하는 일입니다. 이 흐름을 한 번 손으로 따라가면, 이후 AI와 함께 작업하면서 언제 commit해야 하는지 감이 잡힙니다.

바이브코딩에서 첫 commit의 중요성은 두 가지입니다. 첫째, AI가 생성한 초기 구조를 기록으로 남깁니다. 둘째, 이후 AI가 바꾸는 모든 것을 이 기준점과 비교할 수 있게 됩니다.

> 첫 commit은 'snapshot 하나를 만드는 의식'이 아니라 AI가 만든 초기 코드를 안전하게 봉인하는 일입니다. 이 기준점이 있어야 "AI 수정 이전"으로 언제든 돌아갈 수 있습니다.

---

## 이 글에서 다룰 문제
- `git init`은 현재 디렉터리에 정확히 무엇을 만들까요?
- AI가 만든 파일을 어떻게 선택적으로 staging에 올릴까요?
- `git status`는 파일 상태를 어떻게 보여 주고, 어떻게 읽어야 할까요?
- AI가 `.env`나 API 키 파일을 만들었을 때 어떻게 처리해야 할까요?
- 바이브코딩 프로젝트에서 첫 commit message는 어떻게 써야 할까요?

AI로 코드를 시작하는 순간 Working Directory에는 파일이 쌓입니다. Git 없이 계속 가면 AI가 바꾼 것과 내가 바꾼 것이 뒤섞이고, 어느 시점이 "잘 동작하던 버전"인지 알 수 없게 됩니다. `git init`으로 저장소를 만들고, 첫 commit으로 기준점을 잡는 것이 바이브코딩의 출발점입니다.

## 세 영역의 동작 방식

첫 commit을 이해하려면 세 동사가 함께 움직임을 알아야 합니다.

- **edit**: AI가 파일을 만들거나 수정합니다.
- **`add`**: 다음 commit에 포함할 변경으로 올립니다.
- **`commit`**: staging에 모인 내용을 하나의 snapshot으로 저장합니다.

`git status`는 이 흐름 전체에서 현재 위치를 알려 주는 안내판입니다.

```bash
# AI가 파일을 생성한 직후
$ git status
On branch main
Untracked files:
  app.py
  .env          # 위험! API 키가 들어있을 수 있음
  requirements.txt

# .gitignore로 민감 파일 먼저 제외
$ echo ".env" >> .gitignore
$ git add .gitignore app.py requirements.txt
$ git status
Changes to be committed:
  new file: .gitignore
  new file: app.py
  new file: requirements.txt
```

## Before / After

**Git 없이 AI 프로젝트 시작할 때**

```text
my-app/        ← AI가 만든 초기 구조
  app.py       ← 나중에 AI가 수정
  config.py    ← 내가 수정
  .env         ← API 키 (노출 위험)
```

무엇이 원래 AI가 만든 것인지, 어떤 파일이 위험한지 알 수 없습니다.

**Git으로 AI 프로젝트 시작할 때**

```bash
$ git log --oneline
b3f2a1e chore: AI 초기 프로젝트 구조 생성
1a9c3d2 chore: .gitignore 설정 (.env, __pycache__ 제외)
```

AI가 만든 초기 구조와 내 설정이 분리되어 기록됩니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| AI 생성 직후 `git add .` 바로 실행 | `.env`, API 키가 저장소에 올라감 | `git status`로 확인 후 `.gitignore` 먼저 설정 |
| 프로젝트 완성 후 첫 commit | 어느 시점이 AI 초기 구조인지 모름 | AI가 파일 생성하면 즉시 첫 commit |
| 홈 디렉터리에서 `git init` 실행 | 전체 홈 폴더가 저장소가 됨 | 프로젝트 폴더 안에서만 실행 |
| commit message "first commit"으로만 작성 | AI가 만든 것인지 내가 만든 것인지 불분명 | "chore: AI 초기 프로젝트 구조 생성"처럼 명확히 |
| `git add` 없이 `git commit` 시도 | staging이 비어 있어 commit 안 됨 | 반드시 add 후 commit |

## AI에게 Git 관련 질문하는 팁

첫 commit 단계에서 AI에게 물어볼 수 있는 효과적인 프롬프트입니다.

- "이 파이썬 프로젝트에 적합한 `.gitignore` 파일을 만들어 줘. API 키와 가상 환경 폴더를 제외해야 해."
- "방금 네가 만든 파일들을 첫 commit으로 남기려고 해. 어떤 파일을 먼저 add해야 할까?"
- "이 프로젝트의 첫 commit message를 Conventional Commits 형식으로 추천해 줘."
- "`git add -p`로 파일의 일부만 staging하는 방법을 설명해 줘."

## 운영 체크리스트

- [ ] `git init`으로 `.git/` 디렉터리를 만들었습니다.
- [ ] AI 생성 파일 중 `.env`, 비밀 키를 `.gitignore`에 추가했습니다.
- [ ] `git status`로 staging 상태를 확인했습니다.
- [ ] 첫 commit을 만들고 `git log --oneline`으로 확인했습니다.
- [ ] commit 후 `git status`가 `working tree clean`인지 확인했습니다.
- [ ] AI가 이후 코드를 수정할 때 commit 기준점이 생겼습니다.

## 처음 질문으로 돌아가기

AI가 만든 코드를 어떻게 안전하게 저장하나? `git init`으로 저장소를 만들고, `.gitignore`로 민감 파일을 제외하고, `git add`로 기록할 파일을 선택하고, `git commit`으로 스냅샷을 남깁니다. 이 첫 commit이 있어야 AI와 함께하는 모든 이후 변경의 기준점이 생깁니다.

## 정리

`git init`은 현재 폴더를 저장소로 바꾸고, `git status`는 각 변경이 어느 영역에 있는지 알려 주며, `git add`와 `git commit`은 그 변경을 snapshot으로 저장합니다. 바이브코딩 환경에서는 AI가 파일을 생성하는 순간 `.gitignore` 설정과 첫 commit을 바로 남기는 습관이 핵심입니다.

## 참고 자료

### 공식 문서
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)

### 관련 시리즈
- [GitHub Actions 101](../../github-actions-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Git & GitHub 기초 (1/10): Git이란 무엇인가? 버전 관리의 시작
- **바이브코딩을 위한 Git & GitHub 기초 (2/10): 첫 commit 만들기 - init, status, add, commit (현재 글)**
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
