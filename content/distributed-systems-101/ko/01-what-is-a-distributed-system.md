---
series: distributed-systems-101
episode: 1
title: "Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?"
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
  - Fundamentals
  - Latency
  - Failure
  - Coordination
seo_description: 분산 시스템의 정의와 지연, 장애, 조정이라는 세 가지 핵심 축을 중심으로 단일 머신과의 근본적인 차이점을 상세히 정리합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?

서비스를 둘로 나누는 순간, 같은 코드를 돌려도 더 이상 같은 세상에 살지 않습니다. 네트워크가 끼고, 한쪽만 느려지거나 죽을 수 있고, 각 노드가 보는 시간도 조금씩 다르기 때문입니다.

이 글은 Distributed Systems 101 시리즈의 첫 번째 글입니다.

여기서는 그 차이를 지연, 장애, 조정이라는 세 축으로 정리해 두고, 이후 글 전체를 읽을 때 기준점이 되는 멘탈 모델을 세웁니다.

## 먼저 던지는 질문

- 분산 시스템은 정확히 무엇이며 단일 머신 프로그램과 무엇이 다를까요?
- 지연, 장애, 조정이라는 세 축은 왜 분산 시스템의 기본 언어일까요?
- 분산 컴퓨팅의 8가지 허상은 왜 지금도 반복될까요?

## 큰 그림

