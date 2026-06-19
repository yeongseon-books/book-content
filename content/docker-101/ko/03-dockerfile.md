---
series: docker-101
episode: 3
title: "Docker 101 (3/10): Dockerfile 작성하기"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/255"
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
  - Dockerfile
  - Build
  - Layer
  - Cache
seo_description: Dockerfile 명령 순서와 캐시 전략으로 빠르고 재현 가능한 빌드를 만듭니다
last_reviewed: '2026-05-15'
---

# Docker 101 (3/10): Dockerfile 작성하기

빌드가 느리면 생산성이 조금 떨어지는 정도로 끝나지 않습니다. 작은 수정에도 전체 의존성을 다시 설치하고, CI에서 매번 시간을 허비하고, 결국 팀 전체가 느린 피드백 루프에 익숙해집니다. 이런 비용은 눈에 잘 띄지 않지만 오래 갈수록 큽니다.

이 글은 Docker 101 시리즈의 3번째 글입니다.

Docker를 조금 쓰기 시작하면 곧 이런 질문이 생깁니다. "이미지는 직접 어떻게 만들지?" 그 답이 Dockerfile입니다. 그런데 단순히 명령 몇 줄을 적는 파일로만 보면 금방 한계를 만납니다. 같은 애플리케이션인데 어떤 Dockerfile은 빌드가 5분 걸리고, 어떤 Dockerfile은 30초 만에 끝나기 때문입니다.

차이는 대개 명령어 종류보다 순서에서 납니다. 무엇을 먼저 복사하고, 어떤 의존성을 어디서 설치하고, 캐시가 어디에서 재사용되는지를 이해해야 빌드 시간이 줄고 재현성도 올라갑니다. Dockerfile은 빌드 스크립트이면서 동시에 운영 문서입니다.

![Docker 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/03/03-01-concept-at-a-glance.ko.png)
*Docker 101 3장 흐름 개요*

> Dockerfile 빌드 속도의 차이는 명령 종류가 아니라 명령 '순서'에서 납니다 — 자주 안 바뀌는 의존성을 먼저, 자주 바뀌는 소스를 나중에 두는 것만으로도 레이어 캐시가 살아나고, Dockerfile은 빌드 스크립트이면서 동시에 운영 문서가 됩니다.

## 이 글에서 다룰 문제

- `FROM`, `RUN`, `COPY`, `CMD`는 각각 어떤 역할을 할까요?
- Dockerfile 명령 순서는 왜 빌드 속도에 큰 영향을 줄까요?
- `.dockerignore`는 성능뿐 아니라 보안에도 왜 중요할까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 명령 참조

좋은 Dockerfile은 코드를 더 잘 짜게 만들기도 합니다. 변경이 잦은 부분과 드문 부분을 분리하고, 실행 사용자를 명시하고, 이미지 안에 무엇이 들어가는지 의식하게 만들기 때문입니다.

| 명령 | 역할 | 예시 |
|------|------|------|
| `FROM` | 베이스 이미지 선택 | `FROM python:3.12-slim` |
| `WORKDIR` | 작업 디렉터리 설정 | `WORKDIR /app` |
| `COPY` | 파일을 이미지 안으로 복사 | `COPY requirements.txt .` |
| `RUN` | 빌드 시점에 명령 실행 | `RUN pip install -r requirements.txt` |
| `ENV` | 환경변수 설정 (런타임 유지) | `ENV LOG_LEVEL=INFO` |
| `ARG` | 빌드 시점 전용 변수 | `ARG APP_VERSION=dev` |
| `EXPOSE` | 컨테이너 포트 문서화 | `EXPOSE 8000` |
| `USER` | 실행 사용자 지정 | `USER appuser` |
| `HEALTHCHECK` | 컨테이너 상태 확인 명령 | `HEALTHCHECK CMD curl -f http://localhost/` |
| `ENTRYPOINT` | 항상 호출되는 고정 진입점 | `ENTRYPOINT ["tini", "--"]` |
| `CMD` | 컨테이너 시작 시 기본 실행 명령 | `CMD ["python", "app.py"]` |

