---
series: docker-101
episode: 8
title: "Docker 101 (8/10): 데이터베이스와 함께 실행하기"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/260"
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
  - Postgres
  - Compose
  - Migration
  - Healthcheck
seo_description: FastAPI와 PostgreSQL을 Compose로 함께 띄우는 운영 기본 구성을 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (8/10): 데이터베이스와 함께 실행하기

애플리케이션 컨테이너만 잘 만들었다고 해서 실제 서비스 구성이 끝난 것은 아닙니다. 대부분의 애플리케이션은 결국 데이터베이스와 함께 움직입니다. 문제는 여기서부터 훨씬 현실적이 됩니다. 앱이 먼저 떠 버리면 DB가 아직 준비되지 않아 실패하고, 스키마 변경이 자동화되지 않으면 배포마다 사람이 개입해야 하며, 시드 데이터가 중복으로 들어가면 환경이 점점 더 지저분해집니다.

이 글은 Docker 101 시리즈의 8번째 글입니다.

그래서 앱과 DB를 함께 실행하는 구조에서는 세 가지 리듬이 중요합니다. 데이터의 영속성, 준비 상태 확인, 그리고 마이그레이션 자동화입니다. 이 세 가지가 맞물려야 로컬 개발, CI, 운영 전환이 부드러워집니다.

![Docker 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/08/08-01-concept-at-a-glance.ko.png)
*Docker 101 8장 흐름 개요*

> 앱과 DB를 함께 실행하는 구조에서는 세 가지 리듬이 항상 같이 갑니다 — 데이터 영속성(volume), 준비 상태 확인(healthcheck/depends_on), 그리고 마이그레이션 자동화. 이 셋 중 하나라도 빠지면 배포마다 사람이 들어가야 하고, 환경이 점점 일관성을 잃습니다.

## 이 글에서 다룰 문제

- Compose로 PostgreSQL과 앱을 어떻게 함께 띄울까요?
- healthcheck와 시작 순서는 어떻게 연결해야 할까요?
- Alembic migration은 어떤 방식으로 자동화하는 편이 좋을까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

앱은 뜨지만 DB가 준비되지 않은 상태에서 연결을 시도하면 cold start 사고가 납니다. 반대로 DB는 떠 있는데 마이그레이션이 아직 적용되지 않았으면 애플리케이션은 엉뚱한 스키마를 보고 실패합니다. 결국 앱과 DB 경계는 가장 흔한 장애 지점이면서, 동시에 가장 큰 자동화 기회이기도 합니다.

| 개념 | 설명 | 역할 |
|------|------|------|
| **Migration** | DB 스키마를 버전 관리하는 방식 | 스키마 변경 추적, 자동 적용 |
| **Seed** | 초기 기준 데이터를 넣는 작업 | 개발/테스트 환경 초기화 |
| **Healthcheck** | DB가 요청을 받을 준비가 되었는지 알리는 신호 | 시작 순서 보장 |
| **Init container** | 한 번만 실행되는 migration 전용 컨테이너 | 중복 실행 방지 |
| **Volume** | DB 데이터를 영구 저장하는 영역 | 컨테이너 재시작 후 데이터 유지 |

## 전과 후

**Before**: 새 환경마다 수동 SQL을 적용하고, 마이그레이션 순서를 사람 기억에 의존합니다. 팀원이 "내 DB에는 이 테이블이 없는데..."라고 말하는 상황이 반복됩니다.

**After**: `docker compose up` 한 줄로 DB, migration, 앱이 순서대로 올라옵니다. 새 팀원도 같은 상태에서 시작할 수 있습니다.

이 차이는 단순한 편의성이 아닙니다. 팀이 환경을 다시 만드는 비용을 얼마나 낮출 수 있는지와 직결됩니다. 재현 가능한 데이터베이스 초기화는 애플리케이션 품질의 일부입니다.

## 실습: 앱과 DB를 5단계로 묶기

### 1단계 — 완성된 `compose.yaml` 작성

