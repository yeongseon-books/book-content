---
title: 모니터링과 운영 기초
series: azure-functions-101
episode: 7
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
seo_description: 함수 앱을 배포한 뒤부터는 질문이 달라집니다. 함수가 실행되느냐보다, 지금 실패율이 튀는지, 인스턴스 수가 왜 늘었는지,
  외부 의존성이…
---

# 모니터링과 운영 기초

함수 앱을 배포하고 나면 질문이 달라집니다. “함수가 뜨는가”보다 “왜 실패율이 갑자기 올라갔는가”, “인스턴스 수가 왜 늘어났는가”, “지연은 함수 자체 문제인가, downstream 문제인가”, “비용은 어디서 새고 있는가” 같은 질문이 더 중요해집니다. 이 시점부터 Azure Functions는 코드 배포 대상이 아니라 **관측 가능한 운영 시스템**이어야 합니다.

Azure Functions 운영이 특히 어려워 보이는 이유는 이벤트 기반 실행 모델 때문입니다. scale to zero가 가능한 플랜에서는 인스턴스가 계속 바뀔 수 있고, 트리거 종류에 따라 재시도와 실패 패턴도 다르고, Host와 Worker 로그가 섞여 보일 수도 있습니다. 그래서 운영 초반에는 “무엇부터 보면 되는가”를 먼저 정리해 두는 편이 중요합니다.

이 글은 Azure Functions 101 시리즈의 마지막 글입니다. 여기서는 Application Insights를 중심으로, 기본 관측 구조, KQL 조회 패턴, Live Metrics 사용법, 인스턴스 수와 비용 신호 읽는 법, 그리고 초반 알람 우선순위를 정리합니다. 목표는 화려한 대시보드가 아니라 **장애 초반 5분 안에 방향을 잡을 수 있는 최소 운영 기준**을 만드는 것입니다.

앞선 글에서 스케일링과 콜드 스타트가 어떤 동작인지 설명했다면, 이번에는 그 동작을 실제로 어떻게 볼 것인지 다룹니다. 즉 현상을 설명하는 글에서, 현상을 읽고 대응하는 글로 넘어가는 셈입니다.

이제 “무엇이 평소와 다른가”를 가장 빨리 드러내는 화면과 쿼리부터 정리하겠습니다.

---

## 이 글에서 다룰 문제

- Application Insights와 Log Analytics는 Azure Functions 운영에서 어떤 역할로 나뉠까요?
- 함수별 지연, 실패율, 의존성 호출을 보려면 어떤 쿼리를 먼저 갖고 있어야 할까요?
- Live Metrics와 stream logs는 언제 각각 더 유리할까요?
- 비용이 튀기 전에 미리 볼 수 있는 메트릭은 무엇일까요?
- 장애 대응 런북에는 최소 무엇이 반드시 들어가야 할까요?

## 왜 이 글이 중요한가

운영의 대부분은 새로운 기술보다 **이상 징후를 기준선과 비교해 빨리 읽는 능력**에 달려 있습니다. Azure Functions도 예외가 아닙니다. 실패율이 올라간 것인지, 인스턴스 수만 늘어난 것인지, dependency 실패가 늘어난 것인지, 단지 트래픽이 평소보다 많을 뿐인지 빠르게 나눌 수 있어야 합니다. 같은 “느리다”는 현상도 관측 구조가 없으면 매번 처음부터 추측하게 됩니다.

또한 Azure Functions는 trigger별 재시도 모델, scale out, cold start, Host/Worker 분리 때문에 일반 웹 앱과는 다른 운영 함정을 가집니다. 예를 들어 Service Bus와 Storage Queue는 실패 메시지 처리 모델이 다르고, Linux 기반 플랜에서는 Windows에서 보던 Performance Counters를 그대로 기대하면 안 되며, cold start는 단일 메트릭이 아니라 여러 신호의 조합으로 추정해야 합니다. 이런 차이를 모르면 대시보드를 보고도 해석이 빗나가기 쉽습니다.

무엇보다 이 글은 시리즈 전체를 운영 관점에서 닫아 줍니다. 이벤트 기반 실행 모델, 트리거와 바인딩, Host와 Worker, 플랜 선택, 스케일링과 cold start까지 모두 이해해도, 실제로 무엇을 보고 대응해야 하는지 정리되지 않으면 시스템은 아직 운영 가능한 상태가 아닙니다. 이번 장은 그 마지막 연결을 담당합니다.

