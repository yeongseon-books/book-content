---
series: serverless-101
episode: 2
title: "Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?"
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
  - FaaS
  - Lambda
  - Runtime
  - Cloud
seo_description: FaaS를 개념 설명이 아니라 실제 패키지 생성, 스모크 테스트, 아티팩트 점검, 측정 흐름으로 설명합니다
last_reviewed: '2026-05-16'
---

# Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?

이 글은 Serverless 101 시리즈의 두 번째 글입니다.

서버리스를 책임 이동 관점으로 이해했다면, 이제 다음 질문이 남습니다. **“그 책임 이동은 실제 배포 단위에서 어떻게 보이는가?”** 이 질문에 답하지 못하면 FaaS는 계속 추상적인 슬로건으로 남고, 패키지 크기, 런타임 차이, 메모리 튜닝, 콜드 스타트를 전부 감으로만 다루게 됩니다.

그래서 이번 글은 개념 나열 대신 하나의 짧은 루프에 집중합니다. **코드를 만들고, 패키지로 묶고, 로컬에서 같은 입력으로 실행하고, 결과와 아티팩트 크기를 확인하고, 그다음에야 메모리나 런타임을 조정하는 루프**입니다. FaaS를 제대로 다루는 팀은 거의 항상 이 순서로 움직입니다.

## 먼저 던지는 질문

- FaaS의 실행 계약은 핸들러, 런타임, 패키지 사이에서 어떻게 만들어질까요?
- 실제 배포 전에는 어떤 파일 구조와 명령 순서로 검증하는 편이 좋을까요?
- 패키지 크기와 의존성 수는 왜 실행 시간과 콜드 스타트에 직접 영향을 줄까요?

## 큰 그림

![Serverless 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/02/02-01-concept-at-a-glance.ko.png)

*Serverless 101 2장 흐름 개요*

## 왜 이 주제가 중요한가

입문 글에서는 FaaS를 “함수만 올리면 끝나는 서비스”처럼 설명하기 쉽습니다. 하지만 운영에서는 그 반대입니다. 핸들러보다 먼저 패키지가 로드되고, 패키지보다 먼저 런타임이 준비되며, 초기화 비용은 핸들러 본문이 실행되기도 전에 이미 지연 시간으로 청구됩니다.

그래서 성능 문제도 핸들러 한 줄만 고쳐서는 잘 해결되지 않습니다. 불필요한 대형 의존성, 과도한 파일 포함, 런타임 버전 차이, 환경 변수 누락이 같은 정도로 중요합니다. FaaS를 이해한다는 말은 함수 본문을 아는 것이 아니라, **실행 전후를 포함한 배포 계약 전체를 이해한다는 뜻**입니다.

## 한눈에 보는 구조

이 흐름을 실무적으로 풀면 이렇습니다. 개발자는 핸들러를 작성하고, 의존성을 함께 묶어 패키지를 만들고, 플랫폼은 그 패키지를 특정 런타임에서 로드한 뒤 핸들러를 호출합니다. 그러므로 FaaS 성능과 안정성은 자연스럽게 **핸들러 코드 + 패키지 내용 + 런타임 준비 비용**의 합으로 결정됩니다.

## 오늘 사용할 예제 계약

이번 글도 1편의 주문 접수 예제를 이어 갑니다. 차이는 목표가 다릅니다. 1편이 “첫 함수 호출을 성공시키는 글”이었다면, 이번 글은 **같은 핸들러를 FaaS 배포 단위로 만드는 글**입니다.

예제 디렉터리는 아래처럼 둡니다.

```text
faas-demo/
├── app.py
├── smoke_test.py
└── requirements.txt
```

### requirements.txt

```text
requests==2.32.3
```

이 의존성은 일부러 작게 시작합니다. FaaS 첫 패키지에서 중요한 것은 “무엇을 얼마나 넣었는가”를 통제하는 감각입니다. 사용하지 않는 대형 라이브러리를 무심코 추가하는 순간, 패키지 크기와 초기화 시간이 함께 나빠집니다.

### app.py

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

    return build_response(
        202,
        {
            "ok": True,
            "request_id": request_id,
            "accepted_at": datetime.now(UTC).isoformat(),
            "order_id": order_id,
            "item_count": len(items),
        },
    )
```

### smoke_test.py

```python
import json

from app import handler

class LocalContext:
    aws_request_id = "req-smoke-001"

event = {
    "body": json.dumps(
        {
            "order_id": "ord-1001",
            "items": [
                {"sku": "keyboard", "quantity": 1},
                {"sku": "mouse", "quantity": 2},
            ],
        }
    )
}

