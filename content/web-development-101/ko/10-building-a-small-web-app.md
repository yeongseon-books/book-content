---
series: web-development-101
episode: 10
title: "Web Development 101 (10/10): 작은 웹앱 만들기"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/212"
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
  - Capstone
  - Flask
  - FullStack
  - Project
seo_description: Flask, HTML, SQLite, 배포를 묶어 작은 Todo 앱을 만드는 글입니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (10/10): 작은 웹앱 만들기

시리즈를 따라오며 웹의 흐름, 브라우저, HTTP, Frontend와 Backend, 인증, 데이터베이스, 배포, 성능까지 각각 따로 보았습니다. 이제는 이 조각들을 하나의 앱 안에 묶어 볼 차례입니다. 지식은 작은 결과물을 직접 만들어 볼 때 비로소 자기 것이 됩니다.

이 글은 Web Development 101 시리즈의 마지막 글입니다.

여기서는 Todo 앱 하나를 만들면서 HTML, Flask, SQLite, 환경 변수, 헬스 체크, 컨테이너 실행까지 한 흐름으로 연결하겠습니다.

![Web Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/10/10-01-concept-at-a-glance.ko.png)
*Web Development 101 10장 흐름 개요*

> 마지막 글은 시리즈의 모든 조각을 하나의 작은 앱 안에서 다시 연결하는 자리입니다 — HTML·Flask·SQLite·환경 변수·헬스 체크·컨테이너가 따로 배운 개념이 아닌 하나의 흐름임을 손으로 확인하는 단계입니다.

## 이 글에서 다룰 문제

- 앞선 아홉 개 개념은 한 앱 안에서 어떻게 연결될까요?
- 작은 풀스택 프로젝트는 어떤 폴더 구조로 시작하면 좋을까요?
- Frontend, Backend, 데이터베이스는 어떤 API 계약으로 묶일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 마지막 글이 중요한가

개념을 따로 아는 것과 하나의 제품 흐름으로 엮어 보는 것은 다릅니다. 작은 Todo 앱이라도 직접 만들어 보면 URL 요청, HTML 렌더링, API 호출, 데이터베이스 쓰기, 환경 변수, 배포 헬스 체크가 한 선으로 이어집니다. 이 연결 경험이 있어야 다음 프로젝트에서도 어디서부터 시작할지 감이 생깁니다.

## 앱의 전체 흐름

```
사용자가 폼 제출
    |
    | POST /api/todos (fetch)
    v
Flask Backend
    |  입력 검증
    |  SQLite INSERT
    v
데이터베이스 저장 완료
    |
    v  201 Created + 생성된 항목 반환
Frontend
    |  DOM 업데이트 (할 일 목록에 추가)
    v
사용자에게 결과 표시

시리즈 개념과의 연결:
  - 1장: HTTP 요청/응답 흐름
  - 2장: HTML/CSS/JS 분리
  - 3장: DOM 조작 (목록 업데이트)
  - 4장: REST API 설계 (GET/POST/DELETE)
  - 5장: Frontend↔Backend 분리, CORS
  - 6장: 세션 기반 사용자 인증
  - 7장: SQLite CRUD, 파라미터 바인딩
  - 8장: 환경 변수, Docker, 헬스 체크
  - 9장: 정적 자산 캐시 헤더
```

## 먼저 알아둘 용어

- **Capstone**: 시리즈를 마무리하는 통합 프로젝트입니다.
- **Full-stack**: Frontend, Backend, Database, Deployment가 함께 있는 구조입니다.
- **Vertical Slice**: 기능 하나를 UI부터 DB까지 수직으로 끝까지 구현하는 방식입니다.
- **Smoke test**: 핵심 경로가 실제로 동작하는지 빠르게 확인하는 최소 검증입니다.

## 프로젝트 구조

```
todo-app/
├── app.py                  # Flask Backend
├── templates/
│   └── index.html          # HTML 템플릿
├── static/
│   └── style.css           # CSS 스타일
├── requirements.txt        # 의존성 버전 고정
├── .env                    # 로컬 환경 변수 (저장소 제외)
├── .gitignore
└── Dockerfile
```

## 1단계: 프로젝트 초기화

```bash
mkdir todo-app && cd todo-app
python3 -m venv .venv && source .venv/bin/activate

pip install flask gunicorn python-dotenv

# requirements.txt 생성
pip freeze > requirements.txt

# .gitignore 설정
cat > .gitignore << 'EOF'
.venv/
.env
*.db
__pycache__/
*.pyc
.DS_Store
EOF

# 로컬 환경 변수
cat > .env << 'EOF'
DB_PATH=todo.db
SECRET_KEY=dev-only-change-in-production
DEBUG=true
PORT=5000
EOF
```

