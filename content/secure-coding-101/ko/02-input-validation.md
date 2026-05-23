---
series: secure-coding-101
episode: 2
title: "Secure Coding 101 (2/10): 입력값 검증"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - InputValidation
  - SecureCoding
  - Pydantic
  - OWASP
  - AppSec
seo_description: Allowlist, schema 기반 검증, 경계 정책 그리고 안전한 입력 처리의 5단계
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (2/10): 입력값 검증

애플리케이션이 흔들리는 가장 흔한 시작점은 입력입니다. 로그인 폼, 검색창, JSON payload, 파일 이름, 쿼리 문자열처럼 겉보기에는 단순한 값도 서버가 그대로 믿는 순간 버그와 공격이 함께 들어옵니다. SQL injection, XSS, 경로 조작, 안전하지 않은 역직렬화가 모두 여기서 출발합니다.

여기서는 입력값 검증을 단순한 if 문 모음이 아니라, 신뢰 경계에서 시스템을 예측 가능하게 만드는 계약으로 보겠습니다. 이 관점을 잡으면 검증 로직을 여기저기 흩뿌리지 않고, 스키마와 경계 설계로 정리하는 이유도 자연스럽게 이해할 수 있습니다.

![Secure Coding 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/02/02-01-concept-at-a-glance.ko.png)
*Secure Coding 101 2장 흐름 개요*

## 먼저 던지는 질문

- allowlist와 denylist는 무엇이 다를까요?
- 입력 스키마를 쓰면 ad-hoc 검증보다 무엇이 좋아질까요?
- 입력 경계는 정확히 어디라고 봐야 할까요?

## 왜 중요한가

OWASP Top 10의 상당수 항목은 결국 서버가 입력을 너무 쉽게 신뢰했기 때문에 생깁니다. 클라이언트가 화면에서 한 번 체크했다고 해서 서버가 안심하면 안 됩니다. 공격자는 브라우저 UI를 통하지 않고 바로 HTTP 요청을 만들 수 있고, 자동화 도구로 수천 개의 변형 입력을 보낼 수 있습니다.

검증이 중요한 또 다른 이유는 보안뿐 아니라 운영 안정성입니다. 타입과 범위가 맞지 않는 값이 내부 로직까지 흘러 들어가면 장애는 더 뒤에서 터집니다. 그때는 원인 파악도 어려워지고, 예외 메시지로 내부 구조를 노출할 가능성도 커집니다. 경계에서 입력을 좁혀 두면 이후 코드는 훨씬 단순해집니다.

## 한눈에 보는 구조

이 흐름에서 핵심은 검증이 한 번에 끝나는 단일 필터가 아니라는 점입니다. 경계에서 기본 형식을 걸러 내고, 스키마에서 payload의 모양을 고정하고, 그다음 비즈니스 규칙에서 도메인 제약을 확인합니다. 세 층이 분리돼야 각 단계의 책임이 분명해집니다.

## 핵심 용어

- **허용 목록(allowlist)**: 허용한 값만 통과시키는 방식입니다.
- **차단 목록(denylist)**: 금지한 값만 막는 방식입니다. 우회 패턴이 계속 생기므로 늘 불완전합니다.
- **스키마(schema)**: 입력 모양과 제약을 명시한 계약입니다.
- **정제(sanitization)**: 위험한 조각을 제거하거나 이스케이프하는 작업입니다.
- **정규화(canonicalization)**: 입력을 한 가지 표준 형태로 맞춘 뒤 비교와 검증을 쉽게 만드는 과정입니다.

## 바꾸기 전과 후

**바꾸기 전**: 각 라우트가 제각각 if 문으로 검증합니다. 어떤 곳은 길이만 보고, 어떤 곳은 형식만 보고, 빠뜨린 한 곳이 곧 버그와 공격 경로가 됩니다.

**바꾼 후**: 스키마가 입력 모양을 한 번에 검증합니다. 라우트와 서비스 함수는 비즈니스 규칙에 집중하고, 방어 코드는 경계에 모입니다.

