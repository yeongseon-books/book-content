---
series: kubernetes-101
episode: 2
title: "바이브코딩을 위한 Kubernetes 기초 (2/10): Pod"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - Pod
  - Containers
  - DevOps
seo_description: AI가 생성한 Pod YAML을 제대로 이해하고 검토하기 위해 알아야 할 Pod 구조, 사이드카 패턴, 수명 주기를 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 두 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다.

---

AI에게 "Kubernetes로 앱 배포하는 YAML 만들어줘"라고 하면 Deployment YAML이 나오고, 그 안에 Pod 스펙이 포함되어 있습니다. 그런데 Pod가 뭔지 모르면 Deployment를 이해하기 어렵고, 장애가 났을 때 `kubectl describe pod` 출력을 읽어도 무슨 말인지 모릅니다.

컨테이너 하나 = Pod 하나라고 단순하게 외우면 처음에는 넘어갑니다. 하지만 사이드카 패턴, init container, 공유 볼륨, Pod IP가 왜 바뀌는지 같은 실질적인 운영 포인트를 모두 놓칩니다. AI가 생성한 YAML에 `containers` 배열이 왜 있는지, 거기 여러 항목이 들어가면 무슨 의미인지 이해하지 못하게 됩니다.

이 글은 Pod를 "컨테이너 하나의 껍데기"가 아니라 함께 뜨고 함께 내려가며 네트워크와 볼륨을 공유하는 실행 묶음으로 이해하는 데 집중합니다.

> Pod가 컨테이너가 아닌 이유는 '함께 살고 함께 죽는다'는 결정이 필요하기 때문입니다. 같은 네트워크와 볼륨을 공유하며 한 단위로 스케줄·재시작되는 묶음이라야 사이드카·init 컨테이너·로컬 통신 같은 패턴이 비로소 자연스럽게 표현됩니다.

## 이 글에서 답하는 질문들

- Pod와 컨테이너는 정확히 어떻게 다를까요?
- 왜 Kubernetes는 컨테이너가 아니라 Pod를 기본 단위로 삼을까요?
- 사이드카 패턴은 어떤 상황에서 필요할까요?
- Pod YAML을 잘못 작성하면 운영에서 어떤 문제가 생길까요?
- AI가 생성한 Pod 스펙에서 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: AI가 `containers` 배열을 만드는 이유

AI에게 "nginx 컨테이너 하나 실행하는 Pod 만들어줘"라고 하면 이런 YAML을 줍니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports:
    - containerPort: 80
```

여기서 `containers`가 **배열**인 점이 중요합니다. Kubernetes는 처음 설계부터 "Pod 안에 컨테이너가 하나 이상 들어갈 수 있다"를 전제로 만들어졌습니다. 이 구조를 이해하면 AI가 왜 사이드카를 같은 `containers` 배열 안에 추가하는지 알 수 있고, 그렇게 했을 때 어떤 의미인지도 판단할 수 있습니다.

같은 Pod 안의 컨테이너는 네트워크 네임스페이스와 볼륨을 공유합니다. 그래서 메인 앱과 로그 수집기, 메인 앱과 보안 프록시를 같은 Pod에 묶는 패턴이 자연스럽게 나옵니다.

## Pod 구조: 한눈에 보기

**주요 개념**

- **Pod**: 하나 이상의 컨테이너가 공유된 환경에서 함께 실행되는 묶음
- **사이드카**: 주 컨테이너 옆에서 로그 수집, 프록시, 동기화 같은 보조 역할을 하는 컨테이너
- **init container**: 애플리케이션 시작 전에 한 번 실행되는 컨테이너(DB 마이그레이션, 설정 초기화 등)
- **수명 주기**: Pending → Running → Succeeded/Failed 흐름
- **일시성**: Pod가 죽으면 같은 개체가 살아나는 게 아니라 새로 만들어짐. Pod IP도 바뀜

## Pod 도입 전과 후

**컨테이너만 있을 때**

로그 프록시, 보안 에이전트, 보조 프로세스를 어떻게 함께 배치할지 일관된 기준이 없습니다. 리소스 공유 구조를 매번 사람이 직접 설계해야 합니다.

**Pod 모델을 사용하면**

함께 살아야 하는 컨테이너를 한 Pod에 묶고, 네트워크와 볼륨을 자연스럽게 공유하도록 만들 수 있습니다. Kubernetes가 왜 컨테이너보다 Pod를 먼저 보는지 이해되는 지점입니다.

## 단계별 Pod 다루기

### 1단계: Pod 매니페스트 작성

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports:
    - containerPort: 80
```

가장 작은 형태의 Pod입니다. `containers`가 배열이라는 점, 즉 여러 컨테이너를 넣을 수 있다는 설계가 중요합니다.

### 2단계: 적용 및 상태 확인

```bash
kubectl apply -f pod.yaml
kubectl get pod web -o wide
kubectl describe pod web
```

