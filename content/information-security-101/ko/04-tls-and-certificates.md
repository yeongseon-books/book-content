---
title: "Information Security 101 (4/10): TLS와 인증서"
series: information-security-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Computer Science
  - Security
  - TLS
  - Certificate
  - PKI
  - mTLS
last_reviewed: '2026-05-12'
seo_description: TLS 1.3 핸드셰이크, 인증서 체인, mTLS의 핵심을 짧게 정리합니다.
---

# Information Security 101 (4/10): TLS와 인증서

브라우저 주소창의 자물쇠 아이콘은 너무 익숙해서 오히려 의미를 잊기 쉽습니다. 그냥 HTTPS라고만 생각하고 넘어가면 인증서 만료, 약한 암호군 허용, 검증 비활성화 같은 사고가 반복됩니다. 자물쇠는 마법이 아니라 매우 구체적인 절차의 결과입니다.

이 글은 Information Security 101 시리즈의 4번째 글입니다.

## 먼저 던지는 질문

- 브라우저 자물쇠는 정확히 무엇을 보장할까요?
- TLS 1.3 핸드셰이크는 어떤 단계로 진행될까요?
- X.509 인증서 체인은 어떻게 검증될까요?

## 큰 그림

![Information Security 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/information-security-101/04/04-01-big-picture.ko.png)

*Information Security 101 4장 흐름 개요*

그림은 클라이언트와 서버가 CA 인증서로 서로를 검증하고, 공개 키 교환을 거쳐 세션 키를 공유한 뒤 암호화 통신하는 흐름을 보여줍니다. 각 단계에서 누가 누를 검증하고 어떤 증명서를 남기는지가 중요합니다.

> TLS는 단순 암호화가 아니라 '이 서버가 정말 example.com인가'를 인증서로 증명하고, 중간자가 개입할 수 없도록 핸드셰이크를 설계하는 것입니다.

## 왜 중요한가

서비스 간 트래픽의 큰 비중이 TLS로 보호됩니다. 그런데 내부 동작을 이해하지 못하면 인증서 만료를 놓치거나, 약한 암호군을 켜 둔 채 운영하거나, 편의상 검증을 꺼 버리는 식의 사고가 생깁니다. TLS는 켜기만 하면 끝나는 기능이 아니라, 계속 관리해야 하는 운영 절차에 가깝습니다.

자물쇠 아이콘은 신비한 보호막이 아닙니다. 정해진 검증 과정이 모두 통과됐다는 표시일 뿐입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    C["Client"] -->|ClientHello| S["Server"]
    S -->|"Cert + Key Share"| C
    C -->|"Finished"| S
    S -->|"Application Data"| C
```

TLS 1.3은 한 번의 왕복 안에서 키 합의와 서버 인증을 끝냅니다. 그 짧은 과정 안에 꽤 많은 보안 판단이 들어 있습니다.

## 핵심 용어

- **TLS**: TCP 위에서 동작하는 암호화 프로토콜입니다.
- **X.509**: 인증서 형식의 표준입니다.
- **CA**: 인증서를 발급하는 기관입니다.
- 체인: 서버 인증서에서 중간 CA를 거쳐 루트 CA로 이어지는 신뢰 경로입니다.
- **mTLS**: 서버뿐 아니라 클라이언트도 인증서를 제시하는 방식입니다.

## 전후 비교

### 이전 — 평문 HTTP

```text
A middlebox can read and modify packets -> credentials leaked
```

### 이후 — TLS 1.3

```text
Key agreement + server auth + AEAD -> secrecy, integrity, origin
```

평문에서 TLS로 넘어가는 변화는 현대 서비스 보안의 최소선입니다. 여기서부터가 출발점입니다.

## 단계별 실습

### 1단계 — 인증서를 직접 봅니다

```bash
# 1_view_cert.sh
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

