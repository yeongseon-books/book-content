---
series: docker-101
episode: 5
title: "Docker 101 (5/10): Docker Compose"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/257"
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
  - Compose
  - YAML
  - MultiContainer
  - Dev
seo_description: Docker Compose로 멀티 컨테이너 환경을 한 파일에서 재현 가능하게 관리합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (5/10): Docker Compose

컨테이너가 하나일 때는 `docker run` 몇 줄로도 충분합니다. 하지만 웹 애플리케이션, 데이터베이스, 캐시, 워커처럼 구성 요소가 늘어나는 순간부터 명령어 기반 운영은 빠르게 한계에 부딪힙니다. 누가 먼저 떠야 하는지, 어떤 환경변수를 넣어야 하는지, 어떤 볼륨과 네트워크를 써야 하는지를 매번 기억에 의존하게 되기 때문입니다.

이 글은 Docker 101 시리즈의 5번째 글입니다.

Docker Compose는 이 문제를 YAML 하나로 정리합니다. 서비스, 네트워크, 볼륨, 의존 관계를 선언해 두면 팀 전체가 같은 멀티 컨테이너 환경을 같은 방식으로 띄울 수 있습니다. Compose는 많은 팀에서 사실상 첫 번째 인프라 코드입니다.

![Docker 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/05/05-01-concept-at-a-glance.ko.png)
*Docker 101 5장 흐름 개요*

> Compose는 docker run의 편의 래퍼가 아니라 많은 팀의 '첫 번째 인프라 코드'입니다 — 서비스·네트워크·볼륨·의존 관계를 YAML로 선언해 두면 멀티 컨테이너 환경이 사람의 기억이 아니라 파일로 재현 가능해지고, 새 팀원도 같은 환경을 같은 명령으로 띄울 수 있습니다.

## 이 글에서 다룰 문제

- 여러 컨테이너를 한 번에 재현 가능하게 실행하려면 무엇이 필요할까요?
- service, network, volume은 Compose에서 어떻게 정의할까요?
- `depends_on`과 healthcheck는 어떤 관계로 이해해야 할까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

신규 개발자 온보딩 문서가 길어진다는 것은 대개 환경 구성이 코드가 아니라 설명으로 남아 있다는 뜻입니다. 웹은 이렇게 띄우고, DB는 저렇게 띄우고, 순서는 이것을 따르라고 적어 놓기 시작하면, 문서는 곧 낡고 실행 환경은 사람마다 달라집니다.

Compose는 이 문제를 짧고 명시적인 선언으로 바꿉니다. `docker compose up` 한 줄이 온보딩 문서보다 더 강한 이유는, 설명이 아니라 실제 동작을 표준화하기 때문입니다.

| 개념 | 설명 | 예시 |
|------|------|------|
| **Service** | 하나의 이미지에서 만들어지는 컨테이너 집합 | `web`, `db`, `redis` |
| **Project** | Compose가 함께 관리하는 논리적 단위 | 디렉터리 이름이 기본 프로젝트 이름 |
| **Profile** | 특정 상황에서만 켜는 서비스 묶음 | `worker`, `monitoring` |
| **Healthcheck** | 서비스 준비 상태를 판단하는 기준 | `pg_isready`, `curl -f /healthz` |
| **depends_on** | 시작 순서와 대기 조건 정의 | `condition: service_healthy` |

이 중에서 가장 자주 오해되는 것은 `depends_on`입니다. 많은 입문자가 이것만 있으면 "DB가 준비될 때까지 기다린다"고 생각하지만, 실제로는 healthcheck와 함께 써야 의미 있는 준비 상태 보장이 됩니다.

## 전과 후

**Before**: `docker run` 다섯 개를 셸 스크립트로 묶고, 옵션은 기억이나 문서에 의존합니다. 새 팀원이 오면 반나절을 환경 구성에 씁니다.

**After**: `docker compose up`으로 서비스 구성이 YAML에 명시된 그대로 올라옵니다. 신규 입사자도 `git clone` 후 한 줄로 실행합니다.

