---
series: secure-coding-101
episode: 4
title: "Secure Coding 101 (4/10): 인가와 권한"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Authorization
  - RBAC
  - ABAC
  - LeastPrivilege
  - SecureCoding
seo_description: RBAC, ABAC, IDOR 방어, least privilege, 그리고 안전한 인가 흐름의 5단계
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (4/10): 인가와 권한

사용자가 로그인했다는 사실만으로는 아직 아무것도 끝나지 않습니다. 그 사용자가 이 문서를 읽어도 되는지, 저 게시글을 수정해도 되는지, 다른 사람 주문 내역을 내려받아도 되는지는 별도의 판단이 필요합니다. 보안 사고에서 가장 자주 보이는 broken access control도 바로 이 지점에서 시작합니다.

이 글은 Secure Coding 101 시리즈의 4번째 글입니다.

여기서는 인가를 역할 이름 몇 개로 끝내지 않고, 요청마다 자원과 행위를 함께 보는 서버 쪽 결정으로 정리하겠습니다. 이 관점을 잡으면 RBAC와 ABAC의 차이, IDOR 방어, 목록 API 필터링, 기본 거부 정책이 왜 한 세트로 묶이는지도 자연스럽게 보입니다.


![Secure Coding 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/04/04-01-concept-at-a-glance.ko.png)
*Secure Coding 101 4장 흐름 개요*

## 먼저 던지는 질문

- RBAC와 ABAC는 어떤 차이가 있을까요?
- IDOR는 왜 흔하고도 위험한 인가 취약점일까요?
- 인가 판단은 라우트 수준과 자원 수준에서 어떻게 나눠 봐야 할까요?

## 왜 중요한가

OWASP Top 10에서 broken access control이 상위에 반복해서 등장하는 이유는 단순합니다. UI에서 버튼을 숨기는 것으로는 아무것도 막을 수 없기 때문입니다. 공격자는 브라우저 화면을 거치지 않고 직접 API를 호출할 수 있고, URL의 ID 하나만 바꿔도 남의 자원에 접근할 수 있습니다.

인가가 특히 까다로운 이유는 기능 요구사항과 강하게 얽혀 있기 때문입니다. 관리자, 편집자, 일반 사용자처럼 큰 역할만 나눠 두면 처음에는 쉬워 보이지만, 실제 서비스에서는 자원 소유권, 부서, 시간대, 승인 상태 같은 조건이 금방 붙습니다. 그래서 인가는 화면 정책이 아니라 코드와 데이터가 만나는 경계에서 명시적으로 표현돼야 합니다.

## 한눈에 보는 구조

이 흐름에서 가장 중요한 단계는 자원을 먼저 읽고 그 자원 기준으로 권한을 판단하는 부분입니다. 사용자가 누구인지만 알아서는 충분하지 않습니다. 수정하려는 게시글, 다운로드하려는 파일, 조회하려는 주문처럼 실제 대상 자원을 기준으로 다시 결정해야 합니다.

## 핵심 용어

- **역할 기반 접근 제어(RBAC)**: 관리자, 편집자, 조회자처럼 역할을 기준으로 권한을 부여하는 방식입니다.
- **속성 기반 접근 제어(ABAC)**: 소유자, 부서, 시간대, 지역 같은 속성을 기준으로 권한을 판단하는 방식입니다.
- **IDOR**: ID 값을 바꿔 다른 사람 자원에 접근하는 직접 객체 참조 취약점입니다.
- **최소 권한(least privilege)**: 꼭 필요한 권한만 허용하고 나머지는 기본적으로 막는 원칙입니다.
- **정책(policy)**: 비즈니스 로직과 분리해 둔 권한 결정 규칙입니다.

## 바꾸기 전과 후

**바꾸기 전**: 라우트에서 `if user.role == 'admin'` 정도만 확인하고 실제 자원 소유권은 보지 않습니다. 목록 조회에서는 전체 데이터를 내려보낸 뒤 화면에서만 가립니다.

**바꾼 후**: 모든 자원 작업이 `can(user, action, resource)` 같은 명시적 정책 함수를 거칩니다. 목록 API도 동일한 기준으로 필터링하고, 정책이 없는 작업은 기본적으로 거부합니다.