## 운영을 이해하는 가장 좋은 방법: 기준선에서 벗어난 신호를 30초 안에 찾는 문제로 보는 것입니다

Azure Functions 운영을 잘한다는 것은 결국 “지금 무엇이 평소와 다른가”를 아주 빠르게 찾는 능력에 가깝습니다. 요청량이 늘었는지, 실패율이 튀었는지, dependency 호출이 깨지는지, 인스턴스 수가 상한에 가까운지, 비용이 평소보다 빨리 증가하는지 같은 신호를 먼저 잡아야 합니다. 즉 좋은 운영 화면은 모든 것을 보여 주는 화면이 아니라, **평소와 다른 것을 가장 빨리 드러내는 화면**입니다.

운영자가 가장 먼저 열 화면은 대체로 Live Metrics이고, 그다음은 Application Insights 쿼리와 Azure Monitor 메트릭입니다. Live Metrics는 지금 이 순간의 이상 징후를 빠르게 보여 주고, KQL은 그 이상 징후를 어떤 함수와 어떤 외부 의존 호출, 어떤 예외가 만들었는지 좁히는 데 도움을 줍니다. 그리고 메트릭은 인스턴스 수, 실행 단위, 비용 추세처럼 더 긴 시간축의 변화를 읽게 해 줍니다.

따라서 운영의 핵심은 대시보드를 많이 만드는 데 있지 않습니다. **화면, 쿼리, 메트릭, 알람을 어떤 순서로 보는지 표준화하는 데** 있습니다. 순서가 정리되면 장애가 와도 팀이 같은 신호를 보고 같은 언어로 이야기할 수 있습니다.

> Azure Functions 운영의 출발점은 “무슨 일이 벌어졌는가”보다 “평소와 다른 신호가 어디서 처음 보이는가”를 30초 안에 찾는 것입니다.

이 기준을 팀 공통 언어로 만들면 장점이 큽니다. 장애가 났을 때 각자가 임의로 다른 화면을 보지 않고, 같은 순서와 같은 메트릭을 먼저 확인하게 되기 때문입니다. 운영 품질은 개인의 숙련도보다 관측 순서를 표준화했는지에서 더 크게 차이가 나기도 합니다.

## 핵심 개념

### 시작점은 Application Insights입니다

Azure Functions 운영 데이터의 대부분은 Application Insights로 모입니다. 요청, 예외, dependency 호출, 로그, custom metrics가 여기에 모이기 때문에, Function App을 만든 뒤 App Insights 연결을 빨리 붙이는 편이 유리합니다.

```bash
# Function App 생성 후 가장 단순하게 연결하는 방법
az monitor app-insights component create \
    --app ai-hello --location koreacentral --resource-group $RG

az functionapp config appsettings set \
    --name $APP --resource-group $RG \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="<your-connection-string>"
```

연결 후 가장 많이 보는 항목은 아래와 같습니다.

- **Requests** — 함수 호출 기록
- **Exceptions** — 함수 내부 예외
- **Dependencies** — HTTP, DB, Storage 등 외부 시스템 호출
- **Traces** — 애플리케이션 로그
- **Metrics / customMetrics** — 플랫폼 메트릭과 사용자 정의 신호

여기서 중요한 점은 모든 신호가 같은 속도와 같은 해상도로 들어오지 않는다는 사실입니다. 실시간 대응에는 Live Metrics가 강하고, 추세 분석과 원인 분석에는 Logs와 Metrics가 더 강합니다. 따라서 “App Insights 하나로 다 본다”보다는 “App Insights 안에서도 어떤 표면을 언제 여는가”가 더 중요합니다.

한 가지 주의할 점도 있습니다. Linux 기반 환경, 특히 Flex Consumption에서는 Windows에서 보던 방식의 CPU·메모리 성능 카운터를 그대로 기대하면 안 됩니다. 운영 화면에서 바로 볼 수 있는 신호는 플랜과 OS에 따라 달라질 수 있습니다.

### 장애가 의심될 때 가장 먼저 볼 화면은 Live Metrics입니다

실시간 상황에서는 **Application Insights → Live Metrics**가 가장 빠른 출발점입니다. 요청량, 실패율, 응답 시간 변화, 현재 활성 인스턴스 수 같은 신호를 거의 실시간으로 확인할 수 있기 때문입니다.

![장애 초기에 보는 Live Metrics 신호](../../../assets/azure-functions-101/07/07-01-the-first-screen-to-open-during-an-incid.ko.png)

*장애 초기에 보는 Live Metrics 신호*

