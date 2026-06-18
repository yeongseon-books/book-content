---
series: observability-101
episode: 1
title: "바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Monitoring
  - SRE
  - DevOps
seo_description: AI가 만든 서비스가 프로덕션에서 어떻게 동작하는지 보려면 관측성이 필요합니다. 관측성과 모니터링의 차이, 세 신호의 역할을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?

이 글은 **바이브코딩을 위한 Observability 기초** 시리즈의 첫 번째 글입니다. AI와 함께 코드를 짜는 것은 빠릅니다. 그런데 그 코드가 실제 사용자 트래픽을 받는 순간부터 "정말 잘 돌고 있는가"를 보는 능력이 필요해집니다. 이 시리즈는 바이브코딩으로 만든 서비스를 프로덕션에서 안전하게 운영하기 위한 관측성 기초를 다룹니다.

---

운영 시스템은 대개 시끄럽게 무너지지 않습니다. 사용자는 결제가 느리다고 말하고, 알림은 에러율이 조금 올랐다고 말하고, 로그에는 타임아웃 몇 줄만 남습니다. AI가 생성한 코드라도 마찬가지입니다. 증상은 보이는데 내부에서 무슨 일이 일어났는지 바로 설명되지 않는 순간이 반드시 옵니다.

바이브코딩으로 빠르게 서비스를 만들수록, "동작하는 코드"와 "프로덕션에서 안심할 수 있는 코드" 사이의 거리가 더 크게 느껴집니다. 그 거리를 줄이는 것이 바로 관측성입니다.

> "AI가 만든 코드가 프로덕션에서 잘 돌고 있는지 보려면, 시스템 바깥에서 안쪽 상태를 읽을 수 있어야 합니다. 관측성은 그 능력입니다."

## 이 글에서 다룰 문제

- 관측성과 모니터링은 무엇이 다를까요?
- 메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?
- 왜 세 신호를 함께 봐야 할까요?
- 바이브코딩 맥락에서 관측성을 잘못 이해하면 어떤 일이 생길까요?
- 처음 관측성을 붙일 때 가장 자주 놓치는 것은 무엇일까요?

---

바이브코딩으로 만든 서비스는 빠르게 배포됩니다. AI가 FastAPI 앱을 짜주고, Docker 이미지를 만들고, 클라우드에 올리는 것까지 함께 해주기 때문입니다. 그런데 배포한 다음날, 사용자가 "결제가 안 돼요"라고 제보합니다. 로그를 뒤지지만 자유 형식 텍스트라 어디서 무슨 일이 있었는지 바로 나오지 않습니다.

이 순간이 바로 관측성이 없는 서비스의 현실입니다. 대시보드는 미리 준비한 질문에만 답합니다. CPU가 올랐는지, 에러율이 늘었는지는 금방 보이지만, 왜 결제만 느린지, 어느 서비스가 병목인지는 훨씬 오래 걸립니다.

## 모니터링 vs 관측 가능성

| 구분 | 모니터링 | 관측 가능성 |
| --- | --- | --- |
| 목적 | 이미 알고 있는 장애를 감시 | 처음 보는 문제를 파고들기 |
| 질문 방식 | 미리 정한 질문 (CPU 올랐나? 에러율 높나?) | 즉석 질문 (왜 이번 요청만 느릴까?) |
| 도구 | 경보, 대시보드, 체크 스크립트 | 메트릭, 로그, 트레이스 + 질의 인터페이스 |
| 한계 | 새로운 장애 패턴 앞에서 무력 | 질문 설계와 신호 품질이 핵심 |

모니터링은 "이상이 있는가"를 묻고, 관측 가능성은 "왜 이런 일이 생겼는가"를 묻습니다. 바이브코딩으로 만든 서비스는 처음 보는 장애가 더 자주 나타납니다. AI가 예상치 못한 방식으로 외부 API를 호출하거나, 예상보다 많은 DB 연결을 만들 수 있습니다. 그럴 때 관측 가능성이 있어야 빠르게 원인을 찾을 수 있습니다.

## 세 신호: 메트릭, 로그, 트레이스

| 신호 | 답하는 질문 | 저장 형태 | 대표 도구 |
| --- | --- | --- | --- |
| 메트릭 | 언제부터 이상한가? 얼마나 심한가? | 시계열 숫자 | Prometheus, Datadog |
| 로그 | 그 순간 실제로 무슨 일이 있었는가? | 구조화된 이벤트 | Loki, Elasticsearch |
| 트레이스 | 요청이 어디를 거쳤고 어디서 멈췄는가? | span 트리 | Jaeger, Tempo |

세 신호는 서로 다른 해상도에서 같은 시스템을 비추는 렌즈입니다. 메트릭은 넓게, 트레이스는 깊게, 로그는 세밀하게 봅니다.

## 바이브코딩 관점: AI가 만든 코드에 신호 붙이기

AI에게 "FastAPI 앱을 만들어줘"라고 하면 동작하는 코드를 받습니다. 그런데 그 코드에 관측성 신호가 없다면, 프로덕션에서 무언가 잘못됐을 때 아무것도 알 수 없습니다.

AI와 함께 코딩할 때 관측성을 붙이는 가장 단순한 시작은 구조화된 로그입니다.

