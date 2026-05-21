---
episode: 9
language: ko
last_reviewed: '2026-05-15'
seo_description: incident 학습을 회귀 테스트, guardrail, chaos 실험으로 바꿔 재발 가능성을 줄이는 예방 방법을 설명합니다.
series: incident-response-101
status: publish-ready
tags:
- Incident
- Prevention
- Reliability
- Testing
- Operations
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Incident Response 101 (9/10): 재발 방지"
---

# Incident Response 101 (9/10): 재발 방지

이 글은 Incident Response 101 시리즈의 아홉 번째 글입니다.

사후 분석 문서까지 마쳤다고 해서 incident 대응이 끝난 것은 아닙니다. 그 문서가 다시 코드, 테스트, 운영 규칙으로 돌아가지 않으면 조직은 같은 실수를 반복합니다.

그래서 재발 방지는 좋은 회고를 남기는 일이 아니라, 학습을 시스템에 박아 넣는 일에 가깝습니다. 기억보다 테스트와 guardrail이 먼저 막아 주는 상태를 만들어야 합니다.

이 글은 Incident Response 101 시리즈의 9번째 글입니다. 여기서는 후속 조치 추적, 회귀 테스트, guardrail, chaos 실험을 하나의 예방 루프로 묶는 방법을 다룹니다.

## 먼저 던지는 질문

- 사후 분석 뒤에 왜 같은 incident가 다시 반복될까요?
- 후속 조치 추적이 없으면 어떤 문제가 생길까요?
- 회귀 테스트는 왜 재발 방지의 핵심일까요?

## 큰 그림

![Incident Response 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/09/09-01-diagram-at-a-glance.ko.png)

*Incident Response 101 9장 흐름 개요*

재발 방지는 postmortem의 행동 단계입니다. 코드, 모니터링, 문서 개선으로 다음 사건을 빠르게 처리합니다.

> 재발 방지 항목이 구체적일수록 다음 대응이 빠릅니다. 작은 변경도 큰 영향을 줍니다.

## 왜 이 주제가 중요한가

incident는 한 번 해결했다고 사라지지 않습니다. 같은 조건이 남아 있으면 언젠가 같은 방식으로 다시 드러납니다. 그래서 재발 방지는 “다음엔 조심하자”가 아니라, 다음에 같은 실수를 해도 시스템이 막아 주도록 바꾸는 과정이어야 합니다.

또한 예방은 신뢰성 투자 방식을 바꿉니다. 사람 기억에 기대는 조직은 시간이 지날수록 약해지고, 코드와 테스트에 학습을 남기는 조직은 시간이 지날수록 강해집니다. 문서가 출발점이라면, 테스트와 안전 장치는 그 문서를 현실에 고정하는 장치입니다.

## 한눈에 보는 구조

이 흐름은 선형이 아니라 반복 루프입니다. action item이 테스트로 바뀌고, 테스트가 guardrail로 이어지며, chaos 실험이 실제로 잘 막히는지 확인합니다. 그 결과를 다시 학습으로 돌려 다음 action item을 만듭니다.

## 핵심 용어

- **action item**: 사후 분석에서 나온 후속 작업입니다.
- **regression test**: 같은 버그가 다시 생기지 않는지 확인하는 테스트입니다.
- **guardrail**: 위험한 작업을 코드 차원에서 막는 장치입니다.
- **chaos exp**: 의도적으로 실패를 주입하는 실험입니다.
- **learning loop**: incident에서 배운 내용을 다음 예방 작업으로 돌리는 반복 구조입니다.

이 용어를 묶어 보면 재발 방지의 본질이 보입니다. 후속 조치는 할 일 목록이고, 회귀 테스트는 기억 장치이며, guardrail은 실시간 차단 장치입니다. chaos 실험은 그 차단 장치가 실제로 작동하는지 검증하는 단계입니다.

## 전후 비교

이전: 사후 분석 뒤에 문서만 남고 코드와 테스트는 그대로입니다.

이후: 사후 분석 뒤에 테스트, 안전 장치, 운영 규칙이 함께 남습니다.

이후 상태에서 중요한 변화는 재발 방지의 결과물이 문서가 아니라 실행 가능한 산출물이 된다는 점입니다. 나중에 새 팀원이 와도 문서를 읽기 전에 테스트가 먼저 실패하고, guardrail이 먼저 막아 줄 수 있습니다.

