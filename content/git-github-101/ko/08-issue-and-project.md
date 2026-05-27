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
title: "Git & GitHub 101 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법"
seo_description: GitHub Issue와 Project로 일감 흐름을 추적하는 방법을 설명합니다.
---

# Git & GitHub 101 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법

코드 이력은 무엇이 바뀌었는지를 잘 보여 주지만, 팀은 그보다 앞선 질문도 자주 다룹니다. 지금 무엇을 해야 하는지, 누가 맡고 있는지, 어디까지 왔는지를 저장소 안에서 함께 볼 수 있어야 일이 덜 흩어집니다.

이 글은 Git/GitHub 101 시리즈의 여덟 번째 글입니다. 여기서는 Issue, Pull Request, Project board를 하나의 작업 추적 흐름으로 연결해 봅니다.


![Git & GitHub 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/08/08-01-mental-model.ko.png)
*Git & GitHub 101 8장 흐름 개요*

> Issue·PR·Project board를 따로 쓰면 일감과 코드가 따로 흐릅니다 — '무엇을 해야 하는지(Issue)', '무엇을 했는지(PR)', '어디까지 왔는지(Project)'를 같은 저장소 안에 묶어야 작업 추적이 사람의 기억이 아니라 시스템 위에서 흐릅니다.

## 먼저 던지는 질문

- GitHub Issue는 commit이나 PR과 어떻게 다를까요?
- label, assignee, milestone은 언제 유용할까요?
- PR 본문의 `Closes #42`는 왜 중요한 자동화일까요?

## 왜 중요한가

지금까지의 시리즈는 코드 변경 자체를 기록하는 법에 집중했습니다. 하지만 실무에서는 그보다 먼저 "무엇을 해야 하지?"라는 질문이 더 자주 나옵니다. Issue와 Project는 이 질문을 코드 저장소 바로 옆에서 다루게 해 줍니다.

할 일과 진행 상황을 GitHub 안에 두면 작업의 시작과 끝이 선명해집니다. issue를 열고, PR로 작업을 마치고, merge와 함께 issue를 닫으며, board에서는 상태가 카드로 보입니다. 몇 달 뒤 변경 이유를 되짚을 때도 commit → PR → issue 순서로 의도를 다시 찾을 수 있습니다.

## 핵심 그림

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
## 배경
notes.md에 여행 준비물을 기록할 위치가 없습니다.

## 목표
`## Packing list` 섹션을 만들고 기본 항목 3개를 추가합니다.
세부 구조 개선은 후속 PR에서 진행합니다.

## 범위 제외
- 인라인 이미지
- 다국어 처리
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

- issue 본문에 **배경**과 **목표**가 실제로 적혀 있는가
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

작은 팀이라도 주간 triage 미팅을 20~30분 정도 고정해 두면 효과가 큽니다. 이 시간에는 "새 이슈 추가"보다 "기존 이슈 정리"를 우선합니다. `needs-triage`가 오래 남은 카드를 줄이고, 이미 끝났는데 닫히지 않은 카드를 정리하고, `blocked` 이슈의 해소 경로를 확인하는 것만으로도 보드 신뢰도가 올라갑니다.

회의에서 바로 쓰기 좋은 순서는 다음과 같습니다.

1. 지난주 완료 이슈를 빠르게 훑고 재오픈 여부를 확인합니다.
2. 이번 주 milestone에 들어갈 이슈를 우선순위 기준으로 확정합니다.
3. 담당자가 없는 이슈를 정리하거나 backlog로 되돌립니다.
4. 자동화 규칙 누락으로 상태가 어긋난 카드를 수정합니다.

이 루틴을 매주 반복하면 "작업은 했는데 보드엔 반영되지 않은" 상황이 크게 줄어듭니다. 결국 Project는 보고서가 아니라 실행 리듬을 유지하는 장치입니다.

또한 신규 팀원 온보딩 관점에서도 이 구조가 중요합니다. 새로 합류한 사람이 코드를 읽기 전에 issue와 Project를 먼저 보면, 현재 팀이 어디에 시간을 쓰고 있는지 빠르게 파악할 수 있습니다. 작업 이력의 문맥이 남아 있기 때문에 "무엇을 바꿨는가"뿐 아니라 "왜 그 순서로 처리했는가"까지 자연스럽게 전달됩니다.

## 체크리스트

- [ ] issue 본문에 배경과 목표를 적었습니다.
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


## 이슈 템플릿으로 입력 품질 고정하기

Issue를 많이 쓰기 시작하면 가장 먼저 생기는 문제는 "각자 다른 방식으로 적는다"는 점입니다. 누군가는 재현 절차를 남기고, 누군가는 한 줄 제목만 적고 끝냅니다. 이 상태에서는 label과 Project 자동화가 있어도 카드 품질이 들쑥날쑥해서 흐름이 쉽게 무너집니다.

이때 가장 효과적인 장치가 **issue template**입니다. 템플릿은 길게 만들기보다, 작업 판단에 꼭 필요한 항목만 강제하는 편이 좋습니다.

