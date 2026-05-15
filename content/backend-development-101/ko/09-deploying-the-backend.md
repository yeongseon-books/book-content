---
series: backend-development-101
episode: 9
title: 백엔드 배포
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - Deployment
  - Docker
  - DevOps
  - Python
seo_description: Docker와 healthcheck로 백엔드를 안전하게 배포하는 기본기입니다
last_reviewed: '2026-05-12'
---

# 백엔드 배포

이 글은 Backend Development 101 시리즈의 아홉 번째 글입니다. 로컬에서는 잘 되던 애플리케이션이 운영에서 깨지는 이유는 코드만의 문제가 아니라 환경 차이 때문인 경우가 많습니다. 여기서는 Docker, 환경 변수, healthcheck, rolling update를 중심으로 배포를 재현성의 문제로 이해해 보겠습니다.

## 이 글에서 다룰 문제

- 배포 환경은 어떤 요소들로 이루어질까요?
- Dockerfile은 왜 재현 가능한 실행 환경을 만드는 핵심일까요?
- 환경 변수와 secret은 어떻게 분리해야 할까요?
- healthcheck와 readiness probe는 어떤 운영 판단에 쓰일까요?
- 무중단에 가까운 배포는 어떤 아이디어로 동작할까요?

## 왜 중요한가

배포가 두려운 일이 되는 순간 출시 빈도는 떨어집니다. 출시가 드물어질수록 한 번의 배포에 더 많은 변경이 묶이고, 위험은 오히려 커집니다. 그래서 시니어 엔지니어가 만드는 좋은 배포는 화려한 배포가 아니라 드라마가 없는 배포입니다.

배포를 안정화한다는 것은 운영 환경의 차이를 코드와 설정 안에 고정해 두는 일입니다. “내 노트북에서는 됐는데요”라는 말이 더 이상 변명이 되지 않게 만드는 과정이라고 볼 수도 있습니다.

> 배포는 코드가 아니라 환경 차이까지 함께 재현 가능하게 만드는 작업입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Code["Source"] --> Build["Build"]
    Build --> Image["Container image"]
    Image --> Reg["Registry"]
    Reg --> Run["Runner"]
    Run --> LB["Load balancer"]
    LB --> Users["Users"]
```

코드는 이미지가 되고, 이미지는 어디에서나 같은 방식으로 실행되어야 합니다. 이 재현성이 있어야 운영 문제를 환경 탓으로만 돌리지 않을 수 있습니다.

## 핵심 용어

- **Container**: 의존성을 안에 포함한 실행 단위입니다.
- **Image**: 컨테이너를 만드는 청사진입니다.
- **Registry**: 이미지를 저장하는 저장소입니다.
- **Healthcheck**: 컨테이너가 살아 있는지 runner에게 알려 주는 점검 경로입니다.
- **Rolling update**: 새 버전으로 트래픽을 점진적으로 옮기는 배포 방식입니다.

## Before/After

**Before (manual deploy)**

```bash
ssh server
git pull
pip install -r requirements.txt
systemctl restart app
```

**After (Dockerized — same image runs everywhere)**

```bash
docker build -t myapp:1.2.3 .
docker push registry/myapp:1.2.3
# Production pulls the same image and runs it
```

수동 배포는 사람이 기억에 의존합니다. 반면 이미지 기반 배포는 “무엇이 실행되고 있는가”를 버전으로 고정해 줍니다.

## 실습: 다섯 단계로 보는 배포

### Step 1 — Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Dockerfile은 런타임 환경을 코드로 고정합니다. 운영에서 쓰는 Python 버전과 의존성이 로컬과 달라질 때 생기는 문제를 크게 줄여 줍니다.

### Step 2 — Build and run

```bash
docker build -t myapp:0.1 .
docker run -p 8000:8000 myapp:0.1
```

이미지를 한 번 만들면 어디에서나 같은 방식으로 실행할 수 있어야 합니다. 이것이 컨테이너 기반 배포의 가장 큰 장점입니다.

### Step 3 — Environment variables

```python
# main.py
import os
DB_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]
```

```bash
docker run -e DATABASE_URL=postgres://... -e JWT_SECRET=... myapp:0.1
```

설정과 secret을 이미지 안에 구워 넣지 않고 바깥에서 주입해야 환경별 차이를 통제할 수 있습니다. 특히 secret은 코드와 이미지에서 분리되어야 합니다.

### Step 4 — Healthcheck endpoint

```python
# health.py
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

In `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
  interval: 10s
  retries: 3
```

