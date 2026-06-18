---
title: "바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법"
series: git-github-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI에게 무엇을 만들어 달라고 할지 Issue로 정의하고 Project로 진행을 추적하는 방법을 익힙니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 8번째 글입니다.

바이브코딩을 하다 보면 AI에게 이것저것 만들어 달라고 하다가 어느 순간 "지금 뭘 만들고 있었지?"가 됩니다. AI는 프롬프트를 받으면 코드를 만들지만, 큰 그림에서 어떤 기능이 완성됐고 뭐가 남았는지는 사람이 관리해야 합니다.

GitHub Issue는 "AI에게 무엇을 만들어 달라고 할지"를 미리 정의하는 공간입니다. "소셜 로그인 기능 추가", "결제 모듈 구현", "성능 개선"처럼 AI에게 넘길 작업 단위를 Issue로 만들어 두면, 각 AI 세션이 어떤 목적으로 진행됐는지 이력이 남습니다.

Issue와 PR을 연결하면 더 강력해집니다. "AI와 함께 이 Issue를 해결했다"는 기록이 코드 이력에 남고, 나중에 "이 기능은 어떤 배경으로 만들어졌지?"라는 질문에 바로 답할 수 있습니다.

> Issue는 AI에게 작업을 넘기기 전 '무엇을 만들지' 정의하는 공간입니다. PR과 연결하면 AI 협업 이력이 체계적으로 관리됩니다.

---

## 이 글에서 다룰 문제
- GitHub Issue를 AI 작업 관리에 어떻게 활용할까요?
- `Closes #42`는 어떻게 Issue와 PR을 자동으로 연결할까요?
- AI 작업을 위한 Issue 작성 요령은 무엇인가요?
- Project board로 AI 프로젝트 진행을 어떻게 추적할까요?
- label, milestone을 바이브코딩 환경에서 어떻게 활용할까요?

AI와 함께 개발할 때 Issue 없이 진행하면, 각 AI 세션이 왜 시작됐는지 맥락을 잃기 쉽습니다. Issue가 있으면 "이 commit과 PR은 #42 소셜 로그인 Issue를 위한 것"이라는 연결고리가 생깁니다.

## AI 작업용 Issue 작성 요령

AI에게 작업을 넘기기 전 Issue를 잘 작성하면, AI 프롬프트도 더 명확해집니다.

```markdown
## 배경
현재 이메일/비밀번호 로그인만 지원하고 있어
소셜 로그인 요구가 계속 들어오고 있습니다.

## 목표
Google, GitHub OAuth 소셜 로그인 구현

## AI에게 넘길 작업
- [ ] OAuth 인증 플로우 구현
- [ ] 토큰 갱신 로직 작성
- [ ] 테스트 케이스 생성

## 완료 조건
- 소셜 로그인 성공 시 기존 사용자 시스템과 연동
- 테스트 커버리지 80% 이상

## 범위 제외
- 소셜 계정 연결/해제 UI (다음 이슈)
```

## Issue - PR - Project 연결 흐름

```bash
# 1. Issue #42 생성: "소셜 로그인 구현"

# 2. Issue 기반 branch 생성
$ git switch -c feature/social-login-42

# 3. AI와 함께 작업 후 commit
$ git commit -m "feat(auth): AI가 구현한 Google OAuth 플로우"

# 4. PR 생성 시 Issue 연결
# PR 본문: "Closes #42"
# → merge 시 Issue 자동 종료

# 5. Project board에서 상태 확인
# Todo → In Progress → In Review → Done
```

## Before / After

**Issue 없이 AI 바이브코딩할 때**

```text
commit: "소셜 로그인 추가"
commit: "버그 수정"
commit: "개선"
# 몇 달 후: 왜 이런 기능이 있는지, 누가 요청했는지 모름
```

**Issue + PR 연결로 AI 작업 관리할 때**

```text
Issue #42: 소셜 로그인 구현 요청 (사용자 피드백 기반)
PR #17: feat(auth): 소셜 로그인 구현 (Closes #42)
commit: AI가 생성한 OAuth 플로우 + 수동 검토 완료
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Issue 없이 AI에게 바로 작업 요청 | AI 작업의 목적과 맥락이 기록 안 됨 | 작업 시작 전 Issue 먼저 생성 |
| PR 본문에 `Closes #N` 누락 | Issue가 자동으로 안 닫힘 | PR 본문에 항상 연결 Issue 명시 |
| Issue 본문이 너무 추상적 | AI에게 명확한 작업 지시 어려움 | 구체적인 완료 조건 포함 |
| Project board 업데이트 방치 | 현재 진행 상황 파악 어려움 | PR merge 시 자동화 설정 |
| AI 작업을 하나의 거대한 Issue로 묶음 | PR이 너무 커져 리뷰 어려움 | 작업을 작은 Issue로 분리 |

## AI에게 Git 관련 질문하는 팁

Issue와 Project 관리에서 AI를 활용하는 프롬프트입니다.

- "이 기능을 구현하려고 해. GitHub Issue를 어떻게 작성하면 나중에 AI에게 작업을 넘기기 좋을까?"
- "현재 열린 Issue 목록이야. 어떤 순서로 처리하는 게 효율적일까?"
- "이 Issue를 처리하기 위한 Git branch 이름과 PR 제목을 추천해 줘."
- "소셜 로그인 기능을 단계별 Issue로 분리해 줘. AI가 한 번에 처리할 수 있는 크기로."

## 운영 체크리스트

- [ ] AI에게 작업을 넘기기 전 Issue를 먼저 생성합니다.
- [ ] Issue에 완료 조건과 AI에게 넘길 작업을 명시합니다.
- [ ] branch 이름에 Issue 번호를 포함합니다 (예: `feature/social-login-42`).
- [ ] PR 본문에 `Closes #N`을 포함합니다.
- [ ] merge 후 Issue가 자동으로 닫혔는지 확인합니다.
- [ ] Project board에서 AI 작업 진행 상황을 주기적으로 확인합니다.

## 처음 질문으로 돌아가기

AI 바이브코딩 프로젝트를 체계적으로 관리하려면? Issue로 작업을 정의하고, branch와 PR에 Issue 번호를 연결하며, Project board로 진행을 추적합니다. 이렇게 하면 "AI가 무엇을 왜 만들었는지"를 언제든 추적할 수 있는 이력이 생깁니다.

## 정리

Issue는 AI에게 작업을 넘기기 전 무엇을 만들지 정의하는 공간입니다. PR 본문의 `Closes #N`은 merge 시 Issue를 자동으로 닫습니다. Project board는 AI 작업의 현재 상태를 시각화합니다. 바이브코딩에서 이 세 도구를 연결하면 AI와의 협업 이력이 체계적으로 관리됩니다.

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
- 바이브코딩을 위한 Git & GitHub 기초 (2/10): 첫 commit 만들기 - init, status, add, commit
- 바이브코딩을 위한 Git & GitHub 기초 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기
- 바이브코딩을 위한 Git & GitHub 기초 (4/10): branch 기초 - 만들고 옮기고 비교하기
- 바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기
- 바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기
- 바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지
- **바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
