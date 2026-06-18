---
series: backend-development-101
episode: 3
title: "바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Backend
  - FastAPI
  - Architecture
  - REST
  - Python
seo_description: AI가 만든 라우터 코드에서 경계를 나누는 방법을 익히고, path/query/body 파라미터와 REST 설계 기준을 바이브코딩 관점에서 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller

이 글은 **바이브코딩을 위한 백엔드 개발 기초** 시리즈의 3번째 글입니다. AI에게 코드를 맡기기 전에 백엔드가 어떻게 동작하는지 이해해야 원하는 결과를 얻을 수 있습니다.

---

AI에게 "사용자와 주문 API 만들어줘"라고 하면 코드가 나옵니다. 엔드포인트가 세 개일 때는 괜찮습니다. 서른 개를 넘기면 문제가 생깁니다. URL 패턴이 충돌하고, 인증 규칙이 섞이고, 동일한 검증 로직이 파일마다 복제되기 시작합니다. AI가 만든 라우팅 코드를 단순히 복사해서 쓰면, 시간이 지날수록 구조가 무너집니다.

> router는 "요청 주소를 책임 단위로 배치하는 교환기"이고, controller는 "검증된 입력을 서비스 호출로 연결하는 지휘자"입니다. 교환기와 지휘자를 분리하면 경로 충돌, 인증 누락, 타입 불일치를 각각 다른 레이어에서 빠르게 추적할 수 있습니다.

## 이 글에서 다룰 문제

- router와 controller는 각각 무엇을 책임져야 할까요?
- path, query, body parameter는 언제 어떻게 나눠 써야 할까요?
- REST 스타일 엔드포인트는 어떤 기준으로 설계해야 할까요?
- AI가 만든 라우팅 코드에서 어떤 문제를 먼저 확인해야 할까요?
- 바이브코딩에서 라우팅으로 가장 자주 발생하는 문제는 무엇일까요?

## 바이브코딩과 라우팅: AI가 자주 만드는 패턴

AI에게 API를 요청하면 대체로 하나의 핸들러 함수에 인증 확인, 입력 파싱, 비즈니스 분기, DB 트랜잭션, 응답 직렬화가 모두 들어간 "200줄 핸들러"가 나옵니다. 당장은 동작하지만 확장하면 바로 문제가 생깁니다.

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

`/users/me`와 `/users/{user_id}`는 의도가 명확해 보입니다. 경로 선언 순서, 라우터 포함 순서, 변환 규칙이 달라지면 `me`가 `user_id`로 들어가 422를 만들거나, 반대로 특정 경로가 도달 불가 상태가 됩니다.

## Router와 Controller의 경계

Router와 Controller를 분리하는 목적은 계층을 늘리기 위해서가 아닙니다. 변경 이유가 다른 코드를 물리적으로 분리하기 위해서입니다.

- **Router**: URL 맵을 관리합니다. prefix, tags, 공통 의존성(인증)을 선언합니다.
- **Controller**: 요청/응답 경계에서 오케스트레이션합니다. 입력을 타입으로 검증하고, 서비스 호출 순서를 정하고, 응답 모델을 확정합니다.
- **Service**: 비즈니스 규칙을 수행합니다. Controller는 Service를 호출할 뿐입니다.

```python
# routers/orders.py
from fastapi import APIRouter, Depends
from .controllers import create_order_controller
from .dependencies import require_staff

router = APIRouter(prefix='/orders', tags=['orders'])

@router.post('', dependencies=[Depends(require_staff)])
def create_order(payload: 'OrderCreateRequest'):
    return create_order_controller(payload)
```

```python
# controllers/orders.py
from .services import order_service

def create_order_controller(payload):
    created = order_service.create_order(
        customer_id=payload.customer_id,
        items=payload.items,
        note=payload.note,
    )
    return {'id': created.id, 'status': created.status}
```

Controller가 얇으면 장애 분석도 빨라집니다. "요청 경계 오류"와 "도메인 규칙 오류"를 로그 레이어에서 쉽게 분리할 수 있기 때문입니다.

## Path, Query, Body 파라미터를 나누는 기준

파라미터 구분은 취향이 아니라 의미 계약입니다. AI가 만든 코드에서 이 부분이 잘못되면 캐시 동작, 보안 리스크, 운영 가시성이 모두 달라집니다.

| 구분 | 의미 | 대표 사용 | 보안/운영 주의 |
| --- | --- | --- | --- |
| Path | 자원 식별자 | `/users/{user_id}` | 로그/모니터링에 항상 노출됩니다 |
| Query | 조회 조건/정렬/페이지 | `?status=paid&limit=20` | 민감값 포함 시 URL 노출 위험 큽니다 |
| Body | 생성/변경 payload | POST/PUT/PATCH JSON | 스키마 검증, 크기 제한, 마스킹 정책이 핵심입니다 |

민감정보(토큰, 개인 식별값)를 Query parameter로 설계하면 웹서버 접근 로그, APM 트레이스, 브라우저 히스토리에 남습니다.

## REST 설계: 동사는 메서드에, 자원은 URL에

