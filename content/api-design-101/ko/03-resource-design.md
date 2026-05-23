---
title: "API Design 101 (3/10): 리소스 설계"
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
last_reviewed: '2026-05-15'
seo_description: 좋은 REST URL을 만드는 리소스 모델링과 명명 규칙을 실전적으로 정리합니다.
---

# API Design 101 (3/10): 리소스 설계

URL은 한 번 공개되면 데이터베이스 컬럼명보다 훨씬 오래 살아남습니다. 초기에 대충 붙인 경로 이름 하나가 나중에는 SDK, 문서, 캐시 키, 로그 필터까지 끌고 다니는 외부 계약이 됩니다.

여기서는 좋은 REST URL을 예쁜 문자열이 아니라 리소스 모델의 결과물로 봅니다. 컬렉션 경계, 하위 리소스, 식별자 노출 범위를 먼저 정해야 뒤의 메서드와 문서가 함께 안정됩니다.

![API Design 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/03/03-01-concept-at-a-glance.ko.png)
*API Design 101 3장 흐름 개요*

## 먼저 던지는 질문

- 리소스의 경계는 어떻게 나눠야 할까요?
- 명사형 이름, 복수형, 계층 구조는 어떤 원칙으로 잡아야 할까요?
- 하위 리소스는 언제 쓰고 어디까지 깊게 들어가야 할까요?

## 왜 중요한가

URL은 한 번 공개되면 바꾸는 비용이 큽니다. SDK, 캐시 키, 로그 필터, 문서 링크가 모두 그 경로를 참조하기 때문입니다. 데이터베이스 컬럼명은 마이그레이션 스크립트 하나면 바꿀 수 있지만, 공개 URL은 클라이언트 배포 주기, API 버전 정책, SEO까지 엽힙니다.

실제 사례를 하나 들겠습니다. 초기에 `/getUserOrders`라는 RPC 스타일 경로를 공개한 서비스가 있었습니다. 시간이 지나 팀이 REST로 전환하면서 `/users/{id}/orders`를 추가했지만, 기존 경로를 폐기할 수 없어 두 개의 canonical URL이 공존하게 됩니다. 캐시 무효화가 한쪽만 일어나는 버그, 문서에서 어느 URL을 써야 하는지 팀마다 다른 답을 내는 문제가 따라옵니다.

리소스 모델은 이 문제를 설계 단계에서 예방합니다. "이 도메인에서 독립적으로 식별 가능한 것은 무엇인가?"를 먼저 답하면, URL 구조는 자연스럽게 따라옵니다.

## 한눈에 보는 개념

리소스 모델링은 세 가지 질문으로 시작합니다:

1. **무엇이 독립적으로 식별 가능한가?** → 최상위 컬렉션 (`/users`, `/orders`)
2. **무엇이 다른 리소스에 종속되는가?** → 하위 리소스 (`/users/42/orders`)
3. **식별자는 무엇을 쓸 것인가?** → 숫자 PK, UUID, slug

이 세 질문의 답이 곧 URL 구조가 됩니다. 경로만 읽어도 소유 관계와 탐색 방향이 보이면 문서와 디버깅이 쉬워집니다. 반대로 평면적인 쿼리 파라미터 조합만 남으면, 무엇이 기준 리소스인지 팀마다 다르게 해석하기 쉽습니다.

| 패턴 | URL 예시 | 의미 |
|------|---------|------|
| 최상위 컬렉션 | `/articles` | 독립 리소스 목록 |
| 아이템 | `/articles/python-logging` | 단일 리소스 |
| 하위 컬렉션 | `/articles/python-logging/comments` | 종속 리소스 목록 |
| 하위 아이템 | `/articles/python-logging/comments/7` | 종속 단일 리소스 |
| 평면 조회 | `/comments?article=python-logging` | 관계가 URL에 드러나지 않음 |

## 핵심 용어