이 차이는 단순히 명령 길이가 짧아진다는 뜻이 아닙니다. 팀이 공유하는 실행 환경이 문장이 아니라 선언 파일이 되는 순간부터, 환경 자체를 코드 리뷰하고 버전 관리할 수 있게 됩니다.

## 실습: Compose를 5단계로 구성하기

### 1단계 — 완성된 `compose.yaml` 작성

```yaml
# compose.yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOST: db
      DB_PORT: 5432
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: app
      POSTGRES_USER: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  cache:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3

volumes:
  pgdata:
  redisdata:
```

이 예제는 Compose의 핵심을 한 번에 보여 줍니다. 서비스 정의, 볼륨 선언, 환경변수, 의존 관계, healthcheck가 모두 하나의 파일 안에 들어갑니다. `start_period`는 healthcheck가 처음 시작을 기다리는 시간으로, DB 초기화 시간을 고려한 설정입니다.

### 2단계 — 실행과 상태 확인

```bash
# 백그라운드로 실행
docker compose up -d

# 서비스 상태 확인 (healthy 상태 확인 중요)
docker compose ps

# 특정 서비스 로그
docker compose logs -f web

# 모든 서비스 로그
docker compose logs -f

# 실행 중인 서비스 내부 진입
docker compose exec db psql -U postgres -d app

# 서비스 재시작
docker compose restart web
```

이제 멀티 컨테이너 환경도 단일 프로젝트처럼 다룰 수 있습니다. 개별 `docker ps` 대신 Compose 단위로 상태와 로그를 보는 습관이 중요합니다.

### 3단계 — 환경변수 파일 분리하기

```bash
# .env.example (Git에 커밋)
DB_PASSWORD=change_me
APP_PORT=8000
REDIS_MAX_MEMORY=256mb

# .env (Git에 커밋하지 않음 - .gitignore에 추가)
DB_PASSWORD=dev_secret_123
APP_PORT=8000
REDIS_MAX_MEMORY=256mb
```

```yaml
# compose.yaml에서 변수 참조
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
  web:
    ports:
      - "${APP_PORT}:8000"
  cache:
    command: redis-server --maxmemory ${REDIS_MAX_MEMORY:-256mb}
```

환경별 차이를 YAML에 하드코딩하지 않고 외부 변수로 빼면, 같은 Compose 파일을 훨씬 오래 재사용할 수 있습니다. `${VAR:-default}` 문법으로 기본값도 설정할 수 있습니다.

### 4단계 — profile 사용하기

```yaml
services:
  web:
    build: .
    ports: ["8000:8000"]

  db:
    image: postgres:16
    # profile 없으면 항상 실행

  worker:
    image: myapp:1.0
    command: ["python", "-m", "celery", "worker"]
    profiles: ["worker"]   # --profile worker 시에만 실행

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    profiles: ["monitoring"]   # --profile monitoring 시에만 실행

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    profiles: ["monitoring"]
```

```bash
# 기본 서비스만 실행
docker compose up -d

# 워커 포함 실행
docker compose --profile worker up -d

# 모니터링 포함 실행
docker compose --profile monitoring up -d

# 여러 profile 동시 활성화
docker compose --profile worker --profile monitoring up -d
```

profile은 선택적 서비스를 구조적으로 분리하는 방법입니다. 개발 환경에서는 필요하지만 항상 켤 필요는 없는 워커, 모니터링, 디버깅 도구에 특히 유용합니다.

### 5단계 — 정리와 데이터 관리

```bash
# 컨테이너만 내리기 (볼륨 유지)
docker compose down

# 컨테이너 + 볼륨 함께 제거 (데이터 삭제)
docker compose down -v

# 이미지까지 함께 제거
docker compose down --rmi all

# 멈춘 서비스 재시작 없이 설정 확인
docker compose config

# 실행 없이 YAML 유효성 검사
docker compose config --quiet && echo "Valid"

# 특정 서비스만 내리기
docker compose stop web
docker compose rm -f web
```

내리는 방법도 중요합니다. 특히 `down -v`는 볼륨까지 함께 제거하므로, 언제 데이터를 버려도 되는지 분명히 알고 써야 합니다.

### 실행 뒤 바로 확인할 것

