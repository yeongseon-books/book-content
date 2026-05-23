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


![Computer Networks 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/08/08-01-concept-at-a-glance.ko.png)
*Computer Networks 101 8장 흐름 개요*

## 먼저 던지는 질문

- L4 로드밸런서와 L7 로드밸런서는 어떻게 다를까요?
- round-robin, least connections, hash 같은 분산 알고리즘은 언제 쓰일까요?
- 헬스체크와 graceful drain은 왜 신뢰성의 핵심일까요?

## 왜 중요한가

로드밸런서는 단순한 분배기가 아닙니다. 실제로는 시스템의 신뢰성과 배포 전략을 결정하는 장치입니다. blue-green 배포, canary 릴리스, 리전 failover, 자동 스케일링은 모두 로드밸런서 위에서 성립합니다. 헬스체크 하나를 잘못 만들면 죽은 서버에 트래픽이 가거나, 멀쩡한 서버가 풀에서 빠질 수 있습니다.

> 로드밸런서는 "최선의 서버"를 찾는 장치가 아니라, "충분히 괜찮고 살아 있는 서버"를 빠르게 고르는 장치입니다.

## 핵심 그림

```text
┌──────────┐
│ 클라이언트 │
└─────┬────┘
      │  VIP: 203.0.113.100:443
      ▼
┌──────────────────────────────────────────┐
│           Load Balancer (L7)              │
│  ┌────────────────────────────────────┐  │
│  │ TLS 종료 → HTTP 파싱 → 라우팅 결정  │  │
│  └────────────────────────────────────┘  │
└─────┬────────────┬────────────┬──────────┘
      │            │            │
      ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ app1    │  │ app2    │  │ app3    │
│ :9001   │  │ :9002   │  │ :9003   │
│ [정상]   │  │ [정상]   │  │ [drain] │
└─────────┘  └─────────┘  └─────────┘
```

L4 로드밸런서는 TCP/UDP 흐름(IP + 포트)만 보고 백엔드를 고릅니다. L7 로드밸런서는 HTTP 요청(URL, 헤더, 쿠키)까지 파싱한 뒤 라우팅을 결정합니다.

| 구분 | L4 (Transport) | L7 (Application) |
| --- | --- | --- |
| 판단 기준 | src/dst IP, port | URL path, Host header, cookie |
| TLS 종료 | 불가 (pass-through) | 가능 |
| 콘텐츠 기반 라우팅 | 불가 | `/api/*` → service A, `/web/*` → service B |
| 성능 | 매우 높음 (패킷 전달) | 상대적으로 낮음 (HTTP 파싱 비용) |
| 재시도 | 불가 | 요청 단위로 가능 |
| 대표 도구 | AWS NLB, LVS, IPVS | AWS ALB, nginx, Envoy, HAProxy |

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Virtual IP (VIP) | 클라이언트가 바라보는 로드밸런서 주소 |
| 헬스체크 | 백엔드가 살아 있는지 주기적으로 확인하는 절차 |
| Round-robin | 순서대로 고르게 분산하는 방식 |
| Least connections | 현재 연결 수가 가장 적은 백엔드로 보내는 방식 |
| Weighted round-robin | 서버 용량에 비례해 가중치를 두고 분산 |
| Consistent hash | 키(IP, URL 등)를 해시링에 매핑해 같은 키는 같은 백엔드로 |
| Sticky session | 같은 클라이언트를 같은 백엔드에 계속 보내는 방식 |
| Drain | 기존 연결은 유지하되 새 연결을 받지 않는 상태 |

## 적용 전후 비교
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
# backend.py — 플라스크
from flask import Flask, jsonify
import os, sys, time

name = sys.argv[1] if len(sys.argv) > 1 else 'a'
app = Flask(__name__)
start_time = time.time()

@app.get('/')
def home():
    return f'hello from {name}\n'

@app.get('/health')
def health():
    return jsonify(status='ok', server=name, uptime=int(time.time() - start_time))

