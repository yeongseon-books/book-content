---
series: github-actions-101
episode: 3
title: "GitHub Actions 101 (3/10): Trigger 이해하기"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - GitHubActions
  - Trigger
  - Event
  - Schedule
  - CICD
seo_description: push, PR, schedule, workflow_dispatch 트리거 설계를 실무 기준으로 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (3/10): Trigger 이해하기

자동화가 늘어나면 곧 새로운 문제가 생깁니다. “왜 문서 한 줄 바꿨는데 전체 빌드가 도는 거지?”, “왜 같은 PR에 push를 여러 번 하니까 대기열이 꽉 차지?”, “야간 검사는 한국 시간 새벽 2시에 돌고 싶은데 왜 엉뚱한 시각에 실행되지?” GitHub Actions에서 트리거 설계는 비용과 소음을 함께 다루는 문제입니다.

이 글은 GitHub Actions 101 시리즈의 3번째 글입니다. 여기서는 push, pull_request, schedule, workflow_dispatch를 어떻게 나눠 써야 하는지, 그리고 paths 필터와 concurrency로 불필요한 실행을 어떻게 줄이는지 살펴보겠습니다.

![GitHub Actions 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/03/03-01-diagram.ko.png)
*GitHub Actions 101 3장 흐름 개요*

## 먼저 던지는 질문

- push와 pull_request는 어떤 차이로 써야 할까요?
- schedule은 왜 로컬 시간이 아니라 UTC로 이해해야 할까요?
- workflow_dispatch는 언제 유용하고 무엇을 문서화해야 할까요?

## 왜 중요한가

트리거 설계는 실행 시점을 고르는 일이지만, 실제로는 팀의 비용 정책과도 연결됩니다. 모든 커밋마다 전체 테스트, 전체 빌드, 전체 배포 검증이 한꺼번에 돌면 처음에는 든든해 보여도 곧 러너 사용량과 대기 시간이 급격히 늘어납니다. 그 결과 개발자는 체크 결과를 기다리지 않고 머지하려는 유혹을 받게 됩니다.

반대로 PR에서는 빠른 검증만 돌리고, main push에서는 더 무거운 빌드와 배포 단계를 붙이고, 야간에는 오래 걸리는 e2e만 돌리면 같은 저장소도 훨씬 건강하게 운영할 수 있습니다. 트리거는 문법이 아니라 실행 정책입니다.

## 한눈에 보는 트리거 구조

이 그림은 GitHub Actions가 단일 입력만 받는 도구가 아니라는 점을 보여 줍니다. 같은 워크플로우라도 어떤 이벤트에서 시작되느냐에 따라 역할이 완전히 달라질 수 있습니다.

## 핵심 용어를 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| `push` | 브랜치에 커밋이 들어왔을 때 | main에 반영된 코드 기준 검증에 자주 씁니다 |
| `pull_request` | PR이 열리거나 갱신될 때 | 코드 리뷰 전 빠른 피드백용으로 적합합니다 |
| `schedule` | cron 기반 주기 실행 | UTC 기준이라 시간 변환이 중요합니다 |
| `workflow_dispatch` | 수동 실행 버튼 | 배포, 롤백, 점검 작업에 자주 씁니다 |
| `paths` / `branches` | 경로나 브랜치 기준 필터 | 불필요한 실행을 줄이는 가장 쉬운 수단입니다 |
| `concurrency` | 동시 실행 제어 | 중복 실행과 대기열 낭비를 줄입니다 |

트리거를 설계할 때는 “무엇을 실행할까”보다 먼저 “언제 실행하지 않는 것이 맞을까”를 생각하는 편이 좋습니다. 대개 비용 절감은 여기서 시작합니다.

## 자동화 전과 후를 비교해 보겠습니다

문서만 수정했는데도 전체 빌드와 테스트가 도는 저장소는 흔합니다. 관리자는 “어차피 안전하니까”라고 생각할 수 있지만, 개발자 입장에서는 매번 긴 대기 시간을 감수해야 합니다. 알림도 늘어나고, 진짜 중요한 실패가 묻히기도 쉽습니다.

