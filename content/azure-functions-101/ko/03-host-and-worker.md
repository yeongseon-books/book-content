---
title: "Azure Functions 101 (3/7): Host와 Worker — 함수는 누가 실행하는가"
series: azure-functions-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Azure Functions
- Serverless
- Cloud
last_reviewed: '2026-05-15'
seo_description: 여기까지 “Functions의 구조”를 설명했습니다. 여기서 중요한 실무 포인트는, 로컬 실행과 Azure 배포가 결국
  이…
---

# Azure Functions 101 (3/7): Host와 Worker — 함수는 누가 실행하는가

앞선 두 글에서 Azure Functions의 바깥 표면을 먼저 정리했습니다. 이벤트가 함수를 깨우고, 트리거와 바인딩이 함수의 입출력 계약을 만든다는 점까지는 이제 비교적 선명합니다. 그런데 아직 중요한 질문 하나가 남아 있습니다. **여러분이 작성한 Python, Node.js, Java 함수 코드는 도대체 누가 실제로 실행하는가?**

이 질문이 중요한 이유는 Azure Functions Host 자체가 .NET으로 작성돼 있기 때문입니다. 그런데 우리는 .NET이 아닌 언어로도 함수를 아주 자연스럽게 작성하고 배포합니다. 이 둘이 어떻게 연결되는지 모르면, 로컬 실행과 Azure 배포가 무엇을 실제로 띄우는지, 장애가 났을 때 어디 로그를 봐야 하는지, 스케일아웃 시 어떤 프로세스가 늘어나는지까지 전부 흐릿하게 남습니다.

이 글은 Azure Functions 101 시리즈의 세 번째 글입니다. 여기서는 Azure Functions의 실행 모델을 **Host 프로세스와 Worker 프로세스의 분리**라는 관점에서 설명합니다. 이 구조를 이해하면 이전 글에서 다룬 트리거와 바인딩이 실제로 어떤 런타임 경로를 타는지도 자연스럽게 연결됩니다.

먼저 핵심 답부터 미리 적어 두겠습니다. **Azure Functions는 Host 프로세스와 언어별 Worker 프로세스를 분리해 띄우고, 둘은 gRPC로 대화합니다.** 이번 글의 나머지는 이 한 줄을 실무 감각이 붙는 수준까지 풀어 쓰는 과정입니다.

이제 “함수는 결국 어느 프로세스 안에서 돌고 있는가”라는 질문을 기준으로 차근차근 내려가 보겠습니다.

![Azure Functions 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/03/03-01-the-big-picture-two-processes.ko.png)
*Azure Functions 101 3장 흐름 개요*
> Host와 Worker — 함수는 누가 실행하는가의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- Functions Host와 언어 Worker는 왜 같은 프로세스가 아니라 분리된 프로세스일까요?
- Host와 Worker 사이의 gRPC 채널에서는 어떤 메시지 흐름이 오갈까요?
- 한 Worker 프로세스는 동시에 몇 개의 함수 호출을 처리할 수 있을까요?

## 왜 이 글이 중요한가

Azure Functions를 처음 배울 때는 Host와 Worker를 몰라도 로컬에서 코드를 실행하는 데 큰 어려움이 없습니다. 하지만 운영이나 성능 이슈를 마주치는 순간, 이 구조를 모르면 판단이 급격히 어려워집니다. 예를 들어 Service Bus 연결 문제는 Host 쪽 로그에서 먼저 드러나고, Python 코드의 무한 루프나 import 오류는 Worker 쪽에서 먼저 보일 수 있습니다. 같은 “함수가 안 돈다”는 현상도 원인 층이 완전히 다를 수 있습니다.

또한 이 경계는 스케일링과도 직접 연결됩니다. Function App이 스케일아웃되면 단순히 “함수가 더 많이 돈다”가 아니라, **각 인스턴스마다 Host와 Worker가 다시 구성되는 구조**가 됩니다. 이 사실을 모르고 전역 메모리 캐시나 연결 재사용 전략을 짜면, 같은 코드가 인스턴스 수에 따라 전혀 다른 행동을 보일 수 있습니다.

