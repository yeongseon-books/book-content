---
series: docker-101
episode: 8
title: "Docker 101 (8/10): 데이터베이스와 함께 실행하기"
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
  - Postgres
  - Compose
  - Migration
  - Healthcheck
seo_description: FastAPI와 PostgreSQL을 Compose로 함께 띄우는 운영 기본 구성을 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (8/10): 데이터베이스와 함께 실행하기

이 글은 Docker 101 시리즈의 8번째 글입니다.


애플리케이션 컨테이너만 잘 만들었다고 해서 실제 서비스 구성이 끝난 것은 아닙니다. 대부분의 애플리케이션은 결국 데이터베이스와 함께 움직입니다. 문제는 여기서부터 훨씬 현실적이 됩니다. 앱이 먼저 떠 버리면 DB가 아직 준비되지 않아 실패하고, 스키마 변경이 자동화되지 않으면 배포마다 사람이 개입해야 하며, 시드 데이터가 중복으로 들어가면 환경이 점점 더 지저분해집니다.

그래서 앱과 DB를 함께 실행하는 구조에서는 세 가지 리듬이 중요합니다. 데이터의 영속성, 준비 상태 확인, 그리고 마이그레이션 자동화입니다. 이 세 가지가 맞물려야 로컬 개발, CI, 운영 전환이 부드러워집니다.


![Docker 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/08/08-01-concept-at-a-glance.ko.png)
*Docker 101 8장 흐름 개요*

## 먼저 던지는 질문

- Compose로 PostgreSQL과 앱을 어떻게 함께 띄울까요?
- healthcheck와 시작 순서는 어떻게 연결해야 할까요?
- Alembic migration은 어떤 방식으로 자동화하는 편이 좋을까요?

## 왜 이 글이 중요한가

앱은 뜨지만 DB가 준비되지 않은 상태에서 연결을 시도하면 cold start 사고가 납니다. 반대로 DB는 떠 있는데 마이그레이션이 아직 적용되지 않았으면 애플리케이션은 엉뚱한 스키마를 보고 실패합니다. 결국 앱과 DB 경계는 가장 흔한 장애 지점이면서, 동시에 가장 큰 자동화 기회이기도 합니다.

특히 새 환경을 만들 때마다 수동 SQL을 실행하거나, 웹 컨테이너가 뜰 때마다 migration을 함께 돌리는 방식은 시간이 지나면 반드시 문제를 만듭니다. 마이그레이션은 자동이어야 하고, 가능하면 단일 실행자로 분리되어야 합니다.

## 한눈에 보는 개념

## 핵심 용어

- **Migration**: 데이터베이스 스키마를 버전 관리하는 방식입니다.
- **Seed**: 초기 기준 데이터를 넣는 작업입니다.
- **Healthcheck**: DB가 실제 요청을 받을 준비가 되었는지 알리는 신호입니다.
- **Init container**: 한 번만 실행되는 migration 전용 컨테이너입니다.
- **Volume**: DB 데이터를 영구 저장하는 영역입니다.

이 다섯 가지는 하나의 흐름으로 이해하는 편이 좋습니다. 데이터는 volume에 남고, 준비 상태는 healthcheck가 알리며, schema 변화는 migration이 책임지고, 초기값은 seed가 담당합니다.

## 전과 후

**Before**: 새 환경마다 수동 SQL을 적용하고, 마이그레이션 순서를 사람 기억에 의존합니다.

**After**: `docker compose up` 한 줄로 DB, migration, 앱이 순서대로 올라옵니다.

이 차이는 단순한 편의성이 아닙니다. 팀이 환경을 다시 만드는 비용을 얼마나 낮출 수 있는지와 직결됩니다. 재현 가능한 데이터베이스 초기화는 애플리케이션 품질의 일부입니다.

## 실습: 앱과 DB를 5단계로 묶기

