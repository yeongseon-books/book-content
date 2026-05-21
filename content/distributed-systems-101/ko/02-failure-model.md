---
series: distributed-systems-101
episode: 2
title: "Distributed Systems 101 (2/10): 장애 모델"
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
  - Failure Models
  - Crash
  - Byzantine
  - Reliability
seo_description: 장애 모델을 crash, omission, timing, Byzantine으로 구분해 봅니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (2/10): 장애 모델

운영 채널에서 "서버가 죽었습니다"라고 말할 때, 실제로는 여러 종류의 사건이 한 문장에 섞여 있습니다. 프로세스가 멈춘 것인지, 패킷이 빠지는 것인지, 아니면 너무 느려서 살아 있어도 죽은 것처럼 보이는 것인지부터 갈라야 설계가 흔들리지 않습니다.

이 글은 Distributed Systems 101 시리즈의 두 번째 글입니다.

여기서는 crash, omission, timing, Byzantine을 설계 언어로 정리하고, 뒤이어 나오는 CAP와 합의 이야기가 어떤 가정 위에 서는지 분명히 잡습니다.

## 먼저 던지는 질문

- 장애 모델이란 무엇이며 왜 장애를 모델링해야 할까요?
- crash, omission, timing, Byzantine은 어떻게 다를까요?
- 네트워크 파티션은 왜 별도 범주로 봐야 할까요?

## 큰 그림

