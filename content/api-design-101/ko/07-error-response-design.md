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

## 먼저 던지는 질문

- 좋은 error response는 어떤 요소로 이루어질까요?
- RFC 7807 `application/problem+json`은 왜 유용할까요?
- validation error는 어떤 모양으로 표현해야 할까요?

## 큰 그림

![API Design 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/07/07-01-concept-at-a-glance.ko.png)

*API Design 101 7장 흐름 개요*

이 그림에서는 Error response 설계를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Error response 설계의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

성공 경로는 하나지만 에러 경로는 수십, 수백 개입니다. 에러 모양이 제각각이면 클라이언트는 케이스별로 모두 따로 처리해야 하고, 사용자에게는 결국 “알 수 없는 오류”만 남게 됩니다.

> 좋은 error response는 디버깅 시간을 줄여 줍니다.

## 한눈에 보는 개념

이렇게 모양을 고정해 두면 클라이언트는 공통 파서를 유지한 채 `status`, `code`, `errors[]`만 보고도 적절한 사용자 메시지와 재시도 전략을 고를 수 있습니다.

## 핵심 용어

- **Status code**: 에러의 큰 범주입니다. `4xx`는 사용자 측, `5xx`는 서버 측입니다.
- **Error code**: 안정적으로 유지되는 문자열 식별자입니다. 예를 들면 `user.not_found`입니다.
- **Title**: 사람이 빠르게 읽는 짧은 제목입니다.
- **Detail**: 더 긴 설명입니다.
- **Errors[]**: validation 실패 항목을 필드 단위로 담는 배열입니다.

## Before / After

**Before (자유 형식)**

```json
{"error": "something went wrong"}
```

**After (RFC 7807 + code)**

```json
{
  "type": "https://example.com/errors/user-not-found",
  "title": "User not found",
  "status": 404,
  "code": "user.not_found",
  "detail": "User 42 does not exist."
}
```

모양이 안정적이면 클라이언트도 일관되게 다룰 수 있습니다.

## 실습: error response를 만드는 다섯 단계

### Step 1 — Standard envelope

```python
# 1_envelope.py
from flask import Flask, jsonify
app = Flask(__name__)

def problem(status, code, title, detail):
    body = {"type": "about:blank", "title": title,
            "status": status, "code": code, "detail": detail}
    return jsonify(body), status, {"Content-Type": "application/problem+json"}

@app.get("/users/<int:uid>")
def user(uid):
    return problem(404, "user.not_found", "User not found", f"User {uid} does not exist.")
```

모든 에러가 같은 envelope를 공유하면 처리와 문서화가 쉬워집니다.

### Step 2 — Validation errors

```python
# 2_validation.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.post("/users")
def create():
    body = request.get_json() or {}
    errs = []
    if "name" not in body: errs.append({"field": "name", "code": "required"})
    if "email" not in body: errs.append({"field": "email", "code": "required"})
    if errs:
        return jsonify(title="Validation failed", status=422,
                       code="validation_error", errors=errs), 422
    return jsonify(ok=True), 201
```

validation 실패는 `errors[]` 안에 필드별로 쪼개 담아야 클라이언트가 정확히 표시할 수 있습니다.

### Step 3 — Stable error codes

```text
user.not_found
order.payment_required
order.already_paid
```

status code보다 더 안정적으로 분기되는 값이 문자열 error code입니다.

### Step 4 — Avoid leaking secrets

```python
# 4_safe.py
# Bad : detail="No password match for user 'yeongseon'"
# Good: detail="Invalid credentials."
```

인증과 권한 관련 에러는 계정 존재 여부 같은 정보를 과하게 드러내지 않아야 합니다.

### Step 5 — trace id

```python
# 5_trace.py
import uuid
from flask import Flask, jsonify, g, request
app = Flask(__name__)

@app.before_request
def set_trace():
    g.trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex

@app.errorhandler(500)
def server_error(e):
    return jsonify(title="Internal", status=500, trace_id=g.trace_id), 500
```

