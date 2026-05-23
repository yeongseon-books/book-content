---
title: "Azure Functions 101 (6/7): 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간"
series: azure-functions-101
episode: 6
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
seo_description: 서버리스 설명에는 늘 “자동으로 스케일링된다”는 문장이 붙습니다. 맞는 말이지만, 운영에서는 그 한 줄만으로 충분하지
  않습니다.
---

# Azure Functions 101 (6/7): 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간

서버리스 설명에는 늘 “자동으로 스케일링된다”는 문장이 붙습니다. 틀린 말은 아닙니다. 하지만 운영에서는 이 한 문장으로는 거의 아무것도 설명되지 않습니다. 어떤 신호를 보고 인스턴스를 늘리는지, 한 인스턴스가 동시에 몇 개의 호출을 흡수하는지, idle 상태에서 다시 깨어나는 첫 요청은 왜 느릴 수 있는지를 같이 봐야 비로소 현실의 성능과 비용이 읽힙니다.

특히 Azure Functions에서는 앞 글의 플랜 선택과 이 주제가 강하게 연결됩니다. Consumption, Flex Consumption, Premium, Dedicated는 모두 “자동 확장”이라는 표현 아래 묶이지만, 실제로는 warm capacity를 어떻게 유지하는지, scale to zero가 가능한지, concurrency를 어디까지 제어할 수 있는지가 다릅니다. 즉 같은 트래픽 스파이크라도 플랜별 체감은 꽤 다를 수 있습니다.

이 글은 Azure Functions 101 시리즈의 여섯 번째 글입니다. 여기서는 스케일링과 콜드 스타트를 **운영 현상**으로 읽는 기준을 정리합니다. 인스턴스 수와 인스턴스 내부 동시성, cold start가 구성되는 단계, downstream 병목, 비용과 스케일 한도의 관계를 함께 보겠습니다.

이번 장의 목표는 콜드 스타트를 무조건 없애는 비법을 찾는 것이 아닙니다. 더 현실적인 목표는 **어디서 시간이 쓰이는지, 어떤 레버를 먼저 움직여야 하는지, 어떤 비용을 감수해야 하는지**를 판단할 수 있게 만드는 것입니다.

이제 “자동으로 늘어난다”는 말 속에 숨어 있는 두 축과, 첫 요청이 느려지는 실제 이유를 차례로 풀어보겠습니다.

![Azure Functions 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/06/06-01-scaling-has-two-axes-instance-count-and.ko.png)
*Azure Functions 101 6장 흐름 개요*
> 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- Functions scale controller는 어떤 신호를 보고 인스턴스를 추가할까요?
- 콜드 스타트는 정확히 어느 단계에서 발생하고, 무엇을 측정해야 볼 수 있을까요?
- Premium의 Always Ready나 Flex의 always-ready 인스턴스는 콜드 스타트를 어디까지 줄여 줄까요?

## 왜 이 글이 중요한가

스케일링과 콜드 스타트는 Azure Functions에서 가장 많이 회자되지만, 동시에 가장 자주 단순화되는 주제입니다. 많은 팀이 “첫 요청이 느리다 = 플랜이 나쁘다”로 곧장 결론을 내립니다. 하지만 실제로는 새 인스턴스 준비, Host 부팅, Worker 시작, import와 초기화, 첫 요청 자체의 무거움이 모두 섞여 있습니다. 원인을 쪼개 보지 않으면 해결책도 자주 틀립니다.

또한 자동 스케일은 신뢰성과 비용을 동시에 흔듭니다. 인스턴스 수가 늘어나면 처리량은 좋아질 수 있지만, 동시에 DB 연결 수와 외부 API 호출 수도 폭증할 수 있습니다. 반대로 concurrency를 너무 보수적으로 잡으면 인스턴스가 지나치게 빨리 늘어 비용이 튀고, 너무 공격적으로 잡으면 한 인스턴스가 과부하되어 지연이 치솟을 수 있습니다. 즉 스케일링은 성능 기능이면서 비용 제어 기능이기도 합니다.

