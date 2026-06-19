---
series: open-source-101
episode: 3
title: "Open Source 101 (3/10): 이슈 읽기"
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
  - Issues
  - GitHub
  - Triage
  - Beginner
seo_description: 깃허브 이슈를 단순한 할 일 목록이 아니라 문제 정의와 재현 절차, 합의 기록이 담긴 공동 작업 기록으로 읽는 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (3/10): 이슈 읽기

오픈소스 기여를 처음 시도할 때 가장 흔한 실수는 문제를 충분히 이해하기 전에 바로 고치려고 드는 것입니다. 제목만 보고 작업을 시작하거나, 댓글을 끝까지 읽지 않거나, 이미 다른 사람이 맡은 일을 모르고 풀 리퀘스트를 여는 경우가 대표적입니다.

이 글은 오픈소스 101 시리즈의 3번째 글입니다.

여기서는 깃허브 이슈를 단순한 할 일 목록이 아니라, 문제 정의와 재현 절차와 합의 기록이 쌓인 문서로 읽는 방법을 정리하겠습니다.

![Open Source 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/03/03-01-fix-the-reading-order-first.ko.png)
*Open Source 101 3장 흐름 개요*
> 이슈를 제대로 읽을 수 있으려면 **버그, 기능, 설계, 커뮤니티의 관심**이 서로 어떻게 얽히는지 먼저 이해해야 합니다.

## 이 글에서 다룰 문제

- 제목만 보고 판단하면 왜 기여 방향이 자주 빗나갈까요?
- 라벨, 재현 절차, 담당자, 댓글은 각각 어떤 역할을 할까요?
- `good first issue`가 붙어 있어도 바로 들어가기 어려운 경우는 언제일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

이슈를 잘못 읽으면 풀 리퀘스트 방향도 틀어집니다. 문제를 재현하지 못한 채 수정에 들어가면 원인과 증상을 섞기 쉽고, 이미 합의된 해결 방향을 모른 채 다른 방법을 제시하면 리뷰 비용만 늘어납니다. 초보자에게는 코드 실력보다 맥락 읽기 실수가 더 자주 발목을 잡습니다.

반대로 이슈를 차분히 읽을 줄 알면 작은 기여도 훨씬 잘 맞아 들어갑니다. 내가 무엇을 고치려는지, 누가 이미 논의했고, 어디까지가 범위인지 분명해지기 때문입니다. 이 능력은 오픈소스뿐 아니라 회사 안의 이슈 트래커를 읽을 때도 그대로 이어집니다.

## 핵심 관점

이슈를 읽는 올바른 순서는 이렇습니다.

```text
제목 (문제 종류 파악)
  → 라벨 (맥락과 난이도 확인)
  → 본문 (재현 절차, 환경, 기대/실제 동작)
  → 담당자 (작업 중인 사람 있는지 확인)
  → 댓글 (이미 논의된 해결 방향 파악)
  → 참여 가능 여부 판단
```

이 순서를 지키면 "내가 이 이슈를 안전하게 맡을 수 있나"라는 판단을 빠르게 할 수 있습니다. 이 순서를 건너뛰면 이미 닫힌 방향으로 PR을 만들거나, 담당자가 있는 이슈를 중복으로 잡는 실수를 하게 됩니다.

> 이슈는 막연한 게시글이 아닙니다. **문제 정의, 재현 증거, 합의 기록이 담긴 공동 작업 문서**입니다.

## 핵심 개념

### 이슈 유형 분류

| 유형 | 라벨 | 특징 | 참여 조건 |
|---|---|---|---|
| 버그 리포트 | `bug` | 재현 가능한 문제 보고 | 재현 환경 확인 필수 |
| 기능 요청 | `feature`, `enhancement` | 새 기능 제안 | 메인테이너 방향 합의 필요 |
| 문서 개선 | `documentation` | README, docstring 수정 | 진입 장벽 낮음 |
| 질문 | `question` | 사용 방법 문의 | Discussions로 이동 권장 |
| 초보자용 | `good first issue` | 범위가 작고 명확 | 첫 기여에 적합 |
| 도움 요청 | `help wanted` | 메인테이너가 시간 부족 | 경험 있는 기여자 적합 |

### 이슈 라벨 체계

라벨은 단순 태그가 아닙니다. 프로젝트의 분류 체계이며 검색 필터입니다.