```yaml
name: "기능 요청"
description: "사용자 가치가 있는 기능을 제안합니다"
title: "[기능] "
labels: ["enhancement", "needs-triage"]
body:
  - type: textarea
    attributes:
      label: 배경
      description: 어떤 문제를 해결하려고 하나요?
    validations:
      required: true
  - type: textarea
    attributes:
      label: 목표
      description: 이 작업의 완료 조건은 무엇인가요?
    validations:
      required: true
  - type: textarea
    attributes:
      label: 범위 제외
      description: 이번 작업에서 하지 않을 것은 무엇인가요?
```

핵심은 템플릿으로 문서를 예쁘게 만드는 것이 아니라, triage 단계에서 빠르게 판단할 근거를 모으는 일입니다. 배경, 목표, 범위 제외만 있어도 우선순위와 작업 크기 판단이 훨씬 빨라집니다. 버그 템플릿에는 재현 절차, 기대 동작, 실제 동작, 로그 첨부 칸을 따로 두면 좋습니다.

## label과 milestone 설계: 많게보다 일관되게

label은 "분류 체계"이고 milestone은 "시간 단위 묶음"입니다. 둘을 섞어 쓰면 보드가 곧바로 복잡해집니다. 예를 들어 `priority-high` 같은 우선순위와 `sprint-12` 같은 일정을 모두 label로만 관리하면, 검색은 가능해도 계획 관리가 어려워집니다.

실무에서는 label을 4~6개 축으로 제한하는 편이 유지보수에 유리합니다.

| 축 | 예시 label | 목적 |
| --- | --- | --- |
| 유형 | `bug`, `enhancement`, `docs`, `refactor` | 작업 성격 구분 |
| 우선순위 | `priority/p0`, `priority/p1`, `priority/p2` | 대응 순서 정렬 |
| 영역 | `area/auth`, `area/ui`, `area/api` | 코드 소유 영역 추적 |
| 상태 보조 | `needs-triage`, `blocked`, `ready-for-review` | 병목 지점 식별 |

milestone은 "이번 주", "v1.2", "6월 릴리스"처럼 명확한 완료 시점을 가진 단위로만 두는 것이 좋습니다. milestone이 너무 많아지면 오히려 일정 신뢰도가 떨어집니다. 기본 원칙은 간단합니다. **label은 검색과 필터링, milestone은 일정 약속**입니다.

## GitHub Projects 보드 구성: 필드와 뷰를 분리해서 생각하기

Projects(신형)는 칸반 보드 한 화면으로 끝나지 않습니다. 보드(board), 표(table), 타임라인(roadmap) 뷰를 같은 데이터 위에 겹쳐 보여 줍니다. 그래서 처음 설계할 때는 "column 이름"보다 "필드 정의"가 더 중요합니다.

추천 최소 필드는 다음과 같습니다.

- `상태`(단일 선택): `할 일`, `진행 중`, `리뷰 중`, `완료`
- `우선순위`(단일 선택): `P0`, `P1`, `P2`
- `예상 크기`(숫자 또는 단일 선택): `S`, `M`, `L`
- `목표 시점`(date 또는 iteration): 스프린트/주차 관리

이렇게 필드를 분리하면 같은 카드라도 보는 관점이 달라집니다. 개발자는 board 뷰에서 현재 상태를 보고, 리더는 table 뷰에서 우선순위 정렬을 보고, 일정 담당자는 roadmap 뷰에서 마감 밀림을 확인할 수 있습니다. 같은 정보를 여러 번 입력하지 않아도 되는 이유가 여기에 있습니다.

## 이슈-PR 연결 규칙을 팀 규약으로 만들기

`Closes #N`은 단순한 문법이 아니라 팀의 완료 정의와 연결됩니다. 누군가는 PR을 열면 끝났다고 생각하고, 누군가는 merge돼야 끝났다고 생각합니다. 이 차이를 줄이려면 자동 닫기 규칙을 문서로 고정하는 편이 좋습니다.

권장 규칙은 다음과 같습니다.

1. PR 본문 첫 부분에 연결 이슈를 명시합니다. 예: `Closes #128`
2. 여러 이슈를 함께 닫을 때는 각 번호에 키워드를 반복합니다. 예: `Closes #128`, `Resolves #131`
3. 다른 저장소 이슈는 `owner/repo#N` 형식으로 씁니다.
4. "참고 연결"만 하고 닫지는 않을 때는 `Related to #N`을 사용합니다.

아래처럼 템플릿 문구를 미리 넣어 두면 누락이 줄어듭니다.

```text
## 연결 이슈
Closes #

## 변경 이유

## 검증 방법
```

이 규칙의 장점은 merge 직후에 바로 드러납니다. issue 닫힘, Project 상태 전환, 릴리스 노트 수집이 하나의 연결고리로 이어지기 때문입니다.

## 자동화 규칙: 사람이 반복하는 이동을 줄이기

Project를 수동으로만 운영하면 초반에는 괜찮아도 금방 어긋납니다. 카드 이동이 밀리면 보드 신뢰도가 떨어지고, 결국 팀은 보드를 보지 않게 됩니다. 그래서 반복 동작은 자동화로 넘기는 것이 안전합니다.

