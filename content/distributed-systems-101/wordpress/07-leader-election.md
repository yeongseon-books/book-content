---
title: "바이브코딩을 위한 Distributed Systems 기초 (7/10): 리더 선출"
series: distributed-systems-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - DistributedSystems
  - LeaderElection
  - Lease
  - FencingToken
---

# 바이브코딩을 위한 Distributed Systems 기초 (7/10): 리더 선출

이 글은 "바이브코딩을 위한 Distributed Systems 기초" 시리즈의 7번째 글입니다.

---

바이브코딩에서 AI는 분산 시스템의 리더 선출 코드를 빠르게 만들어 줍니다. 하지만 리더 선출에서 가장 위험한 장면은 "누가 이기느냐"가 아닙니다. 죽었다고 믿었던 예전 리더가 늦게 깨어나 다시 쓰기를 시도하는 순간입니다. 이 장면을 막지 못하면 시스템은 아주 짧은 순간에도 두 리더를 허용하게 됩니다.

분산 시스템에서 치명적인 버그 상당수는 두 리더가 동시에 존재하는 순간 발생합니다. 두 리더가 같은 자원에 동시에 쓰기 시작하면 데이터는 곧바로 깨집니다. 올바른 리더 선출은 어떤 시점에도 하나의 리더만 권한을 가진다는 약속을 만들어 냅니다.

AI가 만들어 준 리더 선출 코드에서 lease TTL, heartbeat 갱신 간격, fencing token 사용 여부를 확인해야 합니다.

lease와 fencing token을 함께 써서, 리더를 고르는 문제를 넘어 예전 리더의 영향력을 끊는 운영 안전장치를 정리합니다.

> **핵심 인사이트:** 좋은 리더 선출은 리더가 둘인 순간이 없다는 약속입니다. Lease TTL로 권한을 시간 제한하고, fencing token으로 예전 리더의 요청을 거부합니다.

## 이 글에서 다룰 문제

- 왜 리더 선출이 필요하며 어떤 안전 조건이 필요할까요?
- lease와 heartbeat는 각각 어떤 역할을 할까요?
- fencing token은 왜 이전 리더를 막는 핵심 장치일까요?
- split-brain이란 무엇이고 어떻게 방지할까요?
- AI가 만든 리더 선출 코드에서 확인해야 할 것은 무엇인가요?

## 리더 선출 핵심 패턴

```python
import time
import threading

class LeaderElection:
    def __init__(self, lock_service, node_id: str, ttl: int = 10):
        self.lock_service = lock_service
        self.node_id = node_id
        self.ttl = ttl
        self.is_leader = False
        self.fencing_token = 0  # 단조 증가 토큰

    def try_acquire_leader(self) -> bool:
        """Lease 획득 시도 - TTL 만료 시 자동 해제"""
        token = self.lock_service.acquire(
            key="leader-lock",
            owner=self.node_id,
            ttl=self.ttl
        )
        if token:
            self.is_leader = True
            self.fencing_token = token  # 스토리지에 전달
            return True
        return False

    def heartbeat_loop(self):
        """Lease 갱신 - 실패 시 리더 포기"""
        while self.is_leader:
            renewed = self.lock_service.renew(
                key="leader-lock",
                owner=self.node_id,
                ttl=self.ttl
            )
            if not renewed:
                self.is_leader = False  # 안전하게 포기
                break
            time.sleep(self.ttl / 3)  # TTL의 1/3 주기로 갱신

# 스토리지: fencing token으로 예전 리더 거부
def write_with_fencing(storage, data, token: int):
    if token < storage.current_token:
        raise ValueError(f"Stale token {token}, current {storage.current_token}")
    storage.write(data, token)
```

## 변경 전후 비교

**Before: Lease/Fencing 없는 리더 선출**
```text
- 예전 리더가 네트워크 지연 후 복귀해서 계속 쓰기
- Split-brain: 두 노드가 동시에 자신을 리더로 인식
- 타임아웃만으로 리더 판단 (불확실)
- 데이터 충돌 및 손상 발생
```