Live Metrics가 좋은 이유는 “지금 이 순간”의 변화를 빠르게 보여 주기 때문입니다. 다만 세부 인프라 카운터는 OS와 환경 차이를 같이 염두에 둬야 합니다. 인스턴스 활동과 요청 흐름은 폭넓게 유용하지만, CPU/메모리 같은 저수준 카운터는 항상 동일하지 않을 수 있습니다.

실무에서는 여기서 첫 판단을 내립니다. 실패율이 올라가는데 요청량은 그대로인지, 요청량 증가와 함께 지연이 튀는지, 인스턴스 수가 같이 늘고 있는지 정도만 30초 안에 잡혀도 탐색 방향이 크게 좁혀집니다.

### 자주 쓰는 조회 패턴 다섯 가지를 준비해 둡니다

#### 1) 최근 1시간 호출 수와 실패율

```kusto
requests
| where timestamp > ago(1h)
| summarize Total=count(), Failed=countif(success == false) by bin(timestamp, 1m)
| extend FailureRate = round(100.0 * Failed / Total, 2)
| order by timestamp desc
```

이 쿼리는 “지금 문제가 있는가”를 가장 빠르게 보여 주는 기본형입니다. 전체 호출 수 대비 실패율이 올라가는지부터 확인해야 다른 분석이 의미를 갖습니다.

특히 배포 직후나 설정 변경 직후에는 이 쿼리가 유용합니다. 호출 수는 비슷한데 실패율만 급증했다면, 트래픽 패턴보다 배포나 환경 변화에 더 먼저 의심을 둘 수 있기 때문입니다.

#### 2) 가장 자주 발생한 예외 Top 10

```kusto
exceptions
| where timestamp > ago(24h)
| summarize Count=count() by problemId, type
| top 10 by Count
```

특정 예외가 반복되는지, 새로운 종류의 예외가 등장했는지 파악하는 데 유용합니다. 장애 초반에는 예외 종류를 빠르게 줄여 보는 것만으로도 탐색 범위가 많이 줄어듭니다.

예외 Top 10을 볼 때는 단순 count뿐 아니라 새로 등장한 예외인지 여부도 함께 보는 편이 좋습니다. 어제까지 없던 예외가 오늘 갑자기 상위권으로 올라왔다는 사실만으로도 변경 지점을 의심할 수 있습니다.

#### 3) 가장 느린 함수 Top 10

```kusto
requests
| where timestamp > ago(24h)
| summarize p95=percentile(duration, 95), Count=count() by name
| top 10 by p95
```

평균보다 P95를 보는 이유는 tail latency가 사용자 체감과 운영 위험을 더 빨리 보여 주기 때문입니다. 느린 함수가 특정 몇 개로 집중되는지 확인하면 대응 우선순위를 정하기 쉬워집니다.

#### 4) cold start는 간접 신호로 봅니다

Azure Functions에는 모든 플랜에서 신뢰할 수 있는 단일 “cold start count” 메트릭이 있는 것이 아닙니다. 따라서 운영에서는 아래 신호를 조합해 간접적으로 판단합니다.

- **`InstanceCount`** 추세 — 인스턴스 수 변화
- **`FunctionExecutionUnits`** 추세 — 실행 부하 증가
- **App Insights `customMetrics`의 warm-up 관련 신호** — 환경에 따라 추가 단서 제공

```bash
az monitor metrics list \
    --resource "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP" \
    --metric "InstanceCount" "FunctionExecutionUnits" \
    --interval PT5M
```

이 지표만으로 콜드 스타트 횟수를 정확히 셀 수는 없습니다. 배포, 재시작, scale out 등 여러 현상이 비슷한 신호를 만들 수 있으므로, 언제나 정황을 함께 보며 해석해야 합니다.

#### 5) downstream dependency 실패

```kusto
dependencies
| where timestamp > ago(1h) and success == false
| summarize Count=count() by target, type, resultCode
| order by Count desc
```

함수 코드 자체보다 외부 시스템이 문제일 때 가장 빠르게 단서를 줍니다. 특히 DB, 외부 API, Storage가 병목인지 구분할 때 유용합니다.

### 알람은 네 가지 우선순위면 충분합니다

초기에 너무 많은 알람을 걸면 아무도 믿지 않게 됩니다. 다음 네 가지면 시작점으로 충분합니다.