새 버전이 진짜 준비되었는지 확인하지 않고 트래픽을 보내면 죽은 인스턴스로 요청이 흘러갑니다. healthcheck는 단순 모니터링이 아니라 트래픽 제어 신호입니다.

### Step 5 — Rolling update

```bash
# Kubernetes, ECS, Docker Swarm — same idea
# 1) deploy the new image
# 2) wait for healthcheck to pass
# 3) shift traffic gradually
# 4) remove the old version
```

핵심은 새 버전이 건강하다는 사실을 증명한 뒤 트래픽을 옮기는 것입니다. 무중단 배포는 마법이 아니라, 검증과 점진적 전환의 조합입니다.

## 이 코드에서 먼저 볼 점

- secret은 이미지 안에 넣지 않습니다.
- `--no-cache-dir` 같은 옵션은 이미지를 더 가볍게 만듭니다.
- 애플리케이션이 스스로 healthcheck endpoint를 제공해야 합니다.

이미지가 작고, 설정이 분리되어 있고, healthcheck가 명확할수록 배포 자동화는 훨씬 예측 가능해집니다. 반대로 이 세 가지가 없으면 장애 대응도 사람 손에 의존하게 됩니다.

## 자주 하는 실수 5가지

1. **운영에서 `latest` 태그만 쓰는 실수**입니다. 어떤 버전이 살아 있는지 알기 어렵습니다.
2. **secret을 이미지에 구워 넣는 실수**입니다. 이미지가 유출되면 secret도 함께 유출됩니다.
3. **load balancer 뒤에서 healthcheck를 생략하는 실수**입니다. 죽은 인스턴스로 트래픽이 갑니다.
4. **운영 migration을 수동으로만 처리하는 실수**입니다. 배포 자동화의 의미가 약해집니다.
5. **rollback 절차를 준비하지 않는 실수**입니다. 장애 대응이 즉흥적으로 변합니다.

## 운영에서는 이렇게 드러납니다

많은 팀은 Docker + GitHub Actions + 오케스트레이터(Kubernetes, ECS 등) 조합을 씁니다. PR이 merge되면 CI가 이미지를 만들고 registry에 push하고 배포를 진행합니다. 운영자는 명령을 직접 치기보다 시스템 상태를 관찰하는 쪽으로 역할이 이동합니다.

배포가 안정화된 팀일수록 “배포하는 법”보다 “문제 생기면 어떻게 되돌릴 것인가”를 더 분명히 문서화해 둡니다. 좋은 배포는 성공 절차뿐 아니라 실패 절차도 예측 가능해야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 모든 배포는 되돌릴 수 있어야 합니다.
- secret은 오직 secret manager에 둡니다.
- 이미지가 작을수록 빌드와 배포가 빨라집니다.
- migration은 이전 버전과의 호환성을 고려해 설계합니다.
- 누군가를 깨우는 배포는 그 자체로 나쁜 배포입니다.

## 체크리스트

- [ ] Dockerfile을 작성하고 이미지를 빌드할 수 있습니다.
- [ ] 설정을 환경 변수로 분리할 수 있습니다.
- [ ] `/healthz` endpoint를 추가할 수 있습니다.
- [ ] secret을 이미지 밖에 둘 수 있습니다.
- [ ] rolling update 흐름을 설명할 수 있습니다.

## 연습 문제

1. FastAPI 앱을 Dockerize하고 로컬에서 실행해 보세요.
2. `.env` 파일과 `docker run --env-file`로 설정을 분리해 보세요.
3. healthcheck를 일부러 깨뜨리고 컨테이너 상태가 어떻게 바뀌는지 확인해 보세요.

## 정리와 다음 글

배포는 재현성의 문제입니다. 마지막 글에서는 지금까지 배운 아홉 개 레이어를 하나의 운영 가능한 백엔드 구조로 묶어 보겠습니다.

<!-- toc:begin -->
- [백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [HTTP 서버 만들기](./02-building-an-http-server.md)
- [Routing과 Controller](./03-routing-and-controllers.md)
- [Service Layer](./04-service-layer.md)
- [Database Layer](./05-database-layer.md)
- [인증과 권한](./06-auth-and-authorization.md)
- [Logging과 Error Handling](./07-logging-and-error-handling.md)
- [백엔드 테스트](./08-testing-the-backend.md)
- **백엔드 배포 (현재 글)**
- 운영 가능한 백엔드 구조 (예정)
<!-- toc:end -->

## 참고 자료

- [Docker get-started](https://docs.docker.com/get-started/)
- [The Twelve-Factor App](https://12factor.net/)
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

Tags: Backend, Deployment, Docker, DevOps, Python
