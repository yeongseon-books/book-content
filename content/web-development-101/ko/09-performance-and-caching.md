---
series: web-development-101
episode: 9
title: "Web Development 101 (9/10): 성능과 캐싱"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/211"
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

> 성능은 감각이 아니라 측정에서 시작합니다 — 어디가 느린지를 먼저 끊어 읽어야 캐시·CDN·lazy loading·인덱스·N+1 해결 같은 처방이 진단에 맞는 자리로 갑니다.

## 이 글에서 다룰 문제

- 느린 페이지를 만나면 어디서부터 봐야 할까요?
- 브라우저 캐시와 CDN은 각각 어떤 역할을 할까요?
- lazy loading은 무엇을 늦추고 왜 유용할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 성능은 측정부터 시작하는가

빠른 사이트는 사용자 만족뿐 아니라 전환율, 검색 순위, 운영비에도 영향을 줍니다. 하지만 최적화는 감으로 하면 자주 빗나갑니다. 병목이 서버에 있는데 프론트엔드 코드만 만지거나, 이미지가 문제인데 데이터베이스만 의심하는 식입니다.

그래서 성능 작업의 첫 단계는 늘 측정입니다.

## 성능 계층 구조

```
사용자 체감 속도
    |
    v
브라우저 캐시 (가장 빠름)
    |  캐시 없으면 →
    v
CDN (지리적으로 가까운 서버)
    |  CDN 캐시 없으면 →
    v
웹 서버 (애플리케이션)
    |
    +── 애플리케이션 캐시 (Redis, Memcached)
    |   캐시 없으면 →
    +── 데이터베이스 쿼리 (가장 느림)

최적화 원칙: 가장 빠른 계층에서 더 많이 처리
```

## 먼저 알아둘 용어

- **TTFB (Time to First Byte)**: 요청 후 첫 바이트를 받기까지 걸리는 시간입니다.
- **LCP (Largest Contentful Paint)**: 가장 큰 콘텐츠가 화면에 그려지는 시간입니다.
- **HTTP cache**: 브라우저가 응답을 재사용하게 만드는 규칙입니다.
- **CDN**: 전 세계 여러 지점에 콘텐츠를 가까이 두는 프록시 서버 집합입니다.
- **Lazy load**: 필요해질 때까지 리소스 로딩을 미루는 전략입니다.
- **Index**: 데이터베이스가 원하는 행을 빨리 찾게 도와주는 구조입니다.

## 1단계: 측정하기

```
브라우저:
  F12 → Lighthouse 탭 → "Analyze page load" 실행
  → Performance score, LCP, CLS, FID 확인

  F12 → Network 탭
  → Waterfall: 어느 리소스가 얼마나 걸리는지
  → Size 컬럼: 큰 파일 찾기
  → Time 컬럼: 느린 요청 찾기
```

```python
# 서버 측 측정
import time
from flask import Flask, g, request

app = Flask(__name__)

@app.before_request
def start_timer():
    g.start = time.perf_counter()

@app.after_request
def log_timing(response):
    elapsed = time.perf_counter() - g.start
    print(f"{request.method} {request.path} → {response.status_code} ({elapsed*1000:.1f}ms)")
    return response
```

```bash
# curl로 TTFB 측정
curl -w "TTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
  -o /dev/null -s https://example.com
```

## 2단계: HTTP 캐시 헤더

```http
# 정적 자산 (해시된 파일명): 1년 캐시
Cache-Control: public, max-age=31536000, immutable
# → /style.abc123.css 같이 파일명에 해시 포함 시 영구 캐시

# 동적이지만 짧은 시간 캐시 가능한 콘텐츠
Cache-Control: public, max-age=300, stale-while-revalidate=60
# → 5분 동안 유효, 이후 60초 동안은 기존 캐시 제공하면서 백그라운드 갱신

# 사용자별 데이터 (캐시 금지 또는 비공개)
Cache-Control: private, no-store
# → CDN에 저장 안 됨, 브라우저도 저장 안 함

# 조건부 요청 지원 (ETag)
ETag: "v1-abc123"
# → 클라이언트가 If-None-Match: "v1-abc123" 보내면 304 Not Modified 반환
```