| 우선순위 | 알람 대상 | 임계값 예시 | 이유 |
|---|---|---|---|
| P0 | 함수 실패율 급증 | 5분 실패율 > 5% | 사용자 영향 직접 발생 |
| P0 | 응답 시간 급증 | P95가 평시 대비 3배 | 전체 장애 전 단계에서 먼저 보임 |
| P1 | 인스턴스 상한 근접 | `InstanceCount`가 설정 상한 근처 | 더 들어오는 부하를 못 받을 수 있음 |
| P2 | 비용 급증 | 일일 호출 수가 평시 대비 5배 | 버그, 재시도 폭주, 비정상 트래픽 가능성 |

처음에는 P0 두 개만 안정적으로 운영해도 상당히 유용합니다. 운영팀이 신뢰하는 알람을 만드는 것이, 많은 알람을 만드는 것보다 훨씬 중요합니다.

### 인스턴스 수는 어디서 확인할까요

운영자가 먼저 써야 할 경로는 두 가지입니다.

1. **Live Metrics의 Servers 패널** — 가장 즉각적인 시각 확인
2. **Azure Monitor의 `InstanceCount` 메트릭** — 포털에서는 *Automatic Scaling Instance Count*로 보임

현재 앱 설정을 CLI로 보고 싶다면 아래 경로를 씁니다.

`az functionapp show --name $APP --resource-group $RG --query siteConfig`

이 정보는 “지금 무엇이 배포되어 있고 어떤 설정 계층이 적용되어 있는가”를 점검할 때 유용합니다. 특히 현상은 런타임 문제처럼 보이는데 실제 원인이 설정 변경이었는지 확인할 때 도움이 됩니다.

`/admin/host/scale/status` 같은 엔드포인트는 심화 진단에 가깝고, 일반 운영 표면으로 기대하는 편은 안전하지 않습니다.

### 비용 분석은 재시도 모델부터 나눠 봐야 합니다

비용이 갑자기 늘었을 때 흔한 원인은 호출 폭증, 재시도 폭주, 로그 과다입니다. 특히 큐 트리거는 종류별 실패 처리 방식이 다르므로 먼저 나눠 봐야 합니다.

**Service Bus 트리거**는 `maxDeliveryCount`와 dead-letter queue 모델을 가집니다. 반복 실패 메시지는 delivery count가 올라가고, 한도를 넘으면 DLQ로 이동합니다.

**Storage Queue 트리거**는 같은 용어를 쓰지 않습니다. 메시지는 dequeue count를 늘리며 다시 나타나고, 한도를 넘기면 보통 **poison queue**로 이동합니다. 따라서 “queue trigger는 모두 DLQ와 maxDeliveryCount를 보면 된다”는 식으로 일반화하면 틀립니다.

추가로 비용 누수에서 자주 보는 패턴은 아래 두 가지입니다.

- **타이머 빈도 과다** — 너무 촘촘한 스케줄은 호출 수를 빠르게 키웁니다.
- **과도한 로그** — 큰 payload를 매 요청마다 남기면 App Insights 수집 비용이 커집니다.

여기에 재시도 폭주가 겹치면 비용은 더 빨리 커집니다. 따라서 비용 알람은 단순 청구 알람이 아니라, 호출 수와 실패율과 재시도 패턴을 같이 해석하는 운영 알람으로 보는 편이 유용합니다.

```bash
# 일일 호출 수 추세를 빠르게 확인하는 CLI 예시
az monitor app-insights events show \
    --app ai-hello --resource-group $RG \
    --type requests --offset 7d
```

### 새벽 장애 때는 순서를 표준화해 둡니다

장애 초반 5분은 대체로 같은 질문을 반복합니다.

![장애 초반 점검 순서와 판단 흐름](../../../assets/azure-functions-101/07/07-02-a-useful-3am-incident-order-of-operation.ko.png)

*장애 초반 점검 순서와 판단 흐름*

실패율 → 응답 시간 → 인스턴스 수 → dependency 실패 순서로 보면, 문제를 함수 자체, 스케일, downstream 중 어디서 먼저 봐야 할지 빠르게 감이 옵니다. 이 순서가 런북에 정리되어 있으면 새벽 대응 품질이 크게 올라갑니다.

## 흔히 헷갈리는 지점

- **Application Insights만 붙이면 운영 준비가 끝난다고 생각하면 안 됩니다.** 어떤 화면과 쿼리를 먼저 볼지까지 정리돼야 합니다.
- **cold start는 단일 메트릭으로 정확히 세기 어렵습니다.** 여러 신호를 함께 읽어야 합니다.
- **Live Metrics는 실시간에 강하고, KQL은 원인 좁히기에 강합니다.** 둘을 대체 관계로 보면 안 됩니다.
- **Queue trigger의 실패 처리 모델은 Service Bus와 Storage Queue가 다릅니다.**
- **비용 문제는 성능 문제와 별개가 아니라 재시도, 로그, 호출 수와 직접 연결됩니다.**