`CMD`와 `ENTRYPOINT`는 둘 다 시작 명령처럼 보이지만 의미가 다릅니다. `ENTRYPOINT`는 고정 실행 파일이고, `CMD`는 `ENTRYPOINT`에 전달되는 기본 인자입니다. `docker run myapp --arg`처럼 실행 시 `CMD`만 오버라이드할 수 있습니다.

## 전과 후

**Before**: `COPY .`를 맨 위에 두어 코드 한 줄 바뀔 때마다 전체 빌드를 다시 합니다. 5분 빌드가 매번 반복됩니다.

**After**: 변경 빈도가 낮은 단계는 위에, 높은 단계는 아래에 두어 캐시 적중률을 크게 높입니다. 코드만 바뀌면 30초면 끝납니다.

이 차이가 중요한 이유는 Docker가 캐시를 레이어 단위로 재사용하기 때문입니다. 자주 바뀌는 코드를 너무 일찍 복사하면, 뒤에 있는 의존성 설치 레이어까지 매번 다시 계산하게 됩니다.

## 실습: Dockerfile을 5단계로 개선해 보기

### 1단계 — 문제 있는 Dockerfile (시작점)

```dockerfile
# BAD: 최적화 전
FROM python:3.12-slim
WORKDIR /app
COPY . .                          # 전체 소스를 먼저 복사
RUN pip install -r requirements.txt  # 코드 변경 때마다 재실행됨
CMD ["python", "app.py"]
```

이 예제는 동작은 하지만 개선 여지가 큽니다. 가장 큰 문제는 의존성과 애플리케이션 코드가 한 덩어리처럼 취급된다는 사실입니다. 코드 한 줄만 바뀌어도 `pip install`이 처음부터 다시 실행됩니다.

### 2단계 — 레이어 순서 최적화

```dockerfile
# GOOD: 변경 빈도 기준으로 순서 조정
FROM python:3.12-slim
WORKDIR /app

# 1) 변경이 드문 의존성 먼저
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) 변경이 잦은 소스 코드를 나중에
COPY . .

CMD ["python", "app.py"]
```

이 순서가 실무적으로 중요합니다. `requirements.txt`가 바뀌지 않았다면 의존성 설치 레이어를 다시 만들 필요가 없기 때문입니다. 작은 순서 차이가 빌드 시간을 5분에서 30초로 줄입니다.

### 3단계 — `.dockerignore`로 보안과 성능 확보

```text
# .dockerignore
__pycache__/
*.pyc
*.pyo
.venv/
venv/
.git/
.gitignore
*.log
.env
.env.*
node_modules/
.pytest_cache/
.mypy_cache/
dist/
build/
*.egg-info/
```

`.dockerignore`는 선택 사항이 아닙니다. 두 가지 이유가 있습니다. 첫째, 빌드 컨텍스트를 줄여 `docker build` 속도를 높입니다. 둘째, `.git`이나 `.env`처럼 이미지에 들어가면 절대 안 되는 파일을 막는 역할도 합니다. `.env`가 이미지에 들어가면 레지스트리를 볼 수 있는 누구나 비밀값을 읽을 수 있습니다.

### 4단계 — non-root 사용자와 보안 강화

```dockerfile
FROM python:3.12-slim

# 보안 환경변수
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# non-root 사용자 생성
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
```

개발 단계에서는 크게 체감되지 않아도, 운영에서는 root 실행이 기본값이어서는 안 됩니다. 애플리케이션이 침해되더라도 컨테이너 내부 권한을 최소화해야 하기 때문입니다. `PYTHONDONTWRITEBYTECODE=1`은 `.pyc` 파일 생성을 막고, `PYTHONUNBUFFERED=1`은 로그가 버퍼 없이 즉시 출력되게 합니다.

