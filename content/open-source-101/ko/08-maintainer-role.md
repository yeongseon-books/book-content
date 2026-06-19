---
series: open-source-101
episode: 8
title: "Open Source 101 (8/10): 메인테이너의 역할"
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
  - Maintainer
  - Triage
  - Burnout
  - Beginner
seo_description: 메인테이너의 책임을 기술적 판단을 넘어 운영과 경계 설정, 위임의 관점에서 정의하고 지속 가능한 프로젝트 유지 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (8/10): 메인테이너의 역할

오픈소스를 처음 볼 때는 메인테이너를 코드를 가장 잘 아는 사람 정도로 생각하기 쉽습니다. 물론 기술적인 판단도 중요합니다. 하지만 실제로 메인테이너가 하는 일은 훨씬 넓습니다. 이슈를 정리하고, 리뷰 우선순위를 잡고, 릴리스를 내고, 사람 사이의 경계를 조율하고, 후계자를 키우는 일까지 포함됩니다.

이 글은 오픈소스 101 시리즈의 8번째 글입니다.

여기서는 메인테이너를 뛰어난 개발자 한 명이 아니라, 프로젝트의 흐름과 책임을 오래 유지하게 만드는 운영 책임자로 정리하겠습니다.

![Open Source 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/08/08-01-the-maintainer-loop-in-one-line.ko.png)
*Open Source 101 8장 흐름 개요*
> 메인테이너는 기술 결정만 하는 것이 아니라 **커뮤니티 건강, 방향성, 지속 가능성**을 함께 고민하는 역할입니다.

## 이 글에서 다룰 문제

- 메인테이너는 실제로 어떤 책임을 지고 있을까요?
- triage, review, release는 왜 하나의 루틴으로 묶어 봐야 할까요?
- 권한 위임과 후계자 육성은 왜 선택이 아니라 지속성 문제일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

메인테이너의 건강 상태가 곧 프로젝트의 수명과 연결되는 경우가 많습니다. 한 사람에게 리뷰, 릴리스, 커뮤니티 응답이 모두 몰리면 코드 품질보다 지속 가능성이 먼저 무너집니다.

또 메인테이너는 프로젝트 문화의 기준점 역할을 합니다. 응답 속도, 리뷰 톤, 문서 수준, 릴리스 규칙이 대부분 여기서 시작됩니다. 그래서 메인테이너 역할을 이해하는 것은 오픈소스 운영의 본체를 이해하는 일과 비슷합니다.

## 핵심 관점

메인테이너 일을 한 줄로 그리면 이렇습니다:

```text
Triage (이슈 분류)
  → Review (PR 검토)
  → Release (릴리스)
  → Delegate (위임)
  → 반복
```

이 순서가 중요한 이유는 일이 쌓이는 방식이 이 흐름을 따르기 때문입니다. triage가 흔들리면 리뷰가 밀리고, 리뷰가 밀리면 릴리스가 늦어지고, 릴리스가 늦어지면 메인테이너에게 더 많은 요청이 몰립니다. 결국 위임이 없으면 루프 전체가 막힙니다.

> 강한 메인테이너는 모든 답을 혼자 쥔 사람이 아닙니다. **프로젝트가 자신 없이도 굴러가게 만드는 사람**입니다.

## 핵심 개념

### 메인테이너 성장 단계

| 단계 | 역할 | 특징 | 위험 |
|---|---|---|---|
| 창업 메인테이너 | 모든 작업 직접 수행 | 빠른 결정, 완전한 이해 | bus factor = 1 |
| 위임 메인테이너 | 일부 권한 공유 | 코드 리뷰 분담 | 위임 기준 불명확 |
| 플랫폼 메인테이너 | 방향만 결정 | 팀이 일상 운영 | 관여도 저하 |
| 명예 메인테이너 | 자문 역할 | 후임이 주도 | 전환 실패 시 공백 |

### 오픈소스 문서 유형과 책임

| 문서 | 목적 | 독자 | 업데이트 주기 |
|---|---|---|---|
| README | 첫 5분 온보딩 | 신규 사용자 | 기능 추가·변경 시 |
| CONTRIBUTING.md | 기여 절차 | 신규 기여자 | 규칙 변경 시 |
| CHANGELOG | 버전별 변경 이력 | 기존 사용자 | 릴리스마다 |
| API Reference | 함수/클래스 명세 | 개발자 | 코드 변경 시 |
| GOVERNANCE.md | 의사결정 구조 | 커미터, 기여자 | 구조 변경 시 |

### bus factor 이해

bus factor는 특정 인물이 빠졌을 때 프로젝트가 얼마나 위험해지는지 보여 주는 지표입니다.

```bash
# 기여자 분산 확인
gh api repos/owner/repo/contributors \
  | jq 'sort_by(-.contributions) | .[:5] | .[] | {login, contributions}'

# 출력 예시:
# {"login": "alice", "contributions": 1847}  ← bus factor 위험
# {"login": "bob", "contributions": 23}
# {"login": "carol", "contributions": 12}
```

