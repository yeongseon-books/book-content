---
series: docker-101
episode: 10
title: "Docker 101 (10/10): 배포용 Docker 구성"
status: publish-ready
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

이 글은 Docker 101 시리즈의 마지막 글입니다.


시리즈 내내 이미지를 만들고, 컨테이너를 실행하고, 데이터와 네트워크를 다루고, 설정과 최적화까지 살펴봤습니다. 그런데 프로덕션은 이 모든 요소가 한꺼번에 검증되는 장소입니다. 이미지 태그 정책이 느슨하면 무엇이 배포됐는지 모르게 되고, 로그가 컨테이너 안 파일로 남아 있으면 수집이 깨지며, 런타임 보안이 약하면 운영 전체가 불안정해집니다.

즉, 프로덕션은 개별 기술 체크리스트의 합이 아니라 시스템입니다. 이미지를 어떻게 만들었는지, 어디에 저장하는지, 어떤 권한으로 실행하는지, 실패를 어떻게 관찰하는지가 동시에 맞물려야 합니다. 이 글은 그 마지막 기준선을 정리합니다.


![Docker 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/10/10-01-concept-at-a-glance.ko.png)
*Docker 101 10장 흐름 개요*

## 먼저 던지는 질문

- 프로덕션에서는 어떤 이미지 태그 정책을 가져가야 할까요?
- 레지스트리와 이미지 서명은 왜 공급망 신뢰의 일부일까요?
- read-only, capability 제한, non-root는 어떤 식으로 결합해야 할까요?

## 왜 이 글이 중요한가

운영 환경에서는 이전에 배운 모든 결정이 한 번에 현실이 됩니다. 빌드 단계에서 남겨 둔 불필요한 도구는 공격 표면이 되고, `latest` 태그는 배포 추적을 어렵게 만들며, healthcheck와 재시작 정책이 없으면 죽은 컨테이너가 조용히 방치될 수 있습니다.

프로덕션을 어렵게 만드는 이유는 기술이 복잡해서만이 아닙니다. 각각의 작은 선택이 서로 연결되어 있다는 점 때문입니다. 따라서 프로덕션 컨테이너는 "돌아간다"보다 "추적 가능하고, 안전하고, 관측 가능하다"를 기준으로 평가해야 합니다.

## 한눈에 보는 개념

## 핵심 용어

- **Tag policy**: `semver`와 `git sha`를 함께 쓰는 이중 태깅 규칙입니다.
- **Cosign**: 이미지를 서명하는 도구입니다.
- **Read-only rootfs**: 컨테이너 루트 파일시스템을 읽기 전용으로 잠그는 방식입니다.
- **Capabilities**: Linux 권한을 세분화한 제어 단위입니다.
- **Logging driver**: stdout 로그를 어떻게 수집하고 전달할지 정하는 방식입니다.

이 용어들은 따로 떨어진 옵션처럼 보여도 실제로는 하나의 운영 모델을 이룹니다. 추적 가능한 이미지, 신뢰 가능한 공급망, 최소 권한 런타임, 표준 로그·메트릭 채널이 함께 있어야 MTTR을 줄일 수 있습니다.

## 전과 후

**Before**: `latest`로 배포하고, root로 실행하고, 로그를 컨테이너 내부 파일에 씁니다.

**After**: `1.4.2`와 `sha-abc1234`를 함께 태깅하고, non-root + read-only로 실행하며, 로그는 stdout으로 보냅니다.

이 차이는 프로덕션 장애 대응 속도를 바꿉니다. 무엇이 배포됐는지, 어떤 권한으로 돌고 있는지, 장애 시 어디서 로그를 봐야 하는지를 즉시 설명할 수 있기 때문입니다.

## 실습: 프로덕션 구성을 5단계로 정리하기

### 1단계 — 태그 지정과 push

```bash
TAG=1.4.2
SHA=$(git rev-parse --short HEAD)
docker build -t ghcr.io/me/myapp:${TAG} -t ghcr.io/me/myapp:sha-${SHA} .
docker push ghcr.io/me/myapp:${TAG}
docker push ghcr.io/me/myapp:sha-${SHA}
```

semver 태그는 사람이 읽기 좋고, sha 태그는 변경 추적에 강합니다. 둘을 함께 두면 배포 기록과 사고 대응이 훨씬 단단해집니다.

### 2단계 — 이미지 서명

```bash
cosign sign --yes ghcr.io/me/myapp:${TAG}
cosign verify --certificate-identity-regexp '.*' \
              --certificate-oidc-issuer-regexp '.*' \
              ghcr.io/me/myapp:${TAG}
```

