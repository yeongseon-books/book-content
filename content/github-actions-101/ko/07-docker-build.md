---
series: github-actions-101
episode: 7
title: "GitHub Actions 101 (7/10): Docker 빌드"
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
  - Docker
  - Buildx
  - GHCR
  - CICD
seo_description: Buildx, 캐시, 멀티 플랫폼, GHCR 푸시까지 Docker 빌드 표준을 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (7/10): Docker 빌드

GitHub Actions에서 시간이 가장 오래 걸리는 단계는 대개 Docker 빌드입니다. 캐시가 없으면 PR 하나 열 때마다 레이어를 처음부터 다시 만들고, 태그 전략이 없으면 어떤 이미지가 배포됐는지도 흐려지고, 권한 설정이 어긋나면 푸시 단계에서 401이 터집니다. 컨테이너 빌드는 단순히 `docker build`를 CI에 옮기는 작업이 아닙니다.

이 글은 GitHub Actions 101 시리즈의 7번째 글입니다. 여기서는 Buildx 기반의 Docker 빌드 흐름을 정리하고, 캐시, GHCR 푸시, 멀티 플랫폼 빌드, 권한 설정을 어떤 기준으로 가져가야 하는지 설명하겠습니다.

## 먼저 던지는 질문

- Buildx는 왜 일반 빌더보다 더 자주 쓰일까요?
- GitHub Actions 캐시는 Docker 레이어 시간에 어떤 영향을 줄까요?
- GHCR에 푸시할 때 어떤 권한이 필요할까요?

## 큰 그림

![GitHub Actions 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/07/07-01-docker.ko.png)

*GitHub Actions 101 7장 흐름 개요*

## 왜 중요한가

컨테이너 이미지는 배포의 경계선입니다. 애플리케이션 코드가 어떻든, 결국 배포는 이미지 단위로 일어나는 경우가 많습니다. 따라서 빌드가 느리거나 재현이 어렵다면 배포도 불안정해집니다.

또한 Docker 빌드는 CI 비용에 직접 영향을 줍니다. 매번 모든 레이어를 다시 만드는 파이프라인은 금방 느려지고, 개발자는 체크 결과를 기다리기 싫어집니다. 저는 Docker 빌드 자동화의 핵심을 “빠르게”보다 “예측 가능하게”에 둡니다. 캐시와 태그 전략이 있으면 그 예측 가능성이 생깁니다.

## 한눈에 보는 Docker 빌드 흐름

이 구조의 중심에는 `docker/build-push-action`이 있습니다. Dockerfile을 입력으로 받아 빌드하고, 캐시를 활용하고, 결과를 레지스트리에 올리는 역할을 한 번에 맡습니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| Buildx | Docker의 확장 빌더 | 캐시, 멀티 플랫폼, 고급 빌드 기능의 중심입니다 |
| gha cache | GitHub Actions 캐시 백엔드 | 레이어 재사용으로 빌드 시간을 줄입니다 |
| GHCR | GitHub Container Registry | GitHub 생태계 안에서 이미지 배포가 자연스럽습니다 |
| 멀티 플랫폼 | 여러 CPU 아키텍처용 이미지를 함께 만드는 방식 | 호환성을 넓히지만 비용이 늘어납니다 |
| OCI 이미지 | 표준 컨테이너 이미지 형식 | 다양한 런타임과 레지스트리에서 호환됩니다 |

## 자동화 전과 후를 비교해 보겠습니다

캐시 없는 빌드는 PR마다 모든 레이어를 다시 만듭니다. 의존성 설치, 시스템 패키지 설치, 애플리케이션 복사까지 전부 처음부터 반복되면 4분, 5분은 금방 지나갑니다. 이런 파이프라인은 조금만 저장소가 커져도 팀 전체의 대기 시간을 키웁니다.

반대로 Buildx와 `type=gha` 캐시를 붙이면, 바뀌지 않은 레이어는 그대로 재사용합니다. Dockerfile 구조까지 멀티 스테이지로 정리돼 있다면 빌드 시간은 크게 줄고, 이미지 크기도 함께 줄일 수 있습니다. 저는 Docker 빌드 자동화에서 이 두 가지를 항상 함께 봅니다.

## Docker 빌드를 5단계로 구성해 보겠습니다

### 1단계 — Buildx 준비하기

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
```

이 단계는 고급 빌드 기능의 기반을 깝니다. 특히 멀티 플랫폼을 고려한다면 QEMU와 Buildx 준비가 사실상 시작점입니다.

### 2단계 — GHCR에 로그인하기

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

이미지를 푸시하려면 인증이 필요합니다. GitHub 저장소와 레지스트리를 함께 쓸 때는 `GITHUB_TOKEN` 조합이 기본 출발점이 됩니다.

### 3단계 — 캐시를 포함해 빌드하고 푸시하기

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

여기서 중요한 점은 태그와 캐시를 함께 설계하는 것입니다. `github.sha` 태그는 추적성을 주고, `cache-from`과 `cache-to`는 빌드 시간을 줄여 줍니다.

### 4단계 — 멀티 플랫폼 이미지 만들기

```yaml
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
```

멀티 플랫폼은 편리하지만 공짜가 아닙니다. PR마다 항상 돌리기보다는 main push나 Release 시점처럼 꼭 필요한 순간에만 붙이는 편이 일반적입니다.

### 5단계 — 권한을 명시하기

```yaml
permissions:
  contents: read
  packages: write