주체, 발급자, 유효기간을 한 번에 볼 수 있습니다. 운영에서는 이 기본 정보만 빨리 읽어도 만료나 체인 문제를 상당수 좁힐 수 있습니다.

### 2단계 — 파이썬에서 TLS 연결을 엽니다

```python
# 2_tls_client.py
import ssl, socket
ctx = ssl.create_default_context()
with socket.create_connection(("example.com", 443)) as sock:
    with ctx.wrap_socket(sock, server_hostname="example.com") as s:
        print(s.version())          # TLSv1.3
        print(s.cipher())
```

`create_default_context()`는 검증 활성화와 현대적인 암호군 같은 안전한 기본값을 함께 제공합니다.

### 3단계 — 자체 서명 인증서를 만듭니다

```bash
# 3_selfsigned.sh
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=localhost"
```

개발 환경에서는 쓸 수 있지만 운영 환경에서는 안 됩니다. 신뢰 체인이 없기 때문입니다.

### 4단계 — 인증서 체인을 검증합니다

```bash
# 4_verify_chain.sh
openssl verify -CAfile chain.pem server.pem
```

체인이 깨지면 브라우저 경고가 뜹니다. 많은 장애가 여기서 시작합니다.

### 5단계 — mTLS 서버를 구성합니다

```python
# 5_mtls.py
import ssl
ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ctx.verify_mode = ssl.CERT_REQUIRED
ctx.load_cert_chain("server.pem", "server.key")
ctx.load_verify_locations("client_ca.pem")
# server.serve_forever() ...
```

서비스 간 통신처럼 상대 클라이언트도 식별해야 할 때는 서버뿐 아니라 클라이언트 인증서까지 검증합니다.

## 이 코드와 예제에서 먼저 볼 점

- 호스트명 검증은 절대 꺼 두면 안 됩니다.
- TLS 1.2 이상만 허용하고 1.0, 1.1은 꺼야 합니다.
- RC4, 3DES 같은 약한 암호군은 비활성화해야 합니다.
- 인증서 갱신은 수동 작업이 아니라 자동화 파이프라인이어야 합니다.

## 자주 하는 실수 다섯 가지

1. **인증서 검증을 끄는 실수**: 운영 환경에서 `verify=False`는 금지입니다.
2. **만료 모니터링이 없는 실수**: 만료된 인증서로 예고 없는 장애가 납니다.
3. **약한 암호군을 허용하는 실수**: 다운그레이드 공격 위험을 키웁니다.
4. **운영 환경에서 자체 서명 인증서를 쓰는 실수**: 신뢰 체인이 없습니다.
5. **mTLS 키 회전이 없는 실수**: 한 번 유출되면 장기 노출이 됩니다.

## 실무에서는 이렇게 나타납니다

Kubernetes에서는 cert-manager와 Let's Encrypt가 90일 인증서를 자동 갱신합니다. 서비스 메시인 Istio나 Linkerd는 mTLS 인증서를 눈에 띄지 않게 발급하고 교체합니다. AWS ACM, GCP Certificate Manager도 로드 밸런서와 결합해 인증서 운영을 자동화합니다. 결국 핵심은 암호화 자체보다 신뢰와 갱신을 얼마나 자동화했는가에 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 인증서 만료는 경보 문제가 아니라 자동화 문제로 봅니다.
- 신뢰 저장소 변경은 변경 관리 절차를 거칩니다.
- 서비스 간 통신은 기본적으로 mTLS를 검토합니다.
- TLS 종료 지점을 명시적으로 결정합니다.
- 약한 알고리즘 허용 여부를 주기적으로 재검토합니다.

## 체크리스트

- [ ] TLS 1.3 핸드셰이크 단계를 설명할 수 있습니까?
- [ ] 인증서 체인 검증 과정을 설명할 수 있습니까?
- [ ] 단방향 TLS와 mTLS의 차이를 말할 수 있습니까?
- [ ] 인증서가 자동 갱신되고 있습니까?
- [ ] 약한 암호군을 식별할 수 있습니까?

