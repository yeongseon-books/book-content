---
title: "Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N"
series: azure-aca-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- KEDA
- Autoscaling
- Scale-to-Zero
- Serverless
last_reviewed: '2026-05-15'
seo_description: 스케일링은 신호, 규칙, 범위라는 세 단계 선언형 흐름으로 이해하면 단순해집니다.
---

# Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N

ACA의 스케일링은 단순히 replica 수를 늘리는 기능이 아닙니다. 어떤 신호를 중요하게 볼지, 그리고 0까지 내려갈 수 있게 할지를 정하는 순간 비용 정책과 지연 시간 정책도 함께 정해집니다.

이 글은 Azure Container Apps 101 시리즈의 5번째 글입니다. 여기서는 KEDA scaler와 zero-to-N 모델을 운영 관점에서 풀어 보겠습니다.

![Azure Container Apps 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/05/05-01-the-scaling-path.ko.png)
*Azure Container Apps 101 5장 흐름 개요*
> 스케일링 — KEDA scaler와 zero-to-N의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- Azure Container Apps는 선언형 스케일링 신호를 바탕으로 replica 수를 어떻게 결정할까요?
- 내장 HTTP/TCP 규칙과 사용자 정의 KEDA scaler의 차이는 무엇일까요?
- `min-replicas 0`(scale-to-zero)는 언제 안전하고, 언제 위험할까요?

## 이 글이 답할 질문

- Azure Container Apps는 어떤 신호를 보고 replica 수를 결정하며, 그 판단은 어디에서 이루어질까요?
- 내장 HTTP/TCP 규칙과 사용자 정의 KEDA scaler 중 언제 무엇을 써야 할까요?
- `min-replicas 0`(scale-to-zero)는 언제 안전하고, 언제 위험할까요?
- Service Bus 큐 worker는 왜 HTTP 규칙이 아니라 KEDA scaler로 스케일해야 할까요?
- cold start와 SLO 사이의 트레이드오프는 어떻게 측정하고 받아들여야 할까요?

## 왜 이 글이 중요한가

ACA의 핵심 가치 제안은 "Kubernetes의 무게 없이 컨테이너를 운영한다"입니다. 그 약속이 가장 선명하게 보이는 지점이 스케일링입니다.

여기서는 HPA(Horizontal Pod Autoscaler)나 KEDA를 직접 설치하지 않습니다. 같은 KEDA scaler가 ACA control plane 안에서 동작합니다.

스케일링을 오해하면 두 방향에서 비용을 치르게 됩니다. 첫째는 돈입니다. `min-replicas`를 0보다 크게 둔 채 잊어버리면 유휴 replica 비용을 계속 냅니다. 둘째는 신뢰성입니다. 큐 worker를 HTTP 규칙에 묶어 두면 메시지가 쌓여도 replica는 늘지 않습니다. 스케일 규칙은 비용 정책이면서 동시에 SLO 정책입니다.

## 멘탈 모델

스케일링은 세 단계 선언형 파이프라인으로 보면 단순해집니다.

1. **Signal** — 무엇을 볼지: HTTP 동시 요청 수, TCP 연결 수, Service Bus 큐 길이, CPU 사용률 등
2. **Rule** — 그 신호를 어떻게 해석할지: `--scale-rule-type http`, `azure-servicebus`, `cpu` 등
3. **Bounds** — `--min-replicas`와 `--max-replicas` 사이에서 KEDA가 replica 수를 고릅니다

Signal → Rule → Bounds. 이 세 가지가 정해지면 나머지는 ACA가 처리합니다.
YAML이나 명령형 스케일링 코드를 쓰는 것이 아니라, "이 신호가 오면 N까지 늘려라"라고 선언하는 구조입니다.

> 스케일링은 무엇을 볼지, 어떻게 해석할지, 어디까지 허용할지를 먼저 선언하고, 런타임이 그 범위 안에서 replica 수를 움직이게 하는 모델입니다.

## 핵심 개념

### 1. 세 가지 규칙 범주

