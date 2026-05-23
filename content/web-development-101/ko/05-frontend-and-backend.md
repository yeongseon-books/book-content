---
series: web-development-101
episode: 5
title: "Web Development 101 (5/10): Frontend와 Backend"
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
  - Frontend
  - Backend
  - Architecture
  - FullStack
seo_description: Frontend와 Backend의 책임, SPA와 SSR, API 계약의 의미를 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (5/10): Frontend와 Backend

웹 개발을 배우다 보면 Frontend와 Backend를 서로 다른 기술 묶음처럼만 보기 쉽습니다. 하지만 실무에서 더 중요한 것은 도구 이름이 아니라 책임 경계입니다. 누가 데이터를 보여 주고, 누가 저장하고, 누가 권한을 검증하는지 구분되지 않으면 작은 서비스도 금방 지저분해집니다.

여기서는 Frontend와 Backend의 역할을 나눠 보고, SPA와 SSR이 어떤 차이를 가지는지, 두 세계를 잇는 API 계약이 왜 중요한지 정리하겠습니다.

![Web Development 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/05/05-01-concept-at-a-glance.ko.png)
*Web Development 101 5장 흐름 개요*

## 먼저 던지는 질문

- Frontend와 Backend의 일은 어디서 갈릴까요?
- 데이터의 진실은 어느 쪽이 가져야 할까요?
- SPA와 SSR은 무엇이 다를까요?

## 왜 이 경계가 중요한가

한 사람이 양쪽 코드를 모두 짜더라도 책임 경계가 흐려지면 코드가 빠르게 무너집니다. Frontend에서 권한 검사를 하고, Backend에서 화면용 문자열을 과하게 조립하고, API 형식이 문서 없이 바뀌기 시작하면 변경 영향 범위를 읽기 어려워집니다.

이 경계는 물리적인 선이 아니라 소유권에 대한 약속입니다. 무엇을 저장할지, 무엇을 노출할지, 어느 쪽이 최종 판단권을 가질지 먼저 정해야 시스템이 커져도 버틸 수 있습니다.

## 한눈에 보는 개념 지도

이 그림은 데이터가 보통 데이터베이스에서 시작해 Backend를 거쳐 Frontend로 올라오고, 최종적으로 사용자 경험으로 표현된다는 점을 강조합니다. 화면에 보이는 값과 시스템의 기준 데이터가 늘 같은 위치에 있는 것은 아닙니다.

### 직접 검증해 볼 포인트

- `/api/items` 같은 간단한 JSON 엔드포인트를 만들고 브라우저에서 실제로 목록을 그려 봅니다.
- 같은 데이터를 SSR 템플릿과 SPA fetch 방식으로 각각 렌더링해 첫 화면 차이를 관찰합니다.
- 브라우저 콘솔에서 CORS 오류를 일부러 재현해 어떤 origin 제약이 걸리는지 읽어 봅니다.

**기대 결과:** Backend가 응답 형태를 바꾸면 Frontend도 함께 수정되어야 하고, CORS 허용 없이는 브라우저가 다른 origin 호출을 막습니다.

**실패 모드:** 권한 검사를 Frontend에만 두면 개발자 도구로 우회할 수 있습니다. 계약 없이 양쪽을 동시에 바꾸면 필드 이름과 구조가 쉽게 어긋납니다.

## 먼저 알아둘 용어

- **Frontend**: 브라우저에서 실행되며 사용자에게 정보를 보여 주는 영역입니다.
- **Backend**: 서버에서 실행되며 데이터를 처리하고 저장하는 영역입니다.
- **SPA**: 첫 페이지를 한 번 로드한 뒤 JavaScript로 화면을 바꾸는 방식입니다.
- **SSR**: 요청마다 서버가 HTML을 만들어 돌려주는 방식입니다.
- **Contract**: 두 영역이 합의한 API 요청과 응답의 형태입니다.

## 전후 비교로 보는 책임 배치

**Before (프론트엔드에서 비밀번호 확인)**

```js
if (password === "admin1234") { login(); }  // anyone can read this
```

**After (백엔드에서 확인)**

```python
# 서버에서만 비교
if check_password(user, password):
    return token
```

비밀번호 검증처럼 민감한 판단은 서버에서 해야 합니다. Frontend 코드는 누구나 열어 볼 수 있기 때문입니다.

## 두 세계를 다섯 단계로 연결해 보기

### 1단계 — 아주 작은 Backend 만들기

```python
# server.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/api/items")
def items():
    return jsonify([{"id": 1, "name": "apple"}, {"id": 2, "name": "pear"}])

if __name__ == "__main__":
    app.run(port=8000)
```

이 서버는 `/api/items` 요청에 JSON 배열을 돌려줍니다. 이 응답 형식이 곧 Frontend와 Backend 사이의 첫 번째 계약이 됩니다.

### 2단계 — Frontend에서 호출하기

```html
<!-- index.html -->
<ul id="list"></ul>
<script>
fetch("http://localhost:8000/api/items")
  .then(r => r.json())
  .then(items => {
    const ul = document.getElementById("list");
    for (const it of items) {
      const li = document.createElement("li");
      li.textContent = it.name;
      ul.appendChild(li);
    }
  });
</script>
```