## 실습: 입력을 안전하게 검증하는 5단계

### 1단계 — 먼저 타입을 고정합니다

```python
def to_int(raw: str) -> int:
    if not raw.lstrip("-").isdigit():
        raise ValueError("not an integer")
    return int(raw)
```

타입이 불분명한 상태에서 범위나 형식을 논하면 검증이 흔들립니다. 문자열을 숫자로 해석할 수 있는지 먼저 분명히 해야 이후 규칙도 의미를 갖습니다. 가장 바깥 경계에서 타입을 고정하는 이유가 여기에 있습니다.

### 2단계 — 범위와 길이를 확인합니다

```python
def parse_quantity(n: int) -> int:
    if not (1 <= n <= 1000):
        raise ValueError("quantity out of range")
    return n
```

정상 타입이라고 해서 안전한 값은 아닙니다. 지나치게 큰 수, 비정상적으로 긴 문자열, 음수가 되면 안 되는 필드는 도메인 규칙 안에서 따로 막아야 합니다. 운영에서 자원 고갈이나 엉뚱한 계산 오류는 이런 범위 누락에서 자주 시작합니다.

### 3단계 — 형식은 허용 목록 정규식으로 제한합니다

```python
import re
USERNAME = re.compile(r"^[a-z0-9_]{3,20}$")

def parse_username(raw: str) -> str:
    if not USERNAME.match(raw):
        raise ValueError("invalid username")
    return raw
```

형식 검사는 무엇을 막을지보다 무엇만 허용할지를 먼저 적는 편이 안전합니다. denylist는 금지 패턴을 계속 추가해야 하지만, allowlist는 허용 가능한 표면 자체를 작게 유지합니다. 사용자 이름처럼 규칙이 분명한 값일수록 이 차이가 더 크게 드러납니다.

### 4단계 — payload 전체를 하나의 스키마로 받습니다

```python
from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    username: str = Field(pattern=r"^[a-z0-9_]{3,20}$")
    age: int = Field(ge=0, le=150)
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
```

필드별 검증을 흩어 두면 라우트마다 누락과 중복이 생깁니다. 스키마는 입력 형식, 문서, 에러 처리 기준을 한곳에 모아 줍니다. 팀 단위 개발에서는 이 장점이 특히 큽니다. 누가 새로운 필드를 추가해도 계약이 한곳에서 바뀌기 때문입니다.

### 5단계 — 신뢰 경계를 코드에 명시합니다

```python
def handle_signup(payload: dict):
    user = CreateUser(**payload)  # 입력 경계
    save_user(user)               # 이후 코드는 신뢰 가능한 객체를 받음
```

이 한 줄이 신뢰 경계를 분명히 보여 줍니다. `CreateUser(**payload)` 이전은 신뢰할 수 없는 외부 입력이고, 그 이후는 검증을 통과한 내부 객체입니다. 경계를 명시하면 내부 함수에서 매번 방어 코드를 되풀이하지 않아도 됩니다.

## 이 코드에서 먼저 볼 점

- 허용 목록은 차단 목록보다 공격 표면을 더 작게 유지합니다.
- 스키마 검증은 문서와 실행 코드를 동시에 만족합니다.
- 경계가 분명할수록 내부 로직은 단순해지고 예외 처리도 쉬워집니다.
- 검증 순서는 타입, 범위, 형식, 전체 스키마, 경계 선언으로 잡는 편이 안정적입니다.

## 실무에서 자주 헷갈리는 지점

1. **차단 목록만 쓰는 경우**: 새로운 우회 패턴은 계속 나옵니다. 허용 목록이 기본이어야 합니다.
2. **클라이언트 검증을 서버에서 신뢰하는 경우**: 브라우저는 사용자를 돕는 층이지, 서버를 보호하는 층이 아닙니다.
3. **raw dict를 시스템 전체로 흘려보내는 경우**: 어떤 키가 언제 들어오는지 알 수 없어 예외와 누락이 늘어납니다.
4. **오류 메시지에 원본 입력을 그대로 되돌리는 경우**: 사용자 입력이 곧 XSS 경로가 될 수 있습니다.
5. **국제화 문자열을 바이트 단위로 자르는 경우**: 한글과 이모지처럼 멀티바이트 문자가 쉽게 깨집니다.

