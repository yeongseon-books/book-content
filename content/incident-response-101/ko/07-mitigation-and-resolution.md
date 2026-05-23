---
series: incident-response-101
episode: 7
title: "Incident Response 101 (7/10): Mitigation과 Resolution"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Incident
  - Mitigation
  - Resolution
  - Rollback
  - Operations
seo_description: mitigation과 resolution의 차이, 롤백과 킬 스위치, 복구 검증 지표를 incident 운영 관점에서 정리합니다.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (7/10): Mitigation과 Resolution

이 글은 Incident Response 101 시리즈의 일곱 번째 글입니다.

incident 대응에서 자주 생기는 혼동 하나는 피해를 멈춘 상태와 원인을 제거한 상태를 같은 것으로 보는 일입니다. 고객 영향이 줄어들면 마음이 급히 놓이고, 그 순간 incident가 끝났다고 느끼기 쉽습니다.

하지만 많은 사고는 바로 그 지점에서 다시 터집니다. 잠깐 진정된 것과 실제로 해결된 것은 다르기 때문입니다.

이 글은 Incident Response 101 시리즈의 7번째 글입니다. 여기서는 mitigation과 resolution의 차이, 롤백·스케일 아웃·스로틀·킬 스위치의 사용 순서, 그리고 복구 검증 기준을 정리합니다.


![Incident Response 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/07/07-01-diagram-at-a-glance.ko.png)
*Incident Response 101 7장 흐름 개요*
> Mitigation과 Resolution을 구분하면 대응 속도가 빨라집니다. 먼저 고객을 정상 상태로, 그 다음 근본 원인을 수정합니다.

## 먼저 던지는 질문

- 불을 끄는 일과 원인을 없애는 일은 어떻게 다를까요?
- 롤백은 왜 가장 강력한 mitigation 수단일까요?
- 스케일 아웃, 스로틀, 킬 스위치는 언제 써야 할까요?

## 왜 이 주제가 중요한가

mitigation과 resolution을 혼동하면 같은 incident가 밤에 다시 열릴 수 있습니다. 예를 들어 feature flag를 꺼서 증상을 잠시 멈췄는데, 이를 해결 완료로 간주하고 후속 수정 없이 닫아 버리면 조건이 그대로 남아 있기 때문입니다. 반대로 원인을 완전히 제거할 때까지 공지를 미루면 고객은 이미 안정화된 사실조차 늦게 알게 됩니다.

좋은 대응은 두 단계를 분리합니다. 먼저 피해를 줄이고, 그다음 차분하게 원인을 없앱니다. 이 구분이 있어야 복구 일정과 커뮤니케이션도 정직해집니다.

## 한눈에 보는 구조

incident 대응은 보통 이 순서를 따릅니다. 먼저 서비스를 안정화하고, 그 뒤에 근본 조치를 적용합니다. 두 단계를 섞으면 판단과 공지가 함께 흔들립니다.

## 핵심 용어

- **mitigation**: 피해 확산을 멈추는 조치입니다.
- **resolution**: 원인을 제거하는 조치입니다.
- **rollback**: 이전 버전으로 되돌리는 조치입니다.
- **kill switch**: 기능을 즉시 끄는 안전 장치입니다.
- **throttle**: 유입 트래픽을 제한하는 조치입니다.

이 용어를 분리해 두면 공지가 더 정확해집니다. “완화됨”은 고객 영향이 줄었다는 뜻이지, 원인이 사라졌다는 뜻이 아닙니다. “해결됨”은 그보다 더 강한 표현이어야 합니다.

## 전후 비교

이전: 완전히 고친 뒤에만 공지합니다.

이후: 피해를 막는 즉시 완화 사실을 알리고, 원인 제거는 별도로 공지합니다.

이 차이는 신뢰에 직접 연결됩니다. 고객은 현재 영향이 줄었는지 알고 싶어 하고, 팀은 아직 임시 조치 상태인지 완전 해결 상태인지 구분해서 운영해야 합니다.

## 단계별 실습: 작은 mitigation 키트 만들기

### 1단계 — 롤백 준비하기

가장 빠른 완화 수단은 대개 이전 정상 상태로 돌아가는 것입니다. 그래서 롤백 절차는 incident 전에 준비돼 있어야 합니다.

