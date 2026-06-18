---
title: "바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계"
series: api-design-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- REST
seo_description: "AI가 만들어준 URL이 왜 나중에 문제가 되는지, 좋은 리소스 설계 원칙을 바이브코딩 관점에서 정리합니다."
---

# 바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 3번째 글입니다.

"사용자 주문 API 만들어줘"라고 하면 AI는 URL을 만들어줍니다. `/getUserOrder?userId=42`, `/getOrdersByUser`, `/user/42/order`… 어떤 형태가 나올지는 복불복입니다. 그리고 이 URL은 한 번 공개하면 바꾸기가 매우 어렵습니다. SDK, 캐시 키, 로그 필터, 문서 링크가 모두 이 URL을 참조하기 때문입니다.

AI가 URL을 만들어줄 때 원칙이 없으면 프로젝트가 커질수록 URL 목록이 규칙 없이 쌓입니다. 어떤 엔드포인트는 `/getUser`, 어떤 건 `/users/42`, 어떤 건 `/user-list`가 되고, 팀원마다 다른 URL을 씁니다.

리소스 설계 원칙을 알면 AI에게 정확한 URL 구조를 요청할 수 있고, 받은 코드를 검토해서 "이 URL은 나중에 문제가 될 것 같다"고 판단할 수 있습니다.

> URL은 한 번 공개하면 데이터베이스 컬럼명보다 훨씬 오래 살아남습니다. 리소스 설계는 이 사실을 알고 시작해야 합니다.

---

## 이 글에서 다룰 문제
- 리소스의 경계는 어떻게 나눠야 할까요?
- 명사형 이름, 복수형, 계층 구조는 어떤 원칙으로 잡아야 할까요?
- 하위 리소스는 언제 쓰고 어디까지 깊게 들어가야 할까요?
- AI가 만든 URL 구조가 왜 나중에 문제가 되는지 어떻게 알 수 있을까요?
- 바이브코딩에서 URL 설계 없이 시작하면 어떤 일이 일어날까요?

리소스 설계는 세 가지 질문으로 시작합니다. "무엇이 독립적으로 식별 가능한가?" (최상위 컬렉션), "무엇이 다른 리소스에 종속되는가?" (하위 리소스), "식별자는 무엇을 쓸 것인가?" (UUID vs slug). 이 세 질문의 답이 곧 URL 구조가 됩니다.

## Before / After

**Before — AI가 생성한 규칙 없는 URL:**

```http
GET /getUserOrder?userId=42&orderId=9
POST /createUser
POST /deleteUser?id=42
GET /searchProducts?keyword=laptop&page=2
POST /user/42/activateAccount
```

동사가 URL에 있고, 단수/복수가 섞이고, 쿼리에 식별자가 섞입니다. 새 엔드포인트를 추가할 때마다 이름을 새로 발명해야 합니다.

**After — AI에게 리소스 설계 원칙을 명시하고 받은 URL:**

```http
# 프롬프트: "명사 복수형, 계층 구조, 동사 금지 원칙으로 URL 설계해줘"
GET    /users/42/orders/9        # 42번 사용자의 9번 주문 조회
POST   /users                    # 사용자 생성
DELETE /users/42                 # 사용자 삭제
GET    /products?keyword=laptop&page=2  # 검색은 컬렉션 + 쿼리
POST   /users/42/activation      # 액션은 명사화
```

URL만 읽어도 리소스의 소유 관계와 조작 대상이 명확합니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| URL에 동사 (`/getUser`) | HTTP method와 의미 중복 | "URL에는 명사만, 동사는 HTTP method로" 명시 |
| 단수형 컬렉션 (`/user`) | 목록인지 단일 리소스인지 불분명 | "컬렉션은 항상 복수형으로" 요청 |
| 내부 PK 노출 (`/user/1`, `/user/2`) | 순서 노출, IDOR 취약점 | "공개 식별자는 UUID 사용해줘" 요청 |
| 중첩 4단계 이상 | 클라이언트가 여러 ID를 조합해야 함 | "최대 3단계 중첩으로 제한해줘" 명시 |
| 같은 리소스에 두 URL | 캐시 무효화가 한쪽만 일어남 | "각 리소스에 canonical URL 하나만 허용해줘" |

## AI에게 리소스 설계 관련 질문하는 팁

바이브코딩에서 URL 구조 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **명사 복수형 명시**: "컬렉션은 복수형 명사로"
2. **계층 관계 명시**: "주문(order)은 사용자(user) 하위 리소스로"
3. **식별자 전략 포함**: "공개 ID는 UUID 형태로"

예시 프롬프트:
> "온라인 서점 API URL 구조를 설계해줘. books, users, orders, reviews가 있고, reviews는 book 하위 리소스야. 컬렉션은 복수형 명사, URL에 동사 없이, 최대 3단계 중첩으로 만들어줘. 공개 ID는 UUID 써줘."

이렇게 하면 AI는 `/books`, `/books/{id}/reviews`, `/users/{id}/orders` 같은 일관된 구조를 제안합니다.

## 운영 체크리스트
- [ ] 모든 컬렉션이 복수형인가?
- [ ] URL에 동사가 없는가? (동사는 HTTP method 담당)
- [ ] 각 리소스에 공식 URL이 하나뿐인가? (Canonical URL)
- [ ] 중첩이 3단계 이하로 유지되는가?
- [ ] 공개 식별자가 내부 auto-increment PK와 분리되어 있는가?
- [ ] DB 스키마 이름이 URL에 노출되지 않는가? (`user_tbl` 같은 것)

## 처음 질문으로 돌아가기

AI가 만들어준 URL이 왜 나중에 문제가 되는지 이해하려면, URL이 단순한 문자열이 아니라 도메인을 명사 단위로 잘라 외부에 노출할 경계라는 점을 알아야 합니다. "이 리소스는 독립적인가, 종속적인가?", "이 URL은 5년 뒤에도 이 이름으로 불릴까?"를 묻는 습관이 생기면 AI 코드를 더 잘 검토할 수 있습니다.

## 정리

리소스 설계는 URL을 예쁘게 짓는 일이 아니라, 도메인을 명사 단위로 잘라 외부에 노출할 경계를 정하는 일입니다. 복수형 명사, 동사 금지, 계층은 소유 관계, 깊이는 3단계 이하. 이 네 가지 원칙을 AI 프롬프트에 포함하면 유지보수 가능한 URL 구조를 받을 수 있습니다.

다음 글에서는 이 리소스에 어떤 동작을 얹을지, HTTP method와 상태 코드를 다룹니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [REST Resource Naming Guide (restfulapi.net)](https://restfulapi.net/resource-naming/)
- [Google API Design Guide — Resource Names](https://cloud.google.com/apis/design/resource_names)
- [GitHub REST API: Issues](https://docs.github.com/en/rest/issues/issues)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 API 설계 기초 (1/10): API란 무엇인가?
- 바이브코딩을 위한 API 설계 기초 (2/10): REST 기본
- **바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계 (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code
- 바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema
- 바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering
- 바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계
- 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger
- 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, REST
