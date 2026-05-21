---
series: backend-development-101
episode: 6
title: "Backend Development 101 (6/10): 인증과 권한"
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
  - Auth
  - Security
  - JWT
  - Python
seo_description: 인증(AuthN)과 권한(AuthZ)의 차이를 이해하고 bcrypt와 JWT를 사용하여 안전한 백엔드 보안 시스템을 구축하는 기본기를 익힙니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (6/10): 인증과 권한

이 글은 Backend Development 101 시리즈의 6번째 글입니다.

로그인 기능은 단순해 보이지만, 서버는 매 요청마다 두 가지를 동시에 판단합니다. 지금 요청을 보낸 주체가 누구인지 확인해야 하고, 확인된 주체가 이 행동을 할 수 있는지도 검증해야 합니다. 인증과 권한을 한 덩어리로 다루면 코드가 빠르게 무너집니다. 반대로 경계를 분리하면 실패 원인을 분명히 설명할 수 있고, 운영 중 사고가 났을 때 대응 속도가 달라집니다.

![Backend Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/06/06-01-concept-at-a-glance.ko.png)
*Backend Development 101 6장 흐름 개요*

## 먼저 던지는 질문

- authentication과 authorization은 무엇이 다를까요?
- 비밀번호 저장에서 최소한으로 지켜야 할 안전 기준은 무엇일까요?
- session과 JWT는 각각 언제 더 자연스러울까요?

## 인증과 권한을 분리해서 모델링해야 하는 이유

보안 사고 보고서를 읽어 보면, 치명적인 문제 상당수가 대단한 암호학 실패가 아니라 경계 혼동에서 시작됩니다. 예를 들어 인증은 통과했는데 권한 검사를 잊은 엔드포인트가 열려 있었거나, 토큰 검증은 했는데 만료 검증이 빠졌거나, 로그인 보호는 했는데 브루트포스 제한이 없는 경우입니다.

> 멘탈 모델: 인증은 "신원 확인 경계", 권한은 "행동 허용 경계"입니다. 두 경계가 코드에서 분리되어 있지 않으면 보안 사고는 기능 버그 형태로 숨어 들어옵니다.

백엔드 팀이 가져가야 할 최소한의 모델은 단순합니다.

| 구분 | 질문 | 실패 시 응답 | 주 책임 컴포넌트 |
| --- | --- | --- | --- |
| Authentication (AuthN) | "당신은 누구입니까?" | `401 Unauthorized` | 로그인, 토큰 검증, 세션 확인 |
| Authorization (AuthZ) | "그 행동을 할 수 있습니까?" | `403 Forbidden` | 역할/권한 매핑, 정책 엔진, 리소스 소유권 검사 |

핵심은 두 줄입니다. AuthN이 실패하면 사용자 식별 자체가 안 된 상태이고, AuthZ가 실패하면 식별은 되었지만 행동이 거부된 상태입니다. 이 차이를 API 설계와 로그에 명확히 반영해야 클라이언트, 운영자, 보안 담당자가 같은 사건을 같은 용어로 이해할 수 있습니다.

## 비밀번호 저장: 해시 알고리즘 선택이 보안 수준을 결정합니다

비밀번호 저장은 "암호화하면 된다"가 아닙니다. 서버는 원문 복호화가 필요하지 않으므로, 되돌릴 수 없는 해시를 저장해야 합니다. 여기서도 일반 해시와 비밀번호 전용 해시를 구분해야 합니다.

### 왜 MD5/SHA-256이 비밀번호 저장에 부적합한가

MD5, SHA-1, SHA-256은 설계 목표가 다릅니다. 파일 무결성, 체크섬, 메시지 다이제스트 같은 용도로는 유용하지만, 비밀번호 저장에는 너무 빠릅니다. 공격자가 GPU로 초당 수십억 번 해시를 시도할 수 있다는 뜻입니다. 해시가 빠를수록 대입 공격 비용은 내려갑니다.

비밀번호 저장에는 공격자 비용을 의도적으로 높이는 KDF(Key Derivation Function)가 필요합니다.

