---
series: docker-101
episode: 6
title: "Docker 101 (6/10): 환경변수와 설정"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/258"
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
  - Config
  - EnvVar
  - Secret
  - 12Factor
seo_description: 하나의 이미지에 환경별 설정과 비밀값을 안전하게 주입하는 원칙을 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (6/10): 환경변수와 설정

컨테이너를 만들기 시작하면 곧 이런 요구가 생깁니다. 개발 환경에서는 디버그 로그를 켜고 싶고, 스테이징과 운영에서는 다른 데이터베이스 주소를 써야 하며, 비밀번호와 토큰은 코드나 이미지 안에 넣고 싶지 않습니다. 그런데 이때 환경마다 다른 이미지를 따로 빌드하기 시작하면 재현성은 금방 무너집니다.

이 글은 Docker 101 시리즈의 6번째 글입니다.

좋은 컨테이너 운영의 핵심은 이미지와 환경을 분리하는 것입니다. 이미지는 불변 산출물로 유지하고, 환경별 차이는 런타임 설정으로 주입해야 합니다. 이 원칙이 바로 Twelve-Factor의 config 원칙과도 맞닿아 있습니다.

![Docker 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/06/06-01-concept-at-a-glance.ko.png)
*Docker 101 6장 흐름 개요*

> 컨테이너 운영의 핵심 규칙은 '이미지와 환경을 분리'하는 것입니다 — 환경마다 다른 이미지를 빌드하기 시작하면 재현성이 바로 무너지므로, 이미지는 불변 산출물로 유지하고 환경별 차이는 런타임 환경변수와 외부 설정으로 주입해야 합니다(Twelve-Factor config).

## 이 글에서 다룰 문제

- 하나의 이미지로 여러 환경을 어떻게 지원할 수 있을까요?
- `ENV`와 `ARG`는 무엇이 다를까요?
- 환경변수, 설정 파일, secret은 어떻게 구분하는 편이 좋을까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

컨테이너가 재현 가능하려면 dev, staging, prod를 거치면서도 이미지 자체는 바뀌지 않아야 합니다. 환경별 차이를 코드에 하드코딩하거나, 환경마다 다른 이미지를 다시 빌드하면 "같은 애플리케이션"이라는 전제가 사라집니다.

또한 secret을 어디에 두는지는 단순한 편의 문제가 아니라 보안 문제입니다. 이미지 안에 비밀번호가 들어간 순간, 그 이미지를 받은 모든 곳에 비밀값도 함께 복제됩니다. 한번 새어 나간 secret은 되돌릴 수 없습니다.

### ENV vs ARG 차이

| 특성 | `ENV` | `ARG` |
|------|-------|-------|
| 정의 위치 | Dockerfile | Dockerfile |
| 빌드 시 사용 | O | O |
| 최종 이미지에 남음 | O (항상) | X (빌드 후 사라짐) |
| 런타임에 사용 | O | X |
| 오버라이드 방법 | `-e VAR=value` (런타임) | `--build-arg VAR=value` (빌드 시) |
| 비밀값 저장 | 절대 안 됨 (이미지에 박힘) | 주의 필요 (히스토리에 노출) |

```dockerfile
# ARG: 빌드 시점에만 사용
ARG APP_VERSION=dev
ARG BUILD_DATE

# ENV: 최종 이미지와 런타임에 남음
ENV APP_VERSION=${APP_VERSION} \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

# 빌드: docker build --build-arg APP_VERSION=1.2.3 .
# 런타임: docker run -e LOG_LEVEL=DEBUG myapp
```

### 설정 계층 구조

```
우선순위 (높음 → 낮음)
1. docker run -e KEY=value           런타임 직접 지정
2. docker run --env-file .env.prod   파일 기반 지정
3. compose.yaml environment:         Compose 정의
4. compose.yaml env_file:            Compose 파일 참조
5. .env (Compose 자동 로드)          프로젝트 기본값
6. Dockerfile ENV                    이미지 기본값
```

## 전과 후

**Before**: dev용 이미지와 prod용 이미지를 따로 빌드해 각각 운영합니다. "스테이징에서 됐는데 운영에서 왜 안 되지?"라는 질문이 반복됩니다.

**After**: 이미지는 하나만 유지하고, 환경별 차이는 환경변수와 외부 설정으로 주입합니다. 같은 이미지가 모든 환경을 통과하므로 스테이징 검증을 신뢰할 수 있습니다.

이 차이는 팀 운영에서 매우 큽니다. 하나의 이미지가 여러 환경을 그대로 통과해야, 스테이징에서 검증한 결과를 운영에서도 믿을 수 있기 때문입니다.

## 실습: 환경변수와 설정을 5단계로 정리하기

