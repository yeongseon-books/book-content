---
episode: 10
language: ko
last_reviewed: '2026-05-14'
seo_description: 관측성, 자동화, 안전한 변경, 회복력을 갖춘 운영 가능한 시스템 설계 원칙으로 SRE 시리즈를 마무리합니다.
series: sre-101
status: content-ready
tags:
- SRE
- Operability
- Architecture
- Reliability
- Engineering
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "SRE 101 (10/10): 운영 가능한 시스템 만들기"
---

# SRE 101 (10/10): 운영 가능한 시스템 만들기

많은 시스템은 기능 요구사항은 자세히 적지만, 운영 요구사항은 나중 문제로 남겨 둡니다. 서비스가 커지고 장애가 생긴 뒤에야 로그를 더 남기고, 롤백 절차를 만들고, 자동화를 붙이기 시작합니다. 그런데 운영성은 뒤늦게 덧붙일수록 비용이 더 큽니다.

운영하기 쉬운 시스템은 우연히 만들어지지 않습니다. 문제가 생겼을 때 빨리 볼 수 있어야 하고, 변경을 안전하게 되돌릴 수 있어야 하며, 부분 실패가 전체 붕괴로 번지지 않아야 하고, 반복 운영 절차는 가능한 한 코드로 옮겨져 있어야 합니다.

이 글은 SRE 101 시리즈의 마지막 글입니다. 여기서는 operability를 기능과 함께 설계해야 하는 품질로 보고, 관측성, 자동화, 안전한 변경, 회복력을 한 시스템 안에서 어떻게 묶어 볼지 정리합니다.

![SRE 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/10/10-01-concept-at-a-glance.ko.png)
*SRE 101 10장 흐름 개요*
> 나눰 단계를 멘 나대 멘 메 나나 멘 나대 멘 메 나나 멘 낤낰니다.

## 먼저 던지는 질문

- operability는 왜 기능 뒤에 붙이는 옵션이 아니라 설계 요소일까요?
- 관측성, 자동화, 안전한 변경, 회복력은 왜 함께 봐야 할까요?
- 운영 가능한 시스템을 점검할 때 어떤 질문부터 던져야 할까요?

## 왜 이 주제가 중요한가

운영성이 없는 기능은 시간이 지나면 부채로 돌아옵니다. 기능은 잘 만들어졌는데 로그가 부족하고, 배포는 되는데 롤백이 어렵고, 장애는 복구되는데 같은 절차를 매번 사람이 반복해야 한다면 팀은 점점 느려집니다.

반대로 운영성이 내장된 시스템은 장애를 더 빨리 읽고, 변경을 더 작고 안전하게 내보내며, 부분 실패를 전체 실패로 키우지 않고, 반복 업무를 자동화로 흡수합니다. 서비스가 커질수록 이 차이는 더 크게 벌어집니다.

## 한 문장으로 잡는 멘탈 모델

> 운영성은 출시 후에 덧붙이는 장식이 아니라, 처음부터 기능과 함께 설계해야 하는 품질 속성입니다.

## 한눈에 보는 구조

운영 가능한 시스템은 한 가지 도구로 만들어지지 않습니다. 관측성, 자동화, 안전한 변경, 회복력이 함께 맞물려야 운영성이 생기고, 그 운영성이 결국 고객 신뢰로 이어집니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 실무에서 보는 포인트 |
| --- | --- | --- |
| operability | 시스템을 운영하고 문제를 다루기 쉬운 정도 | 기능 품질의 일부입니다 |
| observability | 외부 신호로 내부 상태를 추론하는 능력 | 디버깅의 출발점이 됩니다 |
| safe change | 작고 되돌리기 쉬운 변경 방식 | 배포 위험을 줄입니다 |
| resilience | 부분 실패에서 버티고 회복하는 능력 | 장애 확산을 막습니다 |
| runbook-as-code | 운영 절차를 코드로 표현한 방식 | 사람 의존적 절차를 줄입니다 |

