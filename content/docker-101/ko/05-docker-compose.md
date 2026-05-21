---
series: docker-101
episode: 5
title: "Docker 101 (5/10): Docker Compose"
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
  - Compose
  - YAML
  - MultiContainer
  - Dev
seo_description: Docker Compose로 멀티 컨테이너 환경을 한 파일에서 재현 가능하게 관리합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (5/10): Docker Compose

이 글은 Docker 101 시리즈의 5번째 글입니다.


컨테이너가 하나일 때는 `docker run` 몇 줄로도 충분합니다. 하지만 웹 애플리케이션, 데이터베이스, 캐시, 워커처럼 구성 요소가 늘어나는 순간부터 명령어 기반 운영은 빠르게 한계에 부딪힙니다. 누가 먼저 떠야 하는지, 어떤 환경변수를 넣어야 하는지, 어떤 볼륨과 네트워크를 써야 하는지를 매번 기억에 의존하게 되기 때문입니다.

Docker Compose는 이 문제를 YAML 하나로 정리합니다. 서비스, 네트워크, 볼륨, 의존 관계를 선언해 두면 팀 전체가 같은 멀티 컨테이너 환경을 같은 방식으로 띄울 수 있습니다. Compose는 많은 팀에서 사실상 첫 번째 인프라 코드입니다.


## 먼저 던지는 질문

- 여러 컨테이너를 한 번에 재현 가능하게 실행하려면 무엇이 필요할까요?
- service, network, volume은 Compose에서 어떻게 정의할까요?
- `depends_on`과 healthcheck는 어떤 관계로 이해해야 할까요?

## 큰 그림

![Docker 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/05/05-01-concept-at-a-glance.ko.png)

*Docker 101 5장 흐름 개요*

## 왜 이 글이 중요한가

신규 개발자 온보딩 문서가 길어진다는 것은 대개 환경 구성이 코드가 아니라 설명으로 남아 있다는 뜻입니다. 웹은 이렇게 띄우고, DB는 저렇게 띄우고, 순서는 이것을 따르라고 적어 놓기 시작하면, 문서는 곧 낡고 실행 환경은 사람마다 달라집니다.

Compose는 이 문제를 짧고 명시적인 선언으로 바꿉니다. `docker compose up` 한 줄이 온보딩 문서보다 더 강한 이유는, 설명이 아니라 실제 동작을 표준화하기 때문입니다.

## 한눈에 보는 개념

## 핵심 용어

- **Service**: 하나의 이미지에서 만들어지는 컨테이너 집합입니다.
- **Project**: Compose가 함께 관리하는 논리적 단위입니다.
- **Profile**: 특정 상황에서만 켜는 서비스 묶음입니다.
- **Healthcheck**: 서비스 준비 상태를 판단하는 기준입니다.
- **depends_on**: 시작 순서와 대기 조건을 정의하는 관계입니다.

이 중에서 가장 자주 오해되는 것은 `depends_on`입니다. 많은 입문자가 이것만 있으면 "DB가 준비될 때까지 기다린다"고 생각하지만, 실제로는 healthcheck와 함께 써야 의미 있는 준비 상태 보장이 됩니다.

## 전과 후

**Before**: `docker run` 다섯 개를 셸 스크립트로 묶고, 옵션은 기억이나 문서에 의존합니다.

**After**: `docker compose up`으로 서비스 구성이 YAML에 명시된 그대로 올라옵니다.

이 차이는 단순히 명령 길이가 짧아진다는 뜻이 아닙니다. 팀이 공유하는 실행 환경이 문장이 아니라 선언 파일이 되는 순간부터, 환경 자체를 코드 리뷰하고 버전 관리할 수 있게 됩니다.

## 실습: Compose를 5단계로 구성하기

### 1단계 — `compose.yaml` 작성

```yaml
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment:
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
volumes:
  pgdata:
```

이 예제는 Compose의 핵심을 한 번에 보여 줍니다. 서비스 정의, 볼륨 선언, 환경변수, 의존 관계, healthcheck가 모두 하나의 파일 안에 들어갑니다.

