---
series: docker-101
episode: 8
title: 데이터베이스와 함께 실행하기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Docker
  - Postgres
  - Compose
  - Migration
  - Healthcheck
seo_description: PostgreSQL 과 FastAPI 를 Compose 로 함께 띄우고 마이그레이션, healthcheck, 시드까지 다루기
last_reviewed: '2026-05-11'
---

# 데이터베이스와 함께 실행하기

> Docker 101 시리즈 (8/10)


## 이 글에서 다룰 문제

DB 가 준비되지 않은 채 앱이 시작하면 cold start 사고가 납니다. 마이그레이션이 자동이 아니면 배포가 수동이 됩니다.

> *DB 와 앱의 결합은 *제일 흔한 사고 지점* 이자 *제일 큰 자동화 기회* 입니다.*

## 전체 흐름
```mermaid
flowchart LR
    Compose["compose.yaml"] --> Db["postgres + healthcheck"]
    Db -->|service_healthy| Mig["alembic upgrade head"]
    Mig --> Web["fastapi"]
```

## Before/After

**Before**: 새 환경마다 *수동 SQL*. 마이그레이션 *순서 의존*.

**After**: `docker compose up` 한 줄로 DB, 마이그레이션, 앱이 순서대로 기동합니다.

## DB 결합 5단계

### 1단계 — `compose.yaml`

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

### 2단계 — Alembic 초기화

```bash
docker compose run --rm migrate alembic init alembic
docker compose run --rm migrate alembic revision --autogenerate -m "init"
```

### 3단계 — 시드

```python
# app/seed.py 파일
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

### 4단계 — 띄우고 검증

```bash
docker compose up -d
docker compose exec db psql -U postgres -d app -c "\dt"
curl http://localhost:8000/users
```

### 5단계 — 백업

```bash
docker compose exec db pg_dump -U postgres app > app.sql
```

## 이 코드에서 주목할 점

- *condition: service_healthy* 가 *진짜 준비* 보장.
- `migrate` 는 *일회성 init container*.
- *seed* 는 *idempotent* 해야 한다.

## 자주 하는 실수 5가지

1. **`depends_on` 만으로 연결을 보장한다고 봅니다.** healthcheck 가 없으면 cold-start fail 이 납니다.
2. **마이그레이션을 *web 컨테이너 entrypoint* 에.** *워커마다 중복 실행*.
3. **DB 를 *bind mount* 로.** 권한/성능 문제.
4. **`POSTGRES_PASSWORD` 기본값을 유지합니다.** 외부에 노출되면 즉시 해킹당합니다.
5. ***백업 절차 없음*.** 사고 시 끝.

## 실무에서는 이렇게 쓰입니다

운영에서는 *RDS / Cloud SQL* 같은 *관리형 DB* 를 쓰지만, *로컬과 CI* 는 동일한 Compose 로 통일해 *환경 평등성* 을 유지합니다.

## 체크리스트

- [ ] DB *healthcheck* 가 있다.
- [ ] migrate 가 일회성으로 분리됐다.
- [ ] data volume 이 *named volume*.
- [ ] *백업 명령* 이 문서화됐다.

## 정리 및 다음 단계

DB 와의 결합이 깔끔해지면 *팀 전체의 셋업 비용* 이 *0* 에 수렴합니다. 다음 글에서는 *image 최적화* 로 *빌드와 풀* 을 빠르게 만듭니다.

<!-- toc:begin -->
- [Docker란 무엇인가?](./01-what-is-docker.md)
- [Image와 Container](./02-image-and-container.md)
- [Dockerfile 작성하기](./03-dockerfile.md)
- [Volume과 Network](./04-volume-and-network.md)
- [Docker Compose](./05-docker-compose.md)
- [환경변수와 설정](./06-env-and-config.md)
- [Python 앱 컨테이너화](./07-python-app-containerize.md)
- **데이터베이스와 함께 실행하기 (현재 글)**
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)
<!-- toc:end -->

## 참고 자료

- [PostgreSQL official image](https://hub.docker.com/_/postgres)
- [Compose - service_completed_successfully](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- [pg_isready](https://www.postgresql.org/docs/current/app-pg-isready.html)

Tags: Docker, Postgres, Compose, Migration, Healthcheck
