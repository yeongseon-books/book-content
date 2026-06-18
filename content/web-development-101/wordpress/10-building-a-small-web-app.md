---
series: web-development-101
episode: 10
title: "바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - 마무리프로젝트
  - Flask
  - 풀스택
  - 프로젝트
seo_description: 바이브코딩으로 배운 웹 개발 기초를 하나의 Todo 앱으로 통합하는 마지막 글입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 마지막 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

이 시리즈를 따라오며 웹의 흐름, HTML/CSS/JavaScript, 브라우저와 DOM, HTTP와 API, Frontend/Backend, 인증, 데이터베이스, 배포, 성능 각 개념을 하나씩 공부했습니다. 이제는 이 조각들을 하나의 앱 안에서 연결할 차례입니다.

바이브코딩의 진짜 힘은 작동하는 결과를 빠르게 만드는 것입니다. 하지만 "빠르게 만들기"는 "이해 없이 만들기"가 아닙니다. AI가 만들어준 코드에서 "이 부분이 HTTP 요청이구나", "이 코드가 환경 변수를 읽는 거구나", "이 함수가 트랜잭션을 처리하는 거구나"라고 읽힐 때 비로소 진정한 바이브코딩이 가능합니다.

이 마지막 글에서는 Todo 앱 하나를 만들면서 HTML, Flask, SQLite, 환경 변수, 헬스 체크, 컨테이너 실행까지 한 흐름으로 연결합니다. 각 코드 조각이 앞서 배운 개념들과 어떻게 연결되는지 함께 확인합니다.

> 마지막 글은 시리즈의 모든 조각을 하나의 작은 앱 안에서 다시 연결하는 자리입니다. 바이브코딩으로 AI에게 앱을 만들어달라고 하기 전에, 이 구조를 한 번 직접 만들어본 경험이 있는 것과 없는 것은 완전히 다릅니다.

## 이 글에서 다룰 문제

- 앞선 아홉 개 개념은 한 앱 안에서 어떻게 연결될까요?
- 바이브코딩으로 앱을 만들 때 어떤 구조가 좋을까요?
- AI가 만들어준 코드에서 각 개념이 어디에 있는지 어떻게 찾을까요?
- 작은 앱을 직접 만들어보면 무엇을 얻을 수 있을까요?
- 이 시리즈 이후 어떻게 계속 배울 수 있을까요?

## 바이브코딩 관점: 왜 직접 만들어봐야 하는가

AI에게 "Todo 앱 만들어줘"라고 하면 전체 코드가 나옵니다. 그런데 그 코드를 수정하거나 기능을 추가하려면, 어느 파일의 어느 부분을 건드려야 하는지 알아야 합니다. 이 글에서 한 번 직접 만들어보면, 다음에 AI가 비슷한 구조의 코드를 생성했을 때 구조가 눈에 들어오기 시작합니다.

또한 작은 앱에서 생긴 문제(데이터가 저장 안 됨, API가 연결 안 됨, 배포 후 환경 변수 오류)를 직접 해결해보는 경험이, AI에게 문제를 더 정확하게 설명하는 능력을 만들어 줍니다.

## 먼저 알아둘 용어

- **Capstone**: 시리즈를 마무리하는 통합 프로젝트입니다.
- **Full-stack**: Frontend, Backend, Database, Deployment가 함께 있는 구조입니다.
- **MVP**: 가장 작은 동작 가능한 제품 조각입니다.
- **Vertical slice**: 기능 하나를 화면부터 데이터베이스까지 끝까지 연결한 구현입니다.
- **Smoke test**: 핵심 경로가 실제로 동작하는지 빠르게 확인하는 최소 검증입니다.

## Before / After: 범위 변화

**Before — 한 줄 스크립트**

```python
print("안녕하세요")
```

**After — 하나의 완성된 앱**

```text
todo-app/
├── app.py              # Backend (Flask)
├── templates/
│   └── index.html      # Frontend (HTML + JS)
├── static/
│   └── style.css       # 스타일
├── requirements.txt    # 의존성
└── Dockerfile          # 배포 준비
```

구조를 잡으면 작은 앱도 바로 배포 가능한 형태가 됩니다.

## Todo 앱을 다섯 단계로 만들기

### 1단계 — 프로젝트 준비

```bash
mkdir todo-app && cd todo-app
python3 -m venv .venv && source .venv/bin/activate
pip install flask gunicorn
```

### 2단계 — Backend 작성 (app.py)

```python
from flask import Flask, request, jsonify, render_template
import sqlite3, os

# 7편에서 배운 환경 변수 (8편 배포 원칙)
DB = os.environ.get("DB_PATH", "todo.db")
app = Flask(__name__)

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

# 7편: 데이터베이스 초기화
with conn() as c:
    c.execute("""
        CREATE TABLE IF NOT EXISTS todos(
            id INTEGER PRIMARY KEY,
            text TEXT,
            done INTEGER DEFAULT 0
        )
    """)

# 5편: Frontend에 HTML 제공
@app.get("/")
def home():
    return render_template("index.html")

# 4편: JSON API 엔드포인트
@app.get("/api/todos")
def list_todos():
    rows = conn().execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/todos")
def add_todo():
    text = request.get_json()["text"]
    with conn() as c:
        # 7편: 파라미터 바인딩으로 SQL injection 방어
        c.execute("INSERT INTO todos(text) VALUES (?)", (text,))
    return jsonify(ok=True), 201

# 8편: 헬스 체크
@app.get("/health")
def health():
    return {"status": "ok"}
```

