---
series: docker-101
episode: 9
title: "Docker 101 (9/10): Image 최적화"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/261"
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
  - Multistage
  - BuildKit
  - Alpine
  - Distroless
seo_description: 멀티스테이지와 BuildKit으로 이미지 크기와 빌드 시간을 줄이는 방법을 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (9/10): Image 최적화

같은 애플리케이션인데 어떤 이미지는 1GB가 넘고, 어떤 이미지는 100MB도 되지 않는 경우가 있습니다. 처음에는 단순히 "작을수록 좋다" 정도로 이해하기 쉽지만, 실제로는 배포 시간, CI 속도, 보안 표면, 디버깅 방식까지 함께 달라집니다. 이미지 크기는 미적 취향이 아니라 운영 지표에 가깝습니다.

이 글은 Docker 101 시리즈의 9번째 글입니다.

좋은 최적화는 한 가지 트릭으로 끝나지 않습니다. 베이스 이미지 선택, 멀티스테이지 빌드, 캐시 전략이 함께 맞물려야 효과가 큽니다. 이 글에서는 그 세 가지를 한 번에 묶어 보겠습니다.

![Docker 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/09/09-01-concept-at-a-glance.ko.png)
*Docker 101 9장 흐름 개요*

> 이미지 크기는 미적 취향이 아니라 운영 지표입니다 — 배포 시간·CI 속도·보안 표면·디버깅 방식이 모두 함께 움직이기 때문에, 베이스 이미지 선택·멀티스테이지 빌드·캐시 전략은 따로 떨어진 트릭이 아니라 같은 목표의 세 축으로 함께 봐야 효과가 큽니다.

## 이 글에서 다룰 문제

- 멀티스테이지 빌드는 왜 build와 runtime을 분리할까요?
- BuildKit cache mount는 어떤 식으로 재빌드를 빠르게 만들까요?
- slim, alpine, distroless는 각각 어떤 trade-off가 있을까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

이미지가 작아지면 pull 시간이 줄고, pull 시간이 줄면 배포 시간이 줄어듭니다. 동시에 이미지 안에 불필요한 패키지와 도구가 적어질수록 공격 표면도 함께 줄어듭니다. 즉, 이미지 최적화는 성능과 보안을 동시에 다루는 주제입니다.

| 기법 | 효과 | 주의점 |
|------|------|--------|
| **멀티스테이지 빌드** | 빌드 도구를 런타임에서 제거 | 스테이지 간 복사 경로 주의 |
| **BuildKit cache mount** | pip/apt 캐시 재사용으로 재빌드 단축 | `# syntax=docker/dockerfile:1.7` 필요 |
| **slim 베이스 이미지** | 표준 이미지 대비 70-80% 크기 감소 | 일부 시스템 도구 없음 |
| **alpine 베이스 이미지** | slim보다 더 작음 (~50MB) | musl libc 호환성 문제 가능 |
| **distroless** | 셸 없는 최소 구성 | 디버깅 방식 변경 필요 |
| **`.dockerignore`** | 빌드 컨텍스트 최소화 | 빌드 속도 + 보안 |

### 베이스 이미지 비교

```
python:3.12          ~1.0 GB   (전체 Debian 포함)
python:3.12-slim     ~150 MB   (최소 Debian 패키지)
python:3.12-alpine   ~50 MB    (musl, 기본 도구 없음)
gcr.io/distroless/python3-debian12  ~50 MB (셸 없음)
```

크기만 보면 alpine이나 distroless가 매력적입니다. 하지만 Alpine은 musl 호환성 이슈가 있을 수 있고, distroless는 셸이 없어 디버깅 전략을 바꿔야 합니다. 결국 베이스 이미지는 팀 차원의 선택입니다.

## 전과 후

**Before**: 단일 스테이지 Dockerfile, 1.2GB 이미지, 6분 빌드, 30초 pull. 빌드 도구, 컴파일러, 캐시 파일이 전부 런타임 이미지에 포함됩니다.

