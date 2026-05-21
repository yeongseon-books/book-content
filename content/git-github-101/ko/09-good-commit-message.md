---
episode: 9
language: ko
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- git-commit-message
- conventional-commits
- commit-style
- imperative-mood
- git-amend
- code-blame
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Git & GitHub 101 (9/10): 좋은 commit message 쓰기: Conventional Commits와 좋은 본문"
seo_description: 좋은 commit message 구조와 Conventional Commits 실무 규칙을 설명합니다.
---

# Git & GitHub 101 (9/10): 좋은 commit message 쓰기: Conventional Commits와 좋은 본문

코드만으로는 왜 이런 변경이 들어왔는지 설명되지 않는 순간이 반드시 옵니다. 그때 commit message가 좋으면 history 자체가 문서가 되고, 나쁘면 원래 PR과 diff를 끝까지 다시 읽어야 합니다.

이 글은 Git/GitHub 101 시리즈의 아홉 번째 글입니다. 여기서는 subject, body, footer 구조와 Conventional Commits, 그리고 message 품질을 지키는 습관을 정리합니다.


![Git & GitHub 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/09/09-01-mental-model.ko.png)
*Git & GitHub 101 9장 흐름 개요*

## 먼저 던지는 질문

- 좋은 commit message는 왜 코드만큼 중요한 자산일까요?
- subject, body, footer는 각각 무엇을 담아야 할까요?
- Conventional Commits의 `feat`, `fix`, `docs` 같은 type은 무엇을 해결할까요?

## 왜 중요한가

`git log`는 미래의 자신과 동료에게 보내는 편지입니다. `git blame`으로 특정 줄에 도달했을 때 message가 선명하면 5초 만에 맥락이 살아나고, `fix`, `update`, `wip` 같은 제목만 있으면 원래 diff와 PR을 다시 읽어야 합니다.

좋은 message는 자동화에도 쓰입니다. Conventional Commits를 따르면 release note 생성기나 버전 정책이 commit type을 기계적으로 읽을 수 있습니다. PR 설명이 짧더라도 commit 단위로 author의 의도를 따라갈 수 있어 리뷰 품질도 좋아집니다.

## 핵심 그림

여기서 먼저 볼 것은 세 가지입니다.

- subject는 짧고 명령형으로 씁니다.
- body는 빈 줄 뒤에 두고 "왜"를 설명합니다.
- footer에는 issue 번호나 breaking change 같은 메타데이터를 둡니다.

## 핵심 개념

| 개념 | 설명 |
| --- | --- |
| Subject | 첫 줄, 50자 이하, 마침표 없이, 명령형 |
| Body | 빈 줄 뒤 본문, 72자 줄바꿈 권장 |
| Footer | `Refs: #42`, `Closes #42`, `BREAKING CHANGE: ...` 같은 메타데이터 |
| Type | `feat`, `fix`, `docs`, `refactor`, `test`, `chore` 등 변경 종류 |
| Scope | `feat(auth): ...`처럼 영역을 괄호로 좁히는 선택적 정보 |
| Imperative mood | `Add`, `Fix`, `Refactor`처럼 적용 명령처럼 읽히는 동사 |
| Atomic commit | 하나의 논리적 변경만 담은 commit |

Conventional Commits를 실제 팀에서 쓰려면 "형식"보다 "의미 매핑"을 먼저 고정해야 합니다. 예를 들어 어떤 팀은 UI 텍스트 수정을 `docs`로, 어떤 팀은 사용자 동작이 바뀌면 `feat`로 분류합니다. 규칙이 문서에 없다면 같은 변경도 사람마다 `fix`, `refactor`, `chore`로 갈라져 log 일관성이 깨집니다.

아래는 실무에서 자주 쓰는 type 해석 기준입니다.

