---
series: kubernetes-101
episode: 7
title: Volume
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - Volume
  - PersistentVolume
  - StorageClass
  - DevOps
seo_description: Kubernetes Volume과 PVC, StorageClass, 동적 프로비저닝의 흐름을 입문자 관점에서 정리한 글
last_reviewed: '2026-05-11'
---

# Volume

## 이 글에서 다룰 문제

- 파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?
- emptyDir와 PVC는 어떤 상황에서 갈라질까요?
- StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?
- PVC만 만들면 백업까지 끝났다고 보면 왜 위험할까요?
- stateful 워크로드를 다룰 때 무엇부터 조심해야 할까요?

> Kubernetes 101 시리즈 (7/10)
>
> 핵심 질문: 파드가 죽어도 데이터를 계속 남기려면 무엇이 필요할까요?

컨테이너는 가볍고 빨리 교체할 수 있다는 장점이 있습니다. 하지만 그 장점은 곧 컨테이너 내부 파일시스템이 영구 저장소가 아니라는 뜻이기도 합니다. 파드가 다시 스케줄되거나 새 컨테이너로 교체되면, 그 안에만 저장한 데이터는 함께 사라집니다.

로그인 세션, 업로드 파일, 데이터베이스 파일처럼 상태를 가진 워크로드는 이 특성을 무시할 수 없습니다. Kubernetes에서 Volume을 배운다는 것은 단순히 디스크를 붙이는 법을 익히는 것이 아니라, 상태 데이터의 생명주기를 파드와 분리하는 법을 익히는 일에 가깝습니다.

## 왜 중요한가

웹 API처럼 stateless한 애플리케이션은 파드가 교체돼도 큰 문제가 없을 수 있습니다. 하지만 PostgreSQL, Redis의 일부 구성, 파일 업로드 처리처럼 상태를 직접 다루는 워크로드는 저장 위치를 잘못 잡는 순간 장애가 바로 데이터 손실로 이어집니다.

특히 초보자가 많이 겪는 실수는 “파드가 다시 살아났으니 데이터도 남아 있겠지”라고 생각하는 것입니다. Kubernetes는 애플리케이션 프로세스를 다시 띄우는 일에는 강하지만, 데이터를 보존하는 일은 별도의 스토리지 계층을 제대로 연결했을 때만 가능합니다.

## 한눈에 보는 구조

```mermaid
flowchart LR
    Pod["파드"] --> PVC["PVC"]
    PVC --> SC["스토리지클래스"]
    SC --> PV["PV(디스크)"]
```

애플리케이션은 보통 PVC를 요청하고, PVC는 StorageClass를 통해 실제 디스크인 PV와 연결됩니다. 이 구조를 이해하면 “앱은 무엇을 원하고, 클러스터는 무엇을 만들어 주는가”가 명확해집니다.

## 핵심 용어

- Volume: 파드 안에서 공유하거나 지속할 수 있는 저장소입니다.
- PersistentVolume(PV): 클러스터 관점의 실제 저장소 리소스입니다.
- PersistentVolumeClaim(PVC): 워크로드가 원하는 저장소를 요청하는 객체입니다.
- StorageClass: 어떤 종류의 디스크를 어떤 방식으로 만들지 정의합니다.
- AccessMode: ReadWriteOnce, ReadOnlyMany, ReadWriteMany 같은 접근 방식입니다.

## 적용 전후 달라지는 점

파드 내부 파일시스템에 데이터베이스 파일을 두면 파드 재시작이나 재배치 때 데이터가 사라질 수 있습니다. 개발 환경에서는 운 좋게 지나가도 운영에서 반드시 문제가 됩니다.

PVC와 PV를 사용하면 데이터는 파드 바깥 디스크에 놓이고, 파드는 그 저장소를 마운트해 사용합니다. 파드가 교체돼도 같은 볼륨을 다시 붙일 수 있으므로 상태를 비교적 안정적으로 유지할 수 있습니다.

## 단계별 실습

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

이 PVC는 5Gi 크기의 스토리지를 요청합니다. `storageClassName: gp3`는 어떤 종류의 디스크를 만들지 클러스터에 알려 주는 값입니다.

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

컨테이너는 `/var/lib/postgresql/data` 경로를 로컬 폴더처럼 보지만, 실제로는 PVC를 통해 연결된 외부 저장소를 쓰게 됩니다. 상태를 파드 바깥으로 밀어내는 핵심 지점입니다.

