# Hosting Models: 어떤 플랜을 선택해야 할까?

> Azure App Service 101 시리즈 (3/7)

App Service를 시작하면 첫 번째로 마주치는 질문: **"어떤 플랜을 선택해야 하지?"**

Free? Basic? Standard? Premium? 그리고 Windows vs Linux? Code vs Container?

이 글에서는 **Hosting Model 선택의 핵심 기준**을 정리해 드립니다.

---

## 결정 흐름도

App Service 호스팅 전략을 결정하는 흐름:

```
1. OS 선택 (Linux / Windows)
   ↓
2. 배포 모델 선택 (Code / Container)
   ↓
3. 플랜 티어 선택 (Dev → Production)
```

![IMAGE: Hosting Model 결정 플로우차트]
`📸 캡처: 결정 흐름도 (draw.io로 그리기)`

---

## App Service Plan이란?

App Service Plan은 앱이 실행되는 **컴퓨팅 리소스 풀**입니다.

### Plan이 정의하는 것

| 항목 | 설명 |
|------|------|
| CPU/Memory | 인스턴스당 사용 가능한 리소스 |
| 최대 인스턴스 수 | Scale out 한계 |
| 기능 세트 | Autoscale, Slots, VNet 등 |
| 가격 및 SLA | 비용과 가용성 보장 |

### 핵심: 하나의 Plan = 여러 앱

같은 Plan에 여러 앱을 배포하면 **컴퓨팅 리소스를 공유**합니다.

```
[App Service Plan: Standard S1]
├── Web App A
├── Web App B  
└── API App C   ← 모두 같은 VM 풀 공유
```

![IMAGE: App Service Plan 개요 화면]
`📸 캡처: Azure Portal → App Service Plans → 특정 Plan 선택 → Overview`

---

## 플랜 티어 비교

### 티어별 특징

| 티어 | 용도 | 주요 제한 |
|------|------|----------|
| **Free/Shared** | 학습, 실험 | 리소스 공유, 기능 제한 |
| **Basic** | 저트래픽 | 고급 기능 없음 |
| **Standard** | 기본 프로덕션 | 중간 스케일 한계 |
| **Premium** | 고성능, 네트워킹 | 높은 비용 |
| **Isolated** | 규정 준수, 네트워크 격리 | 최고 비용, 복잡성 |

### 기능별 티어 요구사항

| 기능 | 최소 티어 |
|------|----------|
| Custom Domain | Shared |
| SSL 인증서 | Basic |
| Deployment Slots | Standard |
| Autoscale | Standard |
| VNet Integration | Standard |
| Private Endpoint | Premium |
| Zone Redundancy | Premium |

### 💡 실전 조언

> "프로덕션은 최소 Standard부터 시작하세요. Autoscale과 Deployment Slots 없이 운영하면 사고가 납니다."

![IMAGE: App Service Plan 가격 비교 화면]
`📸 캡처: Azure Portal → App Service Plan → Scale up (App Service plan) 화면`

---

## OS 선택: Linux vs Windows

### 어떤 OS를 선택할까?

| 고려사항 | 설명 |
|---------|------|
| 기존 운영 표준 | 팀이 익숙한 환경 |
| 의존성 호환성 | 특정 라이브러리 요구사항 |
| 컴플라이언스 | 기업 보안 정책 |
| 툴링/관측성 | 디버깅 워크플로 |

### 실제 차이점

| 측면 | Linux | Windows |
|------|-------|---------|
| 시작 속도 | 일반적으로 빠름 | 약간 느림 |
| 컨테이너 지원 | 네이티브 | 제한적 |
| Kudu/SCM | 제한적 기능 | 풍부한 기능 |
| 비용 | 동일 티어에서 동일 | 동일 |

**권장:** 특별한 이유가 없다면 **Linux** 선택 (모던 스택에 적합)

```bash
# Linux Plan 생성
az appservice plan create \
    --resource-group $RG \
    --name $PLAN_NAME \
    --location koreacentral \
    --sku S1 \
    --is-linux
```

![IMAGE: App Service Plan 생성 화면에서 OS 선택]
`📸 캡처: Azure Portal → Create App Service Plan → Operating System 선택`

---

## 배포 모델: Code vs Container

### Code 기반 배포

플랫폼이 런타임을 제공하고, 코드만 배포합니다.

**장점:**
- ✅ 빠른 온보딩
- ✅ 컨테이너 관리 부담 없음
- ✅ 플랫폼 통합 강력

**단점:**
- ❌ 베이스 이미지 제어 불가
- ❌ 런타임 업데이트가 플랫폼 정책 따름

```bash
# Code 기반 웹앱 생성
az webapp create \
    --resource-group $RG \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --runtime "PYTHON|3.11"
```

### Container 기반 배포

OCI 이미지를 직접 빌드하고 배포합니다.

**장점:**
- ✅ 런타임 스택 완전 제어
- ✅ 로컬-클라우드 환경 일관성
- ✅ OS 레벨 의존성 자유

**단점:**
- ❌ 패치 주기 직접 관리
- ❌ 레지스트리 거버넌스 필요
- ❌ 이미지 품질이 시작 성능에 직접 영향

