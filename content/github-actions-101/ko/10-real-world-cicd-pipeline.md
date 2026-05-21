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

## 먼저 던지는 질문

- PR, main, tag를 왜 서로 다른 책임으로 나눠야 할까요?
- reusable workflow는 어떤 중복을 줄여 줄까요?
- composite action은 어디까지 묶는 편이 좋을까요?

## 큰 그림

![GitHub Actions 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/10/10-01-diagram.ko.png)

*GitHub Actions 101 10장 흐름 개요*

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

## 처음 질문으로 돌아가기

- **PR, main, tag를 왜 서로 다른 책임으로 나눠야 할까요?**
  - 본문의 기준은 실전 CI/CD 파이프라인를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **reusable workflow는 어떤 중복을 줄여 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **composite action은 어디까지 묶는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: GitHubActions, Pipeline, CICD, Capstone, ReusableWorkflow
