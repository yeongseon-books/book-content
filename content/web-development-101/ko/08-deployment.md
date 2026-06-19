---
series: web-development-101
episode: 8
title: "Web Development 101 (8/10): 배포"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/210"
    published_at: '2026-05-26'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - WebDevelopment
  - Deployment
  - DevOps
  - CICD
  - Hosting
seo_description: 환경 분리, 빌드 산출물, PaaS, CI/CD로 배포 기본을 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (8/10): 배포

로컬에서 잘 돌아가는 앱을 세상에 보여 주는 순간부터 개발은 운영과 연결됩니다. 내 노트북에서는 되는데 서버에서는 안 되는 이유, 환경별 설정이 왜 갈리는지, 비밀 값은 어디에 둬야 하는지, 같은 코드를 어떻게 반복 가능하게 배포할지 모두 배포에서 드러납니다.

이 글은 Web Development 101 시리즈의 8번째 글입니다.

여기서는 환경 분리, 환경 변수와 비밀 관리, 빌드 산출물, PaaS와 IaaS의 차이, 그리고 기본적인 CI/CD 흐름을 함께 정리하겠습니다.

![Web Development 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/08/08-01-concept-at-a-glance.ko.png)
*Web Development 101 8장 흐름 개요*

> 배포는 '내 노트북에서는 됩니다'를 '운영 환경에서 반복 가능하게 됩니다'로 바꾸는 단계입니다 — 환경 분리·환경 변수·비밀 관리·빌드 산출물·CI/CD는 모두 같은 코드가 어디서나 똑같이 실행되게 하기 위한 장치입니다.

## 이 글에서 다룰 문제

- 노트북에서만 돌던 앱을 어떻게 운영 환경으로 옮길까요?
- 개발, 스테이징, 운영 환경은 왜 나눌까요?
- 환경 변수와 비밀 값은 왜 저장소 바깥에서 관리할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 배포를 따로 배워야 하는가

수동 배포는 자주 사고를 냅니다. 누가 어느 서버에 어떤 파일을 복사했는지 남지 않고, 테스트를 건너뛰기 쉽고, 롤백도 느립니다. 기능 개발만 보던 팀도 배포 자동화를 시작하면 속도와 안정성이 함께 달라집니다.

## 배포 파이프라인 구조

```
개발자 로컬
    |
    | git push
    v
GitHub Repository
    |
    v  CI (GitHub Actions, GitLab CI, ...)
    ├─ 코드 체크아웃
    ├─ 의존성 설치
    ├─ 테스트 실행
    ├─ Docker 이미지 빌드
    └─ 이미지 레지스트리 푸시 (ghcr.io, ECR, ...)
    |
    v  CD (Continuous Deployment)
    ├─ 스테이징 환경 배포 → 검증
    └─ 운영 환경 배포 → 헬스 체크 → (실패 시 롤백)
```

## 환경 분리

```
환경         용도                     특징
──────────────────────────────────────────────────────────
local        개발자 노트북            디버그 모드, 로컬 DB
development  팀 공유 개발 서버        실제 외부 서비스 연결 X
staging      운영과 동일한 설정       운영 배포 전 최종 검증
production   실제 사용자 서비스       모니터링, 알림 활성화
```

같은 코드가 환경마다 다르게 동작하는 이유는 설정이 다르기 때문입니다. 설정을 환경 변수로 분리하면 코드는 환경을 모릅니다.

## 환경 변수 관리

```python
# 절대 이렇게 하지 말 것: 코드에 비밀 값 하드코딩
DATABASE_URL = "postgresql://user:secret123@prod-db:5432/myapp"
SECRET_KEY = "my-secret-key-12345"

# 올바른 방법: 환경 변수로 읽기
import os

DATABASE_URL = os.environ["DATABASE_URL"]            # 없으면 즉시 오류
SECRET_KEY = os.environ.get("SECRET_KEY")            # 없으면 None
DEBUG = os.environ.get("DEBUG", "false") == "true"  # 기본값 제공
PORT = int(os.environ.get("PORT", "8000"))
```

```bash
# 로컬 개발: .env 파일 (저장소에 절대 커밋 금지)
# .env
DATABASE_URL=sqlite:///local.db
SECRET_KEY=dev-only-secret
DEBUG=true

# .gitignore에 반드시 추가
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

```python
# python-dotenv로 .env 파일 로드
from dotenv import load_dotenv
load_dotenv()

import os
db_url = os.environ["DATABASE_URL"]
```

## 의존성 버전 고정

```text
# requirements.txt (버전 고정)
flask==3.0.3
gunicorn==22.0.0
SQLAlchemy==2.0.30
python-dotenv==1.0.1
bcrypt==4.1.3
PyJWT==2.8.0
```

의존성 버전이 흔들리면 같은 코드도 환경마다 다르게 동작할 수 있습니다. 재현 가능한 배포의 출발점은 버전 고정입니다.

```bash
# 현재 환경의 패키지 버전을 requirements.txt로 고정
pip freeze > requirements.txt

# 버전 고정된 환경 재현
pip install -r requirements.txt
```

## Dockerfile: 불변 산출물 만들기

```dockerfile
# 기반 이미지: 특정 버전 고정
FROM python:3.12-slim