```python
# Flask에서 캐시 헤더 설정
from flask import Flask, send_file, make_response

app = Flask(__name__)

@app.after_request
def set_cache_headers(response):
    path = request.path

    # 정적 자산 (파일명에 해시 포함됨)
    if path.startswith("/static/") and any(
        path.endswith(ext) for ext in [".css", ".js", ".png", ".jpg", ".woff2"]
    ):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"

    # API 응답 (개인 데이터)
    elif path.startswith("/api/"):
        response.headers["Cache-Control"] = "private, no-store"

    return response
```

## 3단계: 서버 사이드 캐싱

```python
import time
import sqlite3

# 간단한 인메모리 캐시 (소규모 앱용)
_cache = {}

def get_or_cache(key: str, ttl: int, loader):
    """캐시에 있으면 반환, 없으면 loader 실행 후 저장"""
    entry = _cache.get(key)
    if entry and time.time() - entry["at"] < ttl:
        return entry["data"]

    data = loader()
    _cache[key] = {"data": data, "at": time.time()}
    return data

# 사용 예: 인기 게시물 (1분 캐시)
@app.get("/api/popular-posts")
def popular_posts():
    def fetch():
        con = sqlite3.connect("app.db")
        rows = con.execute(
            "SELECT id, title FROM posts ORDER BY views DESC LIMIT 10"
        ).fetchall()
        return [dict(r) for r in rows]

    posts = get_or_cache("popular_posts", ttl=60, loader=fetch)
    return jsonify(posts)
```

```python
# Redis 사용 (운영 환경)
import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def cached(key: str, ttl: int):
    """데코레이터: 함수 결과를 Redis에 캐시"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            cached_val = r.get(key)
            if cached_val:
                return json.loads(cached_val)
            result = f(*args, **kwargs)
            r.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get("/api/stats")
@cached("site_stats", ttl=300)
def site_stats():
    # 비용 큰 집계 쿼리
    return {"total_users": db.count_users(), "total_posts": db.count_posts()}
```

## 4단계: CDN과 지연 로딩

```html
<!-- 이미지 지연 로딩 -->
<img src="hero.jpg" alt="히어로 이미지" loading="lazy">

<!-- 뷰포트에 처음 나타나는 이미지는 eager (기본값) -->
<img src="logo.png" alt="로고" loading="eager">

<!-- 비디오 지연 로딩 -->
<video preload="none" poster="thumbnail.jpg">
  <source src="video.mp4" type="video/mp4">
</video>

<!-- 폰트: 중요한 것만 preload -->
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>

<!-- CSS: 중요하지 않은 스타일 비동기 로드 -->
<link rel="preload" href="non-critical.css" as="style"
      onload="this.onload=null;this.rel='stylesheet'">
```

```js
// JavaScript 코드 분할 (동적 import)
// 버튼 클릭 시에만 에디터 모듈 로드
document.getElementById("edit-btn").addEventListener("click", async () => {
  const { Editor } = await import("./editor.js");  // 클릭 시 다운로드
  new Editor("#content");
});

// 무한 스크롤: 화면에 보일 때만 로드
const observer = new IntersectionObserver(async (entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      const { loadMore } = await import("./load-more.js");
      await loadMore();
      observer.unobserve(entry.target);
    }
  }
});
observer.observe(document.querySelector("#load-trigger"));
```

## 5단계: DB 성능 최적화

```sql
-- EXPLAIN으로 쿼리 분석
EXPLAIN QUERY PLAN
SELECT * FROM posts WHERE user_id = 1 ORDER BY created_at DESC LIMIT 20;
-- SCAN TABLE posts  (전체 스캔 → 느림)

-- 인덱스 추가
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);

-- 다시 EXPLAIN
EXPLAIN QUERY PLAN
SELECT * FROM posts WHERE user_id = 1 ORDER BY created_at DESC LIMIT 20;
-- SEARCH TABLE posts USING INDEX idx_posts_user_created  (인덱스 사용 → 빠름)
```

