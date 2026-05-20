---
series: serverless-101
episode: 1
title: "Serverless 101 (1/10): 서버리스란 무엇인가?"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Serverless
  - Cloud
  - FaaS
  - Architecture
  - DevOps
seo_description: 서버리스의 정의를 첫 번째 함수 워크플로, 배포 계약, 비용 판단, 부적합 워크로드 기준까지 함께 설명합니다
last_reviewed: '2026-05-16'
---

# Serverless 101 (1/10): 서버리스란 무엇인가?

이 글은 Serverless 101 시리즈의 첫 번째 글입니다.

서버리스를 처음 들으면 대개 “서버를 안 만지는 방식이구나”라고 이해합니다. 방향은 맞지만, 그 한 문장만으로는 이후 판단이 자꾸 틀어집니다. 서버가 사라지는 것이 아니라 **서버 운영 책임의 기본값이 플랫폼으로 이동**하기 때문입니다.

그래서 서버리스 입문에서 가장 먼저 잡아야 할 질문은 “함수를 어떻게 쓰지?”가 아닙니다. **“이 워크로드를 정말 서버리스로 시작해도 되는가?”** 입니다. 이 판단을 먼저 해 두어야 첫 번째 함수 예제도 의미가 생기고, 뒤이어 나올 FaaS, 트리거, 콜드 스타트, 비용 이야기도 같은 멘탈 모델 안에서 읽힙니다.

## 먼저 던지는 질문

- 서버리스는 정확히 무엇을 플랫폼에 넘기는 실행 모델일까요?
- 첫 번째 서버리스 함수는 어떤 입력 계약과 응답 계약으로 시작해야 할까요?
- 로컬 호출과 실제 배포 사이에서 최소한 무엇을 맞춰 두어야 할까요?

## 큰 그림

![Serverless 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/01/01-01-concept-at-a-glance.ko.png)

*Serverless 101 1장 흐름 개요*

이 그림에서는 서버리스란 무엇인가?를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 서버리스란 무엇인가?의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 서버리스가 틀린 기본값인 순간부터 먼저 구분하기

많은 팀이 서버리스를 “더 빠른 시작 방법”으로만 봅니다. 하지만 실제로는 **잘 맞는 문제에 쓰면 강력하고, 안 맞는 문제에 쓰면 우회 비용이 커지는 실행 모델**입니다. 입문 단계에서 아래 질문을 먼저 통과시키면 이후 판단이 훨씬 선명해집니다.

### 서버리스 적합성 결정 사다리

1. **요청이 수 초 안에 끝나는가?**
   - 예: 다음 질문으로 갑니다.
   - 아니오: 장시간 작업, 실시간 스트리밍 연결, 지속 계산은 다른 실행 환경이 더 단순할 수 있습니다.
2. **호출마다 필요한 상태를 외부 저장소에서 읽고 쓸 수 있는가?**
   - 예: 다음 질문으로 갑니다.
   - 아니오: 프로세스 메모리나 로컬 파일에 오래 붙잡아 둬야 하는 상태가 핵심이면 서버리스 기본값은 위험합니다.
3. **트래픽이 들쭉날쭉하거나 예측하기 어려운가?**
   - 예: 서버리스의 탄력성이 강점이 됩니다.
   - 아니오: 일정하고 오래 지속되는 부하라면 상시 실행 환경이 비용상 더 단순할 수 있습니다.
4. **플랫폼이 정한 타임아웃, 패키징, 런타임 제약을 받아들일 수 있는가?**
   - 예: 서버리스가 좋은 출발점입니다.
   - 아니오: 세밀한 런타임 제어나 장시간 연결이 핵심이면 컨테이너나 VM이 더 낫습니다.

이 네 질문 중 하나라도 초반부터 강하게 “아니오”라면 서버리스를 억지로 기본값으로 둘 필요가 없습니다. 좋은 아키텍처 판단은 최신 유행을 고르는 일이 아니라, **운영 제약을 가장 솔직하게 받아들이는 일**입니다.

