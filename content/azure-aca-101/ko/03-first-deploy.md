---
title: "Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI"
series: azure-aca-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- FastAPI
- ACR
- Dockerfile
- az containerapp
last_reviewed: '2026-05-12'
seo_description: ACA의 첫 배포는 택시를 부르기 전에 출발지가 있어야 한다는 비유로 이해할 수 있습니다.
---

# Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI

첫 배포는 ACA가 다이어그램에서 운영 모델로 바뀌는 순간입니다. 이미지를 밀어 넣고, 의존성을 연결하고, Revision이 살아나는 과정을 직접 봐야 비로소 서비스 경계가 손에 잡힙니다.

이 글은 Azure Container Apps 101 시리즈의 3번째 글입니다. 여기서는 Python/FastAPI 앱을 그 전체 경로로 직접 통과시켜 보겠습니다.

![Azure Container Apps 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/03/03-01-the-end-to-end-path.ko.png)
*Azure Container Apps 101 3장 흐름 개요*
> 첫 배포하기 — Python/FastAPI의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 로컬 FastAPI 코드가 실제 ACA Revision으로 살아나기까지의 전체 경로는 어떻게 될까요?
- ACA가 이미지를 직접 빌드해 주지 않는다는 사실은 책임 분담에 어떤 의미를 가질까요?
- ACR → ACA Environment → Container App → Revision이라는 네 단계 의존성 체인은 어떻게 이어질까요?

## 왜 이 글이 중요한가

"hello world를 한 번 띄워 봤다"는 경험은 ACA를 머리로 이해하는 단계와 손으로 이해하는 단계를 가르는 선입니다. 첫 실제 배포를 하고 나면 아래 질문에 자기 답을 갖게 됩니다.

- ACA의 책임은 어디서 시작하고 어디서 끝날까요? (이미지 빌드는 ACA 책임이 아닙니다.)
- 왜 ACR 같은 레지스트리가 필수일까요? (ACA는 이미지 참조만 소비합니다.)
- 비용은 언제부터 실제로 시작될까요? (Environment 생성 시점과 Revision 실행 시점입니다.)
- 어떤 신호가 배포 성공을 증명할까요? (FQDN 응답과 Revision health입니다.)

이 글은 그 경로를 처음부터 끝까지 이어 줍니다.

## 멘탈 모델

> ACA의 첫 배포는 택시를 부르는 일과 비슷합니다. 택시가 출발하려면 먼저 출발지가 있어야 합니다.

택시(ACA)는 승객(이미지)을 목적지까지 데려다줄 수 있지만, 승객이 기다리고 있지 않으면 출발할 수 없습니다. 승객은 어딘가(레지스트리)에 먼저 서 있어야 하고, 택시에게 그 주소(이미지 참조)를 알려줘야 합니다.

그래서 첫 배포는 image build → registry push → ACA가 그 이미지를 가리키는 Revision 생성이라는 순서로 흐릅니다. 한 단계를 빼면 다음 단계는 일어나지 않습니다.

## 경로를 먼저 보기

경로를 먼저 보면 배포가 훨씬 단순해집니다.

핵심 의존성은 다음 네 가지입니다.

1. **Resource group** — 모든 Azure 리소스를 담는 컨테이너
2. **ACR** — 이미지가 보관되는 곳(또는 다른 OCI 레지스트리)
3. **ACA Environment** — Revision이 실제로 실행되는 경계
4. **Container App + Revision** — 이미지 참조 + 설정 = 실행 인스턴스

## 핵심 개념 — ACA가 하지 않는 일

| 책임 | 소유자 |
|---|---|
| Source code → image build | **Developer / CI** (ACA가 하지 않음) |
| Image storage | **ACR or external registry** (ACA가 하지 않음) |
| Image pull credentials | ACA (managed identity를 통해) |
| Container execution and restart | ACA |
| Ingress, TLS termination | ACA |
| 0-to-N scaling | ACA |
| Log shipping | ACA (to Log Analytics) |

이 표를 한 번만 정확히 외우면 "왜 안 되지?"의 90%는 사라집니다. ACA는 이미지를 빌드해 주지 않습니다.

## 적용 전후 비교
**Before — ACA가 빌드도 해 줄 거라고 가정하는 경우**

```bash
# Pointing at code does not work in general - ACA does not do source builds
az containerapp create \
  --name myapi \
  --source ./my-fastapi-folder   # ← only works in some scenarios via containerapp up + Buildpacks
```

`az containerapp up`는 내부적으로 buildpacks를 호출하기는 합니다. 하지만 프로덕션 CI/CD에서는 명시적인 build → push → deploy 분리가 표준입니다.

**After — 빌드, 푸시, 배포를 명시적으로 분리하는 경우**

