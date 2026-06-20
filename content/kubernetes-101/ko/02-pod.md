---
series: kubernetes-101
episode: 2
title: "Kubernetes 101 (2/10): Pod"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/264"
    published_at: '2026-06-02'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - Pod
  - Containers
  - YAML
  - DevOps
seo_description: 쿠버네티스 최소 배포 단위인 Pod를 컨테이너와 비교 정의하고, 사이드카 패턴과 네트워크 공유, 수명 주기를 통해 Pod의 구조를 이해합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (2/10): Pod

Kubernetes를 처음 배우면 가장 먼저 헷갈리는 지점이 있습니다. 컨테이너를 실행하는 플랫폼이라면서 왜 가장 작은 단위가 컨테이너가 아니라 Pod인지입니다. Docker를 먼저 익힌 사람일수록 이 질문이 더 자연스럽습니다.

이 글은 Kubernetes 101 시리즈의 2번째 글입니다.

여기서는 Pod를 단순히 "컨테이너 하나를 싸는 껍데기"로 보지 않고, 함께 뜨고 함께 내려가며 네트워크와 볼륨을 공유하는 실행 묶음이라는 관점에서 정리하겠습니다.

![Kubernetes 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/02/02-01-concept-at-a-glance.ko.png)
*Kubernetes 101 2장 흐름 개요*

> Pod가 컨테이너가 아닌 이유는 '함께 살고 함께 죽는다'는 결정이 필요하기 때문입니다 — 같은 네트워크와 볼륨을 공유하며 한 단위로 스케줄·재시작되는 묶음이라야 사이드카·init 컨테이너·로컬 통신 같은 패턴이 비로소 자연스럽게 표현됩니다.

## 이 글에서 다룰 문제

- Pod와 컨테이너는 정확히 어떻게 다를까요?
- 왜 Kubernetes는 컨테이너가 아니라 Pod를 기본 단위로 삼을까요?
- 사이드카 패턴은 어떤 상황에서 필요할까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

모든 워크로드는 결국 Pod 위에서 실행됩니다. Deployment를 쓰든 StatefulSet을 쓰든, 마지막에 실제로 스케줄되는 것은 Pod입니다. 그래서 Pod 모델을 이해하지 못하면 뒤에 나오는 상위 객체도 이름만 다르게 보일 뿐입니다.

특히 입문 단계에서는 "컨테이너가 하나면 Pod도 하나"라는 식으로 단순화해서 외우기 쉽습니다. 물론 그런 경우가 많기는 합니다. 하지만 그 정도로만 이해하면 사이드카, init container, 공유 볼륨, 임시 IP 같은 중요한 운영 포인트를 놓치게 됩니다.

## 한눈에 보는 구조

이 구조의 핵심은 Pod 안의 컨테이너가 완전히 독립적이지 않다는 사실입니다. 같은 Pod에 들어간 컨테이너는 네트워크 네임스페이스와 볼륨을 공유합니다. 그래서 하나의 애플리케이션 본체와 그 옆에서 돕는 보조 컨테이너를 함께 묶는 패턴이 자연스럽게 나옵니다.

- Pod: 하나 이상의 컨테이너가 공유된 환경에서 함께 실행되는 묶음입니다.
- 사이드카: 주 컨테이너 옆에서 로그 수집, 프록시, 동기화 같은 보조 역할을 하는 컨테이너입니다.
- init container: 애플리케이션 시작 전에 한 번 실행되는 컨테이너입니다.
- 수명 주기: Pending에서 Running으로 가고, 끝나면 Succeeded 또는 Failed로 마무리되는 흐름입니다.
- 일시성: Pod는 죽은 뒤 같은 개체가 다시 살아나는 방식이 아니라 새로 만들어지는 방식에 가깝습니다.

## 도입 전과 후

| 상황 | 컨테이너 단위 관리 | Pod 모델 도입 후 |
|---|---|---|
| 보조 프로세스 배치 | 사람이 직접 배치 규칙 설계 | 사이드카로 같은 Pod에 자연스럽게 묶음 |
| 로컬 통신 | 포트 노출 및 네트워크 설정 필요 | localhost로 직접 통신 가능 |
| 볼륨 공유 | 별도 네트워크 스토리지 마운트 필요 | emptyDir 볼륨으로 Pod 내 공유 |
| 수명 관리 | 컨테이너별 개별 재시작 정책 필요 | Pod 단위로 함께 재시작 |
| 스케줄링 | 관련 컨테이너가 다른 노드에 배치될 수 있음 | 항상 같은 노드에서 실행 보장 |

