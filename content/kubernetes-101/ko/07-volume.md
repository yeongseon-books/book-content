---
series: kubernetes-101
episode: 7
title: "Kubernetes 101 (7/10): Volume"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/269"
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

![Kubernetes 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/07/07-01-concept-at-a-glance.ko.png)
*Kubernetes 101 7장 흐름 개요*

> Volume의 핵심은 '디스크를 붙인다'가 아니라 '파드의 수명과 데이터의 수명을 분리한다'입니다 — 컨테이너 파일시스템은 임시 작업 공간일 뿐이고, 영구 데이터는 PV/PVC 계층을 통해 파드 교체와 무관한 수명을 가져야 stateful 워크로드가 운영 가능해집니다.

## 이 글에서 다룰 문제

- 파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?
- `emptyDir`와 PVC는 어떤 순간에 갈라질까요?
- StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

웹 API처럼 stateless한 애플리케이션은 파드가 교체돼도 큰 문제가 없을 수 있습니다. 하지만 데이터베이스, 파일 업로드, 작업 큐처럼 상태를 직접 다루는 워크로드는 저장 위치를 잘못 잡는 순간 장애가 바로 데이터 손실로 이어집니다.

초보자가 자주 하는 실수도 여기서 나옵니다. 파드가 다시 살아났으니 데이터도 남아 있을 것이라고 기대하는 것입니다. Kubernetes는 프로세스를 다시 띄우는 일에는 강하지만, 데이터 보존은 별도의 스토리지 계층을 제대로 연결했을 때만 가능합니다.

## Volume 타입 비교

| 타입 | 수명 | 범위 | 사용 시나리오 |
|---|---|---|---|
| emptyDir | 파드 수명과 동일 | 같은 파드 내 컨테이너 간 공유 | 사이드카 간 임시 데이터 공유, 캐시 |
| hostPath | 노드 수명 | 특정 노드에 고정 | 노드 로그 수집, 개발용 (운영 비권장) |
| PVC (PersistentVolumeClaim) | 독립적 | 네임스페이스 내 | 데이터베이스, 파일 저장 등 영구 데이터 |
| ConfigMap/Secret | 객체 수명 | 네임스페이스 내 | 설정 파일 마운트 |
| NFS | 외부 NFS 서버 | 클러스터 전체 | 공유 파일 시스템 (RWX 필요 시) |

## 한눈에 보는 구조

애플리케이션은 보통 PVC를 통해 저장소를 요청하고, StorageClass는 어떤 종류의 디스크를 어떤 방식으로 만들지 결정합니다. 이 흐름을 이해하면 애플리케이션이 원하는 것과 클러스터가 실제로 제공하는 것이 분리되어 보입니다.

- Volume: 파드 안에서 공유하거나 지속할 수 있는 저장소입니다.
- PersistentVolume: 클러스터 관점의 실제 저장소 리소스입니다.
- PersistentVolumeClaim: 워크로드가 원하는 저장소를 요청하는 객체입니다.
- StorageClass: 디스크를 어떤 방식으로 만들지 정의합니다.
- AccessMode: 저장소에 어떤 방식으로 접근할 수 있는지 나타냅니다.

## AccessMode 이해

```yaml
# AccessMode 세 가지
accessModes:
  - ReadWriteOnce    # RWO: 한 노드에서 읽기/쓰기 (가장 일반적)
  - ReadOnlyMany     # ROX: 여러 노드에서 읽기 전용
  - ReadWriteMany    # RWX: 여러 노드에서 읽기/쓰기 (NFS, 특정 CSI만 지원)
```

| AccessMode | 지원 스토리지 예시 | 사용 시나리오 |
|---|---|---|
| ReadWriteOnce (RWO) | AWS EBS, GCP PD, Azure Disk | 데이터베이스, 단일 인스턴스 |
| ReadOnlyMany (ROX) | NFS, 대부분 CSI | 읽기 전용 공유 설정 |
| ReadWriteMany (RWX) | NFS, Azure Files, EFS | 공유 파일 시스템 (여러 파드) |

## PVC와 PV, StorageClass 완전 이해

### StorageClass 정의

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com       # AWS EBS CSI 드라이버
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
reclaimPolicy: Delete               # PVC 삭제 시 PV(디스크)도 삭제
allowVolumeExpansion: true          # PVC 크기 확장 허용
volumeBindingMode: WaitForFirstConsumer  # 파드 스케줄링 후 디스크 생성
```

### PVC 작성

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
  namespace: default
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: gp3             # 어떤 StorageClass를 사용할지 명시
```

이 PVC는 10Gi 저장소를 요청합니다. `storageClassName: gp3`는 어떤 종류의 디스크를 만들지 클러스터에 알려 주는 값입니다.