```python
def rollback(version):
    return {"action": "rollback", "to": version}
```

### 2단계 — 스케일 아웃하기

용량 부족형 incident라면 인스턴스를 늘리는 것만으로도 피해를 빠르게 줄일 수 있습니다.

```python
def scale_out(service, replicas):
    return {"service": service, "replicas": replicas}
```

### 3단계 — 스로틀 걸기

과도한 요청이 문제라면 유입량 제한이 현실적인 완화 수단이 됩니다.

```python
def throttle(endpoint, rps):
    return {"endpoint": endpoint, "rps": rps}
```

### 4단계 — 킬 스위치 실행하기

문제 기능을 빠르게 끌 수 있다면 incident 폭을 크게 줄일 수 있습니다. 킬 스위치는 복잡하면 소용이 없습니다.

```python
FLAGS = {}

def kill(feature):
    FLAGS[feature] = False
    return FLAGS[feature]
```

### 5단계 — 복구 검증하기

“괜찮아 보인다”로는 부족합니다. 완화나 해결 뒤에는 수치로 복구를 확인해야 합니다.

```python
def verify(metrics):
    return metrics.get("err_ratio", 1) < 0.01
```

## 이 코드에서 먼저 볼 점

- mitigation은 큰 개편보다 작은 조치로 빨리 실행해야 합니다.
- 킬 스위치는 플래그 한 줄로 바로 꺼질 정도로 단순해야 합니다.
- 복구 검증은 느낌이 아니라 수치로 확인해야 합니다.

incident 현장에서는 “일단 살리고 나중에 바로잡는다”는 순서가 매우 중요합니다. 완전한 해결을 기다리다 보면 고객 영향이 불필요하게 길어질 수 있습니다.

## 자주 하는 실수 5가지

1. 롤백 수단 없이 전진만 시도합니다.
2. 킬 스위치를 미리 준비하지 않습니다.
3. mitigation을 곧바로 resolution이라고 발표합니다.
4. 검증 없이 incident를 닫습니다.
5. 스로틀을 해제해야 한다는 사실을 잊습니다.

특히 세 번째 실수는 커뮤니케이션 신뢰를 해칩니다. 고객 영향이 줄어든 것과 원인이 제거된 것은 다르기 때문에, 공지 문장도 그 차이를 솔직하게 반영해야 합니다.

## 실무에서는 이렇게 봅니다

실무에서는 feature flag 시스템과 autoscaler를 runbook 명령어 한 줄로 묶어 2분 안에 mitigation할 수 있게 준비하는 경우가 많습니다. 핵심은 incident 현장에서 새로 설계하지 않아도 되게 만드는 것입니다.

시니어 엔지니어는 mitigation을 최우선으로 두되, resolution은 더 차분한 검증과 함께 가져갑니다. 그리고 unthrottle 같은 후속 이벤트도 별도 사건처럼 기록합니다. 완화 이후의 상태 전환도 운영에서는 중요하기 때문입니다.

## mitigation 선택 순서 예시

mitigation은 “무엇이 가장 멋진 해결인가”보다 “무엇이 가장 빨리 피해를 줄이는가”로 고르는 편이 좋습니다. 실무에서는 보통 아래 순서로 후보를 훑습니다.

1. 바로 가능한 롤백이 있는가?
2. feature flag 또는 kill switch로 문제 기능만 끌 수 있는가?
3. 용량 부족형이면 scale out이 바로 가능한가?
4. 트래픽 급증형이면 throttle로 핵심 경로를 보호할 수 있는가?
5. 각 조치 뒤에 어떤 수치로 복구를 확인할 것인가?

완전한 해결은 나중 단계입니다. 초반에는 가장 빠르게 고객 영향을 줄이는 조치를 먼저 고르는 편이 안전합니다.

## 완화 전략 비교

mitigation 수단은 여러 가지가 있지만, 각각 실행 속도와 리스크가 다릅니다. incident 현장에서 빠른 판단을 내리려면 각 전략의 특징을 미리 알고 있어야 합니다.

