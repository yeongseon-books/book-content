---
series: computer-networks-101
episode: 6
title: "Computer Networks 101 (6/10): TLS 기초"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 네트워크
  - TLS
  - 인증서
  - 암호화
  - PKI
seo_description: TLS와 인증서, PKI가 HTTPS를 안전하게 만드는 구조를 설명합니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (6/10): TLS 기초

이 글은 Computer Networks 101 시리즈의 6번째 글입니다.


![Computer Networks 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/06/06-01-concept-at-a-glance.ko.png)
*Computer Networks 101 6장 흐름 개요*

## 먼저 던지는 질문

- TLS가 보장하는 세 가지는 무엇일까요?
- 핸드셰이크는 어떤 순서로 진행될까요?
- 인증서, CA, 체인, trust store는 어떤 관계일까요?

## 왜 중요한가

TLS를 머릿속에 그리지 못하면 인증서 만료 사고가 생겼을 때 손을 대기 어렵고, self-signed 인증서를 그냥 무시하는 위험한 코드도 쉽게 들어갑니다. mTLS, 서비스 메시, zero-trust 같은 현대 인프라는 TLS를 기본 전제로 삼습니다. "왜 안전한가"를 자기 언어로 설명하지 못하면 보안 설계는 금세 관성에 휩쓸립니다.

> TLS는 "이 채널이 안전하다"는 막연한 말이 아니라, "이 키가 정말 이 도메인 것이고 그 키로만 풀 수 있다"는 조합입니다.

## 핵심 그림

비대칭 합의로 대칭 세션 키를 만들고, 그 뒤부터는 그 키로 빠르게 데이터를 암호화합니다.

```text
TLS 1.3 핸드셰이크 (1-RTT):

클라이언트                                      서버
    │                                            │
    │─── ClientHello ───────────────────────────▶│
    │    (지원하는 cipher suite, key share)        │
    │                                            │
    │◀── ServerHello + EncryptedExtensions ──────│
    │    (선택한 cipher, key share, 인증서, 서명)   │
    │                                            │
    │─── Finished ──────────────────────────────▶│
    │    (핸드셰이크 검증 완료)                     │
    │                                            │
    │◀═══════ 암호화된 애플리케이션 데이터 ═══════▶│
    │         (대칭 키로 AEAD 암호화)              │
```

TLS 1.2에서는 2-RTT가 필요했지만, TLS 1.3은 키 교환과 인증서 전달을 하나의 왕복으로 합칩니다. 재접속 시에는 0-RTT도 가능합니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 대칭 암호 | 같은 키로 암호화와 복호화를 하는 방식 (AES-256-GCM) |
| 비대칭 암호 | 공개 키와 개인 키 쌍을 쓰는 방식 (RSA, ECDSA, Ed25519) |
| AEAD | 암호화와 무결성 검증을 함께 제공하는 방식 (AES-GCM, ChaCha20-Poly1305) |
| 인증서 | 공개 키와 도메인을 묶고 서명을 붙인 문서 (X.509) |
| CA | 인증서에 서명하는 신뢰 기관 (Certificate Authority) |
| 체인 | 서버 인증서에서 중간 CA, 루트 CA로 이어지는 검증 경로 |
| trust store | 클라이언트가 신뢰하는 루트 CA 목록 |
| SAN | Subject Alternative Name — 인증서가 유효한 도메인 목록 |
| PFS | Perfect Forward Secrecy — 키가 유출되어도 과거 세션은 안전 |
| OCSP | 인증서 폐기 여부를 실시간으로 확인하는 프로토콜 |

## Before / After

**Before — "https면 그냥 안전하다"**

```text
브라우저 자물쇠가 보이면 끝.
```

**After — "TLS는 키, 신원, 무결성을 함께 묶는다"**

```text
- 누구의 키인가?            → certificate signed by a CA
- 누가 복호화할 수 있는가? → symmetric session key
- 중간에 변조되지 않았는가? → AEAD / MAC
```

## 단계별로 따라하기

### 1단계: 인증서 들여다보기