### 파드에서 PVC 사용

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data  # PostgreSQL 데이터 경로
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: data                      # 위에서 만든 PVC 이름
```

컨테이너는 이 경로를 로컬 폴더처럼 보지만, 실제로는 PVC를 통해 연결된 외부 저장소를 사용합니다. 상태를 파드 바깥으로 밀어내는 핵심 지점입니다.

## 단계별로 파드에 디스크 붙이기

### 1단계 — PVC 적용

```bash
kubectl apply -f pvc.yaml
kubectl get pvc
```

출력 예시:
```
NAME   STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
data   Pending                                      gp3            5s
```

처음에는 `Pending` 상태입니다. `WaitForFirstConsumer` 모드에서는 파드가 스케줄될 때까지 디스크 생성이 지연됩니다.

### 2단계 — 파드 적용 후 PVC 상태 확인

```bash
kubectl apply -f deployment.yaml
kubectl get pvc
```

출력 예시 (파드 스케줄 후):
```
NAME   STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
data   Bound    pvc-abc123-def456-789012-abcdef123456      10Gi       RWO            gp3            1m
```

`Bound` 상태가 되어야 실제 디스크가 연결된 상태입니다.

### 3단계 — 상태 확인

```bash
kubectl describe pvc data
kubectl get pv
```

`Pending` 상태가 오래 이어지면 StorageClass, 용량, 권한, AccessMode를 함께 확인해야 합니다. 상태 조회는 단순 목록 확인이 아니라 스토리지 문제를 읽는 출발점입니다.

### 4단계 — 데이터 지속성 검증

```bash
# 파드에 데이터 쓰기
kubectl exec deploy/postgres -- psql -U postgres -c "CREATE TABLE test (id int);"

# 파드 강제 삭제 (재시작 시뮬레이션)
kubectl delete pod -l app=postgres

# 새 파드에서 데이터 확인
kubectl exec deploy/postgres -- psql -U postgres -c "SELECT * FROM test;"
```

### 5단계 — 정리 시 주의사항

```bash
# PVC 삭제 전 반드시 영향 확인
kubectl get pod --all-namespaces | grep <pvc-name>

# reclaimPolicy 확인
kubectl get pv <pv-name> -o jsonpath='{.spec.persistentVolumeReclaimPolicy}'

# PVC 삭제 (reclaimPolicy: Delete면 실제 디스크도 삭제됨!)
kubectl delete pvc data
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

## 트러블슈팅 시나리오

### 시나리오 1: PVC가 Pending 상태 지속

```bash
# PVC 이벤트 확인
kubectl describe pvc data

# 흔한 원인
# 1. StorageClass가 없거나 이름 오타
kubectl get storageclass

# 2. 용량 요청이 StorageClass 최소값 미만
# 3. AccessMode 미지원 (예: RWX를 EBS에 요청)
# 4. 노드 존(Zone) 불일치 (WaitForFirstConsumer 모드)
```

### 시나리오 2: 파드 재시작 후 데이터 사라짐

```bash
# 볼륨 타입 확인 (emptyDir이면 파드 재시작 시 초기화)
kubectl get pod <pod-name> -o jsonpath='{.spec.volumes}'

# PVC 연결 여부 확인
kubectl get pod <pod-name> -o yaml | grep -A 5 volumes

# emptyDir을 PVC로 전환 필요
```

### 시나리오 3: PVC 크기 확장

```bash
# StorageClass에 allowVolumeExpansion: true 필요
kubectl get storageclass gp3 -o jsonpath='{.allowVolumeExpansion}'

# PVC 크기 변경
kubectl patch pvc data -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# 확장 상태 확인
kubectl describe pvc data | grep -A 5 Conditions
```

## 자주 하는 실수

| 실수 | 문제 | 올바른 방법 |
|---|---|---|
| 상태 데이터를 emptyDir에 저장 | 파드 재시작 시 데이터 손실 | PVC 또는 관리형 데이터베이스 사용 |
| RWX 지원 가정 | 클라우드 블록 스토리지는 RWX 미지원 | 스토리지 유형별 AccessMode 지원 확인 |
| reclaimPolicy 미확인 후 PVC 삭제 | 실제 데이터 영구 삭제 | 삭제 전 reclaimPolicy 반드시 확인 |
| PVC = 백업이라는 오해 | 장애 시 복구 불가 | 별도 백업 정책 (Velero 등) 수립 |
| StorageClass 기본값만 사용 | 성능 요구사항 미충족 | 워크로드에 맞는 StorageClass 선택 |

## 실무에서는 이렇게 봅니다

실무에서는 StatefulSet이 파드마다 PVC를 자동으로 만들고, Velero 같은 도구가 스냅샷과 백업을 맡는 구조를 자주 봅니다. 이때 중요한 점은 PVC가 운영 중인 저장소이고, 백업은 복구 전략이라는 사실입니다. 둘은 서로 대체되지 않습니다.