AI에게 API를 요청하면 동사형 URL을 만드는 경우가 있습니다. REST에서는 URL을 명사로, 동작을 HTTP 메서드로 표현합니다.

```
# 피해야 할 패턴
GET /getOrders
POST /createOrder
DELETE /deleteOrder?id=42

# 권장 패턴
GET /orders
POST /orders
DELETE /orders/{order_id}
```

## Before/After: AI 생성 라우팅 코드 개선

### Before: 메서드 기준으로 파일을 나눈 AI 코드

```python
# get_routes.py
@app.get("/users")
def list_users():
    ...

# post_routes.py
@app.post("/users")
def create_user():
    ...
```

기능 변경 시 항상 여러 파일을 동시에 열어야 합니다.

### After: 도메인 기준으로 구조화

```python
app/
  api/
    routers/
      users.py     # GET + POST + PATCH + DELETE 모두
      orders.py
    controllers/
      users.py
      orders.py
  domain/
    users/
      service.py
      repository.py
```

주문 정책 변경 시 `domain/orders` 주변에서 끝납니다.

## AI가 만든 라우팅 코드에서 자주 하는 실수

| 실수 | 왜 발생하는가 | 왜 문제인가 | AI에게 수정 요청 방법 |
| --- | --- | --- | --- |
| 동사형 URL(`/createUser`) | 빠른 구현 습관 | 메서드 의미와 중복, 일관성 붕괴 | "URL은 명사 리소스로, 동작은 HTTP 메서드로 설계해줘" |
| Controller 비대화 | "한 곳에서 끝내자" 심리 | 테스트 불가, 변경 파급 증가 | "controller는 service 호출만 하고 비즈니스 로직은 service로 옮겨줘" |
| Query에 민감정보 전달 | 디버깅 편의 우선 | URL 노출면 확대 | "인증 토큰은 헤더로, 개인정보는 body로 전달해줘" |
| 무분별한 중첩 리소스 | 관계 표현 집착 | 권한/인덱스/충돌 복잡도 증가 | "중첩 리소스는 2단계로 제한해줘" |

## AI 팁: 라우팅 구조를 AI에게 요청하는 방법

**도메인 기준 구조 요청**: "사용자와 주문 도메인을 분리해서 각 도메인별로 router, controller, service 파일을 만들어줘."

**인증 정책 명시**: "인증이 필요한 라우터 그룹과 공개 라우터 그룹을 APIRouter로 분리해줘. 인증은 Depends를 사용해줘."

**버전 관리**: "API 버전을 /v1 prefix로 관리하도록 라우터를 구성해줘."

## 체크리스트

- [ ] router와 controller의 책임 차이를 설명할 수 있습니다.
- [ ] path/query/body 파라미터를 상황에 맞게 선택할 수 있습니다.
- [ ] REST URL 설계 규칙(명사 리소스 + HTTP 메서드)을 적용할 수 있습니다.
- [ ] AI가 만든 라우팅 코드에서 동사형 URL과 비대한 핸들러를 발견할 수 있습니다.
- [ ] 도메인 기준 프로젝트 구조를 설명할 수 있습니다.

## 처음 질문으로 돌아가기

- **router와 controller는 각각 무엇을 책임져야 할까요?**
  - router는 URL 네임스페이스와 공통 정책(인증, 태그)을 선언합니다. controller는 입력 변환과 서비스 호출 순서를 담당합니다. 비즈니스 로직은 service로 내려갑니다.
- **path, query, body parameter는 언제 어떻게 나눠 써야 할까요?**
  - 자원 식별에는 path, 조회 조건에는 query, 생성/변경 데이터에는 body를 씁니다. 민감정보는 반드시 body나 헤더를 사용합니다.
- **REST 스타일 엔드포인트는 어떤 기준으로 설계해야 할까요?**
  - URL은 명사(복수형 리소스), 동작은 HTTP 메서드(GET/POST/PATCH/DELETE)로 표현합니다. `/createOrder`가 아니라 `POST /orders`입니다.

## 정리

라우팅은 단순히 URL을 함수에 연결하는 작업이 아닙니다. 책임 경계를 분리하고, 인증 정책을 일관되게 적용하며, API 계약을 관리하는 설계입니다. AI가 만든 라우팅 코드를 그대로 쓰면 처음에는 동작하지만 서비스가 커질수록 관리가 어려워집니다. router/controller/service를 분리하는 원칙을 AI에게 명시하면 훨씬 나은 코드를 얻을 수 있습니다.

## 참고 자료

### 공식 문서

- [FastAPI Path operations](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)
- [REST API Tutorial](https://restfulapi.net/)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 백엔드 개발 기초 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [바이브코딩을 위한 백엔드 개발 기초 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- **바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller (현재 글)**
- [바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer](./04-service-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer](./05-database-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- [바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- [바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트](./08-testing-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (9/10): 백엔드 배포](./09-deploying-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (10/10): 운영 가능한 백엔드 구조](./10-production-ready-backend.md)

<!-- toc:end -->

Tags: 바이브코딩, Backend, FastAPI, Architecture, REST, Python