```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
# subject= /CN=*.example.com
# issuer = /CN=DigiCert Global G2
# notBefore=Jan  1 00:00:00 2024 GMT
# notAfter =Jan  1 23:59:59 2025 GMT
# X509v3 Subject Alternative Name:
#     DNS:*.example.com, DNS:example.com
```

SAN(Subject Alternative Name)에 있는 도메인만 이 인증서로 보호됩니다. 와일드카드(`*.example.com`)는 서브도메인 한 단계만 커버합니다.

### 2단계: 인증서 체인 확인하기

```bash
openssl s_client -showcerts -connect example.com:443 -servername example.com </dev/null 2>/dev/null
# --- Certificate chain
#  0 s:CN = *.example.com
#    i:C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
#  1 s:CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
#    i:C = US, O = DigiCert Inc, CN = DigiCert Global Root G2
```

```text
검증 경로:
┌────────────────────────┐
│ DigiCert Global Root G2 │ ← trust store에 있음 (자체 서명)
└────────────┬───────────┘
             │ 서명
┌────────────▼────────────────────────────────────┐
│ DigiCert Global G2 TLS RSA SHA256 2020 CA1      │ ← 중간 CA
└────────────┬────────────────────────────────────┘
             │ 서명
┌────────────▼───────────┐
│ *.example.com           │ ← 서버 인증서 (leaf)
└────────────────────────┘
```

브라우저는 이 체인을 루트 CA까지 따라 올라가며 서명을 검증합니다. 중간 인증서가 누락되면 일부 클라이언트에서 검증이 실패합니다.

### 3단계: TLS 핸드셰이크 상세 관찰

```bash
openssl s_client -connect example.com:443 -servername example.com -msg 2>&1 | head -50
# >>> TLS 1.3, Handshake [length 0200], ClientHello
# <<< TLS 1.3, Handshake [length 0080], ServerHello
# <<< TLS 1.3, Handshake [length 0300], EncryptedExtensions
# <<< TLS 1.3, Handshake [length 0800], Certificate
# <<< TLS 1.3, Handshake [length 0100], CertificateVerify
# <<< TLS 1.3, Handshake [length 0040], Finished
# >>> TLS 1.3, Handshake [length 0040], Finished
```

```bash
# 협상된 cipher suite 확인
echo | openssl s_client -connect example.com:443 2>/dev/null | grep "Cipher"
# New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
```

### 4단계: Python에서 안전하게 호출하기

```python
import ssl, socket

ctx = ssl.create_default_context()   # uses the OS trust store
with socket.create_connection(('example.com', 443)) as s:
    with ctx.wrap_socket(s, server_hostname='example.com') as ts:
        print(ts.version())          # TLSv1.3
        print(ts.cipher())           # ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
        cert = ts.getpeercert()
        print(cert['subject'])
        print(cert['notAfter'])
        # SAN 확인
        sans = [v for t, v in cert.get('subjectAltName', []) if t == 'DNS']
        print(f"SAN domains: {sans}")
```

```python
# 위험한 코드 — 운영에서 절대 사용 금지
ctx_insecure = ssl.create_default_context()
ctx_insecure.check_hostname = False
ctx_insecure.verify_mode = ssl.CERT_NONE  # 모든 인증서를 수락 → MITM 가능
```

### 5단계: self-signed 인증서 만들기

```bash
# RSA 2048 키 + self-signed 인증서 (1일 유효)
openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -subj "/CN=localhost" -keyout key.pem -out cert.pem \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

# 인증서 내용 확인
openssl x509 -in cert.pem -noout -text | grep -A2 "Subject Alternative"
```

```python
# Flask + TLS
from flask import Flask
app = Flask(__name__)

@app.get('/')
def home(): return 'hello'

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), port=8443)
```

```bash
# 검증 실패 (self-signed이므로)
curl https://localhost:8443/
# curl: (60) SSL certificate problem: self-signed certificate

# 명시적으로 CA 인증서 지정하면 성공
curl --cacert cert.pem https://localhost:8443/
# hello

# -k로 우회 (학습용만)
curl -k https://localhost:8443/
```

### 6단계: 만료와 위장 사례 보기