- `bcrypt`: 계산 비용(cost factor)을 조절할 수 있어 운영 환경에 맞춘 튜닝이 쉽습니다.
- `argon2id`: 메모리 비용까지 강제해 병렬 하드웨어 공격 저항성이 높습니다.
- `scrypt`: 메모리 하드한 특성이 있어 여전히 유효한 선택지입니다.

### bcrypt/argon2에서 실제로 튜닝해야 하는 값

해시 알고리즘 이름만 맞추면 끝나지 않습니다. 파라미터가 보안 수준을 결정합니다.

| 항목 | bcrypt | argon2id |
| --- | --- | --- |
| 주요 파라미터 | cost(rounds) | memory/time/parallelism |
| 운영 목표 | 로그인 지연 허용 범위 내 최대 cost | 메모리 압박을 감당하는 선에서 최대 강도 |
| 실무 기준 | 단일 검증이 대략 100~300ms | 단일 검증이 대략 100~300ms |

이 지연은 느린 것이 아니라 의도된 방어막입니다. 로그인 엔드포인트는 초저지연 API가 아니라 계정 보호 경계입니다. 비용이 너무 낮으면 공격자가 유리해지고, 너무 높으면 정상 사용자도 장애를 겪습니다. 인스턴스 스펙이 바뀌면 다시 측정하는 습관이 필요합니다.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    # 비밀번호는 항상 해시 후 저장합니다.
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 문자열 비교가 아니라 해시 검증 함수를 사용합니다.
    return pwd_context.verify(plain_password, hashed_password)
```

해시 문자열에 알고리즘/파라미터 메타데이터가 포함되므로, 이후 cost 상향이나 argon2 전환 시 점진 마이그레이션이 가능합니다. 로그인 성공 시 재해시(rehash) 정책을 넣으면 무중단 강화가 가능합니다.

## JWT를 토큰 문자열이 아니라 프로토콜 구성요소로 보기

JWT는 단순 문자열이 아니라 세 부분의 합입니다.

`header.payload.signature`

- `header`: 알고리즘(`alg`), 타입(`typ`) 같은 메타데이터
- `payload`: `sub`, `exp`, `iat`, `iss`, `aud` 등 클레임
- `signature`: 서버 비밀키(또는 비대칭 키)로 계산된 서명

JWT 검증은 "DB 조회 없이 신뢰한다"가 아니라 "서명과 클레임을 검증한다"입니다. 즉 stateless는 검증 상태가 서버 메모리에 없다는 의미이지, 무검증을 뜻하지 않습니다.

### 필수 검증 항목

| 항목 | 이유 |
| --- | --- |
| 서명 알고리즘 고정(`alg` allowlist) | `alg:none` 혼동 공격 차단 |
| `exp` 검증 | 만료 토큰 차단 |
| `iss`/`aud` 검증 | 다른 시스템 토큰 오용 차단 |
| `nbf`/`iat` 처리 | 시계 오차 및 재생성 타이밍 제어 |

```python
from datetime import UTC, datetime, timedelta
import jwt

SECRET_KEY = "replace-with-env-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def create_access_token(subject: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iss": "backend-development-101",
        "aud": "backend-api",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    # 허용 알고리즘을 명시하고 issuer/audience를 강제합니다.
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer="backend-development-101",
        audience="backend-api",
    )
