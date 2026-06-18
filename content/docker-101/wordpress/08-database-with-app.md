---
title: "바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기"
series: docker-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 앱과 PostgreSQL Compose 설정에서 migration과 데이터 영속성을 올바르게 구성하는 방법을 설명합니다"
---

# 바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 8번째 글입니다.

AI에게 "FastAPI 앱과 PostgreSQL을 Compose로 실행하게 해줘"라고 요청하면 꽤 그럴듯한 `docker-compose.yml`이 나옵니다. 처음 실행하면 동작합니다. 그런데 새 환경을 만들거나 `docker compose down` 후 다시 올리면 문제가 생깁니다. 데이터베이스 테이블이 없다는 오류가 나거나, 이전에 넣어 둔 데이터가 사라졌거나, 마이그레이션을 수동으로 실행해야 합니다.

AI가 만든 Compose 파일은 앱과 DB를 같이 띄우는 데는 성공하지만, 운영 리듬을 갖추지 못한 경우가 많습니다. 데이터 영속성, 준비 상태 확인, 마이그레이션 자동화라는 세 가지가 함께 있어야 새 환경 생성, 재배포, 팀원 온보딩이 모두 `docker compose up` 한 줄로 끝납니다.

이 세 가지가 빠진 설정을 AI가 만들어 줬다면, 이 글에서 설명하는 패턴을 참고해 직접 추가할 수 있습니다.

> 앱과 DB를 함께 실행하는 구조에서는 세 가지 리듬이 항상 같이 갑니다. 데이터 영속성(volume), 준비 상태 확인(healthcheck + depends_on), 마이그레이션 자동화입니다. 이 셋 중 하나라도 빠지면 배포마다 사람이 들어가야 합니다.

---

## 이 글에서 다룰 문제
- DB 데이터가 `docker compose down` 후 사라지지 않으려면 무엇이 필요할까요?
- `depends_on`만으로 DB 준비를 기다릴 수 없는 이유는 무엇일까요?
- Alembic migration을 자동으로 실행하는 방법은 무엇일까요?
- migration 컨테이너와 앱 컨테이너를 왜 분리해야 할까요?
- seed 데이터는 어떻게 여러 번 실행해도 안전하게 만들까요?

## 올바른 Compose 구성의 세 축

AI가 만든 기본 Compose 파일에서 추가해야 할 것들입니다.

1. **Volume**: DB 데이터를 named volume에 저장해야 컨테이너 삭제 후에도 유지됩니다.
2. **Healthcheck + condition**: DB가 실제 연결을 받을 준비가 된 후에 앱이 시작되어야 합니다.
3. **Migration 컨테이너**: `alembic upgrade head`를 별도 컨테이너로 분리해 한 번만 실행합니다.

## Before / After

**Before**: AI가 만든 Compose 파일에 volume 없음, healthcheck 없음, migration 없음. 새 환경을 만들 때마다 수동으로 테이블 생성 SQL을 실행해야 합니다.

**After**: `docker compose up` 한 줄로 DB 시작 → migration 자동 실행 → 앱 시작 순서가 보장됩니다. 데이터는 named volume에 유지됩니다.

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data    # named volume으로 영구 보존
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app"]
      interval: 5s
      retries: 10

  migrate:
    image: myapi:1.0
    command: ["alembic", "upgrade", "head"]    # 마이그레이션만 실행하고 종료
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:${DB_PASSWORD}@db/app
    depends_on:
      db: { condition: service_healthy }    # DB 준비 후 실행

  web:
    image: myapi:1.0
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:${DB_PASSWORD}@db/app
    depends_on:
      migrate: { condition: service_completed_successfully }    # 마이그레이션 완료 후 시작

volumes:
  pgdata:
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| DB volume 없이 실행 | `docker compose down` 시 데이터 삭제 | named volume 선언 및 마운트 |
| migration을 웹 컨테이너 CMD에 포함 | 여러 워커가 동시에 실행되거나 재시작마다 중복 실행 | 별도 migrate 서비스로 분리 |
| DB healthcheck 없이 `depends_on` | cold start 실패 (DB 미준비 상태에서 앱 연결 시도) | DB에 healthcheck 추가, `condition: service_healthy` 사용 |
| 기본 비밀번호를 운영에 그대로 사용 | 즉시 위험 | `.env`로 분리, 강력한 비밀번호 사용 |
| 수동 SQL로 스키마 관리 | 새 환경마다 사람 개입 필요 | Alembic 등 마이그레이션 도구 도입 |

## AI에게 Docker 관련 요청하는 팁

- "DB volume, healthcheck, migration 컨테이너를 포함한 Compose 파일을 만들어줘"라고 한 번에 명시하세요.
- "migration 컨테이너가 완료된 후에 웹 컨테이너가 시작되도록 `condition: service_completed_successfully`를 사용해줘"라고 요청하세요.
- AI가 migration을 웹 컨테이너의 `CMD`에 넣었다면 별도 서비스로 분리해야 한다고 수정을 요청하세요.
- "idempotent한 seed 스크립트도 만들어줘"라고 하면 여러 번 실행해도 중복 데이터가 안 생기는 코드를 얻을 수 있습니다.

## 운영 체크리스트

- [ ] DB 데이터가 named volume에 저장됩니다
- [ ] DB 서비스에 healthcheck가 있습니다
- [ ] migration이 별도 컨테이너로 분리되어 있습니다
- [ ] 웹 서비스가 `condition: service_completed_successfully`로 migration 완료를 기다립니다
- [ ] 비밀번호가 `.env`로 분리되어 있습니다

## 처음 질문으로 돌아가기

AI가 만든 Compose 파일에서 새 환경을 만들 때마다 수동 작업이 필요하다면, 위에서 설명한 세 가지를 확인하세요. volume으로 데이터 영속성을 확보하고, healthcheck + condition으로 시작 순서를 보장하고, migrate 서비스로 마이그레이션을 자동화하면 `docker compose up` 한 줄로 완전한 환경이 됩니다.

## 정리

앱과 DB를 함께 운영하는 것은 단순히 두 컨테이너를 같이 띄우는 것보다 더 많은 것을 필요로 합니다. 데이터 영속성, 준비 상태 확인, 마이그레이션 자동화 세 가지가 맞아야 합니다. AI가 이 중 일부를 빠뜨린다면, 이 글의 패턴을 참고해 추가하면 됩니다. 다음 글에서는 이미지 크기와 빌드 시간을 줄이는 최적화를 다룹니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL official image](https://hub.docker.com/_/postgres)
- [Compose - service_completed_successfully](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Alembic documentation](https://alembic.sqlalchemy.org/)

### 관련 시리즈
- [Containers 101](../../containers-101/ko/)
- [Kubernetes 101](../../kubernetes-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 Docker 기초 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [바이브코딩을 위한 Docker 기초 (2/10): Image와 Container](./02-image-and-container.md)
- [바이브코딩을 위한 Docker 기초 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [바이브코딩을 위한 Docker 기초 (4/10): Volume과 Network](./04-volume-and-network.md)
- [바이브코딩을 위한 Docker 기초 (5/10): Docker Compose](./05-docker-compose.md)
- [바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- **바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기 (현재 글)**
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
