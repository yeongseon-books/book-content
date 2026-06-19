---
series: open-source-101
episode: 4
title: "Open Source 101 (4/10): 풀 리퀘스트 만들기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - PullRequest
  - Git
  - GitHub
  - Beginner
seo_description: 풀 리퀘스트를 단순한 코드 덩어리가 아니라 검토 가능한 변경 제안서로 작성하는 법과 포크부터 리뷰 대응까지의 협업 절차를 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (4/10): 풀 리퀘스트 만들기

오픈소스 기여에서 가장 눈에 잘 보이는 결과물은 풀 리퀘스트입니다. 그래서 초보자는 풀 리퀘스트만 열면 기여가 끝난 것처럼 느끼기 쉽습니다. 하지만 메인테이너 입장에서 풀 리퀘스트는 코드 덩어리가 아니라, 검토 가능한 변경 제안서입니다. 무엇을 왜 바꿨는지, 범위가 적절한지, 안전하게 병합할 수 있는지가 더 중요합니다.

이 글은 오픈소스 101 시리즈의 4번째 글입니다.

여기서는 포크, 브랜치, 커밋, 설명, 리뷰 대응까지 포함해 메인테이너가 반기는 작은 풀 리퀘스트를 만드는 기본 절차를 정리하겠습니다.

![Open Source 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/04/04-01-put-the-flow-in-your-head-first.ko.png)
*Open Source 101 4장 흐름 개요*
> PR을 보내는 것은 완성된 코드를 제출하는 일이 아닙니다. **피드백을 받으면서 함께 코드를 개선하는 과정**입니다.

## 이 글에서 다룰 문제

- 메인테이너가 반기는 풀 리퀘스트는 어떤 모양일까요?
- 포크, 브랜치, 커밋, 풀 리퀘스트 흐름을 왜 매번 분리해야 할까요?
- 커밋 메시지와 풀 리퀘스트 설명은 각각 어떤 역할을 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

코드는 맞는데 풀 리퀘스트가 불편하면 리뷰가 늦어집니다. 반대로 수정 내용이 크지 않아도 풀 리퀘스트 구성이 좋으면 메인테이너가 빠르게 맥락을 파악할 수 있습니다. 초보자 입장에서는 실력보다 협업 방식이 더 먼저 평가될 때가 많습니다.

실무에서도 상황은 같습니다. 회사 안에서든 오픈소스에서든 풀 리퀘스트는 코드 리뷰의 기본 단위입니다. 작은 변경을 명확한 이야기로 정리하는 능력은 어디서나 바로 통합니다.

## 핵심 관점

좋은 풀 리퀘스트는 구현보다 구조가 먼저 정리된 풀 리퀘스트입니다. 브랜치가 독립돼 있고, 변경 범위가 작고, 설명이 분명하고, 관련 이슈와 테스트가 연결돼 있으면 리뷰는 훨씬 부드럽게 흐릅니다.

> PR을 보내는 것은 완성된 코드를 제출하는 일이 아닙니다. **피드백을 받으면서 함께 코드를 개선하는 과정**입니다.

각 역할을 분리해 보면 훨씬 이해가 쉽습니다:
- **포크**: 개인 작업 공간 (원본 보호)
- **브랜치**: 변경 단위 (목적 하나에 브랜치 하나)
- **커밋**: 변경 이력 (각 커밋은 이유가 있어야 함)
- **PR**: 검토 요청 (코드 + 맥락 + 테스트 증거)

## 핵심 개념

### PR 크기와 리뷰 품질

PR 크기는 리뷰 속도에 직결됩니다.

| PR 규모 | 변경 줄 수 | 리뷰 품질 | 권장 여부 |
|---|---|---|---|
| XS | 1-50줄 | 최상 | 항상 권장 |
| S | 50-200줄 | 좋음 | 권장 |
| M | 200-400줄 | 보통 | 가능하면 분할 |
| L | 400-600줄 | 낮음 | 분할 필요 |
| XL | 600줄 이상 | 매우 낮음 | 반드시 분할 |

큰 기능을 작은 PR로 나누는 전략:
```text
기능: 사용자 인증 시스템 추가

PR 1: feat: add User model and database schema
PR 2: feat: implement password hashing
PR 3: feat: add login endpoint
PR 4: feat: add session management
PR 5: feat: add logout endpoint
PR 6: test: add auth integration tests
PR 7: docs: update API documentation
```

