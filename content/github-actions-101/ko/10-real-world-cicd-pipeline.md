---
series: github-actions-101
episode: 10
title: "GitHub Actions 101 (10/10): 실전 CI/CD 파이프라인"
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
  - Pipeline
  - CICD
  - Capstone
  - ReusableWorkflow
seo_description: PR, main, tag를 분리한 실전 GitHub Actions CI/CD 파이프라인을 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (10/10): 실전 CI/CD 파이프라인

지금까지 한 편씩 나눠서 본 요소들은 각각 유용합니다. 하지만 실무에서는 trigger만 따로 존재하지 않고, 테스트만 따로 돌지 않으며, Docker 빌드와 배포와 secret 관리가 결국 하나의 흐름으로 엮입니다. 파이프라인이란 부품의 개수가 아니라, 그 부품들이 어떤 책임으로 연결돼 있는가를 설명하는 구조입니다.

이 글은 GitHub Actions 101 시리즈의 마지막 글입니다. 여기서는 앞선 아홉 편의 내용을 하나의 실전 파이프라인으로 묶고, PR, main, tag를 서로 다른 단계로 분리하는 방법과 reusable workflow, composite action을 어떻게 활용할지 정리하겠습니다.


![GitHub Actions 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/10/10-01-diagram.ko.png)
*GitHub Actions 101 10장 흐름 개요*

## 먼저 던지는 질문

- PR, main, tag를 왜 서로 다른 책임으로 나눠야 할까요?
- reusable workflow는 어떤 중복을 줄여 줄까요?
- composite action은 어디까지 묶는 편이 좋을까요?

## 왜 중요한가

테스트 자동화, 린트, Docker 빌드, 배포 자동화, secret 관리가 각각 있어도 연결이 나쁘면 팀 속도는 기대만큼 올라가지 않습니다. PR마다 너무 무거운 검증이 돌아서 피드백이 늦고, main push에도 production과 같은 수준의 배포가 붙고, 저장소마다 비슷하지만 다른 YAML이 흩어져 있다면 유지비가 계속 올라갑니다.

저는 실전 CI/CD 파이프라인의 목적을 “한 번 잘 만든 구조를 여러 저장소에서 오래 재사용하는 것”으로 봅니다. 부품을 많이 쌓는 것보다 책임을 잘 나누고 공통 부분을 재사용 가능하게 만드는 편이 훨씬 큰 효과를 냅니다.

## 한눈에 보는 전체 파이프라인

이 구조에서 중요한 것은 세 단계가 동일한 무게를 갖지 않는다는 점입니다. PR은 빠른 피드백이 중요하고, main은 통합과 staging 반영이 중요하며, tag는 공식 릴리스와 production 승격이 중요합니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| reusable workflow | `workflow_call`로 호출하는 공통 워크플로 | 저장소 간 중복을 크게 줄여 줍니다 |
| composite action | 여러 스텝을 하나의 재사용 단위로 묶은 액션 | 반복되는 준비 작업 정리에 유리합니다 |
| template repo | 팀이 공통 시작점으로 쓰는 저장소 | 표준 CI/CD 골격을 배포하기 좋습니다 |
| DORA 지표 | 배포 성과를 보는 네 가지 핵심 지표 | 파이프라인 설계 품질과 직접 연결됩니다 |
| 승격 | staging에서 production으로 넘기는 과정 | 같은 산출물을 다음 환경으로 올리는 감각이 중요합니다 |

## 자동화 전과 후를 비교해 보겠습니다

저장소마다 비슷하지만 조금씩 다른 워크플로우를 갖고 있으면, 한곳에서 개선한 내용을 다른 저장소에 다시 반영하는 비용이 큽니다. 어떤 저장소는 lint 규칙이 다르고, 어떤 저장소는 Docker 빌드 캐시가 빠지고, 어떤 저장소는 production 배포 게이트가 없습니다. 이런 상태는 시간이 갈수록 표류를 만듭니다.