bus factor가 1이면 alice가 없으면 프로젝트가 멈출 위험이 높습니다. 3 이상을 목표로 합니다.

## 주간 메인테이너 루틴

번아웃을 방지하려면 반응형이 아닌 계획적 운영이 필요합니다.

### 주간 스케줄 예시

```text
월요일 30분: Triage
  - 새 이슈 확인 및 라벨 부여
  - 재현 불가능 이슈 닫기
  - good first issue 후보 선정

수요일 60분: PR 리뷰
  - 오래된 PR 우선 (FIFO)
  - Draft PR은 방향 피드백만
  - 머지 가능한 PR 처리

금요일 30분: 커뮤니티
  - Discussions 미답변 확인
  - Stale 이슈 처리 (30일 이상 비활성)
  - 다음 릴리스 준비 상태 확인
```

### triage 자동화

```yaml
# .github/workflows/triage.yml
name: Issue Triage

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  auto-label:
    runs-on: ubuntu-latest
    steps:
    # 키워드 기반 자동 라벨링
    - uses: actions/labeler@v5
      with:
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        configuration-path: .github/labeler.yml

    # Stale 이슈 자동 처리
  stale:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
    - uses: actions/stale@v9
      with:
        stale-issue-message: |
          이 이슈는 30일 동안 활동이 없어 자동으로 `stale` 라벨이 붙었습니다.
          관련이 있으면 댓글을 달아 주세요.
        stale-pr-message: |
          이 PR은 14일 동안 업데이트가 없었습니다.
          계속 진행할 계획이 있으면 알려 주세요.
        days-before-stale: 30
        days-before-close: 7
```

## 권한 위임 설계

위임은 부담을 덜기 위한 편법이 아니라 프로젝트 리스크를 줄이는 핵심 수단입니다.

### 역할 단계 문서화 (CONTRIBUTING.md)

```markdown
## 역할 단계

### Contributor
- 조건: PR 1회 이상 머지
- 권한: 이슈 작성, PR 제출
- 경로: 첫 PR 머지 후 자동

### Reviewer
- 조건: 주 1회 이상 PR 리뷰 + 3개월 이상 활동
- 권한: PR 리뷰 코멘트, 라벨링
- 경로: 메인테이너 추천

### Committer
- 조건: 2인 이상 추천 + 1개월 관찰 기간
- 권한: 브랜치 쓰기, PR 머지 (단 main 제외)
- 경로: GitHub Teams 추가

### Maintainer
- 조건: 6개월 이상 커미터 활동 + 릴리스 참여
- 권한: 전체 저장소 관리, 릴리스 권한
- 경로: 기존 메인테이너 만장일치
```

### GitHub Teams 권한 설정

```bash
# GitHub CLI로 팀 생성 및 권한 부여
gh api orgs/owner/teams \
  --method POST \
  --field name="reviewers" \
  --field description="PR reviewers with triage permission"

# 저장소에 팀 권한 추가
gh api orgs/owner/teams/reviewers/repos/owner/repo \
  --method PUT \
  --field permission="triage"  # read/triage/write/maintain/admin
```

## 문서 자동화

메인테이너 혼자 모든 문서를 수동 관리하면 금방 지칩니다.

```yaml
# .github/workflows/docs.yml
name: Deploy Docs

on:
  push:
    branches: [main]
    paths: ['docs/**', 'src/**/*.py']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: pip install mkdocs-material mkdocstrings[python]

    - name: Build and deploy
      run: mkdocs gh-deploy --force
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`mkdocs.yml`:

```yaml
site_name: My Project
theme:
  name: material

plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
```

이렇게 하면 코드의 docstring이 자동으로 API 문서가 됩니다. 메인테이너는 코드와 docstring만 유지하면 됩니다.

## 메인테이너 일정 투명화

```markdown
## Maintainer Availability (README에 추가)

