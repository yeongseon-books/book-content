---
series: web-development-101
episode: 9
title: "Web Development 101 (9/10): 성능과 캐싱"
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
  - Performance
  - Caching
  - CDN
  - Optimization
seo_description: 측정, HTTP 캐시, CDN, 지연 로딩, DB 인덱스로 성능을 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (9/10): 성능과 캐싱

서비스가 느리다는 말은 흔하지만, 어디가 느린지는 생각보다 자주 흐립니다. 서버가 느린지, 브라우저가 느린지, 이미지가 큰지, 데이터베이스 조회가 많은지, 캐시가 전혀 없는지 구분하지 않으면 최적화는 방향을 잃습니다. 성능은 감각보다 측정과 구조가 먼저입니다.

이 글은 Web Development 101 시리즈의 9번째 글입니다.

여기서는 측정의 출발점, HTTP 캐시와 CDN, lazy loading과 code splitting, 데이터베이스 인덱스와 N+1 문제를 함께 보며 느린 웹앱을 빠르게 만드는 기본 원칙을 정리하겠습니다.

![Web Development 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/09/09-01-concept-at-a-glance.ko.png)
*Web Development 101 9장 흐름 개요*

## 먼저 던지는 질문

- 느린 페이지를 만나면 어디서부터 봐야 할까요?
- 브라우저 캐시와 CDN은 각각 어떤 역할을 할까요?
- lazy loading은 무엇을 늦추고 왜 유용할까요?

## 왜 성능은 측정부터 시작하는가

빠른 사이트는 사용자 만족뿐 아니라 전환율, 검색 순위, 운영비에도 영향을 줍니다. 하지만 최적화는 감으로 하면 자주 빗나갑니다. 병목이 서버에 있는데 프론트엔드 코드만 만지거나, 이미지가 문제인데 데이터베이스만 의심하는 식입니다.

그래서 성능 작업의 첫 단계는 늘 측정입니다. 브라우저 기준 지표와 서버 기준 지표를 함께 보고, 어느 층에서 시간이 쓰이는지 확인해야 다음 결정이 맞아집니다.

## 한눈에 보는 개념 지도

같은 데이터를 더 가까운 계층에서 더 적게 계산할수록 응답은 빨라집니다. 그래서 브라우저 캐시, CDN, 애플리케이션 캐시, 데이터베이스 최적화는 경쟁 관계가 아니라 서로 다른 층의 협업입니다.

### 직접 검증해 볼 포인트

- Lighthouse나 Performance 탭으로 첫 측정치를 먼저 남깁니다.
- 정적 파일에 `Cache-Control`을 붙인 뒤 두 번째 요청에서 전송 크기와 응답 시간이 줄어드는지 봅니다.
- 인덱스 추가 전후 또는 join 적용 전후 쿼리 시간을 비교합니다.

**기대 결과:** 캐시가 적용된 정적 파일은 재요청 비용이 크게 줄고, 인덱스나 join 개선 뒤 데이터베이스 응답 시간이 눈에 띄게 낮아집니다.

**실패 모드:** 동적 사용자 응답을 잘못 캐시하면 데이터가 섞일 수 있습니다. 측정 없이 최적화하면 가장 느린 구간이 아닌 곳에 시간을 쓰기 쉽습니다.

## 먼저 알아둘 용어

- **TTFB**: 첫 바이트가 도착하기까지 걸리는 시간입니다.
- **HTTP cache**: 브라우저가 응답을 재사용하게 만드는 규칙입니다.
- **CDN**: 전 세계 여러 지점에 콘텐츠를 가까이 두는 프록시 서버 집합입니다.
- **Lazy load**: 필요해질 때까지 리소스 로딩을 미루는 전략입니다.
- **Index**: 데이터베이스가 원하는 행을 빨리 찾게 도와주는 구조입니다.

## 전후 비교로 보는 캐시 효과

**Before (DB on every request)**