![Distributed Systems 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/01/01-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 1장 흐름 개요*

## 왜 중요한가

오늘 만드는 거의 모든 서비스는 사실상 분산 시스템입니다. 복제본이 하나라도 붙은 데이터베이스는 이미 분산 시스템이고, 두 개의 마이크로서비스가 서로 통신하는 순간도 분산 시스템입니다. 즉시 응답한다, 항상 성공한다, 시계는 하나다 같은 단일 머신의 직관으로 작성한 코드는 실제 트래픽을 만나면 곧바로 흔들립니다.

> 분산 시스템은 단일 머신 프로그램의 가정이 깨지는 정확한 지점에서 시작됩니다.

## 한눈에 보는 개념

이 그림의 화살표 하나하나는 지연과 부분 장애, 그리고 응답 불확실성을 품고 있습니다. 이것이 단일 함수 호출과 본질적으로 다른 점입니다.

## 핵심 용어

- **분산 시스템**: 독립적으로 동작하는 여러 노드가 메시지 전달을 통해 협력하는 시스템입니다.
- 지연: 메시지가 상대편에 도달하는 데 걸리는 시간입니다.
- 장애: 노드, 네트워크, 디스크가 일부 또는 전체로 멈추는 현상입니다.
- 조정: 여러 노드가 하나의 결정을 함께 맞추는 과정입니다.
- **부분 장애**: 어떤 노드는 살아 있고 어떤 노드는 죽어 있는 상태입니다. 분산 환경의 대표적인 조건입니다.

## Before / After

**Before — 단일 머신 직관**

```text
calls finish instantly / always succeed / there is one clock
```

**After — 분산 환경**

```text
calls take ms to s / can fail in part / each node has its own clock
```

이 단순한 전환이 이 시리즈의 거의 모든 주제를 만듭니다. 재시도, 타임아웃, 합의는 모두 여기서 출발합니다.

## 실습: 차이를 몸으로 느껴 보기

### 1단계 — 로컬 함수 호출

```python
# 1_local.py
def add(a, b):
    return a + b

print(add(1, 2))  # 3, instantly
```

이 호출은 마이크로초 수준에서 끝납니다. 실패를 따로 걱정할 이유도 없습니다.

### 2단계 — 같은 머신의 다른 프로세스 호출(HTTP)

```python
# 2_local_http.py
# pip install fastapi uvicorn requests
from fastapi import FastAPI
app = FastAPI()
@app.get("/add")
def add(a: int, b: int): return {"r": a + b}
# run: uvicorn 2_local_http:app --port 8001
```

```python
# 2_client.py
import requests
print(requests.get("http://127.0.0.1:8001/add", params={"a":1,"b":2}, timeout=1).json())
```

같은 머신 안인데도 지연은 밀리초 단위로 뛰어오릅니다. 이것이 첫 번째 분리의 비용입니다.

### 3단계 — 서버를 죽여 보기

```bash
# after killing the server with ctrl+c
python3 2_client.py
# requests.exceptions.ConnectionError
```

호출자는 서버의 실제 상태를 알지 못합니다. 이런 종류의 오류는 단일 머신 함수 호출에서는 나타나지 않았습니다.

### 4단계 — 응답이 느리면 어떻게 될까요?

```python
# 4_slow.py
@app.get("/slow")
def slow():
    import time; time.sleep(5)
    return {"ok": True}
```

```python
requests.get("http://127.0.0.1:8001/slow", timeout=1)
# requests.exceptions.ReadTimeout
```

타임아웃이 없으면 호출은 5초 동안 그대로 붙잡힙니다. 분산 시스템에서 타임아웃은 옵션이 아니라 기본 장치입니다.

### 5단계 — 노드 간 시계 어긋남

```python
# 5_clock.py
import time
print("server time:", time.time())
# run the same code on another machine and the two values
# will not match exactly even with NTP (millisecond-level drift)
```

실제 순서를 벽시계 시간으로 결정하면 안 됩니다. 6편의 합의와 8편의 메시지 순서 이야기가 이 문제를 직접 다룹니다.

## 이 코드에서 먼저 봐야 할 점

- 네트워크가 끼는 순간 같은 호출도 전혀 다른 종류의 오류를 갖게 됩니다.
- 타임아웃, 재시도, 멱등성은 단일 머신에서는 거의 의식하지 않던 개념입니다.
- 시계는 정확히 일치하지 않습니다.
- 성공과 실패 사이에 모름이라는 상태가 새로 생깁니다.

## 자주 하는 실수 5가지

1. **타임아웃 없이 호출합니다.** 응답이 영원히 오지 않을 수 있습니다.
2. **멱등성 없이 재시도합니다.** 대표적인 결과가 중복 결제입니다.
3. **벽시계 시간으로 순서를 정합니다.** 노드마다 보는 시간이 다릅니다.
4. **부분 장애를 무시합니다.** 실제 운영에서 가장 흔한 상태입니다.
5. **단일 머신 지연으로 용량을 계산합니다.** 네트워크 지연이 전체 예산을 지배합니다.

## 실무에서는 이렇게 드러납니다

현실의 거의 모든 웹 백엔드는 분산 시스템입니다. 복제와 장애 조치를 갖춘 관계형 데이터베이스도 그렇고, Redis Cluster, Kafka, Cassandra는 더 말할 것도 없습니다. 클라우드의 AZ 이중화, 멀티 리전 배치, CDN도 모두 분산 시스템 설계의 일부입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 단일 머신의 직관을 의도적으로 의심합니다.
- 타임아웃, 재시도, 멱등성을 첫 줄부터 설계합니다.
- 시스템 모델 안에 모름 상태를 반드시 넣습니다.
- 벽시계는 표시용으로만 보고, 단조 증가 시계를 더 신뢰합니다.
- 굳이 분산이 필요 없는 상황에서는 단일 머신으로 끝내는 선택도 합니다.

## 체크리스트

- [ ] 분산 시스템을 한 문장으로 정의할 수 있는가?
- [ ] 지연, 장애, 조정이라는 세 축을 설명할 수 있는가?
- [ ] 부분 장애가 단일 머신의 장애와 어떻게 다른지 말할 수 있는가?
- [ ] 왜 타임아웃이 필수인지 설명할 수 있는가?
- [ ] 벽시계와 단조 증가 시계의 차이를 알고 있는가?

## 연습 문제

1. 외부 API를 타임아웃 없이 호출하는 코드를 하나 찾아 타임아웃을 추가해 보세요.
2. 재시도해도 안전한 연산과 위험한 연산을 각각 두 가지씩 적어 보세요.
3. 같은 메시지를 두 번 처리해도 결과가 같아지도록 멱등성 키 설계를 해 보세요.

## 정리와 다음 글

분산 시스템은 지연, 장애, 조정이라는 세 축에서 단일 머신 프로그램과 본질적으로 다릅니다. 다음 글에서는 그중 장애를 더 정밀하게 다루기 위해 crash, omission, Byzantine 같은 장애 모델을 살펴봅니다.


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

- **분산 시스템은 정확히 무엇이며 단일 머신 프로그램과 무엇이 다를까요?**
  - 본문의 기준은 분산 시스템이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **지연, 장애, 조정이라는 세 축은 왜 분산 시스템의 기본 언어일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **분산 컴퓨팅의 8가지 허상은 왜 지금도 반복될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **분산 시스템이란 무엇인가? (현재 글)**
- 장애 모델 (예정)
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

- [Distributed computing (Wikipedia)](https://en.wikipedia.org/wiki/Distributed_computing)
- [Fallacies of distributed computing (Wikipedia)](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing)
- [Designing Data-Intensive Applications — Martin Kleppmann](https://dataintensive.net/)
- [Distributed Systems for Fun and Profit](http://book.mixu.net/distsys/)

Tags: Computer Science, Distributed Systems, Fundamentals, Latency, Failure, Coordination