### 5단계 — 빌드, 검증, 최적화 확인

```bash
# 빌드
docker build -t myapp:1.0 .

# 캐시 적중 확인: requirements.txt 변경 없이 코드만 수정 후 재빌드
# → RUN pip install 단계가 "CACHED"로 표시되어야 함
touch app.py && docker build -t myapp:1.0 .

# 이미지 크기 확인
docker images myapp

# 레이어 구조 확인
docker history myapp:1.0

# non-root 실행 확인
docker run --rm myapp:1.0 id
# 출력: uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)

# 이미지 안에 민감한 파일이 없는지 확인
docker run --rm myapp:1.0 ls -la /app
```

여기서 `docker history`를 함께 보는 습관이 중요합니다. 이미지가 예상대로 쌓였는지, 불필요한 레이어가 없는지, 민감한 파일이 들어갔을 가능성은 없는지 점검할 수 있기 때문입니다.

### 실행 뒤 바로 확인할 것

- 코드만 바꾼 뒤 다시 빌드했을 때 `pip install` 단계가 `CACHED`로 빠르게 지나가야 합니다.
- `docker history myapp:1.0`에서 의존성 레이어와 애플리케이션 코드 레이어가 분리되어 보여야 합니다.
- `docker run --rm myapp:1.0 id`에서 root가 아닌 사용자(uid=1000)가 나와야 합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| 캐시가 매번 깨짐 | `COPY .`가 `requirements.txt` 복사보다 위에 있음 | 순서 변경: requirements 먼저, 소스 나중 |
| 이미지에 `.env`가 들어감 | `.dockerignore` 없거나 미작성 | `.dockerignore`에 `.env*` 추가 |
| `permission denied` 오류 | 파일 소유자와 USER가 다름 | `chown -R appuser:appuser /app` 추가 |
| `pip install` 느림 | 네트워크 또는 캐시 없음 | `--no-cache-dir`로 이미지 크기 줄이기 |
| 빌드 컨텍스트가 너무 큼 | `.dockerignore` 없이 큰 디렉터리 포함 | `.dockerignore`로 `node_modules`, `.git` 제외 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| `COPY .`를 맨 위에 배치 | 사소한 코드 수정에도 전체 빌드 재실행 | requirements 먼저, 소스 나중 순서로 배치 |
| `apt update`와 `install`을 별도 `RUN`으로 분리 | 오래된 캐시 재사용으로 예측 불가 | 한 `RUN`에 update, install, clean 모두 실행 |
| `pip install` 후 캐시 미정리 | 이미지 크기 불필요하게 증가 | `--no-cache-dir` 사용 |
| `.dockerignore` 생략 | `.git`, `.env` 등이 이미지에 포함 | 프로젝트 시작 시 `.dockerignore` 필수 작성 |
| root로 실행 방치 | 보안 기본값 약화 | `useradd` 후 `USER` 지정 |

## CMD vs ENTRYPOINT 차이

```dockerfile
# CMD만 사용: 전체 명령을 오버라이드할 수 있음
CMD ["python", "app.py"]

# ENTRYPOINT + CMD: ENTRYPOINT는 고정, CMD는 기본 인자
ENTRYPOINT ["python"]
CMD ["app.py"]

# docker run myimage              → python app.py
# docker run myimage other.py     → python other.py
# docker run --entrypoint bash myimage → bash (ENTRYPOINT 오버라이드)
```

신호 처리 관점에서 exec 형식(`["cmd", "arg"]`)과 shell 형식(`cmd arg`)의 차이도 중요합니다. shell 형식은 `/bin/sh -c`를 통해 실행되므로, SIGTERM 신호가 실제 프로세스에 전달되지 않을 수 있습니다.

## 완성된 Dockerfile 예시 (Python FastAPI)

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

# ── 환경변수 ────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

WORKDIR /app