```bash
# 진입하기 좋은 이슈 찾기
gh issue list --repo pandas-dev/pandas \
  --label "good first issue" \
  --state open \
  --json number,title,assignees \
  | jq '.[] | select(.assignees | length == 0)'

# 도움 필요한 이슈 찾기
gh issue list --repo django/django \
  --label "help wanted" \
  --state open
```

### 재현 절차 (repro steps)의 중요성

버그 이슈에서 재현 절차는 증거에 가깝습니다. 재현이 안 되는 버그는 수정 방향도 불명확합니다.

**좋은 재현 절차 예시**:

```markdown
## 재현 환경
- Python: 3.11.2
- requests: 2.31.0
- OS: macOS 14.1

## 재현 단계
1. `pip install requests==2.31.0` 실행
2. 다음 코드 실행:
```python
import requests
session = requests.Session()
session.get('https://httpbin.org/cookies/set/test/value')
print(session.cookies)  # 예상: {'test': 'value'}, 실제: {}
```

## 기대 동작
쿠키가 세션에 저장되어야 합니다.

## 실제 동작
쿠키 저장소가 비어 있습니다.

## 추가 정보
requests 2.30.0에서는 정상 동작 확인
```

**나쁜 재현 절차 예시**:

```markdown
requests 쓰면 쿠키가 안 됩니다. 버그 아닌가요?
```

차이가 명확합니다. 좋은 재현 절차는 메인테이너가 로컬에서 즉시 확인할 수 있게 해 줍니다.

## 이슈 읽기 실전 예시

실제 GitHub 이슈를 읽는 흐름을 단계별로 봅니다.

### 실제 이슈 분석 예시

```text
제목: [Bug] Session cookies not persisted across redirects on Safari 15

라벨: bug, good first issue, help wanted

담당자: 없음

본문:
## 환경
- Browser: Safari 15.1 on macOS 12
- requests-html: 0.10.0

## 재현 단계
1. https://example.com/login으로 POST 요청
2. 302 리다이렉트 발생
3. 리다이렉트 후 쿠키 확인

## 기대: 쿠키가 유지됨
## 실제: 쿠키 초기화됨

댓글 스레드:
[메인테이너 2일 전]: 재현됨. fix는 HTTPAdapter.send()에서 처리해야 할 것 같습니다.
[기여자 1일 전]: session.merge_environment_settings()를 확인해보겠습니다.
```

이 이슈를 읽는 순서:

```text
1. 제목: 버그 + Safari 15 + 세션 쿠키 → 환경 특이성 있음
2. 라벨: good first issue + help wanted → 진입 가능
3. 담당자: 없음 → 작업 가능
4. 재현 절차: 명확함 → 로컬에서 확인 가능
5. 댓글: 수정 위치 힌트 있음 → HTTPAdapter.send() 확인 필요
6. 판단: 참여 가능, 댓글로 접근 방법 확인 후 시작
```

### 이슈 참여 전 댓글 작성 패턴

이슈에 바로 코드를 제출하기 전에 댓글로 접근 방법을 확인합니다.

```markdown
안녕하세요. 이 이슈를 살펴봤습니다.

재현 환경을 확인했고, 댓글에서 언급된 HTTPAdapter.send() 방향을 검토했습니다.

제가 생각하는 수정 방향:
- `HTTPAdapter.send()`의 리다이렉트 처리 부분에서 쿠키를 다음 요청에 전달하는 로직 추가
- Safari 15의 SameSite 쿠키 정책 변경과 연관 가능성 확인

이 방향이 맞는지 확인 부탁드립니다. 괜찮다면 PR을 작성하겠습니다.

참고 코드 위치:
- `requests/adapters.py` - `HTTPAdapter.send()` 메서드 (라인 540-580)
```

이 방식의 장점: 메인테이너가 초기에 범위를 조정해 주기 때문에, 큰 방향 오류를 PR 단계에서 뒤늦게 고치지 않아도 됩니다.

## 이슈 템플릿 만들기

프로젝트에 이슈 템플릿을 두면 보고자가 필요한 정보를 빠트리지 않고 작성합니다.