## 실무에서는 이렇게 봅니다

대부분의 FastAPI와 Flask 팀은 라우트 진입점에서 Pydantic이나 marshmallow로 payload를 먼저 검증합니다. 유효한 입력은 typed object로 내부에 전달하고, 잘못된 입력은 즉시 4xx 응답으로 돌려보냅니다. 이 구조를 잡으면 비즈니스 함수는 보안 방어보다 업무 규칙에 집중할 수 있습니다.

또한 선임 엔지니어일수록 검증을 사용자 경험과 분리해서 보지 않습니다. 오류 메시지는 충분히 친절해야 하지만, 원본 입력이나 내부 규칙을 과하게 노출해서는 안 됩니다. 검증은 막는 일만이 아니라, 시스템의 계약을 안정적으로 드러내는 일이기도 합니다.

## 선임 엔지니어는 이렇게 생각합니다

- 스키마는 계약이며, 검증은 계약을 실행하는 코드입니다.
- 모든 신뢰 경계는 코드에서 드러나야 합니다.
- 공격자도 오류 메시지를 읽는다고 가정합니다.
- 기본값은 허용이 아니라 거부이며, 허용은 예외적으로 열어 줍니다.
- 정규화는 검증 전에 해야 같은 값을 한 방식으로 다룰 수 있습니다.

## 체크리스트

- [ ] 모든 라우트가 스키마 검증을 거칩니다.
- [ ] 허용 목록이 기본 규칙입니다.
- [ ] 오류 메시지가 민감한 입력이나 내부 구조를 노출하지 않습니다.
- [ ] 길이, 범위, 형식 규칙이 명시돼 있습니다.

## 연습 문제

1. 우편 주소 입력용 Pydantic 스키마를 만들어 보세요.
2. 파일 이름에서 경로 조작을 막는 정규식을 작성해 보세요.
3. 같은 입력에 서로 다른 정규화 규칙 두 개를 적용해 보고 결과 차이를 비교해 보세요.

## 정리와 다음 글

입력값 검증은 시스템을 예측 가능하게 만드는 첫 번째 계약입니다. 이 글에서는 허용 목록, 스키마 검증, 경계 선언을 중심으로 입력을 좁히는 방법을 정리했습니다.

다음 글에서는 입력을 통과한 사용자가 누구인지 확인하고, 그 상태를 안전하게 유지하는 인증과 세션을 다룹니다.

## 심화 실전 노트: 경로 조작, ReDoS, 파일 업로드, 인코딩 공격

입력 검증 원칙을 알아도 실제 공격은 예상하지 못한 경로로 들어옵니다. 여기서는 입력값 검증에서 가장 자주 뚫리는 네 가지 공격 벡터를 재현하고, 각각의 방어 패턴을 코드로 보여 줍니다.

### 경로 조작(Path Traversal) 재현과 방어

공격자가 파일 다운로드 기능에서 `../../etc/passwd` 같은 값을 넣으면 의도하지 않은 파일이 노출됩니다.

```python
# 취약한 패턴 — 사용자 입력을 경로에 직접 결합
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/download")
def download(filename: str):
    # 위험: ../를 이용해 상위 디렉터리 접근 가능
    path = f"/var/uploads/{filename}"
    return FileResponse(path)
```

```python
# 방어 패턴 — 정규화 후 기준 디렉터리 안에 있는지 확인
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()
UPLOAD_DIR = Path("/var/uploads").resolve()

@app.get("/download")
def download(filename: str):
    # 1) 경로 구분자와 null 바이트 차단
    if "\x00" in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="invalid filename")

    # 2) resolve()로 심볼릭 링크와 ..를 풀어 실제 경로를 얻음
    target = (UPLOAD_DIR / filename).resolve()

    # 3) 기준 디렉터리 안에 있는지 확인
    if not str(target).startswith(str(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="path traversal blocked")

    if not target.is_file():
        raise HTTPException(status_code=404, detail="not found")

    return FileResponse(target)
```