**After**: 멀티스테이지 + BuildKit 캐시, 80MB 이미지, 40초 첫 빌드, 캐시 적중 시 5초 빌드, 3초 pull. PR 하나당 수 분이 절약됩니다.

이 차이는 단일 숫자 비교를 넘어 팀의 피드백 루프 전체를 바꿉니다. PR 하나당 몇 분씩 아끼면, 하루와 일주일 단위에서는 꽤 큰 차이가 납니다.

## 실습: 이미지 최적화를 5단계로 적용하기

### 1단계 — 멀티스테이지 Dockerfile (완성형)

```dockerfile
# syntax=docker/dockerfile:1.7
# 최신 BuildKit 문법 활성화

# ── Stage 1: builder ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# BuildKit cache mount: pip 캐시를 빌드 간에 재사용
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /wheels -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# builder에서 빌드된 wheels만 복사 (빌드 도구 없음)
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl && \
    rm -rf /wheels

# 애플리케이션 코드
COPY app/ ./app/

# 보안: non-root 사용자
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()" \
    || exit 1

ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 구성의 핵심은 빌드 도구와 최종 런타임을 분리하는 것입니다. wheel을 만드는 과정은 builder에 남기고, runtime에는 실제 실행에 필요한 결과물만 가져옵니다.

### 2단계 — BuildKit 활성화와 빌드 시간 비교

```bash
# BuildKit 활성화 (Docker 23+ 이상은 기본 활성화)
export DOCKER_BUILDKIT=1

# 첫 빌드 (캐시 없음)
time docker build -t myapp:opt .
# 예: 40초

# 코드만 변경 후 재빌드 (pip 캐시 재사용)
echo "# change" >> app/main.py
time docker build -t myapp:opt .
# 예: 5초 (pip wheel 단계 캐시 적중)