### 2단계 — 실행과 상태 확인

```bash
docker compose up -d
docker compose ps
docker compose logs -f web
```

이제 멀티 컨테이너 환경도 단일 프로젝트처럼 다룰 수 있습니다. 개별 `docker ps` 대신 Compose 단위로 상태와 로그를 보는 습관이 중요합니다.

### 3단계 — 변수 분리하기

```bash
# .env
DB_PASSWORD=dev
APP_PORT=8000
```

```yaml
environment:
  POSTGRES_PASSWORD: ${DB_PASSWORD}
ports: ["${APP_PORT}:8000"]
```

환경별 차이를 YAML에 하드코딩하지 않고 외부 변수로 빼면, 같은 Compose 파일을 훨씬 오래 재사용할 수 있습니다. 다만 이 방식은 비밀값 관리와 함께 생각해야 합니다.

### 4단계 — profile 사용하기

```yaml
services:
  worker:
    image: myapp:1.0
    profiles: ["worker"]
```

```bash
docker compose --profile worker up -d
```

profile은 선택적 서비스를 구조적으로 분리하는 방법입니다. 개발 환경에서는 필요하지만 항상 켤 필요는 없는 워커, 모니터링, 디버깅 도구에 특히 유용합니다.

### 5단계 — 정리하기

```bash
docker compose down            # remove containers
docker compose down -v         # also remove volumes
```

내리는 방법도 중요합니다. 특히 `down -v`는 볼륨까지 함께 제거하므로, 언제 데이터를 버려도 되는지 분명히 알고 써야 합니다.

### 실행 뒤 바로 확인할 것

- `docker compose ps`에서 db가 `healthy`가 된 뒤 web이 올라와야 합니다. 시작 순서만 맞고 health 상태가 비어 있으면 아직 준비 보장이 없습니다.
- `docker compose logs -f web`에서 앱이 DB 연결 오류 없이 기동하는지 확인합니다.

### 잘 안 될 때 먼저 볼 것

- web이 너무 빨리 실패하면 `depends_on`에 `condition: service_healthy`가 들어갔는지 먼저 확인합니다.
- `down -v` 뒤 데이터가 사라졌다면 의도한 동작입니다. 테스트 데이터와 유지해야 할 데이터를 같은 volume에 두지 않았는지 돌아봅니다.

## 이 코드에서 먼저 봐야 할 점

- `healthcheck + condition: service_healthy` 조합이 실제 준비 상태를 반영합니다.
- `depends_on`만으로는 시작 순서만 보장될 뿐, 준비 완료는 보장되지 않습니다.
- optional 서비스는 profile로 분리하는 것이 표준적입니다.

Compose에서 가장 흔한 오해는 "순서대로 시작했으니 이제 연결해도 된다"는 생각입니다. 하지만 DB 프로세스가 떠 있는 것과 실제로 요청을 받을 준비가 된 것은 다른 문제입니다.

## 자주 하는 실수 다섯 가지

1. **`depends_on`만 믿고 DB 준비 전에 연결합니다.** healthcheck가 없으면 cold start 실패가 납니다.
2. **`up`만 반복하고 `down -v`의 의미를 모릅니다.** 이전 데이터가 남아 테스트 결과를 오염시킬 수 있습니다.
3. **`.env`를 그대로 커밋합니다.** 비밀값 유출로 이어집니다.
4. **profile 없이 모든 서비스를 항상 띄웁니다.** 자원 낭비와 복잡성 증가로 이어집니다.
5. **여러 프로젝트가 같은 포트를 씁니다.** 충돌이 나고 문제 원인이 헷갈립니다.

Compose는 편리한 도구이지만, 선언이 명확하지 않으면 오히려 잘못된 가정을 영구화할 수도 있습니다. 그래서 healthcheck, 변수 분리, profile 사용이 중요합니다.

## 실무에서는 이렇게 이어집니다

