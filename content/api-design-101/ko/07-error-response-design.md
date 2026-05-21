---
title: "API Design 101 (7/10): Error response 설계"
series: api-design-101
episode: 7
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
  - Errors
  - RFC7807
  - Validation
  - Backend
last_reviewed: '2026-05-15'
seo_description: 일관된 error response를 만드는 envelope, code, validation 규칙을 정리합니다.
---

# API Design 101 (7/10): Error response 설계

성공 응답은 한두 개만 잘 맞춰도 눈에 잘 띄지 않지만, 에러 응답은 조금만 흔들려도 바로 운영 비용으로 돌아옵니다. 지원 요청은 늘고, 클라이언트는 예외 분기를 늘리고, 로그에서는 같은 실패가 여러 모양으로 찍히기 시작합니다.

이 글은 API Design 101 시리즈의 일곱 번째 글입니다.

여기서는 에러를 부가 정보가 아니라 정식 계약으로 다룹니다. 상태 코드, machine-readable code, validation detail, trace id가 어떻게 함께 움직여야 디버깅과 보안이 동시에 버틸 수 있는지 정리합니다.

![API Design 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/07/07-01-concept-at-a-glance.ko.png)
*에러가 발생하면 status code → error code → detail → trace id 순서로 응답이 구성되는 흐름*

## 먼저 던지는 질문

- 좋은 error response는 어떤 요소로 이루어질까요?
- RFC 7807 `application/problem+json`은 왜 유용할까요?
- validation error는 어떤 모양으로 표현해야 할까요?

## 에러 응답이 API의 두 번째 얼굴인 이유

성공 경로는 하나지만 에러 경로는 수십, 수백 개입니다. 에러 모양이 제각각이면 다음과 같은 비용이 발생합니다.

| 문제 | 운영 비용 |
|---|---|
| 에러 포맷이 endpoint마다 다름 | 클라이언트 코드에 endpoint별 예외 분기 증가 |
| 사람용 메시지만 있고 machine-readable code 없음 | 자동 재시도·분기 로직 구현 불가 |
| validation 실패를 한 문장으로만 반환 | 사용자에게 "어느 필드가 왜 틀렸는지" 표시 불가 |
| stack trace를 그대로 노출 | 내부 구조 유출 → 보안 위험 |
| trace id 없음 | 지원 요청마다 로그 전체를 탐색해야 함 |

Stripe의 에러 객체(`type`, `code`, `param`, `message`)가 사실상 업계 기준처럼 읽히는 이유는, 이 모든 요소를 일관되게 제공하기 때문입니다.

## 전후 비교

실제 프로젝트에서 흔히 보이는 에러 응답 변천을 비교합니다.

**Before — 자유 형식, endpoint마다 다른 모양**

```json
// GET /users/42 → 404
{"error": "not found"}

// POST /orders → 422
{"message": "validation failed", "details": "email is required"}

// POST /login → 401
"Unauthorized"
```

세 endpoint가 세 가지 다른 포맷을 씁니다. 클라이언트는 endpoint마다 별도 파싱 로직을 짜야 합니다.

**After — 통일된 envelope**

```json
// GET /users/42 → 404
{
  "type": "https://api.example.com/errors/user-not-found",
  "title": "User not found",
  "status": 404,
  "code": "user.not_found",
  "detail": "ID 42에 해당하는 사용자가 없습니다.",
  "trace_id": "req_a1b2c3"
}

// POST /orders → 422
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "code": "validation_error",
  "trace_id": "req_d4e5f6",
  "errors": [{"field": "email", "code": "required", "detail": "이메일은 필수입니다."}]
}

// POST /login → 401
{
  "type": "https://api.example.com/errors/invalid-credentials",
  "title": "Invalid credentials",
  "status": 401,
  "code": "auth.invalid_credentials",
  "detail": "이메일 또는 비밀번호가 올바르지 않습니다.",
  "trace_id": "req_g7h8i9"
}
```

