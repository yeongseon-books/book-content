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

## 먼저 던지는 질문

- push와 pull_request는 어떤 차이로 써야 할까요?
- schedule은 왜 로컬 시간이 아니라 UTC로 이해해야 할까요?
- workflow_dispatch는 언제 유용하고 무엇을 문서화해야 할까요?

## 큰 그림

![GitHub Actions 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/03/03-01-diagram.ko.png)

*GitHub Actions 101 3장 흐름 개요*

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

## 정리

트리거는 워크플로우의 시작 시점을 정하는 기능이지만, 실제로는 비용과 신뢰를 함께 설계하는 장치입니다. 언제 실행할지뿐 아니라 언제 실행하지 않을지까지 분명히 정해야 좋은 자동화가 됩니다.

다음 글에서는 Python 테스트 자동화를 다룹니다. 적절한 시점에 워크플로우를 깨우는 법을 이해했다면, 이제 그 안에서 어떤 테스트를 어떻게 돌릴지 구체화할 차례입니다.


## 워크플로 설계를 코드로 구체화하기

워크플로우 품질은 "한 번 돌아간다"가 아니라 "변경이 누적돼도 의도를 유지한다"로 판단해야 합니다. 아래 예시는 테스트, 린트, 빌드를 분리해 실패 지점을 빠르게 찾는 구성입니다.

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest -q

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pip install ruff
      - run: ruff check .

  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    steps:
      - uses: actions/checkout@v6
      - run: docker build -t app:${{ github.sha }} .
```

`needs`를 통해 의존 관계를 명시하면 "테스트 실패인데 빌드는 왜 돌았는가" 같은 혼선을 줄일 수 있습니다. 또한 잡을 분리하면 병렬 실행이 가능해 전체 피드백 시간이 짧아집니다.

## Job Matrix로 중복을 줄이기

동일한 작업을 여러 런타임에서 반복해야 한다면 matrix가 가장 실용적입니다. 아래 구성은 Python 버전과 운영체제를 조합해 호환성을 검증합니다.

```yaml
jobs:
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest -q
```

`fail-fast: false`를 켜면 한 조합이 실패해도 나머지 조합 결과를 끝까지 수집할 수 있습니다. 라이브러리 호환성 이슈를 찾는 단계에서는 이 설정이 원인 파악 속도를 높입니다.

## Secret 처리 원칙

비밀값은 YAML 본문에 직접 넣지 않고 GitHub Secrets나 OIDC 기반 임시 자격 증명을 사용해야 합니다. 고정 토큰을 코드에 넣으면 회전, 감사, 권한 축소가 모두 어려워집니다.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v6
      - name: Login to cloud with OIDC
        run: ./scripts/oidc-login.sh
      - name: Deploy
        env:
          API_BASE_URL: ${{ secrets.API_BASE_URL }}
        run: ./scripts/deploy.sh
```

실무에서는 다음 기준을 함께 둡니다.

- secret 이름은 목적 중심으로 명명해 누가 봐도 용도를 파악할 수 있게 합니다.
- PR from fork에서는 secret이 기본적으로 주입되지 않으므로, 배포 잡을 분리하거나 조건문으로 차단합니다.
- 로그에 비밀값이 노출되지 않도록 `set -x` 사용 구간을 제한하고, 민감 출력은 마스킹합니다.
- 회전 주기를 문서화하고, 사용하지 않는 secret은 즉시 폐기합니다.

## 운영 안정성을 높이는 추가 패턴

- `concurrency`를 사용해 같은 브랜치의 중복 배포를 자동 취소하면 롤백 리스크를 줄일 수 있습니다.
- 캐시 키는 잠금 파일(`poetry.lock`, `requirements.txt`) 해시와 연결해 오염된 캐시 재사용을 막습니다.
- 배포 잡은 `environment` 보호 규칙과 reviewer 승인을 함께 걸어 사고 범위를 줄입니다.
- 실패 알림은 채널 하나에 몰지 말고, 서비스 소유 팀 라우팅 기준으로 분리해야 대응 시간이 짧아집니다.

이 구조를 먼저 잡아 두면 워크플로 파일이 길어져도 책임 경계가 무너지지 않고, CI/CD 품질을 지속적으로 개선하기 쉬워집니다.


## 운영 체크포인트 보강

워크플로를 길게 쓰는 것보다 더 중요한 것은 실패 원인을 빠르게 고립하는 구조입니다. 테스트 잡에서는 의존성 설치 시간을 측정하고, 배포 잡에서는 릴리스 노트와 커밋 SHA를 함께 남겨 추적성을 확보해야 합니다. 또한 `if: github.event_name == "pull_request"` 같은 조건식을 사용해 PR 검증과 main 배포를 분리하면 권한 오남용과 불필요한 실행 시간을 동시에 줄일 수 있습니다.

```yaml
- name: Record build metadata
  run: |
    echo "sha=${GITHUB_SHA}" >> build-info.txt
    echo "ref=${GITHUB_REF}" >> build-info.txt
```

메타데이터 파일을 아티팩트로 보존해 두면 장애 회고에서 "어떤 실행 결과가 어느 커밋과 연결되는가"를 빠르게 확인할 수 있습니다.

## 처음 질문으로 돌아가기

- **push와 pull_request는 어떤 차이로 써야 할까요?**
  - 본문의 기준은 Trigger 이해하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **schedule은 왜 로컬 시간이 아니라 UTC로 이해해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **workflow_dispatch는 언제 유용하고 무엇을 문서화해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: GitHubActions, Trigger, Event, Schedule, CICD