```python
@app.get("/popular")
def popular():
    return db.fetch("SELECT * FROM posts ORDER BY views DESC LIMIT 10")
```

**After (1분간 캐시)**

```python
import time
_cache = {"at": 0, "data": None}
@app.get("/popular")
def popular():
    if time.time() - _cache["at"] > 60:
        _cache["data"] = db.fetch("SELECT * FROM posts ORDER BY views DESC LIMIT 10")
        _cache["at"] = time.time()
    return _cache["data"]
```

같은 결과를 반복해서 줄 때는 매번 데이터베이스를 치지 않는 편이 훨씬 낫습니다. 인기 목록처럼 자주 읽히고 자주 바뀌지 않는 데이터는 캐시의 좋은 후보입니다.

## 성능 개선을 다섯 단계로 적용해 보기

### 1단계 — 먼저 측정하기

```text
브라우저: F12 → Lighthouse 또는 Performance 탭
서버: time.perf_counter() 또는 APM (Datadog, New Relic)
```

브라우저와 서버 양쪽을 함께 봐야 합니다. 첫 화면이 느린데 서버는 빠를 수도 있고, 반대로 브라우저는 가벼운데 서버 TTFB가 긴 경우도 있습니다.

### 2단계 — 정적 파일에 캐시 헤더 붙이기

```python
# Flask
@app.after_request
def add_cache(resp):
    if resp.mimetype.startswith(("image/", "text/css")):
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp
```

이미지와 CSS처럼 자주 바뀌지 않는 파일은 브라우저 캐시를 적극 활용하는 편이 좋습니다. 다시 내려받지 않아도 되면 첫 화면도 빨라지고 서버 부하도 줄어듭니다.

### 3단계 — CDN 추가하기

```text
Cloudflare/Fastly/CloudFront를 앞단에 두면
정적 자산이 여러 대륙의 사용자에게 더 가까워집니다.
```

CDN은 정적 자산에 특히 효과가 큽니다. 사용자의 물리적 거리 자체를 줄여 주기 때문입니다.

### 4단계 — 지연 로딩 적용하기

```html
<img src="big.jpg" loading="lazy" alt="...">
```

```js
// JS 코드 분할(동적 가져오기)
button.onclick = async () => {
  const mod = await import("./editor.js");
  mod.open();
};
```

처음부터 필요 없는 이미지와 코드라면 나중에 가져오는 편이 낫습니다. 초기 다운로드 크기를 줄이는 것만으로도 체감 속도가 좋아질 수 있습니다.

### 5단계 — DB 인덱스와 N+1 문제 보기

```sql
CREATE INDEX idx_posts_views ON posts(views DESC);
```

```python
# N+1 (bad)
for p in posts: print(p.author.name)  # SELECT every loop

# join (good)
posts = db.fetch("SELECT p.*, u.name FROM posts p JOIN users u ON u.id = p.user_id")
```

캐시만으로 해결되지 않는 병목은 데이터베이스에서 자주 나옵니다. 어떤 컬럼으로 조회하는지, 반복해서 추가 쿼리가 나가는지 확인해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- 캐시에는 수명과 무효화 전략이 함께 있어야 합니다.
- CDN은 정적 자산에서 가장 큰 효과를 냅니다.
- 인덱스는 아무 컬럼에나 거는 것이 아니라 실제 조회 패턴을 따라가야 합니다.

## 여기서 자주 헷갈립니다

1. **느릴 것 같다는 감으로 최적화하는 경우**: 병목이 전혀 다른 곳일 수 있습니다.
2. **모든 응답에 `no-cache`를 붙이는 경우**: 얻을 수 있는 캐시 이득을 버립니다.
3. **동적 사용자 응답을 CDN에 캐시하는 경우**: 사용자별 데이터가 섞일 수 있습니다.
4. **모든 컬럼에 인덱스를 다는 경우**: 쓰기 성능이 떨어집니다.
5. **N+1 모니터링 없이 ORM만 믿는 경우**: 트래픽이 늘면서 조용히 느려집니다.