trace id가 있으면 지원 요청이 막연한 추적 작업이 아니라 빠른 조회 작업으로 바뀝니다.

## 이 코드에서 봐야 할 점

- 에러 본문이 항상 같은 형태를 가집니다.
- 사람용 메시지와 기계용 코드가 분리되어 있습니다.
- trace id가 응답과 함께 따라갑니다.

## 자주 하는 실수 다섯 가지

1. **에러 본문이 문자열 하나뿐입니다.** 클라이언트가 파싱할 수 없습니다.
2. **`title`만 있고 error code가 없습니다.** 번역이나 문구 수정 이후 분기가 깨집니다.
3. **validation 에러를 한 문장으로만 반환합니다.** 어느 필드가 틀렸는지 알 수 없습니다.
4. **stack trace를 본문에 넣습니다.** 보안 사고로 이어질 수 있습니다.
5. **trace id가 없습니다.** 모든 지원 요청이 탐정 소설이 됩니다.

## 실무에서는 이렇게 드러납니다

Stripe의 error object는 `type`, `code`, `param`, `message` 조합으로 사실상 업계 기준처럼 읽힙니다. 대규모 내부 API도 RFC 7807 자체를 쓰거나 거의 같은 변형을 사용합니다. 중요한 것은 포맷 이름보다 모양의 안정성입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- error envelope를 공용 모듈로 구현합니다.
- 새 에러는 새 code를 추가해서 표현합니다.
- 4xx에도 trace id를 함께 돌려줍니다.
- 사용자 메시지는 보안과 UX 관점에서 따로 검토합니다.
- 자주 발생하는 에러는 문서 상단에서 먼저 보여 줍니다.

## 검증 포인트와 실패 신호

- **Expected output:** validation 실패는 필드별 `errors[]`, 인증/권한 오류는 안정적인 `code`, 서버 오류는 추적 가능한 `trace_id`를 함께 돌려줘야 합니다.
- **First check:** 같은 404라도 어떤 엔드포인트는 문자열, 어떤 엔드포인트는 JSON 객체를 반환한다면 envelope 통일이 아직 끝나지 않은 상태입니다.
- **Failure mode:** 보안 민감 정보를 `detail`에 그대로 넣거나 trace id를 빼먹으면, 지원 속도와 보안 태세가 동시에 나빠집니다.

## 체크리스트

- [ ] 모든 에러가 같은 envelope를 공유하는가?
- [ ] error code가 안정적인 문자열인가?
- [ ] validation 실패가 필드 단위로 분해되는가?
- [ ] `detail`이 민감한 정보를 노출하지 않는가?
- [ ] 모든 응답에 trace id가 있는가?

## 연습 문제

1. 현재 API에서 자주 나오는 4xx 응답 다섯 개에 안정적인 code 이름을 붙여 보세요.
2. Step 2 예제에 최소 길이 검사를 추가해 보세요.
3. 자유 형식 에러를 RFC 7807 envelope로 옮기는 마이그레이션 절차를 적어 보세요.

## 정리와 다음 글

error response는 API의 두 번째 얼굴입니다. 다음 글에서는 이 모든 계약을 한곳에 모아 주는 OpenAPI와 Swagger를 다룹니다.

## 처음 질문으로 돌아가기

- **좋은 error response는 어떤 요소로 이루어질까요?**
  - 본문의 기준은 Error response 설계를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **RFC 7807 `application/problem+json`은 왜 유용할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **validation error는 어떤 모양으로 표현해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

- [RFC 7807 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc7807)
- [Stripe API: Errors](https://stripe.com/docs/api/errors)
- [GitHub REST API: Errors](https://docs.github.com/en/rest/overview/troubleshooting)
- [Microsoft REST API Guidelines: Errors](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md)

Tags: Computer Science, APIDesign, Errors, RFC7807, Validation, Backend