반대로 공통 reusable workflow를 만들고 각 저장소는 얇은 호출자만 두면 구조가 단순해집니다. 공통 규칙은 한곳에서 관리하고, 저장소별 차이만 입력값으로 남기면 됩니다. 플랫폼 팀이 이 패턴을 좋아하는 이유가 분명합니다.

## 실전 파이프라인을 5단계로 구성해 보겠습니다

### 1단계 — reusable workflow 정의하기

```yaml
# .github/workflows/_ci.yml in org/template-repo
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.12"
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ inputs.python-version }}
      - run: pip install -e ".[dev]"
      - run: ruff check . && mypy . && pytest -q
```

공통 규칙이 반복된다면 복사보다 호출이 낫습니다. reusable workflow는 이런 중복 제거에 가장 직접적인 도구입니다.

### 2단계 — PR 단계는 빠른 피드백에 집중하기

```yaml
# .github/workflows/pr.yml
on:
  pull_request:
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
    with:
      python-version: "3.12"
```

PR에서는 lint, test, typecheck처럼 빠른 피드백 위주의 검증이 핵심입니다. 여기서 배포까지 한꺼번에 붙이면 리뷰 리듬이 무거워집니다.

### 3단계 — main 단계는 통합과 staging으로 이어지게 하기

```yaml
on:
  push:
    branches: [main]
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
  docker:
    needs: ci
    uses: org/template-repo/.github/workflows/_docker.yml@v1
  deploy-staging:
    needs: docker
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/staging/
```

main push는 이미 머지된 코드 기준이므로, 여기서는 빌드와 Docker 이미지 생성, staging 배포까지 자연스럽게 이어질 수 있습니다.

### 4단계 — tag 단계는 공식 릴리스와 production으로 묶기

```yaml
on:
  push:
    tags: ["v*"]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: softprops/action-gh-release@v2
  deploy-prod:
    needs: release
    environment: production  # required reviewers ON
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/production/
```

tag를 production 승격의 기준으로 삼으면 어떤 버전이 나갔는지 추적이 쉬워집니다. production은 가능한 한 태그나 명확한 버전과 연결하는 편이 좋습니다.

### 5단계 — 반복 준비 작업은 composite action으로 묶기

```yaml
# .github/actions/setup-app/action.yml
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v6
      with: { python-version: "3.12" }
    - run: pip install -e ".[dev]"
      shell: bash
```

reusable workflow가 잡 단위 재사용이라면, composite action은 스텝 단위 재사용에 가깝습니다. 둘의 역할을 구분해 쓰면 구조가 더 깔끔해집니다.

## 여기까지 했을 때 기대할 결과

| 트리거 | 기대하는 실행 | 머지/배포 판단 기준 |
| --- | --- | --- |
| PR | lint, test, typecheck | 빠른 피드백이 5분 안쪽에 돌아오는가 |
| main push | build, docker, staging | 검증한 산출물이 staging까지 동일하게 이어지는가 |
| tag push | release, production | 승인 후 같은 버전이 production으로 승격되는가 |

이 표가 실제 실행 로그와 맞아떨어지면 파이프라인 책임 분리가 잘 된 것입니다. 반대로 PR에서 production 직전 검증까지 전부 돈다면 구조를 다시 쪼개야 할 신호로 보는 편이 맞습니다.

## 운영 중 문제가 생기면 이런 순서로 좁힙니다

1. **PR 단계가 느리다**: reusable workflow 안에서 꼭 필요한 검사만 남았는지, matrix가 과한지부터 봅니다.
2. **main 단계가 흔들린다**: build 결과물과 Docker 이미지 태그가 staging에 동일하게 전달되는지 확인합니다.
3. **production 배포가 불안하다**: tag 기준 승격인지, required reviewers와 rollback workflow가 실제로 살아 있는지 점검합니다.

## 브랜치 보호와 승격 정책이 파이프라인의 절반입니다

