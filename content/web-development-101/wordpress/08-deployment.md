---
series: web-development-101
episode: 8
title: "바이브코딩을 위한 웹 개발 기초 (8/10): 배포"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - 배포
  - DevOps
  - CICD
  - 호스팅
seo_description: 바이브코딩으로 만든 웹앱을 안전하게 배포하는 방법과 환경 관리의 기초를 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (8/10): 배포

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 여덟 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

바이브코딩으로 만든 앱이 내 컴퓨터에서는 잘 돌아가는데, 서버에 올리면 안 되는 경우가 있습니다. 데이터베이스 연결 주소가 `localhost`로 하드코딩되어 있거나, 비밀 키가 코드 안에 있거나, 의존성 버전이 맞지 않거나 하는 문제들입니다. 이 모든 것은 배포의 기본을 모르기 때문에 생깁니다.

배포는 코드를 복사하는 작업이 아닙니다. 같은 코드가 어디서나 똑같이 실행되게 만드는 일입니다. 환경 변수, 의존성 관리, 컨테이너, 헬스 체크가 모두 이 목표를 위한 도구들입니다. 바이브코딩으로 빠르게 앱을 만들더라도, 배포를 제대로 하지 않으면 비밀 키가 GitHub에 올라가거나, 운영 서버가 갑자기 멈추는 상황이 생깁니다.

이 글에서는 환경 분리, 환경 변수와 비밀 관리, 불변 산출물, 헬스 체크, CI/CD의 기본을 바이브코딩 관점에서 정리합니다.

> 배포는 "내 노트북에서는 됩니다"를 "운영 환경에서 반복 가능하게 됩니다"로 바꾸는 단계입니다. 바이브코딩으로 만든 앱도 이 기준을 충족해야 실제 서비스가 됩니다.

## 이 글에서 다룰 문제

- 로컬에서만 돌던 앱을 어떻게 운영 환경으로 옮길까요?
- 개발, 스테이징, 운영 환경은 왜 나눌까요?
- 환경 변수와 비밀 값은 왜 코드 바깥에서 관리할까요?
- Docker와 컨테이너는 어떤 문제를 해결하나요?
- CI/CD는 무엇이고 왜 중요한가요?

## 바이브코딩 관점: 배포를 알아야 하는 이유

AI에게 "앱 만들어줘"라고 하면 코드가 나오지만, 배포까지 다루는 경우는 드뭅니다. 그래서 바이브코딩으로 만든 앱에서 자주 보이는 패턴이 있습니다.

```python
# AI가 생성한 코드에서 자주 보이는 위험한 패턴
DATABASE_URL = "postgresql://admin:mypassword@localhost/mydb"
SECRET_KEY = "my-super-secret-key-1234"
```

이 코드를 GitHub에 올리면 비밀번호와 시크릿 키가 공개됩니다. 배포의 기본인 "비밀 값은 코드 밖에서 관리한다"는 원칙을 알면, AI에게 처음부터 "민감한 값은 환경 변수로 읽도록 만들어줘"라고 요청할 수 있습니다.

## 먼저 알아둘 용어

- **Environment**: 같은 코드에 서로 다른 설정을 주는 실행 환경입니다.
- **Build artifact**: 빌드 결과물입니다. 컨테이너 이미지가 대표적입니다.
- **PaaS**: 운영 부담을 줄인 플랫폼입니다. Render, Fly.io, Vercel 등이 있습니다.
- **IaaS**: VM처럼 사용자가 더 많은 운영 책임을 지는 인프라입니다.
- **CI/CD**: push 이후 build, test, deploy를 자동화한 흐름입니다.

## Before / After: 배포 방식의 차이

**Before — SSH로 파일 복사 (수동 배포)**

```bash
scp -r ./app user@server:/var/www/
# 매번 결과가 달라질 수 있고, 기록도 남지 않습니다
```

**After — CI/CD 자동화**

```yaml
# .github/workflows/deploy.yml
on: { push: { branches: [main] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest
      - run: ./deploy.sh
```

자동화된 파이프라인은 같은 절차를 항상 동일하게 실행합니다.

## 배포를 다섯 단계로 구성하기

### 1단계 — 설정을 환경 변수로 분리