# 이미지 크기 확인
docker images myapp
```

BuildKit을 켜야 cache mount 같은 기능을 제대로 활용할 수 있습니다. Python 의존성 설치처럼 반복 비용이 큰 단계에서 체감 차이가 큽니다.

### 3단계 — 레이어 정리와 apt 패키지 최적화

```dockerfile
# BAD: 레이어가 분리되어 캐시가 남음
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# GOOD: 한 RUN에서 설치와 정리를 함께
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tini \
        curl \
    && rm -rf /var/lib/apt/lists/*
```

패키지 설치와 캐시 정리를 한 레이어 안에서 끝내야 불필요한 파일이 이미지에 남지 않습니다. 설치는 했지만 정리는 다른 레이어에서 하겠다는 식은 이미지 크기를 키웁니다.

### 4단계 — distroless 실험

```dockerfile
# distroless 런타임 (셸 없음, 최소 구성)
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --target=/packages -r requirements.txt
COPY app/ ./app/

# distroless Python 이미지
FROM gcr.io/distroless/python3-debian12 AS runtime
WORKDIR /app
COPY --from=builder /packages /packages
COPY --from=builder /app /app
ENV PYTHONPATH=/packages
EXPOSE 8000
CMD ["app.main"]    # 셸 없음, exec form만 사용 가능
```

```bash
# distroless 이미지 크기 확인
docker images | grep distroless

# 주의: 셸이 없으므로 docker exec으로 bash/sh 진입 불가
# 디버깅이 필요한 경우 ephemeral debug container 사용
docker debug <container-id>
# 또는
docker run -it --rm \
  --volumes-from <container-id> \
  --network container:<container-id> \
  busybox sh
```

### 5단계 — 히스토리와 레이어 분석

```bash
# 레이어 크기 확인
docker history myapp:opt

# 이미지 크기 비교
docker images | grep myapp

# dive로 레이어별 상세 분석 (별도 설치 필요)
# https://github.com/wagoodman/dive
dive myapp:opt

# 이미지 구성 요소 확인
docker image inspect myapp:opt | jq '.[0].RootFS.Layers | length'

# 환경변수에 비밀값 없는지 확인
docker inspect myapp:opt | jq '.[0].Config.Env'
```

최적화는 추측보다 측정이 중요합니다. `docker history`와 `dive`를 함께 보면 어느 레이어가 비대해졌는지, 어떤 명령이 비용을 키우는지 더 분명하게 보입니다.

### 실행 뒤 바로 확인할 것

- `DOCKER_BUILDKIT=1 docker build`를 두 번 실행했을 때 두 번째 빌드에서 pip wheel 단계가 눈에 띄게 빨라져야 합니다.
- `docker images myapp`에서 builder와 runtime 이미지 크기 차이를 확인합니다 (runtime이 훨씬 작아야 합니다).
- `docker history myapp:opt`에서 builder 도구가 runtime 이미지에 없는지 확인합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| alpine에서 import 오류 | musl libc 비호환 (C 확장 패키지) | slim으로 변경 또는 alpine용 패키지 탐색 |
| distroless에서 exec 실패 | 셸이 없음 | debug container 사용 또는 로그로 진단 |
| 캐시 적중 안 됨 | `# syntax=docker/dockerfile:1.7` 누락 | Dockerfile 첫 줄에 syntax 지시어 추가 |
| 최적화 후 이미지가 크게 안 줄음 | `.dockerignore` 없거나 불필요한 파일 포함 | `.dockerignore` 점검, `docker history`로 큰 레이어 찾기 |
| wheels 설치 실패 | Python 버전 불일치 (builder vs runtime) | 두 스테이지의 Python 버전 동일하게 유지 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| 무조건 alpine 선택 | musl 비호환으로 런타임 오류 가능 | slim으로 시작, alpine은 검증 후 전환 |
| `--no-install-recommends` 누락 | apt 권장 패키지까지 설치 (수십 MB 증가) | 항상 `--no-install-recommends` 사용 |
| `apt-get clean` 별도 레이어에서 실행 | 이전 레이어에 파일이 이미 존재 | 한 `RUN`에서 install + clean 함께 |
| 빌드 도구를 runtime에 남김 | 공격 표면 + 크기 증가 | 멀티스테이지로 runtime에는 결과물만 |
| `.dockerignore` 없이 `COPY .` | 거대한 빌드 컨텍스트 포함 | `.dockerignore`로 `node_modules`, `.git` 등 제외 |

## 멀티스테이지 빌드 패턴

```dockerfile
# 패턴 1: 빌드 결과물만 복사
FROM node:20 AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build   # dist/ 생성

FROM nginx:1.27-alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html

# 패턴 2: 특정 파일만 선택
FROM python:3.12-slim AS runtime
COPY --from=builder /wheels /wheels
COPY --from=builder /app/config /app/config
# 소스 코드는 복사하지 않음

# 패턴 3: 외부 이미지에서 바이너리 복사
FROM golang:1.22 AS builder
RUN go build -o /bin/myapp .

FROM gcr.io/distroless/static AS runtime
COPY --from=builder /bin/myapp /myapp
ENTRYPOINT ["/myapp"]
```

## 실무에서는 이렇게 이어집니다

현업 빌드 시스템은 BuildKit과 레지스트리 캐시를 함께 사용해 PR 빌드 시간을 줄입니다. 또한 보안 팀은 distroless나 Chainguard 계열 이미지를 권장하기도 합니다. 즉, 이미지 최적화는 로컬 편의가 아니라 CI/CD와 보안 정책 전반에 영향을 줍니다.

팀 단위로 보면 베이스 이미지 표준화도 중요합니다. 프로젝트마다 제각각 다른 베이스를 쓰면 캐시 공유와 취약점 대응이 모두 어려워집니다.

## 운영 체크리스트

- [ ] 멀티스테이지로 build와 runtime이 분리되어 있습니다.
- [ ] BuildKit cache mount를 사용합니다 (`# syntax=docker/dockerfile:1.7`).
- [ ] 이미지 크기가 200MB 이하입니다.
- [ ] `.dockerignore`로 빌드 컨텍스트를 줄였습니다.
- [ ] `docker history`로 불필요한 레이어가 없는지 확인했습니다.
- [ ] 베이스 이미지 버전이 고정되어 있습니다 (`python:3.12-slim`, not `latest`).

## 연습 문제

1. 기존 단일 스테이지 Dockerfile을 멀티스테이지로 바꿔 이미지 크기를 절반 이하로 줄여 보세요. `docker images`로 전후 크기를 비교하세요.
2. BuildKit cache mount를 추가하고 두 번째 빌드 시간이 얼마나 단축되는지 `time docker build`로 측정해 보세요.
3. `python:3.12-slim`과 `python:3.12-alpine`으로 빌드해 크기와 설치 가능 여부를 비교해 보세요. (C 확장을 사용하는 패키지로 테스트)
4. `dive myapp:opt`로 레이어별 파일 크기를 분석하고, 가장 큰 레이어를 줄일 방법을 찾아보세요.

## 처음 질문으로 돌아가기

- **멀티스테이지 빌드는 왜 build와 runtime을 분리할까요?**
  - 컴파일러, 빌드 도구, 캐시 파일은 빌드 시에만 필요하고 런타임에는 필요하지 않습니다. 이들을 runtime 이미지에서 제거하면 이미지가 작아지고, 공격 표면도 줄어듭니다. Python 예에서는 pip, wheel 빌드 도구, `.pyc` 캐시 등이 포함됩니다.

- **BuildKit cache mount는 어떤 식으로 재빌드를 빠르게 만들까요?**
  - `--mount=type=cache`는 빌드 컨테이너 내에 캐시 디렉터리를 마운트합니다. pip는 `/root/.cache/pip`에 다운로드한 패키지를 저장합니다. 재빌드 시 이 캐시를 재사용하므로 네트워크 다운로드 없이 즉시 설치됩니다. 이미지에는 포함되지 않으므로 크기도 늘어나지 않습니다.

- **slim, alpine, distroless는 각각 어떤 trade-off가 있을까요?**
  - slim: Debian 기반으로 호환성이 좋고 디버깅이 쉽지만 alpine보다 큽니다. alpine: musl libc 기반으로 가장 작지만 C 확장 패키지 호환성 문제가 있습니다. distroless: 셸도 없는 최소 구성으로 가장 안전하지만 `docker exec`으로 진입이 안 되어 디버깅 방식이 완전히 달라집니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - 이미지가 작을수록 CVE(취약점)가 적습니다. 하지만 alpine의 musl은 glibc 기반 패키지와 충돌할 수 있습니다. distroless는 셸이 없어 침해 시 공격자가 할 수 있는 일이 제한됩니다. 어떤 이미지든 고정 태그와 정기 업데이트가 필요합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - Alpine에서 C 확장(psycopg2, numpy 등)이 설치되지 않는 경우가 가장 많습니다. `psycopg2-binary` 대신 `psycopg2`를 쓸 때 특히 그렇습니다. 해결책은 slim으로 변경하거나, alpine에서 빌드 의존성(`musl-dev`, `gcc`)을 설치하는 것입니다.

## 정리

이미지 최적화는 팀 속도와 보안을 동시에 끌어올리는 작업입니다. 베이스 이미지를 잘 고르고, 빌드 단계와 런타임 단계를 분리하고, 캐시를 적극 활용하면 빌드 시간과 배포 시간이 모두 짧아집니다. 중요한 것은 한 가지 기법만 쓰는 것이 아니라, 이 세 축을 함께 설계하는 것입니다.

다음 글에서는 시리즈 마지막으로 프로덕션용 Docker 구성을 정리합니다. 이제 이미지를 효율적으로 만들 수 있으니, 실제 운영에 올릴 때 태그, 서명, 로그, 메트릭, 런타임 보안을 어떻게 맞출지 봅니다.

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
- **Docker 101 (9/10): Image 최적화 (현재 글)**
- [배포용 Docker 구성](./10-production-docker.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [BuildKit cache mounts](https://docs.docker.com/build/cache/optimize/)
- [Distroless images](https://github.com/GoogleContainerTools/distroless)
- [dive - layer analysis](https://github.com/wagoodman/dive)

### 검증과 트러블슈팅

- [Optimize cache usage in builds](https://docs.docker.com/build/cache/optimize/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Multistage, BuildKit, Alpine, Distroless
