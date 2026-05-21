---
series: kubernetes-101
episode: 7
title: "Kubernetes 101 (7/10): Volume"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - Volume
  - PersistentVolume
  - StorageClass
  - DevOps
seo_description: Volume과 PVC, StorageClass가 상태 데이터를 분리하는 방식을 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (7/10): Volume

컨테이너는 가볍고 교체가 쉽다는 장점이 있습니다. 하지만 그 장점은 동시에 컨테이너 파일시스템이 영구 저장소가 아니라는 뜻이기도 합니다. 파드가 다시 스케줄되거나 새 컨테이너로 교체되면, 그 안에만 저장한 데이터는 함께 사라집니다.

이 글은 Kubernetes 101 시리즈의 7번째 글입니다.

여기서는 Volume을 단순히 디스크를 붙이는 기능이 아니라, 파드의 수명과 데이터의 수명을 분리해 stateful 워크로드를 운영 가능하게 만드는 저장소 모델로 정리하겠습니다.

## 먼저 던지는 질문

- 파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?
- `emptyDir`와 PVC는 어떤 순간에 갈라질까요?
- StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?

## 큰 그림

![Kubernetes 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/07/07-01-concept-at-a-glance.ko.png)

*Kubernetes 101 7장 흐름 개요*

## 왜 중요한가

웹 API처럼 stateless한 애플리케이션은 파드가 교체돼도 큰 문제가 없을 수 있습니다. 하지만 데이터베이스, 파일 업로드, 작업 큐처럼 상태를 직접 다루는 워크로드는 저장 위치를 잘못 잡는 순간 장애가 바로 데이터 손실로 이어집니다.

초보자가 자주 하는 실수도 여기서 나옵니다. 파드가 다시 살아났으니 데이터도 남아 있을 것이라고 기대하는 것입니다. Kubernetes는 프로세스를 다시 띄우는 일에는 강하지만, 데이터 보존은 별도의 스토리지 계층을 제대로 연결했을 때만 가능합니다.

## 한눈에 보는 구조

애플리케이션은 보통 PVC를 통해 저장소를 요청하고, StorageClass는 어떤 종류의 디스크를 어떤 방식으로 만들지 결정합니다. 이 흐름을 이해하면 애플리케이션이 원하는 것과 클러스터가 실제로 제공하는 것이 분리되어 보입니다.

## 핵심 용어

- Volume: 파드 안에서 공유하거나 지속할 수 있는 저장소입니다.
- PersistentVolume: 클러스터 관점의 실제 저장소 리소스입니다.
- PersistentVolumeClaim: 워크로드가 원하는 저장소를 요청하는 객체입니다.
- StorageClass: 디스크를 어떤 방식으로 만들지 정의합니다.
- AccessMode: 저장소에 어떤 방식으로 접근할 수 있는지 나타냅니다.

## 도입 전과 후

파드 내부 파일시스템에 데이터베이스 파일을 두면 재시작이나 재배치 때 데이터가 사라질 수 있습니다. 개발 환경에서는 운 좋게 지나가도 운영에서는 반드시 문제가 됩니다.

PVC와 PV를 사용하면 데이터는 파드 바깥 디스크에 놓이고, 파드는 그 저장소를 마운트해 씁니다. 파드가 교체돼도 같은 저장소를 다시 붙일 수 있으므로 상태를 비교적 안정적으로 유지할 수 있습니다.

## 단계별로 파드에 디스크 붙이기

### 1단계 — PVC 작성

```python
"""
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: data}
spec:
  accessModes: [ReadWriteOnce]
  resources: {requests: {storage: 5Gi}}
  storageClassName: gp3
"""
```

이 PVC는 5Gi 저장소를 요청합니다. `storageClassName: gp3`는 어떤 종류의 디스크를 만들지 클러스터에 알려 주는 값입니다.

### 2단계 — 파드에서 사용

```python
"""
spec:
  containers:
  - name: app
    image: postgres:16
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim: {claimName: data}
"""
```

컨테이너는 이 경로를 로컬 폴더처럼 보지만, 실제로는 PVC를 통해 연결된 외부 저장소를 사용합니다. 상태를 파드 바깥으로 밀어내는 핵심 지점입니다.

### 3단계 — 적용

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

PVC를 적용하면 클러스터는 StorageClass를 참고해 PV를 동적으로 만들거나 기존 PV와 바인딩합니다. 이 과정을 동적 프로비저닝이라고 부릅니다.