### 3단계 — 적용

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

PVC를 적용하면 클러스터는 적절한 StorageClass를 찾아 PV를 동적으로 만들거나 기존 PV와 바인딩합니다. 이 과정을 동적 프로비저닝이라고 부릅니다.

### 4단계 — 상태 확인

```python
def get_pvc():
    res = subprocess.run(
        ["kubectl", "get", "pvc"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`Pending` 상태가 길게 이어지면 StorageClass, 용량, 권한, 지원 가능한 AccessMode를 함께 확인해야 합니다. 상태 확인은 단순 조회가 아니라 스토리지 계층 문제를 읽는 첫 단계입니다.

### 5단계 — 정리

```python
def delete(name):
    subprocess.run(["kubectl", "delete", "pvc", name], check=True)
```

여기서는 특히 조심해야 합니다. PVC를 지웠을 때 디스크도 함께 사라질 수 있기 때문입니다. 삭제 전에는 StorageClass나 PV의 reclaimPolicy를 먼저 확인하는 습관이 필요합니다.

## 이 코드에서 봐야 할 포인트

- PVC는 직접 디스크를 고르는 객체가 아니라 필요한 저장소를 요청하는 객체입니다.
- `ReadWriteOnce`는 보통 한 노드에서만 읽기/쓰기를 허용합니다.
- 동적 프로비저닝 덕분에 운영자는 매번 수동으로 디스크를 만들지 않아도 됩니다.
- PVC 삭제가 곧 데이터 삭제로 이어질 수 있으므로 reclaimPolicy를 반드시 함께 봐야 합니다.

## 자주 하는 실수 5가지

1. 상태 데이터를 emptyDir에 둡니다.
2. RWX가 어디서나 기본 지원된다고 생각합니다.
3. reclaimPolicy를 보지 않고 삭제했다가 데이터를 잃습니다.
4. PVC만 있으면 백업도 해결됐다고 오해합니다.
5. StorageClass를 신경 쓰지 않고 기본값만 사용합니다.

## 실무에서는 이렇게 본다

실무에서는 StatefulSet이 파드마다 PVC를 자동으로 만들고, Velero 같은 도구가 주기적으로 스냅샷과 백업을 맡는 구조를 자주 봅니다. 이때 중요한 관점은 “PVC는 운영 중인 저장소”이고 “백업은 복구 전략”이라는 점입니다. 둘은 서로 대체되지 않습니다.

또한 많은 팀이 상태 데이터는 가능하면 관리형 데이터베이스로 분리하고, 클러스터 안에는 최소한의 stateful 워크로드만 남기려 합니다. Kubernetes가 못 해서가 아니라, 스토리지 운영 난도가 애플리케이션 운영 난도와 전혀 다른 축이기 때문입니다.

## 체크리스트

- [ ] 상태 데이터가 PVC 또는 관리형 DB에 있는가
- [ ] 백업 정책을 준비했는가
- [ ] AccessMode를 명시했는가
- [ ] reclaimPolicy를 확인했는가

## 연습 문제

1. emptyDir와 PVC의 차이를 한 줄로 설명해 보세요.
2. RWO의 제약을 한 가지 적어 보세요.
3. PVC만으로는 백업이 끝나지 않는 이유를 한 줄로 써 보세요.

## 정리와 다음 글

Volume은 파드의 수명과 데이터의 수명을 분리하는 기본 도구입니다. PVC는 워크로드가 원하는 저장소를 선언하고, StorageClass와 PV는 그 요청을 실제 디스크로 연결합니다. stateful 워크로드를 운영할 때는 저장소 연결만이 아니라 삭제 정책과 백업 전략까지 같이 봐야 합니다.

다음 글에서는 저장소가 아니라 트래픽 변화에 맞춰 파드 수를 자동으로 조절하는 방법을 보겠습니다. 주제는 HPA입니다.

<!-- toc:begin -->
- [Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Pod](./02-pod.md)
- [Deployment](./03-deployment.md)
- [Service](./04-service.md)
- [Ingress](./05-ingress.md)
- [ConfigMap과 Secret](./06-configmap-and-secret.md)
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

Tags: Kubernetes, Volume, PersistentVolume, StorageClass, DevOps
