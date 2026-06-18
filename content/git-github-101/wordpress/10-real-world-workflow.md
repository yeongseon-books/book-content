---
title: "바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로"
series: git-github-101
episode: 10
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI와의 협업을 issue → branch → PR → merge → release tag까지 하나의 반복 가능한 사이클로 만드는 방법을 익힙니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 마지막 글입니다.

AI와 함께 기능을 하나씩 만들 수 있게 됐다면, 이제 그 작업들을 하나의 흐름으로 연결할 차례입니다. Issue로 AI에게 넘길 작업을 정의하고, branch에서 AI와 함께 구현하고, PR로 검토받고, merge 후 release tag를 찍는 것까지가 하나의 사이클입니다.

이 흐름이 반복 가능해지면 \"AI와 함께 무엇을 만들었는지\"가 체계적으로 관리됩니다. 어떤 버전에 어떤 AI 세션이 기여했는지, 각 기능이 어떤 배경으로 만들어졌는지 언제든 추적할 수 있습니다.

> 바이브코딩 workflow는 AI와의 협업을 반복 가능한 사이클로 만드는 일입니다. issue가 입구이고 release tag가 출구입니다. 그 사이에서 AI와 함께 코드를 만들고 검토받는 흐름이 자리잡히면, AI 협업이 \"일회성 실험\"에서 \"체계적인 개발\"로 바뀝니다.

---

## 이 글에서 다룰 문제
- GitHub Flow를 AI 바이브코딩에 어떻게 적용할까요?
- issue → branch → PR → merge → tag까지 전체 흐름은 어떻게 되나요?
- AI 작업 중 실수가 생겼을 때 어떻게 회복할까요?
- squash merge가 AI 프로젝트에서 특히 유용한 이유는 무엇인가요?
- release tag와 Semantic Versioning을 어떻게 활용할까요?

바이브코딩에서 각 명령어를 따로 아는 것과, AI와의 협업 전체를 하나의 흐름으로 운영하는 것은 다릅니다. 이 글에서는 앞선 1~9편의 내용을 AI 바이브코딩 실전 workflow로 묶어 정리합니다.

## AI 바이브코딩 전체 사이클

```bash
# 1. Issue로 AI 작업 정의
# Issue #42: "소셜 로그인 구현 - OAuth 플로우, 토큰 갱신 포함"

# 2. Issue 기반 branch 생성
$ git switch main && git pull
$ git switch -c feat/social-login-42

# 3. AI와 함께 작업 후 atomic commit
$ git add app/auth/oauth.py
$ git commit -m "feat(auth): AI 구현 Google OAuth 플로우 (Issue #42)"
$ git add tests/test_oauth.py
$ git commit -m "test(auth): AI 생성 OAuth 테스트 케이스"

# 4. GitHub에 push → PR 생성
$ git push -u origin feat/social-login-42
# PR 본문: "AI 구현 소셜 로그인\nCloses #42"

# 5. 검토 후 squash merge
# PR merge → Issue #42 자동 종료

# 6. Release tag
$ git switch main && git pull
$ git tag -a v0.3.0 -m "소셜 로그인 추가 (#42)"
$ git push --tags
```

## Issue → Branch → PR → Tag: 한 사이클 완전 흐름

**1단계: Issue로 AI 작업 범위 정의**

```markdown
## Issue #42: 소셜 로그인 구현

## AI에게 넘길 작업
- [ ] Google OAuth 인증 플로우
- [ ] 토큰 갱신 로직
- [ ] 테스트 케이스 생성

## 완료 조건
- 소셜 로그인 성공 시 기존 사용자 시스템 연동
- 테스트 커버리지 80% 이상
```

**2단계: branch 이름에 Issue 번호 포함**

```bash
$ git switch -c feat/social-login-42
# feat/<기능명>-<Issue번호> 형식
```

**3단계: PR 본문에 AI 생성 코드 안내 + Issue 연결**

```markdown
## AI 생성 코드 안내
이 PR의 핵심 로직은 Claude AI가 생성했습니다.
token_refresh.py의 만료 처리 로직을 집중 검토해 주세요.

Closes #42
```

**4단계: squash merge로 main 이력 정리**

```bash
# feature branch의 여러 AI 작업 commit을 하나로 묶어 main에 반영
# main: feat(auth): 소셜 로그인 구현 (#42) — 깔끔한 한 줄 기록
```

**5단계: Semantic Versioning으로 release tag**

```bash
$ git tag -a v0.3.0 -m "Add social login (Closes #42)"
$ git push --tags
# v<MAJOR>.<MINOR>.<PATCH>
# 새 기능 추가 → MINOR 증가
```

## Before / After

**workflow 없이 AI 바이브코딩할 때**

