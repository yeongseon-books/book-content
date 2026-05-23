---
series: distributed-systems-101
episode: 5
title: "Distributed Systems 101 (5/10): 복제"
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
  - Distributed Systems
  - Replication
  - LeaderFollower
  - QuorumWrites
  - Durability
seo_description: 데이터 복제 모델인 리더 기반, 리더리스 구조와 쿼럼 합의, 복제 지연의 원인과 해결 방안을 상세히 정리합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (5/10): 복제

데이터를 여러 노드에 복사해 두면 안전할 것 같지만, 실제 운영 질문은 그 다음부터 시작됩니다. 어떤 복제본이 기준인지, 얼마만큼의 지연을 허용할지, 리더가 죽을 때 최근 쓰기를 얼마나 잃을 수 있는지가 모두 복제 설정에서 갈립니다.

여기서는 복제를 저장소의 뒷단 구현이 아니라, 시스템이 사용자에게 약속하는 안전성과 지연 특성을 결정하는 설계 레이어로 봅니다.

![Distributed Systems 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/05/05-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 5장 흐름 개요*

## 먼저 던지는 질문

- 왜 데이터를 복제하며, 어떤 복제 모델이 있을까요?
- leader-follower, multi-leader, leaderless는 어떻게 다를까요?
- 동기 복제와 비동기 복제는 어떤 데이터 손실 위험을 만들까요?

## 왜 중요한가

복제는 모든 분산 데이터 시스템의 가장 밑바닥 층입니다. 이 층의 선택이 4편에서 본 일관성 모델을 만들고, 6편에서 볼 합의 비용도 규정합니다. 실무에서 데이터베이스가 왜 이런 식으로 동작하는지 묻는 질문의 답은 대개 복제 설정 안에 있습니다.

> 복제 설정은 안전성과 속도 사이의 환율입니다.

## 한눈에 보는 개념

이 세 가지 토폴로지만 이해해도 현실 시스템의 대부분을 설명할 수 있습니다.

## 핵심 용어

- **Leader/follower**: 쓰기는 하나의 리더가 받고, 읽기는 팔로워로 분산할 수 있는 구조입니다.
- **Multi-leader**: 여러 리더가 동시에 쓰기를 받고 서로를 동기화하는 구조입니다.
- **Leaderless**: 모든 노드가 동등하며 quorum으로 최신 값을 판단하는 구조입니다.
- **Sync replication**: 리더가 팔로워의 확인 응답을 기다린 뒤 쓰기를 완료하는 방식입니다.
- **Quorum (R, W, N)**: N개 복제본 중 R개를 읽고 W개에 쓰며, R+W>N이면 최신값을 읽을 수 있다는 원리입니다.

## 적용 전후 비교
**Before — 단일 primary와 비동기 replica**

```text
fast write but possible data loss on crash
```

**After — 다수 동기 복제와 리더 읽기**

```text
slower write, near-zero loss, linearizable reads possible
```

같은 시스템이라도 옵션 하나가 바뀌면 시스템이 약속하는 바가 달라집니다.

## 실습: 복제 모델을 코드로 보기

### 1단계 — 비동기 leader-follower

```python
# 1_async.py
import threading, time
leader = []
follower = []
def write(x):
    leader.append(x)
    threading.Thread(target=lambda: (time.sleep(0.5), follower.append(x))).start()
```

쓰기 지연은 짧지만, 리더가 갑자기 죽으면 최근 0.5초의 데이터가 사라질 수 있습니다.

### 2단계 — 동기 leader-follower

```python
# 2_sync.py
def write(x):
    leader.append(x)
    follower.append(x)   # write both before returning
```

쓰기 하나가 두 노드에 모두 닿아야 끝납니다. 지연은 늘지만 손실 가능성은 거의 사라집니다.

### 3단계 — quorum write

```python
# 3_quorum.py
nodes = [[], [], []]   # N=3
def write(x, w=2):
    acks = 0
    for n in nodes:
        n.append(x); acks += 1
        if acks >= w: return "ok"
def read(x_id, r=2):
    seen = []
    for n in nodes:
        if any(item["id"] == x_id for item in n):
            seen.append(n)
            if len(seen) >= r: return "found"
```

R+W>N이면 읽기와 쓰기 집합이 최소 한 노드에서 겹칩니다. Dynamo 계열 시스템의 핵심이 바로 이 점입니다.

### 4단계 — multi-leader(단순 last-write-wins)

```python
# 4_mlw.py
A, B = {}, {}
def write_a(k, v): A[k] = (time.time(), v)
def write_b(k, v): B[k] = (time.time(), v)
def merge():
    for k in set(A) | set(B):
        ta, va = A.get(k, (0, None))
        tb, vb = B.get(k, (0, None))
        winner = (va if ta >= tb else vb)
        A[k] = B[k] = (max(ta, tb), winner)
```

LWW는 단순하지만, 시계가 어긋나면 사용자의 입력을 잃어버릴 수 있습니다.

### 5단계 — replication lag 측정

```python
# 5_lag.py
def lag(): return leader_lsn - follower_lsn
print("replication lag rows:", lag())
```

대부분의 데이터베이스는 LSN, GTID, offset 같은 지표를 노출합니다. lag을 SLO로 관리하면 stale read를 사용자가 보기 전에 잡을 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 비동기 복제는 빠르지만 데이터 손실 위험을 남깁니다.
- 동기 복제는 안전하지만 느립니다. 둘 중 하나가 절대적으로 옳은 것이 아니라 워크로드가 기준입니다.
- quorum은 R과 W를 조절해 트레이드오프를 다이얼처럼 다루게 해 줍니다.
- multi-leader에서는 충돌 해결 규칙을 애플리케이션이 직접 정의해야 합니다.

## 자주 하는 실수 5가지

1. **복제본 읽기는 항상 빠르다고 생각합니다.** lag 때문에 stale read가 나옵니다.
2. **유일한 동기 복제본을 한 곳에만 둡니다.** 그 한 곳의 지연이 리더 전체를 막습니다.
3. **multi-leader에서 LWW만 믿습니다.** 시계 어긋남이 곧 데이터 손실로 이어집니다.
4. **R+W>N 규칙을 깨뜨립니다.** 최신값을 읽는 보장이 사라집니다.
5. **lag을 모니터링하지 않습니다.** 사용자가 stale read를 신고한 뒤에야 문제를 압니다.

## 실무에서는 이렇게 드러납니다

PostgreSQL과 MySQL은 기본적으로 leader-follower 복제를 사용합니다. Cassandra와 DynamoDB는 leaderless quorum에 가깝고, CRDT 기반 시스템은 multi-leader 성향이 강합니다. 클라우드의 multi-AZ 데이터베이스는 한 AZ에는 동기로, 다른 AZ에는 비동기로 보내는 혼합형 구성을 자주 씁니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 복제 설정을 문서에 명시적으로 남깁니다.
- 복제본 읽기는 별도 경로로 노출하고 허용 stale 시간도 함께 문서화합니다.
- 단일 느린 지점을 만들지 않도록 동기 복제본을 최소 둘 이상 고려합니다.
- 단순 LWW에 기대지 않고 애플리케이션 수준의 merge 전략을 설계합니다.
- lag을 SLO와 알람으로 관리합니다.

## 체크리스트

- [ ] 동기 복제와 비동기 복제의 차이를 한 줄로 말할 수 있는가?
- [ ] R+W>N의 의미를 설명할 수 있는가?
- [ ] multi-leader 충돌 해결 방법 두 가지를 말할 수 있는가?
- [ ] 현재 데이터베이스의 복제 토폴로지를 그릴 수 있는가?
- [ ] replication lag을 어떻게 측정할지 알고 있는가?

## 연습 문제

1. 현재 서비스에서 stale read가 허용되는 화면 두 개를 골라 보세요.
2. quorum 설정 N=5, W=3, R=3의 가용성과 일관성을 평가해 보세요.
3. multi-leader 시스템에서 같은 키에 대한 동시 쓰기를 어떻게 해석할지 애플리케이션 규칙을 설계해 보세요.

## 정리와 다음 글

복제는 분산 데이터의 토대입니다. 다음 글에서는 여러 노드가 다음 값이 무엇인지 함께 동의하는 문제, 즉 합의와 Raft를 다룹니다.

## 실전 설계 확장: 복제 토폴로지와 장애 복구

복제를 운영 관점에서 깊게 보면 질문은 다섯 가지로 압축됩니다. "어떤 노드가 어떤 키를 책임지는가", "쓰기 성공을 어디에서 확정할 것인가", "복제 지연을 어떻게 수치화할 것인가", "리더 장애 때 승격 순서를 어떻게 강제할 것인가", "복구 후 정합성을 어떤 순서로 회복할 것인가"입니다. 이 섹션에서는 바로 이 다섯 질문을 설계 문서와 런북 수준으로 구체화합니다.

### 일관 해싱으로 샤드와 복제본을 배치하는 이유

노드 수가 바뀔 때 전체 키 재배치를 줄이려면 해시 슬롯 테이블보다 일관 해싱이 유리합니다. 핵심 아이디어는 노드와 키를 같은 해시 링 위에 올린 뒤, 키가 시계 방향으로 처음 만나는 노드를 기본 소유자로 삼는 방식입니다.

```text
해시 링 (0 ~ 2^32-1)

                [Node C]
                   |
       key:k9 ---> | ---> primary: Node C
                   v
        +-----------------------+
        |                       |
[Node B]|                       |[Node D]
        |                       |
        +-----------------------+
                   ^
                   |
                [Node A]

복제계수 RF=3이면:
primary(Node C) + 다음 시계 방향 2개(Node D, Node A)
```

이 구조의 장점은 노드 추가/제거 시 이동 키 범위가 "인접 구간"으로 제한된다는 점입니다. 예를 들어 Node E를 C와 D 사이에 추가하면, 대부분 키는 그대로 두고 해당 구간 키만 E로 이동합니다. 대규모 캐시/스토리지에서 리밸런싱 비용을 줄이는 이유가 여기에 있습니다.

운영에서 반드시 문서화할 값은 다음과 같습니다.

- 가상 노드 개수(vnode 수)
- 복제계수(RF)
- 리밸런싱 속도 제한(초당 이동 키 수 또는 MB/s)
- 핫키 감지 기준(예: 특정 키 QPS 임계치)

이 값들이 빠지면 장애 상황에서 "노드만 늘리면 해결된다"는 잘못된 대응이 나옵니다. 실제로는 vnode 불균형과 핫 파티션 때문에 지연이 유지되는 경우가 많습니다.

### 동기 복제와 비동기 복제: 확정 시점 설계

동기/비동기의 본질은 "성공 응답을 언제 보내는가"입니다. 아래 FastAPI 예시는 같은 API가 확정 지점을 다르게 두었을 때 어떤 동작 차이를 만드는지 보여줍니다.

```python
# sync_async_replication.py
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()

leader_store: dict[str, dict] = {}
follower_a_store: dict[str, dict] = {}
follower_b_store: dict[str, dict] = {}

async def replicate_to_follower(target: dict[str, dict], key: str, value: dict, delay_ms: int) -> None:
    await asyncio.sleep(delay_ms / 1000)
    target[key] = value

@app.post("/sync/items/{key}")
async def write_sync(key: str, payload: dict):
    leader_store[key] = payload
    try:
        await asyncio.gather(
            replicate_to_follower(follower_a_store, key, payload, delay_ms=10),
            replicate_to_follower(follower_b_store, key, payload, delay_ms=12),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"sync replication failed: {exc}")
    return {"mode": "sync", "ack": "committed_on_3_nodes"}

@app.post("/async/items/{key}")
async def write_async(key: str, payload: dict):
    leader_store[key] = payload
    asyncio.create_task(replicate_to_follower(follower_a_store, key, payload, delay_ms=200))
    asyncio.create_task(replicate_to_follower(follower_b_store, key, payload, delay_ms=250))
    return {"mode": "async", "ack": "accepted_on_leader"}
```

이 코드를 운영 의미로 읽으면 다음과 같습니다.

- 동기 엔드포인트는 응답 지연이 길어지지만, 리더 직후 장애에서도 손실 확률이 낮습니다.
- 비동기 엔드포인트는 지연이 짧지만, 리더 장애 시 아직 전파되지 않은 최근 쓰기를 잃을 수 있습니다.
- 따라서 "모든 쓰기를 동기" 또는 "모든 쓰기를 비동기"로 두기보다, 도메인별로 확정 수준을 분리하는 것이 일반적입니다.

예를 들어 결제 원장은 동기, 클릭 로그는 비동기로 분리하면 사용자 체감 성능과 데이터 안전성을 동시에 맞출 수 있습니다.

### 체인 복제 패턴: 순서 보장과 읽기 일관성

체인 복제(chain replication)는 복제본을 선형 체인으로 두고, 쓰기는 헤드(head)에서 받아 테일(tail)까지 전달한 뒤 테일 확인을 기준으로 확정합니다. 읽기는 보통 테일에서 수행해 최신 커밋 값을 얻습니다.

```text
Client Write
   |
   v
 [Head] -> [Middle] -> [Tail]
    |         |          |
    +---------+----------+
          ack after Tail persist

Client Read -> [Tail]
```

장점은 명확합니다.

- 쓰기 순서가 체인 순서로 강제되어 충돌 해석이 단순합니다.
- 최신 읽기 경로를 Tail로 고정하면 stale read 위험을 구조적으로 낮출 수 있습니다.
- 노드 장애 시 체인 재구성이 명시적이라 런북 자동화가 쉽습니다.

단점도 분명합니다.

- Tail이 읽기 병목이 될 수 있습니다.
- 체인이 길어질수록 쓰기 지연이 누적됩니다.
- 중간 노드 장애 때 재연결 동안 처리율이 일시 저하됩니다.

실무에서는 "핫키가 많은 쓰기 중심 워크로드"에 체인 복제를 적용하고, 읽기 부하는 캐시 또는 스냅샷 팔로워로 보완하는 조합을 자주 사용합니다.

### 복제 지연을 Prometheus로 계량화하기

복제 지연은 감으로 보지 않고 메트릭으로 다뤄야 합니다. 아래 예시는 리더 LSN과 팔로워 LSN 차이를 게이지로 노출하고, 최근 적용 시각 차이를 초 단위로 계산합니다.

```python
# replication_metrics.py
import time
from fastapi import FastAPI, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest

app = FastAPI()
registry = CollectorRegistry()

replication_lag_lsn = Gauge(
    "replication_lag_lsn",
    "Leader and follower LSN gap",
    ["cluster", "follower"],
    registry=registry,
)

replication_apply_delay_seconds = Gauge(
    "replication_apply_delay_seconds",
    "Delay between leader commit time and follower apply time",
    ["cluster", "follower"],
    registry=registry,
)

state = {
    "leader_lsn": 120500,
    "followers": {
        "follower-a": {"lsn": 120460, "applied_at": time.time() - 1.2},
        "follower-b": {"lsn": 120430, "applied_at": time.time() - 2.8},
    },
}

def refresh_replication_metrics(cluster: str = "orders-prod") -> None:
    leader_lsn = state["leader_lsn"]
    now = time.time()
    for name, follower in state["followers"].items():
        lag = leader_lsn - follower["lsn"]
        apply_delay = max(now - follower["applied_at"], 0)
        replication_lag_lsn.labels(cluster=cluster, follower=name).set(lag)
        replication_apply_delay_seconds.labels(cluster=cluster, follower=name).set(apply_delay)

@app.get("/metrics")
def metrics():
    refresh_replication_metrics()
    payload = generate_latest(registry)
    return Response(content=payload, media_type="text/plain; version=0.0.4")
```

메트릭만 수집하면 끝이 아닙니다. 경보 기준까지 같이 고정해야 합니다.

```yaml
groups:
  - name: replication-alerts
    rules:
      - alert: ReplicationLagCritical
        expr: replication_lag_lsn{cluster="orders-prod"} > 5000
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "복제 LSN 지연이 임계치를 초과했습니다"
      - alert: ReplicationApplyDelayHigh
        expr: replication_apply_delay_seconds{cluster="orders-prod"} > 5
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "팔로워 적용 지연이 5초를 초과했습니다"
```

이렇게 두 축(LSN gap, apply delay)을 같이 보면 "로그는 빨리 따라오는데 적용이 느린 상황"과 "전송 자체가 지연되는 상황"을 분리해 원인을 찾을 수 있습니다.

### 장애 조치와 승격 패턴

리더 장애 시 가장 위험한 상황은 "오래된 팔로워를 새 리더로 승격"하는 경우입니다. 승격 대상 선정은 단순 생존 여부가 아니라 최신성, 동기 복제 참여 여부, 네트워크 건강 상태를 함께 봐야 합니다.

아래는 운영 문서에 바로 넣을 수 있는 승격 정책 예시입니다.

```yaml
failover_policy:
  cluster: orders-prod
  promotion:
    min_candidate_count: 2
    require_sync_replica: true
    max_allowed_lag_lsn: 200
    max_allowed_apply_delay_seconds: 1
  split_brain_guard:
    fencing: required
    method: disable_old_leader_write_via_stonith
  recovery:
    rejoin_old_leader_as_follower: true
    full_resync_if_lag_lsn_gt: 50000
```

핵심 운영 원칙은 네 가지입니다.

1. **펜싱 우선**: 기존 리더의 쓰기 경로를 먼저 차단하고 새 리더를 열어 split-brain을 막습니다.
2. **최신성 우선 승격**: lag 임계치 안의 팔로워만 후보로 두어 데이터 회귀를 줄입니다.
3. **역할 전환 후 검증**: 승격 직후 read-after-write 검사와 핵심 테이블 카운트 검사를 자동 실행합니다.
4. **구 리더 재합류 절차 고정**: 구 리더는 즉시 재리더화하지 않고 팔로워 재동기화부터 수행합니다.

아래와 같은 최소 점검 스크립트를 런북에 두면 사람 의존 오류를 줄일 수 있습니다.

```shell
# failover-check.sh
python3 scripts/check_leader_health.py --cluster orders-prod
python3 scripts/check_replication_lag.py --cluster orders-prod --max-lag-lsn 200
python3 scripts/promote_replica.py --cluster orders-prod --candidate follower-a
python3 scripts/verify_read_after_write.py --cluster orders-prod
```

중요한 점은 자동화 자체보다 "승격 전/중/후 검증 항목"이 고정되어 있어야 한다는 것입니다. 이 고정점이 있어야 야간 장애에서도 동일한 품질로 대응할 수 있습니다.

### 읽기 일관성 전략: stale read를 의도적으로 다루기

복제본에서 읽을 때 가장 큰 위험은 "모르는 사이에 stale read가 사용자에게 노출되는 것"입니다. 이를 방지하려면 읽기 경로를 의도적으로 설계해야 합니다.

```python
# read_consistency.py
from enum import Enum
from fastapi import FastAPI, Query

app = FastAPI()

class ReadConsistency(str, Enum):
    STRONG = "strong"       # leader에서만 읽음
    BOUNDED = "bounded"     # 최대 N초 이내 stale 허용
    EVENTUAL = "eventual"   # 아무 복제본에서 읽음

@app.get("/items/{key}")
async def read_item(key: str, consistency: ReadConsistency = Query(default=ReadConsistency.BOUNDED)):
    if consistency == ReadConsistency.STRONG:
        return await read_from_leader(key)
    elif consistency == ReadConsistency.BOUNDED:
        follower = select_follower_within_lag(max_lag_seconds=2)
        return await read_from_node(follower, key)
    else:
        follower = select_any_healthy_follower()
        return await read_from_node(follower, key)
```

이 패턴의 핵심은 읽기 일관성을 API 인터페이스 수준에서 노출하는 것입니다. 호출자가 자신의 워크로드에 맞는 수준을 선택할 수 있으면, 시스템 전체를 strong consistency로 올릴 필요 없이 대부분의 읽기를 복제본으로 분산할 수 있습니다.

운영에서 흔히 보는 조합은 다음과 같습니다.

| 워크로드 | 일관성 수준 | 이유 |
| --- | --- | --- |
| 결제 잔액 조회 | strong | 실시간 정확성 필수 |
| 대시보드 목록 | bounded (2초) | 약간의 지연은 허용, 부하 분산 필요 |
| 추천 피드 | eventual | 수 초 stale도 사용자 불만 없음 |
| 관리자 감사 로그 | strong | 최신 이벤트 누락 불가 |

bounded staleness에서 `max_lag_seconds`를 어떻게 결정하느냐가 자주 나오는 질문입니다. 답은 "사용자가 인지하는 불일치 허용 시간"에서 출발합니다. 대시보드라면 새로고침 주기(보통 5~30초)보다 짧으면 충분하고, 실시간 채팅이라면 수백 밀리초 이내여야 합니다.

### 복제본 건강 점검과 자동 제외

복제 지연이 임계치를 넘은 팔로워는 읽기 풀에서 자동으로 빠져야 합니다. 그렇지 않으면 특정 사용자만 반복적으로 stale 응답을 받는 "운 나쁜 요청" 문제가 생깁니다.

```python
# follower_health.py
import time

FOLLOWER_STATUS = {
    "follower-a": {"lag_seconds": 0.8, "last_check": time.time()},
    "follower-b": {"lag_seconds": 4.2, "last_check": time.time()},
    "follower-c": {"lag_seconds": 1.1, "last_check": time.time()},
}

MAX_ACCEPTABLE_LAG = 3.0  # seconds

def healthy_followers() -> list[str]:
    return [
        name for name, status in FOLLOWER_STATUS.items()
        if status["lag_seconds"] <= MAX_ACCEPTABLE_LAG
    ]

def select_follower_within_lag(max_lag_seconds: float) -> str:
    candidates = [
        name for name, status in FOLLOWER_STATUS.items()
        if status["lag_seconds"] <= max_lag_seconds
    ]
    if not candidates:
        return "leader"  # fallback to leader
    return min(candidates, key=lambda n: FOLLOWER_STATUS[n]["lag_seconds"])
```

이 코드에서 중요한 결정은 `candidates`가 비었을 때 leader로 fallback하는 부분입니다. 모든 팔로워가 지연 임계치를 넘기면 읽기를 거부하는 대신 leader로 보내되, 이 fallback 비율 자체를 모니터링해야 합니다. leader fallback이 급증하면 복제 인프라 문제의 신호이기 때문입니다.

## 처음 질문으로 돌아가기

- **왜 데이터를 복제하며, 어떤 복제 모델이 있을까요?**
  - 복제의 목적은 단순 백업이 아니라 장애 허용, 읽기 확장, 지역 분산을 동시에 달성하기 위해서입니다. 본문에서 본 것처럼 leader-follower는 운영 단순성과 예측 가능한 쓰기 경로가 강점이고, multi-leader는 다중 쓰기 지점이 필요한 환경에 유리하며, leaderless는 쿼럼으로 가용성과 분산 쓰기를 확보하는 데 적합합니다. 여기에 일관 해싱을 결합하면 노드 증감 시 재배치 비용까지 통제할 수 있습니다.
- **leader-follower, multi-leader, leaderless는 어떻게 다를까요?**
  - leader-follower는 리더를 단일 진실 원천으로 두어 충돌 처리가 단순하지만 리더 장애 대응이 중요합니다. multi-leader는 쓰기 지점이 여러 개라 지역 독립성이 좋지만 충돌 해석 규칙을 애플리케이션이 가져가야 합니다. leaderless는 모든 노드가 대등하고 R/W/N 조합으로 읽기·쓰기 보장을 조절하며, 최신성 관리는 쿼럼과 read repair 정책이 핵심입니다.
- **동기 복제와 비동기 복제는 어떤 데이터 손실 위험을 만들까요?**
  - 동기 복제는 응답 전에 다수 복제본 반영을 기다려 리더 직후 장애에서도 손실 위험이 낮은 대신 지연이 늘어납니다. 비동기 복제는 빠른 응답을 주지만 전파 전 장애가 나면 최근 쓰기를 잃을 수 있습니다. 그래서 본문에서 다룬 것처럼 도메인별로 동기/비동기를 분리하고, Prometheus 기반 lag 지표와 승격 임계치를 함께 운영해야 실제 손실 위험을 관리할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC와 메시지 전달](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): 일관성과 CAP](./04-consistency-and-cap.md)
- **복제 (현재 글)**
- 합의와 Raft (예정)
- 리더 선출 (예정)
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Replication (computing) — Wikipedia](https://en.wikipedia.org/wiki/Replication_(computing))
- [Quorum (distributed computing) — Wikipedia](https://en.wikipedia.org/wiki/Quorum_(distributed_computing))
- [Amazon Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Designing Data-Intensive Applications — chapter 5](https://dataintensive.net/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, Replication, LeaderFollower, QuorumWrites, Durability
