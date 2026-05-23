---
series: backend-development-101
episode: 9
title: "Backend Development 101 (9/10): 백엔드 배포"
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
last_reviewed: '2026-05-15'
---

# Backend Development 101 (9/10): 백엔드 배포

로컬에서 잘 돌아가는 백엔드가 운영에서 실패하는 장면은 드물지 않습니다. 코드가 틀렸기 때문이 아니라, 실행 환경이 재현되지 않았기 때문인 경우가 더 많습니다. 배포를 "코드를 서버에 올리는 일"로 이해하면 이 실패를 설명하기 어렵고, 배포를 "실행 환경을 버전으로 고정하는 일"로 이해하면 실패 원인과 해결 순서가 선명해집니다.

이번 글에서는 재현 가능한 배포를 중심에 두고 Docker, 환경 변수, health check, rolling update, CI/CD, reverse proxy, 로컬 compose 운영까지 한 번에 연결하겠습니다. 목표는 명령어 암기가 아니라 "왜 이 순서로 설계해야 운영에서 안전한가"를 이해하는 것입니다.

![Backend Development 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/09/09-01-concept-at-a-glance.ko.png)
*Backend Development 101 9장 흐름 개요*

## 먼저 던지는 질문

- 배포 환경은 어떤 요소들로 이루어질까요?
- Dockerfile은 왜 재현 가능한 실행 환경을 만드는 핵심일까요?
- 환경 변수와 secret은 어떻게 분리해야 할까요?

## 배포를 재현성 문제로 보는 이유

배포를 업로드 작업으로 보면 결과를 사람 감각으로 확인하게 됩니다. "이번에는 잘 떴나"라는 확인이 반복되고, 담당자가 바뀌면 품질이 흔들립니다. 반대로 배포를 재현성 문제로 보면 핵심 질문이 바뀝니다.

- 같은 커밋에서 같은 이미지가 항상 만들어지는가
- 같은 이미지가 개발/스테이징/운영에서 동일하게 실행되는가
- 환경별 차이는 코드가 아니라 설정 주입으로만 제어되는가
- 새 버전이 준비되기 전에는 트래픽을 받지 않도록 강제되는가

이 네 가지가 만족되면 배포 품질은 개인 숙련도에서 시스템 설계로 이동합니다. 시니어가 보는 배포의 본질은 "실행 결과를 예측 가능하게 만드는 제약"입니다.

## Dockerfile을 운영 문서로 다루기

Dockerfile은 단순 빌드 스크립트가 아니라 런타임 계약서입니다. Python 버전, 시스템 패키지, 의존성 잠금, 실행 엔트리포인트를 명시합니다. 운영 장애의 절반 이상은 코드보다 이 계약서의 빈칸에서 시작합니다.

### Dockerfile anatomy: 각 줄의 책임