@app.get('/slow')
def slow():
    time.sleep(2)
    return f'slow response from {name}\n'

if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 9001)))
```

```bash
PORT=9001 python backend.py app1 &
PORT=9002 python backend.py app2 &

# 확인
curl localhost:9001/health
# {"server":"app1","status":"ok","uptime":3}
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
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
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

기본 분산 방식은 round-robin입니다. 요청이 균등하게 번갈아 가는 것을 볼 수 있습니다.

### 3단계: 헬스체크 추가하기

```nginx
upstream backend {
    server 127.0.0.1:9001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:9002 max_fails=2 fail_timeout=10s;
}
```

이 설정은 passive health check입니다. 실제 요청이 2회 연속 실패하면 10초간 해당 백엔드를 제외합니다.

active health check(주기적으로 `/health`를 호출)가 필요하면 nginx Plus나 Envoy를 사용합니다.

```yaml
# Envoy active health check 예시
health_checks:
  - timeout: 1s
    interval: 3s
    unhealthy_threshold: 3
    healthy_threshold: 2
    http_health_check:
      path: /health
      expected_statuses:
        - start: 200
          end: 299
```

좋은 헬스체크의 조건:

| 조건 | 이유 |
| --- | --- |
| 실제 의존성 일부를 확인 | DB 연결이 끊긴 상태에서 200을 반환하면 무의미 |
| 빠르게 응답 (< 200ms) | 헬스체크 자체가 타임아웃이면 false negative |
| 별도 엔드포인트 사용 | 메인 트래픽과 분리해 모니터링 |
| 상태 정보 포함 | JSON으로 uptime, 연결 풀 상태 등을 반환 |

### 4단계: 분산 알고리즘 비교

```nginx
# Round-robin (기본)
upstream backend {
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}

# Least connections
upstream backend {
    least_conn;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}

# Weighted
upstream backend {
    server 127.0.0.1:9001 weight=3;
    server 127.0.0.1:9002 weight=1;
}

# IP hash (sticky)
upstream backend {
    ip_hash;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

알고리즘 선택 가이드:

| 알고리즘 | 적합한 상황 | 부적합한 상황 |
| --- | --- | --- |
| Round-robin | 백엔드 사양이 동일하고 요청 처리 시간이 균일 | 요청별 처리 시간 차이가 큰 경우 |
| Least connections | 요청 처리 시간이 제각각 (예: API 서버) | 백엔드 수가 매우 많은 경우 (상태 추적 비용) |
| Weighted | 백엔드 사양이 다를 때 (예: 4코어 vs 8코어) | 사양 차이가 없는 동종 클러스터 |
| IP hash | 로컬 캐시 활용이 중요할 때 | 특정 IP에서 트래픽이 쏠릴 때 |
| Consistent hash | 캐시 서버 풀, 샤딩 | 연결 수 균형이 중요한 경우 |

### 5단계: sticky session 붙이기

```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

`ip_hash`는 같은 클라이언트 IP를 같은 백엔드로 보냅니다. 세션이 메모리에 있을 때 잠깐 버티는 용도일 뿐, 장기적으로는 서비스를 stateless하게 만드는 편이 낫습니다.

sticky session의 문제점:

1. 한 백엔드가 죽으면 해당 사용자의 세션이 소실됩니다.
2. 특정 백엔드에 트래픽이 쏠릴 수 있습니다.
3. auto-scaling으로 새 인스턴스를 추가해도 기존 사용자는 이동하지 않습니다.
4. canary 배포 시 사용자 비율 제어가 어렵습니다.

대안: 세션을 Redis나 JWT로 외부화하면 어떤 백엔드가 요청을 받아도 동일하게 처리할 수 있습니다.

### 6단계: graceful drain과 canary를 함께 설계하기

로드밸런서가 진짜 빛나는 순간은 장애 평상시가 아니라 **배포 순간**입니다. 새 버전으로 한 번에 바꾸지 말고, 먼저 새 연결만 소량 보내고 기존 연결은 자연스럽게 빠지게 만들어야 합니다.

