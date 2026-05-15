---
title: Versioning
series: api-design-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Computer Science
  - APIDesign
  - Versioning
  - Compatibility
  - Deprecation
  - Backend
last_reviewed: '2026-05-12'
seo_description: API versioning의 기준, 호환성 정책, sunset 절차를 실무적으로 설명합니다.
---

# Versioning

이 글은 API Design 101 시리즈의 아홉 번째 글입니다. versioning은 URL에 `/v1`을 붙이는 문제만이 아닙니다. 먼저 어떤 변화가 breaking인지 정의하고, 그다음 그 변화를 어떤 채널로 노출할지 분리해서 생각해야 합니다.

## 이 글에서 다룰 문제

- breaking change와 non-breaking change는 어떻게 구분할까요?
- URL versioning과 header versioning은 각각 어떤 장단점이 있을까요?
- semver, calver 같은 호환성 정책은 어떻게 읽어야 할까요?
- deprecation 공지와 sunset 절차는 어떻게 운영해야 할까요?
- 여러 버전을 동시에 유지하는 비용은 무엇일까요?

## 왜 중요한가

외부 클라이언트는 API 계약에 의존합니다. 한 번의 breaking change가 수십, 수백 개의 클라이언트를 동시에 멈출 수 있습니다. 좋은 versioning은 바꾸지 않는 기술이 아니라, 규율 있게 바꿀 자유를 확보하는 기술입니다.

> 호환성은 공짜가 아닙니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    V1["/v1/users"] --> H1["v1 handler"]
    V2["/v2/users"] --> H2["v2 handler"]
    H1 -.deprecated.-> Sunset["sunset 2027-01"]
```

## 핵심 용어

- **Breaking change**: 기존 클라이언트가 수정 없이 계속 동작할 수 없는 변경입니다.
- **Non-breaking change**: 새 필드 추가나 새 endpoint 추가처럼 대체로 안전한 변경입니다.
- **URL versioning**: `/v1/...`, `/v2/...`처럼 경로에 버전을 넣는 방식입니다.
- **Header versioning**: `X-API-Version`이나 `Accept` header로 버전을 전달하는 방식입니다.
- **Sunset**: 특정 버전의 공식 종료 시점입니다.

## Before / After

**Before (조용히 깨짐)**

```text
PATCH /users/42  → response date format changes one day
```

**After (버전이 명시됨)**

```
PATCH /v2/users/42
Sunset: Wed, 31 Jan 2027 23:59:59 GMT  (set on v1 responses)
```

## 실습: versioning을 운영하는 다섯 단계

### Step 1 — URL versioning

```python
# 1_url.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/v1/users/<int:uid>")
def v1(uid): return jsonify(id=uid, name="Y")

@app.get("/v2/users/<int:uid>")
def v2(uid): return jsonify(id=uid, full_name="Y", username="y")
```

가장 직관적인 방식이라 라우팅, 로그, 캐시 추적이 단순합니다.

### Step 2 — Header versioning

```python
# 2_header.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.get("/users/<int:uid>")
def user(uid):
    v = request.headers.get("X-API-Version", "1")
    return jsonify(id=uid, name="Y") if v == "1" else jsonify(id=uid, full_name="Y")
```

URL이 깔끔해지는 대신 디버깅과 캐시 전략이 더 어려워집니다.

### Step 3 — Non-breaking additions

```text
Add a new field to a response → non-breaking (if clients can ignore it)
Add an *optional* field to a request → non-breaking
```

필드 추가는 대체로 안전하지만, 클라이언트가 unknown field를 무시할 수 있다는 전제가 필요합니다.

### Step 4 — Deprecation notice

```python
# 4_deprecate.py
@app.get("/v1/users/<int:uid>")
def v1(uid):
    resp = jsonify(id=uid, name="Y")
    resp.headers["Deprecation"] = "true"
    resp.headers["Sunset"] = "Wed, 31 Jan 2027 23:59:59 GMT"
    resp.headers["Link"] = '</v2/users>; rel="successor-version"'
    return resp
