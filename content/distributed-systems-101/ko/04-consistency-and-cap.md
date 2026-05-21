---
series: distributed-systems-101
episode: 4
title: "Distributed Systems 101 (4/10): 일관성과 CAP"
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
  - Consistency
  - CAP
  - Linearizability
  - Eventual Consistency
seo_description: 일관성 스펙트럼과 CAP, PACELC를 한 번에 읽는 기준을 정리합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (4/10): 일관성과 CAP

데이터가 한 군데에만 있을 때는 "최신값을 읽는다"는 말이 별일 아닙니다. 하지만 복제본이 둘 이상이 되는 순간부터는 어느 복제본을 읽는지, 파티션 중 무엇을 포기하는지에 따라 그 문장이 완전히 다른 뜻을 갖게 됩니다.

이 글은 Distributed Systems 101 시리즈의 네 번째 글입니다.

여기서는 일관성 모델을 스펙트럼으로 보고, CAP와 PACELC를 통해 설계 문서와 데이터베이스 문장을 읽는 기준을 만듭니다.

## 먼저 던지는 질문

- 여기서 말하는 일관성은 정확히 무엇이며 트랜잭션의 C와 어떻게 다를까요?
- linearizable, sequential, causal, eventual은 어떤 스펙트럼을 이룰까요?
- CAP 정리는 무엇을 말하며, 어디서 자주 오해될까요?

## 큰 그림