## 단계별 실습: 재발 방지 키트 만들기

### 1단계 — 후속 조치 등록하기

먼저 사후 분석에서 나온 후속 조치를 열린 상태로 등록합니다. 추적의 시작점은 무엇을 할지를 명시하는 일입니다.

```python
def register(action):
    return {**action, "status": "open"}
```

### 2단계 — 회귀 테스트 붙이기

수정이 코드 변경으로만 끝나면 시간이 지나면서 맥락이 사라집니다. 회귀 테스트를 같이 두면 같은 문제가 다시 들어왔을 때 바로 잡을 수 있습니다.

```python
def test_regression(scenario, run):
    return run(scenario) == "ok"
```

### 3단계 — guardrail 추가하기

위험한 입력이 들어오면 경고만 띄우지 말고, 아예 막아야 할 때가 있습니다. guardrail은 그런 차단선을 코드로 만든 것입니다.

```python
def guard(payload, limit=1000):
    if payload > limit:
        raise ValueError("blocked")
```

### 4단계 — chaos 실험 설계하기

예방 체계는 실제 실패를 넣어 봐야 믿을 수 있습니다. 어떤 실패를 넣고, 시스템이 어떤 방식으로 버텨야 하는지를 함께 적어 두면 실험이 훨씬 명확해집니다.

```python
def inject(failure):
    return {"injected": failure, "expected": "graceful"}
```

### 5단계 — 학습 루프 닫기

마지막은 action item이 실제로 닫혔는지 보는 단계입니다. 상태가 open인지 done인지 구분하는 것만으로도 방치된 작업을 찾을 수 있습니다.

```python
def closed(action):
    return action["status"] == "done"
```

## 이 코드에서 먼저 볼 점

- action status는 단순해야 추적이 쉽습니다.
- guardrail은 경고가 아니라 차단이어야 할 때가 있습니다.
- chaos 실험에는 항상 기대 결과가 함께 있어야 합니다.

재발 방지에서 가장 큰 착각은 경고 메시지만 남기면 충분하다고 생각하는 것입니다. 정말 위험한 경로라면 시스템이 거부해야 합니다. 로그를 남기는 것과 실패를 막는 것은 전혀 다른 수준의 예방입니다.

## 자주 하는 실수 5가지

1. 후속 조치를 등록만 하고 끝까지 추적하지 않습니다.
2. 회귀 테스트를 만들지 않아 같은 버그가 다시 들어와도 모릅니다.
3. guardrail을 경고 수준으로만 두고 실제 차단은 하지 않습니다.
4. chaos 실험 없이 가설만 세워 둡니다.
5. learning loop가 분기 리뷰까지 이어지지 못합니다.

특히 첫 번째 실수는 모든 예방 체계를 무너뜨립니다. 추적 없는 후속 조치는 해야 할 일을 적어 둔 메모와 다르지 않습니다. 담당자, 기한, 점검 주기가 함께 있어야 진짜 시스템이 됩니다.

## 실무에서는 이렇게 봅니다

실무에서는 사후 분석에서 나온 조치를 Jira에 연결하고, 주요 항목은 회귀 테스트와 chaos 시나리오로 바꿔 CI에 포함시키는 식으로 운영합니다. 그다음 분기 단위 리뷰에서 미완료 항목과 실패한 실험을 다시 봅니다. 예방은 한 번의 작업이 아니라 주기적 운영입니다.

시니어 엔지니어는 예방을 문서가 아니라 코드로 봅니다. 사후 분석은 출발점이고, 실제 예방은 테스트와 안전 장치에 남아야 한다고 생각합니다.

## 예방 항목 우선순위 정하기

incident 뒤에는 할 일이 한꺼번에 많아집니다. 그래서 예방 항목을 모두 같은 급으로 다루기보다, 재발 위험과 구현 비용을 함께 보는 표가 도움이 됩니다.

| 항목 | 재발 위험 감소 | 구현 비용 | 우선순위 |
| --- | --- | --- | --- |
| 회귀 테스트 추가 | 높음 | 낮음 | 즉시 |
| feature flag 추가 | 높음 | 중간 | 높음 |
| 장기 아키텍처 개편 | 높음 | 높음 | 분기 계획 |
| 위키 문서 보강 | 낮음 | 낮음 | 보조 |

