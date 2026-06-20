---
title: "바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기"
series: azure-aca-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps
- FastAPI
- ACR
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 3편: 첫 배포하기. ACR → ACA Environment → Container App → Revision 네 단계 의존성 체인을 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기

이 글은 바이브코딩을 위한 Azure Container Apps 시리즈의 3번째 글입니다.

첫 배포는 ACA가 다이어그램에서 운영 모델로 바뀌는 순간입니다. ACA의 첫 배포는 택시를 부르기 전에 출발지가 있어야 한다는 비유로 이해할 수 있습니다. 택시(ACA)는 승객(이미지)을 목적지까지 데려다줄 수 있지만, 승객이 기다리고 있지 않으면 출발할 수 없습니다. 승객은 어딘가(레지스트리)에 먼저 서 있어야 하고, 택시에게 그 주소(이미지 참조)를 알려줘야 합니다. 그래서 첫 배포는 image build → registry push → ACA Revision 생성이라는 순서로 흐릅니다. ACA는 이미지를 직접 빌드하지 않습니다. 이 책임 경계를 모르면 "ACA에 코드를 올리면 빌드해주겠지"라는 가정으로 파이프라인을 잘못 설계하게 됩니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 CI/CD 파이프라인 코드를 요청할 때 빌드(ACR)와 배포(ACA) 단계를 명확히 분리하지 않으면, 배포 명령만 있고 이미지 빌드 단계가 없는 파이프라인이 생성되기 때문입니다.

> 첫 배포의 핵심은 ACA가 하지 않는 일(이미지 빌드, 이미지 저장)을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- 로컬 FastAPI 코드가 ACA Revision으로 살아나기까지의 전체 경로는 어떻게 될까요?
- ACA가 이미지를 직접 빌드해 주지 않는다는 사실은 책임 분담에 어떤 의미를 가질까요?
- ACR → ACA Environment → Container App → Revision 네 단계 의존성 체인은 어떻게 이어질까요?
- 배포 성공과 앱 시작 성공은 어떻게 분리해서 확인할 수 있을까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

첫 배포 경로를 이해하면 AI에게 "ACR에 이미지 빌드 및 푸시 → ACA containerapp update로 새 이미지 배포 → FQDN에서 /health 폴링으로 배포 성공 확인하는 CI/CD 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "FastAPI 앱을 ACA에 배포하는 파이프라인 작성해줘"
→ az containerapp update 명령만 생성
→ 이미지 빌드/푸시 단계 없음
→ 배포 성공 후 앱 동작 확인 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "FastAPI ACA 배포 파이프라인을 단계별로 작성해줘.
    1) docker build + az acr build로 이미지 빌드 및 ACR 푸시
    2) az containerapp update로 새 이미지 배포
    3) FQDN의 /health를 30초 간격 3회 폴링으로 앱 시작 확인
    4) 실패 시 이전 revision으로 트래픽 복귀"
→ 빌드와 배포 단계 분리
→ 배포 성공과 앱 시작 성공 별도 검증
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| ACA가 이미지를 빌드해준다고 가정 | ACA는 이미지 참조만 소비, 빌드는 별도 | CI에서 ACR build → push 단계 추가 |
| 배포 명령 성공을 앱 동작으로 오해 | containerapp update 성공 ≠ 앱 응답 | FQDN /health 폴링으로 별도 확인 |
| Managed Identity 없이 ACR 연결 | 이미지 pull 실패 | containerapp create 시 managed-identity 연결 |
| startup command 없이 배포 | ACA가 어떤 프로세스를 실행할지 모름 | Dockerfile CMD 또는 --command로 명시 |
| 모든 환경 변수를 이미지에 하드코딩 | 이미지 교체 없이 설정 변경 불가 | --env-vars 또는 secrets로 외부화 |

## AI 협업 팁

첫 배포 관련 효과적인 AI 프롬프트 패턴:

1. **이미지 빌드+배포 파이프라인 요청**: "ACR에 이미지 빌드 후 ACA에 배포하고 /health로 앱 시작 확인하는 bash 스크립트 작성해줘"
2. **Managed Identity 설정 요청**: "ACA가 ACR에서 이미지를 pull하도록 Managed Identity를 설정하는 az CLI 명령 작성해줘"
3. **배포 검증 요청**: "ACA 배포 후 FQDN의 /health 엔드포인트를 폴링해 200 응답을 받을 때까지 기다리는 스크립트 작성해줘"

예시 프롬프트:
> "FastAPI ACA 무중단 배포 스크립트를 작성해줘. az acr build로 이미지 빌드 → az containerapp update로 배포 → FQDN /health 3회 폴링(30초 간격) → 실패 시 이전 revision으로 트래픽 복귀."

## 운영 체크리스트

- [ ] 이미지 빌드와 ACA 배포 단계를 분리해서 구성했는가?
- [ ] Managed Identity로 ACR 이미지 pull을 설정했는가?
- [ ] 배포 후 FQDN /health 폴링으로 앱 시작을 별도 확인하는가?
- [ ] 환경 변수를 이미지 외부(--env-vars, secrets)로 관리하는가?
- [ ] 다음 글에서 Ingress와 트래픽 분할을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

첫 배포 경로를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 빌드와 배포 단계를 분리하고 배포 검증을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 CI/CD 파이프라인의 완성도는 크게 다릅니다.

## 정리

첫 배포하기 편은 바이브코딩을 위한 Azure Container Apps에서 코드가 Revision으로 살아나는 전체 경로를 이해하는 핵심 단계입니다. ACA가 하지 않는 일(이미지 빌드, 저장)과 하는 일(Revision 실행, ingress, TLS)의 경계를 이해했습니다. 다음 글에서는 Ingress와 트래픽 분할을 다룹니다.

## 참고 자료

- [Deploy to Azure Container Apps](https://docs.microsoft.com/azure/container-apps/quickstart-portal)
- [Azure Container Registry with Container Apps](https://docs.microsoft.com/azure/container-apps/containers)
- [Managed identities in Container Apps](https://docs.microsoft.com/azure/container-apps/managed-identity)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/03-first-deploy)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?
- 바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision
- **바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기 (현재 글)**
- 바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA
- 바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합
- 바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps, FastAPI, ACR, AI코딩
