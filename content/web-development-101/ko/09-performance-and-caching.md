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

이 글은 Web Development 101 시리즈의 아홉 번째 글입니다. 여기서는 측정의 출발점, HTTP 캐시와 CDN, lazy loading과 code splitting, 데이터베이스 인덱스와 N+1 문제를 함께 보며 느린 웹앱을 빠르게 만드는 기본 원칙을 정리하겠습니다.

## 먼저 던지는 질문

- 느린 페이지를 만나면 어디서부터 봐야 할까요?
- 브라우저 캐시와 CDN은 각각 어떤 역할을 할까요?
- lazy loading은 무엇을 늦추고 왜 유용할까요?

## 큰 그림

![Web Development 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/09/09-01-concept-at-a-glance.ko.png)

*Web Development 101 9장 흐름 개요*

이 그림에서는 성능과 캐싱를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 성능과 캐싱의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## Before / After로 보는 캐시 효과

**Before (DB on every request)**

```python
@app.get("/popular")
def popular():
    return db.fetch("SELECT * FROM posts ORDER BY views DESC LIMIT 10")
```

**After (cache for 1 minute)**

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
// JS code splitting (dynamic import)
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

## 처음 질문으로 돌아가기

- **느린 페이지를 만나면 어디서부터 봐야 할까요?**
  - 본문의 기준은 성능과 캐싱를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **브라우저 캐시와 CDN은 각각 어떤 역할을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **lazy loading은 무엇을 늦추고 왜 유용할까요?**
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

Tags: Computer Science, WebDevelopment, Performance, Caching, CDN, Optimization