| Type | 언제 쓰는가 | 포함/제외 판단 |
| --- | --- | --- |
| `feat` | 사용자 관점에서 기능이 늘어날 때 | API, UI, CLI 동작이 실제로 확장됨 |
| `fix` | 기대 동작과 실제 동작의 차이를 바로잡을 때 | 버그 수정, 회귀 수정, 예외 케이스 보완 |
| `docs` | 문서만 바뀔 때 | 코드 동작 변화 없음 |
| `refactor` | 동작은 유지하고 내부 구조만 개선할 때 | 함수 분리, 이름 개선, 중복 제거 |
| `test` | 테스트 코드 추가/수정 중심일 때 | 프로덕션 코드 변경이 최소 또는 없음 |
| `chore` | 빌드/도구/메타 작업일 때 | 패키지 버전, 스크립트, 설정 정리 |
| `perf` | 기능은 같고 성능 특성만 개선할 때 | 지연 시간/메모리/처리량 개선 |
| `build` | 빌드 시스템/의존성 빌드 과정 변경 | webpack, Gradle, Poetry lock 등 |
| `ci` | CI 파이프라인 동작 변경 | GitHub Actions, Jenkins, lint job |
| `style` | 포맷/세미콜론/공백 등 비동작 변경 | lint autofix, formatting only |

`scope`는 작을수록 좋습니다. `auth`, `checkout`, `docs`, `api`처럼 저장소에서 반복되는 도메인 경계를 쓰면, `git log --oneline`만 봐도 어느 영역이 자주 흔들리는지 보입니다. 반대로 `scope`를 매번 임의 문자열로 쓰면 오히려 검색성과 집계 품질이 떨어집니다.

## Conventional Commits 사양을 실무 언어로 해석하기

Conventional Commits 1.0.0은 복잡한 문법이 아니라 세 줄 규칙으로 요약할 수 있습니다.

1. 첫 줄은 `type(scope)!: subject` 형식입니다. `scope`와 `!`는 선택입니다.
2. 본문(body)은 선택이지만, 넣는다면 빈 줄 뒤에 "왜"를 설명합니다.
3. 꼬리말(footer)은 메타데이터 영역이며 `BREAKING CHANGE:` 같은 키워드를 둡니다.

아래 예시는 사양을 그대로 따르는 형태입니다.

```text
feat(auth): support passwordless login

Add email link based login so users can sign in without memorizing
passwords. This reduces login failure rates on mobile devices.

Closes: #128
```

파괴적 변경은 두 가지 방식 중 하나로 표시합니다.

```text
feat(api)!: remove v1 session endpoint

BREAKING CHANGE: /v1/session has been removed. Use /v2/session instead.
```

혹은 subject에는 `!`를 빼고 footer의 `BREAKING CHANGE:`만 사용해도 됩니다. 중요한 점은 팀이 둘 중 하나를 표준으로 정해 일관되게 쓰는 것입니다.

## Subject, Body, Footer를 더 정확히 쓰는 기준

subject는 "이 commit이 브랜치에 적용될 때 일어나는 변화"를 한 줄로 적는 영역입니다. 그래서 명령형이 잘 맞습니다.

- 좋은 subject: `fix(auth): reject expired refresh tokens`
- 모호한 subject: `fixed tokens`, `token issue`, `update`

body는 diff를 번역하는 칸이 아니라 의사결정을 기록하는 칸입니다. 아래 기준을 권장합니다.

1. **왜 바꿨는지**: 버그 원인, 사용자 영향, 운영 리스크
2. **어떤 선택을 했는지**: 대안 중 무엇을 택했는지
3. **어떤 범위를 의도했는지**: 이번 commit에 포함/제외한 범위

footer는 참조를 정리하는 칸입니다. 대표 키는 다음과 같습니다.

- `Refs: #42` - 참고 이슈 연결
- `Closes: #42` - merge 시 이슈 자동 종료 의도
- `Co-authored-by: Name <mail@example.com>` - 공동 작성자 기록
- `BREAKING CHANGE: ...` - 하위 호환성 깨짐 알림

subject에 이슈 번호, 팀 내부 티켓, 긴 URL을 밀어 넣으면 한 줄 가독성이 바로 무너집니다. 메타정보는 footer에 분리하는 습관이 중요합니다.

## 전후 비교