## 운영성은 왜 기능과 함께 설계해야 할까

기능 개발이 끝난 뒤 운영 요소를 붙이려 하면 늘 타협이 생깁니다. 로그는 빠져 있고, 메트릭 이름은 제각각이고, 롤백은 수동이며, 장애 대응 절차는 특정 담당자 경험에 기대게 됩니다. 이 상태에서는 기능이 늘수록 운영 복잡도도 함께 커집니다.

반대로 처음부터 운영성을 요구사항으로 보면 설계 질문이 달라집니다. 이 기능은 어떤 메트릭을 남겨야 하는가, 실패하면 어떻게 우회할 것인가, 카나리 배포가 가능한가, 롤백은 몇 분 안에 가능한가, 반복 운영 절차를 코드로 표현할 수 있는가 같은 질문이 설계 초기에 들어옵니다.

## 네 가지 축을 함께 봐야 하는 이유

관측성이 없으면 문제를 읽을 수 없습니다. 안전한 변경이 없으면 작은 실수도 크게 퍼집니다. 회복력이 없으면 부분 실패가 연쇄 장애로 번집니다. 자동화가 없으면 팀 시간이 반복 수작업에 묶입니다. 한 축만 좋아서는 운영성이 생기지 않습니다.

그래서 operability audit를 할 때도 여러 축을 한 번에 보는 편이 좋습니다. 현재 시스템이 어디에서 가장 약한지 드러나기 때문입니다. 보통은 한 축의 부족함이 다른 축의 부담으로 이어집니다.

## 운영 가능한 시스템 특성

운영 가능한 시스템은 몇 가지 공통 특성을 가집니다. 각 특성을 체크리스트로 만들면 설계 검토나 코드 리뷰 단계에서 활용할 수 있습니다.

| 특성 | 확인 기준 | 예시 |
| --- | --- | --- |
| 관측 가능 | 메트릭, 로그, 트레이스가 모두 있는가 | Prometheus + Loki + Jaeger |
| 점진 배포 | 카나리 또는 블루-그린 가능한가 | canary 5% → 100% |
| 자동 복구 | 재시도, 타임아웃, 서킷 브레이커 존재하는가 | retry 3회, timeout 5초 |
| 문서화 | runbook, 아키텍처 다이어그램, API 명세가 있는가 | README + ADR + OpenAPI |

이 특성들은 기능을 추가하기 전에 미리 반영해야 합니다. 기능이 완성된 뒤에 붙이려고 하면 비용이 훨씬 커집니다.
## 단계별로 운영성 점검하기

### 1단계 — 관측성 확인

```python
def has_obs(metrics, logs, traces):
    return all([metrics, logs, traces])
```

메트릭, 로그, 트레이스는 각자 다른 질문에 답합니다. 세 가지가 함께 있어야 내부 상태를 더 정확하게 추론할 수 있고, 디버깅 속도도 빨라집니다.

### 2단계 — 안전한 배포 확인

```python
def safe_deploy(canary_pct, rollback_ready):
    return canary_pct <= 5 and rollback_ready
```

운영 가능한 시스템은 변경도 작고 되돌리기 쉬워야 합니다. 카나리와 롤백 준비 여부를 함께 보는 이유가 여기에 있습니다. 배포가 항상 전면 적용이라면 작은 실수도 큰 장애로 번질 수 있습니다.

### 3단계 — 회복 패턴 확인

```python
def has_resilience(retry, timeout, breaker):
    return all([retry, timeout, breaker])
```

재시도, 타임아웃, 서킷 브레이커 같은 패턴은 부분 실패를 가두는 장치입니다. 이런 장치가 없으면 작은 외부 의존성 문제도 전체 요청 흐름을 무너뜨릴 수 있습니다.

### 4단계 — 자동화 비율 확인

```python
def auto_ratio(auto_min, total_min):
    return auto_min / total_min
```

