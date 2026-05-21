---
series: docker-101
episode: 9
title: "Docker 101 (9/10): Image 최적화"
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
  - Multistage
  - BuildKit
  - Alpine
  - Distroless
seo_description: 멀티스테이지와 BuildKit으로 이미지 크기와 빌드 시간을 줄이는 방법을 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (9/10): Image 최적화

같은 애플리케이션인데 어떤 이미지는 1GB가 넘고, 어떤 이미지는 100MB도 되지 않는 경우가 있습니다. 처음에는 단순히 "작을수록 좋다" 정도로 이해하기 쉽지만, 실제로는 배포 시간, CI 속도, 보안 표면, 디버깅 방식까지 함께 달라집니다. 이미지 크기는 미적 취향이 아니라 운영 지표에 가깝습니다.

좋은 최적화는 한 가지 트릭으로 끝나지 않습니다. 베이스 이미지 선택, 멀티스테이지 빌드, 캐시 전략이 함께 맞물려야 효과가 큽니다. 이 글에서는 그 세 가지를 한 번에 묶어 보겠습니다.

이 글은 Docker 101 시리즈의 9번째 글입니다. 여기서는 이미지 크기와 빌드 시간이 왜 팀 속도와 보안에 직접 연결되는지 보고, 멀티스테이지 빌드·BuildKit 캐시·베이스 이미지 선택을 함께 설계하는 방법을 살펴봅니다.

## 먼저 던지는 질문

- 멀티스테이지 빌드는 왜 build와 runtime을 분리할까요?
- BuildKit cache mount는 어떤 식으로 재빌드를 빠르게 만들까요?
- slim, alpine, distroless는 각각 어떤 trade-off가 있을까요?

## 큰 그림

![Docker 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/09/09-01-concept-at-a-glance.ko.png)

*Docker 101 9장 흐름 개요*

## 왜 이 글이 중요한가

이미지가 작아지면 pull 시간이 줄고, pull 시간이 줄면 배포 시간이 줄어듭니다. 동시에 이미지 안에 불필요한 패키지와 도구가 적어질수록 공격 표면도 함께 줄어듭니다. 즉, 이미지 최적화는 성능과 보안을 동시에 다루는 주제입니다.

반대로 빌드 도구와 캐시 파일, 필요 없는 레이어가 그대로 남아 있는 이미지는 느리고 무겁고 위험합니다. 특히 팀 규모가 커질수록 "한 번 빌드할 때 몇 초 더 걸리는가"가 아니라 "하루에 전체 팀이 몇 시간을 잃는가"로 봐야 합니다.

## 한눈에 보는 개념

## 핵심 용어

- **Multistage**: 여러 `FROM`을 사용해 최종 이미지에는 필요한 결과물만 남기는 방식입니다.
- **Cache mount**: BuildKit이 빌드 시점에 재사용하는 캐시 디렉터리입니다.
- **Distroless**: 셸이 없는 최소 구성 이미지입니다.
- **Layer squash**: 여러 레이어를 하나로 합치는 접근입니다.
- **`.dockerignore`**: 빌드 컨텍스트를 줄이는 파일입니다.

이 용어 중에서 특히 distroless는 주의해서 봐야 합니다. 이미지가 작아지는 대신 셸이 없으므로 디버깅 경험이 달라집니다. 즉, 작은 이미지가 항상 무조건 좋은 것은 아니고 팀의 운영 방식과 함께 선택해야 합니다.

## Before / After

**Before**: 1.2GB 이미지, 6분 빌드, 30초 pull.

**After**: 80MB 이미지, 40초 빌드, 캐시 적중 시 5초 빌드, 3초 pull.

이 차이는 단일 숫자 비교를 넘어 팀의 피드백 루프 전체를 바꿉니다. PR 하나당 몇 분씩 아끼면, 하루와 일주일 단위에서는 꽤 큰 차이가 납니다.

## 실습: 이미지 최적화를 5단계로 적용하기

### 1단계 — 멀티스테이지 Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels
COPY . .
RUN useradd -m -u 1000 appuser
USER appuser
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 구성의 핵심은 빌드 도구와 최종 런타임을 분리하는 것입니다. wheel을 만드는 과정은 builder에 남기고, runtime에는 실제 실행에 필요한 결과물만 가져옵니다.

### 2단계 — BuildKit 활성화

```bash
DOCKER_BUILDKIT=1 docker build -t myapp:opt .
docker images myapp
```

BuildKit을 켜야 cache mount 같은 기능을 제대로 활용할 수 있습니다. Python 의존성 설치처럼 반복 비용이 큰 단계에서 체감 차이가 큽니다.

### 3단계 — 베이스 이미지 비교

```text
python:3.12          ~1.0 GB
python:3.12-slim     ~150 MB
python:3.12-alpine   ~50 MB   (watch for musl compat)
gcr.io/distroless/python3-debian12  ~50 MB (no shell)
```

크기만 보면 alpine이나 distroless가 매력적입니다. 하지만 Alpine은 musl 호환성 이슈가 있을 수 있고, distroless는 셸이 없어 디버깅 전략을 바꿔야 합니다. 결국 베이스 이미지는 팀 차원의 선택입니다.