```nginx
upstream backend {
    server 127.0.0.1:9001 weight=19;   # 기존 버전
    server 127.0.0.1:9002 weight=1;    # 새 버전 (canary)
}
```

위처럼 weight를 19:1로 두면 대략 5% 수준의 canary 트래픽을 새 버전으로 보낼 수 있습니다. 절차는 보통 다음 순서를 따릅니다.

1. 새 버전을 풀에 넣되 낮은 비율로만 받게 합니다.
2. 에러율과 p95/p99 지연을 짧게 관찰합니다.
3. 문제가 없으면 비율을 점진적으로 올립니다.
4. 종료할 인스턴스는 먼저 헬스체크에서 빠지게 하고, 진행 중인 요청이 끝난 뒤 프로세스를 내립니다.

graceful drain의 구체적 절차:

```text
1. LB에 "이 백엔드를 drain 상태로" 표시
   → 새 요청을 보내지 않음
2. 기존 진행 중 요청이 완료될 때까지 대기 (timeout 설정)
3. 모든 연결이 닫히면 프로세스 종료
4. 새 버전 프로세스 시작
5. 헬스체크 통과 후 LB가 트래픽 재개
```

```bash
# Kubernetes에서의 graceful shutdown
# pod spec에 preStop hook과 terminationGracePeriodSeconds를 설정
# 1. preStop: sleep 5 (LB가 엔드포인트 제거할 시간)
# 2. SIGTERM 수신 → 새 요청 거부, 기존 요청 완료
# 3. terminationGracePeriodSeconds(30s) 내에 종료
```

### 7단계: HAProxy로 L4 로드밸런서 만들기

nginx가 L7에 강하다면 HAProxy는 L4와 L7 모두에서 높은 성능을 보여줍니다.

```text
# haproxy.cfg
frontend tcp_front
    bind *:3306
    mode tcp
    default_backend mysql_servers

backend mysql_servers
    mode tcp
    balance roundrobin
    option tcp-check
    server db1 10.0.0.11:3306 check inter 3s fall 3 rise 2
    server db2 10.0.0.12:3306 check inter 3s fall 3 rise 2
```

이 설정은 MySQL 접속을 L4에서 분산합니다. `mode tcp`이므로 HTTP를 파싱하지 않고 TCP 연결 단위로 백엔드를 고릅니다. `inter 3s fall 3 rise 2`는 "3초마다 검사, 3회 연속 실패 시 제거, 2회 연속 성공 시 복구"를 의미합니다.

HAProxy의 stats 페이지를 활성화하면 웹 UI로 실시간 상태를 볼 수 있습니다.

```text
listen stats
    bind *:9090
    stats enable
    stats uri /haproxy-stats
    stats refresh 5s
```

이 페이지는 각 백엔드의 연결 수, 응답 시간, 에러율, UP/DOWN 상태를 한 눈에 보여줍니다. 운영 중 문제가 생겼을 때 가장 먼저 확인하는 대시보드이며, Prometheus exporter와 연동하면 Grafana에서도 동일한 지표를 시계열로 볼 수 있습니다.

## 이 코드에서 먼저 볼 점

- 로드밸런서의 진짜 가치는 분산 자체보다 헬스체크와 배포 전략에 있습니다.
- L4는 빠르지만 HTTP를 이해하지 못하고, L7은 라우팅, 재시도, 헤더 조작이 가능합니다.
- sticky session은 당장은 쉬워 보여도 자유로운 확장과 배포를 막습니다.
- TLS를 어디서 종료할지(LB 또는 백엔드)는 보안과 운영에 모두 영향을 줍니다.
- connection draining 없는 배포는 사용자에게 에러를 보여주는 배포입니다.

## TLS 종료 위치 결정

TLS를 어디서 끊느냐에 따라 아키텍처가 달라집니다.