반대로 `paths` 필터로 `src/**`, `tests/**`, `pyproject.toml` 같은 경로에만 반응하게 만들면, 문서 편집과 코드 변경이 다른 비용 구조를 갖게 됩니다. 즉, 트리거 설계만 바꿔도 같은 워크플로우가 훨씬 실용적으로 바뀝니다.

## 트리거를 5단계로 설계해 보겠습니다

### 1단계 — push와 PR을 구분하기

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

PR과 main push는 같은 검증이라도 역할이 다릅니다. PR은 머지 전에 위험을 빠르게 드러내는 용도이고, main push는 실제 기준 브랜치에 반영된 결과를 확인하는 용도입니다.

### 2단계 — 경로 필터로 비용 줄이기

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

`paths-ignore`보다 `paths`가 더 읽기 쉬운 경우가 많습니다. 어떤 파일이 바뀌었을 때 실행하는지가 명시적으로 드러나기 때문입니다.

### 3단계 — 주기 실행 만들기

```yaml
on:
  schedule:
    - cron: "0 17 * * 0-4"  # UTC 17:00 = KST 02:00, Sun-Thu
```

여기서 꼭 기억할 점은 cron이 UTC 기준이라는 사실입니다. 한국 시간 새벽 2시를 원한다면 그대로 `2`를 넣는 것이 아니라 UTC로 변환해서 써야 합니다.

### 4단계 — 수동 실행 입력 만들기

```yaml
on:
  workflow_dispatch:
    inputs:
      env:
        description: "deploy target"
        required: true
        default: staging
        type: choice
        options: [staging, production]
```

수동 실행은 단순히 버튼 하나 추가하는 기능이 아닙니다. 운영자가 어떤 값을 넣을 수 있고, 어떤 환경이 허용되는지를 코드로 드러내는 도구입니다.

### 5단계 — 중복 실행 막기

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

같은 PR에 짧은 시간 안에 여러 번 push가 들어오면, 앞선 실행은 이미 의미가 없어진 경우가 많습니다. `cancel-in-progress: true`는 이런 낭비를 줄여 줍니다.

## 이 코드에서 먼저 봐야 할 점

- `paths`는 무엇을 실행할지보다 무엇을 건너뛸지 명확하게 만듭니다.
- cron은 UTC이므로 로컬 시간으로 착각하면 안 됩니다.
- `cancel-in-progress`는 PR 푸시가 잦은 팀에서 특히 효과가 큽니다.

저는 트리거 설계에서 “정확한 시점”이라는 표현을 자주 씁니다. 빠른 실행만큼 중요한 것이 쓸데없는 실행을 줄이는 일이기 때문입니다.

## 자주 하는 실수 다섯 가지

1. 모든 트리거에서 같은 무거운 워크플로우를 실행합니다.
2. `schedule`을 로컬 시간 기준으로 적습니다.
3. `pull_request_target`을 가볍게 사용해 비밀값 노출 위험을 만듭니다.
4. `concurrency`를 빼서 중복 빌드가 대기열을 채웁니다.
5. `workflow_dispatch`를 만들어 놓고 누가 언제 어떻게 쓰는지 문서화하지 않습니다.

특히 세 번째는 보안 이슈와 직결되므로, “PR에서 secret도 써야 하니까” 같은 단순한 이유로 선택하면 위험합니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 트리거를 역할별로 분리합니다. PR은 빠른 체크, main push는 전체 테스트와 빌드, nightly cron은 오래 걸리는 통합 검증, workflow_dispatch는 배포와 롤백 같은 운영 절차에 연결합니다. 그러면 워크플로우 이름은 늘어나도 시스템은 오히려 더 읽기 쉬워집니다.

