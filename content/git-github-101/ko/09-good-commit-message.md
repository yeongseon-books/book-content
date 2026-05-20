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

## 먼저 던지는 질문

- 좋은 commit message는 왜 코드만큼 중요한 자산일까요?
- subject, body, footer는 각각 무엇을 담아야 할까요?
- Conventional Commits의 `feat`, `fix`, `docs` 같은 type은 무엇을 해결할까요?

## 큰 그림

![Git & GitHub 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/09/09-01-mental-model.ko.png)

*Git & GitHub 101 9장 흐름 개요*

이 그림에서는 좋은 commit message 쓰기: Conventional Commits와 좋은 본문를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 좋은 commit message 쓰기: Conventional Commits와 좋은 본문의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## 처음 질문으로 돌아가기

- **좋은 commit message는 왜 코드만큼 중요한 자산일까요?**
  - 본문의 기준은 좋은 commit message 쓰기: Conventional Commits와 좋은 본문를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **subject, body, footer는 각각 무엇을 담아야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Conventional Commits의 `feat`, `fix`, `docs` 같은 type은 무엇을 해결할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
Tags: git-commit-message, conventional-commits, commit-style, imperative-mood, git-amend, code-blame