문서 보강도 필요하지만, 같은 버그를 직접 막는 테스트와 guardrail이 보통 더 앞에 와야 합니다.

## 장애 주입 예제 (toxiproxy)

chaos 실험을 쉽게 시작하려면 toxiproxy 같은 도구를 쓸 수 있습니다. toxiproxy는 네트워크 계층에서 다양한 장애를 주입할 수 있는 proxy입니다.

```python
import requests
import json


def setup_toxiproxy(proxy_name, listen, upstream):
    """
    toxiproxy를 통해 프록시를 생성합니다.
    """
    toxiproxy_url = "http://localhost:8474"
    payload = {
        "name": proxy_name,
        "listen": listen,
        "upstream": upstream,
        "enabled": True,
    }
    response = requests.post(f"{toxiproxy_url}/proxies", json=payload)
    return response.json()


def inject_latency(proxy_name, latency_ms, jitter_ms=0):
    """
    특정 프록시에 레이턴시를 주입합니다.
    """
    toxiproxy_url = "http://localhost:8474"
    toxic_payload = {
        "type": "latency",
        "attributes": {
            "latency": latency_ms,
            "jitter": jitter_ms,
        },
    }
    response = requests.post(
        f"{toxiproxy_url}/proxies/{proxy_name}/toxics",
        json=toxic_payload,
    )
    return response.json()


def inject_timeout(proxy_name, timeout_ms):
    """
    특정 프록시에 timeout을 주입합니다.
    """
    toxiproxy_url = "http://localhost:8474"
    toxic_payload = {
        "type": "timeout",
        "attributes": {
            "timeout": timeout_ms,
        },
    }
    response = requests.post(
        f"{toxiproxy_url}/proxies/{proxy_name}/toxics",
        json=toxic_payload,
    )
    return response.json()


# 사용 예시
# 1. 결제 API에 대한 proxy 설정
setup_toxiproxy("payment-api", "0.0.0.0:8001", "payment-api.internal:8000")

# 2. 3초 레이턴시 주입
inject_latency("payment-api", latency_ms=3000, jitter_ms=500)
print("결제 API에 3초 레이턴시 주입 완료")

# 3. timeout 후 circuit breaker 동작 확인
# 애플리케이션이 5초 timeout으로 설정되어 있다면
# circuit breaker가 열리고 fallback이 동작해야 함
```

이 코드는 로컬 개발 환경이나 staging에서 돌릴 수 있습니다. 레이턴시를 주입한 뒤 애플리케이션 로그와 메트릭을 확인하면, timeout이 제대로 작동하는지, circuit breaker가 열리는지, alert가 발송되는지 모두 검증할 수 있습니다.

실무에서는 이런 스크립트를 CI의 별도 chaos job으로 등록해 주기적으로 실행하거나, 수동으로 game day를 진행할 때 사용합니다.

## 카오스 엔지니어링

chaos engineering은 의도적으로 실패를 주입해 시스템의 복원력을 검증하는 방법입니다. postmortem에서 나온 예방 장치가 실제로 작동하는지 확인하는 가장 확실한 방법입니다.

chaos 실험의 핵심 요소는 다음과 같습니다.

1. **가설(hypothesis)**: 정상 상태의 기대 동작을 명시합니다.
2. **실패 주입(inject failure)**: 네트워크 지연, CPU 부하, 메모리 부족, 서비스 중단 등을 의도적으로 일으킵니다.
3. **관찰(observe)**: 실패 상황에서 시스템이 어떻게 반응하는지 모니터링합니다.
4. **학습(learn)**: 기대와 다른 동작을 기록하고 개선 항목으로 바꿉니다.

예를 들어 이전 incident에서 결제 API의 timeout이 문제였다면, chaos 실험에서는 일부러 결제 API 응답을 5초 지연시켜 봅니다. 그러면 다음을 확인할 수 있습니다.

- timeout 설정이 정말 적용되었는가?
- circuit breaker가 열렸는가?
- fallback 동작이 정상적으로 발동했는가?
- 모니터링 alert가 예상대로 발송되었는가?

