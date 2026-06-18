---
series: distributed-systems-101
episode: 6
title: "바이브코딩을 위한 분산 시스템 기초 (6/10): 합의와 Raft"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 분산시스템
  - 합의
  - Raft
  - Paxos
  - etcd
language: ko
---

# 바이브코딩을 위한 분산 시스템 기초 (6/10): 합의와 Raft

이 글은 **바이브코딩을 위한 분산 시스템 기초** 시리즈의 6편입니다. AI가 만든 서비스를 스케일하려면 여러 서버가 하나의 진실에 동의하는 메커니즘을 이해해야 합니다. etcd, ZooKeeper, Kafka의 내부, 그리고 Kubernetes가 왜 3개 이상의 컨트롤 플레인을 권장하는지가 모두 합의 알고리즘에서 나옵니다.

---

AI에게 "Kubernetes 클러스터를 고가용성으로 구성해줘"라고 하면 etcd를 3노드로 구성하는 코드가 나옵니다. 왜 3노드인지, 2노드는 왜 안 되는지를 모르면 비용 절감을 위해 2노드로 줄이거나 4노드로 늘리는 잘못된 결정을 내릴 수 있습니다.

"클러스터가 동의하면 된다"는 말은 쉽지만, 실제로는 가장 까다로운 요구 사항 중 하나입니다. 리더가 중간에 사라지고 메시지가 늦게 도착하는 상황에서도 모두가 같은 로그를 본다고 약속해야 하기 때문입니다.

> "합의는 분산 시스템에서 동의가 갖는 가치입니다. 다수결이 없으면 split-brain이 생기고, split-brain이 생기면 데이터가 깨집니다."

## 이 글에서 다룰 질문들

- 합의 문제란 무엇이며 왜 분산 시스템에서 어려울까요?
- Raft의 term, log, commit은 각각 무엇을 뜻할까요?
- 왜 3노드가 최소 고가용성 구성인지 수식으로 설명할 수 있을까요?
- AI가 구성한 etcd/ZooKeeper 클러스터에서 무엇을 확인해야 할까요?
- 합의 알고리즘의 성능 비용을 어떻게 측정할 수 있을까요?

---

## 바이브코딩과 합의: "왜 홀수 노드인가?"

AI가 항상 3, 5, 7 같은 홀수로 노드 수를 구성하는 이유가 있습니다. 합의 알고리즘은 다수결(quorum)로 동작하기 때문입니다.

### Before: 노드 수를 임의로 결정

```yaml
# AI가 만들어 준 etcd 클러스터 구성 — 왜 3개인지 설명 없음
# etcd 클러스터: 3노드
etcd:
  - etcd-1
  - etcd-2
  - etcd-3
```

왜 3개인지, 2개로 줄이면 안 되는지, 4개로 늘리면 더 안전한지를 모른 채 운영하면 잘못된 비용 결정이 나옵니다.

### After: 쿼럼 공식으로 노드 수 결정

```python
# 쿼럼 공식: f개 장애를 허용하려면 최소 2f+1 노드 필요
def min_nodes_for_fault_tolerance(f: int) -> int:
    """
    f: 동시에 허용할 장애 노드 수
    반환: 필요한 최소 노드 수
    """
    return 2 * f + 1

# 1개 장애 허용 → 최소 3노드
print(min_nodes_for_fault_tolerance(1))  # 3

# 2개 장애 허용 → 최소 5노드
print(min_nodes_for_fault_tolerance(2))  # 5

# 2노드가 안 되는 이유:
# 2노드에서 1개가 죽으면 quorum(2/2 = 과반수 1)을 맞출 수 없음
# 살아있는 1노드가 리더가 되면 split-brain 위험

# 4노드가 3노드보다 나쁜 이유:
# 4노드 quorum = 3/4, 즉 3개 살아야 함 → 1개만 장애 허용
# 3노드와 동일한 내결성이지만 비용은 더 높음
```

---

## Raft 핵심 개념

Raft는 이해하기 쉬운 합의 알고리즘으로 설계되었습니다. etcd, CockroachDB, TiKV가 Raft를 사용합니다.

| 개념 | 의미 |
|------|------|
| Term | 단조 증가하는 epoch. 새 리더가 뽑히면 새 term 시작 |
| Log | index로 식별되는 엔트리들의 순서 있는 목록 |
| Commit | 다수가 받은 엔트리가 더 이상 사라지지 않는 상태 |
| Quorum | 보통 2f+1 중 f+1, 즉 다수 |
| Leader | 모든 쓰기를 받는 단일 노드 |
| Follower | 리더로부터 로그를 복제받는 노드 |
| Candidate | 리더 선출에 참여 중인 노드 |

### Raft 쓰기 흐름

```
1. 클라이언트 → 리더: "x = 5로 써줘"
2. 리더 → 로그에 기록 (uncommitted)
3. 리더 → 팔로워: AppendEntries RPC 전송
4. 팔로워 → 리더: 확인 응답
5. 과반수(quorum) 확인 완료 → 리더가 커밋
6. 리더 → 클라이언트: "완료"
7. 리더 → 팔로워: 커밋 알림
```

---

