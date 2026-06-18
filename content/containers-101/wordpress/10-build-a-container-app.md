---
title: "바이브코딩을 위한 Containers 기초 (10/10): 실전 컨테이너 앱 만들기"
series: containers-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Containers
  - Docker
  - Compose
  - FastAPI
  - DevOps
---

# 바이브코딩을 위한 Containers 기초 (10/10): 실전 컨테이너 앱 만들기

이 글은 "바이브코딩을 위한 Containers 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 Dockerfile과 docker-compose.yml을 금방 만들어 줍니다. 하지만 개별 명령이 모여 재현 가능한 스택이 되려면, 이미지, 네트워크, 볼륨, 보안, healthcheck가 하나의 실행 흐름으로 연결되어야 합니다. "일단 뜨는 것"과 "누구나 같은 명령으로 띄우고 관찰하고 복구할 수 있는 것"은 전혀 다른 수준입니다.

FastAPI와 Postgres를 예시로, Dockerfile, Compose, healthcheck, 시크릿 분리, 로그 확인을 하나의 실행 스택으로 연결해 봅니다. 이 루프가 10분 안에 돌아가야 컨테이너의 가치를 실제로 누리는 것입니다.

> **핵심 인사이트:** 실전 컨테이너 앱의 핵심은 개별 명령이 아니라, 로컬 개발 → CI 빌드 → 배포 → 운영 전체 파이프라인에서 재현성과 관찰성을 유지하는 것입니다.

## 이 글에서 다룰 문제

- FastAPI 앱용 Dockerfile은 어떤 기준으로 작성해야 할까요?
- Compose로 앱과 DB를 어떻게 함께 묶을 수 있을까요?
- healthcheck는 왜 orchestration 신호로 중요할까요?
- 바이브코딩에서 AI가 놓치는 운영 포인트는 무엇일까요?
- 컨테이너 스택에서 시크릿을 어떻게 분리해야 할까요?

## 실전 스택 구성

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
USER 1000
EXPOSE 8080
HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8080:8080"]
    environment:
      DB_URL: postgresql://app:secret@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 10
```

## 변경 전후 비교

**Before: 재현 불가능한 수동 명령**
```bash
docker run -d --name pg -e POSTGRES_PASSWORD=secret postgres:16
# DB가 준비됐는지 수동 확인 후
docker run -d --name app -e DB_URL=postgresql://... -p 8080:8080 myapp
```

**After: 선언적 Compose 스택**
```bash
docker compose up -d --build   # 빌드 + 기동 + 의존성 순서 + healthcheck 대기
docker compose ps              # 상태 확인
docker compose down -v         # 정리
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| DB 비밀번호를 Compose 파일에 평문으로 | Git에 올라가면 이력에 영구 기록 | `.env` 파일로 분리 후 `.gitignore` 추가 |
| healthcheck 없이 `depends_on`만 사용 | DB가 아직 준비되지 않았는데 앱이 기동 | `condition: service_healthy` 사용 |
| restart policy 없음 | OOM 시 수동 재시작까지 서비스 중단 | `restart: unless-stopped` 기본 설정 |
| volume 없이 DB 운영 | `down -v`로 데이터 유실 가능 | named volume 사용, `-v` 없이 down |
| 로그를 컨테이너 내부에만 저장 | 재시작 시 로그 소실 | stdout/stderr로 출력 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"FastAPI + Postgres Compose 스택을 만들어줘.
healthcheck, depends_on service_healthy,
비root USER, restart policy를 모두 포함해야 해.
시크릿은 .env로 분리해줘"

# 운영 전 검증 명령:
docker compose config
docker compose up -d --build
docker compose ps
curl -f http://127.0.0.1:8080/health
docker compose logs --tail=100
```

## 운영 체크리스트

- [ ] 런타임에서 비root로 실행한다 (`USER 1000`)
- [ ] healthcheck를 정의했다
- [ ] `depends_on: condition: service_healthy`를 사용한다
- [ ] 시크릿을 `.env`로 분리하고 `.gitignore`에 추가했다
- [ ] `restart: unless-stopped`를 설정했다
- [ ] teardown 명령을 문서화했다

## 처음 질문으로 돌아가기

- **Dockerfile은 어떤 기준으로 작성해야 할까요?** 비root 실행, healthcheck, 의존성 레이어 캐시 최적화를 Dockerfile 안에서 선언합니다.
- **Compose로 앱과 DB를 어떻게 묶을까요?** `depends_on + service_healthy` 조합으로 준비 완료 신호까지 함께 봅니다.
- **healthcheck는 왜 중요할까요?** orchestrator가 트래픽 라우팅과 재시작을 결정하는 신호이기 때문에 처음부터 정의해야 합니다.

## 정리

컨테이너 실전 역량은 명령어 암기가 아니라 이미지, 네트워크, 볼륨, 보안, healthcheck를 재현 가능한 스택으로 조립하는 능력에서 나옵니다. 바이브코딩에서 AI가 만들어 준 Compose 파일에 이 요소들이 빠져 있다면 직접 추가하세요. 다음 단계는 Kubernetes 101처럼 오케스트레이션 세계로 넘어가는 방향입니다.

## 참고 자료

- [Docker Compose](https://docs.docker.com/compose/)
- [FastAPI in containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Containers 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Containers 기초 (1/10): Container란 무엇인가?
- 바이브코딩을 위한 Containers 기초 (2/10): Image와 Layer
- 바이브코딩을 위한 Containers 기초 (3/10): Runtime
- 바이브코딩을 위한 Containers 기초 (4/10): Dockerfile
- 바이브코딩을 위한 Containers 기초 (5/10): Volume
- 바이브코딩을 위한 Containers 기초 (6/10): Network
- 바이브코딩을 위한 Containers 기초 (7/10): Registry
- 바이브코딩을 위한 Containers 기초 (8/10): Container Security
- 바이브코딩을 위한 Containers 기초 (9/10): Containers vs VMs
- **바이브코딩을 위한 Containers 기초 (10/10): 실전 컨테이너 앱 만들기 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Containers, Docker, Compose, FastAPI, DevOps
