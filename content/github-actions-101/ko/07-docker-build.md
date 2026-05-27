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

![GitHub Actions 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/07/07-01-docker.ko.png)
*GitHub Actions 101 7장 흐름 개요*

> Docker 빌드를 CI에 옮기는 일은 `docker build`를 그대로 옮기는 것이 아닙니다 — Buildx 캐시·태그 전략·GHCR 권한·멀티 플랫폼 빌드는 별개 기능이 아니라 '같은 이미지를 빠르고 재현 가능하게 만들고, 어떤 이미지가 어디 배포됐는지 추적되게 한다'는 한 흐름의 부분들입니다.

## 먼저 던지는 질문

- Buildx는 왜 일반 빌더보다 더 자주 쓰일까요?
- GitHub Actions 캐시는 Docker 레이어 시간에 어떤 영향을 줄까요?
- GHCR에 푸시할 때 어떤 권한이 필요할까요?

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

## Dockerfile 최적화와 CI 빌드 시간의 관계

CI에서 Docker 빌드 시간을 줄이려면 Dockerfile 자체를 CI 친화적으로 작성해야 합니다. 레이어 캐시가 효과적으로 동작하려면 변경 빈도가 낮은 레이어를 위에, 높은 레이어를 아래에 배치해야 합니다.

### 캐시 효율이 높은 Dockerfile 패턴

```dockerfile
# 1단계: 의존성 설치 (변경 빈도 낮음)
FROM python:3.12-slim AS deps
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

# 2단계: 애플리케이션 복사 (변경 빈도 높음)
FROM deps AS app
COPY src/ ./src/
COPY pyproject.toml ./

# 3단계: 최종 이미지 (최소화)
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=app /app/src ./src
USER 1000:1000
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 멀티스테이지 빌드의 설계 포인트입니다.

- **의존성 레이어 분리**: `requirements.lock`이 바뀌지 않으면 pip install 레이어가 캐시됩니다. 소스 코드만 바뀌면 이 레이어를 재사용하므로 빌드 시간이 크게 줄어듭니다.
- **멀티스테이지**: 빌드 도구와 개발 의존성을 최종 이미지에 포함하지 않아 이미지 크기를 줄입니다.
- **non-root 사용자**: 보안을 위해 root가 아닌 사용자로 실행합니다.

---

## Buildx 캐시 전략 심화

GitHub Actions에서 Docker 레이어 캐시를 활용하는 방법은 여러 가지가 있습니다. 각각의 장단점을 비교하겠습니다.

### GitHub Actions Cache (gha) 백엔드

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

`mode=max`는 모든 빌드 스테이지의 레이어를 캐시합니다. 기본 `mode=min`은 최종 이미지의 레이어만 캐시하므로, 멀티스테이지 빌드에서는 `max`가 캐시 적중률이 높습니다.

### 레지스트리 캐시

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:cache
    cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:cache,mode=max
```

레지스트리 캐시는 GitHub Actions Cache의 10GB 제한에 걸리지 않고, 다른 CI 시스템에서도 접근할 수 있습니다. 다만 네트워크를 통해 캐시를 주고받으므로 첫 빌드에서는 gha보다 느릴 수 있습니다.

### 캐시 전략 비교

| 전략 | 속도 | 용량 제한 | 공유 범위 |
| --- | --- | --- | --- |
| gha (GitHub Actions) | 빠름 | 10 GB | 같은 저장소 |
| registry | 중간 | 레지스트리 한도 | 조직 전체 |
| local | 가장 빠름 | 러너 디스크 | 불가 (러너 휘발) |

대부분의 프로젝트에서는 `gha`로 시작하고, 캐시 크기가 부족해지면 registry로 전환하는 순서가 현실적입니다.

---

## 태그 전략과 이미지 추적

Docker 이미지의 태그는 "어떤 코드가 이 이미지에 담겼는가"를 추적하는 핵심입니다.

