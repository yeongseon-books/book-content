---
series: docker-101
episode: 7
title: "Docker 101 (7/10): Python 앱 컨테이너화"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/259"
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
  - Python
  - FastAPI
  - Uvicorn
  - PID1
seo_description: FastAPI 앱을 PID 1, signal, healthcheck까지 고려해 컨테이너화합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (7/10): Python 앱 컨테이너화

Python을 컨테이너에 넣고 `python app.py`만 실행해도 일단은 동작해 보일 수 있습니다. 하지만 배포 중 `SIGTERM`을 제대로 처리하지 못하면 진행 중이던 요청이 중간에 끊기고, 오케스트레이터 입장에서는 정상 종료와 강제 종료를 구분하기 어려워집니다. 이런 문제는 개발 단계에서는 보이지 않다가 운영에서만 드러나는 경우가 많습니다.

이 글은 Docker 101 시리즈의 7번째 글입니다.

Python 애플리케이션을 컨테이너에 넣는 일은 생각보다 빨리 시작할 수 있습니다. 하지만 "컨테이너 안에서 뜬다"와 "운영에 올려도 된다"는 전혀 다른 말입니다. 로컬에서는 잘 돌아가도 배포 시 종료 신호를 제대로 받지 못하거나, readiness를 알리지 못하거나, root로 실행되는 상태로 남아 있으면 운영 사고로 바로 이어집니다.

특히 FastAPI처럼 웹 요청을 처리하는 애플리케이션은 종료 시점이 중요합니다. 새 배포가 시작될 때 기존 요청을 안전하게 마무리하고 내려가야 하기 때문입니다. 그래서 Python 컨테이너화의 핵심은 단순 실행보다 PID 1, signal, healthcheck, non-root 같은 운영 조건에 있습니다.

![Docker 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/07/07-01-concept-at-a-glance.ko.png)
*Docker 101 7장 흐름 개요*

> '컨테이너 안에서 뜬다'와 '운영에 올려도 된다'는 다른 말입니다 — Python 웹앱 컨테이너화의 진짜 관문은 코드가 아니라 PID 1·종료 신호 처리·healthcheck·non-root 같은 운영 조건이고, 이 조건들이 없으면 새 배포가 시작될 때 기존 요청이 사라지거나 root로 돌아가는 사고가 그대로 운영에 노출됩니다.

## 이 글에서 다룰 문제

- FastAPI와 uvicorn을 어떤 방식으로 컨테이너에 담아야 할까요?
- PID 1과 SIGTERM은 왜 컨테이너 운영에서 중요할까요?
- healthcheck는 어떻게 구성해야 할까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

Python을 컨테이너에 넣고 `python app.py`만 실행해도 일단은 동작해 보일 수 있습니다. 하지만 배포 중 `SIGTERM`을 제대로 처리하지 못하면 진행 중이던 요청이 중간에 끊기고, 오케스트레이터 입장에서는 정상 종료와 강제 종료를 구분하기 어려워집니다. 이런 문제는 개발 단계에서는 보이지 않다가 운영에서만 드러나는 경우가 많습니다.

| 개념 | 설명 | 왜 중요한가 |
|------|------|------------|
| **PID 1** | 컨테이너 안에서 가장 먼저 실행되는 프로세스 | 신호 처리, 좀비 프로세스 정리 담당 |
| **SIGTERM** | 정상 종료를 요청하는 신호 | `docker stop`이 이 신호를 보냄 |
| **Graceful shutdown** | 진행 중인 요청을 마무리하고 종료 | 배포 중 요청 손실 방지 |
| **Healthcheck** | 컨테이너가 건강한지 보고하는 메커니즘 | 로드밸런서, 오케스트레이터가 준비 상태 판단 |
| **Tini** | 아주 작은 init 프로세스 | PID 1 문제를 안전하게 해결 |

특히 PID 1은 컨테이너에서 특별합니다. 프로세스 신호 전달과 자식 프로세스 정리 동작이 일반 프로세스와 다르게 엮일 수 있기 때문에, 작은 init을 두거나 신호 처리가 명확한 프로세스를 직접 PID 1로 두는 편이 좋습니다.

## 전과 후

**Before**: `python app.py`를 직접 실행해 종료 신호를 놓치고, 결국 강제 종료됩니다. 배포 시 진행 중인 요청이 끊깁니다.