```bash
curl -v https://expired.badssl.com/ 2>&1 | grep "SSL certificate"
# * SSL certificate problem: certificate has expired

curl -v https://wrong.host.badssl.com/ 2>&1 | grep "SSL certificate"
# * SSL certificate problem: hostname mismatch

curl -v https://untrusted-root.badssl.com/ 2>&1 | grep "SSL certificate"
# * SSL certificate problem: unable to get local issuer certificate
```

어느 검증 단계가 실패했는지 메시지로 바로 확인할 수 있습니다.

### 7단계: 인증서 만료 모니터링 스크립트

```python
import ssl, socket
from datetime import datetime

def check_cert_expiry(host: str, port: int = 443) -> int:
    """인증서 만료까지 남은 일수 반환"""
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=5) as s:
        with ctx.wrap_socket(s, server_hostname=host) as ts:
            cert = ts.getpeercert()
            expire_str = cert['notAfter']  # 'Jan  1 23:59:59 2025 GMT'
            expire_dt = datetime.strptime(expire_str, '%b %d %H:%M:%S %Y %Z')
            return (expire_dt - datetime.utcnow()).days

# 여러 도메인 점검
domains = ['example.com', 'github.com', 'google.com']
for domain in domains:
    days = check_cert_expiry(domain)
    status = "WARNING" if days < 30 else "OK"
    print(f"{domain:20s}: {days:4d}일 남음 [{status}]")
```

이 스크립트를 cron으로 매일 실행하고, 30일 미만일 때 Slack이나 PagerDuty로 알림을 보내면 인증서 만료 사고를 예방할 수 있습니다. Let's Encrypt의 자동 갱신도 실패할 수 있으므로, 갱신 성공 여부를 별도로 모니터링하는 것이 좋습니다.

```bash
# CLI로도 빠르게 확인 가능
echo | openssl s_client -connect example.com:443 2>/dev/null | \
  openssl x509 -noout -enddate
# notAfter=Jan  1 23:59:59 2025 GMT
```

## 이 코드에서 먼저 볼 점

- trust store는 운영 체제나 브라우저가 신뢰하는 루트 CA 목록입니다. Linux에서는 `/etc/ssl/certs/`, macOS에서는 Keychain, Python에서는 `certifi` 패키지가 대표적입니다.
- 인증서는 키, 도메인, 만료일, 서명을 함께 담는 문서입니다.
- self-signed 인증서는 학습용일 뿐이고, 운영에서는 공인 CA를 사용합니다.
- TLS 버전과 cipher 선택은 보안 수준에 직접 영향을 줍니다.
- PFS(Perfect Forward Secrecy) 덕분에 서버 키가 유출되어도 과거 트래픽은 복호화할 수 없습니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `verify=False`나 `-k`를 운영에서 사용 | MITM 공격에 노출 | 신뢰할 수 있는 CA 인증서를 사용한다 |
| 인증서 만료 모니터링이 없음 | 갑작스러운 장애 | 만료 30일 전 알림을 자동화한다 |
| 중간 인증서 누락 | 일부 클라이언트 검증 실패 | full chain을 배포한다 |
| 약한 cipher나 오래된 TLS 허용 | 알려진 공격에 노출 | TLS 1.2+와 안전한 cipher만 사용한다 |
| SAN에 필요한 도메인이 없음 | 일부 브라우저가 차단 | 필요한 도메인을 SAN에 모두 넣는다 |

## TLS 버전별 비교

| 특성 | TLS 1.2 | TLS 1.3 |
| --- | --- | --- |
| 핸드셰이크 RTT | 2-RTT | 1-RTT (재접속 시 0-RTT) |
| 키 교환 | RSA, DHE, ECDHE | ECDHE, X25519만 |
| cipher suite | 수백 개 조합 가능 | 5개로 축소 |
| PFS | 선택적 (ECDHE 사용 시) | 필수 |
| 0-RTT | 불가 | 가능 (replay 위험 있음) |
| 암호화 시작 시점 | Finished 이후 | ServerHello 직후 |

```bash
# 서버가 지원하는 TLS 버전 확인
nmap --script ssl-enum-ciphers -p 443 example.com | grep "TLSv"
# |   TLSv1.2:
# |   TLSv1.3:

# TLS 1.2만 강제 연결 시도
openssl s_client -connect example.com:443 -tls1_2
# TLS 1.3만 강제
openssl s_client -connect example.com:443 -tls1_3
```

