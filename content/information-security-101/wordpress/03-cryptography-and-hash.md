---
series: information-security-101
episode: 3
title: "바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 정보보안
  - 암호화
  - 해시
  - AES
  - AI보안
language: ko
---

# 바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시

이 글은 **바이브코딩을 위한 정보 보안 기초** 시리즈의 3편입니다. AI가 만들어주는 코드에는 보안 취약점이 숨어 있을 수 있습니다. 이번에는 암호화와 해시에서 AI가 자주 선택하는 잘못된 조합을 다룹니다.

---

AI에게 "데이터를 암호화해서 저장해줘"라고 하면 코드가 나옵니다. 그런데 그 코드가 AES-ECB 모드를 쓰거나, 해시로 비밀번호를 저장하면서 SHA-256을 선택하거나, 암호화와 무결성 검증을 따로 구현했는데 둘 사이에 구멍이 있는 경우가 있습니다. 암호화를 "켰다"는 것과 "제대로 했다"는 것은 다른 이야기입니다.

> "암호화와 해시는 목적이 다릅니다. 암호화는 복호화를 전제로 데이터를 숨기는 것이고, 해시는 원본을 복원할 수 없는 방식으로 데이터를 변환하는 것입니다. AI가 둘을 잘못 골라주면 안전해 보이지만 뚫리는 코드가 만들어집니다."

## 이 글에서 다룰 질문들

- 암호화와 해시는 어떻게 다르고 언제 각각을 써야 할까요?
- AES-ECB가 왜 위험하고 AES-GCM을 써야 하는 이유는 무엇일까요?
- 비밀번호 저장에 SHA-256을 쓰면 왜 문제가 생길까요?
- HMAC은 해시와 무엇이 다를까요?
- AI가 암호화 코드를 만들 때 자주 빠뜨리는 것은 무엇일까요?

---

## 바이브코딩 관점: AI가 암호화 코드에서 자주 고르는 잘못된 선택

AI는 암호화 코드를 생성할 때 "작동하는" 알고리즘을 선택합니다. 하지만 보안적으로 올바른 선택을 하지 않을 수 있습니다.

### Before: AI가 생성한 암호화 코드의 전형적인 문제

```python
# AI 생성 코드 — 작동하지만 취약한 패턴들
from Crypto.Cipher import AES
import hashlib

# 문제 1: AES-ECB 모드 — 같은 블록이 같은 암호문 생성 → 패턴 노출
def encrypt_ecb(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(data)

# 문제 2: 비밀번호 해시에 SHA-256 — 빠른 해시라서 GPU 크래킹 가능
def hash_password_wrong(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 문제 3: 암호화만 하고 무결성 검증 없음 — 변조 감지 불가
def encrypt_without_integrity(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)
```

### After: 올바른 암호화 패턴

```python
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import bcrypt
import os

# 기밀성 + 무결성: AES-GCM — 암호화와 무결성 검증을 한 번에
def encrypt_aes_gcm(data: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce, ciphertext, tag  # nonce, 암호문, 인증 태그

def decrypt_aes_gcm(nonce: bytes, ciphertext: bytes, tag: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)  # 변조 시 예외 발생

# 비밀번호: 의도적으로 느린 해시 — bcrypt
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
```

---

## 도구 선택 가이드: 언제 무엇을 써야 하나요?

| 상황 | 올바른 도구 | 잘못된 선택 | 이유 |
| --- | --- | --- | --- |
| 비밀번호 저장 | bcrypt, argon2 | MD5, SHA-256, AES | 복호화 불필요, 느린 해시 필요 |
| 데이터 암호화 (복호화 필요) | AES-GCM | AES-ECB, AES-CBC 단독 | ECB는 패턴 노출, CBC는 무결성 없음 |
| 데이터 무결성 확인 | HMAC-SHA256 | 단순 체크섬, CRC | HMAC은 비밀키 없이 위조 불가 |
| 디지털 서명 | RSA-OAEP, ECDSA | RSA-PKCS1v1.5 | PKCS1v1.5는 패딩 오라클 공격 취약 |

---

## AES 모드 비교: ECB vs GCM

AI가 가장 자주 잘못 선택하는 부분이 AES의 운용 모드입니다.

```python
# ECB 모드의 문제 — 같은 입력이 같은 출력을 만든다
# 패턴이 암호문에 그대로 남는다
# 예: 같은 금액이 두 번 나오면 암호문도 두 번 같은 패턴으로 나온다

# 비유: 우편번호처럼 특정 패턴이 노출되면
# 공격자가 "이 패턴은 1만원이다"를 학습할 수 있다

# GCM 모드의 장점
# 1. 같은 입력도 nonce 덕분에 매번 다른 암호문
# 2. 인증 태그로 변조 감지 가능
# 3. 복호화 시 태그 검증 실패 → 즉시 오류
key = get_random_bytes(32)  # AES-256
nonce, ciphertext, tag = encrypt_aes_gcm(b"amount: 10000", key)
plaintext = decrypt_aes_gcm(nonce, ciphertext, tag, key)
```