많은 회사에서 로컬 개발 환경은 Compose 위에서 돌아갑니다. 또한 CI에서도 통합 테스트를 위해 DB, 캐시, 애플리케이션을 함께 띄워야 할 때 Compose를 자주 사용합니다. 즉, Compose는 개발 전용 편의 도구라기보다 팀 환경 재현 도구에 가깝습니다.

운영 배포가 Kubernetes로 가더라도 Compose 경험은 헛되지 않습니다. 서비스 관계, 준비 상태, 환경 변수 외부화 같은 핵심 감각은 그대로 이어지기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 환경 구성은 한 번의 명령으로 끝나야 합니다.
- healthcheck 없는 `depends_on`은 준비 상태를 보장하지 못합니다.
- `.env`와 `.env.example`은 분리해야 합니다.
- profile은 복잡성을 통제하는 좋은 장치입니다.
- `down -v`는 복구 가능한 상태에서만 써야 합니다.

이 기준을 가지고 다음 글의 환경 변수와 설정 주제로 넘어가면, 왜 같은 이미지를 여러 환경에서 다르게 동작시키는 설계가 중요한지도 더 잘 연결됩니다.

## 체크리스트

- [ ] 모든 서비스가 하나의 `compose.yaml`에 정의되어 있습니다.
- [ ] 의존 서비스에 healthcheck가 있습니다.
- [ ] `.env`와 `.env.example`이 분리되어 있습니다.
- [ ] 선택적 서비스는 profile로 분리되어 있습니다.

## 연습 문제

1. Compose로 web, db, redis를 함께 띄워 보세요.
2. db에 healthcheck를 추가해 web이 준비 이후 시작되게 해 보세요.
3. 포트 값을 `.env`로 분리해 YAML에서 참조해 보세요.

## 정리 및 다음 단계

Compose는 팀이 처음으로 갖게 되는 환경 코드인 경우가 많습니다. 여러 `docker run` 명령을 암기하는 대신, 서비스 구조를 선언으로 남기고 동일한 환경을 반복해서 띄울 수 있게 해 주기 때문입니다. Compose를 잘 쓰기 시작하면 온보딩, 테스트, 로컬 재현이 훨씬 단단해집니다.

다음 글에서는 환경 변수와 설정을 다룹니다. 이제 여러 컨테이너를 함께 띄울 수 있게 되었으니, 같은 이미지를 dev, staging, prod에서 어떻게 다르게 설정할지 살펴볼 차례입니다.


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

### 현장 점검 메모

- 배포 직전에는 `docker ps`, `docker logs`, `docker inspect` 세 명령으로 상태, 로그, 설정을 한 번에 교차 확인합니다.
- 장애 재현 시에는 증상 기록(시간, 요청, 에러 코드)을 먼저 남긴 뒤 설정 변경을 적용해야 원인 추적이 가능합니다.
- 팀 기준 문서에는 "정상 신호"와 "실패 신호"를 함께 기록해, 누가 봐도 같은 결론에 도달할 수 있게 만드는 편이 좋습니다.

## 처음 질문으로 돌아가기

- **여러 컨테이너를 한 번에 재현 가능하게 실행하려면 무엇이 필요할까요?**
  - 본문의 기준은 Docker Compose를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **service, network, volume은 Compose에서 어떻게 정의할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`depends_on`과 healthcheck는 어떤 관계로 이해해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- **Docker Compose (현재 글)**
- 환경변수와 설정 (예정)
- Python 앱 컨테이너화 (예정)
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Compose specification](https://docs.docker.com/compose/compose-file/)
- [Overview of Compose](https://docs.docker.com/compose/)
- [Compose profiles](https://docs.docker.com/compose/profiles/)
- [Healthcheck in Compose](https://docs.docker.com/compose/compose-file/05-services/#healthcheck)

### 검증과 트러블슈팅

- [Compose startup order and dependency conditions](https://docs.docker.com/compose/how-tos/startup-order/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Compose, YAML, MultiContainer, Dev