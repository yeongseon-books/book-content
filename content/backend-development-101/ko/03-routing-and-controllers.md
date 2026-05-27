---
series: backend-development-101
episode: 3
title: "Backend Development 101 (3/10): Routing과 Controller"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - FastAPI
  - Architecture
  - REST
  - Python
seo_description: 라우터와 컨트롤러를 분리하여 백엔드 엔드포인트를 깔끔하게 설계하고, 입력 파라미터와 REST 스타일의 설계를 익힙니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (3/10): Routing과 Controller

엔드포인트가 세 개일 때는 구조가 없어도 서비스가 돌아갑니다. 엔드포인트가 서른 개를 넘기면 코드가 먼저 무너집니다. URL 패턴이 충돌하고, 인증 규칙이 섞이고, 동일한 검증 로직이 파일마다 복제되기 시작합니다. 장애는 종종 비즈니스 로직이 아니라 요청을 어디로 보낼지 정하는 경계에서 시작됩니다.

이 글은 Backend Development 101 시리즈의 3번째 글입니다.

![Backend Development 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/03/03-01-concept-at-a-glance.ko.png)
*Backend Development 101 3장 흐름 개요*

## 먼저 던지는 질문

- router와 controller는 각각 무엇을 책임져야 할까요?
- path, query, body parameter는 언제 어떻게 나눠 써야 할까요?
- REST 스타일 엔드포인트는 어떤 기준으로 설계해야 할까요?

## 라우팅은 결국 디스패치 문제입니다

> 정신 모델: router는 "요청 주소를 책임 단위로 배치하는 교환기"이고, controller는 "검증된 입력을 서비스 호출로 연결하는 지휘자"입니다. 교환기와 지휘자를 분리하면 경로 충돌, 인증 누락, 타입 불일치를 각각 다른 레이어에서 빠르게 추적할 수 있습니다.

라우팅은 "URL 문자열을 함수에 연결하는 일"로 보이기 쉽지만, 운영 환경에서는 디스패치 문제에 가깝습니다. 디스패치는 들어온 요청을 가장 정확한 규칙에 매칭하고, 충돌이 있으면 일관된 방식으로 실패시키는 시스템입니다. 이 관점이 중요한 이유는 다음과 같습니다.

- URL은 사람이 읽는 주소이면서 서버 입장에서는 정규화 대상 문자열입니다.
- 매칭 순서와 우선순위가 조금만 어긋나도 전혀 다른 핸들러가 실행됩니다.
- 경로 파라미터 타입이 맞지 않으면 애플리케이션 로직에 진입하기 전에 422가 대량 발생합니다.
- 문서(OpenAPI)와 실제 동작이 어긋나면 클라이언트 팀이 잘못된 계약을 기준으로 개발합니다.

아래처럼 단순해 보이는 두 경로도 디스패치 순서와 타입 규칙을 고려하지 않으면 사고가 납니다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get('/users/me')
def get_me():
    return {'scope': 'self'}

@app.get('/users/{user_id}')
def get_user(user_id: int):
    return {'id': user_id}
```

`/users/me`와 `/users/{user_id}`는 의도가 명확해 보입니다. 경로 선언 순서, 라우터 포함 순서, 변환 규칙이 달라지면 `me`가 `user_id`로 들어가 422를 만들거나, 반대로 특정 경로가 도달 불가 상태가 됩니다. 디스패치를 설계할 때는 "읽기 좋은 URL"만이 아니라 "충돌 없는 매칭"을 동시에 설계해야 합니다.

## Router와 Controller의 경계

Router와 Controller를 분리하는 목적은 계층을 늘리기 위해서가 아닙니다. 변경 이유가 다른 코드를 물리적으로 분리하기 위해서입니다.

- Router는 URL 맵을 관리합니다. 어떤 prefix 아래 어떤 엔드포인트가 존재하는지 선언합니다.
- Controller는 요청/응답 경계에서 오케스트레이션합니다. 입력을 타입으로 검증하고, 서비스 호출 순서를 정하고, 응답 모델을 확정합니다.
- Service는 비즈니스 규칙을 수행합니다. 가격 계산, 상태 전이, 권한 도메인 규칙 같은 핵심 정책이 여기에 있어야 합니다.

실무에서 많이 보이는 안티패턴은 "200줄 핸들러"입니다. 인증 확인, 입력 파싱, 비즈니스 분기, DB 트랜잭션, 응답 직렬화가 한 함수에 몰립니다. 이 함수는 테스트도 어렵고 재사용도 어렵습니다. 해결은 거창하지 않습니다. Router는 선언, Controller는 조립, Service는 규칙으로 쪼개면 됩니다.

```python
# routers/orders.py
from fastapi import APIRouter, Depends
from .controllers import create_order_controller
from .dependencies import require_staff