```yaml
# compose.yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:-dev}
      POSTGRES_DB: ${DB_NAME:-app}
      POSTGRES_USER: ${DB_USER:-postgres}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-app}"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
    restart: unless-stopped

  migrate:
    image: myapi:1.0
    command: ["alembic", "upgrade", "head"]
    environment:
      DATABASE_URL: postgresql+psycopg://${DB_USER:-postgres}:${DB_PASSWORD:-dev}@db/${DB_NAME:-app}
    depends_on:
      db:
        condition: service_healthy
    restart: "no"          # 한 번만 실행하고 성공하면 종료

  seed:
    image: myapi:1.0
    command: ["python", "-m", "app.seed"]
    environment:
      DATABASE_URL: postgresql+psycopg://${DB_USER:-postgres}:${DB_PASSWORD:-dev}@db/${DB_NAME:-app}
    depends_on:
      migrate:
        condition: service_completed_successfully
    restart: "no"

  web:
    image: myapi:1.0
    ports:
      - "${APP_PORT:-8000}:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://${DB_USER:-postgres}:${DB_PASSWORD:-dev}@db/${DB_NAME:-app}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    depends_on:
      migrate:
        condition: service_completed_successfully
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

volumes:
  pgdata:
```

이 구성의 핵심은 역할 분리입니다. DB는 데이터를 유지하고, migrate는 스키마를 맞추고, seed는 초기 데이터를 넣고, web은 애플리케이션 요청만 처리합니다.

### 2단계 — Alembic 초기화와 첫 마이그레이션

```bash
# Alembic 초기화 (최초 한 번만)
docker compose run --rm migrate alembic init alembic

# alembic.ini에서 sqlalchemy.url 설정 (환경변수로 관리)
# alembic/env.py에서 DATABASE_URL 환경변수를 읽도록 수정
```

```python
# alembic/env.py 수정 부분
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

# 환경변수에서 URL 읽기
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
```

```bash
# 첫 마이그레이션 생성
docker compose run --rm migrate alembic revision --autogenerate -m "initial schema"

# 마이그레이션 적용
docker compose run --rm migrate alembic upgrade head

# 마이그레이션 상태 확인
docker compose run --rm migrate alembic current
docker compose run --rm migrate alembic history
```

마이그레이션 체계를 먼저 세우는 이유는 이후의 모든 스키마 변경을 기록 가능한 형태로 남기기 위해서입니다. 수동 SQL보다 느려 보여도, 결국 운영에서는 훨씬 빠르고 안전합니다.

### 3단계 — idempotent seed 작성

```python
# app/seed.py
"""
환경 초기화용 시드 데이터.
여러 번 실행해도 같은 상태를 유지해야 함 (idempotent).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .models import User, Category

def seed_users(session: Session) -> None:
    """어드민 사용자 시드 — 없을 때만 생성"""
    admin_email = "admin@example.com"
    existing = session.query(User).filter_by(email=admin_email).first()
    if not existing:
        session.add(User(
            email=admin_email,
            name="Admin",
            is_superuser=True,
        ))
        print(f"Created admin user: {admin_email}")
    else:
        print(f"Admin user already exists: {admin_email}")

def seed_categories(session: Session) -> None:
    """기본 카테고리 시드 — 없을 때만 생성"""
    defaults = ["General", "Technology", "Science"]
    existing = {c.name for c in session.query(Category).all()}
    for name in defaults:
        if name not in existing:
            session.add(Category(name=name))
            print(f"Created category: {name}")

def main() -> None:
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    with Session(engine) as session:
        seed_users(session)
        seed_categories(session)
        session.commit()
        print("Seed completed successfully")

if __name__ == "__main__":
    main()
```

seed는 반드시 여러 번 실행해도 같은 결과가 나와야 합니다. 그래야 새 환경, 재배포, 테스트 환경 재생성에서 예측 가능한 상태를 유지할 수 있습니다.

### 4단계 — 실행과 검증

```bash
# 전체 스택 실행
docker compose up -d

# 실행 순서 확인 (로그로 흐름 파악)
docker compose logs -f

# DB 테이블 확인
docker compose exec db psql -U postgres -d app -c "\dt"

# 마이그레이션 상태 확인
docker compose exec db psql -U postgres -d app \
  -c "SELECT * FROM alembic_version;"

# API 동작 확인
curl http://localhost:8000/healthz
curl http://localhost:8000/users

# DB 데이터 직접 확인
docker compose exec db psql -U postgres -d app \
  -c "SELECT email, name FROM users;"
```