## 2단계: Backend 작성

```python
# app.py
import os
import sqlite3
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "todo.db")
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=not DEBUG,  # 로컬 개발에서는 HTTP 허용
    SESSION_COOKIE_SAMESITE="Lax",
)


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS todos (
              id         INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id    TEXT    NOT NULL DEFAULT 'anonymous',
              text       TEXT    NOT NULL,
              done       INTEGER NOT NULL DEFAULT 0,
              created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_todos_user ON todos(user_id, created_at DESC)"
        )


init_db()


# ── HTML 화면 ─────────────────────────────────────
@app.get("/")
def home():
    return render_template("index.html")


# ── 할 일 API ─────────────────────────────────────
@app.get("/api/todos")
def list_todos():
    user_id = session.get("user_id", "anonymous")
    rows = get_db().execute(
        "SELECT id, text, done, created_at FROM todos WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/todos")
def create_todo():
    data = request.get_json()
    if not data or not data.get("text", "").strip():
        return jsonify(error={"code": "VALIDATION_ERROR", "message": "text 필드는 필수입니다"}), 400

    user_id = session.get("user_id", "anonymous")
    with get_db() as con:
        cur = con.execute(
            "INSERT INTO todos(user_id, text) VALUES (?, ?)",
            (user_id, data["text"].strip())
        )
        todo_id = cur.lastrowid

    return jsonify({"id": todo_id, "text": data["text"].strip(), "done": False}), 201


@app.patch("/api/todos/<int:todo_id>")
def toggle_todo(todo_id):
    user_id = session.get("user_id", "anonymous")
    with get_db() as con:
        cur = con.execute(
            "UPDATE todos SET done = NOT done WHERE id = ? AND user_id = ?",
            (todo_id, user_id)
        )
    if cur.rowcount == 0:
        return jsonify(error={"code": "NOT_FOUND"}), 404
    return jsonify(ok=True)


@app.delete("/api/todos/<int:todo_id>")
def delete_todo(todo_id):
    user_id = session.get("user_id", "anonymous")
    with get_db() as con:
        cur = con.execute(
            "DELETE FROM todos WHERE id = ? AND user_id = ?",
            (todo_id, user_id)
        )
    if cur.rowcount == 0:
        return jsonify(error={"code": "NOT_FOUND"}), 404
    return "", 204


# ── 헬스 체크 ─────────────────────────────────────
@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/ready")
def ready():
    try:
        get_db().execute("SELECT 1").fetchone()
        return jsonify(status="ready", db="ok"), 200
    except Exception as e:
        return jsonify(status="not ready", db=str(e)), 503


# ── 정적 자산 캐시 헤더 ───────────────────────────
@app.after_request
def set_cache_headers(response):
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "private, no-store"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, debug=DEBUG)
```

## 3단계: Frontend 작성