result = handler(event, LocalContext())
print(json.dumps(result, ensure_ascii=False, indent=2))
```

이렇게 파일을 나누는 이유는 단순합니다. **핸들러 파일과 검증 파일을 분리해야 배포 단위와 검증 단위를 각각 통제할 수 있기 때문**입니다. `app.py`는 런타임이 로드할 실제 진입점이고, `smoke_test.py`는 같은 입력 계약으로 로컬에서 재현하는 최소 검증기입니다.

## build → package → run → measure 루프

이제부터가 FaaS의 핵심입니다. 순서는 바꾸지 않는 편이 좋습니다.

### 1단계 — 의존성을 별도 폴더에 설치합니다

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt -t package
cp app.py package/
```

여기서 `-t package`가 중요한 이유는 FaaS 패키지가 결국 “실행 시 필요한 파일 집합”이기 때문입니다. 가상환경 전체를 올리는 것이 아니라, 런타임이 읽을 최소 파일만 모아 보는 습관을 들이는 편이 좋습니다.

### 2단계 — 아티팩트를 하나의 ZIP으로 묶습니다

```bash
cd package
zip -r ../function.zip .
cd ..
```

이 단계에서 처음 확인해야 할 것은 성공 여부보다 **무엇이 실제로 ZIP 안에 들어갔는가**입니다. 테스트 데이터, 캐시 파일, 로컬 노트, 대형 개발용 의존성이 함께 묶이지 않았는지를 먼저 봐야 합니다.

### 3단계 — 같은 입력으로 로컬 스모크 테스트를 돌립니다

```bash
python3 smoke_test.py
```

기대 결과는 아래와 같습니다.

```json
{
  "statusCode": 202,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"ok\": true, \"request_id\": \"req-smoke-001\", \"accepted_at\": \"2026-05-16T10:00:00+00:00\", \"order_id\": \"ord-1001\", \"item_count\": 2}"
}
```

핸들러가 이 단계에서 실패한다면 아직 배포를 논할 이유가 없습니다. 반대로 이 단계가 성공하면 이후 관리형 런타임에서의 차이는 **환경 차이**로 좁혀서 볼 수 있습니다.

### 4단계 — 패키지 크기와 포함 파일을 확인합니다

```bash
ls -lh function.zip
python3 -m zipfile -l function.zip | sed -n '1,20p'
```

예를 들어 첫 패키지 결과가 아래처럼 나올 수 있습니다.

```text
-rw-r--r--  1 user  staff    1.1M May 16 10:05 function.zip
```

```text
File Name                                             Modified             Size
app.py                                         2026-05-16 10:04:00         1034
requests/__init__.py                           2026-05-16 10:04:00         4963
requests/sessions.py                           2026-05-16 10:04:00        30373
urllib3/__init__.py                            2026-05-16 10:04:00         6979
...
```

이 확인이 중요한 이유는 메모리 튜닝보다 먼저 **패키지 비만**을 잡는 편이 더 자주 효과적이기 때문입니다. 패키지에 무엇이 들어갔는지 모르는 상태에서 메모리만 올리는 것은, 무거운 짐을 실은 채 엔진 출력만 키우는 것과 비슷합니다.

### 5단계 — 측정 후에야 메모리와 CPU를 조정합니다

많은 플랫폼은 메모리와 CPU를 함께 묶습니다. 그래서 메모리를 올리면 단순히 메모리만 늘어나는 것이 아니라 실행 시간도 줄어들 수 있습니다. 하지만 이 판단은 경험칙이 아니라 측정으로 해야 합니다.

#### 메모리 조정 의사결정 흐름

1. **의존성을 줄입니다.**
   - 사용하지 않는 라이브러리, 대형 SDK, 개발 전용 파일을 제거합니다.
2. **패키지를 다시 만들고 크기를 확인합니다.**
   - 아티팩트가 예상보다 크면 원인을 먼저 제거합니다.
3. **같은 이벤트로 로컬 패리티 테스트를 돌립니다.**
   - 입력 계약과 응답 형식이 그대로인지 확인합니다.
4. **그다음에야 메모리를 올려 실행 시간을 비교합니다.**
   - 실행 시간이 줄어 총비용이 내려갈 수도 있고, 아닐 수도 있습니다.

이 순서가 중요한 이유는 FaaS 튜닝의 첫 번째 도구가 메모리 슬라이더가 아니기 때문입니다. 가장 먼저 해야 할 일은 **불필요한 초기화와 패키지 무게를 줄이는 것**입니다.

## 로컬에서는 되는데 관리형 런타임에서 다르게 보일 때

