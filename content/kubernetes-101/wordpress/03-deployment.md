---
series: kubernetes-101
episode: 3
title: "바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - Deployment
  - RollingUpdate
  - DevOps
seo_description: AI가 생성한 Deployment YAML을 제대로 활용하기 위해 알아야 할 ReplicaSet, 롤링 업데이트, 롤백 구조를 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 세 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다.

---

AI에게 "Kubernetes 앱 배포 YAML 만들어줘"라고 하면 거의 항상 Deployment가 나옵니다. 그런데 Deployment가 뭔지, 왜 직접 Pod를 만들면 안 되는지 이해하지 못하면 가장 중요한 부분을 그냥 지나치게 됩니다.

바이브코딩으로 앱을 배포할 때 가장 많이 마주치는 상황이 있습니다. "파드가 죽었는데 왜 안 살아나죠?", "이미지 태그를 업데이트했는데 어떻게 배포하죠?", "배포했더니 문제가 생겼는데 롤백은 어떻게 해요?" 이 세 질문에 대한 답이 모두 Deployment 안에 있습니다.

> Deployment는 '파드를 N개 띄우는 설정'이 아니라 '원하는 개수를 유지하고 버전 교체와 롤백을 책임지는 컨트롤러'입니다. 직접 Pod를 만들지 않는 이유는 Pod가 죽었을 때 자기 자신을 다시 띄우지 못하기 때문이고, 이 빈자리를 컨트롤러가 채우는 것이 Kubernetes 워크로드의 기본 모델입니다.

## 이 글에서 답하는 질문들

- Deployment와 ReplicaSet은 어떤 관계일까요?
- `replicas`는 단순 숫자 이상의 어떤 의미를 가질까요?
- 이미지 변경이 왜 무중단 배포 흐름으로 이어질까요?
- Deployment를 잘못 설정하면 운영에서 어떤 장애가 생길까요?
- AI가 생성한 Deployment YAML에서 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: AI가 Deployment를 기본으로 만드는 이유

AI가 거의 항상 Pod 대신 Deployment를 생성하는 데는 이유가 있습니다.

Pod는 실행 단위일 뿐, 스스로 죽어도 다시 살아나지 않습니다. Deployment는 "이 앱을 N개 실행 중인 상태를 유지해라"라고 선언하는 컨트롤러입니다. 파드 하나가 죽으면 자동으로 새 파드를 만들어 원하는 개수를 맞춥니다.

이미지 태그를 바꾸면 새 ReplicaSet이 생기고, 이전 ReplicaSet은 점진적으로 줄어들면서 무중단 교체가 일어납니다. 문제가 생기면 이전 ReplicaSet으로 되돌릴 수 있습니다. 이것이 AI가 생성한 YAML에서 Deployment가 중심에 있는 이유입니다.

## Deployment 구조: 한눈에 보기

**주요 개념**

- **Deployment**: 파드 집합의 원하는 상태를 선언하는 상위 객체
- **ReplicaSet**: 원하는 파드 개수를 맞추는 컨트롤러(Deployment가 자동 관리)
- **replicas**: 유지하고 싶은 파드 수
- **롤아웃(rollout)**: 새 버전으로 점진적으로 교체하는 흐름
- **롤백(rollback)**: 이전 ReplicaSet으로 되돌리는 흐름

## Deployment 도입 전과 후

**Pod만 직접 만들 때**

파드 하나가 죽으면 서비스가 흔들릴 수 있습니다. 새 버전 배포는 기존 파드를 지우고 새 파드를 만드는 거친 방식입니다. 롤백 방법도 마땅치 않습니다.

**Deployment를 사용하면**

죽은 파드는 자동으로 다시 만들어집니다. 이미지 변경은 배포 전략에 따라 서서히 적용됩니다. 이전 버전 이력이 남고 롤백도 가능합니다. Kubernetes 운영이 예측 가능해지는 이유입니다.

## 단계별 Deployment 다루기

### 1단계: Deployment 매니페스트 작성

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: app
        image: nginx:1.25
