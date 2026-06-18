---
title: "바이브코딩을 위한 Serverless 기초 (8/10): 관측성"
series: serverless-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Serverless
  - Observability
  - Logging
  - Tracing
---

# 바이브코딩을 위한 Serverless 기초 (8/10): 관측성

이 글은 "바이브코딩을 위한 Serverless 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 서버리스 함수 코드를 빠르게 만들어 줍니다. 그런데 서버리스 시스템은 짧고 분산되어 있습니다. 한 요청이 여러 함수, 큐, 데이터 저장소를 거칠 수 있는데, 전통적인 서버라면 서버에 들어가 로그를 보면 됐지만 서버리스에서는 그럴 수 없습니다.

AI가 만든 함수 코드에 `print()`나 `console.log()`만 있다면 운영에서 원인을 찾기 어렵습니다. 평문 로그는 검색과 집계가 어렵고, 상관관계 ID가 없으면 여러 함수에 걸친 요청을 추적할 수 없습니다. 콜드 스타트와 실제 처리 지연이 섞여 있으면 어디가 병목인지도 파악하기 어렵습니다.

관측성은 장애 대응 도구이기도 하지만 설계 도구이기도 합니다. 어느 필드를 로그에 남길지, 어떤 메트릭을 집계할지, 어디서 스팬을 열고 닫을지는 나중으로 미루기 어렵습니다. 코드가 배포된 후 추가하려면 전체 수정이 필요합니다.

> **핵심 인사이트:** 서버리스에서는 서버에 들어가 볼 수 없으므로 관측성은 코드가 무엇을 했는지 보는 유일한 창입니다. 상관관계 ID를 모든 함수에 전파하면 여러 함수에 걸친 요청을 하나의 흐름으로 복원할 수 있습니다. 콜드 스타트 여부를 로그에 기록하면 지연이 초기화 비용인지 실제 처리 지연인지 구분됩니다.

## 이 글에서 다룰 문제

- 구조화 로그는 평문 로그와 어떻게 다를까요?
- 상관관계 ID는 서버리스 환경에서 왜 필수에 가까울까요?
- 로그, 메트릭, 트레이스는 각각 어떤 역할을 맡을까요?
- 콜드 스타트를 관측성으로 어떻게 추적할 수 있을까요?
- AI가 만든 함수 코드에서 관측성 관점으로 확인할 것은 무엇인가요?

## 서버리스 관측성 핵심 패턴

```python
import json
import time
import uuid

# 구조화 로그: 기계가 읽기 쉬운 JSON 형식
def log(level, message, **fields):
    print(json.dumps({"level": level, "message": message, **fields},
                     ensure_ascii=False))

# 상관관계 ID 전파: 모든 함수에서 동일 ID 사용
def handler(event, context):
    cid = (event.get("headers") or {}).get(
        "x-correlation-id", str(uuid.uuid4())
    )
    started = time.time()

    log("INFO", "request.accepted",
        correlationId=cid,
        requestId=context.aws_request_id)
    try:
        # 도메인 처리
        elapsed = int((time.time() - started) * 1000)
        log("INFO", "request.completed",
            correlationId=cid, durationMs=elapsed)
        return {"statusCode": 200, "body": json.dumps({"ok": True})}
    except Exception as e:
        elapsed = int((time.time() - started) * 1000)
        log("ERROR", "request.failed",
            correlationId=cid, durationMs=elapsed, error=str(e))
        return {"statusCode": 500, "body": json.dumps({"error": "internal_error"})}
```

```python
# 콜드 스타트 기록: p99 지연이 초기화 비용인지 확인
COLD = True

def handler(event, context):
    global COLD
    log("INFO", "invoke", cold=COLD)
    COLD = False

# 스팬으로 병목 위치 파악
import contextlib

@contextlib.contextmanager
def span(name):
    t0 = time.perf_counter()
    yield
    log("INFO", "span", name=name,
        ms=(time.perf_counter() - t0) * 1000)

# 사용 예시
with span("db_query"):
    result = db.query(sql)

with span("downstream_api"):
    response = requests.get(url)
```

```yaml
# 경보: 실제 대응 가능한 수만 남기기
alarms:
  - name: lambda-errors-high
    metric: Errors
    threshold: 5
    period: 60
    evaluationPeriods: 3
  - name: lambda-duration-p95-high
    metric: DurationP95
    threshold: 800   # ms
    period: 60
    evaluationPeriods: 5
```

## 변경 전후 비교

**Before: 평문 로그만 있는 코드**
```text
- print("주문 처리 시작")로만 기록
- 같은 요청의 로그를 다른 함수에서 찾을 수 없음
- 지연이 콜드 스타트인지 DB 지연인지 모름
- 경보 없이 사용자가 장애를 먼저 발견
```