```dockerfile
FROM python:3.12-slim AS runtime

# 운영 컨테이너의 기본 작업 디렉터리
WORKDIR /app

# 파이썬 버퍼링/pyc 정책을 고정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 의존성 설치를 먼저 고정해 레이어 캐시 효율을 올림
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY app ./app
COPY main.py .

# FastAPI 앱이 수신할 내부 포트
EXPOSE 8000

# PID 1 프로세스 명시
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`COPY requirements.txt`를 먼저 두는 이유는 의존성 레이어 캐시를 재사용하기 위해서입니다. 코드만 바뀌는 배포에서 pip 재설치를 매번 강제하면 CI 시간이 급격히 늘어납니다. 빌드 속도는 개발 생산성 지표이면서 릴리스 안정성 지표이기도 합니다.

### multi-stage build: 런타임 이미지를 작게 유지

빌드 단계와 실행 단계를 분리하면 보안과 성능을 동시에 얻습니다.

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY app ./app
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

빌드에만 필요한 도구를 runtime에 남기지 않으면 이미지 크기와 공격 표면이 함께 줄어듭니다. "작은 이미지"는 단순 취향이 아니라 배포 시간, 롤백 속도, 취약점 스캔 시간에 직결됩니다.

### .dockerignore: 빌드 컨텍스트 최소화

`.dockerignore`가 없으면 `.git`, 테스트 산출물, 로컬 가상환경이 이미지 빌드 컨텍스트에 포함됩니다. 네트워크 전송량과 캐시 무효화 빈도가 모두 증가합니다.

```gitignore
.git
.venv
__pycache__
.pytest_cache
.coverage
*.log
.env
artifacts
reports
```

`.env`를 제외하지 않으면 secret 유출 리스크가 발생합니다. "이미지는 공개될 수 있다"를 기본 가정으로 두는 것이 안전합니다.

### 이미지 최적화 체크포인트

| 항목 | 나쁜 패턴 | 권장 패턴 | 이유 |
| --- | --- | --- | --- |
| 베이스 이미지 | `python:latest` | `python:3.12-slim` | 버전 고정으로 예측 가능성 확보 |
| 의존성 설치 | 코드 복사 후 설치 | requirements 먼저 복사 | 캐시 적중률 향상 |
| 캐시 처리 | pip 캐시 유지 | `--no-cache-dir` | 이미지 크기 감소 |
| 권한 | root 실행 | 비권한 사용자 실행 | 컨테이너 탈출 피해 축소 |
| 태깅 | latest 단일 태그 | semver + sha 태그 병행 | 롤백 추적 가능 |

## 환경 변수: 12-factor config와 secret 분리

운영 환경 차이는 코드 분기가 아니라 설정 주입으로 관리해야 합니다. 데이터베이스 주소, 외부 API endpoint, feature flag는 config입니다. 토큰, 비밀번호, signing key는 secret입니다. 두 값을 같은 방식으로 저장하면 사고가 납니다.

### pydantic-settings 패턴

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    app_name: str = 'backend-development-101'
    app_env: str = Field(default='local', alias='APP_ENV')

    db_host: str = Field(alias='DB_HOST')
    db_port: int = Field(default=5432, alias='DB_PORT')
    db_name: str = Field(alias='DB_NAME')
    db_user: str = Field(alias='DB_USER')
    db_password: str = Field(alias='DB_PASSWORD')

    jwt_secret: str = Field(alias='JWT_SECRET')
    redis_url: str = Field(alias='REDIS_URL')

settings = Settings()
```

이 패턴의 장점은 누락된 필수 값이 애플리케이션 시작 시점에 바로 실패한다는 점입니다. 배포 후 트래픽을 받은 뒤에야 오류를 발견하는 상황을 줄입니다.

### config와 secret 운영 경계

- config: GitOps 저장소 또는 환경별 설정 파일로 관리합니다.
- secret: Secret Manager, Vault, SSM Parameter Store 같은 전용 저장소로 관리합니다.
- 원칙: 코드 저장소, Dockerfile, 이미지 레이어에 secret을 남기지 않습니다.

```bash
# 나쁜 예: secret을 빌드 인자로 넘김 (레이어에 남을 수 있음)
docker build --build-arg JWT_SECRET=prod-secret .

# 권장 예: 실행 시점 주입
docker run --env-file .env.production myapp:1.4.2
```

## Health check: liveness와 readiness를 분리

오케스트레이터는 애플리케이션 내부를 알지 못합니다. 컨테이너 프로세스가 살아 있어도 DB 연결이 죽어 있으면 요청은 실패합니다. 이 간극을 메우는 인터페이스가 health check입니다.

- liveness: 프로세스가 회복 불가능 상태인지 확인합니다. 실패하면 재시작합니다.
- readiness: 트래픽을 받을 준비가 되었는지 확인합니다. 실패하면 서비스 라우팅에서 제외합니다.

### FastAPI health endpoint 예시

```python
from fastapi import FastAPI
from sqlalchemy import text

app = FastAPI()

@app.get('/health/live')
def liveness() -> dict[str, str]:
    # 프로세스 생존만 확인
    return {'status': 'alive'}

@app.get('/health/ready')
def readiness() -> dict[str, str]:
    # 실제 의존성까지 확인
    with app.state.db_engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    return {'status': 'ready'}
```

readiness에서 외부 의존성을 점검해야 무중단 배포가 성립합니다. "앱은 떴지만 아직 준비되지 않은 상태"를 명시적으로 구분하지 않으면 롤링 업데이트 중 5xx가 발생합니다.

### 왜 오케스트레이터가 이 신호를 필요로 하는가

| 상황 | health check 없음 | readiness 있음 |
| --- | --- | --- |
| 앱 시작 직후 캐시 워밍업 중 | 즉시 트래픽 유입, 초기 오류 발생 | 준비 완료 전까지 라우팅 제외 |
| DB 장애 | 앱은 살아 있음으로 오인 | 준비 실패로 트래픽 차단 |
| 코드 데드락 | 복구 지연 | liveness 실패로 자동 재시작 |

