---
title: "바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템"
series: sre-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SRE
  - Operability
  - Resilience
  - CircuitBreaker
---

# 바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템

이 글은 "바이브코딩을 위한 SRE 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 기능 코드를 빠르게 만들어 줍니다. 그런데 기능이 동작하는 것과 그 기능을 운영할 수 있는 것은 다릅니다. 코드가 배포된 순간부터 질문이 달라집니다. 장애가 났을 때 원인을 찾을 수 있는가? 배포를 안전하게 롤백할 수 있는가? 외부 의존성 하나가 느려져도 전체가 무너지지 않는가?

AI가 만든 코드는 기능 요구사항을 충족합니다. 하지만 관측성, 안전 배포, 복원력, 자동화 수준이 빠진 채 프로덕션에 올라가면 운영 팀은 블랙박스를 관리하게 됩니다. 장애가 났을 때 안에서 무슨 일이 일어나는지 보이지 않고, 어디서부터 확인해야 할지 모릅니다.

운영 가능한 시스템은 처음부터 설계에 포함해야 합니다. 로그가 있고, 배포를 단계적으로 할 수 있고, 외부 의존성 실패를 격리하고, 핵심 작업은 자동화된 시스템을 만드는 것이 SRE 관점의 완성입니다.

> **핵심 인사이트:** 운영 가능성은 배포 후 추가하는 것이 아니라 설계 단계에서 요구사항으로 포함해야 합니다. 관측성, 안전 배포, 복원력, 자동화 네 가지가 모두 갖춰진 시스템은 장애가 나도 빠르게 복구되고, 성장해도 운영 부담이 늘지 않습니다.

## 이 글에서 다룰 문제

- 운영 가능한 시스템의 4가지 요소는 무엇인가요?
- 서킷브레이커는 어떻게 외부 의존성 실패를 격리할까요?
- 안전 배포는 어떤 절차로 이루어질까요?
- 운영 성숙도 4단계는 어떻게 평가할까요?
- AI가 만든 시스템에서 운영 가능성 관점으로 확인할 것은 무엇인가요?

## 운영 가능한 시스템 핵심 패턴

```python
# 운영 가능성 4요소 점검
def has_obs(service):
    """관측성: 로그, 메트릭, 트레이스"""
    return all([
        service.get("structured_logs"),
        service.get("metrics"),
        service.get("tracing"),
    ])

def safe_deploy(service):
    """안전 배포: 단계적 롤아웃 + 롤백 능력"""
    return service.get("canary") and service.get("rollback_proc")

def has_resilience(service):
    """복원력: 서킷브레이커 + 재시도"""
    return service.get("circuit_breaker") and service.get("retry_policy")

def auto_ratio(service):
    """자동화 비율: 수동 작업 대비"""
    manual = service.get("manual_tasks", 0)
    total = service.get("total_ops", 1)
    return 1.0 - manual / total  # 높을수록 좋음
```

```python
# 서킷브레이커: 외부 의존성 실패 격리
import time

class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "CLOSED", "OPEN", "HALF_OPEN"

    def __init__(self, threshold=5, timeout_sec=60):
        self.state = self.CLOSED
        self.failures = 0
        self.threshold = threshold
        self.opened_at = None
        self.timeout_sec = timeout_sec

    def call(self, fn, *args, **kwargs):
        if self.state == self.OPEN:
            if time.time() - self.opened_at > self.timeout_sec:
                self.state = self.HALF_OPEN
            else:
                raise RuntimeError("Circuit OPEN: 외부 서비스 격리 중")

        try:
            result = fn(*args, **kwargs)
            self.failures = 0
            if self.state == self.HALF_OPEN:
                self.state = self.CLOSED
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = self.OPEN
                self.opened_at = time.time()
            raise

# 재시도 + 지수 백오프 + 지터
import random

def retry_with_backoff(fn, max_attempts=3, base_delay=1.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(delay)
```

```python
# 단계적 배포: 카나리 → 25% → 50% → 100%
deployment_stages = [
    {"name": "canary",  "traffic_pct": 5,   "wait_min": 10},
    {"name": "partial", "traffic_pct": 25,  "wait_min": 30},
    {"name": "half",    "traffic_pct": 50,  "wait_min": 30},
    {"name": "full",    "traffic_pct": 100, "wait_min": 0},
]

def should_proceed(stage, metrics):
    """각 단계에서 진행 여부 결정"""
    return (
        metrics["error_rate"] < 0.01 and   # 오류율 1% 미만
        metrics["p99_ms"] < 500             # p99 지연 500ms 미만
    )
```

## 변경 전후 비교

**Before: 운영 가능성 없는 시스템**
```text
- print()로만 로그 출력 (검색 불가)
- 전체 트래픽 한 번에 배포
- 외부 API 타임아웃 → 전체 서비스 응답 멈춤
- 수동 배포 후 수동 점검
- 장애 시 어디서부터 봐야 할지 모름
```