또 하나는 시간대 감각입니다. 글로벌 팀이거나 여러 리전에서 일한다면 cron은 항상 UTC 기준으로 사고하는 편이 낫습니다. 사람이 지역 시간을 암산하는 구조는 오래 못 갑니다.

## 체크리스트

- [ ] 경로 필터로 불필요한 실행을 줄였다.
- [ ] cron은 UTC 기준으로 적었다.
- [ ] `concurrency`를 설정했다.
- [ ] `workflow_dispatch` 입력과 사용 방법을 문서화했다.

## 연습 문제

1. `docs/`만 바뀌면 워크플로우가 실행되지 않도록 바꿔 보세요.
2. 한국 시간 오전 3시에 매일 실행되는 cron 표현식을 작성해 보세요.
3. `workflow_dispatch`에 배포 환경 선택 입력을 추가해 보세요.

## 트리거 조합 전략을 더 구체적으로 보겠습니다

실무에서는 하나의 워크플로우에 여러 트리거를 조합하는 경우가 많습니다. 각 조합이 어떤 효과를 내는지 표로 정리하겠습니다.

| 시나리오 | 트리거 조합 | 이유 |
| --- | --- | --- |
| PR 검증 | `pull_request` + `paths` | 변경된 코드만 검증, 비용 절감 |
| main 배포 | `push: branches: [main]` | 머지된 코드만 배포 대상 |
| 야간 전체 테스트 | `schedule` | 넓은 매트릭스를 비용 낮은 시간대에 실행 |
| 수동 롤백/배포 | `workflow_dispatch` | 긴급 상황에서 사람이 직접 제어 |
| 릴리스 발행 | `push: tags: ['v*']` | 태그 기반 버전 관리 |
| 다른 워크플로우 완료 후 | `workflow_run` | 빌드 완료 후 배포 시작 |

### push와 pull_request를 함께 쓸 때의 중복 실행 문제

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

이 설정에서 PR을 머지하면 `push` 이벤트도 함께 발생합니다. 즉, PR 머지 시점에 워크플로우가 두 번 실행될 수 있습니다. 이를 방지하는 일반적인 방법은 PR에서만 검증하고, push는 main 전용 작업(배포, 릴리스)에만 쓰는 것입니다.

```yaml
# 검증용 (PR만)
on:
  pull_request:

# 배포용 (main push만)
on:
  push:
    branches: [main]
```

파일을 분리하면 중복 실행 없이 각 시점에 적절한 작업만 돌릴 수 있습니다.

---

## paths 필터의 실전 활용

paths 필터는 비용 절감의 핵심 도구입니다. 문서만 바꿨는데 전체 빌드가 돌면 시간과 비용 모두 낭비입니다.

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
      - "requirements*.txt"
    paths-ignore:
      - "docs/**"
      - "*.md"
      - ".github/ISSUE_TEMPLATE/**"
```

`paths`와 `paths-ignore`는 동시에 사용할 수 없습니다. 둘 중 하나만 선택해야 합니다. 일반적으로 포함할 경로가 명확하면 `paths`를, 제외할 경로가 적으면 `paths-ignore`를 사용합니다.

paths 필터에서 자주 하는 실수는 의존성 파일을 빠뜨리는 것입니다. `requirements.txt`가 바뀌면 테스트 결과도 달라질 수 있으므로, 소스 코드뿐 아니라 의존성 선언 파일도 반드시 포함해야 합니다.

### 변경 감지 기반 조건부 실행

paths 필터로는 워크플로우 자체를 건너뛰지만, 잡 수준에서 더 세밀한 제어가 필요할 때는 `dorny/paths-filter` 같은 액션을 사용합니다.

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v6
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'src/api/**'
              - 'requirements*.txt'
            frontend:
              - 'src/web/**'
              - 'package.json'

  test-backend:
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest tests/api -q

  test-frontend:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm test
```

이 패턴은 모노레포에서 특히 유용합니다. 백엔드 코드만 바뀌면 프론트엔드 테스트를 건너뛰고, 그 반대도 마찬가지입니다.