핵심은 `resolve()`로 경로를 정규화한 뒤 기준 디렉터리(`UPLOAD_DIR`) 안에 있는지 비교하는 것입니다. 문자열에서 `..`만 제거하는 방식은 이중 인코딩(`%2e%2e%2f`)이나 OS별 차이로 쉽게 우회됩니다.

### ReDoS(정규표현식 서비스 거부) 패턴

정규식이 백트래킹을 과도하게 일으키면 단일 요청으로 서버 CPU를 점유할 수 있습니다.

```python
import re
import time

# 위험한 정규식 — 중첩 반복자가 지수적 백트래킹을 유발
DANGEROUS = re.compile(r"^(a+)+$")

# 테스트: 'a' * 25 + 'b' → 매칭 실패하면서 백트래킹 폭발
start = time.time()
DANGEROUS.match("a" * 25 + "b")
elapsed = time.time() - start
print(f"elapsed: {elapsed:.2f}s")  # 수 초~수십 초 소요
```

```python
# 안전한 대안 — 중첩 반복자 제거, 또는 시간 제한 적용
import re
import signal

SAFE = re.compile(r"^a+$")  # 중첩 제거

# 또는 시간 제한으로 방어
class RegexTimeout(Exception):
    pass

def handler(signum, frame):
    raise RegexTimeout("regex timed out")

def safe_match(pattern: re.Pattern, text: str, timeout_sec: float = 1.0):
    """정규식 매칭에 시간 제한을 거는 래퍼"""
    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, timeout_sec)
    try:
        return pattern.match(text)
    except RegexTimeout:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
```

운영에서는 정규식을 새로 추가할 때 반드시 ReDoS 취약 패턴 검사 도구(예: `rxxr2`, `safe-regex`)를 CI에 넣어야 합니다. 또한 입력 길이를 제한하면 백트래킹이 폭발하기 전에 차단할 수 있습니다.

### 파일 업로드 검증

파일 업로드는 확장자, MIME 타입, 파일 크기, 내용 시그니처를 모두 확인해야 합니다. 하나만 보면 우회됩니다.

```python
import magic
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
ALLOWED_MIMES = {"image/png", "image/jpeg", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload")
async def upload_image(file: UploadFile):
    # 1) 확장자 확인
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="disallowed extension")

    # 2) 파일 크기 확인 (스트리밍 방식)
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="file too large")

    # 3) 매직 바이트로 실제 파일 타입 확인
    detected_mime = magic.from_buffer(content[:2048], mime=True)
    if detected_mime not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=400,
            detail=f"content type mismatch: {detected_mime}",
        )

    # 4) 안전한 파일명 생성 (원본 이름 사용하지 않음)
    import uuid
    safe_name = f"{uuid.uuid4().hex}{ext}"
    save_path = Path("/var/uploads") / safe_name
    save_path.write_bytes(content)

    return {"filename": safe_name}
```

공격자는 `.jpg` 확장자에 PHP 코드를 넣거나, MIME 헤더만 위조하거나, 파일 내부에 스크립트를 삽입합니다. 매직 바이트 검사와 새 파일명 생성을 함께 적용해야 웹셸 업로드를 막을 수 있습니다.

### 인코딩 정규화 공격

같은 문자를 여러 인코딩으로 표현할 수 있으면 검증을 우회할 수 있습니다. Unicode에는 같아 보이는 문자가 다른 코드 포인트로 존재합니다.

