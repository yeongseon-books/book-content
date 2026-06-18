---
series: kubernetes-101
episode: 1
title: "바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - Orchestration
  - Containers
  - DevOps
seo_description: AI에게 K8s YAML을 생성시키기 전에 반드시 알아야 할 Kubernetes의 기본 구조와 원하는 상태 모델을 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 첫 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다. 모르는 상태로 생성한 YAML은 실수가 나도 어디가 잘못됐는지 알 수 없습니다.

---

AI에게 "Kubernetes YAML 만들어줘"라고 하면 그럴싸한 코드가 금방 나옵니다. 그런데 막상 `kubectl apply`를 눌렀을 때 파드가 뜨지 않거나 서비스가 연결이 안 되면, AI가 만든 YAML 어디를 고쳐야 할지 막막해집니다. Kubernetes를 쓰는 사람이 늘면서 이런 상황이 더 자주 생깁니다.

바이브코딩 흐름에서 Kubernetes가 등장하는 시점은 보통 "이제 컨테이너로 배포하고 싶은데 어떻게 해야 해?"라는 질문 직후입니다. AI가 자신 있게 Deployment, Service, Ingress YAML을 한꺼번에 생성해 줍니다. 그 파일을 그대로 붙여 넣어 돌아가면 다행이지만, 안 돌아가면 Kubernetes가 내부에서 무슨 일을 하는지 모르기 때문에 수정 방향을 잡기 어렵습니다.

이 시리즈는 AI와 함께 쓰기 전에 알아야 할 Kubernetes 핵심 개념을 하나씩 정리합니다. 첫 번째 주제는 가장 기초적이지만 가장 중요한 질문, "Kubernetes가 실제로 뭘 하는 도구인가?"입니다.

> Kubernetes는 '컨테이너를 많이 돌리는 도구'가 아니라 원하는 상태(desired state)를 선언하면 시스템이 그 상태로 계속 수렴하도록 만드는 오케스트레이터입니다. 사람이 명령형으로 맞추던 일을 컨트롤러 루프에 위임한다는 한 가지 발상이 모든 리소스 설계의 출발점입니다.

## 이 글에서 답하는 질문들

- 오케스트레이션이라는 말은 실제로 무엇을 대신해 줄까요?
- 컨트롤 플레인과 워커 노드는 어떤 식으로 역할을 나눌까요?
- 원하는 상태 모델이 왜 Kubernetes의 핵심 철학일까요?
- 이 개념을 잘못 이해하면 운영에서 어떤 문제가 생길까요?
- AI가 생성한 YAML을 검토할 때 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: AI에게 YAML을 맡기기 전에

많은 개발자들이 Kubernetes를 처음 접할 때 Docker Compose는 이해하면서 써왔는데, Kubernetes는 그냥 AI한테 YAML 생성시키면 되는 것 아닌가? 라고 생각합니다. 하지만 Docker Compose와 Kubernetes는 설계 철학 자체가 다릅니다.

Docker Compose는 명령형(imperative) 도구에 가깝습니다. "이 컨테이너를 지금 이 서버에 이렇게 띄워라"라고 지시합니다. Kubernetes는 선언형(declarative) 오케스트레이터입니다. "내가 원하는 최종 상태는 이것이다"라고 선언하면, 시스템이 현재 상태와 원하는 상태 사이의 차이를 스스로 메웁니다.

이 차이를 모른 채 AI가 생성한 YAML을 쓰면, 왜 파드가 안 뜨는지, 왜 트래픽이 안 들어오는지 이유를 찾을 수 없습니다. 원하는 상태 모델을 이해해야 비로소 "지금 무슨 상태고, 왜 원하는 상태에 도달하지 못했는지"를 진단할 수 있습니다.

## Kubernetes 구조: 한눈에 보기

`kubectl`을 실행하면 직접 컨테이너가 뜨는 것이 아닙니다. 사용자는 `kubectl`로 원하는 상태를 API 서버에 전달하고, 이후의 배치와 조정은 컨트롤 플레인 구성요소가 맡습니다.

**주요 개념**

- **클러스터**: 컨트롤 플레인과 워커 노드를 묶은 전체 실행 환경
- **컨트롤 플레인**: API 서버, etcd, scheduler, controller-manager가 클러스터 제어를 담당
- **노드**: 실제로 컨테이너가 실행되는 머신
- **원하는 상태**: YAML에 선언한 목표 상태
- **`kubectl`**: 클러스터 API와 통신하는 CLI

## Kubernetes 도입 전과 후

**도입 전**

서버마다 수동으로 `docker run`을 실행합니다. 컨테이너가 죽으면 사람이 다시 올립니다. 같은 환경을 다른 서버에 재현하기 어렵습니다.

**도입 후**

원하는 상태를 YAML로 선언합니다. 같은 구성을 다른 환경에 반복해서 적용할 수 있습니다. 시스템이 현재 상태를 계속 목표 상태에 맞추려 합니다. 재현성과 자동 복구가 여기서 시작됩니다.