## 자주 하는 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| 2노드 etcd 구성 | 1노드 장애 시 quorum 불가, 쓰기 중단 | 최소 3노드, 권장 5노드 |
| 짝수 노드 구성 | 짝수는 분리 시 두 그룹이 각각 quorum 주장 가능 | 항상 홀수 노드 사용 |
| 리더 선출 시간 SLO에 미포함 | 리더 선출 150~600ms 동안 쓰기 불가 | 리더 선출 시간을 SLO에 포함 |
| Raft와 Paxos를 혼용 | 로그 인덱스와 ballot 번호 개념이 달라 혼란 | 한 시스템에서 하나의 합의 알고리즘 사용 |
| 합의 비용을 일반 RPC와 같게 봄 | Raft 쓰기는 1~2 RTT, 선출은 2~4 RTT | 합의 경로의 지연 예산을 별도 설정 |

---

## AI 팁: AI가 구성한 합의 클러스터 검토법

1. **노드 수 확인**: etcd, ZooKeeper, Consul 구성의 노드 수가 홀수인지, 최소 3개인지 확인하세요.
2. **선출 타임아웃 확인**: heartbeat interval과 election timeout이 적절한 비율(1:10)인지 확인하세요.
3. **쓰기 지연 측정 요청**: "etcd 쓰기 P99 지연을 Prometheus로 모니터링하는 코드를 추가해줘"
4. **리더 선출 빈도 모니터링 요청**: "리더 선출 횟수를 카운터로 수집하는 코드를 추가해줘"

```python
# etcd 클러스터 상태 확인 스크립트
import subprocess
import json

def check_etcd_health():
    result = subprocess.run(
        ["etcdctl", "--endpoints=http://etcd-1:2379,http://etcd-2:2379,http://etcd-3:2379",
         "endpoint", "health", "--write-out=json"],
        capture_output=True, text=True
    )
    health = json.loads(result.stdout)
    for endpoint in health:
        status = "건강" if endpoint["health"] else "비정상"
        print(f"{endpoint['endpoint']}: {status}")

    # quorum 확인: 과반수가 살아있는지
    healthy_count = sum(1 for e in health if e["health"])
    total = len(health)
    quorum = total // 2 + 1
    if healthy_count >= quorum:
        print(f"쿼럼 유지 ({healthy_count}/{total})")
    else:
        print(f"쿼럼 손실! ({healthy_count}/{total}) — 쓰기 불가")
```

---

## 실전 체크리스트

- [ ] 왜 3노드가 최소 고가용성 구성인지 수식으로 설명할 수 있다
- [ ] Raft의 term, log, commit이 무엇인지 말할 수 있다
- [ ] AI가 구성한 etcd/Kafka 클러스터의 노드 수가 홀수인지 확인했다
- [ ] 리더 선출 시간을 SLO에 포함했다
- [ ] 합의 클러스터의 쿼럼 상태를 모니터링하고 있다
- [ ] 4노드보다 3노드가 내결성 관점에서 왜 동일한지 설명할 수 있다

---

## 처음 질문으로 돌아가기

- **왜 3노드가 최소 고가용성 구성인지 수식으로 설명할 수 있을까요?**
  1개 장애를 허용하려면 2×1+1=3노드가 필요합니다. 2노드에서 1개가 죽으면 quorum(과반수)를 만들 수 없어 쓰기가 중단됩니다.

- **AI가 구성한 etcd/ZooKeeper 클러스터에서 무엇을 확인해야 할까요?**
  노드 수가 홀수인지(최소 3개), heartbeat와 election timeout 비율이 1:10 이상인지, 리더 선출 빈도 모니터링이 있는지를 확인하세요.

- **합의 알고리즘의 성능 비용을 어떻게 측정할 수 있을까요?**
  Raft 쓰기는 1~2 RTT(같은 리전 기준 2~10ms), 리더 선출은 2~4 RTT(150~600ms)입니다. etcd의 P99 쓰기 지연과 리더 선출 횟수를 Prometheus로 모니터링하세요.

---

## 정리

합의 알고리즘은 여러 노드가 하나의 진실에 동의하는 메커니즘입니다. 2f+1 공식이 홀수 노드의 이유이고, Raft의 term/log/commit이 이를 구현합니다. AI가 만들어 준 클러스터 구성에서 노드 수와 타임아웃 설정을 반드시 검토하세요. 다음 글에서는 합의 위에서 동작하는 리더 선출의 실전 패턴을 다룹니다.

---

## 참고 자료

- [Raft Consensus Algorithm](https://raft.github.io/)
- [etcd documentation](https://etcd.io/docs/)
- [Designing Data-Intensive Applications — chapter 9](https://dataintensive.net/)
- [In Search of an Understandable Consensus Algorithm (Raft 논문)](https://raft.github.io/raft.pdf)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 분산 시스템 기초 (1/10): 분산 시스템이란 무엇인가?
- 바이브코딩을 위한 분산 시스템 기초 (2/10): 장애 모델
- 바이브코딩을 위한 분산 시스템 기초 (3/10): RPC와 메시지 전달
- 바이브코딩을 위한 분산 시스템 기초 (4/10): 일관성과 CAP
- 바이브코딩을 위한 분산 시스템 기초 (5/10): 복제
- **바이브코딩을 위한 분산 시스템 기초 (6/10): 합의와 Raft (현재 글)**
- 바이브코딩을 위한 분산 시스템 기초 (7/10): 리더 선출
- 바이브코딩을 위한 분산 시스템 기초 (8/10): 메시지 큐와 이벤트 소싱
- 바이브코딩을 위한 분산 시스템 기초 (9/10): 분산 트랜잭션
- 바이브코딩을 위한 분산 시스템 기초 (10/10): 운영 가능한 분산 패턴
<!-- toc:end -->

Tags: 바이브코딩, 분산시스템, 합의, Raft, Paxos, etcd
