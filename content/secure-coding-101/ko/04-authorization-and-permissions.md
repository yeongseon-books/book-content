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

## 먼저 던지는 질문

- RBAC와 ABAC는 어떤 차이가 있을까요?
- IDOR는 왜 흔하고도 위험한 인가 취약점일까요?
- 인가 판단은 라우트 수준과 자원 수준에서 어떻게 나눠 봐야 할까요?

## 큰 그림

![Secure Coding 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/04/04-01-concept-at-a-glance.ko.png)

*Secure Coding 101 4장 흐름 개요*

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

## 심화 실전 노트: 취약점 재현, 수정 패턴, OWASP 기준 연결

보안 코드는 추상 원칙만으로 유지되지 않습니다. 공격자가 실제로 어떤 입력을 넣는지, 코드가 어느 지점에서 그 입력을 신뢰하는지, 실패를 탐지했을 때 운영 단계에서 어떤 증거를 남기는지까지 한 흐름으로 연결해야 합니다. 그래서 실무에서는 취약점 이름을 외우는 것보다 "재현 가능한 실패 시나리오"를 먼저 만들고, 수정 후 같은 시나리오가 반드시 차단되는지 확인합니다.

### 취약점 예시 1: 입력 검증 우회와 타입 혼동

```python
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/transfer")
async def transfer(request: Request):
    body = await request.json()
    amount = body.get("amount")
    if amount <= 0:  # 문자열/None 혼합 입력에서 예외 또는 우회
        raise HTTPException(status_code=400, detail="invalid amount")
    return {"accepted": True}
```

위 코드는 숫자형 검증이 없어서 서비스 거부나 우회 입력이 섞일 수 있습니다. 수정 패턴은 명확합니다. 경계에서 스키마를 강제하고, 타입 변환 실패를 비즈니스 로직 진입 전에 종료합니다. Pydantic 모델, 최소/최대 범위, 소수점 스케일 규칙을 함께 사용하면 입력 품질이 크게 올라갑니다.

### 취약점 예시 2: SQL 인젝션과 문자열 결합

```python
# 취약한 패턴
query = f"SELECT * FROM users WHERE email = '{email}'"

# 개선 패턴
query = "SELECT * FROM users WHERE email = :email"
params = {"email": email}
```

핵심은 "ORM을 쓴다"가 아니라 "쿼리 경계를 데이터와 코드로 분리한다"입니다. ORM을 쓰더라도 raw SQL 지점이 남아 있으면 같은 위험이 재발합니다. 코드 리뷰 시에는 저장소 전체에서 문자열 포매팅 기반 쿼리 구성 지점을 일괄 탐색하고, 파라미터 바인딩으로 일관되게 바꾸는 작업이 필요합니다.

### 취약점 예시 3: 토큰 검증 순서 오류

JWT 처리에서 흔한 실패는 서명 검증보다 클레임 사용이 앞서는 경우입니다. 예를 들어 `sub`를 먼저 꺼내 권한 조회를 수행하면, 위조 토큰이 감사 로그에 정상 사용자처럼 남을 수 있습니다. 수정 패턴은 1) 알고리즘 화이트리스트 고정, 2) 서명 검증, 3) 만료/발급자/대상 검증, 4) 권한 매핑 순서를 고정하는 것입니다.

### OWASP 기준에 맞춘 운영 체크

OWASP Top 10 관점에서 이 시리즈 주제를 매핑하면 우선순위가 선명해집니다.

- `A01 Broken Access Control`: 인가 누락, 객체 단위 권한 검증 누락
- `A02 Cryptographic Failures`: 평문 저장, 약한 해시/암호 설정
- `A03 Injection`: SQL/NoSQL/Command Injection
- `A07 Identification and Authentication Failures`: 세션 고정, 토큰 처리 오류
- `A09 Security Logging and Monitoring Failures`: 추적 불가 로그, 경보 부재

중요한 점은 한 항목을 독립 과제로 다루지 않는 것입니다. 예를 들어 접근제어 결함을 줄이려면 인증, 세션, 로깅이 동시에 개선되어야 합니다. 그래서 팀 기준 문서에는 "취약점 분류"와 "수정 완료 조건"을 함께 적어야 합니다. 예를 들어 "재현 입력 차단 + 단위 테스트 + 감사 로그 필드 검증"을 완료 조건으로 명시하면 품질이 안정됩니다.

### 실무 적용 템플릿

보안 이슈 하나를 수정할 때는 다음 순서를 고정하는 편이 효율적입니다.

1. 실패 입력을 테스트로 먼저 고정합니다.
2. 경계 검증, 인코딩, 파라미터 바인딩 중 필요한 패턴을 적용합니다.
3. 같은 클래스의 취약점이 있는 인접 경로를 같이 점검합니다.
4. 로그/메트릭/경보를 추가해 재발 시 빠르게 감지합니다.

이 흐름을 반복하면 보안 코딩이 문서상의 원칙이 아니라 배포 품질의 일부로 자리잡습니다.

### 추가 사례: 수정 패턴을 테스트와 운영 신호로 닫는 방법

취약점 수정이 실패하는 가장 흔한 이유는 코드 한 줄을 고치고 끝냈다고 판단하기 때문입니다. 보안 수정은 항상 세 겹으로 닫아야 합니다. 첫째, 공격 입력을 재현하는 테스트를 추가합니다. 둘째, 실패 원인을 제거하는 수정 패턴을 적용합니다. 셋째, 운영 환경에서 같은 공격이 다시 들어왔을 때 탐지 가능한 로그와 경보를 남깁니다.

예를 들어 XSS 차단을 위해 출력 인코딩을 넣었다면, 템플릿 경로별 인코딩 누락 여부를 점검하고 CSP 위반 로그를 대시보드로 수집해야 합니다. SQL 인젝션을 차단했다면 파라미터 바인딩 사용률을 정적 점검으로 확인하고, 쿼리 오류율 급증 알람을 설정해야 합니다. 이렇게 테스트, 코드, 운영 신호를 함께 묶어야 OWASP 항목이 문서상의 체크가 아니라 실제 방어선으로 작동합니다.

### 보강 메모: 보안 수정 완료 조건

수정 완료는 "동작함"이 아니라 "공격 입력 차단 + 회귀 테스트 통과 + 운영 탐지 가능" 세 조건을 만족할 때 선언해야 합니다. 이 기준을 팀 규칙으로 고정하면 동일 취약점의 반복 발생률이 빠르게 낮아집니다.

## 처음 질문으로 돌아가기

- **RBAC와 ABAC는 어떤 차이가 있을까요?**
  - 본문의 기준은 인가와 권한를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **IDOR는 왜 흔하고도 위험한 인가 취약점일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **인가 판단은 라우트 수준과 자원 수준에서 어떻게 나눠 봐야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Authorization, RBAC, ABAC, LeastPrivilege, SecureCoding