무엇보다 모니터링 장으로 넘어가기 전에 이 글이 필요합니다. 관측이란 결국 무엇을 볼지 아는 문제인데, cold start와 scale out이 어떤 현상으로 나타나는지 모르면 메트릭과 로그를 봐도 읽히지 않습니다. 이 장은 뒤의 Application Insights, InstanceCount, 알람 설정을 이해하기 위한 동작 모델을 먼저 만들어 줍니다.

## 핵심 관점

Azure Functions의 스케일링은 한 단어가 아닙니다. **수평 스케일링(scale out)** 과 **인스턴스 내부 동시성(in-instance concurrency)** 이라는 두 축을 함께 봐야 합니다. 인스턴스 수가 늘어나는 것만이 스케일이 아니고, 한 인스턴스가 동시에 몇 개 호출을 처리하도록 설정되어 있는지도 같은 정도로 중요합니다.

예를 들어 같은 HTTP 부하라도 어떤 경우에는 인스턴스를 빨리 늘리는 편이 낫고, 어떤 경우에는 인스턴스당 동시성을 먼저 높여도 충분합니다. Python처럼 런타임 특성이 뚜렷한 언어에서는 thread pool, async 처리 방식, HTTP concurrency 설정이 scale out보다 먼저 병목을 만들기도 합니다. 결국 “몇 대가 있나”와 “한 대가 얼마나 세게 일하나”를 동시에 봐야 합니다.

이 관점은 콜드 스타트 해석에도 그대로 이어집니다. 인스턴스 수를 0까지 줄이는 플랜에서는 다음 호출이 새 인스턴스를 깨워야 할 수 있고, warm capacity가 있는 플랜은 그 경로를 줄일 수 있습니다. 따라서 스케일링과 콜드 스타트는 별개가 아니라, **같은 실행 수명주기를 다른 각도에서 보는 주제**라고 이해하는 편이 가장 실용적입니다.

> Azure Functions의 스케일링을 제대로 이해하려면 “얼마나 많이 늘어나는가”보다 먼저 “언제 새 인스턴스가 필요해지고, 그 전에 한 인스턴스를 어디까지 쓰는가”를 봐야 합니다.

## 핵심 개념

### 스케일링은 두 축입니다

- **수평 스케일링(scale out)** — 앱에 몇 개 인스턴스를 둘 것인가
- **인스턴스 내부 동시성(in-instance concurrency)** — 인스턴스 하나가 동시에 몇 개 호출을 처리할 것인가

플랜별 차이는 이 두 축을 누가, 어떤 방식으로 제어하는지에서 갈립니다.

| 플랜 | 스케일아웃 방식 | 플랜에서 특히 봐야 할 점 |
|---|---|---|
| Consumption | 플랫폼 자동 확장 | 인스턴스 수는 추상화되어 있고, 동시성은 런타임·트리거 설정에 크게 영향 받음 |
| Flex Consumption | 플랫폼 자동 확장 + 함수별 scale group | 함수 단위 격리와 인스턴스당 HTTP 동시성 제어가 핵심 |
| Premium | 플랫폼 자동 확장 + warm capacity | Always Ready와 prewarmed 인스턴스로 첫 요청 지연 완화 |
| Dedicated | App Service autoscale 규칙 또는 수동 운영 | scale to zero는 없고, 반응 속도는 규칙 설계에 좌우됨 |

Flex가 특별한 이유는 target-based scaling 개념 자체보다, **per-function scale group과 HTTP concurrency 제어**를 더 적극적으로 다룰 수 있기 때문입니다.

이 차이는 동일한 Function App 안에 성격이 다른 함수가 섞여 있을 때 특히 드러납니다. 어떤 함수는 HTTP burst에 민감하고, 어떤 함수는 큐 backlog에 민감할 수 있습니다. Flex의 장점은 이 차이를 완전히 무시하지 않고 더 세밀하게 다룰 여지를 준다는 사실입니다.

### 트래픽 급증에 대한 플랜별 반응은 다릅니다

같은 상황을 놓고 보면 차이가 더 분명합니다. 평소에는 idle 상태이고, t=0에 HTTP 요청이 갑자기 몰린다고 가정해 보겠습니다.

