---
series: docker-101
episode: 6
title: 환경변수와 설정
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
  - Config
  - EnvVar
  - Secret
  - 12Factor
seo_description: 12-factor 의 config 원칙에 따른 환경변수, 설정 파일, secret 분리 방법
last_reviewed: '2026-05-04'
---

# 환경변수와 설정

> Docker 101 시리즈 (6/10)


## 이 글에서 다룰 문제

*같은 image* 가 *dev / staging / prod* 에 그대로 흘러야 *재현성* 이 보장됩니다. 환경별 설정이 코드 안에 있으면 *그 신뢰가 깨집니다*.

> *Image 는 빌드 산출물, 환경은 *런타임 컨텍스트*.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Image["app:1.0 (불변)"] --> Dev["dev env vars"]
    Image --> Stg["staging env vars"]
    Image --> Prd["prod env vars"]
```

## Before/After

**Before**: prod 용 image 와 dev 용 image 가 *각각 별도 빌드*.

**After**: image 는 *하나*. 환경변수만 *바꿔서 다르게 동작*.

## 실습: 환경변수 5단계

### 1단계 — Dockerfile 의 ENV/ARG

```dockerfile
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    LOG_LEVEL=INFO
```

### 2단계 — 런타임 주입

```bash
docker run --rm \
  -e LOG_LEVEL=DEBUG \
  -e DB_URL=postgres://user:pass@db:5432/app \
  myapp:1.0
```

### 3단계 — `--env-file`

```bash
# .env.staging
LOG_LEVEL=INFO
DB_URL=postgres://user:pass@stg-db:5432/app

docker run --rm --env-file .env.staging myapp:1.0
```

### 4단계 — Compose 변수

```yaml
services:
  web:
    image: myapp:1.0
    env_file: .env.${ENV:-dev}
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
```

### 5단계 — Secret 외부화

```bash
# Doppler 예시
doppler run -- docker compose up -d
# Vault 예시 (envconsul)
envconsul -secret secret/app -- docker compose up -d
```

## 이 코드에서 주목할 점

- *기본값* (`${VAR:-default}`) 으로 *누락 방어*.
- *.env.dev*, *.env.staging* 분리로 *환경 명시*.
- *secret* 은 *Compose 안* 에 두지 *않는다*.

## 자주 하는 실수 5가지

1. **secret 을 *Dockerfile ENV* 에 박음.** image 에 *영구 박제*.
2. **`.env` 를 *Git 에 커밋*.** 유출.
3. **환경별 *별도 image 빌드*.** 재현성 깨짐.
4. **누락된 변수에 *조용히 빈 값* 사용.** 런타임 사고.
5. **로그에 *환경변수 dump*.** secret 노출.

## 실무에서는 이렇게 쓰입니다

성숙한 팀은 *Vault / Doppler / 1Password* 가 *런타임 secret 제공자* 가 되고, 코드에는 *변수 이름만* 남습니다.

## 체크리스트

- [ ] image 는 *환경 무관* 하다.
- [ ] secret 은 *외부 store* 에 있다.
- [ ] *.env.example* 이 있다.
- [ ] 시작 시 *변수 검증* 이 있다.

## 정리 및 다음 단계

설정 분리는 *프로덕션 안정성* 의 절반입니다. 다음 글에서는 *Python 앱* 을 *완전한 컨테이너* 로 만듭니다.

<!-- toc:begin -->
- [Docker란 무엇인가?](./01-what-is-docker.md)
- [Image와 Container](./02-image-and-container.md)
- [Dockerfile 작성하기](./03-dockerfile.md)
- [Volume과 Network](./04-volume-and-network.md)
- [Docker Compose](./05-docker-compose.md)
- **환경변수와 설정 (현재 글)**
- Python 앱 컨테이너화 (예정)
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)
<!-- toc:end -->

## 참고 자료

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Set environment variables in containers](https://docs.docker.com/engine/reference/commandline/run/#env)
- [Compose - environment variables](https://docs.docker.com/compose/environment-variables/)
- [Manage secrets with Docker](https://docs.docker.com/engine/swarm/secrets/)

Tags: Docker, Config, EnvVar, Secret, 12Factor
