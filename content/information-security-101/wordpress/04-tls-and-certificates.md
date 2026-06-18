---
series: information-security-101
episode: 4
title: "바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 정보보안
  - TLS
  - HTTPS
  - 인증서
  - AI보안
language: ko
---

# 바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서

이 글은 **바이브코딩을 위한 정보 보안 기초** 시리즈의 4편입니다. AI가 만들어주는 코드에는 보안 취약점이 숨어 있을 수 있습니다. 이번에는 TLS와 인증서에서 AI 생성 코드가 자주 만드는 구멍을 다룹니다.

---

AI에게 "외부 API를 호출하는 코드를 만들어줘"라고 하면 HTTP 요청 코드가 나옵니다. 그런데 그 코드에 `verify=False`가 있거나, TLS 1.0을 허용하는 설정이 들어가 있는 경우가 있습니다. "개발 환경에서는 괜찮다"는 식으로 주석까지 달려있기도 합니다. 개발 환경에서 쓰던 코드가 그대로 프로덕션에 올라가는 것이 실제 사고의 경로입니다.

> "브라우저의 자물쇠 아이콘은 마법이 아닙니다. 인증서 체인이 올바르게 검증되었고, 핸드셰이크가 강한 암호군으로 완료되었으며, 만료되지 않았다는 표시입니다. AI가 인증서 검증을 끄는 코드를 만들었다면, 자물쇠를 직접 뽑아낸 것과 같습니다."

## 이 글에서 다룰 질문들

- TLS는 정확히 무엇을 보장하나요?
- `verify=False`가 왜 위험한가요?
- 인증서 만료를 어떻게 자동으로 탐지할 수 있을까요?
- AI가 TLS 설정에서 자주 만드는 잘못된 코드는 무엇인가요?
- 내부 서비스 간 통신에서도 TLS가 필요한가요?

---

## 바이브코딩 관점: AI가 TLS 코드에서 자주 만드는 취약점

### Before: AI가 생성하는 취약한 TLS 코드 패턴

```python
# 패턴 1: 인증서 검증 비활성화 — 중간자 공격에 완전히 노출
import requests

response = requests.get("https://api.example.com/data", verify=False)
# InsecureRequestWarning: Unverified HTTPS request is being made
# AI가 "개발 환경용"이라고 주석을 달지만 프로덕션에 그대로 올라간다

# 패턴 2: 오래된 TLS 버전 허용
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.minimum_version = ssl.TLSVersion.TLSv1  # TLS 1.0은 2021년 IETF에서 폐기

# 패턴 3: 약한 암호군 허용
context.set_ciphers("ALL")  # DES, RC4 같은 취약한 암호군도 포함
```

### After: 올바른 TLS 설정

```python
import requests
import ssl

# 인증서 검증 활성화 (기본값이지만 명시적으로 표현)
response = requests.get("https://api.example.com/data", verify=True)

# TLS 1.2 이상만 허용
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.maximum_version = ssl.TLSVersion.TLSv1_3

# 강한 암호군만 허용 (AES-GCM 기반)
context.set_ciphers(
    "ECDHE-ECDSA-AES256-GCM-SHA384:"
    "ECDHE-RSA-AES256-GCM-SHA384:"
    "ECDHE-ECDSA-AES128-GCM-SHA256"
)

# 인증서 검증 필수
context.check_hostname = True
context.verify_mode = ssl.CERT_REQUIRED
```

---

## TLS가 보장하는 것과 보장하지 않는 것

HTTPS를 쓴다고 모든 보안 문제가 해결되는 것은 아닙니다.

| TLS가 보장하는 것 | TLS가 보장하지 않는 것 |
| --- | --- |
| 전송 중 데이터 암호화 | 서버 측 데이터 보안 |
| 서버 신원 확인 (인증서) | 코드의 비즈니스 로직 보안 |
| 중간자 변조 방지 | 입력값 검증 |
| 데이터 무결성 | 인증/인가 처리 |

```python
# TLS는 전송을 보호하지만, 서버 코드 문제는 막지 못한다
# HTTPS를 써도 아래 문제들은 그대로 남는다:
# - SQL 인젝션: AI가 만든 쿼리에 파라미터 바인딩 없음
# - 약한 비밀번호 해시: SHA-256으로 저장
# - 권한 검사 없음: 모든 사용자가 관리자 기능 접근
```

---

## 인증서 만료 자동 탐지

인증서 만료는 서비스 장애의 흔한 원인입니다. AI가 만든 코드에는 인증서 만료 모니터링이 빠져 있는 경우가 많습니다.