무엇보다 이 글은 배포 장의 해석에 필요한 기반입니다. `func start`나 Azure 배포가 실제로 무엇을 띄우고 어떤 프로토콜로 함수를 호출하는지 이해하면, CLI 명령이 단순한 절차가 아니라 런타임 구조를 다루는 작업으로 보이기 시작합니다. 그 감각이 있어야 뒤의 플랜, 스케일링, 모니터링 이야기도 단단하게 연결됩니다.

## 핵심 관점

Azure Functions의 핵심 실행 모델은 단순합니다. **Host는 함수를 언제 실행할지, 어떤 입력을 줄지, 어떤 바인딩을 적용할지를 책임지고, Worker는 실제 사용자 함수를 해당 언어 런타임에서 실행합니다.** 즉 Host는 오케스트레이션과 플랫폼 책임을 맡고, Worker는 코드 실행 책임을 맡습니다.

이 분리는 여러 언어를 지원하기 위한 실용적인 선택입니다. Host가 직접 V8, CPython, JVM을 모두 품고 실행하려 들면 충돌 가능성이 커지고 구조가 복잡해집니다. 반대로 언어별 Worker를 표준 런타임 그대로 띄우면 Host는 언어 중립적인 호출 프로토콜만 유지하면 되고, 각 언어는 자기 런타임에 맞는 Worker만 구현하면 됩니다.

운영 관점에서도 이 분리는 큰 장점이 있습니다. Host와 Worker를 다른 층으로 볼 수 있으면 “문제가 트리거 감지에 있는가, 언어 런타임에 있는가, 함수 코드 자체에 있는가”를 더 빨리 나눌 수 있습니다. 결국 Functions의 실행 모델은 단일 프로세스가 아니라, **역할이 분리된 두 프로세스의 협업**으로 보는 편이 가장 정확합니다.

> Azure Functions에서 Host는 함수를 직접 실행하는 존재가 아니라, 함수를 실행하게 만드는 플랫폼 런타임입니다. 실제 사용자 코드는 언어별 Worker에서 실행됩니다.

## 핵심 개념

### 가장 큰 그림은 두 개의 프로세스입니다

전통적인 웹 프레임워크는 한 프로세스 안에서 코드 로딩, HTTP 처리, DB 호출, 응답 생성을 모두 처리하는 경우가 많습니다. Azure Functions는 다릅니다. 함수 실행에는 최소 두 개의 프로세스가 관여합니다.

- **Host 프로세스** — .NET으로 작성된 런타임입니다. 트리거 감지, 스케일 신호, 로깅, 바인딩 해석을 담당합니다.
- **Worker 프로세스** — 여러분의 언어(Node.js, Python, Java 등)로 실행되는 별도 프로세스입니다. 실제 함수 코드는 여기서 돌아갑니다.

이 그림이 중요한 이유는 Functions의 거의 모든 운영 질문이 여기로 다시 돌아오기 때문입니다. 함수가 안 뜨는가, 트리거가 안 먹는가, 로그가 어디에 남는가, 스케일 시 무엇이 늘어나는가 같은 질문이 모두 이 구조 위에 서 있습니다.

실제로 많은 장애 분석이 이 한 장의 그림으로 빨라집니다. 트리거는 감지되는데 함수 코드가 안 돌아가는지, 아니면 애초에 트리거 감지 자체가 실패하는지 나눌 수 있기 때문입니다. 전자는 Worker나 사용자 코드에 더 가깝고, 후자는 Host나 트리거 인프라에 더 가깝습니다.

### 왜 분리했는가: 여러 언어 런타임을 한 플랫폼에 붙이는 가장 현실적인 방법

Host와 Worker가 같은 프로세스에 있었다면 Host는 V8, CPython, JVM 같은 런타임을 직접 품어야 했을 것입니다. 현실적으로 유지하기 어렵고 충돌 여지도 큽니다. 언어마다 메모리 모델과 GC와 의존성 체계가 다르기 때문입니다.