router = APIRouter(prefix='/orders', tags=['orders'])

@router.post('', dependencies=[Depends(require_staff)])
def create_order(payload: 'OrderCreateRequest'):
    # 컨트롤러 호출만 담당합니다.
    return create_order_controller(payload)
```

```python
# controllers/orders.py
from .services import order_service

def create_order_controller(payload):
    # 입력 객체를 서비스 포맷으로 변환하고 호출 순서를 정합니다.
    created = order_service.create_order(
        customer_id=payload.customer_id,
        items=payload.items,
        note=payload.note,
    )
    return {'id': created.id, 'status': created.status}
```

Controller가 얇으면 장애 분석도 빨라집니다. "요청 경계 오류"와 "도메인 규칙 오류"를 로그 레이어에서 쉽게 분리할 수 있기 때문입니다.

## Path, Query, Body 파라미터를 나누는 기준

파라미터 구분은 취향이 아니라 의미 계약입니다. 같은 데이터를 어디에 두느냐에 따라 캐시 동작, 관측 가능성, 보안 리스크가 달라집니다.

| 구분 | 의미 | 대표 사용 | 캐시/인프라 영향 | 보안/운영 주의 |
| --- | --- | --- | --- | --- |
| Path | 자원 식별자 | `/users/{user_id}` | URL 자체가 캐시 키에 포함됩니다 | 로그/모니터링에 항상 노출됩니다 |
| Query | 조회 조건/정렬/페이지 | `?status=paid&limit=20` | CDN/프록시가 쿼리별 캐시를 분기합니다 | 민감값 포함 시 URL 노출 위험이 큽니다 |
| Body | 생성/변경 payload | POST/PUT/PATCH JSON | 기본적으로 URL 캐시 키와 분리됩니다 | 스키마 검증, 크기 제한, 마스킹 정책이 핵심입니다 |

결정 테이블로 보면 더 선명해집니다.

| 질문 | Yes면 | No면 |
| --- | --- | --- |
| 이 값이 없으면 특정 자원을 지목할 수 없는가? | Path | 다음 질문으로 이동 |
| 이 값이 목록 조회 조건 또는 보기 옵션인가? | Query | 다음 질문으로 이동 |
| 이 값이 생성/수정 데이터 자체인가? | Body | 모델링 재검토 |
| 민감정보인가(토큰, 주민번호, 카드정보 등)? | Body + 별도 보호 정책 | Query/Path 가능 여부 재검토 |

운영 관점에서 중요한 포인트는 "URL 노출면"입니다. 웹서버 접근 로그, APM 트레이스, WAF 로그, 브라우저 히스토리, 리퍼러에 URL이 남을 수 있습니다. 비밀번호 재설정 토큰, 개인 식별값, 내부 키를 Query로 보내면 노출면이 필요 이상으로 넓어집니다.

### 캐싱과 검색성의 트레이드오프

Query는 캐시 친화적입니다. `GET /products?category=shoe&page=2`는 조회 캐시를 만들기 쉽습니다. Body는 일반적으로 조회 조건에 쓰지 않으므로 캐시 계층과 자연스럽게 맞지 않습니다. 반대로 Body는 큰 구조적 데이터를 안전하게 전달하기 좋습니다.

- 읽기 최적화 API: Query 중심 설계가 유리합니다.
- 복잡한 검색 조건: Query 길이 제한, 로그 노출, 인코딩 복잡도를 고려해 POST 검색 엔드포인트를 분리하기도 합니다.
- 민감정보 포함 조건: URL을 피하고 Body로 옮기는 편이 운영 리스크를 줄입니다.

## REST 설계: 동사는 메서드에, 자원은 URL에

REST에서 가장 먼저 지켜야 할 규칙은 URL을 명사로 설계하는 것입니다. 동작은 HTTP 메서드가 표현합니다.

- `GET /orders` : 주문 목록 조회
- `GET /orders/{order_id}` : 주문 단건 조회
- `POST /orders` : 주문 생성
- `PATCH /orders/{order_id}` : 주문 일부 변경
- `DELETE /orders/{order_id}` : 주문 삭제

`/getOrders`, `/createOrder`, `/deleteOrder` 같은 경로는 당장은 빨리 만들 수 있어도 시간이 지날수록 메서드 의미와 충돌합니다. 클라이언트 SDK 자동 생성, 문서 그룹핑, 권한 규칙 선언이 모두 불규칙해집니다.

### Idempotency를 설계에 반영해야 합니다

멱등성(idempotency)은 "같은 요청을 여러 번 보내도 결과 상태가 같아야 하는가"를 의미합니다.

| 메서드 | 일반적 의미 | 멱등성 |
| --- | --- | --- |
| GET | 조회 | 멱등 |
| PUT | 전체 대체 | 멱등 |
| DELETE | 삭제 | 멱등 |
| POST | 생성/명령 | 비멱등(기본) |
| PATCH | 부분 수정 | 케이스별 |

결제, 재고 차감, 쿠폰 발급처럼 재시도가 발생하는 흐름에서는 멱등성 키(`Idempotency-Key`)를 별도로 설계해야 합니다. "HTTP 메서드만 맞췄다"로 끝나지 않습니다.

### 복수형 리소스와 중첩 리소스

복수형(`users`, `orders`)은 컬렉션을 자연스럽게 표현합니다. 중첩 리소스는 관계를 드러낼 때만 제한적으로 사용합니다.

- 적절: `/users/{user_id}/orders` (사용자 기준 주문 조회)
- 과도: `/users/{user_id}/orders/{order_id}/items/{item_id}/events/{event_id}`

중첩 깊이가 깊어질수록 권한 검사, 인덱스 전략, 라우팅 충돌 가능성이 급격히 높아집니다. 식별자 한두 개로 충분히 조회 가능하면 평평한 경로와 Query 조합이 더 운영 친화적입니다.

## FastAPI APIRouter를 실무형으로 쓰는 방법

`APIRouter`는 파일 분리를 위한 도구를 넘어, 경계 정책을 선언하는 단위입니다.

```python
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.schemas.orders import OrderCreateRequest, OrderResponse
from app.controllers.orders import create_order_controller, list_orders_controller