```bash
az acr build --registry $ACR_NAME --image fastapi-hello:v1 .
az containerapp create --name myapi --image $ACR_NAME.azurecr.io/fastapi-hello:v1 ...
```

이 방식에서는 이미지 태그가 "무엇이 배포되었는가"의 정체성이 되므로, 추적, rollback, 감사가 모두 깔끔해집니다.

## 실습

### 단계 0. 변수와 CLI 준비

```bash
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

RG="rg-aca-101-demo"
LOCATION="eastus"
ACA_ENV="aca-env-101-demo"
ACR_NAME="aca101demo$RANDOM"
APP_NAME="fastapi-aca-demo"
IMAGE="$ACR_NAME.azurecr.io/fastapi-hello:v1"
```

### 단계 1. FastAPI 앱과 Dockerfile

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello from azure container apps"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt`에는 최소한 `fastapi`와 `uvicorn[standard]`가 들어 있어야 합니다.

### 단계 2. Resource group과 ACR

```bash
az group create --name $RG --location $LOCATION
az acr create --name $ACR_NAME --resource-group $RG --location $LOCATION --sku Basic
```

### 단계 3. 이미지 빌드 & 푸시(한 명령)

```bash
az acr build --registry $ACR_NAME --image fastapi-hello:v1 .
```

`az acr build`는 소스를 ACR로 보내고, 클라우드에서 빌드하고, 푸시까지 끝냅니다. 로컬 Docker daemon이 필요 없습니다.

### 단계 4. ACA Environment 만들기

```bash
az containerapp env create \
  --name $ACA_ENV \
  --resource-group $RG \
  --location $LOCATION
```

Environment는 네트워크, 로그 목적지, 선택적 통합(Dapr 등)을 공유하는 경계입니다. 이 명령은 2-3분 정도 걸립니다.

### 단계 5. 첫 Container App + Revision 만들기

```bash
az containerapp create \
  --name $APP_NAME \
  --resource-group $RG \
  --environment $ACA_ENV \
  --image $IMAGE \
  --ingress external \
  --target-port 8000 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 3
```

이 한 명령이 (1) Container App 생성, (2) 첫 Revision 생성, (3) ingress + TLS 자동 연결, (4) scale-to-zero 활성화를 한 번에 처리합니다.

### 단계 6. CLI에서 배포 검증하기

```bash
# Get the FQDN
FQDN=$(az containerapp show --name $APP_NAME --resource-group $RG \
  --query properties.configuration.ingress.fqdn --output tsv)
echo "https://$FQDN"

# Hit it
curl https://$FQDN/
curl https://$FQDN/healthz

# Check Revision status
az containerapp revision list --name $APP_NAME --resource-group $RG \
  --query "[].{name:name, active:properties.active, healthState:properties.healthState}" \
  --output table
```

`healthState: Healthy`가 보이면 성공입니다.

## 자주 하는 실수

### 실수 1. `target-port`가 컨테이너가 실제로 듣는 포트와 맞지 않는 경우

ACA의 `--target-port`는 컨테이너가 실제로 listen하는 포트와 같아야 합니다. Dockerfile은 `8000`에서 뜨는데 `--target-port 80`을 넘기면 ingress는 응답을 받지 못합니다.

### 실수 2. 이미지가 ACR에 올라가기 전에 `az containerapp create`를 먼저 실행하는 경우

순서가 중요합니다. Step 3(이미지 푸시)이 끝나야 Step 5(앱 생성)가 이미지를 pull할 수 있습니다. 그렇지 않으면 Revision이 `ImagePullBackOff`와 비슷한 상태로 뜨지 못합니다.

### 실수 3. ACR pull 권한을 준비하지 않는 경우

같은 구독 안에서는 `az containerapp create`가 보통 system-assigned managed identity를 만들고 `AcrPull`을 자동으로 부여합니다. 그렇지 않은 경우(교차 구독, 외부 레지스트리)에는 `--registry-server`, `--registry-username`, `--registry-password` 또는 managed identity를 직접 지정해야 합니다.

### 실수 4. `min-replicas 0`인데 health probe가 드물거나 무거운 경우

Scale-to-zero는 첫 요청에 cold start를 만듭니다. `/healthz`가 무겁거나 시작이 느리면 ingress가 timeout에 걸릴 수 있습니다. 첫 배포 검증 단계에서는 잠시 `--min-replicas 1`로 두는 것도 괜찮습니다.

### 실수 5. 포털의 "Provisioning succeeded"에서 멈추는 경우

Provisioning 성공은 control plane 응답일 뿐, 애플리케이션이 건강하다는 뜻은 아닙니다. 항상 Revision `healthState`와 실제 엔드포인트 응답까지 확인해야 합니다.

## 실무에서는 이렇게 생각한다

프로덕션 첫 배포 체크리스트는 보통 이렇게 정리됩니다.