Frontend는 이 JSON 구조를 믿고 DOM을 만듭니다. `id`와 `name` 필드가 어떻게 생겼는지 양쪽이 함께 알고 있어야 합니다.

### 3단계 — CORS 허용하기

```python
# server.py에 추가
from flask_cors import CORS
CORS(app)
```

브라우저는 다른 origin으로 가는 요청을 기본적으로 제한합니다. 이 정책이 CORS이며, 서버가 허용 범위를 명시해야 브라우저가 요청을 통과시킵니다.

### 4단계 — 서버 사이드 렌더링과 비교하기

```python
# ssr.py
from flask import Flask, render_template_string
app = Flask(__name__)

@app.get("/")
def home():
    items = [{"name": "apple"}, {"name": "pear"}]
    return render_template_string("<ul>{% for i in items %}<li>{{ i.name }}</li>{% endfor %}</ul>", items=items)
```

SSR에서는 서버가 HTML까지 만들어 돌려줍니다. 첫 화면이 빠르게 보일 수 있지만, 이후 상호작용 방식은 SPA와 다르게 설계됩니다.

### 5단계 — 같은 기능, 다른 스타일

```text
SPA: HTML 한 줄과 JS가 데이터를 가져와 DOM을 만듭니다.
SSR: 서버가 매 요청마다 완성된 HTML을 돌려줍니다.
```

둘은 경쟁 관계라기보다 상황에 따라 선택하는 렌더링 방식입니다. 첫 화면 속도, 상호작용 패턴, SEO 요구사항에 따라 달라집니다.

## 이 코드에서 먼저 봐야 할 점

- `/api/items`의 응답 형태는 양쪽이 함께 지켜야 하는 계약입니다.
- CORS는 서버 보안 정책이라기보다 브라우저 보안 정책에 가깝습니다.
- SSR은 첫 paint를 빠르게 만들고, SPA는 이후 상호작용을 빠르게 만드는 데 유리합니다.

## 여기서 자주 헷갈립니다

1. **권한 검사를 Frontend에서만 하는 경우**: 개발자 도구로 쉽게 우회됩니다.
2. **API 계약 없이 양쪽을 동시에 개발하는 경우**: 필드 이름과 형태가 서로 달라집니다.
3. **모든 비즈니스 로직을 Backend로 몰아넣는 경우**: 단순한 화면 로직도 서버 의존이 커집니다.
4. **모든 로직을 Frontend로 밀어 넣는 경우**: 비밀 정보와 검증 규칙이 노출됩니다.
5. **CORS를 모든 origin에 무조건 열어 두는 경우**: 불필요한 보안 구멍이 생깁니다.

## 운영에서는 이렇게 보입니다

스타트업은 SPA + REST API 조합으로 시작하는 경우가 많고, 콘텐츠 사이트는 SSR 계열 프레임워크를 선호하는 경우가 많습니다. 어떤 조합을 택하더라도 강한 팀은 API 계약을 먼저 그리고, 진실은 Backend에, 사용자 경험은 Frontend에 두려는 원칙을 유지합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 데이터의 진실은 Backend에 둡니다.
- 사용자 경험은 Frontend에서 세심하게 다룹니다.
- API 계약을 먼저 그려 두고 양쪽 구현을 시작합니다.
- 보안과 권한 검사는 반드시 Backend에서 다시 확인합니다.
- SPA와 SSR은 유행이 아니라 상황에 맞춰 선택합니다.

## 체크리스트

- [ ] Frontend와 Backend의 책임을 각각 한 문장으로 설명할 수 있습니다.
- [ ] API 계약의 예를 간단히 그릴 수 있습니다.
- [ ] CORS 오류 메시지를 읽을 수 있습니다.
- [ ] SPA와 SSR의 장단점을 알고 있습니다.
- [ ] 권한 검사는 Backend가 맡는다는 점을 알고 있습니다.

## 연습 문제

1. 같은 화면을 SPA와 SSR 두 방식으로 각각 만들어 보고 첫 화면 속도를 비교해 보세요.
2. 일부러 CORS 오류를 만든 뒤 브라우저 콘솔 메시지를 읽어 보세요.
3. 하나의 엔드포인트를 골라 Frontend에서 호출할 때와 Backend에서 호출할 때 차이를 정리해 보세요.

## 정리와 다음 글

Frontend와 Backend의 경계는 기술 분류표가 아니라 책임 약속입니다. 이 약속이 선명해야 데이터, 보안, 사용자 경험이 제자리를 찾습니다. 다음 글에서는 이 경계 위에 로그인과 사용자 기억을 얹는 인증과 세션을 다루겠습니다.

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

## 실전 앵커 모음: 책임 경계을 운영 문서로 바꾸기

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

- **Frontend와 Backend의 일은 어디서 갈릴까요?**
  - 본문의 기준은 Frontend와 Backend를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **데이터의 진실은 어느 쪽이 가져야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **SPA와 SSR은 무엇이 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- **Frontend와 Backend (현재 글)**
- 인증과 세션 (예정)
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Client-side and server-side website programming (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview)
- [Single-page application (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/SPA)
- [Server-side rendering (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/SSR)

### 검증용 자료
- [CORS guide (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [Fetch API 사용법 (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Frontend, Backend, Architecture, FullStack
