---
series: information-security-101
episode: 2
title: "바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 정보보안
  - 인증
  - 인가
  - JWT
  - AI보안
language: ko
---

# 바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가

이 글은 **바이브코딩을 위한 정보 보안 기초** 시리즈의 2편입니다. AI가 만들어주는 코드에는 보안 취약점이 숨어 있을 수 있습니다. 이번에는 AI가 가장 자주 틀리는 영역인 인증과 인가를 다룹니다.

---

AI에게 "로그인 기능을 만들어줘"라고 하면 JWT 토큰을 발급하고 비밀번호를 해시해서 저장하는 코드가 나옵니다. 그럴싸합니다. 그런데 토큰 만료 시간을 24시간으로 설정하거나, 비밀번호를 MD5로 해시하거나, 권한 검사를 클라이언트에서만 하는 코드가 섞여 나오기도 합니다. AI는 작동하는 코드와 안전한 코드를 구분하지 않습니다.

> "인증은 '당신이 누구인지' 확인하는 것이고, 인가는 '당신이 무엇을 해도 되는지' 판단하는 것입니다. AI가 두 개념을 섞어서 구현했다면, 로그인은 되는데 권한은 뚫려 있는 코드가 됩니다."

## 이 글에서 다룰 질문들

- 인증과 인가는 정확히 어떻게 다를까요?
- AI가 생성한 비밀번호 저장 코드, 어디가 문제일까요?
- JWT 수명을 길게 잡으면 무슨 일이 생길까요?
- RBAC 없이 권한을 관리하면 어떤 위험이 있을까요?
- MFA를 추가하면 실제로 얼마나 안전해질까요?

---

## 바이브코딩 관점: AI가 인증 코드에서 자주 놓치는 것

AI는 인증 기능을 빠르게 만들어줍니다. 하지만 AI가 생성한 코드에는 일관적으로 놓치는 패턴이 있습니다.

### Before: AI가 생성한 전형적인 인증 코드

```python
# AI 생성 코드 — 작동하지만 취약한 패턴
import hashlib
import jwt

SECRET = "mysecret"  # 하드코딩된 비밀키

def login(username, password):
    # 문제 1: MD5는 비밀번호 해시로 부적합
    pw_hash = hashlib.md5(password.encode()).hexdigest()
    user = db.find(username, pw_hash)
    if user:
        # 문제 2: 토큰 수명 24시간 — 탈취되면 하루 동안 유효
        token = jwt.encode({"user_id": user.id, "exp": time() + 86400}, SECRET)
        return token
    return None

def get_admin_data(token):
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    # 문제 3: 권한 검사 없음 — 모든 로그인 사용자가 관리자 데이터 접근 가능
    return db.get_admin_data()
```

### After: 보안 개념을 알고 수정한 코드

```python
import bcrypt
import jwt
import os

SECRET = os.environ["JWT_SECRET"]  # 환경 변수에서 로드

def login(username, password):
    user = db.find_by_username(username)
    if not user:
        return None  # 사용자 없음과 비밀번호 틀림을 같은 오류로 처리
    # 기밀성: bcrypt — 의도적으로 느려서 크래킹 비용이 높음
    if bcrypt.checkpw(password.encode(), user.password_hash):
        # 무결성: 짧은 수명 + 역할 클레임 포함
        token = jwt.encode(
            {"user_id": user.id, "role": user.role, "exp": time() + 900},
            SECRET
        )
        return token
    return None

def get_admin_data(token):
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    # 인가: 서버에서 역할 확인
    if payload.get("role") != "admin":
        raise PermissionError("관리자 권한 필요")
    return db.get_admin_data()
```

---

## 인증 방식 비교: AI가 주로 생성하는 패턴과 실제 권장 방식

| 항목 | AI 생성 패턴 | 권장 방식 | 이유 |
| --- | --- | --- | --- |
| 비밀번호 해시 | MD5, SHA-256 | bcrypt, argon2 | 느린 해시 — GPU 크래킹 방어 |
| 토큰 수명 | 24시간 ~ 영구 | 15분 (액세스), 7일 (리프레시) | 탈취 시 피해 범위 축소 |
| 비밀키 위치 | 코드에 하드코딩 | 환경 변수 또는 비밀 관리 서비스 | 코드 노출 시 키 유출 방지 |
| 권한 검사 | 클라이언트 또는 없음 | 서버에서 매 요청마다 | 클라이언트는 조작 가능 |

**바이브코딩 관점에서:** AI가 생성한 인증 코드를 받으면 위 네 항목을 먼저 확인하세요. 네 개 중 하나라도 잘못되어 있으면 전체 인증 체계가 취약해집니다.

---

## JWT vs 세션: 언제 무엇을 써야 할까요?

AI는 보통 둘 중 하나를 아무 이유 없이 선택합니다. 차이를 알고 요청해야 합니다.

| 비교 항목 | 세션 기반 | JWT 기반 |
| --- | --- | --- |
| 강제 로그아웃 | 서버에서 즉시 가능 | 토큰 만료 전까지 어렵다 |
| 서버 부하 | 세션 저장소 필요 | 무상태(stateless) 처리 가능 |
| 마이크로서비스 | 세션 공유 설정 복잡 | 서비스 간 전달 편리 |
| 보안 사고 시 | 즉시 모든 세션 무효화 | 키 교체 또는 토큰 만료 대기 |