### 버그 리포트 템플릿

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: 버그를 발견했다면 여기에 보고해 주세요
labels: ["bug"]
body:
  - type: textarea
    id: description
    attributes:
      label: 버그 설명
      description: 어떤 문제가 발생했나요?
    validations:
      required: true

  - type: textarea
    id: repro-steps
    attributes:
      label: 재현 단계
      placeholder: |
        1. '...'를 실행합니다
        2. '...'를 클릭합니다
        3. 오류가 표시됩니다
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: 기대 동작
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: 실제 동작
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: 버전
      placeholder: v1.2.3
    validations:
      required: true

  - type: dropdown
    id: os
    attributes:
      label: 운영 체제
      options:
        - macOS
        - Windows
        - Linux (Ubuntu)
        - Linux (기타)
    validations:
      required: true
```

### 기능 요청 템플릿

```yaml
# .github/ISSUE_TEMPLATE/feature_request.yml
name: Feature Request
description: 새 기능을 제안합니다
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: 해결하려는 문제
      description: 어떤 불편함이 있나요?
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: 제안하는 해결책
      placeholder: |
        ```python
        # 이런 API가 있으면 좋겠습니다
        result = my_function(input, option='new-feature')
        ```
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: 현재 회피 방법
      description: 지금은 어떻게 해결하고 있나요? (없으면 생략)
```

## 이슈 자동화

대형 프로젝트는 이슈 관리를 자동화합니다.

```yaml
# .github/workflows/issue-automation.yml
name: Issue Automation

on:
  issues:
    types: [opened, labeled]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
    # 새 이슈에 triage 라벨 자동 추가
    - name: Label new issues
      if: github.event.action == 'opened'
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.issues.addLabels({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: context.issue.number,
            labels: ['needs-triage']
          });

    # 30일 이상 비활성 이슈 닫기
    - name: Close stale issues
      uses: actions/stale@v9
      with:
        stale-issue-message: |
          이 이슈는 30일 동안 활동이 없어 자동으로 닫힙니다.
          관련이 있다면 다시 열어 주세요.
        days-before-stale: 30
        days-before-close: 7
```

## 직접 따라해 보기: 이슈 분석 절차

### 1단계 — 제목에서 문제 종류 파악하기

제목은 가장 짧은 요약입니다. 버그인지, 기능 요청인지, 환경 의존 문제인지 먼저 식별합니다.

```text
[Bug] login fails on Safari 15
→ 버그, Safari 특이성, 로그인 기능
```

### 2단계 — 라벨에서 맥락 읽기

라벨은 프로젝트가 이 문제를 어떻게 분류하고 있는지 보여 줍니다.

```text
labels: bug, good first issue, help wanted
→ 버그 + 초보자 진입 가능 + 도움 요청 = 참여 적합
```

### 3단계 — 재현 절차 확인하기

버그 이슈라면 재현 가능 여부가 가장 중요합니다.

```markdown
1. open https://example.com/login
2. enter valid credentials
3. click submit
expected: dashboard
actual: 500 error on Safari 15.1
```

### 4단계 — 댓글 스레드 따라가기

메인테이너가 추가 정보를 요청했는지, 이미 해결 방향이 정해졌는지 확인합니다.

```text
maintainer: "can you share browser version and error trace?"
reporter: "Safari 15.1 on macOS 12, stack trace: ..."
maintainer: "Confirmed. The issue is in session cookie handling."
→ 방향 합의됨, 참여 전 댓글로 확인 필요
```

### 5단계 — 지금 참여해도 되는지 판단하기

```text
- label has "good first issue": ✓
- repro reproducible: ✓
- no assignee: ✓
- direction agreed by maintainer: ✓
→ 댓글로 접근 방법 확인 후 PR 작성 시작
```

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 제목만 읽고 PR 제출 | "TypeError 수정"만 보고 바로 코드 변경 | 댓글 끝까지 읽고 합의된 방향 확인 |
| 재현 미확인 | 로컬에서 재현 안 해보고 수정 시도 | 재현 환경 구성 후 직접 확인 |
| 담당자 있는 이슈 선점 | `assignees` 확인 없이 같은 이슈 작업 | 이슈 댓글로 "진행해도 되나요?" 확인 |
| 라벨 무시 | `wontfix` 이슈에 PR 제출 | 라벨 의미 먼저 파악 후 참여 여부 결정 |
| 댓글 결정 사항 누락 | 50개 댓글 중 30번째 댓글의 방향 변경 무시 | 댓글 전체 읽기, 가장 최신 합의 확인 |

## 실무에서는 이렇게 생각한다

회사 내부 이슈 트래커도 결국 같은 원리로 움직입니다. 제목은 요약, 본문은 상황 설명, 댓글은 의사결정 기록이라는 구조는 깃허브 이슈와 크게 다르지 않습니다. 그래서 오픈소스 이슈를 잘 읽는 습관은 그대로 실무 triage 감각으로 이어집니다.

시니어 엔지니어는 이슈를 해결 목록이 아니라 합의 문서로 봅니다. 누가 어떤 근거로 우선순위를 정했는지, 왜 이 문제를 지금 고치는지, 수정 범위가 어디까지인지 먼저 읽고 움직입니다. 이 단계가 탄탄하면 구현은 오히려 빨라집니다.

**주간 이슈 정리 습관** — 오픈소스 프로젝트는 이슈가 빠르게 쌓입니다. 메인테이너는 주 1-2회 정도 triage 시간을 갖습니다:

```bash
# 새 이슈 확인
gh issue list --state open --label "needs-triage"

