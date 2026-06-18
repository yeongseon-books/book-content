---
title: "바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code"
series: api-design-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- HTTP
seo_description: "AI가 만든 API에서 모든 응답이 200인 이유와, HTTP method와 status code를 제대로 쓰는 방법을 바이브코딩 관점에서 정리합니다."
---

# 바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 4번째 글입니다.

AI에게 API를 만들어달라고 하면 자주 보이는 패턴이 있습니다. 생성이든 삭제든 조회든 모두 `200 OK`로 응답합니다. 성공인지 실패인지는 본문 안의 `{"success": false}` 같은 필드로 알려줍니다. 클라이언트는 모든 응답 본문을 열어봐야 상태를 알 수 있고, HTTP 캐시나 모니터링 도구는 에러를 감지하지 못합니다.

이것은 AI의 실수가 아닙니다. "상태 코드를 HTTP 표준대로 써줘"라고 요청하지 않았으면 AI는 가장 단순한 형태를 선택합니다. method와 status code의 의미를 이해하고 프롬프트에 명시하면, 재시도가 안전한지 판단하고, 모니터링이 자동으로 동작하고, 클라이언트 분기 로직이 명확해집니다.

> status code는 단순한 숫자가 아니라 클라이언트의 다음 행동을 결정하는 계약입니다.

---

## 이 글에서 다룰 문제
- GET, POST, PUT, PATCH, DELETE는 각각 무엇을 의미할까요?
- Safe와 Idempotent는 어떻게 다를까요?
- 2xx, 4xx, 5xx 계열은 클라이언트에게 어떤 의미일까요?
- AI가 만든 API에서 모든 응답이 200인 이유는 무엇이고 왜 문제일까요?
- 바이브코딩에서 올바른 status code 사용이 왜 중요할까요?

method와 status code는 클라이언트의 분기 로직을 결정합니다. 잘못된 코드를 반환하면 클라이언트는 재시도가 안전한지조차 판단할 수 없습니다.

| Method | 의미 | Safe | Idempotent | 대표 성공 코드 |
|--------|------|------|------------|--------------|
| GET | 조회 | 예 | 예 | 200 |
| POST | 생성 | 아니오 | 아니오 | 201 |
| PUT | 전체 대체 | 아니오 | 예 | 200 / 204 |
| PATCH | 부분 수정 | 아니오 | 아니오* | 200 |
| DELETE | 삭제 | 아니오 | 예 | 204 |

*PATCH는 스펙상 Idempotent가 아니지만 실무에서는 Idempotent하게 설계하는 것이 권장됩니다.

## Before / After

**Before — AI가 생성한 "동작하지만 의도가 불분명한" 코드:**

```http
POST /users/42/update   200 OK   {"ok": true}
POST /users/42/delete   200 OK   {"ok": true}
POST /users             200 OK   {"ok": true}
GET  /users/999         200 OK   {"error": "not found"}
```

클라이언트는 본문을 파싱해야 성공/실패를 알 수 있습니다. HTTP 캐시가 에러 응답을 저장할 수 있습니다. SDK의 예외 처리가 작동하지 않습니다.

**After — AI에게 method와 status code를 명시하고 받은 코드:**

```http
# 프롬프트: "HTTP method 의미대로 사용하고, 생성은 201+Location, 삭제는 204, 없는 리소스는 404 써줘"
PATCH  /users/42   200 OK         {"id": 42, "name": "updated"}
DELETE /users/42   204 No Content
POST   /users      201 Created    Location: /users/43
GET    /users/999  404 Not Found  {"error": "user_not_found"}
```

status만 보고도 후속 분기가 그려집니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 성공을 전부 200으로 반환 | 생성, 수정, 삭제의 차이가 사라짐 | "생성은 201, 삭제 성공은 204 써줘" 명시 |
| 검증 실패를 500으로 반환 | 클라이언트가 재시도해도 될 문제라고 오해 | "입력 오류는 400 또는 422 써줘" 요청 |
| 404와 403을 혼동 | 권한 없음인지 없는 리소스인지 불분명 | "인증 없으면 401, 권한 없으면 403, 없는 리소스는 404" |
| PATCH로 전체 대체 | PUT의 의미가 무너짐 | "PUT은 전체 대체, PATCH는 부분 수정으로 구분해줘" |
| DELETE에 본문 포함 | Idempotency 의미를 흐림 | "DELETE는 본문 없이 204 반환해줘" |

## AI에게 HTTP method 관련 질문하는 팁

바이브코딩에서 method와 status code 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **method별 status 명시**: "POST 생성 성공은 201+Location, DELETE 성공은 204"
2. **에러 코드 분리**: "입력 오류 400, 인증 없음 401, 권한 없음 403, 없는 리소스 404"
3. **재시도 가능 여부**: "서버 오류 5xx는 재시도 가능, 클라이언트 오류 4xx는 재시도 무의미"

예시 프롬프트:
> "사용자 API에서 POST /users는 성공 시 201+Location 반환, 이메일 중복이면 409, 필드 누락이면 422 반환해줘. DELETE /users/{id}는 성공 시 204, 없는 ID면 404 반환해줘. 클라이언트가 4xx와 5xx를 다르게 처리할 수 있게 표준을 지켜줘."

## 운영 체크리스트
- [ ] 생성은 201 + Location 헤더를 반환하는가?
- [ ] 삭제 성공은 204를 반환하는가? (본문 없음)
- [ ] 입력 검증 실패는 400 또는 422인가?
- [ ] 인증 누락은 401, 권한 부족은 403으로 구분되는가?
- [ ] GET은 서버 상태를 변경하지 않는가? (Safe)
- [ ] PUT, DELETE를 여러 번 보내도 결과가 같은가? (Idempotent)

## 처음 질문으로 돌아가기

AI가 만든 API에서 모든 응답이 200인 코드를 발견했을 때, "AI가 잘못했다"고 말하는 대신 "이 응답에서 클라이언트는 재시도해야 할지 어떻게 알 수 있을까?"라고 물을 수 있어야 합니다. `2xx`는 성공, `4xx`는 클라이언트가 고칠 수 있는 문제, `5xx`는 서버가 고쳐야 하는 문제. 이 구분이 모니터링, 재시도, 에러 처리 전략을 결정합니다.

## 정리

method와 status code는 항상 짝으로 읽어야 합니다. AI에게 요청할 때 이 두 가지를 명시하면 캐시, 재시도, 모니터링이 자동으로 올바르게 작동하는 코드를 받을 수 있습니다.

다음 글에서는 그 사이를 오가는 실제 데이터, 즉 request와 response schema를 다룹니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [HTTP Methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [HTTP Status Codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [RFC 7231 — HTTP/1.1 Semantics](https://www.rfc-editor.org/rfc/rfc7231)
- [Idempotency in REST APIs (Stripe blog)](https://stripe.com/blog/idempotency)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 API 설계 기초 (1/10): API란 무엇인가?
- 바이브코딩을 위한 API 설계 기초 (2/10): REST 기본
- 바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계
- **바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema
- 바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering
- 바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계
- 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger
- 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, HTTP