```python
import unicodedata

def normalize_and_validate(raw: str) -> str:
    """NFC 정규화 후 검증 — 시각적 위장 공격 방어"""
    # 1) NFC 정규화: 조합형을 완성형으로 통일
    normalized = unicodedata.normalize("NFC", raw)

    # 2) 제어 문자 제거
    cleaned = "".join(
        ch for ch in normalized
        if unicodedata.category(ch) not in ("Cc", "Cf")
    )

    # 3) 혼합 스크립트 탐지 (호모글리프 공격 방어)
    scripts = set()
    for ch in cleaned:
        try:
            script = unicodedata.name(ch).split()[0]
            scripts.add(script)
        except ValueError:
            pass

    # Latin + Cyrillic 혼합은 의심
    if "CYRILLIC" in scripts and "LATIN" in scripts:
        raise ValueError("mixed script detected — possible homoglyph attack")

    return cleaned

# 예시: 'а'(키릴 문자)와 'a'(라틴 문자)는 눈으로 구분 불가
try:
    normalize_and_validate("pаypal")  # 키릴 а 포함
except ValueError as e:
    print(f"차단됨: {e}")
```

URL이나 이메일 주소에서도 같은 문제가 발생합니다. 퓨니코드(punycode) 도메인에서 `xn--pypal-4ve.com` 같은 도메인이 `paypal.com`으로 보이는 피싱에 이용됩니다. 입력을 정규화하고 혼합 스크립트를 탐지하는 것이 기본 방어입니다.

### SSRF를 막는 URL 검증

서버가 사용자 입력 URL을 그대로 요청하면 내부 네트워크가 노출됩니다.

```python
import ipaddress
from urllib.parse import urlparse
from fastapi import HTTPException

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

ALLOWED_SCHEMES = {"http", "https"}

def validate_url(url: str) -> str:
    """외부 URL만 허용 — SSRF 방어"""
    parsed = urlparse(url)

    # 1) 스킴 제한
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise HTTPException(status_code=400, detail="scheme not allowed")

    # 2) 호스트 추출 및 DNS 해석
    import socket
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="no hostname")

    try:
        resolved = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="DNS resolution failed")

    # 3) 해석된 IP가 내부 네트워크인지 확인
    for family, _, _, _, sockaddr in resolved:
        ip = ipaddress.ip_address(sockaddr[0])
        for net in BLOCKED_NETWORKS:
            if ip in net:
                raise HTTPException(
                    status_code=400,
                    detail="internal network access blocked",
                )

    return url
```

DNS rebinding 공격을 방어하려면 해석된 IP로 직접 연결하거나, 요청 시점에 다시 검증해야 합니다. 또한 리다이렉트를 따라갈 때도 매 단계에서 같은 검증을 반복해야 합니다.

### 입력 검증 계층 정리표

| 계층 | 검증 대상 | 도구/패턴 | 실패 시 응답 |
| --- | --- | --- | --- |
| 네트워크 | 요청 크기, 속도 | nginx/WAF 설정 | 413, 429 |
| 프레임워크 | Content-Type, 인코딩 | FastAPI 자동 파싱 | 422 |
| 스키마 | 타입, 범위, 형식 | Pydantic, marshmallow | 400 + 필드별 에러 |
| 도메인 | 비즈니스 제약 | 서비스 함수 내 검증 | 409, 422 |
| 저장 | FK 존재, 유니크 제약 | DB 제약 조건 | 409 |

각 계층은 독립적으로 실패를 잡습니다. 상위 계층이 뚫려도 하위 계층이 마지막 방어선이 됩니다. 이 구조가 심층 방어의 입력 검증 버전입니다.

### 대량 할당(Mass Assignment) 방어

API가 JSON payload를 그대로 ORM 모델에 매핑하면 클라이언트가 의도하지 않은 필드를 주입할 수 있습니다. 예를 들어 사용자 등록 API에서 `{"username": "alice", "role": "admin"}`을 보내면 role 필드가 그대로 저장될 수 있습니다.

```python
from pydantic import BaseModel, Field
from fastapi import FastAPI

# 안전한 패턴: 입력 스키마와 내부 모델을 분리합니다
class UserCreateRequest(BaseModel):
    """클라이언트가 보낼 수 있는 필드만 정의"""
    username: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=8)

class UserInternal(BaseModel):
    """내부에서만 사용하는 전체 필드"""
    username: str
    email: str
    password_hash: str
    role: str = "user"  # 기본값 고정, 외부 입력 불가
    is_active: bool = True

app = FastAPI()

@app.post("/users")
def create_user(req: UserCreateRequest):
    # 외부 스키마에서 허용한 필드만 사용
    internal = UserInternal(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        # 역할과 is_active는 서버가 결정됩니다
    )
    return save_user(internal)
```

