---
series: distributed-systems-101
episode: 2
title: 장애 모델
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

# 장애 모델

운영 채널에서 "서버가 죽었습니다"라고 말할 때, 실제로는 여러 종류의 사건이 한 문장에 섞여 있습니다. 프로세스가 멈춘 것인지, 패킷이 빠지는 것인지, 아니면 너무 느려서 살아 있어도 죽은 것처럼 보이는 것인지부터 갈라야 설계가 흔들리지 않습니다.

이 글은 Distributed Systems 101 시리즈의 두 번째 글입니다.

여기서는 crash, omission, timing, Byzantine을 설계 언어로 정리하고, 뒤이어 나오는 CAP와 합의 이야기가 어떤 가정 위에 서는지 분명히 잡습니다.

## 이 글에서 다룰 문제

- 장애 모델이란 무엇이며 왜 장애를 모델링해야 할까요?
- crash, omission, timing, Byzantine은 어떻게 다를까요?
- 네트워크 파티션은 왜 별도 범주로 봐야 할까요?
- 타임아웃 기반 장애 감지는 왜 근사치일 뿐일까요?
- 실제 시스템은 어떤 장애 모델을 전제로 설계될까요?

> 분산 시스템 설계는 어떤 장애를 가정하는지부터 시작합니다. crash, omission, Byzantine은 그 가정을 문서에 적어 넣기 위한 표준 어휘입니다.

## 왜 중요한가

알고리즘이 노드가 어떤 방식으로 망가지는지를 명시하지 않으면 정확성도 비용도 말할 수 없습니다. Raft, Paxos, BFT 계열 알고리즘이 서로 다른 이유는 각자가 전제하는 장애 모델이 다르기 때문입니다. 이 어휘를 모르면 논문도 문서도 절반밖에 읽히지 않습니다.

> 장애 모델은 알고리즘의 가격표입니다.

## 한눈에 보는 개념

![장애 모델의 강도 스펙트럼](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/02/02-01-concept-at-a-glance.ko.png)

*장애 모델의 강도 스펙트럼*

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

<!-- toc:begin -->
- [분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- **failure model (현재 글)**
- RPC와 message passing (예정)
- consistency와 CAP (예정)
- replication (예정)
- consensus와 Raft (예정)
- leader election (예정)
- message queue와 event sourcing (예정)
- distributed transaction (예정)
- 운영 가능한 분산 시스템 패턴 (예정)
<!-- toc:end -->

## 참고 자료

- [Failure semantics (Wikipedia)](https://en.wikipedia.org/wiki/Failure_semantics)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
- [Network partition (Wikipedia)](https://en.wikipedia.org/wiki/Network_partition)
- [Designing Data-Intensive Applications — chapter 8](https://dataintensive.net/)

Tags: Computer Science, Distributed Systems, Failure Models, Crash, Byzantine, Reliability