메시지가 흐릿하면 log도 흐릿합니다.

```text
$ git log --oneline -5
9f8e7d6 fix
8e7d6c5 update
7d6c5b4 wip
6c5b4a3 stuff
5b4a3f2 final
```

Conventional Commits와 짧은 body를 쓰면 같은 작업도 맥락이 남습니다.

```text
$ git log --oneline -5
9f8e7d6 fix(auth): handle expired refresh tokens
8e7d6c5 feat(auth): add OAuth login button
7d6c5b4 refactor(auth): extract token validation helper
6c5b4a3 test(auth): cover login redirect cases
5b4a3f2 docs(auth): document OAuth setup steps
```

실무에서는 여기에 branch 단위 요약까지 붙여 읽는 경우가 많습니다.

```bash
$ git log --oneline --decorate --graph -10
```

이 명령을 주간 회고나 릴리스 점검에서 열어 보면, message 품질이 낮은 팀은 "무엇이 배포됐는지"를 다시 PR 단위로 역추적해야 합니다. 반대로 subject가 정돈된 팀은 log 자체가 변경 목록 역할을 해 회의 시간이 줄어듭니다.

## 좋은/나쁜 message 비교

같은 변경도 문장에 따라 운영 난이도가 달라집니다.

| 상황 | 나쁜 message | 좋은 message |
| --- | --- | --- |
| 로그인 실패 버그 수정 | `fix` | `fix(auth): handle null redirect_uri in OAuth callback` |
| 문서 오탈자 수정 | `update readme` | `docs(readme): fix typo in local setup command` |
| 성능 개선 | `refactor query` | `perf(search): add index hint for tag filter query` |
| 테스트만 보강 | `more tests` | `test(auth): add regression test for expired token reuse` |
| 파괴적 API 변경 | `change api` | `feat(api)!: rename /v1/orders to /v2/orders` |

좋은 message의 공통점은 화려한 문장이 아니라 "판단에 필요한 최소 맥락"이 있다는 점입니다. 어떤 컴포넌트인지(scope), 무슨 종류 변경인지(type), 무엇이 바뀌는지(subject)가 1초 안에 읽혀야 합니다.

## commit 단위를 자르는 기준

좋은 message는 좋은 commit 단위와 같이 움직입니다. 변경 단위가 거칠면 message를 아무리 잘 써도 정확해질 수 없습니다.

다음 기준으로 커밋 쪼개기를 권장합니다.

1. **하나의 이유(one reason to change)**만 담습니다.
2. **리뷰 가능한 크기**를 유지합니다. 보통 파일 수보다 논리적 일관성이 중요합니다.
3. **되돌리기 가능성**을 고려합니다. 특정 commit만 되돌렸을 때도 저장소가 컴파일/테스트 가능한 상태가 좋아집니다.
4. **기계적 변경과 의미 변경 분리**를 지킵니다. 포맷팅과 로직 수정을 같은 commit에 섞지 않습니다.

예를 들어 인증 모듈 리팩터링을 한다면 아래처럼 쪼개는 편이 좋습니다.

- `refactor(auth): extract token parser into dedicated module`
- `test(auth): add parser edge-case coverage`
- `fix(auth): reject malformed bearer token prefix`

반대로 아래처럼 한 번에 묶으면, 제목 한 줄로 실제 diff 의도를 설명하기 어려워집니다.

- `update auth`

commit granularity는 협업 속도를 좌우합니다. 리뷰어가 "이 commit은 무슨 의도인지"를 매번 질문하기 시작하면, PR 왕복 횟수가 급격히 늘어납니다.

## 단계별 실습

### 1. 다듬기 전 commit 하나 만들기

```bash
$ git switch -c chore/readme-typo
Switched to a new branch 'chore/readme-typo'
$ printf '\nThanks for reading.\n' >> README.md
$ git add README.md
$ git commit -m "fix"
[chore/readme-typo c4d5e6f] fix
 1 file changed, 2 insertions(+)
```

### 2. `--amend`로 message 다시 쓰기