## Rolling update와 무중단 배포

무중단 배포는 "동시에 교체"가 아니라 "겹쳐서 교체"입니다. 핵심은 새 인스턴스 준비 확인, 트래픽 점진 전환, 기존 인스턴스의 정상 종료 순서입니다.

### 표준 시퀀스

1. 새 이미지(`1.4.2`) 컨테이너를 기동합니다.
2. readiness 통과 전까지 외부 트래픽을 붙이지 않습니다.
3. 인스턴스를 조금씩 증설하며 트래픽 비율을 이동합니다.
4. 기존 인스턴스에 종료 신호를 보내고 in-flight 요청 처리를 기다립니다.
5. 종료 유예 시간(grace period) 후 정리합니다.

### in-flight 요청과 graceful shutdown

배포 중 종료 신호(SIGTERM)를 받으면 즉시 프로세스를 죽이지 말고 연결을 정리해야 합니다.

```python
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 리소스 초기화
    app.state.is_draining = False
    yield
    # 종료 시 신규 요청 차단 및 리소스 정리
    app.state.is_draining = True
    await asyncio.sleep(5)

app = FastAPI(lifespan=lifespan)
```

`terminationGracePeriodSeconds` 같은 인프라 설정과 애플리케이션 종료 로직이 맞물려야 실제 무중단이 됩니다. 둘 중 하나만 있어도 끊김이 생깁니다.

## CI/CD: build → test → deploy 파이프라인

수동 배포가 사고를 만드는 이유는 "검증 단계 누락" 때문입니다. 파이프라인은 같은 순서를 기계가 반복하게 만들어야 합니다.

- Build: 이미지 생성, 태그 부여, 레지스트리 push
- Test: 단위 테스트, 통합 테스트, 정적 검사
- Deploy: 스테이징 배포 후 health 검증, 운영 점진 배포

### GitHub Actions 예시

```yaml
name: deploy-backend

on:
  push:
    branches: [main]

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - name: 저장소 체크아웃
        uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: 의존성 설치
        run: pip install -r requirements.txt

      - name: 테스트 실행
        run: pytest -q

      - name: Docker Buildx 설정
        uses: docker/setup-buildx-action@v3

      - name: 레지스트리 로그인
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: 이미지 빌드 및 푸시
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/your-org/backend:${{ github.sha }}
            ghcr.io/your-org/backend:1.4.2

      - name: 스테이징 배포
        run: ./scripts/deploy-staging.sh ${{ github.sha }}

      - name: 헬스 검증
        run: ./scripts/check-health.sh https://staging-api.example.com/health/ready

      - name: 운영 배포
        run: ./scripts/deploy-prod.sh ${{ github.sha }}
```

핵심은 "배포 성공"의 정의를 명령어 종료 코드가 아니라 health 검증 통과로 두는 것입니다.

## Reverse proxy와 TLS termination

FastAPI 애플리케이션이 보통 8000 포트에 바인딩되는 이유는 애플리케이션과 TLS 종단 처리를 분리하기 위해서입니다. 공개 인터넷에 바로 앱을 노출하면 인증서 갱신, 연결 제한, 정적 자산 캐시 정책이 분산됩니다.

### 일반 구성

- 애플리케이션: 내부 네트워크에서 `0.0.0.0:8000`
- reverse proxy(nginx/traefik): 80/443 수신, TLS 종료, 라우팅
- load balancer: 다중 인스턴스 분산

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api/privkey.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

reverse proxy는 단순 포트 전달기가 아니라 운영 제어면입니다. 요청 제한, 타임아웃, gzip, 접근 로그, TLS 갱신 정책을 한 곳에서 관리하게 해 줍니다.

## Docker Compose로 로컬 멀티 서비스 재현

로컬 단일 프로세스 실행만으로는 운영 장애를 재현하기 어렵습니다. 최소한 앱+DB+Redis를 묶어 "의존성 있는 실행"을 반복 가능하게 만들어야 합니다.

```yaml
services:
  app:
    build:
      context: .
    image: backend-dev:local
    ports:
      - '8000:8000'
    env_file:
      - .env.local
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 10s
      timeout: 3s
      retries: 5

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
    ports:
      - '5432:5432'
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 10s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7
    ports:
      - '6379:6379'
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
```

