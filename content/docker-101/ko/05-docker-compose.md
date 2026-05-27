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

컨테이너가 하나일 때는 `docker run` 몇 줄로도 충분합니다. 하지만 웹 애플리케이션, 데이터베이스, 캐시, 워커처럼 구성 요소가 늘어나는 순간부터 명령어 기반 운영은 빠르게 한계에 부딪힙니다. 누가 먼저 떠야 하는지, 어떤 환경변수를 넣어야 하는지, 어떤 볼륨과 네트워크를 써야 하는지를 매번 기억에 의존하게 되기 때문입니다.

이 글은 Docker 101 시리즈의 5번째 글입니다.

Docker Compose는 이 문제를 YAML 하나로 정리합니다. 서비스, 네트워크, 볼륨, 의존 관계를 선언해 두면 팀 전체가 같은 멀티 컨테이너 환경을 같은 방식으로 띄울 수 있습니다. Compose는 많은 팀에서 사실상 첫 번째 인프라 코드입니다.

![Docker 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/05/05-01-concept-at-a-glance.ko.png)
*Docker 101 5장 흐름 개요*

> Compose는 docker run의 편의 래퍼가 아니라 많은 팀의 '첫 번째 인프라 코드'입니다 — 서비스·네트워크·볼륨·의존 관계를 YAML로 선언해 두면 멀티 컨테이너 환경이 사람의 기억이 아니라 파일로 재현 가능해지고, 새 팀원도 같은 환경을 같은 명령으로 띄울 수 있습니다.

## 먼저 던지는 질문

- 여러 컨테이너를 한 번에 재현 가능하게 실행하려면 무엇이 필요할까요?
- service, network, volume은 Compose에서 어떻게 정의할까요?
- `depends_on`과 healthcheck는 어떤 관계로 이해해야 할까요?

## 왜 이 글이 중요한가

신규 개발자 온보딩 문서가 길어진다는 것은 대개 환경 구성이 코드가 아니라 설명으로 남아 있다는 뜻입니다. 웹은 이렇게 띄우고, DB는 저렇게 띄우고, 순서는 이것을 따르라고 적어 놓기 시작하면, 문서는 곧 낡고 실행 환경은 사람마다 달라집니다.

Compose는 이 문제를 짧고 명시적인 선언으로 바꿉니다. `docker compose up` 한 줄이 온보딩 문서보다 더 강한 이유는, 설명이 아니라 실제 동작을 표준화하기 때문입니다.

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

## 처음 질문으로 돌아가기

- **여러 컨테이너를 한 번에 재현 가능하게 실행하려면 무엇이 필요할까요?**
  - 본문에서 강조했듯이 컨테이너마다 `docker run` 명령을 길게 적는 방식은 휴먼 에러와 환경 차이를 만들기 쉽습니다. Compose는 `docker-compose.yml`이라는 선언형 파일에 서비스·네트워크·볼륨을 한꺼번에 적어 두고 `docker compose up` 한 줄로 전체 스택을 띄우게 만들어 재현성을 확보합니다.
- **service, network, volume은 Compose에서 어떻게 정의할까요?**
  - 본문 예시처럼 `services:` 아래에 각 컨테이너를 service 단위로 적고, `networks:`와 `volumes:` 최상위 키에 공유할 네트워크와 영구 저장소를 선언한 뒤 service 안에서 참조합니다. 이렇게 분리하면 같은 네트워크에 붙은 service끼리 이름으로 통신하고 volume이 서비스 재기동을 살아남게 됩니다.
- **`depends_on`과 healthcheck는 어떤 관계로 이해해야 할까요?**
  - `depends_on`만으로는 "DB 컨테이너가 시작됐다"는 것까지만 보장되고, 본문에서 본 것처럼 "DB가 실제로 접속을 받을 수 있다"까지는 보장되지 않습니다. 그래서 DB service에 healthcheck를 두고 `depends_on`에 `condition: service_healthy`를 함께 적어야 앱 service가 진짜로 준비된 DB만 보고 시작합니다.

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