`describe`는 Pod를 처음 배울 때 가장 유용합니다. 스케줄링 이벤트, 이미지 풀 상태, 컨테이너 시작 여부까지 함께 보여 줍니다.

### 3단계: 로그 확인

```bash
kubectl logs web
kubectl logs web -c app  # 특정 컨테이너 로그
```

Pod 안의 컨테이너 로그는 표준 출력으로 보는 것이 기본입니다. 컨테이너 안에 들어가서 로그 파일을 뒤지는 방식은 Kubernetes 운영 모델과 맞지 않습니다.

### 4단계: 삭제

```bash
kubectl delete pod web
```

직접 만든 Pod는 지우면 끝입니다. 다시 살아나지 않습니다. 자동 복구는 Pod 자체가 아니라 상위 컨트롤러(Deployment 등)의 책임입니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| Pod = 컨테이너 하나로만 이해 | 사이드카, 공유 볼륨 패턴을 놓침 | Pod는 컨테이너 묶음이라는 관점으로 이해 |
| 직접 만든 Pod가 자동 복구된다고 기대 | 죽으면 그냥 사라짐 | Deployment 같은 상위 컨트롤러 사용 |
| Pod IP를 안정적으로 사용 | 재시작마다 IP 바뀜 | Service로 안정적인 주소 확보 |
| 사이드카를 아무 때나 같은 Pod에 넣음 | 배포와 스케일링 단위가 묶여버림 | 함께 살아야 하는지 먼저 판단 |
| 로그를 컨테이너 내부 파일로만 확인 | kubectl logs가 안 됨 | 표준 출력으로 로그 설정 |

## AI 팁: Pod YAML 요청과 검토

```
# 사이드카 패턴 요청 예시
"nginx 앱 컨테이너와 fluentd 로그 수집 사이드카가 있는
Pod YAML을 만들어줘. 두 컨테이너가 /var/log 볼륨을 공유해야 해."

# Pod 검토 요청 예시
"이 Pod YAML에서 사이드카 컨테이너가 메인 컨테이너와
네트워크/볼륨을 어떻게 공유하는지 설명해줘.
실수가 있을 수 있는 부분도 찾아줘."

# 장애 진단 요청 예시
"kubectl describe pod 결과를 붙여넣을게.
Pending 상태인 이유와 해결 방법을 알려줘."
```

## 운영 체크리스트

- [ ] Pod를 직접 만드는 것은 학습이나 디버깅 용도로 한정했는가
- [ ] 사이드카가 정말 메인 컨테이너와 같은 수명 주기를 가져야 하는가
- [ ] 로그가 표준 출력으로 나가도록 컨테이너가 설정되었는가
- [ ] Pod IP를 직접 사용하는 코드가 없는가 (Service를 사용하는가)
- [ ] AI가 생성한 YAML의 `containers` 배열 항목이 의도한 대로인가

## 처음 질문으로 돌아가기

**Pod와 컨테이너는 정확히 어떻게 다를까요?**
컨테이너는 격리된 프로세스 실행 환경입니다. Pod는 하나 이상의 컨테이너를 묶어 같은 네트워크 네임스페이스와 볼륨을 공유하게 하는 실행 단위입니다. 같은 Pod 안에서는 `localhost`로 서로 통신할 수 있습니다.

**왜 Kubernetes는 Pod를 기본 단위로 삼을까요?**
"이 컨테이너들은 항상 함께 있어야 한다"는 결정을 표현하기 위해서입니다. 사이드카 패턴처럼 메인 앱과 보조 프로세스가 항상 같은 곳에 있어야 할 때, Pod가 그 묶음을 하나의 스케줄 단위로 다룰 수 있게 합니다.

**사이드카 패턴은 어떤 상황에서 필요할까요?**
로그 수집기가 메인 앱과 같은 로그 파일을 봐야 할 때, 보안 프록시가 메인 앱과 localhost로 통신해야 할 때, 설정을 주기적으로 동기화하는 에이전트가 메인 앱과 항상 같이 있어야 할 때 사이드카를 사용합니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, Pod는 컨테이너 하나가 아니라 네트워크와 볼륨을 공유하는 컨테이너 묶음입니다. 둘째, 직접 만든 Pod는 자동 복구되지 않으므로 Deployment 같은 상위 컨트롤러가 필요합니다. 셋째, Pod를 잘 설계해야 나중에 Deployment, HPA, PDB를 붙일 때 추가 비용이 줄어듭니다.

다음 글에서는 Pod를 직접 관리하지 않고, 원하는 개수를 유지하고 롤링 업데이트까지 맡는 Deployment를 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: Pod](https://kubernetes.io/ko/docs/concepts/workloads/pods/)
- [Kubernetes 공식 문서: 사이드카 컨테이너](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- **바이브코딩을 위한 Kubernetes 기초 (2/10): Pod (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, Pod, Containers, DevOps