| 용어 | 정의 | URL 예시 |
|------|------|---------|
| Collection | 같은 종류의 리소스 집합 | `/users` |
| Item (Document) | 컬렉션 안의 단일 원소 | `/users/42` |
| Sub-resource | 다른 리소스에 소유·종속된 리소스 | `/users/42/orders` |
| Identifier | 리소스를 유일하게 식별하는 키 | `42`, `abc-def`, `python-logging` |
| Canonical URL | 그 리소스를 대표하는 공식 경로 (하나만 존재) | `/users/42` (not `/members/42`) |
| Singleton | 컬렉션 없이 단 하나만 존재하는 리소스 | `/users/42/profile` |

**Collection vs Item 관계를 코드로 표현하면:**

```python
# collection_vs_item.py
from flask import Flask, jsonify

app = Flask(__name__)
BOOKS = {
    "clean-code": {"title": "Clean Code", "author": "Robert C. Martin"},
    "ddd": {"title": "Domain-Driven Design", "author": "Eric Evans"},
}

@app.get("/books")              # Collection: 목록 반환
def list_books():
    return jsonify(list(BOOKS.values()))

@app.get("/books/<slug>")       # Item: 단일 리소스 반환
def get_book(slug):
    return jsonify(BOOKS[slug])
```

컬렉션은 복수형(`/books`), 아이템은 컬렉션 + 식별자(`/books/clean-code`)입니다.

## 전후 비교

**Before (동사, 단수형, 평면 구조)**

```http
GET /getUserOrder?userId=42&orderId=9
POST /createUser
POST /deleteUser?id=42
GET /searchProducts?keyword=laptop&page=2
POST /user/42/activateAccount
```

문제점:
- 동사가 경로에 들어가서 HTTP method의 의미와 중복됩니다.
- 단수형과 복수형이 섞이면 규칙을 예측할 수 없습니다.
- `?userId=42&orderId=9`처럼 쿼리에 식별자가 섞이면 캐시 키 설계가 어렵습니다.

**After (명사, 복수형, 계층 구조)**

```http
GET    /users/42/orders/9        # 42번 사용자의 9번 주문 조회
POST   /users                    # 사용자 생성
DELETE /users/42                  # 사용자 삭제
GET    /products?keyword=laptop&page=2  # 검색은 컬렉션 + 쿼리
POST   /users/42/activation       # action을 명사화
```

URL만 읽어도 리소스의 소유 관계와 조작 대상이 명확합니다.

## 실습: 리소스 모델을 만드는 다섯 단계

### 단계 1 — 도메인 명사 추출 (Start with Nouns)

도메인에서 "관리 대상"을 명사로 뽑습니다. 이때 동사("주문하다")가 아니라 결과물("주문")을 찾습니다.

```text
온라인 서점 도메인 → users, books, orders, reviews, categories
```

**함정:** `search`, `login`, `activate` 같은 동사를 명사처럼 쓰고 싶은 유혹이 있습니다. 이것은 리소스가 아니라 action이므로 별도 처리합니다 (Step 5 이후).

### 단계 2 — 식별자 결정 (Attach Identifiers)

각 컬렉션의 아이템을 구분할 식별자를 정합니다.

```text
/users/42              # 숫자 auto-increment PK
/users/u_7f3a9b2c      # 접두사 + UUID 일부 (Stripe 스타일)
/books/clean-code      # 의미 있는 slug
/orders/ORD-20260520-001  # 비즈니스 형식 코드
```

| 식별자 유형 | 장점 | 단점 |
|------------|------|------|
| 숫자 PK | 짧음, 정렬 가능 | 순서 노출, 보안 추측 가능 |
| UUID | 불투명, 충돌 없음 | 길고 읽기 불편 |
| Slug | 사람이 읽기 좋음 | 유니크 보장 로직 필요, 변경 시 URL 깨짐 |
| 접두사+UUID | 타입 구분 가능, 로그에서 식별 쉬움 | 약간 길다 |

**실무 권장:** 외부 공개 API는 UUID 또는 접두사+UUID를 씁니다. 내부 PK를 그대로 노출하면 enumerate attack에 취약합니다.

### 단계 3 — 소유 관계로 하위 리소스 결정 (Sub-resources)