실전에서는 YAML 자체보다 branch protection과 environment protection이 더 중요할 때가 많습니다. PR에는 status check 강제, main에는 직접 push 제한, production에는 승인 게이트와 환경별 secret 분리를 함께 걸어야 합니다. 파이프라인 파일만 좋아 보여도 저장소 정책이 비어 있으면 운영 품질은 쉽게 무너집니다.

## 이 코드에서 먼저 봐야 할 점

- PR은 피드백, main은 통합, tag는 릴리스라는 책임 분리가 선명합니다.
- reusable workflow는 버전 핀으로 호출해야 상위 변경이 갑자기 깨지지 않습니다.
- production environment는 최종 게이트 역할을 합니다.

이 세 가지가 명확하면 파이프라인이 커져도 읽는 기준이 흔들리지 않습니다.

## 자주 하는 실수 다섯 가지

1. 모든 PR에서 전체 e2e와 배포 직전 검증까지 돌립니다.
2. main에서 바로 production으로 직행합니다.
3. reusable workflow를 `@main`으로 호출합니다.
4. 태그 없이 production 배포를 진행합니다.
5. composite action 입력 검증 없이 값을 그대로 흘려보냅니다.

특히 세 번째 실수는 조용히 큰 문제를 만듭니다. 상위 저장소의 변경이 아무 예고 없이 모든 하위 저장소를 흔들 수 있기 때문입니다.

## 실무에서는 이렇게 생각합니다

플랫폼 팀은 공통 템플릿 저장소를 통해 조직 전체의 CI/CD 골격을 배포합니다. 서비스 팀은 그 위에서 필요한 입력만 바꾸고, 공통 정책은 중앙에서 관리합니다. 이 방식은 YAML 복붙보다 초기 비용이 커 보여도 장기 유지비를 크게 줄여 줍니다.

또한 DORA 지표를 개선하려면 무조건 더 많은 단계를 넣는 것이 아니라, 어떤 트리거에 어떤 책임을 둘지 명확히 나누는 편이 더 중요합니다. 빠른 PR 피드백, 안정적인 main 통합, 추적 가능한 production 배포가 그 핵심입니다.

## 체크리스트

- [ ] PR, main, tag 단계가 분리돼 있다.
- [ ] 공통 검증을 reusable workflow로 추출했다.
- [ ] production에는 승인 게이트가 있다.
- [ ] reusable workflow 호출 버전을 고정했다.

## 연습 문제

1. lint, test, typecheck만 도는 PR 전용 워크플로우를 작성해 보세요.
2. 두 저장소에서 공통으로 호출하는 reusable workflow를 만들어 보세요.
3. tag push 후 승인 게이트를 거쳐 production에 배포되는 흐름을 구성해 보세요.

## 정리

실전 CI/CD 파이프라인은 부품을 많이 붙이는 작업이 아니라, 책임을 분명히 나눈 작은 흐름들을 조합하는 작업입니다. PR, main, tag를 서로 다른 단계로 보고, 공통 부분은 reusable workflow와 composite action으로 묶으면 파이프라인은 더 단순해지고 조직 전체 표준화도 쉬워집니다.

이 시리즈를 끝까지 따라왔다면 대부분의 실무 GitHub Actions 구조를 읽고 직접 설계할 수 있는 기반을 갖춘 셈입니다. 다음 단계에서는 Docker, Kubernetes, 운영 자동화처럼 런타임과 배포 이후의 영역으로 시야를 넓혀 가면 좋습니다.


---

## 실전 파이프라인 전체 아키텍처

지금까지 배운 모든 요소를 하나의 프로젝트에 적용한 전체 파이프라인 구조입니다.

```text
.github/workflows/
├── ci.yml              # PR 검증 (lint + typecheck + test)
├── build.yml           # main push 시 빌드 + Docker + 아티팩트
├── deploy-staging.yml  # main push → staging 자동 배포
├── deploy-prod.yml     # tag push → production 승인 배포
├── nightly.yml         # 야간 전체 매트릭스 + 보안 스캔
└── reusable/
    ├── test.yml        # 재사용 가능 테스트 워크플로우
    └── docker.yml      # 재사용 가능 Docker 빌드
```