## 연습 문제

1. TLS 1.2와 1.3의 큰 차이 두 가지를 적어 보세요.
2. mTLS가 잘 맞는 시나리오 두 가지를 설명해 보세요.
3. 인증서 만료 30일 전에 알림을 보내는 의사코드를 적어 보세요.

## 정리와 다음 글

TLS는 비밀성, 무결성, 출처 검증을 한 번에 묶는 프로토콜입니다. 인증서는 그 약속을 신뢰할 수 있게 만드는 장치입니다. 다음 글에서는 이 보호된 웹 위에서 동작하는 브라우저 보안의 기본, 웹 보안 기초를 다룹니다.


## TLS 핸드셰이크를 단계별로 추적하기

TLS 1.3은 왕복 횟수를 줄였지만 내부 판단은 오히려 더 정교해졌습니다. 운영 관점에서는 다음 다섯 단계를 분리해 이해하는 것이 중요합니다.

1. ClientHello: 지원 버전, 암호군, key share를 제시합니다.
2. ServerHello: 서버가 선택한 암호군과 key share를 반환합니다.
3. Certificate: 서버 인증서 체인을 제공합니다.
4. CertificateVerify + Finished: 서버가 개인키 소유를 증명하고 핸드셰이크 무결성을 확정합니다.
5. Client Finished: 클라이언트도 동일한 트랜스크립트로 완료를 확인합니다.

이 흐름에서 장애가 가장 많이 나는 지점은 3번(인증서 체인)과 1/2번(호환 암호군/버전)입니다. 따라서 트래픽 장애 시 애플리케이션 코드보다 먼저 TLS 협상 로그를 보는 습관이 필요합니다.

## 인증서 체인 검증 체크리스트

| 검증 항목 | 실패 시 증상 | 확인 방법 |
| --- | --- | --- |
| SAN에 요청 도메인 포함 | 브라우저 이름 불일치 경고 | `openssl x509 -text` |
| Not Before/Not After 유효기간 | 갑작스런 접속 실패 | 만료 모니터링/알림 |
| 중간 인증서 누락 | 특정 클라이언트만 실패 | fullchain 배포 확인 |
| 루트 신뢰 저장소 불일치 | 일부 환경에서만 오류 | OS/런타임 trust store 점검 |
| 폐기(Revocation) 상태 | 보안 경고 또는 차단 | OCSP/CRL 정책 점검 |

인증서 체인을 이해하면 "내 로컬에서는 되는데 운영에서는 안 된다" 같은 문제를 빠르게 좁힐 수 있습니다.

## Python으로 TLS 인증서 정보 점검

```python
# tls_probe.py
import socket
import ssl
from datetime import datetime


def probe(host: str, port: int = 443) -> None:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=5) as raw:
        with ctx.wrap_socket(raw, server_hostname=host) as tls:
            cert = tls.getpeercert()
            print("version:", tls.version())
            print("cipher:", tls.cipher())
            print("subject:", cert.get("subject"))
            print("issuer:", cert.get("issuer"))
            print("notAfter:", cert.get("notAfter"))
            if cert.get("notAfter"):
                exp = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                print("days_left:", (exp - datetime.utcnow()).days)

probe("example.com")
```

서비스 상태 점검에 이 코드를 주기적으로 실행하면 만료 임박, 버전 하향, 예기치 않은 인증서 변경을 조기에 감지할 수 있습니다.

## mTLS 도입 시 운영 포인트

mTLS는 서버뿐 아니라 클라이언트도 인증서를 제시하므로 내부 서비스 식별 강도가 크게 올라갑니다. 대신 운영 복잡도가 늘어납니다.