- `docker compose ps`에서 db가 `healthy`가 된 뒤 web이 올라와야 합니다. db 상태가 `starting`이나 `unhealthy`이면 web은 기다리거나 재시도합니다.
- `docker compose logs -f web`에서 앱이 DB 연결 오류 없이 기동하는지 확인합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| web이 DB 연결 실패로 종료됨 | `depends_on`에 `condition: service_healthy` 없음 | healthcheck + condition 설정 |
| `down -v` 후 데이터 사라짐 | 의도한 동작 (볼륨 삭제) | `-v` 없이 `down` 사용, 중요 데이터는 백업 먼저 |
| 포트 충돌 (`address already in use`) | 다른 프로세스나 Compose 프로젝트가 같은 포트 사용 | `lsof -i :8000`으로 확인, 포트 변경 |
| `.env` 값이 반영 안 됨 | `.env` 파일 위치나 변수명 오타 | `docker compose config`로 실제 값 확인 |
| healthcheck 계속 실패 | DB 초기화 시간이 `start_period`보다 김 | `start_period` 값을 늘림 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| `depends_on`만 믿고 DB 준비 전 연결 | cold start 실패 빈발 | `healthcheck + condition: service_healthy` 필수 |
| `.env`를 Git에 커밋 | 비밀값 유출 | `.gitignore`에 `.env` 추가, `.env.example` 관리 |
| `down -v`의 의미를 모름 | 이전 데이터 영구 삭제 | 볼륨 내용 확인 후 사용 |
| profile 없이 모든 서비스 항상 실행 | 자원 낭비, 복잡성 증가 | 선택적 서비스는 profile로 분리 |
| 여러 프로젝트가 같은 포트 사용 | 충돌과 혼동 | `.env`로 포트를 프로젝트별로 분리 |

## Compose 파일 구조 참조

```yaml
# compose.yaml 전체 구조
name: myproject        # 프로젝트 이름 (선택, 기본은 디렉터리 이름)

services:
  service-name:
    image: image:tag          # 기존 이미지 사용
    build:                    # 또는 Dockerfile 빌드
      context: .
      dockerfile: Dockerfile
    ports:
      - "호스트:컨테이너"
    environment:
      KEY: value
    env_file:
      - .env.dev
    volumes:
      - named-volume:/path
      - ./local:/container
    networks:
      - app-net
    depends_on:
      other-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "..."]
      interval: 5s
      timeout: 3s
      retries: 3
      start_period: 10s
    restart: unless-stopped   # no, always, on-failure, unless-stopped
    profiles: ["optional"]
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M

volumes:
  named-volume:              # Docker 관리 볼륨
  external-volume:
    external: true           # 미리 생성된 외부 볼륨

networks:
  app-net:                   # 사용자 정의 네트워크
    driver: bridge
```

## 실무에서는 이렇게 이어집니다

많은 회사에서 로컬 개발 환경은 Compose 위에서 돌아갑니다. 또한 CI에서도 통합 테스트를 위해 DB, 캐시, 애플리케이션을 함께 띄워야 할 때 Compose를 자주 사용합니다. 즉, Compose는 개발 전용 편의 도구라기보다 팀 환경 재현 도구에 가깝습니다.

운영 배포가 Kubernetes로 가더라도 Compose 경험은 헛되지 않습니다. 서비스 관계, 준비 상태, 환경 변수 외부화 같은 핵심 감각은 그대로 이어지기 때문입니다.

## 운영 체크리스트

- [ ] 모든 서비스가 하나의 `compose.yaml`에 정의되어 있습니다.
- [ ] 의존 서비스에 healthcheck가 있습니다.
- [ ] `.env`와 `.env.example`이 분리되어 있습니다.
- [ ] 선택적 서비스는 profile로 분리되어 있습니다.
- [ ] `docker compose config`로 YAML 유효성을 검사했습니다.
- [ ] volume 백업 전략이 있습니다.

## Compose로 실제 개발 환경 구성하기

다음은 실제 팀에서 쓸 수 있는 전체 개발 환경 예시입니다.