**After: Lease + Fencing Token**
```text
- Lease TTL 만료 시 자동 권한 해제
- Heartbeat 실패 시 리더가 안전하게 포기
- Fencing token으로 예전 리더의 쓰기 거부
- Split-brain 발생 불가
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| Lease TTL만 있고 fencing token 없음 | 예전 리더의 늦은 쓰기 허용 | 스토리지에서 토큰 검증 필수 |
| Heartbeat 간격이 TTL보다 긴 경우 | Lease 만료 전 갱신 불가 | Heartbeat = TTL / 3 이하 |
| 리더 포기 없이 장애 대응 | Split-brain 발생 가능 | Heartbeat 실패 시 즉시 리더 포기 |
| Clock 동기화만 믿음 | NTP 오차로 잘못된 판단 | Lease 기반 판단, 시계 의존 최소화 |
| Fencing token을 클라이언트만 검증 | 스토리지 우회 가능 | 스토리지 계층에서 토큰 검증 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"분산 시스템에서 리더 선출 코드를 만들어줘.
Lease TTL 10초, Heartbeat 3초 주기,
Fencing token으로 예전 리더의 쓰기를 거부하는
구조까지 포함해야 해"

# AI 결과물 검증 체크포인트:
# - Lease TTL이 Heartbeat 간격의 3배 이상인가?
# - Fencing token이 단조 증가하는가?
# - Heartbeat 실패 시 리더가 포기하는가?
# - Split-brain 방지 로직이 있는가?
```

## 운영 체크리스트

- [ ] Lease TTL이 Heartbeat 간격의 3배 이상으로 설정되어 있다
- [ ] Fencing token이 모든 쓰기 요청에 포함된다
- [ ] 스토리지 계층에서 fencing token을 검증한다
- [ ] Heartbeat 실패 시 리더가 안전하게 포기한다
- [ ] 리더 선출 이벤트가 로그/메트릭에 기록된다

## 처음 질문으로 돌아가기

- **Lease와 Heartbeat의 역할은?** Lease는 TTL 기반 임시 권한(만료 시 자동 해제), Heartbeat는 Lease를 주기적으로 갱신하는 신호입니다.
- **Fencing token이 왜 핵심인가요?** 예전 리더가 늦게 깨어나도 단조 증가하는 token을 비교해 낡은 요청을 거부합니다. Lease 만료만으로는 불충분합니다.
- **Split-brain을 어떻게 방지하나요?** Quorum 기반 Lock service, Heartbeat 실패 시 즉각 포기, Fencing token 검증을 조합합니다.

## 정리

바이브코딩에서 AI가 만들어 준 리더 선출 코드에서 Lease TTL/Heartbeat 비율, Fencing token 사용 여부, Heartbeat 실패 시 리더 포기 로직을 반드시 확인하세요. 다음 글에서는 메시지 큐와 이벤트 소싱을 다룹니다.

## 참고 자료

- [Designing Data-Intensive Applications — Chapter 8](https://dataintensive.net/)
- [Google Chubby Paper](https://research.google.com/archive/chubby.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Distributed Systems 기초 (1/10): 분산 시스템이란 무엇인가?
- 바이브코딩을 위한 Distributed Systems 기초 (2/10): 장애 모델
- 바이브코딩을 위한 Distributed Systems 기초 (3/10): RPC와 메시지 패싱
- 바이브코딩을 위한 Distributed Systems 기초 (4/10): 일관성과 CAP
- 바이브코딩을 위한 Distributed Systems 기초 (5/10): 복제
- 바이브코딩을 위한 Distributed Systems 기초 (6/10): 합의와 Raft
- **바이브코딩을 위한 Distributed Systems 기초 (7/10): 리더 선출 (현재 글)**
- 바이브코딩을 위한 Distributed Systems 기초 (8/10): 메시지 큐와 이벤트 소싱
- 바이브코딩을 위한 Distributed Systems 기초 (9/10): 분산 트랜잭션
- 바이브코딩을 위한 Distributed Systems 기초 (10/10): 운영 가능한 분산 시스템 패턴
<!-- toc:end -->

Tags: 바이브코딩, DistributedSystems, LeaderElection, Lease, FencingToken