## 실습: 안전한 인가 흐름을 만드는 5단계

### 1단계 — 자원에 소유자를 연결합니다

```python
class Post:
    def __init__(self, id, author_id, content):
        self.id, self.author_id, self.content = id, author_id, content
```

인가를 정확히 하려면 자원이 누구 것인지 코드와 데이터에 드러나 있어야 합니다. 게시글, 주문, 문서처럼 사용자 단위로 보호해야 하는 자원에는 소유자 정보가 빠지면 안 됩니다. 소유자 필드가 없으면 인가는 역할 이름 몇 개에만 기대게 됩니다.

### 2단계 — 정책 함수를 분리합니다

```python
def can_edit(user, post) -> bool:
    return user.id == post.author_id or user.role == "admin"
```

정책 함수는 인가 규칙을 한곳에 모아 줍니다. 라우트마다 조건문을 복사하는 대신 `can_edit`, `can_delete`, `can_view` 같은 함수로 분리하면 누락을 줄이고, 변경 이유도 추적하기 쉬워집니다.

### 3단계 — 자원 단위에서 다시 확인합니다

```python
def edit_post(user, post_id, new_text):
    post = posts.get(post_id)
    if not can_edit(user, post):
        raise PermissionError("forbidden")
    post.content = new_text
```

라우트에서 한 번 인증했다고 끝내지 말고, 실제 작업 직전에 자원을 읽은 뒤 다시 검사해야 합니다. 이 단계가 빠지면 URL 파라미터나 JSON payload의 ID만 바꿔도 남의 자원에 접근하는 IDOR가 쉽게 생깁니다.

### 4단계 — 목록 조회도 같은 기준으로 필터링합니다

```python
def my_posts(user):
    return [p for p in posts.all() if p.author_id == user.id]
```

상세 조회와 수정만 보호하고 목록 API를 그대로 열어 두면 정보 노출은 계속됩니다. 목록은 화면 렌더링 전에 이미 서버에서 권한 필터를 통과해야 합니다. 목록 필터를 빼먹는 팀이 생각보다 많습니다.

### 5단계 — 기본값을 거부로 둡니다

```python
def authorize(user, action, resource):
    handler = POLICIES.get(action)
    if not handler:
        raise PermissionError("no policy")  # 기본 거부
    if not handler(user, resource):
        raise PermissionError("forbidden")
```

정책이 없는 작업을 암묵적으로 허용하면 새 기능이 생길 때마다 구멍이 열립니다. 인가 시스템은 허용 규칙이 명시된 경우에만 열리고, 그렇지 않으면 닫혀 있어야 합니다. 기본 거부는 작은 번거로움이 아니라 구조적 안전장치입니다.

## 이 코드에서 먼저 볼 점

- 인가 정책이 한곳에 모이면 변경과 감사가 쉬워집니다.
- 기본값은 허용이 아니라 거부입니다.
- 라우트 수준 검사와 자원 수준 검사는 서로 대체 관계가 아니라 보완 관계입니다.
- 목록 API도 인가 대상이며, 별도 필터를 반드시 가져야 합니다.

## 실무에서 자주 헷갈리는 지점

1. **UI 숨김을 인가로 착각하는 경우**: 버튼을 감춰도 API는 여전히 호출할 수 있습니다.
2. **`?id=` 값을 믿고 소유권 검사를 생략하는 경우**: 가장 흔한 IDOR 패턴입니다.
3. **역할만 보고 자원 소유권을 무시하는 경우**: 편집자 권한이 곧 전체 데이터 열람 권한으로 번질 수 있습니다.
4. **정책을 라우트마다 흩어 두는 경우**: 한 군데 누락이 전체 취약점이 됩니다.
5. **목록 API를 필터 없이 반환하는 경우**: 상세 권한을 막아도 이미 데이터는 새고 있습니다.

## 실무에서는 이렇게 봅니다