```

### 액세스 토큰 만료와 리프레시 토큰 회전

실무에서는 액세스 토큰을 짧게, 리프레시 토큰을 길게 둡니다. 그리고 리프레시 토큰은 매 재발급마다 회전(rotation)해야 합니다.

1. 클라이언트가 리프레시 토큰으로 재발급 요청
2. 서버가 기존 리프레시 토큰의 `jti`를 검증
3. 새 액세스 토큰 + 새 리프레시 토큰 발급
4. 기존 `jti`를 폐기 목록으로 이동

여기서 재사용(reuse) 탐지가 중요합니다. 이미 폐기된 리프레시 토큰이 다시 들어오면 탈취 신호로 봐야 합니다. 해당 사용자 세션 전체 강제 로그아웃, 비밀번호 재설정 유도, 보안 알림 발송까지 자동화하는 것이 운영적으로 안전합니다.

## 세션 기반 vs 토큰 기반: 무엇이 더 안전한가가 아니라 어떤 위험을 관리할 것인가

"세션이 더 안전하다", "JWT가 확장성이 좋다" 같은 문장은 반쯤만 맞습니다. 설계는 위협 모델과 운영 제약을 같이 봐야 합니다.

| 관점 | Session-based | Token-based (JWT) |
| --- | --- | --- |
| 상태 저장 | 서버/Redis에 세션 저장 | 서버는 보통 상태 비저장 |
| 스케일링 | 세션 저장소 일관성 필요 | 검증 키 공유로 수평 확장 용이 |
| 강제 로그아웃/폐기 | 서버에서 세션 삭제로 즉시 반영 | 블랙리스트/짧은 만료/회전 전략 필요 |
| XSS 리스크 | 쿠키 탈취 방어 필요 | 저장 위치(localStorage 등)에 따라 확대 |
| CSRF 리스크 | 쿠키 인증 시 방어 토큰 필요 | Authorization 헤더 중심이면 상대적으로 낮음 |
| 모바일/다중 클라이언트 | 구현 가능하나 상태 공유 설계 필요 | API 게이트웨이 구조에 자연스러움 |

결론은 이분법이 아닙니다.

- 전통적 웹앱 + 브라우저 중심이면 `httpOnly + secure + sameSite` 쿠키 세션이 단순하고 강력합니다.
- 다중 서비스 API + 모바일/SPA 조합이면 짧은 JWT + 회전형 리프레시 전략이 운영적으로 유리합니다.
- 어떤 방식을 선택해도 로그인 시도 제한, 감사 로그, 비정상 행위 탐지는 별도로 필요합니다.

## OAuth2는 직접 발명보다 검증된 공급자 활용이 기본값입니다

OAuth2를 "소셜 로그인"으로만 좁게 이해하면 설계 판단이 틀어집니다. OAuth2는 위임(Delegation) 프로토콜입니다. 주체는 세 가지로 봅니다.

- Resource Owner: 사용자
- Client: 여러분 애플리케이션(웹, 모바일, 서버)
- Authorization Server: 인증/인가를 담당하는 서버

### 언제 직접 구현하고, 언제 공급자를 쓰는가

- 사내 표준 IdP(Entra ID, Okta, Keycloak)가 있으면 공급자 연동이 기본 선택입니다.
- 멀티테넌트 SaaS, SSO, MFA, 조건부 접근이 필요하면 자체 구현보다 공급자 연동이 비용과 위험 모두 낮습니다.
- 정말 작은 내부 도구에서 단순 계정만 필요하면 자체 인증도 가능하지만, 확장 시 OAuth2/OIDC 이전 비용을 미리 계산해야 합니다.

직접 구현이 나쁜 것이 아니라, 보안 프로토콜 구현은 유지보수 부담이 매우 큽니다. 키 회전, 토큰 무효화, 디바이스 플로우, 동의 화면, 감사 추적까지 포함하면 인증은 기능이 아니라 플랫폼이 됩니다.

### OAuth2 기본 흐름을 운영 언어로 이해하기

Authorization Code + PKCE 기준으로 보면 요청 경로는 다음과 같습니다.

1. 사용자가 Client에서 로그인 시작
2. Client가 Authorization Server로 리다이렉트
3. 사용자가 인증 후 인가 코드 수신
4. Client가 코드 + PKCE verifier로 토큰 교환
5. Access Token으로 Resource Server(API) 호출

중요한 포인트는 비밀번호가 Client 앱을 통과하지 않는다는 점입니다. OAuth2/OIDC를 쓰는 순간 애플리케이션은 계정 저장소를 직접 다루는 부담을 줄이고, 인증 강도(MFA, 위험 기반 정책)를 IdP 역량에 위임할 수 있습니다. 그래서 조직 규모가 커질수록 인증 자체보다 "권한 모델 설계"에 더 집중할 수 있습니다.

## 로그인 보호선: 레이트리밋과 계정 보호 정책

많은 팀이 토큰 설계는 꼼꼼하게 하면서 로그인 엔드포인트 보호를 늦게 붙입니다. 하지만 실제 침입 시도는 로그인에서 시작합니다. 다음 세 층을 함께 써야 방어가 실용적입니다.

- 계정 기준 제한: 동일 계정 연속 실패 횟수 제한
- 네트워크 기준 제한: 동일 IP 또는 CIDR 대역 요청 폭주 제한
- 장치/행동 기준 제한: 비정상 User-Agent, 지리 급변, 봇 패턴 탐지

여기에 지연(backoff)과 잠금(lockout)을 섞어야 합니다. 다만 무조건 잠그면 계정 잠금 DoS에 취약해질 수 있으므로, 위험 점수 기반 단계적 제어가 현실적입니다.

| 이벤트 | 권장 대응 | 운영 주의점 |
| --- | --- | --- |
| 짧은 시간 내 로그인 실패 급증 | CAPTCHA 또는 추가 인증 단계 적용 | 정상 사용자 마찰 최소화 |
| 동일 계정 다수 IP 실패 | 계정 임시 보호 잠금 | 잠금 해제 UX/지원 채널 필요 |
| 국가/ASN 급변 로그인 | 고위험 로그인 플래그 + 재인증 | 출장/원격근무 오탐 관리 |

정리하면 레이트리밋은 편의 기능이 아니라 인증 시스템의 1차 방화벽입니다.

## 권한 검사 누락을 막는 테스트 전략

보안 리뷰에서 가장 자주 나오는 문장이 "새 라우트에 권한 체크가 빠졌습니다"입니다. 개인 실수로 돌리면 반복됩니다. 테스트 구조로 막아야 합니다.

### 1) 엔드포인트 계약 테스트

- 익명 호출은 반드시 `401`
- 인증 사용자지만 권한 없음은 `403`
- 올바른 권한 사용자만 `2xx`

이 세 케이스를 모든 민감 엔드포인트 템플릿 테스트로 고정하면, 새 API 추가 시 누락 확률이 급격히 줄어듭니다.

### 2) 정책 회귀 테스트

역할/권한 매핑 테이블을 코드 데이터로 관리하면 변경 PR마다 회귀 테스트를 돌릴 수 있습니다. 예를 들어 `editor`가 갑자기 `users:delete`를 갖게 되는 사고를 테스트가 바로 잡아냅니다.

### 3) 운영 관측 테스트

`401`/`403` 비율, 로그인 실패율, 토큰 재발급 실패율을 대시보드에 두고 임계치 알람을 걸어야 합니다. 기능 테스트가 통과해도 운영에서 신호를 못 보면 사고를 늦게 발견합니다.

## FastAPI에서 AuthN/AuthZ 경계를 코드로 고정하기

FastAPI는 `Depends` 체인으로 보안 경계를 명시적으로 표현하기 좋습니다. 핵심은 "토큰 해석", "사용자 조회", "권한 검사"를 분리하는 것입니다.

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_access_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
        ) from exc

    user_id = payload.get("sub")
    user = fake_get_user_from_db(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
        )
    return user


def require_permission(permission: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        permissions = set(user.get("permissions", []))
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="요청한 작업 권한이 없습니다.",
            )
        return user

    return checker


@app.get("/profile")
def profile(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"]}


@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, _: dict = Depends(require_permission("users:delete"))):
    return {"deleted_user_id": user_id}
```