![트래픽 급증 시 플랜별 확장 반응](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/06/06-02-how-the-plans-react-to-a-traffic-spike.ko.png)

*트래픽 급증 시 플랜별 확장 반응*

- **Consumption**: scale to zero가 일반적이므로 첫 요청에서 cold start가 가장 쉽게 드러납니다.
- **Flex Consumption**: Always Ready를 0으로 두면 여전히 cold start가 가능합니다. 대신 함수별 스케일과 concurrency 제어가 강점입니다.
- **Premium**: warm 인스턴스를 유지하므로 첫 요청 지연을 더 강하게 누를 수 있습니다.
- **Dedicated**: scale to zero는 없지만, 갑작스러운 부하 대응은 autoscale 규칙 품질에 달려 있습니다.

여기서 자주 나오는 오해는 “Flex면 항상 따뜻하다”는 생각입니다. 아닙니다. **Always Ready가 0이면 Flex도 0으로 내려갈 수 있고, 다음 호출은 cold start를 겪을 수 있습니다.**

반대로 Premium도 “무조건 cold start가 없다”로 단정하면 안 됩니다. warm baseline이 있더라도 모든 상황에서 완전히 같은 지연 특성을 보장하는 것은 아닙니다. 중요한 것은 플랜 이름이 아니라, 실제로 얼마의 warm capacity를 유지하고 어떤 스파이크를 상정하느냐입니다.

### 콜드 스타트는 하나의 시간이 아니라 여러 단계의 합입니다

콜드 스타트를 정확히 정의하면 다음과 같습니다.

> **콜드 스타트 = 새 인스턴스가 할당되고, Host와 Worker가 올라오고, 함수가 준비된 뒤 첫 호출을 처리하기까지 걸리는 전체 시간**

실제로는 다음과 같은 단계로 쪼개어 볼 수 있습니다.

![콜드 스타트를 이루는 준비 단계](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/06/06-03-what-a-cold-start-actually-includes.ko.png)

*콜드 스타트를 이루는 준비 단계*

| 단계 | 시간이 늘어나는 주된 이유 | 줄이는 방법 |
|---|---|---|
| 1 | 새 실행 환경을 준비해야 함 | warm capacity, Always Ready, 플랫폼 최적화 |
| 2 | Host 초기화 | 사용자가 직접 줄일 여지는 제한적 |
| 3 | 언어 Worker 시작 비용 | 런타임 선택, 초기화 비용 점검 |
| 4 | 의존성 import, 애플리케이션 초기화 | lazy import, lazy init, 의존성 정리 |
| 5 | 첫 호출 자체의 무거움 | 캐시 예열, warmup trigger, 더 가벼운 첫 요청 |

실무에서는 4단계가 예상보다 크게 작동하는 경우가 많습니다. 큰 SDK import, 전역 초기화, 모델 로드, 첫 연결 생성이 누적되면 플랜을 바꾸기 전에 이미 애플리케이션이 cold start를 키우고 있는 셈입니다.

그래서 cold start 대응을 플랜 논의로만 시작하면 종종 빗나갑니다. 애플리케이션의 import graph와 초기화 경로를 먼저 읽어 보면, 운영자가 비용을 더 쓰지 않고도 꽤 많은 시간을 줄일 수 있는 경우가 적지 않습니다.

### 플랫폼도 미리 해 주는 일이 있습니다

Azure Functions가 콜드 스타트를 전부 애플리케이션에게 떠넘기는 것은 아닙니다. 플랫폼은 placeholder 모델과 warm capacity 개념을 통해 **인스턴스와 Host 준비 비용 일부를 앞당겨** 놓으려 합니다. Premium의 prewarmed/Always Ready 인스턴스, Flex의 always-ready 인스턴스 수 설정이 바로 그 레버입니다.

하지만 경계도 분명합니다. 플랫폼이 줄여 줄 수 있는 것은 “실행 환경이 존재하고 Host가 기본적으로 준비될 때까지”에 가깝습니다. 여러분의 import 비용, 느린 초기화 코드, 첫 요청에서 열리는 DB 연결, 외부 서비스 응답 지연은 여전히 애플리케이션 책임입니다.