규모가 작은 팀은 보통 `policies.py` 같은 모듈을 두고 라우트나 서비스 함수가 `authorize(user, action, resource)`만 부르게 만듭니다. 이 구조만으로도 중복이 크게 줄고, 권한 변경 리뷰가 쉬워집니다. 서비스가 커지면 Open Policy Agent나 Cedar 같은 외부 정책 엔진을 붙여 서비스 간 규칙을 통합하기도 합니다.

중요한 점은 정책을 비즈니스 로직에서 완전히 떼어 낸다는 뜻이 아니라, 결정 규칙을 재사용 가능한 형태로 분리한다는 점입니다. 자원 소유권, 조직 속성, 감사 로그는 결국 도메인 정보와 연결되기 때문에 정책 계층과 애플리케이션 계층이 명확히 협력해야 합니다.

## 선임 엔지니어는 이렇게 생각합니다

- 인가는 라우트가 아니라 자원 경계에서 판단합니다.
- 정책은 코드 조각이 아니라 관리 가능한 데이터처럼 다룹니다.
- 기본값은 언제나 거부입니다.
- 목록 API에도 같은 권한 필터를 적용합니다.
- 권한 변경과 거부 이벤트는 감사 로그에 남겨야 합니다.

## 체크리스트

- [ ] `can_*` 함수가 한 모듈에 모여 있습니다.
- [ ] 기본 거부 정책이 적용됩니다.
- [ ] 자원 단위 IDOR 방어가 있습니다.
- [ ] 목록 API가 권한 필터를 거칩니다.

## 연습 문제

1. RBAC와 ABAC를 함께 쓰는 예를 하나 설계해 보세요.
2. IDOR를 만드는 코드 한 줄과, 이를 고치는 코드 한 줄을 각각 적어 보세요.
3. 권한 변경 감사 로그 스키마를 설계해 보세요.

## 정리와 다음 글

인가는 로그인 여부를 확인하는 작업이 아니라, 요청마다 자원과 행위를 기준으로 권한을 다시 판단하는 절차입니다. 이 글에서는 정책 함수 분리, 자원 단위 검사, 목록 필터, 기본 거부 원칙이 왜 함께 가야 하는지 정리했습니다.

다음 글에서는 권한으로 보호한 자원 자체를 어떻게 안전하게 저장할지, 데이터 저장 관점의 보안을 다룹니다.

## 심화 실전 노트: IDOR 재현, 멀티테넌트 격리, OPA 정책

인가 취약점은 코드에서 눈에 잘 띄지 않습니다. 기능 테스트는 통과하면서도 다른 사용자의 자원에 접근 가능한 상태가 남아 있기 때문입니다. 여기서는 가장 흔한 인가 취약점인 IDOR를 재현하고, 멀티테넌트 격리와 정책 엔진 적용까지 다룹니다.

### IDOR(Insecure Direct Object Reference) 재현

IDOR는 URL이나 요청 본문의 ID를 바꾸기만 해도 다른 사용자의 자원에 접근할 수 있는 취약점입니다. OWASP Top 10 A01(Broken Access Control)의 가장 흔한 형태입니다.

```python
# 취약한 패턴 — ID만 받고 소유권 확인 없음
@app.get("/orders/{order_id}")
def get_order(order_id: int, user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404)
    return order  # 누구의 주문이든 반환


# 방어 패턴 — 소유권 조건을 쿼리에 포함
@app.get("/orders/{order_id}")
def get_order(order_id: int, user=Depends(get_current_user)):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id,  # 소유권 확인
    ).first()
    if not order:
        raise HTTPException(status_code=404)  # 존재 여부도 숨김
    return order
```

방어의 핵심은 쿼리 자체에 소유권 조건을 포함하는 것입니다. 조회 후 별도 if 문으로 확인하는 방식도 가능하지만, 쿼리에 넣으면 존재하지만 접근 불가능한 자원의 존재 여부조차 노출하지 않습니다.

### 수평 권한 상승과 수직 권한 상승

| 유형 | 설명 | 예시 |
| --- | --- | --- |
| 수평(Horizontal) | 같은 역할의 다른 사용자 자원 접근 | 내 주문이 아닌 주문 조회 |
| 수직(Vertical) | 더 높은 역할의 기능 접근 | 일반 사용자가 관리자 API 호출 |