여기서는 앱이 뜨는지만 보지 말고, 테이블이 실제로 만들어졌는지와 애플리케이션이 DB를 통해 데이터를 읽을 수 있는지를 함께 확인해야 합니다.

### 5단계 — 백업과 복구

```bash
# 전체 DB 백업
docker compose exec db pg_dump \
  -U postgres \
  -d app \
  --no-password \
  -F c \
  -f /tmp/app_backup.dump

docker compose cp db:/tmp/app_backup.dump ./backups/

# 특정 테이블만 백업
docker compose exec db pg_dump \
  -U postgres -d app \
  -t users -t categories \
  > ./backups/tables_$(date +%Y%m%d).sql

# 복구
docker compose exec -T db psql -U postgres -d app \
  < ./backups/tables_20260101.sql

# 또는 custom format 복구
docker compose exec db pg_restore \
  -U postgres -d app \
  /tmp/app_backup.dump
```

영속성을 확보했다고 해서 끝이 아닙니다. 백업 명령이 문서화되어 있어야 사고 이후 복구 가능성까지 확보됩니다. volume만 믿는 것은 운영 기준으로는 부족합니다.

### 실행 뒤 바로 확인할 것

- `docker compose exec db psql -U postgres -d app -c "\dt"`에서 마이그레이션 결과 테이블이 보여야 합니다.
- `curl http://localhost:8000/users`가 DB 기반 응답을 반환해야 합니다.
- seed를 두 번 실행해도 레코드가 중복되지 않아야 합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| web이 바로 죽음 | DB readiness 전에 연결 시도 | `depends_on: db: condition: service_healthy` 확인 |
| migration 실패 | DB 연결 오류 또는 스키마 충돌 | `docker compose logs migrate`로 오류 확인 |
| 테이블이 없음 | migration이 성공적으로 실행 안 됨 | `service_completed_successfully` 조건 확인 |
| seed 중복 실행 | idempotent 코드 미작성 | `filter_by().first()` 패턴으로 중복 방지 |
| `pg_dump` 출력이 비어 있음 | DB 이름이나 권한 오류 | `-U postgres -d app` 파라미터 확인 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| `depends_on`만으로 연결 준비 보장 | DB 프로세스는 떴지만 요청 수용 불가 | `healthcheck + condition: service_healthy` 필수 |
| migration을 web 컨테이너 시작 명령에 포함 | 여러 워커가 동시에 migration 실행 가능 | 별도 migrate 서비스(init container) 분리 |
| DB 데이터를 bind mount에 저장 | 권한 문제, 성능 저하 | named volume 사용 |
| 기본 `POSTGRES_PASSWORD=dev`를 운영에 사용 | 보안 위험 | secret 저장소에서 주입 |
| 백업 절차 미작성 | 사고 시 복구 경로 없음 | `pg_dump` 자동화, 정기 백업 설정 |

## migration 전략

```
권장 migration 흐름:

1. 로컬 개발
   alembic revision --autogenerate -m "add user table"
   alembic upgrade head

2. PR 리뷰
   migration 파일도 코드 리뷰 대상
   하위 호환성 확인 (down 가능한지)

3. 스테이징 배포
   migrate 컨테이너가 먼저 실행
   성공 후 web 컨테이너 시작

4. 운영 배포
   같은 흐름, 배포 중 다운타임 최소화
   (zero-downtime migration: 컬럼 추가는 안전, 삭제는 2단계로)
```

migration을 web entrypoint에서 함께 돌리지 않는 이유는 웹 서버가 여러 개라면 같은 migration이 중복 실행될 수 있고, 실패 모드도 훨씬 복잡해지기 때문입니다.

## 실무에서는 이렇게 이어집니다

운영에서는 RDS, Cloud SQL 같은 관리형 데이터베이스를 쓰는 경우가 많습니다. 그래도 로컬 개발과 CI에서는 Compose 기반 구성을 유지해 환경 간 차이를 줄이는 팀이 많습니다. 즉, 데이터 저장 위치는 바뀌어도 readiness, migration, seed라는 운영 패턴은 그대로 남습니다.

