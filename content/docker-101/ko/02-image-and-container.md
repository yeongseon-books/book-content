---
series: docker-101
episode: 2
title: "Docker 101 (2/10): Image와 Container"
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
  - Image
  - Container
  - Layer
  - Lifecycle
seo_description: image와 container의 수명 주기와 layer 모델을 실습으로 정리합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (2/10): Image와 Container

이 글은 Docker 101 시리즈의 2번째 글입니다.


Docker를 조금만 써 보면 가장 먼저 헷갈리는 지점이 image와 container입니다. 이미지를 받았는데 왜 실행해야 하는지, 컨테이너 안에서 파일을 만들었는데 왜 다시 없어지는지, 삭제한 것은 이미지인지 컨테이너인지가 섞이기 시작합니다. 이 구분이 흐려지면 디버깅도 같이 흐려집니다.

실무에서 발생하는 많은 컨테이너 문제는 복잡한 기술보다 기본 오해에서 출발합니다. 컨테이너 내부에서 뭔가를 바꿔 놓고 "왜 재시작했더니 사라졌지?"라고 묻는 장면이 대표적입니다. 이미지는 불변이고, 컨테이너의 변경은 일시적이라는 감각을 잡아야 Docker를 제대로 다룰 수 있습니다.


![Docker 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/02/02-01-concept-at-a-glance.ko.png)
*Docker 101 2장 흐름 개요*

## 먼저 던지는 질문

- image와 container는 정확히 무엇이 다를까요?
- layer와 copy-on-write는 왜 중요한 개념일까요?
- 컨테이너의 수명 주기는 어떤 흐름으로 흘러갈까요?

## 왜 이 글이 중요한가

컨테이너의 동작 방식을 모르면 디버깅이 운에 가까워집니다. 파일이 사라진 이유, 변경이 남지 않는 이유, 어떤 명령은 이미지에 작용하고 어떤 명령은 컨테이너에 작용하는 이유를 설명하지 못하면 운영 이슈를 재현하기가 어려워집니다.

반대로 lifecycle과 layer 개념을 이해하면 문제의 대부분이 예측 가능해집니다. "이건 컨테이너 상태가 날아간 문제다", "이건 이미지가 다시 빌드되어야 하는 문제다"처럼 원인을 훨씬 빨리 분리할 수 있습니다.

## 한눈에 보는 개념

## 핵심 용어

- **Layer**: 이미지 내부를 구성하는 읽기 전용 파일시스템 조각입니다.
- **Writable layer**: 컨테이너가 실행되면서 맨 위에 추가되는 쓰기 가능한 레이어입니다.
- **Lifecycle**: created → running → stopped → removed로 이어지는 수명 주기입니다.
- **Tag**: `nginx:1.27`처럼 이미지를 식별하는 버전 라벨입니다.
- **Digest**: 이미지 내용을 고정하는 불변 SHA256 식별자입니다.

여기서 특히 중요한 것은 writable layer입니다. 컨테이너 내부에서 여러분이 만드는 모든 변경은 보통 이 쓰기 레이어에 쌓입니다. 그래서 컨테이너를 지우면 그 변경도 함께 사라집니다.

## 전과 후

**Before**: 컨테이너 안에서 `apt install`을 하고 재시작 뒤 변경이 사라져 당황합니다.

**After**: 변경은 Dockerfile에 코드로 남기고, 컨테이너는 언제든 버릴 수 있는 실행 단위로 다룹니다.

이 차이는 단순히 습관의 문제가 아닙니다. 재현 가능한 운영을 만들 수 있느냐의 문제입니다. 손으로 바꾼 컨테이너는 설명하기 어렵고, 다시 만들기도 어렵습니다.

## 실습: image와 container를 5단계로 구분해 보기

### 1단계 — 이미지 살펴보기

```bash
docker pull nginx:1.27
docker image inspect nginx:1.27 | jq '.[0].RootFS.Layers'
docker history nginx:1.27
```

`docker history`는 이미지가 어떤 레이어로 쌓였는지 보여 줍니다. 처음에는 단순한 정보처럼 보이지만, 이미지 크기와 빌드 시간을 이해하는 데 아주 중요한 단서가 됩니다.

### 2단계 — 컨테이너 생성과 실행

```bash
docker create --name web nginx:1.27   # create only
docker start web                       # then start
docker ps
```

이 단계는 create와 start가 분리될 수 있다는 점을 보여 줍니다. 즉, 이미지는 실행 준비물이고, 컨테이너는 실제 실행 상태라는 구분이 명령 수준에서도 드러납니다.

### 3단계 — 내부로 들어가 보기

```bash
docker exec -it web bash
# inside the container
ls /etc/nginx
exit
```

컨테이너 안으로 직접 들어가 보면 파일시스템이 진짜 서버처럼 보입니다. 많은 입문자가 여기서 착각합니다. 눈에 보인다고 해서 영구적이라는 뜻은 아닙니다. 이 감각을 다음 단계에서 바로 확인하게 됩니다.

### 4단계 — 변경은 일시적입니다

```bash
docker exec web touch /tmp/hello
docker stop web && docker rm web
docker run --name web2 nginx:1.27
docker exec web2 ls /tmp/hello   # No such file
```

이 단계가 핵심입니다. 컨테이너 내부에 만든 파일이 다음 컨테이너에서는 보이지 않는 이유는 변경이 이미지에 반영된 것이 아니라, 이전 컨테이너의 writable layer에만 있었기 때문입니다.

### 5단계 — 이미지 정리

```bash
docker image prune -f          # remove dangling
docker image rm nginx:1.27
```

정리 명령도 구분해서 이해해야 합니다. 컨테이너 정리와 이미지 정리는 다른 작업입니다. 이 차이를 혼동하면 디스크 정리가 잘 안 되거나, 필요한 이미지를 실수로 지웠다고 오해하기 쉽습니다.