```html
<!-- templates/index.html -->
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Todo 앱</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <div class="container">
    <h1>할 일 목록</h1>

    <form id="add-form" class="add-form">
      <input id="todo-input" type="text" placeholder="할 일을 입력하세요" required>
      <button type="submit" class="btn btn-primary">추가</button>
    </form>

    <div id="error-msg" class="error-msg" hidden></div>

    <ul id="todo-list" class="todo-list">
      <li class="loading">로딩 중...</li>
    </ul>
  </div>

  <script defer>
    const API = "/api";

    // API 헬퍼 함수
    async function api(path, options = {}) {
      const res = await fetch(API + path, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options,
      });
      if (res.status === 204) return null;
      const body = await res.json();
      if (!res.ok) throw new Error(body.error?.message || `오류 ${res.status}`);
      return body;
    }

    // 오류 표시
    function showError(msg, duration = 4000) {
      const el = document.getElementById("error-msg");
      el.textContent = msg;
      el.hidden = false;
      setTimeout(() => { el.hidden = true; }, duration);
    }

    // 할 일 목록 렌더링
    function renderTodos(todos) {
      const list = document.getElementById("todo-list");
      if (todos.length === 0) {
        list.innerHTML = '<li class="empty">할 일이 없습니다.</li>';
        return;
      }
      const fragment = document.createDocumentFragment();
      for (const todo of todos) {
        const li = document.createElement("li");
        li.className = "todo-item" + (todo.done ? " done" : "");
        li.dataset.id = todo.id;
        li.innerHTML = `
          <span class="todo-text">${escapeHtml(todo.text)}</span>
          <div class="todo-actions">
            <button class="btn-toggle" title="${todo.done ? '미완료' : '완료'}">
              ${todo.done ? '↩' : '✓'}
            </button>
            <button class="btn-delete" title="삭제">✕</button>
          </div>
        `;
        fragment.appendChild(li);
      }
      list.innerHTML = "";
      list.appendChild(fragment);
    }

    // XSS 방어
    function escapeHtml(text) {
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }

    // 목록 불러오기
    async function loadTodos() {
      try {
        const todos = await api("/todos");
        renderTodos(todos);
      } catch (err) {
        showError("목록을 불러오지 못했습니다: " + err.message);
      }
    }

    // 이벤트 처리
    document.getElementById("add-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("todo-input");
      const text = input.value.trim();
      if (!text) return;

      try {
        await api("/todos", {
          method: "POST",
          body: JSON.stringify({ text }),
        });
        input.value = "";
        await loadTodos();
      } catch (err) {
        showError(err.message);
      }
    });

    // 이벤트 위임으로 완료/삭제 처리
    document.getElementById("todo-list").addEventListener("click", async (e) => {
      const li = e.target.closest(".todo-item");
      if (!li) return;
      const id = li.dataset.id;

      if (e.target.closest(".btn-toggle")) {
        try {
          await api(`/todos/${id}`, { method: "PATCH" });
          await loadTodos();
        } catch (err) {
          showError(err.message);
        }
      } else if (e.target.closest(".btn-delete")) {
        try {
          await api(`/todos/${id}`, { method: "DELETE" });
          await loadTodos();
        } catch (err) {
          showError(err.message);
        }
      }
    });

    // 초기 로딩
    loadTodos();
  </script>
</body>
</html>
```

```css
/* static/style.css */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: #f5f5f5;
  color: #333;
  line-height: 1.5;
}

.container {
  max-width: 600px;
  margin: 2rem auto;
  padding: 0 1rem;
}

h1 { font-size: 1.75rem; margin-bottom: 1.5rem; color: #111; }

.add-form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.add-form input {
  flex: 1;
  padding: 0.625rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.btn {
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-primary { background: #3b82f6; color: white; }
.btn-primary:hover { background: #2563eb; }

.error-msg {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.todo-list { list-style: none; }

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: opacity 0.2s;
}

.todo-item.done .todo-text {
  text-decoration: line-through;
  opacity: 0.5;
}

.todo-actions { display: flex; gap: 0.5rem; }

.btn-toggle, .btn-delete {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-toggle:hover { background: #f0fdf4; border-color: #86efac; }
.btn-delete:hover { background: #fef2f2; border-color: #fca5a5; }

.loading, .empty {
  padding: 2rem;
  text-align: center;
  color: #9ca3af;
}
```

## 4단계: Smoke Test

```bash
# 서버 실행
flask --app app run

# 다른 터미널에서 API 테스트
# 할 일 추가
curl -s -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"text": "첫 번째 할 일"}' | python3 -m json.tool

# 목록 조회
curl -s http://localhost:5000/api/todos | python3 -m json.tool

# 완료 토글 (id=1)
curl -s -X PATCH http://localhost:5000/api/todos/1

# 삭제
curl -s -X DELETE http://localhost:5000/api/todos/1
echo "Status: $?"

# 헬스 체크
curl -s http://localhost:5000/health
curl -s http://localhost:5000/ready
```

## 5단계: Docker로 감싸기

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 의존성 먼저 (레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY . .

# 데이터 디렉토리 생성
RUN mkdir -p /data

# 환경 변수 기본값
ENV DB_PATH=/data/todo.db
ENV PORT=8000
ENV DEBUG=false

# 비루트 사용자
RUN useradd -m appuser && chown -R appuser /app /data
USER appuser

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} app:app"]
```

```bash
# 빌드
docker build -t todo-app:latest .

# 실행 (DB를 로컬 디렉토리에 저장)
mkdir -p ./data
docker run -p 8000:8000 \
  -e SECRET_KEY=my-production-secret \
  -v $PWD/data:/data \
  todo-app:latest