모양이 동일하므로 클라이언트는 하나의 `handleApiError(response)` 함수로 모든 에러를 처리할 수 있습니다.

## Error response envelope 설계

### RFC 7807 — HTTP API 문제 상세 형식

RFC 7807(2023년에 RFC 9457로 개정)은 에러 응답의 표준 스키마를 정의합니다.

```json
{
  "type": "https://api.example.com/errors/insufficient-funds",
  "title": "Insufficient funds",
  "status": 403,
  "detail": "Account balance is 30, but transfer requires 50.",
  "instance": "/transfers/txn_abc123"
}
```

| 필드 | 역할 | 필수 |
|---|---|---|
| `type` | 에러 유형을 식별하는 URI. 문서 페이지로 연결 가능 | 권장 |
| `title` | 사람이 읽는 짧은 제목. `type`별로 고정 | 권장 |
| `status` | HTTP status code 복사 (본문만 보고도 판단 가능) | 권장 |
| `detail` | 이번 요청에 한정된 상세 설명 | 선택 |
| `instance` | 이 에러 발생의 고유 참조 URI | 선택 |

### 확장 필드 추가

RFC 7807은 표준 필드 외에 추가 멤버를 허용합니다. 실무에서는 다음을 자주 추가합니다.

```json
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "code": "validation_error",
  "trace_id": "req_7f3a2b1c",
  "errors": [
    {"field": "email", "code": "invalid_format", "detail": "유효한 이메일 형식이 아닙니다."},
    {"field": "age", "code": "out_of_range", "detail": "0 이상 150 이하여야 합니다."}
  ]
}
```

- `code`: status code보다 세분화된 machine-readable 식별자
- `trace_id`: 분산 시스템에서 요청을 추적하는 고유 ID
- `errors[]`: validation 실패를 필드별로 분리

## Error code 네이밍 규칙

status code만으로는 에러를 세분화할 수 없습니다. `404`라고 해도 "사용자를 못 찾음"과 "주문을 못 찾음"은 클라이언트 입장에서 완전히 다른 분기입니다.

### 네이밍 패턴

```text
{resource}.{reason}
```

| Error code | Status | 의미 |
|---|---|---|
| `user.not_found` | 404 | 해당 사용자 없음 |
| `user.email_taken` | 409 | 이메일 중복 |
| `order.payment_required` | 402 | 결제 필요 |
| `order.already_shipped` | 409 | 이미 발송됨, 취소 불가 |
| `auth.token_expired` | 401 | 토큰 만료 |
| `auth.insufficient_scope` | 403 | 권한 부족 |
| `rate_limit.exceeded` | 429 | 요청 제한 초과 |

### 규칙

1. **snake_case + dot 구분**: `resource.reason` 형태로 통일
2. **안정성**: 한 번 공개한 code는 의미를 바꾸지 않음. 새 상황은 새 code를 추가
3. **계층**: 클라이언트가 `auth.*`로 시작하는 코드를 모두 "인증 문제"로 묶어 처리 가능
4. **문서화**: 모든 error code를 API 문서에 열거하고, 각각의 재시도 가능 여부를 명시

## Validation error 상세 설계

### 나쁜 예

```json
{"error": "입력이 올바르지 않습니다."}
```

이 응답으로는 클라이언트가 어떤 필드를 고쳐야 하는지 알 수 없습니다.

### 좋은 예

```json
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "code": "validation_error",
  "errors": [
    {"field": "name", "code": "required", "detail": "이름은 필수입니다."},
    {"field": "email", "code": "invalid_format", "detail": "유효한 이메일 형식이 아닙니다."},
    {"field": "items[0].quantity", "code": "out_of_range", "detail": "1 이상이어야 합니다."}
  ]
}
```

### 설계 규칙

