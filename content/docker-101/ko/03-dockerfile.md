---
series: docker-101
episode: 3
title: "Docker 101 (3/10): Dockerfile 작성하기"
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
  - Dockerfile
  - Build
  - Layer
  - Cache
seo_description: Dockerfile 명령 순서와 캐시 전략으로 빠르고 재현 가능한 빌드를 만듭니다
last_reviewed: '2026-05-15'
---

# Docker 101 (3/10): Dockerfile 작성하기

이 글은 Docker 101 시리즈의 3번째 글입니다.


Docker를 조금 쓰기 시작하면 곧 이런 질문이 생깁니다. "이미지는 직접 어떻게 만들지?" 그 답이 Dockerfile입니다. 그런데 단순히 명령 몇 줄을 적는 파일로만 보면 금방 한계를 만납니다. 같은 애플리케이션인데 어떤 Dockerfile은 빌드가 5분 걸리고, 어떤 Dockerfile은 30초 만에 끝나기 때문입니다.

차이는 대개 명령어 종류보다 순서에서 납니다. 무엇을 먼저 복사하고, 어떤 의존성을 어디서 설치하고, 캐시가 어디에서 재사용되는지를 이해해야 빌드 시간이 줄고 재현성도 올라갑니다. Dockerfile은 빌드 스크립트이면서 동시에 운영 문서입니다.


## 먼저 던지는 질문

- `FROM`, `RUN`, `COPY`, `CMD`는 각각 어떤 역할을 할까요?
- Dockerfile 명령 순서는 왜 빌드 속도에 큰 영향을 줄까요?
- `.dockerignore`는 성능뿐 아니라 보안에도 왜 중요할까요?

## 큰 그림

![Docker 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/03/03-01-concept-at-a-glance.ko.png)

*Docker 101 3장 흐름 개요*

## 왜 이 글이 중요한가

빌드가 느리면 생산성이 조금 떨어지는 정도로 끝나지 않습니다. 작은 수정에도 전체 의존성을 다시 설치하고, CI에서 매번 시간을 허비하고, 결국 팀 전체가 느린 피드백 루프에 익숙해집니다. 이런 비용은 눈에 잘 띄지 않지만 오래 갈수록 큽니다.

좋은 Dockerfile은 코드를 더 잘 짜게 만들기도 합니다. 변경이 잦은 부분과 드문 부분을 분리하고, 실행 사용자를 명시하고, 이미지 안에 무엇이 들어가는지 의식하게 만들기 때문입니다.

## 한눈에 보는 개념

## 핵심 용어

- **FROM**: 베이스 이미지를 선택합니다.
- **RUN**: 빌드 시점에 명령을 실행합니다.
- **COPY**: 파일을 이미지 안으로 복사합니다.
- **CMD**: 컨테이너 시작 시 기본 실행 명령입니다.
- **ENTRYPOINT**: 항상 호출되는 고정 진입점입니다.

이 다섯 가지는 Dockerfile의 뼈대입니다. 특히 `CMD`와 `ENTRYPOINT`는 둘 다 시작 명령처럼 보이지만 의미가 다르므로, 나중에 운영 인자 전달과 종료 신호 처리까지 생각하면 구분해서 이해하는 편이 좋습니다.

## 전과 후

**Before**: `COPY .`를 맨 위에 두어 코드 한 줄 바뀔 때마다 전체 빌드를 다시 합니다.

**After**: 변경 빈도가 낮은 단계는 위에, 높은 단계는 아래에 두어 캐시 적중률을 크게 높입니다.

이 차이가 중요한 이유는 Docker가 캐시를 레이어 단위로 재사용하기 때문입니다. 자주 바뀌는 코드를 너무 일찍 복사하면, 뒤에 있는 의존성 설치 레이어까지 매번 다시 계산하게 됩니다.

## 실습: Dockerfile을 5단계로 개선해 보기

### 1단계 — 최소 Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

이 예제는 동작은 하지만 개선 여지가 큽니다. 가장 큰 문제는 의존성과 애플리케이션 코드가 한 덩어리처럼 취급된다는 점입니다.

### 2단계 — 레이어 순서 최적화

```dockerfile
FROM python:3.12-slim
WORKDIR /app

# 1) low change frequency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) high change frequency
COPY . .

CMD ["python", "app.py"]
```

이 순서가 실무적으로 중요합니다. requirements가 바뀌지 않았다면 의존성 설치 레이어를 다시 만들 필요가 없기 때문입니다. 작은 순서 차이가 빌드 시간을 크게 바꿉니다.

### 3단계 — `.dockerignore`

```text
__pycache__/
.venv/
.git/
*.log
.env
node_modules/
```

`.dockerignore`는 선택 사항이 아닙니다. 빌드 컨텍스트를 줄여 성능을 올릴 뿐 아니라, `.git`이나 `.env`처럼 이미지에 들어가면 안 되는 파일을 막는 역할도 합니다.

### 4단계 — non-root 사용자

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

개발 단계에서는 크게 체감되지 않아도, 운영에서는 root 실행이 기본값이어서는 안 됩니다. 애플리케이션이 침해되더라도 컨테이너 내부 권한을 최소화해야 하기 때문입니다.

### 5단계 — 빌드와 실행

```bash
docker build -t myapp:1.0 .
docker run --rm myapp:1.0
docker history myapp:1.0
```

여기서 `docker history`를 함께 보는 습관이 중요합니다. 이미지가 예상대로 쌓였는지, 불필요한 레이어가 없는지, 민감한 파일이 들어갔을 가능성은 없는지 점검할 수 있기 때문입니다.

### 실행 뒤 바로 확인할 것