| Category | Trigger | Scale-to-zero | 흔한 용도 |
| --- | --- | --- | --- |
| HTTP rule | Concurrent HTTP requests | Yes | Web API, REST 서비스 |
| TCP rule | Concurrent TCP connections | Yes | gRPC, 사용자 정의 TCP 서버 |
| Custom KEDA rules | Service Bus, Event Hubs, Kafka, Redis, CPU, memory 등 | scaler에 따라 다름 | 큐 worker, 배치 프로세서 |

HTTP와 TCP는 ACA ingress 레이어가 직접 측정하므로 추가 인증이 필요 없습니다.
반면 custom rule은 외부 리소스(Service Bus namespace 등)에 접근하므로 `--scale-rule-auth`로 secret을 연결해야 합니다.

### 2. scale-to-zero가 실제로 뜻하는 것

`--min-replicas 0`는 "트래픽이 없으면 replica를 0까지 내린다"는 뜻입니다.
다음 요청이 들어오면 ACA가 새 replica를 띄우면서 cold start가 발생합니다.
HTTP 규칙과 대부분의 이벤트 기반 KEDA scaler(Service Bus, Event Hubs, Kafka 등)는 0까지 내려갈 수 있습니다.
**CPU와 memory scaler는 custom 범주에 속하지만 scale-to-zero는 되지 않습니다.** CPU나 memory를 측정하려면 최소 하나의 replica가 있어야 하기 때문입니다.

### 3. cold start 트레이드오프

Scale-to-zero는 유휴 비용을 거의 0으로 밀어 내지만, 첫 요청은 컨테이너가 뜰 때까지 기다려야 합니다.
Python/FastAPI는 보통 1–3초 정도 걸리고, 무거운 모델 로딩은 10초 이상까지 늘 수 있습니다.
사용자 대면 동기 API는 `min-replicas 1`이 낫고, 비동기 worker나 야간 배치는 `min-replicas 0`이 적절합니다.

## Before / After

### Before (명시적인 스케일 규칙이 없는 경우)

```bash
az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000
```

명시적인 규칙이 없으면 ACA는 기본 HTTP 스케일 규칙(concurrency 10)과 함께 `min-replicas 0`, `max-replicas 10`을 적용합니다.
덕분에 유휴 비용은 없지만 첫 요청은 cold start를 맞습니다.
ACA는 더 높은 replica 상한으로 구성할 수 있지만, 별도 설정이 없다면 기본 스케일 범위는 0~10 replica입니다.

### After (명시적인 HTTP 규칙을 둔 경우)

```bash
az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --min-replicas 1 --max-replicas 10 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```

`min-replicas 1`은 cold start를 없앱니다. `max-replicas 10`은 비용 상한을 잡아 줍니다.
동시 요청 50개를 기준으로 replica가 늘어나므로, 트래픽 스파이크 동안 지연 시간을 더 안정적으로 유지할 수 있습니다.

## 단계별 실습

### Step 1: HTTP API에 스케일 규칙 적용하기

FastAPI 앱이 이미 ACR에 올라가 있다고 가정합니다.

```bash
RG=rg-aca-demo
ACA_ENV=aca-env-demo
IMAGE=myacr.azurecr.io/my-api:latest

az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --min-replicas 0 --max-replicas 5 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100
```

### Step 2: Service Bus 큐 worker 만들기

```bash
az containerapp create \
  --name queue-worker --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE \
  --min-replicas 0 --max-replicas 10 \
  --secrets "sb-connection=<SERVICE_BUS_CONNECTION_STRING>" \
  --scale-rule-name servicebus-rule \
  --scale-rule-type azure-servicebus \
  --scale-rule-metadata \
      "queueName=orders" \
      "namespace=mybus.servicebus.windows.net" \
      "messageCount=5" \
  --scale-rule-auth "connection=sb-connection"
```

`messageCount=5`는 "대기 메시지 5개마다 replica 하나"를 뜻합니다.
큐가 비면 0으로 내려가고, 50개가 쌓이면 10 replica(최대값)까지 올라갑니다.

