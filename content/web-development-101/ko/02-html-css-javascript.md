---
series: web-development-101
episode: 2
title: "Web Development 101 (2/10): HTML, CSS, JavaScript"
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
  - HTML
  - CSS
  - JavaScript
  - Frontend
seo_description: HTML, CSS, JavaScript가 구조, 스타일, 동작을 어떻게 나누는지 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (2/10): HTML, CSS, JavaScript

웹 페이지를 처음 만들 때는 세 언어가 왜 따로 존재하는지 잘 와닿지 않습니다. 화면 하나를 만들 뿐인데 구조용 언어, 스타일용 언어, 동작용 언어가 따로 있다는 사실이 오히려 번거롭게 보이기도 합니다. 하지만 규모가 조금만 커져도 이 분리가 왜 중요한지 금방 드러납니다.

이 글은 Web Development 101 시리즈의 2번째 글입니다.

여기서는 HTML, CSS, JavaScript가 각각 무엇을 맡고, 왜 세 층을 분리하는 편이 유지보수와 협업에 유리한지 정리하겠습니다.

![Web Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/02/02-01-concept-at-a-glance.ko.png)
*Web Development 101 2장 흐름 개요*

> HTML·CSS·JavaScript는 구조·표현·동작이라는 서로 다른 책임을 가진 세 층입니다 — 한 화면을 만들 때는 번거롭게 느껴지지만, 이 분리가 유지보수와 협업 비용을 좌우합니다.

## 먼저 던지는 질문

- 웹 페이지는 왜 세 가지 언어로 나뉠까요?
- HTML, CSS, JavaScript는 각각 무엇을 책임질까요?
- 세 언어가 함께 동작할 때 어떤 연결 지점이 생길까요?

## 왜 이 구분이 중요한가

세 언어가 한 파일 안에서 뒤엉키면 한 줄을 고칠 때마다 다른 영역이 흔들립니다. 디자인 수정이 동작 버그를 부르고, 스크립트 변경이 마크업 구조를 깨뜨리는 식입니다. 작은 예제에서는 버틸 수 있어도 팀 작업으로 넘어가면 금방 읽기 어려워집니다.

이 분리는 단지 미적인 취향이 아닙니다. 디자이너는 CSS를, 프론트엔드 엔지니어는 JavaScript를, 콘텐츠 담당자는 HTML을 주로 다룹니다. 역할이 나뉘어야 변경 범위가 좁아지고, 캐시 전략도 단순해지고, 코드 리뷰도 훨씬 쉬워집니다.

## 한눈에 보는 개념 지도

이 그림에서 중요한 점은 세 언어가 같은 페이지를 만들더라도 같은 문제를 해결하지는 않는다는 사실입니다. HTML은 구조를, CSS는 시각 규칙을, JavaScript는 사용자 반응을 맡으므로 수정 범위를 분리할 수 있습니다.

### 직접 검증해 볼 포인트

- HTML만 있는 파일을 열어 제목과 버튼 구조가 먼저 보이는지 확인합니다.
- 같은 파일에 CSS를 연결한 뒤 색상과 여백만 바뀌는지 관찰합니다.
- JavaScript를 붙여 클릭 시 경고창이 뜨는지 확인해 구조·스타일·동작이 따로 바뀌는 경험을 만듭니다.

**기대 결과:** HTML 없이 CSS나 JavaScript만으로는 페이지 골격이 생기지 않고, 각 파일을 따로 수정할 때 영향 범위도 분리됩니다.

**실패 모드:** 모든 스타일과 동작을 HTML 안에 섞어 넣으면 작은 변경에도 파일 전체를 다시 읽어야 하고, 캐시 이점도 크게 줄어듭니다.

## 먼저 알아둘 용어

