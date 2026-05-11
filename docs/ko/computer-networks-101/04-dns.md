---
series: computer-networks-101
episode: 4
title: DNS
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
  - DNS
  - resolver
  - 캐싱
  - TTL
seo_description: 도메인 이름이 IP로 변환되는 과정과 DNS 계층 구조, TTL과 캐싱의 의미를 한 번에 정리합니다.
last_reviewed: '2026-05-04'
---

# DNS

> Computer Networks 101 시리즈 (4/10)


## 이 글에서 다룰 문제

"인터넷 안 돼요"의 절반은 DNS 문제이고, 그중 상당수는 TTL과 캐시를 오해해서 생깁니다. DNS를 이해하지 못하면 배포 후 "아직 옛날 IP로 가요"가 미스터리로 남고, 서비스 이전이나 region failover가 오래 걸립니다. 또 모든 HTTP 요청은 DNS lookup으로 시작하기 때문에 성능 분석에서 빠질 수 없습니다.

> "It's always DNS" — 인터넷 운영자의 농담이지만 절반 이상의 진실입니다.

## 전체 흐름
> 클라이언트는 OS의 stub resolver에게 묻고, stub은 보통 ISP/회사의 recursive resolver에게 묻습니다. resolver는 root → TLD → authoritative 서버를 순서대로 물어 답을 찾고, 그 답을 TTL 동안 캐시합니다.

```text
browser
  └─ stub resolver (OS)
       └─ recursive resolver (ISP / 8.8.8.8 / 1.1.1.1)
            ├─ root server      (".")
            ├─ TLD server       (".com")
            └─ authoritative    ("example.com.")
```

## Before / After

**Before — "DNS는 어딘가의 큰 사전":**

```text
example.com → 어떻게? 모름.
```

**After — "DNS는 분산된 트리 + 캐시":**

```text
. → com → example.com → A 93.184.216.34
각 단계는 다른 서버이고, resolver가 위임을 따라가며 합친다
```

## 단계별로 따라하기

### 1단계: dig로 단일 조회

```bash
dig example.com +noall +answer
# example.com.  86400  IN  A  93.184.216.34
```

86400(초)은 TTL입니다. 24시간 동안 캐시될 수 있다는 뜻입니다.

### 2단계: 위임 추적

```bash
dig example.com +trace
# .                ← root
# com.             ← TLD
# example.com.     ← authoritative
```

resolver가 실제로 거치는 경로를 그대로 봅니다.

### 3단계: 다양한 레코드 타입

```bash
dig MX gmail.com +short
dig AAAA cloudflare.com +short
dig TXT _dmarc.gmail.com +short
```

도메인 하나에 여러 레코드 타입이 공존합니다.

### 4단계: Python에서 조회

```python
import socket

print(socket.gethostbyname('example.com'))   # 93.184.216.34
print(socket.getaddrinfo('example.com', 443, type=socket.SOCK_STREAM))
# OS의 stub resolver를 그대로 사용
```

또는 더 정밀하게:

```python
import dns.resolver   # pip install dnspython

ans = dns.resolver.resolve('example.com', 'A')
for r in ans:
    print(r.to_text(), 'TTL', ans.rrset.ttl)
```

### 5단계: tcpdump로 DNS 패킷 보기

```bash
sudo tcpdump -i any -nn 'udp port 53'
# A? example.com
# A 93.184.216.34
```

DNS는 기본 UDP 53번 포트, 응답이 크면 TCP로 넘어갑니다(DNSSEC, EDNS 등).

## 이 코드에서 주목할 점

- DNS lookup은 모든 HTTP 요청의 첫 단계 — 캐시되지 않으면 수백 ms가 추가됨
- TTL은 정확한 데드라인이 아니라 캐시의 "유통기한 권고"
- 하나의 도메인에 여러 A/AAAA 레코드가 올 수 있음(라운드로빈, 지리 기반)
- CNAME 체인이 길면 lookup 자체가 느려짐

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TTL을 1일로 두고 IP 즉시 교체 기대 | 클라이언트 캐시 때문에 느린 전환 | 이전 전 TTL을 미리 60초 등으로 낮춤 |
| `/etc/hosts`로 임시 해결 후 잊음 | 영속적 미스터리 | 변경 시 즉시 원복 |
| nslookup만 보고 OK 판단 | 실제 앱은 다른 resolver를 쓸 수 있음 | 앱 컨테이너 안에서 dig |
| DNS 사고를 항상 의심 | 진단 시간 낭비 | ping/curl/dig을 함께 써서 분리 |
| CNAME으로 root 도메인을 가리킴 | RFC 위반, 일부 resolver 실패 | ALIAS/ANAME 등의 대안 사용 |

## 실무에서는 이렇게 쓰입니다

- 서비스 이전: TTL을 미리 줄이고, 새 IP로 변경
- CDN: 사용자 위치에 따라 다른 IP 응답(GeoDNS)
- failover: 헬스체크에 따라 authoritative가 다른 IP 회신
- 메일: SPF, DKIM, DMARC 모두 TXT 레코드
- 컨테이너: k8s 안의 DNS(coredns)가 service 이름을 ClusterIP로 변환

## 체크리스트

- [ ] DNS 계층(root → TLD → authoritative)을 안다
- [ ] A, AAAA, CNAME, MX, TXT의 용도를 안다
- [ ] dig으로 위임을 추적할 수 있다
- [ ] TTL이 운영에 미치는 영향을 안다
- [ ] DNS 변경 전 TTL을 먼저 줄인다

## 정리 및 다음 단계

DNS는 인터넷의 전화번호부이자, 운영 사고의 절반을 차지하는 캐싱 시스템입니다. 계층 구조와 TTL을 이해하면 배포·이전·failover가 갑자기 예측 가능해집니다.

다음 글에서는 DNS로 찾은 IP에 실제로 보내는 메시지 — HTTP와 HTTPS로 넘어갑니다.

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
- [IP와 subnet](./02-ip-and-subnet.md)
- [TCP와 UDP](./03-tcp-and-udp.md)
- **DNS (현재 글)**
- HTTP와 HTTPS (예정)
- TLS 기초 (예정)
- 라우팅과 NAT (예정)
- Load Balancer (예정)
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)
<!-- toc:end -->

## 참고 자료

- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035)
- [Cloudflare Learning — What is DNS?](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [dnspython 문서](https://www.dnspython.org/)
- [Julia Evans — How DNS works (zine)](https://wizardzines.com/zines/dns/)