### 1단계 — Dockerfile의 ENV와 ARG 올바르게 사용하기

```dockerfile
FROM python:3.12-slim

# 빌드 인자: 이미지 메타데이터 태깅용
ARG APP_VERSION=dev
ARG BUILD_DATE=unknown

# 런타임 환경변수: 안전한 기본값만
ENV APP_VERSION=${APP_VERSION} \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 이미지 메타데이터 (비밀값 절대 여기 넣지 않음)
LABEL version="${APP_VERSION}" \
      build-date="${BUILD_DATE}"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN useradd -m -u 1000 appuser
USER appuser

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

`ARG`는 빌드 시 값을 바꾸는 데 쓰고, `ENV`는 컨테이너 실행 시 기본값으로 남깁니다. 비밀값은 절대 `ENV`에 넣으면 안 됩니다. `docker history`나 `docker inspect`로 누구나 볼 수 있기 때문입니다.

### 2단계 — 런타임 주입 방법

```bash
# 단일 변수 주입
docker run --rm \
  -e LOG_LEVEL=DEBUG \
  -e DB_URL=postgres://user:pass@db:5432/app \
  myapp:1.0

# 환경 파일로 주입 (여러 변수를 한번에)
# .env.staging 파일
cat << 'EOF' > .env.staging
LOG_LEVEL=INFO
DB_URL=postgres://user:pass@stg-db:5432/app
REDIS_URL=redis://stg-cache:6379
MAX_WORKERS=4
EOF

docker run --rm --env-file .env.staging myapp:1.0
```

환경별 차이는 가능한 한 실행 시점에 주입하는 편이 좋습니다. 그래야 이미지를 다시 빌드하지 않고도 같은 산출물을 여러 환경에서 재사용할 수 있습니다.

### 3단계 — Compose에서 환경변수 관리

```yaml
# compose.yaml
services:
  web:
    image: myapp:1.0
    env_file:
      - .env.${ENV:-dev}       # ENV 변수로 파일 선택
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-INFO}    # 기본값 포함
      APP_PORT: ${APP_PORT:-8000}
      DB_HOST: db               # 서비스 이름은 직접 지정

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}      # 반드시 외부에서 주입
      POSTGRES_DB: ${DB_NAME:-app}
      POSTGRES_USER: ${DB_USER:-postgres}
```

```bash
# .env.dev
ENV=dev
LOG_LEVEL=DEBUG
DB_PASSWORD=dev_password

# .env.staging
ENV=staging
LOG_LEVEL=INFO
DB_PASSWORD=stg_password_from_vault
```

기본값 문법까지 함께 쓰면 누락된 값을 어느 정도 방어할 수 있습니다. 다만 기본값이 있다고 해서 모든 문제가 해결되는 것은 아닙니다. 필수값은 별도로 검증해야 합니다.

### 4단계 — 시작 시 필수 변수 검증

```python
# app/config.py
import os
import sys

def validate_required_env_vars():
    """필수 환경변수가 없으면 즉시 실패"""
    required = ["DB_URL", "SECRET_KEY", "REDIS_URL"]
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print(f"ERROR: Missing required environment variables: {missing}", file=sys.stderr)
        sys.exit(1)

# app/main.py
from fastapi import FastAPI
from .config import validate_required_env_vars

validate_required_env_vars()   # 시작 시 즉시 검증

app = FastAPI()
```

애플리케이션 시작 시점에 필수 환경변수를 검증해, 값이 없으면 빠르게 실패하게 만듭니다. 조용히 빈 문자열로 실행되는 시스템은 언젠가 더 비싼 장애로 돌아옵니다.

### 5단계 — secret 외부화

```bash
# Doppler를 사용한 secret 주입 (예시)
# doppler run -- docker compose up -d

# AWS Secrets Manager (예시)
SECRET=$(aws secretsmanager get-secret-value \
  --secret-id myapp/prod/db \
  --query SecretString \
  --output text)
export DB_URL=$(echo $SECRET | jq -r '.db_url')
docker run --rm -e DB_URL="$DB_URL" myapp:1.0

# Docker secret (Swarm 환경)
echo "super_secret_password" | docker secret create db_password -
docker service create \
  --secret db_password \
  --name myapp \
  myapp:1.0