![Distributed Systems 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/04/04-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 4장 흐름 개요*

## 왜 중요한가

데이터베이스가 강한 일관성을 가진다, eventual consistency에 가깝다 같은 한 줄 설명은 설계 전체를 바꿉니다. 어떤 화면을 만들 수 있는지, 재시도 정책을 어떻게 둘지, 장애 시 어떤 동작을 허용할지가 모두 여기서 갈립니다. 이 언어를 모르면 데이터베이스 문서를 읽을 때 핵심을 놓치게 됩니다.

> 일관성 모델은 데이터가 맺는 사회적 계약입니다.

## 한눈에 보는 개념

왼쪽으로 갈수록 직관적이지만 비싸고, 오른쪽으로 갈수록 싸고 가용성이 높지만 직관에서 멀어집니다.

## 핵심 용어

- **Linearizability**: 시스템 전체가 하나의 시간선 위에서 동작하는 것처럼 보이는 모델입니다.
- **Sequential consistency**: 모든 노드가 같은 순서를 보지만, 실제 시간 순서까지 보장하지는 않는 모델입니다.
- **Causal consistency**: 인과적으로 연결된 연산의 순서만 보존하는 모델입니다.
- **Eventual consistency**: 충분한 시간이 지나면 모든 복제본이 같은 상태로 수렴하는 모델입니다.
- **CAP**: 파티션 중에는 일관성과 가용성을 동시에 끝까지 지킬 수 없다는 정리입니다.

## Before / After

**Before — 데이터베이스가 알아서 정하겠지**

```text
defaults silently chosen -> races and stale reads in production
```

**After — 모델을 명시적으로 선택**

```text
orders/payments -> linearizable, feeds/recommendations -> eventual
```

화면과 데이터셋별로 비용을 다르게 배분할 수 있습니다.

## 실습: 코드로 보는 일관성 모델

### 1단계 — 단일 노드(linearizable의 기준점)

```python
# 1_single.py
log = []
def write(x): log.append(x)
def read(): return log[-1] if log else None
```

단일 노드에서는 모든 읽기가 최신 쓰기를 봅니다. 우리가 직관이라고 부르는 감각의 출발점입니다.

### 2단계 — 비동기 복제본(eventual)

```python
# 2_eventual.py
import threading, time
primary = []
replica = []
def write(x):
    primary.append(x)
    threading.Thread(target=lambda: (time.sleep(0.5), replica.append(x))).start()
def read_primary(): return primary[-1] if primary else None
def read_replica(): return replica[-1] if replica else None
```

방금 쓴 값이 반대편 복제본에서는 0.5초 동안 보이지 않습니다. 이 코드 조각 하나가 eventual consistency의 본질을 보여 줍니다.

### 3단계 — read-your-writes 흉내 내기

```python
# 3_ryw.py
session_writes = {}
def write(uid, x):
    primary.append(x); session_writes[uid] = x
def read(uid):
    if uid in session_writes:
        return session_writes[uid]   # users see their own writes immediately
    return read_replica()
```

약한 모델 위에 더 강한 사용자 경험 보장을 얹는 대표적인 방식입니다.

### 4단계 — 파티션 시뮬레이션(CAP 선택)

```python
# 4_partition.py (pseudocode)
def write(x):
    if not majority_alive():
        # CP: refuse
        raise Exception("no majority")
        # AP: accept locally and merge later
```

두 줄의 차이가 CP와 AP를 갈라놓습니다.

### 5단계 — causal consistency 흉내 내기

```python
# 5_vector.py
clock = {"A":0, "B":0}
def tick(node): clock[node] += 1
def happens_before(a, b):
    return all(a[k] <= b[k] for k in a) and any(a[k] < b[k] for k in a)
```

인과 일관성은 happens-before 관계만 보존하면 됩니다. 서로 독립적인 동시 사건은 어떤 순서로 보여도 괜찮습니다.

## 이 코드에서 먼저 봐야 할 점

- 일관성은 이분법이 아니라 스펙트럼입니다.
- 같은 시스템 안에서도 화면이나 데이터셋마다 다른 모델을 선택할 수 있습니다.
- read-your-writes는 약한 모델에서 사용자 경험을 지키는 핵심 기술입니다.
- 파티션 중 CP와 AP를 고르는 일은 자동이 아니라 정책 결정입니다.

## 자주 하는 실수 5가지

1. **CAP의 C를 ACID의 C와 혼동합니다.** 두 개념은 다릅니다.
2. **시스템 전체를 한 단어로 CP라고 부릅니다.** 같은 시스템 안에서도 호출별 정책이 다를 수 있습니다.
3. **eventual을 곧바로, 금방으로 읽습니다.** 이 보장은 시간 상한을 주지 않습니다.
4. **read-your-writes가 자동이라고 생각합니다.** 직접 구현해야 합니다.
5. **파티션을 무시한 채 강한 일관성을 약속합니다.** 운영에서 곧바로 깨집니다.

## 실무에서는 이렇게 드러납니다

Spanner, etcd, ZooKeeper는 linearizable에 가깝게 동작하는 CP 계열입니다. DynamoDB, Cassandra, Redis Cluster는 기본적으로 eventual에 가까운 AP 성향을 가집니다. 같은 회사 안에서도 결제 시스템은 CP, 추천 캐시는 AP를 선택하는 경우가 흔합니다. PACELC는 파티션이 없는 평상시에도 지연과 일관성 사이의 비용을 보게 해 줍니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 시스템 전체가 아니라 화면과 경로별로 모델을 매핑합니다.
- read-your-writes를 sticky session 같은 방식으로 명시적으로 제공합니다.
- 파티션 정책을 운영 책임의 일부로 다룹니다.
- 강한 일관성의 비용을 SLO로 측정합니다.
- 모델이 이름 붙어 있지 않은 문서는 신뢰하지 않습니다.

## 체크리스트

- [ ] linearizable과 eventual의 차이를 한 줄로 말할 수 있는가?
- [ ] 파티션이 없을 때 CAP를 어떻게 이해해야 하는지 설명할 수 있는가?
- [ ] 시스템의 주요 화면을 일관성 모델에 매핑할 수 있는가?
- [ ] read-your-writes를 어떻게 구현할지 설명할 수 있는가?
- [ ] PACELC의 ELC가 무엇을 뜻하는지 알고 있는가?

## 연습 문제

1. 서비스의 핵심 데이터셋 세 개를 골라 linearizable, causal, eventual 중 어디에 놓을지 정해 보세요.
2. eventual consistency 시스템에서 read-your-writes를 보장하는 설계를 해 보세요.
3. 파티션 중 CP와 AP 중 무엇을 고를지, 그리고 왜 그런지 적어 보세요.

## 정리와 다음 글

일관성 모델은 데이터를 분산한 뒤 가장 중요한 트레이드오프 축입니다. 다음 글에서는 그 선택의 직접적 원인이 되는 복제 방식, 즉 replication과 동기/비동기 복제를 다룹니다.


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

- **여기서 말하는 일관성은 정확히 무엇이며 트랜잭션의 C와 어떻게 다를까요?**
  - 본문의 기준은 일관성과 CAP를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **linearizable, sequential, causal, eventual은 어떤 스펙트럼을 이룰까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **CAP 정리는 무엇을 말하며, 어디서 자주 오해될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC와 메시지 전달](./03-rpc-and-message-passing.md)
- **일관성과 CAP (현재 글)**
- 복제 (예정)
- 합의와 Raft (예정)
- 리더 선출 (예정)
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [CAP theorem (Wikipedia)](https://en.wikipedia.org/wiki/CAP_theorem)
- [Consistency model (Wikipedia)](https://en.wikipedia.org/wiki/Consistency_model)
- [PACELC theorem (Wikipedia)](https://en.wikipedia.org/wiki/PACELC_theorem)
- [Designing Data-Intensive Applications — chapter 9](https://dataintensive.net/)

Tags: Computer Science, Distributed Systems, Consistency, CAP, Linearizability, Eventual Consistency