**After**: `uvicorn`과 `tini`를 사용해 graceful shutdown을 보장하고, healthcheck로 준비 상태를 노출합니다. 배포 중 요청 손실이 없습니다.

이 차이는 운영 중 배포 품질을 크게 바꿉니다. 애플리케이션이 요청을 받는 순간뿐 아니라 내려가는 순간까지 설계해야 신뢰할 수 있는 컨테이너가 됩니다.

## 실습: Python 앱을 5단계로 컨테이너화하기

### 1단계 — 앱 코드 작성

```python
# app/main.py
import os
import signal
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """시작과 종료 라이프사이클 관리"""
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/healthz")
def healthz() -> dict[str, str]:
    """헬스체크 엔드포인트 — 가볍게 유지"""
    return {"status": "ok"}

@app.get("/readyz")
def readyz() -> dict[str, str]:
    """준비 상태 엔드포인트 — DB 연결 등 확인"""
    # 실제로는 DB 연결 등을 확인
    return {"status": "ready"}

@app.get("/")
def root() -> dict[str, str]:
    return {"hello": "world"}
```

health 엔드포인트를 먼저 두는 이유는 단순합니다. 컨테이너가 떴는지보다 요청을 받을 준비가 되었는지를 분리해 관찰해야 하기 때문입니다. `/healthz`는 가볍게, `/readyz`는 실제 의존성을 확인하는 방식으로 분리합니다.

### 2단계 — production-grade Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# 보안과 로깅을 위한 환경변수
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

WORKDIR /app