```

이 단계가 실제 운영 품질을 가릅니다. secret을 Compose 파일이나 Dockerfile에 직접 넣지 않고, 외부 secret 제공자를 통해 런타임에 주입해야 노출 면적을 줄일 수 있습니다.

### 실행 뒤 바로 확인할 것

- `docker run --env-file .env.staging myapp:1.0`으로 실행했을 때 로그나 진단 엔드포인트에서 `LOG_LEVEL`, `DB_URL` 같은 값이 의도한 환경으로 들어왔는지 확인합니다.
- 필수 변수를 비워 실행해 보면 애플리케이션이 조용히 진행하지 않고 빠르게 실패해야 합니다.
- `docker history myapp:1.0`에서 비밀값이 레이어에 박혀 있지 않은지 확인합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| 환경변수 값이 비어 들어감 | `.env` 파일 경로 오류, 변수명 오타 | `docker compose config`로 실제 값 확인 |
| secret이 이미지에 남음 | Dockerfile `ENV`에 비밀값 지정 | `docker history`로 확인 후 `ENV` 제거, 런타임 주입으로 변경 |
| 필수 변수 누락으로 런타임 오류 | 시작 시 검증 없음 | 앱 시작 시점에 validation 추가 |
| `.env` 파일이 자동 로드 안 됨 | Compose 파일과 다른 디렉터리에 있음 | `compose.yaml`과 같은 위치에 `.env` 파일 배치 |
| ARG로 secret 전달 후 노출 | `docker history`에 build arg 값이 기록됨 | secret은 BuildKit secret mount 사용 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| secret을 Dockerfile `ENV`에 넣음 | 이미지 안에 영구 박제, 누구나 볼 수 있음 | 런타임에 `-e` 또는 `--env-file`로 주입 |
| `.env`를 Git에 커밋 | 비밀값 유출 사고 | `.gitignore`에 추가, `.env.example`만 커밋 |
| 환경마다 별도 이미지를 빌드 | 재현성 붕괴 ("스테이징에서 됐는데...") | 하나의 이미지 + 환경변수로 차이 주입 |
| 필수 변수가 비어도 그냥 실행 | 런타임 오류가 늦게 드러남 | 시작 시 필수 변수 검증 로직 추가 |
| 로그에 환경변수 전체 출력 | 비밀값이 로그에 노출될 수 있음 | 필수 변수 이름만 로그, 값은 마스킹 |

## .env.example 관리

```bash
# .env.example (항상 Git에 커밋)
# 이 파일은 실제 값이 아닌 형식과 설명을 담습니다

# 데이터베이스
DB_URL=postgres://user:password@host:5432/dbname
DB_POOL_SIZE=10

# 애플리케이션
SECRET_KEY=your-secret-key-here         # 최소 32자 이상 랜덤 문자열
LOG_LEVEL=INFO                           # DEBUG, INFO, WARNING, ERROR
APP_PORT=8000

# Redis
REDIS_URL=redis://localhost:6379/0

# 외부 서비스 (선택)
SENTRY_DSN=                              # 비어 있으면 비활성화
```

`.env.example`은 항상 함께 관리해야 합니다. 새 팀원이 어떤 변수가 필요한지 알 수 있고, PR에서 새 변수 추가 시 리뷰 가능해집니다.

## 환경별 설정 파일 구조 예시

```
프로젝트 루트/
├── .env.example          ← Git 커밋 (형식 문서화)
├── .env                  ← Git 제외 (로컬 개발)
├── .env.staging          ← Git 제외 (스테이징)
├── .env.prod             ← Git 제외 또는 secret 관리 도구에서
├── compose.yaml          ← Git 커밋
└── .gitignore
    ├── .env
    ├── .env.staging
    └── .env.prod
```

```bash
# 환경별 실행
ENV=dev     docker compose up -d
ENV=staging docker compose up -d
ENV=prod    docker compose up -d

# compose.yaml에서 ENV 변수로 파일 선택
# env_file: .env.${ENV:-dev}

# Doppler 사용 예시 (CI/CD)
doppler run --project myapp --config prod -- docker compose up -d

# GitHub Actions에서 secret 주입
# env:
#   DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

## 실무에서는 이렇게 이어집니다

성숙한 팀은 Vault, Doppler, 1Password 같은 시스템을 런타임 secret 제공자로 사용하고, 코드 저장소에는 변수 이름과 예시값만 남깁니다. 즉, 저장소는 계약을 설명하고, 실제 값은 환경이 책임지게 만드는 구조입니다.

또한 애플리케이션 시작 시점에 필수 환경변수를 검증해, 값이 없으면 빠르게 실패하게 만듭니다. 조용히 빈 문자열로 실행되는 시스템은 언젠가 더 비싼 장애로 돌아옵니다.

## 환경변수 관련 자주 쓰는 명령