이 문제는 매우 흔합니다. 입문자일수록 “플랫폼이 이상하다”로 결론 내리기 쉬운데, 실제로는 다음 네 항목에서 거의 대부분 설명됩니다.

### 첫 대응 흐름

1. **런타임 버전이 같은가**
   - 로컬은 Python 3.12인데 플랫폼은 3.11이면 의존성 동작이 달라질 수 있습니다.
2. **환경 변수와 시크릿이 같은가**
   - 로컬에서 기본값으로 돌아가던 설정이 관리형 런타임에서는 비어 있을 수 있습니다.
3. **패키지 안에 필요한 파일이 모두 포함되었는가**
   - `app.py`는 들어갔는데 설정 파일이나 템플릿이 빠지는 경우가 흔합니다.
4. **핸들러 경로와 진입점 이름이 정확한가**
   - 코드 자체는 멀쩡해도 `module.function` 지정이 다르면 아예 호출되지 않습니다.

이 네 가지를 먼저 확인하면, “내 코드 문제인지 런타임 문제인지”를 꽤 빠르게 분리할 수 있습니다. FaaS 디버깅에서 가장 위험한 습관은 검증 순서를 건너뛰고 곧바로 메모리나 재시도 설정을 만지는 일입니다.

## 실무에서 자주 헷갈리는 지점

### 핸들러 바깥 초기화 코드는 나쁜가요?

무조건 그렇지 않습니다. 재사용 가능한 클라이언트나 설정 로딩은 핸들러 바깥이 더 나을 수 있습니다. 다만 그 초기화 시간이 곧 콜드 스타트 비용이 되므로, 측정 없이 늘리면 안 됩니다.

### ZIP 패키지가 항상 정답인가요?

작고 단순한 함수에는 좋습니다. 반면 시스템 라이브러리 의존성이 많거나 빌드 재현성이 중요한 경우에는 컨테이너 이미지가 더 적합할 수 있습니다. 중요한 것은 방식 자체보다 **아티팩트 내용을 통제할 수 있는가**입니다.

### 메모리를 낮게 잡는 것이 늘 절약인가요?

아닙니다. 메모리를 낮춰 실행 시간이 크게 늘어나면 총비용이 오를 수 있습니다. 그래서 메모리 설정은 직감이 아니라 **같은 입력, 같은 코드, 같은 측정 기준**으로 비교해야 합니다.

## 체크리스트

- [ ] `requirements.txt`, 핸들러, 스모크 테스트가 분리되어 있는가
- [ ] 배포 전 아티팩트 크기와 포함 파일을 확인했는가
- [ ] 메모리 조정 전에 의존성 축소와 패키지 점검을 먼저 했는가
- [ ] 로컬과 관리형 런타임 차이를 추적할 첫 점검 항목을 알고 있는가

## 정리

FaaS는 함수를 올리는 기능이 아니라, **핸들러·런타임·패키지·측정 루프를 하나의 운영 계약으로 묶는 모델**입니다. 좋은 팀은 코드를 쓴 뒤 곧바로 배포하지 않습니다. 먼저 패키지를 만들고, 같은 이벤트로 로컬 검증을 하고, 아티팩트를 점검하고, 그다음에야 메모리와 성능을 조정합니다.

다음 글에서는 이 함수가 실제 운영에서 어떤 방식으로 깨워지는지, 즉 **HTTP 요청이 큐와 소비자, 멱등성, DLQ로 이어지는 트리거 흐름**을 보겠습니다.

## 심화 실전 노트: Lambda 구성, 콜드 스타트, 이벤트 소스 매핑 운영

서버리스 운영에서는 함수 코드보다 구성값이 장애를 만드는 경우가 더 많습니다. 메모리, 타임아웃, 동시성, 재시도 정책, 이벤트 소스 매핑 배치 크기 같은 설정이 처리량과 비용을 동시에 바꾸기 때문입니다. 따라서 기능 구현과 설정 검토를 분리하지 않고, 배포 단위마다 같이 점검해야 합니다.

### Lambda 구성에서 먼저 고정할 항목

아래 예시는 AWS SAM 템플릿 기준으로 자주 사용하는 안전 기본값입니다.

```yaml
Resources:
  OrdersWorker:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.12
      Handler: app.handler
      MemorySize: 1024
      Timeout: 20
      ReservedConcurrentExecutions: 30
      Environment:
        Variables:
          LOG_LEVEL: INFO
          POWERTOOLS_SERVICE_NAME: orders-worker
```

