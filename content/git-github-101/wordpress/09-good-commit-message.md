---
title: "바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문"
series: git-github-101
episode: 9
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI가 만든 코드에 의미 있는 commit message를 남겨 '왜 이 코드가 있는지' 언제든 추적하는 방법을 배웁니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 9번째 글입니다.

AI는 코드를 빠르게 만들지만 commit message는 만들어 주지 않습니다. AI 세션이 쌓일수록 `git log`는 \"AI가 뭔가 만들었음\", \"버그 수정\", \"수정\"처럼 의미 없는 기록으로 가득 찹니다. 한 달 뒤 \"이 코드는 왜 이렇게 됐지?\"라고 물으면 답을 찾을 수 없습니다.

좋은 commit message는 AI가 만든 코드에 맥락을 붙이는 작업입니다. \"AI가 소셜 로그인 OAuth 플로우를 구현했다\"는 사실이 아니라, \"왜 이 방식을 선택했는지\", \"어떤 Issue를 해결하는 작업인지\"를 기록하는 것입니다. 이것이 바이브코딩에서 commit message가 단순한 형식 이상의 의미를 갖는 이유입니다.

> commit message는 AI가 만든 코드에 사람이 붙이는 맥락입니다. `git log`가 \"AI와 언제 무엇을 왜 만들었는지\"를 답해줄 수 있어야 합니다.

---

## 이 글에서 다룰 문제
- AI가 만든 코드에 왜 좋은 commit message가 특히 중요한가요?
- Conventional Commits의 `feat`, `fix`, `docs` type은 어떻게 구분하나요?
- subject, body, footer에는 각각 무엇을 담아야 하나요?
- AI 코딩에서 commit message를 어떻게 효율적으로 작성하나요?
- `--amend`와 `rebase -i`로 message를 언제 다듬어야 하나요?

AI 바이브코딩에서 commit이 쌓이는 속도는 일반 개발보다 빠릅니다. 바로 그렇기 때문에 각 commit이 \"AI에게 무엇을 시켰고 그 결과가 무엇인지\"를 명확히 기록하지 않으면, 이력 전체가 의미를 잃습니다.

## AI 코딩에서 commit message가 특히 중요한 이유

바이브코딩 프로젝트에서 commit message는 두 가지 역할을 합니다.

```text
# AI 없이 개발할 때
commit: "소셜 로그인 추가"
# 개발자가 직접 구현했으므로 코드를 보면 의도를 어느 정도 유추 가능

# AI와 바이브코딩할 때
commit: "소셜 로그인 추가"
# AI가 만든 코드 → 왜 이 방식인지, 어떤 대안을 고려했는지 불분명
# → commit message가 유일한 맥락 기록
```

AI가 생성한 코드는 작성자의 의도가 코드에 직접 녹아있지 않습니다. commit message가 \"AI에게 무엇을 요청했고 왜 이 결과를 선택했는지\"를 기록하는 유일한 공간입니다.

## Conventional Commits: AI 작업을 분류하는 기준

```bash
# AI가 새 기능을 만들었을 때
$ git commit -m "feat(auth): AI가 구현한 Google OAuth 소셜 로그인"

# AI가 버그를 수정했을 때
$ git commit -m "fix(auth): OAuth 콜백에서 null redirect_uri 처리"

# AI가 코드 구조를 개선했을 때
$ git commit -m "refactor(auth): AI가 토큰 검증 로직을 별도 모듈로 분리"

# AI가 테스트를 작성했을 때
$ git commit -m "test(auth): AI가 생성한 OAuth 플로우 테스트 케이스"
```

| Type | AI 작업 예시 | 언제 쓰는가 |
|------|------------|------------|
| `feat` | AI가 새 기능 구현 | 사용자 관점에서 기능이 추가됨 |
| `fix` | AI가 버그 수정 | 기대 동작과 실제 동작의 차이를 바로잡음 |
| `refactor` | AI가 코드 구조 개선 | 동작은 같고 내부 구조만 개선 |
| `test` | AI가 테스트 작성 | 테스트 코드 추가/수정 |
| `docs` | AI가 문서 작성 | 코드 동작 변화 없이 문서만 변경 |
| `chore` | 빌드/설정 작업 | 패키지, 스크립트, 설정 정리 |

## AI 코딩에 맞는 subject, body, footer

```text
feat(auth): Google OAuth 소셜 로그인 구현

AI(Claude)와 함께 구현한 OAuth 플로우입니다.
이메일/비밀번호 로그인만 지원하던 기존 구조에서
소셜 로그인 요구가 계속 들어와 Issue #42로 정의하고 진행했습니다.

AI가 제안한 두 가지 방식(JWT vs 세션 기반) 중
기존 인증 시스템과의 호환성을 고려해 세션 기반을 선택했습니다.

Closes #42
```

- **subject**: 50자 이하, 명령형, 마침표 없이 — type(scope): 무엇을 했는지
- **body**: 빈 줄 뒤, AI와의 작업 맥락, 선택 이유 — 왜 이 방식인지
- **footer**: Issue 번호, Breaking change — 메타데이터 분리