| 항목 | 단방향 TLS | mTLS |
| --- | --- | --- |
| 서버 신원 검증 | 필수 | 필수 |
| 클라이언트 신원 검증 | 보통 없음 | 필수 |
| 인증서 발급/회전 수 | 상대적으로 적음 | 서비스 수만큼 증가 |
| 사고 시 영향 범위 | 서버 키 유출 중심 | 서버/클라이언트 모두 관리 필요 |

mTLS를 도입할 때는 인증서 자동 발급/회전(예: service mesh, cert-manager)을 먼저 준비해야 합니다. 수동 운영은 장기적으로 실패 확률이 높습니다.


## 운영 점검 루프와 문서화 기준

보안 글에서 가장 자주 빠지는 부분은 "그래서 운영에서는 무엇을 주기적으로 확인할 것인가"입니다. 아래 루프를 기준으로 문서화하면 개념이 실무로 연결됩니다.

| 주기 | 점검 항목 | 산출물 |
| --- | --- | --- |
| 매일 | 고위험 경보, 인증 실패 급증, 권한 거부 급증 | 일일 보안 브리핑 |
| 매주 | 신규 배포 변경점의 보안 영향 | 변경 검토 노트 |
| 매월 | 키/토큰/인증서 만료 예정, 미사용 권한, 미사용 시크릿 | 월간 정리 리포트 |
| 분기 | 위협 모델 재평가, 런북 훈련, 통제 효과 검토 | 분기 보안 회고 |

실행 가능한 문서의 조건도 분명해야 합니다.

- 담당자(owner)와 대체 담당자가 명시되어야 합니다.
- 실패 조건과 에스컬레이션 기준이 수치로 정의되어야 합니다.
- 점검 결과가 티켓이나 액션 아이템으로 추적되어야 합니다.
- 예외 승인에는 만료일이 반드시 있어야 합니다.

보안은 단발성 프로젝트가 아니라 운영 루프입니다. 같은 점검을 반복해도 기준이 유지될 때 품질이 올라갑니다.


## 인증서 투명성과 CT 로그



인증서 투명성(Certificate Transparency, CT)은 CA가 인증서를 발급할 때마다 공개 로그에 기록하도록 강제하는 체계입니다. 잘못된 발급이나 악의적인 CA를 조기에 탐지하는 데 핵심 역할을 합니다.



| 구성 요소 | 역할 | 운영 의미 |

| --- | --- | --- |

| CT 로그 서버 | 발급된 인증서를 append-only 로그에 기록 | 위조 인증서 발견 시 증거 확보 |

| SCT(Signed Certificate Timestamp) | 인증서가 로그에 등록된 증거 | 브라우저가 SCT 없는 인증서를 거부할 수 있음 |

| 모니터링 서비스 | 조직 도메인에 대한 신규 발급 감시 | 피싱/섀도 도메인 조기 경보 |



CT 모니터링은 방어적 관점에서 매우 실용적입니다. 누군가 여러분 도메인에 대해 인증서를 발급하면 알림이 오기 때문에, 도메인 탈취 공격이나 서브도메인 하이재킹을 조기에 인식할 수 있습니다.



```bash

# CT 로그에서 특정 도메인의 인증서 발급 이력 조회

# crt.sh를 이용한 간단한 확인

curl -s "https://crt.sh/?q=%.example.com&output=json" | python3 -m json.tool | head -30

```



## TLS 암호군 감사 스크립트



운영 중인 서비스의 TLS 설정이 기준선을 만족하는지 주기적으로 점검해야 합니다. 다음 스크립트는 서버가 허용하는 암호군 목록을 추출하고, 약한 암호군이 포함되었는지 확인합니다.



