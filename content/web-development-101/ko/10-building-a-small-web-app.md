---
series: web-development-101
episode: 10
title: "Web Development 101 (10/10): 작은 웹앱 만들기"
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
  - Capstone
  - Flask
  - FullStack
  - Project
seo_description: Flask, HTML, SQLite, 배포를 묶어 작은 Todo 앱을 만드는 글입니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (10/10): 작은 웹앱 만들기

이 글은 Web Development 101 시리즈의 마지막 글입니다.

시리즈를 따라오며 웹의 흐름, 브라우저, HTTP, Frontend와 Backend, 인증, 데이터베이스, 배포, 성능까지 각각 따로 보았습니다. 이제는 이 조각들을 하나의 앱 안에 묶어 볼 차례입니다. 지식은 작은 결과물을 직접 만들어 볼 때 비로소 자기 것이 됩니다.

여기서는 Todo 앱 하나를 만들면서 HTML, Flask, SQLite, 환경 변수, 헬스 체크, 컨테이너 실행까지 한 흐름으로 연결하겠습니다.

## 먼저 던지는 질문

- 앞선 아홉 개 개념은 한 앱 안에서 어떻게 연결될까요?
- 작은 풀스택 프로젝트는 어떤 폴더 구조로 시작하면 좋을까요?
- Frontend, Backend, 데이터베이스는 어떤 API 계약으로 묶일까요?

## 큰 그림

![Web Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/10/10-01-concept-at-a-glance.ko.png)

*Web Development 101 10장 흐름 개요*

## 왜 마지막 글이 중요한가

개념을 따로 아는 것과 하나의 제품 흐름으로 엮어 보는 것은 다릅니다. 작은 Todo 앱이라도 직접 만들어 보면 URL 요청, HTML 렌더링, API 호출, 데이터베이스 쓰기, 환경 변수, 배포 헬스 체크가 한 선으로 이어집니다. 이 연결 경험이 있어야 다음 프로젝트에서도 어디서부터 시작할지 감이 생깁니다.

또한 작은 앱은 전체 흐름을 빠르게 반복하게 해 줍니다. 큰 프레임워크부터 잡는 것보다, 작지만 끝까지 가는 앱을 먼저 만드는 편이 훨씬 강한 학습이 됩니다.

## 한눈에 보는 개념 지도

이 마지막 그림은 시리즈에서 배운 개념이 하나의 수직 슬라이스로 만나는 장면입니다. 사용자가 폼을 제출하면 브라우저가 API를 호출하고, 서버는 데이터베이스를 갱신한 뒤 다시 화면이 읽을 수 있는 JSON을 돌려줍니다.

### 직접 검증해 볼 포인트

- `curl`로 Todo를 추가한 뒤 브라우저 새로고침 없이 목록이 다시 그려지는지 확인합니다.
- 앱을 컨테이너로 실행하고 `/health`가 정상 응답하는지 확인합니다.
- `DB_PATH` 값을 바꿔도 코드 수정 없이 다른 데이터 파일을 가리키는지 검증합니다.

**기대 결과:** API와 HTML 화면이 같은 데이터 원본을 공유하고, 환경 변수만 바꿔도 저장 위치가 달라지며, 컨테이너 안에서도 동일한 동작이 재현됩니다.

**실패 모드:** 상태 코드를 제대로 나누지 않으면 Frontend가 실패를 감지하기 어렵습니다. 데이터 경로를 하드코딩하면 로컬과 배포 환경을 같은 코드로 운영하기 어렵습니다.

## 먼저 알아둘 용어

- **Capstone**: 시리즈를 마무리하는 통합 프로젝트입니다.
- **Full-stack**: Frontend, Backend, Database, Deployment가 함께 있는 구조입니다.
- **MVP**: 가장 작은 동작 가능한 제품 조각입니다.
- **Folder layout**: 팀과 공유할 수 있는 프로젝트 구조입니다.
- **Smoke test**: 핵심 경로가 실제로 동작하는지 빠르게 확인하는 최소 검증입니다.

## 전후 비교로 보는 범위 변화

**Before (one-line script)**

```python
print("hello")
```

**After (one app)**

```text
todo-app/
├── app.py
├── templates/index.html
├── static/style.css
├── requirements.txt
└── Dockerfile
```

한 줄 스크립트에서 시작해도, 구조를 잡으면 바로 배포 가능한 작은 앱으로 이어질 수 있습니다.

## Todo 앱을 다섯 단계로 만들기

### 1단계 — 프로젝트 준비