이미지 서명은 공급망 신뢰의 출발점입니다. 레지스트리에 올라가 있다는 사실만으로는 그 이미지가 정말 여러분이 만든 산출물인지 보장할 수 없습니다.

### 3단계 — 런타임 보안 옵션

```bash
docker run -d --name api \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --user 1000:1000 \
  -p 8000:8000 \
  ghcr.io/me/myapp:${TAG}
```

이 명령은 운영 기본값을 바꾸는 좋은 예입니다. 쓰기 권한을 최소화하고, capability를 제거하고, 권한 상승을 막고, non-root로 실행합니다. 결국 프로덕션은 허용보다 차단이 기본이어야 합니다.

### 4단계 — Compose로 표현하기

```yaml
services:
  web:
    image: ghcr.io/me/myapp:1.4.2
    read_only: true
    tmpfs: ["/tmp"]
    cap_drop: ["ALL"]
    user: "1000:1000"
    deploy:
      restart_policy: { condition: on-failure }
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "5" }
```

Compose로도 같은 운영 기준을 선언할 수 있습니다. 보안 플래그와 로그 정책을 명시적으로 남기면, 로컬·스테이징·운영 환경 사이에서 설정 차이를 관리하기 쉬워집니다.

### 5단계 — 메트릭 노출

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

프로덕션에서는 로그만으로는 부족합니다. 상태를 계속 관찰하려면 메트릭이 필요합니다. 특히 요청 수, 지연 시간, 오류율은 운영에서 가장 먼저 보게 되는 신호입니다.

### 실행 뒤 바로 확인할 것

- push 뒤에는 semver 태그와 sha 태그가 둘 다 레지스트리에 올라가 있어야 하고, 서명 검증 명령이 성공해야 합니다.
- 런타임에서는 `/metrics` 엔드포인트가 열리고, 로그가 컨테이너 파일이 아니라 stdout으로 나오는지까지 확인합니다.

### 잘 안 될 때 먼저 볼 것

- `--read-only` 적용 뒤 앱이 실패하면 `/tmp` 같은 쓰기 경로를 tmpfs로 따로 열어 두었는지 먼저 확인합니다.
- 배포 추적이 흐리면 태그보다 digest 고정과 실제 배포 매니페스트가 일치하는지부터 확인합니다.

## 이 코드에서 먼저 봐야 할 점

- 이미지 서명은 공급망 신뢰를 추가합니다.
- read-only와 capability 제거는 런타임 권한을 크게 줄입니다.
- 로그와 메트릭은 stdout과 엔드포인트만으로도 충분한 표준 경로를 만들 수 있습니다.

여기서 중요한 것은 복잡한 기능을 많이 붙이는 것이 아닙니다. 운영 중 가장 자주 보는 신호와 가장 위험한 권한을 표준 방식으로 다루는 것입니다.

## 자주 하는 실수 다섯 가지

1. **`latest`를 그대로 배포합니다.** 어떤 버전이 실제로 떠 있는지 설명하기 어려워집니다.
2. **서명되지 않은 이미지를 사용합니다.** 공급망 공격 방어가 약해집니다.
3. **로그를 컨테이너 내부 파일에 씁니다.** 수집과 회전이 쉽게 깨집니다.
4. **`--privileged`를 습관처럼 사용합니다.** 보안 기본값이 무너집니다.
5. **healthcheck와 restart 정책을 두지 않습니다.** 죽은 컨테이너가 조용히 남을 수 있습니다.

이 다섯 가지는 모두 운영의 추적성과 복구 가능성을 떨어뜨립니다. 프로덕션 품질은 기능 수보다 실패를 얼마나 빨리 식별하고 복구할 수 있는가로 판단해야 합니다.

## 실무에서는 이렇게 이어집니다

실제 운영은 Kubernetes 위에서 이루어지는 경우가 많지만, 여기서 다룬 원칙은 거의 그대로 이어집니다. 태그와 digest 고정, 이미지 서명, read-only root filesystem, non-root 실행, 로그와 메트릭 분리는 Kubernetes manifest에서도 동일한 주제입니다.

즉, Docker 101에서 익힌 습관은 단순한 로컬 실습 기술이 아니라 더 큰 오케스트레이션 환경으로 넘어갈 때 그대로 가져갈 자산입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 프로덕션은 기본값을 허용에서 차단으로 뒤집는 곳입니다.
- 이미지 태그는 불변에 가깝게 관리하고, 실제 배포는 digest로 고정하는 편이 좋습니다.
- 로그는 stdout, 메트릭은 엔드포인트, 추적은 OTel 같은 표준 경로를 따릅니다.
- 서명되지 않은 이미지는 결국 출처가 불분명한 코드입니다.
- 모든 결정은 MTTR을 줄이는 방향으로 평가해야 합니다.