# 작업 디렉토리
WORKDIR /app

# 의존성 먼저 (Docker 레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY . .

# 환경 변수 기본값 (운영에서는 외부에서 오버라이드)
ENV PORT=8000

# 비루트 사용자로 실행 (보안)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# 실행 명령
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} app:app"]
```

```bash
# 이미지 빌드
docker build -t myapp:1.0.0 .

# 로컬 실행 (환경 변수 주입)
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///app.db \
  -e SECRET_KEY=dev-secret \
  myapp:1.0.0

# 헬스 체크
curl http://localhost:8000/health
```

## GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ -v --tb=short

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to server
        run: |
          # 예: SSH로 서버에서 새 이미지 pull 및 재시작
          echo "Deploying ${{ github.sha }}"
```

## 헬스 체크 엔드포인트

```python
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    """배포 시스템이 앱 상태를 판단하는 엔드포인트"""
    return jsonify(status="ok"), 200

@app.get("/ready")
def ready():
    """DB 연결 등 의존성 확인"""
    try:
        # DB 연결 확인
        con = sqlite3.connect(os.environ.get("DB_PATH", "app.db"))
        con.execute("SELECT 1").fetchone()
        con.close()
        return jsonify(status="ready", db="ok"), 200
    except Exception as e:
        return jsonify(status="not ready", db=str(e)), 503
```

```bash
# 배포 후 확인
curl -f http://your-app.com/health || echo "배포 실패"
curl http://your-app.com/ready
```

헬스 체크는 가볍고 빠르게 끝나야 합니다. 무거운 연산을 넣으면 정상 인스턴스도 unhealthy로 판단될 수 있습니다.

## PaaS vs IaaS

```
PaaS (Platform as a Service)        IaaS (Infrastructure as a Service)
────────────────────────────────────────────────────────────────────────
Render, Fly.io, Heroku, Vercel      AWS EC2, GCP Compute, DigitalOcean

코드 push → 자동 빌드/배포          VM 설정, OS 관리, 서버 설치 직접

운영 부담: 낮음                      운영 부담: 높음
유연성: 낮음                         유연성: 높음
비용: 소규모에서 저렴                비용: 대규모에서 저렴

시작 권장: PaaS로 시작, 필요 시 IaaS로 이동
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| 비밀 값을 저장소에 커밋 | GitHub에 공개되면 즉시 유출 | 환경 변수, GitHub Secrets 사용 |
| 환경마다 다른 Dockerfile/빌드 | 스테이징 통과해도 운영에서 실패 | 같은 이미지를 여러 환경에서 승격 |
| 테스트 없는 자동 배포 | 버그 자동 배포 | CI에서 테스트 통과 후 CD 실행 |
| 롤백 계획 없음 | 실패 시 수동 복구로 긴 장애 | 이전 버전 이미지 태그 유지 |
| 무거운 헬스 체크 | 정상 앱도 unhealthy 판정 | /health는 단순 200 반환, /ready에서 DB 확인 |

## 운영에서는 이렇게 보입니다

많은 팀은 초기에 PaaS에서 시작합니다. 운영 부담이 작고 배포 속도가 빠르기 때문입니다. 규모가 커지면 Kubernetes 같은 도구로 넘어가기도 하지만, 여전히 환경 변수, 불변 이미지, 자동화 파이프라인, 모니터링이라는 뼈대는 바뀌지 않습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 빌드는 항상 재현 가능해야 합니다.
- 비밀 값은 secret store에만 둡니다.
- blue/green이나 canary로 배포 리스크를 나눕니다.
- 모든 배포에는 빠른 rollback 경로가 있어야 합니다.
- 배포와 모니터링은 항상 같이 갑니다.

## 운영 체크리스트

- [ ] 설정이 환경 변수로 분리되어 있습니다.
- [ ] merge마다 CI가 테스트를 실행합니다.
- [ ] 하나의 Docker 이미지가 여러 환경에서 재사용됩니다.
- [ ] 배포 후 헬스 체크를 실행합니다.
- [ ] 한 번의 명령으로 rollback할 수 있습니다.

## 연습 문제

1. 작은 Flask 앱에 Dockerfile을 추가하고 로컬 컨테이너로 실행해 보세요.
2. GitHub Actions로 `push → test → build` 워크플로를 연결해 보세요.
3. PaaS 하나를 골라 hello world를 배포하고 health-check URL을 확인해 보세요.

## 정리와 다음 글

배포는 코드 복사 기술이 아니라 재현 가능한 습관입니다. 환경을 나누고, 같은 산출물을 만들고, 자동화와 헬스 체크를 붙여야 운영이 안정됩니다. 다음 글에서는 배포된 앱이 느릴 때 어디부터 봐야 하는지 성능과 캐싱을 다루겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- **Web Development 101 (8/10): 배포 (현재 글)**
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [The Twelve-Factor App](https://12factor.net/)
- [Docker Get Started](https://docs.docker.com/get-started/)
- [GitHub Actions Quickstart](https://docs.github.com/en/actions/writing-workflows/quickstart)

### 실전 체크 포인트
- [Deploying Flask with Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/)
- [Health checks for containers (Docker docs)](https://docs.docker.com/reference/dockerfile/#healthcheck)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Deployment, DevOps, CICD, Hosting
