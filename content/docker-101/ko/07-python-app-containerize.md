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

> '컨테이너 안에서 뜬다'와 '운영에 올려도 된다'는 다른 말입니다 — Python 웹앱 컨테이너화의 진짜 관문은 코드가 아니라 PID 1·종료 신호 처리·healthcheck·non-root 같은 운영 조건이고, 이 조건들이 없으면 새 배포가 시작될 때 기존 요청이 사라지거나 root로 돌아가는 사고가 그대로 운영에 노출됩니다.

## 먼저 던지는 질문

- FastAPI와 uvicorn을 어떤 방식으로 컨테이너에 담아야 할까요?
- PID 1과 SIGTERM은 왜 컨테이너 운영에서 중요할까요?
- healthcheck는 어떻게 구성해야 할까요?

## 왜 이 글이 중요한가

Python을 컨테이너에 넣고 `python app.py`만 실행해도 일단은 동작해 보일 수 있습니다. 하지만 배포 중 `SIGTERM`을 제대로 처리하지 못하면 진행 중이던 요청이 중간에 끊기고, 오케스트레이터 입장에서는 정상 종료와 강제 종료를 구분하기 어려워집니다. 이런 문제는 개발 단계에서는 보이지 않다가 운영에서만 드러나는 경우가 많습니다.

또한 healthcheck와 non-root 실행은 각각 신뢰성과 보안의 기본값입니다. 컨테이너가 실제로 요청을 받을 준비가 되었는지, 혹은 침해되더라도 권한이 과도하지 않은지를 초기에 설계해야 합니다.

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

다음 글에서는 데이터베이스와 함께 실행하는 구성을 다룹니다. 앱만 잘 뜨는 단계를 넘어, DB readiness와 migration까지 포함한 실제 애플리케이션 구성을 봅니다.

## 처음 질문으로 돌아가기

- **FastAPI와 uvicorn을 어떤 방식으로 컨테이너에 담아야 할까요?**
  - 본문 예시처럼 베이스로 `python:3.x-slim`을 쓰고 `requirements.txt`를 먼저 `COPY` 후 `pip install`로 의존성 layer를 분리한 뒤 앱 소스를 복사하고, `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]`처럼 uvicorn을 PID 1로 실행하는 형태가 표준입니다. 의존성 캐시와 신호 처리를 동시에 챙기는 구조입니다.
- **PID 1과 SIGTERM은 왜 컨테이너 운영에서 중요할까요?**
  - 본문에서 강조했듯이 컨테이너의 첫 프로세스가 PID 1이 되고, `docker stop`은 그 프로세스에 SIGTERM을 보냅니다. uvicorn을 직접 실행하지 않고 `sh -c "..."` 같은 셸 래퍼로 띄우면 SIGTERM이 셸에서 멈춰 앱이 graceful shutdown 신호를 못 받기 때문에, 본문에서 본 exec form `CMD`를 써야 신호가 그대로 앱으로 전달됩니다.
- **healthcheck는 어떻게 구성해야 할까요?**
  - 본문에서 본 것처럼 앱에 `/healthz`나 `/livez` 같은 가벼운 엔드포인트를 두고, Dockerfile에 `HEALTHCHECK CMD curl -fs http://localhost:8000/healthz`나 Compose의 `healthcheck` 블록으로 주기·timeout·retry를 함께 명시해야 합니다. healthcheck가 있어야 오케스트레이터가 "기동했지만 실제로 동작 안 함"을 자동으로 감지해 트래픽을 끊거나 재시작할 수 있습니다.

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