```yaml
- uses: docker/metadata-action@v5
  id: meta
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=ref,event=branch
      type=ref,event=pr
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=sha,prefix=,format=short

- uses: docker/build-push-action@v6
  with:
    context: .
    push: ${{ github.event_name != 'pull_request' }}
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

`docker/metadata-action`은 이벤트 종류에 따라 자동으로 적절한 태그를 생성합니다.

| 이벤트 | 생성되는 태그 예시 |
| --- | --- |
| main push | `main`, `sha-a1b2c3d` |
| PR #42 | `pr-42` |
| v1.2.3 태그 | `1.2.3`, `1.2`, `sha-a1b2c3d` |

PR에서는 `push: false`로 이미지를 빌드만 하고 레지스트리에 올리지 않습니다. 빌드 성공 여부만 확인하면 되기 때문입니다.

---

## GHCR 권한 설정

GitHub Container Registry에 이미지를 push하려면 적절한 권한 설정이 필요합니다.

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v6

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

핵심 포인트입니다.

- `permissions: packages: write`가 필요합니다. 기본 권한이 `read`이면 push가 실패합니다.
- `GITHUB_TOKEN`은 자동으로 제공되므로 별도 PAT를 만들 필요가 없습니다.
- 이미지 이름은 소문자여야 합니다. 저장소 이름에 대문자가 있으면 `${{ github.repository }}`를 소문자로 변환해야 합니다.

```yaml
- name: 저장소 이름 소문자 변환
  id: repo
  run: echo "name=$(echo ${{ github.repository }} | tr '[:upper:]' '[:lower:]')" >> "$GITHUB_OUTPUT"
```

---

## 이미지 보안 스캔

빌드된 이미지에 알려진 취약점이 없는지 확인하는 것은 CI의 중요한 역할입니다.

```yaml
- name: 이미지 빌드
  uses: docker/build-push-action@v6
  with:
    context: .
    load: true
    tags: app:scan

- name: 보안 스캔
  uses: aquasecurity/trivy-action@0.28.0
  with:
    image-ref: app:scan
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH

- name: 스캔 결과 업로드
  uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: trivy-results.sarif
```

`load: true`는 이미지를 로컬 Docker 데몬에 로드합니다(push하지 않음). 스캔 후 문제가 없을 때만 push하는 구조입니다.

Trivy의 SARIF 출력을 GitHub Code Scanning에 업로드하면 PR의 Security 탭에서 취약점을 확인할 수 있습니다. 심각도를 `CRITICAL,HIGH`로 제한하면 즉시 조치가 필요한 문제만 걸러냅니다.

---

## 멀티 플랫폼 빌드

ARM 서버나 Apple Silicon Mac에서도 동작하는 이미지를 만들려면 멀티 플랫폼 빌드가 필요합니다.

```yaml
- uses: docker/setup-qemu-action@v3

- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v6
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

QEMU를 사용한 에뮬레이션은 네이티브 빌드보다 2-5배 느립니다. 빌드 시간이 중요하다면 ARM 네이티브 러너를 사용하거나, 플랫폼별로 별도 잡을 실행한 후 manifest로 합치는 방법이 있습니다.

```yaml
jobs:
  build-amd64:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v6
        with:
          platforms: linux/amd64
          ...

  build-arm64:
    runs-on: ubuntu-24.04-arm
    steps:
      - uses: docker/build-push-action@v6
        with:
          platforms: linux/arm64
          ...

  manifest:
    needs: [build-amd64, build-arm64]
    runs-on: ubuntu-latest
    steps:
      - run: |
          docker manifest create ghcr.io/org/app:latest \
            ghcr.io/org/app:amd64 \
            ghcr.io/org/app:arm64
          docker manifest push ghcr.io/org/app:latest
```

---

## Docker Compose 기반 통합 테스트

Docker 빌드와 함께 통합 테스트를 실행하는 패턴입니다. 애플리케이션과 의존성(DB, Redis)을 함께 띄워서 실제 환경에 가까운 테스트를 CI에서 수행할 수 있습니다.

```yaml
jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: 서비스 실행
        run: docker compose -f docker-compose.test.yml up -d

      - name: 서비스 준비 대기
        run: |
          timeout 60 bash -c 'until curl -s http://localhost:8000/health; do sleep 2; done'

      - name: 통합 테스트 실행
        run: |
          docker compose -f docker-compose.test.yml exec -T app pytest tests/integration -q

      - name: 로그 수집
        if: failure()
        run: docker compose -f docker-compose.test.yml logs > docker-logs.txt

      - uses: actions/upload-artifact@v7
        if: failure()
        with:
          name: docker-logs
          path: docker-logs.txt
          retention-days: 3

      - name: 정리
        if: always()
        run: docker compose -f docker-compose.test.yml down -v
```

`if: failure()`로 실패 시에만 로그를 수집하고 아티팩트로 저장합니다. 성공 시에는 불필요한 파일을 만들지 않아 스토리지를 절약합니다.

---

## 이미지 크기 최적화 체크

이미지 크기가 계속 커지면 배포 시간과 스토리지 비용에 영향을 미칩니다. CI에서 이미지 크기를 모니터링하는 방법입니다.