| 방식 | 장점 | 단점 |
| --- | --- | --- |
| LB에서 종료 (TLS offload) | 인증서 관리 집중, 백엔드 부하 감소, HTTP 헤더 검사 가능 | LB↔백엔드 구간 평문 (내부망 신뢰 필요) |
| 백엔드에서 종료 (pass-through) | 종단간 암호화, 규제 준수 용이 | 인증서 분산 관리, L7 기능 불가 |
| LB에서 종료 후 재암호화 | 내부 구간도 암호화, L7 기능 사용 가능 | TLS 핸드셰이크 2회, 성능 비용 |

실무에서는 대부분 LB에서 TLS를 종료하고 내부는 평문 또는 mTLS를 사용합니다. PCI-DSS 같은 규제가 있으면 재암호화를 선택하기도 합니다.

## 로드밸런서 모니터링과 메트릭

로드밸런서를 운영하면 반드시 관찰해야 하는 메트릭이 있습니다.

| 메트릭 | 의미 | 경고 기준 예시 |
| --- | --- | --- |
| Active connections | 현재 열려 있는 연결 수 | 평소 대비 3배 이상 증가 |
| Request rate (RPS) | 초당 처리 요청 수 | 용량 계획의 80% 초과 |
| Error rate (5xx) | 백엔드에서 반환한 서버 에러 비율 | 1% 초과 |
| Latency p50/p95/p99 | 요청 처리 지연 분포 | p99가 SLO 초과 |
| Healthy backends | 헬스체크 통과 백엔드 수 | 전체의 50% 미만 |
| Connection queue | 백엔드 연결 대기 큐 길이 | 0이 아닌 상태가 지속 |
| Bandwidth in/out | 네트워크 처리량 | 인터페이스 용량의 80% 초과 |

```bash
# nginx status 모듈로 실시간 상태 확인
curl localhost:8080/nginx_status
# Active connections: 243
# server accepts handled requests
#  12345678  12345678  45678901
# Reading: 5 Writing: 12 Waiting: 226
```

nginx에서 `Writing`이 `Active connections`의 대부분을 차지하면 백엔드 응답이 느린 것입니다. `Waiting`이 대부분이면 keepalive 연결이 idle 상태로 있는 정상 상황입니다.

## L4 로드밸런서 심화: DSR과 IPVS

고성능이 필요한 환경에서는 L4 로드밸런서의 DSR(Direct Server Return) 모드를 사용합니다.

```text
일반 모드 (proxy):
  Client → LB → Backend → LB → Client
  (모든 트래픽이 LB를 거침)

DSR 모드:
  Client → LB → Backend → Client
  (응답은 LB를 거치지 않고 직접 클라이언트로)
```

DSR의 장점은 응답 트래픽(보통 요청보다 10-100배 큼)이 LB를 거치지 않으므로 LB의 대역폭 병목을 제거할 수 있다는 사실입니다.

Linux에서 IPVS를 사용한 L4 로드밸런서 설정:

```bash
# IPVS 모듈 로드
modprobe ip_vs

# Virtual service 추가 (VIP: 10.0.0.100:80, round-robin)
ipvsadm -A -t 10.0.0.100:80 -s rr

# Real server 추가
ipvsadm -a -t 10.0.0.100:80 -r 10.0.0.1:80 -m  # masquerading (NAT)
ipvsadm -a -t 10.0.0.100:80 -r 10.0.0.2:80 -m

# 상태 확인
ipvsadm -L -n --stats
# IP Virtual Server version 1.2.1
# Prot LocalAddress:Port               Conns   InPkts  OutPkts  InBytes OutBytes
# TCP  10.0.0.100:80                    15234   98765   234567   5.2M    89.1M
#   -> 10.0.0.1:80                       7612   49382   117283   2.6M    44.5M
#   -> 10.0.0.2:80                       7622   49383   117284   2.6M    44.6M
```