**After: 운영 가능한 시스템**
```text
- JSON 구조화 로그 + 메트릭 + 트레이스
- 카나리(5%) → 25% → 50% → 100% 단계 배포
- 서킷브레이커로 외부 의존성 실패 격리
- 배포 파이프라인 자동화 (Toil 0)
- 장애 원인을 correlationId로 즉시 추적
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 관측성을 배포 후 추가 | 첫 장애 때 원인 파악 불가 | 로그/메트릭/트레이스를 설계 단계 요구사항으로 |
| 전체 롤아웃 한 번에 | 문제 감지 전 전체 사용자 영향 | 카나리부터 단계적 배포 |
| 서킷브레이커 없이 외부 호출 | 의존성 실패가 전파되어 연쇄 장애 | 모든 외부 호출에 서킷브레이커 적용 |
| 재시도에 지터 없음 | 동시 재시도로 의존성에 폭풍 | 지수 백오프 + 랜덤 지터 필수 |
| 운영 성숙도 평가 없음 | 개선 우선순위 불명확 | 분기마다 4요소 성숙도 점검 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Python 외부 API 클라이언트에 서킷브레이커와 재시도를 추가해줘.
실패 5회 초과 시 60초 OPEN, HALF_OPEN 상태에서 1회 테스트,
재시도는 지수 백오프 + 지터 포함, 최대 3회"

# AI 결과물 검증 체크포인트:
# - 서킷브레이커가 CLOSED/OPEN/HALF_OPEN 세 상태를 모두 구현하는가?
# - 재시도에 지터가 포함되어 있는가?
# - 서킷브레이커 상태 변화가 로그로 기록되는가?
# - 배포가 단계적으로 진행되고 각 단계에서 메트릭을 확인하는가?
# - 관측성(로그/메트릭/트레이스)이 모두 설계에 포함되는가?
```

## 운영 체크리스트

- [ ] 구조화 로그, 메트릭, 트레이스가 모두 설정되어 있다
- [ ] 배포가 카나리부터 단계적으로 진행되고 각 단계에서 메트릭을 확인한다
- [ ] 모든 외부 의존성 호출에 서킷브레이커가 적용되어 있다
- [ ] 재시도 정책에 지수 백오프와 지터가 포함된다
- [ ] 운영 성숙도(관측성/배포/복원력/자동화)를 분기마다 평가한다

## 처음 질문으로 돌아가기

- **운영 가능한 시스템의 4요소는?** 관측성(로그/메트릭/트레이스), 안전 배포(카나리/단계적 롤아웃/롤백), 복원력(서킷브레이커/재시도/지터), 자동화(Toil 제거/파이프라인). 하나라도 빠지면 운영 부담이 그 지점에 집중됩니다.
- **서킷브레이커는 왜 필요한가?** 외부 서비스가 느려지거나 실패할 때 계속 요청을 보내면 스레드와 커넥션이 고갈되어 내 서비스도 멈춥니다. 서킷브레이커는 실패가 임계값을 초과하면 즉시 차단하고, 일정 시간 후 조심스럽게 복구를 시도합니다.
- **운영 성숙도를 어떻게 높이는가?** 1단계(기본 로그/수동 배포) → 2단계(구조화 로그/단계적 배포) → 3단계(메트릭+트레이스/자동 롤백) → 4단계(전체 자동화/서킷브레이커) 순으로 점진적으로 높입니다. 한 번에 전부 하려면 실패합니다.

## 정리

바이브코딩에서 AI가 만든 시스템이 기능은 동작해도 관측성, 안전 배포, 복원력, 자동화가 없으면 프로덕션에서 오래 버티기 어렵습니다. 이 네 가지를 설계 단계부터 요구사항으로 포함하세요. SRE 101 시리즈를 통해 SRE 기초, 신뢰성 지표, 에러 예산, 모니터링, 장애 대응, 포스트모템, Toil 관리, 용량 계획, 운영 가능성까지 바이브코딩 시대의 SRE 핵심을 다뤘습니다.

## 참고 자료

- [Site Reliability Engineering — Google](https://sre.google/sre-book/table-of-contents/)
- [Production Readiness Review — Google SRE](https://sre.google/sre-book/evolving-sre-engagement-model/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SRE 기초 (1/10): SRE란 무엇인가?
- 바이브코딩을 위한 SRE 기초 (2/10): 신뢰성
- 바이브코딩을 위한 SRE 기초 (3/10): SLI, SLO, SLA
- 바이브코딩을 위한 SRE 기초 (4/10): 에러 예산
- 바이브코딩을 위한 SRE 기초 (5/10): 모니터링
- 바이브코딩을 위한 SRE 기초 (6/10): 장애 대응
- 바이브코딩을 위한 SRE 기초 (7/10): 포스트모템
- 바이브코딩을 위한 SRE 기초 (8/10): Toil 줄이기
- 바이브코딩을 위한 SRE 기초 (9/10): 용량 계획
- **바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, SRE, Operability, Resilience, CircuitBreaker
