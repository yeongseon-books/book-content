---
series: web-development-101
episode: 9
title: "바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - 성능
  - 캐싱
  - CDN
  - 최적화
seo_description: 바이브코딩으로 만든 웹앱이 느릴 때 어디서부터 보고 어떻게 개선하는지 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 아홉 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

바이브코딩으로 앱을 만들다 보면 "왜 이렇게 느리지?"라는 순간이 옵니다. 그때 막연하게 "최적화해줘"라고 AI에게 물어보면 다양한 답변이 나오는데, 어떤 것이 내 상황에 맞는지 판단하기 어렵습니다. 성능 문제는 어디가 느린지 먼저 파악해야 올바른 처방이 가능합니다.

서버가 느린지, 브라우저가 느린지, 이미지가 너무 큰지, 데이터베이스 조회가 매번 일어나는지 구분하지 않으면 최적화는 방향을 잃습니다. 브라우저 측 문제인데 서버를 최적화하거나, 캐시로 해결될 문제를 데이터베이스 인덱스로 접근하는 실수가 생깁니다.

이 글에서는 성능 문제를 진단하는 방법, HTTP 캐시와 CDN, lazy loading, 데이터베이스 인덱스와 N+1 문제를 바이브코딩 관점에서 정리합니다.

> 성능은 감각이 아니라 측정에서 시작합니다. 바이브코딩 중 "느리다"는 문제를 AI에게 전달할 때 어느 층이 병목인지 함께 알려야 정확한 해결책을 받을 수 있습니다.

## 이 글에서 다룰 문제

- 느린 페이지를 만나면 어디서부터 봐야 할까요?
- 브라우저 캐시와 CDN은 각각 어떤 역할을 할까요?
- lazy loading은 무엇을 늦추고 왜 유용할까요?
- N+1 문제란 무엇이고 어떻게 발견할까요?
- 바이브코딩 중 성능 문제를 어떻게 진단할까요?

## 바이브코딩 관점: 성능을 알아야 하는 이유

AI에게 "앱이 너무 느려요"라고만 하면 다양한 최적화 방법이 나오지만, 병목이 어디인지 모르는 상태에서는 맞는 처방을 골라낼 수 없습니다. "Lighthouse 점수가 40점이고, 가장 큰 병목이 이미지 로딩인 것 같아요"처럼 구체적인 정보를 주면 AI가 정확하게 이미지 최적화, lazy loading, CDN 설정을 제안합니다.

또한 AI가 생성한 코드에서 흔히 보이는 N+1 문제를 알아야 합니다. ORM을 쓸 때 반복문 안에서 추가 쿼리가 나가는 패턴은, 데이터가 적을 때는 괜찮지만 사용자가 늘면 앱이 급격히 느려지는 원인이 됩니다.

## 먼저 알아둘 용어

- **TTFB**: 첫 바이트가 도착하기까지 걸리는 시간입니다.
- **HTTP cache**: 브라우저가 응답을 재사용하게 만드는 규칙입니다.
- **CDN**: 전 세계 여러 지점에 콘텐츠를 가까이 두는 프록시 서버 집합입니다.
- **Lazy load**: 필요해질 때까지 리소스 로딩을 미루는 전략입니다.
- **N+1 problem**: 1번의 조회에서 N개의 추가 조회가 발생하는 비효율 패턴입니다.

## Before / After: 캐시를 적용한 API

**Before — 매 요청마다 DB 조회**

```python
@app.get("/popular")
def popular():
    return db.fetch("SELECT * FROM posts ORDER BY views DESC LIMIT 10")
# 초당 100개 요청이 오면 초당 100번 DB 조회
```

**After — 1분간 캐시**

```python
import time
_cache = {"at": 0, "data": None}

@app.get("/popular")
def popular():
    if time.time() - _cache["at"] > 60:
        _cache["data"] = db.fetch("SELECT * FROM posts ORDER BY views DESC LIMIT 10")
        _cache["at"] = time.time()
    return _cache["data"]
# 1분에 1번만 DB 조회
```

자주 읽히고 자주 바뀌지 않는 데이터는 캐시의 좋은 후보입니다.

## 성능 개선을 다섯 단계로 적용해 보기

### 1단계 — 먼저 측정하기

```text
브라우저: F12 → Lighthouse 또는 Performance 탭
서버: time.perf_counter() 또는 APM 도구
```

브라우저와 서버 양쪽을 함께 봐야 합니다.

### 2단계 — 정적 파일에 캐시 헤더 붙이기

