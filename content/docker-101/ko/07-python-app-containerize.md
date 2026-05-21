---
series: docker-101
episode: 7
title: "Docker 101 (7/10): Python 앱 컨테이너화"
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
  - Python
  - FastAPI
  - Uvicorn
  - PID1
seo_description: FastAPI 앱을 PID 1, signal, healthcheck까지 고려해 컨테이너화합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (7/10): Python 앱 컨테이너화

이 글은 Docker 101 시리즈의 7번째 글입니다.


Python 애플리케이션을 컨테이너에 넣는 일은 생각보다 빨리 시작할 수 있습니다. 하지만 "컨테이너 안에서 뜬다"와 "운영에 올려도 된다"는 전혀 다른 말입니다. 로컬에서는 잘 돌아가도 배포 시 종료 신호를 제대로 받지 못하거나, readiness를 알리지 못하거나, root로 실행되는 상태로 남아 있으면 운영 사고로 바로 이어집니다.

특히 FastAPI처럼 웹 요청을 처리하는 애플리케이션은 종료 시점이 중요합니다. 새 배포가 시작될 때 기존 요청을 안전하게 마무리하고 내려가야 하기 때문입니다. 그래서 Python 컨테이너화의 핵심은 단순 실행보다 PID 1, signal, healthcheck, non-root 같은 운영 조건에 있습니다.


![Docker 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/07/07-01-concept-at-a-glance.ko.png)
*Docker 101 7장 흐름 개요*

## 먼저 던지는 질문

- FastAPI와 uvicorn을 어떤 방식으로 컨테이너에 담아야 할까요?
- PID 1과 SIGTERM은 왜 컨테이너 운영에서 중요할까요?
- healthcheck는 어떻게 구성해야 할까요?

## 왜 이 글이 중요한가

Python을 컨테이너에 넣고 `python app.py`만 실행해도 일단은 동작해 보일 수 있습니다. 하지만 배포 중 `SIGTERM`을 제대로 처리하지 못하면 진행 중이던 요청이 중간에 끊기고, 오케스트레이터 입장에서는 정상 종료와 강제 종료를 구분하기 어려워집니다. 이런 문제는 개발 단계에서는 보이지 않다가 운영에서만 드러나는 경우가 많습니다.

또한 healthcheck와 non-root 실행은 각각 신뢰성과 보안의 기본값입니다. 컨테이너가 실제로 요청을 받을 준비가 되었는지, 혹은 침해되더라도 권한이 과도하지 않은지를 초기에 설계해야 합니다.

## 한눈에 보는 개념

## 핵심 용어

- **PID 1**: 컨테이너 안에서 가장 먼저 실행되는 프로세스입니다.
- **SIGTERM**: 정상 종료를 요청하는 신호입니다.
- **Graceful shutdown**: 진행 중인 요청을 마무리하고 종료하는 방식입니다.
- **Healthcheck**: 컨테이너가 건강한지 보고하는 메커니즘입니다.
- **Tini**: 아주 작은 init 프로세스입니다.

특히 PID 1은 컨테이너에서 특별합니다. 프로세스 신호 전달과 자식 프로세스 정리 동작이 일반 프로세스와 다르게 엮일 수 있기 때문에, 작은 init을 두거나 신호 처리가 명확한 프로세스를 직접 PID 1로 두는 편이 좋습니다.

## 전과 후

**Before**: `python app.py`를 직접 실행해 종료 신호를 놓치고, 결국 강제 종료됩니다.

**After**: `uvicorn`과 `tini`를 사용해 graceful shutdown을 보장하고, healthcheck로 준비 상태를 노출합니다.

이 차이는 운영 중 배포 품질을 크게 바꿉니다. 애플리케이션이 요청을 받는 순간뿐 아니라 내려가는 순간까지 설계해야 신뢰할 수 있는 컨테이너가 됩니다.

## 실습: Python 앱을 5단계로 컨테이너화하기

### 1단계 — 앱 코드 작성

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/")
def root() -> dict[str, str]:
    return {"hello": "world"}
```

health 엔드포인트를 먼저 두는 이유는 단순합니다. 컨테이너가 떴는지보다 요청을 받을 준비가 되었는지를 분리해 관찰해야 하기 때문입니다.

### 2단계 — Dockerfile 작성

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# deps layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app layer
COPY . .

RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()" || exit 1

# tini at PID 1 forwards SIGTERM
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 Dockerfile은 이미지 생성뿐 아니라 운영 계약도 함께 정의합니다. 캐시 가능한 deps 레이어, non-root 실행, healthcheck, PID 1 처리 방식이 모두 들어 있습니다.

### 3단계 — `requirements.txt`

```text
fastapi==0.115.*
uvicorn[standard]==0.30.*
```

버전을 어느 정도 고정하는 이유는 컨테이너 재현성을 유지하기 위해서입니다. 개발자 로컬 환경에서 우연히 최신 버전이 설치되는 상황을 줄여 줍니다.

### 4단계 — 빌드와 실행

```bash
docker build -t myapi:1.0 .
docker run -d --name api -p 8000:8000 myapi:1.0
curl http://localhost:8000/healthz
```

실행이 된다는 사실만 확인하지 말고, health 엔드포인트가 기대한 값으로 응답하는지도 함께 확인해야 합니다. 그래야 이후 오케스트레이터나 Compose healthcheck와 연결하기 쉽습니다.

### 5단계 — graceful shutdown 검증

```bash
docker stop api    # sends SIGTERM, uvicorn drains in-flight requests
docker logs api | tail
```

이 단계는 실제 운영 품질과 직결됩니다. `docker stop`이 보내는 `SIGTERM`을 애플리케이션이 제대로 처리해야 배포 시 요청 손실을 줄일 수 있습니다.

### 실행 뒤 바로 확인할 것

- `curl http://localhost:8000/healthz`는 `{"status":"ok"}`를 반환해야 하고, `docker stop api` 뒤 로그에는 강제 종료가 아니라 정상 종료 흐름이 보여야 합니다.
- 컨테이너 내부 프로세스가 non-root인지 `docker exec api id`로 한 번 더 확인하면 좋습니다.