### Certificate Transparency (CT)

인증서를 부정하게 발급한 것을 발견하는 방법이 Certificate Transparency입니다. 모든공인 CA는 발급한 인증서를 공개 CT 로그에 등록해야 합니다.

```bash
# CT 로그에서 특정 도메인의 인증서 이력 검색
# https://crt.sh/?q=example.com

# 인증서의 SCT(Signed Certificate Timestamp) 확인
echo | openssl s_client -connect example.com:443 2>/dev/null | \
  openssl x509 -noout -ext ct_precert_scts
```

이 방식으로 누군가 내 도메인의 인증서를 부정 발급하면 CT 로그에서 발견할 수 있습니다.

### OCSP Stapling

인증서가 폐기되었는지 확인하는 전통적 방법은 클라이언트가 CA의 OCSP 서버에 직접 물어보는 것입니다. 하지만 이 방식은 지연을 유발하고 프라이버시 문제가 있습니다.

```text
전통 OCSP:
  클라이언트 ─── TLS 연결 ─── 서버
  클라이언트 ─── OCSP 질의 ─── CA   ← 추가 지연 + 프라이버시 노출

OCSP Stapling:
  서버가 주기적으로 CA에서 OCSP 응답을 받아 두고,
  TLS 핸드셰이크 시 인증서와 함께 전달
  → 클라이언트는 CA에 직접 물어볼 필요 없음
```

```bash
# OCSP stapling 지원 여부 확인
echo | openssl s_client -connect example.com:443 -status 2>/dev/null | \
  grep "OCSP Response Status"
# OCSP Response Status: successful (0x0)
```

### TLS 진단 플로우차트

TLS 연결 실패 시 단계별로 원인을 좌혀 나가는 방법입니다.

```text
문제: HTTPS 연결 실패
│
├─ TCP 연결은 되는가? (telnet host 443)
│   ├─ No  → 네트워크/방화벽 문제 (이전 글 참조)
│   └─ Yes → 다음 단계
│
├─ ClientHello 응답이 오는가?
│   ├─ No  → 서버가 TLS를 지원하지 않거나 포트 불일치
│   └─ Yes → 다음 단계
│
├─ 인증서 검증 성공?
│   ├─ expired     → 인증서 갱신 필요
│   ├─ wrong host  → SAN 불일치, SNI 설정 확인
│   ├─ untrusted   → 중간 인증서 누락 또는 trust store 문제
│   └─ Yes → 다음 단계
│
└─ cipher suite 협상 성공?
    ├─ No  → 서버/클라이언트의 지원 cipher 불일치
    └─ Yes → 애플리케이션 레벨 문제
```

### Wireshark로 TLS 핸드셰이크 분석

```bash
# TLS 키 로그 생성 (비밀 키 로그 — Wireshark에서 복호화용)
SSLKEYLOGFILE=/tmp/tls-keys.log curl https://example.com

# Wireshark 설정:
# Edit → Preferences → Protocols → TLS
# (Pre)-Master-Secret log filename: /tmp/tls-keys.log
```

Wireshark에서 TLS 핸드셰이크를 보면 다음 메시지를 확인할 수 있습니다.

```text
1. Client Hello
   - Version: TLS 1.3 (or TLS 1.2 in record layer)
   - Cipher Suites: TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256, ...
   - Extensions: server_name=example.com, supported_versions, key_share

2. Server Hello
   - Cipher Suite: TLS_AES_256_GCM_SHA384
   - Key Share: x25519

3. Change Cipher Spec (호환성용, TLS 1.3에서는 실제 의미 없음)

4. Application Data (암호화된 데이터 시작)
```

`SSLKEYLOGFILE`을 설정하면 암호화된 Application Data도 복호화해서 HTTP 메시지를 볼 수 있습니다. 운영 환경에서는 이 파일을 절대 남겨 두지 않습니다.

### 암호화 알고리즘 선택 가이드

TLS 1.3에서 사용 가능한 cipher suite는 5개로 축소되었습니다.