```python
@app.after_request
def add_cache(resp):
    if resp.mimetype.startswith(("image/", "text/css")):
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp
```

### 3단계 — CDN 추가하기

```text
Cloudflare, CloudFront, Fastly 등을 앞단에 두면
정적 자산이 사용자에게 더 가까운 위치에서 제공됩니다
```

### 4단계 — lazy loading 적용하기

```html
<img src="big.jpg" loading="lazy" alt="...">
```

```js
button.onclick = async () => {
  const mod = await import("./editor.js");
  mod.open();
};
```

### 5단계 — N+1 문제 발견하고 수정하기

```python
# N+1 문제 (나쁜 예)
for post in posts:
    print(post.author.name)  # 루프마다 SELECT 실행

# JOIN으로 해결 (좋은 예)
posts = db.fetch("""
    SELECT p.*, u.name
    FROM posts p
    JOIN users u ON u.id = p.user_id
""")
```

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| 측정 없이 최적화 시도 | 진단 없는 처방 | Lighthouse로 먼저 측정, 병목 파악 후 최적화 |
| 모든 응답에 `no-cache` | 캐시 이득 포기 | 정적 자산에는 장기 캐시, 동적 데이터만 제한 |
| ORM 반복문 안에서 추가 조회 | N+1 모름 | JOIN 또는 eager loading으로 한 번에 조회 |
| 인덱스 없이 큰 테이블 조회 | 인덱스 모름 | 자주 조회하는 컬럼에 인덱스 추가 |
| 사용자 응답을 CDN에 캐시 | 캐시 정책 혼동 | 사용자별 데이터는 `private` 또는 `no-store` |

## AI 팁: 성능 문제 진단 요청 방법

```
"앱이 느린 것 같습니다. Lighthouse 점수는 다음과 같습니다:
- Performance: 45
- 가장 큰 문제: LCP 8.2s (큰 이미지 때문)
- 두 번째 문제: 초기 JS 번들이 2MB

이 두 문제를 해결하는 방법을 알려주세요."
```

측정 결과를 포함하면 AI가 실제 병목에 맞는 해결책을 제시합니다.

## 체크리스트

- [ ] Lighthouse를 최소 한 번 실행해 봤습니다.
- [ ] 정적 자산에 `Cache-Control`이 붙어 있습니다.
- [ ] N+1 문제가 무엇인지 알고 있습니다.
- [ ] 데이터베이스 인덱스를 하나 이상 만들어 봤습니다.
- [ ] 브라우저 캐시와 서버 캐시의 차이를 설명할 수 있습니다.

## 처음 질문으로 돌아가기

- **느린 페이지를 만나면 어디서부터 봐야 할까요?**
  먼저 Lighthouse나 DevTools Performance 탭으로 측정합니다. 브라우저가 느린지(큰 이미지, 많은 JS), 서버가 느린지(TTFB), 데이터베이스가 느린지(쿼리 시간)를 구분합니다.

- **브라우저 캐시와 CDN은 각각 어떤 역할을 할까요?**
  브라우저 캐시는 같은 사용자가 재방문할 때 다운로드를 건너뜁니다. CDN은 모든 사용자에게 지리적으로 가까운 서버에서 파일을 제공해 속도를 높입니다.

- **N+1 문제란 무엇이고 어떻게 발견할까요?**
  1개 조회 후 N개 추가 조회가 루프 안에서 발생하는 패턴입니다. ORM의 SQL 로그를 켜거나 APM 도구로 쿼리 수를 모니터링해 발견합니다.

## 정리

성능은 측정 없이 최적화할 수 없습니다. 바이브코딩으로 만든 앱이 느리다면, AI에게 막연하게 물어보기 전에 Lighthouse 결과, 느린 API 응답 시간, N+1 쿼리 로그 같은 측정 데이터를 먼저 모아야 합니다. 데이터가 있어야 AI와의 대화도 정확해집니다. 다음 글에서는 이 시리즈에서 배운 모든 것을 하나의 작은 앱으로 묶어 봅니다.

## 참고 자료

- [HTTP caching (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [Lazy loading (MDN)](https://developer.mozilla.org/en-US/docs/Web/Performance/Lazy_loading)
- [Lighthouse overview (Chrome)](https://developer.chrome.com/docs/lighthouse/overview)
- [Web performance metrics (web.dev)](https://web.dev/explore/metrics)

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
- **바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱 (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, 성능, 캐싱, CDN, 최적화
