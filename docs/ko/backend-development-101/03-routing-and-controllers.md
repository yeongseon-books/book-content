---
series: backend-development-101
episode: 3
title: Routing과 Controller
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - FastAPI
  - Architecture
  - REST
  - Python
seo_description: Routing과 Controller를 분리해 요청을 깔끔하게 받는 법 — path/query/body 파라미터를 한 번에 정리.
last_reviewed: '2026-05-04'
---

# Routing과 Controller

> Backend Development 101 시리즈 (3/10)


## 이 글에서 다룰 문제

작은 프로젝트에서는 한 파일에 모두 넣어도 동작합니다. 하지만 endpoint가 늘면 *한 파일이 곧 지옥* 이 됩니다. 처음부터 layer를 나눠 두면 새 기능을 추가할 때마다 *어디에 둘지* 가 자명해집니다.

> 좋은 구조는 *어디에 코드를 둘지 고민하지 않게* 만들어 줍니다.

## 전체 흐름
```mermaid
flowchart LR
    Req["Request"] --> Router["Router"]
    Router --> Ctrl["Controller"]
    Ctrl --> Service["Service"]
    Service --> Repo["Repository"]
```

Router는 *지도* , Controller는 *접수창구* , Service는 *전문가* 입니다.

## Before/After

**Before (한 파일에 다 넣기)**

```python
# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users(): ...

@app.get("/orders")
def list_orders(): ...

@app.get("/products")
def list_products(): ...
```

**After (모듈 별 router)**

```python
# routers/users.py
from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def list_users():
    return []

# main.py
from fastapi import FastAPI
from routers import users, orders
app = FastAPI()
app.include_router(users.router)
app.include_router(orders.router)
```

기능별로 파일이 나뉘니 *어디를 고쳐야 할지* 가 명확해집니다.

## 5단계로 라우팅 정돈하기

### 1단계 — Path 파라미터

```python
# 1_path.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

### 2단계 — Query 파라미터

```python
# 2_query.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users(active: bool = True, limit: int = 10):
    return {"active": active, "limit": limit}
```

### 3단계 — Body로 JSON 받기

```python
# 3_body.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(payload: UserIn):
    return {"id": 1, **payload.model_dump()}
```

### 4단계 — Router 분리

```python
# routers/products.py
from fastapi import APIRouter
router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products():
    return []

@router.get("/{pid}")
def get_product(pid: int):
    return {"id": pid}
```

### 5단계 — Controller에서 service 호출

```python
# controllers/user_controller.py
from services.user_service import UserService

class UserController:
    def __init__(self, svc: UserService):
        self.svc = svc

    def create(self, payload):
        return self.svc.register(payload.name, payload.age)
```

Controller는 *얇게* 유지합니다 — 검증하고, service에 위임할 뿐.

## 이 코드에서 주목할 점

- Path는 *식별* 에, query는 *필터* 에 씁니다.
- Body는 POST/PUT/PATCH에서만 의미가 있습니다.
- `tags` 는 OpenAPI 문서를 *그룹화* 합니다.

## 자주 하는 실수 5가지

1. **모든 데이터를 query string에 넣는다.** 검색 조건은 query, 새 자원은 body가 맞습니다.
2. **Controller에 비즈니스 로직을 쓴다.** Service로 옮겨야 재사용·테스트가 쉽습니다.
3. **`/getUsers`, `/createUser` 처럼 동사 path를 쓴다.** REST는 *명사 + HTTP method* 입니다.
4. **검증 없이 받은 값을 DB에 직접 넣는다.** Pydantic으로 *항상* 모델링합니다.
5. **상태 변경을 GET으로 한다.** GET은 *안전(safe)* 해야 합니다.

## 실무에서는 이렇게 쓰입니다

큰 백엔드는 도메인별로 router 디렉터리(`routers/orders.py`, `routers/payments.py`)를 둡니다. 새 기능이 들어오면 *어떤 router에 어떤 path를 추가할지* 만 결정하면 됩니다. 이 단순한 규칙 하나가 코드베이스 수명을 몇 년 늘립니다.

## 체크리스트

- [ ] Path / query / body 파라미터를 구분할 수 있다.
- [ ] APIRouter로 router를 분리할 수 있다.
- [ ] REST 명사 path를 설계할 수 있다.
- [ ] Controller에서 service를 호출하는 흐름을 안다.
- [ ] OpenAPI 문서(`/docs`)를 열어 봤다.

## 정리 및 다음 단계

Router는 *지도* , Controller는 *접수창구* 입니다. 다음 글에서는 그 안쪽에서 *비즈니스 규칙* 을 다루는 Service Layer를 봅니다.

<!-- toc:begin -->
- [백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [HTTP 서버 만들기](./02-building-an-http-server.md)
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

- [FastAPI Path operations](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [REST API Tutorial](https://restfulapi.net/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