- 이미지 태그가 불변인가? `:latest`는 쓰지 않습니다. `:v1`, `:sha-abc123`처럼 명시적인 태그를 씁니다.
- 빌드 환경이 재현 가능한가? `az acr build`는 ACR 안에서 일회성 빌드 에이전트를 띄우므로 재현성 측면에서 유리합니다.
- 환경 변수와 secret이 분리돼 있는가? Secret은 `--secrets`, 일반 설정은 `--env-vars`로 나눕니다.
- 첫 배포 비용이 보이는가? Log Analytics 비용은 Environment를 만드는 순간부터 시작됩니다.
- rollback 경로가 명확한가? 다른 이미지 태그로 Step 5를 다시 실행하면 새 Revision이 생기고, Multiple mode에서는 가중치를 나눌 수 있습니다.

## 배포 자동화 — CLI 출력 해석과 IaC 연결

첫 배포를 반복 가능한 운영 경로로 바꾸려면, 명령 결과를 사람이 읽는 수준에서 멈추지 말고 파이프라인 입력으로 연결해야 합니다.

### az CLI 출력에서 꼭 뽑아야 할 값

```bash
az containerapp show --name $APP_NAME --resource-group $RG \
  --query "{fqdn:properties.configuration.ingress.fqdn,latestRevision:properties.latestRevisionName,provisioning:properties.provisioningState}" \
  --output json
```

예상 출력:

```json
{
  "fqdn": "fastapi-aca-demo.<hash>.eastus.azurecontainerapps.io",
  "latestRevision": "fastapi-aca-demo--v1",
  "provisioning": "Succeeded"
}
```

`provisioning=Succeeded`만으로는 충분하지 않습니다. `latestRevision`이 active인지까지 확인해야 배포 완료입니다.

```bash
az containerapp revision list --name $APP_NAME --resource-group $RG \
  --query "[?name=='$APP_NAME--v1'].{active:properties.active,health:properties.healthState}" \
  --output table
```

### Bicep으로 배포 단계 고정

```bicep
param appName string
param envId string
param image string
param registry string

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: resourceGroup().location
  identity: { type: 'SystemAssigned' }
  properties: {
    managedEnvironmentId: envId
    configuration: {
      registries: [
        {
          server: registry
          identity: 'system'
        }
      ]
      ingress: { external: true, targetPort: 8000 }
    }
    template: {
      containers: [
        { name: 'api', image: image, resources: { cpu: 0.5, memory: '1.0Gi' } }
      ]
      scale: { minReplicas: 1, maxReplicas: 5 }
    }
  }
}
```

### 실패 재현 시나리오와 확인 포인트

- 이미지 태그 오타: revision이 `Failed`로 남고 `ImagePull` 관련 시스템 로그가 발생합니다.
- 포트 불일치: revision은 생성되지만 ingress health probe 실패가 반복됩니다.
- ACR 권한 누락: `AcrPull` role assignment가 없는 경우 pull 단계에서 중단됩니다.

실제 운영에서는 이 세 가지가 첫 배포 실패의 대부분을 차지합니다. 배포 문서에 명시해 두면 온콜 대응 시간이 크게 줄어듭니다.

## 파이프라인 템플릿 — Build/Push/Deploy 분리

로컬 실습이 끝나면 바로 CI/CD로 옮겨야 합니다. 첫 배포를 사람 손으로만 반복하면 태그 오염, 순서 누락, 롤백 지연이 거의 반드시 발생합니다.

### GitHub Actions 단계 예시

```yaml
name: deploy-aca
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Build and Push
        run: |
          az acr build --registry $ACR_NAME --image fastapi-hello:${{ github.sha }} .
      - name: Deploy
        run: |
          az containerapp update \
            --name $APP_NAME \
            --resource-group $RG \
            --image $ACR_NAME.azurecr.io/fastapi-hello:${{ github.sha }} \
            --revision-suffix sha-${{ github.sha }}
      - name: Verify
        run: |
          az containerapp revision list --name $APP_NAME --resource-group $RG -o table
```

핵심은 이미지 태그를 `github.sha`로 고정하는 것입니다. 이 한 줄이 배포 추적성과 롤백 가능성을 동시에 보장합니다.

### 배포 후 자동 검증 항목

```bash
FQDN=$(az containerapp show --name $APP_NAME --resource-group $RG \
  --query properties.configuration.ingress.fqdn -o tsv)

curl --fail --max-time 10 https://$FQDN/healthz
```

추가로 다음을 확인하면 배포 신뢰성이 올라갑니다.

- 새 revision `healthState=Healthy`
- 오류 로그 급증 없음
- p95 latency 기준 이내

### Bicep + CLI 혼합 전략

- Environment/로그/네트워크: Bicep(드문 변경)
- 이미지 업데이트/트래픽: CLI(빈번 변경)