```python
# N+1 문제 해결

# 나쁜 예: N+1 쿼리
posts = db.execute("SELECT id, title, user_id FROM posts LIMIT 20").fetchall()
for post in posts:
    # 포스트마다 1번씩, 총 20번 추가 쿼리
    user = db.execute("SELECT username FROM users WHERE id = ?", (post["user_id"],)).fetchone()

# 좋은 예: JOIN으로 1번에 해결
posts_with_users = db.execute("""
    SELECT p.id, p.title, u.username
    FROM posts p
    JOIN users u ON u.id = p.user_id
    ORDER BY p.created_at DESC
    LIMIT 20
""").fetchall()

# 또는 IN 쿼리로 해결
posts = db.execute("SELECT id, title, user_id FROM posts LIMIT 20").fetchall()
user_ids = list({p["user_id"] for p in posts})
users = {u["id"]: u for u in db.execute(
    f"SELECT id, username FROM users WHERE id IN ({','.join('?'*len(user_ids))})",
    user_ids
).fetchall()}
# 총 2번 쿼리로 해결
```

## 성능 측정 지표

```
Core Web Vitals (Google 기준):
  LCP (Largest Contentful Paint):  좋음 < 2.5s, 나쁨 > 4s
  FID (First Input Delay):          좋음 < 100ms, 나쁨 > 300ms
  CLS (Cumulative Layout Shift):    좋음 < 0.1, 나쁨 > 0.25

서버 지표:
  TTFB:       좋음 < 200ms
  p95 응답:   목표 설정 후 모니터링 (예: 500ms 이내)
  오류율:      5xx < 0.1%
```

```bash
# curl로 서버 성능 측정
for i in $(seq 1 10); do
  curl -w "%{time_total}" -o /dev/null -s https://example.com
  echo ""
done | awk '{ sum += $1; count++ } END { print "평균:", sum/count "s" }'
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| 측정 없이 감으로 최적화 | 병목이 아닌 곳에 시간 낭비 | Lighthouse + Network 탭으로 먼저 측정 |
| 모든 응답에 no-cache 설정 | 캐시 이득 전혀 없음 | 데이터 성격에 맞는 캐시 정책 |
| 동적 사용자 응답을 CDN에 캐시 | 사용자별 데이터 혼용 | private 또는 no-store 설정 |
| 모든 컬럼에 인덱스 추가 | INSERT/UPDATE 성능 저하 | 조회 패턴 확인 후 선택적 추가 |
| 캐시 무효화 전략 없이 캐시 적용 | 오래된 데이터 계속 서빙 | TTL 설정 + 변경 시 명시적 무효화 |
| N+1 쿼리를 ORM이 숨김 | 트래픽 증가 시 갑자기 느려짐 | SQL 로그 켜서 쿼리 수 확인 |

## 직접 검증해 볼 포인트

```bash
# 1. 캐시 헤더 확인
curl -I https://example.com
# Cache-Control, ETag 헤더 확인

# 2. 두 번째 요청에서 304 반환 확인
curl -I -H "If-None-Match: \"etag-value\"" https://example.com

# 3. 이미지 크기 확인
curl -o /dev/null -s -w "%{size_download}" https://example.com/image.jpg
```

```
Lighthouse 실행 결과 읽기:
  - Performance score가 낮으면 Opportunities 섹션 확인
  - "Reduce unused JavaScript": JS 코드 분할 검토
  - "Serve images in next-gen formats": WebP/AVIF 변환
  - "Eliminate render-blocking resources": defer/async 적용
  - "Properly size images": 화면 크기에 맞는 이미지 제공
```

## 운영에서는 이렇게 보입니다

큰 서비스는 보통 브라우저 캐시, CDN, 애플리케이션 캐시, 데이터베이스라는 여러 층의 캐시를 함께 씁니다. 실무에서는 기능 설계와 캐시 전략 설계를 동시에 하는 팀이 강합니다. 어떤 데이터가 얼마나 자주 바뀌는지, 어디까지 오래 들고 갈 수 있는지를 먼저 생각하기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 측정, 가설, 실험의 루프를 돌립니다.
- 캐시는 TTL과 invalidation key를 함께 설계합니다.
- 사용자와 가장 가까운 층부터 캐시합니다.
- 인덱스는 `EXPLAIN`으로 검증합니다.
- 평균보다 p95, p99를 더 자주 봅니다.

## 운영 체크리스트

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
- **Web Development 101 (9/10): 성능과 캐싱 (현재 글)**
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

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
