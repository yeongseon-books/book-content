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

시리즈를 따라오며 웹의 흐름, 브라우저, HTTP, Frontend와 Backend, 인증, 데이터베이스, 배포, 성능까지 각각 따로 보았습니다. 이제는 이 조각들을 하나의 앱 안에 묶어 볼 차례입니다. 지식은 작은 결과물을 직접 만들어 볼 때 비로소 자기 것이 됩니다.

이 글은 Web Development 101 시리즈의 마지막 글입니다. 여기서는 Todo 앱 하나를 만들면서 HTML, Flask, SQLite, 환경 변수, 헬스 체크, 컨테이너 실행까지 한 흐름으로 연결하겠습니다.

## 먼저 던지는 질문

- 앞선 아홉 개 개념은 한 앱 안에서 어떻게 연결될까요?
- 작은 풀스택 프로젝트는 어떤 폴더 구조로 시작하면 좋을까요?
- Frontend, Backend, 데이터베이스는 어떤 API 계약으로 묶일까요?

## 큰 그림

![Web Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/10/10-01-concept-at-a-glance.ko.png)

*Web Development 101 10장 흐름 개요*

이 그림에서는 작은 웹앱 만들기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 작은 웹앱 만들기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## Before / After로 보는 범위 변화

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

Tags: Computer Science, WebDevelopment, Capstone, Flask, FullStack, Project