"X 없이 Y가 존재할 수 있는가?"를 묻습니다.

```text
# 주문은 사용자 없이 존재할 수 없다 → 하위 리소스
/users/42/orders
/users/42/orders/9

# 리뷰는 책 없이 존재할 수 없다 → 하위 리소스
/books/clean-code/reviews
/books/clean-code/reviews/15

# 카테고리는 독립적으로 존재한다 → 최상위 컬렉션
/categories
/categories/programming
```

**판단 기준 표:**

| 질문 | Yes → | No → |
|------|-------|------|
| 부모 삭제 시 자식도 삭제되는가? | 하위 리소스 | 최상위 고려 |
| 자식을 부모 없이 조회할 일이 있는가? | 최상위 고려 | 하위 리소스 |
| 여러 부모에 속할 수 있는가? | 최상위 + 관계 링크 | 하위 리소스 |

### 단계 4 — 컬렉션 연산 구현 (Collection Operations)

```python
# resource_operations.py
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

USERS = {
    42: {"id": 42, "name": "Yeongseon", "email": "ys@example.com"},
}
ORDERS = {
    42: [  # user_id -> orders
        {"id": 9, "product": "Clean Code", "status": "shipped"},
        {"id": 10, "product": "DDD", "status": "pending"},
    ]
}

@app.get("/users")
def list_users():
    """Collection: 사용자 목록 반환"""
    return jsonify(list(USERS.values()))

@app.get("/users/<int:uid>")
def get_user(uid):
    """Item: 단일 사용자 반환"""
    if uid not in USERS:
        abort(404)
    return jsonify(USERS[uid])

@app.get("/users/<int:uid>/orders")
def list_user_orders(uid):
    """Sub-collection: 특정 사용자의 주문 목록"""
    if uid not in USERS:
        abort(404)
    return jsonify(ORDERS.get(uid, []))

@app.get("/users/<int:uid>/orders/<int:oid>")
def get_user_order(uid, oid):
    """Sub-item: 특정 사용자의 특정 주문"""
    orders = ORDERS.get(uid, [])
    order = next((o for o in orders if o["id"] == oid), None)
    if order is None:
        abort(404)
    return jsonify(order)
```

각 endpoint가 컬렉션-아이템-하위컬렉션-하위아이템 계층을 정확히 반영합니다.

### 단계 5 — 깊이 제한 (Restraint on Depth)

```text
# 좋음: 2단계
/users/42/orders

# 허용: 3단계 (명확한 소유 관계일 때)
/users/42/orders/9/items

# 나쁨: 4단계 이상
/users/42/orders/9/items/3/options/red
```

3단계를 넘어가면 다음 문제가 발생합니다:

- **클라이언트 부담**: URL 조합에 필요한 ID가 4개 이상이면 호출 전에 여러 번 조회해야 합니다.
- **권한 검증 복잡도**: 각 단계마다 소유 관계를 검증해야 해서 미들웨어가 비대해집니다.
- **캐시 효율 저하**: 경로가 길수록 캐시 hit rate가 낮아집니다.

**대안: 평면화 + 필터**

```http
# 깊은 중첩 대신
GET /users/42/orders/9/items/3/options

# 평면화 + 쿼리 파라미터
GET /order-items/3/options
GET /options?order_item=3
```

### 보너스: Singleton 리소스

컬렉션이 아닌 "딱 하나만 존재하는" 리소스도 있습니다.

```python
# singleton_resource.py
from flask import Flask, jsonify

app = Flask(__name__)
USERS = {42: {"name": "Yeongseon", "bio": "Engineer", "avatar": "/img/ys.png"}}

@app.get("/users/<int:uid>/profile")
def get_profile(uid):
    """Singleton: 사용자당 프로필은 하나뿐"""
    user = USERS.get(uid)
    return jsonify({"bio": user["bio"], "avatar": user["avatar"]})
```

Singleton은 컬렉션(`/profiles`)이 아니라 특정 부모 아래 단일 리소스(`/users/42/profile`)로 표현합니다. 목록 조회(`GET /users/42/profiles`)가 의미 없는 경우가 판단 기준입니다.

