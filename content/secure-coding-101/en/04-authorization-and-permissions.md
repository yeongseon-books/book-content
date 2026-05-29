---
series: secure-coding-101
episode: 4
title: "Secure Coding 101 (4/10): Authorization and Permissions"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Authorization
  - RBAC
  - ABAC
  - LeastPrivilege
  - SecureCoding
seo_description: RBAC, ABAC, IDOR defenses, least privilege, and a five-step playbook for safe authorization on every request.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (4/10): Authorization and Permissions

Logging in does not answer the question that matters most to a secure application: may this user touch this resource right now? Reading another person's order, editing a document, or downloading an internal report all need a separate decision. Broken access control keeps ranking near the top of real-world incident lists because teams often stop at authentication and never finish the authorization model behind it.

This is the 4th post in the Secure Coding 101 series.

In this chapter, we will treat authorization as a server-side decision over actor, action, and resource, not as a UI rule or a handful of role names. That framing makes RBAC, ABAC, IDOR defense, list filtering, and default-deny behavior fit together cleanly.

> Authorization is not a visibility rule. It is a repeated server-side decision over who wants to do what to which resource.


![secure coding 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/04/04-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Authorization and Permissions?
- Which signal should the example or diagram make visible for Authorization and Permissions?
- What failure should be prevented first when Authorization and Permissions reaches a real system?

## Questions This Chapter Answers

- The difference between *RBAC* and *ABAC*
- What *IDOR* is and how to defend
- *Least privilege* in real code
- A five-step authorization flow
- Five common mistakes

## Why It Matters

OWASP Top 10 is often led by *Broken Access Control*. Hiding a button in the UI is *not a defense*. Every decision must happen *on the server*.

> *Authorize at the *resource* level, not just the *route*.*

## Key Terms

- **RBAC**: *role-based* (admin, editor, viewer).
- **ABAC**: *attribute-based* (owner, department, time).
- **IDOR**: changing the *id* to access someone else's resource.
- **Least privilege**: *deny by default*, allow only what is needed.
- **Policy**: decision rules kept *separate from business code*.

## Before/After

**Before**: A route checks `if user.role == 'admin'` and forgets to verify *ownership*.

**After**: Every resource call goes through `can(user, action, resource)` *explicitly*.

## Hands-on: Authorization in Five Steps

### Step 1 — Attach an *owner* to the resource

```python
class Post:
    def __init__(self, id, author_id, content):
        self.id, self.author_id, self.content = id, author_id, content
```

### Step 2 — Write a policy function

```python
def can_edit(user, post) -> bool:
    return user.id == post.author_id or user.role == "admin"
```

### Step 3 — Check at the resource level

```python
def edit_post(user, post_id, new_text):
    post = posts.get(post_id)
    if not can_edit(user, post):
        raise PermissionError("forbidden")
    post.content = new_text
```

### Step 4 — Filter list queries too

```python
def my_posts(user):
    return [p for p in posts.all() if p.author_id == user.id]
```

### Step 5 — Default deny

```python
def authorize(user, action, resource):
    handler = POLICIES.get(action)
    if not handler:
        raise PermissionError("no policy")  # default deny
    if not handler(user, resource):
        raise PermissionError("forbidden")
```

## What to Notice in This Code

- Policies live in *one place*.
- The *default* is *deny*.
- Resource-level checks *complement* route-level ones.

## Five Common Mistakes

1. **Replacing authorization with *UI hiding*.** The API is still callable.
2. **Trusting `?id=` and skipping the *ownership check*.** The classic *IDOR*.
3. **Checking *role only* and ignoring *resource ownership*.** Editors see everything.
4. **Spreading policies across *every route*.** Miss one place and *all are at risk*.
5. **Returning lists *without filtering*.** The page leaks them anyway.

## How This Shows Up in Production

Most teams keep a *policy module* (`policies.py`) and the route just calls `authorize(user, action, resource)`. Larger orgs adopt *OPA* or *Cedar* for cross-service policy.

## How a Senior Engineer Thinks

- *Authorize at the *resource* boundary.*
- *Treat policies as *data*.*
- *The default is *deny*.*
- *List APIs need *permission filters* too.*
- *Permission changes go to the *audit log*.*

## Checklist

- [ ] `can_*` functions live in *one module*.
- [ ] *Default deny* is enforced.
- [ ] *IDOR* defenses exist at the resource level.
- [ ] *List APIs* have *permission filters*.

## Practice Problems

1. Give one example of using *RBAC* and *ABAC* together.
2. Show one line that creates an *IDOR* and one line that fixes it.
3. Design the schema for a *permission-change audit log*.

## Wrap-up and Next Steps

Once authorization is *explicit*, incidents stay *short*. Next we make the *resource itself safe* — *safe data storage*.

## Answering the Opening Questions

- **What distinguishes RBAC from ABAC?**
  - RBAC grants permissions based on roles (admin, editor, viewer), while ABAC decides based on attributes (owner, department, time zone, region). As the OPA policy example showed, in practice the most common model is a hybrid combining role checks (RBAC) with ownership and team-attribute checks (ABAC).
- **Why is IDOR a common yet dangerous authorization vulnerability?**
  - As the IDOR reproduction code showed, changing just one ID in the URL accesses another user's resource. It passes functional testing while surfacing only in security testing, and occurs simply by omitting an ownership condition from the query.
- **How should authorization decisions be split between route level and resource level?**
  - Route level filters "can this role access this API" (vertical privilege escalation defense), while resource level verifies "can this user perform this action on this specific data" (horizontal privilege escalation defense). As multi-tenant isolation showed, both levels must operate independently so that if one layer is breached, the other still blocks.

## Deep Dive: IDOR Reproduction, Multi-Tenant Isolation, OPA Policy

Authorization vulnerabilities hide in plain sight. Functional tests pass while other users' resources remain accessible. This section reproduces the most common authorization flaw — IDOR — then covers multi-tenant isolation and external policy engines.

### IDOR (Insecure Direct Object Reference) Reproduction

IDOR lets an attacker access another user's resource simply by changing an ID in the URL or request body. It is the most common manifestation of OWASP Top 10 A01 (Broken Access Control).

```python
# Vulnerable — accepts ID without ownership check
@app.get("/orders/{order_id}")
def get_order(order_id: int, user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404)
    return order  # returns anyone's order

# Defended — ownership condition in the query itself
@app.get("/orders/{order_id}")
def get_order(order_id: int, user=Depends(get_current_user)):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id,  # ownership check
    ).first()
    if not order:
        raise HTTPException(status_code=404)  # hides existence too
    return order
```

The key defense is embedding the ownership condition directly in the query. A separate `if` after fetching also works, but putting it in the query avoids leaking whether a resource exists at all.

### Horizontal vs. Vertical Privilege Escalation

| Type | Description | Example |
| --- | --- | --- |
| Horizontal | Accessing another user's resource at the same role | Viewing someone else's order |
| Vertical | Accessing a higher role's functionality | Regular user calling admin API |

```python
# Vertical escalation defense — role-based decorator
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
    # Prevent self-deletion
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="cannot delete self")
    db.delete(target)
    db.commit()
    audit_log("user_deleted", actor=user.id, target=user_id)
```

### Multi-Tenant Isolation

In SaaS, cross-tenant data leakage is not just a bug — it is a business crisis. This pattern enforces isolation at the framework level.

```python
from contextvars import ContextVar
from sqlalchemy import event
from sqlalchemy.orm import Query

# Manage current tenant via context variable
current_tenant: ContextVar[str] = ContextVar("current_tenant")

class TenantMixin:
    """Mixin inherited by all tenant-scoped models."""
    tenant_id: str

# Auto-filter every SELECT query by tenant_id
@event.listens_for(Query, "before_compile", retval=True)
def add_tenant_filter(query):
    """Inject tenant_id condition before query compiles."""
    try:
        tenant_id = current_tenant.get()
    except LookupError:
        raise RuntimeError("tenant context not set — query blocked")

    for column_desc in query.column_descriptions:
        entity = column_desc.get("entity")
        if entity and hasattr(entity, "tenant_id"):
            query = query.filter(entity.tenant_id == tenant_id)
    return query

# Middleware sets tenant context per request
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

This pattern ensures isolation even when a developer forgets a WHERE clause. Because the filter is injected before query compilation, structural omission cannot leak data across tenants.

### Open Policy Agent (OPA) for External Policy

As services grow, extracting policy into an external engine simplifies cross-service rule sharing.

```rego
# policy.rego — OPA Rego policy example
package myapp.authz

default allow := false

# Admins can do everything
allow if {
    input.user.role == "admin"
}

# Owners can read/update their own resources
allow if {
    input.action in ["read", "update"]
    input.resource.owner_id == input.user.id
}

# Team members can read
allow if {
    input.action == "read"
    input.resource.team_id == input.user.team_id
}
```

```python
import httpx

OPA_URL = "http://localhost:8181/v1/data/myapp/authz/allow"

async def check_opa(user: dict, action: str, resource: dict) -> bool:
    """Query OPA for an authorization decision."""
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

# Usage
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

OPA enables policy changes without code deployments and lets multiple services share the same rules. However, the added network hop means you must design for latency and define a fail-closed default when OPA is unreachable.

### Authorization Change Audit

Denied authorization events must be logged — they are the most direct signal of attack attempts.

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

Alert rule examples:
- Same user gets 10+ denials in 5 minutes → suspect privilege escalation attempt
- 5+ different users denied on the same resource → suspect sensitive-resource probing

### List API Authorization Filtering

Protecting detail endpoints while leaving list APIs open still leaks data. Lists must apply permission filters at query time.

```python
from sqlalchemy import and_
from fastapi import Query as QueryParam

@app.get("/documents")
def list_documents(
    user=Depends(get_current_user),
    page: int = QueryParam(default=1, ge=1),
    size: int = QueryParam(default=20, ge=1, le=100),
):
    """Return only documents the user is authorized to see."""
    base_query = db.query(Document)

    if user.role == "admin":
        filtered = base_query
    else:
        # Regular users: own documents + team-shared
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

Key points:
1. Apply filters before pagination. Fetching everything then trimming hurts both performance and security.
2. Compute `total` from the filtered result. Exposing the total document count is information leakage.
3. Role-based query conditions must stay aligned with the authorization policy.

### Time-Based Permissions and Temporary Access

Some permissions are not permanent. External auditors may need 30-day read access; on-call engineers may need admin rights only during their shift.

```python
from datetime import datetime, timezone

class TemporaryGrant:
    def __init__(self, user_id: str, permission: str, expires_at: datetime, reason: str):
        self.user_id = user_id
        self.permission = permission
        self.expires_at = expires_at
        self.reason = reason

def check_temporary_grant(user_id: str, permission: str) -> bool:
    """Check if a temporary grant is active. Auto-deny on expiration."""
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
    """Grant time-limited access with audit trail."""
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

Core rules for time-based permissions:
- Auto-deny on expiration. Even if cleanup batches fail, access must be blocked.
- Log who granted, the reason, and the expiration time.
- Set a maximum duration cap to prevent indefinite "temporary" grants.

### Authorization Testing Strategy

Authorization logic requires security tests separate from functional tests. "Does this feature work?" and "Can another user access this resource?" are different questions.

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
        assert resp.status_code == 404  # 404 not 403 — hide existence

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

Key points for this test pattern:
- Write tests for each role (owner, non-owner, admin, unauthenticated).
- If the policy returns 404 instead of 403, the test must match.
- Verify that list APIs do not include other users' data.

<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- [Secure Coding 101 (3/10): Authentication and Session](./03-authentication-and-session.md)
- **Authorization and Permissions (current)**
- Safe Data Storage (upcoming)
- Secret and Key Management (upcoming)
- SQL Injection and Safe ORM Usage (upcoming)
- XSS and CSRF Defense (upcoming)
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP Top 10 — Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [NIST RBAC](https://csrc.nist.gov/projects/role-based-access-control)
- [Open Policy Agent](https://www.openpolicyagent.org/)
- [NIST SP 800-162 — Guide to Attribute Based Access Control](https://csrc.nist.gov/pubs/sp/800/162/upd2/final)

Tags: Authorization, RBAC, ABAC, LeastPrivilege, SecureCoding