```bash
# ── 런타임 환경변수 확인 ─────────────────────────────────────
docker exec api env                    # 컨테이너 내 전체 env
docker exec api env | grep DB         # 특정 변수만 필터
docker inspect api | jq '.[0].Config.Env'  # inspect로 확인

# ── 환경변수 주입 방법 비교 ──────────────────────────────────
# 1. 직접 지정
docker run -e LOG_LEVEL=DEBUG myapp:1.0

# 2. 파일 기반
docker run --env-file .env.staging myapp:1.0

# 3. 호스트 env 전달
export DB_URL=postgres://...
docker run -e DB_URL myapp:1.0         # 값 없이 이름만 쓰면 호스트 값 전달

# 4. Compose
docker compose --env-file .env.staging up -d

# ── 디버깅 ───────────────────────────────────────────────────
docker compose config                  # 실제 값 치환 확인
docker compose config | grep -A5 environment  # 환경변수 섹션만 확인
```

## 운영 체크리스트

- [ ] 이미지는 환경에 중립적입니다 (환경별 이미지를 따로 빌드하지 않음).
- [ ] secret은 이미지나 Compose 파일 안에 없습니다.
- [ ] `.env.example`이 존재하고 최신 상태입니다.
- [ ] `.env`는 `.gitignore`에 포함되어 있습니다.
- [ ] 앱 시작 시 필수 변수 검증이 있습니다.
- [ ] `docker history`에서 비밀값이 보이지 않습니다.

## 연습 문제

1. 같은 이미지를 dev와 staging에서 각각 다른 `--env-file`로 실행해 보세요. `LOG_LEVEL`이 다르게 설정되는지 확인해 보세요.
2. `--env-file`로 환경별 설정을 분리하고 `docker run --env-file .env.dev myapp` 형식으로 실행해 보세요.
3. 필수 환경변수(`DB_URL`, `SECRET_KEY`)가 없으면 시작에 실패하는 검증 코드를 추가해 보세요.
4. `.env.example` 파일을 작성하고 `.env`를 `.gitignore`에 추가해 Git이 실제 값을 추적하지 않게 해 보세요.

## 처음 질문으로 돌아가기

- **하나의 이미지로 여러 환경을 어떻게 지원할 수 있을까요?**
  - 이미지는 모든 환경에서 동일하게 유지하고, 환경별 차이(DB 주소, 로그 레벨, 비밀값 등)는 런타임에 환경변수로 주입합니다. `docker run -e`, `--env-file`, Compose `environment:`로 주입할 수 있습니다.

- **`ENV`와 `ARG`는 무엇이 다를까요?**
  - `ARG`는 빌드 시점에만 존재하고 최종 이미지에 남지 않습니다. `ENV`는 최종 이미지와 런타임에 모두 남습니다. 비밀값은 두 곳 모두에 넣으면 안 됩니다. `ARG`는 `docker history`에 노출될 수 있고, `ENV`는 이미지에 영구적으로 박힙니다.

- **환경변수, 설정 파일, secret은 어떻게 구분하는 편이 좋을까요?**
  - 환경변수: 환경별로 다른 비민감 설정(LOG_LEVEL, PORT, HOST). 설정 파일: 복잡한 구조화 설정(nginx.conf, prometheus.yml). Secret: 비밀번호, 토큰, API 키 — 반드시 외부 시스템(Vault, Doppler)에서 런타임에 주입.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - 이미지 안에 들어간 secret은 이미 유출된 것과 같습니다. `.env` 파일은 절대 Git에 올리면 안 됩니다. 로그에 환경변수 전체를 출력하는 코드는 secret 노출로 이어질 수 있습니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - Dockerfile의 `ENV`에 DB 비밀번호를 넣거나, `.env` 파일을 실수로 Git에 커밋하는 경우가 가장 많습니다. 또한 환경별로 이미지를 따로 빌드해 스테이징과 운영이 사실상 다른 애플리케이션이 되는 문제도 흔합니다.

## 정리

설정 분리는 프로덕션 안정성의 절반입니다. 이미지는 하나로 유지하고, 환경별 차이와 비밀값은 런타임에 주입해야 재현성과 보안을 동시에 지킬 수 있습니다. 컨테이너를 잘 만든다는 것은 Dockerfile만 잘 쓰는 것이 아니라, 무엇을 이미지 밖에 남겨 둘지까지 결정하는 일입니다.

다음 글에서는 Python 앱을 실제로 컨테이너화합니다. 설정 원칙을 바탕으로 FastAPI 앱을 production-grade 수준으로 묶을 때 어떤 점을 챙겨야 하는지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- **Docker 101 (6/10): 환경변수와 설정 (현재 글)**
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- [배포용 Docker 구성](./10-production-docker.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Set environment variables in containers](https://docs.docker.com/engine/reference/commandline/run/#env)
- [Compose - environment variables](https://docs.docker.com/compose/environment-variables/)
- [Manage secrets with Docker](https://docs.docker.com/engine/swarm/secrets/)

### 검증과 트러블슈팅

- [Environment variables in Compose](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Config, EnvVar, Secret, 12Factor
