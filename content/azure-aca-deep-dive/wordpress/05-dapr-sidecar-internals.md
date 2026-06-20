---
title: "바이브코딩을 위한 Azure Container Apps 심화 (5/6): Dapr 사이드카 내부"
series: azure-aca-deep-dive
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps심화
- Dapr
- 사이드카
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 심화 5편: Dapr 사이드카 내부. Dapr를 켤 때 daprd 프로세스가 컨테이너 옆에 붙는 원리와 localhost 포트, component scope를 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps 심화 (5/6): Dapr 사이드카 내부

이 글은 바이브코딩을 위한 Azure Container Apps 심화 시리즈의 5번째 글입니다.

Azure Container Apps에서 Dapr를 처음 켜면 기능이 아주 가볍게 보입니다. 앱 ID 몇 개를 적고, 포트를 지정하면 서비스가 갑자기 localhost:3500으로 Dapr API를 부르기 시작합니다. 겉으로는 체크박스 하나를 켠 것 같지만, 런타임에서는 훨씬 큰 변화가 일어납니다. 실제로는 upstream Dapr sidecar runtime인 daprd 계열 프로세스가 사용자 컨테이너 옆에 붙습니다. Dapr enablement는 앱에 메타데이터를 하나 더 붙이는 일이 아니라, Pod의 런타임 형태 자체를 바꾸는 일입니다. Dapr를 켠 순간부터는 애플리케이션 하나가 아니라 두 개의 협력 프로세스를 운영하게 됩니다. localhost 호출 성공은 바깥 의존성 경로 성공과 같은 뜻이 아니고, sidecar readiness는 앱 readiness와 얽혀 있으며, sidecar 로그는 앱 로그와 별개의 증거입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Dapr 장애 진단 코드를 요청할 때 sidecar 프로세스와 앱 프로세스를 분리해서 명시하지 않으면, 앱 로그만 확인하고 sidecar 부팅 실패를 놓치는 코드가 생성되기 때문입니다.

> Dapr 사이드카 내부의 핵심은 daprd 프로세스가 별도 런타임이며, localhost:3500과 component scope가 운영 계약임을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ACA에서 Dapr를 켠다는 것은 런타임에 정확히 무엇이 추가된다는 뜻일까요?
- sidecar injection은 어떤 upstream 모델로 이해하는 편이 가장 정확할까요?
- localhost 포트 3500, 50001은 왜 중요한 운영 계약일까요?
- sidecar 로그는 어디서 확인하고 앱 로그와 어떻게 구분할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Dapr 사이드카 내부를 이해하면 AI에게 "Dapr 장애 진단 시 앱 컨테이너 로그와 Dapr sidecar 로그를 각각 ContainerAppConsoleLogs_CL에서 분리해서 조회하는 KQL 쿼리와 sidecar 부팅 확인 방법"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Dapr pub/sub 호출이 실패하는데 원인 찾는 방법?"
→ 앱 코드 버그로 가정
→ 앱 로그만 확인
→ sidecar 상태, component scope 미확인
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Dapr 장애를 두 프로세스 관점에서 진단해줘.
    1) sidecar 부팅 확인:
       ContainerAppConsoleLogs_CL에서 ContainerName='daprd' 필터
    2) component scope 확인:
       az containerapp env dapr-component list로 scope 검증
    3) localhost:3500 연결 확인:
       앱 컨테이너에서 curl localhost:3500/v1.0/healthz 결과
    4) backing service 연결:
       sidecar 로그에서 Service Bus 연결 오류 확인"
→ 앱 프로세스와 sidecar 프로세스 분리 진단
→ component scope 설정 오류 조기 발견
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Dapr 장애를 앱 코드 문제로만 봄 | sidecar 부팅 실패가 앱 코드 수정으로 해결 안 됨 | sidecar 로그를 앱 로그와 별개로 확인 |
| localhost:3500 성공을 backing service 성공으로 오해 | sidecar API는 응답해도 backing service 연결 실패 가능 | sidecar 로그에서 backing service 연결 오류 확인 |
| component를 앱 수준에서 설정 시도 | component는 Environment 수준에서 등록됨 | az containerapp env dapr-component set 사용 |
| dapr-app-port 미설정 | sidecar가 앱으로 콜백할 포트를 모름 | --dapr-app-port를 앱 실제 포트와 동일하게 설정 |
| sidecar readiness와 앱 readiness 혼동 | 앱이 응답해도 sidecar가 준비 안 된 상태일 수 있음 | 둘을 별개 probe로 설정 |

## AI 협업 팁

Dapr 사이드카 관련 효과적인 AI 프롬프트 패턴:

1. **sidecar 로그 조회 요청**: "Log Analytics에서 Dapr sidecar(daprd) 컨테이너 로그만 필터링해서 조회하는 KQL 쿼리 작성해줘"
2. **sidecar 부팅 확인 요청**: "ACA 앱의 Dapr sidecar가 정상 부팅됐는지 확인하는 방법과 명령 작성해줘"
3. **component scope 검증 요청**: "ACA Environment의 Dapr component list를 조회하고 특정 앱이 component scope에 포함됐는지 확인하는 az CLI 명령 작성해줘"

예시 프롬프트:
> "ACA Dapr 장애 진단 플레이북을 작성해줘. 1) sidecar 부팅 로그 KQL 2) localhost:3500/healthz 확인 명령 3) component scope 검증 명령 4) backing service 연결 오류 KQL. 각 단계에서 앱 프로세스와 sidecar 프로세스를 분리해서 확인."

## 운영 체크리스트

- [ ] Dapr 장애 진단 시 sidecar 로그를 앱 로그와 별개로 확인하는가?
- [ ] dapr-app-port를 앱 실제 포트와 동일하게 설정했는가?
- [ ] component를 Environment 수준에 등록했는가?
- [ ] localhost:3500 성공이 backing service 성공과 다름을 이해했는가?
- [ ] 다음 글에서 Envoy Ingress 경로를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Dapr 사이드카 내부를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. sidecar 프로세스와 앱 프로세스를 분리해서 명시한 사람과 그렇지 않은 사람이 AI에게 받는 Dapr 장애 진단 코드의 완성도는 크게 다릅니다.

## 정리

Dapr 사이드카 내부 편은 바이브코딩을 위한 Azure Container Apps 심화에서 사이드카 런타임을 이해하는 핵심 단계입니다. daprd 프로세스가 별도 런타임이고, localhost:3500과 component scope가 운영 계약이며, sidecar 로그를 앱 로그와 분리해서 진단해야 함을 이해했습니다. 다음 글에서는 Envoy Ingress 경로와 첫 요청이 컨테이너에 닿는 과정을 다룹니다.

## 참고 자료

- [Dapr integration in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/dapr-overview)
- [Dapr component scopes](https://docs.dapr.io/operations/components/component-scopes/)
- [daprd runtime](https://docs.dapr.io/concepts/dapr-services/sidecar/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-deep-dive/ko/05-dapr-sidecar-internals)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps 심화 (1/6): ACA 아키텍처
- 바이브코딩을 위한 Azure Container Apps 심화 (2/6): Environment 내부
- 바이브코딩을 위한 Azure Container Apps 심화 (3/6): Revision과 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps 심화 (4/6): ACA 안의 KEDA
- **바이브코딩을 위한 Azure Container Apps 심화 (5/6): Dapr 사이드카 내부 (현재 글)**
- 바이브코딩을 위한 Azure Container Apps 심화 (6/6): Envoy Ingress 경로
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps심화, Dapr, AI코딩