# 테스트
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| DB 경로를 코드에 하드코딩 | 환경 간 이식 불가 | `os.environ.get("DB_PATH")` |
| JavaScript를 HTML에 모두 몰아넣기 | 코드 가독성 저하, 캐시 불가 | 외부 .js 파일로 분리 |
| 오류에도 200 반환 | 클라이언트가 실패 감지 불가 | 400/404/500 등 적절한 코드 사용 |
| innerHTML로 사용자 텍스트 삽입 | XSS 취약점 | textContent 또는 escapeHtml 사용 |
| 배포 전 smoke test 생략 | 운영에서 기본 API 장애 발견 | curl로 핵심 경로 검증 |

## 직접 검증해 볼 포인트

```bash
# 1. API 계약 검증
curl -s -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
# → 400 + VALIDATION_ERROR

# 2. 환경 변수로 DB 경로 변경
DB_PATH=/tmp/test.db flask --app app run &
curl -s http://localhost:5000/api/todos
# → /tmp/test.db에 별도로 저장됨

# 3. 컨테이너 실행 후 헬스 체크
docker run -d -p 8000:8000 -e SECRET_KEY=test -e DB_PATH=/tmp/test.db todo-app:latest
sleep 2
curl -f http://localhost:8000/health && echo "OK"
```

**기대 결과:** API와 HTML 화면이 같은 데이터 원본을 공유하고, 환경 변수만 바꿔도 저장 위치가 달라지며, 컨테이너 안에서도 동일한 동작이 재현됩니다.

**실패 모드:** 상태 코드를 제대로 나누지 않으면 Frontend가 실패를 감지하기 어렵습니다. 데이터 경로를 하드코딩하면 로컬과 배포 환경을 같은 코드로 운영하기 어렵습니다.

## 다음에 추가할 수 있는 기능

```
지금 만든 앱에서 한 단계씩:

1. 사용자 인증 추가 (6장)
   - POST /login, POST /logout
   - 세션으로 user_id 관리
   - 사용자별 Todo 분리

2. 페이지네이션 추가 (4장)
   - GET /api/todos?page=1&limit=20
   - 커서 기반 페이지네이션

3. 정적 자산 최적화 (9장)
   - 파일명에 해시 추가 (style.abc123.css)
   - Lighthouse 점수 확인

4. CI/CD 연결 (8장)
   - GitHub Actions로 테스트 자동화
   - PaaS에 배포

5. 모니터링 추가
   - /metrics 엔드포인트
   - 요청별 응답 시간 로깅
```

## 운영에서는 이렇게 보입니다

이 작은 앱은 블로그, 메모 앱, 가계부, 챗봇처럼 다양한 서비스의 출발점이 될 수 있습니다. 큰 SaaS도 구조를 뜯어 보면 결국 여기에서 큐, 캐시, 인증, 배치, 모니터링이 층층이 추가된 형태에 가깝습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 작은 vertical slice를 끝까지 보냅니다.
- 환경마다 다른 값만 환경 변수로 분리합니다.
- health check, logging, monitoring을 처음부터 염두에 둡니다.
- 기능이 늘어나면 경계를 다시 그립니다.
- 제품이 커질수록 코드보다 팀 합의가 더 중요해진다고 봅니다.

## 운영 체크리스트

- [ ] Frontend, Backend, Database가 한 앱 안에 모두 있습니다.
- [ ] health check 엔드포인트가 있습니다.
- [ ] 설정이 환경 변수로 분리되어 있습니다.
- [ ] `curl`로 엔드포인트를 직접 호출해 봤습니다.
- [ ] 컨테이너로 실행해 봤습니다.

## 연습 문제

1. Todo 앱에 `toggle done`과 `delete` 기능이 이미 있습니다. 이번에는 세션 로그인을 붙여 사용자별 Todo를 분리해 보세요.
2. 정적 자산에 캐시 헤더를 붙이고 Lighthouse를 실행해 점수를 확인해 보세요.
3. GitHub Actions 워크플로를 만들어 push마다 `curl /health`를 자동 실행해 보세요.

## 정리와 다음 단계

이것으로 Web Development 101 시리즈를 마칩니다. 작은 앱 하나를 처음부터 끝까지 만들어 보면서 웹의 기본 층을 모두 한 번 연결했습니다. 다음 단계는 깊이입니다. Frontend Development 101, Backend Development 101, Database 101 같은 후속 시리즈로 한 층씩 더 깊게 들어갈 수 있습니다. 하지만 가장 좋은 다음 책은 새 앱 하나를 직접 더 만드는 일입니다.

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