메모리를 올리면 비용만 증가한다고 오해하기 쉽지만, CPU 비율도 함께 올라가서 실행 시간이 줄어 전체 비용이 내려가는 구간이 자주 나타납니다. 그래서 메모리 값은 감으로 정하지 않고, 대표 워크로드를 기준으로 512/1024/1536MB를 비교 측정하는 방식이 필요합니다.

### 콜드 스타트 분석 포인트

콜드 스타트는 "있다/없다" 문제가 아니라 지연 분포를 어떻게 관리하느냐의 문제입니다. 운영에서는 p50보다 p95, p99 구간을 먼저 확인해야 합니다. Python 함수 기준으로는 패키지 크기, import 시점 초기화, VPC 연결 여부가 주요 변수입니다.

- 패키지 크기: 불필요한 의존성을 줄이면 초기 로드 시간이 줄어듭니다.
- 초기화 전략: DB 연결 풀 생성, 모델 로딩, 대형 설정 파싱을 모듈 로딩 시점에 몰아넣지 않습니다.
- 동시성 전략: 예측 가능한 트래픽 구간에는 Provisioned Concurrency를 제한적으로 적용합니다.

단순 평균 지연만 보면 개선 효과가 숨겨질 수 있으므로, 배포 전후의 `Init Duration` 분포와 타임아웃 비율을 같이 비교하는 습관이 중요합니다.

### 이벤트 소스 매핑(Event Source Mapping) 설계

SQS, Kinesis, DynamoDB Streams를 사용할 때는 배치 크기와 실패 재처리 정책이 핵심입니다.

```yaml
Events:
  OrdersQueue:
    Type: SQS
    Properties:
      Queue: !GetAtt OrdersQueue.Arn
      BatchSize: 10
      MaximumBatchingWindowInSeconds: 5
      FunctionResponseTypes:
        - ReportBatchItemFailures
```

`ReportBatchItemFailures`를 사용하면 배치 전체 재시도를 줄이고 실패 레코드만 다시 처리할 수 있습니다. 이 설정이 없으면 정상 처리된 메시지까지 반복 실행되어 비용과 중복 부작용이 늘어납니다. 또한 DLQ 정책을 함께 설정해 영구 실패 메시지를 격리해야 운영자가 원인을 빠르게 분석할 수 있습니다.

### 구성값과 코드의 책임 분리

서버리스에서 흔한 안티패턴은 재시도, 타임아웃, 멱등성 처리를 코드 내부 if 분기로만 해결하려는 접근입니다. 운영 가능한 구조는 다음처럼 책임을 분리합니다.

1. 인프라 설정: 동시성, 재시도, 배치, DLQ
2. 애플리케이션 코드: 멱등 키 검증, 비즈니스 규칙, 오류 분류
3. 관측 체계: 구조화 로그, 지연/오류 메트릭, 알람 임계값

이렇게 분리하면 이벤트 소스가 바뀌어도 코드 수정 범위를 줄일 수 있고, 비용 최적화 실험도 설정 레벨에서 안전하게 반복할 수 있습니다.

### 배포 전 점검 항목

배포 직전에는 함수 코드 테스트와 함께 설정 검증을 반드시 포함해야 합니다. 메모리/타임아웃 조합, 최대 동시성 제한, DLQ 연결, 이벤트 매핑 배치 정책, 콜드 스타트 완화 전략까지 체크리스트로 남기면 장애 복구 시간이 크게 단축됩니다.

## 처음 질문으로 돌아가기

- **FaaS의 실행 계약은 핸들러, 런타임, 패키지 사이에서 어떻게 만들어질까요?**
  - 본문의 기준은 함수형 서비스(FaaS)란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **실제 배포 전에는 어떤 파일 구조와 명령 순서로 검증하는 편이 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **패키지 크기와 의존성 수는 왜 실행 시간과 콜드 스타트에 직접 영향을 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- **함수형 서비스(FaaS)란 무엇인가? (현재 글)**
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

- [AWS Lambda Python 핸들러](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Lambda ZIP 배포 패키지](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)
- [Lambda 컨테이너 이미지](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Azure Functions 호스팅과 스케일](https://learn.microsoft.com/azure/azure-functions/functions-scale)

### 코드와 런타임 예제

- [AWS Lambda 개발자 가이드 예제 (GitHub)](https://github.com/awsdocs/aws-lambda-developer-guide)
- [Azure Functions Python worker samples (GitHub)](https://github.com/Azure/azure-functions-python-worker)
- [Google Cloud Run functions build and deploy guide](https://cloud.google.com/functions/docs/building)

Tags: Serverless, FaaS, Lambda, Runtime, Cloud
