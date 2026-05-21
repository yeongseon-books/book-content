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

이 글은 Distributed Systems 101 시리즈의 다섯 번째 글입니다.

여기서는 복제를 저장소의 뒷단 구현이 아니라, 시스템이 사용자에게 약속하는 안전성과 지연 특성을 결정하는 설계 레이어로 봅니다.

## 먼저 던지는 질문

- 왜 데이터를 복제하며, 어떤 복제 모델이 있을까요?
- leader-follower, multi-leader, leaderless는 어떻게 다를까요?
- 동기 복제와 비동기 복제는 어떤 데이터 손실 위험을 만들까요?

## 큰 그림

![Distributed Systems 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/05/05-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 5장 흐름 개요*

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

## Before / After

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


## 실전 설계 확장: 합의, CAP, 메시지 큐 운영

분산 시스템을 실제로 운영할 때는 "요청을 받았다"보다 "요청이 어느 경계에서 확정되었는가"를 더 먼저 확인해야 합니다. 이유는 단순합니다. 네트워크 지연과 부분 장애가 존재하면 성공/실패 이분법으로 상태를 설명할 수 없고, 노드별 관측 시점이 달라 같은 사건을 다르게 기록할 수 있기 때문입니다. 따라서 설계 문서에는 기능 설명뿐 아니라 합의 규칙, 파티션 시 동작 규칙, 큐 처리 규칙이 함께 들어가야 운영에서 재현 가능한 판단이 가능합니다.

### 합의 알고리즘을 어디에 쓰는가

합의 알고리즘은 이론 주제가 아니라 운영 안전장치입니다. 예를 들어 주문 서비스의 리더 노드가 동시에 두 개 생기면, 같은 주문 번호에 서로 다른 상태가 기록될 수 있습니다. 이때 Raft 같은 리더 기반 합의는 "현재 임기의 과반이 인정한 리더만 쓰기 가능"이라는 제약으로 이중 기록을 막습니다.

```text
노드 5개 구성에서 과반수는 3개입니다.
리더가 쓰기를 확정하려면 최소 3개 노드에 로그가 복제되어야 합니다.
2개 노드만 성공한 쓰기는 클라이언트 성공 응답으로 확정하면 안 됩니다.
```

실무 문서에 반드시 적어야 하는 항목은 다음과 같습니다.

- 리더 선출 타임아웃 범위(예: 150ms~300ms 랜덤)
- 하트비트 간격(예: 50ms)
- 로그 확정 기준(과반 복제 이후 commit)
- 장애 복구 시 재조인 절차(스냅샷/로그 재동기화)

이 네 가지를 수치로 고정하면, 장애 대응 중에 팀원마다 다른 가정을 들고 판단하는 상황을 줄일 수 있습니다.

### CAP을 선언으로 끝내지 않고 시나리오로 적기

"우리 시스템은 AP" 같은 문장은 운영에서 거의 도움이 되지 않습니다. 어떤 API가 파티션 중에도 쓰기를 받는지, 읽기 결과가 얼마나 오래 뒤처질 수 있는지를 함께 정의해야 합니다.

예시로 재고 서비스의 파티션 정책을 문서화하면 아래처럼 표현할 수 있습니다.

```yaml
service: inventory
partition_policy:
  write:
    mode: reject_when_no_quorum
    http_status: 503
  read:
    mode: allow_stale_read
    max_staleness_seconds: 5
recovery_policy:
  reconcile: last_write_wins_with_version_check
  audit_log_required: true
```

위 정책의 의미는 명확합니다. 네트워크가 갈라졌을 때 쓰기를 무조건 받지 않고, 읽기는 최대 5초까지 오래된 값을 허용합니다. 대신 복구 후에는 버전 검증과 감사 로그 기반으로 충돌을 정리합니다. CAP 선택은 이렇게 엔드포인트별 동작과 관측 지표로 내려와야 실제 운영 정책이 됩니다.

### 메시지 큐 설정은 처리량보다 재처리 안전성을 먼저 본다

메시지 큐를 도입하면 비동기로 느슨한 결합을 얻지만, 동시에 중복 처리와 순서 역전이 기본 위험이 됩니다. 큐 설정에서 가장 먼저 다룰 항목은 처리량이 아니라 "실패한 메시지를 어떻게 안전하게 다시 처리할 것인가"입니다.

아래는 RabbitMQ 스타일의 실무 기본 설정 예시입니다.

```yaml
queue:
  name: order.events
  durable: true
  arguments:
    x-dead-letter-exchange: order.dlx
    x-message-ttl: 60000
consumer:
  prefetch_count: 20
  ack_mode: manual
  retry:
    max_attempts: 5
    backoff_ms: 200
idempotency:
  key_source: event_id
  ttl_seconds: 86400
```

핵심은 세 가지입니다.

- `durable: true`로 브로커 재시작 후에도 큐 정의를 유지합니다.
- `manual ack`로 실제 처리 완료 후에만 확인 응답을 보냅니다.
- `event_id` 기반 멱등성 저장소를 두어 중복 전달을 결과 중복으로 이어지지 않게 막습니다.

Kafka를 쓰는 경우도 원칙은 같습니다. 파티션 키를 어떻게 잡아 순서를 보존할지, 커밋 시점을 처리 성공 이후로 둘지, DLQ 토픽을 어떻게 운영할지를 문서로 고정해야 장애 시간에 판단 비용을 줄일 수 있습니다.

### 장애 주입 기반 검증 루프

설계를 문서로만 두면 시간이 지나며 가정이 깨집니다. 그래서 운영 전 검증 루프를 습관화해야 합니다.

1. 리더 노드 강제 종료: 선출 시간과 요청 오류율을 측정합니다.
2. 네트워크 지연 주입: p95/p99 지연과 타임아웃 비율을 기록합니다.
3. 큐 소비자 중단: 적체량 증가 속도와 복구 시간을 측정합니다.
4. 중복 메시지 재주입: 멱등성 키로 결과 중복이 차단되는지 확인합니다.

이 검증을 CI 야간 작업이나 스테이징 런북에 포함하면, 새 기능이 들어와도 합의/CAP/큐 운영 규칙이 계속 살아 있는지 지속적으로 확인할 수 있습니다.

### 운영 대시보드에서 반드시 보는 지표

- 합의 계층: 리더 변경 횟수, 선출 소요 시간, 로그 복제 지연
- 요청 계층: 성공률, 타임아웃률, 재시도 횟수, 멱등성 충돌률
- 큐 계층: consumer lag, DLQ 유입량, 재처리 성공률
- 데이터 계층: 복제 지연, 버전 충돌 건수, 보정 작업 처리량

지표를 계층별로 보면 "느리다"라는 증상을 "리더 불안정 때문에 재시도가 폭증했다"처럼 원인 단위로 분해할 수 있습니다. 분산 시스템 운영 성숙도는 결국 이 분해 능력에서 드러납니다.




### 추가 운영 예시: 쿼럼 손실과 복구 절차

쿼럼이 깨진 순간에는 "일단 쓰기를 받고 나중에 맞춘다"보다 "확정 가능한 쓰기만 받는다"를 기본값으로 두는 편이 안전합니다. 예를 들어 5노드 클러스터에서 2노드만 살아 있으면 새로운 쓰기는 거절하고, 읽기는 최신성 등급을 함께 내려 사용자와 상위 서비스가 의사결정을 할 수 있게 해야 합니다.

```yaml
degraded_mode:
  quorum_required: 3
  write_policy: reject
  read_policy:
    allow: true
    staleness_label: required
  response_headers:
    X-Consistency-Level: stale-possible
```

복구 시에는 아래 순서를 런북으로 고정해 두는 것이 좋습니다. 첫째, 리더 안정화 여부 확인. 둘째, 복제 지연이 임계치 아래로 내려왔는지 확인. 셋째, 큐 적체가 해소되었는지 확인. 넷째, 그 뒤에만 쓰기 트래픽 제한을 해제합니다. 이 순서가 바뀌면 겉보기 정상화 뒤에 데이터 불일치가 남을 가능성이 커집니다.

## 처음 질문으로 돌아가기

- **왜 데이터를 복제하며, 어떤 복제 모델이 있을까요?**
  - 본문의 기준은 복제를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **leader-follower, multi-leader, leaderless는 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **동기 복제와 비동기 복제는 어떤 데이터 손실 위험을 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, Distributed Systems, Replication, LeaderFollower, QuorumWrites, Durability