```python
import ssl
import socket
from datetime import datetime, timezone

def check_cert_expiry(hostname: str, port: int = 443) -> dict:
    """인증서 만료일 확인 — 30일 이내 만료 시 경고"""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()

    expiry_str = cert["notAfter"]
    expiry_date = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
    expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    days_left = (expiry_date - now).days

    return {
        "hostname": hostname,
        "expires_at": expiry_date.isoformat(),
        "days_left": days_left,
        "warning": days_left < 30,
        "critical": days_left < 7,
    }

# 사용 예시
result = check_cert_expiry("api.example.com")
if result["critical"]:
    print(f"긴급: 인증서 {result['days_left']}일 후 만료!")
elif result["warning"]:
    print(f"경고: 인증서 {result['days_left']}일 후 만료")
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| `verify=False` 설정 | 중간자 공격에 완전히 노출 | 항상 `verify=True` (기본값) |
| TLS 1.0/1.1 허용 | POODLE, BEAST 등 알려진 취약점 존재 | TLS 1.2 이상만 허용 |
| 인증서 만료 모니터링 없음 | 만료 시 갑작스러운 서비스 장애 | 30일 전 자동 알림 설정 |
| 내부 서비스 간 TLS 미사용 | 내부망도 완전히 신뢰할 수 없다 | Zero Trust: 내부도 TLS 적용 |

---

## AI 팁: TLS 코드를 올바르게 요청하는 법

1. **`verify=False` 탐지**: "이 코드에서 SSL 인증서 검증이 비활성화된 부분이 있나요?"
2. **TLS 버전 확인**: "TLS 버전이 1.2 이상으로 설정되어 있나요?"
3. **인증서 모니터링 요청**: "인증서 만료일을 확인하고 30일 전에 경고하는 코드를 추가해주세요"
4. **내부 통신 TLS**: "내부 서비스 간 호출에도 TLS를 적용하는 코드를 만들어주세요"

---

## 실전 체크리스트

- [ ] 모든 외부 API 호출에서 `verify=True`가 설정되어 있다 (또는 기본값)
- [ ] TLS 1.2 이상만 허용하도록 설정되어 있다
- [ ] 인증서 만료 모니터링이 구현되어 있다 (30일 전 알림)
- [ ] `verify=False`나 `CERT_NONE` 설정이 코드베이스에 없다
- [ ] 내부 서비스 간 통신에도 TLS가 적용되어 있다
- [ ] Let's Encrypt 또는 자동 갱신이 설정되어 있다

---

## 처음 질문으로 돌아가기

- **TLS는 정확히 무엇을 보장하나요?**
  전송 중 데이터 암호화, 서버 신원 확인, 중간자 변조 방지를 보장합니다. 서버 코드의 보안(SQL 인젝션, 약한 해시 등)은 별도로 처리해야 합니다.

- **`verify=False`가 왜 위험한가요?**
  인증서 검증을 끄면 중간자 공격에 완전히 노출됩니다. 공격자가 위조된 인증서를 제시해도 클라이언트가 그대로 연결하기 때문입니다. 개발 환경이라도 `verify=False`는 쓰지 않는 것이 원칙입니다.

- **AI가 TLS 설정에서 자주 만드는 잘못된 코드는 무엇인가요?**
  `verify=False`, TLS 1.0 허용, 약한 암호군 허용, 인증서 만료 모니터링 없음이 가장 자주 나타나는 패턴입니다.

---

## 정리

TLS는 켜는 것만으로 끝나지 않습니다. AI가 생성한 HTTP 클라이언트 코드에서 `verify=False`, 오래된 TLS 버전 허용, 약한 암호군 설정을 확인하세요. 인증서 만료 모니터링을 추가하고, 내부 서비스 간 통신에도 TLS를 적용하는 것이 현대적인 보안 기준입니다. 다음 글에서는 웹 보안의 기초인 동일 출처 정책과 CORS를 바이브코딩 관점에서 다룹니다.

---

## 참고 자료

- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt 무료 인증서](https://letsencrypt.org/)
- [OWASP Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)
- [TLS 1.3 RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- [바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시](./03-cryptography-and-hash.md)
- **바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서 (현재 글)**
- 바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초
- 바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS
- 바이브코딩을 위한 정보 보안 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 정보 보안 기초 (8/10): 권한 최소화
- 바이브코딩을 위한 정보 보안 기초 (9/10): 로그와 감사
- 바이브코딩을 위한 정보 보안 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, 정보보안, TLS, HTTPS, 인증서, AI보안