```python

# tls_cipher_audit.py

import ssl

import socket

from typing import Final



WEAK_CIPHERS: Final[set] = {"RC4", "3DES", "DES", "NULL", "EXPORT"}





def audit_ciphers(host: str, port: int = 443) -> list[str]:

    ctx = ssl.create_default_context()

    warnings = []

    with socket.create_connection((host, port), timeout=5) as raw:

        with ctx.wrap_socket(raw, server_hostname=host) as tls:

            cipher_name, protocol, bits = tls.cipher()

            for weak in WEAK_CIPHERS:

                if weak in cipher_name.upper():

                    warnings.append(f"약한 암호군 감지: {cipher_name}")

            if bits < 128:

                warnings.append(f"키 길이 부족: {bits}bit")

            if "TLSv1.0" in protocol or "TLSv1.1" in protocol:

                warnings.append(f"구버전 프로토콜: {protocol}")

    return warnings





issues = audit_ciphers("example.com")

if issues:

    for w in issues:

        print(f"[WARN] {w}")

else:

    print("[OK] TLS 설정 기준선 통과")

```



이 스크립트를 CI/CD 파이프라인에 넣으면 배포 시점에 TLS 설정 회귀를 자동 감지할 수 있습니다.



## 방화벽 규칙과 TLS 종료 지점

TLS를 어디서 종료할지 결정하면 네트워크 규칙도 같이 설계해야 합니다. 아래 표는 최소 권장 규칙 예시입니다.

| 구간 | 허용 포트 | 출발지 | 목적지 | 정책 |
| --- | --- | --- | --- | --- |
| 인터넷 -> 엣지 로드밸런서 | 443 | Any | LB | 허용 |
| 인터넷 -> 애플리케이션 노드 | 80,443 | Any | App | 거부 |
| LB -> 앱 서비스 | 443 | LB 서브넷 | App | 허용 |
| 앱 -> DB | 5432 | App 서브넷 | DB | 허용 |

TLS가 켜져 있어도 포트 노출이 넓으면 공격 표면이 크게 남습니다. "암호화됨"과 "접근 제어됨"은 다른 문제이므로 방화벽 규칙을 반드시 함께 검토해야 합니다.

## 인증서 장애 런북 요약

1. 인증서 만료 경보 수신 후 영향 도메인 목록을 확정합니다.
2. 신규 인증서 발급 전 체인(fullchain) 구성을 먼저 점검합니다.
3. 스테이징에서 핸드셰이크 검증 후 점진 배포합니다.
4. 배포 후 `openssl s_client`와 애플리케이션 헬스체크로 재확인합니다.
5. 사후 회고에서 만료 알림 임계값과 자동화 누락을 보완합니다.


## 인증서 운영 캘린더 예시

인증서 장애는 대부분 만료 직전에 발견됩니다. 이를 막으려면 일정 기반 운영 캘린더가 필요합니다.

| 시점 | 작업 | 담당 |
| --- | --- | --- |
| 만료 30일 전 | 자동 갱신 상태 확인, 경보 테스트 | 플랫폼 팀 |
| 만료 14일 전 | 스테이징 체인 검증, 호환성 테스트 | 애플리케이션 팀 |
| 만료 7일 전 | 운영 배포 승인, 롤백 계획 확정 | 보안/운영 공동 |
| 만료 후 | 로그 점검, 회고, 임계값 조정 | SRE/보안 |

## 내부 서비스 mTLS 확장 체크리스트

- 서비스별 클라이언트 인증서 발급 주체를 명확히 합니다.
- 인증서 재발급 자동화를 수동 절차로 대체하지 않습니다.
- 폐기된 인증서 목록(deny list) 배포 지연을 모니터링합니다.
- 서비스 메시 또는 게이트웨이에서 실패 이벤트를 중앙 수집합니다.

mTLS는 보안 강도를 크게 높이지만, 수명 주기 자동화가 없으면 운영 리스크가 더 커질 수 있습니다. 도입 전후로 장애 실험을 반드시 수행해야 합니다.


## TLS 설정 기준선 예시