실무에서는 분기에 한 번씩 chaos day를 진행해, 그동안 추가한 예방 장치들을 실제로 검증합니다. 이 실험을 통해 문서로만 남아 있던 방어가 실제로는 작동하지 않는 경우를 발견할 수 있습니다.

## 예방 계층

재발 방지는 한 번의 크 작업이 아니라 여러 계층에 걸쳐 적용하는 예방 체계입니다. 각 계층마다 적합한 활동과 도구가 다르며, 효과도 차이가 납니다.

| 계층 | 예방 활동 | 도구 | 효과 |
| --- | --- | --- | --- |
| 설계 | 장애 허용 아키텍처 | circuit breaker, fallback, bulkhead | 장애 영향 범위 최소화 |
| 코드 | 안전 장치, guardrail | input validation, rate limiter, feature flag | 위험 입력 차단 |
| 배포 | 점진적 배포, 카나리 | canary, blue-green, rollback script | 비정상 배포 조기 탐지 |
| 운영 | 모니터링, chaos 실험 | alert, dashboard, chaos tool | 실패 패턴 학습 |

가장 안전한 예방은 설계 단계에서 시작합니다. circuit breaker가 있으면 하나의 서비스 장애가 전체 시스템으로 파급되는 일을 막을 수 있습니다. 코드 계층의 guardrail은 위험한 입력을 실시간으로 차단하고, 배포 계층의 카나리는 오류가 확산되기 전에 멈출 수 있게 합니다. 운영 계층의 chaos 실험은 이 모든 방어가 실제로 작동하는지 검증합니다.

실무에서는 incident 후속 조치를 이 네 계층으로 분류해 우선순위를 정하는 경우가 많습니다. 설계 개선은 시간이 걸리지만 효과가 크고, 코드 guardrail은 비교적 빠르게 추가할 수 있습니다.

## 체크리스트

- [ ] 사후 분석 후속 조치를 추적하는 도구가 있다.
- [ ] 주요 incident마다 회귀 테스트가 추가된다.
- [ ] 위험 작업을 막는 guardrail 정책이 있다.
- [ ] chaos 실험 일정과 리뷰 주기가 있다.

## 연습 문제

1. guardrail을 한 문장으로 정의해 보세요.
2. 회귀 테스트가 문서보다 강력한 이유를 설명해 보세요.
3. 여러분 팀에서 chaos 실험으로 검증해 볼 실패 시나리오 하나를 적어 보세요.

## 정리와 다음 글

재발 방지는 “다시는 그러지 말자”는 다짐으로 이루어지지 않습니다. 후속 조치 추적, 회귀 테스트, guardrail, chaos 실험처럼 실행 가능한 장치로 학습을 남겨야 합니다. 사후 분석이 원인과 교훈을 정리한다면, 예방은 그 교훈을 시스템에 새기는 단계입니다.

다음 글에서는 시리즈의 마무리로, 지금까지 배운 severity, 대응, communication, postmortem, prevention을 하나의 incident runbook으로 묶는 방법을 다루겠습니다.


## 예방 심화: MTTA/MTTR 계산과 개선 추적 표

재발 방지는 구호가 아니라 측정 가능한 개선 활동입니다. 특히 incident 대응 체계에서는 시간 기반 지표가 유용합니다. 탐지-인식-완화-복구 구간을 분리해 보면 어디서 병목이 생기는지 명확해집니다.

### 핵심 메트릭 정의

- MTTA(Mean Time To Acknowledge): 탐지 후 담당자가 인지하기까지 평균 시간
- MTTM(Mean Time To Mitigate): 탐지 후 고객 영향 완화까지 평균 시간
- MTTR(Mean Time To Resolve): 탐지 후 완전 복구까지 평균 시간

세 지표를 함께 봐야 합니다. MTTR만 개선해도 MTTA가 길면 고객 체감은 나빠질 수 있습니다.

## 계산 코드 예시

```python
from datetime import datetime


def minutes(a: str, b: str) -> float:
    t1 = datetime.fromisoformat(a)
    t2 = datetime.fromisoformat(b)
    return (t2 - t1).total_seconds() / 60.0


def metrics(incident: dict) -> dict:
    detected = incident["detected"]
    acked = incident["acknowledged"]
    mitigated = incident["mitigated"]
    resolved = incident["resolved"]
    return {
        "mtta": minutes(detected, acked),
        "mttm": minutes(detected, mitigated),
        "mttr": minutes(detected, resolved),
    }
```