### cold start가 아플 때 무엇부터 바꿀까요

#### 1) 플랜 관점

- 첫 요청 지연이 비즈니스 문제라면 **Premium** 또는 **Flex Consumption + Always Ready**를 먼저 검토합니다.
- 간헐적 지연을 허용할 수 있다면 Consumption이나 기본 Flex 구성도 충분할 수 있습니다.

#### 2) 코드 관점

- **의존성 줄이기** — 큰 패키지를 불필요하게 가져오지 않습니다.
- **초기화 시점 늦추기** — import 시점에 DB 연결, 파일 로드, 메타데이터 다운로드를 하지 않습니다.
- **프로세스 로컬 캐시 재사용** — 같은 Worker 안에서 안전하게 재사용 가능한 클라이언트는 모듈 전역에 둡니다.

아래 코드는 lazy initialization의 개념만 보여 주는 예시입니다.

```python
import azure.functions as func

app = func.FunctionApp()
_client = None

def get_client():
    global _client
    if _client is None:
        _client = create_cosmos_client()
    return _client

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    client = get_client()
    return func.HttpResponse("ok")
```

무거운 초기화 비용을 호출마다 내지 않고, Worker 수명주기 동안 한 번만 내도록 구조를 바꿔야 합니다.

#### 3) 운영 관점

- **Warmup trigger** — classic Consumption을 제외한 플랜에서 새 인스턴스가 추가될 때 예열 작업을 넣을 수 있습니다.
- **Always Ready 인스턴스** — Flex와 Premium에서 warm baseline을 유지합니다. 0이면 scale to zero가 가능하고, 1 이상이면 첫 요청 지연을 줄일 수 있습니다.

Warmup trigger와 Always Ready는 같은 기능이 아닙니다. Warmup trigger는 새 인스턴스가 올라올 때 실행되는 훅이고, Always Ready는 아예 warm 인스턴스를 유지하는 설정입니다.

둘을 함께 쓰는 경우도 많습니다. warm baseline을 조금 유지하면서, 새 인스턴스가 추가될 때 최소한의 캐시 예열과 연결 준비를 수행하도록 만드는 식입니다. 이 조합은 비용이 늘 수 있지만, burst 직후의 tail latency를 더 안정적으로 만드는 데 도움이 될 수 있습니다.

### 동시성은 신뢰성과 비용을 동시에 흔듭니다

자동 스케일이 있다고 해서 동시성을 무시하면 운영이 흔들립니다.

#### 1) downstream 시스템은 같이 자동 확장되지 않습니다

DB 커넥션 풀, 외부 API rate limit, Redis 연결 수는 Functions 인스턴스 수와 같이 자동으로 늘어나지 않습니다. 함수 앱만 빠르게 scale out되면 오히려 뒤쪽 시스템을 더 빨리 병목으로 몰아갈 수 있습니다.

![함수 확장과 다운스트림 용량의 차이](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/06/06-04-1-downstream-systems-do-not-scale-with-y.ko.png)

*함수 확장과 다운스트림 용량의 차이*

그래서 운영에서는 보통 두 가지를 함께 봅니다.

- 트리거별 batch size, prefetch, 동시 처리 수 제한
- downstream 처리량에 맞춰 소비 속도를 조절할 큐 구조

이때 중요한 감각은 Functions의 스케일이 downstream 병목을 가려 주지 않는다는 사실입니다. 오히려 더 빨리 드러나게 만들 수 있습니다. 그래서 잘 설계된 queue consumer는 무조건 빨리 읽는 것이 아니라, 뒤 시스템이 감당할 수 있는 속도로 읽도록 조절되는 경우가 많습니다.

#### 2) 한 인스턴스 안에서도 여러 호출이 겹칩니다

동일 인스턴스, 동일 Worker 안에서도 여러 호출이 겹칠 수 있습니다. 따라서 모듈 전역 상태, 연결 재사용, 캐시 구조는 thread-safe 여부와 재진입성을 같이 봐야 합니다. 특히 Flex의 HTTP concurrency 설정은 **인스턴스 수만이 아니라 인스턴스 하나를 얼마나 세게 몰아붙일지**를 결정하므로 비용과 안정성 양쪽에 영향을 줍니다.

