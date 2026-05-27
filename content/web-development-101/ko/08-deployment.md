---
series: web-development-101
episode: 8
title: "Web Development 101 (8/10): 배포"
status: publish-ready
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

## 먼저 던지는 질문

- 노트북에서만 돌던 앱을 어떻게 운영 환경으로 옮길까요?
- 개발, 스테이징, 운영 환경은 왜 나눌까요?
- 환경 변수와 비밀 값은 왜 저장소 바깥에서 관리할까요?

## 왜 배포를 따로 배워야 하는가

수동 배포는 자주 사고를 냅니다. 누가 어느 서버에 어떤 파일을 복사했는지 남지 않고, 테스트를 건너뛰기 쉽고, 롤백도 느립니다. 기능 개발만 보던 팀도 배포 자동화를 시작하면 속도와 안정성이 함께 달라집니다.

이 흐름을 한 번 익혀 두면 플랫폼이 바뀌어도 적응이 빠릅니다. Render, Fly.io, Vercel, Kubernetes처럼 도구는 달라져도 환경 분리, 불변 산출물, 자동화된 배포, 헬스 체크라는 기본 뼈대는 거의 같습니다.

## 한눈에 보는 개념 지도

배포 그림에서 가장 중요한 원칙은 같은 산출물을 여러 환경으로 승격시키는 것입니다. 환경마다 코드를 다시 빌드하면 같은 커밋이 다른 결과를 낼 수 있어 사고 원인 추적이 어려워집니다.

### 직접 검증해 볼 포인트

- 환경 변수 없이 실행했을 때 앱이 어떤 설정 값을 요구하는지 확인합니다.
- `docker build` 뒤 같은 이미지로 로컬과 스테이징 설정만 바꿔 실행합니다.
- `/health` 엔드포인트가 200을 돌려주는지 배포 직후 `curl`로 확인합니다.

**기대 결과:** 설정은 환경 변수에서만 달라지고, 동일한 이미지가 여러 환경에서 재사용되며, 헬스 체크는 배포 성공 여부를 빠르게 알려 줍니다.

**실패 모드:** 환경마다 다른 빌드를 만들면 재현성이 깨집니다. 롤백 경로가 없으면 작은 배포 실패가 긴 장애로 바뀝니다.

## 먼저 알아둘 용어

- **Environment**: 같은 코드에 서로 다른 설정을 주는 실행 환경입니다.
- **Build artifact**: 빌드 결과물입니다. 파일 묶음이나 컨테이너 이미지가 여기에 해당합니다.
- **PaaS**: 운영 부담을 많이 감춘 플랫폼입니다.
- **IaaS**: VM처럼 사용자가 더 많은 운영 책임을 지는 인프라입니다.
- **CI/CD**: push 이후 build, test, deploy를 자동화한 흐름입니다.

## 전후 비교로 보는 배포 방식

**Before (SSH and copy)**

```bash
scp -r ./app user@server:/var/www/  # 매번 결과가 달라질 수 있습니다
```

**After (CI builds and deploys)**