```python
import os
DB_URL = os.environ["DATABASE_URL"]  # 코드에 직접 쓰지 않음
DEBUG = os.environ.get("DEBUG", "0") == "1"
SECRET_KEY = os.environ["SECRET_KEY"]
```

비밀 값과 환경별 설정은 절대 코드에 하드코딩하지 않습니다.

### 2단계 — 의존성 버전 고정

```text
# requirements.txt
flask==3.0.3
gunicorn==22.0.0
```

버전이 흔들리면 같은 코드도 환경마다 다르게 동작할 수 있습니다.

### 3단계 — Dockerfile 작성

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

### 4단계 — PaaS에 배포하기

```bash
# Fly.io
fly launch
fly deploy

# 또는 Render: GitHub 연결 후 자동 배포 설정
```

### 5단계 — 헬스 체크 엔드포인트

```python
@app.get("/health")
def health():
    return {"status": "ok"}, 200
```

배포 시스템이 이 엔드포인트를 호출해 앱이 정상인지 확인합니다.

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| 비밀 값을 코드에 하드코딩 | 배포 개념 부재 | 환경 변수로 분리, `.env` 파일은 `.gitignore`에 |
| `localhost`를 운영 URL로 사용 | 환경 분리 미숙 | 환경별 URL을 환경 변수로 주입 |
| GitHub에 비밀 키 커밋 | 습관 부재 | `.gitignore`에 `.env` 추가 필수 |
| 테스트 없는 자동 배포 | CI 개념 부재 | push 전 테스트 실행 파이프라인 구성 |
| 헬스 체크 없는 배포 | 운영 개념 부재 | `/health` 엔드포인트로 배포 성공 확인 |

## AI 팁: 배포 준비된 코드 요청 방법

```
"다음 배포 요구사항을 충족하는 앱을 만들어줘:
1. 데이터베이스 URL, 시크릿 키 등 민감한 값은 os.environ으로 읽기
2. requirements.txt에 정확한 버전 명시
3. /health 엔드포인트 포함
4. .env.example 파일 생성 (실제 값 없이 키 이름만)
5. .gitignore에 .env 포함"
```

## 체크리스트

- [ ] 설정이 환경 변수로 분리되어 있습니다.
- [ ] 비밀 값이 코드 저장소에 없습니다.
- [ ] `/health` 엔드포인트가 있습니다.
- [ ] 의존성 버전이 고정되어 있습니다.
- [ ] Docker로 컨테이너 실행이 가능합니다.

## 처음 질문으로 돌아가기

- **로컬에서만 돌던 앱을 어떻게 운영 환경으로 옮길까요?**
  환경 변수로 설정을 분리하고, Docker로 실행 환경을 고정하면 로컬과 서버에서 동일하게 동작합니다.

- **환경 변수와 비밀 값은 왜 코드 바깥에서 관리할까요?**
  코드는 GitHub에 올라가지만, 비밀 값은 팀 외부에 노출되면 안 되기 때문입니다. 환경 변수로 분리하면 코드를 공개해도 비밀이 보호됩니다.

- **Docker는 어떤 문제를 해결하나요?**
  "내 컴퓨터에서는 되는데 서버에서는 안 된다"는 문제를 해결합니다. 실행 환경 자체를 컨테이너로 고정하면 어디서나 동일하게 동작합니다.

## 정리

배포는 바이브코딩 후 실제 서비스로 가는 마지막 단계입니다. 비밀 값 관리, 환경 분리, 헬스 체크는 처음부터 습관으로 잡아야 나중에 사고를 막을 수 있습니다. AI에게 배포 준비된 코드를 요청하는 방법을 알면, 만들어진 앱이 처음부터 운영 환경을 고려한 구조를 갖게 됩니다. 다음 글에서는 배포된 앱이 느릴 때 어디서부터 볼지 성능과 캐싱을 다룹니다.

## 참고 자료

- [The Twelve-Factor App](https://12factor.net/)
- [Docker Get Started](https://docs.docker.com/get-started/)
- [GitHub Actions Quickstart](https://docs.github.com/en/actions/writing-workflows/quickstart)
- [Deploying Flask with Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- **바이브코딩을 위한 웹 개발 기초 (8/10): 배포 (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, 배포, DevOps, CICD, 호스팅
