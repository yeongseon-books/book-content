---
series: web-development-101
episode: 4
title: "Web Development 101 (4/10): HTTP와 API"
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
  - HTTP
  - API
  - REST
  - Networking
seo_description: HTTP 요청과 응답, 상태 코드, JSON API의 기본 구조를 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (4/10): HTTP와 API

이 글은 Web Development 101 시리즈의 네 번째 글입니다.

웹 개발을 하다 보면 결국 가장 많이 읽고 쓰는 것은 HTTP 메시지입니다. 브라우저가 페이지를 요청할 때도, JavaScript가 JSON 데이터를 가져올 때도, 모바일 앱이 서버와 통신할 때도 바닥에는 HTTP가 놓여 있습니다. 요청과 응답의 모양을 정확히 모르면 디버깅은 금방 추측 게임으로 바뀝니다.

여기서는 HTTP 요청과 응답이 어떤 형태를 가지는지, method와 status code와 header가 각각 어떤 의미를 가지는지, API 호출이 페이지 요청과 무엇이 다른지 정리하겠습니다.


![Web Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/04/04-01-concept-at-a-glance.ko.png)
*Web Development 101 4장 흐름 개요*

## 먼저 던지는 질문

- 클라이언트와 서버는 실제로 무엇을 주고받을까요?
- HTTP 요청과 응답은 어떤 요소로 구성될까요?
- GET, POST, PUT, DELETE는 각각 어떤 의미일까요?

## 왜 이 구조를 알아야 하는가

웹 개발의 절반은 HTTP 메시지를 만들고 읽는 일입니다. 요청이 어떤 method로 갔는지, 응답이 왜 404인지, 서버가 JSON을 줬는지 HTML을 줬는지를 읽지 못하면 오류 원인을 좁히기 어렵습니다. 프레임워크는 이 메시지를 다루기 쉽게 감싸 줄 뿐, 메시지 자체를 없애 주지는 않습니다.

한 번 HTTP의 모양을 익혀 두면 Flask, FastAPI, React, 모바일 앱, GraphQL, gRPC를 볼 때도 공통된 감각이 생깁니다. 이름은 달라도 많은 시스템이 결국 HTTP 위에서 움직이기 때문입니다.

## 한눈에 보는 개념 지도

그림을 볼 때는 요청과 응답이 모두 같은 틀을 가진다는 점을 먼저 기억하면 좋습니다. method, URL, header, body를 보낸 뒤 서버는 status code, header, body로 답합니다.

### 직접 검증해 볼 포인트

- `curl -v https://httpbin.org/get`으로 요청 줄과 응답 헤더를 그대로 확인합니다.
- GET과 POST를 각각 보내고 method에 따라 서버 동작이 달라지는지 비교합니다.
- JSON API 응답에서 `Content-Type: application/json`이 붙는지 확인합니다.

**기대 결과:** GET과 POST는 같은 URL이라도 다른 의도를 드러내고, JSON API는 `application/json` 헤더와 함께 본문 구조를 돌려줍니다.

**실패 모드:** 모든 실패 응답을 200으로 돌려주면 클라이언트는 오류를 분기하기 어렵습니다. `Content-Type`을 무시하면 HTML과 JSON을 잘못 해석하는 버그가 생깁니다.

## 먼저 알아둘 용어

- **Method**: 무엇을 하려는지 나타냅니다. GET은 조회, POST는 생성에 자주 씁니다.
- **Status code**: 요청 결과를 나타냅니다. 2xx는 성공, 4xx는 클라이언트 오류, 5xx는 서버 오류입니다.
- **Header**: `Content-Type`, `Authorization` 같은 메타데이터입니다.
- **Body**: JSON, HTML, 이미지 바이트처럼 실제 payload가 들어가는 영역입니다.
- **API**: 브라우저 사람이 아니라 프로그램이 호출하도록 설계된 엔드포인트입니다.

## 전후 비교로 보는 요청 대상의 차이

**Before (HTML page request)**

```python
import requests
r = requests.get("https://example.com")
print(r.text[:80])  # <!doctype html>...
```

**After (JSON API call)**

```python
import requests
r = requests.get("https://api.github.com/repos/python/cpython")
data = r.json()
print(data["full_name"], data["stargazers_count"])
```

둘 다 HTTP이지만 응답의 `Content-Type`이 다릅니다. 전자는 HTML 문서, 후자는 JSON 데이터입니다.

## HTTP 메시지를 다섯 단계로 읽어 보기

### 1단계 — GET 요청 보내기

```python
# 1_get.py
import requests
r = requests.get("https://httpbin.org/get?lang=en")
print(r.status_code)
print(r.json()["args"])  # {'lang': 'en'}
```

GET은 읽기 요청에 가장 많이 쓰입니다. 쿼리스트링이 서버에 그대로 전달되는 것도 함께 볼 수 있습니다.

### 2단계 — POST로 본문 보내기

```python
# 2_post.py
import requests
r = requests.post("https://httpbin.org/post", json={"name": "yeongseon"})
print(r.json()["json"])
```

POST는 서버 상태가 바뀔 수 있는 작업에 주로 사용합니다. JSON 본문을 보내면 서버가 그 내용을 읽어 처리합니다.

### 3단계 — 헤더 확인하기

```python
# 3_headers.py
import requests
r = requests.get("https://httpbin.org/headers", headers={"X-Custom": "hi"})
print(r.json()["headers"]["X-Custom"])
```

헤더는 인증, 캐시, 콘텐츠 타입 같은 부가 정보를 실어 나릅니다. 같은 URL이라도 헤더에 따라 처리 방식이 달라질 수 있습니다.