반복 절차를 사람이 계속 수행한다면 운영성은 아직 약합니다. 자동화 비율은 팀 시간이 구조 개선으로 향하고 있는지, 아니면 반복 수작업에 갇혀 있는지 보여 줍니다.

### 5단계 — 운영성 점수 계산

```python
def score(obs, deploy, resil, auto):
    return sum([obs, deploy, resil, auto >= 0.7]) / 4
```

운영성은 추상적이지만, 이런 식으로 차원별 점검 항목으로 나누면 우선순위를 정하기 쉬워집니다. 완벽한 점수를 만들기보다 약한 축을 빨리 드러내는 데 의미가 있습니다.

## 운영 성숙도 모델

운영 가능한 시스템은 단계적으로 만들어집니다. 각 레벨에서 어떤 능력이 추가되는지 보면 현재 위치와 다음 목표를 파악하기 쉬워집니다.

### Level 1 — 반응형 운영

- 장애가 나면 수동으로 대응합니다
- 모니터링은 있으나 알림 기준이 모호합니다
- 배포는 수동이며, 롤백도 수동입니다
- 문서화는 일부 사람의 기억에 의존합니다

### Level 2 — 체계화된 운영

- 모니터링 메트릭과 알림 기준이 명확합니다
- 배포는 CI/CD 파이프라인으로 자동화됩니다
- runbook이 존재하며 주요 절차가 문서화되어 있습니다
- 롤백은 가능하지만 수동입니다

### Level 3 — 예방적 운영

- SLO와 에러 버짓이 정의되어 있습니다
- 카나리 배포가 기본이며, 문제 시 자동 롤백됩니다
- 장애 대응 프로세스가 정형화되고, 포스트모템이 표준화되어 있습니다
- Toil 비율을 측정하고 줄이는 작업이 있습니다

### Level 4 — 자율 운영

- 대부분의 장애가 자동으로 감지되고 복구됩니다
- 용량 계획이 데이터 기반으로 수행됩니다
- 배포는 점진적이며, 테스트 커버리지가 높습니다
- 복잡한 장애 시나리오를 주기적으로 테스트합니다 (chaos engineering)

대부분의 팀은 Level 2와 3 사이에 있습니다. 중요한 것은 현재 위치를 인정하고, 다음 레벨로 올라가기 위해 무엇을 개선해야 할지 아는 것입니다.

## 첫 SRE 도입 로드맵

SRE 원칙을 처음 도입하는 팀은 어디서부터 시작해야 할까요? 모든 것을 한께번에 바꾸려고 하면 부담이 큽니다. 단계적으로 접근하면 성공 가능성이 높아집니다.

### 1단계 (1-2개월) — 가시성 확보

- [ ] 핵심 메트릭 3-5개 선정 (latency, error rate, throughput)
- [ ] 모니터링 대시보드 구성
- [ ] 임계값 초과 시 알림 설정
- [ ] 장애 대응 채널 생성 (Slack/Teams)

### 2단계 (3-4개월) — 목표 설정

- [ ] 핵심 서비스의 SLI 정의
- [ ] SLO 목표값 설정 (99%, 99.9% 등)
- [ ] 에러 버짓 개념 도입
- [ ] 장애 심각도 분류 기준 문서화

### 3단계 (5-6개월) — 프로세스 정형화

- [ ] 포스트모템 템플릿 제정
- [ ] 장애 대응 역할 정의 (IC, ops lead, comms lead)
- [ ] Toil 측정 시작
- [ ] 자동화 후보 목록 작성

### 4단계 (7-12개월) — 엔지니어링 실행

- [ ] 자동화 프로젝트 진행
- [ ] 용량 계획 모델 구축
- [ ] CI/CD 파이프라인 개선
- [ ] 카나리 배포 도입

이 로드맵은 팀의 현재 상태에 따라 조정할 수 있습니다. 중요한 것은 한 번에 모든 것을 도입하려고 하지 말고, 각 단계를 착실히 진행하는 것입니다.

## Runbook-as-Code 실전 예시

