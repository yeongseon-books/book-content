---
series: computer-networks-101
episode: 8
title: Load Balancer
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
  - LoadBalancer
  - L4
  - L7
  - 헬스체크
seo_description: Load Balancer가 트래픽을 분산하고 장애를 격리하는 원리, L4와 L7의 차이, 헬스체크와 sticky session까지 정리합니다.
last_reviewed: '2026-05-04'
---

# Load Balancer

> Computer Networks 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 한 도메인 뒤에 100개의 서버가 있을 때, 클라이언트는 어떻게 매번 "살아 있는 적당한" 서버에 닿을 수 있을까요?

> Load Balancer는 한 가상 IP 뒤에 여러 백엔드를 숨기고, 트래픽을 분산하면서 죽은 서버를 빼냅니다. L4 LB는 IP/포트만 보고 분산하고, L7 LB는 HTTP를 이해해 경로/헤더 기반의 정교한 라우팅을 합니다. 둘 다 현대 서비스의 입구이자 신뢰성의 1선입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- L4 LB와 L7 LB의 차이
- 분산 알고리즘(round-robin, least connections, hash)
- 헬스체크와 graceful drain
- sticky session과 그 비용

## 왜 중요한가

LB는 단순한 분배기가 아니라 시스템의 신뢰성과 배포 전략을 결정짓는 장치입니다. blue-green 배포, canary 출시, region failover, 자동 스케일이 모두 LB 위에서 이뤄집니다. 헬스체크 한 줄을 잘못 쓰면 죽은 서버에 트래픽이 가거나 살아 있는 서버가 통째로 빠집니다.

> LB는 "최선의 서버"를 고르는 장치가 아니라 "충분히 좋은, 살아 있는" 서버를 빨리 고르는 장치입니다.

## 개념 한눈에 보기

```text
client → LB (1 virtual IP) → [backend 1, 2, 3, ...]
            ├─ healthcheck (HTTP/TCP)
            ├─ algorithm  (round-robin / least conn / hash)
            └─ TLS terminate (선택)
```

L4 LB는 TCP 흐름만, L7 LB는 HTTP 요청 단위로 분산합니다.

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| Virtual IP (VIP) | 클라이언트가 보는 LB 주소 |
| 헬스체크 | 백엔드가 살아 있는지 주기적으로 확인 |
| Round-robin | 순서대로 분산 |
| Least connections | 현재 연결 수가 가장 적은 백엔드로 |
| Sticky session | 같은 클라이언트는 같은 백엔드로 (쿠키/IP hash) |

## Before / After

**Before — "서버 한 대로 끝까지":**

```text
client → app1
app1이 죽으면 서비스 다운
```

**After — "여러 백엔드 + LB":**

```text
client → LB → [app1, app2, app3]
app1이 죽으면 헬스체크가 빼고, 나머지로 트래픽이 흐름
```

## 실습: 단계별로 따라하기

### 1단계: 백엔드 두 개 띄우기

```python
# backend.py — Flask
from flask import Flask
import os, sys
name = sys.argv[1] if len(sys.argv) > 1 else 'a'
app = Flask(__name__)
@app.get('/')
def home(): return f'hello from {name}\n'
@app.get('/health')
def health(): return 'ok', 200
if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 9001)))
```

```bash
PORT=9001 python backend.py app1 &
PORT=9002 python backend.py app2 &
```

### 2단계: nginx로 L7 LB

```nginx
# nginx.conf (snippet)
upstream backend {
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
server {
    listen 8080;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

```bash
nginx -c $(pwd)/nginx.conf
for i in 1 2 3 4; do curl -s localhost:8080/; done
# hello from app1
# hello from app2
# hello from app1
# hello from app2
```

기본은 round-robin입니다.

### 3단계: 헬스체크 추가

```nginx
upstream backend {
    server 127.0.0.1:9001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:9002 max_fails=2 fail_timeout=10s;
}
```

`/health`가 실패하면 nginx는 해당 백엔드로 일정 시간 트래픽을 보내지 않습니다. 정교한 active healthcheck는 nginx Plus 또는 envoy/HAProxy 사용.

### 4단계: 알고리즘 바꾸기

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

요청별 처리 시간이 다르면 least connections가 평균 지연을 낮춰 줍니다.

### 5단계: sticky session

```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