## 바이브코딩 AI 활용 팁

AI에게 Kubernetes YAML을 요청할 때 이렇게 질문하면 더 좋은 결과를 얻을 수 있습니다.

```
나쁜 질문: "Kubernetes YAML 만들어줘"

좋은 질문:
- "stateless 웹 앱을 위한 Deployment YAML을 만들어줘.
  replicas는 3, 이미지는 nginx:1.25야.
  원하는 상태 모델에 맞게 selector와 labels를 제대로 연결해줘."

- "이 YAML에서 컨트롤 플레인이 어떤 컴포넌트를 사용해서
  원하는 상태로 수렴시키는지 설명해줘."
```

컨텍스트를 더 많이 줄수록, 그리고 내가 이해하는 개념을 활용해 질문할수록 AI가 더 정확한 YAML을 만들어줍니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| Kubernetes를 "컨테이너 실행 도구"로만 이해 | 원하는 상태 모델을 모르니 장애 원인 파악 불가 | 선언형 오케스트레이터로 이해 |
| 노드 수만 늘리면 운영 문제 해결이라 생각 | 컨트롤 플레인 설정 문제는 노드 추가로 안 해결됨 | 컨트롤 플레인과 워커 노드 역할 구분 |
| `etcd`를 일반 DB처럼 직접 수정 | 클러스터 상태 전체가 망가짐 | API 서버를 통해서만 상태 변경 |
| `kubectl` 컨텍스트 확인 없이 적용 | 잘못된 클러스터에 변경이 들어감 | 항상 `current-context` 먼저 확인 |
| 규모가 작은데 Kubernetes 먼저 도입 | 관리 비용이 이점보다 커짐 | Docker Compose로 시작하고 필요할 때 전환 |

## AI 팁: Kubernetes 개념을 AI와 함께 학습하는 법

```
# 개념 이해용 질문 예시
"Kubernetes의 원하는 상태 모델을 Docker Compose와 비교해서
차이점을 설명해줘. 컨트롤러 루프가 어떻게 동작하는지도 포함해줘."

# YAML 검토용 질문 예시
"이 Deployment YAML에서 컨트롤 플레인이 원하는 상태로
수렴하지 못할 수 있는 부분이 있으면 찾아줘."

# 장애 진단용 질문 예시
"kubectl get pods 결과에서 파드가 Pending 상태인데
이유가 뭘 수 있는지 가장 가능성 높은 원인부터 설명해줘."
```

## 운영 체크리스트

- [ ] 적용 전 현재 컨텍스트(`kubectl config current-context`)를 확인했는가
- [ ] 워크로드를 네임스페이스로 나눌 계획이 있는가
- [ ] 원하는 상태를 YAML로 관리할 준비가 되었는가
- [ ] 관리형 Kubernetes(EKS, GKE, AKS)를 먼저 검토했는가
- [ ] AI가 생성한 YAML의 selector/labels 연결이 올바른지 확인했는가

## 처음 질문으로 돌아가기

**오케스트레이션이라는 말은 실제로 무엇을 대신해 줄까요?**
컨테이너를 어느 서버에 배치할지, 죽은 컨테이너를 언제 다시 띄울지, 새 버전으로 교체할 때 서비스를 끊지 않을 방법 같은 운영 결정을 사람 대신 시스템이 처리합니다. `kubectl`은 그 결정을 내리는 것이 아니라 원하는 결과를 선언하는 도구입니다.

**컨트롤 플레인과 워커 노드는 어떤 식으로 역할을 나눌까요?**
컨트롤 플레인(API 서버, etcd, scheduler, controller-manager)은 "무엇을 어디에 어떻게 배치할지" 결정하는 두뇌입니다. 워커 노드는 그 결정을 실제 컨테이너 실행으로 이행하는 실행 환경입니다.

**원하는 상태 모델이 왜 Kubernetes의 핵심 철학일까요?**
"지금 당장 이것을 해라"가 아니라 "최종 상태는 이것이어야 한다"고 선언하면, 시스템이 어떤 경로로든 그 상태에 도달하려 계속 시도합니다. 파드 하나가 죽어도 시스템이 스스로 복구하는 이유가 바로 이 모델 때문입니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, Kubernetes는 명령형이 아닌 선언형 오케스트레이터입니다. 둘째, 컨트롤 플레인이 원하는 상태와 현재 상태의 차이를 자동으로 메웁니다. 셋째, AI에게 YAML 생성을 맡기기 전에 이 모델을 이해해야 생성된 YAML을 제대로 검토하고 수정할 수 있습니다.

다음 글에서는 Kubernetes가 실제로 다루는 가장 작은 배포 단위인 Pod를 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: 개요](https://kubernetes.io/ko/docs/concepts/overview/)
- [Kubernetes 공식 문서: 컴포넌트](https://kubernetes.io/ko/docs/concepts/overview/components/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가? (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, Orchestration, Containers, DevOps