### 4단계 — 상태 코드로 분기하기

```python
# 4_status.py
import requests
for url in ["https://httpbin.org/status/200", "https://httpbin.org/status/404"]:
    r = requests.get(url)
    if r.ok:
        print("OK", r.status_code)
    else:
        print("FAIL", r.status_code)
```

클라이언트는 응답 본문만 보지 않고 상태 코드도 함께 읽어야 합니다. 같은 JSON 구조라도 200과 404는 전혀 다른 의미입니다.

### 5단계 — raw 요청과 응답 보기

```bash
curl -v https://httpbin.org/get
# > GET /get HTTP/1.1
# > Host: httpbin.org
# < HTTP/1.1 200 OK
# < Content-Type: application/json
```

`curl -v`는 HTTP가 실제로 어떤 텍스트를 주고받는지 감각을 잡는 데 좋습니다. 프레임워크 뒤에 숨은 메시지를 직접 볼 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `Content-Type`이 `text/html`인지 `application/json`인지에 따라 클라이언트 처리 방식이 달라집니다.
- POST는 서버 상태가 바뀔 수 있다는 계약을 담고 있습니다.
- 같은 URL이라도 method가 다르면 완전히 다른 동작을 할 수 있습니다.

## 여기서 자주 헷갈립니다

1. **GET으로 데이터를 생성하는 경우**: GET은 읽기 전용 계약으로 보는 편이 맞습니다.
2. **모든 응답을 200으로 돌려주는 경우**: 클라이언트가 실패를 구분할 수 없습니다.
3. **`Content-Type`을 무시하는 경우**: HTML을 JSON처럼 파싱하다가 오류가 납니다.
4. **에러 본문 형식을 제멋대로 만드는 경우**: 클라이언트가 메시지를 안정적으로 읽기 어렵습니다.
5. **인증 정보를 URL에 넣는 경우**: 로그와 히스토리에 오래 남습니다.

## 운영에서는 이렇게 보입니다

대부분의 웹과 모바일 앱은 JSON over HTTP 형태로 서버와 통신합니다. GraphQL과 gRPC도 결국 HTTP 위에 서 있습니다. 새 서비스를 처음 볼 때 API 문서를 먼저 읽는 이유도 여기에 있습니다. 요청과 응답의 형식이 시스템 계약의 중심이기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- method와 status code를 본래 의미에 맞게 씁니다.
- 에러 응답의 형식을 표준화합니다.
- 인증 정보는 header로 보내고, 토큰 수명은 짧게 둡니다.
- timeout과 retry 예산을 항상 같이 봅니다.
- API와 문서는 함께 자라야 한다고 생각합니다.

## 체크리스트

- [ ] 네 가지 기본 method의 의미를 알고 있습니다.
- [ ] 2xx, 4xx, 5xx 범위의 뜻을 알고 있습니다.
- [ ] `Content-Type`을 읽고 처리 분기를 할 수 있습니다.
- [ ] timeout과 retry를 설정할 수 있습니다.
- [ ] `curl`로 raw 요청을 날릴 수 있습니다.

## 연습 문제

1. `httpbin.org/anything`에 GET, POST, PUT, DELETE를 보내고 응답 차이를 비교해 보세요.
2. 3xx redirect를 따라가지 않는 코드를 작성해 보세요.
3. 공개 API 하나를 골라 세 개 이상의 엔드포인트를 호출해 보세요.

## 정리와 다음 글

HTTP는 문자 기반 계약이지만, 웹 개발에서는 가장 중요한 바닥 구조입니다. 요청과 응답의 모양을 알면 API를 읽고 서버를 디버깅하는 속도가 달라집니다. 다음 글에서는 이 계약의 양쪽 끝, Frontend와 Backend의 책임 경계를 정리하겠습니다.

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

## 실전 앵커 모음: API 계약을 운영 문서로 바꾸기

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

### 릴리스 직후 10분 점검표

```text
1) 핵심 경로 3개(목록 조회, 생성, 수정)를 실제 브라우저와 curl 양쪽에서 호출
2) 4xx/5xx 비율, p95 지연 시간, 로그인 성공률을 대시보드에서 확인
3) 최근 배포의 request_id 샘플 5개를 로그에서 역추적해 누락 필드 확인
4) 캐시 적중률과 DB 쿼리 수가 평시 범위를 벗어나는지 확인
```

이 점검표는 큰 도구가 없어도 바로 적용할 수 있는 최소 운영 습관입니다. 릴리스 직후 10분을 구조적으로 사용하면, 사용자 제보보다 먼저 이상 징후를 발견할 확률이 높아집니다.

추가로, 팀 운영 문서에는 장애 발생 시 1차 확인 순서(DNS, HTTP 상태 코드, 인증, 데이터베이스, 캐시)를 한 줄 체크리스트로 고정해 두는 편이 좋습니다. 같은 문제를 다시 만났을 때 대응 시간이 눈에 띄게 줄어듭니다.

## 처음 질문으로 돌아가기

- **클라이언트와 서버는 실제로 무엇을 주고받을까요?**
  - 본문의 기준은 HTTP와 API를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **HTTP 요청과 응답은 어떤 요소로 구성될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **GET, POST, PUT, DELETE는 각각 어떤 의미일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- **HTTP와 API (현재 글)**
- Frontend와 Backend (예정)
- 인증과 세션 (예정)
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [HTTP request methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [HTTP response status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

### 검증용 자료
- [httpbin](https://httpbin.org/)
- [HTTP Semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, HTTP, API, REST, Networking
