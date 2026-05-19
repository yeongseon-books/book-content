---
episode: 8
language: ko
last_reviewed: '2026-05-15'
series: git-github-101
status: publish-ready
tags:
- github-issue
- github-project
- issue-tracking
- kanban-board
- issue-pr-linking
- closes-keyword
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
seo_description: GitHub Issue와 Project로 일감 흐름을 추적하는 방법을 설명합니다.
---

# Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법

코드 이력은 무엇이 바뀌었는지를 잘 보여 주지만, 팀은 그보다 앞선 질문도 자주 다룹니다. 지금 무엇을 해야 하는지, 누가 맡고 있는지, 어디까지 왔는지를 저장소 안에서 함께 볼 수 있어야 일이 덜 흩어집니다.

이 글은 Git/GitHub 101 시리즈의 여덟 번째 글입니다. 여기서는 Issue, Pull Request, Project board를 하나의 작업 추적 흐름으로 연결해 봅니다.

## 이 글에서 다룰 문제

> Issue는 무엇을 할지 기록하고, PR은 그 일을 실제로 어떻게 끝냈는지 기록하며, Project는 그 일이 지금 어느 상태에 있는지 보여 줍니다.

- GitHub Issue는 commit이나 PR과 어떻게 다를까요?
- label, assignee, milestone은 언제 유용할까요?
- PR 본문의 `Closes #42`는 왜 중요한 자동화일까요?
- Project board는 issue와 PR을 어떤 식으로 한 화면에 모을까요?
- 혼자 쓰는 저장소에서도 issue가 왜 쓸모가 있을까요?

## 왜 중요한가

지금까지의 시리즈는 코드 변경 자체를 기록하는 법에 집중했습니다. 하지만 실무에서는 그보다 먼저 "무엇을 해야 하지?"라는 질문이 더 자주 나옵니다. Issue와 Project는 이 질문을 코드 저장소 바로 옆에서 다루게 해 줍니다.

할 일과 진행 상황을 GitHub 안에 두면 작업의 시작과 끝이 선명해집니다. issue를 열고, PR로 작업을 마치고, merge와 함께 issue를 닫으며, board에서는 상태가 카드로 보입니다. 몇 달 뒤 변경 이유를 되짚을 때도 commit → PR → issue 순서로 의도를 다시 찾을 수 있습니다.

## 핵심 그림

![Mental Model](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/08/08-01-mental-model.ko.png)

*Mental Model*

흐름은 다음과 같습니다.

1. issue가 작업의 출발점입니다.
2. 그 issue를 처리할 branch와 PR이 생깁니다.
3. PR 본문에 `Closes #N`을 쓰면 merge 시 issue가 자동으로 닫힙니다.
4. Project board는 issue와 PR을 카드로 묶어 현재 상태를 보여 줍니다.

## 핵심 개념

| 용어 | 뜻 |
| --- | --- |
| Issue | 제목, 본문, 댓글, label, assignee, milestone을 가진 저장소 단위 할 일 카드 |
| Label | `bug`, `enhancement` 같은 분류 태그 |
| Milestone | 여러 issue와 PR을 묶는 일정 단위 |
| Assignee | 담당자 |
| Project | issue와 PR을 상태별 카드로 관리하는 보드 |
| Closing keywords | `Closes`, `Fixes`, `Resolves` 같은 자동 닫기 키워드 |
| Reference | `#42`처럼 issue/PR을 가리키는 링크 표기 |

## 전후 비교

issue 없이 merge된 PR은 변경 이유가 빠르게 사라집니다.

```text
PR #5: Fix sidebar overflow
- (empty body)
- merged

# 3 months later
$ git log --oneline | grep sidebar
9d8e7f6 Fix sidebar overflow
$ # nobody remembers why this needed fixing
```

issue와 PR이 연결되어 있으면 상황이 달라집니다.

```text
Issue #42: Sidebar text overflows on narrow screens
- Text is cut off below 1024px
- Reports note that mouse interactions are blocked

PR #5: Fix sidebar overflow on narrow screens
Body: Closes #42
- Add 16px left padding, set max-width to 240px
- Verified scroll behavior between 320px and 1280px
```

## 단계별 실습

### 1. 첫 issue 만들기

- Title: `Add a packing list section to notes`
- Description 예시:

```text
## Background
notes.md has nowhere to keep packing items for a trip.

## Goal
Add a `## Packing list` section with three default items.
Detailed structure can be handled in follow-up PRs.

## Out of scope
- Inline images
- i18n
```

새 issue 번호를 `#2`라고 가정합니다.

### 2. label과 assignee 붙이기

- Labels: `enhancement`
- Assignees: 본인
- Milestone: 필요하면 이후에 지정