운영 절차를 Wiki에만 남기면 시간이 지나면서 실제 시스템과 괴리가 생깁니다. 코드로 작성하면 문서이자 실행 가능한 자동화가 되어, 항상 최신 상태를 유지할 수 있습니다.

```python
"""
Runbook: DB 커넥션 풀 고갈 대응
트리거: active_connections / max_connections > 0.9
예상 원인: 배치 작업 커넥션 미반환, 슬로우 쿼리 증가
"""

import subprocess
import json
from datetime import datetime

def diagnose_connection_pool():
    """1단계: 현재 상태 진단"""
    checks = {
        "active_connections": get_metric("active_db_connections"),
        "max_connections": get_metric("max_db_connections"),
        "waiting_queries": get_metric("db_queries_waiting"),
        "slow_queries_5min": get_metric("db_slow_queries_total", range="5m"),
    }
    
    utilization = checks["active_connections"] / checks["max_connections"]
    checks["utilization_pct"] = f"{utilization * 100:.1f}%"
    checks["severity"] = "critical" if utilization > 0.95 else "warning"
    
    return checks

def mitigate_connection_pool():
    """2단계: 즉시 완화 조치"""
    actions = []
    
    # 유휴 커넥션 강제 해제
    result = execute_db_command(
        "SELECT pg_terminate_backend(pid) "
        "FROM pg_stat_activity "
        "WHERE state = 'idle' "
        "AND state_change < now() - interval '5 minutes'"
    )
    actions.append(f"유휴 커넥션 {result['terminated']}개 해제")
    
    # 배치 작업 일시 중단
    pause_batch_jobs()
    actions.append("배치 작업 일시 중단")
    
    return actions

def verify_recovery():
    """3단계: 복구 확인"""
    state = diagnose_connection_pool()
    utilization = float(state["utilization_pct"].replace("%", ""))
    
    if utilization < 70:
        return {"status": "recovered", "utilization": state["utilization_pct"]}
    else:
        return {"status": "not_recovered", "utilization": state["utilization_pct"]}
```

이 코드는 Wiki 문서보다 세 가지 점에서 낫습니다. 첫째, 실행 가능합니다. 둘째, 테스트할 수 있습니다. 셋째, 코드 리뷰를 통해 최신 상태를 유지할 수 있습니다.

## 회복력 패턴 구현

부분 실패가 전체 장애로 번지지 않으려면 회복력 패턴이 필요합니다. 재시도, 타임아웃, 서킷 브레이커는 가장 기본적인 세 가지 패턴입니다.

### 서킷 브레이커 구현

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # 정상 동작
    OPEN = "open"          # 차단 (요청 거부)
    HALF_OPEN = "half_open"  # 시험적 허용

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit is open, request rejected")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitOpenError(Exception):
    pass
```

서킷 브레이커는 외부 의존성(데이터베이스, 외부 API 등)이 응답하지 않을 때 연쇄 장애를 막아 줍니다. 실패가 임계값을 넘으면 요청 자체를 차단하여 시스템 자원을 보호하고, 일정 시간 후 시험적으로 요청을 보내 복구 여부를 확인합니다.

### 재시도와 지수 백오프

```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=30.0):
    """지수 백오프를 적용한 재시도"""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise e
            
            # 지수 백오프 + 지터(jitter)
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            
            print(f"시도 {attempt + 1} 실패, {delay + jitter:.1f}초 후 재시도")
            time.sleep(delay + jitter)
