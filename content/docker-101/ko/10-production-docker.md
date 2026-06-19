---
series: docker-101
episode: 10
title: "Docker 101 (10/10): 배포용 Docker 구성"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/262"
    published_at: '2026-06-01'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Docker
  - Production
  - Security
  - Logging
  - Capstone
seo_description: 프로덕션용 Docker에서 태그, 서명, 보안, 로그, 메트릭의 기준을 정리합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (10/10): 배포용 Docker 구성

시리즈 내내 이미지를 만들고, 컨테이너를 실행하고, 데이터와 네트워크를 다루고, 설정과 최적화까지 살펴봤습니다. 그런데 프로덕션은 이 모든 요소가 한꺼번에 검증되는 장소입니다. 이미지 태그 정책이 느슨하면 무엇이 배포됐는지 모르게 되고, 로그가 컨테이너 안 파일로 남아 있으면 수집이 깨지며, 런타임 보안이 약하면 운영 전체가 불안정해집니다.

이 글은 Docker 101 시리즈의 마지막 글입니다.

즉, 프로덕션은 개별 기술 체크리스트의 합이 아니라 시스템입니다. 이미지를 어떻게 만들었는지, 어디에 저장하는지, 어떤 권한으로 실행하는지, 실패를 어떻게 관찰하는지가 동시에 맞물려야 합니다. 이 글은 그 마지막 기준선을 정리합니다.

![Docker 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/10/10-01-concept-at-a-glance.ko.png)
*Docker 101 10장 흐름 개요*

> 프로덕션은 체크리스트의 합이 아니라 시스템입니다 — 이미지 태그 정책·레지스트리·실행 권한·로그 수집·런타임 보안이 동시에 맞물려야 '무엇이 어디에 배포됐고, 실패했을 때 어떻게 알 수 있는가'에 대한 답이 비로소 존재합니다.

## 이 글에서 다룰 문제

- 프로덕션에서는 어떤 이미지 태그 정책을 가져가야 할까요?
- 레지스트리와 이미지 서명은 왜 공급망 신뢰의 일부일까요?
- read-only, capability 제한, non-root는 어떤 식으로 결합해야 할까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

운영 환경에서는 이전에 배운 모든 결정이 한 번에 현실이 됩니다. 빌드 단계에서 남겨 둔 불필요한 도구는 공격 표면이 되고, `latest` 태그는 배포 추적을 어렵게 만들며, healthcheck와 재시작 정책이 없으면 죽은 컨테이너가 조용히 방치될 수 있습니다.

프로덕션을 어렵게 만드는 이유는 기술이 복잡해서만이 아닙니다. 각각의 작은 선택이 서로 연결되어 있다는 점 때문입니다. 따라서 프로덕션 컨테이너는 "돌아간다"보다 "추적 가능하고, 안전하고, 관측 가능하다"를 기준으로 평가해야 합니다.

| 개념 | 설명 | 역할 |
|------|------|------|
| **Tag policy** | `semver` + `git sha` 이중 태깅 | 배포 추적, 롤백 기준 |
| **Cosign** | 이미지 서명 도구 | 공급망 신뢰, 변조 방지 |
| **Read-only rootfs** | 컨테이너 루트 파일시스템을 읽기 전용으로 잠금 | 런타임 파일 변조 방지 |
| **Capabilities** | Linux 권한을 세분화한 제어 단위 | 최소 권한 원칙 적용 |
| **Logging driver** | stdout 로그 수집 방식 | 중앙 집중 로그 연결 |

## 전과 후

**Before**: `latest`로 배포하고, root로 실행하고, 로그를 컨테이너 내부 파일에 씁니다. 장애 시 "어떤 버전이 떠 있는지" 확인하는 데만 10분이 걸립니다.

**After**: `1.4.2`와 `sha-abc1234`를 함께 태깅하고, non-root + read-only로 실행하며, 로그는 stdout으로 보냅니다. 장애 시 즉시 digest로 버전을 확인하고 롤백 명령을 실행합니다.

이 차이는 프로덕션 장애 대응 속도(MTTR)를 직접적으로 바꿉니다. 무엇이 배포됐는지, 어떤 권한으로 돌고 있는지, 장애 시 어디서 로그를 봐야 하는지를 즉시 설명할 수 있기 때문입니다.

## 실습: 프로덕션 구성을 5단계로 정리하기

### 1단계 — 이미지 태그 정책과 레지스트리 push