---

## schedule 트리거 심화

cron 표현식은 UTC 기준입니다. 한국 시간(KST)은 UTC+9이므로, KST 새벽 2시에 실행하려면 UTC 17시(전날)로 설정해야 합니다.

```yaml
on:
  schedule:
    # KST 새벽 2시 = UTC 17:00 (전날)
    - cron: "0 17 * * *"
    # 월요일~금요일만 (주말 제외)
    - cron: "0 17 * * 1-5"
```

schedule 트리거의 주의점을 정리하겠습니다.

1. **정확한 시각을 보장하지 않습니다.** GitHub은 부하에 따라 최대 수십 분 지연될 수 있습니다. 정확한 시각이 중요하다면 외부 스케줄러에서 `workflow_dispatch`를 호출하는 편이 낫습니다.
2. **기본 브랜치에서만 실행됩니다.** feature 브랜치의 schedule은 무시됩니다.
3. **60일 이상 커밋이 없으면 비활성화됩니다.** 오래된 저장소에서 schedule이 멈추는 이유가 이것입니다.
4. **여러 cron 표현식을 배열로 쓸 수 있습니다.** 야간 전체 테스트와 주간 의존성 검사를 같은 워크플로우에 둘 수 있습니다.

### schedule 활용 패턴

```yaml
on:
  schedule:
    - cron: "0 17 * * 1-5"  # 평일 KST 02:00 - 전체 매트릭스 테스트
    - cron: "0 9 * * 1"     # 월요일 KST 18:00 - 의존성 취약점 스캔

jobs:
  nightly-test:
    if: github.event.schedule == '0 17 * * 1-5'
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest -q

  security-scan:
    if: github.event.schedule == '0 9 * * 1'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pip-audit
```

`github.event.schedule`로 어떤 cron이 트리거했는지 구분해서 다른 잡을 실행할 수 있습니다.

---

## workflow_dispatch 설계 가이드

수동 트리거는 "자동화할 수 없는 상황"이 아니라 "사람의 판단이 필요한 시점"에 사용합니다. 롤백, 긴급 배포, 특정 환경 초기화 같은 작업이 대표적입니다.

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "배포 대상 환경"
        required: true
        type: choice
        options:
          - staging
          - production
      version:
        description: "배포할 버전 태그 (예: v1.2.3)"
        required: true
        type: string
      dry-run:
        description: "실제 배포 없이 검증만 실행"
        required: false
        type: boolean
        default: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ inputs.version }}
      - name: 검증
        run: ./scripts/validate.sh ${{ inputs.environment }}
      - name: 배포
        if: inputs.dry-run == false
        run: ./scripts/deploy.sh ${{ inputs.environment }} ${{ inputs.version }}
```

input 설계 시 지켜야 할 원칙입니다.

- **`choice` 타입으로 선택지를 제한합니다.** 자유 입력은 실수를 유발하므로, 가능하면 정해진 값 중에서 고르게 합니다.
- **`dry-run` 옵션을 기본값으로 둡니다.** 실수로 프로덕션 배포가 실행되는 사고를 막아 줍니다.
- **description에 예시를 포함합니다.** UI에서 바로 보이므로 문서를 찾아보지 않아도 됩니다.

---

## 이벤트 컨텍스트 활용

각 트리거는 `github.event` 객체에 고유한 정보를 담아 줍니다. 이를 활용하면 같은 워크플로우에서도 트리거 종류에 따라 다르게 동작할 수 있습니다.

```yaml
jobs:
  info:
    runs-on: ubuntu-latest
    steps:
      - name: 이벤트 정보 출력
        run: |
          echo "event: ${{ github.event_name }}"
          echo "action: ${{ github.event.action }}"
          echo "sender: ${{ github.event.sender.login }}"

      - name: PR 전용 정보
        if: github.event_name == 'pull_request'
        run: |
          echo "PR number: ${{ github.event.pull_request.number }}"
          echo "PR title: ${{ github.event.pull_request.title }}"
          echo "base branch: ${{ github.event.pull_request.base.ref }}"
          echo "head branch: ${{ github.event.pull_request.head.ref }}"
