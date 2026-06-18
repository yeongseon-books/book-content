---
title: "바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema"
series: api-design-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- JSON
seo_description: "AI가 만든 API에서 필드 이름, 날짜 형식, 금액 표현이 제각각인 이유와 schema를 제대로 설계하는 방법을 바이브코딩 관점에서 정리합니다."
---

# 바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 5번째 글입니다.

AI에게 API를 만들어달라고 하면 자주 이런 응답이 나옵니다.

```json
{"u": "Y", "ct": 1714800000, "act": "ok", "bal": 19.99}
```

`u`가 username인지 user_id인지, `ct`가 Unix timestamp인지 다른 값인지, `bal`이 달러인지 센트인지 알 수 없습니다. 이런 응답을 받은 클라이언트 개발자는 추측하거나 서버 코드를 직접 읽어야 합니다. 몇 달 뒤에는 만든 본인도 이 필드들의 의미를 잊어버립니다.

또 다른 흔한 문제는 내부 데이터 모델을 그대로 노출하는 것입니다. 데이터베이스 컬럼명, 내부 구현 세부 사항이 응답에 그대로 나옵니다. 나중에 DB 스키마를 바꾸면 API 응답도 함께 바뀌어서 모든 클라이언트가 영향을 받습니다.

schema 설계 원칙을 알면 AI에게 명확한 이름, 표준 형식, 분리된 입출력 구조를 요청할 수 있습니다.

> schema는 데이터의 문법입니다. 흔들리는 schema는 흔들리는 클라이언트를 만듭니다.

---

## 이 글에서 다룰 문제
- JSON 필드 이름 규칙은 어떻게 정해야 할까요?
- 날짜와 금액은 어떤 형식으로 표현해야 할까요?
- 입력(request) schema와 출력(response) schema는 왜 분리해야 할까요?
- AI가 만든 API에서 내부 모델이 노출되면 왜 문제일까요?
- 바이브코딩에서 schema 없이 시작하면 어떤 일이 일어날까요?

schema 설계는 네 가지 영역을 다룹니다. 필드 이름 규칙(snake_case vs camelCase), 타입과 값 제약(문자열 길이, enum 값), 시간/금액 표현(UTC ISO 8601, 정수 minor-unit), 입출력 분리(요청에는 id 없음, 내부 필드는 응답에 노출 안 함).

## Before / After

**Before — AI가 생성한 "의미 불명" 응답:**

```json
{"u": "Y", "ct": 1714800000, "act": "ok", "bal": 19.99}
```

`u`가 무슨 필드인지, `ct`가 무슨 시간인지, `bal`의 통화 단위가 무엇인지 알 수 없습니다. `bal`은 float이라 반올림 오차가 누적됩니다.

**After — AI에게 schema 원칙을 명시하고 받은 응답:**

```json
// 프롬프트: "필드명은 snake_case, 날짜는 UTC ISO 8601, 금액은 정수 센트 단위, 의미 있는 이름으로 만들어줘"
{
  "username": "yeongseon",
  "created_at": "2026-05-04T12:00:00Z",
  "active": true,
  "balance_cents": 1999,
  "currency": "USD"
}
```

필드명만 읽어도 데이터의 의미와 단위가 명확합니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 필드명 축약 (`u`, `ct`, `bal`) | 몇 달 뒤 의미를 아무도 모름 | "읽어서 바로 이해할 수 있는 이름 써줘" |
| 날짜에 Unix timestamp | 타임존 모호, 가독성 없음 | "날짜는 UTC ISO 8601 형식으로 (2026-05-04T12:00:00Z)" |
| 금액에 float | 0.1 + 0.2 = 0.30000000000000004 오차 | "금액은 정수 센트 단위로 (19.99 USD = 1999)" |
| 내부 ORM 모델 그대로 노출 | DB 변경 시 API 변경 강제 | "내부 모델과 응답 schema를 분리해줘" |
| 입력과 출력에 같은 schema | id가 요청에 포함, 내부 필드 노출 | "요청 schema와 응답 schema를 별도로 정의해줘" |

## AI에게 schema 관련 질문하는 팁

바이브코딩에서 schema 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **이름 규칙 명시**: "모든 필드는 snake_case로"
2. **특수 타입 형식 명시**: "날짜는 UTC ISO 8601, 금액은 정수 센트 단위"
3. **입출력 분리 요청**: "요청 body schema와 응답 schema를 별도로 정의해줘"

예시 프롬프트:
> "사용자 생성 API를 만들어줘. 요청 body에는 username, email만 포함하고, 응답에는 id, username, email, created_at(UTC ISO 8601)을 포함해줘. 필드명은 snake_case, 내부 DB 필드는 노출하지 마. 검증 실패 시 어떤 필드가 왜 틀렸는지 field별로 422를 반환해줘."

## 운영 체크리스트
- [ ] 모든 필드명을 읽어서 바로 의미를 알 수 있는가?
- [ ] 날짜/시간이 UTC + ISO 8601 형식인가?
- [ ] 금액이 정수 minor-unit(센트 등)으로 표현되는가?
- [ ] 요청 schema와 응답 schema가 분리되어 있는가?
- [ ] 내부 DB 컬럼명이나 ORM 필드가 응답에 노출되지 않는가?
- [ ] 필드 이름 규칙(snake_case 또는 camelCase)이 전체에서 일관적인가?

## 처음 질문으로 돌아가기

AI가 만든 API 응답에서 `{"u": "Y", "ct": 1714800000}` 같은 코드를 발견했을 때, "이게 무슨 의미인지 물어봐야 하나"라고 생각하는 대신 "이 schema가 3개월 뒤에도 읽힐 수 있는가?"라고 물을 수 있어야 합니다. 좋은 schema는 읽기 쉽고, 표준을 따르고, 내부 구현을 숨깁니다.

## 정리

schema는 데이터의 문법입니다. AI에게 필드 이름 규칙, 날짜/금액 표준 형식, 입출력 분리를 명시하면 나중에 유지보수할 수 있는 API를 받을 수 있습니다.

다음 글에서는 거의 모든 목록 API가 마주치는 주제인 pagination과 filtering을 다룹니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [JSON Schema](https://json-schema.org/)
- [pydantic Documentation](https://docs.pydantic.dev/)
- [ISO 8601 Date and Time Format](https://en.wikipedia.org/wiki/ISO_8601)
- [Stripe API: Working with Money](https://stripe.com/docs/currencies)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 API 설계 기초 (1/10): API란 무엇인가?
- 바이브코딩을 위한 API 설계 기초 (2/10): REST 기본
- 바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계
- 바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code
- **바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering
- 바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계
- 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger
- 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, JSON