```python
import json
import time
import uuid
from fastapi import FastAPI, Request

app = FastAPI()

def log_event(event: str, **fields):
    print(json.dumps({
        "ts": time.time(),
        "event": event,
        **fields
    }))

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start = time.time()

    log_event("request_start",
              request_id=request_id,
              method=request.method,
              path=request.url.path)

    response = await call_next(request)
    duration = time.time() - start

    log_event("request_end",
              request_id=request_id,
              status=response.status_code,
              duration_ms=round(duration * 1000, 2))

    return response
```

이 코드를 AI에게 요청할 때 "모든 요청에 request_id를 붙이고 JSON 로그로 시작과 끝을 남겨줘"라고 프롬프트를 주면 비슷한 구조를 바로 받을 수 있습니다.

## Before / After: 관측성이 없을 때와 있을 때

**Before (관측성 없음)**

```text
새벽 3시, 사용자 제보: "결제가 안 돼요"
→ 로그 뒤지기 시작 (자유 형식 텍스트)
→ grep으로 "error" 검색 → 수백 줄
→ 어느 요청인지, 언제부터인지 모름
→ 1시간 후에도 원인 불명
```

**After (관측성 있음)**

```text
새벽 3시, 경보: checkout p95 latency > 1.5s
→ 메트릭: /checkout 경로만 지연 급증, 시작 시점 확인
→ 트레이스: payment span이 전체 지연의 90%
→ 로그: payment_timeout, gateway="stripe", retry=3
→ 15분 안에 원인 파악, 조치 완료
```

## 자주 하는 실수

| 실수 | 증상 | 바이브코딩 맥락에서의 위험 |
| --- | --- | --- |
| 모니터링과 관측성을 같은 것으로 봄 | 새 패턴 장애에서 경보 미탐 | AI가 만든 예상 밖 동작을 놓침 |
| 메트릭만 수집 | 추세는 보이지만 이유 설명 불가 | "왜 느린지" 영원히 모름 |
| 로그를 자유 형식 텍스트로만 남김 | grep만 가능, 집계 불가 | 장애 시 수백 줄을 수동으로 읽어야 함 |
| 서비스 간 trace_id 미전달 | 요청 흐름이 중간에서 끊김 | 마이크로서비스 장애 원인 추적 불가 |
| 모든 신호를 무기한 보관 | 비용 폭증 | 소규모 팀 예산 초과 |

## AI 프롬프트 팁

바이브코딩 워크플로에서 관측성을 처음 붙일 때 유용한 AI 프롬프트 패턴입니다.

```text
[프롬프트 예시]
"이 FastAPI 앱에 다음을 추가해줘:
1. 모든 요청에 request_id 생성 (헤더에서 가져오거나 UUID 생성)
2. 요청 시작/끝을 JSON 형식으로 로깅 (ts, event, request_id, method, path, status, duration_ms 필드)
3. OpenTelemetry 자동 계측 추가 (FastAPIInstrumentor 사용)
4. OTLP 내보내기 설정 (환경변수로 엔드포인트 설정 가능하게)"
```

이 프롬프트 하나로 관측성의 첫 번째 계층(로그 + 트레이스)을 한꺼번에 붙일 수 있습니다.

## 운영 체크리스트

- [ ] 모니터링과 관측성의 차이를 설명할 수 있습니다.
- [ ] 메트릭, 로그, 트레이스의 역할을 각각 말할 수 있습니다.
- [ ] 구조화된 로그 한 줄을 직접 만들 수 있습니다.
- [ ] trace_id가 왜 필요한지 설명할 수 있습니다.
- [ ] AI 프롬프트로 관측성 코드를 요청하는 방법을 압니다.

## 처음 질문으로 돌아가기

- **관측성과 모니터링은 무엇이 다를까요?**
  모니터링은 미리 정한 질문만 감시합니다. 관측성은 처음 보는 장애에서도 바깥 신호로 안쪽 상태를 추론합니다. AI가 만든 코드는 예상 밖 동작을 더 자주 일으키므로, 관측성이 더욱 중요합니다.

- **메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?**
  메트릭은 "언제부터 이상한가", 로그는 "그 순간 무슨 일이 있었는가", 트레이스는 "요청이 어디서 멈췄는가"에 답합니다.

- **왜 세 신호를 함께 봐야 할까요?**
  메트릭만으로는 이유를 모르고, 로그만으로는 전체 흐름을 모릅니다. 세 신호를 함께 읽을 때 장애가 인과 관계로 보이기 시작합니다.

---

## 정리

관측성은 시스템 바깥에서 안쪽을 묻는 운영 기술입니다. 바이브코딩으로 서비스를 빠르게 만들수록, 프로덕션에서 그 서비스가 어떻게 동작하는지 볼 수 있는 눈이 필요합니다. 메트릭은 추세를, 로그는 맥락을, 트레이스는 경로를 보여줍니다. 다음 글에서는 이 세 신호가 각각 어떤 질문에 답하는지 더 자세히 살펴봅니다.

## 참고 자료

- [OpenTelemetry overview](https://opentelemetry.io/docs/concepts/)
- [Google SRE Book — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Three Pillars of Observability](https://www.cncf.io/blog/2022/05/24/observability-cloud-native/)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/)

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가? (현재 글)**
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스
- 바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화
- 바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅
- 바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): 서비스 수준 지표와 목표 기초
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Monitoring, SRE, DevOps