```

지터(jitter)를 추가하는 이유는 여러 클라이언트가 동시에 재시도하면서 서버에 부하를 집중시키는 "thundering herd" 문제를 방지하기 위해서입니다.

## 운영성 감사(Operability Audit) 체크리스트

새 서비스를 프로덕션에 배포하기 전, 또는 기존 서비스의 운영성을 개선하려면 다음 체크리스트로 감사를 수행합니다.

### 관측성

- [ ] 골든 시그널(latency, traffic, errors, saturation) 메트릭이 수집되는가?
- [ ] 구조화 로그가 trace_id를 포함하는가?
- [ ] 분산 트레이싱으로 서비스 간 요청을 추적할 수 있는가?
- [ ] SLO 대시보드가 구성되어 있는가?
- [ ] 에러 버짓 burn rate 알림이 설정되어 있는가?

### 안전한 변경

- [ ] 카나리 배포가 가능한가? (5% → 25% → 100%)
- [ ] 1분 이내 롤백이 가능한가?
- [ ] feature flag로 기능을 끌 수 있는가?
- [ ] 데이터베이스 마이그레이션이 backward-compatible한가?
- [ ] 배포 후 자동 검증(smoke test)이 실행되는가?

### 회복력

- [ ] 외부 의존성에 타임아웃이 설정되어 있는가?
- [ ] 서킷 브레이커가 적용되어 있는가?
- [ ] 재시도에 지수 백오프와 지터가 적용되는가?
- [ ] 부분 장애 시 우아한 성능 저하(graceful degradation)가 가능한가?
- [ ] 단일 장애점(SPOF)이 제거되어 있는가?

### 자동화

- [ ] 반복 운영 작업의 50% 이상이 자동화되어 있는가?
- [ ] runbook이 코드 형태로 관리되는가?
- [ ] 장애 복구 절차가 스크립트로 실행 가능한가?
- [ ] 인증서 갱신, 로그 정리 등이 자동화되어 있는가?
- [ ] 용량 증설이 자동 또는 반자동으로 가능한가?

각 항목이 "아니오"라면 운영 위험이 존재합니다. 이 체크리스트를 PRR(Production Readiness Review)의 일부로 사용하면 프로덕션 배포 전 운영성을 체계적으로 확보할 수 있습니다.

## 시리즈 전체 요약

SRE 101 시리즈에서 다룬 10개 주제는 독립된 개념이 아니라, 하나의 운영 체계를 구성하는 부품들입니다.

| 글 | 핵심 질문 | 실무 산출물 |
| --- | --- | --- |
| 1. SRE란 | 운영을 어떻게 공학화하는가? | SRE 도입 판단 기준 |
| 2. Reliability | 신뢰성을 어떤 차원으로 보는가? | 차원별 측정 체계 |
| 3. SLI/SLO/SLA | 무엇을 재고, 어디까지 약속하는가? | SLO 문서, SLA 계약 |
| 4. Error Budget | 얼마나 실패를 감수하는가? | 버짓 정책, 릴리스 규칙 |
| 5. Monitoring | 어떤 신호를 볼 것인가? | 대시보드, 알림 설계 |
| 6. Incident Response | 장애 시 누가 어떻게 움직이는가? | 역할 매트릭스, 커뮤니케이션 템플릿 |
| 7. Postmortem | 장애에서 무엇을 배우는가? | 포스트모템 템플릿, 액션 추적 |
| 8. Toil 줄이기 | 어떤 반복 작업을 자동화하는가? | Toil 추적표, 자동화 로드맵 |
| 9. Capacity Planning | 언제 자원을 늘려야 하는가? | 용량 모델, 예측 스프레드시트 |
| 10. 운영 가능한 시스템 | 처음부터 운영성을 어떻게 설계하는가? | PRR 체크리스트, 성숙도 모델 |

이 체계가 잘 맞물리면 장애는 줄고, 변경은 더 빠르고 안전해지며, 팀은 반복 작업 대신 시스템 개선에 시간을 쓸 수 있습니다. SRE의 궁극적 목표는 더 많은 운영 업무를 맡는 것이 아니라, 운영에 필요한 사람 시간을 줄이면서 신뢰성을 높이는 것입니다.

## 이 코드에서 먼저 봐야 할 점

- 운영성은 네 가지 축의 결합으로 봐야 합니다.
- 운영성은 문서 주장보다 실제 구현 여부로 확인해야 합니다.
- 안전한 변경과 회복력은 장애 확산을 줄이는 핵심 장치입니다.
- 자동화는 팀 시간을 지키는 운영성 요소입니다.

## 여기서 자주 헷갈립니다

첫 번째 실수는 operability를 나중 문제로 미루는 것입니다. 이 선택은 나중에 더 큰 비용으로 돌아옵니다.

두 번째 실수는 observability가 부족한데도 장애 대응 절차만 강화하려는 것입니다. 보이지 않는 시스템은 잘 대응할 수도 없습니다.

세 번째 실수는 카나리와 롤백 없이 전면 배포를 반복하는 것입니다. 안전한 변경 경로가 없으면 팀은 점점 변경을 두려워하게 됩니다.

## 운영 체크리스트

- [ ] 메트릭, 로그, 트레이스를 모두 확보했다.
- [ ] 카나리와 롤백 절차가 준비되어 있다.
- [ ] 재시도, 타임아웃, 서킷 브레이커 같은 회복 패턴을 점검했다.
- [ ] 반복 운영 절차의 자동화 수준을 측정한다.
- [ ] 운영성 약점을 차원별로 점검하고 우선순위를 정한다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 운영성을 기능의 부가 옵션으로 보지 않습니다. 시스템이 커질수록 운영성이 없는 기능은 더 큰 비용과 더 느린 변경 속도로 되돌아오기 때문입니다.

또한 플랫폼팀이 공통 로깅, 배포, 롤백, 알림 템플릿을 제공하면 제품팀은 비즈니스 기능에 더 집중할 수 있습니다. 운영성을 개별 팀의 감각에 맡기지 않고, 공통 기반으로 끌어올리는 방식입니다.

## 관측 가능한 시스템 평가 체크리스트

관측성(observability)은 운영 가능한 시스템의 기초입니다. 다음 질문으로 현재 시스템의 관측성을 평가할 수 있습니다.

- [ ] 핵심 비즈니스 메트릭이 정의되고 수집되고 있나요? (RPS, latency, error rate)
- [ ] 모든 서비스가 구조화된 로그를 남기나요? (JSON 형식, trace ID 포함)
- [ ] 분산 트레이싱이 구현되어 있나요? (요청 전체 경로 추적 가능)
- [ ] 대시보드에서 현재 상태를 5분 안에 파악할 수 있나요?
- [ ] 알림 기준이 SLO에 기반하며, 오탐지가 낮나요? (<5% false positive)
- [ ] 장애 시 어떤 서비스가 영향을 받았는지 의존성 그래프로 확인할 수 있나요?

이 체크리스트를 모두 통과하면 관측 가능한 시스템으로 볼 수 있습니다. 하나라도 빠지면 장애 대응 속도가 크게 느려집니다.

## 안전한 배포 패턴

안전한 배포는 변경을 작고 되돌리기 쉬운 단위로 나눠서 내보내는 것입니다. 전면 배포 대신 점진적 패턴을 사용하면 위험을 크게 줄일 수 있습니다.

```python
# 점진적 배포 패턴
deployment_stages = [
    {"name": "canary", "traffic_pct": 5, "duration_min": 10},
    {"name": "pilot", "traffic_pct": 25, "duration_min": 20},
    {"name": "full", "traffic_pct": 100, "duration_min": 0},
]

