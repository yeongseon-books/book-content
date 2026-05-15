---
title: 리소스 설계
series: api-design-101
episode: 3
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
  - REST
  - Resources
  - URL
  - Backend
last_reviewed: '2026-05-12'
seo_description: 좋은 REST URL을 만드는 리소스 모델링과 명명 규칙을 실전적으로 정리합니다.
---

# 리소스 설계

이 글은 API Design 101 시리즈의 세 번째 글입니다. 좋은 REST URL은 경로 모양만 예쁘게 다듬는다고 나오지 않습니다. 리소스를 어떻게 나누고, 어떻게 이름 붙이고, 어떤 식별자를 드러낼지부터 제대로 모델링해야 합니다.

## 이 글에서 다룰 문제

- 리소스의 경계는 어떻게 나눠야 할까요?
- 명사형 이름, 복수형, 계층 구조는 어떤 원칙으로 잡아야 할까요?
- 하위 리소스는 언제 쓰고 어디까지 깊게 들어가야 할까요?
- 식별자는 무엇을 공개하고 무엇을 숨겨야 할까요?
- 현업에서 반복해서 등장하는 리소스 설계 안티패턴은 무엇일까요?

## 왜 중요한가

URL은 한 번 공개되면 바꾸는 비용이 큽니다. 리소스 모델이 흔들리면 이후의 method, 상태 코드, 문서 구조까지 모두 흔들립니다. 리소스 설계는 API 설계의 절반이라고 봐도 과장이 아닙니다.

> 리소스가 흔들리면 나머지도 함께 흔들립니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    A["/users"] --> B["/users/42"]
    B --> C["/users/42/orders"]
    C --> D["/users/42/orders/9"]
```

컬렉션에서 아이템으로, 다시 하위 컬렉션과 하위 아이템으로 내려가는 구조입니다.

## 핵심 용어

- **Collection**: 같은 종류의 리소스 집합입니다. 예를 들면 `/users`입니다.
- **Item**: 컬렉션 안의 단일 원소입니다. 예를 들면 `/users/42`입니다.
- **Sub-resource**: 다른 리소스에 속한 리소스입니다. 예를 들면 `/users/42/orders`입니다.
- **Identifier**: 리소스를 식별하는 키입니다. id나 slug가 여기에 해당합니다.
- **Canonical URL**: 그 리소스를 대표하는 공식 경로입니다.

## Before / After

**Before (동사, 단수형, 평면 구조)**

```http
GET /getUserOrder?userId=42&orderId=9
```

**After (명사, 복수형, 계층 구조)**

```http
GET /users/42/orders/9
```

URL만 읽어도 무엇을 의미하는지 이해할 수 있어야 합니다.

## 실습: 리소스 모델을 만드는 다섯 단계

### Step 1 — Start with Nouns

```
/users
/orders
/articles
```

컬렉션은 기본적으로 복수형 명사를 사용합니다.

### Step 2 — Attach Identifiers

```
/users/42
/orders/9
/articles/python-logging
```

숫자 id도 쓸 수 있고 의미 있는 slug도 사용할 수 있습니다.

### Step 3 — Sub-resources

```
/users/42/orders          # the orders that belong to user 42
/users/42/orders/9        # order 9 within that scope
```

URL의 모양만 봐도 소유 관계가 드러나야 합니다.

### Step 4 — Collection Operations

```python
# 4_collection.py
from flask import Flask, jsonify
app = Flask(__name__)

USERS = {42: {"name": "Yeongseon"}}

@app.get("/users")
def list_users(): return jsonify(list(USERS.values()))

@app.get("/users/<int:uid>")
def get_user(uid): return jsonify(USERS[uid])
```

컬렉션 전체와 단일 아이템은 서로 다른 endpoint입니다.

### Step 5 — Restraint on Depth

```
# Good
/users/42/orders

# Too deep
/users/42/orders/9/items/3/options/red
```

세 단계가 넘어가면 읽기 전에 쓰기부터 불편해지기 시작합니다. 그때는 query parameter가 더 나은 경우가 많습니다.

## 이 코드에서 봐야 할 점

- 컬렉션은 모두 복수형입니다.
- 각 리소스에는 공식 URL이 하나만 있어야 합니다.
- 깊은 중첩은 읽기보다 먼저 쓰기 경험을 망칩니다.

## 자주 하는 실수 다섯 가지

1. **단수형 컬렉션을 씁니다.** `/user`는 직관에 맞지 않습니다.
2. **URL에 동사를 넣습니다.** `/users/42/activate`보다는 명시적 action 표현을 고민해야 합니다.
3. **데이터베이스 스키마를 그대로 노출합니다.** `user_tbl` 같은 내부 이름은 밖으로 나오면 안 됩니다.
4. **내부 PK를 곧바로 공개합니다.** 보안성과 이식성 모두 불리해질 수 있습니다.
5. **하나의 리소스에 공식 URL이 여러 개입니다.** 캐시와 문서 일관성이 깨집니다.

## 실무에서는 이렇게 드러납니다

GitHub의 `/repos/{owner}/{repo}/issues/{number}`는 명사, 복수형, 계층 구조가 잘 드러나는 대표 사례입니다. Stripe의 `/v1/customers/{id}/sources`도 같은 패턴을 따릅니다. 규모가 큰 회사들이 내부 URL 가이드를 따로 두는 이유도 팀마다 점점 다른 스타일로 흩어지기 쉽기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- URL은 몇 달이 아니라 몇 년을 산다는 전제로 봅니다.
- 데이터베이스 모델과 리소스 모델을 분리합니다.
- 기본은 두 단계, 예외적으로 세 단계까지만 허용합니다.
- action은 가능하면 상태 변화로 표현하고, 불가피하면 `:verb` 같은 명시적 문법을 씁니다.
- 공개 식별자는 UUID나 slug처럼 불투명한 값을 선호합니다.

## 체크리스트

- [ ] 모든 컬렉션이 복수형인가?
- [ ] URL에 동사가 없는가?
- [ ] 각 리소스에 공식 URL이 하나뿐인가?
- [ ] 깊이가 세 단계 이하로 유지되는가?
- [ ] 공개 식별자가 내부 PK와 분리되어 있는가?

## 연습 문제

1. 내부 시스템 하나를 골라 컬렉션 일곱 개와 관계 다섯 개로 리소스 모델을 그려 보세요.
2. Step 4 예제에 `/users/<uid>/orders`를 추가해 보세요.
3. RPC 스타일 endpoint 다섯 개를 REST 스타일 URL로 다시 써 보세요.

## 정리와 다음 글

리소스는 API의 모양을 결정합니다. 다음 글에서는 이 리소스에 어떤 동작을 얹을지, 즉 HTTP method와 상태 코드를 다룹니다.

<!-- toc:begin -->
- [API란 무엇인가?](./01-what-is-an-api.md)
- [REST 기본](./02-rest-basics.md)
- **리소스 설계 (현재 글)**
- HTTP method와 status code (예정)
- Request와 response schema (예정)
- Pagination과 filtering (예정)
- Error response 설계 (예정)
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [REST Resource Naming Guide (restfulapi.net)](https://restfulapi.net/resource-naming/)
- [Google API Design Guide — Resource Names](https://cloud.google.com/apis/design/resource_names)
- [GitHub REST API: Issues](https://docs.github.com/en/rest/issues/issues)
- [Stripe API Reference](https://stripe.com/docs/api)

Tags: Computer Science, APIDesign, REST, Resources, URL, Backend