Kubernetes의 kube-proxy는 내부적으로 iptables 또는 IPVS를 사용합니다. 대규모 클러스터(Service 수 1000+)에서는 IPVS 모드가 iptables 모드보다 성능이 좋습니다.

## 로드밸런서 장애 시나리오와 대응

| 시나리오 | 증상 | 대응 |
| --- | --- | --- |
| 전체 백엔드 헬스체크 실패 | 503 Service Unavailable | panic mode: 마지막 known-good 백엔드 유지, 또는 static fallback 페이지 |
| LB 자체 과부하 | 연결 큐 증가, 지연 급증 | auto-scaling, 또는 DNS에서 다른 LB로 분산 |
| 백엔드 1대만 느림 | 해당 백엔드 연결이 쌓이고 전체 지연 증가 | circuit breaker, outlier detection (Envoy) |
| TLS 인증서 만료 | 클라이언트 연결 거부 | 인증서 자동 갱신 (Let's Encrypt, cert-manager) |
| 네트워크 파티션 | 일부 백엔드만 접근 불가 | 다중 AZ 배포, cross-zone load balancing |

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 헬스체크가 너무 단순함 (`/` 200) | DB 연결 끊긴 상태를 놓침 | 실제 의존성을 확인하는 `/health`를 만든다 |
| 헬스체크 간격이 너무 김 (30s+) | 죽은 서버가 오래 풀에 남음 | 3~5초 간격과 짧은 `fail_timeout`을 쓴다 |
| graceful drain 없이 종료 | 진행 중인 요청이 끊김 | SIGTERM → 헬스체크 실패 → drain → 종료 순서를 지킨다 |
| sticky session에 과도하게 의존 | 스케일과 배포가 어려워짐 | 세션을 Redis나 JWT로 외부화한다 |
| L7만 만능이라고 생각 | 비HTTP 초저지연 워크로드에 부적합 | L4 또는 전용 프록시를 검토한다 |

## 실무에서는 이렇게 보입니다

- 클라우드에서는 AWS ALB(L7), NLB(L4), GCP HTTP(S) LB, Azure Application Gateway 등을 사용합니다. managed 서비스는 자체 이중화와 auto-scaling을 제공합니다.
- 내부 마이크로서비스는 Envoy sidecar나 Istio service mesh를 통해 서비스 간 통신에도 L7 로드밸런싱을 적용합니다. circuit breaker, retry, timeout을 LB 레벨에서 제어합니다.
- nginx, HAProxy, Caddy는 프록시와 캐시를 겸하는 실무 도구입니다. HAProxy는 connection 수 만 단위에서도 안정적이고, nginx는 정적 파일 서빙을 겸할 때 많이 쓰입니다.
- 데이터베이스 앞에는 pgbouncer(PostgreSQL), ProxySQL(MySQL) 같은 특화된 connection pooler가 놓이기도 합니다. 이들도 헬스체크와 failover를 수행합니다.
- 글로벌 트래픽은 anycast와 DNS 기반 GeoLB를 함께 써서 사용자를 가장 가까운 리전으로 보냅니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 로드밸런서를 단순 분배기가 아니라 서비스 안정성의 첫 줄로 봅니다. 새 서비스를 설계할 때도 제일 먼저 헬스체크와 배포 순서를 스케치합니다. canary, blue-green, weighted routing 같은 패턴이 가능한지 여부는 종종 로드밸런서 설정 한두 줄에 달려 있습니다.

또한 로드밸런서 자신이 단일 장애점이 되지 않도록 다중화 전략도 함께 봅니다. active-active, active-standby, DNS round-robin, anycast 같은 상위 계층 메커니즘을 함께 고려합니다.

장애 시나리오를 미리 그려보는 습관도 있습니다.

- 백엔드 1대가 느려지면? → least connections가 자동으로 트래픽을 줄여주는가?
- 전체 백엔드가 동시에 헬스체크 실패하면? → 마지막 1대는 유지하는 "panic mode"가 있는가?
- LB 자체가 장애나면? → DNS failover 또는 anycast로 다른 LB로 전환되는가?

## 체크리스트

- [ ] L4와 L7의 차이를 판단 기준, TLS 종료, 재시도 가능 여부로 설명할 수 있다
- [ ] 헬스체크 정책을 interval, threshold, endpoint 관점에서 설계할 수 있다
- [ ] round-robin, least connections, weighted, hash의 적합한 상황을 구분할 수 있다
- [ ] sticky session의 비용과 대안을 설명할 수 있다
- [ ] graceful drain 절차를 순서대로 나열할 수 있다
- [ ] 로드밸런서 자체의 이중화를 계획할 수 있다
- [ ] TLS 종료 위치에 따른 trade-off를 안다

## 연습 문제

1. nginx 예제를 확장해 백엔드 하나를 죽인 뒤, 헬스체크가 트래픽을 어떻게 옮기는지 관찰해 보세요.
2. `least_conn`과 `round-robin`을 각각 설정한 뒤, `/slow` 엔드포인트에 동시 요청을 보내 응답 시간 분포가 어떻게 달라지는지 비교해 보세요.
3. 5%만 새 버전으로 보내는 canary 배포를 하려면 로드밸런서 구성이 어떻게 바뀌어야 하는지 스케치해 보세요.
4. "가능하면 sticky session을 피해야 하는 이유"를 한 단락으로 설명해 보세요.
5. 헬스체크 엔드포인트가 DB 연결을 확인하도록 `/health`를 확장하고, DB를 내린 뒤 LB 동작을 관찰해 보세요.

## 정리와 다음 글

로드밸런서는 많은 서버를 하나의 주소 뒤에 숨기고, 살아 있는 서버를 고르는 단순한 역할을 다양한 방식으로 수행합니다. 헬스체크, 배포 전략, sticky session의 비용, TLS 종료 위치가 신뢰성을 가장 크게 움직이는 네 축입니다.

다음 글에서는 요청/응답을 넘어 양방향 스트림으로 가는 WebSocket과 실시간 통신을 다룹니다.

## 처음 질문으로 돌아가기

- **L4 로드밸런서와 L7 로드밸런서는 어떻게 다를까요?**
  - L4는 TCP/UDP 4-tuple(src IP, src port, dst IP, dst port)만 보고 연결 단위로 백엔드를 선택합니다. 패킷을 거의 그대로 전달하므로 빠르지만, HTTP 헤더를 읽거나 URL 기반 라우팅을 할 수 없습니다. L7은 HTTP 요청을 완전히 파싱해 Host 헤더, URL path, 쿠키 등으로 라우팅을 결정하고, 요청 단위 재시도와 헤더 조작이 가능합니다.
- **round-robin, least connections, hash 같은 분산 알고리즘은 언제 쓰일까요?**
  - round-robin은 백엔드가 동종이고 요청 처리 시간이 균일할 때 가장 단순하고 효과적입니다. least connections는 요청별 처리 시간이 크게 다를 때(예: 일부 요청이 DB 쿼리를 오래 걸리는 API 서버) 느린 백엔드로의 쏠림을 방지합니다. hash는 캐시 서버 풀처럼 같은 키가 항상 같은 백엔드에 가야 할 때 사용합니다.
- **헬스체크와 graceful drain은 왜 신뢰성의 핵심일까요?**
  - 헬스체크가 없으면 죽은 서버에 트래픽이 계속 가서 사용자가 에러를 봅니다. graceful drain이 없으면 배포할 때마다 진행 중인 요청이 끊깁니다. 이 둘이 합쳐져야 "배포해도 사용자가 에러를 안 보는" 시스템이 됩니다. 무중단 배포의 전제 조건은 헬스체크 + drain + 새 인스턴스 준비 완료의 세 박자입니다.

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
- [book-examples: computer-networks-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, LoadBalancer, L4, L7, 헬스체크