이 세 정보만으로도 작업 분류, 담당자, 일정 묶음이 분명해집니다.

### 3. issue용 branch 만들기

```text
$ git switch main
Already on 'main'
Your branch is up to date with 'origin/main'.
$ git pull
Already up to date.
$ git switch -c feature/packing-list-2
Switched to a new branch 'feature/packing-list-2'
```

branch 이름에 issue 번호를 넣어 두면 나중 추적이 쉬워집니다.

### 4. 변경을 commit하고 push하기

```text
$ printf '\n## Packing list\n\n- Passport\n- Phone charger\n- Travel adapter\n' >> notes.md
$ git add notes.md
$ git commit -m "Add packing list section"
[feature/packing-list-2 a1b2c3d] Add packing list section
 1 file changed, 5 insertions(+)
$ git push -u origin feature/packing-list-2
Enumerating objects: 5, done.
...
remote: Create a pull request for 'feature/packing-list-2' on GitHub by visiting:
remote:      https://github.com/<your-id>/vacation-notes/pull/new/feature/packing-list-2
To https://github.com/<your-id>/vacation-notes.git
 * [new branch]      feature/packing-list-2 -> feature/packing-list-2
Branch 'feature/packing-list-2' set up to track remote branch 'feature/packing-list-2' from 'origin'.
```

### 5. PR을 issue와 연결해 열기

```text
Title: Add packing list section to notes
Body:
Closes #2

Adds a place to write packing items before a trip.
Only the default items are included so follow-up PRs can refine the structure.
```

`Closes #2`가 오른쪽 Development 섹션에 issue를 연결합니다.

### 6. merge와 함께 issue 닫기

PR을 merge하면 세 가지가 동시에 일어납니다.

1. PR commit이 `main`에 반영됩니다.
2. issue `#2`가 `Closed`로 바뀝니다.
3. issue 화면에 PR을 통해 닫혔다는 기록이 남습니다.

### 7. Project board에서 보기

Projects 탭에서 Board 템플릿을 만들어 `Todo`, `In Progress`, `Done` 흐름을 씁니다.

- issue `#2`를 카드로 올립니다.
- 작업 시작 시 `In Progress`로 옮깁니다.
- PR도 같은 보드에 추가합니다.
- 자동화가 있다면 issue가 닫힐 때 `Done`으로 이동시킵니다.

## 상태 전환 기준을 먼저 정해 두기

Issue와 Project를 도입했는데도 보드가 금방 흐려지는 팀은 대개 column 이름만 있고 이동 기준이 없습니다. 예를 들어 `In Progress`가 “branch를 만든 상태”인지, “PR을 열고 리뷰 대기 중인 상태”인지가 사람마다 다르면 카드를 보고도 실제 진행률을 읽을 수 없습니다.

아래처럼 상태 전환 기준을 먼저 정해 두면 Project가 단순한 장식이 아니라 운영 화면이 됩니다.

![상태 전환 기준을 먼저 정해 두기](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/08/08-01-define-status-transitions-before-the-boa.ko.png)

*Issue · PR · Project 카드가 어떤 기준으로 다음 상태로 넘어가는지 보여 주는 흐름도*

이 기준을 문서화해 두면 issue를 열 때 필요한 정보와 PR을 merge해도 되는 시점이 함께 선명해집니다.

## 자동 닫기가 기대대로 동작하지 않을 때

실무에서 가장 자주 헷갈리는 부분은 `Closes #N`을 썼는데도 issue가 안 닫히는 경우입니다. 이때는 순서를 정해 확인하는 편이 빠릅니다.

1. **PR이 기본 branch로 merge됐는지** 봅니다. 기본적으로 closing keyword는 default branch에 들어갈 때 동작합니다.
2. **PR 본문에 keyword가 있었는지** 다시 봅니다. commit message에만 넣어 두면 squash/rebase 과정에서 기대와 다르게 보일 수 있습니다.
3. **번호가 정확한지** 확인합니다. 저장소가 다르면 `owner/repo#42`처럼 명시해야 합니다.
4. **한 PR에서 여러 issue를 닫을 때**는 `Closes #2, closes #3`처럼 issue마다 keyword를 반복합니다.
5. **이미 닫힌 issue인지** 확인합니다. 닫힌 issue는 다시 닫히지 않습니다.

이 다섯 가지를 먼저 보면 “GitHub 자동화가 이상하다”는 막연한 느낌보다 훨씬 빠르게 원인을 좁힐 수 있습니다.

## merge 전에 보는 검증 루틴

Issue와 Project는 코드가 아니라 흐름을 검증하는 도구이므로, merge 직전에는 다음처럼 연결 상태를 확인하는 편이 좋습니다.

