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

애플리케이션 컨테이너만 잘 만들었다고 해서 실제 서비스 구성이 끝난 것은 아닙니다. 대부분의 애플리케이션은 결국 데이터베이스와 함께 움직입니다. 문제는 여기서부터 훨씬 현실적이 됩니다. 앱이 먼저 떠 버리면 DB가 아직 준비되지 않아 실패하고, 스키마 변경이 자동화되지 않으면 배포마다 사람이 개입해야 하며, 시드 데이터가 중복으로 들어가면 환경이 점점 더 지저분해집니다.

그래서 앱과 DB를 함께 실행하는 구조에서는 세 가지 리듬이 중요합니다. 데이터의 영속성, 준비 상태 확인, 그리고 마이그레이션 자동화입니다. 이 세 가지가 맞물려야 로컬 개발, CI, 운영 전환이 부드러워집니다.

이 글은 Docker 101 시리즈의 8번째 글입니다. 여기서는 앱과 PostgreSQL을 함께 띄울 때 persistence·readiness·migration이라는 세 리듬을 어떻게 맞춰야 하는지, 그리고 migration과 seed를 어떤 순서로 검증해야 하는지 정리합니다.

## 먼저 던지는 질문

- Compose로 PostgreSQL과 앱을 어떻게 함께 띄울까요?
- healthcheck와 시작 순서는 어떻게 연결해야 할까요?
- Alembic migration은 어떤 방식으로 자동화하는 편이 좋을까요?

## 큰 그림

![Docker 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/08/08-01-concept-at-a-glance.ko.png)

*Docker 101 8장 흐름 개요*

이 그림에서는 데이터베이스와 함께 실행하기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 데이터베이스와 함께 실행하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## Before / After

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

Tags: Docker, Postgres, Compose, Migration, Healthcheck