| 항목 | 권장 값 | 금지 값 |
| --- | --- | --- |
| 프로토콜 버전 | TLS 1.2, TLS 1.3 | TLS 1.0, TLS 1.1 |
| 키 교환 | ECDHE | 정적 RSA 키 교환 |
| 대칭 암호 | AES-GCM, ChaCha20-Poly1305 | RC4, 3DES |
| 인증서 키 길이 | RSA 2048+ 또는 ECDSA P-256+ | RSA 1024 이하 |

기준선을 문서화해두면 신규 서비스 온보딩 시 "기본 설정"으로 바로 적용할 수 있습니다. 매 서비스마다 수동 판단을 반복하면 설정 편차가 커집니다.

## 인증서 회전 실패 패턴

- 신규 인증서만 배포하고 중간 인증서 체인 누락
- 스테이징 검증 없이 운영 선배포
- 만료 알림 임계값을 1-2일로 너무 늦게 설정
- 인증서 배포 자동화와 서비스 재로드 분리 실패

이 패턴은 대부분 운영 절차의 빈틈에서 생깁니다. 기술 문제로 보이지만 실제로는 프로세스 문제인 경우가 많습니다.

## 네트워크 팀과의 협업 체크리스트

1. TLS 종료 지점을 단일 다이어그램으로 합의합니다.
2. 종료 지점별 인증서 소유 팀을 명시합니다.
3. 포트/방화벽 변경 시 보안 리뷰를 필수화합니다.
4. 장애 훈련에서 인증서 만료 시나리오를 포함합니다.


## 부록: 팀 보안 리뷰 워크시트

다음 워크시트는 기능 배포 전 보안 리뷰에서 반복적으로 확인하는 항목을 표준화한 것입니다.

### 1) 자산과 경계 정의

| 항목 | 기록 예시 |
| --- | --- |
| 보호 대상 데이터 | 사용자 이메일, 결제 토큰, 내부 리포트 |
| 진입 경로 | 웹 폼, 모바일 API, 관리자 콘솔 |
| 신뢰 경계 | 인터넷-엣지, 엣지-앱, 앱-DB |
| 외부 의존성 | 결제 API, 메시지 큐, 파일 저장소 |

### 2) 통제 매핑

| 위협 | 예방 통제 | 탐지 통제 | 대응 통제 |
| --- | --- | --- | --- |
| 계정 탈취 | MFA, 비밀번호 정책 | 로그인 이상 징후 경보 | 세션 강제 종료, 자격 재설정 |
| 데이터 변조 | 입력 검증, 무결성 서명 | 감사 로그 무결성 검증 | 롤백, 포렌식 조사 |
| 서비스 과부하 | 레이트 리밋, WAF | 오류율/지연 경보 | 트래픽 차단, 임시 확장 |

### 3) 운영 점검 질문

- 이번 변경으로 새로 열리는 네트워크 포트가 있는가
- 권한 범위가 기존보다 넓어지는가
- 로그 스키마 변경이 탐지 규칙에 영향을 주는가
- 비밀 정보 또는 토큰 수명 정책이 달라지는가
- 장애 시 롤백 절차가 검증되어 있는가

### 4) 배포 전 검증 항목

| 항목 | 통과 기준 |
| --- | --- |
| 보안 테스트 | 고위험 실패 없음 |
| 설정 검증 | 디버그/임시 설정 제거 |
| 감사 로그 | 주요 이벤트 필드 누락 없음 |
| 문서 최신화 | 런북과 운영 가이드 업데이트 완료 |

워크시트의 목적은 문서를 늘리는 것이 아니라 의사결정 속도를 높이는 것입니다. 보안 검토가 반복될수록 질문과 답변이 짧아지고, 같은 사고가 재발할 가능성이 줄어듭니다.


## 부록: 인증서 운영 장애 사례

운영에서 자주 만나는 사례는 비슷합니다. 첫째, 자동 갱신이 성공했지만 서비스 재로드가 실패해 구 인증서를 계속 쓰는 경우입니다. 둘째, 신규 서브도메인을 추가했지만 SAN 목록에 누락되어 특정 경로에서만 TLS 오류가 발생하는 경우입니다. 셋째, 중간 인증서 체인이 누락되어 일부 클라이언트에서만 접속 실패가 재현되는 경우입니다.