```

가장 먼저 볼 값은 `replicas: 3`입니다. 단순 숫자가 아니라 "서비스가 감당해야 할 최소 실행 개수"에 대한 선언입니다. 하나가 죽어도 세 개를 유지하려는 의도가 여기에 담깁니다.

`selector.matchLabels`와 `template.metadata.labels`는 반드시 일치해야 합니다. AI가 생성한 YAML에서 가장 먼저 확인해야 할 부분입니다.

### 2단계: 이미지 업데이트 (무중단 배포)

```bash
kubectl set image deployment/web app=nginx:1.26
kubectl rollout status deployment/web
```

이미지 태그 하나를 바꾸어도 Deployment는 새 버전 배포로 해석합니다. 기존 파드를 한 번에 모두 없애지 않고, 전략에 따라 새 파드를 띄우고 준비 상태를 확인하면서 교체합니다.

### 3단계: 롤백

```bash
kubectl rollout history deployment/web
kubectl rollout undo deployment/web
```

배포 후 문제가 생기면 이전 ReplicaSet으로 되돌릴 수 있습니다. 야간 장애 대응에서 이 흐름을 알고 있으면 복구 속도가 달라집니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| Pod를 직접 만들고 자동 복구를 기대 | 직접 만든 Pod는 죽어도 다시 안 뜸 | Deployment로 관리 |
| `replicas: 1`로 고가용성 기대 | 파드 하나만 있으면 재시작 시 다운타임 발생 | 최소 2 이상 설정 |
| readiness probe 없이 배포 | 준비 안 된 파드가 트래픽 받아 오류 발생 | readiness probe 필수 |
| selector와 labels 불일치 | Deployment가 파드를 인식 못 함 | AI 생성 YAML에서 반드시 확인 |
| 롤백 방법을 모른 채 배포만 반복 | 문제 생겼을 때 복구 불가 | `rollout undo` 흐름 미리 연습 |

## AI 팁: Deployment YAML 요청과 검토

```
# Deployment 생성 요청 예시
"stateless 웹 앱을 위한 Deployment YAML을 만들어줘.
replicas는 3, 이미지는 nginx:1.25야.
readiness probe도 포함하고, selector와 labels가
정확히 일치하도록 만들어줘."

# 무중단 배포 설정 요청 예시
"이 Deployment에 RollingUpdate 전략을 추가해줘.
maxUnavailable: 1, maxSurge: 1로 설정하고
그 의미도 설명해줘."

# 롤백 방법 질문 예시
"이 Deployment를 배포했다가 문제가 생겼을 때
이전 버전으로 롤백하는 방법을 단계별로 알려줘."
```

## 운영 체크리스트

- [ ] `replicas`를 2 이상으로 설정할지 검토했는가
- [ ] `selector.matchLabels`와 `template.metadata.labels`가 일치하는가
- [ ] readiness probe를 정의했는가
- [ ] RollingUpdate 옵션을 명시했는가
- [ ] 롤백 절차(`kubectl rollout undo`)를 테스트해봤는가

## 처음 질문으로 돌아가기

**Deployment와 ReplicaSet은 어떤 관계일까요?**
Deployment는 직접 파드 수를 세는 대신 ReplicaSet을 통해 파드를 관리합니다. 이미지가 바뀌면 새 ReplicaSet이 생기고, 이전 ReplicaSet은 점진적으로 줄어듭니다. 이 중간 계층이 있어야 롤링 업데이트와 롤백이 구조적으로 가능합니다.

**`replicas`는 단순 숫자 이상의 어떤 의미를 가질까요?**
"이 개수를 항상 유지하라"는 선언입니다. 파드 하나가 죽으면 시스템이 자동으로 새 파드를 만들어 이 숫자를 맞추려 합니다. 선언한 개수가 항상 실행 중인 상태를 유지해야 한다는 의도가 담긴 값입니다.

**이미지 변경이 왜 무중단 배포 흐름으로 이어질까요?**
이미지 태그가 바뀌면 Deployment는 새 ReplicaSet을 만들고, 기존 ReplicaSet을 줄이는 방식으로 교체합니다. `maxUnavailable`과 `maxSurge` 설정에 따라 동시에 몇 개를 교체할지 조절됩니다. 이 덕분에 배포 중에도 서비스가 유지됩니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, Deployment는 파드 개수 유지, 롤링 업데이트, 롤백을 맡는 기본 워크로드 컨트롤러입니다. 둘째, AI가 생성한 YAML에서 selector와 labels 일치 여부, readiness probe 포함 여부를 반드시 확인해야 합니다. 셋째, 배포하기 전에 롤백 방법을 알고 있어야 장애 대응이 빨라집니다.

다음 글에서는 이렇게 떠 있는 파드 집합을 내부와 외부에서 안정적으로 찾고 호출하는 Service를 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: Deployment](https://kubernetes.io/ko/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes 공식 문서: ReplicaSet](https://kubernetes.io/ko/docs/concepts/workloads/controllers/replicaset/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- **바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, Deployment, RollingUpdate, DevOps