## Pod YAML 구조 완전 이해

### 기본 단일 컨테이너 Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
    version: "1.0"
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
```

가장 작은 형태의 Pod입니다. 여기서는 컨테이너가 하나뿐이지만, `containers`가 배열이라는 사실이 중요합니다. Kubernetes는 처음부터 "하나 이상"을 전제로 설계돼 있습니다.

### 사이드카 패턴 Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-with-logger
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports:
    - containerPort: 80
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  - name: log-shipper           # 사이드카 컨테이너
    image: fluent/fluent-bit:latest
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx  # 같은 볼륨을 공유
  volumes:
  - name: logs
    emptyDir: {}
```

주 컨테이너인 nginx와 로그 수집 사이드카가 같은 볼륨을 공유합니다. nginx가 로그를 `/var/log/nginx`에 쓰면 fluent-bit가 같은 경로에서 읽어 외부로 전송합니다.

### init container 패턴

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-init
spec:
  initContainers:
  - name: wait-for-db          # init 컨테이너: 앱 시작 전 선행 작업
    image: busybox
    command: ['sh', '-c', 'until nc -z db-service 5432; do echo waiting; sleep 2; done']
  containers:
  - name: app
    image: myorg/app:1.0
    env:
    - name: DB_HOST
      value: db-service
```

init container는 애플리케이션 실행 전 선행 조건을 확인할 때 유용합니다. 데이터베이스가 준비될 때까지 기다리거나, 설정 파일을 내려받거나, 마이그레이션을 실행하는 작업에 자주 쓰입니다.

## 단계별로 Pod YAML 다뤄 보기

### 1단계 — 적용

```bash
kubectl apply -f pod.yaml
```

Pod를 직접 적용하는 과정은 학습용으로는 좋습니다. 다만 실무에서는 이 단계에서 끝나지 않고, 보통 Deployment 같은 상위 객체가 Pod 생성을 대신 맡습니다.

### 2단계 — 상세 상태 확인

```bash
kubectl describe pod web
```

출력에서 확인할 주요 항목:
```
Name:         web
Namespace:    default
Node:         worker-01/192.168.1.11    # 어느 노드에 배치됐는가
Status:       Running
IP:           10.244.1.5               # 파드 IP (재시작 시 바뀜)

Containers:
  app:
    Image:          nginx:1.25
    State:          Running
    Ready:          True

Conditions:
  Ready          True

Events:
  Normal  Scheduled  5m    Successfully assigned default/web to worker-01
  Normal  Pulled     5m    Successfully pulled image "nginx:1.25"
  Normal  Started    5m    Started container app
```

`describe`는 Pod를 처음 배울 때 가장 유용한 명령 중 하나입니다. 스케줄링 이벤트, 이미지 풀 상태, 컨테이너 시작 여부까지 함께 보여 주기 때문입니다.

### 3단계 — 로그 확인

```bash
# 단일 컨테이너 로그
kubectl logs web

# 여러 컨테이너 중 특정 컨테이너 로그
kubectl logs web -c log-shipper

# 실시간 로그 스트리밍
kubectl logs web -f

# 이전 컨테이너 로그 (재시작 후)
kubectl logs web --previous
```

Pod 안의 컨테이너 로그는 기본적으로 표준 출력으로 보는 흐름이 중요합니다. 컨테이너 안에 직접 들어가 로그 파일을 뒤지는 방식은 Kubernetes의 기본 운영 모델과 잘 맞지 않습니다.

### 4단계 — 컨테이너 접속

```bash
# 컨테이너 셸 접속
kubectl exec -it web -- /bin/sh

# 단일 명령 실행
kubectl exec web -- env

# 사이드카 컨테이너에 접속
kubectl exec -it web-with-logger -c log-shipper -- /bin/sh
```

### 5단계 — 삭제

```bash
kubectl delete pod web