### 커밋 메시지 규칙

**Conventional Commits** 형식을 따르면 changelog 자동 생성이 가능합니다.

```text
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**타입 목록**:
```text
feat:     새 기능
fix:      버그 수정
docs:     문서 수정
style:    코드 포매팅 (기능 변경 없음)
refactor: 리팩토링 (버그 수정·기능 추가 없음)
test:     테스트 추가·수정
chore:    빌드 과정·도구 설정 변경
perf:     성능 개선
```

**좋은 커밋 메시지 예시**:
```text
fix(auth): prevent session fixation on login

Before this change, the session ID was not rotated after
successful authentication, creating a session fixation
vulnerability.

After login, we now regenerate the session ID while
preserving session data.

Closes #1234
```

**나쁜 커밋 메시지 예시**:
```text
fix bug

WIP

수정

asdfasdf
```

## PR 전체 워크플로 예시

첫 기여부터 머지까지의 전체 흐름을 명령어와 함께 봅니다.

```bash
# 1. 포크 및 클론
gh repo fork requests/requests --clone
cd requests

# 2. upstream 연결 (필수 - 나중에 동기화에 필요)
git remote add upstream https://github.com/psf/requests.git
git remote -v
# origin    https://github.com/yourusername/requests.git
# upstream  https://github.com/psf/requests.git

# 3. 최신 upstream으로 동기화
git fetch upstream
git checkout main
git merge upstream/main

# 4. 작업 브랜치 생성 (이슈 번호 포함)
git checkout -b fix/1234-session-cookie-safari

# 5. 변경 구현
# requests/adapters.py 수정...

# 6. 테스트 실행
pytest tests/test_adapters.py -v
# 기존 테스트 통과 확인
pytest tests/test_adapters.py::TestHttpAdapter::test_cookie_redirect -v
# 새 테스트 통과 확인

# 7. 커밋 (작은 단위로)
git add requests/adapters.py
git commit -m "fix(adapters): preserve cookies across redirects

Safari 15 changed cookie handling for cross-origin redirects.
Update HTTPAdapter.send() to explicitly copy cookies from
the response to the prepared request on redirect.

Closes #1234"

# 테스트도 별도 커밋
git add tests/test_adapters.py
git commit -m "test(adapters): add Safari 15 cookie redirect test"

# 8. 포크에 푸시
git push origin fix/1234-session-cookie-safari

# 9. PR 생성
gh pr create \
  --title "fix(adapters): preserve cookies across redirects on Safari 15" \
  --body "## Summary
Safari 15 changed cookie handling for cross-origin redirects, causing
session cookies to be lost after a redirect.

## Changes
- `requests/adapters.py`: Copy cookies from response to next request in redirect chain
- `tests/test_adapters.py`: Add regression test for Safari 15 behavior

## Testing
\`\`\`bash
pytest tests/test_adapters.py -v
# 142 passed, 0 failed
\`\`\`
Manual testing on Safari 15.1 (macOS 12): cookies persisted correctly.

## Related Issues
Closes #1234

## Checklist
- [x] Tests added and passing
- [x] No breaking changes
- [x] Documentation updated (N/A for internal change)"

# 10. 리뷰 피드백 반영
# 리뷰어: "쿠키 병합 방식을 dict.update() 대신 CookieJar.update()로 변경"
git add requests/adapters.py
git commit -m "fix: use CookieJar.update() per review feedback"
git push origin fix/1234-session-cookie-safari

# 11. 머지 후 정리
git checkout main
git pull upstream main
git branch -d fix/1234-session-cookie-safari
git push origin --delete fix/1234-session-cookie-safari
```

## PR 설명 템플릿

`.github/PULL_REQUEST_TEMPLATE.md`에 다음처럼 작성하면 PR을 열 때 자동으로 본문이 채워집니다.