```python
# 수직 권한 상승 방어 — 역할 기반 데코레이터
from functools import wraps

def require_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user=Depends(get_current_user), **kwargs):
            if user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="insufficient role")
            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator


@app.delete("/admin/users/{user_id}")
@require_role("admin", "superadmin")
def delete_user(user_id: int, user=Depends(get_current_user)):
    target = db.query(User).get(user_id)
    if not target:
        raise HTTPException(status_code=404)
    # 자기 자신 삭제 방지
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="cannot delete self")
    db.delete(target)
    db.commit()
    audit_log("user_deleted", actor=user.id, target=user_id)
```

### 멀티테넌트 격리

SaaS에서는 테넌트 간 데이터가 섞이면 단순 버그가 아니라 사업 위기입니다. 격리를 코드 수준에서 강제하는 패턴입니다.

```python
from contextvars import ContextVar
from sqlalchemy import event
from sqlalchemy.orm import Query

# 현재 요청의 테넌트 ID를 컨텍스트 변수로 관리
current_tenant: ContextVar[str] = ContextVar("current_tenant")


class TenantMixin:
    """모든 테넌트 소속 모델이 상속하는 믹스인"""
    tenant_id: str


# SQLAlchemy 이벤트로 쿼리에 자동 필터 적용
@event.listens_for(Query, "before_compile", retval=True)
def add_tenant_filter(query):
    """모든 SELECT 쿼리에 tenant_id 조건을 자동 추가"""
    try:
        tenant_id = current_tenant.get()
    except LookupError:
        raise RuntimeError("tenant context not set — query blocked")

    for column_desc in query.column_descriptions:
        entity = column_desc.get("entity")
        if entity and hasattr(entity, "tenant_id"):
            query = query.filter(entity.tenant_id == tenant_id)
    return query


# 미들웨어에서 테넌트 컨텍스트 설정
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    tenant_id = extract_tenant_from_request(request)
    token = current_tenant.set(tenant_id)
    try:
        response = await call_next(request)
    finally:
        current_tenant.reset(token)
    return response
```

이 패턴은 개발자가 WHERE 절을 빼먹어도 프레임워크 수준에서 테넌트 격리가 유지되게 합니다. 쿼리가 컴파일되기 전에 자동으로 필터가 붙으므로 실수에 의한 데이터 노출을 구조적으로 막습니다.

### Open Policy Agent(OPA)를 이용한 외부 정책

서비스가 커지면 정책을 코드에서 분리해 외부 엔진으로 관리하는 것이 유지보수에 유리합니다.

```rego
# policy.rego — OPA Rego 정책 예시
package myapp.authz

default allow := false

# 관리자는 모든 작업 허용
allow if {
    input.user.role == "admin"
}

# 소유자는 자기 자원에 대해 읽기/수정 허용
allow if {
    input.action in ["read", "update"]
    input.resource.owner_id == input.user.id
}

# 같은 팀 멤버는 읽기만 허용
allow if {
    input.action == "read"
    input.resource.team_id == input.user.team_id
}
```

```python
import httpx

OPA_URL = "http://localhost:8181/v1/data/myapp/authz/allow"


async def check_opa(user: dict, action: str, resource: dict) -> bool:
    """OPA에 인가 질의를 보냅니다."""
    payload = {
        "input": {
            "user": user,
            "action": action,
            "resource": resource,
        }
    }
    resp = await httpx.AsyncClient().post(OPA_URL, json=payload)
    result = resp.json()
    return result.get("result", False)


# 사용 예시
@app.put("/documents/{doc_id}")
async def update_document(doc_id: int, body: DocUpdate, user=Depends(get_current_user)):
    doc = db.query(Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404)

    allowed = await check_opa(
        user={"id": user.id, "role": user.role, "team_id": user.team_id},
        action="update",
        resource={"owner_id": doc.owner_id, "team_id": doc.team_id},
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="policy denied")

    doc.content = body.content
    db.commit()
```

