---
title: "바이브코딩을 위한 Distributed Systems 기초 (10/10): 운영 가능한 분산 시스템 패턴"
series: distributed-systems-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - DistributedSystems
  - CircuitBreaker
  - Resilience
  - Backpressure
  - Observability
---

# 바이브코딩을 위한 Distributed Systems 기초 (10/10): 운영 가능한 분산 시스템 패턴

이 글은 "바이브코딩을 위한 Distributed Systems 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 분산 시스템 코드를 빠르게 만들어 줍니다. 하지만 마지막 질문은 장애를 없애는 방법이 아닙니다. 느린 upstream 하나가 전체 장애로 번지지 않게 막고, 운영자가 사용자보다 먼저 이상 신호를 읽게 만드는 방법이 핵심입니다.

지금까지 다룬 복제, 합의, 큐, 트랜잭션은 모두 건축 재료였습니다. 운영 패턴은 그 재료를 장애가 흔한 현실에서도 버티게 하는 도구함입니다. 실제 프로덕션에서 시스템을 오래 살려 두는 힘은 기능보다 운영 경계에서 나옵니다.

좋은 운영 패턴은 예상된 장애를 일상적인 사건으로 바꿉니다. 호출 경계마다 timeout, circuit breaker, bulkhead, backpressure를 조합해야 한 곳의 실패가 옆 경계로 번지지 않습니다.

timeout budget, circuit breaker, load shedding, observability를 하나의 운영 경계로 정리합니다.

> **핵심 인사이트:** 분산 시스템에서 장애는 피하는 것이 아니라 격리하는 것입니다. Bulkhead + Circuit Breaker + Backpressure 조합이 연쇄 장애를 막는 기본 도구함입니다.

## 이 글에서 다룰 문제

- Bulkhead로 장애를 어떻게 격리할 수 있을까요?
- Circuit breaker는 연쇄 장애를 어떻게 끊어 줄까요?
- Backpressure는 언제 부하를 안전하게 거절해야 할까요?
- Observability는 어떻게 장애를 먼저 감지하게 해줄까요?
- AI가 만든 분산 시스템 코드에서 운영 관점으로 확인할 것은 무엇인가요?

## 운영 패턴 핵심 구현

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # 정상: 호출 허용
    OPEN = "open"          # 장애: 호출 차단
    HALF_OPEN = "half_open"  # 테스트: 일부 허용

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.last_failure_time = None
        self.recovery_timeout = recovery_timeout

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit is OPEN - fast fail")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Bulkhead: 자원을 서비스별로 분리
import concurrent.futures

class BulkheadPool:
    def __init__(self, service_name: str, max_workers: int):
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.service = service_name

    def submit(self, func, *args):
        try:
            return self.pool.submit(func, *args)
        except concurrent.futures.BrokenExecutor:
            raise Exception(f"Bulkhead full for {self.service}")

# 서비스별 분리 (critical 서비스가 batch 서비스 때문에 못하지 않도록)
critical_pool = BulkheadPool("payment-api", max_workers=10)
batch_pool = BulkheadPool("batch-jobs", max_workers=2)
```

## 변경 전후 비교

**Before: 운영 패턴 없는 분산 시스템**
```text
- 느린 외부 서비스 하나가 전체 쓰레드 풀 점유
- 연쇄 타임아웃으로 전체 서비스 다운
- 과부하 시 큐가 무한히 쌓임
- 장애를 사용자 신고로 인지
```

**After: 운영 패턴 적용**
```text
- Bulkhead로 서비스별 자원 분리
- Circuit Breaker로 연쇄 장애 차단
- Backpressure로 처리 가능한 만큼만 수용
- Observability로 사용자 전에 이상 감지
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| Timeout 없는 외부 호출 | 느린 서비스가 스레드를 무한 점유 | 연결/읽기 timeout 분리 설정 |
| Circuit Breaker 없는 재시도 | 장애 서비스에 계속 호출해 연쇄 장애 | 일정 실패율 초과 시 빠른 실패 |
| 자원 공유 (Bulkhead 없음) | 배치 작업이 실시간 API를 막음 | 서비스 중요도별 자원 분리 |
| Backpressure 없이 무한 큐 | 메모리 고갈 후 OOM | 큐 크기 제한 + 초과 시 거절 |
| Observability 없음 | 장애를 사용자 신고로 인지 | 메트릭/트레이스/로그 기본 탑재 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"외부 결제 API 호출 코드를 만들어줘.
Circuit Breaker (5회 실패 시 30초 차단),
Bulkhead (결제 전용 스레드 풀),
지수 백오프 재시도,
Timeout (연결 3초, 읽기 10초)까지 포함해야 해"

# 운영 패턴 자가 점검:
# - 모든 외부 호출에 timeout이 있는가?
# - 실패가 연쇄되는 경로에 circuit breaker가 있는가?
# - 중요도 다른 워크로드가 자원을 공유하는가? (Bulkhead 필요)
# - 과부하 시 시스템이 어떻게 반응하는가? (Backpressure)
```

## 운영 체크리스트

- [ ] 모든 외부 호출에 timeout이 설정되어 있다
- [ ] Circuit Breaker가 핵심 외부 의존성에 적용되어 있다
- [ ] 중요도별 자원이 Bulkhead로 분리되어 있다
- [ ] 큐/버퍼에 크기 제한이 있다 (Backpressure)
- [ ] 메트릭, 로그, 트레이스가 기본으로 수집된다

## 처음 질문으로 돌아가기

- **Bulkhead가 장애를 격리하는 방법은?** 서비스별로 스레드 풀, 연결 풀을 분리합니다. 한 서비스의 자원 고갈이 다른 서비스에 영향을 주지 않습니다.
- **Circuit Breaker가 연쇄 장애를 끊는 방법은?** 일정 실패율을 초과하면 호출 자체를 차단(fast fail)합니다. 일정 시간 후 반개방 상태에서 테스트 호출로 복구를 확인합니다.
- **Backpressure는 언제 필요한가요?** 소비자가 처리할 수 있는 속도보다 생산 속도가 빠를 때, 무한히 쌓이지 않도록 명시적으로 거절합니다.

## 정리

바이브코딩에서 AI가 만들어 준 분산 시스템 코드에서 timeout, circuit breaker, bulkhead, backpressure 적용 여부를 반드시 확인하세요. 장애는 피하는 것이 아니라 격리하는 것입니다. Distributed Systems 101 시리즈를 통해 분산 시스템 운영의 기초를 갖추셨기를 바랍니다.

## 참고 자료

- [Release It! — Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Circuit Breaker Pattern — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Distributed Systems 기초 (1/10): 분산 시스템이란 무엇인가?
- 바이브코딩을 위한 Distributed Systems 기초 (2/10): 장애 모델
- 바이브코딩을 위한 Distributed Systems 기초 (3/10): RPC와 메시지 패싱
- 바이브코딩을 위한 Distributed Systems 기초 (4/10): 일관성과 CAP
- 바이브코딩을 위한 Distributed Systems 기초 (5/10): 복제
- 바이브코딩을 위한 Distributed Systems 기초 (6/10): 합의와 Raft
- 바이브코딩을 위한 Distributed Systems 기초 (7/10): 리더 선출
- 바이브코딩을 위한 Distributed Systems 기초 (8/10): 메시지 큐와 이벤트 소싱
- 바이브코딩을 위한 Distributed Systems 기초 (9/10): 분산 트랜잭션
- **바이브코딩을 위한 Distributed Systems 기초 (10/10): 운영 가능한 분산 시스템 패턴 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, DistributedSystems, CircuitBreaker, Resilience, Backpressure, Observability