| 규칙 | 이유 |
|---|---|
| `field`에 JSON path 사용 (`items[0].quantity`) | 중첩 객체·배열에서도 정확한 위치 지정 |
| 필드별 `code` 부여 (`required`, `invalid_format`) | 클라이언트가 코드 기반으로 i18n 메시지 매핑 가능 |
| 모든 실패 필드를 한 번에 반환 | "하나 고치고 다시 보내고"를 반복하지 않도록 |
| `detail`은 개발자용 | 사용자 표시 메시지는 클라이언트가 code로 결정 |

## 보안과 에러 응답

### 절대 노출하면 안 되는 정보

| 항목 | 위험 |
|---|---|
| Stack trace | 내부 파일 경로, 프레임워크 버전 노출 |
| SQL 쿼리 | 테이블 구조, 컬럼명 노출 |
| 계정 존재 여부 (`"User not found"` vs `"Wrong password"`) | 열거 공격(enumeration attack) |
| 내부 서비스 이름 | 인프라 구조 노출 |

### 인증 에러의 일관된 처리

```python
# Bad — 계정 존재 여부를 알려줌
if not user:
    return problem(404, "user.not_found", "User not found", "...")
if not check_password(user, password):
    return problem(401, "auth.wrong_password", "Wrong password", "...")

# Good — 동일한 응답으로 열거 공격 차단
return problem(401, "auth.invalid_credentials", "Invalid credentials",
               "이메일 또는 비밀번호가 올바르지 않습니다.")
```

### 응답 시간 차이로 인한 정보 유출

동일한 메시지를 반환해도 "사용자 조회 후 비밀번호 검증"과 "사용자 없음 즉시 반환"의 응답 시간이 다르면 타이밍 공격으로 계정 존재 여부를 알 수 있습니다. 이를 방지하려면:

```python
import hmac, time

def constant_time_auth(email: str, password: str) -> bool:
    user = find_user(email)
    # 사용자가 없어도 동일한 시간이 소요되도록 더미 해시와 비교
    stored_hash = user.password_hash if user else "$2b$12$dummy_hash_value_here"
    return hmac.compare_digest(
        hash_password(password).encode(),
        stored_hash.encode(),
    )
```

`hmac.compare_digest`는 문자열 길이와 무관하게 일정한 시간에 비교를 수행합니다.

## Trace ID — 디버깅의 생명줄

### 왜 필요한가

분산 시스템에서 하나의 API 요청은 여러 내부 서비스를 거칩니다. 에러가 발생했을 때 "어떤 요청이 어떤 경로로 어디서 실패했는지"를 추적하려면 요청 전체를 관통하는 고유 ID가 필요합니다.

### 구현 패턴

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uuid

app = FastAPI()

@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    return response

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal server error",
            "status": 500,
            "code": "internal_error",
            "detail": "예기치 않은 오류가 발생했습니다.",
            "trace_id": request.state.trace_id,
        },
        headers={"X-Trace-Id": request.state.trace_id},
    )
