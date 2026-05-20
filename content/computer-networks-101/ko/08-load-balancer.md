---
series: computer-networks-101
episode: 8
title: "Computer Networks 101 (8/10): Load Balancer"
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
  - LoadBalancer
  - L4
  - L7
  - 헬스체크
seo_description: 부하 분산과 신뢰성의 핵심인 로드밸런서의 동작 원리와 L4, L7의 차이점 및 헬스체크와 분산 알고리즘 활용 방법을 상세히 다룹니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (8/10): Load Balancer

이 글은 Computer Networks 101 시리즈의 8번째 글입니다.

## 먼저 던지는 질문

- L4 로드밸런서와 L7 로드밸런서는 어떻게 다를까요?
- round-robin, least connections, hash 같은 분산 알고리즘은 언제 쓰일까요?
- 헬스체크와 graceful drain은 왜 신뢰성의 핵심일까요?

## 큰 그림

![Computer Networks 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/08/08-01-concept-at-a-glance.ko.png)

*Computer Networks 101 8장 흐름 개요*

이 그림에서는 Load Balancer를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Load Balancer의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

로드밸런서는 단순한 분배기가 아닙니다. 실제로는 시스템의 신뢰성과 배포 전략을 결정하는 장치입니다. blue-green 배포, canary 릴리스, 리전 failover, 자동 스케일링은 모두 로드밸런서 위에서 성립합니다. 헬스체크 하나를 잘못 만들면 죽은 서버에 트래픽이 가거나, 멀쩡한 서버가 풀에서 빠질 수 있습니다.

> 로드밸런서는 "최선의 서버"를 찾는 장치가 아니라, "충분히 괜찮고 살아 있는 서버"를 빠르게 고르는 장치입니다.

## 핵심 그림

L4 로드밸런서는 TCP 흐름만 보고, L7 로드밸런서는 HTTP 요청 단위로 판단합니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Virtual IP (VIP) | 클라이언트가 바라보는 로드밸런서 주소 |
| 헬스체크 | 백엔드가 살아 있는지 주기적으로 확인하는 절차 |
| Round-robin | 순서대로 고르게 분산하는 방식 |
| Least connections | 현재 연결 수가 가장 적은 백엔드로 보내는 방식 |
| Sticky session | 같은 클라이언트를 같은 백엔드에 계속 보내는 방식 |

## Before / After

**Before — "서버 한 대가 죽으면 서비스도 끝"**

```text
client → app1
app1 dies → service down
```

**After — "여러 백엔드와 로드밸런서"**

```text
client → LB → [app1, app2, app3]
app1 dies → health check removes it, traffic flows to the rest
```

## 단계별로 따라하기

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

### 2단계: nginx로 L7 로드밸런서 만들기

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

기본 분산 방식은 round-robin입니다.

### 3단계: 헬스체크 추가하기

```nginx
upstream backend {
    server 127.0.0.1:9001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:9002 max_fails=2 fail_timeout=10s;
}
```

헬스체크가 반복해서 실패하면 nginx는 잠시 그 백엔드로 트래픽을 보내지 않습니다. 더 풍부한 active health check가 필요하면 nginx Plus, Envoy, HAProxy 같은 도구를 씁니다.

### 4단계: 분산 알고리즘 바꿔 보기

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

요청 처리 시간이 제각각이면 least connections가 평균 지연을 낮추는 데 유리합니다.

### 5단계: sticky session 붙이기

