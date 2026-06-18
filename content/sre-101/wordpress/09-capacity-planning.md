---
title: "바이브코딩을 위한 SRE 기초 (9/10): 용량 계획"
series: sre-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SRE
  - CapacityPlanning
  - LoadTest
  - Operations
---

# 바이브코딩을 위한 SRE 기초 (9/10): 용량 계획

이 글은 "바이브코딩을 위한 SRE 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 서버 설정과 인프라 코드를 빠르게 만들어 줍니다. 그런데 지금 서버가 얼마나 버틸 수 있는지, 3개월 후 트래픽이 두 배가 되면 몇 대가 더 필요한지 계산하는 것은 AI가 코드를 만들어 주는 일과 별개입니다. 인프라가 준비되지 않은 상태에서 트래픽 급증이 오면 장애가 납니다.

용량 계획 없이 운영하는 팀이 빠지는 패턴이 있습니다. 장애가 나고 나서야 서버를 늘리고, 늘린 서버가 얼마나 버티는지 모르고, 다음 급증에 또 장애를 겪습니다. 이 패턴을 끊으려면 현재 시스템이 어느 수준의 부하를 감당할 수 있는지 측정하고, 성장 예측에 맞게 미리 준비하는 절차가 필요합니다.

부하 테스트는 용량 계획의 핵심 도구입니다. 실제 트래픽 패턴을 재현해 한계를 확인하고, 병목이 어디인지 찾습니다. AI가 만든 부하 테스트 스크립트도 마찬가지입니다. 어떤 시나리오를 재현하는지, 결과 해석 기준이 무엇인지 확인해야 합니다.

> **핵심 인사이트:** 용량 계획은 "충분히 큰 서버를 미리 사두는 것"이 아닙니다. 현재 한계를 측정하고, 성장 속도를 예측하고, 적정 여유분(headroom)을 계산해 적시에 확장하는 것입니다. 부하 테스트로 병목을 찾지 않으면, 자원을 아무리 늘려도 같은 지점에서 한계가 옵니다.

## 이 글에서 다룰 문제

- 용량 계획은 어떤 순서로 수행할까요?
- 트래픽 성장 예측은 어떻게 계산할까요?
- 적정 여유분(headroom)은 어떻게 결정할까요?
- 부하 테스트 결과를 어떻게 해석할까요?
- AI가 만든 인프라 코드에서 용량 계획 관점으로 확인할 것은 무엇인가요?

## 용량 계획 핵심 패턴

```python
import statistics

# 트래픽 성장 예측: 선형 추세 기반
def linear_forecast(history, weeks_ahead):
    """
    history: [(week_num, rps), ...] 과거 트래픽 데이터
    weeks_ahead: 예측할 미래 주 수
    """
    n = len(history)
    xs = [h[0] for h in history]
    ys = [h[1] for h in history]
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / \
            sum((x - x_mean) ** 2 for x in xs)
    intercept = y_mean - slope * x_mean
    future_week = xs[-1] + weeks_ahead
    return slope * future_week + intercept

# 여유분 계산: 현재 대비 필요 증설 비율
def headroom(target_util, current_util):
    """
    target_util: 목표 최대 사용률 (예: 0.7 = 70%)
    current_util: 현재 사용률 (예: 0.55 = 55%)
    """
    return (current_util / target_util) - 1.0  # 양수면 증설 필요

# 필요 노드 수 계산
def nodes(predicted_rps, rps_per_node, safety_margin=1.3):
    return int(predicted_rps / rps_per_node * safety_margin) + 1

# 비용 추정
def cost(node_count, monthly_per_node_usd):
    return node_count * monthly_per_node_usd
```

```python
# 부하 테스트 결과 분석
def analyze_load_test_results(results):
    """
    results: [{"rps": int, "p99_ms": float, "error_rate": float}, ...]
    SLO 기준: p99 < 500ms, error_rate < 0.01
    """
    slo_p99_ms = 500
    slo_error_rate = 0.01

    passing = [
        r for r in results
        if r["p99_ms"] < slo_p99_ms and r["error_rate"] < slo_error_rate
    ]
    if not passing:
        return {"max_safe_rps": 0, "bottleneck": "테스트 전 범위에서 SLO 초과"}

    max_safe = max(r["rps"] for r in passing)
    # 한계점 직전 구간에서 병목 확인
    near_limit = [r for r in results if r["rps"] > max_safe]
    return {
        "max_safe_rps": max_safe,
        "headroom_to_next_failure": near_limit[0]["rps"] - max_safe if near_limit else None,
    }

# 예시 결과 분석
results = [
    {"rps": 100, "p99_ms": 120, "error_rate": 0.000},
    {"rps": 200, "p99_ms": 180, "error_rate": 0.001},
    {"rps": 300, "p99_ms": 320, "error_rate": 0.003},
    {"rps": 400, "p99_ms": 610, "error_rate": 0.025},  # SLO 초과
]
# → max_safe_rps: 300
```