```bash
$ git commit --amend -m "docs(readme): add closing thank-you note"
[chore/readme-typo a8b7c6d] docs(readme): add closing thank-you note
 Date: Mon May 4 10:21:40 2026 +0900
 1 file changed, 2 insertions(+)
$ git log -1 --pretty=full
commit a8b7c6d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8
Author: You <you@example.com>
Commit: You <you@example.com>

    docs(readme): add closing thank-you note
```

hash가 바뀌므로 이미 push한 commit에는 신중해야 합니다.

### 3. body가 필요하면 editor 열기

```bash
$ git commit
```

```text
feat(packing): add weather-aware section

Summary: extend the packing list section so recommended items shift
based on the weather forecast for the trip date.

Items used to be static, so users departing during the rainy season
got the same checklist as everyone else. The external weather API
call is wrapped in a cache layer to keep response time under 50ms.

Refs: #2
```

첫 줄이 subject, 그 아래가 body, 마지막이 footer입니다.

### 4. 여러 message를 `rebase -i`로 다듬기

```bash
$ git rebase -i HEAD~3
```

```text
pick a8b7c6d docs(readme): add closing thank-you note
pick b9c8d7e fix
pick c0d1e2f wip

# Rebase ...
# Commands:
# p, pick   = use commit
# r, reword = use commit, but edit the commit message
# ...
```

`pick`을 `reword`로 바꾸면 그 commit의 message를 다시 쓸 수 있습니다.

실전에서는 `reword`만 쓰는 경우도 많지만, 메시지 품질을 높일 때 함께 자주 쓰는 명령이 있습니다.

- `squash`: 바로 앞 commit과 합치고 두 메시지를 함께 편집합니다.
- `fixup`: 바로 앞 commit과 합치되 현재 메시지는 버립니다.
- `drop`: 불필요한 commit을 제거합니다.

예를 들어 아래처럼 `wip` 두 개가 섞여 있으면:

```text
pick 11aa22b wip
pick 33cc44d wip
pick 55ee66f fix(auth): reject expired refresh token
```

다음처럼 정리할 수 있습니다.

```text
reword 11aa22b feat(auth): add token refresh path
fixup 33cc44d wip
pick   55ee66f fix(auth): reject expired refresh token
```

이 과정을 거치면 `git log --oneline`이 "작업 흔적"이 아니라 "의도 기록"으로 바뀝니다. 단, 이미 공유된 branch라면 rebase로 인한 hash 변경이 동료 작업과 충돌할 수 있으므로 팀 규칙을 먼저 확인해야 합니다.

### 5. `commit-msg` hook으로 형식 강제하기

```bash
$ cat .git/hooks/commit-msg
#!/bin/sh
pattern='^(feat|fix|docs|refactor|test|chore|perf|build|ci|style)(\([a-z0-9-]+\))?: .{1,50}$'
head -n1 "$1" | grep -Eq "$pattern" || {
  echo "Subject does not match the Conventional Commits format." >&2
  exit 1
}
$ chmod +x .git/hooks/commit-msg
```

## push 전에 message를 검증하는 순서

좋은 message 규칙을 알아도 실제로는 commit 직후 한 번 더 읽지 않으면 subject가 너무 길거나, body가 diff를 그대로 반복하거나, footer가 빠진 채 push되는 일이 자주 생깁니다. 가장 실용적인 방법은 push 전에 짧은 검증 순서를 고정하는 것입니다.

```bash
$ git log -1 --pretty=fuller
$ git show --stat --summary --format=fuller HEAD
```

이 두 명령으로 다음을 확인합니다.

1. **subject만 읽어도 변경 의도가 드러나는가**
2. **body가 있다면 왜를 설명하는가**
3. **issue 번호나 breaking change가 footer에 분리돼 있는가**
4. **diff 범위와 subject가 서로 어긋나지 않는가**

예를 들어 README 오탈자 하나를 고쳤는데 subject가 `refactor(readme): improve docs architecture`처럼 과하면 log를 읽는 사람이 실제 변경을 과대평가하게 됩니다. 반대로 인증 흐름 수정인데 `fix` 한 단어로 끝나면 의도가 사라집니다.