### 1단계 — `compose.yaml` 작성

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app"]
      interval: 5s
      retries: 10

  migrate:
    image: myapi:1.0
    command: ["alembic", "upgrade", "head"]
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:dev@db/app
    depends_on:
      db: { condition: service_healthy }

  web:
    image: myapi:1.0
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:dev@db/app
    depends_on:
      migrate: { condition: service_completed_successfully }

volumes:
  pgdata:
```

이 구성의 핵심은 역할 분리입니다. DB는 데이터를 유지하고, migrate는 스키마를 맞추고, web은 애플리케이션 요청만 처리합니다. 각 책임이 분리될수록 장애 원인도 더 명확해집니다.

### 2단계 — Alembic 초기화

```bash
docker compose run --rm migrate alembic init alembic
docker compose run --rm migrate alembic revision --autogenerate -m "init"
```

마이그레이션 체계를 먼저 세우는 이유는 이후의 모든 스키마 변경을 기록 가능한 형태로 남기기 위해서입니다. 수동 SQL보다 느려 보여도, 결국 운영에서는 훨씬 빠르고 안전합니다.

### 3단계 — seed 작성

```python
# app/seed.py
def seed(session) -> None:
    if session.query(User).count() == 0:
        session.add(User(email="admin@example.com"))
        session.commit()
```

```yaml
seed:
  image: myapi:1.0
  command: ["python", "-m", "app.seed"]
  depends_on:
    migrate: { condition: service_completed_successfully }
```

seed는 반드시 여러 번 실행해도 같은 결과가 나와야 합니다. 그래야 새 환경, 재배포, 테스트 환경 재생성에서 예측 가능한 상태를 유지할 수 있습니다.

### 4단계 — 실행과 검증

```bash
docker compose up -d
docker compose exec db psql -U postgres -d app -c "\dt"
curl http://localhost:8000/users
```

여기서는 앱이 뜨는지만 보지 말고, 테이블이 실제로 만들어졌는지와 애플리케이션이 DB를 통해 데이터를 읽을 수 있는지를 함께 확인해야 합니다. 앱과 DB는 항상 경계 단위로 검증하는 편이 좋습니다.

### 5단계 — 백업

```bash
docker compose exec db pg_dump -U postgres app > app.sql
```

영속성을 확보했다고 해서 끝이 아닙니다. 백업 명령이 문서화되어 있어야 사고 이후 복구 가능성까지 확보됩니다. volume만 믿는 것은 운영 기준으로는 부족합니다.

### 실행 뒤 바로 확인할 것

- `docker compose exec db psql -U postgres -d app -c "\dt"`에서 마이그레이션 결과 테이블이 보여야 하고, `curl http://localhost:8000/users`가 DB 기반 응답을 반환해야 합니다.
- seed를 두 번 실행해도 레코드가 중복되지 않아야 같은 seed를 다시 실행해도 환경이 흔들리지 않습니다.

### 잘 안 될 때 먼저 볼 것

- web이 바로 죽으면 DB readiness보다 migration 성공 여부를 먼저 확인합니다. `docker compose logs migrate`가 가장 빠른 단서입니다.
- `pg_dump` 백업이 비어 있으면 DB 이름이나 권한보다 먼저 실제 volume에 데이터가 쌓였는지 확인합니다.

## 이 코드에서 먼저 봐야 할 점

- `condition: service_healthy`가 실제 준비 상태를 보장합니다.
- `migrate`는 한 번만 실행되는 init container 역할을 합니다.
- seed는 반드시 여러 번 실행해도 같은 상태를 유지해야 합니다.

특히 migration을 web entrypoint에서 함께 돌리지 않는 점이 중요합니다. 웹 서버가 여러 개라면 같은 migration이 중복 실행될 수 있고, 실패 모드도 훨씬 복잡해집니다.

## 자주 하는 실수 다섯 가지

