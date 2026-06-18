---
title: "바이브코딩을 위한 API 설계 기초 (2/10): REST 기본"
series: api-design-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- REST
seo_description: "AI에게 REST API 만들어달라고 하기 전에, REST가 URL 컨벤션이 아니라 여섯 가지 아키텍처 제약이라는 것을 이해해야 합니다."
---

# 바이브코딩을 위한 API 설계 기초 (2/10): REST 기본

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 2번째 글입니다.

"REST API 만들어줘"라는 프롬프트를 쓰면 AI는 보통 `/users`, `/orders` 같은 URL을 가진 코드를 만들어줍니다. 그런데 그 결과물이 정말 REST인지, 아니면 단지 슬래시로 구분된 URL을 가진 코드인지 어떻게 알 수 있을까요?

REST가 URL 스타일이라는 오해는 매우 흔합니다. 실제로 AI가 생성한 "REST API"도 이 오해에서 자유롭지 않습니다. 모든 요청을 POST로 처리하거나, 세션 상태를 서버에 저장하거나, 상태 코드를 무시하는 코드가 나올 수 있습니다. 형태는 REST처럼 생겼지만 원칙은 전혀 따르지 않는 API입니다.

REST의 핵심을 이해하면 AI에게 더 정확한 요청을 할 수 있고, 받은 코드가 원칙을 지키는지 검토할 수 있습니다.

> REST는 URL을 예쁘게 짓는 규칙이 아니라, 여섯 가지 아키텍처 제약이 만드는 설계 규율입니다.

---

## 이 글에서 다룰 문제
- REST는 어디서 나왔고 무엇을 뜻할까요?
- REST를 이루는 여섯 가지 아키텍처 제약은 무엇일까요?
- 리소스 중심 사고는 RPC 스타일과 어떻게 다를까요?
- AI가 생성한 "REST API"가 실제로 REST인지 어떻게 판단할까요?
- 바이브코딩에서 REST 원칙을 무시하면 어떤 문제가 생길까요?

REST(Representational State Transfer)는 Roy Fielding이 2000년에 정의한 아키텍처 스타일입니다. 여섯 가지 제약을 모두 따를 때 캐시, 수평 확장, 계층 추가가 자연스러워집니다. 하나라도 무시하면 그 이점을 잃습니다.

## Before / After

**Before — AI가 생성한 "REST처럼 생긴" RPC 스타일:**

```http
POST /api/getUser        {"userId": 42}
POST /api/createUser     {"name": "Alice"}
POST /api/deleteUser     {"userId": 42}
```

모든 요청이 POST입니다. GET은 캐시 가능하지만 이 코드는 캐시가 전혀 작동하지 않습니다. URL에 동사가 있어서 HTTP method의 의미론이 사라집니다.

**After — AI에게 REST 원칙을 명시하고 받은 코드:**

```http
# 프롬프트: "HTTP method의 의미를 살려 REST 스타일로 만들어줘. GET은 캐시 가능하게, 상태 코드도 표준대로"
GET    /users/42         # 조회 (캐시 가능, 안전)
POST   /users            # 생성
DELETE /users/42         # 삭제 (멱등)
```

같은 리소스(`/users`)에 method만 바꾸면 의도가 달라집니다. GET은 CDN에서 캐시되고, DELETE는 여러 번 보내도 결과가 같습니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| "REST API 만들어줘"만 요청 | URL 형태만 흉내 내는 코드가 나올 수 있음 | 여섯 가지 제약을 구체적으로 명시 |
| 모든 요청을 POST로 처리 | 캐시 불가, 멱등성 없음 | "HTTP method 의미대로 사용해줘" 추가 |
| 세션으로 인증 상태 유지 | 서버 수평 확장 불가 | "Stateless로 매 요청에 인증 정보 포함해줘" |
| 에러도 200으로 반환 | 모니터링, CDN이 에러를 감지 못함 | "HTTP 표준 상태 코드를 써줘" 명시 |
| REST를 "슬래시 URL"로만 이해 | Stateless·Cacheable 이점을 놓침 | Richardson Maturity Model 기준 Level 2 이상 요청 |

## AI에게 REST 관련 질문하는 팁

바이브코딩에서 REST 설계 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **Stateless 명시**: "세션 없이 매 요청에 인증 정보를 담아줘"
2. **Method 의미 명시**: "GET은 조회만, POST는 생성, DELETE는 삭제로 의미대로 써줘"
3. **캐시 전략 포함**: "GET 응답에 Cache-Control 헤더도 추가해줘"

예시 프롬프트:
> "사용자 CRUD API를 REST 스타일로 만들어줘. GET은 캐시 가능하게 Cache-Control 헤더 추가하고, POST는 201과 Location 헤더 반환, DELETE는 204 반환, 모든 요청은 Stateless로 Bearer 토큰 인증 써줘."

이렇게 하면 AI는 Richardson Maturity Model Level 2를 충족하는 코드를 제안합니다.

## 운영 체크리스트
- [ ] URL에 동사가 없는가? (동사는 HTTP method가 담당)
- [ ] GET 요청에 서버 상태 변경이 없는가? (Safe 원칙)
- [ ] PUT/DELETE를 여러 번 보내도 결과가 같은가? (Idempotent 원칙)
- [ ] 서버가 클라이언트 세션을 메모리에 저장하지 않는가? (Stateless)
- [ ] GET 응답에 Cache-Control 헤더가 있는가? (Cacheable)
- [ ] 클라이언트가 중간 레이어(CDN, LB)를 몰라도 되는가? (Layered System)

## 처음 질문으로 돌아가기

AI가 만들어준 API가 "REST API"인지 아닌지 판단하려면, URL 형태만 보는 것으로는 부족합니다. "이 API는 Stateless인가? 캐시가 가능한가? HTTP method를 의미대로 쓰고 있는가?"를 물어야 합니다. 이 여섯 가지 제약이 기준입니다.

## 정리

REST는 단순한 URL 컨벤션이 아니라 여섯 가지 아키텍처 제약이 함께 만드는 설계 규율입니다. AI에게 "REST API"를 요청할 때 이 원칙을 명시하면, 단순히 생긴 것만 REST인 코드 대신 진짜 REST 이점을 가진 코드를 받을 수 있습니다.

다음 글에서는 REST의 핵심인 리소스 설계를 다룹니다. URL을 어떻게 구성해야 하는지, AI에게 어떻게 요청해야 좋은 URL 구조를 받을 수 있는지 살펴봅니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [Roy Fielding — Architectural Styles (Ch. 5)](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [Richardson Maturity Model (Martin Fowler)](https://martinfowler.com/articles/richardsonMaturityModel.html)
- [REST API Tutorial (restfulapi.net)](https://restfulapi.net/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 API 설계 기초 (1/10): API란 무엇인가?
- **바이브코딩을 위한 API 설계 기초 (2/10): REST 기본 (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계
- 바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code
- 바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema
- 바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering
- 바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계
- 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger
- 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, REST