## 운영에서는 이렇게 보입니다

큰 서비스는 보통 브라우저 캐시, CDN, 애플리케이션 캐시, 데이터베이스라는 여러 층의 캐시를 함께 씁니다. 실무에서는 기능 설계와 캐시 전략 설계를 동시에 하는 팀이 강합니다. 어떤 데이터가 얼마나 자주 바뀌는지, 어디까지 오래 들고 갈 수 있는지를 먼저 생각하기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 측정, 가설, 실험의 루프를 돌립니다.
- 캐시는 TTL과 invalidation key를 함께 설계합니다.
- 사용자와 가장 가까운 층부터 캐시합니다.
- 인덱스는 `EXPLAIN`으로 검증합니다.
- 평균보다 p95, p99를 더 자주 봅니다.

## 체크리스트

- [ ] Lighthouse를 최소 한 번 실행해 봤습니다.
- [ ] 정적 자산에 `Cache-Control`이 붙어 있습니다.
- [ ] 정적 자산 앞단에 CDN을 둘 수 있음을 이해했습니다.
- [ ] N+1 query를 찾는 방법을 알고 있습니다.
- [ ] 데이터베이스 인덱스를 하나 이상 만들어 봤습니다.

## 연습 문제

1. 엔드포인트 하나를 골라 캐시 전후 응답 시간을 측정해 보세요.
2. `<img loading="lazy">` 적용 전후로 페이지 로드 체감을 비교해 보세요.
3. N+1 query를 재현한 뒤 하나의 join SQL로 바꿔 보세요.

## 정리와 다음 글

성능은 감으로 고치는 분야가 아닙니다. 측정하고, 캐시하고, 줄이고, 늦추는 방식으로 같은 일을 더 적게 하게 만들어야 합니다. 다음 글에서는 이 시리즈에서 배운 개념을 하나로 묶어 작은 웹앱을 끝까지 만들어 보겠습니다.

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

## 실전 앵커 모음: 성능 예산을 운영 문서로 바꾸기

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

- **느린 페이지를 만나면 어디서부터 봐야 할까요?**
  - 가장 먼저 해야 할 일은 최적화가 아니라 측정입니다. 글에서 Lighthouse·Performance 탭과 `time.perf_counter()` 또는 APM을 함께 보라고 한 이유는, 첫 화면 병목이 브라우저인지 서버 TTFB인지 데이터베이스 조회인지 먼저 갈라야 하기 때문입니다.
- **브라우저 캐시와 CDN은 각각 어떤 역할을 할까요?**
  - 브라우저 캐시는 `Cache-Control: public, max-age=31536000, immutable`처럼 응답을 재사용하게 만들어 같은 CSS와 이미지를 다시 내려받지 않게 합니다. CDN은 그 정적 자산을 사용자와 더 가까운 지점에 두어 전송 거리 자체를 줄이는 역할을 합니다.
- **lazy loading은 무엇을 늦추고 왜 유용할까요?**
  - `loading="lazy"`가 붙은 이미지와 `await import("./editor.js")` 같은 동적 import는 처음부터 꼭 필요하지 않은 리소스의 로딩 시점을 뒤로 미룹니다. 이렇게 초기 다운로드 크기를 줄이면 첫 화면 체감 속도가 좋아지고, 사용자가 실제로 필요로 할 때만 비용을 지불하게 됩니다.

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
- **성능과 캐싱 (현재 글)**
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [HTTP caching (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [Lazy loading (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Lazy_loading)
- [Lighthouse overview (Chrome)](https://developer.chrome.com/docs/lighthouse/overview)

### 검증용 자료
- [Web performance metrics (web.dev)](https://web.dev/explore/metrics)
- [Use The Index, Luke!](https://use-the-index-luke.com/)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, Performance, Caching, CDN, Optimization