1. **`depends_on`만으로 연결 준비를 보장한다고 생각합니다.** healthcheck가 없으면 cold start 실패가 납니다.
2. **migration을 web 컨테이너 시작 명령에 넣습니다.** 여러 워커가 동시에 재실행할 수 있습니다.
3. **DB 데이터를 bind mount에 둡니다.** 권한과 성능 문제가 잦습니다.
4. **기본 `POSTGRES_PASSWORD`를 그대로 둡니다.** 노출 즉시 위험해집니다.
5. **백업 절차를 만들지 않습니다.** 사고 시 복구 경로가 없습니다.

이 실수들은 모두 "일단 로컬에서만 되면 된다"는 태도에서 나옵니다. 하지만 앱과 DB는 가장 먼저 운영 감각이 필요한 경계입니다.

## 실무에서는 이렇게 이어집니다

운영에서는 RDS, Cloud SQL 같은 관리형 데이터베이스를 쓰는 경우가 많습니다. 그래도 로컬 개발과 CI에서는 Compose 기반 구성을 유지해 환경 간 차이를 줄이는 팀이 많습니다. 즉, 데이터 저장 위치는 바뀌어도 readiness, migration, seed라는 운영 패턴은 그대로 남습니다.

또한 사고 분석에서도 같은 구조가 유효합니다. 연결 실패인지, 스키마 불일치인지, 데이터 초기화 문제인지 경계를 분리해 볼 수 있기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- migration은 자동이고, idempotent하며, 단일 실행자가 책임져야 합니다.
- healthcheck가 정직해야 시작 순서가 의미를 가집니다.
- DB 데이터는 named volume이나 관리형 스토리지에 두고, 항상 백업합니다.
- seed는 편의 기능이 아니라 재현성 장치입니다.
- 비밀번호는 secret 저장소에서 오고, 기본값은 운영에서 허용하지 않습니다.

이 기준을 잡고 나면 다음 글의 이미지 최적화도 왜 중요한지 명확해집니다. 앱과 DB 구성이 안정되면, 이제 빌드와 pull 속도를 줄여 팀 전체 피드백 루프를 더 빠르게 만들 수 있기 때문입니다.

## 체크리스트

- [ ] DB에 healthcheck가 있습니다.
- [ ] migration이 one-shot 컨테이너로 분리되어 있습니다.
- [ ] 데이터가 named volume에 저장됩니다.
- [ ] 백업 명령이 문서화되어 있습니다.

## 연습 문제

1. Compose로 postgres, migrate, web을 순서대로 실행해 보세요.
2. Alembic migration이 자동 실행되도록 구성해 보세요.
3. 여러 번 실행해도 안전한 idempotent seed를 작성해 보세요.

## 정리 및 다음 단계

앱과 데이터베이스를 함께 운영하는 순간부터 컨테이너는 진짜 서비스 구조가 됩니다. 이때 중요한 것은 단순히 둘을 같이 띄우는 것이 아니라, 데이터 영속성, 준비 상태, migration 자동화라는 세 가지 리듬을 안정적으로 맞추는 것입니다. 이 경계가 깔끔할수록 팀 셋업 비용은 줄고, 배포 실패도 훨씬 예측 가능해집니다.

다음 글에서는 이미지 최적화를 다룹니다. 이제 구성이 안정되었으니, 빌드 시간과 이미지 크기를 줄여 개발 속도와 배포 효율을 함께 끌어올릴 차례입니다.


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

- **Compose로 PostgreSQL과 앱을 어떻게 함께 띄울까요?**
  - 본문의 기준은 데이터베이스와 함께 실행하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **healthcheck와 시작 순서는 어떻게 연결해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Alembic migration은 어떤 방식으로 자동화하는 편이 좋을까요?**
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
- **데이터베이스와 함께 실행하기 (현재 글)**
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [PostgreSQL official image](https://hub.docker.com/_/postgres)
- [Compose - service_completed_successfully](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- [pg_isready](https://www.postgresql.org/docs/current/app-pg-isready.html)

### 검증과 트러블슈팅

- [docker compose run reference](https://docs.docker.com/reference/cli/docker/compose/run/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Postgres, Compose, Migration, Healthcheck