```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

`ip_hash`는 같은 클라이언트 IP를 같은 백엔드로 보냅니다. 세션이 메모리에 있을 때 잠깐 버티는 용도일 뿐, 장기적으로는 서비스를 stateless하게 만드는 편이 낫습니다.

## 6단계: graceful drain과 canary를 함께 설계하기

로드밸런서가 진짜 빛나는 순간은 장애 평상시가 아니라 **배포 순간**입니다. 새 버전으로 한 번에 바꾸지 말고, 먼저 새 연결만 소량 보내고 기존 연결은 자연스럽게 빠지게 만들어야 합니다.

```nginx
upstream backend {
    server 127.0.0.1:9001 weight=19;
    server 127.0.0.1:9002 weight=1;
}
```

위처럼 weight를 19:1로 두면 대략 5% 수준의 canary 트래픽을 새 버전으로 보낼 수 있습니다. 그다음 절차는 보통 다음 순서를 따릅니다.

1. 새 버전을 풀에 넣되 낮은 비율로만 받게 합니다.
2. 에러율과 p95/p99 지연을 짧게 관찰합니다.
3. 문제가 없으면 비율을 점진적으로 올립니다.
4. 종료할 인스턴스는 먼저 헬스체크에서 빠지게 하고, 진행 중인 요청이 끝난 뒤 프로세스를 내립니다.

sticky session에 의존하는 서비스일수록 이 절차가 어려워집니다. 같은 사용자가 계속 같은 백엔드에 묶여 있으니, 비율 조정이 곧바로 실제 사용자 비율로 이어지지 않기 때문입니다.

## 이 코드에서 먼저 볼 점

- 로드밸런서의 진짜 가치는 분산 자체보다 헬스체크와 배포 전략에 있습니다.
- L4는 빠르지만 HTTP를 이해하지 못하고, L7은 라우팅, 재시도, 헤더 조작이 가능합니다.
- sticky session은 당장은 쉬워 보여도 자유로운 확장과 배포를 막습니다.
- TLS를 어디서 종료할지(LB 또는 백엔드)는 보안과 운영에 모두 영향을 줍니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 헬스체크가 너무 단순함 | 부분 장애를 놓침 | 실제 의존성을 일부 확인하는 `/health`를 만든다 |
| 헬스체크 간격이 너무 김 | 죽은 서버가 오래 풀에 남음 | 1~5초 간격과 짧은 `fail_timeout`을 쓴다 |
| graceful drain 없이 종료 | 진행 중인 요청이 끊김 | SIGTERM → 헬스체크 실패 → drain → 종료 순서를 지킨다 |
| sticky session에 과도하게 의존 | 스케일과 배포가 어려워짐 | 세션을 Redis나 JWT로 외부화한다 |
| L7만 만능이라고 생각 | 비HTTP·초저지연 워크로드에 부적합 | L4 또는 전용 로드밸런서를 검토한다 |

## 실무에서는 이렇게 보입니다

- 클라우드에서는 AWS ALB(L7), NLB(L4), GCP HTTP(S) LB 등을 사용합니다.
- 내부 마이크로서비스는 Envoy나 Istio sidecar를 자주 씁니다.
- nginx, HAProxy, Caddy는 프록시와 캐시를 겸하는 실무 도구입니다.
- 데이터베이스 앞에는 pgbouncer, ProxySQL 같은 특화된 프록시가 놓이기도 합니다.
- 글로벌 트래픽은 anycast와 DNS 기반 GeoLB를 함께 쓰는 경우가 많습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 로드밸런서를 단순 분배기가 아니라 서비스 안정성의 첫 줄로 봅니다. 새 서비스를 설계할 때도 제일 먼저 헬스체크와 배포 순서를 스케치합니다. canary, blue-green, weighted routing 같은 패턴이 가능한지 여부는 종종 로드밸런서 설정 한두 줄에 달려 있습니다.

또한 로드밸런서 자신이 단일 장애점이 되지 않도록 다중화 전략도 함께 봅니다. active-active, active-standby, DNS round-robin, anycast 같은 상위 계층 메커니즘을 함께 고려합니다.

## 체크리스트

- [ ] L4와 L7의 차이를 설명할 수 있다
- [ ] 헬스체크 정책을 설계할 수 있다
- [ ] sticky session의 비용을 안다
- [ ] graceful drain 절차를 설명할 수 있다
- [ ] 로드밸런서 자체의 이중화를 계획한다

## 연습 문제

1. nginx 예제를 확장해 백엔드 하나를 죽인 뒤, 헬스체크가 트래픽을 어떻게 옮기는지 관찰해 보세요.
2. 5%만 새 버전으로 보내는 canary 배포를 하려면 로드밸런서 구성이 어떻게 바뀌어야 하는지 스케치해 보세요.
3. "가능하면 sticky session을 피해야 하는 이유"를 한 단락으로 설명해 보세요.

## 정리와 다음 글

로드밸런서는 많은 서버를 하나의 주소 뒤에 숨기고, 살아 있는 서버를 고르는 단순한 역할을 다양한 방식으로 수행합니다. 헬스체크, 배포 전략, sticky session의 비용, TLS 종료 위치가 신뢰성을 가장 크게 움직이는 네 축입니다.

다음 글에서는 요청/응답을 넘어 양방향 스트림으로 가는 WebSocket과 실시간 통신을 다룹니다.

## 처음 질문으로 돌아가기

- **L4 로드밸런서와 L7 로드밸런서는 어떻게 다를까요?**
  - 본문의 기준은 Load Balancer를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **round-robin, least connections, hash 같은 분산 알고리즘은 언제 쓰일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **헬스체크와 graceful drain은 왜 신뢰성의 핵심일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP와 UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- [Computer Networks 101 (5/10): HTTP와 HTTPS](./05-http-and-https.md)
- [Computer Networks 101 (6/10): TLS 기초](./06-tls-basics.md)
- [Computer Networks 101 (7/10): 라우팅과 NAT](./07-routing-and-nat.md)
- **Load Balancer (현재 글)**
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)

<!-- toc:end -->

## 참고 자료

- [NGINX HTTP Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [HAProxy Documentation](https://docs.haproxy.org/)
- [Envoy Proxy Docs](https://www.envoyproxy.io/docs)
- [AWS ELB User Guide](https://docs.aws.amazon.com/elasticloadbalancing/)
- [Google SRE Book — Handling Overload](https://sre.google/sre-book/handling-overload/)

Tags: Computer Science, 네트워크, LoadBalancer, L4, L7, 헬스체크