```bash
# 버전 정보
TAG=1.4.2
SHA=$(git rev-parse --short HEAD)
REGISTRY=ghcr.io/myorg/myapp

# 멀티 태그 빌드
docker build \
  --build-arg APP_VERSION=${TAG} \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t ${REGISTRY}:${TAG} \
  -t ${REGISTRY}:sha-${SHA} \
  -t ${REGISTRY}:latest \
  .

# 레지스트리 로그인
echo $GHCR_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 모든 태그 push
docker push ${REGISTRY}:${TAG}
docker push ${REGISTRY}:sha-${SHA}
# latest는 프로덕션 배포 기준으로 쓰지 않음 (참조용만)
```

semver 태그는 사람이 읽기 좋고, sha 태그는 변경 추적에 강합니다. 둘을 함께 두면 배포 기록과 사고 대응이 훨씬 단단해집니다. `latest`는 개발 편의용으로만 남겨 두고, 실제 배포는 semver나 sha로 고정합니다.

### 2단계 — 이미지 서명 (Cosign)

```bash
# Cosign 설치 (https://docs.sigstore.dev/cosign/installation/)

# 이미지 서명 (GitHub Actions OIDC 기반)
cosign sign --yes ${REGISTRY}:${TAG}

# 서명 검증
cosign verify \
  --certificate-identity-regexp 'https://github.com/myorg/myapp/.github/workflows/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ${REGISTRY}:${TAG}

# 취약점 스캔 결과를 attestation으로 첨부
trivy image --format cosign-vuln \
  --output vuln.json \
  ${REGISTRY}:${TAG}
cosign attest --yes --predicate vuln.json \
  --type vuln ${REGISTRY}:${TAG}
```

이미지 서명은 공급망 신뢰의 출발점입니다. 레지스트리에 올라가 있다는 사실만으로는 그 이미지가 정말 여러분이 만든 산출물인지 보장할 수 없습니다. 특히 CI/CD 파이프라인 외부에서 생성된 이미지는 반드시 서명을 검증해야 합니다.

### 3단계 — 런타임 보안 옵션

```bash
# 프로덕션 런타임 보안 플래그 조합
docker run -d --name api \
  --read-only \                              # 루트 파일시스템 읽기 전용
  --tmpfs /tmp:noexec,nosuid,size=100m \    # /tmp는 tmpfs로 따로 제공
  --cap-drop=ALL \                           # 모든 capability 제거
  --cap-add=NET_BIND_SERVICE \               # 필요한 것만 추가
  --security-opt=no-new-privileges \         # setuid/setgid 방지
  --security-opt=seccomp=default \           # seccomp 프로필 적용
  --user 1000:1000 \
  --pids-limit 100 \                         # 프로세스 수 제한
  --memory 512m \                            # 메모리 제한
  --cpus 1.0 \                               # CPU 제한
  -p 8000:8000 \
  ${REGISTRY}:${TAG}
```

이 명령은 운영 기본값을 바꾸는 좋은 예입니다. 쓰기 권한을 최소화하고, capability를 제거하고, 권한 상승을 막고, non-root로 실행합니다. 프로덕션은 허용보다 차단이 기본이어야 합니다.

### 4단계 — Compose로 프로덕션 구성 표현하기

```yaml
# compose.prod.yaml
services:
  web:
    image: ghcr.io/myorg/myapp:1.4.2    # 고정 semver 태그
    read_only: true
    tmpfs:
      - "/tmp:noexec,nosuid,size=100m"
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    security_opt:
      - no-new-privileges
    user: "1000:1000"
    ports:
      - "8000:8000"
    environment:
      LOG_LEVEL: INFO
    env_file:
      - .env.prod                       # 비밀값은 외부에서 주입
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 15s
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"

  # 또는 로그를 외부로 전송
  # logging:
  #   driver: fluentd
  #   options:
  #     fluentd-address: localhost:24224
```

Compose로도 같은 운영 기준을 선언할 수 있습니다. 보안 플래그와 로그 정책을 명시적으로 남기면, 로컬·스테이징·운영 환경 사이에서 설정 차이를 관리하기 쉬워집니다.

### 5단계 — 관측 가능성 (로그, 메트릭, 추적)

```python
# app/main.py — 관측 가능성 추가
import logging
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# 구조화 로그 (JSON 형식)
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
)

app = FastAPI()

# Prometheus 메트릭 노출
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    # 실제 의존성 확인 추가 가능
    return {"status": "ready"}
```