# ── 시스템 의존성 (변경 빈도 낮음) ──────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    rm -rf /var/lib/apt/lists/*

# ── Python 의존성 (변경 빈도 중간) ──────────────────────────
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# ── 애플리케이션 코드 (변경 빈도 높음) ──────────────────────
COPY app/ ./app/

# ── 보안: non-root ───────────────────────────────────────────
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=3 --start-period=10s \
  CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()" \
    || exit 1

ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 Dockerfile은 이 글에서 다룬 모든 원칙을 담고 있습니다. 레이어 순서(변경 빈도 기준), `.dockerignore` 필요성, non-root 실행, healthcheck, BuildKit 캐시가 모두 반영되어 있습니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 멀티스테이지 빌드, BuildKit 캐시 마운트, 베이스 이미지 표준화까지 함께 사용해 빌드 시간을 줄입니다. 특히 Python 프로젝트에서는 의존성 레이어 캐시를 어떻게 설계하느냐가 로컬 개발 속도와 CI 시간을 크게 좌우합니다.

운영 관점에서는 Dockerfile이 보안 정책의 일부가 되기도 합니다. 어떤 베이스 이미지를 허용하는지, root 실행을 금지하는지, 헬스체크를 어디서 정의하는지 같은 기준이 모두 Dockerfile 수준에서 드러나기 때문입니다.

## 빌드 관련 자주 쓰는 명령

```bash
# ── 기본 빌드 ────────────────────────────────────────────────
docker build -t myapp:1.0 .
docker build -t myapp:1.0 -f Dockerfile.prod .  # 다른 Dockerfile 지정
docker build --no-cache -t myapp:1.0 .           # 캐시 무시

# ── BuildKit 사용 ────────────────────────────────────────────
DOCKER_BUILDKIT=1 docker build -t myapp:1.0 .
docker buildx build -t myapp:1.0 .              # BuildKit 기반 빌드

# ── 빌드 인자 전달 ───────────────────────────────────────────
docker build \
  --build-arg APP_VERSION=1.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t myapp:1.0 .

# ── 검사 ─────────────────────────────────────────────────────
docker history myapp:1.0                # 레이어 히스토리
docker inspect myapp:1.0               # 전체 이미지 정보
docker run --rm myapp:1.0 id           # 실행 사용자 확인
docker run --rm myapp:1.0 env          # 환경변수 확인
```

## Dockerfile 빌드 캐시 작동 원리

캐시가 어떻게 작동하는지 이해하면 더 효과적으로 최적화할 수 있습니다.

```dockerfile
FROM python:3.12-slim          # ← 이 줄이 바뀌면 아래 모두 무효
WORKDIR /app                   # ← FROM 변경 시 무효
COPY requirements.txt .        # ← requirements.txt 내용이 바뀌면 아래 무효
RUN pip install -r requirements.txt  # ← requirements 변경 시 재실행
COPY . .                       # ← 소스 코드 변경 시 이 줄부터 무효
CMD ["python", "app.py"]       # ← 위 COPY 변경 시 무효
```

```bash
# 캐시 히트 확인
docker build -t myapp:1.0 .
# CACHED로 표시되는 줄은 캐시를 재사용했다는 의미
# Step 4/6 : RUN pip install...
#  ---> Using cache   ← 캐시 적중!
#  ---> a1b2c3d4e5f6

# 강제 재빌드 (캐시 무시)
docker build --no-cache -t myapp:1.0 .

# 특정 단계부터 재빌드
# (해당 파일을 touch해서 변경으로 인식시킴)
touch requirements.txt
docker build -t myapp:1.0 .
```

핵심 규칙: **위의 레이어가 바뀌면 아래의 모든 레이어 캐시가 무효**입니다. 그래서 변경 빈도가 낮은 것(시스템 패키지, 의존성)을 위에, 높은 것(소스 코드)을 아래에 두어야 합니다.

## 운영 체크리스트