각 파일의 책임이 한 문장으로 설명 가능해야 합니다. 한 파일에 여러 책임을 넣으면 "이 파일은 언제 수정해야 하지?"라는 질문에 답하기 어려워집니다.

### PR 검증 워크플로우 (ci.yml)

```yaml
name: ci
on:
  pull_request:
    paths: ["src/**", "tests/**", "pyproject.toml", "Dockerfile"]

concurrency:
  group: ci-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  lint:
    uses: ./.github/workflows/reusable/test.yml
    with:
      command: "ruff check --output-format github && ruff format --check"

  typecheck:
    uses: ./.github/workflows/reusable/test.yml
    with:
      command: "mypy src"

  test:
    uses: ./.github/workflows/reusable/test.yml
    with:
      command: "pytest -q -n auto --cov=src"
      python-versions: '["3.11", "3.12"]'

  docker-check:
    uses: ./.github/workflows/reusable/docker.yml
    with:
      push: false
```

모든 검증이 병렬로 실행되므로, 가장 느린 잡이 전체 시간을 결정합니다.

### 빌드 + 배포 워크플로우 (build.yml + deploy-staging.yml)

```yaml
# build.yml
name: build
on:
  push:
    branches: [main]
    paths: ["src/**", "Dockerfile", "pyproject.toml"]

jobs:
  build:
    uses: ./.github/workflows/reusable/docker.yml
    with:
      push: true
      tags: |
        ghcr.io/${{ github.repository }}:main
        ghcr.io/${{ github.repository }}:${{ github.sha }}
    permissions:
      packages: write

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - run: ./scripts/deploy.sh staging ${{ github.sha }}
```

---

## Reusable Workflow 설계 패턴

재사용 가능 워크플로우는 "조직 표준"을 코드로 만드는 도구입니다.

```yaml
# .github/workflows/reusable/test.yml
name: reusable-test
on:
  workflow_call:
    inputs:
      command:
        required: true
        type: string
      python-versions:
        required: false
        type: string
        default: '["3.12"]'
      working-directory:
        required: false
        type: string
        default: "."

jobs:
  run:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ${{ fromJSON(inputs.python-versions) }}
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: ${{ inputs.command }}
```

이 워크플로우를 호출하는 쪽은 실행할 명령만 전달하면 됩니다. Python 설치, 캐시, 의존성 설치는 한 곳에서 관리되므로, 업데이트할 때 모든 호출처가 자동으로 반영됩니다.

### Reusable Workflow의 제약과 대안

| 제약 | 설명 | 대안 |
| --- | --- | --- |
| 중첩 호출 불가 | reusable에서 다른 reusable 호출 불가 | composite action 조합 |
| secrets 전달 필요 | `secrets: inherit` 또는 명시적 전달 | `secrets: inherit` 사용 |
| 잡 수준에서만 호출 | 스텝 수준 재사용 불가 | composite action 사용 |
| 같은 저장소 또는 public만 | private 다른 저장소 불가 | 조직 internal 가시성 |

---

## Composite Action 설계

스텝 수준의 재사용이 필요하면 composite action을 사용합니다.

```yaml
# .github/actions/setup-project/action.yml
name: "Setup Project"
description: "Python 프로젝트 공통 설정"

inputs:
  python-version:
    description: "Python 버전"
    required: false
    default: "3.12"

runs:
  using: "composite"
  steps:
    - uses: actions/setup-python@v6
      with:
        python-version: ${{ inputs.python-version }}
        cache: "pip"

    - name: 의존성 설치
      shell: bash
      run: pip install -e ".[dev]"

    - name: 환경 확인
      shell: bash
      run: |
        python --version
        pip --version
```