## Before / After

**AI 코딩에서 나쁜 commit message 습관**

```text
$ git log --oneline -6
9f8e7d6 수정
8e7d6c5 AI 작업
7d6c5b4 기능 추가
6c5b4a3 버그 수정
5b4a3f2 일단 커밋
4a3f2e1 테스트
# 한 달 뒤: 어떤 AI 세션이 무엇을 만들었는지 전혀 모름
```

**Conventional Commits + AI 맥락을 담은 message**

```text
$ git log --oneline -6
9f8e7d6 feat(auth): AI 구현 Google OAuth 소셜 로그인 (Closes #42)
8e7d6c5 fix(auth): OAuth 콜백 null 처리 — AI 코드 검토 중 발견
7d6c5b4 refactor(auth): AI가 토큰 검증 로직 모듈화
6c5b4a3 test(auth): AI 생성 OAuth 테스트 케이스 추가
5b4a3f2 docs(auth): AI가 작성한 OAuth 설정 가이드
4a3f2e1 feat(payment): AI 구현 결제 모듈 기초 (Closes #38)
# 각 AI 세션이 무엇을 왜 만들었는지 바로 파악 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| \"AI 코드 추가\" 같은 모호한 message | AI 세션 목적이 기록 안 됨 | type(scope): 구체적 변경 내용 명시 |
| subject에 Issue 번호, URL 넣기 | 한 줄 요약이 지저분해짐 | footer에 `Closes #N`으로 분리 |
| AI가 만든 코드를 전부 하나의 commit으로 | 너무 큰 commit, 되돌리기 어려움 | 기능 단위로 atomic commit 분리 |
| body 없이 subject만 | AI 선택 이유, 대안 검토 기록 없음 | body에 AI와의 작업 맥락 추가 |
| push 후 message 수정 시 `--amend` 무분별 사용 | 동료와 hash 충돌 발생 | push 전에만 amend, 이후엔 새 commit |

## AI에게 Git 관련 질문하는 팁

AI와 commit message를 작성할 때 효과적인 프롬프트입니다.

- \"이 diff를 붙여넣을게. Conventional Commits 형식으로 commit message를 작성해 줘.\"
- \"방금 AI가 구현한 소셜 로그인 코드야. Issue #42 관련 commit message body에 뭘 써야 할까?\"
- \"이 AI 작업을 atomic commit 3개로 나눈다면 어떻게 나눌까?\"
- \"지난 AI 세션 결과를 commit하려 해. subject, body, footer 구조로 message를 만들어 줘.\"

## `--amend`로 AI 작업 커밋 다듬기

```bash
# AI 작업 직후 급하게 commit한 경우
$ git commit -m "AI 코드"

# push 전에 더 나은 message로 수정
$ git commit --amend -m "feat(auth): AI가 구현한 Google OAuth 소셜 로그인"
# hash가 바뀌므로 push 전에만 사용

# body까지 추가하려면 editor 열기
$ git commit --amend
```

```bash
# 여러 AI 세션 commit을 정리할 때
$ git rebase -i HEAD~3

# 편집 화면에서
# pick → reword: message만 변경
# pick → fixup: 앞 commit에 합치고 message는 버림
# pick → squash: 앞 commit에 합치고 두 message 편집
```

## 운영 체크리스트

- [ ] AI 작업 완료 후 Conventional Commits 형식으로 commit합니다.
- [ ] subject에 type(scope)을 명시합니다 (feat, fix, refactor 등).
- [ ] body에 AI와의 작업 맥락과 선택 이유를 기록합니다.
- [ ] Issue와 연결된 작업은 footer에 `Closes #N`을 넣습니다.
- [ ] push 전에 `git log -1 --pretty=fuller`로 message를 확인합니다.
- [ ] AI 작업을 atomic commit으로 분리합니다 (기능 단위).

## 처음 질문으로 돌아가기

AI가 만든 코드의 맥락을 나중에 파악하려면? commit message에 남깁니다. type(scope)으로 AI 작업 종류를 분류하고, body에 왜 이 방식을 선택했는지 기록하며, footer에 Issue 번호를 연결합니다. `git log`가 \"AI와 무엇을 왜 만들었는지\"를 답해주는 이력이 됩니다.

## 정리

Conventional Commits는 AI 작업을 `feat`, `fix`, `refactor` 등으로 분류하는 체계입니다. subject는 무엇을 했는지, body는 왜 이 방식인지(AI 선택 이유 포함), footer는 Issue 번호 같은 메타데이터를 담습니다. push 전에는 `--amend`로 자유롭게 다듬고, 여러 commit을 정리할 때는 `rebase -i`를 활용합니다. 바이브코딩에서 좋은 commit message는 AI와의 협업 이력을 언제든 추적 가능하게 만드는 가장 기본적인 문서입니다.

## 참고 자료

### 공식 문서
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

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
- **바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