```bash
mkdir todo-app && cd todo-app
python3 -m venv .venv && source .venv/bin/activate
pip install flask gunicorn
```

가상환경을 만들고 필요한 패키지를 설치합니다. 지금은 작아 보여도, 처음부터 프로젝트 경계를 분리해 두는 편이 좋습니다.

### 2단계 — Backend 작성하기 (`app.py`)

```python
from flask import Flask, request, jsonify, render_template
import sqlite3, os

DB = os.environ.get("DB_PATH", "todo.db")
app = Flask(__name__)

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

with conn() as c:
    c.execute("CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY, text TEXT, done INTEGER DEFAULT 0)")

@app.get("/")
def home(): return render_template("index.html")

@app.get("/api/todos")
def list_todos():
    rows = conn().execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/todos")
def add_todo():
    text = request.get_json()["text"]
    with conn() as c:
        c.execute("INSERT INTO todos(text) VALUES (?)", (text,))
    return jsonify(ok=True), 201

@app.get("/health")
def health(): return {"status": "ok"}
```

이 Backend는 세 가지 핵심을 보여 줍니다. 환경 변수 `DB_PATH`, SQLite 저장, 그리고 배포 시스템이 확인할 `/health` 엔드포인트입니다.

### 3단계 — Frontend 작성하기 (`templates/index.html`)

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Todo</title>
  <link rel="stylesheet" href="/static/style.css"></head>
<body>
  <h1>Todo</h1>
  <form id="f"><input id="t" placeholder="what to do"><button>add</button></form>
  <ul id="list"></ul>
<script>
async function load() {
  const items = await (await fetch("/api/todos")).json();
  document.getElementById("list").innerHTML = items.map(i => `<li>${i.text}</li>`).join("");
}
document.getElementById("f").addEventListener("submit", async e => {
  e.preventDefault();
  await fetch("/api/todos", {method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({text: document.getElementById("t").value})});
  document.getElementById("t").value = "";
  load();
});
load();
</script>
</body></html>
```

이 Frontend는 `/api/todos`를 호출해 목록을 그리고, 폼 제출 시 새 할 일을 추가합니다. 아주 작은 예제지만 DOM, fetch, JSON API 계약이 모두 들어 있습니다.

### 4단계 — Smoke test 하기

```bash
flask --app app run
# in another terminal
curl -X POST -H "Content-Type: application/json" -d '{"text":"first todo"}' http://localhost:5000/api/todos
curl http://localhost:5000/api/todos
```

브라우저만 믿지 말고 `curl`로 핵심 API가 실제로 동작하는지 확인합니다. 작은 앱일수록 이런 기본 검증이 더 중요합니다.

### 5단계 — Docker로 감싸고 실행하기

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV DB_PATH=/data/todo.db
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

```bash
docker build -t todo-app . && docker run -p 8000:8000 -v $PWD/data:/data todo-app
```

컨테이너로 감싸면 로컬 실행과 배포 실행의 차이를 줄일 수 있습니다. 환경 변수와 데이터 저장 경로를 분리해 둔 이유도 여기서 빛납니다.

## 이 코드에서 먼저 봐야 할 점

- 같은 환경 변수 `DB_PATH`가 로컬과 컨테이너 실행을 함께 지탱합니다.
- `/health`는 배포 시스템이 앱 상태를 판단할 때 쓰는 기본 신호입니다.
- 이 시리즈의 핵심 개념이 약 100줄 안팎의 코드에 모두 들어 있습니다.

## 여기서 자주 헷갈립니다

1. **DB 경로를 코드에 하드코딩하는 경우**: 환경별 실행 유연성이 떨어집니다.
2. **작은 앱이라며 JavaScript를 계속 한 파일에 몰아넣는 경우**: 규모가 조금만 커져도 읽기 어려워집니다.
3. **오류에도 늘 200을 돌려주는 경우**: 클라이언트가 실패를 구분할 수 없습니다.
4. **테스트 없이 바로 배포하는 경우**: 최소한 health check와 `curl` 검증은 필요합니다.
5. **처음부터 거대한 프레임워크를 붙이는 경우**: 학습 대상이 앱이 아니라 도구가 되어 버립니다.

## 운영에서는 이렇게 보입니다

이 작은 앱은 블로그, 메모 앱, 가계부, 챗봇처럼 다양한 서비스의 출발점이 될 수 있습니다. 큰 SaaS도 구조를 뜯어 보면 결국 여기에서 큐, 캐시, 인증, 배치, 모니터링이 층층이 추가된 형태에 가깝습니다. 작은 수직 슬라이스를 끝까지 만드는 훈련이 중요한 이유가 여기에 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 작은 vertical slice를 끝까지 보냅니다.
- 환경마다 다른 값만 환경 변수로 분리합니다.
- health check, logging, monitoring을 처음부터 염두에 둡니다.
- 기능이 늘어나면 경계를 다시 그립니다.
- 제품이 커질수록 코드보다 팀 합의가 더 중요해진다고 봅니다.

## 체크리스트

- [ ] Frontend, Backend, Database가 한 앱 안에 모두 있습니다.
- [ ] health check 엔드포인트가 있습니다.
- [ ] 설정이 환경 변수로 분리되어 있습니다.
- [ ] `curl`로 엔드포인트를 직접 호출해 봤습니다.
- [ ] 컨테이너로 실행해 봤습니다.

## 연습 문제

1. Todo 앱에 `toggle done`과 `delete` 기능을 추가해 보세요.
2. 세션 로그인을 붙여 사용자별 Todo를 분리해 보세요.
3. 정적 자산에 캐시 헤더를 붙이고 Lighthouse를 실행해 보세요.

## 정리와 다음 단계

이것으로 Web Development 101 시리즈를 마칩니다. 작은 앱 하나를 처음부터 끝까지 만들어 보면서 웹의 기본 층을 모두 한 번 연결했습니다. 다음 단계는 깊이입니다. Frontend Development 101, Backend Development 101, Database 101 같은 후속 시리즈로 한 층씩 더 깊게 들어갈 수 있습니다. 하지만 가장 좋은 다음 책은 새 앱 하나를 직접 더 만드는 일입니다.

## 웹 서비스 품질을 높이는 추가 실전 예시

웹 개발에서는 기능 구현 속도만큼 프로토콜 이해와 운영 경계 관리가 중요합니다. 특히 HTTP 메시지 설계, 인증 흐름, 배포 구성은 기능이 늘어날수록 장애 확률과 직접 연결됩니다. 아래 예시는 실제 프로젝트에서 반복해서 쓰이는 기본 패턴입니다.

### HTTP 요청/응답 설계 예시

```http
POST /api/v1/orders HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer <access_token>
Idempotency-Key: 9a7d2f4a-31a2-4b11-9cd8-3e2f4dcf1b20

