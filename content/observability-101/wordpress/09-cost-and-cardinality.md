---
title: "바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티"
series: observability-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Cost
  - Cardinality
  - Sampling
---

# 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티

이 글은 "바이브코딩을 위한 Observability 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 메트릭, 로그, 트레이스 수집 코드를 빠르게 만들어 줍니다. 그런데 어느 날부터 관측성 청구서가 갑자기 열 배쯤 커졌다는 이야기가 나옵니다. 대개는 수집량이 조금 늘어서가 아니라 구조가 잘못돼서 그렇습니다.

관측성 도입 초기에는 비용이 크게 보이지 않습니다. 그러다 어느 순간 시스템을 이해하려고 붙인 관측성 도구가 정작 제품 비용보다 더 큰 압박이 됩니다.

비용을 폭발시키는 대표 원인은 세 가지입니다. 고유값을 메트릭 라벨에 넣어 카디널리티를 키우는 일, 모든 신호를 오래 보관하는 일, 샘플링 없이 트레이스를 전부 저장하는 일입니다.

카디널리티 제어, 보존 계층 분리, 꼬리 샘플링을 중심으로 정리합니다.

> **핵심 인사이트:** `user_id`를 Prometheus 라벨에 넣으면 사용자 수만큼 시계열이 생깁니다. 100만 사용자면 100만 시계열입니다. 사용자 식별자는 로그나 트레이스로 보내고, 메트릭 라벨은 유한한 차원만 사용해야 합니다.

## 이 글에서 다룰 문제

- 카디널리티는 왜 비용과 직접 연결될까요?
- 보존 기간을 나눠 가져가야 하는 이유는 무엇일까요?
- 머리 샘플링과 꼬리 샘플링은 어떻게 다를까요?
- 관측성 비용을 예측 가능하게 만드는 방법은 무엇일까요?
- AI가 만든 수집 코드에서 확인해야 할 것은 무엇인가요?

## 비용과 카디널리티 핵심 패턴

```promql
# 카디널리티 측정: 어떤 메트릭이 시계열을 많이 만드는지 확인
count({__name__=~".+"})                      # 전체 시계열 수
topk(20, count by (__name__) ({__name__=~".+"}))  # 상위 20개 메트릭
```

```text
# 나쁜 예: user_id를 메트릭 라벨에 → 사용자 수만큼 시계열 폭발
http_requests_total{user_id="42", path="/buy"}

# 좋은 예: 유한한 차원만 라벨에 → user_id는 로그로
http_requests_total{path="/buy"}
```

```yaml
# 보존 계층 분리: 오래된 데이터는 낮은 해상도로
prometheus:
  retention: 15d             # 최근 15일: 원본 해상도
thanos:
  retention.resolution-raw: 30d   # 30일: 원본
  retention.resolution-5m: 90d    # 90일: 5분 집계
  retention.resolution-1h: 365d   # 1년: 1시간 집계

# 꼬리 샘플링: 중요한 트레이스만 저장
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 500 }
      - name: random
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

## 변경 전후 비교

**Before: 구조 없이 수집**
```text
- user_id, request_id를 메트릭 라벨에 → 시계열 폭발
- 모든 로그와 트레이스를 같은 해상도로 오래 보관
- 트레이스를 100% 저장 → 비용 폭발
- 어떤 라벨이 비용을 키우는지 모름
```

**After: 구조화된 수집**
```text
- 메트릭 라벨: 유한한 차원만 (path, method, status_code)
- 사용자 식별자: 로그/트레이스로 이동
- 보존 계층: 최근은 정밀, 오래된 것은 집계
- 꼬리 샘플링: 에러/느린 요청 + 5% 무작위만 저장
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| user_id/request_id를 메트릭 라벨에 | 무한 시계열 → 비용 폭발 | 유한 차원만 라벨, 식별자는 로그로 |
| 모든 데이터를 같은 기간 보관 | 불필요한 저장 비용 | 보존 계층 분리 (hot/warm/cold) |
| 트레이스 100% 저장 | 성능 오버헤드 + 비용 | 꼬리 샘플링으로 5% + 에러 저장 |
| 비용 모니터링 없음 | 청구서 받기 전까지 모름 | 월별 시계열 수 + 저장량 트래킹 |
| 카디널리티 확인 없이 새 라벨 추가 | 시계열이 갑자기 늘어남 | 추가 전 카디널리티 영향 추정 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"FastAPI 서비스에 Prometheus 메트릭을 추가해줘.
HTTP 요청 카운터 (method, path, status_code 라벨만),
응답 시간 히스토그램 (p50/p95/p99),
user_id, request_id는 메트릭 라벨에 절대 넣지 말 것"

# AI 결과물 검증 체크포인트:
# - 메트릭 라벨이 유한한 차원인가? (path는 /users, /orders 등 고정값)
# - user_id, session_id 같은 고유값이 라벨에 없는가?
# - 지연 시간이 히스토그램으로 측정되어 p95/p99가 가능한가?
# - 트레이스 샘플링 비율이 설정되어 있는가?
# - 오래된 데이터 보존 정책이 있는가?
```

## 운영 체크리스트

- [ ] 메트릭 라벨에 고유값(user_id, request_id)이 없다
- [ ] 총 시계열 수를 정기적으로 모니터링한다
- [ ] 보존 계층이 분리되어 있다 (hot/warm/cold)
- [ ] 트레이스에 꼬리 샘플링이 적용되어 있다
- [ ] 신호별 월간 예산이 정의되어 있다

## 처음 질문으로 돌아가기

- **카디널리티란?** 메트릭의 고유한 라벨 조합 개수입니다. user_id가 10만이면 같은 메트릭이 10만 시계열을 만듭니다. Prometheus는 메모리에 시계열을 유지하므로 카디널리티가 높으면 메모리와 비용이 폭발합니다.
- **머리 샘플링과 꼬리 샘플링의 차이는?** 머리 샘플링은 요청 시작 시점에 저장 여부를 결정합니다. 꼬리 샘플링은 트레이스가 끝난 후 느리거나 실패한 것만 저장합니다. 꼬리 샘플링이 가치 있는 트레이스를 더 잘 보존합니다.
- **보존 계층을 나누는 이유는?** 최근 데이터는 정밀하게 자주 접근하지만, 과거 데이터는 낮은 해상도로도 충분하고 접근 빈도가 낮습니다. 계층을 나누면 저장 비용을 크게 줄이면서 필요한 데이터를 보존할 수 있습니다.

## 정리

바이브코딩에서 AI가 만들어 준 수집 코드에서 메트릭 라벨의 카디널리티, 보존 기간, 트레이스 샘플링을 반드시 확인하세요. 관측성 비용 문제는 수집을 시작한 후에 갑자기 나타납니다. 처음부터 유한한 라벨, 계층화 보존, 꼬리 샘플링을 설계에 넣어야 합니다. 다음 글에서는 운영 가능한 관측성 스택을 다룹니다.

## 참고 자료

- [Prometheus — Best Practices for Naming Metrics](https://prometheus.io/docs/practices/naming/)
- [OpenTelemetry — Tail Sampling Processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/observability-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭
- 바이브코딩을 위한 Observability 기초 (3/10): 로그
- 바이브코딩을 위한 Observability 기초 (4/10): 트레이스
- 바이브코딩을 위한 Observability 기초 (5/10): 세 신호 연결
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): SLI와 SLO
- **바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티 (현재 글)**
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Cost, Cardinality, Sampling