### 잘 안 될 때 먼저 볼 것

- `tini`가 이미지에 설치되지 않았는데 ENTRYPOINT만 추가한 경우 컨테이너가 바로 실패합니다. 베이스 이미지와 패키지 설치 단계를 다시 확인합니다.
- healthcheck가 계속 실패하면 앱이 `0.0.0.0:8000`에 바인딩되었는지와 `/healthz` 경로가 실제로 존재하는지부터 봅니다.

## 이 코드에서 먼저 봐야 할 점

- 의존성 레이어와 코드 레이어를 분리해 캐시 효율을 높였습니다.
- `tini`가 signal을 올바르게 전달합니다.
- healthcheck는 오케스트레이터가 준비 상태를 판단하는 기준이 됩니다.

특히 healthcheck는 너무 무거워도 안 됩니다. 가벼운 애플리케이션 준비 상태를 확인하는 용도로 유지해야, 외부 의존성 일시 장애 때문에 false negative가 폭증하는 일을 줄일 수 있습니다.

## 자주 하는 실수 다섯 가지

1. **`python app.py`를 직접 실행합니다.** 종료 신호 처리가 부정확해질 수 있습니다.
2. **workers 수를 감으로 과도하게 늘립니다.** 메모리 사용량이 급격히 커질 수 있습니다.
3. **코드가 바뀔 때마다 의존성 설치까지 다시 합니다.** 빌드 시간이 불필요하게 길어집니다.
4. **root로 실행합니다.** 보안 기본값을 낮춥니다.
5. **healthcheck에서 DB까지 깊게 검사합니다.** false negative가 쉽게 늘어납니다.

운영에서는 작은 불편을 줄이는 것보다 실패 모드를 예측 가능하게 만드는 편이 중요합니다. Python 컨테이너에서 signal과 healthcheck를 제대로 다루는 이유가 여기에 있습니다.

## 실무에서는 이렇게 이어집니다

실제 배포에서는 Gunicorn과 Uvicorn worker 조합, Prometheus 메트릭, OpenTelemetry 추적을 함께 붙이는 경우가 많습니다. 하지만 그 이전에 먼저 갖춰야 할 것은 PID 1, signal, healthcheck, non-root라는 기본 계약입니다.

즉, observability 도구를 붙이기 전에 컨테이너가 제대로 뜨고, 준비를 알리고, 안전하게 종료할 수 있어야 합니다. 그 순서가 바뀌면 겉으로는 복잡해 보여도 기초가 약한 시스템이 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 컨테이너에서는 PID 1을 의식해야 합니다.
- graceful shutdown은 사용자 신뢰와 직결됩니다.
- healthcheck는 가볍고 정직해야 합니다.
- non-root는 기본값이어야 합니다.
- worker 수는 추측이 아니라 부하 측정으로 정해야 합니다.

이 관점을 가지고 다음 글의 데이터베이스 연동으로 넘어가면, 왜 앱과 DB의 시작 순서와 readiness가 함께 중요해지는지도 쉽게 이어집니다.

## 체크리스트

- [ ] `tini` 또는 동등한 init을 사용합니다.
- [ ] healthcheck가 가볍고 정확합니다.
- [ ] 컨테이너가 non-root로 실행됩니다.
- [ ] graceful shutdown을 검증했습니다.

## 연습 문제

1. FastAPI 앱을 컨테이너화하고 `/healthz`를 확인해 보세요.
2. `docker stop` 시 진행 중 요청이 종료 전에 처리되는지 점검해 보세요.
3. `USER`를 추가해 non-root로 실행해 보세요.

## 정리 및 다음 단계

Python 컨테이너화의 진짜 어려움은 단순 실행이 아니라 신호와 준비 상태 처리에 있습니다. FastAPI 앱이 뜬다는 것만으로는 충분하지 않습니다. 언제 요청을 받을 준비가 되었는지, 종료 시 현재 요청을 어떻게 마무리할지, 최소 권한으로 어떻게 실행할지를 함께 설계해야 합니다.

다음 글에서는 데이터베이스와 함께 실행하는 구성을 다룹니다. 앱만 잘 뜨는 단계를 넘어, DB readiness와 migration까지 포함한 실제 애플리케이션 구성을 살펴보겠습니다.


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

- **FastAPI와 uvicorn을 어떤 방식으로 컨테이너에 담아야 할까요?**
  - 본문의 기준은 Python 앱 컨테이너화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **PID 1과 SIGTERM은 왜 컨테이너 운영에서 중요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **healthcheck는 어떻게 구성해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- **Python 앱 컨테이너화 (현재 글)**
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [FastAPI in containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Uvicorn deployment](https://www.uvicorn.org/deployment/)
- [tini - a tiny init for containers](https://github.com/krallin/tini)
- [Dockerfile HEALTHCHECK](https://docs.docker.com/engine/reference/builder/#healthcheck)

### 검증과 트러블슈팅

- [Docker stop signal behavior](https://docs.docker.com/reference/cli/docker/container/stop/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Python, FastAPI, Uvicorn, PID1