```bash
# 로그 확인 (stdout → 로그 드라이버 → 중앙 집중)
docker compose logs -f web

# 메트릭 확인
curl http://localhost:8000/metrics

# 실시간 컨테이너 자원 사용 확인
docker stats web
```

프로덕션에서는 로그만으로는 부족합니다. 상태를 계속 관찰하려면 메트릭이 필요합니다. 특히 요청 수, 지연 시간, 오류율은 운영에서 가장 먼저 보게 되는 신호입니다. 로그는 stdout으로, 메트릭은 `/metrics` 엔드포인트로 표준 경로를 따릅니다.

### 실행 뒤 바로 확인할 것

- push 뒤에는 semver 태그와 sha 태그가 둘 다 레지스트리에 올라가 있어야 합니다.
- 서명 검증 명령이 에러 없이 성공해야 합니다.
- `docker stats web`에서 메모리와 CPU가 지정한 limit 이하로 유지되어야 합니다.
- `curl http://localhost:8000/metrics`에서 Prometheus 형식 메트릭이 보여야 합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| `--read-only` 적용 후 앱 실패 | 쓰기 경로(`/tmp` 등)가 없음 | `--tmpfs /tmp` 추가, 앱이 쓰는 경로 확인 |
| cosign verify 실패 | 서명 없거나 OIDC issuer 불일치 | GitHub Actions에서만 서명, issuer URL 확인 |
| 메모리 limit 초과로 OOM Kill | 메모리 limit이 너무 낮음 | `docker stats`로 실제 사용량 확인 후 조정 |
| 로그가 보이지 않음 | 앱이 파일에 로그 쓰거나 버퍼링 | `PYTHONUNBUFFERED=1`, stdout 로그 출력 확인 |
| 배포 추적이 안 됨 | `latest` 태그만 사용 | semver + sha 이중 태깅, digest 기반 배포 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| `latest`를 프로덕션에 배포 | 어떤 버전이 실제로 떠 있는지 알 수 없음 | semver + sha 이중 태깅, digest 고정 |
| 서명되지 않은 이미지 사용 | 공급망 공격 방어 불가 | cosign으로 CI에서 서명, 배포 시 검증 |
| 로그를 컨테이너 내부 파일에 씀 | 컨테이너 종료 시 로그 소실, 회전 관리 복잡 | stdout으로 출력, 로그 드라이버로 수집 |
| `--privileged` 사용 | 컨테이너 격리 완전 해제 | 필요한 capability만 `--cap-add`로 추가 |
| healthcheck와 restart 정책 없음 | 죽은 컨테이너가 조용히 방치됨 | healthcheck + `restart: unless-stopped` |

## CI/CD 파이프라인 패턴

```yaml
# .github/workflows/deploy.yml (예시)
jobs:
  build-and-push:
    steps:
      - name: 이미지 빌드
        run: |
          docker build \
            -t $REGISTRY:${{ github.sha }} \
            -t $REGISTRY:${{ env.TAG }} \
            .

      - name: 이미지 push
        run: |
          docker push $REGISTRY:${{ github.sha }}
          docker push $REGISTRY:${{ env.TAG }}

      - name: 취약점 스캔
        run: trivy image $REGISTRY:${{ env.TAG }}

      - name: 이미지 서명
        run: cosign sign --yes $REGISTRY:${{ env.TAG }}

  deploy:
    needs: build-and-push
    steps:
      - name: 서명 검증
        run: cosign verify $REGISTRY:${{ env.TAG }}

      - name: 배포
        run: |
          docker pull $REGISTRY:${{ env.TAG }}
          docker service update \
            --image $REGISTRY:${{ env.TAG }} \
            myapp_web
```

## 실무에서는 이렇게 이어집니다

실제 운영은 Kubernetes 위에서 이루어지는 경우가 많지만, 여기서 다룬 원칙은 거의 그대로 이어집니다. 태그와 digest 고정, 이미지 서명, read-only root filesystem, non-root 실행, 로그와 메트릭 분리는 Kubernetes manifest에서도 동일한 주제입니다.

즉, Docker 101에서 익힌 습관은 단순한 로컬 실습 기술이 아니라 더 큰 오케스트레이션 환경으로 넘어갈 때 그대로 가져갈 자산입니다.

## 운영 체크리스트