```text
- Issue 없이 AI에게 바로 요청 → 작업 맥락 기록 없음
- main에 직접 AI 코드 push → 검토 없이 배포
- release 시점 불명확 → \"언제 이 기능이 나갔지?\" 모름
- 실수 발생 → 어떻게 되돌릴지 몰라 당황
```

**GitHub Flow로 AI 바이브코딩 관리할 때**

```text
Issue #42 생성 → feat/social-login-42 branch → AI 작업
→ PR #17 (Closes #42, AI 코드 검토 요청)
→ 팀 리뷰 + CI 통과 → squash merge
→ v0.3.0 tag → Issue 자동 종료
→ 6개월 후: "소셜 로그인은 #42에서, PR #17에서, v0.3.0에 포함"
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Issue 없이 AI에게 작업 요청 | AI 세션 목적이 기록 안 됨 | 작업 시작 전 Issue 먼저 생성 |
| main에 직접 AI 코드 commit | 검토 없이 배포, 되돌리기 어려움 | 항상 feature branch에서 시작 |
| AI 작업 전부를 하나의 거대한 PR로 | 리뷰어가 전체를 제대로 못 봄 | Issue 단위로 PR 분리 |
| release tag 없이 배포 | \"이 버전에 뭐가 들어갔지?\" 추적 불가 | merge 후 바로 annotated tag 생성 |
| plain `--force` push 습관화 | 동료 commit을 덮어씀 | `--force-with-lease`만 사용 |

## AI에게 Git 관련 질문하는 팁

workflow 전반에서 AI를 활용하는 프롬프트입니다.

- \"이 AI 작업을 GitHub Flow로 관리하려면 어떤 Issue와 branch 이름이 적절할까?\"
- \"squash merge 후 main log가 너무 길어. commit message를 어떻게 정리하면 좋을까?\"
- \"AI가 만든 PR #17을 되돌려야 해. squash merge commit hash가 d5e6f7a일 때 어떻게 하나요?\"
- \"현재 v0.2.1이야. AI가 새 기능을 추가했는데 다음 버전을 뭐로 해야 할까?\"

## 회복 흐름: AI 작업 중 실수가 생겼을 때

| 상황 | 회복 방법 |
|------|----------|
| 잘못된 branch에 AI 코드 commit (push 전) | `git cherry-pick <hash>`로 올바른 branch에 옮기고, 원래 branch에서 `git reset --hard HEAD~1` |
| AI 코드 commit message만 수정하고 싶음 | `git commit --amend -m "..."` (push 전에만) |
| push한 AI 코드를 되돌리고 싶음 | `git revert <hash>` → `git push` (새 commit으로 안전하게 취소) |
| squash merge된 PR을 되돌려야 함 | `git revert <squash-commit-hash>` → `git push` |
| AI가 `.env`를 commit에 포함했음 | 즉시 secret 회수 → `.gitignore`에 추가 → 기록 정리 |

## 운영 체크리스트

- [ ] AI 작업 시작 전 Issue를 먼저 생성합니다.
- [ ] branch 이름에 Issue 번호를 포함합니다 (`feat/<slug>-<N>`).
- [ ] AI 작업을 atomic commit으로 분리합니다.
- [ ] PR 본문에 AI 생성 코드임을 명시하고 `Closes #N`을 포함합니다.
- [ ] CI 통과 후에만 merge합니다.
- [ ] squash merge 후 feature branch를 삭제합니다.
- [ ] release 시 annotated tag를 만들고 `--tags`로 push합니다.
- [ ] `--force` 대신 `--force-with-lease`를 사용합니다.

## 처음 질문으로 돌아가기

AI 바이브코딩을 체계적으로 관리하는 방법은? Issue로 작업을 정의하고, feature branch에서 AI와 함께 구현하고, PR로 검토받고, squash merge로 main을 정리하고, release tag로 버전을 기록합니다. 이 사이클이 반복 가능해지면 \"AI와 무엇을 왜 만들었는지\"를 언제든 추적할 수 있는 이력이 쌓입니다.

## 정리

GitHub Flow는 바이브코딩에 가장 잘 맞는 workflow입니다. issue가 AI 작업의 입구이고, release tag가 출구입니다. 그 사이에서 feature branch → AI 작업 → PR → 검토 → squash merge의 사이클이 반복됩니다. 팀에서는 branch protection, PR template, CI를 더해 이 흐름을 자동으로 강제합니다. 시리즈를 통해 배운 모든 Git/GitHub 명령이 이 하나의 workflow 안에서 제자리를 찾습니다.

## 참고 자료

### 공식 문서
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [Semantic Versioning](https://semver.org/)

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
- 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- **바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