### Step 3: 동작 검증하기

```bash
az containerapp replica list --name queue-worker --resource-group $RG -o table
```

메시지를 넣은 뒤 30–60초 안에 replica 수가 바뀌어야 정상입니다.

## 자주 하는 실수

- 지연 시간에 민감한 API에 `min-replicas 0`을 쓰는 것 — 매번 cold path가 cold start 비용을 냅니다. 사용자 대면 API는 최소 1로 고정하는 편이 안전합니다.
- `max-replicas`를 지정하지 않는 것 — 트래픽 급증이나 잘못된 규칙 하나가 곧 비용 사고가 됩니다.
- 큐 worker에 HTTP 규칙을 다는 것 — 메시지는 쌓이는데 replica는 늘지 않습니다. 이벤트 기반 scaler를 써야 합니다.
- 인증 없이 Service Bus scaler를 구성하는 것 — `--scale-rule-auth`가 없으면 KEDA가 큐를 polling할 수 없어 스케일링이 일어나지 않습니다.
- CPU scaler에 `min-replicas 0`을 기대하는 것 — CPU와 memory scaler는 측정할 replica가 필요하므로 0까지 내려가지 않습니다.

## 프로덕션에서는 이렇게 둔다

시나리오별 권장값은 보통 아래와 같습니다.

- 공개 REST API — `min=1, max=10`, HTTP rule, concurrency 50–100. cold start 제거를 우선합니다.
- 내부 admin API — `min=0, max=3`, HTTP rule. 비용을 우선합니다.
- 주문 처리 worker — `min=0, max=20`, Service Bus rule, `messageCount=10`. 버스트 처리량을 우선합니다.
- 실시간 추론 API — `min=2, max=20`, HTTP rule, concurrency 20. 지연 시간 SLO가 가장 중요합니다.
- 야간 배치 — `min=0, max=5`, 스케줄 기반 또는 수동 트리거.