| 전략 | 실행 속도 | 리스크 | 적합 상황 |
| --- | --- | --- | --- |
| 롤백 | 1–5분 | 낮음 | 배포 기인, 이전 버전 안정 |
| 페일오버 | 1–10분 | 중간 | 인스턴스/노드 장애 |
| 트래픽 차단 | 30초–2분 | 높음 | DDoS, 불량 트래픽, 입력 폭증 |
| 기능 비활성화 | 30초–1분 | 낮음 | 특정 기능 버그, A/B 테스트 중단 |

롤백은 가장 빠르고 안전하지만, 롤백 절차가 준비돼 있어야 합니다. 트래픽 차단은 빠르지만 정상 사용자까지 영향을 받을 수 있어 신중해야 합니다. 실무에서는 보통 기능 비활성화나 롤백을 먼저 고려하고, 그것이 불가능할 때 페일오버나 트래픽 차단으로 이동합니다.

## 체크리스트

- [ ] 롤백 절차가 문서화되어 있다.
- [ ] 킬 스위치 목록이 정리되어 있다.
- [ ] 스로틀 정책이 준비되어 있다.
- [ ] 복구 검증 지표가 정의되어 있다.

## 연습 문제

1. mitigation을 한 문장으로 정의해 보세요.
2. resolution을 한 문장으로 정의해 보세요.
3. 킬 스위치가 왜 incident 대응에서 강력한 수단인지 설명해 보세요.

## 카나리 롤백 예제

롤백은 가장 강력한 mitigation 수단이지만, 한 번에 전체를 되돌리면 새 배포에 포함된 정상 기능까지 다시 가려지게 됩니다. 실무에서는 일부 트래픽만 먼저 되돌려 보는 카나리 롤백(canary rollback) 패턴을 자주 씁니다.

```python
def canary_rollback(service, old_version, canary_ratio=0.1):
    """
    일부 트래픽만 먼저 이전 버전으로 되돌립니다.
    """
    return {
        "service": service,
        "old_version": old_version,
        "canary_ratio": canary_ratio,
        "status": "rollback_started",
        "watch_metrics": ["error_rate", "latency_p99"],
    }


def expand_rollback(service, canary_ratio, target_ratio):
    """
    카나리 비율을 점진적으로 높입니다.
    """
    if canary_ratio >= target_ratio:
        return {"status": "complete", "ratio": canary_ratio}
    
    new_ratio = min(canary_ratio + 0.1, target_ratio)
    return {
        "service": service,
        "new_ratio": new_ratio,
        "status": "expanding",
    }


# 사용 예시
initial = canary_rollback("payment-api", "v2.4.1", canary_ratio=0.1)
print(f"10% 트래픽을 {initial['old_version']}으로 되돌림")

# 모니터링 확인 후 확대
step1 = expand_rollback("payment-api", 0.1, 0.5)
print(f"오류율 정상, 50%로 확대: {step1['new_ratio']}")

step2 = expand_rollback("payment-api", 0.5, 1.0)
print(f"최종 100% 롤백 완료: {step2['status']}")
```

이 패턴의 장점은 롤백이 새 문제를 일으키는 경우 즉시 멈출 수 있다는 점입니다. 10% 단계에서 예상과 다른 지표가 나오면, 나머지 90%를 대상으로 하는 forward fix를 먼저 시도할 수 있습니다.

실무에서는 이 단계별 비율을 Argo Rollouts, Flagger, 또는 자체 배포 도구에 통합해 메트릭 기반 자동 확대로 연결하기도 합니다.

## 임시 조치 vs 영구 수정

mitigation과 resolution의 구분은 변경의 지속 시간으로도 표현할 수 있습니다. 임시 조치는 incident 대응 중에 바로 적용하지만 나중에 되돌려야 하는 변경이고, 영구 수정은 그대로 유지해도 되는 변경입니다.

예를 들어:

- 임시 조치: 전체 API rate limit을 절반으로 낮춤 (→ 나중에 원래대로 복구)
- 영구 수정: timeout 기본값을 3초에서 5초로 변경 (→ 그대로 유지)
- 임시 조치: 특정 리전으로의 트래픽 우회 (→ 나중에 다시 분산)
- 영구 수정: 장애 발생 코드 삭제 (→ 그대로 유지)

임시 조치를 펼 때는 반드시 "되돌리기" 일정을 함께 기록해야 합니다. 그렇지 않으면 임시 조치가 영구히 남아 시스템이 의도하지 않은 상태로 굳어질 수 있습니다. 실무에서는 mitigation 문서에 "rollback plan" 섹션을 함께 남기는 경우가 많습니다.