`ip_hash`는 같은 클라이언트 IP를 같은 백엔드로 보냅니다. 세션 저장이 메모리에 있을 때 임시 처방이지만, 본질적으로는 stateless로 만드는 것이 정답입니다.

## 이 코드에서 주목할 점

- LB의 가치는 분산 그 자체보다 헬스체크와 배포 전략 지원에 있음
- L4(TCP)는 빠르지만 HTTP 의미를 모름. L7은 라우팅/리트라이/헤더 조작 가능
- sticky session은 쉬운 임시방편이고, 자유로운 스케일을 막는 비용
- TLS termination 위치(LB vs 백엔드)가 보안과 운영 모두에 영향

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 헬스체크가 너무 단순(`/`) | 부분 장애를 못 잡음 | 의존성 점검까지 포함한 `/health` |
| 헬스체크 간격 너무 길음 | 죽은 서버가 오래 살아 있음 | 1~5초 간격 + 빠른 fail_timeout |
| graceful drain 없이 종료 | in-flight 요청 끊김 | SIGTERM → 헬스체크 fail → drain → kill |
| 모든 트래픽을 sticky session | 스케일/배포 어려움 | 세션을 redis/jwt로 분리 |
| L7만 신뢰 | 비-HTTP/저지연 워크로드에 부적합 | gRPC, DB 등은 L4 또는 전용 |

## 실무에서는 이렇게 쓰입니다

- 클라우드: AWS ALB(L7) / NLB(L4), GCP HTTP(S) LB
- 내부 마이크로서비스: envoy/Istio sidecar
- 프록시 + 캐시: nginx, HAProxy, Caddy
- DB: pgbouncer, ProxySQL 같은 전용 LB
- 글로벌 트래픽: anycast + DNS GeoLB

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 LB를 단순한 분배기가 아니라 "서비스 안정성의 1선"으로 봅니다. 새 서비스 설계 시 가장 먼저 그리는 것이 LB의 헬스체크와 배포 시퀀스입니다. canary, blue-green, weighted routing 같은 패턴이 LB 설정 한 줄 차이로 가능 또는 불가능해지기 때문입니다.

또한 시니어는 LB의 한계를 인지합니다. LB가 SPOF가 되지 않도록 LB 자체를 다중화(active-active 또는 active-standby)하고, DNS 라운드로빈, anycast 같은 상위 계층의 장치도 함께 설계합니다.

## 체크리스트

- [ ] L4와 L7의 차이를 안다
- [ ] 헬스체크 정책을 설계할 수 있다
- [ ] sticky session의 비용을 안다
- [ ] graceful drain 절차를 안다
- [ ] LB 자체의 다중화를 고려한다

## 연습 문제

1. 위 nginx 예제를 확장해 한쪽 백엔드를 죽이고, 헬스체크가 트래픽을 어떻게 옮기는지 관찰하세요.

2. canary 배포 시나리오를 그려 보세요. 새 버전에 5%만 보내려면 LB 설정이 어떻게 달라져야 하는가?

3. "왜 sticky session을 가급적 피해야 하는가?"를 한 문단으로 답하세요.

## 정리 및 다음 단계

LB는 "많은 서버를 한 가상 주소 뒤에 숨기고, 살아 있는 것만 고른다"는 단순한 일을 수많은 변형으로 합니다. 헬스체크와 배포 전략, sticky session 비용, TLS termination 위치 — 이 네 가지만 잘 다뤄도 신뢰성이 한 단계 올라갑니다.

다음 글에서는 요청/응답이 아니라 양방향 스트림인 — WebSocket과 실시간 통신을 다룹니다.

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
- [IP와 subnet](./02-ip-and-subnet.md)
- [TCP와 UDP](./03-tcp-and-udp.md)
- [DNS](./04-dns.md)
- [HTTP와 HTTPS](./05-http-and-https.md)
- [TLS 기초](./06-tls-basics.md)
- [라우팅과 NAT](./07-routing-and-nat.md)
- **Load Balancer (현재 글)**
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)
<!-- toc:end -->

## 참고 자료

- [NGINX HTTP Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [HAProxy Documentation](https://docs.haproxy.org/)
- [Envoy Proxy Docs](https://www.envoyproxy.io/docs)
- [AWS ELB User Guide](https://docs.aws.amazon.com/elasticloadbalancing/)