KEDA scaler 종류는 [공식 문서](https://keda.sh/docs/scalers/)에 정리돼 있고, Microsoft Learn에는 ACA가 지원하는 scaler 목록이 나옵니다.

## 스케일링 시나리오 — HTTP와 큐 기반 워크로드 분리

KEDA 규칙은 워크로드 성격별로 따로 설계해야 합니다. API와 worker를 같은 기준으로 스케일링하면 비용 또는 지연 시간 중 하나를 잃습니다.

### 시나리오 1: 공개 API(지연 시간 우선)

```bash
az containerapp update --name api --resource-group $RG \
  --min-replicas 1 --max-replicas 20 \
  --scale-rule-name http-main \
  --scale-rule-type http \
  --scale-rule-http-concurrency 40
```

예상 동작:

```text
평균 20 rps: replicas 1~2
피크 200 rps: replicas 5~7
유휴 0 rps: replicas 1 유지
```

### 시나리오 2: Service Bus worker(비용 우선)

```bash
az containerapp update --name worker --resource-group $RG \
  --min-replicas 0 --max-replicas 30 \
  --scale-rule-name sb-orders \
  --scale-rule-type azure-servicebus \
  --scale-rule-metadata queueName=orders namespace=mybus.servicebus.windows.net messageCount=20 \
  --scale-rule-auth connection=sb-connection
```

예상 동작:

```text
queue depth 0: replicas 0
queue depth 200: replicas 약 10
queue depth 1000: replicas 최대 30
```

### Bicep scale 블록 예시

```bicep
template: {
  scale: {
    minReplicas: 0
    maxReplicas: 30
    rules: [
      {
        name: 'sb-orders'
        custom: {
          type: 'azure-servicebus'
          metadata: {
            queueName: 'orders'
            namespace: 'mybus.servicebus.windows.net'
            messageCount: '20'
          }
          auth: [
            { secretRef: 'sb-connection', triggerParameter: 'connection' }
          ]
        }
      }
    ]
  }
}
```

### 운영 팁 — 과도 스케일 방지

- `maxReplicas`는 반드시 지정합니다.
- 큐 처리량 기준으로 `messageCount`를 역산해 규칙을 잡습니다.
- CPU scaler와 이벤트 scaler를 혼합할 때는 우선순위가 아니라 병렬 평가라는 점을 기억해야 합니다.

결론적으로 스케일 정책은 앱 성능 옵션이 아니라 비용과 SLO의 계약입니다. 계약을 숫자로 적어 두지 않으면 재현 가능한 운영이 어렵습니다.

## 튜닝 방법 — 숫자를 어떻게 고를지

스케일 파라미터는 감으로 정하면 안 됩니다. 최소한 세 가지 입력값을 측정해 역산해야 합니다.

### 입력값

- 목표 p95 latency
- 단일 replica 처리량
- 피크 도달 시간(버스트 상승 기울기)

예를 들어 replica 하나가 초당 25요청을 안정 처리하고 목표 피크가 250요청이라면 이론상 10 replica가 필요합니다. 여기에 안전 계수 1.2를 곱해 `maxReplicas=12`부터 시작할 수 있습니다.

### 단계별 조정 루프

1. 보수적 값으로 시작(`min=1`, `max=12`, concurrency=40)
2. 부하 테스트 10분
3. p95와 오류율 확인
4. concurrency 또는 max 조정
5. 재테스트

이 과정을 두세 번 반복하면 환경별 초기값이 만들어집니다.

### 부하 테스트 명령 예시

```bash
# k6 예시
k6 run --vus 50 --duration 5m scripts/load.js

# 동시에 replica 추적
watch -n 15 "az containerapp replica list --name api --resource-group $RG -o table"
```

예상 관찰 예시:

```text
00:00 replicas=1 p95=180ms
02:00 replicas=3 p95=210ms
04:00 replicas=5 p95=230ms
```

### 다중 규칙 주의점

한 앱에 HTTP와 CPU 규칙을 동시에 두면 더 큰 요구량을 만든 규칙이 실질적으로 상한을 결정합니다. 따라서 규칙을 늘리기 전에 "왜 두 규칙이 모두 필요한가"를 먼저 설명할 수 있어야 합니다.

### 비용 상한 운영

월 예산 기준이 명확하면 `maxReplicas`를 비용 계산과 연계할 수 있습니다.

- 평일 업무시간: `max=20`
- 야간/주말: `max=8`

이런 시간대 정책은 스케줄 기반 업데이트로 자동화할 수 있습니다. 비용은 아키텍처 결과가 아니라 운영 설정 결과이므로, 수치 정책을 코드화하는 것이 가장 효과적입니다.

## 실전 FAQ

### Q1. 포털에서는 정상인데 실제 응답은 불안정한 이유는 무엇일까요?

포털의 Provisioning 성공은 control plane 기준 신호입니다. 실제 사용자 품질은 data plane에서 결정됩니다. 따라서 항상 FQDN 호출 결과, revision health, system log를 함께 봐야 합니다. 운영 체크는 "설정이 저장됐는가"가 아니라 "요청이 안정적으로 처리되는가"로 마무리해야 합니다.

### Q2. `latest` 태그를 쓰면 왜 문제가 될까요?

`latest`는 사람이 보기에는 편하지만 감사/롤백/재현성에 모두 불리합니다. 같은 태그가 다른 이미지를 가리킬 수 있기 때문입니다. 프로덕션에서는 `v1.2.3` 또는 commit SHA처럼 불변 태그를 사용해야 합니다.

### Q3. 스케일과 배포를 동시에 바꾸면 어떤 위험이 있나요?

문제 원인 분리가 어려워집니다. 예를 들어 새 이미지와 새 스케일 규칙을 동시에 올리면 오류가 코드 문제인지 스케일 정책 문제인지 즉시 구분하기 어렵습니다. 안전한 팀은 배포와 스케일 변경을 분리하고, 각 변경마다 관측 지표를 따로 확인합니다.

### Q4. 멀티 서비스에서 네이밍 규칙은 어느 정도로 엄격해야 하나요?

매우 엄격해야 합니다. `orders-api--v12`처럼 서비스명과 revision suffix 패턴을 고정하면 로그, 알림, 런북 자동화가 쉬워집니다. 네이밍이 흔들리면 같은 쿼리를 서비스마다 다르게 써야 하고, 온콜 대응 속도가 느려집니다.

### Q5. 운영 문서에는 최소 무엇이 들어가야 하나요?

- 생성/변경 명령
- 예상 출력
- 실패 시 증상
- 확인할 로그 위치
- 즉시 복구 명령

이 다섯 가지를 글과 저장소 문서에 같이 유지하면, 팀 내 경험 차이가 있어도 대응 품질이 크게 흔들리지 않습니다.

## 참고용 명령 모음

```bash
# 앱 목록
az containerapp list --resource-group $RG -o table

# 단일 앱 상세
az containerapp show --name $APP --resource-group $RG -o json

# revision 목록
az containerapp revision list --name $APP --resource-group $RG -o table

# 트래픽 가중치
az containerapp ingress traffic show --name $APP --resource-group $RG -o table

# 최근 로그
az containerapp logs show --name $APP --resource-group $RG --tail 100
```

운영에서 중요한 것은 명령의 개수가 아니라 실행 순서입니다. 앱 상세 → revision 상태 → 트래픽 가중치 → 로그 순서로 보면 대부분의 이슈를 짧은 시간에 분류할 수 있습니다.

스케일 정책은 서비스 성격이 바뀌면 같이 바뀌어야 합니다. 출시 초기의 트래픽 패턴과 6개월 뒤 패턴은 거의 항상 다르기 때문에, 초기값을 그대로 두면 과소 스케일 또는 과대 비용 둘 중 하나가 발생합니다.

권장되는 방법은 월 단위 튜닝 사이클입니다. 실제 요청량, 큐 적체 시간, p95 지연 시간을 기반으로 `min/max/concurrency/messageCount`를 다시 계산합니다. 이때 변경 전후 지표를 기록해야 다음 조정에서 누적 학습이 가능합니다.

특히 worker 워크로드는 처리량 기준으로 역산해야 합니다. "메시지 1개 처리 평균 200ms" 같은 운영 숫자를 확보하면 KEDA 규칙 설정이 감이 아니라 계산으로 바뀝니다.

## 운영 메모 — 팀 합의가 필요한 항목

실제 운영에서는 기술 선택만큼 팀 합의가 중요합니다. 아래 항목은 서비스별로 값이 달라도 되지만, 같은 서비스 안에서는 반드시 고정해야 합니다.

- 배포 단위: 이미지 태그 규칙, revision suffix 규칙
- 검증 단위: healthz 통과 기준, canary 관찰 시간
- 복구 단위: 즉시 rollback 임계치, 단계적 복구 절차
- 기록 단위: 변경 이력, 영향 범위, 후속 액션

합의가 없는 상태에서는 같은 장애라도 담당자마다 전혀 다른 대응을 하게 됩니다. 반대로 합의를 문서와 자동화에 같이 넣으면, 야간 온콜에서도 대응 품질이 안정적으로 유지됩니다.

### 권장 문서 구조

1. 아키텍처 개요와 경계
2. 배포 절차와 검증 절차
3. 장애 분류와 즉시 조치
4. 모니터링 쿼리와 알림 임계치
5. 사후 분석(RCA) 템플릿

이 다섯 장이 준비되면 서비스 성숙도는 빠르게 올라갑니다. 특히 신입 엔지니어가 투입되어도 동일한 기준으로 운영할 수 있어 팀 전체의 평균 대응 시간이 짧아집니다.

## 추가 시나리오 — 예약 배치와 이벤트 버스트 혼합

야간 배치는 평소에는 0 replica로 두고, 스케줄 시작 시점에만 메시지를 밀어 넣어 처리하게 만드는 구조가 비용 효율이 높습니다. 다만 시작 직후 버스트를 흡수하려면 `maxReplicas`를 보수적으로 크게 열어 두어야 합니다.

또한 배치가 외부 API 한도에 걸리는 경우, 큐 길이만 보고 무작정 확장하면 오히려 실패율이 올라갑니다. 이때는 `messageCount`를 낮추는 대신 worker 내부 동시성을 제한해 안정적으로 처리하는 방식이 유리합니다. 스케일 규칙은 처리량 최대화가 아니라 전체 성공률 최적화 관점에서 조정해야 합니다.

스케일링 규칙을 바꿀 때는 최소 하루 이상 관찰 창을 두는 편이 좋습니다. 업무 시간과 야간 시간의 트래픽 패턴이 다르기 때문입니다. 단기 테스트만으로는 큐 적체나 외부 의존성 병목이 드러나지 않을 수 있으므로, 실제 운영 데이터로 재검증해야 합니다.

추가로, 배포 직후 5분과 30분 지표를 모두 확인해야 단기 이상과 장기 이상을 구분할 수 있습니다.

## 체크리스트

- [ ] 내 워크로드에 맞는 트리거 범주(HTTP / TCP / custom)를 골랐습니까?
- [ ] `min-replicas`가 우리 서비스의 cold-start 허용치와 맞습니까?
- [ ] `max-replicas`로 비용 상한을 설정했습니까?
- [ ] custom scaler라면 `--scale-rule-auth`와 secret을 연결했습니까?
- [ ] 큐 worker가 이벤트 기반 scaler를 사용하고 있습니까?
- [ ] Application Insights 또는 Log Analytics에서 replica 수를 모니터링하고 있습니까?

## 연습 문제

1. 평균 동시성 30, 피크 200인 REST API가 있다면 `min`, `max`, `http-concurrency`를 어떻게 잡겠습니까? 각각 이유를 써 보세요.
2. Service Bus 큐에 메시지 1000개가 쌓였는데 worker replica는 10개뿐입니다. 그럴듯한 원인 세 가지를 적어 보세요.
3. CPU 기반 scaler에 `min-replicas 0`을 주면 무슨 일이 생길까요? 왜 그럴까요?

## 정리

- ACA 스케일링은 선언형 Signal → Rule → Bounds 파이프라인으로 이해하면 됩니다.
- HTTP와 TCP는 내장 규칙이고, 나머지는 custom KEDA scaler입니다.
- Scale-to-zero는 유휴 비용을 거의 0으로 만들지만 cold start를 가져옵니다.
- `min-replicas`와 `max-replicas`는 동시에 비용 정책이자 SLO 정책입니다.

다음 글에서는 **Dapr 통합**을 다룹니다. 사이드카를 붙이면 service invocation, pub/sub, state store 같은 분산 시스템 구성요소를 라이브러리 종속성 없이 어떻게 가져올 수 있는지 보겠습니다.

---

## 처음 질문으로 돌아가기

- **Azure Container Apps는 선언형 스케일링 신호를 바탕으로 replica 수를 어떻게 결정할까요?**
  - 본문의 기준은 스케일링 — KEDA scaler와 zero-to-N를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **내장 HTTP/TCP 규칙과 사용자 정의 KEDA scaler의 차이는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`min-replicas 0`(scale-to-zero)는 언제 안전하고, 언제 위험할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Azure Container Apps 101 (4/7): Ingress와 트래픽 분할 — revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- **Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N (현재 글)**
- Azure Container Apps 101 (6/7): Dapr 통합 — 사이드카로 얻는 것 (예정)
- Azure Container Apps 101 (7/7): 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Scaling in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [KEDA scalers documentation](https://keda.sh/docs/scalers/)
- [Azure Service Bus scaler — KEDA](https://keda.sh/docs/scalers/azure-service-bus/)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/05-scaling-with-keda)

Tags: Azure, Container Apps, Serverless, Containers