- **HTML**: 제목, 문단, 링크, 폼 같은 구조를 표현합니다.
- **CSS**: 색상, 폰트, 레이아웃처럼 보이는 스타일을 정의합니다.
- **JavaScript**: 클릭, 입력, 비동기 호출 같은 동작을 추가합니다.
- **Selector**: CSS가 어느 요소에 적용될지 고르는 규칙입니다.
- **Event**: 사용자 입력이나 브라우저 상태 변화를 JavaScript가 받을 수 있게 하는 신호입니다.

## 전후 비교로 보는 분리의 가치

**Before (모든 것이 혼합)**

```html
<h1 style="color:red" onclick="alert('hi')">Title</h1>
```

**After (역할 분리)**

```html
<h1 class="title">Title</h1>
```

```css
.title { color: red; }
```

```js
document.querySelector(".title").addEventListener("click", () => alert("hi"));
```

결과는 같아도 바꾸는 방법은 훨씬 단순해집니다. 제목 스타일을 바꿀 때 HTML을 뜯지 않아도 되고, 클릭 동작을 지울 때 CSS를 건드릴 이유도 없습니다.

## 분리된 페이지를 다섯 단계로 만들기

### 1단계 — HTML 기본 구조 만들기

```html
<!-- index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Hello</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <h1 class="title">Hello there</h1>
    <button id="say">Greet</button>
    <script src="app.js" defer></script>
  </body>
</html>
```

HTML은 이 페이지에 어떤 요소가 있는지 선언합니다. 제목과 버튼이 있다는 사실이 먼저 정해져야 그다음 스타일과 동작을 붙일 수 있습니다.

### 2단계 — CSS로 스타일 추가하기

```css
/* style.css */
body { font-family: system-ui; }
.title { color: steelblue; }
button { padding: 8px 16px; }
```

CSS는 구조를 바꾸지 않고 모양만 조절합니다. 이 분리 덕분에 시각 디자인을 수정할 때 HTML 구조를 흔들지 않아도 됩니다.

### 3단계 — JavaScript로 동작 추가하기

```js
// app.js
document.getElementById("say").addEventListener("click", () => {
  alert("Nice to meet you");
});
```

JavaScript는 버튼 클릭 같은 사용자 입력에 반응합니다. 이때 `id`와 `class`는 HTML이 JavaScript와 CSS에 제공하는 연결 고리 역할을 합니다.

### 4단계 — 브라우저에서 열기

```bash
python3 -m http.server 8000
# http://localhost:8000 열기
```

간단한 정적 서버를 띄우면 파일 연결 상태를 실제 브라우저에서 확인할 수 있습니다.

### 5단계 — DOM 트리와 스타일 확인하기

```text
F12 → Elements 탭 → DOM 트리와 적용된 스타일 확인
```

Elements 탭에서는 HTML 구조와 CSS 규칙이 어떻게 맞물리는지 한 번에 볼 수 있습니다. 브라우저가 실제로 어떤 DOM을 만들었는지 확인하는 습관이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- HTML의 `class`와 `id`는 CSS와 JavaScript가 연결되는 지점입니다.
- `defer`는 HTML 파싱이 끝난 뒤 JavaScript를 실행하게 만듭니다.
- CSS는 여러 규칙이 우선순위에 따라 합쳐지는 cascade 구조를 가집니다.

## 여기서 자주 헷갈립니다

1. **`style="..."`를 과하게 쓰는 경우**: CSS 파일의 장점이 사라집니다.
2. **큰 `<script>` 블록을 HTML 안에 넣는 경우**: 가독성과 캐시 효율이 모두 떨어집니다.
3. **같은 `id`를 여러 요소에 재사용하는 경우**: `id`는 문서 안에서 유일해야 합니다.
4. **CSS specificity를 이해하지 못한 채 `!important`에 의존하는 경우**: 규칙 충돌이 더 복잡해집니다.
5. **스타일 변경을 모두 JavaScript로만 처리하는 경우**: CSS 클래스를 토글하는 편이 더 단순합니다.

## 운영에서는 이렇게 보입니다