- 코드만 바꾼 뒤 다시 빌드했을 때 `pip install` 단계가 캐시 히트로 빠르게 지나가야 합니다.
- `docker history myapp:1.0`에서 의존성 레이어와 애플리케이션 코드 레이어가 분리되어 보여야 다음 빌드에서도 이점을 얻습니다.

### 잘 안 될 때 먼저 볼 것

- 캐시가 매번 깨지면 `COPY . .`가 requirements 복사보다 위에 있지 않은지부터 봅니다.
- 이미지 안에 `.env`나 `.git`이 들어갔다면 `.dockerignore`가 비어 있거나 빌드 컨텍스트 경로를 잘못 잡은 경우가 많습니다.

## 이 코드에서 먼저 봐야 할 점

- requirements를 먼저 복사하면 의존성 레이어를 캐시하기 좋습니다.
- `.dockerignore`가 없으면 `.git` 전체가 이미지 빌드 컨텍스트로 들어갑니다.
- `USER`를 생략하면 기본적으로 root로 실행됩니다.

결국 Dockerfile 품질은 "잘 동작하느냐"보다 "다음 빌드도 빠르고 예측 가능하냐"로 판단하는 편이 좋습니다. 로컬에서 한 번 돌아가는 Dockerfile은 출발점일 뿐입니다.

## 자주 하는 실수 다섯 가지

1. **`COPY .`를 맨 위에 둡니다.** 사소한 코드 수정에도 전체 빌드가 다시 일어납니다.
2. **`apt update`와 `install`을 다른 `RUN`으로 나눕니다.** 오래된 캐시를 재사용해 예측이 어려워집니다.
3. **`pip install` 뒤 캐시 정리를 하지 않습니다.** 이미지 크기가 불필요하게 커집니다.
4. **`.dockerignore`를 빼먹습니다.** `.git`, `.env` 같은 파일이 이미지에 들어갈 수 있습니다.
5. **root 실행을 그대로 둡니다.** 운영 보안 기본값을 스스로 약화합니다.

이 실수들은 모두 "이미지가 그냥 한 번 만들어지면 된다"는 생각에서 나옵니다. 하지만 Dockerfile은 반복해서 빌드되고, 여러 개발자와 CI가 공유하며, 결국 운영까지 이어집니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 멀티스테이지 빌드, BuildKit 캐시 마운트, 베이스 이미지 표준화까지 함께 사용해 빌드 시간을 줄입니다. 특히 Python 프로젝트에서는 의존성 레이어 캐시를 어떻게 설계하느냐가 로컬 개발 속도와 CI 시간을 크게 좌우합니다.

운영 관점에서는 Dockerfile이 보안 정책의 일부가 되기도 합니다. 어떤 베이스 이미지를 허용하는지, root 실행을 금지하는지, 헬스체크를 어디서 정의하는지 같은 기준이 모두 Dockerfile 수준에서 드러나기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- Dockerfile은 빌드 스크립트이면서 문서입니다.
- 위에서 아래로 갈수록 변경 빈도가 높아지게 구성합니다.
- `.dockerignore`는 성능 최적화이면서 보안 제어이기도 합니다.
- `CMD`와 `ENTRYPOINT`는 의도를 갖고 선택해야 합니다.
- non-root는 예외가 아니라 기본값입니다.

이 사고방식은 이후 이미지 최적화와 프로덕션 주제로 곧바로 이어집니다. 좋은 Dockerfile 없이 좋은 운영은 나오기 어렵습니다.

## 체크리스트

- [ ] 레이어 순서가 변경 빈도를 반영합니다.
- [ ] `.dockerignore`가 존재합니다.
- [ ] 컨테이너가 non-root로 실행됩니다.
- [ ] 의존성과 애플리케이션 코드가 분리되어 있습니다.

## 연습 문제

1. requirements는 그대로 두고 코드만 수정해 캐시 적중 여부를 확인해 보세요.
2. `.dockerignore`를 추가해 이미지 컨텍스트를 줄여 보세요.
3. non-root 사용자로 실행하는 Dockerfile을 직접 작성해 보세요.

## 정리 및 다음 단계

좋은 Dockerfile은 팀의 시간을 매일 절약합니다. 핵심은 명령 수가 적은 것이 아니라, 캐시가 잘 작동하고 재현 가능하며 운영 기준을 담고 있느냐입니다. `FROM`, `RUN`, `COPY`, `CMD`는 단순한 문법이 아니라 빌드 전략과 운영 철학을 담는 수단입니다.

다음 글에서는 volume과 network를 다룹니다. 이미지를 잘 만드는 문제에서 한 걸음 나아가, 실행 중 생기는 데이터와 컨테이너 간 통신을 어떻게 분리하고 연결할지 살펴보겠습니다.


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

- **`FROM`, `RUN`, `COPY`, `CMD`는 각각 어떤 역할을 할까요?**
  - 본문의 기준은 Dockerfile 작성하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Dockerfile 명령 순서는 왜 빌드 속도에 큰 영향을 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`.dockerignore`는 성능뿐 아니라 보안에도 왜 중요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- **Dockerfile 작성하기 (현재 글)**
- Volume과 Network (예정)
- Docker Compose (예정)
- 환경변수와 설정 (예정)
- Python 앱 컨테이너화 (예정)
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Use a .dockerignore file](https://docs.docker.com/engine/reference/builder/#dockerignore-file)
- [BuildKit](https://docs.docker.com/build/buildkit/)

### 검증과 트러블슈팅

- [docker build reference](https://docs.docker.com/engine/reference/commandline/build/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Dockerfile, Build, Layer, Cache