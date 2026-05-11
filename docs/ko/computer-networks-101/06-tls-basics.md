---
series: computer-networks-101
episode: 6
title: TLS 기초
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: TLS handshake가 어떻게 기밀성·무결성·신원을 보장하는지, 인증서와 PKI의 역할을 한 번에 정리합니다.
last_reviewed: '2026-05-04'
---

# TLS 기초

> Computer Networks 101 시리즈 (6/10)


## 이 글에서 다룰 문제

TLS를 모르면 인증서 만료 사고에 손을 대지 못하고, 자기서명을 그냥 무시하는 위험한 코드가 들어갑니다. 또 mTLS·서비스 메시·zero-trust 같은 현대 인프라는 TLS가 기본 가정입니다. "왜 안전한가?"를 자기 언어로 설명하지 못하면 보안 설계는 의식 없이 흐르게 됩니다.

> TLS는 "이 채널이 안전하다"가 아니라 "이 키가 진짜 이 도메인 것이고, 그 키로만 풀 수 있다"의 조합입니다.

## 전체 흐름
```text
Client                          Server
  --- ClientHello (지원 cipher) -->
  <-- ServerHello + Certificate ---
  --- key share / Finished ------->
  <-- Finished --------------------
  ===== 대칭 키로 암호화된 application data =====
```

비대칭 키로 합의된 비밀에서 대칭 세션 키를 만들고, 이후 데이터는 그 키로 빠르게 암호화합니다.

## Before / After

**Before — "https는 그냥 안전":**

```text
자물쇠 아이콘이 있으면 안전 — 끝.
```

**After — "TLS는 키 + 신원 + 무결성":**

```text
- 누구의 키인가? → CA가 보증한 인증서
- 누구만 풀 수 있는가? → 대칭 세션 키
- 변조되지 않았나? → AEAD/MAC
이 셋이 동시에 깨지지 않는 한 안전
```

## 단계별로 따라하기

### 1단계: 인증서 보기

```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
# subject= /CN=*.example.com
# issuer = /CN=DigiCert Global G2
# notBefore=...  notAfter=...
```

### 2단계: 체인 검증

```bash
openssl s_client -showcerts -connect example.com:443 -servername example.com </dev/null
# 체인의 모든 인증서가 출력됨
```

브라우저는 이 체인을 root CA까지 따라가며 서명을 검증합니다.

### 3단계: Python에서 안전한 호출

```python
import ssl, socket

ctx = ssl.create_default_context()   # OS의 신뢰 저장소 사용
with socket.create_connection(('example.com', 443)) as s:
    with ctx.wrap_socket(s, server_hostname='example.com') as ts:
        print(ts.version())          # TLSv1.3
        print(ts.getpeercert()['subject'])
```

### 4단계: 자기서명 인증서 만들기

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -subj "/CN=localhost" -keyout key.pem -out cert.pem
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
curl -k https://localhost:8443/    # -k는 자기서명 허용 (학습용)
```

### 5단계: 만료/위장 사례 보기

```bash
curl -v https://expired.badssl.com/        # 만료
curl -v https://wrong.host.badssl.com/     # 도메인 불일치
curl -v https://untrusted-root.badssl.com/ # 신뢰 안 되는 root
```

각 사례에서 정확히 무엇이 검증에 실패했는지 메시지로 보입니다.

## 이 코드에서 주목할 점

- 신뢰 저장소(trust store)는 OS/브라우저가 가진 root CA 목록
- 인증서는 "키 + 도메인 + 만료 + 서명"의 묶음
- 자기서명은 학습용으로만, 운영에서는 Let's Encrypt 등을 사용
- TLS 버전과 cipher 선택이 보안의 큰 부분

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `verify=False`/`-k` 운영 사용 | MITM 사고 노출 | 신뢰된 CA 인증서 사용 |
| 인증서 만료 모니터링 없음 | 갑작스러운 장애 | 만료 30일 전 알림 자동화 |
| 중간 인증서 누락 | 일부 클라이언트가 검증 실패 | full chain 배포 |
| 약한 cipher/구버전 TLS 허용 | 알려진 공격 노출 | TLS 1.2+ + 안전한 cipher만 |
| 도메인과 SAN 불일치 | 일부 브라우저에서 차단 | SAN에 모든 도메인 포함 |

## 실무에서는 이렇게 쓰입니다

- 웹/모바일: Let's Encrypt + 자동 갱신
- 마이크로서비스: mTLS로 서비스 간 신원 검증
- 메시지 큐/DB 클라이언트: TLS 옵션 활성화
- VPN/QUIC: TLS가 핵심 구성 요소
- IoT: 공장 출하 시 클라이언트 인증서 발급

## 체크리스트

- [ ] TLS 3가지 보장(기밀성/무결성/신원)을 안다
- [ ] 인증서, CA, 체인, 신뢰 저장소를 안다
- [ ] handshake의 큰 단계를 그릴 수 있다
- [ ] 운영에서 `verify=False`를 절대 쓰지 않는다
- [ ] 인증서 만료를 자동 모니터링한다

## 정리 및 다음 단계

TLS는 비대칭 키로 신원과 키 합의를, 대칭 키로 빠른 암호화를, AEAD로 무결성을 보장하는 조합입니다. 인증서와 PKI는 "이 키가 진짜 이 도메인 것"임을 보증합니다. 이 그림이 잡히면 모든 HTTPS 사고가 같은 책장 위에서 보입니다.

다음 글에서는 TLS가 보호한 패킷이 인터넷을 어떻게 흘러가는지 — 라우팅과 NAT로 넘어갑니다.

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
- [IP와 subnet](./02-ip-and-subnet.md)
- [TCP와 UDP](./03-tcp-and-udp.md)
- [DNS](./04-dns.md)
- [HTTP와 HTTPS](./05-http-and-https.md)
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