호출하는 쪽에서는 한 줄로 프로젝트 설정이 완료됩니다.

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: ./.github/actions/setup-project
    with:
      python-version: "3.11"
  - run: pytest -q
```

---

## 파이프라인 성능 모니터링

파이프라인이 느려지면 개발자가 CI를 무시하기 시작합니다. 실행 시간을 주기적으로 확인하는 방법입니다.

```yaml
name: ci-metrics
on:
  schedule:
    - cron: "0 9 * * 1"  # 매주 월요일

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - name: 최근 실행 시간 수집
        run: |
          gh api repos/${{ github.repository }}/actions/runs \
            --jq '.workflow_runs[:20] | .[] | [.name, .updated_at, .run_started_at] | @tsv' \
            > metrics.txt
          
          echo "## CI Performance Report" > report.md
          echo "최근 20회 실행:" >> report.md
          cat metrics.txt >> report.md

      - uses: actions/upload-artifact@v7
        with:
          name: ci-metrics
          path: report.md
          retention-days: 90
```

DORA 메트릭(배포 빈도, 변경 리드타임, 실패율, 복구 시간) 관점에서 파이프라인을 평가하면 개선 방향이 명확해집니다.

| DORA 메트릭 | 측정 대상 | 목표 |
| --- | --- | --- |
| 배포 빈도 | main → production 배포 횟수 | 일 1회 이상 |
| 변경 리드타임 | 커밋 → production 배포까지 시간 | 1시간 이내 |
| 변경 실패율 | 배포 후 롤백/핫픽스 비율 | 5% 미만 |
| 복구 시간 | 장애 발생 → 복구까지 시간 | 1시간 이내 |

---

## 조직 수준 표준화

여러 저장소에서 동일한 CI/CD 패턴을 사용한다면 조직 수준에서 표준화하는 방법을 고려합니다.

### Template Repository

```text
org/ci-template/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── deploy.yml
│   │   └── reusable/
│   │       └── test.yml
│   └── actions/
│       └── setup-project/
│           └── action.yml
├── pyproject.toml (template)
├── Dockerfile (template)
└── scripts/
    └── deploy.sh
```

새 저장소를 만들 때 이 template에서 시작하면 CI/CD가 즉시 동작합니다.

### Centralized Reusable Workflows

```yaml
# 다른 저장소에서 조직의 공용 워크플로우 호출
jobs:
  test:
    uses: org/ci-workflows/.github/workflows/python-test.yml@v1
    with:
      python-version: "3.12"
    secrets: inherit