- @alice: 월-금 UTC 09:00-17:00, PR 리뷰 48시간 이내
- @bob: 주말 위주, 리뷰 72시간 이내
- 휴가/부재: [Status](https://github.com/owner/repo/issues/999)에서 확인

현재 부재: @alice 2026-06-15 ~ 2026-06-22 (휴가)
```

```markdown
<!-- PR 리뷰 대기 중일 때 PR에 추가 -->
[Maintainer status: On vacation until Jun 22.
Reviews will resume after that date.]
```

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 혼자 모든 PR 리뷰 | 리뷰가 한 명에게 집중되어 병목 발생 | Reviewer 역할 분산, Teams 활용 |
| 부재 미공지 | 2주 휴가 동안 무응답 | README 또는 이슈에 부재 공지 |
| bus factor 1 방치 | 핵심 지식이 한 명에게만 있음 | wiki, ADR 문서화, 신규 커미터 육성 |
| 라벨 체계 부재 | 모든 이슈가 우선순위 없이 쌓임 | `P0-critical`, `P1-high`, `P2-normal` 등 우선순위 라벨 |
| 후계자 미육성 | 번아웃 시 프로젝트 중단 | CONTRIBUTING.md에 역할 승격 경로 명시 |

## 실무에서는 이렇게 생각한다

회사 안에서 기술 책임자나 플랫폼 오너가 맡는 역할과 매우 비슷합니다. 들어오는 요청을 정리하고, 코드 기준을 맞추고, 릴리스 일정을 잡고, 사람을 성장시키는 일이 함께 묶여 있습니다. 그래서 오픈소스 메인테이너 경험은 기술 리더십 훈련으로도 가치가 큽니다.

시니어 엔지니어는 메인테이너십을 영웅 역할로 보지 않습니다. 반복 가능한 루틴, 명확한 권한 위임, 공개된 일정과 경계, 그리고 후계자 육성이 있어야 프로젝트가 사람 한 명을 넘어섭니다.

**메인테이너 번아웃 조기 신호**:

```text
- 이슈/PR 응답 시간이 평소 3배 이상 늘어남
- 커밋 그래프에 2주 이상 공백
- CHANGELOG 업데이트 없이 코드만 변경
- "나중에 처리할게요" 댓글이 쌓임
- 기능 요청을 이유 없이 거부하는 패턴
```

번아웃 신호가 보이면 즉시 대응합니다:
1. 부재 공지 게시
2. Reviewer에게 일부 PR 리뷰 위임
3. 새 이슈 intake 임시 중단 (interaction limits 활용)
4. 핵심 버그만 처리하는 "maintenance mode" 공지

## 운영 체크리스트

- [ ] 주간 triage 루틴이 있습니다.
- [ ] 리뷰 응답 기준을 정했습니다.
- [ ] 위임 가능한 권한을 식별했습니다.
- [ ] bus factor를 2 이상으로 올릴 계획이 있습니다.
- [ ] 부재 공지 방법을 정했습니다.

## 연습 문제

1. bus factor를 한 문장으로 정의해 보세요.
2. triage와 review의 차이를 한 문장으로 적어 보세요.
3. 후계자를 키우는 방법 하나를 적어 보세요.

## 정리

이번 글에서는 메인테이너를 뛰어난 개발자가 아니라 프로젝트의 흐름을 지키는 운영 책임자로 정리했습니다. 오픈소스가 오래 가려면 코드를 잘 쓰는 사람보다, 일을 나누고 경계를 세울 수 있는 사람이 필요할 때가 많습니다.

다음 글에서는 이런 경험이 개인 경력에 어떻게 쌓이는지 보겠습니다. 오픈소스 활동을 포트폴리오로 정리하는 방법이 이어집니다.

## 처음 질문으로 돌아가기

- **메인테이너는 실제로 어떤 책임을 지고 있을까요?**
  - 이슈 triage (분류와 우선순위), PR 리뷰 (코드 품질과 방향성 확인), 릴리스 관리 (버전, CHANGELOG, 배포), 커뮤니티 운영 (행동 강령 집행, 신규 기여자 환영), 문서 유지, 권한 위임, 후계자 육성까지입니다. 코드 작성보다 이 모든 일이 프로젝트 수명에 더 큰 영향을 줍니다.
- **triage, review, release는 왜 하나의 루틴으로 묶어 봐야 할까요?**
  - 세 단계는 순환 의존성을 가집니다. triage가 안 되면 무엇을 리뷰해야 하는지 모르고, 리뷰가 안 되면 릴리스 준비가 안 되며, 릴리스가 안 되면 더 많은 이슈가 생깁니다. 이 루프를 하나의 반복 리듬으로 설계하지 않으면 각 단계가 서로를 막습니다.
- **권한 위임과 후계자 육성은 왜 선택이 아니라 지속성 문제일까요?**
  - bus factor가 1인 프로젝트는 메인테이너 한 명의 번아웃, 이직, 사고로 중단됩니다. 이미 수만 명이 쓰는 도구가 메인테이너 한 명의 중단으로 archive되는 사례는 오픈소스 역사에서 반복됩니다. 위임과 후계자 육성은 개인 편의가 아니라 프로젝트가 자신을 넘어 살아남게 만드는 설계 결정입니다.

<!-- toc:end -->

## 참고 자료

- [Open Source Guides — Maintainer](https://opensource.guide/best-practices/)
- [Bus factor](https://en.wikipedia.org/wiki/Bus_factor)
- [Maintainer Burnout](https://opensource.guide/maintainer-mental-health/)
- [GitHub Teams](https://docs.github.com/en/organizations/organizing-members-into-teams)
- [github/maintainers 저장소](https://github.com/github/maintainers)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, Maintainer, Triage, Burnout, Beginner