![Distributed Systems 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/02/02-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 2장 흐름 개요*

## 왜 중요한가

알고리즘이 노드가 어떤 방식으로 망가지는지를 명시하지 않으면 정확성도 비용도 말할 수 없습니다. Raft, Paxos, BFT 계열 알고리즘이 서로 다른 이유는 각자가 전제하는 장애 모델이 다르기 때문입니다. 이 어휘를 모르면 논문도 문서도 절반밖에 읽히지 않습니다.

> 장애 모델은 알고리즘의 가격표입니다.

## 한눈에 보는 개념

오른쪽으로 갈수록 더 험한 세계를 가정합니다. 세계가 험해질수록 알고리즘은 더 비싸지고 더 많은 노드를 요구합니다.

## 핵심 용어

- **Crash (fail-stop)**: 노드가 멈추면 그대로 멈춘 상태로 남는 모델입니다.
- **Omission**: 노드가 가끔 메시지를 빠뜨리거나 누락하는 모델입니다.
- **Timing**: 노드의 응답이 임의로 매우 느려질 수 있는 모델입니다.
- **Byzantine**: 노드가 거짓말하거나 임의의 행동을 할 수 있는 모델입니다.
- **Network partition**: 노드 자체가 아니라 노드 사이 링크가 끊기는 상태입니다.

## Before / After

**Before — 그냥 죽었다고만 가정**

```text
treating every failure the same forces algorithms to over-pay
```

**After — 장애 모델을 명시적으로 선택**

```text
crash only -> Raft / Paxos
byzantine  -> BFT (an order of magnitude more expensive)
```

가정이 달라지면 비용도 달라집니다.

## 실습: 장애를 각각 흉내 내 보기

### 1단계 — crash 시뮬레이션

```python
# 1_crash.py
import os, sys
def handler():
    print("doing work")
    os._exit(1)  # cleanly dies
handler()
```

이 모델에서는 다른 노드가 한 번 죽은 노드는 계속 죽어 있다고 가정합니다. 따라서 장애 감지기가 비교적 단순합니다.

### 2단계 — omission 시뮬레이션

```python
# 2_omission.py
import random
def send(msg):
    if random.random() < 0.1:
        return  # drop with 10% probability
    transport.send(msg)
```

이 시점부터는 재시도, 시퀀스 번호, 확인 응답이 필요해집니다.

### 3단계 — timing(느림) 시뮬레이션

```python
# 3_slow.py
import time, random
def handle(req):
    if random.random() < 0.05:
        time.sleep(10)  # 5% chance of being very slow
    return process(req)
```

밖에서 보기에는 느린 노드와 죽은 노드가 거의 똑같아 보입니다. 이것이 타임아웃 기반 장애 감지의 근본적인 한계입니다.

### 4단계 — Byzantine 동작 시뮬레이션

```python
# 4_byzantine.py
def vote(question):
    real_answer = compute(question)
    return not real_answer if is_malicious() else real_answer
```

이 모델에서는 단순 다수결만으로는 충분하지 않습니다. 서명된 메시지나 3f+1 같은 더 비싼 구조가 필요합니다.

### 5단계 — 네트워크 파티션 시뮬레이션

```bash
# 5_partition.sh (linux)
sudo iptables -A INPUT -s 10.0.0.5 -j DROP
sudo iptables -A OUTPUT -d 10.0.0.5 -j DROP
# restore
sudo iptables -F
```

파티션은 노드는 살아 있지만 서로를 볼 수 없는 상태입니다. 4편의 CAP는 바로 이 상황을 중심으로 전개됩니다.

## 이 코드에서 먼저 봐야 할 점

- 같은 장애처럼 보여도 실제로는 종류와 대응 방식이 다릅니다.
- 메시지 누락과 지연 장애는 타임아웃으로만 가늠할 수 있고, 그 판단도 완전하지 않습니다.
- Byzantine 모델은 비용을 한 단계가 아니라 한 자릿수 이상 끌어올립니다.
- 파티션은 노드 레벨이 아니라 링크 레벨에서 일어나는 사건입니다.

## 자주 하는 실수 5가지

1. **모든 장애를 crash로만 가정합니다.** 네트워크가 부분적으로 끊기면 알고리즘이 잘못 수렴할 수 있습니다.
2. **타임아웃을 너무 짧게 잡습니다.** 살아 있는 노드를 죽었다고 오판합니다.
3. **모든 곳에 Byzantine 모델을 들이댑니다.** 비용이 급격히 커집니다.
4. **파티션을 무시합니다.** 클라우드 환경에서는 일상적으로 일어나는 사건입니다.
5. **완벽한 장애 감지기를 기대합니다.** 비동기 모델에서는 완벽한 감지기가 불가능합니다.

## 실무에서는 이렇게 드러납니다

대부분의 인터넷 서비스는 crash와 partition을 중심에 둔 CFT 모델을 전제로 합니다. 금융이나 블록체인 계열은 Byzantine까지 고려하는 BFT 계열을 선택합니다. Kubernetes, Spanner, Cassandra 같은 시스템의 설계 문서를 보면 어떤 장애 모델을 겨냥했는지가 분명히 적혀 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 필요한 수준을 넘는 강한 가정을 피하고, 충분히 약한 가정의 알고리즘을 고릅니다.
- 장애 감지기는 언제나 근사치라는 사실을 전제로 둡니다.
- 파티션을 예외가 아니라 상수처럼 다룹니다.
- 타임아웃 값은 네트워크 측정값을 기준으로 정합니다.
- 장애 모델이 명시되지 않은 문서나 제품 설명은 곧바로 경계합니다.

## 체크리스트

- [ ] crash와 omission의 차이를 한 줄로 말할 수 있는가?
- [ ] Byzantine이 왜 더 비싼지 설명할 수 있는가?
- [ ] 파티션이 노드 장애와 어떻게 다른지 말할 수 있는가?
- [ ] 타임아웃 기반 감지가 왜 불완전한지 알고 있는가?
- [ ] 우리 시스템이 어떤 장애 모델을 가정하는지 답할 수 있는가?

## 연습 문제

1. 여러분의 서비스가 crash, omission, Byzantine 중 무엇을 전제로 하는지 적어 보세요.
2. 타임아웃 값을 정하기 위해 반드시 측정해야 할 지표 두 가지를 적어 보세요.
3. 파티션이 발생했을 때 split-brain을 막는 메커니즘 하나를 조사해 보세요.

## 정리와 다음 글

장애 모델은 가장 먼저 내려야 하는 설계 결정입니다. 이 결정이 알고리즘과 운영 비용을 함께 정합니다. 다음 글에서는 이런 장애 모델 위에서 노드들이 실제로 어떻게 통신하는지, 즉 RPC와 메시지 전달을 살펴보겠습니다.


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



추가로, 장애 조치 연습은 분기별 1회가 아니라 배포 주기 안으로 넣어야 효과가 큽니다. 배포 전 체크에 리더 재선출, 큐 재처리, stale read 경고 노출 검증을 포함하면 운영 중 최초 발견 리스크를 크게 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **장애 모델이란 무엇이며 왜 장애를 모델링해야 할까요?**
  - 본문의 기준은 장애 모델를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **crash, omission, timing, Byzantine은 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **네트워크 파티션은 왜 별도 범주로 봐야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- **장애 모델 (현재 글)**
- RPC와 메시지 전달 (예정)
- 일관성과 CAP (예정)
- 복제 (예정)
- 합의와 Raft (예정)
- 리더 선출 (예정)
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Failure semantics (Wikipedia)](https://en.wikipedia.org/wiki/Failure_semantics)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
- [Network partition (Wikipedia)](https://en.wikipedia.org/wiki/Network_partition)
- [Designing Data-Intensive Applications — chapter 8](https://dataintensive.net/)

Tags: Computer Science, Distributed Systems, Failure Models, Crash, Byzantine, Reliability