코드는 단순하지만 입력 품질이 핵심입니다. timeline anchor가 부정확하면 지표가 왜곡됩니다.

### 개선 추적 표 예시

| 분기 | MTTA(분) | MTTM(분) | MTTR(분) | 주요 개선 | 결과 |
| --- | --- | --- | --- | --- | --- |
| Q1 | 8.2 | 22.5 | 74.1 | on-call 라우팅 정비 | 인지 지연 감소 |
| Q2 | 5.6 | 17.3 | 61.8 | rollback 자동화 | 완화 시간 단축 |
| Q3 | 4.9 | 14.2 | 55.4 | comms 템플릿 표준화 | 조율 비용 감소 |

이 표의 목적은 숫자 자체가 아니라 "어떤 변경이 어떤 지표를 움직였는가"를 연결하는 데 있습니다.

## 예방 항목 우선순위 프레임

1. 재발 확률이 높고 영향이 큰 항목부터 처리합니다.
2. 회귀 테스트로 즉시 막을 수 있는 항목을 우선합니다.
3. 장기 구조 개선은 분기 계획으로 분리합니다.
4. 문서 개선은 코드/가드레일 개선을 보조하도록 배치합니다.

우선순위를 명시하지 않으면 모든 항목이 중요한 것처럼 보이고 결국 아무것도 끝나지 않습니다.

## 운영 점검 질문

- 주요 incident마다 메트릭이 계산되는가?
- 개선 항목과 지표 변동이 연결되는가?
- 미완료 항목이 다음 분기로 자동 이월되는가?
- chaos 실험 결과가 예방 backlog에 반영되는가?

이 질문에 yes를 늘려 가는 과정이 곧 대응 성숙도 향상입니다.

## 개선 추적 운영 루틴

예방 항목의 실행률을 높이려면 주간 루틴이 필요합니다. 매주 30분 고정 슬롯에서 open action item, 실패한 회귀 테스트, 미완료 guardrail 작업을 함께 검토하면 누락이 줄어듭니다. 중요한 점은 진행률 보고보다 "막힌 이유"를 빠르게 제거하는 데 있습니다.

또한 분기 말에는 메트릭 변화와 투자 대비 효과를 함께 검토해야 합니다. MTTR이 줄었더라도 특정 서비스에서만 개선됐다면 다음 분기에는 편차가 큰 영역에 집중하는 방식으로 계획을 조정할 수 있습니다.

## 운영 보강 메모

현장에서는 문서 규칙만으로 품질이 자동으로 올라가지 않습니다. 그래서 각 팀은 월 1회 이상 실제 incident 사례를 골라 기준 적용 여부를 점검해야 합니다. 점검 항목은 단순할수록 좋습니다. 선언 근거가 수치로 남았는지, 역할 분리가 지켜졌는지, 커뮤니케이션 주기가 유지됐는지, 후속 조치가 티켓으로 연결됐는지 네 가지를 반복 확인하면 됩니다.

이 보강 메모를 남기는 목적은 분량을 늘리는 데 있지 않습니다. 기준을 사건 데이터와 연결해 "다음 대응의 입력"으로 쓰는 데 있습니다. 문서가 저장소 안에서 살아 있으려면 변경 이력, 검증 절차, 교육 루프가 함께 있어야 합니다. 결국 incident 대응 역량은 한 번의 완벽한 대응이 아니라, 같은 실수를 덜 반복하는 조직 습관에서 만들어집니다.

## 운영 리허설 권장안

문서 개정 후에는 반드시 짧은 리허설을 수행해야 합니다. 20분짜리 tabletop만으로도 기준 누락을 빠르게 발견할 수 있습니다. 진행 순서는 간단합니다. 가상 알림을 열고, 역할을 배정하고, 첫 공지를 작성하고, 종료 조건을 선언해 봅니다. 그 과정에서 헷갈리는 문장이나 끊긴 링크가 나오면 즉시 수정 항목으로 기록합니다.

