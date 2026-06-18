---
series: kubernetes-101
episode: 8
title: "바이브코딩을 위한 Kubernetes 기초 (8/10): HPA"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - HPA
  - Autoscaling
  - DevOps
seo_description: AI가 생성한 HPA YAML을 제대로 활용하기 위해 알아야 할 메트릭 기반 자동 스케일링, resource requests 설정, 플래핑 방지를 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 여덟 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다.

---

AI에게 "트래픽이 많아지면 자동으로 파드를 늘리는 설정 만들어줘"라고 하면 HPA(HorizontalPodAutoscaler) YAML이 나옵니다. 그런데 HPA를 설정했는데도 파드가 안 늘어나거나, 너무 자주 늘었다 줄었다 하는 "플래핑(flapping)" 문제가 생기면 원인을 찾기 어렵습니다.

바이브코딩 흐름에서 HPA를 처음 설정할 때 가장 많이 하는 실수가 있습니다. Deployment에 `resources.requests`를 설정하지 않고 HPA를 만드는 것입니다. HPA가 CPU 사용률을 계산하려면 "요청한 CPU"가 기준으로 있어야 하는데, requests가 없으면 비율을 계산할 수 없어 HPA가 동작하지 않습니다.

> HPA는 'CPU 높으면 파드 늘리는 기능'이 아니라 '메트릭을 입력으로 Deployment의 desired replicas를 조절하는 컨트롤러 루프'입니다. 어떤 메트릭을 보느냐, 어떻게 안정화하느냐, 무엇을 최대로 두느냐가 자동화의 안정성을 결정합니다.

## 이 글에서 답하는 질문들

- 트래픽이 바뀔 때마다 수동으로 파드 수를 조절하면 왜 느리고 비쌀까요?
- HPA는 어떤 지표를 보고 스케일 아웃과 스케일 인을 결정할까요?
- `resource requests`가 없으면 왜 HPA가 동작하지 않을까요?
- HPA를 잘못 설정하면 운영에서 어떤 문제가 생길까요?
- AI가 생성한 HPA YAML에서 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: HPA는 Deployment의 replicas를 자동 조정한다

AI가 만들어준 HPA YAML을 이해하려면 HPA가 직접 파드를 만들거나 지우는 것이 아니라, Deployment의 `replicas` 숫자를 자동으로 조정한다는 점을 알아야 합니다.

```
사용자 트래픽 증가
  -> CPU 사용률 올라감 (metrics-server가 수집)
  -> HPA가 "목표 사용률 60%를 넘었다"고 판단
  -> HPA가 Deployment의 replicas를 3 -> 5로 변경
  -> Deployment가 새 파드 2개 생성
  -> CPU 사용률 낮아짐
  -> HPA가 replicas를 5 -> 3으로 변경
```

이 흐름에서 `resource requests`가 없으면 CPU 사용률 자체를 계산할 수 없습니다. 요청한 CPU 200m 대비 현재 사용 CPU가 몇 %인지 비교하는 방식이기 때문입니다.

## HPA 구조: 한눈에 보기

**주요 개념**

- **HPA**: 파드 개수를 자동으로 조절하는 오토스케일러. Deployment의 replicas를 조정
- **metrics-server**: CPU, 메모리 같은 기본 메트릭을 수집하는 클러스터 컴포넌트. 별도 설치 필요
- **목표 사용률(averageUtilization)**: requests 대비 목표 CPU 또는 메모리 비율(%)
- **minReplicas/maxReplicas**: 파드 수의 최솟값과 최댓값
- **플래핑(flapping)**: 파드가 자주 늘었다 줄었다 하는 불안정한 상태

## 도입 전과 후

**수동 스케일링을 할 때**

피크 시간에 503 에러가 늘어난 뒤에야 파드를 늘립니다. 한가한 시간에도 과하게 파드를 띄워 비용을 낭비합니다.

**HPA를 사용하면**

현재 부하에 맞춰 자동으로 파드 수가 조절됩니다. 다만 자동화의 품질은 requests 설정, 메트릭 신뢰도, 최솟값/최댓값 설계에 달려있습니다.

## 단계별 CPU 기반 HPA 구성하기

### 1단계: Deployment에 resource requests 설정 (필수!)

```yaml
spec:
  template:
    spec:
      containers:
      - name: app
        image: myorg/app:1.0
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

HPA를 쓰려면 반드시 `resources.requests`를 설정해야 합니다. requests가 없으면 HPA가 CPU 사용률을 계산할 수 없습니다.

### 2단계: HPA 매니페스트 작성

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

CPU 사용률이 requests 대비 60%를 넘으면 파드를 늘립니다. `minReplicas: 2`는 가용성 최솟값이고, `maxReplicas: 10`은 비용과 용량의 상한선입니다.

### 3단계: metrics-server 확인

```bash
# metrics-server가 있어야 kubectl top이 동작합니다
kubectl top pods
kubectl top nodes