### 4단계 — 상태 확인

```python
def get_pvc():
    res = subprocess.run(
        ["kubectl", "get", "pvc"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`Pending` 상태가 오래 이어지면 StorageClass, 용량, 권한, AccessMode를 함께 확인해야 합니다. 상태 조회는 단순 목록 확인이 아니라 스토리지 문제를 읽는 출발점입니다.

### 5단계 — 정리

```python
def delete(name):
    subprocess.run(["kubectl", "delete", "pvc", name], check=True)
```

PVC 삭제는 특히 조심해야 합니다. reclaimPolicy에 따라 실제 디스크가 함께 삭제될 수 있기 때문입니다. 상태 데이터는 생성보다 삭제가 더 위험한 경우가 많습니다.

## 검증 흐름

```bash
kubectl get pvc
kubectl describe pvc data
kubectl get pv
```

**예상되는 결과:** PVC는 `Bound` 상태가 되어야 하고, describe 결과에는 어떤 StorageClass와 PV에 연결됐는지가 보여야 합니다. PV 목록까지 같이 보면 실제 디스크가 동적으로 만들어졌는지와 reclaim 정책을 한 번에 확인할 수 있습니다.

**먼저 의심할 실패 모드:**

- PVC가 `Pending`이면 애플리케이션보다 StorageClass, 용량, AccessMode를 먼저 봅니다.
- `Bound`인데 마운트가 실패하면 PVC 자체보다 Pod spec의 volumeMount 경로를 확인합니다.
- 삭제가 무서운 이유는 reclaimPolicy가 `Delete`일 때 실제 디스크까지 사라질 수 있기 때문입니다.

## 이 코드에서 먼저 봐야 할 점

- PVC는 직접 디스크를 고르는 객체가 아니라 저장소를 요청하는 객체입니다.
- `ReadWriteOnce`는 보통 한 노드에서만 읽기와 쓰기를 허용합니다.
- PVC 삭제는 데이터 삭제로 이어질 수 있습니다.

이 셋을 이해하면 Volume을 단순 마운트 설정으로 보지 않게 됩니다. 실제로는 워크로드와 저장소 수명을 분리하는 운영 규약입니다.

## 자주 하는 실수 다섯 가지

1. 상태 데이터를 `emptyDir`에 둡니다.
2. RWX가 어디서나 기본 지원된다고 생각합니다.
3. reclaimPolicy를 보지 않고 삭제합니다.
4. PVC만 있으면 백업도 끝났다고 오해합니다.
5. StorageClass를 신경 쓰지 않고 기본값만 사용합니다.

## 실무에서는 이렇게 봅니다

실무에서는 StatefulSet이 파드마다 PVC를 자동으로 만들고, Velero 같은 도구가 스냅샷과 백업을 맡는 구조를 자주 봅니다. 이때 중요한 점은 PVC가 운영 중인 저장소이고, 백업은 복구 전략이라는 사실입니다. 둘은 서로 대체되지 않습니다.

시니어 엔지니어는 가능하면 상태 데이터 자체를 관리형 데이터베이스로 분리하는 편도 많이 선택합니다. Kubernetes가 못 해서가 아니라, 스토리지 운영 난도가 애플리케이션 운영 난도와 다른 축이기 때문입니다.

## 체크리스트

- [ ] 상태 데이터가 PVC 또는 관리형 DB에 있는가
- [ ] 백업 정책을 준비했는가
- [ ] AccessMode를 명시했는가
- [ ] reclaimPolicy를 확인했는가

## 연습 문제

1. `emptyDir`와 PVC의 차이를 한 줄로 설명해 보세요.
2. RWO의 제약을 한 가지 적어 보세요.
3. PVC만으로는 백업이 끝나지 않는 이유를 한 줄로 써 보세요.

## 마무리와 다음 글

이 글에서는 Volume을 파드의 수명과 데이터의 수명을 분리하는 기본 도구로 정리했습니다. PVC는 워크로드가 원하는 저장소를 선언하고, StorageClass와 PV는 그 요청을 실제 디스크로 연결합니다.

다음 글에서는 저장소가 아니라 트래픽 변화에 따라 파드 수를 자동으로 조절하는 방법, HPA를 보겠습니다.


## 매니페스트 중심 운영 예시

Kubernetes의 강점은 명령형 조작보다 선언형 매니페스트에 있습니다. 아래 예시는 Deployment, Service, Ingress를 분리해 책임 경계를 명확히 둔 기본 형태입니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:1.2.0
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

readiness probe와 resource request/limit를 함께 정의하면 "배포는 되었지만 트래픽을 받으면 무너지는" 상태를 줄일 수 있습니다. 선언형 파일에서 운영 안정성을 미리 포함시키는 방식이 중요합니다.

## kubectl 운영 명령 세트

매니페스트를 적용한 뒤에는 상태 관찰 명령을 빠르게 순환해야 합니다. 아래 조합은 장애 분석에서 가장 자주 사용하는 기본 세트입니다.

```bash
kubectl apply -f k8s/
kubectl get deploy,rs,pod -n prod -o wide
kubectl rollout status deploy/api -n prod
kubectl describe pod -n prod -l app=api
kubectl logs -n prod deploy/api --tail=200
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
```

`rollout status`와 `describe`를 먼저 보면 이미지 pull 실패, probe 실패, 스케줄링 실패를 빠르게 구분할 수 있습니다. 로그만 먼저 보면 인프라 원인을 애플리케이션 오류로 오판하기 쉽습니다.

## 아키텍처 관점에서 봐야 할 경계

- **API Server 경계**: 모든 선언 변경은 API 서버를 통과합니다. 직접 노드에 접속해 상태를 손으로 맞추는 방식은 drift를 만듭니다.
- **Scheduler 경계**: Pod 배치는 자원 요청, taint/toleration, affinity 규칙의 결과입니다. 노드 선택 문제는 애플리케이션 버그와 분리해 봐야 합니다.
- **Controller 경계**: Deployment Controller는 replica 수렴과 롤링 업데이트를 담당합니다. desired/current 값 차이를 관찰하는 습관이 핵심입니다.
- **Network 경계**: Service와 Ingress는 L4/L7 책임이 다릅니다. 내부 통신 실패와 외부 진입 실패를 분리해 진단해야 대응이 빨라집니다.

이 경계를 기준으로 장애를 분해하면 "클러스터 문제"라는 모호한 결론 대신, 어느 계층에서 어떤 신호가 깨졌는지 명확히 남길 수 있습니다.

## 배포 안정성을 높이는 실무 체크

1. 모든 워크로드에 readiness/liveness probe를 설정합니다.
2. `latest` 태그 대신 고정 버전 태그를 사용해 롤백 기준을 확보합니다.
3. 변경 전 `kubectl diff -f`로 영향을 검토해 무의식적 설정 누락을 줄입니다.
4. 운영 네임스페이스에는 ResourceQuota와 LimitRange를 적용해 폭주 범위를 제한합니다.
5. 배포 후 `kubectl rollout history`를 확인해 복구 경로를 문서화합니다.

Kubernetes는 기능이 많아서 어려운 도구가 아니라, 경계를 나누어 관찰하지 않으면 쉽게 혼란스러워지는 도구입니다. 매니페스트, 관찰 명령, 아키텍처 경계를 함께 묶어 운영하면 학습 속도와 안정성이 동시에 올라갑니다.


## 운영 관찰 지표 추가

클러스터 상태를 확인할 때 단순 성공 여부만 보지 말고 재시작 횟수, 스케줄링 지연, 이미지 풀 시간 같은 신호를 함께 봐야 합니다. `kubectl get pod -A -o wide`와 `kubectl top pod -A`를 주기적으로 확인하면 자원 부족으로 인한 지연을 조기에 발견할 수 있습니다. 또한 배포 직후 `kubectl rollout status`와 `kubectl get events`를 묶어 실행하면 문제를 애플리케이션 로그로만 좁혀 보는 실수를 줄일 수 있습니다.

```bash
kubectl get pod -A -o wide
kubectl top pod -A
kubectl rollout status deploy/<name> -n <ns>
```

운영 문서에는 위 명령의 기대 출력과 비정상 패턴을 함께 기록해 두는 편이 대응 품질을 높입니다.

## 처음 질문으로 돌아가기

- **파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?**
  - 본문의 기준은 Volume를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`emptyDir`와 PVC는 어떤 순간에 갈라질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- **Volume (현재 글)**
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Velero](https://velero.io/)
- [Change the reclaim policy of a PersistentVolume](https://kubernetes.io/docs/tasks/administer-cluster/change-pv-reclaim-policy/)

Tags: Kubernetes, Volume, PersistentVolume, StorageClass, DevOps