## amend와 rebase를 고르기 전 판단 기준

message를 고칠 때는 명령보다 먼저 **이 commit이 이미 공유됐는가**를 따져야 합니다.

- **아직 push하지 않았다면** `git commit --amend`와 `git rebase -i`로 자유롭게 다듬어도 됩니다.
- **이미 push했고 다른 사람이 가져갔다면** message를 예쁘게 고치기 위해 history를 다시 쓰지 않는 편이 안전합니다.
- **PR 리뷰 중이고 내 개인 branch만 쓰는 상황**이라면 `--force-with-lease`를 전제로 amend/rebase가 가능합니다.

이 기준이 중요한 이유는 message 품질보다 협업 안정성이 더 우선인 순간이 있기 때문입니다. history 정리는 branch 경계 안에서 하고, 공유된 `main` 이력은 새 commit으로 보정하는 편이 사고를 줄입니다.

## hook이 commit을 막을 때 읽는 법

형식 검증을 붙이면 처음에는 "왜 commit이 안 되지?"라는 순간이 꼭 옵니다. 이때는 에러를 한 줄씩 읽으면 됩니다.

```text
Subject does not match the Conventional Commits format.
```

이 메시지가 나오면 보통 세 가지를 먼저 확인합니다.

- type이 `feat`, `fix`, `docs` 같은 허용 목록 안에 있는가
- `type(scope): subject` 뒤의 공백과 콜론 위치가 맞는가
- 첫 줄이 너무 길거나 마침표로 끝나지 않았는가

형식 검증의 목적은 작성자를 괴롭히는 것이 아니라, `main`의 log를 한 번 더 읽기 쉽게 유지하는 것입니다. 그래서 hook이 막았을 때는 우회보다 수정이 기본값이어야 합니다.

## 자주 하는 실수

- 서로 다른 두 변경을 한 commit에 섞습니다.
- subject가 길고 마침표까지 붙어 `git log --oneline`에서 잘립니다.
- diff에 이미 있는 사실만 반복하고 왜 바꿨는지는 쓰지 않습니다.
- 이미 push한 commit을 `--amend`로 고친 뒤 force push 문제를 만듭니다.
- 이슈 번호나 메일 주소 같은 메타데이터를 subject에 넣어 한 줄 요약을 지저분하게 만듭니다.

## 실무에서는 이렇게 본다

팀은 보통 commit message 규칙을 README나 CONTRIBUTING 문서에 적어 둡니다. subject 길이, 명령형 사용, body의 역할, footer 메타데이터, force push 제한 같은 규칙이 대표적입니다. 그리고 사람의 기억만 믿지 않고 `commit-msg` hook과 CI의 lint 단계로 형식을 강제합니다.

특히 squash merge를 쓰는 팀에서는 PR 제목이 그대로 `main`의 commit message가 되므로, PR 제목도 같은 형식으로 맞추는 편이 유리합니다.

또한 commit message 검증은 log를 위한 일일 뿐 아니라 release note 품질을 위한 일이기도 합니다. `feat`, `fix`, `docs`가 꾸준히 맞아 떨어지면 changelog 초안, 배포 공지, 회귀 분석이 모두 쉬워집니다. 결국 좋은 message는 "나중에 덜 고생하기 위한 선불 비용"에 가깝습니다.

운영 조직에서는 type을 기반으로 배포 리스크를 빠르게 스캔합니다. 예를 들어 릴리스 직전 `git log --oneline`에서 `feat!`나 `BREAKING CHANGE`가 보이면, 문서/마이그레이션 공지를 같이 확인합니다. 반대로 대부분이 `docs`, `test`, `chore`라면 사용자 영향이 낮은 배포로 분류할 수 있습니다. message 규칙이 곧 배포 커뮤니케이션 비용을 줄이는 이유가 여기 있습니다.

## 체크리스트