{
  "items": [{"sku": "A-100", "qty": 2}],
  "payment_method": "card"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/orders/ord_1024

{
  "order_id": "ord_1024",
  "status": "created"
}
```

여기서 `Idempotency-Key`는 네트워크 재시도로 인한 중복 결제를 막는 핵심 장치입니다. 웹 API는 "한 번 보냈다"가 아니라 "여러 번 도착할 수 있다"를 기본 가정으로 설계해야 합니다.

### 인증 흐름: Access + Refresh 토큰 분리

```text
1) 사용자가 로그인하면 서버가 access(짧은 수명) + refresh(긴 수명)를 발급
2) 클라이언트는 access로 API 호출
3) access 만료 시 refresh로 재발급 요청
4) refresh 탈취 위험을 줄이기 위해 회전(rotation)과 폐기(revoke) 정책 적용
```

```python
# pseudo-auth-service.py
from datetime import timedelta

def issue_tokens(user_id: str) -> dict:
    return {
        "access_expires": timedelta(minutes=15),
        "refresh_expires": timedelta(days=14),
        "token_type": "Bearer",
    }
```

브라우저 환경에서는 refresh 토큰을 `HttpOnly`, `Secure`, `SameSite` 정책이 적용된 쿠키로 다루는 방식이 일반적입니다. 인증 실패 응답은 `401`과 명확한 오류 코드를 함께 제공해야 클라이언트 재시도 전략을 안정적으로 구성할 수 있습니다.

### 배포 구성: 앱/프록시/헬스체크 분리

```yaml
# docker-compose.prod.yml
services:
  web:
    image: ghcr.io/example/web:1.4.0
    env_file: .env
    ports: ["8000"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
  nginx:
    image: nginx:1.27
    ports: ["80:80", "443:443"]
    depends_on: [web]
```

헬스체크를 배포 단위에 포함하면 롤링 업데이트 중 비정상 인스턴스를 조기에 제외할 수 있습니다. 프록시 계층에서 TLS 종료와 정적 파일 캐싱을 처리하면 애플리케이션 서버는 비즈니스 로직에 더 집중할 수 있습니다.

### 운영 체크 포인트

- API마다 타임아웃, 재시도, 멱등 처리 기준을 문서화합니다.
- 인증 토큰 만료/재발급 실패 비율을 대시보드로 모니터링합니다.
- 배포 후 15분 동안 5xx 비율, p95, 로그인 성공률을 집중 관찰합니다.
- CORS 정책을 `*`로 열어두지 않고 허용 출처를 명시합니다.

웹 개발의 난이도는 화면 구현보다 경계 관리에서 더 크게 올라갑니다. HTTP 계약, 인증 수명주기, 배포 안전장치를 초기에 고정해 두면 기능 확장 시에도 장애 반경을 작게 유지할 수 있고, 팀 전체의 디버깅 속도도 안정적으로 유지됩니다.

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

## 실전 앵커 모음: 통합 운영을 운영 문서로 바꾸기

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

## 운영 사고를 줄이는 검증 시나리오

기능이 맞는지 확인하는 테스트와 운영 사고를 줄이는 테스트는 관점이 다릅니다. 기능 테스트는 정답 값을 맞추는 데 집중하고, 운영 테스트는 실패했을 때 시스템이 어떻게 무너지는지 확인합니다. 아래 시나리오는 작은 프로젝트에서도 바로 적용 가능한 최소 세트입니다.

### 시나리오 1: 타임아웃과 재시도 경계

```python
import requests

def fetch_with_budget(url: str) -> dict:
    for i in range(3):
        try:
            resp = requests.get(url, timeout=1.5)
            if resp.status_code < 500:
                return {"ok": True, "status": resp.status_code}
        except requests.Timeout:
            pass
    return {"ok": False, "status": 504}
```

재시도는 무조건 많을수록 좋은 정책이 아닙니다. 호출 수가 늘수록 상류 서비스 장애를 하류 서비스로 전염시킬 수 있으므로, 재시도 횟수와 타임아웃 예산을 함께 문서화해야 합니다.

### 시나리오 2: 오류 응답 표준화

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "text 필드는 1자 이상이어야 합니다",
    "request_id": "req-2026-05-21-1042"
  }
}
```

오류 본문이 엔드포인트마다 달라지면 프론트엔드 예외 처리와 운영 알림이 모두 복잡해집니다. 최소한 `code`, `message`, `request_id` 구조를 공통화하면 클라이언트 동작과 대시보드 분류가 안정됩니다.

### 시나리오 3: 읽기/쓰기 경계 쿼리 검증

```sql
-- 읽기 경로
SELECT id, text, done
FROM todo_items
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 20;

-- 쓰기 경로
UPDATE todo_items
SET done = 1
WHERE id = ? AND user_id = ?;
```

읽기와 쓰기 쿼리를 분리해 검토하면 권한 누락 버그를 초기에 찾기 쉽습니다. 특히 `WHERE id = ?`만 쓰고 `user_id`를 빠뜨리는 실수는 실제 서비스에서 매우 자주 발생합니다.

### 시나리오 4: 배포 후 자동 확인 명령

```bash
curl -fsS https://example.com/health
curl -fsS https://example.com/api/v1/todos?limit=1
```

배포 스크립트가 끝났다는 사실과 서비스가 정상이라는 사실은 다릅니다. 최소 두 개의 확인 요청을 자동화하면 "배포 성공"과 "운영 성공"의 간극을 줄일 수 있습니다.

### 시나리오 5: 캐시 무효화 기준

```text
정적 파일: 파일명 해시 변경 시 자동 무효화
API 응답: 데이터 변경 이벤트 발생 시 키 삭제
사용자별 데이터: 공유 캐시 금지(private/no-store)
```

캐시는 성능을 올리지만 잘못 적용하면 데이터 일관성을 깨뜨립니다. 따라서 캐시를 추가할 때는 반드시 "언제 비울지"를 같은 문단에서 정의해야 합니다.

## 처음 질문으로 돌아가기

- **앞선 아홉 개 개념은 한 앱 안에서 어떻게 연결될까요?**
  - 본문의 기준은 작은 웹앱 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **작은 풀스택 프로젝트는 어떤 폴더 구조로 시작하면 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Frontend, Backend, 데이터베이스는 어떤 API 계약으로 묶일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- **작은 웹앱 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [sqlite3 — DB-API 2.0 interface for SQLite databases](https://docs.python.org/3/library/sqlite3.html)
- [Docker Get Started](https://docs.docker.com/get-started/)

### 실전 체크 포인트
- [The Twelve-Factor App](https://12factor.net/)
- [Fetch API 사용법 (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Capstone, Flask, FullStack, Project