### 스케일링은 곧 비용 모델입니다

성능 이야기만 하고 비용을 빼면 절반만 본 셈입니다.

- **Consumption**: 실행 시간, 메모리, 호출 수 기준 과금입니다.
- **Flex Consumption**: 여기에 Always Ready 비용이 추가될 수 있습니다.
- **Premium**: warm baseline 비용이 먼저 존재합니다.
- **Dedicated**: App Service Plan 인스턴스 비용이 기본적으로 유지됩니다.

따라서 운영에서 최대 인스턴스 수와 동시성 설정은 성능 튜닝일 뿐 아니라 **비용 안전장치**이기도 합니다. 방치하면 성능 문제보다 비용 문제가 먼저 눈에 띄는 경우도 많습니다.

특히 재시도 폭주나 비정상 트래픽이 발생하는 상황에서는 이 안전장치의 가치가 더 커집니다. 최대 scale-out과 concurrency를 아예 열어 두면 플랫폼은 성실하게 확장하지만, 비즈니스 관점에서는 그 성실함이 곧 비용 사고가 될 수도 있습니다.

## 흔히 헷갈리는 지점

- **스케일링은 인스턴스 수만의 문제가 아닙니다.** 인스턴스 내부 동시성도 같은 만큼 중요합니다.
- **Flex Consumption이 곧 cold start 제거를 뜻하지는 않습니다.** Always Ready가 0이면 cold start는 여전히 가능합니다.
- **cold start는 하나의 원인이 아니라 여러 단계 시간의 합입니다.** 플랜만 바꾼다고 모두 해결되지는 않습니다.
- **Functions가 scale out되면 downstream도 자동으로 버텨 줄 것이라고 기대하면 안 됩니다.**
- **비용 제어와 성능 제어는 같은 스케일 설정 안에서 동시에 일어납니다.**

이 오해들이 자주 반복되는 이유는 스케일링이 겉으로는 “잘 동작하고 있다”처럼 보이기 쉽기 때문입니다. 인스턴스 수가 늘면 문제를 해결한 것처럼 느껴지지만, 실제로는 latency가 개선되지 않거나 downstream 실패율이 동시에 튈 수 있습니다. 스케일은 결과가 아니라 과정이므로, 항상 뒤 시스템과 비용까지 같이 읽어야 합니다.

또한 cold start를 무조건 제거 대상으로만 보는 것도 조심해야 합니다. 어떤 워크로드는 약간의 첫 요청 지연보다 비용 절감이 훨씬 중요할 수 있습니다. 중요한 것은 모든 지연을 없애는 것이 아니라, 비즈니스가 감당할 수 없는 지연과 감당 가능한 지연을 구분해 적절한 비용으로 제어하는 것입니다.

## 운영 체크리스트

- [ ] 워크로드별로 scale controller가 보는 신호와 concurrency 설정을 정리했습니다.
- [ ] cold start 지연을 p50/p95 기준으로 볼 수 있는 대시보드를 준비했습니다.
- [ ] Always Ready 사용 여부와 비용 trade-off를 명시적으로 결정했습니다.
- [ ] DB 커넥션 풀, 외부 API 한도, Redis 연결 수를 최대 인스턴스 수와 함께 계산했습니다.
- [ ] burst 트래픽에 대한 상한(max scale-out, batch, concurrency)을 설정했습니다.

## 정리

이번 글의 핵심은 스케일링과 콜드 스타트를 막연한 현상이 아니라 **실행 수명주기의 구체적인 단계와 제어점**으로 보는 것입니다. Azure Functions의 스케일링은 인스턴스 수와 인스턴스 내부 동시성이라는 두 축으로 읽어야 하고, cold start는 새 인스턴스 준비부터 첫 호출까지 여러 단계 시간이 합쳐진 결과입니다.

또한 좋은 튜닝은 플랜만 바꾸는 일이 아니라, 플랜·코드·운영 설정을 함께 움직이는 일입니다. Flex나 Premium의 warm capacity는 인프라 쪽 지연을 줄여 주지만, import와 초기화가 무거우면 애플리케이션이 스스로 cold start를 키울 수 있습니다. 반대로 concurrency와 scale limit를 적절히 다루면 성능과 비용을 동시에 제어할 수 있습니다.