이 시리즈의 마지막 관점도 여기에 있습니다. Docker를 잘 쓴다는 말은 이미지를 잘 빌드하는 것에서 끝나지 않습니다. 운영에서 믿을 수 있는 단위로 만들고, 추적 가능하고, 안전하며, 관측 가능한 상태로 유지하는 것까지 포함합니다.

## 체크리스트

- [ ] semver와 sha 이중 태그를 사용합니다.
- [ ] 이미지를 서명하고 검증합니다.
- [ ] read-only, cap-drop, non-root를 적용합니다.
- [ ] 로그와 메트릭의 표준 채널이 있습니다.
- [ ] healthcheck와 restart 정책이 있습니다.

## 연습 문제

1. 이미지를 semver와 sha 태그로 함께 push해 보세요.
2. Cosign으로 서명하고 검증해 보세요.
3. read-only와 cap-drop을 적용한 컨테이너가 정상 동작하는지 확인해 보세요.

## 정리 및 다음 단계

여기까지 왔다면 Docker의 핵심 95%는 이미 다뤘다고 봐도 좋습니다. 이미지를 만들고, 컨테이너를 실행하고, 데이터와 네트워크를 분리하고, 설정을 외부화하고, 앱과 DB를 함께 운영하고, 이미지를 최적화하고, 마지막으로 프로덕션 기준까지 정리했습니다. 남는 과제는 이 감각을 더 큰 운영 환경으로 확장하는 것입니다.

다음 단계로는 Kubernetes 101에서 컨테이너 오케스트레이션을, SRE 101에서 운영 신뢰성을 이어서 보는 것이 좋습니다. Docker는 출발점이지만, 이미 충분히 실무적인 출발점입니다.


## 실전 설계 확장: Dockerfile, Compose, 멀티 스테이지

Docker를 팀 표준으로 쓰려면 단순 실행 명령을 넘어서 이미지 빌드 규칙과 서비스 조합 규칙을 함께 정의해야 합니다. 특히 Dockerfile 계층 설계, docker-compose.yml 환경 분리, 멀티 스테이지 빌드 전략은 개발 속도와 보안 품질을 동시에 좌우합니다. 같은 애플리케이션 코드라도 이 세 가지를 어떻게 설계하느냐에 따라 이미지 크기, 빌드 시간, 취약점 노출 범위가 크게 달라집니다.

### Dockerfile을 재현 가능한 빌드 문서로 다루기

좋은 Dockerfile은 "동작한다"보다 "같은 입력에서 같은 산출물이 나온다"를 목표로 합니다. 베이스 이미지 태그를 고정하고, 의존성 설치 순서를 안정적으로 분리하고, 런타임 사용자 권한을 낮춰야 합니다.

```dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd -m appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser
CMD ["python", "main.py"]
```

위 구조에서 중요한 점은 의존성 설치 계층과 소스 복사 계층을 분리해 캐시 효율을 확보하는 것입니다. `requirements.txt`가 바뀌지 않으면 패키지 설치 레이어를 재사용할 수 있어 빌드 시간이 크게 줄어듭니다.

### docker-compose.yml은 서비스 경계를 코드로 남긴다

Compose는 "여러 컨테이너를 한 번에 띄운다"가 전부가 아닙니다. 각 서비스의 책임 경계, 네트워크 연결, 볼륨 지속성, 헬스체크 기준을 파일로 고정하는 역할이 더 큽니다.

```yaml
version: "3.9"
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=local
      - DATABASE_URL=postgresql://app:app@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 3s
      retries: 5

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=app
      - POSTGRES_DB=appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  pgdata:
```

이 파일 하나로 새 팀원은 로컬 환경을 재현하고, CI는 같은 토폴로지를 사용해 통합 테스트를 수행할 수 있습니다. Compose를 문서 대신 코드로 다루는 이유가 여기에 있습니다.

### 멀티 스테이지 빌드로 런타임 이미지를 가볍게 유지하기

빌드 도구와 런타임이 섞이면 이미지가 불필요하게 커지고 공격 표면도 넓어집니다. 멀티 스테이지는 빌드에 필요한 것과 실행에 필요한 것을 분리해 이 문제를 해결합니다.