| Cipher Suite | 키 교환 | 암호화 | 해시 |
| --- | --- | --- | --- |
| TLS_AES_256_GCM_SHA384 | ECDHE/X25519 | AES-256-GCM | SHA-384 |
| TLS_AES_128_GCM_SHA256 | ECDHE/X25519 | AES-128-GCM | SHA-256 |
| TLS_CHACHA20_POLY1305_SHA256 | ECDHE/X25519 | ChaCha20-Poly1305 | SHA-256 |
| TLS_AES_128_CCM_SHA256 | ECDHE/X25519 | AES-128-CCM | SHA-256 |
| TLS_AES_128_CCM_8_SHA256 | ECDHE/X25519 | AES-128-CCM-8 | SHA-256 |

선택 기준:
- 서버에 AES-NI 하드웨어가 있으면 AES-GCM이 빠릅니다
- 모바일/IoT처럼 하드웨어 가속이 없으면 ChaCha20-Poly1305가 더 효율적입니다
- 모든 suite가 PFS를 강제하므로 RSA 키 교환은 더 이상 사용되지 않습니다

```python
# Python에서 특정 cipher 강제
import ssl

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.set_ciphers('TLS_AES_256_GCM_SHA384')  # TLS 1.3 cipher
ctx.minimum_version = ssl.TLSVersion.TLSv1_3
ctx.load_default_certs()
```

## mTLS: 양방향 인증

일반 TLS는 서버만 인증합니다. mTLS(mutual TLS)는 클라이언트도 인증서를 제출합니다.

```text
일반 TLS:
  클라이언트 ─────────────── 서버 인증서 검증 ───── 서버
  (신원 불명)                                      (신원 확인됨)

mTLS:
  클라이언트 ─── 서버 인증서 검증 + 클라이언트 인증서 제출 ─── 서버
  (신원 확인됨)                                              (신원 확인됨)
```

```python
# mTLS 클라이언트 예시
import ssl, socket

ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ctx.load_cert_chain(certfile='client.pem', keyfile='client-key.pem')

with socket.create_connection(('api.internal.com', 443)) as s:
    with ctx.wrap_socket(s, server_hostname='api.internal.com') as ts:
        ts.sendall(b'GET / HTTP/1.1\r\nHost: api.internal.com\r\n\r\n')
        print(ts.recv(1024).decode())
```

Kubernetes 서비스 메시(Istio, Linkerd)는 Pod 간 통신에 자동으로 mTLS를 적용합니다. 애플리케이션 코드는 TLS를 모른 채 평문으로 통신하고, sidecar proxy가 암호화를 처리합니다.

## 실무에서는 이렇게 보입니다

- 웹과 모바일은 Let's Encrypt와 자동 갱신을 널리 사용합니다.
- 마이크로서비스는 mTLS로 서비스 간 신원을 검증합니다.
- 메시지 큐와 DB 클라이언트도 TLS 옵션을 켜는 것이 기본입니다.
- VPN과 QUIC에서도 TLS는 핵심 구성 요소입니다.
- IoT는 제조 단계에서 클라이언트 인증서를 발급하기도 합니다.

### Let's Encrypt 자동 갱신 구성

```bash
# certbot으로 인증서 발급
sudo certbot certonly --nginx -d example.com -d www.example.com

# 자동 갱신 테스트
sudo certbot renew --dry-run

# cron으로 자동 갱신 (보통 설치 시 자동 등록됨)
# 0 0,12 * * * /usr/bin/certbot renew --quiet
```

```bash
# Nginx TLS 설정 (Mozilla 권장)
ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
ssl_protocols       TLSv1.2 TLSv1.3;
ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache   shared:SSL:10m;
```

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 TLS를 단순한 암호화 스위치가 아니라 키 관리 시스템으로 봅니다. 인증서 갱신 주기, 개인 키 보호, 어떤 루트 CA를 신뢰할지, mTLS 정책을 어떻게 배포할지 같은 운영 문제가 알고리즘 선택만큼 중요하다는 것을 잘 압니다.