## 왜 이 주제가 중요한가

서버리스의 장점은 분명합니다. 패치, 기본 스케일링, 실행 인프라 운영 같은 반복 작업을 플랫폼에 넘기고 팀은 기능 개발에 집중할 수 있습니다. 작은 팀일수록 이 효과를 크게 체감합니다.

문제는 장점이 곧바로 단순함을 뜻하지는 않는다는 점입니다. 호출이 있을 때만 비용이 발생한다고 해도, 실제 청구는 호출 수만이 아니라 실행 시간, 메모리, 네트워크 전송, 연결된 관리형 서비스 비용까지 합쳐서 결정됩니다. 함수 수를 잘게 쪼갠다고 해서 분산 시스템의 복잡성이 사라지는 것도 아닙니다.

그래서 첫 글에서 반드시 바로잡아야 할 오해가 하나 있습니다. **서버리스는 편한 서버가 아니라 다른 운영 계약**입니다. 이 계약의 핵심은 “무엇이 자동화되었는가”보다 “무엇을 여전히 내가 설계해야 하는가”에 있습니다.

## 한눈에 보는 구조

이 그림에서 핵심 주체는 함수보다 플랫폼입니다. 이벤트가 들어오면 플랫폼이 실행 환경을 준비하고, 핸들러를 호출하고, 필요하면 재시도하거나 새 인스턴스를 만듭니다. 개발자는 직접 서버를 띄우지 않지만, 대신 **입력 계약, 응답 형식, 상태 저장 위치, 관측성 기준**을 더 명확하게 정해야 합니다.

## 첫 번째 서버리스 함수 워크플로: HTTP 요청 하나를 정상 처리해 보기

이 글에서는 개념만 설명하지 않고, 이후 글에서도 계속 재사용할 아주 작은 주문 접수 예제를 기준으로 보겠습니다. 목표는 단순합니다. **HTTP 이벤트 하나를 받아 검증하고, 플랫폼이 기대하는 형식으로 응답을 돌려주는 최소 계약**을 확인하는 것입니다.

### 1단계 — 핸들러 계약 정하기

```python
import json
from datetime import UTC, datetime

def build_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }

def handler(event: dict, context) -> dict:
    request_id = getattr(context, "aws_request_id", "local-request")
    payload = json.loads(event.get("body") or "{}")

    order_id = payload.get("order_id")
    customer_tier = payload.get("customer_tier", "standard")
    items = payload.get("items", [])

    if not order_id or not items:
        return build_response(
            400,
            {
                "ok": False,
                "request_id": request_id,
                "error": "order_id and items are required",
            },
        )

    total_quantity = sum(item["quantity"] for item in items)

    return build_response(
        202,
        {
            "ok": True,
            "request_id": request_id,
            "accepted_at": datetime.now(UTC).isoformat(),
            "order_id": order_id,
            "customer_tier": customer_tier,
            "total_quantity": total_quantity,
            "next_step": "queued-for-fulfillment",
        },
    )
```

여기서 중요한 것은 복잡한 비즈니스 로직이 아닙니다. 첫 번째 함수에서 먼저 맞춰야 할 계약은 네 가지입니다.

- 입력은 `event`와 `context`로 들어옵니다.
- 실제 비즈니스 입력은 `event["body"]` 안 JSON이라는 점을 분명히 합니다.
- 검증 실패 시에도 플랫폼이 이해할 수 있는 HTTP 응답 형식을 돌려줍니다.
- 성공 시에도 다음 단계가 무엇인지 응답에 남겨 호출 의미를 분명히 합니다.

### 2단계 — 이벤트 페이로드를 명시적으로 고정하기

```python
sample_event = {
    "httpMethod": "POST",
    "path": "/orders",
    "headers": {"content-type": "application/json"},
    "body": json.dumps(
        {
            "order_id": "ord-1001",
            "customer_tier": "gold",
            "items": [
                {"sku": "keyboard", "quantity": 1},
                {"sku": "mouse", "quantity": 2},
            ],
        }
    ),
}
```