이 구조에서 얻는 이점은 명확합니다.

- 인증 실패는 항상 `401`
- 권한 실패는 항상 `403`
- 엔드포인트 코드에서 인증/권한 분기가 사라져 비즈니스 로직 가독성 향상
- 보안 정책 변경 시 의존성 함수만 수정하면 전체 반영

## RBAC를 문자열 비교가 아니라 정책 매핑으로 관리하기

초기 서비스에서는 `if user.role == "admin"`으로 시작해도 됩니다. 운영이 커지면 곧 한계가 옵니다. 역할 수가 늘고, 같은 역할이라도 조직/리소스 범위별 권한이 달라지기 때문입니다.

권장 접근은 "역할 -> 권한 집합"을 데이터로 분리하는 방식입니다.

| Role | Permissions |
| --- | --- |
| `viewer` | `posts:read` |
| `editor` | `posts:read`, `posts:write` |
| `admin` | `posts:*`, `users:delete`, `audit:read` |

미들웨어 또는 `Depends` 검사기는 문자열 역할 자체가 아니라 최종 permission 세트를 검사합니다. 그러면 역할 이름 변경이나 신규 역할 추가가 API 코드 수정으로 번지지 않습니다. 이후 ABAC(속성 기반)나 ReBAC(관계 기반)로 확장할 때도 매핑 레이어가 완충 역할을 합니다.

