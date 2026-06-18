---
title: "바이브코딩을 위한 Backend Development 기초 (9/10): 백엔드 배포"
series: backend-development-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Backend
  - Deployment
  - Docker
  - DevOps
  - Python
---

# 바이브코딩을 위한 Backend Development 기초 (9/10): 백엔드 배포

이 글은 "바이브코딩을 위한 Backend Development 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 "docker build 후 push하면 됩니다"라고 단순하게 안내합니다. 하지만 로컬에서 잘 돌아가는 백엔드가 운영에서 실패하는 장면은 드물지 않습니다. 배포를 "코드를 서버에 올리는 일"로 이해하면 이 실패를 설명하기 어렵습니다. 배포를 "실행 환경을 버전으로 고정하는 일"로 이해해야 실패 원인과 해결 순서가 선명해집니다.

재현 가능한 배포를 중심에 두고 Docker, 환경 변수, health check, rolling update까지 한 번에 연결합니다. 목표는 명령어 암기가 아니라 "왜 이 순서로 설계해야 운영에서 안전한가"를 이해하는 것입니다.

> **핵심 인사이트:** 배포는 '코드를 서버에 올리는 일'이 아니라 '실행 중인 시스템의 상태를 한 버전에서 다른 버전으로 안전하게 옮기는 일'입니다.

## 이 글에서 다룰 문제

- 배포 환경은 어떤 요소들로 이루어질까요?
- Dockerfile은 왜 재현 가능한 실행 환경을 만드는 핵심일까요?
- 환경 변수와 secret은 어떻게 분리해야 할까요?
- liveness와 readiness probe의 차이는 무엇인가요?
- AI가 배포를 단순하게 안내할 때 어떻게 보완할까요?

## Dockerfile과 health check 패턴

```dockerfile
FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# health endpoint
@app.get('/health/live')
def liveness():
    return {'status': 'alive'}

@app.get('/health/ready')
def readiness():
    with app.state.db_engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    return {'status': 'ready'}
```

## 변경 전후 비교

**Before: 환경별 코드 분기**
```python
if os.environ.get("ENV") == "prod":
    DB_URL = "postgresql://prod-host/app"
else:
    DB_URL = "sqlite:///./dev.db"
```

**After: 환경 변수로만 주입**
```python
class Settings(BaseSettings):
    db_url: str = Field(alias='DATABASE_URL')
    jwt_secret: str = Field(alias='JWT_SECRET')

settings = Settings()  # 필수 값 누락 시 시작 시점에 실패
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `latest` 태그만 사용 | 같은 태그가 다른 이미지를 가리킬 수 있어 재현 불가 | semver + git-sha 태그 병행 |
| secret을 `.env`로 커밋 | 사고 시 키 회전과 영향 분석 비용이 큼 | Secret Manager, Vault 사용 |
| readiness 없이 liveness만 설정 | 준비되지 않은 인스턴스로 트래픽 유입 | liveness/readiness 분리 |
| migration을 수동으로 실행 | 야간 배포, 담당자 교체 시 누락 가능 | 배포 파이프라인에 migration 단계 명시 |
| graceful shutdown 시간 0 | in-flight 요청 끊겨 사용자 체감 장애 | SIGTERM 후 유예 시간 확보 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"FastAPI 백엔드 Dockerfile을 만들어줘.
multi-stage build, 비root 실행,
liveness/readiness health endpoint,
pydantic-settings로 환경 변수 관리까지 포함해야 해"

# 배포 전 점검 질문:
- 현재 릴리스 이미지 sha를 한 문장으로 설명할 수 있는가
- 이 릴리스가 의존하는 환경 변수 목록이 문서화되어 있는가
- readiness가 외부 의존성(DB, 캐시)까지 검증하는가
```

## 운영 체크리스트

- [ ] 배포 파이프라인에 build → test → deploy 단계가 있다
- [ ] 이미지 태그가 semver와 git-sha로 고정되어 있다
- [ ] secret이 이미지와 로그에 남지 않는다
- [ ] liveness와 readiness probe가 분리되어 있다
- [ ] migration이 배포 파이프라인에 포함되어 있다
- [ ] 롤백 가능한 이전 안정 버전이 확보되어 있다

## 처음 질문으로 돌아가기

- **배포 환경은 어떤 요소들로 이루어질까요?** 이미지 버전, 환경 변수, secret, 네트워크 설정, health check가 모두 재현 가능하게 고정되어야 합니다.
- **Dockerfile은 왜 핵심일까요?** Python 버전, 의존성, 엔트리포인트를 명시해 런타임 계약서 역할을 합니다.
- **환경 변수와 secret 분리는?** config는 설정 파일, secret은 전용 저장소(Vault, Secret Manager)로 분리합니다.

## 정리

배포를 재현성 문제로 보는 시각이 잡히면 Dockerfile, health check, secret 관리, rolling update의 목적이 선명해집니다. 바이브코딩에서 AI가 단순한 배포 스크립트를 제시할 때, 이 글의 원칙들을 더해 운영 가능한 배포로 완성하세요. 다음 글에서는 운영 가능한 백엔드 전체 구조를 정리합니다.

## 참고 자료

- [Docker get-started](https://docs.docker.com/get-started/)
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [The Twelve-Factor App](https://12factor.net/)
- [backend-development-101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Backend Development 기초 (1/10): 백엔드 개발이란 무엇인가?
- 바이브코딩을 위한 Backend Development 기초 (2/10): HTTP 서버 만들기
- 바이브코딩을 위한 Backend Development 기초 (3/10): Routing과 Controller
- 바이브코딩을 위한 Backend Development 기초 (4/10): Service Layer
- 바이브코딩을 위한 Backend Development 기초 (5/10): Database Layer
- 바이브코딩을 위한 Backend Development 기초 (6/10): 인증과 권한
- 바이브코딩을 위한 Backend Development 기초 (7/10): Logging과 Error Handling
- 바이브코딩을 위한 Backend Development 기초 (8/10): 백엔드 테스트
- **바이브코딩을 위한 Backend Development 기초 (9/10): 백엔드 배포 (현재 글)**
- 바이브코딩을 위한 Backend Development 기초 (10/10): 운영 가능한 백엔드 구조
<!-- toc:end -->

Tags: 바이브코딩, Backend, Deployment, Docker, DevOps, Python