핵심은 입력 스키마(`UserCreateRequest`)와 내부 모델(`UserInternal`)을 분리하는 것입니다. `**payload`로 바로 모델을 생성하면 클라이언트가 어떤 필드든 덮어쓸 수 있습니다. Django에서는 `ModelForm`의 `fields` 선언, SQLAlchemy에서는 `__init__`에서 허용 필드를 명시하는 것이 같은 원칙입니다.

### 멀티파트 요청과 JSON 혼합 공격

파일 업로드와 JSON 필드가 혼합된 멀티파트 요청에서는 각 파트를 독립적으로 검증해야 합니다. Content-Type이 `multipart/form-data`일 때 JSON 파트를 파싱하면서 타입 검증을 누락하는 경우가 많습니다.

```python
from pydantic import BaseModel, Field
from fastapi import FastAPI, UploadFile, Form, HTTPException
import json

class MetadataSchema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    tags: list[str] = Field(max_length=10)

app = FastAPI()

@app.post("/documents")
async def upload_document(
    file: UploadFile,
    metadata: str = Form(...),  # JSON 문자열로 받음
):
    # 메타데이터 JSON 파싱 및 스키마 검증
    try:
        meta_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="invalid JSON in metadata")

    meta = MetadataSchema(**meta_dict)  # 스키마로 검증

    # 파일 검증은 별도로
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file too large")

    return {"title": meta.title, "filename": file.filename}
```

멀티파트 요청의 각 파트는 서로 다른 검증 규칙이 필요합니다. 파일 파트는 크기와 타입을, 텍스트 파트는 스키마를 각각 적용합니다. 하나의 요청이라고 해서 하나의 검증으로 끝내면 안 됩니다.

## 처음 질문으로 돌아가기

- **allowlist와 denylist는 무엇이 다를까요?**
  - 본문의 USERNAME 정규식 예시처럼 allowlist는 "이것만 허용"을 선언해 공격 표면을 작게 유지합니다. denylist는 금지 패턴을 계속 추가해야 하고, 인코딩 정규화 공격에서 보았듯이 같은 문자의 다른 표현만으로 우회됩니다.
- **입력 스키마를 쓰면 ad-hoc 검증보다 무엇이 좋아질까요?**
  - Pydantic `CreateUser` 예시에서 보았듯이 스키마는 검증 규칙, API 문서, 에러 메시지 형식을 한곳에 모읍니다. 라우트마다 if 문을 흩뿌리면 어디서 누락이 생겼는지 찾기 어렵지만, 스키마 하나를 보면 계약 전체가 드러납니다.
- **입력 경계는 정확히 어디라고 봐야 할까요?**
  - `handle_signup` 예시의 `CreateUser(**payload)` 한 줄이 경계입니다. 그 이전은 적대적 외부 데이터, 그 이후는 검증을 통과한 내부 객체입니다. 계층 정리표에서 보았듯이 경계는 네트워크, 프레임워크, 스키마, 도메인, 저장소까지 다층으로 존재합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- **입력값 검증 (현재 글)**
- 인증과 세션 (예정)
- 인가와 권한 (예정)
- 안전한 데이터 저장 (예정)
- Secret과 키 관리 (예정)
- SQL Injection과 ORM 안전 사용 (예정)
- XSS와 CSRF 방어 (예정)
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Pydantic docs](https://docs.pydantic.dev/)
- [OWASP — Mass Assignment](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [PortSwigger — Input validation](https://portswigger.net/web-security)
- [Unicode Technical Standard #39 — Unicode Security Mechanisms](https://unicode.org/reports/tr39/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: InputValidation, SecureCoding, Pydantic, OWASP, AppSec