좋은 예:

- mitigation: rate limit 50 → 25 RPS, rollback: 24시간 후 단계별 복구, owner: @platform
- resolution: timeout 기본값 3s → 5s, 테스트 통과 후 배포, rollback plan: N/A

## 정리와 다음 글

mitigation은 피해를 멈추는 일이고, resolution은 원인을 제거하는 일입니다. 둘을 구분해야 incident 현장에서 빠른 완화와 정직한 커뮤니케이션, 그리고 안전한 후속 수정이 가능합니다. 롤백, 스케일 아웃, 스로틀, 킬 스위치 같은 수단은 먼저 서비스를 살리는 데 쓰고, 해결 완료 여부는 숫자로 검증해야 합니다.

다음 글에서는 incident가 끝난 뒤 학습을 조직 자산으로 바꾸는 postmortem을 다루겠습니다.


## 대응 심화: 런북형 구조와 자동화 스크립트 예시

mitigation과 resolution을 분리하면 incident 중 의사결정 속도가 높아집니다. "지금 피해를 줄이는 행동"과 "나중에 원인을 제거하는 행동"을 같은 큐에 두면 우선순위가 꼬입니다. 따라서 실행 순서를 명시한 런북 구조가 필요합니다.

### 런북 기본 구조

| 단계 | 목적 | 대표 액션 | 종료 기준 |
| --- | --- | --- | --- |
| Detect | 이상 징후 확인 | alert 검증, 영향 추정 | incident 선언 여부 결정 |
| Mitigate | 고객 피해 축소 | rollback, kill switch, throttle | 오류율/실패율 하락 |
| Stabilize | 상태 유지 | scale 조정, 캐시/큐 점검 | 지표 안정 유지 |
| Resolve | 근본 수정 적용 | 코드 수정, 설정 교정 | 재현 테스트 통과 |
| Verify | 회복 검증 | SLI 회복 확인, 공지 | 종료 승인 |

이 구조를 팀 공통 언어로 쓰면 incident 채널에서 "현재 단계"만 공유해도 실행 컨텍스트가 맞춰집니다.

### 자동화 스크립트 예시

```python
def mitigation_plan(can_rollback: bool, has_flag: bool, traffic_spike: bool) -> list[str]:
    actions = []
    if can_rollback:
        actions.append("rollback")
    if has_flag:
        actions.append("disable_feature_flag")
    if traffic_spike:
        actions.append("apply_throttle")
    if not actions:
        actions.append("scale_out")
    return actions


def resolution_ready(test_pass: bool, config_reviewed: bool, peer_approved: bool) -> bool:
    return test_pass and config_reviewed and peer_approved
```

이 스크립트는 복잡한 자동화가 아니라 "판단 조건의 명시"에 의미가 있습니다. 조건을 코드화하면 야간 대응에서도 동일한 기준을 유지할 수 있습니다.

### 단계 전환 기준

- Mitigate -> Stabilize: 오류율이 임계값 아래로 하락하고 10분 이상 유지
- Stabilize -> Resolve: 추가 확산 징후 없음, 원인 후보 수렴
- Resolve -> Verify: 수정 반영 후 회귀 테스트 통과
- Verify -> Close: 외부 공지 완료, postmortem 링크 생성

단계 전환 기준을 문서화하면 "분위기상 종료" 같은 위험한 결정을 줄일 수 있습니다.

## 운영 팁

- rollback 가능 상태를 항상 유지합니다.
- kill switch는 클릭 1~2회 이내로 실행 가능해야 합니다.
- throttle 해제 조건을 incident 중에 함께 정의합니다.
- mitigation 성공 후에도 resolution task를 별도 트래킹합니다.

이 네 가지를 지키면 임시 안정화 후 재폭발하는 패턴을 크게 줄일 수 있습니다.

## 검증용 체크 스니펫

```yaml
recovery_gates:
  error_ratio_below: 0.01
  p95_latency_below_ms: 800
  sustained_minutes: 15
  customer_updates_sent: true
  postmortem_ticket_created: true
```

복구 선언은 감각보다 gate 통과 여부로 판단해야 합니다. gate가 있어야 교대 인계에서도 판단 일관성이 유지됩니다.