OPA를 쓰면 정책 변경이 코드 배포 없이 가능하고, 동일한 정책을 여러 서비스에서 공유할 수 있습니다. 단, 네트워크 호출이 추가되므로 지연 시간과 장애 시 기본 동작(fail-closed)을 함께 설계해야 합니다.

### 권한 변경 감사

권한 거부 이벤트는 반드시 감사 로그에 남겨야 합니다. 공격 시도를 탐지하는 가장 직접적인 신호이기 때문입니다.

```python
def audit_authz_decision(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    decision: str,  # "allow" or "deny"
    reason: str = "",
):
    logger.info(
        "authz_decision",
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        decision=decision,
        reason=reason,
    )
```

경보 규칙 예시:
- 동일 사용자가 5분간 10회 이상 deny: 권한 상승 시도 의심
- 동일 자원에 서로 다른 5명이 deny: 민감 자원에 대한 탐색 의심

### 목록 API에서의 인가 필터링 패턴

단건 조회만 보호하고 목록 API를 열어 두면 정보 유출이 계속됩니다. 목록은 쿼리 시점에 권한 필터를 적용해야 합니다.

```python
from sqlalchemy import and_
from fastapi import Query as QueryParam


@app.get("/documents")
def list_documents(
    user=Depends(get_current_user),
    page: int = QueryParam(default=1, ge=1),
    size: int = QueryParam(default=20, ge=1, le=100),
):
    """사용자가 볼 수 있는 문서만 반환합니다."""
    base_query = db.query(Document)

    if user.role == "admin":
        # 관리자는 전체 조회 가능
        filtered = base_query
    else:
        # 일반 사용자: 본인 소유 + 팀 공유 문서만
        filtered = base_query.filter(
            or_(
                Document.owner_id == user.id,
                and_(
                    Document.team_id == user.team_id,
                    Document.visibility == "team",
                ),
            )
        )

    total = filtered.count()
    items = filtered.offset((page - 1) * size).limit(size).all()
    return {"total": total, "items": items}
```

이 패턴에서 중요한 점:
1. 페이지네이션 전에 필터를 적용합니다. 필터 없이 전체를 가져온 뒤 잘라내면 성능과 보안 모두 나빠집니다.
2. total count도 필터된 결과에서 계산합니다. 전체 문서 수를 노출하면 정보 유출입니다.
3. 역할에 따라 쿼리 조건이 달라지므로 정책과 쿼리가 일치해야 합니다.

### 시간 기반 권한과 임시 접근

일부 권한은 영구적이지 않고 시간 제한이 필요합니다. 예를 들어 외부 감사인에게 30일간만 조회 권한을 부여하거나, 온콜 엔지니어에게 교대 시간 동안만 관리자 권한을 주는 경우입니다.

```python
from datetime import datetime, timezone


class TemporaryGrant:
    def __init__(self, user_id: str, permission: str, expires_at: datetime, reason: str):
        self.user_id = user_id
        self.permission = permission
        self.expires_at = expires_at
        self.reason = reason


def check_temporary_grant(user_id: str, permission: str) -> bool:
    """임시 권한 부여를 확인합니다. 만료 시 자동 거부."""
    grant = db.query(TemporaryGrant).filter(
        TemporaryGrant.user_id == user_id,
        TemporaryGrant.permission == permission,
        TemporaryGrant.expires_at > datetime.now(timezone.utc),
    ).first()
    return grant is not None


def grant_temporary_access(
    admin_id: str,
    target_user_id: str,
    permission: str,
    duration_hours: int,
    reason: str,
) -> TemporaryGrant:
    """임시 권한을 부여하고 감사 로그를 남깁니다."""
    expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
    grant = TemporaryGrant(
        user_id=target_user_id,
        permission=permission,
        expires_at=expires_at,
        reason=reason,
    )
    db.add(grant)
    db.commit()

    audit_log(
        "temporary_grant_created",
        actor=admin_id,
        target=target_user_id,
        permission=permission,
        expires_at=expires_at.isoformat(),
        reason=reason,
    )
    return grant
```