```

이미지 푸시는 패키지 쓰기 권한이 필요합니다. 이 설정이 빠지면 빌드는 잘 됐는데 마지막 푸시에서 401로 실패하는 상황을 자주 보게 됩니다.

## 여기까지 했을 때 기대할 결과

```text
#17 [linux/amd64] exporting to image
#17 exporting manifest sha256:8f4c...
#17 naming to ghcr.io/acme/demo:4d2e9f1
#17 DONE 2.1s
```

위와 같이 digest와 태그가 함께 보이면 최소 기준은 통과한 것입니다. PR 검증 단계라면 `push: false` 상태에서도 캐시 적중률과 레이어 재사용 여부는 로그에서 바로 확인할 수 있습니다.

## 빌드가 실패하면 먼저 볼 세 가지

- **401 또는 permission denied**: `permissions: packages: write`가 빠졌거나, 대상 패키지에 대한 GHCR 권한이 정리되지 않은 경우가 많습니다.
- **캐시가 계속 비는 경우**: Dockerfile에서 자주 바뀌는 파일을 너무 앞단에 `COPY`하고 있는지 확인합니다. 레이어 순서가 캐시 효율을 크게 좌우합니다.
- **멀티 플랫폼 빌드만 느리거나 깨지는 경우**: PR에서는 amd64 단일 빌드만 돌리고, arm64는 main 또는 tag에서만 실행하는 편이 더 안정적입니다.

## 브랜치와 태그 정책은 따로 가져가는 편이 좋습니다

저는 보통 PR에서는 `push: false`로 이미지가 실제로 만들어지는지만 검증하고, main push에서는 `sha` 태그와 `latest`를 함께 푸시합니다. 정식 릴리스 태그가 붙을 때만 멀티 플랫폼 이미지와 서명까지 확장하는 식입니다. 이 구분이 있어야 리뷰 피드백 시간과 배포 추적성을 동시에 챙길 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `cache-to: type=gha,mode=max`는 레이어 재사용을 극대화합니다.
- 멀티 플랫폼 빌드는 편의만큼 비용도 늘립니다.
- `GITHUB_TOKEN`으로 푸시하려면 `packages: write` 권한이 필요합니다.

즉, Docker 빌드 자동화는 Dockerfile만의 문제가 아니라 권한, 캐시, 태그 정책이 함께 얽힌 설계 문제입니다.

## 자주 하는 실수 다섯 가지

1. Buildx 없이 기본 빌드만 사용합니다.
2. `permissions: packages: write`를 빼먹습니다.
3. `latest` 태그만 푸시해 롤백 기준을 잃습니다.
4. 모든 PR에서 멀티 플랫폼 빌드를 수행합니다.
5. 단일 스테이지 Dockerfile로 이미지 크기를 불필요하게 키웁니다.

특히 세 번째는 사고 후 추적성을 크게 떨어뜨립니다. 어떤 커밋의 이미지인지 분명한 고정 태그가 항상 함께 있어야 합니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 PR에서는 amd64와 캐시 중심의 빠른 검증만 하고, main push나 태그 푸시에서는 멀티 플랫폼 이미지와 서명까지 붙입니다. 즉, 모든 상황에서 같은 무게의 컨테이너 빌드를 돌리지 않습니다.

또한 `latest`는 편의 태그일 뿐 진실의 원천이 아니라는 감각이 중요합니다. 실제 배포 추적과 롤백은 보통 SHA나 버전 태그 같은 고정 식별자를 기준으로 해야 합니다.

## 체크리스트

- [ ] Buildx와 gha 캐시를 활성화했다.
- [ ] 고정 태그와 `latest`를 함께 관리한다.
- [ ] `packages: write` 권한을 명시했다.
- [ ] 멀티 플랫폼 빌드는 필요한 트리거에서만 실행한다.

## 연습 문제

1. PR에서는 amd64만 빌드하게 구성해 보세요.
2. main push에서는 멀티 플랫폼과 `latest` 태그를 함께 푸시해 보세요.
3. Dockerfile을 멀티 스테이지로 바꿔 이미지 크기를 줄여 보세요.

## 정리

Docker 빌드 자동화의 핵심은 Buildx, 캐시, 태그 전략, 권한 설정을 함께 설계하는 것입니다. 이 조합이 맞아야 빌드는 빨라지고, 어떤 이미지가 배포됐는지도 선명해집니다.

다음 글에서는 배포 자동화를 다룹니다. 이미지를 안정적으로 만들 수 있게 됐다면, 이제 그 결과를 staging과 production까지 어떻게 안전하게 올릴지 고민해야 합니다.


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

- **Buildx는 왜 일반 빌더보다 더 자주 쓰일까요?**
  - 본문의 기준은 Docker 빌드를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **GitHub Actions 캐시는 Docker 레이어 시간에 어떤 영향을 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **GHCR에 푸시할 때 어떤 권한이 필요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint와 Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): 빌드 아티팩트](./06-build-artifact.md)
- **Docker 빌드 (현재 글)**
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [docker/build-push-action](https://github.com/docker/build-push-action)
- [docker/setup-buildx-action](https://github.com/docker/setup-buildx-action)
- [GHCR documentation](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Buildx GitHub Actions cache](https://docs.docker.com/build/ci/github-actions/cache/)

Tags: GitHubActions, Docker, Buildx, GHCR, CICD