### 3단계 — Frontend 작성 (templates/index.html)

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>Todo</title>
  <!-- 2편: 분리된 CSS -->
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <h1>할 일 목록</h1>
  <form id="f">
    <input id="t" placeholder="할 일을 입력하세요">
    <button>추가</button>
  </form>
  <!-- 3편: DOM 조작으로 목록 표시 -->
  <ul id="list"></ul>
<script>
async function load() {
  // 4편: fetch API로 JSON 데이터 요청
  const items = await (await fetch("/api/todos")).json();
  const ul = document.getElementById("list");
  ul.innerHTML = "";
  items.forEach(i => {
    const li = document.createElement("li");
    li.textContent = i.text;
    ul.appendChild(li);
  });
}

document.getElementById("f").addEventListener("submit", async e => {
  e.preventDefault();
  const text = document.getElementById("t").value;
  // 4편: POST 요청으로 데이터 저장
  await fetch("/api/todos", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({text})
  });
  document.getElementById("t").value = "";
  load();
});

load();
</script>
</body>
</html>
```

### 4단계 — Smoke test

```bash
flask --app app run
# 다른 터미널에서
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"첫 번째 할 일"}' http://localhost:5000/api/todos
curl http://localhost:5000/api/todos
curl http://localhost:5000/health
```

### 5단계 — Docker로 감싸기 (8편 배포)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV DB_PATH=/data/todo.db
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

```bash
docker build -t todo-app .
docker run -p 8000:8000 -v $PWD/data:/data todo-app
```

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| DB 경로를 코드에 하드코딩 | 배포 개념 부재 | 환경 변수로 분리 (8편) |
| 에러에도 항상 200 응답 | HTTP 상태 코드 모름 | 실패 시 4xx/5xx 돌려주기 (4편) |
| 권한 검사를 Frontend에만 배치 | 경계 개념 부재 | Backend에서 재검사 필수 (5편) |
| 처음부터 큰 프레임워크 선택 | 도구 위주 학습 | 작은 앱 완성 후 확장 |
| 테스트 없이 바로 배포 | 검증 습관 부재 | curl로 핵심 API 먼저 확인 |

## AI 팁: 이 구조를 바탕으로 요청하는 방법

이 시리즈를 읽고 나면 AI에게 다음과 같이 구체적으로 요청할 수 있습니다.

```
"Flask + SQLite로 Todo 앱을 만들어줘.
다음 요구사항을 반드시 포함해줘:
1. DB 경로는 DB_PATH 환경 변수로 읽기
2. API 엔드포인트: GET/POST /api/todos, GET /health
3. SQL 쿼리는 파라미터 바인딩 사용 (SQL injection 방어)
4. Dockerfile 포함
5. requirements.txt에 버전 명시"
```

이 정도로 구체적으로 요청하면, AI가 보안과 배포까지 고려한 코드를 만들어 줍니다.

## 체크리스트

- [ ] Frontend, Backend, Database가 한 앱 안에 모두 있습니다.
- [ ] `/health` 엔드포인트가 있습니다.
- [ ] 설정이 환경 변수로 분리되어 있습니다.
- [ ] SQL injection 방어를 위한 파라미터 바인딩이 있습니다.
- [ ] `curl`로 핵심 API를 직접 호출해 봤습니다.

## 처음 질문으로 돌아가기

- **앞선 아홉 개 개념은 한 앱 안에서 어떻게 연결될까요?**
  URL 요청(1편) → HTML/CSS/JS 제공(2편) → DOM 조작(3편) → HTTP API 통신(4편) → Backend 처리(5편) → 인증 확인(6편) → DB 저장(7편) → 환경 변수와 헬스 체크(8편) → 캐시 정책(9편)이 하나의 흐름으로 이어집니다.

- **바이브코딩으로 앱을 만들 때 어떤 구조가 좋을까요?**
  처음부터 환경 변수 분리, 파라미터 바인딩, 헬스 체크를 포함해 요청하면, AI가 배포 가능한 구조로 만들어 줍니다.

- **이 시리즈 이후 어떻게 계속 배울 수 있을까요?**
  이 앱에 기능을 추가하는 것이 가장 좋은 다음 단계입니다. 로그인 기능, 완료 토글, 삭제 기능, 실제 PaaS 배포를 차례로 시도해 보세요.

## 정리

이것으로 바이브코딩을 위한 웹 개발 기초 시리즈를 마칩니다. 웹의 흐름부터 배포까지, 각 개념이 왜 중요한지를 바이브코딩 관점에서 함께 봤습니다. AI 도구는 계속 발전하지만, 웹의 기본 원리는 변하지 않습니다. 이 원리를 알고 AI와 협력하면, 빠르게 만들면서도 안전하고 유지보수 가능한 앱을 만들 수 있습니다.

## 참고 자료

- [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [sqlite3 — DB-API 2.0 interface for SQLite databases](https://docs.python.org/3/library/sqlite3.html)
- [Docker Get Started](https://docs.docker.com/get-started/)
- [The Twelve-Factor App](https://12factor.net/)
- [Fetch API 사용법 (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- **바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기 (현재 글)**

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, 마무리프로젝트, Flask, 풀스택, 프로젝트