---

## HMAC: 해시와 무엇이 다른가요?

```python
import hmac
import hashlib

# 단순 해시: 비밀키 없음 → 누구나 같은 해시 생성 가능
def simple_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

# HMAC: 비밀키 포함 → 키 없이는 같은 태그 생성 불가
def create_hmac(data: str, secret_key: bytes) -> str:
    return hmac.new(secret_key, data.encode(), hashlib.sha256).hexdigest()

# 활용: API 요청 서명, 쿠키 무결성 검증, 웹훅 검증
secret = os.environ["WEBHOOK_SECRET"].encode()
payload = '{"event": "payment", "amount": 10000}'
signature = create_hmac(payload, secret)

# 수신 측 검증
received_signature = request.headers.get("X-Signature")
if not hmac.compare_digest(signature, received_signature):
    raise ValueError("서명 검증 실패 — 변조 의심")
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| AES-ECB 사용 | 패턴이 암호문에 그대로 남는다 | AES-GCM 또는 AES-CBC + HMAC |
| SHA-256으로 비밀번호 해시 | 빠른 해시 → GPU 크래킹 가능 | bcrypt(cost=12) 또는 argon2 |
| 암호화만 하고 무결성 검증 없음 | 변조된 암호문을 그대로 복호화 | AES-GCM의 인증 태그 사용 |
| 키를 코드에 하드코딩 | 코드 유출 시 모든 데이터 복호화 가능 | 환경 변수 또는 KMS 사용 |

---

## AI 팁: AI에게 암호화 코드를 올바르게 요청하는 법

1. **모드 명시**: "AES 암호화"가 아니라 "AES-GCM 암호화"로 요청하세요.
2. **무결성 포함 요청**: "암호화와 무결성 검증을 함께 해주세요"라고 요청하면 AES-GCM이나 HMAC이 포함됩니다.
3. **비밀번호 해시 명시**: "비밀번호 저장에 bcrypt를 써주세요"라고 명시하세요.
4. **키 관리 확인**: AI가 코드에 키를 하드코딩했다면 환경 변수로 옮겨달라고 요청하세요.

---

## 실전 체크리스트

- [ ] 비밀번호 저장에 bcrypt 또는 argon2를 사용하고 있다 (SHA-256 아님)
- [ ] 데이터 암호화에 AES-GCM을 사용하고 있다 (ECB 아님)
- [ ] API 서명에 HMAC을 사용하고 있다 (단순 해시 아님)
- [ ] 암호화 키가 환경 변수 또는 KMS에 저장되어 있다
- [ ] 복호화 시 인증 태그 검증이 포함되어 있다
- [ ] nonce/IV가 매번 다르게 생성된다 (고정값 아님)

---

## 처음 질문으로 돌아가기

- **암호화와 해시는 어떻게 다르고 언제 각각을 써야 할까요?**
  암호화는 복호화를 전제로 합니다. 데이터를 보호하면서도 나중에 원본을 꺼내야 할 때 씁니다. 해시는 단방향입니다. 비밀번호처럼 원본 복원이 불필요하고 "같은 입력인지 확인"만 필요할 때 씁니다.

- **AES-ECB가 왜 위험하고 AES-GCM을 써야 하는 이유는 무엇일까요?**
  ECB는 같은 입력 블록이 같은 암호문 블록을 만듭니다. 패턴이 그대로 노출됩니다. GCM은 nonce 덕분에 같은 입력도 매번 다른 암호문이 나오고, 인증 태그로 변조까지 감지합니다.

- **비밀번호 저장에 SHA-256을 쓰면 왜 문제가 생길까요?**
  SHA-256은 빠른 해시 함수입니다. 현대 GPU는 초당 수십억 번의 SHA-256을 계산할 수 있어서 레인보우 테이블이나 브루트포스 공격에 취약합니다. bcrypt처럼 의도적으로 느린 함수가 비밀번호 저장에 맞습니다.

---

## 정리

암호화와 해시는 목적이 다릅니다. AI가 생성한 암호화 코드에서 AES 모드, 비밀번호 해시 함수, 무결성 검증 여부를 먼저 확인하세요. AES-GCM, bcrypt, HMAC 세 가지 키워드를 기억하면 AI 생성 코드의 암호화 품질을 빠르게 점검할 수 있습니다. 다음 글에서는 TLS와 인증서를 바이브코딩 관점에서 다룹니다.

---

## 참고 자료

- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST 암호화 알고리즘 가이드라인](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)
- [cryptography.io 라이브러리 문서](https://cryptography.io/en/latest/)
- [bcrypt 설계 원리](https://www.usenix.org/legacy/events/usenix99/provos/provos.pdf)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- **바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시 (현재 글)**
- 바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서
- 바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초
- 바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS
- 바이브코딩을 위한 정보 보안 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 정보 보안 기초 (8/10): 권한 최소화
- 바이브코딩을 위한 정보 보안 기초 (9/10): 로그와 감사
- 바이브코딩을 위한 정보 보안 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, 정보보안, 암호화, 해시, AES, AI보안