```markdown
## Summary
<!-- 이 PR이 무엇을 하는지 1-2줄로 요약합니다 -->

## Problem
<!-- 어떤 문제가 있었나요? 관련 이슈를 연결합니다 -->
Closes #

## Solution
<!-- 어떻게 해결했나요? 왜 이 접근 방식을 선택했나요? -->

## Changes
<!-- 변경된 파일과 이유를 목록으로 적습니다 -->
- `file.py`:
- `tests/test_file.py`:

## Testing
<!-- 어떻게 테스트했나요? -->
```bash
pytest tests/ -v
```

## Checklist
- [ ] 테스트 추가 또는 기존 테스트 통과
- [ ] 문서 업데이트 (해당되는 경우)
- [ ] 커밋 메시지가 Conventional Commits 형식을 따름
- [ ] CI 통과 확인
- [ ] Breaking change 없음 (있다면 이유 설명)
```

## 코드 리뷰 대응 에티켓

리뷰를 받는 일도 협업 능력입니다.

### 좋은 리뷰 대응 vs 나쁜 리뷰 대응

**리뷰어 코멘트**: "34번 줄의 `dict.update()` 대신 `CookieJar.update()`를 사용하면 더 안전합니다."

```markdown
# 나쁜 대응
"왜요? dict.update()도 동작하는데요."

# 좋은 대응
"좋은 지적 감사합니다. CookieJar.update()를 사용하면
thread-safety가 보장되는군요. 수정했습니다.

다만 한 가지 확인할 것이 있습니다. Python 3.8에서
CookieJar.update()의 동작이 달라지는 경우가 있는데,
이 프로젝트가 지원하는 최소 Python 버전이 무엇인지
확인하고 싶습니다."
```

### 반대 의견을 표현할 때

```markdown
# 상황: 리뷰어가 복잡한 캐싱 레이어 추가를 제안했을 때

감사합니다. 제안하신 캐싱 접근 방식이 성능 측면에서
더 우수하다는 점에 동의합니다.

다만 이 이슈의 범위가 쿠키 버그 수정이라, 캐싱 추가는
별도 이슈에서 더 넓은 논의가 필요할 것 같습니다.

이 PR에서는 쿠키 버그만 수정하고,
캐싱 개선을 위한 #1300 이슈를 별도로 열겠습니다.
이렇게 진행해도 될까요?
```

## 브랜치 전략

프로젝트마다 브랜치 전략이 다릅니다. 기여 전에 확인합니다.

| 전략 | 특징 | 적합한 프로젝트 | 기여자 브랜치 |
|---|---|---|---|
| GitHub Flow | `main` + feature 브랜치 | 대부분의 오픈소스 | `fix/`, `feat/`, `docs/` |
| Git Flow | `develop`, `release`, `hotfix` | 버전 관리 중심 대형 프로젝트 | `feature/`, `fix/` |
| Trunk Based | `main` 직접, short-lived 브랜치 | CI/CD 고도화 팀 | 매우 짧은 브랜치 |

**GitHub Flow 기여 패턴** (대부분의 오픈소스):

```bash
# main에서 브랜치 생성
git checkout main
git pull upstream main
git checkout -b fix/1234-description

# 작업 후 PR 생성 → 리뷰 → main에 머지
```

## Draft PR 활용법

코드가 완성되지 않았지만 초기 방향에 대해 피드백을 받고 싶을 때 유용합니다.

```bash
# Draft PR 생성
gh pr create \
  --title "WIP: fix session cookie handling" \
  --body "작업 진행 중입니다. 접근 방향에 대한 피드백 부탁드립니다." \
  --draft

# 완성 후 Ready for Review로 전환
gh pr ready
```

Draft 상태에서는 리뷰어에게 알림이 가지 않습니다. "Ready for review"로 전환하면 그때부터 정식 리뷰가 시작됩니다.

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| main 브랜치에서 작업 | `git checkout main` 후 직접 수정 | 항상 새 브랜치 생성: `git checkout -b fix/description` |
| 모호한 커밋 메시지 | "fix bug", "update", "WIP" | Conventional Commits 형식 사용 |
| 테스트 없는 PR | 기능 변경 후 테스트 미추가 | 버그 수정 PR에 반드시 회귀 테스트 포함 |
| 이슈 연결 누락 | PR 본문에 관련 이슈 링크 없음 | `Closes #N` 형식으로 이슈 연결 |
| 리뷰 피드백 무시 | 코멘트에 응답 없이 새 커밋만 푸시 | 각 코멘트에 응답 후 변경 내용 설명 |