router = APIRouter(
    prefix='/orders',
    tags=['orders'],
    dependencies=[Depends(get_current_user)],
)

@router.get('', response_model=list[OrderResponse])
def list_orders(status: str | None = None, page: int = 1, limit: int = 20):
    # 조회 조건만 컨트롤러로 전달합니다.
    return list_orders_controller(status=status, page=page, limit=limit)

@router.post('', response_model=OrderResponse)
def create_order(payload: OrderCreateRequest):
    # 생성 payload는 Body 모델로 검증합니다.
    return create_order_controller(payload)
```

핵심은 세 가지입니다.

- `prefix`: URL 네임스페이스를 강제합니다.
- `tags`: OpenAPI 그룹을 명확히 만들어 문서 탐색 비용을 낮춥니다.
- `dependencies`: 라우터 단위 공통 정책(인증, 조직 컨텍스트, 감사 로깅)을 선언합니다.

`main.py`에서는 `include_router`로 조립합니다.

```python
from fastapi import FastAPI
from app.api.routers import users_router, orders_router

app = FastAPI(title='Backend Development 101 API')

app.include_router(users_router)
app.include_router(orders_router)
```

라우터 조립 순서와 prefix 중복 여부를 점검하지 않으면 충돌이 발생합니다. 동일 메서드+동일 경로가 두 번 선언되면 초기화 단계에서 오류가 나거나, 팀 규칙에 따라 마지막 선언만 유효해지는 상황이 생깁니다. "도메인별 분리"와 "글로벌 조립 점검"은 항상 같이 가야 합니다.

## 프로젝트 구조는 메서드 기준이 아니라 도메인 기준으로

초기 프로젝트에서 자주 보이는 구조는 다음과 같습니다.

- `get_routes.py`
- `post_routes.py`
- `put_routes.py`

이 구조는 단기적으로 파일을 나눈 느낌을 주지만, 기능 변경 시 항상 여러 파일을 동시에 열어야 합니다. 사용자 도메인을 수정하는데 GET/POST/PATCH 파일을 모두 건드리게 됩니다.

도메인 중심 구조가 더 오래 버팁니다.

```text
app/
  api/
    routers/
      users.py
      orders.py
    controllers/
      users.py
      orders.py
    dependencies/
      auth.py
  domain/
    users/
      service.py
      repository.py
    orders/
      service.py
      repository.py
  schemas/
    users.py
    orders.py