```

조직의 공용 저장소에 reusable workflow를 두면 모든 저장소에서 `@v1` 태그로 호출할 수 있습니다. 워크플로우 업데이트는 태그를 올리면 되고, 각 저장소는 준비될 때 버전을 올립니다.


### 조직 정책을 코드로 관리하기

GitHub Organization 설정에서 Actions 권한을 제어하면 보안 사고를 사전에 방지합니다.

```yaml
# org-level .github/workflows/policy-check.yml
name: Policy Compliance
on:
  workflow_run:
    workflows: ["*"]
    types: [completed]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Verify approved actions only
        run: |
          # 승인된 action 목록
          ALLOWED="actions/checkout actions/setup-python actions/upload-artifact"
          ALLOWED="$ALLOWED docker/build-push-action aws-actions/configure-aws-credentials"

          # 워크플로우 파일에서 uses: 구문 추출
          for wf in .github/workflows/*.yml; do
            grep -oP 'uses:\s*\K[^@]+' "$wf" | while read action; do
              if ! echo "$ALLOWED" | grep -q "$action"; then
                echo "::error::Unapproved action: $action in $wf"
                exit 1
              fi
            done
          done

      - name: Check secret naming convention
        run: |
          # secret 이름이 ENV_SERVICE_KEY 패턴을 따르는지 검증
          gh secret list --json name -q '.[].name' | while read name; do
            if ! echo "$name" | grep -qP '^(PROD|STG|DEV)_[A-Z_]+$'; then
              echo "::warning::Non-standard secret name: $name"
            fi
          done
        env:
          GH_TOKEN: ${{ secrets.ORG_ADMIN_TOKEN }}
```

이 정책 워크플로우가 있으면 팀원이 승인되지 않은 third-party action을 추가하거나 비표준 secret 이름을 사용할 때 즉시 경고가 발생합니다.

### 비용 최적화

GitHub Actions의 무료 할당량(public repo: 무제한, private repo: 월 2,000분)을 넘기면 분당 과금됩니다. 비용을 줄이는 실전 패턴입니다.

| 기법 | 절감 효과 | 적용 방법 |
|------|-----------|-----------|
| Path filter | 불필요 실행 제거 | `paths:` + `paths-ignore:` |
| Concurrency cancel | 중복 실행 제거 | `concurrency.cancel-in-progress: true` |
| Dependency cache | 설치 시간 단축 | `actions/cache` 또는 `setup-*`의 cache 옵션 |
| Self-hosted runner | 분당 과금 회피 | EC2 spot instance + runner 등록 |
| Matrix 최적화 | 조합 축소 | `include`/`exclude`로 필수 조합만 |

```yaml
# 비용 최적화가 적용된 워크플로우 헤더
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

이렇게 설정하면 문서만 변경한 커밋에서는 CI가 실행되지 않고, 같은 브랜치에 빠르게 연속 푸시하면 이전 실행이 취소됩니다.


## 처음 질문으로 돌아가기

- **PR, main, tag를 왜 서로 다른 책임으로 나눠야 할까요?**
  - PR은 "이 코드가 안전한가"를 검증하는 단계이고, main push는 "검증된 코드를 빌드하고 staging에 배포"하는 단계이며, tag push는 "프로덕션 릴리스"를 의미합니다. 각 단계에서 필요한 권한, 시크릿, 실행 범위가 다르므로 워크플로우 파일을 분리해야 책임이 명확해지고 보안도 강화됩니다.
- **reusable workflow는 어떤 중복을 줄여 줄까요?**
  - Python 설치, 캐시 설정, 의존성 설치, Docker 빌드 같은 공통 단계를 한 번 정의하고 여러 워크플로우에서 호출합니다. 업데이트할 때 한 곳만 고치면 모든 호출처에 반영되므로, "이 저장소의 setup은 왜 다른 저장소와 다르지?"라는 drift를 방지합니다. 조직 수준에서는 여러 저장소의 CI 표준을 하나의 공용 워크플로우로 통일할 수 있습니다.
- **composite action은 어디까지 묶는 편이 좋을까요?**
  - "이 스텝 조합이 항상 함께 실행되고, 여러 잡/워크플로우에서 반복된다"면 composite action 후보입니다. 프로젝트 설정(checkout + setup + install), 알림 전송, 캐시 복원 + 빌드 같은 패턴이 대표적입니다. 너무 많은 기능을 하나에 넣으면 input이 복잡해지므로, "한 문장으로 설명 가능한 단위"를 기준으로 잡는 편이 좋습니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint와 Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): 빌드 아티팩트](./06-build-artifact.md)
- [GitHub Actions 101 (7/10): Docker 빌드](./07-docker-build.md)
- [GitHub Actions 101 (8/10): 배포 자동화](./08-deploy-automation.md)
- [GitHub Actions 101 (9/10): Secret 관리](./09-secret-management.md)
- **실전 CI/CD 파이프라인 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Reusing workflows](https://docs.github.com/actions/using-workflows/reusing-workflows)
- [Creating a composite action](https://docs.github.com/actions/creating-actions/creating-a-composite-action)
- [DORA - Accelerate State of DevOps](https://dora.dev/)
- [Creating a template repository](https://docs.github.com/repositories/creating-and-managing-repositories/creating-a-template-repository)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Pipeline, CICD, Capstone, ReusableWorkflow
