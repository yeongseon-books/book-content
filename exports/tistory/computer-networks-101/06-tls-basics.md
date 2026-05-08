
# TLS 기초

> Computer Networks 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: HTTPS의 "S"는 어떻게 도청·변조·위장 세 가지를 동시에 막을 수 있을까요?

> TLS는 세 가지 기술을 한 박자에 합칩니다. 비대칭 키로 신원과 키 합의를, 대칭 키로 빠른 암호화를, MAC/AEAD로 무결성을 보장합니다. 인증서와 PKI(공개키 인프라)는 "이 키가 정말 이 도메인의 키인가?"를 보장합니다. 이 그림이 머릿속에 있으면 인증서 만료, 자기서명, MITM이 모두 같은 그림 위의 사고로 보입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- TLS가 보장하는 3가지(기밀성, 무결성, 신원)
- handshake 흐름(client hello → server hello → key exchange → finished)
- 인증서, CA, 체인, 신뢰 저장소
- TLS 1.2와 1.3의 차이

## 왜 중요한가

TLS를 모르면 인증서 만료 사고에 손을 대지 못하고, 자기서명을 그냥 무시하는 위험한 코드가 들어갑니다. 또 mTLS·서비스 메시·zero-trust 같은 현대 인프라는 TLS가 기본 가정입니다. "왜 안전한가?"를 자기 언어로 설명하지 못하면 보안 설계는 의식 없이 흐르게 됩니다.

> TLS는 "이 채널이 안전하다"가 아니라 "이 키가 진짜 이 도메인 것이고, 그 키로만 풀 수 있다"의 조합입니다.

## 개념 한눈에 보기

```text
Client                          Server
  --- ClientHello (지원 cipher) -->
  <-- ServerHello + Certificate ---
  --- key share / Finished ------->
  <-- Finished --------------------
  ===== 대칭 키로 암호화된 application data =====
```

비대칭 키로 합의된 비밀에서 대칭 세션 키를 만들고, 이후 데이터는 그 키로 빠르게 암호화합니다.

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 대칭 키 암호 | 같은 키로 암복호(예: AES) |
| 비대칭 키 암호 | 공개키/개인키 쌍(예: RSA, ECDSA) |
| AEAD | 암호화 + 무결성을 한 번에(예: AES-GCM, ChaCha20-Poly1305) |
| 인증서(certificate) | 공개키 + 도메인 + 서명을 묶은 문서 |
| CA | 인증서를 서명해 주는 신뢰 기관 |
| 체인 | 서버 cert → 중간 CA → root CA로 이어지는 검증 경로 |

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

## 실습: 단계별로 따라하기

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

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 TLS를 "안전 = ON" 스위치가 아니라 키 관리 시스템으로 봅니다. 갱신 주기, 비공개 키 보호, root CA 신뢰 정책, mTLS 정책 — 이 운영 측면이 알고리즘 자체보다 중요합니다. 인증서가 만료된 그 1시간이 분기 매출을 결정할 수도 있기 때문입니다.

또한 시니어는 "암호화는 했다, 그러므로 안전하다"는 단순한 결론을 경계합니다. 어떤 키가 어떤 메타데이터를 누구에게 노출하는지, 키가 유출되면 무엇이 무너지는지를 구체적으로 그려 봅니다.

## 체크리스트

- [ ] TLS 3가지 보장(기밀성/무결성/신원)을 안다
- [ ] 인증서, CA, 체인, 신뢰 저장소를 안다
- [ ] handshake의 큰 단계를 그릴 수 있다
- [ ] 운영에서 `verify=False`를 절대 쓰지 않는다
- [ ] 인증서 만료를 자동 모니터링한다

## 연습 문제

1. 자주 가는 사이트의 인증서를 openssl로 받아 issuer, 만료일, SAN을 정리하세요.

2. 자기서명 인증서로 로컬 HTTPS 서버를 띄우고, Python `ssl` 모듈로 정상/실패 케이스 두 가지를 시연하세요.

3. "왜 mTLS가 zero-trust 인프라에서 중요한가?"를 한 문단으로 설명하세요.

## 정리 및 다음 단계

TLS는 비대칭 키로 신원과 키 합의를, 대칭 키로 빠른 암호화를, AEAD로 무결성을 보장하는 조합입니다. 인증서와 PKI는 "이 키가 진짜 이 도메인 것"임을 보증합니다. 이 그림이 잡히면 모든 HTTPS 사고가 같은 책장 위에서 보입니다.

다음 글에서는 TLS가 보호한 패킷이 인터넷을 어떻게 흘러가는지 — 라우팅과 NAT로 넘어갑니다.

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
## 참고 자료

- [RFC 8446 — TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Bulletproof TLS — Ivan Ristic](https://www.feistyduck.com/books/bulletproof-tls-and-pki/)

Tags: Computer Science, 네트워크, TLS, 인증서, 암호화, PKI

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