```

이 구조의 장점은 변경의 지역성입니다.

- 주문 정책 변경: `domain/orders` 주변에서 끝납니다.
- 주문 API 계약 변경: `schemas/orders.py`, `api/controllers/orders.py` 중심으로 끝납니다.
- 주문 라우팅 변경: `api/routers/orders.py`만 먼저 보면 됩니다.

## 버전 전략: `/v1` prefix vs Header 기반

API 버전 관리는 "어떤 방식이 정답"이 아니라 소비자와 운영 환경을 기준으로 고르는 문제입니다.

| 전략 | 예시 | 장점 | 단점 | 적합한 상황 |
| --- | --- | --- | --- | --- |
| URL Prefix | `/v1/orders` | 명시적이고 디버깅이 쉽습니다 | URL이 길어지고 라우터 중복이 생깁니다 | 외부 공개 API, 다수 클라이언트 |
| Header 기반 | `Accept: application/vnd.acme.v2+json` | URL이 깔끔합니다 | 프록시/캐시/테스트에서 가시성이 떨어집니다 | 내부 API, 강한 게이트웨이 통제 |

대부분 팀은 `/v1` prefix를 먼저 택합니다. 이유는 단순합니다. 로그와 모니터링에서 버전을 즉시 식별할 수 있고, 운영자가 curl 한 줄로 재현하기 쉽습니다.

FastAPI에서는 상위 prefix 라우터를 조립하는 방식으로 관리합니다.

```python
from fastapi import APIRouter
from app.api.v1 import users as v1_users
from app.api.v2 import users as v2_users

api_router = APIRouter()
api_router.include_router(v1_users.router, prefix='/v1')
api_router.include_router(v2_users.router, prefix='/v2')
```

버전은 늘어나는 것이 정상입니다. 중요한 것은 "폐기 정책"입니다. deprecation 헤더, 문서 공지, 마이그레이션 기간을 함께 운영해야 합니다.

## 운영에서 자주 만나는 네 가지 사고 시나리오

### 시나리오 1: 200줄 핸들러가 감당 불가 상태가 된 경우

징후는 명확합니다. 같은 함수에서 인증, 파싱, 권한, 비즈니스 규칙, 외부 API 호출, 에러 매핑까지 수행합니다. 수정 하나가 회귀 버그를 만듭니다.

해법은 기능 분해 순서를 정하는 것입니다.

- 1단계: 입력 모델과 응답 모델을 분리합니다.
- 2단계: 비즈니스 로직을 서비스로 이동합니다.
- 3단계: 컨트롤러는 호출 순서와 에러 매핑만 남깁니다.
- 4단계: 라우터는 의존성과 메타데이터만 선언합니다.

### 시나리오 2: 인증이 일부 라우트에만 적용되어야 하는 경우

`/users/me`는 인증 필요, `/users/public-profile/{id}`는 공개일 수 있습니다. 전역 미들웨어로 강제하면 예외 처리가 난해해집니다. 라우터 수준 의존성이 효과적입니다.

```python
private_router = APIRouter(prefix='/users', dependencies=[Depends(get_current_user)])
public_router = APIRouter(prefix='/users')
```

같은 prefix를 쓰더라도 경로 집합을 명확히 분리하면 정책이 코드 구조에 드러납니다.

### 시나리오 3: 라우터 간 URL 충돌

팀이 커지면 다른 개발자가 동일 경로를 선언하는 일이 반드시 생깁니다. 충돌은 코드리뷰에서만 잡지 못합니다.

- 라우터 등록 표를 유지합니다.
- CI에서 OpenAPI 스펙 diff를 검사합니다.
- `include_router` 조립 파일을 단일 진입점으로 고정합니다.

### 시나리오 4: Path 타입 불일치로 422 로그가 급증

`/orders/{order_id}`에 문자열을 보내는 클라이언트 버그는 흔합니다. 서버는 정상적으로 422를 돌려주지만, 운영 지표에서는 에러 폭주처럼 보일 수 있습니다.

대응은 두 갈래입니다.

- 서버: 타입 힌트와 에러 메시지를 명확히 유지하고, 422 비율을 별도 모니터링합니다.
- 클라이언트: SDK 타입/유효성 검사를 강화해 잘못된 요청을 전송 전에 차단합니다.

## 타입 선언이 OpenAPI 품질을 결정합니다

FastAPI의 강점은 타입 기반 문서 자동화입니다. 라우팅과 컨트롤러를 제대로 분리하고 타입을 정확히 선언하면 `/docs`가 팀 계약 문서로 동작합니다.

```python
from pydantic import BaseModel, Field