시간 기반 권한의 핵심 규칙:
- 만료 시 자동으로 거부해야 합니다. 정리 배치가 실패해도 접근이 차단되어야 합니다.
- 부여한 사람, 이유, 만료 시각을 감사 로그에 남겨야 합니다.
- 최대 기간 상한을 설정해 무기한 임시 권한을 방지합니다.

### 인가 테스트 전략

인가 로직은 기능 테스트와 별도로 보안 테스트를 작성해야 합니다. "이 기능이 동작하는가"와 "다른 사용자 자원에 접근할 수 없는가"는 다른 질문입니다.

```python
import pytest


class TestOrderAuthorization:
    def test_owner_can_view_own_order(self, client, user_alice, order_of_alice):
        resp = client.get(
            f"/orders/{order_of_alice.id}",
            headers=auth_header(user_alice),
        )
        assert resp.status_code == 200

    def test_other_user_cannot_view_order(self, client, user_bob, order_of_alice):
        resp = client.get(
            f"/orders/{order_of_alice.id}",
            headers=auth_header(user_bob),
        )
        assert resp.status_code == 404  # 403이 아닌 404 — 존재 여부 숨김

    def test_admin_can_view_any_order(self, client, admin_user, order_of_alice):
        resp = client.get(
            f"/orders/{order_of_alice.id}",
            headers=auth_header(admin_user),
        )
        assert resp.status_code == 200

    def test_unauthenticated_cannot_view(self, client, order_of_alice):
        resp = client.get(f"/orders/{order_of_alice.id}")
        assert resp.status_code == 401

    def test_list_only_shows_own_orders(self, client, user_alice):
        resp = client.get("/orders", headers=auth_header(user_alice))
        assert resp.status_code == 200
        for order in resp.json()["items"]:
            assert order["user_id"] == user_alice.id
```

이 테스트 패턴에서 중요한 점:
- 각 역할(소유자, 비소유자, 관리자, 미인증)별로 테스트를 작성합니다.
- 403 대신 404를 반환하는 정책이라면 테스트도 그에 맞춰야 합니다.
- 목록 API가 다른 사용자의 데이터를 포함하지 않는지 확인합니다.

## 처음 질문으로 돌아가기

- **RBAC와 ABAC는 어떤 차이가 있을까요?**
  - RBAC는 역할(admin, editor, viewer)을 기준으로 권한을 부여하고, ABAC는 속성(소유자, 부서, 시간대, 지역)을 기준으로 판단합니다. OPA 정책 예시에서 보았듯이 실무에서는 역할 확인(RBAC)과 소유권·팀 속성 확인(ABAC)을 함께 쓰는 혼합 모델이 가장 흔합니다.
- **IDOR는 왜 흔하고도 위험한 인가 취약점일까요?**
  - IDOR 재현 코드에서 보았듯이 URL의 ID 하나만 바꾸면 다른 사용자의 자원에 접근할 수 있기 때문입니다. 기능 테스트는 통과하면서도 보안 테스트에서만 드러나며, 쿼리에 소유권 조건을 빠뜨리기만 해도 발생합니다.
- **인가 판단은 라우트 수준과 자원 수준에서 어떻게 나눠 봐야 할까요?**
  - 라우트 수준은 역할 기반으로 "이 API에 접근할 수 있는가"를 걸러 내고(수직 권한 상승 방어), 자원 수준은 "이 특정 데이터에 대해 이 작업을 할 수 있는가"를 확인합니다(수평 권한 상승 방어). 멀티테넌트 격리에서 보았듯이 두 수준이 독립적으로 작동해야 한 층이 뚫려도 다른 층이 막습니다.
<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): 입력값 검증](./02-input-validation.md)
- [Secure Coding 101 (3/10): 인증과 세션](./03-authentication-and-session.md)
- **인가와 권한 (현재 글)**
- 안전한 데이터 저장 (예정)
- Secret과 키 관리 (예정)
- SQL Injection과 ORM 안전 사용 (예정)
- XSS와 CSRF 방어 (예정)
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP Top 10 — Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [NIST RBAC](https://csrc.nist.gov/projects/role-based-access-control)
- [Open Policy Agent](https://www.openpolicyagent.org/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: Authorization, RBAC, ABAC, LeastPrivilege, SecureCoding