# 오래된 이슈 확인 (30일 이상 비활성)
gh issue list --state open --json number,title,updatedAt \
  | jq '.[] | select(.updatedAt < "2026-04-20")'

# 재현 절차 없는 버그 이슈 찾기
gh issue list --label "bug,needs-repro"
```

## 운영 체크리스트

- [ ] 제목과 본문을 끝까지 읽었습니다.
- [ ] 재현 절차를 확인하거나 직접 따라해 보았습니다.
- [ ] 라벨과 담당자 상태를 확인했습니다.
- [ ] 댓글에서 이미 정리된 합의가 있는지 확인했습니다.
- [ ] 참여 전 댓글로 접근 방법을 메인테이너에게 확인했습니다.

## 연습 문제

1. `good first issue` 라벨의 의미를 한 문장으로 적어 보세요.
2. triage를 한 문장으로 설명해 보세요.
3. 재현 절차가 없는 버그 이슈의 위험을 한 문장으로 적어 보세요.

## 정리

이번 글에서는 이슈를 읽는 순서와 기준을 정리했습니다. 중요한 점은 이슈를 단순한 문제 제기 글이 아니라 공동 작업 기록으로 보는 시각입니다. 이 관점이 생기면 어떤 이슈를 골라야 할지, 어디까지 준비한 뒤에 기여를 시작해야 할지가 훨씬 분명해집니다.

다음 글에서는 이렇게 읽어 낸 문제를 실제 풀 리퀘스트로 연결하는 과정을 다룹니다. 작은 변경을 어떻게 깔끔한 기여 단위로 만들지 이어서 보겠습니다.

## 처음 질문으로 돌아가기

- **제목만 보고 판단하면 왜 기여 방향이 자주 빗나갈까요?**
  - 이슈 제목은 증상을 압축한 요약입니다. 댓글에는 이미 합의된 해결 방향, 시도했다가 실패한 접근, 메인테이너의 우선순위 판단이 담겨 있습니다. 제목만 보고 구현하면 이미 다른 방향으로 논의가 끝난 경우에 헛수고를 하게 됩니다.
- **라벨, 재현 절차, 담당자, 댓글은 각각 어떤 역할을 할까요?**
  - 라벨은 문제의 성격과 난이도를 알려 주는 분류 체계입니다. 재현 절차는 버그를 논의 가능한 상태로 만드는 증거입니다. 담당자는 이미 작업 중인 사람이 있는지 알려 줍니다. 댓글은 이미 지나간 의사결정과 합의 기록입니다.
- **`good first issue`가 붙어 있어도 바로 들어가기 어려운 경우는 언제일까요?**
  - 담당자가 이미 배정된 경우, 재현 절차가 없어 문제를 확인하기 어려운 경우, 댓글에서 이미 구현 방향이 바뀐 경우, 또는 해결에 프로젝트 전체 구조 이해가 필요한 경우에는 `good first issue` 라벨이 있어도 참여하기 어렵습니다.

<!-- toc:end -->

## 참고 자료

- [GitHub Issues docs](https://docs.github.com/en/issues)
- [good first issue](https://github.blog/2020-01-22-how-we-built-good-first-issues/)
- [Triage guide](https://opensource.guide/best-practices/)
- [Issue templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [github/issue-labeler](https://github.com/github/issue-labeler)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, Issues, GitHub, Triage, Beginner