또한 "암호화했으니 안전하다"는 단순한 결론을 경계합니다. 어떤 키가 유출되면 누가 무엇을 볼 수 있는지, 메타데이터는 어디까지 노출되는지까지 함께 그려 봅니다.

TLS 장애 진단에서 가장 흔한 시나리오 세 가지는 다음과 같습니다.

1. **인증서 만료**: 자동 갱신 실패 → 서비스 전체 접속 불가. 해결: 만료 30일 전 알림 + 갱신 실패 시 별도 알림
2. **중간 인증서 누락**: 서버에서 leaf만 전송 → Android/Java 클라이언트 실패 (macOS/iOS는 AIA로 자동 보완). 해결: `fullchain.pem` 배포
3. **SNI 미설정**: 하나의 IP에 여러 도메인을 호스팅할 때 ClientHello에 hostname이 빠지면 잘못된 인증서 반환. 해결: `server_hostname` 파라미터 확인

## 체크리스트

- [ ] TLS의 세 가지 보장(기밀성, 무결성, 신원 확인)을 설명할 수 있다
- [ ] 인증서, CA, 체인, trust store의 관계를 안다
- [ ] TLS 1.3 핸드셰이크의 큰 흐름을 그릴 수 있다
- [ ] 운영에서 `verify=False`를 쓰지 않는다
- [ ] 인증서 만료를 자동 모니터링한다
- [ ] PFS의 의미를 한 문장으로 설명할 수 있다
- [ ] mTLS가 필요한 상황을 식별할 수 있다

## 연습 문제

1. 좋아하는 사이트의 인증서를 `openssl`로 확인하고 issuer, 만료일, SAN 목록을 적어 보세요.
2. self-signed 인증서로 로컬 HTTPS 서버를 띄운 뒤, Python `ssl` 모듈로 성공하는 호출과 실패하는 호출을 각각 만들어 보세요.
3. "zero-trust 인프라에서 mTLS가 왜 중요한가"를 한 단락으로 설명해 보세요.
4. `openssl s_client`로 TLS 1.2와 1.3 연결을 각각 시도하고, 협상된 cipher suite의 차이를 비교해 보세요.

## 정리와 다음 글

TLS는 비대칭 암호로 신원 확인과 키 합의를 하고, 대칭 암호로 빠른 데이터 암호화를 하며, AEAD로 무결성을 보장합니다. 인증서와 PKI는 그 키가 정말 해당 도메인의 것임을 증명합니다. 이 그림이 잡히면 HTTPS 관련 사고가 한 자리에서 정리되기 시작합니다.

다음 글에서는 이 TLS로 보호된 패킷이 인터넷에서 어떻게 이동하는지, 라우팅과 NAT를 다룹니다.

## 처음 질문으로 돌아가기

- **TLS가 보장하는 세 가지는 무엇일까요?**
  - 기밀성(session key로 데이터 암호화), 무결성(AEAD로 변조 감지), 신원 확인(CA 서명 인증서로 서버가 진짜인지 검증)입니다.
- **핸드셰이크는 어떤 순서로 진행될까요?**
  - TLS 1.3 기준: ClientHello(지원 cipher + key share) → ServerHello + 인증서 + 서명 → Finished. 1-RTT로 완료되며, 이후 모든 데이터는 합의된 대칭 키로 암호화됩니다.
- **인증서, CA, 체인, trust store는 어떤 관계일까요?**
  - 서버 인증서(leaf)는 중간 CA가 서명하고, 중간 CA는 루트 CA가 서명합니다. 클라이언트의 trust store에 루트 CA가 있으면 체인 전체를 신뢰합니다. 중간 인증서가 빠지면 체인이 끊겨 검증이 실패합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP와 UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- [Computer Networks 101 (5/10): HTTP와 HTTPS](./05-http-and-https.md)
- **TLS 기초 (현재 글)**
- 라우팅과 NAT (예정)
- Load Balancer (예정)
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)

<!-- toc:end -->

## 참고 자료

- [RFC 8446 — TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Bulletproof TLS — Ivan Ristic](https://www.feistyduck.com/books/bulletproof-tls-and-pki/)
- [RFC 5280 — PKIX Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280)
- [시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, TLS, 인증서, 암호화, PKI