- [ ] semver와 sha 이중 태그를 사용합니다 (`latest`는 배포 기준이 아님).
- [ ] CI에서 이미지를 서명하고 배포 시 검증합니다.
- [ ] `--read-only`, `--cap-drop=ALL`, `--user 1000:1000`을 적용합니다.
- [ ] 로그는 stdout으로, 메트릭은 `/metrics` 엔드포인트로 노출합니다.
- [ ] healthcheck와 restart 정책이 있습니다.
- [ ] 메모리와 CPU limit이 설정되어 있습니다.
- [ ] 취약점 스캔이 CI 파이프라인에 포함되어 있습니다.

## 연습 문제

1. 이미지를 semver(`1.0.0`)와 sha(`sha-abc1234`) 태그로 함께 GHCR에 push해 보세요.
2. Cosign으로 서명하고 검증해 보세요. 서명 없는 이미지를 verify하면 어떤 에러가 나는지 확인해 보세요.
3. `--read-only`와 `--tmpfs /tmp`를 적용한 컨테이너가 정상 동작하는지 확인하고, 앱이 어떤 경로에 쓰기를 시도하는지 확인해 보세요.
4. `prometheus-fastapi-instrumentator`를 추가하고 `/metrics`에서 요청 수와 지연 시간을 확인해 보세요.

## 처음 질문으로 돌아가기

- **프로덕션에서는 어떤 이미지 태그 정책을 가져가야 할까요?**
  - semver 태그(`1.4.2`)는 릴리스 버전을 명확하게 표시하고, sha 태그(`sha-abc1234`)는 정확히 어떤 커밋에서 빌드됐는지 추적합니다. 두 태그를 함께 유지하면 "이번 배포가 어떤 코드인지"를 즉시 확인하고 롤백 기준을 명확히 할 수 있습니다. `latest`는 최신 이미지를 가리키지만 배포 기준으로는 쓰지 않습니다.

- **레지스트리와 이미지 서명은 왜 공급망 신뢰의 일부일까요?**
  - 레지스트리에 올라가 있다는 사실만으로는 이미지가 정말 우리 팀이 만든 것인지 보장할 수 없습니다. 빌드 시스템이 침해되거나 레지스트리 자격증명이 탈취되면 악의적인 이미지가 올라올 수 있습니다. Cosign 서명은 이 이미지가 특정 CI 파이프라인에서 생성됐다는 것을 암호학적으로 증명합니다.

- **read-only, capability 제한, non-root는 어떤 식으로 결합해야 할까요?**
  - 세 가지는 서로 보완합니다. non-root는 파일시스템 권한 제한, read-only는 런타임 파일 변조 방지, capability 제거는 커널 수준 권한 제한입니다. 이 세 가지를 모두 적용하면 컨테이너가 침해되더라도 공격자가 할 수 있는 일이 극적으로 줄어듭니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - `--privileged`는 컨테이너 격리를 완전히 해제하므로 절대 사용하면 안 됩니다. `--network host`도 네트워크 격리를 없애므로 주의해야 합니다. 로그에 비밀값이 출력되지 않도록 하고, 이미지 취약점을 정기적으로 스캔(trivy 등)해야 합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - `--read-only` 적용 후 앱이 `/tmp`나 `/var/run`에 쓰기를 시도해 실패하는 경우가 가장 많습니다. 해결책은 `--tmpfs /tmp`로 메모리 기반 임시 파일시스템을 추가하는 것입니다. 앱이 쓰는 모든 경로를 파악하고 tmpfs로 제공해야 합니다.

## 정리

여기까지 왔다면 Docker의 핵심 95%는 이미 다뤘다고 봐도 좋습니다. 이미지를 만들고, 컨테이너를 실행하고, 데이터와 네트워크를 분리하고, 설정을 외부화하고, 앱과 DB를 함께 운영하고, 이미지를 최적화하고, 마지막으로 프로덕션 기준까지 정리했습니다. 남는 과제는 이 감각을 더 큰 운영 환경으로 확장하는 것입니다.

다음 단계로는 Kubernetes 101에서 컨테이너 오케스트레이션을, SRE 101에서 운영 신뢰성을 이어서 보는 것이 좋습니다. Docker는 출발점이지만, 이미 충분히 실무적인 출발점입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- **배포용 Docker 구성 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Docker security](https://docs.docker.com/engine/security/)
- [Sigstore Cosign](https://docs.sigstore.dev/cosign/overview/)
- [Read-only filesystem](https://docs.docker.com/engine/reference/run/#read-only)
- [12-factor - logs](https://12factor.net/logs)

### 검증과 트러블슈팅

- [Image digests and immutable pulls](https://docs.docker.com/reference/cli/docker/image/pull/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Production, Security, Logging, Capstone