```

클라이언트가 지원 요청을 보낼 때 `trace_id`를 함께 전달하면, 운영팀은 해당 ID로 로그를 즉시 조회할 수 있습니다.

### Trace ID 전파 규칙

| 규칙 | 설명 |
|---|---|
| 클라이언트가 `X-Trace-Id`를 보내면 그대로 사용 | 프론트엔드 → BFF → 백엔드 전체를 하나의 ID로 추적 가능 |
| 없으면 서버가 생성 | 요청 시작 시점에 UUID 또는 ULID 생성 |
| 응답 header에 항상 포함 | 클라이언트가 에러 리포트에 첨부 가능 |
| 에러 본문에도 포함 | header를 읽지 못하는 환경(브라우저 제한 등) 대비 |
| 내부 서비스 간 전파 | 서비스 A → B → C 호출 시 동일 trace_id를 header로 전달 |

OpenTelemetry를 사용하는 환경이라면 `traceparent` header(W3C Trace Context)가 이미 같은 역할을 합니다. 이 경우 `trace_id`는 OpenTelemetry trace ID의 앞 16자리를 단축해서 사용하는 방식도 실무에서 흔합니다.

## 재시도 가능 여부 표시

모든 에러가 재시도할 수 있는 것은 아닙니다. 클라이언트에게 명확한 힌트를 주면 불필요한 재시도를 줄일 수 있습니다. 특히 429와 503은 `Retry-After` header를 반드시 함께 반환해야 클라이언트가 적절한 대기 시간을 계산할 수 있습니다.

| Status | 재시도 | 예시 |
|---|---|---|
| 400 | 불가 — 요청 자체가 잘못됨 | validation 실패 |
| 401 | 불가 — 인증 정보 갱신 후 재시도 | 토큰 만료 |
| 403 | 불가 — 권한 없음 | 접근 권한 부족 |
| 404 | 불가 — 리소스 없음 | 잘못된 ID |
| 409 | 조건부 — 충돌 해소 후 가능 | 이미 존재하는 이메일 |
| 429 | 가능 — `Retry-After` header 확인 | rate limit |
| 500 | 가능 — 일시적 장애일 수 있음 | DB timeout |
| 503 | 가능 — `Retry-After` header 확인 | 점검 중 |

```json
{
  "status": 429,
  "code": "rate_limit.exceeded",
  "title": "Too many requests",
  "detail": "분당 100회 제한을 초과했습니다.",
  "retry_after": 30
}
```

클라이언트 SDK를 제공한다면 error response의 `status`와 `code`를 기반으로 자동 재시도 로직을 내장할 수 있습니다. 예를 들어 `429`이면 `retry_after` 값만큼 대기 후 재시도, `500`이면 exponential backoff로 최대 3회 재시도, `400`/`401`/`403`/`404`는 재시도 없이 즉시 에러 반환하는 식입니다. 이 정보를 API 문서에 명시하면 SDK를 쓰지 않는 클라이언트도 동일한 전략을 구현할 수 있습니다.

## 자주 하는 실수 다섯 가지

| # | 실수 | 결과 | 해결 |
|---|---|---|---|
| 1 | 에러 본문이 문자열 하나 | 클라이언트가 파싱 불가 | RFC 7807 envelope 적용 |
| 2 | `title`만 있고 code 없음 | 번역·문구 수정 시 분기 깨짐 | 안정적 error code 추가 |
| 3 | validation 에러를 한 문장으로 반환 | 어느 필드가 틀렸는지 알 수 없음 | `errors[]` 필드별 분리 |
| 4 | stack trace를 본문에 노출 | 보안 사고 | production에서 상세 로그는 서버에만 |
| 5 | trace id 없음 | 지원 요청마다 전체 로그 탐색 | 모든 응답에 trace_id 포함 |

## 시니어 엔지니어는 이렇게 판단합니다

- error envelope를 공용 미들웨어나 base exception class로 구현합니다. endpoint마다 직접 조립하면 포맷이 흩어집니다.
- 새 에러 상황이 생기면 기존 code를 재활용하지 않고 새 code를 추가합니다. 의미가 달라진 code는 클라이언트를 깨뜨립니다.
- 4xx에도 반드시 trace_id를 넣습니다. 클라이언트가 "왜 400이 오는지 모르겠다"고 문의하면 즉시 해당 요청 로그를 조회할 수 있어야 합니다.
- error response도 API 문서의 정식 섹션입니다. "성공 응답만 문서화"하는 습관은 클라이언트 개발자의 생산성을 떨어뜨립니다.
- 인증 관련 에러는 계정 존재 여부를 드러내지 않도록 응답을 의도적으로 모호하게 만듭니다.

## 검증 포인트와 실패 신호

- **Expected output:** validation 실패는 필드별 `errors[]`, 인증/권한 오류는 안정적인 `code`, 서버 오류는 추적 가능한 `trace_id`를 함께 돌려줘야 합니다.
- **First check:** 같은 404라도 어떤 endpoint는 문자열, 어떤 endpoint는 JSON 객체를 반환한다면 envelope 통일이 아직 끝나지 않은 상태입니다.
- **Failure mode:** 보안 민감 정보를 `detail`에 그대로 넣거나 trace id를 빼먹으면, 지원 속도와 보안 태세가 동시에 나빠집니다.

## 체크리스트

- [ ] 모든 에러가 같은 envelope(RFC 7807 또는 동등한 구조)를 공유하는가?
- [ ] error code가 안정적인 문자열이며 문서화되어 있는가?
- [ ] validation 실패가 필드 단위 `errors[]`로 분해되는가?
- [ ] `detail`이 stack trace, SQL, 계정 존재 여부 등을 노출하지 않는가?
- [ ] 모든 응답(4xx 포함)에 trace_id가 있는가?
- [ ] 재시도 가능 여부가 status code와 문서로 명확히 전달되는가?

## 연습 문제

1. 현재 API에서 자주 나오는 4xx 응답 다섯 개에 `resource.reason` 형태의 error code를 붙이고, 각각의 재시도 가능 여부를 정리해 보세요.
2. validation 에러를 필드별로 반환하는 FastAPI exception handler를 작성해 보세요. `RequestValidationError`를 잡아서 RFC 7807 형태로 변환합니다.
3. 인증 에러에서 "사용자 없음"과 "비밀번호 틀림"을 구분하지 않는 응답을 설계하고, 그 이유를 정리해 보세요.

## 정리와 다음 글

error response는 API의 두 번째 얼굴입니다. envelope의 모양을 한 번 안정적으로 잡아 두면 클라이언트 코드와 운영 도구 모두 그 위에 일관되게 쌓을 수 있습니다. 다음 글에서는 이 모든 계약—성공 응답, 에러 응답, 파라미터—을 한곳에 모아 명세하는 OpenAPI와 Swagger를 다룹니다.

## 처음 질문으로 돌아가기

- **좋은 error response는 어떤 요소로 이루어질까요?**
  - HTTP status code(큰 범주), machine-readable error code(세분화된 식별자), 사람용 title/detail, 필드별 validation errors 배열, 그리고 trace_id입니다. 이 다섯 요소가 하나의 고정된 envelope 안에 항상 함께 있어야 클라이언트가 단일 파서로 모든 에러를 처리할 수 있습니다.
- **RFC 7807 `application/problem+json`은 왜 유용할까요?**
  - 팀마다 에러 포맷을 새로 발명하는 대신, 표준화된 스키마(`type`, `title`, `status`, `detail`, `instance`)를 쓰면 클라이언트 라이브러리, 문서 도구, 모니터링 시스템이 별도 설정 없이 에러를 이해할 수 있습니다. 확장 필드도 허용하므로 `code`, `errors[]`, `trace_id`를 자유롭게 추가할 수 있습니다.
- **validation error는 어떤 모양으로 표현해야 할까요?**
  - `errors[]` 배열 안에 필드별로 `field`(JSON path), `code`(machine-readable), `detail`(개발자용 설명)을 담아야 합니다. 모든 실패 필드를 한 번에 반환해야 "하나 고치고 다시 보내기"를 반복하지 않습니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- [API Design 101 (4/10): HTTP method와 status code](./04-http-methods-and-status.md)
- [API Design 101 (5/10): Request와 response schema](./05-request-and-response-schema.md)
- [API Design 101 (6/10): Pagination과 filtering](./06-pagination-and-filtering.md)
- **Error response 설계 (현재 글)**
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [RFC 7807 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc7807)
- [RFC 9457 — Problem Details for HTTP APIs (개정판)](https://www.rfc-editor.org/rfc/rfc9457)
- [Stripe API: Errors](https://stripe.com/docs/api/errors)
- [GitHub REST API: Errors](https://docs.github.com/en/rest/overview/troubleshooting)
- [Microsoft REST API Guidelines: Errors](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md)

Tags: Computer Science, APIDesign, Errors, RFC7807, Validation, Backend