이 세 가지는 모두 "검증 자동화"가 있으면 배포 전에 걸러집니다. 따라서 만료 모니터링만으로는 충분하지 않고, 실제 핸드셰이크 검증까지 파이프라인에 포함해야 합니다.


### TLS 인증서 자동 검증 스크립트

배포 파이프라인에 포함할 수 있는 인증서 검증 스크립트입니다.

```python
"""TLS 인증서 핸드셰이크 검증 스크립트."""
import ssl
import socket
from datetime import datetime, timezone


def verify_certificate(hostname: str, port: int = 443) -> dict:
    """실제 핸드셰이크를 수행하여 인증서 상태를 확인한다."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
            not_after = datetime.strptime(
                cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
            ).replace(tzinfo=timezone.utc)
            days_left = (not_after - datetime.now(timezone.utc)).days
            san_list = [
                entry[1]
                for entry in cert.get("subjectAltName", [])
                if entry[0] == "DNS"
            ]
            return {
                "hostname": hostname,
                "protocol": tls.version(),
                "cipher": tls.cipher()[0],
                "days_until_expiry": days_left,
                "san_entries": san_list,
                "issuer": dict(x[0] for x in cert["issuer"]),
            }


if __name__ == "__main__":
    targets = ["api.example.com", "web.example.com"]
    for host in targets:
        result = verify_certificate(host)
        status = "OK" if result["days_until_expiry"] > 30 else "WARN"
        print(f"[{status}] {host}: {result['days_until_expiry']}일 남음, "
              f"{result['protocol']}, {result['cipher']}")
```

이 스크립트는 단순 만료 확인을 넘어서 세 가지를 동시에 검증합니다. 첫째, 실제 TLS 핸드셰이크 성공 여부(중간 인증서 체인 포함)를 확인합니다. 둘째, SAN 목록에 대상 호스트가 포함되었는지 검증합니다. 셋째, 프로토콜 버전과 암호군이 기대 값인지 점검합니다.

## 처음 질문으로 돌아가기

- **브라우저 자물쇠는 정확히 무엇을 보장할까요?**
  - HTTPS 요청이 들어왔을 때 서버 인증서를 읽고, 클라이언트가 CA 체인으로 검증하고, 공개 키 핸드셰이크를 거쳐 세션이 맺어지는 각 단계를 이해하면 인증서 오류를 대응할 수 있습니다.
- **TLS 1.3 핸드셰이크는 어떤 단계로 진행될까요?**
  - Self-signed 인증서와 CA 서명 인증서의 차이, 와일드카드와 SAN 인증서의 검증 차이를 구분하면 배포 장애를 줄일 수 있습니다.
- **X.509 인증서 체인은 어떻게 검증될까요?**
  - 인증서 만료일 모니터링, 갱신 스크립트 검증, 인증서 핀징 정책을 정의하고, 인증서 오류 발생 시 로그 규칙을 정합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Information Security 101 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [Information Security 101 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- [Information Security 101 (3/10): 암호화와 해시](./03-cryptography-and-hash.md)
- **TLS와 인증서 (현재 글)**
- 웹 보안 기초 (예정)
- SQL 인젝션과 XSS (예정)
- 비밀 정보 관리 (예정)
- 권한 최소화 (예정)
- 로그와 감사 (예정)
- 보안 사고 대응 (예정)

<!-- toc:end -->

## 참고 자료

- [RFC 8446 — TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt — How It Works](https://letsencrypt.org/how-it-works/)
- [BetterTLS — Test Suite](https://bettertls.com/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/information-security-101/ko)

Tags: Computer Science, Security, TLS, Certificate, PKI, mTLS