이 구성은 "로컬에서도 readiness 실패를 경험할 수 있는가"를 기준으로 설계한 것입니다. 로컬과 운영의 차이를 줄이는 가장 현실적인 출발점입니다.

## 운영 시나리오로 배우는 실패 패턴

### 시나리오 1: 로컬은 되는데 운영만 실패

- 증상: 배포 직후 500 오류, 로그에 `KeyError: DB_HOST`
- 원인: 필수 환경 변수 미주입
- 대응: 시작 시 설정 검증 실패로 빠르게 중단, 누락 키를 배포 단계에서 차단

### 시나리오 2: deploy는 성공했는데 컨테이너가 즉시 종료

- 증상: 오케스트레이터 이벤트에 CrashLoopBackOff
- 원인: 애플리케이션 내부 포트(8000)와 서비스 포트 매핑 불일치
- 대응: `CMD`, `EXPOSE`, 서비스 매니페스트 포트를 단일 기준으로 통일

### 시나리오 3: 롤백이 불가능

- 증상: 장애 시 되돌릴 이미지가 없음
- 원인: `latest`만 사용, immutable tag 부재
- 대응: `service:semver`, `service:git-sha`를 동시 발행하고 배포 이력에 sha 기록

### 시나리오 4: 배포 후 DB migration 누락

- 증상: API는 살아 있으나 특정 endpoint만 500
- 원인: 코드와 스키마 버전 불일치
- 대응: 배포 파이프라인에서 migration 단계 명시, 실패 시 자동 중단

## 배포 체크리스트

아래 항목은 "있으면 좋은 것"이 아니라 운영 기본선입니다.

| 점검 항목 | 확인 질문 | 실패 시 위험 |
| --- | --- | --- |
| 환경 변수 | 필수 키가 모두 주입되었는가 | 부팅 실패 또는 런타임 예외 |
| secret 관리 | secret이 이미지/로그에 남지 않는가 | 보안 사고, 키 교체 비용 증가 |
| migration | 현재 릴리스에 필요한 스키마 반영 완료인가 | 부분 기능 장애 |
| health | liveness/readiness 모두 통과하는가 | 무중단 배포 실패 |
| rollback | 이전 안정 버전으로 즉시 복귀 가능한가 | 장애 장기화 |
| monitoring | 에러율/지연/리소스 경보가 활성화되었는가 | 탐지 지연 |

## 시니어 관점에서 보는 흔한 실수와 이유

1. `latest` 태그만 쓰는 실수
   - 왜 위험한가: 같은 태그가 다른 이미지를 가리킬 수 있어 재현이 불가능합니다.
2. secret을 `.env`와 함께 저장소에 커밋하는 실수
   - 왜 위험한가: 사고가 나면 키 회전과 영향 분석 비용이 배포 속도보다 훨씬 큽니다.
3. readiness 없이 liveness만 설정하는 실수
   - 왜 위험한가: 앱은 살아 있는데 준비되지 않은 인스턴스로 트래픽이 들어갑니다.
4. migration을 수동으로 실행하는 실수
   - 왜 위험한가: 야간 배포, 담당자 교체, 긴급 패치에서 누락 가능성이 높습니다.
5. graceful shutdown 시간을 0에 가깝게 두는 실수
   - 왜 위험한가: in-flight 요청이 끊겨 사용자 체감 장애가 발생합니다.

## 실전 배포 흐름 예시

아래 순서는 팀 규모와 플랫폼이 달라도 거의 그대로 적용됩니다.

```text
1) main merge
2) CI 테스트 통과
3) 이미지 빌드 및 sha 태깅
4) 스테이징 배포
5) readiness/에러율 검증
6) 운영 rolling update
7) 배포 후 10분 관측
8) 기준 초과 시 자동 또는 수동 rollback
```

좋은 배포 프로세스는 "실패를 빨리 발견하고, 빨리 되돌리는 능력"까지 포함합니다. 성공률만 보는 지표는 위험합니다.

## 배포 직후 10분 운영 루틴

배포 명령이 끝난 시점은 시작선입니다. 실제 안정성은 배포 직후 10분 관측 루틴으로 결정됩니다. 이 루틴이 고정되어 있으면 야간 배포와 긴급 패치에서도 판단 기준이 흔들리지 않습니다.