## 운영 시나리오로 보는 사고 대응

이론만 아는 상태와 운영 가능한 상태의 차이는 "사건 발생 시 즉시 판단 가능한가"입니다. 아래는 실제로 자주 발생하는 시나리오입니다.

### 1) 토큰이 로그에 노출되었습니다

원인 예시는 디버그 로그에 `Authorization` 헤더를 그대로 출력한 경우입니다.

즉시 조치 순서:

1. 로그 수집 파이프라인에서 민감 헤더 마스킹 정책 적용
2. 노출 시간대 발급 토큰 강제 폐기
3. 사용자 세션 강제 재인증
4. 재발 방지로 로거 필터 테스트 추가

핵심은 "로그 시스템도 데이터 유출 경로"라는 인식입니다.

### 2) 새 엔드포인트에 권한 검사를 빼먹었습니다

배포 직후 QA나 버그바운티에서 발견되는 전형적 사고입니다.

대응 포인트:

- 라우트 선언 단계에서 보안 의존성을 강제하는 템플릿 사용
- PR 체크리스트에 "민감 리소스 권한 검사" 항목 의무화
- OpenAPI 스캔으로 보호 경로/비보호 경로 차이 자동 탐지

코드 리뷰를 잘하는 것만으로는 부족합니다. 구조적으로 누락이 불가능하게 만들어야 합니다.

### 3) 리프레시 토큰 재사용이 탐지되었습니다

이미 폐기한 토큰이 다시 들어왔다면 탈취를 강하게 의심해야 합니다.

권장 처리:

- 해당 계정의 모든 리프레시 토큰 계보(family) 폐기
- 고위험 이벤트로 SIEM에 전송
- 사용자에게 보안 알림 + 최근 로그인 이력 확인 UX 제공
- 필요 시 비밀번호 초기화 및 MFA 재등록 강제

"재발급 실패"로 끝내면 사고를 놓칩니다. 재사용 탐지는 침해지표(IOC)입니다.

### 4) DB 백업에서 평문 비밀번호가 발견되었습니다

이 경우는 취약점이 아니라 사고입니다. 즉시 사고 대응 프로세스로 전환해야 합니다.

- 신규 가입/비밀번호 변경 API 즉시 차단 또는 유지보수 모드 전환
- 전체 사용자 비밀번호 강제 재설정
- 법적/정책적 공지 의무 검토
- 백업 파이프라인과 데이터 마스킹 정책 전면 재점검

예방의 핵심은 단 하나입니다. 애초에 평문을 저장하지 않는 것입니다.

## 자주 놓치는 취약점 세 가지

### 타이밍 공격

사용자 존재 여부나 비밀번호 일치 여부를 처리 시간 차이로 노출하면 정보 누출이 발생합니다. 인증 실패 메시지를 통일하고, 가능한 한 일정한 경로로 처리해야 합니다.

### JWT `alg:none` 혼동