def should_proceed(stage, metrics):
    """Check if metrics are healthy before proceeding to next stage"""
    thresholds = {
        "error_rate": 0.01,  # 1%
        "latency_p99_ms": 1000,
        "cpu_pct": 80
    }
    
    return all(
        metrics[key] <= threshold
        for key, threshold in thresholds.items()
    )

# 예시
current_metrics = {
    "error_rate": 0.005,
    "latency_p99_ms": 850,
    "cpu_pct": 65
}

if should_proceed("canary", current_metrics):
    print("✅ Canary 통과, pilot 단계로 진행")
else:
    print("❌ Canary 실패, 롤백 필요")
```

이 패턴은 각 단계에서 메트릭을 검증하고, 문제가 없을 때만 다음 단계로 나아갑니다. 문제가 발견되면 즉시 롤백하여 영향 범위를 최소화합니다.

## 운영 가능한 시스템 설계 원칙

운영 가능한 시스템을 처음부터 만들려면 몇 가지 설계 원칙을 염두에 두어야 합니다. 이 원칙들은 기능 개발과 함께 적용할 수 있습니다.

### 원칙 1 — 실패는 항상 일어난다

모든 컴포넌트는 언젠가 실패합니다. 네트워크는 끊기고, 디스크는 가득 차고, 외부 API는 타임아웃됩니다. 실패를 예외로 보지 말고 정상 동작의 일부로 설계해야 합니다.

### 원칙 2 — 관측 가능하지 않으면 디버그 불가능

메트릭, 로그, 트레이스가 없는 시스템은 블랙박스입니다. 장애가 나도 원인을 찾을 수 없고, 추측에 의존하게 됩니다. 모든 기능은 관측 가능하게 만들어야 합니다.

### 원칙 3 — 작고 자주 배포하라

큰 변경은 위험도 크고, 문제가 생겼을 때 원인 범위도 넓습니다. 작은 변경을 자주 배포하면 각 변경의 영향을 빨리 파악할 수 있고, 롤백도 쉽습니다.

### 원칙 4 — 자동화는 반복 작업부터

모든 작업을 한 번에 자동화할 수는 없습니다. 빈도가 높고, 위험이 낮고, 절차가 명확한 작업부터 자동화해야 합니다. 자동화는 팀 시간을 지키는 투자입니다.

### 원칙 5 — 장애 대응 절차는 코드로 문서화

runbook을 Wiki에만 남기면 오래되기 쉽습니다. 절차를 스크립트로 만들어 두면 문서이자 실행 가능한 자동화가 됩니다. 코드는 문서보다 정직합니다.

이 원칙들을 모든 새로운 기능에 적용하면, 시간이 지나도 운영 부담이 선형으로 늘지 않습니다.
## 정리

운영 가능한 시스템은 관측성, 자동화, 안전한 변경, 회복력이 함께 설계된 시스템입니다. SRE에서 다룬 SLO, 에러 버짓, 모니터링, 인시던트 대응, 포스트모템, Toil 감소, 용량 계획은 모두 이 운영성을 만들기 위한 서로 다른 관문이었습니다.

이로써 SRE 101 시리즈를 마칩니다. 다음에는 더 깊은 장애 대응이나 서비스별 운영 주제로 들어가며, 여기서 다룬 기본 원칙을 더 구체적인 사례에 적용하게 됩니다.

## 처음 질문으로 돌아가기

- **operability는 왜 기능 뒤에 붙이는 옵션이 아니라 설계 요소일까요?**
  - 본문의 기준은 운영 가능한 시스템 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **관측성, 자동화, 안전한 변경, 회복력은 왜 함께 봐야 할까요?**
  - 각 기능이 언제 무엇 때문에 실패할 수 있는지, 그 신호를 어떻게 빨리 감지할지가 운영 비용을 크게 좌우합니다.
- **운영 가능한 시스템을 점검할 때 어떤 질문부터 던져야 할까요?**
  - 설계 단계에서 운영을 함께 고려하면, 나중에 사람이 손수 해야 할 일이 훨씬 줄어듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
- [SRE 101 (8/10): Toil 줄이기](./08-reducing-toil.md)
- [SRE 101 (9/10): Capacity Planning](./09-capacity-planning.md)
- **운영 가능한 시스템 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Building Secure and Reliable Systems - Google](https://sre.google/books/building-secure-reliable-systems/)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Resilience Engineering - Wikipedia](https://en.wikipedia.org/wiki/Resilience_engineering)
- [Observability Engineering - O'Reilly](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

Tags: SRE, Operability, Architecture, Reliability, Engineering