다른 예시:
- `/users/42/settings` — 사용자별 설정 (하나)
- `/repos/org/proj/readme` — 저장소별 README (하나)
- `/system/health` — 시스템 전체 상태 (하나)

## Action은 어떻게 표현하는가

리소스가 아닌 동작(activate, search, export)은 세 가지 방법으로 처리합니다:

| 방법 | URL 예시 | 적합한 상황 |
|------|---------|-----------|
| 상태 변경 PATCH | `PATCH /users/42 {"status": "active"}` | boolean/enum 토글 |
| 하위 명사 POST | `POST /users/42/activation` | 부작용이 크고 로그가 필요할 때 |
| Custom verb (Google 스타일) | `POST /documents/42:export` | 위 두 가지가 부자연스러울 때 |

어떤 방법이든 URL path에 동사가 직접 들어가지 않는 것이 핵심입니다. 동사는 HTTP method와 body가 담당합니다.
## 설계 원칙 정리

| 원칙 | 설명 | 위반 예시 |
|------|------|----------|
| 복수형 명사 | 컬렉션은 항상 복수형 | `/user` → `/users` |
| 동사 금지 | HTTP method가 동사 역할 | `/getUser` → `GET /users/{id}` |
| 계층은 소유 관계 | URL 계층 = 도메인 소유 관계 | 무관한 리소스를 중첩하지 않음 |
| 하나의 Canonical URL | 같은 리소스에 두 경로 금지 | `/user/42` + `/members/42` |
| 깊이 ≤ 3 | 그 이상은 평면화 | `/a/1/b/2/c/3/d/4` |
| 내부 구현 은닉 | DB 스키마, PK 노출 금지 | `/user_tbl/42` |
## 자주 하는 실수 다섯 가지
1. **단수형 컬렉션** — `/user`는 "한 명의 사용자"처럼 읽힙니다. 컬렉션은 `/users`처럼 복수형이어야 목록이라는 의미가 즉시 전달됩니다.
2. **URL에 동사** — `/users/42/activate`는 HTTP method와 의미가 중복됩니다. `POST /users/42/activation` 또는 `PATCH /users/42 {"status": "active"}`로 상태 변경을 표현합니다.
3. **DB 스키마 노출** — `user_tbl`, `order_seq`처럼 내부 이름이 URL에 나오면 DB 마이그레이션이 API 변경을 강제합니다. 리소스 이름은 도메인 언어를 씁니다.
4. **내부 PK 공개** — auto-increment PK를 그대로 쓰면 `/users/1`, `/users/2`... 를 순회해서 전체 사용자 수나 데이터를 추측할 수 있습니다 (IDOR 취약점).
5. **Canonical URL 중복** — `/users/42`와 `/members/42`가 같은 리소스를 가리키면 캐시 무효화가 한쪽만 일어나고, 문서에서 어느 URL을 쓸지 팀마다 달라집니다.

## 실무에서는 이렇게 드러납니다

### GitHub REST API

```http
GET /repos/{owner}/{repo}/issues/{number}
GET /repos/{owner}/{repo}/issues/{number}/comments
GET /repos/{owner}/{repo}/pulls/{number}/reviews
```

- 명사 복수형: `repos`, `issues`, `comments`, `pulls`, `reviews`
- 소유 계층: owner → repo → issue → comment
- 깊이 최대 4단계이지만, 각 단계가 명확한 소유 관계를 나타냄

### Stripe API

```http
GET /v1/customers/{id}
GET /v1/customers/{id}/sources
GET /v1/customers/{id}/subscriptions/{sub_id}
```

- 접두사 식별자: `cus_`, `sub_`, `pi_`로 타입을 URL 밖에서도 구분 가능
- 2단계 중첩이 기본, 3단계는 예외적

### Google Cloud API

```http
GET /v1/projects/{project}/locations/{location}/datasets/{dataset}
```

- Google은 깊은 중첩을 허용하지만, Resource Name 규약으로 일관성을 유지
- 모든 리소스에 `name` 필드가 full path를 포함: `projects/my-proj/locations/us-central1/datasets/ds1`