## 실무에서는 이렇게 생각한다

시니어 엔지니어는 풀 리퀘스트를 코드 제출이 아니라 협업 인터페이스로 봅니다. 코드가 맞아도 범위가 너무 크면 리뷰 속도가 떨어지고, 맥락이 비어 있으면 검토자가 방어적으로 변합니다. 그래서 작은 풀 리퀘스트, 분명한 설명, 빠른 피드백 반영이 중요합니다.

또 리뷰는 합격 시험이 아닙니다. 좋은 리뷰 대화는 둘 중 누가 옳으냐보다, 어떤 선택이 저장소의 기존 방향과 더 잘 맞느냐를 맞춰 가는 과정입니다.

**리뷰 대기 시간 활용법** — PR을 올린 뒤 리뷰를 기다리는 동안:

```bash
# 다른 good first issue 탐색
gh issue list --repo psf/requests --label "good first issue"

# 기존 오픈 PR에 리뷰 코멘트 달기 (커뮤니티 기여)
gh pr list --repo psf/requests --state open

# 관련 문서 업데이트 확인
gh api repos/psf/requests/contents/docs
```

## 운영 체크리스트

- [ ] 작업용 브랜치를 따로 만들었습니다.
- [ ] 커밋 메시지가 변경 의도를 설명합니다.
- [ ] 테스트 결과나 검증 방법을 준비했습니다.
- [ ] 풀 리퀘스트 설명에 관련 이슈와 맥락을 적었습니다.
- [ ] CI가 통과했는지 확인했습니다.

## 연습 문제

1. fork와 clone의 차이를 한 문장으로 적어 보세요.
2. `Closes #N` 표현이 하는 일을 한 문장으로 적어 보세요.
3. 작은 풀 리퀘스트가 유리한 이유를 한 문장으로 적어 보세요.

## 정리

이번 글에서는 풀 리퀘스트를 단순 업로드가 아니라, 검토 가능한 변경 제안으로 보는 관점을 정리했습니다. 좋은 풀 리퀘스트는 기능보다 협업 비용을 줄이는 구조에서 시작합니다.

다음 글에서는 리드미 문서를 다룹니다. 기여를 받는 저장소라면 코드만큼 중요한 것이 첫 방문자가 길을 잃지 않게 만드는 문서이기 때문입니다.

## 처음 질문으로 돌아가기

- **메인테이너가 반기는 풀 리퀘스트는 어떤 모양일까요?**
  - 변경 범위가 하나의 목적으로 제한되고, 커밋 메시지가 이유를 설명하며, 테스트가 포함되어 있고, PR 본문에 관련 이슈와 검증 방법이 명시된 PR입니다. 메인테이너가 코드를 열기 전에 이미 맥락을 파악할 수 있는 PR이 가장 좋습니다.
- **포크, 브랜치, 커밋, 풀 리퀘스트 흐름을 왜 매번 분리해야 할까요?**
  - 포크는 원본 저장소를 보호하는 개인 작업 공간이고, 브랜치는 변경을 목적별로 격리하며, 커밋은 이력을 원자 단위로 남기고, PR은 그 결과를 검토 가능한 형태로 제안합니다. 이 네 단계를 섞으면 실수를 되돌리기 어렵고 리뷰가 복잡해집니다.
- **커밋 메시지와 풀 리퀘스트 설명은 각각 어떤 역할을 할까요?**
  - 커밋 메시지는 개별 변경의 이유를 기록하는 영구적 이력입니다. `git log`에서 항상 보입니다. PR 설명은 이 변경들을 하나의 맥락으로 묶어 리뷰어에게 전달하는 임시 문서입니다. 커밋은 "무엇을 왜 바꿨나", PR은 "전체적으로 어떤 문제를 어떻게 해결했나"를 담당합니다.

<!-- toc:end -->

## 참고 자료

- [GitHub PR docs](https://docs.github.com/en/pull-requests)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to write a Git commit message](https://cbea.ms/git-commit/)
- [gh CLI](https://cli.github.com/manual/gh_pr_create)
- [GitHub pull request templates 예시](https://github.com/github/docs/tree/main/.github)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, PullRequest, Git, GitHub, Beginner