- issue 본문에 **Background**와 **Goal**이 실제로 적혀 있는가
- label과 assignee가 최소 한 개 이상 붙어 있는가
- branch 이름과 PR 본문에서 같은 issue 번호를 가리키는가
- PR 본문에 `Closes #N`과 검증 방법이 함께 적혀 있는가
- Project 카드가 `In Review`인지, 아직 `Todo`에 남아 있지는 않은가
- merge 후 issue가 `Closed`, Project 카드가 `Done`으로 옮겨졌는가

이 루틴은 화려하지 않지만, 몇 달 뒤 "왜 이 일이 끝난 것으로 처리됐지?"라는 질문에 가장 강한 방어선이 됩니다.

## 자주 하는 실수

- issue를 만들었지만 PR 본문에 `Closes #N`을 적지 않아 자동 닫기를 놓칩니다.
- issue 본문이 제목 반복 수준이라 몇 달 뒤 맥락을 복원하기 어렵습니다.
- label을 너무 많이 만들어 분류 체계가 오히려 복잡해지기도 합니다.
- commit message에만 닫기 키워드를 넣고 PR 본문은 비워 두는 경우도 안전하지 않습니다.
- 혼자 쓰는 저장소라며 issue를 생략하면 나중에 할 일의 맥락을 잃기 쉽습니다.

## 실무에서는 이렇게 본다

issue 템플릿, milestone, `good first issue`, Project 자동화는 팀 규모가 커질수록 더 유용해집니다. 하지만 핵심은 거창한 자동화보다도, 할 일을 issue로 열고 PR과 연결해 닫는 기본 루프를 습관으로 만드는 것입니다.

특히 Project는 모든 걸 다 담으려 할수록 무거워집니다. 처음에는 `Todo`, `In Progress`, `In Review`, `Done` 네 칸만 두고, 카드 이동 기준부터 팀이 합의하는 편이 낫습니다. 보드가 실제 상태와 자주 어긋나면 새 column보다 먼저 전환 규칙을 손봐야 합니다.

## 체크리스트

- [ ] issue 본문에 background와 goal을 적었습니다.
- [ ] issue에 최소 하나의 label과 assignee를 지정했습니다.
- [ ] branch 이름에 issue 번호를 포함했습니다.
- [ ] PR 본문에 `Closes #N`을 넣었습니다.
- [ ] merge 후 issue가 자동으로 닫혔는지 확인했습니다.
- [ ] Project board에서 issue와 PR을 카드로 볼 수 있습니다.

## 연습 문제

1. issue 두 개를 만들고 하나의 PR에만 `Closes #N`을 넣은 뒤 merge 결과 차이를 비교해 보세요.
2. Project board의 column 이름을 팀에 맞게 바꾸고 직접 카드 이동 흐름을 설계해 보세요.

## 정리와 다음 글

issue는 할 일, PR은 그 일을 끝내는 변경, Project는 현재 상태를 보여 주는 보드입니다. PR 본문에 `Closes #N`을 적으면 merge 시 issue가 자동으로 닫히고, label, milestone, assignee는 작업을 분류하고 맡기고 묶는 데 쓰입니다.

다음 글에서는 PR 본문보다 더 짧지만 훨씬 자주 읽히는 commit message를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- [merge와 conflict 해결하기 - 두 줄기를 다시 합치기](./05-merge-and-conflict.md)
- [GitHub repository 만들기 - remote, push, pull 한 번에 익히기](./06-github-repository.md)
- [Pull Request로 협업하기 - branch에서 review를 거쳐 main까지](./07-pull-request.md)
- **Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (현재 글)**
- 좋은 commit message 쓰기 (예정)
- 실전 Git workflow 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [GitHub Docs — About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) — issue를 commit·PR과 다른 작업 단위로 이해하는 출발점입니다.
- [GitHub Docs — Managing labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels) — label을 분류 체계로 쓰는 방법을 확인할 수 있습니다.
- [GitHub Docs — About milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones) — milestone으로 여러 issue와 PR을 일정 단위로 묶는 개념을 보강합니다.
- [GitHub Docs — Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) — `Closes #N`이 default branch merge와 함께 issue를 닫는 규칙을 설명합니다.
- [GitHub Docs — Using keywords in issues and pull requests](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/using-keywords-in-issues-and-pull-requests) — closing keyword 문법과 여러 issue를 함께 닫는 표기법의 기준 문서입니다.
- [GitHub Docs — About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) — board, custom field, automation을 포함한 Projects의 기본 개념을 정리합니다.
Tags: github-issue, github-project, issue-tracking, kanban-board, issue-pr-linking, closes-keyword