라이브러리 기본값에 의존해 알고리즘 검증이 열려 있으면 서명 없는 토큰이 수용될 위험이 있습니다. 항상 허용 알고리즘 allowlist를 명시해야 합니다.

### 로그인 레이트리밋 부재

강한 비밀번호 정책이 있어도 무차별 대입 시도를 제한하지 않으면 방어선이 약해집니다. 사용자 계정 기준 + IP 기준 + 장치 지문 기준을 함께 고려한 제한이 필요합니다.

## 프로덕션 체크리스트

- [ ] 인증 관련 모든 트래픽을 HTTPS로만 허용했습니다.
- [ ] 브라우저 저장 토큰은 `httpOnly`, `secure`, `sameSite` 정책을 적용했습니다.
- [ ] 액세스 토큰은 짧은 만료, 리프레시 토큰은 회전 + 재사용 탐지를 적용했습니다.
- [ ] 로그인/토큰 재발급/권한 거부 이벤트를 감사 로그로 남깁니다.
- [ ] 로그인 엔드포인트에 레이트리밋과 계정 잠금 정책을 적용했습니다.
- [ ] 비밀키는 코드 저장소가 아닌 시크릿 매니저에서 관리합니다.
- [ ] `401`과 `403`를 구분해 API/모니터링 대시보드에서 추적합니다.

## 시니어가 보는 흔한 실수와 이유

- "JWT니까 서버 상태가 필요 없다"고 믿고 강제 로그아웃 요구사항을 뒤늦게 처리합니다. 결과적으로 블랙리스트/회전 정책을 급하게 붙이며 복잡도가 폭증합니다.
- "권한은 프론트엔드에서 막으니 충분하다"고 착각합니다. 클라이언트는 신뢰 경계 바깥이므로 서버 재검증이 필수입니다.
- "해시 알고리즘은 SHA-256이면 충분하다"고 생각합니다. 빠른 해시는 공격자 비용을 낮추는 선택입니다.
- "로그는 많을수록 좋다"고 보고 인증 헤더를 원문으로 남깁니다. 관측성 강화가 유출 경로가 되는 역설을 만듭니다.
- "OAuth2는 나중에"라고 미루며 커스텀 인증을 키웁니다. 조직 규모가 커질수록 전환 비용이 기하급수적으로 늘어납니다.

좋은 보안 설계는 영리한 트릭이 아니라 보수적인 기본기의 조합입니다. 알고리즘 선택, 토큰 수명, 권한 경계, 운영 로그 정책을 단순하고 반복 가능하게 만드는 팀이 장기적으로 사고를 줄입니다.

## 처음 질문으로 돌아가기

- **authentication과 authorization은 무엇이 다를까요?**
  - 인증은 "누구인지"를 확인해 `401` 경계를 결정하고, 권한은 "무엇을 할 수 있는지"를 확인해 `403` 경계를 결정합니다. 운영 로그와 API 응답에서 이 차이가 분리되어야 원인 분석이 정확해집니다.
- **비밀번호 저장에서 최소한으로 지켜야 할 안전 기준은 무엇일까요?**
  - 비밀번호는 절대 평문이나 MD5/SHA-256으로 저장하지 않고, bcrypt/argon2 같은 전용 KDF로 해시해야 합니다. 검증 지연을 100~300ms 수준으로 튜닝하고, 파라미터 상향 시 재해시 전략까지 포함해야 최소 기준을 충족합니다.
- **session과 JWT는 각각 언제 더 자연스러울까요?**
  - 브라우저 중심 웹앱에서는 보안 쿠키 세션이 단순하고 강력하며, 다중 API/모바일 구조에서는 짧은 JWT와 회전형 리프레시가 자연스럽습니다. 선택 기준은 유행이 아니라 폐기 전략, XSS/CSRF 위험, 운영 복잡도입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): Database Layer](./05-database-layer.md)
- **인증과 권한 (현재 글)**
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Passlib bcrypt docs](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [JWT Introduction](https://jwt.io/introduction)

Tags: Backend, Auth, Security, JWT, Python