리허설의 목적은 사람 평가가 아니라 문서 검증입니다. 실제 incident는 긴장 상태에서 진행되므로, 평시에는 분명해 보이던 절차도 현장에서는 모호해질 수 있습니다. 정기 리허설을 운영 루틴에 넣으면 문서와 실행 사이의 간극을 줄일 수 있습니다.

## 예방 백로그 운영 템플릿

재발 방지는 우선순위 관리가 핵심입니다. incident 뒤에는 개선 항목이 한꺼번에 늘어나므로, 예방 백로그를 별도로 운영해야 합니다.

| 항목 | 유형 | 위험 감소 | 구현 비용 | 우선순위 | 상태 |
| --- | --- | --- | --- | --- | --- |
| checkout 회귀 테스트 | 테스트 | 높음 | 낮음 | 즉시 | 진행중 |
| 배포 가드레일 추가 | 운영 규칙 | 높음 | 중간 | 높음 | 예정 |
| 카오스 실험 자동화 | 검증 | 중간 | 중간 | 중간 | 예정 |

이 표를 분기 리뷰에 포함하면 문서 기반 개선이 실제 실행으로 이어집니다. 예방은 한 번의 프로젝트가 아니라 운영 루틴입니다.

## 온콜 교대 설정 예시

```yaml
oncall_rotation:
  timezone: Asia/Seoul
  handoff_minutes: 10
  schedule:
    - name: primary
      weekday: mon-fri
      from: "09:00"
      to: "18:00"
    - name: secondary
      weekday: mon-fri
      from: "18:00"
      to: "09:00"
  handoff_template:
    - current_impact
    - mitigation_status
    - open_risks
    - next_30m_plan
```

교대 설정은 incident가 없을 때 준비해야 incident가 있을 때 쓸 수 있습니다. 특히 인계 템플릿을 고정해 두면 팀 숙련도 차이로 인한 품질 편차를 줄일 수 있습니다.

## 운영 부록: 예방 항목 상태 정의

- `open`: 항목 생성, 아직 착수 전
- `in_progress`: 구현 또는 검증 진행 중
- `blocked`: 외부 의존성으로 지연
- `done`: 검증 완료

상태 정의를 단순하게 두면 분기 리뷰에서 누락 항목을 빠르게 찾을 수 있습니다.

## 운영 메모: 점검 루프

운영 문서는 작성으로 끝나지 않습니다. 월간 점검 루프를 통해 선언 기준, 역할 분리, 공지 주기, 후속 조치 추적이 실제 incident에서 유지되는지 확인해야 합니다. 점검 결과는 다음 리허설 시나리오와 runbook 개정 항목으로 바로 연결하는 편이 좋습니다.

## 처음 질문으로 돌아가기

- **사후 분석 뒤에 왜 같은 incident가 다시 반복될까요?**
  - 본문의 기준은 재발 방지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
  - Postmortem에서 나온 '재발 방지' 항목을 코드, 모니터링, 문서로 구체화합니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
  - 작은 변경(모니터링 추가, 에러 메시지 개선)도 다음 대응 시간을 크게 단축합니다.
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.
  - 완료 기준을 명확히 하고, 다음 postmortem 전에 확인합니다.
<!-- toc:begin -->
## 시리즈 목차

- [Incident Response 101 (1/10): Incident란 무엇인가?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity 분류](./02-severity.md)
- [Incident Response 101 (3/10): 초기 대응](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Timeline 작성](./05-timeline.md)
- [Incident Response 101 (6/10): Root Cause Analysis](./06-root-cause-analysis.md)
- [Incident Response 101 (7/10): Mitigation과 Resolution](./07-mitigation-and-resolution.md)
- [Incident Response 101 (8/10): Postmortem](./08-postmortem.md)
- **재발 방지 (현재 글)**
- Incident Runbook 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Postmortem Action Items - Google SRE Workbook](https://sre.google/workbook/postmortem-culture/)
- [Preventing recurrence - PagerDuty](https://response.pagerduty.com/after/preventing/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [Guardrails, not gates - Thoughtworks](https://www.thoughtworks.com/insights/blog/guardrails-not-gates)

### 예제 소스
- [incident-response-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/incident-response-101/ko)
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Prevention, Reliability, Testing, Operations