# metrics-server가 없다면
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

HPA가 동작하려면 클러스터에 metrics-server가 설치되어 있어야 합니다.

### 4단계: HPA 상태 모니터링

```bash
kubectl get hpa web
kubectl describe hpa web
kubectl get hpa web -w  # 변화를 실시간으로 관찰
```

TARGETS 컬럼에 `현재사용률/목표사용률`이 보여야 합니다. `unknown/60%`가 나오면 metrics-server 문제나 requests 미설정을 의심합니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| `resource requests` 없이 HPA 생성 | TARGETS가 `unknown`이고 자동화 안 됨 | 반드시 requests 먼저 설정 |
| `maxReplicas`를 너무 낮게 설정 | 피크 트래픽에 파드가 충분히 안 늘어남 | 예상 최대 트래픽을 감당하는 값으로 설정 |
| metrics-server 없이 HPA 생성 | HPA가 동작하지 않음 | metrics-server 설치 확인 |
| 노드 용량을 고려하지 않음 | HPA가 파드를 늘리려 해도 노드가 부족해 파드가 Pending | Cluster Autoscaler 함께 검토 |
| 너무 공격적인 스케일 아웃 기준 | 플래핑(자주 늘었다 줄었다 반복) 발생 | 안정화 윈도우 설정, 기준값 조정 |

## AI 팁: HPA YAML 요청과 검토

```
# HPA 생성 요청 예시
"이 Deployment(web)에 HPA를 설정해줘.
CPU 사용률 60%가 되면 파드를 늘리고,
최소 2개, 최대 10개로 제한해줘.
Deployment에 resource requests도 함께 설정해줘."

# 문제 진단 요청 예시
"kubectl get hpa 결과에서 TARGETS가 'unknown/60%'로 나와.
이유와 해결 방법을 알려줘."

# 커스텀 메트릭 질문 예시
"CPU 대신 HTTP 요청 수를 기준으로 HPA를 설정하고 싶어.
Prometheus Adapter를 사용하는 방법을 알려줘."
```

## 운영 체크리스트

- [ ] Deployment에 `resources.requests`를 설정했는가
- [ ] 클러스터에 metrics-server가 설치되어 있는가
- [ ] `minReplicas`를 2 이상으로 설정했는가(고가용성)
- [ ] `maxReplicas`가 실제 피크 트래픽을 감당할 수 있는 값인가
- [ ] 노드 수가 maxReplicas를 수용할 수 있는지 검토했는가

## 처음 질문으로 돌아가기

**트래픽이 바뀔 때마다 수동으로 파드 수를 조절하면 왜 느리고 비쌀까요?**
수동 스케일링은 항상 한 박자 늦습니다. 이미 응답 시간이 나빠진 뒤에 파드를 늘리고, 한가한 시간에도 과하게 파드를 띄워두면 비용이 낭비됩니다. HPA는 메트릭을 보고 실시간으로 필요한 파드 수를 자동 조정합니다.

**HPA는 어떤 지표를 보고 스케일 아웃과 스케일 인을 결정할까요?**
기본은 CPU와 메모리 사용률입니다. requests 대비 현재 사용량의 비율을 계산해서 목표 사용률과 비교합니다. 커스텀 메트릭을 사용하면 HTTP 요청 수, 큐 길이, 응답 시간 등 서비스별 지표로도 스케일링할 수 있습니다.

**`resource requests`가 없으면 왜 HPA가 동작하지 않을까요?**
CPU 사용률은 "요청한 CPU 대비 현재 사용 CPU"의 비율입니다. requests가 없으면 분모가 없어서 비율 계산이 불가능합니다. `kubectl get hpa`에서 TARGETS가 `unknown`으로 표시되고 자동 스케일링이 동작하지 않습니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, HPA가 동작하려면 Deployment에 `resource requests`가 반드시 설정되어 있어야 합니다. 둘째, HPA는 파드를 직접 만들지 않고 Deployment의 replicas 값을 조정합니다. 셋째, 자동화의 품질은 requests 설정, 메트릭 신뢰도, 최솟값/최댓값 설계에 달려있습니다.

다음 글에서는 늘어나는 YAML을 반복 가능하게 패키징하고 배포하는 Helm을 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: HPA](https://kubernetes.io/ko/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Kubernetes 공식 문서: metrics-server](https://github.com/kubernetes-sigs/metrics-server)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- **바이브코딩을 위한 Kubernetes 기초 (8/10): HPA (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, HPA, Autoscaling, DevOps