서버리스 입문에서 흔한 실수는 핸들러 코드만 보고 이벤트 구조를 흐릿하게 넘기는 일입니다. 그러나 운영에서는 함수 이름보다 **이벤트 모양이 더 중요**합니다. HTTP 이벤트, 큐 이벤트, 스케줄 이벤트는 입력 구조와 실패 의미가 완전히 다르기 때문입니다.

### 3단계 — 로컬 호출 진입점을 분리하기

```python
class LocalContext:
    aws_request_id = "req-local-001"

if __name__ == "__main__":
    result = handler(sample_event, LocalContext())
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

실무에서 좋은 시작점은 플랫폼 없이도 함수 본체를 한 번 성공시켜 보는 것입니다. 이렇게 해야 함수가 실패했을 때 **핸들러 로직 문제인지, 배포 설정 문제인지** 더 빨리 구분할 수 있습니다.

실행 명령은 다음처럼 단순하게 시작해도 충분합니다.

```bash
python3 app.py
```

### 4단계 — 기대 결과를 미리 문서화하기

```json
{
  "statusCode": 202,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"ok\": true, \"request_id\": \"req-local-001\", \"accepted_at\": \"2026-05-16T10:00:00+00:00\", \"order_id\": \"ord-1001\", \"customer_tier\": \"gold\", \"total_quantity\": 3, \"next_step\": \"queued-for-fulfillment\"}"
}
```

서버리스 글에서 기대 결과를 명시하는 이유는 단순히 친절함 때문이 아닙니다. 성공 기준이 없으면 이후 글에서 큐, 재시도, DLQ를 설명할 때도 “무엇이 정상 상태인지”가 계속 흐려집니다.

## 이 함수가 암묵적으로 전제하는 배포 계약

첫 번째 함수 예제라도 로컬 장난감 코드에서 끝나면 안 됩니다. 실제 배포를 염두에 두면 아래 계약이 이미 숨어 있습니다.

| 항목 | 이 예제의 계약 | 왜 중요한가 |
| --- | --- | --- |
| 이벤트 형식 | HTTP 이벤트의 `body`는 JSON 문자열입니다 | 로컬 테스트와 실제 플랫폼 입력을 맞추기 위해 필요합니다 |
| 타임아웃 예산 | 이 함수는 수 초 안에 끝나는 작업만 맡습니다 | 장시간 처리 작업을 섞으면 곧바로 타임아웃과 재시도 비용이 커집니다 |
| 상태 경계 | 주문 상태 자체는 함수 안에 저장하지 않습니다 | 프로세스 메모리나 로컬 파일은 신뢰할 수 있는 저장소가 아닙니다 |
| 로그 필드 | `request_id`, `order_id`, `next_step`를 남깁니다 | 이후 중복 처리와 장애 추적의 최소 단서가 됩니다 |

이 표가 중요한 이유는 서버리스가 “코드 몇 줄을 실행하는 기능”이 아니기 때문입니다. 함수 본문은 짧아 보여도, 실제 운영은 언제나 **이벤트 계약 + 실행 시간 예산 + 외부 상태 경계 + 로그 기준** 위에서 성패가 갈립니다.

## 운영자가 첫 함수에서 바로 확인해야 할 체크포인트

처음부터 거창한 관측성을 붙일 필요는 없습니다. 대신 아래 네 가지는 첫 함수 단계에서 바로 확인하는 편이 좋습니다.

1. **이벤트 모양이 문서화되어 있는가**
   - 필수 필드와 선택 필드가 구분되어 있어야 합니다.
2. **타임아웃 안에 끝나는 경계만 함수에 넣었는가**
   - 오래 걸리는 후속 작업은 비동기로 넘기는 편이 낫습니다.
3. **상태를 외부 저장소에 두도록 설계했는가**
   - “일단 메모리에 들고 가자”는 설계는 다음 글들에서 거의 항상 문제를 만듭니다.
4. **추적용 로그 필드가 정해져 있는가**
   - `request_id`, `order_id`, `event_type` 같은 공통 키가 없으면 운영이 급격히 어려워집니다.

## 실무에서 자주 헷갈리는 지점

### 서버리스면 자동으로 비용이 낮아질까요?

그렇지 않습니다. 호출 수가 적어도 실행 시간이 길거나 메모리 설정이 크면 비용이 커질 수 있습니다. 여기에 메시지 큐, 데이터베이스, 네트워크 전송 비용까지 더해지면 체감은 더 달라집니다.

### 함수가 짧으면 설계도 자동으로 단순해질까요?

아닙니다. 함수가 짧아져도 시스템 경계가 늘어나면 오히려 추적과 재시도 설계가 더 어려워질 수 있습니다. 서버리스는 코드 줄 수보다 **이벤트 경계 설계**가 더 중요합니다.

### 서버리스는 모든 API 백엔드의 좋은 출발점일까요?

짧고 독립적인 요청, 트래픽 변동이 큰 API, 이벤트 기반 후처리에는 좋습니다. 반대로 장시간 연결, 실시간 게임 세션, 지속적 스트리밍, 세밀한 런타임 제어가 필요한 서비스는 상시 실행 환경이 더 단순할 수 있습니다.

## 체크리스트

- [ ] 이 워크로드가 서버리스 적합성 결정 사다리를 통과하는가
- [ ] 첫 함수의 입력 이벤트와 응답 형식을 문서화했는가
- [ ] 상태를 외부 저장소로 분리할 계획이 있는가
- [ ] 요청 추적용 로그 필드를 정했는가

## 정리

서버리스의 핵심은 서버 삭제가 아니라 책임 이동입니다. 플랫폼이 실행 환경 준비와 기본 운영을 맡는 대신, 개발자는 이벤트 계약, 상태 경계, 시간 예산, 관측성 기준을 더 명확하게 설계해야 합니다.

이번 글의 가장 작은 예제는 주문 접수용 HTTP 핸들러 하나였지만, 그 안에도 이미 서버리스의 핵심 계약이 모두 들어 있었습니다. 다음 글에서는 이 예제를 이어 받아, 실제로 **패키지를 만들고 실행하고 측정하는 FaaS 워크플로**를 보겠습니다.

## 처음 질문으로 돌아가기

- **서버리스는 정확히 무엇을 플랫폼에 넘기는 실행 모델일까요?**
  - 본문의 기준은 서버리스란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **첫 번째 서버리스 함수는 어떤 입력 계약과 응답 계약으로 시작해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **로컬 호출과 실제 배포 사이에서 최소한 무엇을 맞춰 두어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **서버리스란 무엇인가? (현재 글)**
- 함수형 서비스(FaaS)란 무엇인가? (예정)
- 트리거와 이벤트 (예정)
- 콜드 스타트 (예정)
- 스케일링 (예정)
- 상태 관리 (예정)
- 큐와 이벤트 기반 아키텍처 (예정)
- 관측성 (예정)
- 비용 (예정)
- 서버리스 앱 설계 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [AWS Lambda 개요](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Google Cloud Functions 개요](https://cloud.google.com/functions/docs)
- [Azure Functions 개요](https://learn.microsoft.com/azure/azure-functions/functions-overview)

### 아키텍처와 운영 가이드

- [Serverless 정의 - Martin Fowler](https://martinfowler.com/articles/serverless.html)
- [AWS Serverless Lens](https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/welcome.html)
- [Azure Well-Architected Framework for serverless workloads](https://learn.microsoft.com/azure/well-architected/service-guides/azure-functions)

### 코드와 관련 읽을거리

- [AWS Lambda 개발자 가이드 예제 (GitHub)](https://github.com/awsdocs/aws-lambda-developer-guide)
- [Azure Functions 101](../../azure-functions-101/ko/)

Tags: Serverless, Cloud, FaaS, Architecture, DevOps