```yaml
# compose.yaml (개발용 완성 예시)
name: myproject

services:
  web:
    build:
      context: .
      target: runtime    # 멀티스테이지 중 runtime 스테이지
    ports:
      - "${APP_PORT:-8000}:8000"
    volumes:
      - .:/app           # 개발 중 코드 변경 즉시 반영 (hot reload)
    environment:
      DB_URL: postgresql+psycopg://postgres:dev@db/app
      REDIS_URL: redis://cache:6379
      LOG_LEVEL: DEBUG
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_healthy }
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app"]
      interval: 5s
      retries: 5
    ports:
      - "5432:5432"    # 로컬 DB 클라이언트 접속용 (개발에서만)

  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
    ports:
      - "6379:6379"    # 로컬 Redis 클라이언트 접속용 (개발에서만)

  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "8025:8025"    # 웹 UI
    profiles: ["email"]  # --profile email 시에만 실행

volumes:
  pgdata:
```

## 연습 문제

1. Compose로 web(FastAPI), db(PostgreSQL), cache(Redis)를 함께 띄워 보세요. 각 서비스에 healthcheck를 추가해 보세요.
2. DB에 healthcheck를 추가해 web이 DB 준비 완료 이후 시작되게 해 보세요.
3. 포트 값을 `.env`로 분리해 YAML에서 참조해 보세요. `docker compose config`로 실제 값이 반영됐는지 확인해 보세요.
4. worker 서비스를 profile로 분리하고 `--profile worker`로만 실행해 보세요.

## 처음 질문으로 돌아가기

- **여러 컨테이너를 한 번에 재현 가능하게 실행하려면 무엇이 필요할까요?**
  - 서비스 정의(이미지/빌드), 네트워크 연결, 볼륨 선언, 환경변수, 의존 관계와 준비 상태 확인이 모두 YAML 한 파일에 선언되어야 합니다. 그래야 `docker compose up` 한 줄로 팀 전체가 같은 환경을 재현할 수 있습니다.

- **service, network, volume은 Compose에서 어떻게 정의할까요?**
  - `services`에서 각 컨테이너의 이미지, 포트, 환경변수를 선언합니다. `volumes`에서 named volume을 정의하고 서비스에서 참조합니다. 별도 `networks` 선언 없이도 같은 Compose 파일 내 서비스들은 자동으로 같은 네트워크에 연결됩니다.

- **`depends_on`과 healthcheck는 어떤 관계로 이해해야 할까요?**
  - `depends_on`만 쓰면 컨테이너 프로세스가 시작됐는지만 확인합니다. `condition: service_healthy`를 함께 써야 healthcheck가 성공한 이후 다음 서비스가 시작됩니다. DB 프로세스가 뜬 것과 요청을 받을 준비가 된 것은 다릅니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - `.env` 파일을 절대 Git에 커밋하지 말고 `.gitignore`에 추가해야 합니다. `docker compose down -v`는 데이터를 영구 삭제하므로 주의해야 합니다. 프로덕션용 비밀값은 Compose 파일이 아닌 외부 secret 관리 시스템(Vault, Doppler 등)에서 가져와야 합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - `depends_on`만 설정하고 healthcheck를 추가하지 않아 DB가 준비되기 전에 앱이 연결을 시도하는 경우가 가장 많습니다. DB 컨테이너가 `Up`이어도 실제 준비는 몇 초 더 걸릴 수 있습니다.

## 정리

Compose는 팀이 처음으로 갖게 되는 환경 코드인 경우가 많습니다. 여러 `docker run` 명령을 암기하는 대신, 서비스 구조를 선언으로 남기고 동일한 환경을 반복해서 띄울 수 있게 해 주기 때문입니다. Compose를 잘 쓰기 시작하면 온보딩, 테스트, 로컬 재현이 훨씬 단단해집니다.

다음 글에서는 환경 변수와 설정을 다룹니다. 이제 여러 컨테이너를 함께 띄울 수 있게 되었으니, 같은 이미지를 dev, staging, prod에서 어떻게 다르게 설정할지 살펴볼 차례입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- **Docker 101 (5/10): Docker Compose (현재 글)**
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- [배포용 Docker 구성](./10-production-docker.md)

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