```dockerfile
FROM node:22-alpine AS build
WORKDIR /src
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

이 방식의 장점은 명확합니다.

- 최종 이미지는 정적 파일과 최소 런타임만 포함합니다.
- 빌드 도구 체인 취약점이 운영 이미지로 전파될 가능성을 줄입니다.
- 배포 전 전송량이 줄어 레지스트리 푸시/풀 시간이 단축됩니다.

### 운영 기준으로 보는 체크포인트

- 이미지 태그는 `latest` 대신 버전+커밋 해시를 사용합니다.
- 기본 사용자로 root를 피하고 최소 권한 사용자로 실행합니다.
- 헬스체크를 통해 readiness 판단을 자동화합니다.
- `.dockerignore`로 불필요한 파일 유입을 차단합니다.
- Secret은 이미지에 bake-in 하지 않고 런타임 주입으로 관리합니다.

### 빌드 파이프라인 예시

```bash
docker build -t ghcr.io/acme/app:1.4.2-3f2a9d1 .
docker run --rm ghcr.io/acme/app:1.4.2-3f2a9d1 python -m pytest -q
docker push ghcr.io/acme/app:1.4.2-3f2a9d1
```

위처럼 테스트 통과 이미지만 푸시하도록 규칙화하면 "코드는 통과했는데 이미지가 깨졌다" 같은 불일치를 줄일 수 있습니다. 컨테이너 운영의 핵심은 코드와 실행 단위를 같은 검증 루프로 묶는 데 있습니다.

### 장애 대응 관점에서 Compose와 Dockerfile을 함께 본다

운영 이슈가 발생하면 단일 파일만 봐서는 원인이 잘 드러나지 않습니다. 예를 들어 앱 컨테이너가 재시작 루프에 빠졌다면 Dockerfile의 엔트리포인트, Compose의 환경변수, 의존 서비스 헬스체크를 한 번에 확인해야 합니다. 따라서 리뷰 단계에서 "Dockerfile 단독 리뷰"가 아니라 "Dockerfile + Compose + 실행 로그"를 묶어 검토하는 습관이 필요합니다.

이 관점을 유지하면 컨테이너는 단순 포장 기술이 아니라 신뢰 가능한 배포 단위로 자리잡습니다.


## 실전 앵커: 운영에서 바로 쓰는 명령 모음

개념을 이해했다면 이제 실제 운영에서 자주 쓰는 명령과 구성으로 연결해 보는 것이 좋습니다. 아래 예시는 로컬 개발, CI 검증, 스테이징 점검에서 그대로 재사용할 수 있도록 구성했습니다. 핵심은 "한 번 실행해 보고 끝"이 아니라, 실패 원인을 빠르게 분리할 수 있는 관찰 포인트를 같이 남기는 것입니다.

### Dockerfile 앵커: 빌드 캐시와 보안 기본값

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip     pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl     && rm -rf /wheels     && useradd -m -u 10001 appuser
COPY . .
USER appuser
CMD ["python", "app.py"]
```

이 패턴은 의존성 빌드와 런타임 이미지를 분리해 크기와 취약점 표면을 함께 줄입니다. 또한 non-root 실행을 기본값으로 두어 운영 보안 정책과 충돌을 줄입니다.

### Compose 앵커: 앱, DB, 캐시를 재현 가능한 단위로 묶기

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=local
      - DATABASE_URL=postgresql://app:app@db:5432/appdb
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./:/workspace:ro
  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=app
      - POSTGRES_DB=appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 10
  cache:
    image: redis:7-alpine

volumes:
  pgdata:
```

여기서 중요한 점은 의존 관계를 명시하되, 앱 자체도 재시도 가능한 연결 로직을 가져야 한다는 것입니다. `depends_on`은 시작 순서를 도와주지만 분산 환경의 모든 지연을 해결하지는 못합니다.

### 볼륨 마운트 앵커: 상태와 소스 코드를 분리하기

```bash
# 영속 데이터 볼륨
docker volume create app-data

# 읽기 전용 소스 마운트 + 쓰기 가능한 임시 디렉터리
docker run --rm   -v "$PWD":/workspace:ro   -v app-data:/var/lib/app   --tmpfs /tmp   myapp:latest
```

운영에서 가장 흔한 실수는 애플리케이션 상태와 개발 편의용 마운트를 같은 경로에 섞는 것입니다. 상태 데이터 경로는 팀 규칙으로 고정하고, 개발 편의용 bind mount는 읽기 전용을 기본으로 두는 편이 안전합니다.

### 네트워킹 앵커: 이름 기반 통신과 점검 명령

```bash
docker network create service-net