class OrderCreateRequest(BaseModel):
    customer_id: int = Field(gt=0)
    item_ids: list[int] = Field(min_length=1)
    note: str | None = Field(default=None, max_length=200)

class OrderResponse(BaseModel):
    id: int
    status: str
```

이 선언만으로도 다음이 자동으로 정리됩니다.

- 필수/선택 필드 구분
- 숫자 제약, 문자열 길이 제약
- 요청/응답 예시 생성 기반
- 422 오류 케이스의 구조화

문서가 정확하면 QA와 프론트엔드 팀은 추측 대신 계약으로 개발할 수 있습니다. 타입을 소홀히 하면 API 문서는 장식이 됩니다.

## 라우팅 설계를 팀 규칙으로 고정하는 방법

개별 개발자의 취향에 맡겨두면 라우팅 스타일은 금방 분열합니다. 팀 규칙으로 고정해야 품질이 유지됩니다.

| 항목 | 권장 규칙 | 검증 방법 |
| --- | --- | --- |
| 리소스 네이밍 | 복수형 명사(`users`, `orders`) | 코드리뷰 체크리스트 |
| 경로 파라미터 | 식별자만 허용(`{user_id}`) | 타입 힌트 + 테스트 |
| 조회 파라미터 | 필터/정렬/페이지로 제한 | OpenAPI 파라미터 검사 |
| 생성/수정 입력 | Body 모델 필수 | Pydantic 스키마 검사 |
| 컨트롤러 길이 | 30~50줄 내 유지 권장 | 정적 분석 + 리뷰 |
| 라우터 조립 | 단일 진입점 파일 유지 | CI에서 경로 중복 검사 |

규칙은 문서만으로 유지되지 않습니다. PR 템플릿에 넣고, CI에서 기계적으로 검사해야 실제 습관이 됩니다.

## 단계적 리팩터링 예시: 거친 API를 안정적인 구조로

이미 운영 중인 API를 한 번에 갈아엎는 방식은 실패 확률이 높습니다. 라우팅/컨트롤러 구조는 보통 다음 순서가 안전합니다.

1. 엔드포인트 동작을 바꾸지 않고 응답 모델부터 명시합니다.
2. 비대한 핸들러에서 순수 비즈니스 함수만 서비스로 추출합니다.
3. 라우터 파일을 도메인 기준으로 쪼개고 `include_router`로 재조립합니다.
4. 인증/권한 규칙을 라우터 의존성으로 이동합니다.
5. OpenAPI diff와 회귀 테스트로 계약 변경 여부를 확인합니다.

이 접근의 장점은 "동작은 유지하고 구조만 개선"할 수 있다는 사실입니다. 고객 영향 없이 기술부채를 줄일 수 있습니다.

## 성능과 관측성 관점의 라우팅 설계

라우팅 설계는 단지 코드 미학이 아니라 성능과 관측성에도 직접 영향을 줍니다.

- **로그 카드inality 관리**: Path 변수값이 과도하면 지표 레이블 cardinality가 폭증합니다.
- **캐시 효율**: Query 조합이 무한히 늘어나면 캐시 적중률이 급감합니다.
- **오류 분류 정확도**: 4xx(클라이언트 입력 오류)와 5xx(서버 오류)를 컨트롤러에서 명확히 분리해야 알람 품질이 올라갑니다.
- **추적 가능성**: 도메인 라우터 단위 태그를 유지하면 OpenTelemetry 스팬 분석이 쉬워집니다.

특히 422 비율이 높아질 때는 "서버가 불안정하다"가 아니라 "클라이언트 계약이 깨졌다"는 신호일 수 있습니다. 라우팅과 타입 계약을 관측지표와 함께 운영해야 원인을 빠르게 분리할 수 있습니다.

## 자주 하는 실수와 왜 문제인지

| 실수 | 왜 발생하는가 | 왜 문제인가 | 개선 방법 |
| --- | --- | --- | --- |
| 동사형 URL(`/createUser`) | 빠른 구현 습관 | 메서드 의미와 중복, 일관성 붕괴 | 명사 리소스 + HTTP 메서드로 재설계 |
| Controller 비대화 | "한 곳에서 끝내자" 심리 | 테스트 불가, 변경 파급 증가 | 서비스로 규칙 이동, 컨트롤러 얇게 유지 |
| Query에 민감정보 전달 | 디버깅 편의 우선 | URL 노출면 확대 | Body/헤더로 이동, 마스킹 정책 적용 |
| 도메인 아닌 메서드 기준 파일 분리 | 초기 단순화 | 기능 단위 탐색이 어려움 | users/orders 도메인 기준 재구성 |
| 무분별한 중첩 리소스 | 관계 표현 집착 | 권한/인덱스/충돌 복잡도 증가 | 깊이 제한, 평평한 경로 병행 |
| 버전 폐기 계획 부재 | "나중에 정리" | 레거시 영구 유지, 운영비 증가 | 지원 기간·폐기 일정·알림 정책 명시 |

시니어 관점의 핵심은 "지금의 편의가 6개월 뒤 운영비를 어떻게 바꾸는가"입니다. 라우팅과 컨트롤러는 처음부터 정확히 분리해 두는 편이 결국 더 빠릅니다.

## 실무 체크리스트

- 새 엔드포인트를 추가할 때 먼저 리소스 명사와 메서드 조합을 확정했는가
- Path/Query/Body의 의미 계약이 문서와 코드에서 일치하는가
- 라우터 단위 인증/권한 정책이 중복 없이 선언되었는가
- 컨트롤러 함수가 입력 변환과 호출 오케스트레이션을 넘어서지 않는가
- 응답 모델과 오류 모델이 OpenAPI에서 검증 가능한 형태인가
- 버전 정책(`/v1` 또는 헤더)과 폐기 정책이 운영 문서에 있는가

## 점검 체크리스트

- [ ] 엔드포인트가 명사 리소스 + HTTP 메서드 조합으로 설계되어 있습니다.
- [ ] path/query/body 파라미터가 의미 계약에 맞게 분리되어 있습니다.
- [ ] 라우터에 공통 의존성(인증/권한/컨텍스트)이 선언되어 있습니다.
- [ ] 컨트롤러가 서비스 오케스트레이션 이상으로 비대해지지 않았습니다.
- [ ] 요청/응답 모델이 OpenAPI 문서에서 정확히 표시됩니다.
- [ ] 버전 정책과 폐기 정책이 실제 운영 절차와 연결되어 있습니다.

## 처음 질문으로 돌아가기

- **router와 controller는 각각 무엇을 책임져야 할까요?**
  - router는 URL 패턴을 충돌 없이 매핑하고 공통 의존성(인증, 컨텍스트)을 선언하는 경계입니다. controller는 검증된 입력을 받아 서비스 호출 순서를 조립하고 응답 계약을 확정하는 얇은 오케스트레이터입니다.
- **path, query, body parameter는 언제 어떻게 나눠 써야 할까요?**
  - 자원 식별자는 path, 조회 조건과 정렬/페이지 옵션은 query, 생성·수정 payload와 민감 데이터는 body로 분리합니다. 이 구분은 캐시 키 구성, URL 노출면, 422 오류 관측성까지 직접 바꿉니다.
- **REST 스타일 엔드포인트는 어떤 기준으로 설계해야 할까요?**
  - URL은 복수형 명사 리소스로 두고 동작 의미는 HTTP 메서드로 표현합니다. 멱등성, 중첩 깊이, 버전 전략, 폐기 정책을 함께 설계해야 운영에서 예측 가능한 API가 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- **Routing과 Controller (현재 글)**
- Service Layer (예정)
- Database Layer (예정)
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [FastAPI Path operations](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [REST API Tutorial](https://restfulapi.net/)

Tags: Backend, FastAPI, Architecture, REST, Python