예를 들면 다음 규칙부터 시작할 수 있습니다.

- 이슈가 생성되면 `상태=할 일`로 설정
- PR이 열리면 연결 이슈 `상태=진행 중`
- PR이 `review requested`면 `상태=리뷰 중`
- PR이 merge되고 이슈가 닫히면 `상태=완료`
- `blocked` label이 붙으면 우선순위 점검 알림

자동화는 한 번에 많이 넣기보다 "누락이 잦은 2~3개"부터 두는 편이 좋습니다. 자동화 자체도 운영 대상이기 때문에, 규칙이 많을수록 디버깅 비용이 증가합니다.

## 계획 수립 워크플로: backlog에서 완료까지

Issue와 Project를 진짜 운영 도구로 쓰려면 계획 주기를 함께 정해야 합니다. 아래 흐름은 작은 팀에서도 바로 적용하기 쉽습니다.

1. **수집(Backlog)**: 새 아이디어와 버그를 issue로 등록하고 `needs-triage`를 붙입니다.
2. **분류(Triage)**: 주 1~2회 짧게 모여 우선순위, 담당자, milestone을 정합니다.
3. **실행(Delivery)**: 담당자는 branch를 만들고 PR 본문에 `Closes #N`을 넣습니다.
4. **검토(Review)**: 코드 리뷰와 테스트 통과 후 merge합니다.
5. **회고(Review of flow)**: 닫힌 issue의 lead time, 재오픈 비율, blocked 원인을 간단히 점검합니다.

이 흐름에서 중요한 점은 "정교한 지표"보다 "반복 가능한 리듬"입니다. 매주 같은 규칙으로 triage하고, 같은 형식으로 PR을 열고, 같은 자동화로 상태를 갱신하면 작업량이 늘어도 흐름이 깨지지 않습니다.

## 운영 중 자주 생기는 막힘과 대응

아래는 Project를 도입한 팀에서 자주 만나는 병목입니다.

| 상황 | 흔한 원인 | 대응 |
| --- | --- | --- |
| `진행 중` 카드가 계속 쌓임 | WIP 제한 없음 | `진행 중` 최대 개수 규칙 도입 |
| `할 일` 카드만 많고 착수 안 됨 | 우선순위 기준 불명확 | `P0/P1/P2` 기준 문서화 |
| merge됐는데 보드가 안 바뀜 | 이슈-PR 연결 누락 | PR 템플릿에 `Closes #` 강제 |
| 이슈 재오픈 반복 | 완료 조건 미정의 | issue에 수용 기준(acceptance criteria) 추가 |

이 표를 보면 공통점이 보입니다. 대부분의 문제는 GitHub 기능 부족이 아니라, 입력 규칙과 상태 전환 규칙이 약해서 생깁니다. 결국 Issue와 Project 운영은 도구 사용법보다 팀 규약 설계에 더 가깝습니다.

## 처음 질문으로 돌아가기

- **GitHub Issue는 commit이나 PR과 어떻게 다를까요?**
  - Issue는 작업의 맥락과 완료 조건을 담는 계획 단위이고, PR은 그 작업을 코드 변경으로 실현한 검토 단위입니다. commit은 변경 조각을 기록하는 최소 단위이므로, 세 개를 역할별로 분리해야 추적이 선명해집니다.
- **label, assignee, milestone은 언제 유용할까요?**
  - label은 분류와 필터링, assignee는 책임 주체, milestone은 일정 약속을 나타냅니다. 세 값을 함께 써야 backlog 정리, 우선순위 결정, 릴리스 계획이 같은 화면에서 연결됩니다.
- **PR 본문의 `Closes #42`는 왜 중요한 자동화일까요?**
  - merge 시 issue를 자동으로 닫고 Project 상태 전환까지 이어 주기 때문입니다. 연결 문구 하나가 완료 기록, 릴리스 추적, 회고 지표를 동시에 정확하게 만듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- [Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기](./05-merge-and-conflict.md)
- [Git & GitHub 101 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기](./06-github-repository.md)
- [Git & GitHub 101 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지](./07-pull-request.md)
- **Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (현재 글)**
- 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (예정)
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [GitHub Docs — About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) — issue를 commit·PR과 다른 작업 단위로 이해하는 출발점입니다.
- [GitHub Docs — Managing labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels) — label을 분류 체계로 쓰는 방법을 확인할 수 있습니다.
- [GitHub Docs — About milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones) — milestone으로 여러 issue와 PR을 일정 단위로 묶는 개념을 보강합니다.
- [GitHub Docs — Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) — `Closes #N`이 default branch merge와 함께 issue를 닫는 규칙을 설명합니다.
- [GitHub Docs — Using keywords in issues and pull requests](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/using-keywords-in-issues-and-pull-requests) — closing keyword 문법과 여러 issue를 함께 닫는 표기법의 기준 문서입니다.
- [GitHub Docs — About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) — board, custom field, automation을 포함한 Projects의 기본 개념을 정리합니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/08-issue-and-project)

Tags: github-issue, github-project, issue-tracking, kanban-board, issue-pr-linking, closes-keyword