- [ ] 레이어 순서가 변경 빈도를 반영합니다 (드문 것 위, 잦은 것 아래).
- [ ] `.dockerignore`가 존재하고 `.env`, `.git`을 포함합니다.
- [ ] 컨테이너가 non-root로 실행됩니다.
- [ ] 의존성과 애플리케이션 코드가 별도 레이어로 분리되어 있습니다.
- [ ] `apt-get clean`이나 `--no-cache-dir`로 캐시를 정리합니다.
- [ ] `HEALTHCHECK`가 정의되어 있습니다.

## 연습 문제

1. requirements는 그대로 두고 코드만 수정해 빌드했을 때 `pip install` 단계가 `CACHED`로 표시되는지 확인해 보세요.
2. `.dockerignore` 없이 빌드한 이미지와 있는 이미지의 `docker history` 크기를 비교해 보세요.
3. non-root 사용자로 실행하는 Dockerfile을 직접 작성하고 `docker run --rm myimage id`로 확인해 보세요.
4. `CMD`와 `ENTRYPOINT`를 조합해 `docker run myimage --help`가 동작하는 Dockerfile을 작성해 보세요.

## 처음 질문으로 돌아가기

- **`FROM`, `RUN`, `COPY`, `CMD`는 각각 어떤 역할을 할까요?**
  - `FROM`은 베이스 이미지 선택, `RUN`은 빌드 시점 명령 실행, `COPY`는 파일 복사, `CMD`는 컨테이너 시작 시 기본 실행 명령입니다. 각 명령은 독립적인 레이어를 만들고, 레이어 순서가 캐시 효율에 직접 영향을 줍니다.

- **Dockerfile 명령 순서는 왜 빌드 속도에 큰 영향을 줄까요?**
  - Docker는 캐시를 레이어 단위로 재사용합니다. 어떤 레이어가 변경되면 그 이후의 모든 레이어는 다시 빌드됩니다. 따라서 자주 바뀌는 코드를 위에 두면 변경 없는 의존성 설치도 매번 반복됩니다. 변경 빈도가 낮은 것을 위에 두어야 캐시가 잘 작동합니다.

- **`.dockerignore`는 성능뿐 아니라 보안에도 왜 중요할까요?**
  - `.dockerignore`가 없으면 `.git` 전체(커밋 히스토리 포함)와 `.env`(비밀값 포함)가 빌드 컨텍스트에 들어갑니다. 빌드 컨텍스트는 Docker 데몬으로 전송되고, 이미지에 포함된 파일은 레지스트리를 통해 노출될 수 있습니다. 성능 최적화와 보안 제어가 동시에 필요한 이유입니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - root 실행 방지(`USER` 지정), 민감 파일 제외(`.dockerignore`), 베이스 이미지 고정(태그 + digest), `HEALTHCHECK` 정의, 그리고 `docker commit` 대신 항상 Dockerfile로 빌드하는 것이 핵심입니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - `COPY . .`를 의존성 설치 전에 두어 캐시가 전혀 작동하지 않는 경우가 가장 흔합니다. 또한 `.dockerignore` 없이 `.env` 파일이 이미지에 들어가는 보안 사고도 자주 발생합니다.

## 정리

좋은 Dockerfile은 팀의 시간을 매일 절약합니다. 핵심은 명령 수가 적은 것이 아니라, 캐시가 잘 작동하고 재현 가능하며 운영 기준을 담고 있느냐입니다. `FROM`, `RUN`, `COPY`, `CMD`는 단순한 문법이 아니라 빌드 전략과 운영 철학을 담는 수단입니다.

다음 글에서는 volume과 network를 다룹니다. 이미지를 잘 만드는 문제에서 한 걸음 나아가, 실행 중 생기는 데이터와 컨테이너 간 통신을 어떻게 분리하고 연결할지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- **Docker 101 (3/10): Dockerfile 작성하기 (현재 글)**
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- [배포용 Docker 구성](./10-production-docker.md)

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