```yaml
# .github/workflows/deploy.yml (gist)
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

자동화된 파이프라인은 같은 입력에서 같은 결과를 반복해서 만들게 해 줍니다. 배포가 사람 손기술에서 시스템 절차로 바뀝니다.

## 작은 앱을 다섯 단계로 배포해 보기

### 1단계 — 설정을 환경 변수로 옮기기

```python
# app.py
import os
DB_URL = os.environ["DATABASE_URL"]
DEBUG = os.environ.get("DEBUG", "0") == "1"
```

비밀 값과 환경별 설정은 코드에 박아 두지 않습니다. 코드 저장소에 들어가면 관리와 회수가 어려워집니다.

### 2단계 — 의존성 버전 고정하기

```text
# requirements.txt
flask==3.0.3
gunicorn==22.0.0
```

의존성 버전이 흔들리면 같은 코드도 환경마다 다르게 동작할 수 있습니다. 재현 가능한 배포의 출발점은 버전 고정입니다.

### 3단계 — Dockerfile로 산출물 만들기

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

컨테이너 이미지는 불변 산출물 역할을 합니다. 한 번 빌드한 이미지를 여러 환경에 같은 방식으로 올릴 수 있습니다.

### 4단계 — PaaS에 올리기

```bash
# Fly.io
fly launch     # once
fly deploy     # every release
```

Render 같은 PaaS는 저장소를 연결하면 push마다 자동 배포를 수행하기도 합니다. 처음에는 이런 관리형 플랫폼이 진입 장벽을 크게 낮춰 줍니다.

### 5단계 — 헬스 체크와 롤백 준비하기

```python
@app.get("/health")
def health(): return {"status": "ok"}, 200
```

헬스 체크는 배포 이후 앱이 정상인지 판단하는 가장 단순한 신호입니다. 많은 PaaS가 이 엔드포인트를 보고 자동 롤백 여부를 결정합니다.

## 이 코드에서 먼저 봐야 할 점

- 환경 변수는 코드 밖에서 주입됩니다.
- 스테이징과 운영은 같은 이미지를 승격시키는 방식이 좋습니다.
- 헬스 체크는 가볍고 빠르게 끝나야 의미가 있습니다.

## 여기서 자주 헷갈립니다

1. **비밀 값을 저장소에 커밋하는 경우**: 한 번 유출되면 회수가 어렵습니다.
2. **환경마다 다른 빌드를 만드는 경우**: 재현성이 사라집니다.
3. **테스트 없는 자동 배포를 붙이는 경우**: CI/CD가 사고 자동화가 됩니다.
4. **롤백 계획이 없는 경우**: 작은 배포 실패가 긴 장애로 이어집니다.
5. **무거운 헬스 체크를 두는 경우**: 정상 인스턴스도 unhealthy로 보일 수 있습니다.

## 운영에서는 이렇게 보입니다

많은 팀은 초기에 PaaS에서 시작합니다. 운영 부담이 작고 배포 속도가 빠르기 때문입니다. 규모가 커지면 Kubernetes 같은 도구로 넘어가기도 하지만, 여전히 환경 변수, 불변 이미지, 자동화 파이프라인, 모니터링이라는 뼈대는 바뀌지 않습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 빌드는 항상 재현 가능해야 합니다.
- 비밀 값은 secret store에만 둡니다.
- blue/green이나 canary로 배포 리스크를 나눕니다.
- 모든 배포에는 빠른 rollback 경로가 있어야 합니다.
- 배포와 모니터링은 항상 같이 갑니다.

## 체크리스트

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

## HTTP-인증-배포를 함께 검증하는 점검 루틴

웹 서비스는 단일 기능이 아니라 경로 전체의 안정성으로 평가됩니다. 따라서 API 스펙, 인증 예외, 배포 헬스체크를 같은 릴리스 체크리스트로 묶는 편이 안전합니다.

```text
배포 전 점검
1) 핵심 API 3개에 대해 상태 코드/응답 스키마 계약 테스트 실행
2) access 만료, refresh 만료, revoke 토큰 시나리오 재현
3) /health, /ready 엔드포인트를 배포 환경에서 실제 호출
4) CDN/브라우저 캐시 무효화 정책 확인
```

### 장애 예방을 위한 최소 헤더 정책

```http
Cache-Control: no-store
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

헤더 정책은 프론트엔드 코드 변경 없이도 보안/캐시 동작을 크게 바꿉니다. 기능 개발과 별개로 표준 헤더를 고정해 두면 릴리스 변동성이 줄어듭니다.

### 배포 후 15분 관찰 항목

- 5xx 비율과 p95 지연 시간의 급격한 상승 여부
- 로그인 성공률, 토큰 재발급 성공률
- 정적 자산 404 발생률

이 루틴을 반복하면 "배포는 되었지만 정상 운영은 아닌" 상태를 초기에 감지할 수 있습니다.

## 실무 적용 메모

아래 항목은 실제 팀 운영에서 즉시 적용 가능한 최소 기준입니다.

- 요구사항 ID를 브랜치 이름과 PR 제목에 포함해 추적성을 높입니다.
- 코드 리뷰에서 "변경 위험" 항목을 별도로 두고, 장애 반경을 한 줄로 남깁니다.
- 테스트 결과는 성공 여부만 기록하지 않고 실패 시 복구 절차 링크를 같이 둡니다.
- 배포 후 모니터링 대시보드 URL을 릴리스 노트에 고정합니다.

작은 기록 규칙이 누적되면 협업 비용이 줄고, 동일한 문제를 반복해서 조사하는 시간을 크게 줄일 수 있습니다.

## 실전 앵커 모음: 배포 안정성을 운영 문서로 바꾸기

작은 기능이라도 운영 단계까지 생각하면 문서화 기준이 달라집니다. 아래 예시는 팀이 기능 구현과 동시에 남겨 두면 바로 도움이 되는 최소 산출물입니다. 특히 요청/응답 계약, 세션/쿠키 정책, SQL 기준 쿼리, 배포 설정, 캐시 규칙을 함께 기록하면 변경 시점의 실패 반경을 크게 줄일 수 있습니다.

### HTTP 요청/응답 계약 예시

```http
GET /api/v1/todos?limit=20&cursor=todo_120 HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer <access_token>
X-Request-Id: req-2026-05-21-0001
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, max-age=30
ETag: "todo-list-v42"

{
  "items": [
    {"id": "todo_121", "text": "문서 작성", "done": false},
    {"id": "todo_122", "text": "테스트 실행", "done": true}
  ],
  "next_cursor": "todo_122"
}
```

응답 예시는 상태 코드만 맞추는 수준에서 끝내지 말고, 캐시 정책과 추적 ID를 함께 포함하는 편이 좋습니다. 특히 `X-Request-Id`를 표준화하면 장애 시점에 브라우저 로그와 서버 로그를 빠르게 결합할 수 있습니다.