```bash
# Container 기반 웹앱 생성
az webapp create \
    --resource-group $RG \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --deployment-container-image-name myregistry.azurecr.io/myapp:latest
```

![IMAGE: Web App 생성 시 Publish 옵션]
`📸 캡처: Azure Portal → Create Web App → Publish: Code vs Docker Container`

---

## 공유 Plan vs 전용 Plan

### 공유 Plan 전략

여러 앱을 하나의 Plan에 배치:

**장점:**
- 비용 효율적
- 트래픽 패턴이 다른 앱들끼리 리소스 상호보완

**단점:**
- 앱 간 리소스 경쟁 (Noisy Neighbor)
- 하나의 앱 문제가 다른 앱에 영향

### 전용 Plan 전략

중요한 앱마다 별도 Plan:

**장점:**
- 리소스 격리
- 용량 예측 용이
- Blast Radius 제한

**단점:**
- 비용 증가

### 💡 권장 접근법

```
비즈니스 크리티컬 앱 → 전용 Plan
내부 도구, 낮은 트래픽 앱 → 공유 Plan
```

![IMAGE: 여러 앱이 같은 Plan에 있는 화면]
`📸 캡처: Azure Portal → App Service Plan → Apps 탭`

---

## 기능 매핑

어떤 기능이 Plan에 의존하고, 어떤 기능이 배포 모델에 의존하는지:

| 기능 | Plan 의존 | 배포 모델 의존 |
|------|----------|---------------|
| Autoscale | ✅ | ❌ |
| Deployment Slots | ✅ | ❌ |
| Private Endpoint | ✅ | ❌ |
| VNet Integration | ✅ | ❌ |
| Custom Startup Image | ❌ | ✅ (Container) |
| Platform Build | ❌ | ✅ (Code) |

---

## 비용 및 용량 계획

### 용량 계획 시 고려사항

| 항목 | 질문 |
|------|------|
| 트래픽 | 피크 vs 평균 요청률? |
| 리소스 | CPU 집약 vs IO 집약? |
| 메모리 | 요청당 메모리, 백그라운드 워커? |
| 시작 시간 | Cold start 빈도? |

### 실전 패턴

```
1. 프로덕션 가능 티어로 시작 (Standard 이상)
2. 실제 트래픽 패턴으로 부하 테스트
3. Autoscale 임계값과 쿨다운 설정
4. 월별로 Plan 크기 재평가
```

### CLI로 Plan 정보 확인

```bash
az appservice plan show \
    --resource-group $RG \
    --name $PLAN_NAME \
    --query "{sku:sku, workers:numberOfWorkers, reserved:reserved}" \
    --output json
```

**출력 예시:**
```json
{
  "sku": {
    "name": "S1",
    "tier": "Standard",
    "capacity": 2
  },
  "workers": 2,
  "reserved": true
}
```

![IMAGE: App Service Plan의 Scale up 화면]
`📸 캡처: Azure Portal → App Service Plan → Scale up (App Service plan)`

---

## Bicep 예시: 재현 가능한 인프라

```bicep
param location string = resourceGroup().location
param planName string
param appName string

// App Service Plan
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: {
    name: 'S1'
    tier: 'Standard'
    capacity: 1
  }
  properties: {
    reserved: true  // Linux
  }
}

// Web App
resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
  }
}
```

![IMAGE: Bicep 배포 결과 화면]
`📸 캡처: Azure Portal → Resource Group → 배포된 리소스들`

---

## Right-Sizing 체크리스트

Plan을 선택하기 전에 확인하세요:

| 질문 | 확인 |
|------|------|
| 필요한 네트워킹 기능을 지원하는가? | ☐ |
| 필요한 배포 패턴을 지원하는가? (Slots) | ☐ |
| Autoscale이 포화 전에 반응하는가? | ☐ |
| 피크 시 인스턴스당 메모리가 충분한가? | ☐ |
| 의존성 서비스가 증가된 부하를 감당하는가? | ☐ |

---

## 정리

Hosting Model 선택의 핵심:

- **OS**: 특별한 이유 없으면 Linux
- **배포 모델**: 시작은 Code, 제어 필요시 Container
- **티어**: 프로덕션은 Standard 이상
- **Plan 전략**: 크리티컬 앱은 전용, 나머지는 공유

다음 글에서는 실제로 **Python Flask 앱을 Azure에 배포**하는 과정을 단계별로 진행합니다.

---

## 시리즈 목차

1. Azure App Service란? - 플랫폼 아키텍처 이해하기
2. Request Lifecycle: 요청이 앱에 도달하기까지
3. **[현재 글] Hosting Models: 어떤 플랜을 선택해야 할까?**
4. 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)
5. Configuration 마스터하기: App Settings & 환경변수
6. 로그와 모니터링 기초
7. Scaling 101: 언제 Scale Up vs Scale Out?

---

## 참고 자료

- [App Service plan overview (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview-hosting-plans)
- [Custom container in App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/tutorial-custom-container)
- [App Service pricing (Azure)](https://azure.microsoft.com/pricing/details/app-service/)

---

**태그:** `Azure` `App Service` `Cloud` `Pricing` `DevOps`