분리된 구조에서는 역할이 단순해집니다.

- Host는 **실행 시점, 입력, 출력 계약**을 책임집니다.
- Worker는 **자기 언어의 표준 런타임에서 함수 코드 실행**을 책임집니다.
- 둘은 **gRPC + Protobuf** 같은 언어 중립 프로토콜로만 대화합니다.

이 덕분에 새 언어를 지원하는 문제도 “Host를 갈아엎는다”가 아니라 “그 언어용 Worker를 만들고 프로토콜을 맞춘다”는 문제로 바뀝니다. 실제 Host 쪽 구현은 [`azure-functions-host`](https://github.com/Azure/azure-functions-host)에 있고, 언어별 실행 파일과 인수는 각 worker 레포의 `worker.config.json`에서 확인할 수 있습니다.

이 설계는 운영 안정성에도 이점이 있습니다. 언어별 런타임 문제가 전체 Host 안정성을 항상 함께 무너뜨리지 않도록 경계를 만들 수 있기 때문입니다. 즉 다중 언어 지원을 위한 구조이면서 동시에 장애 격리와 진단에도 도움이 되는 구조라고 볼 수 있습니다.

### .NET은 예외가 있습니다

여기서 한 가지 예외도 알아둘 만합니다. **.NET in-process 모델은 Host와 같은 프로세스에서 실행되는 역사적 예외**입니다. 다만 신규 프로젝트 관점에서는 isolated worker 모델을 기본값으로 이해하는 편이 안전합니다. 이 글의 멘탈 모델도 그 기준을 중심으로 잡으면 대부분의 언어와 현재 권장 방향을 함께 설명할 수 있습니다.

이 예외를 굳이 언급하는 이유는 문서나 예제를 읽다가 “왜 어떤 설명은 Host 안에서 직접 실행된다고 하고, 어떤 설명은 Worker 분리를 말하지?”라는 혼란을 줄이기 위해서입니다. 입문 단계에서는 비-.NET 언어를 중심으로 Host/Worker 분리 모델을 먼저 익히고, .NET은 역사적·플랫폼적 예외가 있다는 정도로 이해해도 충분합니다.

### 한 인스턴스 안에서 실제로 무슨 일이 벌어질까요

Function App 인스턴스 하나가 호출을 처리하는 순서는 대략 다음과 같습니다.

![한 인스턴스 안의 호출 처리 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/03/03-02-what-happens-inside-a-single-instance.ko.png)

*한 인스턴스 안의 호출 처리 흐름*

이 흐름에서 꼭 기억해야 할 포인트는 두 가지입니다.

1. **Host는 함수 코드를 직접 호출하지 않습니다.** Host는 Worker에게 gRPC 요청을 보내 “이 입력으로 이 함수를 실행해 달라”고 전달합니다.
2. **Worker는 트리거 이벤트를 직접 받지 않습니다.** 트리거는 Host가 감지하고, 입력을 정리해 Worker에 넘깁니다.

이 분리는 운영에서도 유용합니다. 예를 들어 Python 코드가 무한 루프에 빠져 Worker가 응답하지 않으면 Host는 Worker만 재시작할 수 있습니다. 반대로 Service Bus 연결이나 바인딩 해석 문제가 생기면 Host 쪽 로그가 먼저 단서를 줄 가능성이 큽니다.

여기서 중요한 운영 습관 하나가 나옵니다. 함수가 실패했다고 해서 무조건 애플리케이션 로그부터 보는 것이 아니라, **실패가 트리거 감지 전인지 후인지**를 먼저 구분하는 것입니다. 그 질문 하나로 로그 탐색 범위가 크게 줄어듭니다.

### Function App, Host, Worker는 서로 다른 층입니다

세 단어가 비슷해서 헷갈리기 쉽지만, 층이 다릅니다.

| 단어 | 무엇 | 단위 |
|---|---|---|
| **Function App** | 배포·과금·스케일링의 단위 | 사용자가 Azure에서 보는 리소스 |
| **Host** | Function App 인스턴스에서 돌아가는 .NET 런타임 | 인스턴스당 1개 |
| **Worker** | Host가 띄운 언어 런타임 프로세스 | 인스턴스당 1개 이상 (`FUNCTIONS_WORKER_PROCESS_COUNT`로 조정 가능) |

![Function App과 Host, Worker의 위계 관계](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/03/03-03-function-app-host-worker-the-hierarchy-o.ko.png)

*Function App과 Host, Worker의 위계 관계*

이 위계는 스케일아웃을 이해할 때 특히 중요합니다. Function App 인스턴스가 늘어나면 각 인스턴스는 자기 Host와 Worker를 따로 가집니다. **인스턴스 간 메모리는 공유되지 않습니다.** 따라서 모듈 전역 캐시나 프로세스 로컬 상태는 같은 인스턴스 안에서만 의미가 있습니다.

이 말은 곧, 로컬 테스트에서 잘 보이던 캐시 효과가 프로덕션 scale out 상황에서는 희미해질 수 있다는 뜻이기도 합니다. 그래서 Functions에서 캐시 전략을 말할 때는 항상 “프로세스 로컬 최적화”와 “여러 인스턴스 간 공유 상태”를 따로 생각해야 합니다.

### 한 인스턴스에서 동시에 몇 개를 처리할 수 있을까요

“Worker가 하나면 호출도 하나씩 순차 처리되나요?”라는 질문이 자주 나옵니다. Python에서는 그렇게 단순하지 않습니다.

**동기 `def` 함수는 Python worker 내부의 thread pool에서 실행**될 수 있으므로, worker 하나가 여러 동기 호출을 겹쳐 처리할 수 있습니다. **비동기 `async def` 함수는 단일 asyncio event loop를 공유**하므로 I/O에는 유리하지만 CPU-바운드 작업에서는 또 다른 병목이 생길 수 있습니다.

따라서 Python Functions의 동시성은 “단일 이벤트 루프 한 줄 설명”으로 끝나지 않습니다. GIL 아래의 단일 Python 프로세스라는 특성과, thread pool과 async scheduling의 조합을 함께 이해해야 합니다. 여기에 `FUNCTIONS_WORKER_PROCESS_COUNT`를 높이면 한 인스턴스 안에 Worker 프로세스를 여러 개 띄워 동시성을 더 넓힐 수 있습니다.

운영에서 특히 알아둘 점은 **Flex Consumption의 Python HTTP 기본 동시성이 인스턴스당 1일 수 있다**는 점입니다. 즉 스케일 행동은 단순히 인스턴스 수만이 아니라, 인스턴스 내부 동시성 설정과도 같이 읽어야 합니다.

이 지점 때문에 같은 Python 함수라도 어떤 팀은 scale out이 빨리 일어난다고 느끼고, 어떤 팀은 인스턴스 하나가 예상보다 오래 버틴다고 느낄 수 있습니다. 결국 관측해야 할 대상은 인스턴스 수만이 아니라, 요청이 인스턴스 내부에서 어떻게 겹치고 있는가까지 포함됩니다.

### 이 구조는 실제 코드로 검증할 수 있습니다

이 설명은 추상적인 개념도가 아닙니다. Functions Host는 [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host)에 공개되어 있고, Host와 Worker 사이의 메시지 계약은 [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf)에 정의되어 있습니다.

즉 이 글의 핵심 주장들은 모두 코드로 따라갈 수 있습니다. Host가 Worker 프로세스를 어떻게 띄우는지, gRPC 핸드셰이크가 어떤지, 트리거가 발화했을 때 Dispatcher가 어떤 요청을 만드는지, Placeholder 모드가 어떻게 콜드 스타트를 줄이는지까지 실제 구현을 통해 확인할 수 있습니다. 더 깊이 보고 싶다면 이후 심화 시리즈가 그 길을 이어 줍니다.

### host.json도 이 실행 경계의 일부입니다

아래와 같은 `host.json` 설정은 바로 이 Host 런타임의 동작을 조정합니다.

```json
{
  "version": "2.0",
  "functionTimeout": "00:05:00",
  "extensions": {
    "http": { "maxConcurrentRequests": 100 }
  }
}
```

이 파일은 단순한 설정 파일이 아니라, Host가 얼마나 오래 실행을 허용할지, HTTP 확장에서 동시 요청을 어떻게 다룰지 같은 런타임 계약을 담고 있습니다. 따라서 인프라 설정과 코드 사이의 중간층으로 이해하는 편이 좋습니다.

또한 `host.json`은 개발 편의 설정이 아니라 운영 행동을 바꾸는 파일이라는 점도 중요합니다. 여기의 값이 달라지면 timeout, concurrency, 확장 동작이 달라질 수 있으므로, 코드 저장소 안에 있다고 해서 가볍게 다루면 안 됩니다. IaC나 배포 검토 절차 안에서 함께 관리하는 편이 안전합니다.

### 로컬 실행과 Azure 실행을 같은 구조로 보는 감각이 중요합니다

`func start`로 로컬에서 함수를 실행할 때도 결국은 이 Host/Worker 구조가 축소판으로 올라옵니다. 즉 로컬 실행은 별도의 개발용 장난감이 아니라, 실제 프로덕션 구조와 같은 개념 모델을 따라가는 환경입니다.

이 감각이 있으면 배포 장에서 CLI 명령을 외울 때도 덜 피상적으로 접근하게 됩니다. 단순히 명령이 성공했다가 아니라, 지금 Azure 쪽에 올리는 것이 Host가 이해할 메타데이터와 Worker가 실행할 코드의 묶음으로 보이기 시작하기 때문입니다.

### 로그를 읽을 때도 이 경계가 바로 적용됩니다

운영 현장에서 가장 체감이 큰 장점은 로그 해석입니다. 예를 들어 함수 인덱싱 실패, 바인딩 확장 로드 실패, 트리거 연결 실패 같은 문제는 Host 쪽 단서가 먼저 보일 가능성이 큽니다. 반대로 import 오류, 애플리케이션 예외, Python 코드의 동시성 문제는 Worker나 애플리케이션 로그에서 먼저 드러날 수 있습니다.

이 차이를 모르면 모든 문제를 한 로그 스트림에서만 찾으려다 시간을 많이 씁니다. 반대로 Host와 Worker를 분리해 보면 “이 문제는 호출이 전달되기 전인가 후인가”를 먼저 물을 수 있고, 그 질문만으로도 탐색 범위가 절반 가까이 줄어듭니다.

### 스케일아웃 시 복제되는 것은 코드만이 아닙니다

Function App이 스케일아웃된다는 말은 단순히 같은 코드 복사본이 하나 더 생긴다는 말이 아닙니다. 각 인스턴스마다 Host와 Worker 조합이 다시 떠서, 트리거와 바인딩과 프로세스 로컬 상태를 저마다 따로 가집니다.

### 로컬에서 Host와 Worker 분리를 직접 확인할 수 있습니다

개념도만 보면 두 프로세스 분리가 추상적으로 느껴질 수 있습니다. 하지만 `func start`를 켠 뒤에는 로컬에서도 이 구조를 바로 확인할 수 있습니다. 아래 명령은 “정말 Host와 Worker가 따로 뜨는가?”를 빠르게 검증할 때 쓸 만한 최소 확인 절차입니다.

```bash
# 터미널 1
func start --verbose

# 터미널 2
ps -ef | grep -E "func|python.*worker" | grep -v grep
```

```text
...
Worker process started and initialized.
Functions:
    hello: [GET,POST] http://localhost:7071/api/hello
...
python ... azure_functions_worker ...
```

위 출력에서 중요한 것은 두 줄입니다. `Worker process started and initialized.`는 Host가 언어 Worker를 띄웠다는 뜻이고, `azure_functions_worker` 프로세스는 실제 사용자 코드가 별도 프로세스에서 돈다는 증거입니다. 배포 전에도 로컬에서 이 정도 확인만 해 두면, 뒤에서 로그를 읽거나 동시성을 논의할 때 추상도가 훨씬 내려갑니다.

그래서 어떤 팀이 로컬 테스트에서는 문제를 못 보다가 프로덕션 다중 인스턴스에서만 이상한 캐시 동작이나 연결 수 급증을 경험하는 일이 생깁니다. 프로세스 로컬 최적화는 인스턴스 수가 늘어나는 순간 다른 문제로 보일 수 있기 때문입니다. 이 주제는 뒤의 스케일링 장에서 다시 이어집니다.

### 운영 질문을 바꿔 주는 장이라는 점이 중요합니다

이 글의 목적은 Host와 Worker 구현 세부를 외우는 데 있지 않습니다. 더 중요한 목적은 문제를 묻는 방식을 바꾸는 데 있습니다. “왜 함수가 실패했지?” 대신 “실패가 Host 쪽인가, Worker 쪽인가?”, “트리거 감지 전인가, 호출 후인가?”, “프로세스 로컬 상태가 관여했는가?”처럼 더 좋은 질문을 하게 만드는 것이 핵심입니다.

좋은 질문이 생기면 뒤의 배포, 스케일링, 모니터링이 훨씬 읽기 쉬워집니다. Azure Functions는 추상화가 강한 플랫폼이지만, Host/Worker 경계만 잡히면 그 추상화가 오히려 문제를 분해하기 쉬운 형태로 보이기 시작합니다.

## 흔히 헷갈리는 지점

- **Host가 사용자 함수를 직접 실행한다고 생각하기 쉽지만, 비-.NET 언어에서는 실제 코드는 Worker에서 실행됩니다.**
- **Worker가 곧 트리거를 직접 받는다고 보면 안 됩니다.** 트리거 감지와 바인딩 해석은 Host가 담당합니다.
- **Function App, Host, Worker는 같은 말이 아닙니다.** 배포 단위와 런타임 프로세스 단위를 분리해서 봐야 합니다.
- **전역 캐시가 있으면 모든 인스턴스에서 공유될 것이라고 기대하면 안 됩니다.** 프로세스 로컬 상태일 뿐입니다.
- **동시성은 인스턴스 수만으로 설명되지 않습니다.** Worker 프로세스 수, HTTP 동시성, 언어 런타임 특성이 함께 작동합니다.

이 오해들이 반복되는 이유는 Functions가 애플리케이션과 런타임을 잘 분리해 주기 때문입니다. 겉으로는 함수 코드만 보이니, 그 뒤에서 Host가 무슨 일을 하고 Worker가 어디서 실행되는지 잊기 쉽습니다. 하지만 운영 문제는 거의 항상 그 숨겨진 경계 위에서 발생합니다. 그래서 Host/Worker 모델은 입문용 세부사항이 아니라 실전용 기본 지식에 가깝습니다.

## 운영 체크리스트

- [ ] 사용하는 언어가 in-process인지 out-of-process인지 확인했습니다.
- [ ] Host 로그와 Worker 로그를 분리해서 볼 수 있는 관측 경로를 만들었습니다.
- [ ] `maxConcurrentRequests` 같은 동시성 설정을 워크로드 기준으로 검토했습니다.
- [ ] Worker 충돌이나 응답 불능 상황에서 자동 복구 동작을 테스트했습니다.
- [ ] `host.json`의 주요 설정을 IaC나 배포 파이프라인으로 관리합니다.

## 정리

이번 글의 핵심은 Azure Functions를 단일 런타임으로 보지 않는 것입니다. **Host는 플랫폼 실행을 담당하고, Worker는 실제 언어 코드를 실행합니다.** 이 분리를 이해하면 트리거와 바인딩이 어느 층에서 해석되는지, 로그를 어디서 봐야 하는지, 스케일아웃 시 무엇이 복제되는지까지 훨씬 선명하게 읽을 수 있습니다.

또한 Function App, Host, Worker의 위계를 구분하면 프로세스 로컬 상태와 인스턴스 스케일의 관계가 명확해집니다. 이것은 단순한 구조 설명이 아니라, 연결 재사용, 캐시 전략, 동시성 튜닝, 장애 분석의 출발점입니다. 특히 Python처럼 런타임 특성이 동시성과 직결되는 언어에서는 더욱 그렇습니다.

다음 글에서는 이 구조를 실제 배포 흐름으로 연결합니다. 즉 로컬에서 만든 함수를 Azure에 올릴 때, 지금까지 본 Host/Worker 모델이 어떤 식으로 현실의 Function App 리소스로 바뀌는지 봅니다.

결국 Host와 Worker를 이해한다는 것은 Azure Functions를 함수 코드 저장소가 아니라 플랫폼 런타임과 언어 런타임이 협업하는 구조로 본다는 뜻입니다. 이 관점이 잡히면 뒤의 배포와 운영 주제도 훨씬 덜 추상적으로 읽힙니다.

## 처음 질문으로 돌아가기

- **Functions Host와 언어 Worker는 왜 같은 프로세스가 아니라 분리된 프로세스일까요?**
  - Host가 `CPython`, `V8`, `JVM`을 한 프로세스 안에 직접 품는 대신, Azure Functions는 Host와 언어 Worker를 분리해 언어별 런타임 충돌을 줄입니다. 그래서 Host는 트리거와 바인딩, 스케일 신호를 맡고 실제 사용자 코드는 `azure_functions_worker` 같은 별도 프로세스에서 실행됩니다.
- **Host와 Worker 사이의 gRPC 채널에서는 어떤 메시지 흐름이 오갈까요?**
  - Host는 트리거를 감지한 뒤 함수 이름, 입력 페이로드, 바인딩 해석 결과를 gRPC로 Worker에 넘깁니다. Worker는 그 호출을 실행한 뒤 반환값과 예외, 로그 신호를 다시 Host로 돌려주므로, `func start --verbose`에서 보이는 초기화 메시지와 실제 함수 호출은 이 채널 위에서 이어집니다.
- **한 Worker 프로세스는 동시에 몇 개의 함수 호출을 처리할 수 있을까요?**
  - Python Worker는 단순히 “항상 한 번에 하나”로 끝나지 않습니다. 동기 `def`는 thread pool에서 겹칠 수 있고, `async def`는 하나의 event loop를 공유하며, 필요하면 `FUNCTIONS_WORKER_PROCESS_COUNT`와 `host.json`의 `maxConcurrentRequests` 같은 설정으로 인스턴스 내부 동시성을 더 조절할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions 101 (1/7): Azure Functions란? — 이벤트가 함수를 호출하는 세상](./01-what-is-azure-functions.md)