```yaml
- name: 이미지 크기 확인
  run: |
    SIZE=$(docker image inspect app:latest --format='{{.Size}}')
    SIZE_MB=$((SIZE / 1024 / 1024))
    echo "Image size: ${SIZE_MB} MB"
    
    # 임계값 초과 시 경고
    if [ "$SIZE_MB" -gt 500 ]; then
      echo "::warning::Image size exceeds 500MB (${SIZE_MB}MB)"
    fi
    
    # 임계값 초과 시 실패
    if [ "$SIZE_MB" -gt 1000 ]; then
      echo "::error::Image size exceeds 1GB limit (${SIZE_MB}MB)"
      exit 1
    fi
```

`::warning::`과 `::error::`는 GitHub Actions의 워크플로우 커맨드로, PR 체크에 경고와 오류를 표시합니다. 이미지 크기가 서서히 커지는 것을 조기에 발견할 수 있습니다.

이미지 크기를 줄이는 일반적인 방법입니다.

| 기법 | 효과 |
| --- | --- |
| slim/alpine 베이스 이미지 | 50-80% 감소 |
| 멀티스테이지 빌드 | 빌드 도구 제외 |
| .dockerignore 설정 | 불필요 파일 제외 |
| pip --no-cache-dir | pip 캐시 제외 |
| 레이어 합치기 (RUN 체이닝) | 중간 파일 제거 |

---

## CI에서의 Docker 보안 모범 사례

```yaml
jobs:
  docker-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Dockerfile 린트
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile

      - name: 빌드
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: app:security-check

      - name: 취약점 스캔
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: app:security-check
          severity: CRITICAL,HIGH
          exit-code: 1

      - name: SBOM 생성
        uses: anchore/sbom-action@v0
        with:
          image: app:security-check
          output-file: sbom.spdx.json
```

이 워크플로우는 세 단계의 보안 검증을 수행합니다.

1. **Hadolint**: Dockerfile의 모범 사례 위반을 검사합니다 (root 사용, latest 태그, 불필요한 패키지 등).
2. **Trivy**: 빌드된 이미지의 OS 패키지와 언어 의존성에서 알려진 취약점을 찾습니다.
3. **SBOM**: 소프트웨어 구성 요소 목록을 생성해 공급망 보안을 지원합니다.

`exit-code: 1`로 설정하면 CRITICAL/HIGH 취약점이 발견되면 잡이 실패합니다. 이를 통해 취약한 이미지가 배포되는 것을 원천 차단합니다.

## 정리

Docker 빌드 자동화의 핵심은 Buildx, 캐시, 태그 전략, 권한 설정을 함께 설계하는 것입니다. 이 조합이 맞아야 빌드는 빨라지고, 어떤 이미지가 배포됐는지도 선명해집니다.

다음 글에서는 배포 자동화를 다룹니다. 이미지를 안정적으로 만들 수 있게 됐다면, 이제 그 결과를 staging과 production까지 어떻게 안전하게 올릴지 고민해야 합니다.

---

## 처음 질문으로 돌아가기

- **Buildx는 왜 일반 빌더보다 더 자주 쓰일까요?**
  - Buildx는 멀티 플랫폼 빌드, 고급 캐시 백엔드(gha, registry), 병렬 빌드 스테이지 실행을 지원합니다. 일반 `docker build`는 로컬 빌드에는 충분하지만, CI에서 캐시 최적화와 멀티 아키텍처 지원이 필요해지면 Buildx가 사실상 필수입니다. `docker/setup-buildx-action` 한 줄로 설정할 수 있습니다.
- **GitHub Actions 캐시는 Docker 레이어 시간에 어떤 영향을 줄까요?**
  - `cache-from: type=gha`를 설정하면 이전 빌드의 레이어를 재사용해서 변경되지 않은 레이어를 다시 빌드하지 않습니다. 의존성 설치 레이어가 캐시되면 빌드 시간이 수 분에서 수십 초로 줄어듭니다. `mode=max`로 모든 스테이지를 캐시하면 멀티스테이지 빌드에서도 효과가 극대화됩니다.
- **GHCR에 푸시할 때 어떤 권한이 필요할까요?**
  - `permissions: packages: write`를 잡 수준에서 설정하고, `docker/login-action`으로 `GITHUB_TOKEN`을 사용해 로그인합니다. 별도 PAT 없이도 동작하며, 이미지 이름은 소문자여야 합니다. PR에서는 push하지 않고 빌드 검증만 수행하는 패턴이 일반적입니다.

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
- [Trivy](https://github.com/aquasecurity/trivy)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Docker, Buildx, GHCR, CICD