### 실행 뒤 바로 확인할 것

- `docker history nginx:1.27`는 레이어 목록을 보여 주어야 하고, `docker exec web2 ls /tmp/hello`는 파일이 없다는 오류를 반환해야 합니다.
- 이 두 결과가 함께 나와야 image와 container 상태가 분리된다는 사실을 눈으로 확인한 셈입니다.

### 잘 안 될 때 먼저 볼 것

- `docker exec -it web bash`가 실패하면 해당 이미지에 `bash`가 없는 경우가 많으니 `sh`로 다시 시도합니다.
- 정리 단계에서 이미지 삭제가 안 되면 먼저 실행 중인 컨테이너가 모두 내려갔는지 `docker ps -a`로 확인합니다.

## 이 코드에서 먼저 봐야 할 점

- `docker history`는 각 레이어 뒤에 있는 빌드 단계를 보여 줍니다.
- 컨테이너 내부 변경은 commit하지 않는 한 다음 실행으로 이어지지 않습니다.
- 태그보다 digest가 훨씬 더 강한 재현성 기준입니다.

특히 운영 환경에서는 "어떤 이미지를 띄웠는가"를 태그보다 digest 기준으로 추적하는 경우가 많습니다. 태그는 가리키는 대상이 바뀔 수 있지만, digest는 내용 자체를 고정하기 때문입니다.

## 자주 하는 실수 다섯 가지

1. **컨테이너 안에 파일을 영구 저장하려고 합니다.** 재시작이나 재생성 시 사라집니다.
2. **`docker commit`으로 이미지를 만듭니다.** 재현하기 어려운 산출물이 됩니다.
3. **멈춘 컨테이너를 계속 쌓아 둡니다.** `docker ps -a`가 금방 관리하기 어려워집니다.
4. **`latest`만 믿습니다.** 어느 날 다른 이미지가 같은 태그를 가리킬 수 있습니다.
5. **레이어가 지나치게 많은 이미지를 만듭니다.** 빌드와 pull이 느려집니다.

이 실수들은 모두 "실행 상태"와 "배포 산출물"을 섞어 보는 데서 나옵니다. 이미지는 만들고, 컨테이너는 실행하고, 상태는 외부에 둔다는 원칙이 중요합니다.

## 실무에서는 이렇게 이어집니다

CI 파이프라인은 이미지 빌드 결과를 digest 기준으로 고정하고, 운영에서는 어떤 digest가 배포되었는지 로그와 메트릭 시스템과 연결해 추적합니다. 사고 분석에서도 "어떤 코드가 배포됐나"만큼이나 "어떤 이미지가 실제로 실행됐나"가 중요합니다.

결국 image와 container를 분리해서 보는 습관은 단순한 개념 학습이 아니라 변경 이력을 추적할 수 있는 운영 습관으로 이어집니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 이미지는 빌드하는 것이고, 컨테이너는 실행하는 것입니다.
- 변경은 코드와 Dockerfile로 남겨야지, 실행 중인 컨테이너에 손으로 남기면 안 됩니다.
- 프로덕션의 기본 식별자는 태그보다 digest에 가깝습니다.
- 레이어 캐시는 빌드 속도와 직결됩니다.
- 컨테이너는 언제든 버릴 수 있게 설계해야 합니다.

이 관점을 잡고 나면 다음 글의 Dockerfile도 훨씬 잘 읽힙니다. 왜 명령 순서가 중요한지, 왜 layer cache를 의식해야 하는지가 자연스럽게 이어지기 때문입니다.

## 체크리스트

- [ ] image와 container의 차이를 설명할 수 있습니다.
- [ ] 컨테이너 내부 변경이 휘발된다는 점을 이해했습니다.
- [ ] layer와 digest가 왜 중요한지 설명할 수 있습니다.
- [ ] 멈춘 컨테이너를 정리할 수 있습니다.

## 연습 문제

1. `nginx:1.27`의 레이어 개수를 확인해 보세요.
2. 컨테이너 안에 파일을 만든 뒤 다시 실행해서 파일이 사라지는지 확인해 보세요.
3. `docker image prune`으로 사용하지 않는 이미지를 정리해 보세요.

## 정리 및 다음 단계

Docker의 기본기는 image와 container를 분리해서 이해하는 데서 시작합니다. image는 불변 산출물이고, container는 그 위에 잠깐 올라가는 실행 상태입니다. 이 관점을 놓치지 않으면 상태 손실, 재현성, 디버깅 문제 대부분을 훨씬 빨리 설명할 수 있습니다.

다음 글에서는 Dockerfile을 직접 작성하면서 이 불변 산출물을 어떻게 만드는지 살펴보겠습니다. 결국 컨테이너 운영의 품질은 이미지를 얼마나 재현 가능하게 빌드하느냐에서 시작합니다.


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

- **image와 container는 정확히 무엇이 다를까요?**
  - 본문의 기준은 Image와 Container를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **layer와 copy-on-write는 왜 중요한 개념일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **컨테이너의 수명 주기는 어떤 흐름으로 흘러갈까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- **Image와 Container (현재 글)**
- Dockerfile 작성하기 (예정)
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

- [Docker images](https://docs.docker.com/engine/reference/commandline/image/)
- [Docker container lifecycle](https://docs.docker.com/engine/reference/commandline/container/)
- [Storage drivers and layers](https://docs.docker.com/storage/storagedriver/)
- [Image digests](https://docs.docker.com/engine/reference/commandline/pull/#pull-an-image-by-digest-immutable-identifier)

### 검증과 트러블슈팅

- [docker exec reference](https://docs.docker.com/engine/reference/commandline/exec/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Image, Container, Layer, Lifecycle