```

표준 header는 조용하지만 분명한 신호를 보냅니다. release note와 함께 써야 효과가 큽니다.

### Step 5 — Sunset procedure

```
1. Ship the new version + start sending Deprecation
2. Monitor usage (identify clients)
3. Announce sunset 6-12 months out by email
4. Simulate 410 Gone for 30 days before sunset
5. Sunset — return 410 Gone or 308 Permanent Redirect
```

버전 종료는 하루아침에 처리할 작업이 아니라 관찰, 공지, 유예, 종료가 이어지는 절차입니다.

## 이 코드에서 봐야 할 점

- 서로 다른 버전이 동시에 공존합니다.
- 공지는 header, 문서, 이메일이 함께 움직여야 합니다.
- sunset에는 명확한 날짜가 있어야 합니다.

## 자주 하는 실수 다섯 가지

1. **버전 없이 배포합니다.** 외부 클라이언트가 깨져도 원인을 추적하기 어렵습니다.
2. **모든 변경을 breaking으로 취급합니다.** v3, v4가 너무 자주 생겨 운영 비용이 폭증합니다.
3. **예고 없이 버전을 종료합니다.** 신뢰를 잃습니다.
4. **모든 버전을 영원히 유지합니다.** 코드가 지층처럼 쌓입니다.
5. **한 handler 안에 버전 분기를 전부 넣습니다.** 유지보수가 급격히 어려워집니다.

## 실무에서는 이렇게 드러납니다

Stripe는 `Stripe-Version: 2024-04-10`처럼 날짜 기반 versioning을 header로 운용합니다. GitHub는 URL과 `X-GitHub-Api-Version`을 함께 씁니다. AWS는 거의 모든 API를 명시적으로 버전 관리하고, 호환성도 매우 오래 유지하는 편입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 무엇을 breaking으로 볼지 호환성 정책부터 문서화합니다.
- 대부분의 변경은 additive하게 처리하고 새 major 버전은 드물게 만듭니다.
- 표준 header와 명시적 sunset 날짜를 함께 사용합니다.
- 여러 버전을 유지하는 내부 비용을 숫자로 계산합니다.
- 실제 사용량이 충분히 줄어든 뒤에만 sunset합니다.

## 체크리스트

- [ ] 호환성 정책이 문서화되어 있는가?
- [ ] 버전 채널(URL 또는 header)이 일관적인가?
- [ ] deprecation header와 sunset 날짜가 설정되어 있는가?
- [ ] 클라이언트별 사용량을 추적하는가?
- [ ] 동시에 살아 있는 버전 수에 상한이 있는가?

## 연습 문제

1. 최근 API 변경 다섯 개를 골라 breaking / non-breaking으로 분류해 보세요.
2. Step 4 예제에 v1 사용 시 warning log를 남기도록 코드를 추가해 보세요.
3. 자신의 상황에서 URL versioning과 header versioning 중 무엇이 더 나은지 trade-off를 적어 보세요.

## 정리와 다음 글

versioning은 계약과 변경을 함께 다루는 기술입니다. 마지막 글에서는 그 모든 약속을 사람에게 읽히게 만드는 API 문서 작성 원칙을 다룹니다.

<!-- toc:begin -->
- [API란 무엇인가?](./01-what-is-an-api.md)
- [REST 기본](./02-rest-basics.md)
- [리소스 설계](./03-resource-design.md)
- [HTTP method와 status code](./04-http-methods-and-status.md)
- [Request와 response schema](./05-request-and-response-schema.md)
- [Pagination과 filtering](./06-pagination-and-filtering.md)
- [Error response 설계](./07-error-response-design.md)
- [OpenAPI와 Swagger](./08-openapi-and-swagger.md)
- **Versioning (현재 글)**
- 좋은 API 문서 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Stripe API Versioning](https://stripe.com/docs/upgrades)
- [GitHub REST API: API Versions](https://docs.github.com/en/rest/overview/api-versions)
- [Sunset HTTP Header (RFC 8594)](https://www.rfc-editor.org/rfc/rfc8594)
- [Deprecation HTTP Header](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-deprecation-header)

Tags: Computer Science, APIDesign, Versioning, Compatibility, Deprecation, Backend