## 완화 후 재확산 방지 점검

mitigation 직후에는 "지표 반등"을 확인하는 짧은 관찰 구간이 필요합니다. 5분 단위로 오류율, 지연, 큐 적체를 확인하고 재확산 징후가 보이면 즉시 이전 단계로 되돌아가야 합니다. 많은 팀이 이 구간을 생략해 incident를 조기 종료하는 실수를 반복합니다.

또한 완화 조치가 고객 경험에 만든 부작용도 함께 점검해야 합니다. 예를 들어 throttle은 핵심 경로를 보호하지만 일부 요청을 의도적으로 지연시킬 수 있으므로, 해제 조건과 공지 문구를 사전에 준비해야 합니다.

## 운영 보강 메모

현장에서는 문서 규칙만으로 품질이 자동으로 올라가지 않습니다. 그래서 각 팀은 월 1회 이상 실제 incident 사례를 골라 기준 적용 여부를 점검해야 합니다. 점검 항목은 단순할수록 좋습니다. 선언 근거가 수치로 남았는지, 역할 분리가 지켜졌는지, 커뮤니케이션 주기가 유지됐는지, 후속 조치가 티켓으로 연결됐는지 네 가지를 반복 확인하면 됩니다.

이 보강 메모를 남기는 목적은 분량을 늘리는 데 있지 않습니다. 기준을 사건 데이터와 연결해 "다음 대응의 입력"으로 쓰는 데 있습니다. 문서가 저장소 안에서 살아 있으려면 변경 이력, 검증 절차, 교육 루프가 함께 있어야 합니다. 결국 incident 대응 역량은 한 번의 완벽한 대응이 아니라, 같은 실수를 덜 반복하는 조직 습관에서 만들어집니다.

## 운영 리허설 권장안

문서 개정 후에는 반드시 짧은 리허설을 수행해야 합니다. 20분짜리 tabletop만으로도 기준 누락을 빠르게 발견할 수 있습니다. 진행 순서는 간단합니다. 가상 알림을 열고, 역할을 배정하고, 첫 공지를 작성하고, 종료 조건을 선언해 봅니다. 그 과정에서 헷갈리는 문장이나 끊긴 링크가 나오면 즉시 수정 항목으로 기록합니다.

리허설의 목적은 사람 평가가 아니라 문서 검증입니다. 실제 incident는 긴장 상태에서 진행되므로, 평시에는 분명해 보이던 절차도 현장에서는 모호해질 수 있습니다. 정기 리허설을 운영 루틴에 넣으면 문서와 실행 사이의 간극을 줄일 수 있습니다.

## 완화-해결 전환 체크포인트

완화와 해결을 구분하려면 단계 전환 기준을 숫자로 고정해야 합니다. 아래 표는 incident 현장에서 자주 쓰는 전환 기준 예시입니다.

| 전환 | 필수 조건 | 확인 지표 |
| --- | --- | --- |
| Mitigate -> Stabilize | 오류율 하락 후 10분 유지 | error_ratio, p95 |
| Stabilize -> Resolve | 원인 후보 수렴, 추가 확산 없음 | timeline, alert noise |
| Resolve -> Verify | 영구 수정 반영, 회귀 테스트 통과 | test report |
| Verify -> Close | 고객 공지 완료, postmortem 링크 생성 | comms log |

단계 전환 기준이 있으면 "분위기상 종료"를 막을 수 있습니다. 특히 완화 직후에는 재확산 가능성이 높으므로 관찰 구간을 반드시 둬야 합니다.

## on-call 실행 명령 템플릿

```text
[mitigation-command-sheet]
- rollback_command:
- feature_flag_off_command:
- scale_out_command:
- throttle_command:
- verify_query:
- rollback_of_mitigation_plan:
```

incident 중에는 명령 위치를 찾는 시간도 비용입니다. 서비스별로 이 명령 시트를 준비해 두면 초기 10분 대응 품질이 크게 좋아집니다.

## 운영 부록: 완화 명령 실행 순서 카드

```text
[mitigation-order]
1) rollback 가능 여부 확인
2) feature flag off 실행
3) scale out 또는 throttle 적용
4) 5분 관찰 지표 확인
5) 고객 공지 업데이트
6) 재확산 시 이전 단계로 즉시 복귀
```