# 강제 삭제 (응답 없을 때)
kubectl delete pod web --force --grace-period=0
```

직접 만든 Pod는 지우면 끝입니다. 다시 살아나지 않습니다. 이 지점이 바로 "Pod를 직접 만들지 말라"는 조언의 핵심과 이어집니다. 자동 복구와 재시작은 Pod 자체가 아니라 상위 컨트롤러의 책임입니다.

## 검증 흐름

```bash
kubectl get pod web -o wide
kubectl describe pod web
kubectl logs web
```

**예상되는 결과:** `get pod`에서는 `Running` 또는 준비 직전 상태가 보여야 하고, `describe`에서는 이미지 풀·스케줄링·컨테이너 시작 이벤트가 시간순으로 보여야 합니다. 로그는 애플리케이션이 표준 출력으로 남긴 초기화 메시지를 확인하는 용도로 읽습니다.

**먼저 의심할 실패 모드:**

- `Pending`이 길면 이미지가 아니라 스케줄링 자원 부족이나 taint를 먼저 봅니다.
- `ImagePullBackOff`면 YAML 문법보다 레지스트리 인증과 이미지 태그를 우선 확인합니다.
- 로그가 비어 있으면 애플리케이션이 파일 로그만 쓰는지, 혹은 컨테이너가 시작 직후 죽는지 나눠서 봐야 합니다.

## 트러블슈팅 시나리오

### 시나리오 1: CrashLoopBackOff

```bash
# 현재 상태 확인
kubectl get pod web

# 이전 실행 로그 확인 (핵심)
kubectl logs web --previous

# 상세 이벤트 확인
kubectl describe pod web

# 자주 나오는 원인
# 1. 애플리케이션 시작 코드에 오류
# 2. 환경 변수 누락
# 3. 의존 서비스 연결 실패
# 4. OOMKilled (메모리 한도 초과)
```

### 시나리오 2: Pending 상태 지속

```bash
# 스케줄러 이유 확인
kubectl describe pod web | grep -A 10 Events

# 노드 자원 확인
kubectl describe nodes | grep -A 5 "Allocated resources"

# 자주 나오는 원인
# 1. 노드 자원 부족 (CPU/메모리 requests 합산 초과)
# 2. taint가 있는 노드만 존재
# 3. nodeSelector/affinity 조건 불일치
# 4. PVC Pending (볼륨 사용 시)
```

### 시나리오 3: OOMKilled

```bash
# 종료 이유 확인
kubectl describe pod web | grep -A 3 "Last State"

# limits 조정
# resources.limits.memory를 현재 사용량 기준으로 여유 있게 설정
kubectl top pod web  # 현재 메모리 사용량 확인
```

## 자주 하는 실수

| 실수 | 문제 | 올바른 방법 |
|---|---|---|
| Pod와 컨테이너 동일시 | 공유 리소스 패턴을 이해 못함 | Pod = 공유 환경의 컨테이너 묶음으로 이해 |
| 직접 만든 Pod 복구 기대 | 장애 시 수동 개입 필요 | Deployment로 자동 복구 위임 |
| Pod IP 고정 가정 | 재시작 후 통신 단절 | Service를 통한 DNS 이름으로 통신 |
| 로그를 파일에서만 찾음 | 운영 효율 저하 | 표준 출력 기반 로그 설계 |
| resources 미설정 | 노드 과부하, 스케줄링 문제 | requests/limits 반드시 지정 |

## 실무에서는 이렇게 봅니다

실무에서는 로그 수집기, 프록시, 비밀 동기화기 같은 보조 컨테이너를 사이드카 형태로 붙이는 경우가 많습니다. 이때 Pod는 단순 배포 단위가 아니라 결합 경계를 결정하는 도구가 됩니다.

시니어 엔지니어는 Pod를 볼 때 "무엇이 함께 살아야 하는가"를 먼저 생각합니다. 동시에 사이드카는 편리한 도구이면서 결합 비용이기도 하다는 점도 함께 봅니다. 너무 쉽게 같은 Pod에 넣으면 배포와 스케일링 단위까지 함께 묶이기 때문입니다.

```bash
# 실무에서 Pod 디버깅 시 자주 쓰는 명령 모음
kubectl get pods -o wide                      # 파드 위치와 IP 확인
kubectl describe pod <name>                   # 이벤트와 조건 상세 확인
kubectl logs <name> --previous -c <container> # 재시작 전 로그
kubectl exec -it <name> -- /bin/sh            # 컨테이너 내부 접속
kubectl top pod <name>                        # 실시간 자원 사용량
```

## 운영 체크리스트

- [ ] Pod 직접 생성은 학습이나 디버깅 상황으로 한정했는가
- [ ] 사이드카가 정말 같은 수명 주기를 가져야 하는가
- [ ] 로그가 표준 출력으로 나가도록 구성했는가
- [ ] Pod 수명 주기를 상위 객체와 함께 이해하고 있는가
- [ ] resources.requests와 limits를 설정했는가
- [ ] 헬스체크(liveness/readiness probe)를 정의했는가

## 연습 문제

1. Pod와 컨테이너의 차이를 한 줄로 설명해 보세요.
2. 사이드카의 실제 예시를 하나 적어 보세요.
3. 왜 직접 Pod를 만들고 운영 기본값으로 삼으면 안 되는지 한 줄로 정리해 보세요.
4. init container와 사이드카의 차이는 무엇인가요?
5. Pod가 `CrashLoopBackOff` 상태일 때 가장 먼저 실행할 kubectl 명령은 무엇인가요?

## Pod 수명 주기 완전 이해

Pod의 상태 전환을 이해하면 장애 상황에서 무슨 일이 일어나는지 빠르게 판단할 수 있습니다.

```
Pod 수명 주기:

Pending
  └─ 스케줄러가 노드를 찾는 중
  └─ 이미지를 내려받는 중
  └─ init container 실행 중

Running
  └─ 컨테이너가 실행 중
  └─ readiness probe 통과 시 트래픽 수신

Succeeded
  └─ 모든 컨테이너가 정상 종료 (exit 0)
  └─ 주로 Job에서 발생

Failed
  └─ 하나 이상의 컨테이너가 비정상 종료

Unknown
  └─ 노드와 통신 불가 (노드 장애)
```

```bash
# 파드 상태 변화 실시간 모니터링
kubectl get pods -w

# 파드 상태 이유 확인
kubectl get pod <name> -o jsonpath='{.status.conditions}'

# 컨테이너별 종료 이유 확인
kubectl get pod <name> -o jsonpath='{.status.containerStatuses[0].lastState}'
```

## Pod가 직접 사용되는 유효한 케이스

직접 Pod를 만드는 것이 모두 나쁜 것은 아닙니다. 아래 상황에서는 합리적입니다.

| 케이스 | 설명 |
|---|---|
| 일회성 디버깅 | `kubectl run tmp --rm -it --image=busybox -- sh` |
| 클러스터 내부 DNS 확인 | nslookup, wget 등 임시 실행 |
| 단발성 마이그레이션 작업 | Job 대신 임시 Pod 사용 |
| 빠른 프로토타입 검증 | Deployment 전 빠른 동작 확인 |

```bash
# 임시 디버그 파드 (자동 삭제)
kubectl run debug --rm -it --restart=Never --image=busybox -- sh

# 특정 서비스 DNS 확인용 임시 파드
kubectl run dnscheck --rm -it --restart=Never --image=busybox -- \
  nslookup my-service.default.svc.cluster.local

# 특정 노드에 디버그 파드 배치
kubectl run debug --rm -it --restart=Never --image=busybox \
  --overrides='{"spec":{"nodeName":"worker-01"}}' -- sh
```

## 마무리와 다음 글

이 글에서는 Pod를 Kubernetes의 최소 실행 단위로 정리했습니다. 컨테이너 하나와 비슷해 보일 때도 있지만, 실제로는 여러 컨테이너가 네트워크와 볼륨을 공유하며 함께 수명을 가지는 묶음이라는 점이 핵심입니다.

다음 글에서는 이 Pod를 사람이 직접 관리하지 않고, 원하는 개수를 유지하고 롤링 업데이트까지 맡는 Deployment를 보겠습니다.

Pod를 잘 설계하면 나중에 Deployment, HPA, PDB를 붙일 때 추가 비용이 크게 줄어듭니다.

## 정리

Pod가 컨테이너가 아닌 이유는 '함께 살고 함께 죽는다'는 결정이 필요하기 때문입니다 — 같은 네트워크와 볼륨을 공유하며 한 단위로 스케줄·재시작되는 묶음이라야 사이드카·init 컨테이너·로컬 통신 같은 패턴이 비로소 자연스럽게 표현됩니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **Pod와 컨테이너는 정확히 어떻게 다를까요?**
  - Pod는 네트워크와 볼륨을 공유하며 함께 수명을 가지는 컨테이너 묶음입니다. 단일 컨테이너 Pod도 있지만, 구조적으로 항상 "하나 이상"을 전제합니다.
- **왜 Kubernetes는 컨테이너가 아니라 Pod를 기본 단위로 삼을까요?**
  - 사이드카, init container, 공유 볼륨 같은 패턴을 지원하려면 묶음 단위가 필요합니다. 컨테이너 하나씩 스케줄하면 이 패턴을 표현할 방법이 없습니다.
- **사이드카 패턴은 어떤 상황에서 필요할까요?**
  - 로그 수집, 서비스 메시 프록시, 시크릿 동기화처럼 주 애플리케이션과 같은 네트워크·볼륨을 공유해야 하는 보조 기능이 필요할 때 씁니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- **Kubernetes 101 (2/10): Pod (현재 글)**
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