### 4단계 — RUN 결합과 정리

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
```

패키지 설치와 캐시 정리를 한 레이어 안에서 끝내야 불필요한 파일이 이미지에 남지 않습니다. 설치는 했지만 정리는 다른 레이어에서 하겠다는 식은 이미지 크기를 키우기 쉽습니다.

### 5단계 — 히스토리와 레이어 분석

```bash
docker history myapp:opt
# Use 'dive' to analyze per-layer size
# https://github.com/wagoodman/dive
```

최적화는 추측보다 측정이 중요합니다. `docker history`와 `dive`를 함께 보면 어느 레이어가 비대해졌는지, 어떤 명령이 비용을 키우는지 더 분명하게 보입니다.

### 실행 뒤 바로 확인할 것

- `DOCKER_BUILDKIT=1 docker build`를 두 번 실행했을 때 두 번째 빌드에서 캐시 단계가 눈에 띄게 빨라져야 합니다.
- `docker images myapp`와 `docker history myapp:opt`를 함께 보고 builder 도구가 runtime 이미지에 남지 않았는지 확인합니다.

### 잘 안 될 때 먼저 볼 것

- alpine이나 distroless에서 런타임 오류가 나면 이미지 크기보다 먼저 glibc/musl 호환성과 셸 부재를 점검합니다.
- 최적화 후에도 이미지가 크게 줄지 않으면 `.dockerignore`와 멀티스테이지 복사 범위가 과도하지 않은지 봅니다.

## 이 코드에서 먼저 봐야 할 점

- wheels stage를 따로 두어 런타임에는 컴파일 결과물만 남겼습니다.
- cache mount가 pip 캐시를 재사용해 재빌드를 빠르게 합니다.
- distroless는 셸이 없으므로 디버깅 난도가 올라갑니다.

즉, 최적화는 무조건 작게 만드는 경쟁이 아닙니다. 빌드 시간, 런타임 단순성, 디버깅 가능성을 함께 저울질하는 일입니다.

## 자주 하는 실수 다섯 가지

1. **무조건 alpine부터 고릅니다.** musl 비호환으로 런타임 문제가 생길 수 있습니다.
2. **`--no-install-recommends`를 빼먹습니다.** 이미지가 수십 MB씩 커질 수 있습니다.
3. **`apt-get install` 뒤 캐시를 정리하지 않습니다.** 같은 이유로 이미지가 비대해집니다.
4. **빌드 도구를 runtime에 남깁니다.** 공격 표면과 크기가 함께 늘어납니다.
5. **`.dockerignore` 없이 `COPY .`를 합니다.** 거대한 빌드 컨텍스트가 함께 들어옵니다.

이 실수들은 대부분 "일단 빌드만 되면 된다"는 태도에서 나옵니다. 하지만 이미지 최적화는 운영 효율을 높이는 구조적 작업입니다.

## 실무에서는 이렇게 이어집니다

현업 빌드 시스템은 BuildKit과 레지스트리 캐시를 함께 사용해 PR 빌드 시간을 줄입니다. 또한 보안 팀은 distroless나 Chainguard 계열 이미지를 권장하기도 합니다. 즉, 이미지 최적화는 로컬 편의가 아니라 CI/CD와 보안 정책 전반에 영향을 줍니다.

팀 단위로 보면 베이스 이미지 표준화도 중요합니다. 프로젝트마다 제각각 다른 베이스를 쓰면 캐시 공유와 취약점 대응이 모두 어려워집니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 작은 이미지는 미덕이 아니라 운영 KPI입니다.
- 멀티스테이지는 기본값이고, 단일 스테이지는 예외에 가깝습니다.
- 베이스 이미지는 개인 취향이 아니라 팀 정책에 가깝습니다.
- 이해하지 못하는 레이어는 공격 표면일 가능성이 큽니다.
- `dive` 같은 도구로 주기적으로 점검해야 합니다.

이 시점을 지나면 마지막 글의 프로덕션 구성으로 자연스럽게 넘어갈 수 있습니다. 이제 이미지를 잘 만들고 작게 만드는 문제를 넘어서, 어떻게 안전하게 서명하고 배포할지를 다룰 차례입니다.

## 체크리스트

- [ ] 멀티스테이지로 build와 runtime이 분리되어 있습니다.
- [ ] BuildKit cache mount를 사용합니다.
- [ ] 이미지 크기가 200MB 이하입니다.
- [ ] `.dockerignore`로 빌드 컨텍스트를 줄였습니다.

## 연습 문제

1. 기존 Dockerfile을 멀티스테이지로 바꿔 이미지 크기를 절반 이하로 줄여 보세요.
2. cache mount를 사용해 빌드 시간을 크게 줄여 보세요.
3. distroless 베이스로 한 번 실험해 보세요.

## 정리 및 다음 단계

이미지 최적화는 팀 속도와 보안을 동시에 끌어올리는 작업입니다. 베이스 이미지를 잘 고르고, 빌드 단계와 런타임 단계를 분리하고, 캐시를 적극 활용하면 빌드 시간과 배포 시간이 모두 짧아집니다. 중요한 것은 한 가지 기법만 쓰는 것이 아니라, 이 세 축을 함께 설계하는 것입니다.

다음 글에서는 시리즈 마지막으로 프로덕션용 Docker 구성을 정리합니다. 이제 이미지를 효율적으로 만들 수 있으니, 실제 운영에 올릴 때 태그, 서명, 로그, 메트릭, 런타임 보안을 어떻게 맞출지 살펴보겠습니다.


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


## 처음 질문으로 돌아가기

- **멀티스테이지 빌드는 왜 build와 runtime을 분리할까요?**
  - 본문의 기준은 Image 최적화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **BuildKit cache mount는 어떤 식으로 재빌드를 빠르게 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **slim, alpine, distroless는 각각 어떤 trade-off가 있을까요?**
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
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- **Image 최적화 (현재 글)**
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [BuildKit cache mounts](https://docs.docker.com/build/cache/optimize/)
- [Distroless images](https://github.com/GoogleContainerTools/distroless)
- [dive - layer analysis](https://github.com/wagoodman/dive)

### 검증과 트러블슈팅

- [Optimize cache usage in builds](https://docs.docker.com/build/cache/optimize/)

Tags: Docker, Multistage, BuildKit, Alpine, Distroless