### REST API 설계 스케치

```text
GET    /api/v1/todos            목록 조회
POST   /api/v1/todos            항목 생성
PATCH  /api/v1/todos/{id}       항목 일부 수정(done 토글 등)
DELETE /api/v1/todos/{id}       항목 삭제
```

리소스 이름은 복수형으로 고정하고, 동작은 method로 분리하는 편이 유지보수에 유리합니다. 예를 들어 `/toggleTodo`처럼 동사형 엔드포인트를 늘리기 시작하면 권한 정책과 감사 로그 규칙이 빠르게 파편화됩니다.

### 세션/쿠키 정책 코드 예시

```python
from flask import Flask, session, jsonify

app = Flask(__name__)
app.secret_key = "change-me"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

@app.get("/api/v1/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error={"code": "UNAUTHORIZED"}), 401
    return jsonify(user_id=user_id)
```

인증은 로그인 성공 시점보다 실패 시점 설계가 더 중요합니다. 어떤 경우에 401을 돌리고, 어떤 경우에 403을 돌릴지 미리 고정해 두어야 프론트엔드 재시도 정책과 알림 문구가 안정됩니다.

### SQL 기준 쿼리와 인덱스 예시

```sql
CREATE TABLE IF NOT EXISTS todo_items (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  text TEXT NOT NULL,
  done INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_todo_user_created
ON todo_items(user_id, created_at DESC);

SELECT id, text, done, created_at
FROM todo_items
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 20;
```

조회 패턴을 먼저 적고 그다음 인덱스를 정의하면 불필요한 인덱스 폭증을 피할 수 있습니다. 특히 쓰기 비중이 높은 서비스에서는 인덱스를 한 개 추가할 때마다 INSERT 비용이 늘어난다는 점을 함께 기록해야 합니다.

### 배포 설정과 헬스 체크 예시

```yaml
services:
  api:
    image: ghcr.io/example/todo-api:1.0.0
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://app:***@db:5432/todo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

배포 문서에는 반드시 "성공 기준"을 남겨야 합니다. 예를 들어 `/health`가 200을 반환하고, 배포 후 15분 동안 5xx 비율이 1% 미만이며, 로그인 성공률이 평시 대비 하락하지 않는지를 체크리스트로 고정하면 릴리스 판단이 사람마다 달라지지 않습니다.

### 캐시 전략 표준 예시

```http
Cache-Control: public, max-age=31536000, immutable
```

정적 자산은 파일명에 해시를 넣고 장기 캐시를 적용하는 편이 안전합니다. 반대로 사용자별 데이터는 `private` 또는 `no-store` 정책을 명시해 캐시 오염을 방지해야 합니다. 이 구분을 코드 리뷰 항목으로 올려 두면 보안 이슈와 성능 이슈를 동시에 예방할 수 있습니다.

### 운영 체크리스트

- 요청/응답 샘플에 상태 코드, 헤더, 오류 본문 형식을 모두 기록합니다.
- 인증 실패(401), 권한 실패(403), 입력 오류(400) 경계를 API 문서에 고정합니다.
- 핵심 SQL 쿼리 3개를 선정해 `EXPLAIN` 결과를 릴리스마다 비교합니다.
- 배포 후 15분 관측 지표(5xx, p95, 로그인 성공률)를 팀 표준으로 유지합니다.
- 캐시 정책 변경 시 무효화 전략과 롤백 절차를 같은 PR에 포함합니다.

## 처음 질문으로 돌아가기

- **노트북에서만 돌던 앱을 어떻게 운영 환경으로 옮길까요?**
  - 먼저 `DATABASE_URL` 같은 설정을 환경 변수로 분리하고, `requirements.txt`로 의존성을 고정한 뒤, Dockerfile로 `gunicorn` 실행 이미지를 만듭니다. 그다음 PaaS나 CI/CD에서 같은 산출물을 배포하고 `/health` 엔드포인트로 실제 기동 여부를 확인하는 흐름으로 운영 환경에 올립니다.
- **개발, 스테이징, 운영 환경은 왜 나눌까요?**
  - 환경을 나누면 코드는 그대로 두고 설정만 바꿔 위험을 낮춘 상태로 검증 단계를 거칠 수 있습니다. 글에서 강조한 것처럼 같은 이미지를 스테이징과 운영으로 승격시키면, 환경마다 다시 빌드해서 생기는 재현성 문제와 원인 추적 어려움을 줄일 수 있습니다.
- **환경 변수와 비밀 값은 왜 저장소 바깥에서 관리할까요?**
  - `DB_URL = os.environ["DATABASE_URL"]`처럼 코드는 값을 참조만 하고 실제 비밀은 외부에서 주입해야 유출 시 회수와 교체가 가능합니다. 저장소에 비밀번호나 토큰을 커밋하면 환경 교체도 어려워지고, 한 번 노출된 비밀을 되돌리기 힘들어집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- **배포 (현재 글)**
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

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