**공통점**: 규모가 큰 조직일수록 URL 네이밍 가이드를 문서화합니다. 팀이 많아지면 자연스럽게 스타일이 흩어지기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **URL은 몇 달이 아니라 몇 년을 산다는 전제로 봅니다.** 내부 리팩토링이 URL 변경을 강제하지 않도록 리소스 모델과 데이터 모델을 분리합니다.
- **"이 리소스가 5년 뒤에도 이 이름으로 불릴까?"를 먼저 묻습니다.** `payment-methods`는 살아남지만 `stripe-cards`는 Stripe 의존성이 사라지면 의미를 잃습니다.
- **기본은 두 단계, 예외적으로 세 단계까지만 허용합니다.** 깊이가 늘어날 때마다 "정말 소유 관계인가, 아니면 참조 관계인가?"를 재확인합니다.
- **Action endpoint는 가능하면 상태 변화로 표현합니다.** `POST /users/42/activate` 대신 `PATCH /users/42 {"status": "active"}`. 불가피하면 Google 스타일 `:verb`(`POST /users/42:ban`)를 씁니다.
- **공개 식별자는 UUID나 slug처럼 불투명한 값을 선호합니다.** Sequential ID는 내부 통계용으로만 남기고, 외부에는 `usr_7f3a9b2c` 같은 접두사+랜덤을 노출합니다.
- **API 리뷰 체크리스트에 URL 구조를 포함시킵니다.** 코드 리뷰에서 로직만 보고 URL은 넘어가면, 나중에 breaking change가 됩니다.

## 검증 포인트와 실패 신호

- **Expected output:** `/users`, `/users/42`, `/users/42/orders`를 나란히 두었을 때 컬렉션·아이템·하위 컬렉션 관계를 별도 설명 없이 읽을 수 있어야 합니다.
- **First check:** 같은 리소스를 `/user/42`, `/users?id=42`, `/members/42`처럼 여러 경로로 노출하면 공식 URL이 흔들리고 있다는 신호입니다.
- **Failure mode:** 중첩을 끝없이 늘리면 캐시 키, 권한 경계, 문서 예제가 함께 복잡해져서 결국 action endpoint을 뒤늦게 덧붙이게 됩니다.

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

## 처음 질문으로 돌아가기

- **리소스의 경계는 어떻게 나눠야 할까요?**
  - "X 없이 Y가 존재할 수 있는가?"를 묻습니다. 독립적으로 존재하면 최상위 컬렉션, 부모 없이 의미가 없으면 하위 리소스입니다. 부모가 삭제될 때 자식도 삭제되는가, 여러 부모에 속할 수 있는가를 추가로 확인하면 경계가 명확해집니다.
- **명사형 이름, 복수형, 계층 구조는 어떤 원칙으로 잡아야 할까요?**
  - 컬렉션은 복수형 명사, 동사는 HTTP method에 맡기고, URL 계층은 도메인의 소유 관계를 반영합니다. 동일 리소스에 canonical URL은 하나만 두고, 도메인 언어를 쓰되 내부 구현(DB 테이블명, PK)은 숨깁니다.
- **하위 리소스는 언제 쓰고 어디까지 깊게 들어가야 할까요?**
  - 부모가 삭제되면 함께 삭제되고, 부모 없이 조회할 일이 없을 때 하위 리소스로 둡니다. 깊이는 3단계까지가 실용적 한계이고, 그 이상은 평면화 + 쿼리 파라미터가 클라이언트 경험과 캐시 효율 모두에서 낫습니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
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

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [REST Resource Naming Guide (restfulapi.net)](https://restfulapi.net/resource-naming/)
- [Google API Design Guide — Resource Names](https://cloud.google.com/apis/design/resource_names)
- [GitHub REST API: Issues](https://docs.github.com/en/rest/issues/issues)
- [Stripe API Reference](https://stripe.com/docs/api)

Tags: Computer Science, APIDesign, REST, Resources, URL, Backend