- [ ] subject가 50자 이하, 명령형, 마침표 없음 규칙을 따릅니까?
- [ ] type이 Conventional Commits 분류 중 하나입니까?
- [ ] body가 있다면 빈 줄 뒤에 있고 "왜"를 설명합니까?
- [ ] footer에 issue 번호나 breaking change 정보를 넣었습니까?
- [ ] hook 또는 CI lint로 형식을 자동 검증합니까?
- [ ] push 전에 `--amend`로 한 번 더 다듬을 수 있는지 확인했습니까?

## 연습 문제

1. 최근 저장소의 `git log --oneline -20`을 보고 애매한 message 3개를 더 좋은 문장으로 바꿔 보세요.
2. `git commit --amend -m "..."`으로 최신 commit message를 다시 쓰고 hash가 바뀌는지 확인해 보세요.
3. 새 branch에서 작은 commit 세 개를 만든 뒤 `git rebase -i HEAD~3`으로 두 번째 message를 `reword`해 보세요.
4. 위 `commit-msg` hook을 샘플 저장소에 넣고 형식이 어긋난 commit이 거부되는지 확인해 보세요.

## 정리와 다음 글

좋은 commit message는 코드만 다시 읽지 않고도 변경 의도를 이해하게 해 주는 가장 값싼 문서입니다. subject, body, footer 구조와 Conventional Commits type을 익히면 `git log` 자체가 읽기 좋은 변경 이력이 됩니다. 아직 push하지 않은 commit은 `--amend`와 `rebase -i`로 다듬고, 형식은 hook과 CI로 강제하는 편이 안전합니다.

다음 글에서는 지금까지 배운 도구를 하나의 실전 워크플로로 묶어 issue부터 release tag까지 한 흐름으로 연결해 보겠습니다.


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

- **좋은 commit message는 왜 코드만큼 중요한 자산일까요?**
  - 좋은 message는 `git log`, `git blame`, release note에서 동일한 맥락을 재사용하게 만들어 줍니다. 즉, diff를 다시 열어 보기 전에 의도를 먼저 읽을 수 있어 협업 비용을 줄입니다.
- **subject, body, footer는 각각 무엇을 담아야 할까요?**
  - subject는 한 줄 요약, body는 왜와 선택 근거, footer는 이슈/파괴적 변경 같은 메타데이터를 담습니다. 이 분리가 지켜질수록 log 가독성이 높아집니다.
- **Conventional Commits의 `feat`, `fix`, `docs` 같은 type은 무엇을 해결할까요?**
  - type은 변경의 종류를 사람이 일관되게 읽고, 도구가 자동으로 분류하게 만드는 공통 언어입니다. 결과적으로 changelog 생성, 릴리스 위험 판단, 회귀 추적이 쉬워집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- [Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기](./05-merge-and-conflict.md)
- [Git & GitHub 101 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기](./06-github-repository.md)
- [Git & GitHub 101 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지](./07-pull-request.md)
- [Git & GitHub 101 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법](./08-issue-and-project.md)
- **좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (현재 글)**
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [Conventional Commits — Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — `type(scope): subject`와 body/footer 구조, SemVer 연결 규칙의 원문 사양입니다.
- [Tim Pope — A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) — 50자 subject, 72자 줄바꿈, 명령형 문체 같은 실무 규칙의 고전적인 기준입니다.
- [git-commit manual](https://git-scm.com/docs/git-commit) — 메시지 작성, `--amend`, editor 기반 입력 흐름을 공식 문법으로 확인할 수 있습니다.
- [git-rebase manual](https://git-scm.com/docs/git-rebase) — `rebase -i`와 `reword`로 이전 commit message를 다듬는 단계와 연결됩니다.
- [githooks manual — commit-msg](https://git-scm.com/docs/githooks#_commit_msg) — `commit-msg` hook으로 메시지 형식을 강제하는 방법의 기준 문서입니다.
- [GitHub Docs — About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github) — squash merge 시 PR 제목이 기본 branch history에 어떤 형태로 남는지 이해하는 데 도움이 됩니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/09-good-commit-message)

Tags: git-commit-message, conventional-commits, commit-style, imperative-mood, git-amend, code-blame
