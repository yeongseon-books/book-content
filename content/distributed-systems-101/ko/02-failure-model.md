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


![Distributed Systems 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/02/02-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 2장 흐름 개요*

## 먼저 던지는 질문

- 장애 모델이란 무엇이며 왜 장애를 모델링해야 할까요?
- crash, omission, timing, Byzantine은 어떻게 다를까요?
- 네트워크 파티션은 왜 별도 범주로 봐야 할까요?

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

## 장애 모델 스펙트럼: 약한 가정에서 강한 가정으로

장애 모델은 스펙트럼으로 이해하는 것이 가장 정확합니다. 왼쪽이 가장 약한 가정(노드는 멈추기만 함)이고, 오른쪽이 가장 강한 가정(노드가 거짓말을 함)입니다.

```text
Crash (fail-stop)  ⊂  Crash-recovery  ⊂  Omission  ⊂  Timing  ⊂  Byzantine
────────────────────────────────────────────────────────────────────
약한 가정 (cheap)  ────────────────────────────────→  강한 가정 (expensive)
```

각 단계는 이전 단계를 포함합니다. Byzantine 모델을 견디는 알고리즘은 crash도 당연히 견딥니다. 하지만 비용이 너무 높기 때문에, 실무에서는 필요한 최소한의 가정을 선택하는 것이 원칙입니다.

### 각 모델의 내결성 요구사항

| 모델 | f개 장애 허용 시 최소 노드 수 | 대표 알고리즘 | 운영 비용 |
|--------|--------------------------|---------------|---------|
| Crash (fail-stop) | 2f + 1 | Raft, Paxos | 낮음 |
| Crash-recovery | 2f + 1 | Raft (로그 복원) | 낮음~중간 |
| Omission | 2f + 1 | 재전송 프로토콜 | 중간 |
| Byzantine | 3f + 1 | PBFT, HotStuff | 높음 |

5노드 Raft 클러스터는 f=2, 즉 동시에 2노드가 죽어도 정상 작동합니다. 같은 5노드로 Byzantine을 견디려면 f=1만 허용되므로, 동일 내결성을 위해 노드 수를 더 늘려야 합니다.

---

## Crash-recovery: 현실에서 가장 흔한 모델

순수한 fail-stop(죽으면 영원히 죽음)은 이론적 모델입니다. 현실의 서버는 죽었다가 다시 살아납니다. OOM kill 후 systemd가 재시작하거나, VM이 다른 호스트에서 부활합니다. 이때 노드는 자신이 어디까지 처리했는지 기억해야 합니다.

```python
# crash-recovery 모델에서 안전한 상태 복원
import json
from pathlib import Path

WAL_PATH = Path("/var/lib/myapp/wal.jsonl")

def append_wal(entry: dict) -> None:
    """디스크에 먼저 쓴 뒤 메모리에 반영한다."""
    with open(WAL_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
        f.flush()
        import os; os.fsync(f.fileno())  # 디스크까지 보장

def recover_from_wal() -> list[dict]:
    """재시작 시 WAL을 읽어 마지막 상태를 복원한다."""
    entries = []
    if WAL_PATH.exists():
        for line in WAL_PATH.read_text().splitlines():
            entries.append(json.loads(line))
    return entries
```

WAL(Write-Ahead Log)은 crash-recovery 모델의 기본 도구입니다. 디스크에 먼저 쓰고, 메모리에 반영하고, 재시작 시 WAL을 다시 읽어 복원합니다. PostgreSQL, etcd, Kafka 모두 이 패턴을 사용합니다.

---

## 장애 감지기의 한계와 트레이드오프

비동기 시스템에서 완벽한 장애 감지기는 불가능합니다. 이것은 FLP impossibility(1985)로 증명된 결과입니다. 현실에서는 두 가지 종류의 오류를 트레이드오프합니다.

| 오류 종류 | 의미 | 결과 |
|-----------|------|------|
| False positive | 살아 있는 노드를 죽었다고 판단 | 불필요한 페일오버, 재선출, 트래픽 재분배 |
| False negative | 죽은 노드를 살아 있다고 판단 | 요청 유실, 타임아웃 누적, 사용자 오류 |

타임아웃을 짧게 잡으면 false positive가 늘고, 길게 잡으면 false negative가 늘어납니다. 이 관계는 제거할 수 없고 관리할 수만 있습니다.

### 적응형 타임아웃 구현

```python
# adaptive_timeout.py
import time
from collections import deque

class AdaptiveTimeout:
    """RTT 측정값 기반으로 타임아웃을 동적 조정한다."""
    def __init__(self, initial_ms: float = 500, safety_factor: float = 4.0):
        self._samples: deque[float] = deque(maxlen=100)
        self._timeout_ms = initial_ms
        self._safety_factor = safety_factor

    def record_rtt(self, rtt_ms: float) -> None:
        self._samples.append(rtt_ms)
        if len(self._samples) >= 10:
            avg = sum(self._samples) / len(self._samples)
            std = (sum((x - avg) ** 2 for x in self._samples) / len(self._samples)) ** 0.5
            self._timeout_ms = avg + self._safety_factor * std

    @property
    def timeout_ms(self) -> float:
        return self._timeout_ms
```

이 구현은 TCP의 RTO 계산과 유사한 원리입니다. 평균 RTT + 4×표준편차를 타임아웃으로 사용하면, 정상적인 지연 변동은 흡수하면서도 진짜 장애는 빠르게 감지할 수 있습니다.

---

## 네트워크 파티션의 현실

네트워크 파티션은 "노드는 모두 살아 있지만 서로를 볼 수 없는 상태"입니다. 노드 장애와 달리 파티션은 비대칭적일 수 있습니다.

```text
대칭 파티션:   A ↔ B 상호 통신 불가
비대칭 파티션: A → B 가능, B → A 불가

예) 3노드 {A, B, C}에서:
    A ↔ B 정상
    A ↔ C 정상
    B ↔ C 단절  ← B와 C는 서로를 죽었다고 판단할 수 있음
```

이런 부분 파티션에서 각 노드가 독립적으로 "상대가 죽었다"고 판단하면 split-brain이 됩니다. B는 C 없이 리더를 자처하고, C도 B 없이 리더를 자처합니다. 결과는 두 개의 리더, 두 개의 진실입니다.

### 파티션 시 설계 선택지

| 선택 | 설명 | 대표 시스템 |
|------|------|------------|
| CP — 쓰기 거부 | 파티션 중 쓰기를 받지 않음, 일관성 유지 | etcd, ZooKeeper, Spanner |
| AP — 쓰기 허용 | 파티션 중에도 쓰기를 받음, 충돌은 나중에 해결 | Cassandra, DynamoDB |
| 하이브리드 | API별로 CP/AP를 다르게 적용 | 실무 대부분 |

실무에서는 시스템 전체가 CP나 AP인 경우는 드뭅니다. 결제 API는 CP로, 상품 조회 API는 AP로 설정하는 하이브리드가 일반적입니다. 이 부분은 4편(CAP)에서 상세히 다룹니다.

---

## 장애 모델과 테스트: Chaos Engineering의 기초

장애 모델을 명시하면, 그 모델에 맞는 테스트를 체계적으로 만들 수 있습니다.

| 장애 모델 | 주입 방법 | 검증 항목 |
|-----------|----------|----------|
| Crash | `kill -9`, pod delete | 리더 재선출 시간, 요청 오류율 |
| Omission | `tc netem loss 10%` | 재전송 성공률, 중복 처리 여부 |
| Timing | `tc netem delay 500ms 200ms` | P99 응답, 타임아웃 비율 |
| Byzantine | 응답 조작 proxy | 데이터 정합성, 감사 로그 |
| Partition | `iptables DROP` | split-brain 발생 여부, 복구 시간 |

```bash
# tc를 사용한 장애 주입 예시 (Linux)
# 10% 패킷 유실 + 200ms 지연 주입
sudo tc qdisc add dev eth0 root netem delay 200ms loss 10%

# 테스트 실행
python3 -m pytest tests/integration/test_under_failure.py -v

# 정리
sudo tc qdisc del dev eth0 root
```

이 테스트를 CI에 포함하면 "장애 모델 X를 가정했을 때 시스템이 Y 시간 안에 복구되는가"를 반복적으로 검증할 수 있습니다. Netflix의 Chaos Monkey, AWS의 FIS, Gremlin 같은 도구들이 모두 이 원리 위에 만들어져 있습니다.

---

## 장애 감지 패턴 비교

시스템이 장애를 감지하는 방식도 장애 모델에 따라 달라집니다.

| 패턴 | 동작 | 장점 | 단점 |
|--------|------|------|------|
| Heartbeat | 주기적 신호 전송, 미도달 시 장애 판단 | 단순, 구현 쉬움 | false positive 위험 |
| Lease | 리스 만료 시 자동 해제 | 시간 기반 안전 보장 | 시계 동기화 필요 |
| Gossip | 노드들이 서로의 상태를 전파 | 중앙 장애점 없음 | 수렴 시간 느림 |
| Accrual (φ) | 의심 도를 연속 값으로 출력 | 임계값 조절 가능 | 구현 복잡 |

Cassandra는 Gossip + Accrual φ 조합을 사용합니다. etcd/Raft는 Heartbeat + Lease 조합을 사용합니다. 어떤 조합을 선택하든 false positive/negative 트레이드오프는 남습니다.

---

## 운영 시나리오: 장애 모델 오판으로 생기는 사고

다음은 실제 운영에서 자주 발생하는 시나리오입니다.

1. 네트워크 지연이 일시적으로 치솟습니다 (timing 장애).
2. 타임아웃 기반 장애 감지기가 리더를 "죽었다"고 판단합니다 (false positive).
3. 새 리더가 선출되고, 기존 리더도 복구됩니다.
4. 순간적으로 두 리더가 동시에 쓰기를 받습니다 (split-brain).
5. 클라이언트 요청 일부가 이전 리더로 가서 충돌하는 데이터가 생깁니다.

이 사고의 근본 원인은 "느림"을 "죽음"으로 오판한 것입니다. 예방책은 다음과 같습니다.

- fencing token: 이전 리더의 쓰기를 무효화하는 단조 증가 토큰을 사용합니다.
- 적응형 타임아웃: 고정값 대신 측정 기반 동적 타임아웃을 사용합니다.
- 리더 임기(term) 검증: 모든 쓰기 요청에 현재 임기 번호를 포함시키고, 이전 임기의 쓰기는 거부합니다.

```python
# fencing token 검증 예시
def write_with_fence(key: str, value: str, fence_token: int) -> bool:
    current_fence = db.get_fence_token(key)
    if fence_token < current_fence:
        return False  # 이전 리더의 쓰기 — 거부
    db.put(key, value, fence_token=fence_token)
    return True
```

---

## 실무에서는 이렇게 드러납니다

대부분의 인터넷 서비스는 crash와 partition을 중심에 둔 CFT 모델을 전제로 합니다. 금융이나 블록체인 계열은 Byzantine까지 고려하는 BFT 계열을 선택합니다. Kubernetes, Spanner, Cassandra 같은 시스템의 설계 문서를 보면 어떤 장애 모델을 겨냥했는지가 분명히 적혀 있습니다. 예를 들어 Kubernetes의 etcd는 Raft를 사용하므로 crash-recovery를 전제하고, Cassandra는 gossip 기반 장애 감지로 네트워크 파티션 상황에서도 가용성을 유지하도록 설계되어 있습니다. 장애 모델을 명시하지 않은 시스템은 암묵적으로 crash-stop을 가정하는 경우가 많은데, 이때 파티션이 발생하면 예측 불가능한 동작이 나타납니다.

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

## 실제 시스템의 장애 모델 선택 사례

각 시스템이 어떤 장애 모델을 전제로 설계되었는지를 아는 것은 운영에서 매우 중요합니다.

| 시스템 | 장애 모델 가정 | 내결성 | 설계 결과 |
|--------|--------------|--------|----------|
| etcd / Raft | Crash-recovery | 2f+1 (보통 3 or 5) | WAL + 스냅샷 복원, 리더 선출 |
| Cassandra | Crash + Partition | QUORUM 설정 | Gossip 기반 감지, hinted handoff |
| ZooKeeper | Crash-recovery | 2f+1 | 세션 + 임시 노드로 장애 전파 |
| Bitcoin | Byzantine | 50% 해시파워 | PoW, 가장 긴 체인 선택 |
| Spanner | Crash + Timing | 2f+1 | TrueTime으로 시계 불확실성 명시 |
| Kafka | Crash-recovery | ISR 기반 | 최소 ISR 유지 시만 쓰기 허용 |

이 표에서 주목할 점은 Bitcoin만 Byzantine을 가정한다는 사실입니다. 나머지는 모두 "노드가 거짓말하지 않는다"를 전제합니다. 데이터센터 내부에서는 노드를 운영자가 통제하기 때문입니다. 외부 참여자가 있는 시스템만 Byzantine 비용을 감수합니다.

### Kafka ISR: crash-recovery 모델의 실무 적용

Kafka는 ISR(In-Sync Replicas)이라는 개념으로 crash-recovery를 구현합니다.

```text
토픽: orders, 파티션 0
리더: broker-1
ISR: [broker-1, broker-2, broker-3]

1. broker-3이 10초간 복제를 못 따라옴
2. 리더가 broker-3을 ISR에서 제거
   ISR: [broker-1, broker-2]
3. min.insync.replicas=2 이므로 쓰기 계속 가능
4. broker-3 복구 → 로그 따라잡기 → ISR 복귀
   ISR: [broker-1, broker-2, broker-3]
```

만약 ISR이 `min.insync.replicas` 미만으로 떨어지면 프로듀서는 `NotEnoughReplicasException`을 받습니다. 이것이 Kafka가 crash-recovery 상황에서 데이터 유실을 방지하는 메커니즘입니다.

---

## 장애 모델 문서화 템플릿

시스템의 장애 모델을 명시적으로 문서화하면 팀 전체가 같은 가정 위에서 판단할 수 있습니다.

```yaml
# failure-model.yaml
service: payment-gateway
failure_model:
  node: crash-recovery
  network: partition-possible
  byzantine: not-assumed
  rationale: >
    내부 데이터센터 운영이므로 악의적 노드를 가정하지 않음.
    노드는 OOM/배포로 죽었다 살아날 수 있으므로 crash-recovery 가정.

detection:
  method: heartbeat
  interval_ms: 500
  timeout_ms: 2000
  false_positive_action: fencing_token_check

partition_policy:
  write: reject_without_quorum
  read: allow_stale_with_header
  recovery: log_replay_then_reconcile
```

이 문서가 존재하면 새로 합류하는 엔지니어도 "이 시스템은 왜 3노드인가", "타임아웃이 왜 2초인가", "파티션 시 왜 쓰기를 거부하는가"에 대한 답을 즉시 찾을 수 있습니다.

---

## 운영 대시보드에서 장애 모델을 모니터링하는 지표

장애 모델이 정해졌으면, 그 모델이 현실과 맞는지 지속적으로 모니터링해야 합니다.

| 범주 | 지표 | 의미 |
|------|------|------|
| Crash 감지 | 리더 재선출 횟수/시간 | 예상보다 잦으면 타임아웃 조정 필요 |
| Omission | 재전송 비율, ACK 누락률 | 네트워크 품질 저하 신호 |
| Timing | P99/P99.9 응답 시간 | 꼬리 지연이 타임아웃에 근접하면 위험 |
| Partition | 노드 간 연결 상태 매트릭스 | 비대칭 파티션 조기 감지 |
| Recovery | WAL 복원 시간, ISR 복귀 시간 | 복구 SLO 충족 여부 |

```python
# Prometheus 지표 예시
from prometheus_client import Counter, Histogram

leader_elections = Counter(
    "leader_elections_total",
    "Number of leader elections triggered",
)

detection_latency = Histogram(
    "failure_detection_seconds",
    "Time from actual failure to detection",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

false_positives = Counter(
    "false_positive_detections_total",
    "Nodes incorrectly marked as failed",
)
```

false positive 카운터가 급증하면 타임아웃을 늘려야 합니다. leader election이 잦으면 네트워크 품질을 점검해야 합니다. 이렇게 장애 모델의 가정이 현실과 맞는지를 데이터로 검증하는 것이 운영 성숙도의 핵심입니다.

## 정리와 다음 글

장애 모델은 가장 먼저 내려야 하는 설계 결정입니다. 이 결정이 알고리즘과 운영 비용을 함께 정합니다. 다음 글에서는 이런 장애 모델 위에서 노드들이 실제로 어떻게 통신하는지, 즉 RPC와 메시지 전달을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **장애 모델이란 무엇이며 왜 장애를 모델링해야 할까요?**
  - 장애 모델은 "노드가 어떤 방식으로 망가질 수 있는가"를 명시하는 계약입니다. 이 계약 없이는 알고리즘의 정확성도 비용도 논할 수 없습니다. crash만 가정하면 2f+1 노드로 충분하지만, Byzantine을 가정하면 3f+1이 필요합니다.
- **crash, omission, timing, Byzantine은 어떻게 다를까요?**
  - 스펙트럼의 왼쪽에서 오른쪽으로: crash는 멈추기만 하고, omission은 메시지를 빠뜨리고, timing은 임의로 느려지며, Byzantine은 거짓말까지 합니다. 각 단계는 이전 단계를 포함하며 비용은 급격히 올라갑니다.
- **네트워크 파티션은 왜 별도 범주로 봐야 할까요?**
  - 파티션은 노드가 아닌 링크의 장애입니다. 노드는 모두 정상인데 서로를 볼 수 없는 상태가 가능하고, 이때 독립적 판단은 split-brain으로 이어집니다. CAP 정리가 다루는 핵심 상황이 바로 이것입니다.

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
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, Failure Models, Crash, Byzantine, Reliability