```python
# 세션: 서버가 상태를 들고 있음 → 즉시 로그아웃 가능
# 바이브코딩 팁: 보안 사고 대응이 중요하다면 세션이 더 안전

# JWT: 토큰이 스스로 증거 → 분산 시스템에 편리
# 바이브코딩 팁: JWT 쓸 때는 수명을 짧게(15분) 설정
```

---

## RBAC로 권한 설계하기

AI가 만든 코드에는 역할 기반 권한 관리(RBAC)가 빠져 있는 경우가 많습니다.

```python
# AI가 자주 생성하는 패턴 — 권한 구분 없음
@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    if not current_user.is_authenticated:  # 로그인만 확인
        return 401
    db.delete(user_id)  # 모든 로그인 사용자가 삭제 가능 — 위험!

# RBAC 적용 — 역할에 따라 허용/거부
ROLE_PERMISSIONS = {
    "admin": {"read", "write", "delete"},
    "editor": {"read", "write"},
    "viewer": {"read"},
}

def check_permission(user_role, action):
    return action in ROLE_PERMISSIONS.get(user_role, set())

@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    if not check_permission(current_user.role, "delete"):
        return 403  # Forbidden
    db.delete(user_id)
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| MD5/SHA로 비밀번호 해시 | GPU로 초당 수십억 번 시도 가능 | bcrypt 또는 argon2 사용 |
| JWT 수명을 길게 설정 | 탈취 후 대응 수단이 없어진다 | 15분 액세스 + 회전 리프레시 토큰 |
| 클라이언트에서만 권한 검사 | 브라우저 DevTools로 우회 가능 | 서버에서 매 요청마다 확인 |
| 비밀키를 코드에 하드코딩 | 코드가 공개되면 모든 토큰 위조 가능 | 환경 변수 또는 시크릿 매니저 사용 |

---

## AI 팁: 인증 코드를 AI에게 검토받는 법

1. **해시 함수 물어보기**: "이 코드에서 비밀번호 해시 함수가 적절한가요?"
2. **토큰 수명 확인**: "JWT 만료 시간이 너무 길지 않나요? 권장 시간은?"
3. **권한 검사 위치 확인**: "권한 검사가 서버에서 이루어지고 있나요?"
4. **하드코딩 탐지**: "비밀 정보가 코드에 직접 들어가 있는 부분이 있나요?"

---

## 실전 체크리스트

- [ ] 비밀번호 해시에 bcrypt 또는 argon2를 사용하고 있다
- [ ] JWT 액세스 토큰 수명이 15분 이내로 설정되어 있다
- [ ] 비밀키가 환경 변수나 시크릿 매니저에 저장되어 있다
- [ ] 권한 검사가 서버 코드에 있다 (클라이언트에만 있지 않다)
- [ ] 역할 기반 권한 모델(RBAC)이 정의되어 있다
- [ ] 로그인 실패 횟수 제한이 구현되어 있다

---

## 처음 질문으로 돌아가기

- **인증과 인가는 정확히 어떻게 다를까요?**
  인증은 "당신이 누구인지"를 확인하는 과정이고, 인가는 "그 신원이 특정 작업을 해도 되는지"를 판단하는 과정입니다. AI가 두 개념을 하나로 처리하면 로그인은 작동하지만 권한 통제가 없는 코드가 만들어집니다.

- **JWT 수명을 길게 잡으면 무슨 일이 생길까요?**
  토큰이 탈취되었을 때 만료 전까지 공격자가 계속 사용할 수 있습니다. 15분 액세스 토큰 + 회전형 리프레시 토큰 조합이 피해 범위를 줄이는 현실적인 방법입니다.

- **RBAC 없이 권한을 관리하면 어떤 위험이 있을까요?**
  모든 로그인 사용자가 같은 권한을 가지게 됩니다. 일반 사용자가 관리자 기능에 접근하거나, 한 계정이 탈취되면 전체 시스템이 노출되는 상황이 됩니다.

---

## 정리

AI가 생성한 인증 코드에서 가장 자주 발견되는 문제는 약한 비밀번호 해시, 긴 JWT 수명, 클라이언트에서만 이루어지는 권한 검사입니다. 네 가지 체크포인트(해시 함수, 토큰 수명, 비밀키 위치, 권한 검사 위치)를 습관적으로 확인하면 AI 생성 코드의 인증 보안을 크게 높일 수 있습니다. 다음 글에서는 암호화와 해시를 바이브코딩 관점에서 다룹니다.

---

## 참고 자료

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [NIST SP 800-63B Digital Identity](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [JWT 보안 모범 사례](https://datatracker.ietf.org/doc/html/rfc8725)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- **바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가 (현재 글)**
- 바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시
- 바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서
- 바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초
- 바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS
- 바이브코딩을 위한 정보 보안 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 정보 보안 기초 (8/10): 권한 최소화
- 바이브코딩을 위한 정보 보안 기초 (9/10): 로그와 감사
- 바이브코딩을 위한 정보 보안 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, 정보보안, 인증, 인가, JWT, AI보안