```yaml
# k6 부하 테스트: 단계적 부하 증가
stages:
  - duration: 2m
    target: 100   # 워밍업
  - duration: 5m
    target: 300   # 목표 트래픽
  - duration: 2m
    target: 500   # 스파이크 테스트
  - duration: 2m
    target: 0     # 쿨다운

thresholds:
  http_req_duration:
    - "p(99)<500"   # p99 500ms 이하
  http_req_failed:
    - "rate<0.01"   # 오류율 1% 미만
```

## 변경 전후 비교

**Before: 용량 계획 없는 운영**
```text
- 장애 나고 나서 서버 증설
- 얼마나 버티는지 모르는 채 운영
- 트래픽 급증 예측 없음
- 부하 테스트 없이 배포
- 같은 지점에서 반복 장애
```

**After: 용량 계획 기반 운영**
```text
- 부하 테스트로 현재 한계(max_safe_rps) 파악
- 12주 트래픽 예측으로 증설 일정 수립
- 현재 사용률 55%, 목표 70% → 여유분 확인
- 스파이크 테스트로 병목 위치 파악
- 장애 전에 미리 증설 완료
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 부하 테스트 없이 용량 추정 | 실제 한계와 추정치 불일치 | 단계적 부하 증가 테스트로 실측 |
| 최대 부하만 테스트 | 스파이크 패턴을 재현 못 함 | 워밍업 → 목표 → 스파이크 단계 포함 |
| CPU만 보고 병목 판단 | DB 커넥션, 메모리, 네트워크 놓침 | 모든 자원 계층을 함께 모니터링 |
| 안전 여유분 없이 계획 | 예측 오차로 장애 | 필요 노드 × 1.3 안전 마진 적용 |
| 용량 계획을 일회성으로 | 트래픽 패턴 변화 미반영 | 분기마다 재측정, 예측 업데이트 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"k6로 API 서버 부하 테스트 스크립트를 만들어줘.
100→300→500 RPS 단계적 증가, 각 단계 5분 유지,
p99 지연 500ms와 오류율 1% SLO 기준으로 통과 여부 판정,
결과를 CSV로 저장"

# AI 결과물 검증 체크포인트:
# - SLO 기준(p99, error_rate)이 실제 서비스 목표와 일치하는가?
# - 워밍업 단계가 포함되어 있는가?
# - 테스트 중 CPU, 메모리, DB 커넥션을 함께 모니터링하는가?
# - 결과 해석 기준이 명시되어 있는가?
# - 부하 테스트 환경이 프로덕션과 충분히 유사한가?
```

## 운영 체크리스트

- [ ] 현재 시스템의 최대 안전 처리량(max_safe_rps)을 부하 테스트로 측정했다
- [ ] 12주 트래픽 성장 예측과 증설 일정이 수립되어 있다
- [ ] 안전 여유분(1.3배)이 용량 계획에 포함된다
- [ ] 분기마다 부하 테스트를 재실행하고 예측을 업데이트한다
- [ ] 부하 테스트 결과에서 병목 위치(CPU/메모리/DB/네트워크)를 확인한다

## 처음 질문으로 돌아가기

- **용량 계획은 어떤 순서로 하는가?** 현재 한계 측정(부하 테스트) → 성장 예측(선형 추세) → 필요 노드 계산(예측 RPS ÷ 노드당 RPS × 안전 마진) → 증설 일정 수립 순서로 진행합니다.
- **적정 여유분은 얼마인가?** 목표 최대 사용률을 70%로 두면, 현재 55%일 때 약 21% 여유가 있습니다. 예측 트래픽이 현재의 1.21배를 초과하기 전에 증설해야 합니다. 안전 마진 1.3을 곱해 노드 수를 계산합니다.
- **부하 테스트 결과를 어떻게 해석하는가?** p99 지연과 오류율이 SLO 이하를 유지하는 최대 RPS가 현재 안전 처리량입니다. 그 이상에서 어느 자원(CPU/메모리/DB)이 먼저 한계에 도달하는지 확인해 병목을 찾습니다.

## 정리

바이브코딩에서 AI가 인프라 코드를 빠르게 만들어도, 현재 시스템이 얼마나 버티는지 모르면 트래픽 급증 시 장애가 납니다. 부하 테스트로 현재 한계를 측정하고, 성장 예측으로 증설 일정을 수립하고, 안전 여유분을 포함한 용량 계획을 분기마다 업데이트하세요. 다음 글에서는 운영 가능한 시스템을 다룹니다.

## 참고 자료

- [Capacity Planning — Google SRE Book](https://sre.google/sre-book/planning/)
- [k6 부하 테스트 도구](https://k6.io/)
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
- **바이브코딩을 위한 SRE 기초 (9/10): 용량 계획 (현재 글)**
- 바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템
<!-- toc:end -->

Tags: 바이브코딩, SRE, CapacityPlanning, LoadTest, Operations