| 시간 구간 | 확인 지표 | 판단 기준 |
| --- | --- | --- |
| 0-2분 | readiness 통과율 | 인스턴스별 100% 통과 확인 |
| 2-5분 | 5xx 비율, p95 지연 | 직전 배포 대비 급증 여부 확인 |
| 5-10분 | DB 연결 수, 큐 적체, 재시도율 | 백그라운드 부하 증가 여부 확인 |

이 관측 루틴에서 중요한 점은 "평균"이 아니라 "변화율"입니다. 평균 응답 시간이 정상이어도 p95가 급등하면 특정 경로에서 병목이 발생했을 가능성이 큽니다. 배포 기준선은 단일 숫자가 아니라 다중 지표의 조합으로 관리해야 합니다.

## migration과 롤백을 함께 설계하기

백엔드 배포에서 가장 위험한 변경은 코드가 아니라 스키마입니다. migration을 포함한 배포는 항상 "앞으로 가는 경로"와 "뒤로 오는 경로"를 같이 설계해야 합니다.

- expand 단계: nullable 컬럼 추가, 새 인덱스 생성처럼 이전 버전과 공존 가능한 변경을 먼저 배포합니다.
- deploy 단계: 새 코드가 구/신 스키마를 모두 읽을 수 있게 점진 전환합니다.
- contract 단계: 충분한 관측 후 더 이상 쓰지 않는 컬럼/경로를 정리합니다.

이 전략을 적용하면 배포 실패 시 이전 애플리케이션 버전으로 되돌려도 데이터 계층 충돌을 줄일 수 있습니다. 반대로 파괴적 migration을 코드 배포와 한 번에 묶으면, 애플리케이션 롤백이 곧 데이터 롤백을 요구하게 되어 복구 시간이 급증합니다.

## 현장에서 바로 쓰는 배포 전 점검 질문

- 현재 릴리스 이미지 sha를 한 문장으로 설명할 수 있는가
- 이 릴리스가 의존하는 환경 변수 목록이 문서화되어 있는가
- migration 실패 시 중단/복구 절차가 스크립트로 존재하는가
- readiness가 외부 의존성(DB, 캐시, 메시지 브로커)까지 검증하는가
- 롤백 시 되돌리지 말아야 할 값(예: feature flag, 운영 토글)을 분리했는가

팀이 이 질문에 즉답하지 못하면 배포 자동화가 있어도 운영 자동화는 없는 상태입니다. 시니어 엔지니어의 배포 설계는 도구 선택보다 "실패했을 때 팀이 같은 판단을 하게 만드는 문서와 절차"에 더 많은 시간을 씁니다.

## 처음 질문으로 돌아가기

- **배포 환경은 어떤 요소들로 이루어질까요?**
  - 배포 환경은 코드 저장소, 컨테이너 이미지, 환경 변수와 secret, 오케스트레이터, reverse proxy, 관측 도구가 결합된 실행 시스템입니다. 코드만 맞아도 실패할 수 있으며, 각 계층의 계약이 일치해야 실제 운영에서 재현됩니다.
- **Dockerfile은 왜 재현 가능한 실행 환경을 만드는 핵심일까요?**
  - Dockerfile은 런타임 버전, 의존성 설치 순서, 엔트리포인트를 고정해 동일한 이미지를 반복 생산하게 만듭니다. multi-stage, 레이어 캐시, `.dockerignore`를 함께 설계하면 속도와 안정성, 보안이 동시에 개선됩니다.
- **환경 변수와 secret은 어떻게 분리해야 할까요?**
  - config는 환경별 동작 값을 주입하고, secret은 전용 비밀 저장소에서 런타임에만 전달해야 합니다. `pydantic-settings`로 필수 값을 시작 시 검증하면 누락을 조기에 차단할 수 있고, 배포 실패를 트래픽 유입 전에 멈출 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): Database Layer](./05-database-layer.md)
- [Backend Development 101 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- [Backend Development 101 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- [Backend Development 101 (8/10): 백엔드 테스트](./08-testing-the-backend.md)
- **백엔드 배포 (현재 글)**
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Docker get-started](https://docs.docker.com/get-started/)
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [The Twelve-Factor App](https://12factor.net/)

Tags: Backend, Deployment, Docker, DevOps, Python