다음 글에서는 이 동작을 실제로 관측하는 방법으로 넘어갑니다. **Application Insights, Live Metrics, KQL, InstanceCount, 알람**을 통해 지금 몇 개 인스턴스가 도는지, 실패율과 지연이 어디서 올라가는지, 비용 신호가 어떻게 보이는지 정리하겠습니다.

결국 스케일링과 cold start를 잘 다루는 팀은 “왜 느린가”를 단일 원인으로 보지 않습니다. 인스턴스 준비, runtime 시작, 코드 초기화, downstream 병목, 비용 상한까지 같은 그림 안에서 읽습니다. 그 시야가 다음 장의 모니터링과 운영 기준으로 자연스럽게 이어집니다.

## 처음 질문으로 돌아가기

- **Functions scale controller는 어떤 신호를 보고 인스턴스를 추가할까요?**
  - scale controller는 트리거 종류에 맞는 수요 신호를 보고 인스턴스를 늘립니다. HTTP에서는 요청 압력과 인스턴스당 concurrency가 중요하고, 큐 계열에서는 backlog·batch·prefetch 같은 값이 더 직접적인 신호가 되므로, 같은 앱이라도 어떤 트리거가 병목을 만들었는지 먼저 봐야 합니다.
- **콜드 스타트는 정확히 어느 단계에서 발생하고, 무엇을 측정해야 볼 수 있을까요?**
  - cold start는 새 인스턴스 할당, Host 초기화, Worker 시작, import와 전역 초기화, 첫 호출 처리까지의 합입니다. 그래서 `InstanceCount`, `FunctionExecutionUnits`, App Insights 지연 분포와 함께 `create_cosmos_client()` 같은 초기화 경로가 첫 요청 시간을 얼마나 키우는지도 같이 봐야 정확합니다.
- **Premium의 Always Ready나 Flex의 always-ready 인스턴스는 콜드 스타트를 어디까지 줄여 줄까요?**
  - 이 설정들은 새 인스턴스와 Host 준비 비용을 앞당겨 두어 첫 호출 지연을 줄여 줍니다. 다만 `Always Ready`나 always-ready 인스턴스가 있어도 큰 import, 느린 전역 초기화, 첫 DB 연결 생성까지 대신 없애 주는 것은 아니므로, 플랜 설정과 코드 초기화를 같이 다뤄야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions 101 (1/7): Azure Functions란? — 이벤트가 함수를 호출하는 세상](./01-what-is-azure-functions.md)
- [Azure Functions 101 (2/7): 트리거와 바인딩 — 함수 입출력의 모든 것](./02-triggers-and-bindings.md)
- [Azure Functions 101 (3/7): Host와 Worker — 함수는 누가 실행하는가](./03-host-and-worker.md)
- [Azure Functions 101 (4/7): 함수 하나 배포하기 — 로컬에서 Azure까지](./04-first-deploy.md)
- [Azure Functions 101 (5/7): 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated](./05-choosing-a-plan.md)
- **Azure Functions 101 (6/7): 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 (현재 글)**
- Azure Functions 101 (7/7): 모니터링과 운영 기초 (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Event-driven scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Target-based scaling](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)
- [Warmup trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-warmup)
- [Manage connections in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections)

### 관련 시리즈

- [Azure Functions 101 — 어떤 플랜을 선택해야 할까](./05-choosing-a-plan.md)
- [Azure Functions 101 — 모니터링과 운영 기초](./07-monitoring-and-ops.md)
- [Azure Functions Deep Dive — 스케일링 내부 동작](../../azure-functions-deep-dive/ko/05-scaling-internals.md)
- [Azure Functions Deep Dive — 콜드 스타트와 Placeholder Mode](../../azure-functions-deep-dive/ko/06-cold-start-placeholder.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-101/ko/06-scaling-and-cold-start)

Tags: Azure, Azure Functions, Serverless, Cloud
