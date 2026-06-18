---
title: "바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계"
series: api-design-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- 에러처리
seo_description: "AI가 만든 API에서 에러 응답이 제각각인 이유와, 일관된 에러 설계로 디버깅과 클라이언트 처리를 쉽게 하는 방법을 정리합니다."
---

# 바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 7번째 글입니다.

AI에게 여러 엔드포인트를 만들어달라고 하면 에러 응답 형태가 종종 이렇게 됩니다.

```json
// 404 에러
{"error": "not found"}

// 422 에러
{"message": "validation failed", "details": "email is required"}

// 401 에러
"Unauthorized"
```

세 엔드포인트가 세 가지 다른 포맷을 씁니다. 클라이언트는 엔드포인트마다 별도 파싱 로직을 만들어야 합니다. 어떤 에러는 문자열, 어떤 에러는 JSON 객체입니다. 사용자가 "왜 안 되나요?"라고 문의할 때 어떤 요청에서 오류가 났는지 추적할 방법도 없습니다.

이것은 AI의 실수라기보다 "에러 응답을 어떻게 구성해야 하는지 알려주지 않았기 때문"입니다. 에러 응답 설계 원칙을 이해하면 AI에게 일관된 에러 구조를 요청할 수 있고, 디버깅, 모니터링, 클라이언트 처리가 모두 쉬워집니다.

> 에러 응답 설계는 실패를 알리는 일이 아니라, 클라이언트가 다음 행동을 결정할 수 있게 실패를 분류해 주는 일입니다.

---

## 이 글에서 다룰 문제
- 좋은 error response는 어떤 요소로 이루어질까요?
- RFC 7807이란 무엇이고 왜 유용할까요?
- validation error는 어떤 형태로 표현해야 할까요?
- 에러 응답에서 보안 정보를 어떻게 숨겨야 할까요?
- 바이브코딩에서 에러 설계를 미루면 어떤 비용이 생길까요?

성공 경로는 하나지만 에러 경로는 수십, 수백 개입니다. 에러 모양이 제각각이면 클라이언트 코드에 엔드포인트별 예외 분기가 늘어나고, 자동 재시도/분기 로직 구현이 불가능해지고, 지원 요청마다 로그 전체를 탐색해야 합니다.

## Before / After

**Before — AI가 생성한 "제각각 에러 포맷":**

```json
// GET /users/42 → 404
{"error": "not found"}

// POST /orders → 422
{"message": "validation failed", "details": "email is required"}

// POST /login → 401
"Unauthorized"
```

세 개의 다른 포맷. 클라이언트는 엔드포인트마다 다른 파싱 로직 필요.

**After — AI에게 일관된 에러 envelope를 명시하고 받은 코드:**

```json
// 프롬프트: "RFC 7807 형태의 일관된 에러 응답, machine-readable code, trace_id 포함해줘"

// GET /users/42 → 404
{
  "type": "https://api.example.com/errors/user-not-found",
  "title": "User not found",
  "status": 404,
  "code": "user.not_found",
  "detail": "ID 42에 해당하는 사용자가 없습니다.",
  "trace_id": "req_a1b2c3"
}

// POST /orders → 422 (validation error)
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "code": "validation_error",
  "trace_id": "req_d4e5f6",
  "errors": [
    {"field": "email", "code": "required", "detail": "이메일은 필수입니다."},
    {"field": "items[0].quantity", "code": "out_of_range", "detail": "1 이상이어야 합니다."}
  ]
}
```

모양이 동일하므로 클라이언트는 하나의 `handleApiError()` 함수로 모든 에러를 처리할 수 있습니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 에러 본문이 문자열 하나 | 클라이언트가 파싱 불가 | "RFC 7807 envelope로 통일해줘" 요청 |
| code 없이 title만 있음 | 번역/문구 수정 시 클라이언트 분기 깨짐 | "안정적인 machine-readable error code 추가해줘" |
| validation 에러를 한 문장으로 | 어느 필드가 왜 틀렸는지 알 수 없음 | "errors[] 필드별로 분리해줘" 요청 |
| stack trace를 응답에 포함 | 내부 구조 노출, 보안 위험 | "production에서는 detail에 내부 정보 빼줘" |
| trace_id 없음 | 지원 요청마다 로그 전체를 탐색해야 함 | "모든 응답에 trace_id 포함해줘" 명시 |

## AI에게 에러 설계 관련 질문하는 팁

바이브코딩에서 에러 응답 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **envelope 통일**: "모든 에러를 RFC 7807 형태로 통일해줘"
2. **code 체계**: "resource.reason 형태의 error code를 써줘 (user.not_found, auth.token_expired)"
3. **trace ID**: "모든 응답(4xx 포함)에 trace_id를 포함해줘"

예시 프롬프트:
> "API 전체에서 에러 응답을 RFC 7807 형태로 통일해줘. status, code (resource.reason 형태), title, detail, trace_id 필드 포함. validation 에러는 errors[] 배열에 field, code, detail로 분리해줘. stack trace나 SQL 쿼리는 절대 응답에 포함하지 마. 인증 에러는 계정 존재 여부를 드러내지 말고 통합해줘."

## 운영 체크리스트
- [ ] 모든 에러가 같은 envelope(RFC 7807 또는 동등한 구조)를 공유하는가?
- [ ] error code가 안정적인 문자열이며 문서화되어 있는가?
- [ ] validation 실패가 필드 단위 errors[]로 분해되는가?
- [ ] detail에 stack trace, SQL, 계정 존재 여부가 포함되지 않는가?
- [ ] 모든 응답(4xx 포함)에 trace_id가 있는가?
- [ ] 429와 503에 Retry-After 헤더가 포함되는가?

## 처음 질문으로 돌아가기

AI가 만든 API에서 에러 응답이 엔드포인트마다 다른 형태일 때, "지금은 괜찮은데 나중에 고치지 뭐"라고 생각하는 대신 "이 API를 쓰는 클라이언트는 에러를 어떻게 처리해야 할까?"라고 물을 수 있어야 합니다. 에러 설계를 나중으로 미루면 클라이언트 코드에 엔드포인트별 분기가 쌓이고, 결국 아무것도 바꿀 수 없는 상태가 됩니다.

## 정리

에러 응답은 API의 두 번째 얼굴입니다. AI에게 RFC 7807 envelope, error code 체계, trace_id를 명시하면 디버깅과 클라이언트 처리가 모두 쉬워지는 일관된 에러 구조를 받을 수 있습니다.

다음 글에서는 이 모든 계약을 한곳에 모아 명세하는 OpenAPI와 Swagger를 다룹니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [RFC 7807 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc7807)
- [RFC 9457 — Problem Details for HTTP APIs (개정판)](https://www.rfc-editor.org/rfc/rfc9457)
- [Stripe API: Errors](https://stripe.com/docs/api/errors)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 API 설계 기초 (1/10): API란 무엇인가?
- 바이브코딩을 위한 API 설계 기초 (2/10): REST 기본
- 바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계
- 바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code
- 바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema
- 바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering
- **바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계 (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger
- 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, 에러처리