```

이 컨텍스트를 조건문에 활용하면 한 워크플로우에서 여러 시나리오를 처리할 수 있습니다. 다만 너무 많은 분기를 한 파일에 넣으면 읽기 어려워지므로, 복잡도가 올라가면 파일을 분리하는 편이 낫습니다.

---

## concurrency 설정의 실전 패턴

앞에서 `concurrency`를 간단히 언급했지만, 트리거 설계와 함께 고려해야 하는 중요한 요소이므로 더 깊이 다루겠습니다.

```yaml
# 패턴 1: PR 단위 직렬화
concurrency:
  group: pr-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

# 패턴 2: 환경별 직렬화 (배포용)
concurrency:
  group: deploy-${{ inputs.environment || 'staging' }}
  cancel-in-progress: false
```

`cancel-in-progress`의 선택 기준은 명확합니다.

- **검증 워크플로우**: `true` — 새 push가 왔으면 이전 결과는 의미 없습니다.
- **배포 워크플로우**: `false` — 진행 중인 배포를 취소하면 불완전한 상태가 될 수 있습니다.

group 키 설계도 중요합니다. PR 번호를 포함하면 서로 다른 PR은 독립적으로 실행되면서, 같은 PR 내에서만 직렬화됩니다. `github.ref`만 쓰면 같은 브랜치의 모든 실행이 직렬화됩니다.

---

## 트리거 관련 보안 고려사항

트리거 선택은 보안과 직결됩니다. 특히 fork에서 오는 PR을 처리할 때 주의할 점을 정리하겠습니다.

| 이벤트 | secret 접근 | 위험도 | 사용 지침 |
| --- | --- | --- | --- |
| `pull_request` | 불가 (fork) | 낮음 | 기본 검증용으로 안전 |
| `pull_request_target` | 가능 | 높음 | 신뢰할 수 없는 코드 실행 금지 |
| `push` | 가능 | 중간 | 보호 브랜치만 사용 |
| `workflow_dispatch` | 가능 | 낮음 | 권한 있는 사용자만 실행 |

`pull_request_target`은 base 브랜치의 워크플로우를 실행하면서 secret에 접근할 수 있어, fork에서 악의적인 코드가 secret을 탈취할 수 있는 공격 벡터가 됩니다. 꼭 필요한 경우(라벨링, 코멘트 등)에만 사용하고, PR의 코드를 checkout하거나 실행하지 않아야 합니다.

---

## 트리거 디버깅 기법

워크플로우가 예상대로 트리거되지 않을 때 확인해야 할 체크리스트입니다.

1. **워크플로우 파일이 기본 브랜치에 있는가?** `schedule`과 `workflow_dispatch`는 기본 브랜치의 워크플로우만 인식합니다. feature 브랜치에서 새 워크플로우를 추가하면 해당 브랜치에서는 `pull_request` 트리거만 동작합니다.

2. **YAML 문법이 올바른가?** `on:` 키 아래의 들여쓰기가 잘못되면 전체 워크플로우가 무시됩니다. GitHub UI의 "Workflow file" 탭에서 구문 오류를 확인할 수 있습니다.

3. **paths 필터가 올바르게 동작하는가?** paths 필터가 있을 때 변경 파일이 필터에 매칭되지 않으면 워크플로우가 "skipped" 상태로 나타납니다. 이는 정상 동작이며, branch protection에서 "Require status checks"를 사용한다면 skipped 상태의 처리 방식을 확인해야 합니다.

4. **이벤트 payload를 확인했는가?** `github.event`의 구조는 이벤트마다 다릅니다. 조건문이 예상대로 동작하지 않으면 payload를 출력해서 실제 값을 확인합니다.

```yaml
- name: 이벤트 payload 전체 출력
  run: echo '${{ toJSON(github.event) }}' | jq .