또한 사고 분석에서도 같은 구조가 유효합니다. 연결 실패인지, 스키마 불일치인지, 데이터 초기화 문제인지 경계를 분리해 볼 수 있기 때문입니다.

## 운영 체크리스트

- [ ] DB에 healthcheck가 있고 `service_healthy` 조건을 사용합니다.
- [ ] migration이 별도 init container로 분리되어 있습니다.
- [ ] 데이터가 named volume에 저장됩니다.
- [ ] seed가 여러 번 실행해도 안전한 idempotent 코드입니다.
- [ ] `pg_dump` 백업 절차가 문서화되어 있습니다.
- [ ] `POSTGRES_PASSWORD`가 기본값(`dev`)이 아닙니다.

## 연습 문제

1. Compose로 postgres, migrate, web을 순서대로 실행하고 `docker compose ps`에서 각 상태를 확인해 보세요.
2. Alembic으로 새 테이블(`articles`)을 추가하는 migration을 작성하고 적용해 보세요.
3. 여러 번 실행해도 안전한 idempotent seed를 작성하고 `docker compose run --rm seed`로 두 번 실행해 보세요.
4. `pg_dump`로 백업하고 새 DB에 복구하는 흐름을 실습해 보세요.

## 처음 질문으로 돌아가기

- **Compose로 PostgreSQL과 앱을 어떻게 함께 띄울까요?**
  - DB 서비스에 healthcheck를 정의하고, migrate와 web 서비스에서 `depends_on: db: condition: service_healthy`를 설정합니다. migrate가 `service_completed_successfully` 이후 web이 시작되도록 체인을 구성합니다.

- **healthcheck와 시작 순서는 어떻게 연결해야 할까요?**
  - `depends_on`과 `condition`을 조합합니다. `condition: service_healthy`는 healthcheck가 성공할 때까지 다음 서비스를 기다리게 합니다. `condition: service_completed_successfully`는 서비스가 성공적으로 종료(exit 0)될 때까지 기다립니다. migrate → seed → web 체인이 이 방식으로 구성됩니다.

- **Alembic migration은 어떤 방식으로 자동화하는 편이 좋을까요?**
  - web 컨테이너 시작 명령에 포함하지 않고, 별도 migrate 서비스(init container)로 분리합니다. 이 서비스는 `restart: "no"`로 설정하고, DB healthy 이후 한 번만 실행됩니다. 여러 web 인스턴스가 있을 때 중복 실행을 방지합니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - `POSTGRES_PASSWORD`를 기본값(`dev`)으로 운영하면 안 됩니다. secret 저장소에서 런타임에 주입해야 합니다. DB 포트(5432)를 호스트에 직접 노출하지 않고, 앱 컨테이너와 같은 내부 네트워크로만 통신해야 합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - `depends_on`만 설정하고 healthcheck를 추가하지 않아 DB 준비 전에 앱이 연결을 시도하는 경우가 가장 많습니다. 또한 migration을 web 시작 명령에 포함해 여러 인스턴스가 동시에 실행하거나, seed가 idempotent하지 않아 중복 데이터가 쌓이는 경우도 흔합니다.

## 정리

앱과 데이터베이스를 함께 운영하는 순간부터 컨테이너는 진짜 서비스 구조가 됩니다. 이때 중요한 것은 단순히 둘을 같이 띄우는 것이 아니라, 데이터 영속성, 준비 상태, migration 자동화라는 세 가지 리듬을 안정적으로 맞추는 것입니다. 이 경계가 깔끔할수록 팀 셋업 비용은 줄고, 배포 실패도 훨씬 예측 가능해집니다.

다음 글에서는 이미지 최적화를 다룹니다. 이제 구성이 안정되었으니, 빌드 시간과 이미지 크기를 줄여 개발 속도와 배포 효율을 함께 끌어올릴 차례입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- **Docker 101 (8/10): 데이터베이스와 함께 실행하기 (현재 글)**
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- [배포용 Docker 구성](./10-production-docker.md)

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