- [Azure Functions 101 (2/7): 트리거와 바인딩 — 함수 입출력의 모든 것](./02-triggers-and-bindings.md)
- **Azure Functions 101 (3/7): Host와 Worker — 함수는 누가 실행하는가 (현재 글)**
- Azure Functions 101 (4/7): 함수 하나 배포하기 — 로컬에서 Azure까지 (예정)
- Azure Functions 101 (5/7): 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated (예정)
- Azure Functions 101 (6/7): 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 (예정)
- Azure Functions 101 (7/7): 모니터링과 운영 기초 (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Azure Functions runtime versions overview](https://learn.microsoft.com/en-us/azure/azure-functions/functions-versions)
- [Use multiple worker processes (`FUNCTIONS_WORKER_PROCESS_COUNT`)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [.NET isolated worker model](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)

### 소스 코드

- [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host) — Host 본체
- [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf) — Host/Worker 메시지 계약
- [`Azure/azure-functions-nodejs-worker`](https://github.com/Azure/azure-functions-nodejs-worker)
- [`Azure/azure-functions-python-worker`](https://github.com/Azure/azure-functions-python-worker)
- [`Azure/azure-functions-java-worker`](https://github.com/Azure/azure-functions-java-worker)

### 관련 시리즈

- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/) — Host/Worker 분리를 코드 레벨에서 따라가는 심화 시리즈

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-101/ko/03-host-and-worker)

Tags: Azure, Azure Functions, Serverless, Cloud