# tini 설치 (PID 1 init 역할)
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    rm -rf /var/lib/apt/lists/*

# 의존성 레이어 먼저 (캐시 효율)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드
COPY app/ ./app/

# non-root 사용자 생성
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 헬스체크: 가볍고 앱 자체만 확인
HEALTHCHECK --interval=10s --timeout=3s --retries=3 --start-period=10s \
  CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()" \
    || exit 1

# tini를 PID 1로, uvicorn을 자식 프로세스로 실행
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 Dockerfile은 이미지 생성뿐 아니라 운영 계약도 함께 정의합니다. 캐시 가능한 deps 레이어, non-root 실행, healthcheck, PID 1 처리 방식이 모두 들어 있습니다.

### 3단계 — `requirements.txt`와 의존성 관리

```text
# requirements.txt
fastapi==0.115.*
uvicorn[standard]==0.30.*
httpx==0.27.*     # 테스트용 HTTP 클라이언트
```

버전을 어느 정도 고정하는 이유는 컨테이너 재현성을 유지하기 위해서입니다. `0.115.*`처럼 minor version을 고정하면 패치는 허용하되 breaking change를 막을 수 있습니다. 프로덕션에서는 정확한 버전(`==0.115.6`)을 고정하는 팀도 많습니다.

### 4단계 — Compose로 실행

```yaml
# compose.yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 15s
    restart: unless-stopped
```

```bash
# 빌드와 실행
docker compose up -d --build

# 헬스체크 상태 확인
docker compose ps
# Status: Up (healthy) 가 되어야 함

# 엔드포인트 확인
curl http://localhost:8000/healthz
# {"status":"ok"}

curl http://localhost:8000/readyz
# {"status":"ready"}
```

### 5단계 — graceful shutdown 검증

```bash
# 컨테이너 실행 중 로그 모니터링
docker compose logs -f api &

# graceful shutdown 테스트
docker compose stop api
# 로그에서 "Application shutting down..." 메시지 확인

# 강제 종료와 비교
docker compose kill api
# 로그에 종료 메시지 없음 (즉시 종료)

# non-root 실행 확인
docker compose exec api id
# uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)

# PID 1 확인
docker compose exec api ps aux
# PID 1이 tini인지 확인
```

이 단계는 실제 운영 품질과 직결됩니다. `docker stop`이 보내는 `SIGTERM`을 애플리케이션이 제대로 처리해야 배포 시 요청 손실을 줄일 수 있습니다.

### 실행 뒤 바로 확인할 것

- `curl http://localhost:8000/healthz`는 `{"status":"ok"}`를 반환해야 합니다.
- `docker compose ps`에서 Status가 `Up (healthy)`여야 합니다.
- `docker compose stop` 뒤 로그에 "Application shutting down..." 메시지가 보여야 합니다.
- `docker compose exec api id`에서 root가 아닌 `appuser`가 나와야 합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| `tini: exec /bin/sh: no such file or directory` | tini가 설치 안 됨 | `apt-get install -y tini` 추가 |
| healthcheck 계속 실패 | 앱이 `0.0.0.0:8000`에 바인딩 안 됨 | `--host 0.0.0.0` 옵션 확인 |
| 컨테이너 종료 시 요청 끊김 | SIGTERM 처리 안 됨 | tini + uvicorn 조합 사용 |
| `permission denied` | non-root 사용자가 파일 접근 불가 | `chown -R appuser:appuser /app` 추가 |
| 이미지 빌드가 느림 | `COPY . .`를 deps 전에 배치 | 순서 변경: requirements 먼저, 소스 나중 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| `python app.py`를 직접 실행 | PID 1 문제, SIGTERM 미처리 | uvicorn + tini 사용 |
| workers 수를 과도하게 설정 | 메모리 사용량 급증 | CPU 코어 수 × 2 + 1 정도, 측정 후 조정 |
| deps 레이어 분리 안 함 | 코드 변경마다 pip install 재실행 | `requirements.txt` → `pip install` → 소스 순서 |
| root로 실행 | 보안 취약 | `useradd` + `USER appuser` |
| healthcheck에서 DB까지 확인 | 외부 의존성 실패 시 false negative | `/healthz`는 앱만, `/readyz`는 DB 포함 |

## PID 1 문제와 tini

```bash
# PID 1 없이 실행하면 signal 처리에 문제 생길 수 있음
# CMD ["uvicorn", ...]  ← uvicorn이 PID 1

# tini를 PID 1으로 설정하면 안전
# ENTRYPOINT ["tini", "--"]
# CMD ["uvicorn", ...]  ← uvicorn은 PID 2, tini가 신호 전달

# 또는 --init 플래그로 임시 해결 (권장하지 않음)
# docker run --init myapp:1.0
```

tini의 역할은 두 가지입니다. 첫째, SIGTERM을 받아 자식 프로세스(uvicorn)에 전달합니다. 둘째, 좀비 프로세스(`defunct`)를 정리합니다. 이 두 가지가 없으면 장기 운영 시 프로세스 관리가 불안정해질 수 있습니다.

## Gunicorn + Uvicorn 조합 (고부하 운영)

```dockerfile
# requirements.txt에 추가
# gunicorn==22.*
# uvicorn[standard]==0.30.*
```

```bash
# Gunicorn으로 여러 Uvicorn worker 실행
CMD ["gunicorn", "app.main:app",
     "--workers", "4",
     "--worker-class", "uvicorn.workers.UvicornWorker",
     "--bind", "0.0.0.0:8000",
     "--timeout", "30",
     "--graceful-timeout", "30",
     "--access-logfile", "-",
     "--error-logfile", "-"]
```

```bash
# worker 수 결정 기준
# CPU 집약적: CPU 코어 수
# I/O 집약적: CPU 코어 수 × 2
# 메모리 제한 있을 때: 각 worker 메모리 × 수 < 총 메모리

# worker 수 과도하게 설정 시 메모리 OOM 발생
# docker stats로 실제 사용량 모니터링 후 조정
docker stats api
```

## 실무에서는 이렇게 이어집니다

실제 배포에서는 Gunicorn과 Uvicorn worker 조합, Prometheus 메트릭, OpenTelemetry 추적을 함께 붙이는 경우가 많습니다. 하지만 그 이전에 먼저 갖춰야 할 것은 PID 1, signal, healthcheck, non-root라는 기본 계약입니다.

즉, observability 도구를 붙이기 전에 컨테이너가 제대로 뜨고, 준비를 알리고, 안전하게 종료할 수 있어야 합니다. 그 순서가 바뀌면 겉으로는 복잡해 보여도 기초가 약한 시스템이 됩니다.

## Python 컨테이너 관련 자주 쓰는 명령

```bash
# ── 빌드와 실행 ─────────────────────────────────────────────
docker build -t myapi:1.0 .
docker run -d --name api -p 8000:8000 myapi:1.0

# ── 상태 확인 ────────────────────────────────────────────────
docker exec api id                              # 실행 사용자 확인
docker exec api ps aux                         # 프로세스 목록 (PID 1 확인)
docker exec api env | grep -i python           # Python 환경변수
curl http://localhost:8000/healthz             # 헬스체크
curl http://localhost:8000/metrics             # 메트릭 (있을 경우)

# ── 로그와 디버깅 ────────────────────────────────────────────
docker logs -f api                             # 실시간 로그
docker logs --since 10m api                   # 최근 10분 로그
docker stats api                              # 자원 사용량 실시간 확인

# ── graceful shutdown 테스트 ────────────────────────────────
# 터미널 1: 로그 모니터링
docker logs -f api

# 터미널 2: 종료 신호 전송
docker stop api      # SIGTERM → 10초 대기 → SIGKILL
docker kill api      # 즉시 SIGKILL

# 로그에 "Application shutting down..." 확인
```

## 운영 체크리스트

- [ ] `tini` 또는 동등한 init을 PID 1으로 사용합니다.
- [ ] `/healthz` 엔드포인트가 있고 Dockerfile에 HEALTHCHECK가 정의되어 있습니다.
- [ ] 컨테이너가 non-root(uid=1000)로 실행됩니다.
- [ ] graceful shutdown을 `docker stop`으로 검증했습니다.
- [ ] `PYTHONUNBUFFERED=1`로 로그가 즉시 출력됩니다.
- [ ] `requirements.txt`와 소스 코드 레이어가 분리되어 있습니다.

## 연습 문제

1. FastAPI 앱을 컨테이너화하고 `/healthz`와 `/readyz`를 curl로 확인해 보세요.
2. `docker stop` 시 진행 중 요청이 종료 전에 처리되는지 점검해 보세요. (`uvicorn`에 `--timeout-graceful-shutdown 30` 옵션 추가)
3. `USER appuser`를 추가해 non-root로 실행하고 `docker exec api id`로 확인해 보세요.
4. healthcheck에 DB 연결 확인 코드를 추가하면 어떤 문제가 생길 수 있는지 실험해 보세요.

## 처음 질문으로 돌아가기

- **FastAPI와 uvicorn을 어떤 방식으로 컨테이너에 담아야 할까요?**
  - tini를 PID 1으로 두고 (`ENTRYPOINT ["tini", "--"]`), uvicorn을 자식 프로세스로 실행합니다 (`CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`). 이 구조가 SIGTERM 전달과 좀비 프로세스 정리를 모두 해결합니다.

- **PID 1과 SIGTERM은 왜 컨테이너 운영에서 중요할까요?**
  - `docker stop`은 컨테이너에 SIGTERM을 보냅니다. PID 1 프로세스가 이 신호를 받아야 합니다. 하지만 많은 프로세스가 PID 1로 실행될 때 신호를 올바르게 처리하지 못합니다. tini는 신호를 안전하게 자식 프로세스에 전달해 graceful shutdown을 가능하게 합니다.

- **healthcheck는 어떻게 구성해야 할까요?**
  - 가볍게 유지해야 합니다. `/healthz`는 앱이 살아 있는지만 확인하고, DB 연결 같은 외부 의존성은 포함하지 않습니다. 외부 의존성을 포함하면 DB 일시 장애 시 false negative가 폭증해 불필요한 재시작이 일어납니다. `interval=10s`, `timeout=3s`, `retries=3`을 기본값으로 시작합니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - non-root 실행은 필수입니다. 침해 시 컨테이너 내 권한을 최소화해야 합니다. `PYTHONDONTWRITEBYTECODE=1`로 `.pyc` 파일 생성을 막고, 로그에 비밀값이 출력되지 않도록 주의해야 합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - `python app.py` 직접 실행 시 SIGTERM이 처리되지 않아 `docker stop` 후 10초 대기 뒤 강제 종료되는 경우가 많습니다. 또한 healthcheck 엔드포인트가 없거나 DB까지 확인해 외부 장애 시 앱 자체가 unhealthy로 분류되는 경우도 흔합니다.

## 정리

Python 컨테이너화의 진짜 어려움은 단순 실행이 아니라 신호와 준비 상태 처리에 있습니다. FastAPI 앱이 뜬다는 것만으로는 충분하지 않습니다. 언제 요청을 받을 준비가 되었는지, 종료 시 현재 요청을 어떻게 마무리할지, 최소 권한으로 어떻게 실행할지를 함께 설계해야 합니다.

다음 글에서는 데이터베이스와 함께 실행하는 구성을 다룹니다. 앱만 잘 뜨는 단계를 넘어, DB readiness와 migration까지 포함한 실제 애플리케이션 구성을 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- **Docker 101 (7/10): Python 앱 컨테이너화 (현재 글)**
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- [배포용 Docker 구성](./10-production-docker.md)

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