## 운영 부록: 완화 이후 관찰 표

| 구간 | 확인 지표 | 기준 |
| --- | --- | --- |
| 0~5분 | error ratio | 하락 추세 확인 |
| 5~10분 | p95 latency | 임계값 이하 유지 |
| 10~15분 | 신규 critical alert | 0건 |
| 15분 이후 | 고객 신고 | 증가 없음 |

관찰 표가 있으면 완화 직후 조기 종료를 줄일 수 있습니다.

## 완화-해결 운영 추가 점검 항목

아래 항목은 실무에서 바로 점검할 수 있는 추가 체크포인트입니다.

- 체크포인트 1: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 2: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 3: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.

```text
[quick-audit]
- declaration_latency_minutes:
- first_update_latency_minutes:
- mitigation_started_minutes:
- recovery_verification_metrics:
- postmortem_linked: true/false
```


## 운영 메모: 점검 루프

운영 문서는 작성으로 끝나지 않습니다. 월간 점검 루프를 통해 선언 기준, 역할 분리, 공지 주기, 후속 조치 추적이 실제 incident에서 유지되는지 확인해야 합니다. 점검 결과는 다음 리허설 시나리오와 runbook 개정 항목으로 바로 연결하는 편이 좋습니다.

## 처음 질문으로 돌아가기

- **불을 끄는 일과 원인을 없애는 일은 어떻게 다를까요?**
  - 본문에서 강조했듯이 mitigation은 "지금 사용자 피해를 멈춘다"는 단기 목표, resolution은 "같은 원인이 다시 일어나지 않게 한다"는 영구 목표입니다. 두 작업을 같은 자리에서 동시에 끝내려 하면 mitigation이 늦어져 피해가 커지므로, 먼저 잠시라도 피를 멎게 하고 그 다음에 정확한 치료에 시간을 쓰는 순서가 원칙입니다.
- **롤백은 왜 가장 강력한 mitigation 수단일까요?**
  - 본문에서 본 것처럼 대부분의 incident는 직전 변경(배포·설정·기능 플래그)으로 시작되고, 롤백은 그 변경을 통째로 되돌려 "최소한 어제는 잘 됐다"는 알려진 안전 상태로 즉시 복귀하는 가장 단순한 액션이기 때문입니다. 진단을 마치기 전에도 쓸 수 있다는 점에서, "원인을 다 이해할 때까지 기다리지 않아도 되는" 거의 유일한 1차 대응 수단입니다.
- **스케일 아웃, 스로틀, 킬 스위치는 언제 써야 할까요?**
  - 본문 사용처처럼 스케일 아웃은 트래픽이 한계 용량을 초과해 정상 코드가 단지 자원이 부족해 실패할 때, 스로틀은 일부 사용자/엔드포인트의 과도한 호출이 다른 사용자까지 무너뜨릴 때, 킬 스위치는 특정 기능 자체가 사고의 원인이라 그 기능만 즉시 꺼야 할 때 씁니다. 셋 다 mitigation 도구이지 resolution은 아니므로, 적용 후에는 반드시 원인 제거 작업이 별도로 따라붙어야 합니다.
  - 먼저 고객을 정상 상태로 돌리는 게 우선입니다.
<!-- toc:begin -->
## 시리즈 목차

- [Incident Response 101 (1/10): Incident란 무엇인가?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity 분류](./02-severity.md)
- [Incident Response 101 (3/10): 초기 대응](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Timeline 작성](./05-timeline.md)
- [Incident Response 101 (6/10): Root Cause Analysis](./06-root-cause-analysis.md)
- **Mitigation과 Resolution (현재 글)**
- Postmortem (예정)
- 재발 방지 (예정)
- Incident Runbook 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [incident-response-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/incident-response-101/ko)

### 공식 문서
- [Mitigation during incidents - PagerDuty](https://response.pagerduty.com/during/mitigation/)
- [Release Engineering - Google SRE Book](https://sre.google/sre-book/release-engineering/)
- [Feature Toggles - Martin Fowler](https://martinfowler.com/articles/feature-toggles.html)
- [Incident management guide - Atlassian](https://www.atlassian.com/incident-management)

Tags: Incident, Mitigation, Resolution, Rollback, Operations