이 전략은 infra drift를 줄이면서도 배포 속도를 유지합니다. 모든 것을 CLI로 처리하면 환경 일관성이 깨지고, 모든 것을 Bicep로 처리하면 배포 회전 속도가 과도하게 느려질 수 있습니다.

### 운영 기록 예시

배포 노트에 최소한 아래를 남깁니다.

- commit SHA
- 이미지 태그
- revision 이름
- 배포 시작/종료 시간
- 검증 결과(healthz, 오류율)

이 기록은 장애 분석에서 "언제 무엇이 바뀌었는가"를 분 단위로 복원하는 기준점이 됩니다.

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

첫 배포 문서를 작성할 때는 성공 경로만 적으면 안 됩니다. 실패 경로를 같이 적어야 진짜 운영 문서가 됩니다. 예를 들어 이미지 pull 실패, 포트 불일치, 권한 누락은 각각 로그 위치와 해결 명령이 다르므로 표로 정리해 두는 것이 좋습니다.

또한 배포 직후 자동 검증을 반드시 기계화해야 합니다. 사람이 브라우저로 한 번 열어 보는 방식은 재현성이 낮고, 야간 배포에서는 사실상 검증 누락으로 이어집니다. healthz 호출, revision health 확인, 기본 KQL 조회를 파이프라인 마지막 단계에 넣어 두면 배포 신뢰도가 크게 올라갑니다.

배포 성숙도의 핵심은 "누가 실행해도 같은 결과"입니다. build/push/deploy/verify가 고정된 순서로 반복되면, 팀은 배포 자체보다 제품 품질에 집중할 수 있습니다.

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

## 체크리스트

- [ ] image build → push → deploy의 책임 분담을 설명할 수 있습니다
- [ ] `--target-port`가 Dockerfile의 EXPOSE/CMD와 어떻게 맞아야 하는지 알고 있습니다
- [ ] CLI에서 FQDN을 가져와 실제 응답을 확인했습니다
- [ ] CLI에서 Revision `healthState`를 확인하는 방법을 알고 있습니다
- [ ] 이미지 태그를 불변으로 관리해야 하는 이유를 설명할 수 있습니다

## 연습 문제

1. Step 1-6을 그대로 따라 배포해 보세요. 그런 다음 `app/main.py`의 응답 메시지를 바꾸고, 이미지 태그 `:v2`로 build/push한 뒤 앱을 업데이트해서 `az containerapp revision list`에 새 Revision이 생겼는지 확인해 보세요.
2. `--min-replicas 0` 상태에서 앱을 5분 동안 유휴 상태로 두고 첫 요청의 지연 시간을 측정해 보세요. 그다음 `--min-replicas 1`로 바꾼 뒤 같은 실험을 반복해서 cold start 차이를 확인해 보세요.

## 정리

- ACA는 이미지 빌드의 소유자가 아닙니다. 그 일은 개발자나 CI의 책임입니다.
- 첫 배포 흐름은 RG → ACR → image build/push → Environment → Container App + Revision입니다.
- `az containerapp create` 한 번으로 (1) App, (2) 첫 Revision, (3) ingress + TLS, (4) scaling이 연결됩니다.
- 검증은 포털의 "Provisioning succeeded"가 아니라 **Revision healthState + FQDN 응답**으로 해야 합니다.
- 추적과 rollback을 위해 이미지 태그는 반드시 불변(`:v1`, `:sha-abc123`)이어야 합니다.

다음 글에서는 ingress와 트래픽 분할을 깊게 다룹니다. 두 개의 Revision을 만들고 90/10 canary를 실습한 뒤, 문제가 생기면 100/0으로 즉시 되돌리는 과정을 직접 해 봅니다.

## 처음 질문으로 돌아가기

- **로컬 FastAPI 코드가 실제 ACA Revision으로 살아나기까지의 전체 경로는 어떻게 될까요?**
  - 본문의 기준은 첫 배포하기 — Python/FastAPI를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **ACA가 이미지를 직접 빌드해 주지 않는다는 사실은 책임 분담에 어떤 의미를 가질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **ACR → ACA Environment → Container App → Revision이라는 네 단계 의존성 체인은 어떻게 이어질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- **Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI (현재 글)**
- Azure Container Apps 101 (4/7): Ingress와 트래픽 분할 — revision 기반 배포 전략 (예정)
- Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N (예정)
- Azure Container Apps 101 (6/7): Dapr 통합 — 사이드카로 얻는 것 (예정)
- Azure Container Apps 101 (7/7): 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Quickstart: Deploy your first container app with containerapp up — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/get-started)
- [az containerapp create — Microsoft Learn](https://learn.microsoft.com/en-us/cli/azure/containerapp#az-containerapp-create)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Run containers from any registry — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/containers)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/03-first-deploy)

Tags: Azure, Container Apps, Serverless, Containers