docker run -d --name db --network service-net postgres:16-alpine
docker run -d --name api --network service-net -e DB_HOST=db myapp:latest

docker exec api getent hosts db
docker exec api sh -lc 'nc -zv db 5432'
docker network inspect service-net
```

컨테이너 통신 문제를 만났을 때는 먼저 DNS 해석(`getent hosts`)과 포트 도달성(`nc -zv`)을 분리해 확인합니다. 두 단계를 나누면 애플리케이션 버그와 네트워크 구성을 섞어 디버깅하는 일을 줄일 수 있습니다.

### 이미지 최적화 앵커: 측정 기반으로 개선하기

```bash
DOCKER_BUILDKIT=1 docker build -t myapp:opt .
docker history myapp:opt

docker image inspect myapp:opt --format '{{.Size}}'
docker run --rm wagoodman/dive:latest myapp:opt
```

이미지 최적화는 "작아 보인다"가 아니라 "측정값이 줄었다"로 판단해야 합니다. 히스토리와 레이어 분석 도구를 같이 쓰면 어떤 단계가 크기를 키우는지 빠르게 찾을 수 있습니다.

### 운영 체크포인트

- 같은 코드를 다시 빌드했을 때 캐시 적중으로 시간이 줄어드는지 확인합니다.
- 컨테이너 재생성 후에도 필요한 데이터가 volume에 남는지 확인합니다.
- healthcheck 실패 시 로그와 네트워크 점검 명령으로 원인을 1차 분리합니다.
- 이미지 태그를 `latest`만 쓰지 않고 버전과 커밋 식별자를 함께 남깁니다.

## 검증 시나리오: 실패를 재현하고 복구 경로까지 확인하기

운영 준비가 되었는지 확인하려면 성공 경로만 보면 부족합니다. 의도적으로 실패를 만들고, 관찰 신호와 복구 절차가 준비되어 있는지 함께 점검해야 합니다. 아래 시나리오는 대부분의 Docker 기반 서비스에서 공통으로 재사용할 수 있습니다.

### 시나리오 1: 애플리케이션 프로세스 비정상 종료

```bash
docker kill --signal=SIGKILL api
docker ps -a
docker logs api
```

- 재시작 정책이 있다면 컨테이너가 자동 복구되는지 확인합니다.
- 자동 복구가 없다면 운영 기준에 맞는 실패 알림이 발생하는지 확인합니다.

### 시나리오 2: 데이터베이스 일시 중단

```bash
docker stop db
sleep 5
docker start db
docker compose logs -f app
```

- 애플리케이션이 즉시 영구 실패하지 않고 재시도하는지 확인합니다.
- DB 복구 후 정상 요청 흐름으로 복귀하는지 확인합니다.

### 시나리오 3: 네트워크 단절

```bash
docker network disconnect service-net api
docker exec api sh -lc 'nc -zv db 5432 || true'
docker network connect service-net api
```

- 단절 시 오류 메시지가 관찰 가능한 형태로 남는지 확인합니다.
- 재연결 후 별도 수동 조치 없이 복구되는지 확인합니다.

### 시나리오 4: 디스크 사용량 증가

```bash
docker system df
docker volume ls
docker image ls --format '{{.Repository}}:{{.Tag}} {{.Size}}'
```

- 정리 기준이 없는 중간 이미지와 미사용 볼륨이 빠르게 증가하는지 확인합니다.
- 정리 정책(`image prune`, 보존 기간, 태그 규칙)이 문서화되어 있는지 확인합니다.

### 시나리오 5: 배포 롤백 검증

```bash
docker pull ghcr.io/me/myapp:1.4.1
docker run --rm ghcr.io/me/myapp:1.4.1 python -m pytest -q
```

- 이전 안정 버전으로 즉시 되돌릴 수 있는 태그 체계가 있는지 확인합니다.
- 롤백 시 필요한 환경변수, 볼륨, 네트워크 계약이 변하지 않았는지 확인합니다.

이 시나리오를 정기적으로 반복하면 "문제가 생겼을 때 무엇을 볼지"가 팀 공통 지식으로 고정됩니다. Docker 운영 품질은 고급 기능보다 실패를 얼마나 빨리 좁혀 가는지에서 차이가 납니다.

## 처음 질문으로 돌아가기

- **프로덕션에서는 어떤 이미지 태그 정책을 가져가야 할까요?**
  - 본문의 기준은 배포용 Docker 구성를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **레지스트리와 이미지 서명은 왜 공급망 신뢰의 일부일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **read-only, capability 제한, non-root는 어떤 식으로 결합해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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