**After: 구조화 관측성**
```text
- JSON 구조화 로그로 필드 단위 검색/집계
- 상관관계 ID로 여러 함수의 로그를 한 흐름으로 복원
- 콜드 스타트 기록으로 지연 원인 분류
- 스팬으로 병목 위치 정확히 파악
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 평문 로그만 사용 | 검색, 집계, 필터링 어려움 | JSON 구조화 로그 사용 |
| 상관관계 ID 없음 | 여러 함수 로그를 연결할 수 없음 | 요청 시작 시 생성 후 모든 함수에 전파 |
| 민감 정보를 로그에 기록 | 보안 사고 위험 | 토큰, 비밀번호, 개인정보 로깅 금지 |
| 트레이스 100% 수집 | 비용 폭증 | 정상 요청은 낮은 비율, 오류는 100% |
| 대응 불가 경보 남발 | 경보 피로로 진짜 장애 놓침 | 실제 행동으로 이어지는 경보만 유지 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Lambda 핸들러에 구조화 로그와 상관관계 ID를 추가해줘.
JSON 형식으로 level, message, correlationId, durationMs 포함,
콜드 스타트 여부 기록,
외부 API 호출에 span으로 지연 측정"

# AI 결과물 검증 체크포인트:
# - 로그가 JSON 구조화 형식인가?
# - 상관관계 ID를 입력 이벤트에서 읽어 모든 로그에 포함하는가?
# - 콜드 스타트 여부를 기록하는가?
# - 민감 정보(토큰, 비밀번호)가 로그에 없는가?
# - 경보가 실제 대응 절차와 연결되어 있는가?
```

## 운영 체크리스트

- [ ] 모든 함수가 JSON 구조화 로그를 사용한다
- [ ] 상관관계 ID가 모든 함수 경계를 통과해 전파된다
- [ ] 콜드 스타트 여부를 로그에 기록한다
- [ ] 핵심 처리 경로에 스팬으로 지연 측정이 있다
- [ ] 경보가 실제 대응 가능한 수준으로 유지된다

## 처음 질문으로 돌아가기

- **구조화 로그가 필요한 이유는?** 평문 로그는 사람이 읽기엔 편하지만 자동 집계와 필드 단위 필터링이 어렵습니다. JSON 형식이면 CloudWatch Logs Insights나 Splunk에서 `correlationId == "xxx"`로 바로 검색할 수 있습니다.
- **상관관계 ID가 서버리스에서 더 중요한 이유는?** 전통 서버에서는 하나의 프로세스 로그를 따라가면 됐지만, 서버리스에서는 같은 요청이 여러 함수를 거칩니다. 상관관계 ID 없이는 각 함수의 로그가 서로 다른 요청인지 같은 요청인지 알 수 없습니다.
- **로그, 메트릭, 트레이스 중 하나만 쓰면 안 되는가?** 로그는 개별 사건의 세부 내용을, 메트릭은 추세와 집계를, 트레이스는 전체 호출 경로를 봅니다. 하나만으로는 부족합니다. 장애를 빠르게 찾으려면 세 신호가 같은 상관관계 ID로 연결되어야 합니다.

## 정리

바이브코딩에서 AI가 만든 Lambda 코드에 구조화 로그, 상관관계 ID, 콜드 스타트 기록, 스팬 측정이 있는지 반드시 확인하세요. 관측성은 장애가 난 후 추가하기 어렵습니다. 처음부터 설계에 넣어야 "가장 먼저 실패한 요청이 무엇인가"를 몇 분 안에 답할 수 있는 시스템이 됩니다. 다음 글에서는 서버리스 비용을 다룹니다.

## 참고 자료

- [OpenTelemetry 문서](https://opentelemetry.io/docs/)
- [AWS Powertools for Lambda Python](https://github.com/aws-powertools/powertools-lambda-python)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Serverless 기초 (1/10): 서버리스란 무엇인가?
- 바이브코딩을 위한 Serverless 기초 (2/10): 함수형 서비스(FaaS)
- 바이브코딩을 위한 Serverless 기초 (3/10): 트리거와 이벤트
- 바이브코딩을 위한 Serverless 기초 (4/10): 콜드 스타트
- 바이브코딩을 위한 Serverless 기초 (5/10): 스케일링
- 바이브코딩을 위한 Serverless 기초 (6/10): 상태 관리
- 바이브코딩을 위한 Serverless 기초 (7/10): 큐와 이벤트 기반 아키텍처
- **바이브코딩을 위한 Serverless 기초 (8/10): 관측성 (현재 글)**
- 바이브코딩을 위한 Serverless 기초 (9/10): 비용
- 바이브코딩을 위한 Serverless 기초 (10/10): 서버리스 앱 설계
<!-- toc:end -->

Tags: 바이브코딩, Serverless, Observability, Logging, Tracing