이런 오해들이 반복되는 이유는 운영 도구가 많기 때문입니다. 화면이 많다고 관측력이 자동으로 좋아지지는 않습니다. 오히려 너무 많은 화면이 있으면 팀마다 보는 기준이 달라져 같은 장애를 서로 다른 이야기로 해석하기 쉽습니다. 그래서 운영 초반일수록 도구보다 순서가 더 중요합니다.

## 운영 체크리스트

- [ ] 함수별 latency와 실패율 차트를 기본 대시보드에 추가했습니다.
- [ ] 주요 dependency(DB, 외부 API, Storage)의 분산 추적과 실패 조회 경로를 준비했습니다.
- [ ] 실행 수, GB-s, 호출 폭증에 대한 비용 알람을 설정했습니다.
- [ ] 장애 대응 런북에 첫 5분 점검 순서를 명시했습니다.
- [ ] 운영팀이 Live Metrics와 App Insights Logs에 접근할 수 있도록 권한을 정리했습니다.

## 정리

이번 글은 Azure Functions 101 시리즈를 운영 관점에서 마무리했습니다. 핵심은 단순합니다. **좋은 운영은 많은 화면이 아니라, 기준선에서 벗어난 신호를 빠르게 찾는 구조**에서 시작합니다. Application Insights는 그 중심이고, Live Metrics는 실시간 출발점이며, KQL은 원인을 좁히는 도구이고, Azure Monitor 메트릭은 인스턴스 수와 비용 같은 장기 추세를 읽게 해 줍니다.

또한 Azure Functions 운영에서는 trigger별 재시도 모델, cold start의 간접 관측, Host/Worker 구조, scale out과 downstream 병목을 함께 읽는 감각이 필요합니다. 즉 단순히 “에러가 났다”를 보는 것이 아니라, 어떤 함수가, 어떤 dependency와, 어떤 스케일 상태에서, 어떤 비용 신호와 함께 문제를 만들고 있는지 해석해야 합니다.

이 시리즈 전체를 한 문장으로 접으면 이렇습니다. **이벤트가 코드를 깨우고, 트리거와 바인딩이 입출력을 정의하고, Host와 Worker가 실행을 분리하고, 플랜이 비용과 성능 특성을 바꾸며, 운영은 그 모든 동작을 관측하고 대응하는 일**입니다. 이제 Azure Functions를 단순한 서버리스 데모가 아니라, 운영 가능한 플랫폼으로 볼 준비가 된 셈입니다.

시리즈의 끝에서 남는 실무 조언도 하나 덧붙일 수 있습니다. 운영은 완벽한 대시보드를 만드는 일이 아니라, 팀이 같은 기준선과 같은 대응 순서를 공유하게 만드는 일입니다. 그 기준이 잡혀 있으면 Azure Functions는 추상화가 강한 플랫폼이면서도 충분히 예측 가능한 운영 대상이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions란? — 이벤트가 함수를 호출하는 세상](./01-what-is-azure-functions.md)
- [트리거와 바인딩 — 함수 입출력의 모든 것](./02-triggers-and-bindings.md)
- [Host와 Worker — 함수는 누가 실행하는가](./03-host-and-worker.md)
- [함수 하나 배포하기 — 로컬에서 Azure까지](./04-first-deploy.md)
- [어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated](./05-choosing-a-plan.md)
- [스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간](./06-scaling-and-cold-start.md)
- **모니터링과 운영 기초 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Monitor Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-monitoring)
- [Application Insights overview](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Metrics supported for Microsoft.Web/sites](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-web-sites-metrics)
- [Kusto Query Language reference](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Configure monitoring for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/configure-monitoring)

### 관련 시리즈

- [Azure Functions 101 — 스케일링과 콜드 스타트](./06-scaling-and-cold-start.md)
- [Azure Functions Deep Dive — 스케일링 내부 동작](../../azure-functions-deep-dive/ko/05-scaling-internals.md)
- [Azure Functions Deep Dive — 콜드 스타트와 Placeholder Mode](../../azure-functions-deep-dive/ko/06-cold-start-placeholder.md)

Tags: Azure, Azure Functions, Serverless, Cloud
