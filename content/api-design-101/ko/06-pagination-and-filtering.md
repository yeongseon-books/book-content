---
series: api-design-101
episode: 6
title: Pagination과 filtering
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - APIDesign
  - Pagination
  - Filtering
  - Performance
  - Backend
seo_description: offset/limit과 cursor 페이지네이션, 정렬과 필터링의 표준 패턴을 정리합니다.
last_reviewed: '2026-05-04'
---

# Pagination과 filtering

> API Design 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 큰 컬렉션을 *조각으로* 돌려줄 때, 안전하고 빠른 방법은 무엇일까요?

> 정답은 데이터의 *변화 속도* 가 결정합니다 — 정적이면 offset, 빠르게 변하면 cursor.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- offset / limit 페이지네이션의 한계
- cursor 기반 페이지네이션
- 정렬(sort), 필터(filter), 검색(search)
- 응답 메타와 링크 헤더
- 큰 결과셋의 성능 함정

## 왜 중요한가

페이지네이션이 잘못되면 *느린 쿼리* 와 *중복·누락* 이 동시에 옵니다. 그리고 한 번 외부에 나가면 쉽게 못 바꿉니다 — 처음부터 의도가 있어야 합니다.

> 큰 컬렉션은 *반드시* 조각으로.

## 개념 한눈에 보기

```mermaid
flowchart LR
    A["?limit=20"] --> P1["page 1 + next_cursor"]
    P1 --> A2["?limit=20&cursor=..."]
    A2 --> P2["page 2 + next_cursor"]
```

cursor는 *다음 페이지의 시작점* 입니다.

## 핵심 용어 정리

- **Offset/Limit**: `?offset=40&limit=20` — 단순하지만 *깊을수록* 느림.
- **Cursor**: 마지막 항목의 정렬 키를 *불투명* 하게 인코딩.
- **Total count**: 전체 개수 — 큰 테이블에선 *비쌉니다*.
- **Sort**: `?sort=created_at:desc`.
- **Filter**: `?status=active&tier=pro`.

## Before/After

**Before (정렬·필터·페이지가 뒤엉킴)**

```
GET /orders?p=3&s=date&q=paid
```

**After (이름·표준·메타)**

```
GET /orders?status=paid&sort=created_at:desc&limit=20&cursor=eyJpZCI6MTIzfQ
```

## 실습: Pagination 5단계

### 1단계 — offset/limit

```python
# 1_offset.py
from flask import Flask, request, jsonify
app = Flask(__name__)
ITEMS = list(range(1000))

@app.get("/items")
def items():
    offset = int(request.args.get("offset", 0))
    limit = min(int(request.args.get("limit", 20)), 100)
    return jsonify(items=ITEMS[offset:offset+limit], total=len(ITEMS))
```

`limit` 에는 *상한* 을 둡니다.

### 2단계 — cursor

```python
# 2_cursor.py
from flask import Flask, request, jsonify
app = Flask(__name__)
ITEMS = list(range(1000))

@app.get("/items")
def items():
    cursor = int(request.args.get("cursor", 0))
    limit = min(int(request.args.get("limit", 20)), 100)
    page = ITEMS[cursor:cursor+limit]
    nxt = cursor + len(page)
    return jsonify(items=page, next_cursor=(nxt if nxt < len(ITEMS) else None))
```

cursor는 *불투명* 하게 — 클라이언트가 해석하지 않습니다.

### 3단계 — 정렬

```
GET /items?sort=created_at:desc
GET /items?sort=name:asc,id:desc
```

여러 키 조합도 표준화합니다.

### 4단계 — 필터

```
GET /orders?status=paid&tier=pro
GET /orders?created_at__gte=2026-01-01
```

연산자는 `__gte`, `__lt` 같은 명시적 접미사로.

### 5단계 — 검색

```
GET /articles?q=python+logging
```

검색은 *별도 파라미터* `q` 로 분리 — 필터와 섞지 않습니다.

## 이 코드에서 주목할 점

- `limit` 에 *상한* 이 있어야 합니다.
- cursor는 *불투명한 토큰*.
- 정렬·필터·검색은 *각각 다른 의미* — 같은 파라미터에 섞지 않음.

## 자주 하는 실수 5가지

1. **`limit` 상한 없음.** 클라이언트가 10만개를 한 번에 요청.
2. **deep offset.** `offset=100000` 은 인덱스가 있어도 *느림*.
3. **total count 항상 계산.** 큰 테이블에서 *주범*.
4. **필터·정렬·검색 한 파라미터에.** 검증·문서화 모두 어려움.
5. **cursor 의 *내용* 노출.** 클라이언트가 위조해 데이터를 빼냄.

## 실무에서는 이렇게 쓰입니다

GitHub은 `Link` 헤더로 next/prev URL을 *돌려줍니다*. Twitter·Slack 같은 빠르게 변하는 데이터는 cursor 기반이 표준. Stripe는 `has_more` + `data[].id` 로 단순한 cursor를 노출합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 새 컬렉션은 *기본 cursor*, 작은 정적 컬렉션만 offset.
- `limit` 의 기본값과 상한을 *문서* 에 명시.
- total은 *옵션* 으로 — 비싸면 빼는 선택을.
- 필터의 가능한 값을 enum 으로 *문서화*.
- 검색은 *별도 endpoint* 로 분리하는 것을 고려.

## 체크리스트

- [ ] `limit` 에 상한이 있는가?
- [ ] cursor가 불투명한가?
- [ ] 정렬·필터·검색이 각자 다른 파라미터인가?
- [ ] 응답에 *다음 페이지* 링크 또는 cursor가 있는가?
- [ ] total count가 *비용 인식* 후 결정되었는가?

## 연습 문제

1. 자신의 list endpoint를 *cursor* 기반으로 다시 설계해 보세요.
2. 위 1단계에 `limit` 상한 100을 강제하세요.
3. 검색을 별도 endpoint로 분리할지, 같은 endpoint의 `q` 로 둘지 — 두 안의 장단점을 정리하세요.

## 정리 및 다음 단계

페이지네이션은 *성능과 정확성* 의 교차점입니다. 다음 글에서는 컬렉션이든 단일 자원이든 빠질 수 없는 — error response 설계 — 를 봅니다.

<!-- toc:begin -->
- [API란 무엇인가?](./01-what-is-an-api.md)
- [REST 기본](./02-rest-basics.md)
- [리소스 설계](./03-resource-design.md)
- [HTTP method와 status code](./04-http-methods-and-status.md)
- [Request와 response schema](./05-request-and-response-schema.md)
- **Pagination과 filtering (현재 글)**
- Error response 설계 (예정)
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Stripe API: Pagination](https://stripe.com/docs/api/pagination)
- [GitHub REST API: Using Pagination](https://docs.github.com/en/rest/guides/using-pagination-in-the-rest-api)
- [Slack API: Cursor-based Pagination](https://api.slack.com/docs/pagination)
- [RFC 5988 — Web Linking (Link header)](https://www.rfc-editor.org/rfc/rfc5988)

Tags: Computer Science, APIDesign, Pagination, Filtering, Performance, Backend