시니어 엔지니어는 가능하면 상태 데이터 자체를 관리형 데이터베이스로 분리하는 편도 많이 선택합니다. Kubernetes가 못 해서가 아니라, 스토리지 운영 난도가 애플리케이션 운영 난도와 다른 축이기 때문입니다.

```yaml
# StatefulSet의 volumeClaimTemplates 예시
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:             # 파드마다 자동으로 PVC 생성
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      resources:
        requests:
          storage: 10Gi
      storageClassName: gp3
```

## 운영 체크리스트

- [ ] 상태 데이터가 PVC 또는 관리형 DB에 있는가
- [ ] 백업 정책을 준비했는가
- [ ] AccessMode를 명시했는가
- [ ] reclaimPolicy를 확인했는가
- [ ] StorageClass의 성능 특성이 워크로드에 맞는가
- [ ] PVC 크기 확장 가능 여부를 확인했는가

## 연습 문제

1. `emptyDir`와 PVC의 차이를 한 줄로 설명해 보세요.
2. RWO의 제약을 한 가지 적어 보세요.
3. PVC만으로는 백업이 끝나지 않는 이유를 한 줄로 써 보세요.
4. PVC가 Pending 상태일 때 가장 먼저 확인할 것은 무엇인가요?
5. reclaimPolicy가 `Retain`과 `Delete`일 때 PVC 삭제 결과의 차이를 설명해 보세요.

## StatefulSet과 Volume의 조합

StatefulSet은 파드마다 독립적인 PVC를 자동으로 생성합니다. 데이터베이스 클러스터처럼 각 인스턴스가 다른 데이터를 가져야 할 때 핵심입니다.

```yaml
# StatefulSet volumeClaimTemplates 예시
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: gp3
      resources:
        requests:
          storage: 5Gi
```

```bash
# StatefulSet 파드와 PVC 확인
kubectl get statefulset redis-cluster
kubectl get pods -l app=redis
# redis-cluster-0, redis-cluster-1, redis-cluster-2

kubectl get pvc -l app=redis
# data-redis-cluster-0, data-redis-cluster-1, data-redis-cluster-2
```

## 백업 전략: Velero 사용

PVC는 운영 중인 저장소일 뿐, 백업이 아닙니다. Velero를 사용하면 PVC 스냅샷과 전체 클러스터 백업을 자동화할 수 있습니다.

```bash
# Velero 백업 생성
velero backup create daily-backup \
  --include-namespaces production \
  --storage-location default

# 백업 상태 확인
velero backup describe daily-backup

# 특정 네임스페이스 복원
velero restore create --from-backup daily-backup \
  --include-namespaces production

# 스케줄 백업 설정 (매일 새벽 2시)
velero schedule create daily \
  --schedule="0 2 * * *" \
  --include-namespaces production
```

| PVC | 백업 |
|---|---|
| 현재 운영 데이터를 보존 | 특정 시점의 스냅샷으로 복구 가능 |
| 파드 재시작에도 데이터 유지 | 실수로 지운 데이터 복원 |
| 클러스터 종속 | 다른 클러스터로 마이그레이션 가능 |

## 마무리와 다음 글

이 글에서는 Volume을 파드의 수명과 데이터의 수명을 분리하는 기본 도구로 정리했습니다. PVC는 워크로드가 원하는 저장소를 선언하고, StorageClass와 PV는 그 요청을 실제 디스크로 연결합니다.

다음 글에서는 저장소가 아니라 트래픽 변화에 따라 파드 수를 자동으로 조절하는 방법, HPA를 보겠습니다.

## 정리

Volume의 핵심은 '디스크를 붙인다'가 아니라 '파드의 수명과 데이터의 수명을 분리한다'입니다 — 컨테이너 파일시스템은 임시 작업 공간일 뿐이고, 영구 데이터는 PV/PVC 계층을 통해 파드 교체와 무관한 수명을 가져야 stateful 워크로드가 운영 가능해집니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?**
  - 컨테이너 파일시스템은 컨테이너 레이어에 임시로 존재합니다. 파드가 재시작되면 새 컨테이너가 이미지에서 다시 만들어지므로 기존 파일시스템 내용은 사라집니다.
- **`emptyDir`와 PVC는 어떤 순간에 갈라질까요?**
  - 파드 재시작을 넘어 데이터가 살아남아야 한다면 PVC가 필요합니다. emptyDir는 파드 내 컨테이너 간 임시 공유에만 적합합니다.
- **StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?**
  - 어떤 유형의 디스크를 생성할지, reclaimPolicy, 확장 허용 여부, 바인딩 타이밍까지 결정합니다. 잘못 선택하면 성능과 비용, 안전성에 모두 영향을 줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- **Kubernetes 101 (7/10): Volume (현재 글)**
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