React나 Vue 같은 프레임워크를 써도 브라우저가 받는 것은 HTML, CSS, JavaScript입니다. 프레임워크는 이 세 언어를 더 잘 관리하게 도와주는 도구일 뿐입니다. 이 원칙을 알고 있으면 새로운 도구를 배울 때도 중심을 잃지 않습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 먼저 의미 있는 HTML을 씁니다. 가능하면 semantic tag를 사용합니다.
- CSS는 재사용 가능한 클래스 중심으로 설계합니다.
- JavaScript는 동작에만 집중하게 둡니다.
- 접근성은 나중이 아니라 처음부터 함께 봅니다.
- 변경이 한 곳에서 끝나도록 구조를 짭니다.

## 체크리스트

- [ ] 세 언어의 책임을 각각 한 문장으로 설명할 수 있습니다.
- [ ] inline CSS와 external CSS의 차이를 알고 있습니다.
- [ ] DevTools에서 DOM 트리와 CSS 규칙을 읽을 수 있습니다.
- [ ] `defer`와 `async`의 차이를 알고 있습니다.
- [ ] 뒤섞인 코드를 분리된 파일 구조로 옮길 수 있습니다.

## 연습 문제

1. inline style이 많은 HTML 파일 하나를 골라 CSS 파일로 분리해 보세요.
2. 버튼 다섯 개를 만들고 CSS 클래스를 토글해 배경색이 바뀌게 해 보세요.
3. 자주 가는 사이트의 HTML에서 semantic tag 다섯 개를 찾아보세요.

## 정리와 다음 글

HTML, CSS, JavaScript는 관심사를 분리하는 가장 기본적인 훈련입니다. 구조, 스타일, 동작을 나눠 생각할 수 있어야 브라우저가 화면을 어떻게 그리는지도 자연스럽게 이해됩니다. 다음 글에서는 브라우저가 HTML을 DOM 트리로 바꾸는 과정을 보겠습니다.

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

## 실전 앵커 모음: 화면 구성을 운영 문서로 바꾸기

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

- **웹 페이지는 왜 세 가지 언어로 나뉠까요?**
  - 구조, 스타일, 동작을 한 파일에 섞어 두면 제목 색 하나를 바꾸는 일도 HTML과 스크립트를 함께 읽어야 해서 변경 범위가 커집니다. `style="..."`와 `onclick="..."`를 걷어 내고 HTML·CSS·JavaScript를 분리하면 역할이 선명해지고 캐시와 코드 리뷰도 쉬워집니다.
- **HTML, CSS, JavaScript는 각각 무엇을 책임질까요?**
  - HTML은 `<h1 class="title">`와 `<button id="say">`처럼 페이지 골격을 선언하고, CSS는 `.title { color: steelblue; }`와 `button { padding: 8px 16px; }`처럼 보이는 규칙을 정합니다. JavaScript는 `getElementById("say")`에 클릭 리스너를 붙여 `alert("Nice to meet you")`를 띄우는 식으로 사용자 반응을 담당합니다.
- **세 언어가 함께 동작할 때 어떤 연결 지점이 생길까요?**
  - HTML의 `class`와 `id`가 CSS selector와 JavaScript DOM API가 만나는 연결점입니다. `<link rel="stylesheet" href="style.css">`와 `<script src="app.js" defer></script>`가 붙으면 같은 문서를 기준으로 스타일과 동작이 각각 결합되고, Elements 탭에서 그 결합 결과를 바로 확인할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- **HTML, CSS, JavaScript (현재 글)**
- 브라우저와 DOM (예정)
- HTTP와 API (예정)
- Frontend와 Backend (예정)
- 인증과 세션 (예정)
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [HTML basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Creating_the_content)
- [CSS basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Styling_the_content)
- [JavaScript basics (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Adding_interactivity)

### 개념 보강
- [Semantic HTML (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/Semantics)
- [script 요소와 defer/async (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, HTML, CSS, JavaScript, Frontend