```

5. **Activity type을 확인했는가?** `pull_request`는 기본적으로 `opened`, `synchronize`, `reopened`에서만 트리거됩니다. 라벨 추가나 리뷰 요청 시에도 실행하려면 `types:`를 명시해야 합니다.

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, review_requested]
```

---

## 실무에서 자주 쓰는 트리거 조합 레시피

### 레시피 1: PR 검증 + main 배포 분리

```yaml
# .github/workflows/ci.yml
on:
  pull_request:
    paths: ["src/**", "tests/**", "pyproject.toml"]

# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
    paths: ["src/**"]
```

### 레시피 2: 태그 기반 릴리스

```yaml
on:
  push:
    tags: ["v[0-9]+.[0-9]+.[0-9]+"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
      - uses: softprops/action-gh-release@v2
        with:
          files: dist/*
          generate_release_notes: true
```

### 레시피 3: 의존성 자동 업데이트 + 자동 머지

```yaml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  auto-merge-dependabot:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v6
      - run: pytest -q
      - uses: fastify/github-action-merge-dependabot@v3
        with:
          target: minor
```

이 레시피들은 그대로 복사해서 쓸 수 있는 출발점입니다. 팀 상황에 맞게 paths 필터와 조건문을 조정하면 됩니다.

## 정리

트리거는 워크플로우의 시작 시점을 정하는 기능이지만, 실제로는 비용과 신뢰를 함께 설계하는 장치입니다. 언제 실행할지뿐 아니라 언제 실행하지 않을지까지 분명히 정해야 좋은 자동화가 됩니다.

다음 글에서는 Python 테스트 자동화를 다룹니다. 적절한 시점에 워크플로우를 깨우는 법을 이해했다면, 이제 그 안에서 어떤 테스트를 어떻게 돌릴지 구체화할 차례입니다.

---

## 처음 질문으로 돌아가기

- **push와 pull_request는 어떤 차이로 써야 할까요?**
  - `pull_request`는 코드 검증용입니다. PR이 열리거나 업데이트될 때 실행되며, fork에서는 secret이 차단되므로 안전합니다. `push`는 머지된 코드에 대한 후속 작업(배포, 릴리스)에 적합합니다. 두 이벤트를 같은 워크플로우에 넣으면 머지 시점에 중복 실행될 수 있으므로, 파일을 분리하거나 조건문으로 구분하는 편이 좋습니다.
- **schedule은 왜 로컬 시간이 아니라 UTC로 이해해야 할까요?**
  - GitHub Actions의 cron은 UTC 고정입니다. KST 새벽 2시에 돌리려면 UTC 17시로 설정해야 하고, 서머타임이 있는 지역에서는 연중 시각이 바뀌는 점도 고려해야 합니다. 또한 정확한 시각을 보장하지 않으므로, 분 단위 정확도가 필요하면 외부 스케줄러에서 `workflow_dispatch`를 호출하는 구조가 더 안정적입니다.
- **workflow_dispatch는 언제 유용하고 무엇을 문서화해야 할까요?**
  - 긴급 배포, 롤백, 환경 초기화처럼 사람의 판단이 필요한 시점에 유용합니다. input의 `description`에 예시와 제약 조건을 적고, `choice` 타입과 `dry-run` 기본값으로 실수를 방지하며, 누가 언제 실행했는지 감사 로그에 남는다는 점을 팀에 공유해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- **Trigger 이해하기 (현재 글)**
- Python 테스트 자동화 (예정)
- Lint와 Type Check (예정)
- 빌드 아티팩트 (예정)
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [Events that trigger workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)
- [Schedule events](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
- [workflow_dispatch](https://docs.github.com/actions/using-workflows/manually-running-a-workflow)
- [Concurrency](https://docs.github.com/actions/using-jobs/using-concurrency)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Trigger, Event, Schedule, CICD
